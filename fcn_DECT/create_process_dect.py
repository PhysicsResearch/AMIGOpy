from fcn_load.populate_dcm_list import populate_DICOM_tree
from fcn_DECT.spr_calc_plot import calculate_beta
import copy
import pydicom
from pydicom.dataset import Dataset
from pydicom.dataelem import DataElement
import numpy as np
import csv
import os
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, QFileDialog,
    QWidget, QLineEdit, QLabel, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem, QMessageBox)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# Convert images to RED Zeff SPR and I-value
#
#
def creat_DECT_derived_maps(self):
    # Get HU_low
    if not hasattr(self, 'series_info_dict') or not self.series_info_dict:
        warning_box = QMessageBox()
        warning_box.setIcon(QMessageBox.Warning)
        warning_box.setWindowTitle("Warning")
        warning_box.setText('Calibration not loaded or missing parameters')
        warning_box.setStandardButtons(QMessageBox.Ok)
        warning_box.exec_()
        return
    selected_index_L = self.scatter_plot_im_01.currentIndex()
    series_label_L, patient_id_L, study_id_L, modality_L, item_index_L = self.series_info_dict[selected_index_L]      
    # Get HU_High
    selected_index_H = self.scatter_plot_im_02.currentIndex()
    series_label_H, patient_id_H, study_id_H, modality_H, item_index_H = self.series_info_dict[selected_index_H]      
    
    # Assuming the reference image is a 3D NumPy array
    reference_image_L = self.medical_image[patient_id_L][study_id_L][modality_L][item_index_L]['3DMatrix'].astype(np.float32)
    reference_image_H = self.medical_image[patient_id_H][study_id_H][modality_H][item_index_H]['3DMatrix'].astype(np.float32)
    
    im_c_01 = self.medical_image[patient_id_L][study_id_L][modality_L][item_index_L]['metadata']['ImageComments']
    im_c_02 = self.medical_image[patient_id_H][study_id_H][modality_H][item_index_H]['metadata']['ImageComments']
    Im_com  = (f"{im_c_01}_{im_c_02}")
    

    m_text = self.Zeff_m.text()
    m      = float(m_text)
    
    # calculate water Zeff
    # Z/A H = 0.99212 mass fraction 0.1111
    # Z/A 0 = 0.50002 mass fraction 0.8889
    
    Zeff_w = (((0.99212*0.1111*1**m) + (0.50002*0.8889*8**m)) / ((0.99212*0.1111) + (0.50002*0.8889)))**(1/m)
    
    
    # GET RED METHOD AND PARAMETERS
    selected_red_method = self.RED_method_list.currentText()
    if   selected_red_method == "Saito":
        # a, alpha and beta
        a_text     = self.RED_fit_01_text.text()
        a          = float(a_text)
        alpha_text = self.RED_fit_02_text.text()
        alpha      = float(alpha_text)
        b_text     = self.RED_fit_03_text.text()
        b          = float(b_text)
        
        Low        = (reference_image_L * alpha)*a/1000
        High       = (reference_image_H * (1+alpha))*a/1000
        RED_matrix = (High-Low+b)
        #
    elif   selected_red_method == "Hunemohr":
        ce_text     = self.RED_fit_01_text.text()
        ce           = float(ce_text)
        Low        = (reference_image_L/1000 + 1)
        High       = (reference_image_H/1000 + 1)
        RED_matrix = (Low*ce+High*(1-ce))
    #    
    RED_matrix  = np.nan_to_num(RED_matrix)
    if self.checkBox_Im_RED.isChecked():
        # copy the header of the low image ... in the future some tags will be adjusted
        original_data = self.medical_image[patient_id_L][study_id_L][modality_L][item_index_L].copy()
        # Ensure the list is long enough to accommodate new indices
        required_length = len(self.medical_image[patient_id_L][study_id_L][modality_L]) + 1
        while len(self.medical_image[patient_id_L][study_id_L][modality_L]) < required_length:
            self.medical_image[patient_id_L][study_id_L][modality_L].append(None)
        # Store data into new series indice
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]                              = copy.deepcopy(original_data)
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['3DMatrix']                  = RED_matrix.astype(np.float32)
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['SliceImageComments']        = 'RED Calculated AMB'
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['ImageComments'] = "RED Calculated AMB"
        image_comment = str('RED Calculated AMB')
        data_element = DataElement((0x0020, 0x4000), 'LO', image_comment)
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['DCM_Info']['ImageComments'] = data_element
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['LUTLabel'] = 'Calculated RED'
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['LUTLabel'] = (f"RED {Im_com}")
        #
        #
        
    # GET Zeff METHOD AND PARAMETERS
    selected_zeff_method = self.Zeff_method_list.currentText()
    if   selected_zeff_method == "Saito":
        g_text       = self.Zeff_fit_01_text.text()
        g            = float(g_text)
        g0_text      = self.Zeff_fit_02_text.text()
        g0           = float(g0_text)
        #
        Zeff_matrix  = ((g*((reference_image_L/1000+1)/RED_matrix -1) + g0 + 1)**(1/m))*Zeff_w
    elif   selected_zeff_method == "Hunemohr":
        de_text     =  self.Zeff_fit_01_text.text()
        de          =  float(de_text)
        Z           =  Low*de + High*(Zeff_w**m -de)
        Zeff_matrix =  (Z/RED_matrix)**(1/m)   
    #
    Zeff_matrix  = np.nan_to_num(Zeff_matrix)
    if self.checkBox_Im_Zeff.isChecked():
        # copy the header of the low image ... in the future some tags will be adjusted
        original_data = self.medical_image[patient_id_L][study_id_L][modality_L][item_index_L].copy()
        # Ensure the list is long enough to accommodate new indices
        required_length = len(self.medical_image[patient_id_L][study_id_L][modality_L]) + 1
        while len(self.medical_image[patient_id_L][study_id_L][modality_L]) < required_length:
            self.medical_image[patient_id_L][study_id_L][modality_L].append(None)
        # Store data into new series indice
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]                              = copy.deepcopy(original_data)
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['3DMatrix']                  = Zeff_matrix.astype(np.float32)
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['SliceImageComments']        = 'Zeff Calculated AMB'
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['ImageComments'] = "Zeff Calculated AMB"
        image_comment = str('Zeff Calculated AMB')
        data_element = DataElement((0x0020, 0x4000), 'LO', image_comment)
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['DCM_Info']['ImageComments'] = data_element
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['LUTLabel'] = 'Calculated Zeff'
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['LUTLabel'] = (f"Zeff {Im_com}")
        #
        #
    if self.checkBox_Im_I.isChecked() or self.checkBox_Im_SPR.isChecked():
        # GET RED METHOD AND PARAMETERS
        # Get calibration parameters
        #
        # Number of intervals
        Intervals   = self.N_lin_fit.value()
        #
        # Limit intervals
        text            = self.I_Fit_limits.text()
        elements        = text.split()
        Intervals_lim   = []
        for elem in elements:
            try:
                number = float(elem)  # Try to convert the element to a float
                Intervals_lim .append(number)
            except ValueError:
                print("I-value interval limits error")
                return

        Int_limits = np.array(Intervals_lim)
        #
        # a 
        text = self.I_value_a_coeff_calc.text()
        elements = text.split()
        coef_a   = []

        for elem in elements:
            try:
                number = float(elem)  # Try to convert the element to a float
                coef_a.append(number)
            except ValueError:
                print("I-value coeficiednt a error")
                return

        a_c = np.array(coef_a)
        # b
        text = self.I_value_b_coeff_calc.text()
        elements = text.split()
        coef_b   = []

        for elem in elements:
            try:
                number = float(elem)  # Try to convert the element to a float
                coef_b.append(number)
            except ValueError:
                print("I-value coeficiednt b error")
                return

        b_c = np.array(coef_b)
        #
        selected_Ivalue_method = self.Ivalue_method_list.currentText()
        #
        I_matrix = np.zeros_like(Zeff_matrix)
        if   selected_Ivalue_method == "Hunemohr":
            for i in range(Zeff_matrix.shape[0]):
                for j in range(Zeff_matrix.shape[1]):
                    for k in range(Zeff_matrix.shape[2]):
                        element = Zeff_matrix[i,j,k]
                        if element == 0:
                            continue
                        for idx in range(Intervals-1):
                            Int_limits[idx]
                            if   element < Int_limits[idx]:
                                I_matrix[i,j,k] = a_c[idx]*element + b_c[idx]
                                break
                            elif idx == Intervals-2:
                                I_matrix[i,j,k] = a_c[-1]*element + b_c[-1]
                                break
            I_matrix = np.exp(I_matrix)
        elif   selected_Ivalue_method == "Saito":
            I_water = float(self.Iv_water_ref.value())
            for i in range(Zeff_matrix.shape[0]):
                for j in range(Zeff_matrix.shape[1]):
                    for k in range(Zeff_matrix.shape[2]):
                        element = Zeff_matrix[i,j,k]
                        if element == 0:
                            continue
                        for idx in range(Intervals-1):
                            if   element < Int_limits[idx]:
                                I_matrix[i,j,k] = a_c[idx]*((element/Zeff_w)**m-1) + b_c[idx] + np.log(I_water)
                                break
                            elif idx == Intervals-2:
                                I_matrix[i,j,k] = a_c[-1]*((element/Zeff_w)**m-1)  + b_c[-1]  + np.log(I_water)
                                break
                self.progressBar.setValue(int(i/Zeff_matrix.shape[0]*100))
            I_matrix = np.exp(I_matrix)
        
        I_matrix  = np.nan_to_num(I_matrix)
        if self.checkBox_Im_I.isChecked():
            # copy the header of the low image ... in the future some tags will be adjusted
            original_data = self.medical_image[patient_id_L][study_id_L][modality_L][item_index_L].copy()
            # Ensure the list is long enough to accommodate new indices
            required_length = len(self.medical_image[patient_id_L][study_id_L][modality_L]) + 1
            while len(self.medical_image[patient_id_L][study_id_L][modality_L]) < required_length:
                self.medical_image[patient_id_L][study_id_L][modality_L].append(None)
            # Store data into new series indice
            self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]                              = copy.deepcopy(original_data)
            self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['3DMatrix']                  = I_matrix.astype(np.float32)
            self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['SliceImageComments']        = 'Ivalue Calculated AMB'
            self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['ImageComments'] = "Ivalue Calculated AMB"
            image_comment = str('Ivalue Calculated AMB')
            data_element = DataElement((0x0020, 0x4000), 'LO', image_comment)
            self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['DCM_Info']['ImageComments'] = data_element
            self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['LUTLabel'] = 'Calculated Ivalue'
            self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['LUTLabel'] = (f"Ivalue {Im_com}")
    
    if self.checkBox_Im_SPR.isChecked():
        I_w          = float(self.Iv_water_ref.value())
        Energy       = self.SPR_ref_energy.value()
        # Constants
        m_e_c2 = 0.511  # MeV, rest mass energy of electron
        # Calculate beta for given energy
        beta = calculate_beta(Energy)
        # eV to MeV
        I_w = I_w/1e6
        I   = I_matrix.copy()
        I   = I/1e6
        # Calculate constants
        denominator = np.log(2 * m_e_c2 * beta**2 / (I_w * (1 - beta**2))) - beta**2

        # Calculate the numerator term ln(2m_e c^2 beta^2 / (I(1 - beta^2))) - beta^2
        numerator = np.log(2 * m_e_c2 * beta**2) -np.log(I) - np.log(1 - beta**2) - beta**2

        SPR_matrix = RED_matrix * (numerator / denominator)
        
        # copy the header of the low image ... in the future some tags will be adjusted
        original_data = self.medical_image[patient_id_L][study_id_L][modality_L][item_index_L].copy()
        # Ensure the list is long enough to accommodate new indices
        required_length = len(self.medical_image[patient_id_L][study_id_L][modality_L]) + 1
        while len(self.medical_image[patient_id_L][study_id_L][modality_L]) < required_length:
            self.medical_image[patient_id_L][study_id_L][modality_L].append(None)
        # Store data into new series indice
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]                              = copy.deepcopy(original_data)
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['3DMatrix']                  = SPR_matrix.astype(np.float32)
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['SliceImageComments']        = 'SPR Calculated AMB'
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['ImageComments'] = "SPR Calculated AMB"
        image_comment = str('Ivalue Calculated AMB')
        data_element = DataElement((0x0020, 0x4000), 'LO', image_comment)
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['DCM_Info']['ImageComments'] = data_element
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['LUTLabel'] = 'Calculated SPR'
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['LUTLabel'] = (f"SPR {Im_com}")
    
    populate_DICOM_tree(self)




