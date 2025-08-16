from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QDialog, QMessageBox
from fcn_display.Data_tree_general import on_DataTreeView_clicked
from fcn_export.export_dcm import export_dicom_series
from fcn_export.export_nii import export_nifti
from fcn_load.populate_dcm_list import populate_DICOM_tree
from fcn_init.datatree_selection_box import SeriesPickerDialog
import copy
from fcn_load.populate_dcm_list import populate_DICOM_tree
import numpy as np


def set_context_menu(self):
    """
    Set the context menu for the DataTreeView.
    This method connects the custom context menu request signal to the handler.
    """
    # Ensure the DataTreeView has a context menu policy set 
    self.DataTreeView.setContextMenuPolicy(Qt.CustomContextMenu)
    self.DataTreeView.customContextMenuRequested.connect(lambda pos: on_tree_context_menu(self,pos))



def on_tree_context_menu(self, pos):
    idx = self.DataTreeView.indexAt(pos)
    if not idx.isValid():
        return

    item = self.model.itemFromIndex(idx)
    model = self.DataTreeView.model()

    # Build hierarchy path and indices
    current_index = idx
    hierarchy = []
    hierarchy_indices = []
    while current_index.isValid():
        hierarchy.append(model.itemFromIndex(current_index).text())
        hierarchy_indices.append(current_index)
        current_index = current_index.parent()
    hierarchy.reverse()
    hierarchy_indices.reverse()

    # Print the hierarchy for debugging
    print("Hierarchy:", hierarchy)

    # Parse levels
    Type = hierarchy[0] if len(hierarchy) >= 1 else None
    Patient = hierarchy[1].replace("PatientID: ", "") if len(hierarchy) >= 2 else None
    Study = hierarchy[2].replace("StudyID: ", "") if len(hierarchy) >= 3 else None
    Modality = hierarchy[3].replace("Modality: ", "") if len(hierarchy) >= 4 else None
    Series = hierarchy_indices[4].row() if len(hierarchy) >= 5 else None
    Series_sub_data = hierarchy[5] if len(hierarchy) >= 6 else None

    # -------------------------
    # Series-level 
    # -------------------------
    if Type == "DICOM" and len(hierarchy) == 5:
        menu = QMenu()
        open_action        = menu.addAction("Open…")

        currentTabText = self.tabModules.tabText(self.tabModules.currentIndex())
        reset_view = None
        if currentTabText == "View":
            reset_view = menu.addAction("Reset view …")

        exp_action_dcm     = menu.addAction("Export DCM")
        exp_action_nii     = menu.addAction("Export Nifti")
        delete_action      = menu.addAction("Delete series")

        action = menu.exec_(self.DataTreeView.viewport().mapToGlobal(pos))
        if action == open_action:
            on_DataTreeView_clicked(self, idx)
        elif reset_view and action == reset_view:
            adjust_reset_view(self)
        elif action == delete_action:
            # optional confirm:
            # if not _confirm(self, "Delete series", f"Delete series at {Patient}/{Study}/{Modality}[{Series}]?"): return
            delete_series(self, Patient, Study, Modality, Series)
            populate_DICOM_tree(self)
        elif action == exp_action_dcm:
            meta_data   = self.dicom_data[Patient][Study][Modality][Series]['metadata'].get('DCM_Info')
            data        = self.dicom_data[Patient][Study][Modality][Series]['3DMatrix']
            slice_thick = self.dicom_data[Patient][Study][Modality][Series]['metadata']['SliceThickness']
            if meta_data is None:
                print("No DICOM header available for export (likely NIfTI-derived).")
            else:
                export_dicom_series(meta_data, data, slice_thick, output_folder=None)
        elif action == exp_action_nii:
            export_nifti(self, Patient, Study, Modality, Series,output_folder=None, file_name=None)


    # -------------------------
    # Modality-level
    # -------------------------
    if Type == "DICOM" and len(hierarchy) == 4:
        menu = QMenu()
        delete_action = menu.addAction(f"Delete modality '{Modality}' and all series")
        action = menu.exec_(self.DataTreeView.viewport().mapToGlobal(pos))
        if action == delete_action:
            # if not _confirm(self, "Delete modality", f"Delete {Patient}/{Study}/{Modality} (all series)?"): return
            delete_modality(self, Patient, Study, Modality)
            populate_DICOM_tree(self)

    # -------------------------
    # Study-level
    # -------------------------
    if Type == "DICOM" and len(hierarchy) == 3:
        menu = QMenu()
        delete_action = menu.addAction(f"Delete study '{Study}' and everything underneath")
        action = menu.exec_(self.DataTreeView.viewport().mapToGlobal(pos))
        if action == delete_action:
            # if not _confirm(self, "Delete study", f"Delete {Patient}/{Study} (all modalities/series)?"): return
            delete_study(self, Patient, Study)
            populate_DICOM_tree(self)

    # -------------------------
    # Patient-level
    # -------------------------
    if Type == "DICOM" and len(hierarchy) == 2:
        menu = QMenu()
        delete_action = menu.addAction(f"Delete patient '{Patient}' and everything underneath")
        action = menu.exec_(self.DataTreeView.viewport().mapToGlobal(pos))
        if action == delete_action:
            # if not _confirm(self, "Delete patient", f"Delete {Patient} (all studies/modalities/series)?"): return
            delete_patient(self, Patient)
            populate_DICOM_tree(self)

    # -------------------------
    # DICOM root-level
    # -------------------------
    if Type == "DICOM" and len(hierarchy) == 1:
        menu = QMenu()
        delete_action = menu.addAction("Delete ALL DICOM data")
        action = menu.exec_(self.DataTreeView.viewport().mapToGlobal(pos))
        if action == delete_action:
            # if not _confirm(self, "Delete all", "Delete ALL DICOM data?"): return
            delete_all_dicom(self)
            populate_DICOM_tree(self)



    # -------------------------
    if Type == "DICOM" and len(hierarchy) == 6 and Series_sub_data == "Structures":
        # Build your menu
        menu = QMenu()
        copy_action        = menu.addAction("Copy structures to…")
        delete_action      = menu.addAction("Delete")
        
        # Pop up the menu at the global screen position
        action = menu.exec_(self.DataTreeView.viewport().mapToGlobal(pos))
        if action == copy_action:
            print("Copy action triggered")
            on_copy_structures_from_tree_item(self, Patient, Study, Modality, Series)
            # on_DataTreeView_clicked(self,idx)   
        elif action == delete_action:
            print("Delete action triggered")
            delete_structure_set(self, Patient, Study, Modality, Series)
            populate_DICOM_tree(self)


