import numpy as np
import vtk
from copy import deepcopy
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, 
    QWidget, QLineEdit, QLabel, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem,QHeaderView, QInputDialog, QMessageBox)

from PyQt5.QtCore import Qt  # Import Qt to use Qt.ItemIsEditable flag
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import pandas as pd


def init_ct_cal_table(self):
    self.ct_cal_table.setRowCount(6)
    self.ct_cal_table.setColumnCount(2)
    self.ct_cal_table.clear()
    item0=QTableWidgetItem('HU')
    item0.setTextAlignment(Qt.AlignCenter)
    item0.setFlags(item0.flags() & ~Qt.ItemIsEditable)  # Make (0, 0) uneditable
    self.ct_cal_table.setItem(0, 0, item0)
    item1 = QTableWidgetItem('DENSITY')
    item1.setTextAlignment(Qt.AlignCenter)
    self.ct_cal_table.setItem(0, 1, item1)  # Editable by default
    # Add 5 empty editable rows below the header
    for row in range(1, 6):
        for col in range(6):
            empty_item = QTableWidgetItem("")
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.ct_cal_table.setItem(row, col, empty_item)
    

def add_row_to_ct_table(self):
    current_rows = self.ct_cal_table.rowCount()
    self.ct_cal_table.insertRow(current_rows)  # Add a new row at the bottom
    
    # Insert empty, centered items into each column of the new row
    for col in range(self.ct_cal_table.columnCount()):
        item = QTableWidgetItem("")
        item.setTextAlignment(Qt.AlignCenter)
        self.ct_cal_table.setItem(current_rows, col, item)
        
def validate_ct_cal_headers(self, data_ct_cal):
    # Force all column names to uppercase
    data_ct_cal.columns = [col.upper() for col in data_ct_cal.columns]
    headers = data_ct_cal.columns.tolist()

    # Check that there are exactly two columns
    if len(headers) != 2:
        QMessageBox.warning(self, "Invalid Format", "File must contain exactly two columns.")
        return None

    # First column must be 'HU'
    if headers[0] != 'HU':
        QMessageBox.warning(self, "Invalid Format", "The first column must be 'HU'.")
        return None

    # Second column must be 'A', 'B', or 'C'
    possible_headers=['DENSITY','RED','SPR']
    while headers[1] not in possible_headers:
        # Ask user to rename the second column
        text, ok = QInputDialog.getText(
            self, "Rename Column",
            f"Second column name '{headers[1]}' is invalid.\nEnter 'DENSITY', 'RED', or 'SPR':"
        )
        if not ok:
            return None  # User canceled
        if text.upper() in possible_headers:
            data_ct_cal.columns = ['HU', text.upper()]
            return data_ct_cal
        else:
            QMessageBox.warning(self, "Invalid Input", "Please enter 'DENSITY', 'RED', or 'SPR'.")

    return data_ct_cal

