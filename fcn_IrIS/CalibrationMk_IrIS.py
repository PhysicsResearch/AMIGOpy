# calibration module functions
import sys
import csv
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
from PyQt5.QtGui import QColor, QBrush
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from scipy.optimize import minimize

def set_ref_shift(self):
    # during calibration the spource is placed on top of a reference marker (XY)
    # this function adjust the shift to match the proejcetion of the reference marker (XY) with source and physical marker positions
    Reference_ID =  self.IrIS_cal_Ref_MK_ID.value()-1
    ref_mk_x  = float(self.IrIS_cal_ref_table.item(Reference_ID, 3).text())  
    ref_mk_y  = float(self.IrIS_cal_ref_table.item(Reference_ID, 4).text())  
    x         = float(self.IrIS_cal_ref_table.item(Reference_ID, 0).text())
    y         = float(self.IrIS_cal_ref_table.item(Reference_ID, 1).text())
    #
    #
    # source position should also match the marker (XY)
    self.IrIS_cal_Sour_01.setValue(ref_mk_x)
    self.IrIS_cal_Sour_02.setValue(ref_mk_y)
          

def find_intersections(x_r, y_r, z_r, x_data, y_data, z_data):
    """
    Finds the intersection points between a reference plane at height z_r
    and lines defined by points (x_r, y_r, z_r) and (x_data, y_data, z_data).

    Parameters:
        x_r (float): x-coordinate of the reference point.
        y_r (float): y-coordinate of the reference point.
        z_r (float): z-coordinate (height) of the reference plane.
        x_data (list or np.ndarray): x-coordinates of points.
        y_data (list or np.ndarray): y-coordinates of points.
        z_data (list or np.ndarray): z-coordinates of points.

    Returns:
        np.ndarray: Array of x-coordinates of intersections.
        np.ndarray: Array of y-coordinates of intersections.
    """
    x_int = []
    y_int = []
    
    for x_i, y_i, z_i in zip(x_data, y_data, z_data):
        if z_i != z_r:  # Ensure we're not dividing by zero
            t = -z_r / (z_i - z_r)
            x_prime = x_r + t * (x_i - x_r)
            y_prime = y_r + t * (y_i - y_r)
            
            x_int.append(x_prime)
            y_int.append(y_prime)
        else:
            # Handle the case where z_i == z_r if necessary
            pass
    
    return np.array(x_int), np.array(y_int)

def rot_phy_mk_around_X(theta, y_data_np, z_data_np, P_ref):
    # Apply rotation around X
    # Step 1: Translate points to make the reference point the origin
    y_translated = y_data_np - P_ref[1]
    z_translated = z_data_np - P_ref[2]
    # Step 2: Apply the rotation around the new origin
    y_rotated = y_translated * np.cos(theta) + z_translated * np.sin(theta)
    z_rotated = -y_translated * np.sin(theta) + z_translated * np.cos(theta)
    # Step 3: Translate points back
    y_rotated_back = y_rotated + P_ref[1]
    z_rotated_back = z_rotated + P_ref[2]
    #
    return y_rotated_back, z_rotated_back

def rot_phy_mk_around_Y(theta, x_data_np, z_data_np, P_ref):
    # Apply rotation around Y
    # Step 1: Translate points to make the reference point the origin
    x_translated = x_data_np - P_ref[0]
    z_translated = z_data_np - P_ref[2]
    # Step 2: Apply the rotation around the new origin
    x_rotated = x_translated * np.cos(theta) + z_translated * np.sin(theta)
    z_rotated = -x_translated * np.sin(theta) + z_translated * np.cos(theta)
    # Step 3: Translate points back
    x_rotated_back = x_rotated + P_ref[0]
    z_rotated_back = z_rotated + P_ref[2]
    #
    return x_rotated_back, z_rotated_back

