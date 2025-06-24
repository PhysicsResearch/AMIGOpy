import tkinter as tk
from tkinter import filedialog
import numpy as np
from PyQt5.QtWidgets import QVBoxLayout, QFileDialog, QMessageBox

# IrIS ------------------------------------------------------------
def export_np_array(self):

    # if save_path:
    idx = self.layer_selection_box.currentIndex()
    if idx not in self.display_data_IrIS_eval or self.display_data_IrIS_eval[idx].size == 0:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText("This function requires an image set to be loaded in the IrIS module ... not View mode")
        msg.setWindowTitle("Error")
        msg.exec_()
        return
    #
    array_to_save = self.display_data_IrIS_eval[idx]  
    save_folder = get_save_path()
    full_path = f"{save_folder}/AMBpy_export.npy"
    # Save the array to disk
    np.save(full_path, array_to_save)
 
   
def export_dw_np(self):
    # Open a dialog to select a directory
    directory = QFileDialog.getExistingDirectory(None, "Select Folder")
    if not directory:
        return  # User canceled or closed the dialog, exit the function
    #
    keys_list         = list(self.IrIS_data.keys())
    margin            = self.IrIsAVg_dw_margin.value()
    for i in range(len(self.Dw_pos_info)):
        ch    = int(self.Dw_pos_info[i,15])-1
        data  = self.IrIS_data[keys_list[ch]]['3DMatrix']
        start_index = int(self.Dw_pos_info[i,2]) + margin
        end_index   = int(self.Dw_pos_info[i,3]) - margin
        if start_index < end_index:  # Ensure the range is valid
            # Slice the data array to get all frames in the range
            frames_slice = data[start_index:end_index]
            filename = f"chan_{ch+1}_dw_{i+1}.npy"
            filepath = f"{directory}/{filename}"
            np.save(filepath, frames_slice)
            print(f"Saved {filepath}")
        else:
            print(f"Skipping chan_{ch+1},dw_{i+1} due to margin settings or invalid range.")
 
 
# DICOM ------------------------------------------------------------
def export_dcm_np_array(self):
    save_folder = get_save_path()
    # if save_path:
    idx = self.layer_selection_box.currentIndex()
    full_path = f"{save_folder}/{self.series_index+1}_export.npy"
    array_to_save = self.display_data[idx]
    # Save the array to disk
    np.save(full_path, array_to_save)
              
 
def get_save_path():
    root = tk.Tk()
    root.withdraw()  # we don't want a full GUI, so keep the root window from appearing

    # Show the file dialog and store the selected directory path
    folder_selected = filedialog.askdirectory(title='Select Folder')

    if folder_selected:  # If a folder was selected
        root.destroy()  # Close the tkinter root window
        return folder_selected
    else:
        print("No folder selected.")
        return None