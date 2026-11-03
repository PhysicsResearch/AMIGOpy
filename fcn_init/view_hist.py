"""
View > View histogram (hist_container_01): an analysis tool for the image layers.
- It shows the selected layer, and its window level is the selected layer's only: Min / Max WL, the red
  lines (drag them), the WL menu (data quantiles, presets, another layer's window). The layers set
  Visible in the Layers menu are shown too; each curve follows its layer, so a new image in a layer
  replaces its curve.
- Exact voxel counts, with the same bins for all the layers shown (fcn_display/layer_histogram.py):
  Bins menu (number or width of the bins, range, smoothing), Axes menu (limits, log scale, voxels or
  % of voxels), Layers menu (visible, colour, fill and fill transparency per layer), Export CSV.
- Font sizes, line width and style (None: no line), legend and background follow the Figures menu.
Its settings are remembered in settings.json ("view_histogram").
CompareHistogramDialog (below) is the Compare module's own histogram.
"""
import csv
import os

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPixmap
from PySide6.QtWidgets import (QCheckBox, QColorDialog, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout,
                               QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMenu, QMessageBox, QPushButton,
                               QSizePolicy, QSpinBox, QToolButton, QVBoxLayout, QWidget, QWidgetAction)

from fcn_display.figure_style import add_figure_style_listener, figure_style
from fcn_display.layer_histogram import (array_histogram, bin_edges, csv_table, finite_range, quantile_range,
                                         smooth, table_histogram, value_table)

SETTING = "view_histogram"                      # settings.json
LAYER_COLORS = ("#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd")     # not red: the window level lines are
DEFAULTS = {"bin_mode": "number", "bins": 512, "width": 1.0, "smooth": True,
            "range_auto": True, "range_min": -1000.0, "range_max": 3000.0,
            "x_auto": True, "x_min": -1000.0, "x_max": 3000.0, "y_auto": True, "y_min": 0.0, "y_max": 1000.0,
            "log_y": False, "values": "voxels", "wl_lines": True,
            "layers": [{"color": c, "fill": True, "alpha": 0.25} for c in LAYER_COLORS]}
# remembered between sessions (the range and axis limits belong to the images shown)
SAVED = ("bin_mode", "bins", "width", "smooth", "log_y", "values", "wl_lines", "layers")
VALUE_NAMES = {"voxels": "Voxels", "percent": "% of voxels"}


class MiniToolbar(NavigationToolbar):
    toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Pan',  'Pan (LMB), Zoom (RMB)', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        ('Save', 'Save figure', 'filesave', 'save_figure'),
    )
    def __init__(self, canvas, parent=None):
        super().__init__(canvas, parent)
        self.setIconSize(QSize(14, 14))
        self.setMovable(False)
        self.setFloatable(False)
        self.setMaximumHeight(26)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))

def _on_hist_wheel(self, event):
    if event.inaxes is not getattr(self, "ax_Hist_01", None) or event.xdata is None:
        return
    ax = self.ax_Hist_01
    zx, zy = True, False
    if event.key == 'shift': zx, zy = False, True
    elif event.key == 'control': zx, zy = True, True
    s = getattr(self, "_hist_zoom_factor", 1.2)
    s = s if event.button == 'up' else 1.0 / s
    if zx:
        x0, x1 = ax.get_xlim(); xc = event.xdata
        new_w = (x1 - x0) / s
        x0n = xc - (xc - x0) / s
        ax.set_xlim(x0n, x0n + new_w)
    if zy and event.ydata is not None:
        y0, y1 = ax.get_ylim(); yc = event.ydata
        new_h = (y1 - y0) / s
        y0n = yc - (yc - y0) / s
        ax.set_ylim(y0n, y0n + new_h)
    self.canvas_Hist_01.draw_idle()


# --- settings ------------------------------------------------------------------------------------------

def _settings(self):
    """The histogram settings: DEFAULTS, with the ones remembered in settings.json."""
    s = getattr(self, "hist_settings", None)
    if s is None:
        from fcn_materialassignment.hu_lut import _get_setting
        saved = _get_setting(SETTING, {})
        saved = saved if isinstance(saved, dict) else {}
        s = {key: saved.get(key, value) for key, value in DEFAULTS.items() if key != "layers"}
        s["layers"] = [dict(style) for style in DEFAULTS["layers"]]
        for k, style in enumerate((saved.get("layers") or [])[:len(s["layers"])]):
            if isinstance(style, dict):
                s["layers"][k].update({key: style[key] for key in ("color", "fill", "alpha") if key in style})
        self.hist_settings = s
    return s


def _save_settings(self):
    from fcn_materialassignment.hu_lut import _set_setting
    s = _settings(self)
    _set_setting(SETTING, {key: s[key] for key in SAVED})


def _changed(self, **values):
    """Settings changed in a menu: remembered, and the histogram drawn again."""
    _settings(self).update(values)
    _save_settings(self)
    draw_histogram(self)


# --- the layers ----------------------------------------------------------------------------------------

def _selected(self):
    combo = getattr(self, "layer_selected", None)
    return combo.currentIndex() if combo is not None else 0


def shown_layers(self):
    """The layers whose histogram is shown: the ones set Visible (Layers menu) and always the selected one."""
    return sorted(self._hist_visible | {_selected(self)})


def _layer_image(self, k):
    """(image of the layer, its cache key); IrIS data: the current slice. (None, None) when the layer is empty."""
    data = (getattr(self, "display_data", None) or {}).get(k)
    if data is None or getattr(data, "size", 0) == 0:
        return None, None
    if getattr(self, "DataType", None) == "IrIS" and data.ndim == 3:
        index = int(np.clip(self.current_axial_slice_index[k], 0, data.shape[0] - 1))
        return data[index], (id(data), data.shape, data.dtype.str, index)
    return data, (id(data), data.shape, data.dtype.str)


def _layer_entry(self, k, image, key):
    """Range, number of finite voxels and value table of a layer's image, kept while the image is the same."""
    cache = self._hist_cache
    entry = cache.get(k)
    if entry is None or entry["key"] != key:
        rng = finite_range(image)
        if rng is None:
            cache.pop(k, None)
            return None
        entry = {"key": key, "range": rng, "integer": image.dtype.kind in "iub",
                 "table": value_table(image, rng[0], rng[1]), "counts": {}}
        cache[k] = entry
    return entry


