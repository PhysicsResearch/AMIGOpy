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
        'Name': "tumors"
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
