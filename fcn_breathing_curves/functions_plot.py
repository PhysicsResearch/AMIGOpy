import os
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QVBoxLayout, QTableWidgetItem, QFileDialog


def getColumnIndexByName(self, column_name):
    for i in range(self.tableViewCSV_BrCv.columnCount()):
        if self.tableViewCSV_BrCv.horizontalHeaderItem(i).text() == column_name:
            return i
    return None


def getDataframeFromTable(self):
    """Extract data from tableWidget and convert to pandas.DataFrame"""
    x_col = self.editXAxis_BrCv.currentText()
    y_col = "amplitude"

    # Get column indices based on selected column names
    x_index = getColumnIndexByName(self, x_col)
    y_index = getColumnIndexByName(self, y_col)
    
    if x_index is None or y_index is None:
        return
    
    cols = [x_index, y_index]
    extra_cols = ["time", "cycle time", "phase", "velocity", "instance"]
    for col in range(self.tableViewCSV_BrCv.columnCount()):
        if self.tableViewCSV_BrCv.horizontalHeaderItem(col).text() in extra_cols:
            cols.append(col)
        
    # Extract data from the table widget
    data = {}
    for col in cols:
        column_name = self.tableViewCSV_BrCv.horizontalHeaderItem(col).text()
        data[column_name] = []
        for row in range(0, self.tableViewCSV_BrCv.rowCount()):
            item = self.tableViewCSV_BrCv.item(row, col)
            if item:
                data[column_name].append(float(item.text()))

    self.dfEdit_BrCv = pd.DataFrame(data)


def init_BrCv_plot(self):
    if self.tabWidget_BrCv.currentIndex() == 2:
        try:
            if not hasattr(self, "dfEdit_BrCv"):
                getDataframeFromTable(self)
            self.plotXAxis_BrCv.setCurrentText("timestamp")
            self.plotYAxis_BrCv.setCurrentText("amplitude")
        
            plotViewData_BrCv_plot(self)   
        except:
            return
           

def addColumns(self, dataframe):
    # If phase information in the CSV/VXP file create separate id per cycle
    # (instance already created in createCv function)
    if "instance" in dataframe.columns:
        time_step = dataframe.loc[1, "time"] - dataframe.loc[0, "time"]
        dataframe["cycle time"] = 0
        for i in range(1, len(dataframe)):
            if dataframe.loc[i, "instance"] > dataframe.loc[i-1, "instance"]:
                dataframe.loc[i, "cycle time"] = 0
            else:
                dataframe.loc[i, "cycle time"] = dataframe.loc[i-1, "cycle time"] + time_step
                
    dataframe = calcGrad(self, dataframe)

    return dataframe


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


def plotViewData_BrCv_plot(self):
    x_col = self.plotXAxis_BrCv.currentText()
    y_col = self.plotYAxis_BrCv.currentText()

    if not x_col or not y_col:
        return  # Ensure columns are selected

    i_index = None
    for col in range(self.tableViewCSV_BrCv.columnCount()):
        if self.tableViewCSV_BrCv.horizontalHeaderItem(col).text() == "instance":
            i_index = col

    df = self.dfEdit_BrCv
    df = addColumns(self, df) 
    
    if x_col in ["timestamp", "time", "velocity"] and y_col == "amplitude":
        x_data = df[x_col]
        y_data = df[y_col]
    elif x_col in ["phase", "cycle time"] and y_col == "amplitude" and i_index is not None:
        g = df.groupby('instance').cumcount()
        x_data = (df.set_index(['instance', g])
                 .unstack(fill_value=np.nan)
                 .stack().groupby(level=0)[x_col]
                 .apply(lambda x: x.values.tolist())
                 .tolist())
        y_data = (df.set_index(['instance', g])
                 .unstack(fill_value=np.nan)
                 .stack().groupby(level=0)[y_col]
                 .apply(lambda x: x.values.tolist())
                 .tolist())
    else:
        return

    self.plot_fig = Figure()  # Create a figure for the first time
    ax = self.plot_fig.add_subplot(111) 
    
    if self.selected_background == "Transparent":
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
    else:
        ax.tick_params(labelsize=self.selected_font_size-2)  # White ticks with larger text

    # Plot the data
    if x_col in ["timestamp", "time", "velocity"] and y_col == "amplitude":
        ax.set_xlim(np.min(x_data), np.max(x_data))
        ax.plot(x_data, y_data, label=f'{x_col} vs {y_col}')

    elif x_col in ["phase", "cycle time"] and y_col == "amplitude" and i_index is not None:
        ax.set_xlim(np.min([x for xs in x_data for x in xs]),
                    np.max([x for xs in x_data for x in xs]))
        for x, y in zip(x_data, y_data):
            ax.plot(x, y)

    from PyQt5 import QtWidgets
    self.plotPeaksBrCv = QtWidgets.QCheckBox(self.smoothing_BrCv)
    self.plotPeaksBrCv.setChecked(False)
    self.plotPeaksBrCv.setObjectName("plotPeaksBrCv")
    if 'mark' in self.dfEdit_BrCv.columns and self.plotXAxis_BrCv.currentText() in ['timestamp', 'time'] \
        and self.plotPeaksBrCv.isChecked():
        time_col = self.plotXAxis_BrCv.currentText()
        z_marks = self.dfEdit_BrCv.loc[self.dfEdit_BrCv['mark'] == 'Z']
        ax.scatter(z_marks[time_col], z_marks['amplitude'],
                color='#bc80bd', marker='*', s=25, label='Peak')
        ax.vlines(z_marks[time_col], ymin=0, ymax=z_marks['amplitude'],
                colors='#bc80bd', linewidth=1.5)

    # Set x_col as xlabel
    if x_col == 'time':
        ax.set_xlabel('Time (s)', fontsize=self.selected_font_size)
    elif x_col == 'timestamp':
        ax.set_xlabel('Time (ms)', fontsize=self.selected_font_size)
    else:
        ax.set_xlabel(x_col, fontsize=self.selected_font_size)

    # Set y_col as ylabel
    if y_col == 'amplitude':
        ax.set_ylabel('Amplitude (mm)', fontsize=self.selected_font_size)
    else:
        ax.set_ylabel(y_col, fontsize=self.selected_font_size)
        
    if self.selected_background == "Transparent":
        ax.set_title(f"{x_col} vs {y_col}", 
                               fontsize=self.selected_font_size + 4,
                               color="white")
    else:
        ax.set_title(f"{x_col} vs {y_col}", 
                               fontsize=self.selected_font_size + 4)
    
    if self.selected_legend_on_off == "On":
        if self.selected_background == "Transparent":
            ax.legend(edgecolor='white')
        else:
            ax.legend()
        

    # Create a canvas and toolbar
    canvas = FigureCanvas(self.plot_fig)
    canvas.setStyleSheet(f"background-color:{self.selected_background};")
    toolbar = NavigationToolbar(canvas, self)

    # Check if the container has a layout, set one if not
    container = self.plotAxView_BrCv
    if container.layout() is None:
        layout = QVBoxLayout(container)
        container.setLayout(layout)
    else:
        # Clear existing content in the container, if any
        while container.layout().count():
            child = container.layout().takeAt(0)
            if child.widget() and not isinstance(child.widget(), NavigationToolbar):
                child.widget().deleteLater()

    # Add the canvas and toolbar to the container
    container.layout().addWidget(toolbar)
    container.layout().addWidget(canvas)
    canvas.draw()
    
    
