from tkinter import filedialog
import os
import pandas as pd
from PySide6.QtWidgets import QFileDialog
from PySide6 import QtCore
from PySide6.QtCore import Qt
import pandas as pd

# Global variables to store file paths
gammex_path = None
reference_path = None

from fcn_3DPrinting.material_selection import (
    give_tissues,
    find_best_matching_filament,
    RED_or_RED_and_infill
)

class PandasModel(QtCore.QAbstractTableModel):
    """Interface a pandas DataFrame with Qt's QTableView."""
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._data = df

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Vertical:
                return str(self._data.index[section])
        return None

def import_reference_file(self):
    global reference_path
    file_path = filedialog.askopenfilename(title="Select Reference File")
    if file_path:
        self.reference_path = file_path
        # print(f"Reference file loaded: {reference_path}")
        # self.result_text.append(f"Reference file loaded:\n{reference_path}")
        tissues = give_tissues(file_path)
        self.tissue_combo.clear()
        self.tissue_combo.addItems(tissues)
        self.tissue_combo.setEnabled(True)

def load_gammex_file(self):
    path, _ = QFileDialog.getOpenFileName(self, "Select filament metrics file")
    if path:
        self.gammex_path = path
        # self.tissue_combo.clear()
        # self.tissue_combo.addItems(tissues)
        # self.tissue_combo.setEnabled(True)

def load_cal_file(self):
    path, _ = QFileDialog.getOpenFileName(self, "Select calibration matrix file")
    if path:
        self.cal_mat_path = path
        try:
            df = pd.read_excel(path)
            filaments = df['Filament'].dropna().unique().tolist()
            self.filament_combo.clear()
            self.filament_combo.addItems(filaments)
            self.filament_combo.setEnabled(True)
        except Exception as e:
            self.result_text2.setPlainText(f"Error loading file: {e}")

def show_best_matching_filaments(self):
    tissue = self.tissue_combo.currentText()

    result = find_best_matching_filament(self.reference_path, self.gammex_path, tissue)

    # Convert result['closest filaments'] into a DataFrame if it isn’t one yet
    if isinstance(result['closest filaments'], pd.DataFrame):
        df = result['closest filaments']
    else:
        # Fallback: assume it's a list of dicts or similar
        df = pd.DataFrame(result['closest filaments'])

    # Create a model for the QTableView
    model = PandasModel(df)
    self.tableView_filaments.setModel(model)



def calculate_red(self):
    filament = self.filament_combo.currentText()
    tissue = self.tissue_combo.currentText()

    # # Input validation
    # if not filament or not tissue:
    #     self.result_text2.setPlainText(" Please select filament and tissue type.")
    #     return

    input1 = "Flow and Infill" if self.radio_flow_infill.isChecked() else "Flow"
    input2 = "Extrapolate" if self.radio_extrap.isChecked() else "No"

    
    # Run your RED calculation
    result = RED_or_RED_and_infill(
        input1=input1,
        input2=input2,
        cal_mat_file_path=self.cal_mat_path,
        ref_file_path=self.reference_path,
        filament=filament,
        ref_tissue=tissue
    )

    # Prepare a table-friendly DataFrame
    data = {
        "Filament": [filament],
        "Tissue": [tissue],
        "Optimized RED": [result.get("found_red", "—")],
        "Z_eff": [result.get("mean_zeff", "—")],
        "Flow": [result.get("found_flow", "—")],
        "Infill": [result.get("found_infill", "n/a" if input1 == "Flow" else "—")],
    }

    df = pd.DataFrame(data)

    # Apply DataFrame to QTableView
    model = PandasModel(df)
    self.tableView_red.setModel(model)



# if __name__ == "__main__":

    # path, _ = QFileDialog.getOpenFileName(self, "Select filament metrics file")
