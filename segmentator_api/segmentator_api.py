# segmentator_api.py
# FastAPI wrapper for TotalSegmentator (self-sufficient + frozen-safe)
# - No top-level TS import (lazy at call time)
# - Safe flags: fast, ml, resample, output_type {nifti,dicom}
# - Optional targets via roi_subset
# - Per-request staging under system TEMP
# - Progress log + /progress/{req_id}, /status/{req_id}

import os, sys, uuid, shutil, re, tempfile, threading, importlib, subprocess
from pathlib import Path
from typing import Optional, List, Tuple

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse

# -----------------------------------------------------------------------------
# Robust writable locations (works when double-clicking the EXE)
# -----------------------------------------------------------------------------
_local_root = Path(os.getenv("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "AMIGOpy"
_prog_root  = Path(os.getenv("PROGRAMDATA", r"C:\ProgramData")) / "AMIGOpy"

def _is_writable(p: Path) -> bool:
    try:
        p.mkdir(parents=True, exist_ok=True)
        t = p / ".amigo_test"
        t.write_text("ok", encoding="utf-8")
        t.unlink(missing_ok=True)
        return True
    except Exception:
        return False

def _first_writable(paths):
    for p in map(Path, paths):
        try:
            if _is_writable(p):
                return str(p.resolve())
        except Exception:
            continue
    return str(Path(tempfile.gettempdir()).resolve())

# Temp: prefer LocalAppData, then system temp
TMP_DIR = _first_writable([_local_root / "tmp", Path(tempfile.gettempdir())])
os.environ["TMPDIR"] = os.environ["TEMP"] = os.environ["TMP"] = TMP_DIR

# Models: prefer LocalAppData; if env var is set, use it only if writable; then ProgramData; else temp
_env_ts_home = os.getenv("TOTALSEG_HOME")
_models_candidates: List[Path] = [
    _local_root / "Models" / "TotalSegmentator",
]
if _env_ts_home:
    _models_candidates.append(Path(_env_ts_home))
_models_candidates.append(_prog_root / "Models" / "TotalSegmentator")

MODELS_DIR = _first_writable(_models_candidates)
os.environ["TOTALSEG_HOME"] = MODELS_DIR  # ensure TS sees this

# Base dir for any other app data
BASE_DIR = _first_writable([_local_root, Path(tempfile.gettempdir())])

# Avoid duplicate startup prints if module is imported twice by a runner
if not os.environ.get("AMIGO_SEG_PRINTED"):
    os.environ["AMIGO_SEG_PRINTED"] = "1"
    print(f"[Segmentator API] TMP_DIR={TMP_DIR}")
    print(f"[Segmentator API] TOTALSEG_HOME={MODELS_DIR}")
    print(f"[Segmentator API] BASE_DIR={BASE_DIR}")
    # Best-effort TS version (no import of package module)
    try:
        import importlib.metadata as _ilm
        _ts_ver = _ilm.version("TotalSegmentator")
    except Exception:
        _ts_ver = "unknown"
    print(f"[Segmentator API] TotalSegmentator package version: {_ts_ver}")

# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------
app = FastAPI()

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
_normer_re = re.compile(r"[^a-z0-9]+")

def _norm_label(s: str) -> str:
    s = (s or "").strip().lower()
    s = _normer_re.sub("_", s)
    return re.sub(r"_+", "_", s).strip("_")

def _map_targets_for_cli(raw_targets: Optional[str]) -> List[str]:
    """
    Preserve case (TS class names are case-sensitive).
    Map trailing '_l'/'_r' (any case) to 'left_'/'right_'.
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
    req_dir = os.path.join(TMP_DIR, req_id)
    os.makedirs(req_dir, exist_ok=True)
    input_path = os.path.join(req_dir, "input_ct.nii.gz")
    output_dir = os.path.join(req_dir, "ts_out")
    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(req_dir, "ts_progress.log")
    return req_id, req_dir, input_path, output_dir, log_path

# -----------------------------------------------------------------------------
# TotalSegmentator runner (lazy import, frozen-safe)
# -----------------------------------------------------------------------------
def _run_totalseg_inproc(
    input_path: str,
    output_dir: str,
    fast: bool = False,
    ml: bool = False,
    resample: Optional[float] = None,
    output_type: str = "nifti",
    targets: Optional[List[str]] = None,
    log_path: Optional[str] = None,
) -> int:
    """
    Try, in order:
      1) python_api.totalseg(**kwargs)
      2) in-process totalsegmentator.__main__.main (if present)
      3) subprocess console script "TotalSegmentator"
      4) subprocess module run: python -m totalsegmentator
    Return 0 on success, non-zero/127 with a helpful message if nothing is available.
    """
    # optional redirection for in-process paths
    old_out = old_err = None
    fh = None
    try:
        if log_path:
            fh = open(log_path, "w", encoding="utf-8")
            old_out, old_err = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = fh

        # ---------- 1) Python API ----------
        try:
            python_api = importlib.import_module("totalsegmentator.python_api")
            totalseg = getattr(python_api, "totalseg", None)
            if callable(totalseg):
                kwargs = {
                    "input": input_path,
                    "output": output_dir,
                    "task": "total",
                    "output_type": output_type,
                    "fast": fast,
                    "ml": ml,
                    "resample": resample,
                    "roi_subset": targets or [],
                }
                print("[Segmentator API] Using python_api.totalseg with kwargs:", kwargs)
                totalseg(**kwargs)
                return 0
            else:
                print("[Segmentator API] python_api.totalseg not found; trying __main__.")
        except Exception as e:
            print("[Segmentator API] python_api import/use failed; trying __main__. Error:", e)

        # ---------- 2) In-process __main__.main ----------
        try:
            main = importlib.import_module("totalsegmentator.__main__").main  # may not exist in some builds
            argv = [
                "TotalSegmentator",
                "-i", input_path,
                "-o", output_dir,
                "--output_type", (output_type or "nifti"),
            ]
            if fast:
                argv.append("--fast")
            if ml:
                argv.append("--ml")
            if resample and float(resample) > 0:
                argv += ["--resample", str(resample)]
            if targets:
                argv += ["--roi_subset"] + list(targets)

            print("[Segmentator API] Calling __main__.main with argv:", argv)
            old_argv = sys.argv[:]
            try:
                sys.argv = argv
                try:
                    main()
                    return 0
                except SystemExit as se:
                    code = se.code if isinstance(se.code, int) else 1
                    print("[Segmentator API] __main__.main exited with code:", code)
                    if code == 0:
                        return 0
            finally:
                sys.argv = old_argv
        except Exception as e:
            print("[Segmentator API] __main__ path unavailable; trying subprocess. Error:", e)

    finally:
        if fh:
            fh.flush()
            fh.close()
        if old_out is not None:
            sys.stdout, sys.stderr = old_out, old_err

    # ---------- 3) Subprocess: console script ----------
    # Build CLI argv once
    cli_argv = [
        "-i", input_path,
        "-o", output_dir,
        "--output_type", (output_type or "nifti"),
    ]
    if fast:
        cli_argv.append("--fast")
    if ml:
        cli_argv.append("--ml")
    if resample and float(resample) > 0:
        cli_argv += ["--resample", str(resample)]
    if targets:
        cli_argv += ["--roi_subset"] + list(targets)

    exe = shutil.which("TotalSegmentator") or shutil.which("TotalSegmentator.exe")
    if exe:
        try:
            with open(log_path or os.devnull, "a", encoding="utf-8", errors="ignore") as lf:
                lf.write("[Segmentator API] Running console script: " + exe + " " + " ".join(cli_argv) + "\n")
                proc = subprocess.run([exe] + cli_argv, stdout=lf, stderr=lf, text=True)
                return int(proc.returncode or 0)
        except Exception as e:
            with open(log_path or os.devnull, "a", encoding="utf-8", errors="ignore") as lf:
                lf.write(f"[Segmentator API] Console script failed: {e}\n")

    # ---------- 4) Subprocess: python -m totalsegmentator ----------
    try:
        with open(log_path or os.devnull, "a", encoding="utf-8", errors="ignore") as lf:
            cmd = [sys.executable, "-m", "totalsegmentator"] + cli_argv
            lf.write("[Segmentator API] Running module: " + " ".join(cmd) + "\n")
            proc = subprocess.run(cmd, stdout=lf, stderr=lf, text=True)
            return int(proc.returncode or 0)
    except Exception as e:
        with open(log_path or os.devnull, "a", encoding="utf-8", errors="ignore") as lf:
            lf.write(f"[Segmentator API] Module execution failed: {e}\n")
            lf.write("[Segmentator API] No runnable TotalSegmentator entrypoint found.\n")
        # 127 is the classic "command not found"
        return 127

# -----------------------------------------------------------------------------
# Health
# -----------------------------------------------------------------------------
@app.get("/ping")
def ping():
    return {"status": "Segmentator is running"}

# Optional alternate endpoint some clients probe
@app.get("/health")
def health():
    return {"ok": True}

# -----------------------------------------------------------------------------
# Progress
# -----------------------------------------------------------------------------
@app.get("/progress/{req_id}")
def get_progress(req_id: str):
    req_dir = os.path.join(TMP_DIR, req_id)
    log_file = os.path.join(req_dir, "ts_progress.log")
    if not os.path.exists(log_file):
        return {"status": "not_found", "lines": []}
    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        lines = []
    return {"status": "ok", "lines": lines[-10:]}

# -----------------------------------------------------------------------------
# Main segmentation
# -----------------------------------------------------------------------------
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

        # Map targets for roi_subset (only relevant when not merging)
        ts_targets: List[str] = []
        if not ml and (output_type or "nifti").lower() == "nifti" and targets:
            ts_targets = _map_targets_for_cli(targets)

        ret = _run_totalseg_inproc(
            input_path=input_path,
            output_dir=output_dir,
            fast=fast,
            ml=ml,
            resample=resample,
            output_type=output_type,
            targets=ts_targets,
            log_path=log_path,
        )
        if ret != 0:
            tail = []
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    tail = f.readlines()[-20:]
            return JSONResponse(
                status_code=500,
                content={
                    "error": f"TotalSegmentator failed (exit {ret})",
                    "stderr_tail": tail,
                    "req_id": req_id,
                    "output_dir": output_dir,
                },
            )

        return {"req_id": req_id, "output_dir": output_dir}

    except Exception as e:
        if not persist_raw:
            shutil.rmtree(req_dir, ignore_errors=True)
        tail = []
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    tail = f.readlines()[-20:]
            except Exception:
                pass
        return JSONResponse(status_code=500, content={"error": str(e), "stderr_tail": tail})

# -----------------------------------------------------------------------------
# Async segmentation
# -----------------------------------------------------------------------------
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
    Starts TotalSegmentator in a background thread and returns immediately with req_id.
    Use /progress/{req_id} and /status/{req_id}.
    """
    req_id, req_dir, input_path, output_dir, log_path = _stage_dirs()

    try:
        with open(input_path, "wb") as f:
            f.write(await file.read())

        ts_targets: List[str] = []
        if not ml and (output_type or "nifti").lower() == "nifti" and targets:
            ts_targets = _map_targets_for_cli(targets)

        # Clear/create log file early
        try:
            open(log_path, "w", encoding="utf-8").close()
        except Exception:
            pass

        def _worker():
            ret = 1
            try:
                ret = _run_totalseg_inproc(
                    input_path=input_path,
                    output_dir=output_dir,
                    fast=fast,
                    ml=ml,
                    resample=resample,
                    output_type=output_type,
                    targets=ts_targets,
                    log_path=log_path,
                )
            except Exception as e:
                try:
                    with open(log_path, "a", encoding="utf-8") as lf:
                        lf.write("\n[FATAL] " + str(e) + "\n")
                except Exception:
                    pass
            finally:
                marker = "done.ok" if ret == 0 else "done.err"
                try:
                    with open(os.path.join(req_dir, marker), "w") as mf:
                        mf.write(str(ret))
                except Exception:
                    pass

        threading.Thread(target=_worker, daemon=True).start()
        return {"req_id": req_id, "output_dir": output_dir}

    except Exception as e:
        if not persist_raw:
            shutil.rmtree(req_dir, ignore_errors=True)
        return JSONResponse(status_code=500, content={"error": str(e)})

