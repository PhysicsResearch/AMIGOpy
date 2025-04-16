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
    
    x_min = self.threshMinSlider.value()
    x_max = self.threshMaxSlider.value()
    
    v, x = np.histogram(self.display_seg_data[0], range=(-500, 500), bins=1000)
    ax.plot(x[:-1], v, "-")
    ax.axvline(x_min, color="r")
    ax.axvline(x_max, color="r")
    
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
        