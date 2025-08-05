import os
import csv
import nibabel as nib
# from rt_utils import RTStructBuilder
import numpy as np
import SimpleITK as sitk

from fcn_load.populate_dcm_list import populate_DICOM_tree
from fcn_load.populate_nifti_list import populate_nifti_tree
from fcn_display.disp_data_type import adjust_data_type_seg_input
from fcn_display.display_images_seg import disp_seg_image_slice

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QWidget, QCheckBox, QLabel, QPushButton, QHBoxLayout, QMessageBox,
    QVBoxLayout, QColorDialog, QDoubleSpinBox, QListWidgetItem, QFileDialog, QTableWidgetItem
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

#########################
### GENERAL FUNCTIONS ###
#########################

def InitSeg(self):
    if 0 not in self.display_seg_data:
        QMessageBox.warning(None, "Warning", "No image volume was selected.")
        return
    
    structures_keys = []

    if self.initStructCheck.isChecked():
        check_duplicates = True
        if self.DataType == "DICOM":
            target_series = self.dicom_data[self.patientID][self.studyID][self.modality]
        elif self.DataType == "nifti":
            target_series = self.nifti_data
        else:
            return

        for target_series_dict in target_series:
            mask_3d = np.zeros_like(target_series_dict["3DMatrix"])
            mask_3d = mask_3d.astype(np.uint8)

            existing_structures = target_series_dict.get('structures', {})
            existing_structure_count = len(existing_structures)
            
            if existing_structure_count == 0:
                target_series_dict['structures'] = {}
                target_series_dict['structures_keys'] = []
                target_series_dict['structures_names'] = []

            current_structure_index = existing_structure_count + 1
            
            if len(self.segStructName.text()) > 0:
                name = self.segStructName.text()
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

            target_series_dict['structures'][new_s_key] = {
                'Mask3D': mask_3d,
                'Name': name,
                'Modified': 1
            }
            target_series_dict['structures_keys'].append(new_s_key)
            target_series_dict['structures_names'].append(name)
            structures_keys.append([new_s_key, name, target_series_dict['SeriesNumber'], self.patientID])

    else:
        if self.DataType == "DICOM":
            target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
        elif self.DataType == "nifti":
            target_series_dict = self.nifti_data[self.series_index]
        else:
            return
        
        mask_3d = np.zeros_like(target_series_dict["3DMatrix"])
        mask_3d = mask_3d.astype(np.uint8)
        
        existing_structures = target_series_dict.get('structures', {})
        existing_structure_count = len(existing_structures)
        
        if existing_structure_count == 0:
            target_series_dict['structures'] = {}
            target_series_dict['structures_keys'] = []
            target_series_dict['structures_names'] = []

        current_structure_index = existing_structure_count + 1
        
        if len(self.segStructName.text()) > 0:
            name = self.segStructName.text()
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

        target_series_dict['structures'][new_s_key] = {
            'Mask3D': mask_3d,
            'Name': name,
            'Modified': 1
        }
        target_series_dict['structures_keys'].append(new_s_key)
        target_series_dict['structures_names'].append(name)
        structures_keys.append([new_s_key, name, target_series_dict['SeriesNumber'], self.patientID])
    
    if self.DataType == "DICOM":
        populate_DICOM_tree(self)
        target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    elif self.DataType == "nifti":
        populate_nifti_tree(self)
        target_series_dict = self.nifti_data[self.series_index]

    new_s_key = target_series_dict['structures_keys'][target_series_dict['structures_names'].index(name)]
    mask_3d = target_series_dict["structures"][new_s_key]["Mask3D"]
    self.display_seg_data[1] = mask_3d
    self.slice_data_copy = np.zeros(self.display_seg_data[0].shape, dtype=np.uint8)
    self.curr_struc_key, self.curr_struc_name = None, None
    adjust_data_type_seg_input(self,1)
    disp_seg_image_slice(self)
    update_seg_struct_list(self, structures_keys, delete=False)


