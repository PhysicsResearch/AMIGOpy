# fcn_display/roi_additional_plots.py

import os
import csv
from PySide6 import QtWidgets, QtCore, QtGui
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)

class ROIDialog(QtWidgets.QDialog):
    def __init__(
        self,
        parent: QtWidgets.QWidget,
        display_data: dict,
        Im_Offset: np.ndarray,
        pixel_spac: np.ndarray,
        slice_thick: np.ndarray,
        orientation: str,
        center: tuple,
        radii: tuple,
        roi_type: str = 'circle',
        window_title: str = 'ROI Analysis'
    ):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        # Store context variables
        self.main_window = parent
        self.display_data = display_data
        self.Im_Offset = Im_Offset
        self.pixel_spac = pixel_spac
        self.slice_thick = slice_thick
        self.orientation = orientation
        self.center = center
        self.radii = radii
        self.roi_type = roi_type

        # Extraction parameters
        self.cx_mm, self.cy_mm, _ = center
        if roi_type == 'square':
            self.rx_mm, self.ry_mm = radii

        # Theme and view state variables
        self.current_theme = 'dark'  # default theme
        self.overlay_mode = False
        self.avg_mode = False

        # Gather ROI data per layer
        self.entries = []  # for circle/ellipse
        self.subs = []     # for rectangle/square
        self.gather_roi_data()

        # Initialize per-layer styling map
        # idx -> { 'name': str, 'visible': bool, 'color': str, 'linestyle': str, 'marker': str, 'markersize': int }
        self.layer_styles = {}
        default_colors = ['cyan', 'red', 'green', 'magenta', 'yellow', 'blue', 'white', 'black']
        active_layers = [info['idx'] for info in self.subs] if roi_type == 'square' else [e[3] for e in self.entries]
        for i, idx in enumerate(active_layers):
            self.layer_styles[idx] = {
                'name': f"Layer {idx}",
                'visible': True,
                'color': default_colors[i % len(default_colors)],
                'linestyle': '-',
                'marker': 'None',
                'markersize': 4
            }

        # Matplotlib Figure and Canvas Setup
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Setup GUI layout
        self.setup_ui()
        self.apply_theme()
        self.update_plots()

    def gather_roi_data(self):
        cx_mm, cy_mm = self.cx_mm, self.cy_mm
        radii = self.radii
        if self.roi_type == 'square':
            rx_mm, ry_mm = self.rx_mm, self.ry_mm

        for idx, data in self.display_data.items():
            if data is None or not hasattr(data, 'ndim'):
                continue

            try:
                if data.ndim == 2:
                    slc = data
                elif self.orientation == 'axial':
                    slc = data[self.main_window.current_axial_slice_index[idx]]
                elif self.orientation == 'coronal':
                    slc = data[:, self.main_window.current_coronal_slice_index[idx]]
                else:  # sagittal
                    slc = data[:, :, self.main_window.current_sagittal_slice_index[idx]]
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "ROI Plot Error",
                    f"Layer {idx}: cannot extract slice ({e})."
                )
                continue

            h, w = slc.shape

            # map world-center -> pixel (px,py)
            if self.orientation == 'axial':
                px = (cx_mm - self.Im_Offset[idx,0]) / self.pixel_spac[idx,0]
                py = (cy_mm - self.Im_Offset[idx,1]) / self.pixel_spac[idx,1]
            elif self.orientation == 'coronal':
                px = (cx_mm - self.Im_Offset[idx,0]) / self.pixel_spac[idx,0]
                py = (cy_mm - self.Im_Offset[idx,2]) / self.slice_thick[idx]
            else:  # sagittal
                px = (cx_mm - self.Im_Offset[idx,1]) / self.pixel_spac[idx,1]
                py = (cy_mm - self.Im_Offset[idx,2]) / self.slice_thick[idx]

            px, py = int(round(px)), int(round(py))
            px = np.clip(px, 0, w-1)
            py = np.clip(py, 0, h-1)

            if self.roi_type in ('circle','ellipse'):
                rx_mm, ry_mm = radii
                if self.orientation == 'axial':
                    rpx = int(round(rx_mm / self.pixel_spac[idx,0]))
                    rpy = int(round(ry_mm / self.pixel_spac[idx,1]))
                elif self.orientation == 'coronal':
                    rpx = int(round(rx_mm / self.pixel_spac[idx,0]))
                    rpy = int(round(ry_mm / self.slice_thick[idx]))
                else:
                    rpx = int(round(rx_mm / self.pixel_spac[idx,1]))
                    rpy = int(round(ry_mm / self.slice_thick[idx]))
                self.entries.append((slc, px, py, idx, rpx, rpy))
            else:
                if self.orientation == 'axial':
                    rpx = int(round(rx_mm / self.pixel_spac[idx,0]))
                    rpy = int(round(ry_mm / self.pixel_spac[idx,1]))
                elif self.orientation == 'coronal':
                    rpx = int(round(rx_mm / self.pixel_spac[idx,0]))
                    rpy = int(round(ry_mm / self.slice_thick[idx]))
                else:  # sagittal
                    rpx = int(round(rx_mm / self.pixel_spac[idx,1]))
                    rpy = int(round(ry_mm / self.slice_thick[idx]))

                yy, xx = np.ogrid[:h, :w]
                mask = (np.abs(xx - px) <= rpx) & (np.abs(yy - py) <= rpy)
                rows = np.any(mask, axis=1)
                cols = np.any(mask, axis=0)
                if not rows.any() or not cols.any():
                    continue
                y0, y1 = np.where(rows)[0][[0, -1]]
                x0, x1 = np.where(cols)[0][[0, -1]]
                sub = slc[y0:y1+1, x0:x1+1]
                if sub.size:
                    self.subs.append({'idx': idx, 'sub': sub, 'x0': x0, 'y0': y0})

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # 1. Top Controls Layout
        top_bar = QtWidgets.QHBoxLayout()

        self.btn_theme = QtWidgets.QPushButton("Switch Theme")
        self.btn_theme.setStyleSheet("background-color: blue; color: white; font-weight: bold; min-height: 25px; border-radius: 4px; padding: 4px;")
        self.btn_theme.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.btn_theme)

        self.btn_export = QtWidgets.QPushButton("Export CSV")
        self.btn_export.setStyleSheet("background-color: blue; color: white; font-weight: bold; min-height: 25px; border-radius: 4px; padding: 4px;")
        self.btn_export.clicked.connect(self.export_csv)
        top_bar.addWidget(self.btn_export)

        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # Matplotlib toolbar
        main_layout.addWidget(self.toolbar)

        # Horizontal layout for plot + side customizer controls
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.addWidget(self.canvas, stretch=4)

        # Settings sidebar panel
        self.sidebar = QtWidgets.QGroupBox("Settings")
        sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar)
        self.sidebar.setMaximumWidth(300)

        # Global Graph Settings Groupbox
        self.global_group = QtWidgets.QGroupBox("Global Graph Settings")
        global_layout = QtWidgets.QVBoxLayout(self.global_group)

        # Global overlay and average checkbox controls moved here
        self.btn_overlay = QtWidgets.QCheckBox("Show all data in the same row")
        self.btn_overlay.toggled.connect(self.toggle_overlay)
        global_layout.addWidget(self.btn_overlay)
        num_layers = len(self.subs) if self.roi_type == 'square' else len(self.entries)
        if num_layers <= 1:
            self.btn_overlay.setVisible(False)

        if self.roi_type == 'square':
            self.chk_avg = QtWidgets.QCheckBox("Show average line profile")
            self.chk_avg.toggled.connect(self.toggle_avg)
            global_layout.addWidget(self.chk_avg)

        # Separator line
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        global_layout.addWidget(line)

        # Custom Titles
        lay_t1 = QtWidgets.QHBoxLayout()
        lay_t1.addWidget(QtWidgets.QLabel("Hist Title:"))
        self.txt_hist_title = QtWidgets.QLineEdit()
        self.txt_hist_title.setPlaceholderText("Auto")
        self.txt_hist_title.textChanged.connect(lambda: self.update_plots())
        lay_t1.addWidget(self.txt_hist_title)
        global_layout.addLayout(lay_t1)

        lay_t2 = QtWidgets.QHBoxLayout()
        lay_t2.addWidget(QtWidgets.QLabel("Vert Title:"))
        self.txt_vert_title = QtWidgets.QLineEdit()
        self.txt_vert_title.setPlaceholderText("Auto")
        self.txt_vert_title.textChanged.connect(lambda: self.update_plots())
        lay_t2.addWidget(self.txt_vert_title)
        global_layout.addLayout(lay_t2)

        lay_t3 = QtWidgets.QHBoxLayout()
        lay_t3.addWidget(QtWidgets.QLabel("Horz Title:"))
        self.txt_horz_title = QtWidgets.QLineEdit()
        self.txt_horz_title.setPlaceholderText("Auto")
        self.txt_horz_title.textChanged.connect(lambda: self.update_plots())
        lay_t3.addWidget(self.txt_horz_title)
        global_layout.addLayout(lay_t3)

        # Global Font Settings
        lay_fs = QtWidgets.QHBoxLayout()
        lay_fs.addWidget(QtWidgets.QLabel("Font Size:"))
        self.spin_font_size = QtWidgets.QSpinBox()
        self.spin_font_size.setRange(6, 24)
        self.spin_font_size.setValue(10)
        self.spin_font_size.valueChanged.connect(lambda: self.update_plots())
        lay_fs.addWidget(self.spin_font_size)
        global_layout.addLayout(lay_fs)

        lay_fc = QtWidgets.QHBoxLayout()
        lay_fc.addWidget(QtWidgets.QLabel("Font Color:"))
        self.cmb_font_color = QtWidgets.QComboBox()
        self.cmb_font_color.addItems(['Default/Theme', 'White', 'Black', 'Gray', 'Red', 'Green', 'Blue', 'Yellow', 'Cyan', 'Magenta'])
        self.cmb_font_color.currentTextChanged.connect(lambda: self.update_plots())
        lay_fc.addWidget(self.cmb_font_color)
        global_layout.addLayout(lay_fc)

        sidebar_layout.addWidget(self.global_group)

        # Add scroll area for Layer Customization sidebar
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Generate a styling row for each layer
        for idx, style in self.layer_styles.items():
            row_box = QtWidgets.QGroupBox(f"Layer {idx} Customization")
            row_layout = QtWidgets.QVBoxLayout(row_box)

            # Name Label Input
            lay_lbl = QtWidgets.QHBoxLayout()
            lay_lbl.addWidget(QtWidgets.QLabel("Label:"))
            txt_lbl = QtWidgets.QLineEdit()
            txt_lbl.setText(style['name'])
            txt_lbl.textChanged.connect(lambda val, i=idx: self.update_style(i, 'name', val))
            lay_lbl.addWidget(txt_lbl)
            row_layout.addLayout(lay_lbl)

            # Visibility Checkbox
            chk_vis = QtWidgets.QCheckBox("Visible")
            chk_vis.setChecked(style['visible'])
            chk_vis.toggled.connect(lambda val, i=idx: self.update_style(i, 'visible', val))
            row_layout.addWidget(chk_vis)

            # Color Selection
            lay_color = QtWidgets.QHBoxLayout()
            lay_color.addWidget(QtWidgets.QLabel("Color:"))
            cmb_color = QtWidgets.QComboBox()
            cmb_color.addItems(['Cyan', 'Red', 'Green', 'Magenta', 'Yellow', 'Blue', 'White', 'Black'])
            cmb_color.setCurrentText(style['color'].capitalize())
            cmb_color.currentTextChanged.connect(lambda val, i=idx: self.update_style(i, 'color', val.lower()))
            lay_color.addWidget(cmb_color)
            row_layout.addLayout(lay_color)

            # Line Style Selection
            lay_style = QtWidgets.QHBoxLayout()
            lay_style.addWidget(QtWidgets.QLabel("Style:"))
            cmb_style = QtWidgets.QComboBox()
            cmb_style.addItems(['Solid', 'Dashed', 'Dotted', 'Dash-Dot', 'None'])
            style_map_inv = {'-': 'Solid', '--': 'Dashed', ':': 'Dotted', '-.': 'Dash-Dot', 'None': 'None'}
            cmb_style.setCurrentText(style_map_inv.get(style['linestyle'], 'Solid'))
            style_map = {'Solid': '-', 'Dashed': '--', 'Dotted': ':', 'Dash-Dot': '-.', 'None': 'None'}
            cmb_style.currentTextChanged.connect(lambda val, i=idx: self.update_style(i, 'linestyle', style_map[val]))
            lay_style.addWidget(cmb_style)
            row_layout.addLayout(lay_style)

            # Marker Size Selection
            lay_marker = QtWidgets.QHBoxLayout()
            lay_marker.addWidget(QtWidgets.QLabel("Point Size:"))
            spin_size = QtWidgets.QSpinBox()
            spin_size.setRange(0, 15)
            spin_size.setValue(style['markersize'])
            spin_size.valueChanged.connect(lambda val, i=idx: self.update_style(i, 'markersize', val))
            lay_marker.addWidget(spin_size)
            row_layout.addLayout(lay_marker)

            scroll_layout.addWidget(row_box)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        sidebar_layout.addWidget(scroll_area)
        content_layout.addWidget(self.sidebar, stretch=1)

        main_layout.addLayout(content_layout)

        # 2. X and Y Sliders for Rectangle ROI
        if self.roi_type == 'square' and self.subs:
            # compute world extents
            world_x0, world_x1, world_y0, world_y1 = [], [], [], []
            for info in self.subs:
                idx, sub, x0, y0 = info['idx'], info['sub'], info['x0'], info['y0']
                if self.orientation == 'axial':
                    wx = self.Im_Offset[idx,0]
                    world_x0.append(wx + x0 * self.pixel_spac[idx,0])
                    world_x1.append(wx + (x0 + sub.shape[1] - 1) * self.pixel_spac[idx,0])
                elif self.orientation == 'sagittal':
                    wy = self.Im_Offset[idx,1]
                    world_x0.append(wy + x0 * self.pixel_spac[idx,1])
                    world_x1.append(wy + (x0 + sub.shape[1] - 1) * self.pixel_spac[idx,1])
                else:  # coronal
                    wx = self.Im_Offset[idx,0]
                    world_x0.append(wx + x0 * self.pixel_spac[idx,0])
                    world_x1.append(wx + (x0 + sub.shape[1] - 1) * self.pixel_spac[idx,0])

                if self.orientation == 'axial':
                    wy = self.Im_Offset[idx,1]
                    world_y0.append(wy + y0 * self.pixel_spac[idx,1])
                    world_y1.append(wy + (y0 + sub.shape[0] - 1) * self.pixel_spac[idx,1])
                else:
                    wz = self.Im_Offset[idx,2]
                    world_y0.append(wz + y0 * self.slice_thick[idx])
                    world_y1.append(wz + (y0 + sub.shape[0] - 1) * self.slice_thick[idx])

            self.col_min = int(np.floor(min(world_x0)))
            self.col_max = int(np.ceil(max(world_x1)))
            self.row_min = int(np.floor(min(world_y0)))
            self.row_max = int(np.ceil(max(world_y1)))

            self.slider_layout = QtWidgets.QHBoxLayout()

            # X Slider
            self.sld_x_box = QtWidgets.QVBoxLayout()
            self.sld_x = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            self.sld_x.setRange(self.col_min, self.col_max)
            self.sld_x.setValue(int(round(self.cx_mm)))
            self.lbl_x = QtWidgets.QLabel(f"X={self.cx_mm:.1f} mm")
            self.sld_x.valueChanged.connect(self.on_slider_changed)
            self.sld_x_box.addWidget(self.lbl_x)
            self.sld_x_box.addWidget(self.sld_x)

            # Y Slider
            self.sld_y_box = QtWidgets.QVBoxLayout()
            self.sld_y = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            self.sld_y.setRange(self.row_min, self.row_max)
            self.sld_y.setValue(int(round(self.cy_mm)))
            self.lbl_y = QtWidgets.QLabel(f"Y={self.cy_mm:.1f} mm")
            self.sld_y.valueChanged.connect(self.on_slider_changed)
            self.sld_y_box.addWidget(self.lbl_y)
            self.sld_y_box.addWidget(self.sld_y)

            self.slider_layout.addLayout(self.sld_x_box)
            self.slider_layout.addLayout(self.sld_y_box)
            main_layout.addLayout(self.slider_layout)

    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme()
        self.update_plots()

    def apply_theme(self):
        if self.current_theme == 'dark':
            import qdarkstyle
            self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
            self.sidebar.setStyleSheet("QGroupBox { font-weight: bold; }")
        else:
            self.setStyleSheet("")
            self.sidebar.setStyleSheet("")

    def toggle_overlay(self, checked):
        self.overlay_mode = checked
        self.update_plots()

    def toggle_avg(self, checked):
        self.avg_mode = checked
        # Show/hide/disable sliders in average mode
        if hasattr(self, 'sld_x'):
            self.sld_x.setEnabled(not checked)
            self.sld_y.setEnabled(not checked)
        self.update_plots()

    def update_style(self, layer_idx, style_key, value):
        self.layer_styles[layer_idx][style_key] = value
        self.update_plots()

    def on_slider_changed(self):
        if hasattr(self, 'sld_x') and hasattr(self, 'sld_y'):
            val_x = self.sld_x.value()
            val_y = self.sld_y.value()
            self.lbl_x.setText(f"X={val_x} mm")
            self.lbl_y.setText(f"Y={val_y} mm")
            self.update_plots()

    def update_plots(self):
        self.fig.clear()

        # Gather visible layers
        visible_layers = [idx for idx, style in self.layer_styles.items() if style['visible']]

        if not visible_layers:
            self.canvas.draw()
            return

        # Fetch custom titles
        hist_custom = self.txt_hist_title.text().strip()
        vert_custom = self.txt_vert_title.text().strip()
        horz_custom = self.txt_horz_title.text().strip()

        # Prepare plots
        if self.roi_type in ('circle', 'ellipse'):
            active_entries = [e for e in self.entries if e[3] in visible_layers]
            if not active_entries:
                self.canvas.draw()
                return

            if self.overlay_mode:
                axes = self.fig.subplots(1, 3, squeeze=False)
                axh, axv, axH = axes[0]
                
                # Compute global profile limits for formatting
                all_ys = []
                all_xs = []
                for slc, px, py, idx, rpx, rpy in active_entries:
                    if self.orientation == 'axial':
                        y_world = self.Im_Offset[idx,1] + np.arange(slc.shape[0]) * self.pixel_spac[idx,1]
                    else:
                        y_world = self.Im_Offset[idx,2] + np.arange(slc.shape[0]) * self.slice_thick[idx]
                    all_ys.append((y_world.min(), y_world.max()))

                    if self.orientation in ('axial','coronal'):
                        x_world = self.Im_Offset[idx,0] + np.arange(slc.shape[1]) * self.pixel_spac[idx,0]
                    else:
                        x_world = self.Im_Offset[idx,1] + np.arange(slc.shape[1]) * self.pixel_spac[idx,1]
                    all_xs.append((x_world.min(), x_world.max()))

                y_min, y_max = min(y0 for y0,y1 in all_ys), max(y1 for y0,y1 in all_ys)
                x_min, x_max = min(x0 for x0,x1 in all_xs), max(x1 for x0,x1 in all_xs)

                axh.set_title(hist_custom if hist_custom else "Overlaid Histograms")
                axv.set_title(vert_custom if vert_custom else "Overlaid Vertical Profiles")
                axH.set_title(horz_custom if horz_custom else "Overlaid Horizontal Profiles")
                axv.set_xlim(y_min, y_max)
                axH.set_xlim(x_min, x_max)

                for slc, px, py, idx, rpx, rpy in active_entries:
                    st = self.layer_styles[idx]
                    color = st['color']
                    ls = st['linestyle']
                    ms = st['markersize']
                    marker = 'o' if ms > 0 else 'None'
                    lbl_name = st['name']

                    # Histogram
                    yy, xx = np.ogrid[:slc.shape[0], :slc.shape[1]]
                    mask = ((xx-px)**2)/(rpx**2) + ((yy-py)**2)/(rpy**2) <= 1
                    axh.hist(slc[mask].ravel(), bins='auto', alpha=0.5, density=True, label=lbl_name, color=color)
                    axh.legend()

                    # Vertical
                    row_start = max(0, py-rpy)
                    row_end   = min(slc.shape[0]-1, py+rpy)
                    if self.orientation == 'axial':
                        ys = self.Im_Offset[idx,1] + np.arange(slc.shape[0]) * self.pixel_spac[idx,1]
                    else:
                        ys = self.Im_Offset[idx,2] + np.arange(slc.shape[0]) * self.slice_thick[idx]
                    
                    if ls != 'None' or marker != 'None':
                        axv.plot(ys, slc[:,px], color=color, linestyle=ls, marker=marker, markersize=ms, label=lbl_name)
                        axv.axvline(ys[row_start], color=color, linestyle='--')
                        axv.axvline(ys[row_end], color=color, linestyle='--')
                    axv.legend()

                    # Horizontal
                    col_start = max(0, px-rpx)
                    col_end   = min(slc.shape[1]-1, px+rpx)
                    if self.orientation in ('axial','coronal'):
                        xs = self.Im_Offset[idx,0] + np.arange(slc.shape[1]) * self.pixel_spac[idx,0]
                    else:
                        xs = self.Im_Offset[idx,1] + np.arange(slc.shape[1]) * self.pixel_spac[idx,1]

                    if ls != 'None' or marker != 'None':
                        axH.plot(xs, slc[py,:], color=color, linestyle=ls, marker=marker, markersize=ms, label=lbl_name)
                        axH.axvline(xs[col_start], color=color, linestyle='--')
                        axH.axvline(xs[col_end], color=color, linestyle='--')
                    axH.legend()
            else:
                n = len(active_entries)
                axes = self.fig.subplots(n, 3, squeeze=False)
                
                # Compute global profile limits for formatting
                all_ys = []
                all_xs = []
                for slc, px, py, idx, rpx, rpy in active_entries:
                    if self.orientation == 'axial':
                        y_world = self.Im_Offset[idx,1] + np.arange(slc.shape[0]) * self.pixel_spac[idx,1]
                    else:
                        y_world = self.Im_Offset[idx,2] + np.arange(slc.shape[0]) * self.slice_thick[idx]
                    all_ys.append((y_world.min(), y_world.max()))

                    if self.orientation in ('axial','coronal'):
                        x_world = self.Im_Offset[idx,0] + np.arange(slc.shape[1]) * self.pixel_spac[idx,0]
                    else:
                        x_world = self.Im_Offset[idx,1] + np.arange(slc.shape[1]) * self.pixel_spac[idx,1]
                    all_xs.append((x_world.min(), x_world.max()))

                y_min, y_max = min(y0 for y0,y1 in all_ys), max(y1 for y0,y1 in all_ys)
                x_min, x_max = min(x0 for x0,x1 in all_xs), max(x1 for x0,x1 in all_xs)

                for r, (slc, px, py, idx, rpx, rpy) in enumerate(active_entries):
                    axh, axv, axH = axes[r]
                    st = self.layer_styles[idx]
                    color = st['color']
                    ls = st['linestyle']
                    ms = st['markersize']
                    marker = 'o' if ms > 0 else 'None'
                    lbl_name = st['name']

                    # Histogram
                    yy, xx = np.ogrid[:slc.shape[0], :slc.shape[1]]
                    mask = ((xx-px)**2)/(rpx**2) + ((yy-py)**2)/(rpy**2) <= 1
                    axh.hist(slc[mask].ravel(), bins='auto', density=True, color=color)
                    axh.set_title(hist_custom if hist_custom else f"{lbl_name} Histogram")

                    # Vertical
                    row_start = max(0, py-rpy)
                    row_end   = min(slc.shape[0]-1, py+rpy)
                    if self.orientation == 'axial':
                        ys = self.Im_Offset[idx,1] + np.arange(slc.shape[0]) * self.pixel_spac[idx,1]
                    else:
                        ys = self.Im_Offset[idx,2] + np.arange(slc.shape[0]) * self.slice_thick[idx]

                    if ls != 'None' or marker != 'None':
                        axv.plot(ys, slc[:,px], color=color, linestyle=ls, marker=marker, markersize=ms)
                        axv.axvline(ys[row_start], color='r', linestyle='--')
                        axv.axvline(ys[row_end], color='r', linestyle='--')
                    axv.set_xlabel('Y (mm)')
                    axv.set_title(vert_custom if vert_custom else f"{lbl_name} Vertical")
                    axv.set_xlim(y_min, y_max)

                    # Horizontal
                    col_start = max(0, px-rpx)
                    col_end   = min(slc.shape[1]-1, px+rpx)
                    if self.orientation in ('axial','coronal'):
                        xs = self.Im_Offset[idx,0] + np.arange(slc.shape[1]) * self.pixel_spac[idx,0]
                    else:
                        xs = self.Im_Offset[idx,1] + np.arange(slc.shape[1]) * self.pixel_spac[idx,1]

                    if ls != 'None' or marker != 'None':
                        axH.plot(xs, slc[py,:], color=color, linestyle=ls, marker=marker, markersize=ms)
                        axH.axvline(xs[col_start], color='r', linestyle='--')
                        axH.axvline(xs[col_end], color='r', linestyle='--')
                    axH.set_xlabel('X (mm)')
                    axH.set_title(horz_custom if horz_custom else f"{lbl_name} Horizontal")
                    axH.set_xlim(x_min, x_max)

        else:
            # Rectangle ROI Mode
            active_subs = [s for s in self.subs if s['idx'] in visible_layers]
            if not active_subs:
                self.canvas.draw()
                return

            slider_val_x = self.sld_x.value() if hasattr(self, 'sld_x') else self.cx_mm
            slider_val_y = self.sld_y.value() if hasattr(self, 'sld_y') else self.cy_mm

            if self.overlay_mode:
                axes = self.fig.subplots(1, 3, squeeze=False)
                axh, axv, axH = axes[0]
                axh.set_title(hist_custom if hist_custom else "Overlaid Histograms")

                for info in active_subs:
                    sub, idx, x0, y0 = info['sub'], info['idx'], info['x0'], info['y0']
                    st = self.layer_styles[idx]
                    color = st['color']
                    ls = st['linestyle']
                    ms = st['markersize']
                    marker = 'o' if ms > 0 else 'None'
                    lbl_name = st['name']

                    # Histogram
                    axh.hist(sub.ravel(), bins='auto', alpha=0.5, density=True, label=lbl_name, color=color)
                    axh.legend()

                    # Vertical profile
                    if self.avg_mode:
                        ys = self.Im_Offset[idx,2] + (y0 + np.arange(sub.shape[0])) * self.slice_thick[idx] if self.orientation != 'axial' else self.Im_Offset[idx,1] + (y0 + np.arange(sub.shape[0])) * self.pixel_spac[idx,1]
                        profile_y = np.mean(sub, axis=1)
                        title_y = vert_custom if vert_custom else "Vertical Average Profile"
                    else:
                        if self.orientation == 'sagittal':
                            gx = (slider_val_x - self.Im_Offset[idx,1]) / self.pixel_spac[idx,1]
                        else:
                            gx = (slider_val_x - self.Im_Offset[idx,0]) / self.pixel_spac[idx,0]
                        gxi = int(round(gx))
                        local_col = gxi - x0
                        if self.orientation == 'axial':
                            ys = self.Im_Offset[idx,1] + (y0 + np.arange(sub.shape[0])) * self.pixel_spac[idx,1]
                        else:
                            ys = self.Im_Offset[idx,2] + (y0 + np.arange(sub.shape[0])) * self.slice_thick[idx]
                        
                        profile_y = sub[:, local_col] if 0 <= local_col < sub.shape[1] else np.zeros_like(ys)
                        title_y = vert_custom if vert_custom else f"Vert @ X={slider_val_x} mm"

                    if ls != 'None' or marker != 'None':
                        axv.plot(ys, profile_y, color=color, linestyle=ls, marker=marker, markersize=ms, label=lbl_name)
                    axv.set_title(title_y)
                    axv.legend()

                    # Horizontal profile
                    if self.avg_mode:
                        if self.orientation in ('axial','coronal'):
                            xs = self.Im_Offset[idx,0] + (x0 + np.arange(sub.shape[1])) * self.pixel_spac[idx,0]
                        else:
                            xs = self.Im_Offset[idx,1] + (x0 + np.arange(sub.shape[1])) * self.pixel_spac[idx,1]
                        profile_x = np.mean(sub, axis=0)
                        title_x = horz_custom if horz_custom else "Horizontal Average Profile"
                    else:
                        if self.orientation == 'axial':
                            gy = (slider_val_y - self.Im_Offset[idx,1]) / self.pixel_spac[idx,1]
                        else:
                            gy = (slider_val_y - self.Im_Offset[idx,2]) / self.slice_thick[idx]
                        gyi = int(round(gy))
                        local_row = gyi - y0

                        if self.orientation in ('axial','coronal'):
                            xs = self.Im_Offset[idx,0] + (x0 + np.arange(sub.shape[1])) * self.pixel_spac[idx,0]
                        else:
                            xs = self.Im_Offset[idx,1] + (x0 + np.arange(sub.shape[1])) * self.pixel_spac[idx,1]
                        
                        profile_x = sub[local_row, :] if 0 <= local_row < sub.shape[0] else np.zeros_like(xs)
                        title_x = horz_custom if horz_custom else f"Horz @ Y={slider_val_y} mm"

                    if ls != 'None' or marker != 'None':
                        axH.plot(xs, profile_x, color=color, linestyle=ls, marker=marker, markersize=ms, label=lbl_name)
                    axH.set_title(title_x)
                    axH.legend()

            else:
                n = len(active_subs)
                axes = self.fig.subplots(n, 3, squeeze=False)

                for r, info in enumerate(active_subs):
                    sub, idx, x0, y0 = info['sub'], info['idx'], info['x0'], info['y0']
                    axh, axv, axH = axes[r]
                    st = self.layer_styles[idx]
                    color = st['color']
                    ls = st['linestyle']
                    ms = st['markersize']
                    marker = 'o' if ms > 0 else 'None'
                    lbl_name = st['name']

                    # Histogram
                    axh.hist(sub.ravel(), bins='auto', density=True, color=color)
                    axh.set_title(hist_custom if hist_custom else f"{lbl_name} Histogram")

                    # Vertical
                    if self.avg_mode:
                        ys = self.Im_Offset[idx,2] + (y0 + np.arange(sub.shape[0])) * self.slice_thick[idx] if self.orientation != 'axial' else self.Im_Offset[idx,1] + (y0 + np.arange(sub.shape[0])) * self.pixel_spac[idx,1]
                        profile_y = np.mean(sub, axis=1)
                        title_y = vert_custom if vert_custom else f"{lbl_name} Vert (Avg)"
                    else:
                        if self.orientation == 'sagittal':
                            gx = (slider_val_x - self.Im_Offset[idx,1]) / self.pixel_spac[idx,1]
                        else:
                            gx = (slider_val_x - self.Im_Offset[idx,0]) / self.pixel_spac[idx,0]
                        gxi = int(round(gx))
                        local_col = gxi - x0
                        if self.orientation == 'axial':
                            ys = self.Im_Offset[idx,1] + (y0 + np.arange(sub.shape[0])) * self.pixel_spac[idx,1]
                        else:
                            ys = self.Im_Offset[idx,2] + (y0 + np.arange(sub.shape[0])) * self.slice_thick[idx]
                        
                        profile_y = sub[:, local_col] if 0 <= local_col < sub.shape[1] else np.zeros_like(ys)
                        title_y = vert_custom if vert_custom else f"{lbl_name} Vert @ X={slider_val_x} mm"

                    if ls != 'None' or marker != 'None':
                        axv.plot(ys, profile_y, color=color, linestyle=ls, marker=marker, markersize=ms)
                    axv.set_xlabel('Y (mm)')
                    axv.set_title(title_y)

                    # Horizontal
                    if self.avg_mode:
                        if self.orientation in ('axial','coronal'):
                            xs = self.Im_Offset[idx,0] + (x0 + np.arange(sub.shape[1])) * self.pixel_spac[idx,0]
                        else:
                            xs = self.Im_Offset[idx,1] + (x0 + np.arange(sub.shape[1])) * self.pixel_spac[idx,1]
                        profile_x = np.mean(sub, axis=0)
                        title_x = horz_custom if horz_custom else f"{lbl_name} Horz (Avg)"
                    else:
                        if self.orientation == 'axial':
                            gy = (slider_val_y - self.Im_Offset[idx,1]) / self.pixel_spac[idx,1]
                        else:
                            gy = (slider_val_y - self.Im_Offset[idx,2]) / self.slice_thick[idx]
                        gyi = int(round(gy))
                        local_row = gyi - y0

                        if self.orientation in ('axial','coronal'):
                            xs = self.Im_Offset[idx,0] + (x0 + np.arange(sub.shape[1])) * self.pixel_spac[idx,0]
                        else:
                            xs = self.Im_Offset[idx,1] + (x0 + np.arange(sub.shape[1])) * self.pixel_spac[idx,1]
                        
                        profile_x = sub[local_row, :] if 0 <= local_row < sub.shape[0] else np.zeros_like(xs)
                        title_x = horz_custom if horz_custom else f"{lbl_name} Horz @ Y={slider_val_y} mm"

                    if ls != 'None' or marker != 'None':
                        axH.plot(xs, profile_x, color=color, linestyle=ls, marker=marker, markersize=ms)
                    axH.set_xlabel('X (mm)')
                    axH.set_title(title_x)

        # Style updates for dark/light matplotlib axes formatting & global font customization
        font_size = self.spin_font_size.value()
        font_color_sel = self.cmb_font_color.currentText()
        if font_color_sel == 'Default/Theme':
            color_str = 'white' if self.current_theme == 'dark' else 'black'
        else:
            color_str = font_color_sel.lower()

        for ax in self.fig.axes:
            if self.current_theme == 'dark':
                self.fig.patch.set_facecolor('#19232D')
                ax.set_facecolor('#1e2936')
                spine_color = 'white'
            else:
                self.fig.patch.set_facecolor('white')
                ax.set_facecolor('white')
                spine_color = 'black'

            # Spines styling
            ax.spines['bottom'].set_color(spine_color)
            ax.spines['top'].set_color(spine_color)
            ax.spines['left'].set_color(spine_color)
            ax.spines['right'].set_color(spine_color)

            # Font/Color updates
            ax.xaxis.label.set_size(font_size)
            ax.xaxis.label.set_color(color_str)
            ax.yaxis.label.set_size(font_size)
            ax.yaxis.label.set_color(color_str)
            ax.title.set_size(font_size)
            ax.title.set_color(color_str)
            ax.tick_params(labelsize=font_size, colors=color_str)

            # Legend custom styling
            legend = ax.get_legend()
            if legend is not None:
                legend.get_frame().set_edgecolor(spine_color)
                legend.get_frame().set_facecolor('#19232D' if self.current_theme == 'dark' else 'white')
                for text in legend.get_texts():
                    text.set_fontsize(font_size)
                    text.set_color(color_str)

        self.fig.tight_layout()
        self.canvas.draw()

    def export_csv(self):
        # 1. Ask for file name using QFileDialog
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export CSV",
            "",
            "CSV Files (*.csv)"
        )
        if not file_path:
            return

        export_matrix = False
        if self.roi_type == 'square':
            # Custom QDialog with a clean vertical layout and blue buttons to prevent text truncation
            exp_dlg = QtWidgets.QDialog(self)
            exp_dlg.setWindowTitle("Export Data Options")
            exp_layout = QtWidgets.QVBoxLayout(exp_dlg)

            lbl = QtWidgets.QLabel("Choose export type for the Rectangle ROI:")
            lbl.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
            exp_layout.addWidget(lbl)

            btn_matrix = QtWidgets.QPushButton("All Matrix Values in Rectangle")
            btn_matrix.setStyleSheet("background-color: blue; color: white; font-weight: bold; min-height: 30px; margin: 4px; border-radius: 4px; padding: 4px;")
            btn_profiles = QtWidgets.QPushButton("Displayed Line Profiles Only")
            btn_profiles.setStyleSheet("background-color: blue; color: white; font-weight: bold; min-height: 30px; margin: 4px; border-radius: 4px; padding: 4px;")
            btn_cancel = QtWidgets.QPushButton("Cancel")
            btn_cancel.setStyleSheet("background-color: #3b3b4a; color: white; min-height: 30px; margin: 4px; border-radius: 4px; padding: 4px;")

            exp_layout.addWidget(btn_matrix)
            exp_layout.addWidget(btn_profiles)
            exp_layout.addWidget(btn_cancel)

            # Container for the result
            selection = [None]

            def on_matrix():
                selection[0] = 'matrix'
                exp_dlg.accept()

            def on_profiles():
                selection[0] = 'profiles'
                exp_dlg.accept()

            def on_cancel():
                selection[0] = 'cancel'
                exp_dlg.reject()

            btn_matrix.clicked.connect(on_matrix)
            btn_profiles.clicked.connect(on_profiles)
            btn_cancel.clicked.connect(on_cancel)

            exp_dlg.exec_()

            if selection[0] == 'matrix':
                export_matrix = True
            elif selection[0] == 'profiles':
                export_matrix = False
            else:
                return

        # Prepare to export
        try:
            with open(file_path, mode='w', newline='') as f:
                writer = csv.writer(f)

                if self.roi_type == 'square' and export_matrix:
                    # Export the full matrix of values for each layer
                    for info in self.subs:
                        idx = info['idx']
                        sub = info['sub']
                        st = self.layer_styles[idx]
                        writer.writerow([st['name']])
                        for row in sub:
                            writer.writerow(row)
                        writer.writerow([])  # Line break between layers
                else:
                    # Export the profiles
                    if self.roi_type in ('circle', 'ellipse'):
                        for slc, px, py, idx, rpx, rpy in self.entries:
                            st = self.layer_styles[idx]
                            writer.writerow([st['name']])
                            
                            # Y vertical profile
                            if self.orientation == 'axial':
                                ys = self.Im_Offset[idx,1] + np.arange(slc.shape[0]) * self.pixel_spac[idx,1]
                            else:
                                ys = self.Im_Offset[idx,2] + np.arange(slc.shape[0]) * self.slice_thick[idx]
                            v_profile = slc[:, px]

                            # X horizontal profile
                            if self.orientation in ('axial','coronal'):
                                xs = self.Im_Offset[idx,0] + np.arange(slc.shape[1]) * self.pixel_spac[idx,0]
                            else:
                                xs = self.Im_Offset[idx,1] + np.arange(slc.shape[1]) * self.pixel_spac[idx,1]
                            h_profile = slc[py, :]

                            writer.writerow(["Y (mm)", "Vertical Profile Value"])
                            for y_val, v_val in zip(ys, v_profile):
                                writer.writerow([y_val, v_val])

                            writer.writerow(["X (mm)", "Horizontal Profile Value"])
                            for x_val, h_val in zip(xs, h_profile):
                                writer.writerow([x_val, h_val])
                            
                            writer.writerow([])
                    else:
                        # Rectangle profile output
                        slider_val_x = self.sld_x.value() if hasattr(self, 'sld_x') else self.cx_mm
                        slider_val_y = self.sld_y.value() if hasattr(self, 'sld_y') else self.cy_mm

                        for info in self.subs:
                            sub, idx, x0, y0 = info['sub'], info['idx'], info['x0'], info['y0']
                            st = self.layer_styles[idx]
                            writer.writerow([st['name']])

                            # Y vertical profile
                            if self.avg_mode:
                                ys = self.Im_Offset[idx,2] + (y0 + np.arange(sub.shape[0])) * self.slice_thick[idx] if self.orientation != 'axial' else self.Im_Offset[idx,1] + (y0 + np.arange(sub.shape[0])) * self.pixel_spac[idx,1]
                                v_profile = np.mean(sub, axis=1)
                            else:
                                if self.orientation == 'sagittal':
                                    gx = (slider_val_x - self.Im_Offset[idx,1]) / self.pixel_spac[idx,1]
                                else:
                                    gx = (slider_val_x - self.Im_Offset[idx,0]) / self.pixel_spac[idx,0]
                                gxi = int(round(gx))
                                local_col = gxi - x0
                                if self.orientation == 'axial':
                                    ys = self.Im_Offset[idx,1] + (y0 + np.arange(sub.shape[0])) * self.pixel_spac[idx,1]
                                else:
                                    ys = self.Im_Offset[idx,2] + (y0 + np.arange(sub.shape[0])) * self.slice_thick[idx]
                                v_profile = sub[:, local_col] if 0 <= local_col < sub.shape[1] else np.zeros_like(ys)

                            # X horizontal profile
                            if self.avg_mode:
                                if self.orientation in ('axial','coronal'):
                                    xs = self.Im_Offset[idx,0] + (x0 + np.arange(sub.shape[1])) * self.pixel_spac[idx,0]
                                else:
                                    xs = self.Im_Offset[idx,1] + (x0 + np.arange(sub.shape[1])) * self.pixel_spac[idx,1]
                                h_profile = np.mean(sub, axis=0)
                            else:
                                if self.orientation == 'axial':
                                    gy = (slider_val_y - self.Im_Offset[idx,1]) / self.pixel_spac[idx,1]
                                else:
                                    gy = (slider_val_y - self.Im_Offset[idx,2]) / self.slice_thick[idx]
                                gyi = int(round(gy))
                                local_row = gyi - y0

                                if self.orientation in ('axial','coronal'):
                                    xs = self.Im_Offset[idx,0] + (x0 + np.arange(sub.shape[1])) * self.pixel_spac[idx,0]
                                else:
                                    xs = self.Im_Offset[idx,1] + (x0 + np.arange(sub.shape[1])) * self.pixel_spac[idx,1]
                                h_profile = sub[local_row, :] if 0 <= local_row < sub.shape[0] else np.zeros_like(xs)

                            writer.writerow(["Y (mm)", "Vertical Profile Value"])
                            for y_val, v_val in zip(ys, v_profile):
                                writer.writerow([y_val, v_val])

                            writer.writerow(["X (mm)", "Horizontal Profile Value"])
                            for x_val, h_val in zip(xs, h_profile):
                                writer.writerow([x_val, h_val])
                            
                            writer.writerow([])

            QtWidgets.QMessageBox.information(self, "Export Success", f"Successfully exported data to:\n{file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Export Error", f"Failed to save CSV file:\n{e}")


def show_roi_plots(
    parent: QtWidgets.QWidget,
    display_data: dict,
    Im_Offset: np.ndarray,
    pixel_spac: np.ndarray,
    slice_thick: np.ndarray,
    orientation: str,
    center: tuple,
    radii: tuple,
    roi_type: str = 'circle',
    window_title: str = 'ROI Analysis',
    return_dialog: bool = False
):
    """
    Shows the enhanced custom QDialog containing the interactive analysis canvas
    """
    dlg = ROIDialog(
        parent=parent,
        display_data=display_data,
        Im_Offset=Im_Offset,
        pixel_spac=pixel_spac,
        slice_thick=slice_thick,
        orientation=orientation,
        center=center,
        radii=radii,
        roi_type=roi_type,
        window_title=window_title
    )

    if return_dialog:
        return dlg

    dlg.exec_()
    return None
