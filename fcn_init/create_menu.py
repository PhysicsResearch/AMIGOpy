from PySide6.QtWidgets import QMenuBar
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtGui import QFont
from fcn_operations.operations_dialog import open_operations_dialog
from fcn_reg.registration_dialog import open_registration_dialog

from fcn_load.read_IrIS import load_IrIS_folder
from fcn_load.load_dcm  import load_all_dcm
from fcn_load.save_load import load_amigo_bundle, save_amigo_bundle
from fcn_display.win_level import window_auto, window_custom, window_stissue, window_lung, window_bone, window_sprred, window_zeff, window_IrIS_1, window_IrIS_2, window_IrIS_3, window_IrIS_4
from fcn_display.colormap_set import set_color_map_gray, set_color_map_bone, set_color_map_hot, set_color_map_coolwarm, set_color_map_cold, set_color_map_jet, set_color_map_viridis, set_color_map_rainbow, set_color_map_magma, set_color_map_cividis, set_color_map_red, set_color_map_green, set_color_map_blue
from fcn_export.export_fcn import export_np_array, export_dw_np, export_dcm_np_array
from fcn_processing.split_dcm_series import shift_and_split_3D_matrix
from fcn_3Dprint.split_gcode_file import  split_gcode
from fcn_DECT.calculateVMIs import calculate_VMI
from fcn_load.load_STL import load_stl_files
from fcn_load.load_OBJ import load_obj_files
from fcn_load.load_nifti import load_nifti_files
from fcn_load.load_mha import load_mha_files
from fcn_load.load_npy import load_npy_files
from fcn_load.load_tiff_similar import load_tiff_files, load_png_files, load_jpeg_files, load_bmp_files  
from fcn_autocont.segmentator_calls import open_segmentator_tab
from functools import partial
from fcn_init.create_3D_database_tab import export_3dp_database_action, import_3dp_database_action, restore_3dp_database_action