def DeleteSeg(self):
    if 0 not in self.display_seg_data or self.curr_struc_key is None:
        return
    
    if self.DataType == "DICOM":
        target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    elif self.DataType == "nifti":
        target_series_dict = self.nifti_data[self.series_index]
    else:
        return
    
    s_key = self.curr_struc_key
    structures_keys = []

    if 'structures' not in target_series_dict:
        return
    if s_key not in target_series_dict['structures']:
        return
    s_key_name = target_series_dict['structures'][s_key]['Name']

    if self.initStructCheck.isChecked():
        if delete_dialog(self, s_key_name, all_series=True):
            pass
        else:
            return
        
        if self.DataType == "DICOM":
            target_series = self.dicom_data[self.patientID][self.studyID][self.modality]
        elif self.DataType == "nifti":
            target_series = self.nifti_data
        else:
            return
            
        for target_series_dict in target_series:
            if 'structures' in target_series_dict:
                if s_key in target_series_dict['structures']:
                    target_series_dict['structures_keys'].remove(s_key)
                    target_series_dict['structures_names'].remove(s_key_name)
                    target_series_dict['structures'].pop(s_key, None)
                    structures_keys.append([s_key, s_key_name, target_series_dict['SeriesNumber'], self.patientID])

    else:
        if delete_dialog(self, s_key_name, all_series=False):
            pass
        else:
            return
        target_series_dict['structures_keys'].remove(s_key)
        target_series_dict['structures_names'].remove(s_key_name)
        target_series_dict['structures'].pop(s_key, None)
        structures_keys.append([s_key, s_key_name, target_series_dict['SeriesNumber'], self.patientID])

    self.display_seg_data[1] = np.zeros(self.display_seg_data[0].shape, dtype=np.uint8)
    self.slice_data_copy = np.zeros(self.display_seg_data[0].shape, dtype=np.uint8)
    adjust_data_type_seg_input(self,1)

    if self.DataType == "DICOM":
        populate_DICOM_tree(self)
    elif self.DataType == "nifti":
        populate_nifti_tree(self)

    self.curr_struc_key, self.curr_struc_name = None, None

    slice_data = np.zeros((100, 100), dtype=np.uint16)
    data_string = slice_data.tobytes()
    extent = slice_data.shape
    # initialize display image
    self.dataImporterSeg[1].SetDataScalarTypeToUnsignedShort()
    self.dataImporterSeg[1].CopyImportVoidPointer(data_string, len(data_string))
    self.dataImporterSeg[1].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
    self.dataImporterSeg[1].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
    imageProperty = self.imageActorSeg[1].GetProperty()
    imageProperty.SetOpacity(0)  
    self.dataImporterSeg[1].Modified()    
    self.renSeg.GetRenderWindow().Render() 

    update_seg_struct_list(self, structures_keys, delete=True)


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
    

def delete_dialog(self, name, all_series=False):
    dlg = QMessageBox(self)
    dlg.setWindowTitle("Delete warning!")
    if all_series:
        dlg.setText(f"Structure '{name}' will be deleted from ALL series. \nProceed?")
    else:
        dlg.setText(f"Structure '{name}' will be deleted from this series. \nProceed?")
    dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    dlg.setIcon(QMessageBox.Question)
    button = dlg.exec()
    if button == QMessageBox.Yes:
        return True
    else:
        return False
    

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
    
    try:
        x_min = int(self.threshMinHU.text())
    except:
        x_min = -200
    try:
        x_max = int(self.threshMaxHU.text())
    except:
        x_max = 200
    
    v, x = np.histogram(self.display_seg_data[0], range=(-1000, 1000), bins=2000)
    
    min_lim = -500; max_lim = 500
    if x_min < -500:
        min_lim = x_min - 100
    if x_max > 500:
        max_lim = x_max + 100
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
    ax.legend(["HU distribution"], loc='upper right')
    
    # Custom canvas that adjusts on resize
    class ResizableCanvas(FigureCanvas):
        def resizeEvent(self, event):
            # Schedule tight_layout after the resize event completes
            QTimer.singleShot(0, self._apply_tight_layout)
            super().resizeEvent(event)

        def _apply_tight_layout(self):
            self.figure.tight_layout()
            self.draw()

    # Create the canvas
    canvas = ResizableCanvas(self.plot_fig)
    canvas.setStyleSheet(f"background-color:{self.selected_background};")

    # Layout setup
    container = self.VTK_SegHistView
    if container.layout() is None:
        layout = QVBoxLayout(container)
        container.setLayout(layout)
    else:
        layout = container.layout()

    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # Clear previous widgets except the toolbar
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() and not isinstance(child.widget(), NavigationToolbar):
            child.widget().deleteLater()

    # Add the canvas
    layout.addWidget(canvas)

    # Tight layout to remove extra padding
    self.plot_fig.tight_layout()
    canvas.draw()


