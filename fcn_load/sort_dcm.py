"""
Script: DICOM and IMA File Analyzer (also works with files in the DICOM format but without an extension)

Purpose:
- Inspect DICOM and IMA files in a specified directory.
- Recursively check folders and subfolders.
- Extract DICOM headers containing patient ID, study, series, and modality information.
- Group files based on extracted information.
- Generate a list of file paths and unique tags without loading image data.

Usage:
1) Command Line without arguments:
   $ python sort_dcm.py 
   [Prompts user interactively to select a folder]

2) Command Line with a directory argument:
   $ python sort_dcm.py -d c:\Path2YourFolder

3) In another script:
   from sort_dcm import get_data_description
   all_files, unique_combinations = get_data_description() 
   OR 
   all_files, unique_combinations = get_data_description("c:\Path2YourFolder")

Returns:
- For methods 1 & 2: Printed list of unique combinations of PatientID, study, series, etc.
- For method 3: File paths and unique combinations for data handling.
"""

import os
import pydicom
import argparse
import tkinter as tk
from tkinter import filedialog
import numpy as np



def get_folder_path_from_cmd():
    """Retrieve folder path from command line arguments if provided."""
    parser = argparse.ArgumentParser(description="Process a directory containing DICOM files.")
    parser.add_argument('-d', '--directory', help='Path to the directory containing DICOM files', default=None)
    return parser.parse_args().directory


