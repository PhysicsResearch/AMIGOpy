# -*- coding: utf-8 -*-

from fcn_DECT.constants import ATOMIC_NUMBER_TO_SYMBOL
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
import csv, math
from PyQt5.QtGui         import QColor, QBrush
from PyQt5.QtCore        import Qt
from fcn_materialassignment.material_map import update_material_list

SYMBOL_TO_ATOMIC_NUMBER = {v: k for k, v in ATOMIC_NUMBER_TO_SYMBOL.items()}

def create_dataframe_materials(self):
    # Open file dialog to select a CSV file

    filename = 'fcn_materialassignment/materials_db.csv'

    #
    data = []
    additional_tags = ['Den', 'RED', 'SPR','Tissue']
    all_columns = set(additional_tags)
    

    with open(filename, 'r') as file:
        for line in file:
            if not line.startswith('#'):
                data.append(line.strip().split(','))

    rows_list = []
    for idx,row in enumerate(data):
        row_data = {'Name': row[0]}
        i = 1
        while i < len(row):
            key = row[i].strip()
            if key.isdigit():
                atomic_number = int(key)
                symbol = ATOMIC_NUMBER_TO_SYMBOL.get(atomic_number, str(atomic_number))
                all_columns.add(symbol)
                mass_fraction = float(row[i + 1])
                row_data[symbol] = mass_fraction
                i += 2
            else:
                tag = key
                if i + 1 < len(row):
                    value = float(row[i + 1]) if row[i + 1].replace('.', '', 1).isdigit() else row[i + 1]
                    row_data[tag] = value
                i += 2
        rows_list.append(row_data)

    # Sorting columns by atomic number
    column_order = ['Name'] + sorted(
        [col for col in all_columns if col not in additional_tags + ['Name']],
        key=lambda x: list(ATOMIC_NUMBER_TO_SYMBOL.values()).index(x) if x in ATOMIC_NUMBER_TO_SYMBOL.values() else float('inf')
    ) + [col for col in additional_tags if col in all_columns]

    df = pd.DataFrame(rows_list, columns=column_order)
    df.fillna(0, inplace=True)
    print(df)
    return df


def update_mat_table_style(self):
    num_rows = self.mat_table.rowCount()
    num_columns = self.mat_table.columnCount()
    for i in range(num_rows):
        for j in range(num_columns):
            tableWidgetItem = self.mat_table.item(i, j)
            if tableWidgetItem is None:  # Create item if it does not exist
                tableWidgetItem = QTableWidgetItem()
                self.mat_table.setItem(i, j, tableWidgetItem)

            # Set text color to white
            tableWidgetItem.setForeground(QBrush(QColor(255, 255, 255)))

            # Set background color based on column index
            if j >= num_columns - 2:
                tableWidgetItem.setBackground(QBrush(QColor(0, 128, 255)) if j % 2 == 0 else QBrush(QColor(102, 0, 204)))
            elif j >= num_columns - 7:
                tableWidgetItem.setBackground(QBrush(QColor(255, 51, 153)) if j % 2 == 0 else QBrush(QColor(255, 102, 178)))
            elif j == 0:
                tableWidgetItem.setBackground(QBrush(QColor(255, 0, 127)))
            else:
                tableWidgetItem.setBackground(QBrush(QColor(0, 128, 255)) if j % 2 == 0 else QBrush(QColor(102, 0, 204)))
            # If it's not the first column, centralize the text
            if j != 0:
                tableWidgetItem.setTextAlignment(Qt.AlignCenter)
            

def update_mat_properties_table(self,df):
    self.Mat_df =df;
    # Check if Mat_df is None
    if self.Mat_df is None:
        return
    self.mat_table.setRowCount(len(self.Mat_df))
    self.mat_table.setColumnCount(len(self.Mat_df.columns))
    # Setting the column headers
    self.mat_table.setHorizontalHeaderLabels(self.Mat_df.columns)
    num_columns = len(self.Mat_df.columns)
    for i in range(len(self.Mat_df)):
        for j in range(num_columns):
            item = str(self.Mat_df.iloc[i, j])
            tableWidgetItem = QTableWidgetItem(item) 
            self.mat_table.setItem(i, j, tableWidgetItem)
    update_material_list(self)   
    
def add_mat_row(self):
    # Getting the current row count
    currentRowCount = self.mat_table.rowCount()
    
    # Inserting a new row at the end of the table
    self.mat_table.insertRow(currentRowCount)
    
    # Setting the text of the first item in the new row to "New Material and add the new ID"
    newItem = QTableWidgetItem("New Material")
    self.mat_table.setItem(currentRowCount, 0, newItem)

    
    # Optionally, fill the remaining cells in the new row with default values
    for j in range(1, self.mat_table.columnCount()):
        defaultItem = QTableWidgetItem(str(0))
        self.mat_table.setItem(currentRowCount, j, defaultItem)
    update_mat_table_style(self)  # Update the table style after removing the column
            
def del_mat_row(self):
    selected_indexes = self.mat_table.selectionModel().selectedRows()

    if selected_indexes:  # if any row is selected
        for index in sorted(selected_indexes, reverse=True):
            self.mat_table.removeRow(index.row())
    else:  # if no row is selected, remove the last row
        last_row = self.mat_table.rowCount() - 1
        if last_row >= 0:  # checking if there are any rows to remove
            self.mat_table.removeRow(last_row)
    update_mat_table_style(self)  # Update the table style after removing the column  