def adjust_reset_view(self):
    """
    Reset the camera view in all three VTK widgets.
    """
    self.renAxial.ResetCamera()
    self.renSagittal.ResetCamera()
    self.renCoronal.ResetCamera()
    self.vtkWidgetAxial.GetRenderWindow().Render()
    self.vtkWidgetSagittal.GetRenderWindow().Render()
    self.vtkWidgetCoronal.GetRenderWindow().Render()


def _cleanup_empty_levels(self, patient_id, study_id=None):
    """
    After a deletion, remove any empty dict/list levels up the chain.
    """
    try:
        if study_id is not None:
            # If modality dict for this study is empty, drop the study
            if not self.dicom_data.get(patient_id, {}).get(study_id, {}):
                self.dicom_data.get(patient_id, {}).pop(study_id, None)
        # If patient dict is now empty, drop the patient
        if not self.dicom_data.get(patient_id, {}):
            self.dicom_data.pop(patient_id, None)
    except Exception:
        pass

def delete_series(self, patient_id, study_id, modality, series_index: int):
    try:
        series_list = self.dicom_data[patient_id][study_id][modality]
        if 0 <= series_index < len(series_list):
            series_list.pop(series_index)
            # If modality list now empty, remove it and clean upwards
            if not series_list:
                self.dicom_data[patient_id][study_id].pop(modality, None)
                _cleanup_empty_levels(self, patient_id, study_id)
        else:
            print(f"Series index {series_index} out of range.")
    except KeyError:
        print("Invalid path when deleting series.")