class ColorCheckItem(QWidget):
    """
    A custom widget that displays:
      - A checkbox (to toggle the structure on/off),
      - A label (for the structure name),
      - A color-selection button,
      - A 'Line Width' spinbox,
      - A 'Transparency' spinbox,
      - A 'Fill' checkbox (to indicate whether to display a filled polygon).
    """

    def __init__(self, widget_info, struct_colors, parent=None):
        super().__init__(parent)

        # 1) Master checkbox to enable/disable the structure
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)

        # 2) Label for the structure name
        patient_id, series_id, struct_name = widget_info
        self.patient_id = QLabel(str(patient_id))
        self.series_id = QLabel(str(series_id))
        self.struct_name = QLabel(str(struct_name))

        # 3) Button to pick color
        if struct_name not in struct_colors:
            struct_colors[struct_name] = QColor(Qt.red)
        self.selectedColor = struct_colors[struct_name]
        self.struct_colors = struct_colors

        self.color_button = QPushButton("Select Color")
        self.color_button.setMaximumWidth(100)
        self.color_button.clicked.connect(self.openColorDialog)
        if self.selectedColor.isValid():
            self.color_button.setStyleSheet(f"background-color: {self.selectedColor.name()};")

        # 5) Spinbox for transparency (0=opaque, 1=fully transparent)
        self.transparency_spinbox = QDoubleSpinBox()
        self.transparency_spinbox.setRange(0.0, 1.0)
        self.transparency_spinbox.setValue(1.0)
        self.transparency_spinbox.setSingleStep(0.1)
        self.transparency_spinbox.setDecimals(2)

        # Lay out horizontally
        layout = QHBoxLayout()
        layout.addWidget(self.checkbox)
        layout.addWidget(self.patient_id)
        layout.addWidget(self.series_id)
        layout.addWidget(self.struct_name)
        layout.addWidget(self.color_button)
        layout.addWidget(QLabel("Transp:"))
        layout.addWidget(self.transparency_spinbox)

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def openColorDialog(self):
        color = QColorDialog.getColor(
            initial=self.selectedColor or QColor(Qt.white),
            parent=self
        )
        if color.isValid():
            self.selectedColor = color
            self.color_button.setStyleSheet(f"background-color: {color.name()};")


