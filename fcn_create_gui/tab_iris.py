# -*- coding: utf-8 -*-
"""
tab_iris.py - AMIGOpy GUI Module
===================================

This file is part of the fcn_create_gui package which replaces the
auto-generated uiImGUI.py (from Qt Designer / pyside6-uic).

All widget attribute names are preserved for backward compatibility
with existing signal/slot connections in init_buttons.py, init_tables.py,
display functions, etc.
"""

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame, QGraphicsView, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLCDNumber, QLabel,
    QLayout, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QProgressBar, QPushButton, QRadioButton,
    QSizePolicy, QSlider, QSpacerItem, QSpinBox,
    QStatusBar, QTabWidget, QTableView, QTableWidget,
    QTableWidgetItem, QTextEdit, QToolBox, QToolButton,
    QTreeView, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
except ImportError:
    pass


def create_tab_iris(w):
    """
    Create the IrIS module tab (IrIS_tab).

    Creates the In-room Imaging System interface:
    - tabWidget_5 with sub-tabs:
      * PlanCheck: plan verification tools
      * DoseMetrics: dose metric calculations
      * Calibration: IrIS calibration with load/operations/calibration
      * Evaluation: dwell finding, peak settings, source calibration
      * Advanced: advanced analysis tools

    Args:
        w: The main application window (QMainWindow instance).
           All widgets are attached as attributes on w.
    """
    # Shared size policies and fonts
    sizePolicy = w._size_policies['sizePolicy']
    sizePolicy1 = w._size_policies['sizePolicy1']
    sizePolicy2 = w._size_policies['sizePolicy2']
    sizePolicy3 = w._size_policies['sizePolicy3']
    sizePolicy4 = w._size_policies['sizePolicy4']
    sizePolicy5 = w._size_policies['sizePolicy5']
    sizePolicy6 = w._size_policies['sizePolicy6']
    sizePolicy7 = w._size_policies['sizePolicy7']
    sizePolicy8 = w._size_policies['sizePolicy8']
    sizePolicy9 = w._size_policies['sizePolicy9']

    font = w._fonts['font']
    font1 = w._fonts['font1']
    font2 = w._fonts['font2']
    font3 = w._fonts['font3']
    w.IrIS_tab = QWidget()
    w.IrIS_tab.setObjectName(u"IrIS_tab")
    w.gridLayout_10 = QGridLayout(w.IrIS_tab)
    w.gridLayout_10.setObjectName(u"gridLayout_10")
    w.tabWidget_5 = QTabWidget(w.IrIS_tab)
    w.tabWidget_5.setObjectName(u"tabWidget_5")
    w.tab_23 = QWidget()
    w.tab_23.setObjectName(u"tab_23")
    w.tabWidget_5.addTab(w.tab_23, "")
    w.tab_24 = QWidget()
    w.tab_24.setObjectName(u"tab_24")
    w.tabWidget_5.addTab(w.tab_24, "")
    w.tab_15 = QWidget()
    w.tab_15.setObjectName(u"tab_15")
    w.gridLayout_11 = QGridLayout(w.tab_15)
    w.gridLayout_11.setObjectName(u"gridLayout_11")
    w.line_9 = QFrame(w.tab_15)
    w.line_9.setObjectName(u"line_9")
    w.line_9.setFrameShape(QFrame.Shape.HLine)
    w.line_9.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_11.addWidget(w.line_9, 2, 0, 1, 3)

    w.IrIS_cal_widget01 = QWidget(w.tab_15)
    w.IrIS_cal_widget01.setObjectName(u"IrIS_cal_widget01")

    w.gridLayout_11.addWidget(w.IrIS_cal_widget01, 1, 0, 1, 1)

    w.IrIS_cal_widget02 = QWidget(w.tab_15)
    w.IrIS_cal_widget02.setObjectName(u"IrIS_cal_widget02")
    w.IrIS_cal_widget02.setEnabled(True)

    w.gridLayout_11.addWidget(w.IrIS_cal_widget02, 1, 1, 1, 1)

    w.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_11.addItem(w.verticalSpacer_6, 3, 0, 1, 1)

    w.tabWidget_7 = QTabWidget(w.tab_15)
    w.tabWidget_7.setObjectName(u"tabWidget_7")
    w.tab_28 = QWidget()
    w.tab_28.setObjectName(u"tab_28")
    w.gridLayout_27 = QGridLayout(w.tab_28)
    w.gridLayout_27.setObjectName(u"gridLayout_27")
    w.IrIS_cal_MK_02 = QDoubleSpinBox(w.tab_28)
    w.IrIS_cal_MK_02.setObjectName(u"IrIS_cal_MK_02")
    w.IrIS_cal_MK_02.setMinimum(-999999.000000000000000)
    w.IrIS_cal_MK_02.setMaximum(9999999.000000000000000)
    w.IrIS_cal_MK_02.setValue(0.000000000000000)

    w.gridLayout_27.addWidget(w.IrIS_cal_MK_02, 3, 2, 1, 1)

    w.IrIS_cal_Sour_01 = QDoubleSpinBox(w.tab_28)
    w.IrIS_cal_Sour_01.setObjectName(u"IrIS_cal_Sour_01")
    w.IrIS_cal_Sour_01.setMinimum(-999999.000000000000000)
    w.IrIS_cal_Sour_01.setMaximum(9999999.000000000000000)
    w.IrIS_cal_Sour_01.setValue(177.000000000000000)

    w.gridLayout_27.addWidget(w.IrIS_cal_Sour_01, 5, 0, 1, 1)

    w.horizontalSpacer_21 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_27.addItem(w.horizontalSpacer_21, 18, 13, 1, 1)

    w.IrIS_cal_MK_06 = QDoubleSpinBox(w.tab_28)
    w.IrIS_cal_MK_06.setObjectName(u"IrIS_cal_MK_06")
    w.IrIS_cal_MK_06.setMinimum(-999999.000000000000000)
    w.IrIS_cal_MK_06.setMaximum(9999999.000000000000000)

    w.gridLayout_27.addWidget(w.IrIS_cal_MK_06, 3, 6, 1, 1)

    w.IrIS_cal_MK_01 = QDoubleSpinBox(w.tab_28)
    w.IrIS_cal_MK_01.setObjectName(u"IrIS_cal_MK_01")
    w.IrIS_cal_MK_01.setMinimum(-999999.000000000000000)
    w.IrIS_cal_MK_01.setMaximum(9999999.000000000000000)
    w.IrIS_cal_MK_01.setValue(0.000000000000000)

    w.gridLayout_27.addWidget(w.IrIS_cal_MK_01, 3, 0, 1, 1)

    w.IrIS_cal_MK_03 = QDoubleSpinBox(w.tab_28)
    w.IrIS_cal_MK_03.setObjectName(u"IrIS_cal_MK_03")
    w.IrIS_cal_MK_03.setMinimum(-999999.000000000000000)
    w.IrIS_cal_MK_03.setMaximum(9999999.000000000000000)

    w.gridLayout_27.addWidget(w.IrIS_cal_MK_03, 3, 3, 1, 1)

    w.line_20 = QFrame(w.tab_28)
    w.line_20.setObjectName(u"line_20")
    w.line_20.setFrameShape(QFrame.Shape.HLine)
    w.line_20.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_27.addWidget(w.line_20, 1, 0, 1, 16)

    w.IrIS_cal_load_meas = QPushButton(w.tab_28)
    w.IrIS_cal_load_meas.setObjectName(u"IrIS_cal_load_meas")

    w.gridLayout_27.addWidget(w.IrIS_cal_load_meas, 18, 11, 1, 1)

    w.IrIS_cal_MK_04 = QDoubleSpinBox(w.tab_28)
    w.IrIS_cal_MK_04.setObjectName(u"IrIS_cal_MK_04")
    w.IrIS_cal_MK_04.setMinimum(-999999.000000000000000)
    w.IrIS_cal_MK_04.setMaximum(9999999.000000000000000)

    w.gridLayout_27.addWidget(w.IrIS_cal_MK_04, 3, 4, 1, 1)

    w.IrIS_cal_ref_table = QTableWidget(w.tab_28)
    w.IrIS_cal_ref_table.setObjectName(u"IrIS_cal_ref_table")

    w.gridLayout_27.addWidget(w.IrIS_cal_ref_table, 2, 11, 16, 5)

    w.lineEdit_44 = QLineEdit(w.tab_28)
    w.lineEdit_44.setObjectName(u"lineEdit_44")
    w.lineEdit_44.setEnabled(False)

    w.gridLayout_27.addWidget(w.lineEdit_44, 2, 0, 1, 4)

    w.IrIS_cal_load_ref = QPushButton(w.tab_28)
    w.IrIS_cal_load_ref.setObjectName(u"IrIS_cal_load_ref")

    w.gridLayout_27.addWidget(w.IrIS_cal_load_ref, 18, 12, 1, 1)

    w.line_21 = QFrame(w.tab_28)
    w.line_21.setObjectName(u"line_21")
    w.line_21.setFrameShape(QFrame.Shape.VLine)
    w.line_21.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_27.addWidget(w.line_21, 2, 10, 18, 1)

    w.IrIS_cal_MK_05 = QDoubleSpinBox(w.tab_28)
    w.IrIS_cal_MK_05.setObjectName(u"IrIS_cal_MK_05")
    w.IrIS_cal_MK_05.setMinimum(-999999.000000000000000)
    w.IrIS_cal_MK_05.setMaximum(9999999.000000000000000)

    w.gridLayout_27.addWidget(w.IrIS_cal_MK_05, 3, 5, 1, 1)

    w.lineEdit_45 = QLineEdit(w.tab_28)
    w.lineEdit_45.setObjectName(u"lineEdit_45")
    w.lineEdit_45.setEnabled(False)

    w.gridLayout_27.addWidget(w.lineEdit_45, 2, 4, 1, 3)

    w.lineEdit_43 = QLineEdit(w.tab_28)
    w.lineEdit_43.setObjectName(u"lineEdit_43")
    w.lineEdit_43.setEnabled(False)

    w.gridLayout_27.addWidget(w.lineEdit_43, 4, 0, 1, 4)

    w.IrIS_cal_Sour_02 = QDoubleSpinBox(w.tab_28)
    w.IrIS_cal_Sour_02.setObjectName(u"IrIS_cal_Sour_02")
    w.IrIS_cal_Sour_02.setMinimum(-999999.000000000000000)
    w.IrIS_cal_Sour_02.setMaximum(9999999.000000000000000)
    w.IrIS_cal_Sour_02.setValue(217.500000000000000)

    w.gridLayout_27.addWidget(w.IrIS_cal_Sour_02, 5, 2, 1, 1)

    w.IrIS_cal_Sour_03 = QDoubleSpinBox(w.tab_28)
    w.IrIS_cal_Sour_03.setObjectName(u"IrIS_cal_Sour_03")
    w.IrIS_cal_Sour_03.setMinimum(-999999.000000000000000)
    w.IrIS_cal_Sour_03.setMaximum(9999999.000000000000000)
    w.IrIS_cal_Sour_03.setValue(370.000000000000000)

    w.gridLayout_27.addWidget(w.IrIS_cal_Sour_03, 5, 3, 1, 1)

    w.lineEdit_40 = QLineEdit(w.tab_28)
    w.lineEdit_40.setObjectName(u"lineEdit_40")
    w.lineEdit_40.setEnabled(False)

    w.gridLayout_27.addWidget(w.lineEdit_40, 4, 4, 1, 2)

    w.IrIS_cal_Ref_MK_ID = QSpinBox(w.tab_28)
    w.IrIS_cal_Ref_MK_ID.setObjectName(u"IrIS_cal_Ref_MK_ID")
    w.IrIS_cal_Ref_MK_ID.setValue(0)

    w.gridLayout_27.addWidget(w.IrIS_cal_Ref_MK_ID, 4, 6, 1, 1)

    w.IrIS_Cal_plot_deg = QCheckBox(w.tab_28)
    w.IrIS_Cal_plot_deg.setObjectName(u"IrIS_Cal_plot_deg")

    w.gridLayout_27.addWidget(w.IrIS_Cal_plot_deg, 5, 4, 1, 1)

    w.IrIS_Cal_plot_mm = QCheckBox(w.tab_28)
    w.IrIS_Cal_plot_mm.setObjectName(u"IrIS_Cal_plot_mm")
    w.IrIS_Cal_plot_mm.setChecked(True)

    w.gridLayout_27.addWidget(w.IrIS_Cal_plot_mm, 5, 5, 1, 1)

    w.IrIS_cal_plot = QPushButton(w.tab_28)
    w.IrIS_cal_plot.setObjectName(u"IrIS_cal_plot")

    w.gridLayout_27.addWidget(w.IrIS_cal_plot, 5, 6, 1, 1)

    w.line_22 = QFrame(w.tab_28)
    w.line_22.setObjectName(u"line_22")
    w.line_22.setFrameShape(QFrame.Shape.HLine)
    w.line_22.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_27.addWidget(w.line_22, 6, 0, 1, 7)

    w.IrIS_cal_save = QPushButton(w.tab_28)
    w.IrIS_cal_save.setObjectName(u"IrIS_cal_save")

    w.gridLayout_27.addWidget(w.IrIS_cal_save, 7, 6, 1, 1)

    w.IrIS_cal_export = QPushButton(w.tab_28)
    w.IrIS_cal_export.setObjectName(u"IrIS_cal_export")

    w.gridLayout_27.addWidget(w.IrIS_cal_export, 7, 5, 1, 1)

    w.IrIS_cal_findMK = QPushButton(w.tab_28)
    w.IrIS_cal_findMK.setObjectName(u"IrIS_cal_findMK")

    w.gridLayout_27.addWidget(w.IrIS_cal_findMK, 7, 0, 1, 1)

    w.ref_frame_cal_IrIS = QSpinBox(w.tab_28)
    w.ref_frame_cal_IrIS.setObjectName(u"ref_frame_cal_IrIS")

    w.gridLayout_27.addWidget(w.ref_frame_cal_IrIS, 7, 2, 1, 1)

    w.lineEdit_11 = QLineEdit(w.tab_28)
    w.lineEdit_11.setObjectName(u"lineEdit_11")
    w.lineEdit_11.setEnabled(False)

    w.gridLayout_27.addWidget(w.lineEdit_11, 7, 3, 1, 1)

    w.tabWidget_7.addTab(w.tab_28, "")
    w.tab_29 = QWidget()
    w.tab_29.setObjectName(u"tab_29")
    w.tabWidget_7.addTab(w.tab_29, "")

    w.gridLayout_11.addWidget(w.tabWidget_7, 4, 0, 1, 3)

    w.tabWidget_5.addTab(w.tab_15, "")
    w.tab_16 = QWidget()
    w.tab_16.setObjectName(u"tab_16")
    w.gridLayout_18 = QGridLayout(w.tab_16)
    w.gridLayout_18.setObjectName(u"gridLayout_18")
    w.groupBox_4 = QGroupBox(w.tab_16)
    w.groupBox_4.setObjectName(u"groupBox_4")
    w.gridLayout_20 = QGridLayout(w.groupBox_4)
    w.gridLayout_20.setObjectName(u"gridLayout_20")
    w.tabWidget = QTabWidget(w.groupBox_4)
    w.tabWidget.setObjectName(u"tabWidget")
    w.tab_20 = QWidget()
    w.tab_20.setObjectName(u"tab_20")
    w.gridLayout_22 = QGridLayout(w.tab_20)
    w.gridLayout_22.setObjectName(u"gridLayout_22")
    w.pushButton_13 = QPushButton(w.tab_20)
    w.pushButton_13.setObjectName(u"pushButton_13")

    w.gridLayout_22.addWidget(w.pushButton_13, 5, 2, 1, 1)

    w.groupBox_7 = QGroupBox(w.tab_20)
    w.groupBox_7.setObjectName(u"groupBox_7")
    w.gridLayout_23 = QGridLayout(w.groupBox_7)
    w.gridLayout_23.setObjectName(u"gridLayout_23")
    w.IrISPlot03 = QComboBox(w.groupBox_7)
    w.IrISPlot03.setObjectName(u"IrISPlot03")

    w.gridLayout_23.addWidget(w.IrISPlot03, 5, 0, 1, 2)

    w.lineEdit_38 = QLineEdit(w.groupBox_7)
    w.lineEdit_38.setObjectName(u"lineEdit_38")

    w.gridLayout_23.addWidget(w.lineEdit_38, 0, 0, 1, 1)

    w.DownSizeN_IrIS = QSpinBox(w.groupBox_7)
    w.DownSizeN_IrIS.setObjectName(u"DownSizeN_IrIS")
    w.DownSizeN_IrIS.setValue(16)

    w.gridLayout_23.addWidget(w.DownSizeN_IrIS, 0, 3, 1, 1)

    w.IrISPlot01 = QComboBox(w.groupBox_7)
    w.IrISPlot01.setObjectName(u"IrISPlot01")
    w.IrISPlot01.setAcceptDrops(False)

    w.gridLayout_23.addWidget(w.IrISPlot01, 2, 0, 1, 2)

    w.IrIS_grad_frame = QSpinBox(w.groupBox_7)
    w.IrIS_grad_frame.setObjectName(u"IrIS_grad_frame")
    w.IrIS_grad_frame.setMinimum(1)

    w.gridLayout_23.addWidget(w.IrIS_grad_frame, 0, 1, 1, 1)

    w.IrIS_ProcessPlot = QPushButton(w.groupBox_7)
    w.IrIS_ProcessPlot.setObjectName(u"IrIS_ProcessPlot")

    w.gridLayout_23.addWidget(w.IrIS_ProcessPlot, 5, 3, 1, 1)

    w.IrISPlot02 = QComboBox(w.groupBox_7)
    w.IrISPlot02.setObjectName(u"IrISPlot02")

    w.gridLayout_23.addWidget(w.IrISPlot02, 2, 2, 1, 2)

    w.line_17 = QFrame(w.groupBox_7)
    w.line_17.setObjectName(u"line_17")
    w.line_17.setFrameShape(QFrame.Shape.HLine)
    w.line_17.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_23.addWidget(w.line_17, 1, 0, 1, 1)

    w.lineEdit_25 = QLineEdit(w.groupBox_7)
    w.lineEdit_25.setObjectName(u"lineEdit_25")

    w.gridLayout_23.addWidget(w.lineEdit_25, 0, 2, 1, 1)

    w.IrIS_Plot = QPushButton(w.groupBox_7)
    w.IrIS_Plot.setObjectName(u"IrIS_Plot")

    w.gridLayout_23.addWidget(w.IrIS_Plot, 5, 2, 1, 1)


    w.gridLayout_22.addWidget(w.groupBox_7, 1, 0, 1, 5)

    w.IrIS_findPK = QPushButton(w.tab_20)
    w.IrIS_findPK.setObjectName(u"IrIS_findPK")

    w.gridLayout_22.addWidget(w.IrIS_findPK, 5, 0, 1, 1)

    w.line_14 = QFrame(w.tab_20)
    w.line_14.setObjectName(u"line_14")
    w.line_14.setFrameShape(QFrame.Shape.HLine)
    w.line_14.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_22.addWidget(w.line_14, 0, 0, 1, 1)

    w.horizontalSpacer_20 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_22.addItem(w.horizontalSpacer_20, 5, 1, 1, 1)

    w.Average = QGroupBox(w.tab_20)
    w.Average.setObjectName(u"Average")
    w.gridLayout_24 = QGridLayout(w.Average)
    w.gridLayout_24.setObjectName(u"gridLayout_24")
    w.IrIsAVg_dw = QPushButton(w.Average)
    w.IrIsAVg_dw.setObjectName(u"IrIsAVg_dw")

    w.gridLayout_24.addWidget(w.IrIsAVg_dw, 0, 6, 1, 1)

    w.lineEdit_10 = QLineEdit(w.Average)
    w.lineEdit_10.setObjectName(u"lineEdit_10")
    w.lineEdit_10.setEnabled(False)

    w.gridLayout_24.addWidget(w.lineEdit_10, 0, 1, 1, 4)

    w.IrIsAVg_dw_margin = QSpinBox(w.Average)
    w.IrIsAVg_dw_margin.setObjectName(u"IrIsAVg_dw_margin")

    w.gridLayout_24.addWidget(w.IrIsAVg_dw_margin, 0, 5, 1, 1)


    w.gridLayout_22.addWidget(w.Average, 2, 0, 1, 5)

    w.checkBox_IrIS_time_rel = QCheckBox(w.tab_20)
    w.checkBox_IrIS_time_rel.setObjectName(u"checkBox_IrIS_time_rel")
    w.checkBox_IrIS_time_rel.setChecked(True)

    w.gridLayout_22.addWidget(w.checkBox_IrIS_time_rel, 4, 0, 1, 1)

    w.groupBox_6 = QGroupBox(w.tab_20)
    w.groupBox_6.setObjectName(u"groupBox_6")
    w.gridLayout_25 = QGridLayout(w.groupBox_6)
    w.gridLayout_25.setObjectName(u"gridLayout_25")
    w.avg_frames_within_dwell_N = QSpinBox(w.groupBox_6)
    w.avg_frames_within_dwell_N.setObjectName(u"avg_frames_within_dwell_N")
    w.avg_frames_within_dwell_N.setValue(2)

    w.gridLayout_25.addWidget(w.avg_frames_within_dwell_N, 1, 2, 1, 1)

    w.IrIsAVg_Framesdw = QPushButton(w.groupBox_6)
    w.IrIsAVg_Framesdw.setObjectName(u"IrIsAVg_Framesdw")

    w.gridLayout_25.addWidget(w.IrIsAVg_Framesdw, 1, 3, 1, 1)

    w.lineEdit_12 = QLineEdit(w.groupBox_6)
    w.lineEdit_12.setObjectName(u"lineEdit_12")
    w.lineEdit_12.setEnabled(False)

    w.gridLayout_25.addWidget(w.lineEdit_12, 1, 0, 1, 1)


    w.gridLayout_22.addWidget(w.groupBox_6, 3, 0, 1, 5)

    w.IrIS_ExportCSV = QPushButton(w.tab_20)
    w.IrIS_ExportCSV.setObjectName(u"IrIS_ExportCSV")

    w.gridLayout_22.addWidget(w.IrIS_ExportCSV, 5, 4, 1, 1)

    w.tabWidget.addTab(w.tab_20, "")
    w.tab_21 = QWidget()
    w.tab_21.setObjectName(u"tab_21")
    w.gridLayout_21 = QGridLayout(w.tab_21)
    w.gridLayout_21.setObjectName(u"gridLayout_21")
    w.remove_dw_table = QPushButton(w.tab_21)
    w.remove_dw_table.setObjectName(u"remove_dw_table")

    w.gridLayout_21.addWidget(w.remove_dw_table, 1, 1, 1, 1)

    w.add_dw_table = QPushButton(w.tab_21)
    w.add_dw_table.setObjectName(u"add_dw_table")

    w.gridLayout_21.addWidget(w.add_dw_table, 1, 0, 1, 1)

    w.dw_table_pos = QSpinBox(w.tab_21)
    w.dw_table_pos.setObjectName(u"dw_table_pos")
    w.dw_table_pos.setMinimum(1)
    w.dw_table_pos.setMaximum(9999)
    w.dw_table_pos.setValue(1)

    w.gridLayout_21.addWidget(w.dw_table_pos, 1, 2, 1, 1)

    w.Dwells_table = QTableWidget(w.tab_21)
    w.Dwells_table.setObjectName(u"Dwells_table")

    w.gridLayout_21.addWidget(w.Dwells_table, 0, 0, 1, 3)

    w.tabWidget.addTab(w.tab_21, "")
    w.tab_22 = QWidget()
    w.tab_22.setObjectName(u"tab_22")
    w.gridLayout_26 = QGridLayout(w.tab_22)
    w.gridLayout_26.setObjectName(u"gridLayout_26")
    w.lineEdit_34 = QLineEdit(w.tab_22)
    w.lineEdit_34.setObjectName(u"lineEdit_34")
    w.lineEdit_34.setEnabled(False)
    w.lineEdit_34.setFont(font)

    w.gridLayout_26.addWidget(w.lineEdit_34, 14, 0, 1, 1)

    w.Pk_find_13 = QSpinBox(w.tab_22)
    w.Pk_find_13.setObjectName(u"Pk_find_13")

    w.gridLayout_26.addWidget(w.Pk_find_13, 14, 1, 1, 1)

    w.lineEdit_27 = QLineEdit(w.tab_22)
    w.lineEdit_27.setObjectName(u"lineEdit_27")
    w.lineEdit_27.setEnabled(False)
    w.lineEdit_27.setFont(font)

    w.gridLayout_26.addWidget(w.lineEdit_27, 2, 2, 1, 1)

    w.Pk_find_01 = QDoubleSpinBox(w.tab_22)
    w.Pk_find_01.setObjectName(u"Pk_find_01")
    w.Pk_find_01.setMinimum(-99999999.000000000000000)
    w.Pk_find_01.setMaximum(999999999.000000000000000)
    w.Pk_find_01.setValue(2.500000000000000)

    w.gridLayout_26.addWidget(w.Pk_find_01, 2, 1, 1, 1)

    w.lineEdit_33 = QLineEdit(w.tab_22)
    w.lineEdit_33.setObjectName(u"lineEdit_33")
    w.lineEdit_33.setEnabled(False)
    w.lineEdit_33.setFont(font)

    w.gridLayout_26.addWidget(w.lineEdit_33, 8, 2, 1, 1)

    w.Pk_find_06 = QDoubleSpinBox(w.tab_22)
    w.Pk_find_06.setObjectName(u"Pk_find_06")
    w.Pk_find_06.setMinimum(-99999999.000000000000000)
    w.Pk_find_06.setMaximum(999999999.000000000000000)
    w.Pk_find_06.setValue(-1.000000000000000)

    w.gridLayout_26.addWidget(w.Pk_find_06, 6, 3, 1, 1)

    w.lineEdit_30 = QLineEdit(w.tab_22)
    w.lineEdit_30.setObjectName(u"lineEdit_30")
    w.lineEdit_30.setEnabled(False)
    w.lineEdit_30.setFont(font)

    w.gridLayout_26.addWidget(w.lineEdit_30, 8, 0, 1, 1)

    w.line_16 = QFrame(w.tab_22)
    w.line_16.setObjectName(u"line_16")
    w.line_16.setFrameShape(QFrame.Shape.HLine)
    w.line_16.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_26.addWidget(w.line_16, 10, 0, 1, 2)

    w.Pk_find_05 = QDoubleSpinBox(w.tab_22)
    w.Pk_find_05.setObjectName(u"Pk_find_05")
    w.Pk_find_05.setMinimum(-99999999.000000000000000)
    w.Pk_find_05.setMaximum(999999999.000000000000000)
    w.Pk_find_05.setValue(1.000000000000000)

    w.gridLayout_26.addWidget(w.Pk_find_05, 6, 1, 1, 1)

    w.Pk_find_07 = QDoubleSpinBox(w.tab_22)
    w.Pk_find_07.setObjectName(u"Pk_find_07")
    w.Pk_find_07.setMinimum(-99999999.000000000000000)
    w.Pk_find_07.setMaximum(999999999.000000000000000)
    w.Pk_find_07.setValue(1.000000000000000)

    w.gridLayout_26.addWidget(w.Pk_find_07, 8, 1, 1, 1)

    w.Pk_find_03 = QDoubleSpinBox(w.tab_22)
    w.Pk_find_03.setObjectName(u"Pk_find_03")
    w.Pk_find_03.setMinimum(-99999999.000000000000000)
    w.Pk_find_03.setMaximum(999999999.000000000000000)
    w.Pk_find_03.setValue(1.000000000000000)

    w.gridLayout_26.addWidget(w.Pk_find_03, 4, 1, 1, 1)

    w.lineEdit_29 = QLineEdit(w.tab_22)
    w.lineEdit_29.setObjectName(u"lineEdit_29")
    w.lineEdit_29.setEnabled(False)
    w.lineEdit_29.setFont(font)

    w.gridLayout_26.addWidget(w.lineEdit_29, 4, 2, 1, 1)

    w.lineEdit_26 = QLineEdit(w.tab_22)
    w.lineEdit_26.setObjectName(u"lineEdit_26")
    w.lineEdit_26.setEnabled(False)
    w.lineEdit_26.setFont(font)

    w.gridLayout_26.addWidget(w.lineEdit_26, 2, 0, 1, 1)

    w.lineEdit_35 = QLineEdit(w.tab_22)
    w.lineEdit_35.setObjectName(u"lineEdit_35")
    w.lineEdit_35.setEnabled(False)
    w.lineEdit_35.setFont(font)

    w.gridLayout_26.addWidget(w.lineEdit_35, 14, 2, 1, 1)

    w.Pk_find_04 = QDoubleSpinBox(w.tab_22)
    w.Pk_find_04.setObjectName(u"Pk_find_04")
    w.Pk_find_04.setMinimum(-99999999.000000000000000)
    w.Pk_find_04.setMaximum(999999999.000000000000000)
    w.Pk_find_04.setValue(1.000000000000000)

    w.gridLayout_26.addWidget(w.Pk_find_04, 4, 3, 1, 1)

    w.line_15 = QFrame(w.tab_22)
    w.line_15.setObjectName(u"line_15")
    w.line_15.setFrameShape(QFrame.Shape.HLine)
    w.line_15.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_26.addWidget(w.line_15, 1, 0, 1, 1)

    w.checkBox_Pk_find_range = QCheckBox(w.tab_22)
    w.checkBox_Pk_find_range.setObjectName(u"checkBox_Pk_find_range")
    w.checkBox_Pk_find_range.setChecked(True)

    w.gridLayout_26.addWidget(w.checkBox_Pk_find_range, 12, 0, 1, 1)

    w.lineEdit_36 = QLineEdit(w.tab_22)
    w.lineEdit_36.setObjectName(u"lineEdit_36")
    w.lineEdit_36.setEnabled(False)
    w.lineEdit_36.setFont(font)
    w.lineEdit_36.setAlignment(Qt.AlignmentFlag.AlignCenter)

    w.gridLayout_26.addWidget(w.lineEdit_36, 0, 0, 1, 4)

    w.lineEdit_32 = QLineEdit(w.tab_22)
    w.lineEdit_32.setObjectName(u"lineEdit_32")
    w.lineEdit_32.setEnabled(False)
    w.lineEdit_32.setFont(font)

    w.gridLayout_26.addWidget(w.lineEdit_32, 6, 2, 1, 1)

    w.Pk_find_09 = QDoubleSpinBox(w.tab_22)
    w.Pk_find_09.setObjectName(u"Pk_find_09")
    w.Pk_find_09.setValue(0.800000000000000)

    w.gridLayout_26.addWidget(w.Pk_find_09, 12, 1, 1, 1)

    w.lineEdit_31 = QLineEdit(w.tab_22)
    w.lineEdit_31.setObjectName(u"lineEdit_31")
    w.lineEdit_31.setEnabled(False)
    w.lineEdit_31.setFont(font)

    w.gridLayout_26.addWidget(w.lineEdit_31, 6, 0, 1, 1)

    w.lineEdit_28 = QLineEdit(w.tab_22)
    w.lineEdit_28.setObjectName(u"lineEdit_28")
    w.lineEdit_28.setEnabled(False)
    w.lineEdit_28.setFont(font)

    w.gridLayout_26.addWidget(w.lineEdit_28, 4, 0, 1, 1)

    w.Pk_find_08 = QDoubleSpinBox(w.tab_22)
    w.Pk_find_08.setObjectName(u"Pk_find_08")
    w.Pk_find_08.setMinimum(-99999999.000000000000000)
    w.Pk_find_08.setMaximum(999999999.000000000000000)
    w.Pk_find_08.setValue(1.000000000000000)

    w.gridLayout_26.addWidget(w.Pk_find_08, 8, 3, 1, 1)

    w.lineEdit_37 = QLineEdit(w.tab_22)
    w.lineEdit_37.setObjectName(u"lineEdit_37")
    w.lineEdit_37.setEnabled(False)
    w.lineEdit_37.setFont(font)
    w.lineEdit_37.setAlignment(Qt.AlignmentFlag.AlignCenter)

    w.gridLayout_26.addWidget(w.lineEdit_37, 11, 0, 1, 4)

    w.Pk_find_02 = QDoubleSpinBox(w.tab_22)
    w.Pk_find_02.setObjectName(u"Pk_find_02")
    w.Pk_find_02.setMinimum(-99999999.000000000000000)
    w.Pk_find_02.setMaximum(999999999.000000000000000)
    w.Pk_find_02.setValue(-1.000000000000000)

    w.gridLayout_26.addWidget(w.Pk_find_02, 2, 3, 1, 1)

    w.Pk_Plot = QPushButton(w.tab_22)
    w.Pk_Plot.setObjectName(u"Pk_Plot")

    w.gridLayout_26.addWidget(w.Pk_Plot, 15, 3, 1, 1)

    w.Pk_find_14 = QSpinBox(w.tab_22)
    w.Pk_find_14.setObjectName(u"Pk_find_14")

    w.gridLayout_26.addWidget(w.Pk_find_14, 14, 3, 1, 1)

    w.Pk_find_10 = QDoubleSpinBox(w.tab_22)
    w.Pk_find_10.setObjectName(u"Pk_find_10")
    w.Pk_find_10.setValue(1.200000000000000)

    w.gridLayout_26.addWidget(w.Pk_find_10, 13, 1, 1, 1)

    w.checkBox_Pk_find_adj_1st_last = QCheckBox(w.tab_22)
    w.checkBox_Pk_find_adj_1st_last.setObjectName(u"checkBox_Pk_find_adj_1st_last")
    w.checkBox_Pk_find_adj_1st_last.setChecked(True)

    w.gridLayout_26.addWidget(w.checkBox_Pk_find_adj_1st_last, 12, 2, 1, 1)

    w.Pk_find_11 = QSpinBox(w.tab_22)
    w.Pk_find_11.setObjectName(u"Pk_find_11")
    w.Pk_find_11.setMaximum(99999)
    w.Pk_find_11.setValue(20)

    w.gridLayout_26.addWidget(w.Pk_find_11, 12, 3, 1, 1)

    w.Pk_find_12 = QDoubleSpinBox(w.tab_22)
    w.Pk_find_12.setObjectName(u"Pk_find_12")
    w.Pk_find_12.setValue(0.100000000000000)

    w.gridLayout_26.addWidget(w.Pk_find_12, 13, 3, 1, 1)

    w.tabWidget.addTab(w.tab_22, "")
    w.tab_26 = QWidget()
    w.tab_26.setObjectName(u"tab_26")
    w.gridLayout_28 = QGridLayout(w.tab_26)
    w.gridLayout_28.setObjectName(u"gridLayout_28")
    w.Source_save_cal = QPushButton(w.tab_26)
    w.Source_save_cal.setObjectName(u"Source_save_cal")

    w.gridLayout_28.addWidget(w.Source_save_cal, 1, 1, 1, 1)

    w.horizontalSpacer_23 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_28.addItem(w.horizontalSpacer_23, 1, 0, 1, 1)

    w.Source_Cal_table = QTableWidget(w.tab_26)
    w.Source_Cal_table.setObjectName(u"Source_Cal_table")

    w.gridLayout_28.addWidget(w.Source_Cal_table, 0, 0, 1, 2)

    w.tabWidget.addTab(w.tab_26, "")

    w.gridLayout_20.addWidget(w.tabWidget, 0, 0, 1, 7)

    w.Pk_find_channel = QSpinBox(w.groupBox_4)
    w.Pk_find_channel.setObjectName(u"Pk_find_channel")
    w.Pk_find_channel.setMinimum(1)
    w.Pk_find_channel.setMaximum(9999)
    w.Pk_find_channel.setValue(1)

    w.gridLayout_20.addWidget(w.Pk_find_channel, 1, 6, 1, 1)

    w.horizontalSpacer_22 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_20.addItem(w.horizontalSpacer_22, 1, 1, 1, 1)

    w.IrIsAVg_loadSSD_check = QCheckBox(w.groupBox_4)
    w.IrIsAVg_loadSSD_check.setObjectName(u"IrIsAVg_loadSSD_check")

    w.gridLayout_20.addWidget(w.IrIsAVg_loadSSD_check, 1, 0, 1, 1)

    w.lineEdit_9 = QLineEdit(w.groupBox_4)
    w.lineEdit_9.setObjectName(u"lineEdit_9")
    w.lineEdit_9.setEnabled(False)
    w.lineEdit_9.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

    w.gridLayout_20.addWidget(w.lineEdit_9, 1, 4, 1, 1)

    w.Pk_find_processl_all_check = QCheckBox(w.groupBox_4)
    w.Pk_find_processl_all_check.setObjectName(u"Pk_find_processl_all_check")
    w.Pk_find_processl_all_check.setChecked(True)

    w.gridLayout_20.addWidget(w.Pk_find_processl_all_check, 1, 3, 1, 1)


    w.gridLayout_18.addWidget(w.groupBox_4, 2, 0, 1, 1)

    w.horizontalSpacer_17 = QSpacerItem(30, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_18.addItem(w.horizontalSpacer_17, 3, 0, 1, 1)

    w.horizontalSpacer_18 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_18.addItem(w.horizontalSpacer_18, 3, 2, 1, 1)

    w.groupBox_3 = QGroupBox(w.tab_16)
    w.groupBox_3.setObjectName(u"groupBox_3")
    w.gridLayout_19 = QGridLayout(w.groupBox_3)
    w.gridLayout_19.setObjectName(u"gridLayout_19")
    w.Slider_Eval_IrIS = QSlider(w.groupBox_3)
    w.Slider_Eval_IrIS.setObjectName(u"Slider_Eval_IrIS")
    w.Slider_Eval_IrIS.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_19.addWidget(w.Slider_Eval_IrIS, 1, 0, 1, 1)

    w.IrIS_Ax_Eval_01 = QWidget(w.groupBox_3)
    w.IrIS_Ax_Eval_01.setObjectName(u"IrIS_Ax_Eval_01")

    w.gridLayout_19.addWidget(w.IrIS_Ax_Eval_01, 0, 0, 1, 2)

    w.List_Eval_Direction = QComboBox(w.groupBox_3)
    w.List_Eval_Direction.setObjectName(u"List_Eval_Direction")

    w.gridLayout_19.addWidget(w.List_Eval_Direction, 1, 1, 1, 1)

    w.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_19.addItem(w.verticalSpacer, 1, 2, 1, 1)


    w.gridLayout_18.addWidget(w.groupBox_3, 0, 0, 1, 1)

    w.groupBox_5 = QGroupBox(w.tab_16)
    w.groupBox_5.setObjectName(u"groupBox_5")
    w.verticalLayout_2 = QVBoxLayout(w.groupBox_5)
    w.verticalLayout_2.setObjectName(u"verticalLayout_2")
    w.IrIS_Ax_Eval_02 = QWidget(w.groupBox_5)
    w.IrIS_Ax_Eval_02.setObjectName(u"IrIS_Ax_Eval_02")

    w.verticalLayout_2.addWidget(w.IrIS_Ax_Eval_02)

    w.IrIS_Ax_Eval_03 = QWidget(w.groupBox_5)
    w.IrIS_Ax_Eval_03.setObjectName(u"IrIS_Ax_Eval_03")

    w.verticalLayout_2.addWidget(w.IrIS_Ax_Eval_03)

    w.IrIS_Ax_Eval_04 = QWidget(w.groupBox_5)
    w.IrIS_Ax_Eval_04.setObjectName(u"IrIS_Ax_Eval_04")

    w.verticalLayout_2.addWidget(w.IrIS_Ax_Eval_04)


    w.gridLayout_18.addWidget(w.groupBox_5, 0, 1, 3, 2)

    w.line_13 = QFrame(w.tab_16)
    w.line_13.setObjectName(u"line_13")
    w.line_13.setFrameShape(QFrame.Shape.HLine)
    w.line_13.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_18.addWidget(w.line_13, 1, 0, 1, 1)

    w.horizontalSpacer_19 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_18.addItem(w.horizontalSpacer_19, 3, 1, 1, 1)

    w.tabWidget_5.addTab(w.tab_16, "")
    w.tab_25 = QWidget()
    w.tab_25.setObjectName(u"tab_25")
    w.tabWidget_5.addTab(w.tab_25, "")

    w.gridLayout_10.addWidget(w.tabWidget_5, 0, 1, 1, 1)

