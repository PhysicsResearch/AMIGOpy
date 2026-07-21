# -*- coding: utf-8 -*-
"""
tab_breathing_curves.py - AMIGOpy GUI Module
===============================================

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


def create_tab_breathing_curves(w):
    """
    Create the Breathing Curves module tab (tab_BrCv).

    Creates the respiratory motion analysis interface:
    - tabWidget_BrCv with sub-tabs:
      * Import & Create: curve file import and creation
      * Edit & Export: curve editing, operations, and export
      * Analyze & Visualize: statistical analysis and plotting
      * Phantom Operation: Duet control and MoVe phantom controls

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
    w.tab_BrCv = QWidget()
    w.tab_BrCv.setObjectName(u"tab_BrCv")
    w.gridLayout_BrCv = QGridLayout(w.tab_BrCv)
    w.gridLayout_BrCv.setObjectName(u"gridLayout_BrCv")
    w.tabWidget_BrCv = QTabWidget(w.tab_BrCv)
    w.tabWidget_BrCv.setObjectName(u"tabWidget_BrCv")
    w.tab_import = QWidget()
    w.tab_import.setObjectName(u"tab_import")
    w.gridLayout_BrCv_1 = QGridLayout(w.tab_import)
    w.gridLayout_BrCv_1.setObjectName(u"gridLayout_BrCv_1")
    w.groupBox_BrCv_importCSV = QGroupBox(w.tab_import)
    w.groupBox_BrCv_importCSV.setObjectName(u"groupBox_BrCv_importCSV")
    w.gridLayout_BrCv_3 = QGridLayout(w.groupBox_BrCv_importCSV)
    w.gridLayout_BrCv_3.setObjectName(u"gridLayout_BrCv_3")
    w.lineEdit_BrCv_5 = QLineEdit(w.groupBox_BrCv_importCSV)
    w.lineEdit_BrCv_5.setObjectName(u"lineEdit_BrCv_5")
    w.lineEdit_BrCv_5.setEnabled(False)

    w.gridLayout_BrCv_3.addWidget(w.lineEdit_BrCv_5, 0, 0, 1, 1)

    w.selDelimCSV_BrCv = QComboBox(w.groupBox_BrCv_importCSV)
    w.selDelimCSV_BrCv.setObjectName(u"selDelimCSV_BrCv")

    w.gridLayout_BrCv_3.addWidget(w.selDelimCSV_BrCv, 0, 1, 1, 1)

    w.lineHeadCSV_BrCv = QSpinBox(w.groupBox_BrCv_importCSV)
    w.lineHeadCSV_BrCv.setObjectName(u"lineHeadCSV_BrCv")
    w.lineHeadCSV_BrCv.setValue(4)

    w.gridLayout_BrCv_3.addWidget(w.lineHeadCSV_BrCv, 1, 1, 1, 1)

    w.lineSkipCSV_BrCv = QSpinBox(w.groupBox_BrCv_importCSV)
    w.lineSkipCSV_BrCv.setObjectName(u"lineSkipCSV_BrCv")
    w.lineSkipCSV_BrCv.setValue(10)

    w.gridLayout_BrCv_3.addWidget(w.lineSkipCSV_BrCv, 2, 1, 1, 1)

    w.lineEdit_BrCv_6 = QLineEdit(w.groupBox_BrCv_importCSV)
    w.lineEdit_BrCv_6.setObjectName(u"lineEdit_BrCv_6")
    w.lineEdit_BrCv_6.setEnabled(False)

    w.gridLayout_BrCv_3.addWidget(w.lineEdit_BrCv_6, 2, 0, 1, 1)

    w.verticalSpacer_BrCv_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_BrCv_3.addItem(w.verticalSpacer_BrCv_2, 6, 1, 1, 1)

    w.lineEdit_BrCv_7 = QLineEdit(w.groupBox_BrCv_importCSV)
    w.lineEdit_BrCv_7.setObjectName(u"lineEdit_BrCv_7")
    w.lineEdit_BrCv_7.setEnabled(False)

    w.gridLayout_BrCv_3.addWidget(w.lineEdit_BrCv_7, 1, 0, 1, 1)

    w.flipCSV_BrCv = QCheckBox(w.groupBox_BrCv_importCSV)
    w.flipCSV_BrCv.setObjectName(u"flipCSV_BrCv")
    w.flipCSV_BrCv.setEnabled(True)
    w.flipCSV_BrCv.setChecked(True)

    w.gridLayout_BrCv_3.addWidget(w.flipCSV_BrCv, 4, 1, 1, 1)

    w.loadCSVView_BrCv = QPushButton(w.groupBox_BrCv_importCSV)
    w.loadCSVView_BrCv.setObjectName(u"loadCSVView_BrCv")

    w.gridLayout_BrCv_3.addWidget(w.loadCSVView_BrCv, 5, 1, 1, 1)

    w.lineEdit_BrCv_8 = QLineEdit(w.groupBox_BrCv_importCSV)
    w.lineEdit_BrCv_8.setObjectName(u"lineEdit_BrCv_8")
    w.lineEdit_BrCv_8.setEnabled(False)

    w.gridLayout_BrCv_3.addWidget(w.lineEdit_BrCv_8, 3, 0, 1, 1)

    w.timeUnitCSV_BrCv = QComboBox(w.groupBox_BrCv_importCSV)
    w.timeUnitCSV_BrCv.setObjectName(u"timeUnitCSV_BrCv")

    w.gridLayout_BrCv_3.addWidget(w.timeUnitCSV_BrCv, 3, 1, 1, 1)

    w.gridLayout_BrCv_3.setColumnStretch(0, 2)
    w.gridLayout_BrCv_3.setColumnStretch(1, 1)

    w.gridLayout_BrCv_1.addWidget(w.groupBox_BrCv_importCSV, 2, 0, 1, 1)

    w.groupBox_BrCv_createCurve = QGroupBox(w.tab_import)
    w.groupBox_BrCv_createCurve.setObjectName(u"groupBox_BrCv_createCurve")
    w.gridLayout_BrCv_2 = QGridLayout(w.groupBox_BrCv_createCurve)
    w.gridLayout_BrCv_2.setObjectName(u"gridLayout_BrCv_2")
    w.cvType = QComboBox(w.groupBox_BrCv_createCurve)
    w.cvType.setObjectName(u"cvType")

    w.gridLayout_BrCv_2.addWidget(w.cvType, 0, 1, 1, 1)

    w.lineEdit_BrCv_1 = QLineEdit(w.groupBox_BrCv_createCurve)
    w.lineEdit_BrCv_1.setObjectName(u"lineEdit_BrCv_1")
    w.lineEdit_BrCv_1.setEnabled(False)

    w.gridLayout_BrCv_2.addWidget(w.lineEdit_BrCv_1, 1, 0, 1, 1)

    w.createCvAmpl = QDoubleSpinBox(w.groupBox_BrCv_createCurve)
    w.createCvAmpl.setObjectName(u"createCvAmpl")
    w.createCvAmpl.setValue(15.000000000000000)

    w.gridLayout_BrCv_2.addWidget(w.createCvAmpl, 2, 1, 1, 1)

    w.createCvNumCycl = QSpinBox(w.groupBox_BrCv_createCurve)
    w.createCvNumCycl.setObjectName(u"createCvNumCycl")
    w.createCvNumCycl.setValue(10)

    w.gridLayout_BrCv_2.addWidget(w.createCvNumCycl, 1, 1, 1, 1)

    w.lineEdit_BrCv = QLineEdit(w.groupBox_BrCv_createCurve)
    w.lineEdit_BrCv.setObjectName(u"lineEdit_BrCv")
    w.lineEdit_BrCv.setEnabled(False)

    w.gridLayout_BrCv_2.addWidget(w.lineEdit_BrCv, 3, 0, 1, 1)

    w.createCvCyclTime = QDoubleSpinBox(w.groupBox_BrCv_createCurve)
    w.createCvCyclTime.setObjectName(u"createCvCyclTime")
    w.createCvCyclTime.setValue(6.000000000000000)

    w.gridLayout_BrCv_2.addWidget(w.createCvCyclTime, 3, 1, 1, 1)

    w.lineEdit_BrCv_3 = QLineEdit(w.groupBox_BrCv_createCurve)
    w.lineEdit_BrCv_3.setObjectName(u"lineEdit_BrCv_3")
    w.lineEdit_BrCv_3.setEnabled(False)

    w.gridLayout_BrCv_2.addWidget(w.lineEdit_BrCv_3, 2, 0, 1, 1)

    w.setParamsCreateCv = QPushButton(w.groupBox_BrCv_createCurve)
    w.setParamsCreateCv.setObjectName(u"setParamsCreateCv")

    w.gridLayout_BrCv_2.addWidget(w.setParamsCreateCv, 5, 1, 1, 1)

    w.createCv = QPushButton(w.groupBox_BrCv_createCurve)
    w.createCv.setObjectName(u"createCv")

    w.gridLayout_BrCv_2.addWidget(w.createCv, 7, 2, 1, 1)

    w.tableViewEditParams = QTableWidget(w.groupBox_BrCv_createCurve)
    w.tableViewEditParams.setObjectName(u"tableViewEditParams")

    w.gridLayout_BrCv_2.addWidget(w.tableViewEditParams, 0, 2, 7, 1)

    w.lineEdit_BrCv_4 = QLineEdit(w.groupBox_BrCv_createCurve)
    w.lineEdit_BrCv_4.setObjectName(u"lineEdit_BrCv_4")
    w.lineEdit_BrCv_4.setEnabled(False)

    w.gridLayout_BrCv_2.addWidget(w.lineEdit_BrCv_4, 0, 0, 1, 1)

    w.lineEdit_BrCv_2 = QLineEdit(w.groupBox_BrCv_createCurve)
    w.lineEdit_BrCv_2.setObjectName(u"lineEdit_BrCv_2")
    w.lineEdit_BrCv_2.setEnabled(False)

    w.gridLayout_BrCv_2.addWidget(w.lineEdit_BrCv_2, 4, 0, 1, 1)

    w.createCvFreq = QSpinBox(w.groupBox_BrCv_createCurve)
    w.createCvFreq.setObjectName(u"createCvFreq")
    w.createCvFreq.setValue(25)

    w.gridLayout_BrCv_2.addWidget(w.createCvFreq, 4, 1, 1, 1)

    w.verticalSpacer_BrCv = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_BrCv_2.addItem(w.verticalSpacer_BrCv, 6, 1, 2, 1)

    w.gridLayout_BrCv_2.setColumnStretch(0, 1)
    w.gridLayout_BrCv_2.setColumnStretch(1, 1)
    w.gridLayout_BrCv_2.setColumnStretch(2, 2)

    w.gridLayout_BrCv_1.addWidget(w.groupBox_BrCv_createCurve, 2, 1, 1, 1)

    w.horizontalSpacer_BrCv = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_BrCv_1.addItem(w.horizontalSpacer_BrCv, 2, 2, 1, 1)

    w.horizontalLayout_BrCv_1 = QHBoxLayout()
    w.horizontalLayout_BrCv_1.setObjectName(u"horizontalLayout_BrCv_1")
    w.tableViewCSV_BrCv = QTableWidget(w.tab_import)
    w.tableViewCSV_BrCv.setObjectName(u"tableViewCSV_BrCv")

    w.horizontalLayout_BrCv_1.addWidget(w.tableViewCSV_BrCv)

    w.textViewCSV_BrCv = QTextEdit(w.tab_import)
    w.textViewCSV_BrCv.setObjectName(u"textViewCSV_BrCv")

    w.horizontalLayout_BrCv_1.addWidget(w.textViewCSV_BrCv)

    w.horizontalLayout_BrCv_1.setStretch(0, 2)
    w.horizontalLayout_BrCv_1.setStretch(1, 1)

    w.gridLayout_BrCv_1.addLayout(w.horizontalLayout_BrCv_1, 0, 0, 1, 3)

    w.gridLayout_BrCv_1.setRowStretch(0, 2)
    w.gridLayout_BrCv_1.setRowStretch(2, 1)
    w.gridLayout_BrCv_1.setColumnStretch(0, 1)
    w.gridLayout_BrCv_1.setColumnStretch(1, 2)
    w.gridLayout_BrCv_1.setColumnStretch(2, 1)
    w.tabWidget_BrCv.addTab(w.tab_import, "")
    w.tab_BrCv_edit = QWidget()
    w.tab_BrCv_edit.setObjectName(u"tab_BrCv_edit")
    w.gridLayout_BrCv_edit = QGridLayout(w.tab_BrCv_edit)
    w.gridLayout_BrCv_edit.setObjectName(u"gridLayout_BrCv_edit")
    w.gridLayout_BrCv_6 = QGridLayout()
    w.gridLayout_BrCv_6.setObjectName(u"gridLayout_BrCv_6")
    w.breathhold_BrCv = QGroupBox(w.tab_BrCv_edit)
    w.breathhold_BrCv.setObjectName(u"breathhold_BrCv")
    w.gridLayout_BrCv_8 = QGridLayout(w.breathhold_BrCv)
    w.gridLayout_BrCv_8.setObjectName(u"gridLayout_BrCv_8")
    w.lineEdit_BrCv_30 = QLineEdit(w.breathhold_BrCv)
    w.lineEdit_BrCv_30.setObjectName(u"lineEdit_BrCv_30")
    w.lineEdit_BrCv_30.setEnabled(False)

    w.gridLayout_BrCv_8.addWidget(w.lineEdit_BrCv_30, 2, 0, 1, 1)

    w.breathholdStart = QSpinBox(w.breathhold_BrCv)
    w.breathholdStart.setObjectName(u"breathholdStart")
    w.breathholdStart.setMaximum(999999)

    w.gridLayout_BrCv_8.addWidget(w.breathholdStart, 1, 1, 1, 1)

    w.lineEdit_BrCv_29 = QLineEdit(w.breathhold_BrCv)
    w.lineEdit_BrCv_29.setObjectName(u"lineEdit_BrCv_29")
    w.lineEdit_BrCv_29.setEnabled(False)

    w.gridLayout_BrCv_8.addWidget(w.lineEdit_BrCv_29, 1, 0, 1, 1)

    w.breathholdDuration = QDoubleSpinBox(w.breathhold_BrCv)
    w.breathholdDuration.setObjectName(u"breathholdDuration")

    w.gridLayout_BrCv_8.addWidget(w.breathholdDuration, 2, 1, 1, 1)

    w.applyBreathhold = QCheckBox(w.breathhold_BrCv)
    w.applyBreathhold.setObjectName(u"applyBreathhold")

    w.gridLayout_BrCv_8.addWidget(w.applyBreathhold, 0, 0, 1, 1)

    w.gridLayout_BrCv_8.setColumnStretch(0, 2)
    w.gridLayout_BrCv_8.setColumnStretch(1, 1)

    w.gridLayout_BrCv_6.addWidget(w.breathhold_BrCv, 1, 1, 1, 2)

    w.operations_BrCv = QGroupBox(w.tab_BrCv_edit)
    w.operations_BrCv.setObjectName(u"operations_BrCv")
    w.gridLayout_BrCv_7 = QGridLayout(w.operations_BrCv)
    w.gridLayout_BrCv_7.setObjectName(u"gridLayout_BrCv_7")
    w.lineEdit_BrCv_22 = QLineEdit(w.operations_BrCv)
    w.lineEdit_BrCv_22.setObjectName(u"lineEdit_BrCv_22")
    w.lineEdit_BrCv_22.setEnabled(False)

    w.gridLayout_BrCv_7.addWidget(w.lineEdit_BrCv_22, 2, 0, 1, 1)

    w.shiftAmpl_BrCv = QDoubleSpinBox(w.operations_BrCv)
    w.shiftAmpl_BrCv.setObjectName(u"shiftAmpl_BrCv")
    w.shiftAmpl_BrCv.setMinimum(-99.000000000000000)
    w.shiftAmpl_BrCv.setMaximum(99.000000000000000)

    w.gridLayout_BrCv_7.addWidget(w.shiftAmpl_BrCv, 2, 1, 1, 1)

    w.lineEdit_BrCv_23 = QLineEdit(w.operations_BrCv)
    w.lineEdit_BrCv_23.setObjectName(u"lineEdit_BrCv_23")
    w.lineEdit_BrCv_23.setEnabled(False)

    w.gridLayout_BrCv_7.addWidget(w.lineEdit_BrCv_23, 3, 0, 1, 1)

    w.scaleFreq_BrCv = QDoubleSpinBox(w.operations_BrCv)
    w.scaleFreq_BrCv.setObjectName(u"scaleFreq_BrCv")
    w.scaleFreq_BrCv.setValue(1.000000000000000)

    w.gridLayout_BrCv_7.addWidget(w.scaleFreq_BrCv, 0, 1, 1, 1)

    w.lineEdit_BrCv_20 = QLineEdit(w.operations_BrCv)
    w.lineEdit_BrCv_20.setObjectName(u"lineEdit_BrCv_20")
    w.lineEdit_BrCv_20.setEnabled(False)

    w.gridLayout_BrCv_7.addWidget(w.lineEdit_BrCv_20, 0, 0, 1, 1)

    w.lineEdit_BrCv_21 = QLineEdit(w.operations_BrCv)
    w.lineEdit_BrCv_21.setObjectName(u"lineEdit_BrCv_21")
    w.lineEdit_BrCv_21.setEnabled(False)

    w.gridLayout_BrCv_7.addWidget(w.lineEdit_BrCv_21, 1, 0, 1, 1)

    w.maxAmplThresh_BrCv = QDoubleSpinBox(w.operations_BrCv)
    w.maxAmplThresh_BrCv.setObjectName(u"maxAmplThresh_BrCv")
    w.maxAmplThresh_BrCv.setValue(39.000000000000000)

    w.gridLayout_BrCv_7.addWidget(w.maxAmplThresh_BrCv, 3, 1, 1, 1)

    w.setMinZero_BrCv = QCheckBox(w.operations_BrCv)
    w.setMinZero_BrCv.setObjectName(u"setMinZero_BrCv")
    w.setMinZero_BrCv.setChecked(True)

    w.gridLayout_BrCv_7.addWidget(w.setMinZero_BrCv, 5, 1, 1, 1)

    w.scaleAmpl_BrCv = QDoubleSpinBox(w.operations_BrCv)
    w.scaleAmpl_BrCv.setObjectName(u"scaleAmpl_BrCv")
    w.scaleAmpl_BrCv.setValue(1.000000000000000)

    w.gridLayout_BrCv_7.addWidget(w.scaleAmpl_BrCv, 1, 1, 1, 1)

    w.gridLayout_BrCv_7.setColumnStretch(0, 2)
    w.gridLayout_BrCv_7.setColumnStretch(1, 1)

    w.gridLayout_BrCv_6.addWidget(w.operations_BrCv, 0, 1, 1, 2)

    w.applyOper_BrCv = QPushButton(w.tab_BrCv_edit)
    w.applyOper_BrCv.setObjectName(u"applyOper_BrCv")

    w.gridLayout_BrCv_6.addWidget(w.applyOper_BrCv, 3, 1, 1, 1)

    w.verticalSpacer_BrCv_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_BrCv_6.addItem(w.verticalSpacer_BrCv_4, 9, 1, 1, 2)

    w.export_BrCv = QGroupBox(w.tab_BrCv_edit)
    w.export_BrCv.setObjectName(u"export_BrCv")
    w.gridLayout_BrCv_9 = QGridLayout(w.export_BrCv)
    w.gridLayout_BrCv_9.setObjectName(u"gridLayout_BrCv_9")
    w.exportData_BrCv = QPushButton(w.export_BrCv)
    w.exportData_BrCv.setObjectName(u"exportData_BrCv")

    w.gridLayout_BrCv_9.addWidget(w.exportData_BrCv, 4, 0, 1, 1)

    w.copyCurve_BrCv = QSpinBox(w.export_BrCv)
    w.copyCurve_BrCv.setObjectName(u"copyCurve_BrCv")
    w.copyCurve_BrCv.setValue(1)

    w.gridLayout_BrCv_9.addWidget(w.copyCurve_BrCv, 2, 1, 1, 2)

    w.lineEdit_BrCv_28 = QLineEdit(w.export_BrCv)
    w.lineEdit_BrCv_28.setObjectName(u"lineEdit_BrCv_28")
    w.lineEdit_BrCv_28.setEnabled(False)

    w.gridLayout_BrCv_9.addWidget(w.lineEdit_BrCv_28, 3, 0, 1, 1)

    w.interp_BrCv = QCheckBox(w.export_BrCv)
    w.interp_BrCv.setObjectName(u"interp_BrCv")
    w.interp_BrCv.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    w.interp_BrCv.setChecked(True)

    w.gridLayout_BrCv_9.addWidget(w.interp_BrCv, 0, 0, 1, 1)

    w.exportGCODE_BrCv = QPushButton(w.export_BrCv)
    w.exportGCODE_BrCv.setObjectName(u"exportGCODE_BrCv")

    w.gridLayout_BrCv_9.addWidget(w.exportGCODE_BrCv, 4, 1, 1, 2)

    w.editExportFile_BrCv = QLineEdit(w.export_BrCv)
    w.editExportFile_BrCv.setObjectName(u"editExportFile_BrCv")

    w.gridLayout_BrCv_9.addWidget(w.editExportFile_BrCv, 3, 1, 1, 2)

    w.lineEdit_77 = QLineEdit(w.export_BrCv)
    w.lineEdit_77.setObjectName(u"lineEdit_77")
    w.lineEdit_77.setEnabled(False)
    sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    sizePolicy6.setHorizontalStretch(0)
    sizePolicy6.setVerticalStretch(0)
    sizePolicy6.setHeightForWidth(w.lineEdit_77.sizePolicy().hasHeightForWidth())
    w.lineEdit_77.setSizePolicy(sizePolicy6)

    w.gridLayout_BrCv_9.addWidget(w.lineEdit_77, 0, 2, 1, 1)

    w.interp_value_BrCv = QDoubleSpinBox(w.export_BrCv)
    w.interp_value_BrCv.setObjectName(u"interp_value_BrCv")
    w.interp_value_BrCv.setValue(10.000000000000000)

    w.gridLayout_BrCv_9.addWidget(w.interp_value_BrCv, 0, 1, 1, 1)

    w.lineEdit_BrCv_24 = QLineEdit(w.export_BrCv)
    w.lineEdit_BrCv_24.setObjectName(u"lineEdit_BrCv_24")
    w.lineEdit_BrCv_24.setEnabled(False)

    w.gridLayout_BrCv_9.addWidget(w.lineEdit_BrCv_24, 2, 0, 1, 1)

    w.lineEdit_83 = QLineEdit(w.export_BrCv)
    w.lineEdit_83.setObjectName(u"lineEdit_83")
    w.lineEdit_83.setEnabled(False)

    w.gridLayout_BrCv_9.addWidget(w.lineEdit_83, 1, 0, 1, 1)

    w.compress_speed_BrCv = QDoubleSpinBox(w.export_BrCv)
    w.compress_speed_BrCv.setObjectName(u"compress_speed_BrCv")

    w.gridLayout_BrCv_9.addWidget(w.compress_speed_BrCv, 1, 1, 1, 2)

    w.gridLayout_BrCv_9.setColumnStretch(0, 2)
    w.gridLayout_BrCv_9.setColumnStretch(1, 1)
    w.gridLayout_BrCv_9.setColumnStretch(2, 1)

    w.gridLayout_BrCv_6.addWidget(w.export_BrCv, 6, 1, 1, 2)

    w.line_BrCv = QFrame(w.tab_BrCv_edit)
    w.line_BrCv.setObjectName(u"line_BrCv")
    w.line_BrCv.setFrameShape(QFrame.Shape.HLine)
    w.line_BrCv.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_BrCv_6.addWidget(w.line_BrCv, 5, 1, 1, 2)

    w.undoOperations_BrCv = QPushButton(w.tab_BrCv_edit)
    w.undoOperations_BrCv.setObjectName(u"undoOperations_BrCv")

    w.gridLayout_BrCv_6.addWidget(w.undoOperations_BrCv, 3, 2, 1, 1)

    w.smoothing_BrCv = QGroupBox(w.tab_BrCv_edit)
    w.smoothing_BrCv.setObjectName(u"smoothing_BrCv")
    w.gridLayout_77 = QGridLayout(w.smoothing_BrCv)
    w.gridLayout_77.setObjectName(u"gridLayout_77")
    w.smooth_BrCv = QCheckBox(w.smoothing_BrCv)
    w.smooth_BrCv.setObjectName(u"smooth_BrCv")
    w.smooth_BrCv.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    w.smooth_BrCv.setChecked(True)

    w.gridLayout_77.addWidget(w.smooth_BrCv, 2, 0, 1, 1)

    w.lineEdit_79 = QLineEdit(w.smoothing_BrCv)
    w.lineEdit_79.setObjectName(u"lineEdit_79")
    w.lineEdit_79.setEnabled(False)
    sizePolicy6.setHeightForWidth(w.lineEdit_79.sizePolicy().hasHeightForWidth())
    w.lineEdit_79.setSizePolicy(sizePolicy6)

    w.gridLayout_77.addWidget(w.lineEdit_79, 4, 3, 1, 1)

    w.lineEdit_78 = QLineEdit(w.smoothing_BrCv)
    w.lineEdit_78.setObjectName(u"lineEdit_78")
    w.lineEdit_78.setEnabled(False)
    sizePolicy6.setHeightForWidth(w.lineEdit_78.sizePolicy().hasHeightForWidth())
    w.lineEdit_78.setSizePolicy(sizePolicy6)

    w.gridLayout_77.addWidget(w.lineEdit_78, 2, 3, 1, 1)

    w.threshFourierSlider = QSlider(w.smoothing_BrCv)
    w.threshFourierSlider.setObjectName(u"threshFourierSlider")
    sizePolicy7 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
    sizePolicy7.setHorizontalStretch(0)
    sizePolicy7.setVerticalStretch(0)
    sizePolicy7.setHeightForWidth(w.threshFourierSlider.sizePolicy().hasHeightForWidth())
    w.threshFourierSlider.setSizePolicy(sizePolicy7)
    w.threshFourierSlider.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_77.addWidget(w.threshFourierSlider, 6, 0, 1, 2)

    w.lineEdit_81 = QLineEdit(w.smoothing_BrCv)
    w.lineEdit_81.setObjectName(u"lineEdit_81")
    w.lineEdit_81.setEnabled(False)
    sizePolicy6.setHeightForWidth(w.lineEdit_81.sizePolicy().hasHeightForWidth())
    w.lineEdit_81.setSizePolicy(sizePolicy6)

    w.gridLayout_77.addWidget(w.lineEdit_81, 6, 3, 1, 1)

    w.threshFourierValue = QLineEdit(w.smoothing_BrCv)
    w.threshFourierValue.setObjectName(u"threshFourierValue")
    w.threshFourierValue.setEnabled(False)

    w.gridLayout_77.addWidget(w.threshFourierValue, 6, 2, 1, 1)

    w.smooth_size_BrCv = QSpinBox(w.smoothing_BrCv)
    w.smooth_size_BrCv.setObjectName(u"smooth_size_BrCv")
    w.smooth_size_BrCv.setValue(5)

    w.gridLayout_77.addWidget(w.smooth_size_BrCv, 4, 2, 1, 1)

    w.smooth_method_BrCv = QComboBox(w.smoothing_BrCv)
    w.smooth_method_BrCv.setObjectName(u"smooth_method_BrCv")

    w.gridLayout_77.addWidget(w.smooth_method_BrCv, 2, 2, 1, 1)

    w.detrend_BrCv = QCheckBox(w.smoothing_BrCv)
    w.detrend_BrCv.setObjectName(u"detrend_BrCv")
    w.detrend_BrCv.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    w.gridLayout_77.addWidget(w.detrend_BrCv, 4, 0, 1, 1)

    w.gridLayout_77.setColumnStretch(0, 1)
    w.gridLayout_77.setColumnStretch(1, 1)
    w.gridLayout_77.setColumnStretch(2, 1)

    w.gridLayout_BrCv_6.addWidget(w.smoothing_BrCv, 2, 1, 1, 2)


    w.gridLayout_BrCv_edit.addLayout(w.gridLayout_BrCv_6, 0, 0, 1, 1)

    w.gridLayout_BrCv_10 = QGridLayout()
    w.gridLayout_BrCv_10.setObjectName(u"gridLayout_BrCv_10")
    w.editXMinSlider_BrCv = QSlider(w.tab_BrCv_edit)
    w.editXMinSlider_BrCv.setObjectName(u"editXMinSlider_BrCv")
    w.editXMinSlider_BrCv.setMaximum(999999)
    w.editXMinSlider_BrCv.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_BrCv_10.addWidget(w.editXMinSlider_BrCv, 2, 1, 1, 1)

    w.lineEdit_BrCv_26 = QLineEdit(w.tab_BrCv_edit)
    w.lineEdit_BrCv_26.setObjectName(u"lineEdit_BrCv_26")
    w.lineEdit_BrCv_26.setEnabled(False)

    w.gridLayout_BrCv_10.addWidget(w.lineEdit_BrCv_26, 3, 0, 1, 1)

    w.editAxView_BrCv = QWidget(w.tab_BrCv_edit)
    w.editAxView_BrCv.setObjectName(u"editAxView_BrCv")

    w.gridLayout_BrCv_10.addWidget(w.editAxView_BrCv, 0, 0, 1, 2)

    w.verticalSpacer_BrCv_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_BrCv_10.addItem(w.verticalSpacer_BrCv_6, 7, 0, 1, 1)

    w.clipCycles_BrCv = QCheckBox(w.tab_BrCv_edit)
    w.clipCycles_BrCv.setObjectName(u"clipCycles_BrCv")
    w.clipCycles_BrCv.setChecked(True)

    w.gridLayout_BrCv_10.addWidget(w.clipCycles_BrCv, 4, 0, 1, 1)

    w.editXMaxSlider_BrCv = QSlider(w.tab_BrCv_edit)
    w.editXMaxSlider_BrCv.setObjectName(u"editXMaxSlider_BrCv")
    w.editXMaxSlider_BrCv.setMaximum(999999)
    w.editXMaxSlider_BrCv.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_BrCv_10.addWidget(w.editXMaxSlider_BrCv, 3, 1, 1, 1)

    w.lineEdit_BrCv_25 = QLineEdit(w.tab_BrCv_edit)
    w.lineEdit_BrCv_25.setObjectName(u"lineEdit_BrCv_25")
    w.lineEdit_BrCv_25.setEnabled(False)

    w.gridLayout_BrCv_10.addWidget(w.lineEdit_BrCv_25, 2, 0, 1, 1)

    w.cropRangeEdit_BrCv = QPushButton(w.tab_BrCv_edit)
    w.cropRangeEdit_BrCv.setObjectName(u"cropRangeEdit_BrCv")

    w.gridLayout_BrCv_10.addWidget(w.cropRangeEdit_BrCv, 5, 0, 1, 1)

    w.editXAxis_BrCv = QComboBox(w.tab_BrCv_edit)
    w.editXAxis_BrCv.setObjectName(u"editXAxis_BrCv")
    sizePolicy6.setHeightForWidth(w.editXAxis_BrCv.sizePolicy().hasHeightForWidth())
    w.editXAxis_BrCv.setSizePolicy(sizePolicy6)

    w.gridLayout_BrCv_10.addWidget(w.editXAxis_BrCv, 1, 1, 1, 1)

    w.lineEdit_BrCv_27 = QLineEdit(w.tab_BrCv_edit)
    w.lineEdit_BrCv_27.setObjectName(u"lineEdit_BrCv_27")
    w.lineEdit_BrCv_27.setEnabled(False)

    w.gridLayout_BrCv_10.addWidget(w.lineEdit_BrCv_27, 1, 0, 1, 1)

    w.gridLayout_BrCv_10.setRowStretch(0, 3)
    w.gridLayout_BrCv_10.setColumnStretch(0, 1)
    w.gridLayout_BrCv_10.setColumnStretch(1, 4)

    w.gridLayout_BrCv_edit.addLayout(w.gridLayout_BrCv_10, 0, 1, 1, 1)

    w.gridLayout_BrCv_edit.setColumnStretch(0, 2)
    w.gridLayout_BrCv_edit.setColumnStretch(1, 5)
    w.tabWidget_BrCv.addTab(w.tab_BrCv_edit, "")
    w.tab_BrCv_plot = QWidget()
    w.tab_BrCv_plot.setObjectName(u"tab_BrCv_plot")
    w.gridLayout_BrCv_4 = QGridLayout(w.tab_BrCv_plot)
    w.gridLayout_BrCv_4.setObjectName(u"gridLayout_BrCv_4")
    w.verticalLayout_BrCv_1 = QVBoxLayout()
    w.verticalLayout_BrCv_1.setObjectName(u"verticalLayout_BrCv_1")
    w.calcStats_BrCv = QPushButton(w.tab_BrCv_plot)
    w.calcStats_BrCv.setObjectName(u"calcStats_BrCv")

    w.verticalLayout_BrCv_1.addWidget(w.calcStats_BrCv)

    w.lineEdit_BrCv_9 = QLineEdit(w.tab_BrCv_plot)
    w.lineEdit_BrCv_9.setObjectName(u"lineEdit_BrCv_9")
    w.lineEdit_BrCv_9.setEnabled(False)

    w.verticalLayout_BrCv_1.addWidget(w.lineEdit_BrCv_9)

    w.tableViewAmplStats = QTableWidget(w.tab_BrCv_plot)
    w.tableViewAmplStats.setObjectName(u"tableViewAmplStats")

    w.verticalLayout_BrCv_1.addWidget(w.tableViewAmplStats)

    w.lineEdit_BrCv_10 = QLineEdit(w.tab_BrCv_plot)
    w.lineEdit_BrCv_10.setObjectName(u"lineEdit_BrCv_10")
    w.lineEdit_BrCv_10.setEnabled(False)

    w.verticalLayout_BrCv_1.addWidget(w.lineEdit_BrCv_10)

    w.tableViewCyclStats = QTableWidget(w.tab_BrCv_plot)
    w.tableViewCyclStats.setObjectName(u"tableViewCyclStats")

    w.verticalLayout_BrCv_1.addWidget(w.tableViewCyclStats)

    w.lineEdit_BrCv_11 = QLineEdit(w.tab_BrCv_plot)
    w.lineEdit_BrCv_11.setObjectName(u"lineEdit_BrCv_11")
    w.lineEdit_BrCv_11.setEnabled(False)

    w.verticalLayout_BrCv_1.addWidget(w.lineEdit_BrCv_11)

    w.tableViewSpeedStats = QTableWidget(w.tab_BrCv_plot)
    w.tableViewSpeedStats.setObjectName(u"tableViewSpeedStats")

    w.verticalLayout_BrCv_1.addWidget(w.tableViewSpeedStats)


    w.gridLayout_BrCv_4.addLayout(w.verticalLayout_BrCv_1, 0, 0, 1, 1)

    w.gridLayout_BrCv_11 = QGridLayout()
    w.gridLayout_BrCv_11.setObjectName(u"gridLayout_BrCv_11")
    w.gridLayout_BrCv_11.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
    w.plotXAxis_BrCv = QComboBox(w.tab_BrCv_plot)
    w.plotXAxis_BrCv.setObjectName(u"plotXAxis_BrCv")
    sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    sizePolicy8.setHorizontalStretch(0)
    sizePolicy8.setVerticalStretch(0)
    sizePolicy8.setHeightForWidth(w.plotXAxis_BrCv.sizePolicy().hasHeightForWidth())
    w.plotXAxis_BrCv.setSizePolicy(sizePolicy8)

    w.gridLayout_BrCv_11.addWidget(w.plotXAxis_BrCv, 1, 1, 1, 1)

    w.lineEdit_BrCv_15 = QLineEdit(w.tab_BrCv_plot)
    w.lineEdit_BrCv_15.setObjectName(u"lineEdit_BrCv_15")
    w.lineEdit_BrCv_15.setEnabled(False)

    w.gridLayout_BrCv_11.addWidget(w.lineEdit_BrCv_15, 2, 0, 1, 1)

    w.plotView_BrCv = QPushButton(w.tab_BrCv_plot)
    w.plotView_BrCv.setObjectName(u"plotView_BrCv")

    w.gridLayout_BrCv_11.addWidget(w.plotView_BrCv, 5, 0, 1, 1)

    w.plotAxView_BrCv = QWidget(w.tab_BrCv_plot)
    w.plotAxView_BrCv.setObjectName(u"plotAxView_BrCv")

    w.gridLayout_BrCv_11.addWidget(w.plotAxView_BrCv, 0, 0, 1, 4)

    w.lineEdit_BrCv_14 = QLineEdit(w.tab_BrCv_plot)
    w.lineEdit_BrCv_14.setObjectName(u"lineEdit_BrCv_14")
    w.lineEdit_BrCv_14.setEnabled(False)
    sizePolicy8.setHeightForWidth(w.lineEdit_BrCv_14.sizePolicy().hasHeightForWidth())
    w.lineEdit_BrCv_14.setSizePolicy(sizePolicy8)

    w.gridLayout_BrCv_11.addWidget(w.lineEdit_BrCv_14, 1, 0, 1, 1)

    w.lineEdit_82 = QLineEdit(w.tab_BrCv_plot)
    w.lineEdit_82.setObjectName(u"lineEdit_82")
    w.lineEdit_82.setEnabled(False)

    w.gridLayout_BrCv_11.addWidget(w.lineEdit_82, 3, 0, 1, 1)

    w.plotYAxis_BrCv = QComboBox(w.tab_BrCv_plot)
    w.plotYAxis_BrCv.setObjectName(u"plotYAxis_BrCv")
    sizePolicy8.setHeightForWidth(w.plotYAxis_BrCv.sizePolicy().hasHeightForWidth())
    w.plotYAxis_BrCv.setSizePolicy(sizePolicy8)

    w.gridLayout_BrCv_11.addWidget(w.plotYAxis_BrCv, 2, 1, 1, 1)

    w.verticalSpacer_BrCv_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_BrCv_11.addItem(w.verticalSpacer_BrCv_3, 6, 0, 1, 1)

    w.plotPeaks_BrCv = QCheckBox(w.tab_BrCv_plot)
    w.plotPeaks_BrCv.setObjectName(u"plotPeaks_BrCv")

    w.gridLayout_BrCv_11.addWidget(w.plotPeaks_BrCv, 4, 0, 1, 1)

    w.plotTitle_BrCv = QLineEdit(w.tab_BrCv_plot)
    w.plotTitle_BrCv.setObjectName(u"plotTitle_BrCv")

    w.gridLayout_BrCv_11.addWidget(w.plotTitle_BrCv, 3, 1, 1, 1)

    w.gridLayout_BrCv_11.setRowStretch(0, 4)
    w.gridLayout_BrCv_11.setRowStretch(1, 1)
    w.gridLayout_BrCv_11.setRowStretch(2, 1)
    w.gridLayout_BrCv_11.setRowStretch(3, 1)
    w.gridLayout_BrCv_11.setRowStretch(4, 1)
    w.gridLayout_BrCv_11.setRowStretch(5, 1)
    w.gridLayout_BrCv_11.setRowStretch(6, 1)
    w.gridLayout_BrCv_11.setColumnStretch(0, 1)
    w.gridLayout_BrCv_11.setColumnStretch(1, 1)
    w.gridLayout_BrCv_11.setColumnStretch(2, 1)
    w.gridLayout_BrCv_11.setColumnStretch(3, 1)

    w.gridLayout_BrCv_4.addLayout(w.gridLayout_BrCv_11, 0, 1, 1, 1)

    w.gridLayout_BrCv_4.setColumnStretch(0, 1)
    w.gridLayout_BrCv_4.setColumnStretch(1, 3)
    w.tabWidget_BrCv.addTab(w.tab_BrCv_plot, "")
    w.tab_PhOper = QWidget()
    w.tab_PhOper.setObjectName(u"tab_PhOper")
    w.gridLayout_73 = QGridLayout(w.tab_PhOper)
    w.gridLayout_73.setObjectName(u"gridLayout_73")
    w.BrCv_PhOperWidget = QTabWidget(w.tab_PhOper)
    w.BrCv_PhOperWidget.setObjectName(u"BrCv_PhOperWidget")
    w.tab_DuetControl = QWidget()
    w.tab_DuetControl.setObjectName(u"tab_DuetControl")
    w.gridLayout_DuetWebControl = QGridLayout(w.tab_DuetControl)
    w.gridLayout_DuetWebControl.setObjectName(u"gridLayout_DuetWebControl")
    w.loadDuetPage = QPushButton(w.tab_DuetControl)
    w.loadDuetPage.setObjectName(u"loadDuetPage")

    w.gridLayout_DuetWebControl.addWidget(w.loadDuetPage, 0, 2, 1, 1)

    w.DuetIPAddress = QLineEdit(w.tab_DuetControl)
    w.DuetIPAddress.setObjectName(u"DuetIPAddress")

    w.gridLayout_DuetWebControl.addWidget(w.DuetIPAddress, 0, 1, 1, 1)

    w.DuetControlView = QWebEngineView(w.tab_DuetControl)
    w.DuetControlView.setObjectName(u"DuetControlView")
    w.DuetControlView.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
    w.DuetControlView.setUrl(QUrl(u"http://192.168.0.1/Job/Status"))

    w.gridLayout_DuetWebControl.addWidget(w.DuetControlView, 2, 0, 1, 5)

    w.lineEdit_65 = QLineEdit(w.tab_DuetControl)
    w.lineEdit_65.setObjectName(u"lineEdit_65")
    w.lineEdit_65.setEnabled(False)

    w.gridLayout_DuetWebControl.addWidget(w.lineEdit_65, 0, 0, 1, 1)

    w.definePhOperFolder = QPushButton(w.tab_DuetControl)
    w.definePhOperFolder.setObjectName(u"definePhOperFolder")

    w.gridLayout_DuetWebControl.addWidget(w.definePhOperFolder, 1, 2, 1, 1)

    w.PhOperFolder = QLineEdit(w.tab_DuetControl)
    w.PhOperFolder.setObjectName(u"PhOperFolder")
    w.PhOperFolder.setEnabled(False)

    w.gridLayout_DuetWebControl.addWidget(w.PhOperFolder, 1, 0, 1, 2)

    w.horizontalSpacer_78 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_DuetWebControl.addItem(w.horizontalSpacer_78, 0, 3, 1, 2)

    w.gridLayout_DuetWebControl.setColumnStretch(0, 1)
    w.gridLayout_DuetWebControl.setColumnStretch(1, 1)
    w.gridLayout_DuetWebControl.setColumnStretch(2, 1)
    w.gridLayout_DuetWebControl.setColumnStretch(3, 4)
    w.BrCv_PhOperWidget.addTab(w.tab_DuetControl, "")
    w.tab_MoVe = QWidget()
    w.tab_MoVe.setObjectName(u"tab_MoVe")
    w.gridLayout_93 = QGridLayout(w.tab_MoVe)
    w.gridLayout_93.setObjectName(u"gridLayout_93")
    w.MoVeView = QWidget(w.tab_MoVe)
    w.MoVeView.setObjectName(u"MoVeView")

    w.gridLayout_93.addWidget(w.MoVeView, 0, 0, 1, 3)

    w.lineEdit_MoVeOffset = QLineEdit(w.tab_MoVe)
    w.lineEdit_MoVeOffset.setObjectName(u"lineEdit_MoVeOffset")
    w.lineEdit_MoVeOffset.setEnabled(False)

    w.gridLayout_93.addWidget(w.lineEdit_MoVeOffset, 1, 0, 1, 1)

    w.MoVeOffsetSlider = QSlider(w.tab_MoVe)
    w.MoVeOffsetSlider.setObjectName(u"MoVeOffsetSlider")
    w.MoVeOffsetSlider.setMinimum(-50)
    w.MoVeOffsetSlider.setMaximum(50)
    w.MoVeOffsetSlider.setSingleStep(1)
    w.MoVeOffsetSlider.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_93.addWidget(w.MoVeOffsetSlider, 1, 1, 1, 1)

    w.horizontalSpacer_77 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_93.addItem(w.horizontalSpacer_77, 1, 2, 1, 1)

    w.lineEdit_MoVeSF = QLineEdit(w.tab_MoVe)
    w.lineEdit_MoVeSF.setObjectName(u"lineEdit_MoVeSF")
    w.lineEdit_MoVeSF.setEnabled(False)

    w.gridLayout_93.addWidget(w.lineEdit_MoVeSF, 2, 0, 1, 1)

    w.MoVeSpeedFactor = QSpinBox(w.tab_MoVe)
    w.MoVeSpeedFactor.setObjectName(u"MoVeSpeedFactor")
    w.MoVeSpeedFactor.setMaximum(200)
    w.MoVeSpeedFactor.setValue(100)

    w.gridLayout_93.addWidget(w.MoVeSpeedFactor, 2, 1, 1, 1)

    w.MoVeAutoControl = QCheckBox(w.tab_MoVe)
    w.MoVeAutoControl.setObjectName(u"MoVeAutoControl")

    w.gridLayout_93.addWidget(w.MoVeAutoControl, 2, 2, 1, 1)

    w.lineEdit_80 = QLineEdit(w.tab_MoVe)
    w.lineEdit_80.setObjectName(u"lineEdit_80")
    w.lineEdit_80.setEnabled(False)

    w.gridLayout_93.addWidget(w.lineEdit_80, 3, 0, 1, 1)

    w.MoVeSystemLatency = QDoubleSpinBox(w.tab_MoVe)
    w.MoVeSystemLatency.setObjectName(u"MoVeSystemLatency")

    w.gridLayout_93.addWidget(w.MoVeSystemLatency, 3, 1, 1, 1)

    w.stop_until_radiation = QCheckBox(w.tab_MoVe)
    w.stop_until_radiation.setObjectName(u"stop_until_radiation")

    w.gridLayout_93.addWidget(w.stop_until_radiation, 3, 2, 1, 1)

    w.exportDataMoVe = QPushButton(w.tab_MoVe)
    w.exportDataMoVe.setObjectName(u"exportDataMoVe")

    w.gridLayout_93.addWidget(w.exportDataMoVe, 4, 0, 1, 1)

    w.MoVeAcqStart = QPushButton(w.tab_MoVe)
    w.MoVeAcqStart.setObjectName(u"MoVeAcqStart")

    w.gridLayout_93.addWidget(w.MoVeAcqStart, 4, 1, 1, 1)

    w.BrCv_PhOperWidget.addTab(w.tab_MoVe, "")

    w.gridLayout_73.addWidget(w.BrCv_PhOperWidget, 0, 0, 2, 1)

    w.tabWidget_BrCv.addTab(w.tab_PhOper, "")

    w.gridLayout_BrCv.addWidget(w.tabWidget_BrCv, 0, 0, 1, 1)

