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
from PyQt5.QtCore import QThread, QUrl
from datetime import datetime

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
    self.DuetControlView.setUrl(QUrl(self.duet_ip))
    self.DuetControlView.reload()
    self.DuetControlView.setUrl(QUrl())


def defineInputFolder(self):
    options = QFileDialog.Options()
    folder = QFileDialog.getExistingDirectory(self, options=options)
    self.PhOperFolder.setText(folder)


def get_curr_file(self, init=True):
    # Get the filename of the GCODE currently being executed on Duet
    try:
        url = f'http://{self.duet_ip}/rr_fileinfo'
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data['err'] == 1:
                QMessageBox.warning(None, "Warning", "Duet could not be reached.")
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
    # Import the reference curve from a CSV file corresponding to the GCODE being executed
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


def set_GCODE_speed(self, sf=None):
    # Send a GCODE command to adjust the speed factor on Duet
    if self.MoVeAutoControl.isChecked() and sf is None:
        return
    if sf is None:
        speed_factor = self.MoVeSpeedFactor.value()
    else:
        speed_factor = sf
        self.MoVeSpeedFactor.setValue(int(speed_factor))
    try:
        url = f'http://{self.duet_ip}/rr_gcode'
        code = f"M220 S{speed_factor}"
        requests.get(url, {'gcode': code})
    except Exception as e:
        print(f"Exception while sending GCODE: {e}")


def init_MoVeTab(self):
    self.duet_ip = self.DuetIPAddress.text()
    filename = get_curr_file(self)
    if filename is None:
        return
    
    import_planned_curve(self, filename)
    if self.orig_data is None:
        return
    
    self.acq_timestamps = self.orig_data.loc[(self.orig_data["acq"] == 1), "timestamp"].tolist()
    self.MoVeOffsetSlider.setRange(-200, 200)

    self.t0 = time.time() 
    self.MoVeData = {'t': [], 'x': [], 'acq': [], 'geiger': []}

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
    plt.tight_layout()

    # Start MoVe data thread
    self.ani = FuncAnimation(self.fig_MoVe, lambda frame: update_MoVeData(self), interval=50)
    plt.show()
    # self.move_thread = MoVeThread(self)
    # self.move_thread.start()


class MoVeThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.running = True
        self.parent = parent

    def run(self):
        interval = 0.05  # 50 ms
        while self.running:
            start_time = time.time()
            update_MoVeData(self.parent)
            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)
            time.sleep(sleep_time)

    def stop(self):
        self.running = False
        self.wait()


def get_duet_status(self):
    try:
        url = f'http://{self.duet_ip}/rr_status?type=3'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            x = data['coords']['xyz'][0]
            geiger = data['sensors']['probeValue']
            t = time.time() - self.t0 + self.tprint
            return t, x, geiger
        else:
            print(f"Error: {response.status_code}")
            return None, None, None
    except Exception as e:
        print(f"Exception while retrieving DUET data: {e}")
        return None, None, None


def pause_continue_GCODE(self, pause=True):
    # Send a GCODE command to pause the current print on Duet
    try:
        code = "M25" if pause else "M24"
        url = f'http://{self.duet_ip}/rr_gcode'
        response = requests.get(url, {'gcode': code})
        if response.status_code != 200:
            print(f"Error pausing GCODE: {response.status_code}")
    except Exception as e:
        print(f"Exception while pausing GCODE: {e}")


def update_MoVeData(self):
    try:
        t, x, geiger = get_duet_status(self)
        if t is None:
            return
        
        if len(self.acq_timestamps) > 0 and \
            t > self.acq_timestamps[0] - self.MoVeOffsetSlider.value() * UPDATE_INTERVAL:
            self.acq_timestamps.pop(0)

            if self.stop_until_radiation.isChecked():
                # Pause if not paused yet
                if not hasattr(self, 'pause'):
                    pause_continue_GCODE(self)
                    self.pause = time.time()
                    return
            
        if self.stop_until_radiation.isChecked() and hasattr(self, 'pause'):
            # Continue if paused and radiation detected
            if hasattr(self, 'pause') and geiger > 0:
                    self.t0 += (time.time() - self.pause)
                    t       -= (time.time() - self.pause)
                    pause_continue_GCODE(self, False)
                    delattr(self, 'pause')
                    self.MoVeData['t'].append(t)
                    self.MoVeData['x'].append(x)
                    self.MoVeData['acq'].append(1)
                    self.MoVeData['geiger'].append(1000)
                    return
            else:  
                return
            
        if not self.MoVeAutoControl.isChecked():
            self.MoVeUserSetSpeed = self.MoVeSpeedFactor.value()
        if self.MoVeAutoControl.isChecked():
            calc_diff(self)

        self.time_buffer.append(t)
        self.x_buffer.append(x)
        self.MoVeData['t'].append(t)
        self.MoVeData['x'].append(x)
        self.MoVeData['acq'].append(0)
        self.MoVeData['geiger'].append(geiger)
        plot_MoVeData(self)
    except:
        return
    

