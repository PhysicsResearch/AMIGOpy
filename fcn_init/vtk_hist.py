# fcn_init/vtk_hist.py
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QVBoxLayout, QSizePolicy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import numpy as np

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
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self.setMaximumHeight(26)

def _on_hist_wheel(self, event):
    if event.inaxes is not getattr(self, "ax_Hist_01", None) or event.xdata is None:
        return
    ax = self.ax_Hist_01
    # default: zoom X; Shift: zoom Y; Ctrl: both
    zoom_x, zoom_y = True, False
    if event.key == 'shift':
        zoom_x, zoom_y = False, True
    elif event.key == 'control':
        zoom_x, zoom_y = True, True
    scale = getattr(self, "_hist_zoom_factor", 1.2)
    scale = scale if event.button == 'up' else 1.0 / scale

    if zoom_x:
        x0, x1 = ax.get_xlim(); xc = event.xdata
        new_w = (x1 - x0) / scale
        x0n = xc - (xc - x0) / scale
        ax.set_xlim(x0n, x0n + new_w)
    if zoom_y and event.ydata is not None:
        y0, y1 = ax.get_ylim(); yc = event.ydata
        new_h = (y1 - y0) / scale
        y0n = yc - (yc - y0) / scale
        ax.set_ylim(y0n, y0n + new_h)

    self.canvas_Hist_01.draw_idle()

def init_histogram_ui(self):
    # create once
    if hasattr(self, "canvas_Hist_01"):
        return
    self.fig_Hist_01 = Figure(figsize=(6, 2.0), dpi=100)
    self.ax_Hist_01 = self.fig_Hist_01.add_subplot(111)
    self.ax_Hist_01.set_facecolor('none'); self.fig_Hist_01.set_facecolor('none')

    self.canvas_Hist_01 = FigureCanvas(self.fig_Hist_01)
    self.canvas_Hist_01.setFocusPolicy(Qt.StrongFocus)
    self.canvas_Hist_01.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum))

    self.toolbar_Hist_01 = MiniToolbar(self.canvas_Hist_01, self)

    if self.hist_container_01.layout() is None:
        self.hist_container_01.setLayout(QVBoxLayout())
    lay = self.hist_container_01.layout()
    lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(2)
    while lay.count():
        w = lay.takeAt(0).widget()
        if w: w.deleteLater()
    lay.addWidget(self.toolbar_Hist_01)
    lay.addWidget(self.canvas_Hist_01)

    self._hist_zoom_factor = 1.2
    # IMPORTANT: bind module-level function with self
    self.canvas_Hist_01.mpl_connect('scroll_event', lambda ev: _on_hist_wheel(self, ev))

    self.fig_Hist_01.subplots_adjust(left=0.06, right=0.99, top=0.95, bottom=0.20)
    self.canvas_Hist_01.draw_idle()

def set_vtk_histogran_fig(self):
    if not hasattr(self, 'canvas_Hist_01'):
        init_histogram_ui(self)

    idx = self.layer_selected.currentIndex()
    if self.DataType == "IrIS":
        arr = (self.display_data[idx] if self.display_data[idx].ndim == 2
               else self.display_data[idx][self.current_axial_slice_index[idx], :, :])
        data = arr.ravel().astype(np.float32, copy=False)
        from fcn_display.win_level import set_window
        set_window(self, float(np.std(data))*3.0, float(np.mean(data)))
    else:
        data = self.display_data[idx].ravel().astype(np.float32, copy=False)

    lo, hi = -1024.0, 3072.0
    np.clip(data, lo, hi, out=data)
    if data.size > 500_000:
        rng = np.random.default_rng(123)
        data = data[rng.choice(data.size, 500_000, replace=False)]

    counts, edges = np.histogram(data, bins=512, range=(lo, hi))
    centers = 0.5 * (edges[:-1] + edges[1:])

    ax = self.ax_Hist_01
    ax.clear(); ax.set_facecolor('none')
    ax.plot(centers, counts, lw=1)
    ax.tick_params(axis='both', which='major', labelsize=10, colors='white')
    for sp in ax.spines.values(): sp.set_color('white')
    ax.set_xlim(lo, hi); ax.set_ylim(0, max(1, counts.max()))
    self.fig_Hist_01.subplots_adjust(left=0.06, right=0.99, top=0.95, bottom=0.20)
    self.canvas_Hist_01.draw_idle()
