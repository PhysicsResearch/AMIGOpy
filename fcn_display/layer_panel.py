# -*- coding: utf-8 -*-
"""
layer_panel.py - layer panel of the side bar (fcn_create_gui/sidebar.py)
=======================================================================
- A click on a layer name makes it the active layer (Ctrl+1..4 too). self.layer_selected, the
  hidden Layer_sel combo, stays the one source of the active layer (many modules read it): the
  names follow it, whoever changes it.
- Each layer has its transparency and a colour map button: its icon shows the layer's map
  (CmapIDX) and its menu sets that layer's map without changing the active layer
  (colormap_set.set_color_map(self, layer)).
"""
from PySide6.QtGui import QColor, QIcon, QImage, QPixmap
from PySide6.QtWidgets import QMenu

from fcn_display.colormap_set import COLORMAP_NAMES, create_colormap, set_color_map

ICON_SIZE = (34, 12)


def colormap_pixmap(index, width=ICON_SIZE[0], height=ICON_SIZE[1]):
    """A gradient of a colour map (create_colormap index), low values on the left."""
    ctf = create_colormap(int(index), [0.0, 1.0])
    image = QImage(width, height, QImage.Format.Format_RGB32)
    for x in range(width):
        r, g, b = ctf.GetColor(x / (width - 1))
        color = QColor.fromRgbF(r, g, b)
        for y in range(height):
            image.setPixelColor(x, y, color)
    return QPixmap.fromImage(image)


def layer_colormap(self, layer):
    """Colour map index (CmapIDX) of a layer, 0 (gray) if unknown."""
    try:
        index = int(self.CmapIDX[layer])
    except (AttributeError, IndexError, KeyError, TypeError, ValueError):
        return 0
    return index if 0 <= index < len(COLORMAP_NAMES) else 0


def active_layer(self):
    combo = getattr(self, "layer_selected", None)
    return combo.currentIndex() if combo is not None else 0


def refresh_layer_panel(self):
    """The active layer's name highlighted, each colour map button showing its layer's map."""
    active = active_layer(self)
    for k, btn in enumerate(getattr(self, "layer_name_btns", None) or []):
        if btn.isChecked() != (k == active):
            btn.blockSignals(True)
            btn.setChecked(k == active)
            btn.blockSignals(False)
    for k, btn in enumerate(getattr(self, "layer_cmap_btns", None) or []):
        index = layer_colormap(self, k)
        if btn.property("cmap") != index:
            btn.setIcon(QIcon(colormap_pixmap(index)))
            btn.setProperty("cmap", index)
            btn.setToolTip(f"Layer {k + 1} colour map: {COLORMAP_NAMES[index]}\n"
                           "Click to pick another one (the active layer stays the same)")


def select_layer(self, layer):
    """A layer name clicked: the active layer (update_layer_view runs on the combo's change)."""
    combo = getattr(self, "layer_selected", None)
    if combo is not None and 0 <= layer < combo.count():
        combo.setCurrentIndex(layer)
    refresh_layer_panel(self)


def set_layer_colormap(self, layer, index):
    """Colour map of one layer, active or not."""
    self.CmapIDX[layer] = index
    set_color_map(self, layer=None if layer == active_layer(self) else layer)
    refresh_layer_panel(self)


def show_layer_colormap_menu(self, layer):
    """The colour maps, with their gradients; the one picked goes to this layer only."""
    btn = self.layer_cmap_btns[layer]
    menu = QMenu(btn)
    current = layer_colormap(self, layer)
    for index, name in enumerate(COLORMAP_NAMES):
        action = menu.addAction(QIcon(colormap_pixmap(index)), name)
        action.setCheckable(True)
        action.setChecked(index == current)
        action.triggered.connect(lambda checked=False, i=index: set_layer_colormap(self, layer, i))
    menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))


def init_layer_panel(self):
    """Connect the layer names, colour map buttons and the active layer, once (the init functions run again on lazy tab loads)."""
    if getattr(self, "_layer_panel_ready", False) or getattr(self, "layer_selected", None) is None:
        return
    if not getattr(self, "layer_name_btns", None):
        return
    self._layer_panel_ready = True
    for k, btn in enumerate(self.layer_name_btns):
        btn.clicked.connect(lambda checked=False, i=k: select_layer(self, i))
    for k, btn in enumerate(self.layer_cmap_btns):
        btn.clicked.connect(lambda checked=False, i=k: show_layer_colormap_menu(self, i))
    self.layer_selected.currentIndexChanged.connect(lambda _index: refresh_layer_panel(self))
    refresh_layer_panel(self)
