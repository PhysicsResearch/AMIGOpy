import numpy as np
from PyQt5.QtWidgets import QVBoxLayout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from fcn_display.win_level import set_window

def set_vtk_histogran_fig(self): 
    idx = self.layer_selection_box.currentIndex()
    # 
    if self.DataType == "IrIS":
        if self.display_data[idx].ndim==2:
            data = self.display_data[idx].flatten()
        else:     
            data = self.display_data[idx][self.current_axial_slice_index[idx], :, :].flatten()
        Window = np.std(data)*3
        Level  = np.mean(data)
        set_window(self,Window,Level)  
    else:
        data = self.display_data[idx].flatten()  # Use your actual data source here
    # Plotting
    self.fig_Hist_01, self.ax_Hist_01 = plt.subplots()
    # Make the background of the figure transparent
    self.fig_Hist_01.patch.set_facecolor('none')
    self.fig_Hist_01.patch.set_alpha(0)
    self.ax_Hist_01.set_facecolor('none')
    # Plotting the histogram with the calculated data
    self.ax_Hist_01.hist(data, bins=500, density=None, weights=None)  # Adjust parameters as needed
    # Set axes and labels color to blue
    self.ax_Hist_01.tick_params(axis='both', which='major', labelsize=14, colors='white')
    
    # Embed the plot in the Qt interface
    self.canvas_Hist_01 = FigureCanvas(self.fig_Hist_01)
    self.canvas_Hist_01.setStyleSheet("background-color:transparent;")
    toolbar = NavigationToolbar(self.canvas_Hist_01, self)  # Adjust as necessary
    
    # Check if hist_container_01 has a layout, set one if not
    if self.hist_container_01.layout() is None:
        layout = QVBoxLayout(self.hist_container_01)
        self.hist_container_01.setLayout(layout)
    else:
        # Clear existing content in hist_container_01, if any
        while self.hist_container_01.layout().count():
            child = self.hist_container_01.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    # Add the canvas and toolbar to hist_container_01
    self.hist_container_01.layout().addWidget(toolbar)
    self.hist_container_01.layout().addWidget(self.canvas_Hist_01)
    self.canvas_Hist_01.draw()
    
