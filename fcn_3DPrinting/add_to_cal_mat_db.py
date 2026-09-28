"""
"Add to 3DP Database..." - push ROI statistics measured in the View tab into the
3D-printing calibration tables.

Source: the View tab's circle-ROI tool. `c_roi_getdata` (fcn_processing/roi_circle.py)
fills `table_roi_c_values` with one row per ROI and, per active image layer, the
columns `Mean_L<n>`, `STD_L<n>`, `N_L<n>` (prefixed `S<series>_` when several
series are evaluated; in "vertical" layout column 0 holds the series label).
The user maps those layer sources to the roles HU-low / HU-high / RED / Zeff,
picks the kV pair (read from the series' DICOM KVP when possible) and a target
material or mix, previews the rows and commits them.
"""

import logging
import math
import re
from dataclasses import dataclass

from fcn_3DPrinting import db_schema as schema
from fcn_3DPrinting import material_props as props

logger = logging.getLogger("amigopy")

ROLES = ("hu_low", "hu_high", "red", "zeff")
ROLE_LABELS = {"hu_low": "HU (low kV)", "hu_high": "HU (high kV)", "red": "RED", "zeff": "Zeff"}
ROI_HEADER_RE = re.compile(r"^(?:(?P<series>S[^_]+)_)?(?P<stat>Mean|STD|N)_L(?P<layer>\d+)$")

PRINT_SETTING_FIELDS = ("Print Temp", "Bed Temp", "Infill Pattern", "Flow Multiplier", "Shape",
                        "Layer Height", "Line Width", "Print Speed")


def _tab():
    from fcn_init import create_3D_database_tab as m
    return m


# --------------------------------------------------------------------------- ROI table parsing

@dataclass
class RoiSource:
    key: str
    series_tag: str
    layer: int
    mean_col: int
    std_col: int
    n_col: int
    label: str


def _header_texts(table):
    texts = []
    for c in range(table.columnCount()):
        item = table.horizontalHeaderItem(c)
        texts.append(item.text().strip() if item is not None else "")
    return texts


def parse_roi_value_sources(table):
    """Return ([RoiSource], vertical_mode) for the ROI values table."""
    headers = _header_texts(table)
    vertical = bool(headers) and headers[0] == "Series"
    groups = {}
    for col, text in enumerate(headers):
        m = ROI_HEADER_RE.match(text)
        if not m:
            continue
        key = (m.group("series"), int(m.group("layer")))
        groups.setdefault(key, {})[m.group("stat").lower()] = col
    sources = []
    for (tag, layer), cols in sorted(groups.items(), key=lambda kv: (kv[0][0] or "", kv[0][1])):
        if "mean" not in cols:
            continue
        label = f"Layer {layer + 1} (L{layer})"
        if tag:
            label = f"{tag} - {label}"
        sources.append(RoiSource(
            key=f"{tag}_L{layer}" if tag else f"L{layer}", series_tag=tag, layer=layer,
            mean_col=cols["mean"], std_col=cols.get("std", -1), n_col=cols.get("n", -1), label=label,
        ))
    return sources, vertical


def _cell_float(table, r, c, default=0.0):
    if c < 0:
        return default
    item = table.item(r, c)
    return schema.to_float(item.text() if item is not None else None, default)


def read_roi_rows(table, sources, vertical_mode=False):
    """[{row, series_label, values: {source.key: {mean, std, n}}}] for every row of the ROI values table."""
    rows = []
    for r in range(table.rowCount()):
        values = {}
        for src in sources:
            values[src.key] = {
                "mean": _cell_float(table, r, src.mean_col),
                "std": _cell_float(table, r, src.std_col),
                "n": int(_cell_float(table, r, src.n_col, 0)),
            }
        series_label = None
        if vertical_mode:
            item = table.item(r, 0)
            series_label = item.text().strip() if item is not None else ""
        rows.append({"row": r, "series_label": series_label, "values": values})
    return rows


def default_role_assignment(sources, kvp_by_tag=None):
    """
    Guess which source feeds which role. One series: layers in order -> HU-low, HU-high,
    RED, Zeff (the app's convention). Several series each with a single layer: the
    lower-kVp series is HU-low.
    """
    roles = {role: None for role in ROLES}
    if not sources:
        return roles
    kvp_by_tag = kvp_by_tag or {}
    tags = []
    for src in sources:
        if src.series_tag not in tags:
            tags.append(src.series_tag)
    by_tag = {tag: sorted((s for s in sources if s.series_tag == tag), key=lambda s: s.layer) for tag in tags}

    if len(tags) > 1 and all(len(by_tag[t]) == 1 for t in tags):
        def sort_key(tag):
            kvp = kvp_by_tag.get(tag)
            return (0, kvp) if kvp is not None else (1, str(tag))
        ordered = sorted(tags, key=sort_key)
        roles["hu_low"] = by_tag[ordered[0]][0]
        roles["hu_high"] = by_tag[ordered[1]][0]
        return roles

    layers = by_tag[tags[0]]
    for role, src in zip(ROLES, layers):
        roles[role] = src
    return roles