def initializeMenuBar(self):
    # define fontsize
    f = QFont()
    f.setPointSize(11)  
    # Create a menu bar
    menu_bar = QMenuBar(self)
    menu_bar.setFont(f)
    self.setMenuBar(menu_bar)
    fileMenu = self.menuBar().addMenu("File")
    # ------------------------------------------------------------
    # save
    # -------------------------------------------------------------
    saveAction = QAction("Save", self)
    saveAction.setShortcut("Ctrl+S")          # Ctrl+S on all platforms
    saveAction.triggered.connect(lambda: save_amigo_bundle(self))
    fileMenu.addAction(saveAction)                     # temporarily add; we’ll reposition later
    # -----------------------------------------------------------------------
    # open
    openMenu = fileMenu.addMenu("Open")
    # Add items 
    items = ["DICOM", "NIfTI","AMIGOpy","MHA","npy","STL","Obj","3mf", "Tiff", "EGSPhant","IrIS", "MCNPinp", "MCNPout"]
    for item in items:
        action = QAction(item, self)
        # Connect the Folder action to the load_dcm function
        if item == "DICOM":
            action.triggered.connect(lambda: load_all_dcm(self,folder_path=None, progress_callback=None, update_label=None))
            action.setShortcut("Ctrl+D")
        if item == "IrIS":
            action.triggered.connect(lambda: load_IrIS_folder(self))
            action.setShortcut("Ctrl+I")
        if item == "AMIGOpy":
            action.triggered.connect(lambda: load_amigo_bundle(self))
            action.setShortcut("Ctrl+A") 
        if item == "MHA":
            action.triggered.connect(lambda: load_mha_files(self))
        if item == "npy":
            action.triggered.connect(lambda: load_npy_files(self))
        if item == "STL":
            action.triggered.connect(lambda: load_stl_files(self)) 
        if item == "Obj":
            action.triggered.connect(lambda: load_obj_files(self))  
        if item == "3mf":
            action.triggered.connect(lambda: load_3mf(self)) 
        if item == "NIfTI":
            action.triggered.connect(lambda: load_nifti_files(self))
            action.setShortcut("Ctrl+N")    
        if item == "Tiff":
            action.triggered.connect(lambda: load_tiff_files(self))
        openMenu.addAction(action)
        
    importMenu = fileMenu.addMenu("Import")
    import_3dp_action = QAction("3DP Database", self)
    import_3dp_action.triggered.connect(lambda: import_3dp_database_action(self))
    importMenu.addAction(import_3dp_action)

    ViewMenu      = self.menuBar().addMenu("View")
    WindowingMenu = ViewMenu .addMenu("Window")
    # Add items 
    items = ["Lung", "SoftTissue", "Bone", "SPR/RED", "Zeff", "IrIS_2000","IrIS_5000","IrIS_10000","IrIS_20000","Custom"]
    for item in items:
        action = QAction(item, self)
        if item == "Lung":
              action.triggered.connect(lambda: window_lung(self))
              action.setShortcut("Ctrl+W, 1")
        elif item == "SoftTissue":
              action.triggered.connect(lambda: window_stissue(self))
              action.setShortcut("Ctrl+W, 2")
        elif item == "Bone":
              action.triggered.connect(lambda: window_bone(self))
              action.setShortcut("Ctrl+W, 3")
        elif item == "SPR/RED":
              action.triggered.connect(lambda: window_sprred(self))
              action.setShortcut("Ctrl+W, 4")
        elif item == "Zeff":
              action.triggered.connect(lambda: window_zeff(self))
              action.setShortcut("Ctrl+W, 5")
        elif item == "IrIS_2000":
              action.triggered.connect(lambda: window_IrIS_1(self))
              action.setShortcut("Ctrl+W, 6") 
        elif item == "IrIS_5000":
              action.triggered.connect(lambda: window_IrIS_2(self))
              action.setShortcut("Ctrl+W, 7") 
        elif item == "IrIS_10000":          
              action.triggered.connect(lambda: window_IrIS_3(self))
              action.setShortcut("Ctrl+W, 8") 
        elif item == "IrIS_20000":          
              action.triggered.connect(lambda: window_IrIS_4(self))
              action.setShortcut("Ctrl+W, 9")  
        elif item == "Custom":
              action.triggered.connect(lambda: window_custom(self))
              action.setShortcut("Ctrl+W, 0")       
        WindowingMenu.addAction(action)
        
        
    CmapMenu = ViewMenu.addMenu("Color")
    # Add items 
    # Add items 
    items = ["Gray","Bone","Hot","Cold","Jet","Viridis","CoolWarm","Rainbow","Magma","Cividis","Red","Green","Blue"]
    for item in items:
        action = QAction(item, self)
        if item == "Gray":
             action.triggered.connect(lambda: set_color_map_gray(self))
             action.setShortcut("Ctrl+C, 1")
        elif item == "Bone":
             action.triggered.connect(lambda: set_color_map_bone(self))
             action.setShortcut("Ctrl+C, 2")
        elif item == "Hot":
             action.triggered.connect(lambda: set_color_map_hot(self))
             action.setShortcut("Ctrl+C, 3")
        elif item == "Cold":
             action.triggered.connect(lambda: set_color_map_cold(self))
             action.setShortcut("Ctrl+C, 4")
        elif item == "Jet":
             action.triggered.connect(lambda: set_color_map_jet(self))
             action.setShortcut("Ctrl+C, 5")
        elif item == "Viridis":
             action.triggered.connect(lambda: set_color_map_viridis(self))
             action.setShortcut("Ctrl+C, 6")
        elif item == "CoolWarm":
             action.triggered.connect(lambda: set_color_map_coolwarm(self))
             action.setShortcut("Ctrl+C, 7") 
        elif item == "Rainbow":
             action.triggered.connect(lambda: set_color_map_rainbow(self))
             action.setShortcut("Ctrl+C, 8")    
        elif item == "Magma":
             action.triggered.connect(lambda: set_color_map_magma(self))
             action.setShortcut("Ctrl+C, 9")    
        elif item == "Cividis":
             action.triggered.connect(lambda: set_color_map_cividis(self))
             action.setShortcut("Ctrl+C, 0")    
        elif item == "Red":
             action.triggered.connect(lambda: set_color_map_red(self))
             action.setShortcut("Ctrl+R")
        elif item == "Green":
             action.triggered.connect(lambda: set_color_map_green(self))
             action.setShortcut("Ctrl+G")
        elif item == "Blue":
             action.triggered.connect(lambda: set_color_map_blue(self))
             action.setShortcut("Ctrl+B")
        CmapMenu.addAction(action)    
        
           

    ToolsMenu = self.menuBar().addMenu("Tools")
    # Add items 
    dcm_fold_action = QAction("Sort DCM Folder", self)
    dcm_fold_action.triggered.connect(self.organize_dcm_folder)
    ToolsMenu.addAction(dcm_fold_action)
    
    # Add items 
    split_series_action = QAction("Split Series", self)
    split_series_action.triggered.connect(lambda: shift_and_split_3D_matrix(self))
    ToolsMenu.addAction(split_series_action)
    
    vmi_action = QAction("Calculate VMI", self)
    vmi_action.triggered.connect(lambda: calculate_VMI(self))
    ToolsMenu.addAction(vmi_action)
        
    # Add operations dialog entry
    operations_action = QAction("Operations…", self)
    operations_action.triggered.connect(lambda: open_operations_dialog(self))
    ToolsMenu.addAction(operations_action)
    
    # 3DP submenu
    tdp_menu = ToolsMenu.addMenu("3DP")
    restore_3dp_action = QAction("Restore Database…", self)
    restore_3dp_action.triggered.connect(lambda: restore_3dp_database_action(self))
    tdp_menu.addAction(restore_3dp_action)

    # ── Auto-Contouring menu ──
    AutoContMenu = self.menuBar().addMenu("Auto-Contouring")

    total_seg_action = QAction("TotalSegmentator…", self)
    total_seg_action.triggered.connect(partial(open_segmentator_tab, self))
    AutoContMenu.addAction(total_seg_action)

    # ── Registration menu ──
    RegMenu = self.menuBar().addMenu("Registration")

    reg_dialog_action = QAction("Image Registration…", self)
    reg_dialog_action.setShortcut("Ctrl+Shift+R")
    reg_dialog_action.triggered.connect(lambda: open_registration_dialog(self))
    RegMenu.addAction(reg_dialog_action)

    ExportMenu = self.menuBar().addMenu("Export")
    TypeMenu = ExportMenu.addMenu("IrIS")
    # Add items 
    items = ["Current","Frames2Dw"]
    for item in items:
        action = QAction(item, self)
        # Connect the Folder action to the load_dcm function
        if item == "Current":
            action.triggered.connect(lambda: export_np_array(self))
        elif item == "Frames2Dw":
            action.triggered.connect(lambda: export_dw_np(self))
            
        TypeMenu.addAction(action)
        
    TypeMenu = ExportMenu.addMenu("DICOM")
    # Add items 
    items = ["Current","All"]
    for item in items:
        action = QAction(item, self)
        # Connect the Folder action to the load_dcm function
        if item == "Current":
            action.triggered.connect(lambda: export_dcm_np_array(self))
        elif item == "All":
            action.triggered.connect(lambda: export_dw_np(self))
            
        TypeMenu.addAction(action)
        
    export_3dp_action = QAction("3DP Database", self)
    export_3dp_action.triggered.connect(lambda: export_3dp_database_action(self))
    ExportMenu.addAction(export_3dp_action)
    
    # Figures
    self.selected_font_size = 14
    self.selected_legend_font_size = 14
    self.selected_legend_on_off = "On"
    self.selected_background = "Transparent"
    self.selected_line_width = 2.0
    self.selected_line_color = "Red" 
    self.selected_point_size = 8
    self.selected_point_color = "Blue"
    self.selected_line_style = "Solid"
    self.selected_marker_type = "Circle"

    # Colorbar scale layout state
    self.scale_pos_x = 0.91
    self.scale_pos_y = 0.15
    self.scale_width = 0.06
    self.scale_height = 0.7

    styleMenu = self.menuBar().addMenu("Figures")

    # 1. Background submenu
    backgroundMenu = styleMenu.addMenu("Background")
    backgroundGroup = QActionGroup(self)
    backgrounds = ["Transparent", "White"]
    for bg in backgrounds:
        action = QAction(bg, self, checkable=True)
        if bg == self.selected_background:
            action.setChecked(True)
        action.triggered.connect(lambda checked, b=bg: set_background(self,b))
        backgroundMenu.addAction(action)
        backgroundGroup.addAction(action)

    # 2. Font Size submenu
    fontSizeMenu = styleMenu.addMenu("Font Size")
    fontSizeGroup = QActionGroup(self)
    fontSizes = [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40]
    for size in fontSizes:
        action = QAction(str(size), self, checkable=True)
        if size == self.selected_font_size:
            action.setChecked(True)
        action.triggered.connect(lambda checked, s=size: set_font_size(self,s))
        fontSizeMenu.addAction(action)
        fontSizeGroup.addAction(action)

    # 3. Font Size Legend submenu
    lg_fontSizeMenu = styleMenu.addMenu("Font Size Legend")
    lg_fontSizeGroup = QActionGroup(self)
    fontSizes = [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40]
    for size in fontSizes:
        action = QAction(str(size), self, checkable=True)
        if size == self.selected_legend_font_size:
            action.setChecked(True)
        action.triggered.connect(lambda checked, s=size: set_legend_font_size(self,s))
        lg_fontSizeMenu.addAction(action)
        lg_fontSizeGroup.addAction(action)

    # 4. Legend on/off submenu
    legendMenu = styleMenu.addMenu("Legend")
    legendGroup = QActionGroup(self)
    legends = ["On", "Off"]
    for lg in legends:
        action = QAction(lg, self, checkable=True)
        if lg == self.selected_legend_on_off:
            action.setChecked(True)
        action.triggered.connect(lambda checked, l=lg: set_legend_on_off(self,l))
        legendMenu.addAction(action)
        legendGroup.addAction(action)

    # 5. Line Color submenu
    lg_lineColorMenu = styleMenu.addMenu("Line Color")
    lg_lineColor     = QActionGroup(self)
    lineColors       = ["blue", "black", "green", "red", "white"]
    for color in lineColors:
        action = QAction(color, self, checkable=True)
        if color.lower() == self.selected_line_color.lower():
            action.setChecked(True)
        action.triggered.connect(lambda checked, s=color: set_line_color(self,s))
        lg_lineColorMenu.addAction(action)
        lg_lineColor.addAction(action)

    # 6. Line Style submenu
    lineStyleMenu = styleMenu.addMenu("Line Style")
    lineStyleGroup = QActionGroup(self)
    lineStyles = ["Solid", "Dashed", "Dotted", "Dash-Dot", "None"]
    for style in lineStyles:
        action = QAction(style, self, checkable=True)
        if style.lower() == self.selected_line_style.lower():
            action.setChecked(True)
        action.triggered.connect(lambda checked, s=style: set_line_style(self,s))
        lineStyleMenu.addAction(action)
        lineStyleGroup.addAction(action)

    # 7. Line Width submenu
    lg_lineWidthMenu = styleMenu.addMenu("Line Width")
    lg_lineWidth     = QActionGroup(self)
    lineWidth        = [0.5, 1, 2, 3, 4, 5, 6]
    for size in lineWidth:
        action = QAction(str(size), self, checkable=True)
        if size == self.selected_line_width:
            action.setChecked(True)
        action.triggered.connect(lambda checked, s=size: set_line_width(self,s))
        lg_lineWidthMenu.addAction(action)
        lg_lineWidth.addAction(action)

    # 8. Marker Type submenu
    markerTypeMenu = styleMenu.addMenu("Marker Type")
    markerTypeGroup = QActionGroup(self)
    markerTypes = ["Circle", "Square", "Triangle", "Star", "None"]
    for mtype in markerTypes:
        action = QAction(mtype, self, checkable=True)
        if mtype.lower() == self.selected_marker_type.lower():
            action.setChecked(True)
        action.triggered.connect(lambda checked, m=mtype: set_marker_type(self,m))
        markerTypeMenu.addAction(action)
        markerTypeGroup.addAction(action)

    # 9. Point Color submenu
    lg_pColorMenu = styleMenu.addMenu("Point Color")
    lg_pColor     = QActionGroup(self)
    lineColors       = ["blue", "black", "green", "red", "white"]
    for color in lineColors:
        action = QAction(color, self, checkable=True)
        if color.lower() == self.selected_point_color.lower():
            action.setChecked(True)
        action.triggered.connect(lambda checked, s=color: set_point_color(self,s))
        lg_pColorMenu.addAction(action)
        lg_pColor.addAction(action)

    # 10. Point size submenu
    lg_psizetMenu = styleMenu.addMenu("Point size")
    lg_psize     = QActionGroup(self)
    psize        = [2, 4, 6, 8, 10, 15, 20]
    for size in psize:
        action = QAction(str(size), self, checkable=True)
        if size == self.selected_point_size:
            action.setChecked(True)
        action.triggered.connect(lambda checked, s=size: set_psize(self,s))
        lg_psizetMenu.addAction(action)
        lg_psize.addAction(action)

    # 11. Scale Settings submenu
    scaleSettingsMenu = styleMenu.addMenu("Scale Settings")
    
    # Toggle to enable/disable scale
    scale_action = QAction("Show Intensity Scale", self, checkable=True)
    scale_action.setChecked(False)
    self.show_intensity_scale = False

    def toggle_scale(checked):
        self.show_intensity_scale = checked
        idx = self.layer_selected.currentIndex() if hasattr(self, 'layer_selected') else 0
        has_data = hasattr(self, 'display_data') and self.display_data.get(idx) is not None
        
        if has_data:
            from fcn_display.colormap_set import set_color_map
            set_color_map(self)
        else:
            actors = ['scalarBarActorAxial', 'scalarBarActorSagittal', 'scalarBarActorCoronal']
            widgets = ['vtkWidgetAxial', 'vtkWidgetSagittal', 'vtkWidgetCoronal']
            for act_name, widget_name in zip(actors, widgets):
                if hasattr(self, act_name):
                    actor = getattr(self, act_name)
                    actor.SetVisibility(checked)
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    widget.GetRenderWindow().Render()

    scale_action.triggered.connect(toggle_scale)
    scaleSettingsMenu.addAction(scale_action)
    scaleSettingsMenu.addSeparator()
        
    # Scale Position Presets
    scalePosMenu = scaleSettingsMenu.addMenu("Position Preset")
    scalePosGroup = QActionGroup(self)
    
    presets = [
        ("Right (Vertical)", 0.91, 0.15, 0.06, 0.7),
        ("Left (Vertical)", 0.02, 0.15, 0.06, 0.7),
        ("Top (Horizontal)", 0.15, 0.90, 0.7, 0.06),
        ("Bottom (Horizontal)", 0.15, 0.05, 0.7, 0.06),
    ]
    for label, x, y, w, h in presets:
        action = QAction(label, self, checkable=True)
        if label.startswith("Right"):
            action.setChecked(True)
        action.triggered.connect(lambda checked, px=x, py=y, pw=w, ph=h: apply_scale_preset(self, px, py, pw, ph))
        scalePosMenu.addAction(action)
        scalePosGroup.addAction(action)
        
    # Custom Adjust Position dialog trigger
    adjustPosAction = QAction("Adjust Position...", self)
    adjustPosAction.triggered.connect(lambda: open_scale_position_dialog(self))
    scaleSettingsMenu.addAction(adjustPosAction)

    # Layout menu
    # intended to adjust the view
    #
    styleMenu = self.menuBar().addMenu("Layout")
    # Gcode submenu
    ViewMenu = styleMenu.addMenu("View_Tab")
    ViewGroup = QActionGroup(self)
    # Add items 
    items = ["All","Axial", "Sagittal", "Coronal"]
    for item in items:
        action = QAction(item, self)
        # Connect the Folder action to the load_dcm function
        if item == "All":
            action.triggered.connect(lambda: self.set_view_mode("all"))
        elif item == "Axial":
            action.triggered.connect(lambda: self.set_view_mode("axial"))
        elif item == "Sagittal":
            action.triggered.connect(lambda: self.set_view_mode("sagittal"))
        elif item == "Coronal":
            action.triggered.connect(lambda: self.set_view_mode("coronal"))

        ViewMenu.addAction(action)


    
    # adjust font size:
    apply_font_recursively(menu_bar, f)


        