def _layer_counts(entry, image, edges):
    """Voxel counts of a layer in the bins (the last bins kept)."""
    key = (float(edges[0]), float(edges[-1]), len(edges))
    counts = entry["counts"].get(key)
    if counts is None:
        counts = table_histogram(entry["table"], edges) if entry["table"] is not None else array_histogram(image, edges)
        entry["counts"] = {key: counts}
    return counts


def layer_name(self, k):
    """What a layer shows, as in the data tree: modality and series description, or the map / structure name."""
    data = (getattr(self, "display_data", None) or {}).get(k)
    if data is None:
        return ""
    for studies in (getattr(self, "medical_image", None) or {}).values():
        for study in (studies.values() if isinstance(studies, dict) else ()):
            for modality, series_list in (study.items() if isinstance(study, dict) else ()):
                for series in (series_list if isinstance(series_list, list) else ()):
                    if not isinstance(series, dict):
                        continue
                    if series.get("3DMatrix") is data:
                        meta = series.get("metadata") or {}
                        return f"{modality} {meta.get('SeriesDescription') or series.get('SeriesNumber') or ''}".strip()
                    for group in ("density_maps", "mat_maps", "mcnp_lattice_maps"):
                        for name, item in (series.get(group) or {}).items():
                            if isinstance(item, dict) and item.get("3DMatrix") is data:
                                return str(name)
                    for name, item in (series.get("structures") or {}).items():
                        if isinstance(item, dict) and item.get("Mask3D") is data:
                            return str(item.get("Name") or name)
    return ""


def _label(self, k):
    name = layer_name(self, k)
    name = name if len(name) <= 40 else name[:39] + "…"
    return f"Layer {k + 1}" + (f": {name}" if name else "")


def _view_window(self, k):
    """(window, level) of a layer in the View module, None when it has none."""
    wl = (getattr(self, "windowLevelAxial", None) or {}).get(k)
    return (float(wl.GetWindow()), float(wl.GetLevel())) if wl is not None else None


# --- drawing -------------------------------------------------------------------------------------------

def draw_histogram(self):
    """The histograms of the selected layer and of the layers set Visible (same bins)."""
    ax = getattr(self, "ax_Hist_01", None)
    if ax is None:
        return
    s, st = _settings(self), figure_style(self)
    selected = _selected(self)
    shown = {}
    for k in shown_layers(self):
        image, key = _layer_image(self, k)
        entry = _layer_entry(self, k, image, key) if image is not None else None
        if entry is not None:
            shown[k] = (image, entry)

    transparent = st["background"] == "transparent"
    text = "white" if (transparent and getattr(self, "current_theme", "dark") == "dark") else "black"
    face = (0, 0, 0, 0) if transparent else st["background"]
    self.fig_Hist_01.patch.set_facecolor(face)
    ax.clear()
    ax.set_facecolor(face)
    self._vline_low = self._vline_high = self._vline_center = self._fill_out = None      # cleared with the axes
    ax.tick_params(axis="both", which="major", labelsize=st["font"], colors=text)
    for spine in ax.spines.values():
        spine.set_color(text)
    ax.set_ylabel(VALUE_NAMES[s["values"]], fontsize=st["font"], color=text)
    self._hist_shown = None
    if not shown:
        self.canvas_Hist_01.draw_idle()
        return

    lo = min(entry["range"][0] for _, entry in shown.values())
    hi = max(entry["range"][1] for _, entry in shown.values())
    if not s["range_auto"] and s["range_max"] > s["range_min"]:
        lo, hi = s["range_min"], s["range_max"]
    edges = bin_edges(lo, hi, s["bins"], s["width"] if s["bin_mode"] == "width" else None,
                      all(entry["integer"] for _, entry in shown.values()))
    centers = 0.5 * (edges[:-1] + edges[1:])
    log = s["log_y"]
    curves = []
    for k in sorted(shown, key=lambda k: (k == selected, k)):          # the selected layer drawn last, on top
        image, entry = shown[k]
        counts = _layer_counts(entry, image, edges)
        values = counts * (100.0 / entry["range"][2]) if s["values"] == "percent" else counts.astype(float)
        if s["smooth"]:
            values = smooth(values)
            dmin, dmax = entry["range"][:2]
            values[(edges[1:] <= dmin) | (edges[:-1] > dmax)] = 0.0    # nothing outside the layer's values
        if log:
            values = np.where(values > 0, values, np.nan)
        curves.append((k, _label(self, k), counts, values))
    self._hist_shown = {"edges": edges, "centers": centers, "curves": curves, "values": s["values"],
                        "smooth": s["smooth"]}

    margin = 0.01 * (edges[-1] - edges[0])
    if s["x_auto"] or s["x_max"] <= s["x_min"]:
        x_limits = (edges[0] - margin, edges[-1] + margin)
    else:
        x_limits = (s["x_min"], s["x_max"])
    visible = (edges[1:] >= x_limits[0]) & (edges[:-1] <= x_limits[1])     # automatic Y: the bins in view
    seen = [v[visible] for *_, v in curves if np.isfinite(v[visible]).any()]
    top = max([np.nanmax(v) for v in seen] or [1.0])
    bottom = 0.0
    if log:
        ax.set_yscale("log")
        bottom = 0.5 * min([np.nanmin(v) for v in seen] or [1.0])
    for k, label, counts, values in curves:
        style = s["layers"][k]
        ax.plot(centers, values, color=style["color"], lw=st["line_width"], ls=st["line_style"], label=label,
                drawstyle="default" if s["smooth"] else "steps-mid")
        if style["fill"] and style["alpha"] > 0:
            ax.fill_between(centers, np.nan_to_num(values, nan=bottom), bottom, step="mid", color=style["color"],
                            alpha=style["alpha"], lw=0, label="_nolegend_")
    if s["y_auto"] or s["y_max"] <= s["y_min"]:
        ax.set_ylim(bottom, top * 2.0) if log else ax.set_ylim(0.0, max(top, 1e-9) * 1.05)
    else:
        ax.set_ylim(s["y_min"] if not log or s["y_min"] > 0 else bottom, s["y_max"])
    ax.set_xlim(*x_limits)
    if st["legend"]:            # in layer order (the selected layer is drawn last)
        handles, labels = ax.get_legend_handles_labels()
        order = sorted(range(len(labels)), key=lambda i: labels[i])
        legend = ax.legend([handles[i] for i in order], [labels[i] for i in order], fontsize=st["legend_font"],
                           loc="upper right", frameon=False, labelcolor=text)
        legend.set_draggable(True)
    update_histogram_wl_lines(self)


