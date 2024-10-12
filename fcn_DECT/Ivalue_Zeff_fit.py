# Zeff _ I value fit functions
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
from PyQt5.QtWidgets import QVBoxLayout, QApplication, QMessageBox

# Plot I-values
def plot_I_value_points(self):
    # Close the previous figure if exists
    plt.close('all')
    # Find column indexes for 'Zeff' and 'I'
    zeff_column_index = find_column_index(self,"Zeff")
    i_column_index = find_column_index(self,"I")

    # Extract Zeff and I values from the table
    zeff_values = []
    i_values = []
    for row in range(self.MatInfoTable.rowCount()):
        zeff_item = self.MatInfoTable.item(row, zeff_column_index)
        i_item = self.MatInfoTable.item(row, i_column_index)

        if zeff_item is not None and i_item is not None:
            zeff_values.append(float(zeff_item.text()))
            i_val = np.log(float(i_item.text()))
            i_values.append(i_val)
    selected_Ivalue_method = self.Ivalue_method_list.currentText()
    
    #
    if selected_Ivalue_method == "Saito":
        # calculate water Zeff
        # Z/A H = 0.99212 mass fraction 0.1111
        # Z/A 0 = 0.50002 mass fraction 0.8889
        m_text = self.Zeff_m.text()
        m      = float(m_text)
        Zeff_w = (((0.99212*0.1111*1**m) + (0.50002*0.8889*8**m)) / ((0.99212*0.1111) + (0.50002*0.8889)))**(1/m)
        I_water = float(self.Iv_water_ref.value())
        #
        zeff_values = np.array(zeff_values)
        zeff_values = (zeff_values/Zeff_w)**m -1
        i_values    = np.array(i_values)
        i_values    = i_values - np.log(I_water)
        # Plotting
        self.fig_I_value, self.ax_I_value = plt.subplots()
        self.ax_I_value.scatter(zeff_values, i_values)
        self.ax_I_value.set_xlabel("(Zeff/Zeff_w)^m-1", fontsize=16)
        self.ax_I_value.set_ylabel("Ln(I/Iw) value", fontsize=16)
        self.ax_I_value.tick_params(axis='both', which='major', labelsize=14)

    elif selected_Ivalue_method == "Hunemohr":
        # Plotting
        self.fig_I_value, self.ax_I_value = plt.subplots()
        self.ax_I_value.scatter(zeff_values, i_values)
        self.ax_I_value.set_xlabel("Zeff", fontsize=16)
        self.ax_I_value.set_ylabel("Ln(I) value", fontsize=16)
        self.ax_I_value.tick_params(axis='both', which='major', labelsize=14)

    # Embed the plot in the Qt interface
    self.canvas_I_value = FigureCanvas(self.fig_I_value)
    toolbar = NavigationToolbar(self.canvas_I_value, self.Ivalue_plot)

    # Check if Ivalue_plot has a layout, set one if not
    if self.Ivalue_figure.layout() is None:
        layout = QVBoxLayout(self.Ivalue_plot)
        self.Ivalue_figure.setLayout(layout)
    else:
        # Clear existing content in Ivalue_plot, if any
        while self.Ivalue_figure.layout().count():
            child = self.Ivalue_figure.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # Add the canvas to Ivalue_plot
    self.Ivalue_figure.layout().addWidget(toolbar)
    self.Ivalue_figure.layout().addWidget(self.canvas_I_value)
    self.canvas_I_value.draw()
    
    
