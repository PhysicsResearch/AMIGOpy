# -*- coding: utf-8 -*-
"""
tab_3d_printing.py - AMIGOpy GUI Module
==========================================

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


def create_tab_3d_printing(w):
    """
    Create the 3D Printing module tab (tab_3DP).

    Creates the 3D printing material management interface:
    - D3 QTabWidget with sub-tabs:
      * MatDB: material database table
      * MatMix: material mixing controls
      * Calibration: 3D printing calibration data

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
    w.tab_3DP = QWidget()
    w.tab_3DP.setObjectName(u"tab_3DP")
    w.gridLayout_87 = QGridLayout(w.tab_3DP)
    w.gridLayout_87.setObjectName(u"gridLayout_87")
    w.D3 = QTabWidget(w.tab_3DP)
    w.D3.setObjectName(u"D3")
    w.tab_18 = QWidget()
    w.tab_18.setObjectName(u"tab_18")
    w.D3.addTab(w.tab_18, "")
    w.tab_27 = QWidget()
    w.tab_27.setObjectName(u"tab_27")
    w.D3.addTab(w.tab_27, "")
    w.tab_19 = QWidget()
    w.tab_19.setObjectName(u"tab_19")
    w.gridLayout_29 = QGridLayout(w.tab_19)
    w.gridLayout_29.setObjectName(u"gridLayout_29")
    w.import_reference_btn = QPushButton(w.tab_19)
    w.import_reference_btn.setObjectName(u"import_reference_btn")

    w.gridLayout_29.addWidget(w.import_reference_btn, 0, 0, 1, 1)

    w.import_tested_filaments_btn = QPushButton(w.tab_19)
    w.import_tested_filaments_btn.setObjectName(u"import_tested_filaments_btn")

    w.gridLayout_29.addWidget(w.import_tested_filaments_btn, 0, 1, 1, 1)

    w.label_human_tissue = QLabel(w.tab_19)
    w.label_human_tissue.setObjectName(u"label_human_tissue")

    w.gridLayout_29.addWidget(w.label_human_tissue, 1, 0, 1, 1)

    w.tissue_combo = QComboBox(w.tab_19)
    w.tissue_combo.setObjectName(u"tissue_combo")

    w.gridLayout_29.addWidget(w.tissue_combo, 1, 1, 1, 1)

    w.show_filaments_button = QPushButton(w.tab_19)
    w.show_filaments_button.setObjectName(u"show_filaments_button")

    w.gridLayout_29.addWidget(w.show_filaments_button, 2, 0, 1, 2)

    w.tableView_filaments = QTableView(w.tab_19)
    w.tableView_filaments.setObjectName(u"tableView_filaments")

    w.gridLayout_29.addWidget(w.tableView_filaments, 3, 0, 1, 2)

    w.load_cal_btn = QPushButton(w.tab_19)
    w.load_cal_btn.setObjectName(u"load_cal_btn")

    w.gridLayout_29.addWidget(w.load_cal_btn, 4, 0, 1, 2)

    w.label_filament = QLabel(w.tab_19)
    w.label_filament.setObjectName(u"label_filament")

    w.gridLayout_29.addWidget(w.label_filament, 5, 0, 1, 1)

    w.filament_combo = QComboBox(w.tab_19)
    w.filament_combo.setObjectName(u"filament_combo")

    w.gridLayout_29.addWidget(w.filament_combo, 5, 1, 1, 1)

    w.groupBox_optim_method = QGroupBox(w.tab_19)
    w.groupBox_optim_method.setObjectName(u"groupBox_optim_method")
    w.gridLayout_88 = QGridLayout(w.groupBox_optim_method)
    w.gridLayout_88.setObjectName(u"gridLayout_88")
    w.radio_flow = QRadioButton(w.groupBox_optim_method)
    w.radio_flow.setObjectName(u"radio_flow")

    w.gridLayout_88.addWidget(w.radio_flow, 0, 0, 1, 1)

    w.radio_flow_infill = QRadioButton(w.groupBox_optim_method)
    w.radio_flow_infill.setObjectName(u"radio_flow_infill")

    w.gridLayout_88.addWidget(w.radio_flow_infill, 0, 1, 1, 1)


    w.gridLayout_29.addWidget(w.groupBox_optim_method, 6, 0, 1, 2)

    w.groupBox_Extrap = QGroupBox(w.tab_19)
    w.groupBox_Extrap.setObjectName(u"groupBox_Extrap")
    w.gridLayout_89 = QGridLayout(w.groupBox_Extrap)
    w.gridLayout_89.setObjectName(u"gridLayout_89")
    w.radio_extrap = QRadioButton(w.groupBox_Extrap)
    w.radio_extrap.setObjectName(u"radio_extrap")

    w.gridLayout_89.addWidget(w.radio_extrap, 0, 0, 1, 1)

    w.radio_no_extrap = QRadioButton(w.groupBox_Extrap)
    w.radio_no_extrap.setObjectName(u"radio_no_extrap")

    w.gridLayout_89.addWidget(w.radio_no_extrap, 0, 1, 1, 1)


    w.gridLayout_29.addWidget(w.groupBox_Extrap, 7, 0, 1, 2)

    w.RED_calc_button = QPushButton(w.tab_19)
    w.RED_calc_button.setObjectName(u"RED_calc_button")

    w.gridLayout_29.addWidget(w.RED_calc_button, 8, 0, 1, 2)

    w.tableView_red = QTableView(w.tab_19)
    w.tableView_red.setObjectName(u"tableView_red")

    w.gridLayout_29.addWidget(w.tableView_red, 9, 0, 1, 2)

    w.verticalSpacer_24 = QSpacerItem(20, 209, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_29.addItem(w.verticalSpacer_24, 10, 0, 1, 2)

    w.D3.addTab(w.tab_19, "")

    w.gridLayout_87.addWidget(w.D3, 0, 0, 1, 1)

