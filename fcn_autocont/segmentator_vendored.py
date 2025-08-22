# fcn_autocont/segmentator_vendored.py
# -*- coding: utf-8 -*-
from __future__ import annotations

import os, sys, time, traceback, json
from pathlib import Path
from typing import Dict, List, Any, Tuple

# ---------------------------------------------------------------------------
# Make sure stdlib 'statistics' is used (avoid any vendored shadowing)
import statistics as _stdlib_statistics
sys.modules.setdefault("statistics", _stdlib_statistics)

# Optional Qt (for warnings shown on the GUI thread only)
try:
    from PyQt5.QtWidgets import QMessageBox, QApplication
    from PyQt5.QtCore import QThread
except Exception:
    QMessageBox = None
    QApplication = None
    QThread = None

# Third-party runtime imports
import numpy as np
import SimpleITK as sitk

# Your exporter
from fcn_export.export_nii import export_nifti


# ======================== vendor / worker discovery ==========================

def _worker_exists_in_bundle() -> bool:
    """True if we are frozen and a bundled worker exe is present."""
    if not getattr(sys, "frozen", False):
        return False
    base = Path(sys.executable).parent
    candidates = [
        base / ("segmentator_worker.exe" if os.name == "nt" else "segmentator_worker"),
        base / "workers" / "cpu" / ("segmentator_worker.exe" if os.name == "nt" else "segmentator_worker"),
        base / "workers" / "cuda" / ("segmentator_worker.exe" if os.name == "nt" else "segmentator_worker"),
    ]
    return any(p.exists() for p in candidates)

def _ensure_vendor_on_path() -> Path:
    """
    Dev convenience: if a local vendor tree exists, add it to sys.path.
    Packaged app: do NOT require a vendor tree (the worker exe has TS inside).
    Never raises.
    """
    # 1) explicit override
    env_dir = os.environ.get("AMIGO_TOTALSEG_VENDOR_DIR")
    if env_dir:
        p = Path(env_dir)
        if p.is_dir():
            if str(p) not in sys.path:
                sys.path.insert(0, str(p))
            return p

    # 2) packaged app with a bundled worker → nothing to add, just return app dir
    if _worker_exists_in_bundle():
        return Path(sys.executable).parent if getattr(sys, "frozen", False) else Path.cwd()

    # 3) dev mode: try project-local vendor tree (<repo>/third_party/TotalSegmentator)
    try:
        here = Path(__file__).resolve()
        dev_vendor = here.parents[1] / "third_party" / "TotalSegmentator"
        if dev_vendor.is_dir():
            if str(dev_vendor) not in sys.path:
                sys.path.insert(0, str(dev_vendor))
            return dev_vendor
    except Exception:
        pass

    # 4) last resort: do nothing; let an installed 'totalsegmentator' be importable from site-packages
    return Path.cwd()


# ============================== UI helpers ===================================

def _show_warn(title: str, text: str, details: str | None = None, parent=None):
    """Show a warning on the GUI thread; otherwise just log to console."""
    if QMessageBox is None or QApplication is None:
        print(f"[WARN] {title}: {text}")
        if details:
            print(details)
        return

    try:
        app = QApplication.instance()
        on_gui = bool(app and QThread and (app.thread() == QThread.currentThread()))
    except Exception:
        on_gui = False

    if not on_gui:
        print(f"[WARN] {title}: {text}")
        if details:
            print(details)
        return

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
    models = _ensure_dir(Path(env_home)) if env_home else _ensure_dir(root / "Models" / "TotalSegmentator")

    return {"root": root, "tmp": tmp, "models": models, "logs": logs}


# ========================= TS kwargs / env helpers ===========================

def _normalize_task(task: str) -> str:
    t = (task or "total").strip()
    return {"total_ct": "total"}.get(t, t)

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





# If these helpers already exist in your file, you can keep your originals and
# delete these guarded versions. The guards avoid duplicate definitions.
if '_ensure_series_containers' not in globals():
    def _ensure_series_containers(owner, patient_id: str, study_id: str, modality: str, series_index: int) -> Dict[str, Any]:
        dicom = getattr(owner, "medical_image", None)
        if dicom is None:
            dicom = {}
            setattr(owner, "medical_image", dicom)
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

