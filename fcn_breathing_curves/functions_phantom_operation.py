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
from PyQt5.QtCore import QTimer, QThread, QUrl
import pyaudio
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


class AudioThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.running = True
        self.parent = parent

    def run(self):
        interval = 0.01 # 10 ms
        while self.running:
            start_time = time.time()
            record_audio_chunk(self.parent)
            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)
            time.sleep(sleep_time)

    def stop(self):
        self.running = False
        self.wait()


def record_audio_chunk(self):
    t = time.time() - self.t0 + self.tprint
    try:
        data = self.stream.read(self.CHUNK, exception_on_overflow=False)
        samples = np.frombuffer(data, dtype=np.int16)
        volume = np.max(np.abs(samples))
    except:
        volume = np.nan
    self.audio_signal.append([t, volume])


def initialize_audio_stream(self):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    self.CHUNK = 1024

    p = pyaudio.PyAudio()
    default_input_index = p.get_default_input_device_info()["index"]
    print(f"Recording: {p.get_default_input_device_info()['name']}")
    self.stream = p.open(format=FORMAT,
                         channels=CHANNELS,
                         rate=RATE,
                         input=True,
                         input_device_index=default_input_index,
                         frames_per_buffer=self.CHUNK)


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

    # Initialize Audio Record
    initialize_audio_stream(self)
    self.audio_signal = []

    # Start audio thread
    self.audio_thread = AudioThread(self)
    self.audio_thread.start()

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
    self.move_thread = MoVeThread(self)
    self.move_thread.start()


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

        # Calculate t_offset with minimum amplitude differences
        ampl_diff = x_plan - x_meas
        idx = ampl_diff.abs().idxmin()
        t_diff = t - t_roi[idx]

        # Calculate the speed factor adjustment, relative to user defined default 
        sf = self.MoVeUserSetSpeed * (t_diff * np.median(self.MoVeData['x']) / 35 + 1)
        # Clip between 90 - 120% to avoid explosive speed changes
        sf = np.clip(sf, 0.9 * self.MoVeUserSetSpeed, 1.2 * self.MoVeUserSetSpeed)

        # Set adjusted GCODE speed factor
        set_GCODE_speed(self, sf)
    except:
        return


def setAcqStart(self):
    self.MoVeData['acq'][-1] = 1
    QMessageBox.information(None, "Info", f"MoVe Acquistion time stamp added")


def stop_threads(self):
    if hasattr(self, "audio_thread") and self.audio_thread.isRunning():
        self.audio_thread.stop()

    if hasattr(self, "move_thread") and self.move_thread.isRunning():
        self.move_thread.stop()
        print('threads stopped')


def exportMoVeData(self):
    csv_root = self.PhOperFolder.text()
    if not os.path.exists(csv_root):
        return

    filename = get_curr_file(self, init=False)
    if filename is None:
        return
    
    if not (hasattr(self, 'MoVeData') and hasattr(self, 'audio_signal')):
        return

    now = datetime.now()
    formatted_time = now.strftime("%Y%m%d_%H%M") 
    filepath = os.path.join(csv_root, filename.replace(".gcode", f"_MoVe_{formatted_time}.csv"))
    df = pd.DataFrame(self.MoVeData)
    df.to_csv(filepath, index=False)

    df = pd.DataFrame(self.audio_signal[0:-2])
    df.to_csv(filepath.replace('MoVe', 'scan_intervals'))
    QMessageBox.information(None, "Info", f"MoVe Data exported to {filepath}")
    stop_threads(self)

    
def plot_MoVeData(self):
    ax = self.fig_MoVe.gca()
    ax.clear()

    # Plot measured signal from buffer
    ax.plot(self.time_buffer, self.x_buffer)

    # Plot planned signal from csv data
    t0, t1 = min(self.time_buffer), max(self.time_buffer) 
    t_offset = self.MoVeOffsetSlider.value() * UPDATE_INTERVAL
    t_roi = self.orig_data.loc[(self.orig_data["timestamp"] >= t0 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset), "timestamp"] - t_offset
    x_roi = self.orig_data.loc[(self.orig_data["timestamp"] >= t0 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset), "amplitude"]
    ax.plot(t_roi, x_roi, color="pink")

    t_roi = self.orig_data.loc[(self.orig_data["timestamp"] > t1 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset + 10), "timestamp"] - t_offset
    x_roi = self.orig_data.loc[(self.orig_data["timestamp"] > t1 + t_offset) & (self.orig_data["timestamp"] <= t1 + t_offset + 10), "amplitude"]
    ax.plot(t_roi, x_roi, linestyle="--", color="pink")

    # Plot timestamps of acquisition regions-of-interest
    acq_timestamps = self.orig_data.loc[(self.orig_data["acq"] == 1) & \
                                        (self.orig_data["timestamp"] >= t0 + t_offset) & \
                                        (self.orig_data["timestamp"] <= t1 + t_offset + 10 + self.MoVeSystemLatency.value()), 
                                        "timestamp"] - t_offset

    ax.vlines(acq_timestamps, 0, 20, color="red")
    ax.vlines(acq_timestamps - self.MoVeSystemLatency.value(), 0, 20, color="green")
    [ax.axvspan(xmin=t_acq, xmax=t_acq + 6, color="lightblue") \
     for t_acq in acq_timestamps]

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
        stop_threads(self)
        exportMoVeData(self)