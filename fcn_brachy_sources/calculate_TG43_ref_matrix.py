from PySide6.QtWidgets import  QMessageBox
import os
import numpy as np
import pandas as pd

def calculate_dose_reference_matrix(self):
    """
    Builds a full 3D TG-43 dose reference volume over [-S,S] mm at Res-mm spacing by:
      1. Computing a 2D meridian map D_mer[z, x] in the X-Z plane (Y=0) - vectorized
      2. Filling zeros along the central axis (angles 0 & 180) by neighbor averaging
      3. Revolving that meridian around the Z axis using linear interpolation
    Stores result in self.TG43.activesource.DoseMatrix (cGy/h) as float32.
    """
    from scipy.interpolate import RegularGridInterpolator
    from PySide6.QtWidgets import QMessageBox

    src = self.TG43.activesource

    # 1) Read UI parameters and sync to model
    try:
        Λ    = float(self.Brachy_dose_rate_cte_value.text().strip())         # cGy/h/U
        L_mm = float(self.Brachy_rad_leng.text().strip())                    # mm
        Res  = float(self.Tg43_dose_grid.currentText().strip())              # mm per voxel
        S    = float(self.Tg43_matrix_size_2.currentText().split('x',1)[0])  # mm half-span
    except Exception as e:
        QMessageBox.critical(self, "Input Error", f"Invalid TG-43 inputs:{e}")
        return

    # Cap reference matrix to max 401 voxels per axis to prevent memory issues
    max_voxels = 401
    n_check = int(2 * S / Res) + 1
    if n_check > max_voxels:
        S = (max_voxels - 1) * Res / 2.0

    src.DoseMatrix_res_mm = Res
    src.DoseMatrix_size   = S
    # Set the progress bar value
    self.progressBar.setValue(10)

    # 2) Unpack polynomial fit and anisotropy
    coeffs    = src.radial_fit                 # 5th-degree poly
    ani       = src.anisotropy
    dist_cm   = ani[0,1:]                      # distances (cm)
    ang_deg   = ani[1:,0]                      # angles (deg)
    F_data    = np.nan_to_num(ani[1:,1:], nan=0.0)
    # Set the progress bar value
    self.progressBar.setValue(20)

    # 3) Geometry factor reference value: G_line at r=1 cm, θ=90°
    L_cm = L_mm / 10.0
    G_ref = 2.0 * np.arctan2(L_cm / 2.0, 1.0) / L_cm
    # Set the progress bar value
    self.progressBar.setValue(30)

    # 4) Build 1D axes for meridian plane
    n = int(2 * S / Res) + 1
    xs = np.linspace(-S, S, n)
    zs = np.linspace(-S, S, n)
    nx, nz = xs.size, zs.size
    center_x = nx // 2
    # Set the progress bar value
    self.progressBar.setValue(40)

    # 5) Compute 2D meridian dose map D_mer[z, x] — fully vectorized
    Z_mm, X_mm = np.meshgrid(zs, xs, indexing='ij')  # shape (nz, nx)
    R_mm = np.hypot(X_mm, Z_mm)
    R_cm = R_mm / 10.0

    valid = R_cm > 1e-10
    Theta = np.zeros_like(R_cm)
    Theta[valid] = np.arccos(np.clip(Z_mm[valid] / R_mm[valid], -1.0, 1.0))

    # Vectorized geometry factor G_line(r, θ, L_cm)
    G = np.zeros_like(R_cm)
    r_v = R_cm[valid]
    sin_t = np.sin(Theta[valid])
    cos_t = np.cos(Theta[valid])
    on_axis = np.abs(sin_t) < 1e-8
    off_axis = ~on_axis
    G_v = np.zeros(r_v.size, dtype=np.float64)

    if on_axis.any():
        d = r_v[on_axis]**2 - (L_cm / 2.0)**2
        G_v[on_axis] = np.where(d > 0, 1.0 / d, 0.0)

    if off_axis.any():
        rho = r_v[off_axis] * sin_t[off_axis]
        z_off = r_v[off_axis] * cos_t[off_axis]
        a1 = np.arctan2((L_cm / 2.0) - z_off, rho)
        a2 = np.arctan2((L_cm / 2.0) + z_off, rho)
        G_v[off_axis] = (a1 + a2) / (L_cm * rho)

    G[valid] = G_v
    # Set the progress bar value
    self.progressBar.setValue(50)

    # Radial dose function g(r)
    g = np.ones_like(R_cm)
    far = valid & (R_cm >= dist_cm[0])
    g[far] = np.maximum(0.0, np.polyval(coeffs, R_cm[far]))

    # Anisotropy function F(r, θ) — bilinear interpolation on (angle, distance) grid
    F_all = np.zeros_like(R_cm)
    if valid.any():
        deg_v = np.clip(np.degrees(Theta[valid]), float(ang_deg[0]), float(ang_deg[-1]))
        r_v_clamped = np.clip(R_cm[valid], float(dist_cm[0]), float(dist_cm[-1]))
        F_interp = RegularGridInterpolator(
            (ang_deg.astype(np.float64), dist_cm.astype(np.float64)),
            F_data.astype(np.float64),
            method='linear', bounds_error=False, fill_value=None
        )
        pts = np.column_stack([deg_v.ravel(), r_v_clamped.ravel()])
        F_all[valid] = F_interp(pts)

    # Final meridian dose map
    D_mer = np.where(valid, Λ * (G / G_ref) * g * F_all, 0.0)
    # Set the progress bar value
    self.progressBar.setValue(60)

    # 6) Replace zeros along the central axis by 1-D neighbor averaging
    #
    center_x = nx // 2

    for iz in range(nz):
        # if this central voxel is zero…
        if D_mer[iz, center_x] == 0.0:
            # grab its left/right neighbors (or 0 if out of bounds)
            left_val  = D_mer[iz, center_x - 1] if center_x > 0     else 0.0
            right_val = D_mer[iz, center_x + 1] if center_x < nx-1 else 0.0

            # pick a positive neighbor (or average them)
            if left_val > 0 and right_val > 0:
                D_mer[iz, center_x] = 0.5 * (left_val + right_val)
            elif left_val > 0:
                D_mer[iz, center_x] = left_val
            elif right_val > 0:
                D_mer[iz, center_x] = right_val
            # otherwise leave it at zero
    # Set the progress bar value
    self.progressBar.setValue(70)

    # 7) Revolve meridian into full 3D volume using linear interpolation
    ys = xs.copy()
    ny = ys.size
    Dose3D = np.zeros((nz, ny, nx), dtype=np.float32)
    Xg, Yg = np.meshgrid(xs, ys, indexing='xy')
    Rg = np.hypot(Xg, Yg)

    # Use positive half of meridian for smooth radial interpolation
    x_positive = xs[center_x:]  # [0, Res, 2*Res, ..., S]
    Rg_flat = Rg.ravel()

    for iz in range(nz):
        meridian_half = D_mer[iz, center_x:]
        Dose3D[iz] = np.interp(Rg_flat, x_positive, meridian_half).reshape(ny, nx)
    # Set the progress bar value
    self.progressBar.setValue(90)

    # 8) Store result and update along-away
    src.DoseMatrix = Dose3D

    # Optionally recalc along-away from central slice
    calculate_along_away_reference_calc(self)
    # Set the progress bar value
    self.progressBar.setValue(100)



