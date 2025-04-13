import os
import sys
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QVBoxLayout, QMessageBox, QTableWidgetItem, QFileDialog

def on_brachy_load_sources(self):
    """
    Callback for the Brachy_load_sources button.
    Scans the 'fcn_brachy_sources' folder for subfolders and updates the combobox 'brachy_source_list'.
    """
    # Determine the base directory:
    # When compiled (e.g., with PyInstaller), __file__ might not work as expected.
    if getattr(sys, 'frozen', False):
        # In a compiled application, use the directory of the executable.
        base_dir = os.path.dirname(sys.executable)  
        # Construct the path to the 'fcn_brachy_sources' folder.
        brachy_folder = os.path.join(base_dir, "fcn_brachy_sources")
    else:
        # When running as a Python script, use the directory of the current file.
        brachy_folder = os.path.dirname(os.path.abspath(__file__))
    
  
    
    # Check if the folder exists.
    if not os.path.exists(brachy_folder):
        QMessageBox.critical(self, "Error", f"The folder {brachy_folder} does not exist.")
        return

    try:
        # List only subdirectory names, ignoring the folder named "_pycache_".
        subfolder_names = [
            name for name in os.listdir(brachy_folder)
            if os.path.isdir(os.path.join(brachy_folder, name)) and name != "__pycache__"
        ]
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to list subfolders in {brachy_folder}.\nError: {e}")
        subfolder_names = []

    # Clear the combobox before updating.
    self.brachy_source_list.clear()

    # Update the combobox with the folder names.
    self.brachy_source_list.addItems(subfolder_names)

    # Provide a brief confirmation message or log output.
    # print(f"Updated brachy_source_list with folders: {subfolder_names}")

def on_brachy_source_selection(self):
    """
    Callback for when a folder is selected from the combobox (self.brachy_source_list).
    It opens the folder, looks for 'radial.txt', reads its content, and does the following:
      - First line: Sets the text of self.brachy_radial_1stline (a QLineEdit).
      - Second line: Uses the comma-separated values as column headers for self.Brachy_Radial_table.
      - The remaining lines: Splits each by comma and adds them as rows to the table.
    """
    # Get the selected folder name (trim any whitespace).
    selected_folder = self.brachy_source_list.currentText().strip()
    if not selected_folder:
        # QMessageBox.critical(self, "Error", "No folder selected.")
        return

    # Determine the base directory. This works for both compiled executables and scripts.
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        # Build the full path to the radial.txt file inside the selected folder.
        radial_file_path = os.path.join(base_dir, "fcn_brachy_sources", selected_folder, "radial.txt")
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        radial_file_path = os.path.join(base_dir, selected_folder, "radial.txt")
    
    
    
    # Check if the radial.txt file exists.
    if not os.path.exists(radial_file_path):
        QMessageBox.critical(self, "Error", f"radial.txt not found in folder:\n{radial_file_path}")
        return
    else:
        load_radial_data(self,radial_file_path)

def select_Radial_file2load(self):
    """
    Opens a file dialog to select a radial.txt file.
    Once selected, it reads the file and populates the Brachy_Radial_table.
    """
    # Open a file dialog to select the radial.txt file.
    radial_file_path, _ = QFileDialog.getOpenFileName(self, "Select radial.txt", "", "Text Files (*.txt);;All Files (*)")

    # If no file was selected, return early.
    if not radial_file_path:
        return

    # Load the data from the selected file.
    load_radial_data(self,radial_file_path)

def load_radial_data(self,radial_file_path):

    try:
        # Open and read the file, collecting only non-empty lines.
        with open(radial_file_path, "r") as file:
            lines = [line.strip() for line in file if line.strip()]
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to open radial.txt.\nError: {e}")
        return

    # Ensure the file has at least two lines.
    if len(lines) < 2:
        QMessageBox.critical(self, "Error", "radial.txt must contain at least two lines (the header line and column titles).")
        return

    # # 1. Update the QLineEdit with the first line.
    self.brachy_radial_1stline.setText(lines[0])

    # 2. Process the second line as comma-separated column titles.
    # Disable signals before making changes.
    self.Brachy_Radial_table.blockSignals(True)
    headers = [header.strip() for header in lines[1].split(",")]
    
    # Clear and set up the table.
    self.Brachy_Radial_table.clear()
    self.Brachy_Radial_table.setColumnCount(len(headers))
    self.Brachy_Radial_table.setHorizontalHeaderLabels(headers)
    self.Brachy_Radial_table.setRowCount(0)

    # 3. Process the remaining lines as rows in the table.
    for data_line in lines[2:]:
        # Split the line using a comma.
        row_values = [value.strip() for value in data_line.split(",")]
        # Insert a new row into the table.
        current_row = self.Brachy_Radial_table.rowCount()
        self.Brachy_Radial_table.insertRow(current_row)
        # Loop over the expected number of columns.
        for col in range(len(headers)):
            # If data for this column exists, use it; otherwise, leave the cell empty.
            cell_value = row_values[col] if col < len(row_values) else ""
            item = QTableWidgetItem(cell_value)
            self.Brachy_Radial_table.setItem(current_row, col, item)
    # Disable signals before making changes.
    self.Brachy_Radial_table.blockSignals(False)
    # print(f"Loaded radial.txt from folder '{selected_folder}' with headers {headers} and {len(lines)-2} data rows.")
    plot_brachy_radial_fit(self)

