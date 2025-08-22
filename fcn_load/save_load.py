# ──────────────────────────────────────────────────────────────
# Imports  (put these near the top of your file)
# ──────────────────────────────────────────────────────────────
from PyQt5.QtCore    import QObject, QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import (QFileDialog, QProgressDialog,
                             QMessageBox, QApplication)
import joblib, pickle, importlib.util
from pathlib import Path
from fcn_load.load_dcm import populate_DICOM_tree
import copy
import numpy as np


# ─────────────────────────────────────────────────────────────
# UNIVERSAL VTK-actor stripper
# ─────────────────────────────────────────────────────────────
def strip_vtk_actors_from_dicom_tree(node):
    """
    Recursively delete any dict entry whose key is 'VTKActors2D'
    from *any* depth inside *node* (dict / list / tuple / set).

    Parameters
    ----------
    node : any
        Typically the deep-copied medical_image tree.

    Returns
    -------
    None   (node is modified in place)
    """
    if isinstance(node, dict):
        if "VTKActors2D" in node:
            del node["VTKActors2D"]          # ← nuke the entire actor cache
        for v in list(node.values()):
            strip_vtk_actors_from_dicom_tree(v)

    elif isinstance(node, (list, tuple, set)):
        for item in node:
            strip_vtk_actors_from_dicom_tree(item)

def _is_picklable(x) -> bool:
    try:
        pickle.dumps(x, protocol=pickle.HIGHEST_PROTOCOL)
        return True
    except Exception:
        return False

def make_pickle_safe(node):
    """
    Return a *new* object tree that is identical to *node* except that

      • every dict entry with key 'VTKActors2D' is removed
      • every leaf that cannot be pickled is skipped

    The original tree is left untouched; NumPy arrays are shared
    (shallow-copy) so memory overhead is small.
    """
    if isinstance(node, dict):
        new = {}
        for k, v in node.items():
            if k == "VTKActors2D":
                continue                    # nuke the whole cache
            cleaned = make_pickle_safe(v)
            if cleaned is not None:
                new[k] = cleaned
        return new

    elif isinstance(node, list):
        return [c for v in node
                  if (c := make_pickle_safe(v)) is not None]

    elif isinstance(node, tuple):
        return tuple(c for v in node
                       if (c := make_pickle_safe(v)) is not None)

    elif isinstance(node, set):
        return {c for v in node
                  if (c := make_pickle_safe(v)) is not None}

    else:
        return node if _is_picklable(node) else None



# ──────────────────────────────────────────────────────────────
# Helper: pick fastest available compressor
# ──────────────────────────────────────────────────────────────
def _pick_compressor():
    if importlib.util.find_spec("lz4"):
        return ("lz4", 3)
    return ("lzma", 3)                   # always works


# ──────────────────────────────────────────────────────────────
# Worker classes run inside a QThread
# ──────────────────────────────────────────────────────────────
class SaveWorker(QObject):
    finished = pyqtSignal()
    error    = pyqtSignal(str)

    def __init__(self, data, path):
        super().__init__()
        self._data, self._path = data, path

    def run(self):
        try:
            # ➊ build a pickle-safe clone (no vtkActors anywhere)
            clean_data = make_pickle_safe(self._data)

            # ➋ (optional) assertion during development
            find_unpicklable(clean_data)

            # ➌ dump
            joblib.dump(
                clean_data,
                self._path,
                compress=_pick_compressor(),
                protocol=pickle.HIGHEST_PROTOCOL,
            )

        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

def _shim_pydicom_pickle():
    """
    Provide a stub for pydicom.sequence.validate_dataset if missing,
    so old pickles can unpickle under pydicom ≥3.0.
    """
    try:
        import pydicom.sequence as seq
        if not hasattr(seq, "validate_dataset"):
            def validate_dataset(x):  # no-op stub
                return x
            seq.validate_dataset = validate_dataset
    except Exception:
        # If pydicom isn't installed in this env, just skip.
        pass

class LoadWorker(QObject):
    result   = pyqtSignal(object)    # loaded medical_image
    finished = pyqtSignal()
    error    = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()
        self._path = path

    def run(self):
        try:
            _shim_pydicom_pickle()
            data = joblib.load(self._path, mmap_mode=None)
            self.result.emit(data)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


# ──────────────────────────────────────────────────────────────
# Main-window slots
# ──────────────────────────────────────────────────────────────
BUNDLE_FILTER = "AMIGOpy data (*.amigo)" 

