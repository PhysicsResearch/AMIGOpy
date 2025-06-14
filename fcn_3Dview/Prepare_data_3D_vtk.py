# Diplay dicom 3D - VTK

# Imports for VTK 9.x
from vtkmodules.vtkRenderingVolumeOpenGL2 import vtkSmartVolumeMapper
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtkmodules.all as vtk
from vtkmodules.util.numpy_support import numpy_to_vtk, get_vtk_array_type

# Standard imports
import numpy as np
from PyQt5.QtWidgets import QVBoxLayout

def display_numpy_volume(self,
                         volume_np: np.ndarray,
                         voxel_spacing=(1.0, 1.0, 1.0)):
    """
    Render a 3D NumPy array as a volume in the given renderer.
    
    Args:
        renderer:      vtkRenderer returned from init_vtk_widget
        interactor:    vtkRenderWindowInteractor returned from init_vtk_widget
        volume_np:     3D NumPy array with shape (Z, Y, X)
        voxel_spacing: tuple (sx, sy, sz), defaults to (1,1,1) if not provided
    """
    renderer   = self.VTK3D_renderer
    interactor = self.VTK3D_interactor

    # Convert NumPy array to a flat VTK array
    flat_data = volume_np.flatten(order='C')
    vtk_array = numpy_to_vtk(
        num_array=flat_data,
        deep=True,
        array_type=get_vtk_array_type(volume_np.dtype)
    )

    # Create vtkImageData and assign dimensions & spacing
    img = vtk.vtkImageData()
    img.SetDimensions(volume_np.shape[2], volume_np.shape[1], volume_np.shape[0])
    img.SetSpacing(*voxel_spacing)
    img.GetPointData().SetScalars(vtk_array)

    # Set up GPU volume mapper (falls back if no GPU)
    mapper = vtkSmartVolumeMapper()
    mapper.SetInputData(img)

    # Define simple grayscale transfer functions
    vmin, vmax = float(volume_np.min()), float(volume_np.max())
    ctf = vtk.vtkColorTransferFunction()
    ctf.AddRGBPoint(vmin, 0.0, 0.0, 0.0)
    ctf.AddRGBPoint(vmax, 1.0, 1.0, 1.0)

    otf = vtk.vtkPiecewiseFunction()
    otf.AddPoint(vmin, 0.0)
    otf.AddPoint(vmax, 1.0)

    vol_prop = vtk.vtkVolumeProperty()
    vol_prop.SetColor(ctf)
    vol_prop.SetScalarOpacity(otf)
    vol_prop.ShadeOn()
    vol_prop.SetInterpolationTypeToLinear()

    volume = vtk.vtkVolume()
    volume.SetMapper(mapper)
    volume.SetProperty(vol_prop)

    # Render: clear old, add new, reset camera
    renderer.RemoveAllViewProps()
    renderer.AddVolume(volume)
    renderer.ResetCamera()
    interactor.GetRenderWindow().Render()