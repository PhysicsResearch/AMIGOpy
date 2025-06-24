import numpy as np
from scipy.optimize import curve_fit
from PyQt5.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

def Iv_copy_ref_columns(self):
    # copy reference data from the material info
    row_count    = self.MatInfoTable.rowCount()
    column_count = self.MatInfoTable.columnCount()

    # Index of the fourth-last column
    fourth_last_column_index = column_count - 4

    # Ensure REDTable has the same row count as MatInfoTable
    self.tableIv.setRowCount(row_count)
    self.tableIv.setColumnCount(5)  # Ensure ZeffTable has 2 columns

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

        # Set data to the first column of REDTable
        self.tableIv.setItem(row, 0, QTableWidgetItem(first_col_text))

        # Set data to the second column of REDTable
        self.tableIv.setItem(row, 1, QTableWidgetItem(fourth_last_col_text))
        
        

# 
def extract_data_and_fit(self):
    # Get calibration parameters
    #
    # Number of intervals
    Intervals   = self.N_lin_fit.value()
    #
    # Limit intervals
    text            = self.I_Fit_limits.text()
    elements        = text.split()
    Intervals_lim   = []

    for elem in elements:
        try:
            number = float(elem)  # Try to convert the element to a float
            Intervals_lim .append(number)
        except ValueError:
            print("I-value interval limits error")
            return

    Int_limits = np.array(Intervals_lim)
    #
    # a 
    text = self.I_value_a_coeff_calc.text()
    elements = text.split()
    coef_a   = []

    for elem in elements:
        try:
            number = float(elem)  # Try to convert the element to a float
            coef_a.append(number)
        except ValueError:
            print("I-value coeficiednt a error")
            return

    a_c = np.array(coef_a)
    # b
    text = self.I_value_b_coeff_calc.text()
    elements = text.split()
    coef_b   = []

    for elem in elements:
        try:
            number = float(elem)  # Try to convert the element to a float
            coef_b.append(number)
        except ValueError:
            print("I-value coeficiednt b error")
            return

    b_c = np.array(coef_b)
    
    selected_Ivalue_method = self.Ivalue_method_list.currentText()
    
    row_count    = self.tableIv.rowCount()
    
    # calculate water Zeff
    # Z/A H = 0.99212 mass fraction 0.1111
    # Z/A 0 = 0.50002 mass fraction 0.8889
    m_text  = self.Zeff_m.text()
    m       = float(m_text)
    Zeff_w  = (((0.99212*0.1111*1**m) + (0.50002*0.8889*8**m)) / ((0.99212*0.1111) + (0.50002*0.8889)))**(1/m)
    I_water = float(self.Iv_water_ref.value())
    #   
    # Lists to store zeff and Iv_cal values
    Iv_values     = []
    Iv_cal_values = []

    for row in range(row_count):
        zeff_item = self.tableZeff.item(row, 2) # Reference Zeff
        Iv_item   = self.tableIv.item(row, 1)   # Reference I-value
        #
        Iv_cal    = 0
        zeff      = float(zeff_item.text())   # Reference Zeff
        Iv        = float(Iv_item.text())     # Reference I-value
        #
        if   selected_Ivalue_method == "Hunemohr":
            # Calculate I value for each row
            #
            for idx in range(Intervals-1):
                Int_limits[idx]
                if   zeff < Int_limits[idx]:
                    Iv_cal = np.exp(a_c[idx]*zeff + b_c[idx])
                    break
                elif idx == Intervals-2:
                    Iv_cal = np.exp(a_c[-1]*zeff + b_c[-1])
                    break
        elif selected_Ivalue_method == "Saito":
            # Calculate I value for each row
            for idx in range(Intervals-1):
                Int_limits[idx]
                if   zeff < Int_limits[idx]:
                    Iv_cal = np.exp(a_c[idx]*((zeff/Zeff_w)**m-1) + b_c[idx]+np.log(I_water))
                    break
                elif idx == Intervals-2:
                    Iv_cal = np.exp(a_c[-1]*((zeff/Zeff_w)**m-1) + b_c[-1]+np.log(I_water))
                    break
        # Update the second, third, and fourth columns of REDTable
        difference = Iv_cal - Iv
        percentage = difference/Iv * 100
        self.tableIv.setItem(row, 2, QTableWidgetItem(f"{Iv_cal:.3f}"))
        self.tableIv.setItem(row, 3, QTableWidgetItem(f"{difference:.3f}"))
        self.tableIv.setItem(row, 4, QTableWidgetItem(f"{percentage:.2f}%"))
        
        # Store the values for plotting
        Iv_values.append(Iv)
        Iv_cal_values.append(Iv_cal)
    
    Iv_values     = np.array(Iv_values)
    Iv_cal_values = np.array(Iv_cal_values)
    #
    residuals = Iv_cal_values - Iv_values 
    # Calculate RMSE
    rmse = np.sqrt(np.mean(residuals**2))
    self.Ivalue_RMSE_text.setText(f"{rmse:.4f}")
    #
    
    # Plot reference values vs fitted values
    fig, ax = plt.subplots()
    fig.patch.set_facecolor('none')
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # Scatter plot for reference vs fitted values
    ax.scatter(Iv_values,Iv_cal_values, label='Data Points', color='blue')

    # Continuous fit line (diagonal line for perfect fit reference)
    min_val = min(Iv_values.min(), Iv_cal_values.min())
    max_val = max(Iv_values.max(), Iv_cal_values.max())
    ax.plot([min_val, max_val], [min_val, max_val], label='Perfect Fit Line', color='red', linestyle='--')

    # Customize the plot
    ax.set_xlabel('Reference Values (I-value)', fontsize=14,color='white')
    ax.set_ylabel('Fitted Values (I-value)', fontsize=14,color='white')
    ax.set_title('Reference vs Fitted I-value', fontsize=14,color='white')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7)
    ax.legend()

    ax.tick_params(axis='both', which='major', labelsize=14, colors='white')

    container = self.Ivalue_plot_2
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
   
   
   
def create_and_embed_plot_Ivalue_plot_01(self):
    # Extract data from self.tableRED
    row_count = self.tableZeff.rowCount()

    names = []
    ref_values = []
    fit_values = []
    deviations = []

    for row in range(row_count):
        name_item = self.tableIv.item(row, 0)  # name or line ID is in the first column
        ref_item  = self.tableIv.item(row, 1)  # ref data is in the second column
        fit_item  = self.tableIv.item(row, 2)  # fit data is in the third column

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

    container = self.Ivalue_plot_1
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
    
def Iv_fit_plot_fcn(self):
    try:
        extract_data_and_fit(self)
        create_and_embed_plot_Ivalue_plot_01(self)
    except Exception as e:
        # Catch any other unexpected errors and show them in a dialog
        show_error_dialog(self, f"An error occurred: {str(e)}")  