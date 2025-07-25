import os
from PyQt5.QtWidgets import QWidget, QTreeView
from PyQt5.QtCore import Qt
from fcn_load.load_dcm  import load_all_dcm
from fcn_display.dicom_info import open_dicom_tag_viewer
from fcn_load.save_load import load_amigo_bundle
from fcn_load.load_STL import load_stl_files
from fcn_load.load_OBJ import load_obj_files


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
        self.setDragDropMode(self.DropOnly)

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
        if is_dicom_file(path):
            open_dicom_tag_viewer(path)

        elif is_amigo_file(path):
            # call your async loader (reuse the existing menu slot)
            load_amigo_bundle(main_window, path)      # see note ①
        elif is_stl_file(path):
            # call your async loader (reuse the existing menu slot)
            load_stl_files(main_window, path)      # see note ①
        elif is_obj_file(path):
            # call your async loader (reuse the existing menu slot)
            load_obj_files(main_window, path)      # see note ①
        else:
            print(f"Unsupported file type: {os.path.splitext(path)[-1]}")
        return

    elif os.path.isdir(path):
        # print(f"Dropped folder: {path}")
        try:
            for root, _, files in os.walk(path):
                for file in files:
                    full_path = os.path.join(root, file)
                    ext = os.path.splitext(file)[-1].lower()
                    if is_dicom_file(file):
                        load_all_dcm(main_window,folder_path=path,
                                    progress_callback=main_window.update_progress,
                                    update_label=main_window.label)                  	
                        return
                    elif ext == '.iris':
                        print(f"Found IrIS file: {full_path}")
                        return
            print("No recognized files found in folder.")
        except Exception as e:
            print(f"Error scanning folder: {e}")