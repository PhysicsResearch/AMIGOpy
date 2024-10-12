import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, 
    QWidget, QLineEdit, QLabel, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


def openCSVFile_exp(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            previewCSV(self,fileName)
            processCSV(self,fileName)

def previewCSV(self, filePath):
    try:
        with open(filePath, 'r') as file:
            # Read the next 100 lines and add line numbers
            lines = []
            for i in range(1, 101):
                line = file.readline()
                if not line:
                    break
                lines.append(f"{i}: {line}")
            
            preview = ''.join(lines)
        self.CSVViewText.setPlainText(preview)
    except Exception as e:
        self.CSVViewText.setPlainText(f'Error reading file: {e}')
    
def processCSV(self, filePath):
    separator   = self.csv_sep_list.currentText()
    skip_lines  = int(self.CSVLineSkip.value())
    header_line = int(self.CSVLinHeader.value())-1
    # Determine the header parameter for pandas read_csv
    header_param = header_line if header_line >= 0 else None
    
    # Load the CSV file into a DataFrame
    dataframe = pd.read_csv(filePath, sep=separator, skiprows=skip_lines, header=header_param)
    
    # If no header, set default column names
    if header_line == -1:
        dataframe.columns = [f'C{i+1}' for i in range(dataframe.shape[1])]
    
    # Update the combo boxes for x and y axis selection
    self.CSV_X_plot.clear()
    self.CSV_Y_plot.clear()
    self.CSV_X_plot.addItems(dataframe.columns)
    self.CSV_Y_plot.addItems(dataframe.columns)
    
    # Display the data in the QTableWidget
    loadTable(self,dataframe, header_line)
    
def loadTable(self, dataframe, header_line):
    # Clear the table before populating it
    self.csvTable.clear()
    self.csvTable.setRowCount(dataframe.shape[0])
    self.csvTable.setColumnCount(dataframe.shape[1])
    
    # Set table headers
    if header_line >= 0:
        self.csvTable.setHorizontalHeaderLabels(dataframe.columns)
    else:
        self.csvTable.setHorizontalHeaderLabels([f'C{i+1}' for i in range(dataframe.shape[1])])
    
    # Populate the table with data
    for row in range(dataframe.shape[0]):
        for col in range(dataframe.shape[1]):
            self.csvTable.setItem(row, col, QTableWidgetItem(str(dataframe.iat[row, col])))
            
def plotCSV_ViewData(self):
    x_col = self.CSV_X_plot.currentText()
    y_col = self.CSV_Y_plot.currentText()

    if not x_col or not y_col:
        return  # Ensure columns are selected

    # Get column indices based on selected column names
    x_index = self.csvTable.horizontalHeaderItem(self.CSV_X_plot.currentIndex()).text()
    y_index = self.csvTable.horizontalHeaderItem(self.CSV_Y_plot.currentIndex()).text()

    # Extract data from the table widget
    x_data = []
    y_data = []
    for row in range(self.csvTable.rowCount()):
        x_item = self.csvTable.item(row, self.CSV_X_plot.currentIndex())
        y_item = self.csvTable.item(row, self.CSV_Y_plot.currentIndex())
        if x_item and y_item:
            x_data.append(float(x_item.text()))
            y_data.append(float(y_item.text()))

    if not hasattr(self, 'plot_fig'):
        self.plot_fig = Figure()  # Create a figure for the first time

    # Clear the plot if the checkbox is not checked
    if not self.cvs_add_plot.isChecked():
        self.plot_fig.clear()

    ax = self.plot_fig.add_subplot(111) if not self.cvs_add_plot.isChecked() else self.plot_fig.gca()

    # Set plot background to transparent
    ax.patch.set_alpha(0.0)
    self.plot_fig.patch.set_alpha(0.0)

    # Customize text and axes properties
    ax.tick_params(colors='white', labelsize=14)  # White ticks with larger text
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')

    # Plot the data
    ax.plot(x_data, y_data, label=f'{x_col} vs {y_col}')
    ax.legend(edgecolor='white')
    # Create a canvas and toolbar
    canvas = FigureCanvas(self.plot_fig)
    canvas.setStyleSheet("background-color:transparent;")
    toolbar = NavigationToolbar(canvas, self)

    # Check if the container has a layout, set one if not
    container = self.CVS_Ax_View
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

def CSV_apply_oper(self):
    operation = self.operation_list_csv.currentText()  # Assuming your combo box is named operationComboBox
    x_col     = self.CSV_X_plot.currentText()
    y_col     = self.CSV_Y_plot.currentText()
    value     = self.CSV_Oper_Value.value()  # Assuming you have a spin box named csv_spin_box
    
    if not x_col or not y_col:
        return  # Ensure columns are selected

    # Get column indices based on selected column names
    x_index = getColumnIndexByName(self,x_col)
    y_index = getColumnIndexByName(self,y_col)

    if operation == "Swap":
        swapColumns(self,x_index, y_index)
    elif operation == "Copy":
        copyColumn(self,x_index, y_index)
    elif operation == "Add Column":
        addColumn(self)
    else:
        applyOperation(self,x_index, operation, value)

def getColumnIndexByName(self, column_name):
    for i in range(self.csvTable.columnCount()):
        if self.csvTable.horizontalHeaderItem(i).text() == column_name:
            return i
    return None

def swapColumns(self, x_index, y_index):
    for row in range(self.csvTable.rowCount()):
        x_item = self.csvTable.item(row, x_index)
        y_item = self.csvTable.item(row, y_index)
        if x_item and y_item:
            x_value = x_item.text()
            y_value = y_item.text()
            self.csvTable.setItem(row, x_index, QTableWidgetItem(y_value))
            self.csvTable.setItem(row, y_index, QTableWidgetItem(x_value))

def copyColumn(self, x_index, y_index):
    for row in range(self.csvTable.rowCount()):
        x_item = self.csvTable.item(row, x_index)
        if x_item:
            x_value = x_item.text()
            self.csvTable.setItem(row, y_index, QTableWidgetItem(x_value))

def applyOperation(self, x_index, operation, value):
    for row in range(self.csvTable.rowCount()):
        x_item = self.csvTable.item(row, x_index)
        if x_item:
            x_value = float(x_item.text())
            if operation == "Add/Subtract":
                new_value = x_value + value  # You can handle subtract similarly
            elif operation == "Multiply":
                new_value = x_value * value
            elif operation == "Divide":
                if value != 0:
                    new_value = x_value / value
                else:
                    new_value = 0  # Handle divide by zero error
            elif operation == "Log":
                if x_value > 0:
                    new_value = np.log(x_value)
                else:
                    new_value = float('nan')  # Handle log of non-positive number
            elif operation == "Exp.":
                new_value = np.exp(x_value)
            elif operation == "Up.Thresh":
                if x_value > value:
                   new_value = value
                else: 
                   new_value = x_value
            elif operation == "Lw.Thresh":
                if x_value < value:
                   new_value = value
                else: 
                   new_value = x_value
            self.csvTable.setItem(row, x_index, QTableWidgetItem(str(new_value)))
            
def addColumn(self):
    # Determine the new column index and name
    new_col_index = self.csvTable.columnCount()
    new_col_name = f"C{new_col_index + 1}"

    # Add a new column to the table
    self.csvTable.insertColumn(new_col_index)
    self.csvTable.setHorizontalHeaderItem(new_col_index, QTableWidgetItem(new_col_name))

    # Populate the new column with empty items
    for row in range(self.csvTable.rowCount()):
        self.csvTable.setItem(row, new_col_index, QTableWidgetItem(""))
    
    #
    self.CSV_X_plot.addItem(new_col_name)
    self.CSV_Y_plot.addItem(new_col_name)
        
def exp_csv2_gcode(self):
    # Prompt user to select a folder
    folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
    if not folder_path:
        return  # User canceled, exit the function

    # Get the file name and number of columns
    file_name = self.gcode_f_name.text()
    num_columns = self.gcode_col.value()
    
    # Ensure the number of columns is at least 2
    if num_columns < 2:
        num_columns = 2
    
    # Prepare the file path
    file_path = os.path.join(folder_path, file_name + ".csv")
    
    # Extract data from the table widget
    data = {}
    for col in range(num_columns):
        column_name = self.csvTable.horizontalHeaderItem(col).text()
        data[column_name] = []
        for row in range(self.csvTable.rowCount()):
            item = self.csvTable.item(row, col)
            if item:
                data[column_name].append(float(item.text()))
    
    # Convert data to DataFrame
    df = pd.DataFrame(data)
    
    # Convert the time column to TimedeltaIndex for resampling
    time_col = df.columns[0]
    df[time_col] = pd.to_timedelta(df[time_col], unit='s')
    
    # Create a new index for resampling at 0.1s intervals
    new_index = pd.timedelta_range(start=df[time_col].min(), end=df[time_col].max(), freq='10L')
    
    # Reindex the DataFrame to the new index, keeping original data points
    df = df.set_index(time_col).reindex(new_index.union(df[time_col])).sort_index()
    
    # Interpolate only the missing values
    df = df.interpolate(method='linear', limit_area='inside')
    
    # Ensure the original time points are not modified
    df.loc[df.index.isin(new_index) == False, :] = df.loc[df.index.isin(new_index) == False, :].fillna(method='ffill').fillna(method='bfill')
    
    df.reset_index(inplace=True)
    df.rename(columns={'index': time_col}, inplace=True)
    
    # Calculate velocity and acceleration for each column
    results = pd.DataFrame()
    results[time_col] = df[time_col].dt.total_seconds()
    axis_labels = ['X', 'Y', 'Z', 'U', 'W']  # Define axis labels
    # N_repetitions
    num_repetitions = self.gcode_cycles.value()
    # Write G-code file
    for col in df.columns[1:]:
        results[col] = df[col]
        # Calculate average speed
        vel = df[col].diff().shift(-1) / df[time_col].diff().shift(-1).dt.total_seconds()
        vel.iloc[-1] = vel.iloc[-2]  # Copy the second last value to the last element
        results[f'{col}_vel'] = vel
        
        # Calculate acceleration
        accel = vel.diff() / df[time_col].diff().dt.total_seconds()
        accel.iloc[-1] = accel.iloc[-2]  # Copy the second last value to the last element
        results[f'{col}_accel'] = accel
    #       
    for _ in range(num_repetitions):
        # Write the results to the file
        if _ == 0:
            results.to_csv(file_path, index=False, mode='w')
        else:
            results.to_csv(file_path, index=False, mode='a', header=False)
    print(f"Exported data to {file_path}")
    #
    gcode_file_path = os.path.join(folder_path, file_name + ".gcode")
    gcode_lines = ["G90"]  # Initialize G-code lines with absolute positioning command
    # Write G-code file
    for _ in range(num_repetitions):
        for i, row in results.iterrows():
            if i == 0:
                continue  # Skip the first row for G-code generation
            # Calculate speed in mm per minute
            speed = abs(row[f'{df.columns[1]}_vel'] * 60)  # Convert m/s to mm/min
            # Prepare G-code line
            gcode_line = f"G0 F{speed:.6f}"
            for j, col in enumerate(df.columns[1:num_columns]):
                if j < len(axis_labels):
                    gcode_line += f" {axis_labels[j]}{row[col]:.6f}"  # X, Y, Z, U, W
                else:
                    gcode_line += f" {chr(85 + j)}{row[col]:.6f}"  # Continue with U, V, W, etc. if more than 5 columns
            gcode_lines.append(gcode_line)

    # Write G-code lines to the file
    with open(gcode_file_path, 'w') as gcode_file:
        gcode_file.write('\n'.join(gcode_lines))

    print(f"Generated G-code file at {gcode_file_path}")