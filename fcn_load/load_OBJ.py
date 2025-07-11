from PyQt5.QtWidgets import QFileDialog, QMessageBox
import vtk
from vtkmodules.util.numpy_support import vtk_to_numpy
import numpy as np
from pathlib import Path
from fcn_load.populate_stl_list import populate_stl_tree
from PyQt5.QtWidgets import QApplication

def load_obj_files(self, file_names=None):
    """
    Load one or more OBJ files and add to STL_data.
    Remembers last used directory in self.last_obj_dir.
    Updates the tree using populate_stl_tree.
    """
    # Initialize STL_data if needed
    if not hasattr(self, 'STL_data') or self.STL_data is None:
        self.STL_data = {}

    # Determine directory to open dialog in
    start_dir = getattr(self, 'last_obj_dir', str(Path.home()))

    # Get file list
    if file_names is None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open OBJ surface files",
            start_dir,
            "OBJ files (*.obj);;All files (*)"
        )
    else:
        if isinstance(file_names, str):
            paths = [file_names]
        else:
            paths = list(file_names)

    if not paths:
        return

    # Update the last used directory
    self.last_obj_dir = str(Path(paths[0]).parent)

    for obj_path in paths:
        # Reset progress for this file
        self.progressBar.setValue(0)
        # --- OBJ reading as before ---
        reader = vtk.vtkOBJReader()
        reader.SetFileName(obj_path)
        reader.Update()
        polydata = reader.GetOutput()
        if polydata.GetNumberOfPoints() == 0:
            QMessageBox.warning(self, "OBJ Load Error", f"File '{obj_path}' could not be read as a valid OBJ mesh.")
            continue
        self.progressBar.setValue(10)
        tri_filter = vtk.vtkTriangleFilter()
        tri_filter.SetInputData(polydata)
        tri_filter.Update()
        polydata_tri = tri_filter.GetOutput()

        points = vtk_to_numpy(polydata_tri.GetPoints().GetData())
        n_cells = polydata_tri.GetNumberOfCells()
        faces = []

        # Extract triangles and update progress
        for i in range(n_cells):
            cell = polydata_tri.GetCell(i)
            faces.append([cell.GetPointId(j) for j in range(3)])
            # Update every 10%
            if n_cells > 10 and (i % max(1, n_cells // 10) == 0 or i == n_cells - 1):
                progress = ((i + 1) / n_cells) * 100
                self.progressBar.setValue(int(progress))
                QApplication.processEvents() # Ensure GUI updates

        faces = np.array(faces, dtype=np.int32)

        name = Path(obj_path).stem
        key = name
        idx = 1
        while key in self.STL_data:
            key = f"{name}_{idx}"
            idx += 1

        # Extract the first comment or header line, or leave empty
        try:
            with open(obj_path, 'r', encoding='utf-8', errors='ignore') as f:
                header = ""
                for line in f:
                    if line.startswith('#'):
                        header = line.strip()
                        break
        except Exception:
            header = ""

        self.STL_data[key] = {
            "name": key,
            "filename": obj_path,
            "points": points,
            "faces": faces,
            "header": header
        }

    # Populate the tree view with all loaded STL (and OBJ) data
    populate_stl_tree(self)