def save_amigo_bundle(self):
    """
    Save self.medical_image in a background thread while showing
    an indeterminate (animated) progress bar.
    """
    path, _ = QFileDialog.getSaveFileName(
        self, "Save AMIGOpy data",
        str(Path.home() / "dataset.amigo"),
        BUNDLE_FILTER,
    )
    if not path:
        return       # user cancelled

    # 1) Progress dialog  (range 0–0 => barber-pole animation)
    dlg = QProgressDialog("Saving dataset … can take a minute or two ...", None, 0, 0, self)
    dlg.setWindowModality(Qt.ApplicationModal)
    dlg.setWindowTitle("Please wait")
    dlg.setMinimumDuration(0)        # show immediately
    dlg.setValue(0)
    # used for debugging
    if self.DataType == "DICOM":
        find_unpicklable(self.medical_image)
    elif self.DataType == "nifti":
        find_unpicklable(self.nifti_data)
    else:
        return
    #
    # 2) Thread + worker
    thread = QThread(self)
    if self.DataType == "DICOM":
        worker = SaveWorker(self.medical_image, path)
    elif self.DataType == "nifti":
        worker = SaveWorker(self.nifti_data, path)
    else:
        return

    worker.moveToThread(thread)

    # 3) Wiring
    worker.error.connect(lambda msg: QMessageBox.critical(self, "Save error", msg))
    worker.finished.connect(dlg.close)
    worker.finished.connect(thread.quit)
    worker.finished.connect(thread.deleteLater)
    thread.started.connect(worker.run)

    # keep refs so they’re not GC’d mid-way
    self._saveThread  = thread
    self._saveWorker  = worker
    self._saveDialog  = dlg

    thread.start()                   # hands off, thread owns worker


def load_amigo_bundle(self, path: str | None = None):
    """
    Load an *.amigo* bundle.

    • If *path* is given (e.g. from drag-and-drop), load it directly.
    • Otherwise show QFileDialog so the user can choose a file.
    • Runs in a background QThread with an indeterminate progress bar.
    """

    # ─── 1)  Figure out which file to open ──────────────────────────
    if path is None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open AMIGOpy data",
            str(Path.home()),
            BUNDLE_FILTER,
        )
        if not path:                              # user pressed Cancel
            return

    # ─── 2)  Progress dialog (indeterminate) ────────────────────────
    dlg = QProgressDialog("Loading dataset … this may take a minute",
                          None, 0, 0, self)
    dlg.setWindowModality(Qt.ApplicationModal)
    dlg.setWindowTitle("Please wait")
    dlg.setMinimumDuration(0)
    dlg.setValue(0)

    # ─── 3)  Worker thread ------------------------------------------------
    thread = QThread(self)
    worker = LoadWorker(path)
    worker.moveToThread(thread)

    def _apply_loaded_data(data):
        try:
            self.DataType = data[0]['metadata']['DataType']
        except:
            self.DataType = "DICOM"

        if self.DataType == "DICOM" or self.DataType == "nifti":
            self.medical_image = data
            self.DataType = "DICOM"
            populate_DICOM_tree(self)        # refresh your UI
        else:
            return


    # wiring
    worker.result.connect(_apply_loaded_data)
    worker.error.connect(lambda msg: QMessageBox.critical(self, "Load error", msg))
    worker.finished.connect(dlg.close)
    worker.finished.connect(thread.quit)
    worker.finished.connect(thread.deleteLater)
    thread.started.connect(worker.run)

    # keep references so GC can’t kill them mid-load
    self._loadThread  = thread
    self._loadWorker  = worker
    self._loadDialog  = dlg

    thread.start()


def _safe_repr(x, max_len=40):
    r = repr(x)
    return r if len(r) <= max_len else r[:max_len] + "…"

def find_unpicklable(obj, *, skip_numpy=True, _path="root"):
    """
    Recursively traverse *obj*; report the first item that cannot be pickled.

    Parameters
    ----------
    obj : any
        The object tree to inspect (e.g. self.medical_image).
    skip_numpy : bool, default True
        Large NumPy arrays are almost always pickle-safe and expensive to
        test; skip them unless you really suspect trouble there.

    Returns
    -------
    None
        Prints a message when a non-picklable item is found, otherwise prints
        "All objects pickled OK".
    """
    # 1) fast path: try pickling the whole thing first
    try:
        pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
        print("✅ All objects pickled OK")
        return
    except Exception as top_err:
        # fall through to detailed search
        pass

    stack = [(obj, _path)]

    while stack:
        current, path = stack.pop()

        # optionally skip big arrays
        if skip_numpy and isinstance(current, np.ndarray):
            continue

        # try pickling current leaf
        try:
            pickle.dumps(current, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as err:
            # if current is a container, drill deeper
            if isinstance(current, dict):
                for k, v in current.items():
                    stack.append((v, f"{path}[{repr(k)}]"))
            elif isinstance(current, (list, tuple, set)):
                for idx, v in enumerate(current):
                    stack.append((v, f"{path}[{idx}]"))
            else:
                print("❌ Cannot pickle object at:", path)
                print("   type :", type(current))
                print("   repr :", _safe_repr(current))
                print("   error:", err)
                return
    print("⚠️  Pickling failed for a container, but no unpicklable leaf found.")


