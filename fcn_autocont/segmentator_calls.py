# in your main window module
import os, sys, time, requests, io, tempfile, zipfile, pathlib
from PyQt5.QtCore import QProcess, QTimer, Qt, QProcessEnvironment
from PyQt5.QtWidgets import QMessageBox, QProgressDialog, QApplication, QDialog, QVBoxLayout, QLabel, QProgressBar
from fcn_autocont.segmentator_ui import SegmentatorWindow
from fcn_load.populate_dcm_list import populate_DICOM_tree
import numpy as np
import SimpleITK as sitk
from pathlib import Path
from typing import Dict, List, Any
import sip
import winreg  # <-- registry lookup
from fcn_autocont.segmentator_ui import TS_ALL_SET  # canonical case-sensitive set


def open_segmentator_tab(self):
    # If an old reference exists but the C++ object is gone, wipe it
    if getattr(self, "segwin", None) is not None:
        try:
            # check if still alive
            if not sip.isdeleted(self.segwin) and self.segwin.isVisible():
                self.segwin.raise_()
                self.segwin.activateWindow()
                return
        except RuntimeError:
            # wrapped C/C++ object has been deleted
            self.segwin = None

    # Create a NEW window
    excluded = {'RTPLAN','RTSTRUCT','RTDOSE'}
    self.segwin = SegmentatorWindow(
        parent=None,
        dicom_data=self.dicom_data,                    # initial fill
        excluded_modalities=excluded,
        data_provider=lambda: self.dicom_data          # <- used by Refresh Series
    )
    self.segwin.setAttribute(Qt.WA_DeleteOnClose, True)

    # When the window is destroyed, clear the Python reference
    self.segwin.destroyed.connect(lambda *_: setattr(self, "segwin", None))

    # Wire signals (free-function style)
    self.segwin.startApiRequested.connect(
        lambda host, port, owner=self: on_start_api_requested(owner, host, port)
    )
    self.segwin.stopApiRequested.connect(
        lambda owner=self: on_stop_api_requested(owner)
    )
    self.segwin.runSegRequested.connect(
        lambda series_list, params, owner=self:
            on_run_segmentation_requested(owner, series_list, params)
    )

    self.segwin.show()
    self.segwin.raise_()
    self.segwin.activateWindow()


def _get_appdata_root():
    base = os.getenv("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
    root = os.path.join(base, "AMIGOpy")
    os.makedirs(root, exist_ok=True)
    return root

def _api_is_up(host, port, timeout_s=0.5):
    try:
        # First try /ping
        r = requests.get(f"http://{host}:{port}/ping", timeout=timeout_s)
        if r.ok:
            return True
    except requests.RequestException:
        pass

    try:
        # Fallback to /health (used by some builds)
        r = requests.get(f"http://{host}:{port}/health", timeout=timeout_s)
        if r.ok:
            return True
    except requests.RequestException:
        pass

    return False


def _ensure_dir(p: Path) -> bool:
    try:
        p.mkdir(parents=True, exist_ok=True)
        # writeability probe (works even on redirected folders)
        test = p / ".amigo_write_test"
        test.write_text("ok", encoding="utf-8")
        test.unlink(missing_ok=True)
        return True
    except Exception:
        return False

def _get_paths_for_segmentator() -> dict:
    """
    Compute per-user log/tmp dirs and a writable models dir with smart fallbacks.
    Returns: dict with keys: app_root, log_path, tmp_dir, models_dir
    """
    # Per-user base (no admin needed)
    app_root = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "AMIGOpy"
    _ensure_dir(app_root)

    # Logs & temp are always per-user
    log_path = app_root / "segmentator_api.log"
    tmp_dir  = app_root / "tmp"
    _ensure_dir(tmp_dir)

    # 1) If TOTALSEG_HOME is set and writable, respect it
    env_home = os.getenv("TOTALSEG_HOME")
    if env_home:
        models_dir = Path(env_home)
        if _ensure_dir(models_dir):
            return {
                "app_root": app_root, "log_path": log_path,
                "tmp_dir": tmp_dir, "models_dir": models_dir
            }

    # 2) Prefer machine-wide ProgramData (nice for shared caches)
    progdata = Path(os.getenv("PROGRAMDATA", r"C:\ProgramData"))
    pd_models = progdata / "AMIGOpy" / "Models" / "TotalSegmentator"
    if _ensure_dir(pd_models):
        return {
            "app_root": app_root, "log_path": log_path,
            "tmp_dir": tmp_dir, "models_dir": pd_models
        }

    # 3) Fallback to per-user models (works in dev / no admin)
    user_models = app_root / "Models" / "TotalSegmentator"
    _ensure_dir(user_models)
    return {
        "app_root": app_root, "log_path": log_path,
        "tmp_dir": tmp_dir, "models_dir": user_models
    }


def _get_segmentator_from_registry() -> str:
    """
    Look in HKLM\SOFTWARE\AMIGOpy\Segmentator for InstalledPath (set by installer).
    Returns full path to segmentator_api.exe if present and valid, else "".
    """
    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\AMIGOpy\Segmentator"
        ) as key:
            val, _ = winreg.QueryValueEx(key, "InstalledPath")
            if val and os.path.exists(val):
                return os.path.normpath(val)
    except FileNotFoundError:
        return ""
    except OSError:
        return ""
    return ""


