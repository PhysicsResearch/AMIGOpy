from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtkmodules.all as vtk
from PySide6.QtWidgets import QVBoxLayout, QWidget

def init_vtk3d_widget(self, placeholder_widget):
    """
    Embed a QVTKRenderWindowInteractor into placeholder_widget,
    give it a black background, trackball‐style interaction, and start it.
    Stores widget, renderer and interactor as self.vtk3dWidget, self.ren3D, self.iren3D.
    """
    # 1) Layout + widget
    vtk_layout3D = QVBoxLayout()
    vtk_layout3D.setContentsMargins(0, 0, 0, 0)
    self.vtk3dWidget = QVTKRenderWindowInteractor()        # no parent here
    vtk_layout3D.addWidget(self.vtk3dWidget)
    placeholder_widget.setLayout(vtk_layout3D)

    # 2) Renderer
    self.ren3D = vtk.vtkRenderer()
    self.ren3D.SetBackground(0.0, 0.0, 0.0)                # black
    self.vtk3dWidget.GetRenderWindow().AddRenderer(self.ren3D)

    # 3) Initialize & start
    self.vtk3dWidget.Initialize()
    self.vtk3dWidget.Start()                               # nonblocking under Qt

    # 4) Use a 3D trackball interactor
    style3D = vtk.vtkInteractorStyleTrackballCamera()
    self.vtk3dWidget.SetInteractorStyle(style3D)
    self.iren3D = self.vtk3dWidget.GetRenderWindow().GetInteractor()

    # 5) Install event filter for double click expand/restore
    self.vtk3dWidget.installEventFilter(self)
    placeholder_widget.installEventFilter(self)
    for child in self.vtk3dWidget.findChildren(QWidget):
        child.installEventFilter(self)

    return self.vtk3dWidget, self.ren3D, self.iren3D