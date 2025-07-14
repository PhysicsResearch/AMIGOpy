from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
import trimesh
import numpy as np
from pathlib import Path
from fcn_load.populate_stl_list import populate_stl_tree

def load_3mf_files(self, file_names=None):
    """
    Load one or more 3MF files and add to STL_data.
    Remembers last used directory in self.last_3mf_dir.
    Updates the tree using populate_stl_tree.
    """
    if not hasattr(self, 'STL_data') or self.STL_data is None:
        self.STL_data = {}

    start_dir = getattr(self, 'last_3mf_dir', str(Path.home()))

    if file_names is None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open 3MF surface files",
            start_dir,
            "3MF files (*.3mf);;All files (*)"
        )
    else:
        if isinstance(file_names, str):
            paths = [file_names]
        else:
            paths = list(file_names)

    if not paths:
        return

    self.last_3mf_dir = str(Path(paths[0]).parent)

    for file_path in paths:
        self.progressBar.setValue(20)
        QApplication.processEvents()
        try:
            # trimesh.load can return a Scene if there are multiple objects
            scene_or_mesh = trimesh.load(file_path, force='scene')
        except Exception as e:
            QMessageBox.warning(self, "3MF Load Error", f"File '{file_path}' could not be read as a valid 3MF mesh.\n{e}")
            continue

        # Handle scene with multiple meshes
        if hasattr(scene_or_mesh, 'geometry'):
            mesh_dict = scene_or_mesh.geometry
        else:
            mesh_dict = {'main': scene_or_mesh}

        n_meshes = len(mesh_dict)
        for mesh_idx, (obj_name, mesh) in enumerate(mesh_dict.items(), 1):
            points = np.array(mesh.vertices, dtype=np.float32)
            faces = np.array(mesh.faces, dtype=np.int32)
            name = f"{Path(file_path).stem}_{obj_name}" if n_meshes > 1 else Path(file_path).stem
            key = name
            idx = 1
            while key in self.STL_data:
                key = f"{name}_{idx}"
                idx += 1

            self.STL_data[key] = {
                "name": key,
                "filename": file_path,
                "points": points,
                "faces": faces,
                "header": "3MF"
            }

            # Progress update per mesh in file
            progress = (mesh_idx / n_meshes) * 100
            self.progressBar.setValue(int(progress))
            QApplication.processEvents()

        self.progressBar.setValue(100)
        QApplication.processEvents()

    populate_stl_tree(self)