def plot_brachy_radial_fit(self):
    """
    Plots the radial data from self.Brachy_Radial_table:
    - X-axis: First column (Distance (cm))
    - Y-axis: Second column (g_L(r))
    
    Data points are plotted as circles.
    A 5th degree polynomial is fitted to the data and plotted as a dashed line.
    The fitted polynomial equation is printed to the command line.
    
    Text colors are set to black when the background color is white, otherwise white.
    """
    # Retrieve user-selected settings
    font_size = self.selected_font_size
    background_color = self.selected_background
    
    # Determine text color based on the background selection
    text_color = 'black' if background_color.lower() == 'white' else 'white'
    
    # Get the container widget for the plot
    container = self.Brachy_radial_axes

    # Set the background color for the container widget
    if background_color.lower() == 'transparent':
        container.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
    else:
        container.setStyleSheet(f"background-color: {background_color};")
    
    # Initialize the Matplotlib Figure if it doesn't exist
    if not hasattr(self, 'plot_Brachy_Radial_Fig'):
        self.plot_Brachy_Radial_Fig = Figure()
        self.plot_radial_canvas = FigureCanvas(self.plot_Brachy_Radial_Fig)
        self.plot_radial_toolbar = NavigationToolbar(self.plot_radial_canvas, self)
        
        # Create or update the layout for the container widget
        if container.layout() is None:
            layout = QVBoxLayout(container)
            container.setLayout(layout)
        else:
            while container.layout().count():
                child = container.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                    
        container.layout().addWidget(self.plot_radial_toolbar)
        container.layout().addWidget(self.plot_radial_canvas)
    else:
        # Clear the figure if it exists
        self.plot_Brachy_Radial_Fig.clf()
    
    # Create the axes for plotting
    ax = self.plot_Brachy_Radial_Fig.add_subplot(111)
    
    # Set background for plot and figure
    if background_color.lower() == 'transparent':
        ax.set_facecolor((0, 0, 0, 0))
        self.plot_Brachy_Radial_Fig.patch.set_alpha(0.0)
    else:
        ax.set_facecolor(background_color)
        self.plot_Brachy_Radial_Fig.patch.set_facecolor(background_color)
    
    # Set text properties for axes
    ax.tick_params(labelsize=font_size, colors=text_color)
    ax.set_xlabel("Distance (cm)", fontsize=font_size, color=text_color)
    ax.set_ylabel("g_L(r)", fontsize=font_size, color=text_color)
    
    # Retrieve data from the radial table widget
    x_data = []
    y_data = []
    table = self.Brachy_Radial_table
    row_count = table.rowCount()
    
    for row in range(row_count):
        x_item = table.item(row, 0)  # First column: Distance (cm)
        y_item = table.item(row, 1)  # Second column: g_L(r)
        if x_item is None or y_item is None:
            continue
        try:
            x_val = float(x_item.text())
            y_val = float(y_item.text())
        except ValueError:
            continue  # Skip non-numeric data
        x_data.append(x_val)
        y_data.append(y_val)
    
    if not x_data or not y_data:
        QMessageBox.warning(self, "Data Missing", "No valid radial data available for plotting.")
        return

    # Plot the data points as circles (markers only)
    ax.plot(x_data, y_data, 'o', markersize=self.selected_point_size, mfc=self.selected_point_color, markeredgecolor=self.selected_point_color, label='Data Points')
    
    # Fit a 5th degree polynomial to the data
    try:
        poly_coeffs = np.polyfit(x_data, y_data, 5)
    except Exception as e:
        QMessageBox.critical(self, "Fit Error", f"Error during polynomial fitting:\n{e}")
        return
    
    # Generate x-values for the polynomial fit curve
    x_fit = np.linspace(min(x_data), max(x_data), 200)
    y_fit = np.polyval(poly_coeffs, x_fit)
    
    # Plot the polynomial fit as dashed lines
    ax.plot(x_fit, y_fit, linestyle='--',linewidth=self.selected_line_width, color=self.selected_line_color,  label='5th Degree Fit')
    
    # Construct a string representation of the polynomial equation
    # Equation form: y = a5*x^5 + a4*x^4 + ... + a1*x + a0
    equation_terms = []
    degree = 5
    for coef in poly_coeffs[:-1]:
        equation_terms.append(f"{coef:.3g}*x^{degree}")
        degree -= 1
    equation_terms.append(f"{poly_coeffs[-1]:.3g}")
    # equation_str = " + ".join(equation_terms)
    
    # print("Fitted 5th degree polynomial:")
    # print("g_L(r) = " + equation_str)
    

    # Assign the polynomial coefficients to the corresponding QLineEdit widgets.
    try:
        self.Brachy_rad_A0.setText(f"{poly_coeffs[5]:.3g}")  # constant term
        self.Brachy_rad_A1.setText(f"{poly_coeffs[4]:.3g}")  # coefficient for x^1
        self.Brachy_rad_A2.setText(f"{poly_coeffs[3]:.3g}")  # coefficient for x^2
        self.Brachy_rad_A3.setText(f"{poly_coeffs[2]:.3g}")  # coefficient for x^3
        self.Brachy_rad_A4.setText(f"{poly_coeffs[1]:.3g}")  # coefficient for x^4
        self.Brachy_rad_A5.setText(f"{poly_coeffs[0]:.3g}")  # coefficient for x^5
    except AttributeError:
        # In case some widgets are not defined, print a warning.
        print("Warning: One or more coefficient QLineEdit widgets (Brachy_rad_A0...A5) are not defined.")


    # 
    ax.legend(fontsize=font_size)
    
    # Draw the updated canvas to display the new plot
    self.plot_radial_canvas.draw()