if '_is_nii_path' not in globals():
    def _is_nii_path(p: Path) -> bool:
        """True for *.nii or *.nii.gz (robust)."""
        if p.suffix.lower() == ".nii":
            return True
        sfx = "".join(s.lower() for s in p.suffixes[-2:])
        return sfx == ".nii.gz"

def _import_masks_into_series(owner, out_dir: Path,
                              patient_id: str, study_id: str,
                              modality: str, series_index: int) -> int:
    """
    Import per-organ NIfTI masks from TotalSegmentator. If only a single
    multi-label file exists, split it into binary masks per label.
    Returns number of structures imported.
    """
    if not out_dir.is_dir():
        return 0

    series = _ensure_series_containers(owner, patient_id, study_id, modality, series_index)
    structures = series["structures"]
    keys_list: List[str] = series["structures_keys"]
    names_list: List[str] = series["structures_names"]

    start_idx = len(keys_list)

    files = sorted(p for p in out_dir.rglob("*") if _is_nii_path(p))

    # Debug: record what we saw
    try:
        (out_dir / "_ts_import_seen.json").write_text(
            json.dumps({"files": [str(f) for f in files]}, indent=2),
            encoding="utf-8"
        )
    except Exception:
        pass

    imported = 0

    # Path A: many per-organ files (typical TS 'nifti' output)
    for f in files:
        try:
            img = sitk.ReadImage(str(f))
            arr = sitk.GetArrayFromImage(img)  # (z, y, x)
            # Adjust orientation if your app expects it
            arr = np.flip(arr, axis=1)
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
            structures.setdefault(s_key, {})
            structures[s_key]["Mask3D"] = mask
            structures[s_key]["Name"]   = name
            imported += 1
        except Exception as e:
            print(f"[TS][import] Failed to import {f}: {e}")

    # Path B: fallback for a single multi-label file (e.g., segmentations.nii.gz)
    if imported == 0 and len(files) == 1:
        try:
            f = files[0]
            img = sitk.ReadImage(str(f))
            arr = sitk.GetArrayFromImage(img)
            arr = np.flip(arr, axis=1)
            labels = [int(v) for v in np.unique(arr) if int(v) > 0]
            for lv in labels:
                m = (arr == lv).astype(np.uint8)
                s_idx = start_idx + imported
                s_key = f"Structure_{s_idx:03d}"
                name  = f"Label_{lv}"
                keys_list.append(s_key)
                names_list.append(name)
                structures.setdefault(s_key, {})["Mask3D"] = m
                structures[s_key]["Name"] = name
                imported += 1
        except Exception as e:
            print(f"[TS][import] Failed to split multi-label: {e}")

    # Clean empty subfolders (best effort)
    try:
        for root, _, _ in os.walk(out_dir, topdown=False):
            if not os.listdir(root):
                os.rmdir(root)
    except Exception:
        pass

    # Debug: write import count
    try:
        (out_dir / "_ts_import_result.txt").write_text(f"imported={imported}\n", encoding="utf-8")
    except Exception:
        pass

    return imported














# =========================== subprocess runner ===============================

