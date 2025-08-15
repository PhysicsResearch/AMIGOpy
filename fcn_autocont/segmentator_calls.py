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





# ===================== helpers: series access & NIfTI I/O =====================

def _get_series_dict(owner, patient, study, modality, index):
    return owner.dicom_data[patient][study][modality][index]

def _ensure_yxz(arr3d: np.ndarray):
    """
    Force array to (Y, X, Z) order = (rows, cols, slices).
    This is the only layout we ever use for NIfTI I/O.
    """
    if arr3d.ndim != 3:
        raise ValueError(f"Expected 3D array, got {arr3d.shape}")

    # If it's (Z, Y, X) → (Y, X, Z)
    if arr3d.shape[0] <= min(arr3d.shape[1], arr3d.shape[2]):
        return np.transpose(arr3d, (1, 2, 0))
    # If it's (X, Y, Z) → swap first two axes
    if arr3d.shape[0] > arr3d.shape[1]:
        return np.transpose(arr3d, (1, 0, 2))
    return arr3d

def _dicom_affine_from_md(md: dict):
    ps = md.get("PixelSpacing", [1.0, 1.0])
    dy = float(ps[0]) if len(ps) > 0 else 1.0  # rows
    dx = float(ps[1]) if len(ps) > 1 else 1.0  # cols
    dz = float(md.get("SpacingBetweenSlices", md.get("SliceThickness", 1.0)))

    iop = md.get("ImageOrientationPatient", None)
    ipp = md.get("ImagePositionPatient", [0.0, 0.0, 0.0])

    if iop and len(iop) >= 6:
        xr, yr, zr, xc, yc, zc = map(float, iop[:6])
        row_dir = np.array([xr, yr, zr], dtype=np.float32)
        col_dir = np.array([xc, yc, zc], dtype=np.float32)
        slc_dir = np.cross(row_dir, col_dir)

        aff = np.eye(4, dtype=np.float32)
        aff[:3, 0] = row_dir * dy
        aff[:3, 1] = col_dir * dx
        aff[:3, 2] = slc_dir * dz
        aff[:3, 3] = np.array(ipp[:3], dtype=np.float32)
    else:
        aff = np.diag([dy, dx, dz, 1.0]).astype(np.float32)

    return aff, (dy, dx, dz)


def _write_temp_nifti_from_amigo(arr3d: np.ndarray, md: dict, tmpdir: str) -> str:
    # Force (z,x,y) → (z,y,x) swap
    arr_yxz = np.swapaxes(arr3d, 0, 2)  # swap X and Y in-plane
    aff, (sy, sx, sz) = _dicom_affine_from_md(md)

    img = nib.Nifti1Image(arr_yxz.astype(np.float32, copy=False), aff)
    try:
        img.header.set_zooms((sy, sx, sz))
    except Exception:
        pass
    out_path = os.path.join(tmpdir, "input.nii.gz")
    nib.save(img, out_path)
    return out_path

def _resample_nifti_mask_to_grid(mask_path: str, target_shape, md: dict):
    aff, (sy, sx, sz) = _dicom_affine_from_md(md)  # keep (dy, dx, dz)
    target = (tuple(int(v) for v in target_shape), aff)
    src = nib.load(mask_path)
    res = resample_from_to(src, target, order=0)
    return (res.get_fdata() > 0.5).astype(np.uint8)

def _map_output_type(val: str) -> str:
    v = (val or "").strip().lower()
    if v in ("nifti", "nii", "nii.gz", "nifti_gz"):
        return "nifti"
    if v in ("dicom", "dcm", "dicom_seg", "seg"):
        return "dicom"
    return "nifti"  # safe default

def _params_to_query_no_ml(params: dict) -> dict:
    q = {"ml": "false"}  # we want per-organ files
    if params.get("fast"):     q["fast"] = "true"
    if params.get("no_crop"):  q["nr_crop"] = "true"
    if params.get("resample"): q["resample"] = str(params["resample"])
    q["output_type"] = _map_output_type(params.get("output_type"))
    if params.get("targets"):  q["targets"] = ",".join(params["targets"])
    return q