def trigger_mix_graph_update(self):
    if hasattr(self, "update_mix_graph_func"):
        try:
            self.update_mix_graph_func()
        except Exception as e:
            print(f"Error updating mix graph: {e}")

def set_font_size(self, size):
    self.selected_font_size = int(size)
    trigger_mix_graph_update(self)

def set_legend_font_size(self, size):
    self.selected_legend_font_size = int(size)
    if hasattr(self, 'scalarBarActorAxial') or hasattr(self, 'scalarBarActorSagittal') or hasattr(self, 'scalarBarActorCoronal'):
        from fcn_display.colormap_set import set_color_map
        set_color_map(self)
    trigger_mix_graph_update(self)

def set_background(self, background):
    self.selected_background    = background
    trigger_mix_graph_update(self)
    
def set_legend_on_off(self, legend):
    self.selected_legend_on_off = legend
    trigger_mix_graph_update(self)

def set_line_width(self, size):
    self.selected_line_width = float(size)
    trigger_mix_graph_update(self)

def set_line_color(self, color):
    self.selected_line_color = color
    trigger_mix_graph_update(self)

def set_line_style(self, style):
    self.selected_line_style = style
    trigger_mix_graph_update(self)

def set_marker_type(self, mtype):
    self.selected_marker_type = mtype
    trigger_mix_graph_update(self)

