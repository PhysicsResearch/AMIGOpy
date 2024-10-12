import numpy as np
from PyQt5.QtWidgets import QVBoxLayout, QFileDialog, QMessageBox, QWidget
import matplotlib.pyplot as plt
import math
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from scipy.signal import find_peaks
from PyQt5.QtCore import QModelIndex, Qt, QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel
from fcn_display.Data_tree_general import on_DataTreeView_clicked
from fcn_IrIS.plot_IrIS_profiles   import plot_IrIS_eval, create_and_embed_plot
from fcn_IrIS.source_activity_time import calculate_time_from_ref, time_since_calibration, calculate_current_activity
from fcn_load.read_IrIS import populate_IrIS_tree


def process_frames(self):
    #
    if len(self.IrIS_Eval) > len(self.IrIS_data):
        self.IrIS_Eval = {}           
    keys_list = list(self.IrIS_data.keys())
    if self.Pk_find_processl_all_check.isChecked():
        for i in range(len(self.IrIS_data)):
            self.progressBar.setValue(int(i/len(self.IrIS_data)*100))
            self.Pk_find_channel.setValue(i+1)
            cal_profiles(self,keys_list)

    else:
        self.progressBar.setValue(50)
        cal_profiles(self,keys_list)
    #
    self.progressBar.setValue(100)
    find_pks_dw(self)
    

def cal_profiles(self,keys_list):
    channel = self.Pk_find_channel.value()
    data    = self.IrIS_data[keys_list[channel-1]]['3DMatrix']
    time    = self.IrIS_data[keys_list[channel-1]]['AcquisitionTime']
    # 1. Average of each slice
    averages = np.mean(data, axis=(1, 2))
    averages_grad  = np.diff(averages)
    averages_grad  = np.append(averages_grad, 0)
    # 2. 90th percentile of each slice
    percentiles_90 = np.percentile(data, 90, axis=(1, 2))
    percentiles_90_grad  = np.diff(percentiles_90)
    percentiles_90_grad  = np.append(percentiles_90_grad, 0)
    #
    max_value       = np.max(data, axis=(1, 2))
    max_value_grad  = np.diff(max_value)
    max_value_grad  = np.append(max_value_grad, 0)
    # 3. Sum of absolute differences between consecutive slices
    #
    # Calculate the zoom factors for each dimension
    D_dim = self.DownSizeN_IrIS.value()
    downsampled_data = downsample_array(data,(D_dim,D_dim))
    # Proceed with your calculations
    differences_1 = np.diff(downsampled_data, n=1, axis=0)
    # frames to skip
    N = self.IrIS_grad_frame.value()
    differences_N = np.diff(downsampled_data, n=N, axis=0)
    #
    abs_differences_1 = np.abs(differences_1)
    abs_differences_N = np.abs(differences_N)
    #
    max_abs_diff_1 = np.max(abs_differences_1, axis=(1, 2))
    max_abs_diff_N = np.max(abs_differences_N, axis=(1, 2))
    #
    max_abs_diff_1 = np.append(max_abs_diff_1, 0)
    max_abs_diff_N = np.append(max_abs_diff_N, np.repeat(0, N))
    #
    sum_abs_diff_1 = np.sum(abs_differences_1, axis=(1, 2))
    sum_abs_diff_N = np.sum(abs_differences_N, axis=(1, 2))
    #
    #
    sum_abs_diff_1 = np.append(sum_abs_diff_1, 0)
    sum_abs_diff_N = np.append(sum_abs_diff_N, np.repeat(0, N))
    #   
    # calculate the difference inf perct of the mean value - this can be more consistent for different intensities
    averages_downsampled = np.mean(downsampled_data, axis=(1, 2))
    sum_abs_diff_1_perc  = sum_abs_diff_1 / averages_downsampled 
    sum_abs_diff_N_perc  = sum_abs_diff_N / averages_downsampled
    
    fps  = 1/np.diff(time)
    fps  = np.append(fps, 0)
    #
    # Defining a unique index or key for the new evaluation
    self.IrIS_Eval[channel] = { 'time': time,
                                        'fps': fps,
                                        'averages': averages,
                                        'averages_grad': averages_grad,
                                        'max_val': max_value,
                                        'max_val_grad': max_value,
                                        'percentiles_90': percentiles_90,
                                        'percentiles_90_grad': percentiles_90_grad,
                                        'differences_1': sum_abs_diff_1, 
                                        'differences_N': sum_abs_diff_N, 
                                        'differences_1_perc': sum_abs_diff_1_perc, 
                                        'differences_N_perc': sum_abs_diff_N_perc, 
                                        'm_differences_1': max_abs_diff_1, 
                                        'm_differences_N': max_abs_diff_N}




