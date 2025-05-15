import numpy as np
from fcn_load.populate_dcm_list import populate_DICOM_tree
from fcn_display.disp_data_type import adjust_data_type_seg_input
from fcn_display.display_images_seg import disp_seg_image_slice
from PyQt5.QtWidgets import QTableWidgetItem, QCheckBox, QFileDialog, QMessageBox
from PyQt5 import QtCore
import os


def threshSeg(self):
    if 0 not in self.display_seg_data:
        return
    min_, max_ = self.threshMinSlider.value(), self.threshMaxSlider.value()
    target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]

    existing_structures = target_series_dict.get('structures', {})
    existing_structure_count = len(existing_structures)

    if existing_structure_count == 0:
        return
    
    mask_3d = ((self.display_seg_data[0] >= min_) * (self.display_seg_data[0] <= max_)).astype(np.uint8)

    self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures'][self.seg_curr_struc]['Mask3D'] = mask_3d
    self.display_seg_data[1] = mask_3d

    adjust_data_type_seg_input(self,1)
    disp_seg_image_slice(self) 


def overwrite_dialog(self, all_series=False):
    dlg = QMessageBox(self)
    dlg.setWindowTitle("Overwrite warning!")
    if all_series:
        dlg.setText("One of the series already has a structure with the same name. \nDo you want to overwrite ALL?")
    else:
        dlg.setText("This series already has a structure with the same name. \nDo you want to overwrite it?")
    dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    dlg.setIcon(QMessageBox.Question)
    button = dlg.exec()
    if button == QMessageBox.Yes:
        return True
    else:
        return False
    
    
def InitSeg(self):
    if len(self.display_seg_data) == 0:
        return

    if self.initStrucCheck.isChecked():
        check_duplicates = True
        for target_series_dict in self.dicom_data[self.patientID][self.studyID][self.modality]: 
            mask_3d = np.zeros_like(target_series_dict["3DMatrix"])
            mask_3d = mask_3d.astype(np.uint8)

            existing_structures = target_series_dict.get('structures', {})
            existing_structure_count = len(existing_structures)
            
            if existing_structure_count == 0:
                target_series_dict['structures'] = {}
                target_series_dict['structures_keys'] = []
                target_series_dict['structures_names'] = []

            current_structure_index = existing_structure_count + 1
            
            if len(self.segStructureName.text()) > 1:
                name = self.segStructureName.text()
            else:
                name = "structure"
                
            if name in target_series_dict['structures_names']:
                if check_duplicates:
                    check_duplicates = False
                    if overwrite_dialog(self, all_series=True):
                        pass
                    else:
                        return

                new_s_key = target_series_dict['structures_keys'][target_series_dict['structures_names'].index(name)]
            else:
                # Create a new unique key for the structure clearly:
                new_s_key = f"Structure_{current_structure_index:03d}"

            # target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
            target_series_dict['structures'][new_s_key] = {
                'Mask3D': mask_3d,
                'Name': name
            }
            target_series_dict['structures_keys'].append(new_s_key)
            target_series_dict['structures_names'].append(name)

    else:
        target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
        mask_3d = np.zeros_like(target_series_dict["3DMatrix"])
        mask_3d = mask_3d.astype(np.uint8)
        
        existing_structures = target_series_dict.get('structures', {})
        existing_structure_count = len(existing_structures)
        
        if existing_structure_count == 0:
            target_series_dict['structures'] = {}
            target_series_dict['structures_keys'] = []
            target_series_dict['structures_names'] = []

        current_structure_index = existing_structure_count + 1
        
        if len(self.segStructureName.text()) > 1:
            name = self.segStructureName.text()
        else:
            name = "structure"
            
        if name in target_series_dict['structures_names']:
            if overwrite_dialog(self, all_series=False):
                pass
            else:
                return

            new_s_key = target_series_dict['structures_keys'][target_series_dict['structures_names'].index(name)]
        else:
            # Create a new unique key for the structure clearly:
            new_s_key = f"Structure_{current_structure_index:03d}"

        # target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
        target_series_dict['structures'][new_s_key] = {
            'Mask3D': mask_3d,
            'Name': name
        }
        target_series_dict['structures_keys'].append(new_s_key)
        target_series_dict['structures_names'].append(name)
    
    populate_DICOM_tree(self)

    target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    new_s_key = target_series_dict['structures_keys'][target_series_dict['structures_names'].index(name)]
    mask_3d = target_series_dict["structures"][new_s_key]["Mask3D"]
    self.display_seg_data[1] = mask_3d
    adjust_data_type_seg_input(self,1)
    disp_seg_image_slice(self)

    

    
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QVBoxLayout

    
def plot_hist(self):
    if 0 not in self.display_seg_data:
        return

    self.plot_fig = Figure()  # Create a figure for the first time
    ax = self.plot_fig.add_subplot(111) 
    
    if self.selected_background == "Transparent":
        # Set plot background to transparent
        ax.patch.set_alpha(0.0)
        self.plot_fig.patch.set_alpha(0.0)
        
        # Customize text and axes properties
        ax.tick_params(colors='white', labelsize=10)  # White ticks with larger text
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
    
    x_min = self.threshMinSlider.value()
    x_max = self.threshMaxSlider.value()
    
    v, x = np.histogram(self.display_seg_data[0], range=(-1000, 1000), bins=2000)
    
    min_lim = -500; max_lim = 500
    if self.threshMinSlider.value() < -500:
        min_lim = self.threshMinSlider.value() - 100
    if self.threshMaxSlider.value() > 500:
        max_lim = self.threshMaxSlider.value() + 100
    max_counts = (v * (x[:-1] >= min_lim) * (x[:-1] <= max_lim)).max()

    ax.tick_params(
        axis='y',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        left=False,      # ticks along the bottom edge are off
        right=False,         # ticks along the top edge are off
        labelleft=False) # labels along the bottom edge are off
    
    ax.plot(x[:-1], v / max_counts, "-")
    ax.axvline(x_min, color="r")
    ax.axvline(x_max, color="r")
    ax.set_xlim(min_lim, max_lim)
    ax.set_ylim(0, 1.1)
    ax.set_xlabel("HU")
    
    # Create a canvas and toolbar
    canvas = FigureCanvas(self.plot_fig)
    canvas.setStyleSheet(f"background-color:{self.selected_background};")

    # Check if the container has a layout, set one if not
    container = self.VTK_SegHistView
    if container.layout() is None:
        layout = QVBoxLayout(container)
        container.setLayout(layout)
    else:
        # Clear existing content in the container, if any
        while container.layout().count():
            child = container.layout().takeAt(0)
            if child.widget() and not isinstance(child.widget(), NavigationToolbar):
                child.widget().deleteLater()

    # Add the canvas and toolbar to the container
    container.layout().addWidget(canvas)
    canvas.draw()
    
    
