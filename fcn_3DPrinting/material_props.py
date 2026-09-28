"""
Material / mix property model for the 3D-printing tab.

One implementation of the reference-value lookup ("MatMix table first, then the
material database"), the mixing-rule predictors, and the summaries that feed
the read-only Overview panels. The main window is passed as `self`, and
fcn_init.create_3D_database_tab is imported inside functions to avoid an
import cycle (that module imports this one at load time).
"""

import html
from dataclasses import dataclass

from fcn_3DPrinting import db_schema as schema


@dataclass
class RefValue:
    value: float
    std: float
    source: str  # "matmix" | "database" | "missing"

    @property
    def is_missing(self):
        return self.source == "missing" or self.value == 0.0


def _tab():
    from fcn_init import create_3D_database_tab as m
    return m


# --------------------------------------------------------------------------- lookups

def get_material_db_map(self):
    """{material name: {row, brand, type, color, printer, date, red, red_std, zeff, zeff_std}} from table_3d_db."""
    m = _tab()
    result = {}
    table = getattr(self, "table_3d_db", None)
    if table is None:
        return result
    for r in range(table.rowCount()):
        name = m.safe_get_cell_text(table, r, 0).strip()
        if not name or name in result:
            continue
        result[name] = {
            "row": r,
            "brand": m.safe_get_cell_text(table, r, 1),
            "type": m.safe_get_cell_text(table, r, 2),
            "color": m.safe_get_cell_text(table, r, 3),
            "printer": m.safe_get_cell_text(table, r, 4),
            "date": m.safe_get_cell_text(table, r, 5),
            "red": schema.to_float(m.safe_get_cell_text(table, r, 6)),
            "red_std": schema.to_float(m.safe_get_cell_text(table, r, 7)),
            "zeff": schema.to_float(m.safe_get_cell_text(table, r, 8)),
            "zeff_std": schema.to_float(m.safe_get_cell_text(table, r, 9)),
        }
    return result


def get_material_reference_values(self, name):
    info = get_material_db_map(self).get(name)
    if info is None:
        return {"red": RefValue(0.0, 0.0, "missing"), "zeff": RefValue(0.0, 0.0, "missing")}
    return {
        "red": RefValue(info["red"], info["red_std"], "database" if info["red"] != 0.0 else "missing"),
        "zeff": RefValue(info["zeff"], info["zeff_std"], "database" if info["zeff"] != 0.0 else "missing"),
    }


def get_mix_group(self, mix_id):
    return _tab().find_mix_group_row_and_size(self, mix_id)


def get_mix_name(self, mix_id):
    m = _tab()
    start_row, _ = get_mix_group(self, mix_id)
    if start_row != -1:
        name = m.safe_get_cell_text(self.table_mat_mix, start_row, 2).strip()
        if name:
            return name
    return f"Mix {mix_id}"


def list_mixes(self):
    """[{mix_id, name, components:[names]}] for every group in table_mat_mix, in table order."""
    m = _tab()
    table = getattr(self, "table_mat_mix", None)
    if table is None:
        return []
    from PySide6.QtWidgets import QSpinBox
    mixes = []
    r = 0
    while r < table.rowCount():
        spin = table.cellWidget(r, 0)
        if isinstance(spin, QSpinBox) and spin.property("mix_id") is not None:
            size = max(1, spin.value())
            mix_id = spin.property("mix_id")
            mixes.append({
                "mix_id": mix_id,
                "name": get_mix_name(self, mix_id),
                "components": m.get_materials_in_mix(self, r, size),
            })
            r += size
        else:
            r += 1
    return mixes


def get_mix_components(self, mix_id):
    """
    Per component of a mix: {row, name, red: RefValue, zeff: RefValue}.
    Reference values come from the MatMix table (cols 3/4) and fall back to the
    material database (cols 6/8) when empty or zero - the single implementation of
    the rule that used to be copied in five places.
    """
    m = _tab()
    start_row, group_size = get_mix_group(self, mix_id)
    if start_row == -1:
        return []
    db_map = get_material_db_map(self)
    components = []
    for i in range(group_size):
        r = start_row + i
        if r >= self.table_mat_mix.rowCount():
            break
        name = m.safe_get_combo_text(self.table_mat_mix.cellWidget(r, 1)).strip()
        db_info = db_map.get(name)

        red_text = m.safe_get_cell_text(self.table_mat_mix, r, 3).strip()
        zeff_text = m.safe_get_cell_text(self.table_mat_mix, r, 4).strip()
        red = RefValue(schema.to_float(red_text), 0.0, "matmix") if red_text else RefValue(0.0, 0.0, "missing")
        zeff = RefValue(schema.to_float(zeff_text), 0.0, "matmix") if zeff_text else RefValue(0.0, 0.0, "missing")
        if red.value == 0.0 and db_info is not None:
            red = RefValue(db_info["red"], db_info["red_std"], "database" if db_info["red"] != 0.0 else "missing")
        elif db_info is not None:
            red.std = db_info["red_std"]
        if zeff.value == 0.0 and db_info is not None:
            zeff = RefValue(db_info["zeff"], db_info["zeff_std"], "database" if db_info["zeff"] != 0.0 else "missing")
        elif db_info is not None:
            zeff.std = db_info["zeff_std"]
        if red.value == 0.0:
            red.source = "missing"
        if zeff.value == 0.0:
            zeff.source = "missing"
        components.append({"row": r, "name": name, "red": red, "zeff": zeff})
    return components