# --------------------------------------------------------------------------- series / kVp lookup

def list_series_choices(self):
    """Loaded image series (as listed in the DECT combos) with their DICOM kVp when available."""
    choices = []
    info = getattr(self, "series_info_dict", None) or {}
    images = getattr(self, "medical_image", None) or {}
    for combo_index in sorted(info):
        try:
            label, patient_id, study_id, modality, item_index = info[combo_index]
        except (TypeError, ValueError):
            continue
        series = None
        try:
            series = images[patient_id][study_id][modality][item_index]
        except (KeyError, IndexError, TypeError):
            pass
        kvp = None
        series_number = None
        if isinstance(series, dict):
            series_number = series.get("SeriesNumber")
            dcm = (series.get("metadata") or {}).get("DCM_Info")
            if dcm is not None:
                try:
                    raw = dcm.get("KVP") if hasattr(dcm, "get") else getattr(dcm, "KVP", None)
                    if raw not in (None, ""):
                        kvp = float(raw)
                except (TypeError, ValueError):
                    kvp = None
        choices.append({
            "combo_index": combo_index, "label": label, "patient_id": patient_id, "study_id": study_id,
            "modality": modality, "item_index": item_index, "series_number": series_number, "kvp": kvp,
        })
    return choices


def kvp_by_series_tag(choices):
    """{'S<SeriesNumber>': kVp} for the prefixes c_roi_getdata uses in multi-series mode."""
    result = {}
    for ch in choices:
        if ch["series_number"] is not None and ch["kvp"] is not None:
            result[f"S{ch['series_number']}"] = ch["kvp"]
    return result


# --------------------------------------------------------------------------- DECT HU -> RED/Zeff

class DectFitUnavailable(Exception):
    pass


def _widget_text(self, name):
    widget = getattr(self, name, None)
    if widget is None:
        raise DectFitUnavailable("Open the DECT tab and fit the RED/Zeff calibration first.")
    try:
        text = widget.currentText() if hasattr(widget, "currentText") else widget.text()
    except RuntimeError as e:
        raise DectFitUnavailable("DECT widgets are not available.") from e
    return str(text).strip()


def _widget_float(self, name, what):
    text = _widget_text(self, name)
    try:
        return float(text.replace(",", "."))
    except ValueError:
        raise DectFitUnavailable(f"No fitted value for {what} in the DECT tab (field is '{text or 'empty'}').")


def get_dect_fit_parameters(self):
    """Read the fitted DECT model parameters from the DECT tab widgets (see fcn_DECT/create_process_dect.py)."""
    red_method = _widget_text(self, "RED_method_list")
    zeff_method = _widget_text(self, "Zeff_method_list")
    params = {"red_method": red_method, "zeff_method": zeff_method, "m": _widget_float(self, "Zeff_m", "m")}
    if red_method == "Saito":
        params.update(a=_widget_float(self, "RED_fit_01_text", "a"),
                      alpha=_widget_float(self, "RED_fit_02_text", "alpha"),
                      b=_widget_float(self, "RED_fit_03_text", "b"))
    elif red_method == "Hunemohr":
        params.update(ce=_widget_float(self, "RED_fit_01_text", "ce"))
    else:
        raise DectFitUnavailable(f"Unknown RED method '{red_method}'.")
    if zeff_method == "Saito":
        params.update(g=_widget_float(self, "Zeff_fit_01_text", "gamma"),
                      g0=_widget_float(self, "Zeff_fit_02_text", "gamma0"))
    elif zeff_method == "Hunemohr":
        params.update(de=_widget_float(self, "Zeff_fit_01_text", "de"))
    else:
        raise DectFitUnavailable(f"Unknown Zeff method '{zeff_method}'.")
    if params["m"] == 0:
        raise DectFitUnavailable("The Zeff exponent m is zero.")
    return params


def zeff_water(m):
    # water: Z/A(H) = 0.99212 (mass fraction 0.1111), Z/A(O) = 0.50002 (mass fraction 0.8889)
    return (((0.99212 * 0.1111 * 1 ** m) + (0.50002 * 0.8889 * 8 ** m))
            / ((0.99212 * 0.1111) + (0.50002 * 0.8889))) ** (1 / m)


def _root(value, m):
    """value ** (1/m) with numpy's nan_to_num semantics: negative base / non-finite -> 0.0."""
    if value is None or not math.isfinite(value) or value < 0:
        return 0.0
    result = value ** (1.0 / m)
    return result if math.isfinite(result) else 0.0


