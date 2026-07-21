# -*- coding: utf-8 -*-
"""
tab_segmentation.py - AMIGOpy GUI Module
===========================================

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


def create_tab_segmentation(w):
    """
    Create the Segmentation module tab (tab_seg).

    Creates the image segmentation interface:
    - toolBox_seg QToolBox with tool pages for different segmentation methods
    - Brush and eraser controls for manual segmentation
    - Morphological operation controls (dilate, erode, open, close)
    - Structure statistics display and export

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
    w.tab_seg = QWidget()
    w.tab_seg.setObjectName(u"tab_seg")
    w.gridLayout_62 = QGridLayout(w.tab_seg)
    w.gridLayout_62.setObjectName(u"gridLayout_62")
    w.segSelectView = QComboBox(w.tab_seg)
    w.segSelectView.setObjectName(u"segSelectView")

    w.gridLayout_62.addWidget(w.segSelectView, 6, 2, 1, 1)

    w.groupBox_segStruct = QGroupBox(w.tab_seg)
    w.groupBox_segStruct.setObjectName(u"groupBox_segStruct")
    w.gridLayout_64 = QGridLayout(w.groupBox_segStruct)
    w.gridLayout_64.setObjectName(u"gridLayout_64")
    w.createSegStruct = QPushButton(w.groupBox_segStruct)
    w.createSegStruct.setObjectName(u"createSegStruct")

    w.gridLayout_64.addWidget(w.createSegStruct, 2, 1, 1, 1)

    w.lineEdit_createStructSeg = QLineEdit(w.groupBox_segStruct)
    w.lineEdit_createStructSeg.setObjectName(u"lineEdit_createStructSeg")
    w.lineEdit_createStructSeg.setEnabled(False)

    w.gridLayout_64.addWidget(w.lineEdit_createStructSeg, 1, 0, 1, 1)

    w.segStructName = QLineEdit(w.groupBox_segStruct)
    w.segStructName.setObjectName(u"segStructName")

    w.gridLayout_64.addWidget(w.segStructName, 1, 1, 1, 2)

    w.initStructCheck = QCheckBox(w.groupBox_segStruct)
    w.initStructCheck.setObjectName(u"initStructCheck")
    w.initStructCheck.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    w.gridLayout_64.addWidget(w.initStructCheck, 2, 0, 1, 1)

    w.deleteSegStruct = QPushButton(w.groupBox_segStruct)
    w.deleteSegStruct.setObjectName(u"deleteSegStruct")

    w.gridLayout_64.addWidget(w.deleteSegStruct, 2, 2, 1, 1)

    w.segStructList = QListWidget(w.groupBox_segStruct)
    w.segStructList.setObjectName(u"segStructList")

    w.gridLayout_64.addWidget(w.segStructList, 0, 0, 1, 3)

    w.gridLayout_64.setRowStretch(0, 1)
    w.gridLayout_64.setColumnStretch(0, 1)
    w.gridLayout_64.setColumnStretch(1, 1)
    w.gridLayout_64.setColumnStretch(2, 1)

    w.gridLayout_62.addWidget(w.groupBox_segStruct, 1, 3, 1, 1)

    w.horizontalLayout_6 = QHBoxLayout()
    w.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
    w.threshMinBox = QLineEdit(w.tab_seg)
    w.threshMinBox.setObjectName(u"threshMinBox")
    w.threshMinBox.setEnabled(False)
    sizePolicy7.setHeightForWidth(w.threshMinBox.sizePolicy().hasHeightForWidth())
    w.threshMinBox.setSizePolicy(sizePolicy7)

    w.horizontalLayout_6.addWidget(w.threshMinBox)

    w.threshMinHU = QLineEdit(w.tab_seg)
    w.threshMinHU.setObjectName(u"threshMinHU")

    w.horizontalLayout_6.addWidget(w.threshMinHU)

    w.threshMaxBox = QLineEdit(w.tab_seg)
    w.threshMaxBox.setObjectName(u"threshMaxBox")
    w.threshMaxBox.setEnabled(False)
    sizePolicy7.setHeightForWidth(w.threshMaxBox.sizePolicy().hasHeightForWidth())
    w.threshMaxBox.setSizePolicy(sizePolicy7)

    w.horizontalLayout_6.addWidget(w.threshMaxBox)

    w.threshMaxHU = QLineEdit(w.tab_seg)
    w.threshMaxHU.setObjectName(u"threshMaxHU")

    w.horizontalLayout_6.addWidget(w.threshMaxHU)

    w.horizontalLayout_6.setStretch(0, 2)
    w.horizontalLayout_6.setStretch(2, 2)

    w.gridLayout_62.addLayout(w.horizontalLayout_6, 3, 3, 1, 1)

    w.VTK_SegView = QWidget(w.tab_seg)
    w.VTK_SegView.setObjectName(u"VTK_SegView")

    w.gridLayout_62.addWidget(w.VTK_SegView, 1, 0, 5, 3)

    w.segViewSlider = QSlider(w.tab_seg)
    w.segViewSlider.setObjectName(u"segViewSlider")
    w.segViewSlider.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_62.addWidget(w.segViewSlider, 6, 0, 1, 2)

    w.VTK_SegHistView = QWidget(w.tab_seg)
    w.VTK_SegHistView.setObjectName(u"VTK_SegHistView")

    w.gridLayout_62.addWidget(w.VTK_SegHistView, 2, 3, 1, 1)

    w.toolBox_seg = QToolBox(w.tab_seg)
    w.toolBox_seg.setObjectName(u"toolBox_seg")
    w.seg_manual_contour = QWidget()
    w.seg_manual_contour.setObjectName(u"seg_manual_contour")
    w.seg_manual_contour.setGeometry(QRect(0, 0, 392, 292))
    w.gridLayout_60 = QGridLayout(w.seg_manual_contour)
    w.gridLayout_60.setObjectName(u"gridLayout_60")
    w.undoSegText = QLineEdit(w.seg_manual_contour)
    w.undoSegText.setObjectName(u"undoSegText")
    w.undoSegText.setEnabled(False)

    w.gridLayout_60.addWidget(w.undoSegText, 3, 1, 1, 1)

    w.undoSeg = QToolButton(w.seg_manual_contour)
    w.undoSeg.setObjectName(u"undoSeg")
    icon = QIcon()
    icon.addFile(u"../Users/gabriel.paivafonseca/Downloads/undo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
    w.undoSeg.setIcon(icon)

    w.gridLayout_60.addWidget(w.undoSeg, 3, 0, 1, 1)

    w.segBrushButton = QToolButton(w.seg_manual_contour)
    w.segBrushButton.setObjectName(u"segBrushButton")
    icon1 = QIcon()
    icon1.addFile(u"../Users/gabriel.paivafonseca/Downloads/brush.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
    w.segBrushButton.setIcon(icon1)
    w.segBrushButton.setCheckable(True)

    w.gridLayout_60.addWidget(w.segBrushButton, 0, 0, 1, 1)

    w.segEraseButton = QToolButton(w.seg_manual_contour)
    w.segEraseButton.setObjectName(u"segEraseButton")
    icon2 = QIcon()
    icon2.addFile(u"../Users/gabriel.paivafonseca/Downloads/eraser.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
    w.segEraseButton.setIcon(icon2)
    w.segEraseButton.setCheckable(True)

    w.gridLayout_60.addWidget(w.segEraseButton, 2, 0, 1, 1)

    w.BrushSizeText = QLineEdit(w.seg_manual_contour)
    w.BrushSizeText.setObjectName(u"BrushSizeText")
    w.BrushSizeText.setEnabled(False)

    w.gridLayout_60.addWidget(w.BrushSizeText, 4, 0, 1, 2)

    w.brushClipHU = QCheckBox(w.seg_manual_contour)
    w.brushClipHU.setObjectName(u"brushClipHU")

    w.gridLayout_60.addWidget(w.brushClipHU, 0, 2, 1, 1)

    w.segBrushBox = QLineEdit(w.seg_manual_contour)
    w.segBrushBox.setObjectName(u"segBrushBox")
    w.segBrushBox.setEnabled(False)
    sizePolicy8.setHeightForWidth(w.segBrushBox.sizePolicy().hasHeightForWidth())
    w.segBrushBox.setSizePolicy(sizePolicy8)

    w.gridLayout_60.addWidget(w.segBrushBox, 0, 1, 1, 1)

    w.BrushSizeSlider = QSlider(w.seg_manual_contour)
    w.BrushSizeSlider.setObjectName(u"BrushSizeSlider")
    w.BrushSizeSlider.setMinimum(1)
    w.BrushSizeSlider.setMaximum(25)
    w.BrushSizeSlider.setValue(5)
    w.BrushSizeSlider.setOrientation(Qt.Orientation.Horizontal)

    w.gridLayout_60.addWidget(w.BrushSizeSlider, 4, 2, 1, 1)

    w.segEraseBox = QLineEdit(w.seg_manual_contour)
    w.segEraseBox.setObjectName(u"segEraseBox")
    w.segEraseBox.setEnabled(False)
    sizePolicy8.setHeightForWidth(w.segEraseBox.sizePolicy().hasHeightForWidth())
    w.segEraseBox.setSizePolicy(sizePolicy8)

    w.gridLayout_60.addWidget(w.segEraseBox, 2, 1, 1, 1)

    w.verticalSpacer_20 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_60.addItem(w.verticalSpacer_20, 5, 1, 1, 1)

    w.gridLayout_60.setColumnStretch(0, 1)
    w.gridLayout_60.setColumnStretch(2, 3)
    w.toolBox_seg.addItem(w.seg_manual_contour, u"Manual contouring && edits")
    w.page_thresholding = QWidget()
    w.page_thresholding.setObjectName(u"page_thresholding")
    w.page_thresholding.setGeometry(QRect(0, 0, 174, 106))
    w.gridLayout_70 = QGridLayout(w.page_thresholding)
    w.gridLayout_70.setObjectName(u"gridLayout_70")
    w.indexMinThreshSeg = QSpinBox(w.page_thresholding)
    w.indexMinThreshSeg.setObjectName(u"indexMinThreshSeg")

    w.gridLayout_70.addWidget(w.indexMinThreshSeg, 0, 2, 1, 1)

    w.indexMaxThreshSeg = QSpinBox(w.page_thresholding)
    w.indexMaxThreshSeg.setObjectName(u"indexMaxThreshSeg")

    w.gridLayout_70.addWidget(w.indexMaxThreshSeg, 1, 2, 1, 1)

    w.lineEdit_75 = QLineEdit(w.page_thresholding)
    w.lineEdit_75.setObjectName(u"lineEdit_75")
    w.lineEdit_75.setEnabled(False)

    w.gridLayout_70.addWidget(w.lineEdit_75, 0, 0, 1, 2)

    w.applyThreshSeg = QPushButton(w.page_thresholding)
    w.applyThreshSeg.setObjectName(u"applyThreshSeg")
    sizePolicy9 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    sizePolicy9.setHorizontalStretch(0)
    sizePolicy9.setVerticalStretch(0)
    sizePolicy9.setHeightForWidth(w.applyThreshSeg.sizePolicy().hasHeightForWidth())
    w.applyThreshSeg.setSizePolicy(sizePolicy9)

    w.gridLayout_70.addWidget(w.applyThreshSeg, 2, 2, 1, 1)

    w.lineEdit_76 = QLineEdit(w.page_thresholding)
    w.lineEdit_76.setObjectName(u"lineEdit_76")
    w.lineEdit_76.setEnabled(False)

    w.gridLayout_70.addWidget(w.lineEdit_76, 1, 0, 1, 2)

    w.verticalSpacer_21 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_70.addItem(w.verticalSpacer_21, 3, 2, 1, 1)

    w.gridLayout_70.setRowStretch(0, 2)
    w.gridLayout_70.setColumnStretch(0, 1)
    w.gridLayout_70.setColumnStretch(2, 1)
    w.toolBox_seg.addItem(w.page_thresholding, u"Thresholding")
    w.morph_oper = QWidget()
    w.morph_oper.setObjectName(u"morph_oper")
    w.morph_oper.setGeometry(QRect(0, 0, 242, 165))
    w.gridLayout_79 = QGridLayout(w.morph_oper)
    w.gridLayout_79.setObjectName(u"gridLayout_79")
    w.lineEdit_70 = QLineEdit(w.morph_oper)
    w.lineEdit_70.setObjectName(u"lineEdit_70")
    w.lineEdit_70.setEnabled(False)
    w.lineEdit_70.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

    w.gridLayout_79.addWidget(w.lineEdit_70, 3, 0, 1, 2)

    w.lineEdit_67 = QLineEdit(w.morph_oper)
    w.lineEdit_67.setObjectName(u"lineEdit_67")
    w.lineEdit_67.setEnabled(False)
    w.lineEdit_67.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    w.lineEdit_67.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

    w.gridLayout_79.addWidget(w.lineEdit_67, 0, 0, 1, 2)

    w.morph_oper_rank = QSpinBox(w.morph_oper)
    w.morph_oper_rank.setObjectName(u"morph_oper_rank")
    w.morph_oper_rank.setMinimum(1)
    w.morph_oper_rank.setMaximum(3)
    w.morph_oper_rank.setValue(2)

    w.gridLayout_79.addWidget(w.morph_oper_rank, 2, 3, 1, 2)

    w.verticalSpacer_23 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    w.gridLayout_79.addItem(w.verticalSpacer_23, 6, 4, 1, 1)

    w.morph_oper_method = QComboBox(w.morph_oper)
    w.morph_oper_method.setObjectName(u"morph_oper_method")

    w.gridLayout_79.addWidget(w.morph_oper_method, 0, 3, 1, 2)

    w.lineEdit_69 = QLineEdit(w.morph_oper)
    w.lineEdit_69.setObjectName(u"lineEdit_69")
    w.lineEdit_69.setEnabled(False)
    w.lineEdit_69.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    w.lineEdit_69.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

    w.gridLayout_79.addWidget(w.lineEdit_69, 2, 0, 1, 2)

    w.lineEdit_68 = QLineEdit(w.morph_oper)
    w.lineEdit_68.setObjectName(u"lineEdit_68")
    w.lineEdit_68.setEnabled(False)
    w.lineEdit_68.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

    w.gridLayout_79.addWidget(w.lineEdit_68, 4, 0, 1, 2)

    w.morph_oper_conn = QSpinBox(w.morph_oper)
    w.morph_oper_conn.setObjectName(u"morph_oper_conn")
    w.morph_oper_conn.setMinimum(1)
    w.morph_oper_conn.setMaximum(3)
    w.morph_oper_conn.setValue(1)

    w.gridLayout_79.addWidget(w.morph_oper_conn, 3, 3, 1, 2)

    w.morph_oper_iter = QSpinBox(w.morph_oper)
    w.morph_oper_iter.setObjectName(u"morph_oper_iter")
    w.morph_oper_iter.setMinimum(1)
    w.morph_oper_iter.setValue(1)

    w.gridLayout_79.addWidget(w.morph_oper_iter, 4, 3, 1, 2)

    w.UndoMorphOper = QPushButton(w.morph_oper)
    w.UndoMorphOper.setObjectName(u"UndoMorphOper")

    w.gridLayout_79.addWidget(w.UndoMorphOper, 5, 4, 1, 1)

    w.ApplyMorphOper = QPushButton(w.morph_oper)
    w.ApplyMorphOper.setObjectName(u"ApplyMorphOper")

    w.gridLayout_79.addWidget(w.ApplyMorphOper, 5, 3, 1, 1)

    w.toolBox_seg.addItem(w.morph_oper, u"Morphological operations")
    w.page = QWidget()
    w.page.setObjectName(u"page")
    w.page.setGeometry(QRect(0, 0, 228, 134))
    w.gridLayout_61 = QGridLayout(w.page)
    w.gridLayout_61.setObjectName(u"gridLayout_61")
    w.calcSegStatsButton = QPushButton(w.page)
    w.calcSegStatsButton.setObjectName(u"calcSegStatsButton")

    w.gridLayout_61.addWidget(w.calcSegStatsButton, 0, 0, 1, 1)

    w.exportSegStatsButton = QPushButton(w.page)
    w.exportSegStatsButton.setObjectName(u"exportSegStatsButton")

    w.gridLayout_61.addWidget(w.exportSegStatsButton, 0, 1, 1, 1)

    w.tableSegStrucStats = QTableWidget(w.page)
    w.tableSegStrucStats.setObjectName(u"tableSegStrucStats")

    w.gridLayout_61.addWidget(w.tableSegStrucStats, 1, 0, 1, 2)

    w.exportSegStrucButton = QPushButton(w.page)
    w.exportSegStrucButton.setObjectName(u"exportSegStrucButton")

    w.gridLayout_61.addWidget(w.exportSegStrucButton, 2, 0, 1, 1)

    w.toolBox_seg.addItem(w.page, u"Export && analyze")

    w.gridLayout_62.addWidget(w.toolBox_seg, 4, 3, 1, 1)

    w.gridLayout_62.setRowStretch(1, 3)
    w.gridLayout_62.setRowStretch(2, 2)
    w.gridLayout_62.setRowStretch(4, 4)
    w.gridLayout_62.setColumnStretch(0, 3)
    w.gridLayout_62.setColumnStretch(2, 1)
    w.gridLayout_62.setColumnStretch(3, 2)