def get_mix_component_reference_values(self, mix_id):
    """(reference REDs, reference Zeffs) aligned with the mix rows, or (None, None) if the mix is not in the table."""
    if mix_id is None:
        return None, None
    components = get_mix_components(self, mix_id)
    if not components:
        return None, None
    return [c["red"].value for c in components], [c["zeff"].value for c in components]


def get_mix_m_value(self, mix_id):
    cache = getattr(self, "mix_m_value_cache", None) or {}
    return cache.get(mix_id, 3.4)


# --------------------------------------------------------------------------- predictors

def predict_mix_red(comp_reds, percentages):
    """Mass-weighted mean of the component reference REDs."""
    total = 0.0
    for idx, pct in enumerate(percentages):
        if idx < len(comp_reds):
            total += (pct / 100.0) * comp_reds[idx]
    return total


def predict_mix_zeff(comp_zeffs, percentages, m):
    """Mayneord power-law mixing rule: (sum_i Zeff_i^m * w_i)^(1/m)."""
    if not m:
        return 0.0
    term_sum = 0.0
    for idx, pct in enumerate(percentages):
        if idx < len(comp_zeffs):
            term_sum += (comp_zeffs[idx] ** m) * (pct / 100.0)
    if term_sum <= 0.0:
        return 0.0
    return term_sum ** (1.0 / m)


def fit_red_vs_infill(points):
    """Least-squares line through (infill %, RED) points; None unless >= 2 distinct infill values."""
    points = [(float(x), float(y)) for x, y in points]
    if len({p[0] for p in points}) < 2:
        return None
    n = len(points)
    sum_x = sum(p[0] for p in points)
    sum_y = sum(p[1] for p in points)
    sum_xx = sum(p[0] ** 2 for p in points)
    sum_xy = sum(p[0] * p[1] for p in points)
    denominator = n * sum_xx - sum_x ** 2
    if abs(denominator) <= 1e-5:
        return None
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    return {"slope": slope, "intercept": intercept, "n": n}


def predict_mix_red_for(self, mix_id, ratios, infill_pct=100.0):
    """Predicted RED of a mix at a given infill, from each component's measured RED-vs-infill trend."""
    if mix_id is None:
        return 0.0
    m = _tab()
    components = get_mix_components(self, mix_id)
    if not components:
        return 0.0
    expected = [m.get_expected_material_red(self, c["name"], c["red"].value, infill_pct) for c in components]
    return predict_mix_red(expected, ratios)


def predict_mix_zeff_for(self, mix_id, ratios):
    if mix_id is None:
        return 0.0
    components = get_mix_components(self, mix_id)
    if not components:
        return 0.0
    return predict_mix_zeff([c["zeff"].value for c in components], ratios, get_mix_m_value(self, mix_id))


# --------------------------------------------------------------------------- summaries

def _numeric_row(fields, row, text_idx):
    d = schema.row_to_dict(fields, row)
    for i, name in enumerate(fields):
        if i not in text_idx:
            d[name] = schema.to_float(d[name])
    return d


def _mean_std(values):
    if not values:
        return None
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    return {"mean": mean, "std": var ** 0.5, "n": n}


