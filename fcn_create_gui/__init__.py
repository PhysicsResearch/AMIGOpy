# -*- coding: utf-8 -*-
"""
fcn_create_gui - Programmatic GUI Creation Package
----------------------------------------------------

This package replaces the auto-generated uiImGUI.py file (from Qt Designer).
Each module file creates widgets for one logical section of the application,
organized by tab/feature area.

Package structure:
    __init__.py           - This file, exports setup_ui
    setup_ui.py           - Main orchestrator (replaces setupUi)
    common.py             - Shared size policies and fonts
    sidebar.py            - Left sidebar (data tree + layer controls)
    tab_view.py           - View module tab (VTK views, histogram, transforms, ROI)
    tab_3dview.py         - 3D View module tab (volume rendering)
    tab_compare.py        - Compare module tab (side-by-side comparison)
    tab_dect.py           - DECT module tab (dual-energy CT analysis)
    tab_plan.py           - Plan module tab (brachy, EQD2, evaluation, materials)
    tab_iris.py           - IrIS module tab (in-room imaging system)
    tab_breathing_curves.py - Breathing Curves module tab
    tab_segmentation.py   - Segmentation module tab
    tab_3d_printing.py    - 3D Printing module tab
    retranslate.py        - Text/label translations
"""

from .setup_ui import setup_ui

__all__ = ["setup_ui"]