def update_selection_tree(self):
    channel   = self.Pk_find_channel.value()
    keys_list = list(self.IrIS_data.keys())
    model = self.DataTreeView.model()
    index = findItem(model,f'PatientID: {keys_list[channel-1]}')
    if index.isValid():
        # Clear the current selection
        self.DataTreeView.selectionModel().clearSelection()
        self.DataTreeView.selectionModel().select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.DataTreeView.scrollTo(index)
        on_DataTreeView_clicked(self,index)
        if channel in self.IrIS_Eval:
            plot_IrIS_eval(self)
                
def findItem(model, text, parent=QModelIndex()):
    for row in range(model.rowCount(parent)):
        for column in range(model.columnCount(parent)):
            index = model.index(row, column, parent)
            if model.data(index) == text:
                return index
            # Recursively search in children
            if model.hasChildren(index):
                possible_match = findItem(model, text, index)
                if possible_match.isValid():
                    return possible_match
    return QModelIndex()  # Return an invalid index if not found

# Function to find the index of the first value that goes below or above the specified thresholds
def find_threshold_index(lower_threshold,upper_threshold,values, start, end, step):
    for i in range(start, end, step):
        if values[i] < lower_threshold or values[i] > upper_threshold:
            return i
    return None


def update_first_peak_index(self, data, peaks_indices):
    """
    Scans the next 20 frames from the first peak to find a value below X% of the peak's value.
    If found, replaces the first peak's index with the new index.
    
    Parameters:
    - data: The original dataset as a numpy array.
    - peaks_indices: A numpy array containing the indices of the peaks.
    
    Returns:
    - A numpy array of the updated peak indices.
    """
    if len(peaks_indices) > 0:
        first_peak_index = peaks_indices[0]
        first_peak_value = data[first_peak_index]
        threshold_value = self.Pk_find_12.value()  * first_peak_value
        
        # Initialize a variable to keep track if a new index is found; assume none initially
        new_index = None
        
        # Scan the next X frames from the first peak
        range_scan = self.Pk_find_11.value() +1
        for i in range(first_peak_index + 1, min(first_peak_index + range_scan, len(data))):
            if data[i] < threshold_value:
                new_index = i
                break  # Stop scanning once a value below the threshold is found
        
        # Replace the peak's index with the new one if found
        if new_index is not None:
            peaks_indices[0] = new_index
            
    return peaks_indices

def update_last_peak_index(self, data, peaks_indices):
    """
    Scans the 20 frames before the last peak to find a value below x% of the peak's value.
    If found, replaces the last peak's index with the new index.
    
    Parameters:
    - data: The original dataset as a numpy array.
    - peaks_indices: A numpy array containing the indices of the peaks.
    
    Returns:
    - A numpy array of the updated peak indices.
    """
    if len(peaks_indices) > 0:
        last_peak_index = peaks_indices[-1]
        last_peak_value = data[last_peak_index-1]
        threshold_value = self.Pk_find_12.value()  * last_peak_value
        
        # Initialize a variable to keep track if a new index is found; assume none initially
        new_index = None
        
        # Scan the X frames before the last peak, moving backwards
        range_scan = self.Pk_find_11.value() +1
        for i in range(last_peak_index - 1, max(last_peak_index - range_scan, -1), -1):
            if data[i] < threshold_value:
                new_index = i
                break  # Stop scanning once a value below the threshold is found
        
        # Replace the peak's index with the new one if found
        if new_index is not None:
            peaks_indices[-1] = new_index
            
    return peaks_indices


