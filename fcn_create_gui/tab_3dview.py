# -*- coding: utf-8 -*-
"""
tab_3dview.py - AMIGOpy GUI Module
=====================================

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


def create_tab_3dview(w):
    """
    Create the 3D View module tab (_3Dview).

    Creates the 3D volume rendering interface:
    - Render controls group box (quality, brightness, specular, lighting, shading)
    - VTK 3D render window container (View3D_VTK_view)
    - tabWidget_3Dview with sub-tabs:
      * Structures: structure tree and visibility controls
      * Surfaces: surface rendering controls
      * Plan_Brachy: brachytherapy plan 3D view
      * Plan_Proton: proton plan 3D view

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
    w._3Dview = QWidget()
    w._3Dview.setObjectName(u"_3Dview")
    w.gridLayout_63 = QGridLayout(w._3Dview)
    w.gridLayout_63.setObjectName(u"gridLayout_63")
    w.View3DgroupBox_12 = QGroupBox(w._3Dview)
    w.View3DgroupBox_12.setObjectName(u"View3DgroupBox_12")
    w.gridLayout_65 = QGridLayout(w.View3DgroupBox_12)
    w.gridLayout_65.setObjectName(u"gridLayout_65")
    w.View3D_name_02 = QLineEdit(w.View3DgroupBox_12)
    w.View3D_name_02.setObjectName(u"View3D_name_02")
    w.View3D_name_02.setEnabled(False)

    w.gridLayout_65.addWidget(w.View3D_name_02, 1, 0, 1, 1)

    w.View3D_name_04 = QLineEdit(w.View3DgroupBox_12)
    w.View3D_name_04.setObjectName(u"View3D_name_04")
    w.View3D_name_04.setEnabled(False)

    w.gridLayout_65.addWidget(w.View3D_name_04, 3, 0, 1, 1)

    w.View3D_clear_all = QPushButton(w.View3DgroupBox_12)
    w.View3D_clear_all.setObjectName(u"View3D_clear_all")
    w.View3D_clear_all.setEnabled(True)

    w.gridLayout_65.addWidget(w.View3D_clear_all, 6, 2, 1, 1)

    w.View3D_quality_spin_01 = QDoubleSpinBox(w.View3DgroupBox_12)
    w.View3D_quality_spin_01.setObjectName(u"View3D_quality_spin_01")
    w.View3D_quality_spin_01.setEnabled(False)

    w.gridLayout_65.addWidget(w.View3D_quality_spin_01, 0, 2, 1, 1)

    w.View3D_quality_slider = QSlider(w.View3DgroupBox_12)
    w.View3D_quality_slider.setObjectName(u"View3D_quality_slider")
    w.View3D_quality_slider.setEnabled(False)
    w.View3D_quality_slider.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_65.addWidget(w.View3D_quality_slider, 0, 1, 1, 1)

    w.View3D_reset_camera = QPushButton(w.View3DgroupBox_12)
    w.View3D_reset_camera.setObjectName(u"View3D_reset_camera")
    w.View3D_reset_camera.setEnabled(True)

    w.gridLayout_65.addWidget(w.View3D_reset_camera, 6, 1, 1, 1)

    w.View3D_name_05 = QLineEdit(w.View3DgroupBox_12)
    w.View3D_name_05.setObjectName(u"View3D_name_05")
    w.View3D_name_05.setEnabled(False)

    w.gridLayout_65.addWidget(w.View3D_name_05, 4, 0, 1, 1)

    w.View3D_name_01 = QLineEdit(w.View3DgroupBox_12)
    w.View3D_name_01.setObjectName(u"View3D_name_01")
    w.View3D_name_01.setEnabled(False)

    w.gridLayout_65.addWidget(w.View3D_name_01, 0, 0, 1, 1)

    w.View3D_brightness_slider = QSlider(w.View3DgroupBox_12)
    w.View3D_brightness_slider.setObjectName(u"View3D_brightness_slider")
    w.View3D_brightness_slider.setEnabled(False)
    w.View3D_brightness_slider.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_65.addWidget(w.View3D_brightness_slider, 1, 1, 1, 1)

    w.View3D_name_03 = QLineEdit(w.View3DgroupBox_12)
    w.View3D_name_03.setObjectName(u"View3D_name_03")
    w.View3D_name_03.setEnabled(False)

    w.gridLayout_65.addWidget(w.View3D_name_03, 2, 0, 1, 1)

    w.View3D_brightness_spin_01 = QDoubleSpinBox(w.View3DgroupBox_12)
    w.View3D_brightness_spin_01.setObjectName(u"View3D_brightness_spin_01")
    w.View3D_brightness_spin_01.setEnabled(False)

    w.gridLayout_65.addWidget(w.View3D_brightness_spin_01, 1, 2, 1, 1)

    w.iew3D_lighting_options = QComboBox(w.View3DgroupBox_12)
    w.iew3D_lighting_options.setObjectName(u"iew3D_lighting_options")

    w.gridLayout_65.addWidget(w.iew3D_lighting_options, 4, 1, 1, 2)

    w.View3D_render_options = QComboBox(w.View3DgroupBox_12)
    w.View3D_render_options.setObjectName(u"View3D_render_options")

    w.gridLayout_65.addWidget(w.View3D_render_options, 3, 1, 1, 2)

    w.View3D_specular_spin_01 = QDoubleSpinBox(w.View3DgroupBox_12)
    w.View3D_specular_spin_01.setObjectName(u"View3D_specular_spin_01")
    w.View3D_specular_spin_01.setEnabled(False)

    w.gridLayout_65.addWidget(w.View3D_specular_spin_01, 2, 2, 1, 1)

    w.View3D_specular_slider = QSlider(w.View3DgroupBox_12)
    w.View3D_specular_slider.setObjectName(u"View3D_specular_slider")
    w.View3D_specular_slider.setEnabled(False)
    w.View3D_specular_slider.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_65.addWidget(w.View3D_specular_slider, 2, 1, 1, 1)

    w.View3D_shading_checkBox = QCheckBox(w.View3DgroupBox_12)
    w.View3D_shading_checkBox.setObjectName(u"View3D_shading_checkBox")
    w.View3D_shading_checkBox.setEnabled(False)

    w.gridLayout_65.addWidget(w.View3D_shading_checkBox, 5, 0, 1, 1)

    w.View3D_shoiw_axes_checkBox = QCheckBox(w.View3DgroupBox_12)
    w.View3D_shoiw_axes_checkBox.setObjectName(u"View3D_shoiw_axes_checkBox")
    w.View3D_shoiw_axes_checkBox.setEnabled(False)

    w.gridLayout_65.addWidget(w.View3D_shoiw_axes_checkBox, 5, 1, 1, 1)

    w.View3D_annotation_checkBox = QCheckBox(w.View3DgroupBox_12)
    w.View3D_annotation_checkBox.setObjectName(u"View3D_annotation_checkBox")
    w.View3D_annotation_checkBox.setEnabled(False)

    w.gridLayout_65.addWidget(w.View3D_annotation_checkBox, 5, 2, 1, 1)


    w.gridLayout_63.addWidget(w.View3DgroupBox_12, 0, 3, 1, 1)

    w.View3DhorizontalSpacer_78 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_63.addItem(w.View3DhorizontalSpacer_78, 3, 3, 1, 1)

    w.View3DverticalSpacer_22 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_63.addItem(w.View3DverticalSpacer_22, 2, 0, 1, 1)

    w.View3DverticalSpacer_21 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_63.addItem(w.View3DverticalSpacer_21, 0, 0, 1, 1)

    w.View3DhorizontalSpacer_79 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_63.addItem(w.View3DhorizontalSpacer_79, 3, 2, 1, 1)

    w.View3DhorizontalSpacer_77 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_63.addItem(w.View3DhorizontalSpacer_77, 3, 1, 1, 1)

    w.VTK_view_3D = QWidget(w._3Dview)
    w.VTK_view_3D.setObjectName(u"VTK_view_3D")

    w.gridLayout_63.addWidget(w.VTK_view_3D, 0, 1, 2, 2)

    w.tabWidget_3Dview = QTabWidget(w._3Dview)
    w.tabWidget_3Dview.setObjectName(u"tabWidget_3Dview")
    w.tab_40 = QWidget()
    w.tab_40.setObjectName(u"tab_40")
    w.gridLayout_74 = QGridLayout(w.tab_40)
    w.gridLayout_74.setObjectName(u"gridLayout_74")
    w._3D_Struct_table = QTableWidget(w.tab_40)
    w._3D_Struct_table.setObjectName(u"_3D_Struct_table")

    w.gridLayout_74.addWidget(w._3D_Struct_table, 0, 0, 1, 1)

    w.tabWidget_3Dview.addTab(w.tab_40, "")
    w.tab_42 = QWidget()
    w.tab_42.setObjectName(u"tab_42")
    w.gridLayout_75 = QGridLayout(w.tab_42)
    w.gridLayout_75.setObjectName(u"gridLayout_75")
    w._STL_Surface_table = QTableWidget(w.tab_42)
    w._STL_Surface_table.setObjectName(u"_STL_Surface_table")

    w.gridLayout_75.addWidget(w._STL_Surface_table, 0, 0, 1, 1)

    w.tabWidget_3Dview.addTab(w.tab_42, "")
    w.tab_41 = QWidget()
    w.tab_41.setObjectName(u"tab_41")
    w.tabWidget_3Dview.addTab(w.tab_41, "")
    w.tab_43 = QWidget()
    w.tab_43.setObjectName(u"tab_43")
    w.gridLayout_76 = QGridLayout(w.tab_43)
    w.gridLayout_76.setObjectName(u"gridLayout_76")
    w._3D_proton_table = QTableWidget(w.tab_43)
    w._3D_proton_table.setObjectName(u"_3D_proton_table")

    w.gridLayout_76.addWidget(w._3D_proton_table, 0, 0, 1, 1)

    w.tabWidget_3Dview.addTab(w.tab_43, "")

    w.gridLayout_63.addWidget(w.tabWidget_3Dview, 2, 1, 1, 2)

    w.View3DgroupBox_13 = QGroupBox(w._3Dview)
    w.View3DgroupBox_13.setObjectName(u"View3DgroupBox_13")
    w.gridLayout_67 = QGridLayout(w.View3DgroupBox_13)
    w.gridLayout_67.setObjectName(u"gridLayout_67")
    w.View3DhorizontalSpacer_86 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_67.addItem(w.View3DhorizontalSpacer_86, 15, 3, 1, 1)

    w.View3D_Threshold_slider_01 = QSlider(w.View3DgroupBox_13)
    w.View3D_Threshold_slider_01.setObjectName(u"View3D_Threshold_slider_01")
    w.View3D_Threshold_slider_01.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_67.addWidget(w.View3D_Threshold_slider_01, 2, 1, 1, 4)

    w.View3D_coronal_slider_01 = QSlider(w.View3DgroupBox_13)
    w.View3D_coronal_slider_01.setObjectName(u"View3D_coronal_slider_01")
    w.View3D_coronal_slider_01.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_67.addWidget(w.View3D_coronal_slider_01, 6, 1, 1, 4)

    w.View3DverticalSpacer_23 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_67.addItem(w.View3DverticalSpacer_23, 14, 5, 1, 1)

    w.View3D_axial_slider_01 = QSlider(w.View3DgroupBox_13)
    w.View3D_axial_slider_01.setObjectName(u"View3D_axial_slider_01")
    w.View3D_axial_slider_01.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_67.addWidget(w.View3D_axial_slider_01, 4, 1, 1, 4)

    w.View3D_axial_spin_02 = QSpinBox(w.View3DgroupBox_13)
    w.View3D_axial_spin_02.setObjectName(u"View3D_axial_spin_02")

    w.gridLayout_67.addWidget(w.View3D_axial_spin_02, 5, 5, 1, 1)

    w.View3DhorizontalSpacer_80 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_67.addItem(w.View3DhorizontalSpacer_80, 15, 0, 1, 1)

    w.View3D_Apply = QPushButton(w.View3DgroupBox_13)
    w.View3D_Apply.setObjectName(u"View3D_Apply")

    w.gridLayout_67.addWidget(w.View3D_Apply, 12, 5, 1, 1)

    w.View3D_colormap = QComboBox(w.View3DgroupBox_13)
    w.View3D_colormap.setObjectName(u"View3D_colormap")

    w.gridLayout_67.addWidget(w.View3D_colormap, 10, 1, 1, 4)

    w.View3D_axial_spin_01 = QSpinBox(w.View3DgroupBox_13)
    w.View3D_axial_spin_01.setObjectName(u"View3D_axial_spin_01")

    w.gridLayout_67.addWidget(w.View3D_axial_spin_01, 4, 5, 1, 1)

    w.View3DhorizontalSpacer_82 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_67.addItem(w.View3DhorizontalSpacer_82, 15, 4, 1, 1)

    w.View3D_Threshold_spin_01 = QDoubleSpinBox(w.View3DgroupBox_13)
    w.View3D_Threshold_spin_01.setObjectName(u"View3D_Threshold_spin_01")

    w.gridLayout_67.addWidget(w.View3D_Threshold_spin_01, 2, 5, 1, 1)

    w.View3DhorizontalSpacer_85 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_67.addItem(w.View3DhorizontalSpacer_85, 15, 2, 1, 1)

    w.View3D_coronal_spin_01 = QSpinBox(w.View3DgroupBox_13)
    w.View3D_coronal_spin_01.setObjectName(u"View3D_coronal_spin_01")

    w.gridLayout_67.addWidget(w.View3D_coronal_spin_01, 6, 5, 1, 1)

    w.View3D_name_06 = QLineEdit(w.View3DgroupBox_13)
    w.View3D_name_06.setObjectName(u"View3D_name_06")
    w.View3D_name_06.setEnabled(False)

    w.gridLayout_67.addWidget(w.View3D_name_06, 1, 0, 1, 1)

    w.View3D_sagittal_slider_01 = QSlider(w.View3DgroupBox_13)
    w.View3D_sagittal_slider_01.setObjectName(u"View3D_sagittal_slider_01")
    w.View3D_sagittal_slider_01.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_67.addWidget(w.View3D_sagittal_slider_01, 8, 1, 1, 4)

    w.View3D_sagittal_slider_02 = QSlider(w.View3DgroupBox_13)
    w.View3D_sagittal_slider_02.setObjectName(u"View3D_sagittal_slider_02")
    w.View3D_sagittal_slider_02.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_67.addWidget(w.View3D_sagittal_slider_02, 9, 1, 1, 4)

    w.View3D_Threshold_spin_02 = QDoubleSpinBox(w.View3DgroupBox_13)
    w.View3D_Threshold_spin_02.setObjectName(u"View3D_Threshold_spin_02")

    w.gridLayout_67.addWidget(w.View3D_Threshold_spin_02, 3, 5, 1, 1)

    w.View3D_sagittal_spin_02 = QSpinBox(w.View3DgroupBox_13)
    w.View3D_sagittal_spin_02.setObjectName(u"View3D_sagittal_spin_02")

    w.gridLayout_67.addWidget(w.View3D_sagittal_spin_02, 9, 5, 1, 1)

    w.View3D_sagittal_spin_01 = QSpinBox(w.View3DgroupBox_13)
    w.View3D_sagittal_spin_01.setObjectName(u"View3D_sagittal_spin_01")

    w.gridLayout_67.addWidget(w.View3D_sagittal_spin_01, 8, 5, 1, 1)

    w.View3D_name_08 = QLineEdit(w.View3DgroupBox_13)
    w.View3D_name_08.setObjectName(u"View3D_name_08")
    w.View3D_name_08.setEnabled(False)

    w.gridLayout_67.addWidget(w.View3D_name_08, 4, 0, 1, 1)

    w.View3D_isovalue_slider = QSlider(w.View3DgroupBox_13)
    w.View3D_isovalue_slider.setObjectName(u"View3D_isovalue_slider")
    w.View3D_isovalue_slider.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_67.addWidget(w.View3D_isovalue_slider, 1, 1, 1, 4)

    w.View3D_name_09 = QLineEdit(w.View3DgroupBox_13)
    w.View3D_name_09.setObjectName(u"View3D_name_09")
    w.View3D_name_09.setEnabled(False)

    w.gridLayout_67.addWidget(w.View3D_name_09, 6, 0, 1, 1)

    w.View3D_Threshold_slider_02 = QSlider(w.View3DgroupBox_13)
    w.View3D_Threshold_slider_02.setObjectName(u"View3D_Threshold_slider_02")
    w.View3D_Threshold_slider_02.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_67.addWidget(w.View3D_Threshold_slider_02, 3, 1, 1, 4)

    w.View3D_name_10 = QLineEdit(w.View3DgroupBox_13)
    w.View3D_name_10.setObjectName(u"View3D_name_10")
    w.View3D_name_10.setEnabled(False)

    w.gridLayout_67.addWidget(w.View3D_name_10, 8, 0, 1, 1)

    w.View3DhorizontalSpacer_81 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_67.addItem(w.View3DhorizontalSpacer_81, 15, 1, 1, 1)

    w.View3D_axial_slider_02 = QSlider(w.View3DgroupBox_13)
    w.View3D_axial_slider_02.setObjectName(u"View3D_axial_slider_02")
    w.View3D_axial_slider_02.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_67.addWidget(w.View3D_axial_slider_02, 5, 1, 1, 4)

    w.View3DhorizontalSpacer_83 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_67.addItem(w.View3DhorizontalSpacer_83, 15, 5, 1, 1)

    w.View3D_histogram = QWidget(w.View3DgroupBox_13)
    w.View3D_histogram.setObjectName(u"View3D_histogram")

    w.gridLayout_67.addWidget(w.View3D_histogram, 0, 0, 1, 6)

    w.View3D_name_07 = QLineEdit(w.View3DgroupBox_13)
    w.View3D_name_07.setObjectName(u"View3D_name_07")
    w.View3D_name_07.setEnabled(False)

    w.gridLayout_67.addWidget(w.View3D_name_07, 2, 0, 1, 1)

    w.View3D_coronal_spin_02 = QSpinBox(w.View3DgroupBox_13)
    w.View3D_coronal_spin_02.setObjectName(u"View3D_coronal_spin_02")

    w.gridLayout_67.addWidget(w.View3D_coronal_spin_02, 7, 5, 1, 1)

    w.View3D_isovalue_spin_01 = QDoubleSpinBox(w.View3DgroupBox_13)
    w.View3D_isovalue_spin_01.setObjectName(u"View3D_isovalue_spin_01")

    w.gridLayout_67.addWidget(w.View3D_isovalue_spin_01, 1, 5, 1, 1)

    w.View3DgroupBox_14 = QGroupBox(w.View3DgroupBox_13)
    w.View3DgroupBox_14.setObjectName(u"View3DgroupBox_14")
    w.gridLayout_66 = QGridLayout(w.View3DgroupBox_14)
    w.gridLayout_66.setObjectName(u"gridLayout_66")
    w.View3D_4D_speed_play_slider = QSlider(w.View3DgroupBox_14)
    w.View3D_4D_speed_play_slider.setObjectName(u"View3D_4D_speed_play_slider")
    w.View3D_4D_speed_play_slider.setEnabled(False)
    w.View3D_4D_speed_play_slider.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_66.addWidget(w.View3D_4D_speed_play_slider, 0, 2, 1, 1)

    w.View3D_play4D = QToolButton(w.View3DgroupBox_14)
    w.View3D_play4D.setObjectName(u"View3D_play4D")

    w.gridLayout_66.addWidget(w.View3D_play4D, 0, 0, 1, 1)

    w.View3D_name_12 = QLineEdit(w.View3DgroupBox_14)
    w.View3D_name_12.setObjectName(u"View3D_name_12")
    w.View3D_name_12.setEnabled(False)

    w.gridLayout_66.addWidget(w.View3D_name_12, 0, 1, 1, 1)

    w.View3D_4D_speed_play_spin_01 = QDoubleSpinBox(w.View3DgroupBox_14)
    w.View3D_4D_speed_play_spin_01.setObjectName(u"View3D_4D_speed_play_spin_01")
    w.View3D_4D_speed_play_spin_01.setEnabled(False)

    w.gridLayout_66.addWidget(w.View3D_4D_speed_play_spin_01, 0, 3, 1, 1)


    w.gridLayout_67.addWidget(w.View3DgroupBox_14, 16, 0, 1, 7)

    w.View3D_name_11 = QLineEdit(w.View3DgroupBox_13)
    w.View3D_name_11.setObjectName(u"View3D_name_11")
    w.View3D_name_11.setEnabled(False)

    w.gridLayout_67.addWidget(w.View3D_name_11, 10, 0, 1, 1)

    w.View3D_coronal_slider_02 = QSlider(w.View3DgroupBox_13)
    w.View3D_coronal_slider_02.setObjectName(u"View3D_coronal_slider_02")
    w.View3D_coronal_slider_02.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_67.addWidget(w.View3D_coronal_slider_02, 7, 1, 1, 4)

    w.View3D_real_time_checkBox = QCheckBox(w.View3DgroupBox_13)
    w.View3D_real_time_checkBox.setObjectName(u"View3D_real_time_checkBox")
    w.View3D_real_time_checkBox.setEnabled(False)

    w.gridLayout_67.addWidget(w.View3D_real_time_checkBox, 11, 5, 1, 1)

    w.View3D_update_all_3D = QCheckBox(w.View3DgroupBox_13)
    w.View3D_update_all_3D.setObjectName(u"View3D_update_all_3D")
    w.View3D_update_all_3D.setEnabled(False)

    w.gridLayout_67.addWidget(w.View3D_update_all_3D, 10, 5, 1, 1)


    w.gridLayout_63.addWidget(w.View3DgroupBox_13, 1, 3, 2, 1)

    w.verticalSpacer_19 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_63.addItem(w.verticalSpacer_19, 1, 0, 1, 1)