def summarize_material(self, name):
    info = get_material_db_map(self).get(name, {})
    ref = get_material_reference_values(self, name)
    raw_rows = (getattr(self, "calibration_data_cache", None) or {}).get(name, [])
    cal_rows = [_numeric_row(schema.MATERIAL_CAL_FIELDS, r, schema.MATERIAL_CAL_TEXT_IDX) for r in raw_rows]

    red_vs_infill = [(r["Infill Density"], r["RED"], r["RED_STD"]) for r in cal_rows if r["RED"] > 0.0]
    at_100 = [r for r in cal_rows if abs(r["Infill Density"] - 100.0) < 1e-6]
    cal_red_100 = _mean_std([r["RED"] for r in at_100 if r["RED"] > 0.0])
    cal_zeff_100 = _mean_std([r["Zeff"] for r in at_100 if r["Zeff"] > 0.0])
    used_in = [mx for mx in list_mixes(self) if name in mx["components"]]
    notes = (getattr(self, "notes_cache", None) or {}).get(name, "") or ""

    warnings = []
    if ref["red"].is_missing:
        warnings.append("No reference RED in the material database.")
    if ref["zeff"].is_missing:
        warnings.append("No reference Zeff in the material database.")
    if not cal_rows:
        warnings.append("No calibration measurements recorded.")
    if cal_red_100 and not ref["red"].is_missing:
        dev = abs(cal_red_100["mean"] - ref["red"].value) / ref["red"].value * 100.0
        if dev > 2.0:
            warnings.append(f"Calibration RED at 100% infill ({cal_red_100['mean']:.4f}) deviates "
                            f"{dev:.1f}% from the reference RED ({ref['red'].value:.4f}).")
    no_hu = sum(1 for r in cal_rows if r["HU_low"] == 0.0 and r["HU_hig"] == 0.0)
    if no_hu:
        warnings.append(f"{no_hu} calibration row(s) have no HU values yet.")

    return {
        "name": name,
        "brand": info.get("brand", ""), "type": info.get("type", ""), "color": info.get("color", ""),
        "printer": info.get("printer", ""), "date": info.get("date", ""),
        "red": ref["red"], "zeff": ref["zeff"],
        "n_cal_rows": len(cal_rows), "cal_rows": cal_rows,
        "infill_levels": sorted({round(r["Infill Density"], 2) for r in cal_rows}),
        "kv_pairs": sorted({(str(r["kV_low"]), str(r["kV_hig"])) for r in cal_rows}),
        "red_vs_infill": red_vs_infill,
        "red_fit": fit_red_vs_infill([(x, y) for x, y, _ in red_vs_infill]),
        "cal_red_at_100": cal_red_100, "cal_zeff_at_100": cal_zeff_100,
        "used_in_mixes": used_in,
        "notes_preview": notes[:300] + ("..." if len(notes) > 300 else ""),
        "warnings": warnings,
    }


def summarize_mix(self, mix_id):
    m = _tab()
    components = get_mix_components(self, mix_id)
    names = [c["name"] for c in components]
    comp_reds = [c["red"].value for c in components]
    comp_zeffs = [c["zeff"].value for c in components]
    m_value = get_mix_m_value(self, mix_id)

    cal_rows = []
    for raw in (getattr(self, "mix_calibration_cache", None) or {}).get(mix_id, []):
        ratios = schema.parse_ratios(raw[0]) if raw else []
        row = _numeric_row(schema.MIX_CAL_FIELDS, raw[1:], schema.MIX_CAL_TEXT_IDX)
        row["ratios"] = ratios
        row["pred_red"] = predict_mix_red(comp_reds, ratios)
        row["pred_zeff"] = predict_mix_zeff(comp_zeffs, ratios, m_value)
        row["diff_red"] = row["RED"] - row["pred_red"]
        row["diff_zeff"] = row["Zeff"] - row["pred_zeff"]
        cal_rows.append(row)

    combos = []
    for combo in (getattr(self, "mix_red_cache", None) or {}).get(mix_id, []):
        pct = list(combo.get("percentage", []))
        rows = []
        for raw in combo.get("rows", []):
            row = _numeric_row(schema.MIX_RED_FIELDS, raw, schema.MIX_RED_TEXT_IDX)
            row["pred_red"] = predict_mix_red_for(self, mix_id, pct, row["Infill %"])
            row["pred_zeff"] = predict_mix_zeff_for(self, mix_id, pct)
            rows.append(row)
        combos.append({
            "percentage": pct,
            "label": m.format_ratio_string(names, pct) if names else ", ".join(f"{p:g}%" for p in pct),
            "n_rows": len(rows), "rows": rows,
        })

    notes = (getattr(self, "mix_notes_cache", None) or {}).get(mix_id, "") or ""
    warnings = []
    for c in components:
        if not c["name"] or c["name"].startswith("Material "):
            warnings.append(f"Component row {c['row'] + 1} has no material assigned.")
        else:
            if c["red"].is_missing:
                warnings.append(f"{c['name']}: no reference RED available.")
            if c["zeff"].is_missing:
                warnings.append(f"{c['name']}: no reference Zeff available.")
    for i, row in enumerate(cal_rows, start=1):
        total = sum(row["ratios"])
        if abs(total - 100.0) > 0.001:
            warnings.append(f"Calibration row {i}: mixing percentages sum to {total:.2f}% (must be 100%).")
    for combo in combos:
        total = sum(combo["percentage"])
        if abs(total - 100.0) > 0.001:
            warnings.append(f"Ratio combination {combo['label']}: percentages sum to {total:.2f}%.")
        if combo["n_rows"] == 0:
            warnings.append(f"Ratio combination {combo['label']} has no measurements yet.")
    if not cal_rows and not combos:
        warnings.append("No calibration measurements recorded for this mix.")

    return {
        "mix_id": mix_id, "name": get_mix_name(self, mix_id), "m_value": m_value,
        "components": components, "n_cal_rows": len(cal_rows), "cal_rows": cal_rows,
        "red_ratio_combos": combos,
        "notes_preview": notes[:300] + ("..." if len(notes) > 300 else ""),
        "warnings": warnings,
    }