def export_all_DECT_tables(self):
    """
    Ask the user to pick a folder and then export all tables to separate CSV files.
    """
    options = QFileDialog.Options()
    folder = QFileDialog.getExistingDirectory(self, "Select Folder", options=options)
    if folder:
        export_tableRED(self,folder)
        export_tableZeff(self,folder)
        export_tableIv(self,folder)
        export_tableSPR(self,folder)

def export_tableRED(self, folder=None):
    """
    Export the tableRED to a CSV file.
    """
    if folder is None:
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
    if folder:
        file_path = os.path.join(folder, "tableRED.csv")
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write headers
            writer.writerow([self.tableRED.horizontalHeaderItem(i).text() for i in range(self.tableRED.columnCount())])
            # Write data
            for row in range(self.tableRED.rowCount()):
                row_data = [self.tableRED.item(row, col).text() if self.tableRED.item(row, col) else '' for col in range(self.tableRED.columnCount())]
                writer.writerow(row_data)

def export_tableZeff(self, folder=None):
    """
    Export the tableZeff to a CSV file.
    """
    if folder is None:
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
    if folder:
        file_path = os.path.join(folder, "tableZeff.csv")
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write headers
            writer.writerow([self.tableZeff.horizontalHeaderItem(i).text() for i in range(self.tableZeff.columnCount())])
            # Write data
            for row in range(self.tableZeff.rowCount()):
                row_data = [self.tableZeff.item(row, col).text() if self.tableZeff.item(row, col) else '' for col in range(self.tableZeff.columnCount())]
                writer.writerow(row_data)

