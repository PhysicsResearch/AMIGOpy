import numpy as np
from scipy.optimize import curve_fit
from PyQt5.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

def SPR_copy_ref_columns(self):
    # copy reference data from the material info
    row_count    = self.MatInfoTable.rowCount()
    column_count = self.MatInfoTable.columnCount()

    # Index of the fourth-last column
    fourth_last_column_index = column_count - 3

    # Ensure SPRTable has the same row count as MatInfoTable
    self.tableSPR.setRowCount(row_count)
    self.tableSPR.setColumnCount(5)  # Ensure ZeffTable has 2 columns

    for row in range(row_count):
        # Get data from the first column of MatInfoTable
        first_col_item = self.MatInfoTable.item(row, 0)
        if first_col_item is not None:
            first_col_text = first_col_item.text()
        else:
            first_col_text = ""

        # Get data from the fourth-last column of MatInfoTable
        fourth_last_col_item = self.MatInfoTable.item(row, fourth_last_column_index)
        if fourth_last_col_item is not None:
            fourth_last_col_text = fourth_last_col_item.text()
        else:
            fourth_last_col_text = ""

        # Set data to the first column of SPRTable
        self.tableSPR.setItem(row, 0, QTableWidgetItem(first_col_text))

        # Set data to the second column of SPRTable
        self.tableSPR.setItem(row, 1, QTableWidgetItem(fourth_last_col_text))
        
        

# 
def extract_data_and_fit(self):
    # Get calibration parameters
    
    row_count    = self.tableZeff.rowCount()
    column_count = self.MatInfoTable.columnCount()
    
    I_water      = float(self.Iv_water_ref.value())
    Energy       = self.SPR_ref_energy.value()
    #   
    SPR_cal = []
    SPR_ref = []
    #
    # Initialize a list to store squared percentage errors
    squared_percentage_errors = []
    for row in range(row_count):
        I_item   = self.tableIv.item(row, 2)
        RED_item = self.tableRED.item(row, 2)
        SPR_item = self.tableSPR.item(row, 1)
        
        I     = float(I_item.text()) 
        RED   = float(RED_item.text())
        SPR_r = float(SPR_item.text())   
        SPR_c =  calculate_spr(RED, I, I_water, Energy)
        
        difference = SPR_c - SPR_r
        percentage = difference/SPR_r * 100
        squared_percentage_errors.append(percentage**2)
        self.tableSPR.setItem(row, 2, QTableWidgetItem(f"{SPR_c:.3f}"))
        self.tableSPR.setItem(row, 3, QTableWidgetItem(f"{difference:.3f}"))
        self.tableSPR.setItem(row, 4, QTableWidgetItem(f"{percentage:.2f}%"))
        # Store the values for plotting
        SPR_cal.append(SPR_c)
        SPR_ref.append(SPR_r)
        
    SPR_cal = np.array(SPR_cal)
    SPR_ref = np.array(SPR_ref)
    #
    # Calculate RMSE
    rmse = np.sqrt(np.mean(squared_percentage_errors))      
    self.SPR_RMSE_text.setText(f"{rmse:.4f}")
    #
    
    # Plot reference values vs fitted values
    fig, ax = plt.subplots()
    fig.patch.set_facecolor('none')
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # Scatter plot for reference vs fitted values
    ax.scatter(SPR_ref,SPR_cal, label='Data Points', color='blue')

    # Continuous fit line (diagonal line for perfect fit reference)
    min_val = min(SPR_ref.min(), SPR_cal.min())
    max_val = max(SPR_ref.max(), SPR_cal.max())
    ax.plot([min_val, max_val], [min_val, max_val], label='Perfect Fit Line', color='red', linestyle='--')

    # Customize the plot
    ax.set_xlabel('Reference Values (SPR)', fontsize=14,color='white')
    ax.set_ylabel('Fitted Values (SPR)', fontsize=14,color='white')
    ax.set_title('Reference vs SPR', fontsize=14,color='white')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7)
    ax.legend()

    ax.tick_params(axis='both', which='major', labelsize=14, colors='white')

    container = self.SPR_plot_1
    canvas = FigureCanvas(fig)
    canvas.setStyleSheet("background-color:transparent;")
    toolbar = NavigationToolbar(canvas, self)  # Adjust as necessary

    # Check if the container has a layout, set one if not
    if container.layout() is None:
        layout = QVBoxLayout(container)
        container.setLayout(layout)
    else:
        # Clear existing content in the container, if any
        while container.layout().count():
            child = container.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # Add the canvas and toolbar to the container
    container.layout().addWidget(toolbar)
    container.layout().addWidget(canvas)
    canvas.draw()    

