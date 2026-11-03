"""
Layer panel of the side bar (fcn_create_gui/sidebar.py, fcn_display/layer_panel.py): a click on a layer
name makes it the active layer (self.layer_selected, also changed by Ctrl+1..4 and the module tabs: the
names follow it), and a layer's colour map button sets that layer's map without changing the active one.
"""
from types import SimpleNamespace

import numpy as np
import pytest
import vtk

from fcn_display import colormap_set, layer_panel
from fcn_display.layer_panel import init_layer_panel, set_layer_colormap


class _RenderWindow:
    def Render(self):
        pass


class _View:
    def GetRenderWindow(self):
        return _RenderWindow()


@pytest.fixture
def window(qapp):
    """The side bar on a bare main window, its active layer combo filled as populate_list_menus does."""
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QGridLayout, QSizePolicy, QTabWidget, QWidget
    from fcn_create_gui.retranslate import retranslate_ui
    from fcn_create_gui.sidebar import create_sidebar
    from fcn_init.vtk_comp import init_axial_image_Actor, init_coronal_image_Actor, init_sagittal_image_Actor

    w = SimpleNamespace()
    w.centralwidget = QWidget()
    w.gridLayout_3 = QGridLayout(w.centralwidget)
    w._size_policies = {f"sizePolicy{s}": QSizePolicy() for s in ("", *range(1, 10))}
    w._fonts = {f"font{s}": QFont() for s in ("", 1, 2, 3)}
    create_sidebar(w)
    retranslate_ui(w)
    w.layer_selected = w.Layer_sel
    w.Layer_sel.addItems(["1", "2", "3", "4"])
    # what colormap_set needs: per layer VTK pipelines, the layer colour maps, a module tab, the views
    init_axial_image_Actor(w)
    init_sagittal_image_Actor(w)
    init_coronal_image_Actor(w)
    w.CmapIDX = np.zeros(4)
    w.display_data = {}
    w.tabModules = QTabWidget()
    w.tabModules.addTab(QWidget(), "View")
    w.vtkWidgetAxial = w.vtkWidgetSagittal = w.vtkWidgetCoronal = _View()
    init_layer_panel(w)
    return w


def _checked(w):
    return [btn.isChecked() for btn in w.layer_name_btns]


def test_pmi_and_active_layer_box_are_gone(window):
    w = window
    for name in ("horizontalSlider_5", "doubleSpinBox_7", "lineEdit_22", "lineEdit_24"):
        assert not hasattr(w, name)
    # numbered from 1 like their shortcuts (Ctrl+1 = layer index 0); no title or headers: tooltips instead
    assert [btn.text() for btn in w.layer_name_btns] == ["Layer 1", "Layer 2", "Layer 3", "Layer 4"]
    assert "Ctrl+1" in w.layer_name_btns[0].toolTip()
    assert not hasattr(w, "layer_header_transp") and not hasattr(w, "layer_header_cmap")
    for k in range(4):
        sli, spin = getattr(w, f"Layer_{k}_alpha_sli"), getattr(w, f"Layer_{k}_alpha_spin")
        assert sli.toolTip() == spin.toolTip() and sli.toolTip().startswith(f"Layer {k + 1} transparency")
    assert w.Layer_sel.isHidden() and [w.Layer_0_alpha_spin.value(), w.Layer_1_alpha_spin.value()] == [1.0, 0.5]


def test_clicked_name_is_the_active_layer_and_names_follow_it(window):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    w = window
    assert _checked(w) == [True, False, False, False]
    QTest.mouseClick(w.layer_name_btns[2], Qt.MouseButton.LeftButton)
    assert w.layer_selected.currentIndex() == 2 and _checked(w) == [False, False, True, False]
    QTest.mouseClick(w.layer_name_btns[2], Qt.MouseButton.LeftButton)      # the active one stays active
    assert w.layer_selected.currentIndex() == 2 and _checked(w) == [False, False, True, False]
    w.layer_selected.setCurrentIndex(1)                                     # Ctrl+2, module tabs, ...
    assert _checked(w) == [False, True, False, False]


def test_colour_map_of_another_layer_keeps_the_active_one(window):
    w = window
    w.layer_selected.setCurrentIndex(1)
    set_layer_colormap(w, 3, 4)                                             # Jet on layer 3
    assert w.layer_selected.currentIndex() == 1 and w.CmapIDX[3] == 4 and w.CmapIDX[1] == 0
    # layer 3's image goes through its colour lookup table; layer 1 keeps its window / level pipeline
    mapped = w.imageActorAxial[3].GetMapper().GetInputConnection(0, 0).GetProducer()
    assert isinstance(mapped, vtk.vtkImageMapToColors)
    lut = mapped.GetLookupTable()
    jet = colormap_set.create_colormap(4, lut.GetRange()).GetColor(lut.GetRange()[1])
    assert lut.GetTableValue(255)[:3] == pytest.approx(jet, abs=1 / 255)       # stored with 8 bits
    assert isinstance(w.imageActorAxial[1].GetMapper().GetInputConnection(0, 0).GetProducer(),
                      vtk.vtkImageMapToWindowLevelColors)
    # the buttons show each layer's map
    assert [btn.property("cmap") for btn in w.layer_cmap_btns] == [0, 0, 0, 4]
    assert "Jet" in w.layer_cmap_btns[3].toolTip()


def test_colour_map_menu_lists_the_maps(window, monkeypatch):
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    w = window
    seen = []

    def pick():
        menu = QApplication.activePopupWidget()
        seen.extend(a.text() for a in menu.actions())
        next(a for a in menu.actions() if a.text() == "Hot").trigger()
        menu.close()

    QTimer.singleShot(0, pick)
    layer_panel.show_layer_colormap_menu(w, 2)
    assert seen == list(colormap_set.COLORMAP_NAMES)
    assert w.CmapIDX[2] == 2 and w.layer_selected.currentIndex() == 0
