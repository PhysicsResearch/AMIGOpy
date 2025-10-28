import os, sys, traceback, faulthandler
faulthandler.enable()
os.environ.setdefault("QT_OPENGL", "software")  # safer on RDP/VM

from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QSurfaceFormat, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QToolBar
from PySide6.QtCore import QEvent, Qt, QTimer, Signal, QObject
# Force software GL (stable on many Windows setups)
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL, True)

# Compatibility profile is safest with VTK on Windows
fmt = QSurfaceFormat()
fmt.setRenderableType(QSurfaceFormat.OpenGL)
fmt.setProfile(QSurfaceFormat.CompatibilityProfile)
fmt.setVersion(3, 2)
fmt.setDepthBufferSize(24)
fmt.setStencilBufferSize(8)
QSurfaceFormat.setDefaultFormat(fmt)

from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor as QVTKWidget

import vtk
from PySide6.QtWidgets import QApplication
import qdarkstyle
from uiImGUI import Ui_AMIGOpy
from fcn_load.sort_dcm import get_data_description
from fcn_load.org_fol_dcm import organize_files_into_folders
from fcn_breathing_curves.functions_plot import init_BrCv_plot, plotViewData_BrCv_plot
from fcn_breathing_curves.functions_edit import initXRange, init_BrCv_edit, plotViewData_BrCv_edit
from fcn_breathing_curves.functions_phantom_operation import set_fcn_MoVeTab_changed
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
from fcn_init.vtk_hist import init_histogram_ui
from fcn_segmentation.functions_segmentation import plot_hist
from fcn_init.init_vtk_3D_display     import init_vtk3d_widget


from fcn_3Dview.volume_3d_viewer import VTK3DViewerMixin
from fcn_3Dview.structures_3D_table import init_3D_Struct_table 
from fcn_init.init_tool_tip import set_tooltip
from fcn_3Dview.surfaces_3D_table import init_STL_Surface_table
from fcn_3Dview.protons_3D_plan import init_3D_proton_table
from fcn_init.init_data_tree import set_context_menu
from fcn_3DPrinting.material_selection import calculate_red_settings
from fcn_3DPrinting import handlers as hdl

# from fcn_init.init_reg_elements import init_reg_elements




# map logical names -> (pane_object_name, slider_object_name)
_VIEW_ATTRS = {
    "axial":    ("VTK_view_01", "AxialSlider"),
    "sagittal": ("VTK_view_02", "SagittalSlider"),
    "coronal":  ("VTK_view_03", "CoronalSlider"),
}

# original grid positions in the new layout
_ORIG_POS = {
    "axial":    {"pane": (0, 0), "slider": (1, 0)},
    "sagittal": {"pane": (0, 1), "slider": (1, 1)},
    "coronal":  {"pane": (0, 2), "slider": (1, 2)},
    # tab spans all columns at row=2
    "tab":      {"pane": (2, 0), "span": (1, 3)},
}
# 
def _resolve_names(axis: str):
    """
    Return (pane_name, vtk_name, slider_name) no matter how _VIEW_ATTRS is shaped.
    If only (pane, slider) are provided, vtk_name == pane_name.
    """
    names = _VIEW_ATTRS[axis]
    if isinstance(names, dict):
        pane = names["pane"]
        vtk  = names.get("vtk", pane)
        sl   = names["slider"]
        return pane, vtk, sl
    elif len(names) == 3:
        return names  # (pane, vtk, slider)
    elif len(names) == 2:
        pane, sl = names
        return pane, pane, sl
    else:
        raise ValueError(f"Bad mapping for {axis}: {names!r}")
# ──────────────────────────────────────────────────────────────────────────────

