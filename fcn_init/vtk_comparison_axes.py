import vtk
import numpy as np
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PySide6.QtWidgets import QVBoxLayout, QInputDialog
from PySide6 import QtWidgets
# from fcn_display.mouse_move_slicechanges import onMouseMoveCoronal, onMouseMoveSagittal, onMouseMoveAxial, left_button_pressaxial_event, left_button_releaseaxial_event
from fcn_display.comp_mouse_fcn import left_button_presscomp_event, left_button_releasecomp_event, on_scroll_backwardcomp, on_scroll_forwardcomp, onMouseMovecomp
from fcn_display.comp_link_zoom       import toggle_camera_linking
from fcn_display.display_images_comp import disp_comp_image_slice
from fcn_display.win_level import set_window
from fcn_display.display_images_comp  import sliderCompareView_change

# ---------------------------------------------------------------------------
# Compare-tab viewports style. We use standard vtkInteractorStyleUser to avoid
# default styles (zoom/dolly/WL) interfering with custom Compare tab events,
# and to avoid Python subclassing virtual dispatch overhead during mouse events.
# ---------------------------------------------------------------------------


class GridDimensionsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Grid Dimensions")
        self.setMinimumWidth(220)
        
        layout = QtWidgets.QFormLayout(self)
        
        self.rows_spin = QtWidgets.QSpinBox(self)
        self.rows_spin.setRange(1, 3)
        self.rows_spin.setValue(1)
        
        self.cols_spin = QtWidgets.QSpinBox(self)
        self.cols_spin.setRange(1, 4)
        self.cols_spin.setValue(2) # Default to 2 columns
        
        layout.addRow("Rows (1 - 3):", self.rows_spin)
        layout.addRow("Columns (1 - 4):", self.cols_spin)
        
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
    def get_dimensions(self):
        return self.rows_spin.value(), self.cols_spin.value()


def build_comparison_grid(self, rows, cols):
    N_im = cols * rows
    self.Comp_im_idx.setMaximum(N_im - 1)
    self.Comp_im_idx.setValue(0)
    populate_view_list(self)
    setup_vtk_comp(self, N_im)
    rearrange_widgets_in_grid(self, rows, cols)


def create_vtk_elements_comp(self):
    dialog = GridDimensionsDialog(self)
    if dialog.exec():
        rows, cols = dialog.get_dimensions()
        build_comparison_grid(self, rows, cols)


def on_grid_preset_changed(self, index):
    if index == 0:
        return # Placeholder selected
    combo = self.combo_grid_presets
    text = combo.itemText(index)
    
    mapping = {
        "1 Row x 1 Col": (1, 1),
        "1 Row x 2 Col": (1, 2),
        "1 Row x 3 Col": (1, 3),
        "1 Row x 4 Col": (1, 4),
        "2 Rows x 1 Col": (2, 1),
        "2 Rows x 2 Col": (2, 2),
        "2 Rows x 3 Col": (2, 3),
        "2 Rows x 4 Col": (2, 4),
        "3 Rows x 1 Col": (3, 1),
        "3 Rows x 2 Col": (3, 2),
        "3 Rows x 3 Col": (3, 3),
        "3 Rows x 4 Col": (3, 4)
    }
    
    if text in mapping:
        rows, cols = mapping[text]
        build_comparison_grid(self, rows, cols)


def populate_view_list(self):
    self.Comp_view_sel_box.blockSignals(True)
    self.Comp_view_sel_box.clear()
    self.Comp_view_sel_box.addItems(["Axial", "Sagittal", "Coronal"])
    self.Comp_view_sel_box.blockSignals(False)

def comp_link_winlev(self):
    if self.link_win_lev.isChecked():
        set_window(self,-99,-99)
        disp_comp_image_slice(self)

def setup_vtk_comp(self,N_im):
    from fcn_init.set_menu_bar_icons import remove_rulers, remove_points, remove_circles, remove_ellipses, remove_squares
    remove_rulers(self)
    remove_points(self)
    remove_circles(self)
    remove_ellipses(self)
    remove_squares(self)

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
                # Use vtkInteractorStyleUser which has no default bindings
                # to prevent built-in interactions from conflicting.
                imageStyle = vtk.vtkInteractorStyleUser()
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
                #
                #
                self.vtkWidgetsComp[i].AddObserver("LeftButtonPressEvent", lambda caller, event: left_button_presscomp_event(self, caller, event),0)
                self.vtkWidgetsComp[i].AddObserver("LeftButtonReleaseEvent",lambda caller, event:left_button_releasecomp_event(self, caller, event),0)
                # mouse
                # self.vtkWidgetsComp[i].AddObserver("MouseWheelForwardEvent", lambda caller, event: on_scroll_forwardcomp(self, caller, event))
                # self.vtkWidgetsComp[i].AddObserver("MouseWheelBackwardEvent", lambda caller, event: on_scroll_backwardcomp(self, caller, event))
                #
                iren = self.vtkWidgetsComp[i].GetRenderWindow().GetInteractor()
                iren.AddObserver("MouseMoveEvent",lambda caller, event:onMouseMovecomp(self, caller, event))
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
    