# -----------------------------------------------------------------------------
# Status
# -----------------------------------------------------------------------------
@app.get("/status/{req_id}")
def get_status(req_id: str):
    """
    Returns {"state": "running"|"finished"|"failed"} and output_dir if known.
    """
    req_dir = os.path.join(TMP_DIR, req_id)
    output_dir = os.path.join(req_dir, "ts_out")
    ok = os.path.join(req_dir, "done.ok")
    err = os.path.join(req_dir, "done.err")
    if os.path.exists(ok):
        return {"state": "finished", "output_dir": output_dir}
    if os.path.exists(err):
        tail = []
        log_file = os.path.join(req_dir, "ts_progress.log")
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    tail = f.readlines()[-20:]
            except Exception:
                pass
        return {"state": "failed", "output_dir": output_dir, "tail": tail}
    if os.path.isdir(req_dir):
        return {"state": "running", "output_dir": output_dir}
    return {"state": "unknown"}

# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Lazy import uvicorn to keep module import clean for frozen builds
    import uvicorn
    host = os.getenv("AMIGO_SEG_HOST", "127.0.0.1")
    port = int(os.getenv("AMIGO_SEG_PORT", "5000"))
    # When frozen, run object directly; when dev, use module:app
    if getattr(sys, "frozen", False):
        uvicorn.run(app, host=host, port=port, reload=False, log_level="warning")
    else:
        uvicorn.run("segmentator_api:app", host=host, port=port, reload=False, log_level="warning")