def _run_ts_subprocess(owner, kwargs, log_dir: Path, env_extra: Dict[str, str]):
    """
    Launch TotalSegmentator as a child process.
    - Dev: run a tiny runner via python/pythonw with a __main__ guard.
    - Frozen app: prefer segmentator_worker(.exe) next to sys.executable.
    - Windows: no popups; new process group; tree-kill with taskkill as last resort.
    - POSIX: new session (setsid); kill the group.
    """
    import subprocess

    # ---- environment for the child
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)

    # ---- paths
    args_json   = log_dir / "_ts_args.json"
    runner_py   = log_dir / "_ts_run.py"   # dev-mode runner (not used when frozen-worker exists)
    stdout_path = log_dir / "_ts_stdout.txt"
    stderr_path = log_dir / "_ts_stderr.txt"

    _write_json(args_json, kwargs)

    # ---- create a Windows-safe runner for dev mode (multiprocessing-friendly)
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

    # ---- choose child command
    if getattr(sys, "frozen", False):
        worker_name = "segmentator_worker.exe" if os.name == "nt" else "segmentator_worker"
        worker_path = os.path.join(os.path.dirname(sys.executable), worker_name)
        if os.path.exists(worker_path):
            cmd = [worker_path, str(args_json)]
        else:
            cmd = [sys.executable, str(runner_py), str(args_json)]
    else:
        py = sys.executable
        if os.name == "nt":
            pyw = py.replace("python.exe", "pythonw.exe")
            if os.path.exists(pyw):
                py = pyw
        cmd = [py, str(runner_py), str(args_json)]

    # ---- launch flags (hide windows; isolate process group/session)
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
        preexec_fn = _os.setsid  # new session for the child

    def _cancelled() -> bool:
        segwin = getattr(owner, "segwin", owner)
        return bool(getattr(segwin, "_seg_cancel", False))

    # ---- run
    with open(stdout_path, "w", encoding="utf-8") as so, open(stderr_path, "w", encoding="utf-8") as se:
        proc = subprocess.Popen(
            cmd,
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
                    # 1) graceful terminate
                    try:
                        proc.terminate()
                    except Exception:
                        pass

                    # 2) brief wait
                    for _ in range(30):
                        if proc.poll() is not None:
                            break
                        time.sleep(0.1)

                    # 3) hard kill if still alive
                    if proc.poll() is None:
                        try:
                            proc.kill()
                        except Exception:
                            pass

                    # 4) Windows last resort: kill the whole tree (hidden)
                    if os.name == "nt" and proc.poll() is None:
                        try:
                            CREATE_NO_WINDOW = 0x08000000
                            si = subprocess.STARTUPINFO()
                            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                            si.wShowWindow = 0
                            subprocess.run(
                                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                check=False,
                                creationflags=CREATE_NO_WINDOW,
                                startupinfo=si
                            )
                        except Exception:
                            pass

                    return False, "Stopped by user"

                time.sleep(0.3)
        finally:
            pass

    if proc.returncode == 0:
        return True, "ok"

    # include last lines of stderr for diagnosis
    try:
        tail = "\n".join((stderr_path.read_text(encoding="utf-8", errors="ignore").splitlines())[-60:])
        return False, "TotalSegmentator failed:\n" + tail
    except Exception:
        return False, "TotalSegmentator failed (no stderr available)."


# ============================= top-level call ================================

def _run_totalseg(owner, input_nii: Path, out_dir: Path, params: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Returns (ok, message). On success, out_dir will contain per-organ NIfTI masks.
    Runs in a subprocess so it can be stopped mid-run.
    """
    _ensure_vendor_on_path()  # harmless if not present; worker exe has TS when frozen
    ap = _work_paths()

    env_extra: Dict[str, str] = {}
    if "TOTALSEG_HOME" not in os.environ:
        env_extra["TOTALSEG_HOME"] = str(ap["models"])

    # Tame thread counts on CPU-only systems
    if _device_from_params(params) == "cpu":
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


# ============================ public entry point =============================

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
                _show_warn("TotalSegmentator", f"Failed to export NIfTI for {tag}",
                           parent=getattr(owner, "segwin", None) or owner)
                continue

            # Respect cancel right before starting TS
            if getattr(getattr(owner, "segwin", owner), "_seg_cancel", False):
                break

            # 2) run TS (subprocess, killable)
            ok, msg = _run_totalseg(owner, input_nii, out_dir, params or {})
            if not ok:
                _show_warn("TotalSegmentator failed", msg,
                           parent=getattr(owner, "segwin", None) or owner)
                continue

            # 3) import output masks
            n = _import_masks_into_series(owner, out_dir, pid, sid, mod, idx)
            print(f"[TS] Imported {n} structures for {tag} from {out_dir}")

        except Exception as ex:
            tb = traceback.format_exc()
            _show_warn("TotalSegmentator error", f"{ex}", tb,
                       parent=getattr(owner, "segwin", None) or owner)

    # Optional: refresh your DICOM tree
    try:
        from fcn_load.populate_med_image_list import populate_medical_image_tree
        populate_medical_image_tree(owner)
    except Exception:
        pass
