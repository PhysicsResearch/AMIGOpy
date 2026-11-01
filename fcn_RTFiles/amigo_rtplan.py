"""
Brachytherapy RT plans made in AMIGOpy (View > PLAN > Brachy: New, Save, Save as).

- build_brachy_rtplan: a DICOM RT Plan (brachy) from the plan as AMIGOpy keeps it: the
  source and its air kerma strength (Sk), one application setup with a channel per
  catheter (each dwell position a pair of control points, times in s) and the dose
  reference points. As Oncentra / ACE (Elekta) do, and unlike Varian (RTSTRUCT), the
  catheter points are stored in the plan itself: a private sequence (300F,1000) holds
  a structure set with one BRACHY_CHANNEL ROI per catheter, which its channel references
  (ReferencedROINumber). Only what AMIGOpy uses is written, not all a TPS writes.
- Manufacturer and private creator "AMIGOpy" mark a plan made in AMIGOpy (is_amigo_plan);
  when such a plan is loaded, apply_embedded_catheters puts its catheter points (and
  names) back into its channels.
- Saved state: the plan as it was last saved (or when first shown), to tell whether it
  was changed since (plan_modified) and to put it back (Save as keeps the original).
"""
import datetime

import numpy as np
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
from pydicom.sequence import Sequence
from pydicom.uid import PYDICOM_IMPLEMENTATION_UID, ExplicitVRLittleEndian, generate_uid
from pydicom.valuerep import format_number_as_ds


# Manufacturer, model and private creator of the plans made in AMIGOpy
AMIGO_NAME = "AMIGOpy"
# Private group and element (in the creator's block) of the catheter points: (300F,1000)
CATHETER_GROUP = 0x300F
CATHETER_ELEMENT = 0x00
RT_PLAN_STORAGE = "1.2.840.10008.5.1.4.1.1.481.5"
# Air kerma strength (U = uGy m2 / h) of a new plan
DEFAULT_SK_U = 40700.0
# Plan metadata: the saved state, and False for a new plan that was never saved
SAVED_STATE_KEY = 'AMIGO_SavedState'
SAVED_KEY = 'AMIGO_Saved'
# Shown / hidden on the images: not part of the plan
DISPLAY_KEYS = ('Visible',)


# ---------------------------------------------------------------------------
# What the plan is
# ---------------------------------------------------------------------------
def is_amigo_plan(meta):
    """True for a plan made (saved) in AMIGOpy."""
    return any(str(meta.get(key) or '').strip() == AMIGO_NAME for key in ('Manufacturer', 'PrivateCreator'))


def plan_never_saved(meta):
    """True for a new plan (New) that was not saved yet."""
    return meta.get(SAVED_KEY) is False


def plan_display_name(meta):
    """Name of a plan in the data tree and the Plan box (AMIGOpy plans: the full name, not the 16-character label)."""
    keys = ('RTPlanName', 'RTPlanLabel') if is_amigo_plan(meta) else ('RTPlanLabel', 'RTPlanName')
    for key in keys:
        name = str(meta.get(key) or '').strip()
        if name:
            return name
    return 'Plan'


def _number(value, default=None):
    """float of a number, a DICOM value or a DICOM element; 'default' if not a finite number."""
    value = getattr(value, 'value', value)
    try:
        value = float(value)
    except (TypeError, ValueError):
        return default
    return value if np.isfinite(value) else default


def plan_sk(meta, default=DEFAULT_SK_U):
    """Air kerma strength (U) of a plan; 'default' if it has none."""
    value = _number(meta.get('ReferenceAirKermaRate'))
    return value if value is not None and value > 0 else default


def time_scale(ch):
    """
    Factor from the 'Time' column of a channel's dwells to seconds: ChannelTotalTime /
    FinalCumulativeTimeWeight, as the TG43 dose and the total times use it (1 if missing).
    """
    total = _number(ch.get('ChannelTotalTime'), 1.0)
    final = _number(ch.get('FinalCumulativeTimeWeight'), 1.0)
    return total / final if final > 0 else 1.0