def update_seg_struct_list(self, structures_keys=None, delete=False):
    """
    Update self.STRUCTlist (a QListWidget) with custom items that display the structure name,
    a checkbox, and a color-selection button. The corresponding structure key is stored in the custom widget.
    """
    if getattr(self, 'series_index', None) is None:
        return
    if structures_keys is None:
        self.segStructList.clear()
        if self.segStructList.count() != 0 or not (self.DataType in ["DICOM", "nifti"]):
            return

        if self.DataType == "DICOM":
            target_series = []
            for patientID in self.dicom_data:
                for studyID in self.dicom_data[patientID]:
                    for modality in self.dicom_data[patientID][studyID]:
                        if modality != "CT":
                            continue
                        if not hasattr(self, 'series_index') or self.series_index is None:
                            continue

                        target_series_dict = self.dicom_data[patientID][studyID][modality][self.series_index]
                        target_series_dict["PatientID"] = patientID
                        target_series.append(target_series_dict)
        elif self.DataType == "nifti":
            target_series = self.nifti_data
        else:
            return
        
        for target_series_dict in target_series:
            if type(target_series_dict) is dict and 'structures' in target_series_dict:
                if target_series_dict["SeriesNumber"] != target_series[self.series_index]["SeriesNumber"]:
                    continue
                patientID = target_series_dict.get("PatientID", "")
                seriesID = target_series_dict.get("SeriesNumber", None)
                for k in target_series_dict['structures']:
                    name = target_series_dict['structures'][k]['Name']
                    target_key = f"{patientID}_{seriesID}_{name}"
                
                    list_item = QListWidgetItem(self.segStructList)
                    custom_item = ColorCheckItem([patientID, seriesID, name], self.struct_colors)
                    custom_item.structure_key = target_key
                    self.struct_colors = custom_item.struct_colors
                    list_item.setSizeHint(custom_item.sizeHint())

                    # Append new item
                    self.segStructList.addItem(list_item)
                    self.segStructList.setItemWidget(list_item, custom_item)
    else:
        for key, name, series_id, patient_id in structures_keys:
            target_key  = f"{patient_id}_{series_id}_{name}"

            if delete:
                for i in range(self.segStructList.count()):
                    item = self.segStructList.item(i)
                    widget = self.segStructList.itemWidget(item)
                    if not widget:
                        continue
                    if getattr(widget, "structure_key", None) == target_key:
                        self.segStructList.removeItemWidget(item)  # Detach widget
                        widget.deleteLater()                       # Schedule widget for deletion
                        self.segStructList.takeItem(i)             # Remove the QListWidgetItem
                        break

            else:
                # Check if the item already exists and delete it first
                for i in range(self.segStructList.count()):
                    item = self.segStructList.item(i)
                    widget = self.segStructList.itemWidget(item)
                    if not widget:
                        continue
                    if getattr(widget, "structure_key", None) == target_key:
                        self.segStructList.removeItemWidget(item)
                        widget.deleteLater()
                        self.segStructList.takeItem(i)
                        break
                list_item = QListWidgetItem(self.segStructList)
                custom_item = ColorCheckItem([patient_id, series_id, name], self.struct_colors)
                custom_item.structure_key = target_key
                self.struct_colors = custom_item.struct_colors
                
                list_item.setSizeHint(custom_item.sizeHint())
        
                # Append new item
                self.segStructList.addItem(list_item)
                self.segStructList.setItemWidget(list_item, custom_item)

        disp_seg_image_slice(self)
        
    for row in range(self.segStructList.count()):
        item = self.segStructList.item(row)
        widget = self.segStructList.itemWidget(item)
        checkbox = getattr(widget, "checkbox", None)
        checkbox.stateChanged.connect(lambda: disp_seg_image_slice(self))
        colorbutton = getattr(widget, "color_button", None)
        colorbutton.clicked.connect(lambda: disp_seg_image_slice(self))
        transparency_spinbox = getattr(widget, "transparency_spinbox", None)
        transparency_spinbox.valueChanged.connect(lambda: disp_seg_image_slice(self))

    


##########################
### SEGMENTATION TOOLS ###
##########################

