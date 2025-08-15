# segmentator_api.py
# FastAPI wrapper for TotalSegmentator with:
# - Safe CLI flags only: --fast, --ml, --resample, --output_type {nifti,dicom}
# - Optional `targets` for subset runs:
#     • If the installed CLI supports --roi_subset, pass it for speed.
#     • Otherwise, run full segmentation and filter the returned ZIP server-side.
# - Staging per request under %LOCALAPPDATA%\AMIGOpy, with cleanup controls:
#     • persist_raw (default False) keeps the raw TS folder.
#     • keep_only_selected (default True) prunes raw folder to selected targets when kept.
# - Helpful error payloads: includes stderr tail and exact command on failure.

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List, Tuple
import os, uuid, subprocess, shutil, zipfile, re, tempfile

app = FastAPI()

# ---------- Paths ----------
BASE_DIR = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser("~")), "AMIGOpy")
os.makedirs(BASE_DIR, exist_ok=True)
print(f"[Segmentator API] Using base directory: {BASE_DIR}")

# ---------- Helpers ----------
def _map_output_type(v: Optional[str]) -> str:
    s = (v or "").strip().lower()
    if s in ("nifti", "nii", "nii.gz", "nifti_gz"): return "nifti"
    if s in ("dicom", "dcm", "dicom_seg", "seg"):   return "dicom"
    return "nifti"

_normer_re = re.compile(r"[^a-z0-9]+")
def _norm_label(s: str) -> str:
    s = (s or "").strip().lower()
    s = _normer_re.sub("_", s)
    return re.sub(r"_+", "_", s).strip("_")

def _collect_nifti_files(root_dir: str) -> List[str]:
    out = []
    for r, _, files in os.walk(root_dir):
        for fn in files:
            low = fn.lower()
            if low.endswith(".nii") or low.endswith(".nii.gz"):
                out.append(os.path.join(r, fn))
    return out

def _double_ext_stem(fp: str) -> str:
    """Return filename stem handling .nii.gz as a single extension."""
    base = os.path.basename(fp)
    if base.endswith(".nii.gz"): return base[:-7]
    if base.endswith(".nii"):    return base[:-4]
    return os.path.splitext(base)[0]

def _zipdir(src_dir: str, zip_no_ext: str) -> str:
    zpath = zip_no_ext + ".zip"
    try:
        if os.path.exists(zpath): os.remove(zpath)
    except Exception:
        pass
    shutil.make_archive(zip_no_ext, "zip", src_dir)
    return zpath

def _cli_supports_roi_subset() -> bool:
    """Detect once if TotalSegmentator provides --roi_subset."""
    try:
        h = subprocess.run(["TotalSegmentator", "-h"], capture_output=True, text=True, timeout=10)
        txt = (h.stdout or "") + (h.stderr or "")
        return "--roi_subset" in txt
    except Exception:
        return False

ROI_SUBSET_OK = _cli_supports_roi_subset()

def _map_targets_for_cli(raw_targets: Optional[str]) -> List[str]:
    """
    Normalize incoming UI names to CLI-ish tokens.
    Heuristics only (safe): lowercase, underscores, handle *_l/*_r -> left_*/right_*.
    If your UI uses 'Kidney_L' -> 'left_kidney', this catches the common pattern.
    """
    if not raw_targets: return []
    out = []
    for t in raw_targets.split(","):
        t0 = _norm_label(t)
        if not t0: continue
        # Move trailing _l/_r to prefix left_/right_
        m = re.match(r"^(.*)_(l|r)$", t0)
        if m:
            core, side = m.group(1), m.group(2)
            t0 = ("left_" if side == "l" else "right_") + core
        out.append(t0)
    return out

def _stage_dirs() -> Tuple[str, str, str]:
    """
    Create a per-request staging directory:
      req_dir: request root under BASE_DIR
      input_path: where we store uploaded nii.gz
      output_dir: TotalSegmentator output
    """
    req_dir = tempfile.mkdtemp(prefix="tsreq_", dir=BASE_DIR)
    input_path = os.path.join(req_dir, "input_ct.nii.gz")
    output_dir = os.path.join(req_dir, "ts_out")
    os.makedirs(output_dir, exist_ok=True)
    return req_dir, input_path, output_dir

# ---------- Health ----------
@app.get("/ping")
def ping():
    return {"status": "Segmentator is running"}