def average_frames_within_dw(self):
    keys_list = list(self.IrIS_data.keys())
    N_frames  = self.avg_frames_within_dwell_N.value()
    #
    for i in range(len(self.IrIS_data)):
        # Check if the current element ends with '_Dw'
        if keys_list[i].endswith('_Dw'):# data already processed should not be averaged again            
            continue  # Skip to the next iteration
        #    
        data        = self.IrIS_data[keys_list[i]]['3DMatrix']
        peaks       = self.IrIS_Eval[i+1]['peaks']
        new_name    = f"{keys_list[i]}_AVG{N_frames}_Dw"
        total_intervals = 0
        for j in range(len(peaks)- 1):
            total_intervals += math.ceil((peaks[j+1]-peaks[j])/N_frames)
        #
        # total_intervals = sum(len(self.IrIS_Eval[i+1]['peaks']) - 1 for i in range(len(self.IrIS_data)))*10
        first_data_shape = self.IrIS_data[keys_list[0]]['3DMatrix'].shape
        averaged_data_shape = (total_intervals,) + first_data_shape[1:]
        averaged_data = np.zeros(averaged_data_shape, dtype=float) 
        time_avg = np.zeros(total_intervals, dtype=float)
        #
        time        = np.array(self.IrIS_Eval[i+1]['time'])
        frame_ID    = 0
        for j in range(len(peaks)- 1):
            intervals = math.floor((peaks[j+1]-peaks[j])/N_frames)
            for k in range(intervals):
                start_index = peaks[j]   + k*N_frames
                end_index   = start_index+ N_frames-1
                if end_index > data.shape[0]:
                    end_index -=1
                # Perform averaging and assign to the pre-initialized matrices
                averaged_data[frame_ID] = data[start_index:end_index].mean(axis=0)
                if k==0:
                    time_avg[frame_ID]      = time[start_index]
                else:
                    time_avg[frame_ID]      = time[end_index]
                frame_ID += 1
            #
            if math.ceil((peaks[j+1]-peaks[j])/N_frames) > math.floor((peaks[j+1]-peaks[j])/N_frames):
                print('Last interval does not have the same number of frames due to rounding')
                start_index             = peaks[j]   + (k+1)*N_frames
                averaged_data[frame_ID] = data[start_index:].mean(axis=0)
                time_avg[frame_ID]      = time[data.shape[0]-1]
                
                
            self.IrIS_data[new_name] = {
                        '3DMatrix': averaged_data.astype(np.uint16),
                        'mode': self.IrIS_data[keys_list[i]]['mode'],
                        'VxVy': self.IrIS_data[keys_list[i]]['VxVy'],
                        'binning': self.IrIS_data[keys_list[i]]['binning'],
                        'panel': self.IrIS_data[keys_list[i]]['panel'],
                        'average':self.IrIS_data[keys_list[i]]['average'],
                        'average_skip': self.IrIS_data[keys_list[i]]['average_skip'],
                        'delay': self.IrIS_data[keys_list[i]]['delay'],
                        'FOV': self.IrIS_data[keys_list[i]]['FOV'],
                        'C_offset': self.IrIS_data[keys_list[i]]['C_offset'],
                        'C_sens': self.IrIS_data[keys_list[i]]['C_sens'],
                        'C_sum': self.IrIS_data[keys_list[i]]['C_sum'],
                        'C_N_sum': self.IrIS_data[keys_list[i]]['C_N_sum'],
                        'fps': self.IrIS_data[keys_list[i]]['fps']/N_frames,
                        'fps_id': self.IrIS_data[keys_list[i]]['fps_id'],
                        'Resolution': self.IrIS_data[keys_list[i]]['Resolution'],
                        'Diff': self.IrIS_data[keys_list[i]]['Diff'],
                        'AcquisitionTime': np.array(time_avg),
                        'AcquisitionTime_abs': np.array(time_avg)}
    populate_IrIS_tree(self)

