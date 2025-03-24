import numpy as np
import os
import tkinter as tk
from tkinter import filedialog
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from fcn_load.populate_dcm_list import _get_or_create_parent_item
from concurrent.futures import ProcessPoolExecutor
from skimage.measure import block_reduce
import time


# Function to initialize the shared Im array
def init_im(downsampled_shape):
    global Im
    Im = np.zeros(downsampled_shape, dtype=np.uint16)

def process_file(file, Buf, Im_shape, N_div):
    with open(file, 'rb') as fid:
        fid.seek(Buf)
        #frame = np.fromfile(fid, dtype=np.uint16, count=Im_shape[0]*Im_shape[1]).reshape(Im_shape[0:2])
        frame = np.rot90(np.fromfile(fid, dtype=np.uint16, count=Im_shape[0]*Im_shape[1]).reshape(Im_shape[0:2]), 2)
        fid.seek(2008)
        Time = np.fromfile(fid, dtype=np.uint64, count=1)[0] * 1e-9
        
        # Downsample the frame by averaging, if N_div > 1
        if N_div > 1:
            frame_downsampled = block_reduce(frame, block_size=(N_div, N_div), func=np.mean)
        else:
            frame_downsampled = frame
            
        return frame_downsampled, Time

def read_IrIS_parallel(self, files):

    # Get file info
    with open(files[0], 'rb') as fid:
        Info = np.fromfile(fid, dtype=np.uint16, count=1000)
        Info = np.concatenate((Info, np.fromfile(fid, dtype=np.float32, count=2)))
        Info = np.concatenate((Info, np.fromfile(fid, dtype=np.uint64, count=5)))
        Buf = int(Info[0])
    IrIS_results = {
        'mode': Info[1],
        'VxVy': Info[4:8],
        'binning': Info[8],
        'panel': Info[9],
        'average': Info[10],
        'average_skip': Info[11],
        'delay': Info[12],
        'FOV': Info[13],
        'C_offset': Info[14],
        'C_sens': Info[15],
        'C_sum': Info[16],
        'C_N_sum': Info[17],
        'fps': Info[999],
        'fps_id': Info[1000],
        'Resolution': Info[1001],
        'Diff': Info[1004]
    }
    #
    # DOWNSAMPLE FACTOR
    N_div = self.IrIS_DownSample.value()
    Time = np.zeros(len(files))
    Im_shape = (
        np.uint(IrIS_results['VxVy'][3] - IrIS_results['VxVy'][2] + 1),
        np.uint(IrIS_results['VxVy'][1] - IrIS_results['VxVy'][0] + 1),
        np.uint(len(files))
    )

    # Calculate downsampled shape outside of the loop
    downsampled_shape = (Im_shape[0] // N_div, Im_shape[1] // N_div, len(files))
    init_im(downsampled_shape)  # Initialize Im with the downsampled shape

    # Process files in parallel
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(process_file, files, [Buf] * len(files), [Im_shape] * len(files), [N_div] * len(files)))

    # Collect results
    for i, (frame_downsampled, frame_time) in enumerate(results):
        Im[:, :, i] = frame_downsampled
        Time[i] = frame_time
        
        # if i % 20 == 0 or i == Total_f - 1:
        #     progress_percentage = int((i + 1) / Total_f * 100)
        #     self.progressBar.setValue(progress_percentage)
        #     QApplication.processEvents()    

    IrIS_results['Im'] = Im
    IrIS_results['AcquisitionTime'] = Time

    return IrIS_results