def set_psize(self, size):
    self.selected_point_size = int(size)
    trigger_mix_graph_update(self)

def set_p_color(self, color):
    self.selected_point_color = color
    trigger_mix_graph_update(self)

def set_point_color(self, color):
    self.selected_point_color = color
    trigger_mix_graph_update(self)


def apply_font_recursively(menu: QMenuBar, font: QFont):
    menu.setFont(font)
    for act in menu.actions():
        sub = act.menu()
        if sub is not None:
            apply_font_recursively(sub, font)


def apply_scale_preset(self, x, y, w, h):
    self.scale_pos_x = x
    self.scale_pos_y = y
    self.scale_width = w
    self.scale_height = h
    from fcn_display.colormap_set import set_color_map
    set_color_map(self)


def open_scale_position_dialog(self):
    from PySide6.QtWidgets import QDialog, QFormLayout, QDoubleSpinBox, QDialogButtonBox
    
    dialog = QDialog(self)
    dialog.setWindowTitle("Adjust Scale Position")
    layout = QFormLayout(dialog)
    
    x_spin = QDoubleSpinBox()
    x_spin.setRange(0.0, 1.0)
    x_spin.setSingleStep(0.01)
    x_spin.setValue(getattr(self, 'scale_pos_x', 0.91))
    
    y_spin = QDoubleSpinBox()
    y_spin.setRange(0.0, 1.0)
    y_spin.setSingleStep(0.01)
    y_spin.setValue(getattr(self, 'scale_pos_y', 0.15))
    
    w_spin = QDoubleSpinBox()
    w_spin.setRange(0.01, 1.0)
    w_spin.setSingleStep(0.01)
    w_spin.setValue(getattr(self, 'scale_width', 0.06))
    
    h_spin = QDoubleSpinBox()
    h_spin.setRange(0.01, 1.0)
    h_spin.setSingleStep(0.01)
    h_spin.setValue(getattr(self, 'scale_height', 0.7))
    
    layout.addRow("Position X:", x_spin)
    layout.addRow("Position Y:", y_spin)
    layout.addRow("Width:", w_spin)
    layout.addRow("Height:", h_spin)
    
    def update_positions():
        self.scale_pos_x = x_spin.value()
        self.scale_pos_y = y_spin.value()
        self.scale_width = w_spin.value()
        self.scale_height = h_spin.value()
        
        actors = ['scalarBarActorAxial', 'scalarBarActorSagittal', 'scalarBarActorCoronal']
        widgets = ['vtkWidgetAxial', 'vtkWidgetSagittal', 'vtkWidgetCoronal']
        for act_name, widget_name in zip(actors, widgets):
            if hasattr(self, act_name):
                actor = getattr(self, act_name)
                actor.GetPositionCoordinate().SetValue(self.scale_pos_x, self.scale_pos_y)
                actor.SetWidth(self.scale_width)
                actor.SetHeight(self.scale_height)
            if hasattr(self, widget_name):
                widget = getattr(self, widget_name)
                widget.GetRenderWindow().Render()
                
    x_spin.valueChanged.connect(update_positions)
    y_spin.valueChanged.connect(update_positions)
    w_spin.valueChanged.connect(update_positions)
    h_spin.valueChanged.connect(update_positions)
    
    buttons = QDialogButtonBox(QDialogButtonBox.Ok, dialog)
    buttons.accepted.connect(dialog.accept)
    layout.addWidget(buttons)
    
    dialog.exec()