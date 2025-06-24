import numpy as np
from PyQt5.QtWidgets import QVBoxLayout, QFileDialog, QMessageBox, QWidget
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from scipy.signal import find_peaks
from PyQt5.QtCore import QModelIndex, Qt, QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel
from fcn_display.Data_tree_general import on_DataTreeView_clicked


def aggregate_channel_data(self, data_key):
    # Initialize empty arrays for the data and time
    aggregated_data = np.array([], dtype=float)
    aggregated_time = np.array([], dtype=float)
    
    # Sort keys if a sort_key function is provided, else use keys as they are
    keys_list  = list(self.IrIS_Eval.keys())
    last_index = len(keys_list) - 1
    for i, channel_key in enumerate(keys_list):
        channel_data = np.atleast_1d(self.IrIS_Eval[channel_key][data_key])
        channel_time = np.atleast_1d(self.IrIS_Eval[channel_key]['time'])
        
        if i > 0:  # From the second channel onwards, add a bridging point
            last_data = aggregated_data[-1]
            bridging_time = channel_time[0] - 0.001
            aggregated_data = np.append(aggregated_data, last_data)
            aggregated_time = np.append(aggregated_time, bridging_time)
        
        aggregated_data = np.concatenate((aggregated_data, channel_data))
        aggregated_time = np.concatenate((aggregated_time, channel_time))
    
    return aggregated_data, aggregated_time

def aggregate_peaks_data(self):
    # Initialize empty arrays for the data and time
    aggregated_peaks= np.array([],dtype=int)
    # Sort keys if a sort_key function is provided, else use keys as they are
    offset = 0
    keys_list  = list(self.IrIS_Eval.keys())
    for i, channel_key in enumerate(keys_list):
        channel_time = np.atleast_1d(self.IrIS_Eval[channel_key]['time'])
        peaks = self.IrIS_Eval[channel_key]['peaks'].copy()
        peaks += offset    
        aggregated_peaks = np.concatenate((aggregated_peaks, peaks)) 
        offset = offset + len(channel_time)+1
    return aggregated_peaks
    
