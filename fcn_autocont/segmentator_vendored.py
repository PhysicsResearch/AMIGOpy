# fcn_autocont/segmentator_vendored.py
# -*- coding: utf-8 -*-
from __future__ import annotations

import os, sys, time, traceback, json, subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# 1) Lock in the stdlib 'statistics' module so vendored 'statistics.py' can't shadow it
import statistics as _stdlib_statistics
sys.modules.setdefault("statistics", _stdlib_statistics)

# 2) Locate a vendored TS checkout and put it on sys.path (append so stdlib/site-packages win)
def _vendor_root() -> Path:
    env = os.getenv("AMIGO_TOTALSEG_VENDOR_DIR")
    if env:
        return Path(env)
    here = Path(__file__).resolve()
    amigo_root = here.parents[1]  # AMIGOpy/
    return (amigo_root / "third_party" / "TotalSegmentator").resolve()

_VENDOR_ROOT = _vendor_root()
if not _vendor_root().exists():
    raise FileNotFoundError(
        f"Vendored folder not found: {_VENDOR_ROOT}\n"
        "Expected at <AMIGOpy>/third_party/TotalSegmentator or set AMIGO_TOTALSEG_VENDOR_DIR."
    )
_vendor_path = str(_VENDOR_ROOT)
if _vendor_path not in sys.path:
    sys.path.append(_vendor_path)

# Try early import (helps fail fast if repo is missing)
try:
    import totalsegmentator as ts_api  # noqa: F401
except Exception as e:
    raise ImportError(
        f"Failed to import vendored 'totalsegmentator' from {_VENDOR_ROOT}\n{e}"
    )

# ---------------------------------------------------------------------------

import numpy as np
import SimpleITK as sitk

# Optional Qt message box (if available)
try:
    from PyQt5.QtWidgets import QMessageBox, QApplication
except Exception:
    QMessageBox = None
    QApplication = None

# ------------ AMIGOpy integration utilities ----------------------------------

def _show_warn(title: str, text: str, details: str | None = None, parent=None):
    # If Qt isn't available, just print
    if QMessageBox is None or QApplication is None:
        print(f"[WARN] {title}: {text}")
        if details: print(details)
        return

    # Only create/parent widgets on the GUI (main) thread
    try:
        app = QApplication.instance()
        on_gui = bool(app and (app.thread() == QThread.currentThread()))
    except Exception:
        on_gui = False

    if not on_gui:
        # Worker thread: avoid QWidget creation; just log
        print(f"[WARN] {title}: {text}")
        if details: print(details)
        return

    # GUI thread: safe to create a message box (now it's fine to pass parent)
    box = QMessageBox(QMessageBox.Warning, title, text, parent=parent)
    if details:
        box.setDetailedText(details)
    box.exec_()


def _ensure(owner, attr, default):
    if not hasattr(owner, attr) or getattr(owner, attr) is None:
        setattr(owner, attr, default)
    return getattr(owner, attr)

def _ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p