def on_start_api_requested(owner, host: str, port: int):
    # Block re-entry / double-clicks
    if getattr(owner, "_api_starting", False):
        return

    # If already up, reflect UI and lock buttons
    if _api_is_up(host, port):
        if getattr(owner, "segwin", None):
            owner.segwin.set_api_running(True)
            try:
                owner.segwin.btn_start_api.setEnabled(False)
                owner.segwin.btn_stop_api.setEnabled(True)
            except Exception:
                pass
        print(f"[Segmentator] API already running at {host}:{port}")
        return

    owner._api_starting = True
    if getattr(owner, "segwin", None):
        try:
            owner.segwin.btn_start_api.setEnabled(False)
            owner.segwin.btn_stop_api.setEnabled(False)
        except Exception:
            pass

    # Non-blocking "Starting..." dialog
    start_dlg = QDialog(getattr(owner, "segwin", owner))
    start_dlg.setWindowTitle("Segmentator")
    start_dlg.setModal(False)
    lay = QVBoxLayout(start_dlg)
    lbl = QLabel(f"Starting API at {host}:{port}…", start_dlg)
    pgb = QProgressBar(start_dlg); pgb.setRange(0, 0)
    lay.addWidget(lbl); lay.addWidget(pgb)
    start_dlg.show()
    owner._seg_start_dlg = start_dlg

    paths = _get_paths_for_segmentator()
    app_root  = str(paths["app_root"])
    log_path  = str(paths["log_path"])
    tmp_dir   = str(paths["tmp_dir"])
    models_dir= str(paths["models_dir"])
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=True)

    # Prepare QProcess
    proc = QProcess(owner)
    env = QProcessEnvironment.systemEnvironment()
    env.insert("AMIGO_SEG_HOST", host)
    env.insert("AMIGO_SEG_PORT", str(port))

    # Only set TOTALSEG_HOME if caller/OS hasn't already set it
    if not env.contains("TOTALSEG_HOME"):
        env.insert("TOTALSEG_HOME", models_dir)

    env.insert("TMPDIR", tmp_dir); env.insert("TEMP", tmp_dir); env.insert("TMP", tmp_dir)
    proc.setProcessEnvironment(env)
    proc.setStandardOutputFile(log_path)
    proc.setStandardErrorFile(log_path)

    # -------- Prefer compiled API (search multiple locations) --------
    candidate_paths = []
    _norm = lambda p: os.path.normpath(p)

    # 0) If installer registered the API path (env var), prefer it
    env_api = os.getenv("AMIGO_API_EXE")
    if env_api:
        env_api = _norm(env_api.strip().strip('"'))
        if os.path.exists(env_api):
            candidate_paths.append(env_api)

    # 0b) If installer wrote registry key, prefer that next
    reg_api = _get_segmentator_from_registry()
    if reg_api:
        candidate_paths.append(reg_api)

    # 1) Next to AMIGOpy.exe (typical for the small installer)
    try:
        appdir = os.path.dirname(os.path.abspath(sys.argv[0]))
        candidate_paths.append(_norm(os.path.join(appdir, "segmentator", "segmentator_api.exe")))
        candidate_paths.append(_norm(os.path.join(appdir, "segmentator_api.exe")))
    except Exception:
        pass

    # 1b) Common Program Files location (if the small installer put it there)
    for pf in (os.environ.get("ProgramFiles"), os.environ.get("ProgramW6432")):
        if pf:
            candidate_paths.append(_norm(os.path.join(pf, "AMIGOpy", "segmentator", "segmentator_api.exe")))
            candidate_paths.append(_norm(os.path.join(pf, "AMIGOpy", "segmentator_api.exe")))

    # 2) Previous per-user location (still check it)
    app_root_legacy = _get_appdata_root()
    candidate_paths.append(_norm(os.path.join(app_root_legacy, "Segmentator", "segmentator_api.exe")))

    # 3) Fallback: developer layout (python script)
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir   = _norm(os.path.join(base_dir, os.pardir))      # repo root
    api_dir    = _norm(os.path.join(root_dir, "segmentator_api"))
    fallback_py = _norm(os.path.join(api_dir, "segmentator_api.py"))

    exe_path = next((p for p in candidate_paths if os.path.exists(p)), None)
    if exe_path:
        proc.setProgram(exe_path)
        proc.setArguments([])  # host/port via env
        proc.setWorkingDirectory(os.path.dirname(exe_path))
    else:
        if not os.path.exists(fallback_py):
            try: start_dlg.close()
            except Exception: pass
            owner._api_starting = False
            if getattr(owner, "segwin", None):
                try: owner.segwin.btn_start_api.setEnabled(True)
                except Exception: pass
            QMessageBox.critical(
                owner, "Segmentator",
                "Segmentator API not found.\n\n"
                "Install the AMIGOpy Segmentator add-on or provide a dev copy at:\n" + fallback_py
            )
            return
        proc.setWorkingDirectory(api_dir)
        proc.setProgram(sys.executable)
        proc.setArguments([fallback_py])  # run "python segmentator_api.py"
    # ------------------------------------------------------------

    # Keep a handle so it isn't GC'd
    owner.segmentator_proc = proc

    def _on_finished(*_):
        owner._api_starting = False
        try:
            if hasattr(owner, "_seg_start_dlg") and owner._seg_start_dlg:
                owner._seg_start_dlg.close()
        except Exception:
            pass
        if getattr(owner, "segwin", None):
            owner.segwin.set_api_running(False)
            try:
                owner.segwin.btn_start_api.setEnabled(True)
                owner.segwin.btn_stop_api.setEnabled(False)
            except Exception:
                pass
        print("[Segmentator] API process finished.")
    proc.finished.connect(_on_finished)

    proc.start()

    # Poll /ping for readiness
    owner._api_timer = QTimer(owner)
    owner._api_timer.setInterval(250)
    owner._api_checks = 0

    def _poll():
        owner._api_checks += 1
        if _api_is_up(host, port):
            owner._api_timer.stop()
            owner._api_starting = False
            try:
                if hasattr(owner, "_seg_start_dlg") and owner._seg_start_dlg:
                    owner._seg_start_dlg.close()
            except Exception:
                pass
        # set UI
            if getattr(owner, "segwin", None):
                owner.segwin.set_api_running(True)
                try:
                    owner.segwin.btn_start_api.setEnabled(False)
                    owner.segwin.btn_stop_api.setEnabled(True)
                except Exception:
                    pass
            print(f"[Segmentator] API is running at {host}:{port}")
            return

        if owner._api_checks >= 480:  # ~2 minutes at 250 ms interval
            owner._api_timer.stop()    # ensure timer stops on timeout
            owner._api_starting = False
            try:
                if hasattr(owner, "_seg_start_dlg") and owner._seg_start_dlg:
                    owner._seg_start_dlg.close()
            except Exception:
                pass
            if getattr(owner, "segwin", None):
                owner.segwin.set_api_running(False)
                try:
                    owner.segwin.btn_start_api.setEnabled(True)
                    owner.segwin.btn_stop_api.setEnabled(False)
                except Exception:
                    pass
            print("[Segmentator] API failed to start (timeout). See log:", log_path)
            QMessageBox.warning(owner, "Segmentator",
                                "API failed to start (timeout).\nCheck log:\n" + log_path)

    owner._api_timer.timeout.connect(_poll)
    owner._api_timer.start()


