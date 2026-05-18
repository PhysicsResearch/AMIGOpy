from fcn_load.sort_dcm import get_data_description
import shutil
import os
import math
import pydicom
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox

# ---------- Qt helpers ---------------------------------------------------------
def _ensure_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def get_folder_path_from_dialog(parent: QWidget | None = None) -> str | None:
    """Open a Qt directory picker and return the selected path or None."""
    _ensure_app()
    folder_path = QFileDialog.getExistingDirectory(parent, "Select an output folder")
    return folder_path or None

def show_warning(message: str, parent: QWidget | None = None) -> None:
    _ensure_app()
    QMessageBox.warning(parent, "Warning", message)

# ---------- utils --------------------------------------------------------------
def compare_file_counts(detailed_files_info, root_destination):
    """
    Compare the number of files in detailed_files_info with the number of files
    found under root_destination.
    """
    original_file_count = len(detailed_files_info)
    copied_file_count = sum(len(files) for _, _, files in os.walk(root_destination))
    return original_file_count == copied_file_count, abs(original_file_count - copied_file_count)

def generate_patient_id_map(detailed_files_info, max_length=30):
    patient_id_map = {}
    short_name_counter = 1
    for info in detailed_files_info:
        patient_id = info["PatientID"]
        if len(patient_id) > max_length:
            if patient_id not in patient_id_map:
                patient_id_map[patient_id] = f"Pat_{short_name_counter:02d}"
                short_name_counter += 1
        else:
            patient_id_map[patient_id] = patient_id
    return patient_id_map

def make_hashable(val):
    if isinstance(val, (list, pydicom.multival.MultiValue)):
        return tuple(val)
    return val

def remove_and_count_duplicates(detailed_files_info):
    """
    Remove duplicate entries (second and later appearances) and return
    (cleaned_list, duplicate_count).
    """
    file_info = [
        (
            make_hashable(info['StudyID']),
            make_hashable(info['Modality']),
            make_hashable(info['SeriesTime']),
            make_hashable(info['KVP']),
            make_hashable(info['InstanceNumber']),
            make_hashable(info['SOPInstanceUID']),
            make_hashable(info['ImagePatientPosition']),
        )
        for info in detailed_files_info
    ]

    file_counts = {}
    duplicate_indices = []
    for index, key in enumerate(file_info):
        if file_counts.get(key, 0) >= 1:
            duplicate_indices.append(index)
        file_counts[key] = file_counts.get(key, 0) + 1

    for index in sorted(duplicate_indices, reverse=True):
        del detailed_files_info[index]

    duplicate_count = len(duplicate_indices)
    return detailed_files_info, duplicate_count

# ---------- main worker --------------------------------------------------------
def organize_files_into_folders(root_destination,
                                detailed_files_info,
                                progress_callback=None,
                                update_label=None,
                                dialog_parent: QWidget | None = None):
    """
    Organize files into a hierarchical folder structure based on metadata.

    :param root_destination: Root folder where patient/study/modality/series are created.
    :param detailed_files_info: List[dict] with DICOM file metadata.
    :param progress_callback: Callable[int] to update progress (0-100).
    :param update_label: QLabel-like object with setText(str), or None.
    :param dialog_parent: Optional QWidget parent for any modal dialogs.
    """
    # De-dup
    detailed_files_info, duplicate_count = remove_and_count_duplicates(detailed_files_info)
    if duplicate_count > 0:
        warning_message = f"{duplicate_count} duplicate files found."
        if update_label:
            update_label.setText(warning_message)
        else:
            print(warning_message)
        show_warning(warning_message, parent=dialog_parent)

    total_steps = len(detailed_files_info)

    # If no destination was given, ask the user (kept for flexibility)
    if not root_destination:
        if update_label:
            update_label.setText("Please select the root destination folder ...")
        else:
            print("Please select the root destination folder ...")
        root_destination = get_folder_path_from_dialog(dialog_parent)

    if not root_destination:
        if update_label:
            update_label.setText("No folder selected. Exiting the organizing process.")
        else:
            print("No folder selected. Exiting the organizing process.")
        return

    if progress_callback:
        progress_callback(0)

    if update_label:
        update_label.setText(f"Copying {total_steps} files")
    else:
        print("Copying the files")

    patient_id_map = generate_patient_id_map(detailed_files_info)

    # Ensure root exists
    os.makedirs(root_destination, exist_ok=True)

    for index, info in enumerate(detailed_files_info):
        mapped_patient_id = patient_id_map[info["PatientID"]]

        # hierarchy
        patient_folder = os.path.join(root_destination, mapped_patient_id)
        study_folder   = os.path.join(patient_folder, "Study_" + info["StudyID"])
        modality_folder = os.path.join(study_folder, info["Modality"])

        # series folder name
        if info["AcquisitionDate"] == 'N/A':
            year_short, month_day, hour_minute = '', '', ''
        else:
            year_short  = info["AcquisitionDate"][-2:]
            month_day   = info["AcquisitionDate"][4:8]
            hour_minute = info["ReferenceTime"][:4]

        LUTe = '' if info.get('LUTExplanation', 'N/A') == 'N/A' else info['LUTExplanation']
        LUTl = '' if info.get('LUTLabel', 'N/A') == 'N/A' else info['LUTLabel']

        if info.get('KVP'):
            series_folder_name = f"S_{year_short}{month_day}_{hour_minute}_{info['SeriesNumber']}_{info['KVP']}kV_{LUTe}_{LUTl}"
        else:
            series_folder_name = f"S_{year_short}{month_day}_{hour_minute}_{info['SeriesNumber']}_{LUTe}_{LUTl}"

        series_folder = os.path.join(modality_folder, series_folder_name)

        # create dirs
        os.makedirs(series_folder, exist_ok=True)

        # copy file
        destination_file_path = os.path.join(series_folder, os.path.basename(info["FilePath"]))
        shutil.copy2(info["FilePath"], destination_file_path)

        # progress
        if progress_callback:
            progress = math.ceil((index + 1) / total_steps * 100) if total_steps else 100
            progress_callback(progress)

    # finalize
    if update_label:
        update_label.setText("Done - going to check the number of files now")
    else:
        print("Done - going to check the number of files now")

    # Compare file counts against the ROOT (not last patient folder)
    ok, diff = compare_file_counts(detailed_files_info, root_destination)
    if ok:
        msg = "All files successfully copied. Excluding duplicated files if any."
    else:
        msg = f"File count mismatch by {diff} files. Please verify. Excluding duplicated files if any."

    if update_label:
        update_label.setText(msg)
    else:
        print(msg)

# ---------- CLI use ------------------------------------------------------------
if __name__ == "__main__":
    # Minimal interactive run (asks for dest if not given by get_data_description)
    _ensure_app()
    detailed_files_info, unique_files_info, outputfolder = get_data_description(sort_folder=1)
    organize_files_into_folders(outputfolder, detailed_files_info, dialog_parent=None)
