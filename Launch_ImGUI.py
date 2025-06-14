import sys
import os
import qdarkstyle
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar
from PyQt5.QtGui import QIcon
from ImGUI import Ui_AMIGOpy  # Assuming this is the name of your main window class in ImGUI.py
from fcn_load.sort_dcm import get_data_description
from fcn_load.org_fol_dcm import organize_files_into_folders
from fcn_breathing_curves.functions_plot import init_BrCv_plot, plotViewData_BrCv_plot
from fcn_breathing_curves.functions_edit import initXRange, init_BrCv_edit, plotViewData_BrCv_edit
from fcn_display.mouse_move_slicechanges import change_sliceAxial, change_sliceSagittal, change_sliceCoronal
from fcn_display.Data_tree_general import on_DataTreeView_clicked
from fcn_init.create_menu import initializeMenuBar
from fcn_init.vtk_comp import setup_vtk_comp
from fcn_init.vtk_comp_seg import setup_vtk_seg
from fcn_init.transp_slider_spin_set  import set_transp_slider_fcn
from fcn_init.set_menu_bar_icons      import menu_bar_icon_actions
from fcn_init.vtk_IrIS_eval_axes      import setup_vtk_IrISEval
from fcn_display.display_images       import update_layer_view
from fcn_display.display_images_seg   import update_seg_slider, disp_seg_image_slice
from fcn_init.ModulesTab_change       import set_fcn_tabModules_changed
from fcn_init.IrIS_cal_init           import init_cal_markers_IrIS
from fcn_init.init_variables          import initialize_software_variables
from fcn_init.init_tables             import initialize_software_tables
from fcn_init.init_buttons            import initialize_software_buttons
from fcn_init.init_load_files         import load_Source_cal_csv_file
from fcn_init.init_list_menus         import populate_list_menus
from fcn_init.init_drop_options       import initialize_drop_fcn
from fcn_load.load_dcm                import load_all_dcm
from fcn_segmentation.functions_segmentation import plot_hist
from fcn_init.init_vtk_3D_display     import init_vtk3d_widget
import vtk
from PyQt5.QtGui import QSurfaceFormat