def exportPlot(self):
        options = QFileDialog.Options()
        folder = QFileDialog.getExistingDirectory(self, options=options)
        fileName = os.path.join(folder, self.BrCv_exportPlotTitle.text()+".png")
        self.plot_fig.savefig(fileName, dpi=300, bbox_inches="tight")


def calcStats(self):

    data = {}
    cols = ["timestamp", "amplitude", "instance", "speed", "cycle time"]
    for col in range(self.tableViewCSV_BrCv.columnCount()):
        column_name = self.tableViewCSV_BrCv.horizontalHeaderItem(col).text()
        if column_name in cols:
            data[column_name] = []
            for row in range(self.tableViewCSV_BrCv.rowCount()):
                item = self.tableViewCSV_BrCv.item(row, col)
                if item:
                    data[column_name].append(float(item.text()))

    # Convert data to DataFrame
    df = pd.DataFrame(data)

    for var in ["amplitude", "cycle time", "speed"]:
        if var not in df.columns:
            continue
        if "instance" in df.columns:
            stats = {}
            stats["min"] = df.groupby("instance").max()[var].min()
            stats["max"] = df.groupby("instance").max()[var].max()
            stats["mean"] = df.groupby("instance").max()[var].mean()
            stats["std"] = df.groupby("instance").max()[var].std()
            stats["median"] = df.groupby("instance").max()[var].median()
            Q1 = df.groupby("instance").max()[var].quantile(0.25)
            Q3 = df.groupby("instance").max()[var].quantile(0.75)
            stats["iqr"] = Q3 - Q1

        elif "instance" not in df.columns and var in ["amplitude", "speed"]:
            stats = {}
            stats["max"] = df[var].max()

        if var == "amplitude":
            self.tableViewAmplStats.clear()
            self.tableViewAmplStats.setColumnCount(1)
            self.tableViewAmplStats.setHorizontalHeaderLabels(['amplitude'])
            self.tableViewAmplStats.setRowCount(len(stats))
            self.tableViewAmplStats.setVerticalHeaderLabels(list(stats.keys()))
            for i, metric in enumerate(stats):
                self.tableViewAmplStats.setItem(i, 0, QTableWidgetItem("{:.4f}".format(stats[metric])))

        elif var == "cycle time":
            self.tableViewCyclStats.clear()
            self.tableViewCyclStats.setColumnCount(1)
            self.tableViewCyclStats.setHorizontalHeaderLabels(['cycle time'])
            self.tableViewCyclStats.setRowCount(len(stats))
            self.tableViewCyclStats.setVerticalHeaderLabels(list(stats.keys()))

            for i, metric in enumerate(stats):
                self.tableViewCyclStats.setItem(i, 0, QTableWidgetItem("{:.4f}".format(stats[metric])))

        elif var == "speed":
            self.tableViewSpeedStats.clear()
            self.tableViewSpeedStats.setColumnCount(1)
            self.tableViewSpeedStats.setHorizontalHeaderLabels(['speed'])
            self.tableViewSpeedStats.setRowCount(len(stats))
            self.tableViewSpeedStats.setVerticalHeaderLabels(list(stats.keys()))

            for i, metric in enumerate(stats):
                self.tableViewSpeedStats.setItem(i, 0, QTableWidgetItem("{:.4f}".format(stats[metric])))
