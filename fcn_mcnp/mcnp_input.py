# -*- coding: utf-8 -*-
"""
mcnp_input.py - MCNP input (.inp) file generator for AMIGOpy
============================================================

Generates an MCNP input file for a voxel phantom based on:
  * The MCNP universe map created in AMIGOpy (mcnp_lattice_maps)
  * The voxelization grid (mc_vox) defining the phantom bounds
  * The calculation grid (mc_grid) defining the scoring/dose grid
  * Original CT geometry (origin, spacing, dimensions)

Key MCNP constraints:
  * Maximum 80 columns per line (strictly enforced).
  * Lattice card uses run-length repeat notation (e.g. 1 7r for 8 repetitions).
  * Container cell 500 (fill=999).
  * Lattice cell 600 (lat=1 u=999 fill 0:nx 0:ny 0:nz).
  * Individual universe cell cards for each material/density combination.
  * Cell 998 (air region of interest around phantom, +2 cm margin).
  * Cell 999 (graveyard, outside universe, imp:p=0).
  * Surfaces 501-506 (phantom outer box, cm).
  * Surfaces 601-606 (lattice unit cell, cm).
  * Surfaces 971-976 (air margin boundary box, cm).
"""

from datetime import datetime
import os
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox, QProgressDialog

from fcn_processing.mc_grid import (
    get_grid_bounds,
    get_grid_origin_abs,
    get_grid_resolution,
    is_grid_mm_mode,
    _ref_origin_and_spacing,
)

MAX_COL = 80
LINE_INDENT = "     "


def _comment(text="", max_col=MAX_COL):
    """Format an MCNP comment line, strictly truncated to max_col."""
    if not text:
        return "c"
    line = f"c {text}"
    return line[:max_col]


def _sep(char="=", max_col=MAX_COL):
    """Return a full-width comment separator line."""
    return f"c {char * (max_col - 2)}"


def run_length_encode(arr):
    """Convert a 1D numpy array into (values, counts) using vectorized diff."""
    arr = np.asarray(arr)
    if arr.size == 0:
        return np.array([]), np.array([])
    locs = np.where(arr[:-1] != arr[1:])[0]
    starts = np.r_[0, locs + 1]
    ends = np.r_[locs + 1, arr.size]
    counts = ends - starts
    vals = arr[starts]
    return vals, counts


def format_rle_tokens(vals, counts):
    """Format runs of values as MCNP tokens: 'val' if count==1, 'val (c-1)r' if count>1."""
    tokens = []
    for v, c in zip(vals, counts):
        if c == 1:
            tokens.append(str(int(v)))
        else:
            tokens.append(f"{int(v)} {int(c - 1)}r")
    return tokens


def pack_tokens_to_lines(tokens, max_col=MAX_COL, indent=LINE_INDENT):
    """Pack tokens into lines <= max_col columns, appending trailing ' &' when continuing."""
    lines = []
    curr = indent
    for tok in tokens:
        sep = "" if curr == indent else " "
        # Check if adding tok plus trailing ' &' would exceed max_col
        if len(curr) + len(sep) + len(tok) + 2 > max_col:
            curr += " &"
            lines.append(curr)
            curr = indent + tok
        else:
            curr += sep + tok
    if curr.strip():
        lines.append(curr)
    return lines


def get_mcnp_sim_options(self):
    """Retrieve MCNP options from GUI widgets with robust defaults."""
    # 1. Tallies
    chk_ww = getattr(self, "mcnp_chk_dwater_water", None)
    chk_wm = getattr(self, "mcnp_chk_dwater_med", None)
    chk_tl = getattr(self, "mcnp_chk_dmed_med_tl", None)
    chk_ed = getattr(self, "mcnp_chk_dmed_med_ed", None)

    dwater_water = bool(chk_ww.isChecked()) if chk_ww is not None else False
    dwater_med = bool(chk_wm.isChecked()) if chk_wm is not None else False
    dmed_med_tl = bool(chk_tl.isChecked()) if chk_tl is not None else False
    dmed_med_ed = bool(chk_ed.isChecked()) if chk_ed is not None else False

    # 2. Source
    combo = getattr(self, "mcnp_source_combo", None)
    source_model = combo.currentText() if combo is not None else "None (External beam / custom)"

    # 3. Standard cards
    chk_std = getattr(self, "mcnp_chk_std_cards", None)
    std_cards = bool(chk_std.isChecked()) if chk_std is not None else True

    # 4. NPS
    nps_input = getattr(self, "mcnp_nps_input", None)
    nps_val = nps_input.text().strip() if nps_input is not None and nps_input.text().strip() else "1e6"

    return {
        "dwater_water": dwater_water,
        "dwater_med": dwater_med,
        "dmed_med_tl": dmed_med_tl,
        "dmed_med_ed": dmed_med_ed,
        "source_model": source_model,
        "std_cards": std_cards,
        "nps": nps_val,
    }


def get_material_composition(self, mat_name):
    """Return dict {Z: mass_fraction} for a given material name from Mat_df or database."""
    try:
        from fcn_DECT.constants import ATOMIC_NUMBER_TO_SYMBOL
        symbol_to_z = {v: k for k, v in ATOMIC_NUMBER_TO_SYMBOL.items()}
    except Exception:
        symbol_to_z = {}

    df = getattr(self, "Mat_df", None)
    if df is None:
        try:
            from fcn_materialassignment.material_assignment_properties import create_dataframe_materials
            df = create_dataframe_materials(self)
            self.Mat_df = df
        except Exception:
            df = None

    s_name = str(mat_name).strip().lower()

    # Special case: Air (dry air at sea level)
    if s_name == "air" or s_name.startswith("air-") or s_name.startswith("air_"):
        return {6: 0.000125, 7: 0.755267, 8: 0.231781, 18: 0.012827}

    elements = {}
    if df is not None and "Name" in df.columns:
        match = df[df["Name"] == mat_name]
        if match.empty:
            match = df[df["Name"].astype(str).str.strip().str.lower() == s_name]
        if match.empty:
            match = df[df["Name"].apply(
                lambda n: str(n).strip().lower() in s_name or s_name in str(n).strip().lower()
            )]

        if not match.empty:
            row = match.iloc[0]
            for col in df.columns:
                if col in symbol_to_z:
                    try:
                        val = float(row[col])
                    except (ValueError, TypeError):
                        continue
                    if val > 1.0:
                        val /= 100.0   # e.g. 88.8% -> 0.888
                    if val > 0:
                        elements[symbol_to_z[col]] = val

    if elements:
        total = sum(elements.values())
        if total > 0:
            return {z: v / total for z, v in elements.items()}

    # Standard fallback compositions if not found in df
    if "water" in s_name:
        return {1: 0.111894, 8: 0.888106}
    if "bone" in s_name:
        return {1: 0.034, 6: 0.155, 7: 0.042, 8: 0.435, 11: 0.001, 12: 0.002, 15: 0.103, 16: 0.003, 20: 0.225}
    if "lung" in s_name:
        return {1: 0.103, 6: 0.105, 7: 0.031, 8: 0.749, 11: 0.002, 15: 0.002, 16: 0.003, 17: 0.003, 19: 0.002}
    if "adipose" in s_name:
        return {1: 0.114, 6: 0.089, 7: 0.007, 8: 0.278, 11: 0.001, 16: 0.001, 17: 0.001}

    # Generic soft tissue / water approximation
    return {1: 0.111894, 8: 0.888106}