class MyApp(QMainWindow, Ui_AMIGOpy):  # or QWidget/Ui_Form, QDialog/Ui_Dialog, etc.
    def __init__(self,folder_path=None):
        super(MyApp, self).__init__()
        #
        # Set up the user interface from Designer.
        self.setupUi(self)
        initializeMenuBar(self)
        
        self.DataType = "None"
        # Create a toolbar
        self.toolbar = QToolBar("My main toolbar")
        self.addToolBar(self.toolbar)

        # Set the progress bar value to 0
        self.progressBar.setValue(0)


        # populate the list menus
        populate_list_menus(self)
        # initialize variables
        initialize_software_variables(self)
        # initialize tables
        initialize_software_tables(self)
        # initialize buttons
        initialize_software_buttons(self)
        # initialize drop functions
        # Enable drag and drop
        initialize_drop_fcn(self)
        # load ref csv files
        load_Source_cal_csv_file(self)
        
        self.LeftButtonSagittalDown = False
        self.LeftButtonCoronalDown  = False
        self.LeftButtonRuler        = False
        # self.LeftButtonSegDown = False
        #
        set_fcn_tabModules_changed(self)
        

        #
        self.layerTab = {}
        self.transTab = {}
        #
        self.layerTab['View']               = 0
        self.transTab['View']               = [1,0,0,0]
        self.layerTab['_3Dview']            = 0
        self.transTab['_3Dview']            = [1,0,0,0]
        self.layerTab['Compare']            = 0
        self.transTab['Compare']            = [1,0,0,0]
        self.layerTab['IrIS']               = 0
        self.transTab['IrIS']               = [1,0,0,0]
        self.layerTab['DECT']               = 0
        self.transTab['DECT']               = [1,0,0,0]
        self.layerTab['Plan']               = 0
        self.transTab['Plan']               = [1,0,0,0]
        self.layerTab['CSV Files']          = 0
        self.transTab['CSV Files']          = [1,0,0,0]
        self.layerTab['Breathing curves']   = 0
        self.transTab['Breathing curves']   = [1,0,0,0]
        self.layerTab['Segmentation']       = 0
        self.transTab['Segmentation']       = [1,0.99,0.99,0]
        #
        # Set the path relative to the executable's location
        base_path = os.path.dirname(os.path.abspath(__file__))     # Location of the script or the executable
        menu_bar_icon_actions(self,base_path)
        #

        # This section initialize variables related to images dimentions, currentl displaying set
        # slice index ... It is important so different element of the GUI can have access to them 
        #
        self.dicom_data   = None            # Initialize the attribute to store DICOM data
        #self.TG43_Data    = None            # Initialize the attribute to store TG43 data
        self.IrIS_data    = None            # Initialize the attribute to store IrIS data
        self.IrIS_corr    = {}              # Initialize the attribute to store IrIS correction data
        self.current_slice_index = [-1,-1,-1]  # axial, sagital and coronal slices
        #
        # information about dwell positions and dwell times
        self.IrIS_Eval = {}
        #
        
        self.BrCvTab_index = 0
        self.tabWidget_BrCv.currentChanged.connect(lambda: init_BrCv_plot(self))
        self.plotXAxis_BrCv.currentTextChanged.connect(lambda: plotViewData_BrCv_plot(self))

        self.tabWidget_BrCv.currentChanged.connect(lambda: init_BrCv_edit(self))
        self.editXMinSlider_BrCv.valueChanged.connect(lambda: plotViewData_BrCv_edit(self))
        self.editXMaxSlider_BrCv.valueChanged.connect(lambda: plotViewData_BrCv_edit(self))
        self.editXAxis_BrCv.currentTextChanged.connect(lambda: initXRange(self))
        #
        self.LeftButtonAxialDown     = False
        self.LeftButtonSagittalDown  = False
        # self.LeftButtonSegDown = False
        #

        # This section conects GUI elemtns with functions
        # slider to adjust the images
        self.AxialSlider.valueChanged.connect(self.on_axialslider_change)
        self.SagittalSlider.valueChanged.connect(self.on_sagittalslider_change)
        self.CoronalSlider.valueChanged.connect(self.on_coronalslider_change)
        
        
              
        # # Initialize VTK components
        setup_vtk_comp(self)
        setup_vtk_IrISEval(self)
        setup_vtk_seg(self)
        # VTK 3D view
        self.VTK3D_widget, self.VTK3D_renderer, self.VTK3D_interactor = init_vtk3d_widget(self, self.VTK_view_3D)
        # Calibration module IrIS
        init_cal_markers_IrIS(self)
        
        self.segThreshMinHU.setValue(-200)
        self.segThreshMaxHU.setValue(200)
        self.segThreshMinHU.valueChanged.connect(self.on_seg_hu_min_change)
        self.segThreshMaxHU.valueChanged.connect(self.on_seg_hu_max_change)
        self.segSelectView.currentTextChanged.connect(lambda: update_seg_slider(self))
        self.segViewSlider.valueChanged.connect(lambda: disp_seg_image_slice(self))

        self.segBrushButton.setIcon(QIcon("./icons/brush.png"))
        self.segEraseButton.setIcon(QIcon("./icons/eraser.png") )
        self.undoSeg.setIcon(QIcon("./icons/undo.png"))
        #
        # VTK Comparison module
        self.vtkWidgetsComp = []
        self.renAxComp      = []
        self.dataImporterAxComp = {}
        self.windowLevelAxComp  = {}
        self.imageActorAxComp   = {}
        #
        
        self.DataTreeView.clicked.connect(lambda index: on_DataTreeView_clicked(self, index))
        #
        vtk.vtkObject.GlobalWarningDisplayOff()
        # if folder_path is not None:
        #     print(folder_path)
        #     load_all_dcm(self,folder_path, progress_callback=None, update_label=None)
        set_transp_slider_fcn(self)

    def organize_dcm_folder(self):
        self.label.setText("Reading folders")
        detailed_files_info, unique_files_info = get_data_description(folder_path=None, progress_callback=self.update_progress,update_label=self.label)
        total_steps = len(detailed_files_info)
        self.label.setText(f"Copying {total_steps} files")
        organize_files_into_folders(detailed_files_info,progress_callback=self.update_progress,update_label=self.label)
        
            
    # Slot for the 'About' action
    def on_about_click(self):
        # Your logic for displaying info about the application goes here.
        pass
     

        
    def left_button_presssagittal_event(self, obj, event):
        self.LeftButtonSagittalDown = True

    def left_button_releasesagittal_event(self, obj, event):
        self.LeftButtonSagittalDown = False
        
    def left_button_presscoronal_event(self, obj, event):
        self.LeftButtonCoronalDown = True

    def left_button_releasecoronal_event(self, obj, event):
        self.LeftButtonCoronalDown = False

    def on_axialslider_change(self):
        idx = self.layer_selection_box.currentIndex()
        # Set the slice index based on the slider value.
        self.current_axial_slice_index[idx] = self.AxialSlider.value()
        change_sliceAxial(self,0)
        
    def on_sagittalslider_change(self):
        idx = self.layer_selection_box.currentIndex()
        # Set the slice index based on the slider value.
        self.current_sagittal_slice_index[idx] = self.SagittalSlider.value()
        change_sliceSagittal(self,0)
            
    def on_coronalslider_change(self):
        idx = self.layer_selection_box.currentIndex()
        # Set the slice index based on the slider value.
        self.current_coronal_slice_index[idx] = self.CoronalSlider.value()
        change_sliceCoronal(self,0)
                    
    def on_scroll_forwardAxial(self, obj, ev):
        change_sliceAxial(self,1)
    
    def on_scroll_backwardAxial(self, obj, ev):
        change_sliceAxial(self,-1)
        
    def on_scroll_forwardSagittal(self, obj, ev):
        change_sliceSagittal(self,1)
    
    def on_scroll_backwardSagittal(self, obj, ev):
        change_sliceSagittal(self,-1)
        
    def on_scroll_forwardCoronal(self, obj, ev):
        change_sliceCoronal(self,1)
    
    def on_scroll_backwardCoronal(self, obj, ev):
        change_sliceCoronal(self,-1)
        
    def update_progress(self, progress):
        self.progressBar.setValue(int(progress))
   
    def on_seg_hu_min_change(self):
        min_ = self.segThreshMinHU.value()
        if min_ >= self.segThreshMaxHU.value():
            self.segThreshMinHU.setValue(self.segThreshMaxHU.value()-1)
        plot_hist(self)

    def on_seg_hu_max_change(self):
        max_ = self.segThreshMaxHU.value()
        if max_ <= self.segThreshMinHU.value():
            self.segThreshMaxHU.setValue(self.segThreshMinHU.value()+1)
        plot_hist(self)
        
if __name__ == "__main__":
    fmt = QSurfaceFormat()
    fmt.setVersion(3, 2)                   # request at least OpenGL 3.2
    fmt.setProfile(QSurfaceFormat.CoreProfile)
    fmt.setDepthBufferSize(24)
    fmt.setStencilBufferSize(8)
    QSurfaceFormat.setDefaultFormat(fmt)
    app = QApplication(sys.argv)
    folder_path = None
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]  # Capture folder path from the command-line arguments
    window = MyApp(folder_path)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window.show()
    if folder_path is not None:
        print(folder_path)
        load_all_dcm(window,folder_path, progress_callback=None, update_label=None)
    sys.exit(app.exec_())
