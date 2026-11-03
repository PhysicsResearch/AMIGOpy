"""
View > View histogram (fcn_init/view_hist.py): it follows the selected layer, the layers set Visible are
shown too and each follows its layer's image, the selected layer's window lines, exact counts in shared
bins, the CSV export and the settings remembered.
"""
import csv

import numpy as np
import pytest


class _WindowLevel:
    def __init__(self, window, level):
        self.window, self.level = window, level

    def GetWindow(self):
        return self.window

    def GetLevel(self):
        return self.level


@pytest.fixture
def win(qapp, tmp_path, monkeypatch):
    """A window with the histogram panel: layer 1 a CT (int16), layer 2 a dose (float, with NaN)."""
    from PySide6.QtWidgets import QComboBox, QWidget
    from fcn_materialassignment import hu_lut
    monkeypatch.setattr(hu_lut, "_settings_path", lambda: str(tmp_path / "settings.json"))
    from fcn_init import view_hist

    w = QWidget()
    w.hist_container_01 = QWidget(w)
    w.layer_selected = QComboBox(w)
    w.layer_selected.addItems(["1", "2", "3", "4"])
    rng = np.random.default_rng(0)
    ct = np.concatenate([np.full(600, -1000), rng.integers(-50, 60, 400)]).astype(np.int16).reshape(10, 10, 10)
    dose = rng.uniform(0, 7, (8, 10, 10))
    dose[0, 0, :3] = np.nan
    w.display_data = {0: ct, 1: dose}
    w.windowLevelAxial = {0: _WindowLevel(400.0, 40.0), 1: _WindowLevel(6.0, 3.0)}
    w.medical_image = {"P": {"S": {"CT": [{"3DMatrix": ct, "metadata": {"SeriesDescription": "Pelvis"}}],
                                   "RTDOSE": [{"3DMatrix": dose, "metadata": {"SeriesDescription": "TG43"}}]}}}
    w.DataType = "DICOM"
    view_hist.init_histogram_ui(w)
    yield w
    w.close()


def _select(w, k):
    from fcn_init.view_hist import set_vtk_histogran_fig
    w.layer_selected.setCurrentIndex(k)
    set_vtk_histogran_fig(w, data_changed=False)


def _layers(w):
    return [k for k, *_ in w._hist_shown["curves"]]


def _counts(w, k):
    return next(counts for layer, _, counts, _ in w._hist_shown["curves"] if layer == k)


def _visible(w, k, on=True):
    """Layer k's Visible box in the Layers menu."""
    from fcn_init.view_hist import _show_layers_menu
    _show_layers_menu(w)
    w._hist_layer_rows[k][0].setChecked(on)


def test_follows_the_selected_layer_and_shows_the_visible_ones(win):
    from fcn_init.view_hist import _show_layers_menu
    w = win
    assert not hasattr(w, "combo_colormap") and not hasattr(w, "hist_hold")
    assert _layers(w) == [0]
    _select(w, 1)
    assert _layers(w) == [1]                                   # the layer shown before is not visible
    _visible(w, 0)
    assert _layers(w) == [0, 1]                                # the selected layer drawn last, on top
    legend = [text.get_text() for text in w.ax_Hist_01.get_legend().get_texts()]
    assert legend == ["Layer 1: CT Pelvis", "Layer 2: RTDOSE TG43"]          # in layer order
    _select(w, 0)
    assert _layers(w) == [0]                                   # layer 2 was shown as the selected one only
    _select(w, 2)                                              # an empty layer selected: the visible one stays
    assert _layers(w) == [0]
    _visible(w, 0, False)
    assert w._hist_shown is None
    _select(w, 1)
    _show_layers_menu(w)
    visible = w._hist_layer_rows[1][0]                         # the selected layer: always shown
    assert visible.isChecked() and not visible.isEnabled() and "(selected)" in w._hist_layer_rows[1][1].text()
    assert w._hist_layer_rows[0][0].isEnabled() and not w._hist_layer_rows[0][0].isChecked()


def test_exact_counts_in_shared_bins(win):
    from fcn_init.view_hist import _changed
    w = win
    _visible(w, 1)
    assert _counts(w, 0).sum() == 1000 and _counts(w, 1).sum() == 800 - 3      # NaN voxels not counted
    _changed(w, values="percent", smooth=False)
    plotted = {k: values for k, _, _, values in w._hist_shown["curves"]}
    assert plotted[0].sum() == pytest.approx(100.0) and plotted[1].sum() == pytest.approx(100.0)
    _changed(w, bin_mode="width", width=10.0, smooth=False, values="voxels")
    edges = w._hist_shown["edges"]
    assert np.allclose(np.diff(edges), 10.0) and np.allclose((edges[:-1] + edges[1:]) / 2 % 10, 0)


def test_a_new_image_in_a_visible_layer_replaces_its_curve(win):
    from fcn_init.view_hist import set_vtk_histogran_fig
    w = win
    _visible(w, 1)
    w.display_data[1] = np.full((2, 5, 5), 4.0)                # a new image in visible layer 2
    _select(w, 0)
    assert _counts(w, 1).sum() == 50
    w.display_data[0][:] = 100                                  # changed in place, then shown again
    set_vtk_histogran_fig(w)
    assert _counts(w, 0).sum() == 1000 and w._hist_cache[0]["range"][:2] == (100.0, 100.0)