def format_material_card(mat_index, mat_name, comp_dict, max_col=MAX_COL, indent="        "):
    """Format an MCNP material card (e.g. m2) with ZAID and mass fractions.

    All lines <= max_col columns. Continuation lines use 8 spaces indentation.
    """
    lines = []
    lines.append(_comment(f"Material {mat_index}: {mat_name}"))
    if not comp_dict:
        comp_dict = {1: 0.111894, 8: 0.888106}
        lines.append(_comment(f"Warning: no composition found for '{mat_name}', using Water"))

    sorted_z = sorted(comp_dict.keys())
    tokens = []
    for z in sorted_z:
        frac = float(comp_dict[z])
        if frac <= 0:
            continue
        zaid_str = f"{int(z * 1000)}."
        frac_str = f"-{frac:.6f}"
        tokens.append(f"{zaid_str} {frac_str}")

    prefix = f"m{mat_index:<4}  "
    curr = prefix
    for tok in tokens:
        sep = "" if curr == prefix or curr == indent else "  "
        if len(curr) + len(sep) + len(tok) > max_col:
            lines.append(curr)
            curr = indent + tok
        else:
            curr += sep + tok
    if curr.strip():
        lines.append(curr)
    lines.append("c")
    return lines


# =============================================================================
# Standard Brachytherapy Source Component Surfaces (matching MATLAB source.mat)
# =============================================================================
SOURCE_SURFACES = {
    "microselectron": [
        "c MicroSelectron v2",
        "987 cx 0.045",
        "989 sq  2500  493.83 493.83  0 0 0  -1  -0.18  0.0 0.0",
        "990 kx 0.3025 0.44444444444 -1",
        "992 cx 0.036",
        "993 px 0.45",
    ],
    "gammamed": [
        "c Gammamed Plus",
        "9 cx  0.045",
        "12 kx -0.248 6.25 1",
        "13 px -0.242",
        "16 px 0.41",
    ],
    "flexisource": [
        "c Flexisource",
        "987 cx 0.045",
        "989 sq  2500  493.83 493.83  0 0 0  -1  -0.18  0.0 0.0",
        "990 kx 0.3025 0.44444444444 -1",
        "992 cx 0.036",
        "993 px 0.45",
    ],
    "tg186": [
        "c TG186 source model",
        "5    px  0.465",
        "7    cx  0.05",
        "8    sx -0.185 0.05",
    ],
    "axxent": [
        "c Axxent 50 keV",
        "18   px  0.3840",
        "20   x 0.3840 0.140 0.3468 0.2140 0.2570 0.267",
        "42   cx  0.267",
    ],
}


def get_source_surfaces(source_name):
    """Return list of MCNP surface card lines for the selected source model.

    Matches MATLAB AMIGO source.mat surface definitions:
      * MicroSelectron v2: surfaces 987, 989, 990, 992, 993
      * GammaMed Plus:     surfaces 9, 12, 13, 16
      * Flexisource:       surfaces 987, 989, 990, 992, 993
      * TG-186:            surfaces 5, 7, 8
      * Axxent:            surfaces 18, 20, 42
    """
    s = str(source_name).strip().lower().replace("-", "").replace("_", "").replace(" ", "")

    key = None
    if "microselectron" in s:
        key = "microselectron"
    elif "gammamed" in s:
        key = "gammamed"
    elif "flexisource" in s:
        key = "flexisource"
    elif "tg186" in s:
        key = "tg186"
    elif "axxent" in s:
        key = "axxent"

    if key is None:
        return []

    lines = SOURCE_SURFACES.get(key, [])
    res = []
    for l in lines:
        l_str = str(l).strip()
        if l_str.startswith("c"):
            res.append(_comment(l_str[1:].strip()))
        else:
            res.append(f"   {l_str}"[:MAX_COL])
    return res


