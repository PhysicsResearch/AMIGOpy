from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy, QToolButton, QLabel, QLineEdit, QComboBox
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

    # Bottom row: manual min/max W/L inputs + Colormap dropdown
    bot_row = QWidget(self.hist_container_01)
    h_bot = QHBoxLayout(bot_row)
    h_bot.setContentsMargins(4, 0, 4, 4); h_bot.setSpacing(8)

    lbl_min = QLabel("Min WL:", bot_row)
    self.txt_min_wl = QLineEdit(bot_row)
    self.txt_min_wl.setFixedWidth(80)
    self.txt_min_wl.setPlaceholderText("Min")

    lbl_max = QLabel("Max WL:", bot_row)
    self.txt_max_wl = QLineEdit(bot_row)
    self.txt_max_wl.setFixedWidth(80)
    self.txt_max_wl.setPlaceholderText("Max")

    lbl_cmap = QLabel("Color Map:", bot_row)
    self.combo_colormap = QComboBox(bot_row)
    self.combo_colormap.setObjectName("combo_colormap")
    cmap_options = ["Gray", "Bone", "Hot", "Cold", "Jet", "Viridis", "CoolWarm", "Rainbow", "Magma", "Cividis", "Red", "Green", "Blue"]
    self.combo_colormap.addItems(cmap_options)
    self.combo_colormap.setFixedWidth(100)

    h_bot.addWidget(lbl_min)
    h_bot.addWidget(self.txt_min_wl)
    h_bot.addWidget(lbl_max)
    h_bot.addWidget(self.txt_max_wl)
    h_bot.addSpacing(10)
    h_bot.addWidget(lbl_cmap)
    h_bot.addWidget(self.combo_colormap)
    h_bot.addStretch(1)

    lay_container.addWidget(top_row, 0)
    lay_container.addWidget(self.canvas_Hist_01, 1)
    lay_container.addWidget(bot_row, 0)

    # Connect colormap dropdown
    def _on_combo_cmap_changed(idx_cmap):
        layer_idx = self.layer_selected.currentIndex() if hasattr(self, 'layer_selected') and self.layer_selected is not None else 0
        if hasattr(self, 'CmapIDX') and len(self.CmapIDX) > layer_idx:
            self.CmapIDX[layer_idx] = idx_cmap
        from fcn_display.colormap_set import set_color_map
        set_color_map(self)

    self.combo_colormap.currentIndexChanged.connect(_on_combo_cmap_changed)

    # Connect manual inputs
    def _on_manual_wl_change():
        try:
            min_val = float(self.txt_min_wl.text())
            max_val = float(self.txt_max_wl.text())
            if min_val >= max_val:
                max_val = min_val + 1.0

            new_W = max_val - min_val
            new_L = (max_val + min_val) / 2.0

            from fcn_display.win_level import set_window
            set_window(self, new_W, new_L)
        except ValueError:
            pass

    self.txt_min_wl.editingFinished.connect(_on_manual_wl_change)
    self.txt_max_wl.editingFinished.connect(_on_manual_wl_change)

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

    # Data-driven range (replaces hardcoded HU bounds)
    dmin = float(np.nanmin(data)) if data.size else 0.0
    dmax = float(np.nanmax(data)) if data.size else 1.0
    if not np.isfinite(dmin) or not np.isfinite(dmax) or dmin == dmax:
        dmin, dmax = dmin - 0.5, dmin + 0.5
    lo_all = dmin
    hi_all = dmax

    # Clip + sample
    np.clip(data, lo_all, hi_all, out=data)
    if data.size > 500_000:
        rng = np.random.default_rng(123)
        data = data[rng.choice(data.size, 500_000, replace=False)]

    margin = 0.01 * (dmax - dmin)
    x_lo = dmin - margin; x_hi = dmax + margin
    
    # Adjust to include current window level bounds so bars are always visible
    if hasattr(self, 'windowLevelAxial') and idx in self.windowLevelAxial:
        Window = self.windowLevelAxial[idx].GetWindow()
        Level  = self.windowLevelAxial[idx].GetLevel()
    else:
        Window = 2000.0
        Level = 0.0
    low_x = Level - Window / 2.0
    high_x = Level + Window / 2.0
    margin_wl = max(0.05 * Window, 0.1)
    x_lo = min(x_lo, low_x - margin_wl)
    x_hi = max(x_hi, high_x + margin_wl)

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
    # Do not leak smoothed counts outside the actual data range
    smooth[centers < dmin] = 0.0
    smooth[centers > dmax] = 0.0

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

    # Store data range for histogram interaction clamping
    self._hist_data_lo = lo_all
    self._hist_data_hi = hi_all

    self.fig_Hist_01.subplots_adjust(left=0.06, right=0.99, top=0.95, bottom=0.20)

    # Draw vertical lines for window level
    idx = self.layer_selected.currentIndex()
    if hasattr(self, 'windowLevelAxial') and idx in self.windowLevelAxial:
        Window = self.windowLevelAxial[idx].GetWindow()
        Level  = self.windowLevelAxial[idx].GetLevel()
    else:
        Window = 2000.0
        Level = 0.0

    update_histogram_wl_lines(self, Window, Level)
    init_histogram_interaction(self)