def average_dw(self):
    #
    keys_list = list(self.IrIS_data.keys())
    total_intervals = sum(len(self.IrIS_Eval[i+1]['peaks']) - 1 for i in range(len(self.IrIS_data)))
    first_data_shape = self.IrIS_data[keys_list[0]]['3DMatrix'].shape
    marging = self.IrIsAVg_dw_margin.value()
    averaged_data_shape = (total_intervals,) + first_data_shape[1:]
    averaged_data = np.zeros(averaged_data_shape, dtype=float)  
    time_dw = np.zeros(total_intervals, dtype=float)  
    dwell_time = np.zeros(total_intervals, dtype=float) 
    ch_dw = np.zeros(total_intervals)  
    new_name = f"{keys_list[0]}_Dw"
    #
    channel_offset = 0
    for i in range(len(self.IrIS_data)):
        data = self.IrIS_data[keys_list[i]]['3DMatrix']
        peaks = self.IrIS_Eval[i+1]['peaks']
        time = np.array(self.IrIS_Eval[i+1]['time'])
        
        for j in range(len(peaks) - 1):
            start_index = peaks[j] + marging
            end_index = peaks[j+1] - marging
            frame_index = j + channel_offset
            # Perform averaging and assign to the pre-initialized matrices
            averaged_data[frame_index] = data[start_index:end_index].mean(axis=0)
            time_dw[frame_index] = time[start_index]
            ch_dw[frame_index]   = i+1
            dwell_time[frame_index] = time[peaks[j + 1]] - time[peaks[j]]
            #
        channel_offset += len(peaks) - 1
        #
    self.IrIS_data[new_name] = {
                '3DMatrix': averaged_data.astype(np.uint16),
                'mode': self.IrIS_data[keys_list[i]]['mode'],
                'VxVy': self.IrIS_data[keys_list[i]]['VxVy'],
                'binning': self.IrIS_data[keys_list[i]]['binning'],
                'panel': self.IrIS_data[keys_list[i]]['panel'],
                'average':self.IrIS_data[keys_list[i]]['average'],
                'average_skip': self.IrIS_data[keys_list[i]]['average_skip'],
                'delay': self.IrIS_data[keys_list[i]]['delay'],
                'FOV': self.IrIS_data[keys_list[i]]['FOV'],
                'C_offset': self.IrIS_data[keys_list[i]]['C_offset'],
                'C_sens': self.IrIS_data[keys_list[i]]['C_sens'],
                'C_sum': self.IrIS_data[keys_list[i]]['C_sum'],
                'C_N_sum': self.IrIS_data[keys_list[i]]['C_N_sum'],
                'fps': self.IrIS_data[keys_list[i]]['fps'],
                'fps_id': self.IrIS_data[keys_list[i]]['fps_id'],
                'Resolution': self.IrIS_data[keys_list[i]]['Resolution'],
                'Diff': self.IrIS_data[keys_list[i]]['Diff'],
                'AcquisitionTime': np.array(time_dw),
                'AcquisitionTime_abs': np.array(time_dw),
                'ch_dw': ch_dw,
                'dwell_time': dwell_time
            }
    populate_IrIS_tree(self)

def find_pks_dw(self):
    #
    self.progressBar.setValue(25)
    if self.Pk_find_processl_all_check.isChecked():
        for i in range(len(self.IrIS_data)):
            find_pks_dw_process(self,i+1)
    else:
        find_pks_dw_process(self,self.Pk_find_channel.value())
    channel       = self.Pk_find_channel.value()
    time          = np.array(self.IrIS_Eval[channel]['time'])
    data          = self.IrIS_Eval[channel]['differences_1_perc']    
    # adjust dwell calculate transit ... 
    find_adjust_dwells(self)
    update_dwell_times_table(self)
    self.progressBar.setValue(100)
    plot_IrIS_eval(self)
        
