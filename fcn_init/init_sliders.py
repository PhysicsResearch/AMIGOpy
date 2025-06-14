from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout


def initialize_sliders(self):
    self.View3D_Threshold_slider = build_range_slider(self.View3D_Threshold_slider_PH)


def build_range_slider(placeholder: QtWidgets.QWidget,
                       low=500, high=1500, span=(0, 2000)) -> QRangeSlider:
    """Remove all old children, then insert a fresh two-thumb slider."""
    # 1) purge old widgets that might obscure the new one
    for child in placeholder.findChildren(QtWidgets.QWidget):
        child.deleteLater()

    # 2) layout with zero margins
    layout = placeholder.layout() or QtWidgets.QVBoxLayout(placeholder)
    layout.setContentsMargins(0, 0, 0, 0)

    # 3) make the slider big enough to see
    slider = QRangeSlider(Qt.Horizontal, placeholder)
    slider.setMinimumHeight(40)
    slider.setRange(*span)
    slider.setValue((low, high))

    # 4) simple stylesheet without left/right margin
    slider.setStyleSheet("""
        QRangeSlider::groove:horizontal  {height:8px; background:#ccc; border-radius:4px;}
        QRangeSlider::sub-page:horizontal{background:#3498db; border-radius:4px;}
        QRangeSlider::handle:horizontal  {background:white; border:2px solid #3498db;
                                          width:20px; height:20px; margin:-6px 0; border-radius:10px;}
    """)

    layout.addWidget(slider)
    slider.raise_()                     # be sure it sits on top

    slider.valueChanged.connect(lambda v: print("range →", v))
    return slider