def on_stop_api_requested(owner):
    """Terminate the API process if running and update UI."""
    # Stop timer if present
    try:
        if getattr(owner, "_api_timer", None):
            owner._api_timer.stop()
    except Exception:
        pass

    try:
        proc = getattr(owner, "segmentator_proc", None)
        if proc and proc.state() != QProcess.NotRunning:
            proc.terminate()
            proc.waitForFinished(2000)
            if proc.state() != QProcess.NotRunning:
                proc.kill()
    except Exception:
        pass

    if getattr(owner, "segwin", None):
        owner.segwin.set_api_running(False)


from fcn_export.export_nii import export_nifti

def _params_to_query_no_ml(params: dict) -> dict:
    """
    Build query for per-organ output (no merge). If the UI provided 'targets',
    pass them along so the server can map to --roi_subset (speed-up).
    """
    q = {"ml": "false"}  # per-organ files
    q["task"] = params.get("task", "total")  # keep 'total'

    if params.get("fast"):     q["fast"] = "true"
    if params.get("no_crop"):  q["nr_crop"] = "true"
    if params.get("resample"): q["resample"] = str(params["resample"])
    q["output_type"] = _map_output_type(params.get("output_type"))

    # include selected targets (comma-separated) if present
    targets = params.get("targets") or []
    if isinstance(targets, (list, tuple)) and len(targets) > 0:
        q["targets"] = ",".join(targets)

    return q

