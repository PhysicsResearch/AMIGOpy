import numpy as np
from scipy.optimize import curve_fit
from scipy.optimize import least_squares
from PyQt5.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

def Zeff_copy_ref_columns(self):
    # copy reference data from the material info
    row_count    = self.MatInfoTable.rowCount()
    column_count = self.MatInfoTable.columnCount()

    # Index of the fourth-last column
    fourth_last_column_index = column_count - 5

    # Ensure REDTable has the same row count as MatInfoTable
    self.tableZeff.setRowCount(row_count)
    self.tableZeff.setColumnCount(5)  # Ensure ZeffTable has 2 columns

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
        self.tableZeff.setItem(row, 0, QTableWidgetItem(first_col_text))

        # Set data to the second column of REDTable
        self.tableZeff.setItem(row, 1, QTableWidgetItem(fourth_last_col_text))
        
        
def fit_function_Z_saito(HU_data, gamma, gamma0):
    HUH, HUL, rho_e = HU_data
    return gamma * ((HUL/1000 +1)/rho_e -1) + gamma0

def fit_function_Z_hun(HU_data, de, Zeff_w, m):
    HUH, HUL, rho_e = HU_data
    return ((1/rho_e)*(de*(HUL/1000 +1) + (Zeff_w**m - de)*(HUH/1000+1)))**(1/m)

def fit_function_Z_hun_wrapped(HU_data, de, Zeff_w, m):
    return fit_function_Z_hun(HU_data, de, Zeff_w, m)

