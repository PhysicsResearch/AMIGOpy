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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox, QDoubleSpinBox,
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


# Layer panel (qdarkstyle colours): the names are buttons, the active layer's one highlighted
LAYER_PANEL_QSS = """
QPushButton[layerName="true"] {
    background-color: #19232D; color: #DFE1E2; border: 1px solid #455364;
    border-radius: 4px; padding: 3px 10px; text-align: left;
}
QPushButton[layerName="true"]:hover { border-color: #346792; }
QPushButton[layerName="true"]:checked {
    background-color: #346792; border-color: #259AE9; color: #FFFFFF; font-weight: bold;
}
QToolButton[layerCmap="true"] {
    background-color: #19232D; border: 1px solid #455364; border-radius: 4px; padding: 1px;
}
QToolButton[layerCmap="true"]:hover { border-color: #259AE9; }
"""


def create_sidebar(w):
    """
    Create the left sidebar widgets.

    Creates:
    - groupBox: Layer panel: per layer a name button (click: active layer),
      transparency slider / spinbox and colour map button; the active layer
      combo Layer_sel is hidden (fcn_display.layer_panel)
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
    # Layer panel: a click on a layer name makes it the active layer (Ctrl+1..4 too), then its
    # transparency and a colour map button (menu: that layer's map, the active layer stays). The hidden
    # Layer_sel combo (self.layer_selected) stays the one source of the active layer
    # (fcn_display.layer_panel connects it all).
    w.groupBox = QGroupBox(w.centralwidget)
    w.groupBox.setObjectName(u"groupBox")
    w.groupBox.setStyleSheet(LAYER_PANEL_QSS)
    w.gridLayout_14 = QGridLayout(w.groupBox)
    w.gridLayout_14.setObjectName(u"gridLayout_14")
    w.gridLayout_14.setContentsMargins(10, 8, 10, 8)
    w.gridLayout_14.setHorizontalSpacing(8)
    w.gridLayout_14.setVerticalSpacing(6)

    # no title: the slider and value tooltips say what they set (retranslate.py)
    w.layer_name_group = QButtonGroup(w.groupBox)
    w.layer_name_group.setExclusive(True)
    w.layer_name_btns, w.layer_cmap_btns = [], []
    for k in range(4):
        name = QPushButton(w.groupBox)
        name.setObjectName(f"layer_name_btn_{k}")
        name.setProperty("layerName", True)
        name.setProperty("customStyle", True)      # not coloured by button_style
        name.setCheckable(True)
        name.setCursor(Qt.CursorShape.PointingHandCursor)
        name.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        name.setMinimumWidth(76)
        w.layer_name_group.addButton(name, k)
        w.layer_name_btns.append(name)

        sli = QSlider(w.groupBox)
        sli.setObjectName(f"Layer_{k}_alpha_sli")
        sli.setMaximum(100)
        sli.setSingleStep(1)
        sli.setValue(100 if k == 0 else 50)
        sli.setOrientation(Qt.Orientation.Horizontal)
        setattr(w, f"Layer_{k}_alpha_sli", sli)

        spin = QDoubleSpinBox(w.groupBox)
        spin.setObjectName(f"Layer_{k}_alpha_spin")
        spin.setMaximum(1.0)
        spin.setSingleStep(0.05)
        spin.setValue(1.0 if k == 0 else 0.5)
        spin.setFixedWidth(68)
        setattr(w, f"Layer_{k}_alpha_spin", spin)

        cmap = QToolButton(w.groupBox)
        cmap.setObjectName(f"layer_cmap_btn_{k}")
        cmap.setProperty("layerCmap", True)
        cmap.setIconSize(QSize(34, 12))
        cmap.setFixedSize(46, 24)
        cmap.setCursor(Qt.CursorShape.PointingHandCursor)
        w.layer_cmap_btns.append(cmap)

        w.gridLayout_14.addWidget(name, k, 0, 1, 1)
        w.gridLayout_14.addWidget(sli, k, 1, 1, 1)
        w.gridLayout_14.addWidget(spin, k, 2, 1, 1)
        w.gridLayout_14.addWidget(cmap, k, 3, 1, 1)
    w.gridLayout_14.setColumnStretch(1, 1)

    # the active layer (items in init_list_menus.populate_list_menus): kept, hidden
    w.Layer_sel = QComboBox(w.groupBox)
    w.Layer_sel.setObjectName(u"Layer_sel")
    w.Layer_sel.hide()

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

