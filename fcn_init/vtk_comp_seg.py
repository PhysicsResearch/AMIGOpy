import vtk
import numpy as np
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QVBoxLayout
# from fcn_display.mouse_move_slicechanges import onMouseMoveCoronal, onMouseMoveSagittal, onMouseMoveAxial, left_button_pressaxial_event, left_button_releaseaxial_event
from fcn_display.seg_mouse_fcn import left_button_pressseg_event, left_button_releaseseg_event, on_scroll_backwardseg, on_scroll_forwardseg, onMouseMoveseg, onKeyPressseg
from fcn_display.display_images_comp import disp_comp_image_slice
from fcn_display.win_level import set_window
from fcn_display.display_images_seg  import sliderSegView_change


def comp_link_winlev(self):
    if self.link_win_lev.isChecked():
        set_window(self,-99,-99)
        disp_comp_image_slice(self)

def setup_vtk_comp_seg(self,N_im):
    #
    self.textActorAxSeg ={}
    # First, clean up previous instances if they exist
    if hasattr(self, 'renAxComp') and self.renAxSeg:
        for ren in self.renAxSeg:
            ren.RemoveAllViewProps()  # Remove all actors from the renderer
            ren.GetRenderWindow().Finalize()  # Clean up the render window
    self.renAxSeg = []  # Reset the renderer list
    
    if hasattr(self, 'vtkWidgetSeg') and self.vtkWidgetSeg:
        for vtkWidget in self.vtkWidgetSeg:
            vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveAllViewProps()
            vtkWidget.GetRenderWindow().Finalize()
            vtkWidget.setParent(None)
            vtkWidget.deleteLater()
    self.vtkWidgetSeg = []  # Reset the VTK widgets list
    
    # Assume similar reset/cleanup steps for dataImporterAxComp, windowLevelAxComp, and imageActorAxComp
    self.dataImporterAxSeg = {}
    self.windowLevelAxSeg = {}
    self.imageActorAxSeg = {}
    self.interactor_to_index = {}
    #
    self.SliderSegView.valueChanged.connect(lambda: sliderSegView_change(self))
    #
    slice_data = np.zeros((100, 100), dtype=np.uint16)
    data_string = slice_data.tobytes()
    extent = slice_data.shape
    #
    
    vtk_layout = QVBoxLayout()
    self.vtkWidgetSeg = QVTKRenderWindowInteractor()
    vtk_layout.addWidget(self.vtkWidgetSeg)
    self.VTK_view_seg.setLayout(vtk_layout)
    # Create the renderer here
    self.renSeg = vtk.vtkRenderer()
    self.vtkWidgetSeg.GetRenderWindow().AddRenderer(self.renSeg)
 
    # Start the VTK widget
    self.vtkWidgetSeg.Initialize()  
    self.vtkWidgetSeg.Start() 
    #
    imageStyle = vtk.vtkInteractorStyleImage()
    self.vtkWidgetAxial.SetInteractorStyle(imageStyle)

    self.renSeg.GetActiveCamera().SetParallelProjection(1)
    
    for i in range (0,4):
        self.dataImporterAxSeg[i] = vtk.vtkImageImport()
        self.windowLevelAxSeg[i]  = vtk.vtkImageMapToWindowLevelColors()
        self.windowLevelAxSeg[i].SetInputConnection(self.dataImporterAxComp[i].GetOutputPort())
        self.imageActorAxSeg[i]   = vtk.vtkImageActor()
        self.imageActorAxSeg[i].GetMapper().SetInputConnection(self.windowLevelAxSeg[i].GetOutputPort())
        self.renAxSeg[i].AddActor(self.imageActorAxSeg[i])
    self.renAxSeg[i].ResetCamera()
        
    
    for i in range (0,4):
        self.dataImporterAxSeg[i].SetDataScalarTypeToUnsignedShort()
        #
        self.dataImporterAxSeg[i].CopyImportVoidPointer(data_string, len(data_string))
        self.dataImporterAxSeg[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        self.dataImporterAxSeg[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        imageProperty = self.imageActorAxSeg[i].GetProperty()
        imageProperty.SetOpacity(0)  
        # Inform the pipeline that data has changed.
        self.dataImporterAxSeg[i].Modified()  
        #
    # After setting up your vtkWidget and renderer:
    interactor_styleSeg = self.vtkWidgetSeg[i].GetInteractorStyle()
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
    self.vtkWidgetSeg.GetRenderWindow().GetInteractor().AddObserver("KeyPressEvent",lambda caller, event:onKeyPressseg(self, caller, event))
    # Create text for annotation - lable-ID
    self.textActorAxSeg[0] = vtk.vtkTextActor()
    self.textActorAxSeg[0].GetTextProperty().SetFontFamilyToArial()
    self.textActorAxSeg[0].GetTextProperty().SetFontSize(12)
    self.textActorAxSeg[0].GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorAxSeg[0].GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorAxSeg[0].SetPosition(0.01, 0.95)  # position at the bottom left
    # Window and Level
    self.textActorAxSeg[1] = vtk.vtkTextActor()
    self.textActorAxSeg[1].GetTextProperty().SetFontFamilyToArial()
    self.textActorAxSeg[1].GetTextProperty().SetFontSize(12)
    self.textActorAxSeg[1].GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorAxSeg[1].GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorAxSeg[1].SetPosition(0.01, 0.90)  # Near top-left corner
    # Voxel info
    self.textActorAxSeg[2] = vtk.vtkTextActor()
    self.textActorAxSeg[2].GetTextProperty().SetFontFamilyToArial()
    self.textActorAxSeg[2].GetTextProperty().SetFontSize(12)
    self.textActorAxSeg[2].GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorAxSeg[2].GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorAxSeg[2].SetPosition(0.01, 0.01)  
    # add text actors
    self.renAxSeg.AddActor(self.textActorAxSeg[0])
    self.renAxSeg.AddActor(self.textActorAxSeg[1])
    self.renAxSeg.AddActor(self.textActorAxSeg[2])


