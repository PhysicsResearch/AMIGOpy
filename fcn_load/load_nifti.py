
import os
import SimpleITK as sitk
import numpy as np
from PyQt5.QtWidgets import QFileDialog
from pathlib import Path
from fcn_load.populate_nifti_list import populate_nifti_tree

def read_nifti(path):
    filename = os.path.basename(path).removesuffix('.nii.gz')

    reader = sitk.ImageFileReader()
    reader.SetImageIO("NiftiImageIO")
    reader.SetFileName(path)
    image = reader.Execute()

    # Get image volume and flip to match coordinate system
    image = sitk.Cast(image, sitk.sitkInt16)
    image_volume = sitk.GetArrayFromImage(image)
    image_volume = np.flip(image_volume, axis=1)

    # Get metadata
    spacing = image.GetSpacing()
    size = image.GetSize()
    origin = image.GetOrigin()

    return {'SeriesNumber': filename, '3DMatrix': image_volume, 
            'metadata': {'SliceThickness': spacing[2],'PixelSpacing': spacing[0:2], 
                         'size': size, 'ImagePositionPatient': origin}
    }


def load_nifti_files(self, path=None):

    start_dir = getattr(self, 'last_nifti_dir', str(Path.home()))

    if path is None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open nifti files",
            start_dir,
            "Nifti files (*.nii.gz);;All files (*)"
        )
    else:
        # If dir, import all nii.gz files
        if os.path.isdir(path):
            paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.nii.gz')]

        if os.path.isfile(path):
            paths = [path]

    if len(paths) == 0:
        return
    
    # Initialize nifti_data if needed
    if not hasattr(self, 'nifti_data') or self.nifti_data is None:
        self.nifti_data = []

    for path in paths:
        if path.endswith('.nii.gz'):
            data = read_nifti(path)
            self.nifti_data.append(data)

    self.last_nifti_dir = str(Path(paths[0]).parent)
    self.file_format = "nifti"

    populate_nifti_tree(self)