import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem

def openCSVFile_BrCv(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open CSV and VXP File", "", "CSV Files (*.csv *.vxp);;All Files (*)", options=options)
        if fileName:
            if fileName.lower().endswith('.vxp'):
                previewVXP(self, fileName)
                processVXP(self, fileName)
            else:
                previewCSV(self,fileName)
                processCSV(self,fileName)


def previewVXP(self, filePath):
    try:
        with open(filePath, 'r') as file:
            # Read the next 100 lines and add line numbers
            lines = []
            for i in range(1, 101):
                line = file.readline()
                if '[Data]' in line:
                    self.lineSkipCSV_BrCv.setValue(i)  # Set the line number containing data
                if 'Data_layout' in line:
                    self.lineHeadCSV_BrCv.setValue(i)  # Set the line number containing header
                if not line:
                    break
                lines.append(f"{i}: {line}")
            
            preview = ''.join(lines)
        self.textViewCSV_BrCv.setPlainText(preview)
    except Exception as e:
        self.textViewCSV_BrCv.setPlainText(f'Error reading file: {e}')


def previewCSV(self, filePath):
    try:
        with open(filePath, 'r') as file:
            # Read the next 100 lines and add line numbers
            lines = []
            for i in range(1, 101):
                line = file.readline()
                if not line:
                    break
                lines.append(f"{i}: {line}")

            preview = ''.join(lines)
        self.textViewCSV_BrCv.setPlainText(preview)
    except Exception as e:
        self.textViewCSV_BrCv.setPlainText(f'Error reading file: {e}')


def processVXP(self, filePath):
    separator   = self.csv_sep_list_BrCv.currentText()
    skip_lines  = int(self.lineSkipCSV_BrCv.value())
    header_line = int(self.lineHeadCSV_BrCv.value())-1
    scale_factor = 1.0

    # Determine the header parameter for pandas read_csv 
    if header_line >= 0:
        # Read the header line separately
        with open(filePath, 'r') as file:
            for i, line in enumerate(file):
                if i == header_line: 
                    header_param = line.strip().split('=')[1].split(separator)
                if "Scale_factor" in line:
                    scale_factor = float(line.split('=')[1].strip())
                if i == skip_lines:
                    break
    else:
        header_param = None

    # Load the CSV file into a DataFrame
    try:
        dataframe = pd.read_csv(filePath, sep=separator, skiprows=skip_lines, header=None)
        dataframe.columns = header_param

        # Ensure 'timestamp' is the first column
        if 'timestamp' in dataframe.columns:
            cols = dataframe.columns.tolist()
            cols.insert(0, cols.pop(cols.index('timestamp')))
            dataframe = dataframe[cols]

        # Ensure 'amplitude' is the second column
        if 'amplitude' in dataframe.columns:
            cols = dataframe.columns.tolist()
            cols.insert(1, cols.pop(cols.index('amplitude')))
            dataframe = dataframe[cols]

        # If no header, set default column names
        if header_line == -1:
            dataframe.columns = [f'C{i+1}' for i in range(dataframe.shape[1])]

        # Scale and flip amplitude if needed
        dataframe["amplitude"] = dataframe["amplitude"] * scale_factor
        if self.flipCSV_BrCv.isChecked():
            dataframe["amplitude"] = dataframe["amplitude"] * -1

        # Add additional information
        self.curve_origin = "measured"
        dataframe = dataframe[dataframe.loc[::-1, 'amplitude'].ne(0).cummax()]
        dataframe = addColumns(self, dataframe)
        
        # Update the combo boxes for x and y axis selection
        self.plotXAxis_BrCv.clear()
        self.plotYAxis_BrCv.clear()
        self.plotXAxis_BrCv.addItems(dataframe.columns)
        self.plotYAxis_BrCv.addItems(dataframe.columns)

        if hasattr(self, 'lower_bound'):
            del self.lower_bound
        if hasattr(self, 'upper_bound'):
            del self.upper_bound

        # Display the data in the QTableWidget
        loadTable(self, dataframe, header_line)

    except pd.errors.ParserError as e:
        print(f"Error parsing CSV file: {e}")
        # Handle the error, e.g., by logging or showing a message to the user

    
def processCSV(self, filePath):
    separator   = self.csv_sep_list_BrCv.currentText()
    skip_lines  = int(self.lineSkipCSV_BrCv.value())
    header_line = int(self.lineHeadCSV_BrCv.value())-1
    # Determine the header parameter for pandas read_csv
    header_param = header_line if header_line >= 0 else None
    
    # Load the CSV file into a DataFrame
    try:
        dataframe = pd.read_csv(filePath, sep=separator, skiprows=skip_lines, header=header_param)
        # Remove columns that are completely NaN
        dataframe = dataframe.dropna(axis=1, how='all')
        
        if 'timestamp' not in dataframe.columns or 'amplitude' not in dataframe.columns:
            return
        # 
        # If no header, set default column names
        if header_line == -1:
            dataframe.columns = [f'C{i+1}' for i in range(dataframe.shape[1])]

        # Flip amplitude if needed
        if self.flipCSV_BrCv.isChecked():
            dataframe["amplitude"] = dataframe["amplitude"] * -1

        # Add additional information
        self.curve_origin = "measured"
        dataframe = addColumns(self, dataframe)
        
        # Update the combo boxes for x and y axis selection
        self.plotXAxis_BrCv.clear()
        self.plotYAxis_BrCv.clear()
        self.plotXAxis_BrCv.addItems(dataframe.columns)
        self.plotYAxis_BrCv.addItems(dataframe.columns)

        if hasattr(self, 'lower_bound'):
            del self.lower_bound
        if hasattr(self, 'upper_bound'):
            del self.upper_bound

        # Display the data in the QTableWidget
        loadTable(self,dataframe, header_line)
    except pd.errors.ParserError as e:
        print(f"Error parsing CSV file: {e}")
        # Handle the error, e.g., by logging or showing a message to the user


def addColumns(self, dataframe):

    # Remove trailing rows with only zero amplitude
    # dataframe = dataframe[dataframe.loc[::-1, 'amplitude'].ne(0).cummax()]

    # Interpolate amplitude values equal to 0
    if self.curve_origin == "measured":
        dataframe.loc[dataframe["amplitude"] == 0, "amplitude"] = np.nan
        dataframe["amplitude"] = dataframe["amplitude"].interpolate(method='linear', limit_direction='forward')

    # Add column with time in seconds
    dataframe["time"] = pd.to_timedelta(dataframe["timestamp"], unit=self.timeUnitCSV_BrCv.currentText())
    dataframe["time"] = dataframe["time"].dt.total_seconds()
    time_step = dataframe.loc[1, "time"] - dataframe.loc[0, "time"]

    # Add local maxima and minima
    if "mark" in dataframe.columns and self.curve_origin == "measured":
        idxs = dataframe[dataframe["mark"] == "Z"].index

        for i in range(len(idxs)-1):
            min_idx = dataframe.loc[idxs[i]:idxs[i+1], "amplitude"].idxmin()
            dataframe.loc[min_idx, "mark"] = "P_min"
            dataframe.loc[idxs[i+1]-1, "mark"] = "E"

    # Calculate speed and acceleration
    dataframe = calcGrad(self, dataframe)

    # If phase information in the CSV/VXP file create separate id per cycle
    # (instance already created in createCv function)
    if "phase" in dataframe.columns and "instance" not in dataframe.columns:
        dataframe["instance"] = 0

        for i in range(1, len(dataframe)):
            if dataframe.loc[i, "phase"] < dataframe.loc[i-1, "phase"]:
                dataframe.loc[i, "instance"] = dataframe.loc[i-1, "instance"] + 1
            else:
                dataframe.loc[i, "instance"] = dataframe.loc[i-1, "instance"]

    if "instance" in dataframe.columns:
        dataframe["cycle time"] = 0
        for i in range(1, len(dataframe)):
            if dataframe.loc[i, "instance"] > dataframe.loc[i-1, "instance"]:
                dataframe.loc[i, "cycle time"] = 0
            else:
                dataframe.loc[i, "cycle time"] = dataframe.loc[i-1, "cycle time"] + time_step

    return dataframe


def loadTable(self, dataframe, header_line):
    # Clear the table before populating it
    self.tableViewCSV_BrCv.clear()
    self.tableViewCSV_BrCv.setRowCount(dataframe.shape[0])
    self.tableViewCSV_BrCv.setColumnCount(dataframe.shape[1])

    # Set table headers
    if header_line >= 0:
        self.tableViewCSV_BrCv.setHorizontalHeaderLabels(dataframe.columns)
    else:
        self.tableViewCSV_BrCv.setHorizontalHeaderLabels([f'C{i+1}' for i in range(dataframe.shape[1])])

    # Populate the table with data
    for row in range(dataframe.shape[0]):
        for col in range(dataframe.shape[1]):
            self.tableViewCSV_BrCv.setItem(row, col, QTableWidgetItem(str(dataframe.iat[row, col])))
            
    if hasattr(self, "dfEdit_BrCv"):
        delattr(self, "dfEdit_BrCv")
        
    self.BrCvTab_index = 0


def calcGrad(self, df):
    # Convert the time column to TimedeltaIndex for resampling

    col = "amplitude"
    # Calculate average speed
    vel = df[col].diff().shift(-1) / df["time"].diff().shift(-1)
    vel.iloc[-1] = vel.iloc[-2]  # Copy the second last value to the last element
    df['velocity'] = vel

    speed = abs(vel) * 60  # Convert m/s to mm/min
    df['speed'] = speed

    # Calculate acceleration
    accel = vel.diff(-1) / df["time"].diff(-1)
    accel.iloc[-1] = accel.iloc[-2]  # Copy the second last value to the last element
    df['accel'] = accel

    return df


def setParams(self):
    num_cycles = self.createCvNumCycl.value()
    amplitude = self.createCvAmpl.value()
    cycle_time = self.createCvCyclTime.value()

    self.tableViewEditParams.clear()
    self.tableViewEditParams.setRowCount(num_cycles)
    self.tableViewEditParams.setColumnCount(2)

    # Set table headers
    self.tableViewEditParams.setHorizontalHeaderLabels(['amplitude', 'cycle time'])

    # Populate the table with data
    for row in range(num_cycles):
        self.tableViewEditParams.setItem(row, 0, QTableWidgetItem(str(amplitude)))
        self.tableViewEditParams.setItem(row, 1, QTableWidgetItem(str(cycle_time)))


def createCurve(self):
    cv_type = self.cvType.currentText()
    num_cycles = self.createCvNumCycl.value()
    freq = self.createCvFreq.value()

    step = 1e3 / freq      # ms

    for row in range(num_cycles):
        amplitude = float(self.tableViewEditParams.item(row, 0).text()) #* np.random.uniform(0.9, 1.1)
        cycle_time_s = float(self.tableViewEditParams.item(row, 1).text()) #* np.random.uniform(0.9, 1.1)
        num_steps = int((cycle_time_s * 1e3) // step)
        cycle_time_ms = int((num_steps - 1) * step)
        cycle_time_s = cycle_time_ms / 1e3

        t = np.linspace(0, cycle_time_ms, num_steps)
        x = t / 1e3

        if cv_type == "Cosine^2":
            y = amplitude * np.sin(x * np.pi / cycle_time_s) ** 2
        elif cv_type == "Cosine^4":
            y = amplitude * np.sin(x * np.pi / cycle_time_s) ** 4
        elif cv_type == "Cosine^6":
            y = amplitude * np.sin(x * np.pi / cycle_time_s) ** 6

        if row == 0:
            timestamps = t
        else:
            timestamps = t + dataframe.loc[len(dataframe)-1, "timestamp"] + step

        df_cycle = pd.DataFrame({"timestamp": timestamps, "amplitude": y})
        df_cycle["instance"] = row
        df_cycle["mark"] = np.nan
        df_cycle.loc[df_cycle["amplitude"].idxmax(), "mark"] = "Z"
        df_cycle.loc[0, "mark"] = "P_min"
        df_cycle.loc[len(df_cycle)-1, "mark"] = "E"

        if row == 0:
            dataframe = df_cycle.copy()
        else:
            dataframe = pd.concat([dataframe, df_cycle], ignore_index=True)

    self.curve_origin = "created"
    dataframe = addColumns(self, dataframe)
    
    # Update the combo boxes for x and y axis selection
    self.plotXAxis_BrCv.clear()
    self.plotYAxis_BrCv.clear()
    self.plotXAxis_BrCv.addItems(dataframe.columns)
    self.plotYAxis_BrCv.addItems(dataframe.columns)

    if hasattr(self, 'lower_bound'):
        del self.lower_bound
    if hasattr(self, 'upper_bound'):
        del self.upper_bound

    self.textViewCSV_BrCv.clear()
    loadTable(self, dataframe, 4)

