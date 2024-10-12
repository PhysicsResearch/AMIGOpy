# Importing necessary libraries
import numpy as np
import pydicom
import math
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from fcn_display.Data_tree_general import _get_or_create_parent_item
from fcn_RTFiles.process_rt_files  import process_rt_plans

# Import the function that retrieves a detailed description of DICOM data.
from fcn_load.sort_dcm import get_data_description

def load_images(detailed_files_info, progress_callback=None, total_steps=None):
    """
    Load DICOM images and organize them hierarchically based on their DICOM headers.
    
    The images are structured by PatientID, StudyID, Modality, and SeriesNumber.

    Args:
        detailed_files_info (list): Contains metadata about DICOM files including 
                                    file_path, patient_id, study_id, etc.
    Returns:
        structured_data (dict): Hierarchical representation of DICOM data.
        non_ct_files (list): List of DICOM metadata for files that aren't of CT modality.
    """
    structured_data = {}
    non_im_files = []
        
    for index, file_info in enumerate(detailed_files_info):
        file_path, patient_id, study_id, series_number, modality, LUTExplanation, LUTLabel = (
            file_info['FilePath'], file_info['PatientID'], file_info['StudyID'], 
            file_info['SeriesNumber'], file_info['Modality'], 
            file_info['LUTExplanation'], file_info['LUTLabel']
        )
        
        
        if (modality != 'CT' and modality != 'MR' and modality != 'RTDOSE' and modality != 'RTPLAN'
            and modality != 'RTSTRUCT'):
            #
            non_im_files.append(file_info)
            continue

        #
        dicom_file    = pydicom.dcmread(file_path)
        patient_data  = structured_data.setdefault(patient_id, {})
        study_data    = patient_data.setdefault(study_id, {})
        modality_data = study_data.setdefault(modality, [])
        
        if (modality == 'CT' or modality == 'MR' or modality== 'RTDOSE'):
            
            image = dicom_file.pixel_array
            #
            #
            instance_number           = int(getattr(dicom_file, "InstanceNumber", 0))
            image_position_patient    = getattr(dicom_file, "ImagePositionPatient", [0,0,0])
              
            # slice thickness it not always available specially for RTDose so this needs to be considered 
            sli_thick = getattr(dicom_file, "SliceThickness", None)
            if sli_thick is None or sli_thick == 0 or sli_thick == '':
               # calculate the slice thickness usin additional info if available
               vect = getattr(dicom_file, "GridFrameOffsetVector", None)
               if vect is None or vect == 0 or vect == '':
                   sli_thick = np.float32(1)
               else:
                   sli_thick = vect[1]-vect[0]
        
        # Check if the current series_number already exists in the modality_data list
        existing_series_data = next((s for s in modality_data if s.get('SeriesNumber') == series_number), None)
        if not existing_series_data:
            if (modality == 'CT' or modality == 'MR' or modality== 'RTDOSE'):
                Header = Header = pydicom.dcmread(file_path,stop_before_pixels=True)
                existing_series_data = {
                    'SeriesNumber': series_number,
                    'metadata': {
                        'PixelSpacing': getattr(dicom_file, "PixelSpacing", 1),
                        'SliceThickness': sli_thick,
                        'LUTExplanation': LUTExplanation,
                        'LUTLabel': LUTLabel,
                        'ImageOrientationPatient': getattr(dicom_file, "ImageOrientationPatient", "N/A"),
                        'ImagePositionPatient': getattr(dicom_file, "ImagePositionPatient", [0,0,0]),
                        'RescaleSlope': getattr(dicom_file, "RescaleSlope", "N/A"),
                        'RescaleIntercept': getattr(dicom_file, "RescaleIntercept", "N/A"),
                        'WindowWidth': getattr(dicom_file, "WindowWidth", "N/A"),
                        'WindowCenter': getattr(dicom_file, "WindowCenter", "N/A"),
                        'SeriesDescription':getattr(dicom_file, "SeriesDescription", ''),
                        'StudyDescription': getattr(dicom_file, "StudyDescription", ''),
                        'ImageComments': getattr(dicom_file, "ImageComments", ''),
                        'DoseGridScaling': getattr(dicom_file, "DoseGridScaling", "N/A"),
                        'AcquisitionNumber': getattr(dicom_file, "AcquisitionNumber", "N/A"),
                        'Modality': modality,
                        'DCM_Info': Header
                    },
                    'images': {},
                    'ImagePositionPatients': [],
                    'SliceImageComments':{},
                }
            elif modality == 'RTPLAN':
                existing_series_data = {
                    'SeriesNumber': series_number,
                    'metadata': {
                        'Modality': modality,
                        'Manufacuter': getattr(dicom_file, "Manufacturer", "N/A"),
                        'BrachyTreatmentType': getattr(dicom_file, "BrachyTreatmentType", "N/A"),
                        'LUTLabel': "N/A",                                                      # just to create the filed as this is checked later
                        'AcquisitionNumber': getattr(dicom_file, "AcquisitionNumber", "N/A"),   # just to create the filed as this is checked later
                        'RTPlanLabel': getattr(dicom_file, "RTPlanLabel", ''),
                        'StudyDescription': getattr(dicom_file, "StudyDescription", ''),
                        'ReferencedStructureSetSequence': getattr(dicom_file, "ReferencedStructureSetSequence", ''),
                        'ApplicationSetupSequence': getattr(dicom_file, "ApplicationSetupSequence", ''),
                        'SourceSequence': getattr(dicom_file, "SourceSequence", ''),
                        'DCM_Info': dicom_file
                    },
                    'images': {},
                    'ImagePositionPatients': [],
                    'SliceImageComments':{},
                }
            elif modality == 'RTSTRUCT':
                existing_series_data = {
                    'SeriesNumber': series_number,
                    'metadata': {
                        'Modality': modality,
                        'LUTLabel': "N/A",                                                      # just to create the filed as this is checked later
                        'AcquisitionNumber': getattr(dicom_file, "AcquisitionNumber", "N/A"),   # just to create the filed as this is checked later
                        'StudyDescription': getattr(dicom_file, "StudyDescription", ''),
                        'StructureSetLabel': getattr(dicom_file, "StructureSetLabel", ''),
                        'SOPInstanceUID': getattr(dicom_file, "SOPInstanceUID", ''),
                        'ReferencedFrameOfReferenceSequence': getattr(dicom_file, "ReferencedFrameOfReferenceSequence", ''),
                        'ROIContourSequence': getattr(dicom_file,"ROIContourSequence",''),
                        'DCM_Info': dicom_file
                    },
                    'images': {},
                    'ImagePositionPatients': [],
                    'SliceImageComments':{},
                }
                
            modality_data.append(existing_series_data)
        
        if modality == 'CT' or modality == 'MR':
            existing_series_data['images'][instance_number] = {
                'ImageData': image,
                'ImagePositionPatient': image_position_patient,
            }
            existing_series_data['ImagePositionPatients'].append(image_position_patient)
            existing_series_data['SliceImageComments'][instance_number] = getattr(dicom_file, "ImageComments", '')
        elif modality == 'RTDOSE':
           # RT dose are loaded using absolut coordinates 
           # Initial position and voxel size are difned when displaying so it alignes with referenced images
           # Get the dimensions
           RTDose_matrix = image.reshape((dicom_file.NumberOfFrames, dicom_file.Rows, dicom_file.Columns)) 

        # Progress callback update
        if progress_callback and total_steps:        
            progress = math.ceil((index + 1) / total_steps * 100)
            progress_callback(int(progress))
            #
    # Adjusting how data is processed after being loaded, to handle series data as a list
    #
    
    # Check RTPlans and make a list so it can be processed later
    # Initialize an empty list to store RTPLAN data
    rtplan_files      = []
    # Check RTSTRUCT and make a list so it can be processed later
    rtstruct_files    = []
    #
    
    for patient_id, studies in structured_data.items():
        for study_id, modalities in studies.items():
            for modality, series_list in modalities.items():
                for index, series_data in enumerate(series_list):
                    if modality == 'CT':
                        sorted_comments = sorted(series_data['SliceImageComments'].items(), key=lambda x: x[0])
                        # Extract only the values from the sorted list of tuples
                        series_data['SliceImageComments'] = [comment for _, comment in sorted_comments]
                        sorted_image_data = sorted(series_data['images'].items(), key=lambda x: x[0])
                        series_data['3DMatrix'] = np.stack([item[1]['ImageData'] for item in sorted_image_data], axis=0)
                        series_data['3DMatrix'] = np.flip(series_data['3DMatrix'], axis=1)
                        if len(sorted_image_data) >= 2 and (sorted_image_data[0][1]['ImagePositionPatient'][2] - sorted_image_data[1][1]['ImagePositionPatient'][2] >0):
                            print('Image needs to be flipped to match coordinate system')
                            series_data['3DMatrix'] = np.flip(series_data['3DMatrix'], axis=0)
                            series_data['metadata']['ImagePositionPatient']  =sorted_image_data[-1][1]['ImagePositionPatient']
                        else:
                            series_data['metadata']['ImagePositionPatient']=sorted_image_data[0][1]['ImagePositionPatient']
                        series_data['3DMatrix'] = series_data['3DMatrix'].astype(np.float32)
                        #
                    elif modality == 'MR':
                        sorted_comments = sorted(series_data['SliceImageComments'].items(), key=lambda x: x[0])
                        # Extract only the values from the sorted list of tuples
                        series_data['SliceImageComments'] = [comment for _, comment in sorted_comments]
                        sorted_image_data = sorted(series_data['images'].items(), key=lambda x: x[0])
                        series_data['3DMatrix'] = np.stack([item[1]['ImageData'] for item in sorted_image_data], axis=0)
                        series_data['3DMatrix'] = np.flip(series_data['3DMatrix'], axis=1)
                        if len(sorted_image_data) >= 2 and (sorted_image_data[0][1]['ImagePositionPatient'][2] - sorted_image_data[1][1]['ImagePositionPatient'][2] >0):
                            print('Image needs to be flipped to match coordinate system')
                            series_data['3DMatrix'] = np.flip(series_data['3DMatrix'], axis=0)
                            series_data['metadata']['ImagePositionPatient']  =sorted_image_data[-1][1]['ImagePositionPatient']
                        else:
                            series_data['metadata']['ImagePositionPatient']=sorted_image_data[0][1]['ImagePositionPatient']
                        series_data['3DMatrix'] = series_data['3DMatrix'].astype(np.float32)
                        #
                    elif modality == 'RTDOSE':
                        series_data['3DMatrix'] = RTDose_matrix
                        series_data['3DMatrix'] = np.flip(series_data['3DMatrix'], axis=1)
                        series_data['3DMatrix'] = series_data['3DMatrix'].astype(np.float32)
                        series_data['3DMatrix'] = series_data['3DMatrix']*series_data['metadata']['DoseGridScaling']
                        ref_value = np.max(series_data['3DMatrix']);
                        series_data['metadata']['WindowWidth'] = ref_value*0.02
                        series_data['metadata']['WindowCenter']= ref_value*0.80
                    #
                    elif modality == 'RTPLAN':
                        # Store patient_id, study_id, modality, and other relevant data
                        rtplan_info = {
                            'patient_id': patient_id,
                            'study_id': study_id,
                            'modality': modality,
                            'series_index': index,
                            'PlanLabel': series_data['metadata']['RTPlanLabel']
                        }
                        rtplan_files.append(rtplan_info)
                    elif modality == 'RTSTRUCT':
                        # Store patient_id, study_id, modality, and other relevant data
                        rtstruct_info = {
                            'patient_id': patient_id,
                            'study_id': study_id,
                            'modality': modality,
                            'series_index': index,
                            'SOPInstanceUID':series_data['metadata']['SOPInstanceUID']
                        }
                        rtstruct_files.append(rtstruct_info)
                        #
                    # Rescale slope + Rescale interpect HU
                    if '3DMatrix' in series_data and series_data['3DMatrix'] is not None:
                        if modality != 'RTDOSE' and series_data['metadata']['RescaleSlope'] != 'N/A' and series_data['metadata']['RescaleIntercept'] != 'N/A':
                            series_data['3DMatrix'] = (series_data['3DMatrix'] * series_data['metadata']['RescaleSlope']) + series_data['metadata']['RescaleIntercept'] 
                    #
                    if 'images' in series_data:
                        del series_data['images']
                    #
                    if series_data['metadata']['LUTLabel']== "SPR":
                         series_data['3DMatrix'] = (series_data['3DMatrix']/1000)+1
                         series_data['metadata']['WindowWidth'] = 0.5
                         series_data['metadata']['WindowCenter']= 1.0
                    elif series_data['metadata']['LUTLabel']== "EFF_ATOMIC_NUM":
                             # series_data['3DMatrix'] = (series_data['3DMatrix']/10)
                         series_data['metadata']['WindowWidth'] = 4
                         series_data['metadata']['WindowCenter']= 8 
                    elif series_data['metadata']['LUTLabel']== "ELECTRON_DENSITY":
                         series_data['3DMatrix'] = (series_data['3DMatrix']/1000)+1
                         series_data['metadata']['WindowWidth'] = 0.5
                         series_data['metadata']['WindowCenter']= 1.0  
                    elif (modality != 'RTDOSE' and '3DMatrix' in series_data and series_data['3DMatrix'] is not None) :
                         series_data['3DMatrix'] = series_data['3DMatrix'].astype(np.int16)
    #
    # 
    for plan in rtplan_files:
        # Access the ReferencedStructureSetSequence from metadata
        sequence = structured_data[plan['patient_id']][plan['study_id']][plan['modality']][plan['series_index']]['metadata']['ReferencedStructureSetSequence']
        # Check if the sequence is a list and not empty
        if  len(sequence) > 0:
            # Access the first item in the sequence (index 0)
            str_item = sequence[0]
            # Now, access the ReferencedSOPInstanceUID within str_item
            ref_struct_UID = str_item.get("ReferencedSOPInstanceUID", "N/A")
        else:
            ref_struct_UID = "N/A"
        
        # 
        # Now, search in rtstruct_files for a matching SOPInstanceUID
        matching_rtstruct = None
        for rtstruct in rtstruct_files:
            if rtstruct['SOPInstanceUID'] == ref_struct_UID:
                matching_rtstruct = rtstruct
                break  # Stop the search once a match is found
        
        
        # call a function to process plan data ... which is different depeding on TPS and treatment type.    
        process_rt_plans(plan,matching_rtstruct,structured_data)    
            
    return structured_data, non_im_files 
 