def _dwells(ch):
    """The channel's (M, 9) 'DwellInfo' array (empty if missing / invalid)."""
    dwells = ch.get('DwellInfo')
    if isinstance(dwells, np.ndarray) and dwells.ndim == 2 and dwells.shape[1] >= 9:
        return dwells
    return np.empty((0, 9), dtype=np.float32)


def _points(ch):
    """The channel's catheter points (N, 3), rows with all coordinates set."""
    pts = ch.get('ChPos')
    if not isinstance(pts, np.ndarray) or pts.ndim != 2 or pts.shape[1] < 3:
        return np.empty((0, 3))
    pts = pts[:, :3].astype(float)
    return pts[np.all(np.isfinite(pts), axis=1)]


def normalize_channel_times(ch):
    """
    Dwell times of a channel in seconds, with ChannelTotalTime = FinalCumulativeTimeWeight
    = their sum, as written in the plan (in place; the same dose).
    """
    dwells = _dwells(ch)
    if len(dwells):
        scale = time_scale(ch)
        if scale != 1.0:
            dwells[:, 2] = dwells[:, 2] * scale
        total = float(np.nansum(dwells[:, 2]))
    else:
        total = 0.0
    ch['ChannelTotalTime'] = ch['FinalCumulativeTimeWeight'] = total
    ch['NumberofControlPoints'] = 2 * len(dwells)


# ---------------------------------------------------------------------------
# DICOM RT Plan
# ---------------------------------------------------------------------------
def _ds(value):
    """DICOM decimal string (DS, at most 16 characters) of a number."""
    return format_number_as_ds(float(value))


def _int(value, default=None):
    value = _number(value)
    return int(round(value)) if value is not None else default


def _text(value, max_len):
    return str(value or '').strip()[:max_len]


def _template_value(template, keyword):
    value = getattr(template, keyword, None) if template is not None else None
    return None if value is None or value == '' else value


def _first(template, keyword):
    """First item of a sequence of the template plan, or None."""
    seq = _template_value(template, keyword)
    return seq[0] if seq else None


def _source_item(template, sk, date, time):
    """The source (number 1): from the plan copied, else Ir-192; with the plan's Sk."""
    old = _first(template, 'SourceSequence')
    src = Dataset()
    src.SourceNumber = 1
    src.SourceType = _template_value(old, 'SourceType') or 'LINE'
    for keyword in ('SourceManufacturer', 'ActiveSourceDiameter', 'ActiveSourceLength'):
        value = _template_value(old, keyword)
        if value is not None:
            setattr(src, keyword, value)
    src.SourceIsotopeName = _template_value(old, 'SourceIsotopeName') or 'Ir-192'
    src.SourceIsotopeHalfLife = _template_value(old, 'SourceIsotopeHalfLife') or '73.83'
    src.ReferenceAirKermaRate = _ds(sk)
    # the date of the strength is kept while Sk is the one of the plan copied
    old_sk = _number(_template_value(old, 'ReferenceAirKermaRate'))
    same = old_sk is not None and np.isclose(old_sk, sk) and _template_value(old, 'SourceStrengthReferenceDate')
    src.SourceStrengthReferenceDate = old.SourceStrengthReferenceDate if same else date
    src.SourceStrengthReferenceTime = (_template_value(old, 'SourceStrengthReferenceTime') or '000000') if same else time
    return src