def test_window_lines_follow_the_selected_layer(win):
    w = win
    assert w.txt_min_wl.text() == "-160.0" and w.txt_max_wl.text() == "240.0"
    assert w._vline_low.get_visible() and list(w._vline_low.get_xdata()) == [-160.0, -160.0]
    w.hist_wl_lines.setChecked(False)
    assert w._vline_low is None or not w._vline_low.get_visible()
    w.hist_wl_lines.setChecked(True)
    _select(w, 1)
    assert list(w._vline_high.get_xdata()) == [6.0, 6.0] and w.txt_min_wl.text() == "0.0"


def test_dragging_a_window_line(win, monkeypatch):
    from matplotlib.backend_bases import MouseEvent
    from fcn_display import win_level
    calls = []
    monkeypatch.setattr(win_level, "set_window", lambda self, window, level: calls.append((window, level)))
    canvas, ax = win.canvas_Hist_01, win.ax_Hist_01
    canvas.draw()
    y = 0.5 * sum(ax.get_ylim())
    for name, x in (("button_press_event", -160.0), ("motion_notify_event", -100.0), ("button_release_event", -100.0)):
        px, py = ax.transData.transform((x, y))
        canvas.callbacks.process(name, MouseEvent(name, canvas, px, py, button=1))
    window, level = calls[-1]                                   # the low line moved: max stays at 240
    assert window == pytest.approx(340.0, abs=3) and level == pytest.approx(70.0, abs=2)


def test_automatic_y_follows_the_bins_in_view(win):
    from fcn_init.view_hist import _changed
    _changed(win, smooth=False, x_auto=False, x_min=-100.0, x_max=100.0)
    edges = win._hist_shown["edges"]
    in_view = _counts(win, 0)[(edges[1:] >= -100) & (edges[:-1] <= 100)].max()
    assert win.ax_Hist_01.get_ylim()[1] == pytest.approx(in_view * 1.05)    # not the air peak out of view
    assert win.ax_Hist_01.get_xlim() == (-100.0, 100.0)


def test_window_from_the_layer_values(win, monkeypatch):
    from fcn_display import win_level
    from fcn_init.view_hist import _window_from_quantiles, _window_like
    calls = []
    monkeypatch.setattr(win_level, "set_window", lambda self, window, level: calls.append((window, level)))
    _window_from_quantiles(win, 0.0, 1.0)
    assert calls[-1] == (1059.0, -470.5)                        # -1000 .. 59: the CT's full range
    _window_like(win, 1)
    assert calls[-1] == (6.0, 3.0)


def test_iris_data_uses_the_current_slice(win, monkeypatch):
    from fcn_display import win_level
    from fcn_init.view_hist import set_vtk_histogran_fig
    calls = []
    monkeypatch.setattr(win_level, "set_window", lambda self, window, level: calls.append((window, level)))
    frames = np.stack([np.full((4, 5), 10, np.uint16), np.arange(20, dtype=np.uint16).reshape(4, 5)])
    win.DataType = "IrIS"
    win.display_data[0] = frames
    win.current_axial_slice_index = [1, 0, 0, 0]
    set_vtk_histogran_fig(win)
    assert _counts(win, 0).sum() == 20 and win._hist_cache[0]["range"][:2] == (0.0, 19.0)    # frame 1 only
    assert calls[-1] == pytest.approx((3.0 * np.std(np.arange(20)), 9.5))     # its window, as before


def test_export_csv(win, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QFileDialog
    from fcn_init.view_hist import export_histogram_csv
    path = tmp_path / "histogram.csv"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(path), "")))
    _visible(win, 1)
    export_histogram_csv(win)
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    assert header[:5] == ["bin_start", "bin_end", "bin_center", "Layer 1: CT Pelvis voxels",
                          "Layer 1: CT Pelvis (voxels, smoothed)"]
    assert "Layer 2: RTDOSE TG43 voxels" in header and len(body) == len(win._hist_shown["centers"])
    assert sum(float(r[3]) for r in body) == 1000


def test_layer_styles_are_remembered(win, qapp):
    from PySide6.QtWidgets import QComboBox, QWidget
    from fcn_init import view_hist
    view_hist._set_layer_style(win, 1, color="#00ff00", fill=False, alpha=0.6)
    view_hist._changed(win, bins=128, log_y=True)
    other = QWidget()
    other.hist_container_01 = QWidget(other)
    other.layer_selected = QComboBox(other)
    other.display_data = {}
    view_hist.init_histogram_ui(other)
    s = other.hist_settings
    assert s["layers"][1] == {"color": "#00ff00", "fill": False, "alpha": 0.6} and s["bins"] == 128 and s["log_y"]
    assert s["layers"][0]["color"] == view_hist.LAYER_COLORS[0]
    other.close()


def test_figures_menu_restyles_it(win):
    win.selected_font_size = 7
    win._figure_style_listeners["view_histogram"]()
    assert win.ax_Hist_01.xaxis.get_ticklabels()[0].get_fontsize() == 7