def plot_IrIS_eval(self):
    channel             = self.Pk_find_channel.value()
    try:
        # Attempt to access 'time' for the specified channel
        time = self.IrIS_Eval[channel]['time']
    except KeyError:
        # If 'time' is not found or 'channel' does not exist in 'IrIS_Eval', display an error message
        QMessageBox.critical(self, "Data Missing", "Process the data for this channel first")
        return  # Optionally return from the function if the error condition is met
    #
    vector_positions    = np.arange(len(time))
    #
    if self.IrIS_plot_sel_box1.currentText() == "None": 
        # Check if the container has a layout, set one if not
        if self.IrIS_Ax_Eval_02.layout() is None:
            layout = QVBoxLayout(self.IrIS_Ax_Eval_02)
            self.IrIS_Ax_Eval_02.setLayout(layout)
        else:
            # Clear existing content in the container, if any
            while self.IrIS_Ax_Eval_02.layout().count():
                child = self.IrIS_Ax_Eval_02.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
    #
    elif   self.IrIS_plot_sel_box1.currentText() == "fps":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_fps, aggregated_time = aggregate_channel_data(self, 'fps')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, aggregated_fps, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, self.IrIS_Eval[channel]['fps'], self.IrIS_Eval[channel]['time'], plot_type='line') 
  
    elif   self.IrIS_plot_sel_box1.currentText() == "Time":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_time, aggregated_time = aggregate_channel_data(self, 'time')
            vector_positions    = np.arange(len(aggregated_time))
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, aggregated_time, vector_positions, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, time, vector_positions, plot_type='line')
    elif   self.IrIS_plot_sel_box1.currentText() == "Peaks":
        if self.Pk_find_processl_all_check.isChecked():
            try:
                aggregated_differences_1_perc, aggregated_time = aggregate_channel_data(self, 'differences_1_perc')
                peaks=aggregate_peaks_data(self)
                create_and_embed_plot(self, self.IrIS_Ax_Eval_02, aggregated_differences_1_perc,aggregated_time,'Peaks', peaks)
            except KeyError:
                QMessageBox.critical(self, "Data Missing", "Peaks not found or not available for all channels... check find peaks options")
                return  # Optionally return from the function if the error condition is met
        else:
            try:
                create_and_embed_plot(self, self.IrIS_Ax_Eval_02, self.IrIS_Eval[channel]['differences_1_perc'],np.array(time),'Peaks', self.IrIS_Eval[channel]['peaks'])
            except KeyError:
                QMessageBox.critical(self, "Data Missing", "Peaks not found  ... check find peaks options")
                return  # Optionally return from the function if the error condition is met
                
    elif   self.IrIS_plot_sel_box1.currentText() == "Mean":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_averages, aggregated_time = aggregate_channel_data(self, 'averages')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, aggregated_averages, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, self.IrIS_Eval[channel]['averages'], time, plot_type='line') 
    elif self.IrIS_plot_sel_box1.currentText() == "Max. (90th)":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_max_90th, aggregated_time = aggregate_channel_data(self, 'percentiles_90')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, aggregated_max_90th, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, self.IrIS_Eval[channel]['percentiles_90'], time, plot_type='line')
    elif   self.IrIS_plot_sel_box1.currentText() == "Mean - Grad.":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_averages_grad, aggregated_time = aggregate_channel_data(self, 'averages_grad')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, aggregated_averages_grad, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02,self.IrIS_Eval[channel]['averages_grad'], time, plot_type='line') 
    elif self.IrIS_plot_sel_box1.currentText() == "Max. (90th) - Grad.":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_percentiles_90_grad, aggregated_time = aggregate_channel_data(self, 'percentiles_90_grad')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, aggregated_percentiles_90_grad, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, self.IrIS_Eval[channel]['percentiles_90_grad'], time, plot_type='line')
    elif self.IrIS_plot_sel_box1.currentText() == "Diff. 1 Frame": 
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_differences_1, aggregated_time = aggregate_channel_data(self, 'differences_1')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, aggregated_differences_1, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, self.IrIS_Eval[channel]['differences_1'], time, plot_type='line')
    elif self.IrIS_plot_sel_box1.currentText() == "Diff. N Frames": 
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_differences_N, aggregated_time = aggregate_channel_data(self, 'differences_N')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, aggregated_differences_N, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, self.IrIS_Eval[channel]['differences_N'], time, plot_type='line')
    elif self.IrIS_plot_sel_box1.currentText() == "Diff. 1 Frame %":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_differences_1_perc, aggregated_time = aggregate_channel_data(self, 'differences_1_perc')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, aggregated_differences_1_perc, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, self.IrIS_Eval[channel]['differences_1_perc'], time, plot_type='line')
    elif self.IrIS_plot_sel_box1.currentText() == "Diff. N Frames %":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_differences_N_perc, aggregated_time = aggregate_channel_data(self, 'differences_N_perc')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, aggregated_differences_N_perc, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, self.IrIS_Eval[channel]['differences_N_per'], time, plot_type='line')
    elif self.IrIS_plot_sel_box1.currentText() == "Max. Diff. 1 Frame": 
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_m_differences_1, aggregated_time = aggregate_channel_data(self, 'm_differences_1')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, aggregated_m_differences_1, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, self.IrIS_Eval[channel]['m_differences_1'], time, plot_type='line')
    elif self.IrIS_plot_sel_box1.currentText() == "Max. Diff. N Frames": 
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_m_differences_N, aggregated_time = aggregate_channel_data(self, 'm_differences_N')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, aggregated_m_differences_N, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, self.IrIS_Eval[channel]['m_differences_N'], time, plot_type='line')
          
    #
    if self.IrIS_plot_sel_box2.currentText() == "None": 
        # Check if the container has a layout, set one if not
        if self.IrIS_Ax_Eval_03.layout() is None:
            layout = QVBoxLayout(self.IrIS_Ax_Eval_03)
            self.IrIS_Ax_Eval_03.setLayout(layout)
        else:
            # Clear existing content in the container, if any
            while self.IrIS_Ax_Eval_03.layout().count():
                child = self.IrIS_Ax_Eval_03.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
    #  
    elif   self.IrIS_plot_sel_box2.currentText() == "fps":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_fps, aggregated_time = aggregate_channel_data(self, 'fps')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, aggregated_fps, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, self.IrIS_Eval[channel]['fps'], self.IrIS_Eval[channel]['time'], plot_type='line') 
    
    elif   self.IrIS_plot_sel_box2.currentText() == "Time":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_time, aggregated_time = aggregate_channel_data(self, 'time')
            vector_positions    = np.arange(len(aggregated_time))
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, aggregated_time, vector_positions, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, time, vector_positions, plot_type='line')
    elif   self.IrIS_plot_sel_box2.currentText() == "Peaks":
        if self.Pk_find_processl_all_check.isChecked():
            try:
                aggregated_differences_1_perc, aggregated_time = aggregate_channel_data(self, 'differences_1_perc')
                peaks=aggregate_peaks_data(self)
                create_and_embed_plot(self, self.IrIS_Ax_Eval_03, aggregated_differences_1_perc,aggregated_time,'Peaks', peaks)
            except KeyError:
                QMessageBox.critical(self, "Data Missing", "Peaks not found or not available for all channels... check find peaks options")
                return  # Optionally return from the function if the error condition is met
        else:
            try:
                create_and_embed_plot(self, self.IrIS_Ax_Eval_03, self.IrIS_Eval[channel]['differences_1_perc'],np.array(time),'Peaks', self.IrIS_Eval[channel]['peaks'])
            except KeyError:
                QMessageBox.critical(self, "Data Missing", "Peaks not found  ... check find peaks options")
                return  # Optionally return from the function if the error condition is met
    elif   self.IrIS_plot_sel_box2.currentText() == "Mean":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_averages, aggregated_time = aggregate_channel_data(self, 'averages')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, aggregated_averages, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, self.IrIS_Eval[channel]['averages'], time, plot_type='line') 
    elif self.IrIS_plot_sel_box2.currentText() == "Max. (90th)":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_max_90th, aggregated_time = aggregate_channel_data(self, 'percentiles_90')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, aggregated_max_90th, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, self.IrIS_Eval[channel]['percentiles_90'], time, plot_type='line')
    elif   self.IrIS_plot_sel_box2.currentText() == "Mean - Grad.":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_averages_grad, aggregated_time = aggregate_channel_data(self, 'averages_grad')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, aggregated_averages_grad, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03,self.IrIS_Eval[channel]['averages_grad'], time, plot_type='line') 
    elif self.IrIS_plot_sel_box2.currentText() == "Max. (90th) - Grad.":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_percentiles_90_grad, aggregated_time = aggregate_channel_data(self, 'percentiles_90_grad')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, aggregated_percentiles_90_grad, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, self.IrIS_Eval[channel]['percentiles_90_grad'], time, plot_type='line')
    elif self.IrIS_plot_sel_box2.currentText() == "Diff. 1 Frame": 
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_differences_1, aggregated_time = aggregate_channel_data(self, 'differences_1')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, aggregated_differences_1, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, self.IrIS_Eval[channel]['differences_1'], time, plot_type='line')
    elif self.IrIS_plot_sel_box2.currentText() == "Diff. N Frames": 
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_differences_N, aggregated_time = aggregate_channel_data(self, 'differences_N')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, aggregated_differences_N, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, self.IrIS_Eval[channel]['differences_N'], time, plot_type='line')
    elif self.IrIS_plot_sel_box2.currentText() == "Diff. 1 Frame %":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_differences_1_perc, aggregated_time = aggregate_channel_data(self, 'differences_1_perc')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, aggregated_differences_1_perc, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, self.IrIS_Eval[channel]['differences_1_perc'], time, plot_type='line')
    elif self.IrIS_plot_sel_box2.currentText() == "Diff. N Frames %":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_differences_N_perc, aggregated_time = aggregate_channel_data(self, 'differences_N_perc')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, aggregated_differences_N_perc, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, self.IrIS_Eval[channel]['differences_N_per'], time, plot_type='line')
    elif self.IrIS_plot_sel_box2.currentText() == "Max. Diff. 1 Frame": 
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_m_differences_1, aggregated_time = aggregate_channel_data(self, 'm_differences_1')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, aggregated_m_differences_1, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, self.IrIS_Eval[channel]['m_differences_1'], time, plot_type='line')
    elif self.IrIS_plot_sel_box2.currentText() == "Max. Diff. N Frames": 
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_m_differences_N, aggregated_time = aggregate_channel_data(self, 'm_differences_N')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, aggregated_m_differences_N, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_03, self.IrIS_Eval[channel]['m_differences_N'], time, plot_type='line') 