def _channel_item(ch, k, roi_number):
    """Channel of catheter k: applicator fields, times and its dwell positions (control point pairs)."""
    item = Dataset()
    item.ChannelNumber = _int(ch.get('ChannelNumber'), k + 1)
    for keyword in ('ChannelLength', 'SourceApplicatorLength', 'SourceApplicatorStepSize'):
        value = _number(ch.get(keyword))
        if value is not None:
            setattr(item, keyword, _ds(value))
    number = _int(ch.get('SourceApplicatorNumber'))
    if number is not None:
        item.SourceApplicatorNumber = number
    for keyword, max_len in (('SourceApplicatorID', 16), ('SourceApplicatorType', 16)):
        value = _text(ch.get(keyword), max_len)
        if value and value != 'N/A':
            setattr(item, keyword, value)
    dwells = _dwells(ch)
    times = np.nan_to_num(dwells[:, 2].astype(float)) * time_scale(ch)
    cumulative = np.concatenate(([0.0], np.cumsum(times)))
    item.SourceMovementType = 'STEPWISE'
    item.ChannelTotalTime = _ds(cumulative[-1])
    item.FinalCumulativeTimeWeight = _ds(cumulative[-1])
    item.NumberOfControlPoints = 2 * len(dwells)
    item.ReferencedSourceNumber = 1
    item.ReferencedROINumber = roi_number
    control_points = []
    for i, row in enumerate(dwells.astype(float)):
        # the source arrives (cumulative time before the dwell) and leaves (after it)
        for j, weight in enumerate((cumulative[i], cumulative[i + 1])):
            cp = Dataset()
            cp.ControlPointIndex = 2 * i + j
            if np.isfinite(row[1]):
                cp.ControlPointRelativePosition = _ds(row[1])
            if np.all(np.isfinite(row[3:6])):
                cp.ControlPoint3DPosition = [_ds(v) for v in row[3:6]]
            cp.CumulativeTimeWeight = _ds(weight)
            if np.all(np.isfinite(row[6:9])):
                cp.ControlPointOrientation = [float(v) for v in row[6:9]]
            control_points.append(cp)
    item.BrachyControlPointSequence = Sequence(control_points)
    return item


def _dose_reference_items(refs):
    """Dose reference points; unnamed ones without a position (empty rows) are left out."""
    from fcn_display.brachy_channel_edit import ref_point_name, ref_point_xyz
    items = []
    for k, pt in enumerate(refs):
        xyz = ref_point_xyz(pt)
        number = _int(pt.get('DoseReferenceNumber'), k + 1)
        name = ref_point_name(pt, k)
        if xyz is None and name == f"Point {number}":
            continue
        item = Dataset()
        item.DoseReferenceNumber = number
        item.DoseReferenceStructureType = 'COORDINATE' if xyz is not None else 'SITE'
        item.DoseReferenceDescription = _text(name, 64)
        if xyz is not None:
            item.DoseReferencePointCoordinates = [_ds(v) for v in xyz]
        kind = str(pt.get('DoseReferenceType') or '').strip().upper()
        item.DoseReferenceType = kind if kind in ('TARGET', 'ORGAN_AT_RISK') else 'TARGET'
        dose = _number(pt.get('TargetPrescriptionDose'))
        if dose is not None:
            item.TargetPrescriptionDose = _ds(dose)
        items.append(item)
    return items


def _catheter_structure_set(channels, frame_uid):
    """Structure set (private, as Oncentra / ACE) with ROI k + 1 = the points of catheter k."""
    from fcn_display.brachy_channel_edit import catheter_name
    rois, contours, observations = [], [], []
    for k, ch in enumerate(channels):
        number = k + 1
        roi = Dataset()
        roi.ROINumber = number
        if frame_uid:
            roi.ReferencedFrameOfReferenceUID = frame_uid
        roi.ROIName = _text(catheter_name(ch, k), 64)
        roi.ROIGenerationAlgorithm = 'MANUAL'
        rois.append(roi)
        contour = Dataset()
        contour.ReferencedROINumber = number
        pts = _points(ch)
        if len(pts):
            line = Dataset()
            line.ContourGeometricType = 'OPEN_NONPLANAR'
            line.NumberOfContourPoints = len(pts)
            line.ContourData = [_ds(v) for v in pts.ravel()]
            contour.ContourSequence = Sequence([line])
        contours.append(contour)
        observation = Dataset()
        observation.ObservationNumber = number
        observation.ReferencedROINumber = number
        observation.RTROIInterpretedType = 'BRACHY_CHANNEL'
        observation.ROIInterpreter = ''
        observations.append(observation)
    item = Dataset()
    item.StructureSetROISequence = Sequence(rois)
    item.ROIContourSequence = Sequence(contours)
    item.RTROIObservationsSequence = Sequence(observations)
    return item