def calculate_beta(energy_mev, rest_mass_mev=938.27):
    """Calculate beta (v/c) for a given energy in MeV."""
    total_energy = energy_mev + rest_mass_mev
    gamma = total_energy / rest_mass_mev
    beta = np.sqrt(1 - 1 / gamma**2)
    return beta

def calculate_spr(rho, I, I_w, energy_mev):
    # Constants
    m_e_c2 = 0.511  # MeV, rest mass energy of electron
    # Calculate beta for given energy
    beta = calculate_beta(energy_mev)
    # eV to MeV
    I_w = I_w/1e6
    I   = I/1e6
    # Calculate constants
    ln_Iw_term = np.log(2 * m_e_c2 * beta**2 / (I_w * (1 - beta**2))) - beta**2
    denominator = ln_Iw_term

    # Calculate the numerator term ln(2m_e c^2 beta^2 / (I(1 - beta^2))) - beta^2
    ln_I_term = np.log(2 * m_e_c2 * beta**2 / (I * (1 - beta**2))) - beta**2
    
    # Calculate the SPR
    numerator = ln_I_term
    SPR_w = rho * (numerator / denominator)
    return SPR_w    
   
def show_error_dialog(self, message):
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setText("Error")
    error_dialog.setInformativeText(message)
    error_dialog.setWindowTitle("Error")
    error_dialog.exec_()       
   
def create_and_embed_plot_SPR_plot_01(self):
    # Extract data from self.tableRED
    row_count = self.tableZeff.rowCount()

    names = []
    ref_values = []
    fit_values = []
    deviations = []

    for row in range(row_count):
        name_item = self.tableSPR.item(row, 0)  # name or line ID is in the first column
        ref_item  = self.tableSPR.item(row, 1)  # ref data is in the second column
        fit_item  = self.tableSPR.item(row, 2)  # fit data is in the third column

        if name_item and ref_item and fit_item:
            names.append(name_item.text())
            ref_value = float(ref_item.text())
            fit_value = float(fit_item.text())
            ref_values.append(ref_value)
            fit_values.append(fit_value)
            deviation = ((fit_value - ref_value) / ref_value) * 100 if ref_value != 0 else 0
            deviations.append(deviation)

    # Convert lists to numpy arrays
    names = np.array(names)
    deviations = np.array(deviations)

    # Create the figure and axis for the plot
    fig, ax = plt.subplots(figsize=(12, 6))  # Adjust the size of the plot if needed
    fig.patch.set_facecolor('none')
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # Bar plot for deviations
    ax.bar(names, deviations, color='blue')

    # Customize the plot
    ax.set_ylabel('Deviation (%)', fontsize=14, color='white')

    # Add grid
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7)

    # Rotate and set font size of x-tick labels
    ax.tick_params(axis='both', which='major', labelsize=14, colors='white')
    plt.xticks(rotation=45, fontsize=10)

    container = self.SPR_plot_2
    canvas = FigureCanvas(fig)
    canvas.setStyleSheet("background-color:transparent;")
    toolbar = NavigationToolbar(canvas, self)  # Adjust as necessary

    # Check if the container has a layout, set one if not
    if container.layout() is None:
        layout = QVBoxLayout(container)
        container.setLayout(layout)
    else:
        # Clear existing content in the container, if any
        while container.layout().count():
            child = container.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # Add the canvas and toolbar to the container
    container.layout().addWidget(toolbar)
    container.layout().addWidget(canvas)
    canvas.draw()

def show_error_dialog(self, message):
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setText("Error")
    error_dialog.setInformativeText(message)
    error_dialog.setWindowTitle("Error")
    error_dialog.exec_()        
    
def SPR_fit_plot_fcn(self):
    try:
        extract_data_and_fit(self)
        create_and_embed_plot_SPR_plot_01(self)
    except Exception as e:
        # Catch any other unexpected errors and show them in a dialog
        show_error_dialog(self, f"An error occurred: {str(e)}")  