def calc_diff(self):
    # Get the last time and position from the buffers
    t = self.time_buffer[-1]
    x_meas = self.x_buffer[-1]

    t_offset = self.MoVeOffsetSlider.value() * UPDATE_INTERVAL
    t0, t1 = t - 1.5, t + 1.5

    df_roi = self.orig_data.loc[(self.orig_data["timestamp"] >= t0 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset)]
    t_roi = df_roi["timestamp"] - t_offset
    x_planned = df_roi["amplitude"]

    # Calculate t_offset with minimum amplitude differences
    ampl_diff = x_planned - x_meas
    idx = ampl_diff.abs().idxmin()
    t_diff = t - t_roi[idx]

    # Calculate the speed factor adjustment, relative to user defined default 
    sf = self.MoVeUserSetSpeed * (t_diff * np.median(self.MoVeData['x']) / 35 + 1)

    # Clip between 90 - 120% to avoid explosive speed changes
    sf = np.clip(sf, 0.9 * self.MoVeUserSetSpeed, 1.2 * self.MoVeUserSetSpeed)

    # Set adjusted GCODE speed factor
    set_GCODE_speed(self, sf)


def setAcqStart(self):
    # Set the start of an acquisition
    self.MoVeData['acq'][-1] = 1
    QMessageBox.information(None, "Info", f"MoVe Acquistion time stamp added")


def stop_threads(self):
    # Set the threads to stop when MoVe is finished
    if hasattr(self, "move_thread") and self.move_thread.isRunning():
        self.move_thread.stop()


def exportMoVeData(self):
    # Export the MoVe data to a CSV file
    csv_root = self.PhOperFolder.text()
    if not os.path.exists(csv_root):
        return

    filename = get_curr_file(self, init=False)
    if filename is None:
        return
    
    if not hasattr(self, 'MoVeData'):
        return

    formatted_time = datetime.now().strftime("%Y%m%d_%H%M") 
    filepath = os.path.join(csv_root, filename.replace(".gcode", f"_MoVe_{formatted_time}.csv"))
    df = pd.DataFrame(self.MoVeData)
    df.to_csv(filepath, index=False)

    
def plot_MoVeData(self):
    ax = self.fig_MoVe.gca()
    ax.clear()

    # Plot measured signal from buffer
    ax.plot(self.time_buffer, self.x_buffer)

    # Plot past planned signal from csv data
    t0, t1 = min(self.time_buffer), max(self.time_buffer) 
    t_offset = self.MoVeOffsetSlider.value() * UPDATE_INTERVAL
    df_roi = self.orig_data.loc[(self.orig_data["timestamp"] >= t0 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset)]
    t_roi = df_roi["timestamp"] - t_offset
    x_roi = df_roi["amplitude"]
    ax.plot(t_roi, x_roi, color="pink")

    # Plot planned signal ahead of current time
    df_roi = self.orig_data.loc[(self.orig_data["timestamp"] > t1 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset + 10)]
    t_roi = df_roi["timestamp"] - t_offset
    x_roi = df_roi["amplitude"]
    ax.plot(t_roi, x_roi, linestyle="--", color="pink")

    # Plot timestamps and window of acquisition regions-of-interest
    acq_timestamps = self.orig_data.loc[(self.orig_data["acq"] == 1) & \
                                        (self.orig_data["timestamp"] >= t0 + t_offset) & \
                                        (self.orig_data["timestamp"] <= t1 + t_offset + 10 + self.MoVeSystemLatency.value()), 
                                        "timestamp"] - t_offset

    ax.vlines(acq_timestamps, 0, 20, color="red")
    ax.vlines(acq_timestamps - self.MoVeSystemLatency.value(), 0, 20, color="green")
    for t_acq in acq_timestamps:
        ax.axvspan(xmin=t_acq, xmax=t_acq + 6, color="lightblue") 

    # Plot timestamps of start of copies
    copy_timestamps = self.orig_data.loc[(self.orig_data["start"] == 1) & \
                                         (self.orig_data["timestamp"] >= t0 + t_offset) & \
                                         (self.orig_data["timestamp"] <= t1 + t_offset + 10), 
                                         "timestamp"] - t_offset
    ax.vlines(copy_timestamps, 0, 20, color="blue")
    ax.vlines(copy_timestamps - self.MoVeSystemLatency.value(), 0, 20, color="green")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Position (mm)")
    ax.set_xlim(min(self.time_buffer), max(self.time_buffer)+10)

    self.MoVeCanvas.draw()

    # Stop MoVe if end of curve is reached
    if self.orig_data['timestamp'].max() < t1 + t_offset:
        exportMoVeData(self)
        self.ani.event_source.stop()
        