def read_IrIS_quick(self, files):

    # Get file info
    with open(files[0], 'rb') as fid:
        Info = np.fromfile(fid, dtype=np.uint16, count=1000)
        Info = np.concatenate((Info, np.fromfile(fid, dtype=np.float32, count=2)))
        Info = np.concatenate((Info, np.fromfile(fid, dtype=np.uint64, count=5)))
        Buf = int(Info[0])
    IrIS_results = {
        'mode': Info[1],
        'VxVy': Info[4:8],
        'binning': Info[8],
        'panel': Info[9],
        'average': Info[10],
        'average_skip': Info[11],
        'delay': Info[12],
        'FOV': Info[13],
        'C_offset': Info[14],
        'C_sens': Info[15],
        'C_sum': Info[16],
        'C_N_sum': Info[17],
        'fps': Info[999],
        'fps_id': Info[1000],
        'Resolution': Info[1001],
        'Diff': Info[1004]
    }
    #
    # DOWNSAMPLE FACTOR
    N_div = self.IrIS_DownSample.value()
    # Open the files
    Im_shape = (
        np.uint(IrIS_results['VxVy'][3] - IrIS_results['VxVy'][2] + 1),
        np.uint(IrIS_results['VxVy'][1] - IrIS_results['VxVy'][0] + 1),
        np.uint(len(files))
    )
    # Im = np.zeros(Im_shape, dtype=np.uint16)
    Time = np.zeros(len(files))
    
    Total_f = len(files)
    self.progressBar.setValue(0)
    # Process Qt events to update GUI
    QApplication.processEvents() 
    
    for i, file in enumerate(files):
        with open(file, 'rb') as fid:
            fid.seek(Buf)
            frame = np.fromfile(fid, dtype=np.uint16, count=Im_shape[0]*Im_shape[1]).reshape(Im_shape[0:2])  
            #frame = np.rot90(np.fromfile(fid, dtype=np.uint16, count=Im_shape[0]*Im_shape[1]).reshape(Im_shape[0:2]), 2)      
            fid.seek(2008)
            Time[i] = np.fromfile(fid, dtype=np.uint64, count=1)[0] * 1e-9
            
            # Downsample the frame by averaging, if N_div > 1
            if N_div > 1:
                # Apply block reduce with averaging
                frame_downsampled = block_reduce(frame, block_size=(N_div, N_div), func=np.mean)
            else:
                frame_downsampled = frame
            #
            # Adjust Im_shape for downsampled images, only once
            if i == 0:
                downsampled_shape = (frame_downsampled.shape[0], frame_downsampled.shape[1], len(files))
                Im = np.zeros(downsampled_shape, dtype=np.uint16)
            #
            Im[:, :, i] = frame_downsampled
            
        if i % 20 == 0 or i == Total_f - 1:  # Update every 10 slices or on the last slice
            progress_percentage = int((i + 1) / Total_f * 100)
            self.progressBar.setValue(progress_percentage)
            # Process Qt events to update GUI
            QApplication.processEvents()    

    IrIS_results['Im']   = Im
    IrIS_results['AcquisitionTime'] = Time

    return IrIS_results

