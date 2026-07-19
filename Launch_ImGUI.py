import os, sys, traceback, faulthandler
faulthandler.enable()
os.environ.setdefault("QT_OPENGL", "software")  # safer on RDP/VM

# Force pyarrow to be treated as unavailable to prevent crashes from leftover files in dirty upgrades
sys.modules['pyarrow'] = None

from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QSurfaceFormat, QIcon, QGuiApplication
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
from fcn_display.mouse_move_slicechanges import change_sliceAxial, change_sliceSagittal, change_sliceCoronal
from fcn_display.Data_tree_general import on_DataTreeView_clicked
from fcn_init.create_menu import initializeMenuBar
from fcn_init.vtk_comp import setup_vtk_comp
from fcn_init.transp_slider_spin_set  import set_transp_slider_fcn
from fcn_init.set_menu_bar_icons      import menu_bar_icon_actions
from fcn_display.display_images       import update_layer_view
from fcn_display.display_images_seg   import update_seg_slider, disp_seg_image_slice
from fcn_init.ModulesTab_change       import set_fcn_tabModules_changed
from fcn_init.init_variables          import initialize_software_variables
from fcn_init.init_tables             import initialize_software_tables
from fcn_init.init_buttons            import initialize_software_buttons
from fcn_init.create_3D_database_tab  import setup_3d_database_tab, setup_mat_mix_tab
from fcn_init.init_load_files         import load_Source_cal_csv_file
from fcn_init.init_list_menus         import populate_list_menus
from fcn_init.init_drop_options       import initialize_drop_fcn
from fcn_load.load_dcm                import load_all_dcm

