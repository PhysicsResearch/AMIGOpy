from PyQt5.QtWidgets import QMenuBar, QAction, QActionGroup
from fcn_load.read_IrIS import load_IrIS_folder
from fcn_load.load_dcm  import load_all_dcm
from fcn_display.win_level import window_auto, window_custom, window_stissue, window_lung, window_bone, window_sprred, window_zeff, window_IrIS_1, window_IrIS_2, window_IrIS_3, window_IrIS_4
from fcn_display.colormap_set import set_color_map_gray, set_color_map_bone, set_color_map_hot, set_color_map_coolwarm, set_color_map_cold, set_color_map_jet, set_color_map_viridis, set_color_map_rainbow
from fcn_export.export_fcn import export_np_array, export_dw_np, export_dcm_np_array
from fcn_processing.split_dcm_series import shift_and_split_3D_matrix

def initializeMenuBar(self):
    # Create a menu bar
    menu_bar = QMenuBar(self)
    self.setMenuBar(menu_bar)
    fileMenu = self.menuBar().addMenu("File")
    openMenu = fileMenu.addMenu("Open")
    # Add items 
    items = ["DICOM", "NIfTI", "Tiff", "EGSPhant","IrIS", "MCNPinp", "MCNPout"]
    for item in items:
        action = QAction(item, self)
        # Connect the Folder action to the load_dcm function
        if item == "DICOM":
            action.triggered.connect(lambda: load_all_dcm(self,folder_path=None, progress_callback=None, update_label=None))
            action.setShortcut("Ctrl+D")
        if item == "IrIS":
            action.triggered.connect(lambda: load_IrIS_folder(self))
            action.setShortcut("Ctrl+I")
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
    # fontSizes = [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40]
    for size in fontSizes:
        action = QAction(str(size), self, checkable=True)
        if size == self.selected_font_size:
            action.setChecked(True)
        action.triggered.connect(lambda checked, s=size: set_legend_font_size(self,s))
        lg_fontSizeMenu.addAction(action)
        lg_fontSizeGroup.addAction(action)
    
    
        
def set_font_size(self, size):
    self.selected_font_size = int(size)

def set_legend_font_size(self, size):
    self.selected_legend_font_size = int(size)

def set_background(self, background):
    self.selected_background    = background
    
def set_legend_on_off(self, legend):
    self.selected_legend_on_off = legend