def cal_plot_I_value_points(self):     
    # Find column indexes for 'Zeff' and 'I'
    zeff_column_index = find_column_index(self,"Zeff")
    i_column_index    = find_column_index(self,"I")
    # Extract Zeff and I values from the table
    zeff_values = []
    i_values = []
    for row in range(self.MatInfoTable.rowCount()):
        zeff_item = self.MatInfoTable.item(row, zeff_column_index)
        i_item    = self.MatInfoTable.item(row, i_column_index)
        if zeff_item is not None and i_item is not None:
            zeff_values.append(float(zeff_item.text()))
            i_val = np.log(float(i_item.text()))
            i_values.append(i_val)
    # Get number of fits and fit limits
    n_fits, fit_limits = get_fit_regions(self)
    # Ensure fit_limits has the correct number of entries
    if len(fit_limits) < n_fits:
        fit_limits.append(max(zeff_values))  # Append the max value for the last segment

    # Sort the zeff_values and i_values based on zeff_values to ensure order
    sorted_pairs = sorted(zip(zeff_values, i_values))
    zeff_values, i_values = [list(t) for t in zip(*sorted_pairs)]
    zeff_values = np.array(zeff_values)
    i_values    = np.array(i_values)
    # Lists to store coefficients
    a_coefficients  = []
    b_coefficients  = []
    max_zeff_values = []
    min_zeff_values = [min(zeff_values)]  # Start with the minimum Zeff value
    # Perform fits and collect coefficients
    #
    # method
    selected_Ivalue_method = self.Ivalue_method_list.currentText()
    #
    start = 0
    prev_limit = min(zeff_values)  # Initialize prev_limit to the first value
    #
    for i, limit in enumerate(fit_limits):
        end = next((i for i, x in enumerate(zeff_values[start:], start) if x > limit), len(zeff_values))
        is_last_segment = (i == n_fits - 1)
        if   selected_Ivalue_method == "Hunemohr":
            a, b = perform_and_plot_fit_H(self,zeff_values[start:end], i_values[start:end], prev_limit, limit, is_last_segment)
        elif selected_Ivalue_method == "Saito":
            # calculate water Zeff
            # Z/A H = 0.99212 mass fraction 0.1111
            # Z/A 0 = 0.50002 mass fraction 0.8889
            m_text = self.Zeff_m.text()
            m      = float(m_text)
            Zeff_w = (((0.99212*0.1111*1**m) + (0.50002*0.8889*8**m)) / ((0.99212*0.1111) + (0.50002*0.8889)))**(1/m)
            I_water = float(self.Iv_water_ref.value())
            #   
            x_values = (zeff_values[start:end]/Zeff_w)**m-1
            y_values = i_values[start:end] - np.log(I_water)
            p_limit  = (prev_limit/Zeff_w)**m-1
            lim      = (limit/Zeff_w)**m-1
            a, b = perform_and_plot_fit_S(self,x_values,y_values, p_limit, lim, is_last_segment)
        #    
        a_coefficients.append(a)
        b_coefficients.append(b)
        max_zeff_values.append(zeff_values[end - 1] if end - 1 < len(zeff_values) else zeff_values[-1])
        if i < n_fits - 1:  # For all but the last interval, set the next min limit
            min_zeff_values.append(limit)
        start = end
        prev_limit = limit  # Update prev_limit for the next segment
        self.canvas_I_value.draw()
    # Redraw the figure
    self.canvas_I_value.draw_idle() # Assuming canvas 
    QApplication.processEvents()
    # Format coefficients with five decimal places and update QLineEdit widgets
    formatted_a_coeffs = " ".join(f"{a:.5f}" for a in a_coefficients)
    formatted_b_coeffs = " ".join(f"{b:.5f}" for b in b_coefficients)
    formatted_max_zeff = " ".join(f"{z:.5f}" for z in max_zeff_values)
    formatted_min_zeff = " ".join(f"{z:.5f}" for z in min_zeff_values)
    self.I_value_a_coeff_calc.setText(formatted_a_coeffs)
    self.I_value_b_coeff_calc.setText(formatted_b_coeffs)
    self.I_value_z_up_values.setText(formatted_max_zeff)
    self.I_value_z_lw_values.setText(formatted_min_zeff)

