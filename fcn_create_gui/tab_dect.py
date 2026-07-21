# -*- coding: utf-8 -*-
"""
tab_dect.py - AMIGOpy GUI Module
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


def create_tab_dect(w):
    """
    Create the DECT module tab (DECT_tab).

    Creates the Dual-Energy CT analysis interface:
    - DECTmenu QTabWidget with sub-tabs for:
      * RED (Relative Electron Density) calibration
      * I-Value (mean excitation energy) fitting
      * Zeff (effective atomic number) calculation
      * SPR (stopping power ratio) determination
      * Scatter plots and DECT maps
      * Calibration data management
    - Material tables, polynomial fit controls, coefficient inputs

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
    w.DECT_tab = QWidget()
    w.DECT_tab.setObjectName(u"DECT_tab")
    w.gridLayout = QGridLayout(w.DECT_tab)
    w.gridLayout.setObjectName(u"gridLayout")
    w.DECTmenu = QTabWidget(w.DECT_tab)
    w.DECTmenu.setObjectName(u"DECTmenu")
    w.tab = QWidget()
    w.tab.setObjectName(u"tab")
    w.gridLayout_2 = QGridLayout(w.tab)
    w.gridLayout_2.setObjectName(u"gridLayout_2")
    w.export_table_mat = QPushButton(w.tab)
    w.export_table_mat.setObjectName(u"export_table_mat")

    w.gridLayout_2.addWidget(w.export_table_mat, 7, 18, 1, 1)

    w.Load_csv_mat = QPushButton(w.tab)
    w.Load_csv_mat.setObjectName(u"Load_csv_mat")

    w.gridLayout_2.addWidget(w.Load_csv_mat, 7, 0, 1, 1)

    w.Zeff_m = QLineEdit(w.tab)
    w.Zeff_m.setObjectName(u"Zeff_m")
    w.Zeff_m.setAlignment(Qt.AlignmentFlag.AlignCenter)

    w.gridLayout_2.addWidget(w.Zeff_m, 7, 16, 1, 1)

    w.checkBox_calSPR = QCheckBox(w.tab)
    w.checkBox_calSPR.setObjectName(u"checkBox_calSPR")
    w.checkBox_calSPR.setChecked(True)

    w.gridLayout_2.addWidget(w.checkBox_calSPR, 7, 13, 1, 1)

    w.line_3 = QFrame(w.tab)
    w.line_3.setObjectName(u"line_3")
    w.line_3.setFrameShape(QFrame.Shape.HLine)
    w.line_3.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_2.addWidget(w.line_3, 6, 0, 1, 20)

    w.remove_row_table_mat = QPushButton(w.tab)
    w.remove_row_table_mat.setObjectName(u"remove_row_table_mat")

    w.gridLayout_2.addWidget(w.remove_row_table_mat, 5, 0, 1, 1)

    w.lineEdit = QLineEdit(w.tab)
    w.lineEdit.setObjectName(u"lineEdit")

    w.gridLayout_2.addWidget(w.lineEdit, 5, 16, 1, 1)

    w.lineEdit_41 = QLineEdit(w.tab)
    w.lineEdit_41.setObjectName(u"lineEdit_41")
    w.lineEdit_41.setEnabled(False)
    w.lineEdit_41.setFont(font)

    w.gridLayout_2.addWidget(w.lineEdit_41, 5, 10, 1, 1)

    w.DECT_list_02 = QComboBox(w.tab)
    w.DECT_list_02.setObjectName(u"DECT_list_02")

    w.gridLayout_2.addWidget(w.DECT_list_02, 5, 11, 1, 3)

    w.checkBox_cal_I = QCheckBox(w.tab)
    w.checkBox_cal_I.setObjectName(u"checkBox_cal_I")
    w.checkBox_cal_I.setChecked(True)

    w.gridLayout_2.addWidget(w.checkBox_cal_I, 7, 11, 1, 1)

    w.label_3 = QLabel(w.tab)
    w.label_3.setObjectName(u"label_3")

    w.gridLayout_2.addWidget(w.label_3, 7, 15, 1, 1)

    w.DECT_list_01 = QComboBox(w.tab)
    w.DECT_list_01.setObjectName(u"DECT_list_01")

    w.gridLayout_2.addWidget(w.DECT_list_01, 5, 6, 1, 4)

    w.reset_table_mat = QPushButton(w.tab)
    w.reset_table_mat.setObjectName(u"reset_table_mat")

    w.gridLayout_2.addWidget(w.reset_table_mat, 7, 19, 1, 1)

    w.add_row_table_mat = QPushButton(w.tab)
    w.add_row_table_mat.setObjectName(u"add_row_table_mat")

    w.gridLayout_2.addWidget(w.add_row_table_mat, 5, 2, 1, 1)

    w.lineEdit_8 = QLineEdit(w.tab)
    w.lineEdit_8.setObjectName(u"lineEdit_8")
    w.lineEdit_8.setEnabled(False)
    w.lineEdit_8.setFont(font)

    w.gridLayout_2.addWidget(w.lineEdit_8, 5, 4, 1, 1)

    w.mat_table_label = QLineEdit(w.tab)
    w.mat_table_label.setObjectName(u"mat_table_label")
    w.mat_table_label.setAutoFillBackground(False)

    w.gridLayout_2.addWidget(w.mat_table_label, 2, 0, 1, 20)

    w.get_HU_high = QPushButton(w.tab)
    w.get_HU_high.setObjectName(u"get_HU_high")

    w.gridLayout_2.addWidget(w.get_HU_high, 5, 15, 1, 1)

    w.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_2.addItem(w.horizontalSpacer_2, 7, 7, 1, 1)

    w.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_2.addItem(w.horizontalSpacer_4, 7, 12, 1, 1)

    w.checkBox_calRED = QCheckBox(w.tab)
    w.checkBox_calRED.setObjectName(u"checkBox_calRED")
    w.checkBox_calRED.setChecked(True)

    w.gridLayout_2.addWidget(w.checkBox_calRED, 7, 8, 1, 1)

    w.cal_mat_ref_info = QPushButton(w.tab)
    w.cal_mat_ref_info.setObjectName(u"cal_mat_ref_info")

    w.gridLayout_2.addWidget(w.cal_mat_ref_info, 7, 2, 1, 1)

    w.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_2.addItem(w.horizontalSpacer_3, 7, 10, 1, 1)

    w.add_coll_table_mat = QPushButton(w.tab)
    w.add_coll_table_mat.setObjectName(u"add_coll_table_mat")

    w.gridLayout_2.addWidget(w.add_coll_table_mat, 5, 18, 1, 1)

    w.line_2 = QFrame(w.tab)
    w.line_2.setObjectName(u"line_2")
    w.line_2.setFrameShape(QFrame.Shape.HLine)
    w.line_2.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_2.addWidget(w.line_2, 4, 0, 1, 20)

    w.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_2.addItem(w.horizontalSpacer_8, 7, 14, 1, 1)

    w.remove_coll_table_mat = QPushButton(w.tab)
    w.remove_coll_table_mat.setObjectName(u"remove_coll_table_mat")

    w.gridLayout_2.addWidget(w.remove_coll_table_mat, 5, 19, 1, 1)

    w.checkBox_calZeff = QCheckBox(w.tab)
    w.checkBox_calZeff.setObjectName(u"checkBox_calZeff")
    w.checkBox_calZeff.setChecked(True)

    w.gridLayout_2.addWidget(w.checkBox_calZeff, 7, 9, 1, 1)

    w.MatInfoTable = QTableWidget(w.tab)
    w.MatInfoTable.setObjectName(u"MatInfoTable")

    w.gridLayout_2.addWidget(w.MatInfoTable, 3, 0, 1, 20)

    w.lineEdit_47 = QLineEdit(w.tab)
    w.lineEdit_47.setObjectName(u"lineEdit_47")
    w.lineEdit_47.setEnabled(False)

    w.gridLayout_2.addWidget(w.lineEdit_47, 7, 4, 1, 1)

    w.Iv_water_ref = QDoubleSpinBox(w.tab)
    w.Iv_water_ref.setObjectName(u"Iv_water_ref")
    w.Iv_water_ref.setValue(78.000000000000000)

    w.gridLayout_2.addWidget(w.Iv_water_ref, 7, 6, 1, 1)

    w.DECTmenu.addTab(w.tab, "")
    w.IValue = QWidget()
    w.IValue.setObjectName(u"IValue")
    w.gridLayout_6 = QGridLayout(w.IValue)
    w.gridLayout_6.setObjectName(u"gridLayout_6")
    w.Ivalue_figure = QWidget(w.IValue)
    w.Ivalue_figure.setObjectName(u"Ivalue_figure")

    w.gridLayout_6.addWidget(w.Ivalue_figure, 1, 0, 25, 2)

    w.Ivalue_pre_calc_fit = QPushButton(w.IValue)
    w.Ivalue_pre_calc_fit.setObjectName(u"Ivalue_pre_calc_fit")

    w.gridLayout_6.addWidget(w.Ivalue_pre_calc_fit, 23, 3, 1, 1)

    w.I_value_b_coeff_calc = QLineEdit(w.IValue)
    w.I_value_b_coeff_calc.setObjectName(u"I_value_b_coeff_calc")

    w.gridLayout_6.addWidget(w.I_value_b_coeff_calc, 14, 3, 1, 1)

    w.Ivalue_calc_fit = QPushButton(w.IValue)
    w.Ivalue_calc_fit.setObjectName(u"Ivalue_calc_fit")

    w.gridLayout_6.addWidget(w.Ivalue_calc_fit, 7, 3, 1, 1)

    w.line_8 = QFrame(w.IValue)
    w.line_8.setObjectName(u"line_8")
    w.line_8.setFrameShape(QFrame.Shape.HLine)
    w.line_8.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_6.addWidget(w.line_8, 18, 3, 1, 1)

    w.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_6.addItem(w.verticalSpacer_2, 24, 3, 1, 1)

    w.lineEdit_3 = QLineEdit(w.IValue)
    w.lineEdit_3.setObjectName(u"lineEdit_3")
    w.lineEdit_3.setEnabled(False)

    w.gridLayout_6.addWidget(w.lineEdit_3, 3, 3, 1, 1)

    w.I_value_z_up_lim = QLineEdit(w.IValue)
    w.I_value_z_up_lim.setObjectName(u"I_value_z_up_lim")
    w.I_value_z_up_lim.setEnabled(False)

    w.gridLayout_6.addWidget(w.I_value_z_up_lim, 19, 3, 1, 1)

    w.Ivalue_plot = QPushButton(w.IValue)
    w.Ivalue_plot.setObjectName(u"Ivalue_plot")

    w.gridLayout_6.addWidget(w.Ivalue_plot, 6, 3, 1, 1)

    w.lineEdit_2 = QLineEdit(w.IValue)
    w.lineEdit_2.setObjectName(u"lineEdit_2")
    w.lineEdit_2.setEnabled(False)

    w.gridLayout_6.addWidget(w.lineEdit_2, 1, 3, 1, 1)

    w.I_value_z_up_values = QLineEdit(w.IValue)
    w.I_value_z_up_values.setObjectName(u"I_value_z_up_values")

    w.gridLayout_6.addWidget(w.I_value_z_up_values, 21, 3, 1, 1)

    w.line_4 = QFrame(w.IValue)
    w.line_4.setObjectName(u"line_4")
    w.line_4.setFrameShape(QFrame.Shape.VLine)
    w.line_4.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_6.addWidget(w.line_4, 0, 0, 1, 1)

    w.I_value_b_coeff = QLineEdit(w.IValue)
    w.I_value_b_coeff.setObjectName(u"I_value_b_coeff")
    w.I_value_b_coeff.setEnabled(False)

    w.gridLayout_6.addWidget(w.I_value_b_coeff, 13, 3, 1, 1)

    w.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_6.addItem(w.horizontalSpacer_6, 26, 1, 1, 1)

    w.line_6 = QFrame(w.IValue)
    w.line_6.setObjectName(u"line_6")
    w.line_6.setFrameShape(QFrame.Shape.HLine)
    w.line_6.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_6.addWidget(w.line_6, 12, 3, 1, 1)

    w.N_lin_fit = QSpinBox(w.IValue)
    w.N_lin_fit.setObjectName(u"N_lin_fit")
    w.N_lin_fit.setMinimum(1)
    w.N_lin_fit.setMaximum(5)
    w.N_lin_fit.setValue(2)

    w.gridLayout_6.addWidget(w.N_lin_fit, 2, 3, 1, 1)

    w.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_6.addItem(w.horizontalSpacer_5, 26, 0, 1, 1)

    w.line_7 = QFrame(w.IValue)
    w.line_7.setObjectName(u"line_7")
    w.line_7.setFrameShape(QFrame.Shape.HLine)
    w.line_7.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_6.addWidget(w.line_7, 15, 3, 1, 1)

    w.I_value_a_coeff_calc = QLineEdit(w.IValue)
    w.I_value_a_coeff_calc.setObjectName(u"I_value_a_coeff_calc")

    w.gridLayout_6.addWidget(w.I_value_a_coeff_calc, 11, 3, 1, 1)

    w.I_value_z_lw_lim = QLineEdit(w.IValue)
    w.I_value_z_lw_lim.setObjectName(u"I_value_z_lw_lim")
    w.I_value_z_lw_lim.setEnabled(False)

    w.gridLayout_6.addWidget(w.I_value_z_lw_lim, 16, 3, 1, 1)

    w.line_5 = QFrame(w.IValue)
    w.line_5.setObjectName(u"line_5")
    w.line_5.setFrameShape(QFrame.Shape.HLine)
    w.line_5.setFrameShadow(QFrame.Shadow.Sunken)

    w.gridLayout_6.addWidget(w.line_5, 9, 3, 1, 1)

    w.I_value_z_lw_values = QLineEdit(w.IValue)
    w.I_value_z_lw_values.setObjectName(u"I_value_z_lw_values")

    w.gridLayout_6.addWidget(w.I_value_z_lw_values, 17, 3, 1, 1)

    w.Ivaluefit_method = QComboBox(w.IValue)
    w.Ivaluefit_method.setObjectName(u"Ivaluefit_method")

    w.gridLayout_6.addWidget(w.Ivaluefit_method, 26, 3, 1, 1)

    w.I_value_a_coeff = QLineEdit(w.IValue)
    w.I_value_a_coeff.setObjectName(u"I_value_a_coeff")
    w.I_value_a_coeff.setEnabled(False)

    w.gridLayout_6.addWidget(w.I_value_a_coeff, 10, 3, 1, 1)

    w.I_Fit_limits = QLineEdit(w.IValue)
    w.I_Fit_limits.setObjectName(u"I_Fit_limits")

    w.gridLayout_6.addWidget(w.I_Fit_limits, 5, 3, 1, 1)

    w.DECTmenu.addTab(w.IValue, "")
    w.tab_2 = QWidget()
    w.tab_2.setObjectName(u"tab_2")
    w.gridLayout_35 = QGridLayout(w.tab_2)
    w.gridLayout_35.setObjectName(u"gridLayout_35")
    w.RED_method = QComboBox(w.tab_2)
    w.RED_method.setObjectName(u"RED_method")

    w.gridLayout_35.addWidget(w.RED_method, 5, 0, 1, 4)

    w.RED_fit_02_text = QLineEdit(w.tab_2)
    w.RED_fit_02_text.setObjectName(u"RED_fit_02_text")
    w.RED_fit_02_text.setFont(font2)

    w.gridLayout_35.addWidget(w.RED_fit_02_text, 5, 11, 1, 1)

    w.RED_fit_01 = QLineEdit(w.tab_2)
    w.RED_fit_01.setObjectName(u"RED_fit_01")
    w.RED_fit_01.setEnabled(False)
    w.RED_fit_01.setFont(font2)

    w.gridLayout_35.addWidget(w.RED_fit_01, 4, 10, 1, 1)

    w.RED_RMSE = QLineEdit(w.tab_2)
    w.RED_RMSE.setObjectName(u"RED_RMSE")
    w.RED_RMSE.setEnabled(False)
    w.RED_RMSE.setFont(font2)

    w.gridLayout_35.addWidget(w.RED_RMSE, 5, 8, 1, 1)

    w.RED_calc_cal = QPushButton(w.tab_2)
    w.RED_calc_cal.setObjectName(u"RED_calc_cal")

    w.gridLayout_35.addWidget(w.RED_calc_cal, 4, 1, 1, 1)

    w.RED_plot_02 = QWidget(w.tab_2)
    w.RED_plot_02.setObjectName(u"RED_plot_02")

    w.gridLayout_35.addWidget(w.RED_plot_02, 2, 9, 2, 5)

    w.RED_get_ref = QPushButton(w.tab_2)
    w.RED_get_ref.setObjectName(u"RED_get_ref")

    w.gridLayout_35.addWidget(w.RED_get_ref, 4, 0, 1, 1)

    w.RED_r_square = QLineEdit(w.tab_2)
    w.RED_r_square.setObjectName(u"RED_r_square")
    w.RED_r_square.setEnabled(False)
    w.RED_r_square.setFont(font2)

    w.gridLayout_35.addWidget(w.RED_r_square, 4, 8, 1, 1)

    w.RED_fit_01_text = QLineEdit(w.tab_2)
    w.RED_fit_01_text.setObjectName(u"RED_fit_01_text")
    w.RED_fit_01_text.setFont(font2)

    w.gridLayout_35.addWidget(w.RED_fit_01_text, 4, 11, 1, 1)

    w.RED_fit_03 = QLineEdit(w.tab_2)
    w.RED_fit_03.setObjectName(u"RED_fit_03")
    w.RED_fit_03.setEnabled(False)
    w.RED_fit_03.setFont(font2)

    w.gridLayout_35.addWidget(w.RED_fit_03, 4, 12, 1, 1)

    w.RED_plot_01 = QWidget(w.tab_2)
    w.RED_plot_01.setObjectName(u"RED_plot_01")

    w.gridLayout_35.addWidget(w.RED_plot_01, 0, 9, 2, 5)

    w.RED_r_square_text = QLineEdit(w.tab_2)
    w.RED_r_square_text.setObjectName(u"RED_r_square_text")
    w.RED_r_square_text.setFont(font2)

    w.gridLayout_35.addWidget(w.RED_r_square_text, 4, 9, 1, 1)

    w.RED_fit_03_text = QLineEdit(w.tab_2)
    w.RED_fit_03_text.setObjectName(u"RED_fit_03_text")
    w.RED_fit_03_text.setFont(font2)

    w.gridLayout_35.addWidget(w.RED_fit_03_text, 4, 13, 1, 1)

    w.tableRED = QTableWidget(w.tab_2)
    w.tableRED.setObjectName(u"tableRED")

    w.gridLayout_35.addWidget(w.tableRED, 0, 0, 4, 9)

    w.RED_fit_02 = QLineEdit(w.tab_2)
    w.RED_fit_02.setObjectName(u"RED_fit_02")
    w.RED_fit_02.setEnabled(False)
    w.RED_fit_02.setFont(font2)

    w.gridLayout_35.addWidget(w.RED_fit_02, 5, 10, 1, 1)

    w.RED_RMSE_text = QLineEdit(w.tab_2)
    w.RED_RMSE_text.setObjectName(u"RED_RMSE_text")
    w.RED_RMSE_text.setFont(font2)

    w.gridLayout_35.addWidget(w.RED_RMSE_text, 5, 9, 1, 1)

    w.DECTmenu.addTab(w.tab_2, "")
    w.tab_3 = QWidget()
    w.tab_3.setObjectName(u"tab_3")
    w.gridLayout_39 = QGridLayout(w.tab_3)
    w.gridLayout_39.setObjectName(u"gridLayout_39")
    w.Zeff_r_square = QLineEdit(w.tab_3)
    w.Zeff_r_square.setObjectName(u"Zeff_r_square")
    w.Zeff_r_square.setEnabled(False)
    w.Zeff_r_square.setFont(font2)

    w.gridLayout_39.addWidget(w.Zeff_r_square, 2, 5, 1, 1)

    w.Zeff_RMSE = QLineEdit(w.tab_3)
    w.Zeff_RMSE.setObjectName(u"Zeff_RMSE")
    w.Zeff_RMSE.setEnabled(False)
    w.Zeff_RMSE.setFont(font2)

    w.gridLayout_39.addWidget(w.Zeff_RMSE, 3, 5, 1, 1)

    w.Zeff_plot_1 = QWidget(w.tab_3)
    w.Zeff_plot_1.setObjectName(u"Zeff_plot_1")

    w.gridLayout_39.addWidget(w.Zeff_plot_1, 0, 7, 1, 5)

    w.Zeff_RMSE_text = QLineEdit(w.tab_3)
    w.Zeff_RMSE_text.setObjectName(u"Zeff_RMSE_text")
    w.Zeff_RMSE_text.setFont(font2)

    w.gridLayout_39.addWidget(w.Zeff_RMSE_text, 3, 7, 1, 1)

    w.Zeff_fit_01_text = QLineEdit(w.tab_3)
    w.Zeff_fit_01_text.setObjectName(u"Zeff_fit_01_text")
    w.Zeff_fit_01_text.setFont(font2)

    w.gridLayout_39.addWidget(w.Zeff_fit_01_text, 2, 9, 1, 1)

    w.Zeff_fit_1 = QLineEdit(w.tab_3)
    w.Zeff_fit_1.setObjectName(u"Zeff_fit_1")
    w.Zeff_fit_1.setEnabled(False)
    w.Zeff_fit_1.setFont(font2)

    w.gridLayout_39.addWidget(w.Zeff_fit_1, 2, 8, 1, 1)

    w.Zeff_get_ref = QPushButton(w.tab_3)
    w.Zeff_get_ref.setObjectName(u"Zeff_get_ref")

    w.gridLayout_39.addWidget(w.Zeff_get_ref, 2, 0, 1, 1)

    w.Zeff_fit_2 = QLineEdit(w.tab_3)
    w.Zeff_fit_2.setObjectName(u"Zeff_fit_2")
    w.Zeff_fit_2.setEnabled(False)
    w.Zeff_fit_2.setFont(font2)

    w.gridLayout_39.addWidget(w.Zeff_fit_2, 2, 10, 1, 1)

    w.Zeff_calc_cal = QPushButton(w.tab_3)
    w.Zeff_calc_cal.setObjectName(u"Zeff_calc_cal")

    w.gridLayout_39.addWidget(w.Zeff_calc_cal, 2, 1, 1, 1)

    w.tableZeff = QTableWidget(w.tab_3)
    w.tableZeff.setObjectName(u"tableZeff")

    w.gridLayout_39.addWidget(w.tableZeff, 0, 0, 2, 6)

    w.Zeff_method = QComboBox(w.tab_3)
    w.Zeff_method.setObjectName(u"Zeff_method")

    w.gridLayout_39.addWidget(w.Zeff_method, 3, 0, 1, 5)

    w.Zeff_fit_02_text = QLineEdit(w.tab_3)
    w.Zeff_fit_02_text.setObjectName(u"Zeff_fit_02_text")
    w.Zeff_fit_02_text.setFont(font2)

    w.gridLayout_39.addWidget(w.Zeff_fit_02_text, 2, 11, 1, 1)

    w.Zeff_plot_2 = QWidget(w.tab_3)
    w.Zeff_plot_2.setObjectName(u"Zeff_plot_2")

    w.gridLayout_39.addWidget(w.Zeff_plot_2, 1, 7, 1, 5)

    w.Zeff_r_square_text = QLineEdit(w.tab_3)
    w.Zeff_r_square_text.setObjectName(u"Zeff_r_square_text")
    w.Zeff_r_square_text.setFont(font2)

    w.gridLayout_39.addWidget(w.Zeff_r_square_text, 2, 7, 1, 1)

    w.DECTmenu.addTab(w.tab_3, "")
    w.tab_4 = QWidget()
    w.tab_4.setObjectName(u"tab_4")
    w.gridLayout_36 = QGridLayout(w.tab_4)
    w.gridLayout_36.setObjectName(u"gridLayout_36")
    w.Iv_calc_cal = QPushButton(w.tab_4)
    w.Iv_calc_cal.setObjectName(u"Iv_calc_cal")

    w.gridLayout_36.addWidget(w.Iv_calc_cal, 3, 1, 1, 1)

    w.Ivalue_RMSE_text = QLineEdit(w.tab_4)
    w.Ivalue_RMSE_text.setObjectName(u"Ivalue_RMSE_text")
    w.Ivalue_RMSE_text.setFont(font2)

    w.gridLayout_36.addWidget(w.Ivalue_RMSE_text, 3, 3, 1, 1)

    w.Ivalue_plot_1 = QWidget(w.tab_4)
    w.Ivalue_plot_1.setObjectName(u"Ivalue_plot_1")

    w.gridLayout_36.addWidget(w.Ivalue_plot_1, 0, 3, 1, 4)

    w.Ivalue_plot_2 = QWidget(w.tab_4)
    w.Ivalue_plot_2.setObjectName(u"Ivalue_plot_2")

    w.gridLayout_36.addWidget(w.Ivalue_plot_2, 1, 3, 1, 4)

    w.Ivalue_RMSE = QLineEdit(w.tab_4)
    w.Ivalue_RMSE.setObjectName(u"Ivalue_RMSE")
    w.Ivalue_RMSE.setEnabled(False)
    w.Ivalue_RMSE.setFont(font2)

    w.gridLayout_36.addWidget(w.Ivalue_RMSE, 3, 2, 1, 1)

    w.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_36.addItem(w.horizontalSpacer, 3, 6, 1, 1)

    w.Iv_get_ref = QPushButton(w.tab_4)
    w.Iv_get_ref.setObjectName(u"Iv_get_ref")

    w.gridLayout_36.addWidget(w.Iv_get_ref, 3, 0, 1, 1)

    w.tableIv = QTableWidget(w.tab_4)
    w.tableIv.setObjectName(u"tableIv")

    w.gridLayout_36.addWidget(w.tableIv, 0, 0, 2, 3)

    w.horizontalSpacer_26 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_36.addItem(w.horizontalSpacer_26, 3, 4, 1, 1)

    w.DECTmenu.addTab(w.tab_4, "")
    w.tab_7 = QWidget()
    w.tab_7.setObjectName(u"tab_7")
    w.gridLayout_37 = QGridLayout(w.tab_7)
    w.gridLayout_37.setObjectName(u"gridLayout_37")
    w.SPR_plot_1 = QWidget(w.tab_7)
    w.SPR_plot_1.setObjectName(u"SPR_plot_1")

    w.gridLayout_37.addWidget(w.SPR_plot_1, 1, 4, 1, 4)

    w.SPR_ref_energy = QDoubleSpinBox(w.tab_7)
    w.SPR_ref_energy.setObjectName(u"SPR_ref_energy")
    w.SPR_ref_energy.setMaximum(9999.989999999999782)
    w.SPR_ref_energy.setValue(100.000000000000000)

    w.gridLayout_37.addWidget(w.SPR_ref_energy, 2, 6, 1, 1)

    w.lineEdit_46 = QLineEdit(w.tab_7)
    w.lineEdit_46.setObjectName(u"lineEdit_46")
    w.lineEdit_46.setEnabled(False)

    w.gridLayout_37.addWidget(w.lineEdit_46, 2, 3, 1, 1)

    w.SPR_get_ref = QPushButton(w.tab_7)
    w.SPR_get_ref.setObjectName(u"SPR_get_ref")

    w.gridLayout_37.addWidget(w.SPR_get_ref, 2, 0, 1, 1)

    w.SPR_calc_cal = QPushButton(w.tab_7)
    w.SPR_calc_cal.setObjectName(u"SPR_calc_cal")

    w.gridLayout_37.addWidget(w.SPR_calc_cal, 2, 1, 1, 1)

    w.SPR_RMSE_text = QLineEdit(w.tab_7)
    w.SPR_RMSE_text.setObjectName(u"SPR_RMSE_text")

    w.gridLayout_37.addWidget(w.SPR_RMSE_text, 2, 4, 1, 1)

    w.SPR_plot_2 = QWidget(w.tab_7)
    w.SPR_plot_2.setObjectName(u"SPR_plot_2")

    w.gridLayout_37.addWidget(w.SPR_plot_2, 0, 4, 1, 4)

    w.lineEdit_42 = QLineEdit(w.tab_7)
    w.lineEdit_42.setObjectName(u"lineEdit_42")
    w.lineEdit_42.setEnabled(False)

    w.gridLayout_37.addWidget(w.lineEdit_42, 2, 5, 1, 1)

    w.horizontalSpacer_27 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_37.addItem(w.horizontalSpacer_27, 2, 7, 1, 1)

    w.tableSPR = QTableWidget(w.tab_7)
    w.tableSPR.setObjectName(u"tableSPR")

    w.gridLayout_37.addWidget(w.tableSPR, 0, 0, 2, 4)

    w.SPR_particle = QComboBox(w.tab_7)
    w.SPR_particle.setObjectName(u"SPR_particle")

    w.gridLayout_37.addWidget(w.SPR_particle, 2, 2, 1, 1)

    w.DECTmenu.addTab(w.tab_7, "")
    w.tab_8 = QWidget()
    w.tab_8.setObjectName(u"tab_8")
    w.gridLayout_40 = QGridLayout(w.tab_8)
    w.gridLayout_40.setObjectName(u"gridLayout_40")
    w.groupBox_10 = QGroupBox(w.tab_8)
    w.groupBox_10.setObjectName(u"groupBox_10")
    w.gridLayout_38 = QGridLayout(w.groupBox_10)
    w.gridLayout_38.setObjectName(u"gridLayout_38")
    w.Create_DECT_Images = QPushButton(w.groupBox_10)
    w.Create_DECT_Images.setObjectName(u"Create_DECT_Images")

    w.gridLayout_38.addWidget(w.Create_DECT_Images, 0, 0, 1, 5)

    w.checkBox_Im_RED = QCheckBox(w.groupBox_10)
    w.checkBox_Im_RED.setObjectName(u"checkBox_Im_RED")
    w.checkBox_Im_RED.setChecked(True)

    w.gridLayout_38.addWidget(w.checkBox_Im_RED, 1, 0, 1, 1)

    w.checkBox_Im_Zeff = QCheckBox(w.groupBox_10)
    w.checkBox_Im_Zeff.setObjectName(u"checkBox_Im_Zeff")
    w.checkBox_Im_Zeff.setChecked(True)

    w.gridLayout_38.addWidget(w.checkBox_Im_Zeff, 1, 1, 1, 1)

    w.checkBox_Im_SPR = QCheckBox(w.groupBox_10)
    w.checkBox_Im_SPR.setObjectName(u"checkBox_Im_SPR")
    w.checkBox_Im_SPR.setChecked(True)

    w.gridLayout_38.addWidget(w.checkBox_Im_SPR, 1, 4, 1, 1)

    w.checkBox_Im_I = QCheckBox(w.groupBox_10)
    w.checkBox_Im_I.setObjectName(u"checkBox_Im_I")
    w.checkBox_Im_I.setChecked(True)

    w.gridLayout_38.addWidget(w.checkBox_Im_I, 1, 3, 1, 1)


    w.gridLayout_40.addWidget(w.groupBox_10, 3, 0, 3, 1)

    w.groupBox_9 = QGroupBox(w.tab_8)
    w.groupBox_9.setObjectName(u"groupBox_9")
    w.gridLayout_41 = QGridLayout(w.groupBox_9)
    w.gridLayout_41.setObjectName(u"gridLayout_41")
    w.checkBox_newScplot = QCheckBox(w.groupBox_9)
    w.checkBox_newScplot.setObjectName(u"checkBox_newScplot")

    w.gridLayout_41.addWidget(w.checkBox_newScplot, 2, 11, 1, 1)

    w.horizontalSpacer_39 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_41.addItem(w.horizontalSpacer_39, 1, 6, 1, 1)

    w.DECT_exp_scatt_data = QCheckBox(w.groupBox_9)
    w.DECT_exp_scatt_data.setObjectName(u"DECT_exp_scatt_data")

    w.gridLayout_41.addWidget(w.DECT_exp_scatt_data, 2, 13, 1, 1)

    w.DECT_sct_p_size = QSpinBox(w.groupBox_9)
    w.DECT_sct_p_size.setObjectName(u"DECT_sct_p_size")
    w.DECT_sct_p_size.setMinimum(1)
    w.DECT_sct_p_size.setValue(5)

    w.gridLayout_41.addWidget(w.DECT_sct_p_size, 3, 10, 1, 1)

    w.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_41.addItem(w.verticalSpacer_7, 0, 13, 1, 1)

    w.horizontalSpacer_37 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_41.addItem(w.horizontalSpacer_37, 1, 4, 1, 1)

    w.horizontalSpacer_33 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_41.addItem(w.horizontalSpacer_33, 1, 0, 1, 1)

    w.horizontalSpacer_40 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_41.addItem(w.horizontalSpacer_40, 1, 7, 1, 1)

    w.DECT_scatt_N = QSpinBox(w.groupBox_9)
    w.DECT_scatt_N.setObjectName(u"DECT_scatt_N")
    w.DECT_scatt_N.setMinimum(1)
    w.DECT_scatt_N.setMaximum(20000)
    w.DECT_scatt_N.setValue(100)

    w.gridLayout_41.addWidget(w.DECT_scatt_N, 3, 11, 1, 1)

    w.DECT_Scatt_Ax_View = QWidget(w.groupBox_9)
    w.DECT_Scatt_Ax_View.setObjectName(u"DECT_Scatt_Ax_View")

    w.gridLayout_41.addWidget(w.DECT_Scatt_Ax_View, 0, 0, 1, 13)

    w.horizontalSpacer_35 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_41.addItem(w.horizontalSpacer_35, 1, 2, 1, 1)

    w.horizontalSpacer_41 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_41.addItem(w.horizontalSpacer_41, 1, 8, 1, 1)

    w.lineEdit_50 = QLineEdit(w.groupBox_9)
    w.lineEdit_50.setObjectName(u"lineEdit_50")
    w.lineEdit_50.setEnabled(False)

    w.gridLayout_41.addWidget(w.lineEdit_50, 2, 10, 1, 1)

    w.horizontalSpacer_38 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_41.addItem(w.horizontalSpacer_38, 1, 5, 1, 1)

    w.plot_roi_scatter = QPushButton(w.groupBox_9)
    w.plot_roi_scatter.setObjectName(u"plot_roi_scatter")

    w.gridLayout_41.addWidget(w.plot_roi_scatter, 3, 13, 1, 1)

    w.horizontalSpacer_34 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_41.addItem(w.horizontalSpacer_34, 1, 1, 1, 1)

    w.horizontalSpacer_36 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_41.addItem(w.horizontalSpacer_36, 1, 3, 1, 1)

    w.horizontalSpacer_42 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_41.addItem(w.horizontalSpacer_42, 1, 9, 1, 1)

    w.lineEdit_49 = QLineEdit(w.groupBox_9)
    w.lineEdit_49.setObjectName(u"lineEdit_49")
    w.lineEdit_49.setEnabled(False)

    w.gridLayout_41.addWidget(w.lineEdit_49, 2, 5, 1, 5)

    w.scatter_plot_im_02 = QComboBox(w.groupBox_9)
    w.scatter_plot_im_02.setObjectName(u"scatter_plot_im_02")

    w.gridLayout_41.addWidget(w.scatter_plot_im_02, 3, 5, 1, 5)

    w.scatter_plot_im_01 = QComboBox(w.groupBox_9)
    w.scatter_plot_im_01.setObjectName(u"scatter_plot_im_01")

    w.gridLayout_41.addWidget(w.scatter_plot_im_01, 3, 0, 1, 5)

    w.lineEdit_48 = QLineEdit(w.groupBox_9)
    w.lineEdit_48.setObjectName(u"lineEdit_48")
    w.lineEdit_48.setEnabled(False)

    w.gridLayout_41.addWidget(w.lineEdit_48, 2, 0, 1, 5)


    w.gridLayout_40.addWidget(w.groupBox_9, 2, 0, 1, 8)

    w.export_all_DECT_tables = QPushButton(w.tab_8)
    w.export_all_DECT_tables.setObjectName(u"export_all_DECT_tables")

    w.gridLayout_40.addWidget(w.export_all_DECT_tables, 3, 2, 1, 1)

    w.horizontalSpacer_31 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_40.addItem(w.horizontalSpacer_31, 3, 7, 1, 1)

    w.horizontalSpacer_28 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_40.addItem(w.horizontalSpacer_28, 3, 4, 1, 1)

    w.horizontalSpacer_29 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_40.addItem(w.horizontalSpacer_29, 3, 5, 1, 1)

    w.horizontalSpacer_30 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_40.addItem(w.horizontalSpacer_30, 3, 6, 1, 1)

    w.horizontalSpacer_32 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    w.gridLayout_40.addItem(w.horizontalSpacer_32, 3, 8, 1, 1)

    w.DECT_exp_fit_par = QPushButton(w.tab_8)
    w.DECT_exp_fit_par.setObjectName(u"DECT_exp_fit_par")

    w.gridLayout_40.addWidget(w.DECT_exp_fit_par, 4, 2, 1, 1)

    w.DECT_load_fit_par = QPushButton(w.tab_8)
    w.DECT_load_fit_par.setObjectName(u"DECT_load_fit_par")

    w.gridLayout_40.addWidget(w.DECT_load_fit_par, 5, 2, 1, 1)

    w.DECTmenu.addTab(w.tab_8, "")

    w.gridLayout.addWidget(w.DECTmenu, 1, 0, 1, 1)