# Saito
def extract_data_and_fit(self):
    row_count    = self.MatInfoTable.rowCount()
    column_count = self.MatInfoTable.columnCount()

    # Assuming the last column is HUH and the second to last is HUL
    HUH_column_index = column_count - 1
    HUL_column_index = column_count - 2

    HUH   = []
    HUL   = []
    rho_e = []  
    zeff  = []  

    for row in range(row_count):
        HUH_item   = self.MatInfoTable.item(row, HUH_column_index)
        HUL_item   = self.MatInfoTable.item(row, HUL_column_index)
        rho_e_item = self.tableRED.item(row, 2)  # Calculated RED
        zeff_item  = self.tableZeff.item(row, 1) # Reference Zeff
        if HUH_item and HUL_item and rho_e_item:
            HUH.append(float(HUH_item.text()))
            HUL.append(float(HUL_item.text()))
            rho_e.append(float(rho_e_item.text()))
            zeff.append(float(zeff_item.text()))

    # Convert lists to numpy arrays
    HUH = np.array(HUH)
    HUL = np.array(HUL)
    rho_e = np.array(rho_e)
    zeff  = np.array(zeff)

    # Prepare data for curve fitting
    HU_data     = np.vstack((HUH, HUL, rho_e))
    m_text = self.Zeff_m.text()
    m      = float(m_text)
    
    # calculate water Zeff
    # Z/A H = 0.99212 mass fraction 0.1111
    # Z/A 0 = 0.50002 mass fraction 0.8889
    
    Zeff_w = (((0.99212*0.1111*1**m) + (0.50002*0.8889*8**m)) / ((0.99212*0.1111) + (0.50002*0.8889)))**(1/m)
    #   
    selected_zeff_method = self.Zeff_method_list.currentText()
    #
    if   selected_zeff_method == "Saito":
       #  # Calculate Zeff_m for each row
       # Zeff_m = (zeff / Zeff_w) ** m -1
       
       # # Initial guess for the parameters a, alpha, and b
       # initial_guess = [10, 0]
       
       # bounds = ([-np.inf, -np.inf], [np.inf, np.inf])
   
       # # Perform the curve fitting
       # popt, pcov = curve_fit(fit_function_Z_saito, HU_data, Zeff_m, p0=initial_guess, bounds=bounds)
   
       # # Extract the fitted parameters
       # gamma, gamma0 = popt
   
       # # Calculate fitted values
       # fitted_zeff = fit_function_Z_saito(HU_data, *popt)
       # fitted_zeff = (fitted_zeff+1)**(1/m)*Zeff_w
       #
       # Calculate Zeff_m for each row
       Zeff_m = (zeff / Zeff_w) ** m -1
        
       # Define the residuals function
       def residuals(params, HU_data, Zeff_m, m):
           gamma, gamma0 = params  # Unpack the parameters
           # Calculate the predicted Zeff_m based on the current parameters
           predicted_zeff = fit_function_Z_saito(HU_data, gamma, gamma0)
           # predicted_zeff = (predicted_zeff ** (1 / m)) * Zeff_w
           # Return the residuals (difference between predicted and actual Zeff_m)
           return predicted_zeff - Zeff_m
        
       # Initial guess for the parameters gamma and gamma0
       initial_guess = [9, 0.04]
        
       # Set the bounds for the parameters (could be infinite bounds if no restriction is needed)
       bounds = ([-20, -2], [20, 2])
        
       # Perform least squares optimization using the 'residuals' function
       result = least_squares(
            residuals,  # residuals function
            initial_guess,  # initial guess for gamma and gamma0
            args=(HU_data, Zeff_m, m),  # pass additional arguments to the residuals function
            bounds=bounds,  # parameter bounds
            method='trf',   # optimization method (trust region reflective)
            ftol=1e-11, xtol=1e-11, gtol=1e-11, max_nfev=500000  # tolerance settings for precision
       )
        
       # Extract the optimal parameters from the result
       gamma, gamma0 = result.x  # Extract optimized gamma and gamma0
        
       # Calculate the fitted values based on the optimal parameters
       fitted_zeff = fit_function_Z_saito(HU_data, gamma, gamma0)
       fitted_zeff = (fitted_zeff+1) ** (1 / m) * Zeff_w
        
    elif selected_zeff_method == "Hunemohr":
        # Define the residuals function
        def residuals(params, HU_data, zeff, Zeff_w, m):
            de = params[0]  # Unpack the single parameter
            # Calculate the predicted zeff based on the current parameter 'de'
            predicted_zeff = fit_function_Z_hun_wrapped(HU_data, de, Zeff_w, m)
            # Return the residuals (difference between predicted and actual zeff)
            return predicted_zeff - zeff
        
        # Initial guess for the parameter 'de'
        initial_guess = [0.5]
        
        # Set the bounds for the parameter (could be infinite bounds if no restriction is needed)
        bounds = ([-np.inf], [np.inf])
        
        # Perform least squares optimization using the 'residuals' function
        result = least_squares(
            residuals,  # residuals function
            initial_guess,  # initial guess for 'de'
            args=(HU_data, zeff, Zeff_w, m),  # pass additional arguments to the residuals function
            bounds=bounds,  # parameter bounds
            method='trf',   # optimization method (trust region reflective)
            ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=50000  # tolerance settings for precision
        )
        
        # Extract the optimal parameter from the result
        de = result.x[0]  # Extract optimized 'de'
        
        # Calculate the fitted values based on the optimal parameter
        fitted_zeff = fit_function_Z_hun_wrapped(HU_data, de, Zeff_w, m)

    # Calculate R^2 (coefficient of determination)
    residuals = zeff - fitted_zeff
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((zeff - np.mean(rho_e))**2)
    r_squared = 1 - (ss_res / ss_tot)


    
    self.Zeff_r_square_text.setText(f"{r_squared:.4f}")
    
    
    if   selected_zeff_method == "Saito":
        self.Zeff_fit_1.setText("gamma")
        self.Zeff_fit_01_text.setText(f"{gamma:.4f}")
        self.Zeff_fit_2.setText("gamm_o")
        self.Zeff_fit_02_text.setText(f"{gamma0:.4f}")

        #
    elif selected_zeff_method == "Hunemohr":
        self.Zeff_fit_1.setText("de")
        self.Zeff_fit_01_text.setText(f"{de:.4f}")
        self.Zeff_fit_2.setText(" ")
        self.Zeff_fit_02_text.setText(" ")
        
    # Initialize a list to store squared percentage errors
    squared_percentage_errors = []
        
    # Calculate new zeff values and update the second, third, and fourth columns of REDTable
    for row in range(row_count):
        # Calculate the difference and percentage
        difference = fitted_zeff[row] - zeff[row]
        percentage = (difference / zeff[row]) * 100 if zeff[row] != 0 else 0
        squared_percentage_errors.append(percentage**2)
        # Update the second, third, and fourth columns of REDTable
        self.tableZeff.setItem(row, 2, QTableWidgetItem(f"{fitted_zeff[row]:.3f}"))
        self.tableZeff.setItem(row, 3, QTableWidgetItem(f"{difference:.3f}"))
        self.tableZeff.setItem(row, 4, QTableWidgetItem(f"{percentage:.2f}%"))
        
    # Calculate RMSE
    rmse = np.sqrt(np.mean(squared_percentage_errors))       
    self.Zeff_RMSE_text.setText(f"{rmse:.4f}")
    
    
    # Plot reference values vs fitted values
    fig, ax = plt.subplots()
    fig.patch.set_facecolor('none')
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # Scatter plot for reference vs fitted values
    ax.scatter(zeff, fitted_zeff, label='Data Points', color='blue')

    # Continuous fit line (diagonal line for perfect fit reference)
    min_val = min(zeff.min(), fitted_zeff.min())
    max_val = max(zeff.max(), fitted_zeff.max())
    ax.plot([min_val, max_val], [min_val, max_val], label='Perfect Fit Line', color='red', linestyle='--')

    # Customize the plot
    ax.set_xlabel('Reference Values (Zeff)', fontsize=14,color='white')
    ax.set_ylabel('Fitted Values (Zeff)', fontsize=14,color='white')
    ax.set_title('Reference vs Fitted Zeff', fontsize=14,color='white')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7)
    ax.legend()

    ax.tick_params(axis='both', which='major', labelsize=14, colors='white')

    container = self.Zeff_plot_2
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
   
   
   
def create_and_embed_plot_Zeff_plot_01(self):
    # Extract data from self.tableRED
    row_count = self.tableZeff.rowCount()

    names = []
    ref_values = []
    fit_values = []
    deviations = []

    for row in range(row_count):
        name_item = self.tableZeff.item(row, 0)  # Assuming name or line ID is in the first column
        ref_item  = self.tableZeff.item(row, 1)  # Assuming ref data is in the second column
        fit_item  = self.tableZeff.item(row, 2)  # Assuming fit data is in the third column

        if name_item and ref_item and fit_item:
            names.append(name_item.text())
            ref_value = float(ref_item.text())
            fit_value = float(fit_item.text())
            ref_values.append(ref_value)
            fit_values.append(fit_value)
            deviation = ((fit_value - ref_value) / ref_value) * 100 if ref_value != 0 else 0.00
            # if 0 === sewt a small value so it is visible in the plot ... not used for any caluclation
            if deviation == 0:
                deviation = 0.01
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

    container = self.Zeff_plot_1
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
    
def Zeff_fit_plot_fcn(self):
    try:
        extract_data_and_fit(self)
        create_and_embed_plot_Zeff_plot_01(self)
    except Exception as e:
        # Catch any other unexpected errors and show them in a dialog
        show_error_dialog(self, f"An error occurred: {str(e)}")   