from fcn_IrIS.source_activity_time import update_reference_time_table
from PyQt5.QtWidgets import QTableWidgetItem
import os
import csv

def load_Source_cal_csv_file(self):
    # Construct the file path for the default CSV file
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory where the program is located
    file_name = "Source_Cal.csv"  # Default CSV file name
    default_csv_path = os.path.join(base_dir, file_name)
    
    # Check if the file exists before proceeding
    print('Loading source calibration file')
    if os.path.isfile(default_csv_path):
        try:
            with open(default_csv_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header row

                # Clear existing table data before loading new data
                self.Source_Cal_table.setRowCount(0)

                for row_data in reader:
                    row = self.Source_Cal_table.rowCount()
                    self.Source_Cal_table.insertRow(row)
                    for column in range(len(row_data)):  # Load all columns in the row
                        self.Source_Cal_table.setItem(row, column, QTableWidgetItem(row_data[column].strip()))
        except Exception as e:
            print("Failed to read the file:", e)
    else:
        print("Default source calibration file not found:", default_csv_path)
    update_reference_time_table(self)