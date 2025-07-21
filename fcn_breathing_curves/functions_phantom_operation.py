import os
import requests
import time
from collections import deque
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from PyQt5.QtWidgets import QVBoxLayout, QFileDialog, QMessageBox
from PyQt5 import QtCore

WINDOW_DURATION = 10     # seconds to show on the plot
UPDATE_INTERVAL = 0.05    # seconds between polls

def set_fcn_MoVeTab_changed(self):
    # Connect the currentChanged signal to the onTabChanged slot
    self.BrCv_PhOperWidget.currentChanged.connect(lambda: onTabChanged(self))


def onTabChanged(self):
    if self.BrCv_PhOperWidget.currentIndex() == 1:
        self.MoVeSpeedFactor.setValue(100)
        self.MoVeSpeedFactor.valueChanged.connect(lambda: set_GCODE_speed(self))
        init_MoVeTab(self)


def setDuetIP(self):
    self.duet_ip = self.DuetIPAddress.text()


def defineInputFolder(self):
    options = QFileDialog.Options()
    folder = QFileDialog.getExistingDirectory(self, options=options)
    self.PhOperFolder.setText(folder)


def set_GCODE_speed(self, sf=None):
    if self.MoVeAutoControl.isChecked() and sf is None:
        return
    if sf is None:
        speed_factor = self.MoVeSpeedFactor.value()
    else:
        speed_factor = sf
        self.MoVeSpeedFactor.setValue(int(speed_factor))
    url = f'http://{self.duet_ip}/rr_gcode'
    code = f"M220 S{speed_factor}"
    r = requests.get(url, {'gcode': code})


def init_MoVeTab(self):
    self.duet_ip = self.DuetIPAddress.text()
    filename = get_curr_file(self)
    if filename is None:
        return
    import_planned_curve(self, filename)
    if self.orig_data is None:
        return

    self.MoVeOffsetSlider.setRange(-150, 150)

    self.t0 = time.time() 
    self.MoVeData = {'t': [], 'x': [], 'acq': []}

    max_points = int(WINDOW_DURATION / UPDATE_INTERVAL)
    self.time_buffer = deque(maxlen=max_points)
    self.x_buffer = deque(maxlen=max_points)

    self.fig_MoVe = Figure()  # Create a figure for the first time
    self.MoVeCanvas = FigureCanvas(self.fig_MoVe)
    self.MoVeCanvas.setStyleSheet("background-color:Transparent;")

    container = self.MoVeView
    layout = container.layout()
    if layout is None:
        layout = QVBoxLayout(container)
        container.setLayout(layout)
    else:
        # Clear existing content in the container, if any
        while container.layout().count():
            child = container.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    layout.addWidget(self.MoVeCanvas)

    self.ani = FuncAnimation(self.fig_MoVe, lambda i: update_MoVeData(self), interval=UPDATE_INTERVAL * 1000)
    plt.tight_layout()


def get_curr_file(self, init=True):
    url = f'http://{self.duet_ip}/rr_fileinfo'
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['err'] == 1:
                return None
            filepath = data['fileName']
            if init == True:
                self.tprint = data['printDuration']
            _, filename = os.path.split(filepath)
            return filename
    except:
        QMessageBox.warning(None, "Warning", "Duet could not be reached.")
        return None       


def import_planned_curve(self, filename):
    csv_root = self.PhOperFolder.text()
    if not os.path.exists(csv_root):
        self.orig_data = None
        QMessageBox.warning(None, "Warning", "No valid input folder was provided.")
        return
    filepath = os.path.join(csv_root, filename.replace("gcode", "csv"))
    if not os.path.exists(filepath):
        self.orig_data = None
        QMessageBox.warning(None, "Warning", "The input folder does not contain a csv file corresponding to the GCODE being executed.")
        return
    self.orig_data = pd.read_csv(filepath)


def get_duet_status(self):
    url = f'http://{self.duet_ip}/rr_status?type=3'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            x = data['coords']['xyz'][0]
            t = time.time() - self.t0 + self.tprint
            return t, x
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Exception: {e}")


def update_MoVeData(self):
    try:
        t, x = get_duet_status(self)

        if not self.MoVeAutoControl.isChecked():
            self.MoVeUserSetSpeed = self.MoVeSpeedFactor.value()
        if self.MoVeAutoControl.isChecked():
            calc_diff(self)

        self.time_buffer.append(t)
        self.x_buffer.append(x)
        self.MoVeData['t'].append(t); self.MoVeData['x'].append(x)
        self.MoVeData['acq'].append(0)
        plot_MoVeData(self)
    except:
        return
    

