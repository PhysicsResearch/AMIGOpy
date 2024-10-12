import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QColor
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTableWidget, QVBoxLayout, QPushButton, QSpinBox, QLabel, QMessageBox
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
from matplotlib.figure import Figure
import matplotlib.colors as mcolors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar




def update_plan_tables(self):
    if 'Plan_Brachy_Channels' in self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']:
        N_channels = len(self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['Plan_Brachy_Channels'])
        #
        self.brachy_N_channels.setText(f"{N_channels:.0f}")
        #
        # set spinbo min value
        self.brachy_spinBox_01.setMinimum(1)
        self.brachy_spinBox_02.setMinimum(1)
        # Set the maximum value
        self.brachy_spinBox_01.setMaximum(N_channels)
        self.brachy_spinBox_02.setMaximum(N_channels)
        # Set the current value
        self.brachy_spinBox_01.setValue(1)
        self.brachy_spinBox_02.setValue(1)
        #
        update_disp_brachy_plan(self)
    else:
        print("'Plan_Brachy_Channels' does NOT exist.")

def update_disp_brachy_plan(self):
    channels   = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['Plan_Brachy_Channels']
    current_ch = channels[self.brachy_spinBox_01.value()-1]
    #
    #
    clear_brachy_table(self)
    setup_brachy_table_headers(self)
    selected_dw_ch = self.brachy_combobox_02.currentText()
    if selected_dw_ch == "Dwells": 
        populate_brachy_table(self, current_ch.get('DwellInfo'))
    else:
        populate_brachy_table(self, current_ch.get('ChPos'))
    #
    apply_alternating_row_colors(self)
    #
    plot_brachy_dwell_channels(self)
    calculate_total_time(self)
    

def calculate_total_time(self):
    """
    Calculates the total time across all channels by summing the "Time (s)" column
    of each channel's DwellInfo matrix. Additionally, calculates the total time for the
    specific channel indicated by the spinbox (self.brachy_spinBox_02).
    
    :return: None
    """
    channels = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['Plan_Brachy_Channels']
    
    total_time = 0.0  # Initialize total time across all channels
    selected_channel_time = 0.0  # Initialize total time for the selected channel
    
    selected_channel_idx = self.brachy_spinBox_02.value() - 1  # Adjust for zero-based indexing
    
    for idx, channel in enumerate(channels):
        dwell_info = channel.get('DwellInfo')
        
        if dwell_info is None:
            print(f"Channel {idx + 1}: 'DwellInfo' is None. Skipping.")
            continue
        
        if not isinstance(dwell_info, np.ndarray):
            print(f"Channel {idx + 1}: 'DwellInfo' is not a NumPy array. Skipping.")
            continue
        
        if dwell_info.ndim != 2 or dwell_info.shape[1] < 3:
            print(f"Channel {idx + 1}: 'DwellInfo' does not have at least 3 columns. Skipping.")
            continue
        
        # Extract the "Time (s)" column (index 2)
        time_column = dwell_info[:, 2]
        
        # Handle NaN values by treating them as 0
        time_column = np.nan_to_num(time_column, nan=0.0)
        
        # Sum the "Time (s)" values for this channel
        channel_total = np.sum(time_column)
        total_time += channel_total
        
        # If this is the selected channel, save its total time
        if idx == selected_channel_idx:
            selected_channel_time = channel_total
    
    # Display the total time across all channels
    self.brachy_total_time.setText(f"{total_time:.4f} s")
    
    # Display the total time for the selected channel
    self.brachy_ch_time.setText(f"{selected_channel_time:.4f} s")
    

    
def clear_brachy_table(self):
    """
    Clears all existing rows and columns from the brachy_table_01.
    """
    self.brachy_table_01.clear()   # Clears the table content but retains headers
    self.brachy_table_01.setRowCount(0)    # Removes all rows
    self.brachy_table_01.setColumnCount(0) # Removes all columns
    #
    self.brachy_table_02.clear()   # Clears the table content but retains headers
    self.brachy_table_02.setRowCount(0)    # Removes all rows
    self.brachy_table_02.setColumnCount(0) # Removes all columns
    
