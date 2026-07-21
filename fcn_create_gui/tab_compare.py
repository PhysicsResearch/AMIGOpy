# -*- coding: utf-8 -*-
"""
tab_compare.py - AMIGOpy GUI Module
======================================

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


def create_tab_compare(w):
    """
    Create the Compare module tab (im_compare_tab).

    Creates the side-by-side image comparison interface:
    - Dual VTK view containers for comparison display
    - Comparison sliders and overlay controls

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
    w.im_compare_tab = QWidget()
    w.im_compare_tab.setObjectName(u"im_compare_tab")
    w.gridLayout_16 = QGridLayout(w.im_compare_tab)
    w.gridLayout_16.setObjectName(u"gridLayout_16")
    w.SliderCompareView = QSlider(w.im_compare_tab)
    w.SliderCompareView.setObjectName(u"SliderCompareView")
    w.SliderCompareView.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_16.addWidget(w.SliderCompareView, 3, 1, 1, 1)

    w.groupBox_2 = QGroupBox(w.im_compare_tab)
    w.groupBox_2.setObjectName(u"groupBox_2")
    w.groupBox_2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    w.gridLayout_17 = QGridLayout(w.groupBox_2)
    w.gridLayout_17.setObjectName(u"gridLayout_17")
    w.gridLayout_17.setContentsMargins(2, 2, 2, 2)
    w.gridLayout_17.setSpacing(2)
    for r in range(3):
        w.gridLayout_17.setRowStretch(r, 1)
    for c in range(4):
        w.gridLayout_17.setColumnStretch(c, 1)

    w.Ax_comp_cont_1 = QWidget(w.groupBox_2)
    w.Ax_comp_cont_1.setObjectName(u"Ax_comp_cont_1")

    w.gridLayout_17.addWidget(w.Ax_comp_cont_1, 0, 0, 1, 1)

    w.Ax_comp_cont_4 = QWidget(w.groupBox_2)
    w.Ax_comp_cont_4.setObjectName(u"Ax_comp_cont_4")

    w.gridLayout_17.addWidget(w.Ax_comp_cont_4, 0, 1, 1, 1)

    w.Ax_comp_cont_7 = QWidget(w.groupBox_2)
    w.Ax_comp_cont_7.setObjectName(u"Ax_comp_cont_7")

    w.gridLayout_17.addWidget(w.Ax_comp_cont_7, 0, 2, 1, 1)

    w.Ax_comp_cont_10 = QWidget(w.groupBox_2)
    w.Ax_comp_cont_10.setObjectName(u"Ax_comp_cont_10")

    w.gridLayout_17.addWidget(w.Ax_comp_cont_10, 0, 3, 1, 1)

    w.Ax_comp_cont_2 = QWidget(w.groupBox_2)
    w.Ax_comp_cont_2.setObjectName(u"Ax_comp_cont_2")

    w.gridLayout_17.addWidget(w.Ax_comp_cont_2, 1, 0, 1, 1)

    w.Ax_comp_cont_5 = QWidget(w.groupBox_2)
    w.Ax_comp_cont_5.setObjectName(u"Ax_comp_cont_5")

    w.gridLayout_17.addWidget(w.Ax_comp_cont_5, 1, 1, 1, 1)

    w.Ax_comp_cont_8 = QWidget(w.groupBox_2)
    w.Ax_comp_cont_8.setObjectName(u"Ax_comp_cont_8")

    w.gridLayout_17.addWidget(w.Ax_comp_cont_8, 1, 2, 1, 1)

    w.Ax_comp_cont_11 = QWidget(w.groupBox_2)
    w.Ax_comp_cont_11.setObjectName(u"Ax_comp_cont_11")

    w.gridLayout_17.addWidget(w.Ax_comp_cont_11, 1, 3, 1, 1)

    w.Ax_comp_cont_6 = QWidget(w.groupBox_2)
    w.Ax_comp_cont_6.setObjectName(u"Ax_comp_cont_6")

    w.gridLayout_17.addWidget(w.Ax_comp_cont_6, 2, 1, 1, 1)

    w.Ax_comp_cont_9 = QWidget(w.groupBox_2)
    w.Ax_comp_cont_9.setObjectName(u"Ax_comp_cont_9")

    w.gridLayout_17.addWidget(w.Ax_comp_cont_9, 2, 2, 1, 1)

    w.Ax_comp_cont_12 = QWidget(w.groupBox_2)
    w.Ax_comp_cont_12.setObjectName(u"Ax_comp_cont_12")

    w.gridLayout_17.addWidget(w.Ax_comp_cont_12, 2, 3, 1, 1)

    w.Ax_comp_cont_3 = QWidget(w.groupBox_2)
    w.Ax_comp_cont_3.setObjectName(u"Ax_comp_cont_3")

    w.gridLayout_17.addWidget(w.Ax_comp_cont_3, 2, 0, 1, 1)


    w.gridLayout_16.setRowStretch(0, 1)
    w.gridLayout_16.setRowStretch(3, 0)
    w.gridLayout_16.addWidget(w.groupBox_2, 0, 0, 1, 10)

    w.Comp_im_idx = QSpinBox(w.im_compare_tab)
    w.Comp_im_idx.setObjectName(u"Comp_im_idx")
    w.Comp_im_idx.setMinimum(-1)
    w.Comp_im_idx.setMaximum(-1)
    w.Comp_im_idx.setValue(-1)

    w.gridLayout_16.addWidget(w.Comp_im_idx, 3, 0, 1, 1)

    w.but_create_comp_axes = QPushButton(w.im_compare_tab)
    w.but_create_comp_axes.setObjectName(u"but_create_comp_axes")
    w.but_create_comp_axes.setFont(font)

    w.gridLayout_16.addWidget(w.but_create_comp_axes, 3, 8, 1, 1)

    w.line_12 = QFrame(w.im_compare_tab)
    w.line_12.setObjectName(u"line_12")
    w.line_12.setFrameShape(QFrame.Shape.HLine)
    w.line_12.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_16.addWidget(w.line_12, 1, 0, 1, 10)

    w.Comp_linkSlices = QCheckBox(w.im_compare_tab)
    w.Comp_linkSlices.setObjectName(u"Comp_linkSlices")
    w.Comp_linkSlices.setChecked(True)

    w.gridLayout_16.addWidget(w.Comp_linkSlices, 3, 3, 1, 1)

    w.Comp_view_sel_box = QComboBox(w.im_compare_tab)
    w.Comp_view_sel_box.setObjectName(u"Comp_view_sel_box")

    w.gridLayout_16.addWidget(w.Comp_view_sel_box, 3, 6, 1, 1)

    w.link_win_lev = QCheckBox(w.im_compare_tab)
    w.link_win_lev.setObjectName(u"link_win_lev")
    w.link_win_lev.setChecked(True)

    w.gridLayout_16.addWidget(w.link_win_lev, 3, 4, 1, 1)

    w.horizontalSpacer_16 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_16.addItem(w.horizontalSpacer_16, 3, 7, 1, 1)

    w.comp_link_zoom = QCheckBox(w.im_compare_tab)
    w.comp_link_zoom.setObjectName(u"comp_link_zoom")

    w.gridLayout_16.addWidget(w.comp_link_zoom, 3, 5, 1, 1)