def rot_phy_mk_around_Z(theta,x_data_np,y_data_np,P_ref):
    # Apply rotation around Z
    # Step 1: Translate points to make the reference point the origin
    x_translated = x_data_np - P_ref[0]
    y_translated = y_data_np - P_ref[1]
    # Step 2: Apply the rotation around the new origin
    x_rotated = x_translated * np.cos(theta) - y_translated * np.sin(theta)
    y_rotated = x_translated * np.sin(theta) + y_translated * np.cos(theta)
    # Step 3: Translate points back
    x_rotated_back = x_rotated + P_ref[0]
    y_rotated_back = y_rotated + P_ref[1]
    #
    return x_rotated_back, y_rotated_back

def shift_phy_mk(self,x_rotated_back,y_rotated_back,z_data_np):
    # Apply shift to match markers
    # apply shift to the markers - From interface so user can adjust - 
    # First position for optmization comes from manual adjustment
    x_data_sh = x_rotated_back + self.IrIS_cal_MK_01.value() 
    y_data_sh = y_rotated_back + self.IrIS_cal_MK_02.value() 
    z_data_sh = z_data_np      + self.IrIS_cal_MK_03.value() 
    return x_data_sh, y_data_sh, z_data_sh

def update_table(self):
    # Reading table - Marker real positons (X,Y,Z) and measured projections (X,Y)
    x_data = []
    y_data = []
    z_data = []
    #
    # Reference point for rotation - central marker
    P_ref = np.zeros(3)
    for row in range(self.IrIS_cal_ref_table.rowCount()):
        try:
                x = float(self.IrIS_cal_ref_table.item(row, 0).text())
                y = float(self.IrIS_cal_ref_table.item(row, 1).text())
                z = float(self.IrIS_cal_ref_table.item(row, 2).text())
                x_data.append(x)
                y_data.append(y)
                z_data.append(z)
                if row == self.IrIS_cal_Ref_MK_ID.value()-1 :
                    P_ref[0] = x
                    P_ref[1] = y
                    P_ref[2] = z
        except ValueError:
            continue  # Skip rows with invalid data
    #
    #
    # Convert lists to NumPy arrays for efficient manipulation
    x_data_np = np.array(x_data)
    y_data_np = np.array(y_data)
    z_data_np = np.array(z_data)
    #
    # Apply transformation to physical markers
    #
    # rotation around Z
    theta_z = np.radians(self.IrIS_cal_MK_06.value())  # 
    x_rotated_back, y_rotated_back = rot_phy_mk_around_Z(theta_z,x_data_np,y_data_np,P_ref)
    #
    # rotation around Y
    theta_y = np.radians(self.IrIS_cal_MK_05.value())  # 
    x_rotated_back, z_rotated_back = rot_phy_mk_around_Y(theta_y,x_rotated_back,z_data_np,P_ref)
    
    # rotation around X
    theta_x = np.radians(self.IrIS_cal_MK_04.value())  # 
    y_rotated_back, z_rotated_back = rot_phy_mk_around_X(theta_x,y_rotated_back,z_rotated_back,P_ref)
    
    # Shift 
    x_data_sh, y_data_sh, z_data_sh = shift_phy_mk(self,x_rotated_back,y_rotated_back,z_rotated_back)
    
    # update table
    # Loop through each row in the table and update with the new values
    for row in range(self.IrIS_cal_ref_table.rowCount()):
        x_text = f"{x_data_sh[row]:.3f}"
        y_text = f"{y_data_sh[row]:.3f}"
        z_text = f"{z_data_sh[row]:.3f}"
        # Update the table with new X, Y, and Z values
        self.IrIS_cal_ref_table.item(row, 0).setText(x_text)
        self.IrIS_cal_ref_table.item(row, 1).setText(y_text)
        self.IrIS_cal_ref_table.item(row, 2).setText(z_text)
    #
    # set rotation and shift to zero as the values have been adjusted in the table already
    self.IrIS_cal_MK_01.setValue(0)
    self.IrIS_cal_MK_02.setValue(0)
    self.IrIS_cal_MK_03.setValue(0)
    self.IrIS_cal_MK_04.setValue(0)
    self.IrIS_cal_MK_05.setValue(0)
    self.IrIS_cal_MK_06.setValue(0)
    
                  
