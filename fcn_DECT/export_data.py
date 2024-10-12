from PyQt5.QtWidgets import QFileDialog, QMessageBox
import pandas as pd
from fcn_DECT.constants import ATOMIC_NUMBER_TO_SYMBOL
import csv 

       

def export_matinfotable_to_csv(self):
    # Prompt user to select a folder
    folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
    if not folder_path:
        return  # User canceled, exit the function

    # Get the data from the table
    row_count = self.MatInfoTable.rowCount()
    column_count = self.MatInfoTable.columnCount()


    def get_atomic_number(symbol):
        result = [k for k, v in ATOMIC_NUMBER_TO_SYMBOL.items() if v.upper() == symbol.upper()]
        return result[0] if result else None

    # Create a list to hold the data
    data = []

    # Add the custom label from QLineEdit if it doesn't start with #
    mat_table_label = self.mat_table_label.text()
    if not mat_table_label.startswith("#"):
        mat_table_label = f"#{mat_table_label}"
    data.append(mat_table_label)

    # Get the header labels
    header = [self.MatInfoTable.horizontalHeaderItem(i).text() for i in range(column_count)]

    # Define the columns to be kept as is
    keep_as_is = ["Den", "RED", "Zeff", "I", "SPR", "HUlow", "HUhigh"]

    # Construct the header row as specified
    header_row = "# Material Name, Atomic Number, Mass Fraction, Den, RED, Zeff, I, SPR, HUlow, HUhigh"
    data.append(header_row)

    # Get the table data
    for row in range(row_count):
        row_data = []
        for column in range(column_count):
            item = self.MatInfoTable.item(row, column)
            cell_value = item.text() if item is not None else ''
            column_label = header[column]

            if column == 0:  # First column is text
                row_data.append(cell_value)
            elif column_label in ATOMIC_NUMBER_TO_SYMBOL.values():
                atomic_number = get_atomic_number(column_label)
                if atomic_number is not None:
                    row_data.append(f"{atomic_number}, {cell_value}")
                else:
                    row_data.append(cell_value)
            elif column_label in keep_as_is:
                row_data.append(f"{column_label}, {cell_value}")
            else:
                row_data.append(cell_value)

        data.append(", ".join(row_data))

    # Construct the file path
    file_path = f"{folder_path}/dect_export_AMB.csv"

    try:
        # Write the data to a CSV file manually to avoid quotes
        with open(file_path, mode='w', newline='') as file:
            for row in data:
                file.write(row + '\n')
        QMessageBox.information(self, "Success", f"Data exported successfully to {file_path}")
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
        
        
    # export a second file which is easier for excel
    # Prompt user to select a folder
    # Create a list to hold the data
    data = []
    # Get the header labels
    header = [self.MatInfoTable.horizontalHeaderItem(i).text() for i in range(column_count)]
    data.append(header)

    # Get the table data
    for row in range(row_count):
        row_data = []
        for column in range(column_count):
            item = self.MatInfoTable.item(row, column)
            row_data.append(item.text() if item is not None else '')
        data.append(row_data)

    # Convert the data to a DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])

    # Construct the file path
    file_path = f"{folder_path}/dect_export.csv"
    try:
        # Save the DataFrame to a CSV file
        df.to_csv(file_path, index=False)
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")