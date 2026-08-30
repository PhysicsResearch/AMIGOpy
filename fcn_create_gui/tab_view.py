# -*- coding: utf-8 -*-
"""
tab_view.py - AMIGOpy GUI Module
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


def create_tab_view(w):
    """
    Create the View module tab (im_display_tab).

    This is the main image viewing area containing:
    - VTK orthogonal view containers (VTK_view_01, VTK_view_02, VTK_view_03)
    - Axial, Sagittal, and Coronal slice sliders
    - tabView01 QTabWidget (west-positioned) with sub-tabs:
      * View: histogram container + tabWidget_10 (Transform_01, Transform_02, Process)
      * DOSE: dose overlay controls
      * PLAN: brachy plan overlay with channel/dwell display
      * STRUCT: structure list and mask creation
      * IrIS: load/operations/calibration sub-tabs
      * MetaData: DICOM metadata search and display
      * 4DCT: 4D CT playback and average calculation
      * ROI: circular ROI management (Circles + Data sub-tabs)

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
    w.tabModules.setObjectName(u"tabModules")
    w.im_display_tab = QWidget()
    w.im_display_tab.setObjectName(u"im_display_tab")
    w.gridLayout_4 = QGridLayout(w.im_display_tab)
    w.gridLayout_4.setObjectName(u"gridLayout_4")
    w.AxialSlider = QSlider(w.im_display_tab)
    w.AxialSlider.setObjectName(u"AxialSlider")
    w.AxialSlider.setSingleStep(25)
    w.AxialSlider.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_4.addWidget(w.AxialSlider, 1, 0, 1, 1)

    w.SagittalSlider = QSlider(w.im_display_tab)
    w.SagittalSlider.setObjectName(u"SagittalSlider")
    w.SagittalSlider.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_4.addWidget(w.SagittalSlider, 1, 1, 1, 1)

    w.CoronalSlider = QSlider(w.im_display_tab)
    w.CoronalSlider.setObjectName(u"CoronalSlider")
    w.CoronalSlider.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_4.addWidget(w.CoronalSlider, 1, 2, 1, 1)

    w.VTK_view_02 = QWidget(w.im_display_tab)
    w.VTK_view_02.setObjectName(u"VTK_view_02")
    sizePolicy2.setHeightForWidth(w.VTK_view_02.sizePolicy().hasHeightForWidth())
    w.VTK_view_02.setSizePolicy(sizePolicy2)
    w.gridLayout_92 = QGridLayout(w.VTK_view_02)
    w.gridLayout_92.setObjectName(u"gridLayout_92")
    w.horizontalSpacer_80 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_92.addItem(w.horizontalSpacer_80, 1, 1, 1, 1)

    w.verticalSpacer_26 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_92.addItem(w.verticalSpacer_26, 1, 0, 1, 1)


    w.gridLayout_4.addWidget(w.VTK_view_02, 0, 1, 1, 1)

    w.VTK_view_01 = QWidget(w.im_display_tab)
    w.VTK_view_01.setObjectName(u"VTK_view_01")
    sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    sizePolicy3.setHorizontalStretch(0)
    sizePolicy3.setVerticalStretch(0)
    sizePolicy3.setHeightForWidth(w.VTK_view_01.sizePolicy().hasHeightForWidth())
    w.VTK_view_01.setSizePolicy(sizePolicy3)
    w.gridLayout_90 = QGridLayout(w.VTK_view_01)
    w.gridLayout_90.setObjectName(u"gridLayout_90")
    w.verticalSpacer_25 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_90.addItem(w.verticalSpacer_25, 0, 0, 1, 1)

    w.horizontalSpacer_46 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_90.addItem(w.horizontalSpacer_46, 0, 1, 1, 1)


    w.gridLayout_4.addWidget(w.VTK_view_01, 0, 0, 1, 1)

    w.VTK_view_03 = QWidget(w.im_display_tab)
    w.VTK_view_03.setObjectName(u"VTK_view_03")
    sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    sizePolicy4.setHorizontalStretch(0)
    sizePolicy4.setVerticalStretch(0)
    sizePolicy4.setHeightForWidth(w.VTK_view_03.sizePolicy().hasHeightForWidth())
    w.VTK_view_03.setSizePolicy(sizePolicy4)
    w.gridLayout_91 = QGridLayout(w.VTK_view_03)
    w.gridLayout_91.setObjectName(u"gridLayout_91")
    w.verticalSpacer_27 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_91.addItem(w.verticalSpacer_27, 1, 0, 1, 1)

    w.horizontalSpacer_81 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_91.addItem(w.horizontalSpacer_81, 1, 1, 1, 1)


    w.gridLayout_4.addWidget(w.VTK_view_03, 0, 2, 1, 1)

    w.tabView01 = QTabWidget(w.im_display_tab)
    w.tabView01.setObjectName(u"tabView01")
    sizePolicy1.setHeightForWidth(w.tabView01.sizePolicy().hasHeightForWidth())
    w.tabView01.setSizePolicy(sizePolicy1)
    w.tabView01.setFont(font)
    w.tabView01.setTabPosition(QTabWidget.TabPosition.West)
    w.tab_5 = QWidget()
    w.tab_5.setObjectName(u"tab_5")
    w.gridLayout_81 = QGridLayout(w.tab_5)
    w.gridLayout_81.setObjectName(u"gridLayout_81")
    w.hist_container_01 = QWidget(w.tab_5)
    w.hist_container_01.setObjectName(u"hist_container_01")
    sizePolicy1.setHeightForWidth(w.hist_container_01.sizePolicy().hasHeightForWidth())
    w.hist_container_01.setSizePolicy(sizePolicy1)

    w.gridLayout_81.addWidget(w.hist_container_01, 0, 0, 1, 1)

    w.tabWidget_10 = QTabWidget(w.tab_5)
    w.tabWidget_10.setObjectName(u"tabWidget_10")
    sizePolicy1.setHeightForWidth(w.tabWidget_10.sizePolicy().hasHeightForWidth())
    w.tabWidget_10.setSizePolicy(sizePolicy1)
    w.tab_44 = QWidget()
    w.tab_44.setObjectName(u"tab_44")
    w.gridLayout_31 = QGridLayout(w.tab_44)
    w.gridLayout_31.setObjectName(u"gridLayout_31")
    w.groupBox_13 = QGroupBox(w.tab_44)
    w.groupBox_13.setObjectName(u"groupBox_13")
    w.gridLayout_83 = QGridLayout(w.groupBox_13)
    w.gridLayout_83.setObjectName(u"gridLayout_83")
    w.lineEdit_85 = QLineEdit(w.groupBox_13)
    w.lineEdit_85.setObjectName(u"lineEdit_85")
    w.lineEdit_85.setEnabled(False)

    w.gridLayout_83.addWidget(w.lineEdit_85, 0, 0, 1, 1)

    w.Reg_manual_Rot_Z = QDoubleSpinBox(w.groupBox_13)
    w.Reg_manual_Rot_Z.setObjectName(u"Reg_manual_Rot_Z")

    w.gridLayout_83.addWidget(w.Reg_manual_Rot_Z, 3, 0, 1, 1)

    w.Reg_manual_Rot_X = QDoubleSpinBox(w.groupBox_13)
    w.Reg_manual_Rot_X.setObjectName(u"Reg_manual_Rot_X")

    w.gridLayout_83.addWidget(w.Reg_manual_Rot_X, 1, 0, 1, 1)

    w.Reg_manual_Rot_Y = QDoubleSpinBox(w.groupBox_13)
    w.Reg_manual_Rot_Y.setObjectName(u"Reg_manual_Rot_Y")

    w.gridLayout_83.addWidget(w.Reg_manual_Rot_Y, 2, 0, 1, 1)


    w.gridLayout_31.addWidget(w.groupBox_13, 1, 0, 1, 1)

    w.groupBox_15 = QGroupBox(w.tab_44)
    w.groupBox_15.setObjectName(u"groupBox_15")
    w.gridLayout_85 = QGridLayout(w.groupBox_15)
    w.gridLayout_85.setObjectName(u"gridLayout_85")
    w.pushButton_5 = QPushButton(w.groupBox_15)
    w.pushButton_5.setObjectName(u"pushButton_5")

    w.gridLayout_85.addWidget(w.pushButton_5, 2, 1, 1, 1)

    w.pushButton_6 = QPushButton(w.groupBox_15)
    w.pushButton_6.setObjectName(u"pushButton_6")

    w.gridLayout_85.addWidget(w.pushButton_6, 3, 1, 1, 1)

    w.pushButton_4 = QPushButton(w.groupBox_15)
    w.pushButton_4.setObjectName(u"pushButton_4")

    w.gridLayout_85.addWidget(w.pushButton_4, 1, 1, 1, 1)


    w.gridLayout_31.addWidget(w.groupBox_15, 1, 1, 1, 1)

    w.groupBox_12 = QGroupBox(w.tab_44)
    w.groupBox_12.setObjectName(u"groupBox_12")
    w.gridLayout_82 = QGridLayout(w.groupBox_12)
    w.gridLayout_82.setObjectName(u"gridLayout_82")
    w.lineEdit_71 = QLineEdit(w.groupBox_12)
    w.lineEdit_71.setObjectName(u"lineEdit_71")
    w.lineEdit_71.setEnabled(False)

    w.gridLayout_82.addWidget(w.lineEdit_71, 0, 0, 1, 1)

    w.Reg_manual_Refx = QDoubleSpinBox(w.groupBox_12)
    w.Reg_manual_Refx.setObjectName(u"Reg_manual_Refx")
    w.Reg_manual_Refx.setEnabled(False)
    w.Reg_manual_Refx.setMinimum(-9999999.000000000000000)
    w.Reg_manual_Refx.setMaximum(9999999.990000000223517)

    w.gridLayout_82.addWidget(w.Reg_manual_Refx, 0, 1, 1, 2)

    w.Reg_manual_Refy = QDoubleSpinBox(w.groupBox_12)
    w.Reg_manual_Refy.setObjectName(u"Reg_manual_Refy")
    w.Reg_manual_Refy.setEnabled(False)
    w.Reg_manual_Refy.setMinimum(-9999999.000000000000000)
    w.Reg_manual_Refy.setMaximum(9999999.990000000223517)

    w.gridLayout_82.addWidget(w.Reg_manual_Refy, 0, 3, 1, 1)

    w.Reg_manual_Refz = QDoubleSpinBox(w.groupBox_12)
    w.Reg_manual_Refz.setObjectName(u"Reg_manual_Refz")
    w.Reg_manual_Refz.setEnabled(False)
    w.Reg_manual_Refz.setMinimum(-9999999.000000000000000)
    w.Reg_manual_Refz.setMaximum(9999999.990000000223517)

    w.gridLayout_82.addWidget(w.Reg_manual_Refz, 0, 4, 1, 3)

    w.lineEdit_72 = QLineEdit(w.groupBox_12)
    w.lineEdit_72.setObjectName(u"lineEdit_72")
    w.lineEdit_72.setEnabled(False)

    w.gridLayout_82.addWidget(w.lineEdit_72, 1, 0, 1, 1)

    w.Reg_manual_Tx = QDoubleSpinBox(w.groupBox_12)
    w.Reg_manual_Tx.setObjectName(u"Reg_manual_Tx")
    w.Reg_manual_Tx.setMinimum(-9999999.000000000000000)
    w.Reg_manual_Tx.setMaximum(9999999.990000000223517)

    w.gridLayout_82.addWidget(w.Reg_manual_Tx, 1, 1, 1, 2)

    w.lineEdit_73 = QLineEdit(w.groupBox_12)
    w.lineEdit_73.setObjectName(u"lineEdit_73")
    w.lineEdit_73.setEnabled(False)

    w.gridLayout_82.addWidget(w.lineEdit_73, 2, 0, 1, 1)

    w.apply_Im_transformation = QPushButton(w.groupBox_12)
    w.apply_Im_transformation.setObjectName(u"apply_Im_transformation")

    w.gridLayout_82.addWidget(w.apply_Im_transformation, 3, 5, 1, 2)

    w.Reg_manual_Ty = QDoubleSpinBox(w.groupBox_12)
    w.Reg_manual_Ty.setObjectName(u"Reg_manual_Ty")
    w.Reg_manual_Ty.setMinimum(-9999999.000000000000000)
    w.Reg_manual_Ty.setMaximum(9999999.990000000223517)

    w.gridLayout_82.addWidget(w.Reg_manual_Ty, 1, 3, 1, 1)

    w.Reg_manual_Tz = QDoubleSpinBox(w.groupBox_12)
    w.Reg_manual_Tz.setObjectName(u"Reg_manual_Tz")
    w.Reg_manual_Tz.setMinimum(-9999999.000000000000000)
    w.Reg_manual_Tz.setMaximum(9999999.990000000223517)

    w.gridLayout_82.addWidget(w.Reg_manual_Tz, 1, 4, 1, 3)

    w.lineEdit_89 = QLineEdit(w.groupBox_12)
    w.lineEdit_89.setObjectName(u"lineEdit_89")
    w.lineEdit_89.setEnabled(False)

    w.gridLayout_82.addWidget(w.lineEdit_89, 2, 3, 1, 1)

    w.Manual_reg_step = QDoubleSpinBox(w.groupBox_12)
    w.Manual_reg_step.setObjectName(u"Manual_reg_step")
    w.Manual_reg_step.setMinimum(-9999999.000000000000000)
    w.Manual_reg_step.setMaximum(9999999.990000000223517)

    w.gridLayout_82.addWidget(w.Manual_reg_step, 2, 1, 1, 2)

    w.reg_fill_value = QDoubleSpinBox(w.groupBox_12)
    w.reg_fill_value.setObjectName(u"reg_fill_value")
    w.reg_fill_value.setMinimum(-9999999.000000000000000)
    w.reg_fill_value.setMaximum(9999999.990000000223517)
    w.reg_fill_value.setValue(-1024.000000000000000)

    w.gridLayout_82.addWidget(w.reg_fill_value, 2, 4, 1, 3)


    w.gridLayout_31.addWidget(w.groupBox_12, 0, 0, 1, 2)

    w.tabWidget_10.addTab(w.tab_44, "")
    w.tab_17 = QWidget()
    w.tab_17.setObjectName(u"tab_17")
    w.gridLayout_12 = QGridLayout(w.tab_17)
    w.gridLayout_12.setObjectName(u"gridLayout_12")
    w.groupBox_14 = QGroupBox(w.tab_17)
    w.groupBox_14.setObjectName(u"groupBox_14")
    w.gridLayout_84 = QGridLayout(w.groupBox_14)
    w.gridLayout_84.setObjectName(u"gridLayout_84")
    w.lineEdit_74 = QLineEdit(w.groupBox_14)
    w.lineEdit_74.setObjectName(u"lineEdit_74")
    w.lineEdit_74.setEnabled(False)

    w.gridLayout_84.addWidget(w.lineEdit_74, 0, 0, 1, 1)

    w.doubleSpinBox_15 = QDoubleSpinBox(w.groupBox_14)
    w.doubleSpinBox_15.setObjectName(u"doubleSpinBox_15")
    w.doubleSpinBox_15.setEnabled(False)

    w.gridLayout_84.addWidget(w.doubleSpinBox_15, 0, 1, 1, 1)

    w.doubleSpinBox_13 = QDoubleSpinBox(w.groupBox_14)
    w.doubleSpinBox_13.setObjectName(u"doubleSpinBox_13")
    w.doubleSpinBox_13.setEnabled(False)

    w.gridLayout_84.addWidget(w.doubleSpinBox_13, 0, 2, 1, 1)

    w.doubleSpinBox_14 = QDoubleSpinBox(w.groupBox_14)
    w.doubleSpinBox_14.setObjectName(u"doubleSpinBox_14")
    w.doubleSpinBox_14.setEnabled(False)

    w.gridLayout_84.addWidget(w.doubleSpinBox_14, 0, 3, 1, 1)

    w.lineEdit_84 = QLineEdit(w.groupBox_14)
    w.lineEdit_84.setObjectName(u"lineEdit_84")
    w.lineEdit_84.setEnabled(False)

    w.gridLayout_84.addWidget(w.lineEdit_84, 1, 0, 1, 1)

    w.doubleSpinBox_18 = QDoubleSpinBox(w.groupBox_14)
    w.doubleSpinBox_18.setObjectName(u"doubleSpinBox_18")

    w.gridLayout_84.addWidget(w.doubleSpinBox_18, 1, 1, 1, 1)

    w.doubleSpinBox_17 = QDoubleSpinBox(w.groupBox_14)
    w.doubleSpinBox_17.setObjectName(u"doubleSpinBox_17")

    w.gridLayout_84.addWidget(w.doubleSpinBox_17, 1, 2, 1, 1)

    w.doubleSpinBox_16 = QDoubleSpinBox(w.groupBox_14)
    w.doubleSpinBox_16.setObjectName(u"doubleSpinBox_16")

    w.gridLayout_84.addWidget(w.doubleSpinBox_16, 1, 3, 1, 1)

    w.pushButton_2 = QPushButton(w.groupBox_14)
    w.pushButton_2.setObjectName(u"pushButton_2")

    w.gridLayout_84.addWidget(w.pushButton_2, 2, 3, 1, 1)


    w.gridLayout_12.addWidget(w.groupBox_14, 0, 0, 1, 1)

    w.groupBox_16 = QGroupBox(w.tab_17)
    w.groupBox_16.setObjectName(u"groupBox_16")
    w.gridLayout_86 = QGridLayout(w.groupBox_16)
    w.gridLayout_86.setObjectName(u"gridLayout_86")
    w.doubleSpinBox_22 = QDoubleSpinBox(w.groupBox_16)
    w.doubleSpinBox_22.setObjectName(u"doubleSpinBox_22")
    w.doubleSpinBox_22.setEnabled(False)

    w.gridLayout_86.addWidget(w.doubleSpinBox_22, 1, 7, 1, 1)

    w.doubleSpinBox_27 = QDoubleSpinBox(w.groupBox_16)
    w.doubleSpinBox_27.setObjectName(u"doubleSpinBox_27")

    w.gridLayout_86.addWidget(w.doubleSpinBox_27, 2, 0, 1, 1)

    w.doubleSpinBox_26 = QDoubleSpinBox(w.groupBox_16)
    w.doubleSpinBox_26.setObjectName(u"doubleSpinBox_26")

    w.gridLayout_86.addWidget(w.doubleSpinBox_26, 2, 1, 1, 1)

    w.doubleSpinBox_20 = QDoubleSpinBox(w.groupBox_16)
    w.doubleSpinBox_20.setObjectName(u"doubleSpinBox_20")
    w.doubleSpinBox_20.setEnabled(False)

    w.gridLayout_86.addWidget(w.doubleSpinBox_20, 1, 1, 1, 1)

    w.doubleSpinBox_21 = QDoubleSpinBox(w.groupBox_16)
    w.doubleSpinBox_21.setObjectName(u"doubleSpinBox_21")
    w.doubleSpinBox_21.setEnabled(False)

    w.gridLayout_86.addWidget(w.doubleSpinBox_21, 1, 0, 1, 1)

    w.doubleSpinBox_23 = QDoubleSpinBox(w.groupBox_16)
    w.doubleSpinBox_23.setObjectName(u"doubleSpinBox_23")
    w.doubleSpinBox_23.setEnabled(False)

    w.gridLayout_86.addWidget(w.doubleSpinBox_23, 1, 6, 1, 1)

    w.lineEdit_88 = QLineEdit(w.groupBox_16)
    w.lineEdit_88.setObjectName(u"lineEdit_88")
    w.lineEdit_88.setEnabled(False)

    w.gridLayout_86.addWidget(w.lineEdit_88, 0, 6, 1, 2)

    w.doubleSpinBox_28 = QDoubleSpinBox(w.groupBox_16)
    w.doubleSpinBox_28.setObjectName(u"doubleSpinBox_28")

    w.gridLayout_86.addWidget(w.doubleSpinBox_28, 2, 7, 1, 1)

    w.doubleSpinBox_29 = QDoubleSpinBox(w.groupBox_16)
    w.doubleSpinBox_29.setObjectName(u"doubleSpinBox_29")

    w.gridLayout_86.addWidget(w.doubleSpinBox_29, 2, 6, 1, 1)

    w.doubleSpinBox_24 = QDoubleSpinBox(w.groupBox_16)
    w.doubleSpinBox_24.setObjectName(u"doubleSpinBox_24")
    w.doubleSpinBox_24.setEnabled(False)

    w.gridLayout_86.addWidget(w.doubleSpinBox_24, 1, 4, 1, 1)

    w.doubleSpinBox_30 = QDoubleSpinBox(w.groupBox_16)
    w.doubleSpinBox_30.setObjectName(u"doubleSpinBox_30")

    w.gridLayout_86.addWidget(w.doubleSpinBox_30, 2, 4, 1, 1)

    w.doubleSpinBox_19 = QDoubleSpinBox(w.groupBox_16)
    w.doubleSpinBox_19.setObjectName(u"doubleSpinBox_19")
    w.doubleSpinBox_19.setEnabled(False)

    w.gridLayout_86.addWidget(w.doubleSpinBox_19, 1, 3, 1, 1)

    w.doubleSpinBox_25 = QDoubleSpinBox(w.groupBox_16)
    w.doubleSpinBox_25.setObjectName(u"doubleSpinBox_25")

    w.gridLayout_86.addWidget(w.doubleSpinBox_25, 2, 3, 1, 1)

    w.lineEdit_86 = QLineEdit(w.groupBox_16)
    w.lineEdit_86.setObjectName(u"lineEdit_86")
    w.lineEdit_86.setEnabled(False)

    w.gridLayout_86.addWidget(w.lineEdit_86, 0, 0, 1, 2)

    w.lineEdit_87 = QLineEdit(w.groupBox_16)
    w.lineEdit_87.setObjectName(u"lineEdit_87")
    w.lineEdit_87.setEnabled(False)

    w.gridLayout_86.addWidget(w.lineEdit_87, 0, 3, 1, 2)


    w.gridLayout_12.addWidget(w.groupBox_16, 1, 0, 1, 1)

    w.tabWidget_10.addTab(w.tab_17, "")
    w.tab_45 = QWidget()
    w.tab_45.setObjectName(u"tab_45")
    w.gridLayout_80 = QGridLayout(w.tab_45)
    w.gridLayout_80.setObjectName(u"gridLayout_80")
    w.Process_list = QComboBox(w.tab_45)
    w.Process_list.setObjectName(u"Process_list")

    w.gridLayout_80.addWidget(w.Process_list, 0, 0, 1, 2)

    w.Func_description = QTextEdit(w.tab_45)
    w.Func_description.setObjectName(u"Func_description")
    w.Func_description.setFont(font)

    w.gridLayout_80.addWidget(w.Func_description, 0, 2, 2, 1)

    w.run_im_process = QPushButton(w.tab_45)
    w.run_im_process.setObjectName(u"run_im_process")
    font1 = QFont()
    font1.setPointSize(10)
    font1.setBold(True)
    w.run_im_process.setFont(font1)

    w.gridLayout_80.addWidget(w.run_im_process, 1, 0, 1, 1)

    w.ImageUndo_operation = QPushButton(w.tab_45)
    w.ImageUndo_operation.setObjectName(u"ImageUndo_operation")
    w.ImageUndo_operation.setFont(font1)

    w.gridLayout_80.addWidget(w.ImageUndo_operation, 1, 1, 1, 1)

    w.ProcessSetBox = QGroupBox(w.tab_45)
    w.ProcessSetBox.setObjectName(u"ProcessSetBox")
    w.ProcessSetBox.setEnabled(True)
    w.gridLayout_13 = QGridLayout(w.ProcessSetBox)
    w.gridLayout_13.setObjectName(u"gridLayout_13")
    w.Proces_spinbox_02 = QDoubleSpinBox(w.ProcessSetBox)
    w.Proces_spinbox_02.setObjectName(u"Proces_spinbox_02")
    w.Proces_spinbox_02.setFont(font)
    w.Proces_spinbox_02.setMinimum(-1.000000000000000)
    w.Proces_spinbox_02.setMaximum(99999999.989999994635582)

    w.gridLayout_13.addWidget(w.Proces_spinbox_02, 2, 1, 1, 1)

    w.Proces_spinbox_04 = QDoubleSpinBox(w.ProcessSetBox)
    w.Proces_spinbox_04.setObjectName(u"Proces_spinbox_04")
    w.Proces_spinbox_04.setFont(font)
    w.Proces_spinbox_04.setMinimum(-1.000000000000000)
    w.Proces_spinbox_04.setMaximum(9999999999.989999771118164)

    w.gridLayout_13.addWidget(w.Proces_spinbox_04, 4, 0, 1, 1)

    w.Process_set_box3 = QComboBox(w.ProcessSetBox)
    w.Process_set_box3.setObjectName(u"Process_set_box3")

    w.gridLayout_13.addWidget(w.Process_set_box3, 5, 2, 1, 1)

    w.Proces_spinbox_05 = QDoubleSpinBox(w.ProcessSetBox)
    w.Proces_spinbox_05.setObjectName(u"Proces_spinbox_05")
    w.Proces_spinbox_05.setFont(font)
    w.Proces_spinbox_05.setMinimum(-1.000000000000000)
    w.Proces_spinbox_05.setMaximum(99999999.989999994635582)

    w.gridLayout_13.addWidget(w.Proces_spinbox_05, 4, 1, 1, 1)

    w.Proces_label_05 = QLineEdit(w.ProcessSetBox)
    w.Proces_label_05.setObjectName(u"Proces_label_05")
    w.Proces_label_05.setEnabled(False)
    w.Proces_label_05.setFont(font)

    w.gridLayout_13.addWidget(w.Proces_label_05, 3, 1, 1, 1)

    w.Proces_label_06 = QLineEdit(w.ProcessSetBox)
    w.Proces_label_06.setObjectName(u"Proces_label_06")
    w.Proces_label_06.setEnabled(False)
    w.Proces_label_06.setFont(font)

    w.gridLayout_13.addWidget(w.Proces_label_06, 3, 2, 1, 1)

    w.Process_set_box = QComboBox(w.ProcessSetBox)
    w.Process_set_box.setObjectName(u"Process_set_box")

    w.gridLayout_13.addWidget(w.Process_set_box, 5, 0, 1, 1)

    w.Proces_label_04 = QLineEdit(w.ProcessSetBox)
    w.Proces_label_04.setObjectName(u"Proces_label_04")
    w.Proces_label_04.setEnabled(False)
    w.Proces_label_04.setFont(font)

    w.gridLayout_13.addWidget(w.Proces_label_04, 3, 0, 1, 1)

    w.Process_set_box2 = QComboBox(w.ProcessSetBox)
    w.Process_set_box2.setObjectName(u"Process_set_box2")

    w.gridLayout_13.addWidget(w.Process_set_box2, 5, 1, 1, 1)

    w.Proces_label_01 = QLineEdit(w.ProcessSetBox)
    w.Proces_label_01.setObjectName(u"Proces_label_01")
    w.Proces_label_01.setEnabled(False)
    w.Proces_label_01.setFont(font)

    w.gridLayout_13.addWidget(w.Proces_label_01, 0, 0, 1, 1)

    w.Proces_label_02 = QLineEdit(w.ProcessSetBox)
    w.Proces_label_02.setObjectName(u"Proces_label_02")
    w.Proces_label_02.setEnabled(False)
    w.Proces_label_02.setFont(font)

    w.gridLayout_13.addWidget(w.Proces_label_02, 0, 1, 1, 1)

    w.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_13.addItem(w.verticalSpacer_4, 6, 0, 1, 1)

    w.Proces_spinbox_01 = QDoubleSpinBox(w.ProcessSetBox)
    w.Proces_spinbox_01.setObjectName(u"Proces_spinbox_01")
    w.Proces_spinbox_01.setFont(font)
    w.Proces_spinbox_01.setMinimum(-1.000000000000000)
    w.Proces_spinbox_01.setMaximum(99999999999.990005493164063)

    w.gridLayout_13.addWidget(w.Proces_spinbox_01, 2, 0, 1, 1)

    w.Proces_label_03 = QLineEdit(w.ProcessSetBox)
    w.Proces_label_03.setObjectName(u"Proces_label_03")
    w.Proces_label_03.setEnabled(False)
    w.Proces_label_03.setFont(font)

    w.gridLayout_13.addWidget(w.Proces_label_03, 0, 2, 1, 1)

    w.Process_DataType_box = QComboBox(w.ProcessSetBox)
    w.Process_DataType_box.setObjectName(u"Process_DataType_box")

    w.gridLayout_13.addWidget(w.Process_DataType_box, 7, 0, 1, 1)

    w.Proces_spinbox_03 = QDoubleSpinBox(w.ProcessSetBox)
    w.Proces_spinbox_03.setObjectName(u"Proces_spinbox_03")
    w.Proces_spinbox_03.setFont(font)
    w.Proces_spinbox_03.setMinimum(-1.000000000000000)
    w.Proces_spinbox_03.setMaximum(999999999990000.000000000000000)

    w.gridLayout_13.addWidget(w.Proces_spinbox_03, 2, 2, 1, 1)

    w.Proces_spinbox_06 = QDoubleSpinBox(w.ProcessSetBox)
    w.Proces_spinbox_06.setObjectName(u"Proces_spinbox_06")
    w.Proces_spinbox_06.setFont(font)
    w.Proces_spinbox_06.setMinimum(-1.000000000000000)
    w.Proces_spinbox_06.setMaximum(999999999.990000009536743)

    w.gridLayout_13.addWidget(w.Proces_spinbox_06, 4, 2, 1, 1)


    w.gridLayout_80.addWidget(w.ProcessSetBox, 2, 0, 1, 3)

    w.tabWidget_10.addTab(w.tab_45, "")

    w.gridLayout_81.addWidget(w.tabWidget_10, 0, 1, 1, 1)

    w.tabView01.addTab(w.tab_5, "")
    w.tab_6 = QWidget()
    w.tab_6.setObjectName(u"tab_6")
    w.tabView01.addTab(w.tab_6, "")
    w.tab_14 = QWidget()
    w.tab_14.setObjectName(u"tab_14")
    w.gridLayout_44 = QGridLayout(w.tab_14)
    w.gridLayout_44.setObjectName(u"gridLayout_44")
    w.tabWidget_3 = QTabWidget(w.tab_14)
    w.tabWidget_3.setObjectName(u"tabWidget_3")
    sizePolicy1.setHeightForWidth(w.tabWidget_3.sizePolicy().hasHeightForWidth())
    w.tabWidget_3.setSizePolicy(sizePolicy1)
    w.tab_37 = QWidget()
    w.tab_37.setObjectName(u"tab_37")
    w.gridLayout_8 = QGridLayout(w.tab_37)
    w.gridLayout_8.setObjectName(u"gridLayout_8")
    w.display_brachy_channel_overlay = QCheckBox(w.tab_37)
    w.display_brachy_channel_overlay.setObjectName(u"display_brachy_channel_overlay")

    w.gridLayout_8.addWidget(w.display_brachy_channel_overlay, 2, 4, 1, 1)

    w.verticalSpacer_28 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_8.addItem(w.verticalSpacer_28, 0, 5, 1, 1)

    w.brachy_table_01 = QTableWidget(w.tab_37)
    w.brachy_table_01.setObjectName(u"brachy_table_01")
    font2 = QFont()
    font2.setPointSize(12)
    w.brachy_table_01.setFont(font2)

    w.gridLayout_8.addWidget(w.brachy_table_01, 0, 0, 4, 4)

    w.brachy_export_dw_channels_csv = QPushButton(w.tab_37)
    w.brachy_export_dw_channels_csv.setObjectName(u"brachy_export_dw_channels_csv")

    w.gridLayout_8.addWidget(w.brachy_export_dw_channels_csv, 5, 4, 1, 1)

    w.display_dw_overlay = QCheckBox(w.tab_37)
    w.display_dw_overlay.setObjectName(u"display_dw_overlay")

    w.gridLayout_8.addWidget(w.display_dw_overlay, 3, 4, 1, 1)

    w.lineEdit_63 = QLineEdit(w.tab_37)
    w.lineEdit_63.setObjectName(u"lineEdit_63")
    w.lineEdit_63.setEnabled(False)
    w.lineEdit_63.setFont(font)

    w.gridLayout_8.addWidget(w.lineEdit_63, 5, 2, 1, 1)

    w.brachy_combobox_01 = QComboBox(w.tab_37)
    w.brachy_combobox_01.setObjectName(u"brachy_combobox_01")

    w.gridLayout_8.addWidget(w.brachy_combobox_01, 5, 0, 1, 1)

    w.brachy_spinBox_01 = QSpinBox(w.tab_37)
    w.brachy_spinBox_01.setObjectName(u"brachy_spinBox_01")
    w.brachy_spinBox_01.setFont(font)

    w.gridLayout_8.addWidget(w.brachy_spinBox_01, 5, 1, 1, 1)

    w.overlay_all_channels = QCheckBox(w.tab_37)
    w.overlay_all_channels.setObjectName(u"overlay_all_channels")
    w.overlay_all_channels.setChecked(True)

    w.gridLayout_8.addWidget(w.overlay_all_channels, 1, 4, 1, 1)

    w.dw_ch_point_size = QSpinBox(w.tab_37)
    w.dw_ch_point_size.setObjectName(u"dw_ch_point_size")
    w.dw_ch_point_size.setFont(font)
    w.dw_ch_point_size.setValue(3)

    w.gridLayout_8.addWidget(w.dw_ch_point_size, 5, 3, 1, 1)

    w.horizontalSpacer_45 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_8.addItem(w.horizontalSpacer_45, 4, 0, 1, 1)

    w.tabWidget_3.addTab(w.tab_37, "")
    w.tab_38 = QWidget()
    w.tab_38.setObjectName(u"tab_38")
    w.gridLayout_ebrt = QGridLayout(w.tab_38)
    w.gridLayout_ebrt.setObjectName(u"gridLayout_ebrt")

    w.display_ebrt_fields_overlay = QCheckBox(w.tab_38)
    w.display_ebrt_fields_overlay.setObjectName(u"display_ebrt_fields_overlay")
    w.display_ebrt_fields_overlay.setChecked(True)
    w.gridLayout_ebrt.addWidget(w.display_ebrt_fields_overlay, 0, 0, 1, 1)

    w.display_ebrt_isocenter = QCheckBox(w.tab_38)
    w.display_ebrt_isocenter.setObjectName(u"display_ebrt_isocenter")
    w.display_ebrt_isocenter.setChecked(True)
    w.gridLayout_ebrt.addWidget(w.display_ebrt_isocenter, 0, 1, 1, 1)

    w.display_ebrt_cax = QCheckBox(w.tab_38)
    w.display_ebrt_cax.setObjectName(u"display_ebrt_cax")
    w.display_ebrt_cax.setChecked(True)
    w.gridLayout_ebrt.addWidget(w.display_ebrt_cax, 0, 2, 1, 1)

    w.display_ebrt_beam_fan = QCheckBox(w.tab_38)
    w.display_ebrt_beam_fan.setObjectName(u"display_ebrt_beam_fan")
    w.display_ebrt_beam_fan.setChecked(True)
    w.gridLayout_ebrt.addWidget(w.display_ebrt_beam_fan, 0, 3, 1, 1)

    w.ebrt_overlay_all_fields = QCheckBox(w.tab_38)
    w.ebrt_overlay_all_fields.setObjectName(u"ebrt_overlay_all_fields")
    w.ebrt_overlay_all_fields.setChecked(True)
    w.gridLayout_ebrt.addWidget(w.ebrt_overlay_all_fields, 1, 0, 1, 1)

    w.ebrt_plan_info_label = QLabel(w.tab_38)
    w.ebrt_plan_info_label.setObjectName(u"ebrt_plan_info_label")
    w.ebrt_plan_info_label.setText("No Plan Selected")
    w.gridLayout_ebrt.addWidget(w.ebrt_plan_info_label, 1, 1, 1, 2)

    w.ebrt_export_csv = QPushButton(w.tab_38)
    w.ebrt_export_csv.setObjectName(u"ebrt_export_csv")
    w.gridLayout_ebrt.addWidget(w.ebrt_export_csv, 1, 3, 1, 1)

    w.ebrt_table_01 = QTableWidget(w.tab_38)
    w.ebrt_table_01.setObjectName(u"ebrt_table_01")
    w.ebrt_table_01.setFont(font2)
    w.gridLayout_ebrt.addWidget(w.ebrt_table_01, 2, 0, 1, 4)

    w.tabWidget_3.addTab(w.tab_38, "")

    w.gridLayout_44.addWidget(w.tabWidget_3, 0, 0, 1, 1)

    w.tabView01.addTab(w.tab_14, "")
    w.tab_39 = QWidget()
    w.tab_39.setObjectName(u"tab_39")
    w.gridLayout_9 = QGridLayout(w.tab_39)
    w.gridLayout_9.setObjectName(u"gridLayout_9")
    w.StructRefSeries = QLineEdit(w.tab_39)
    w.StructRefSeries.setObjectName(u"StructRefSeries")
    w.StructRefSeries.setFont(font)

    w.gridLayout_9.addWidget(w.StructRefSeries, 1, 1, 1, 1)

    w.lineEdit_66 = QLineEdit(w.tab_39)
    w.lineEdit_66.setObjectName(u"lineEdit_66")
    w.lineEdit_66.setEnabled(False)
    w.lineEdit_66.setFont(font)

    w.gridLayout_9.addWidget(w.lineEdit_66, 1, 0, 1, 1)

    w.CreateMask_Structures = QPushButton(w.tab_39)
    w.CreateMask_Structures.setObjectName(u"CreateMask_Structures")

    w.gridLayout_9.addWidget(w.CreateMask_Structures, 1, 2, 1, 1)

    w.STRUCTlist = QListWidget(w.tab_39)
    w.STRUCTlist.setObjectName(u"STRUCTlist")
    sizePolicy1.setHeightForWidth(w.STRUCTlist.sizePolicy().hasHeightForWidth())
    w.STRUCTlist.setSizePolicy(sizePolicy1)

    w.gridLayout_9.addWidget(w.STRUCTlist, 0, 0, 1, 3)

    w.tabView01.addTab(w.tab_39, "")
    w.tab_9 = QWidget()
    w.tab_9.setObjectName(u"tab_9")
    w.gridLayout_7 = QGridLayout(w.tab_9)
    w.gridLayout_7.setObjectName(u"gridLayout_7")
    w.tabWidget_4 = QTabWidget(w.tab_9)
    w.tabWidget_4.setObjectName(u"tabWidget_4")
    sizePolicy1.setHeightForWidth(w.tabWidget_4.sizePolicy().hasHeightForWidth())
    w.tabWidget_4.setSizePolicy(sizePolicy1)
    w.tab_10 = QWidget()
    w.tab_10.setObjectName(u"tab_10")
    w.IrIS_CorFrame_checkbox = QCheckBox(w.tab_10)
    w.IrIS_CorFrame_checkbox.setObjectName(u"IrIS_CorFrame_checkbox")
    w.IrIS_CorFrame_checkbox.setGeometry(QRect(9, 75, 125, 22))
    w.line_18 = QFrame(w.tab_10)
    w.line_18.setObjectName(u"line_18")
    w.line_18.setGeometry(QRect(9, 105, 1327, 16))
    w.line_18.setFrameShape(QFrame.Shape.HLine)
    w.line_18.setFrameShadow(QFrame.Shadow.Sunken)
    w.line_19 = QFrame(w.tab_10)
    w.line_19.setObjectName(u"line_19")
    w.line_19.setGeometry(QRect(9, 144, 1327, 16))
    w.line_19.setFrameShape(QFrame.Shape.HLine)
    w.line_19.setFrameShadow(QFrame.Shadow.Sunken)
    w.lineEdit_39 = QLineEdit(w.tab_10)
    w.lineEdit_39.setObjectName(u"lineEdit_39")
    w.lineEdit_39.setEnabled(False)
    w.lineEdit_39.setGeometry(QRect(678, 115, 132, 22))
    w.Skip_IrIS_Files = QSpinBox(w.tab_10)
    w.Skip_IrIS_Files.setObjectName(u"Skip_IrIS_Files")
    w.Skip_IrIS_Files.setGeometry(QRect(9, 308, 70, 24))
    w.Load_IrIS_Files = QSpinBox(w.tab_10)
    w.Load_IrIS_Files.setObjectName(u"Load_IrIS_Files")
    w.Load_IrIS_Files.setGeometry(QRect(678, 308, 119, 24))
    w.Load_IrIS_Files.setMaximum(999999999)
    w.IrIS_DownSample = QSpinBox(w.tab_10)
    w.IrIS_DownSample.setObjectName(u"IrIS_DownSample")
    w.IrIS_DownSample.setGeometry(QRect(1266, 114, 70, 24))
    w.IrIS_DownSample.setMinimum(1)
    w.IrIS_Offset_checkbox = QCheckBox(w.tab_10)
    w.IrIS_Offset_checkbox.setObjectName(u"IrIS_Offset_checkbox")
    w.IrIS_Offset_checkbox.setGeometry(QRect(9, 11, 61, 22))
    w.IrIS_parallel_proc_box = QCheckBox(w.tab_10)
    w.IrIS_parallel_proc_box.setObjectName(u"IrIS_parallel_proc_box")
    w.IrIS_parallel_proc_box.setGeometry(QRect(9, 153, 133, 22))
    w.lineEdit_6 = QLineEdit(w.tab_10)
    w.lineEdit_6.setObjectName(u"lineEdit_6")
    w.lineEdit_6.setGeometry(QRect(9, 280, 132, 22))
    w.IrIS_Sens_checkbox = QCheckBox(w.tab_10)
    w.IrIS_Sens_checkbox.setObjectName(u"IrIS_Sens_checkbox")
    w.IrIS_Sens_checkbox.setGeometry(QRect(9, 43, 113, 22))
    w.lineEdit_7 = QLineEdit(w.tab_10)
    w.lineEdit_7.setObjectName(u"lineEdit_7")
    w.lineEdit_7.setGeometry(QRect(678, 280, 132, 22))
    w.checkBox_4 = QCheckBox(w.tab_10)
    w.checkBox_4.setObjectName(u"checkBox_4")
    w.checkBox_4.setGeometry(QRect(9, 115, 196, 22))
    w.checkBox_4.setChecked(True)
    w.IrIS_CorrFrame_oper = QComboBox(w.tab_10)
    w.IrIS_CorrFrame_oper.setObjectName(u"IrIS_CorrFrame_oper")
    w.IrIS_CorrFrame_oper.setGeometry(QRect(592, 73, 80, 26))
    w.IrIS_Load_CorrectionFrame = QPushButton(w.tab_10)
    w.IrIS_Load_CorrectionFrame.setObjectName(u"IrIS_Load_CorrectionFrame")
    w.IrIS_Load_CorrectionFrame.setGeometry(QRect(678, 73, 79, 26))
    w.IrIS_Load_SensMap = QPushButton(w.tab_10)
    w.IrIS_Load_SensMap.setObjectName(u"IrIS_Load_SensMap")
    w.IrIS_Load_SensMap.setGeometry(QRect(678, 41, 79, 26))
    w.IrIS_Load_Offset = QPushButton(w.tab_10)
    w.IrIS_Load_Offset.setObjectName(u"IrIS_Load_Offset")
    w.IrIS_Load_Offset.setGeometry(QRect(678, 9, 79, 26))
    w.tabWidget_4.addTab(w.tab_10, "")
    w.tab_11 = QWidget()
    w.tab_11.setObjectName(u"tab_11")
    w.tabWidget_4.addTab(w.tab_11, "")
    w.tab_12 = QWidget()
    w.tab_12.setObjectName(u"tab_12")
    w.tabWidget_4.addTab(w.tab_12, "")

    w.gridLayout_7.addWidget(w.tabWidget_4, 0, 0, 1, 1)

    w.tabView01.addTab(w.tab_9, "")
    w.tab_13 = QWidget()
    w.tab_13.setObjectName(u"tab_13")
    w.gridLayout_15 = QGridLayout(w.tab_13)
    w.gridLayout_15.setObjectName(u"gridLayout_15")
    w.lineEdit_64 = QLineEdit(w.tab_13)
    w.lineEdit_64.setObjectName(u"lineEdit_64")
    w.lineEdit_64.setEnabled(False)
    w.lineEdit_64.setFont(font)

    w.gridLayout_15.addWidget(w.lineEdit_64, 1, 0, 1, 1)

    w.metadata_search = QLineEdit(w.tab_13)
    w.metadata_search.setObjectName(u"metadata_search")
    w.metadata_search.setFont(font)

    w.gridLayout_15.addWidget(w.metadata_search, 1, 1, 1, 1)

    w.MetaViewTable = QTreeWidget(w.tab_13)
    __qtreewidgetitem = QTreeWidgetItem()
    __qtreewidgetitem.setText(0, u"1");
    w.MetaViewTable.setHeaderItem(__qtreewidgetitem)
    w.MetaViewTable.setObjectName(u"MetaViewTable")
    sizePolicy5 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    sizePolicy5.setHorizontalStretch(0)
    sizePolicy5.setVerticalStretch(0)
    sizePolicy5.setHeightForWidth(w.MetaViewTable.sizePolicy().hasHeightForWidth())
    w.MetaViewTable.setSizePolicy(sizePolicy5)

    w.gridLayout_15.addWidget(w.MetaViewTable, 0, 0, 1, 2)

    w.tabView01.addTab(w.tab_13, "")
    w.tab_31 = QWidget()
    w.tab_31.setObjectName(u"tab_31")
    w.gridLayout_30 = QGridLayout(w.tab_31)
    w.gridLayout_30.setObjectName(u"gridLayout_30")
    w.tabWidget_8 = QTabWidget(w.tab_31)
    w.tabWidget_8.setObjectName(u"tabWidget_8")
    sizePolicy1.setHeightForWidth(w.tabWidget_8.sizePolicy().hasHeightForWidth())
    w.tabWidget_8.setSizePolicy(sizePolicy1)
    w.tab_32 = QWidget()
    w.tab_32.setObjectName(u"tab_32")
    w.gridLayout_33 = QGridLayout(w.tab_32)
    w.gridLayout_33.setObjectName(u"gridLayout_33")
    w.Play4D_Buttom = QPushButton(w.tab_32)
    w.Play4D_Buttom.setObjectName(u"Play4D_Buttom")
    w.Play4D_Buttom.setCheckable(True)
    w.Play4D_Buttom.setChecked(False)

    w.gridLayout_33.addWidget(w.Play4D_Buttom, 1, 0, 1, 1)

    w.horizontalSpacer_25 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_33.addItem(w.horizontalSpacer_25, 1, 1, 1, 1)

    w.horizontalSpacer_24 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_33.addItem(w.horizontalSpacer_24, 1, 2, 1, 1)

    w.lineEdit_5 = QLineEdit(w.tab_32)
    w.lineEdit_5.setObjectName(u"lineEdit_5")
    w.lineEdit_5.setEnabled(False)

    w.gridLayout_33.addWidget(w.lineEdit_5, 1, 3, 1, 1)

    w.Play_DCT_speed = QSpinBox(w.tab_32)
    w.Play_DCT_speed.setObjectName(u"Play_DCT_speed")
    w.Play_DCT_speed.setMinimum(1)
    w.Play_DCT_speed.setMaximum(10)
    w.Play_DCT_speed.setValue(4)

    w.gridLayout_33.addWidget(w.Play_DCT_speed, 1, 4, 1, 1)

    w.CT4D_table_display = QTableWidget(w.tab_32)
    w.CT4D_table_display.setObjectName(u"CT4D_table_display")

    w.gridLayout_33.addWidget(w.CT4D_table_display, 0, 0, 1, 5)

    w.tabWidget_8.addTab(w.tab_32, "")
    w.tab_33 = QWidget()
    w.tab_33.setObjectName(u"tab_33")
    w.gridLayout_78 = QGridLayout(w.tab_33)
    w.gridLayout_78.setObjectName(u"gridLayout_78")
    w.calcAvg4DCT = QPushButton(w.tab_33)
    w.calcAvg4DCT.setObjectName(u"calcAvg4DCT")

    w.gridLayout_78.addWidget(w.calcAvg4DCT, 0, 0, 1, 1)

    w.horizontalSpacer_79 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_78.addItem(w.horizontalSpacer_79, 0, 1, 1, 1)

    w.verticalSpacer_22 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_78.addItem(w.verticalSpacer_22, 1, 0, 1, 1)

    w.tabWidget_8.addTab(w.tab_33, "")

    w.gridLayout_30.addWidget(w.tabWidget_8, 0, 0, 1, 1)

    w.tabView01.addTab(w.tab_31, "")
    w.tab_30 = QWidget()
    w.tab_30.setObjectName(u"tab_30")
    w.gridLayout_32 = QGridLayout(w.tab_30)
    w.gridLayout_32.setObjectName(u"gridLayout_32")
    w.tabWidget_9 = QTabWidget(w.tab_30)
    w.tabWidget_9.setObjectName(u"tabWidget_9")
    sizePolicy1.setHeightForWidth(w.tabWidget_9.sizePolicy().hasHeightForWidth())
    w.tabWidget_9.setSizePolicy(sizePolicy1)
    w.tab_34 = QWidget()
    w.tab_34.setObjectName(u"tab_34")
    w.gridLayout_45 = QGridLayout(w.tab_34)
    w.gridLayout_45.setObjectName(u"gridLayout_45")
    w.table_circ_roi = QTableWidget(w.tab_34)
    w.table_circ_roi.setObjectName(u"table_circ_roi")
    w.table_circ_roi.setFont(font2)

    w.gridLayout_45.addWidget(w.table_circ_roi, 0, 0, 1, 6)

    w.circ_roi_load_csv = QPushButton(w.tab_34)
    w.circ_roi_load_csv.setObjectName(u"circ_roi_load_csv")

    w.gridLayout_45.addWidget(w.circ_roi_load_csv, 1, 0, 1, 1)

    w.roi_circle_add_row = QPushButton(w.tab_34)
    w.roi_circle_add_row.setObjectName(u"roi_circle_add_row")

    w.gridLayout_45.addWidget(w.roi_circle_add_row, 1, 1, 1, 1)

    w.roi_circle_remove_row = QPushButton(w.tab_34)
    w.roi_circle_remove_row.setObjectName(u"roi_circle_remove_row")

    w.gridLayout_45.addWidget(w.roi_circle_remove_row, 1, 2, 1, 1)

    w.circ_roi_exp_csv = QPushButton(w.tab_34)
    w.circ_roi_exp_csv.setObjectName(u"circ_roi_exp_csv")

    w.gridLayout_45.addWidget(w.circ_roi_exp_csv, 2, 0, 1, 1)

    w.get_circ_roi_data = QPushButton(w.tab_34)
    w.get_circ_roi_data.setObjectName(u"get_circ_roi_data")

    w.gridLayout_45.addWidget(w.get_circ_roi_data, 2, 1, 1, 1)

    w.checkBox_circ_roi_data_01 = QCheckBox(w.tab_34)
    w.checkBox_circ_roi_data_01.setObjectName(u"checkBox_circ_roi_data_01")

    w.gridLayout_45.addWidget(w.checkBox_circ_roi_data_01, 2, 2, 1, 1)

    w.holdOnROI = QCheckBox(w.tab_34)
    w.holdOnROI.setObjectName(u"holdOnROI")

    w.gridLayout_45.addWidget(w.holdOnROI, 2, 3, 1, 1)

    w.checkBox_circ_roi_data_2 = QCheckBox(w.tab_34)
    w.checkBox_circ_roi_data_2.setObjectName(u"checkBox_circ_roi_data_2")

    w.gridLayout_45.addWidget(w.checkBox_circ_roi_data_2, 2, 4, 1, 1)

    w.groupBox_8 = QGroupBox(w.tab_34)
    w.groupBox_8.setObjectName(u"groupBox_8")

    w.gridLayout_45.addWidget(w.groupBox_8, 1, 4, 1, 1)

    w.tabWidget_9.addTab(w.tab_34, "")
    w.tab_35 = QWidget()
    w.tab_35.setObjectName(u"tab_35")
    w.gridLayout_34 = QGridLayout(w.tab_35)
    w.gridLayout_34.setObjectName(u"gridLayout_34")
    w.get_circ_roi_data2 = QPushButton(w.tab_35)
    w.get_circ_roi_data2.setObjectName(u"get_circ_roi_data2")

    w.gridLayout_34.addWidget(w.get_circ_roi_data2, 1, 0, 1, 1)

    w.exp_csv_roi_c_values = QPushButton(w.tab_35)
    w.exp_csv_roi_c_values.setObjectName(u"exp_csv_roi_c_values")

    w.gridLayout_34.addWidget(w.exp_csv_roi_c_values, 1, 1, 1, 1)

    w.table_roi_c_values = QTableWidget(w.tab_35)
    w.table_roi_c_values.setObjectName(u"table_roi_c_values")

    w.gridLayout_34.addWidget(w.table_roi_c_values, 0, 0, 1, 2)

    w.tabWidget_9.addTab(w.tab_35, "")

    w.gridLayout_32.addWidget(w.tabWidget_9, 0, 0, 1, 1)

    w.tabView01.addTab(w.tab_30, "")

    w.gridLayout_4.addWidget(w.tabView01, 2, 0, 1, 3)