def plot_mk_cal_data(self):
    # Plot reference IrIS Image
    im_data =self.display_data_IrIS_eval[0][int(self.current_IrIS_eval_slice_index[0]), :, :]
    #
    # Reading table - Marker real positons (X,Y,Z) and measured projections (X,Y)
    x_data = []
    y_data = []
    z_data = []
    x_ref_mkdata = []
    y_ref_mkdata = []
    #
    # Reference point for rotation - central marker
    P_ref = np.zeros(3)
    for row in range(self.IrIS_cal_ref_table.rowCount()):
        try:
            ref_mk_x  = float(self.IrIS_cal_ref_table.item(row, 3).text())  
            ref_mk_y  = float(self.IrIS_cal_ref_table.item(row, 4).text())  
            if  ref_mk_x  > 0 and ref_mk_y  > 0 :  # Only consider active points
                x = float(self.IrIS_cal_ref_table.item(row, 0).text())
                y = float(self.IrIS_cal_ref_table.item(row, 1).text())
                z = float(self.IrIS_cal_ref_table.item(row, 2).text())
                x_data.append(x)
                y_data.append(y)
                z_data.append(z)
                x_ref_mkdata.append(ref_mk_x)
                y_ref_mkdata.append(ref_mk_y)
                if row == self.IrIS_cal_Ref_MK_ID.value()-1 :
                    P_ref[0] = x
                    P_ref[1] = y
                    P_ref[2] = z
        except ValueError:
            continue  # Skip rows with invalid data
    #
    #
    # Convert lists to NumPy arrays for efficient manipulation
    x_data_np = np.array(x_data)
    y_data_np = np.array(y_data)
    z_data_np = np.array(z_data)
    #
    # Apply transformation to physical markers
    #
    # rotation around Z
    theta_z = np.radians(self.IrIS_cal_MK_06.value())  # 
    x_rotated_back, y_rotated_back = rot_phy_mk_around_Z(theta_z,x_data_np,y_data_np,P_ref)
    #
    # rotation around Y
    theta_y = np.radians(self.IrIS_cal_MK_05.value())  # 
    x_rotated_back, z_rotated_back = rot_phy_mk_around_Y(theta_y,x_rotated_back,z_data_np,P_ref)
    
    # rotation around X
    theta_x = np.radians(self.IrIS_cal_MK_04.value())  # 
    y_rotated_back, z_rotated_back = rot_phy_mk_around_X(theta_x,y_rotated_back,z_rotated_back,P_ref)
    
    # Shift 
    x_data_sh, y_data_sh, z_data_sh = shift_phy_mk(self,x_rotated_back,y_rotated_back,z_rotated_back)

    # now we use provided source position to estimate new marker potions trying to match reference data 
    x_sou = self.IrIS_cal_Sour_01.value()
    y_sou = self.IrIS_cal_Sour_02.value()
    z_sou = self.IrIS_cal_Sour_03.value()  
    
    # intersection of the projection with z=0, EPID plane
    inter_x_fit, inter_y_fit  = find_intersections(x_sou, y_sou, z_sou, x_data_sh, y_data_sh, z_data_sh)
    
    # update projection values
    
    for row_index in range(self.IrIS_cal_ref_table.rowCount()):
        self.IrIS_cal_ref_table.setItem(row_index, 5, QTableWidgetItem("0"))
        self.IrIS_cal_ref_table.setItem(row_index, 6, QTableWidgetItem("0"))
    c=0
    for row in range(self.IrIS_cal_ref_table.rowCount()):
        try:
            ref_mk_x  = float(self.IrIS_cal_ref_table.item(row, 3).text())  
            ref_mk_y  = float(self.IrIS_cal_ref_table.item(row, 4).text())  
            if  ref_mk_x  > 0 and ref_mk_y  > 0 :  # Only consider active points
                x_text = f"{inter_x_fit[c]:.3f}"
                y_text = f"{inter_y_fit[c]:.3f}"
                c += 1
                # Update the table with X, Y for comparison
                self.IrIS_cal_ref_table.item(row, 5).setText(x_text)
                self.IrIS_cal_ref_table.item(row, 6).setText(y_text)
        except ValueError:
            continue  # Skip rows with invalid data
    
    # evaluate parameters
    avg_dist_x, avg_dist_y, avg_dist_z, avg_dist_x_rot, avg_dist_y_rot, avg_dist_z_rot = eval_best_fit(self,x_sou,y_sou,z_sou, x_data_sh, y_data_sh, z_data_sh,x_ref_mkdata, y_ref_mkdata, x_data_np, y_data_np, z_data_np, P_ref)

    # plot 1
    plot_image_markers(self,im_data,x_ref_mkdata, y_ref_mkdata,inter_x_fit, inter_y_fit)
    # plot 2
    plot_eval(self,avg_dist_x, avg_dist_y, avg_dist_z, avg_dist_x_rot, avg_dist_y_rot, avg_dist_z_rot)
    
     
