# segmentator_api.py
# FastAPI wrapper for TotalSegmentator with direct Python API calls
# - Safe flags: fast, ml, resample, output_type {nifti,dicom}
# - Optional targets for subset runs (via roi_subset)
# - Per-request staging under system TEMP
# - Progress log + /progress/{req_id}, /status/{req_id}

import os, sys, uuid, shutil, re, tempfile, logging, threading
from typing import Optional, List, Tuple

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse

from totalsegmentator.python_api import totalseg

# -------------------------------------------------------------------------
# App setup
# -------------------------------------------------------------------------
app = FastAPI()

BASE_DIR = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser("~")), "AMIGOpy")
MODELS_DIR = os.path.join(BASE_DIR, "Models")
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

print(f"[Segmentator API] Using base directory: {BASE_DIR}")
print(f"[Segmentator API] Using models directory: {MODELS_DIR}")

# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------
_normer_re = re.compile(r"[^a-z0-9]+")

def _norm_label(s: str) -> str:
    s = (s or "").strip().lower()
    s = _normer_re.sub("_", s)
    return re.sub(r"_+", "_", s).strip("_")

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

# -------------------------------------------------------------------------
# Totalseg runner
# -------------------------------------------------------------------------
def run_totalseg(input_path, output_dir, fast=False, ml=False,
                 resample=None, output_type="nifti", targets=None, log_path=None):
    args = {
        "input": input_path,
        "output": output_dir,
        "task": "total",
        "output_type": output_type,
        "fast": fast,
        "ml": ml,
        "resample": resample,
        "roi_subset": targets or [],
    }
    if log_path:
        sys.stdout = open(log_path, "w", encoding="utf-8")
        sys.stderr = sys.stdout
    totalseg(**args)

# -------------------------------------------------------------------------
# Health
# -------------------------------------------------------------------------
@app.get("/ping")
def ping():
    return {"status": "Segmentator is running"}

# -------------------------------------------------------------------------
# Progress
# -------------------------------------------------------------------------
@app.get("/progress/{req_id}")
def get_progress(req_id: str):
    req_dir = os.path.join(tempfile.gettempdir(), req_id)
    log_file = os.path.join(req_dir, "ts_progress.log")
    if not os.path.exists(log_file):
        return {"status": "not_found", "lines": []}
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    return {"status": "ok", "lines": lines[-10:]}  # last 10 lines

# -------------------------------------------------------------------------
# Main segmentation
# -------------------------------------------------------------------------
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

        # Map targets
        targets_cli = []
        if not ml and (output_type or "nifti").lower() == "nifti" and targets:
            targets_cli = _map_targets_for_cli(targets)

        # Run segmentation
        run_totalseg(
            input_path=input_path,
            output_dir=output_dir,
            fast=fast,
            ml=ml,
            resample=resample,
            output_type=output_type,
            targets=targets_cli,
            log_path=log_path
        )

        return {"req_id": req_id, "output_dir": output_dir}

    except Exception as e:
        if not persist_raw:
            shutil.rmtree(req_dir, ignore_errors=True)
        tail = []
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                tail = f.readlines()[-20:]
        return JSONResponse(status_code=500, content={"error": str(e), "stderr_tail": tail})

# -------------------------------------------------------------------------
# Async segmentation
# -------------------------------------------------------------------------
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
    req_id, req_dir, input_path, output_dir, log_path = _stage_dirs()

    try:
        # Save uploaded NIfTI
        with open(input_path, "wb") as f:
            f.write(await file.read())

        targets_cli = []
        if not ml and (output_type or "nifti").lower() == "nifti" and targets:
            targets_cli = _map_targets_for_cli(targets)

        def _worker():
            try:
                run_totalseg(
                    input_path=input_path,
                    output_dir=output_dir,
                    fast=fast,
                    ml=ml,
                    resample=resample,
                    output_type=output_type,
                    targets=targets_cli,
                    log_path=log_path
                )
                with open(os.path.join(req_dir, "done.ok"), "w") as mf:
                    mf.write("0")
            except Exception as e:
                with open(os.path.join(req_dir, "done.err"), "w") as mf:
                    mf.write(str(e))

        th = threading.Thread(target=_worker, daemon=True)
        th.start()

        return {"req_id": req_id, "output_dir": output_dir}

    except Exception as e:
        if not persist_raw:
            shutil.rmtree(req_dir, ignore_errors=True)
        return JSONResponse(status_code=500, content={"error": str(e)})

# -------------------------------------------------------------------------
# Status
# -------------------------------------------------------------------------
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
        tail = []
        log_file = os.path.join(req_dir, "ts_progress.log")
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                tail = f.readlines()[-20:]
        return {"state": "failed", "output_dir": output_dir, "tail": tail}
    if os.path.isdir(req_dir):
        return {"state": "running", "output_dir": output_dir}
    return {"state": "unknown"}

# -------------------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("AMIGO_SEG_HOST", "127.0.0.1")
    port = int(os.getenv("AMIGO_SEG_PORT", "5000"))
    if getattr(sys, "frozen", False):
        uvicorn.run(app, host=host, port=port, reload=False, log_level="warning")
    else:
        uvicorn.run("segmentator_api:app", host=host, port=port, reload=False, log_level="warning")
