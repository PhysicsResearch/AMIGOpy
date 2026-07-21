# -*- coding: utf-8 -*-
"""
common.py - Shared Size Policies and Fonts
--------------------------------------------

Defines reusable QSizePolicy and QFont objects used across all GUI modules.
These were originally defined once at the top of setupUi() and referenced
throughout the 6700-line file. Centralizing them here avoids duplication.

This file is part of the fcn_create_gui package which replaces the
auto-generated uiImGUI.py.
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy


def create_size_policies():
    """
    Create and return all size policies used throughout the GUI.
    """
    sp0 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
    sp0.setHorizontalStretch(0)
    sp0.setVerticalStretch(0)

    sp1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    sp1.setHorizontalStretch(0)
    sp1.setVerticalStretch(0)

    sp2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
    sp2.setHorizontalStretch(0)
    sp2.setVerticalStretch(0)

    sp3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    sp3.setHorizontalStretch(0)
    sp3.setVerticalStretch(0)

    sp4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    sp4.setHorizontalStretch(0)
    sp4.setVerticalStretch(0)

    sp5 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    sp5.setHorizontalStretch(0)
    sp5.setVerticalStretch(0)

    sp6 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
    sp6.setHorizontalStretch(0)
    sp6.setVerticalStretch(0)

    sp7 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
    sp7.setHorizontalStretch(0)
    sp7.setVerticalStretch(0)

    sp8 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
    sp8.setHorizontalStretch(0)
    sp8.setVerticalStretch(0)

    sp9 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    sp9.setHorizontalStretch(0)
    sp9.setVerticalStretch(0)

    return {
        'sizePolicy': sp0,
        'sizePolicy1': sp1,
        'sizePolicy2': sp2,
        'sizePolicy3': sp3,
        'sizePolicy4': sp4,
        'sizePolicy5': sp5,
        'sizePolicy6': sp6,
        'sizePolicy7': sp7,
        'sizePolicy8': sp8,
        'sizePolicy9': sp9,
    }


def create_fonts():
    """
    Create and return all standard fonts used throughout the GUI.
    """
    font = QFont()
    font.setPointSize(10)

    font1 = QFont()
    font1.setPointSize(10)
    font1.setBold(True)

    font2 = QFont()
    font2.setPointSize(12)

    font3 = QFont()
    font3.setPointSize(12)
    font3.setBold(True)

    return {
        'font': font,
        'font1': font1,
        'font2': font2,
        'font3': font3,
    }