class MyApp(QMainWindow, Ui_AMIGOpy, VTK3DViewerMixin):  # or QWidget/Ui_Form, QDialog/Ui_Dialog, etc.
        # emmit signal when the slice changes
        # This signal can be connected to other functions to update the display when the slice changes.
    sliceChanged = Signal(str, list)

    def __init__(self,folder_path=None):
        super(MyApp, self).__init__()
        
        # Set up the user interface from Designer.
        self.setupUi(self)

        self.setWindowTitle("AMIGOpy")
        #
        #
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
        #
        init_3D_Struct_table(self)
        init_STL_Surface_table(self)
        init_3D_proton_table(self)
        
        #
        self.LeftButtonSagittalDown = False
        self.LeftButtonCoronalDown  = False
        self.LeftButtonRuler        = False
        # self.LeftButtonSegDown = False
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
        self.layerTab['3D Printing']        = 0
        self.transTab['3D Printing']        = [1,0,0,0]
        #


        # This section initialize variables related to images dimentions, currentl displaying set
        # slice index ... It is important so different element of the GUI can have access to them 
        #
        self.medical_image   = None            # Initialize the attribute to store DICOM data
        self.IrIS_data    = None            # Initialize the attribute to store IrIS data
        self.STL_data     = None            # Initialize the attribute to store STL data
        self.IrIS_corr    = {}              # Initialize the attribute to store IrIS correction data
        self.current_slice_index = [-1,-1,-1]  # axial, sagital and coronal slices
        #
        # information about dwell positions and dwell times
        self.IrIS_Eval = {}
        #

        #
        self.BrCvTab_index = 0
        self.tabWidget_BrCv.currentChanged.connect(lambda: init_BrCv_plot(self))
        self.plotXAxis_BrCv.currentTextChanged.connect(lambda: plotViewData_BrCv_plot(self))

        self.tabWidget_BrCv.currentChanged.connect(lambda: init_BrCv_edit(self))
        self.editXMinSlider_BrCv.valueChanged.connect(lambda: plotViewData_BrCv_edit(self))
        self.editXMaxSlider_BrCv.valueChanged.connect(lambda: plotViewData_BrCv_edit(self))
        self.editXAxis_BrCv.currentTextChanged.connect(lambda: initXRange(self))
        self.DuetIPAddress.setText("192.168.0.1")

        set_fcn_MoVeTab_changed(self)
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
        init_histogram_ui(self)
        self._hook_vtk_dblclicks()
        # Calibration module IrIS
        init_cal_markers_IrIS(self)
        
        self.threshMinHU.setText("-200")
        self.threshMaxHU.setText("200")
        self.threshMinHU.textChanged.connect(lambda: plot_hist(self))
        self.threshMaxHU.textChanged.connect(lambda: plot_hist(self))
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
        set_transp_slider_fcn(self)
        #
        # # Initialize the 3D viewer
        self.VTK3D_widget, self.VTK3D_renderer, self.VTK3D_interactor = \
            init_vtk3d_widget(self, self.VTK_view_3D)
        self.init_3d_viewer()       

        set_fcn_tabModules_changed(self)
        # state flag: which axis is currently maximised  (None → original layout)
        self._max_axis = None
        self._cycle_order = ["axial", "sagittal", "coronal"]

        # for axis in _VIEW_ATTRS.keys():
        #     _, vtk_name, _ = _resolve_names(axis)
        #     vtkw = getattr(self, vtk_name)
        #     vtkw._axis_name = axis
        #     vtkw.installEventFilter(self)

        # Install filter on the parent container for “show all”
        self.im_display_tab.installEventFilter(self)
        #
        # 3D view:
        self.VTK_view_3D.installEventFilter(self)
        self.vtk3dWidget.installEventFilter(self)
        self._vtk3d_is_maximized = False
        #
        initializeMenuBar(self)
        self.DataType = "None"
        # Create a toolbar
        self.toolbar = QToolBar("My main toolbar")
        self.addToolBar(self.toolbar)
                # Set the path relative to the executable's location
        base_path = os.path.dirname(os.path.abspath(__file__))     # Location of the script or the executable
        menu_bar_icon_actions(self,base_path)
        #

        # Set the progress bar value to 0
        self.progressBar.setValue(0)

        # set tooltip 
        set_tooltip(self)

        # set data tree context menu
        set_context_menu(self)

        

    def organize_dcm_folder(self):
        self.label.setText("Reading folders")
        detailed_files_info, unique_files_info, outputfolder = get_data_description(folder_path=None, progress_callback=self.progressBar.setValue,update_label=self.label,sort_folder=1)
        total_steps = len(detailed_files_info)
        self.label.setText(f"Copying {total_steps} files")
        organize_files_into_folders(outputfolder, detailed_files_info,progress_callback=self.progressBar.setValue,update_label=self.label)
        
            
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
        idx = self.layer_selected.currentIndex()
        # Set the slice index based on the slider value.
        self.current_axial_slice_index[idx] = self.AxialSlider.value()
        change_sliceAxial(self,0)
        
    def on_sagittalslider_change(self):
        idx = self.layer_selected.currentIndex()
        # Set the slice index based on the slider value.
        self.current_sagittal_slice_index[idx] = self.SagittalSlider.value()
        change_sliceSagittal(self,0)
            
    def on_coronalslider_change(self):
        idx = self.layer_selected.currentIndex()
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

    


    def _get_next_axis(self):
        if self._max_axis is None:
            return "axial"
        idx = self._cycle_order.index(self._max_axis)
        return self._cycle_order[(idx + 1) % len(self._cycle_order)]

    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonDblClick and event.button() == Qt.MouseButton.LeftButton:
            if watched is self.im_display_tab:
                self.set_view_mode("all")
                return True

            if watched is self.VTK_view_3D or watched is self.vtk3dWidget:
                parent = self.VTK_view_3D.parentWidget()
                current_tab = self.tabModules.tabText(self.tabModules.currentIndex())
                if current_tab == "_3Dview":
                    layout = parent.layout()
                    if not self._vtk3d_is_maximized:
                        # Store original grid layout position
                        row, col, rowSpan, colSpan = _find_widget_in_gridlayout(layout, self.VTK_view_3D)
                        self._vtk3d_orig_grid = (row, col, rowSpan, colSpan)
                        self._vtk3d_orig_parent = parent
                        self._vtk3d_orig_geometry = self.VTK_view_3D.geometry()
                        # Maximize widget to fill parent
                        self.VTK_view_3D.setParent(parent)
                        self.VTK_view_3D.raise_()
                        self.VTK_view_3D.setGeometry(parent.rect())
                        self.VTK_view_3D.show()
                        self._vtk3d_is_maximized = True
                    else:
                        # Restore to original grid position and span
                        row, col, rowSpan, colSpan = self._vtk3d_orig_grid
                        layout.addWidget(self.VTK_view_3D, row, col, rowSpan, colSpan)
                        self.VTK_view_3D.setParent(parent)
                        self.VTK_view_3D.setMinimumSize(0, 0)  # Reset min size
                        self.VTK_view_3D.updateGeometry()
                        self._vtk3d_is_maximized = False
                return True

            # Double click on any axis render widget
            if hasattr(watched, "_axis_name"):
                axis = watched._axis_name
                if self._max_axis != axis:
                    # If not maximized, maximize this one
                    self.set_view_mode(axis)
                else:
                    # If maximized, go to the next in cycle
                    next_axis = self._get_next_axis()
                    self.set_view_mode(next_axis)
                return True

        return super().eventFilter(watched, event)



    def _hook_vtk_dblclicks(self):
        # Install the event filter on the QVTKRenderWindowInteractor children,
        # not on the placeholder containers.
        for axis in _VIEW_ATTRS.keys():
            pane_name, _, _ = _resolve_names(axis)
            holder = getattr(self, pane_name)
            for vtk_child in holder.findChildren(QVTKWidget):
                vtk_child._axis_name = axis
                vtk_child.installEventFilter(self)
        


    def set_view_mode(self, mode: str = "all"):
        """
        mode = "all" | "axial" | "coronal" | "sagittal"
        3-col layout in 'all':
        row 0: VTK1 | VTK2 | VTK3
        row 1:  S1  |  S2  |  S3
        row 2: [ tabView01 spans 3 cols ]
        In single mode:
        row 0: [   BIG spans 3 cols   ]
        row 1: [ BIG slider spans 3  ]
        (tab + other views/sliders hidden)
        """
        if mode not in {"all", "axial", "coronal", "sagittal"}:
            print(f"[set_view_mode] unknown key {mode!r}")
            return

        gl = self.gridLayout_4

        # resolve widgets
        def w(name): return getattr(self, name)
        views = {k: (w(p), w(s)) for k, (p, s) in _VIEW_ATTRS.items()}
        tab = self.tabView01

        # clear grid
        while gl.count():
            gl.takeAt(0)

        # hide everything upfront (prevents leftovers)
        for vw, sl in views.values():
            vw.hide()
            sl.hide()
            sl.setMinimumHeight(0)
        tab.hide()
        if hasattr(self, "label_2"):
            self.label_2.hide()  # just in case

        if mode == "all":
            # --- equal 3-up + sliders + tab
            gl.setRowStretch(0, 5)   # views
            gl.setRowStretch(1, 0)   # sliders
            gl.setRowStretch(2, 2)   # tab
            gl.setColumnStretch(0, 1); gl.setColumnStretch(1, 1); gl.setColumnStretch(2, 1)

            for key, (vw, sl) in views.items():
                r, c = _ORIG_POS[key]["pane"];   gl.addWidget(vw, r, c, 1, 1); vw.show()
                r, c = _ORIG_POS[key]["slider"]; gl.addWidget(sl, r, c, 1, 1); sl.show()

            r, c = _ORIG_POS["tab"]["pane"]; rs, cs = _ORIG_POS["tab"]["span"]
            gl.addWidget(tab, r, c, rs, cs); tab.show()

            self._max_axis = None
            return

        # --- true single-ax maximize: only BIG view + its slider
        big_axis = mode
        big_vw, big_sl = views[big_axis]

        # give almost all space to row 0 (big view); small to row 1 (slider)
        gl.setRowStretch(0, 9)    # big view
        gl.setRowStretch(1, 1)    # slider
        gl.setRowStretch(2, 0)    # no tab row used
        gl.setColumnStretch(0, 1); gl.setColumnStretch(1, 1); gl.setColumnStretch(2, 1)

        # add ONLY the big view and its slider
        gl.addWidget(big_vw, 0, 0, 1, 3); big_vw.show()
        gl.addWidget(big_sl, 1, 0, 1, 3); big_sl.show()

        # keep tab/others hidden (already hidden above)
        self._max_axis = big_axis

    def _resolve_names(axis: str):
        names = _VIEW_ATTRS[axis]
        if isinstance(names, dict):
            pane = names["pane"]; vtk = names.get("vtk", pane); sl = names["slider"]; return pane, vtk, sl
        elif len(names) == 3:
            return names
        elif len(names) == 2:
            pane, sl = names; return pane, pane, sl
        else:
            raise ValueError(f"Bad mapping for {axis}: {names!r}")

    def _hook_vtk_dblclicks(self):
        for axis in _VIEW_ATTRS.keys():
            pane_name, _, _ = _resolve_names(axis)
            holder = getattr(self, pane_name)
            for vtk_child in holder.findChildren(QVTKWidget):
                vtk_child._axis_name = axis
                vtk_child.installEventFilter(self)


