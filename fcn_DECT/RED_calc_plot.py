import numpy as np
# from scipy.optimize import curve_fit
from scipy.optimize import least_squares
from PyQt5.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

def RED_copy_ref_columns(self):
    # copy reference data from the material info
    row_count    = self.MatInfoTable.rowCount()
    column_count = self.MatInfoTable.columnCount()

    # Index of the fourth-last column
    fourth_last_column_index = column_count - 6

    # Ensure REDTable has the same row count as MatInfoTable
    self.tableRED.setRowCount(row_count)
    self.tableRED.setColumnCount(5)  # Ensure REDTable has 2 columns

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
        self.tableRED.setItem(row, 0, QTableWidgetItem(first_col_text))

        # Set data to the second column of REDTable
        self.tableRED.setItem(row, 1, QTableWidgetItem(fourth_last_col_text))
        
        
def fit_function_saito(HU_data, a, alpha, b):
    HUH, HUL = HU_data
    return a * ((1 + alpha) * HUH - alpha * HUL) / 1000 + b

def fit_function_hun(HU_data, ce):
    HUH, HUL = HU_data
    return ce * (HUL/1000 +1) + (1 -ce)*(HUH/1000+1)

# Saito and Hun
def extract_data_and_fit(self):
    try:
        row_count = self.MatInfoTable.rowCount()
        column_count = self.MatInfoTable.columnCount()
    
        # Assuming the last column is HUH and the second to last is HUL
        HUH_column_index = column_count - 1
        HUL_column_index = column_count - 2
    
        HUH = []
        HUL = []
        rho_e = []  # Assuming you have some measured data for rho_e
    
        for row in range(row_count):
            HUH_item = self.MatInfoTable.item(row, HUH_column_index)
            HUL_item = self.MatInfoTable.item(row, HUL_column_index)
            rho_e_item = self.tableRED.item(row, 1)  # Assuming you have rho_e in the first column of tableRED
    
            if HUH_item and HUL_item and rho_e_item:
                HUH.append(float(HUH_item.text()))
                HUL.append(float(HUL_item.text()))
                rho_e.append(float(rho_e_item.text()))
    
        # Convert lists to numpy arrays
        HUH = np.array(HUH)
        HUL = np.array(HUL)
        rho_e = np.array(rho_e)
    
        # Prepare data for curve fitting
        HU_data = np.vstack((HUH, HUL))
    
    
        selected_red_method = self.RED_method_list.currentText()
        #
        if   selected_red_method == "Saito":
            def residuals(params, HU_data, rho_e):
                a, alpha, b = params  # Unpack the parameters
                # Calculate the predicted rho_e based on the current parameters
                predicted_rho_e = fit_function_saito(HU_data, a, alpha, b)
                # Return the residuals (difference between predicted and actual values)
                return predicted_rho_e - rho_e
            
            # Initial guess for the parameters a, alpha, and b
            initial_guess = [1, 1, 1]  # Adjust this based on prior knowledge
        
            # Set the bounds for the parameters
            bounds = ([-2, -1, 0.9], [2, 1, 1.1])
        
            # Perform least squares optimization using the 'residuals' function
            result = least_squares(
                residuals,  # residual function
                initial_guess,  # initial guess for a, alpha, and b
                args=(HU_data, rho_e),  # pass additional arguments to the residuals function
                bounds=bounds,  # parameter bounds
                method='trf',   # optimization method (trust region reflective)
                ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=50000  # tolerance settings for precision
            )
        
            # Extract the optimal parameters from the result
            a, alpha, b = result.x  # Extract optimized a, alpha, and b
        
            # Calculate the fitted values based on the optimal parameters
            fitted_rho_e = fit_function_saito(HU_data, a, alpha, b)
            #
        elif selected_red_method == "Hunemohr":
            def residuals(ce, HU_data, rho_e):
                return fit_function_hun(HU_data, ce) - rho_e
            # Initial guess and bounds for the parameter
            initial_guess = [-0.8]  # You can adjust this based on prior knowledge
            bounds = ([-2], [2])  # Expand or tighten based on your needs
            
            # Perform least squares optimization
            # Perform least squares optimization
            result = least_squares(
                residuals,  # residual function
                initial_guess,  # initial guess for ce
                args=(HU_data, rho_e),  # additional arguments to residuals function
                bounds=bounds,  # parameter bounds
                method='trf',  # optimization method
                ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=50000  # strict tolerances for precision
            )
                    
            # Extract the optimal parameter from the result
            ce = result.x[0]
            
            # Calculate the fitted values
            fitted_rho_e = fit_function_hun(HU_data, ce)
    
        # Calculate R^2 (coefficient of determination)
        residuals = rho_e - fitted_rho_e
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((rho_e - np.mean(rho_e))**2)
        r_squared = 1 - (ss_res / ss_tot)
        self.RED_r_square_text.setText(f"{r_squared:.4f}")
        
        
        if   selected_red_method == "Saito":
            self.RED_fit_01.setText("a")
            self.RED_fit_01_text.setText(f"{a:.4f}")
            self.RED_fit_02.setText("alpha")
            self.RED_fit_02_text.setText(f"{alpha:.4f}")
            self.RED_fit_03.setText("b")
            self.RED_fit_03_text.setText(f"{b:.4f}")
            #
        elif selected_red_method == "Hunemohr":
            self.RED_fit_01.setText("ce")
            self.RED_fit_01_text.setText(f"{ce:.4f}")
            self.RED_fit_02.setText(" ")
            self.RED_fit_02_text.setText(" ")
            self.RED_fit_03.setText(" ")
            self.RED_fit_03_text.setText(" ")
        
        # Initialize a list to store squared percentage errors
        squared_percentage_errors = []
        
        # Calculate differences and update table
        for row in range(row_count):
            # # Calculate the difference and percentage
            # difference = new_rho_e - ref_rho_        
            difference  = rho_e[row] - fitted_rho_e[row]
            percentage = (difference / rho_e[row]) * 100 if rho_e[row] != 0 else 0
            squared_percentage_errors.append(percentage**2)
            # Update the second, third, and fourth columns of REDTable
            self.tableRED.setItem(row, 2, QTableWidgetItem(f"{fitted_rho_e[row]:.3f}"))
            self.tableRED.setItem(row, 3, QTableWidgetItem(f"{difference:.3f}"))
            self.tableRED.setItem(row, 4, QTableWidgetItem(f"{percentage:.2f}%"))
        
        # Calculate RMSE
        rmse = np.sqrt(np.mean(squared_percentage_errors))
        self.RED_RMSE_text.setText(f"{rmse:.4f}")
                       
        # Plot reference values vs fitted values
        fig, ax = plt.subplots()
        fig.patch.set_facecolor('none')
        fig.patch.set_alpha(0)
        ax.set_facecolor('none')
    
        # Scatter plot for reference vs fitted values
        ax.scatter(rho_e, fitted_rho_e, label='Data Points', color='blue')
    
        # Continuous fit line (diagonal line for perfect fit reference)
        min_val = min(rho_e.min(), fitted_rho_e.min())
        max_val = max(rho_e.max(), fitted_rho_e.max())
        ax.plot([min_val, max_val], [min_val, max_val], label='Perfect Fit Line', color='red', linestyle='--')
    
        # Customize the plot
        ax.set_xlabel('Reference Values (ρ_e)', fontsize=14,color='white')
        ax.set_ylabel('Fitted Values (ρ_e)', fontsize=14,color='white')
        ax.set_title('Reference vs Fitted ρ_e', fontsize=14,color='white')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.7)
        ax.legend()
    
        ax.tick_params(axis='both', which='major', labelsize=14, colors='white')
    
        container = self.RED_plot_02
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
    except Exception as e:
        # Catch any other unexpected errors and show them in a dialog
        show_error_dialog(self, f"An error occurred: {str(e)}")   
   
   
def create_and_embed_plot_RED_plot_01(self):
    # Extract data from self.tableRED
    row_count = self.tableRED.rowCount()

    names = []
    ref_values = []
    fit_values = []
    deviations = []

    for row in range(row_count):
        name_item = self.tableRED.item(row, 0)  # Assuming name or line ID is in the first column
        ref_item = self.tableRED.item(row, 1)  # Assuming ref data is in the second column
        fit_item = self.tableRED.item(row, 2)  # Assuming fit data is in the third column

        if name_item and ref_item and fit_item:
            names.append(name_item.text())
            ref_value = float(ref_item.text())
            fit_value = float(fit_item.text())
            ref_values.append(ref_value)
            fit_values.append(fit_value)
            deviation = ((fit_value - ref_value) / ref_value) * 100 if ref_value != 0 else 0
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

    container = self.RED_plot_01
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
    
def RED_fit_plot_fcn(self):
    extract_data_and_fit(self)
    create_and_embed_plot_RED_plot_01(self)