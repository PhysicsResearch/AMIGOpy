# calibration module functions
import csv
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QFileDialog
from PyQt5.QtGui import QColor, QBrush
import os



def load_referencecsv_into_table(self):
    # Construct the file path for the default CSV file
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory where the program is located
    file_name = "IrIS_ref_phys_markers.csv"  # Default CSV file name
    default_csv_path = os.path.join(base_dir, file_name)

    # Check if the file exists before proceeding
    if os.path.isfile(default_csv_path):
        with open(default_csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row

            # Clear existing table data before loading new data
            self.IrIS_cal_ref_table.setRowCount(0)

            for row_data in reader:
                row = self.IrIS_cal_ref_table.rowCount()
                self.IrIS_cal_ref_table.insertRow(row)
                for column in range(min(3, len(row_data))):  # Assume at least 3 columns of interest
                    self.IrIS_cal_ref_table.setItem(row, column, QTableWidgetItem(row_data[column]))

            # Ensure the table shows at least 6 columns, adjusting if necessary
            if self.IrIS_cal_ref_table.columnCount() < 7:
                self.IrIS_cal_ref_table.setColumnCount(7)
    else:
        print("Default reference markers file not found:", default_csv_path)
        # Optionally, display a message box or another form of notification to the user

def load_csv_into_table(self):
    # Open dialog to select CSV file
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)", options=options)
    if file_name:
        with open(file_name, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row

            # Clear existing table data before loading new data
            self.IrIS_cal_ref_table.setRowCount(0)

            for row_data in reader:
                row = self.IrIS_cal_ref_table.rowCount()
                self.IrIS_cal_ref_table.insertRow(row)
                for column in range(min(4, len(row_data))):  # Populate up to 4 columns
                    self.IrIS_cal_ref_table.setItem(row, column, QTableWidgetItem(row_data[column]))

        # Ensure the table shows at least 6 columns, adjusting if necessary
        if self.IrIS_cal_ref_table.columnCount() < 7:
            self.IrIS_cal_ref_table.setColumnCount(7)
    #set_color_for_column3_equals_1(self)

def load_csv_ref_pro(self):        
    # Open dialog to select CSV file
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)", options=options)
    if file_name:
        with open(file_name, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            # Initialize columns 4 and 5 with zeros for all potentially affected rows
            for row_index in range(self.IrIS_cal_ref_table.rowCount()):
                self.IrIS_cal_ref_table.setItem(row_index, 3, QTableWidgetItem("0"))
                self.IrIS_cal_ref_table.setItem(row_index, 4, QTableWidgetItem("0"))
                self.IrIS_cal_ref_table.setItem(row_index, 5, QTableWidgetItem("0"))
                self.IrIS_cal_ref_table.setItem(row_index, 6, QTableWidgetItem("0"))
            
            for row_data in reader:
                if len(row_data) < 3:  # Check for minimum required data length
                    continue
                
                try:
                    table_row_index = int(row_data[0]) - 1
                    # Ensure the table has enough rows
                    while self.IrIS_cal_ref_table.rowCount() <= table_row_index:
                        self.IrIS_cal_ref_table.insertRow(self.IrIS_cal_ref_table.rowCount())
    
                    # Set data in columns 4 and 5
                    self.IrIS_cal_ref_table.setItem(table_row_index, 3, QTableWidgetItem(row_data[1]))
                    self.IrIS_cal_ref_table.setItem(table_row_index, 4, QTableWidgetItem(row_data[2]))
                except ValueError:
                    continue
    
        # Fill empty cells in columns 4 and 5 with "0" after all rows are processed
        for row_index in range(self.IrIS_cal_ref_table.rowCount()):
            for column_index in [3, 4]:
                if not self.IrIS_cal_ref_table.item(row_index, column_index):
                    self.IrIS_cal_ref_table.setItem(row_index, column_index, QTableWidgetItem("0"))
        
        # Ensure the table shows at least 6 columns, adjusting if necessary
        if self.IrIS_cal_ref_table.columnCount() < 7:
            self.IrIS_cal_ref_table.setColumnCount(7)
    set_color_for_column3_equals_1(self)

def set_color_for_column3_equals_1(self):
    for row in range(self.IrIS_cal_ref_table.rowCount()):
        ref_mk_x  = float(self.IrIS_cal_ref_table.item(row, 3).text())  
        ref_mk_y  = float(self.IrIS_cal_ref_table.item(row, 4).text())  
        if ref_mk_x  > 0 and ref_mk_y  > 0 :
            for column_index in range(self.IrIS_cal_ref_table.columnCount()):
                item = self.IrIS_cal_ref_table.item(row, column_index) or QTableWidgetItem()
                item.setBackground(QBrush(QColor(100, 149, 237)))  # Medium (cornflower) blue
                item.setForeground(QBrush(QColor(255, 255, 255)))  # White
                self.IrIS_cal_ref_table.setItem(row, column_index, item)