#    
    if self.IrIS_plot_sel_box3.currentText() == "None": 
        # Check if the container has a layout, set one if not
        if self.IrIS_Ax_Eval_04.layout() is None:
            layout = QVBoxLayout(self.IrIS_Ax_Eval_04)
            self.IrIS_Ax_Eval_04.setLayout(layout)
        else:
            # Clear existing content in the container, if any
            while self.IrIS_Ax_Eval_04.layout().count():
                child = self.IrIS_Ax_Eval_04.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
    #  
    elif   self.IrIS_plot_sel_box3.currentText() == "fps":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_fps, aggregated_time = aggregate_channel_data(self, 'fps')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, aggregated_fps, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, self.IrIS_Eval[channel]['fps'], self.IrIS_Eval[channel]['time'], plot_type='line') 
    
    elif   self.IrIS_plot_sel_box3.currentText() == "Time":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_time, aggregated_time = aggregate_channel_data(self, 'time')
            vector_positions    = np.arange(len(aggregated_time))
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, aggregated_time, vector_positions, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, time, vector_positions, plot_type='line')
    elif   self.IrIS_plot_sel_box3.currentText() == "Peaks":
        if self.Pk_find_processl_all_check.isChecked():
            try:
                aggregated_differences_1_perc, aggregated_time = aggregate_channel_data(self, 'differences_1_perc')
                peaks=aggregate_peaks_data(self)
                create_and_embed_plot(self, self.IrIS_Ax_Eval_04, aggregated_differences_1_perc,aggregated_time,'Peaks', peaks)
            except KeyError:
                QMessageBox.critical(self, "Data Missing", "Peaks not found or not available for all channels... check find peaks options")
                return  # Optionally return from the function if the error condition is met
        else:
            try:
                create_and_embed_plot(self, self.IrIS_Ax_Eval_04, self.IrIS_Eval[channel]['differences_1_perc'],np.array(time),'Peaks', self.IrIS_Eval[channel]['peaks'])
            except KeyError:
                QMessageBox.critical(self, "Data Missing", "Peaks not found  ... check find peaks options")
                return  # Optionally return from the function if the error condition is met
    elif   self.IrIS_plot_sel_box3.currentText() == "Mean":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_averages, aggregated_time = aggregate_channel_data(self, 'averages')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, aggregated_averages, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, self.IrIS_Eval[channel]['averages'], time, plot_type='line') 
    elif self.IrIS_plot_sel_box3.currentText() == "Max. (90th)":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_max_90th, aggregated_time = aggregate_channel_data(self, 'percentiles_90')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, aggregated_max_90th, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, self.IrIS_Eval[channel]['percentiles_90'], time, plot_type='line')
    elif   self.IrIS_plot_sel_box3.currentText() == "Mean - Grad.":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_averages_grad, aggregated_time = aggregate_channel_data(self, 'averages_grad')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, aggregated_averages_grad, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04,self.IrIS_Eval[channel]['averages_grad'], time, plot_type='line') 
    elif self.IrIS_plot_sel_box3.currentText() == "Max. (90th) - Grad.":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_percentiles_90_grad, aggregated_time = aggregate_channel_data(self, 'percentiles_90_grad')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, aggregated_percentiles_90_grad, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, self.IrIS_Eval[channel]['percentiles_90_grad'], time, plot_type='line')
    elif self.IrIS_plot_sel_box3.currentText() == "Diff. 1 Frame": 
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_differences_1, aggregated_time = aggregate_channel_data(self, 'differences_1')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, aggregated_differences_1, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, self.IrIS_Eval[channel]['differences_1'], time, plot_type='line')
    elif self.IrIS_plot_sel_box3.currentText() == "Diff. N Frames": 
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_differences_N, aggregated_time = aggregate_channel_data(self, 'differences_N')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, aggregated_differences_N, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, self.IrIS_Eval[channel]['differences_N'], time, plot_type='line')
    elif self.IrIS_plot_sel_box3.currentText() == "Diff. 1 Frame %":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_differences_1_perc, aggregated_time = aggregate_channel_data(self, 'differences_1_perc')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, aggregated_differences_1_perc, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, self.IrIS_Eval[channel]['differences_1_perc'], time, plot_type='line')
    elif self.IrIS_plot_sel_box3.currentText() == "Diff. N Frames %":
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_differences_N_perc, aggregated_time = aggregate_channel_data(self, 'differences_N_perc')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, aggregated_differences_N_perc, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, self.IrIS_Eval[channel]['differences_N_per'], time, plot_type='line')
    elif self.IrIS_plot_sel_box3.currentText() == "Max. Diff. 1 Frame": 
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_m_differences_1, aggregated_time = aggregate_channel_data(self, 'm_differences_1')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, aggregated_m_differences_1, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_02, self.IrIS_Eval[channel]['m_differences_1'], time, plot_type='line')
    elif self.IrIS_plot_sel_box3.currentText() == "Max. Diff. N Frames": 
        if self.Pk_find_processl_all_check.isChecked():
            aggregated_m_differences_N, aggregated_time = aggregate_channel_data(self, 'm_differences_N')
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, aggregated_m_differences_N, aggregated_time, plot_type='line')     
        else:
            create_and_embed_plot(self, self.IrIS_Ax_Eval_04, self.IrIS_Eval[channel]['m_differences_N'], time, plot_type='line')
        
        
        
                
