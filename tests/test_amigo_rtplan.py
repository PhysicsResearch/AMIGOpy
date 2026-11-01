import datetime

import numpy as np
import pydicom
import pytest
from pydicom.dataset import Dataset

from fcn_RTFiles import amigo_rtplan as ar


def _dwells(z, times, orient=(0.0, 0.0, 1.0)):
    """DwellInfo-like (M, 9) float32 array along z: IDX, RelPos, Time, X, Y, Z, Ux, Uy, Uz."""
    out = np.zeros((len(z), 9), dtype=np.float32)
    out[:, 0] = np.arange(1, len(z) + 1)
    out[:, 1] = np.arange(len(z)) * 5.0
    out[:, 2] = times
    out[:, 5] = z
    out[:, 6:9] = orient
    return out


def _plan():
    named = {'ChannelNumber': 1, 'CatheterName': 'Tandem', 'ChannelLength': 1300.0,
             'ChPos': np.array([(0, 0, -10), (0, 0, 0), (0, 0, 10)], dtype=np.float32),
             'DwellInfo': _dwells([-5.0, 0.0, 5.0], [2.5, 0.0, 7.25]), 'Visible': False}
    plain = {'ChannelNumber': 2, 'ChPos': np.array([(20, 1.5, -10), (20, 1.5, 10)], dtype=np.float32),
             'DwellInfo': _dwells([0.0], [3.0], orient=(np.nan, np.nan, np.nan))}
    refs = [{'DoseReferenceNumber': 1, 'DoseReferenceDescription': 'A left', 'DoseReferencePointCoordinates': [-20.0, 0.0, 5.0],
             'DoseReferenceType': 'POINT', 'Visible': False},
            {'DoseReferenceNumber': 2, 'DoseReferenceDescription': 'Point 2', 'DoseReferencePointCoordinates': ['N/A'] * 3},
            {'DoseReferenceNumber': 3, 'DoseReferenceDescription': 'Bladder', 'DoseReferencePointCoordinates': 'N/A'}]
    return {'Plan_Brachy_Channels': [named, plain], 'Plan_Dose_References': refs, 'ReferenceAirKermaRate': 20350.0}


def _load(folder):
    """The plans of a folder as the DICOM loader of the data tree reads them."""
    from fcn_load.load_dcm import load_images
    from fcn_load.sort_dcm import get_data_description
    info, _, _ = get_data_description(str(folder))
    return load_images(None, info)[0]


def _write_and_load(tmp_path, meta, name="Plan A", **kwargs):
    ds = ar.build_brachy_rtplan(meta, name, **kwargs)
    pydicom.dcmwrite(tmp_path / "RP.dcm", ds, enforce_file_format=True)
    return ds, _load(tmp_path)


def test_saved_plan_loads_back_with_catheters_from_the_plan(tmp_path):
    meta = _plan()
    ds, data = _write_and_load(tmp_path, meta, name="A long plan name, more than 16", patient_id='P1', study_id='S1',
                               series_number=7)
    loaded = data['P1']['S1']['RTPLAN'][0]
    back = loaded['metadata']
    assert ar.is_amigo_plan(back) and back['Manufacturer'] == ar.AMIGO_NAME and back['PrivateCreator'] == ar.AMIGO_NAME
    assert ds.RTPlanLabel == "A long plan name" and ar.plan_display_name(back) == "A long plan name, more than 16"
    assert loaded['SeriesNumber'] == 7 and ar.plan_sk(back) == pytest.approx(20350.0)
    assert ds.ApplicationSetupSequence[0].TotalReferenceAirKerma == pytest.approx(20350.0 * 12.75 / 3600)
    channels = back['Plan_Brachy_Channels']
    assert [ch['ChannelNumber'] for ch in channels] == [1, 2]
    assert channels[0]['CatheterName'] == 'Tandem' and 'CatheterName' not in channels[1]
    for old, new in zip(meta['Plan_Brachy_Channels'], channels):
        np.testing.assert_allclose(new['ChPos'], old['ChPos'], atol=1e-5)
        np.testing.assert_allclose(new['DwellInfo'][:, 1:], old['DwellInfo'][:, 1:], atol=1e-5)   # NaN orientation kept
    # dose reference points: placed and named ones; an empty "Point <n>" row is left out
    refs = back['Plan_Dose_References']
    assert [r['DoseReferenceDescription'] for r in refs] == ['A left', 'Bladder']
    assert refs[0]['DoseReferencePointCoordinates'] == pytest.approx([-20.0, 0.0, 5.0])
    assert refs[0]['DoseReferenceStructureType'] == 'COORDINATE' and refs[1]['DoseReferenceStructureType'] == 'SITE'
    assert refs[1]['DoseReferencePointCoordinates'] == 'N/A'