def export_tableIv(self, folder=None):
    """
    Export the tableIv to a CSV file.
    """
    if folder is None:
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
    if folder:
        file_path = os.path.join(folder, "tableIv.csv")
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write headers
            writer.writerow([self.tableIv.horizontalHeaderItem(i).text() for i in range(self.tableIv.columnCount())])
            # Write data
            for row in range(self.tableIv.rowCount()):
                row_data = [self.tableIv.item(row, col).text() if self.tableIv.item(row, col) else '' for col in range(self.tableIv.columnCount())]
                writer.writerow(row_data)

def export_tableSPR(self, folder=None):
    """
    Export the tableSPR to a CSV file.
    """
    if folder is None:
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
    if folder:
        file_path = os.path.join(folder, "tableSPR.csv")
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write headers
            writer.writerow([self.tableSPR.horizontalHeaderItem(i).text() for i in range(self.tableSPR.columnCount())])
            # Write data
            for row in range(self.tableSPR.rowCount()):
                row_data = [self.tableSPR.item(row, col).text() if self.tableSPR.item(row, col) else '' for col in range(self.tableSPR.columnCount())]
                writer.writerow(row_data)

    
    
def c_roi_scatter_plot(self):
    try:
        selected_index_im_01 = self.scatter_plot_im_01.currentIndex()
        series_label_01, patient_id_01, study_id_01, modality_01, item_index_01 = self.series_info_dict[selected_index_im_01]
        reference_image_01 = self.medical_image[patient_id_01][study_id_01][modality_01][item_index_01]['3DMatrix']
    
        selected_index_im_02 = self.scatter_plot_im_02.currentIndex()
        series_label_02, patient_id_02, study_id_02, modality_02, item_index_02 = self.series_info_dict[selected_index_im_02]
        reference_image_02 = self.medical_image[patient_id_02][study_id_02][modality_02][item_index_02]['3DMatrix']
    
        num_values = self.DECT_scatt_N.value()
        point_size = self.DECT_sct_p_size.value()
    
        x_data_all = []
        y_data_all = []
        colors = []
        labels = []
    
        export_data = []
        
        
        font_size = self.selected_font_size
        background_color = self.selected_background
        
        # Determine text and label colors based on the background color
        if background_color == 'Transparent':
            text_color = 'white'
            bg         = 'transparent'
        elif background_color == 'White':
            text_color = 'black'
            bg         = 'white'
        else:
            text_color = 'black'  # Default to black for any other background color
        
    
        for row in range(self.table_circ_roi.rowCount()):
            try:
                item_x = self.table_circ_roi.item(row, 0)
                item_y = self.table_circ_roi.item(row, 1)
                item_radius = self.table_circ_roi.item(row, 2)
                sli_ini = self.table_circ_roi.item(row, 3)
                sli_fin = self.table_circ_roi.item(row, 4)
                item_r = self.table_circ_roi.item(row, 6)
                item_g = self.table_circ_roi.item(row, 7)
                item_b = self.table_circ_roi.item(row, 8)
    
                if item_x is None or item_y is None or item_radius is None or sli_ini is None or sli_fin is None or item_r is None or item_g is None or item_b is None:
                    print(f'Skipping row {row} due to missing data')
                    continue
    
                center_x = float(item_x.text())
                center_y = float(item_y.text())
                radius = float(item_radius.text())
                slice_ini = int(float(sli_ini.text()))
                slice_fin = int(float(sli_fin.text()))
                color = (float(item_r.text()), float(item_g.text()), float(item_b.text()))
    
                # Create a mask for the ROI
                mask = np.zeros(reference_image_01.shape, dtype=bool)
                for z in range(slice_ini, slice_fin + 1):
                    y, x = np.ogrid[-center_y:reference_image_01.shape[1] - center_y, -center_x:reference_image_01.shape[2] - center_x]
                    mask[z] = x*x + y*y <= radius*radius
    
                # Apply the mask to the reference images
                masked_data_01 = reference_image_01[mask]
                masked_data_02 = reference_image_02[mask]
    
                # Store selected number of values
                if len(masked_data_01) >= num_values and len(masked_data_02) >= num_values:
                    selected_values_01 = np.random.choice(masked_data_01, num_values, replace=False)
                    selected_values_02 = np.random.choice(masked_data_02, num_values, replace=False)
    
                    x_data_all.append(selected_values_01)
                    y_data_all.append(selected_values_02)
                    colors.append(color)
                    labels.append(f'ROI {row + 1}')
    
                    for x_val, y_val in zip(selected_values_01, selected_values_02):
                        export_data.append([row + 1, x_val, y_val])
                else:
                    print(f'Not enough data points in the ROI for row {row}')
    
            except ValueError:
                print(f'Skipping row {row} due to invalid data')
                continue
    
        if not hasattr(self, 'plot_DECT_scat_fig'):
            self.plot_DECT_scat_fig = Figure()  # Create a figure for the first time
    
        # Clear the plot if the checkbox is not checked
        if not self.checkBox_newScplot.isChecked():
            self.plot_DECT_scat_fig.clear()
    
        ax = self.plot_DECT_scat_fig.add_subplot(111) if not self.checkBox_newScplot.isChecked() else self.plot_DECT_scat_fig.gca()
    
        # Set plot background to transparent
        ax.patch.set_alpha(0.0)
        self.plot_DECT_scat_fig.patch.set_alpha(0.0)
    
        # Customize text and axes properties
        # Customize text and axes properties
        ax.tick_params(colors=text_color, labelsize=font_size)  # Set text color and font size
        ax.xaxis.label.set_color(text_color)
        ax.yaxis.label.set_color(text_color)
        ax.xaxis.label.set_fontsize(font_size)  # Set font size for x-axis label
        ax.yaxis.label.set_fontsize(font_size)  # Set font size for y-axis label
        ax.spines['bottom'].set_color(text_color)
        ax.spines['top'].set_color(text_color)
        ax.spines['left'].set_color(text_color)
        ax.spines['right'].set_color(text_color)
    
        # Plot the data as a scatter plot
        scatter_plots = []
        if self.selected_legend_on_off == "On":
            for i in range(len(x_data_all)):
                scatter = ax.scatter(x_data_all[i], y_data_all[i], label=labels[i], color=colors[i], s=point_size)
                scatter_plots.append(scatter)
            ax.legend(edgecolor=text_color, fontsize=self.selected_legend_font_size)
        else:
            for i in range(len(x_data_all)):
                scatter = ax.scatter(x_data_all[i], y_data_all[i], color=colors[i], s=point_size)
                scatter_plots.append(scatter)
    
        # Create a canvas and toolbar
        canvas = FigureCanvas(self.plot_DECT_scat_fig)
        canvas.setStyleSheet(f"background-color:{bg};")
        toolbar = NavigationToolbar(canvas, self)
    
        # Plot the data as a scatter plot
        if self.selected_legend_on_off == "On":
            for i in range(len(x_data_all)):
                ax.scatter(x_data_all[i], y_data_all[i], label=labels[i], color=colors[i], s=point_size)
            ax.legend(edgecolor=text_color, fontsize=self.selected_legend_font_size)
        else:
            for i in range(len(x_data_all)):
                ax.scatter(x_data_all[i], y_data_all[i], color=colors[i], s=point_size)
    
    
        # Create a canvas and toolbar
        canvas = FigureCanvas(self.plot_DECT_scat_fig)
        canvas.setStyleSheet(f"background-color:{bg};")
        toolbar = NavigationToolbar(canvas, self)
    
        # Check if the container has a layout, set one if not
        container = self.DECT_Scatt_Ax_View
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
    
    
        # Export data to CSV if checkbox is checked
        if self.DECT_exp_scatt_data.isChecked():
            options = QFileDialog.Options()
            folder = QFileDialog.getExistingDirectory(self, "Select Folder", options=options)
            if folder:
                file_path = os.path.join(folder, "DECT_scatter_export.csv")
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['ROI', 'Image1_Value', 'Image2_Value'])
                    writer.writerows(export_data)
    except Exception as e:
        # Catch any other unexpected errors and show them in a dialog
        show_error_dialog(self, f"An error occurred: {str(e)}")  
        
        