def eval_best_fit(self,x_sou,y_sou,z_sou, x_data_sh, y_data_sh, z_data_sh,x_ref_mkdata, y_ref_mkdata, x_data_np, y_data_np, z_data_np, P_ref):
    # adjust each parameter around the selected value and compare the deviations
    # 
    avg_dist_z = []
    for shift in np.arange(-5,5.1,0.1):   
        eval_x_fit, eval_y_fit = find_intersections(x_sou, y_sou, z_sou+shift, x_data_sh, y_data_sh, z_data_sh+shift)
        dx = eval_x_fit - x_ref_mkdata
        dy = eval_y_fit - y_ref_mkdata
        # Calculate the Euclidean distance for each pair of points
        distances = np.sqrt(dx**2 + dy**2)
        # Calculate the average of these distances
        avg_dist_z.append(np.mean(distances))

    avg_dist_y = []
    for shift in np.arange(-5,5.1,0.1):   
        eval_x_fit, eval_y_fit = find_intersections(x_sou, y_sou+shift, z_sou, x_data_sh, y_data_sh+shift, z_data_sh)
        dx = eval_x_fit - x_ref_mkdata
        dy = eval_y_fit - y_ref_mkdata
        # Calculate the Euclidean distance for each pair of points
        distances = np.sqrt(dx**2 + dy**2)
        # Calculate the average of these distances
        avg_dist_y.append(np.mean(distances))
    
    avg_dist_x = []
    for shift in np.arange(-5,5.1,0.1):   
        eval_x_fit, eval_y_fit = find_intersections(x_sou+shift, y_sou, z_sou, x_data_sh+shift, y_data_sh, z_data_sh)
        dx = eval_x_fit - x_ref_mkdata
        dy = eval_y_fit - y_ref_mkdata
        # Calculate the Euclidean distance for each pair of points
        distances = np.sqrt(dx**2 + dy**2)
        # Calculate the average of these distances
        avg_dist_x.append(np.mean(distances))
    
    # rotations
    # rotation around Z
    avg_dist_z_rot = []
    for shift in np.arange(-5,5.1,0.1):   
        theta = np.radians(self.IrIS_cal_MK_06.value()+shift)  # 
        x_rot_eval, y_rot_eval = rot_phy_mk_around_Z(theta,x_data_np,y_data_np,P_ref)
        #
        # Shift 
        x_data_eval, y_data_eval, z_data_eval = shift_phy_mk(self,x_rot_eval, y_rot_eval,z_data_np)       
        # intersection of the proecjetion with z=0, EPID plane
        eval_x_fit, eval_y_fit  = find_intersections(x_sou, y_sou, z_sou, x_data_eval, y_data_eval, z_data_eval)
        dx = eval_x_fit - x_ref_mkdata
        dy = eval_y_fit - y_ref_mkdata
        # Calculate the Euclidean distance for each pair of points
        distances = np.sqrt(dx**2 + dy**2)
        # Calculate the average of these distances
        avg_dist_z_rot.append(np.mean(distances))
        
    # rotation around Y
    avg_dist_y_rot = []
    for shift in np.arange(-5,5.1,0.1):   
        #
        # rotation around Z
        theta_z = np.radians(self.IrIS_cal_MK_06.value())  # 
        x_rot_eval, y_rot_eval = rot_phy_mk_around_Z(theta_z,x_data_np,y_data_np,P_ref)
        #
        # rotation around Y
        theta = np.radians(self.IrIS_cal_MK_05.value()+shift)  # 
        x_rot_eval, z_rot_eval = rot_phy_mk_around_Y(theta,x_rot_eval,z_data_np,P_ref)
        
        # Shift 
        x_data_eval, y_data_eval, z_data_eval = shift_phy_mk(self,x_rot_eval, y_rot_eval, z_rot_eval)       
        # intersection of the proecjetion with z=0, EPID plane
        eval_x_fit, eval_y_fit  = find_intersections(x_sou, y_sou, z_sou, x_data_eval, y_data_eval, z_data_eval)
        dx = eval_x_fit - x_ref_mkdata
        dy = eval_y_fit - y_ref_mkdata
        # Calculate the Euclidean distance for each pair of points
        distances = np.sqrt(dx**2 + dy**2)
        # Calculate the average of these distances
        avg_dist_y_rot.append(np.mean(distances))
        
    # rotation around Y
    avg_dist_x_rot = []
    for shift in np.arange(-5,5.1,0.1):   
        #
        # rotation around Z
        theta_z = np.radians(self.IrIS_cal_MK_06.value())  # 
        x_rot_eval, y_rot_eval = rot_phy_mk_around_Z(theta_z,x_data_np,y_data_np,P_ref)
        #
        # rotation around Y
        theta_y = np.radians(self.IrIS_cal_MK_05.value())  # 
        x_rot_eval, z_rot_eval = rot_phy_mk_around_Y(theta_y,x_rot_eval,z_data_np,P_ref)
        # rotation around X
        theta = np.radians(self.IrIS_cal_MK_04.value()+shift)  # 
        y_rot_eval, z_rot_eval = rot_phy_mk_around_X(theta,y_rot_eval,z_rot_eval,P_ref)
        # Shift 
        x_data_eval, y_data_eval, z_data_eval = shift_phy_mk(self,x_rot_eval, y_rot_eval, z_rot_eval)       
        # intersection of the proecjetion with z=0, EPID plane
        eval_x_fit, eval_y_fit  = find_intersections(x_sou, y_sou, z_sou, x_data_eval, y_data_eval, z_data_eval)
        dx = eval_x_fit - x_ref_mkdata
        dy = eval_y_fit - y_ref_mkdata
        # Calculate the Euclidean distance for each pair of points
        distances = np.sqrt(dx**2 + dy**2)
        # Calculate the average of these distances
        avg_dist_x_rot.append(np.mean(distances))   
        
    return avg_dist_x, avg_dist_y, avg_dist_z, avg_dist_x_rot, avg_dist_y_rot, avg_dist_z_rot