def extract_plan_dwells(self, target=None):
    """Retrieve brachy dwell positions in original coordinates (cm) and dwell time in s.

    Matches MATLAB AMIGO logic:
      simulation.dwells(:,1:3) = dwells(:,1:3) / 10; % cm
      simulation.dwells(:,4)   = dwells(:,4); % time in s

    Returns: (dwell_list, total_dwell_time, total_air_kerma)
    """

    # 1. Look for RTPLAN entry in medical_image
    plan_entry = None
    pat_id_plan = getattr(self, "patientID_plan", None)
    study_id_plan = getattr(self, "studyID_plan", None)
    mod_plan = getattr(self, "modality_plan", "RTPLAN")
    ser_idx_plan = getattr(self, "series_index_plan", 0)

    med_img = getattr(self, "medical_image", {}) or {}

    if pat_id_plan and pat_id_plan in med_img:
        try:
            entry = med_img[pat_id_plan][study_id_plan][mod_plan][ser_idx_plan]
            if "Plan_Brachy_Channels" in entry.get("metadata", {}):
                plan_entry = entry
        except Exception:
            plan_entry = None

    # Fallback to current patientID
    if plan_entry is None:
        cur_pat = getattr(self, "patientID", None)
        if cur_pat and cur_pat in med_img:
            for s_id, s_dict in med_img[cur_pat].items():
                if isinstance(s_dict, dict) and "RTPLAN" in s_dict:
                    for s in s_dict["RTPLAN"]:
                        if "Plan_Brachy_Channels" in s.get("metadata", {}):
                            plan_entry = s
                            break
                    if plan_entry:
                        break

    # Fallback: search all patients
    if plan_entry is None:
        for p_id, p_dict in med_img.items():
            if isinstance(p_dict, dict):
                for s_id, s_dict in p_dict.items():
                    if isinstance(s_dict, dict) and "RTPLAN" in s_dict:
                        for s in s_dict["RTPLAN"]:
                            if "Plan_Brachy_Channels" in s.get("metadata", {}):
                                plan_entry = s
                                break
                    if plan_entry:
                        break
            if plan_entry:
                break

    # Fallback: check target metadata directly
    if plan_entry is None and target is not None:
        meta = target.get("metadata", {}) or {}
        if "Plan_Brachy_Channels" in meta:
            plan_entry = target

    dwell_list = []
    total_time = 0.0
    total_air_kerma = None

    if plan_entry is not None:
        meta = plan_entry.get("metadata", {}) or {}
        channels = meta.get("Plan_Brachy_Channels", [])
        total_air_kerma = meta.get("TotalAirKerma")
        ref_rate = meta.get("ReferenceAirKermaRate")

        for ch_idx, ch in enumerate(channels, start=1):
            ch_pos = ch.get("ChPos")
            cat_pts = None
            if ch_pos is not None:
                try:
                    c_arr = np.asarray(ch_pos, dtype=float)
                    if c_arr.ndim == 2 and c_arr.shape[0] >= 2 and c_arr.shape[1] >= 3:
                        cat_pts = c_arr[:, :3]
                except Exception:
                    cat_pts = None

            dw_info = ch.get("DwellInfo")
            if dw_info is None:
                continue
            if not isinstance(dw_info, np.ndarray):
                try:
                    dw_info = np.asarray(dw_info, dtype=float)
                except Exception:
                    continue
            if dw_info.size == 0 or dw_info.ndim != 2 or dw_info.shape[1] < 3:
                continue

            tot_time = ch.get("ChannelTotalTime", 1.0)
            final_w = ch.get("FinalCumulativeTimeWeight", 1.0)
            try:
                tot_time = float(tot_time) if tot_time is not None and tot_time != "N/A" else 1.0
            except (ValueError, TypeError):
                tot_time = 1.0
            try:
                final_w = float(final_w) if final_w is not None and final_w != "N/A" else 1.0
            except (ValueError, TypeError):
                final_w = 1.0
            scale = (tot_time / final_w) if (final_w > 0 and tot_time > 0) else 1.0

            # First pass: collect active dwells for this channel (dwell time > 0 only)
            ch_active = []
            for r in range(dw_info.shape[0]):
                try:
                    raw_t = float(dw_info[r, 2])
                except (IndexError, ValueError, TypeError):
                    continue

                if np.isnan(raw_t) or raw_t <= 0.0:
                    continue

                t_s = raw_t * scale
                if np.isnan(t_s) or t_s <= 1e-4 or round(t_s, 2) <= 0.0:
                    continue

                x_mm = float(dw_info[r, 3]) if dw_info.shape[1] > 3 else 0.0
                y_mm = float(dw_info[r, 4]) if dw_info.shape[1] > 4 else 0.0
                z_mm = float(dw_info[r, 5]) if dw_info.shape[1] > 5 else 0.0

                dir_x = float(dw_info[r, 6]) if dw_info.shape[1] > 6 else np.nan
                dir_y = float(dw_info[r, 7]) if dw_info.shape[1] > 7 else np.nan
                dir_z = float(dw_info[r, 8]) if dw_info.shape[1] > 8 else np.nan

                ch_active.append({
                    "r": r,
                    "t_s": t_s,
                    "x_mm": x_mm, "y_mm": y_mm, "z_mm": z_mm,
                    "dir_x": dir_x, "dir_y": dir_y, "dir_z": dir_z,
                })

            # Second pass: compute direction cosines matching MATLAB calculate_source_inclination
            for k, it in enumerate(ch_active):
                p = np.array([it["x_mm"], it["y_mm"], it["z_mm"]])
                ux, uy, uz = 0.0, 0.0, 0.0

                has_dicom_dir = (
                    not (np.isnan(it["dir_x"]) or np.isnan(it["dir_y"]) or np.isnan(it["dir_z"]))
                    and (abs(it["dir_x"]) > 1e-4 or abs(it["dir_y"]) > 1e-4 or abs(it["dir_z"]) > 1e-4)
                )
                # 1. Direct orientation from DICOM (planned by TPS)
                if has_dicom_dir:
                    v = np.array([it["dir_x"], it["dir_y"], it["dir_z"]])
                    norm = np.linalg.norm(v)
                    if norm > 1e-4:
                        ux, uy, uz = v[0] / norm, v[1] / norm, v[2] / norm
                # 2. Catheter path points
                elif cat_pts is not None:
                    dists = np.sum((cat_pts - p) ** 2, axis=1)
                    idx = int(np.argmin(dists))
                    if idx == len(cat_pts) - 1 or (
                        idx > 0 and np.sum((cat_pts[idx - 1] - p) ** 2) < np.sum((cat_pts[idx + 1] - p) ** 2)
                    ):
                        idx = idx - 1
                    v = cat_pts[idx + 1] - cat_pts[idx]
                    norm = np.linalg.norm(v)
                    if norm > 1e-6:
                        ux, uy, uz = v[0] / norm, v[1] / norm, v[2] / norm
                # 3. Adjacent active dwells
                elif len(ch_active) > 1:
                    if k + 1 < len(ch_active):
                        v = np.array([ch_active[k + 1]["x_mm"], ch_active[k + 1]["y_mm"], ch_active[k + 1]["z_mm"]]) - p
                    else:
                        v = p - np.array([ch_active[k - 1]["x_mm"], ch_active[k - 1]["y_mm"], ch_active[k - 1]["z_mm"]])
                    norm = np.linalg.norm(v)
                    if norm > 1e-6:
                        ux, uy, uz = v[0] / norm, v[1] / norm, v[2] / norm

                # Dwell coordinates in cm in original patient coordinate system (not shifted to 0)
                x_cm = it["x_mm"] / 10.0
                y_cm = it["y_mm"] / 10.0
                z_cm = it["z_mm"] / 10.0

                dwell_list.append({
                    "channel": ch_idx,
                    "x_cm": x_cm,
                    "y_cm": y_cm,
                    "z_cm": z_cm,
                    "time_s": it["t_s"],
                    "x_mm": it["x_mm"],
                    "y_mm": it["y_mm"],
                    "z_mm": it["z_mm"],
                    "dir_x": ux,
                    "dir_y": uy,
                    "dir_z": uz,
                })
                total_time += it["t_s"]

        if total_air_kerma is None and ref_rate is not None:
            try:
                total_air_kerma = float(ref_rate) * (total_time / 3600.0)
            except (ValueError, TypeError):
                total_air_kerma = None

    # Fallback to Dw_pos_info (e.g. from IrIS) if no RTPLAN dwells found
    if not dwell_list:
        dw_arr = getattr(self, "Dw_pos_info", None)
        if isinstance(dw_arr, np.ndarray) and dw_arr.ndim == 2 and dw_arr.shape[1] >= 15:
            if np.any(dw_arr[:, 8]) or np.any(dw_arr[:, 12:15]):
                for r in range(dw_arr.shape[0]):
                    try:
                        raw_t = float(dw_arr[r, 8]) if dw_arr[r, 8] > 0 else float(dw_arr[r, 10])
                    except (IndexError, ValueError, TypeError):
                        continue

                    # Omit any dwell without positive dwell time
                    if np.isnan(raw_t) or raw_t <= 1e-4 or round(raw_t, 2) <= 0.0:
                        continue  # Only count and print dwells with dwell time above 0

                    x_mm = float(dw_arr[r, 12])
                    y_mm = float(dw_arr[r, 13])
                    z_mm = float(dw_arr[r, 14])
                    # Dwell coordinates in cm in original patient coordinate system (not shifted to 0)
                    x_cm = x_mm / 10.0
                    y_cm = y_mm / 10.0
                    z_cm = z_mm / 10.0
                    dwell_list.append({
                        "channel": int(dw_arr[r, 15]) if dw_arr.shape[1] > 15 else 1,
                        "x_cm": x_cm,
                        "y_cm": y_cm,
                        "z_cm": z_cm,
                        "time_s": raw_t,
                        "x_mm": x_mm,
                        "y_mm": y_mm,
                        "z_mm": z_mm,
                        "dir_x": 0.0,
                        "dir_y": 0.0,
                        "dir_z": 0.0,
                    })
                    total_time += raw_t

    return dwell_list, total_time, total_air_kerma