def update_histogram_wl_lines(self, Window=None, Level=None):
    """
    The selected layer's window on the histogram (red: min / max, yellow: level, the curve outside it
    darker) and in Min / Max WL. Window / Level are not needed: it reads the View module's window of the
    selected layer (set_window also calls this from other modules, with their own window).
    """
    if getattr(self, "ax_Hist_01", None) is None:
        return
    ax, s = self.ax_Hist_01, _settings(self)
    selected = _selected(self)
    window = _view_window(self, selected)
    if window is None:
        if Window is None:
            return
        window = (float(Window), float(Level))
    Window, Level = window
    low_x, high_x = Level - Window / 2.0, Level + Window / 2.0
    for edit, value in ((getattr(self, "txt_min_wl", None), low_x), (getattr(self, "txt_max_wl", None), high_x)):
        if edit is not None and not edit.hasFocus():
            edit.setText(f"{value:.1f}")

    old = getattr(self, "_fill_out", None)
    if old is not None:
        try:
            old.remove()
        except (ValueError, NotImplementedError):
            pass
        self._fill_out = None
    shown = getattr(self, "_hist_shown", None)
    curve = next((c for c in (shown or {}).get("curves", ()) if c[0] == selected), None)
    lines = [getattr(self, name, None) for name in ("_vline_low", "_vline_high", "_vline_center")]
    if not (s["wl_lines"] and curve is not None):
        for line in lines:
            if line is not None:
                line.set_visible(False)
        self.canvas_Hist_01.draw_idle()
        return

    if s["x_auto"]:     # the lines inside the plot
        x0, x1 = ax.get_xlim()
        margin = max(0.05 * Window, 0.1)
        if low_x < x0 or high_x > x1:
            ax.set_xlim(min(x0, low_x - margin), max(x1, high_x + margin))
    if any(line is None or line not in ax.lines for line in lines):
        self._vline_low = ax.axvline(low_x, color="red", linestyle="--", linewidth=1.5, alpha=0.8)
        self._vline_high = ax.axvline(high_x, color="red", linestyle="--", linewidth=1.5, alpha=0.8)
        self._vline_center = ax.axvline(Level, color="yellow", linestyle=":", linewidth=1.0, alpha=0.6)
    else:
        for line, x in zip(lines, (low_x, high_x, Level)):
            line.set_xdata([x, x])
            line.set_visible(True)
    centers = shown["centers"]
    bottom = ax.get_ylim()[0] if ax.get_yscale() == "log" else 0.0
    self._fill_out = ax.fill_between(centers, np.nan_to_num(curve[3], nan=bottom), bottom,
                                     where=(centers < low_x) | (centers > high_x),
                                     step="mid", facecolor="black", alpha=0.45, lw=0)
    self.canvas_Hist_01.draw_idle()


def set_vtk_histogran_fig(self, data_changed=True):
    """
    The histogram after a new image in the selected layer (data_changed) or another layer selected
    (update_layer_view: data_changed False).
    """
    init_histogram_ui(self)
    k = _selected(self)
    if data_changed:
        self._hist_cache.pop(k, None)
    if getattr(self, "DataType", None) == "IrIS":     # as always: the window from the slice shown
        image, _ = _layer_image(self, k)
        if image is not None:
            values = image.ravel().astype(np.float32, copy=False)
            from fcn_display.win_level import set_window
            set_window(self, float(np.std(values)) * 3.0, float(np.mean(values)))
    draw_histogram(self)


# --- the controls --------------------------------------------------------------------------------------

def _menu_button(parent, text, tip):
    button = QToolButton(parent)
    button.setText(text)
    button.setToolTip(tip)
    button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
    button.setMenu(QMenu(button))
    return button


def _panel_action(menu, widget):
    action = QWidgetAction(menu)
    action.setDefaultWidget(widget)
    menu.addAction(action)


def _number_box(parent, decimals=3, low=-1e9, high=1e9):
    box = QDoubleSpinBox(parent)
    box.setRange(low, high)
    box.setDecimals(decimals)
    box.setKeyboardTracking(False)          # applied with Enter / leaving the box, not per key
    box.setFixedWidth(96)
    return box


def _color_icon(color):
    pixmap = QPixmap(28, 12)
    pixmap.fill(QColor(color))
    return QIcon(pixmap)


def _build_layers_menu(self, menu):
    """Each layer's curve: visible (the selected layer always is), colour, fill and fill transparency."""
    panel = QWidget(menu)
    grid = QGridLayout(panel)
    grid.setContentsMargins(10, 8, 10, 8)
    grid.setHorizontalSpacing(10)
    for col, text in enumerate(("Visible", "", "Colour", "Fill", "Transparency")):
        grid.addWidget(QLabel(text, panel), 0, col)
    self._hist_layer_rows = []
    for k in range(len(LAYER_COLORS)):
        visible = QCheckBox(panel)
        visible.toggled.connect(lambda on, k=k: _set_layer_visible(self, k, on))
        name = QLabel(f"Layer {k + 1}", panel)
        color = QToolButton(panel)
        color.setIconSize(QSize(28, 12))
        color.setToolTip(f"Layer {k + 1} curve colour")
        color.clicked.connect(lambda checked=False, k=k: _pick_layer_color(self, k))
        fill = QCheckBox(panel)
        fill.setToolTip(f"Fill under the Layer {k + 1} curve")
        fill.toggled.connect(lambda on, k=k: _set_layer_style(self, k, fill=bool(on)))
        alpha = _number_box(panel, decimals=2, low=0.0, high=1.0)
        alpha.setSingleStep(0.05)
        alpha.setFixedWidth(70)
        alpha.setToolTip(f"Layer {k + 1} fill transparency: 0 = fully transparent, 1 = opaque")
        alpha.valueChanged.connect(lambda value, k=k: _set_layer_style(self, k, alpha=float(value)))
        for col, widget in enumerate((visible, name, color, fill, alpha)):
            grid.addWidget(widget, k + 1, col)
        self._hist_layer_rows.append((visible, name, color, fill, alpha))
    _panel_action(menu, panel)
    menu.aboutToShow.connect(lambda: _show_layers_menu(self))