# --------------------------------------------------------------------------- HTML rendering (Qt rich-text subset)

_TEXT = "#e5e7eb"
_MUTED = "#9ca3af"
_ACCENT = "#3b82f6"
_OK = "#10b981"
_WARN = "#ef4444"
_CELL_BG = "#2b2b36"


def _e(value):
    return html.escape(str(value))


def _f(value, digits=4):
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return _e(value)


def _ref_html(ref, digits=4):
    if ref.is_missing:
        return f'<span style="color:{_WARN}">missing</span>'
    std = f" &plusmn; {_f(ref.std, digits)}" if ref.std else ""
    badge = {"matmix": "MatMix table", "database": "material database"}.get(ref.source, ref.source)
    return f'{_f(ref.value, digits)}{std} <span style="color:{_MUTED}">({_e(badge)})</span>'


def _delta_html(value, digits=4):
    color = _OK if abs(value) < 1e-9 else (_ACCENT if value > 0 else _WARN)
    return f'<span style="color:{color}">{value:+.{digits}f}</span>'


def _warnings_html(warnings):
    if not warnings:
        return f'<p style="color:{_OK}">No issues detected.</p>'
    items = "".join(f"<li>{_e(w)}</li>" for w in warnings)
    return (f'<table width="100%" cellpadding="6" bgcolor="#2d1f22"><tr><td style="color:{_WARN}">'
            f"<b>Attention</b><ul>{items}</ul></td></tr></table>")


def _table_html(headers, rows):
    head = "".join(f'<th align="left" style="color:{_ACCENT}">{_e(h)}</th>' for h in headers)
    body = "".join("<tr>" + "".join(f'<td bgcolor="{_CELL_BG}">{cell}</td>' for cell in row) + "</tr>" for row in rows)
    return f'<table width="100%" cellpadding="4" cellspacing="1"><tr>{head}</tr>{body}</table>'


def _section(title):
    return f'<h3 style="color:{_ACCENT}">{_e(title)}</h3>'