def test_catheters_matched_by_roi_number_not_order(tmp_path):
    meta = _plan()
    ds = ar.build_brachy_rtplan(meta, "Plan", patient_id='P1', study_id='S1')
    channel_items = ds.ApplicationSetupSequence[0].ChannelSequence
    channel_items[0].ReferencedROINumber, channel_items[1].ReferencedROINumber = 2, 1
    pydicom.dcmwrite(tmp_path / "RP.dcm", ds, enforce_file_format=True)
    channels = _load(tmp_path)['P1']['S1']['RTPLAN'][0]['metadata']['Plan_Brachy_Channels']
    assert len(channels[0]['ChPos']) == 2 and channels[1]['CatheterName'] == 'Tandem'


def test_plan_without_catheters_loads_as_empty_brachy_plan(tmp_path):
    meta = {'Plan_Brachy_Channels': [], 'Plan_Dose_References': [], 'ReferenceAirKermaRate': ar.DEFAULT_SK_U}
    _, data = _write_and_load(tmp_path, meta, patient_id='P1', study_id='S1')
    back = data['P1']['S1']['RTPLAN'][0]['metadata']
    assert back['Plan_Brachy_Channels'] == [] and back['Plan_Dose_References'] == []
    assert ar.plan_sk(back) == pytest.approx(40700.0) and back['BrachyTreatmentType'] == 'HDR'


def test_times_are_written_in_seconds():
    ch = {'ChannelTotalTime': 300.0, 'FinalCumulativeTimeWeight': 1.0, 'DwellInfo': _dwells([0.0, 5.0], [0.25, 0.75])}
    ds = ar.build_brachy_rtplan({'Plan_Brachy_Channels': [ch]}, "Plan")
    item = ds.ApplicationSetupSequence[0].ChannelSequence[0]
    assert [float(cp.CumulativeTimeWeight) for cp in item.BrachyControlPointSequence] == [0, 75, 75, 300]
    assert float(item.ChannelTotalTime) == float(item.FinalCumulativeTimeWeight) == 300
    ar.normalize_channel_times(ch)
    np.testing.assert_allclose(ch['DwellInfo'][:, 2], [75, 225])
    assert ch['ChannelTotalTime'] == ch['FinalCumulativeTimeWeight'] == 300 and ch['NumberofControlPoints'] == 4
    assert ar.time_scale(ch) == 1.0


def test_patient_study_and_source_from_the_template():
    template = Dataset()
    template.PatientName, template.StudyInstanceUID, template.FrameOfReferenceUID = "Doe^J", "1.2.3", "1.2.3.4"
    source = Dataset()
    source.SourceIsotopeName, source.SourceIsotopeHalfLife, source.ReferenceAirKermaRate = "Ir-192", "73.83", "40700"
    source.SourceStrengthReferenceDate, source.SourceStrengthReferenceTime = "20250101", "120000"
    template.SourceSequence = [source]
    now = datetime.datetime(2026, 10, 31, 9, 30)
    same = ar.build_brachy_rtplan({'ReferenceAirKermaRate': 40700.0}, "Plan", template, patient_id='P1', study_id='N/A', now=now)
    assert same.PatientName == "Doe^J" and same.PatientID == 'P1' and 'StudyID' not in same   # 'N/A': not in the image
    assert same.StudyInstanceUID == "1.2.3" and same.FrameOfReferenceUID == "1.2.3.4"
    assert same.SourceSequence[0].SourceStrengthReferenceDate == "20250101"
    new = ar.build_brachy_rtplan({'ReferenceAirKermaRate': 20350.0}, "Plan", template, now=now)
    assert float(new.SourceSequence[0].ReferenceAirKermaRate) == 20350
    assert (new.SourceSequence[0].SourceStrengthReferenceDate, new.SourceSequence[0].SourceStrengthReferenceTime) == ("20261031", "093000")


