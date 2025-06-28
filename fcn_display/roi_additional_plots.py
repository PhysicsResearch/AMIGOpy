# fcn_display/roi_additional_plots.py
from PyQt5 import QtWidgets, QtCore
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
import vtk

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
    window_title: str = 'ROI Analysis'
):
    """
    Pops up a Qt dialog with Matplotlib plots:
     - circle/ellipse → N rows × 3 cols (histogram, vertical+bounds, horizontal+bounds)
     - square (rectangle) → N rows × 4 cols + sliders over ROI-local indices
    """
    cx_mm, cy_mm, _ = center

    # lists to collect per-layer ROI data
    entries = []  # for circle/ellipse
    subs    = []  # for rectangle

    # half-widths in mm (for rectangle mode only)
    if roi_type == 'square':
        rx_mm, ry_mm = radii

    # -- collect ROI on each layer --
    for idx, data in display_data.items():
        if data is None or not hasattr(data, 'ndim'):
            continue

        ### 1) extract the 2D slice ###
        try:
            if data.ndim == 2:
                slc = data
            elif orientation == 'axial':
                slc = data[parent.current_axial_slice_index[idx]]
            elif orientation == 'coronal':
                slc = data[:, parent.current_coronal_slice_index[idx]]
            else:  # sagittal
                slc = data[:, :, parent.current_sagittal_slice_index[idx]]
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                parent, "ROI Plot Error",
                f"Layer {idx}: cannot extract slice ({e})."
            )
            return

        h, w = slc.shape

        ### 2) map world‐center → pixel (px,py) ###
        if orientation == 'axial':
            px = (cx_mm - Im_Offset[idx,0]) / pixel_spac[idx,0]
            py = (cy_mm - Im_Offset[idx,1]) / pixel_spac[idx,1]
        elif orientation == 'coronal':
            px = (cx_mm - Im_Offset[idx,0]) / pixel_spac[idx,0]
            py = (cy_mm - Im_Offset[idx,2]) / slice_thick[idx]
        else:  # sagittal
            px = (cx_mm - Im_Offset[idx,1]) / pixel_spac[idx,1]
            py = (cy_mm - Im_Offset[idx,2]) / slice_thick[idx]

        px, py = int(round(px)), int(round(py))
        px = np.clip(px, 0, w-1)
        py = np.clip(py, 0, h-1)

        if roi_type in ('circle','ellipse'):
            ### 3a) circle/ellipse → store for later plotting ###
            rx_mm, ry_mm = radii
            if orientation == 'axial':
                rpx = int(round(rx_mm / pixel_spac[idx,0]))
                rpy = int(round(ry_mm / pixel_spac[idx,1]))
            elif orientation == 'coronal':
                rpx = int(round(rx_mm / pixel_spac[idx,0]))
                rpy = int(round(ry_mm / slice_thick[idx]))
            else:
                rpx = int(round(rx_mm / pixel_spac[idx,1]))
                rpy = int(round(ry_mm / slice_thick[idx]))
            entries.append((slc, px, py, idx, rpx, rpy))

        else:
            ### 3b) rectangle → mask out a sub-array ###
            # compute rpx,rpy in pixels exactly like circle’s radii:
            if orientation == 'axial':
                rpx = int(round(rx_mm / pixel_spac[idx,0]))
                rpy = int(round(ry_mm / pixel_spac[idx,1]))
            elif orientation == 'coronal':
                rpx = int(round(rx_mm / pixel_spac[idx,0]))
                rpy = int(round(ry_mm / slice_thick[idx]))
            else:  # sagittal
                rpx = int(round(rx_mm / pixel_spac[idx,1]))
                rpy = int(round(ry_mm / slice_thick[idx]))

            # mask + bounding box
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
                subs.append({'idx': idx, 'sub': sub, 'x0': x0, 'y0': y0})

    # no data guard
    if roi_type in ('circle','ellipse') and not entries:
        QtWidgets.QMessageBox.information(parent, window_title, "No data in ROI.")
        return
    if roi_type == 'square' and not subs:
        QtWidgets.QMessageBox.information(parent, window_title, "ROI does not overlap any layer.")
        return

    # -- create the dialog & figure --
    dlg = QtWidgets.QDialog(parent)
    dlg.setWindowTitle(window_title)
    dlg.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    dlg.resize(1200, 800)
    dlg.setMinimumSize(800, 600)

    if roi_type in ('circle','ellipse'):
        # N × 3 layout
        n = len(entries)
        fig, axes = plt.subplots(n, 3, figsize=(12, 4*n), squeeze=False)
        for r,(slc,px,py,idx,rpx,rpy) in enumerate(entries):
            axh, axv, axH = axes[r]
            # histogram
            yy,xx = np.ogrid[:slc.shape[0], :slc.shape[1]]
            mask = ((xx-px)**2)/(rpx**2) + ((yy-py)**2)/(rpy**2) <= 1
            axh.hist(slc[mask].ravel(), bins='auto')
            axh.set_title(f"Layer {idx} Histogram")
            # vertical
            vert = slc[:,px]
            axv.plot(vert)
            axv.axvline(py-rpy, color='r', linestyle='--')
            axv.axvline(py+rpy, color='r', linestyle='--')
            axv.set_title(f"Layer {idx} Vertical (col={px})")
            # horizontal
            horz = slc[py,:]
            axH.plot(horz)
            axH.axvline(px-rpx, color='r', linestyle='--')
            axH.axvline(px+rpx, color='r', linestyle='--')
            axH.set_title(f"Layer {idx} Horizontal (row={py})")

    else:
        # rectangle mode: N × 4
        n = len(subs)
        fig, axes = plt.subplots(n, 4, figsize=(16, 4*n), squeeze=False)
        # determine common local dims for slider ranges
        common_w = min(info['sub'].shape[1] for info in subs)
        common_h = min(info['sub'].shape[0] for info in subs)
        col0, row0 = common_w//2, common_h//2

        for r,info in enumerate(subs):
            sub, idx = info['sub'], info['idx']
            ax0, ax1, ax2, ax3 = axes[r]
            # histogram
            ax0.hist(sub.ravel(), bins='auto', alpha=0.7)
            ax0.set_title(f"Layer {idx} Histogram")
            # mean rows/cols
            mr, mc = sub.mean(axis=1), sub.mean(axis=0)
            ax1.plot(mr, label='Row mean')
            ax1.plot(mc, label='Col mean')
            ax1.legend()
            ax1.set_title(f"Layer {idx} Mean")
            # center vertical
            ax2.plot(sub[:, col0])
            ax2.set_title(f"Layer {idx} Vert idx={col0}")
            # center horizontal
            ax3.plot(sub[row0, :])
            ax3.set_title(f"Layer {idx} Horz idx={row0}")

    # embed
    canvas = FigureCanvas(fig)
    toolbar = NavigationToolbar(canvas, dlg)
    vlay = QtWidgets.QVBoxLayout(dlg)
    vlay.addWidget(toolbar)
    vlay.addWidget(canvas)

    # ─── sliders for rectangle mode ────────────────────────────────
    if roi_type == 'square':
        # compute combined world extents in X and Y
        world_x0, world_x1, world_y0, world_y1 = [], [], [], []
        for info in subs:
            idx, sub, x0, y0 = info['idx'], info['sub'], info['x0'], info['y0']
            # world X extents from global pixel x0…x0+width-1
            wx0 = Im_Offset[idx,0] + x0 * pixel_spac[idx,0]
            wx1 = Im_Offset[idx,0] + (x0 + sub.shape[1] - 1) * pixel_spac[idx,0]
            world_x0.append(wx0); world_x1.append(wx1)
            # world Y extents differ by orientation
            if orientation == 'axial':
                wy0 = Im_Offset[idx,1] + y0 * pixel_spac[idx,1]
                wy1 = Im_Offset[idx,1] + (y0 + sub.shape[0] - 1) * pixel_spac[idx,1]
            else:  # coronal or sagittal, Y ↔ slice_thick
                wy0 = Im_Offset[idx,2] + y0 * slice_thick[idx]
                wy1 = Im_Offset[idx,2] + (y0 + sub.shape[0] - 1) * slice_thick[idx]
            world_y0.append(wy0); world_y1.append(wy1)

        col_min = int(np.floor(min(world_x0))); col_max = int(np.ceil(max(world_x1)))
        row_min = int(np.floor(min(world_y0))); row_max = int(np.ceil(max(world_y1)))

        hbox = QtWidgets.QHBoxLayout()

        # — X slider (world mm) —
        sld_x = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sld_x.setRange(col_min, col_max)
        init_x = int(round(cx_mm))
        sld_x.setValue(init_x)
        lbl_x = QtWidgets.QLabel(f"X={init_x} mm")
        def on_x(val):
            lbl_x.setText(f"X={val} mm")
            for r, info in enumerate(subs):
                idx, sub, x0 = info['idx'], info['sub'], info['x0']
                # global pixel = (world – offset) / spacing
                gx = (val - Im_Offset[idx,0]) / pixel_spac[idx,0]
                local_col = int(round(gx)) - x0
                ax = axes[r][2]
                ax.clear()
                if 0 <= local_col < sub.shape[1]:
                    ax.plot(sub[:, local_col])
                ax.set_title(f"Layer {idx} Vert @ X={val} mm")
            canvas.draw()
        sld_x.valueChanged.connect(on_x)

        # — Y slider (world mm) —
        sld_y = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sld_y.setRange(row_min, row_max)
        init_y = int(round(cy_mm))
        sld_y.setValue(init_y)
        lbl_y = QtWidgets.QLabel(f"Y={init_y} mm")
        def on_y(val):
            lbl_y.setText(f"Y={val} mm")
            for r, info in enumerate(subs):
                idx, sub, y0 = info['idx'], info['sub'], info['y0']
                if orientation == 'axial':
                    gy = (val - Im_Offset[idx,1]) / pixel_spac[idx,1]
                else:
                    gy = (val - Im_Offset[idx,2]) / slice_thick[idx]
                local_row = int(round(gy)) - y0
                ax = axes[r][3]
                ax.clear()
                if 0 <= local_row < sub.shape[0]:
                    ax.plot(sub[local_row, :])
                ax.set_title(f"Layer {idx} Horz @ Y={val} mm")
            canvas.draw()
        sld_y.valueChanged.connect(on_y)

        # lay out
        col_box = QtWidgets.QVBoxLayout(); col_box.addWidget(lbl_x); col_box.addWidget(sld_x)
        row_box = QtWidgets.QVBoxLayout(); row_box.addWidget(lbl_y); row_box.addWidget(sld_y)
        hbox.addLayout(col_box); hbox.addLayout(row_box)
        vlay.addLayout(hbox)

    dlg.exec_()