def _post_to_api(nifti_path: str, host: str, port: int, query: dict):
    url = f"http://{host}:{port}/segment/"
    with open(nifti_path, "rb") as f:
        files = {"file": ("ct.nii.gz", f, "application/octet-stream")}
        r = requests.post(url, params=query, files=files, timeout=None)
    ct = r.headers.get("content-type", "").lower()
    if ("application/json" in ct) or (not r.ok):
        try:    return None, r.json()
        except: return None, {"error": f"HTTP {r.status_code}"}
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    tmp.write(r.content); tmp.close()
    return tmp.name, None

# ===================== helpers: structures bookkeeping =====================

def _ensure_structure_fields(series_dict: dict):
    if "structures" not in series_dict or not isinstance(series_dict["structures"], dict):
        series_dict["structures"] = {}
    if "structures_keys" not in series_dict or not isinstance(series_dict["structures_keys"], list):
        series_dict["structures_keys"] = []
    if "structures_names" not in series_dict or not isinstance(series_dict["structures_names"], list):
        series_dict["structures_names"] = []

def _parse_struct_num(key: str):
    # accepts "Structure_001" -> 1; else returns None
    try:
        if key.startswith("Structure_"):
            return int(key.split("_", 1)[1])
    except Exception:
        pass
    return None

def _next_structure_key(series_dict: dict) -> str:
    _ensure_structure_fields(series_dict)
    nums = []
    for k in series_dict["structures_keys"]:
        n = _parse_struct_num(k)
        if n is not None:
            nums.append(n)
    nxt = (max(nums) + 1) if nums else 1
    return f"Structure_{nxt:03d}"

def _append_structure(owner, patient, study, modality, index, organ_name: str, mask3d: np.ndarray):
    sdict = _get_series_dict(owner, patient, study, modality, index)
    _ensure_structure_fields(sdict)

    mask3d = np.asarray(mask3d, dtype=np.uint8)
    if mask3d.ndim != 3:
        raise ValueError(f"Mask3D must be 3D; got shape {mask3d.shape}")

    key = _next_structure_key(sdict)

    # Create/overwrite the entry and set *name fields* explicitly
    entry = {"Mask3D": mask3d}
    organ_name = str(organ_name)
    entry["Name"] = organ_name              # AMIGOpy readers commonly use this
    entry["name"] = organ_name              # lowercase alias for robustness
    entry["StructureName"] = organ_name     # legacy alias if any code expects it
    sdict["structures"][key] = entry

    # Keep your parallel lists in sync
    sdict["structures_keys"].append(key)
    sdict["structures_names"].append(organ_name)

# ===================== main entry called by the UI =====================