def red_zeff_from_hu(hu_low, hu_high, p):
    """
    Scalar transcription of creat_DECT_derived_maps (fcn_DECT/create_process_dect.py:45-113).
    The Hunemohr Zeff branch deliberately reuses Low/High as left by the *RED* branch,
    exactly like the matrix implementation does.
    """
    m = p["m"]
    zw = zeff_water(m)
    if p["red_method"] == "Saito":
        low = (hu_low * p["alpha"]) * p["a"] / 1000
        high = (hu_high * (1 + p["alpha"])) * p["a"] / 1000
        red = high - low + p["b"]
    else:
        low = hu_low / 1000 + 1
        high = hu_high / 1000 + 1
        red = low * p["ce"] + high * (1 - p["ce"])
    if not math.isfinite(red):
        red = 0.0
    if red == 0.0:
        return 0.0, 0.0
    if p["zeff_method"] == "Saito":
        zeff = _root(p["g"] * ((hu_low / 1000 + 1) / red - 1) + p["g0"] + 1, m) * zw
    else:
        z = low * p["de"] + high * (zw ** m - p["de"])
        zeff = _root(z / red, m)
    return red, (zeff if math.isfinite(zeff) else 0.0)


# --------------------------------------------------------------------------- row construction

def measurements_for_row(roi_row, roles, dect=None, propagate_std=False):
    """Resolve HU/RED/Zeff (mean, std) for one ROI row from the role mapping (and the DECT fit if requested)."""
    def stat(role):
        src = roles.get(role)
        if src is None:
            return 0.0, 0.0
        v = roi_row["values"].get(src.key, {})
        return v.get("mean", 0.0), v.get("std", 0.0)

    hu_low, hu_low_std = stat("hu_low")
    hu_high, hu_high_std = stat("hu_high")
    red, red_std = stat("red")
    zeff, zeff_std = stat("zeff")
    from_dect = False
    if dect is not None and roles.get("hu_low") is not None and roles.get("hu_high") is not None:
        red, zeff = red_zeff_from_hu(hu_low, hu_high, dect)
        from_dect = True
        if propagate_std:
            r_hi, z_hi = red_zeff_from_hu(hu_low + hu_low_std, hu_high + hu_high_std, dect)
            r_lo, z_lo = red_zeff_from_hu(hu_low - hu_low_std, hu_high - hu_high_std, dect)
            red_std, zeff_std = abs(r_hi - r_lo) / 2, abs(z_hi - z_lo) / 2
        else:
            red_std, zeff_std = 0.0, 0.0
    return {
        "hu_low": hu_low, "hu_low_std": hu_low_std, "hu_high": hu_high, "hu_high_std": hu_high_std,
        "red": red, "red_std": red_std, "zeff": zeff, "zeff_std": zeff_std, "from_dect": from_dect,
    }


def _per_row(per_row, roi_row):
    override = (per_row or {}).get(roi_row["row"], {})
    return (schema.to_float(override.get("infill", 100.0), 100.0),
            schema.to_float(override.get("flow", 100.0), 100.0),
            bool(override.get("use", True)))


def build_material_cal_rows(roi_rows, roles, kv_low, kv_high, settings, per_row=None, dect=None, propagate_std=False):
    rows = []
    for roi_row in roi_rows:
        infill, flow, use = _per_row(per_row, roi_row)
        if not use:
            continue
        mv = measurements_for_row(roi_row, roles, dect, propagate_std)
        data = {
            "kV_low": str(kv_low), "kV_hig": str(kv_high),
            "HU_low": mv["hu_low"], "HU_low_STD": mv["hu_low_std"], "HU_hig": mv["hu_high"], "HU_hig_STD": mv["hu_high_std"],
            "RED": mv["red"], "RED_STD": mv["red_std"], "Zeff": mv["zeff"], "Zeff STD": mv["zeff_std"],
            "Infill Density": infill, "Flow": flow,
        }
        data.update({k: v for k, v in (settings or {}).items() if k in schema.MATERIAL_CAL_FIELDS})
        rows.append(schema.dict_to_row(schema.MATERIAL_CAL_FIELDS, data, schema.MATERIAL_CAL_DEFAULTS, schema.MATERIAL_CAL_TEXT_IDX))
    return rows


def build_mix_cal_rows(roi_rows, roles, ratios, kv_low, kv_high, settings, per_row=None, dect=None, propagate_std=False):
    rows = []
    for roi_row in roi_rows:
        infill, flow, use = _per_row(per_row, roi_row)
        if not use:
            continue
        mv = measurements_for_row(roi_row, roles, dect, propagate_std)
        data = {
            "kV_low": str(kv_low), "kV_hig": str(kv_high),
            "HU_low": mv["hu_low"], "HU_low_STD": mv["hu_low_std"], "HU_hig": mv["hu_high"], "HU_hig_STD": mv["hu_high_std"],
            "RED": mv["red"], "RED_STD": mv["red_std"], "Zeff": mv["zeff"], "Zeff STD": mv["zeff_std"],
            "Infill Density": infill, "Flow": flow,
        }
        for key, value in (settings or {}).items():
            if key == "Infill Pattern":
                data["Infill Type"] = value
            elif key in schema.MIX_CAL_FIELDS:
                data[key] = value
        rows.append([schema.format_ratios(ratios)]
                    + schema.dict_to_row(schema.MIX_CAL_FIELDS, data, schema.MIX_CAL_DEFAULTS, schema.MIX_CAL_TEXT_IDX))
    return rows