def export_mk_pos2csv(self):
    # Reading table - Marker real positons (X,Y,Z) and measured projections (X,Y)
    x_data = []
    y_data = []
    z_data = []
    #
    for row in range(self.IrIS_cal_ref_table.rowCount()):
        try:
                x  = float(self.IrIS_cal_ref_table.item(row, 0).text())
                y  = float(self.IrIS_cal_ref_table.item(row, 1).text())
                z  = float(self.IrIS_cal_ref_table.item(row, 2).text())
                x_data.append(x)
                y_data.append(y)
                z_data.append(z)
        except ValueError:
            continue  # Skip rows with invalid data
    #
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    fileName, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)", options=options)
    
    if fileName:
        if not fileName.endswith('.csv'):
            fileName += '.csv'
        # Create a DataFrame from the collected data
        df = pd.DataFrame({
            'X(mm)': x_data,
            'Y(mm)': y_data,
            'Z(mm)': z_data
        })
        # Save the DataFrame to CSV
        df.to_csv(fileName, index=False)
        QMessageBox.information(self, "Success", f"File was successfully saved to {fileName}")
    else:
        QMessageBox.warning(self, "Cancelled", "Operation was cancelled.")

def plot_image_markers(self,im_data,x_ref_mkdata, y_ref_mkdata,inter_x_fit, inter_y_fit):
    # Create a figure and canvas for 3D plotting
    fig = Figure(figsize=(10, 10), dpi=200)
    fig.patch.set_alpha(0.0)  # Set the background transparency of the figure
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.set_facecolor("none")  # Set the background transparency of the axes
     
    # reference image
    ax.imshow(im_data, cmap='gray', extent=[0, im_data.shape[1]*0.45, im_data.shape[0]*0.45, 0])
    # reference data markers projections
    ax.scatter(x_ref_mkdata, y_ref_mkdata, facecolors='none', edgecolors='red', linewidth=1, label='Measured',s=3)
    # Prediuction that will be used to match reference
    ax.scatter(inter_x_fit, inter_y_fit,edgecolor='blue', marker='o',facecolors='none',linewidth=1, label='Prediction',s=3)
    
    # Labels and Legend
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.legend()
    
    ax.set_xlabel('X', color='white')
    ax.set_ylabel('Y', color='white')
    # Set tick labels color to white
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.set_xlim(0,430)
    ax.set_ylim(0,430)
    
    
    # Clear existing layout contents
    layout = self.IrIS_cal_widget01.layout()
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
    else:
        layout = QVBoxLayout(self.IrIS_cal_widget01)
    
    # Add the canvas and toolbar to the specified QWidget
    toolbar = NavigationToolbar(canvas, self.IrIS_cal_widget01)
    layout.addWidget(toolbar)
    layout.addWidget(canvas)
    self.IrIS_cal_widget01.setLayout(layout)
    canvas.draw()


    
    
