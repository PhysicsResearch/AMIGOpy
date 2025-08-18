# segmentator_api.py
# FastAPI wrapper for TotalSegmentator with:
# - Safe CLI flags only: --fast, --ml, --resample, --output_type {nifti,dicom}
# - Optional `targets` for subset runs (via --roi_subset if supported)
# - Per-request staging under system TEMP, models under LOCALAPPDATA\AMIGOpy\Models
# - Progress log per request + /progress/{req_id} endpoint

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List, Tuple
import os, uuid, subprocess, shutil, zipfile, re, tempfile
import multipart 

app = FastAPI()

# ---------- Persistent Models ----------
BASE_DIR = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser("~")), "AMIGOpy")
MODELS_DIR = os.path.join(BASE_DIR, "Models")
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
print(f"[Segmentator API] Using base directory: {BASE_DIR}")
print(f"[Segmentator API] Using models directory: {MODELS_DIR}")

# ---------- Helpers ----------
_normer_re = re.compile(r"[^a-z0-9]+")

def _norm_label(s: str) -> str:
    s = (s or "").strip().lower()
    s = _normer_re.sub("_", s)
    return re.sub(r"_+", "_", s).strip("_")

def _double_ext_stem(fp: str) -> str:
    base = os.path.basename(fp)
    if base.endswith(".nii.gz"): return base[:-7]
    if base.endswith(".nii"):    return base[:-4]
    return os.path.splitext(base)[0]

def _collect_nifti_files(root_dir: str) -> List[str]:
    out = []
    for r, _, files in os.walk(root_dir):
        for fn in files:
            if fn.lower().endswith((".nii", ".nii.gz")):
                out.append(os.path.join(r, fn))
    return out

def _cli_supports_roi_subset() -> bool:
    try:
        h = subprocess.run(["TotalSegmentator", "-h"], capture_output=True, text=True, timeout=10)
        txt = (h.stdout or "") + (h.stderr or "")
        return "--roi_subset" in txt
    except Exception:
        return False

ROI_SUBSET_OK = _cli_supports_roi_subset()

def _map_targets_for_cli(raw_targets: Optional[str]) -> List[str]:
    """
    Preserve case (TS class names are case-sensitive).
    Only map a trailing '_l'/'_r' (any case) to 'left_'/ 'right_'.
    """
    if not raw_targets:
        return []
    out: List[str] = []
    for t in raw_targets.split(","):
        t = (t or "").strip()
        if not t:
            continue
        m = re.match(r"^(.*)_(l|r)$", t, flags=re.IGNORECASE)
        if m:
            core, side = m.group(1), m.group(2)
            t = ("left_" if side.lower() == "l" else "right_") + core
        out.append(t)
    return out

def _stage_dirs() -> Tuple[str, str, str, str, str]:
    """
    Create a per-request staging directory under system TEMP.
    Returns (req_id, req_dir, input_path, output_dir, log_path).
    """
    req_id = "tsreq_" + uuid.uuid4().hex
    tmp_root = tempfile.gettempdir()
    req_dir = os.path.join(tmp_root, req_id)
    os.makedirs(req_dir, exist_ok=True)
    input_path = os.path.join(req_dir, "input_ct.nii.gz")
    output_dir = os.path.join(req_dir, "ts_out")
    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(req_dir, "ts_progress.log")
    return req_id, req_dir, input_path, output_dir, log_path

# ---------- Health ----------
@app.get("/ping")
def ping():
    return {"status": "Segmentator is running"}

# ---------- Progress ----------
@app.get("/progress/{req_id}")
def get_progress(req_id: str):
    req_dir = os.path.join(tempfile.gettempdir(), req_id)
    log_file = os.path.join(req_dir, "ts_progress.log")
    if not os.path.exists(log_file):
        return {"status": "not_found", "lines": []}

    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    return {"status": "ok", "lines": lines[-10:]}  # last 10 lines

# ---------- Main segmentation ----------
@app.post("/segment/")
async def segment_ct(
    file: UploadFile = File(...),
    fast: bool = Query(False, description="--fast"),
    ml: bool = Query(False, description="--ml merge labels"),
    resample: Optional[float] = Query(None, description="--resample <mm>"),
    output_type: str = Query("nifti", description="nifti|dicom"),
    targets: Optional[str] = Query(None, description="comma-separated organ names"),
    persist_raw: bool = Query(False, description="keep request folder"),
):
    req_id, req_dir, input_path, output_dir, log_path = _stage_dirs()

    try:
        # Save uploaded NIfTI
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # Build CLI
        ot = (output_type or "nifti").lower()
        cmd = ["TotalSegmentator", "-i", input_path, "-o", output_dir, "--output_type", ot]
        if fast: cmd.append("--fast")
        if ml:   cmd.append("--ml")
        if resample and resample > 0:
            cmd += ["--resample", str(resample)]

        # ROI subset (only if supported & per-organ nifti)
        requested_cli: List[str] = []
        if not ml and ot == "nifti" and targets:
            requested_cli = _map_targets_for_cli(targets)
            if ROI_SUBSET_OK and requested_cli:
                cmd += ["--roi_subset"] + requested_cli

        # Run with live log
        with open(log_path, "w", encoding="utf-8") as logf:
            proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, text=True)
            ret = proc.wait()

        if ret != 0:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                tail = f.readlines()[-20:]
            return JSONResponse(
                status_code=500,
                content={"error": f"TotalSegmentator failed (exit {ret})",
                         "cmd": " ".join(cmd),
                         "stderr_tail": tail,
                         "req_id": req_id}
            )

        # Return ID + info about output directory
        return {"req_id": req_id, "output_dir": output_dir}

    except Exception as e:
        if not persist_raw:
            shutil.rmtree(req_dir, ignore_errors=True)
        return JSONResponse(status_code=500, content={"error": str(e)})

