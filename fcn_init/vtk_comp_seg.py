import vtk
import numpy as np
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QVBoxLayout
from fcn_display.seg_mouse_fcn import left_button_pressseg_event, left_button_releaseseg_event, on_scroll_backwardseg, on_scroll_forwardseg, onMouseMoveseg
from fcn_display.win_level import set_window
from fcn_display.display_images_seg  import sliderSegView_change


def setup_vtk_seg(self):
    #
    self.textActorSeg ={}
    # First, clean up previous instances if they exist
    if hasattr(self, 'renSeg') and self.renSeg:
        for ren in self.renSeg:
            ren.RemoveAllViewProps()  # Remove all actors from the renderer
            ren.GetRenderWindow().Finalize()  # Clean up the render window
    self.renSeg = []  # Reset the renderer list
    
    if hasattr(self, 'vtkWidgetSeg') and self.vtkWidgetSeg:
        for vtkWidget in self.vtkWidgetSeg:
            vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveAllViewProps()
            vtkWidget.GetRenderWindow().Finalize()
            vtkWidget.setParent(None)
            vtkWidget.deleteLater()
    self.vtkWidgetSeg = []  # Reset the VTK widgets list
    
    # Assume similar reset/cleanup steps for dataImporterSeg, windowLevelSeg, and imageActorSeg
    self.dataImporterSeg = {}
    self.windowLevelSeg = {}
    self.imageActorSeg = {}
    self.interactor_to_index = {}
    #
    self.segViewSlider.valueChanged.connect(lambda: sliderSegView_change(self))
    #
    slice_data = np.zeros((100, 100), dtype=np.uint16)
    data_string = slice_data.tobytes()
    extent = slice_data.shape
    #
    vtk_layout = QVBoxLayout()
    self.vtkWidgetSeg = QVTKRenderWindowInteractor()
    vtk_layout.addWidget(self.vtkWidgetSeg)
    self.VTK_SegView.setLayout(vtk_layout)
    # Create the renderer here
    self.renSeg = vtk.vtkRenderer()
    self.vtkWidgetSeg.GetRenderWindow().AddRenderer(self.renSeg)
 
    # Start the VTK widget
    self.vtkWidgetSeg.Initialize()  
    self.vtkWidgetSeg.Start() 
    #
    imageStyle = vtk.vtkInteractorStyleImage()
    self.vtkWidgetSeg.SetInteractorStyle(imageStyle)

    self.renSeg.GetActiveCamera().SetParallelProjection(1)
    
    for i in range (0,4):
        self.dataImporterSeg[i] = vtk.vtkImageImport()
        self.windowLevelSeg[i]  = vtk.vtkImageMapToWindowLevelColors()
        self.windowLevelSeg[i].SetInputConnection(self.dataImporterSeg[i].GetOutputPort())
        self.imageActorSeg[i]   = vtk.vtkImageActor()
        self.imageActorSeg[i].GetMapper().SetInputConnection(self.windowLevelSeg[i].GetOutputPort())
        self.renSeg.AddActor(self.imageActorSeg[i])
    self.renSeg.ResetCamera()
        
    for i in range (0,4):
        self.dataImporterSeg[i].SetDataScalarTypeToUnsignedShort()
        self.dataImporterSeg[i].CopyImportVoidPointer(data_string, len(data_string))
        self.dataImporterSeg[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        self.dataImporterSeg[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        imageProperty = self.imageActorSeg[i].GetProperty()
        imageProperty.SetOpacity(0)  
        # Inform the pipeline that data has changed.
        self.dataImporterSeg[i].Modified()  
        #

    # After setting up your vtkWidget and renderer:
    interactor_styleSeg = self.vtkWidgetSeg.GetInteractorStyle()
    self.interactor_to_index[interactor_styleSeg] = i
    interactor_styleSeg.AddObserver("MouseWheelForwardEvent", lambda caller, event: on_scroll_forwardseg(self, caller, event))
    interactor_styleSeg.AddObserver("MouseWheelBackwardEvent", lambda caller, event: on_scroll_backwardseg(self, caller, event))
    interactor_styleSeg.AddObserver("LeftButtonReleaseEvent", lambda caller, event: left_button_releaseseg_event(self, caller, event))
    interactor_styleSeg.AddObserver("LeftButtonPressEvent", lambda caller, event: left_button_pressseg_event(self, caller, event))
    interactor_styleSeg.OnMouseWheelForward = lambda: None
    interactor_styleSeg.OnMouseWheelBackward = lambda: None
    interactor_styleSeg.OnLeftButtonDown = lambda: None
    interactor_styleSeg.OnLeftButtonUp = lambda: None
    #
    self.vtkWidgetSeg.AddObserver("LeftButtonPressEvent", lambda caller, event: left_button_pressseg_event(self, caller, event),0)
    self.vtkWidgetSeg.AddObserver("LeftButtonReleaseEvent",lambda caller, event:left_button_releaseseg_event(self, caller, event),0)
    # mouse
    self.vtkWidgetSeg.AddObserver("MouseWheelForwardEvent", lambda caller, event: on_scroll_forwardseg(self, caller, event))
    self.vtkWidgetSeg.AddObserver("MouseWheelBackwardEvent", lambda caller, event: on_scroll_backwardseg(self, caller, event))
    #
    self.vtkWidgetSeg.GetRenderWindow().GetInteractor().AddObserver("MouseMoveEvent",lambda caller, event:onMouseMoveseg(self, caller, event))
    # self.vtkWidgetSeg.GetRenderWindow().GetInteractor().AddObserver("KeyPressEvent",lambda caller, event:onKeyPressseg(self, caller, event))
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


