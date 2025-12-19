from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy, QToolButton, QLabel
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import matplotlib as mpl

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

def init_histogram_ui(self):
    # Always (re)install a clean VERTICAL layout on the container
    lay_container = QVBoxLayout()
    lay_container.setContentsMargins(0, 0, 0, 0)
    lay_container.setSpacing(2)
    self.hist_container_01.setLayout(lay_container)

    # Figure / canvas
    self.fig_Hist_01 = Figure(figsize=(6, 2.0), dpi=100)
    self.ax_Hist_01  = self.fig_Hist_01.add_subplot(111)
    self.ax_Hist_01.set_facecolor('none'); self.fig_Hist_01.set_facecolor('none')

    self.canvas_Hist_01 = FigureCanvas(self.fig_Hist_01)
    self.canvas_Hist_01.setFocusPolicy(Qt.StrongFocus)
    self.canvas_Hist_01.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum))

    # Top row: toolbar (left) + (x,y) label (left)
    toolbar = MiniToolbar(self.canvas_Hist_01, self)
    self.toolbar_Hist_01 = toolbar  # keep a ref if you need it

    self._xy_label = QLabel("(x, y) = (—, —)", self)
    self._xy_label.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))

    top_row = QWidget(self.hist_container_01)
    h = QHBoxLayout(top_row)
    h.setContentsMargins(0, 0, 0, 0); h.setSpacing(6)
    h.addWidget(toolbar, 0, Qt.AlignLeft)
    h.addSpacing(8)
    h.addWidget(self._xy_label, 0, Qt.AlignLeft)
    h.addStretch(1)

    lay_container.addWidget(top_row, 0)
    lay_container.addWidget(self.canvas_Hist_01, 1)

    # Interactions
    self._hist_zoom_factor = 1.2
    self.canvas_Hist_01.mpl_connect('scroll_event', lambda ev: _on_hist_wheel(self, ev))

    def _on_motion(ev):
        if ev.inaxes is not self.ax_Hist_01 or ev.xdata is None:
            self._xy_label.setText("(x, y) = (—, —)")
            return
        x = float(ev.xdata); y = 0.0
        if hasattr(self, "_hist_centers") and hasattr(self, "_hist_counts") and self._hist_centers.size:
            i = int(np.clip(np.searchsorted(self._hist_centers, x) - 1, 0, self._hist_centers.size - 1))
            y = float(self._hist_counts[i])
        self._xy_label.setText(f"(x, y) = ({x:.0f}, {y:,.2f})")
    self.canvas_Hist_01.mpl_connect('motion_notify_event', _on_motion)

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

    # Clip + sample
    lo_all, hi_all = -1024.0, 3072.0
    np.clip(data, lo_all, hi_all, out=data)
    if data.size > 500_000:
        rng = np.random.default_rng(123)
        data = data[rng.choice(data.size, 500_000, replace=False)]

    # Autoscale X to data span within HU bounds
    dmin = float(np.min(data)) if data.size else lo_all
    dmax = float(np.max(data)) if data.size else hi_all
    if not np.isfinite(dmin) or not np.isfinite(dmax) or dmin == dmax:
        dmin, dmax = lo_all, hi_all
    margin = 0.01 * (dmax - dmin if dmax > dmin else (hi_all - lo_all))
    x_lo = max(lo_all, dmin - margin); x_hi = min(hi_all, dmax + margin)

    # Histogram + smoothing
    counts, edges = np.histogram(data, bins=512, range=(x_lo, x_hi))
    centers = 0.5 * (edges[:-1] + edges[1:])
    if counts.size >= 13:
        k = 13; x = np.arange(k) - (k - 1) / 2.0; sigma = 2.0
        ker = np.exp(-0.5 * (x / sigma) ** 2); ker /= ker.sum()
        smooth = np.convolve(counts.astype(float), ker, mode='same')
    else:
        smooth = counts.astype(float)

    # Keep arrays for hover
    self._hist_centers = centers
    self._hist_counts  = smooth

    ax = self.ax_Hist_01
    ax.clear(); ax.set_facecolor('none')
    ax.plot(centers, smooth, lw=1)
    ax.fill_between(centers, smooth, step='mid', alpha=0.25)

    ax.tick_params(axis='both', which='major', labelsize=10, colors='white')
    for sp in ax.spines.values(): sp.set_color('white')

    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(0, max(1.0, float(smooth.max())) * 1.05)

    self.fig_Hist_01.subplots_adjust(left=0.06, right=0.99, top=0.95, bottom=0.20)
    self.canvas_Hist_01.draw_idle()