def build_mix_red_rows(self, mix_id, ratios, roi_rows, roles, kv_low, kv_high, per_row=None, dect=None, propagate_std=False):
    rows = []
    pred_zeff = props.predict_mix_zeff_for(self, mix_id, ratios)
    for roi_row in roi_rows:
        infill, flow, use = _per_row(per_row, roi_row)
        if not use:
            continue
        mv = measurements_for_row(roi_row, roles, dect, propagate_std)
        data = {
            "Infill %": infill, "Flow": flow,
            "HU-Low": mv["hu_low"], "HU-Low STD": mv["hu_low_std"], "HU-High": mv["hu_high"], "HU-High STD": mv["hu_high_std"],
            "RED": mv["red"], "RED STD": mv["red_std"], "Pred. RED": props.predict_mix_red_for(self, mix_id, ratios, infill),
            "Zeff": mv["zeff"], "Zeff STD": mv["zeff_std"], "Pred. Zeff": pred_zeff,
            "kV - Low": schema.to_float(kv_low, 80.0), "kV - High": schema.to_float(kv_high, 140.0),
        }
        rows.append(schema.dict_to_row(schema.MIX_RED_FIELDS, data, schema.MIX_RED_DEFAULTS, schema.MIX_RED_TEXT_IDX))
    return rows


# --------------------------------------------------------------------------- commits

def commit_to_material(self, name, rows):
    m = _tab()
    viewing = getattr(self, "current_viewed_filament", None) == name
    if viewing:
        m.save_current_active_material_cache(self)
    self.calibration_data_cache.setdefault(name, []).extend(rows)
    m.save_calibration_database(self)
    if viewing:
        self.current_viewed_filament = None
        m.display_selected_filament_details(self)
    m.auto_save_all_databases(self)


def commit_to_mix_red(self, mix_id, combo_idx, rows):
    m = _tab()
    viewing = getattr(self, "current_viewed_mix_id", None) == mix_id
    if viewing:
        m.save_current_active_mix_cache(self)
    self.mix_red_cache[mix_id][combo_idx]["rows"].extend(rows)
    list_widget = getattr(self, "list_mix_red_ratios", None)
    if viewing and list_widget is not None and list_widget.currentRow() == combo_idx:
        m.display_selected_mix_red_ratio_details(self, combo_idx)
    m.save_mix_calibration_database(self)
    m.auto_save_all_databases(self)


def commit_to_mix_cal(self, mix_id, rows):
    m = _tab()
    viewing = getattr(self, "current_viewed_mix_id", None) == mix_id
    if viewing:
        m.save_current_active_mix_cache(self)
    self.mix_calibration_cache.setdefault(mix_id, []).extend(rows)
    m.save_mix_calibration_database(self)
    if viewing:
        start_row, _ = m.find_mix_group_row_and_size(self, mix_id)
        self.current_viewed_mix_id = None
        if start_row != -1:
            self.table_mat_mix.selectRow(start_row)
        m.display_selected_mix_details(self)
    m.auto_save_all_databases(self)


def last_material_settings(self, name):
    """Print settings of the material's most recent calibration row (to pre-fill the dialog)."""
    rows = (getattr(self, "calibration_data_cache", None) or {}).get(name, [])
    if not rows:
        return {}
    d = schema.row_to_dict(schema.MATERIAL_CAL_FIELDS, rows[-1])
    return {k: d[k] for k in PRINT_SETTING_FIELDS if k in d}


# --------------------------------------------------------------------------- dialog