def load_ct_cal_curve(self):
    options = QFileDialog.Options()
    fileName, _ = QFileDialog.getOpenFileName(self, "Open the CT calibration curve ", "", "CSV Files (*.csv);;All Files (*)", options=options)
    if not fileName:
        return  # user canceled

    # Detect delimiter by reading the first non-header line
    with open(fileName, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if len(lines) < 2:
            return  # file too short or empty
        delimiter = ',' if ',' in lines[1] else ';'
    data_ct_cal=pd.read_csv(fileName,skiprows=[0],delimiter=delimiter)
    #Checking the headers
    validated_data = validate_ct_cal_headers(self,data_ct_cal)
    if validated_data is None:
        return  # User cancelled or headers invalid
    # Proceed with validated_data
    ct_cal_name=fileName.split('/')[-1].split('.')[0]
    i=1
    while ct_cal_name in self.ct_cal_curves.keys():
        if i>1:
            splitted_name=ct_cal_name.split('_')
            if len(splitted_name)>1:
                ct_cal_name='_'.join(splitted_name[:len(splitted_name)-1])
            else:
                ct_cal_name=splitted_name[0]
        ct_cal_name=f'{ct_cal_name}_{i}'
        i=i+1
    self.ct_cal_curves[ct_cal_name]=validated_data
    update_ct_cal_list(self)
    
    
    
def update_ct_cal_list(self):
    self.ct_cal_list.clear()
    names=[k for k in self.ct_cal_curves.keys()]
    self.ct_cal_list.addItems(['<New...>'])
    self.ct_cal_list.addItems(names)


def update_ct_cal_table(self,ct_cal_data):
    self.ct_cal_table.clear()

    n_rows, n_cols = ct_cal_data.shape
    self.ct_cal_table.setRowCount(n_rows+1)
    self.ct_cal_table.setColumnCount(n_cols)
    
    # Set column headers (e.g., 'HU', 'Density', etc.)
    header = ct_cal_data.columns.tolist()
    item0 = QTableWidgetItem(header[0])
    item0.setTextAlignment(Qt.AlignCenter)
    item0.setFlags(item0.flags() & ~Qt.ItemIsEditable)  # Make (0, 0) uneditable
    self.ct_cal_table.setItem(0, 0, item0)

    item1 = QTableWidgetItem(header[1])
    item1.setTextAlignment(Qt.AlignCenter)
    self.ct_cal_table.setItem(0, 1, item1)  # Editable by default

    # Loop through all rows and columns to make all cells editable
    for row in range(n_rows):
        for col in range(n_cols):
            item = QTableWidgetItem(str(ct_cal_data.iloc[row, col]))
            item.setTextAlignment(Qt.AlignCenter)
            self.ct_cal_table.setItem(row+1, col, item)

    self.ct_cal_table.horizontalHeader().setVisible(False)
    self.ct_cal_table.verticalHeader().setVisible(False)

def plot_ct_cal(self, ct_cal_data):
    # Clean up previous figure, canvas, and toolbar
    if hasattr(self, 'fig_ct_cal') and self.fig_ct_cal:
        plt.close(self.fig_ct_cal)
    if hasattr(self, 'canvas_ct_cal') and self.canvas_ct_cal:
        self.canvas_ct_cal.deleteLater()
    if hasattr(self, 'toolbar_ct_cal') and self.toolbar_ct_cal:
        self.toolbar_ct_cal.deleteLater()

    # Create new figure and axes
    self.fig_ct_cal, self.ax_ct_cal = plt.subplots()

    # Apply transparency settings to Matplotlib figure
    if self.selected_background == "Transparent":
        self.ax_ct_cal.patch.set_alpha(0.0)
        self.fig_ct_cal.patch.set_alpha(0.0)

        self.ax_ct_cal.tick_params(colors='white', labelsize=self.selected_font_size - 2)
        self.ax_ct_cal.xaxis.label.set_color('white')
        self.ax_ct_cal.yaxis.label.set_color('white')
        for spine in self.ax_ct_cal.spines.values():
            spine.set_color('white')
    else:
        self.ax_ct_cal.tick_params(labelsize=self.selected_font_size - 2)

    # Plot data
    headers = ct_cal_data.columns.tolist()
    HU = ct_cal_data['HU']
    density = ct_cal_data[headers[1]]
    self.ax_ct_cal.plot(HU, density)
    self.ax_ct_cal.set_xlabel('HU', fontsize=self.selected_font_size)
    y_label=headers[1]
    if y_label=='DENSITY':
        y_label=f'{y_label} (g/$cm^3$)'
    self.ax_ct_cal.set_ylabel(y_label, fontsize=self.selected_font_size)

    title_kwargs = {'fontsize': self.selected_font_size + 4}
    if self.selected_background == "Transparent":
        title_kwargs['color'] = 'white'
    self.fig_ct_cal.suptitle(f"HU vs {headers[1]}", **title_kwargs)

    # Create canvas and toolbar
    self.canvas_ct_cal = FigureCanvas(self.fig_ct_cal)
    self.toolbar_ct_cal = NavigationToolbar(self.canvas_ct_cal, self)

    # Apply transparency to canvas and container
    if self.selected_background == "Transparent":
        for widget in [self.canvas_ct_cal, self.ct_cal_plot]:
            widget.setAttribute(Qt.WA_TranslucentBackground)
            widget.setAutoFillBackground(False)
            widget.setStyleSheet("background-color: transparent;")
    else:
        self.canvas_ct_cal.setStyleSheet(f"background-color:{self.selected_background};")

    # Ensure container has a layout
    container = self.ct_cal_plot
    if container.layout() is None:
        layout = QVBoxLayout(container)
        container.setLayout(layout)
    else:
        # Clear existing content in layout
        while container.layout().count():
            child = container.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # Add toolbar and canvas to layout
    container.layout().addWidget(self.toolbar_ct_cal)
    container.layout().addWidget(self.canvas_ct_cal)
    self.canvas_ct_cal.draw()


            
    
def update_ct_cal_view(self):
    selected_text = self.ct_cal_list.currentText()

    if selected_text == '<New...>':
        init_ct_cal_table(self)
    # If a previous plot exists, clear it
        if hasattr(self, 'fig_ct_cal') and self.fig_ct_cal:
            plt.close(self.fig_ct_cal)
            self.fig_ct_cal = None
        if hasattr(self, 'canvas_ct_cal') and self.canvas_ct_cal:
            self.canvas_ct_cal.deleteLater()
            self.canvas_ct_cal = None
        if hasattr(self, 'toolbar_ct_cal') and self.toolbar_ct_cal:
            self.toolbar_ct_cal.deleteLater()
            self.toolbar_ct_cal = None
    
        # Also clear the layout in the plot container
        container = self.ct_cal_plot
        if container.layout() is not None:
            while container.layout().count():
                child = container.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
    
        return  # Do not proceed to plot or update table with real data
    
    elif selected_text not in self.ct_cal_curves.keys():
        return 
    ct_cal_data=self.ct_cal_curves[selected_text]
    update_ct_cal_table(self, ct_cal_data)
    plot_ct_cal(self, ct_cal_data)



def export_ct_cal_to_csv(self):
    pass


def save_changes(self):
    row_count = self.ct_cal_table.rowCount()
    col_count = self.ct_cal_table.columnCount()

    # Extract header from the first row
    headers = []
    for col in range(col_count):
        item = self.ct_cal_table.item(0, col)
        headers.append(item.text() if item else f"Column{col}")

    # Extract data starting from row 1
    data = []
    for row in range(1, row_count):
        row_data = []
        for col in range(col_count):
            item = self.ct_cal_table.item(row, col)
            row_data.append(item.text() if item else "")
        data.append(row_data)

    # Convert to DataFrame
    df = pd.DataFrame(data, columns=headers)

    # Optional: Convert to numeric if needed
    df = df.apply(pd.to_numeric, errors='ignore')
    df=df.dropna()
    validate_df=validate_ct_cal_headers(self, df)
    #getting the current table name:
    table_name=self.ct_cal_list.currentText()
    if table_name=='<New...>':
        table_name='NewTable'
        i=1
        while table_name in self.ct_cal_curves.keys():
            if i>1:
                splitted_name=table_name.split('_')
                if len(splitted_name)>1:
                   table_name='_'.join(splitted_name[:len(splitted_name)-1])
                else:
                    table_name=splitted_name[0]
            table_name=f'{table_name}_{i}'
            i=i+1
    self.ct_cal_curves[table_name]=validate_df
    update_ct_cal_list(self)
    self.ct_cal_list.setCurrentText(table_name)
    update_ct_cal_view(self)

    
# def plot_ct_cal(self,ct_cal_data):
#     #cleaning all figures to free up memory
    
#     # Close the previous figure if it exists
#     if hasattr(self, 'fig_ct_cal') and self.fig_ct_cal:
#         plt.close(self.fig_ct_cal)  # Close the previous figure to release memory
#     # Check if previous canvas exists, and delete it
#     if hasattr(self, 'canvas_ct_cal') and self.canvas_ct_cal:
#         self.canvas_ct_cal.deleteLater()  # Delete the previous canvas
    
#     # Check if previous toolbar exists, and delete it
#     if hasattr(self, 'toolbar_ct_cal') and self.toolbar_ct_cal:
#         self.toolbar_ct_cal.deleteLater()  # Delete the previous toolbar
        

    
#     self.fig_ct_cal,self.ax_ct_cal=plt.subplots()
#     if self.selected_background == "Transparent":
#         # Set plot background to transparent
#         self.ax_ct_cal.patch.set_alpha(0.0)
#         self.fig_ct_cal.set_alpha(0.0)
        
#         # Customize text and axes properties
#         self.ax_ct_cal.tick_params(colors='white', labelsize=self.selected_font_size-2)  # White ticks with larger text
#         self.ax_ct_cal.xaxis.label.set_color('white')
#         self.ax_ct_cal.yaxis.label.set_color('white')
#         self.ax_ct_cal.spines['bottom'].set_color('white')
#         self.ax_ct_cal.spines['top'].set_color('white')
#         self.ax_ct_cal.spines['left'].set_color('white')
#         self.ax_ct_cal.spines['right'].set_color('white')
#     else:
#         self.ax_ct_cal.tick_params(labelsize=self.selected_font_size-2)  # White ticks with larger text
        
#     #plot the data
#     headers=ct_cal_data.columns.tolist()
#     HU=ct_cal_data['HU']
#     density=ct_cal_data[headers[1]]
#     self.ax_ct_cal.plot(HU,density)
#     self.ax_ct_cal.set_xlabel('HU', fontsize=self.selected_font_size)
#     self.ax_ct_cal.set_ylabel(headers[1], fontsize=self.selected_font_size)
    
#     if self.selected_background == "Transparent":
#         self.fig_ct_cal.suptitle(f"HU vs {headers[1]}", 
#                                fontsize=self.selected_font_size + 4,
#                                color="white")
#     else:
#         self.fig_ct_cal.suptitle(f"HU vs {headers[1]}", 
#                                fontsize=self.selected_font_size + 4)
    

#     # Create a canvas and toolbar
#     self.canvas_ct_cal = FigureCanvas(self.fig_ct_cal)
#     self.canvas_ct_cal.setStyleSheet(f"background-color:{self.selected_background};")
#     self.toolbar_ct_cal = NavigationToolbar(self.canvas_ct_cal, self)

#     # Check if the container has a layout, set one if not
#     container = self.ct_cal_plot
#     if container.layout() is None:
#         layout = QVBoxLayout(container)
#         container.setLayout(layout)
#     else:
#         # Clear existing content in the container, if any
#         while container.layout().count():
#             child = container.layout().takeAt(0)
#             if child.widget() and not isinstance(child.widget(), NavigationToolbar):
#                 child.widget().deleteLater()

#     # Add the canvas and toolbar to the container
#     container.layout().addWidget(self.toolbar_ct_cal)
#     container.layout().addWidget(self.canvas_ct_cal)
#     self.canvas_ct_cal.draw()