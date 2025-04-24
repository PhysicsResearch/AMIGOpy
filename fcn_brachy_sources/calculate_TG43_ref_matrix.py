from PyQt5.QtWidgets import  QMessageBox
import os
import numpy as np
import pandas as pd

def calculate_dose_reference_matrix(self):
        """
        Builds a 2D TG-43 dose reference matrix over [-S,S] mm at Res-mm spacing,
        using the fitted radial polynomial and anisotropy table, and stores it in
        self.TG43.activesource.DoseMatrix (cGy/h).
        """
        src = self.TG43.activesource

        # 1) Sync UI → model: dose-rate constant & source length
        try:
            src.dose_rate_constant = float(self.Brachy_dose_rate_cte_value.text().strip())
            src.source_length_mm   = float(self.Brachy_rad_leng.text().strip())
        except ValueError as e:
            QMessageBox.critical(self, "Input Error",
                                 f"Could not parse TG-43 parameters:\n{e}")
            return

        # 2) Sync UI → model: grid resolution and half-size
        try:
            src.DoseMatrix_res_mm = float(self.Tg43_dose_grid.currentText().strip())
        except ValueError:
            QMessageBox.critical(self, "Input Error",
                                 f"Invalid grid resolution: '{self.Tg43_dose_grid.currentText()}'")
            return

        try:
            size_mm = float(self.Tg43_matrix_size_2.currentText().split('x',1)[0])
            src.DoseMatrix_size = size_mm
        except Exception:
            QMessageBox.critical(self, "Input Error",
                                 f"Invalid matrix size: '{self.Tg43_matrix_size_2.currentText()}'")
            return

        # # 3) Validate that everything else is loaded
        # missing = []
        # if src.airkerma_strength is None:
        #     missing.append("air-kerma strength")
        # if not hasattr(src, 'radial_fit') or src.radial_fit is None:
        #     missing.append("radial fit coefficients")
        # if src.anisotropy is None:
        #     missing.append("anisotropy data")
        # if missing:
        #     QMessageBox.critical(self, "Missing TG-43 Data",
        #                          "Please load or set:\n • " + "\n • ".join(missing))
        #     return

        # 4) Unpack
        Sk     = src.airkerma_strength          # U
        Λ      = src.dose_rate_constant         # cGy/h/U
        L_cm   = src.source_length_mm / 10.0    # cm
        Res    = src.DoseMatrix_res_mm          # mm
        S      = src.DoseMatrix_size            # mm half-span
        coeffs = src.radial_fit                 # [a5, a4, …, a0]

        # anisotropy table
        ani        = src.anisotropy
        # Correct definition of distance and anisotropy values (skip first column!)
        dist_vals  = ani[0, 1:]  # distances start at second column!
        angle_vals = ani[1:, 0]  # angles correctly from first column
        F_data     = np.nan_to_num(ani[1:, 1:], nan=0.0)  # skip angle column

        # geometry factor for a line of length L_cm
        def geometry_factor(r, theta_rad, L_cm):
            """
            TG-43 line-source geometry factor.
            
            r        : distance (cm)
            theta_rad: polar angle (radians)
            L_cm     : active source length (cm)
            """
            # On-axis case (theta=0 or 180°) → (r^2 - (L/2)^2)^{-1}
            if abs(np.sin(theta_rad)) < 1e-8:
                denom = r*r - (L_cm/2)**2
                return 1.0/denom if denom>0 else 0.0

            # Off-axis: standard line‐source formula
            rho = r * np.sin(theta_rad)
            z   = r * np.cos(theta_rad)
            alpha1 = np.arctan2((L_cm/2) - z, rho)
            alpha2 = np.arctan2((L_cm/2) + z, rho)
            beta   = alpha1 + alpha2
            return beta / (L_cm * rho)

        G_ref = geometry_factor(1.0, np.deg2rad(90.0),L_cm)

        # build grid coords in mm
        xs = np.linspace(-S, S, int(2*S/Res) + 1)
        ys = np.linspace(-S, S, int(2*S/Res) + 1)
        ny, nx = ys.size, xs.size

        Dose = np.zeros((ny, nx), dtype=float)

        # 5) fill dose matrix
        for iy, y in enumerate(ys):
            for ix, x in enumerate(xs):
                r_cm = np.hypot(x, y) / 10.0
                if r_cm == 0:  # singularity
                    continue

                theta = np.arctan2(y, x)
                theta_deg = (np.degrees(theta) + 360) % 360
                if theta_deg > 180:
                    theta_deg = 360 - theta_deg

                # geometry
                G = geometry_factor(r_cm, theta, L_cm)

                # radial
                if r_cm<src.radial[0,0]:
                    g = 1
                else:
                    # from polynomial
                    g = np.polyval(coeffs, r_cm)
                    if g < 0:
                        g = 0.0
                # anisotropy
                # Angle interpolation indices
                ai = np.clip(np.searchsorted(angle_vals, theta_deg), 1, angle_vals.size-1)
                a0, a1 = ai-1, ai
                θ0, θ1 = angle_vals[a0], angle_vals[a1]
                w = 0.0 if θ1==θ0 else (theta_deg - θ0)/(θ1 - θ0)

                # Clamp to first radial distance if below minimum
                if r_cm <= dist_vals[0]:
                    F0 = F_data[a0, 0]  # correct: first radial-distance bin at angle θ0
                    F1 = F_data[a1, 0]  # correct: first radial-distance bin at angle θ1
                    F  = F0*(1 - w) + F1*w
                else:
                    F0 = np.interp(r_cm, dist_vals, F_data[a0, :], left=F_data[a0, 0], right=0.0)
                    F1 = np.interp(r_cm, dist_vals, F_data[a1, :], left=F_data[a1, 0], right=0.0)
                    F  = F0*(1 - w) + F1*w


                # TG-43 dose rate - Sk will be multiplied during plan dose calculation
                Dose[iy, ix] = Λ * (G/G_ref) * g * F

        src.DoseMatrix = Dose

        # 6) build along–away from the matrix
        calculate_along_away_reference_calc(self)



