import vtk
import numpy as np
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5 import QtWidgets
from fcn_display.win_level import set_window
from fcn_display.display_images_IrISeval  import sliderIrISeval_change
from fcn_IrIS.FindDwell_IrIS  import process_frames, save_eval_to_csv, find_pks_dw, update_selection_tree, average_dw, average_frames_within_dw

from fcn_IrIS.plot_IrIS_profiles import plot_IrIS_eval
from fcn_load.read_IrIS import time_relative_2_channel

def populate_view_list(self):
    # List of operations
    view = ["XY","X-Time","Y-Time"]
    self.IrIS_eval_sel_box = self.findChild(QtWidgets.QComboBox, 'List_Eval_Direction')
    # Populate the QComboBox
    self.IrIS_eval_sel_box.addItems(view)
    # You can also connect the selection change event to a function
    #self.active_layer.currentIndexChanged.connect(lambda index: on_operation_selected(self, index))
    #
    plot_type = ["None","fps","Time","Peaks", "Mean", "Mean - Grad.", "Max. (90th)", "Max. (90th) - Grad.", "Diff. 1 Frame","Diff. N Frames", 
                 "Diff. 1 Frame %","Diff. N Frames %", "Max. Diff. 1 Frame","Max. Diff. N Frames"]
    #
    self.IrIS_plot_sel_box1 = self.findChild(QtWidgets.QComboBox, 'IrISPlot01')
    self.IrIS_plot_sel_box1.addItems(plot_type)
    self.IrIS_plot_sel_box2 = self.findChild(QtWidgets.QComboBox, 'IrISPlot02')
    self.IrIS_plot_sel_box2.addItems(plot_type)
    #self.IrIS_plot_sel_box2.setCurrentIndex(2)
    self.IrIS_plot_sel_box3 = self.findChild(QtWidgets.QComboBox, 'IrISPlot03')
    self.IrIS_plot_sel_box3.addItems(plot_type)
    #self.IrIS_plot_sel_box3.setCurrentIndex(3)