def calc_diff(self):
    try:
        t = self.time_buffer[-1]
        x_meas = self.x_buffer[-1]

        t_offset = self.MoVeOffsetSlider.value() * UPDATE_INTERVAL
        t0, t1 = t - 1.5, t + 1.5

        t_roi = self.orig_data.loc[(self.orig_data["timestamp"] >= t0 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset), "timestamp"] - t_offset
        x_plan = self.orig_data.loc[(self.orig_data["timestamp"] >= t0 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset), "amplitude"]

        ampl_diff = x_plan - x_meas
        idx = ampl_diff.abs().idxmin()
        t_diff = t - t_roi[idx]

        # calculate the speed factor adjustment, relative to user defined default 
        # and clip between 90 - 20 to avoid explosive speed changes
        sf = np.clip(self.MoVeUserSetSpeed * (t_diff * np.median(self.MoVeData['x']) / 35 + 1), 90, 120)
        set_GCODE_speed(self, sf)
    except:
        return


def setAcqStart(self):
    try:
        self.MoVeData['acq'][-1] = 1
        self.MoVeAcqStart.setStyleSheet("background-color: blue; color:white")
        QMessageBox.information(None, "Info", f"MoVe Acquistion time stamp added")
    except:
        return


def exportMoVeData(self):
    try:
        csv_root = self.PhOperFolder.text()
        if not os.path.exists(csv_root):
            return

        self.exportDataMoVe.setStyleSheet("background-color: blue; color:white")
        filename = get_curr_file(self, init=False)
        if filename is None:
            return

        filepath = os.path.join(csv_root, filename.replace(".gcode", "_MoVe.csv"))
        df = pd.DataFrame(self.MoVeData)
        df.to_csv(filepath, index=False)
        QMessageBox.information(None, "Info", f"MoVe Data exported to {filepath}")
    except:
        pass

    
def plot_MoVeData(self):
    ax = self.fig_MoVe.gca()

    ax.clear()
    ax.plot(self.time_buffer, self.x_buffer)

    # plot original data
    t0, t1 = min(self.time_buffer), max(self.time_buffer) 
    t_offset = self.MoVeOffsetSlider.value() * UPDATE_INTERVAL
    t_roi = self.orig_data.loc[(self.orig_data["timestamp"] >= t0 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset), "timestamp"] - t_offset
    x_roi = self.orig_data.loc[(self.orig_data["timestamp"] >= t0 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset), "amplitude"]
    ax.plot(t_roi, x_roi, color="pink")

    t_roi = self.orig_data.loc[(self.orig_data["timestamp"] > t1 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset + 10), "timestamp"] - t_offset
    x_roi = self.orig_data.loc[(self.orig_data["timestamp"] > t1 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset + 10), "amplitude"]
    ax.plot(t_roi, x_roi, linestyle="--", color="pink")

    acq_timestamps = self.orig_data.loc[(self.orig_data["acq"] == 1) & \
                                        (self.orig_data["timestamp"] >= t0 + t_offset) & \
                                        (self.orig_data["timestamp"] <= t1 + t_offset + 10 + self.MoVeSystemLatency.value()), 
                                        "timestamp"] - t_offset
    start_timestamps = acq_timestamps - self.MoVeSystemLatency.value() 
    ax.vlines(acq_timestamps, 0, 20, color="red")
    ax.vlines(start_timestamps, 0, 20, color="green")
    [ax.axvspan(xmin=t_acq, xmax=t_acq + 6, color="lightblue") \
     for t_acq in acq_timestamps]

    copy_timestamps = self.orig_data.loc[(self.orig_data["start"] == 1) & \
                                         (self.orig_data["timestamp"] >= t0 + t_offset) & \
                                         (self.orig_data["timestamp"] <= t1 + t_offset + 10), 
                                         "timestamp"] - t_offset
    ax.vlines(copy_timestamps, 0, 20, color="blue")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Position (mm)")
    ax.legend()
    ax.set_xlim(min(self.time_buffer), max(self.time_buffer)+10)

    self.MoVeCanvas.draw()
    self.MoVeAcqStart.setStyleSheet("background-color: green; color:white")
    self.exportDataMoVe.setStyleSheet("background-color: green; color:white")