def threshSeg(self):
    if 0 not in self.display_seg_data or not hasattr(self, 'curr_struc_key'):
        return
    if self.curr_struc_key == None:
        QMessageBox.warning(None, "Warning", "No structure was selected.\nPlease select a structure.")
        return

    try:
        min_ = int(self.threshMinHU.text())
    except:
        QMessageBox.warning(None, "Warning", "No valid value (int) was provided for min. HU")
        return
    try:
        max_ = int(self.threshMaxHU.text())
    except:
        QMessageBox.warning(None, "Warning", "No valid value (int) was provided for max. HU")
        return
    
    if min_ >= max_:
        QMessageBox.warning(None, "Warning", "No valid HU range was provided (ensure min HU < max HU)")
        return       
    
    if self.DataType == "DICOM":
        target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    elif self.DataType == "nifti":
        target_series_dict = self.nifti_data[self.series_index]
    else:
        return

    existing_structures = target_series_dict.get('structures', {})
    if len(existing_structures) == 0:
        return
    
    slice_mask = np.zeros(self.display_seg_data[0].shape, dtype=np.uint8)
    min_idx = self.indexMinThreshSeg.value() 
    max_idx = self.indexMaxThreshSeg.value()

    if self.im_ori_seg == "axial":
        if min_idx >= 0 and max_idx < slice_mask.shape[0] and min_idx <= max_idx:
            slice_mask[min_idx:max_idx + 1, :, :] = 1
        else:
            QMessageBox.warning(None, "Warning", "Invalid slice indices for axial orientation.")
            return
    elif self.im_ori_seg == "sagittal":
        if min_idx >= 0 and max_idx < slice_mask.shape[2] and min_idx <= max_idx:
            slice_mask[:, :, min_idx:max_idx + 1] = 1
        else:
            QMessageBox.warning(None, "Warning", "Invalid slice indices for sagittal orientation.")
            return
    elif self.im_ori_seg == "coronal":
        if min_idx >= 0 and max_idx < slice_mask.shape[1] and min_idx <= max_idx:
            slice_mask[:, min_idx:max_idx + 1, :] = 1  
        else:
            QMessageBox.warning(None, "Warning", "Invalid slice indices for coronal orientation.")
            return
        
    mask_3d = ((self.display_seg_data[0] >= min_) * (self.display_seg_data[0] <= max_) * slice_mask).astype(np.uint8)

    if self.DataType == "DICOM":
        self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures'][self.curr_struc_key]['Modified'] = 1
        self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures'][self.curr_struc_key]['Mask3D'] = mask_3d
    elif self.DataType == "nifti":
        self.nifti_data[self.series_index]['structures'][self.curr_struc_key]['Modified'] = 1
        self.nifti_data[self.series_index]['structures'][self.curr_struc_key]['Mask3D'] = mask_3d

    self.display_seg_data[1] = mask_3d

    adjust_data_type_seg_input(self,1)
    disp_seg_image_slice(self) 


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


def undo_brush_seg(self):
    if hasattr(self, 'slice_data_copy'):
        self.display_seg_data[1] = self.slice_data_copy.copy()  
        self.slice_data_copy = self.display_seg_data[1].copy()
        if self.DataType == "DICOM":
            self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures'][self.curr_struc_key]['Mask3D'] = self.display_seg_data[1]
        elif self.DataType == "nifti":
            self.nifti_data[self.series_index]['structures'][self.curr_struc_key]['Mask3D'] = self.display_seg_data[1]
        else:
            return
        disp_seg_image_slice(self)
    else:
        return
    
    
################
### ANALYSIS ###
################

def calc_com(segmentation):
    from scipy.ndimage import center_of_mass
    return center_of_mass(segmentation)


