import numpy as np
from fcn_load.populate_dcm_list import populate_DICOM_tree


def threshSeg(self):
    layer  = int(self.layer_selection_box.currentIndex())
    min_, max_ = self.threshMinSlider.value(), self.threshMaxSlider.value()
    mask_3d = (self.display_seg_data[layer] >= min_) * (self.display_seg_data[layer] <= max_)
    mask_3d = mask_3d.astype(np.uint8)
    
    target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    
    existing_structures = target_series_dict.get('structures', {})
    existing_structure_count = len(existing_structures)
    
    if existing_structure_count == 0:
        target_series_dict['structures'] = {}
        target_series_dict['structures_keys'] = []
        target_series_dict['structures_names'] = []

    current_structure_index = existing_structure_count + 1
        
    name = "tumor"
    # Create a new unique key for the structure clearly:
    new_s_key = f"Structure_{current_structure_index:03d}"

    # target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    target_series_dict['structures'][new_s_key] = {
        'Mask3D': mask_3d,
        'Name': name
    }
    target_series_dict['structures_keys'].append(new_s_key)
    target_series_dict['structures_names'].append(name)
    
    populate_DICOM_tree(self)
    
    
def InitSeg(self):
    layer  = int(self.layer_selection_box.currentIndex())
    mask_3d = np.zeros_like(self.display_seg_data[layer])
    mask_3d = mask_3d.astype(np.uint8)
    
    target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    
    existing_structures = target_series_dict.get('structures', {})
    existing_structure_count = len(existing_structures)
    
    if existing_structure_count == 0:
        target_series_dict['structures'] = {}
        target_series_dict['structures_keys'] = []
        target_series_dict['structures_names'] = []

    current_structure_index = existing_structure_count + 1
    
    if len(self.segStructureName.text()) > 1:
        name = self.segStructureName.text()
    else:
        name = "structure"
        
    if name in target_series_dict['structures_names']:
        new_s_key = target_series_dict['structures_keys'][target_series_dict['structures_names'].index(name)]
    else:
        # Create a new unique key for the structure clearly:
        new_s_key = f"Structure_{current_structure_index:03d}"

    # target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    target_series_dict['structures'][new_s_key] = {
        'Mask3D': mask_3d,
        'Name': name
    }
    target_series_dict['structures_keys'].append(new_s_key)
    target_series_dict['structures_names'].append(name)
    
    populate_DICOM_tree(self)
    

    
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QVBoxLayout

    
def plot_hist(self):
    self.plot_fig = Figure()  # Create a figure for the first time
    ax = self.plot_fig.add_subplot(111) 
    
    if self.selected_background == "Transparent":
        # Set plot background to transparent
        ax.patch.set_alpha(0.0)
        self.plot_fig.patch.set_alpha(0.0)
        
        # Customize text and axes properties
        ax.tick_params(colors='white', labelsize=10)  # White ticks with larger text
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
    
    x_min = self.threshMinSlider.value()
    x_max = self.threshMaxSlider.value()
    
    v, x = np.histogram(self.display_seg_data[0], range=(-1000, 1000), bins=2000)
    
    min_lim = -500; max_lim = 500
    if self.threshMinSlider.value() < -500:
        min_lim = self.threshMinSlider.value() - 100
    if self.threshMaxSlider.value() > 500:
        max_lim = self.threshMaxSlider.value() + 100
    max_counts = (v * (x[:-1] >= min_lim) * (x[:-1] <= max_lim)).max()
    
    ax.plot(x[:-1], v / max_counts, "-")
    ax.axvline(x_min, color="r")
    ax.axvline(x_max, color="r")
    ax.set_xlim(min_lim, max_lim)
    ax.set_ylim(0, 1.1)
    ax.set_xlabel("HU")
    
    # Create a canvas and toolbar
    canvas = FigureCanvas(self.plot_fig)
    canvas.setStyleSheet(f"background-color:{self.selected_background};")

    # Check if the container has a layout, set one if not
    container = self.VTK_SegHistView
    if container.layout() is None:
        layout = QVBoxLayout(container)
        container.setLayout(layout)
    else:
        # Clear existing content in the container, if any
        while container.layout().count():
            child = container.layout().takeAt(0)
            if child.widget() and not isinstance(child.widget(), NavigationToolbar):
                child.widget().deleteLater()

    # Add the canvas and toolbar to the container
    container.layout().addWidget(canvas)
    canvas.draw()
    
    