def build_brachy_rtplan(meta, name, template=None, patient_id=None, study_id=None, series_number=1,
                        sop_uid=None, series_uid=None, now=None):
    """
    DICOM RT Plan (FileDataset) of a brachy plan from its AMIGOpy metadata ('Plan_Brachy_Channels',
    'Plan_Dose_References', Sk), named 'name'.
    - template: DICOM dataset for the patient, study and frame of reference (the plan copied,
      or the image of a new plan) and, if it is a plan, for the source and the treatment.
    - patient_id / study_id: as in the data tree (where the plan goes when it is loaded again);
      'N/A' (not in the image either) is not written.
    """
    template = template if isinstance(template, Dataset) else None
    now = now or datetime.datetime.now()
    date, time = now.strftime('%Y%m%d'), now.strftime('%H%M%S')
    sop_uid = sop_uid or generate_uid()
    series_uid = series_uid or generate_uid()
    channels = meta.get('Plan_Brachy_Channels') or []
    refs = [pt for pt in meta.get('Plan_Dose_References') or [] if isinstance(pt, dict)]
    sk = plan_sk(meta)

    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = RT_PLAN_STORAGE
    file_meta.MediaStorageSOPInstanceUID = sop_uid
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = PYDICOM_IMPLEMENTATION_UID
    file_meta.ImplementationVersionName = AMIGO_NAME
    ds = FileDataset('', Dataset(), file_meta=file_meta, preamble=b'\0' * 128)

    ds.SpecificCharacterSet = 'ISO_IR 192'
    ds.InstanceCreationDate, ds.InstanceCreationTime = date, time
    ds.SOPClassUID, ds.SOPInstanceUID = RT_PLAN_STORAGE, sop_uid
    # patient, study and frame of reference (Type 2 ones written empty if unknown)
    for keyword, required in (('PatientName', True), ('PatientBirthDate', True), ('PatientSex', True),
                              ('StudyInstanceUID', False), ('StudyDate', True), ('StudyTime', True),
                              ('StudyDescription', False), ('AccessionNumber', True), ('ReferringPhysicianName', True),
                              ('FrameOfReferenceUID', False), ('InstitutionName', False)):
        value = _template_value(template, keyword)
        if value is not None or required:
            setattr(ds, keyword, value if value is not None else '')
    for keyword, value in (('PatientID', patient_id), ('StudyID', study_id)):
        value = value if value is not None else _template_value(template, keyword)
        if value is not None and str(value) != 'N/A':
            setattr(ds, keyword, str(value))
    if 'StudyInstanceUID' not in ds:
        ds.StudyInstanceUID = generate_uid()
    ds.Modality = 'RTPLAN'
    ds.Manufacturer = AMIGO_NAME
    ds.ManufacturerModelName = AMIGO_NAME
    ds.SeriesInstanceUID = series_uid
    ds.SeriesNumber = _int(series_number, 1)
    ds.SeriesDescription = _text(name, 64)
    ds.SeriesDate, ds.SeriesTime = date, time
    ds.PositionReferenceIndicator = ''
    # RT general plan
    ds.RTPlanLabel = _text(name, 16)
    ds.RTPlanName = _text(name, 64)
    ds.RTPlanDescription = f"Brachytherapy plan made in {AMIGO_NAME}"
    ds.RTPlanDate, ds.RTPlanTime = date, time
    ds.RTPlanGeometry = 'PATIENT'
    ds.ApprovalStatus = 'UNAPPROVED'
    # brachy treatment, machine and source
    treatment = str(meta.get('BrachyTreatmentType') or '').strip()
    ds.BrachyTreatmentType = treatment if treatment not in ('', 'N/A') else (_template_value(template, 'BrachyTreatmentType') or 'HDR')
    ds.BrachyTreatmentTechnique = _template_value(template, 'BrachyTreatmentTechnique') or 'INTERSTITIAL'
    machine = Dataset()
    old_machine = _first(template, 'TreatmentMachineSequence')
    machine.TreatmentMachineName = _template_value(old_machine, 'TreatmentMachineName') or AMIGO_NAME
    ds.TreatmentMachineSequence = Sequence([machine])
    ds.SourceSequence = Sequence([_source_item(template, sk, date, time)])
    # application setup: a channel per catheter
    setup = Dataset()
    setup.ApplicationSetupType = 'OTHER'
    setup.ApplicationSetupNumber = 1
    setup.ApplicationSetupName = _text(name, 64)
    total_time = sum(float(np.nansum(_dwells(ch)[:, 2])) * time_scale(ch) for ch in channels)
    setup.TotalReferenceAirKerma = _ds(sk * total_time / 3600.0)
    setup.ChannelSequence = Sequence([_channel_item(ch, k, k + 1) for k, ch in enumerate(channels)])
    ds.ApplicationSetupSequence = Sequence([setup])
    fraction = Dataset()
    fraction.FractionGroupNumber = 1
    fraction.NumberOfFractionsPlanned = 1
    fraction.NumberOfBeams = 0
    fraction.NumberOfBrachyApplicationSetups = 1
    referenced = Dataset()
    referenced.ReferencedBrachyApplicationSetupNumber = 1
    fraction.ReferencedBrachyApplicationSetupSequence = Sequence([referenced])
    ds.FractionGroupSequence = Sequence([fraction])
    references = _dose_reference_items(refs)
    if references:
        ds.DoseReferenceSequence = Sequence(references)
    # the catheter points, in the plan (private, as Oncentra / ACE)
    block = ds.private_block(CATHETER_GROUP, AMIGO_NAME, create=True)
    block.add_new(CATHETER_ELEMENT, 'SQ', Sequence([_catheter_structure_set(channels, _template_value(template, 'FrameOfReferenceUID'))]))
    return ds