def calculate_along_away_reference_calc(self):
    """
    Samples self.TG43.activesource.DoseMatrix at the along/away reference
    points (in self.TG43.activesource.along_away_reference) with bilinear interp.
    Any point that lies beyond the grid extent (±S mm) is set to NaN.
    """
    ref  = self.TG43.activesource.along_away_reference
    Dose = self.TG43.activesource.DoseMatrix
    Res  = self.TG43.activesource.DoseMatrix_res_mm
    S    = self.TG43.activesource.DoseMatrix_size

    # Rebuild the same grid as the dose‐matrix
    xs = np.arange(-S, S + Res, Res)  # mm
    ys = np.arange(-S, S + Res, Res)  # mm
    ny, nx = ys.size, xs.size

    # Compute the numeric bounds
    x_min, x_max = xs[0], xs[-1]
    y_min, y_max = ys[0], ys[-1]

    # Prepare the output array (same shape as ref)
    calc = np.empty_like(ref, dtype=float)
    # Copy headers back
    calc[0, 0]  = ref[0, 0]
    calc[0, 1:] = ref[0, 1:]
    calc[1:, 0] = ref[1:, 0]

    # Convert along/away from cm to mm
    along_mm = ref[1:, 0] * 10.0
    away_mm  = ref[0, 1:] * 10.0

    # Loop and interpolate
    for i, a in enumerate(along_mm, start=1):
        for j, b in enumerate(away_mm, start=1):
            # 1) If outside the ±S range, set NaN and continue.
            if not (x_min <= a <= x_max and y_min <= b <= y_max):
                calc[i, j] = np.nan
                continue

            # 2) Else find the four surrounding voxels...
            ix = np.clip(np.searchsorted(xs, a), 1, nx - 1)
            iy = np.clip(np.searchsorted(ys, b), 1, ny - 1)

            # Explicit check to avoid indexing at the boundary
            if ix == nx - 1:
                ix -= 1
            if iy == ny - 1:
                iy -= 1

            x0, x1 = xs[ix-1], xs[ix]
            y0, y1 = ys[iy-1], ys[iy]

            Q11 = Dose[iy-1, ix-1]
            Q21 = Dose[iy-1, ix]
            Q12 = Dose[iy,   ix-1]
            Q22 = Dose[iy,   ix]

            # 3) Compute weights
            tx = 0.0 if x1 == x0 else (a - x0) / (x1 - x0)
            ty = 0.0 if y1 == y0 else (b - y0) / (y1 - y0)

            # 4) Bilinear interpolation
            calc[i, j] = (
                Q11 * (1 - tx) * (1 - ty) +
                Q21 *   tx   * (1 - ty) +
                Q12 * (1 - tx) *   ty   +
                Q22 *   tx   *   ty
            )

    # Store the result back on the model
    # Flip vertical: reverse all rows except the header row
    calc[1:, :] = calc[1:, :][::-1, :]
    # Flip necessary to match with refrence data for along away .... 
    self.TG43.activesource.along_away_reference_calc = calc