def _find_widget_in_gridlayout(layout, widget):
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item and item.widget() is widget:
            row, col, rowSpan, colSpan = layout.getItemPosition(i)
            return row, col, rowSpan, colSpan
    return None, None, 1, 1


def calculate_red(self):
        filament = self.filament_combo.currentText()
        tissue   = self.tissue_combo.currentText()
        if filament and tissue:
            result = calculate_red_settings(self.cal_mat_path, self.ICRU_reference_path, filament, tissue)
            self.result_text.setPlainText(str(result))





if __name__ == "__main__":
    import sys, os, time
    from PySide6.QtCore import Qt, QCoreApplication, QTimer
    from PySide6.QtGui import QSurfaceFormat, QPixmap
    from PySide6.QtWidgets import QApplication, QSplashScreen
    import qdarkstyle
    import resources_rc 

    # --- Keep your GL defaults (unchanged) ---
    fmt = QSurfaceFormat()
    fmt.setRenderableType(QSurfaceFormat.OpenGL)
    fmt.setProfile(QSurfaceFormat.CompatibilityProfile)
    fmt.setDepthBufferSize(24)
    fmt.setStencilBufferSize(8)
    QSurfaceFormat.setDefaultFormat(fmt)

    app = QApplication(sys.argv)

    # --- Show splash ASAP ---
    # Pu
    pix = QPixmap(":/assets/Open_logo.png")
    if pix.isNull():
        pix = QPixmap(600, 300); pix.fill(Qt.black)
    if pix.isNull():
        pix = QPixmap(600, 300)  # fallback
        pix.fill(Qt.black)
    splash = QSplashScreen(pix)
    splash.showMessage("Starting AMIGOpy…", Qt.AlignBottom | Qt.AlignHCenter | Qt.TextWordWrap, Qt.white)
    splash.show()
    app.processEvents()  # let the splash paint immediately

    # --- Create main window (keep __init__ as-is for now) ---
    folder_path = sys.argv[1] if len(sys.argv) > 1 else None
    window = MyApp(folder_path)

    # Optional: apply theme after splash is visible
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
    splash.showMessage("Loading UI…", Qt.AlignBottom | Qt.AlignHCenter | Qt.TextWordWrap, Qt.white)
    app.processEvents()

    # --- Show window and close splash ---
    window.show()
    splash.finish(window)

    # (Optional) if you pass a folder on the command line, keep your current behavior
    if folder_path is not None:
        load_all_dcm(window, folder_path, progress_callback=None, update_label=None)

    sys.exit(app.exec())