def _params_to_query_singlefile(params: dict) -> dict:
    q = {
        "ml": "true",                 # single merged labelmap (one file)
        "task": params.get("task", "total"),
    }
    if params.get("fast"):     q["fast"] = "true"
    if params.get("no_crop"):  q["nr_crop"] = "true"
    if params.get("resample"): q["resample"] = str(params["resample"])
    q["output_type"] = _map_output_type(params.get("output_type"))
    # no q["targets"] in ML mode
    return q

def _map_output_type(val: str) -> str:
    v = (val or "").strip().lower()
    if v in ("nifti", "nii", "nii.gz", "nifti_gz"):
        return "nifti"
    if v in ("dicom", "dcm", "dicom_seg", "seg"):
        return "dicom"
    return "nifti"  # safe default


# Define your API working folder (same as your API startup)
BASE_DIR = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser("~")), "AMIGOpy")
os.makedirs(BASE_DIR, exist_ok=True)


def _get_or_make_step_dialog(owner) -> QDialog:
    dlg = getattr(owner, "_seg_step_dlg", None)
    if dlg is None or sip.isdeleted(dlg):
        dlg = QDialog(getattr(owner, "segwin", owner))
        dlg.setWindowTitle("Segmentator")
        dlg.setModal(False)

        lay = QVBoxLayout(dlg)
        lbl = QLabel("Starting…", dlg)
        pgb = QProgressBar(dlg)
        pgb.setRange(0, 100)
        pgb.setValue(0)

        lay.addWidget(lbl)
        lay.addWidget(pgb)

        dlg._lbl = lbl           # stash widgets for quick access
        dlg._pgb = pgb

        owner._seg_step_dlg = dlg
    return dlg

def _step_update(dlg: QDialog, text: str, value: int = None):
    try:
        dlg._lbl.setText(text)
        if value is not None:
            dlg._pgb.setValue(max(0, min(100, int(value))))
        dlg.show()
        QApplication.processEvents()
    except Exception:
        pass


