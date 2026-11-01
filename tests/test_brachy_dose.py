from types import SimpleNamespace

import numpy as np

from fcn_brachy.cal_TG43_dose import (_rotation_matrix_from_direction, store_dose_to_medical_image,
                                      transform_and_sum_dose_matrix_centered_3D)
from fcn_brachy_sources.process_brachy_database import brachy_source_names
from fcn_load.populate_med_image_list import rtdose_tree_label


def test_source_names_are_the_subfolders(tmp_path):
    for name in ("SourceA", "SourceB", "__pycache__"):
        (tmp_path / name).mkdir()
    (tmp_path / "notes.txt").write_text("not a source")
    assert sorted(brachy_source_names(str(tmp_path))) == ["SourceA", "SourceB"]


def test_source_database_has_the_gammamed_source():
    assert "GammaMed_Ir192HDR_Plus" in brachy_source_names()


def test_rotation_turns_z_to_the_source_direction():
    d = np.array([1.0, 2.0, 2.0]) / 3.0
    rot = _rotation_matrix_from_direction(*d)
    assert np.allclose(rot @ [0.0, 0.0, 1.0], d)
    assert np.allclose(rot @ rot.T, np.eye(3))


def test_rotation_without_direction_is_identity():
    assert np.array_equal(_rotation_matrix_from_direction(np.nan, np.nan, np.nan), np.eye(3))
    assert np.array_equal(_rotation_matrix_from_direction(0.0, 0.0, 0.0), np.eye(3))


def _kernel():
    """Reference matrix (z, y, x) at 1 mm: 1 at the source, 2 at 5 mm along its axis (+z)."""
    kernel = np.zeros((21, 21, 21), dtype=np.float32)
    kernel[10, 10, 10] = 1.0
    kernel[15, 10, 10] = 2.0
    return kernel


def test_dose_follows_the_source_direction_and_time():
    up = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 3.0]])
    down = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 3.0]])
    dose_up, meta = transform_and_sum_dose_matrix_centered_3D(up, _kernel(), 1.0, output_margin_mm=10, output_res_mm=1.0)
    dose_down, _ = transform_and_sum_dose_matrix_centered_3D(down, _kernel(), 1.0, output_margin_mm=10, output_res_mm=1.0)
    assert dose_up.shape == (21, 21, 21) and meta['origin_mm'] == (-10.0, -10.0, -10.0)
    assert np.isclose(dose_up[10, 10, 10], 3.0) and np.isclose(dose_up[15, 10, 10], 6.0)
    assert np.isclose(dose_down[5, 10, 10], 6.0) and np.isclose(dose_down[15, 10, 10], 0.0)


def test_dwell_without_orientation_gives_the_dose_along_z():
    dwells = np.array([[0.0, 0.0, 0.0, np.nan, np.nan, np.nan, 3.0]])
    dose, _ = transform_and_sum_dose_matrix_centered_3D(dwells, _kernel(), 1.0, output_margin_mm=10, output_res_mm=1.0)
    assert np.all(np.isfinite(dose)) and np.isclose(dose[15, 10, 10], 6.0)


def test_dose_stored_in_the_given_study_with_its_plan():
    app = SimpleNamespace(medical_image={'P': {'S': {'CT': [{'SeriesNumber': 2}]}}})
    meta = {'pixel_spacing_mm': 2.0, 'origin_mm': (-100.0, -100.0, -100.0)}
    k = store_dose_to_medical_image(app, np.ones((3, 3, 3), dtype=np.float32), meta, 'P', 'S', 7, '1.2.3')
    k2 = store_dose_to_medical_image(app, np.zeros((3, 3, 3), dtype=np.float32), meta, 'P', 'S', 8)
    doses = app.medical_image['P']['S']['RTDOSE']
    assert (k, k2) == (0, 1)
    assert doses[0]['SeriesNumber'] == 7 and doses[0]['metadata']['ReferencedRTPlanSOPInstanceUID'] == '1.2.3'
    assert doses[0]['metadata']['PixelSpacing'] == [2.0, 2.0]
    assert doses[0]['metadata']['ImagePositionPatient'] == meta['origin_mm']
    assert doses[1]['SeriesNumber'] == 8 and 'ReferencedRTPlanSOPInstanceUID' not in doses[1]['metadata']


def test_dose_label_has_the_name_of_its_plan():
    study = {'RTPLAN': [{'metadata': {'SOPInstanceUID': '1.1', 'RTPlanLabel': 'CaseA'}},
                        {'metadata': {'SOPInstanceUID': '1.2', 'Manufacturer': 'AMIGOpy', 'RTPlanLabel': 'Cervix plan 2',
                                      'RTPlanName': 'Cervix plan 2 with needles'}}]}

    def dose(uid):
        return {'SeriesNumber': 5, 'metadata': {'SeriesDescription': 'TG43_AMIGOpy', 'ReferencedRTPlanSOPInstanceUID': uid}}

    assert rtdose_tree_label(study, dose('1.1')) == "TG43_AMIGOpy (CaseA)_Series: 5"
    assert rtdose_tree_label(study, dose('1.2')) == "TG43_AMIGOpy (Cervix plan 2 with needles)_Series: 5"
    assert rtdose_tree_label(study, dose('9.9')) == "TG43_AMIGOpy_Series: 5"
    assert rtdose_tree_label({}, {'SeriesNumber': 1, 'metadata': {'DoseSummationType': 'PLAN'}}) == "PLAN_Series: 1"