def setup_brachy_table_headers(self):
    """
    Sets up the column headers for brachy_table_01.
    """
    selected_dw_ch = self.brachy_combobox_02.currentText()
    if selected_dw_ch == "Dwells": 
        headers = ["IDX", "Rel. Pos (mm)", "Time (s)", "X (mm)", "Y (mm)", "Z(mm)", "Ux", "Uy", "Uz"]
    else:
        headers = ["X (mm)", "Y (mm)", "Z(mm)"]
    
    self.brachy_table_01.setColumnCount(len(headers))
    self.brachy_table_01.setHorizontalHeaderLabels(headers)
    
    # Optional: Adjust column widths to fit content
    self.brachy_table_01.resizeColumnsToContents()
    #
    self.brachy_table_02.setColumnCount(len(headers))
    self.brachy_table_02.setHorizontalHeaderLabels(headers)
    
    # Optional: Adjust column widths to fit content
    self.brachy_table_02.resizeColumnsToContents()


    
def populate_brachy_table(self, dwell_info):
    """
    Populates brachy_table_01 with data from dwell_info.

    :param dwell_info: NumPy array with shape (n, 9)
    """
    
    
    num_rows = dwell_info.shape[0]
    num_columns = dwell_info.shape[1]
    
    # Set the number of rows and columns
    self.brachy_table_01.setRowCount(num_rows)
    self.brachy_table_01.setColumnCount(num_columns)
    #
    self.brachy_table_02.setRowCount(num_rows)
    self.brachy_table_02.setColumnCount(num_columns)
    
    # Populate the table
    for row in range(num_rows):
        for col in range(num_columns):
            # Assuming all data is numerical; adjust if data types vary
            item = QTableWidgetItem(str(dwell_info[row, col]))
            item.setTextAlignment(Qt.AlignCenter)  # Optional: Center-align the text
            self.brachy_table_01.setItem(row, col, item)
            #
            item2 = QTableWidgetItem(str(dwell_info[row, col]))
            item2.setTextAlignment(Qt.AlignCenter)  # Optional: Center-align the text
            self.brachy_table_02.setItem(row, col, item2)

    # Optional: Resize columns to fit content
    self.brachy_table_01.resizeColumnsToContents()
    self.brachy_table_02.resizeColumnsToContents()

def apply_alternating_row_colors(self):
    """
    Applies alternating blue and light blue colors to the table rows.
    """
    blue_color = QColor(0, 70, 184)           
    light_blue_color = QColor(0, 104, 184) 
    
    num_rows = self.brachy_table_01.rowCount()
    num_rows = self.brachy_table_02.rowCount()
    
    for row in range(num_rows):
        # Choose color based on even or odd row
        if row % 2 == 0:
            color = blue_color
        else:
            color = light_blue_color
        
        for col in range(self.brachy_table_01.columnCount()):
            item  = self.brachy_table_01.item(row, col)
            item2 = self.brachy_table_02.item(row, col)
            if item:
                item.setBackground(color)
                item2.setBackground(color)








