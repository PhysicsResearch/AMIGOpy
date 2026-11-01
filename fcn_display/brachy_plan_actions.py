"""
The plan of View > PLAN > Brachy (Plan box, bottom right, next to Display).

- New: a brachy plan from scratch for the image shown (layer 0): no catheters yet (add them
  with Edit > Catheter > New), Sk 40700 U. It goes into the data tree (RTPLAN) as not saved.
- Save: the plan, as a DICOM RT plan made in AMIGOpy (fcn_RTFiles.amigo_rtplan: catheter
  points in the plan, as Oncentra / ACE), into the data tree. A plan loaded from another
  system, and a new plan, are saved with Save as.
- Save as: the plan as it is now, with a name, as a new plan in the data tree; the plan it
  came from goes back to how it was last saved (or loaded). The edits (and their undo) go on
  in the new plan.
- The box title has the plan's name and whether it is saved; the data tree marks the plans
  made in AMIGOpy, not saved or changed (plan_tree_label).
- Export DCM (data tree, right-click): a plan, as last saved, to a DICOM file.
The air kerma strength (Sk) of the plan is set in the Dose calculation panel (brachy_dose_calc).
"""
import numpy as np
import pydicom
from pydicom.dataset import Dataset
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox

from fcn_RTFiles.amigo_rtplan import (AMIGO_NAME, DEFAULT_SK_U, SAVED_KEY, SAVED_STATE_KEY, build_brachy_rtplan,
                                      is_amigo_plan, normalize_channel_times, plan_display_name, plan_modified,
                                      plan_never_saved, plan_sk, plan_tree_label, remember_saved_state,
                                      restore_saved_state)
from fcn_display.brachy_channel_edit import _end_drag, catheter_being_drawn, commit_channel_edit
from fcn_load.populate_med_image_list import add_series_tree_item, find_tree_item


# Longer plan names are shortened in the Plan box title
TITLE_WIDTH_PX = 150


# ---------------------------------------------------------------------------
# The plan shown and its place in the data tree
# ---------------------------------------------------------------------------
def _current_plan(self):
    """(patient, study, index, series) of the brachy plan shown in View > PLAN > Brachy, or None."""
    try:
        pid, sid, modality, idx = self.patientID_plan, self.studyID_plan, self.modality_plan, self.series_index_plan
        series = self.medical_image[pid][sid][modality][idx]
    except (AttributeError, KeyError, IndexError, TypeError):
        return None
    if modality != 'RTPLAN' or 'Plan_Brachy_Channels' not in series.get('metadata', {}):
        return None
    return pid, sid, idx, series


def _finish_editing(self):
    """End a drag, and a new catheter being clicked (Stop), before the plan is saved."""
    _end_drag(self)
    if catheter_being_drawn(self) is not None:
        self.brachy_new_catheter_btn.setChecked(False)


def _image_series(self):
    """
    (patient, study, series) of the image on layer 0; series None for an image that is not a
    series of the data tree (a structure, a map: the study selected in the tree). None without an image.
    """
    try:
        data = self.display_data[0]
    except (AttributeError, KeyError, IndexError, TypeError):
        return None
    if not isinstance(data, np.ndarray) or data.ndim != 3:
        return None
    medical_image = getattr(self, 'medical_image', None) or {}
    for pid, studies in medical_image.items():
        for sid, modalities in studies.items():
            for series_list in modalities.values():
                for series in series_list:
                    if isinstance(series, dict) and series.get('3DMatrix') is data:
                        return pid, sid, series
    pid, sid = getattr(self, 'patientID', None), getattr(self, 'studyID', None)
    if sid in medical_image.get(pid, {}):
        return pid, sid, None
    return None


def _next_series_number(study):
    """Series number for a new plan: one more than the largest in the study."""
    numbers = [0]
    for series_list in study.values():
        for series in series_list:
            try:
                numbers.append(int(series.get('SeriesNumber')))
            except (AttributeError, TypeError, ValueError):
                pass
    return max(numbers) + 1


def _unique_name(plans, base):
    names = {plan_display_name(plan.get('metadata', {})) for plan in plans}
    k = 2
    name = base
    while name in names:
        name = f"{base} {k}"
        k += 1
    return name


