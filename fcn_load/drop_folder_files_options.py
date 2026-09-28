import os
from PySide6.QtWidgets import QWidget, QTreeView, QAbstractItemView, QHeaderView
from PySide6.QtCore import Qt
from fcn_load.load_dcm  import load_all_dcm
from fcn_display.dicom_info import open_dicom_tag_viewer
from fcn_load.save_load import load_amigo_bundle
from fcn_load.load_STL import load_stl_files
from fcn_load.load_OBJ import load_obj_files
from fcn_load.load_nifti import load_nifti_files


class FolderDropArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setAcceptDrops(True)

        # Bind shared event handlers
        self.dragEnterEvent = lambda event: generic_drag_enter_event(self, event)
        self.dragMoveEvent  = lambda event: generic_drag_move_event(self, event)
        self.dropEvent      = lambda event: generic_drop_event(self, event)

class FolderDropTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)

        # Allow horizontal scrollbar and auto-resize column to fit text content
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Bind shared event handlers
        self.dragEnterEvent = lambda event: generic_drag_enter_event(self, event)
        self.dragMoveEvent  = lambda event: generic_drag_move_event(self, event)
        self.dropEvent      = lambda event: generic_drop_event(self, event)

def generic_drag_enter_event(self, event):
    if event.mimeData().hasUrls():
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.exists(path):  # Accept both files and folders
                event.setDropAction(Qt.LinkAction)  # "Open" cursor
                event.accept()
                return
    event.ignore()

def generic_drag_move_event(self, event):
    if event.mimeData().hasUrls():
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.exists(path):
                event.setDropAction(Qt.LinkAction)
                event.accept()
                return
    event.ignore()

def generic_drop_event(self, event):
    for url in event.mimeData().urls():
        path = url.toLocalFile()
        if hasattr(self, 'main_window'):
            handle_dropped_path(self.main_window, path)
        else:
            print("No main_window attribute found")

## check file extensition and define proper callback function

def handle_dropped_path(main_window, path):
    def is_nifti_file(filename: str) -> bool:
        fl = str(filename).lower()
        return fl.endswith('.nii') or fl.endswith('.nii.gz') or fl.endswith('.gz')

    def is_dicom_file(filename: str) -> bool:
        ext = os.path.splitext(filename)[-1].lower()
        return ext in ("", ".dcm", ".ima")

    def is_amigo_file(filename: str) -> bool:
        return os.path.splitext(filename)[-1].lower() == ".amigo"
    
    def is_stl_file(filename: str) -> bool:
        return os.path.splitext(filename)[-1].lower() == ".stl"
    
    def is_obj_file(filename: str) -> bool:
        return os.path.splitext(filename)[-1].lower() == ".obj"

    if os.path.isfile(path):
        if is_nifti_file(path):
            load_nifti_files(main_window, path)
        elif is_amigo_file(path):
            load_amigo_bundle(main_window, path)
        elif is_stl_file(path):
            load_stl_files(main_window, path)
        elif is_obj_file(path):
            load_obj_files(main_window, path)
        elif is_dicom_file(path):
            open_dicom_tag_viewer(path)
        else:
            print(f"Unsupported file type: {os.path.splitext(path)[-1]}")
        return

    elif os.path.isdir(path):
        try:
            has_dcm = False
            has_nifti = False
            has_iris = False
            for root, _, files in os.walk(path):
                for file in files:
                    fl = file.lower()
                    if fl.endswith(('.nii', '.nii.gz', '.gz')):
                        has_nifti = True
                        break
                    elif fl.endswith(('.dcm', '.ima')):
                        has_dcm = True
                        break
                    elif fl.endswith('.iris'):
                        has_iris = True
                        break
                if has_nifti or has_dcm or has_iris:
                    break

            if has_nifti:
                load_nifti_files(main_window, path)
                return
            elif has_dcm:
                load_all_dcm(main_window, folder_path=path,
                             progress_callback=main_window.update_progress,
                             update_label=main_window.label)
                return
            elif has_iris:
                print(f"Found IrIS file in: {path}")
                return
            else:
                # Fallback: check if DICOM without extensions
                load_all_dcm(main_window, folder_path=path,
                             progress_callback=main_window.update_progress,
                             update_label=main_window.label)
                return
        except Exception as e:
            print(f"Error scanning folder: {e}")