def show_error_dialog(self, message):
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setText("Error")
    error_dialog.setInformativeText(message)
    error_dialog.setWindowTitle("Error")
    error_dialog.exec_()                    
                
def save_parameters_to_csv(self):
        options = QFileDialog.Options()
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", options=options)
        if folder:
            filepath = os.path.join(folder, "dect_par_export.csv")
            elements = {
                'N_lin_fit': self.N_lin_fit.value(),
                'I_Fit_limits': self.I_Fit_limits.text(),
                'I_value_a_coeff_calc': self.I_value_a_coeff_calc.text(),
                'I_value_b_coeff_calc': self.I_value_b_coeff_calc.text(),
                'I_value_z_lw_values': self.I_value_z_lw_values.text(),
                'I_value_z_up_values': self.I_value_z_up_values.text(),
                'RED_r_square_text': self.RED_r_square_text.text(),
                'RED_RMSE_text': self.RED_RMSE_text.text(),
                'RED_fit_01_text': self.RED_fit_01_text.text(),
                'RED_fit_02_text': self.RED_fit_02_text.text(),
                'RED_fit_03_text': self.RED_fit_03_text.text(),
                'Zeff_r_square_text': self.Zeff_r_square_text.text(),
                'Zeff_RMSE_text': self.Zeff_RMSE_text.text(),
                'Zeff_fit_01_text': self.Zeff_fit_01_text.text(),
                'Zeff_fit_02_text': self.Zeff_fit_02_text.text(),
                'Ivalue_RMSE_text': self.Ivalue_RMSE_text.text(),
                'SPR_RMSE_text': self.SPR_RMSE_text.text(),
                'Zeff_fit_1': self.Zeff_fit_1.text(),
                'Zeff_fit_2': self.Zeff_fit_2.text(),
                'SPR_ref_energy': str(self.SPR_ref_energy.value()),
                'Ivaluefit_method_index': str(self.Ivaluefit_method.currentIndex()),
                'RED_method_index': str(self.RED_method.currentIndex()),
                'Zeff_method_index': str(self.Zeff_method.currentIndex())
            }
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for key, value in elements.items():
                    writer.writerow([key, value])