def add_element(self):
    # Getting the text from lineEdit
        text = self.element.text()
        # If the text is a digit, convert it to corresponding symbol
        if text.isdigit():
            atomic_number = int(text)
            text = ATOMIC_NUMBER_TO_SYMBOL.get(atomic_number, text)
            if text == str(atomic_number):  # If atomic_number not in the dictionary
                QMessageBox.critical(self, 'Error', 'Invalid atomic number!')
                return
        else:
            # Converting symbol to atomic number for comparison
            atomic_number_list = [k for k, v in ATOMIC_NUMBER_TO_SYMBOL.items() if v.upper() == text.upper()]
            if not atomic_number_list:  # If no atomic numbers found for the symbol
                QMessageBox.critical(self, 'Error', 'Invalid element symbol!')
                return
            atomic_number = atomic_number_list[0]
                    
        # Getting current column headers
        headers = [self.mat_table.horizontalHeaderItem(i).text() for i in range(self.mat_table.columnCount())]
        
        # Check if the column already exists
        if text in headers:
            # Optionally, show a message saying the column already exists
            QMessageBox.information(self, "Info", "Column already exists.")
            return  # Exit the function
        
        # Defining the range to search the position (from the second column until 7 columns before the end)
        search_range = range(1, len(headers) - 7)
        
        # Finding the correct position to insert new column
        position = None
        for i in search_range:
            current_header = headers[i]
            # Converting current header to atomic number for comparison
            current_atomic_number = [k for k, v in ATOMIC_NUMBER_TO_SYMBOL.items() if v == current_header][0]
            if atomic_number < current_atomic_number:
                position = i
                break
        
        if position is None:
            position = len(headers) - 4  # default to inserting 7 columns before the end if no position found
        
        # Inserting a new column at the found position
        self.mat_table.insertColumn(position)
        
        # Setting the header for the new column
        headers.insert(position, text)
        self.mat_table.setHorizontalHeaderLabels(headers)
        
        # Filling the new column with default values
        for i in range(self.mat_table.rowCount()):
            defaultItem = QTableWidgetItem(str(0))
            self.mat_table.setItem(i, position, defaultItem) 
        update_mat_table_style(self)

def del_element(self):
    # Getting the text from lineEdit
     text = self.element.text()

     # If the text is a digit, convert it to corresponding symbol
     if text.isdigit():
         atomic_number = int(text)
         text = ATOMIC_NUMBER_TO_SYMBOL.get(atomic_number, text)
         if not atomic_number:  # If no atomic numbers found for the symbol
            QMessageBox.critical(self, 'Error', 'Invalid element symbol!')
            return

     # Getting current column headers
     headers = [self.mat_table.horizontalHeaderItem(i).text() for i in range(self.mat_table.columnCount())]

     # Finding the index of the column to remove
     position = None
     for i, header in enumerate(headers):
         if header == text:
             position = i
             break
      # If the column is not found, show error message
     if position is None:
        QMessageBox.critical(self, 'Error', 'Element not found in the table!')
        return       
            
     # If the column is found, remove it
     if position is not None:
         self.mat_table.removeColumn(position)
         update_mat_table_style(self)  # Update the table style after removing the column

def save_mat_db(self):
    # Prompt user to select a folder

    # Get the data from the table
    row_count = self.mat_table.rowCount()
    column_count = self.mat_table.columnCount()


    def get_atomic_number(symbol):
        result = [k for k, v in ATOMIC_NUMBER_TO_SYMBOL.items() if v.upper() == symbol.upper()]
        return result[0] if result else None

    # Create a list to hold the data
    data = []

    # Add the custom label from QLineEdit if it doesn't start with #

    mat_table_label = "#Materials DB"
    data.append(mat_table_label)

    # Get the header labels
    header = [self.mat_table.horizontalHeaderItem(i).text() for i in range(column_count)]

    # Define the columns to be kept as is
    keep_as_is = ["Den", "RED",  "SPR", 'Tissue', ]

    # Construct the header row as specified
    header_row = "# Material Name, Atomic Number, Mass Fraction, Den, RED, SPR, HUlow, Tissue"
    data.append(header_row)

    # Get the table data
    for row in range(row_count):
        row_data = []
        for column in range(column_count):
            item = self.mat_table.item(row, column)
            cell_value = item.text() 
            column_label = header[column]

            if column == 0:  # First column is text
                row_data.append(cell_value)
            elif column_label in ATOMIC_NUMBER_TO_SYMBOL.values():
                atomic_number = get_atomic_number(column_label)
                if atomic_number is not None:
                    if float(cell_value) !=0:
                        row_data.append(f"{atomic_number}, {cell_value}")
                    else:
                        continue
                else:
                    row_data.append(cell_value)
            elif column_label in keep_as_is:
                row_data.append(f"{column_label}, {cell_value}")
            else:
                row_data.append(cell_value)

        data.append(", ".join(row_data))

    # Construct the file path
    file_path =  'fcn_materialassignment/materials_db.csv'

    try:
        # Write the data to a CSV file manually to avoid quotes
        with open(file_path, mode='w', newline='') as file:
            for row in data:
                file.write(row + '\n')
        #Reload updated db and update material df
        df=create_dataframe_materials(self)
        update_mat_properties_table(self,df)
        update_mat_table_style(self)
        QMessageBox.information(self, "Success", "Data saved")
        print(self.Mat_df)
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")
        

            