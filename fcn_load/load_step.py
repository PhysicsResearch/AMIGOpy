from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
import numpy as np
from pathlib import Path
from fcn_load.populate_stl_list import populate_stl_tree

# OCC imports
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_SOLID, TopAbs_FACE
from OCC.Core.TopoDS import topods_Solid
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRep import BRep_Tool

def load_step_files(self, file_names=None):
    """
    Load one or more STEP files and add all solids (parts) to STL_data.
    Remembers last used directory in self.last_step_dir.
    Updates the tree using populate_stl_tree.
    """
    if not hasattr(self, 'STL_data') or self.STL_data is None:
        self.STL_data = {}

    start_dir = getattr(self, 'last_step_dir', str(Path.home()))

    if file_names is None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open STEP surface files",
            start_dir,
            "STEP files (*.step *.stp);;All files (*)"
        )
    else:
        if isinstance(file_names, str):
            paths = [file_names]
        else:
            paths = list(file_names)

    if not paths:
        return

    self.last_step_dir = str(Path(paths[0]).parent)

    for step_path in paths:
        self.progressBar.setValue(0)
        QApplication.processEvents()
        try:
            reader = STEPControl_Reader()
            status = reader.ReadFile(step_path)
            if status != 1:  # IFSelect_ReturnStatus == IFSelect_RetDone
                QMessageBox.warning(self, "STEP Load Error", f"File '{step_path}' could not be read as a valid STEP file (status={status}).")
                continue
            reader.TransferRoots()
            shape = reader.OneShape()
        except Exception as e:
            QMessageBox.warning(self, "STEP Load Error", f"File '{step_path}' could not be read as a valid STEP file.\n{e}")
            continue

        # Find all solids (parts) in the file
        explorer = TopExp_Explorer(shape, TopAbs_SOLID)
        solids = []
        while explorer.More():
            solids.append(topods_Solid(explorer.Current()))
            explorer.Next()

        n_solids = len(solids)
        if n_solids == 0:
            QMessageBox.warning(self, "STEP Load Error", f"File '{step_path}' contains no solids.")
            continue

        for solid_idx, solid in enumerate(solids, 1):
            # Mesh the solid (tessellation)
            BRepMesh_IncrementalMesh(solid, 0.1)
            points = []
            faces = []
            point_map = {}  # maps (x, y, z) to index
            idx_counter = 0

            face_exp = TopExp_Explorer(solid, TopAbs_FACE)
            while face_exp.More():
                face = face_exp.Current()
                triangulation = BRep_Tool.Triangulation(face, face.Location())
                if triangulation is not None:
                    nodes = triangulation.Nodes()
                    tris = triangulation.Triangles()
                    # map OCC nodes to point indices
                    local_indices = []
                    for i in range(1, nodes.Length()+1):
                        pt = nodes.Value(i)
                        key = (pt.X(), pt.Y(), pt.Z())
                        if key not in point_map:
                            point_map[key] = idx_counter
                            points.append([pt.X(), pt.Y(), pt.Z()])
                            idx_counter += 1
                        local_indices.append(point_map[key])
                    # faces
                    for i in range(1, tris.Length()+1):
                        tri = tris.Value(i)
                        faces.append([
                            local_indices[tri.Value(1) - 1],
                            local_indices[tri.Value(2) - 1],
                            local_indices[tri.Value(3) - 1]
                        ])
                face_exp.Next()

            points = np.array(points, dtype=np.float32)
            faces = np.array(faces, dtype=np.int32)
            name = f"{Path(step_path).stem}_part{solid_idx}" if n_solids > 1 else Path(step_path).stem
            key = name
            idx = 1
            while key in self.STL_data:
                key = f"{name}_{idx}"
                idx += 1
            self.STL_data[key] = {
                "name": key,
                "filename": step_path,
                "points": points,
                "faces": faces,
                "header": "STEP"
            }

            # Progress per part
            progress = (solid_idx / n_solids) * 100
            self.progressBar.setValue(int(progress))
            QApplication.processEvents()
        self.progressBar.setValue(100)
        QApplication.processEvents()

    populate_stl_tree(self)