def delete_modality(self, patient_id, study_id, modality):
    try:
        self.dicom_data[patient_id][study_id].pop(modality, None)
        _cleanup_empty_levels(self, patient_id, study_id)
    except KeyError:
        print("Invalid path when deleting modality.")

def delete_study(self, patient_id, study_id):
    try:
        self.dicom_data[patient_id].pop(study_id, None)
        _cleanup_empty_levels(self, patient_id, study_id=None)
    except KeyError:
        print("Invalid path when deleting study.")

def delete_patient(self, patient_id):
    try:
        self.dicom_data.pop(patient_id, None)
    except KeyError:
        print("Invalid path when deleting patient.")

def delete_all_dicom(self):
    self.dicom_data = {}


def delete_structure_set(self, src_patient, src_study, src_modality, src_series_index):
    """
    Remove all structure-related data from a series, safely:
      - 'structures', 'structures_names', 'structures_keys'
      - 'structures_view', 'structures_color', 'structures_line_width', 'structures_transparency'
    If the deleted series is the one currently displayed, remove overlay actors and clear the list UI.
    Returns True if anything was deleted, else False.
    """
    # ---- locate the series dict safely ----
    try:
        s_series = self.dicom_data[src_patient][src_study][src_modality][src_series_index]
    except (KeyError, IndexError, TypeError):
        return False

    # ---- if this is the currently displayed series, remove any overlay actors ----
    is_current = (
        getattr(self, 'patientID', None)   == src_patient  and
        getattr(self, 'studyID', None)     == src_study    and
        getattr(self, 'modality', None)    == src_modality and
        getattr(self, 'series_index', None)== src_series_index
    )
    if is_current:
        # Axial
        try:
            ren_ax = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()
            for a in getattr(self, 'structure_actors_ax', []):
                try: ren_ax.RemoveActor(a)
                except Exception: pass
            self.structure_actors_ax = []
        except Exception:
            pass
        # Sagittal
        try:
            ren_sa = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()
            for a in getattr(self, 'structure_actors_sa', []):
                try: ren_sa.RemoveActor(a)
                except Exception: pass
            self.structure_actors_sa = []
        except Exception:
            pass
        # Coronal
        try:
            ren_co = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()
            for a in getattr(self, 'structure_actors_co', []):
                try: ren_co.RemoveActor(a)
                except Exception: pass
            self.structure_actors_co = []
        except Exception:
            pass

    # ---- delete structure-related keys safely ----
    keys_to_delete = [
        'structures',
        'structures_names',
        'structures_keys',
        'structures_view',
        'structures_color',
        'structures_line_width',
        'structures_transparency',
    ]
    deleted_any = False
    for k in keys_to_delete:
        if k in s_series:
            s_series.pop(k, None)
            deleted_any = True

    # ---- clear the UI list if we’re looking at this series ----
    if is_current and hasattr(self, 'STRUCTlist') and self.STRUCTlist is not None:
        try:
            self.STRUCTlist.clear()
        except Exception:
            pass

    # ---- quick re-render of the three views (cheap) ----
    if is_current:
        try: self.vtkWidgetAxial.GetRenderWindow().Render()
        except Exception: pass
        try: self.vtkWidgetSagittal.GetRenderWindow().Render()
        except Exception: pass
        try: self.vtkWidgetCoronal.GetRenderWindow().Render()
        except Exception: pass

    return deleted_any