def _plan_tree_item(self, pid, sid, idx):
    """Item of plan idx of a study in the data tree (Medical Image > patient > study > RTPLAN), or None."""
    item = find_tree_item(self, ("Medical Image", f"PatientID: {pid}", f"StudyID: {sid}", "Modality: RTPLAN"))
    return item.child(idx) if item is not None and 0 <= idx < item.rowCount() else None


def update_plan_tree_label(self, pid, sid, idx):
    """The plan's label in the data tree (name; made in AMIGOpy, not saved, changed)."""
    item = _plan_tree_item(self, pid, sid, idx)
    if item is None:
        return
    label = plan_tree_label(self.medical_image[pid][sid]['RTPLAN'][idx], "[Brachy]")
    if item.text() != label:
        item.setText(label)


def _show_plan(self, pid, sid, idx, reset):
    """
    Show plan idx of the study (tables, list, images, metadata), as a click on it in the data
    tree does; reset: from its first catheter (else the catheter and table mode stay).
    """
    from PySide6.QtCore import QItemSelectionModel
    from fcn_display.disp_plan_data import update_disp_brachy_plan, update_plan_tables
    from fcn_display.meta_viewer import update_meta_view_table_dicom
    self.patientID_plan, self.studyID_plan, self.modality_plan, self.series_index_plan = pid, sid, 'RTPLAN', idx
    self.patientID, self.studyID, self.modality, self.series_index = pid, sid, 'RTPLAN', idx
    self.modality_metadata = 'RTPLAN'
    if _plan_tree_item(self, pid, sid, idx) is None:
        # (added as it is: rebuilding the tree would click the image series shown again)
        add_series_tree_item(self, pid, sid, 'RTPLAN', idx, plan_tree_label(self.medical_image[pid][sid]['RTPLAN'][idx], "[Brachy]"))
    item = _plan_tree_item(self, pid, sid, idx)
    if item is not None:  # selected (not clicked: the plan is shown here)
        selection = self.DataTreeView.selectionModel()
        selection.clearSelection()
        selection.select(item.index(), QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
        self.DataTreeView.scrollTo(item.index())
    update_meta_view_table_dicom(self, self.medical_image[pid][sid]['RTPLAN'][idx]['metadata']['DCM_Info'])
    if reset:
        update_plan_tables(self)
    else:
        update_disp_brachy_plan(self)
        if hasattr(self, '_3D_brachy_table'):
            from fcn_3Dview.brachy_3D_table import repopulate_3D_brachy_table
            repopulate_3D_brachy_table(self)


def _refresh(self):
    """Tables, list, plots and images after the plan changed (without asking for the RTDOSE again)."""
    if self.brachy_combobox_01.currentText() == "Ref. Points":
        from fcn_display.brachy_tree import refresh_ref_points
        refresh_ref_points(self)
    else:
        commit_channel_edit(self)


# ---------------------------------------------------------------------------
# New, Save, Save as
# ---------------------------------------------------------------------------
def _write_plan(meta, series, pid, sid, name, template, new_uids):
    """
    Save a plan: dwell times in s, catheters numbered as written, the DICOM RT plan (DCM_Info)
    and the plan's DICOM fields from it (as for a loaded plan); remembered as saved.
    """
    from fcn_load.load_dcm import rtplan_metadata
    channels = meta.setdefault('Plan_Brachy_Channels', [])
    for k, ch in enumerate(channels):
        normalize_channel_times(ch)
        ch['ReferencedROINumber'] = k + 1  # its catheter (ROI) in the plan
    meta['ReferenceAirKermaRate'] = plan_sk(meta)
    uids, path = {}, ''
    if not new_uids:  # saved again: the same plan (and the file it was loaded from, if any)
        uids = {key: meta.get(field) for key, field in (('sop_uid', 'SOPInstanceUID'), ('series_uid', 'SeriesInstanceUID'))
                if meta.get(field) not in (None, '', 'N/A')}
        path = meta.get('OriginalFilePath') or ''
    ds = build_brachy_rtplan(meta, name, template, patient_id=pid, study_id=sid,
                             series_number=series.get('SeriesNumber', 1), **uids)
    meta.update(rtplan_metadata(ds, file_path=path))
    meta[SAVED_KEY] = True
    remember_saved_state(meta)
    return ds


def _plan_saved(self, pid, sid, idx):
    """After a plan was saved in place: its label, its metadata (if shown) and the tables."""
    from fcn_display.meta_viewer import update_meta_view_table_dicom
    update_plan_tree_label(self, pid, sid, idx)
    if getattr(self, 'modality', None) == 'RTPLAN' and (self.patientID, self.studyID, self.series_index) == (pid, sid, idx):
        update_meta_view_table_dicom(self, self.medical_image[pid][sid]['RTPLAN'][idx]['metadata']['DCM_Info'])
    _refresh(self)


def brachy_new_plan(self):
    """New: an empty brachy plan (no catheters, Sk 40700 U) for the image shown; in the data tree, not saved."""
    _finish_editing(self)
    found = _image_series(self)
    if found is None:
        QMessageBox.warning(self, "New plan", "Load an image first (click an image series in the data tree): "
                                              "the catheters of the plan are placed on it.")
        return
    pid, sid, image = found
    study = self.medical_image[pid][sid]
    plans = study.setdefault('RTPLAN', [])
    meta = {'Plan_Brachy_Channels': [], 'Plan_Dose_References': [], 'ReferenceAirKermaRate': DEFAULT_SK_U}
    series = {'SeriesNumber': _next_series_number(study), 'metadata': meta, 'images': {},
              'ImagePositionPatients': [], 'SliceImageComments': {}}
    # patient, study and frame of reference of the image
    template = image.get('metadata', {}).get('DCM_Info') if image is not None else None
    _write_plan(meta, series, pid, sid, _unique_name(plans, "New plan"), template, new_uids=True)
    meta[SAVED_KEY] = False
    plans.append(series)
    _show_plan(self, pid, sid, len(plans) - 1, reset=True)


def brachy_save_plan(self):
    """Save: a plan made in AMIGOpy into the data tree (as a DICOM RT plan); other plans and new ones: Save as."""
    plan = _current_plan(self)
    if plan is None:
        QMessageBox.warning(self, "Save plan", "No brachy plan loaded.")
        return
    pid, sid, idx, series = plan
    meta = series['metadata']
    if not is_amigo_plan(meta) or plan_never_saved(meta):
        brachy_save_plan_as(self)
        return
    _finish_editing(self)
    _write_plan(meta, series, pid, sid, plan_display_name(meta), meta.get('DCM_Info'), new_uids=False)
    _plan_saved(self, pid, sid, idx)


def brachy_save_plan_as(self):
    """
    Save as: the plan as it is now, with a name, as a new plan made in AMIGOpy in the data
    tree; the plan it came from goes back to how it was last saved (or loaded). A new plan
    not saved yet is saved itself, with that name.
    """
    plan = _current_plan(self)
    if plan is None:
        QMessageBox.warning(self, "Save plan as", "No brachy plan loaded.")
        return
    pid, sid, idx, series = plan
    meta = series['metadata']
    name = plan_display_name(meta)
    first_save = is_amigo_plan(meta) and plan_never_saved(meta)
    if first_save:
        prompt, default = "Name of the plan:", name
    elif is_amigo_plan(meta):
        prompt, default = f"Name of the new plan (\"{name}\" keeps its last saved version):", f"{name} copy"
    else:
        prompt, default = (f"\"{name}\" was not made in {AMIGO_NAME}: it is saved as a new plan, made in {AMIGO_NAME}.\n"
                           f"\"{name}\" keeps its version as loaded.\n\nName of the new plan:"), f"{name} copy"
    text, ok = QInputDialog.getText(self, "Save plan as", prompt, text=default)
    name = text.strip()
    if not ok or not name:
        return
    _finish_editing(self)
    if first_save:
        _write_plan(meta, series, pid, sid, name, meta.get('DCM_Info'), new_uids=False)
        _plan_saved(self, pid, sid, idx)
        return
    study = self.medical_image[pid][sid]
    # the new plan takes the catheters and reference points being edited (their undo goes on there)
    new_meta = {key: val for key, val in meta.items() if key not in (SAVED_STATE_KEY, SAVED_KEY)}
    new_series = {'SeriesNumber': _next_series_number(study), 'metadata': new_meta, 'images': {},
                  'ImagePositionPatients': [], 'SliceImageComments': {}}
    restore_saved_state(meta)
    update_plan_tree_label(self, pid, sid, idx)
    _write_plan(new_meta, new_series, pid, sid, name, meta.get('DCM_Info'), new_uids=True)
    study['RTPLAN'].append(new_series)
    _show_plan(self, pid, sid, len(study['RTPLAN']) - 1, reset=False)


# ---------------------------------------------------------------------------
# Plan box
# ---------------------------------------------------------------------------
def update_brachy_plan_box(self):
    """Plan box: title (name; not saved / changed), buttons; and the plan's data tree label."""
    group = getattr(self, 'brachy_plan_group', None)
    if group is None:
        return
    plan = _current_plan(self)
    for name in ('brachy_save_plan_btn', 'brachy_save_plan_as_btn'):
        widget = getattr(self, name, None)
        if widget is not None:
            widget.setEnabled(plan is not None)
    if plan is None:
        group.setTitle("Plan")
        group.setToolTip("No brachy plan shown: click one in the data tree, or New")
        return
    pid, sid, idx, series = plan
    meta = series['metadata']
    name = plan_display_name(meta)
    if plan_never_saved(meta):
        state, note = " (not saved)", "\nNew plan, not saved yet."
    elif plan_modified(meta):
        state, note = " *", "\nChanged since it was saved: Save to keep the changes."
    else:
        state, note = "", ""
    group.setTitle(f"Plan: {QFontMetrics(group.font()).elidedText(name, Qt.ElideRight, TITLE_WIDTH_PX)}{state}")
    origin = f"Made in {AMIGO_NAME}" if is_amigo_plan(meta) else f"Loaded (made by {meta.get('Manufacturer') or 'N/A'})"
    group.setToolTip(f"{name}\n{origin}.{note}")
    update_plan_tree_label(self, pid, sid, idx)


# ---------------------------------------------------------------------------
# Export (data tree)
# ---------------------------------------------------------------------------
def export_rtplan(self, pid, sid, idx):
    """Export DCM in the data tree: a plan, as last saved (or loaded), to a DICOM file."""
    try:
        meta = self.medical_image[pid][sid]['RTPLAN'][idx]['metadata']
    except (KeyError, IndexError, TypeError):
        return
    ds, name = meta.get('DCM_Info'), plan_display_name(meta)
    if not isinstance(ds, Dataset):
        QMessageBox.warning(self, "Export RT plan", f"\"{name}\" has no DICOM data to export.")
        return
    if plan_never_saved(meta):
        QMessageBox.information(self, "Export RT plan", f"\"{name}\" is not saved yet: save it first "
                                                        "(View > PLAN > Brachy, Plan: Save).")
        return
    if plan_modified(meta):
        answer = QMessageBox.question(self, "Export RT plan", f"\"{name}\" has changes that are not saved: the file "
                                                              "has the plan as last saved.\n\nExport it anyway?")
        if answer != QMessageBox.Yes:
            return
    file_name = "RP_" + "".join(c if c.isalnum() or c in "-_." else "_" for c in name) + ".dcm"
    path, _ = QFileDialog.getSaveFileName(self, "Export RT plan", file_name, "DICOM files (*.dcm);;All files (*)")
    if not path:
        return
    try:
        try:
            pydicom.dcmwrite(path, ds, enforce_file_format=True)
        except (AttributeError, ValueError):  # no file meta information (e.g. read with force=True)
            pydicom.dcmwrite(path, ds)
    except Exception as e:
        QMessageBox.critical(self, "Export RT plan", f"The plan could not be written to\n{path}\n\n{e}")
        return
    label = getattr(self, 'label_2', None)
    if label is not None:
        label.setText(f"RT plan exported: {path}")
        label.show()