def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be a matplotlib color string, hex string, or RGB tuple.
    """
    try:
        c = mcolors.cnames[color]
    except:
        c = color
    c = mcolors.to_rgb(c)
    return mcolors.to_hex([min(1, c[i] + amount * (1 - c[i])) for i in range(3)])

def darken_color(color, amount=0.3):
    """
    Darkens the given color by multiplying its RGB values by the given amount.
    Input can be a matplotlib color string, hex string, or RGB tuple.
    """
    try:
        c = mcolors.cnames[color]
    except:
        c = color
    c = mcolors.to_rgb(c)
    return mcolors.to_hex([max(0, c[i] * (1 - amount)) for i in range(3)])

def plot_brachy_dwell_channels(self):
    plot_brachy_3D_dwell_channels(self)
    plot_brachy_bar_channels(self)
    
def plot_brachy_3D_dwell_channels(self):
    # Retrieve user-selected settings
    font_size = self.selected_font_size
    background_color = self.selected_background
    
    # Get the point color, line color, and special first point color from the combo boxes
    point_color = self.brachy_dw_sel_col.currentText()
    line_color = self.brachy_lin_sel_col.currentText()
    first_point_color = self.brachy_p1_sel_col.currentText()

    # Adjust the colors (lighten and darken)
    lighter_green = lighten_color("green", 0.4)  # Example: make green lighter
    point_color = lighter_green if point_color == "Green" else point_color

    # Get the point size, line width, and first point size from the spin boxes
    point_size = self.brachy_dw_size.value()  # Assuming it's an int spinbox
    line_width = self.brachy_ch_line_width.value()  # Assuming it's a double spinbox
    first_point_size = self.brachy_ch_size.value()  # Assuming it's a double spinbox
    
    # Determine text and label colors based on the background color
    if background_color.lower() == 'transparent':
        text_color = 'white'
        bg = 'transparent'
    elif background_color.lower() == 'white':
        text_color = 'black'
        bg = 'white'
    else:
        text_color = 'black'
        bg = background_color
    
    # Initialize the Matplotlib Figure if it doesn't exist
    if not hasattr(self, 'plot_Brachy_3D_ch_dw_fig'):
        self.plot_Brachy_3D_ch_dw_fig = Figure()
        self.plot_canvas = FigureCanvas(self.plot_Brachy_3D_ch_dw_fig)
        self.plot_toolbar = NavigationToolbar(self.plot_canvas, self)
        container = self.brachy_ax_02
        
        if container.layout() is None:
            layout = QVBoxLayout(container)
            container.setLayout(layout)
        else:
            while container.layout().count():
                child = container.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        container.layout().addWidget(self.plot_toolbar)
        container.layout().addWidget(self.plot_canvas)
    else:
        self.plot_Brachy_3D_ch_dw_fig.clf()
    
    ax = self.plot_Brachy_3D_ch_dw_fig.add_subplot(111, projection='3d')
    
    if bg.lower() == 'transparent':
        ax.set_facecolor((0, 0, 0, 0))
        self.plot_Brachy_3D_ch_dw_fig.patch.set_alpha(0.0)
    else:
        ax.set_facecolor(bg)
        self.plot_Brachy_3D_ch_dw_fig.patch.set_facecolor(bg)
    
    ax.tick_params(colors=text_color, labelsize=font_size)
    ax.set_xlabel("X (mm)", fontsize=font_size, color=text_color)
    ax.set_ylabel("Y (mm)", fontsize=font_size, color=text_color)
    ax.set_zlabel("Z (mm)", fontsize=font_size, color=text_color)
    
    # Retrieve channels from dicom_data
    channels = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['Plan_Brachy_Channels']
    
    # Determine whether to plot all channels or just the selected one
    if self.checkBox_dw_ch_plot.isChecked():
        # Show all channels
        channel_indices = range(len(channels))
    else:
        # Show only the selected channel from the spinbox
        selected_channel = self.brachy_spinBox_02.value() - 1  # Adjust for zero-based indexing
        if 0 <= selected_channel < len(channels):
            channel_indices = [selected_channel]
        else:
            print(f"Selected channel {selected_channel + 1} is out of range.")
            return

    # Iterate through the selected channels to plot their points
    for idx in channel_indices:
        channel = channels[idx]
        dwell_info = channel.get('DwellInfo')
        chpos_info = channel.get('ChPos')
        
        if dwell_info is None or not isinstance(dwell_info, np.ndarray) or dwell_info.ndim != 2 or dwell_info.shape[1] < 7:
            continue

        # Filter dwell points based on dwell time > 0 if self.checkBox_show_dw_plot is selected
        if self.checkBox_show_dw_plot.isChecked():
            valid_dwell_indices = dwell_info[:, 2] > 0  # Assuming column 2 is the "Time (s)" column
            dwell_info = dwell_info[valid_dwell_indices]  # Filter rows where time > 0

        # Ensure there's valid data after filtering
        if dwell_info.shape[0] == 0:
            continue

        # Extract the X, Y, Z coordinates (columns 3, 4, 5)
        x, y, z = dwell_info[:, 3], dwell_info[:, 4], dwell_info[:, 5]
        x, y, z = np.nan_to_num(x, nan=0.0), np.nan_to_num(y, nan=0.0), np.nan_to_num(z, nan=0.0)
        
        # Plot all valid points
        ax.scatter(x, y, z, c=point_color, marker='o', s=point_size, alpha=0.6, edgecolors=darken_color(point_color, 0.2))
        
        # Plot the line representing the channel's position if checkbox is selected
        if self.checkBox_show_ch_plot.isChecked() and chpos_info is not None and isinstance(chpos_info, np.ndarray) and chpos_info.ndim == 2 and chpos_info.shape[1] >= 3:
            ch_x, ch_y, ch_z = chpos_info[:, 0], chpos_info[:, 1], chpos_info[:, 2]
            ch_x, ch_y, ch_z = np.nan_to_num(ch_x, nan=0.0), np.nan_to_num(ch_y, nan=0.0), np.nan_to_num(ch_z, nan=0.0)
            
            ax.plot(ch_x, ch_y, ch_z, color=line_color, linewidth=line_width, label=f'Channel {idx + 1} Position')

    # After all points are plotted, plot the first point of each channel with the special color
    for idx in channel_indices:
        channel = channels[idx]
        dwell_info = channel.get('DwellInfo')
        
        if dwell_info is None or not isinstance(dwell_info, np.ndarray) or dwell_info.ndim != 2 or dwell_info.shape[1] < 7:
            continue

        # Filter first point if it has dwell time > 0, when self.checkBox_show_dw_plot is selected
        if self.checkBox_show_dw_plot.isChecked() and dwell_info[0, 2] <= 0:  # Assuming dwell time in column 2
            continue

        x, y, z = dwell_info[0, 3], dwell_info[0, 4], dwell_info[0, 5]
        ax.scatter(x, y, z, c=first_point_color, marker='o', s=first_point_size, alpha=1.0, edgecolors=darken_color(first_point_color, 0.2))
    
    ax.xaxis.pane.set_alpha(0.0)
    ax.yaxis.pane.set_alpha(0.0)
    ax.zaxis.pane.set_alpha(0.0)
    
    self.plot_canvas.setStyleSheet(f"background-color:{bg};")
    self.plot_canvas.draw()





def plot_brachy_bar_channels(self):
    # Retrieve user-selected settings
    font_size = self.selected_font_size
    background_color = self.selected_background
    
    # Get the selected channel from the spinbox
    selected_channel = self.brachy_spinBox_02.value()  # Integer spinbox value for selected channel
    
    # Get the container for the bar plot
    container = self.brachy_ax_01
    
    # Set the background color for the container itself
    if background_color.lower() == 'transparent':
        container.setStyleSheet("background-color: rgba(0, 0, 0, 0);")  # Transparent background for the entire container
    else:
        container.setStyleSheet(f"background-color: {background_color};")  # Set the background color for the entire container
    
    # Initialize the Matplotlib Figure if it doesn't exist
    if not hasattr(self, 'plot_Brachy_Bar_Fig'):
        self.plot_Brachy_Bar_Fig = Figure()
        self.plot_bar_canvas = FigureCanvas(self.plot_Brachy_Bar_Fig)
        self.plot_bar_toolbar = NavigationToolbar(self.plot_bar_canvas, self)
        
        # Set layout for the container if it doesn't have one
        if container.layout() is None:
            layout = QVBoxLayout(container)
            container.setLayout(layout)
        else:
            # Clear existing content in the container, if any
            while container.layout().count():
                child = container.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        # Add the toolbar and canvas to the container
        container.layout().addWidget(self.plot_bar_toolbar)
        container.layout().addWidget(self.plot_bar_canvas)
    else:
        # If the figure already exists, clear it for new plotting
        self.plot_Brachy_Bar_Fig.clf()

    # Create an axes for the bar plot
    ax = self.plot_Brachy_Bar_Fig.add_subplot(111)
    
    # Set plot and figure background based on user selection
    if background_color.lower() == 'transparent':
        ax.set_facecolor((0, 0, 0, 0))  # Transparent background for the plot itself
        self.plot_Brachy_Bar_Fig.patch.set_alpha(0.0)
    else:
        ax.set_facecolor(background_color)
        self.plot_Brachy_Bar_Fig.patch.set_facecolor(background_color)
    
    # Customize text and axes properties
    ax.tick_params(labelsize=font_size, colors='black' if background_color.lower() == 'white' else 'white')  # Adjust label color based on background
    ax.set_xlabel("Dwell Position", fontsize=font_size, color='black' if background_color.lower() == 'white' else 'white')
    ax.set_ylabel("Dwell Time (s)", fontsize=font_size, color='black' if background_color.lower() == 'white' else 'white')

    # Retrieve the channels from dicom_data
    channels = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['Plan_Brachy_Channels']
    
    # Check if the selected channel is valid
    channel_idx = selected_channel - 1  # Adjust to zero-based indexing
    if 0 <= channel_idx < len(channels):
        channel = channels[channel_idx]
        dwell_info = channel.get('DwellInfo')
        
        if dwell_info is None or not isinstance(dwell_info, np.ndarray):
            print(f"Channel {selected_channel}: 'DwellInfo' is not valid. Skipping.")
            return
        
        # Extract dwell times (assuming column 2 holds the dwell time)
        dwell_times = dwell_info[:, 2]  # Example: assuming the dwell times are in the 3rd column

        # Create labels for each dwell position
        bar_labels = [f"{i + 1}" for i in range(len(dwell_times))]
        bar_values = dwell_times
        
        # Plot the bar chart
        ax.bar(bar_labels, bar_values, color='blue')
        
        # Optionally, add value labels on top of the bars
        for i, v in enumerate(bar_values):
            ax.text(i, v + (v * 0.02), f'{v:.2f}', ha='center', fontsize=font_size, color='black' if background_color.lower() == 'white' else 'white')

    else:
        print(f"Selected channel {selected_channel} is out of range.")
        return

    # Draw the updated plot
    self.plot_bar_canvas.draw()