def on_run_segmentation_requested(owner, series_list, params):
    host = "127.0.0.1"
    port = 5000
    if getattr(owner, "segwin", None):
        try:
            host = (owner.segwin.addr_edit.text() or host).strip()
            port = int((owner.segwin.port_edit.text() or str(port)).strip())
        except Exception:
            pass

    params = dict(params or {})
    params["merge_labels"] = False
    query = _params_to_query_no_ml(params)
    _warn_on_unknown_targets(query.get("targets", ""))

    dlg = _get_or_make_step_dialog(owner)

    for meta in series_list:
        pid   = meta["patient"]
        study = meta["study"]
        mod   = meta["modality"]
        idx   = meta["index"]

        series_tag = f"{pid}/{study}/{mod}[{idx}]"

        # Step 1: write NIfTI input
        _step_update(dlg, f"Writing input for TS…\n{series_tag}", 10)
        nifti_path = export_nifti(
            owner, pid, study, mod, idx,
            output_folder=BASE_DIR,
            file_name="input.nii.gz"
        )
        if not nifti_path:
            _show_api_error(owner, "Export error",
                            {"error": f"Failed to export NIfTI for {series_tag}"})
            _step_update(dlg, f"Export failed — continuing…\n{series_tag}", 0)
            continue

        # Step 2: call TS
        _step_update(dlg, f"Calling TS…\n{series_tag}", 40)
        info, err = _post_to_api(nifti_path, host, port, query)
        if err:
            _show_api_error(owner, f"API error for {series_tag}", err)
            _step_update(dlg, f"TS call failed — continuing…\n{series_tag}", 0)
            continue

        # Step 3: process outputs
        outdir = info.get("output_dir")
        _step_update(dlg, f"Processing output folder…\n{outdir or '(none)'}", 75)
        count = process_output(
            owner, info,
            patient_id=pid, study_id=study, modality=mod, series_index=idx
        )
        print(f"[Segmentator] Imported {count} structure(s) from {outdir}")
        try:
            populate_DICOM_tree(owner)
        except Exception:
            pass

        # Finish this series
        _step_update(dlg, f"Done: {series_tag}", 100)

    _step_update(dlg, "All series processed.", 100)
    # dlg.close()  # uncomment if you prefer it to close automatically


def _post_to_api(nifti_path: str, host: str, port: int, query: dict):
    """
    POST the NIfTI to the TS API /segment/ endpoint.
    Your API returns JSON: {"req_id": "...", "output_dir": "<folder>"}.
    Returns (info_dict, None) on success, or (None, err_dict) on failure.
    """
    url = f"http://{host}:{port}/segment/"
    with open(nifti_path, "rb") as f:
        files = {"file": (os.path.basename(nifti_path), f, "application/octet-stream")}
        try:
            r = requests.post(url, params=query, files=files, timeout=None)
        except Exception as ex:
            return None, {"error": f"POST failed: {ex}", "cmd": f"POST {url}"}

    # Expect JSON containing req_id + output_dir
    try:
        data = r.json()
    except Exception:
        return None, {"error": f"Unexpected response (HTTP {r.status_code})", "cmd": f"POST {url}"}

    if not r.ok or (isinstance(data, dict) and data.get("error")):
        return None, data if isinstance(data, dict) else {"error": "Unknown error"}

    return data, None

def _show_api_error(owner, title: str, payload: dict):
    try:
        msg = payload.get("error", str(payload))
    except Exception:
        msg = str(payload)

    details = []
    if isinstance(payload, dict):
        if payload.get("cmd"):
            details.append("Command:\n" + payload["cmd"])
        st = payload.get("stderr_tail")
        if isinstance(st, (list, tuple)):
            details.append("stderr (last 20 lines):\n" + "\n".join(st))
        elif isinstance(st, str):
            details.append("stderr (tail):\n" + st)

    parent = getattr(owner, "segwin", None) or owner
    box = QMessageBox(QMessageBox.Warning, title, msg, parent=parent)
    if details:
        box.setDetailedText("\n\n".join(details))
    box.exec_()


