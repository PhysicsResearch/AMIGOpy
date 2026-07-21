# -*- coding: utf-8 -*-
"""
sidebar.py - AMIGOpy GUI Module
==================================

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


def create_sidebar(w):
    """
    Create the left sidebar widgets.

    Creates:
    - groupBox: Layer controls panel with alpha sliders/spinboxes for
      Layers 0-3, PMI slider, transparency label, active layer selector
    - progressBar: Progress indicator bar
    - label_2: Status text label
    - groupBox_17: Data tree panel with DataTreeView

    Note: The groupBox and groupBox_17 are added to gridLayout_3 which
    must already exist on w.centralwidget.

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
    w.groupBox = QGroupBox(w.centralwidget)
    w.groupBox.setObjectName(u"groupBox")
    w.gridLayout_14 = QGridLayout(w.groupBox)
    w.gridLayout_14.setObjectName(u"gridLayout_14")
    w.Layer_1_alpha_sli = QSlider(w.groupBox)
    w.Layer_1_alpha_sli.setObjectName(u"Layer_1_alpha_sli")
    w.Layer_1_alpha_sli.setMaximum(100)
    w.Layer_1_alpha_sli.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_14.addWidget(w.Layer_1_alpha_sli, 6, 2, 1, 4)

    w.Layer_2_alpha_sli = QSlider(w.groupBox)
    w.Layer_2_alpha_sli.setObjectName(u"Layer_2_alpha_sli")
    w.Layer_2_alpha_sli.setMaximum(100)
    w.Layer_2_alpha_sli.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_14.addWidget(w.Layer_2_alpha_sli, 7, 2, 1, 4)

    w.Layer_3_alpha_spin = QDoubleSpinBox(w.groupBox)
    w.Layer_3_alpha_spin.setObjectName(u"Layer_3_alpha_spin")
    w.Layer_3_alpha_spin.setMaximum(1.000000000000000)
    w.Layer_3_alpha_spin.setSingleStep(5.000000000000000)

    w.gridLayout_14.addWidget(w.Layer_3_alpha_spin, 8, 6, 1, 1)

    w.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_14.addItem(w.horizontalSpacer_11, 12, 3, 1, 1)

    w.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_14.addItem(w.horizontalSpacer_13, 12, 5, 1, 1)

    w.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_14.addItem(w.horizontalSpacer_12, 12, 4, 1, 1)

    w.lineEdit_18 = QLineEdit(w.groupBox)
    w.lineEdit_18.setObjectName(u"lineEdit_18")

    w.gridLayout_14.addWidget(w.lineEdit_18, 4, 1, 1, 1)

    w.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_14.addItem(w.horizontalSpacer_10, 12, 1, 1, 1)

    w.Layer_0_alpha_sli = QSlider(w.groupBox)
    w.Layer_0_alpha_sli.setObjectName(u"Layer_0_alpha_sli")
    w.Layer_0_alpha_sli.setMaximum(100)
    w.Layer_0_alpha_sli.setSingleStep(1)
    w.Layer_0_alpha_sli.setValue(100)
    w.Layer_0_alpha_sli.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_14.addWidget(w.Layer_0_alpha_sli, 4, 2, 1, 4)

    w.Layer_0_alpha_spin = QDoubleSpinBox(w.groupBox)
    w.Layer_0_alpha_spin.setObjectName(u"Layer_0_alpha_spin")
    w.Layer_0_alpha_spin.setMaximum(1.000000000000000)
    w.Layer_0_alpha_spin.setSingleStep(0.050000000000000)
    w.Layer_0_alpha_spin.setValue(1.000000000000000)

    w.gridLayout_14.addWidget(w.Layer_0_alpha_spin, 4, 6, 1, 1)

    w.Layer_3_alpha_sli = QSlider(w.groupBox)
    w.Layer_3_alpha_sli.setObjectName(u"Layer_3_alpha_sli")
    w.Layer_3_alpha_sli.setMaximum(100)
    w.Layer_3_alpha_sli.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_14.addWidget(w.Layer_3_alpha_sli, 8, 2, 1, 4)

    w.lineEdit_21 = QLineEdit(w.groupBox)
    w.lineEdit_21.setObjectName(u"lineEdit_21")

    w.gridLayout_14.addWidget(w.lineEdit_21, 8, 1, 1, 1)

    w.line_10 = QFrame(w.groupBox)
    w.line_10.setObjectName(u"line_10")
    w.line_10.setFrameShape(QFrame.Shape.HLine)
    w.line_10.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_14.addWidget(w.line_10, 9, 1, 1, 6)

    w.lineEdit_20 = QLineEdit(w.groupBox)
    w.lineEdit_20.setObjectName(u"lineEdit_20")

    w.gridLayout_14.addWidget(w.lineEdit_20, 7, 1, 1, 1)

    w.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_14.addItem(w.horizontalSpacer_14, 12, 6, 1, 1)

    w.lineEdit_22 = QLineEdit(w.groupBox)
    w.lineEdit_22.setObjectName(u"lineEdit_22")

    w.gridLayout_14.addWidget(w.lineEdit_22, 11, 1, 1, 1)

    w.Layer_1_alpha_spin = QDoubleSpinBox(w.groupBox)
    w.Layer_1_alpha_spin.setObjectName(u"Layer_1_alpha_spin")
    w.Layer_1_alpha_spin.setMaximum(1.000000000000000)
    w.Layer_1_alpha_spin.setSingleStep(0.050000000000000)

    w.gridLayout_14.addWidget(w.Layer_1_alpha_spin, 6, 6, 1, 1)

    w.line_11 = QFrame(w.groupBox)
    w.line_11.setObjectName(u"line_11")
    w.line_11.setFrameShape(QFrame.Shape.HLine)
    w.line_11.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_14.addWidget(w.line_11, 2, 1, 1, 6)

    w.horizontalSlider_5 = QSlider(w.groupBox)
    w.horizontalSlider_5.setObjectName(u"horizontalSlider_5")
    w.horizontalSlider_5.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_14.addWidget(w.horizontalSlider_5, 11, 2, 1, 4)

    w.lineEdit_23 = QLineEdit(w.groupBox)
    w.lineEdit_23.setObjectName(u"lineEdit_23")
    font = QFont()
    font.setPointSize(10)
    w.lineEdit_23.setFont(font)
    w.lineEdit_23.setAlignment(Qt.AlignmentFlag.AlignCenter)

    w.gridLayout_14.addWidget(w.lineEdit_23, 3, 1, 1, 6)

    w.Layer_2_alpha_spin = QDoubleSpinBox(w.groupBox)
    w.Layer_2_alpha_spin.setObjectName(u"Layer_2_alpha_spin")
    w.Layer_2_alpha_spin.setMaximum(1.000000000000000)
    w.Layer_2_alpha_spin.setSingleStep(0.050000000000000)

    w.gridLayout_14.addWidget(w.Layer_2_alpha_spin, 7, 6, 1, 1)

    w.horizontalSpacer_15 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_14.addItem(w.horizontalSpacer_15, 12, 2, 1, 1)

    w.lineEdit_24 = QLineEdit(w.groupBox)
    w.lineEdit_24.setObjectName(u"lineEdit_24")

    w.gridLayout_14.addWidget(w.lineEdit_24, 1, 1, 1, 1)

    w.doubleSpinBox_7 = QDoubleSpinBox(w.groupBox)
    w.doubleSpinBox_7.setObjectName(u"doubleSpinBox_7")

    w.gridLayout_14.addWidget(w.doubleSpinBox_7, 11, 6, 1, 1)

    w.lineEdit_19 = QLineEdit(w.groupBox)
    w.lineEdit_19.setObjectName(u"lineEdit_19")

    w.gridLayout_14.addWidget(w.lineEdit_19, 6, 1, 1, 1)

    w.Layer_sel = QComboBox(w.groupBox)
    w.Layer_sel.setObjectName(u"Layer_sel")

    w.gridLayout_14.addWidget(w.Layer_sel, 1, 2, 1, 1)


    w.gridLayout_3.addWidget(w.groupBox, 1, 0, 1, 2)

    w.progressBar = QProgressBar(w.centralwidget)
    w.progressBar.setObjectName(u"progressBar")
    w.progressBar.setValue(24)

    w.gridLayout_3.addWidget(w.progressBar, 4, 0, 2, 1)

    w.label_2 = QLabel(w.centralwidget)
    w.label_2.setObjectName(u"label_2")
    sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    sizePolicy1.setHorizontalStretch(0)
    sizePolicy1.setVerticalStretch(0)
    sizePolicy1.setHeightForWidth(w.label_2.sizePolicy().hasHeightForWidth())
    w.label_2.setSizePolicy(sizePolicy1)

    w.gridLayout_3.addWidget(w.label_2, 4, 1, 1, 2)

    w.groupBox_17 = QGroupBox(w.centralwidget)
    w.groupBox_17.setObjectName(u"groupBox_17")
    w.gridLayout_47 = QGridLayout(w.groupBox_17)
    w.gridLayout_47.setObjectName(u"gridLayout_47")
    w.DataTreeView = QTreeView(w.groupBox_17)
    w.DataTreeView.setObjectName(u"DataTreeView")
    sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
    sizePolicy2.setHorizontalStretch(0)
    sizePolicy2.setVerticalStretch(0)
    sizePolicy2.setHeightForWidth(w.DataTreeView.sizePolicy().hasHeightForWidth())
    w.DataTreeView.setSizePolicy(sizePolicy2)

    w.gridLayout_47.addWidget(w.DataTreeView, 0, 0, 1, 1)


    w.gridLayout_3.addWidget(w.groupBox_17, 0, 0, 1, 2)