# ---------- Main endpoint ----------
@app.post("/segment/")
async def segment_ct(
    file: UploadFile = File(...),
    fast: bool = Query(False, description="--fast"),
    ml: bool = Query(False, description="--ml merge labels"),
    resample: Optional[float] = Query(None, description="--resample <mm>"),
    output_type: str = Query("nifti", description="nifti|dicom"),
    targets: Optional[str] = Query(None, description="comma-separated organ names to include"),
    persist_raw: bool = Query(False, description="keep the raw TS output directory on disk"),
    keep_only_selected: bool = Query(True, description="when persisting raw and targets set, prune to selected"),
):
    req_dir, input_path, output_dir = _stage_dirs()

    try:
        # 1) Save upload
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # 2) Build CLI (safe flags only)
        ot = _map_output_type(output_type)
        cmd = ["TotalSegmentator", "-i", input_path, "-o", output_dir, "--output_type", ot]
        if fast: cmd.append("--fast")
        if ml:   cmd.append("--ml")
        if resample and resample > 0:
            cmd += ["--resample", str(resample)]

        # 3) Optional ROI subset (speed-up) if supported & per-organ NIfTI & targets provided
        requested_cli: List[str] = []
        if not ml and ot == "nifti" and targets:
            requested_cli = _map_targets_for_cli(targets)
            if ROI_SUBSET_OK and requested_cli:
                cmd += ["--roi_subset"] + requested_cli  # space-separated list after the flag

        # 4) Run and capture logs
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            return JSONResponse(
                status_code=500,
                content={
                    "error": f"TotalSegmentator failed (exit {proc.returncode})",
                    "cmd": " ".join(cmd),
                    "stderr_tail": (proc.stderr or "").splitlines()[-20:],
                },
            )

        # 5) Outputs
        if ml:
            # merged single file (try common names)
            candidates = [
                os.path.join(output_dir, "segmentations.nii.gz"),
                os.path.join(output_dir, "merged_labels.nii.gz"),
                os.path.join(output_dir, "segmentations.dcm"),
            ]
            for p in candidates:
                if os.path.exists(p):
                    final_path = os.path.join(BASE_DIR, f"{uuid.uuid4().hex}_{os.path.basename(p)}")
                    try:
                        shutil.move(p, final_path)
                    except Exception:
                        # fallback: copy if move fails across devices
                        shutil.copy2(p, final_path)
                    if not persist_raw:
                        shutil.rmtree(req_dir, ignore_errors=True)
                    return FileResponse(final_path, filename=os.path.basename(final_path))
            return JSONResponse(status_code=500, content={"error": "Merged output file not found.", "outdir": output_dir})

        # Per-organ outputs
        if ot == "nifti":
            seg_dir = os.path.join(output_dir, "segmentations")
            search_dir = seg_dir if os.path.isdir(seg_dir) else output_dir
            files = _collect_nifti_files(search_dir)

            # If ROI_SUBSET not supported, do server-side filtering by targets
            requested = set(_map_targets_for_cli(targets)) if targets else None
            if requested and not ROI_SUBSET_OK:
                files = [
                    fp for fp in files
                    if _norm_label(_double_ext_stem(fp)) in requested
                ]

            # Prepare ZIP in BASE_DIR
            zip_no_ext = os.path.join(BASE_DIR, f"{uuid.uuid4().hex}_segmentations")
            zpath = zip_no_ext + ".zip"
            try:
                if os.path.exists(zpath): os.remove(zpath)
            except Exception:
                pass

            with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as z:
                added = 0
                for fp in files:
                    # if requested provided and ROI_SUBSET OK, files should already be a subset
                    if (not requested) or (_norm_label(_double_ext_stem(fp)) in requested):
                        arc = os.path.relpath(fp, output_dir)
                        z.write(fp, arc)
                        added += 1

            if not os.path.exists(zpath) or os.path.getsize(zpath) == 0:
                if not persist_raw:
                    shutil.rmtree(req_dir, ignore_errors=True)
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "No matching organ files to zip.",
                        "outdir": output_dir,
                        "requested": list(requested or []),
                        "roi_subset_used": ROI_SUBSET_OK and bool(requested_cli),
                    },
                )

            # Optionally prune the raw dir if we keep it but only want selected
            if persist_raw and requested and keep_only_selected:
                keep = {os.path.abspath(fp) for fp in files}
                for fp in _collect_nifti_files(search_dir):
                    if os.path.abspath(fp) not in keep:
                        try: os.remove(fp)
                        except Exception: pass

            if not persist_raw:
                shutil.rmtree(req_dir, ignore_errors=True)

            return FileResponse(zpath, filename=os.path.basename(zpath))

        # DICOM outputs: zip entire TS folder (no per-organ filtering here)
        zpath = _zipdir(output_dir, os.path.join(BASE_DIR, f"{uuid.uuid4().hex}_segmentations"))
        if not persist_raw:
            shutil.rmtree(req_dir, ignore_errors=True)
        return FileResponse(zpath, filename=os.path.basename(zpath))

    except Exception as e:
        # Clean staging on error unless persistence requested
        try:
            if not persist_raw:
                shutil.rmtree(req_dir, ignore_errors=True)
        except Exception:
            pass
        return JSONResponse(status_code=500, content={"error": str(e)})

# ---------- Entrypoint ----------
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("AMIGO_SEG_HOST", "127.0.0.1")
    port = int(os.getenv("AMIGO_SEG_PORT", "5000"))
    uvicorn.run("segmentator_api:app", host=host, port=port, reload=False)