def perform_and_plot_fit_H(self, x_data, y_data, x_start, x_end, is_last_segment=False):
    # Calculate linear fit
    fit_parameters = np.polyfit(x_data, y_data, 1)  # Linear fit
    fit_function = np.poly1d(fit_parameters)
    a, b = fit_parameters
    print(f"Plotting segment: x_start={x_start}, x_end={x_end}, len(x_data)={len(x_data)}")
    # Generate y-values for the fit line
    x_fit = np.linspace(x_start, x_end, 100)
    fit_line_y_values = fit_function(x_fit)

    # Create label with equation and upper limit
    label = f"y = {a:.2f}x + {b:.2f}"
    if not is_last_segment:
        label += f" (up to {x_end:.2f})"

    # Plot fit line on the existing figure
    self.ax_I_value.plot(x_fit, fit_line_y_values, color='red', label=label)
    self.ax_I_value.legend()  # Update the legend

    # Return the slope (a) and intercept (b)
    return a, b

def perform_and_plot_fit_S(self, x_data, y_data, x_start, x_end, is_last_segment=False):
    # Calculate linear fit
    fit_parameters = np.polyfit(x_data, y_data, 1)  # Linear fit
    fit_function = np.poly1d(fit_parameters)
    a, b = fit_parameters
    print(f"Plotting segment: x_start={x_start}, x_end={x_end}, len(x_data)={len(x_data)}")
    # Generate y-values for the fit line
    x_fit = np.linspace(x_start, x_end, 100)
    fit_line_y_values = fit_function(x_fit)

    # Create label with equation and upper limit
    label = f"y = {a:.2f}x + {b:.2f}"
    if not is_last_segment:
        label += f" (up to {x_end:.2f})"

    # Plot fit line on the existing figure
    self.ax_I_value.plot(x_fit, fit_line_y_values, color='red', label=label)
    self.ax_I_value.legend()  # Update the legend

    # Return the slope (a) and intercept (b)
    return a, b


def find_column_index(self, column_name):
    for column in range(self.MatInfoTable.columnCount()):
        if self.MatInfoTable.horizontalHeaderItem(column).text() == column_name:
            return column
    return -1  # Return -1 if column name not found
    
def get_fit_regions(self):
    n_fits = self.N_lin_fit.value()  # Get number of fits
    fit_limits_str = self.I_Fit_limits.text()  # Get fit limits as string
    fit_limits = [float(x) for x in fit_limits_str.split(' ') if x]  # Convert to list of numbers
    # Check if the number of limits is correct
    if n_fits > 1 and len(fit_limits) != n_fits - 1:
        # Show error message
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error in Fit Limits")
        msg.setInformativeText("The number of fit limits should be one less than the number of fits.")
        msg.setWindowTitle("Error")
        msg.exec_()
        return None, None  # Return None to indicate an error
    
    return n_fits, fit_limits                   
    
    
def plot_I_value_precalc(self):  
    # Retrieve and split the values from QLineEdit fields
    a_values = [float(a) for a in self.I_value_a_coeff_calc.text().split()]
    b_values = [float(b) for b in self.I_value_b_coeff_calc.text().split()]
    min_values = [float(min_val) for min_val in self.I_value_z_lw_values.text().split()]
    max_values = [float(max_val) for max_val in self.I_value_z_up_values.text().split()]
    # Check if all lists have the same length
    if not (len(a_values) == len(b_values) == len(min_values) == len(max_values)):
        print("Error: Mismatch in the number of entries in the fields.")
        return
    # Plot each line segment
    for a, b, min_val, max_val in zip(a_values, b_values, min_values, max_values):
        x = np.linspace(min_val, max_val, 100)
        y = a * x + b
        self.ax_I_value.plot(x, y, color='red', label=f'y = {a:.2f}x + {b:.2f}')

    # Update the legend and redraw the canvas
    self.ax_I_value.legend()
    self.canvas_I_value.draw_idle()