def build_mcnp_header(self, target, lat_map_name, lat_entry, vox_info, grid_info, sim_options=None, dwells_info=None):
    """Build MCNP header comment cards listing geometry, metadata, and grid extents."""
    lines = []
    lines.append(_sep("="))
    lines.append(_comment("MCNP VOXEL PHANTOM INPUT FILE"))
    lines.append(_comment("Created with AMIGOpy"))
    lines.append(_comment(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"))
    lines.append(_sep("-"))

    # Series & Patient metadata
    pat_id = getattr(self, "patientID", "Unknown")
    study_id = getattr(self, "studyID", "Unknown")
    meta = target.get("metadata", {}) or {}
    ser_num = meta.get("SeriesNumber", target.get("SeriesNumber", "1"))
    ser_desc = meta.get("SeriesDescription", "CT")
    lines.append(_comment(f"Patient ID:        {pat_id}"))
    lines.append(_comment(f"Study ID:          {study_id}"))
    lines.append(_comment(f"Series Number:     {ser_num}"))
    lines.append(_comment(f"Series Description:{ser_desc}"))
    lines.append(_comment(f"Lattice Map:       {lat_map_name}"))
    lines.append(_sep("-"))

    # Simulation Settings & Scoring Options
    if sim_options is not None:
        lines.append(_comment("SIMULATION SETTINGS:"))
        lines.append(_comment(f"  Source model:          {sim_options['source_model']}"))
        lines.append(_comment(f"  Particles (nps / N):   {sim_options['nps']}"))
        lines.append(_comment(f"  Standard physics cards:{'Included' if sim_options['std_cards'] else 'Excluded'}"))
        lines.append(_comment("  Scoring / Tallies requested:"))
        lines.append(_comment(f"    * Dwater in water (Track length):       {'YES' if sim_options['dwater_water'] else 'NO'}"))
        lines.append(_comment(f"    * Dwater in medium (Track length):      {'YES' if sim_options['dwater_med'] else 'NO'}"))
        lines.append(_comment(f"    * Dose to medium in Medium (Track len): {'YES' if sim_options['dmed_med_tl'] else 'NO'}"))
        lines.append(_comment(f"    * Dose to med in med (Energy deposit):  {'YES' if sim_options['dmed_med_ed'] else 'NO'}"))
        lines.append(_sep("-"))

    # Dwell positions (written similarly to MATLAB write_header, strictly dwell time > 0)
    if dwells_info is not None:
        dwells, total_dwell_time, air_kerma = dwells_info
    else:
        dwells, total_dwell_time, air_kerma = extract_plan_dwells(self, target)

    if dwells:
        lines.append(_comment("BRACHYTHERAPY DWELL POSITIONS (dwell time > 0 only):"))
        lines.append(_comment(f"  Total Dwell Points: {len(dwells)}"))
        lines.append(_comment(f"  Total Dwell Time:   {total_dwell_time:.4f} s"))
        if air_kerma is not None:
            lines.append(_comment(f"  Total Air Kerma:    {air_kerma:.2f}"))
        lines.append(_comment("  Format: c <X_cm> <Y_cm> <Z_cm> <Time_s> (AMIGO patient coordinates [cm])"))
        for d in dwells:
            card = f"c {d['x_cm']:6.2f} {d['y_cm']:6.2f} {d['z_cm']:6.2f} {d['time_s']:6.2f}"
            lines.append(card[:MAX_COL])
        lines.append(_sep("-"))

    # Original Image Geometry
    (ox, oy, oz), (ps_col, ps_row, st) = _ref_origin_and_spacing(self)
    d0 = target.get("3DMatrix")
    if d0 is not None:
        ns, nr, nc = d0.shape
    else:
        ns, nr, nc = vox_info["img_shape"]

    lines.append(_comment("ORIGINAL IMAGE GEOMETRY:"))
    lines.append(_comment(f"  Dimensions (Z, Y, X): {ns} x {nr} x {nc} voxels"))
    lines.append(_comment(f"  Voxel size (dx,dy,dz): {ps_col:.4f} x {ps_row:.4f} x {st:.4f} mm"))
    lines.append(_comment(f"  Image Origin (IPP):   [{ox:.3f}, {oy:.3f}, {oz:.3f}] mm"))
    lines.append(_comment(f"  Extents in mm (X):    0.000 to {nc * ps_col:.3f} mm"))
    lines.append(_comment(f"  Extents in mm (Y):    0.000 to {nr * ps_row:.3f} mm"))
    lines.append(_comment(f"  Extents in mm (Z):    0.000 to {ns * st:.3f} mm"))
    lines.append(_sep("-"))

    # Voxelization Grid (Phantom)
    vx = vox_info
    lines.append(_comment("VOXELIZATION GRID (mc_vox) - PHANTOM BOUNDS:"))
    lines.append(_comment(f"  Voxel index range (inclusive, 0-based):"))
    lines.append(_comment(f"    MCNP X (cols / sagittal):  [{vx['cmin']}, {vx['cmax']}] ({vx['nc']} voxels)"))
    lines.append(_comment(f"    MCNP Y (rows / coronal):   [{vx['rmin']}, {vx['rmax']}] ({vx['nr']} voxels)"))
    lines.append(_comment(f"    MCNP Z (slices / axial):   [{vx['smin']}, {vx['smax']}] ({vx['ns']} voxels)"))
    lines.append(_comment(f"  Offset from image origin (mm):"))
    lines.append(_comment(f"    MCNP X (cols):   {vx['x_rel_min']:.3f} to {vx['x_rel_max']:.3f} mm ({vx['x_rel_min']/10:.4f} to {vx['x_rel_max']/10:.4f} cm)"))
    lines.append(_comment(f"    MCNP Y (rows):   {vx['y_rel_min']:.3f} to {vx['y_rel_max']:.3f} mm ({vx['y_rel_min']/10:.4f} to {vx['y_rel_max']/10:.4f} cm)"))
    lines.append(_comment(f"    MCNP Z (slices): {vx['z_rel_min']:.3f} to {vx['z_rel_max']:.3f} mm ({vx['z_rel_min']/10:.4f} to {vx['z_rel_max']/10:.4f} cm)"))
    lines.append(_comment(f"  Absolute DICOM coordinates (mm):"))
    lines.append(_comment(f"    X (cols):   {vx['x_abs_min']:.3f} to {vx['x_abs_max']:.3f} mm"))
    lines.append(_comment(f"    Y (rows):   {vx['y_abs_min']:.3f} to {vx['y_abs_max']:.3f} mm"))
    lines.append(_comment(f"    Z (slices): {vx['z_abs_min']:.3f} to {vx['z_abs_max']:.3f} mm"))
    lines.append(_sep("-"))

    # Calculation Grid
    gx = grid_info
    lines.append(_comment("CALCULATION GRID (mc_grid) - DOSE / TALLY BOUNDS:"))
    lines.append(_comment(f"  Mode: {gx['mode']}"))
    lines.append(_comment(f"  Resolution (col, row, slice mm):"))
    lines.append(_comment(f"    {gx['res_col_mm']:.8f} x {gx['res_row_mm']:.8f} x {gx['res_slice_mm']:.8f} mm"))
    lines.append(_comment(f"  Voxel index range (inclusive):"))
    lines.append(_comment(f"    MCNP X / UI X (cols / sagittal):  [{gx['cmin']:.1f}, {gx['cmax']:.1f}]"))
    lines.append(_comment(f"    MCNP Y / UI Z (rows / coronal):   [{gx['rmin']:.1f}, {gx['rmax']:.1f}]"))
    lines.append(_comment(f"    MCNP Z / UI Y (slices / axial):   [{gx['smin']:.1f}, {gx['smax']:.1f}]"))
    lines.append(_comment(f"  Absolute origin (mm): [{gx['orig_x']:.3f}, {gx['orig_y']:.3f}, {gx['orig_z']:.3f}] mm"))
    lines.append(_comment(f"  Absolute origin (cm): [{gx['orig_x']/10:.4f}, {gx['orig_y']/10:.4f}, {gx['orig_z']/10:.4f}] cm"))
    lines.append(_sep("="))
    return lines


def build_source_cards(sim_options, dwells, total_dwell_time, max_col=MAX_COL):
    """Build MCNP source definition cards (SSR, SI1, SP1, tr cards) for brachy source models.

    Matches MATLAB AMIGO simulation_main write_source:
      c Source ... Tr ... Parameters  
      mode p 
      SSR  OLD <surfaces> tr=D1 WGT=<total_time>
      SI1  L 1 2 3 4 5 6 7 8 9 10 11 12 
            13 14 ... 
      c
      SP1   13.6 13.6 ... 
            13.6 ... 
      c
      tr1 <X_cm> <Y_cm> <Z_cm> <dir_X> <dir_Y> <dir_Z>
      ...
      c
    """
    source_model = sim_options.get("source_model", "")
    s = str(source_model).strip().lower().replace("-", "").replace("_", "").replace(" ", "")

    if "none" in s or not source_model:
        return [
            "c Source ... Tr ... Parameters  ",
            "mode p ",
            _comment("External beam / custom source - specify source here"),
            "c",
        ]

    lines = []
    lines.append("c Source ... Tr ... Parameters  ")
    lines.append("mode p ")

    if not dwells:
        lines.append(_comment(f"Note: No active dwell positions found for {source_model}"))
        lines.append("c")
        return lines

    # Determine surface list for SSR card based on source model (matching MATLAB source.mat)
    if "gammamed" in s:
        surf_str = "9 12 13 16"
    elif "microselectron" in s:
        surf_str = "987 989 990 992 993"
    elif "flexisource" in s:
        surf_str = "987 989 990 992 993"
    elif "tg186" in s:
        surf_str = "5 7 8"
    elif "axxent" in s:
        surf_str = "18 20 42"
    else:
        surf_str = "987 989 990 992 993"

    n_dwells = len(dwells)
    tot_wgt = total_dwell_time if total_dwell_time > 0 else sum(d["time_s"] for d in dwells)

    # 1. SSR card
    tr_ref = "1" if n_dwells == 1 else "D1"
    ssr_card = f"SSR  OLD {surf_str} tr={tr_ref} WGT={tot_wgt:.3f}"
    lines.append(ssr_card[:max_col])

    if n_dwells > 1:
        # 2. SI1 card (Dwell IDs, 12 items per line, continuation 6 spaces)
        cont = 1
        curr = "SI1  L"
        for i in range(1, n_dwells + 1):
            curr += f" {i}"
            cont += 1
            if cont == 13 and i != n_dwells:
                lines.append((curr + " ")[:max_col])
                curr = "     "
                cont = 1
            elif i == n_dwells:
                lines.append((curr + " ")[:max_col])
        lines.append("c")

        # 3. SP1 card (Dwell times as sampling probability, 12 items per line, continuation 6 spaces)
        cont = 1
        curr = "SP1  "
        for i, d in enumerate(dwells, start=1):
            curr += f" {d['time_s']:4.1f}"
            cont += 1
            if cont == 13 and i != n_dwells:
                lines.append((curr + " ")[:max_col])
                curr = "     "
                cont = 1
            elif i == n_dwells:
                lines.append((curr + " ")[:max_col])
        lines.append("c")

    # 4. Translation cards (tr1, tr2, ... trN) matching DICOM / MCNP coordinate convention:
    # MCNP X -> DICOM X (columns / sagittal)
    # MCNP Y -> DICOM Y (rows / coronal)
    # MCNP Z -> DICOM Z (slices / axial)
    for i, d in enumerate(dwells, start=1):
        x_c = d["x_cm"]
        y_c = d["y_cm"]
        z_c = d["z_cm"]
        dir_x = d.get("dir_x", 0.0)
        dir_y = d.get("dir_y", 0.0)
        dir_z = d.get("dir_z", 0.0)

        # Check if direction cosines are available
        if abs(dir_x) > 1e-5 or abs(dir_y) > 1e-5 or abs(dir_z) > 1e-5:
            tr_card = f"tr{i} {x_c:6.5f} {y_c:6.5f} {z_c:6.5f} {dir_x:6.5f} {dir_y:6.5f} {dir_z:6.5f}"
        else:
            tr_card = f"tr{i} {x_c:6.5f} {y_c:6.5f} {z_c:6.5f}"
        lines.append(tr_card[:max_col])

    lines.append("c")
    return lines


NIST_WATER_COEF_LINES = [
    "#  de4     df4",
    "   0.0010   4065.0000",
    "   0.0015   1372.0000",
    "   0.0020    615.2000",
    "   0.0030    191.7000",
    "   0.0040    81.9100",
    "   0.005    41.88000",
    "   0.006    24.05000",
    "   0.008     9.91500",
    "   0.010     4.94400",
    "   0.015     1.37400",
    "   0.020     0.55030",
    "   0.030     0.15570",
    "   0.040     0.06947",
    "   0.050     0.04223",
    "   0.060     0.03190",
    "   0.080     0.02597",
    "   0.100     0.02546",
    "   0.150     0.02764",
    "   0.200     0.02967",
    "   0.300     0.03192",
    "   0.400     0.03279",
    "   0.500     0.03299",
    "   0.600     0.03284",
    "   0.800     0.03206",
    "   1.000     0.03103",
    "   1.250     0.02965",
    "   1.500     0.02833",
]


def build_mcnp_tallies(grid_info, sim_options, max_col=MAX_COL):
    """
    Generate MCNP FMESH tally cards matching MATLAB AMIGO simulation_main write_tally.
    Supports:
      - Dose to water in water / Dose to water in medium (Track length): *FMESH4:p with NIST water coefficients
      - Dose to medium in medium (Track length): FMESH14:p with FM14 -1 -0 -5 -6

    MCNP Coordinate System mapping matching AMIGO:
      - MCNP X-axis (px, IMESH, IINTS): Columns (sagittal, AMIGO X)
      - MCNP Y-axis (py, JMESH, JINTS): Slices (axial, AMIGO Y)
      - MCNP Z-axis (pz, KMESH, KINTS): Rows (coronal, AMIGO Z)
    """
    st_mm = float(grid_info.get("st", grid_info.get("res_slice_mm", 1.0)))
    ps_col_mm = float(grid_info.get("ps_col", grid_info.get("res_col_mm", 1.0)))
    ps_row_mm = float(grid_info.get("ps_row", grid_info.get("res_row_mm", 1.0)))

    # Calculation grid bin sizes (in mm)
    res_col_mm = float(grid_info.get("res_col_mm", grid_info.get("res_x", ps_col_mm)))
    res_slice_mm = float(grid_info.get("res_slice_mm", grid_info.get("res_y", st_mm)))
    res_row_mm = float(grid_info.get("res_row_mm", grid_info.get("res_z", ps_row_mm)))

    # Bounds in voxel units (0-based)
    cmin = float(grid_info.get("cmin", 0))
    cmax = float(grid_info.get("cmax", 0))
    smin = float(grid_info.get("smin", 0))
    smax = float(grid_info.get("smax", 0))
    rmin = float(grid_info.get("rmin", 0))
    rmax = float(grid_info.get("rmax", 0))

    # Reference image origin (in mm)
    ox = float(grid_info.get("ox", 0.0))
    oy = float(grid_info.get("oy", 0.0))
    oz = float(grid_info.get("oz", 0.0))

    span_x_mm = (cmax - cmin + 1.0) * ps_col_mm
    span_y_mm = (rmax - rmin + 1.0) * ps_row_mm
    span_z_mm = (smax - smin + 1.0) * st_mm
    mcnp_x_ints = max(1, int(round(span_x_mm / res_col_mm)))
    mcnp_y_ints = max(1, int(round(span_y_mm / res_row_mm)))
    mcnp_z_ints = max(1, int(round(span_z_mm / res_slice_mm)))

    if grid_info.get("mode") == "mm":
        # Absolute coordinates from calculation grid spinboxes (already in DICOM mm)
        orig_x = float(grid_info.get("orig_x", ox))
        orig_y = float(grid_info.get("orig_y", oy)) # Coronal / Row -> DICOM Y
        orig_z = float(grid_info.get("orig_z", oz)) # Axial / Slice -> DICOM Z
        mcnp_x0_cm = orig_x / 10.0
        mcnp_x1_cm = mcnp_x0_cm + span_x_mm / 10.0
        mcnp_y0_cm = orig_y / 10.0
        mcnp_y1_cm = mcnp_y0_cm + span_y_mm / 10.0
        mcnp_z0_cm = orig_z / 10.0
        mcnp_z1_cm = mcnp_z0_cm + span_z_mm / 10.0
    else:
        # Voxel mode: true DICOM coordinates (not shifted to 0)
        # MCNP X-axis (Columns / Sagittal, DICOM X)
        mcnp_x0_cm = (ox + cmin * ps_col_mm) / 10.0
        mcnp_x1_cm = (ox + (cmax + 1.0) * ps_col_mm) / 10.0
        # MCNP Y-axis (Rows / Coronal, DICOM Y)
        mcnp_y0_cm = (oy + rmin * ps_row_mm) / 10.0
        mcnp_y1_cm = (oy + (rmax + 1.0) * ps_row_mm) / 10.0
        # MCNP Z-axis (Slices / Axial, DICOM Z)
        mcnp_z0_cm = (oz + smin * st_mm) / 10.0
        mcnp_z1_cm = (oz + (smax + 1.0) * st_mm) / 10.0

    want_dwm = bool(sim_options.get("dwater_water") or sim_options.get("dwater_med"))
    want_dmm = bool(sim_options.get("dmed_med_tl"))
    # Default to Dose to water (Track length) if no tally is explicitly selected so file is ready to run
    if not (want_dwm or want_dmm):
        want_dwm = True

    lines = []

    # 1. Dose to water (Track length) -> *FMESH4:p with NIST water conversion coefficients
    if want_dwm:
        lines.append("c ------------ FMESH ----------")
        lines.append(f"*FMESH4:p GEOM=xyz ORIGIN= {mcnp_x0_cm:.16f} {mcnp_y0_cm:.16f} &"[:max_col])
        lines.append(f"     {mcnp_z0_cm:.16f} IMESH={mcnp_x1_cm:.16f}"[:max_col])
        lines.append(f"     IINTS={mcnp_x_ints} JMESH={mcnp_y1_cm:.16f}"[:max_col])
        lines.append(f"     JINTS={mcnp_y_ints} KMESH={mcnp_z1_cm:.16f} KINTS={mcnp_z_ints} OUT=ik"[:max_col])
        lines.append("c")
        lines.extend(NIST_WATER_COEF_LINES)
        lines.append("c")

    # 2. Dose to medium in medium (Track length) -> FMESH14:p with local medium multiplier
    if want_dmm:
        lines.append("c ------------ FMESH ----------")
        lines.append(f"FMESH14:p GEOM=xyz ORIGIN= {mcnp_x0_cm:.16f} {mcnp_y0_cm:.16f} &"[:max_col])
        lines.append(f"     {mcnp_z0_cm:.16f} IMESH={mcnp_x1_cm:.16f}"[:max_col])
        lines.append(f"     IINTS={mcnp_x_ints} JMESH={mcnp_y1_cm:.16f}"[:max_col])
        lines.append(f"     JINTS={mcnp_y_ints} KMESH={mcnp_z1_cm:.16f} KINTS={mcnp_z_ints} OUT=ik"[:max_col])
        lines.append("c")
        lines.append("FM14 -1 -0 -5 -6")
        lines.append("c")

    return lines


def build_mcnp_cards(self, target, lat_map_name, progress_cb=None):
    """Assemble all MCNP cards (Header, Cells, Surfaces, Data) into a list of lines."""
    if progress_cb:
        progress_cb(10, "Reading lattice map and geometry...")

    lat_entry = target["mcnp_lattice_maps"][lat_map_name]
    uni_map = np.asarray(lat_entry["3DMatrix"])
    universes = lat_entry.get("universes", [])

    img_shape = uni_map.shape  # (ns, nr, nc)
    (ox, oy, oz), (ps_col, ps_row, st) = _ref_origin_and_spacing(self)

    # 1. Determine Voxelization Grid bounds (phantom subvolume)
    if progress_cb:
        progress_cb(20, "Determining phantom grid bounds...")
    vox_bounds = get_grid_bounds(self, "mc_vox")
    if vox_bounds is None:
        cmin_i, cmax_i = 0, img_shape[2] - 1
        rmin_i, rmax_i = 0, img_shape[1] - 1
        smin_i, smax_i = 0, img_shape[0] - 1
    else:
        cmin_raw, cmax_raw, rmin_raw, rmax_raw, smin_raw, smax_raw = vox_bounds
        cmin_i = max(0, min(img_shape[2] - 1, int(round(cmin_raw))))
        cmax_i = max(cmin_i, min(img_shape[2] - 1, int(round(cmax_raw))))
        rmin_i = max(0, min(img_shape[1] - 1, int(round(rmin_raw))))
        rmax_i = max(rmin_i, min(img_shape[1] - 1, int(round(rmax_raw))))
        smin_i = max(0, min(img_shape[0] - 1, int(round(smin_raw))))
        smax_i = max(smin_i, min(img_shape[0] - 1, int(round(smax_raw))))

    nc_vox = cmax_i - cmin_i + 1
    nr_vox = rmax_i - rmin_i + 1
    ns_vox = smax_i - smin_i + 1

    vox_info = {
        "img_shape": img_shape,
        "cmin": cmin_i, "cmax": cmax_i, "nc": nc_vox,
        "rmin": rmin_i, "rmax": rmax_i, "nr": nr_vox,
        "smin": smin_i, "smax": smax_i, "ns": ns_vox,
        "x_rel_min": cmin_i * ps_col, "x_rel_max": (cmax_i + 1) * ps_col,
        "y_rel_min": rmin_i * ps_row, "y_rel_max": (rmax_i + 1) * ps_row,
        "z_rel_min": smin_i * st,     "z_rel_max": (smax_i + 1) * st,
        "x_abs_min": ox + cmin_i * ps_col, "x_abs_max": ox + (cmax_i + 1) * ps_col,
        "y_abs_min": oy + rmin_i * ps_row, "y_abs_max": oy + (rmax_i + 1) * ps_row,
        "z_abs_min": oz + smin_i * st,     "z_abs_max": oz + (smax_i + 1) * st,
    }

    # 2. Determine Calculation Grid bounds
    grid_bounds = get_grid_bounds(self, "mc_grid")
    if grid_bounds is None:
        gc_min, gc_max, gr_min, gr_max, gs_min, gs_max = 0, img_shape[2] - 1, 0, img_shape[1] - 1, 0, img_shape[0] - 1
    else:
        gc_min, gc_max, gr_min, gr_max, gs_min, gs_max = grid_bounds
    gres = get_grid_resolution(self, "mc_grid")
    # UI order: x -> cols (ps_col), y -> slices (st), z -> rows (ps_row)
    col_res_mm = gres[0] if gres else ps_col
    slice_res_mm = gres[1] if gres else st
    row_res_mm = gres[2] if gres else ps_row
    gorig = get_grid_origin_abs(self, "mc_grid") or (ox, oy, oz)

    grid_info = {
        "mode": "mm" if is_grid_mm_mode(self, "mc_grid") else "voxel",
        "res_col_mm": col_res_mm,
        "res_slice_mm": slice_res_mm,
        "res_row_mm": row_res_mm,
        "ps_col": ps_col,
        "ps_row": ps_row,
        "st": st,
        "cmin": gc_min, "cmax": gc_max,
        "rmin": gr_min, "rmax": gr_max,
        "smin": gs_min, "smax": gs_max,
        "res_x": col_res_mm,
        "res_y": slice_res_mm,
        "res_z": row_res_mm,
        "orig_x": gorig[0], "orig_y": gorig[1], "orig_z": gorig[2],
        "ox": ox, "oy": oy, "oz": oz,
    }

    # Extract subvolume for the phantom
    if progress_cb:
        progress_cb(35, "Extracting phantom subvolume...")
    sub = uni_map[smin_i:smax_i + 1, rmin_i:rmax_i + 1, cmin_i:cmax_i + 1]
    # Rows in AMIGO display_data were flipped along axis 1 (vol = np.flip(vol, axis=1)).
    # Flip axis 1 back to match DICOM physical Y (Anterior-to-Posterior):
    sub_mcnp = np.flip(sub, axis=1)
    # M matrix for lattice filling matching DICOM / MCNP coordinate convention:
    #   Dimension 1 (px, cols, size nc_vox, advances fastest in 'F' order): axis 2 of sub_mcnp
    #   Dimension 2 (py, rows, size nr_vox, advances second in 'F' order):  axis 1 of sub_mcnp
    #   Dimension 3 (pz, slices, size ns_vox, advances slowest in 'F' order): axis 0 of sub_mcnp
    M = sub_mcnp.transpose(2, 1, 0)
    flat = M.flatten(order="F")

    if progress_cb:
        progress_cb(50, "Compressing lattice with run-length encoding...")
    vals, counts = run_length_encode(flat)
    tokens = format_rle_tokens(vals, counts)

    # 4. Read simulation options from UI
    sim_options = get_mcnp_sim_options(self)

    # Extract dwell positions (strictly only active dwells with dwell time > 0)
    dwells_info = extract_plan_dwells(self, target)
    dwells, total_dwell_time, air_kerma = dwells_info

    # 5. Generate Cards
    out_lines = []

    # --- Header ---
    out_lines.extend(build_mcnp_header(self, target, lat_map_name, lat_entry, vox_info, grid_info, sim_options, dwells_info=dwells_info))

    # =========================================================================
    # BLOCK 1: CELL CARDS
    # =========================================================================
    out_lines.append(_comment("CELL CARDS (Block 1)"))
    out_lines.append(_comment("Container Cell 500 (Voxel Phantom)"))
    out_lines.append("500 0        501 -502 503 -504 505 -506      fill=999  imp:p=1")

    out_lines.append(_comment("Lattice Cell 600"))
    out_lines.append("600 0       -606 605 -604 603 -602 601     lat=1 u=999 imp:p=1 &")
    out_lines.append(f"     fill 0:{nc_vox - 1} 0:{nr_vox - 1} 0:{ns_vox - 1} &")

    # Packed RLE fill lines
    if progress_cb:
        progress_cb(70, "Formatting MCNP fill cards (<= 80 columns)...")
    fill_lines = pack_tokens_to_lines(tokens, max_col=MAX_COL, indent=LINE_INDENT)
    out_lines.extend(fill_lines)

    # Individual Universe Cell Cards
    if progress_cb:
        progress_cb(85, "Assembling cell, surface, and data cards...")
    out_lines.append(_comment("Universes (Material and Density mapping)"))
    for row in universes:
        u = row["universe"]
        mat_idx = row["material_index"]
        density = row["density"]
        cell_id = 1000 + u
        card = f"{cell_id} {mat_idx} -{density:.6f} -606 605 -604 603 -602 601 u={u} imp:p=1"
        out_lines.append(card[:MAX_COL])

    out_lines.append(_comment("Region of interest (air margin around phantom)"))
    out_lines.append("998  1 -0.001205  971 -972 973 -974 975 -976 #500   imp:p=1")
    out_lines.append(_comment("Graveyard (Region of no interest)"))
    out_lines.append("999  0    -971:972:-973:974:-975:976               imp:p=0")

    # Blank line ending Cell Cards block (required by MCNP)
    out_lines.append("")

    # =========================================================================
    # BLOCK 2: SURFACE CARDS
    # =========================================================================
    # Coordinates in cm (divided by 10) in original patient coordinate system (not shifted to 0):
    # Mapping matching DICOM / MCNP Cartesian convention:
    #   px -> cols   (sagittal, DICOM X)
    #   py -> rows   (coronal,  DICOM Y)
    #   pz -> slices (axial,    DICOM Z)
    px_min_cm = (ox + cmin_i * ps_col) / 10.0
    px_max_cm = (ox + (cmax_i + 1) * ps_col) / 10.0
    py_min_cm = (oy + rmin_i * ps_row) / 10.0
    py_max_cm = (oy + (rmax_i + 1) * ps_row) / 10.0
    pz_min_cm = (oz + smin_i * st) / 10.0
    pz_max_cm = (oz + (smax_i + 1) * st) / 10.0

    # Lattice unit voxel (1 voxel width starting from min)
    px_vox_cm = (ox + (cmin_i + 1) * ps_col) / 10.0
    py_vox_cm = (oy + (rmin_i + 1) * ps_row) / 10.0
    pz_vox_cm = (oz + (smin_i + 1) * st) / 10.0

    # Air margin: 2 cm padding
    margin_cm = 2.0

    out_lines.append(_comment("SURFACE CARDS (Block 2)"))

    # Source surfaces (specific to the selected source model, matching MATLAB)
    source_surfs = get_source_surfaces(sim_options["source_model"])
    if source_surfs:
        out_lines.append(_sep("-"))
        out_lines.append(_comment(f"Source Surfaces ({sim_options['source_model']})"))
        out_lines.extend(source_surfs)
        out_lines.append(_sep("-"))

    out_lines.append(_comment("Phantom Bounding Box Surfaces (cm)"))
    out_lines.append(f"   501 px  {px_min_cm:.6f}")
    out_lines.append(f"   502 px  {px_max_cm:.6f}")
    out_lines.append(f"   503 py  {py_min_cm:.6f}")
    out_lines.append(f"   504 py  {py_max_cm:.6f}")
    out_lines.append(f"   505 pz  {pz_min_cm:.6f}")
    out_lines.append(f"   506 pz  {pz_max_cm:.6f}")

    out_lines.append(_comment("Lattice Unit Voxel Surfaces (cm)"))
    out_lines.append(f"   601 px  {px_min_cm:.6f}")
    out_lines.append(f"   602 px  {px_vox_cm:.6f}")
    out_lines.append(f"   603 py  {py_min_cm:.6f}")
    out_lines.append(f"   604 py  {py_vox_cm:.6f}")
    out_lines.append(f"   605 pz  {pz_min_cm:.6f}")
    out_lines.append(f"   606 pz  {pz_vox_cm:.6f}")

    out_lines.append(_comment("World / Air Margin Bounding Surfaces (+2 cm, cm)"))
    out_lines.append(f"   971 px  {px_min_cm - margin_cm:.6f}")
    out_lines.append(f"   972 px  {px_max_cm + margin_cm:.6f}")
    out_lines.append(f"   973 py  {py_min_cm - margin_cm:.6f}")
    out_lines.append(f"   974 py  {py_max_cm + margin_cm:.6f}")
    out_lines.append(f"   975 pz  {pz_min_cm - margin_cm:.6f}")
    out_lines.append(f"   976 pz  {pz_max_cm + margin_cm:.6f}")

    # Blank line ending Surface Cards block (required by MCNP)
    out_lines.append("")

    # =========================================================================
    # BLOCK 3: DATA CARDS (Sources, Tallies, Materials, Physics)
    # =========================================================================
    out_lines.append(_comment("DATA CARDS (Block 3)"))
    out_lines.append(_sep("-"))

    # 1. Source cards (active dwells only) - matches MATLAB simulation_main write_source
    source_cards = build_source_cards(sim_options, dwells, total_dwell_time)
    out_lines.extend(source_cards)

    # 2. Tally cards (Track length FMESH) - matches MATLAB simulation_main write_tally
    tally_cards = build_mcnp_tallies(grid_info, sim_options)
    out_lines.extend(tally_cards)

    # 3. Materials - matches MATLAB simulation_main write_material
    out_lines.append(_sep("-"))
    out_lines.append(_comment("MATERIALS"))
    out_lines.append(_sep("-"))
    # Material 1: Standard Air (rho = 0.001205 g/cm3) - ALWAYS defined
    air_card = format_material_card(
        1, "Air (standard reference material, rho = 0.001205 g/cm3)",
        {6: 0.000125, 7: 0.755267, 8: 0.231781, 18: 0.012827}
    )
    out_lines.extend(air_card)

    # Phantom materials starting from Material ID 2
    seen_mats = set()
    for row in universes:
        midx = row.get("material_index", 1)
        if midx >= 2 and midx not in seen_mats:
            seen_mats.add(midx)
            mname = row.get("material", f"Material {midx}")
            comp = get_material_composition(self, mname)
            card_lines = format_material_card(midx, mname, comp)
            out_lines.extend(card_lines)

    # 4. Standard physics cards
    if sim_options["std_cards"]:
        out_lines.append(_comment("Standard physics cards"))
        out_lines.append("PHYS:P")
        out_lines.append("cut:p j 0.001")
        out_lines.append("prdmp j 1e+9 j j")
        out_lines.append("dbcn 17j 1 30j 2")

    # 5. Number of particles (NPS)
    out_lines.append(f"nps {sim_options['nps']}")
    out_lines.append("c")

    # Strict assertion for column 80 limit
    for idx, l in enumerate(out_lines):
        if len(l) > MAX_COL:
            raise ValueError(f"Line {idx + 1} exceeds {MAX_COL} columns ({len(l)} chars): {l}")

    return out_lines, vox_info, grid_info


def create_mcnp_input(self):
    """Button callback: prompts user for output file and writes MCNP input."""
    if not getattr(self, "patientID", None):
        QMessageBox.critical(self, "Error", "No patient selected")
        return
    ct_list = self.medical_image.get(self.patientID, {}).get(self.studyID, {}).get("CT", [])
    if not ct_list:
        QMessageBox.critical(self, "Error", "No CT series found")
        return
    cur_m = getattr(self, "modality", None)
    cur_idx = getattr(self, "series_index", 0)
    ct_idx = cur_idx if (cur_m == "CT" and 0 <= cur_idx < len(ct_list)) else 0
    target = ct_list[ct_idx]

    lat_maps = target.get("mcnp_lattice_maps", {}) or {}
    if not lat_maps:
        QMessageBox.warning(
            self, "No Lattice Map",
            "No MCNP lattice maps found for this CT.\n"
            "Please click 'Create MCNP lattice map' first."
        )
        return

    # Select lattice map if multiple exist
    keys = list(lat_maps.keys())
    if len(keys) == 1:
        lat_map_name = keys[0]
    else:
        item, ok = QInputDialog.getItem(
            self, "Select MCNP lattice map", "Lattice map:", keys, len(keys) - 1, False
        )
        if not ok or not item:
            return
        lat_map_name = item

    # Ask user for destination file path
    default_name = f"{lat_map_name}.inp"
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Save MCNP Input File", default_name, "MCNP Input Files (*.inp);;All Files (*)"
    )
    if not file_path:
        return

    pb = getattr(self, "progressBar", None)
    prog = QProgressDialog("Generating MCNP input file...", None, 0, 100, self)
    prog.setWindowTitle("MCNP Input")
    prog.setWindowModality(Qt.WindowModality.ApplicationModal)
    prog.setMinimumDuration(0)
    prog.setValue(5)
    QApplication.processEvents()

    def update_prog(pct, text=None):
        if prog is not None:
            if text:
                prog.setLabelText(text)
            prog.setValue(pct)
        if pb is not None:
            pb.setValue(pct)
        QApplication.processEvents()

    try:
        cards, vox_info, grid_info = build_mcnp_cards(
            self, target, lat_map_name, progress_cb=update_prog
        )
        update_prog(95, "Writing file to disk...")
        with open(file_path, "w", encoding="utf-8", newline="\n") as f:
            for l in cards:
                f.write(l + "\n")
        update_prog(100, "Done")
    except Exception as e:
        prog.close()
        if pb is not None:
            pb.setValue(0)
        QMessageBox.critical(self, "Export Error", f"Failed to generate MCNP input:\n{e}")
        return
    finally:
        prog.close()
        if pb is not None:
            pb.setValue(0)

    lat_entry = target["mcnp_lattice_maps"][lat_map_name]
    n_uni = len(lat_entry.get("universes", []))
    dim_str = f"{vox_info['nc']} x {vox_info['nr']} x {vox_info['ns']}"

    QMessageBox.information(
        self, "MCNP Input Created",
        f"MCNP input file successfully generated:\n{file_path}\n\n"
        f"Total lines: {len(cards)} (all <= {MAX_COL} columns)\n"
        f"Phantom lattice dimensions: {dim_str} (cols x rows x slices)\n"
        f"Universes defined: {n_uni}"
    )