def on_copy_structures_from_tree_item(self, src_patient, src_study, src_modality, src_series_index):
    excluded = {'RTPLAN','RTSTRUCT','RTDOSE'}
    dlg = SeriesPickerDialog(
        self.dicom_data,
        excluded_modalities=excluded,
        source_tuple=(src_patient, src_study, src_modality, src_series_index),
        parent=self
    )
    if dlg.exec_() != QDialog.Accepted:
        return

    dst_patient = dlg.selected_patient
    (series_label, dst_study, dst_modality, dst_series_index) = dlg.selected_series_tuple

    compatible, diffs = check_series_compatibility(
        self.dicom_data,
        src=(src_patient, src_study, src_modality, src_series_index),
        dst=(dst_patient, dst_study, dst_modality, dst_series_index),
        tol=1e-6
    )
    if not compatible:
        details = ", ".join(diffs)
        m = QMessageBox(self)
        m.setIcon(QMessageBox.Warning)
        m.setWindowTitle("Compatibility warning")
        m.setText(
            "Differences detected between original and destination.\n\n"
            "Copy function does not account for different resolution, sizes and reference positions.\n"
            "It is intended only for multiple reconstructions of the same image; this is NOT image registration.\n"
            "Proceeding may cause other functions to crash.\n\n"
            f"Differing fields: {details}\n\n"
            "Do you want to proceed anyway?"
        )
        m.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        m.button(QMessageBox.Yes).setText("Proceed")
        m.button(QMessageBox.No).setText("Cancel")
        if m.exec_() != QMessageBox.Yes:
            return

    # Destination series dict
    try:
        dst_series = self.dicom_data[dst_patient][dst_study][dst_modality][dst_series_index]
    except (KeyError, IndexError, TypeError):
        QMessageBox.warning(self, "Error", "Destination series not found.")
        return

    def _dst_has_structs(s):
        return (
            isinstance(s.get('structures'), dict) and s['structures'] or
            (isinstance(s.get('structures_names'), list) and s['structures_names']) or
            (isinstance(s.get('structures_keys'), list) and s['structures_keys'])
        )

    mode = 'overwrite'
    if _dst_has_structs(dst_series):
        q = QMessageBox(self)
        q.setIcon(QMessageBox.Question)
        q.setWindowTitle("Destination already has structures")
        q.setText("The destination series already contains structures.\n\nHow would you like to proceed?")
        merge_btn   = q.addButton("Merge", QMessageBox.ActionRole)
        replace_btn = q.addButton("Replace", QMessageBox.DestructiveRole)
        cancel_btn  = q.addButton(QMessageBox.Cancel)
        q.setDefaultButton(merge_btn)
        q.exec_()
        clicked = q.clickedButton()
        if clicked is cancel_btn:
            return
        mode = 'merge' if clicked is merge_btn else 'overwrite'

        # Snapshot current key order + state to preserve on merge
        if mode == 'merge':
            dst_series['_prev_structures_keys'] = list(dst_series.get('structures_keys', []))
        else:
            # Replace: clear everything so state recreates fresh
            try:
                self.delete_structure_set(dst_patient, dst_study, dst_modality, dst_series_index)
            except Exception:
                pass

    # Do the copy
    ok, msg = copy_structures_between_series(
        self.dicom_data,
        src=(src_patient, src_study, src_modality, src_series_index),
        dst=(dst_patient, dst_study, dst_modality, dst_series_index),
        mode=mode  # 'merge' or 'overwrite'
    )
    print("Copy result:", ok, msg)
    if not ok:
        return

    # After successful copy:
    _clear_structure_display_state(dst_series)


    # Refresh UI
    populate_DICOM_tree(self)


def _clear_structure_display_state(series):
    for k in ('structures_view','structures_color','structures_line_width','structures_transparency'):
        series.pop(k, None)


def _equalish(a, b, tol=1e-6):
    if a is None or b is None:
        return a is None and b is None
    # sequences (PixelSpacing, ImagePositionPatient often lists/tuples)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return False
        # numeric tolerant compare where possible
        def as_float(x):
            try: return float(x)
            except Exception: return x
        aa = [as_float(x) for x in a]
        bb = [as_float(x) for x in b]
        return all((abs(x - y) <= tol) if isinstance(x,(int,float)) and isinstance(y,(int,float)) else (x == y)
                   for x, y in zip(aa, bb))
    # numbers (strings fall back to ==)
    try:
        af = float(a); bf = float(b)
        return abs(af - bf) <= tol
    except Exception:
        return a == b