def _set_quietly(box, value):
    """A menu control showing a setting, without applying it again."""
    box.blockSignals(True)
    if isinstance(box, QComboBox):
        box.setCurrentIndex(value)
    elif isinstance(box, QCheckBox):
        box.setChecked(bool(value))
    else:
        box.setValue(value)
    box.blockSignals(False)


def _show_layers_menu(self):
    styles, selected = _settings(self)["layers"], _selected(self)
    for k, (visible, name, color, fill, alpha) in enumerate(self._hist_layer_rows):
        _set_quietly(visible, k == selected or k in self._hist_visible)
        visible.setEnabled(k != selected)
        visible.setToolTip(f"Layer {k + 1} is selected: always shown" if k == selected
                           else f"Show the Layer {k + 1} histogram")
        name.setText(_label(self, k) + (" (selected)" if k == selected else ""))
        color.setIcon(_color_icon(styles[k]["color"]))
        _set_quietly(fill, styles[k]["fill"])
        _set_quietly(alpha, styles[k]["alpha"])


def _set_layer_visible(self, k, on):
    """A layer's histogram shown or not (the selected layer's always is)."""
    if on:
        self._hist_visible.add(k)
    else:
        self._hist_visible.discard(k)
    draw_histogram(self)


def _set_layer_style(self, k, **values):
    styles = [dict(style) for style in _settings(self)["layers"]]
    styles[k].update(values)
    _changed(self, layers=styles)


def _pick_layer_color(self, k):
    color = QColorDialog.getColor(QColor(_settings(self)["layers"][k]["color"]), self, f"Layer {k + 1} curve colour")
    if color.isValid():
        _set_layer_style(self, k, color=color.name())
        if getattr(self, "_hist_layer_rows", None):
            self._hist_layer_rows[k][2].setIcon(_color_icon(color.name()))


def _build_bins_menu(self, menu):
    """Number or width of the bins, the range binned (all values of the layers shown, or set) and smoothing."""
    panel = QWidget(menu)
    form = QFormLayout(panel)
    form.setContentsMargins(10, 8, 10, 8)
    mode = QComboBox(panel)
    mode.addItems(["Number", "Width"])
    count = QSpinBox(panel)
    count.setRange(2, 20000)
    count.setKeyboardTracking(False)
    count.setToolTip("Number of bins over the range (integer images: whole-number bins centred on the values)")
    width = _number_box(panel)
    width.setMinimum(1e-6)
    width.setToolTip("Width of the bins (bins centred on its multiples: width 1 = one bin per value of a CT)")
    row = QHBoxLayout()
    for widget in (mode, count, width):
        row.addWidget(widget)
    form.addRow("Bins:", row)
    auto = QCheckBox("All values", panel)
    auto.setToolTip("Bin all the values of the layers shown; else from / to")
    low, high = _number_box(panel), _number_box(panel)
    row = QHBoxLayout()
    for widget in (auto, low, QLabel("to", panel), high):
        row.addWidget(widget)
    form.addRow("Range:", row)
    smoothing = QCheckBox("Smooth the curves (Gaussian, 2 bins)", panel)
    form.addRow(smoothing)
    self._hist_bins_widgets = (mode, count, width, auto, low, high, smoothing)

    def mode_changed(index):
        count.setVisible(index == 0)
        width.setVisible(index == 1)
        _changed(self, bin_mode=("number", "width")[index])

    def auto_toggled(on):
        low.setEnabled(not on)
        high.setEnabled(not on)
        _changed(self, range_auto=bool(on), range_min=low.value(), range_max=high.value())

    mode.currentIndexChanged.connect(mode_changed)
    count.valueChanged.connect(lambda value: _changed(self, bins=int(value)))
    width.valueChanged.connect(lambda value: _changed(self, width=float(value)))
    auto.toggled.connect(auto_toggled)
    low.valueChanged.connect(lambda value: _changed(self, range_min=float(value)))
    high.valueChanged.connect(lambda value: _changed(self, range_max=float(value)))
    smoothing.toggled.connect(lambda on: _changed(self, smooth=bool(on)))
    _panel_action(menu, panel)
    menu.aboutToShow.connect(lambda: _show_bins_menu(self))


def _show_bins_menu(self):
    s = _settings(self)
    mode, count, width, auto, low, high, smoothing = self._hist_bins_widgets
    shown = getattr(self, "_hist_shown", None)
    lo, hi = (s["range_min"], s["range_max"])
    if s["range_auto"] and shown is not None:
        lo, hi = float(shown["edges"][0]), float(shown["edges"][-1])
    for box, value in ((mode, ("number", "width").index(s["bin_mode"])), (count, s["bins"]), (width, s["width"]),
                       (auto, s["range_auto"]), (low, lo), (high, hi), (smoothing, s["smooth"])):
        _set_quietly(box, value)
    count.setVisible(s["bin_mode"] == "number")
    width.setVisible(s["bin_mode"] == "width")
    low.setEnabled(not s["range_auto"])
    high.setEnabled(not s["range_auto"])


def _build_axes_menu(self, menu):
    """Axis limits (automatic or set), log scale and voxels or % of voxels."""
    panel = QWidget(menu)
    form = QFormLayout(panel)
    form.setContentsMargins(10, 8, 10, 8)
    rows = {}
    for axis in ("x", "y"):
        auto = QCheckBox("Auto", panel)
        low, high = _number_box(panel), _number_box(panel)
        row = QHBoxLayout()
        for widget in (auto, low, QLabel("to", panel), high):
            row.addWidget(widget)
        form.addRow(f"{axis.upper()} axis:", row)
        rows[axis] = (auto, low, high)

        def toggled(on, axis=axis, low=low, high=high):
            low.setEnabled(not on)
            high.setEnabled(not on)
            _changed(self, **{f"{axis}_auto": bool(on), f"{axis}_min": low.value(), f"{axis}_max": high.value()})

        auto.toggled.connect(toggled)
        low.valueChanged.connect(lambda value, axis=axis: _changed(self, **{f"{axis}_min": float(value)}))
        high.valueChanged.connect(lambda value, axis=axis: _changed(self, **{f"{axis}_max": float(value)}))
    log = QCheckBox("Log scale (Y)", panel)
    log.toggled.connect(lambda on: _changed(self, log_y=bool(on)))
    form.addRow(log)
    values = QComboBox(panel)
    values.addItems(list(VALUE_NAMES.values()))
    values.setToolTip("Voxels per bin, or % of the layer's voxels (layers of different sizes compared)")
    values.currentIndexChanged.connect(lambda index: _changed(self, values=list(VALUE_NAMES)[index]))
    form.addRow("Values:", values)
    self._hist_axes_widgets = (rows, log, values)
    _panel_action(menu, panel)
    menu.aboutToShow.connect(lambda: _show_axes_menu(self))