def calculate_along_away_reference_calc(self):
    """
    Samples the 3D DoseMatrix at along/away reference points using direct voxel lookup.
    """
    import numpy as np

    src   = self.TG43.activesource
    ref   = src.along_away_reference        # shape (M+1, N+1)
    Dose3 = src.DoseMatrix                  # shape (nz, ny, nx)
    Res   = src.DoseMatrix_res_mm           # mm/voxel
    S     = src.DoseMatrix_size             # mm half-span

    nz, ny, nx = Dose3.shape

    # center indices for each axis
    cz = nz // 2
    cy = ny // 2
    cx = nx // 2

    # Prepare output
    calc = np.empty_like(ref, dtype=float)
    calc[0, 0]   = ref[0, 0]
    calc[0, 1:]  = ref[0, 1:]
    calc[1:, 0]  = ref[1:, 0]

    # Convert reference distances (cm → mm)
    along_mm = ref[1:, 0] * 10.0
    away_mm  = ref[0, 1:] * 10.0

    # Loop over each table cell
    for i, z_mm in enumerate(along_mm, start=1):
        z_idx = int(round(z_mm / Res)) + cz
        for j, r_mm in enumerate(away_mm, start=1):
            x_idx = cx + int(round(r_mm / Res))
            # if indices in range, sample; else NaN
            if 0 <= z_idx < nz and 0 <= cy < ny and 0 <= x_idx < nx:
                calc[i, j] = Dose3[z_idx, cy, x_idx]
            else:
                calc[i, j] = np.nan

    # Flip rows (so along=0 appears at top or bottom as desired)
    calc[1:, :] = calc[1:, :][::-1, :]

    # Store back
    src.along_away_reference_calc = calc
