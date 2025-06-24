from fcn_load.sort_dcm import get_data_description
import shutil
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import math


def get_folder_path_from_dialog():
    """
    Open a GUI dialog for the user to select a directory.

    :return: The selected folder path as a string.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    # Bring the tkinter window to the front
    root.lift()
    root.attributes('-topmost', True)
    # Open a dialog for the user to select a directory.
    folder_path = filedialog.askdirectory(title="Select an output folder")
    root.attributes('-topmost', False)
    root.destroy()  # Clean up the root window after getting the path
    return folder_path


def compare_file_counts(detailed_files_info, root_destination):
    """
    Compare the number of files in the detailed files info list with the number of files in the root destination.

    :param detailed_files_info: List containing file information.
    :param root_destination: Path to the root destination folder.
    :return: Tuple containing a boolean and an integer. The boolean is True if the file counts match, and the integer is the difference in file counts.
    """
    original_file_count = len(detailed_files_info)
    copied_file_count = sum([len(files) for r, d, files in os.walk(root_destination)])
    
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

def remove_and_count_duplicates(detailed_files_info):
    """
    Count the number of duplicated files in the detailed files info list,
    and remove the second appearances from the detailed_files_info.

    :param detailed_files_info: List containing file information.
    :return: Tuple of the updated detailed_files_info and the number of duplicated files.
    """
    # Create a list of tuples containing the relevant information for each file
    file_info = [(info['StudyID'], info['Modality'], info['SeriesTime'],info['KVP'],
                  info['InstanceNumber'], info['SOPInstanceUID'], info['ImagePatientPosition'])
                 for info in detailed_files_info]

    file_counts = {}
    duplicate_indices = []
    for index, info in enumerate(file_info):
        if file_counts.get(info, 0) >= 1:
            duplicate_indices.append(index)
        file_counts[info] = file_counts.get(info, 0) + 1

    # Reverse the duplicate indices list to not mess up the indexing when deleting
    for index in sorted(duplicate_indices, reverse=True):
        del detailed_files_info[index]

    # Count duplicates
    duplicate_count = len(duplicate_indices)

    return detailed_files_info, duplicate_count


def show_warning(message):
    """
    Display a warning dialog with the specified message.

    :param message: Message to display in the warning dialog.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showwarning("Warning", message)
    root.destroy()  # Clean up the root window after showing the dialog

def organize_files_into_folders(detailed_files_info, progress_callback=None, update_label=None):
    """
    Organize files into a hierarchical folder structure based on their metadata.

    :param detailed_files_info: List of dictionaries containing file metadata.
    :param progress_callback: Function to update the progress (default is None).
    :param update_label: Label to update the status (default is None).
    :param total_steps: Total number of steps for progress (default is None).
    """
    
    # Counting duplicated files in the list before proceeding.
    detailed_files_info, duplicate_count = remove_and_count_duplicates(detailed_files_info)
    if duplicate_count > 0:
        warning_message = f"{duplicate_count} duplicate files found."
        if update_label:
            update_label.setText(warning_message)
        else:
            print(warning_message)
        
        # Showing warning dialog.
        show_warning(warning_message)
    #
    total_steps = len(detailed_files_info)
    # Requesting the user to select the root destination folder.
    if update_label:
        update_label.setText("Please select the root destination folder ... Minimize other windows in case you don't see it")
    else:
        print("Please select the root destination folder ... Minimize other windows in case you don't see it")

    # Getting the root destination folder from the user.
    root_destination = get_folder_path_from_dialog()

    # Check if the user closed the dialog without selecting a folder.
    if not root_destination:  
        if update_label:
            update_label.setText("No folder selected. Exiting the organizing process.")
        else:
            print("No folder selected. Exiting the organizing process.")
        return
    
    if progress_callback:
        progress_callback(0)  # Initialize the progress callback to 0.
            
    # Update the label or print the copying status.
    if update_label:
        update_label.setText(f"Copying {total_steps} files")
    else:
        print("Copying the files")
    
    # Generate the patient ID map
    patient_id_map = generate_patient_id_map(detailed_files_info)
         
    for index, info in enumerate(detailed_files_info):
        # Use the mapped patient ID
        mapped_patient_id = patient_id_map[info["PatientID"]]
        # Constructing the hierarchy paths
        patient_folder = os.path.join(root_destination, mapped_patient_id)
        study_folder = os.path.join(patient_folder, "Study_" + info["StudyID"])
        modality_folder = os.path.join(study_folder, info["Modality"])

        # Formatting acquisition date and time for the series folder name.
        if info["AcquisitionDate"] == 'N/A':
            year_short  = ''
            month_day   = ''
            hour_minute = ''   
        else:
            year_short = info["AcquisitionDate"][-2:]  # Last two digits of the year
            month_day = info["AcquisitionDate"][4:8]   # MMDD
            hour_minute = info["ReferenceTime"][:4]    # HHMM
        #
        # adjust the content to avoid printing N/A which creates subfolders
        #
        if info['LUTExplanation'] == 'N/A':
           LUTe = ''
        else:
           LUTe = info['LUTExplanation']
        #
        if info['LUTLabel'] == 'N/A':
           LUTl = ''
        else:
           LUTl = info['LUTLabel']
               
        if info['KVP']:
           series_folder_name = f"S_{year_short}{month_day}_{hour_minute}_{info['SeriesNumber']}_{info['KVP']}kV_{LUTe}_{LUTl}"
        else:
           series_folder_name = f"S_{year_short}{month_day}_{hour_minute}_{info['SeriesNumber']}_{LUTe}_{LUTl}"
           
        series_folder = os.path.join(modality_folder, series_folder_name)

        # Checking and creating directories if they don't exist
        if not os.path.exists(series_folder):
            os.makedirs(series_folder)

        # Copying the file to the appropriate location
        destination_file_path = os.path.join(series_folder, os.path.basename(info["FilePath"]))
        shutil.copy2(info["FilePath"], destination_file_path)

        # Updating the progress
        if progress_callback:
            progress = math.ceil((index + 1) / total_steps * 100)
            progress_callback(progress)

    # Finalizing the process.
    if update_label:
        update_label.setText("Done - going to check the number of files now")
    else:
        print("Done - going to check the number of files now")
        
    # After finalizing, compare the file counts.
    result, diff = compare_file_counts(detailed_files_info, root_destination)
    if result:
        print("All files successfully copied. Excl. duplicated files if any.")
        if update_label:
            update_label.setText("All files successfully copied. Excl. duplicated files if any.")
    else:
        print(f"File count mismatch by {diff} files. Please verify the files. Excl. duplicated files if any.")
        if update_label:
            update_label.setText(f"File count mismatch by {diff} files. Please verify the files. Excl. duplicated files if any.")

if __name__ == "__main__":
    # Getting detailed file information and organizing files.
    detailed_files_info, unique_files_info = get_data_description()
    organize_files_into_folders(detailed_files_info)