def select_folder_and_read_files(self):
    root = tk.Tk()
    root.withdraw()  
    folder_selected = filedialog.askdirectory()
    start_time = time.time()
    # number of files to skip at the beggining and totla number of files to read per folder
    skip_files = self.Skip_IrIS_Files.value()  # Get value from the Skip_IrIS_Files SpinBox
    load_files = self.Load_IrIS_Files.value()  # Get value from the Load_IrIS_Files SpinBox
    
    # Ensure the values are non-negative
    skip_files = max(0, skip_files)
    load_files = max(0, load_files)
    
    
    IrISData = {}
    folder_count = 0
    
    for dirpath, dirnames, filenames in os.walk(folder_selected):
        # Splitting files into those that follow the naming convention and those that do not
        convention_files = []
        non_convention_files = []
        for f in filenames:
            if f.endswith('.IrIS'):
                parts = f.split('_')
                if len(parts) > 1 and parts[-1].split('.')[0].isdigit():
                    convention_files.append(os.path.join(dirpath, f))
                else:
                    non_convention_files.append(os.path.join(dirpath, f))
        
        # Sorting files that follow the naming convention by their numeric value
        convention_files_sorted = sorted(
            convention_files,
            key=lambda x: int(x.split('_')[-1].split('.')[0])
        )
        
        # Concatenating the lists, with non-convention files at the end
        files = convention_files_sorted + non_convention_files
        #
        if files:
            
            # Skip the first N files as specified by the user
            files = files[skip_files:]
            
            folder_name = os.path.basename(dirpath)
            if folder_name not in IrISData:
                IrISData[folder_name] = {}
    
            folder_count += 1
            iris_count = len(files)
            if load_files != 0:
                frames_to_save = min(load_files, iris_count)
            else:
                frames_to_save = iris_count
            #
            if self.IrIS_parallel_proc_box.isChecked():
                results = read_IrIS_parallel(self,files[:frames_to_save])  
            else:
                results = read_IrIS_quick(self,files[:frames_to_save])
                
            #
            results['Im'] = np.transpose(results['Im'], (2, 1, 0))
            # subtract the initial time so it becomes relative to the first frame
            acquisition_times = results['AcquisitionTime']
            # Subtract the first element from the rest of the elements
            adjusted_times = [Time - acquisition_times[0] for Time in acquisition_times]
            # Storing the result in IrISData
            IrISData[folder_name] = {
                        '3DMatrix': results['Im'],
                        'mode': results['mode'],
                        'VxVy': results['VxVy'],
                        'binning': results['binning'],
                        'panel': results['panel'],
                        'average':results['average'],
                        'average_skip': results['average_skip'],
                        'delay': results['delay'],
                        'FOV': results['FOV'],
                        'C_offset': results['C_offset'],
                        'C_sens': results['C_sens'],
                        'C_sum': results['C_sum'],
                        'C_N_sum': results['C_N_sum'],
                        'fps': results['fps'],
                        'fps_id': results['fps_id'],
                        'Resolution': results['Resolution'],
                        'Diff': results['Diff'],
                        'AcquisitionTime': np.array(adjusted_times),
                        'AcquisitionTime_abs': np.array(acquisition_times)   
                    }
        else:
            print(f"No .IrIS files found in the directory: {dirpath}")
    # 
    # Correction
    if   self.IrIS_Offset_checkbox.isChecked() or self.IrIS_CorFrame_checkbox.isChecked():
        Data_corr = IrISData[folder_name]['3DMatrix'].copy()
        if   self.IrIS_Offset_checkbox.isChecked():
            Data_corr = offsetcorrection(self,Data_corr)
        if  self.IrIS_CorFrame_checkbox.isChecked():
            Data_corr = framecorrection(self,Data_corr)
        IrISData[folder_name]['3DMatrix'] = np.clip(Data_corr, 0, np.iinfo(np.uint16).max).astype(np.uint16)
        
    #
    end_time = time.time()
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print(f"Loading completed in {elapsed_time:.2f} seconds.")  # Display the time it took to load
    return IrISData

def framecorrection(self, IrIS_Data):
    # Check if 'Corr_frame' exists in self.IrIS_corr and '3DMatrix' in IrISData[folder_name]
    if 'Corr_frame' in self.IrIS_corr and '3DMatrix' in self.IrIS_corr['Corr_frame']:
        
        operation        = self.IrIS_CorrFrame_oper.currentText()
        correction_matrix = self.IrIS_corr['Corr_frame']['3DMatrix']
        
        # Check if the offset_matrix is a 2D numpy array
        if  correction_matrix.ndim == 2:
            data_matrix = IrIS_Data
            if data_matrix.shape[1:] ==  correction_matrix.shape:
                # Convert to a signed integer type to avoid overflow
                data_matrix_signed       =  data_matrix.astype(np.int32)
                correction_matrix_signed =  correction_matrix.astype(np.int32)
                # Perform the selected operation
                if operation   == 'Add':
                    corrected_matrix = data_matrix_signed + correction_matrix_signed
                elif operation == 'Sub.':
                    corrected_matrix = data_matrix_signed - correction_matrix_signed
                else:
                    raise ValueError(f"Unsupported operation: {operation}")
                #
                return corrected_matrix
            else:
                raise ValueError("Dimensions of the offset matrix do not match the last two dimensions of the 3D matrix.")
        else:
            raise ValueError("self.IrIS_corr['Offset']['3DMatrix'] is not a 2D numpy array.")
    else:
        raise KeyError("Offset key does not exist in self.IrIS_corr or '3DMatrix' key is missing in the Offset dictionary.")