def _ensure_series_struct_containers(
    owner,
    patient_id: str = None,
    study_id: str = None,
    modality: str = None,
    series_index: int = None,
) -> Dict[str, Any]:
    """
    Ensure the AMIGOpy structure containers exist for the given series and return that series dict.
    Tries explicit ids first; if None, falls back to owner.patientID / owner.studyID / owner.modality / owner.series_index.
    """
    pid  = patient_id  if patient_id  is not None else getattr(owner, "patientID", None)
    sid  = study_id    if study_id    is not None else getattr(owner, "studyID", None)
    mod  = modality    if modality    is not None else getattr(owner, "modality", None)
    sidx = series_index if series_index is not None else getattr(owner, "series_index", None)

    if pid is None or sid is None or mod is None or sidx is None:
        raise RuntimeError("Current series identifiers (patientID, studyID, modality, series_index) are not set on owner or were not provided.")

    dicom = getattr(owner, "dicom_data", None)
    if dicom is None:
        dicom = {}
        setattr(owner, "dicom_data", dicom)

    dicom.setdefault(pid, {})
    dicom[pid].setdefault(sid, {})
    dicom[pid][sid].setdefault(mod, [])

    while len(dicom[pid][sid][mod]) <= int(sidx):
        dicom[pid][sid][mod].append({})

    series = dicom[pid][sid][mod][int(sidx)]
    if not isinstance(series, dict):
        series = dicom[pid][sid][mod][int(sidx)] = {}

    series.setdefault("structures", {})
    series.setdefault("structures_keys", [])
    series.setdefault("structures_names", [])

    # Keep lists consistent
    sk = series["structures_keys"]
    sn = series["structures_names"]
    if len(sn) < len(sk):
        sn.extend([""] * (len(sk) - len(sn)))
    elif len(sk) < len(sn):
        del sn[len(sk):]

    return series


def process_output(
    owner,
    info: dict,
    patient_id: str = None,
    study_id: str = None,
    modality: str = None,
    series_index: int = None,
):
    """
    Use info['output_dir'] from the API, open all .nii/.nii.gz masks, convert to uint8,
    flip in Y (axis=1) to match your load pipeline, and store them into AMIGOpy structures
    for the specified (or current) series. Skip masks that are entirely zero.
    """
    output_dir = info.get("output_dir")
    if not output_dir or not os.path.isdir(output_dir):
        print("[Segmentator] No valid output directory.")
        return 0

    if owner is None:
        print("[Segmentator][import] No owner provided; cannot attach structures.")
        return 0

    series = _ensure_series_struct_containers(
        owner,
        patient_id=patient_id,
        study_id=study_id,
        modality=modality,
        series_index=series_index,
    )
    structures = series["structures"]
    keys_list: List[str] = series["structures_keys"]
    names_list: List[str] = series["structures_names"]

    start_idx = len(keys_list)

    # Gather NIfTI files
    all_files = []
    for root, _, files in os.walk(output_dir):
        for fn in files:
            lf = fn.lower()
            if lf.endswith(".nii") or lf.endswith(".nii.gz"):
                all_files.append(os.path.join(root, fn))
    all_files.sort()

    imported = 0
    for fpath in all_files:
        try:
            img = sitk.ReadImage(fpath)
            arr = sitk.GetArrayFromImage(img)  # (z, y, x)
            # Apply same flip as in your reader
            arr = np.flip(arr, axis=1)

            # Fast skip if mask is entirely zero
            if not np.any(arr):
                print(f"[Segmentator][import] Skipped (all zeros): {fpath}")
                continue

            mask = (arr > 0).astype(np.uint8)

            s_idx = start_idx + imported
            s_key = f"Structure_{s_idx:03d}"
            s_name = Path(fpath).stem
            if s_name.endswith(".nii"):
                s_name = s_name[:-4]

            # Append lists and dicts
            keys_list.append(s_key)
            names_list.append(s_name)
            if s_key not in structures:
                structures[s_key] = {}
            structures[s_key]["Mask3D"] = mask
            structures[s_key]["Name"]   = s_name

            imported += 1
            print(f"[Segmentator][import] Added {s_key} = {s_name} from {fpath}")
        except Exception as e:
            print(f"[Segmentator][import] Failed to import {fpath}: {e}")

    try:
        for root, _, _ in os.walk(output_dir, topdown=False):
            if not os.listdir(root):
                os.rmdir(root)
                print(f"[Segmentator][cleanup] Removed empty folder {root}")
    except Exception as e:
        print(f"[Segmentator][cleanup] Folder cleanup failed: {e}")

    return imported

def _warn_on_unknown_targets(targets_csv: str):
    try:
        if not targets_csv:
            return
        bad = [t for t in (x.strip() for x in targets_csv.split(",")) if t and t not in TS_ALL_SET]
        if bad:
            print("[Segmentator][client][warn] Unknown or wrong-case targets:", bad)
    except Exception:
        pass