# ---------------------------------------------------------------------------
# Loading a plan made in AMIGOpy
# ---------------------------------------------------------------------------
def embedded_catheters(ds):
    """{ROI number: (name, (N, 3) float32 points)} of the catheters stored in a plan made in AMIGOpy."""
    try:
        seq = ds.private_block(CATHETER_GROUP, AMIGO_NAME)[CATHETER_ELEMENT].value
        item = seq[0]
    except (AttributeError, KeyError, IndexError, TypeError, ValueError):
        return {}
    names = {}
    for roi in getattr(item, 'StructureSetROISequence', []):
        number = _int(getattr(roi, 'ROINumber', None))
        if number is not None:
            names[number] = str(getattr(roi, 'ROIName', '') or '').strip()
    catheters = {}
    for contour in getattr(item, 'ROIContourSequence', []):
        number = _int(getattr(contour, 'ReferencedROINumber', None))
        if number is None:
            continue
        data = [v for line in getattr(contour, 'ContourSequence', []) for v in getattr(line, 'ContourData', [])]
        pts = np.asarray(data, dtype=np.float32)
        pts = pts.reshape(-1, 3) if pts.size % 3 == 0 else np.empty((0, 3), dtype=np.float32)
        catheters[number] = (names.get(number, ''), pts)
    return catheters


def apply_embedded_catheters(meta):
    """Catheter points and names of a plan made in AMIGOpy (stored in the plan) into its channels."""
    catheters = embedded_catheters(meta.get('DCM_Info'))
    for k, ch in enumerate(meta.get('Plan_Brachy_Channels') or []):
        number = _int(ch.get('ReferencedROINumber'))
        if number not in catheters:
            continue
        name, pts = catheters[number]
        ch['ChPos'] = pts
        if name and name != f"Catheter {k + 1}":
            ch['CatheterName'] = name