def calcStrucStats(self):
    
    data = {}
    if self.DataType not in ["DICOM", "nifti"]:
        return
    
    if self.DataType == "DICOM":
        target_series = []
        for patientID in self.dicom_data:
            for studyID in self.dicom_data[patientID]:
                for modality in self.dicom_data[patientID][studyID]:
                    if modality != "CT":
                        continue
                    for target_series_dict in self.dicom_data[patientID][studyID][modality]:
                        if len(target_series_dict.get('structures', {})) == 0:
                            continue
                        target_series.append(target_series_dict)
    elif self.DataType == "nifti":
        target_series = self.nifti_data
        patientID = ""

    for target_series_dict in target_series:          
        slice_thick = target_series_dict['metadata']['SliceThickness']
        pixel_spac = target_series_dict['metadata']['PixelSpacing']
        Im_PatPosition = target_series_dict['metadata']['ImagePositionPatient']
        image_vol = target_series_dict['3DMatrix']
        if 'structures' not in target_series_dict:
            continue

        for k in target_series_dict['structures']:
            struct = target_series_dict['structures'][k]
            series_id = target_series_dict.get('SeriesNumber', None)
            struct_name = struct['Name']
            mask = struct["Mask3D"]
            if image_vol.shape != mask.shape:
                QMessageBox.warning(None, "Warning", f"Structure '{struct_name}' does not match the image volume shape.")
                continue
            vol_in_voxels = mask.sum() 
            vol_in_mm = vol_in_voxels * slice_thick * pixel_spac[0] * pixel_spac[1]
            CoM = calc_com(mask) * np.array([slice_thick, pixel_spac[0], pixel_spac[1]]) + Im_PatPosition[::-1]
            hu_mean = np.ma.masked_array(image_vol, np.logical_not(mask)).mean()
            hu_std = np.ma.masked_array(image_vol, np.logical_not(mask)).std()
            data[f"{patientID}_{series_id}_{struct_name}"] = {"patient_id": patientID, "series_id": series_id, 
                                                                "name": struct_name, "volume": vol_in_mm, "CoM": CoM,
                                                                "hu_mean": hu_mean, "hu_std": hu_std}
                        
    self.tableSegStrucStats.clear()
    # Clear the table before populating it
    header_cols = ["Export", "Patient ID", "Series ID", "Name", "Volume (mm^3)", "CoM (z)", "CoM (y)", "CoM (x)", "HU Mean", "HU Std"]
    self.tableSegStrucStats.clear()
    self.tableSegStrucStats.setRowCount(len(data))
    self.tableSegStrucStats.setColumnCount(len(header_cols))
    self.tableSegStrucStats.setHorizontalHeaderLabels(header_cols)

    for row, name in enumerate(data):
        instance_data = ["checkbox", data[name]["patient_id"], data[name]["series_id"], 
                         data[name]["name"], data[name]["volume"], 
                         data[name]["CoM"][0], data[name]["CoM"][1], data[name]["CoM"][2], 
                         data[name]["hu_mean"], data[name]["hu_std"]]
        for col, val in enumerate(instance_data):
            if val == "checkbox":
                checkkBoxItem = QTableWidgetItem()
                checkkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                checkkBoxItem.setCheckState(QtCore.Qt.Checked)       
                self.tableSegStrucStats.setItem(row,col,checkkBoxItem)
            elif type(val) == str:
                self.tableSegStrucStats.setItem(row, col, QTableWidgetItem(val))
            elif col == 2:
                self.tableSegStrucStats.setItem(row, col, QTableWidgetItem(str(int(val))))
            else:
                try:
                    self.tableSegStrucStats.setItem(row, col, QTableWidgetItem(f"{val:03f}"))
                except:
                    self.tableSegStrucStats.setItem(row, col, QTableWidgetItem(""))