def load_parameters_from_csv(self):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if filepath:
            elements = {}
            with open(filepath, 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) == 2:
                        elements[row[0]] = row[1]

            self.N_lin_fit.setValue(int(elements.get('N_lin_fit', '')))
            self.I_Fit_limits.setText(elements.get('I_Fit_limits', ''))
            self.I_value_a_coeff_calc.setText(elements.get('I_value_a_coeff_calc', ''))
            self.I_value_b_coeff_calc.setText(elements.get('I_value_b_coeff_calc', ''))
            self.I_value_z_lw_values.setText(elements.get('I_value_z_lw_values', ''))
            self.I_value_z_up_values.setText(elements.get('I_value_z_up_values', ''))
            self.RED_r_square_text.setText(elements.get('RED_r_square_text', ''))
            self.RED_RMSE_text.setText(elements.get('RED_RMSE_text', ''))
            self.RED_fit_01_text.setText(elements.get('RED_fit_01_text', ''))
            self.RED_fit_02_text.setText(elements.get('RED_fit_02_text', ''))
            self.RED_fit_03_text.setText(elements.get('RED_fit_03_text', ''))
            self.Zeff_r_square_text.setText(elements.get('Zeff_r_square_text', ''))
            self.Zeff_RMSE_text.setText(elements.get('Zeff_RMSE_text', ''))
            self.Zeff_fit_01_text.setText(elements.get('Zeff_fit_01_text', ''))
            self.Zeff_fit_02_text.setText(elements.get('Zeff_fit_02_text', ''))
            self.Ivalue_RMSE_text.setText(elements.get('Ivalue_RMSE_text', ''))
            self.SPR_RMSE_text.setText(elements.get('SPR_RMSE_text', ''))
            self.Zeff_fit_1.setText(elements.get('Zeff_fit_1', ''))
            self.Zeff_fit_2.setText(elements.get('Zeff_fit_2', ''))
            self.SPR_ref_energy.setValue(float(elements.get('SPR_ref_energy', '0')))
            self.Ivaluefit_method.setCurrentIndex(int(elements.get('Ivaluefit_method_index', '0')))
            self.RED_method.setCurrentIndex(int(elements.get('RED_method_index', '0')))
            self.Zeff_method.setCurrentIndex(int(elements.get('Zeff_method_index', '0')))             
                
    