from fcn_3DPrinting import db_schema as s


def test_schema_lengths_are_consistent():
    assert len(s.MATERIAL_DB_COLUMNS) == 10
    assert len(s.MATERIAL_CAL_FIELDS) == len(s.MATERIAL_CAL_UI_HEADERS) == len(s.MATERIAL_CAL_DEFAULTS) == 20
    assert len(s.MIX_CAL_FIELDS) == len(s.MIX_CAL_DEFAULTS) == 19
    assert len(s.MIX_RED_FIELDS) == len(s.MIX_RED_DEFAULTS) == 14


def test_row_dict_round_trip_material():
    row = list(s.MATERIAL_CAL_DEFAULTS)
    d = s.row_to_dict(s.MATERIAL_CAL_FIELDS, row)
    assert d["Infill Pattern"] == "Grid" and d["kV_low"] == "80"
    back = s.dict_to_row(s.MATERIAL_CAL_FIELDS, d, s.MATERIAL_CAL_DEFAULTS, s.MATERIAL_CAL_TEXT_IDX)
    assert back == row


def test_dict_to_row_tolerates_numbers_strings_and_missing():
    d = {"HU_low": 123.456789, "HU_hig": "150,5", "Shape": "Cube"}
    row = s.dict_to_row(s.MATERIAL_CAL_FIELDS, d, s.MATERIAL_CAL_DEFAULTS, s.MATERIAL_CAL_TEXT_IDX)
    assert row[2] == "123.4568"
    assert row[4] == "150,5"          # non-numeric text is passed through, not silently zeroed
    assert row[16] == "Cube"
    assert row[13] == "Grid"          # missing -> default


def test_ratios_round_trip():
    assert s.parse_ratios("50.0000,50.0000") == [50.0, 50.0]
    assert s.parse_ratios("garbage") == []
    assert s.format_ratios([30, 70.5]) == "30.0000,70.5000"
    assert s.to_float("1,25") == 1.25 and s.to_float(None, 7.0) == 7.0
