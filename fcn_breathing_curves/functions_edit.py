# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 14:40:30 2025

@author: lars.daenen
"""
import os
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QVBoxLayout, QFileDialog
from fcn_breathing_curves.functions_import import addColumns


######################
### INITIALIZATION ###
######################

def getColumnIndexByName(self, column_name):
    """Get index of column in tableWidget by name"""
    for i in range(self.tableViewCSV_BrCv.columnCount()):
        if self.tableViewCSV_BrCv.horizontalHeaderItem(i).text() == column_name:
            return i
    return None


def on_fourierSlider_change(self):
    cutoff = self.fourier_cutoffs[self.threshFourierSlider.value()]
    self.threshFourierValue.setText(f"{cutoff:.2e} Hz")
    # self.threshFourierSlider.setToolTip(f"Cutoff frequency: {cutoff:.2e} Hz")


def getDataframeFromTable(self):
    """Extract data from tableWidget and convert to pandas.DataFrame"""
    x_col = self.editXAxis_BrCv.currentText()
    y_col = "amplitude"

    # Get column indices based on selected column names
    x_index = getColumnIndexByName(self, x_col)
    y_index = getColumnIndexByName(self, y_col)
    
    if x_index is None or y_index is None:
        return
        
    # Extract data from the table widget
    data = {}
    for col in range(self.tableViewCSV_BrCv.columnCount()):
        column_name = self.tableViewCSV_BrCv.horizontalHeaderItem(col).text()
        data[column_name] = []
        for row in range(0, self.tableViewCSV_BrCv.rowCount()):
            item = self.tableViewCSV_BrCv.item(row, col)
            if item:
                try:
                    data[column_name].append(float(item.text()))
                except:
                    data[column_name].append(item.text())

    self.dfEdit_BrCv = pd.DataFrame(data)
    self.dfEdit_BrCv_copy = self.dfEdit_BrCv.copy()
    
    
def init_BrCv_edit(self):
    if self.tabWidget_BrCv.currentIndex() == 1 and self.BrCvTab_index == 0:
        self.BrCvTab_index = 1
        # try:
        on_fourierSlider_change(self)
        self.threshFourierSlider.valueChanged.connect(lambda:on_fourierSlider_change(self))
        getDataframeFromTable(self)
        initXRange(self)
        plotViewData_BrCv_edit(self)   
        # except:
        #     return

  
def initXRange(self):
    import math
    try:
        x_col = self.editXAxis_BrCv.currentText()
        min_val = math.floor(self.dfEdit_BrCv[x_col].min())
        max_val = math.ceil(self.dfEdit_BrCv[x_col].max())
    
        self.editXMinSlider_BrCv.setMinimum(min_val)
        self.editXMinSlider_BrCv.setMaximum(max_val - 1)
        self.editXMinSlider_BrCv.setValue(min_val)
        
        self.editXMaxSlider_BrCv.setMinimum(min_val + 1)
        self.editXMaxSlider_BrCv.setMaximum(max_val)
        self.editXMaxSlider_BrCv.setValue(max_val)
    except:
        return


############
### CROP ###
############
    
def clipCycles(self):
    """Function to remove non-complete cycles at the beginning/end
        Input:
            - df
        Ouput:
            - df without non-complete cycles at the beginning/end"""
    
    
    if "instance" in self.dfEdit_BrCv.columns:
        # This function is only executed if instance information is available
        # Otherwise return original dataframe
        df = self.dfEdit_BrCv
        min_, max_ = int(df["instance"].min()), int(df["instance"].max())
        for i in range(min_, max_):
            if ((df[df["instance"] == i]["mark"] == "P_min").sum() == 0) or \
                ((df[df["instance"] == i]["mark"] == "Z").sum() == 0):
                min_ = i + 1
                break

        for i in range(max_, min_, -1):
            if ((df[df["instance"] == i]["mark"] == "E").sum() == 0):
                max_ = i - 1
                break

        df = df[(df["instance"] >= min_) & (df["instance"] <= max_)]
        df.loc[:, "timestamp"] -= df["timestamp"].min()
        df.loc[:, "time"] -= df["time"].min()
        df.loc[:, "instance"] -= df["instance"].min()
        df = df.reset_index(drop=True)
        self.dfEdit_BrCv = df
    else:
        return


def cropRange_BrCv_edit(self):
    self.dfEdit_BrCv_copy = self.dfEdit_BrCv.copy()
    
    x_col = self.editXAxis_BrCv.currentText()
    df = self.dfEdit_BrCv
    self.dfEdit_BrCv = df[(df[x_col] >= self.lower_bound) & (df[x_col] <= self.upper_bound)]

    if self.clipCycles_BrCv.isChecked():
        clipCycles(self)

    initXRange(self)
    plotViewData_BrCv_edit(self, self.dfEdit_BrCv)
    

def resetRange_BrCv_edit(self):
    delattr(self, "dfEdit_BrCv")
    init_BrCv_edit(self)
    

##################
### OPERATIONS ###
################## 

def setMinZero(self):
    self.dfEdit_BrCv["amplitude"] -= self.dfEdit_BrCv["amplitude"].min()
    
    
def scaleFreq(self):

    df = self.dfEdit_BrCv.copy()
    
    time_step_init = df.loc[1, "timestamp"] - df.loc[0, "timestamp"]
    time_step_ms = df.loc[1, "time"] - df.loc[0, "time"]
    time_step = int(time_step_init * self.scaleFreq_BrCv.value())
    scale_factor = time_step_init / time_step

    col_names = ["timestamp", "amplitude", "phase", "cycle_time", "instance", "ttlin", "ttlout"] 
    df = df[df.columns.intersection(col_names)] 

    if "instance" in df.columns:
        t0 = 0
        df_scaled = pd.DataFrame()
        for i in df["instance"].unique():
            df_i = df[df["instance"] == i].copy()
            
            # Convert the time column to TimedeltaIndex for resampling
            df_i["timedelta"] = pd.to_timedelta(df_i["timestamp"], unit='ms')

            # Create a new index for resampling at 1ms intervals
            new_index = pd.timedelta_range(start=df_i["timedelta"].min(), end=df_i["timedelta"].max(), freq='ms')

            # Reindex the DataFrame to the new index, keeping original data points
            df_i = df_i.set_index("timedelta").reindex(new_index.union(df_i["timedelta"])).sort_index()
        
            # Interpolate only the missing values
            df_i = df_i.interpolate(method='linear', limit_area='inside')
            df_i = df_i.resample(f"{time_step}ms").median()
            if "ttlin" in df_i.columns:
                df_i["ttlin"] = df_i["ttlin"].round()

            df_i["timestamp"] = np.linspace(t0, t0 + (len(df_i) - 1) * time_step_init, len(df_i))
            df_i["time"] = np.linspace(t0 / 1e3, t0 / 1e3 + (len(df_i) - 1) * time_step_ms, len(df_i))
            t0 = df_i["timestamp"].max() + time_step_init
            df_i = df_i.reset_index(drop=True)

            # Define the mark column
            df_i["mark"] = np.nan
            if self.curve_origin == "created":
                df_i.loc[0, "mark"] = "P_min"
                max_idx = df_i["amplitude"].idxmax()
                df_i.loc[max_idx, "mark"] = "Z"
                df_i.loc[len(df_i) - 1, "mark"] = "E"
            elif self.curve_origin == "measured":
                df_i.loc[0, "mark"] = "Z"
                min_idx = df_i["amplitude"].idxmin()
                df_i.loc[min_idx, "mark"] = "P_min"
                df_i.loc[len(df_i) - 1, "mark"] = "E"

            # Concatenate the scaled instance DataFrame
            df_scaled = pd.concat([df_scaled, df_i], ignore_index=True)

        df_scaled["acq"] = np.nan
        if "acq" in self.dfEdit_BrCv.columns and self.dfEdit_BrCv["acq"].sum() > 0:
            timestamps = self.dfEdit_BrCv.loc[self.dfEdit_BrCv["acq"] == 1, "timestamp"]
            for t in timestamps:
                closest_t = (df_scaled["timestamp"] - t / self.scaleFreq_BrCv.value()).abs().idxmin()
                df_scaled.loc[closest_t, "acq"] = 1 

        self.dfEdit_BrCv = df_scaled
        del df_i, df_scaled

    else:
        if "mark" in df.columns:
            mark_timestamps_P = df.loc[df["mark"] == "P_min", "timestamp"].tolist()
            mark_timestamps_Z = df.loc[df["mark"] == "Z", "timestamp"].tolist()
            mark_timestamps_E = df.loc[df["mark"] == "E", "timestamp"].tolist()

        # Convert the time column to TimedeltaIndex for resampling
        df["timedelta"] = pd.to_timedelta(df["timestamp"], unit='ms')
        
        # Create a new index for resampling at 1ms intervals
        new_index = pd.timedelta_range(start=df["timedelta"].min(), end=df["timedelta"].max(), freq='ms')
        
        # Reindex the DataFrame to the new index, keeping original data points
        df = df.set_index("timedelta").reindex(new_index.union(df["timedelta"])).sort_index()
        
        # Interpolate only the missing values
        df = df.interpolate(method='linear', limit_area='inside')
        df = df.resample(f"{time_step}ms").median()
        if "instance" in df.columns and "ttlin" in df.columns:
            df["instance"] = df["instance"].round()
            df["ttlin"] = df["ttlin"].round()

        df["timestamp"] = np.linspace(0, (len(df) - 1) * time_step_init, len(df))
        df["time"] = np.linspace(0, (len(df) - 1) * time_step_ms, len(df))

        df = df.reset_index(drop=True)

        if "mark" in df.columns:
            df["mark"] = np.nan
            for t in mark_timestamps_P:
                df.loc[df.iloc[(df['timestamp']-t*scale_factor).abs().argsort()].index[0], "mark"] = "P_min"
            for t in mark_timestamps_Z:
                df.loc[df.iloc[(df['timestamp']-t*scale_factor).abs().argsort()].index[0], "mark"] = "Z"
            for t in mark_timestamps_E:
                df.loc[df.iloc[(df['timestamp']-t*scale_factor).abs().argsort()].index[0], "mark"] = "E"
        
        df_scaled["acq"] = np.nan
        if "acq" in self.dfEdit_BrCv.columns and self.dfEdit_BrCv["acq"].sum() > 0:
            timestamps = self.dfEdit_BrCv.loc[self.dfEdit_BrCv["acq"] == 1, "timestamp"]
            for t in timestamps:
                closest_t = (df_scaled["timestamp"] - t / self.scaleFreq_BrCv.value()).abs().idxmin()
                df_scaled.loc[closest_t, "acq"] = 1 

        self.dfEdit_BrCv = df
    del df
    
    
def scaleAmpl(self):
    """Function to scale amplitude of the fragment
        Input:
            - df: fragment to scale [pandas.dataframe]
            - scaleAmpl_BrCv: factor to scale amplitude [float],
        Output:
            - pandas.DataFrame with scaled amplitude
    """
    scale_factor = self.scaleAmpl_BrCv.value()
    self.dfEdit_BrCv["amplitude"] *= scale_factor
    
    
def shiftAmpl(self):
    """Function to shift amplitude of the fragment
        Input:
            - df: fragment to shift [pandas.dataframe]
            - shiftAmpl_BrCv: value to shift amplitude [float],
        Output:
            - pandas.DataFrame with shifted amplitude
    """
    self.dfEdit_BrCv["amplitude"] += self.shiftAmpl_BrCv.value()
    
    
def setMaxThresh(self):
    """Function to clip maximum amplitude of the fragment
        Input:
            - df: fragment to clip maximum amplitude [pandas.dataframe]
            - maxAmplThresh_BrCv: value to clip amplitude [float],
        Output:
            - pandas.DataFrame with clipped amplitude
    """
    t = self.maxAmplThresh_BrCv.value()
    self.dfEdit_BrCv.loc[self.dfEdit_BrCv["amplitude"] > t, "amplitude"] = t
    

def applyBreathhold(self):
    """Function to insert breathhold in the fragment
        Input:
            - df: fragment to insert breathhold [pandas.dataframe]
            - breathholdStart: timestamp at which to insert breathhold [float],
            - breathholdDuration: duration of breathhold [float],
        Output:
            - pandas.DataFrame with shifted amplitude
    """
    
    df = self.dfEdit_BrCv
    x_col = self.editXAxis_BrCv.currentText()
    # Get the breathhold duration value
    duration = self.breathholdDuration.value()

    timestep_ms = df.loc[1, "timestamp"] - df.loc[0, "timestamp"]
    timestep = df.loc[1, "time"] - df.loc[0, "time"]
    
    if x_col == "timestamp":
        i_start = int(self.breathholdStart.value() / timestep_ms)
    else:
        i_start = int(self.breathholdStart.value() / timestep)

    if "instance" in df.columns:
        # Get the index of the maximum amplitude for each instance
        max_idx = df.groupby(by="instance")["amplitude"].idxmax().tolist()
        idx = min(max_idx, key=lambda x:abs(x-i_start)) 
    else:
        idx = (df[x_col] - self.breathholdStart.value()).abs().idxmin()

    n_time = int(duration / timestep_ms * 1e3) 
        
    # Copy the row at breathhold index and repeat it n_time times
    b = pd.concat([df.iloc[idx:idx+1]] * n_time)
    b = b.reset_index(drop=True)
    
    for n in range(n_time):
        b.loc[n, "timestamp"] += n * timestep_ms
        b.loc[n, "time"] += n * timestep
    
    df.loc[idx:, "timestamp"] += (n + 1) * timestep_ms
    df.loc[idx:, "time"] += (n + 1) * timestep
    
    # Insert the copied rows into the original DataFrame
    df = pd.concat([df.iloc[:idx], b, df.iloc[idx:]]).reset_index(drop=True)
    self.dfEdit_BrCv = df


def smoothAmpl(self):
    if self.smooth_method_BrCv.currentText() == "Fourier":
        threshold = self.fourier_cutoffs[self.threshFourierSlider.value()]
        fourier = np.fft.rfft(self.dfEdit_BrCv["amplitude"])
        frequencies = np.fft.rfftfreq(self.dfEdit_BrCv["amplitude"].size, d=self.dfEdit_BrCv["timestamp"].diff().iloc[1])#20e-3/self.dfEdit_BrCv["amplitude"].size)
        fourier[frequencies > threshold] = 0
        smooth_signal = np.fft.irfft(fourier, n=self.dfEdit_BrCv["amplitude"].size)
        self.dfEdit_BrCv["amplitude"] = smooth_signal
        
    if self.smooth_method_BrCv.currentText() == "Uniform":
        self.dfEdit_BrCv["amplitude"] = uniform_filter1d(self.dfEdit_BrCv["amplitude"], size=self.smooth_size_BrCv.value())
    elif self.smooth_method_BrCv.currentText() == "Median":
        self.dfEdit_BrCv["amplitude"] = median_filter(self.dfEdit_BrCv["amplitude"], size=self.smooth_size_BrCv.value())
    

def applyOperations(self):
    """Function to apply operation to the fragment
        Input:
            - df: fragment to apply operations [pandas.dataframe]
            - breathholdStart: timestamp at which to insert breathhold [float],
            - breathholdDuration: duration of breathhold [float],
        Output:
            - pandas.DataFrame with shifted amplitude
    """
    
    self.dfEdit_BrCv_copy = self.dfEdit_BrCv.copy()
    
    if self.scaleAmpl_BrCv.value() != 1:
        scaleAmpl(self)
        
    if self.shiftAmpl_BrCv.value() != 0:
        shiftAmpl(self)

    if self.smooth_BrCv.isChecked():
        smoothAmpl(self)

    if self.scaleFreq_BrCv.value() != 1:
        scaleFreq(self)
 
    if self.applyBreathhold.isChecked():
        applyBreathhold(self)
        
    # Set minimum value to zero, to get relative amplitudes
    if self.setMinZero_BrCv.isChecked():
        setMinZero(self)
        
    setMaxThresh(self)
    
    # Calculate additional columns for the edited dataframe
    self.dfEdit_BrCv = addColumns(self, self.dfEdit_BrCv)

    # Reset the plot view to the new data range
    initXRange(self)
    plotViewData_BrCv_edit(self)
    
    
def undoOperations(self):
    """Function to undo the last operations applied to the fragment
        Input: 
            - dfEdit_BrCv_copy: latest copy of the fragment [pandas.dataframe]
        Output:
            - pandas.DataFrame of fragment with operations undone [pandas.dataframe]
    """

    self.dfEdit_BrCv = self.dfEdit_BrCv_copy.copy()
    initXRange(self)
    plotViewData_BrCv_edit(self)
    
    
####################
###### EXPORT ######
####################

def copyCurve(self):
    """Function to copy fragment N times
        Input: 
            - df: fragment to copy [pandas.dataframe]
            - N: number of times to copy [int],
        Output:
            - pandas.DataFrame with N copies of df
    """
    
    df = self.dfEdit_BrCv
    N = self.copyCurve_BrCv.value()
    timestep = df.iloc[1]["timestamp"] - df.iloc[0]["timestamp"]
    
    if "instance" in df.columns and N > 1 and self.curve_origin == "measured":
        # If instance information available, scale last cycle from minimum
        # until the end to ensure that the beginning and end of fragment match
        min1 = df[df["instance"] == df["instance"].max()]["amplitude"].min()
        min1_idx = df[df["instance"] == df["instance"].max()]["amplitude"].idxmin()
        max1 = df.iloc[-1]["amplitude"]
        max2 = df.iloc[0]["amplitude"]
    
        scale = (max2 - min1) / (max1 - min1)
        shift = max2 - max1 * (max2 - min1) / (max1 - min1)
        df.loc[min1_idx:, "amplitude"] = df.loc[min1_idx:, "amplitude"] * scale + shift
    
    df_mult = df.copy()

    for i in range(N - 1):
        # Copy fragment N times
        df_copy = df.copy()
        df_copy["timestamp"] += df_mult["timestamp"].max() + timestep
        df_copy["time"] += df_mult["time"].max() + timestep / 1000
        if "instance" in df.columns:
            df_copy["instance"] += df_mult["instance"].max()
        df_mult = pd.concat([df_mult, df_copy]).reset_index(drop=True)

    self.dfEdit_BrCv = df_mult
    
    
def exportData(self):
    """Function to export all the columns of the edited fragment to a CSV file
        Input:
            - df: fragment to apply operations [pandas.dataframe]
            - breathholdStart: timestamp at which to insert breathhold [float],
            - breathholdDuration: duration of breathhold [float],
        Output:
            - pandas.DataFrame with shifted amplitude
    """
    
    if not hasattr(self, "dfEdit_BrCv"):
        try:
            getDataframeFromTable(self)
        except:
            return
    self.dfEdit_BrCv_copy = self.dfEdit_BrCv.copy()
    # Copy the fragment N times
    copyCurve(self)
    # Prompt user to select a folder
    options = QFileDialog.Options()
    folder = QFileDialog.getExistingDirectory(self, options=options)
    # Save the DataFrame to a CSV file in the selected folder
    fileName = os.path.join(folder, self.editExportFile_BrCv.text()+".csv")
    self.dfEdit_BrCv.to_csv(fileName)
    # Reset the dataframe to one copy
    undoOperations(self)
    
from scipy.ndimage import uniform_filter1d, median_filter
    
def exportGCODE(self):
    # Prompt user to select a folder
    self.dfEdit_BrCv_copy = self.dfEdit_BrCv.copy()
    folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
    if not folder_path:
        return  # User canceled, exit the function

    # Get the file name 
    file_name = self.editExportFile_BrCv.text()
    file_path = os.path.join(folder_path, file_name + ".csv")
    
    # Copy the fragment N times and extract timestamp and amplitude data
    copyCurve(self)
    df = self.dfEdit_BrCv[["timestamp", "amplitude"]]
    if "acq" not in self.dfEdit_BrCv.columns:
        self.dfEdit_BrCv["acq"] = np.nan
    
    # Convert the time column to TimedeltaIndex for resampling
    time_col = df.columns[0]
    df[time_col] = pd.to_timedelta(df[time_col], unit=self.timeUnitCSV_BrCv.currentText())
    
    if self.interp_BrCv.isChecked():
        # Create a new index for resampling at 0.1s intervals
        freq = int(self.interp_value_BrCv.value())
        new_index = pd.timedelta_range(start=df[time_col].min(), end=df[time_col].max(), freq=f'{freq}L')

        # Reindex the DataFrame to the new index, keeping original data points
        df = df.set_index(time_col).reindex(new_index.union(df[time_col])).sort_index()
        
        # Interpolate only the missing values
        df = df.interpolate(method='linear', limit_area='inside')
        
        # Ensure the original time points are not modified
        df.loc[df.index.isin(new_index) == False, :] = df.loc[df.index.isin(new_index) == False, :].fillna(method='ffill').fillna(method='bfill')
        
        df.reset_index(inplace=True)

    df.rename(columns={'index': time_col}, inplace=True)
    
    # Calculate velocity and acceleration for each column
    results = pd.DataFrame()
    results[time_col] = df[time_col].dt.total_seconds()
    axis_labels = ['X', 'Y', 'Z']  # Define axis labels

    if self.dfEdit_BrCv["acq"].sum() > 0:
        timestamps = self.dfEdit_BrCv.loc[self.dfEdit_BrCv["acq"] == 1, "time"]
        for t in timestamps:
            closest_t = (df[time_col].dt.total_seconds() - t).abs().idxmin()
            df.loc[closest_t, "acq"] = 1 
    else:
        df["acq"] = np.nan

    # Write G-code file
    for col in df.columns[1:2]:
        df["diff"] = df[col].diff().shift(-1)
        for i in range(len(df[col]) - 1):
            if df.loc[i, "diff"] < 1e-3:
                df.loc[i, col] += np.random.choice([1, 1], 1) * np.random.choice(list(range(1, 1000)), 1) * 1e-5
        results[col] = df[col]

        # Calculate average speed
        vel = df[col].diff().shift(-1) / df[time_col].diff().shift(-1).dt.total_seconds()
        vel.iloc[-1] = vel.iloc[-2]  # Copy the second last value to the last element
        results[f'{col}_vel'] = vel
        # Calculate speed in mm/min
        results[f'{col}_speed'] = abs(vel) * 60 
        
        # Calculate acceleration
        accel = vel.diff() / df[time_col].diff().dt.total_seconds()
        accel.iloc[-1] = accel.iloc[-2]  # Copy the second last value to the last element
        results[f'{col}_accel'] = accel

    results["acq"] = df["acq"]
     
    # Save results to CSV file
    try:
        results.to_csv(file_path, index=False, mode='w')
    except:
        return
    #
    gcode_file_path = os.path.join(folder_path, file_name + ".gcode")
    gcode_lines = ["G90"]  # Initialize G-code lines with absolute positioning command
    # Write G-code file
    for i, row in results.iterrows():
        if i == 0:
            continue  # Skip the first row for G-code generation
        # Calculate speed in mm per minute
        speed = row[f'{df.columns[1]}_speed'] * np.sqrt(len(axis_labels))
        # Prepare G-code line
        gcode_line = f"G0 F{speed:.8f}"
        for j, col in enumerate(axis_labels):
            if j < len(axis_labels):
                gcode_line += f" {axis_labels[j]}{row[f'{df.columns[1]}']:.8f}"  # X, Y, Z, U, W
            else:
                gcode_line += f" {chr(85 + j)}{row[f'{df.columns[1]}']:.8f}"  # Continue with U, V, W, etc. if more than 5 columns
        gcode_lines.append(gcode_line)

    # Write G-code lines to the file
    with open(gcode_file_path, 'w') as gcode_file:
        gcode_file.write('\n'.join(gcode_lines))

    # Set the DataFrame back to non-interpolated state
    undoOperations(self)
    
    
################
### PLOTTING ###
################
def onclick(self, event):
    """Function to handle mouse click events on the plot"""
    x_col = self.editXAxis_BrCv.currentText()
    if event.button == 1:  # Left click
        if "acq" not in self.dfEdit_BrCv.columns:
            self.dfEdit_BrCv["acq"] = np.nan
        x = event.xdata
        self.dfEdit_BrCv.loc[(self.dfEdit_BrCv[x_col] - x).abs().idxmin(), "acq"] = 1
    elif event.button == 3:  # Right click
        x = event.xdata
        if "acq" in self.dfEdit_BrCv.columns and self.dfEdit_BrCv["acq"].sum() > 0:
            delete_idx = (self.dfEdit_BrCv.loc[self.dfEdit_BrCv["acq"] == 1, x_col] - x).abs().idxmin()
            self.dfEdit_BrCv.loc[delete_idx, "acq"] = np.nan
    plotViewData_BrCv_edit(self)


def plotViewData_BrCv_edit(self, df=None):
    
    x_col = self.editXAxis_BrCv.currentText()
    y_col = "amplitude"
    
    self.lower_bound = self.editXMinSlider_BrCv.value()
    self.upper_bound = self.editXMaxSlider_BrCv.value()
    
    if self.lower_bound >= self.upper_bound:
        initXRange(self)
        plotViewData_BrCv_edit(self)
        
    if df is None:
        df = self.dfEdit_BrCv

    x_data = df[x_col][(df[x_col] >= self.lower_bound) & (df[x_col] <= self.upper_bound)]
    y_data = df[y_col][(df[x_col] >= self.lower_bound) & (df[x_col] <= self.upper_bound)]

    self.plot_fig = Figure()  # Create a figure for the first time
    ax = self.plot_fig.add_subplot(111) 
    
    # Set plot background to transparent
    ax.patch.set_alpha(0.0)
    self.plot_fig.patch.set_alpha(0.0)
    
    # Customize text and axes properties
    ax.tick_params(colors='white', labelsize=self.selected_font_size-2)  # White ticks with larger text
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')

    # Plot the data
    ax.set_xlim(np.min(x_data), np.max(x_data))
    ax.plot(x_data, y_data, label=f'{x_col} vs {y_col}')
    if "acq" in self.dfEdit_BrCv.columns and self.dfEdit_BrCv["acq"].sum() > 0:
        x_acq = self.dfEdit_BrCv.loc[self.dfEdit_BrCv["acq"] == 1, x_col]
        for x in x_acq:
            if x > np.min(x_data) and x < np.max(x_data):
                ax.axvline(x, color='red', label="Acquisition Timestamps")
                if x_col == "timestamp":
                    ax.fill_between(x=[x, x + 6000], y1=np.min(y_data), y2=np.max(y_data), facecolor="pink", alpha=0.5)
                else:
                    ax.fill_between(x=[x, x + 6], y1=np.min(y_data), y2=np.max(y_data), facecolor="pink", alpha=0.5)

    ax.set_xlabel(x_col, fontsize=self.selected_font_size)
    ax.set_ylabel(y_col, fontsize=self.selected_font_size)

    # Create a canvas and toolbar
    canvas = FigureCanvas(self.plot_fig)
    canvas.setStyleSheet("background-color:Transparent;")
    canvas.mpl_connect('button_press_event', lambda event: onclick(self, event))

    # Check if the container has a layout, set one if not
    container = self.editAxView_BrCv
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
    container.layout().addWidget(canvas)
    canvas.draw()
    
     