def plot_eval(self,avg_dist_x, avg_dist_y, avg_dist_z, avg_dist_x_rot, avg_dist_y_rot, avg_dist_z_rot):     
    # Create a figure and canvas for plotting
    fig_2 = Figure(figsize=(10, 10), dpi=200)
    fig_2.patch.set_alpha(0.0)  # Set the background transparency of the figure
    canvas_2 = FigureCanvas(fig_2)
    ax2 = fig_2.add_subplot(111)
    ax2.set_facecolor("none")  # Set the background transparency of the axes
    
    if self.IrIS_Cal_plot_mm.isChecked():
        ax2.plot(np.arange(-5,5.1,0.1), avg_dist_z, label='Z', color='purple', linestyle='-', linewidth=1)
        ax2.plot(np.arange(-5,5.1,0.1), avg_dist_y, label='Y', color='green', linestyle='-', linewidth=1)
        ax2.plot(np.arange(-5,5.1,0.1), avg_dist_x, label='X', color='red', linestyle='-', linewidth=1)
    #
    if self.IrIS_Cal_plot_deg.isChecked():
        ax2.plot(np.arange(-5,5.1,0.1), avg_dist_z_rot, label='Zrot', color='purple', linestyle='--', linewidth=1)
        ax2.plot(np.arange(-5,5.1,0.1), avg_dist_y_rot, label='Yrot', color='green', linestyle='--', linewidth=1)
        ax2.plot(np.arange(-5,5.1,0.1), avg_dist_x_rot, label='Xrot', color='red', linestyle='--', linewidth=1)
    
    ax2.set_ylabel('Mean of Distances', color='white')
    ax2.set_xlabel('Shift (mm or deg)', color='white')
    # Set tick labels color to white
    ax2.tick_params(axis='x', colors='white')
    ax2.tick_params(axis='y', colors='white')
    ax2.legend()
    # Clear existing layout contents
    layout = self.IrIS_cal_widget02.layout()
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
    else:
        layout = QVBoxLayout(self.IrIS_cal_widget02)

    # Add the canvas and toolbar to the specified QWidget
    toolbar = NavigationToolbar(canvas_2, self.IrIS_cal_widget02)
    layout.addWidget(toolbar)
    layout.addWidget(canvas_2)
    self.IrIS_cal_widget02.setLayout(layout)
    canvas_2.draw()