import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
import csv, math
from fcn_DECT.constants import ATOMIC_NUMBER_TO_SYMBOL


# Inverse the dictionary to map from symbol to atomic number
SYMBOL_TO_ATOMIC_NUMBER = {v: k for k, v in ATOMIC_NUMBER_TO_SYMBOL.items()}


def read_reference_csv(filename, key_column, value_column):
    """
    Reads a CSV file and returns a dictionary with keys and values based on specified columns.

    :param filename: the name of the CSV file to read.
    :param key_column: the column index for the dictionary keys.
    :param value_column: the column index for the dictionary values.
    :return: a dictionary representation of the CSV file.
    """
    data = {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # Ignoring lines that start with #
            if not row[key_column].startswith("#"):
                data[row[key_column]] = float(row[value_column])
    return data




def calculate_mat_par(self):
    """
    Get the data from self.MatInfoTable and convert it to a pandas DataFrame.

    :return: A pandas DataFrame containing the table data.
    """
    try:
        table = self.MatInfoTable
        column_count = table.columnCount()
        row_count = table.rowCount()
    
        # Getting the table column headers
        column_headers = []
        for i in range(column_count):
            item = table.horizontalHeaderItem(i)
            if item and item.text():
                column_headers.append(item.text())
            else:
                column_headers.append(f"Column {i+1}")
    
        # Getting the table data
        table_data = []
        for row in range(row_count):
            row_data = []
            for col in range(column_count):
                item = table.item(row, col)
                row_data.append(item.text() if item else None)
            table_data.append(row_data)
    
        # Creating DataFrame
        df = pd.DataFrame(table_data, columns=column_headers)
    
        # Reading the Reference_I_value.csv into Ivalues dictionary
        Ivalues = read_reference_csv('Reference_I_value.csv', 0, 1)
    
        # Reading the Reference_ZbyA.csv into ZbyA dictionary
        ZbyA = read_reference_csv('Reference_ZbyA.csv', 0, 1)
        
        # the last 7 colluns have info abou Den, RED, Zeff ... not composition
        selected_columns = df.columns[1:-7]
        # Convert selected columns to numeric
        df[selected_columns] = df[selected_columns].apply(pd.to_numeric, errors='coerce')
        # 
        # duplicate df to perform Zeff operations
        df_Z = df.copy();
        df_I = df.copy();
        # Check if the sum of each row in the selected columns adds up to 100
        for index, row in df[selected_columns].iterrows():
            row_sum = row.sum()
            if row_sum < 99.8 or row_sum > 100.2:
                # Show warning dialog
                QMessageBox.warning(None, 'Warning', f"Row {df.iat[index, 0]} does not sum to 100, adjusting values.")
            if row_sum != 100:
                # Normalize the values in the row to make the sum 100
                df.loc[index, selected_columns] = (row / row_sum) * 100
            
        # # RED Zeff I SPR
        #
        # Get Zeff^m so user can set different values for the equation
        Zeff_m_text = self.Zeff_m.text()
        
        try:
            # Try to convert the text to a float
            Zeff_m = float(Zeff_m_text)
        except ValueError:
            # If conversion fails, show an error message
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText("Error")
            error_dialog.setInformativeText('Please enter a valid number.')
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()
        #
        # Multiply the values in the selected columns by their corresponding  ZbyA
        for col in selected_columns:
            if col in ZbyA:
                df[col]   *= ZbyA[col]
                df_Z[col] *= (ZbyA[col] * np.power(SYMBOL_TO_ATOMIC_NUMBER.get(col, None),Zeff_m))
                df_I[col] *= (ZbyA[col] * math.log(Ivalues[col]))
        
    
    
        Zeff = df_Z[selected_columns].sum(axis=1)/df[selected_columns].sum(axis=1)
        Zeff = np.power(Zeff, 1/Zeff_m)
        Zeff = Zeff.round(2)
        # Now converting the series to a DataFrame
        Zeff = Zeff.to_frame(name='Zeff')
        # print(Zeff)
        if self.checkBox_cal_I.isChecked():
            Iv   = df_I[selected_columns].sum(axis=1)/df[selected_columns].sum(axis=1)
            Iv   = np.exp(Iv)
            Iv   = Iv.round(2)
            Iv   = Iv.to_frame(name='Iv')
        else:
            # If the checkBox_calRED is not checked, take the RED values from the 'RED' column in df
            Iv = df[['Iv']].copy()
            Iv['Iv'] = pd.to_numeric(Iv['Iv'], errors='coerce')  # Convert 'RED' column to float or appropriate dtype
        # #
        # Check the state of the checkBox_calRED
        if self.checkBox_calRED.isChecked():
            # Perform the RED calculation as you already have in the function
            RED  = df[selected_columns].sum(axis=1).to_frame(name='RED')
            # Divide each row in new_df by the corresponding row in the 'Den' column of df
            # Convert 'Den' column to float
            #
            # Check if 'Den' column exists and is not None
            if 'Den' not in df.columns or df['Den'].isnull().all():
                # Print the message in red using ANSI escape codes
                return
            df['Den'] = pd.to_numeric(df['Den'], errors='coerce')
            # 0.998 is the density of water
            df['Den'] =  df['Den'] / 0.998
            # it is divided by 100 since the mass fr
            # At the end where you are calculating RED
            RED['RED'] = RED['RED'] * df['Den'].values / 0.555085990000000 / 100
            RED['RED'] = RED['RED'].round(4)
        else:
            # If the checkBox_calRED is not checked, take the RED values from the 'RED' column in df
            RED = df[['RED']].copy()
            RED['RED'] = pd.to_numeric(RED['RED'], errors='coerce')  # Convert 'RED' column to float or appropriate dtype
    
        # ...
        Iv_transformed = Iv.applymap(lambda x: 12.16 - np.log(x))
        Iv_transformed = Iv_transformed / 7.838
        # Ensure both RED and Iv_transformed have the same shape
        SPR = RED.multiply(Iv_transformed['Iv'], axis=0)  # Use 'I' column from Iv_transformed to multiply with RED
        SPR = SPR.rename(columns={'RED': 'SPR'})
        SPR['SPR'] = SPR['SPR'].round(4)
        #
        # Assuming 'Zeff' and 'RED' columns exist 
        zeff_column_index = column_headers.index('Zeff')
        red_column_index  = column_headers.index('RED')
        i_column_index    = column_headers.index('Iv')
        spr_column_index  = column_headers.index('SPR')
        
    
        for row in range(row_count):
            if self.checkBox_calZeff.isChecked(): 
                zeff_item = QTableWidgetItem(str(Zeff.iloc[row, 0]))  # convert Zeff value to string
                table.setItem(row, zeff_column_index, zeff_item)      # set the Zeff value in the table
            if self.checkBox_calRED.isChecked(): 
                red_item = QTableWidgetItem(str(RED.iloc[row, 0]))    # convert RED value to string
                table.setItem(row, red_column_index, red_item)        # set the RED value in the table
            if self.checkBox_cal_I.isChecked():
                i_item = QTableWidgetItem(str(Iv.iloc[row, 0]))       # convert I value to string
                table.setItem(row, i_column_index, i_item)            # set the I value in the table
            if self.checkBox_calSPR.isChecked():
                spr_item = QTableWidgetItem(str(SPR.iloc[row, 0]))    # convert I value to string
                table.setItem(row, spr_column_index, spr_item)        # set the I value in the table

    except Exception as e:
            # If any other error occurs, show a general error dialog
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText("An error occurred")
            error_dialog.setInformativeText(str(e))
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()  
