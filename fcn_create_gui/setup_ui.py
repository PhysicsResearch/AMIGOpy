# -*- coding: utf-8 -*-
"""
setup_ui.py - Main GUI Setup Orchestrator
============================================

This is the entry point that replaces Ui_AMIGOpy.setupUi(). It orchestrates
the creation of all GUI components by calling module-specific creator functions.

Tabs that are not immediately visible on startup are created lazily — their
widgets are only instantiated when the user first switches to that tab,
improving application launch time.

This file is part of the fcn_create_gui package which replaces the
auto-generated uiImGUI.py (from Qt Designer / pyside6-uic).
"""

from PySide6.QtCore import Qt, QMetaObject, QRect
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QTabWidget, QGridLayout, QSizePolicy, QLabel, QStatusBar,
)

from .common import create_size_policies, create_fonts
from .sidebar import create_sidebar
from .tab_view import create_tab_view
from .retranslate import retranslate_ui


# --- Lazy tab definitions ---
# Maps tab index → (widget_attr_name, module_name, creator_function_name, tab_label)
# These tabs are NOT created at startup — only when the user first clicks on them.
_LAZY_TABS = {
    1: ("_3Dview",           "tab_3dview",           "create_tab_3dview"),
    2: ("im_compare_tab",    "tab_compare",          "create_tab_compare"),
    3: ("DECT_tab",          "tab_dect",             "create_tab_dect"),
    4: ("Plan_tab",          "tab_plan",             "create_tab_plan"),
    5: ("IrIS_tab",          "tab_iris",             "create_tab_iris"),
    6: ("tab_BrCv",          "tab_breathing_curves", "create_tab_breathing_curves"),
    7: ("tab_seg",           "tab_segmentation",     "create_tab_segmentation"),
    8: ("tab_3DP",           "tab_3d_printing",      "create_tab_3d_printing"),
}


def _on_tab_changed(w, index):
    """
    Lazy-load handler: when a tabModules tab is selected for the first time,
    replace its placeholder widget with the real content.

    This is connected to tabModules.currentChanged signal.
    """
    if index in w._lazy_loaded or index not in _LAZY_TABS:
        return

    attr_name, module_name, func_name = _LAZY_TABS[index]

    # Dynamically import and call the creation function
    import importlib
    mod = importlib.import_module(f".{module_name}", package="fcn_create_gui")
    create_func = getattr(mod, func_name)

    # The placeholder widget was already set as an attribute.
    # The creator function will overwrite w.<attr_name> with the real widget.
    old_placeholder = getattr(w, attr_name)

    # Mark as loaded early to prevent recursion during signal emissions
    w._lazy_loaded.add(index)

    # Call the creator — it sets w.<attr_name> to a new, fully-populated widget
    create_func(w)

    # Replace the placeholder in tabModules with the real widget safely
    real_widget = getattr(w, attr_name)
    w.tabModules.blockSignals(True)
    tab_idx = w.tabModules.indexOf(old_placeholder)
    if tab_idx >= 0:
        tab_text = w.tabModules.tabText(tab_idx)
        w.tabModules.removeTab(tab_idx)
        w.tabModules.insertTab(tab_idx, real_widget, tab_text)
        w.tabModules.setCurrentIndex(tab_idx)
    w.tabModules.blockSignals(False)

    # Apply translations for newly created widgets
    retranslate_ui(w)

    # Re-run initializations for the newly instantiated tab
    from fcn_init.init_list_menus import populate_list_menus
    from fcn_init.init_buttons import initialize_software_buttons
    from fcn_init.init_tables import initialize_software_tables
    
    populate_list_menus(w)
    initialize_software_tables(w)
    initialize_software_buttons(w)

    if attr_name == "tab_3DP":
        from fcn_init.create_3D_database_tab import setup_3d_database_tab, setup_mat_mix_tab, setup_view_and_fit_tab
        setup_3d_database_tab(w)
        setup_mat_mix_tab(w)
        setup_view_and_fit_tab(w)