def on_brush_click(self):
    self.seg_brush = 0 if self.seg_brush == 1 else 1
    if self.seg_brush == 1:
        self.segEraseButton.setChecked(0)
        self.seg_erase = 0  

def on_erase_click(self):
    self.seg_erase = 0 if self.seg_erase == 1 else 1 
    if self.seg_erase == 1:
        self.segBrushButton.setChecked(0) 
        self.seg_brush = 0 

def calc_com(segmentation):
    from scipy.ndimage import center_of_mass
    return center_of_mass(segmentation)


def calcStrucStats(self):
    
    data = {}
    if self.dicom_data is None:
        return
    for patientID in self.dicom_data:
        for studyID in self.dicom_data[patientID]:
            for modality in self.dicom_data[patientID][studyID]:
                for target_series_dict in self.dicom_data[patientID][studyID][modality]:
                    if len(target_series_dict.get('structures', {})) == 0:
                        continue
                    
                    slice_thick = target_series_dict['metadata']['SliceThickness']
                    pixel_spac = target_series_dict['metadata']['PixelSpacing']
                    Im_PatPosition = target_series_dict['metadata']['ImagePositionPatient']
                    
                    for k in target_series_dict['structures']:
                        struct = target_series_dict['structures'][k]
                        series_id = target_series_dict['SeriesNumber']
                        struct_name = struct['Name']
                        mask = struct["Mask3D"]
                        vol_in_voxels = mask.sum() 
                        vol_in_mm = vol_in_voxels * slice_thick * pixel_spac[0] * pixel_spac[1]
                        CoM = calc_com(mask) * np.array([slice_thick, pixel_spac[0], pixel_spac[1]]) + Im_PatPosition[::-1]
                        data[f"{series_id}_{struct_name}"] = {"series_id": series_id, "name": struct_name, "volume": vol_in_mm, "CoM": CoM}
                        
    self.tableSegStrucStats.clear()
    # Clear the table before populating it
    header_cols = ["Export", "Series ID", "Name", "Volume (mm^3)", "CoM (z)", "CoM (y)", "CoM (x)"]
    self.tableSegStrucStats.clear()
    self.tableSegStrucStats.setRowCount(len(data))
    self.tableSegStrucStats.setColumnCount(len(header_cols))
    self.tableSegStrucStats.setHorizontalHeaderLabels(header_cols)

    for row, name in enumerate(data):
        instance_data = ["checkbox", data[name]["series_id"], data[name]["name"], data[name]["volume"], data[name]["CoM"][0],
                                     data[name]["CoM"][1], data[name]["CoM"][2]]
        for col, val in enumerate(instance_data):
            if val == "checkbox":
                checkkBoxItem = QTableWidgetItem()
                checkkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                checkkBoxItem.setCheckState(QtCore.Qt.Unchecked)       
                self.tableSegStrucStats.setItem(row,col,checkkBoxItem)
            elif type(val) == str:
                self.tableSegStrucStats.setItem(row, col, QTableWidgetItem(val))
            elif col == 1:
                self.tableSegStrucStats.setItem(row, col, QTableWidgetItem(str(int(val))))
            else:
                try:
                    self.tableSegStrucStats.setItem(row, col, QTableWidgetItem(f"{val:03f}"))
                except:
                    self.tableSegStrucStats.setItem(row, col, QTableWidgetItem(""))