from fcn_3Dview.volume_3d_viewer import VTK3DViewerMixin
from fcn_init.init_tool_tip import set_tooltip
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

        self.setWindowIcon(QIcon("AMBpy.ico"))
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
        # initialize 3D Printing Database tab
        setup_3d_database_tab(self)
        setup_mat_mix_tab(self)
        # initialize drop functions
        # Enable drag and drop
        initialize_drop_fcn(self)

        # Restructure layout of centralwidget to use a horizontal splitter
        import shiboken6
        from PySide6.QtWidgets import QSplitter, QVBoxLayout, QHBoxLayout, QWidget, QGridLayout
        
        # 1. Remove widgets from the old gridLayout_3
        self.gridLayout_3.removeWidget(self.groupBox_17)
        self.gridLayout_3.removeWidget(self.groupBox)
        self.gridLayout_3.removeWidget(self.progressBar)
        self.gridLayout_3.removeWidget(self.label_2)
        self.gridLayout_3.removeWidget(self.tabModules)
        
        # 2. Delete the old gridLayout_3 layout safely
        shiboken6.delete(self.gridLayout_3)
        
        # 3. Create a horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal, self.centralwidget)
        main_splitter.setObjectName("main_horizontal_splitter")
        main_splitter.setHandleWidth(8)
        
        # 4. Create a left-side container widget and layout
        left_container = QWidget(main_splitter)
        left_container.setObjectName("left_side_container")
        left_container.setMinimumWidth(1)
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # Create a vertical splitter for the left panel widgets so they expand and are resizable
        left_splitter = QSplitter(Qt.Vertical, left_container)
        left_splitter.setObjectName("left_vertical_splitter")
        left_splitter.setHandleWidth(8)
        
        self.groupBox_17.setMinimumSize(1, 1)
        self.DataTreeView.setMinimumSize(1, 1)
        self.groupBox.setMinimumSize(1, 1)
        left_splitter.addWidget(self.groupBox_17)
        left_splitter.addWidget(self.groupBox)
        left_splitter.setStretchFactor(0, 3)
        left_splitter.setStretchFactor(1, 1)
        
        left_layout.addWidget(left_splitter, 1)
        left_layout.addWidget(self.progressBar)
        left_layout.addWidget(self.label_2)
        
        # 5. Add widgets to splitter
        self.tabModules.setMinimumWidth(1)
        main_splitter.addWidget(left_container)
        main_splitter.addWidget(self.tabModules)
        
        # 6. Set initial pane sizes & stretch factors
        main_splitter.setSizes([320, 1300])
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 4)
        
        # 7. Create a new layout on centralwidget containing the splitter
        new_central_layout = QVBoxLayout(self.centralwidget)
        new_central_layout.setContentsMargins(10, 10, 10, 10)
        new_central_layout.addWidget(main_splitter)

        # -------------------------------------------------------------
        # Restructure display layout with vertical splitter (Horizontal divider bar)
        # between the VTK orthogonal views/axes (top) and tabView01 (bottom)
        # -------------------------------------------------------------
        # Remove widgets from old layout
        self.gridLayout_4.removeWidget(self.VTK_view_01)
        self.gridLayout_4.removeWidget(self.VTK_view_02)
        self.gridLayout_4.removeWidget(self.VTK_view_03)
        self.gridLayout_4.removeWidget(self.AxialSlider)
        self.gridLayout_4.removeWidget(self.SagittalSlider)
        self.gridLayout_4.removeWidget(self.CoronalSlider)
        self.gridLayout_4.removeWidget(self.tabView01)
        
        # Delete old layout
        shiboken6.delete(self.gridLayout_4)
        
        # Create a vertical splitter for the display tab (creates horizontal drag divider bar)
        self.view_splitter = QSplitter(Qt.Vertical, self.im_display_tab)
        self.view_splitter.setObjectName("main_view_vertical_splitter")
        self.view_splitter.setHandleWidth(8)
        
        # Create container and layout for top views
        top_views_container = QWidget(self.view_splitter)
        top_views_container.setMinimumHeight(1)
        self.top_grid = QGridLayout(top_views_container)
        self.top_grid.setContentsMargins(0, 0, 0, 0)
        self.top_grid.setSpacing(6)
        
        # Override self.gridLayout_4 so set_view_mode populates the top grid layout
        self.gridLayout_4 = self.top_grid
        
        # Add views and sliders to top_grid immediately so they have a valid parent layout
        # hierarchy on VTK initialization/startup.
        self.VTK_view_01.setMinimumSize(1, 1)
        self.VTK_view_02.setMinimumSize(1, 1)
        self.VTK_view_03.setMinimumSize(1, 1)
        self.top_grid.addWidget(self.VTK_view_01, 0, 0, 1, 1)
        self.top_grid.addWidget(self.VTK_view_02, 0, 1, 1, 1)
        self.top_grid.addWidget(self.VTK_view_03, 0, 2, 1, 1)
        self.top_grid.addWidget(self.AxialSlider, 1, 0, 1, 1)
        self.top_grid.addWidget(self.SagittalSlider, 1, 1, 1, 1)
        self.top_grid.addWidget(self.CoronalSlider, 1, 2, 1, 1)
        
        # Add components to splitter
        self.tabView01.setMinimumHeight(1)
        self.view_splitter.addWidget(top_views_container)
        self.view_splitter.addWidget(self.tabView01)
        
        # Set stretch factors & initial sizes
        self.view_splitter.setStretchFactor(0, 3)
        self.view_splitter.setStretchFactor(1, 2)
        self.view_splitter.setSizes([500, 300])
        
        # Create new layout for display tab containing the splitter
        new_display_layout = QVBoxLayout(self.im_display_tab)
        new_display_layout.setContentsMargins(0, 0, 0, 0)
        new_display_layout.addWidget(self.view_splitter)

        # -------------------------------------------------------------
        # Restructure View tab in tabView01 (bottom area) with a horizontal splitter
        # between the histogram (left) and the transform tabs (right)
        # -------------------------------------------------------------
        # Remove widgets from the gridLayout_81 on tab_5
        self.gridLayout_81.removeWidget(self.hist_container_01)
        self.gridLayout_81.removeWidget(self.tabWidget_10)
        
        # Delete old gridLayout_81
        shiboken6.delete(self.gridLayout_81)
        
        # Create a horizontal splitter for the bottom View tab
        self.bottom_view_splitter = QSplitter(Qt.Horizontal, self.tab_5)
        self.bottom_view_splitter.setObjectName("bottom_view_horizontal_splitter")
        self.bottom_view_splitter.setHandleWidth(8)
        
        # Set minimum sizes to 1 to allow smooth intermediate steps
        self.hist_container_01.setMinimumWidth(1)
        self.tabWidget_10.setMinimumWidth(1)
        
        # Add components to the splitter
        self.bottom_view_splitter.addWidget(self.hist_container_01)
        self.bottom_view_splitter.addWidget(self.tabWidget_10)
        
        # Set stretch factors & initial sizes
        self.bottom_view_splitter.setStretchFactor(0, 2)
        self.bottom_view_splitter.setStretchFactor(1, 1)
        self.bottom_view_splitter.setSizes([600, 300])
        
        # Create a new layout for tab_5 to hold the splitter
        new_tab5_layout = QHBoxLayout(self.tab_5)
        new_tab5_layout.setContentsMargins(0, 0, 0, 0)
        new_tab5_layout.addWidget(self.bottom_view_splitter)

        # load ref csv files
        # load_Source_cal_csv_file(self)
        #
        # 3D tables are now lazy loaded in fcn_init/ModulesTab_change.py
        #

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
        self.image           = None            # Initialize the attribute to store DICOM data
        self.IrIS_data       = None            # Initialize the attribute to store IrIS data
        self.STL_data        = None            # Initialize the attribute to store STL data
        self.IrIS_corr    = {}              # Initialize the attribute to store IrIS correction data
        self.current_slice_index = [-1,-1,-1]  # axial, sagital and coronal slices
        #
        # information about dwell positions and dwell times
        self.IrIS_Eval = {}
        #

        #
        self.BrCvTab_index = 0
        self.DuetIPAddress.setText("192.168.0.1")
        # Breathing curves connects/setups are now lazy loaded on tab change in ModulesTab_change.py

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
        # IrIS, Segmentation, and Histogram are now lazy loaded in ModulesTab_change.py/view_hist.py
        self._hook_vtk_dblclicks()
        
        self.threshMinHU.setText("-200")
        self.threshMaxHU.setText("200")
        def run_plot_hist():
            from fcn_segmentation.functions_segmentation import plot_hist
            plot_hist(self)
        self.threshMinHU.textChanged.connect(run_plot_hist)
        self.threshMaxHU.textChanged.connect(run_plot_hist)
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
        # # 3D viewer is now lazy loaded on tab change in ModulesTab_change.py
        #


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
        if event.type() == QEvent.MouseButtonDblClick and event.button() == Qt.LeftButton:
            # If an ROI just consumed this double-click, don't toggle the view
            if getattr(self, "_roi_dblclick_consumed", False):
                self._roi_dblclick_consumed = False
                return True  # stop here

            # Optional guard: if text/handle is being dragged, ignore dbl-clicks
            if getattr(self, "_text_dragging", False):
                return True

            # --- your existing logic follows ---
            if watched is self.im_display_tab:
                self.set_view_mode("all")
                return True

            if watched is self.VTK_view_3D or (hasattr(self, 'vtk3dWidget') and watched is self.vtk3dWidget):
                parent = self.VTK_view_3D.parentWidget()
                current_tab = self.tabModules.tabText(self.tabModules.currentIndex())
                if current_tab == "_3Dview":
                    layout = parent.layout()
                    if not getattr(self, '_vtk3d_is_maximized', False):
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

            if hasattr(watched, "_axis_name"):
                axis = watched._axis_name
                if self._max_axis != axis:
                    self.set_view_mode(axis)
                else:
                    self.set_view_mode(self._get_next_axis())
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

        # Save sizes if we are maximizing from the unmaximized (all) state
        if mode != "all" and self._max_axis is None and hasattr(self, 'view_splitter'):
            self._saved_view_splitter_sizes = self.view_splitter.sizes()

        # clear grid
        while gl.count():
            gl.takeAt(0)

        # hide everything upfront (prevents leftovers)
        for vw, sl in views.values():
            vw.hide()
            sl.hide()
            sl.setMinimumHeight(0)
        tab.hide()

        if mode == "all":
            # --- equal 3-up + sliders
            gl.setRowStretch(0, 1)   # views get all the vertical space in top_views_container
            gl.setRowStretch(1, 0)   # sliders wrap height
            gl.setRowStretch(2, 0)   # no tab row stretch
            gl.setColumnStretch(0, 1); gl.setColumnStretch(1, 1); gl.setColumnStretch(2, 1)

            for key, (vw, sl) in views.items():
                r, c = _ORIG_POS[key]["pane"];   gl.addWidget(vw, r, c, 1, 1); vw.show()
                r, c = _ORIG_POS[key]["slider"]; gl.addWidget(sl, r, c, 1, 1); sl.show()

            # If splitter is initialized, tab is managed by it
            if hasattr(self, 'view_splitter'):
                tab.show()
                # Restore the splitter sizes so the panel structure doesn't collapse
                if hasattr(self, '_saved_view_splitter_sizes'):
                    self.view_splitter.setSizes(self._saved_view_splitter_sizes)
                else:
                    self.view_splitter.setSizes([500, 300])
            else:
                r, c = _ORIG_POS["tab"]["pane"]; rs, cs = _ORIG_POS["tab"]["span"]
                gl.addWidget(tab, r, c, rs, cs); tab.show()

            self._max_axis = None
            return

        # --- true single-ax maximize: only BIG view + its slider
        big_axis = mode
        big_vw, big_sl = views[big_axis]

        # give all space to row 0 (big view) in top_views_container
        gl.setRowStretch(0, 1)    # big view gets all vertical space
        gl.setRowStretch(1, 0)    # slider wraps height
        gl.setRowStretch(2, 0)    # no tab row stretch
        gl.setColumnStretch(0, 1); gl.setColumnStretch(1, 1); gl.setColumnStretch(2, 1)

        # add ONLY the big view and its slider
        gl.addWidget(big_vw, 0, 0, 1, 3); big_vw.show()
        gl.addWidget(big_sl, 1, 0, 1, 3); big_sl.show()

        # keep tab/others hidden (already hidden above)
        self._max_axis = big_axis

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
    import sys, os, time, traceback, datetime
    from PySide6.QtCore import Qt, QCoreApplication, QTimer
    from PySide6.QtGui import QSurfaceFormat, QPixmap
    from PySide6.QtWidgets import QApplication, QSplashScreen, QMessageBox
    from PySide6.QtNetwork import QLocalServer, QLocalSocket
    import qdarkstyle
    import resources_rc 

    # --- Setup log directory and file in AppData ---
    appdata_dir = os.path.join(os.getenv('APPDATA', os.path.expanduser('~')), 'AMIGOpy')
    try:
        os.makedirs(appdata_dir, exist_ok=True)
        log_file_path = os.path.join(appdata_dir, 'amigopy.log')
        log_file = open(log_file_path, 'w', encoding='utf-8')
        log_file.write(f"=== AMIGOpy Log Started: {datetime.datetime.now()} ===\n")
        log_file.flush()
    except Exception as e:
        log_file = None
        print("Failed to initialize logging:", e)

    # Redirection class for standard outputs
    class LoggerRedirector:
        def __init__(self, original_stream, log_file):
            self.original_stream = original_stream
            self.log_file = log_file

        def write(self, message):
            if self.original_stream:
                try:
                    self.original_stream.write(message)
                except:
                    pass
            if self.log_file:
                try:
                    self.log_file.write(message)
                    self.log_file.flush()
                except:
                    pass

        def flush(self):
            if self.original_stream:
                try:
                    self.original_stream.flush()
                except:
                    pass
            if self.log_file:
                try:
                    self.log_file.flush()
                except:
                    pass

    # Redirect sys.stdout and sys.stderr
    if log_file:
        sys.stdout = LoggerRedirector(sys.stdout, log_file)
        sys.stderr = LoggerRedirector(sys.stderr, log_file)

    # Custom exception hook to display a critical QMessageBox on crash
    def exception_hook(exctype, value, tb):
        tb_str = "".join(traceback.format_exception(exctype, value, tb))
        sys.stderr.write(f"\nFATAL EXCEPTION CRASH:\n{tb_str}\n")
        
        if QApplication.instance():
            QMessageBox.critical(
                None,
                "AMIGOpy Crash",
                f"AMIGOpy has encountered a fatal error and has crashed.\n\n"
                f"Error Details:\n{value}\n\n"
                f"A detailed log containing the crash traceback has been saved to:\n"
                f"{log_file_path}\n\n"
                f"Please retrieve this log file to inspect or report the issue.",
                QMessageBox.StandardButton.Ok
            )
        sys.__excepthook__(exctype, value, tb)
        sys.exit(1)

    sys.excepthook = exception_hook

    # --- Keep your GL defaults (unchanged) ---
    fmt = QSurfaceFormat()
    fmt.setRenderableType(QSurfaceFormat.OpenGL)
    fmt.setProfile(QSurfaceFormat.CompatibilityProfile)
    fmt.setDepthBufferSize(24)
    fmt.setStencilBufferSize(8)
    QSurfaceFormat.setDefaultFormat(fmt)

    # Set Windows Taskbar Icon Grouping ID so the taskbar icon displays correctly
    import ctypes
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("amigo.amigopy.gui.1.0")
    except Exception:
        pass

    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("AMBpy.ico"))

    socket_name = "amigopy_single_instance_socket"
    
    # Try to connect to an existing local server
    socket = QLocalSocket()
    socket.connectToServer(socket_name)
    if socket.waitForConnected(500):
        # We connected to an existing instance!
        # Send all command line arguments (each path on a new line)
        paths_str = "\n".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
        socket.write(paths_str.encode('utf-8'))
        socket.flush()
        socket.disconnectFromServer()
        sys.exit(0) # Exit immediately

    # If we get here, we are the primary instance. Start the local server
    server = QLocalServer()
    QLocalServer.removeServer(socket_name)
    server.listen(socket_name)

    # --- Show splash ASAP ---
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
    paths = sys.argv[1:] if len(sys.argv) > 1 else []
    folder_path = paths if len(paths) > 1 else (paths[0] if len(paths) == 1 else None)
    window = MyApp(folder_path)

    # Optional: apply theme after splash is visible
    custom_qss = """
    QSplitter {
        background-color: #19232D;
    }
    QSplitter::handle {
        background-color: #19232D;
        border: none;
    }
    #centralwidget, #im_display_tab, #left_side_container {
        background-color: #19232D;
        border: none;
    }
    """
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6') + custom_qss)
    splash.showMessage("Loading UI…", Qt.AlignBottom | Qt.AlignHCenter | Qt.TextWordWrap, Qt.white)
    app.processEvents()

    window.buffered_paths = []
    window.path_accumulation_timer = QTimer(window)
    window.path_accumulation_timer.setSingleShot(True)

    def process_accumulated_paths():
        paths = list(window.buffered_paths)
        window.buffered_paths.clear()
        if paths:
            # Bring window to front
            window.setWindowState(window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
            window.raise_()
            window.activateWindow()
            # Load all accumulated paths together
            to_load = paths if len(paths) > 1 else paths[0]
            load_all_dcm(window, to_load, progress_callback=None, update_label=None)

    window.path_accumulation_timer.timeout.connect(process_accumulated_paths)

    # Define the slot for incoming connection on the primary instance
    def handle_new_connection():
        client_socket = server.nextPendingConnection()
        if client_socket.waitForReadyRead(1000):
            path_data = client_socket.readAll().data().decode('utf-8').strip()
            if path_data:
                # split by newline to handle multiple files sent at once
                received_paths = [p.strip() for p in path_data.split('\n') if p.strip()]
                if received_paths:
                    # Accumulate paths and restart the debounced timer
                    window.buffered_paths.extend(received_paths)
                    window.path_accumulation_timer.start(500)
        client_socket.disconnectFromServer()

    server.newConnection.connect(handle_new_connection)

    # --- Show window and close splash ---
    # Adjust initial window size and position dynamically to fit within screen available geometry
    screen = app.primaryScreen()
    if screen:
        geom = screen.availableGeometry()
        scr_w = geom.width()
        scr_h = geom.height()
        
        # Default design dimensions are 1713x1122. If screen is smaller, clamp and center.
        if scr_w < 1713 or scr_h < 1122:
            new_w = min(1713, int(scr_w * 0.95))
            new_h = min(1122, int(scr_h * 0.90))
            
            x = geom.x() + (scr_w - new_w) // 2
            y = geom.y() + (scr_h - new_h) // 2
            window.setGeometry(x, y, new_w, new_h)
            
    window.show()
    splash.finish(window)

    # Use the same accumulation timer for startup load so that concurrent launches group together
    if folder_path is not None:
        if isinstance(folder_path, list):
            window.buffered_paths.extend(folder_path)
        else:
            window.buffered_paths.append(folder_path)
        window.path_accumulation_timer.start(500)

    sys.exit(app.exec())