def _show_axes_menu(self):
    s = _settings(self)
    rows, log, values = self._hist_axes_widgets
    limits = {"x": self.ax_Hist_01.get_xlim(), "y": self.ax_Hist_01.get_ylim()}
    boxes = [(log, s["log_y"]), (values, list(VALUE_NAMES).index(s["values"]))]
    for axis, (auto, low, high) in rows.items():
        current = limits[axis] if s[f"{axis}_auto"] else (s[f"{axis}_min"], s[f"{axis}_max"])
        boxes += [(auto, s[f"{axis}_auto"]), (low, current[0]), (high, current[1])]
        low.setEnabled(not s[f"{axis}_auto"])
        high.setEnabled(not s[f"{axis}_auto"])
    for box, value in boxes:
        _set_quietly(box, value)


def _fill_wl_menu(self, menu):
    """Quick windows of the selected layer: from its values, the presets, another layer's window."""
    from fcn_display.win_level import window_bone, window_custom, window_lung, window_sprred, window_stissue, window_zeff
    menu.clear()
    entries = [("Full range of the layer", lambda: _window_from_quantiles(self, 0.0, 1.0)),
               ("1 - 99 % of its voxels", lambda: _window_from_quantiles(self, 0.01, 0.99)),
               ("5 - 95 % of its voxels", lambda: _window_from_quantiles(self, 0.05, 0.95)),
               None,
               ("Lung", lambda: window_lung(self)), ("Soft tissue", lambda: window_stissue(self)),
               ("Bone", lambda: window_bone(self)), ("SPR / RED", lambda: window_sprred(self)),
               ("Zeff", lambda: window_zeff(self)), ("Custom...", lambda: window_custom(self))]
    selected = _selected(self)
    others = [k for k in range(len(LAYER_COLORS))
              if k != selected and _layer_image(self, k)[0] is not None and _view_window(self, k) is not None]
    if others:
        entries.append(None)
        entries += [(f"Same as {_label(self, k)}", lambda k=k: _window_like(self, k)) for k in others]
    for item in entries:
        if item is None:
            menu.addSeparator()
            continue
        action = QAction(item[0], menu)
        action.triggered.connect(lambda checked=False, run=item[1]: run())
        menu.addAction(action)


def _window_from_quantiles(self, q_low, q_high):
    k = _selected(self)
    image, key = _layer_image(self, k)
    entry = _layer_entry(self, k, image, key) if image is not None else None
    if entry is None:
        return
    low, high = quantile_range(image, entry["range"], entry["table"], q_low, q_high)
    if high > low:
        from fcn_display.win_level import set_window
        set_window(self, high - low, 0.5 * (high + low))


def _window_like(self, k):
    window = _view_window(self, k)
    if window is not None:
        from fcn_display.win_level import set_window
        set_window(self, *window)


def export_histogram_csv(self):
    """The histograms shown, to a CSV file: bins, voxel counts per layer and the values plotted."""
    shown = getattr(self, "_hist_shown", None)
    if not shown or not shown["curves"]:
        QMessageBox.information(self, "Export histogram", "There is no histogram to export: show an image in a layer.")
        return
    start = getattr(self, "_hist_export_dir", None) or os.path.expanduser("~")
    path, _ = QFileDialog.getSaveFileName(self, "Export histograms", os.path.join(start, "histogram.csv"),
                                          "CSV files (*.csv)")
    if not path:
        return
    what = VALUE_NAMES[shown["values"]].lower() + (", smoothed" if shown["smooth"] else "")
    plotted = shown["values"] == "percent" or shown["smooth"]
    curves = [(label, counts, values if plotted else None, f"({what})")
              for _, label, counts, values in sorted(shown["curves"], key=lambda curve: curve[0])]   # layer order
    header, rows = csv_table(shown["edges"], curves)
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
    except OSError as e:
        QMessageBox.warning(self, "Export histogram", f"Could not write {path}:\n{e}")
        return
    self._hist_export_dir = os.path.dirname(path)


def _hover_text(self, x):
    shown = getattr(self, "_hist_shown", None)
    if not shown:
        return f"x = {x:.4g}"
    i = int(np.clip(np.searchsorted(shown["edges"], x, side="right") - 1, 0, len(shown["centers"]) - 1))
    parts = [f"x = {x:.4g}"] + [f"L{k + 1} {np.nan_to_num(values[i]):,.4g}" for k, _, _, values in shown["curves"]]
    return "   ".join(parts)