def find_pks_dw_process(self,channel): 
    try:
        # Attempt to access 'time' for the specified channel
        time = np.array(self.IrIS_Eval[channel]['time'])
    except KeyError:
        # If 'time' is not found or 'channel' does not exist in 'IrIS_Eval', display an error message
        QMessageBox.critical(self, "Data Missing", "Process the data for this channel first")
        return  # Optionally return from the function if the error condition is met
    #       
    data          = self.IrIS_Eval[channel]['differences_1_perc']
    averages      = self.IrIS_Eval[channel]['averages']
    #
    if self.checkBox_Pk_find_range.isChecked():
        # if the option is selected the code should use mean values to define the range ... excluding the frames corresponding to the frame arriving and leaving
        # Find the length of the `averages` vector
        N = len(averages)
        # Calculate the start and end indices for the middle 10 values
        start_index = (N // 2) - 5
        end_index = (N // 2) + 5  # Python slicing is exclusive at the end
        # Calculate the mean of these 10 values
        middle_values_mean = np.mean(averages[start_index:end_index])
        #
        # go from the center towards the start and find the first value below 80% or above 120% ... then do the same towards the end
        # this will the define the range of interest
        # Define thresholds based on the previously calculated middle_values_mean
        lower_threshold = self.Pk_find_09.value() * middle_values_mean
        upper_threshold = self.Pk_find_10.value() * middle_values_mean
        #
        # Search from the center towards the beginning for the first value outside the thresholds
        index_from_center_to_beginning = find_threshold_index(lower_threshold,upper_threshold,averages, N//2, -1, -1)
        np_index_ini = np.array(index_from_center_to_beginning)
        # Search from the center towards the end for the first value outside the thresholds
        index_from_center_to_end = find_threshold_index(lower_threshold,upper_threshold,averages, N//2, N, 1)
        np_index_end = np.array(index_from_center_to_end)
        #
        # Print the results
        #
        if np_index_ini.dtype == object and np_index_ini.item() is None:
            np_index_ini = 0 
            # # Show a warning message
            # msg = QMessageBox()
            # msg.setIcon(QMessageBox.Warning)
            # msg.setWindowTitle("Peak Detection Warning")
            # msg.setText(f"No initial range found! Check channel {channel}")
            # msg.exec_()
            print(f"No initial range index found! Check channel {channel}")
        if np_index_end.dtype == object and np_index_end.item() is None:
            np_index_end = len(data)-1
            # Show a warning message
            # msg = QMessageBox()
            # msg.setIcon(QMessageBox.Warning)
            # msg.setWindowTitle("Peak Detection Warning")
            # msg.setText(f"No final range index found! Check channel {channel}")
            # msg.exec_() 
            print(f"No final range index found! Check channel {channel}")
        #   
        # Adjust data to the range of interest
        data_adjusted = data[np_index_ini:np_index_end]
    else:
        data_adjusted = data
        np_index_ini  = 0
    # 
   
    # Extract parameters from spin boxes
    height        = self.Pk_find_01.value() if self.Pk_find_01.value() >= 0 else None
    threshold     = self.Pk_find_02.value() if self.Pk_find_02.value() >= 0 else None
    distance      = self.Pk_find_03.value() if self.Pk_find_03.value() >= 0 else None
    prominence    = self.Pk_find_04.value() if self.Pk_find_04.value() >= 0 else None
    width         = self.Pk_find_05.value() if self.Pk_find_05.value() >= 0 else None
    wlen          = self.Pk_find_06.value() if self.Pk_find_06.value() >= 0 else None
    rel_height    = self.Pk_find_07.value() if self.Pk_find_07.value() >= 0 else None
    plateau_size  = self.Pk_find_08.value() if self.Pk_find_08.value() >= 0 else None

    # Call find_peaks with parameters from the GUI
    peaks, properties = find_peaks(data_adjusted, height=height, threshold=threshold, distance=distance,
                                   prominence=prominence, width=width, wlen=wlen, rel_height=rel_height,
                                   plateau_size=plateau_size)
    #
    if len(peaks) < 2 and (np_index_ini>0 or np_index_end<(len(data)-1)) and self.checkBox_Pk_find_range.isChecked():
        # Show a warning message
        # msg = QMessageBox()
        # msg.setIcon(QMessageBox.Warning)
        # msg.setWindowTitle("Peak Detection Warning")
        # msg.setText(f" {len(peaks)} peak was found with the specified range. Range set to full profile ... Check channel {channel}")
        # msg.show()
        # #
        print(f" {len(peaks)} peak was found with the specified range. Range set to full profile ... Check channel {channel}")
        # Call find_peaks with parameters from the GUI
        data_adjusted = data
        np_index_ini  = 0
        peaks, properties = find_peaks(data_adjusted, height=height, threshold=threshold, distance=distance,
                                       prominence=prominence, width=width, wlen=wlen, rel_height=rel_height,
                                       plateau_size=plateau_size)
        #
    if len(peaks) < 2:
        # # Show a warning message
        # msg = QMessageBox()
        # msg.setIcon(QMessageBox.Warning)
        # msg.setWindowTitle("Peak Detection Warning")
        # msg.setText(f" {len(peaks)} peak was found with the specified range. Check channel {channel}")
        # msg.show()
        # #
        print(f" {len(peaks)} peak was found with the specified range. Check channel {channel}")
        # Manually add peaks at the first and last positions of data_adjusted
        peaks = np.array([0,len(data_adjusted)-1])    
        
    #
    if self.checkBox_Pk_find_adj_1st_last.isChecked():
        # Convert to list for easier manipulations
        peaks_list = peaks.tolist()
        # Check and adjust for peaks with index below X 
        range_scan = self.Pk_find_11.value() +1
        if not any(peak < range_scan for peak in peaks_list):
            peaks_list.insert(0, 0)  # Add a peak at the start if none are within the first 10 indices
        else:
            # Keep only the last peak if more than one peak is within the first 10 indices
            early_peaks = [peak for peak in peaks_list if peak < range_scan]
            for peak in early_peaks[:-1]:  # Remove all but the last early peak
                peaks_list.remove(peak)
        
        # Adjust for the end of the data range
        if not any(peak > len(data_adjusted) - range_scan for peak in peaks_list):
            peaks_list.append(len(data_adjusted) - 1 + np_index_ini)  # Add a peak at the end if needed
        else:
            # Keep only the first peak if more than one peak is within the last 10 indices of the adjusted data
            late_peaks = [peak for peak in peaks_list if peak > len(data_adjusted) - range_scan + np_index_ini]
            for peak in late_peaks[1:]:  # Remove all but the first late peak
                peaks_list.remove(peak)
        # Convert back to numpy array if necessary
        peaks = np.array(peaks_list)
        # Adjust the indices of the found peaks to match their original positions
        peaks = peaks + np_index_ini 
        #
        peaks = update_first_peak_index(self,data, peaks)
        peaks = update_last_peak_index(self,data, peaks)
    else:
        peaks = peaks + np_index_ini 
    # 
    # peaks contains the indices of peaks in line_prof
    # properties is a dictionary containing properties of the peaks
    peaks = np.array(peaks, dtype=int)
    #
    # remove first and las (N) if requested
    # Remove elements
    # Ensure we don't attempt to remove more elements than the array contains
    Rem_ini = self.Pk_find_13.value()
    Rem_fin = self.Pk_find_14.value()
    if Rem_ini + Rem_fin <= len(peaks):
        peaks = peaks[Rem_ini:len(peaks)-Rem_fin]
    else:
        raise ValueError("Attempt to remove more elements than are present in the array.")

    #    
    self.IrIS_Eval[channel]['peaks'] = peaks

def find_adjust_dwells(self):
    total_intervals    = sum(len(self.IrIS_Eval[i+1]['peaks']) - 1 for i in range(len(self.IrIS_data)))
    self.Dw_pos_info   = np.zeros((total_intervals,17))
    #
    row_offset = 0 
    keys_list  = list(self.IrIS_data.keys())
    #
    for j in range(len(self.IrIS_data)):
        channel                 = j
        peaks                   = self.IrIS_Eval[channel+1]['peaks']
        time                    = np.array(self.IrIS_Eval[channel+1]['time'])
        data                    = self.IrIS_Eval[channel+1]['differences_1_perc']
        ref_source_time         = calculate_time_from_ref(self,keys_list[j])
        time_since_cal, ac_Cal  = time_since_calibration(self, ref_source_time)
        current_ac              = calculate_current_activity(ac_Cal, time_since_cal)
        Scale_ac                = current_ac/10
        #
        #  
        #
        for i in range(len(peaks) - 1):
            row_index = i + row_offset
            # Ensure the table has enough rows
            if row_index >= self.Dwells_table.rowCount():
                self.Dwells_table.insertRow(self.Dwells_table.rowCount())
            #
            # store peak values
            self.Dw_pos_info[row_index,0] = peaks[i]
            self.Dw_pos_info[row_index,1] = peaks[i+1]
            # check the number of frames to see if is possible to correctfor transit ... only dwelll longer than 0.5s
            interval_frames = peaks[i + 1] - peaks[i]
            #
            if interval_frames > 10:
                mid_point   = round(peaks[i] + interval_frames // 2)
                start_index = max(mid_point - 2, 0)  # Ensure not going below array bounds
                end_index   = min(mid_point + 3, len(data))  # Ensure not exceeding array bounds
                average_value = np.mean(data[start_index:end_index])
                # transit threshold 1.1 to start
                self.Dw_pos_info[row_index,2] = peaks[i]
                for k in range(peaks[i],peaks[i]+10):
                    if data[k] < average_value*1.1:
                        self.Dw_pos_info[row_index,2] = k
                        break
                #
                self.Dw_pos_info[row_index,3] = peaks[i+1]
                for k in range(peaks[i+1],peaks[i+1]-10,-1):
                    if data[k] < average_value*1.1:
                        self.Dw_pos_info[row_index,3] = k
                        break
            else:
                self.Dw_pos_info[row_index,2] = peaks[i]
                self.Dw_pos_info[row_index,3] = peaks[i+1]
            #
            # time
            self.Dw_pos_info[row_index,4] = time[int(self.Dw_pos_info[row_index,0])]
            self.Dw_pos_info[row_index,5] = time[int(self.Dw_pos_info[row_index,1])]
            self.Dw_pos_info[row_index,6] = time[int(self.Dw_pos_info[row_index,2])]
            self.Dw_pos_info[row_index,7] = time[int(self.Dw_pos_info[row_index,3])]
            #
            # Dwell time
            self.Dw_pos_info[row_index,8] = self.Dw_pos_info[row_index,7] - self.Dw_pos_info[row_index,6]
            # Transit time
            if i ==0 :
                self.Dw_pos_info[row_index,9] = 0
            else:
                self.Dw_pos_info[row_index,9] = time[int(self.Dw_pos_info[row_index,2])] - time[int(self.Dw_pos_info[row_index-1,3])]
            #
            # total time
            self.Dw_pos_info[row_index,10] = self.Dw_pos_info[row_index,8] + self.Dw_pos_info[row_index,9]
            # total time 10 Ci - scale only the dwell time not the transit
            self.Dw_pos_info[row_index,11] = self.Dw_pos_info[row_index,8]*Scale_ac + self.Dw_pos_info[row_index,9]
            # Channel
            self.Dw_pos_info[row_index,15] = channel+1 
            # Activity
            self.Dw_pos_info[row_index,16] = current_ac
        row_offset += len(peaks) - 1

 
def update_dwell_times_table(self):
    # Set the number of rows in the table based on the number of rows in your numpy array
    self.Dwells_table.setRowCount(self.Dw_pos_info.shape[0])
    for row_index in range(self.Dw_pos_info.shape[0]):
        # channel
        data_formatted = f"{self.Dw_pos_info[row_index,15]:.0f}"
        self.Dwells_table.setItem(row_index, 0, QTableWidgetItem(f"{data_formatted}")) 
        # Time-1 (s) 
        data_formatted = f"{self.Dw_pos_info[row_index,6]:.2f}"
        self.Dwells_table.setItem(row_index, 1, QTableWidgetItem(f"{data_formatted}")) 
        # Time-1 (s) 
        data_formatted = f"{self.Dw_pos_info[row_index,7]:.2f}"
        self.Dwells_table.setItem(row_index, 2, QTableWidgetItem(f"{data_formatted}")) 
        # Transit time (s)  
        data_formatted = f"{self.Dw_pos_info[row_index,9]:.2f}"
        self.Dwells_table.setItem(row_index, 3, QTableWidgetItem(f"{data_formatted}")) 
        # Dwell time without transit (s)  
        data_formatted = f"{self.Dw_pos_info[row_index,8]:.2f}"
        self.Dwells_table.setItem(row_index, 4, QTableWidgetItem(f"{data_formatted}")) 
        # Dwell time total (s)  
        data_formatted = f"{self.Dw_pos_info[row_index,10]:.2f}"
        self.Dwells_table.setItem(row_index, 5, QTableWidgetItem(f"{data_formatted}")) 
        # Dwell time total (s)  10 Ci
        data_formatted = f"{self.Dw_pos_info[row_index,11]:.2f}"
        self.Dwells_table.setItem(row_index, 6, QTableWidgetItem(f"{data_formatted}")) 
        # Soruce activity during measurement  
        data_formatted = f"{self.Dw_pos_info[row_index,16]:.2f}"
        self.Dwells_table.setItem(row_index, 10, QTableWidgetItem(f"{data_formatted}")) 

def add_row_dw_table(self):
    position          = self.dw_table_pos.value()-1
    zero_row          = np.zeros(self.Dw_pos_info.shape[1])
    self.Dw_pos_info  = np.insert(self.Dw_pos_info, position, zero_row, axis=0)
    update_dwell_times_table(self)

def remove_row_dw_table(self):
    position          = self.dw_table_pos.value()-1
    zero_row          = np.zeros(self.Dw_pos_info.shape[1])
    self.Dw_pos_info  = np.delete(self.Dw_pos_info, position, axis=0)
    update_dwell_times_table(self)
    
def downsample_array(data, new_dim=(16, 16)):
    """
    Downsample a 3D numpy array by averaging, without using scipy.
    
    Parameters:
    - data: 3D numpy array to downsample.
    - new_dim: Tuple indicating the new dimensions for the 2nd and 3rd axes.
    
    Returns:
    - Downsampled 3D numpy array.
    """
    # Calculate the size of blocks to average over in the 2nd and 3rd dimensions
    block_size_y = data.shape[1] / new_dim[0]
    block_size_x = data.shape[2] / new_dim[1]
    
    # Initialize the downsampled array
    downsampled = np.zeros((data.shape[0], new_dim[0], new_dim[1]))
    
    for z in range(data.shape[0]):
        for y in range(new_dim[0]):
            for x in range(new_dim[1]):
                # Calculate the start and end indices for each block
                start_y = int(round(y * block_size_y))
                end_y = int(round((y + 1) * block_size_y))
                start_x = int(round(x * block_size_x))
                end_x = int(round((x + 1) * block_size_x))
                
                # Extract the block and calculate its mean
                block = data[z, start_y:end_y, start_x:end_x]
                downsampled[z, y, x] = block.mean()
    
    return downsampled




    
def save_eval_to_csv(self):
    channel  = self.Pk_find_channel.value()
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    fileName, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)", options=options)
    
    if fileName:
        if not fileName.endswith('.csv'):
            fileName += '.csv'
        # Creating a DataFrame from the dictionary
        df = pd.DataFrame(self.IrIS_Eval[channel])
        # Save the DataFrame to CSV
        df.to_csv(fileName, index=False)
        QMessageBox.information(self, "Success", f"File was successfully saved to {fileName}")
    else:
        QMessageBox.warning(self, "Cancelled", "Operation was cancelled.")
        
        