def _appdata_root() -> Path:
    base = os.getenv("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
    return _ensure_dir(Path(base) / "AMIGOpy")

def _work_paths() -> Dict[str, Path]:
    """
    Returns:
      root:   %LOCALAPPDATA%\AMIGOpy
      tmp:    %LOCALAPPDATA%\AMIGOpy\tmp
      models: %LOCALAPPDATA%\AMIGOpy\Models\TotalSegmentator  (unless TOTALSEG_HOME already set)
      logs:   %LOCALAPPDATA%\AMIGOpy\logs
    """
    root = _appdata_root()
    tmp  = _ensure_dir(root / "tmp")
    logs = _ensure_dir(root / "logs")

    env_home = os.getenv("TOTALSEG_HOME")
    if env_home:
        models = _ensure_dir(Path(env_home))
    else:
        models = _ensure_dir(root / "Models" / "TotalSegmentator")

    return {"root": root, "tmp": tmp, "models": models, "logs": logs}

# ------------ Flexible vendor path (for subprocess PYTHONPATH) ---------------

ENV_VENDOR_DIR   = "AMIGOPY_VENDOR_TOTALSEG_DIR"
ENV_AMIGOPY_ROOT = "AMIGOPY_ROOT"

def _candidate_roots_for_amigopy() -> List[Path]:
    cands: List[Path] = []
    if os.getenv(ENV_AMIGOPY_ROOT):
        cands.append(Path(os.getenv(ENV_AMIGOPY_ROOT)).resolve())
    if getattr(sys, "frozen", False):
        cands.append(Path(sys.executable).resolve().parent)
    try:
        here = Path(__file__).resolve()
        cands.append(here.parents[1])  # AMIGOpy root
    except Exception:
        pass
    cands.append(Path.cwd())
    if os.name == "nt":
        p = Path(r"C:\AMIGOpy")
        if p.exists():
            cands.append(p)
    out: List[Path] = []
    seen = set()
    for p in cands:
        if p not in seen:
            out.append(p); seen.add(p)
    return out

def _resolve_vendor_root() -> Path:
    hinted = os.getenv(ENV_VENDOR_DIR)
    if hinted:
        p = Path(hinted).resolve()
        if (p / "totalsegmentator").is_dir() or (p / "python_api.py").exists():
            return p
    for root in _candidate_roots_for_amigopy():
        vendor = (root / "third_party" / "TotalSegmentator").resolve()
        if (vendor / "totalsegmentator").is_dir() or (vendor / "python_api.py").exists():
            return vendor
    return _VENDOR_ROOT  # fall back to the earlier-validated one

def _ensure_vendor_on_path() -> Path:
    repo = _resolve_vendor_root()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    return repo

# ------------ Export / import to AMIGOpy structures ---------------------------

from fcn_export.export_nii import export_nifti  # your existing exporter

def _ensure_series_containers(
    owner, patient_id: str, study_id: str, modality: str, series_index: int
) -> Dict[str, Any]:
    dicom = _ensure(owner, "dicom_data", {})
    dicom.setdefault(patient_id, {}) \
         .setdefault(study_id, {}) \
         .setdefault(modality, [])
    lst = dicom[patient_id][study_id][modality]
    while len(lst) <= int(series_index):
        lst.append({})
    series = lst[int(series_index)]
    if not isinstance(series, dict):
        series = lst[int(series_index)] = {}

    series.setdefault("structures", {})
    series.setdefault("structures_keys", [])
    series.setdefault("structures_names", [])

    sk = series["structures_keys"]
    sn = series["structures_names"]
    if len(sn) < len(sk):
        sn.extend([""] * (len(sk) - len(sn)))
    elif len(sk) < len(sn):
        del sn[len(sk):]

    return series

def _import_masks_into_series(owner, out_dir: Path,
                              patient_id: str, study_id: str,
                              modality: str, series_index: int) -> int:
    if not out_dir.is_dir():
        return 0

    series = _ensure_series_containers(owner, patient_id, study_id, modality, series_index)
    structures = series["structures"]
    keys_list: List[str] = series["structures_keys"]
    names_list: List[str] = series["structures_names"]

    start_idx = len(keys_list)
    files = sorted(
        p for p in out_dir.rglob("*")
        if p.suffix == ".nii" or p.suffixes == [".nii", ".gz"]
    )

    imported = 0
    for f in files:
        try:
            img = sitk.ReadImage(str(f))
            arr = sitk.GetArrayFromImage(img)  # (z, y, x)
            arr = np.flip(arr, axis=1)         # match your orientation
            if not np.any(arr):
                continue
            mask = (arr > 0).astype(np.uint8)

            s_idx = start_idx + imported
            s_key = f"Structure_{s_idx:03d}"
            name  = f.stem
            if name.endswith(".nii"):
                name = name[:-4]

            keys_list.append(s_key)
            names_list.append(name)
            if s_key not in structures:
                structures[s_key] = {}
            structures[s_key]["Mask3D"] = mask
            structures[s_key]["Name"]   = name
            imported += 1
        except Exception as e:
            print(f"[TS][import] Failed to import {f}: {e}")

    # Clean empty subfolders
    try:
        for root, _, _ in os.walk(out_dir, topdown=False):
            if not os.listdir(root):
                os.rmdir(root)
    except Exception:
        pass

    return imported

# ------------ TotalSegmentator execution (vendored, killable) -----------------

def _normalize_task(task: str) -> str:
    t = (task or "total").strip()
    aliases = {"total_ct": "total"}
    return aliases.get(t, t)

def _targets_from_params(params: Dict[str, Any]) -> List[str]:
    trg = params.get("targets")
    if not trg:
        return []
    if isinstance(trg, str):
        parts = [x.strip() for x in trg.split(",")]
    else:
        parts = list(trg)
    return [x for x in parts if x]

def _device_from_params(params: Dict[str, Any]) -> str:
    dev = (params.get("device") or "cpu").strip().lower()
    if dev in ("gpu0", "gpu:0"):
        return "gpu:0"
    if dev not in ("cpu", "gpu", "mps") and not dev.startswith("gpu:"):
        return "cpu"
    return dev

def _write_json(p: Path, obj: Any):
    try:
        p.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    except Exception:
        pass

def _build_ts_kwargs(input_nii: Path, out_dir: Path, params: Dict[str, Any]) -> Dict[str, Any]:
    task    = _normalize_task(params.get("task", "total"))
    targets = _targets_from_params(params)
    fast    = bool(params.get("fast", False))
    fastest = bool(params.get("fastest", False))
    device  = _device_from_params(params)
    return dict(
        input=str(input_nii),
        output=str(out_dir),
        ml=False,                        # per-organ files
        task=task,
        fast=fast,
        fastest=fastest,
        roi_subset=targets if targets else None,
        output_type="nifti",             # we import masks ourselves
        device=device,
        quiet=True,
        verbose=False,
        no_derived_masks=False,
        skip_saving=False,
    )

def _run_ts_subprocess(owner, kwargs, log_dir: Path, env_extra: Dict[str, str]):
    import os, sys, time, signal, subprocess

    # --- env for child
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)

    args_json   = log_dir / "_ts_args.json"
    runner_py   = log_dir / "_ts_run.py"
    stdout_path = log_dir / "_ts_stdout.txt"
    stderr_path = log_dir / "_ts_stderr.txt"

    _write_json(args_json, kwargs)

    # Write a Windows-safe runner with __main__ guard (prevents multiprocessing crash)
    runner_py.write_text(
        "import json, sys, os, sysconfig, importlib.util, multiprocessing\n"
        "if os.name == 'nt':\n"
        "    multiprocessing.freeze_support()\n"
        "stdlib_dir = sysconfig.get_paths().get('stdlib') or ''\n"
        "stats_path = os.path.join(stdlib_dir, 'statistics.py')\n"
        "if os.path.isfile(stats_path):\n"
        "    spec = importlib.util.spec_from_file_location('statistics', stats_path)\n"
        "    mod = importlib.util.module_from_spec(spec)\n"
        "    spec.loader.exec_module(mod)\n"
        "    sys.modules['statistics'] = mod\n"
        "else:\n"
        "    import statistics as mod\n"
        "    sys.modules['statistics'] = mod\n"
        "from totalsegmentator import python_api as ts\n"
        "def _main():\n"
        "    with open(sys.argv[1], 'r', encoding='utf-8') as f:\n"
        "        k = json.load(f)\n"
        "    ts.totalsegmentator(**k)\n"
        "if __name__ == '__main__':\n"
        "    _main()\n",
        encoding="utf-8"
    )

    # Launch options: new group on Windows, detached from any console; POSIX gets a new session.
    creationflags = 0
    preexec_fn = None
    if os.name == "nt":
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        DETACHED_PROCESS         = 0x00000008
        creationflags = CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS
    else:
        preexec_fn = os.setsid  # new process group on POSIX

    def _cancelled() -> bool:
        segwin = getattr(owner, "segwin", owner)
        return bool(getattr(segwin, "_seg_cancel", False))

    with open(stdout_path, "w", encoding="utf-8") as so, open(stderr_path, "w", encoding="utf-8") as se:
        proc = subprocess.Popen(
            [sys.executable, str(runner_py), str(args_json)],
            stdout=so, stderr=se, env=env,
            creationflags=creationflags,
            preexec_fn=preexec_fn
        )

        try:
            while True:
                rc = proc.poll()
                if rc is not None:
                    break

                if _cancelled():
                    # 1) Try graceful terminate
                    try:
                        proc.terminate()
                    except Exception:
                        pass

                    # 2) Short wait
                    for _ in range(30):
                        if proc.poll() is not None:
                            break
                        time.sleep(0.1)

                    # 3) Hard kill if still alive
                    if proc.poll() is None:
                        try:
                            proc.kill()
                        except Exception:
                            pass

                    # 4) Windows: nuke the entire child tree (TS + workers)
                    if os.name == "nt" and proc.poll() is None:
                        try:
                            subprocess.run(
                                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                check=False,
                            )
                        except Exception:
                            pass

                    return False, "Stopped by user"

                time.sleep(0.3)
        finally:
            pass

    if proc.returncode == 0:
        return True, "ok"

    # Include last lines of stderr in the message for quick diagnosis
    try:
        tail = "\n".join((stderr_path.read_text(encoding="utf-8", errors="ignore").splitlines())[-60:])
        return False, "TotalSegmentator failed:\n" + tail
    except Exception:
        return False, "TotalSegmentator failed (no stderr available)."