def exportStrucStats(self): 
    if self.DataType not in ["DICOM", "nifti"]:
        return
    if self.tableSegStrucStats.rowCount() == 0:
        calcStrucStats(self)
        QMessageBox.warning(None, "Warning", "No statistics to export.\nPlease select the statistics to export.")
        return
    
    options = QFileDialog.Options()
    folder = QFileDialog.getExistingDirectory(self, options=options)
    
    # Get the checked items from the table
    checked_items = [("patient_id", "series_id", "name", "volume", "z", "y", "x", "mean", "std")]
    for row in range(self.tableSegStrucStats.rowCount()):
        item = self.tableSegStrucStats.item(row, 0)  # Assuming the checkbox is in the first column
        if item and item.checkState() == QtCore.Qt.Checked:
            patient_id = self.tableSegStrucStats.item(row, 1).text()
            series_id = self.tableSegStrucStats.item(row, 2).text()
            name = self.tableSegStrucStats.item(row, 3).text()
            volume = self.tableSegStrucStats.item(row, 4).text()
            z = self.tableSegStrucStats.item(row, 5).text()
            y = self.tableSegStrucStats.item(row, 6).text()
            x = self.tableSegStrucStats.item(row, 7).text()
            hu_mean = self.tableSegStrucStats.item(row, 8).text()
            hu_std = self.tableSegStrucStats.item(row, 9).text()
            checked_items.append((patient_id, series_id, name, volume, z, y, x, hu_mean, hu_std))

    with open(os.path.join(folder, "structure_stats.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(checked_items)


#########################
### EXPORT STRUCTURES ###
#########################

def overwrite_rtstruct_dialog(self, name):
    dlg = QMessageBox(self)
    dlg.setWindowTitle("Overwrite warning!")
    dlg.setText(f"A structure named '{name}' already exists in this RTSTRUCT. \nDo you want to overwrite this structure?")
    dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    dlg.setIcon(QMessageBox.Question)
    button = dlg.exec()
    if button == QMessageBox.Yes:
        return True
    else:
        return False


def remove_roi_by_name(rtstruct, roi_name):
    # Get index corresponding to ROI_name
    roi_index = None
    for i, roi in enumerate(rtstruct.ds.StructureSetROISequence):
        if roi.ROIName == roi_name:
            roi_index = i
            break

    if roi_index is None:
        return None
    
    rtstruct.ds.StructureSetROISequence.pop(roi_index)
    rtstruct.ds.ROIContourSequence.pop(roi_index)
    rtstruct.ds.RTROIObservationsSequence.pop(roi_index)

    return rtstruct


def exportSegStruc(self):
    if self.DataType not in ["DICOM", "nifti"]:
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
    for row in range(self.tableSegStrucStats.rowCount()):
        item = self.tableSegStrucStats.item(row, 0)  # Assuming the checkbox is in the first column
        if item and item.checkState() == QtCore.Qt.Checked:
            patient_id = self.tableSegStrucStats.item(row, 1).text()
            series_id = self.tableSegStrucStats.item(row, 2).text()
            s_key = self.tableSegStrucStats.item(row, 3).text()
            target_series = []
            if self.DataType == "DICOM":
                for studyID in self.dicom_data[patient_id]:
                    for modality in self.dicom_data[patient_id][studyID]:
                        for target_series_dict in self.dicom_data[patient_id][studyID][modality]:
                            if not ('SeriesNumber' not in target_series_dict or \
                                    str(target_series_dict['SeriesNumber']) != series_id or \
                                    'structures' not in target_series_dict):
                                target_series.append(target_series_dict) 
            if self.DataType == "nifti":
                for target_series_dict in self.nifti_data:
                    if not ('SeriesNumber' not in target_series_dict or \
                            str(target_series_dict['SeriesNumber']) != series_id or \
                            'structures' not in target_series_dict):
                        target_series.append(target_series_dict) 
                    
            for target_series_dict in target_series:
                for k in target_series_dict['structures']:
                    struct = target_series_dict['structures'][k]
                    if struct['Name'] == s_key:
                        mask = target_series_dict['structures'][k]["Mask3D"]
                        if self.DataType == "DICOM":
                            mask = np.flip(mask, axis=1)
                        elif self.DataType == "nifti":
                            mask = np.flip(mask, axis=1)
                            
                        img = sitk.GetImageFromArray(mask)
                        img.SetSpacing((*target_series_dict['metadata']['PixelSpacing'],
                                    target_series_dict['metadata']['SliceThickness']))
                        img.SetOrigin(target_series_dict['metadata']['ImagePositionPatient'])

                        save_path = os.path.join(save_dir, f"{patient_id}_{series_id}_{s_key}.nii.gz")
                        sitk.WriteImage(img, save_path)

                        # img = nib.Nifti1Image(mask, np.eye(4))
                        # img.header.get_xyzt_units()
                        # nib.save(img, os.path.join(save_dir, f"{patient_id}_{series_id}_{s_key}.nii.gz"))  