def exportStrucStats(self): 
    if self.dicom_data is None:
        return
    if self.tableSegStrucStats.rowCount() == 0:
        calcStrucStats(self)
        QMessageBox.warning(None, "Warning", "No statistics to export.\nPlease select the statistics to export.")
        return
    
    options = QFileDialog.Options()
    folder = QFileDialog.getExistingDirectory(self, options=options)
    
    # Get the checked items from the table
    checked_items = [("series_id", "name", "volume", "z", "y", "x")]
    for row in range(self.tableSegStrucStats.rowCount()):
        item = self.tableSegStrucStats.item(row, 0)  # Assuming the checkbox is in the first column
        if item and item.checkState() == QtCore.Qt.Checked:
            series_id = self.tableSegStrucStats.item(row, 1).text()
            name = self.tableSegStrucStats.item(row, 2).text()
            volume = self.tableSegStrucStats.item(row, 3).text()
            z = self.tableSegStrucStats.item(row, 4).text()
            y = self.tableSegStrucStats.item(row, 5).text()
            x = self.tableSegStrucStats.item(row, 6).text()
            checked_items.append((series_id, name, volume, z, y, x))

    import csv

    with open(os.path.join(folder, "structure_stats.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(checked_items)

import nibabel as nib

def exportSegStruc(self):
    if self.dicom_data is None:
        return
    if self.tableSegStrucStats.rowCount() == 0:
        calcStrucStats(self)
        QMessageBox.warning(None, "Warning", "No structures to export.\nPlease select the structures to export.")
        return

    options = QFileDialog.Options()
    folder = QFileDialog.getExistingDirectory(self, options=options)
    save_dir = os.path.join(folder, "segmentations")
    os.makedirs(save_dir, exist_ok=True)
    
    # Get the checked items from the table
    checked_items = []
    for row in range(self.tableSegStrucStats.rowCount()):
        item = self.tableSegStrucStats.item(row, 0)  # Assuming the checkbox is in the first column
        if item and item.checkState() == QtCore.Qt.Checked:
            series_id = int(self.tableSegStrucStats.item(row, 1).text())
            s_key = self.tableSegStrucStats.item(row, 2).text()
            for target_series_dict in self.dicom_data[self.patientID][self.studyID][self.modality]:
                if target_series_dict['SeriesNumber'] == series_id:        
                    for k in target_series_dict['structures']:
                        struct = target_series_dict['structures'][k]
                        if struct['Name'] == s_key:
                            mask = target_series_dict['structures'][k]["Mask3D"]
                            img = nib.Nifti1Image(mask, np.eye(4))
                            img.header.get_xyzt_units()
                            nib.save(img, os.path.join(save_dir, f"{series_id}_{s_key}.nii.gz"))  