def load_all_dcm(self,folder_path=None, progress_callback=None, update_label=None):
    """
    Master function that facilitates loading, extraction, and organization of DICOM data.

    This function calls the necessary sub-functions to process and organize the DICOM data 
    in a hierarchical manner.

    Args:
        folder_path (str, optional): Path to the directory with DICOM files.
        progress_callback (function, optional): Optional callback function for tracking progress.
        update_label (label, optional): UI label to display progress updates.

    Returns:
        dicom_data (dict): Hierarchical representation of DICOM data.
    """
    detailed_files_info, unique_files_info = get_data_description(folder_path, self.progressBar.setValue, update_label)
    if detailed_files_info is None:
        # user cacled or folder does not exist
        return
    total_steps = len(detailed_files_info)
    
    if update_label:
        update_label.setText(f"Loading {total_steps} files")
        
    self.dicom_data, non_im_files = load_images(detailed_files_info, self.progressBar.setValue, total_steps)
    populate_DICOM_tree(self)
    
    for index, file_info in enumerate(non_im_files):
        print(f"{file_info['FilePath']} {file_info['Modality']}")
    #return dicom_data

# 
def populate_DICOM_tree(self):
    #self.dicom_data=load_all_dcm(folder_path=None, progress_callback=self.update_progress,update_label=self.label);
    # Create the data model for the tree view
    # Create the data model for the tree view if it doesn't exist
    if not hasattr(self, 'model') or self.model is None:
        self.model = QStandardItemModel()
        self.DataTreeView.setModel(self.model)
        self.model.setHorizontalHeaderLabels(['Data'])

    # Check for existing 'DICOM' parent item
    dicom_parent_item = _get_or_create_parent_item(self,'DICOM')
    #
    # Clear the clist of series menus for DECT
    self.DECT_list_01.clear()
    self.DECT_list_02.clear()
    self.scatter_plot_im_01.clear()
    self.scatter_plot_im_02.clear()
    # Dictionary to store series_label and related information
    self.series_info_dict = {}
    
    # Index for comboBox items
    combo_index = 0
    # Clear all children of the 'DICOM' parent item
    dicom_parent_item.removeRows(0, dicom_parent_item.rowCount())
    #
    # Populate tree view with DICOM data
    for patient_id, patient_data in self.dicom_data.items():
        patient_item = QStandardItem(f"PatientID: {patient_id}")
        dicom_parent_item.appendRow(patient_item)
        for study_id, study_data in patient_data.items():
            study_item = QStandardItem(f"StudyID: {study_id}")
            patient_item.appendRow(study_item)
            for modality, modality_data in study_data.items():
                modality_item = QStandardItem(f"Modality: {modality}")
                study_item.appendRow(modality_item)
                for item_index, series_data in enumerate(modality_data):  # Iterating over the list
                    if   modality == 'RTPLAN':
                        Plan_label = series_data['metadata']['RTPlanLabel']
                        series_label = f"{Plan_label}_Series: {series_data['SeriesNumber']}"
                        #
                    elif modality == 'RTSTRUCT':
                        Struct_label = series_data['metadata']['StructureSetLabel']
                        series_label = f"{Struct_label}_Series: {series_data['SeriesNumber']}"
                    elif modality == 'RTDOSE':
                        Dose_label = series_data['metadata']['SeriesDescription']
                        series_label = f"{Dose_label}_Series: {series_data['SeriesNumber']}"
                    else:
                        LUT = series_data['metadata']
                        Acq_number = series_data['metadata']['AcquisitionNumber']
                        series_label = f"Acq_{Acq_number}_Series: {series_data['SeriesNumber']}"
                        if LUT['LUTLabel'] != 'N/A':
                            series_label += f" {LUT['LUTLabel']} {LUT['LUTExplanation']}"
                    series_item = QStandardItem(series_label)
                    modality_item.appendRow(series_item)
                    # Add to comboBox
                    self.DECT_list_01.addItem(series_label)
                    self.DECT_list_02.addItem(series_label)
                    self.scatter_plot_im_01.addItem(series_label)
                    self.scatter_plot_im_02.addItem(series_label)
                    # Store information in the dictionary
                    self.series_info_dict[combo_index] = (series_label, patient_id, study_id, modality, item_index)
                    combo_index += 1
    

if __name__ == "__main__":
    dicom_data = load_all_dcm()
    # data_plot = dicom_data['Siem_K']['4']['CT'][0]['3DMatrix']
    # # Plot an axial slice - for example the fifth slice along the third axis (0-indexed)
    # axial_slice = data_plot[150, :,:]
    # plt.imshow(axial_slice, cmap='gray')
    # plt.colorbar()
    # plt.title('Axial Slice')
    # plt.show()
    for patient_id, patient_data in dicom_data.items():
        print(f"PatientID: {patient_id}")
        for study_id, study_data in patient_data.items():
            print(f"\tStudyID: {study_id}")
            for modality, modality_list in study_data.items():
                print(f"\t\tModality: {modality}")
                for series_data in modality_list:  # Now iterating over the list
                    series_number = series_data['SeriesNumber']
                    print(f"\t\t\tSeriesNumber: {series_number}")
                    LUT = series_data['metadata']
                    print(f"\t\t\t\tLUTLabel: {LUT['LUTLabel']}")
                    print(f"\t\t\t\tLUTExplanation: {LUT['LUTExplanation']}")
                    
                    
