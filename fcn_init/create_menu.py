from PyQt5.QtWidgets import QMenuBar, QAction, QActionGroup
from PyQt5.QtGui import QFont
from fcn_load.read_IrIS import load_IrIS_folder
from fcn_load.load_dcm  import load_all_dcm
from fcn_load.save_load import load_amigo_bundle, save_amigo_bundle
from fcn_display.win_level import window_auto, window_custom, window_stissue, window_lung, window_bone, window_sprred, window_zeff, window_IrIS_1, window_IrIS_2, window_IrIS_3, window_IrIS_4
from fcn_display.colormap_set import set_color_map_gray, set_color_map_bone, set_color_map_hot, set_color_map_coolwarm, set_color_map_cold, set_color_map_jet, set_color_map_viridis, set_color_map_rainbow
from fcn_export.export_fcn import export_np_array, export_dw_np, export_dcm_np_array
from fcn_processing.split_dcm_series import shift_and_split_3D_matrix
from fcn_3Dprint.split_gcode_file import  split_gcode
from fcn_DECT.calculateVMIs import calculate_VMI
from fcn_load.load_STL import load_stl_files
from fcn_load.load_OBJ import load_obj_files
from fcn_load.load_nifti import load_nifti_files


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
    items = ["DICOM", "NIfTI","AMIGOpy","STL","Obj","3mf", "Tiff", "EGSPhant","IrIS", "MCNPinp", "MCNPout"]
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
        if item == "STL":
            action.triggered.connect(lambda: load_stl_files(self))
            action.setShortcut("Ctrl+S")    
        if item == "Obj":
            action.triggered.connect(lambda: load_obj_files(self))
            action.setShortcut("Ctrl+O")    
        if item == "3mf":
            action.triggered.connect(lambda: load_3mf(self))
            action.setShortcut("Ctrl+3+D")    
        if item == "NIfTI":
            action.triggered.connect(lambda: load_nifti_files(self))
            action.setShortcut("Ctrl+N")    
        openMenu.addAction(action)

    ViewMenu      = self.menuBar().addMenu("View")
    WindowingMenu = ViewMenu .addMenu("Window")
    # Add items 
    items = ["Auto","Lung", "SoftTissue", "Bone", "SPR/RED", "Zeff", "IrIS_2000","IrIS_5000","IrIS_10000","IrIS_20000","Custom"]
    for item in items:
        action = QAction(item, self)
        # Connect the Folder action to the load_dcm function
        if item == "Auto":
              action.triggered.connect(lambda: window_auto(self))
              action.setShortcut("Ctrl+Shift+1")
        elif item == "Lung":
              action.triggered.connect(lambda: window_lung(self))
              action.setShortcut("Ctrl+1")
        elif item == "SoftTissue":
              action.triggered.connect(lambda: window_stissue(self))
              action.setShortcut("Ctrl+2")
        elif item == "Bone":
              action.triggered.connect(lambda: window_bone(self))
              action.setShortcut("Ctrl+3")
        elif item == "SPR/RED":
              action.triggered.connect(lambda: window_sprred(self))
              action.setShortcut("Ctrl+4")
        elif item == "Zeff":
              action.triggered.connect(lambda: window_zeff(self))
              action.setShortcut("Ctrl+5")
        elif item == "IrIS_2000":
              action.triggered.connect(lambda: window_IrIS_1(self))
              action.setShortcut("Ctrl+6") 
        elif item == "IrIS_5000":
              action.triggered.connect(lambda: window_IrIS_2(self))
              action.setShortcut("Ctrl+7") 
        elif item == "IrIS_10000":          
              action.triggered.connect(lambda: window_IrIS_3(self))
              action.setShortcut("Ctrl+8") 
        elif item == "IrIS_20000":          
              action.triggered.connect(lambda: window_IrIS_4(self))
              action.setShortcut("Ctrl+9")  
        elif item == "Custom":
              action.triggered.connect(lambda: window_custom(self))
              action.setShortcut("Ctrl+0")       
        WindowingMenu.addAction(action)
        
        
    CmapMenu = ViewMenu.addMenu("Color")
    # Add items 
    items = ["Gray","Bone","Hot","Cold","Jet","Viridis","CoolWarm","Rainbow"]
    for item in items:
        action = QAction(item, self)
        # Connect the Folder action to the load_dcm function
        if item == "Gray":
             action.triggered.connect(lambda: set_color_map_gray(self))
             action.setShortcut("Ctrl+c+1")
        elif item == "Bone":
             action.triggered.connect(lambda: set_color_map_bone(self))
             action.setShortcut("Ctrl+c+1")
        elif item == "Hot":
             action.triggered.connect(lambda: set_color_map_hot(self))
             action.setShortcut("Ctrl+c+2")
        elif item == "Cold":
             action.triggered.connect(lambda: set_color_map_cold(self))
             action.setShortcut("Ctrl+c+3")
        elif item == "Jet":
             action.triggered.connect(lambda: set_color_map_jet(self))
             action.setShortcut("Ctrl+c+4")
        elif item == "Viridis":
             action.triggered.connect(lambda: set_color_map_viridis(self))
             action.setShortcut("Ctrl+c+5")
        elif item == "CoolWarm":
             action.triggered.connect(lambda: set_color_map_coolwarm(self))
             action.setShortcut("Ctrl+c+6") 
        elif item == "Rainbow":
             action.triggered.connect(lambda: set_color_map_rainbow(self))
             action.setShortcut("Ctrl+c+7")    
        CmapMenu.addAction(action)    
        
           

    ToolsMenu = self.menuBar().addMenu("Tools")
    SortMenu = ToolsMenu.addMenu("Sort")
    # Add items 
    items = ["DICOM_Folder"]
    for item in items:
        action = QAction(item, self)
        # Connect the Folder action to the load_dcm function
        if item == "DICOM_Folder":
            action.triggered.connect(self.organize_dcm_folder)
        SortMenu.addAction(action)
    
    SeriesMenu = ToolsMenu.addMenu("Series")
    # Add items 
    items = ["Split"]
    for item in items:
        action = QAction(item, self)
        # Connect the Folder action to the load_dcm function
        if item == "Split":
            action.triggered.connect(lambda: shift_and_split_3D_matrix(self))
        SeriesMenu.addAction(action)
    
    # Add items 
    items = ["Create_VMI"]
    for item in items:
        action = QAction(item, self)
        # Connect the Folder action to the load_dcm function
        if item == "Create_VMI":
            action.triggered.connect(lambda: calculate_VMI(self))
        SeriesMenu.addAction(action)
        

  
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
    
    # Figures
    self.selected_font_size = 14
    self.selected_legend_font_size = 14
    self.selected_legend_on_off = "On"
    self.selected_background = "Transparent"
    self.selected_line_width = 2.0
    self.selected_line_color = "Red" 
    self.selected_point_size = 8
    self.selected_point_color = "Blue"

    styleMenu = self.menuBar().addMenu("Figures")

    # Font Size submenu
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

    # Background submenu
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
        
    # Legend on/off submenu
    legendMenu = styleMenu.addMenu("Legend")
    legendGroup = QActionGroup(self)
    legends = ["On", "Off"]
    for lg in legends:
        action = QAction(lg, self, checkable=True)
        if lg == "On":
            action.setChecked(True)
        action.triggered.connect(lambda checked, l=lg: set_legend_on_off(self,l))
        legendMenu.addAction(action)
        legendGroup.addAction(action)
    
    # Font Size LEgend submenu
    lg_fontSizeMenu = styleMenu.addMenu("Font Size Legend")
    lg_fontSizeGroup = QActionGroup(self)
    fontSizes = [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40]
    for size in fontSizes:
        action = QAction(str(size), self, checkable=True)
        if size == self.selected_font_size:
            action.setChecked(True)
        action.triggered.connect(lambda checked, s=size: set_legend_font_size(self,s))
        lg_fontSizeMenu.addAction(action)
        lg_fontSizeGroup.addAction(action)

    # Line Width submenu
    lg_lineWidthMenu = styleMenu.addMenu("Line Width")
    lg_lineWidth     = QActionGroup(self)
    lineWidth        = [0.5, 1, 2, 3, 4, 5, 6]
    for size in lineWidth :
        action = QAction(str(size), self, checkable=True)
        if size == self.selected_line_width:
            action.setChecked(True)
        action.triggered.connect(lambda checked, s=size: set_line_width(self,s))
        lg_lineWidthMenu.addAction(action)
        lg_lineWidth.addAction(action)

    # Line Color submenu
    lg_lineColorMenu = styleMenu.addMenu("Line Color")
    lg_lineColor     = QActionGroup(self)
    lineColors       = ["blue","black","green","red","white"]
    for color in lineColors :
        action = QAction(str(color), self, checkable=True)
        if color == self.selected_line_color:
            action.setChecked(True)
        action.triggered.connect(lambda checked, s=color: set_line_color(self,s))
        lg_lineColorMenu.addAction(action)
        lg_lineColor.addAction(action)



    # Point size submenu
    lg_psizetMenu = styleMenu.addMenu("Point size")
    lg_psize     = QActionGroup(self)
    psize        = [2, 4, 6, 8, 10, 15, 20]
    for size in psize :
        action = QAction(str(size), self, checkable=True)
        if size == self.selected_point_size:
            action.setChecked(True)
        action.triggered.connect(lambda checked, s=size: set_psize(self,s))
        lg_psizetMenu.addAction(action)
        lg_psize.addAction(action)

    # Point Color submenu
    lg_pColorMenu = styleMenu.addMenu("Point Color")
    lg_pColor     = QActionGroup(self)
    lineColors       = ["blue","black","green","red","white"]
    for color in lineColors :
        action = QAction(str(color), self, checkable=True)
        if color == self.selected_point_color:
            action.setChecked(True)
        action.triggered.connect(lambda checked, s=color: set_point_color(self,s))
        lg_pColorMenu.addAction(action)
        lg_pColor.addAction(action)

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


        
def set_font_size(self, size):
    self.selected_font_size = int(size)

def set_legend_font_size(self, size):
    self.selected_legend_font_size = int(size)

def set_background(self, background):
    self.selected_background    = background
    
def set_legend_on_off(self, legend):
    self.selected_legend_on_off = legend

def set_line_width(self, size):
    self.selected_line_width = float(size)

def set_line_color(self, color):
    self.selected_line_color = color

def set_psize(self, size):
    self.selected_point_size = int(size)

def set_p_color(self, color):
    self.selected_point_color = color

def set_point_color(self, color):
    self.selected_point_color = color


def apply_font_recursively(menu: QMenuBar, font: QFont):
    menu.setFont(font)
    for act in menu.actions():
        sub = act.menu()
        if sub is not None:
            apply_font_recursively(sub, font)