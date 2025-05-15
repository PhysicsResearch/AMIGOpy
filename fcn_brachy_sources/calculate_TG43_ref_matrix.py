from PyQt5.QtWidgets import  QMessageBox
import os
import numpy as np
import pandas as pd

def calculate_dose_reference_matrix(self):
    """
    Builds a full 3D TG-43 dose reference volume over [-S,S] mm at Res-mm spacing by:
      1. Computing a 2D meridian map D_mer[z, x] in the X–Z plane (Y=0)
      2. Filling zeros along the central axis (angles 0 & 180) by neighbor averaging
      3. Revolving that meridian around the Z axis to create the full [Z,Y,X] grid
    If S=200 mm and Res=1 mm, produces a 401×401×401 array.
    Stores result in self.TG43.activesource.DoseMatrix (cGy/h).
    """
    import numpy as np
    from PyQt5.QtWidgets import QMessageBox

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

    # 3) Geometry factor
    def G_line(r, θ, L_cm):
        if abs(np.sin(θ)) < 1e-8:
            d = r*r - (L_cm/2)**2
            return 1.0/d if d>0 else 0.0
        ρ = r*np.sin(θ)
        z = r*np.cos(θ)
        a1 = np.arctan2((L_cm/2)-z, ρ)
        a2 = np.arctan2((L_cm/2)+z, ρ)
        return (a1 + a2) / (L_cm * ρ)
    L_cm = L_mm / 10.0
    G_ref = G_line(1.0, np.deg2rad(90.0), L_cm)
    # Set the progress bar value
    self.progressBar.setValue(30)

    # 4) Build 1D axes for meridian plane
    xs = np.linspace(-S, S, int(2*S/Res)+1)  # X in mm
    zs = np.linspace(-S, S, int(2*S/Res)+1)  # Z in mm
    nx, nz = xs.size, zs.size
    # Set the progress bar value
    self.progressBar.setValue(60)
    # 5) Compute 2D meridian dose map D_mer[z, x]
    D_mer = np.zeros((nz, nx), dtype=float)
    for iz, z_mm in enumerate(zs):
        for ix, x_mm in enumerate(xs):
            r_cm = np.hypot(x_mm, z_mm)/10.0
            if r_cm == 0:
                continue
            θ = np.arccos(z_mm/(r_cm*10.0))
            G = G_line(r_cm, θ, L_cm)
            g = 1.0 if r_cm < dist_cm[0] else max(0.0, np.polyval(coeffs, r_cm))

            deg = np.degrees(θ)
            ai  = np.clip(np.searchsorted(ang_deg, deg), 1, len(ang_deg)-1)
            a0, a1 = ai-1, ai
            w = 0.0 if ang_deg[a1]==ang_deg[a0] else (deg-ang_deg[a0])/(ang_deg[a1]-ang_deg[a0])
            if r_cm <= dist_cm[0]:
                F0, F1 = F_data[a0,0], F_data[a1,0]
            else:
                F0 = np.interp(r_cm, dist_cm, F_data[a0], left=F_data[a0,0])
                F1 = np.interp(r_cm, dist_cm, F_data[a1], left=F_data[a1,0])
            F = F0*(1-w) + F1*w

            D_mer[iz, ix] = Λ * (G/G_ref) * g * F
    # Set the progress bar value
    self.progressBar.setValue(80)
    # 6) Replace *all* zeros along the central axis by 1-D interpolation
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
    self.progressBar.setValue(90)

    # 7) Revolve meridian into full 3D volume
    ys = xs.copy()
    ny = ys.size
    Dose3D = np.zeros((nz, ny, nx), dtype=float)
    Xg, Yg = np.meshgrid(xs, ys, indexing='xy')
    Rg = np.hypot(Xg, Yg)
    k = np.rint(Rg/Res).astype(int)
    idx = center_x + k
    np.clip(idx, 0, nx-1, out=idx)
    for iz in range(nz):
        Dose3D[iz] = D_mer[iz, idx]

    # 8) Store result and update along-away
    src.DoseMatrix = Dose3D

    # # 1) grab the 3D array and axes info
    # dose3d = src.DoseMatrix                      # shape (nz, ny, nx)
    # nz, ny, nx = dose3d.shape
    # Res = src.DoseMatrix_res_mm                   # mm
    # S   = src.DoseMatrix_size                     # mm half-span

    # # 2) central-slice index (Z-axis)
    # zc = nz // 2
    # slice2d = dose3d[:, zc, :]                    # shape (ny, nx)

    # # 3) build real-world axes in cm
    # xs_mm = np.linspace(-S, S, nx)
    # ys_mm = np.linspace(-S, S, ny)
    # xs_cm = xs_mm / 10.0
    # ys_cm = ys_mm / 10.0
    # # 4) make a DataFrame and export
    # df = pd.DataFrame(slice2d, index=ys_cm, columns=xs_cm)
    # df.index.name  = "Y (cm)"
    # df.columns.name = "X (cm)"

    # out_dir = r"c:\test"
    # os.makedirs(out_dir, exist_ok=True)
    # out_path = os.path.join(out_dir, "central_dose_slice.csv")
    # df.to_csv(out_path, float_format="%.6g")

    # QMessageBox.information(self, "Export Successful",
    #     f"Central Z-slice (z={zc}) exported to:\n{out_path}")

    # # Optionally recalc along–away from central slice
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
