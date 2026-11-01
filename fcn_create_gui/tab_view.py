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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame, QGraphicsView, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLCDNumber, QLabel,
    QLayout, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QProgressBar, QPushButton, QRadioButton,
    QSizePolicy, QSlider, QSpacerItem, QSpinBox,
    QStatusBar, QTabWidget, QTableView, QTableWidget,
    QTableWidgetItem, QTextEdit, QToolBox, QToolButton,
    QTreeView, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget, QMenu, QScrollArea, QSplitter)
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
except ImportError:
    pass
from fcn_create_gui.range_slider import RangeSlider
from fcn_create_gui.brachy_widgets import CheckTree, ContentWidthTable, FitScrollArea, TrimmedDoubleSpinBox, tool_icon


def create_tab_view(w):
    """
    Create the View module tab (im_display_tab).

    This is the main image viewing area containing:
    - VTK orthogonal view containers (VTK_view_01, VTK_view_02, VTK_view_03)
    - Axial, Sagittal, and Coronal slice sliders
    - tabView01 QTabWidget (west-positioned) with sub-tabs:
      * View: histogram container + MetaData viewer container (MetaViewTable, search)
      * PLAN: brachy plan overlay with channel/dwell display
      * STRUCT: structure list and mask creation
      * IrIS: load/operations/calibration sub-tabs
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

    w.metadata_container = QWidget(w.tab_5)
    w.metadata_container.setObjectName(u"metadata_container")
    w.gridLayout_15 = QGridLayout(w.metadata_container)
    w.gridLayout_15.setObjectName(u"gridLayout_15")
    w.gridLayout_15.setContentsMargins(4, 4, 4, 4)
    w.gridLayout_15.setSpacing(4)

    w.MetaViewTable = QTreeWidget(w.metadata_container)
    __qtreewidgetitem = QTreeWidgetItem()
    __qtreewidgetitem.setText(0, u"Element")
    __qtreewidgetitem.setText(1, u"Value / Subitems")
    w.MetaViewTable.setHeaderItem(__qtreewidgetitem)
    w.MetaViewTable.setObjectName(u"MetaViewTable")
    sizePolicy5 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    sizePolicy5.setHorizontalStretch(0)
    sizePolicy5.setVerticalStretch(0)
    sizePolicy5.setHeightForWidth(w.MetaViewTable.sizePolicy().hasHeightForWidth())
    w.MetaViewTable.setSizePolicy(sizePolicy5)
    w.MetaViewTable.header().setStretchLastSection(True)
    w.gridLayout_15.addWidget(w.MetaViewTable, 0, 0, 1, 2)

    w.lineEdit_64 = QLineEdit(w.metadata_container)
    w.lineEdit_64.setObjectName(u"lineEdit_64")
    w.lineEdit_64.setEnabled(False)
    w.lineEdit_64.setFont(font)
    w.lineEdit_64.setMaximumWidth(60)
    w.gridLayout_15.addWidget(w.lineEdit_64, 1, 0, 1, 1)

    w.metadata_search = QLineEdit(w.metadata_container)
    w.metadata_search.setObjectName(u"metadata_search")
    w.metadata_search.setFont(font)
    w.metadata_search.setPlaceholderText(u"Search metadata...")
    w.gridLayout_15.addWidget(w.metadata_search, 1, 1, 1, 1)

    w.gridLayout_81.addWidget(w.metadata_container, 0, 1, 1, 1)

    w.tabView01.addTab(w.tab_5, "")

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

    # The parts side by side (catheter list, table, Edit, Dose, Style); drag the bars between them to resize
    w.brachy_splitter = QSplitter(Qt.Orientation.Horizontal, w.tab_37)
    w.brachy_splitter.setObjectName(u"brachy_splitter")
    w.brachy_splitter.setChildrenCollapsible(False)
    w.brachy_splitter.setHandleWidth(7)
    w.brachy_splitter.setStyleSheet("QSplitter#brachy_splitter::handle { background-color: #78909c; margin: 6px 2px; border-radius: 1px; }"
                                    " QSplitter#brachy_splitter::handle:hover { background-color: #b0bec5; }")

    # Catheters and dose reference points of the plan; the check boxes show / hide them on the images
    w.brachy_tree = CheckTree(w.brachy_splitter)
    w.brachy_tree.setObjectName(u"brachy_tree")
    w.brachy_tree.setFont(font)
    w.brachy_tree.setColumnCount(1)
    w.brachy_tree.setHeaderHidden(True)
    w.brachy_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    w.brachy_tree.setMinimumWidth(120)  # (names readable: in a narrow window the table gives up space first)
    # rename: click the selected item again or F2 (a double click goes to the item)
    w.brachy_tree.setEditTriggers(QAbstractItemView.EditTrigger.SelectedClicked | QAbstractItemView.EditTrigger.EditKeyPressed)

    w.brachy_splitter.addWidget(w.brachy_tree)

    # Title (what the table lists), the table (as wide as its columns) and, below it,
    # the table mode and the export
    w.brachy_table_panel = QWidget(w.brachy_splitter)
    w.brachy_table_panel.setObjectName(u"brachy_table_panel")
    w.gridLayout_brachy_table = QGridLayout(w.brachy_table_panel)
    w.gridLayout_brachy_table.setObjectName(u"gridLayout_brachy_table")
    w.gridLayout_brachy_table.setContentsMargins(0, 0, 0, 0)
    w.brachy_table_title = QLabel(w.brachy_table_panel)
    w.brachy_table_title.setObjectName(u"brachy_table_title")
    w.brachy_table_title.setFont(font1)
    w.brachy_table_title.setWordWrap(True)
    # the title wraps instead of widening the table part
    w.brachy_table_title.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

    w.gridLayout_brachy_table.addWidget(w.brachy_table_title, 0, 0, 1, 3)

    w.brachy_table_01 = ContentWidthTable(w.brachy_table_panel)
    w.brachy_table_01.setObjectName(u"brachy_table_01")
    font2 = QFont()
    font2.setPointSize(12)
    w.brachy_table_01.setFont(font2)

    w.gridLayout_brachy_table.addWidget(w.brachy_table_01, 1, 0, 1, 3)

    # Click: dwell positions <-> catheter points; the menu also has the reference points
    w.brachy_mode_btn = QToolButton(w.brachy_table_panel)
    w.brachy_mode_btn.setObjectName(u"brachy_mode_btn")
    w.brachy_mode_btn.setFont(font)
    w.brachy_mode_btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
    w.brachy_mode_btn.setMinimumWidth(110)
    w.brachy_mode_menu = QMenu(w.brachy_mode_btn)
    w.brachy_mode_menu.setObjectName(u"brachy_mode_menu")
    w.brachy_mode_act_dwells = w.brachy_mode_menu.addAction(u"")
    w.brachy_mode_act_channels = w.brachy_mode_menu.addAction(u"")
    w.brachy_mode_act_refpts = w.brachy_mode_menu.addAction(u"")
    w.brachy_mode_btn.setMenu(w.brachy_mode_menu)

    w.gridLayout_brachy_table.addWidget(w.brachy_mode_btn, 2, 0, 1, 1)

    w.brachy_export_dw_channels_csv = QPushButton(w.brachy_table_panel)
    w.brachy_export_dw_channels_csv.setObjectName(u"brachy_export_dw_channels_csv")

    w.gridLayout_brachy_table.addWidget(w.brachy_export_dw_channels_csv, 2, 2, 1, 1)
    w.gridLayout_brachy_table.setColumnStretch(1, 1)
    w.gridLayout_brachy_table.setRowStretch(1, 1)

    w.brachy_splitter.addWidget(w.brachy_table_panel)

    # Hidden: the table mode (kept in sync with the Plan module, set with brachy_mode_btn) and
    # the selected catheter (set by clicking it in brachy_tree)
    w.brachy_combobox_01 = QComboBox(w.tab_37)
    w.brachy_combobox_01.setObjectName(u"brachy_combobox_01")
    w.brachy_combobox_01.setVisible(False)
    w.brachy_spinBox_01 = QSpinBox(w.tab_37)
    w.brachy_spinBox_01.setObjectName(u"brachy_spinBox_01")
    w.brachy_spinBox_01.setVisible(False)

    # Catheter editing: tools for the 2D views (toggle buttons), undo, points, catheters,
    # dwell positions and times. In a scroll area (vertical: it keeps the width of its content).
    w.brachy_edit_scroll = FitScrollArea(w.brachy_splitter, keep_width=True)
    w.brachy_edit_scroll.setObjectName(u"brachy_edit_scroll")
    w.brachy_edit_scroll.setWidgetResizable(True)
    w.brachy_edit_scroll.setFrameShape(QFrame.Shape.NoFrame)
    w.brachy_edit_group = QGroupBox(w.brachy_edit_scroll)
    w.brachy_edit_group.setObjectName(u"brachy_edit_group")
    w.gridLayout_brachy_edit = QGridLayout(w.brachy_edit_group)
    w.gridLayout_brachy_edit.setObjectName(u"gridLayout_brachy_edit")
    w.horizontalLayout_brachy_tools = QHBoxLayout()
    w.horizontalLayout_brachy_tools.setObjectName(u"horizontalLayout_brachy_tools")
    w.brachy_tool_move = QToolButton(w.brachy_edit_group)
    w.brachy_tool_move.setObjectName(u"brachy_tool_move")
    w.brachy_tool_move.setIcon(tool_icon('move'))
    w.brachy_tool_move.setIconSize(QSize(24, 24))
    w.brachy_tool_move.setCheckable(True)
    w.horizontalLayout_brachy_tools.addWidget(w.brachy_tool_move)
    w.brachy_tool_translate = QToolButton(w.brachy_edit_group)
    w.brachy_tool_translate.setObjectName(u"brachy_tool_translate")
    w.brachy_tool_translate.setIcon(tool_icon('translate'))
    w.brachy_tool_translate.setIconSize(QSize(24, 24))
    w.brachy_tool_translate.setCheckable(True)
    w.horizontalLayout_brachy_tools.addWidget(w.brachy_tool_translate)
    w.brachy_tool_rotate = QToolButton(w.brachy_edit_group)
    w.brachy_tool_rotate.setObjectName(u"brachy_tool_rotate")
    w.brachy_tool_rotate.setIcon(tool_icon('rotate'))
    w.brachy_tool_rotate.setIconSize(QSize(24, 24))
    w.brachy_tool_rotate.setCheckable(True)
    w.horizontalLayout_brachy_tools.addWidget(w.brachy_tool_rotate)
    w.horizontalLayout_brachy_tools.addSpacing(8)
    w.brachy_undo_btn = QToolButton(w.brachy_edit_group)
    w.brachy_undo_btn.setObjectName(u"brachy_undo_btn")
    w.brachy_undo_btn.setIcon(tool_icon('undo'))
    w.brachy_undo_btn.setIconSize(QSize(24, 24))
    w.brachy_undo_btn.setEnabled(False)
    w.horizontalLayout_brachy_tools.addWidget(w.brachy_undo_btn)
    w.horizontalLayout_brachy_tools.addSpacing(12)
    w.brachy_hold_idd = QCheckBox(w.brachy_edit_group)
    w.brachy_hold_idd.setObjectName(u"brachy_hold_idd")
    w.horizontalLayout_brachy_tools.addWidget(w.brachy_hold_idd)
    w.horizontalLayout_brachy_tools.addStretch()

    w.gridLayout_brachy_edit.addLayout(w.horizontalLayout_brachy_tools, 0, 0, 1, 4)

    w.brachy_point_label = QLabel(w.brachy_edit_group)
    w.brachy_point_label.setObjectName(u"brachy_point_label")

    w.gridLayout_brachy_edit.addWidget(w.brachy_point_label, 1, 0, 1, 1)

    w.brachy_add_point_btn = QPushButton(w.brachy_edit_group)
    w.brachy_add_point_btn.setObjectName(u"brachy_add_point_btn")

    w.gridLayout_brachy_edit.addWidget(w.brachy_add_point_btn, 1, 1, 1, 1)

    w.brachy_del_point_btn = QPushButton(w.brachy_edit_group)
    w.brachy_del_point_btn.setObjectName(u"brachy_del_point_btn")

    w.gridLayout_brachy_edit.addWidget(w.brachy_del_point_btn, 1, 2, 1, 1)

    w.brachy_catheter_edit_label = QLabel(w.brachy_edit_group)
    w.brachy_catheter_edit_label.setObjectName(u"brachy_catheter_edit_label")

    w.gridLayout_brachy_edit.addWidget(w.brachy_catheter_edit_label, 2, 0, 1, 1)

    w.brachy_new_catheter_btn = QPushButton(w.brachy_edit_group)
    w.brachy_new_catheter_btn.setObjectName(u"brachy_new_catheter_btn")
    w.brachy_new_catheter_btn.setCheckable(True)

    w.gridLayout_brachy_edit.addWidget(w.brachy_new_catheter_btn, 2, 1, 1, 1)

    w.brachy_dup_catheter_btn = QPushButton(w.brachy_edit_group)
    w.brachy_dup_catheter_btn.setObjectName(u"brachy_dup_catheter_btn")

    w.gridLayout_brachy_edit.addWidget(w.brachy_dup_catheter_btn, 2, 2, 1, 1)

    w.brachy_del_catheter_btn = QPushButton(w.brachy_edit_group)
    w.brachy_del_catheter_btn.setObjectName(u"brachy_del_catheter_btn")

    w.gridLayout_brachy_edit.addWidget(w.brachy_del_catheter_btn, 2, 3, 1, 1)

    w.brachy_dwells_edit_label = QLabel(w.brachy_edit_group)
    w.brachy_dwells_edit_label.setObjectName(u"brachy_dwells_edit_label")

    w.gridLayout_brachy_edit.addWidget(w.brachy_dwells_edit_label, 3, 0, 1, 1)

    w.brachy_set_dwells_btn = QPushButton(w.brachy_edit_group)
    w.brachy_set_dwells_btn.setObjectName(u"brachy_set_dwells_btn")

    w.gridLayout_brachy_edit.addWidget(w.brachy_set_dwells_btn, 3, 1, 1, 1)

    w.brachy_zero_catheter_btn = QPushButton(w.brachy_edit_group)
    w.brachy_zero_catheter_btn.setObjectName(u"brachy_zero_catheter_btn")

    w.gridLayout_brachy_edit.addWidget(w.brachy_zero_catheter_btn, 3, 2, 1, 1)

    w.brachy_zero_all_btn = QPushButton(w.brachy_edit_group)
    w.brachy_zero_all_btn.setObjectName(u"brachy_zero_all_btn")

    w.gridLayout_brachy_edit.addWidget(w.brachy_zero_all_btn, 3, 3, 1, 1)
    w.gridLayout_brachy_edit.setRowStretch(4, 1)
    w.gridLayout_brachy_edit.setColumnMinimumWidth(1, 70)
    w.gridLayout_brachy_edit.setColumnMinimumWidth(2, 70)
    w.gridLayout_brachy_edit.setColumnMinimumWidth(3, 70)

    w.brachy_edit_scroll.setWidget(w.brachy_edit_group)
    # same background as the other parts (setWidget turns filling on)
    w.brachy_edit_scroll.viewport().setAutoFillBackground(False)
    w.brachy_edit_group.setAutoFillBackground(False)
    w.brachy_splitter.addWidget(w.brachy_edit_scroll)

    # Dose calculation: the source (TG43 source database), the air kerma strength of the plan
    # and the TG43 dose of the plan (into the data tree). In a scroll area (vertical: it keeps
    # the width of its content, the other parts give up space first).
    w.brachy_dose_scroll = FitScrollArea(w.brachy_splitter, keep_width=True)
    w.brachy_dose_scroll.setObjectName(u"brachy_dose_scroll")
    w.brachy_dose_scroll.setWidgetResizable(True)
    w.brachy_dose_scroll.setFrameShape(QFrame.Shape.NoFrame)
    w.brachy_dose_group = QGroupBox(w.brachy_dose_scroll)
    w.brachy_dose_group.setObjectName(u"brachy_dose_group")
    w.gridLayout_brachy_dose = QGridLayout(w.brachy_dose_group)
    w.gridLayout_brachy_dose.setObjectName(u"gridLayout_brachy_dose")
    w.brachy_source_label = QLabel(w.brachy_dose_group)
    w.brachy_source_label.setObjectName(u"brachy_source_label")

    w.gridLayout_brachy_dose.addWidget(w.brachy_source_label, 0, 0, 1, 1)

    w.brachy_dose_source = QComboBox(w.brachy_dose_group)
    w.brachy_dose_source.setObjectName(u"brachy_dose_source")
    w.brachy_dose_source.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

    w.gridLayout_brachy_dose.addWidget(w.brachy_dose_source, 0, 1, 1, 1)

    w.brachy_sk_label = QLabel(w.brachy_dose_group)
    w.brachy_sk_label.setObjectName(u"brachy_sk_label")

    w.gridLayout_brachy_dose.addWidget(w.brachy_sk_label, 1, 0, 1, 1)

    # (typed; Enter or leaving the box sets it)
    w.brachy_sk_spin = TrimmedDoubleSpinBox(w.brachy_dose_group)
    w.brachy_sk_spin.setObjectName(u"brachy_sk_spin")
    w.brachy_sk_spin.setDecimals(2)
    w.brachy_sk_spin.setRange(0.01, 99999.99)
    w.brachy_sk_spin.setValue(40700.0)
    w.brachy_sk_spin.setSuffix(u" U")
    w.brachy_sk_spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
    w.brachy_sk_spin.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    w.brachy_sk_spin.setKeyboardTracking(False)

    w.gridLayout_brachy_dose.addWidget(w.brachy_sk_spin, 1, 1, 1, 1)

    w.brachy_calc_dose_btn = QPushButton(w.brachy_dose_group)
    w.brachy_calc_dose_btn.setObjectName(u"brachy_calc_dose_btn")

    w.gridLayout_brachy_dose.addWidget(w.brachy_calc_dose_btn, 2, 0, 1, 2)
    w.gridLayout_brachy_dose.setRowStretch(3, 1)
    w.gridLayout_brachy_dose.setColumnStretch(2, 1)

    w.brachy_dose_scroll.setWidget(w.brachy_dose_group)
    # same background as the other parts (setWidget turns filling on)
    w.brachy_dose_scroll.viewport().setAutoFillBackground(False)
    w.brachy_dose_group.setAutoFillBackground(False)
    w.brachy_splitter.addWidget(w.brachy_dose_scroll)

    # Colors (each button opens a color dialog) and sizes of the catheter, dwell and
    # reference point overlays, and the size of their labels. In a scroll area, so the
    # Style part can be made narrower than its content (it gives up space first).
    # Not shown at first (Display > Panels > Style).
    w.brachy_style_scroll = FitScrollArea(w.brachy_splitter)
    w.brachy_style_scroll.setObjectName(u"brachy_style_scroll")
    w.brachy_style_scroll.setWidgetResizable(True)
    w.brachy_style_scroll.setFrameShape(QFrame.Shape.NoFrame)
    w.brachy_style_group = QGroupBox(w.brachy_style_scroll)
    w.brachy_style_group.setObjectName(u"brachy_style_group")
    w.gridLayout_brachy_style = QGridLayout(w.brachy_style_group)
    w.gridLayout_brachy_style.setObjectName(u"gridLayout_brachy_style")
    w.gridLayout_brachy_style.setVerticalSpacing(3)
    w.brachy_style_ch_label = QLabel(w.brachy_style_group)
    w.brachy_style_ch_label.setObjectName(u"brachy_style_ch_label")

    w.gridLayout_brachy_style.addWidget(w.brachy_style_ch_label, 0, 0, 1, 1)

    w.brachy_col_ch_point = QToolButton(w.brachy_style_group)
    w.brachy_col_ch_point.setObjectName(u"brachy_col_ch_point")
    w.brachy_col_ch_point.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    w.gridLayout_brachy_style.addWidget(w.brachy_col_ch_point, 0, 1, 1, 1)

    w.brachy_col_ch_line = QToolButton(w.brachy_style_group)
    w.brachy_col_ch_line.setObjectName(u"brachy_col_ch_line")
    w.brachy_col_ch_line.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    w.gridLayout_brachy_style.addWidget(w.brachy_col_ch_line, 0, 2, 1, 1)

    w.brachy_col_ch_selected = QToolButton(w.brachy_style_group)
    w.brachy_col_ch_selected.setObjectName(u"brachy_col_ch_selected")
    w.brachy_col_ch_selected.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    w.gridLayout_brachy_style.addWidget(w.brachy_col_ch_selected, 0, 3, 1, 1)

    w.brachy_col_edit = QToolButton(w.brachy_style_group)
    w.brachy_col_edit.setObjectName(u"brachy_col_edit")
    w.brachy_col_edit.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    w.gridLayout_brachy_style.addWidget(w.brachy_col_edit, 0, 4, 1, 1)

    w.brachy_col_edit_point = QToolButton(w.brachy_style_group)
    w.brachy_col_edit_point.setObjectName(u"brachy_col_edit_point")
    w.brachy_col_edit_point.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    w.gridLayout_brachy_style.addWidget(w.brachy_col_edit_point, 0, 5, 1, 1)

    w.dw_ch_point_size = QSpinBox(w.brachy_style_group)
    w.dw_ch_point_size.setObjectName(u"dw_ch_point_size")
    w.dw_ch_point_size.setFont(font)
    w.dw_ch_point_size.setRange(1, 30)
    w.dw_ch_point_size.setValue(3)

    w.gridLayout_brachy_style.addWidget(w.dw_ch_point_size, 1, 1, 1, 1)

    w.brachy_ov_line_width = QSpinBox(w.brachy_style_group)
    w.brachy_ov_line_width.setObjectName(u"brachy_ov_line_width")
    w.brachy_ov_line_width.setFont(font)
    w.brachy_ov_line_width.setRange(1, 10)
    w.brachy_ov_line_width.setValue(2)

    w.gridLayout_brachy_style.addWidget(w.brachy_ov_line_width, 1, 2, 1, 1)

    w.brachy_style_dw_label = QLabel(w.brachy_style_group)
    w.brachy_style_dw_label.setObjectName(u"brachy_style_dw_label")

    w.gridLayout_brachy_style.addWidget(w.brachy_style_dw_label, 2, 0, 1, 1)

    w.brachy_col_dw_slice = QToolButton(w.brachy_style_group)
    w.brachy_col_dw_slice.setObjectName(u"brachy_col_dw_slice")
    w.brachy_col_dw_slice.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    w.gridLayout_brachy_style.addWidget(w.brachy_col_dw_slice, 2, 1, 1, 1)

    w.brachy_col_dw_other = QToolButton(w.brachy_style_group)
    w.brachy_col_dw_other.setObjectName(u"brachy_col_dw_other")
    w.brachy_col_dw_other.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    w.gridLayout_brachy_style.addWidget(w.brachy_col_dw_other, 2, 2, 1, 1)

    w.brachy_col_dw_zero = QToolButton(w.brachy_style_group)
    w.brachy_col_dw_zero.setObjectName(u"brachy_col_dw_zero")
    w.brachy_col_dw_zero.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    w.gridLayout_brachy_style.addWidget(w.brachy_col_dw_zero, 2, 3, 1, 1)

    w.brachy_ov_dw_size = QDoubleSpinBox(w.brachy_style_group)
    w.brachy_ov_dw_size.setObjectName(u"brachy_ov_dw_size")
    w.brachy_ov_dw_size.setFont(font)
    w.brachy_ov_dw_size.setDecimals(1)
    w.brachy_ov_dw_size.setRange(0.5, 30.0)
    w.brachy_ov_dw_size.setSingleStep(0.5)
    w.brachy_ov_dw_size.setValue(3.0)

    w.gridLayout_brachy_style.addWidget(w.brachy_ov_dw_size, 3, 1, 1, 1)

    w.brachy_ov_dw_edge = QSpinBox(w.brachy_style_group)
    w.brachy_ov_dw_edge.setObjectName(u"brachy_ov_dw_edge")
    w.brachy_ov_dw_edge.setFont(font)
    w.brachy_ov_dw_edge.setRange(1, 10)
    w.brachy_ov_dw_edge.setValue(2)

    w.gridLayout_brachy_style.addWidget(w.brachy_ov_dw_edge, 3, 2, 1, 1)

    w.brachy_ov_dw_fill = QSpinBox(w.brachy_style_group)
    w.brachy_ov_dw_fill.setObjectName(u"brachy_ov_dw_fill")
    w.brachy_ov_dw_fill.setFont(font)
    w.brachy_ov_dw_fill.setRange(0, 100)
    w.brachy_ov_dw_fill.setSingleStep(5)
    w.brachy_ov_dw_fill.setValue(15)

    w.gridLayout_brachy_style.addWidget(w.brachy_ov_dw_fill, 3, 3, 1, 1)

    w.brachy_style_ref_label = QLabel(w.brachy_style_group)
    w.brachy_style_ref_label.setObjectName(u"brachy_style_ref_label")

    w.gridLayout_brachy_style.addWidget(w.brachy_style_ref_label, 4, 0, 1, 1)

    w.brachy_col_ref_slice = QToolButton(w.brachy_style_group)
    w.brachy_col_ref_slice.setObjectName(u"brachy_col_ref_slice")
    w.brachy_col_ref_slice.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    w.gridLayout_brachy_style.addWidget(w.brachy_col_ref_slice, 4, 1, 1, 1)

    w.brachy_col_ref_other = QToolButton(w.brachy_style_group)
    w.brachy_col_ref_other.setObjectName(u"brachy_col_ref_other")
    w.brachy_col_ref_other.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    w.gridLayout_brachy_style.addWidget(w.brachy_col_ref_other, 4, 2, 1, 1)

    w.brachy_ov_ref_size = QDoubleSpinBox(w.brachy_style_group)
    w.brachy_ov_ref_size.setObjectName(u"brachy_ov_ref_size")
    w.brachy_ov_ref_size.setFont(font)
    w.brachy_ov_ref_size.setDecimals(1)
    w.brachy_ov_ref_size.setRange(1.0, 50.0)
    w.brachy_ov_ref_size.setSingleStep(1.0)
    w.brachy_ov_ref_size.setValue(6.0)

    w.gridLayout_brachy_style.addWidget(w.brachy_ov_ref_size, 4, 3, 1, 1)

    w.brachy_ov_ref_width = QSpinBox(w.brachy_style_group)
    w.brachy_ov_ref_width.setObjectName(u"brachy_ov_ref_width")
    w.brachy_ov_ref_width.setFont(font)
    w.brachy_ov_ref_width.setRange(1, 10)
    w.brachy_ov_ref_width.setValue(2)

    w.gridLayout_brachy_style.addWidget(w.brachy_ov_ref_width, 4, 4, 1, 1)

    w.brachy_ov_label_size = QSpinBox(w.brachy_style_group)
    w.brachy_ov_label_size.setObjectName(u"brachy_ov_label_size")
    w.brachy_ov_label_size.setFont(font)
    w.brachy_ov_label_size.setRange(6, 40)
    w.brachy_ov_label_size.setValue(12)

    w.gridLayout_brachy_style.addWidget(w.brachy_ov_label_size, 1, 3, 1, 1)
    w.gridLayout_brachy_style.setRowStretch(5, 1)
    w.gridLayout_brachy_style.setColumnStretch(6, 1)

    w.brachy_style_scroll.setWidget(w.brachy_style_group)
    # same background as the other parts (setWidget turns filling on)
    w.brachy_style_scroll.viewport().setAutoFillBackground(False)
    w.brachy_style_group.setAutoFillBackground(False)
    w.brachy_style_scroll.setVisible(False)
    w.brachy_splitter.addWidget(w.brachy_style_scroll)
    # the last part shown (Dose, or Style when shown) takes the spare width; the others keep
    # the width they were given (update_brachy_panels)
    w.brachy_splitter.setStretchFactor(w.brachy_splitter.indexOf(w.brachy_dose_scroll), 1)

    w.gridLayout_8.addWidget(w.brachy_splitter, 0, 0, 1, 2)

    # Display: the parts shown in the tab (the list always is) and the overlays drawn on the
    # images. The options after a bold box (catheters, dwells, reference points) need that box.
    font_bold = QFont(font)
    font_bold.setBold(True)
    w.brachy_display_group = QGroupBox(w.tab_37)
    w.brachy_display_group.setObjectName(u"brachy_display_group")
    w.brachy_display_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    w.horizontalLayout_brachy_display = QHBoxLayout(w.brachy_display_group)
    w.horizontalLayout_brachy_display.setObjectName(u"horizontalLayout_brachy_display")
    w.brachy_panels_label = QLabel(w.brachy_display_group)
    w.brachy_panels_label.setObjectName(u"brachy_panels_label")
    w.brachy_panels_label.setFont(font_bold)
    w.horizontalLayout_brachy_display.addWidget(w.brachy_panels_label)
    w.brachy_show_table_panel = QCheckBox(w.brachy_display_group)
    w.brachy_show_table_panel.setObjectName(u"brachy_show_table_panel")
    w.brachy_show_table_panel.setChecked(True)
    w.horizontalLayout_brachy_display.addWidget(w.brachy_show_table_panel)
    w.brachy_show_edit_panel = QCheckBox(w.brachy_display_group)
    w.brachy_show_edit_panel.setObjectName(u"brachy_show_edit_panel")
    w.brachy_show_edit_panel.setChecked(True)
    w.horizontalLayout_brachy_display.addWidget(w.brachy_show_edit_panel)
    w.brachy_show_dose_panel = QCheckBox(w.brachy_display_group)
    w.brachy_show_dose_panel.setObjectName(u"brachy_show_dose_panel")
    w.brachy_show_dose_panel.setChecked(True)
    w.horizontalLayout_brachy_display.addWidget(w.brachy_show_dose_panel)
    w.brachy_show_style_panel = QCheckBox(w.brachy_display_group)
    w.brachy_show_style_panel.setObjectName(u"brachy_show_style_panel")
    w.horizontalLayout_brachy_display.addWidget(w.brachy_show_style_panel)
    w.horizontalLayout_brachy_display.addSpacing(8)
    w.brachy_display_sep_0 = QFrame(w.brachy_display_group)
    w.brachy_display_sep_0.setObjectName(u"brachy_display_sep_0")
    w.brachy_display_sep_0.setFrameShape(QFrame.Shape.VLine)
    w.brachy_display_sep_0.setFrameShadow(QFrame.Shadow.Sunken)
    w.horizontalLayout_brachy_display.addWidget(w.brachy_display_sep_0)
    w.horizontalLayout_brachy_display.addSpacing(8)
    w.display_brachy_channel_overlay = QCheckBox(w.brachy_display_group)
    w.display_brachy_channel_overlay.setObjectName(u"display_brachy_channel_overlay")
    w.display_brachy_channel_overlay.setFont(font_bold)
    w.horizontalLayout_brachy_display.addWidget(w.display_brachy_channel_overlay)
    w.brachy_show_ch_points = QCheckBox(w.brachy_display_group)
    w.brachy_show_ch_points.setObjectName(u"brachy_show_ch_points")
    w.brachy_show_ch_points.setChecked(True)
    w.horizontalLayout_brachy_display.addWidget(w.brachy_show_ch_points)
    w.brachy_show_ch_path = QCheckBox(w.brachy_display_group)
    w.brachy_show_ch_path.setObjectName(u"brachy_show_ch_path")
    w.brachy_show_ch_path.setChecked(True)
    w.horizontalLayout_brachy_display.addWidget(w.brachy_show_ch_path)
    w.brachy_show_ch_labels = QCheckBox(w.brachy_display_group)
    w.brachy_show_ch_labels.setObjectName(u"brachy_show_ch_labels")
    w.horizontalLayout_brachy_display.addWidget(w.brachy_show_ch_labels)
    w.horizontalLayout_brachy_display.addSpacing(8)
    w.brachy_display_sep_1 = QFrame(w.brachy_display_group)
    w.brachy_display_sep_1.setObjectName(u"brachy_display_sep_1")
    w.brachy_display_sep_1.setFrameShape(QFrame.Shape.VLine)
    w.brachy_display_sep_1.setFrameShadow(QFrame.Shadow.Sunken)
    w.horizontalLayout_brachy_display.addWidget(w.brachy_display_sep_1)
    w.horizontalLayout_brachy_display.addSpacing(8)
    w.display_dw_overlay = QCheckBox(w.brachy_display_group)
    w.display_dw_overlay.setObjectName(u"display_dw_overlay")
    w.display_dw_overlay.setFont(font_bold)
    w.horizontalLayout_brachy_display.addWidget(w.display_dw_overlay)
    w.brachy_show_dw_zero = QCheckBox(w.brachy_display_group)
    w.brachy_show_dw_zero.setObjectName(u"brachy_show_dw_zero")
    w.brachy_show_dw_zero.setChecked(True)
    w.horizontalLayout_brachy_display.addWidget(w.brachy_show_dw_zero)
    w.horizontalLayout_brachy_display.addSpacing(8)
    w.brachy_display_sep_2 = QFrame(w.brachy_display_group)
    w.brachy_display_sep_2.setObjectName(u"brachy_display_sep_2")
    w.brachy_display_sep_2.setFrameShape(QFrame.Shape.VLine)
    w.brachy_display_sep_2.setFrameShadow(QFrame.Shadow.Sunken)
    w.horizontalLayout_brachy_display.addWidget(w.brachy_display_sep_2)
    w.horizontalLayout_brachy_display.addSpacing(8)
    w.brachy_show_ref_points = QCheckBox(w.brachy_display_group)
    w.brachy_show_ref_points.setObjectName(u"brachy_show_ref_points")
    w.brachy_show_ref_points.setFont(font_bold)
    w.horizontalLayout_brachy_display.addWidget(w.brachy_show_ref_points)
    w.brachy_show_ref_labels = QCheckBox(w.brachy_display_group)
    w.brachy_show_ref_labels.setObjectName(u"brachy_show_ref_labels")
    w.horizontalLayout_brachy_display.addWidget(w.brachy_show_ref_labels)
    w.horizontalLayout_brachy_display.addStretch()

    w.gridLayout_8.addWidget(w.brachy_display_group, 1, 0, 1, 1)

    # Plan: a new plan, save / save as (into the data tree, as a DICOM RT plan made in AMIGOpy);
    # the title has the plan's name and whether it is saved
    w.brachy_plan_group = QGroupBox(w.tab_37)
    w.brachy_plan_group.setObjectName(u"brachy_plan_group")
    w.brachy_plan_group.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    w.horizontalLayout_brachy_plan = QHBoxLayout(w.brachy_plan_group)
    w.horizontalLayout_brachy_plan.setObjectName(u"horizontalLayout_brachy_plan")
    w.brachy_new_plan_btn = QPushButton(w.brachy_plan_group)
    w.brachy_new_plan_btn.setObjectName(u"brachy_new_plan_btn")
    w.brachy_new_plan_btn.setMinimumWidth(46)
    w.horizontalLayout_brachy_plan.addWidget(w.brachy_new_plan_btn)
    w.brachy_save_plan_btn = QPushButton(w.brachy_plan_group)
    w.brachy_save_plan_btn.setObjectName(u"brachy_save_plan_btn")
    w.brachy_save_plan_btn.setMinimumWidth(46)
    w.horizontalLayout_brachy_plan.addWidget(w.brachy_save_plan_btn)
    w.brachy_save_plan_as_btn = QPushButton(w.brachy_plan_group)
    w.brachy_save_plan_as_btn.setObjectName(u"brachy_save_plan_as_btn")
    w.brachy_save_plan_as_btn.setMinimumWidth(60)
    w.horizontalLayout_brachy_plan.addWidget(w.brachy_save_plan_as_btn)

    w.gridLayout_8.addWidget(w.brachy_plan_group, 1, 1, 1, 1)
    w.gridLayout_8.setRowStretch(0, 1)
    w.gridLayout_8.setColumnStretch(0, 1)

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

    # --- MonteCarlo tab: calculation + voxelization grid definition ----------
    w.tab_montecarlo = QWidget()
    w.tab_montecarlo.setObjectName(u"tab_montecarlo")
    w.gridLayout_mc_outer = QGridLayout(w.tab_montecarlo)
    w.gridLayout_mc_outer.setObjectName(u"gridLayout_mc_outer")

    # Sub-tabs (on top): GRID, Source/Scorer, Physics, MCNP, TOPAS
    w.mc_tabs = QTabWidget(w.tab_montecarlo)
    w.mc_tabs.setObjectName(u"mc_tabs")
    w.mc_tabs.setTabPosition(QTabWidget.TabPosition.North)
    w.gridLayout_mc_outer.addWidget(w.mc_tabs, 0, 0, 1, 1)

    w.mc_tab_grid = QWidget()
    w.mc_tab_grid.setObjectName(u"mc_tab_grid")
    w.gridLayout_mc = QGridLayout(w.mc_tab_grid)
    w.gridLayout_mc.setObjectName(u"gridLayout_mc")

    _mc_axes = (("x", u"X (columns / sagittal)"),
                ("y", u"Y (slices / axial)"),
                ("z", u"Z (rows / coronal)"))

    # (prefix, title, accent colour)
    _mc_grids = (("mc_grid", u"Calculation grid", "#ffd900"),
                 ("mc_vox",  u"Voxelization grid (voxels only)", "#ff2626"))

    for col, (prefix, title, accent) in enumerate(_mc_grids):
        gb = QGroupBox(w.mc_tab_grid)
        gb.setObjectName(f"{prefix}_groupbox")
        gb.setTitle(f"{title} (voxel or mm)" if prefix == "mc_grid" else f"{title} (voxel indices only)")
        gb.setStyleSheet(f"QGroupBox {{ border: 1px solid {accent}; border-radius: 4px; margin-top: 8px; }}"
                         f"QGroupBox::title {{ color: {accent}; subcontrol-origin: margin; left: 8px; padding: 0 3px; }}")
        setattr(w, f"{prefix}_groupbox", gb)
        gl = QGridLayout(gb)
        gl.setObjectName(f"gridLayout_{prefix}")
        setattr(w, f"gridLayout_{prefix}", gl)

        lbl_min = QLabel(u"Min (vox)", gb)
        lbl_range = QLabel(u"Range", gb)
        lbl_max = QLabel(u"Max (vox)", gb)
        lbl_res = QLabel(u"Res. (mm)", gb)
        for _hl in (lbl_min, lbl_range, lbl_max, lbl_res):
            _hl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setattr(w, f"{prefix}_header_min", lbl_min)
        setattr(w, f"{prefix}_header_max", lbl_max)

        gl.addWidget(lbl_min, 0, 1, 1, 1)
        gl.addWidget(lbl_range, 0, 2, 1, 1)
        gl.addWidget(lbl_max, 0, 3, 1, 1)
        gl.addWidget(lbl_res, 0, 4, 1, 1)
        gl.setColumnStretch(2, 1)

        for r, (ax, label) in enumerate(_mc_axes, start=1):
            ax_lbl = QLabel(label, gb)
            setattr(w, f"{prefix}_lbl_{ax}", ax_lbl)
            gl.addWidget(ax_lbl, r, 0, 1, 1)
            for c, kind in ((1, "min"), (3, "max")):
                if prefix == "mc_grid":
                    sb = QDoubleSpinBox(gb)
                    sb.setDecimals(0)
                    sb.setRange(-99999.0, 99999.0)
                    sb.setSingleStep(1.0)
                else:
                    sb = QSpinBox(gb)
                    sb.setRange(0, 99999)
                sb.setObjectName(f"{prefix}_{ax}{kind}")
                sb.setMinimumWidth(75)
                sb.setFont(font)
                setattr(w, f"{prefix}_{ax}{kind}", sb)
                gl.addWidget(sb, r, c, 1, 1)
            # Two-handle slider, kept in sync with the Min/Max boxes (see mc_grid.py)
            rs = RangeSlider(gb, accent=accent)
            rs.setObjectName(f"{prefix}_{ax}slider")
            rs.setMinimumWidth(160)
            rs.setRange(0, 511)
            rs.setValues(0, 0)
            setattr(w, f"{prefix}_{ax}slider", rs)
            gl.addWidget(rs, r, 2, 1, 1)
            # Resolution (bin size) along this axis, in mm
            res = QDoubleSpinBox(gb)
            res.setObjectName(f"{prefix}_{ax}res")
            res.setDecimals(8)
            res.setRange(0.00000001, 1000.0)
            res.setSingleStep(0.1)
            res.setValue(1.0)
            res.setMinimumWidth(100)
            res.setFont(font)
            if prefix == "mc_vox":
                res.setEnabled(False)
                res.setToolTip(u"Voxel size matches the image voxel size (editing disabled)")
            setattr(w, f"{prefix}_{ax}res", res)
            gl.addWidget(res, r, 4, 1, 1)

        cb = QCheckBox(gb)
        cb.setObjectName(f"{prefix}_display")
        cb.setText(u"Display")
        cb.setChecked(False)
        setattr(w, f"{prefix}_display", cb)
        gl.addWidget(cb, 4, 0, 1, 1)

        btn = QPushButton(gb)
        btn.setObjectName(f"{prefix}_fit_btn")
        btn.setText(u"Fit to image")
        setattr(w, f"{prefix}_fit_btn", btn)
        gl.addWidget(btn, 4, 1, 1, 1)

        if prefix == "mc_grid":
            btn_ref = QPushButton(gb)
            btn_ref.setObjectName(f"{prefix}_ref_res_btn")
            btn_ref.setText(u"= Ref. image")
            btn_ref.setToolTip(u"Set calculation grid resolution to match reference image voxel size")
            setattr(w, f"{prefix}_ref_res_btn", btn_ref)
            gl.addWidget(btn_ref, 4, 2, 1, 1)

            lbl_unit = QLabel(u"Unit:", gb)
            lbl_unit.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            gl.addWidget(lbl_unit, 4, 3, 1, 1)

            combo = QComboBox(gb)
            combo.setObjectName(f"{prefix}_mode_combo")
            combo.addItems([u"voxel", u"mm"])
            combo.setMinimumWidth(75)
            setattr(w, f"{prefix}_mode_combo", combo)
            gl.addWidget(combo, 4, 4, 1, 1)

        info = QLabel(gb)
        info.setObjectName(f"{prefix}_info")
        info.setText(u"-")
        setattr(w, f"{prefix}_info", info)
        gl.addWidget(info, 5, 0, 1, 5)

        w.gridLayout_mc.addWidget(gb, 0, col, 1, 1)

    w.gridLayout_mc.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum), 0, 2, 1, 1)
    w.gridLayout_mc.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 1, 0, 1, 1)

    w.mc_tabs.addTab(w.mc_tab_grid, u"GRID")

    # Material Assignment and Density Map (moved here from Plan)
    from fcn_create_gui.tab_plan import create_tab_mat_assignment, create_tab_density_map
    create_tab_mat_assignment(w)
    w.mc_tabs.addTab(w.tab_mat_assignment, u"Material Assignment")
    w.mc_tabs.addTab(w.tab_mat_composition, u"Mat. Composition")
    create_tab_density_map(w)
    w.mc_tabs.addTab(w.density_map_tab, u"Density Map")

    # Placeholder sub-tabs (to be populated later)
    for _name, _label in (("mc_tab_source",  u"Source/Scorer"),
                          ("mc_tab_physics", u"Physics"),
                          ("mc_tab_mcnp",    u"MCNP"),
                          ("mc_tab_topas",   u"TOPAS")):
        _t = QWidget()
        _t.setObjectName(_name)
        QGridLayout(_t).setObjectName(f"gridLayout_{_name}")
        setattr(w, _name, _t)
        w.mc_tabs.addTab(_t, _label)

    # MCNP sub-tab: options, sources, tallies, simulation settings & input generation
    _gl_mcnp = w.mc_tab_mcnp.layout()

    # 1. Scoring / Tallies options
    gb_tallies = QGroupBox(u"Tallies / Scoring Options", w.mc_tab_mcnp)
    gb_tallies.setObjectName(u"mcnp_gb_tallies")
    gb_tallies.setStyleSheet(
        "QGroupBox { border: 1px solid #4a90e2; border-radius: 4px; margin-top: 8px; font-weight: bold; }"
        "QGroupBox::title { color: #4a90e2; subcontrol-origin: margin; left: 8px; padding: 0 3px; }"
    )
    vbox_tallies = QVBoxLayout(gb_tallies)

    w.mcnp_chk_dwater_water = QCheckBox(u"Dwater in water (Track length)", gb_tallies)
    w.mcnp_chk_dwater_water.setObjectName(u"mcnp_chk_dwater_water")
    vbox_tallies.addWidget(w.mcnp_chk_dwater_water)

    w.mcnp_chk_dwater_med = QCheckBox(u"Dwater in medium (Track length)", gb_tallies)
    w.mcnp_chk_dwater_med.setObjectName(u"mcnp_chk_dwater_med")
    vbox_tallies.addWidget(w.mcnp_chk_dwater_med)

    w.mcnp_chk_dmed_med_tl = QCheckBox(u"Dose to medium in Medium (Track length)", gb_tallies)
    w.mcnp_chk_dmed_med_tl.setObjectName(u"mcnp_chk_dmed_med_tl")
    vbox_tallies.addWidget(w.mcnp_chk_dmed_med_tl)

    w.mcnp_chk_dmed_med_ed = QCheckBox(u"Dose to medium in medium (Energy deposition)", gb_tallies)
    w.mcnp_chk_dmed_med_ed.setObjectName(u"mcnp_chk_dmed_med_ed")
    vbox_tallies.addWidget(w.mcnp_chk_dmed_med_ed)

    _gl_mcnp.addWidget(gb_tallies, 0, 0, 1, 1)

    # 2. Source Selection & Simulation settings
    gb_sim = QGroupBox(u"Source & Simulation Settings", w.mc_tab_mcnp)
    gb_sim.setObjectName(u"mcnp_gb_sim")
    gb_sim.setStyleSheet(
        "QGroupBox { border: 1px solid #50e3c2; border-radius: 4px; margin-top: 8px; font-weight: bold; }"
        "QGroupBox::title { color: #50e3c2; subcontrol-origin: margin; left: 8px; padding: 0 3px; }"
    )
    vbox_sim = QVBoxLayout(gb_sim)

    lbl_source = QLabel(u"Source:", gb_sim)
    vbox_sim.addWidget(lbl_source)
    w.mcnp_source_combo = QComboBox(gb_sim)
    w.mcnp_source_combo.setObjectName(u"mcnp_source_combo")
    w.mcnp_source_combo.addItems([
        u"None (External beam / custom)",
        u"MicroSelectron-v2",
        u"GammaMedPlus",
        u"Flexisource",
        u"TG-186",
        u"Axxent",
    ])
    vbox_sim.addWidget(w.mcnp_source_combo)

    w.mcnp_chk_std_cards = QCheckBox(u"Include standard cards (PHYS:P, cut:p, prdmp, dbcn)", gb_sim)
    w.mcnp_chk_std_cards.setObjectName(u"mcnp_chk_std_cards")
    w.mcnp_chk_std_cards.setChecked(True)
    vbox_sim.addWidget(w.mcnp_chk_std_cards)

    hbox_nps = QHBoxLayout()
    lbl_nps = QLabel(u"nps (N):", gb_sim)
    w.mcnp_nps_input = QLineEdit(gb_sim)
    w.mcnp_nps_input.setObjectName(u"mcnp_nps_input")
    w.mcnp_nps_input.setText(u"1e6")
    hbox_nps.addWidget(lbl_nps)
    hbox_nps.addWidget(w.mcnp_nps_input)
    vbox_sim.addLayout(hbox_nps)

    _gl_mcnp.addWidget(gb_sim, 0, 1, 1, 1)

    # 3. Actions / Generation
    gb_actions = QGroupBox(u"Actions", w.mc_tab_mcnp)
    gb_actions.setObjectName(u"mcnp_gb_actions")
    gb_actions.setStyleSheet(
        "QGroupBox { border: 1px solid #f5a623; border-radius: 4px; margin-top: 8px; font-weight: bold; }"
        "QGroupBox::title { color: #f5a623; subcontrol-origin: margin; left: 8px; padding: 0 3px; }"
    )
    vbox_actions = QVBoxLayout(gb_actions)

    w.mcnp_create_lattice_btn = QPushButton(gb_actions)
    w.mcnp_create_lattice_btn.setObjectName(u"mcnp_create_lattice_btn")
    w.mcnp_create_lattice_btn.setText(u"Create MCNP lattice map")
    vbox_actions.addWidget(w.mcnp_create_lattice_btn)

    w.mcnp_create_input_btn = QPushButton(gb_actions)
    w.mcnp_create_input_btn.setObjectName(u"mcnp_create_input_btn")
    w.mcnp_create_input_btn.setText(u"Create input")
    vbox_actions.addWidget(w.mcnp_create_input_btn)

    vbox_actions.addStretch(1)

    _gl_mcnp.addWidget(gb_actions, 0, 2, 1, 1)

    _gl_mcnp.setColumnStretch(0, 1)
    _gl_mcnp.setColumnStretch(1, 1)
    _gl_mcnp.setColumnStretch(2, 1)
    _gl_mcnp.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 1, 0, 1, 3)

    w.mc_tabs.setCurrentIndex(0)

    w.tabView01.addTab(w.tab_montecarlo, "")

    w.gridLayout_4.addWidget(w.tabView01, 2, 0, 1, 3)