def on_brush_click(self):
    self.seg_brush = 0 if self.seg_brush == 1 else 1
    if self.seg_brush == 1:
        self.segEraseButton.setChecked(0)
        self.seg_erase = 0  

def on_erase_click(self):
    self.seg_erase = 0 if self.seg_erase == 1 else 1 
    if self.seg_erase == 1:
        self.segBrushButton.setChecked(0) 
        self.seg_brush = 0 

def calc_com(segmentation):
    from scipy.ndimage import center_of_mass
    return center_of_mass(segmentation)


from PyQt5.QtWidgets import (
    QWidget, QCheckBox, QLabel, QPushButton, QHBoxLayout,
    QVBoxLayout, QColorDialog, QDoubleSpinBox, QListWidgetItem,
)


class listWidgetRow(QWidget):
    """
    A custom widget that displays:
      - A checkbox (to toggle the structure on/off),
      - A label (for the structure name),
      - A color-selection button,
      - A 'Line Width' spinbox,
      - A 'Transparency' spinbox,
      - A 'Fill' checkbox (to indicate whether to display a filled polygon).
    """

    def __init__(self, vals, parent=None, checkbox=True):
        super().__init__(parent)

        # 1) Master checkbox to enable/disable the structure
        self.checkbox = QCheckBox()

        # Lay out horizontally
        layout = QHBoxLayout()
        if checkbox:
            layout.addWidget(self.checkbox)
        for val in vals:
            if type(val) == str:
                layout.addWidget(QLabel(val))
            else:
                try:
                    layout.addWidget(QLabel(f"{val:03f}"))
                except:
                    layout.addWidget(QLabel(""))

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


def calcStrucStats(self):
    
    data = {}
    
    for patientID in self.dicom_data:
        print(patientID)
        for studyID in self.dicom_data[patientID]:
            print(studyID)
            for modality in self.dicom_data[patientID][studyID]:
                print(modality)
                for target_series_dict in self.dicom_data[patientID][studyID][modality]:
                    if len(target_series_dict.get('structures', {})) == 0:
                        continue
                    print(target_series_dict)
                    
                    slice_thick = target_series_dict['metadata']['SliceThickness']
                    pixel_spac = target_series_dict['metadata']['PixelSpacing']
                    Im_PatPosition = target_series_dict['metadata']['ImagePositionPatient']
                    
                    for k in target_series_dict['structures']:
                        struct = target_series_dict['structures'][k]
                        name = f"{target_series_dict['SeriesNumber']}_{struct['Name']}"
                        mask = struct["Mask3D"]
                        vol_in_voxels = mask.sum() 
                        vol_in_mm = vol_in_voxels * slice_thick * pixel_spac[0] * pixel_spac[1]
                        CoM = calc_com(mask)
                        data[name] = {"volume": vol_in_mm, "CoM": CoM}
                        
    self.tableSegStrucStats.clear()

    list_item = QListWidgetItem(self.tableSegStrucStats)
    custom_item = listWidgetRow(["Export", "Name", "Volume (mm^3)",
                                 "CoM (x)", "CoM (y)", "CoM (z)"], checkbox=False)
    
    custom_item.structure_key = name  # Save the key for later lookup
    list_item.setSizeHint(custom_item.sizeHint())
    self.tableSegStrucStats.addItem(list_item)
    self.tableSegStrucStats.setItemWidget(list_item, custom_item)
    
    for name in data:
        
        list_item = QListWidgetItem(self.tableSegStrucStats)
        custom_item = listWidgetRow([name, data[name]["volume"], data[name]["CoM"][0],
                                     data[name]["CoM"][1], data[name]["CoM"][2]])
        
        custom_item.structure_key = name  # Save the key for later lookup
        list_item.setSizeHint(custom_item.sizeHint())
        self.tableSegStrucStats.addItem(list_item)
        self.tableSegStrucStats.setItemWidget(list_item, custom_item)