def setup_ui(w):
    """
    Create the complete GUI for the AMIGOpy application.

    This replaces the old Ui_AMIGOpy.setupUi() method. It:
    1. Configures the main window (size, policies)
    2. Creates shared size policies and fonts (stored on w._size_policies, w._fonts)
    3. Creates the central widget, main grid layout, and status bar
    4. Creates the sidebar (data tree + layer controls) — always loaded
    5. Creates the tabModules QTabWidget with 9 module tabs
    6. Eagerly creates the View tab (always visible on startup)
    7. Creates lightweight placeholders for all other tabs (lazy loading)
    8. Applies text translations
    9. Connects lazy-load handler for deferred tab creation

    Args:
        w: The main application window (QMainWindow instance).
    """
    # --- Window setup ---
    if not w.objectName():
        w.setObjectName("AMIGOpy")
    w.resize(1379, 1122)

    sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(w.sizePolicy().hasHeightForWidth())
    w.setSizePolicy(sizePolicy)
    w.setAutoFillBackground(False)
    w.setInputMethodHints(Qt.InputMethodHint.ImhNone)

    # --- Store shared resources for use by all module creators ---
    w._size_policies = create_size_policies()
    w._fonts = create_fonts()

    # --- Central widget and main layout ---
    w.centralwidget = QWidget(w)
    w.centralwidget.setObjectName("centralwidget")

    w.label = QLabel(w.centralwidget)
    w.label.setObjectName("label")
    w.label.setGeometry(QRect(481, 1089, 16, 16))

    w.gridLayout_3 = QGridLayout(w.centralwidget)
    w.gridLayout_3.setObjectName("gridLayout_3")

    w.gridLayout_50 = QGridLayout()
    w.gridLayout_50.setObjectName("gridLayout_50")
    w.gridLayout_3.addLayout(w.gridLayout_50, 3, 0, 1, 1)

    # --- Create sidebar (always needed at startup) ---
    create_sidebar(w)

    # --- Create tabModules (the main module tab widget) ---
    w.tabModules = QTabWidget(w.centralwidget)
    w.tabModules.setObjectName("tabModules")

    # --- Eagerly create the View tab (tab index 0, always visible first) ---
    create_tab_view(w)
    w.tabModules.addTab(w.im_display_tab, "")

    # --- Create placeholder widgets for lazy-loaded tabs ---
    for idx in sorted(_LAZY_TABS.keys()):
        attr_name, module_name, func_name = _LAZY_TABS[idx]
        placeholder = QWidget()
        placeholder.setObjectName(attr_name)
        setattr(w, attr_name, placeholder)
        w.tabModules.addTab(placeholder, "")

    # --- Add tabModules to main layout ---
    w.gridLayout_3.addWidget(w.tabModules, 2, 0, 1, 2)

    # --- Set central widget ---
    w.setCentralWidget(w.centralwidget)

    # --- Status bar ---
    w.statusbar = QStatusBar(w)
    w.statusbar.setObjectName("statusbar")
    w.setStatusBar(w.statusbar)

    # --- Set initial tab indices ---
    w.tabModules.setCurrentIndex(0)
    w.tabView01.setCurrentIndex(0)
    w.tabWidget_10.setCurrentIndex(0)
    w.tabWidget_3.setCurrentIndex(0)
    w.tabWidget_4.setCurrentIndex(0)
    w.tabWidget_8.setCurrentIndex(0)
    w.tabWidget_9.setCurrentIndex(0)

    # --- Apply translations ---
    retranslate_ui(w)

    # --- Connect slots by name ---
    QMetaObject.connectSlotsByName(w)

    # --- Connect lazy loading (AFTER translations, so tab text is set) ---
    w._lazy_loaded = {0}  # View tab (index 0) is already loaded
    w.tabModules.currentChanged.connect(lambda idx: _on_tab_changed(w, idx))
