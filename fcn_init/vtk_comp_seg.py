import vtk
import numpy as np
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from fcn_display.seg_mouse_fcn import left_button_pressseg_event, left_button_releaseseg_event, on_scroll_backwardseg, on_scroll_forwardseg, onMouseMoveseg, on_right_click_move_pan

def setup_vtk_seg(self):
    vtk_layoutSeg = QVBoxLayout()
    self.vtkWidgetSeg = QVTKRenderWindowInteractor()
    vtk_layoutSeg.addWidget(self.vtkWidgetSeg)
    self.VTK_SegView.setLayout(vtk_layoutSeg)
    # Create the renderer here
    self.renSeg = vtk.vtkRenderer()
    self.vtkWidgetSeg.GetRenderWindow().AddRenderer(self.renSeg)
    #
    self.textActorSeg ={}
    # Create text for annotation - lable-ID
    self.textActorSeg[0] = vtk.vtkTextActor()
    self.textActorSeg[0].GetTextProperty().SetFontFamilyToArial()
    self.textActorSeg[0].GetTextProperty().SetFontSize(12)
    self.textActorSeg[0].GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorSeg[0].GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorSeg[0].SetPosition(0.01, 0.95)  # position at the bottom left
    # Window and Level
    self.textActorSeg[1] = vtk.vtkTextActor()
    self.textActorSeg[1].GetTextProperty().SetFontFamilyToArial()
    self.textActorSeg[1].GetTextProperty().SetFontSize(12)
    self.textActorSeg[1].GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorSeg[1].GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorSeg[1].SetPosition(0.01, 0.90)  # Near top-left corner
    # Voxel info
    self.textActorSeg[2] = vtk.vtkTextActor()
    self.textActorSeg[2].GetTextProperty().SetFontFamilyToArial()
    self.textActorSeg[2].GetTextProperty().SetFontSize(12)
    self.textActorSeg[2].GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorSeg[2].GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorSeg[2].SetPosition(0.01, 0.01)  
    # add text actors
    self.renSeg.AddActor(self.textActorSeg[0])
    self.renSeg.AddActor(self.textActorSeg[1])
    self.renSeg.AddActor(self.textActorSeg[2])
    #
    # Start the VTK widget
    self.vtkWidgetSeg.Initialize()  
    self.vtkWidgetSeg.Start() 
    #
    imageStyle = vtk.vtkInteractorStyleImage()
    self.vtkWidgetSeg.SetInteractorStyle(imageStyle)
    # 
    self.dataImporterSeg = {}
    self.windowLevelSeg  = {}
    self.imageActorSeg   = {}
    self.interactor_to_index = {}
    #
    for i in range(4):  # Assuming 4 layers, adjust the range as needed
        self.dataImporterSeg[i] = vtk.vtkImageImport()
        self.windowLevelSeg[i]  = vtk.vtkImageMapToWindowLevelColors()
        self.windowLevelSeg[i].SetInputConnection(self.dataImporterSeg[i].GetOutputPort())
        self.imageActorSeg[i] = vtk.vtkImageActor()
        self.imageActorSeg[i].GetMapper().SetInputConnection(self.windowLevelSeg[i].GetOutputPort())
    #
    self.renSeg.GetActiveCamera().SetParallelProjection(1)
    #
    #
    slice_data = np.zeros((100, 100), dtype=np.uint16)
    data_string = slice_data.tobytes()
    extent = slice_data.shape
    # initialize display image
    for i in range(len(self.dataImporterSeg)):
        self.dataImporterSeg[i].SetDataScalarTypeToUnsignedShort()
        #
        self.dataImporterSeg[i].CopyImportVoidPointer(data_string, len(data_string))
        self.dataImporterSeg[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        self.dataImporterSeg[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        imageProperty = self.imageActorSeg[i].GetProperty()
        imageProperty.SetOpacity(0)  
        # Inform the pipeline that data has changed.
        self.dataImporterSeg[i].Modified()   
    #
    for i in range(len(self.dataImporterSeg)):
        self.renSeg.AddActor(self.imageActorSeg[i])
    self.renSeg.ResetCamera()
    #
    interactor = self.vtkWidgetSeg.GetRenderWindow().GetInteractor()
    interactor_styleSeg = self.vtkWidgetSeg.GetInteractorStyle()
    # self.interactor_to_index[interactor] = i
    self.interactor_to_index[interactor_styleSeg] = i
    # self.interactor_to_index[self.vtkWidgetSeg] = i
    interactor_styleSeg.AddObserver("MouseWheelForwardEvent", lambda caller, event: on_scroll_forwardseg(self, caller, event))
    interactor_styleSeg.AddObserver("MouseWheelBackwardEvent", lambda caller, event: on_scroll_backwardseg(self, caller, event))
    interactor_styleSeg.AddObserver("LeftButtonReleaseEvent", lambda caller, event: left_button_releaseseg_event(self, caller, event))
    interactor_styleSeg.AddObserver("LeftButtonPressEvent", lambda caller, event: left_button_pressseg_event(self, caller, event))
    interactor_styleSeg.AddObserver("RightButtonReleaseEvent", lambda caller, event:on_right_click_move_pan(self, caller, event))
    interactor_styleSeg.AddObserver("MiddleButtonReleaseEvent", lambda caller, event:on_right_click_move_pan(self, caller, event))
    interactor_styleSeg.OnMouseWheelForward = lambda: None
    interactor_styleSeg.OnMouseWheelBackward = lambda: None
    interactor_styleSeg.OnLeftButtonDown = lambda: None
    interactor_styleSeg.OnLeftButtonUp = lambda: None
    #
    self.vtkWidgetSeg.AddObserver("LeftButtonPressEvent", lambda caller, event: left_button_pressseg_event(self, caller, event),0)
    self.vtkWidgetSeg.AddObserver("LeftButtonReleaseEvent",lambda caller, event:left_button_releaseseg_event(self, caller, event),0)
    self.vtkWidgetSeg.AddObserver("MouseWheelForwardEvent", lambda caller, event: on_scroll_forwardseg(self, caller, event))
    self.vtkWidgetSeg.AddObserver("MouseWheelBackwardEvent", lambda caller, event: on_scroll_backwardseg(self, caller, event))
    self.vtkWidgetSeg.AddObserver("RightButtonReleaseEvent", lambda caller, event:on_right_click_move_pan(self, caller, event))
    self.vtkWidgetSeg.AddObserver("MiddleButtonReleaseEvent", lambda caller, event:on_right_click_move_pan(self, caller, event))
    #
    self.vtkWidgetSeg.GetRenderWindow().GetInteractor().AddObserver("MouseMoveEvent",lambda caller, event:onMouseMoveseg(self, caller, event))

    # Limit the naming of structures to letters and digits
    reg_ex = QRegExp("[a-zA-Z][a-zA-Z0-9]{0,15}")
    input_validator = QRegExpValidator(reg_ex, self.segStructName)
    self.segStructName.setValidator(input_validator)