def setup_vtk_IrISEval(self):
    #
    # buttons
    self.Slider_Eval_IrIS.valueChanged.connect(lambda: sliderIrISeval_change(self))
    self.IrIS_ProcessPlot.clicked.connect(lambda: process_frames(self))
    self.IrIS_Plot.clicked.connect(lambda: plot_IrIS_eval(self))
    self.IrIS_ExportCSV.clicked.connect(lambda: save_eval_to_csv(self))
    self.IrIS_findPK.clicked.connect(lambda: find_pks_dw(self))
    self.Pk_Plot.clicked.connect(lambda: find_pks_dw(self))
    self.Pk_find_channel.valueChanged.connect(lambda: update_selection_tree(self))
    self.checkBox_IrIS_time_rel.stateChanged.connect(lambda: time_relative_2_channel(self))
    self.IrIsAVg_dw.clicked.connect(lambda: average_dw(self))
    self.IrIsAVg_Framesdw.clicked.connect(lambda: average_frames_within_dw(self))
    #
    #
    # Initialize variables
    populate_view_list(self)
    self.textActorIrEval    = {}
    self.vtkWidgetsIrEval   = {}  # Reset the VTK widgets list
    self.renIrEval          = {}  # Reset the renderer list
    # Assume similar reset/cleanup steps for dataImporterAxComp, windowLevelAxComp, and imageActorAxComp
    self.dataImporterIrEval = {}
    self.windowLevelIrEval  = {}
    self.imageActorIrEval   = {}
    #
    vtk_layout = QVBoxLayout() 
    self.vtkWidgetsIrEval= QVTKRenderWindowInteractor(self)
    vtk_layout.addWidget(self.vtkWidgetsIrEval)    
    self.IrIS_Ax_Eval_01.setLayout(vtk_layout)  # Set layout on the dynamically retrieved container
    # Create renderer, configure it, and add to vtkWidget
    self.renIrEval = vtk.vtkRenderer()
    self.vtkWidgetsIrEval.GetRenderWindow().AddRenderer(self.renIrEval)
    # Initialize and start VTK widget
    self.vtkWidgetsIrEval.Initialize()
    self.vtkWidgetsIrEval.Start()
    # Optional: Set interaction style
    imageStyle = vtk.vtkInteractorStyleImage()
    self.vtkWidgetsIrEval.SetInteractorStyle(imageStyle)
    self.renIrEval.GetActiveCamera().SetParallelProjection(1)
    slice_data  = np.zeros((100, 100), dtype=np.uint16)
    data_string = slice_data.tobytes()
    extent      = slice_data.shape
    for i in range(4):  # Assuming 4 layers, adjust the range as needed
        self.dataImporterIrEval[i] = vtk.vtkImageImport()
        self.windowLevelIrEval[i]  = vtk.vtkImageMapToWindowLevelColors()
        self.windowLevelIrEval[i].SetInputConnection(self.dataImporterIrEval[i].GetOutputPort())
        self.imageActorIrEval[i]   = vtk.vtkImageActor()
        self.imageActorIrEval[i].GetMapper().SetInputConnection(self.windowLevelIrEval[i].GetOutputPort()) 
        #
        self.dataImporterIrEval[i].SetDataScalarTypeToUnsignedShort()
        #
        self.dataImporterIrEval[i].CopyImportVoidPointer(data_string, len(data_string))
        self.dataImporterIrEval[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        self.dataImporterIrEval[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        imageProperty = self.imageActorIrEval[i].GetProperty()
        imageProperty.SetOpacity(0)  
        # Inform the pipeline that data has changed.
        self.dataImporterIrEval[i].Modified()          
        self.renIrEval.AddActor(self.imageActorIrEval[i])
    self.renIrEval.ResetCamera()
    #
    # # After setting up your vtkWidget and renderer:
    # interactor_styleAxial = self.vtkWidgetsComp[i].GetInteractorStyle()
    # interactor_styleAxial.AddObserver("MouseWheelForwardEvent", lambda caller, event: on_scroll_forwardcomp(self, caller, event))
    # interactor_styleAxial.AddObserver("MouseWheelBackwardEvent", lambda caller, event: on_scroll_backwardcomp(self, caller, event))
    # interactor_styleAxial.AddObserver("LeftButtonReleaseEvent", lambda caller, event: left_button_releasecomp_event(self, caller, event))
    # interactor_styleAxial.AddObserver("LeftButtonPressEvent", lambda caller, event: left_button_presscomp_event(self, caller, event))
    # interactor_styleAxial.OnMouseWheelForward = lambda: None
    # interactor_styleAxial.OnMouseWheelBackward = lambda: None
    # interactor_styleAxial.OnLeftButtonDown = lambda: None
    # interactor_styleAxial.OnLeftButtonUp = lambda: None
    # #
    # self.vtkWidgetsComp[i].AddObserver("LeftButtonPressEvent", lambda caller, event: left_button_presscomp_event(self, caller, event),0)
    # self.vtkWidgetsComp[i].AddObserver("LeftButtonReleaseEvent",lambda caller, event:left_button_releasecomp_event(self, caller, event),0)
    # # mouse
    # self.vtkWidgetsComp[i].AddObserver("MouseWheelForwardEvent", lambda caller, event: on_scroll_forwardcomp(self, caller, event))
    # self.vtkWidgetsComp[i].AddObserver("MouseWheelBackwardEvent", lambda caller, event: on_scroll_backwardcomp(self, caller, event))
    # #
    # self.vtkWidgetsComp[i].GetRenderWindow().GetInteractor().AddObserver("MouseMoveEvent",lambda caller, event:onMouseMovecomp(self, caller, event))
    # #
    # # Create text for annotation - lable-ID
    # self.textActorAxCom[i,0] = vtk.vtkTextActor()
    # self.textActorAxCom[i,0].GetTextProperty().SetFontFamilyToArial()
    # self.textActorAxCom[i,0].GetTextProperty().SetFontSize(12)
    # self.textActorAxCom[i,0].GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    # self.textActorAxCom[i,0].GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    # self.textActorAxCom[i,0].SetPosition(0.01, 0.95)  # position at the bottom left
    # # Window and Level
    # self.textActorAxCom[i,1] = vtk.vtkTextActor()
    # self.textActorAxCom[i,1].GetTextProperty().SetFontFamilyToArial()
    # self.textActorAxCom[i,1].GetTextProperty().SetFontSize(12)
    # self.textActorAxCom[i,1].GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    # self.textActorAxCom[i,1].GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    # self.textActorAxCom[i,1].SetPosition(0.01, 0.90)  # Near top-left corner
    # #
    # # Voxel info
    # self.textActorAxCom[i,2] = vtk.vtkTextActor()
    # self.textActorAxCom[i,2].GetTextProperty().SetFontFamilyToArial()
    # self.textActorAxCom[i,2].GetTextProperty().SetFontSize(12)
    # self.textActorAxCom[i,2].GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    # self.textActorAxCom[i,2].GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    # self.textActorAxCom[i,2].SetPosition(0.01, 0.01)  
    # #
    # # add text actors
    # self.renAxComp[i].AddActor(self.textActorAxCom[i,0])
    # self.renAxComp[i].AddActor(self.textActorAxCom[i,1])
    # self.renAxComp[i].AddActor(self.textActorAxCom[i,2])
