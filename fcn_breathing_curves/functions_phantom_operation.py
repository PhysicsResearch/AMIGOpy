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

UPDATE_INTERVAL = 0.1    # seconds between polls
WINDOW_DURATION = 10     # seconds to show on the plot

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


def set_GCODE_speed(self):
    speed_factor = self.MoVeSpeedFactor.value()
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
    # self.MoVeData = []

    max_points = int(WINDOW_DURATION / UPDATE_INTERVAL)
    self.time_buffer = deque(maxlen=max_points)
    self.x_buffer = deque(maxlen=max_points)
    self.y_buffer = deque(maxlen=max_points)
    self.z_buffer = deque(maxlen=max_points)
    self.speed_buffer = deque(maxlen=max_points)

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
    # plt.show()


def get_curr_file(self):
    url = f'http://{self.duet_ip}/rr_fileinfo'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['err'] == 1:
            return None
        filepath = data['fileName']
        self.tprint = data['printDuration']
        _, filename = os.path.split(filepath)
        return filename
    else:
        QMessageBox.warning(None, "Warning", "No valid Duet IP provided.")
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
            x, y, z = data['coords']['xyz']
            speed = data['speeds']['requested']
            top_speed = data['speeds']['top']
            t = time.time() - self.t0 + self.tprint
            return t, x, y, z, speed, top_speed
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Exception: {e}")


def update_MoVeData(self):
    try:
        t, x, y, z, speed, top_speed = get_duet_status(self)

        self.time_buffer.append(t)
        self.x_buffer.append(x)
        self.y_buffer.append(y)
        self.z_buffer.append(z)  # Example: Z position
        self.speed_buffer.append((speed * 60 == 1200) * 5)
        # self.MoVeData.append([t, x, y, z, speed, top_speed])
        plot_MoVeData(self)
    except:
        return


def plot_MoVeData(self):
    ax = self.fig_MoVe.gca()
    # ax1 = ax.twinx()

    ax.clear()
    ax.plot(self.time_buffer, self.x_buffer, label="x")
    ax.plot(self.time_buffer, self.y_buffer, label="y")
    ax.plot(self.time_buffer, self.z_buffer, label="z")
    ax.plot(self.time_buffer, self.speed_buffer, label="speed check", color="r")

    # plot original data
    t0, t1 = min(self.time_buffer), max(self.time_buffer) 
    t_offset = self.MoVeOffsetSlider.value() * UPDATE_INTERVAL
    t_roi = self.orig_data.loc[(self.orig_data["timestamp"] >= t0 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset), "timestamp"] - t_offset
    x_roi = self.orig_data.loc[(self.orig_data["timestamp"] >= t0 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset), "amplitude"]
    ax.plot(t_roi, x_roi, label="og", color="pink")

    t_offset = self.MoVeOffsetSlider.value() * UPDATE_INTERVAL
    t_roi = self.orig_data.loc[(self.orig_data["timestamp"] > t1 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset + 10), "timestamp"] - t_offset
    x_roi = self.orig_data.loc[(self.orig_data["timestamp"] > t1 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset + 10), "amplitude"]
    ax.plot(t_roi, x_roi, linestyle="--", color="pink")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Position (mm)")
    ax.legend()

    # ax1.clear()
    # print(len(self.speed_buffer))
    # ax1.plot(self.time_buffer, self.speed_buffer, "r-")

    self.MoVeCanvas.draw()
