from PyQt5.QtWidgets import QFileDialog, QMessageBox
import vtk
from vtkmodules.util.numpy_support import vtk_to_numpy
import numpy as np
from pathlib import Path
from fcn_load.populate_stl_list import populate_stl_tree


def load_stl_files(self, file_names=None):
    """
    Load one or more STL files. If file_names is None, opens dialog.
    Remembers last used directory in self.last_stl_dir.
    Stores all mesh data in self.STL_data (dict).
    """
    # Initialize STL_data if needed
    if not hasattr(self, 'STL_data') or self.STL_data is None:
        self.STL_data = {}

    # Determine directory to open dialog in
    start_dir = getattr(self, 'last_stl_dir', str(Path.home()))

    # Get file list
    if file_names is None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open STL surface files",
            start_dir,
            "STL files (*.stl);;All files (*)"
        )
    else:
        if isinstance(file_names, str):
            paths = [file_names]
        else:
            paths = list(file_names)

    if not paths:
        return

    # Update the last used directory
    self.last_stl_dir = str(Path(paths[0]).parent)

    for stl_path in paths:
        # --- Read STL ---
        reader = vtk.vtkSTLReader()
        reader.SetFileName(stl_path)
        reader.Update()
        polydata = reader.GetOutput()
        if polydata.GetNumberOfPoints() == 0:
            QMessageBox.warning(self, "STL Load Error", f"File '{stl_path}' could not be read as a valid STL mesh.")
            continue

        points = vtk_to_numpy(polydata.GetPoints().GetData())
        faces = []
        for i in range(polydata.GetNumberOfCells()):
            cell = polydata.GetCell(i)
            faces.append([cell.GetPointId(j) for j in range(cell.GetNumberOfPoints())])
        faces = np.array(faces, dtype=np.int32)

        name = Path(stl_path).stem
        key = name
        idx = 1
        while key in self.STL_data:
            key = f"{name}_{idx}"
            idx += 1

        try:
            with open(stl_path, 'rb') as f:
                header = f.read(80).decode(errors='ignore').strip()
        except Exception:
            header = ""

        self.STL_data[key] = {
            "name": key,
            "filename": stl_path,
            "points": points,
            "faces": faces,
            "header": header
        }

    # Populate the tree view with the loaded STL data
    populate_stl_tree(self)