# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ImGUI.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame, QGraphicsView, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLCDNumber, QLabel,
    QLayout, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy,
    QSlider, QSpacerItem, QSpinBox, QStatusBar,
    QTabWidget, QTableWidget, QTableWidgetItem, QTextEdit,
    QToolBox, QToolButton, QTreeView, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget)

class Ui_AMIGOpy(object):
    def setupUi(self, AMIGOpy):
        if not AMIGOpy.objectName():
            AMIGOpy.setObjectName(u"AMIGOpy")
        AMIGOpy.resize(1731, 1156)
        AMIGOpy.setAutoFillBackground(False)
        AMIGOpy.setInputMethodHints(Qt.InputMethodHint.ImhNone)
        self.centralwidget = QWidget(AMIGOpy)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_3 = QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_3.addWidget(self.line, 6, 1, 1, 2)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.gridLayout_3.addWidget(self.label, 8, 1, 1, 2)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)

        self.gridLayout_3.addWidget(self.progressBar, 8, 0, 1, 1)

        self.line1 = QFrame(self.centralwidget)
        self.line1.setObjectName(u"line1")
        self.line1.setFrameShape(QFrame.Shape.HLine)
        self.line1.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_3.addWidget(self.line1, 6, 1, 1, 2)

        self.gridLayout_50 = QGridLayout()
        self.gridLayout_50.setObjectName(u"gridLayout_50")

        self.gridLayout_3.addLayout(self.gridLayout_50, 5, 0, 2, 1)

        self.tabModules = QTabWidget(self.centralwidget)
        self.tabModules.setObjectName(u"tabModules")
        self.im_display_tab = QWidget()
        self.im_display_tab.setObjectName(u"im_display_tab")
        self.gridLayout_4 = QGridLayout(self.im_display_tab)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.SagittalSlider = QSlider(self.im_display_tab)
        self.SagittalSlider.setObjectName(u"SagittalSlider")
        self.SagittalSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_4.addWidget(self.SagittalSlider, 1, 1, 1, 1)

        self.AxialSlider = QSlider(self.im_display_tab)
        self.AxialSlider.setObjectName(u"AxialSlider")
        self.AxialSlider.setSingleStep(25)
        self.AxialSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_4.addWidget(self.AxialSlider, 1, 0, 1, 1)

        self.VTK_view_03 = QWidget(self.im_display_tab)
        self.VTK_view_03.setObjectName(u"VTK_view_03")

        self.gridLayout_4.addWidget(self.VTK_view_03, 2, 0, 1, 1)

        self.CoronalSlider = QSlider(self.im_display_tab)
        self.CoronalSlider.setObjectName(u"CoronalSlider")
        self.CoronalSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_4.addWidget(self.CoronalSlider, 5, 0, 1, 1)

        self.VTK_view_02 = QWidget(self.im_display_tab)
        self.VTK_view_02.setObjectName(u"VTK_view_02")

        self.gridLayout_4.addWidget(self.VTK_view_02, 0, 1, 1, 1)

        self.VTK_view_01 = QWidget(self.im_display_tab)
        self.VTK_view_01.setObjectName(u"VTK_view_01")

        self.gridLayout_4.addWidget(self.VTK_view_01, 0, 0, 1, 1)

        self.label_2 = QLabel(self.im_display_tab)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_4.addWidget(self.label_2, 5, 1, 1, 1)

        self.tabView01 = QTabWidget(self.im_display_tab)
        self.tabView01.setObjectName(u"tabView01")
        font = QFont()
        font.setPointSize(10)
        self.tabView01.setFont(font)
        self.tab_5 = QWidget()
        self.tab_5.setObjectName(u"tab_5")
        self.verticalLayout = QVBoxLayout(self.tab_5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget_6 = QTabWidget(self.tab_5)
        self.tabWidget_6.setObjectName(u"tabWidget_6")
        self.tab_18 = QWidget()
        self.tab_18.setObjectName(u"tab_18")
        self.gridLayout_15 = QGridLayout(self.tab_18)
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.hist_container_01 = QWidget(self.tab_18)
        self.hist_container_01.setObjectName(u"hist_container_01")

        self.gridLayout_15.addWidget(self.hist_container_01, 0, 0, 1, 2)

        self.tabWidget_6.addTab(self.tab_18, "")
        self.tab_19 = QWidget()
        self.tab_19.setObjectName(u"tab_19")
        self.tabWidget_6.addTab(self.tab_19, "")

        self.verticalLayout.addWidget(self.tabWidget_6)

        self.tabView01.addTab(self.tab_5, "")
        self.tab_6 = QWidget()
        self.tab_6.setObjectName(u"tab_6")
        self.tabView01.addTab(self.tab_6, "")
        self.tab_14 = QWidget()
        self.tab_14.setObjectName(u"tab_14")
        self.gridLayout_44 = QGridLayout(self.tab_14)
        self.gridLayout_44.setObjectName(u"gridLayout_44")
        self.tabWidget_3 = QTabWidget(self.tab_14)
        self.tabWidget_3.setObjectName(u"tabWidget_3")
        self.tab_37 = QWidget()
        self.tab_37.setObjectName(u"tab_37")
        self.gridLayout_45 = QGridLayout(self.tab_37)
        self.gridLayout_45.setObjectName(u"gridLayout_45")
        self.horizontalSpacer_46 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_45.addItem(self.horizontalSpacer_46, 2, 2, 1, 1)

        self.display_brachy_channel_overlay = QCheckBox(self.tab_37)
        self.display_brachy_channel_overlay.setObjectName(u"display_brachy_channel_overlay")

        self.gridLayout_45.addWidget(self.display_brachy_channel_overlay, 1, 4, 1, 1)

        self.overlay_all_channels = QCheckBox(self.tab_37)
        self.overlay_all_channels.setObjectName(u"overlay_all_channels")
        self.overlay_all_channels.setChecked(True)

        self.gridLayout_45.addWidget(self.overlay_all_channels, 1, 5, 1, 1)

        self.display_dw_overlay = QCheckBox(self.tab_37)
        self.display_dw_overlay.setObjectName(u"display_dw_overlay")

        self.gridLayout_45.addWidget(self.display_dw_overlay, 1, 3, 1, 1)

        self.lineEdit_63 = QLineEdit(self.tab_37)
        self.lineEdit_63.setObjectName(u"lineEdit_63")
        self.lineEdit_63.setEnabled(False)
        self.lineEdit_63.setFont(font)

        self.gridLayout_45.addWidget(self.lineEdit_63, 2, 0, 1, 1)

        self.brachy_combobox_01 = QComboBox(self.tab_37)
        self.brachy_combobox_01.setObjectName(u"brachy_combobox_01")

        self.gridLayout_45.addWidget(self.brachy_combobox_01, 1, 0, 1, 1)

        self.brachy_table_01 = QTableWidget(self.tab_37)
        self.brachy_table_01.setObjectName(u"brachy_table_01")
        font1 = QFont()
        font1.setPointSize(12)
        self.brachy_table_01.setFont(font1)

        self.gridLayout_45.addWidget(self.brachy_table_01, 0, 0, 1, 6)

        self.brachy_export_dw_channels_csv = QPushButton(self.tab_37)
        self.brachy_export_dw_channels_csv.setObjectName(u"brachy_export_dw_channels_csv")

        self.gridLayout_45.addWidget(self.brachy_export_dw_channels_csv, 2, 5, 1, 1)

        self.brachy_spinBox_01 = QSpinBox(self.tab_37)
        self.brachy_spinBox_01.setObjectName(u"brachy_spinBox_01")
        self.brachy_spinBox_01.setFont(font)

        self.gridLayout_45.addWidget(self.brachy_spinBox_01, 1, 1, 1, 1)

        self.horizontalSpacer_45 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_45.addItem(self.horizontalSpacer_45, 2, 3, 1, 2)

        self.dw_ch_point_size = QSpinBox(self.tab_37)
        self.dw_ch_point_size.setObjectName(u"dw_ch_point_size")
        self.dw_ch_point_size.setFont(font)
        self.dw_ch_point_size.setValue(3)

        self.gridLayout_45.addWidget(self.dw_ch_point_size, 2, 1, 1, 1)

        self.tabWidget_3.addTab(self.tab_37, "")
        self.tab_38 = QWidget()
        self.tab_38.setObjectName(u"tab_38")
        self.tabWidget_3.addTab(self.tab_38, "")

        self.gridLayout_44.addWidget(self.tabWidget_3, 0, 0, 1, 1)

        self.tabView01.addTab(self.tab_14, "")
        self.tab_39 = QWidget()
        self.tab_39.setObjectName(u"tab_39")
        self.gridLayout_47 = QGridLayout(self.tab_39)
        self.gridLayout_47.setObjectName(u"gridLayout_47")
        self.STRUCTlist = QListWidget(self.tab_39)
        self.STRUCTlist.setObjectName(u"STRUCTlist")

        self.gridLayout_47.addWidget(self.STRUCTlist, 0, 0, 1, 4)

        self.CreateMask_Structures = QPushButton(self.tab_39)
        self.CreateMask_Structures.setObjectName(u"CreateMask_Structures")

        self.gridLayout_47.addWidget(self.CreateMask_Structures, 1, 3, 1, 1)

        self.lineEdit_66 = QLineEdit(self.tab_39)
        self.lineEdit_66.setObjectName(u"lineEdit_66")
        self.lineEdit_66.setEnabled(False)
        self.lineEdit_66.setFont(font)

        self.gridLayout_47.addWidget(self.lineEdit_66, 1, 0, 1, 1)

        self.StructRefSeries = QLineEdit(self.tab_39)
        self.StructRefSeries.setObjectName(u"StructRefSeries")
        self.StructRefSeries.setFont(font)

        self.gridLayout_47.addWidget(self.StructRefSeries, 1, 1, 1, 2)

        self.horizontalSpacer_80 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_47.addItem(self.horizontalSpacer_80, 2, 1, 1, 1)

        self.tabView01.addTab(self.tab_39, "")
        self.tab_9 = QWidget()
        self.tab_9.setObjectName(u"tab_9")
        self.gridLayout_7 = QGridLayout(self.tab_9)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.tabWidget_4 = QTabWidget(self.tab_9)
        self.tabWidget_4.setObjectName(u"tabWidget_4")
        self.tab_10 = QWidget()
        self.tab_10.setObjectName(u"tab_10")
        self.gridLayout_8 = QGridLayout(self.tab_10)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.IrIS_CorFrame_checkbox = QCheckBox(self.tab_10)
        self.IrIS_CorFrame_checkbox.setObjectName(u"IrIS_CorFrame_checkbox")

        self.gridLayout_8.addWidget(self.IrIS_CorFrame_checkbox, 2, 0, 1, 1)

        self.line_18 = QFrame(self.tab_10)
        self.line_18.setObjectName(u"line_18")
        self.line_18.setFrameShape(QFrame.Shape.HLine)
        self.line_18.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_8.addWidget(self.line_18, 3, 0, 1, 5)

        self.line_19 = QFrame(self.tab_10)
        self.line_19.setObjectName(u"line_19")
        self.line_19.setFrameShape(QFrame.Shape.HLine)
        self.line_19.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_8.addWidget(self.line_19, 5, 0, 1, 5)

        self.lineEdit_39 = QLineEdit(self.tab_10)
        self.lineEdit_39.setObjectName(u"lineEdit_39")
        self.lineEdit_39.setEnabled(False)

        self.gridLayout_8.addWidget(self.lineEdit_39, 4, 2, 1, 2)

        self.Skip_IrIS_Files = QSpinBox(self.tab_10)
        self.Skip_IrIS_Files.setObjectName(u"Skip_IrIS_Files")

        self.gridLayout_8.addWidget(self.Skip_IrIS_Files, 9, 0, 1, 1)

        self.Load_IrIS_Files = QSpinBox(self.tab_10)
        self.Load_IrIS_Files.setObjectName(u"Load_IrIS_Files")
        self.Load_IrIS_Files.setMaximum(999999999)

        self.gridLayout_8.addWidget(self.Load_IrIS_Files, 9, 2, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_8.addItem(self.verticalSpacer_3, 7, 0, 1, 1)

        self.IrIS_DownSample = QSpinBox(self.tab_10)
        self.IrIS_DownSample.setObjectName(u"IrIS_DownSample")
        self.IrIS_DownSample.setMinimum(1)

        self.gridLayout_8.addWidget(self.IrIS_DownSample, 4, 4, 1, 1)

        self.IrIS_Offset_checkbox = QCheckBox(self.tab_10)
        self.IrIS_Offset_checkbox.setObjectName(u"IrIS_Offset_checkbox")

        self.gridLayout_8.addWidget(self.IrIS_Offset_checkbox, 0, 0, 1, 1)

        self.IrIS_parallel_proc_box = QCheckBox(self.tab_10)
        self.IrIS_parallel_proc_box.setObjectName(u"IrIS_parallel_proc_box")

        self.gridLayout_8.addWidget(self.IrIS_parallel_proc_box, 6, 0, 1, 1)

        self.lineEdit_6 = QLineEdit(self.tab_10)
        self.lineEdit_6.setObjectName(u"lineEdit_6")

        self.gridLayout_8.addWidget(self.lineEdit_6, 8, 0, 1, 1)

        self.IrIS_Sens_checkbox = QCheckBox(self.tab_10)
        self.IrIS_Sens_checkbox.setObjectName(u"IrIS_Sens_checkbox")

        self.gridLayout_8.addWidget(self.IrIS_Sens_checkbox, 1, 0, 1, 1)

        self.lineEdit_7 = QLineEdit(self.tab_10)
        self.lineEdit_7.setObjectName(u"lineEdit_7")

        self.gridLayout_8.addWidget(self.lineEdit_7, 8, 2, 1, 1)

        self.checkBox_4 = QCheckBox(self.tab_10)
        self.checkBox_4.setObjectName(u"checkBox_4")
        self.checkBox_4.setChecked(True)

        self.gridLayout_8.addWidget(self.checkBox_4, 4, 0, 1, 1)

        self.IrIS_CorrFrame_oper = QComboBox(self.tab_10)
        self.IrIS_CorrFrame_oper.setObjectName(u"IrIS_CorrFrame_oper")

        self.gridLayout_8.addWidget(self.IrIS_CorrFrame_oper, 2, 1, 1, 1)

        self.IrIS_Load_CorrectionFrame = QPushButton(self.tab_10)
        self.IrIS_Load_CorrectionFrame.setObjectName(u"IrIS_Load_CorrectionFrame")

        self.gridLayout_8.addWidget(self.IrIS_Load_CorrectionFrame, 2, 2, 1, 3)

        self.IrIS_Load_SensMap = QPushButton(self.tab_10)
        self.IrIS_Load_SensMap.setObjectName(u"IrIS_Load_SensMap")

        self.gridLayout_8.addWidget(self.IrIS_Load_SensMap, 1, 2, 1, 3)

        self.IrIS_Load_Offset = QPushButton(self.tab_10)
        self.IrIS_Load_Offset.setObjectName(u"IrIS_Load_Offset")

        self.gridLayout_8.addWidget(self.IrIS_Load_Offset, 0, 2, 1, 3)

        self.tabWidget_4.addTab(self.tab_10, "")
        self.tab_11 = QWidget()
        self.tab_11.setObjectName(u"tab_11")
        self.tabWidget_4.addTab(self.tab_11, "")
        self.tab_12 = QWidget()
        self.tab_12.setObjectName(u"tab_12")
        self.tabWidget_4.addTab(self.tab_12, "")

        self.gridLayout_7.addWidget(self.tabWidget_4, 0, 0, 1, 1)

        self.tabView01.addTab(self.tab_9, "")
        self.tab_13 = QWidget()
        self.tab_13.setObjectName(u"tab_13")
        self.gridLayout_9 = QGridLayout(self.tab_13)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.lineEdit_64 = QLineEdit(self.tab_13)
        self.lineEdit_64.setObjectName(u"lineEdit_64")
        self.lineEdit_64.setEnabled(False)
        self.lineEdit_64.setFont(font)

        self.gridLayout_9.addWidget(self.lineEdit_64, 1, 0, 1, 1)

        self.metadata_search = QLineEdit(self.tab_13)
        self.metadata_search.setObjectName(u"metadata_search")
        self.metadata_search.setFont(font)

        self.gridLayout_9.addWidget(self.metadata_search, 1, 1, 1, 1)

        self.MetaViewTable = QTreeWidget(self.tab_13)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.MetaViewTable.setHeaderItem(__qtreewidgetitem)
        self.MetaViewTable.setObjectName(u"MetaViewTable")

        self.gridLayout_9.addWidget(self.MetaViewTable, 0, 0, 1, 2)

        self.tabView01.addTab(self.tab_13, "")
        self.tab_17 = QWidget()
        self.tab_17.setObjectName(u"tab_17")
        self.gridLayout_12 = QGridLayout(self.tab_17)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.tabWidget_10 = QTabWidget(self.tab_17)
        self.tabWidget_10.setObjectName(u"tabWidget_10")
        self.tab_44 = QWidget()
        self.tab_44.setObjectName(u"tab_44")
        self.gridLayout_80 = QGridLayout(self.tab_44)
        self.gridLayout_80.setObjectName(u"gridLayout_80")
        self.run_im_process = QPushButton(self.tab_44)
        self.run_im_process.setObjectName(u"run_im_process")
        font2 = QFont()
        font2.setPointSize(10)
        font2.setBold(True)
        self.run_im_process.setFont(font2)

        self.gridLayout_80.addWidget(self.run_im_process, 0, 2, 1, 1)

        self.ImageUndo_operation = QPushButton(self.tab_44)
        self.ImageUndo_operation.setObjectName(u"ImageUndo_operation")
        self.ImageUndo_operation.setFont(font2)

        self.gridLayout_80.addWidget(self.ImageUndo_operation, 0, 3, 1, 1)

        self.Process_list = QComboBox(self.tab_44)
        self.Process_list.setObjectName(u"Process_list")

        self.gridLayout_80.addWidget(self.Process_list, 0, 0, 1, 2)

        self.pushButton_2 = QPushButton(self.tab_44)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.gridLayout_80.addWidget(self.pushButton_2, 0, 4, 1, 1)

        self.ProcessSetBox = QGroupBox(self.tab_44)
        self.ProcessSetBox.setObjectName(u"ProcessSetBox")
        self.ProcessSetBox.setEnabled(True)
        self.gridLayout_13 = QGridLayout(self.ProcessSetBox)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.Process_set_box2 = QComboBox(self.ProcessSetBox)
        self.Process_set_box2.setObjectName(u"Process_set_box2")

        self.gridLayout_13.addWidget(self.Process_set_box2, 5, 2, 1, 1)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_13.addItem(self.horizontalSpacer_9, 2, 3, 1, 1)

        self.Process_set_box3 = QComboBox(self.ProcessSetBox)
        self.Process_set_box3.setObjectName(u"Process_set_box3")

        self.gridLayout_13.addWidget(self.Process_set_box3, 5, 4, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_13.addItem(self.verticalSpacer_4, 6, 0, 1, 1)

        self.Proces_spinbox_05 = QDoubleSpinBox(self.ProcessSetBox)
        self.Proces_spinbox_05.setObjectName(u"Proces_spinbox_05")
        self.Proces_spinbox_05.setFont(font)
        self.Proces_spinbox_05.setMinimum(-1.000000000000000)
        self.Proces_spinbox_05.setMaximum(99999999.989999994635582)

        self.gridLayout_13.addWidget(self.Proces_spinbox_05, 4, 2, 1, 1)

        self.Proces_spinbox_02 = QDoubleSpinBox(self.ProcessSetBox)
        self.Proces_spinbox_02.setObjectName(u"Proces_spinbox_02")
        self.Proces_spinbox_02.setFont(font)
        self.Proces_spinbox_02.setMinimum(-1.000000000000000)
        self.Proces_spinbox_02.setMaximum(99999999.989999994635582)

        self.gridLayout_13.addWidget(self.Proces_spinbox_02, 2, 2, 1, 1)

        self.Proces_spinbox_06 = QDoubleSpinBox(self.ProcessSetBox)
        self.Proces_spinbox_06.setObjectName(u"Proces_spinbox_06")
        self.Proces_spinbox_06.setFont(font)
        self.Proces_spinbox_06.setMinimum(-1.000000000000000)
        self.Proces_spinbox_06.setMaximum(999999999.990000009536743)

        self.gridLayout_13.addWidget(self.Proces_spinbox_06, 4, 4, 1, 1)

        self.Process_DataType_box = QComboBox(self.ProcessSetBox)
        self.Process_DataType_box.setObjectName(u"Process_DataType_box")

        self.gridLayout_13.addWidget(self.Process_DataType_box, 7, 0, 1, 1)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_13.addItem(self.horizontalSpacer_7, 2, 1, 1, 1)

        self.Proces_label_01 = QLineEdit(self.ProcessSetBox)
        self.Proces_label_01.setObjectName(u"Proces_label_01")
        self.Proces_label_01.setEnabled(False)
        self.Proces_label_01.setFont(font)

        self.gridLayout_13.addWidget(self.Proces_label_01, 0, 0, 1, 1)

        self.Proces_spinbox_01 = QDoubleSpinBox(self.ProcessSetBox)
        self.Proces_spinbox_01.setObjectName(u"Proces_spinbox_01")
        self.Proces_spinbox_01.setFont(font)
        self.Proces_spinbox_01.setMinimum(-1.000000000000000)
        self.Proces_spinbox_01.setMaximum(99999999999.990005493164063)

        self.gridLayout_13.addWidget(self.Proces_spinbox_01, 2, 0, 1, 1)

        self.Process_set_box = QComboBox(self.ProcessSetBox)
        self.Process_set_box.setObjectName(u"Process_set_box")

        self.gridLayout_13.addWidget(self.Process_set_box, 5, 0, 1, 1)

        self.Proces_spinbox_04 = QDoubleSpinBox(self.ProcessSetBox)
        self.Proces_spinbox_04.setObjectName(u"Proces_spinbox_04")
        self.Proces_spinbox_04.setFont(font)
        self.Proces_spinbox_04.setMinimum(-1.000000000000000)
        self.Proces_spinbox_04.setMaximum(9999999999.989999771118164)

        self.gridLayout_13.addWidget(self.Proces_spinbox_04, 4, 0, 1, 1)

        self.Proces_spinbox_03 = QDoubleSpinBox(self.ProcessSetBox)
        self.Proces_spinbox_03.setObjectName(u"Proces_spinbox_03")
        self.Proces_spinbox_03.setFont(font)
        self.Proces_spinbox_03.setMinimum(-1.000000000000000)
        self.Proces_spinbox_03.setMaximum(999999999990000.000000000000000)

        self.gridLayout_13.addWidget(self.Proces_spinbox_03, 2, 4, 1, 1)

        self.Proces_label_06 = QLineEdit(self.ProcessSetBox)
        self.Proces_label_06.setObjectName(u"Proces_label_06")
        self.Proces_label_06.setEnabled(False)
        self.Proces_label_06.setFont(font)

        self.gridLayout_13.addWidget(self.Proces_label_06, 3, 4, 1, 1)

        self.Proces_label_05 = QLineEdit(self.ProcessSetBox)
        self.Proces_label_05.setObjectName(u"Proces_label_05")
        self.Proces_label_05.setEnabled(False)
        self.Proces_label_05.setFont(font)

        self.gridLayout_13.addWidget(self.Proces_label_05, 3, 2, 1, 1)

        self.Proces_label_02 = QLineEdit(self.ProcessSetBox)
        self.Proces_label_02.setObjectName(u"Proces_label_02")
        self.Proces_label_02.setEnabled(False)
        self.Proces_label_02.setFont(font)

        self.gridLayout_13.addWidget(self.Proces_label_02, 0, 2, 1, 1)

        self.Proces_label_03 = QLineEdit(self.ProcessSetBox)
        self.Proces_label_03.setObjectName(u"Proces_label_03")
        self.Proces_label_03.setEnabled(False)
        self.Proces_label_03.setFont(font)

        self.gridLayout_13.addWidget(self.Proces_label_03, 0, 4, 1, 1)

        self.Proces_label_04 = QLineEdit(self.ProcessSetBox)
        self.Proces_label_04.setObjectName(u"Proces_label_04")
        self.Proces_label_04.setEnabled(False)
        self.Proces_label_04.setFont(font)

        self.gridLayout_13.addWidget(self.Proces_label_04, 3, 0, 1, 1)


        self.gridLayout_80.addWidget(self.ProcessSetBox, 4, 0, 1, 5)

        self.tabWidget_10.addTab(self.tab_44, "")
        self.tab_45 = QWidget()
        self.tab_45.setObjectName(u"tab_45")
        self.gridLayout_81 = QGridLayout(self.tab_45)
        self.gridLayout_81.setObjectName(u"gridLayout_81")
        self.groupBox_13 = QGroupBox(self.tab_45)
        self.groupBox_13.setObjectName(u"groupBox_13")
        self.gridLayout_83 = QGridLayout(self.groupBox_13)
        self.gridLayout_83.setObjectName(u"gridLayout_83")
        self.lineEdit_73 = QLineEdit(self.groupBox_13)
        self.lineEdit_73.setObjectName(u"lineEdit_73")
        self.lineEdit_73.setEnabled(False)

        self.gridLayout_83.addWidget(self.lineEdit_73, 0, 1, 1, 1)

        self.Reg_manual_Rot_X = QDoubleSpinBox(self.groupBox_13)
        self.Reg_manual_Rot_X.setObjectName(u"Reg_manual_Rot_X")

        self.gridLayout_83.addWidget(self.Reg_manual_Rot_X, 1, 1, 1, 1)

        self.Reg_manual_Rot_Y = QDoubleSpinBox(self.groupBox_13)
        self.Reg_manual_Rot_Y.setObjectName(u"Reg_manual_Rot_Y")

        self.gridLayout_83.addWidget(self.Reg_manual_Rot_Y, 2, 1, 1, 1)

        self.Reg_manual_Rot_Z = QDoubleSpinBox(self.groupBox_13)
        self.Reg_manual_Rot_Z.setObjectName(u"Reg_manual_Rot_Z")

        self.gridLayout_83.addWidget(self.Reg_manual_Rot_Z, 3, 1, 1, 1)


        self.gridLayout_81.addWidget(self.groupBox_13, 0, 2, 1, 1)

        self.groupBox_15 = QGroupBox(self.tab_45)
        self.groupBox_15.setObjectName(u"groupBox_15")
        self.gridLayout_85 = QGridLayout(self.groupBox_15)
        self.gridLayout_85.setObjectName(u"gridLayout_85")
        self.lineEdit_88 = QLineEdit(self.groupBox_15)
        self.lineEdit_88.setObjectName(u"lineEdit_88")
        self.lineEdit_88.setEnabled(False)

        self.gridLayout_85.addWidget(self.lineEdit_88, 0, 0, 1, 1)

        self.doubleSpinBox = QDoubleSpinBox(self.groupBox_15)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setEnabled(False)

        self.gridLayout_85.addWidget(self.doubleSpinBox, 0, 1, 1, 1)

        self.doubleSpinBox_2 = QDoubleSpinBox(self.groupBox_15)
        self.doubleSpinBox_2.setObjectName(u"doubleSpinBox_2")
        self.doubleSpinBox_2.setEnabled(False)

        self.gridLayout_85.addWidget(self.doubleSpinBox_2, 0, 2, 1, 1)

        self.doubleSpinBox_3 = QDoubleSpinBox(self.groupBox_15)
        self.doubleSpinBox_3.setObjectName(u"doubleSpinBox_3")
        self.doubleSpinBox_3.setEnabled(False)

        self.gridLayout_85.addWidget(self.doubleSpinBox_3, 0, 3, 1, 1)

        self.lineEdit_89 = QLineEdit(self.groupBox_15)
        self.lineEdit_89.setObjectName(u"lineEdit_89")
        self.lineEdit_89.setEnabled(False)

        self.gridLayout_85.addWidget(self.lineEdit_89, 1, 0, 1, 1)

        self.doubleSpinBox_6 = QDoubleSpinBox(self.groupBox_15)
        self.doubleSpinBox_6.setObjectName(u"doubleSpinBox_6")

        self.gridLayout_85.addWidget(self.doubleSpinBox_6, 1, 1, 1, 1)

        self.doubleSpinBox_5 = QDoubleSpinBox(self.groupBox_15)
        self.doubleSpinBox_5.setObjectName(u"doubleSpinBox_5")

        self.gridLayout_85.addWidget(self.doubleSpinBox_5, 1, 2, 1, 1)

        self.doubleSpinBox_4 = QDoubleSpinBox(self.groupBox_15)
        self.doubleSpinBox_4.setObjectName(u"doubleSpinBox_4")

        self.gridLayout_85.addWidget(self.doubleSpinBox_4, 1, 3, 1, 1)

        self.pushButton_6 = QPushButton(self.groupBox_15)
        self.pushButton_6.setObjectName(u"pushButton_6")

        self.gridLayout_85.addWidget(self.pushButton_6, 2, 3, 1, 1)


        self.gridLayout_81.addWidget(self.groupBox_15, 2, 0, 1, 1)

        self.groupBox_14 = QGroupBox(self.tab_45)
        self.groupBox_14.setObjectName(u"groupBox_14")
        self.gridLayout_84 = QGridLayout(self.groupBox_14)
        self.gridLayout_84.setObjectName(u"gridLayout_84")
        self.pushButton_4 = QPushButton(self.groupBox_14)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.gridLayout_84.addWidget(self.pushButton_4, 1, 1, 1, 1)

        self.pushButton_3 = QPushButton(self.groupBox_14)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.gridLayout_84.addWidget(self.pushButton_3, 0, 1, 1, 1)

        self.pushButton_5 = QPushButton(self.groupBox_14)
        self.pushButton_5.setObjectName(u"pushButton_5")

        self.gridLayout_84.addWidget(self.pushButton_5, 2, 1, 1, 1)


        self.gridLayout_81.addWidget(self.groupBox_14, 2, 1, 1, 2)

        self.groupBox_12 = QGroupBox(self.tab_45)
        self.groupBox_12.setObjectName(u"groupBox_12")
        self.gridLayout_82 = QGridLayout(self.groupBox_12)
        self.gridLayout_82.setObjectName(u"gridLayout_82")
        self.Manual_reg_step = QDoubleSpinBox(self.groupBox_12)
        self.Manual_reg_step.setObjectName(u"Manual_reg_step")
        self.Manual_reg_step.setMaximum(2000.000000000000000)

        self.gridLayout_82.addWidget(self.Manual_reg_step, 2, 1, 1, 1)

        self.Reg_manual_Ty = QDoubleSpinBox(self.groupBox_12)
        self.Reg_manual_Ty.setObjectName(u"Reg_manual_Ty")
        self.Reg_manual_Ty.setDecimals(3)
        self.Reg_manual_Ty.setMinimum(-200000.000000000000000)
        self.Reg_manual_Ty.setMaximum(200000.000000000000000)
        self.Reg_manual_Ty.setSingleStep(1.000000000000000)

        self.gridLayout_82.addWidget(self.Reg_manual_Ty, 1, 2, 1, 1)

        self.Reg_manual_Tz = QDoubleSpinBox(self.groupBox_12)
        self.Reg_manual_Tz.setObjectName(u"Reg_manual_Tz")
        self.Reg_manual_Tz.setDecimals(3)
        self.Reg_manual_Tz.setMinimum(-200000.000000000000000)
        self.Reg_manual_Tz.setMaximum(200000.000000000000000)
        self.Reg_manual_Tz.setSingleStep(1.000000000000000)

        self.gridLayout_82.addWidget(self.Reg_manual_Tz, 1, 3, 1, 1)

        self.lineEdit_72 = QLineEdit(self.groupBox_12)
        self.lineEdit_72.setObjectName(u"lineEdit_72")
        self.lineEdit_72.setEnabled(False)

        self.gridLayout_82.addWidget(self.lineEdit_72, 0, 0, 1, 1)

        self.lineEdit_71 = QLineEdit(self.groupBox_12)
        self.lineEdit_71.setObjectName(u"lineEdit_71")
        self.lineEdit_71.setEnabled(False)

        self.gridLayout_82.addWidget(self.lineEdit_71, 1, 0, 1, 1)

        self.Reg_manual_Tx = QDoubleSpinBox(self.groupBox_12)
        self.Reg_manual_Tx.setObjectName(u"Reg_manual_Tx")
        self.Reg_manual_Tx.setDecimals(3)
        self.Reg_manual_Tx.setMinimum(-200000.000000000000000)
        self.Reg_manual_Tx.setMaximum(200000.000000000000000)
        self.Reg_manual_Tx.setSingleStep(1.000000000000000)

        self.gridLayout_82.addWidget(self.Reg_manual_Tx, 1, 1, 1, 1)

        self.Reg_manual_Refz = QDoubleSpinBox(self.groupBox_12)
        self.Reg_manual_Refz.setObjectName(u"Reg_manual_Refz")
        self.Reg_manual_Refz.setEnabled(False)

        self.gridLayout_82.addWidget(self.Reg_manual_Refz, 0, 3, 1, 1)

        self.Reg_manual_Refy = QDoubleSpinBox(self.groupBox_12)
        self.Reg_manual_Refy.setObjectName(u"Reg_manual_Refy")
        self.Reg_manual_Refy.setEnabled(False)

        self.gridLayout_82.addWidget(self.Reg_manual_Refy, 0, 2, 1, 1)

        self.lineEdit_74 = QLineEdit(self.groupBox_12)
        self.lineEdit_74.setObjectName(u"lineEdit_74")
        self.lineEdit_74.setEnabled(False)

        self.gridLayout_82.addWidget(self.lineEdit_74, 2, 0, 1, 1)

        self.lineEdit_86 = QLineEdit(self.groupBox_12)
        self.lineEdit_86.setObjectName(u"lineEdit_86")

        self.gridLayout_82.addWidget(self.lineEdit_86, 2, 2, 1, 1)

        self.reg_fill_value = QDoubleSpinBox(self.groupBox_12)
        self.reg_fill_value.setObjectName(u"reg_fill_value")
        self.reg_fill_value.setMinimum(-10000000.000000000000000)
        self.reg_fill_value.setMaximum(100000.000000000000000)
        self.reg_fill_value.setValue(-1024.000000000000000)

        self.gridLayout_82.addWidget(self.reg_fill_value, 2, 3, 1, 1)

        self.Reg_manual_Refx = QDoubleSpinBox(self.groupBox_12)
        self.Reg_manual_Refx.setObjectName(u"Reg_manual_Refx")
        self.Reg_manual_Refx.setEnabled(False)

        self.gridLayout_82.addWidget(self.Reg_manual_Refx, 0, 1, 1, 1)

        self.apply_Im_transformation = QPushButton(self.groupBox_12)
        self.apply_Im_transformation.setObjectName(u"apply_Im_transformation")

        self.gridLayout_82.addWidget(self.apply_Im_transformation, 3, 3, 1, 1)


        self.gridLayout_81.addWidget(self.groupBox_12, 0, 0, 1, 1)

        self.groupBox_17 = QGroupBox(self.tab_45)
        self.groupBox_17.setObjectName(u"groupBox_17")
        self.gridLayout_86 = QGridLayout(self.groupBox_17)
        self.gridLayout_86.setObjectName(u"gridLayout_86")
        self.lineEdit_85 = QLineEdit(self.groupBox_17)
        self.lineEdit_85.setObjectName(u"lineEdit_85")
        self.lineEdit_85.setEnabled(False)

        self.gridLayout_86.addWidget(self.lineEdit_85, 0, 2, 1, 2)

        self.lineEdit_87 = QLineEdit(self.groupBox_17)
        self.lineEdit_87.setObjectName(u"lineEdit_87")
        self.lineEdit_87.setEnabled(False)

        self.gridLayout_86.addWidget(self.lineEdit_87, 0, 4, 1, 2)

        self.doubleSpinBox_14 = QDoubleSpinBox(self.groupBox_17)
        self.doubleSpinBox_14.setObjectName(u"doubleSpinBox_14")
        self.doubleSpinBox_14.setEnabled(False)

        self.gridLayout_86.addWidget(self.doubleSpinBox_14, 1, 0, 1, 1)

        self.doubleSpinBox_15 = QDoubleSpinBox(self.groupBox_17)
        self.doubleSpinBox_15.setObjectName(u"doubleSpinBox_15")
        self.doubleSpinBox_15.setEnabled(False)

        self.gridLayout_86.addWidget(self.doubleSpinBox_15, 1, 1, 1, 1)

        self.doubleSpinBox_16 = QDoubleSpinBox(self.groupBox_17)
        self.doubleSpinBox_16.setObjectName(u"doubleSpinBox_16")
        self.doubleSpinBox_16.setEnabled(False)

        self.gridLayout_86.addWidget(self.doubleSpinBox_16, 1, 2, 1, 1)

        self.doubleSpinBox_17 = QDoubleSpinBox(self.groupBox_17)
        self.doubleSpinBox_17.setObjectName(u"doubleSpinBox_17")
        self.doubleSpinBox_17.setEnabled(False)

        self.gridLayout_86.addWidget(self.doubleSpinBox_17, 1, 3, 1, 1)

        self.doubleSpinBox_19 = QDoubleSpinBox(self.groupBox_17)
        self.doubleSpinBox_19.setObjectName(u"doubleSpinBox_19")
        self.doubleSpinBox_19.setEnabled(False)

        self.gridLayout_86.addWidget(self.doubleSpinBox_19, 1, 4, 1, 1)

        self.doubleSpinBox_18 = QDoubleSpinBox(self.groupBox_17)
        self.doubleSpinBox_18.setObjectName(u"doubleSpinBox_18")
        self.doubleSpinBox_18.setEnabled(False)

        self.gridLayout_86.addWidget(self.doubleSpinBox_18, 1, 5, 1, 1)

        self.doubleSpinBox_21 = QDoubleSpinBox(self.groupBox_17)
        self.doubleSpinBox_21.setObjectName(u"doubleSpinBox_21")

        self.gridLayout_86.addWidget(self.doubleSpinBox_21, 2, 0, 1, 1)

        self.doubleSpinBox_22 = QDoubleSpinBox(self.groupBox_17)
        self.doubleSpinBox_22.setObjectName(u"doubleSpinBox_22")

        self.gridLayout_86.addWidget(self.doubleSpinBox_22, 2, 1, 1, 1)

        self.doubleSpinBox_20 = QDoubleSpinBox(self.groupBox_17)
        self.doubleSpinBox_20.setObjectName(u"doubleSpinBox_20")

        self.gridLayout_86.addWidget(self.doubleSpinBox_20, 2, 2, 1, 1)

        self.doubleSpinBox_25 = QDoubleSpinBox(self.groupBox_17)
        self.doubleSpinBox_25.setObjectName(u"doubleSpinBox_25")

        self.gridLayout_86.addWidget(self.doubleSpinBox_25, 2, 3, 1, 1)

        self.doubleSpinBox_23 = QDoubleSpinBox(self.groupBox_17)
        self.doubleSpinBox_23.setObjectName(u"doubleSpinBox_23")

        self.gridLayout_86.addWidget(self.doubleSpinBox_23, 2, 4, 1, 1)

        self.doubleSpinBox_24 = QDoubleSpinBox(self.groupBox_17)
        self.doubleSpinBox_24.setObjectName(u"doubleSpinBox_24")

        self.gridLayout_86.addWidget(self.doubleSpinBox_24, 2, 5, 1, 1)

        self.lineEdit_84 = QLineEdit(self.groupBox_17)
        self.lineEdit_84.setObjectName(u"lineEdit_84")
        self.lineEdit_84.setEnabled(False)

        self.gridLayout_86.addWidget(self.lineEdit_84, 0, 0, 1, 2)


        self.gridLayout_81.addWidget(self.groupBox_17, 3, 0, 1, 3)

        self.tabWidget_10.addTab(self.tab_45, "")

        self.gridLayout_12.addWidget(self.tabWidget_10, 0, 1, 1, 1)

        self.tabView01.addTab(self.tab_17, "")
        self.tab_31 = QWidget()
        self.tab_31.setObjectName(u"tab_31")
        self.gridLayout_30 = QGridLayout(self.tab_31)
        self.gridLayout_30.setObjectName(u"gridLayout_30")
        self.tabWidget_8 = QTabWidget(self.tab_31)
        self.tabWidget_8.setObjectName(u"tabWidget_8")
        self.tab_32 = QWidget()
        self.tab_32.setObjectName(u"tab_32")
        self.gridLayout_31 = QGridLayout(self.tab_32)
        self.gridLayout_31.setObjectName(u"gridLayout_31")
        self.lineEdit_5 = QLineEdit(self.tab_32)
        self.lineEdit_5.setObjectName(u"lineEdit_5")
        self.lineEdit_5.setEnabled(False)

        self.gridLayout_31.addWidget(self.lineEdit_5, 1, 3, 1, 1)

        self.Play4D_Buttom = QPushButton(self.tab_32)
        self.Play4D_Buttom.setObjectName(u"Play4D_Buttom")
        self.Play4D_Buttom.setCheckable(True)
        self.Play4D_Buttom.setChecked(False)

        self.gridLayout_31.addWidget(self.Play4D_Buttom, 1, 0, 1, 1)

        self.horizontalSpacer_24 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_31.addItem(self.horizontalSpacer_24, 1, 2, 1, 1)

        self.horizontalSpacer_25 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_31.addItem(self.horizontalSpacer_25, 1, 1, 1, 1)

        self.CT4D_table_display = QTableWidget(self.tab_32)
        self.CT4D_table_display.setObjectName(u"CT4D_table_display")

        self.gridLayout_31.addWidget(self.CT4D_table_display, 0, 0, 1, 6)

        self.Play_DCT_speed = QSpinBox(self.tab_32)
        self.Play_DCT_speed.setObjectName(u"Play_DCT_speed")
        self.Play_DCT_speed.setMinimum(1)
        self.Play_DCT_speed.setMaximum(10)
        self.Play_DCT_speed.setValue(4)

        self.gridLayout_31.addWidget(self.Play_DCT_speed, 1, 4, 1, 1)

        self.tabWidget_8.addTab(self.tab_32, "")
        self.tab_33 = QWidget()
        self.tab_33.setObjectName(u"tab_33")
        self.gridLayout_78 = QGridLayout(self.tab_33)
        self.gridLayout_78.setObjectName(u"gridLayout_78")
        self.calcAvg4DCT = QPushButton(self.tab_33)
        self.calcAvg4DCT.setObjectName(u"calcAvg4DCT")

        self.gridLayout_78.addWidget(self.calcAvg4DCT, 0, 0, 1, 1)

        self.horizontalSpacer_79 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_78.addItem(self.horizontalSpacer_79, 0, 1, 1, 1)

        self.verticalSpacer_22 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_78.addItem(self.verticalSpacer_22, 1, 0, 1, 1)

        self.tabWidget_8.addTab(self.tab_33, "")

        self.gridLayout_30.addWidget(self.tabWidget_8, 0, 0, 1, 1)

        self.tabView01.addTab(self.tab_31, "")
        self.tab_30 = QWidget()
        self.tab_30.setObjectName(u"tab_30")
        self.gridLayout_32 = QGridLayout(self.tab_30)
        self.gridLayout_32.setObjectName(u"gridLayout_32")
        self.tabWidget_9 = QTabWidget(self.tab_30)
        self.tabWidget_9.setObjectName(u"tabWidget_9")
        self.tab_34 = QWidget()
        self.tab_34.setObjectName(u"tab_34")
        self.gridLayout_33 = QGridLayout(self.tab_34)
        self.gridLayout_33.setObjectName(u"gridLayout_33")
        self.roi_circle_add_row = QPushButton(self.tab_34)
        self.roi_circle_add_row.setObjectName(u"roi_circle_add_row")

        self.gridLayout_33.addWidget(self.roi_circle_add_row, 2, 1, 1, 1)

        self.circ_roi_exp_csv = QPushButton(self.tab_34)
        self.circ_roi_exp_csv.setObjectName(u"circ_roi_exp_csv")

        self.gridLayout_33.addWidget(self.circ_roi_exp_csv, 3, 0, 1, 1)

        self.get_circ_roi_data = QPushButton(self.tab_34)
        self.get_circ_roi_data.setObjectName(u"get_circ_roi_data")

        self.gridLayout_33.addWidget(self.get_circ_roi_data, 3, 1, 1, 1)

        self.roi_circle_remove_row = QPushButton(self.tab_34)
        self.roi_circle_remove_row.setObjectName(u"roi_circle_remove_row")

        self.gridLayout_33.addWidget(self.roi_circle_remove_row, 2, 2, 1, 1)

        self.circ_roi_load_csv = QPushButton(self.tab_34)
        self.circ_roi_load_csv.setObjectName(u"circ_roi_load_csv")

        self.gridLayout_33.addWidget(self.circ_roi_load_csv, 2, 0, 1, 1)

        self.checkBox_circ_roi_data_2 = QCheckBox(self.tab_34)
        self.checkBox_circ_roi_data_2.setObjectName(u"checkBox_circ_roi_data_2")

        self.gridLayout_33.addWidget(self.checkBox_circ_roi_data_2, 3, 4, 1, 4)

        self.table_circ_roi = QTableWidget(self.tab_34)
        self.table_circ_roi.setObjectName(u"table_circ_roi")
        self.table_circ_roi.setFont(font1)

        self.gridLayout_33.addWidget(self.table_circ_roi, 0, 0, 1, 8)

        self.checkBox_circ_roi_data_01 = QCheckBox(self.tab_34)
        self.checkBox_circ_roi_data_01.setObjectName(u"checkBox_circ_roi_data_01")

        self.gridLayout_33.addWidget(self.checkBox_circ_roi_data_01, 3, 2, 1, 1)

        self.holdOnROI = QCheckBox(self.tab_34)
        self.holdOnROI.setObjectName(u"holdOnROI")

        self.gridLayout_33.addWidget(self.holdOnROI, 3, 3, 1, 1)

        self.groupBox_8 = QGroupBox(self.tab_34)
        self.groupBox_8.setObjectName(u"groupBox_8")

        self.gridLayout_33.addWidget(self.groupBox_8, 2, 3, 1, 5)

        self.tabWidget_9.addTab(self.tab_34, "")
        self.tab_35 = QWidget()
        self.tab_35.setObjectName(u"tab_35")
        self.gridLayout_34 = QGridLayout(self.tab_35)
        self.gridLayout_34.setObjectName(u"gridLayout_34")
        self.get_circ_roi_data2 = QPushButton(self.tab_35)
        self.get_circ_roi_data2.setObjectName(u"get_circ_roi_data2")

        self.gridLayout_34.addWidget(self.get_circ_roi_data2, 1, 0, 1, 1)

        self.exp_csv_roi_c_values = QPushButton(self.tab_35)
        self.exp_csv_roi_c_values.setObjectName(u"exp_csv_roi_c_values")

        self.gridLayout_34.addWidget(self.exp_csv_roi_c_values, 1, 1, 1, 1)

        self.table_roi_c_values = QTableWidget(self.tab_35)
        self.table_roi_c_values.setObjectName(u"table_roi_c_values")

        self.gridLayout_34.addWidget(self.table_roi_c_values, 0, 0, 1, 2)

        self.tabWidget_9.addTab(self.tab_35, "")

        self.gridLayout_32.addWidget(self.tabWidget_9, 0, 0, 1, 1)

        self.tabView01.addTab(self.tab_30, "")

        self.gridLayout_4.addWidget(self.tabView01, 2, 1, 1, 1)

        self.gridLayout_4.setRowStretch(0, 1)
        self.gridLayout_4.setRowStretch(2, 1)
        self.gridLayout_4.setColumnStretch(0, 1)
        self.gridLayout_4.setColumnStretch(1, 1)
        self.tabModules.addTab(self.im_display_tab, "")
        self._3Dview = QWidget()
        self._3Dview.setObjectName(u"_3Dview")
        self.gridLayout_63 = QGridLayout(self._3Dview)
        self.gridLayout_63.setObjectName(u"gridLayout_63")
        self.View3DgroupBox_12 = QGroupBox(self._3Dview)
        self.View3DgroupBox_12.setObjectName(u"View3DgroupBox_12")
        self.gridLayout_65 = QGridLayout(self.View3DgroupBox_12)
        self.gridLayout_65.setObjectName(u"gridLayout_65")
        self.View3D_name_02 = QLineEdit(self.View3DgroupBox_12)
        self.View3D_name_02.setObjectName(u"View3D_name_02")
        self.View3D_name_02.setEnabled(False)

        self.gridLayout_65.addWidget(self.View3D_name_02, 1, 0, 1, 1)

        self.View3D_name_04 = QLineEdit(self.View3DgroupBox_12)
        self.View3D_name_04.setObjectName(u"View3D_name_04")
        self.View3D_name_04.setEnabled(False)

        self.gridLayout_65.addWidget(self.View3D_name_04, 3, 0, 1, 1)

        self.View3D_clear_all = QPushButton(self.View3DgroupBox_12)
        self.View3D_clear_all.setObjectName(u"View3D_clear_all")
        self.View3D_clear_all.setEnabled(True)

        self.gridLayout_65.addWidget(self.View3D_clear_all, 6, 2, 1, 1)

        self.View3D_quality_spin_01 = QDoubleSpinBox(self.View3DgroupBox_12)
        self.View3D_quality_spin_01.setObjectName(u"View3D_quality_spin_01")
        self.View3D_quality_spin_01.setEnabled(False)

        self.gridLayout_65.addWidget(self.View3D_quality_spin_01, 0, 2, 1, 1)

        self.View3D_quality_slider = QSlider(self.View3DgroupBox_12)
        self.View3D_quality_slider.setObjectName(u"View3D_quality_slider")
        self.View3D_quality_slider.setEnabled(False)
        self.View3D_quality_slider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_65.addWidget(self.View3D_quality_slider, 0, 1, 1, 1)

        self.View3D_reset_camera = QPushButton(self.View3DgroupBox_12)
        self.View3D_reset_camera.setObjectName(u"View3D_reset_camera")
        self.View3D_reset_camera.setEnabled(True)

        self.gridLayout_65.addWidget(self.View3D_reset_camera, 6, 1, 1, 1)

        self.View3D_name_05 = QLineEdit(self.View3DgroupBox_12)
        self.View3D_name_05.setObjectName(u"View3D_name_05")
        self.View3D_name_05.setEnabled(False)

        self.gridLayout_65.addWidget(self.View3D_name_05, 4, 0, 1, 1)

        self.View3D_name_01 = QLineEdit(self.View3DgroupBox_12)
        self.View3D_name_01.setObjectName(u"View3D_name_01")
        self.View3D_name_01.setEnabled(False)

        self.gridLayout_65.addWidget(self.View3D_name_01, 0, 0, 1, 1)

        self.View3D_brightness_slider = QSlider(self.View3DgroupBox_12)
        self.View3D_brightness_slider.setObjectName(u"View3D_brightness_slider")
        self.View3D_brightness_slider.setEnabled(False)
        self.View3D_brightness_slider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_65.addWidget(self.View3D_brightness_slider, 1, 1, 1, 1)

        self.View3D_name_03 = QLineEdit(self.View3DgroupBox_12)
        self.View3D_name_03.setObjectName(u"View3D_name_03")
        self.View3D_name_03.setEnabled(False)

        self.gridLayout_65.addWidget(self.View3D_name_03, 2, 0, 1, 1)

        self.View3D_brightness_spin_01 = QDoubleSpinBox(self.View3DgroupBox_12)
        self.View3D_brightness_spin_01.setObjectName(u"View3D_brightness_spin_01")
        self.View3D_brightness_spin_01.setEnabled(False)

        self.gridLayout_65.addWidget(self.View3D_brightness_spin_01, 1, 2, 1, 1)

        self.iew3D_lighting_options = QComboBox(self.View3DgroupBox_12)
        self.iew3D_lighting_options.setObjectName(u"iew3D_lighting_options")

        self.gridLayout_65.addWidget(self.iew3D_lighting_options, 4, 1, 1, 2)

        self.View3D_render_options = QComboBox(self.View3DgroupBox_12)
        self.View3D_render_options.setObjectName(u"View3D_render_options")

        self.gridLayout_65.addWidget(self.View3D_render_options, 3, 1, 1, 2)

        self.View3D_specular_spin_01 = QDoubleSpinBox(self.View3DgroupBox_12)
        self.View3D_specular_spin_01.setObjectName(u"View3D_specular_spin_01")
        self.View3D_specular_spin_01.setEnabled(False)

        self.gridLayout_65.addWidget(self.View3D_specular_spin_01, 2, 2, 1, 1)

        self.View3D_specular_slider = QSlider(self.View3DgroupBox_12)
        self.View3D_specular_slider.setObjectName(u"View3D_specular_slider")
        self.View3D_specular_slider.setEnabled(False)
        self.View3D_specular_slider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_65.addWidget(self.View3D_specular_slider, 2, 1, 1, 1)

        self.View3D_shading_checkBox = QCheckBox(self.View3DgroupBox_12)
        self.View3D_shading_checkBox.setObjectName(u"View3D_shading_checkBox")
        self.View3D_shading_checkBox.setEnabled(False)

        self.gridLayout_65.addWidget(self.View3D_shading_checkBox, 5, 0, 1, 1)

        self.View3D_shoiw_axes_checkBox = QCheckBox(self.View3DgroupBox_12)
        self.View3D_shoiw_axes_checkBox.setObjectName(u"View3D_shoiw_axes_checkBox")
        self.View3D_shoiw_axes_checkBox.setEnabled(False)

        self.gridLayout_65.addWidget(self.View3D_shoiw_axes_checkBox, 5, 1, 1, 1)

        self.View3D_annotation_checkBox = QCheckBox(self.View3DgroupBox_12)
        self.View3D_annotation_checkBox.setObjectName(u"View3D_annotation_checkBox")
        self.View3D_annotation_checkBox.setEnabled(False)

        self.gridLayout_65.addWidget(self.View3D_annotation_checkBox, 5, 2, 1, 1)


        self.gridLayout_63.addWidget(self.View3DgroupBox_12, 0, 3, 1, 1)

        self.View3DhorizontalSpacer_78 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_63.addItem(self.View3DhorizontalSpacer_78, 3, 3, 1, 1)

        self.View3DverticalSpacer_22 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_63.addItem(self.View3DverticalSpacer_22, 2, 0, 1, 1)

        self.View3DverticalSpacer_21 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_63.addItem(self.View3DverticalSpacer_21, 0, 0, 1, 1)

        self.View3DhorizontalSpacer_79 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_63.addItem(self.View3DhorizontalSpacer_79, 3, 2, 1, 1)

        self.View3DhorizontalSpacer_77 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_63.addItem(self.View3DhorizontalSpacer_77, 3, 1, 1, 1)

        self.VTK_view_3D = QWidget(self._3Dview)
        self.VTK_view_3D.setObjectName(u"VTK_view_3D")

        self.gridLayout_63.addWidget(self.VTK_view_3D, 0, 1, 2, 2)

        self.tabWidget_3Dview = QTabWidget(self._3Dview)
        self.tabWidget_3Dview.setObjectName(u"tabWidget_3Dview")
        self.tab_40 = QWidget()
        self.tab_40.setObjectName(u"tab_40")
        self.gridLayout_74 = QGridLayout(self.tab_40)
        self.gridLayout_74.setObjectName(u"gridLayout_74")
        self._3D_Struct_table = QTableWidget(self.tab_40)
        self._3D_Struct_table.setObjectName(u"_3D_Struct_table")

        self.gridLayout_74.addWidget(self._3D_Struct_table, 0, 0, 1, 1)

        self.tabWidget_3Dview.addTab(self.tab_40, "")
        self.tab_42 = QWidget()
        self.tab_42.setObjectName(u"tab_42")
        self.gridLayout_75 = QGridLayout(self.tab_42)
        self.gridLayout_75.setObjectName(u"gridLayout_75")
        self._STL_Surface_table = QTableWidget(self.tab_42)
        self._STL_Surface_table.setObjectName(u"_STL_Surface_table")

        self.gridLayout_75.addWidget(self._STL_Surface_table, 0, 0, 1, 1)

        self.tabWidget_3Dview.addTab(self.tab_42, "")
        self.tab_41 = QWidget()
        self.tab_41.setObjectName(u"tab_41")
        self.tabWidget_3Dview.addTab(self.tab_41, "")
        self.tab_43 = QWidget()
        self.tab_43.setObjectName(u"tab_43")
        self.gridLayout_76 = QGridLayout(self.tab_43)
        self.gridLayout_76.setObjectName(u"gridLayout_76")
        self._3D_proton_table = QTableWidget(self.tab_43)
        self._3D_proton_table.setObjectName(u"_3D_proton_table")

        self.gridLayout_76.addWidget(self._3D_proton_table, 0, 0, 1, 1)

        self.tabWidget_3Dview.addTab(self.tab_43, "")

        self.gridLayout_63.addWidget(self.tabWidget_3Dview, 2, 1, 1, 2)

        self.View3DgroupBox_13 = QGroupBox(self._3Dview)
        self.View3DgroupBox_13.setObjectName(u"View3DgroupBox_13")
        self.gridLayout_67 = QGridLayout(self.View3DgroupBox_13)
        self.gridLayout_67.setObjectName(u"gridLayout_67")
        self.View3DhorizontalSpacer_86 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_67.addItem(self.View3DhorizontalSpacer_86, 15, 3, 1, 1)

        self.View3D_Threshold_slider_01 = QSlider(self.View3DgroupBox_13)
        self.View3D_Threshold_slider_01.setObjectName(u"View3D_Threshold_slider_01")
        self.View3D_Threshold_slider_01.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_67.addWidget(self.View3D_Threshold_slider_01, 2, 1, 1, 4)

        self.View3D_coronal_slider_01 = QSlider(self.View3DgroupBox_13)
        self.View3D_coronal_slider_01.setObjectName(u"View3D_coronal_slider_01")
        self.View3D_coronal_slider_01.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_67.addWidget(self.View3D_coronal_slider_01, 6, 1, 1, 4)

        self.View3DverticalSpacer_23 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_67.addItem(self.View3DverticalSpacer_23, 14, 5, 1, 1)

        self.View3D_axial_slider_01 = QSlider(self.View3DgroupBox_13)
        self.View3D_axial_slider_01.setObjectName(u"View3D_axial_slider_01")
        self.View3D_axial_slider_01.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_67.addWidget(self.View3D_axial_slider_01, 4, 1, 1, 4)

        self.View3D_axial_spin_02 = QSpinBox(self.View3DgroupBox_13)
        self.View3D_axial_spin_02.setObjectName(u"View3D_axial_spin_02")

        self.gridLayout_67.addWidget(self.View3D_axial_spin_02, 5, 5, 1, 1)

        self.View3DhorizontalSpacer_80 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_67.addItem(self.View3DhorizontalSpacer_80, 15, 0, 1, 1)

        self.View3D_Apply = QPushButton(self.View3DgroupBox_13)
        self.View3D_Apply.setObjectName(u"View3D_Apply")

        self.gridLayout_67.addWidget(self.View3D_Apply, 12, 5, 1, 1)

        self.View3D_colormap = QComboBox(self.View3DgroupBox_13)
        self.View3D_colormap.setObjectName(u"View3D_colormap")

        self.gridLayout_67.addWidget(self.View3D_colormap, 10, 1, 1, 4)

        self.View3D_axial_spin_01 = QSpinBox(self.View3DgroupBox_13)
        self.View3D_axial_spin_01.setObjectName(u"View3D_axial_spin_01")

        self.gridLayout_67.addWidget(self.View3D_axial_spin_01, 4, 5, 1, 1)

        self.View3DhorizontalSpacer_82 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_67.addItem(self.View3DhorizontalSpacer_82, 15, 4, 1, 1)

        self.View3D_Threshold_spin_01 = QDoubleSpinBox(self.View3DgroupBox_13)
        self.View3D_Threshold_spin_01.setObjectName(u"View3D_Threshold_spin_01")

        self.gridLayout_67.addWidget(self.View3D_Threshold_spin_01, 2, 5, 1, 1)

        self.View3DhorizontalSpacer_85 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_67.addItem(self.View3DhorizontalSpacer_85, 15, 2, 1, 1)

        self.View3D_coronal_spin_01 = QSpinBox(self.View3DgroupBox_13)
        self.View3D_coronal_spin_01.setObjectName(u"View3D_coronal_spin_01")

        self.gridLayout_67.addWidget(self.View3D_coronal_spin_01, 6, 5, 1, 1)

        self.View3D_name_06 = QLineEdit(self.View3DgroupBox_13)
        self.View3D_name_06.setObjectName(u"View3D_name_06")
        self.View3D_name_06.setEnabled(False)

        self.gridLayout_67.addWidget(self.View3D_name_06, 1, 0, 1, 1)

        self.View3D_sagittal_slider_01 = QSlider(self.View3DgroupBox_13)
        self.View3D_sagittal_slider_01.setObjectName(u"View3D_sagittal_slider_01")
        self.View3D_sagittal_slider_01.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_67.addWidget(self.View3D_sagittal_slider_01, 8, 1, 1, 4)

        self.View3D_sagittal_slider_02 = QSlider(self.View3DgroupBox_13)
        self.View3D_sagittal_slider_02.setObjectName(u"View3D_sagittal_slider_02")
        self.View3D_sagittal_slider_02.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_67.addWidget(self.View3D_sagittal_slider_02, 9, 1, 1, 4)

        self.View3D_Threshold_spin_02 = QDoubleSpinBox(self.View3DgroupBox_13)
        self.View3D_Threshold_spin_02.setObjectName(u"View3D_Threshold_spin_02")

        self.gridLayout_67.addWidget(self.View3D_Threshold_spin_02, 3, 5, 1, 1)

        self.View3D_sagittal_spin_02 = QSpinBox(self.View3DgroupBox_13)
        self.View3D_sagittal_spin_02.setObjectName(u"View3D_sagittal_spin_02")

        self.gridLayout_67.addWidget(self.View3D_sagittal_spin_02, 9, 5, 1, 1)

        self.View3D_sagittal_spin_01 = QSpinBox(self.View3DgroupBox_13)
        self.View3D_sagittal_spin_01.setObjectName(u"View3D_sagittal_spin_01")

        self.gridLayout_67.addWidget(self.View3D_sagittal_spin_01, 8, 5, 1, 1)

        self.View3D_name_08 = QLineEdit(self.View3DgroupBox_13)
        self.View3D_name_08.setObjectName(u"View3D_name_08")
        self.View3D_name_08.setEnabled(False)

        self.gridLayout_67.addWidget(self.View3D_name_08, 4, 0, 1, 1)

        self.View3D_isovalue_slider = QSlider(self.View3DgroupBox_13)
        self.View3D_isovalue_slider.setObjectName(u"View3D_isovalue_slider")
        self.View3D_isovalue_slider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_67.addWidget(self.View3D_isovalue_slider, 1, 1, 1, 4)

        self.View3D_name_09 = QLineEdit(self.View3DgroupBox_13)
        self.View3D_name_09.setObjectName(u"View3D_name_09")
        self.View3D_name_09.setEnabled(False)

        self.gridLayout_67.addWidget(self.View3D_name_09, 6, 0, 1, 1)

        self.View3D_Threshold_slider_02 = QSlider(self.View3DgroupBox_13)
        self.View3D_Threshold_slider_02.setObjectName(u"View3D_Threshold_slider_02")
        self.View3D_Threshold_slider_02.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_67.addWidget(self.View3D_Threshold_slider_02, 3, 1, 1, 4)

        self.View3D_name_10 = QLineEdit(self.View3DgroupBox_13)
        self.View3D_name_10.setObjectName(u"View3D_name_10")
        self.View3D_name_10.setEnabled(False)

        self.gridLayout_67.addWidget(self.View3D_name_10, 8, 0, 1, 1)

        self.View3DhorizontalSpacer_81 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_67.addItem(self.View3DhorizontalSpacer_81, 15, 1, 1, 1)

        self.View3D_axial_slider_02 = QSlider(self.View3DgroupBox_13)
        self.View3D_axial_slider_02.setObjectName(u"View3D_axial_slider_02")
        self.View3D_axial_slider_02.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_67.addWidget(self.View3D_axial_slider_02, 5, 1, 1, 4)

        self.View3DhorizontalSpacer_83 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_67.addItem(self.View3DhorizontalSpacer_83, 15, 5, 1, 1)

        self.View3D_histogram = QWidget(self.View3DgroupBox_13)
        self.View3D_histogram.setObjectName(u"View3D_histogram")

        self.gridLayout_67.addWidget(self.View3D_histogram, 0, 0, 1, 6)

        self.View3D_name_07 = QLineEdit(self.View3DgroupBox_13)
        self.View3D_name_07.setObjectName(u"View3D_name_07")
        self.View3D_name_07.setEnabled(False)

        self.gridLayout_67.addWidget(self.View3D_name_07, 2, 0, 1, 1)

        self.View3D_coronal_spin_02 = QSpinBox(self.View3DgroupBox_13)
        self.View3D_coronal_spin_02.setObjectName(u"View3D_coronal_spin_02")

        self.gridLayout_67.addWidget(self.View3D_coronal_spin_02, 7, 5, 1, 1)

        self.View3D_isovalue_spin_01 = QDoubleSpinBox(self.View3DgroupBox_13)
        self.View3D_isovalue_spin_01.setObjectName(u"View3D_isovalue_spin_01")

        self.gridLayout_67.addWidget(self.View3D_isovalue_spin_01, 1, 5, 1, 1)

        self.View3DgroupBox_14 = QGroupBox(self.View3DgroupBox_13)
        self.View3DgroupBox_14.setObjectName(u"View3DgroupBox_14")
        self.gridLayout_66 = QGridLayout(self.View3DgroupBox_14)
        self.gridLayout_66.setObjectName(u"gridLayout_66")
        self.View3D_4D_speed_play_slider = QSlider(self.View3DgroupBox_14)
        self.View3D_4D_speed_play_slider.setObjectName(u"View3D_4D_speed_play_slider")
        self.View3D_4D_speed_play_slider.setEnabled(False)
        self.View3D_4D_speed_play_slider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_66.addWidget(self.View3D_4D_speed_play_slider, 0, 2, 1, 1)

        self.View3D_play4D = QToolButton(self.View3DgroupBox_14)
        self.View3D_play4D.setObjectName(u"View3D_play4D")

        self.gridLayout_66.addWidget(self.View3D_play4D, 0, 0, 1, 1)

        self.View3D_name_12 = QLineEdit(self.View3DgroupBox_14)
        self.View3D_name_12.setObjectName(u"View3D_name_12")
        self.View3D_name_12.setEnabled(False)

        self.gridLayout_66.addWidget(self.View3D_name_12, 0, 1, 1, 1)

        self.View3D_4D_speed_play_spin_01 = QDoubleSpinBox(self.View3DgroupBox_14)
        self.View3D_4D_speed_play_spin_01.setObjectName(u"View3D_4D_speed_play_spin_01")
        self.View3D_4D_speed_play_spin_01.setEnabled(False)

        self.gridLayout_66.addWidget(self.View3D_4D_speed_play_spin_01, 0, 3, 1, 1)


        self.gridLayout_67.addWidget(self.View3DgroupBox_14, 16, 0, 1, 7)

        self.View3D_name_11 = QLineEdit(self.View3DgroupBox_13)
        self.View3D_name_11.setObjectName(u"View3D_name_11")
        self.View3D_name_11.setEnabled(False)

        self.gridLayout_67.addWidget(self.View3D_name_11, 10, 0, 1, 1)

        self.View3D_coronal_slider_02 = QSlider(self.View3DgroupBox_13)
        self.View3D_coronal_slider_02.setObjectName(u"View3D_coronal_slider_02")
        self.View3D_coronal_slider_02.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_67.addWidget(self.View3D_coronal_slider_02, 7, 1, 1, 4)

        self.View3D_real_time_checkBox = QCheckBox(self.View3DgroupBox_13)
        self.View3D_real_time_checkBox.setObjectName(u"View3D_real_time_checkBox")
        self.View3D_real_time_checkBox.setEnabled(False)

        self.gridLayout_67.addWidget(self.View3D_real_time_checkBox, 11, 5, 1, 1)

        self.View3D_update_all_3D = QCheckBox(self.View3DgroupBox_13)
        self.View3D_update_all_3D.setObjectName(u"View3D_update_all_3D")
        self.View3D_update_all_3D.setEnabled(False)

        self.gridLayout_67.addWidget(self.View3D_update_all_3D, 10, 5, 1, 1)


        self.gridLayout_63.addWidget(self.View3DgroupBox_13, 1, 3, 2, 1)

        self.verticalSpacer_19 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_63.addItem(self.verticalSpacer_19, 1, 0, 1, 1)

        self.tabModules.addTab(self._3Dview, "")
        self.im_compare_tab = QWidget()
        self.im_compare_tab.setObjectName(u"im_compare_tab")
        self.gridLayout_16 = QGridLayout(self.im_compare_tab)
        self.gridLayout_16.setObjectName(u"gridLayout_16")
        self.SliderCompareView = QSlider(self.im_compare_tab)
        self.SliderCompareView.setObjectName(u"SliderCompareView")
        self.SliderCompareView.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_16.addWidget(self.SliderCompareView, 3, 1, 1, 1)

        self.groupBox_2 = QGroupBox(self.im_compare_tab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_17 = QGridLayout(self.groupBox_2)
        self.gridLayout_17.setObjectName(u"gridLayout_17")
        self.Ax_comp_cont_1 = QWidget(self.groupBox_2)
        self.Ax_comp_cont_1.setObjectName(u"Ax_comp_cont_1")

        self.gridLayout_17.addWidget(self.Ax_comp_cont_1, 0, 0, 1, 1)

        self.Ax_comp_cont_4 = QWidget(self.groupBox_2)
        self.Ax_comp_cont_4.setObjectName(u"Ax_comp_cont_4")

        self.gridLayout_17.addWidget(self.Ax_comp_cont_4, 0, 1, 1, 1)

        self.Ax_comp_cont_7 = QWidget(self.groupBox_2)
        self.Ax_comp_cont_7.setObjectName(u"Ax_comp_cont_7")

        self.gridLayout_17.addWidget(self.Ax_comp_cont_7, 0, 2, 1, 1)

        self.Ax_comp_cont_10 = QWidget(self.groupBox_2)
        self.Ax_comp_cont_10.setObjectName(u"Ax_comp_cont_10")

        self.gridLayout_17.addWidget(self.Ax_comp_cont_10, 0, 3, 1, 1)

        self.Ax_comp_cont_2 = QWidget(self.groupBox_2)
        self.Ax_comp_cont_2.setObjectName(u"Ax_comp_cont_2")

        self.gridLayout_17.addWidget(self.Ax_comp_cont_2, 1, 0, 1, 1)

        self.Ax_comp_cont_5 = QWidget(self.groupBox_2)
        self.Ax_comp_cont_5.setObjectName(u"Ax_comp_cont_5")

        self.gridLayout_17.addWidget(self.Ax_comp_cont_5, 1, 1, 1, 1)

        self.Ax_comp_cont_8 = QWidget(self.groupBox_2)
        self.Ax_comp_cont_8.setObjectName(u"Ax_comp_cont_8")

        self.gridLayout_17.addWidget(self.Ax_comp_cont_8, 1, 2, 1, 1)

        self.Ax_comp_cont_11 = QWidget(self.groupBox_2)
        self.Ax_comp_cont_11.setObjectName(u"Ax_comp_cont_11")

        self.gridLayout_17.addWidget(self.Ax_comp_cont_11, 1, 3, 1, 1)

        self.Ax_comp_cont_6 = QWidget(self.groupBox_2)
        self.Ax_comp_cont_6.setObjectName(u"Ax_comp_cont_6")

        self.gridLayout_17.addWidget(self.Ax_comp_cont_6, 2, 1, 1, 1)

        self.Ax_comp_cont_9 = QWidget(self.groupBox_2)
        self.Ax_comp_cont_9.setObjectName(u"Ax_comp_cont_9")

        self.gridLayout_17.addWidget(self.Ax_comp_cont_9, 2, 2, 1, 1)

        self.Ax_comp_cont_12 = QWidget(self.groupBox_2)
        self.Ax_comp_cont_12.setObjectName(u"Ax_comp_cont_12")

        self.gridLayout_17.addWidget(self.Ax_comp_cont_12, 2, 3, 1, 1)

        self.Ax_comp_cont_3 = QWidget(self.groupBox_2)
        self.Ax_comp_cont_3.setObjectName(u"Ax_comp_cont_3")

        self.gridLayout_17.addWidget(self.Ax_comp_cont_3, 2, 0, 1, 1)


        self.gridLayout_16.addWidget(self.groupBox_2, 0, 0, 1, 9)

        self.Comp_im_idx = QSpinBox(self.im_compare_tab)
        self.Comp_im_idx.setObjectName(u"Comp_im_idx")
        self.Comp_im_idx.setMinimum(-1)
        self.Comp_im_idx.setMaximum(-1)
        self.Comp_im_idx.setValue(-1)

        self.gridLayout_16.addWidget(self.Comp_im_idx, 3, 0, 1, 1)

        self.but_create_comp_axes = QPushButton(self.im_compare_tab)
        self.but_create_comp_axes.setObjectName(u"but_create_comp_axes")
        self.but_create_comp_axes.setFont(font)

        self.gridLayout_16.addWidget(self.but_create_comp_axes, 3, 8, 1, 1)

        self.line_12 = QFrame(self.im_compare_tab)
        self.line_12.setObjectName(u"line_12")
        self.line_12.setFrameShape(QFrame.Shape.HLine)
        self.line_12.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_16.addWidget(self.line_12, 1, 0, 1, 9)

        self.Comp_linkSlices = QCheckBox(self.im_compare_tab)
        self.Comp_linkSlices.setObjectName(u"Comp_linkSlices")
        self.Comp_linkSlices.setChecked(True)

        self.gridLayout_16.addWidget(self.Comp_linkSlices, 3, 3, 1, 1)

        self.Comp_view_sel_box = QComboBox(self.im_compare_tab)
        self.Comp_view_sel_box.setObjectName(u"Comp_view_sel_box")

        self.gridLayout_16.addWidget(self.Comp_view_sel_box, 3, 6, 1, 1)

        self.link_win_lev = QCheckBox(self.im_compare_tab)
        self.link_win_lev.setObjectName(u"link_win_lev")
        self.link_win_lev.setChecked(True)

        self.gridLayout_16.addWidget(self.link_win_lev, 3, 4, 1, 1)

        self.horizontalSpacer_16 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_16.addItem(self.horizontalSpacer_16, 3, 7, 1, 1)

        self.comp_link_zoom = QCheckBox(self.im_compare_tab)
        self.comp_link_zoom.setObjectName(u"comp_link_zoom")

        self.gridLayout_16.addWidget(self.comp_link_zoom, 3, 5, 1, 1)

        self.tabModules.addTab(self.im_compare_tab, "")
        self.DECT_tab = QWidget()
        self.DECT_tab.setObjectName(u"DECT_tab")
        self.gridLayout = QGridLayout(self.DECT_tab)
        self.gridLayout.setObjectName(u"gridLayout")
        self.DECTmenu = QTabWidget(self.DECT_tab)
        self.DECTmenu.setObjectName(u"DECTmenu")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_2 = QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.export_table_mat = QPushButton(self.tab)
        self.export_table_mat.setObjectName(u"export_table_mat")

        self.gridLayout_2.addWidget(self.export_table_mat, 7, 18, 1, 1)

        self.Load_csv_mat = QPushButton(self.tab)
        self.Load_csv_mat.setObjectName(u"Load_csv_mat")

        self.gridLayout_2.addWidget(self.Load_csv_mat, 7, 0, 1, 1)

        self.Zeff_m = QLineEdit(self.tab)
        self.Zeff_m.setObjectName(u"Zeff_m")
        self.Zeff_m.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.Zeff_m, 7, 16, 1, 1)

        self.checkBox_calSPR = QCheckBox(self.tab)
        self.checkBox_calSPR.setObjectName(u"checkBox_calSPR")
        self.checkBox_calSPR.setChecked(True)

        self.gridLayout_2.addWidget(self.checkBox_calSPR, 7, 13, 1, 1)

        self.line_3 = QFrame(self.tab)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line_3, 6, 0, 1, 20)

        self.remove_row_table_mat = QPushButton(self.tab)
        self.remove_row_table_mat.setObjectName(u"remove_row_table_mat")

        self.gridLayout_2.addWidget(self.remove_row_table_mat, 5, 0, 1, 1)

        self.lineEdit = QLineEdit(self.tab)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout_2.addWidget(self.lineEdit, 5, 16, 1, 1)

        self.lineEdit_41 = QLineEdit(self.tab)
        self.lineEdit_41.setObjectName(u"lineEdit_41")
        self.lineEdit_41.setEnabled(False)
        self.lineEdit_41.setFont(font)

        self.gridLayout_2.addWidget(self.lineEdit_41, 5, 10, 1, 1)

        self.DECT_list_02 = QComboBox(self.tab)
        self.DECT_list_02.setObjectName(u"DECT_list_02")

        self.gridLayout_2.addWidget(self.DECT_list_02, 5, 11, 1, 3)

        self.checkBox_cal_I = QCheckBox(self.tab)
        self.checkBox_cal_I.setObjectName(u"checkBox_cal_I")
        self.checkBox_cal_I.setChecked(True)

        self.gridLayout_2.addWidget(self.checkBox_cal_I, 7, 11, 1, 1)

        self.label_3 = QLabel(self.tab)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 7, 15, 1, 1)

        self.DECT_list_01 = QComboBox(self.tab)
        self.DECT_list_01.setObjectName(u"DECT_list_01")

        self.gridLayout_2.addWidget(self.DECT_list_01, 5, 6, 1, 4)

        self.reset_table_mat = QPushButton(self.tab)
        self.reset_table_mat.setObjectName(u"reset_table_mat")

        self.gridLayout_2.addWidget(self.reset_table_mat, 7, 19, 1, 1)

        self.add_row_table_mat = QPushButton(self.tab)
        self.add_row_table_mat.setObjectName(u"add_row_table_mat")

        self.gridLayout_2.addWidget(self.add_row_table_mat, 5, 2, 1, 1)

        self.lineEdit_8 = QLineEdit(self.tab)
        self.lineEdit_8.setObjectName(u"lineEdit_8")
        self.lineEdit_8.setEnabled(False)
        self.lineEdit_8.setFont(font)

        self.gridLayout_2.addWidget(self.lineEdit_8, 5, 4, 1, 1)

        self.mat_table_label = QLineEdit(self.tab)
        self.mat_table_label.setObjectName(u"mat_table_label")
        self.mat_table_label.setAutoFillBackground(False)

        self.gridLayout_2.addWidget(self.mat_table_label, 2, 0, 1, 20)

        self.get_HU_high = QPushButton(self.tab)
        self.get_HU_high.setObjectName(u"get_HU_high")

        self.gridLayout_2.addWidget(self.get_HU_high, 5, 15, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_2, 7, 7, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_4, 7, 12, 1, 1)

        self.checkBox_calRED = QCheckBox(self.tab)
        self.checkBox_calRED.setObjectName(u"checkBox_calRED")
        self.checkBox_calRED.setChecked(True)

        self.gridLayout_2.addWidget(self.checkBox_calRED, 7, 8, 1, 1)

        self.cal_mat_ref_info = QPushButton(self.tab)
        self.cal_mat_ref_info.setObjectName(u"cal_mat_ref_info")

        self.gridLayout_2.addWidget(self.cal_mat_ref_info, 7, 2, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_3, 7, 10, 1, 1)

        self.add_coll_table_mat = QPushButton(self.tab)
        self.add_coll_table_mat.setObjectName(u"add_coll_table_mat")

        self.gridLayout_2.addWidget(self.add_coll_table_mat, 5, 18, 1, 1)

        self.line_2 = QFrame(self.tab)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line_2, 4, 0, 1, 20)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_8, 7, 14, 1, 1)

        self.remove_coll_table_mat = QPushButton(self.tab)
        self.remove_coll_table_mat.setObjectName(u"remove_coll_table_mat")

        self.gridLayout_2.addWidget(self.remove_coll_table_mat, 5, 19, 1, 1)

        self.checkBox_calZeff = QCheckBox(self.tab)
        self.checkBox_calZeff.setObjectName(u"checkBox_calZeff")
        self.checkBox_calZeff.setChecked(True)

        self.gridLayout_2.addWidget(self.checkBox_calZeff, 7, 9, 1, 1)

        self.MatInfoTable = QTableWidget(self.tab)
        self.MatInfoTable.setObjectName(u"MatInfoTable")

        self.gridLayout_2.addWidget(self.MatInfoTable, 3, 0, 1, 20)

        self.lineEdit_47 = QLineEdit(self.tab)
        self.lineEdit_47.setObjectName(u"lineEdit_47")
        self.lineEdit_47.setEnabled(False)

        self.gridLayout_2.addWidget(self.lineEdit_47, 7, 4, 1, 1)

        self.Iv_water_ref = QDoubleSpinBox(self.tab)
        self.Iv_water_ref.setObjectName(u"Iv_water_ref")
        self.Iv_water_ref.setValue(78.000000000000000)

        self.gridLayout_2.addWidget(self.Iv_water_ref, 7, 6, 1, 1)

        self.DECTmenu.addTab(self.tab, "")
        self.IValue = QWidget()
        self.IValue.setObjectName(u"IValue")
        self.gridLayout_6 = QGridLayout(self.IValue)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.Ivalue_figure = QWidget(self.IValue)
        self.Ivalue_figure.setObjectName(u"Ivalue_figure")

        self.gridLayout_6.addWidget(self.Ivalue_figure, 1, 0, 25, 2)

        self.Ivalue_pre_calc_fit = QPushButton(self.IValue)
        self.Ivalue_pre_calc_fit.setObjectName(u"Ivalue_pre_calc_fit")

        self.gridLayout_6.addWidget(self.Ivalue_pre_calc_fit, 23, 3, 1, 1)

        self.I_value_b_coeff_calc = QLineEdit(self.IValue)
        self.I_value_b_coeff_calc.setObjectName(u"I_value_b_coeff_calc")

        self.gridLayout_6.addWidget(self.I_value_b_coeff_calc, 14, 3, 1, 1)

        self.Ivalue_calc_fit = QPushButton(self.IValue)
        self.Ivalue_calc_fit.setObjectName(u"Ivalue_calc_fit")

        self.gridLayout_6.addWidget(self.Ivalue_calc_fit, 7, 3, 1, 1)

        self.line_8 = QFrame(self.IValue)
        self.line_8.setObjectName(u"line_8")
        self.line_8.setFrameShape(QFrame.Shape.HLine)
        self.line_8.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_6.addWidget(self.line_8, 18, 3, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_6.addItem(self.verticalSpacer_2, 24, 3, 1, 1)

        self.lineEdit_3 = QLineEdit(self.IValue)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setEnabled(False)

        self.gridLayout_6.addWidget(self.lineEdit_3, 3, 3, 1, 1)

        self.I_value_z_up_lim = QLineEdit(self.IValue)
        self.I_value_z_up_lim.setObjectName(u"I_value_z_up_lim")
        self.I_value_z_up_lim.setEnabled(False)

        self.gridLayout_6.addWidget(self.I_value_z_up_lim, 19, 3, 1, 1)

        self.Ivalue_plot = QPushButton(self.IValue)
        self.Ivalue_plot.setObjectName(u"Ivalue_plot")

        self.gridLayout_6.addWidget(self.Ivalue_plot, 6, 3, 1, 1)

        self.lineEdit_2 = QLineEdit(self.IValue)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setEnabled(False)

        self.gridLayout_6.addWidget(self.lineEdit_2, 1, 3, 1, 1)

        self.I_value_z_up_values = QLineEdit(self.IValue)
        self.I_value_z_up_values.setObjectName(u"I_value_z_up_values")

        self.gridLayout_6.addWidget(self.I_value_z_up_values, 21, 3, 1, 1)

        self.line_4 = QFrame(self.IValue)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.VLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_6.addWidget(self.line_4, 0, 0, 1, 1)

        self.I_value_b_coeff = QLineEdit(self.IValue)
        self.I_value_b_coeff.setObjectName(u"I_value_b_coeff")
        self.I_value_b_coeff.setEnabled(False)

        self.gridLayout_6.addWidget(self.I_value_b_coeff, 13, 3, 1, 1)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer_6, 26, 1, 1, 1)

        self.line_6 = QFrame(self.IValue)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.Shape.HLine)
        self.line_6.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_6.addWidget(self.line_6, 12, 3, 1, 1)

        self.N_lin_fit = QSpinBox(self.IValue)
        self.N_lin_fit.setObjectName(u"N_lin_fit")
        self.N_lin_fit.setMinimum(1)
        self.N_lin_fit.setMaximum(5)
        self.N_lin_fit.setValue(2)

        self.gridLayout_6.addWidget(self.N_lin_fit, 2, 3, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer_5, 26, 0, 1, 1)

        self.line_7 = QFrame(self.IValue)
        self.line_7.setObjectName(u"line_7")
        self.line_7.setFrameShape(QFrame.Shape.HLine)
        self.line_7.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_6.addWidget(self.line_7, 15, 3, 1, 1)

        self.I_value_a_coeff_calc = QLineEdit(self.IValue)
        self.I_value_a_coeff_calc.setObjectName(u"I_value_a_coeff_calc")

        self.gridLayout_6.addWidget(self.I_value_a_coeff_calc, 11, 3, 1, 1)

        self.I_value_z_lw_lim = QLineEdit(self.IValue)
        self.I_value_z_lw_lim.setObjectName(u"I_value_z_lw_lim")
        self.I_value_z_lw_lim.setEnabled(False)

        self.gridLayout_6.addWidget(self.I_value_z_lw_lim, 16, 3, 1, 1)

        self.line_5 = QFrame(self.IValue)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.Shape.HLine)
        self.line_5.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_6.addWidget(self.line_5, 9, 3, 1, 1)

        self.I_value_z_lw_values = QLineEdit(self.IValue)
        self.I_value_z_lw_values.setObjectName(u"I_value_z_lw_values")

        self.gridLayout_6.addWidget(self.I_value_z_lw_values, 17, 3, 1, 1)

        self.Ivaluefit_method = QComboBox(self.IValue)
        self.Ivaluefit_method.setObjectName(u"Ivaluefit_method")

        self.gridLayout_6.addWidget(self.Ivaluefit_method, 26, 3, 1, 1)

        self.I_value_a_coeff = QLineEdit(self.IValue)
        self.I_value_a_coeff.setObjectName(u"I_value_a_coeff")
        self.I_value_a_coeff.setEnabled(False)

        self.gridLayout_6.addWidget(self.I_value_a_coeff, 10, 3, 1, 1)

        self.I_Fit_limits = QLineEdit(self.IValue)
        self.I_Fit_limits.setObjectName(u"I_Fit_limits")

        self.gridLayout_6.addWidget(self.I_Fit_limits, 5, 3, 1, 1)

        self.DECTmenu.addTab(self.IValue, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.gridLayout_35 = QGridLayout(self.tab_2)
        self.gridLayout_35.setObjectName(u"gridLayout_35")
        self.RED_method = QComboBox(self.tab_2)
        self.RED_method.setObjectName(u"RED_method")

        self.gridLayout_35.addWidget(self.RED_method, 5, 0, 1, 4)

        self.RED_fit_02_text = QLineEdit(self.tab_2)
        self.RED_fit_02_text.setObjectName(u"RED_fit_02_text")
        self.RED_fit_02_text.setFont(font1)

        self.gridLayout_35.addWidget(self.RED_fit_02_text, 5, 11, 1, 1)

        self.RED_fit_01 = QLineEdit(self.tab_2)
        self.RED_fit_01.setObjectName(u"RED_fit_01")
        self.RED_fit_01.setEnabled(False)
        self.RED_fit_01.setFont(font1)

        self.gridLayout_35.addWidget(self.RED_fit_01, 4, 10, 1, 1)

        self.RED_RMSE = QLineEdit(self.tab_2)
        self.RED_RMSE.setObjectName(u"RED_RMSE")
        self.RED_RMSE.setEnabled(False)
        self.RED_RMSE.setFont(font1)

        self.gridLayout_35.addWidget(self.RED_RMSE, 5, 8, 1, 1)

        self.RED_calc_cal = QPushButton(self.tab_2)
        self.RED_calc_cal.setObjectName(u"RED_calc_cal")

        self.gridLayout_35.addWidget(self.RED_calc_cal, 4, 1, 1, 1)

        self.RED_plot_02 = QWidget(self.tab_2)
        self.RED_plot_02.setObjectName(u"RED_plot_02")

        self.gridLayout_35.addWidget(self.RED_plot_02, 2, 9, 2, 5)

        self.RED_get_ref = QPushButton(self.tab_2)
        self.RED_get_ref.setObjectName(u"RED_get_ref")

        self.gridLayout_35.addWidget(self.RED_get_ref, 4, 0, 1, 1)

        self.RED_r_square = QLineEdit(self.tab_2)
        self.RED_r_square.setObjectName(u"RED_r_square")
        self.RED_r_square.setEnabled(False)
        self.RED_r_square.setFont(font1)

        self.gridLayout_35.addWidget(self.RED_r_square, 4, 8, 1, 1)

        self.RED_fit_01_text = QLineEdit(self.tab_2)
        self.RED_fit_01_text.setObjectName(u"RED_fit_01_text")
        self.RED_fit_01_text.setFont(font1)

        self.gridLayout_35.addWidget(self.RED_fit_01_text, 4, 11, 1, 1)

        self.RED_fit_03 = QLineEdit(self.tab_2)
        self.RED_fit_03.setObjectName(u"RED_fit_03")
        self.RED_fit_03.setEnabled(False)
        self.RED_fit_03.setFont(font1)

        self.gridLayout_35.addWidget(self.RED_fit_03, 4, 12, 1, 1)

        self.RED_plot_01 = QWidget(self.tab_2)
        self.RED_plot_01.setObjectName(u"RED_plot_01")

        self.gridLayout_35.addWidget(self.RED_plot_01, 0, 9, 2, 5)

        self.RED_r_square_text = QLineEdit(self.tab_2)
        self.RED_r_square_text.setObjectName(u"RED_r_square_text")
        self.RED_r_square_text.setFont(font1)

        self.gridLayout_35.addWidget(self.RED_r_square_text, 4, 9, 1, 1)

        self.RED_fit_03_text = QLineEdit(self.tab_2)
        self.RED_fit_03_text.setObjectName(u"RED_fit_03_text")
        self.RED_fit_03_text.setFont(font1)

        self.gridLayout_35.addWidget(self.RED_fit_03_text, 4, 13, 1, 1)

        self.tableRED = QTableWidget(self.tab_2)
        self.tableRED.setObjectName(u"tableRED")

        self.gridLayout_35.addWidget(self.tableRED, 0, 0, 4, 9)

        self.RED_fit_02 = QLineEdit(self.tab_2)
        self.RED_fit_02.setObjectName(u"RED_fit_02")
        self.RED_fit_02.setEnabled(False)
        self.RED_fit_02.setFont(font1)

        self.gridLayout_35.addWidget(self.RED_fit_02, 5, 10, 1, 1)

        self.RED_RMSE_text = QLineEdit(self.tab_2)
        self.RED_RMSE_text.setObjectName(u"RED_RMSE_text")
        self.RED_RMSE_text.setFont(font1)

        self.gridLayout_35.addWidget(self.RED_RMSE_text, 5, 9, 1, 1)

        self.DECTmenu.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.gridLayout_39 = QGridLayout(self.tab_3)
        self.gridLayout_39.setObjectName(u"gridLayout_39")
        self.Zeff_r_square = QLineEdit(self.tab_3)
        self.Zeff_r_square.setObjectName(u"Zeff_r_square")
        self.Zeff_r_square.setEnabled(False)
        self.Zeff_r_square.setFont(font1)

        self.gridLayout_39.addWidget(self.Zeff_r_square, 2, 5, 1, 1)

        self.Zeff_RMSE = QLineEdit(self.tab_3)
        self.Zeff_RMSE.setObjectName(u"Zeff_RMSE")
        self.Zeff_RMSE.setEnabled(False)
        self.Zeff_RMSE.setFont(font1)

        self.gridLayout_39.addWidget(self.Zeff_RMSE, 3, 5, 1, 1)

        self.Zeff_plot_1 = QWidget(self.tab_3)
        self.Zeff_plot_1.setObjectName(u"Zeff_plot_1")

        self.gridLayout_39.addWidget(self.Zeff_plot_1, 0, 7, 1, 5)

        self.Zeff_RMSE_text = QLineEdit(self.tab_3)
        self.Zeff_RMSE_text.setObjectName(u"Zeff_RMSE_text")
        self.Zeff_RMSE_text.setFont(font1)

        self.gridLayout_39.addWidget(self.Zeff_RMSE_text, 3, 7, 1, 1)

        self.Zeff_fit_01_text = QLineEdit(self.tab_3)
        self.Zeff_fit_01_text.setObjectName(u"Zeff_fit_01_text")
        self.Zeff_fit_01_text.setFont(font1)

        self.gridLayout_39.addWidget(self.Zeff_fit_01_text, 2, 9, 1, 1)

        self.Zeff_fit_1 = QLineEdit(self.tab_3)
        self.Zeff_fit_1.setObjectName(u"Zeff_fit_1")
        self.Zeff_fit_1.setEnabled(False)
        self.Zeff_fit_1.setFont(font1)

        self.gridLayout_39.addWidget(self.Zeff_fit_1, 2, 8, 1, 1)

        self.Zeff_get_ref = QPushButton(self.tab_3)
        self.Zeff_get_ref.setObjectName(u"Zeff_get_ref")

        self.gridLayout_39.addWidget(self.Zeff_get_ref, 2, 0, 1, 1)

        self.Zeff_fit_2 = QLineEdit(self.tab_3)
        self.Zeff_fit_2.setObjectName(u"Zeff_fit_2")
        self.Zeff_fit_2.setEnabled(False)
        self.Zeff_fit_2.setFont(font1)

        self.gridLayout_39.addWidget(self.Zeff_fit_2, 2, 10, 1, 1)

        self.Zeff_calc_cal = QPushButton(self.tab_3)
        self.Zeff_calc_cal.setObjectName(u"Zeff_calc_cal")

        self.gridLayout_39.addWidget(self.Zeff_calc_cal, 2, 1, 1, 1)

        self.tableZeff = QTableWidget(self.tab_3)
        self.tableZeff.setObjectName(u"tableZeff")

        self.gridLayout_39.addWidget(self.tableZeff, 0, 0, 2, 6)

        self.Zeff_method = QComboBox(self.tab_3)
        self.Zeff_method.setObjectName(u"Zeff_method")

        self.gridLayout_39.addWidget(self.Zeff_method, 3, 0, 1, 5)

        self.Zeff_fit_02_text = QLineEdit(self.tab_3)
        self.Zeff_fit_02_text.setObjectName(u"Zeff_fit_02_text")
        self.Zeff_fit_02_text.setFont(font1)

        self.gridLayout_39.addWidget(self.Zeff_fit_02_text, 2, 11, 1, 1)

        self.Zeff_plot_2 = QWidget(self.tab_3)
        self.Zeff_plot_2.setObjectName(u"Zeff_plot_2")

        self.gridLayout_39.addWidget(self.Zeff_plot_2, 1, 7, 1, 5)

        self.Zeff_r_square_text = QLineEdit(self.tab_3)
        self.Zeff_r_square_text.setObjectName(u"Zeff_r_square_text")
        self.Zeff_r_square_text.setFont(font1)

        self.gridLayout_39.addWidget(self.Zeff_r_square_text, 2, 7, 1, 1)

        self.DECTmenu.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.gridLayout_36 = QGridLayout(self.tab_4)
        self.gridLayout_36.setObjectName(u"gridLayout_36")
        self.Iv_calc_cal = QPushButton(self.tab_4)
        self.Iv_calc_cal.setObjectName(u"Iv_calc_cal")

        self.gridLayout_36.addWidget(self.Iv_calc_cal, 3, 1, 1, 1)

        self.Ivalue_RMSE_text = QLineEdit(self.tab_4)
        self.Ivalue_RMSE_text.setObjectName(u"Ivalue_RMSE_text")
        self.Ivalue_RMSE_text.setFont(font1)

        self.gridLayout_36.addWidget(self.Ivalue_RMSE_text, 3, 3, 1, 1)

        self.Ivalue_plot_1 = QWidget(self.tab_4)
        self.Ivalue_plot_1.setObjectName(u"Ivalue_plot_1")

        self.gridLayout_36.addWidget(self.Ivalue_plot_1, 0, 3, 1, 4)

        self.Ivalue_plot_2 = QWidget(self.tab_4)
        self.Ivalue_plot_2.setObjectName(u"Ivalue_plot_2")

        self.gridLayout_36.addWidget(self.Ivalue_plot_2, 1, 3, 1, 4)

        self.Ivalue_RMSE = QLineEdit(self.tab_4)
        self.Ivalue_RMSE.setObjectName(u"Ivalue_RMSE")
        self.Ivalue_RMSE.setEnabled(False)
        self.Ivalue_RMSE.setFont(font1)

        self.gridLayout_36.addWidget(self.Ivalue_RMSE, 3, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_36.addItem(self.horizontalSpacer, 3, 6, 1, 1)

        self.Iv_get_ref = QPushButton(self.tab_4)
        self.Iv_get_ref.setObjectName(u"Iv_get_ref")

        self.gridLayout_36.addWidget(self.Iv_get_ref, 3, 0, 1, 1)

        self.tableIv = QTableWidget(self.tab_4)
        self.tableIv.setObjectName(u"tableIv")

        self.gridLayout_36.addWidget(self.tableIv, 0, 0, 2, 3)

        self.horizontalSpacer_26 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_36.addItem(self.horizontalSpacer_26, 3, 4, 1, 1)

        self.DECTmenu.addTab(self.tab_4, "")
        self.tab_7 = QWidget()
        self.tab_7.setObjectName(u"tab_7")
        self.gridLayout_37 = QGridLayout(self.tab_7)
        self.gridLayout_37.setObjectName(u"gridLayout_37")
        self.SPR_plot_1 = QWidget(self.tab_7)
        self.SPR_plot_1.setObjectName(u"SPR_plot_1")

        self.gridLayout_37.addWidget(self.SPR_plot_1, 1, 4, 1, 4)

        self.SPR_ref_energy = QDoubleSpinBox(self.tab_7)
        self.SPR_ref_energy.setObjectName(u"SPR_ref_energy")
        self.SPR_ref_energy.setMaximum(9999.989999999999782)
        self.SPR_ref_energy.setValue(100.000000000000000)

        self.gridLayout_37.addWidget(self.SPR_ref_energy, 2, 6, 1, 1)

        self.lineEdit_46 = QLineEdit(self.tab_7)
        self.lineEdit_46.setObjectName(u"lineEdit_46")
        self.lineEdit_46.setEnabled(False)

        self.gridLayout_37.addWidget(self.lineEdit_46, 2, 3, 1, 1)

        self.SPR_get_ref = QPushButton(self.tab_7)
        self.SPR_get_ref.setObjectName(u"SPR_get_ref")

        self.gridLayout_37.addWidget(self.SPR_get_ref, 2, 0, 1, 1)

        self.SPR_calc_cal = QPushButton(self.tab_7)
        self.SPR_calc_cal.setObjectName(u"SPR_calc_cal")

        self.gridLayout_37.addWidget(self.SPR_calc_cal, 2, 1, 1, 1)

        self.SPR_RMSE_text = QLineEdit(self.tab_7)
        self.SPR_RMSE_text.setObjectName(u"SPR_RMSE_text")

        self.gridLayout_37.addWidget(self.SPR_RMSE_text, 2, 4, 1, 1)

        self.SPR_plot_2 = QWidget(self.tab_7)
        self.SPR_plot_2.setObjectName(u"SPR_plot_2")

        self.gridLayout_37.addWidget(self.SPR_plot_2, 0, 4, 1, 4)

        self.lineEdit_42 = QLineEdit(self.tab_7)
        self.lineEdit_42.setObjectName(u"lineEdit_42")
        self.lineEdit_42.setEnabled(False)

        self.gridLayout_37.addWidget(self.lineEdit_42, 2, 5, 1, 1)

        self.horizontalSpacer_27 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_37.addItem(self.horizontalSpacer_27, 2, 7, 1, 1)

        self.tableSPR = QTableWidget(self.tab_7)
        self.tableSPR.setObjectName(u"tableSPR")

        self.gridLayout_37.addWidget(self.tableSPR, 0, 0, 2, 4)

        self.SPR_particle = QComboBox(self.tab_7)
        self.SPR_particle.setObjectName(u"SPR_particle")

        self.gridLayout_37.addWidget(self.SPR_particle, 2, 2, 1, 1)

        self.DECTmenu.addTab(self.tab_7, "")
        self.tab_8 = QWidget()
        self.tab_8.setObjectName(u"tab_8")
        self.gridLayout_40 = QGridLayout(self.tab_8)
        self.gridLayout_40.setObjectName(u"gridLayout_40")
        self.groupBox_10 = QGroupBox(self.tab_8)
        self.groupBox_10.setObjectName(u"groupBox_10")
        self.gridLayout_38 = QGridLayout(self.groupBox_10)
        self.gridLayout_38.setObjectName(u"gridLayout_38")
        self.Create_DECT_Images = QPushButton(self.groupBox_10)
        self.Create_DECT_Images.setObjectName(u"Create_DECT_Images")

        self.gridLayout_38.addWidget(self.Create_DECT_Images, 0, 0, 1, 5)

        self.checkBox_Im_RED = QCheckBox(self.groupBox_10)
        self.checkBox_Im_RED.setObjectName(u"checkBox_Im_RED")
        self.checkBox_Im_RED.setChecked(True)

        self.gridLayout_38.addWidget(self.checkBox_Im_RED, 1, 0, 1, 1)

        self.checkBox_Im_Zeff = QCheckBox(self.groupBox_10)
        self.checkBox_Im_Zeff.setObjectName(u"checkBox_Im_Zeff")
        self.checkBox_Im_Zeff.setChecked(True)

        self.gridLayout_38.addWidget(self.checkBox_Im_Zeff, 1, 1, 1, 1)

        self.checkBox_Im_SPR = QCheckBox(self.groupBox_10)
        self.checkBox_Im_SPR.setObjectName(u"checkBox_Im_SPR")
        self.checkBox_Im_SPR.setChecked(True)

        self.gridLayout_38.addWidget(self.checkBox_Im_SPR, 1, 4, 1, 1)

        self.checkBox_Im_I = QCheckBox(self.groupBox_10)
        self.checkBox_Im_I.setObjectName(u"checkBox_Im_I")
        self.checkBox_Im_I.setChecked(True)

        self.gridLayout_38.addWidget(self.checkBox_Im_I, 1, 3, 1, 1)


        self.gridLayout_40.addWidget(self.groupBox_10, 3, 0, 3, 1)

        self.groupBox_9 = QGroupBox(self.tab_8)
        self.groupBox_9.setObjectName(u"groupBox_9")
        self.gridLayout_41 = QGridLayout(self.groupBox_9)
        self.gridLayout_41.setObjectName(u"gridLayout_41")
        self.checkBox_newScplot = QCheckBox(self.groupBox_9)
        self.checkBox_newScplot.setObjectName(u"checkBox_newScplot")

        self.gridLayout_41.addWidget(self.checkBox_newScplot, 2, 11, 1, 1)

        self.horizontalSpacer_39 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_41.addItem(self.horizontalSpacer_39, 1, 6, 1, 1)

        self.DECT_exp_scatt_data = QCheckBox(self.groupBox_9)
        self.DECT_exp_scatt_data.setObjectName(u"DECT_exp_scatt_data")

        self.gridLayout_41.addWidget(self.DECT_exp_scatt_data, 2, 13, 1, 1)

        self.DECT_sct_p_size = QSpinBox(self.groupBox_9)
        self.DECT_sct_p_size.setObjectName(u"DECT_sct_p_size")
        self.DECT_sct_p_size.setMinimum(1)
        self.DECT_sct_p_size.setValue(5)

        self.gridLayout_41.addWidget(self.DECT_sct_p_size, 3, 10, 1, 1)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_41.addItem(self.verticalSpacer_7, 0, 13, 1, 1)

        self.horizontalSpacer_37 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_41.addItem(self.horizontalSpacer_37, 1, 4, 1, 1)

        self.horizontalSpacer_33 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_41.addItem(self.horizontalSpacer_33, 1, 0, 1, 1)

        self.horizontalSpacer_40 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_41.addItem(self.horizontalSpacer_40, 1, 7, 1, 1)

        self.DECT_scatt_N = QSpinBox(self.groupBox_9)
        self.DECT_scatt_N.setObjectName(u"DECT_scatt_N")
        self.DECT_scatt_N.setMinimum(1)
        self.DECT_scatt_N.setMaximum(20000)
        self.DECT_scatt_N.setValue(100)

        self.gridLayout_41.addWidget(self.DECT_scatt_N, 3, 11, 1, 1)

        self.DECT_Scatt_Ax_View = QWidget(self.groupBox_9)
        self.DECT_Scatt_Ax_View.setObjectName(u"DECT_Scatt_Ax_View")

        self.gridLayout_41.addWidget(self.DECT_Scatt_Ax_View, 0, 0, 1, 13)

        self.horizontalSpacer_35 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_41.addItem(self.horizontalSpacer_35, 1, 2, 1, 1)

        self.horizontalSpacer_41 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_41.addItem(self.horizontalSpacer_41, 1, 8, 1, 1)

        self.lineEdit_50 = QLineEdit(self.groupBox_9)
        self.lineEdit_50.setObjectName(u"lineEdit_50")
        self.lineEdit_50.setEnabled(False)

        self.gridLayout_41.addWidget(self.lineEdit_50, 2, 10, 1, 1)

        self.horizontalSpacer_38 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_41.addItem(self.horizontalSpacer_38, 1, 5, 1, 1)

        self.plot_roi_scatter = QPushButton(self.groupBox_9)
        self.plot_roi_scatter.setObjectName(u"plot_roi_scatter")

        self.gridLayout_41.addWidget(self.plot_roi_scatter, 3, 13, 1, 1)

        self.horizontalSpacer_34 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_41.addItem(self.horizontalSpacer_34, 1, 1, 1, 1)

        self.horizontalSpacer_36 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_41.addItem(self.horizontalSpacer_36, 1, 3, 1, 1)

        self.horizontalSpacer_42 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_41.addItem(self.horizontalSpacer_42, 1, 9, 1, 1)

        self.lineEdit_49 = QLineEdit(self.groupBox_9)
        self.lineEdit_49.setObjectName(u"lineEdit_49")
        self.lineEdit_49.setEnabled(False)

        self.gridLayout_41.addWidget(self.lineEdit_49, 2, 5, 1, 5)

        self.scatter_plot_im_02 = QComboBox(self.groupBox_9)
        self.scatter_plot_im_02.setObjectName(u"scatter_plot_im_02")

        self.gridLayout_41.addWidget(self.scatter_plot_im_02, 3, 5, 1, 5)

        self.scatter_plot_im_01 = QComboBox(self.groupBox_9)
        self.scatter_plot_im_01.setObjectName(u"scatter_plot_im_01")

        self.gridLayout_41.addWidget(self.scatter_plot_im_01, 3, 0, 1, 5)

        self.lineEdit_48 = QLineEdit(self.groupBox_9)
        self.lineEdit_48.setObjectName(u"lineEdit_48")
        self.lineEdit_48.setEnabled(False)

        self.gridLayout_41.addWidget(self.lineEdit_48, 2, 0, 1, 5)


        self.gridLayout_40.addWidget(self.groupBox_9, 2, 0, 1, 8)

        self.export_all_DECT_tables = QPushButton(self.tab_8)
        self.export_all_DECT_tables.setObjectName(u"export_all_DECT_tables")

        self.gridLayout_40.addWidget(self.export_all_DECT_tables, 3, 2, 1, 1)

        self.horizontalSpacer_31 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_40.addItem(self.horizontalSpacer_31, 3, 7, 1, 1)

        self.horizontalSpacer_28 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_40.addItem(self.horizontalSpacer_28, 3, 4, 1, 1)

        self.horizontalSpacer_29 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_40.addItem(self.horizontalSpacer_29, 3, 5, 1, 1)

        self.horizontalSpacer_30 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_40.addItem(self.horizontalSpacer_30, 3, 6, 1, 1)

        self.horizontalSpacer_32 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_40.addItem(self.horizontalSpacer_32, 3, 8, 1, 1)

        self.DECT_exp_fit_par = QPushButton(self.tab_8)
        self.DECT_exp_fit_par.setObjectName(u"DECT_exp_fit_par")

        self.gridLayout_40.addWidget(self.DECT_exp_fit_par, 4, 2, 1, 1)

        self.DECT_load_fit_par = QPushButton(self.tab_8)
        self.DECT_load_fit_par.setObjectName(u"DECT_load_fit_par")

        self.gridLayout_40.addWidget(self.DECT_load_fit_par, 5, 2, 1, 1)

        self.DECTmenu.addTab(self.tab_8, "")

        self.gridLayout.addWidget(self.DECTmenu, 1, 0, 1, 1)

        self.tabModules.addTab(self.DECT_tab, "")
        self.Plan_tab = QWidget()
        self.Plan_tab.setObjectName(u"Plan_tab")
        self.gridLayout_42 = QGridLayout(self.Plan_tab)
        self.gridLayout_42.setObjectName(u"gridLayout_42")
        self.Plan_tabs = QTabWidget(self.Plan_tab)
        self.Plan_tabs.setObjectName(u"Plan_tabs")
        self.Brachy_plan_tab = QWidget()
        self.Brachy_plan_tab.setObjectName(u"Brachy_plan_tab")
        self.gridLayout_43 = QGridLayout(self.Brachy_plan_tab)
        self.gridLayout_43.setObjectName(u"gridLayout_43")
        self.BrachytabWidget_2 = QTabWidget(self.Brachy_plan_tab)
        self.BrachytabWidget_2.setObjectName(u"BrachytabWidget_2")
        self.Br_tab_42 = QWidget()
        self.Br_tab_42.setObjectName(u"Br_tab_42")
        self.gridLayout_48 = QGridLayout(self.Br_tab_42)
        self.gridLayout_48.setObjectName(u"gridLayout_48")
        self.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_48.addItem(self.verticalSpacer_9, 0, 0, 1, 1)

        self.brachy_ax_01 = QWidget(self.Br_tab_42)
        self.brachy_ax_01.setObjectName(u"brachy_ax_01")

        self.gridLayout_48.addWidget(self.brachy_ax_01, 0, 1, 2, 5)

        self.brachy_ax_02 = QWidget(self.Br_tab_42)
        self.brachy_ax_02.setObjectName(u"brachy_ax_02")

        self.gridLayout_48.addWidget(self.brachy_ax_02, 0, 6, 2, 4)

        self.verticalSpacer_11 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_48.addItem(self.verticalSpacer_11, 1, 0, 1, 1)

        self.verticalSpacer_10 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_48.addItem(self.verticalSpacer_10, 2, 0, 1, 1)

        self.brachy_table_02 = QTableWidget(self.Br_tab_42)
        self.brachy_table_02.setObjectName(u"brachy_table_02")
        self.brachy_table_02.setFont(font1)

        self.gridLayout_48.addWidget(self.brachy_table_02, 2, 1, 2, 5)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_48.addItem(self.verticalSpacer_8, 3, 0, 1, 1)

        self.lineEdit_51 = QLineEdit(self.Br_tab_42)
        self.lineEdit_51.setObjectName(u"lineEdit_51")
        self.lineEdit_51.setEnabled(False)
        self.lineEdit_51.setFont(font)

        self.gridLayout_48.addWidget(self.lineEdit_51, 4, 1, 1, 1)

        self.brachy_ch_time = QLineEdit(self.Br_tab_42)
        self.brachy_ch_time.setObjectName(u"brachy_ch_time")
        self.brachy_ch_time.setEnabled(False)
        self.brachy_ch_time.setFont(font)

        self.gridLayout_48.addWidget(self.brachy_ch_time, 4, 2, 1, 1)

        self.lineEdit_52 = QLineEdit(self.Br_tab_42)
        self.lineEdit_52.setObjectName(u"lineEdit_52")
        self.lineEdit_52.setEnabled(False)
        self.lineEdit_52.setFont(font)

        self.gridLayout_48.addWidget(self.lineEdit_52, 4, 3, 1, 1)

        self.brachy_total_time = QLineEdit(self.Br_tab_42)
        self.brachy_total_time.setObjectName(u"brachy_total_time")
        self.brachy_total_time.setEnabled(False)
        self.brachy_total_time.setFont(font)

        self.gridLayout_48.addWidget(self.brachy_total_time, 4, 4, 1, 1)

        self.lineEdit_54 = QLineEdit(self.Br_tab_42)
        self.lineEdit_54.setObjectName(u"lineEdit_54")
        self.lineEdit_54.setEnabled(False)
        self.lineEdit_54.setFont(font)

        self.gridLayout_48.addWidget(self.lineEdit_54, 4, 5, 1, 1)

        self.brachy_plan_Ac = QLineEdit(self.Br_tab_42)
        self.brachy_plan_Ac.setObjectName(u"brachy_plan_Ac")
        self.brachy_plan_Ac.setEnabled(False)
        self.brachy_plan_Ac.setFont(font)

        self.gridLayout_48.addWidget(self.brachy_plan_Ac, 4, 6, 1, 1)

        self.lineEdit_53 = QLineEdit(self.Br_tab_42)
        self.lineEdit_53.setObjectName(u"lineEdit_53")
        self.lineEdit_53.setEnabled(False)
        self.lineEdit_53.setFont(font)

        self.gridLayout_48.addWidget(self.lineEdit_53, 4, 7, 1, 1)

        self.brachy_N_channels = QLineEdit(self.Br_tab_42)
        self.brachy_N_channels.setObjectName(u"brachy_N_channels")
        self.brachy_N_channels.setEnabled(False)
        self.brachy_N_channels.setFont(font)

        self.gridLayout_48.addWidget(self.brachy_N_channels, 4, 8, 1, 1)

        self.pushButton = QPushButton(self.Br_tab_42)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout_48.addWidget(self.pushButton, 4, 9, 1, 1)

        self.lineEdit_55 = QLineEdit(self.Br_tab_42)
        self.lineEdit_55.setObjectName(u"lineEdit_55")
        self.lineEdit_55.setEnabled(False)
        self.lineEdit_55.setFont(font)

        self.gridLayout_48.addWidget(self.lineEdit_55, 5, 1, 1, 1)

        self.brachy_spinBox_02 = QSpinBox(self.Br_tab_42)
        self.brachy_spinBox_02.setObjectName(u"brachy_spinBox_02")
        self.brachy_spinBox_02.setFont(font)

        self.gridLayout_48.addWidget(self.brachy_spinBox_02, 5, 2, 1, 1)

        self.brachy_combobox_02 = QComboBox(self.Br_tab_42)
        self.brachy_combobox_02.setObjectName(u"brachy_combobox_02")

        self.gridLayout_48.addWidget(self.brachy_combobox_02, 5, 3, 1, 1)

        self.checkBox_show_dw_plot = QCheckBox(self.Br_tab_42)
        self.checkBox_show_dw_plot.setObjectName(u"checkBox_show_dw_plot")
        self.checkBox_show_dw_plot.setFont(font)
        self.checkBox_show_dw_plot.setChecked(True)

        self.gridLayout_48.addWidget(self.checkBox_show_dw_plot, 5, 6, 1, 1)

        self.checkBox_show_ch_plot = QCheckBox(self.Br_tab_42)
        self.checkBox_show_ch_plot.setObjectName(u"checkBox_show_ch_plot")
        self.checkBox_show_ch_plot.setFont(font)
        self.checkBox_show_ch_plot.setChecked(True)

        self.gridLayout_48.addWidget(self.checkBox_show_ch_plot, 5, 7, 1, 1)

        self.checkBox_dw_ch_plot = QCheckBox(self.Br_tab_42)
        self.checkBox_dw_ch_plot.setObjectName(u"checkBox_dw_ch_plot")
        self.checkBox_dw_ch_plot.setFont(font)
        self.checkBox_dw_ch_plot.setChecked(True)

        self.gridLayout_48.addWidget(self.checkBox_dw_ch_plot, 5, 8, 1, 1)

        self.brachy_ch_plot = QPushButton(self.Br_tab_42)
        self.brachy_ch_plot.setObjectName(u"brachy_ch_plot")

        self.gridLayout_48.addWidget(self.brachy_ch_plot, 5, 9, 1, 1)

        self.groupBox_11 = QGroupBox(self.Br_tab_42)
        self.groupBox_11.setObjectName(u"groupBox_11")
        self.gridLayout_46 = QGridLayout(self.groupBox_11)
        self.gridLayout_46.setObjectName(u"gridLayout_46")
        self.brachy_ch_line_width = QDoubleSpinBox(self.groupBox_11)
        self.brachy_ch_line_width.setObjectName(u"brachy_ch_line_width")
        self.brachy_ch_line_width.setFont(font)
        self.brachy_ch_line_width.setValue(1.000000000000000)

        self.gridLayout_46.addWidget(self.brachy_ch_line_width, 1, 3, 1, 1)

        self.brachy_ch_p1_color = QComboBox(self.groupBox_11)
        self.brachy_ch_p1_color.setObjectName(u"brachy_ch_p1_color")
        self.brachy_ch_p1_color.setFont(font)

        self.gridLayout_46.addWidget(self.brachy_ch_p1_color, 7, 2, 1, 1)

        self.lineEdit_60 = QLineEdit(self.groupBox_11)
        self.lineEdit_60.setObjectName(u"lineEdit_60")
        self.lineEdit_60.setEnabled(False)
        self.lineEdit_60.setFont(font)

        self.gridLayout_46.addWidget(self.lineEdit_60, 2, 2, 1, 1)

        self.brachy_dw_size = QSpinBox(self.groupBox_11)
        self.brachy_dw_size.setObjectName(u"brachy_dw_size")
        self.brachy_dw_size.setFont(font)
        self.brachy_dw_size.setValue(15)

        self.gridLayout_46.addWidget(self.brachy_dw_size, 1, 1, 1, 1)

        self.lineEdit_57 = QLineEdit(self.groupBox_11)
        self.lineEdit_57.setObjectName(u"lineEdit_57")
        self.lineEdit_57.setEnabled(False)
        self.lineEdit_57.setFont(font)

        self.gridLayout_46.addWidget(self.lineEdit_57, 1, 2, 1, 1)

        self.brachy_ch_size = QDoubleSpinBox(self.groupBox_11)
        self.brachy_ch_size.setObjectName(u"brachy_ch_size")
        self.brachy_ch_size.setFont(font)
        self.brachy_ch_size.setValue(20.000000000000000)

        self.gridLayout_46.addWidget(self.brachy_ch_size, 4, 3, 1, 1)

        self.lineEdit_56 = QLineEdit(self.groupBox_11)
        self.lineEdit_56.setObjectName(u"lineEdit_56")
        self.lineEdit_56.setEnabled(False)
        self.lineEdit_56.setFont(font)

        self.gridLayout_46.addWidget(self.lineEdit_56, 1, 0, 1, 1)

        self.lineEdit_58 = QLineEdit(self.groupBox_11)
        self.lineEdit_58.setObjectName(u"lineEdit_58")
        self.lineEdit_58.setEnabled(False)
        self.lineEdit_58.setFont(font)

        self.gridLayout_46.addWidget(self.lineEdit_58, 4, 2, 1, 1)

        self.brachy_line_color = QComboBox(self.groupBox_11)
        self.brachy_line_color.setObjectName(u"brachy_line_color")
        self.brachy_line_color.setFont(font)

        self.gridLayout_46.addWidget(self.brachy_line_color, 3, 2, 1, 1)

        self.lineEdit_59 = QLineEdit(self.groupBox_11)
        self.lineEdit_59.setObjectName(u"lineEdit_59")
        self.lineEdit_59.setEnabled(False)
        self.lineEdit_59.setFont(font)

        self.gridLayout_46.addWidget(self.lineEdit_59, 2, 0, 1, 1)

        self.brachy_dw_color = QComboBox(self.groupBox_11)
        self.brachy_dw_color.setObjectName(u"brachy_dw_color")
        self.brachy_dw_color.setFont(font)

        self.gridLayout_46.addWidget(self.brachy_dw_color, 3, 0, 1, 1)

        self.lineEdit_61 = QLineEdit(self.groupBox_11)
        self.lineEdit_61.setObjectName(u"lineEdit_61")
        self.lineEdit_61.setEnabled(False)
        self.lineEdit_61.setFont(font)

        self.gridLayout_46.addWidget(self.lineEdit_61, 5, 2, 1, 1)

        self.lineEdit_62 = QLineEdit(self.groupBox_11)
        self.lineEdit_62.setObjectName(u"lineEdit_62")
        self.lineEdit_62.setEnabled(False)

        self.gridLayout_46.addWidget(self.lineEdit_62, 4, 0, 1, 1)

        self.brachy_struc_show_01 = QComboBox(self.groupBox_11)
        self.brachy_struc_show_01.setObjectName(u"brachy_struc_show_01")
        self.brachy_struc_show_01.setFont(font)

        self.gridLayout_46.addWidget(self.brachy_struc_show_01, 5, 0, 1, 1)

        self.brachy_struc_show_02 = QComboBox(self.groupBox_11)
        self.brachy_struc_show_02.setObjectName(u"brachy_struc_show_02")
        self.brachy_struc_show_02.setFont(font)

        self.gridLayout_46.addWidget(self.brachy_struc_show_02, 7, 0, 1, 1)


        self.gridLayout_48.addWidget(self.groupBox_11, 2, 6, 1, 4)

        self.Brachy_groupBox_12 = QGroupBox(self.Br_tab_42)
        self.Brachy_groupBox_12.setObjectName(u"Brachy_groupBox_12")
        self.gridLayout_49 = QGridLayout(self.Brachy_groupBox_12)
        self.gridLayout_49.setObjectName(u"gridLayout_49")
        self.Brachy_setalldwtimes = QPushButton(self.Brachy_groupBox_12)
        self.Brachy_setalldwtimes.setObjectName(u"Brachy_setalldwtimes")

        self.gridLayout_49.addWidget(self.Brachy_setalldwtimes, 1, 0, 1, 1)

        self.Brachy_create_new_channel = QPushButton(self.Brachy_groupBox_12)
        self.Brachy_create_new_channel.setObjectName(u"Brachy_create_new_channel")

        self.gridLayout_49.addWidget(self.Brachy_create_new_channel, 1, 1, 1, 1)

        self.Brachy_DuplicateChannel = QPushButton(self.Brachy_groupBox_12)
        self.Brachy_DuplicateChannel.setObjectName(u"Brachy_DuplicateChannel")

        self.gridLayout_49.addWidget(self.Brachy_DuplicateChannel, 2, 1, 1, 1)

        self.Brachy_setIDD_distance = QPushButton(self.Brachy_groupBox_12)
        self.Brachy_setIDD_distance.setObjectName(u"Brachy_setIDD_distance")

        self.gridLayout_49.addWidget(self.Brachy_setIDD_distance, 2, 0, 1, 1)

        self.Brachy_DeadSpace_Offset = QPushButton(self.Brachy_groupBox_12)
        self.Brachy_DeadSpace_Offset.setObjectName(u"Brachy_DeadSpace_Offset")

        self.gridLayout_49.addWidget(self.Brachy_DeadSpace_Offset, 3, 0, 1, 1)

        self.Brachy_DeleteChannel = QPushButton(self.Brachy_groupBox_12)
        self.Brachy_DeleteChannel.setObjectName(u"Brachy_DeleteChannel")

        self.gridLayout_49.addWidget(self.Brachy_DeleteChannel, 4, 1, 1, 1)

        self.Brachy_Calcualte_TG43 = QPushButton(self.Brachy_groupBox_12)
        self.Brachy_Calcualte_TG43.setObjectName(u"Brachy_Calcualte_TG43")

        self.gridLayout_49.addWidget(self.Brachy_Calcualte_TG43, 3, 1, 1, 1)


        self.gridLayout_48.addWidget(self.Brachy_groupBox_12, 3, 6, 1, 4)

        self.BrachytabWidget_2.addTab(self.Br_tab_42, "")
        self.Br_tab_43 = QWidget()
        self.Br_tab_43.setObjectName(u"Br_tab_43")
        self.gridLayout_51 = QGridLayout(self.Br_tab_43)
        self.gridLayout_51.setObjectName(u"gridLayout_51")
        self.brachy_save_tg43_source = QPushButton(self.Br_tab_43)
        self.brachy_save_tg43_source.setObjectName(u"brachy_save_tg43_source")

        self.gridLayout_51.addWidget(self.brachy_save_tg43_source, 4, 0, 1, 1)

        self.horizontalSpacer_48 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_51.addItem(self.horizontalSpacer_48, 2, 1, 1, 1)

        self.Brachy_load_sources = QPushButton(self.Br_tab_43)
        self.Brachy_load_sources.setObjectName(u"Brachy_load_sources")

        self.gridLayout_51.addWidget(self.Brachy_load_sources, 3, 0, 1, 1)

        self.horizontalSpacer_49 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_51.addItem(self.horizontalSpacer_49, 2, 2, 1, 1)

        self.brachy_source_list = QComboBox(self.Br_tab_43)
        self.brachy_source_list.setObjectName(u"brachy_source_list")

        self.gridLayout_51.addWidget(self.brachy_source_list, 3, 1, 1, 1)

        self.horizontalSpacer_51 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_51.addItem(self.horizontalSpacer_51, 2, 3, 1, 1)

        self.brachy_delete_source = QPushButton(self.Br_tab_43)
        self.brachy_delete_source.setObjectName(u"brachy_delete_source")

        self.gridLayout_51.addWidget(self.brachy_delete_source, 4, 1, 1, 1)

        self.horizontalSpacer_44 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_51.addItem(self.horizontalSpacer_44, 2, 0, 1, 1)

        self.horizontalSpacer_50 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_51.addItem(self.horizontalSpacer_50, 2, 4, 1, 1)

        self.tabWidget_2 = QTabWidget(self.Br_tab_43)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        self.Brachy_tab_45 = QWidget()
        self.Brachy_tab_45.setObjectName(u"Brachy_tab_45")
        self.gridLayout_52 = QGridLayout(self.Brachy_tab_45)
        self.gridLayout_52.setObjectName(u"gridLayout_52")
        self.Brachy_Radial_load = QPushButton(self.Brachy_tab_45)
        self.Brachy_Radial_load.setObjectName(u"Brachy_Radial_load")

        self.gridLayout_52.addWidget(self.Brachy_Radial_load, 5, 0, 1, 1)

        self.horizontalSpacer_67 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_67, 5, 4, 1, 1)

        self.Brachy_rad_eq = QLineEdit(self.Brachy_tab_45)
        self.Brachy_rad_eq.setObjectName(u"Brachy_rad_eq")
        self.Brachy_rad_eq.setEnabled(False)
        self.Brachy_rad_eq.setFont(font)

        self.gridLayout_52.addWidget(self.Brachy_rad_eq, 3, 3, 1, 12)

        self.horizontalSpacer_71 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_71, 5, 13, 1, 1)

        self.horizontalSpacer_52 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_52, 5, 1, 1, 1)

        self.horizontalSpacer_72 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_72, 5, 11, 1, 1)

        self.horizontalSpacer_75 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_75, 5, 9, 1, 1)

        self.Brachy_radial_axes = QWidget(self.Brachy_tab_45)
        self.Brachy_radial_axes.setObjectName(u"Brachy_radial_axes")

        self.gridLayout_52.addWidget(self.Brachy_radial_axes, 1, 3, 2, 12)

        self.horizontalSpacer_68 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_68, 5, 5, 1, 1)

        self.horizontalSpacer_53 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_53, 5, 3, 1, 1)

        self.horizontalSpacer_54 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_54, 5, 2, 1, 1)

        self.horizontalSpacer_73 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_73, 5, 6, 1, 1)

        self.horizontalSpacer_74 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_74, 5, 7, 1, 1)

        self.horizontalSpacer_61 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_61, 5, 14, 1, 1)

        self.Brachy_Radial_table = QTableWidget(self.Brachy_tab_45)
        self.Brachy_Radial_table.setObjectName(u"Brachy_Radial_table")

        self.gridLayout_52.addWidget(self.Brachy_Radial_table, 1, 0, 4, 3)

        self.horizontalSpacer_70 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_70, 5, 12, 1, 1)

        self.horizontalSpacer_69 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_69, 5, 10, 1, 1)

        self.horizontalSpacer_76 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_52.addItem(self.horizontalSpacer_76, 5, 8, 1, 1)

        self.Brachy_rad_A0L = QLineEdit(self.Brachy_tab_45)
        self.Brachy_rad_A0L.setObjectName(u"Brachy_rad_A0L")
        self.Brachy_rad_A0L.setEnabled(False)
        self.Brachy_rad_A0L.setFont(font)
        self.Brachy_rad_A0L.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.Brachy_rad_A0L.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_52.addWidget(self.Brachy_rad_A0L, 4, 3, 1, 1)

        self.Brachy_rad_A0 = QLineEdit(self.Brachy_tab_45)
        self.Brachy_rad_A0.setObjectName(u"Brachy_rad_A0")

        self.gridLayout_52.addWidget(self.Brachy_rad_A0, 4, 4, 1, 1)

        self.Brachy_rad_A1L = QLineEdit(self.Brachy_tab_45)
        self.Brachy_rad_A1L.setObjectName(u"Brachy_rad_A1L")
        self.Brachy_rad_A1L.setEnabled(False)
        self.Brachy_rad_A1L.setFont(font)
        self.Brachy_rad_A1L.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.Brachy_rad_A1L.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_52.addWidget(self.Brachy_rad_A1L, 4, 5, 1, 1)

        self.Brachy_rad_A1 = QLineEdit(self.Brachy_tab_45)
        self.Brachy_rad_A1.setObjectName(u"Brachy_rad_A1")

        self.gridLayout_52.addWidget(self.Brachy_rad_A1, 4, 6, 1, 1)

        self.Brachy_rad_A2L = QLineEdit(self.Brachy_tab_45)
        self.Brachy_rad_A2L.setObjectName(u"Brachy_rad_A2L")
        self.Brachy_rad_A2L.setEnabled(False)
        self.Brachy_rad_A2L.setFont(font)
        self.Brachy_rad_A2L.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.Brachy_rad_A2L.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_52.addWidget(self.Brachy_rad_A2L, 4, 7, 1, 1)

        self.brachy_radial_1stline = QLineEdit(self.Brachy_tab_45)
        self.brachy_radial_1stline.setObjectName(u"brachy_radial_1stline")
        self.brachy_radial_1stline.setEnabled(False)
        self.brachy_radial_1stline.setFont(font)

        self.gridLayout_52.addWidget(self.brachy_radial_1stline, 0, 0, 1, 15)

        self.Brachy_rad_A2 = QLineEdit(self.Brachy_tab_45)
        self.Brachy_rad_A2.setObjectName(u"Brachy_rad_A2")

        self.gridLayout_52.addWidget(self.Brachy_rad_A2, 4, 8, 1, 1)

        self.Brachy_rad_A3L = QLineEdit(self.Brachy_tab_45)
        self.Brachy_rad_A3L.setObjectName(u"Brachy_rad_A3L")
        self.Brachy_rad_A3L.setEnabled(False)
        self.Brachy_rad_A3L.setFont(font)
        self.Brachy_rad_A3L.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.Brachy_rad_A3L.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_52.addWidget(self.Brachy_rad_A3L, 4, 9, 1, 1)

        self.Brachy_rad_A3 = QLineEdit(self.Brachy_tab_45)
        self.Brachy_rad_A3.setObjectName(u"Brachy_rad_A3")

        self.gridLayout_52.addWidget(self.Brachy_rad_A3, 4, 10, 1, 1)

        self.Brachy_rad_A4L = QLineEdit(self.Brachy_tab_45)
        self.Brachy_rad_A4L.setObjectName(u"Brachy_rad_A4L")
        self.Brachy_rad_A4L.setEnabled(False)
        self.Brachy_rad_A4L.setFont(font)
        self.Brachy_rad_A4L.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.Brachy_rad_A4L.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_52.addWidget(self.Brachy_rad_A4L, 4, 11, 1, 1)

        self.Brachy_rad_A4 = QLineEdit(self.Brachy_tab_45)
        self.Brachy_rad_A4.setObjectName(u"Brachy_rad_A4")

        self.gridLayout_52.addWidget(self.Brachy_rad_A4, 4, 12, 1, 1)

        self.Brachy_rad_A5L = QLineEdit(self.Brachy_tab_45)
        self.Brachy_rad_A5L.setObjectName(u"Brachy_rad_A5L")
        self.Brachy_rad_A5L.setEnabled(False)
        self.Brachy_rad_A5L.setFont(font)
        self.Brachy_rad_A5L.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.Brachy_rad_A5L.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_52.addWidget(self.Brachy_rad_A5L, 4, 13, 1, 1)

        self.Brachy_rad_A5 = QLineEdit(self.Brachy_tab_45)
        self.Brachy_rad_A5.setObjectName(u"Brachy_rad_A5")

        self.gridLayout_52.addWidget(self.Brachy_rad_A5, 4, 14, 1, 1)

        self.tabWidget_2.addTab(self.Brachy_tab_45, "")
        self.Brachy_tab_46 = QWidget()
        self.Brachy_tab_46.setObjectName(u"Brachy_tab_46")
        self.gridLayout_53 = QGridLayout(self.Brachy_tab_46)
        self.gridLayout_53.setObjectName(u"gridLayout_53")
        self.Brachy_ani_dist_list = QComboBox(self.Brachy_tab_46)
        self.Brachy_ani_dist_list.setObjectName(u"Brachy_ani_dist_list")

        self.gridLayout_53.addWidget(self.Brachy_ani_dist_list, 4, 7, 1, 1)

        self.verticalSpacer_17 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_53.addItem(self.verticalSpacer_17, 8, 8, 1, 1)

        self.horizontalSpacer_56 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_53.addItem(self.horizontalSpacer_56, 12, 3, 1, 1)

        self.verticalSpacer_13 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_53.addItem(self.verticalSpacer_13, 1, 8, 1, 1)

        self.verticalSpacer_15 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_53.addItem(self.verticalSpacer_15, 3, 8, 1, 1)

        self.Brachy_ani_dist_label = QLineEdit(self.Brachy_tab_46)
        self.Brachy_ani_dist_label.setObjectName(u"Brachy_ani_dist_label")
        self.Brachy_ani_dist_label.setEnabled(False)

        self.gridLayout_53.addWidget(self.Brachy_ani_dist_label, 4, 6, 1, 1)

        self.Brachy_ani_table = QTableWidget(self.Brachy_tab_46)
        self.Brachy_ani_table.setObjectName(u"Brachy_ani_table")

        self.gridLayout_53.addWidget(self.Brachy_ani_table, 0, 0, 4, 8)

        self.verticalSpacer_18 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_53.addItem(self.verticalSpacer_18, 10, 8, 1, 1)

        self.horizontalSpacer_57 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_53.addItem(self.horizontalSpacer_57, 12, 7, 1, 1)

        self.verticalSpacer_12 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_53.addItem(self.verticalSpacer_12, 0, 8, 1, 1)

        self.horizontalSpacer_58 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_53.addItem(self.horizontalSpacer_58, 12, 6, 1, 1)

        self.horizontalSpacer_55 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_53.addItem(self.horizontalSpacer_55, 12, 0, 1, 1)

        self.horizontalSpacer_59 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_53.addItem(self.horizontalSpacer_59, 12, 5, 1, 1)

        self.verticalSpacer_14 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_53.addItem(self.verticalSpacer_14, 2, 8, 1, 1)

        self.verticalSpacer_16 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_53.addItem(self.verticalSpacer_16, 6, 8, 1, 1)

        self.horizontalSpacer_60 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_53.addItem(self.horizontalSpacer_60, 12, 4, 1, 1)

        self.Brachy_load_ani = QPushButton(self.Brachy_tab_46)
        self.Brachy_load_ani.setObjectName(u"Brachy_load_ani")

        self.gridLayout_53.addWidget(self.Brachy_load_ani, 11, 7, 1, 1)

        self.Brach_plot_ani = QPushButton(self.Brachy_tab_46)
        self.Brach_plot_ani.setObjectName(u"Brach_plot_ani")

        self.gridLayout_53.addWidget(self.Brach_plot_ani, 5, 7, 1, 1)

        self.Brachy_ani_plot_hold = QCheckBox(self.Brachy_tab_46)
        self.Brachy_ani_plot_hold.setObjectName(u"Brachy_ani_plot_hold")

        self.gridLayout_53.addWidget(self.Brachy_ani_plot_hold, 5, 6, 1, 1)

        self.Brachy_ani_axes = QWidget(self.Brachy_tab_46)
        self.Brachy_ani_axes.setObjectName(u"Brachy_ani_axes")

        self.gridLayout_53.addWidget(self.Brachy_ani_axes, 4, 0, 8, 6)

        self.tabWidget_2.addTab(self.Brachy_tab_46, "")
        self.tab_36 = QWidget()
        self.tab_36.setObjectName(u"tab_36")
        self.gridLayout_55 = QGridLayout(self.tab_36)
        self.gridLayout_55.setObjectName(u"gridLayout_55")
        self.comboBox_tg43_along_away = QComboBox(self.tab_36)
        self.comboBox_tg43_along_away.setObjectName(u"comboBox_tg43_along_away")

        self.gridLayout_55.addWidget(self.comboBox_tg43_along_away, 2, 1, 1, 1)

        self.horizontalSpacer_43 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_55.addItem(self.horizontalSpacer_43, 2, 0, 1, 1)

        self.TG43_along_away = QTableWidget(self.tab_36)
        self.TG43_along_away.setObjectName(u"TG43_along_away")

        self.gridLayout_55.addWidget(self.TG43_along_away, 1, 0, 1, 2)

        self.tabWidget_2.addTab(self.tab_36, "")
        self.DECT_tab_47 = QWidget()
        self.DECT_tab_47.setObjectName(u"DECT_tab_47")
        self.gridLayout_54 = QGridLayout(self.DECT_tab_47)
        self.gridLayout_54.setObjectName(u"gridLayout_54")
        self.horizontalSpacer_62 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_54.addItem(self.horizontalSpacer_62, 2, 0, 1, 1)

        self.horizontalSpacer_63 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_54.addItem(self.horizontalSpacer_63, 2, 4, 1, 1)

        self.horizontalSpacer_65 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_54.addItem(self.horizontalSpacer_65, 2, 2, 1, 1)

        self.horizontalSpacer_64 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_54.addItem(self.horizontalSpacer_64, 2, 3, 1, 1)

        self.horizontalSpacer_66 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_54.addItem(self.horizontalSpacer_66, 2, 1, 1, 1)

        self.Brachy_cal_table = QTableWidget(self.DECT_tab_47)
        self.Brachy_cal_table.setObjectName(u"Brachy_cal_table")

        self.gridLayout_54.addWidget(self.Brachy_cal_table, 0, 0, 1, 2)

        self.Brachy_cal_add_line = QPushButton(self.DECT_tab_47)
        self.Brachy_cal_add_line.setObjectName(u"Brachy_cal_add_line")

        self.gridLayout_54.addWidget(self.Brachy_cal_add_line, 1, 0, 1, 1)

        self.Brachy_cal_Delete_line = QPushButton(self.DECT_tab_47)
        self.Brachy_cal_Delete_line.setObjectName(u"Brachy_cal_Delete_line")

        self.gridLayout_54.addWidget(self.Brachy_cal_Delete_line, 1, 1, 1, 1)

        self.tabWidget_2.addTab(self.DECT_tab_47, "")

        self.gridLayout_51.addWidget(self.tabWidget_2, 0, 0, 1, 6)

        self.Brachy_doseRate_label = QLineEdit(self.Br_tab_43)
        self.Brachy_doseRate_label.setObjectName(u"Brachy_doseRate_label")
        self.Brachy_doseRate_label.setEnabled(False)
        self.Brachy_doseRate_label.setFont(font)

        self.gridLayout_51.addWidget(self.Brachy_doseRate_label, 3, 2, 1, 1)

        self.Brachy_rad_leng_label = QLineEdit(self.Br_tab_43)
        self.Brachy_rad_leng_label.setObjectName(u"Brachy_rad_leng_label")
        self.Brachy_rad_leng_label.setEnabled(False)
        self.Brachy_rad_leng_label.setFont(font)

        self.gridLayout_51.addWidget(self.Brachy_rad_leng_label, 4, 2, 1, 1)

        self.Brachy_dose_rate_cte_value = QLineEdit(self.Br_tab_43)
        self.Brachy_dose_rate_cte_value.setObjectName(u"Brachy_dose_rate_cte_value")
        self.Brachy_dose_rate_cte_value.setFont(font)

        self.gridLayout_51.addWidget(self.Brachy_dose_rate_cte_value, 3, 3, 1, 1)

        self.Brachy_rad_leng = QLineEdit(self.Br_tab_43)
        self.Brachy_rad_leng.setObjectName(u"Brachy_rad_leng")
        self.Brachy_rad_leng.setFont(font)

        self.gridLayout_51.addWidget(self.Brachy_rad_leng, 4, 3, 1, 1)

        self.Tg43_matrix_size = QGroupBox(self.Br_tab_43)
        self.Tg43_matrix_size.setObjectName(u"Tg43_matrix_size")
        self.gridLayout_56 = QGridLayout(self.Tg43_matrix_size)
        self.gridLayout_56.setObjectName(u"gridLayout_56")
        self.Tg43_dose_grid = QComboBox(self.Tg43_matrix_size)
        self.Tg43_dose_grid.setObjectName(u"Tg43_dose_grid")

        self.gridLayout_56.addWidget(self.Tg43_dose_grid, 0, 1, 1, 1)

        self.Tg43_matrix_size_2 = QComboBox(self.Tg43_matrix_size)
        self.Tg43_matrix_size_2.setObjectName(u"Tg43_matrix_size_2")

        self.gridLayout_56.addWidget(self.Tg43_matrix_size_2, 1, 1, 1, 1)

        self.lineEdit_tg43_01 = QLineEdit(self.Tg43_matrix_size)
        self.lineEdit_tg43_01.setObjectName(u"lineEdit_tg43_01")
        self.lineEdit_tg43_01.setEnabled(False)

        self.gridLayout_56.addWidget(self.lineEdit_tg43_01, 0, 0, 1, 1)

        self.lineEdit_tg43_02 = QLineEdit(self.Tg43_matrix_size)
        self.lineEdit_tg43_02.setObjectName(u"lineEdit_tg43_02")
        self.lineEdit_tg43_02.setEnabled(False)

        self.gridLayout_56.addWidget(self.lineEdit_tg43_02, 1, 0, 1, 1)


        self.gridLayout_51.addWidget(self.Tg43_matrix_size, 3, 4, 2, 1)

        self.BrachytabWidget_2.addTab(self.Br_tab_43, "")

        self.gridLayout_43.addWidget(self.BrachytabWidget_2, 0, 1, 1, 1)

        self.Plan_tabs.addTab(self.Brachy_plan_tab, "")
        self.eqd2 = QWidget()
        self.eqd2.setObjectName(u"eqd2")
        self.dose_matri_to_eqd2 = QGroupBox(self.eqd2)
        self.dose_matri_to_eqd2.setObjectName(u"dose_matri_to_eqd2")
        self.dose_matri_to_eqd2.setGeometry(QRect(9, 9, 1543, 511))
        self.layoutWidget = QWidget(self.dose_matri_to_eqd2)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 20, 451, 30))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setSpacing(8)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.eqd2_lab1 = QLabel(self.layoutWidget)
        self.eqd2_lab1.setObjectName(u"eqd2_lab1")

        self.horizontalLayout.addWidget(self.eqd2_lab1)

        self.dose_list = QComboBox(self.layoutWidget)
        self.dose_list.setObjectName(u"dose_list")

        self.horizontalLayout.addWidget(self.dose_list)

        self.horizontalLayout.setStretch(1, 3)
        self.layoutWidget1 = QWidget(self.dose_matri_to_eqd2)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(10, 70, 771, 61))
        self.chose_struct = QHBoxLayout(self.layoutWidget1)
        self.chose_struct.setSpacing(8)
        self.chose_struct.setObjectName(u"chose_struct")
        self.chose_struct.setContentsMargins(0, 0, 0, 0)
        self.eqd2_lab1_2 = QLabel(self.layoutWidget1)
        self.eqd2_lab1_2.setObjectName(u"eqd2_lab1_2")

        self.chose_struct.addWidget(self.eqd2_lab1_2)

        self.eqd2_struct_list = QComboBox(self.layoutWidget1)
        self.eqd2_struct_list.setObjectName(u"eqd2_struct_list")

        self.chose_struct.addWidget(self.eqd2_struct_list)

        self.horizontalSpacer_47 = QSpacerItem(58, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.chose_struct.addItem(self.horizontalSpacer_47)

        self.eqd2_lab1_3 = QLabel(self.layoutWidget1)
        self.eqd2_lab1_3.setObjectName(u"eqd2_lab1_3")

        self.chose_struct.addWidget(self.eqd2_lab1_3)

        self.ab_input = QLineEdit(self.layoutWidget1)
        self.ab_input.setObjectName(u"ab_input")

        self.chose_struct.addWidget(self.ab_input)

        self.add_to_ab_list = QPushButton(self.layoutWidget1)
        self.add_to_ab_list.setObjectName(u"add_to_ab_list")

        self.chose_struct.addWidget(self.add_to_ab_list)

        self.delete_from_ab_list = QPushButton(self.layoutWidget1)
        self.delete_from_ab_list.setObjectName(u"delete_from_ab_list")

        self.chose_struct.addWidget(self.delete_from_ab_list)

        self.chose_struct.setStretch(1, 8)
        self.layoutWidget2 = QWidget(self.dose_matri_to_eqd2)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.layoutWidget2.setGeometry(QRect(10, 140, 681, 331))
        self.laststep = QHBoxLayout(self.layoutWidget2)
        self.laststep.setSpacing(8)
        self.laststep.setObjectName(u"laststep")
        self.laststep.setContentsMargins(0, 0, 0, 0)
        self.ab_table = QTableWidget(self.layoutWidget2)
        self.ab_table.setObjectName(u"ab_table")

        self.laststep.addWidget(self.ab_table)

        self.n_fractions_label = QLabel(self.layoutWidget2)
        self.n_fractions_label.setObjectName(u"n_fractions_label")

        self.laststep.addWidget(self.n_fractions_label)

        self.input_fractions = QLineEdit(self.layoutWidget2)
        self.input_fractions.setObjectName(u"input_fractions")

        self.laststep.addWidget(self.input_fractions)

        self.calc_eqd2 = QPushButton(self.layoutWidget2)
        self.calc_eqd2.setObjectName(u"calc_eqd2")

        self.laststep.addWidget(self.calc_eqd2)

        self.ab_matrix = QPushButton(self.dose_matri_to_eqd2)
        self.ab_matrix.setObjectName(u"ab_matrix")
        self.ab_matrix.setGeometry(QRect(10, 480, 261, 28))
        self.eqd2_calc = QGroupBox(self.eqd2)
        self.eqd2_calc.setObjectName(u"eqd2_calc")
        self.eqd2_calc.setGeometry(QRect(10, 540, 1543, 451))
        self.eqd2_out = QLCDNumber(self.eqd2_calc)
        self.eqd2_out.setObjectName(u"eqd2_out")
        self.eqd2_out.setGeometry(QRect(240, 100, 131, 51))
        self.label_1_eqd2_calc_5 = QLabel(self.eqd2_calc)
        self.label_1_eqd2_calc_5.setObjectName(u"label_1_eqd2_calc_5")
        self.label_1_eqd2_calc_5.setGeometry(QRect(390, 100, 91, 51))
        font3 = QFont()
        font3.setPointSize(28)
        self.label_1_eqd2_calc_5.setFont(font3)
        self.label_1_eqd2_calc_5.setScaledContents(True)
        self.layoutWidget3 = QWidget(self.eqd2_calc)
        self.layoutWidget3.setObjectName(u"layoutWidget3")
        self.layoutWidget3.setGeometry(QRect(10, 50, 704, 30))
        self.horizontalLayout_2 = QHBoxLayout(self.layoutWidget3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_1_eqd2_calc_2 = QLabel(self.layoutWidget3)
        self.label_1_eqd2_calc_2.setObjectName(u"label_1_eqd2_calc_2")

        self.horizontalLayout_2.addWidget(self.label_1_eqd2_calc_2)

        self.input_total_dose = QLineEdit(self.layoutWidget3)
        self.input_total_dose.setObjectName(u"input_total_dose")

        self.horizontalLayout_2.addWidget(self.input_total_dose)

        self.label_1_eqd2_calc_3 = QLabel(self.layoutWidget3)
        self.label_1_eqd2_calc_3.setObjectName(u"label_1_eqd2_calc_3")

        self.horizontalLayout_2.addWidget(self.label_1_eqd2_calc_3)

        self.input_ab_calculator = QLineEdit(self.layoutWidget3)
        self.input_ab_calculator.setObjectName(u"input_ab_calculator")

        self.horizontalLayout_2.addWidget(self.input_ab_calculator)

        self.label_1_eqd2_calc_4 = QLabel(self.layoutWidget3)
        self.label_1_eqd2_calc_4.setObjectName(u"label_1_eqd2_calc_4")

        self.horizontalLayout_2.addWidget(self.label_1_eqd2_calc_4)

        self.input_frac_calc = QLineEdit(self.layoutWidget3)
        self.input_frac_calc.setObjectName(u"input_frac_calc")

        self.horizontalLayout_2.addWidget(self.input_frac_calc)

        self.calc_eqd2_2 = QPushButton(self.layoutWidget3)
        self.calc_eqd2_2.setObjectName(u"calc_eqd2_2")

        self.horizontalLayout_2.addWidget(self.calc_eqd2_2)

        self.Plan_tabs.addTab(self.eqd2, "")
        self.Plan_Evaluation = QWidget()
        self.Plan_Evaluation.setObjectName(u"Plan_Evaluation")
        self.gridLayout_59 = QGridLayout(self.Plan_Evaluation)
        self.gridLayout_59.setObjectName(u"gridLayout_59")
        self.plan_eval_grid_left = QGridLayout()
        self.plan_eval_grid_left.setObjectName(u"plan_eval_grid_left")
        self.dose_unit_Gy = QCheckBox(self.Plan_Evaluation)
        self.dose_unit_Gy.setObjectName(u"dose_unit_Gy")

        self.plan_eval_grid_left.addWidget(self.dose_unit_Gy, 18, 2, 1, 1)

        self.HS_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_left.addItem(self.HS_6, 17, 1, 1, 1)

        self.DoseUnit = QLabel(self.Plan_Evaluation)
        self.DoseUnit.setObjectName(u"DoseUnit")

        self.plan_eval_grid_left.addWidget(self.DoseUnit, 17, 2, 1, 1)

        self.VolumeUnit = QLabel(self.Plan_Evaluation)
        self.VolumeUnit.setObjectName(u"VolumeUnit")

        self.plan_eval_grid_left.addWidget(self.VolumeUnit, 17, 0, 1, 1)

        self.HS_1 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_left.addItem(self.HS_1, 16, 1, 1, 1)

        self.struct_list_DVH = QListWidget(self.Plan_Evaluation)
        self.struct_list_DVH.setObjectName(u"struct_list_DVH")

        self.plan_eval_grid_left.addWidget(self.struct_list_DVH, 13, 0, 1, 3)

        self.button_calculate_dvhs = QPushButton(self.Plan_Evaluation)
        self.button_calculate_dvhs.setObjectName(u"button_calculate_dvhs")

        self.plan_eval_grid_left.addWidget(self.button_calculate_dvhs, 20, 2, 1, 1)

        self.select_dose = QLabel(self.Plan_Evaluation)
        self.select_dose.setObjectName(u"select_dose")

        self.plan_eval_grid_left.addWidget(self.select_dose, 2, 0, 1, 1)

        self.box_reference_dose = QLineEdit(self.Plan_Evaluation)
        self.box_reference_dose.setObjectName(u"box_reference_dose")

        self.plan_eval_grid_left.addWidget(self.box_reference_dose, 16, 2, 1, 1)

        self.HS_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_left.addItem(self.HS_2, 20, 0, 1, 2)

        self.volume_unit_percentage = QCheckBox(self.Plan_Evaluation)
        self.volume_unit_percentage.setObjectName(u"volume_unit_percentage")

        self.plan_eval_grid_left.addWidget(self.volume_unit_percentage, 19, 0, 1, 1)

        self.HS_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_left.addItem(self.HS_5, 18, 1, 1, 1)

        self.HS_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_left.addItem(self.HS_8, 6, 1, 1, 2)

        self.HS_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_left.addItem(self.HS_4, 19, 1, 1, 1)

        self.HS_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_left.addItem(self.HS_3, 14, 0, 1, 2)

        self.volume_unit_cm3 = QCheckBox(self.Plan_Evaluation)
        self.volume_unit_cm3.setObjectName(u"volume_unit_cm3")

        self.plan_eval_grid_left.addWidget(self.volume_unit_cm3, 18, 0, 1, 1)

        self.Structures = QLabel(self.Plan_Evaluation)
        self.Structures.setObjectName(u"Structures")

        self.plan_eval_grid_left.addWidget(self.Structures, 6, 0, 1, 1)

        self.HS_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_left.addItem(self.HS_7, 2, 1, 1, 2)

        self.dose_unit_percentage = QCheckBox(self.Plan_Evaluation)
        self.dose_unit_percentage.setObjectName(u"dose_unit_percentage")

        self.plan_eval_grid_left.addWidget(self.dose_unit_percentage, 19, 2, 1, 1)

        self.box_select_dose = QListWidget(self.Plan_Evaluation)
        self.box_select_dose.setObjectName(u"box_select_dose")

        self.plan_eval_grid_left.addWidget(self.box_select_dose, 4, 0, 1, 3)

        self.reference_dose = QLabel(self.Plan_Evaluation)
        self.reference_dose.setObjectName(u"reference_dose")

        self.plan_eval_grid_left.addWidget(self.reference_dose, 16, 0, 1, 1)

        self.button_update_select_dose = QPushButton(self.Plan_Evaluation)
        self.button_update_select_dose.setObjectName(u"button_update_select_dose")

        self.plan_eval_grid_left.addWidget(self.button_update_select_dose, 14, 2, 1, 1)

        self.horizontalline_left_grid = QFrame(self.Plan_Evaluation)
        self.horizontalline_left_grid.setObjectName(u"horizontalline_left_grid")
        self.horizontalline_left_grid.setFrameShape(QFrame.Shape.HLine)
        self.horizontalline_left_grid.setFrameShadow(QFrame.Shadow.Sunken)

        self.plan_eval_grid_left.addWidget(self.horizontalline_left_grid, 15, 0, 1, 3)

        self.plan_eval_grid_left.setColumnStretch(0, 3)
        self.plan_eval_grid_left.setColumnStretch(1, 1)
        self.plan_eval_grid_left.setColumnStretch(2, 3)

        self.gridLayout_59.addLayout(self.plan_eval_grid_left, 0, 0, 1, 1)

        self.plan_eval_grid_middle = QGridLayout()
        self.plan_eval_grid_middle.setObjectName(u"plan_eval_grid_middle")
        self.HS_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_middle.addItem(self.HS_11, 0, 2, 1, 2)

        self.DoseStatistics = QLabel(self.Plan_Evaluation)
        self.DoseStatistics.setObjectName(u"DoseStatistics")

        self.plan_eval_grid_middle.addWidget(self.DoseStatistics, 5, 0, 1, 1)

        self.verticalline_middle_grid = QFrame(self.Plan_Evaluation)
        self.verticalline_middle_grid.setObjectName(u"verticalline_middle_grid")
        self.verticalline_middle_grid.setFrameShape(QFrame.Shape.VLine)
        self.verticalline_middle_grid.setFrameShadow(QFrame.Shadow.Sunken)

        self.plan_eval_grid_middle.addWidget(self.verticalline_middle_grid, 9, 0, 1, 1)

        self.button_select_all_rows_DST = QPushButton(self.Plan_Evaluation)
        self.button_select_all_rows_DST.setObjectName(u"button_select_all_rows_DST")

        self.plan_eval_grid_middle.addWidget(self.button_select_all_rows_DST, 7, 0, 1, 1)

        self.view_dvhs = QGraphicsView(self.Plan_Evaluation)
        self.view_dvhs.setObjectName(u"view_dvhs")

        self.plan_eval_grid_middle.addWidget(self.view_dvhs, 1, 0, 1, 4)

        self.DVHs = QLabel(self.Plan_Evaluation)
        self.DVHs.setObjectName(u"DVHs")

        self.plan_eval_grid_middle.addWidget(self.DVHs, 0, 0, 1, 1)

        self.line_split_planevaluation_2 = QFrame(self.Plan_Evaluation)
        self.line_split_planevaluation_2.setObjectName(u"line_split_planevaluation_2")
        self.line_split_planevaluation_2.setFrameShape(QFrame.Shape.VLine)
        self.line_split_planevaluation_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.plan_eval_grid_middle.addWidget(self.line_split_planevaluation_2, 4, 0, 1, 1)

        self.button_update_plot = QPushButton(self.Plan_Evaluation)
        self.button_update_plot.setObjectName(u"button_update_plot")

        self.plan_eval_grid_middle.addWidget(self.button_update_plot, 8, 0, 1, 1)

        self.table_dose_stats = QTableWidget(self.Plan_Evaluation)
        self.table_dose_stats.setObjectName(u"table_dose_stats")

        self.plan_eval_grid_middle.addWidget(self.table_dose_stats, 6, 0, 1, 4)

        self.line_split_planevaluation_3 = QFrame(self.Plan_Evaluation)
        self.line_split_planevaluation_3.setObjectName(u"line_split_planevaluation_3")
        self.line_split_planevaluation_3.setFrameShape(QFrame.Shape.HLine)
        self.line_split_planevaluation_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.plan_eval_grid_middle.addWidget(self.line_split_planevaluation_3, 2, 0, 1, 4)

        self.HS_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_middle.addItem(self.HS_10, 5, 1, 1, 1)

        self.button_delete_column = QPushButton(self.Plan_Evaluation)
        self.button_delete_column.setObjectName(u"button_delete_column")

        self.plan_eval_grid_middle.addWidget(self.button_delete_column, 5, 2, 1, 2)

        self.HS_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_middle.addItem(self.HS_9, 8, 1, 1, 1)

        self.HS_17 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_middle.addItem(self.HS_17, 7, 1, 1, 1)

        self.button_export_dose_stats_to_excel = QPushButton(self.Plan_Evaluation)
        self.button_export_dose_stats_to_excel.setObjectName(u"button_export_dose_stats_to_excel")

        self.plan_eval_grid_middle.addWidget(self.button_export_dose_stats_to_excel, 8, 2, 1, 2)

        self.plan_eval_grid_middle.setRowStretch(1, 4)
        self.plan_eval_grid_middle.setRowStretch(2, 4)
        self.plan_eval_grid_middle.setColumnStretch(0, 1)
        self.plan_eval_grid_middle.setColumnStretch(1, 2)
        self.plan_eval_grid_middle.setColumnStretch(2, 1)

        self.gridLayout_59.addLayout(self.plan_eval_grid_middle, 0, 1, 1, 1)

        self.plan_eval_grid_right = QGridLayout()
        self.plan_eval_grid_right.setObjectName(u"plan_eval_grid_right")
        self.Dxx = QLabel(self.Plan_Evaluation)
        self.Dxx.setObjectName(u"Dxx")

        self.plan_eval_grid_right.addWidget(self.Dxx, 12, 0, 1, 1)

        self.vxx_input_dropdown = QComboBox(self.Plan_Evaluation)
        self.vxx_input_dropdown.setObjectName(u"vxx_input_dropdown")

        self.plan_eval_grid_right.addWidget(self.vxx_input_dropdown, 11, 1, 1, 1)

        self.vxx_t_label = QLabel(self.Plan_Evaluation)
        self.vxx_t_label.setObjectName(u"vxx_t_label")

        self.plan_eval_grid_right.addWidget(self.vxx_t_label, 11, 2, 1, 1)

        self.HS_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_right.addItem(self.HS_12, 16, 0, 1, 3)

        self.dxx_input_value = QLineEdit(self.Plan_Evaluation)
        self.dxx_input_value.setObjectName(u"dxx_input_value")

        self.plan_eval_grid_right.addWidget(self.dxx_input_value, 15, 0, 1, 1)

        self.HS_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_right.addItem(self.HS_13, 8, 0, 1, 4)

        self.dxx_input_dropdown = QComboBox(self.Plan_Evaluation)
        self.dxx_input_dropdown.setObjectName(u"dxx_input_dropdown")

        self.plan_eval_grid_right.addWidget(self.dxx_input_dropdown, 15, 1, 1, 1)

        self.button_calculate_vxx_dxx = QPushButton(self.Plan_Evaluation)
        self.button_calculate_vxx_dxx.setObjectName(u"button_calculate_vxx_dxx")

        self.plan_eval_grid_right.addWidget(self.button_calculate_vxx_dxx, 16, 3, 1, 1)

        self.HS_16 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_right.addItem(self.HS_16, 10, 1, 1, 3)

        self.vxx_input_value = QLineEdit(self.Plan_Evaluation)
        self.vxx_input_value.setObjectName(u"vxx_input_value")

        self.plan_eval_grid_right.addWidget(self.vxx_input_value, 11, 0, 1, 1)

        self.Vxx = QLabel(self.Plan_Evaluation)
        self.Vxx.setObjectName(u"Vxx")

        self.plan_eval_grid_right.addWidget(self.Vxx, 10, 0, 1, 1)

        self.dxx_output_dropdown = QComboBox(self.Plan_Evaluation)
        self.dxx_output_dropdown.setObjectName(u"dxx_output_dropdown")

        self.plan_eval_grid_right.addWidget(self.dxx_output_dropdown, 15, 3, 1, 1)

        self.dxx_to_label = QLabel(self.Plan_Evaluation)
        self.dxx_to_label.setObjectName(u"dxx_to_label")

        self.plan_eval_grid_right.addWidget(self.dxx_to_label, 15, 2, 1, 1)

        self.HS_14 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_right.addItem(self.HS_14, 12, 1, 1, 3)

        self.vxx_output_dropdown = QComboBox(self.Plan_Evaluation)
        self.vxx_output_dropdown.setObjectName(u"vxx_output_dropdown")

        self.plan_eval_grid_right.addWidget(self.vxx_output_dropdown, 11, 3, 1, 1)

        self.HS_15 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_right.addItem(self.HS_15, 17, 0, 1, 4)

        self.line_grid_right = QFrame(self.Plan_Evaluation)
        self.line_grid_right.setObjectName(u"line_grid_right")
        self.line_grid_right.setFrameShape(QFrame.Shape.HLine)
        self.line_grid_right.setFrameShadow(QFrame.Shadow.Sunken)

        self.plan_eval_grid_right.addWidget(self.line_grid_right, 7, 0, 1, 4)

        self.tab_errors = QTabWidget(self.Plan_Evaluation)
        self.tab_errors.setObjectName(u"tab_errors")
        self.uncertainty = QWidget()
        self.uncertainty.setObjectName(u"uncertainty")
        self.Mean = QLabel(self.uncertainty)
        self.Mean.setObjectName(u"Mean")
        self.Mean.setGeometry(QRect(80, 10, 69, 20))
        self.box_Y_std_input = QLineEdit(self.uncertainty)
        self.box_Y_std_input.setObjectName(u"box_Y_std_input")
        self.box_Y_std_input.setGeometry(QRect(210, 80, 81, 25))
        self.NumberOfInteractions = QLabel(self.uncertainty)
        self.NumberOfInteractions.setObjectName(u"NumberOfInteractions")
        self.NumberOfInteractions.setGeometry(QRect(0, 250, 171, 20))
        self.Y = QLabel(self.uncertainty)
        self.Y.setObjectName(u"Y")
        self.Y.setGeometry(QRect(0, 80, 31, 20))
        self.box_X_std_input = QLineEdit(self.uncertainty)
        self.box_X_std_input.setObjectName(u"box_X_std_input")
        self.box_X_std_input.setGeometry(QRect(210, 40, 81, 25))
        self.box_Z_mean_input = QLineEdit(self.uncertainty)
        self.box_Z_mean_input.setObjectName(u"box_Z_mean_input")
        self.box_Z_mean_input.setGeometry(QRect(70, 120, 81, 25))
        self.box_X_mean_input = QLineEdit(self.uncertainty)
        self.box_X_mean_input.setObjectName(u"box_X_mean_input")
        self.box_X_mean_input.setGeometry(QRect(70, 40, 81, 25))
        self.StandardDeviation = QLabel(self.uncertainty)
        self.StandardDeviation.setObjectName(u"StandardDeviation")
        self.StandardDeviation.setGeometry(QRect(210, 10, 69, 20))
        self.X = QLabel(self.uncertainty)
        self.X.setObjectName(u"X")
        self.X.setGeometry(QRect(0, 40, 31, 20))
        self.T = QLabel(self.uncertainty)
        self.T.setObjectName(u"T")
        self.T.setGeometry(QRect(0, 160, 31, 20))
        self.button_apply_uncertainty = QPushButton(self.uncertainty)
        self.button_apply_uncertainty.setObjectName(u"button_apply_uncertainty")
        self.button_apply_uncertainty.setGeometry(QRect(0, 310, 89, 28))
        self.box_T_mean_input = QLineEdit(self.uncertainty)
        self.box_T_mean_input.setObjectName(u"box_T_mean_input")
        self.box_T_mean_input.setGeometry(QRect(70, 160, 81, 25))
        self.box_Z_std_input = QLineEdit(self.uncertainty)
        self.box_Z_std_input.setObjectName(u"box_Z_std_input")
        self.box_Z_std_input.setGeometry(QRect(210, 120, 81, 25))
        self.box_T_std_input = QLineEdit(self.uncertainty)
        self.box_T_std_input.setObjectName(u"box_T_std_input")
        self.box_T_std_input.setGeometry(QRect(210, 160, 81, 25))
        self.box_Y_mean_input = QLineEdit(self.uncertainty)
        self.box_Y_mean_input.setObjectName(u"box_Y_mean_input")
        self.box_Y_mean_input.setGeometry(QRect(70, 80, 81, 25))
        self.Z = QLabel(self.uncertainty)
        self.Z.setObjectName(u"Z")
        self.Z.setGeometry(QRect(0, 120, 31, 20))
        self.box_number_of_interactions = QLineEdit(self.uncertainty)
        self.box_number_of_interactions.setObjectName(u"box_number_of_interactions")
        self.box_number_of_interactions.setGeometry(QRect(210, 250, 81, 25))
        self.button_show_uncertainty_bands = QPushButton(self.uncertainty)
        self.button_show_uncertainty_bands.setObjectName(u"button_show_uncertainty_bands")
        self.button_show_uncertainty_bands.setGeometry(QRect(0, 360, 89, 28))
        self.tab_errors.addTab(self.uncertainty, "")
        self.error_simulation = QWidget()
        self.error_simulation.setObjectName(u"error_simulation")
        self.tab_errors.addTab(self.error_simulation, "")

        self.plan_eval_grid_right.addWidget(self.tab_errors, 0, 0, 2, 4)

        self.Deviation_Metrics = QLabel(self.Plan_Evaluation)
        self.Deviation_Metrics.setObjectName(u"Deviation_Metrics")

        self.plan_eval_grid_right.addWidget(self.Deviation_Metrics, 9, 0, 1, 1)

        self.HS_18 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.plan_eval_grid_right.addItem(self.HS_18, 9, 1, 1, 3)

        self.plan_eval_grid_right.setRowStretch(0, 4)
        self.plan_eval_grid_right.setRowStretch(1, 7)
        self.plan_eval_grid_right.setRowStretch(10, 1)
        self.plan_eval_grid_right.setRowStretch(16, 1)
        self.plan_eval_grid_right.setRowStretch(17, 1)
        self.plan_eval_grid_right.setColumnStretch(0, 1)
        self.plan_eval_grid_right.setColumnStretch(1, 1)
        self.plan_eval_grid_right.setColumnStretch(2, 1)
        self.plan_eval_grid_right.setColumnStretch(3, 1)

        self.gridLayout_59.addLayout(self.plan_eval_grid_right, 0, 2, 1, 1)

        self.gridLayout_59.setColumnStretch(0, 1)
        self.gridLayout_59.setColumnStretch(1, 2)
        self.gridLayout_59.setColumnStretch(2, 1)
        self.Plan_tabs.addTab(self.Plan_Evaluation, "")
        self.tab_mat_assignment = QWidget()
        self.tab_mat_assignment.setObjectName(u"tab_mat_assignment")
        self.gridLayout_69 = QGridLayout(self.tab_mat_assignment)
        self.gridLayout_69.setObjectName(u"gridLayout_69")
        self.groupBox_mat_to_struct = QGroupBox(self.tab_mat_assignment)
        self.groupBox_mat_to_struct.setObjectName(u"groupBox_mat_to_struct")
        self.gridLayout_72 = QGridLayout(self.groupBox_mat_to_struct)
        self.gridLayout_72.setObjectName(u"gridLayout_72")
        self.mat_to_struct_tab = QTableWidget(self.groupBox_mat_to_struct)
        self.mat_to_struct_tab.setObjectName(u"mat_to_struct_tab")

        self.gridLayout_72.addWidget(self.mat_to_struct_tab, 0, 0, 1, 1)

        self.remove_mat_from_struct = QPushButton(self.groupBox_mat_to_struct)
        self.remove_mat_from_struct.setObjectName(u"remove_mat_from_struct")

        self.gridLayout_72.addWidget(self.remove_mat_from_struct, 1, 0, 1, 1)


        self.gridLayout_69.addWidget(self.groupBox_mat_to_struct, 1, 1, 1, 1)

        self.assign_mat = QGroupBox(self.tab_mat_assignment)
        self.assign_mat.setObjectName(u"assign_mat")
        self.gridLayout_5 = QGridLayout(self.assign_mat)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.mat_to_hu = QPushButton(self.assign_mat)
        self.mat_to_hu.setObjectName(u"mat_to_hu")

        self.gridLayout_5.addWidget(self.mat_to_hu, 0, 6, 1, 1)

        self.Select_mat = QComboBox(self.assign_mat)
        self.Select_mat.setObjectName(u"Select_mat")

        self.gridLayout_5.addWidget(self.Select_mat, 0, 0, 1, 2)

        self.HU_high = QLineEdit(self.assign_mat)
        self.HU_high.setObjectName(u"HU_high")

        self.gridLayout_5.addWidget(self.HU_high, 0, 5, 1, 1)

        self.label_mat_2 = QLabel(self.assign_mat)
        self.label_mat_2.setObjectName(u"label_mat_2")

        self.gridLayout_5.addWidget(self.label_mat_2, 0, 4, 1, 1)

        self.HU_low = QLineEdit(self.assign_mat)
        self.HU_low.setObjectName(u"HU_low")

        self.gridLayout_5.addWidget(self.HU_low, 0, 3, 1, 1)

        self.label_mat = QLabel(self.assign_mat)
        self.label_mat.setObjectName(u"label_mat")

        self.gridLayout_5.addWidget(self.label_mat, 0, 2, 1, 1)

        self.Struct_list_mat = QComboBox(self.assign_mat)
        self.Struct_list_mat.setObjectName(u"Struct_list_mat")

        self.gridLayout_5.addWidget(self.Struct_list_mat, 2, 0, 1, 2)

        self.mat_to_struct = QPushButton(self.assign_mat)
        self.mat_to_struct.setObjectName(u"mat_to_struct")

        self.gridLayout_5.addWidget(self.mat_to_struct, 2, 2, 1, 3)

        self.update_mat_struct_list = QPushButton(self.assign_mat)
        self.update_mat_struct_list.setObjectName(u"update_mat_struct_list")

        self.gridLayout_5.addWidget(self.update_mat_struct_list, 2, 5, 1, 2)

        self.gridLayout_5.setColumnStretch(0, 10)
        self.gridLayout_5.setColumnStretch(1, 1)
        self.gridLayout_5.setColumnStretch(2, 1)
        self.gridLayout_5.setColumnStretch(3, 1)
        self.gridLayout_5.setColumnStretch(4, 1)
        self.gridLayout_5.setColumnStretch(5, 1)
        self.gridLayout_5.setColumnStretch(6, 1)

        self.gridLayout_69.addWidget(self.assign_mat, 0, 0, 1, 2)

        self.groupBox_mat_properties = QGroupBox(self.tab_mat_assignment)
        self.groupBox_mat_properties.setObjectName(u"groupBox_mat_properties")
        self.gridLayout_68 = QGridLayout(self.groupBox_mat_properties)
        self.gridLayout_68.setObjectName(u"gridLayout_68")
        self.element = QLineEdit(self.groupBox_mat_properties)
        self.element.setObjectName(u"element")

        self.gridLayout_68.addWidget(self.element, 2, 0, 1, 2)

        self.Add_mat = QPushButton(self.groupBox_mat_properties)
        self.Add_mat.setObjectName(u"Add_mat")

        self.gridLayout_68.addWidget(self.Add_mat, 1, 0, 1, 1)

        self.add_element = QPushButton(self.groupBox_mat_properties)
        self.add_element.setObjectName(u"add_element")

        self.gridLayout_68.addWidget(self.add_element, 2, 2, 1, 1)

        self.del_element = QPushButton(self.groupBox_mat_properties)
        self.del_element.setObjectName(u"del_element")

        self.gridLayout_68.addWidget(self.del_element, 2, 3, 1, 1)

        self.hs_mat_2 = QSpacerItem(295, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_68.addItem(self.hs_mat_2, 1, 2, 1, 2)

        self.del_mat = QPushButton(self.groupBox_mat_properties)
        self.del_mat.setObjectName(u"del_mat")

        self.gridLayout_68.addWidget(self.del_mat, 1, 1, 1, 1)

        self.mat_table = QTableWidget(self.groupBox_mat_properties)
        self.mat_table.setObjectName(u"mat_table")

        self.gridLayout_68.addWidget(self.mat_table, 0, 0, 1, 6)

        self.save_mat_table = QPushButton(self.groupBox_mat_properties)
        self.save_mat_table.setObjectName(u"save_mat_table")

        self.gridLayout_68.addWidget(self.save_mat_table, 1, 4, 1, 2)

        self.undo_mat_tab = QPushButton(self.groupBox_mat_properties)
        self.undo_mat_tab.setObjectName(u"undo_mat_tab")

        self.gridLayout_68.addWidget(self.undo_mat_tab, 2, 4, 1, 2)


        self.gridLayout_69.addWidget(self.groupBox_mat_properties, 0, 2, 5, 1)

        self.mat_to_HU_box = QGroupBox(self.tab_mat_assignment)
        self.mat_to_HU_box.setObjectName(u"mat_to_HU_box")
        self.gridLayout_71 = QGridLayout(self.mat_to_HU_box)
        self.gridLayout_71.setObjectName(u"gridLayout_71")
        self.tableMatToHU = QTableWidget(self.mat_to_HU_box)
        self.tableMatToHU.setObjectName(u"tableMatToHU")

        self.gridLayout_71.addWidget(self.tableMatToHU, 0, 0, 1, 1)

        self.remove_mat_fromhu = QPushButton(self.mat_to_HU_box)
        self.remove_mat_fromhu.setObjectName(u"remove_mat_fromhu")

        self.gridLayout_71.addWidget(self.remove_mat_fromhu, 1, 0, 1, 1)


        self.gridLayout_69.addWidget(self.mat_to_HU_box, 1, 0, 1, 1)

        self.del_mat_map = QPushButton(self.tab_mat_assignment)
        self.del_mat_map.setObjectName(u"del_mat_map")

        self.gridLayout_69.addWidget(self.del_mat_map, 2, 1, 1, 1)

        self.create_mat_map = QPushButton(self.tab_mat_assignment)
        self.create_mat_map.setObjectName(u"create_mat_map")

        self.gridLayout_69.addWidget(self.create_mat_map, 2, 0, 1, 1)

        self.gridLayout_69.setRowStretch(0, 1)
        self.gridLayout_69.setRowStretch(1, 10)
        self.gridLayout_69.setRowStretch(2, 1)
        self.gridLayout_69.setColumnStretch(0, 1)
        self.gridLayout_69.setColumnStretch(1, 1)
        self.gridLayout_69.setColumnStretch(2, 4)
        self.Plan_tabs.addTab(self.tab_mat_assignment, "")
        self.density_map_tab = QWidget()
        self.density_map_tab.setObjectName(u"density_map_tab")
        self.gridLayout_58 = QGridLayout(self.density_map_tab)
        self.gridLayout_58.setObjectName(u"gridLayout_58")
        self.ct_cal_input = QWidget(self.density_map_tab)
        self.ct_cal_input.setObjectName(u"ct_cal_input")
        self.gridLayout_57 = QGridLayout(self.ct_cal_input)
        self.gridLayout_57.setObjectName(u"gridLayout_57")
        self.save_changes_ct_cal = QPushButton(self.ct_cal_input)
        self.save_changes_ct_cal.setObjectName(u"save_changes_ct_cal")

        self.gridLayout_57.addWidget(self.save_changes_ct_cal, 1, 0, 1, 1)

        self.ct_cal_table = QTableWidget(self.ct_cal_input)
        self.ct_cal_table.setObjectName(u"ct_cal_table")

        self.gridLayout_57.addWidget(self.ct_cal_table, 2, 0, 1, 2)

        self.Export_ct_cal = QPushButton(self.ct_cal_input)
        self.Export_ct_cal.setObjectName(u"Export_ct_cal")

        self.gridLayout_57.addWidget(self.Export_ct_cal, 1, 1, 1, 1)

        self.load_ct_cal = QPushButton(self.ct_cal_input)
        self.load_ct_cal.setObjectName(u"load_ct_cal")

        self.gridLayout_57.addWidget(self.load_ct_cal, 0, 1, 1, 1)

        self.ct_cal_save_copy = QPushButton(self.ct_cal_input)
        self.ct_cal_save_copy.setObjectName(u"ct_cal_save_copy")

        self.gridLayout_57.addWidget(self.ct_cal_save_copy, 3, 1, 1, 1)

        self.ct_cal_list = QComboBox(self.ct_cal_input)
        self.ct_cal_list.setObjectName(u"ct_cal_list")
        self.ct_cal_list.setEditable(True)

        self.gridLayout_57.addWidget(self.ct_cal_list, 0, 0, 1, 1)

        self.ct_cal_add_row = QPushButton(self.ct_cal_input)
        self.ct_cal_add_row.setObjectName(u"ct_cal_add_row")

        self.gridLayout_57.addWidget(self.ct_cal_add_row, 3, 0, 1, 1)


        self.gridLayout_58.addWidget(self.ct_cal_input, 0, 0, 1, 2)

        self.ct_cal_plot = QWidget(self.density_map_tab)
        self.ct_cal_plot.setObjectName(u"ct_cal_plot")

        self.gridLayout_58.addWidget(self.ct_cal_plot, 0, 2, 1, 1)

        self.create_density_map = QPushButton(self.density_map_tab)
        self.create_density_map.setObjectName(u"create_density_map")

        self.gridLayout_58.addWidget(self.create_density_map, 1, 0, 1, 1)

        self.create_density_map__from_mat_map = QPushButton(self.density_map_tab)
        self.create_density_map__from_mat_map.setObjectName(u"create_density_map__from_mat_map")

        self.gridLayout_58.addWidget(self.create_density_map__from_mat_map, 2, 0, 1, 1)

        self.vspacer_ct_cal = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_58.addItem(self.vspacer_ct_cal, 3, 0, 1, 1)

        self.delete_density_map = QPushButton(self.density_map_tab)
        self.delete_density_map.setObjectName(u"delete_density_map")

        self.gridLayout_58.addWidget(self.delete_density_map, 2, 1, 1, 1)

        self.override_no_tissue = QCheckBox(self.density_map_tab)
        self.override_no_tissue.setObjectName(u"override_no_tissue")

        self.gridLayout_58.addWidget(self.override_no_tissue, 1, 1, 1, 1)

        self.gridLayout_58.setRowStretch(0, 6)
        self.gridLayout_58.setRowStretch(1, 2)
        self.gridLayout_58.setRowStretch(2, 2)
        self.gridLayout_58.setColumnStretch(0, 1)
        self.gridLayout_58.setColumnStretch(1, 1)
        self.gridLayout_58.setColumnStretch(2, 6)
        self.Plan_tabs.addTab(self.density_map_tab, "")

        self.gridLayout_42.addWidget(self.Plan_tabs, 0, 0, 1, 1)

        self.tabModules.addTab(self.Plan_tab, "")
        self.IrIS_tab = QWidget()
        self.IrIS_tab.setObjectName(u"IrIS_tab")
        self.gridLayout_10 = QGridLayout(self.IrIS_tab)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.tabWidget_5 = QTabWidget(self.IrIS_tab)
        self.tabWidget_5.setObjectName(u"tabWidget_5")
        self.tab_23 = QWidget()
        self.tab_23.setObjectName(u"tab_23")
        self.tabWidget_5.addTab(self.tab_23, "")
        self.tab_24 = QWidget()
        self.tab_24.setObjectName(u"tab_24")
        self.tabWidget_5.addTab(self.tab_24, "")
        self.tab_15 = QWidget()
        self.tab_15.setObjectName(u"tab_15")
        self.gridLayout_11 = QGridLayout(self.tab_15)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.line_9 = QFrame(self.tab_15)
        self.line_9.setObjectName(u"line_9")
        self.line_9.setFrameShape(QFrame.Shape.HLine)
        self.line_9.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_11.addWidget(self.line_9, 2, 0, 1, 3)

        self.IrIS_cal_widget01 = QWidget(self.tab_15)
        self.IrIS_cal_widget01.setObjectName(u"IrIS_cal_widget01")

        self.gridLayout_11.addWidget(self.IrIS_cal_widget01, 1, 0, 1, 1)

        self.IrIS_cal_widget02 = QWidget(self.tab_15)
        self.IrIS_cal_widget02.setObjectName(u"IrIS_cal_widget02")
        self.IrIS_cal_widget02.setEnabled(True)

        self.gridLayout_11.addWidget(self.IrIS_cal_widget02, 1, 1, 1, 1)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_11.addItem(self.verticalSpacer_6, 3, 0, 1, 1)

        self.tabWidget_7 = QTabWidget(self.tab_15)
        self.tabWidget_7.setObjectName(u"tabWidget_7")
        self.tab_28 = QWidget()
        self.tab_28.setObjectName(u"tab_28")
        self.gridLayout_27 = QGridLayout(self.tab_28)
        self.gridLayout_27.setObjectName(u"gridLayout_27")
        self.IrIS_cal_MK_02 = QDoubleSpinBox(self.tab_28)
        self.IrIS_cal_MK_02.setObjectName(u"IrIS_cal_MK_02")
        self.IrIS_cal_MK_02.setMinimum(-999999.000000000000000)
        self.IrIS_cal_MK_02.setMaximum(9999999.000000000000000)
        self.IrIS_cal_MK_02.setValue(0.000000000000000)

        self.gridLayout_27.addWidget(self.IrIS_cal_MK_02, 3, 2, 1, 1)

        self.IrIS_cal_Sour_01 = QDoubleSpinBox(self.tab_28)
        self.IrIS_cal_Sour_01.setObjectName(u"IrIS_cal_Sour_01")
        self.IrIS_cal_Sour_01.setMinimum(-999999.000000000000000)
        self.IrIS_cal_Sour_01.setMaximum(9999999.000000000000000)
        self.IrIS_cal_Sour_01.setValue(177.000000000000000)

        self.gridLayout_27.addWidget(self.IrIS_cal_Sour_01, 5, 0, 1, 1)

        self.horizontalSpacer_21 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_27.addItem(self.horizontalSpacer_21, 18, 13, 1, 1)

        self.IrIS_cal_MK_06 = QDoubleSpinBox(self.tab_28)
        self.IrIS_cal_MK_06.setObjectName(u"IrIS_cal_MK_06")
        self.IrIS_cal_MK_06.setMinimum(-999999.000000000000000)
        self.IrIS_cal_MK_06.setMaximum(9999999.000000000000000)

        self.gridLayout_27.addWidget(self.IrIS_cal_MK_06, 3, 6, 1, 1)

        self.IrIS_cal_MK_01 = QDoubleSpinBox(self.tab_28)
        self.IrIS_cal_MK_01.setObjectName(u"IrIS_cal_MK_01")
        self.IrIS_cal_MK_01.setMinimum(-999999.000000000000000)
        self.IrIS_cal_MK_01.setMaximum(9999999.000000000000000)
        self.IrIS_cal_MK_01.setValue(0.000000000000000)

        self.gridLayout_27.addWidget(self.IrIS_cal_MK_01, 3, 0, 1, 1)

        self.IrIS_cal_MK_03 = QDoubleSpinBox(self.tab_28)
        self.IrIS_cal_MK_03.setObjectName(u"IrIS_cal_MK_03")
        self.IrIS_cal_MK_03.setMinimum(-999999.000000000000000)
        self.IrIS_cal_MK_03.setMaximum(9999999.000000000000000)

        self.gridLayout_27.addWidget(self.IrIS_cal_MK_03, 3, 3, 1, 1)

        self.line_20 = QFrame(self.tab_28)
        self.line_20.setObjectName(u"line_20")
        self.line_20.setFrameShape(QFrame.Shape.HLine)
        self.line_20.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_27.addWidget(self.line_20, 1, 0, 1, 16)

        self.IrIS_cal_load_meas = QPushButton(self.tab_28)
        self.IrIS_cal_load_meas.setObjectName(u"IrIS_cal_load_meas")

        self.gridLayout_27.addWidget(self.IrIS_cal_load_meas, 18, 11, 1, 1)

        self.IrIS_cal_MK_04 = QDoubleSpinBox(self.tab_28)
        self.IrIS_cal_MK_04.setObjectName(u"IrIS_cal_MK_04")
        self.IrIS_cal_MK_04.setMinimum(-999999.000000000000000)
        self.IrIS_cal_MK_04.setMaximum(9999999.000000000000000)

        self.gridLayout_27.addWidget(self.IrIS_cal_MK_04, 3, 4, 1, 1)

        self.IrIS_cal_ref_table = QTableWidget(self.tab_28)
        self.IrIS_cal_ref_table.setObjectName(u"IrIS_cal_ref_table")

        self.gridLayout_27.addWidget(self.IrIS_cal_ref_table, 2, 11, 16, 5)

        self.lineEdit_44 = QLineEdit(self.tab_28)
        self.lineEdit_44.setObjectName(u"lineEdit_44")
        self.lineEdit_44.setEnabled(False)

        self.gridLayout_27.addWidget(self.lineEdit_44, 2, 0, 1, 4)

        self.IrIS_cal_load_ref = QPushButton(self.tab_28)
        self.IrIS_cal_load_ref.setObjectName(u"IrIS_cal_load_ref")

        self.gridLayout_27.addWidget(self.IrIS_cal_load_ref, 18, 12, 1, 1)

        self.line_21 = QFrame(self.tab_28)
        self.line_21.setObjectName(u"line_21")
        self.line_21.setFrameShape(QFrame.Shape.VLine)
        self.line_21.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_27.addWidget(self.line_21, 2, 10, 18, 1)

        self.IrIS_cal_MK_05 = QDoubleSpinBox(self.tab_28)
        self.IrIS_cal_MK_05.setObjectName(u"IrIS_cal_MK_05")
        self.IrIS_cal_MK_05.setMinimum(-999999.000000000000000)
        self.IrIS_cal_MK_05.setMaximum(9999999.000000000000000)

        self.gridLayout_27.addWidget(self.IrIS_cal_MK_05, 3, 5, 1, 1)

        self.lineEdit_45 = QLineEdit(self.tab_28)
        self.lineEdit_45.setObjectName(u"lineEdit_45")
        self.lineEdit_45.setEnabled(False)

        self.gridLayout_27.addWidget(self.lineEdit_45, 2, 4, 1, 3)

        self.lineEdit_43 = QLineEdit(self.tab_28)
        self.lineEdit_43.setObjectName(u"lineEdit_43")
        self.lineEdit_43.setEnabled(False)

        self.gridLayout_27.addWidget(self.lineEdit_43, 4, 0, 1, 4)

        self.IrIS_cal_Sour_02 = QDoubleSpinBox(self.tab_28)
        self.IrIS_cal_Sour_02.setObjectName(u"IrIS_cal_Sour_02")
        self.IrIS_cal_Sour_02.setMinimum(-999999.000000000000000)
        self.IrIS_cal_Sour_02.setMaximum(9999999.000000000000000)
        self.IrIS_cal_Sour_02.setValue(217.500000000000000)

        self.gridLayout_27.addWidget(self.IrIS_cal_Sour_02, 5, 2, 1, 1)

        self.IrIS_cal_Sour_03 = QDoubleSpinBox(self.tab_28)
        self.IrIS_cal_Sour_03.setObjectName(u"IrIS_cal_Sour_03")
        self.IrIS_cal_Sour_03.setMinimum(-999999.000000000000000)
        self.IrIS_cal_Sour_03.setMaximum(9999999.000000000000000)
        self.IrIS_cal_Sour_03.setValue(370.000000000000000)

        self.gridLayout_27.addWidget(self.IrIS_cal_Sour_03, 5, 3, 1, 1)

        self.lineEdit_40 = QLineEdit(self.tab_28)
        self.lineEdit_40.setObjectName(u"lineEdit_40")
        self.lineEdit_40.setEnabled(False)

        self.gridLayout_27.addWidget(self.lineEdit_40, 4, 4, 1, 2)

        self.IrIS_cal_Ref_MK_ID = QSpinBox(self.tab_28)
        self.IrIS_cal_Ref_MK_ID.setObjectName(u"IrIS_cal_Ref_MK_ID")
        self.IrIS_cal_Ref_MK_ID.setValue(0)

        self.gridLayout_27.addWidget(self.IrIS_cal_Ref_MK_ID, 4, 6, 1, 1)

        self.IrIS_Cal_plot_deg = QCheckBox(self.tab_28)
        self.IrIS_Cal_plot_deg.setObjectName(u"IrIS_Cal_plot_deg")

        self.gridLayout_27.addWidget(self.IrIS_Cal_plot_deg, 5, 4, 1, 1)

        self.IrIS_Cal_plot_mm = QCheckBox(self.tab_28)
        self.IrIS_Cal_plot_mm.setObjectName(u"IrIS_Cal_plot_mm")
        self.IrIS_Cal_plot_mm.setChecked(True)

        self.gridLayout_27.addWidget(self.IrIS_Cal_plot_mm, 5, 5, 1, 1)

        self.IrIS_cal_plot = QPushButton(self.tab_28)
        self.IrIS_cal_plot.setObjectName(u"IrIS_cal_plot")

        self.gridLayout_27.addWidget(self.IrIS_cal_plot, 5, 6, 1, 1)

        self.line_22 = QFrame(self.tab_28)
        self.line_22.setObjectName(u"line_22")
        self.line_22.setFrameShape(QFrame.Shape.HLine)
        self.line_22.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_27.addWidget(self.line_22, 6, 0, 1, 7)

        self.IrIS_cal_save = QPushButton(self.tab_28)
        self.IrIS_cal_save.setObjectName(u"IrIS_cal_save")

        self.gridLayout_27.addWidget(self.IrIS_cal_save, 7, 6, 1, 1)

        self.IrIS_cal_export = QPushButton(self.tab_28)
        self.IrIS_cal_export.setObjectName(u"IrIS_cal_export")

        self.gridLayout_27.addWidget(self.IrIS_cal_export, 7, 5, 1, 1)

        self.IrIS_cal_findMK = QPushButton(self.tab_28)
        self.IrIS_cal_findMK.setObjectName(u"IrIS_cal_findMK")

        self.gridLayout_27.addWidget(self.IrIS_cal_findMK, 7, 0, 1, 1)

        self.ref_frame_cal_IrIS = QSpinBox(self.tab_28)
        self.ref_frame_cal_IrIS.setObjectName(u"ref_frame_cal_IrIS")

        self.gridLayout_27.addWidget(self.ref_frame_cal_IrIS, 7, 2, 1, 1)

        self.lineEdit_11 = QLineEdit(self.tab_28)
        self.lineEdit_11.setObjectName(u"lineEdit_11")
        self.lineEdit_11.setEnabled(False)

        self.gridLayout_27.addWidget(self.lineEdit_11, 7, 3, 1, 1)

        self.tabWidget_7.addTab(self.tab_28, "")
        self.tab_29 = QWidget()
        self.tab_29.setObjectName(u"tab_29")
        self.tabWidget_7.addTab(self.tab_29, "")

        self.gridLayout_11.addWidget(self.tabWidget_7, 4, 0, 1, 3)

        self.tabWidget_5.addTab(self.tab_15, "")
        self.tab_16 = QWidget()
        self.tab_16.setObjectName(u"tab_16")
        self.gridLayout_18 = QGridLayout(self.tab_16)
        self.gridLayout_18.setObjectName(u"gridLayout_18")
        self.groupBox_4 = QGroupBox(self.tab_16)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_20 = QGridLayout(self.groupBox_4)
        self.gridLayout_20.setObjectName(u"gridLayout_20")
        self.tabWidget = QTabWidget(self.groupBox_4)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_20 = QWidget()
        self.tab_20.setObjectName(u"tab_20")
        self.gridLayout_22 = QGridLayout(self.tab_20)
        self.gridLayout_22.setObjectName(u"gridLayout_22")
        self.pushButton_13 = QPushButton(self.tab_20)
        self.pushButton_13.setObjectName(u"pushButton_13")

        self.gridLayout_22.addWidget(self.pushButton_13, 5, 2, 1, 1)

        self.groupBox_7 = QGroupBox(self.tab_20)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.gridLayout_23 = QGridLayout(self.groupBox_7)
        self.gridLayout_23.setObjectName(u"gridLayout_23")
        self.IrISPlot03 = QComboBox(self.groupBox_7)
        self.IrISPlot03.setObjectName(u"IrISPlot03")

        self.gridLayout_23.addWidget(self.IrISPlot03, 5, 0, 1, 2)

        self.lineEdit_38 = QLineEdit(self.groupBox_7)
        self.lineEdit_38.setObjectName(u"lineEdit_38")

        self.gridLayout_23.addWidget(self.lineEdit_38, 0, 0, 1, 1)

        self.DownSizeN_IrIS = QSpinBox(self.groupBox_7)
        self.DownSizeN_IrIS.setObjectName(u"DownSizeN_IrIS")
        self.DownSizeN_IrIS.setValue(16)

        self.gridLayout_23.addWidget(self.DownSizeN_IrIS, 0, 3, 1, 1)

        self.IrISPlot01 = QComboBox(self.groupBox_7)
        self.IrISPlot01.setObjectName(u"IrISPlot01")
        self.IrISPlot01.setAcceptDrops(False)

        self.gridLayout_23.addWidget(self.IrISPlot01, 2, 0, 1, 2)

        self.IrIS_grad_frame = QSpinBox(self.groupBox_7)
        self.IrIS_grad_frame.setObjectName(u"IrIS_grad_frame")
        self.IrIS_grad_frame.setMinimum(1)

        self.gridLayout_23.addWidget(self.IrIS_grad_frame, 0, 1, 1, 1)

        self.IrIS_ProcessPlot = QPushButton(self.groupBox_7)
        self.IrIS_ProcessPlot.setObjectName(u"IrIS_ProcessPlot")

        self.gridLayout_23.addWidget(self.IrIS_ProcessPlot, 5, 3, 1, 1)

        self.IrISPlot02 = QComboBox(self.groupBox_7)
        self.IrISPlot02.setObjectName(u"IrISPlot02")

        self.gridLayout_23.addWidget(self.IrISPlot02, 2, 2, 1, 2)

        self.line_17 = QFrame(self.groupBox_7)
        self.line_17.setObjectName(u"line_17")
        self.line_17.setFrameShape(QFrame.Shape.HLine)
        self.line_17.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_23.addWidget(self.line_17, 1, 0, 1, 1)

        self.lineEdit_25 = QLineEdit(self.groupBox_7)
        self.lineEdit_25.setObjectName(u"lineEdit_25")

        self.gridLayout_23.addWidget(self.lineEdit_25, 0, 2, 1, 1)

        self.IrIS_Plot = QPushButton(self.groupBox_7)
        self.IrIS_Plot.setObjectName(u"IrIS_Plot")

        self.gridLayout_23.addWidget(self.IrIS_Plot, 5, 2, 1, 1)


        self.gridLayout_22.addWidget(self.groupBox_7, 1, 0, 1, 5)

        self.IrIS_findPK = QPushButton(self.tab_20)
        self.IrIS_findPK.setObjectName(u"IrIS_findPK")

        self.gridLayout_22.addWidget(self.IrIS_findPK, 5, 0, 1, 1)

        self.line_14 = QFrame(self.tab_20)
        self.line_14.setObjectName(u"line_14")
        self.line_14.setFrameShape(QFrame.Shape.HLine)
        self.line_14.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_22.addWidget(self.line_14, 0, 0, 1, 1)

        self.horizontalSpacer_20 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_22.addItem(self.horizontalSpacer_20, 5, 1, 1, 1)

        self.Average = QGroupBox(self.tab_20)
        self.Average.setObjectName(u"Average")
        self.gridLayout_24 = QGridLayout(self.Average)
        self.gridLayout_24.setObjectName(u"gridLayout_24")
        self.IrIsAVg_dw = QPushButton(self.Average)
        self.IrIsAVg_dw.setObjectName(u"IrIsAVg_dw")

        self.gridLayout_24.addWidget(self.IrIsAVg_dw, 0, 6, 1, 1)

        self.lineEdit_10 = QLineEdit(self.Average)
        self.lineEdit_10.setObjectName(u"lineEdit_10")
        self.lineEdit_10.setEnabled(False)

        self.gridLayout_24.addWidget(self.lineEdit_10, 0, 1, 1, 4)

        self.IrIsAVg_dw_margin = QSpinBox(self.Average)
        self.IrIsAVg_dw_margin.setObjectName(u"IrIsAVg_dw_margin")

        self.gridLayout_24.addWidget(self.IrIsAVg_dw_margin, 0, 5, 1, 1)


        self.gridLayout_22.addWidget(self.Average, 2, 0, 1, 5)

        self.checkBox_IrIS_time_rel = QCheckBox(self.tab_20)
        self.checkBox_IrIS_time_rel.setObjectName(u"checkBox_IrIS_time_rel")
        self.checkBox_IrIS_time_rel.setChecked(True)

        self.gridLayout_22.addWidget(self.checkBox_IrIS_time_rel, 4, 0, 1, 1)

        self.groupBox_6 = QGroupBox(self.tab_20)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.gridLayout_25 = QGridLayout(self.groupBox_6)
        self.gridLayout_25.setObjectName(u"gridLayout_25")
        self.avg_frames_within_dwell_N = QSpinBox(self.groupBox_6)
        self.avg_frames_within_dwell_N.setObjectName(u"avg_frames_within_dwell_N")
        self.avg_frames_within_dwell_N.setValue(2)

        self.gridLayout_25.addWidget(self.avg_frames_within_dwell_N, 1, 2, 1, 1)

        self.IrIsAVg_Framesdw = QPushButton(self.groupBox_6)
        self.IrIsAVg_Framesdw.setObjectName(u"IrIsAVg_Framesdw")

        self.gridLayout_25.addWidget(self.IrIsAVg_Framesdw, 1, 3, 1, 1)

        self.lineEdit_12 = QLineEdit(self.groupBox_6)
        self.lineEdit_12.setObjectName(u"lineEdit_12")
        self.lineEdit_12.setEnabled(False)

        self.gridLayout_25.addWidget(self.lineEdit_12, 1, 0, 1, 1)


        self.gridLayout_22.addWidget(self.groupBox_6, 3, 0, 1, 5)

        self.IrIS_ExportCSV = QPushButton(self.tab_20)
        self.IrIS_ExportCSV.setObjectName(u"IrIS_ExportCSV")

        self.gridLayout_22.addWidget(self.IrIS_ExportCSV, 5, 4, 1, 1)

        self.tabWidget.addTab(self.tab_20, "")
        self.tab_21 = QWidget()
        self.tab_21.setObjectName(u"tab_21")
        self.gridLayout_21 = QGridLayout(self.tab_21)
        self.gridLayout_21.setObjectName(u"gridLayout_21")
        self.remove_dw_table = QPushButton(self.tab_21)
        self.remove_dw_table.setObjectName(u"remove_dw_table")

        self.gridLayout_21.addWidget(self.remove_dw_table, 1, 1, 1, 1)

        self.add_dw_table = QPushButton(self.tab_21)
        self.add_dw_table.setObjectName(u"add_dw_table")

        self.gridLayout_21.addWidget(self.add_dw_table, 1, 0, 1, 1)

        self.dw_table_pos = QSpinBox(self.tab_21)
        self.dw_table_pos.setObjectName(u"dw_table_pos")
        self.dw_table_pos.setMinimum(1)
        self.dw_table_pos.setMaximum(9999)
        self.dw_table_pos.setValue(1)

        self.gridLayout_21.addWidget(self.dw_table_pos, 1, 2, 1, 1)

        self.Dwells_table = QTableWidget(self.tab_21)
        self.Dwells_table.setObjectName(u"Dwells_table")

        self.gridLayout_21.addWidget(self.Dwells_table, 0, 0, 1, 3)

        self.tabWidget.addTab(self.tab_21, "")
        self.tab_22 = QWidget()
        self.tab_22.setObjectName(u"tab_22")
        self.gridLayout_26 = QGridLayout(self.tab_22)
        self.gridLayout_26.setObjectName(u"gridLayout_26")
        self.lineEdit_34 = QLineEdit(self.tab_22)
        self.lineEdit_34.setObjectName(u"lineEdit_34")
        self.lineEdit_34.setEnabled(False)
        self.lineEdit_34.setFont(font)

        self.gridLayout_26.addWidget(self.lineEdit_34, 14, 0, 1, 1)

        self.Pk_find_13 = QSpinBox(self.tab_22)
        self.Pk_find_13.setObjectName(u"Pk_find_13")

        self.gridLayout_26.addWidget(self.Pk_find_13, 14, 1, 1, 1)

        self.lineEdit_27 = QLineEdit(self.tab_22)
        self.lineEdit_27.setObjectName(u"lineEdit_27")
        self.lineEdit_27.setEnabled(False)
        self.lineEdit_27.setFont(font)

        self.gridLayout_26.addWidget(self.lineEdit_27, 2, 2, 1, 1)

        self.Pk_find_01 = QDoubleSpinBox(self.tab_22)
        self.Pk_find_01.setObjectName(u"Pk_find_01")
        self.Pk_find_01.setMinimum(-99999999.000000000000000)
        self.Pk_find_01.setMaximum(999999999.000000000000000)
        self.Pk_find_01.setValue(2.500000000000000)

        self.gridLayout_26.addWidget(self.Pk_find_01, 2, 1, 1, 1)

        self.lineEdit_33 = QLineEdit(self.tab_22)
        self.lineEdit_33.setObjectName(u"lineEdit_33")
        self.lineEdit_33.setEnabled(False)
        self.lineEdit_33.setFont(font)

        self.gridLayout_26.addWidget(self.lineEdit_33, 8, 2, 1, 1)

        self.Pk_find_06 = QDoubleSpinBox(self.tab_22)
        self.Pk_find_06.setObjectName(u"Pk_find_06")
        self.Pk_find_06.setMinimum(-99999999.000000000000000)
        self.Pk_find_06.setMaximum(999999999.000000000000000)
        self.Pk_find_06.setValue(-1.000000000000000)

        self.gridLayout_26.addWidget(self.Pk_find_06, 6, 3, 1, 1)

        self.lineEdit_30 = QLineEdit(self.tab_22)
        self.lineEdit_30.setObjectName(u"lineEdit_30")
        self.lineEdit_30.setEnabled(False)
        self.lineEdit_30.setFont(font)

        self.gridLayout_26.addWidget(self.lineEdit_30, 8, 0, 1, 1)

        self.line_16 = QFrame(self.tab_22)
        self.line_16.setObjectName(u"line_16")
        self.line_16.setFrameShape(QFrame.Shape.HLine)
        self.line_16.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_26.addWidget(self.line_16, 10, 0, 1, 2)

        self.Pk_find_05 = QDoubleSpinBox(self.tab_22)
        self.Pk_find_05.setObjectName(u"Pk_find_05")
        self.Pk_find_05.setMinimum(-99999999.000000000000000)
        self.Pk_find_05.setMaximum(999999999.000000000000000)
        self.Pk_find_05.setValue(1.000000000000000)

        self.gridLayout_26.addWidget(self.Pk_find_05, 6, 1, 1, 1)

        self.Pk_find_07 = QDoubleSpinBox(self.tab_22)
        self.Pk_find_07.setObjectName(u"Pk_find_07")
        self.Pk_find_07.setMinimum(-99999999.000000000000000)
        self.Pk_find_07.setMaximum(999999999.000000000000000)
        self.Pk_find_07.setValue(1.000000000000000)

        self.gridLayout_26.addWidget(self.Pk_find_07, 8, 1, 1, 1)

        self.Pk_find_03 = QDoubleSpinBox(self.tab_22)
        self.Pk_find_03.setObjectName(u"Pk_find_03")
        self.Pk_find_03.setMinimum(-99999999.000000000000000)
        self.Pk_find_03.setMaximum(999999999.000000000000000)
        self.Pk_find_03.setValue(1.000000000000000)

        self.gridLayout_26.addWidget(self.Pk_find_03, 4, 1, 1, 1)

        self.lineEdit_29 = QLineEdit(self.tab_22)
        self.lineEdit_29.setObjectName(u"lineEdit_29")
        self.lineEdit_29.setEnabled(False)
        self.lineEdit_29.setFont(font)

        self.gridLayout_26.addWidget(self.lineEdit_29, 4, 2, 1, 1)

        self.lineEdit_26 = QLineEdit(self.tab_22)
        self.lineEdit_26.setObjectName(u"lineEdit_26")
        self.lineEdit_26.setEnabled(False)
        self.lineEdit_26.setFont(font)

        self.gridLayout_26.addWidget(self.lineEdit_26, 2, 0, 1, 1)

        self.lineEdit_35 = QLineEdit(self.tab_22)
        self.lineEdit_35.setObjectName(u"lineEdit_35")
        self.lineEdit_35.setEnabled(False)
        self.lineEdit_35.setFont(font)

        self.gridLayout_26.addWidget(self.lineEdit_35, 14, 2, 1, 1)

        self.Pk_find_04 = QDoubleSpinBox(self.tab_22)
        self.Pk_find_04.setObjectName(u"Pk_find_04")
        self.Pk_find_04.setMinimum(-99999999.000000000000000)
        self.Pk_find_04.setMaximum(999999999.000000000000000)
        self.Pk_find_04.setValue(1.000000000000000)

        self.gridLayout_26.addWidget(self.Pk_find_04, 4, 3, 1, 1)

        self.line_15 = QFrame(self.tab_22)
        self.line_15.setObjectName(u"line_15")
        self.line_15.setFrameShape(QFrame.Shape.HLine)
        self.line_15.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_26.addWidget(self.line_15, 1, 0, 1, 1)

        self.checkBox_Pk_find_range = QCheckBox(self.tab_22)
        self.checkBox_Pk_find_range.setObjectName(u"checkBox_Pk_find_range")
        self.checkBox_Pk_find_range.setChecked(True)

        self.gridLayout_26.addWidget(self.checkBox_Pk_find_range, 12, 0, 1, 1)

        self.lineEdit_36 = QLineEdit(self.tab_22)
        self.lineEdit_36.setObjectName(u"lineEdit_36")
        self.lineEdit_36.setEnabled(False)
        self.lineEdit_36.setFont(font)
        self.lineEdit_36.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_26.addWidget(self.lineEdit_36, 0, 0, 1, 4)

        self.lineEdit_32 = QLineEdit(self.tab_22)
        self.lineEdit_32.setObjectName(u"lineEdit_32")
        self.lineEdit_32.setEnabled(False)
        self.lineEdit_32.setFont(font)

        self.gridLayout_26.addWidget(self.lineEdit_32, 6, 2, 1, 1)

        self.Pk_find_09 = QDoubleSpinBox(self.tab_22)
        self.Pk_find_09.setObjectName(u"Pk_find_09")
        self.Pk_find_09.setValue(0.800000000000000)

        self.gridLayout_26.addWidget(self.Pk_find_09, 12, 1, 1, 1)

        self.lineEdit_31 = QLineEdit(self.tab_22)
        self.lineEdit_31.setObjectName(u"lineEdit_31")
        self.lineEdit_31.setEnabled(False)
        self.lineEdit_31.setFont(font)

        self.gridLayout_26.addWidget(self.lineEdit_31, 6, 0, 1, 1)

        self.lineEdit_28 = QLineEdit(self.tab_22)
        self.lineEdit_28.setObjectName(u"lineEdit_28")
        self.lineEdit_28.setEnabled(False)
        self.lineEdit_28.setFont(font)

        self.gridLayout_26.addWidget(self.lineEdit_28, 4, 0, 1, 1)

        self.Pk_find_08 = QDoubleSpinBox(self.tab_22)
        self.Pk_find_08.setObjectName(u"Pk_find_08")
        self.Pk_find_08.setMinimum(-99999999.000000000000000)
        self.Pk_find_08.setMaximum(999999999.000000000000000)
        self.Pk_find_08.setValue(1.000000000000000)

        self.gridLayout_26.addWidget(self.Pk_find_08, 8, 3, 1, 1)

        self.lineEdit_37 = QLineEdit(self.tab_22)
        self.lineEdit_37.setObjectName(u"lineEdit_37")
        self.lineEdit_37.setEnabled(False)
        self.lineEdit_37.setFont(font)
        self.lineEdit_37.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_26.addWidget(self.lineEdit_37, 11, 0, 1, 4)

        self.Pk_find_02 = QDoubleSpinBox(self.tab_22)
        self.Pk_find_02.setObjectName(u"Pk_find_02")
        self.Pk_find_02.setMinimum(-99999999.000000000000000)
        self.Pk_find_02.setMaximum(999999999.000000000000000)
        self.Pk_find_02.setValue(-1.000000000000000)

        self.gridLayout_26.addWidget(self.Pk_find_02, 2, 3, 1, 1)

        self.Pk_Plot = QPushButton(self.tab_22)
        self.Pk_Plot.setObjectName(u"Pk_Plot")

        self.gridLayout_26.addWidget(self.Pk_Plot, 15, 3, 1, 1)

        self.Pk_find_14 = QSpinBox(self.tab_22)
        self.Pk_find_14.setObjectName(u"Pk_find_14")

        self.gridLayout_26.addWidget(self.Pk_find_14, 14, 3, 1, 1)

        self.Pk_find_10 = QDoubleSpinBox(self.tab_22)
        self.Pk_find_10.setObjectName(u"Pk_find_10")
        self.Pk_find_10.setValue(1.200000000000000)

        self.gridLayout_26.addWidget(self.Pk_find_10, 13, 1, 1, 1)

        self.checkBox_Pk_find_adj_1st_last = QCheckBox(self.tab_22)
        self.checkBox_Pk_find_adj_1st_last.setObjectName(u"checkBox_Pk_find_adj_1st_last")
        self.checkBox_Pk_find_adj_1st_last.setChecked(True)

        self.gridLayout_26.addWidget(self.checkBox_Pk_find_adj_1st_last, 12, 2, 1, 1)

        self.Pk_find_11 = QSpinBox(self.tab_22)
        self.Pk_find_11.setObjectName(u"Pk_find_11")
        self.Pk_find_11.setMaximum(99999)
        self.Pk_find_11.setValue(20)

        self.gridLayout_26.addWidget(self.Pk_find_11, 12, 3, 1, 1)

        self.Pk_find_12 = QDoubleSpinBox(self.tab_22)
        self.Pk_find_12.setObjectName(u"Pk_find_12")
        self.Pk_find_12.setValue(0.100000000000000)

        self.gridLayout_26.addWidget(self.Pk_find_12, 13, 3, 1, 1)

        self.tabWidget.addTab(self.tab_22, "")
        self.tab_26 = QWidget()
        self.tab_26.setObjectName(u"tab_26")
        self.gridLayout_28 = QGridLayout(self.tab_26)
        self.gridLayout_28.setObjectName(u"gridLayout_28")
        self.Source_save_cal = QPushButton(self.tab_26)
        self.Source_save_cal.setObjectName(u"Source_save_cal")

        self.gridLayout_28.addWidget(self.Source_save_cal, 1, 1, 1, 1)

        self.horizontalSpacer_23 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_28.addItem(self.horizontalSpacer_23, 1, 0, 1, 1)

        self.Source_Cal_table = QTableWidget(self.tab_26)
        self.Source_Cal_table.setObjectName(u"Source_Cal_table")

        self.gridLayout_28.addWidget(self.Source_Cal_table, 0, 0, 1, 2)

        self.tabWidget.addTab(self.tab_26, "")

        self.gridLayout_20.addWidget(self.tabWidget, 0, 0, 1, 7)

        self.Pk_find_channel = QSpinBox(self.groupBox_4)
        self.Pk_find_channel.setObjectName(u"Pk_find_channel")
        self.Pk_find_channel.setMinimum(1)
        self.Pk_find_channel.setMaximum(9999)
        self.Pk_find_channel.setValue(1)

        self.gridLayout_20.addWidget(self.Pk_find_channel, 1, 6, 1, 1)

        self.horizontalSpacer_22 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_20.addItem(self.horizontalSpacer_22, 1, 1, 1, 1)

        self.IrIsAVg_loadSSD_check = QCheckBox(self.groupBox_4)
        self.IrIsAVg_loadSSD_check.setObjectName(u"IrIsAVg_loadSSD_check")

        self.gridLayout_20.addWidget(self.IrIsAVg_loadSSD_check, 1, 0, 1, 1)

        self.lineEdit_9 = QLineEdit(self.groupBox_4)
        self.lineEdit_9.setObjectName(u"lineEdit_9")
        self.lineEdit_9.setEnabled(False)
        self.lineEdit_9.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_20.addWidget(self.lineEdit_9, 1, 4, 1, 1)

        self.Pk_find_processl_all_check = QCheckBox(self.groupBox_4)
        self.Pk_find_processl_all_check.setObjectName(u"Pk_find_processl_all_check")
        self.Pk_find_processl_all_check.setChecked(True)

        self.gridLayout_20.addWidget(self.Pk_find_processl_all_check, 1, 3, 1, 1)


        self.gridLayout_18.addWidget(self.groupBox_4, 2, 0, 1, 1)

        self.horizontalSpacer_17 = QSpacerItem(30, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_18.addItem(self.horizontalSpacer_17, 3, 0, 1, 1)

        self.horizontalSpacer_18 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_18.addItem(self.horizontalSpacer_18, 3, 2, 1, 1)

        self.groupBox_3 = QGroupBox(self.tab_16)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_19 = QGridLayout(self.groupBox_3)
        self.gridLayout_19.setObjectName(u"gridLayout_19")
        self.Slider_Eval_IrIS = QSlider(self.groupBox_3)
        self.Slider_Eval_IrIS.setObjectName(u"Slider_Eval_IrIS")
        self.Slider_Eval_IrIS.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_19.addWidget(self.Slider_Eval_IrIS, 1, 0, 1, 1)

        self.IrIS_Ax_Eval_01 = QWidget(self.groupBox_3)
        self.IrIS_Ax_Eval_01.setObjectName(u"IrIS_Ax_Eval_01")

        self.gridLayout_19.addWidget(self.IrIS_Ax_Eval_01, 0, 0, 1, 2)

        self.List_Eval_Direction = QComboBox(self.groupBox_3)
        self.List_Eval_Direction.setObjectName(u"List_Eval_Direction")

        self.gridLayout_19.addWidget(self.List_Eval_Direction, 1, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_19.addItem(self.verticalSpacer, 1, 2, 1, 1)


        self.gridLayout_18.addWidget(self.groupBox_3, 0, 0, 1, 1)

        self.groupBox_5 = QGroupBox(self.tab_16)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.IrIS_Ax_Eval_02 = QWidget(self.groupBox_5)
        self.IrIS_Ax_Eval_02.setObjectName(u"IrIS_Ax_Eval_02")

        self.verticalLayout_2.addWidget(self.IrIS_Ax_Eval_02)

        self.IrIS_Ax_Eval_03 = QWidget(self.groupBox_5)
        self.IrIS_Ax_Eval_03.setObjectName(u"IrIS_Ax_Eval_03")

        self.verticalLayout_2.addWidget(self.IrIS_Ax_Eval_03)

        self.IrIS_Ax_Eval_04 = QWidget(self.groupBox_5)
        self.IrIS_Ax_Eval_04.setObjectName(u"IrIS_Ax_Eval_04")

        self.verticalLayout_2.addWidget(self.IrIS_Ax_Eval_04)


        self.gridLayout_18.addWidget(self.groupBox_5, 0, 1, 3, 2)

        self.line_13 = QFrame(self.tab_16)
        self.line_13.setObjectName(u"line_13")
        self.line_13.setFrameShape(QFrame.Shape.HLine)
        self.line_13.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_18.addWidget(self.line_13, 1, 0, 1, 1)

        self.horizontalSpacer_19 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_18.addItem(self.horizontalSpacer_19, 3, 1, 1, 1)

        self.tabWidget_5.addTab(self.tab_16, "")
        self.tab_25 = QWidget()
        self.tab_25.setObjectName(u"tab_25")
        self.tabWidget_5.addTab(self.tab_25, "")

        self.gridLayout_10.addWidget(self.tabWidget_5, 0, 1, 1, 1)

        self.tabModules.addTab(self.IrIS_tab, "")
        self.tab_27 = QWidget()
        self.tab_27.setObjectName(u"tab_27")
        self.gridLayout_29 = QGridLayout(self.tab_27)
        self.gridLayout_29.setObjectName(u"gridLayout_29")
        self.LoadCSVView = QPushButton(self.tab_27)
        self.LoadCSVView.setObjectName(u"LoadCSVView")
        self.LoadCSVView.setFont(font2)

        self.gridLayout_29.addWidget(self.LoadCSVView, 1, 4, 1, 1)

        self.lineEdit_14 = QLineEdit(self.tab_27)
        self.lineEdit_14.setObjectName(u"lineEdit_14")
        self.lineEdit_14.setEnabled(False)
        self.lineEdit_14.setFont(font)

        self.gridLayout_29.addWidget(self.lineEdit_14, 4, 4, 1, 1)

        self.gcode_f_name = QLineEdit(self.tab_27)
        self.gcode_f_name.setObjectName(u"gcode_f_name")

        self.gridLayout_29.addWidget(self.gcode_f_name, 6, 1, 1, 2)

        self.CSVDeli_Sel = QComboBox(self.tab_27)
        self.CSVDeli_Sel.setObjectName(u"CSVDeli_Sel")

        self.gridLayout_29.addWidget(self.CSVDeli_Sel, 3, 7, 1, 3)

        self.CSV_Oper_Value = QDoubleSpinBox(self.tab_27)
        self.CSV_Oper_Value.setObjectName(u"CSV_Oper_Value")
        self.CSV_Oper_Value.setMinimum(-9999999999.000000000000000)
        self.CSV_Oper_Value.setMaximum(99990000.000000000000000)

        self.gridLayout_29.addWidget(self.CSV_Oper_Value, 2, 1, 1, 1)

        self.PlotCSVView = QPushButton(self.tab_27)
        self.PlotCSVView.setObjectName(u"PlotCSVView")
        self.PlotCSVView.setFont(font2)

        self.gridLayout_29.addWidget(self.PlotCSVView, 1, 7, 1, 2)

        self.lineEdit_16 = QLineEdit(self.tab_27)
        self.lineEdit_16.setObjectName(u"lineEdit_16")
        self.lineEdit_16.setEnabled(False)
        self.lineEdit_16.setFont(font)

        self.gridLayout_29.addWidget(self.lineEdit_16, 2, 4, 1, 1)

        self.line_24 = QFrame(self.tab_27)
        self.line_24.setObjectName(u"line_24")
        self.line_24.setFrameShape(QFrame.Shape.HLine)
        self.line_24.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_29.addWidget(self.line_24, 3, 1, 1, 2)

        self.cvs_add_plot = QCheckBox(self.tab_27)
        self.cvs_add_plot.setObjectName(u"cvs_add_plot")

        self.gridLayout_29.addWidget(self.cvs_add_plot, 1, 9, 1, 1)

        self.exp_csv_2_gcode = QPushButton(self.tab_27)
        self.exp_csv_2_gcode.setObjectName(u"exp_csv_2_gcode")
        self.exp_csv_2_gcode.setFont(font)

        self.gridLayout_29.addWidget(self.exp_csv_2_gcode, 4, 1, 1, 1)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_29.addItem(self.verticalSpacer_5, 8, 5, 1, 1)

        self.lineEdit_17 = QLineEdit(self.tab_27)
        self.lineEdit_17.setObjectName(u"lineEdit_17")
        self.lineEdit_17.setEnabled(False)
        self.lineEdit_17.setFont(font)

        self.gridLayout_29.addWidget(self.lineEdit_17, 2, 8, 1, 1)

        self.CSV_X_plot = QComboBox(self.tab_27)
        self.CSV_X_plot.setObjectName(u"CSV_X_plot")

        self.gridLayout_29.addWidget(self.CSV_X_plot, 4, 7, 1, 3)

        self.csvTable = QTableWidget(self.tab_27)
        self.csvTable.setObjectName(u"csvTable")

        self.gridLayout_29.addWidget(self.csvTable, 0, 0, 1, 8)

        self.CSV_Oper_Box = QComboBox(self.tab_27)
        self.CSV_Oper_Box.setObjectName(u"CSV_Oper_Box")

        self.gridLayout_29.addWidget(self.CSV_Oper_Box, 1, 1, 1, 2)

        self.CSVLineSkip = QSpinBox(self.tab_27)
        self.CSVLineSkip.setObjectName(u"CSVLineSkip")

        self.gridLayout_29.addWidget(self.CSVLineSkip, 2, 7, 1, 1)

        self.lineEdit_13 = QLineEdit(self.tab_27)
        self.lineEdit_13.setObjectName(u"lineEdit_13")
        self.lineEdit_13.setEnabled(False)
        self.lineEdit_13.setFont(font)

        self.gridLayout_29.addWidget(self.lineEdit_13, 3, 4, 1, 1)

        self.line_23 = QFrame(self.tab_27)
        self.line_23.setObjectName(u"line_23")
        self.line_23.setFrameShape(QFrame.Shape.VLine)
        self.line_23.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_29.addWidget(self.line_23, 1, 3, 6, 1)

        self.CSVLinHeader = QSpinBox(self.tab_27)
        self.CSVLinHeader.setObjectName(u"CSVLinHeader")

        self.gridLayout_29.addWidget(self.CSVLinHeader, 2, 9, 1, 1)

        self.CSV_Oper_Apply = QPushButton(self.tab_27)
        self.CSV_Oper_Apply.setObjectName(u"CSV_Oper_Apply")
        self.CSV_Oper_Apply.setFont(font)

        self.gridLayout_29.addWidget(self.CSV_Oper_Apply, 2, 2, 1, 1)

        self.gcode_col = QSpinBox(self.tab_27)
        self.gcode_col.setObjectName(u"gcode_col")
        self.gcode_col.setMinimum(2)

        self.gridLayout_29.addWidget(self.gcode_col, 4, 2, 1, 1)

        self.CSVViewText = QTextEdit(self.tab_27)
        self.CSVViewText.setObjectName(u"CSVViewText")
        self.CSVViewText.setFont(font1)

        self.gridLayout_29.addWidget(self.CSVViewText, 0, 8, 1, 2)

        self.CVS_Ax_View = QWidget(self.tab_27)
        self.CVS_Ax_View.setObjectName(u"CVS_Ax_View")

        self.gridLayout_29.addWidget(self.CVS_Ax_View, 7, 4, 2, 6)

        self.lineEdit_4 = QLineEdit(self.tab_27)
        self.lineEdit_4.setObjectName(u"lineEdit_4")
        self.lineEdit_4.setEnabled(False)

        self.gridLayout_29.addWidget(self.lineEdit_4, 5, 1, 1, 1)

        self.gcode_cycles = QSpinBox(self.tab_27)
        self.gcode_cycles.setObjectName(u"gcode_cycles")
        self.gcode_cycles.setMinimum(1)

        self.gridLayout_29.addWidget(self.gcode_cycles, 5, 2, 1, 1)

        self.lineEdit_15 = QLineEdit(self.tab_27)
        self.lineEdit_15.setObjectName(u"lineEdit_15")
        self.lineEdit_15.setEnabled(False)
        self.lineEdit_15.setFont(font)

        self.gridLayout_29.addWidget(self.lineEdit_15, 5, 4, 1, 1)

        self.CSV_Y_plot = QComboBox(self.tab_27)
        self.CSV_Y_plot.setObjectName(u"CSV_Y_plot")

        self.gridLayout_29.addWidget(self.CSV_Y_plot, 5, 7, 1, 3)

        self.tabModules.addTab(self.tab_27, "")
        self.tab_BrCv = QWidget()
        self.tab_BrCv.setObjectName(u"tab_BrCv")
        self.gridLayout_BrCv = QGridLayout(self.tab_BrCv)
        self.gridLayout_BrCv.setObjectName(u"gridLayout_BrCv")
        self.tabWidget_BrCv = QTabWidget(self.tab_BrCv)
        self.tabWidget_BrCv.setObjectName(u"tabWidget_BrCv")
        self.tab_import = QWidget()
        self.tab_import.setObjectName(u"tab_import")
        self.gridLayout_BrCv_1 = QGridLayout(self.tab_import)
        self.gridLayout_BrCv_1.setObjectName(u"gridLayout_BrCv_1")
        self.groupBox_BrCv_importCSV = QGroupBox(self.tab_import)
        self.groupBox_BrCv_importCSV.setObjectName(u"groupBox_BrCv_importCSV")
        self.gridLayout_BrCv_3 = QGridLayout(self.groupBox_BrCv_importCSV)
        self.gridLayout_BrCv_3.setObjectName(u"gridLayout_BrCv_3")
        self.lineEdit_BrCv_5 = QLineEdit(self.groupBox_BrCv_importCSV)
        self.lineEdit_BrCv_5.setObjectName(u"lineEdit_BrCv_5")
        self.lineEdit_BrCv_5.setEnabled(False)

        self.gridLayout_BrCv_3.addWidget(self.lineEdit_BrCv_5, 0, 0, 1, 1)

        self.selDelimCSV_BrCv = QComboBox(self.groupBox_BrCv_importCSV)
        self.selDelimCSV_BrCv.setObjectName(u"selDelimCSV_BrCv")

        self.gridLayout_BrCv_3.addWidget(self.selDelimCSV_BrCv, 0, 1, 1, 1)

        self.lineHeadCSV_BrCv = QSpinBox(self.groupBox_BrCv_importCSV)
        self.lineHeadCSV_BrCv.setObjectName(u"lineHeadCSV_BrCv")
        self.lineHeadCSV_BrCv.setValue(4)

        self.gridLayout_BrCv_3.addWidget(self.lineHeadCSV_BrCv, 1, 1, 1, 1)

        self.lineSkipCSV_BrCv = QSpinBox(self.groupBox_BrCv_importCSV)
        self.lineSkipCSV_BrCv.setObjectName(u"lineSkipCSV_BrCv")
        self.lineSkipCSV_BrCv.setValue(10)

        self.gridLayout_BrCv_3.addWidget(self.lineSkipCSV_BrCv, 2, 1, 1, 1)

        self.lineEdit_BrCv_6 = QLineEdit(self.groupBox_BrCv_importCSV)
        self.lineEdit_BrCv_6.setObjectName(u"lineEdit_BrCv_6")
        self.lineEdit_BrCv_6.setEnabled(False)

        self.gridLayout_BrCv_3.addWidget(self.lineEdit_BrCv_6, 2, 0, 1, 1)

        self.verticalSpacer_BrCv_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_BrCv_3.addItem(self.verticalSpacer_BrCv_2, 6, 1, 1, 1)

        self.lineEdit_BrCv_7 = QLineEdit(self.groupBox_BrCv_importCSV)
        self.lineEdit_BrCv_7.setObjectName(u"lineEdit_BrCv_7")
        self.lineEdit_BrCv_7.setEnabled(False)

        self.gridLayout_BrCv_3.addWidget(self.lineEdit_BrCv_7, 1, 0, 1, 1)

        self.flipCSV_BrCv = QCheckBox(self.groupBox_BrCv_importCSV)
        self.flipCSV_BrCv.setObjectName(u"flipCSV_BrCv")
        self.flipCSV_BrCv.setEnabled(True)
        self.flipCSV_BrCv.setChecked(True)

        self.gridLayout_BrCv_3.addWidget(self.flipCSV_BrCv, 4, 1, 1, 1)

        self.loadCSVView_BrCv = QPushButton(self.groupBox_BrCv_importCSV)
        self.loadCSVView_BrCv.setObjectName(u"loadCSVView_BrCv")

        self.gridLayout_BrCv_3.addWidget(self.loadCSVView_BrCv, 5, 1, 1, 1)

        self.lineEdit_BrCv_8 = QLineEdit(self.groupBox_BrCv_importCSV)
        self.lineEdit_BrCv_8.setObjectName(u"lineEdit_BrCv_8")
        self.lineEdit_BrCv_8.setEnabled(False)

        self.gridLayout_BrCv_3.addWidget(self.lineEdit_BrCv_8, 3, 0, 1, 1)

        self.timeUnitCSV_BrCv = QComboBox(self.groupBox_BrCv_importCSV)
        self.timeUnitCSV_BrCv.setObjectName(u"timeUnitCSV_BrCv")

        self.gridLayout_BrCv_3.addWidget(self.timeUnitCSV_BrCv, 3, 1, 1, 1)

        self.gridLayout_BrCv_3.setColumnStretch(0, 2)
        self.gridLayout_BrCv_3.setColumnStretch(1, 1)

        self.gridLayout_BrCv_1.addWidget(self.groupBox_BrCv_importCSV, 2, 0, 1, 1)

        self.groupBox_BrCv_createCurve = QGroupBox(self.tab_import)
        self.groupBox_BrCv_createCurve.setObjectName(u"groupBox_BrCv_createCurve")
        self.gridLayout_BrCv_2 = QGridLayout(self.groupBox_BrCv_createCurve)
        self.gridLayout_BrCv_2.setObjectName(u"gridLayout_BrCv_2")
        self.cvType = QComboBox(self.groupBox_BrCv_createCurve)
        self.cvType.setObjectName(u"cvType")

        self.gridLayout_BrCv_2.addWidget(self.cvType, 0, 1, 1, 1)

        self.lineEdit_BrCv_1 = QLineEdit(self.groupBox_BrCv_createCurve)
        self.lineEdit_BrCv_1.setObjectName(u"lineEdit_BrCv_1")
        self.lineEdit_BrCv_1.setEnabled(False)

        self.gridLayout_BrCv_2.addWidget(self.lineEdit_BrCv_1, 1, 0, 1, 1)

        self.createCvAmpl = QDoubleSpinBox(self.groupBox_BrCv_createCurve)
        self.createCvAmpl.setObjectName(u"createCvAmpl")
        self.createCvAmpl.setValue(15.000000000000000)

        self.gridLayout_BrCv_2.addWidget(self.createCvAmpl, 2, 1, 1, 1)

        self.createCvNumCycl = QSpinBox(self.groupBox_BrCv_createCurve)
        self.createCvNumCycl.setObjectName(u"createCvNumCycl")
        self.createCvNumCycl.setValue(10)

        self.gridLayout_BrCv_2.addWidget(self.createCvNumCycl, 1, 1, 1, 1)

        self.lineEdit_BrCv = QLineEdit(self.groupBox_BrCv_createCurve)
        self.lineEdit_BrCv.setObjectName(u"lineEdit_BrCv")
        self.lineEdit_BrCv.setEnabled(False)

        self.gridLayout_BrCv_2.addWidget(self.lineEdit_BrCv, 3, 0, 1, 1)

        self.createCvCyclTime = QDoubleSpinBox(self.groupBox_BrCv_createCurve)
        self.createCvCyclTime.setObjectName(u"createCvCyclTime")
        self.createCvCyclTime.setValue(6.000000000000000)

        self.gridLayout_BrCv_2.addWidget(self.createCvCyclTime, 3, 1, 1, 1)

        self.lineEdit_BrCv_3 = QLineEdit(self.groupBox_BrCv_createCurve)
        self.lineEdit_BrCv_3.setObjectName(u"lineEdit_BrCv_3")
        self.lineEdit_BrCv_3.setEnabled(False)

        self.gridLayout_BrCv_2.addWidget(self.lineEdit_BrCv_3, 2, 0, 1, 1)

        self.setParamsCreateCv = QPushButton(self.groupBox_BrCv_createCurve)
        self.setParamsCreateCv.setObjectName(u"setParamsCreateCv")

        self.gridLayout_BrCv_2.addWidget(self.setParamsCreateCv, 5, 1, 1, 1)

        self.createCv = QPushButton(self.groupBox_BrCv_createCurve)
        self.createCv.setObjectName(u"createCv")

        self.gridLayout_BrCv_2.addWidget(self.createCv, 7, 2, 1, 1)

        self.tableViewEditParams = QTableWidget(self.groupBox_BrCv_createCurve)
        self.tableViewEditParams.setObjectName(u"tableViewEditParams")

        self.gridLayout_BrCv_2.addWidget(self.tableViewEditParams, 0, 2, 7, 1)

        self.lineEdit_BrCv_4 = QLineEdit(self.groupBox_BrCv_createCurve)
        self.lineEdit_BrCv_4.setObjectName(u"lineEdit_BrCv_4")
        self.lineEdit_BrCv_4.setEnabled(False)

        self.gridLayout_BrCv_2.addWidget(self.lineEdit_BrCv_4, 0, 0, 1, 1)

        self.lineEdit_BrCv_2 = QLineEdit(self.groupBox_BrCv_createCurve)
        self.lineEdit_BrCv_2.setObjectName(u"lineEdit_BrCv_2")
        self.lineEdit_BrCv_2.setEnabled(False)

        self.gridLayout_BrCv_2.addWidget(self.lineEdit_BrCv_2, 4, 0, 1, 1)

        self.createCvFreq = QSpinBox(self.groupBox_BrCv_createCurve)
        self.createCvFreq.setObjectName(u"createCvFreq")
        self.createCvFreq.setValue(25)

        self.gridLayout_BrCv_2.addWidget(self.createCvFreq, 4, 1, 1, 1)

        self.verticalSpacer_BrCv = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_BrCv_2.addItem(self.verticalSpacer_BrCv, 6, 1, 2, 1)

        self.gridLayout_BrCv_2.setColumnStretch(0, 1)
        self.gridLayout_BrCv_2.setColumnStretch(1, 1)
        self.gridLayout_BrCv_2.setColumnStretch(2, 2)

        self.gridLayout_BrCv_1.addWidget(self.groupBox_BrCv_createCurve, 2, 1, 1, 1)

        self.horizontalSpacer_BrCv = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_BrCv_1.addItem(self.horizontalSpacer_BrCv, 2, 2, 1, 1)

        self.horizontalLayout_BrCv_1 = QHBoxLayout()
        self.horizontalLayout_BrCv_1.setObjectName(u"horizontalLayout_BrCv_1")
        self.tableViewCSV_BrCv = QTableWidget(self.tab_import)
        self.tableViewCSV_BrCv.setObjectName(u"tableViewCSV_BrCv")

        self.horizontalLayout_BrCv_1.addWidget(self.tableViewCSV_BrCv)

        self.textViewCSV_BrCv = QTextEdit(self.tab_import)
        self.textViewCSV_BrCv.setObjectName(u"textViewCSV_BrCv")

        self.horizontalLayout_BrCv_1.addWidget(self.textViewCSV_BrCv)

        self.horizontalLayout_BrCv_1.setStretch(0, 2)
        self.horizontalLayout_BrCv_1.setStretch(1, 1)

        self.gridLayout_BrCv_1.addLayout(self.horizontalLayout_BrCv_1, 0, 0, 1, 3)

        self.gridLayout_BrCv_1.setRowStretch(0, 2)
        self.gridLayout_BrCv_1.setRowStretch(2, 1)
        self.gridLayout_BrCv_1.setColumnStretch(0, 1)
        self.gridLayout_BrCv_1.setColumnStretch(1, 2)
        self.gridLayout_BrCv_1.setColumnStretch(2, 1)
        self.tabWidget_BrCv.addTab(self.tab_import, "")
        self.tab_BrCv_edit = QWidget()
        self.tab_BrCv_edit.setObjectName(u"tab_BrCv_edit")
        self.gridLayout_BrCv_edit = QGridLayout(self.tab_BrCv_edit)
        self.gridLayout_BrCv_edit.setObjectName(u"gridLayout_BrCv_edit")
        self.gridLayout_BrCv_6 = QGridLayout()
        self.gridLayout_BrCv_6.setObjectName(u"gridLayout_BrCv_6")
        self.breathhold_BrCv = QGroupBox(self.tab_BrCv_edit)
        self.breathhold_BrCv.setObjectName(u"breathhold_BrCv")
        self.gridLayout_BrCv_8 = QGridLayout(self.breathhold_BrCv)
        self.gridLayout_BrCv_8.setObjectName(u"gridLayout_BrCv_8")
        self.lineEdit_BrCv_30 = QLineEdit(self.breathhold_BrCv)
        self.lineEdit_BrCv_30.setObjectName(u"lineEdit_BrCv_30")
        self.lineEdit_BrCv_30.setEnabled(False)

        self.gridLayout_BrCv_8.addWidget(self.lineEdit_BrCv_30, 2, 0, 1, 1)

        self.breathholdStart = QSpinBox(self.breathhold_BrCv)
        self.breathholdStart.setObjectName(u"breathholdStart")
        self.breathholdStart.setMaximum(999999)

        self.gridLayout_BrCv_8.addWidget(self.breathholdStart, 1, 1, 1, 1)

        self.lineEdit_BrCv_29 = QLineEdit(self.breathhold_BrCv)
        self.lineEdit_BrCv_29.setObjectName(u"lineEdit_BrCv_29")
        self.lineEdit_BrCv_29.setEnabled(False)

        self.gridLayout_BrCv_8.addWidget(self.lineEdit_BrCv_29, 1, 0, 1, 1)

        self.breathholdDuration = QDoubleSpinBox(self.breathhold_BrCv)
        self.breathholdDuration.setObjectName(u"breathholdDuration")

        self.gridLayout_BrCv_8.addWidget(self.breathholdDuration, 2, 1, 1, 1)

        self.applyBreathhold = QCheckBox(self.breathhold_BrCv)
        self.applyBreathhold.setObjectName(u"applyBreathhold")

        self.gridLayout_BrCv_8.addWidget(self.applyBreathhold, 0, 0, 1, 1)

        self.gridLayout_BrCv_8.setColumnStretch(0, 2)
        self.gridLayout_BrCv_8.setColumnStretch(1, 1)

        self.gridLayout_BrCv_6.addWidget(self.breathhold_BrCv, 1, 1, 1, 2)

        self.operations_BrCv = QGroupBox(self.tab_BrCv_edit)
        self.operations_BrCv.setObjectName(u"operations_BrCv")
        self.gridLayout_BrCv_7 = QGridLayout(self.operations_BrCv)
        self.gridLayout_BrCv_7.setObjectName(u"gridLayout_BrCv_7")
        self.lineEdit_BrCv_22 = QLineEdit(self.operations_BrCv)
        self.lineEdit_BrCv_22.setObjectName(u"lineEdit_BrCv_22")
        self.lineEdit_BrCv_22.setEnabled(False)

        self.gridLayout_BrCv_7.addWidget(self.lineEdit_BrCv_22, 2, 0, 1, 1)

        self.shiftAmpl_BrCv = QDoubleSpinBox(self.operations_BrCv)
        self.shiftAmpl_BrCv.setObjectName(u"shiftAmpl_BrCv")
        self.shiftAmpl_BrCv.setMinimum(-99.000000000000000)
        self.shiftAmpl_BrCv.setMaximum(99.000000000000000)

        self.gridLayout_BrCv_7.addWidget(self.shiftAmpl_BrCv, 2, 1, 1, 1)

        self.lineEdit_BrCv_23 = QLineEdit(self.operations_BrCv)
        self.lineEdit_BrCv_23.setObjectName(u"lineEdit_BrCv_23")
        self.lineEdit_BrCv_23.setEnabled(False)

        self.gridLayout_BrCv_7.addWidget(self.lineEdit_BrCv_23, 3, 0, 1, 1)

        self.scaleFreq_BrCv = QDoubleSpinBox(self.operations_BrCv)
        self.scaleFreq_BrCv.setObjectName(u"scaleFreq_BrCv")
        self.scaleFreq_BrCv.setValue(1.000000000000000)

        self.gridLayout_BrCv_7.addWidget(self.scaleFreq_BrCv, 0, 1, 1, 1)

        self.lineEdit_BrCv_20 = QLineEdit(self.operations_BrCv)
        self.lineEdit_BrCv_20.setObjectName(u"lineEdit_BrCv_20")
        self.lineEdit_BrCv_20.setEnabled(False)

        self.gridLayout_BrCv_7.addWidget(self.lineEdit_BrCv_20, 0, 0, 1, 1)

        self.lineEdit_BrCv_21 = QLineEdit(self.operations_BrCv)
        self.lineEdit_BrCv_21.setObjectName(u"lineEdit_BrCv_21")
        self.lineEdit_BrCv_21.setEnabled(False)

        self.gridLayout_BrCv_7.addWidget(self.lineEdit_BrCv_21, 1, 0, 1, 1)

        self.maxAmplThresh_BrCv = QDoubleSpinBox(self.operations_BrCv)
        self.maxAmplThresh_BrCv.setObjectName(u"maxAmplThresh_BrCv")
        self.maxAmplThresh_BrCv.setValue(39.000000000000000)

        self.gridLayout_BrCv_7.addWidget(self.maxAmplThresh_BrCv, 3, 1, 1, 1)

        self.setMinZero_BrCv = QCheckBox(self.operations_BrCv)
        self.setMinZero_BrCv.setObjectName(u"setMinZero_BrCv")
        self.setMinZero_BrCv.setChecked(True)

        self.gridLayout_BrCv_7.addWidget(self.setMinZero_BrCv, 5, 1, 1, 1)

        self.scaleAmpl_BrCv = QDoubleSpinBox(self.operations_BrCv)
        self.scaleAmpl_BrCv.setObjectName(u"scaleAmpl_BrCv")
        self.scaleAmpl_BrCv.setValue(1.000000000000000)

        self.gridLayout_BrCv_7.addWidget(self.scaleAmpl_BrCv, 1, 1, 1, 1)

        self.gridLayout_BrCv_7.setColumnStretch(0, 2)
        self.gridLayout_BrCv_7.setColumnStretch(1, 1)

        self.gridLayout_BrCv_6.addWidget(self.operations_BrCv, 0, 1, 1, 2)

        self.applyOper_BrCv = QPushButton(self.tab_BrCv_edit)
        self.applyOper_BrCv.setObjectName(u"applyOper_BrCv")

        self.gridLayout_BrCv_6.addWidget(self.applyOper_BrCv, 3, 1, 1, 1)

        self.verticalSpacer_BrCv_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_BrCv_6.addItem(self.verticalSpacer_BrCv_4, 9, 1, 1, 2)

        self.export_BrCv = QGroupBox(self.tab_BrCv_edit)
        self.export_BrCv.setObjectName(u"export_BrCv")
        self.gridLayout_BrCv_9 = QGridLayout(self.export_BrCv)
        self.gridLayout_BrCv_9.setObjectName(u"gridLayout_BrCv_9")
        self.exportData_BrCv = QPushButton(self.export_BrCv)
        self.exportData_BrCv.setObjectName(u"exportData_BrCv")

        self.gridLayout_BrCv_9.addWidget(self.exportData_BrCv, 4, 0, 1, 1)

        self.copyCurve_BrCv = QSpinBox(self.export_BrCv)
        self.copyCurve_BrCv.setObjectName(u"copyCurve_BrCv")
        self.copyCurve_BrCv.setValue(1)

        self.gridLayout_BrCv_9.addWidget(self.copyCurve_BrCv, 2, 1, 1, 2)

        self.lineEdit_BrCv_28 = QLineEdit(self.export_BrCv)
        self.lineEdit_BrCv_28.setObjectName(u"lineEdit_BrCv_28")
        self.lineEdit_BrCv_28.setEnabled(False)

        self.gridLayout_BrCv_9.addWidget(self.lineEdit_BrCv_28, 3, 0, 1, 1)

        self.interp_BrCv = QCheckBox(self.export_BrCv)
        self.interp_BrCv.setObjectName(u"interp_BrCv")
        self.interp_BrCv.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.interp_BrCv.setChecked(True)

        self.gridLayout_BrCv_9.addWidget(self.interp_BrCv, 0, 0, 1, 1)

        self.exportGCODE_BrCv = QPushButton(self.export_BrCv)
        self.exportGCODE_BrCv.setObjectName(u"exportGCODE_BrCv")

        self.gridLayout_BrCv_9.addWidget(self.exportGCODE_BrCv, 4, 1, 1, 2)

        self.editExportFile_BrCv = QLineEdit(self.export_BrCv)
        self.editExportFile_BrCv.setObjectName(u"editExportFile_BrCv")

        self.gridLayout_BrCv_9.addWidget(self.editExportFile_BrCv, 3, 1, 1, 2)

        self.lineEdit_77 = QLineEdit(self.export_BrCv)
        self.lineEdit_77.setObjectName(u"lineEdit_77")
        self.lineEdit_77.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_77.sizePolicy().hasHeightForWidth())
        self.lineEdit_77.setSizePolicy(sizePolicy)

        self.gridLayout_BrCv_9.addWidget(self.lineEdit_77, 0, 2, 1, 1)

        self.interp_value_BrCv = QDoubleSpinBox(self.export_BrCv)
        self.interp_value_BrCv.setObjectName(u"interp_value_BrCv")
        self.interp_value_BrCv.setValue(10.000000000000000)

        self.gridLayout_BrCv_9.addWidget(self.interp_value_BrCv, 0, 1, 1, 1)

        self.lineEdit_BrCv_24 = QLineEdit(self.export_BrCv)
        self.lineEdit_BrCv_24.setObjectName(u"lineEdit_BrCv_24")
        self.lineEdit_BrCv_24.setEnabled(False)

        self.gridLayout_BrCv_9.addWidget(self.lineEdit_BrCv_24, 2, 0, 1, 1)

        self.lineEdit_83 = QLineEdit(self.export_BrCv)
        self.lineEdit_83.setObjectName(u"lineEdit_83")
        self.lineEdit_83.setEnabled(False)

        self.gridLayout_BrCv_9.addWidget(self.lineEdit_83, 1, 0, 1, 1)

        self.compress_speed_BrCv = QDoubleSpinBox(self.export_BrCv)
        self.compress_speed_BrCv.setObjectName(u"compress_speed_BrCv")

        self.gridLayout_BrCv_9.addWidget(self.compress_speed_BrCv, 1, 1, 1, 2)

        self.gridLayout_BrCv_9.setColumnStretch(0, 2)
        self.gridLayout_BrCv_9.setColumnStretch(1, 1)
        self.gridLayout_BrCv_9.setColumnStretch(2, 1)

        self.gridLayout_BrCv_6.addWidget(self.export_BrCv, 6, 1, 1, 2)

        self.line_BrCv = QFrame(self.tab_BrCv_edit)
        self.line_BrCv.setObjectName(u"line_BrCv")
        self.line_BrCv.setFrameShape(QFrame.Shape.HLine)
        self.line_BrCv.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_BrCv_6.addWidget(self.line_BrCv, 5, 1, 1, 2)

        self.undoOperations_BrCv = QPushButton(self.tab_BrCv_edit)
        self.undoOperations_BrCv.setObjectName(u"undoOperations_BrCv")

        self.gridLayout_BrCv_6.addWidget(self.undoOperations_BrCv, 3, 2, 1, 1)

        self.smoothing_BrCv = QGroupBox(self.tab_BrCv_edit)
        self.smoothing_BrCv.setObjectName(u"smoothing_BrCv")
        self.gridLayout_77 = QGridLayout(self.smoothing_BrCv)
        self.gridLayout_77.setObjectName(u"gridLayout_77")
        self.smooth_BrCv = QCheckBox(self.smoothing_BrCv)
        self.smooth_BrCv.setObjectName(u"smooth_BrCv")
        self.smooth_BrCv.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.smooth_BrCv.setChecked(True)

        self.gridLayout_77.addWidget(self.smooth_BrCv, 2, 0, 1, 1)

        self.lineEdit_79 = QLineEdit(self.smoothing_BrCv)
        self.lineEdit_79.setObjectName(u"lineEdit_79")
        self.lineEdit_79.setEnabled(False)
        sizePolicy.setHeightForWidth(self.lineEdit_79.sizePolicy().hasHeightForWidth())
        self.lineEdit_79.setSizePolicy(sizePolicy)

        self.gridLayout_77.addWidget(self.lineEdit_79, 4, 3, 1, 1)

        self.lineEdit_78 = QLineEdit(self.smoothing_BrCv)
        self.lineEdit_78.setObjectName(u"lineEdit_78")
        self.lineEdit_78.setEnabled(False)
        sizePolicy.setHeightForWidth(self.lineEdit_78.sizePolicy().hasHeightForWidth())
        self.lineEdit_78.setSizePolicy(sizePolicy)

        self.gridLayout_77.addWidget(self.lineEdit_78, 2, 3, 1, 1)

        self.threshFourierSlider = QSlider(self.smoothing_BrCv)
        self.threshFourierSlider.setObjectName(u"threshFourierSlider")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.threshFourierSlider.sizePolicy().hasHeightForWidth())
        self.threshFourierSlider.setSizePolicy(sizePolicy1)
        self.threshFourierSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_77.addWidget(self.threshFourierSlider, 6, 0, 1, 2)

        self.lineEdit_81 = QLineEdit(self.smoothing_BrCv)
        self.lineEdit_81.setObjectName(u"lineEdit_81")
        self.lineEdit_81.setEnabled(False)
        sizePolicy.setHeightForWidth(self.lineEdit_81.sizePolicy().hasHeightForWidth())
        self.lineEdit_81.setSizePolicy(sizePolicy)

        self.gridLayout_77.addWidget(self.lineEdit_81, 6, 3, 1, 1)

        self.threshFourierValue = QLineEdit(self.smoothing_BrCv)
        self.threshFourierValue.setObjectName(u"threshFourierValue")
        self.threshFourierValue.setEnabled(False)

        self.gridLayout_77.addWidget(self.threshFourierValue, 6, 2, 1, 1)

        self.smooth_size_BrCv = QSpinBox(self.smoothing_BrCv)
        self.smooth_size_BrCv.setObjectName(u"smooth_size_BrCv")
        self.smooth_size_BrCv.setValue(5)

        self.gridLayout_77.addWidget(self.smooth_size_BrCv, 4, 2, 1, 1)

        self.smooth_method_BrCv = QComboBox(self.smoothing_BrCv)
        self.smooth_method_BrCv.setObjectName(u"smooth_method_BrCv")

        self.gridLayout_77.addWidget(self.smooth_method_BrCv, 2, 2, 1, 1)

        self.gridLayout_77.setColumnStretch(0, 1)
        self.gridLayout_77.setColumnStretch(1, 1)
        self.gridLayout_77.setColumnStretch(2, 1)

        self.gridLayout_BrCv_6.addWidget(self.smoothing_BrCv, 2, 1, 1, 2)


        self.gridLayout_BrCv_edit.addLayout(self.gridLayout_BrCv_6, 0, 0, 1, 1)

        self.gridLayout_BrCv_10 = QGridLayout()
        self.gridLayout_BrCv_10.setObjectName(u"gridLayout_BrCv_10")
        self.editXMinSlider_BrCv = QSlider(self.tab_BrCv_edit)
        self.editXMinSlider_BrCv.setObjectName(u"editXMinSlider_BrCv")
        self.editXMinSlider_BrCv.setMaximum(999999)
        self.editXMinSlider_BrCv.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_BrCv_10.addWidget(self.editXMinSlider_BrCv, 2, 1, 1, 1)

        self.lineEdit_BrCv_26 = QLineEdit(self.tab_BrCv_edit)
        self.lineEdit_BrCv_26.setObjectName(u"lineEdit_BrCv_26")
        self.lineEdit_BrCv_26.setEnabled(False)

        self.gridLayout_BrCv_10.addWidget(self.lineEdit_BrCv_26, 3, 0, 1, 1)

        self.editAxView_BrCv = QWidget(self.tab_BrCv_edit)
        self.editAxView_BrCv.setObjectName(u"editAxView_BrCv")

        self.gridLayout_BrCv_10.addWidget(self.editAxView_BrCv, 0, 0, 1, 2)

        self.verticalSpacer_BrCv_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_BrCv_10.addItem(self.verticalSpacer_BrCv_6, 7, 0, 1, 1)

        self.clipCycles_BrCv = QCheckBox(self.tab_BrCv_edit)
        self.clipCycles_BrCv.setObjectName(u"clipCycles_BrCv")
        self.clipCycles_BrCv.setChecked(True)

        self.gridLayout_BrCv_10.addWidget(self.clipCycles_BrCv, 4, 0, 1, 1)

        self.editXMaxSlider_BrCv = QSlider(self.tab_BrCv_edit)
        self.editXMaxSlider_BrCv.setObjectName(u"editXMaxSlider_BrCv")
        self.editXMaxSlider_BrCv.setMaximum(999999)
        self.editXMaxSlider_BrCv.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_BrCv_10.addWidget(self.editXMaxSlider_BrCv, 3, 1, 1, 1)

        self.lineEdit_BrCv_25 = QLineEdit(self.tab_BrCv_edit)
        self.lineEdit_BrCv_25.setObjectName(u"lineEdit_BrCv_25")
        self.lineEdit_BrCv_25.setEnabled(False)

        self.gridLayout_BrCv_10.addWidget(self.lineEdit_BrCv_25, 2, 0, 1, 1)

        self.cropRangeEdit_BrCv = QPushButton(self.tab_BrCv_edit)
        self.cropRangeEdit_BrCv.setObjectName(u"cropRangeEdit_BrCv")

        self.gridLayout_BrCv_10.addWidget(self.cropRangeEdit_BrCv, 5, 0, 1, 1)

        self.editXAxis_BrCv = QComboBox(self.tab_BrCv_edit)
        self.editXAxis_BrCv.setObjectName(u"editXAxis_BrCv")
        sizePolicy.setHeightForWidth(self.editXAxis_BrCv.sizePolicy().hasHeightForWidth())
        self.editXAxis_BrCv.setSizePolicy(sizePolicy)

        self.gridLayout_BrCv_10.addWidget(self.editXAxis_BrCv, 1, 1, 1, 1)

        self.lineEdit_BrCv_27 = QLineEdit(self.tab_BrCv_edit)
        self.lineEdit_BrCv_27.setObjectName(u"lineEdit_BrCv_27")
        self.lineEdit_BrCv_27.setEnabled(False)

        self.gridLayout_BrCv_10.addWidget(self.lineEdit_BrCv_27, 1, 0, 1, 1)

        self.gridLayout_BrCv_10.setRowStretch(0, 3)
        self.gridLayout_BrCv_10.setColumnStretch(0, 1)
        self.gridLayout_BrCv_10.setColumnStretch(1, 4)

        self.gridLayout_BrCv_edit.addLayout(self.gridLayout_BrCv_10, 0, 1, 1, 1)

        self.gridLayout_BrCv_edit.setColumnStretch(0, 2)
        self.gridLayout_BrCv_edit.setColumnStretch(1, 5)
        self.tabWidget_BrCv.addTab(self.tab_BrCv_edit, "")
        self.tab_BrCv_plot = QWidget()
        self.tab_BrCv_plot.setObjectName(u"tab_BrCv_plot")
        self.gridLayout_BrCv_4 = QGridLayout(self.tab_BrCv_plot)
        self.gridLayout_BrCv_4.setObjectName(u"gridLayout_BrCv_4")
        self.verticalLayout_BrCv_1 = QVBoxLayout()
        self.verticalLayout_BrCv_1.setObjectName(u"verticalLayout_BrCv_1")
        self.calcStats_BrCv = QPushButton(self.tab_BrCv_plot)
        self.calcStats_BrCv.setObjectName(u"calcStats_BrCv")

        self.verticalLayout_BrCv_1.addWidget(self.calcStats_BrCv)

        self.lineEdit_BrCv_9 = QLineEdit(self.tab_BrCv_plot)
        self.lineEdit_BrCv_9.setObjectName(u"lineEdit_BrCv_9")
        self.lineEdit_BrCv_9.setEnabled(False)

        self.verticalLayout_BrCv_1.addWidget(self.lineEdit_BrCv_9)

        self.tableViewAmplStats = QTableWidget(self.tab_BrCv_plot)
        self.tableViewAmplStats.setObjectName(u"tableViewAmplStats")

        self.verticalLayout_BrCv_1.addWidget(self.tableViewAmplStats)

        self.lineEdit_BrCv_10 = QLineEdit(self.tab_BrCv_plot)
        self.lineEdit_BrCv_10.setObjectName(u"lineEdit_BrCv_10")
        self.lineEdit_BrCv_10.setEnabled(False)

        self.verticalLayout_BrCv_1.addWidget(self.lineEdit_BrCv_10)

        self.tableViewCyclStats = QTableWidget(self.tab_BrCv_plot)
        self.tableViewCyclStats.setObjectName(u"tableViewCyclStats")

        self.verticalLayout_BrCv_1.addWidget(self.tableViewCyclStats)

        self.lineEdit_BrCv_11 = QLineEdit(self.tab_BrCv_plot)
        self.lineEdit_BrCv_11.setObjectName(u"lineEdit_BrCv_11")
        self.lineEdit_BrCv_11.setEnabled(False)

        self.verticalLayout_BrCv_1.addWidget(self.lineEdit_BrCv_11)

        self.tableViewSpeedStats = QTableWidget(self.tab_BrCv_plot)
        self.tableViewSpeedStats.setObjectName(u"tableViewSpeedStats")

        self.verticalLayout_BrCv_1.addWidget(self.tableViewSpeedStats)


        self.gridLayout_BrCv_4.addLayout(self.verticalLayout_BrCv_1, 0, 0, 1, 1)

        self.gridLayout_BrCv_11 = QGridLayout()
        self.gridLayout_BrCv_11.setObjectName(u"gridLayout_BrCv_11")
        self.gridLayout_BrCv_11.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.plotXAxis_BrCv = QComboBox(self.tab_BrCv_plot)
        self.plotXAxis_BrCv.setObjectName(u"plotXAxis_BrCv")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.plotXAxis_BrCv.sizePolicy().hasHeightForWidth())
        self.plotXAxis_BrCv.setSizePolicy(sizePolicy2)

        self.gridLayout_BrCv_11.addWidget(self.plotXAxis_BrCv, 1, 1, 1, 1)

        self.lineEdit_BrCv_15 = QLineEdit(self.tab_BrCv_plot)
        self.lineEdit_BrCv_15.setObjectName(u"lineEdit_BrCv_15")
        self.lineEdit_BrCv_15.setEnabled(False)

        self.gridLayout_BrCv_11.addWidget(self.lineEdit_BrCv_15, 2, 0, 1, 1)

        self.plotView_BrCv = QPushButton(self.tab_BrCv_plot)
        self.plotView_BrCv.setObjectName(u"plotView_BrCv")

        self.gridLayout_BrCv_11.addWidget(self.plotView_BrCv, 5, 0, 1, 1)

        self.plotAxView_BrCv = QWidget(self.tab_BrCv_plot)
        self.plotAxView_BrCv.setObjectName(u"plotAxView_BrCv")

        self.gridLayout_BrCv_11.addWidget(self.plotAxView_BrCv, 0, 0, 1, 4)

        self.lineEdit_BrCv_14 = QLineEdit(self.tab_BrCv_plot)
        self.lineEdit_BrCv_14.setObjectName(u"lineEdit_BrCv_14")
        self.lineEdit_BrCv_14.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.lineEdit_BrCv_14.sizePolicy().hasHeightForWidth())
        self.lineEdit_BrCv_14.setSizePolicy(sizePolicy2)

        self.gridLayout_BrCv_11.addWidget(self.lineEdit_BrCv_14, 1, 0, 1, 1)

        self.lineEdit_82 = QLineEdit(self.tab_BrCv_plot)
        self.lineEdit_82.setObjectName(u"lineEdit_82")
        self.lineEdit_82.setEnabled(False)

        self.gridLayout_BrCv_11.addWidget(self.lineEdit_82, 3, 0, 1, 1)

        self.plotYAxis_BrCv = QComboBox(self.tab_BrCv_plot)
        self.plotYAxis_BrCv.setObjectName(u"plotYAxis_BrCv")
        sizePolicy2.setHeightForWidth(self.plotYAxis_BrCv.sizePolicy().hasHeightForWidth())
        self.plotYAxis_BrCv.setSizePolicy(sizePolicy2)

        self.gridLayout_BrCv_11.addWidget(self.plotYAxis_BrCv, 2, 1, 1, 1)

        self.verticalSpacer_BrCv_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_BrCv_11.addItem(self.verticalSpacer_BrCv_3, 6, 0, 1, 1)

        self.plotPeaks_BrCv = QCheckBox(self.tab_BrCv_plot)
        self.plotPeaks_BrCv.setObjectName(u"plotPeaks_BrCv")

        self.gridLayout_BrCv_11.addWidget(self.plotPeaks_BrCv, 4, 0, 1, 1)

        self.plotTitle_BrCv = QLineEdit(self.tab_BrCv_plot)
        self.plotTitle_BrCv.setObjectName(u"plotTitle_BrCv")

        self.gridLayout_BrCv_11.addWidget(self.plotTitle_BrCv, 3, 1, 1, 1)

        self.gridLayout_BrCv_11.setRowStretch(0, 4)
        self.gridLayout_BrCv_11.setRowStretch(1, 1)
        self.gridLayout_BrCv_11.setRowStretch(2, 1)
        self.gridLayout_BrCv_11.setRowStretch(3, 1)
        self.gridLayout_BrCv_11.setRowStretch(4, 1)
        self.gridLayout_BrCv_11.setRowStretch(5, 1)
        self.gridLayout_BrCv_11.setRowStretch(6, 1)
        self.gridLayout_BrCv_11.setColumnStretch(0, 1)
        self.gridLayout_BrCv_11.setColumnStretch(1, 1)
        self.gridLayout_BrCv_11.setColumnStretch(2, 1)
        self.gridLayout_BrCv_11.setColumnStretch(3, 1)

        self.gridLayout_BrCv_4.addLayout(self.gridLayout_BrCv_11, 0, 1, 1, 1)

        self.gridLayout_BrCv_4.setColumnStretch(0, 1)
        self.gridLayout_BrCv_4.setColumnStretch(1, 3)
        self.tabWidget_BrCv.addTab(self.tab_BrCv_plot, "")
        self.tab_PhOper = QWidget()
        self.tab_PhOper.setObjectName(u"tab_PhOper")
        self.gridLayout_73 = QGridLayout(self.tab_PhOper)
        self.gridLayout_73.setObjectName(u"gridLayout_73")
        self.BrCv_PhOperWidget = QTabWidget(self.tab_PhOper)
        self.BrCv_PhOperWidget.setObjectName(u"BrCv_PhOperWidget")
        self.tab_DuetControl = QWidget()
        self.tab_DuetControl.setObjectName(u"tab_DuetControl")
        self.gridLayout_DuetWebControl = QGridLayout(self.tab_DuetControl)
        self.gridLayout_DuetWebControl.setObjectName(u"gridLayout_DuetWebControl")
        self.loadDuetPage = QPushButton(self.tab_DuetControl)
        self.loadDuetPage.setObjectName(u"loadDuetPage")

        self.gridLayout_DuetWebControl.addWidget(self.loadDuetPage, 0, 2, 1, 1)

        self.DuetIPAddress = QLineEdit(self.tab_DuetControl)
        self.DuetIPAddress.setObjectName(u"DuetIPAddress")

        self.gridLayout_DuetWebControl.addWidget(self.DuetIPAddress, 0, 1, 1, 1)

        self.DuetControlView = QWebEngineView(self.tab_DuetControl)
        self.DuetControlView.setObjectName(u"DuetControlView")
        self.DuetControlView.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.DuetControlView.setUrl(QUrl(u"http://192.168.0.1/Job/Status"))

        self.gridLayout_DuetWebControl.addWidget(self.DuetControlView, 2, 0, 1, 5)

        self.lineEdit_65 = QLineEdit(self.tab_DuetControl)
        self.lineEdit_65.setObjectName(u"lineEdit_65")
        self.lineEdit_65.setEnabled(False)

        self.gridLayout_DuetWebControl.addWidget(self.lineEdit_65, 0, 0, 1, 1)

        self.definePhOperFolder = QPushButton(self.tab_DuetControl)
        self.definePhOperFolder.setObjectName(u"definePhOperFolder")

        self.gridLayout_DuetWebControl.addWidget(self.definePhOperFolder, 1, 2, 1, 1)

        self.PhOperFolder = QLineEdit(self.tab_DuetControl)
        self.PhOperFolder.setObjectName(u"PhOperFolder")
        self.PhOperFolder.setEnabled(False)

        self.gridLayout_DuetWebControl.addWidget(self.PhOperFolder, 1, 0, 1, 2)

        self.horizontalSpacer_78 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_DuetWebControl.addItem(self.horizontalSpacer_78, 0, 3, 1, 2)

        self.gridLayout_DuetWebControl.setColumnStretch(0, 1)
        self.gridLayout_DuetWebControl.setColumnStretch(1, 1)
        self.gridLayout_DuetWebControl.setColumnStretch(2, 1)
        self.gridLayout_DuetWebControl.setColumnStretch(3, 4)
        self.BrCv_PhOperWidget.addTab(self.tab_DuetControl, "")
        self.tab_MoVe = QWidget()
        self.tab_MoVe.setObjectName(u"tab_MoVe")
        self.gridLayout_MotionVerification = QGridLayout(self.tab_MoVe)
        self.gridLayout_MotionVerification.setObjectName(u"gridLayout_MotionVerification")
        self.lineEdit_MoVeOffset = QLineEdit(self.tab_MoVe)
        self.lineEdit_MoVeOffset.setObjectName(u"lineEdit_MoVeOffset")
        self.lineEdit_MoVeOffset.setEnabled(False)

        self.gridLayout_MotionVerification.addWidget(self.lineEdit_MoVeOffset, 1, 0, 1, 1)

        self.MoVeSystemLatency = QDoubleSpinBox(self.tab_MoVe)
        self.MoVeSystemLatency.setObjectName(u"MoVeSystemLatency")

        self.gridLayout_MotionVerification.addWidget(self.MoVeSystemLatency, 3, 1, 1, 1)

        self.MoVeView = QWidget(self.tab_MoVe)
        self.MoVeView.setObjectName(u"MoVeView")

        self.gridLayout_MotionVerification.addWidget(self.MoVeView, 0, 0, 1, 3)

        self.MoVeAutoControl = QCheckBox(self.tab_MoVe)
        self.MoVeAutoControl.setObjectName(u"MoVeAutoControl")

        self.gridLayout_MotionVerification.addWidget(self.MoVeAutoControl, 2, 2, 1, 1)

        self.lineEdit_MoVeSF = QLineEdit(self.tab_MoVe)
        self.lineEdit_MoVeSF.setObjectName(u"lineEdit_MoVeSF")
        self.lineEdit_MoVeSF.setEnabled(False)

        self.gridLayout_MotionVerification.addWidget(self.lineEdit_MoVeSF, 2, 0, 1, 1)

        self.MoVeOffsetSlider = QSlider(self.tab_MoVe)
        self.MoVeOffsetSlider.setObjectName(u"MoVeOffsetSlider")
        self.MoVeOffsetSlider.setMinimum(-50)
        self.MoVeOffsetSlider.setMaximum(50)
        self.MoVeOffsetSlider.setSingleStep(1)
        self.MoVeOffsetSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_MotionVerification.addWidget(self.MoVeOffsetSlider, 1, 1, 1, 1)

        self.lineEdit_80 = QLineEdit(self.tab_MoVe)
        self.lineEdit_80.setObjectName(u"lineEdit_80")
        self.lineEdit_80.setEnabled(False)

        self.gridLayout_MotionVerification.addWidget(self.lineEdit_80, 3, 0, 1, 1)

        self.horizontalSpacer_77 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_MotionVerification.addItem(self.horizontalSpacer_77, 1, 2, 1, 1)

        self.MoVeSpeedFactor = QSpinBox(self.tab_MoVe)
        self.MoVeSpeedFactor.setObjectName(u"MoVeSpeedFactor")
        self.MoVeSpeedFactor.setMaximum(200)
        self.MoVeSpeedFactor.setValue(100)

        self.gridLayout_MotionVerification.addWidget(self.MoVeSpeedFactor, 2, 1, 1, 1)

        self.MoVeAcqStart = QPushButton(self.tab_MoVe)
        self.MoVeAcqStart.setObjectName(u"MoVeAcqStart")

        self.gridLayout_MotionVerification.addWidget(self.MoVeAcqStart, 4, 1, 1, 1)

        self.exportDataMoVe = QPushButton(self.tab_MoVe)
        self.exportDataMoVe.setObjectName(u"exportDataMoVe")

        self.gridLayout_MotionVerification.addWidget(self.exportDataMoVe, 4, 0, 1, 1)

        self.gridLayout_MotionVerification.setColumnStretch(0, 1)
        self.gridLayout_MotionVerification.setColumnStretch(1, 1)
        self.gridLayout_MotionVerification.setColumnStretch(2, 4)
        self.BrCv_PhOperWidget.addTab(self.tab_MoVe, "")

        self.gridLayout_73.addWidget(self.BrCv_PhOperWidget, 0, 0, 2, 1)

        self.tabWidget_BrCv.addTab(self.tab_PhOper, "")

        self.gridLayout_BrCv.addWidget(self.tabWidget_BrCv, 0, 0, 1, 1)

        self.tabModules.addTab(self.tab_BrCv, "")
        self.tab_seg = QWidget()
        self.tab_seg.setObjectName(u"tab_seg")
        self.gridLayout_62 = QGridLayout(self.tab_seg)
        self.gridLayout_62.setObjectName(u"gridLayout_62")
        self.segSelectView = QComboBox(self.tab_seg)
        self.segSelectView.setObjectName(u"segSelectView")

        self.gridLayout_62.addWidget(self.segSelectView, 6, 2, 1, 1)

        self.groupBox_segStruct = QGroupBox(self.tab_seg)
        self.groupBox_segStruct.setObjectName(u"groupBox_segStruct")
        self.gridLayout_64 = QGridLayout(self.groupBox_segStruct)
        self.gridLayout_64.setObjectName(u"gridLayout_64")
        self.createSegStruct = QPushButton(self.groupBox_segStruct)
        self.createSegStruct.setObjectName(u"createSegStruct")

        self.gridLayout_64.addWidget(self.createSegStruct, 2, 1, 1, 1)

        self.lineEdit_createStructSeg = QLineEdit(self.groupBox_segStruct)
        self.lineEdit_createStructSeg.setObjectName(u"lineEdit_createStructSeg")
        self.lineEdit_createStructSeg.setEnabled(False)

        self.gridLayout_64.addWidget(self.lineEdit_createStructSeg, 1, 0, 1, 1)

        self.segStructName = QLineEdit(self.groupBox_segStruct)
        self.segStructName.setObjectName(u"segStructName")

        self.gridLayout_64.addWidget(self.segStructName, 1, 1, 1, 2)

        self.initStructCheck = QCheckBox(self.groupBox_segStruct)
        self.initStructCheck.setObjectName(u"initStructCheck")
        self.initStructCheck.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.gridLayout_64.addWidget(self.initStructCheck, 2, 0, 1, 1)

        self.deleteSegStruct = QPushButton(self.groupBox_segStruct)
        self.deleteSegStruct.setObjectName(u"deleteSegStruct")

        self.gridLayout_64.addWidget(self.deleteSegStruct, 2, 2, 1, 1)

        self.segStructList = QListWidget(self.groupBox_segStruct)
        self.segStructList.setObjectName(u"segStructList")

        self.gridLayout_64.addWidget(self.segStructList, 0, 0, 1, 3)

        self.gridLayout_64.setRowStretch(0, 1)
        self.gridLayout_64.setColumnStretch(0, 1)
        self.gridLayout_64.setColumnStretch(1, 1)
        self.gridLayout_64.setColumnStretch(2, 1)

        self.gridLayout_62.addWidget(self.groupBox_segStruct, 1, 3, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.threshMinBox = QLineEdit(self.tab_seg)
        self.threshMinBox.setObjectName(u"threshMinBox")
        self.threshMinBox.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.threshMinBox.sizePolicy().hasHeightForWidth())
        self.threshMinBox.setSizePolicy(sizePolicy1)

        self.horizontalLayout_6.addWidget(self.threshMinBox)

        self.threshMinHU = QLineEdit(self.tab_seg)
        self.threshMinHU.setObjectName(u"threshMinHU")

        self.horizontalLayout_6.addWidget(self.threshMinHU)

        self.threshMaxBox = QLineEdit(self.tab_seg)
        self.threshMaxBox.setObjectName(u"threshMaxBox")
        self.threshMaxBox.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.threshMaxBox.sizePolicy().hasHeightForWidth())
        self.threshMaxBox.setSizePolicy(sizePolicy1)

        self.horizontalLayout_6.addWidget(self.threshMaxBox)

        self.threshMaxHU = QLineEdit(self.tab_seg)
        self.threshMaxHU.setObjectName(u"threshMaxHU")

        self.horizontalLayout_6.addWidget(self.threshMaxHU)

        self.horizontalLayout_6.setStretch(0, 2)
        self.horizontalLayout_6.setStretch(2, 2)

        self.gridLayout_62.addLayout(self.horizontalLayout_6, 3, 3, 1, 1)

        self.VTK_SegView = QWidget(self.tab_seg)
        self.VTK_SegView.setObjectName(u"VTK_SegView")

        self.gridLayout_62.addWidget(self.VTK_SegView, 1, 0, 5, 3)

        self.segViewSlider = QSlider(self.tab_seg)
        self.segViewSlider.setObjectName(u"segViewSlider")
        self.segViewSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_62.addWidget(self.segViewSlider, 6, 0, 1, 2)

        self.VTK_SegHistView = QWidget(self.tab_seg)
        self.VTK_SegHistView.setObjectName(u"VTK_SegHistView")

        self.gridLayout_62.addWidget(self.VTK_SegHistView, 2, 3, 1, 1)

        self.toolBox_seg = QToolBox(self.tab_seg)
        self.toolBox_seg.setObjectName(u"toolBox_seg")
        self.seg_manual_contour = QWidget()
        self.seg_manual_contour.setObjectName(u"seg_manual_contour")
        self.seg_manual_contour.setGeometry(QRect(0, 0, 442, 307))
        self.gridLayout_60 = QGridLayout(self.seg_manual_contour)
        self.gridLayout_60.setObjectName(u"gridLayout_60")
        self.undoSegText = QLineEdit(self.seg_manual_contour)
        self.undoSegText.setObjectName(u"undoSegText")
        self.undoSegText.setEnabled(False)

        self.gridLayout_60.addWidget(self.undoSegText, 3, 1, 1, 1)

        self.undoSeg = QToolButton(self.seg_manual_contour)
        self.undoSeg.setObjectName(u"undoSeg")
        icon = QIcon()
        icon.addFile(u"../Users/gabriel.paivafonseca/Downloads/undo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.undoSeg.setIcon(icon)

        self.gridLayout_60.addWidget(self.undoSeg, 3, 0, 1, 1)

        self.segBrushButton = QToolButton(self.seg_manual_contour)
        self.segBrushButton.setObjectName(u"segBrushButton")
        icon1 = QIcon()
        icon1.addFile(u"../Users/gabriel.paivafonseca/Downloads/brush.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.segBrushButton.setIcon(icon1)
        self.segBrushButton.setCheckable(True)

        self.gridLayout_60.addWidget(self.segBrushButton, 0, 0, 1, 1)

        self.segEraseButton = QToolButton(self.seg_manual_contour)
        self.segEraseButton.setObjectName(u"segEraseButton")
        icon2 = QIcon()
        icon2.addFile(u"../Users/gabriel.paivafonseca/Downloads/eraser.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.segEraseButton.setIcon(icon2)
        self.segEraseButton.setCheckable(True)

        self.gridLayout_60.addWidget(self.segEraseButton, 2, 0, 1, 1)

        self.BrushSizeText = QLineEdit(self.seg_manual_contour)
        self.BrushSizeText.setObjectName(u"BrushSizeText")
        self.BrushSizeText.setEnabled(False)

        self.gridLayout_60.addWidget(self.BrushSizeText, 4, 0, 1, 2)

        self.brushClipHU = QCheckBox(self.seg_manual_contour)
        self.brushClipHU.setObjectName(u"brushClipHU")

        self.gridLayout_60.addWidget(self.brushClipHU, 0, 2, 1, 1)

        self.segBrushBox = QLineEdit(self.seg_manual_contour)
        self.segBrushBox.setObjectName(u"segBrushBox")
        self.segBrushBox.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.segBrushBox.sizePolicy().hasHeightForWidth())
        self.segBrushBox.setSizePolicy(sizePolicy2)

        self.gridLayout_60.addWidget(self.segBrushBox, 0, 1, 1, 1)

        self.BrushSizeSlider = QSlider(self.seg_manual_contour)
        self.BrushSizeSlider.setObjectName(u"BrushSizeSlider")
        self.BrushSizeSlider.setMinimum(1)
        self.BrushSizeSlider.setMaximum(25)
        self.BrushSizeSlider.setValue(5)
        self.BrushSizeSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_60.addWidget(self.BrushSizeSlider, 4, 2, 1, 1)

        self.segEraseBox = QLineEdit(self.seg_manual_contour)
        self.segEraseBox.setObjectName(u"segEraseBox")
        self.segEraseBox.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.segEraseBox.sizePolicy().hasHeightForWidth())
        self.segEraseBox.setSizePolicy(sizePolicy2)

        self.gridLayout_60.addWidget(self.segEraseBox, 2, 1, 1, 1)

        self.verticalSpacer_20 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_60.addItem(self.verticalSpacer_20, 5, 1, 1, 1)

        self.gridLayout_60.setColumnStretch(0, 1)
        self.gridLayout_60.setColumnStretch(2, 3)
        self.toolBox_seg.addItem(self.seg_manual_contour, u"Manual contouring && edits")
        self.page_thresholding = QWidget()
        self.page_thresholding.setObjectName(u"page_thresholding")
        self.page_thresholding.setGeometry(QRect(0, 0, 175, 106))
        self.gridLayout_70 = QGridLayout(self.page_thresholding)
        self.gridLayout_70.setObjectName(u"gridLayout_70")
        self.indexMinThreshSeg = QSpinBox(self.page_thresholding)
        self.indexMinThreshSeg.setObjectName(u"indexMinThreshSeg")

        self.gridLayout_70.addWidget(self.indexMinThreshSeg, 0, 2, 1, 1)

        self.indexMaxThreshSeg = QSpinBox(self.page_thresholding)
        self.indexMaxThreshSeg.setObjectName(u"indexMaxThreshSeg")

        self.gridLayout_70.addWidget(self.indexMaxThreshSeg, 1, 2, 1, 1)

        self.lineEdit_75 = QLineEdit(self.page_thresholding)
        self.lineEdit_75.setObjectName(u"lineEdit_75")
        self.lineEdit_75.setEnabled(False)

        self.gridLayout_70.addWidget(self.lineEdit_75, 0, 0, 1, 2)

        self.applyThreshSeg = QPushButton(self.page_thresholding)
        self.applyThreshSeg.setObjectName(u"applyThreshSeg")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.applyThreshSeg.sizePolicy().hasHeightForWidth())
        self.applyThreshSeg.setSizePolicy(sizePolicy3)

        self.gridLayout_70.addWidget(self.applyThreshSeg, 2, 2, 1, 1)

        self.lineEdit_76 = QLineEdit(self.page_thresholding)
        self.lineEdit_76.setObjectName(u"lineEdit_76")
        self.lineEdit_76.setEnabled(False)

        self.gridLayout_70.addWidget(self.lineEdit_76, 1, 0, 1, 2)

        self.verticalSpacer_21 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_70.addItem(self.verticalSpacer_21, 3, 2, 1, 1)

        self.gridLayout_70.setRowStretch(0, 2)
        self.gridLayout_70.setColumnStretch(0, 1)
        self.gridLayout_70.setColumnStretch(2, 1)
        self.toolBox_seg.addItem(self.page_thresholding, u"Thresholding")
        self.morph_oper = QWidget()
        self.morph_oper.setObjectName(u"morph_oper")
        self.morph_oper.setGeometry(QRect(0, 0, 243, 165))
        self.gridLayout_79 = QGridLayout(self.morph_oper)
        self.gridLayout_79.setObjectName(u"gridLayout_79")
        self.lineEdit_70 = QLineEdit(self.morph_oper)
        self.lineEdit_70.setObjectName(u"lineEdit_70")
        self.lineEdit_70.setEnabled(False)
        self.lineEdit_70.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_79.addWidget(self.lineEdit_70, 3, 0, 1, 2)

        self.lineEdit_67 = QLineEdit(self.morph_oper)
        self.lineEdit_67.setObjectName(u"lineEdit_67")
        self.lineEdit_67.setEnabled(False)
        self.lineEdit_67.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.lineEdit_67.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_79.addWidget(self.lineEdit_67, 0, 0, 1, 2)

        self.morph_oper_rank = QSpinBox(self.morph_oper)
        self.morph_oper_rank.setObjectName(u"morph_oper_rank")
        self.morph_oper_rank.setMinimum(1)
        self.morph_oper_rank.setMaximum(3)
        self.morph_oper_rank.setValue(2)

        self.gridLayout_79.addWidget(self.morph_oper_rank, 2, 3, 1, 2)

        self.verticalSpacer_23 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_79.addItem(self.verticalSpacer_23, 6, 4, 1, 1)

        self.morph_oper_method = QComboBox(self.morph_oper)
        self.morph_oper_method.setObjectName(u"morph_oper_method")

        self.gridLayout_79.addWidget(self.morph_oper_method, 0, 3, 1, 2)

        self.lineEdit_69 = QLineEdit(self.morph_oper)
        self.lineEdit_69.setObjectName(u"lineEdit_69")
        self.lineEdit_69.setEnabled(False)
        self.lineEdit_69.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.lineEdit_69.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_79.addWidget(self.lineEdit_69, 2, 0, 1, 2)

        self.lineEdit_68 = QLineEdit(self.morph_oper)
        self.lineEdit_68.setObjectName(u"lineEdit_68")
        self.lineEdit_68.setEnabled(False)
        self.lineEdit_68.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_79.addWidget(self.lineEdit_68, 4, 0, 1, 2)

        self.morph_oper_conn = QSpinBox(self.morph_oper)
        self.morph_oper_conn.setObjectName(u"morph_oper_conn")
        self.morph_oper_conn.setMinimum(1)
        self.morph_oper_conn.setMaximum(3)
        self.morph_oper_conn.setValue(1)

        self.gridLayout_79.addWidget(self.morph_oper_conn, 3, 3, 1, 2)

        self.morph_oper_iter = QSpinBox(self.morph_oper)
        self.morph_oper_iter.setObjectName(u"morph_oper_iter")
        self.morph_oper_iter.setMinimum(1)
        self.morph_oper_iter.setValue(1)

        self.gridLayout_79.addWidget(self.morph_oper_iter, 4, 3, 1, 2)

        self.UndoMorphOper = QPushButton(self.morph_oper)
        self.UndoMorphOper.setObjectName(u"UndoMorphOper")

        self.gridLayout_79.addWidget(self.UndoMorphOper, 5, 4, 1, 1)

        self.ApplyMorphOper = QPushButton(self.morph_oper)
        self.ApplyMorphOper.setObjectName(u"ApplyMorphOper")

        self.gridLayout_79.addWidget(self.ApplyMorphOper, 5, 3, 1, 1)

        self.toolBox_seg.addItem(self.morph_oper, u"Morphological operations")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.page.setGeometry(QRect(0, 0, 228, 134))
        self.gridLayout_61 = QGridLayout(self.page)
        self.gridLayout_61.setObjectName(u"gridLayout_61")
        self.calcSegStatsButton = QPushButton(self.page)
        self.calcSegStatsButton.setObjectName(u"calcSegStatsButton")

        self.gridLayout_61.addWidget(self.calcSegStatsButton, 0, 0, 1, 1)

        self.exportSegStatsButton = QPushButton(self.page)
        self.exportSegStatsButton.setObjectName(u"exportSegStatsButton")

        self.gridLayout_61.addWidget(self.exportSegStatsButton, 0, 1, 1, 1)

        self.tableSegStrucStats = QTableWidget(self.page)
        self.tableSegStrucStats.setObjectName(u"tableSegStrucStats")

        self.gridLayout_61.addWidget(self.tableSegStrucStats, 1, 0, 1, 2)

        self.exportSegStrucButton = QPushButton(self.page)
        self.exportSegStrucButton.setObjectName(u"exportSegStrucButton")

        self.gridLayout_61.addWidget(self.exportSegStrucButton, 2, 0, 1, 1)

        self.toolBox_seg.addItem(self.page, u"Export && analyze")

        self.gridLayout_62.addWidget(self.toolBox_seg, 4, 3, 1, 1)

        self.gridLayout_62.setRowStretch(1, 3)
        self.gridLayout_62.setRowStretch(2, 2)
        self.gridLayout_62.setRowStretch(4, 4)
        self.gridLayout_62.setColumnStretch(0, 3)
        self.gridLayout_62.setColumnStretch(2, 1)
        self.gridLayout_62.setColumnStretch(3, 2)
        self.tabModules.addTab(self.tab_seg, "")

        self.gridLayout_3.addWidget(self.tabModules, 0, 1, 6, 2)

        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_14 = QGridLayout(self.groupBox)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_14.addItem(self.horizontalSpacer_14, 12, 6, 1, 1)

        self.lineEdit_22 = QLineEdit(self.groupBox)
        self.lineEdit_22.setObjectName(u"lineEdit_22")

        self.gridLayout_14.addWidget(self.lineEdit_22, 11, 1, 1, 1)

        self.lineEdit_23 = QLineEdit(self.groupBox)
        self.lineEdit_23.setObjectName(u"lineEdit_23")
        self.lineEdit_23.setFont(font)
        self.lineEdit_23.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_14.addWidget(self.lineEdit_23, 3, 1, 1, 6)

        self.Layer_1_alpha_spin = QDoubleSpinBox(self.groupBox)
        self.Layer_1_alpha_spin.setObjectName(u"Layer_1_alpha_spin")
        self.Layer_1_alpha_spin.setMaximum(1.000000000000000)
        self.Layer_1_alpha_spin.setSingleStep(0.050000000000000)

        self.gridLayout_14.addWidget(self.Layer_1_alpha_spin, 6, 6, 1, 1)

        self.Layer_2_alpha_sli = QSlider(self.groupBox)
        self.Layer_2_alpha_sli.setObjectName(u"Layer_2_alpha_sli")
        self.Layer_2_alpha_sli.setMaximum(100)
        self.Layer_2_alpha_sli.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_14.addWidget(self.Layer_2_alpha_sli, 7, 2, 1, 4)

        self.lineEdit_18 = QLineEdit(self.groupBox)
        self.lineEdit_18.setObjectName(u"lineEdit_18")

        self.gridLayout_14.addWidget(self.lineEdit_18, 4, 1, 1, 1)

        self.doubleSpinBox_7 = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_7.setObjectName(u"doubleSpinBox_7")

        self.gridLayout_14.addWidget(self.doubleSpinBox_7, 11, 6, 1, 1)

        self.line_10 = QFrame(self.groupBox)
        self.line_10.setObjectName(u"line_10")
        self.line_10.setFrameShape(QFrame.Shape.HLine)
        self.line_10.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_14.addWidget(self.line_10, 9, 1, 1, 6)

        self.Layer_1_alpha_sli = QSlider(self.groupBox)
        self.Layer_1_alpha_sli.setObjectName(u"Layer_1_alpha_sli")
        self.Layer_1_alpha_sli.setMaximum(100)
        self.Layer_1_alpha_sli.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_14.addWidget(self.Layer_1_alpha_sli, 6, 2, 1, 4)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_14.addItem(self.horizontalSpacer_13, 12, 5, 1, 1)

        self.Layer_3_alpha_spin = QDoubleSpinBox(self.groupBox)
        self.Layer_3_alpha_spin.setObjectName(u"Layer_3_alpha_spin")
        self.Layer_3_alpha_spin.setMaximum(1.000000000000000)
        self.Layer_3_alpha_spin.setSingleStep(5.000000000000000)

        self.gridLayout_14.addWidget(self.Layer_3_alpha_spin, 8, 6, 1, 1)

        self.horizontalSlider_5 = QSlider(self.groupBox)
        self.horizontalSlider_5.setObjectName(u"horizontalSlider_5")
        self.horizontalSlider_5.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_14.addWidget(self.horizontalSlider_5, 11, 2, 1, 4)

        self.lineEdit_19 = QLineEdit(self.groupBox)
        self.lineEdit_19.setObjectName(u"lineEdit_19")

        self.gridLayout_14.addWidget(self.lineEdit_19, 6, 1, 1, 1)

        self.Layer_sel = QComboBox(self.groupBox)
        self.Layer_sel.setObjectName(u"Layer_sel")

        self.gridLayout_14.addWidget(self.Layer_sel, 1, 2, 1, 1)

        self.Layer_3_alpha_sli = QSlider(self.groupBox)
        self.Layer_3_alpha_sli.setObjectName(u"Layer_3_alpha_sli")
        self.Layer_3_alpha_sli.setMaximum(100)
        self.Layer_3_alpha_sli.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_14.addWidget(self.Layer_3_alpha_sli, 8, 2, 1, 4)

        self.lineEdit_24 = QLineEdit(self.groupBox)
        self.lineEdit_24.setObjectName(u"lineEdit_24")

        self.gridLayout_14.addWidget(self.lineEdit_24, 1, 1, 1, 1)

        self.Layer_0_alpha_sli = QSlider(self.groupBox)
        self.Layer_0_alpha_sli.setObjectName(u"Layer_0_alpha_sli")
        self.Layer_0_alpha_sli.setMaximum(100)
        self.Layer_0_alpha_sli.setSingleStep(1)
        self.Layer_0_alpha_sli.setValue(100)
        self.Layer_0_alpha_sli.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_14.addWidget(self.Layer_0_alpha_sli, 4, 2, 1, 4)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_14.addItem(self.horizontalSpacer_10, 12, 1, 1, 1)

        self.line_11 = QFrame(self.groupBox)
        self.line_11.setObjectName(u"line_11")
        self.line_11.setFrameShape(QFrame.Shape.HLine)
        self.line_11.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_14.addWidget(self.line_11, 2, 1, 1, 6)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_14.addItem(self.horizontalSpacer_11, 12, 3, 1, 1)

        self.lineEdit_21 = QLineEdit(self.groupBox)
        self.lineEdit_21.setObjectName(u"lineEdit_21")

        self.gridLayout_14.addWidget(self.lineEdit_21, 8, 1, 1, 1)

        self.Layer_0_alpha_spin = QDoubleSpinBox(self.groupBox)
        self.Layer_0_alpha_spin.setObjectName(u"Layer_0_alpha_spin")
        self.Layer_0_alpha_spin.setMaximum(1.000000000000000)
        self.Layer_0_alpha_spin.setSingleStep(0.050000000000000)
        self.Layer_0_alpha_spin.setValue(1.000000000000000)

        self.gridLayout_14.addWidget(self.Layer_0_alpha_spin, 4, 6, 1, 1)

        self.lineEdit_20 = QLineEdit(self.groupBox)
        self.lineEdit_20.setObjectName(u"lineEdit_20")

        self.gridLayout_14.addWidget(self.lineEdit_20, 7, 1, 1, 1)

        self.Layer_2_alpha_spin = QDoubleSpinBox(self.groupBox)
        self.Layer_2_alpha_spin.setObjectName(u"Layer_2_alpha_spin")
        self.Layer_2_alpha_spin.setMaximum(1.000000000000000)
        self.Layer_2_alpha_spin.setSingleStep(0.050000000000000)

        self.gridLayout_14.addWidget(self.Layer_2_alpha_spin, 7, 6, 1, 1)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_14.addItem(self.horizontalSpacer_12, 12, 4, 1, 1)

        self.horizontalSpacer_15 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_14.addItem(self.horizontalSpacer_15, 12, 2, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox, 3, 0, 1, 1)

        self.groupBox1 = QGroupBox(self.centralwidget)
        self.groupBox1.setObjectName(u"groupBox1")
        self.gridLayout_141 = QGridLayout(self.groupBox1)
        self.gridLayout_141.setObjectName(u"gridLayout_141")
        self.line_111 = QFrame(self.groupBox1)
        self.line_111.setObjectName(u"line_111")
        self.line_111.setFrameShape(QFrame.Shape.HLine)
        self.line_111.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_141.addWidget(self.line_111, 2, 1, 1, 2)

        self.line_101 = QFrame(self.groupBox1)
        self.line_101.setObjectName(u"line_101")
        self.line_101.setFrameShape(QFrame.Shape.HLine)
        self.line_101.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_141.addWidget(self.line_101, 4, 1, 1, 2)

        self.DataTreeView = QTreeView(self.groupBox1)
        self.DataTreeView.setObjectName(u"DataTreeView")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.DataTreeView.sizePolicy().hasHeightForWidth())
        self.DataTreeView.setSizePolicy(sizePolicy4)
        self.DataTreeView.setAcceptDrops(True)
        self.DataTreeView.setFrameShape(QFrame.Shape.Panel)

        self.gridLayout_141.addWidget(self.DataTreeView, 1, 1, 1, 1)


        self.gridLayout_3.addWidget(self.groupBox1, 1, 0, 2, 1)

        self.gridLayout_3.setRowStretch(1, 8)
        self.gridLayout_3.setRowStretch(2, 1)
        self.gridLayout_3.setColumnStretch(0, 2)
        self.gridLayout_3.setColumnStretch(1, 8)
        AMIGOpy.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(AMIGOpy)
        self.statusbar.setObjectName(u"statusbar")
        AMIGOpy.setStatusBar(self.statusbar)
        QWidget.setTabOrder(self.Proces_spinbox_01, self.Proces_spinbox_02)
        QWidget.setTabOrder(self.Proces_spinbox_02, self.Proces_spinbox_03)
        QWidget.setTabOrder(self.Proces_spinbox_03, self.Proces_spinbox_04)
        QWidget.setTabOrder(self.Proces_spinbox_04, self.Proces_spinbox_05)
        QWidget.setTabOrder(self.Proces_spinbox_05, self.Proces_spinbox_06)
        QWidget.setTabOrder(self.Proces_spinbox_06, self.Process_set_box)
        QWidget.setTabOrder(self.Process_set_box, self.IrIS_Load_CorrectionFrame)
        QWidget.setTabOrder(self.IrIS_Load_CorrectionFrame, self.lineEdit_6)
        QWidget.setTabOrder(self.lineEdit_6, self.Skip_IrIS_Files)
        QWidget.setTabOrder(self.Skip_IrIS_Files, self.Load_IrIS_Files)
        QWidget.setTabOrder(self.Load_IrIS_Files, self.lineEdit_7)
        QWidget.setTabOrder(self.lineEdit_7, self.MetaViewTable)
        QWidget.setTabOrder(self.MetaViewTable, self.SagittalSlider)
        QWidget.setTabOrder(self.SagittalSlider, self.IrIS_Sens_checkbox)
        QWidget.setTabOrder(self.IrIS_Sens_checkbox, self.IrIS_Load_SensMap)
        QWidget.setTabOrder(self.IrIS_Load_SensMap, self.IrIS_CorFrame_checkbox)
        QWidget.setTabOrder(self.IrIS_CorFrame_checkbox, self.add_coll_table_mat)
        QWidget.setTabOrder(self.add_coll_table_mat, self.remove_row_table_mat)
        QWidget.setTabOrder(self.remove_row_table_mat, self.checkBox_calSPR)
        QWidget.setTabOrder(self.checkBox_calSPR, self.MatInfoTable)
        QWidget.setTabOrder(self.MatInfoTable, self.checkBox_calZeff)
        QWidget.setTabOrder(self.checkBox_calZeff, self.mat_table_label)
        QWidget.setTabOrder(self.mat_table_label, self.add_row_table_mat)
        QWidget.setTabOrder(self.add_row_table_mat, self.lineEdit)
        QWidget.setTabOrder(self.lineEdit, self.checkBox_cal_I)
        QWidget.setTabOrder(self.checkBox_cal_I, self.export_table_mat)
        QWidget.setTabOrder(self.export_table_mat, self.Load_csv_mat)
        QWidget.setTabOrder(self.Load_csv_mat, self.remove_coll_table_mat)
        QWidget.setTabOrder(self.remove_coll_table_mat, self.Zeff_m)
        QWidget.setTabOrder(self.Zeff_m, self.Ivalue_plot)
        QWidget.setTabOrder(self.Ivalue_plot, self.I_value_b_coeff)
        QWidget.setTabOrder(self.I_value_b_coeff, self.I_value_z_lw_values)
        QWidget.setTabOrder(self.I_value_z_lw_values, self.I_value_z_up_lim)
        QWidget.setTabOrder(self.I_value_z_up_lim, self.lineEdit_3)
        QWidget.setTabOrder(self.lineEdit_3, self.I_value_z_up_values)
        QWidget.setTabOrder(self.I_value_z_up_values, self.Ivalue_pre_calc_fit)
        QWidget.setTabOrder(self.Ivalue_pre_calc_fit, self.Ivalue_calc_fit)
        QWidget.setTabOrder(self.Ivalue_calc_fit, self.I_value_a_coeff)
        QWidget.setTabOrder(self.I_value_a_coeff, self.I_value_z_lw_lim)
        QWidget.setTabOrder(self.I_value_z_lw_lim, self.lineEdit_2)
        QWidget.setTabOrder(self.lineEdit_2, self.I_Fit_limits)
        QWidget.setTabOrder(self.I_Fit_limits, self.I_value_a_coeff_calc)
        QWidget.setTabOrder(self.I_value_a_coeff_calc, self.N_lin_fit)
        QWidget.setTabOrder(self.N_lin_fit, self.I_value_b_coeff_calc)
        QWidget.setTabOrder(self.I_value_b_coeff_calc, self.tabWidget_5)
        QWidget.setTabOrder(self.tabWidget_5, self.reset_table_mat)
        QWidget.setTabOrder(self.reset_table_mat, self.tabModules)
        QWidget.setTabOrder(self.tabModules, self.Proces_label_01)
        QWidget.setTabOrder(self.Proces_label_01, self.Proces_label_02)
        QWidget.setTabOrder(self.Proces_label_02, self.Proces_label_03)
        QWidget.setTabOrder(self.Proces_label_03, self.cal_mat_ref_info)
        QWidget.setTabOrder(self.cal_mat_ref_info, self.AxialSlider)
        QWidget.setTabOrder(self.AxialSlider, self.Proces_label_04)
        QWidget.setTabOrder(self.Proces_label_04, self.Proces_label_05)
        QWidget.setTabOrder(self.Proces_label_05, self.Proces_label_06)
        QWidget.setTabOrder(self.Proces_label_06, self.CoronalSlider)
        QWidget.setTabOrder(self.CoronalSlider, self.IrIS_Offset_checkbox)
        QWidget.setTabOrder(self.IrIS_Offset_checkbox, self.IrIS_Load_Offset)

        self.retranslateUi(AMIGOpy)

        self.tabModules.setCurrentIndex(0)
        self.tabView01.setCurrentIndex(0)
        self.tabWidget_6.setCurrentIndex(0)
        self.tabWidget_4.setCurrentIndex(0)
        self.tabWidget_10.setCurrentIndex(1)
        self.tabWidget_8.setCurrentIndex(0)
        self.tabWidget_9.setCurrentIndex(0)
        self.tabWidget_3Dview.setCurrentIndex(0)
        self.DECTmenu.setCurrentIndex(0)
        self.Plan_tabs.setCurrentIndex(0)
        self.BrachytabWidget_2.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)
        self.tab_errors.setCurrentIndex(0)
        self.tabWidget_5.setCurrentIndex(3)
        self.tabWidget_7.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_BrCv.setCurrentIndex(0)
        self.BrCv_PhOperWidget.setCurrentIndex(0)
        self.toolBox_seg.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(AMIGOpy)
    # setupUi

    def retranslateUi(self, AMIGOpy):
        AMIGOpy.setWindowTitle(QCoreApplication.translate("AMIGOpy", u"MainWindow", None))
        self.label.setText("")
        self.label_2.setText("")
        self.tabWidget_6.setTabText(self.tabWidget_6.indexOf(self.tab_18), QCoreApplication.translate("AMIGOpy", u"Histograms", None))
        self.tabWidget_6.setTabText(self.tabWidget_6.indexOf(self.tab_19), QCoreApplication.translate("AMIGOpy", u"Settings", None))
        self.tabView01.setTabText(self.tabView01.indexOf(self.tab_5), QCoreApplication.translate("AMIGOpy", u"View", None))
        self.tabView01.setTabText(self.tabView01.indexOf(self.tab_6), QCoreApplication.translate("AMIGOpy", u"DOSE", None))
        self.display_brachy_channel_overlay.setText(QCoreApplication.translate("AMIGOpy", u"Show channel", None))
        self.overlay_all_channels.setText(QCoreApplication.translate("AMIGOpy", u"All channels", None))
        self.display_dw_overlay.setText(QCoreApplication.translate("AMIGOpy", u"Show dwell", None))
        self.lineEdit_63.setText(QCoreApplication.translate("AMIGOpy", u"Point size", None))
        self.brachy_export_dw_channels_csv.setText(QCoreApplication.translate("AMIGOpy", u"Export", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_37), QCoreApplication.translate("AMIGOpy", u"Brachy", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_38), QCoreApplication.translate("AMIGOpy", u"Tab 2", None))
        self.tabView01.setTabText(self.tabView01.indexOf(self.tab_14), QCoreApplication.translate("AMIGOpy", u"PLAN", None))
        self.CreateMask_Structures.setText(QCoreApplication.translate("AMIGOpy", u"Create Mask", None))
        self.lineEdit_66.setText(QCoreApplication.translate("AMIGOpy", u"Ref. Series", None))
        self.tabView01.setTabText(self.tabView01.indexOf(self.tab_39), QCoreApplication.translate("AMIGOpy", u"STRUCT", None))
        self.IrIS_CorFrame_checkbox.setText(QCoreApplication.translate("AMIGOpy", u"Correction Frame", None))
        self.lineEdit_39.setText(QCoreApplication.translate("AMIGOpy", u"Dowmsample while laoding Size  / (N)", None))
        self.IrIS_Offset_checkbox.setText(QCoreApplication.translate("AMIGOpy", u"Offset", None))
        self.IrIS_parallel_proc_box.setText(QCoreApplication.translate("AMIGOpy", u"Parallel processing", None))
        self.lineEdit_6.setText(QCoreApplication.translate("AMIGOpy", u"Skip (N) frames before loading ", None))
        self.IrIS_Sens_checkbox.setText(QCoreApplication.translate("AMIGOpy", u"Sensitivity map", None))
        self.lineEdit_7.setText(QCoreApplication.translate("AMIGOpy", u"Load (N) frames per folder", None))
        self.checkBox_4.setText(QCoreApplication.translate("AMIGOpy", u"Histogram - Central slice only", None))
        self.IrIS_Load_CorrectionFrame.setText(QCoreApplication.translate("AMIGOpy", u"Load", None))
        self.IrIS_Load_SensMap.setText(QCoreApplication.translate("AMIGOpy", u"Load", None))
        self.IrIS_Load_Offset.setText(QCoreApplication.translate("AMIGOpy", u"Load", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_10), QCoreApplication.translate("AMIGOpy", u"Load", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_11), QCoreApplication.translate("AMIGOpy", u"Operations", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_12), QCoreApplication.translate("AMIGOpy", u"Calibration", None))
        self.tabView01.setTabText(self.tabView01.indexOf(self.tab_9), QCoreApplication.translate("AMIGOpy", u"IrIS", None))
        self.lineEdit_64.setText(QCoreApplication.translate("AMIGOpy", u"Search", None))
        self.tabView01.setTabText(self.tabView01.indexOf(self.tab_13), QCoreApplication.translate("AMIGOpy", u"MetaData", None))
        self.run_im_process.setText(QCoreApplication.translate("AMIGOpy", u"Run", None))
        self.ImageUndo_operation.setText(QCoreApplication.translate("AMIGOpy", u"UNDO", None))
        self.pushButton_2.setText(QCoreApplication.translate("AMIGOpy", u"Help", None))
        self.ProcessSetBox.setTitle(QCoreApplication.translate("AMIGOpy", u"Settings", None))
        self.tabWidget_10.setTabText(self.tabWidget_10.indexOf(self.tab_44), QCoreApplication.translate("AMIGOpy", u"Process", None))
        self.groupBox_13.setTitle(QCoreApplication.translate("AMIGOpy", u"Rotation", None))
        self.lineEdit_73.setText(QCoreApplication.translate("AMIGOpy", u"Moving ", None))
        self.groupBox_15.setTitle(QCoreApplication.translate("AMIGOpy", u"Resolution", None))
        self.lineEdit_88.setText(QCoreApplication.translate("AMIGOpy", u"Current", None))
        self.lineEdit_89.setText(QCoreApplication.translate("AMIGOpy", u"Target", None))
        self.pushButton_6.setText(QCoreApplication.translate("AMIGOpy", u"Apply", None))
        self.groupBox_14.setTitle(QCoreApplication.translate("AMIGOpy", u"Flip", None))
        self.pushButton_4.setText(QCoreApplication.translate("AMIGOpy", u"Y", None))
        self.pushButton_3.setText(QCoreApplication.translate("AMIGOpy", u"X", None))
        self.pushButton_5.setText(QCoreApplication.translate("AMIGOpy", u"Z", None))
        self.groupBox_12.setTitle(QCoreApplication.translate("AMIGOpy", u"Translation", None))
        self.lineEdit_72.setText(QCoreApplication.translate("AMIGOpy", u"Layer 0", None))
        self.lineEdit_71.setText(QCoreApplication.translate("AMIGOpy", u"Layer", None))
        self.lineEdit_74.setText(QCoreApplication.translate("AMIGOpy", u"STEP", None))
        self.lineEdit_86.setText(QCoreApplication.translate("AMIGOpy", u"Fill value", None))
        self.apply_Im_transformation.setText(QCoreApplication.translate("AMIGOpy", u"Apply", None))
        self.groupBox_17.setTitle(QCoreApplication.translate("AMIGOpy", u"Crop", None))
        self.lineEdit_85.setText(QCoreApplication.translate("AMIGOpy", u"Y", None))
        self.lineEdit_87.setText(QCoreApplication.translate("AMIGOpy", u"Z", None))
        self.lineEdit_84.setText(QCoreApplication.translate("AMIGOpy", u"X", None))
        self.tabWidget_10.setTabText(self.tabWidget_10.indexOf(self.tab_45), QCoreApplication.translate("AMIGOpy", u"Transform", None))
        self.tabView01.setTabText(self.tabView01.indexOf(self.tab_17), QCoreApplication.translate("AMIGOpy", u"Processing", None))
        self.lineEdit_5.setText(QCoreApplication.translate("AMIGOpy", u"Speed", None))
        self.Play4D_Buttom.setText(QCoreApplication.translate("AMIGOpy", u"Play 4DCT", None))
        self.tabWidget_8.setTabText(self.tabWidget_8.indexOf(self.tab_32), QCoreApplication.translate("AMIGOpy", u"Display", None))
        self.calcAvg4DCT.setText(QCoreApplication.translate("AMIGOpy", u"Calculate average", None))
        self.tabWidget_8.setTabText(self.tabWidget_8.indexOf(self.tab_33), QCoreApplication.translate("AMIGOpy", u"Tab 2", None))
        self.tabView01.setTabText(self.tabView01.indexOf(self.tab_31), QCoreApplication.translate("AMIGOpy", u"4DCT", None))
        self.roi_circle_add_row.setText(QCoreApplication.translate("AMIGOpy", u"+", None))
        self.circ_roi_exp_csv.setText(QCoreApplication.translate("AMIGOpy", u"Export CSV", None))
        self.get_circ_roi_data.setText(QCoreApplication.translate("AMIGOpy", u"GET DATA", None))
        self.roi_circle_remove_row.setText(QCoreApplication.translate("AMIGOpy", u"-", None))
        self.circ_roi_load_csv.setText(QCoreApplication.translate("AMIGOpy", u"Load CSV", None))
        self.checkBox_circ_roi_data_2.setText(QCoreApplication.translate("AMIGOpy", u"Display", None))
        self.checkBox_circ_roi_data_01.setText(QCoreApplication.translate("AMIGOpy", u"All image series", None))
        self.holdOnROI.setText(QCoreApplication.translate("AMIGOpy", u"Hold on", None))
        self.groupBox_8.setTitle(QCoreApplication.translate("AMIGOpy", u"Direction", None))
        self.tabWidget_9.setTabText(self.tabWidget_9.indexOf(self.tab_34), QCoreApplication.translate("AMIGOpy", u"Circles", None))
        self.get_circ_roi_data2.setText(QCoreApplication.translate("AMIGOpy", u"GET", None))
        self.exp_csv_roi_c_values.setText(QCoreApplication.translate("AMIGOpy", u"ExportCSV", None))
        self.tabWidget_9.setTabText(self.tabWidget_9.indexOf(self.tab_35), QCoreApplication.translate("AMIGOpy", u"Data", None))
        self.tabView01.setTabText(self.tabView01.indexOf(self.tab_30), QCoreApplication.translate("AMIGOpy", u"ROI", None))
        self.tabModules.setTabText(self.tabModules.indexOf(self.im_display_tab), QCoreApplication.translate("AMIGOpy", u"View", None))
        self.View3DgroupBox_12.setTitle(QCoreApplication.translate("AMIGOpy", u"Render", None))
        self.View3D_name_02.setText(QCoreApplication.translate("AMIGOpy", u"Brightness", None))
        self.View3D_name_04.setText(QCoreApplication.translate("AMIGOpy", u"Render mode", None))
        self.View3D_clear_all.setText(QCoreApplication.translate("AMIGOpy", u"Clear all", None))
        self.View3D_reset_camera.setText(QCoreApplication.translate("AMIGOpy", u"Reset Camera", None))
        self.View3D_name_05.setText(QCoreApplication.translate("AMIGOpy", u"Lighting", None))
        self.View3D_name_01.setText(QCoreApplication.translate("AMIGOpy", u"Quality (vs speed) ", None))
        self.View3D_name_03.setText(QCoreApplication.translate("AMIGOpy", u"Specular power", None))
        self.View3D_shading_checkBox.setText(QCoreApplication.translate("AMIGOpy", u"Shading", None))
        self.View3D_shoiw_axes_checkBox.setText(QCoreApplication.translate("AMIGOpy", u"Show axes", None))
        self.View3D_annotation_checkBox.setText(QCoreApplication.translate("AMIGOpy", u"Annotation", None))
        self.tabWidget_3Dview.setTabText(self.tabWidget_3Dview.indexOf(self.tab_40), QCoreApplication.translate("AMIGOpy", u"Structures", None))
        self.tabWidget_3Dview.setTabText(self.tabWidget_3Dview.indexOf(self.tab_42), QCoreApplication.translate("AMIGOpy", u"Surfaces", None))
        self.tabWidget_3Dview.setTabText(self.tabWidget_3Dview.indexOf(self.tab_41), QCoreApplication.translate("AMIGOpy", u"Plan_Brachy", None))
        self.tabWidget_3Dview.setTabText(self.tabWidget_3Dview.indexOf(self.tab_43), QCoreApplication.translate("AMIGOpy", u"Plan_Proton", None))
        self.View3DgroupBox_13.setTitle(QCoreApplication.translate("AMIGOpy", u"3D view", None))
        self.View3D_Apply.setText(QCoreApplication.translate("AMIGOpy", u"Apply", None))
        self.View3D_name_06.setText(QCoreApplication.translate("AMIGOpy", u"Isovalue ", None))
        self.View3D_name_08.setText(QCoreApplication.translate("AMIGOpy", u"Axial Limit", None))
        self.View3D_name_09.setText(QCoreApplication.translate("AMIGOpy", u"Cor. Limit", None))
        self.View3D_name_10.setText(QCoreApplication.translate("AMIGOpy", u"Sag. Limit", None))
        self.View3D_name_07.setText(QCoreApplication.translate("AMIGOpy", u"Threshold", None))
        self.View3DgroupBox_14.setTitle(QCoreApplication.translate("AMIGOpy", u"4D-CT", None))
        self.View3D_play4D.setText(QCoreApplication.translate("AMIGOpy", u"Play", None))
        self.View3D_name_12.setText(QCoreApplication.translate("AMIGOpy", u"Speed", None))
        self.View3D_name_11.setText(QCoreApplication.translate("AMIGOpy", u"Colormap", None))
        self.View3D_real_time_checkBox.setText(QCoreApplication.translate("AMIGOpy", u"Real-time", None))
        self.View3D_update_all_3D.setText(QCoreApplication.translate("AMIGOpy", u"Sync all", None))
        self.tabModules.setTabText(self.tabModules.indexOf(self._3Dview), QCoreApplication.translate("AMIGOpy", u"_3Dview", None))
        self.groupBox_2.setTitle("")
        self.but_create_comp_axes.setText(QCoreApplication.translate("AMIGOpy", u"Create", None))
        self.Comp_linkSlices.setText(QCoreApplication.translate("AMIGOpy", u"Link slices", None))
        self.link_win_lev.setText(QCoreApplication.translate("AMIGOpy", u"Link Window/Level", None))
        self.comp_link_zoom.setText(QCoreApplication.translate("AMIGOpy", u"Link zoom", None))
        self.tabModules.setTabText(self.tabModules.indexOf(self.im_compare_tab), QCoreApplication.translate("AMIGOpy", u"Compare", None))
        self.export_table_mat.setText(QCoreApplication.translate("AMIGOpy", u"EXPORT", None))
        self.Load_csv_mat.setText(QCoreApplication.translate("AMIGOpy", u"LOAD", None))
        self.Zeff_m.setText(QCoreApplication.translate("AMIGOpy", u"3.1", None))
        self.checkBox_calSPR.setText(QCoreApplication.translate("AMIGOpy", u"SPR", None))
        self.remove_row_table_mat.setText(QCoreApplication.translate("AMIGOpy", u"-", None))
        self.lineEdit.setText(QCoreApplication.translate("AMIGOpy", u"Column Name", None))
        self.lineEdit_41.setText(QCoreApplication.translate("AMIGOpy", u"HU High", None))
        self.checkBox_cal_I.setText(QCoreApplication.translate("AMIGOpy", u"I-value", None))
        self.label_3.setText(QCoreApplication.translate("AMIGOpy", u"Zeff m", None))
        self.reset_table_mat.setText(QCoreApplication.translate("AMIGOpy", u"Reset", None))
        self.add_row_table_mat.setText(QCoreApplication.translate("AMIGOpy", u"+", None))
        self.lineEdit_8.setText(QCoreApplication.translate("AMIGOpy", u"HU Low", None))
        self.get_HU_high.setText(QCoreApplication.translate("AMIGOpy", u"GET HU HIGH & LOW", None))
        self.checkBox_calRED.setText(QCoreApplication.translate("AMIGOpy", u"RED", None))
        self.cal_mat_ref_info.setText(QCoreApplication.translate("AMIGOpy", u"CALCULATE ALL", None))
        self.add_coll_table_mat.setText(QCoreApplication.translate("AMIGOpy", u"...Add...", None))
        self.remove_coll_table_mat.setText(QCoreApplication.translate("AMIGOpy", u"Remove", None))
        self.checkBox_calZeff.setText(QCoreApplication.translate("AMIGOpy", u"Zeff", None))
        self.lineEdit_47.setText(QCoreApplication.translate("AMIGOpy", u"I-value water (eV) - Ref.", None))
        self.DECTmenu.setTabText(self.DECTmenu.indexOf(self.tab), QCoreApplication.translate("AMIGOpy", u"Mat_Info", None))
        self.Ivalue_pre_calc_fit.setText(QCoreApplication.translate("AMIGOpy", u"Pre-Calculated Fit", None))
        self.Ivalue_calc_fit.setText(QCoreApplication.translate("AMIGOpy", u"Calculate Fit", None))
        self.lineEdit_3.setText(QCoreApplication.translate("AMIGOpy", u"Z - limit for each line (separated with an space)", None))
        self.I_value_z_up_lim.setText(QCoreApplication.translate("AMIGOpy", u"Z upper limits", None))
        self.Ivalue_plot.setText(QCoreApplication.translate("AMIGOpy", u"Plot", None))
        self.lineEdit_2.setText(QCoreApplication.translate("AMIGOpy", u"Number of Line fits", None))
        self.I_value_b_coeff.setText(QCoreApplication.translate("AMIGOpy", u"Coefficients (b)", None))
        self.I_value_z_lw_lim.setText(QCoreApplication.translate("AMIGOpy", u"Z lower limits", None))
        self.I_value_a_coeff.setText(QCoreApplication.translate("AMIGOpy", u"Coefficients (a)", None))
        self.I_Fit_limits.setText(QCoreApplication.translate("AMIGOpy", u"8.5", None))
        self.DECTmenu.setTabText(self.DECTmenu.indexOf(self.IValue), QCoreApplication.translate("AMIGOpy", u"Zeff vs I Value", None))
        self.RED_fit_01.setText(QCoreApplication.translate("AMIGOpy", u"a", None))
        self.RED_RMSE.setText(QCoreApplication.translate("AMIGOpy", u"RMSE", None))
        self.RED_calc_cal.setText(QCoreApplication.translate("AMIGOpy", u"Fit - Calculate", None))
        self.RED_get_ref.setText(QCoreApplication.translate("AMIGOpy", u"Get Ref", None))
        self.RED_r_square.setText(QCoreApplication.translate("AMIGOpy", u"R-square", None))
        self.RED_fit_03.setText(QCoreApplication.translate("AMIGOpy", u"b", None))
        self.RED_fit_02.setText(QCoreApplication.translate("AMIGOpy", u"alpha", None))
        self.DECTmenu.setTabText(self.DECTmenu.indexOf(self.tab_2), QCoreApplication.translate("AMIGOpy", u"RED", None))
        self.Zeff_r_square.setText(QCoreApplication.translate("AMIGOpy", u"R-square", None))
        self.Zeff_RMSE.setText(QCoreApplication.translate("AMIGOpy", u"RMSE", None))
        self.Zeff_fit_1.setText(QCoreApplication.translate("AMIGOpy", u"gamma", None))
        self.Zeff_get_ref.setText(QCoreApplication.translate("AMIGOpy", u"Get Ref", None))
        self.Zeff_fit_2.setText(QCoreApplication.translate("AMIGOpy", u"gamma_o", None))
        self.Zeff_calc_cal.setText(QCoreApplication.translate("AMIGOpy", u"Fit - Calculate", None))
        self.DECTmenu.setTabText(self.DECTmenu.indexOf(self.tab_3), QCoreApplication.translate("AMIGOpy", u"Zeff", None))
        self.Iv_calc_cal.setText(QCoreApplication.translate("AMIGOpy", u"Calculate", None))
        self.Ivalue_RMSE.setText(QCoreApplication.translate("AMIGOpy", u"RMSE", None))
        self.Iv_get_ref.setText(QCoreApplication.translate("AMIGOpy", u"Get Ref", None))
        self.DECTmenu.setTabText(self.DECTmenu.indexOf(self.tab_4), QCoreApplication.translate("AMIGOpy", u"I Value", None))
        self.lineEdit_46.setText(QCoreApplication.translate("AMIGOpy", u"RMSE", None))
        self.SPR_get_ref.setText(QCoreApplication.translate("AMIGOpy", u"Get Ref", None))
        self.SPR_calc_cal.setText(QCoreApplication.translate("AMIGOpy", u"Calculate", None))
        self.lineEdit_42.setText(QCoreApplication.translate("AMIGOpy", u"Reference energy (MeV)", None))
        self.DECTmenu.setTabText(self.DECTmenu.indexOf(self.tab_7), QCoreApplication.translate("AMIGOpy", u"SPR", None))
        self.groupBox_10.setTitle(QCoreApplication.translate("AMIGOpy", u"Process", None))
        self.Create_DECT_Images.setText(QCoreApplication.translate("AMIGOpy", u"Create IMAGES", None))
        self.checkBox_Im_RED.setText(QCoreApplication.translate("AMIGOpy", u"RED", None))
        self.checkBox_Im_Zeff.setText(QCoreApplication.translate("AMIGOpy", u"Zeff", None))
        self.checkBox_Im_SPR.setText(QCoreApplication.translate("AMIGOpy", u"SPR", None))
        self.checkBox_Im_I.setText(QCoreApplication.translate("AMIGOpy", u"I-value", None))
        self.groupBox_9.setTitle(QCoreApplication.translate("AMIGOpy", u"Plot", None))
        self.checkBox_newScplot.setText(QCoreApplication.translate("AMIGOpy", u"Hold plot", None))
        self.DECT_exp_scatt_data.setText(QCoreApplication.translate("AMIGOpy", u"Export", None))
        self.lineEdit_50.setText(QCoreApplication.translate("AMIGOpy", u"Point size", None))
        self.plot_roi_scatter.setText(QCoreApplication.translate("AMIGOpy", u"Plot", None))
        self.lineEdit_49.setText(QCoreApplication.translate("AMIGOpy", u"High keV or kV", None))
        self.lineEdit_48.setText(QCoreApplication.translate("AMIGOpy", u"Low keV or kV", None))
        self.export_all_DECT_tables.setText(QCoreApplication.translate("AMIGOpy", u"Export all tables", None))
        self.DECT_exp_fit_par.setText(QCoreApplication.translate("AMIGOpy", u"Export fit parameters", None))
        self.DECT_load_fit_par.setText(QCoreApplication.translate("AMIGOpy", u"Load fit parameters", None))
        self.DECTmenu.setTabText(self.DECTmenu.indexOf(self.tab_8), QCoreApplication.translate("AMIGOpy", u"Eval / Process", None))
        self.tabModules.setTabText(self.tabModules.indexOf(self.DECT_tab), QCoreApplication.translate("AMIGOpy", u"DECT", None))
        self.lineEdit_51.setText(QCoreApplication.translate("AMIGOpy", u"Total channel time", None))
        self.lineEdit_52.setText(QCoreApplication.translate("AMIGOpy", u"Total time", None))
        self.lineEdit_54.setText(QCoreApplication.translate("AMIGOpy", u"Plan Acitvity/kerma", None))
        self.lineEdit_53.setText(QCoreApplication.translate("AMIGOpy", u"Number of Channels", None))
        self.pushButton.setText(QCoreApplication.translate("AMIGOpy", u"Export", None))
        self.lineEdit_55.setText(QCoreApplication.translate("AMIGOpy", u"Current channel", None))
        self.checkBox_show_dw_plot.setText(QCoreApplication.translate("AMIGOpy", u"Show Active Dwells", None))
        self.checkBox_show_ch_plot.setText(QCoreApplication.translate("AMIGOpy", u"Show channels", None))
        self.checkBox_dw_ch_plot.setText(QCoreApplication.translate("AMIGOpy", u"Plot all channels", None))
        self.brachy_ch_plot.setText(QCoreApplication.translate("AMIGOpy", u"Plot", None))
        self.groupBox_11.setTitle(QCoreApplication.translate("AMIGOpy", u"PlotSettings", None))
        self.lineEdit_60.setText(QCoreApplication.translate("AMIGOpy", u"Line color", None))
        self.lineEdit_57.setText(QCoreApplication.translate("AMIGOpy", u"Ch. line width", None))
        self.lineEdit_56.setText(QCoreApplication.translate("AMIGOpy", u"Dw. point size", None))
        self.lineEdit_58.setText(QCoreApplication.translate("AMIGOpy", u"First ch. point size", None))
        self.lineEdit_59.setText(QCoreApplication.translate("AMIGOpy", u"Dw. color", None))
        self.lineEdit_61.setText(QCoreApplication.translate("AMIGOpy", u"1st point color", None))
        self.lineEdit_62.setText(QCoreApplication.translate("AMIGOpy", u"Structure", None))
        self.Brachy_groupBox_12.setTitle(QCoreApplication.translate("AMIGOpy", u"Channel settings", None))
        self.Brachy_setalldwtimes.setText(QCoreApplication.translate("AMIGOpy", u"Set all Dwell Times", None))
        self.Brachy_create_new_channel.setText(QCoreApplication.translate("AMIGOpy", u"Create New Channel", None))
        self.Brachy_DuplicateChannel.setText(QCoreApplication.translate("AMIGOpy", u"Duplicate Channel", None))
        self.Brachy_setIDD_distance.setText(QCoreApplication.translate("AMIGOpy", u"Change Inter dwell Distance", None))
        self.Brachy_DeadSpace_Offset.setText(QCoreApplication.translate("AMIGOpy", u"Dead space - Offset", None))
        self.Brachy_DeleteChannel.setText(QCoreApplication.translate("AMIGOpy", u"Delete Channel", None))
        self.Brachy_Calcualte_TG43.setText(QCoreApplication.translate("AMIGOpy", u"Calculate TG43 Dose", None))
        self.BrachytabWidget_2.setTabText(self.BrachytabWidget_2.indexOf(self.Br_tab_42), QCoreApplication.translate("AMIGOpy", u"Plan", None))
        self.brachy_save_tg43_source.setText(QCoreApplication.translate("AMIGOpy", u"Save", None))
        self.Brachy_load_sources.setText(QCoreApplication.translate("AMIGOpy", u"Load Sources", None))
        self.brachy_delete_source.setText(QCoreApplication.translate("AMIGOpy", u"Delete Source", None))
        self.Brachy_Radial_load.setText(QCoreApplication.translate("AMIGOpy", u"Load", None))
        self.Brachy_rad_eq.setText(QCoreApplication.translate("AMIGOpy", u"gL = A0 + A1*r + A2*r^2 + A3*r^3 + A4*r^4 + A5*r^5 (only withing the fit range)   ", None))
        self.Brachy_rad_A0L.setText(QCoreApplication.translate("AMIGOpy", u"A0", None))
        self.Brachy_rad_A1L.setText(QCoreApplication.translate("AMIGOpy", u"A1", None))
        self.Brachy_rad_A2L.setText(QCoreApplication.translate("AMIGOpy", u"A2", None))
        self.Brachy_rad_A3L.setText(QCoreApplication.translate("AMIGOpy", u"A3", None))
        self.Brachy_rad_A4L.setText(QCoreApplication.translate("AMIGOpy", u"A4", None))
        self.Brachy_rad_A5L.setText(QCoreApplication.translate("AMIGOpy", u"A5", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.Brachy_tab_45), QCoreApplication.translate("AMIGOpy", u"Radial Dose", None))
        self.Brachy_ani_dist_label.setText(QCoreApplication.translate("AMIGOpy", u"Distance (cm)", None))
        self.Brachy_load_ani.setText(QCoreApplication.translate("AMIGOpy", u"Load", None))
        self.Brach_plot_ani.setText(QCoreApplication.translate("AMIGOpy", u"Plot", None))
        self.Brachy_ani_plot_hold.setText(QCoreApplication.translate("AMIGOpy", u"Hold", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.Brachy_tab_46), QCoreApplication.translate("AMIGOpy", u"Anisotropy", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_36), QCoreApplication.translate("AMIGOpy", u"AlongAway", None))
        self.Brachy_cal_add_line.setText(QCoreApplication.translate("AMIGOpy", u"Add", None))
        self.Brachy_cal_Delete_line.setText(QCoreApplication.translate("AMIGOpy", u"Delete", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.DECT_tab_47), QCoreApplication.translate("AMIGOpy", u"Calibration", None))
        self.Brachy_doseRate_label.setText(QCoreApplication.translate("AMIGOpy", u"Dose Rate Constant ", None))
        self.Brachy_rad_leng_label.setText(QCoreApplication.translate("AMIGOpy", u"Source Length", None))
        self.Tg43_matrix_size.setTitle(QCoreApplication.translate("AMIGOpy", u"Dose Matrix", None))
        self.lineEdit_tg43_01.setText(QCoreApplication.translate("AMIGOpy", u"Dose grid (mm)", None))
        self.lineEdit_tg43_02.setText(QCoreApplication.translate("AMIGOpy", u"Matriz size (mm)", None))
        self.BrachytabWidget_2.setTabText(self.BrachytabWidget_2.indexOf(self.Br_tab_43), QCoreApplication.translate("AMIGOpy", u"TG43", None))
        self.Plan_tabs.setTabText(self.Plan_tabs.indexOf(self.Brachy_plan_tab), QCoreApplication.translate("AMIGOpy", u"Brachy", None))
        self.dose_matri_to_eqd2.setTitle(QCoreApplication.translate("AMIGOpy", u"Convert dose matrix to EQD2", None))
        self.eqd2_lab1.setText(QCoreApplication.translate("AMIGOpy", u"Select dose", None))
        self.eqd2_lab1_2.setText(QCoreApplication.translate("AMIGOpy", u"Select Structure", None))
        self.eqd2_lab1_3.setText(QCoreApplication.translate("AMIGOpy", u"\u03b1/\u03b2", None))
        self.add_to_ab_list.setText(QCoreApplication.translate("AMIGOpy", u"Add", None))
        self.delete_from_ab_list.setText(QCoreApplication.translate("AMIGOpy", u"Delete", None))
        self.n_fractions_label.setText(QCoreApplication.translate("AMIGOpy", u"Number of fractions", None))
        self.calc_eqd2.setText(QCoreApplication.translate("AMIGOpy", u"Convert to EQD2", None))
        self.ab_matrix.setText(QCoreApplication.translate("AMIGOpy", u"Save \u03b1/\u03b2 values", None))
        self.eqd2_calc.setTitle(QCoreApplication.translate("AMIGOpy", u"EQD2 Calculator", None))
        self.label_1_eqd2_calc_5.setText(QCoreApplication.translate("AMIGOpy", u"Gy", None))
        self.label_1_eqd2_calc_2.setText(QCoreApplication.translate("AMIGOpy", u"Total dose (Gy)", None))
        self.label_1_eqd2_calc_3.setText(QCoreApplication.translate("AMIGOpy", u"\u03b1/\u03b2", None))
        self.label_1_eqd2_calc_4.setText(QCoreApplication.translate("AMIGOpy", u"Number of fractions", None))
        self.calc_eqd2_2.setText(QCoreApplication.translate("AMIGOpy", u"Calculate EQD2", None))
        self.Plan_tabs.setTabText(self.Plan_tabs.indexOf(self.eqd2), QCoreApplication.translate("AMIGOpy", u"EQD2", None))
        self.dose_unit_Gy.setText(QCoreApplication.translate("AMIGOpy", u"Gy", None))
        self.DoseUnit.setText(QCoreApplication.translate("AMIGOpy", u"Dose Unit", None))
        self.VolumeUnit.setText(QCoreApplication.translate("AMIGOpy", u"Volume Unit", None))
        self.button_calculate_dvhs.setText(QCoreApplication.translate("AMIGOpy", u"Calculate DVHs", None))
        self.select_dose.setText(QCoreApplication.translate("AMIGOpy", u"Select Dose", None))
        self.volume_unit_percentage.setText(QCoreApplication.translate("AMIGOpy", u"%", None))
        self.volume_unit_cm3.setText(QCoreApplication.translate("AMIGOpy", u"cm\u00b3", None))
        self.Structures.setText(QCoreApplication.translate("AMIGOpy", u"Structures", None))
        self.dose_unit_percentage.setText(QCoreApplication.translate("AMIGOpy", u"%", None))
        self.reference_dose.setText(QCoreApplication.translate("AMIGOpy", u"Reference Dose", None))
        self.button_update_select_dose.setText(QCoreApplication.translate("AMIGOpy", u"Update", None))
        self.DoseStatistics.setText(QCoreApplication.translate("AMIGOpy", u"Dose Statistics ", None))
        self.button_select_all_rows_DST.setText(QCoreApplication.translate("AMIGOpy", u"Select all", None))
        self.DVHs.setText(QCoreApplication.translate("AMIGOpy", u"Dose Volume Histogram", None))
        self.button_update_plot.setText(QCoreApplication.translate("AMIGOpy", u"Plot", None))
        self.button_delete_column.setText(QCoreApplication.translate("AMIGOpy", u"Delete column", None))
        self.button_export_dose_stats_to_excel.setText(QCoreApplication.translate("AMIGOpy", u"Export to CSV", None))
        self.Dxx.setText(QCoreApplication.translate("AMIGOpy", u"Dx", None))
        self.vxx_t_label.setText(QCoreApplication.translate("AMIGOpy", u"to", None))
        self.button_calculate_vxx_dxx.setText(QCoreApplication.translate("AMIGOpy", u"Calculate / Add to table", None))
        self.Vxx.setText(QCoreApplication.translate("AMIGOpy", u"Vx", None))
        self.dxx_to_label.setText(QCoreApplication.translate("AMIGOpy", u"to", None))
        self.Mean.setText(QCoreApplication.translate("AMIGOpy", u"Mean", None))
        self.NumberOfInteractions.setText(QCoreApplication.translate("AMIGOpy", u"Number of Interactions", None))
        self.Y.setText(QCoreApplication.translate("AMIGOpy", u"Y", None))
        self.StandardDeviation.setText(QCoreApplication.translate("AMIGOpy", u"St. Dev.", None))
        self.X.setText(QCoreApplication.translate("AMIGOpy", u"X", None))
        self.T.setText(QCoreApplication.translate("AMIGOpy", u"T", None))
        self.button_apply_uncertainty.setText(QCoreApplication.translate("AMIGOpy", u"Apply", None))
        self.Z.setText(QCoreApplication.translate("AMIGOpy", u"Z", None))
        self.button_show_uncertainty_bands.setText(QCoreApplication.translate("AMIGOpy", u"Show Bands", None))
        self.tab_errors.setTabText(self.tab_errors.indexOf(self.uncertainty), QCoreApplication.translate("AMIGOpy", u"Uncertainty", None))
        self.tab_errors.setTabText(self.tab_errors.indexOf(self.error_simulation), QCoreApplication.translate("AMIGOpy", u"Error Simulation", None))
        self.Deviation_Metrics.setText(QCoreApplication.translate("AMIGOpy", u"Deviation Metrics", None))
        self.Plan_tabs.setTabText(self.Plan_tabs.indexOf(self.Plan_Evaluation), QCoreApplication.translate("AMIGOpy", u"Plan Evaluation ", None))
        self.groupBox_mat_to_struct.setTitle(QCoreApplication.translate("AMIGOpy", u"Materials to structures", None))
        self.remove_mat_from_struct.setText(QCoreApplication.translate("AMIGOpy", u"Remove material", None))
        self.assign_mat.setTitle(QCoreApplication.translate("AMIGOpy", u"Assign", None))
        self.mat_to_hu.setText(QCoreApplication.translate("AMIGOpy", u"Assign to HU range", None))
        self.label_mat_2.setText(QCoreApplication.translate("AMIGOpy", u"To", None))
        self.label_mat.setText(QCoreApplication.translate("AMIGOpy", u"From", None))
        self.mat_to_struct.setText(QCoreApplication.translate("AMIGOpy", u"Assign to structure", None))
        self.update_mat_struct_list.setText(QCoreApplication.translate("AMIGOpy", u"Update list", None))
        self.groupBox_mat_properties.setTitle(QCoreApplication.translate("AMIGOpy", u"Properties", None))
        self.element.setText(QCoreApplication.translate("AMIGOpy", u"Column Name", None))
        self.Add_mat.setText(QCoreApplication.translate("AMIGOpy", u"Add Material", None))
        self.add_element.setText(QCoreApplication.translate("AMIGOpy", u"Add Element", None))
        self.del_element.setText(QCoreApplication.translate("AMIGOpy", u"Delete Element", None))
        self.del_mat.setText(QCoreApplication.translate("AMIGOpy", u"Delete Material", None))
        self.save_mat_table.setText(QCoreApplication.translate("AMIGOpy", u"Save", None))
        self.undo_mat_tab.setText(QCoreApplication.translate("AMIGOpy", u"Reset", None))
        self.mat_to_HU_box.setTitle(QCoreApplication.translate("AMIGOpy", u"Materials to HU ranges", None))
        self.remove_mat_fromhu.setText(QCoreApplication.translate("AMIGOpy", u"Remove material", None))
        self.del_mat_map.setText(QCoreApplication.translate("AMIGOpy", u"Delete Material Map", None))
        self.create_mat_map.setText(QCoreApplication.translate("AMIGOpy", u"Create Material Map", None))
        self.Plan_tabs.setTabText(self.Plan_tabs.indexOf(self.tab_mat_assignment), QCoreApplication.translate("AMIGOpy", u"Material Assignment", None))
        self.save_changes_ct_cal.setText(QCoreApplication.translate("AMIGOpy", u"Update", None))
        self.Export_ct_cal.setText(QCoreApplication.translate("AMIGOpy", u"Export", None))
        self.load_ct_cal.setText(QCoreApplication.translate("AMIGOpy", u"Load", None))
        self.ct_cal_save_copy.setText(QCoreApplication.translate("AMIGOpy", u"Save", None))
        self.ct_cal_add_row.setText(QCoreApplication.translate("AMIGOpy", u"Add row", None))
        self.create_density_map.setText(QCoreApplication.translate("AMIGOpy", u"Create density map", None))
        self.create_density_map__from_mat_map.setText(QCoreApplication.translate("AMIGOpy", u"Create density map from material map", None))
        self.delete_density_map.setText(QCoreApplication.translate("AMIGOpy", u"Delete density map", None))
        self.override_no_tissue.setText(QCoreApplication.translate("AMIGOpy", u"Override non tissue materials densities", None))
        self.Plan_tabs.setTabText(self.Plan_tabs.indexOf(self.density_map_tab), QCoreApplication.translate("AMIGOpy", u"Density Map", None))
        self.tabModules.setTabText(self.tabModules.indexOf(self.Plan_tab), QCoreApplication.translate("AMIGOpy", u"Plan", None))
        self.tabWidget_5.setTabText(self.tabWidget_5.indexOf(self.tab_23), QCoreApplication.translate("AMIGOpy", u"PlanCheck", None))
        self.tabWidget_5.setTabText(self.tabWidget_5.indexOf(self.tab_24), QCoreApplication.translate("AMIGOpy", u"DoseMetrics", None))
        self.IrIS_cal_load_meas.setText(QCoreApplication.translate("AMIGOpy", u"Load Measurement", None))
        self.lineEdit_44.setText(QCoreApplication.translate("AMIGOpy", u"Markers initial shift (mm)   X  Y  Z", None))
        self.IrIS_cal_load_ref.setText(QCoreApplication.translate("AMIGOpy", u"Load Ref Markers", None))
        self.lineEdit_45.setText(QCoreApplication.translate("AMIGOpy", u"Markers initial rotation (deg)", None))
        self.lineEdit_43.setText(QCoreApplication.translate("AMIGOpy", u"Source initial position (mm)  X  Y  Z", None))
        self.lineEdit_40.setText(QCoreApplication.translate("AMIGOpy", u"Reference Marker ID", None))
        self.IrIS_Cal_plot_deg.setText(QCoreApplication.translate("AMIGOpy", u"XYZ (deg)", None))
        self.IrIS_Cal_plot_mm.setText(QCoreApplication.translate("AMIGOpy", u" XYZ (mm)", None))
        self.IrIS_cal_plot.setText(QCoreApplication.translate("AMIGOpy", u"PLOT", None))
        self.IrIS_cal_save.setText(QCoreApplication.translate("AMIGOpy", u"Save", None))
        self.IrIS_cal_export.setText(QCoreApplication.translate("AMIGOpy", u"Export CSV", None))
        self.IrIS_cal_findMK.setText(QCoreApplication.translate("AMIGOpy", u"Find Markers", None))
        self.lineEdit_11.setText(QCoreApplication.translate("AMIGOpy", u"Ref. Frame", None))
        self.tabWidget_7.setTabText(self.tabWidget_7.indexOf(self.tab_28), QCoreApplication.translate("AMIGOpy", u"Tab 1", None))
        self.tabWidget_7.setTabText(self.tabWidget_7.indexOf(self.tab_29), QCoreApplication.translate("AMIGOpy", u"Tab 2", None))
        self.tabWidget_5.setTabText(self.tabWidget_5.indexOf(self.tab_15), QCoreApplication.translate("AMIGOpy", u"Calibration", None))
        self.groupBox_4.setTitle("")
        self.pushButton_13.setText(QCoreApplication.translate("AMIGOpy", u"LoadCSV", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("AMIGOpy", u"Plot Type", None))
        self.lineEdit_38.setText(QCoreApplication.translate("AMIGOpy", u"Grad. between (N) frames", None))
        self.IrIS_ProcessPlot.setText(QCoreApplication.translate("AMIGOpy", u"Process", None))
        self.lineEdit_25.setText(QCoreApplication.translate("AMIGOpy", u"Downsize (N x N)", None))
        self.IrIS_Plot.setText(QCoreApplication.translate("AMIGOpy", u"Plot", None))
        self.IrIS_findPK.setText(QCoreApplication.translate("AMIGOpy", u"Find Dwells", None))
        self.Average.setTitle(QCoreApplication.translate("AMIGOpy", u"Average dwells (Single frame per dwell)", None))
        self.IrIsAVg_dw.setText(QCoreApplication.translate("AMIGOpy", u"Avg Dwells", None))
        self.lineEdit_10.setText(QCoreApplication.translate("AMIGOpy", u"Marging to avoid motion (Frames)", None))
        self.checkBox_IrIS_time_rel.setText(QCoreApplication.translate("AMIGOpy", u"Time relative to the first channel", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("AMIGOpy", u"Average frames (within dwell)", None))
        self.IrIsAVg_Framesdw.setText(QCoreApplication.translate("AMIGOpy", u"Avg Frames", None))
        self.lineEdit_12.setText(QCoreApplication.translate("AMIGOpy", u"Number of frames to average", None))
        self.IrIS_ExportCSV.setText(QCoreApplication.translate("AMIGOpy", u"ExportCSV", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_20), QCoreApplication.translate("AMIGOpy", u"Dwell_Find", None))
        self.remove_dw_table.setText(QCoreApplication.translate("AMIGOpy", u"Delete", None))
        self.add_dw_table.setText(QCoreApplication.translate("AMIGOpy", u"Add", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_21), QCoreApplication.translate("AMIGOpy", u"Dwell_List", None))
        self.lineEdit_34.setText(QCoreApplication.translate("AMIGOpy", u"Skip first ", None))
        self.lineEdit_27.setText(QCoreApplication.translate("AMIGOpy", u"Threshold", None))
        self.lineEdit_33.setText(QCoreApplication.translate("AMIGOpy", u"Plateau size", None))
        self.lineEdit_30.setText(QCoreApplication.translate("AMIGOpy", u"Relative height", None))
        self.lineEdit_29.setText(QCoreApplication.translate("AMIGOpy", u"Prominence", None))
        self.lineEdit_26.setText(QCoreApplication.translate("AMIGOpy", u"Height", None))
        self.lineEdit_35.setText(QCoreApplication.translate("AMIGOpy", u"Skip last", None))
        self.checkBox_Pk_find_range.setText(QCoreApplication.translate("AMIGOpy", u"Define range using intensity", None))
        self.lineEdit_36.setText(QCoreApplication.translate("AMIGOpy", u"Scipy signal find peaks", None))
        self.lineEdit_32.setText(QCoreApplication.translate("AMIGOpy", u"Window length", None))
        self.lineEdit_31.setText(QCoreApplication.translate("AMIGOpy", u"Width", None))
        self.lineEdit_28.setText(QCoreApplication.translate("AMIGOpy", u"Distance", None))
        self.lineEdit_37.setText(QCoreApplication.translate("AMIGOpy", u"Additional AMIGOpy settings", None))
        self.Pk_Plot.setText(QCoreApplication.translate("AMIGOpy", u"FindPk", None))
        self.checkBox_Pk_find_adj_1st_last.setText(QCoreApplication.translate("AMIGOpy", u"Adjust first/last", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_22), QCoreApplication.translate("AMIGOpy", u"Pk Settings", None))
        self.Source_save_cal.setText(QCoreApplication.translate("AMIGOpy", u"Save", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_26), QCoreApplication.translate("AMIGOpy", u"Source calibration", None))
        self.IrIsAVg_loadSSD_check.setText(QCoreApplication.translate("AMIGOpy", u"Load from SSD", None))
        self.lineEdit_9.setText(QCoreApplication.translate("AMIGOpy", u"Channel", None))
        self.Pk_find_processl_all_check.setText(QCoreApplication.translate("AMIGOpy", u"Process all", None))
        self.groupBox_3.setTitle("")
        self.groupBox_5.setTitle("")
        self.tabWidget_5.setTabText(self.tabWidget_5.indexOf(self.tab_16), QCoreApplication.translate("AMIGOpy", u"Evaluation", None))
        self.tabWidget_5.setTabText(self.tabWidget_5.indexOf(self.tab_25), QCoreApplication.translate("AMIGOpy", u"Advanced", None))
        self.tabModules.setTabText(self.tabModules.indexOf(self.IrIS_tab), QCoreApplication.translate("AMIGOpy", u"IrIS", None))
        self.LoadCSVView.setText(QCoreApplication.translate("AMIGOpy", u"Load File", None))
        self.lineEdit_14.setText(QCoreApplication.translate("AMIGOpy", u"X - Axes", None))
        self.gcode_f_name.setText(QCoreApplication.translate("AMIGOpy", u"GCODE_FILE_Name", None))
        self.PlotCSVView.setText(QCoreApplication.translate("AMIGOpy", u"Plot", None))
        self.lineEdit_16.setText(QCoreApplication.translate("AMIGOpy", u"Lines to skip", None))
        self.cvs_add_plot.setText(QCoreApplication.translate("AMIGOpy", u"Hold Plot", None))
        self.exp_csv_2_gcode.setText(QCoreApplication.translate("AMIGOpy", u"Exp. GCODE", None))
        self.lineEdit_17.setText(QCoreApplication.translate("AMIGOpy", u"Header line", None))
        self.lineEdit_13.setText(QCoreApplication.translate("AMIGOpy", u"Delimitation", None))
        self.CSV_Oper_Apply.setText(QCoreApplication.translate("AMIGOpy", u"Apply", None))
        self.CSVViewText.setHtml(QCoreApplication.translate("AMIGOpy", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:7.8pt;\"><br /></p></body></html>", None))
        self.lineEdit_4.setText(QCoreApplication.translate("AMIGOpy", u"Cycles", None))
        self.lineEdit_15.setText(QCoreApplication.translate("AMIGOpy", u"Y - Axes", None))
        self.tabModules.setTabText(self.tabModules.indexOf(self.tab_27), QCoreApplication.translate("AMIGOpy", u"CSV Files", None))
        self.groupBox_BrCv_importCSV.setTitle(QCoreApplication.translate("AMIGOpy", u"Import CSV/VXP", None))
        self.lineEdit_BrCv_5.setText(QCoreApplication.translate("AMIGOpy", u"Delimiter", None))
        self.lineEdit_BrCv_6.setText(QCoreApplication.translate("AMIGOpy", u"Lines to skip", None))
        self.lineEdit_BrCv_7.setText(QCoreApplication.translate("AMIGOpy", u"Header line", None))
        self.flipCSV_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Flip", None))
        self.loadCSVView_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Import", None))
        self.lineEdit_BrCv_8.setText(QCoreApplication.translate("AMIGOpy", u"Time unit", None))
        self.groupBox_BrCv_createCurve.setTitle(QCoreApplication.translate("AMIGOpy", u"Create analytical curve", None))
        self.lineEdit_BrCv_1.setText(QCoreApplication.translate("AMIGOpy", u"No. of cycles", None))
        self.lineEdit_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Cycle time (s)", None))
        self.lineEdit_BrCv_3.setText(QCoreApplication.translate("AMIGOpy", u"Amplitude (mm)", None))
        self.setParamsCreateCv.setText(QCoreApplication.translate("AMIGOpy", u"Set parameters", None))
        self.createCv.setText(QCoreApplication.translate("AMIGOpy", u"Create", None))
        self.lineEdit_BrCv_4.setText(QCoreApplication.translate("AMIGOpy", u"Curve type", None))
        self.lineEdit_BrCv_2.setText(QCoreApplication.translate("AMIGOpy", u"Sampling frequency (Hz)", None))
        self.tabWidget_BrCv.setTabText(self.tabWidget_BrCv.indexOf(self.tab_import), QCoreApplication.translate("AMIGOpy", u"Import && create", None))
        self.breathhold_BrCv.setTitle(QCoreApplication.translate("AMIGOpy", u"Breath hold", None))
        self.lineEdit_BrCv_30.setText(QCoreApplication.translate("AMIGOpy", u"Duration (s)", None))
        self.lineEdit_BrCv_29.setText(QCoreApplication.translate("AMIGOpy", u"Start timestamp (s)", None))
        self.applyBreathhold.setText(QCoreApplication.translate("AMIGOpy", u"Apply breath hold", None))
        self.operations_BrCv.setTitle(QCoreApplication.translate("AMIGOpy", u"Operations", None))
        self.lineEdit_BrCv_22.setText(QCoreApplication.translate("AMIGOpy", u"Shift amplitude (mm)", None))
        self.lineEdit_BrCv_23.setText(QCoreApplication.translate("AMIGOpy", u"Max. amplitude threshold (mm)", None))
        self.lineEdit_BrCv_20.setText(QCoreApplication.translate("AMIGOpy", u"Scale frequency", None))
        self.lineEdit_BrCv_21.setText(QCoreApplication.translate("AMIGOpy", u"Scale amplitude", None))
        self.setMinZero_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Set min value to zero", None))
        self.applyOper_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Apply operations", None))
        self.export_BrCv.setTitle(QCoreApplication.translate("AMIGOpy", u"Export", None))
        self.exportData_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Export CSV", None))
        self.lineEdit_BrCv_28.setText(QCoreApplication.translate("AMIGOpy", u"Filename", None))
        self.interp_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Interpolate", None))
        self.exportGCODE_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Export GCODE", None))
        self.lineEdit_77.setText(QCoreApplication.translate("AMIGOpy", u"ms", None))
        self.lineEdit_BrCv_24.setText(QCoreApplication.translate("AMIGOpy", u"Copy fragment", None))
        self.lineEdit_83.setText(QCoreApplication.translate("AMIGOpy", u"Compress below speed", None))
        self.undoOperations_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Undo", None))
        self.smoothing_BrCv.setTitle(QCoreApplication.translate("AMIGOpy", u"Smoothing", None))
        self.smooth_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Smoothing", None))
        self.lineEdit_79.setText(QCoreApplication.translate("AMIGOpy", u"kernel size", None))
        self.lineEdit_78.setText(QCoreApplication.translate("AMIGOpy", u"method", None))
        self.lineEdit_81.setText(QCoreApplication.translate("AMIGOpy", u"cut-off frequency", None))
        self.lineEdit_BrCv_26.setText(QCoreApplication.translate("AMIGOpy", u"X max", None))
        self.clipCycles_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Clip to whole cycles", None))
        self.lineEdit_BrCv_25.setText(QCoreApplication.translate("AMIGOpy", u"X min", None))
        self.cropRangeEdit_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Crop", None))
        self.lineEdit_BrCv_27.setText(QCoreApplication.translate("AMIGOpy", u"X-axis", None))
        self.tabWidget_BrCv.setTabText(self.tabWidget_BrCv.indexOf(self.tab_BrCv_edit), QCoreApplication.translate("AMIGOpy", u"Edit && export", None))
        self.calcStats_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Calculate statistics", None))
        self.lineEdit_BrCv_9.setText(QCoreApplication.translate("AMIGOpy", u"Amplitude", None))
        self.lineEdit_BrCv_10.setText(QCoreApplication.translate("AMIGOpy", u"Cycle time ", None))
        self.lineEdit_BrCv_11.setText(QCoreApplication.translate("AMIGOpy", u"Speed", None))
        self.lineEdit_BrCv_15.setText(QCoreApplication.translate("AMIGOpy", u"Y - Axis", None))
        self.plotView_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Plot", None))
        self.lineEdit_BrCv_14.setText(QCoreApplication.translate("AMIGOpy", u"X - Axis", None))
        self.lineEdit_82.setText(QCoreApplication.translate("AMIGOpy", u"Title", None))
        self.plotPeaks_BrCv.setText(QCoreApplication.translate("AMIGOpy", u"Plot peaks", None))
        self.tabWidget_BrCv.setTabText(self.tabWidget_BrCv.indexOf(self.tab_BrCv_plot), QCoreApplication.translate("AMIGOpy", u"Analyze && visualize", None))
        self.loadDuetPage.setText(QCoreApplication.translate("AMIGOpy", u"Load Duet Web Control", None))
        self.lineEdit_65.setText(QCoreApplication.translate("AMIGOpy", u"IP address", None))
        self.definePhOperFolder.setText(QCoreApplication.translate("AMIGOpy", u"Define Input Folder", None))
        self.BrCv_PhOperWidget.setTabText(self.BrCv_PhOperWidget.indexOf(self.tab_DuetControl), QCoreApplication.translate("AMIGOpy", u"Duet Web Control", None))
        self.lineEdit_MoVeOffset.setText(QCoreApplication.translate("AMIGOpy", u"Offset", None))
        self.MoVeAutoControl.setText(QCoreApplication.translate("AMIGOpy", u"Auto-control", None))
        self.lineEdit_MoVeSF.setText(QCoreApplication.translate("AMIGOpy", u"Speed factor", None))
        self.lineEdit_80.setText(QCoreApplication.translate("AMIGOpy", u"System latency (s)", None))
        self.MoVeAcqStart.setText(QCoreApplication.translate("AMIGOpy", u"Acquisition Start", None))
        self.exportDataMoVe.setText(QCoreApplication.translate("AMIGOpy", u"Export motion verification data", None))
        self.BrCv_PhOperWidget.setTabText(self.BrCv_PhOperWidget.indexOf(self.tab_MoVe), QCoreApplication.translate("AMIGOpy", u"Motion Verification", None))
        self.tabWidget_BrCv.setTabText(self.tabWidget_BrCv.indexOf(self.tab_PhOper), QCoreApplication.translate("AMIGOpy", u"Phantom operation", None))
        self.tabModules.setTabText(self.tabModules.indexOf(self.tab_BrCv), QCoreApplication.translate("AMIGOpy", u"Breathing curves", None))
        self.groupBox_segStruct.setTitle(QCoreApplication.translate("AMIGOpy", u"Structures overview", None))
        self.createSegStruct.setText(QCoreApplication.translate("AMIGOpy", u"Create structure", None))
        self.lineEdit_createStructSeg.setText(QCoreApplication.translate("AMIGOpy", u"Structure name", None))
        self.initStructCheck.setText(QCoreApplication.translate("AMIGOpy", u"All series", None))
        self.deleteSegStruct.setText(QCoreApplication.translate("AMIGOpy", u"Delete structure", None))
        self.threshMinBox.setText(QCoreApplication.translate("AMIGOpy", u"Min. HU threshold", None))
        self.threshMaxBox.setText(QCoreApplication.translate("AMIGOpy", u"Max. HU threshold", None))
        self.undoSegText.setText(QCoreApplication.translate("AMIGOpy", u"Undo", None))
        self.undoSeg.setText(QCoreApplication.translate("AMIGOpy", u"undo", None))
        self.segBrushButton.setText(QCoreApplication.translate("AMIGOpy", u"Brush", None))
        self.segEraseButton.setText(QCoreApplication.translate("AMIGOpy", u"Eraser", None))
        self.BrushSizeText.setText(QCoreApplication.translate("AMIGOpy", u"Brush size", None))
        self.brushClipHU.setText(QCoreApplication.translate("AMIGOpy", u"Use HU thresholds", None))
        self.segBrushBox.setText(QCoreApplication.translate("AMIGOpy", u"Brush", None))
        self.segEraseBox.setText(QCoreApplication.translate("AMIGOpy", u"Eraser", None))
        self.toolBox_seg.setItemText(self.toolBox_seg.indexOf(self.seg_manual_contour), QCoreApplication.translate("AMIGOpy", u"Manual contouring && edits", None))
        self.lineEdit_75.setText(QCoreApplication.translate("AMIGOpy", u"Min slice index", None))
        self.applyThreshSeg.setText(QCoreApplication.translate("AMIGOpy", u"Apply threshold", None))
        self.lineEdit_76.setText(QCoreApplication.translate("AMIGOpy", u"Max slice index", None))
        self.toolBox_seg.setItemText(self.toolBox_seg.indexOf(self.page_thresholding), QCoreApplication.translate("AMIGOpy", u"Thresholding", None))
        self.lineEdit_70.setText(QCoreApplication.translate("AMIGOpy", u"Connectivity", None))
        self.lineEdit_67.setText(QCoreApplication.translate("AMIGOpy", u"Operation", None))
        self.lineEdit_69.setText(QCoreApplication.translate("AMIGOpy", u"Rank (dimension)", None))
        self.lineEdit_68.setText(QCoreApplication.translate("AMIGOpy", u"Iterations", None))
        self.UndoMorphOper.setText(QCoreApplication.translate("AMIGOpy", u"Undo", None))
        self.ApplyMorphOper.setText(QCoreApplication.translate("AMIGOpy", u"Apply", None))
        self.toolBox_seg.setItemText(self.toolBox_seg.indexOf(self.morph_oper), QCoreApplication.translate("AMIGOpy", u"Morphological operations", None))
        self.calcSegStatsButton.setText(QCoreApplication.translate("AMIGOpy", u"Calculate statistics", None))
        self.exportSegStatsButton.setText(QCoreApplication.translate("AMIGOpy", u"Export statistics", None))
        self.exportSegStrucButton.setText(QCoreApplication.translate("AMIGOpy", u"Export structures", None))
        self.toolBox_seg.setItemText(self.toolBox_seg.indexOf(self.page), QCoreApplication.translate("AMIGOpy", u"Export && analyze", None))
        self.tabModules.setTabText(self.tabModules.indexOf(self.tab_seg), QCoreApplication.translate("AMIGOpy", u"Segmentation", None))
        self.groupBox.setTitle(QCoreApplication.translate("AMIGOpy", u"GroupBox", None))
        self.lineEdit_22.setText(QCoreApplication.translate("AMIGOpy", u"PMI", None))
        self.lineEdit_23.setText(QCoreApplication.translate("AMIGOpy", u"Transparency", None))
        self.lineEdit_18.setText(QCoreApplication.translate("AMIGOpy", u"Layer 0", None))
        self.lineEdit_19.setText(QCoreApplication.translate("AMIGOpy", u"Layer 1", None))
        self.lineEdit_24.setText(QCoreApplication.translate("AMIGOpy", u"Active layer", None))
        self.lineEdit_21.setText(QCoreApplication.translate("AMIGOpy", u"Layer 3", None))
        self.lineEdit_20.setText(QCoreApplication.translate("AMIGOpy", u"Layer 2", None))
        self.groupBox1.setTitle("")
    # retranslateUi