def create_and_embed_plot(self, container, data, time=None, plot_type='line', peaks=None):
    # Create the figure and axis for the plot
    fig, ax = plt.subplots()
    fig.patch.set_facecolor('none')
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    
    # Plot based on the specified plot_type
    if   plot_type == 'histogram':
        ax.hist(data, bins=500)  # Adjust parameters as needed
    elif plot_type == 'line':
        if time is not None:
            ax.plot(time, data)  # Plot data against time
        else:
            ax.plot(data)  # Simple line plot
    elif plot_type == 'Peaks':
        ax.plot(time,data)
        ax.plot(time[peaks], data[peaks], "x", color='red')
        # print(self.Dw_pos_info)
        for i in range(self.Dw_pos_info.shape[0]):
            if self.Dw_pos_info[i,6] >= time[peaks[0]] and self.Dw_pos_info[i,7] <= time[peaks[-1]+1]:
                ax.plot([self.Dw_pos_info[i,6], self.Dw_pos_info[i,6]], [data.min(),data.max()], ":", color='red')
                ax.plot([self.Dw_pos_info[i,7], self.Dw_pos_info[i,7]], [data.min(),data.max()], ":", color='green')
    
    # Customize the plot (optional)
    ax.tick_params(axis='both', which='major', labelsize=14, colors='white')
       
    canvas = FigureCanvas(fig)
    canvas.setStyleSheet("background-color:transparent;")
    toolbar = NavigationToolbar(canvas, self)  # Adjust as necessary
    
    # Check if the container has a layout, set one if not
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