def _shape_of_3d(x):
    if x is None:
        return None
    arr = np.asarray(x)
    return tuple(arr.shape)

def check_series_compatibility(dicom_data, src, dst, tol=1e-6):
    """
    Return (compatible: bool, differences: list[str])
    Compares:
      - metadata['SliceThickness'] (tolerant numeric compare)
      - metadata['PixelSpacing'] (elementwise tolerant compare)
      - metadata['ImagePositionPatient'] (elementwise tolerant compare)
      - 3DMatrix **shape only** (no content check)
    """
    sp, ss, sm, si = src
    dp, ds, dm, di = dst

    s = dicom_data[sp][ss][sm][si]
    d = dicom_data[dp][ds][dm][di]

    diffs = []

    def get_meta(x, key, default=None):
        return x.get('metadata', {}).get(key, default)

    # Metadata value checks (as before)
    if not _equalish(get_meta(s, "SliceThickness"), get_meta(d, "SliceThickness"), tol):
        diffs.append("SliceThickness")
    if not _equalish(get_meta(s, "PixelSpacing"), get_meta(d, "PixelSpacing"), tol):
        diffs.append("PixelSpacing")
    if not _equalish(get_meta(s, "ImagePositionPatient"), get_meta(d, "ImagePositionPatient"), tol):
        diffs.append("ImagePositionPatient")

    # 3DMatrix: compare shapes only
    s_shape = _shape_of_3d(s.get("3DMatrix"))
    d_shape = _shape_of_3d(d.get("3DMatrix"))
    if s_shape != d_shape:
        diffs.append(f"3DMatrix shape {s_shape} vs {d_shape}")

    return (len(diffs) == 0, diffs)


def copy_structures_between_series(dicom_data, src, dst, mode='overwrite'):
    """
    src, dst: (patient_id, study_id, modality, series_index)
    mode: 'overwrite' or 'merge'
    Skips copying the 'VTKActors2D' and 'Contours2D' fields inside each structure.
    """
    sp, ss, sm, si = src
    dp, ds, dm, di = dst

    s_series = dicom_data[sp][ss][sm][si]
    d_series = dicom_data[dp][ds][dm][di]

    src_names = s_series.get('structures_names')
    src_keys  = s_series.get('structures_keys')
    src_dict  = s_series.get('structures')

    if src_dict is None:
        return False, "Source has no 'structures' to copy."

    if src_names is None and isinstance(src_dict, dict):
        src_names = [src_dict[k].get('Name', k) for k in src_dict.keys()]
    if src_keys is None and isinstance(src_dict, dict):
        src_keys = list(src_dict.keys())

    # Helper: make a filtered deep copy
    def filtered_copy(struct):
        new_struct = {}
        for key, value in struct.items():
            if key not in ("VTKActors2D", "Contours2D"):
                new_struct[key] = copy.deepcopy(value)
        return new_struct

    if mode == 'overwrite':
        d_series['structures'] = {k: filtered_copy(v) for k, v in src_dict.items()}
        if src_names is not None:
            d_series['structures_names'] = copy.deepcopy(src_names)
        if src_keys is not None:
            d_series['structures_keys'] = copy.deepcopy(src_keys)

    elif mode == 'merge':
        d_series.setdefault('structures', {})
        for k, v in src_dict.items():
            d_series['structures'][k] = filtered_copy(v)
        d_series['structures_keys']  = list(d_series['structures'].keys())
        d_series['structures_names'] = [
            d_series['structures'][k].get('Name', k)
            for k in d_series['structures_keys']
        ]
    else:
        return False, f"Unknown mode: {mode}"

    return True, "Structures copied."