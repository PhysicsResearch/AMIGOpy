"""
Versioned JSON packages for moving single materials or mixes between AMIGOpy
installations (File > Import / Export > "3DP Material/Mix Package").

A package is self-describing: calibration rows are keyed by the canonical CSV
header names from db_schema, a mix carries its component materials' reference
values so they can be re-created on a machine that lacks them, and mix ids are
always re-assigned on import. Importing never touches the on-disk database
schema; a snapshot is taken before anything is written.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime

from fcn_3DPrinting import db_schema as schema
from fcn_3DPrinting import material_props as props
from fcn_3DPrinting.safe_io import atomic_write_json

logger = logging.getLogger("amigopy")

SCHEMA_VERSION = 1
PACKAGE_KIND = "amigopy.3dp.package"
PACKAGE_EXTENSION = ".amigo3dp.json"
PACKAGE_FILTER = "AMIGOpy 3DP package (*.amigo3dp.json *.json);;All files (*)"

CONFLICT_MODES = ("rename", "skip", "overwrite")


class PackageError(Exception):
    pass


def _tab():
    from fcn_init import create_3D_database_tab as m
    return m


# --------------------------------------------------------------------------- building

def _material_dict(info, name):
    return {
        "name": name,
        "brand": info.get("brand", ""), "type": info.get("type", ""), "color": info.get("color", ""),
        "printer": info.get("printer", ""), "date": info.get("date", ""),
        "red": info.get("red", 0.0), "red_std": info.get("red_std", 0.0),
        "zeff": info.get("zeff", 0.0), "zeff_std": info.get("zeff_std", 0.0),
    }


def build_material_item(self, name, include_calibration=True, include_notes=True):
    info = props.get_material_db_map(self).get(name)
    if info is None:
        raise PackageError(f"Material '{name}' was not found in the database.")
    cal_rows = (getattr(self, "calibration_data_cache", None) or {}).get(name, []) if include_calibration else []
    notes = (getattr(self, "notes_cache", None) or {}).get(name, "") if include_notes else ""
    return {
        "kind": "material",
        "material": _material_dict(info, name),
        "notes": notes or "",
        "calibration": [schema.row_to_dict(schema.MATERIAL_CAL_FIELDS, row) for row in cal_rows],
    }


def build_mix_item(self, mix_id, include_component_calibration=False):
    components = props.get_mix_components(self, mix_id)
    if not components:
        raise PackageError(f"Mix {mix_id} was not found in the MatMix table.")
    db_map = props.get_material_db_map(self)
    comp_items = []
    for comp in components:
        info = db_map.get(comp["name"], {})
        reference = _material_dict(info, comp["name"])
        # the MatMix table may carry values the database lacks - keep whichever is populated
        if reference["red"] == 0.0:
            reference["red"] = comp["red"].value
        if reference["zeff"] == 0.0:
            reference["zeff"] = comp["zeff"].value
        entry = {"name": comp["name"], "reference": reference}
        if include_component_calibration and comp["name"] in db_map:
            mat_item = build_material_item(self, comp["name"])
            entry["calibration"] = mat_item["calibration"]
            entry["notes"] = mat_item["notes"]
        comp_items.append(entry)

    cal_rows = []
    for raw in (getattr(self, "mix_calibration_cache", None) or {}).get(mix_id, []):
        row = {"ratios": schema.parse_ratios(raw[0]) if raw else []}
        row.update(schema.row_to_dict(schema.MIX_CAL_FIELDS, raw[1:]))
        cal_rows.append(row)
    combos = [
        {"percentage": list(combo.get("percentage", [])),
         "rows": [schema.row_to_dict(schema.MIX_RED_FIELDS, r) for r in combo.get("rows", [])]}
        for combo in (getattr(self, "mix_red_cache", None) or {}).get(mix_id, [])
    ]
    return {
        "kind": "mix",
        "mix": {"name": props.get_mix_name(self, mix_id), "m_value": props.get_mix_m_value(self, mix_id),
                "source_mix_id": mix_id},
        "components": comp_items,
        "notes": (getattr(self, "mix_notes_cache", None) or {}).get(mix_id, "") or "",
        "calibration": cal_rows,
        "red_ratio_combos": combos,
    }


def build_package(items):
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": PACKAGE_KIND,
        "generator": {"app": "AMIGOpy", "exported_at": datetime.now().isoformat(timespec="seconds")},
        "items": list(items),
    }


def write_package(path, pkg):
    atomic_write_json(path, pkg, indent=2)


def read_package(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            pkg = json.load(f)
    except (OSError, ValueError) as e:
        raise PackageError(f"The file could not be read as a package: {e}") from e
    errors = validate_package(pkg)
    if errors:
        raise PackageError("Invalid package:\n- " + "\n- ".join(errors))
    return pkg


def validate_package(pkg):
    errors = []
    if not isinstance(pkg, dict):
        return ["The file does not contain a JSON object."]
    if pkg.get("kind") != PACKAGE_KIND:
        errors.append(f"Not an AMIGOpy 3DP package (kind = {pkg.get('kind')!r}).")
    version = pkg.get("schema_version")
    if not isinstance(version, int):
        errors.append("Missing schema_version.")
    elif version > SCHEMA_VERSION:
        logger.warning("Package schema version %s is newer than supported (%s); importing anyway", version, SCHEMA_VERSION)
    items = pkg.get("items")
    if not isinstance(items, list) or not items:
        errors.append("The package contains no items.")
        return errors
    for i, item in enumerate(items, start=1):
        kind = item.get("kind") if isinstance(item, dict) else None
        if kind == "material":
            if not str((item.get("material") or {}).get("name", "")).strip():
                errors.append(f"Item {i}: material without a name.")
        elif kind == "mix":
            comps = item.get("components")
            if not isinstance(comps, list) or not comps:
                errors.append(f"Item {i}: mix without components.")
            elif any(not str(c.get("name", "")).strip() for c in comps if isinstance(c, dict)):
                errors.append(f"Item {i}: mix component without a name.")
        else:
            errors.append(f"Item {i}: unknown item kind {kind!r}.")
    return errors


# --------------------------------------------------------------------------- planning

@dataclass
class ImportAction:
    index: int
    kind: str            # "material" | "mix"
    source_name: str
    action: str          # "add" | "skip" | "overwrite" | "rename"
    new_name: str = None
    existing_id: int = None   # mix id of the conflicting mix (for overwrite)
    synthesized: bool = False  # material created from a mix component's reference values


@dataclass
class ImportPlan:
    actions: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


def _unique_material_name(base, taken):
    n = 1
    while True:
        candidate = f"{base} (imported {n})"
        if candidate.strip().lower() not in taken:
            return candidate
        n += 1


def plan_import(self, pkg, conflict_mode="rename"):
    if conflict_mode not in CONFLICT_MODES:
        raise ValueError(f"conflict_mode must be one of {CONFLICT_MODES}")
    plan = ImportPlan()
    taken = {name.strip().lower() for name in props.get_material_db_map(self)}
    existing_mixes = {(mx["name"].strip().lower(), tuple(sorted(mx["components"]))): mx["mix_id"]
                      for mx in props.list_mixes(self)}
    planned_materials = set()

    def plan_material(index, name, synthesized=False):
        key = name.strip().lower()
        if key in planned_materials:
            return
        if key in taken:
            if synthesized:
                return  # component already exists locally - nothing to do
            if conflict_mode == "rename":
                new_name = _unique_material_name(name, taken | planned_materials)
                plan.actions.append(ImportAction(index, "material", name, "rename", new_name=new_name))
                planned_materials.add(new_name.strip().lower())
            else:
                plan.actions.append(ImportAction(index, "material", name, conflict_mode))
        else:
            plan.actions.append(ImportAction(index, "material", name, "add", synthesized=synthesized))
            planned_materials.add(key)
            if synthesized:
                plan.warnings.append(f"Component material '{name}' does not exist here and will be created "
                                     "from the reference values stored in the package.")

    for index, item in enumerate(pkg["items"]):
        if item["kind"] == "material":
            plan_material(index, str(item["material"]["name"]).strip())
        else:
            for comp in item["components"]:
                plan_material(index, str(comp["name"]).strip(), synthesized=True)
            name = str(item.get("mix", {}).get("name", "")).strip()
            key = (name.lower(), tuple(sorted(str(c["name"]).strip() for c in item["components"])))
            existing_id = existing_mixes.get(key)
            if existing_id is not None:
                action = "add" if conflict_mode == "rename" else conflict_mode
                plan.actions.append(ImportAction(index, "mix", name or f"mix {index + 1}", action,
                                                 new_name=(f"{name} (imported)" if action == "add" else None),
                                                 existing_id=existing_id))
            else:
                plan.actions.append(ImportAction(index, "mix", name or f"mix {index + 1}", "add"))
    return plan


# --------------------------------------------------------------------------- applying

@dataclass
class ImportResult:
    added_materials: list = field(default_factory=list)
    renamed: list = field(default_factory=list)
    overwritten: list = field(default_factory=list)
    skipped: list = field(default_factory=list)
    added_mix_ids: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


def _set_material_row(self, row_idx, mat):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QTableWidgetItem
    table = self.table_3d_db
    for col, key in enumerate(("name", "brand", "type", "color", "printer", "date")):
        table.setItem(row_idx, col, QTableWidgetItem(str(mat.get(key, "") or "")))
    for col, key in ((6, "red"), (7, "red_std"), (8, "zeff"), (9, "zeff_std")):
        value = schema.to_float(mat.get(key))
        item = QTableWidgetItem()
        item.setData(Qt.EditRole, value)
        item.setText(f"{value:.4f}")
        table.setItem(row_idx, col, item)


def _apply_material(self, item_mat, cal_rows, notes, name, mode, result):
    m = _tab()
    table = self.table_3d_db
    db_map = props.get_material_db_map(self)
    mat = dict(item_mat)
    mat["name"] = name
    with m.signals_blocked(table):
        sorting = table.isSortingEnabled()
        table.setSortingEnabled(False)
        try:
            if mode == "overwrite" and name in db_map:
                row_idx = db_map[name]["row"]
            else:
                row_idx = table.rowCount()
                table.insertRow(row_idx)
            _set_material_row(self, row_idx, mat)
        finally:
            table.setSortingEnabled(sorting)
    rows = [schema.dict_to_row(schema.MATERIAL_CAL_FIELDS, r, schema.MATERIAL_CAL_DEFAULTS, schema.MATERIAL_CAL_TEXT_IDX)
            for r in cal_rows]
    if mode == "overwrite" or rows:
        self.calibration_data_cache[name] = rows
    else:
        self.calibration_data_cache.setdefault(name, [])
    if mode == "overwrite" or notes:
        self.notes_cache[name] = notes or ""
    if getattr(self, "current_viewed_filament", None) == name:
        self.current_viewed_filament = None  # force the detail view to reload from the cache


def _insert_mix_group(self, item, mix_name, result):
    m = _tab()
    from PySide6.QtWidgets import QComboBox, QSpinBox
    table = self.table_mat_mix
    max_id = -1
    for r in range(table.rowCount()):
        spin = table.cellWidget(r, 0)
        if isinstance(spin, QSpinBox) and spin.property("mix_id") is not None:
            max_id = max(max_id, spin.property("mix_id"))
    new_id = max_id + 1
    names = [str(c["name"]).strip() for c in item["components"]]
    with m.signals_blocked(table):
        sorting = table.isSortingEnabled()
        table.setSortingEnabled(False)
        try:
            for i, comp_name in enumerate(names):
                row_idx = table.rowCount()
                table.insertRow(row_idx)
                m.populate_mix_row(self, row_idx, has_spinbox=(i == 0), group_size_val=len(names), mix_id_val=new_id)
                combo = table.cellWidget(row_idx, 1)
                if isinstance(combo, QComboBox):
                    combo.setProperty("saved_selection", comp_name)
                    if combo.findText(comp_name) < 0:
                        combo.addItem(comp_name)
                    combo.setCurrentText(comp_name)
                name_item = table.item(row_idx, 2)
                if name_item is not None:
                    name_item.setText(mix_name if i == 0 else "")
        finally:
            table.setSortingEnabled(sorting)
    _fill_mix_caches(self, new_id, item)
    result.added_mix_ids.append(new_id)
    return new_id


def _fill_mix_caches(self, mix_id, item):
    cal_rows = []
    for r in item.get("calibration", []):
        ratios = r.get("ratios") or []
        cal_rows.append([schema.format_ratios(ratios)]
                        + schema.dict_to_row(schema.MIX_CAL_FIELDS, r, schema.MIX_CAL_DEFAULTS, schema.MIX_CAL_TEXT_IDX))
    self.mix_calibration_cache[mix_id] = cal_rows
    self.mix_notes_cache[mix_id] = item.get("notes", "") or ""
    self.mix_m_value_cache[mix_id] = schema.to_float(item.get("mix", {}).get("m_value"), 3.4) or 3.4
    self.mix_red_cache[mix_id] = [
        {"percentage": [schema.to_float(p) for p in combo.get("percentage", [])],
         "rows": [schema.dict_to_row(schema.MIX_RED_FIELDS, row, schema.MIX_RED_DEFAULTS, schema.MIX_RED_TEXT_IDX)
                  for row in combo.get("rows", [])]}
        for combo in item.get("red_ratio_combos", [])
    ]


def apply_import(self, pkg, plan):
    m = _tab()
    result = ImportResult(warnings=list(plan.warnings))
    items = pkg["items"]
    if getattr(self, "current_viewed_filament", None):
        m.save_current_active_material_cache(self)
    if getattr(self, "current_viewed_mix_id", None) is not None:
        m.save_current_active_mix_cache(self)

    for action in plan.actions:
        item = items[action.index]
        if action.kind == "material":
            if action.action == "skip":
                result.skipped.append(action.source_name)
                continue
            if action.synthesized:
                comp = next(c for c in item["components"] if str(c["name"]).strip() == action.source_name)
                mat = dict(comp.get("reference", {}))
                mat["name"] = action.source_name
                cal_rows, notes = comp.get("calibration", []), comp.get("notes", "")
            else:
                mat, cal_rows, notes = item["material"], item.get("calibration", []), item.get("notes", "")
            target = action.new_name if action.action == "rename" else action.source_name
            _apply_material(self, mat, cal_rows, notes, target, action.action, result)
            if action.action == "rename":
                result.renamed.append(f"{action.source_name} -> {target}")
            elif action.action == "overwrite":
                result.overwritten.append(target)
            else:
                result.added_materials.append(target)
        else:
            if action.action == "skip":
                result.skipped.append(f"mix '{action.source_name}'")
                continue
            if action.action == "overwrite" and action.existing_id is not None:
                _fill_mix_caches(self, action.existing_id, item)
                if getattr(self, "current_viewed_mix_id", None) == action.existing_id:
                    self.current_viewed_mix_id = None
                result.overwritten.append(f"mix '{action.source_name}' (ID {action.existing_id})")
                continue
            mix_name = action.new_name or action.source_name
            _insert_mix_group(self, item, mix_name, result)

    m.update_group_borders_and_properties(self)
    self._force_combobox_update = True
    m.update_mat_mix_comboboxes(self)
    m.populate_view_and_fit_list(self)
    m.auto_save_all_databases(self)
    return result


def summarize_result(result):
    lines = []
    if result.added_materials:
        lines.append("Materials added: " + ", ".join(result.added_materials))
    if result.renamed:
        lines.append("Materials renamed: " + ", ".join(result.renamed))
    if result.overwritten:
        lines.append("Overwritten: " + ", ".join(result.overwritten))
    if result.added_mix_ids:
        lines.append("Mixes added (new IDs): " + ", ".join(str(i) for i in result.added_mix_ids))
    if result.skipped:
        lines.append("Skipped: " + ", ".join(result.skipped))
    if result.warnings:
        lines.append("")
        lines.extend("Note: " + w for w in result.warnings)
    return "\n".join(lines) if lines else "Nothing was imported."


def suggested_file_name(label):
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", str(label)).strip("_") or "package"
    return safe + PACKAGE_EXTENSION