def _run_ts_subprocess(owner, kwargs, log_dir: Path, env_extra: Dict[str, str]):
    import os, sys, time, subprocess

    # --- env for child
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)

    args_json   = log_dir / "_ts_args.json"
    runner_py   = log_dir / "_ts_run.py"
    stdout_path = log_dir / "_ts_stdout.txt"
    stderr_path = log_dir / "_ts_stderr.txt"

    _write_json(args_json, kwargs)

    # Windows-safe runner: main guard + freeze_support() to keep nnU-Net from crashing
    runner_py.write_text(
        "import json, sys, os, sysconfig, importlib.util, multiprocessing\n"
        "if os.name == 'nt':\n"
        "    multiprocessing.freeze_support()\n"
        "stdlib_dir = sysconfig.get_paths().get('stdlib') or ''\n"
        "stats_path = os.path.join(stdlib_dir, 'statistics.py')\n"
        "if os.path.isfile(stats_path):\n"
        "    spec = importlib.util.spec_from_file_location('statistics', stats_path)\n"
        "    mod = importlib.util.module_from_spec(spec)\n"
        "    spec.loader.exec_module(mod)\n"
        "    sys.modules['statistics'] = mod\n"
        "else:\n"
        "    import statistics as mod\n"
        "    sys.modules['statistics'] = mod\n"
        "from totalsegmentator import python_api as ts\n"
        "def _main():\n"
        "    with open(sys.argv[1], 'r', encoding='utf-8') as f:\n"
        "        k = json.load(f)\n"
        "    ts.totalsegmentator(**k)\n"
        "if __name__ == '__main__':\n"
        "    _main()\n",
        encoding="utf-8"
    )

    # Use pythonw if available (no console), else hide window via flags
    py = sys.executable
    if os.name == 'nt':
        pyw = py.replace("python.exe", "pythonw.exe")
        if os.path.exists(pyw):
            py = pyw

    creationflags = 0
    startupinfo = None
    preexec_fn = None

    if os.name == "nt":
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        CREATE_NO_WINDOW         = 0x08000000
        creationflags = CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
    else:
        import os as _os
        preexec_fn = _os.setsid  # POSIX: new session/group

    def _cancelled() -> bool:
        segwin = getattr(owner, "segwin", owner)
        return bool(getattr(segwin, "_seg_cancel", False))

    with open(stdout_path, "w", encoding="utf-8") as so, open(stderr_path, "w", encoding="utf-8") as se:
        proc = subprocess.Popen(
            [py, str(runner_py), str(args_json)],
            stdout=so, stderr=se, env=env,
            creationflags=creationflags,
            startupinfo=startupinfo,
            preexec_fn=preexec_fn,
            close_fds=True
        )

        try:
            while True:
                rc = proc.poll()
                if rc is not None:
                    break

                if _cancelled():
                    # Try graceful terminate, then kill
                    try: proc.terminate()
                    except Exception: pass

                    for _ in range(25):
                        if proc.poll() is not None: break
                        time.sleep(0.1)

                    if proc.poll() is None:
                        try: proc.kill()
                        except Exception: pass

                    # Last resort on Windows: kill the whole tree WITHOUT showing a window
                    if os.name == "nt" and proc.poll() is None:
                        CREATE_NO_WINDOW = 0x08000000
                        si = subprocess.STARTUPINFO()
                        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        si.wShowWindow = 0
                        subprocess.run(
                            ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            check=False, creationflags=CREATE_NO_WINDOW, startupinfo=si
                        )
                    return False, "Stopped by user"

                time.sleep(0.3)
        finally:
            pass

    if proc.returncode == 0:
        return True, "ok"

    try:
        tail = "\n".join((stderr_path.read_text(encoding="utf-8", errors="ignore").splitlines())[-60:])
        return False, "TotalSegmentator failed:\n" + tail
    except Exception:
        return False, "TotalSegmentator failed (no stderr available)."

