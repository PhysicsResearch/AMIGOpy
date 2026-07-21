# -*- coding: utf-8 -*-
"""
tab_plan.py - AMIGOpy GUI Module
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


def create_tab_plan(w):
    """
    Create the Plan module tab (Plan_tab).

    Creates the treatment planning interface:
    - Plan_tabs QTabWidget with sub-tabs:
      * Brachy plan: plan data display, TG43 dose calculation,
        radial dose, anisotropy, along-away tables
      * EQD2: alpha/beta ratio table and EQD2 dose conversion
      * Plan Evaluation: uncertainty analysis and error simulation
      * Material Assignment: material-to-HU mapping and structure assignment
      * Density Map: electron/mass density map creation

    This is the largest module (~1500 lines of widget definitions).

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
    w.Plan_tab = QWidget()
    w.Plan_tab.setObjectName(u"Plan_tab")
    w.gridLayout_42 = QGridLayout(w.Plan_tab)
    w.gridLayout_42.setObjectName(u"gridLayout_42")
    w.Plan_tabs = QTabWidget(w.Plan_tab)
    w.Plan_tabs.setObjectName(u"Plan_tabs")
    w.Brachy_plan_tab = QWidget()
    w.Brachy_plan_tab.setObjectName(u"Brachy_plan_tab")
    w.gridLayout_43 = QGridLayout(w.Brachy_plan_tab)
    w.gridLayout_43.setObjectName(u"gridLayout_43")
    w.BrachytabWidget_2 = QTabWidget(w.Brachy_plan_tab)
    w.BrachytabWidget_2.setObjectName(u"BrachytabWidget_2")
    w.Br_tab_42 = QWidget()
    w.Br_tab_42.setObjectName(u"Br_tab_42")
    w.gridLayout_48 = QGridLayout(w.Br_tab_42)
    w.gridLayout_48.setObjectName(u"gridLayout_48")
    w.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_48.addItem(w.verticalSpacer_9, 0, 0, 1, 1)

    w.brachy_ax_01 = QWidget(w.Br_tab_42)
    w.brachy_ax_01.setObjectName(u"brachy_ax_01")

    w.gridLayout_48.addWidget(w.brachy_ax_01, 0, 1, 2, 5)

    w.brachy_ax_02 = QWidget(w.Br_tab_42)
    w.brachy_ax_02.setObjectName(u"brachy_ax_02")

    w.gridLayout_48.addWidget(w.brachy_ax_02, 0, 6, 2, 4)

    w.verticalSpacer_11 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_48.addItem(w.verticalSpacer_11, 1, 0, 1, 1)

    w.verticalSpacer_10 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_48.addItem(w.verticalSpacer_10, 2, 0, 1, 1)

    w.brachy_table_02 = QTableWidget(w.Br_tab_42)
    w.brachy_table_02.setObjectName(u"brachy_table_02")
    w.brachy_table_02.setFont(font2)

    w.gridLayout_48.addWidget(w.brachy_table_02, 2, 1, 2, 5)

    w.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_48.addItem(w.verticalSpacer_8, 3, 0, 1, 1)

    w.lineEdit_51 = QLineEdit(w.Br_tab_42)
    w.lineEdit_51.setObjectName(u"lineEdit_51")
    w.lineEdit_51.setEnabled(False)
    w.lineEdit_51.setFont(font)

    w.gridLayout_48.addWidget(w.lineEdit_51, 4, 1, 1, 1)

    w.brachy_ch_time = QLineEdit(w.Br_tab_42)
    w.brachy_ch_time.setObjectName(u"brachy_ch_time")
    w.brachy_ch_time.setEnabled(False)
    w.brachy_ch_time.setFont(font)

    w.gridLayout_48.addWidget(w.brachy_ch_time, 4, 2, 1, 1)

    w.lineEdit_52 = QLineEdit(w.Br_tab_42)
    w.lineEdit_52.setObjectName(u"lineEdit_52")
    w.lineEdit_52.setEnabled(False)
    w.lineEdit_52.setFont(font)

    w.gridLayout_48.addWidget(w.lineEdit_52, 4, 3, 1, 1)

    w.brachy_total_time = QLineEdit(w.Br_tab_42)
    w.brachy_total_time.setObjectName(u"brachy_total_time")
    w.brachy_total_time.setEnabled(False)
    w.brachy_total_time.setFont(font)

    w.gridLayout_48.addWidget(w.brachy_total_time, 4, 4, 1, 1)

    w.lineEdit_54 = QLineEdit(w.Br_tab_42)
    w.lineEdit_54.setObjectName(u"lineEdit_54")
    w.lineEdit_54.setEnabled(False)
    w.lineEdit_54.setFont(font)

    w.gridLayout_48.addWidget(w.lineEdit_54, 4, 5, 1, 1)

    w.brachy_plan_Ac = QLineEdit(w.Br_tab_42)
    w.brachy_plan_Ac.setObjectName(u"brachy_plan_Ac")
    w.brachy_plan_Ac.setEnabled(False)
    w.brachy_plan_Ac.setFont(font)

    w.gridLayout_48.addWidget(w.brachy_plan_Ac, 4, 6, 1, 1)

    w.lineEdit_53 = QLineEdit(w.Br_tab_42)
    w.lineEdit_53.setObjectName(u"lineEdit_53")
    w.lineEdit_53.setEnabled(False)
    w.lineEdit_53.setFont(font)

    w.gridLayout_48.addWidget(w.lineEdit_53, 4, 7, 1, 1)

    w.brachy_N_channels = QLineEdit(w.Br_tab_42)
    w.brachy_N_channels.setObjectName(u"brachy_N_channels")
    w.brachy_N_channels.setEnabled(False)
    w.brachy_N_channels.setFont(font)

    w.gridLayout_48.addWidget(w.brachy_N_channels, 4, 8, 1, 1)

    w.pushButton = QPushButton(w.Br_tab_42)
    w.pushButton.setObjectName(u"pushButton")

    w.gridLayout_48.addWidget(w.pushButton, 4, 9, 1, 1)

    w.lineEdit_55 = QLineEdit(w.Br_tab_42)
    w.lineEdit_55.setObjectName(u"lineEdit_55")
    w.lineEdit_55.setEnabled(False)
    w.lineEdit_55.setFont(font)

    w.gridLayout_48.addWidget(w.lineEdit_55, 5, 1, 1, 1)

    w.brachy_spinBox_02 = QSpinBox(w.Br_tab_42)
    w.brachy_spinBox_02.setObjectName(u"brachy_spinBox_02")
    w.brachy_spinBox_02.setFont(font)

    w.gridLayout_48.addWidget(w.brachy_spinBox_02, 5, 2, 1, 1)

    w.brachy_combobox_02 = QComboBox(w.Br_tab_42)
    w.brachy_combobox_02.setObjectName(u"brachy_combobox_02")

    w.gridLayout_48.addWidget(w.brachy_combobox_02, 5, 3, 1, 1)

    w.checkBox_show_dw_plot = QCheckBox(w.Br_tab_42)
    w.checkBox_show_dw_plot.setObjectName(u"checkBox_show_dw_plot")
    w.checkBox_show_dw_plot.setFont(font)
    w.checkBox_show_dw_plot.setChecked(True)

    w.gridLayout_48.addWidget(w.checkBox_show_dw_plot, 5, 6, 1, 1)

    w.checkBox_show_ch_plot = QCheckBox(w.Br_tab_42)
    w.checkBox_show_ch_plot.setObjectName(u"checkBox_show_ch_plot")
    w.checkBox_show_ch_plot.setFont(font)
    w.checkBox_show_ch_plot.setChecked(True)

    w.gridLayout_48.addWidget(w.checkBox_show_ch_plot, 5, 7, 1, 1)

    w.checkBox_dw_ch_plot = QCheckBox(w.Br_tab_42)
    w.checkBox_dw_ch_plot.setObjectName(u"checkBox_dw_ch_plot")
    w.checkBox_dw_ch_plot.setFont(font)
    w.checkBox_dw_ch_plot.setChecked(True)

    w.gridLayout_48.addWidget(w.checkBox_dw_ch_plot, 5, 8, 1, 1)

    w.brachy_ch_plot = QPushButton(w.Br_tab_42)
    w.brachy_ch_plot.setObjectName(u"brachy_ch_plot")

    w.gridLayout_48.addWidget(w.brachy_ch_plot, 5, 9, 1, 1)

    w.groupBox_11 = QGroupBox(w.Br_tab_42)
    w.groupBox_11.setObjectName(u"groupBox_11")
    w.gridLayout_46 = QGridLayout(w.groupBox_11)
    w.gridLayout_46.setObjectName(u"gridLayout_46")
    w.brachy_ch_line_width = QDoubleSpinBox(w.groupBox_11)
    w.brachy_ch_line_width.setObjectName(u"brachy_ch_line_width")
    w.brachy_ch_line_width.setFont(font)
    w.brachy_ch_line_width.setValue(1.000000000000000)

    w.gridLayout_46.addWidget(w.brachy_ch_line_width, 1, 3, 1, 1)

    w.brachy_ch_p1_color = QComboBox(w.groupBox_11)
    w.brachy_ch_p1_color.setObjectName(u"brachy_ch_p1_color")
    w.brachy_ch_p1_color.setFont(font)

    w.gridLayout_46.addWidget(w.brachy_ch_p1_color, 7, 2, 1, 1)

    w.lineEdit_60 = QLineEdit(w.groupBox_11)
    w.lineEdit_60.setObjectName(u"lineEdit_60")
    w.lineEdit_60.setEnabled(False)
    w.lineEdit_60.setFont(font)

    w.gridLayout_46.addWidget(w.lineEdit_60, 2, 2, 1, 1)

    w.brachy_dw_size = QSpinBox(w.groupBox_11)
    w.brachy_dw_size.setObjectName(u"brachy_dw_size")
    w.brachy_dw_size.setFont(font)
    w.brachy_dw_size.setValue(15)

    w.gridLayout_46.addWidget(w.brachy_dw_size, 1, 1, 1, 1)

    w.lineEdit_57 = QLineEdit(w.groupBox_11)
    w.lineEdit_57.setObjectName(u"lineEdit_57")
    w.lineEdit_57.setEnabled(False)
    w.lineEdit_57.setFont(font)

    w.gridLayout_46.addWidget(w.lineEdit_57, 1, 2, 1, 1)

    w.brachy_ch_size = QDoubleSpinBox(w.groupBox_11)
    w.brachy_ch_size.setObjectName(u"brachy_ch_size")
    w.brachy_ch_size.setFont(font)
    w.brachy_ch_size.setValue(20.000000000000000)

    w.gridLayout_46.addWidget(w.brachy_ch_size, 4, 3, 1, 1)

    w.lineEdit_56 = QLineEdit(w.groupBox_11)
    w.lineEdit_56.setObjectName(u"lineEdit_56")
    w.lineEdit_56.setEnabled(False)
    w.lineEdit_56.setFont(font)

    w.gridLayout_46.addWidget(w.lineEdit_56, 1, 0, 1, 1)

    w.lineEdit_58 = QLineEdit(w.groupBox_11)
    w.lineEdit_58.setObjectName(u"lineEdit_58")
    w.lineEdit_58.setEnabled(False)
    w.lineEdit_58.setFont(font)

    w.gridLayout_46.addWidget(w.lineEdit_58, 4, 2, 1, 1)

    w.brachy_line_color = QComboBox(w.groupBox_11)
    w.brachy_line_color.setObjectName(u"brachy_line_color")
    w.brachy_line_color.setFont(font)

    w.gridLayout_46.addWidget(w.brachy_line_color, 3, 2, 1, 1)

    w.lineEdit_59 = QLineEdit(w.groupBox_11)
    w.lineEdit_59.setObjectName(u"lineEdit_59")
    w.lineEdit_59.setEnabled(False)
    w.lineEdit_59.setFont(font)

    w.gridLayout_46.addWidget(w.lineEdit_59, 2, 0, 1, 1)

    w.brachy_dw_color = QComboBox(w.groupBox_11)
    w.brachy_dw_color.setObjectName(u"brachy_dw_color")
    w.brachy_dw_color.setFont(font)

    w.gridLayout_46.addWidget(w.brachy_dw_color, 3, 0, 1, 1)

    w.lineEdit_61 = QLineEdit(w.groupBox_11)
    w.lineEdit_61.setObjectName(u"lineEdit_61")
    w.lineEdit_61.setEnabled(False)
    w.lineEdit_61.setFont(font)

    w.gridLayout_46.addWidget(w.lineEdit_61, 5, 2, 1, 1)

    w.lineEdit_62 = QLineEdit(w.groupBox_11)
    w.lineEdit_62.setObjectName(u"lineEdit_62")
    w.lineEdit_62.setEnabled(False)

    w.gridLayout_46.addWidget(w.lineEdit_62, 4, 0, 1, 1)

    w.brachy_struc_show_01 = QComboBox(w.groupBox_11)
    w.brachy_struc_show_01.setObjectName(u"brachy_struc_show_01")
    w.brachy_struc_show_01.setFont(font)

    w.gridLayout_46.addWidget(w.brachy_struc_show_01, 5, 0, 1, 1)

    w.brachy_struc_show_02 = QComboBox(w.groupBox_11)
    w.brachy_struc_show_02.setObjectName(u"brachy_struc_show_02")
    w.brachy_struc_show_02.setFont(font)

    w.gridLayout_46.addWidget(w.brachy_struc_show_02, 7, 0, 1, 1)


    w.gridLayout_48.addWidget(w.groupBox_11, 2, 6, 1, 4)

    w.Brachy_groupBox_12 = QGroupBox(w.Br_tab_42)
    w.Brachy_groupBox_12.setObjectName(u"Brachy_groupBox_12")
    w.gridLayout_49 = QGridLayout(w.Brachy_groupBox_12)
    w.gridLayout_49.setObjectName(u"gridLayout_49")
    w.Brachy_setalldwtimes = QPushButton(w.Brachy_groupBox_12)
    w.Brachy_setalldwtimes.setObjectName(u"Brachy_setalldwtimes")

    w.gridLayout_49.addWidget(w.Brachy_setalldwtimes, 1, 0, 1, 1)

    w.Brachy_create_new_channel = QPushButton(w.Brachy_groupBox_12)
    w.Brachy_create_new_channel.setObjectName(u"Brachy_create_new_channel")

    w.gridLayout_49.addWidget(w.Brachy_create_new_channel, 1, 1, 1, 1)

    w.Brachy_DuplicateChannel = QPushButton(w.Brachy_groupBox_12)
    w.Brachy_DuplicateChannel.setObjectName(u"Brachy_DuplicateChannel")

    w.gridLayout_49.addWidget(w.Brachy_DuplicateChannel, 2, 1, 1, 1)

    w.Brachy_setIDD_distance = QPushButton(w.Brachy_groupBox_12)
    w.Brachy_setIDD_distance.setObjectName(u"Brachy_setIDD_distance")

    w.gridLayout_49.addWidget(w.Brachy_setIDD_distance, 2, 0, 1, 1)

    w.Brachy_DeadSpace_Offset = QPushButton(w.Brachy_groupBox_12)
    w.Brachy_DeadSpace_Offset.setObjectName(u"Brachy_DeadSpace_Offset")

    w.gridLayout_49.addWidget(w.Brachy_DeadSpace_Offset, 3, 0, 1, 1)

    w.Brachy_DeleteChannel = QPushButton(w.Brachy_groupBox_12)
    w.Brachy_DeleteChannel.setObjectName(u"Brachy_DeleteChannel")

    w.gridLayout_49.addWidget(w.Brachy_DeleteChannel, 4, 1, 1, 1)

    w.Brachy_Calcualte_TG43 = QPushButton(w.Brachy_groupBox_12)
    w.Brachy_Calcualte_TG43.setObjectName(u"Brachy_Calcualte_TG43")

    w.gridLayout_49.addWidget(w.Brachy_Calcualte_TG43, 3, 1, 1, 1)


    w.gridLayout_48.addWidget(w.Brachy_groupBox_12, 3, 6, 1, 4)

    w.BrachytabWidget_2.addTab(w.Br_tab_42, "")
    w.Br_tab_43 = QWidget()
    w.Br_tab_43.setObjectName(u"Br_tab_43")
    w.gridLayout_51 = QGridLayout(w.Br_tab_43)
    w.gridLayout_51.setObjectName(u"gridLayout_51")
    w.brachy_save_tg43_source = QPushButton(w.Br_tab_43)
    w.brachy_save_tg43_source.setObjectName(u"brachy_save_tg43_source")

    w.gridLayout_51.addWidget(w.brachy_save_tg43_source, 4, 0, 1, 1)

    w.horizontalSpacer_48 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_51.addItem(w.horizontalSpacer_48, 2, 1, 1, 1)

    w.Brachy_load_sources = QPushButton(w.Br_tab_43)
    w.Brachy_load_sources.setObjectName(u"Brachy_load_sources")

    w.gridLayout_51.addWidget(w.Brachy_load_sources, 3, 0, 1, 1)

    w.horizontalSpacer_49 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_51.addItem(w.horizontalSpacer_49, 2, 2, 1, 1)

    w.brachy_source_list = QComboBox(w.Br_tab_43)
    w.brachy_source_list.setObjectName(u"brachy_source_list")

    w.gridLayout_51.addWidget(w.brachy_source_list, 3, 1, 1, 1)

    w.horizontalSpacer_51 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_51.addItem(w.horizontalSpacer_51, 2, 3, 1, 1)

    w.brachy_delete_source = QPushButton(w.Br_tab_43)
    w.brachy_delete_source.setObjectName(u"brachy_delete_source")

    w.gridLayout_51.addWidget(w.brachy_delete_source, 4, 1, 1, 1)

    w.horizontalSpacer_44 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_51.addItem(w.horizontalSpacer_44, 2, 0, 1, 1)

    w.horizontalSpacer_50 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_51.addItem(w.horizontalSpacer_50, 2, 4, 1, 1)

    w.tabWidget_2 = QTabWidget(w.Br_tab_43)
    w.tabWidget_2.setObjectName(u"tabWidget_2")
    w.Brachy_tab_45 = QWidget()
    w.Brachy_tab_45.setObjectName(u"Brachy_tab_45")
    w.gridLayout_52 = QGridLayout(w.Brachy_tab_45)
    w.gridLayout_52.setObjectName(u"gridLayout_52")
    w.Brachy_Radial_load = QPushButton(w.Brachy_tab_45)
    w.Brachy_Radial_load.setObjectName(u"Brachy_Radial_load")

    w.gridLayout_52.addWidget(w.Brachy_Radial_load, 5, 0, 1, 1)

    w.horizontalSpacer_67 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_52.addItem(w.horizontalSpacer_67, 5, 4, 1, 1)

    w.Brachy_rad_eq = QLineEdit(w.Brachy_tab_45)
    w.Brachy_rad_eq.setObjectName(u"Brachy_rad_eq")
    w.Brachy_rad_eq.setEnabled(False)
    w.Brachy_rad_eq.setFont(font)

    w.gridLayout_52.addWidget(w.Brachy_rad_eq, 3, 3, 1, 12)

    w.horizontalSpacer_71 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_52.addItem(w.horizontalSpacer_71, 5, 13, 1, 1)

    w.horizontalSpacer_52 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_52.addItem(w.horizontalSpacer_52, 5, 1, 1, 1)

    w.horizontalSpacer_72 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_52.addItem(w.horizontalSpacer_72, 5, 11, 1, 1)

    w.horizontalSpacer_75 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_52.addItem(w.horizontalSpacer_75, 5, 9, 1, 1)

    w.Brachy_radial_axes = QWidget(w.Brachy_tab_45)
    w.Brachy_radial_axes.setObjectName(u"Brachy_radial_axes")

    w.gridLayout_52.addWidget(w.Brachy_radial_axes, 1, 3, 2, 12)

    w.horizontalSpacer_68 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_52.addItem(w.horizontalSpacer_68, 5, 5, 1, 1)

    w.horizontalSpacer_53 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_52.addItem(w.horizontalSpacer_53, 5, 3, 1, 1)

    w.horizontalSpacer_54 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_52.addItem(w.horizontalSpacer_54, 5, 2, 1, 1)

    w.horizontalSpacer_73 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_52.addItem(w.horizontalSpacer_73, 5, 6, 1, 1)

    w.horizontalSpacer_74 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_52.addItem(w.horizontalSpacer_74, 5, 7, 1, 1)

    w.horizontalSpacer_61 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_52.addItem(w.horizontalSpacer_61, 5, 14, 1, 1)

    w.Brachy_Radial_table = QTableWidget(w.Brachy_tab_45)
    w.Brachy_Radial_table.setObjectName(u"Brachy_Radial_table")

    w.gridLayout_52.addWidget(w.Brachy_Radial_table, 1, 0, 4, 3)

    w.horizontalSpacer_70 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_52.addItem(w.horizontalSpacer_70, 5, 12, 1, 1)

    w.horizontalSpacer_69 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_52.addItem(w.horizontalSpacer_69, 5, 10, 1, 1)

    w.horizontalSpacer_76 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_52.addItem(w.horizontalSpacer_76, 5, 8, 1, 1)

    w.Brachy_rad_A0L = QLineEdit(w.Brachy_tab_45)
    w.Brachy_rad_A0L.setObjectName(u"Brachy_rad_A0L")
    w.Brachy_rad_A0L.setEnabled(False)
    w.Brachy_rad_A0L.setFont(font)
    w.Brachy_rad_A0L.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    w.Brachy_rad_A0L.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

    w.gridLayout_52.addWidget(w.Brachy_rad_A0L, 4, 3, 1, 1)

    w.Brachy_rad_A0 = QLineEdit(w.Brachy_tab_45)
    w.Brachy_rad_A0.setObjectName(u"Brachy_rad_A0")

    w.gridLayout_52.addWidget(w.Brachy_rad_A0, 4, 4, 1, 1)

    w.Brachy_rad_A1L = QLineEdit(w.Brachy_tab_45)
    w.Brachy_rad_A1L.setObjectName(u"Brachy_rad_A1L")
    w.Brachy_rad_A1L.setEnabled(False)
    w.Brachy_rad_A1L.setFont(font)
    w.Brachy_rad_A1L.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    w.Brachy_rad_A1L.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

    w.gridLayout_52.addWidget(w.Brachy_rad_A1L, 4, 5, 1, 1)

    w.Brachy_rad_A1 = QLineEdit(w.Brachy_tab_45)
    w.Brachy_rad_A1.setObjectName(u"Brachy_rad_A1")

    w.gridLayout_52.addWidget(w.Brachy_rad_A1, 4, 6, 1, 1)

    w.Brachy_rad_A2L = QLineEdit(w.Brachy_tab_45)
    w.Brachy_rad_A2L.setObjectName(u"Brachy_rad_A2L")
    w.Brachy_rad_A2L.setEnabled(False)
    w.Brachy_rad_A2L.setFont(font)
    w.Brachy_rad_A2L.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    w.Brachy_rad_A2L.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

    w.gridLayout_52.addWidget(w.Brachy_rad_A2L, 4, 7, 1, 1)

    w.brachy_radial_1stline = QLineEdit(w.Brachy_tab_45)
    w.brachy_radial_1stline.setObjectName(u"brachy_radial_1stline")
    w.brachy_radial_1stline.setEnabled(False)
    w.brachy_radial_1stline.setFont(font)

    w.gridLayout_52.addWidget(w.brachy_radial_1stline, 0, 0, 1, 15)

    w.Brachy_rad_A2 = QLineEdit(w.Brachy_tab_45)
    w.Brachy_rad_A2.setObjectName(u"Brachy_rad_A2")

    w.gridLayout_52.addWidget(w.Brachy_rad_A2, 4, 8, 1, 1)

    w.Brachy_rad_A3L = QLineEdit(w.Brachy_tab_45)
    w.Brachy_rad_A3L.setObjectName(u"Brachy_rad_A3L")
    w.Brachy_rad_A3L.setEnabled(False)
    w.Brachy_rad_A3L.setFont(font)
    w.Brachy_rad_A3L.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    w.Brachy_rad_A3L.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

    w.gridLayout_52.addWidget(w.Brachy_rad_A3L, 4, 9, 1, 1)

    w.Brachy_rad_A3 = QLineEdit(w.Brachy_tab_45)
    w.Brachy_rad_A3.setObjectName(u"Brachy_rad_A3")

    w.gridLayout_52.addWidget(w.Brachy_rad_A3, 4, 10, 1, 1)

    w.Brachy_rad_A4L = QLineEdit(w.Brachy_tab_45)
    w.Brachy_rad_A4L.setObjectName(u"Brachy_rad_A4L")
    w.Brachy_rad_A4L.setEnabled(False)
    w.Brachy_rad_A4L.setFont(font)
    w.Brachy_rad_A4L.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    w.Brachy_rad_A4L.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

    w.gridLayout_52.addWidget(w.Brachy_rad_A4L, 4, 11, 1, 1)

    w.Brachy_rad_A4 = QLineEdit(w.Brachy_tab_45)
    w.Brachy_rad_A4.setObjectName(u"Brachy_rad_A4")

    w.gridLayout_52.addWidget(w.Brachy_rad_A4, 4, 12, 1, 1)

    w.Brachy_rad_A5L = QLineEdit(w.Brachy_tab_45)
    w.Brachy_rad_A5L.setObjectName(u"Brachy_rad_A5L")
    w.Brachy_rad_A5L.setEnabled(False)
    w.Brachy_rad_A5L.setFont(font)
    w.Brachy_rad_A5L.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    w.Brachy_rad_A5L.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

    w.gridLayout_52.addWidget(w.Brachy_rad_A5L, 4, 13, 1, 1)

    w.Brachy_rad_A5 = QLineEdit(w.Brachy_tab_45)
    w.Brachy_rad_A5.setObjectName(u"Brachy_rad_A5")

    w.gridLayout_52.addWidget(w.Brachy_rad_A5, 4, 14, 1, 1)

    w.tabWidget_2.addTab(w.Brachy_tab_45, "")
    w.Brachy_tab_46 = QWidget()
    w.Brachy_tab_46.setObjectName(u"Brachy_tab_46")
    w.gridLayout_53 = QGridLayout(w.Brachy_tab_46)
    w.gridLayout_53.setObjectName(u"gridLayout_53")
    w.Brachy_ani_dist_list = QComboBox(w.Brachy_tab_46)
    w.Brachy_ani_dist_list.setObjectName(u"Brachy_ani_dist_list")

    w.gridLayout_53.addWidget(w.Brachy_ani_dist_list, 4, 7, 1, 1)

    w.verticalSpacer_17 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_53.addItem(w.verticalSpacer_17, 8, 8, 1, 1)

    w.horizontalSpacer_56 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_53.addItem(w.horizontalSpacer_56, 12, 3, 1, 1)

    w.verticalSpacer_13 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_53.addItem(w.verticalSpacer_13, 1, 8, 1, 1)

    w.verticalSpacer_15 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_53.addItem(w.verticalSpacer_15, 3, 8, 1, 1)

    w.Brachy_ani_dist_label = QLineEdit(w.Brachy_tab_46)
    w.Brachy_ani_dist_label.setObjectName(u"Brachy_ani_dist_label")
    w.Brachy_ani_dist_label.setEnabled(False)

    w.gridLayout_53.addWidget(w.Brachy_ani_dist_label, 4, 6, 1, 1)

    w.Brachy_ani_table = QTableWidget(w.Brachy_tab_46)
    w.Brachy_ani_table.setObjectName(u"Brachy_ani_table")

    w.gridLayout_53.addWidget(w.Brachy_ani_table, 0, 0, 4, 8)

    w.verticalSpacer_18 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_53.addItem(w.verticalSpacer_18, 10, 8, 1, 1)

    w.horizontalSpacer_57 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_53.addItem(w.horizontalSpacer_57, 12, 7, 1, 1)

    w.verticalSpacer_12 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_53.addItem(w.verticalSpacer_12, 0, 8, 1, 1)

    w.horizontalSpacer_58 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_53.addItem(w.horizontalSpacer_58, 12, 6, 1, 1)

    w.horizontalSpacer_55 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_53.addItem(w.horizontalSpacer_55, 12, 0, 1, 1)

    w.horizontalSpacer_59 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_53.addItem(w.horizontalSpacer_59, 12, 5, 1, 1)

    w.verticalSpacer_14 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_53.addItem(w.verticalSpacer_14, 2, 8, 1, 1)

    w.verticalSpacer_16 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_53.addItem(w.verticalSpacer_16, 6, 8, 1, 1)

    w.horizontalSpacer_60 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_53.addItem(w.horizontalSpacer_60, 12, 4, 1, 1)

    w.Brachy_load_ani = QPushButton(w.Brachy_tab_46)
    w.Brachy_load_ani.setObjectName(u"Brachy_load_ani")

    w.gridLayout_53.addWidget(w.Brachy_load_ani, 11, 7, 1, 1)

    w.Brach_plot_ani = QPushButton(w.Brachy_tab_46)
    w.Brach_plot_ani.setObjectName(u"Brach_plot_ani")

    w.gridLayout_53.addWidget(w.Brach_plot_ani, 5, 7, 1, 1)

    w.Brachy_ani_plot_hold = QCheckBox(w.Brachy_tab_46)
    w.Brachy_ani_plot_hold.setObjectName(u"Brachy_ani_plot_hold")

    w.gridLayout_53.addWidget(w.Brachy_ani_plot_hold, 5, 6, 1, 1)

    w.Brachy_ani_axes = QWidget(w.Brachy_tab_46)
    w.Brachy_ani_axes.setObjectName(u"Brachy_ani_axes")

    w.gridLayout_53.addWidget(w.Brachy_ani_axes, 4, 0, 8, 6)

    w.tabWidget_2.addTab(w.Brachy_tab_46, "")
    w.tab_36 = QWidget()
    w.tab_36.setObjectName(u"tab_36")
    w.gridLayout_55 = QGridLayout(w.tab_36)
    w.gridLayout_55.setObjectName(u"gridLayout_55")
    w.comboBox_tg43_along_away = QComboBox(w.tab_36)
    w.comboBox_tg43_along_away.setObjectName(u"comboBox_tg43_along_away")

    w.gridLayout_55.addWidget(w.comboBox_tg43_along_away, 2, 1, 1, 1)

    w.horizontalSpacer_43 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_55.addItem(w.horizontalSpacer_43, 2, 0, 1, 1)

    w.TG43_along_away = QTableWidget(w.tab_36)
    w.TG43_along_away.setObjectName(u"TG43_along_away")

    w.gridLayout_55.addWidget(w.TG43_along_away, 1, 0, 1, 2)

    w.tabWidget_2.addTab(w.tab_36, "")
    w.DECT_tab_47 = QWidget()
    w.DECT_tab_47.setObjectName(u"DECT_tab_47")
    w.gridLayout_54 = QGridLayout(w.DECT_tab_47)
    w.gridLayout_54.setObjectName(u"gridLayout_54")
    w.horizontalSpacer_62 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_54.addItem(w.horizontalSpacer_62, 2, 0, 1, 1)

    w.horizontalSpacer_63 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_54.addItem(w.horizontalSpacer_63, 2, 4, 1, 1)

    w.horizontalSpacer_65 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_54.addItem(w.horizontalSpacer_65, 2, 2, 1, 1)

    w.horizontalSpacer_64 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_54.addItem(w.horizontalSpacer_64, 2, 3, 1, 1)

    w.horizontalSpacer_66 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_54.addItem(w.horizontalSpacer_66, 2, 1, 1, 1)

    w.Brachy_cal_table = QTableWidget(w.DECT_tab_47)
    w.Brachy_cal_table.setObjectName(u"Brachy_cal_table")

    w.gridLayout_54.addWidget(w.Brachy_cal_table, 0, 0, 1, 2)

    w.Brachy_cal_add_line = QPushButton(w.DECT_tab_47)
    w.Brachy_cal_add_line.setObjectName(u"Brachy_cal_add_line")

    w.gridLayout_54.addWidget(w.Brachy_cal_add_line, 1, 0, 1, 1)

    w.Brachy_cal_Delete_line = QPushButton(w.DECT_tab_47)
    w.Brachy_cal_Delete_line.setObjectName(u"Brachy_cal_Delete_line")

    w.gridLayout_54.addWidget(w.Brachy_cal_Delete_line, 1, 1, 1, 1)

    w.tabWidget_2.addTab(w.DECT_tab_47, "")

    w.gridLayout_51.addWidget(w.tabWidget_2, 0, 0, 1, 6)

    w.Brachy_doseRate_label = QLineEdit(w.Br_tab_43)
    w.Brachy_doseRate_label.setObjectName(u"Brachy_doseRate_label")
    w.Brachy_doseRate_label.setEnabled(False)
    w.Brachy_doseRate_label.setFont(font)

    w.gridLayout_51.addWidget(w.Brachy_doseRate_label, 3, 2, 1, 1)

    w.Brachy_rad_leng_label = QLineEdit(w.Br_tab_43)
    w.Brachy_rad_leng_label.setObjectName(u"Brachy_rad_leng_label")
    w.Brachy_rad_leng_label.setEnabled(False)
    w.Brachy_rad_leng_label.setFont(font)

    w.gridLayout_51.addWidget(w.Brachy_rad_leng_label, 4, 2, 1, 1)

    w.Brachy_dose_rate_cte_value = QLineEdit(w.Br_tab_43)
    w.Brachy_dose_rate_cte_value.setObjectName(u"Brachy_dose_rate_cte_value")
    w.Brachy_dose_rate_cte_value.setFont(font)

    w.gridLayout_51.addWidget(w.Brachy_dose_rate_cte_value, 3, 3, 1, 1)

    w.Brachy_rad_leng = QLineEdit(w.Br_tab_43)
    w.Brachy_rad_leng.setObjectName(u"Brachy_rad_leng")
    w.Brachy_rad_leng.setFont(font)

    w.gridLayout_51.addWidget(w.Brachy_rad_leng, 4, 3, 1, 1)

    w.Tg43_matrix_size = QGroupBox(w.Br_tab_43)
    w.Tg43_matrix_size.setObjectName(u"Tg43_matrix_size")
    w.gridLayout_56 = QGridLayout(w.Tg43_matrix_size)
    w.gridLayout_56.setObjectName(u"gridLayout_56")
    w.Tg43_dose_grid = QComboBox(w.Tg43_matrix_size)
    w.Tg43_dose_grid.setObjectName(u"Tg43_dose_grid")

    w.gridLayout_56.addWidget(w.Tg43_dose_grid, 0, 1, 1, 1)

    w.Tg43_matrix_size_2 = QComboBox(w.Tg43_matrix_size)
    w.Tg43_matrix_size_2.setObjectName(u"Tg43_matrix_size_2")

    w.gridLayout_56.addWidget(w.Tg43_matrix_size_2, 1, 1, 1, 1)

    w.lineEdit_tg43_01 = QLineEdit(w.Tg43_matrix_size)
    w.lineEdit_tg43_01.setObjectName(u"lineEdit_tg43_01")
    w.lineEdit_tg43_01.setEnabled(False)

    w.gridLayout_56.addWidget(w.lineEdit_tg43_01, 0, 0, 1, 1)

    w.lineEdit_tg43_02 = QLineEdit(w.Tg43_matrix_size)
    w.lineEdit_tg43_02.setObjectName(u"lineEdit_tg43_02")
    w.lineEdit_tg43_02.setEnabled(False)

    w.gridLayout_56.addWidget(w.lineEdit_tg43_02, 1, 0, 1, 1)


    w.gridLayout_51.addWidget(w.Tg43_matrix_size, 3, 4, 2, 1)

    w.BrachytabWidget_2.addTab(w.Br_tab_43, "")

    w.gridLayout_43.addWidget(w.BrachytabWidget_2, 0, 1, 1, 1)

    w.Plan_tabs.addTab(w.Brachy_plan_tab, "")
    w.eqd2 = QWidget()
    w.eqd2.setObjectName(u"eqd2")
    w.dose_matri_to_eqd2 = QGroupBox(w.eqd2)
    w.dose_matri_to_eqd2.setObjectName(u"dose_matri_to_eqd2")
    w.dose_matri_to_eqd2.setGeometry(QRect(9, 9, 1543, 511))
    w.layoutWidget = QWidget(w.dose_matri_to_eqd2)
    w.layoutWidget.setObjectName(u"layoutWidget")
    w.layoutWidget.setGeometry(QRect(10, 20, 451, 30))
    w.horizontalLayout = QHBoxLayout(w.layoutWidget)
    w.horizontalLayout.setSpacing(8)
    w.horizontalLayout.setObjectName(u"horizontalLayout")
    w.horizontalLayout.setContentsMargins(0, 0, 0, 0)
    w.eqd2_lab1 = QLabel(w.layoutWidget)
    w.eqd2_lab1.setObjectName(u"eqd2_lab1")

    w.horizontalLayout.addWidget(w.eqd2_lab1)

    w.dose_list = QComboBox(w.layoutWidget)
    w.dose_list.setObjectName(u"dose_list")

    w.horizontalLayout.addWidget(w.dose_list)

    w.horizontalLayout.setStretch(1, 3)
    w.layoutWidget1 = QWidget(w.dose_matri_to_eqd2)
    w.layoutWidget1.setObjectName(u"layoutWidget1")
    w.layoutWidget1.setGeometry(QRect(10, 70, 771, 61))
    w.chose_struct = QHBoxLayout(w.layoutWidget1)
    w.chose_struct.setSpacing(8)
    w.chose_struct.setObjectName(u"chose_struct")
    w.chose_struct.setContentsMargins(0, 0, 0, 0)
    w.eqd2_lab1_2 = QLabel(w.layoutWidget1)
    w.eqd2_lab1_2.setObjectName(u"eqd2_lab1_2")

    w.chose_struct.addWidget(w.eqd2_lab1_2)

    w.eqd2_struct_list = QComboBox(w.layoutWidget1)
    w.eqd2_struct_list.setObjectName(u"eqd2_struct_list")

    w.chose_struct.addWidget(w.eqd2_struct_list)

    w.horizontalSpacer_47 = QSpacerItem(58, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

    w.chose_struct.addItem(w.horizontalSpacer_47)

    w.eqd2_lab1_3 = QLabel(w.layoutWidget1)
    w.eqd2_lab1_3.setObjectName(u"eqd2_lab1_3")

    w.chose_struct.addWidget(w.eqd2_lab1_3)

    w.ab_input = QLineEdit(w.layoutWidget1)
    w.ab_input.setObjectName(u"ab_input")

    w.chose_struct.addWidget(w.ab_input)

    w.add_to_ab_list = QPushButton(w.layoutWidget1)
    w.add_to_ab_list.setObjectName(u"add_to_ab_list")

    w.chose_struct.addWidget(w.add_to_ab_list)

    w.delete_from_ab_list = QPushButton(w.layoutWidget1)
    w.delete_from_ab_list.setObjectName(u"delete_from_ab_list")

    w.chose_struct.addWidget(w.delete_from_ab_list)

    w.chose_struct.setStretch(1, 8)
    w.layoutWidget2 = QWidget(w.dose_matri_to_eqd2)
    w.layoutWidget2.setObjectName(u"layoutWidget2")
    w.layoutWidget2.setGeometry(QRect(10, 140, 681, 331))
    w.laststep = QHBoxLayout(w.layoutWidget2)
    w.laststep.setSpacing(8)
    w.laststep.setObjectName(u"laststep")
    w.laststep.setContentsMargins(0, 0, 0, 0)
    w.ab_table = QTableWidget(w.layoutWidget2)
    w.ab_table.setObjectName(u"ab_table")

    w.laststep.addWidget(w.ab_table)

    w.n_fractions_label = QLabel(w.layoutWidget2)
    w.n_fractions_label.setObjectName(u"n_fractions_label")

    w.laststep.addWidget(w.n_fractions_label)

    w.input_fractions = QLineEdit(w.layoutWidget2)
    w.input_fractions.setObjectName(u"input_fractions")

    w.laststep.addWidget(w.input_fractions)

    w.calc_eqd2 = QPushButton(w.layoutWidget2)
    w.calc_eqd2.setObjectName(u"calc_eqd2")

    w.laststep.addWidget(w.calc_eqd2)

    w.ab_matrix = QPushButton(w.dose_matri_to_eqd2)
    w.ab_matrix.setObjectName(u"ab_matrix")
    w.ab_matrix.setGeometry(QRect(10, 480, 261, 28))
    w.eqd2_calc = QGroupBox(w.eqd2)
    w.eqd2_calc.setObjectName(u"eqd2_calc")
    w.eqd2_calc.setGeometry(QRect(10, 540, 1543, 451))
    w.eqd2_out = QLCDNumber(w.eqd2_calc)
    w.eqd2_out.setObjectName(u"eqd2_out")
    w.eqd2_out.setGeometry(QRect(240, 100, 131, 51))
    w.label_1_eqd2_calc_5 = QLabel(w.eqd2_calc)
    w.label_1_eqd2_calc_5.setObjectName(u"label_1_eqd2_calc_5")
    w.label_1_eqd2_calc_5.setGeometry(QRect(390, 100, 91, 51))
    font3 = QFont()
    font3.setPointSize(28)
    w.label_1_eqd2_calc_5.setFont(font3)
    w.label_1_eqd2_calc_5.setScaledContents(True)
    w.layoutWidget3 = QWidget(w.eqd2_calc)
    w.layoutWidget3.setObjectName(u"layoutWidget3")
    w.layoutWidget3.setGeometry(QRect(10, 50, 704, 30))
    w.horizontalLayout_2 = QHBoxLayout(w.layoutWidget3)
    w.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
    w.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
    w.label_1_eqd2_calc_2 = QLabel(w.layoutWidget3)
    w.label_1_eqd2_calc_2.setObjectName(u"label_1_eqd2_calc_2")

    w.horizontalLayout_2.addWidget(w.label_1_eqd2_calc_2)

    w.input_total_dose = QLineEdit(w.layoutWidget3)
    w.input_total_dose.setObjectName(u"input_total_dose")

    w.horizontalLayout_2.addWidget(w.input_total_dose)

    w.label_1_eqd2_calc_3 = QLabel(w.layoutWidget3)
    w.label_1_eqd2_calc_3.setObjectName(u"label_1_eqd2_calc_3")

    w.horizontalLayout_2.addWidget(w.label_1_eqd2_calc_3)

    w.input_ab_calculator = QLineEdit(w.layoutWidget3)
    w.input_ab_calculator.setObjectName(u"input_ab_calculator")

    w.horizontalLayout_2.addWidget(w.input_ab_calculator)

    w.label_1_eqd2_calc_4 = QLabel(w.layoutWidget3)
    w.label_1_eqd2_calc_4.setObjectName(u"label_1_eqd2_calc_4")

    w.horizontalLayout_2.addWidget(w.label_1_eqd2_calc_4)

    w.input_frac_calc = QLineEdit(w.layoutWidget3)
    w.input_frac_calc.setObjectName(u"input_frac_calc")

    w.horizontalLayout_2.addWidget(w.input_frac_calc)

    w.calc_eqd2_2 = QPushButton(w.layoutWidget3)
    w.calc_eqd2_2.setObjectName(u"calc_eqd2_2")

    w.horizontalLayout_2.addWidget(w.calc_eqd2_2)

    w.Plan_tabs.addTab(w.eqd2, "")
    w.Plan_Evaluation = QWidget()
    w.Plan_Evaluation.setObjectName(u"Plan_Evaluation")
    w.gridLayout_59 = QGridLayout(w.Plan_Evaluation)
    w.gridLayout_59.setObjectName(u"gridLayout_59")
    w.plan_eval_grid_left = QGridLayout()
    w.plan_eval_grid_left.setObjectName(u"plan_eval_grid_left")
    w.dose_unit_Gy = QCheckBox(w.Plan_Evaluation)
    w.dose_unit_Gy.setObjectName(u"dose_unit_Gy")

    w.plan_eval_grid_left.addWidget(w.dose_unit_Gy, 18, 2, 1, 1)

    w.HS_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_left.addItem(w.HS_6, 17, 1, 1, 1)

    w.DoseUnit = QLabel(w.Plan_Evaluation)
    w.DoseUnit.setObjectName(u"DoseUnit")

    w.plan_eval_grid_left.addWidget(w.DoseUnit, 17, 2, 1, 1)

    w.VolumeUnit = QLabel(w.Plan_Evaluation)
    w.VolumeUnit.setObjectName(u"VolumeUnit")

    w.plan_eval_grid_left.addWidget(w.VolumeUnit, 17, 0, 1, 1)

    w.HS_1 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_left.addItem(w.HS_1, 16, 1, 1, 1)

    w.struct_list_DVH = QListWidget(w.Plan_Evaluation)
    w.struct_list_DVH.setObjectName(u"struct_list_DVH")

    w.plan_eval_grid_left.addWidget(w.struct_list_DVH, 13, 0, 1, 3)

    w.button_calculate_dvhs = QPushButton(w.Plan_Evaluation)
    w.button_calculate_dvhs.setObjectName(u"button_calculate_dvhs")

    w.plan_eval_grid_left.addWidget(w.button_calculate_dvhs, 20, 2, 1, 1)

    w.select_dose = QLabel(w.Plan_Evaluation)
    w.select_dose.setObjectName(u"select_dose")

    w.plan_eval_grid_left.addWidget(w.select_dose, 2, 0, 1, 1)

    w.box_reference_dose = QLineEdit(w.Plan_Evaluation)
    w.box_reference_dose.setObjectName(u"box_reference_dose")

    w.plan_eval_grid_left.addWidget(w.box_reference_dose, 16, 2, 1, 1)

    w.HS_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_left.addItem(w.HS_2, 20, 0, 1, 2)

    w.volume_unit_percentage = QCheckBox(w.Plan_Evaluation)
    w.volume_unit_percentage.setObjectName(u"volume_unit_percentage")

    w.plan_eval_grid_left.addWidget(w.volume_unit_percentage, 19, 0, 1, 1)

    w.HS_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_left.addItem(w.HS_5, 18, 1, 1, 1)

    w.HS_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_left.addItem(w.HS_8, 6, 1, 1, 2)

    w.HS_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_left.addItem(w.HS_4, 19, 1, 1, 1)

    w.HS_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_left.addItem(w.HS_3, 14, 0, 1, 2)

    w.volume_unit_cm3 = QCheckBox(w.Plan_Evaluation)
    w.volume_unit_cm3.setObjectName(u"volume_unit_cm3")

    w.plan_eval_grid_left.addWidget(w.volume_unit_cm3, 18, 0, 1, 1)

    w.Structures = QLabel(w.Plan_Evaluation)
    w.Structures.setObjectName(u"Structures")

    w.plan_eval_grid_left.addWidget(w.Structures, 6, 0, 1, 1)

    w.HS_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_left.addItem(w.HS_7, 2, 1, 1, 2)

    w.dose_unit_percentage = QCheckBox(w.Plan_Evaluation)
    w.dose_unit_percentage.setObjectName(u"dose_unit_percentage")

    w.plan_eval_grid_left.addWidget(w.dose_unit_percentage, 19, 2, 1, 1)

    w.box_select_dose = QListWidget(w.Plan_Evaluation)
    w.box_select_dose.setObjectName(u"box_select_dose")

    w.plan_eval_grid_left.addWidget(w.box_select_dose, 4, 0, 1, 3)

    w.reference_dose = QLabel(w.Plan_Evaluation)
    w.reference_dose.setObjectName(u"reference_dose")

    w.plan_eval_grid_left.addWidget(w.reference_dose, 16, 0, 1, 1)

    w.button_update_select_dose = QPushButton(w.Plan_Evaluation)
    w.button_update_select_dose.setObjectName(u"button_update_select_dose")

    w.plan_eval_grid_left.addWidget(w.button_update_select_dose, 14, 2, 1, 1)

    w.horizontalline_left_grid = QFrame(w.Plan_Evaluation)
    w.horizontalline_left_grid.setObjectName(u"horizontalline_left_grid")
    w.horizontalline_left_grid.setFrameShape(QFrame.Shape.HLine)
    w.horizontalline_left_grid.setFrameShadow(QFrame.Shadow.Sunken)

    w.plan_eval_grid_left.addWidget(w.horizontalline_left_grid, 15, 0, 1, 3)

    w.plan_eval_grid_left.setColumnStretch(0, 3)
    w.plan_eval_grid_left.setColumnStretch(1, 1)
    w.plan_eval_grid_left.setColumnStretch(2, 3)

    w.gridLayout_59.addLayout(w.plan_eval_grid_left, 0, 0, 1, 1)

    w.plan_eval_grid_middle = QGridLayout()
    w.plan_eval_grid_middle.setObjectName(u"plan_eval_grid_middle")
    w.HS_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_middle.addItem(w.HS_11, 0, 2, 1, 2)

    w.DoseStatistics = QLabel(w.Plan_Evaluation)
    w.DoseStatistics.setObjectName(u"DoseStatistics")

    w.plan_eval_grid_middle.addWidget(w.DoseStatistics, 5, 0, 1, 1)

    w.verticalline_middle_grid = QFrame(w.Plan_Evaluation)
    w.verticalline_middle_grid.setObjectName(u"verticalline_middle_grid")
    w.verticalline_middle_grid.setFrameShape(QFrame.Shape.VLine)
    w.verticalline_middle_grid.setFrameShadow(QFrame.Shadow.Sunken)

    w.plan_eval_grid_middle.addWidget(w.verticalline_middle_grid, 9, 0, 1, 1)

    w.button_select_all_rows_DST = QPushButton(w.Plan_Evaluation)
    w.button_select_all_rows_DST.setObjectName(u"button_select_all_rows_DST")

    w.plan_eval_grid_middle.addWidget(w.button_select_all_rows_DST, 7, 0, 1, 1)

    w.view_dvhs = QGraphicsView(w.Plan_Evaluation)
    w.view_dvhs.setObjectName(u"view_dvhs")

    w.plan_eval_grid_middle.addWidget(w.view_dvhs, 1, 0, 1, 4)

    w.DVHs = QLabel(w.Plan_Evaluation)
    w.DVHs.setObjectName(u"DVHs")

    w.plan_eval_grid_middle.addWidget(w.DVHs, 0, 0, 1, 1)

    w.line_split_planevaluation_2 = QFrame(w.Plan_Evaluation)
    w.line_split_planevaluation_2.setObjectName(u"line_split_planevaluation_2")
    w.line_split_planevaluation_2.setFrameShape(QFrame.Shape.VLine)
    w.line_split_planevaluation_2.setFrameShadow(QFrame.Shadow.Sunken)

    w.plan_eval_grid_middle.addWidget(w.line_split_planevaluation_2, 4, 0, 1, 1)

    w.button_update_plot = QPushButton(w.Plan_Evaluation)
    w.button_update_plot.setObjectName(u"button_update_plot")

    w.plan_eval_grid_middle.addWidget(w.button_update_plot, 8, 0, 1, 1)

    w.table_dose_stats = QTableWidget(w.Plan_Evaluation)
    w.table_dose_stats.setObjectName(u"table_dose_stats")

    w.plan_eval_grid_middle.addWidget(w.table_dose_stats, 6, 0, 1, 4)

    w.line_split_planevaluation_3 = QFrame(w.Plan_Evaluation)
    w.line_split_planevaluation_3.setObjectName(u"line_split_planevaluation_3")
    w.line_split_planevaluation_3.setFrameShape(QFrame.Shape.HLine)
    w.line_split_planevaluation_3.setFrameShadow(QFrame.Shadow.Sunken)

    w.plan_eval_grid_middle.addWidget(w.line_split_planevaluation_3, 2, 0, 1, 4)

    w.HS_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_middle.addItem(w.HS_10, 5, 1, 1, 1)

    w.button_delete_column = QPushButton(w.Plan_Evaluation)
    w.button_delete_column.setObjectName(u"button_delete_column")

    w.plan_eval_grid_middle.addWidget(w.button_delete_column, 5, 2, 1, 2)

    w.HS_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_middle.addItem(w.HS_9, 8, 1, 1, 1)

    w.HS_17 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_middle.addItem(w.HS_17, 7, 1, 1, 1)

    w.button_export_dose_stats_to_excel = QPushButton(w.Plan_Evaluation)
    w.button_export_dose_stats_to_excel.setObjectName(u"button_export_dose_stats_to_excel")

    w.plan_eval_grid_middle.addWidget(w.button_export_dose_stats_to_excel, 8, 2, 1, 2)

    w.plan_eval_grid_middle.setRowStretch(1, 4)
    w.plan_eval_grid_middle.setRowStretch(2, 4)
    w.plan_eval_grid_middle.setColumnStretch(0, 1)
    w.plan_eval_grid_middle.setColumnStretch(1, 2)
    w.plan_eval_grid_middle.setColumnStretch(2, 1)

    w.gridLayout_59.addLayout(w.plan_eval_grid_middle, 0, 1, 1, 1)

    w.plan_eval_grid_right = QGridLayout()
    w.plan_eval_grid_right.setObjectName(u"plan_eval_grid_right")
    w.Dxx = QLabel(w.Plan_Evaluation)
    w.Dxx.setObjectName(u"Dxx")

    w.plan_eval_grid_right.addWidget(w.Dxx, 12, 0, 1, 1)

    w.vxx_input_dropdown = QComboBox(w.Plan_Evaluation)
    w.vxx_input_dropdown.setObjectName(u"vxx_input_dropdown")

    w.plan_eval_grid_right.addWidget(w.vxx_input_dropdown, 11, 1, 1, 1)

    w.vxx_t_label = QLabel(w.Plan_Evaluation)
    w.vxx_t_label.setObjectName(u"vxx_t_label")

    w.plan_eval_grid_right.addWidget(w.vxx_t_label, 11, 2, 1, 1)

    w.HS_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_right.addItem(w.HS_12, 16, 0, 1, 3)

    w.dxx_input_value = QLineEdit(w.Plan_Evaluation)
    w.dxx_input_value.setObjectName(u"dxx_input_value")

    w.plan_eval_grid_right.addWidget(w.dxx_input_value, 15, 0, 1, 1)

    w.HS_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_right.addItem(w.HS_13, 8, 0, 1, 4)

    w.dxx_input_dropdown = QComboBox(w.Plan_Evaluation)
    w.dxx_input_dropdown.setObjectName(u"dxx_input_dropdown")

    w.plan_eval_grid_right.addWidget(w.dxx_input_dropdown, 15, 1, 1, 1)

    w.button_calculate_vxx_dxx = QPushButton(w.Plan_Evaluation)
    w.button_calculate_vxx_dxx.setObjectName(u"button_calculate_vxx_dxx")

    w.plan_eval_grid_right.addWidget(w.button_calculate_vxx_dxx, 16, 3, 1, 1)

    w.HS_16 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_right.addItem(w.HS_16, 10, 1, 1, 3)

    w.vxx_input_value = QLineEdit(w.Plan_Evaluation)
    w.vxx_input_value.setObjectName(u"vxx_input_value")

    w.plan_eval_grid_right.addWidget(w.vxx_input_value, 11, 0, 1, 1)

    w.Vxx = QLabel(w.Plan_Evaluation)
    w.Vxx.setObjectName(u"Vxx")

    w.plan_eval_grid_right.addWidget(w.Vxx, 10, 0, 1, 1)

    w.dxx_output_dropdown = QComboBox(w.Plan_Evaluation)
    w.dxx_output_dropdown.setObjectName(u"dxx_output_dropdown")

    w.plan_eval_grid_right.addWidget(w.dxx_output_dropdown, 15, 3, 1, 1)

    w.dxx_to_label = QLabel(w.Plan_Evaluation)
    w.dxx_to_label.setObjectName(u"dxx_to_label")

    w.plan_eval_grid_right.addWidget(w.dxx_to_label, 15, 2, 1, 1)

    w.HS_14 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_right.addItem(w.HS_14, 12, 1, 1, 3)

    w.vxx_output_dropdown = QComboBox(w.Plan_Evaluation)
    w.vxx_output_dropdown.setObjectName(u"vxx_output_dropdown")

    w.plan_eval_grid_right.addWidget(w.vxx_output_dropdown, 11, 3, 1, 1)

    w.HS_15 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_right.addItem(w.HS_15, 17, 0, 1, 4)

    w.line_grid_right = QFrame(w.Plan_Evaluation)
    w.line_grid_right.setObjectName(u"line_grid_right")
    w.line_grid_right.setFrameShape(QFrame.Shape.HLine)
    w.line_grid_right.setFrameShadow(QFrame.Shadow.Sunken)

    w.plan_eval_grid_right.addWidget(w.line_grid_right, 7, 0, 1, 4)

    w.tab_errors = QTabWidget(w.Plan_Evaluation)
    w.tab_errors.setObjectName(u"tab_errors")
    w.uncertainty = QWidget()
    w.uncertainty.setObjectName(u"uncertainty")
    w.Mean = QLabel(w.uncertainty)
    w.Mean.setObjectName(u"Mean")
    w.Mean.setGeometry(QRect(80, 10, 69, 20))
    w.box_Y_std_input = QLineEdit(w.uncertainty)
    w.box_Y_std_input.setObjectName(u"box_Y_std_input")
    w.box_Y_std_input.setGeometry(QRect(210, 80, 81, 25))
    w.NumberOfInteractions = QLabel(w.uncertainty)
    w.NumberOfInteractions.setObjectName(u"NumberOfInteractions")
    w.NumberOfInteractions.setGeometry(QRect(0, 250, 171, 20))
    w.Y = QLabel(w.uncertainty)
    w.Y.setObjectName(u"Y")
    w.Y.setGeometry(QRect(0, 80, 31, 20))
    w.box_X_std_input = QLineEdit(w.uncertainty)
    w.box_X_std_input.setObjectName(u"box_X_std_input")
    w.box_X_std_input.setGeometry(QRect(210, 40, 81, 25))
    w.box_Z_mean_input = QLineEdit(w.uncertainty)
    w.box_Z_mean_input.setObjectName(u"box_Z_mean_input")
    w.box_Z_mean_input.setGeometry(QRect(70, 120, 81, 25))
    w.box_X_mean_input = QLineEdit(w.uncertainty)
    w.box_X_mean_input.setObjectName(u"box_X_mean_input")
    w.box_X_mean_input.setGeometry(QRect(70, 40, 81, 25))
    w.StandardDeviation = QLabel(w.uncertainty)
    w.StandardDeviation.setObjectName(u"StandardDeviation")
    w.StandardDeviation.setGeometry(QRect(210, 10, 69, 20))
    w.X = QLabel(w.uncertainty)
    w.X.setObjectName(u"X")
    w.X.setGeometry(QRect(0, 40, 31, 20))
    w.T = QLabel(w.uncertainty)
    w.T.setObjectName(u"T")
    w.T.setGeometry(QRect(0, 160, 31, 20))
    w.button_apply_uncertainty = QPushButton(w.uncertainty)
    w.button_apply_uncertainty.setObjectName(u"button_apply_uncertainty")
    w.button_apply_uncertainty.setGeometry(QRect(0, 310, 89, 28))
    w.box_T_mean_input = QLineEdit(w.uncertainty)
    w.box_T_mean_input.setObjectName(u"box_T_mean_input")
    w.box_T_mean_input.setGeometry(QRect(70, 160, 81, 25))
    w.box_Z_std_input = QLineEdit(w.uncertainty)
    w.box_Z_std_input.setObjectName(u"box_Z_std_input")
    w.box_Z_std_input.setGeometry(QRect(210, 120, 81, 25))
    w.box_T_std_input = QLineEdit(w.uncertainty)
    w.box_T_std_input.setObjectName(u"box_T_std_input")
    w.box_T_std_input.setGeometry(QRect(210, 160, 81, 25))
    w.box_Y_mean_input = QLineEdit(w.uncertainty)
    w.box_Y_mean_input.setObjectName(u"box_Y_mean_input")
    w.box_Y_mean_input.setGeometry(QRect(70, 80, 81, 25))
    w.Z = QLabel(w.uncertainty)
    w.Z.setObjectName(u"Z")
    w.Z.setGeometry(QRect(0, 120, 31, 20))
    w.box_number_of_interactions = QLineEdit(w.uncertainty)
    w.box_number_of_interactions.setObjectName(u"box_number_of_interactions")
    w.box_number_of_interactions.setGeometry(QRect(210, 250, 81, 25))
    w.button_show_uncertainty_bands = QPushButton(w.uncertainty)
    w.button_show_uncertainty_bands.setObjectName(u"button_show_uncertainty_bands")
    w.button_show_uncertainty_bands.setGeometry(QRect(0, 360, 89, 28))
    w.tab_errors.addTab(w.uncertainty, "")
    w.error_simulation = QWidget()
    w.error_simulation.setObjectName(u"error_simulation")
    w.tab_errors.addTab(w.error_simulation, "")

    w.plan_eval_grid_right.addWidget(w.tab_errors, 0, 0, 2, 4)

    w.Deviation_Metrics = QLabel(w.Plan_Evaluation)
    w.Deviation_Metrics.setObjectName(u"Deviation_Metrics")

    w.plan_eval_grid_right.addWidget(w.Deviation_Metrics, 9, 0, 1, 1)

    w.HS_18 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.plan_eval_grid_right.addItem(w.HS_18, 9, 1, 1, 3)

    w.plan_eval_grid_right.setRowStretch(0, 4)
    w.plan_eval_grid_right.setRowStretch(1, 7)
    w.plan_eval_grid_right.setRowStretch(10, 1)
    w.plan_eval_grid_right.setRowStretch(16, 1)
    w.plan_eval_grid_right.setRowStretch(17, 1)
    w.plan_eval_grid_right.setColumnStretch(0, 1)
    w.plan_eval_grid_right.setColumnStretch(1, 1)
    w.plan_eval_grid_right.setColumnStretch(2, 1)
    w.plan_eval_grid_right.setColumnStretch(3, 1)

    w.gridLayout_59.addLayout(w.plan_eval_grid_right, 0, 2, 1, 1)

    w.gridLayout_59.setColumnStretch(0, 1)
    w.gridLayout_59.setColumnStretch(1, 2)
    w.gridLayout_59.setColumnStretch(2, 1)
    w.Plan_tabs.addTab(w.Plan_Evaluation, "")
    w.tab_mat_assignment = QWidget()
    w.tab_mat_assignment.setObjectName(u"tab_mat_assignment")
    w.gridLayout_69 = QGridLayout(w.tab_mat_assignment)
    w.gridLayout_69.setObjectName(u"gridLayout_69")
    w.groupBox_mat_to_struct = QGroupBox(w.tab_mat_assignment)
    w.groupBox_mat_to_struct.setObjectName(u"groupBox_mat_to_struct")
    w.gridLayout_72 = QGridLayout(w.groupBox_mat_to_struct)
    w.gridLayout_72.setObjectName(u"gridLayout_72")
    w.mat_to_struct_tab = QTableWidget(w.groupBox_mat_to_struct)
    w.mat_to_struct_tab.setObjectName(u"mat_to_struct_tab")

    w.gridLayout_72.addWidget(w.mat_to_struct_tab, 0, 0, 1, 1)

    w.remove_mat_from_struct = QPushButton(w.groupBox_mat_to_struct)
    w.remove_mat_from_struct.setObjectName(u"remove_mat_from_struct")

    w.gridLayout_72.addWidget(w.remove_mat_from_struct, 1, 0, 1, 1)


    w.gridLayout_69.addWidget(w.groupBox_mat_to_struct, 1, 1, 1, 1)

    w.assign_mat = QGroupBox(w.tab_mat_assignment)
    w.assign_mat.setObjectName(u"assign_mat")
    w.gridLayout_5 = QGridLayout(w.assign_mat)
    w.gridLayout_5.setObjectName(u"gridLayout_5")
    w.mat_to_hu = QPushButton(w.assign_mat)
    w.mat_to_hu.setObjectName(u"mat_to_hu")

    w.gridLayout_5.addWidget(w.mat_to_hu, 0, 6, 1, 1)

    w.Select_mat = QComboBox(w.assign_mat)
    w.Select_mat.setObjectName(u"Select_mat")

    w.gridLayout_5.addWidget(w.Select_mat, 0, 0, 1, 2)

    w.HU_high = QLineEdit(w.assign_mat)
    w.HU_high.setObjectName(u"HU_high")

    w.gridLayout_5.addWidget(w.HU_high, 0, 5, 1, 1)

    w.label_mat_2 = QLabel(w.assign_mat)
    w.label_mat_2.setObjectName(u"label_mat_2")

    w.gridLayout_5.addWidget(w.label_mat_2, 0, 4, 1, 1)

    w.HU_low = QLineEdit(w.assign_mat)
    w.HU_low.setObjectName(u"HU_low")

    w.gridLayout_5.addWidget(w.HU_low, 0, 3, 1, 1)

    w.label_mat = QLabel(w.assign_mat)
    w.label_mat.setObjectName(u"label_mat")

    w.gridLayout_5.addWidget(w.label_mat, 0, 2, 1, 1)

    w.Struct_list_mat = QComboBox(w.assign_mat)
    w.Struct_list_mat.setObjectName(u"Struct_list_mat")

    w.gridLayout_5.addWidget(w.Struct_list_mat, 2, 0, 1, 2)

    w.mat_to_struct = QPushButton(w.assign_mat)
    w.mat_to_struct.setObjectName(u"mat_to_struct")

    w.gridLayout_5.addWidget(w.mat_to_struct, 2, 2, 1, 3)

    w.update_mat_struct_list = QPushButton(w.assign_mat)
    w.update_mat_struct_list.setObjectName(u"update_mat_struct_list")

    w.gridLayout_5.addWidget(w.update_mat_struct_list, 2, 5, 1, 2)

    w.gridLayout_5.setColumnStretch(0, 10)
    w.gridLayout_5.setColumnStretch(1, 1)
    w.gridLayout_5.setColumnStretch(2, 1)
    w.gridLayout_5.setColumnStretch(3, 1)
    w.gridLayout_5.setColumnStretch(4, 1)
    w.gridLayout_5.setColumnStretch(5, 1)
    w.gridLayout_5.setColumnStretch(6, 1)

    w.gridLayout_69.addWidget(w.assign_mat, 0, 0, 1, 2)

    w.groupBox_mat_properties = QGroupBox(w.tab_mat_assignment)
    w.groupBox_mat_properties.setObjectName(u"groupBox_mat_properties")
    w.gridLayout_68 = QGridLayout(w.groupBox_mat_properties)
    w.gridLayout_68.setObjectName(u"gridLayout_68")
    w.element = QLineEdit(w.groupBox_mat_properties)
    w.element.setObjectName(u"element")

    w.gridLayout_68.addWidget(w.element, 2, 0, 1, 2)

    w.Add_mat = QPushButton(w.groupBox_mat_properties)
    w.Add_mat.setObjectName(u"Add_mat")

    w.gridLayout_68.addWidget(w.Add_mat, 1, 0, 1, 1)

    w.add_element = QPushButton(w.groupBox_mat_properties)
    w.add_element.setObjectName(u"add_element")

    w.gridLayout_68.addWidget(w.add_element, 2, 2, 1, 1)

    w.del_element = QPushButton(w.groupBox_mat_properties)
    w.del_element.setObjectName(u"del_element")

    w.gridLayout_68.addWidget(w.del_element, 2, 3, 1, 1)

    w.hs_mat_2 = QSpacerItem(295, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_68.addItem(w.hs_mat_2, 1, 2, 1, 2)

    w.del_mat = QPushButton(w.groupBox_mat_properties)
    w.del_mat.setObjectName(u"del_mat")

    w.gridLayout_68.addWidget(w.del_mat, 1, 1, 1, 1)

    w.mat_table = QTableWidget(w.groupBox_mat_properties)
    w.mat_table.setObjectName(u"mat_table")

    w.gridLayout_68.addWidget(w.mat_table, 0, 0, 1, 6)

    w.save_mat_table = QPushButton(w.groupBox_mat_properties)
    w.save_mat_table.setObjectName(u"save_mat_table")

    w.gridLayout_68.addWidget(w.save_mat_table, 1, 4, 1, 2)

    w.undo_mat_tab = QPushButton(w.groupBox_mat_properties)
    w.undo_mat_tab.setObjectName(u"undo_mat_tab")

    w.gridLayout_68.addWidget(w.undo_mat_tab, 2, 4, 1, 2)


    w.gridLayout_69.addWidget(w.groupBox_mat_properties, 0, 2, 5, 1)

    w.mat_to_HU_box = QGroupBox(w.tab_mat_assignment)
    w.mat_to_HU_box.setObjectName(u"mat_to_HU_box")
    w.gridLayout_71 = QGridLayout(w.mat_to_HU_box)
    w.gridLayout_71.setObjectName(u"gridLayout_71")
    w.tableMatToHU = QTableWidget(w.mat_to_HU_box)
    w.tableMatToHU.setObjectName(u"tableMatToHU")

    w.gridLayout_71.addWidget(w.tableMatToHU, 0, 0, 1, 1)

    w.remove_mat_fromhu = QPushButton(w.mat_to_HU_box)
    w.remove_mat_fromhu.setObjectName(u"remove_mat_fromhu")

    w.gridLayout_71.addWidget(w.remove_mat_fromhu, 1, 0, 1, 1)


    w.gridLayout_69.addWidget(w.mat_to_HU_box, 1, 0, 1, 1)

    w.del_mat_map = QPushButton(w.tab_mat_assignment)
    w.del_mat_map.setObjectName(u"del_mat_map")

    w.gridLayout_69.addWidget(w.del_mat_map, 2, 1, 1, 1)

    w.create_mat_map = QPushButton(w.tab_mat_assignment)
    w.create_mat_map.setObjectName(u"create_mat_map")

    w.gridLayout_69.addWidget(w.create_mat_map, 2, 0, 1, 1)

    w.gridLayout_69.setRowStretch(0, 1)
    w.gridLayout_69.setRowStretch(1, 10)
    w.gridLayout_69.setRowStretch(2, 1)
    w.gridLayout_69.setColumnStretch(0, 1)
    w.gridLayout_69.setColumnStretch(1, 1)
    w.gridLayout_69.setColumnStretch(2, 4)
    w.Plan_tabs.addTab(w.tab_mat_assignment, "")
    w.density_map_tab = QWidget()
    w.density_map_tab.setObjectName(u"density_map_tab")
    w.gridLayout_58 = QGridLayout(w.density_map_tab)
    w.gridLayout_58.setObjectName(u"gridLayout_58")
    w.ct_cal_input = QWidget(w.density_map_tab)
    w.ct_cal_input.setObjectName(u"ct_cal_input")
    w.gridLayout_57 = QGridLayout(w.ct_cal_input)
    w.gridLayout_57.setObjectName(u"gridLayout_57")
    w.save_changes_ct_cal = QPushButton(w.ct_cal_input)
    w.save_changes_ct_cal.setObjectName(u"save_changes_ct_cal")

    w.gridLayout_57.addWidget(w.save_changes_ct_cal, 1, 0, 1, 1)

    w.ct_cal_table = QTableWidget(w.ct_cal_input)
    w.ct_cal_table.setObjectName(u"ct_cal_table")

    w.gridLayout_57.addWidget(w.ct_cal_table, 2, 0, 1, 2)

    w.Export_ct_cal = QPushButton(w.ct_cal_input)
    w.Export_ct_cal.setObjectName(u"Export_ct_cal")

    w.gridLayout_57.addWidget(w.Export_ct_cal, 1, 1, 1, 1)

    w.load_ct_cal = QPushButton(w.ct_cal_input)
    w.load_ct_cal.setObjectName(u"load_ct_cal")

    w.gridLayout_57.addWidget(w.load_ct_cal, 0, 1, 1, 1)

    w.ct_cal_save_copy = QPushButton(w.ct_cal_input)
    w.ct_cal_save_copy.setObjectName(u"ct_cal_save_copy")

    w.gridLayout_57.addWidget(w.ct_cal_save_copy, 3, 1, 1, 1)

    w.ct_cal_list = QComboBox(w.ct_cal_input)
    w.ct_cal_list.setObjectName(u"ct_cal_list")
    w.ct_cal_list.setEditable(True)

    w.gridLayout_57.addWidget(w.ct_cal_list, 0, 0, 1, 1)

    w.ct_cal_add_row = QPushButton(w.ct_cal_input)
    w.ct_cal_add_row.setObjectName(u"ct_cal_add_row")

    w.gridLayout_57.addWidget(w.ct_cal_add_row, 3, 0, 1, 1)


    w.gridLayout_58.addWidget(w.ct_cal_input, 0, 0, 1, 2)

    w.ct_cal_plot = QWidget(w.density_map_tab)
    w.ct_cal_plot.setObjectName(u"ct_cal_plot")

    w.gridLayout_58.addWidget(w.ct_cal_plot, 0, 2, 1, 1)

    w.create_density_map = QPushButton(w.density_map_tab)
    w.create_density_map.setObjectName(u"create_density_map")

    w.gridLayout_58.addWidget(w.create_density_map, 1, 0, 1, 1)

    w.create_density_map__from_mat_map = QPushButton(w.density_map_tab)
    w.create_density_map__from_mat_map.setObjectName(u"create_density_map__from_mat_map")

    w.gridLayout_58.addWidget(w.create_density_map__from_mat_map, 2, 0, 1, 1)

    w.vspacer_ct_cal = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_58.addItem(w.vspacer_ct_cal, 3, 0, 1, 1)

    w.delete_density_map = QPushButton(w.density_map_tab)
    w.delete_density_map.setObjectName(u"delete_density_map")

    w.gridLayout_58.addWidget(w.delete_density_map, 2, 1, 1, 1)

    w.override_no_tissue = QCheckBox(w.density_map_tab)
    w.override_no_tissue.setObjectName(u"override_no_tissue")

    w.gridLayout_58.addWidget(w.override_no_tissue, 1, 1, 1, 1)

    w.gridLayout_58.setRowStretch(0, 6)
    w.gridLayout_58.setRowStretch(1, 2)
    w.gridLayout_58.setRowStretch(2, 2)
    w.gridLayout_58.setColumnStretch(0, 1)
    w.gridLayout_58.setColumnStretch(1, 1)
    w.gridLayout_58.setColumnStretch(2, 6)
    w.Plan_tabs.addTab(w.density_map_tab, "")

    w.gridLayout_42.addWidget(w.Plan_tabs, 0, 0, 1, 1)