def open_add_roi_to_3dp_dialog(self):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
                                   QComboBox, QDoubleSpinBox, QLineEdit, QCheckBox, QRadioButton, QPushButton,
                                   QTableWidget, QTableWidgetItem, QAbstractItemView)
    m = _tab()

    table = getattr(self, "table_roi_c_values", None)
    if table is None or table.rowCount() == 0:
        QMessageBox.warning(self, "No ROI data", "Draw circle ROIs in the View tab (ROI > Circles) and press 'Get Data' first.")
        return
    sources, vertical = parse_roi_value_sources(table)
    if not sources:
        QMessageBox.warning(self, "No ROI data", "The ROI values table has no Mean/STD columns; press 'Get Data' first.")
        return

    tab_modules = getattr(self, "tabModules", None)
    previous_tab = tab_modules.currentIndex() if tab_modules is not None else None
    if not m.ensure_3dp_tab_loaded(self):
        QMessageBox.warning(self, "Warning", "The 3D Printing tab could not be initialised.")
        return
    if tab_modules is not None and previous_tab is not None:
        tab_modules.setCurrentIndex(previous_tab)

    roi_rows = read_roi_rows(table, sources, vertical)
    series_choices = list_series_choices(self)
    roles = default_role_assignment(sources, kvp_by_series_tag(series_choices))
    try:
        dect = get_dect_fit_parameters(self)
        dect_reason = ""
    except DectFitUnavailable as e:
        dect, dect_reason = None, str(e)

    materials = sorted(props.get_material_db_map(self))
    mixes = props.list_mixes(self)

    dlg = QDialog(self)
    dlg.setWindowTitle("Add ROI data to the 3DP database")
    dlg.setMinimumSize(980, 720)
    dlg.setStyleSheet("""
        QDialog { background-color: #1e1e24; color: #ffffff; }
        QLabel, QCheckBox, QRadioButton { color: #e5e7eb; }
        QGroupBox { color: #3b82f6; font-weight: bold; border: 1px solid #3c4450; border-radius: 4px; margin-top: 10px; padding: 8px; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
        QComboBox, QDoubleSpinBox, QLineEdit { background-color: #2b2b36; border: 1px solid #4b5563; border-radius: 4px; color: #ffffff; padding: 3px; }
        QTableWidget { background-color: #1e1e24; color: #ffffff; border: 1px solid #3c4450; }
        QHeaderView::section { background-color: #2b2b36; color: #e5e7eb; padding: 4px; }
        QPushButton { font-weight: bold; padding: 6px 12px; border-radius: 4px; }
    """)
    layout = QVBoxLayout(dlg)

    # --- roles -----------------------------------------------------------------------------
    grp_roles = QGroupBox("1. Which ROI columns hold which quantity?")
    grid = QGridLayout(grp_roles)
    role_combos = {}
    for i, role in enumerate(ROLES):
        grid.addWidget(QLabel(ROLE_LABELS[role] + ":"), i // 2, (i % 2) * 2)
        combo = QComboBox()
        combo.addItem("(none)", None)
        for src in sources:
            combo.addItem(src.label, src.key)
        current = roles.get(role)
        combo.setCurrentIndex(combo.findData(current.key) if current is not None else 0)
        grid.addWidget(combo, i // 2, (i % 2) * 2 + 1)
        role_combos[role] = combo
    chk_dect = QCheckBox("Compute RED and Zeff from the HU pair with the DECT calibration"
                         + (f" ({dect['red_method']} / {dect['zeff_method']}, m = {dect['m']:g})" if dect else ""))
    chk_dect.setEnabled(dect is not None)
    if dect is None:
        chk_dect.setToolTip(dect_reason)
    chk_std = QCheckBox("Estimate RED/Zeff uncertainty from the HU standard deviations")
    chk_std.setEnabled(False)
    grid.addWidget(chk_dect, 2, 0, 1, 4)
    grid.addWidget(chk_std, 3, 0, 1, 4)
    if dect and dect["red_method"] != dect["zeff_method"]:
        lbl_mixed = QLabel("Note: the DECT tab uses different models for RED and Zeff; the Zeff formula reuses the RED "
                           "model's intermediate values, exactly like the DECT map calculation.")
        lbl_mixed.setWordWrap(True)
        lbl_mixed.setStyleSheet("color: #f59e0b;")
        grid.addWidget(lbl_mixed, 4, 0, 1, 4)
    layout.addWidget(grp_roles)

    # --- kV --------------------------------------------------------------------------------
    grp_kv = QGroupBox("2. Tube voltages")
    kv_grid = QGridLayout(grp_kv)
    kv_widgets = {}
    for i, (role, default) in enumerate((("hu_low", 80.0), ("hu_high", 140.0))):
        kv_grid.addWidget(QLabel(f"{ROLE_LABELS[role]} series:"), i, 0)
        combo = QComboBox()
        combo.addItem("Manual", None)
        for ch in series_choices:
            suffix = f"  [{ch['kvp']:g} kV]" if ch["kvp"] is not None else ""
            combo.addItem(f"{ch['label']}{suffix}", ch["combo_index"])
        kv_grid.addWidget(combo, i, 1)
        kv_grid.addWidget(QLabel("kV:"), i, 2)
        spin = QDoubleSpinBox()
        spin.setRange(0.0, 999.0)
        spin.setDecimals(1)
        spin.setValue(default)
        kv_grid.addWidget(spin, i, 3)
        kv_widgets[role] = (combo, spin)
    with_kvp = sorted((ch for ch in series_choices if ch["kvp"] is not None), key=lambda ch: ch["kvp"])
    if len(with_kvp) >= 2:
        kv_widgets["hu_low"][0].setCurrentIndex(kv_widgets["hu_low"][0].findData(with_kvp[0]["combo_index"]))
        kv_widgets["hu_high"][0].setCurrentIndex(kv_widgets["hu_high"][0].findData(with_kvp[-1]["combo_index"]))

    def on_series_picked(role):
        combo, spin = kv_widgets[role]
        idx = combo.currentData()
        for ch in series_choices:
            if ch["combo_index"] == idx and ch["kvp"] is not None:
                spin.setValue(ch["kvp"])
    for role in ("hu_low", "hu_high"):
        kv_widgets[role][0].currentIndexChanged.connect(lambda _i, r=role: on_series_picked(r))
        on_series_picked(role)
    layout.addWidget(grp_kv)

    # --- target ----------------------------------------------------------------------------
    grp_target = QGroupBox("3. Where should the rows go?")
    tgt = QGridLayout(grp_target)
    rb_material = QRadioButton("Material calibration table")
    rb_mix_red = QRadioButton("Mix - RED ratio combination (Mix RED tab)")
    rb_mix_cal = QRadioButton("Mix - main calibration table (Info / Z && RED tabs)")
    combo_material = QComboBox()
    combo_material.addItems(materials)
    current_mat = getattr(self, "current_viewed_filament", None)
    if current_mat in materials:
        combo_material.setCurrentText(current_mat)
    combo_mix = QComboBox()
    for mx in mixes:
        combo_mix.addItem(f"ID {mx['mix_id']} - {mx['name']} ({' / '.join(mx['components'])})", mx["mix_id"])
    current_mix = getattr(self, "current_viewed_mix_id", None)
    if current_mix is not None and combo_mix.findData(current_mix) >= 0:
        combo_mix.setCurrentIndex(combo_mix.findData(current_mix))
    combo_ratio = QComboBox()
    ratio_spins = []
    ratio_box = QHBoxLayout()

    def selected_mix_id():
        return combo_mix.currentData()

    def rebuild_mix_dependent():
        mix_id = selected_mix_id()
        combo_ratio.clear()
        while ratio_box.count():
            w = ratio_box.takeAt(0).widget()
            if w is not None:
                w.deleteLater()
        ratio_spins.clear()
        if mix_id is None:
            return
        names = next((mx["components"] for mx in mixes if mx["mix_id"] == mix_id), [])
        for idx, combo in enumerate((getattr(self, "mix_red_cache", None) or {}).get(mix_id, [])):
            combo_ratio.addItem(m.format_ratio_string(names, combo.get("percentage", [])), idx)
        for name in names:
            ratio_box.addWidget(QLabel(f"% {name}:"))
            spin = QDoubleSpinBox()
            spin.setRange(0.0, 100.0)
            spin.setDecimals(2)
            spin.setValue(100.0 / max(1, len(names)))
            ratio_box.addWidget(spin)
            ratio_spins.append(spin)
        if len(ratio_spins) >= 2:
            def sync_last():
                for sp in ratio_spins:
                    sp.blockSignals(True)
                ratio_spins[-1].setValue(max(0.0, 100.0 - sum(sp.value() for sp in ratio_spins[:-1])))
                for sp in ratio_spins:
                    sp.blockSignals(False)
                rebuild_preview()
            for sp in ratio_spins[:-1]:
                sp.valueChanged.connect(lambda _v: sync_last())
    combo_mix.currentIndexChanged.connect(lambda _i: (rebuild_mix_dependent(), rebuild_preview()))

    tgt.addWidget(rb_material, 0, 0)
    tgt.addWidget(combo_material, 0, 1)
    tgt.addWidget(rb_mix_red, 1, 0)
    tgt.addWidget(combo_mix, 1, 1)
    tgt.addWidget(QLabel("Ratio combination:"), 2, 0)
    tgt.addWidget(combo_ratio, 2, 1)
    tgt.addWidget(rb_mix_cal, 3, 0)
    tgt.addLayout(ratio_box, 3, 1)
    if current_mix is not None and current_mat is None:
        rb_mix_red.setChecked(True)
    else:
        rb_material.setChecked(True)
    if not materials:
        rb_material.setEnabled(False)
    if not mixes:
        rb_mix_red.setEnabled(False)
        rb_mix_cal.setEnabled(False)
    layout.addWidget(grp_target)

    # --- print settings --------------------------------------------------------------------
    grp_print = QGroupBox("4. Print settings applied to every new row")
    pg = QGridLayout(grp_print)
    setting_widgets = {}
    spec = (("Infill Pattern", "text", "Grid"), ("Shape", "text", "Cylinder"), ("Flow Multiplier", "num", 1.0),
            ("Print Temp", "num", 210.0), ("Bed Temp", "num", 60.0), ("Layer Height", "num", 0.2),
            ("Line Width", "num", 0.4), ("Print Speed", "num", 50.0))
    for i, (field_name, kind, default) in enumerate(spec):
        pg.addWidget(QLabel(field_name + ":"), i // 4, (i % 4) * 2)
        if kind == "text":
            w = QLineEdit(str(default))
        else:
            w = QDoubleSpinBox()
            w.setRange(0.0, 10000.0)
            w.setDecimals(4)
            w.setValue(default)
        pg.addWidget(w, i // 4, (i % 4) * 2 + 1)
        setting_widgets[field_name] = w

    def apply_settings_from(existing):
        for key, w in setting_widgets.items():
            if key in existing and str(existing[key]).strip():
                if isinstance(w, QLineEdit):
                    w.setText(str(existing[key]))
                else:
                    w.setValue(schema.to_float(existing[key], w.value()))
    apply_settings_from(last_material_settings(self, combo_material.currentText()))
    combo_material.currentTextChanged.connect(lambda name: (apply_settings_from(last_material_settings(self, name)), rebuild_preview()))
    layout.addWidget(grp_print)

    def current_settings():
        out = {}
        for key, w in setting_widgets.items():
            out[key] = w.text() if isinstance(w, QLineEdit) else w.value()
        return out

    # --- preview ---------------------------------------------------------------------------
    grp_prev = QGroupBox("5. Rows that will be added (Infill % and Flow % are editable per row)")
    pv = QVBoxLayout(grp_prev)
    preview = QTableWidget(0, 12)
    preview.setHorizontalHeaderLabels(["Use", "ROI row", "Series", "HU low", "+/-", "HU high", "+/-", "RED", "+/-", "Zeff", "+/-", "Infill % | Flow %"])
    preview.setSelectionMode(QAbstractItemView.NoSelection)
    pv.addWidget(preview)
    lbl_status = QLabel()
    lbl_status.setWordWrap(True)
    pv.addWidget(lbl_status)
    layout.addWidget(grp_prev, stretch=1)

    per_row = {rr["row"]: {"infill": 100.0, "flow": 100.0, "use": True} for rr in roi_rows}
    state = {"rebuilding": False}

    def current_roles():
        by_key = {s.key: s for s in sources}
        return {role: by_key.get(role_combos[role].currentData()) for role in ROLES}

    def active_dect():
        return dect if (dect is not None and chk_dect.isChecked()) else None

    def rebuild_preview():
        state["rebuilding"] = True
        try:
            roles_now = current_roles()
            d = active_dect()
            preview.setRowCount(0)
            missing = [ROLE_LABELS[r] for r in ("hu_low", "hu_high") if roles_now[r] is None]
            for rr in roi_rows:
                mv = measurements_for_row(rr, roles_now, d, chk_std.isChecked())
                r = preview.rowCount()
                preview.insertRow(r)
                use_item = QTableWidgetItem()
                use_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                use_item.setCheckState(Qt.Checked if per_row[rr["row"]]["use"] else Qt.Unchecked)
                preview.setItem(r, 0, use_item)
                cells = [str(rr["row"] + 1), rr["series_label"] or "",
                         f"{mv['hu_low']:.1f}", f"{mv['hu_low_std']:.1f}", f"{mv['hu_high']:.1f}", f"{mv['hu_high_std']:.1f}",
                         f"{mv['red']:.4f}" + (" *" if mv["from_dect"] else ""), f"{mv['red_std']:.4f}",
                         f"{mv['zeff']:.2f}" + (" *" if mv["from_dect"] else ""), f"{mv['zeff_std']:.2f}"]
                for c, text in enumerate(cells, start=1):
                    item = QTableWidgetItem(text)
                    item.setFlags(Qt.ItemIsEnabled)
                    preview.setItem(r, c, item)
                edit = QTableWidgetItem(f"{per_row[rr['row']]['infill']:g} | {per_row[rr['row']]['flow']:g}")
                preview.setItem(r, 11, edit)
            preview.resizeColumnsToContents()
            notes = []
            if missing:
                notes.append("No source selected for: " + ", ".join(missing) + " (those columns stay 0).")
            if d is not None:
                notes.append("* RED/Zeff computed from HU with the DECT calibration.")
            lbl_status.setText(" ".join(notes))
        finally:
            state["rebuilding"] = False

    def on_preview_changed(item):
        if state["rebuilding"]:
            return
        r = item.row()
        roi_index = roi_rows[r]["row"]
        if item.column() == 0:
            per_row[roi_index]["use"] = item.checkState() == Qt.Checked
        elif item.column() == 11:
            parts = [p.strip() for p in item.text().replace(";", "|").split("|")]
            if parts:
                per_row[roi_index]["infill"] = schema.to_float(parts[0], per_row[roi_index]["infill"])
            if len(parts) > 1:
                per_row[roi_index]["flow"] = schema.to_float(parts[1], per_row[roi_index]["flow"])
    preview.itemChanged.connect(on_preview_changed)

    def on_dect_toggled(checked):
        for role in ("red", "zeff"):
            role_combos[role].setEnabled(not checked)
        chk_std.setEnabled(checked)
        rebuild_preview()
    chk_dect.toggled.connect(on_dect_toggled)
    chk_std.toggled.connect(lambda _c: rebuild_preview())
    for combo in role_combos.values():
        combo.currentIndexChanged.connect(lambda _i: rebuild_preview())
    for rb in (rb_material, rb_mix_red, rb_mix_cal):
        rb.toggled.connect(lambda _c: rebuild_preview())

    rebuild_mix_dependent()
    rebuild_preview()

    # --- buttons ---------------------------------------------------------------------------
    buttons = QHBoxLayout()
    btn_ok = QPushButton("Add rows")
    btn_ok.setStyleSheet("background-color: #16a34a; color: white;")
    btn_cancel = QPushButton("Cancel")
    btn_cancel.setStyleSheet("background-color: #4b5563; color: white;")
    buttons.addStretch()
    buttons.addWidget(btn_ok)
    buttons.addWidget(btn_cancel)
    layout.addLayout(buttons)
    btn_cancel.clicked.connect(dlg.reject)

    def on_accept():
        roles_now = current_roles()
        d = active_dect()
        kv_low = kv_widgets["hu_low"][1].value()
        kv_high = kv_widgets["hu_high"][1].value()
        kv_low_text = f"{kv_low:g}"
        kv_high_text = f"{kv_high:g}"
        settings = current_settings()
        if not any(v["use"] for v in per_row.values()):
            QMessageBox.warning(dlg, "Nothing selected", "Tick at least one ROI row.")
            return
        try:
            if rb_material.isChecked():
                name = combo_material.currentText()
                if not name:
                    QMessageBox.warning(dlg, "No material", "Select a target material.")
                    return
                rows = build_material_cal_rows(roi_rows, roles_now, kv_low_text, kv_high_text, settings, per_row, d, chk_std.isChecked())
                commit_to_material(self, name, rows)
                target_desc = f"material '{name}'"
                land = ("tab_18", None)
            elif rb_mix_red.isChecked():
                mix_id = selected_mix_id()
                combo_idx = combo_ratio.currentData()
                if mix_id is None or combo_idx is None:
                    QMessageBox.warning(dlg, "No ratio combination",
                                        "Select a mix and a RED ratio combination (create one in the Mix RED tab first).")
                    return
                ratios = self.mix_red_cache[mix_id][combo_idx]["percentage"]
                rows = build_mix_red_rows(self, mix_id, ratios, roi_rows, roles_now, kv_low, kv_high, per_row, d, chk_std.isChecked())
                commit_to_mix_red(self, mix_id, combo_idx, rows)
                target_desc = f"mix {props.get_mix_name(self, mix_id)} - {combo_ratio.currentText()}"
                land = ("tab_27", combo_idx)
            else:
                mix_id = selected_mix_id()
                if mix_id is None or not ratio_spins:
                    QMessageBox.warning(dlg, "No mix", "Select a target mix.")
                    return
                ratios = [sp.value() for sp in ratio_spins]
                if abs(sum(ratios) - 100.0) > 0.001:
                    QMessageBox.warning(dlg, "Invalid ratios", f"The mixing percentages sum to {sum(ratios):.2f}% (must be 100%).")
                    return
                rows = build_mix_cal_rows(roi_rows, roles_now, ratios, kv_low_text, kv_high_text, settings, per_row, d, chk_std.isChecked())
                commit_to_mix_cal(self, mix_id, rows)
                target_desc = f"mix {props.get_mix_name(self, mix_id)} (main calibration table)"
                land = ("tab_27", None)
        except Exception as e:
            logger.exception("Adding ROI rows to the 3DP database failed")
            QMessageBox.critical(dlg, "Failed", f"The rows could not be added:\n{e}\n\nSee the log for details.")
            return
        dlg.accept()
        m.refresh_material_overview(self)
        m.refresh_mix_overview(self)
        try:
            if tab_modules is not None and hasattr(self, "tab_3DP"):
                tab_modules.setCurrentWidget(self.tab_3DP)
            sub_tab = getattr(self, land[0], None)
            if sub_tab is not None and hasattr(self, "D3"):
                self.D3.setCurrentWidget(sub_tab)
            if land[1] is not None and hasattr(self, "list_mix_red_ratios"):
                self.list_mix_red_ratios.setCurrentRow(land[1])
        except Exception:
            logger.exception("Could not switch to the 3D Printing tab after adding ROI rows")
        QMessageBox.information(self, "Rows added", f"{len(rows)} calibration row(s) were added to {target_desc}.")
    btn_ok.clicked.connect(on_accept)
    dlg.exec()
