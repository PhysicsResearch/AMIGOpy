from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QDialog, QMessageBox
from fcn_display.Data_tree_general import on_DataTreeView_clicked
from fcn_export.export_dcm import export_dicom_series
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
    # Map the click into an index in the model
    idx = self.DataTreeView.indexAt(pos)
    if not idx.isValid():
        return

    # Get the corresponding QStandardItem, if you need it
    item = self.model.itemFromIndex(idx)
    print(item)

    model = self.DataTreeView.model()
    #
    # check file type
    # Extract hierarchy information based on the clicked index
    current_index = idx
    hierarchy = []
    hierarchy_indices = []
    while current_index.isValid():
        hierarchy.append(model.itemFromIndex(current_index).text())
        hierarchy_indices.append(current_index)
        current_index = current_index.parent()
    # Reverse the hierarchy data so it starts from the topmost level
    hierarchy.reverse()
    hierarchy_indices.reverse()

    # Print the hierarchy for debugging
    print("Hierarchy:", hierarchy)

    if len(hierarchy) >= 1: 
        Type = hierarchy[0]
    if len(hierarchy) >= 2:
        Patient = hierarchy[1].replace("PatientID: ", "")
    if len(hierarchy) >= 3:
        Study = hierarchy[2].replace("StudyID: ", "")
    if len(hierarchy) >= 4:     
        Modality = hierarchy[3].replace("Modality: ", "")
    if len(hierarchy) >= 5:
        Series = hierarchy_indices[4].row()
    if len(hierarchy) >= 6:
        Series_sub_data = hierarchy[5]

    if Type == "DICOM" and len(hierarchy) == 5:
        # Build your menu
        menu = QMenu()
        open_action        = menu.addAction("Open…")
        exp_action_dcm     = menu.addAction("Export DCM")
        exp_action_np      = menu.addAction("Export NumPy")
        delete_action      = menu.addAction("Delete")
        
        # Pop up the menu at the global screen position
        action = menu.exec_(self.DataTreeView.viewport().mapToGlobal(pos))
        if action == open_action:
            print("Open action triggered")
            on_DataTreeView_clicked(self,idx)
   
        elif action == delete_action:
            print("Delete action triggered")
            delete_series(self, Patient, Study, Modality, Series)
            populate_DICOM_tree(self)
        elif action == exp_action_dcm:
            print("Export action triggered")
            meta_data   = self.dicom_data[Patient][Study][Modality][Series]['metadata']['DCM_Info']
            data        = self.dicom_data[Patient][Study][Modality][Series]['3DMatrix']
            slice_thick = self.dicom_data[Patient][Study][Modality][Series]['metadata']['SliceThickness']
            export_dicom_series(meta_data, data, slice_thick, output_folder=None)

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
            delete_series(self, Patient, Study, Modality, Series)
            populate_DICOM_tree(self)

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

    # 1) compatibility check
    compatible, diffs = check_series_compatibility(
        self.dicom_data,
        src=(src_patient, src_study, src_modality, src_series_index),
        dst=(dst_patient, dst_study, dst_modality, dst_series_index),
        tol=1e-6
    )

    if not compatible:
        # Build warning text
        details = ", ".join(diffs)
        text = (
            "Differences detected between original and destination.\n\n"
            "Copy function does not account for different resolution, sizes and reference positions.\n"
            "It is intended only for multiple reconstructions of the same image; this is NOT image registration.\n"
            "Proceeding may cause other functions to crash.\n\n"
            f"Differing fields: {details}\n\n"
            "Do you want to proceed anyway?"
        )
        m = QMessageBox(self)
        m.setIcon(QMessageBox.Warning)
        m.setWindowTitle("Compatibility warning")
        m.setText(text)
        m.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        # rename buttons to Proceed / Cancel
        yes_btn = m.button(QMessageBox.Yes); yes_btn.setText("Proceed")
        no_btn  = m.button(QMessageBox.No);  no_btn.setText("Cancel")

        if m.exec_() != QMessageBox.Yes:
            return  # user cancelled

    # 2) copy
    ok, msg = copy_structures_between_series(
        self.dicom_data,
        src=(src_patient, src_study, src_modality, src_series_index),
        dst=(dst_patient, dst_study, dst_modality, dst_series_index),
        mode='overwrite'  # or 'merge'
    )
    print("Copy result:", ok, msg)

    # 3) refresh tree if needed
    if ok:
        populate_DICOM_tree(self)


def delete_series(self, Patient, Study, Modality, Series):
    """
    Deletes the series at index 'Series' (int) from self.dicom_data[Patient][Study][Modality] (a list).
    After deletion, recursively removes empty parent containers: Modality, Study, Patient.
    """
    # Step 1: Try to delete the series
    try:
        series_list = self.dicom_data[Patient][Study][Modality]
        del series_list[Series]
        print(f"Series at index {Series} deleted.")
    except (KeyError, IndexError):
        print(f"Series index {Series} not found for {Patient}, {Study}, {Modality}.")
        return

    # Step 2: If the list is empty, delete the Modality key from the dict
    if not series_list:
        del self.dicom_data[Patient][Study][Modality]
        print(f"Modality '{Modality}' deleted (was empty).")

        # Step 3: If Study dict is now empty, delete Study key
        if not self.dicom_data[Patient][Study]:
            del self.dicom_data[Patient][Study]
            print(f"Study '{Study}' deleted (was empty).")

            # Step 4: If Patient dict is now empty, delete Patient key
            if not self.dicom_data[Patient]:
                del self.dicom_data[Patient]
                print(f"Patient '{Patient}' deleted (was empty).")

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
    (Same as before; no dialog logic in here so it's testable.)
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

    if mode == 'overwrite':
        d_series['structures'] = copy.deepcopy(src_dict)
        if src_names is not None:
            d_series['structures_names'] = copy.deepcopy(src_names)
        if src_keys is not None:
            d_series['structures_keys'] = copy.deepcopy(src_keys)
    elif mode == 'merge':
        d_series.setdefault('structures', {})
        for k, v in src_dict.items():
            d_series['structures'][k] = copy.deepcopy(v)
        d_series['structures_keys']  = list(d_series['structures'].keys())
        d_series['structures_names'] = [d_series['structures'][k].get('Name', k)
                                        for k in d_series['structures_keys']]
    else:
        return False, f"Unknown mode: {mode}"

    return True, "Structures copied."