def test_plan_sk_and_names():
    element = pydicom.DataElement(0x300A022A, 'DS', '40832.7')
    assert ar.plan_sk({'ReferenceAirKermaRate': element}) == pytest.approx(40832.7)
    assert ar.plan_sk({'ReferenceAirKermaRate': 'N/A'}) == ar.plan_sk({}) == ar.DEFAULT_SK_U
    varian = {'Manufacturer': 'Varian Medical Systems', 'RTPlanLabel': 'CaseA', 'RTPlanName': 'Case A long'}
    amigo = {'Manufacturer': ar.AMIGO_NAME, 'RTPlanLabel': 'Case A long name', 'RTPlanName': 'Case A long name, full'}
    assert not ar.is_amigo_plan(varian) and ar.plan_display_name(varian) == 'CaseA'
    assert ar.is_amigo_plan(amigo) and ar.plan_display_name(amigo) == 'Case A long name, full'
    assert ar.is_amigo_plan({'PrivateCreator': ar.AMIGO_NAME})


def test_saved_state_tells_changes_and_puts_the_plan_back():
    meta = _plan()
    assert not ar.plan_modified(meta)   # never shown: nothing to compare with
    ar.ensure_saved_state(meta)
    ar.ensure_saved_state(meta)        # (kept)
    channels = meta['Plan_Brachy_Channels']
    channels[0]['Visible'] = True       # shown / hidden is not a change
    meta['Plan_Dose_References'][0]['Visible'] = True
    assert not ar.plan_modified(meta)
    channels[1]['ChPos'][0, 0] = 25.0
    assert ar.plan_modified(meta)
    channels[1]['ChPos'][0, 0] = 20.0
    meta['ReferenceAirKermaRate'] = 40700.0
    assert ar.plan_modified(meta)
    ar.restore_saved_state(meta)
    assert not ar.plan_modified(meta) and meta['ReferenceAirKermaRate'] == 20350.0
    assert meta['Plan_Brachy_Channels'][0] is not channels[0]   # new copies: the saved state stays as it is
    meta['Plan_Brachy_Channels'].pop()
    assert ar.plan_modified(meta)
    # the empty reference point row of a plan without reference points is not a change
    empty = {'Plan_Brachy_Channels': [], 'Plan_Dose_References': []}
    ar.ensure_saved_state(empty)
    empty['Plan_Dose_References'] = [{'DoseReferenceNumber': 1, 'DoseReferencePointCoordinates': ['N/A'] * 3}]
    assert ar.plan_modified(empty)
    ar.adopt_placeholder_ref(empty)
    assert not ar.plan_modified(empty)


def test_plan_tree_label():
    varian = {'SeriesNumber': 18, 'metadata': {'Manufacturer': 'Varian', 'RTPlanLabel': 'CaseA'}}
    assert ar.plan_tree_label(varian, "[Brachy]") == "[Brachy] CaseA_Series: 18"
    meta = {'Manufacturer': ar.AMIGO_NAME, 'RTPlanName': 'New plan', ar.SAVED_KEY: False,
            'Plan_Brachy_Channels': [], 'Plan_Dose_References': []}
    ar.ensure_saved_state(meta)
    new = {'SeriesNumber': 19, 'metadata': meta}
    assert ar.plan_tree_label(new, "[Brachy]") == "[Brachy AMIGOpy] New plan (not saved)_Series: 19"
    meta['Plan_Brachy_Channels'].append({'ChPos': np.zeros((1, 3))})
    assert ar.plan_tree_label(new, "[Brachy]").endswith("_Series: 19 *")
