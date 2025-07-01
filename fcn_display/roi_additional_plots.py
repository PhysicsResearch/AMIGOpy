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
     - square (rectangle)   → N rows × 4 cols + sliders over ROI-local indices
    """
    cx_mm, cy_mm, _ = center

    # lists to collect per-layer ROI data
    entries = []  # for circle/ellipse
    subs    = []  # for rectangle

    # half-widths in mm (for rectangle mode only)
    if roi_type == 'square':
        rx_mm, ry_mm = radii

    # — collect ROI on each layer —
    for idx, data in display_data.items():
        if data is None or not hasattr(data, 'ndim'):
            continue

        # 1) extract the 2D slice
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

        # 2) map world-center → pixel (px,py)
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
            # 3a) circle/ellipse → store for later plotting
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
            # 3b) rectangle → mask out a sub-array
            if orientation == 'axial':
                rpx = int(round(rx_mm / pixel_spac[idx,0]))
                rpy = int(round(ry_mm / pixel_spac[idx,1]))
            elif orientation == 'coronal':
                rpx = int(round(rx_mm / pixel_spac[idx,0]))
                rpy = int(round(ry_mm / slice_thick[idx]))
            else:  # sagittal
                rpx = int(round(rx_mm / pixel_spac[idx,1]))
                rpy = int(round(ry_mm / slice_thick[idx]))

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

    # guard no-data cases
    if roi_type in ('circle','ellipse') and not entries:
        QtWidgets.QMessageBox.information(parent, window_title, "No data in ROI.")
        return
    if roi_type == 'square' and not subs:
        QtWidgets.QMessageBox.information(parent, window_title, "ROI does not overlap any layer.")
        return

    # — create dialog & figure —
    dlg = QtWidgets.QDialog(parent)
    dlg.setWindowTitle(window_title)
    dlg.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    dlg.resize(1200, 800)
    dlg.setMinimumSize(800, 600)

    if roi_type in ('circle','ellipse'):
        # N × 3 layout
        n = len(entries)
        fig, axes = plt.subplots(n, 3, figsize=(12, 4*n), squeeze=False)

        # --- NEW: compute global profile limits across all layers ---
        # for vertical profiles (Y axis)
        all_ys = []
        # for horizontal profiles (X axis)
        all_xs = []
        for slc, px, py, idx, rpx, rpy in entries:
            # build full-world Y
            if orientation == 'axial':
                y_world = Im_Offset[idx,1] + np.arange(slc.shape[0]) * pixel_spac[idx,1]
            else:
                y_world = Im_Offset[idx,2] + np.arange(slc.shape[0]) * slice_thick[idx]
            all_ys.append((y_world.min(), y_world.max()))
            # build full-world X
            if orientation in ('axial','coronal'):
                x_world = Im_Offset[idx,0] + np.arange(slc.shape[1]) * pixel_spac[idx,0]
            else:
                x_world = Im_Offset[idx,1] + np.arange(slc.shape[1]) * pixel_spac[idx,1]
            all_xs.append((x_world.min(), x_world.max()))

        # global min/max
        y_min, y_max = min(y0 for y0,y1 in all_ys), max(y1 for y0,y1 in all_ys)
        x_min, x_max = min(x0 for x0,x1 in all_xs), max(x1 for x0,x1 in all_xs)
        # ------------------------------------------------------------

        for r,(slc,px,py,idx,rpx,rpy) in enumerate(entries):
            axh, axv, axH = axes[r]
            # histogram
            yy,xx = np.ogrid[:slc.shape[0], :slc.shape[1]]
            mask = ((xx-px)**2)/(rpx**2) + ((yy-py)**2)/(rpy**2) <= 1
            axh.hist(slc[mask].ravel(), bins='auto', density=True)
            axh.set_title(f"Layer {idx} Histogram")
            # vertical profile in absolute Y
            row_start = max(0, py-rpy)
            row_end   = min(slc.shape[0]-1, py+rpy)
            if orientation=='axial':
                ys = Im_Offset[idx,1] + np.arange(slc.shape[0]) * pixel_spac[idx,1]
            else:
                ys = Im_Offset[idx,2] + np.arange(slc.shape[0]) * slice_thick[idx]
            axv.plot(ys, slc[:,px])
            axv.axvline(ys[row_start], color='r', linestyle='--')
            axv.axvline(ys[row_end],   color='r', linestyle='--')
            axv.set_xlabel('Y (mm)')
            axv.set_title(f"Vertical (col={py})")
            axv.set_xlim(y_min, y_max)
            # 
            # horizontal profile in absolute X
            col_start = max(0, px-rpx)
            col_end   = min(slc.shape[1]-1, px+rpx)
            if orientation in ('axial','coronal'):
                xs = Im_Offset[idx,0] + np.arange(slc.shape[1]) * pixel_spac[idx,0]
            else:
                xs = Im_Offset[idx,1] + np.arange(slc.shape[1]) * pixel_spac[idx,1]
            axH.plot(xs, slc[py,:])
            axH.axvline(xs[col_start], color='r', linestyle='--')
            axH.axvline(xs[col_end],   color='r', linestyle='--')
            axH.set_xlabel('X (mm)')
            axH.set_title(f"Horizontal (row={py})")
            axH.set_xlim(x_min, x_max)

        # ─── embed canvas & toolbar ─────────────────────────────
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, dlg)
        vlay = QtWidgets.QVBoxLayout(dlg)
        vlay.addWidget(toolbar)
        vlay.addWidget(canvas)

    else:
        # rectangle mode: N × 3 (hist, vert, horz)
        n = len(subs)
        fig, axes = plt.subplots(n, 3, figsize=(15, 4*n), squeeze=False)

        # draw each row: histogram, vertical, horizontal
        for r, info in enumerate(subs):
            sub, idx = info['sub'], info['idx']
            x0, y0 = info['x0'], info['y0']
            axh, axv, axH = axes[r]

            # 1) normalized histogram
            axh.hist(sub.ravel(), bins='auto', density=True)
            axh.set_title(f"Layer {idx} Histogram")

            # 2) central vertical profile
            col0 = sub.shape[1] // 2
            if orientation == 'axial':
                xs0 = Im_Offset[idx,0] + (x0 + col0) * pixel_spac[idx,0]
                ys = Im_Offset[idx,1] + (y0 + np.arange(sub.shape[0])) * pixel_spac[idx,1]
            elif orientation == 'coronal':
                xs0 = Im_Offset[idx,0] + (x0 + col0) * pixel_spac[idx,0]
                ys = Im_Offset[idx,2] + (y0 + np.arange(sub.shape[0])) * slice_thick[idx]
            else:  # sagittal
                xs0 = Im_Offset[idx,1] + (x0 + col0) * pixel_spac[idx,1]
                ys = Im_Offset[idx,2] + (y0 + np.arange(sub.shape[0])) * slice_thick[idx]

            axv.plot(ys, sub[:, col0])
            axv.set_xlabel('Y (mm)')
            axv.set_title(f"Vert @ X={xs0:.1f} mm")

            # 3) central horizontal profile
            row0 = sub.shape[0] // 2
            if orientation in ('axial','coronal'):
                xs = Im_Offset[idx,0] + (x0 + np.arange(sub.shape[1])) * pixel_spac[idx,0]
            else:
                xs = Im_Offset[idx,1] + (x0 + np.arange(sub.shape[1])) * pixel_spac[idx,1]
            axH.plot(xs, sub[row0, :])
            axH.set_xlabel('X (mm)')
            axH.set_title(f"Horz @ Y={ys[row0]:.1f} mm")

        # ─── embed canvas & toolbar ─────────────────────────────
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, dlg)
        vlay = QtWidgets.QVBoxLayout(dlg)     # <— make sure to create this!
        vlay.addWidget(toolbar)
        vlay.addWidget(canvas)

        # ─── sliders for rectangle mode ───────────────────────────
        # compute world extents just as before...
        world_x0, world_x1, world_y0, world_y1 = [], [], [], []
        for info in subs:
            idx, sub, x0, y0 = info['idx'], info['sub'], info['x0'], info['y0']
            # X extents in mm
            if orientation == 'axial':
                wx = Im_Offset[idx,0]
                world_x0.append(wx + x0 * pixel_spac[idx,0])
                world_x1.append(wx + (x0 + sub.shape[1] - 1) * pixel_spac[idx,0])
            elif orientation == 'sagittal':
                wy = Im_Offset[idx,1]
                world_x0.append(wy + x0 * pixel_spac[idx,1])
                world_x1.append(wy + (x0 + sub.shape[1] - 1) * pixel_spac[idx,1])
            else:  # coronal
                wx = Im_Offset[idx,0]
                world_x0.append(wx + x0 * pixel_spac[idx,0])
                world_x1.append(wx + (x0 + sub.shape[1] - 1) * pixel_spac[idx,0])

            # Y extents in mm
            if orientation == 'axial':
                wy = Im_Offset[idx,1]
                world_y0.append(wy + y0 * pixel_spac[idx,1])
                world_y1.append(wy + (y0 + sub.shape[0] - 1) * pixel_spac[idx,1])
            else:
                wz = Im_Offset[idx,2]
                world_y0.append(wz + y0 * slice_thick[idx])
                world_y1.append(wz + (y0 + sub.shape[0] - 1) * slice_thick[idx])

        col_min = int(np.floor(min(world_x0))); col_max = int(np.ceil(max(world_x1)))
        row_min = int(np.floor(min(world_y0))); row_max = int(np.ceil(max(world_y1)))

        hbox = QtWidgets.QHBoxLayout()

        # X slider
        sld_x = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sld_x.setRange(col_min, col_max)
        sld_x.setValue(int(round(cx_mm)))
        lbl_x = QtWidgets.QLabel(f"X={cx_mm:.1f} mm")
        def on_x(val):
            lbl_x.setText(f"X={val} mm")
            for r, info in enumerate(subs):
                idx, sub, x0, y0 = (
                    info['idx'],
                    info['sub'],
                    info['x0'],
                    info['y0'],   # <— pull y0 here
                )
                if orientation == 'sagittal':
                    gx = (val - Im_Offset[idx,1]) / pixel_spac[idx,1]
                else:
                    gx = (val - Im_Offset[idx,0]) / pixel_spac[idx,0]
                gxi = int(round(gx)); local_col = gxi - x0

                # recalc Y axis for this SAME layer
                if orientation == 'axial':
                    ys = Im_Offset[idx,1] + (y0 + np.arange(sub.shape[0])) * pixel_spac[idx,1]
                else:
                    ys = Im_Offset[idx,2] + (y0 + np.arange(sub.shape[0])) * slice_thick[idx]

                axv = axes[r][1]
                axv.clear()
                if 0 <= local_col < sub.shape[1]:
                    axv.plot(ys, sub[:, local_col])
                axv.set_title(f"Vert @ X={val} mm")
            canvas.draw()
        sld_x.valueChanged.connect(on_x)

        # Y slider
        sld_y = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sld_y.setRange(row_min, row_max)
        sld_y.setValue(int(round(cy_mm)))
        lbl_y = QtWidgets.QLabel(f"Y={cy_mm:.1f} mm")
        def on_y(val):
            lbl_y.setText(f"Y={val} mm")
            for r, info in enumerate(subs):
                idx, sub, x0, y0 = (
                   info['idx'],
                   info['sub'],
                   info['x0'],   # <— grab x0 here too
                   info['y0'],
                )
                if orientation == 'axial':
                    gy = (val - Im_Offset[idx,1]) / pixel_spac[idx,1]
                else:
                    gy = (val - Im_Offset[idx,2]) / slice_thick[idx]
                gyi = int(round(gy)); local_row = gyi - y0

                # now x0 refers to THIS layer’s column offset
                if orientation in ('axial','coronal'):
                    xs = Im_Offset[idx,0] + (x0 + np.arange(sub.shape[1])) * pixel_spac[idx,0]
                else:
                    xs = Im_Offset[idx,1] + (x0 + np.arange(sub.shape[1])) * pixel_spac[idx,1]

                axH = axes[r][2]
                axH.clear()
                if 0 <= local_row < sub.shape[0]:
                    axH.plot(xs, sub[local_row, :])
                axH.set_title(f"Horz @ Y={val} mm")
            canvas.draw()
        sld_y.valueChanged.connect(on_y)

        col_box = QtWidgets.QVBoxLayout(); col_box.addWidget(lbl_x); col_box.addWidget(sld_x)
        row_box = QtWidgets.QVBoxLayout(); row_box.addWidget(lbl_y); row_box.addWidget(sld_y)
        hbox.addLayout(col_box); hbox.addLayout(row_box)
        vlay.addLayout(hbox)

    dlg.exec_()
