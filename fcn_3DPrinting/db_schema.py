"""
Column schemas of the 3D-printing databases, declared once.

The tables in fcn_init/create_3D_database_tab.py address cells by index and the
CSV files use different header spellings than the table headers; this module
is the canonical description used by the JSON package export/import, the ROI
bridge and the Overview panels, so none of them have to hard-code indices.
Field names are the CSV header names.
"""

MATERIAL_DB_COLUMNS = [
    "Material Name", "Brand", "Type", "Color", "3DPrinter", "Date",
    "RED", "RED STD", "Zeff", "Zeff STD",
]

MATERIAL_CAL_FIELDS = [
    "kV_low", "kV_hig", "HU_low", "HU_low_STD", "HU_hig", "HU_hig_STD",
    "RED", "RED_STD", "Zeff", "Zeff STD", "Print Temp", "Bed Temp",
    "Infill Density", "Infill Pattern", "Flow Multiplier", "Flow", "Shape",
    "Layer Height", "Line Width", "Print Speed",
]
MATERIAL_CAL_UI_HEADERS = [
    "kV - Low", "kV - High", "HU-Low", "HU-Low STD", "HU-High", "HU-High STD",
    "RED", "RED_STD", "Zeff", "Zeff STD", "Print. Temp (C)", "Bed Temp (C)",
    "Infill Density (%)", "Infill Pattern", "Flow Multiplier", "Flow (%)", "Shape",
    "Layer Height (mm)", "Line Width (mm)", "Print Speed (mm/s)",
]
MATERIAL_CAL_TEXT_IDX = {0, 1, 13, 16}
MATERIAL_CAL_DEFAULTS = [
    "80", "140", "100.0000", "5.0000", "150.0000", "5.0000",
    "1.0000", "0.0200", "6.0000", "0.1000", "210.0000", "60.0000",
    "100.0000", "Grid", "1.0000", "100.0000", "Cylinder",
    "0.2000", "0.4000", "50.0000",
]

MIX_CAL_FIELDS = [
    "kV_low", "kV_hig", "HU_low", "HU_low_STD", "HU_hig", "HU_hig_STD",
    "RED", "RED_STD", "Zeff", "Zeff STD", "Infill Type", "Infill Density",
    "Layer Height", "Line Width", "Print Temp", "Bed Temp", "Flow Multiplier",
    "Flow", "Print Speed",
]
MIX_CAL_TEXT_IDX = {10}
MIX_CAL_DEFAULTS = [
    "80", "140", "100.0000", "5.0000", "150.0000", "5.0000",
    "1.0000", "0.0200", "6.0000", "0.1000", "Grid", "100.0000",
    "0.2000", "0.4000", "210.0000", "60.0000", "1.0000",
    "100.0000", "50.0000",
]

MIX_RED_FIELDS = [
    "Infill %", "Flow", "HU-Low", "HU-Low STD", "HU-High", "HU-High STD",
    "RED", "RED STD", "Pred. RED", "Zeff", "Zeff STD", "Pred. Zeff",
    "kV - Low", "kV - High",
]
MIX_RED_TEXT_IDX = set()
MIX_RED_DEFAULTS = [
    "100.0000", "100.0000", "0.0000", "0.0000", "0.0000", "0.0000",
    "0.0000", "0.0000", "0.0000", "0.0000", "0.0000", "0.0000",
    "80.0000", "140.0000",
]


def to_float(value, default=0.0):
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError):
        return default


def fmt4(value):
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return str(value)


def row_to_dict(fields, row):
    return {name: (row[i] if i < len(row) else "") for i, name in enumerate(fields)}


def dict_to_row(fields, data, defaults, text_idx):
    row = []
    for i, name in enumerate(fields):
        value = data.get(name) if isinstance(data, dict) else None
        if value is None or str(value).strip() == "":
            value = defaults[i]
        if i in text_idx:
            row.append(str(value))
        else:
            try:
                row.append(f"{float(value):.4f}")
            except (TypeError, ValueError):
                row.append(str(value))
    return row


def parse_ratios(text):
    try:
        return [float(part.strip()) for part in str(text).split(",") if part.strip()]
    except ValueError:
        return []


def format_ratios(values):
    return ",".join(f"{float(v):.4f}" for v in values)
