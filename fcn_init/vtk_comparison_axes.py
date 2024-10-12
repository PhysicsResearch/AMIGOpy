import vtk
import numpy as np
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QVBoxLayout, QInputDialog
from PyQt5 import QtWidgets
# from fcn_display.mouse_move_slicechanges import onMouseMoveCoronal, onMouseMoveSagittal, onMouseMoveAxial, left_button_pressaxial_event, left_button_releaseaxial_event
from fcn_display.comp_mouse_fcn import left_button_presscomp_event, left_button_releasecomp_event, on_scroll_backwardcomp, on_scroll_forwardcomp, onMouseMovecomp
from fcn_display.comp_link_zoom       import toggle_camera_linking
from fcn_display.display_images_comp import disp_comp_image_slice
from fcn_display.win_level import set_window
from fcn_display.display_images_comp  import sliderCompareView_change

def create_vtk_elements_comp(self):
    # 
    cols, ok1 = QInputDialog.getInt(self, "Input Collumn", "Enter N collumns (max 4):", min=1, max=4, step=1)
    if not ok1:
        return  # User cancelled or closed the dialog
    # 
    rows, ok2 = QInputDialog.getInt(self, "Input Rows", "Enter N rows (max 3):", min=1, max=3, step=1)
    if not ok2:
        return  # User cancelled or closed the dialog
    
    #
    N_im = cols*rows
    #
    self.Comp_im_idx.setMaximum(N_im-1)
    self.Comp_im_idx.setValue(0)
    populate_view_list(self)
    setup_vtk_comp(self,N_im)
    rearrange_widgets_in_grid(self, rows, cols)


def populate_view_list(self):
    # List of operations
    view = ["Axial","Sagittal","Coronal"]
    self.view_sel_box = self.findChild(QtWidgets.QComboBox, 'Comp_view_sel_box')
    # Populate the QComboBox
    self.view_sel_box.addItems(view)
    # You can also connect the selection change event to a function
    #self.active_layer.currentIndexChanged.connect(lambda index: on_operation_selected(self, index))

def comp_link_winlev(self):
    if self.link_win_lev.isChecked():
        set_window(self,-99,-99)
        disp_comp_image_slice(self)