def offsetcorrection(self, IrIS_Data):
    # Check if 'Offset' exists in self.IrIS_corr and '3DMatrix' in IrISData[folder_name]
    if 'Offset' in self.IrIS_corr and '3DMatrix' in self.IrIS_corr['Offset']:
        
        offset_matrix = self.IrIS_corr['Offset']['3DMatrix']
        
        # Check if the offset_matrix is a 2D numpy array
        if offset_matrix.ndim == 2:
            data_matrix = IrIS_Data
            if data_matrix.shape[1:] == offset_matrix.shape:
                # Convert to a signed integer type to avoid overflow
                data_matrix_signed   = data_matrix.astype(np.int32)
                offset_matrix_signed = offset_matrix.astype(np.int32)
                # Subtract offset_matrix from each slice of the 3D matrix
                corrected_matrix_signed = data_matrix_signed - offset_matrix_signed
                # corrected_matrix = np.clip(corrected_matrix_signed, 0, np.iinfo(np.uint16).max).astype(np.uint16)
                return corrected_matrix_signed
            else:
                raise ValueError("Dimensions of the offset matrix do not match the last two dimensions of the 3D matrix.")
        else:
            raise ValueError("self.IrIS_corr['Offset']['3DMatrix'] is not a 2D numpy array.")
    else:
        raise KeyError("Offset key does not exist in self.IrIS_corr or '3DMatrix' key is missing in the Offset dictionary.")
    

def load_IrIS_folder(self):
    self.IrIS_data=select_folder_and_read_files(self)
    populate_IrIS_tree(self)
    time_relative_2_channel(self)    

def time_relative_2_channel(self):
    keys_list = list(self.IrIS_data.keys())
    # make the time relative to the first channel
    # 
    if self.checkBox_IrIS_time_rel.isChecked():
        for channel_key in keys_list:
            # Vectorized subtraction for NumPy arrays
            self.IrIS_data[channel_key]['AcquisitionTime'] = (self.IrIS_data[channel_key]['AcquisitionTime_abs'] - self.IrIS_data[keys_list[0]]['AcquisitionTime_abs'][0]).copy()    
    else:
        for channel_key in keys_list:
            # Vectorized subtraction for NumPy arrays
            self.IrIS_data[channel_key]['AcquisitionTime'] -= self.IrIS_data[channel_key]['AcquisitionTime'][0]             
        
# Slot for the 'Open' action
def populate_IrIS_tree(self):
    # Create the data model for the tree view if it doesn't exist
    if not hasattr(self, 'model') or self.model is None:
        self.model = QStandardItemModel()
        self.DataTreeView.setModel(self.model)
        self.model.setHorizontalHeaderLabels(['Data'])

    # Check for existing 'IrIS' parent item
    IrIS_parent_item = _get_or_create_parent_item(self,'IrIS')
    #
    # Clear all children of the 'IrIS' parent item
    IrIS_parent_item.removeRows(0, IrIS_parent_item.rowCount())
    # Setup headers for the tree view columns
    # Populate tree view with data
    for patient_id, patient_data in self.IrIS_data.items():
        patient_item = QStandardItem(f"PatientID: {patient_id}")
        IrIS_parent_item.appendRow(patient_item)
    # set number of channel for IrIS eval
    self.Pk_find_channel.setMaximum(len(self.IrIS_data))