# ---------- Async segmentation (non-blocking) ----------
@app.post("/segment_async/")
async def segment_ct_async(
    file: UploadFile = File(...),
    fast: bool = Query(False, description="--fast"),
    ml: bool = Query(False, description="--ml merge labels"),
    resample: Optional[float] = Query(None, description="--resample <mm>"),
    output_type: str = Query("nifti", description="nifti|dicom"),
    targets: Optional[str] = Query(None, description="comma-separated organ names"),
    persist_raw: bool = Query(False, description="keep request folder"),
):
    """
    Starts TotalSegmentator in the background and returns immediately with req_id.
    Use /progress/{req_id} to fetch log tails and /status/{req_id} to check completion.
    """
    req_id, req_dir, input_path, output_dir, log_path = _stage_dirs()

    try:
        # Save uploaded NIfTI
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # Build CLI
        ot = (output_type or "nifti").lower()
        cmd = ["TotalSegmentator", "-i", input_path, "-o", output_dir, "--output_type", ot]
        if fast: cmd.append("--fast")
        if ml:   cmd.append("--ml")
        if resample and resample > 0:
            cmd += ["--resample", str(resample)]

        # ROI subset (only if supported & per-organ nifti)
        requested_cli: List[str] = []
        if not ml and ot == "nifti" and targets:
            requested_cli = _map_targets_for_cli(targets)
            if ROI_SUBSET_OK and requested_cli:
                cmd += ["--roi_subset"] + requested_cli
                print("[Segmentator API] roi_subset (async):", requested_cli)

        if requested_cli:
            cmd += requested_cli

        # Launch in background with live log
        with open(log_path, "w", encoding="utf-8") as logf:
            proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, text=True)

        # Write a pid file so /status can find it
        with open(os.path.join(req_dir, "pid.txt"), "w") as pf:
            pf.write(str(proc.pid))

        # In a background thread, wait and write a done marker
        import threading
        def _wait_and_mark():
            ret = proc.wait()
            marker = "done.ok" if ret == 0 else "done.err"
            with open(os.path.join(req_dir, marker), "w") as mf:
                mf.write(str(ret))
            # Optionally cleanup raw folder on success
            if not persist_raw and ret == 0:
                # keep req_dir since user may still poll logs; but could cleanup later
                pass

        th = threading.Thread(target=_wait_and_mark, daemon=True)
        th.start()

        return {"req_id": req_id, "output_dir": output_dir}

    except Exception as e:
        if not persist_raw:
            shutil.rmtree(req_dir, ignore_errors=True)
        return JSONResponse(status_code=500, content={"error": str(e)})


# ---------- Status ----------
@app.get("/status/{req_id}")
def get_status(req_id: str):
    """
    Returns {"state": "running"|"finished"|"failed"} and output_dir if known.
    """
    req_dir = os.path.join(tempfile.gettempdir(), req_id)
    output_dir = os.path.join(req_dir, "ts_out")
    ok = os.path.join(req_dir, "done.ok")
    err = os.path.join(req_dir, "done.err")
    if os.path.exists(ok):
        return {"state": "finished", "output_dir": output_dir}
    if os.path.exists(err):
        # include last log lines
        log_file = os.path.join(req_dir, "ts_progress.log")
        tail = []
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                tail = f.readlines()[-20:]
        return {"state": "failed", "output_dir": output_dir, "tail": tail}
    # If neither marker exists but dir exists, assume running
    if os.path.isdir(req_dir):
        return {"state": "running", "output_dir": output_dir}
    return {"state": "unknown"}

if __name__ == "__main__":
    import uvicorn, os, sys
    host = os.getenv("AMIGO_SEG_HOST", "127.0.0.1")
    port = int(os.getenv("AMIGO_SEG_PORT", "5000"))
    # When frozen, run the object directly (no import string issues)
    if getattr(sys, "frozen", False):
        uvicorn.run(app, host=host, port=port, reload=False, log_level="warning")
    else:
        uvicorn.run("segmentator_api:app", host=host, port=port, reload=False, log_level="warning")