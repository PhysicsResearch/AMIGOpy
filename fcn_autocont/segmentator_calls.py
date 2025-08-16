# in your main window module
import os, sys, time, requests, io, tempfile, zipfile, pathlib
from PyQt5.QtCore import QProcess, QTimer, Qt, QProcessEnvironment
from PyQt5.QtWidgets import QMessageBox, QProgressDialog, QApplication
from fcn_autocont.segmentator_ui import SegmentatorWindow
import numpy as np
import nibabel as nib
from nibabel.processing import resample_from_to
import sip


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
        r = requests.get(f"http://{host}:{port}/ping", timeout=timeout_s)
        return r.ok
    except requests.RequestException:
        return False

def on_start_api_requested(owner, host: str, port: int):
    """Start the API as a background QProcess with working dir in AppData."""
    # Already running?
    if _api_is_up(host, port):
        if getattr(owner, "segwin", None): owner.segwin.set_api_running(True)
        QMessageBox.information(owner, "Segmentator", f"API already running at {host}:{port}")
        return

    app_root   = _get_appdata_root()                              # C:\Users\...\AppData\Local\AMIGOpy
    plugin_dir = os.path.join(app_root, "Segmentator")            # working dir
    models_dir = os.path.join(app_root, "Models")
    tmp_dir    = os.path.join(app_root, "tmp")
    os.makedirs(plugin_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=True)
    log_path = os.path.join(app_root, "segmentator_api.log")

    # Prepare process & env
    proc = QProcess(owner)
    env = QProcessEnvironment.systemEnvironment()
    env.insert("TOTALSEG_HOME", models_dir)   # TotalSegmentator model cache
    env.insert("TMPDIR", tmp_dir); env.insert("TEMP", tmp_dir); env.insert("TMP", tmp_dir)
    proc.setProcessEnvironment(env)

    exe_path = os.path.join(plugin_dir, "segmentator_api.exe")
    if os.path.exists(exe_path):
        # Compiled plugin present
        proc.setProgram(exe_path)
        proc.setArguments([f"--host={host}", f"--port={port}"])
        proc.setWorkingDirectory(plugin_dir)
    else:
        # Dev fallback: run uvicorn against your source tree in repo
        # Adjust this path if segmentator_api.py lives elsewhere in your repo
        repo_plugin_dir = os.path.join(os.path.dirname(__file__), "segmentator_api")
        proc.setWorkingDirectory(repo_plugin_dir)
        proc.setProgram(sys.executable)
        proc.setArguments([
            "-m", "uvicorn",
            "segmentator_api:app",
            "--host", host,
            "--port", str(port),
            "--log-level", "warning"
        ])

    # Log stdout/stderr to AppData
    proc.setStandardOutputFile(log_path)
    proc.setStandardErrorFile(log_path)

    # Keep handles on owner so GC won't kill them
    owner.segmentator_proc = proc
    owner._api_timer = QTimer(owner)
    owner._api_timer.setInterval(250)
    owner._api_checks = 0

    # When the process exits unexpectedly, reflect in UI
    def _on_finished(*_):
        if getattr(owner, "segwin", None):
            owner.segwin.set_api_running(False)

    proc.finished.connect(_on_finished)

    # Start non-blocking
    proc.start()

    # Poll readiness without blocking UI
    def _poll():
        owner._api_checks += 1
        if _api_is_up(host, port):
            owner._api_timer.stop()
            if getattr(owner, "segwin", None):
                owner.segwin.set_api_running(True)
                QMessageBox.information(owner, "Segmentator", f"API is running at {host}:{port}")
        elif owner._api_checks >= 60:  # ~15s
            owner._api_timer.stop()
            if getattr(owner, "segwin", None):
                owner.segwin.set_api_running(False)
            QMessageBox.warning(
                owner, "Segmentator",
                "API failed to start (timeout). Check firewall and log:\n" + log_path
            )
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

    stopped = False
    try:
        proc = getattr(owner, "segmentator_proc", None)
        if proc and proc.state() != QProcess.NotRunning:
            proc.terminate()
            proc.waitForFinished(2000)
            if proc.state() != QProcess.NotRunning:
                proc.kill()
            stopped = True
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
    q["task"] = params.get("task", "total")  # keep 'total' (you said ignore 'body' for now)

    if params.get("fast"):     q["fast"] = "true"
    if params.get("no_crop"):  q["nr_crop"] = "true"
    if params.get("resample"): q["resample"] = str(params["resample"])
    q["output_type"] = _map_output_type(params.get("output_type"))

    # >>> IMPORTANT: include selected targets (comma-separated) if present
    targets = params.get("targets") or []
    if isinstance(targets, (list, tuple)) and len(targets) > 0:
        # UI already provides canonical TS names; server will translate to --roi_subset
        q["targets"] = ",".join(targets)

    return q

def _params_to_query_singlefile(params: dict) -> dict:
    q = {
        "ml": "true",                 # <- single merged labelmap (one file)
        "task": params.get("task", "total"),  # keep total task
    }
    if params.get("fast"):     q["fast"] = "true"
    if params.get("no_crop"):  q["nr_crop"] = "true"
    if params.get("resample"): q["resample"] = str(params["resample"])
    q["output_type"] = _map_output_type(params.get("output_type"))
    # IMPORTANT: do NOT set q["targets"] -> no subset; TS outputs all classes in one file
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
    # query = _params_to_query_singlefile(params)

    for meta in series_list:
        pid = meta["patient"]
        study = meta["study"]
        mod = meta["modality"]
        idx = meta["index"]

        # Export NIfTI directly into BASE_DIR instead of a temp folder
        nifti_path = export_nifti(owner,
            pid, study, mod, idx,
            output_folder=BASE_DIR,
            file_name="input.nii.gz"
        )

        if nifti_path:
            # Send it to the API
            zip_path, err = _post_to_api(nifti_path, host, port, query)
            if err:
                _show_api_error(owner, f"API error for {pid}/{study}/{mod}[{idx}]", err)


def _post_to_api(nifti_path: str, host: str, port: int, query: dict, out_dir: str = BASE_DIR):
    """
    POST the NIfTI to the TS API and save the binary ZIP response to out_dir.
    Returns (zip_path, None) on success, or (None, err_dict) on failure.
    """
    url = f"http://{host}:{port}/segment/"
    with open(nifti_path, "rb") as f:
        files = {"file": (os.path.basename(nifti_path), f, "application/octet-stream")}
        r = requests.post(url, params=query, files=files, timeout=None)

    ct = (r.headers.get("content-type") or "").lower()
    if not r.ok or ("application/json" in ct):
        # Try to return structured error from API
        try:
            return None, r.json()
        except Exception:
            return None, {"error": f"HTTP {r.status_code}", "cmd": f"POST {url}"}

    # Save the response body as a ZIP in the working folder
    os.makedirs(out_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    zip_path = os.path.join(out_dir, f"ts_output_{ts}.zip")
    with open(zip_path, "wb") as zf:
        zf.write(r.content)
    return zip_path, None

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