def render_material_overview_html(s):
    parts = [f'<h2 style="color:{_TEXT}">{_e(s["name"])}</h2>']
    meta = " &nbsp;|&nbsp; ".join(
        f"<b>{label}:</b> {_e(s[key]) or '-'}"
        for label, key in (("Brand", "brand"), ("Type", "type"), ("Color", "color"), ("Printer", "printer"), ("Date", "date"))
    )
    parts.append(f'<p style="color:{_MUTED}">{meta}</p>')
    parts.append(_section("Reference values"))
    parts.append(_table_html(["Property", "Value"], [
        ["RED", _ref_html(s["red"])], ["Zeff", _ref_html(s["zeff"], 2)],
    ]))
    parts.append(_section("Status"))
    parts.append(_warnings_html(s["warnings"]))

    parts.append(_section("Calibration measurements"))
    facts = [["Rows", str(s["n_cal_rows"])]]
    if s["infill_levels"]:
        facts.append(["Infill levels (%)", ", ".join(f"{v:g}" for v in s["infill_levels"])])
    if s["kv_pairs"]:
        facts.append(["kV pairs", ", ".join(f"{lo}/{hi}" for lo, hi in s["kv_pairs"])])
    if s["cal_red_at_100"]:
        c = s["cal_red_at_100"]
        facts.append(["RED @ 100% infill", f"{c['mean']:.4f} &plusmn; {c['std']:.4f} (n={c['n']})"])
    if s["cal_zeff_at_100"]:
        c = s["cal_zeff_at_100"]
        facts.append(["Zeff @ 100% infill", f"{c['mean']:.2f} &plusmn; {c['std']:.2f} (n={c['n']})"])
    if s["red_fit"]:
        fit = s["red_fit"]
        facts.append(["RED vs infill fit", f"RED = {fit['slope']:.5f} &middot; infill + {fit['intercept']:.4f} (n={fit['n']})"])
    parts.append(_table_html(["Item", "Value"], facts))

    if s["cal_rows"]:
        rows = []
        for r in s["cal_rows"]:
            rows.append([
                f"{_e(r['kV_low'])}/{_e(r['kV_hig'])}", f"{r['Infill Density']:g}", f"{r['Flow']:g}",
                f"{_f(r['HU_low'], 1)} &plusmn; {_f(r['HU_low_STD'], 1)}",
                f"{_f(r['HU_hig'], 1)} &plusmn; {_f(r['HU_hig_STD'], 1)}",
                f"{_f(r['RED'])} &plusmn; {_f(r['RED_STD'])}",
                f"{_f(r['Zeff'], 2)} &plusmn; {_f(r['Zeff STD'], 2)}",
            ])
        parts.append(_table_html(["kV", "Infill %", "Flow %", "HU low", "HU high", "RED", "Zeff"], rows))

    parts.append(_section("Used in mixes"))
    if s["used_in_mixes"]:
        parts.append("<p>" + ", ".join(f"{_e(mx['name'])} (ID {mx['mix_id']})" for mx in s["used_in_mixes"]) + "</p>")
    else:
        parts.append(f'<p style="color:{_MUTED}">Not used in any mix.</p>')

    parts.append(_section("Notes"))
    parts.append(f'<p style="color:{_MUTED}">{_e(s["notes_preview"]) or "-"}</p>')
    return "".join(parts)


def render_mix_overview_html(s):
    parts = [f'<h2 style="color:{_TEXT}">{_e(s["name"])} <span style="color:{_MUTED}">(mix ID {s["mix_id"]})</span></h2>']
    parts.append(f'<p style="color:{_MUTED}"><b>Zeff mixing exponent m:</b> {s["m_value"]:.2f}</p>')

    parts.append(_section("Components"))
    parts.append(_table_html(["Material", "Reference RED", "Reference Zeff"], [
        [_e(c["name"]) or f'<span style="color:{_WARN}">unassigned</span>', _ref_html(c["red"]), _ref_html(c["zeff"], 2)]
        for c in s["components"]
    ]))
    parts.append(_section("Status"))
    parts.append(_warnings_html(s["warnings"]))

    parts.append(_section("Calibration rows (Info / Z &amp; RED)"))
    if s["cal_rows"]:
        rows = []
        for r in s["cal_rows"]:
            rows.append([
                " / ".join(f"{p:g}" for p in r["ratios"]), f"{r['Infill Density']:g}",
                f"{_f(r['RED'])}", f"{_f(r['pred_red'])}", _delta_html(r["diff_red"]),
                f"{_f(r['Zeff'], 2)}", f"{_f(r['pred_zeff'], 2)}", _delta_html(r["diff_zeff"], 2),
            ])
        parts.append(_table_html(["Ratios %", "Infill %", "RED", "Pred. RED", "&Delta;RED", "Zeff", "Pred. Zeff", "&Delta;Zeff"], rows))
    else:
        parts.append(f'<p style="color:{_MUTED}">None.</p>')

    parts.append(_section("RED ratio combinations (Mix RED)"))
    if s["red_ratio_combos"]:
        for combo in s["red_ratio_combos"]:
            parts.append(f'<p><b>{_e(combo["label"])}</b> &nbsp;<span style="color:{_MUTED}">{combo["n_rows"]} measurement(s)</span></p>')
            if combo["rows"]:
                rows = []
                for r in combo["rows"]:
                    rows.append([
                        f"{r['Infill %']:g}", f"{r['Flow']:g}",
                        f"{_f(r['RED'])}", f"{_f(r['pred_red'])}", _delta_html(r["RED"] - r["pred_red"]),
                        f"{_f(r['Zeff'], 2)}", f"{_f(r['pred_zeff'], 2)}", _delta_html(r["Zeff"] - r["pred_zeff"], 2),
                    ])
                parts.append(_table_html(["Infill %", "Flow %", "RED", "Pred. RED", "&Delta;RED", "Zeff", "Pred. Zeff", "&Delta;Zeff"], rows))
    else:
        parts.append(f'<p style="color:{_MUTED}">None.</p>')

    parts.append(_section("Notes"))
    parts.append(f'<p style="color:{_MUTED}">{_e(s["notes_preview"]) or "-"}</p>')
    return "".join(parts)