def setup_vtk_comp(self,N_im):
    #
    self.textActorAxCom ={}
    # # First, clean up previous instances if they exist
    # if hasattr(self, 'renAxComp') and self.renAxComp:
    #     for ren in self.renAxComp:
    #         ren.RemoveAllViewProps()  # Remove all actors from the renderer
    #         ren.GetRenderWindow().Finalize()  # Clean up the render window
    # self.renAxComp = []  # Reset the renderer list
    
    if hasattr(self, 'vtkWidgetsComp') and self.vtkWidgetsComp:
        for vtkWidget in self.vtkWidgetsComp:
            vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveAllViewProps()
            vtkWidget.GetRenderWindow().Finalize()
            vtkWidget.setParent(None)
            vtkWidget.deleteLater()
    self.vtkWidgetsComp = []  # Reset the VTK widgets list
    self.renAxComp = []  # Reset the renderer list
    # Assume similar reset/cleanup steps for dataImporterAxComp, windowLevelAxComp, and imageActorAxComp
    self.dataImporterAxComp = {}
    self.windowLevelAxComp = {}
    self.imageActorAxComp = {}
    self.interactor_to_index = {}
    #
    self.SliderCompareView.valueChanged.connect(lambda: sliderCompareView_change(self))
    self.comp_link_zoom.stateChanged.connect(lambda: toggle_camera_linking(self))
    self.link_win_lev.stateChanged.connect(lambda: comp_link_winlev(self))
    #
    slice_data = np.zeros((100, 100), dtype=np.uint16)
    data_string = slice_data.tobytes()
    extent = slice_data.shape
    #
    for i in range(N_im):
        containerName = f"Ax_comp_cont_{i+1}"  # Construct the dynamic attribute name
        containerWidget = getattr(self, containerName, None)  # Safely get the attribute
        #
        if containerWidget is not None:
                vtk_layout = QVBoxLayout()
                vtkWidget  = QVTKRenderWindowInteractor(self)
                self.vtkWidgetsComp.append(vtkWidget)  # Store for later use
                vtk_layout.addWidget(vtkWidget)
                containerWidget.setLayout(vtk_layout)  # Set layout on the dynamically retrieved container
                # Create renderer, configure it, and add to vtkWidget
                ren = vtk.vtkRenderer()
                self.renAxComp.append(ren)  # Store for later use
                vtkWidget.GetRenderWindow().AddRenderer(ren)
                # Initialize and start VTK widget
                vtkWidget.Initialize()
                vtkWidget.Start()
                # Optional: Set interaction style
                imageStyle = vtk.vtkInteractorStyleImage()
                self.vtkWidgetsComp[i].SetInteractorStyle(imageStyle)
                ren.GetActiveCamera().SetParallelProjection(1)
                #
                for j in range (0,4):
                    self.dataImporterAxComp[i,j] = vtk.vtkImageImport()
                    self.windowLevelAxComp[i,j]  = vtk.vtkImageMapToWindowLevelColors()
                    self.windowLevelAxComp[i,j].SetInputConnection(self.dataImporterAxComp[i,j].GetOutputPort())
                    self.imageActorAxComp[i,j]   = vtk.vtkImageActor()
                    self.imageActorAxComp[i,j].GetMapper().SetInputConnection(self.windowLevelAxComp[i,j].GetOutputPort())
                    self.renAxComp[i].AddActor(self.imageActorAxComp[i,j])
                self.renAxComp[i].ResetCamera()
                    
                #
                for j in range (0,4):
                    self.dataImporterAxComp[i,j].SetDataScalarTypeToUnsignedShort()
                    #
                    self.dataImporterAxComp[i,j].CopyImportVoidPointer(data_string, len(data_string))
                    self.dataImporterAxComp[i,j].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
                    self.dataImporterAxComp[i,j].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
                    imageProperty = self.imageActorAxComp[i,j].GetProperty()
                    imageProperty.SetOpacity(0)  
                    # Inform the pipeline that data has changed.
                    self.dataImporterAxComp[i,j].Modified()  
                    #
                # After setting up your vtkWidget and renderer:
                interactor_styleAxial = self.vtkWidgetsComp[i].GetInteractorStyle()
                self.interactor_to_index[interactor_styleAxial] = i
                interactor_styleAxial.AddObserver("MouseWheelForwardEvent", lambda caller, event: on_scroll_forwardcomp(self, caller, event))
                interactor_styleAxial.AddObserver("MouseWheelBackwardEvent", lambda caller, event: on_scroll_backwardcomp(self, caller, event))
                interactor_styleAxial.AddObserver("LeftButtonReleaseEvent", lambda caller, event: left_button_releasecomp_event(self, caller, event))
                interactor_styleAxial.AddObserver("LeftButtonPressEvent", lambda caller, event: left_button_presscomp_event(self, caller, event))
                interactor_styleAxial.OnMouseWheelForward = lambda: None
                interactor_styleAxial.OnMouseWheelBackward = lambda: None
                interactor_styleAxial.OnLeftButtonDown = lambda: None
                interactor_styleAxial.OnLeftButtonUp = lambda: None
                #
                self.vtkWidgetsComp[i].AddObserver("LeftButtonPressEvent", lambda caller, event: left_button_presscomp_event(self, caller, event),0)
                self.vtkWidgetsComp[i].AddObserver("LeftButtonReleaseEvent",lambda caller, event:left_button_releasecomp_event(self, caller, event),0)
                # mouse
                self.vtkWidgetsComp[i].AddObserver("MouseWheelForwardEvent", lambda caller, event: on_scroll_forwardcomp(self, caller, event))
                self.vtkWidgetsComp[i].AddObserver("MouseWheelBackwardEvent", lambda caller, event: on_scroll_backwardcomp(self, caller, event))
                #
                self.vtkWidgetsComp[i].GetRenderWindow().GetInteractor().AddObserver("MouseMoveEvent",lambda caller, event:onMouseMovecomp(self, caller, event))
                #
                # Create text for annotation - lable-ID
                self.textActorAxCom[i,0] = vtk.vtkTextActor()
                self.textActorAxCom[i,0].GetTextProperty().SetFontFamilyToArial()
                self.textActorAxCom[i,0].GetTextProperty().SetFontSize(12)
                self.textActorAxCom[i,0].GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
                self.textActorAxCom[i,0].GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
                self.textActorAxCom[i,0].SetPosition(0.01, 0.95)  # position at the bottom left
                # Window and Level
                self.textActorAxCom[i,1] = vtk.vtkTextActor()
                self.textActorAxCom[i,1].GetTextProperty().SetFontFamilyToArial()
                self.textActorAxCom[i,1].GetTextProperty().SetFontSize(12)
                self.textActorAxCom[i,1].GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
                self.textActorAxCom[i,1].GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
                self.textActorAxCom[i,1].SetPosition(0.01, 0.90)  # Near top-left corner
                #
                # Voxel info
                self.textActorAxCom[i,2] = vtk.vtkTextActor()
                self.textActorAxCom[i,2].GetTextProperty().SetFontFamilyToArial()
                self.textActorAxCom[i,2].GetTextProperty().SetFontSize(12)
                self.textActorAxCom[i,2].GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
                self.textActorAxCom[i,2].GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
                self.textActorAxCom[i,2].SetPosition(0.01, 0.01)  
                #
                # add text actors
                self.renAxComp[i].AddActor(self.textActorAxCom[i,0])
                self.renAxComp[i].AddActor(self.textActorAxCom[i,1])
                self.renAxComp[i].AddActor(self.textActorAxCom[i,2])

        
        





def rearrange_widgets_in_grid(self, rows, cols):
    # Assuming groupBox_2 is the QGroupBox you're working with
    gridLayout = self.groupBox_2.layout()

    # Optional: Remove all widgets from the layout first if rearranging
    # This step depends on your application's needs
    for i in reversed(range(gridLayout.count())): 
        widget = gridLayout.itemAt(i).widget()
        gridLayout.removeWidget(widget)
        widget.hide()  # Hide the widget temporarily
    # Now, add the widgets back in the new configuration
    for row in range(rows):
        for col in range(cols):
            widget =  self.vtkWidgetsComp[row * cols + col]
            if widget:
                gridLayout.addWidget(widget, row, col)
                widget.show()  # Ensure the widget is visible   
    