def on_run_segmentation_requested(owner, series_list, params):
    """
    series_list items: {patient, study, modality, index, label}
    params: dict from SegmentatorWindow.build_params(); we force ml=False here.
    """
    # Host/port from the window
    host = "127.0.0.1"
    port = 5000
    if getattr(owner, "segwin", None):
        try:
            host = (owner.segwin.addr_edit.text() or host).strip()
            port = int((owner.segwin.port_edit.text() or str(port)).strip())
        except Exception:
            pass

    # Force per-organ output
    params = dict(params or {})
    params["merge_labels"] = False
    query = _params_to_query_no_ml(params)

    # Progress dialog
    total = len(series_list)
    dlg = QProgressDialog("Preparing…", "Cancel", 0, total, getattr(owner, "segwin", None) or owner)
    dlg.setWindowTitle("Auto-Contouring")
    dlg.setWindowModality(True)
    dlg.setMinimumDuration(0)
    dlg.setValue(0)
    QApplication.processEvents()

    for i, meta in enumerate(series_list, start=1):
        if dlg.wasCanceled():
            break

        pid = meta["patient"]; study = meta["study"]; mod = meta["modality"]; idx = meta["index"]
        dlg.setLabelText(f"Series {i}/{total}: {pid} / {study} / {mod} [{idx}]")
        QApplication.processEvents()

        # ---- 1) Fetch source volume + spacing from your structure ----
        try:
            sdict = _get_series_dict(owner, pid, study, mod, idx)
            vol = sdict["3DMatrix"]  # your exact key (3D numpy array)
            if not isinstance(vol, np.ndarray) or vol.ndim != 3:
                raise ValueError(f"3DMatrix is not a 3D numpy array (got {type(vol)} shape={getattr(vol,'shape',None)})")
            md = sdict["metadata"]
            ps = md["PixelSpacing"]   # [sx, sy]
            sx, sy = float(ps[0]), float(ps[1])
            sz = float(md["SliceThickness"])
            spacing = (sx, sy, sz)
        except Exception as e:
            print(f"[AutoContouring] Cannot read series for {pid}/{study}/{mod}[{idx}]: {e}")
            dlg.setValue(i); QApplication.processEvents()
            continue

        # ---- 2) Write temp NIfTI and call API (expects ZIP) ----
        with tempfile.TemporaryDirectory() as td:
            nii_in = _write_temp_nifti_from_amigo(vol, sdict.get("metadata", {}), td)

            dlg.setLabelText(f"Processing {pid} / {study} / {mod} [{idx}] …")
            QApplication.processEvents()
            zip_path, err = _post_to_api(nii_in, host, port, query)
            if err:
                _show_api_error(owner, f"API error for {pid}/{study}/{mod}[{idx}]", err)
                dlg.setValue(i); QApplication.processEvents()
                continue

            # ---- 3) Read results: ZIP with one NIfTI per organ ----
            if not zipfile.is_zipfile(zip_path):
                # Likely an error JSON or unexpected file; try to show details
                try:
                    with open(zip_path, "rb") as f:
                        payload = f.read()
                    try:
                        j = json.loads(payload.decode("utf-8", "ignore"))
                        _show_api_error(owner, "Segmentator error", j)
                    except Exception:
                        _show_api_error(owner, "Unexpected response", {"error": f"Not a zip file: {zip_path}"})
                except Exception:
                    _show_api_error(owner, "Unexpected response", {"error": "No valid ZIP returned"})
                dlg.setValue(i); QApplication.processEvents()
                continue

            try:
                extract_dir = os.path.join(td, "seg_out")
                os.makedirs(extract_dir, exist_ok=True)
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(extract_dir)

                # Collect all NIfTI masks
                organ_files = []
                for root, _, files in os.walk(extract_dir):
                    for fname in files:
                        low = fname.lower()
                        if low.endswith(".nii") or low.endswith(".nii.gz"):
                            organ_files.append(os.path.join(root, fname))
                organ_files.sort()

                for fpath in organ_files:
                    organ = pathlib.Path(fpath).name
                    if organ.endswith(".nii.gz"): organ = organ[:-7]
                    elif organ.endswith(".nii"):  organ = organ[:-4]

                    dlg.setLabelText(f"Importing {organ} for {pid} / {study} / {mod} [{idx}] …")
                    QApplication.processEvents()

                    nii = nib.load(fpath)
                    mask = (nii.get_fdata() > 0).astype(np.uint8)

                    # Resample every mask onto the original grid to guarantee identical size
                    mask = _resample_nifti_mask_to_grid(
                        mask_path=fpath,
                        target_shape= _ensure_yxz(vol).shape,          # grid used for the input
                        md=sdict.get("metadata", {})
                    )
                    # ---- 4) Append to your dicom_data structure ----
                    _append_structure(owner, pid, study, mod, idx, organ, mask)

            except Exception as e:
                print(f"[AutoContouring] Failed to import results for {pid}/{study}/{mod}[{idx}]: {e}")

        dlg.setValue(i)
        QApplication.processEvents()

    dlg.close()
    # Optional completion toast
    try:
        QMessageBox.information(getattr(owner, "segwin", None) or owner,
                                "Auto-Contouring",
                                "Segmentation finished.")
    except Exception:
        pass


# ===================== small UI helper =====================

def _show_api_error(owner, title: str, payload: dict):
    # Short message
    try:
        msg = payload.get("error", str(payload))
    except Exception:
        msg = str(payload)

    # Rich details (cmd + stderr tail)
    details = []
    if isinstance(payload, dict):
        if payload.get("cmd"):
            details.append("Command:\n" + payload["cmd"])
        st = payload.get("stderr_tail")
        if isinstance(st, (list, tuple)):
            details.append("stderr (last 20 lines):\n" + "\n".join(st))
        elif isinstance(st, str):
            details.append("stderr (tail):\n" + st)

    # Qt dialog with a collapsible “Show Details”
    parent = getattr(owner, "segwin", None) or owner
    box = QMessageBox(QMessageBox.Warning, title, msg, parent=parent)
    if details:
        box.setDetailedText("\n\n".join(details))
    box.exec_()