def init_histogram_ui(self):
    """The histogram panel in hist_container_01, once: plot, its toolbar, the window level and the analysis controls."""
    if getattr(self, "canvas_Hist_01", None) is not None:
        return
    s = _settings(self)
    self._hist_visible, self._hist_cache, self._hist_shown = set(), {}, None
    lay_container = QVBoxLayout()
    lay_container.setContentsMargins(0, 0, 0, 0)
    lay_container.setSpacing(2)
    self.hist_container_01.setLayout(lay_container)

    self.fig_Hist_01 = Figure(figsize=(6, 2.0), dpi=100)
    self.fig_Hist_01.set_layout_engine("constrained", w_pad=0.03, h_pad=0.03)
    self.ax_Hist_01 = self.fig_Hist_01.add_subplot(111)
    self.ax_Hist_01.set_facecolor("none"); self.fig_Hist_01.set_facecolor("none")
    self.canvas_Hist_01 = FigureCanvas(self.fig_Hist_01)
    self.canvas_Hist_01.setFocusPolicy(Qt.StrongFocus)
    self.canvas_Hist_01.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum))

    # top row: toolbar and the values under the mouse
    self.toolbar_Hist_01 = MiniToolbar(self.canvas_Hist_01, self)
    self._xy_label = QLabel("x = —", self)
    self._xy_label.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
    top_row = QWidget(self.hist_container_01)
    h = QHBoxLayout(top_row)
    h.setContentsMargins(0, 0, 0, 0); h.setSpacing(6)
    h.addWidget(self.toolbar_Hist_01, 0, Qt.AlignLeft)
    h.addSpacing(8)
    h.addWidget(self._xy_label, 0, Qt.AlignLeft)
    h.addStretch(1)

    # bottom row: the selected layer's window, then the analysis controls
    bot_row = QWidget(self.hist_container_01)
    h_bot = QHBoxLayout(bot_row)
    h_bot.setContentsMargins(4, 0, 4, 4); h_bot.setSpacing(8)
    self.txt_min_wl = QLineEdit(bot_row)
    self.txt_max_wl = QLineEdit(bot_row)
    for edit, text in ((self.txt_min_wl, "Min"), (self.txt_max_wl, "Max")):
        edit.setFixedWidth(80)
        edit.setPlaceholderText(text)
        edit.setToolTip(f"{text}imum of the selected layer's window (Enter to apply)")
    self.hist_wl_btn = _menu_button(bot_row, "WL", "Window of the selected layer: from its values (full range, "
                                    "percentiles), the presets, or the window of another layer")
    self.hist_wl_btn.menu().aboutToShow.connect(lambda: _fill_wl_menu(self, self.hist_wl_btn.menu()))
    self.hist_wl_lines = QCheckBox("WL lines", bot_row)
    self.hist_wl_lines.setToolTip("Show the selected layer's window on the histogram (drag the lines to change it)")
    self.hist_wl_lines.setChecked(bool(s["wl_lines"]))
    self.hist_wl_lines.toggled.connect(lambda on: _changed(self, wl_lines=bool(on)))
    self.hist_layers_btn = _menu_button(bot_row, "Layers", "Which layers are shown (the selected one always), "
                                        "and the colour, fill and fill transparency of each layer's curve")
    _build_layers_menu(self, self.hist_layers_btn.menu())
    self.hist_bins_btn = _menu_button(bot_row, "Bins", "Number or width of the bins, the range binned, smoothing")
    _build_bins_menu(self, self.hist_bins_btn.menu())
    self.hist_axes_btn = _menu_button(bot_row, "Axes", "Axis limits, log scale, voxels or % of voxels")
    _build_axes_menu(self, self.hist_axes_btn.menu())
    self.hist_export_btn = QPushButton("Export CSV", bot_row)
    self.hist_export_btn.setToolTip("Save the histograms shown as a CSV file (bins, voxel counts per layer, values plotted)")
    self.hist_export_btn.clicked.connect(lambda: export_histogram_csv(self))
    for widget in (QLabel("Min WL:", bot_row), self.txt_min_wl, QLabel("Max WL:", bot_row), self.txt_max_wl,
                   self.hist_wl_btn):
        h_bot.addWidget(widget)
    h_bot.addSpacing(14)
    for widget in (self.hist_wl_lines, self.hist_layers_btn, self.hist_bins_btn, self.hist_axes_btn,
                   self.hist_export_btn):
        h_bot.addWidget(widget)
    h_bot.addStretch(1)

    lay_container.addWidget(top_row, 0)
    lay_container.addWidget(self.canvas_Hist_01, 1)
    lay_container.addWidget(bot_row, 0)

    def _on_manual_wl_change():
        try:
            min_val = float(self.txt_min_wl.text())
            max_val = float(self.txt_max_wl.text())
        except ValueError:
            return
        if min_val >= max_val:
            max_val = min_val + 1.0
        from fcn_display.win_level import set_window
        set_window(self, max_val - min_val, (max_val + min_val) / 2.0)

    self.txt_min_wl.editingFinished.connect(_on_manual_wl_change)
    self.txt_max_wl.editingFinished.connect(_on_manual_wl_change)

    self._hist_zoom_factor = 1.2
    self.canvas_Hist_01.mpl_connect('scroll_event', lambda ev: _on_hist_wheel(self, ev))

    def _on_motion(ev):
        if ev.inaxes is not self.ax_Hist_01 or ev.xdata is None:
            self._xy_label.setText("x = —")
            return
        self._xy_label.setText(_hover_text(self, float(ev.xdata)))
    self.canvas_Hist_01.mpl_connect('motion_notify_event', _on_motion)

    add_figure_style_listener(self, "view_histogram", lambda: draw_histogram(self))
    init_histogram_interaction(self)
    draw_histogram(self)


def init_histogram_interaction(self):
    if hasattr(self, '_hist_interaction_connected') and self._hist_interaction_connected:
        return

    self._dragging_line = None
    self._hist_interaction_connected = True

    def on_press(event):
        if event.inaxes != self.ax_Hist_01 or event.button != 1 or event.xdata is None:
            return
        line = getattr(self, "_vline_low", None)
        if line is None or not line.get_visible():      # no window lines shown
            return
        window = _view_window(self, _selected(self))
        if window is None:
            return
        Window, Level = window
        xlim = self.ax_Hist_01.get_xlim()
        tol = 0.02 * (xlim[1] - xlim[0])
        low_x, high_x = Level - Window / 2.0, Level + Window / 2.0
        dists = {'low': abs(event.xdata - low_x), 'high': abs(event.xdata - high_x), 'center': abs(event.xdata - Level)}
        closest = min(dists, key=dists.get)
        if dists[closest] <= tol:
            self._dragging_line = closest
            self._drag_start_low = low_x
            self._drag_start_high = high_x

    def on_motion(event):
        if self._dragging_line is None or event.inaxes != self.ax_Hist_01 or event.xdata is None:
            return
        from fcn_display.win_level import set_window
        new_x = event.xdata
        if self._dragging_line == 'low':
            high_x = self._drag_start_high
            low_x = min(new_x, high_x - 1.0)
            set_window(self, high_x - low_x, (high_x + low_x) / 2.0)
        elif self._dragging_line == 'high':
            low_x = self._drag_start_low
            high_x = max(new_x, low_x + 1.0)
            set_window(self, high_x - low_x, (high_x + low_x) / 2.0)
        else:
            set_window(self, self._drag_start_high - self._drag_start_low, new_x)

    def on_release(event):
        self._dragging_line = None

    self.canvas_Hist_01.mpl_connect('button_press_event', on_press)
    self.canvas_Hist_01.mpl_connect('motion_notify_event', on_motion)
    self.canvas_Hist_01.mpl_connect('button_release_event', on_release)

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QSize
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

class CompareHistogramDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compare View Histogram")
        self.resize(600, 350)
        self.parent_app = parent
        
        # Main layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(6)
        
        # Matplotlib elements
        self.fig = Figure(figsize=(6, 2.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('none')
        self.fig.set_facecolor('none')
        
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        
        # Toolbar and hover label
        self.toolbar = MiniToolbar(self.canvas, self)
        self._xy_label = QtWidgets.QLabel("(x, y) = (—, —)", self)
        self._xy_label.setStyleSheet("color: white; font-size: 11pt;")
        
        top_row = QtWidgets.QWidget(self)
        h = QtWidgets.QHBoxLayout(top_row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)
        h.addWidget(self.toolbar, 0, Qt.AlignLeft)
        h.addSpacing(8)
        h.addWidget(self._xy_label, 0, Qt.AlignLeft)
        h.addStretch(1)
        
        self.layout.addWidget(top_row, 0)
        self.layout.addWidget(self.canvas, 1)
        
        # Bottom row: edit fields for min and max bounds
        bottom_row = QtWidgets.QWidget(self)
        h_bottom = QtWidgets.QHBoxLayout(bottom_row)
        h_bottom.setContentsMargins(0, 4, 0, 0)
        h_bottom.setSpacing(10)
        
        lbl_min = QtWidgets.QLabel("Min (Lower Bound):", self)
        lbl_min.setStyleSheet("color: white; font-size: 11pt;")
        h_bottom.addWidget(lbl_min)
        
        self.edit_min = QtWidgets.QLineEdit(self)
        self.edit_min.setFixedWidth(120)
        self.edit_min.setStyleSheet("color: black; background-color: white; font-size: 11pt; border-radius: 3px; padding: 2px;")
        h_bottom.addWidget(self.edit_min)
        
        lbl_max = QtWidgets.QLabel("Max (Upper Bound):", self)
        lbl_max.setStyleSheet("color: white; font-size: 11pt;")
        h_bottom.addWidget(lbl_max)
        
        self.edit_max = QtWidgets.QLineEdit(self)
        self.edit_max.setFixedWidth(120)
        self.edit_max.setStyleSheet("color: black; background-color: white; font-size: 11pt; border-radius: 3px; padding: 2px;")
        h_bottom.addWidget(self.edit_max)
        
        h_bottom.addStretch(1)
        self.layout.addWidget(bottom_row, 0)
        
        # Connect edit signals
        self.edit_min.editingFinished.connect(self.on_bounds_edited)
        self.edit_max.editingFinished.connect(self.on_bounds_edited)
        
        # Zoom and Hover connections
        self.canvas.mpl_connect('scroll_event', self._on_scroll)
        self.canvas.mpl_connect('motion_notify_event', self._on_motion_hover)
        
        # Window / Level dragging state
        self._dragging_line = None
        self._vline_low = None
        self._vline_high = None
        self._vline_center = None
        
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion_drag)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        
        self.fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.20)
        
        # Populate data
        self.update_histogram()

    def _on_scroll(self, event):
        if event.inaxes is not self.ax or event.xdata is None:
            return
        ax = self.ax
        zx, zy = True, False
        if event.key == 'shift': zx, zy = False, True
        elif event.key == 'control': zx, zy = True, True
        s = 1.2 if event.button == 'up' else 1.0 / 1.2
        if zx:
            x0, x1 = ax.get_xlim(); xc = event.xdata
            new_w = (x1 - x0) / s
            x0n = xc - (xc - x0) / s
            ax.set_xlim(x0n, x0n + new_w)
        if zy and event.ydata is not None:
            y0, y1 = ax.get_ylim(); yc = event.ydata
            new_h = (y1 - y0) / s
            y0n = yc - (yc - y0) / s
            ax.set_ylim(y0n, y0n + new_h)
        self.canvas.draw_idle()

    def _on_motion_hover(self, event):
        if event.inaxes is not self.ax or event.xdata is None:
            self._xy_label.setText("(x, y) = (—, —)")
            return
        x = float(event.xdata); y = 0.0
        if hasattr(self, "_hist_centers") and hasattr(self, "_hist_counts") and self._hist_centers.size:
            i = int(np.clip(np.searchsorted(self._hist_centers, x) - 1, 0, self._hist_centers.size - 1))
            y = float(self._hist_counts[i])
        self._xy_label.setText(f"(x, y) = ({x:.0f}, {y:,.2f})")

    def update_histogram(self):
        app = self.parent_app
        if not hasattr(app, 'Comp_im_idx') or not hasattr(app, 'display_comp_data'):
            return
            
        layer = app.layer_selected.currentIndex()
        ref_idx = app.Comp_im_idx.value()
        
        if (ref_idx, layer) not in app.display_comp_data:
            self.ax.clear()
            self.ax.text(0.5, 0.5, "No data loaded in active viewport", 
                         ha='center', va='center', color='red', transform=self.ax.transAxes)
            self.canvas.draw_idle()
            return
            
        # Get raw data of active comparison viewport
        vol_c = app.display_comp_data[ref_idx, layer]
        # Subsample large volumes before flattening to avoid OOM
        n_vox_c = vol_c.size
        if n_vox_c > 2_000_000:
            step_c = max(1, int(round((n_vox_c / 1_000_000) ** (1.0 / 3.0))))
            data = vol_c[::step_c, ::step_c, ::step_c].ravel().astype(np.float32)
        else:
            data = vol_c.ravel().astype(np.float32, copy=False)
        dmin = float(np.nanmin(data)) if data.size else 0.0
        dmax = float(np.nanmax(data)) if data.size else 1.0
        if not np.isfinite(dmin) or not np.isfinite(dmax) or dmin == dmax:
            dmin, dmax = dmin - 0.5, dmin + 0.5
            
        np.clip(data, dmin, dmax, out=data)
        if data.size > 500_000:
            rng = np.random.default_rng(123)
            data = data[rng.choice(data.size, 500_000, replace=False)]
            
        # W/L values for this viewport
        wl = app.windowLevelAxComp[ref_idx, layer]
        Window = wl.GetWindow()
        Level = wl.GetLevel()
        
        low_x = Level - Window / 2.0
        high_x = Level + Window / 2.0
        
        margin_wl = max(0.05 * Window, 0.1)
        x_lo = min(dmin - 0.01 * (dmax - dmin), low_x - margin_wl)
        x_hi = max(dmax + 0.01 * (dmax - dmin), high_x + margin_wl)
        
        counts, edges = np.histogram(data, bins=512, range=(x_lo, x_hi))
        centers = 0.5 * (edges[:-1] + edges[1:])
        
        if counts.size >= 13:
            k = 13; x = np.arange(k) - (k - 1) / 2.0; sigma = 2.0
            ker = np.exp(-0.5 * (x / sigma) ** 2); ker /= ker.sum()
            smooth = np.convolve(counts.astype(float), ker, mode='same')
        else:
            smooth = counts.astype(float)
            
        smooth[centers < dmin] = 0.0
        smooth[centers > dmax] = 0.0
        
        self._hist_centers = centers
        self._hist_counts = smooth
        
        self.ax.clear()
        self.ax.set_facecolor('none')
        self.ax.plot(centers, smooth, lw=1)
        self.ax.fill_between(centers, smooth, step='mid', alpha=0.25)
        
        # Tick parameters and spines style
        self.ax.tick_params(axis='both', which='major', labelsize=11, colors='white')
        for sp in self.ax.spines.values():
            sp.set_color('white')
            
        self.ax.set_xlim(x_lo, x_hi)
        self.ax.set_ylim(0, max(1.0, float(smooth.max())) * 1.05)
        
        self.update_wl_lines(Window, Level)

    def update_wl_lines(self, Window, Level):
        low_x = Level - Window / 2.0
        high_x = Level + Window / 2.0
        
        # Adjust axes limits dynamically if lines go outside current xlim
        xlim = self.ax.get_xlim()
        new_xlim = list(xlim)
        changed = False
        margin_wl = max(0.05 * Window, 0.1)
        if low_x < xlim[0]:
            new_xlim[0] = low_x - margin_wl
            changed = True
        if high_x > xlim[1]:
            new_xlim[1] = high_x + margin_wl
            changed = True
            
        if changed:
            self.ax.set_xlim(new_xlim[0], new_xlim[1])
            
        if self._vline_low in self.ax.lines:
            self._vline_low.set_xdata([low_x, low_x])
            self._vline_high.set_xdata([high_x, high_x])
            self._vline_center.set_xdata([Level, Level])
        else:
            self._vline_low = self.ax.axvline(low_x, color='red', linestyle='--', linewidth=1.5, alpha=0.8)
            self._vline_high = self.ax.axvline(high_x, color='red', linestyle='--', linewidth=1.5, alpha=0.8)
            self._vline_center = self.ax.axvline(Level, color='white', linestyle=':', linewidth=1.2, alpha=0.7)
            
        # Update text inputs
        self.edit_min.blockSignals(True)
        self.edit_min.setText(f"{low_x:.2f}")
        self.edit_min.blockSignals(False)
        
        self.edit_max.blockSignals(True)
        self.edit_max.setText(f"{high_x:.2f}")
        self.edit_max.blockSignals(False)
        
        self.canvas.draw_idle()

    def on_press(self, event):
        if event.inaxes != self.ax or event.button != 1:
            return
        click_x = event.xdata
        if click_x is None:
            return
            
        xlim = self.ax.get_xlim()
        tol = 0.02 * (xlim[1] - xlim[0])
        
        app = self.parent_app
        layer = app.layer_selected.currentIndex()
        ref_idx = app.Comp_im_idx.value()
        wl = app.windowLevelAxComp[ref_idx, layer]
        Window = wl.GetWindow()
        Level = wl.GetLevel()
        
        low_x = Level - Window / 2.0
        high_x = Level + Window / 2.0
        
        dists = {
            'low': abs(click_x - low_x),
            'high': abs(click_x - high_x),
            'center': abs(click_x - Level)
        }
        
        closest = min(dists, key=dists.get)
        if dists[closest] <= tol:
            self._dragging_line = closest
            self._drag_start_low = low_x
            self._drag_start_high = high_x
            self._drag_start_center = Level

    def on_motion_drag(self, event):
        if self._dragging_line is None or event.inaxes != self.ax or event.xdata is None:
            return
        new_x = event.xdata
        
        if self._dragging_line == 'low':
            high_x = self._drag_start_high
            low_x = new_x
            if low_x >= high_x:
                low_x = high_x - 1.0
            new_W = high_x - low_x
            new_L = (high_x + low_x) / 2.0
            
        elif self._dragging_line == 'high':
            low_x = self._drag_start_low
            high_x = new_x
            if high_x <= low_x:
                high_x = low_x + 1.0
            new_W = high_x - low_x
            new_L = (high_x + low_x) / 2.0
            
        elif self._dragging_line == 'center':
            new_L = new_x
            new_W = self._drag_start_high - self._drag_start_low
            
        # Update Window Level on parent
        from fcn_display.win_level import set_window
        set_window(self.parent_app, new_W, new_L)
        
        # Update lines on this popup histogram axes
        self.update_wl_lines(new_W, new_L)

    def on_bounds_edited(self):
        try:
            low_x = float(self.edit_min.text())
            high_x = float(self.edit_max.text())
            if low_x >= high_x:
                high_x = low_x + 1.0
                self.edit_max.setText(f"{high_x:.2f}")
            new_W = high_x - low_x
            new_L = (high_x + low_x) / 2.0
            
            # Update Window Level on parent
            from fcn_display.win_level import set_window
            set_window(self.parent_app, new_W, new_L)
            
            # Update lines
            self.update_wl_lines(new_W, new_L)
        except ValueError:
            pass

    def on_release(self, event):
        self._dragging_line = None


def open_compare_histogram(self):
    if not hasattr(self, '_comp_hist_dialog') or self._comp_hist_dialog is None:
        self._comp_hist_dialog = CompareHistogramDialog(self)
    self._comp_hist_dialog.update_histogram()
    self._comp_hist_dialog.show()
    self._comp_hist_dialog.raise_()
    self._comp_hist_dialog.activateWindow()