# ---------------------------------------------------------------------------
# Saved state
# ---------------------------------------------------------------------------
def _copy_items(d):
    """Copy of a catheter / reference point dict (arrays and lists copied), without what is only shown."""
    return {key: (val.copy() if isinstance(val, (np.ndarray, list)) else val)
            for key, val in d.items() if key not in DISPLAY_KEYS}


def plan_state(meta):
    """Copy of what can be edited in a plan: catheters, reference points and Sk."""
    return {'channels': [_copy_items(ch) for ch in meta.get('Plan_Brachy_Channels') or []],
            'refs': [_copy_items(pt) for pt in meta.get('Plan_Dose_References') or [] if isinstance(pt, dict)],
            'has_sk': 'ReferenceAirKermaRate' in meta, 'sk': meta.get('ReferenceAirKermaRate')}


def remember_saved_state(meta):
    meta[SAVED_STATE_KEY] = plan_state(meta)


def ensure_saved_state(meta):
    """The state of a plan when it is first shown (loaded), unless it has one."""
    if SAVED_STATE_KEY not in meta:
        remember_saved_state(meta)


def restore_saved_state(meta):
    """Put the plan back as it was saved (new copies: the saved state stays as it is)."""
    saved = meta.get(SAVED_STATE_KEY)
    if saved is None:
        return
    meta['Plan_Brachy_Channels'] = [_copy_items(ch) for ch in saved['channels']]
    meta['Plan_Dose_References'] = [_copy_items(pt) for pt in saved['refs']]
    if saved['has_sk']:
        meta['ReferenceAirKermaRate'] = saved['sk']
    else:
        meta.pop('ReferenceAirKermaRate', None)


def adopt_placeholder_ref(meta):
    """
    The empty reference point row added when a plan without reference points lists them
    is not a change of the plan: it becomes part of the saved state.
    """
    saved = meta.get(SAVED_STATE_KEY)
    if saved is not None and not saved['refs']:
        saved['refs'] = [_copy_items(pt) for pt in meta.get('Plan_Dose_References') or [] if isinstance(pt, dict)]


def _same(a, b):
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        try:
            a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
        except (TypeError, ValueError):
            return False
        return a.shape == b.shape and np.array_equal(a, b, equal_nan=True)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    try:
        return bool(a == b)
    except (TypeError, ValueError):
        return False


def _same_elements(current, saved):
    """Catheter / reference point dicts as saved (what is only shown left out)."""
    if len(current) != len(saved):
        return False
    for el, old in zip(current, saved):
        keys = set(el) - set(DISPLAY_KEYS)
        if keys != set(old) or not all(_same(el[key], old[key]) for key in keys):
            return False
    return True


def plan_modified(meta):
    """True if the plan was changed since it was saved (or first shown)."""
    saved = meta.get(SAVED_STATE_KEY)
    if saved is None:
        return False
    refs = [pt for pt in meta.get('Plan_Dose_References') or [] if isinstance(pt, dict)]
    return not (np.isclose(plan_sk(meta), plan_sk({'ReferenceAirKermaRate': saved['sk']}))
                and _same_elements(meta.get('Plan_Brachy_Channels') or [], saved['channels'])
                and _same_elements(refs, saved['refs']))


def plan_tree_label(series, type_tag):
    """Label of a plan in the data tree: '<type> <name>_Series: <number>', marked if made in AMIGOpy, not saved or changed."""
    meta = series.get('metadata', {})
    if is_amigo_plan(meta) and type_tag.endswith(']'):
        type_tag = f"{type_tag[:-1]} {AMIGO_NAME}]"
    label = f"{type_tag} {plan_display_name(meta)}"
    if plan_never_saved(meta):
        label += " (not saved)"
    label += f"_Series: {series.get('SeriesNumber')}"
    return label + (" *" if plan_modified(meta) else "")