def update_histogram_wl_lines(self, Window, Level):
    if not hasattr(self, 'ax_Hist_01') or not hasattr(self, 'canvas_Hist_01'):
        return
        
    low_x = Level - Window / 2.0
    high_x = Level + Window / 2.0
    
    # Adjust axes limits dynamically if the lines go outside current xlim
    xlim = self.ax_Hist_01.get_xlim()
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
        self.ax_Hist_01.set_xlim(new_xlim[0], new_xlim[1])
        xlim = new_xlim
        
    # Check if we have the lines already on the axes
    lines_exist = True
    for attr in ('_vline_low', '_vline_high', '_vline_center'):
        if not hasattr(self, attr) or getattr(self, attr) not in self.ax_Hist_01.lines:
            lines_exist = False
            break
            
    if lines_exist:
        self._vline_low.set_xdata([low_x, low_x])
        self._vline_high.set_xdata([high_x, high_x])
        self._vline_center.set_xdata([Level, Level])
    else:
        self._vline_low = self.ax_Hist_01.axvline(low_x, color='red', linestyle='--', linewidth=1.5, alpha=0.8)
        self._vline_high = self.ax_Hist_01.axvline(high_x, color='red', linestyle='--', linewidth=1.5, alpha=0.8)
        self._vline_center = self.ax_Hist_01.axvline(Level, color='yellow', linestyle=':', linewidth=1.0, alpha=0.6)
        
    # Remove old overlay fill if it exists
    if hasattr(self, '_fill_out'):
        try:
            self._fill_out.remove()
        except Exception:
            pass

    # Draw new black overlay fill under the curve, outside the W/L region
    if hasattr(self, '_hist_centers') and hasattr(self, '_hist_counts') and self._hist_centers.size:
        centers = self._hist_centers
        smooth = self._hist_counts
        self._fill_out = self.ax_Hist_01.fill_between(
            centers, smooth, where=(centers < low_x) | (centers > high_x),
            step='mid', facecolor='black', alpha=0.45
        )

    # Update text fields if they are not currently focused
    if hasattr(self, 'txt_min_wl') and not self.txt_min_wl.hasFocus():
        self.txt_min_wl.setText(f"{low_x:.1f}")
    if hasattr(self, 'txt_max_wl') and not self.txt_max_wl.hasFocus():
        self.txt_max_wl.setText(f"{high_x:.1f}")

    if hasattr(self, 'combo_colormap') and self.combo_colormap is not None:
        idx = self.layer_selected.currentIndex() if hasattr(self, 'layer_selected') and self.layer_selected is not None else 0
        if hasattr(self, 'CmapIDX') and len(self.CmapIDX) > idx:
            self.combo_colormap.blockSignals(True)
            self.combo_colormap.setCurrentIndex(int(self.CmapIDX[idx]))
            self.combo_colormap.blockSignals(False)

    self.canvas_Hist_01.draw_idle()


def init_histogram_interaction(self):
    if hasattr(self, '_hist_interaction_connected') and self._hist_interaction_connected:
        return
        
    self._dragging_line = None
    self._hist_interaction_connected = True
    
    def on_press(event):
        if event.inaxes != self.ax_Hist_01:
            return
        if event.button != 1:  # Left click only
            return
            
        # Get click x coordinate
        click_x = event.xdata
        if click_x is None:
            return
            
        xlim = self.ax_Hist_01.get_xlim()
        tol = 0.02 * (xlim[1] - xlim[0])
        
        idx = self.layer_selected.currentIndex()
        if hasattr(self, 'windowLevelAxial') and idx in self.windowLevelAxial:
            Window = self.windowLevelAxial[idx].GetWindow()
            Level  = self.windowLevelAxial[idx].GetLevel()
        else:
            Window = 2000.0
            Level = 0.0
            
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
            
    def on_motion(event):
        if self._dragging_line is None or event.inaxes != self.ax_Hist_01:
            return
        new_x = event.xdata
        if new_x is None:
            return
            
        from fcn_display.win_level import set_window
        
        if self._dragging_line == 'low':
            high_x = self._drag_start_high
            low_x = new_x
            if low_x >= high_x:
                low_x = high_x - 1.0
            new_W = high_x - low_x
            new_L = (high_x + low_x) / 2.0
            set_window(self, new_W, new_L)
            
        elif self._dragging_line == 'high':
            low_x = self._drag_start_low
            high_x = new_x
            if high_x <= low_x:
                high_x = low_x + 1.0
            new_W = high_x - low_x
            new_L = (high_x + low_x) / 2.0
            set_window(self, new_W, new_L)
            
        elif self._dragging_line == 'center':
            new_L = new_x
            new_W = self._drag_start_high - self._drag_start_low
            set_window(self, new_W, new_L)
            
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
        data = app.display_comp_data[ref_idx, layer].ravel().astype(np.float32, copy=False)
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