def get_folder_path_from_dialog():
    """Open a GUI dialog for the user to select a directory if none is provided."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    return filedialog.askdirectory(title="Select a Folder")


def get_all_files(path):
    """Retrieve all DICOM, IMA, or files without extensions in a directory.
    
    Args:
    - path: Directory path to search for DICOM files.
    
    Returns:
    - List of paths to relevant files.
    """
    all_files = []
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext in ('.dcm', '.ima') or not ext:
                all_files.append(os.path.normpath(os.path.join(dirpath, filename)))
    return all_files


def extract_file_info(all_files, progress_callback=None, total_steps=None):
    """Extract metadata from DICOM files, sort them by PatientID, StudyID, Modality, SeriesNumber, and SeriesTime,
    and add ReferenceTime to each series.
    
    Args:
    - all_files: List of paths to DICOM files.
    - progress_callback: Optional callback for progress reporting.
    - total_steps: Optional total number of steps for progress calculation.
    
    Returns:
    - detailed_files_info: List of dictionaries with detailed file info, sorted and with ReferenceTime added.
    - unique_files_info: List of dictionaries with unique file info combinations.
    """
    detailed_files_info = []
    unique_files_info = []
    seen_combinations = set()  # To track already seen unique tag combinations
    reference_times = {}  # To store the earliest SeriesTime for each series

    # Iterate over each DICOM file
    for index, file_path in enumerate(all_files):
        dicom_file = pydicom.dcmread(file_path, stop_before_pixels=True, force=True)
        
        # Extract necessary attributes
        patient_id = getattr(dicom_file, "PatientID", "N/A")
        study_id = getattr(dicom_file, "StudyID", "N/A")
        series_number = getattr(dicom_file, "SeriesNumber", "N/A")
        modality = getattr(dicom_file, "Modality", "N/A")
        series_time = getattr(dicom_file, "SeriesTime", "N/A")
        instance_number = getattr(dicom_file, "InstanceNumber", "N/A")
        sop_instance_uid = getattr(dicom_file, "SOPInstanceUID", "N/A")
        acquisition_date = getattr(dicom_file, "AcquisitionDate", "N/A")
        acquisition_time = getattr(dicom_file, "AcquisitionTime", "N/A")
        acquisition_number = getattr(dicom_file, "AcquisitionNumber", "N/A")
        KVP = getattr(dicom_file, "KVP", "N/A")
        image_patient_position = getattr(dicom_file, "ImagePositionPatient", "N/A")
        
        # RealWorldValueMappingSequence can be a list
        RWV = getattr(dicom_file, "RealWorldValueMappingSequence", [])
        study_LUTExplanation = "N/A"
        study_LUTLabel = "N/A"
        for item in RWV:
            if hasattr(item, "LUTExplanation"):
                study_LUTExplanation = item.LUTExplanation
            if hasattr(item, "LUTLabel"):
                study_LUTLabel = item.LUTLabel

        # Create a dictionary for each file's information
        file_info = {
            "FilePath": file_path,
            "PatientID": patient_id,
            "StudyID": study_id,
            "SeriesNumber": series_number,
            "Modality": modality,
            "LUTExplanation": study_LUTExplanation,
            "LUTLabel": study_LUTLabel,
            "AcquisitionDate": acquisition_date,
            "SeriesTime": series_time,
            "InstanceNumber": instance_number,
            "SOPInstanceUID": sop_instance_uid,
            "AcquisitionTime": acquisition_time,
            "AcquisitionNumber": acquisition_number,
            "KVP": KVP,
            "ImagePatientPosition": image_patient_position
        }
        detailed_files_info.append(file_info)
        # Create a unique key for each combination
        unique_combination_key = (patient_id, study_id, series_number, modality)
        if unique_combination_key not in seen_combinations:
            seen_combinations.add(unique_combination_key)
            unique_files_info.append(file_info)  # Add the current file's info to the unique list

        # Progress callback update
        if progress_callback and total_steps:
            progress = (index + 1) / total_steps * 100
            progress_callback(int(progress))

    # Sort detailed_files_info by PatientID, StudyID, Modality, SeriesNumber, and SeriesTime
    detailed_files_info.sort(key=lambda x: (
        x['PatientID'], 
        x['StudyID'], 
        x['Modality'], 
        x['SeriesNumber'], 
        x['AcquisitionTime']
    ))

    # Assign ReferenceTime for each file_info
    for file_info in detailed_files_info:
        # Create a unique key for each combination
        unique_combination_key = (
            file_info['PatientID'], 
            file_info['StudyID'], 
            file_info['Modality'], 
            file_info['SeriesNumber']
        )

        # Check if we have a ReferenceTime for this combination already
        if unique_combination_key not in reference_times:
            reference_times[unique_combination_key] = file_info['AcquisitionTime']
        
        # Set the ReferenceTime for the current file_info
        file_info['ReferenceTime'] = reference_times[unique_combination_key]


    # INSERT MISSING INSTANCE NUMBER FIX HERE
    from collections import defaultdict

    series_groups = defaultdict(list)
    for file_info in detailed_files_info:
        series_key = (
            file_info['PatientID'],
            file_info['StudyID'],
            file_info['Modality'],
            file_info['SeriesNumber']
        )
        series_groups[series_key].append(file_info)

    for series_files in series_groups.values():
        need_fix = [f for f in series_files if f['InstanceNumber'] in [None, "N/A", "", "None"]]
        if len(series_files) > 1 and need_fix:
            z_positions = []
            for f in series_files:
                ipp = f.get('ImagePatientPosition', [0,0,0])
                try:
                    if isinstance(ipp, str):  # Convert string repr to list
                        ipp = eval(ipp)
                    ipp = [float(v) for v in ipp]
                except Exception:
                    ipp = [0,0,0]
                f['_z'] = float(ipp[2])
                z_positions.append(f['_z'])
                # Always get thickness for later
                try:
                    dcm = pydicom.dcmread(f['FilePath'], stop_before_pixels=True, force=True)
                    thick = getattr(dcm, 'SliceThickness', None)
                    if thick is not None: thick = float(thick)
                except Exception:
                    thick = None
                f['_slice_thickness'] = thick

            # Calculate median slice thickness from DICOM field if possible
            slice_thicknesses = [f['_slice_thickness'] for f in series_files if f['_slice_thickness'] and f['_slice_thickness'] > 0]
            slice_thickness = np.median(slice_thicknesses) if slice_thicknesses else None
            # Estimate from z-positions if DICOM field is missing or zero
            z_unique_sorted = sorted(list(set(z_positions)))
            est_thick = np.median(np.diff(z_unique_sorted)) if len(z_unique_sorted) > 1 else None
            if not slice_thickness or slice_thickness == 0:
                slice_thickness = est_thick

            # # Debug print
            # print("Series: {} | z_positions: {} | slice_thickness: {} | est_thick: {}".format(
            #     series_files[0]['SeriesNumber'], z_positions, slice_thickness, est_thick))

            # Fallback to sequential if impossible to determine
            if not slice_thickness or slice_thickness == 0 or np.allclose(z_positions, z_positions[0]):
                instance_counter = 1
                for f in sorted(series_files, key=lambda f: f['_z']):
                    if f['InstanceNumber'] in [None, "N/A", "", "None"]:
                        f['InstanceNumber'] = instance_counter
                        instance_counter += 1
            else:
                min_z = min(z_positions)
                # Always sort by z for numbering
                for f in series_files:
                    if f['InstanceNumber'] in [None, "N/A", "", "None"]:
                        idx = int(round((f['_z'] - min_z) / slice_thickness)) + 1
                        f['InstanceNumber'] = idx
            # Clean up
            for f in series_files:
                if '_z' in f: del f['_z']
                if '_slice_thickness' in f: del f['_slice_thickness']
        else:
            # Fallback: sequential assign for missing
            instance_counter = 1
            for f in series_files:
                if f['InstanceNumber'] in [None, "N/A", "", "None"]:
                    f['InstanceNumber'] = instance_counter
                    instance_counter += 1



    return detailed_files_info, unique_files_info


def get_data_description(folder_path=None, progress_callback=None, update_label=None):
    """Main function to handle directory selection, DICOM extraction, and metadata analysis.
    
    Args:
    - folder_path (optional): Initial directory to analyze. 
    
    Returns:
    - Paths to DICOM files and dictionary of unique metadata combinations.
    """
    if folder_path is None:
        folder_path = get_folder_path_from_cmd()
    
    if folder_path is None:
        folder_path = get_folder_path_from_dialog()

    if not os.path.exists(folder_path) or folder_path is None:
        print(f"Error: The folder '{folder_path}' does not exist or the operation was cancelled!")
        return None, None

    all_files = get_all_files(folder_path)
    total_steps = len(all_files)
    if update_label:
        update_label.setText(f"Checking and sorting the header of {total_steps} files")
    detailed_files_info, unique_files_info  = extract_file_info(all_files,progress_callback,total_steps)

    return  detailed_files_info, unique_files_info





if __name__ == "__main__":
    detailed_files_info, unique_files_info = get_data_description()
    # Print a sample from detailed_files_info
    # for info in detailed_files_info[:5]:
    #    for key, value in info.items():
    #         print(f"{key}: {value}")
    #   print("------")
        
    # # Print all unique combinations
    # print("\nUnique combinations of metadata:")
    # for combination in unique_files_info:
    #     print(combination)