def _run_totalseg(owner, input_nii: Path, out_dir: Path, params: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Returns (ok, message). On success, out_dir will contain per-organ NIfTI masks.
    Runs in a subprocess so it can be stopped mid-run.
    """
    repo = _ensure_vendor_on_path()
    ap = _work_paths()

    env_extra = {}
    if "TOTALSEG_HOME" not in os.environ:
        env_extra["TOTALSEG_HOME"] = str(ap["models"])

    # Optional but recommended on CPU-only laptops:
    dev = _device_from_params(params)
    if dev == "cpu":
        env_extra.update({
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
            "ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS": "1",
            "TOTALSEG_NUM_WORKERS": "0",
            "NNUNET_NUM_THREADS_PREPROCESSING": "1",
            "NNUNET_NUM_THREADS_NIFTI": "1",
        })

    kwargs = _build_ts_kwargs(input_nii, out_dir, params)
    _write_json(out_dir / "_ts_call.json",
                {"kwargs": kwargs,
                 "env": {"TOTALSEG_HOME": env_extra.get("TOTALSEG_HOME",
                                                       os.getenv("TOTALSEG_HOME"))}})
    ok, msg = _run_ts_subprocess(owner, kwargs, out_dir, env_extra)
    return ok, msg
# ------------ Public entry point ---------------------------------------------

def run_totalseg_for_series(owner, series_list: List[Dict[str, Any]], params: Dict[str, Any]) -> None:
    """
    Replaces the HTTP client call. Usage:
      run_totalseg_for_series(self, series_list, params)

    Each item of series_list:
      { "patient": <pid>, "study": <sid>, "modality": <mod>, "index": <series_index> }

    params example for CT total subset:
      { "task": "total", "fast": True, "targets": ["liver", "spleen"], "device": "cpu" }
    """
    ap = _work_paths()
    tmp  = ap["tmp"]

    for meta in series_list or []:
        # Respect cancel before starting a new series
        if getattr(getattr(owner, "segwin", owner), "_seg_cancel", False):
            break

        pid = meta["patient"]; sid = meta["study"]; mod = meta["modality"]; idx = int(meta["index"])
        tag = f"{pid}/{sid}/{mod}[{idx}]"
        try:
            # 1) export NIfTI
            req_dir   = _ensure_dir(tmp / f"ts_req_{int(time.time()*1000)}")
            input_nii = Path(str(req_dir / "input.nii.gz"))
            out_dir   = _ensure_dir(req_dir / "out")

            nii_path = export_nifti(
                owner, pid, sid, mod, idx,
                output_folder=str(req_dir),
                file_name="input.nii.gz"
            )
            if not nii_path or not Path(nii_path).exists():
                _show_warn("TotalSegmentator", f"Failed to export NIfTI for {tag}", parent=getattr(owner, "segwin", None) or owner)
                continue

            # Respect cancel right before starting TS
            if getattr(getattr(owner, "segwin", owner), "_seg_cancel", False):
                break

            # 2) run TS (vendored, killable)
            ok, msg = _run_totalseg(owner, input_nii, out_dir, params or {})
            if not ok:
                _show_warn("TotalSegmentator failed", msg, parent=getattr(owner, "segwin", None) or owner)
                continue

            # 3) import output masks
            n = _import_masks_into_series(owner, out_dir, pid, sid, mod, idx)
            print(f"[TS] Imported {n} structures for {tag} from {out_dir}")

        except Exception as ex:
            tb = traceback.format_exc()
            _show_warn("TotalSegmentator error", f"{ex}", tb, parent=getattr(owner, "segwin", None) or owner)

    # Optional: refresh your DICOM tree
    try:
        from fcn_load.populate_dcm_list import populate_DICOM_tree
        populate_DICOM_tree(owner)
    except Exception:
        pass
