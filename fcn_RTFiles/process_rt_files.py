import numpy as np
import copy

def process_rt_struct(rtstruct,structured_data):
    # Extract identifiers for navigation.
    patient_id   = rtstruct['patient_id']
    study_id     = rtstruct['study_id']
    modality     = rtstruct['modality']
    series_index = rtstruct['series_index']
    
    try:
        series_data = structured_data[patient_id][study_id][modality][series_index]
    except KeyError:
        print("Error: The specified series could not be found. Please check rtstruct identifiers.")
        return
    
    metadata = series_data.get('metadata')
    if metadata is None:
        print("Error: No metadata found in the series data.")
        return
    
    # Retrieve the two sequences.
    rt_roi_obs_seq  = metadata.get('RTROIObservationsSequence')
    roi_contour_seq = metadata.get('ROIContourSequence')
    
    if rt_roi_obs_seq is None:
        print("Error: RTROIObservationsSequence not found in metadata.")
        return
    if roi_contour_seq is None:
        print("Error: ROIContourSequence not found in metadata.")
        return

    # Ensure a 'structures' dictionary exists.
    structures = series_data.setdefault('structures', {})
    # Clear any existing structures (optional)
    # structures.clear()
    
    # This list will hold ROIObservationLabel for each included observation.
    structures_names = []
    #
    for idx, obs_item in enumerate(rt_roi_obs_seq):
        key = f"Item_{idx+1}"
        if hasattr(obs_item, 'RTROIInterpretedType') and obs_item.RTROIInterpretedType == 'BRACHY_CHANNEL':
            continue

        copied_obs = copy.deepcopy(obs_item)
        structures[key] = copied_obs

        if hasattr(obs_item, 'ROIObservationLabel'):
            structures_names.append(obs_item.ROIObservationLabel)
        else:
            structures_names.append(key)

        try:
            ref_roi_number = obs_item.ReferencedROINumber
        except AttributeError:
            print(f"{key} does not have a ReferencedROINumber; skipping ROIContour matching for this item.")
            continue

        match_found = False
        if hasattr(roi_contour_seq, 'keys'):
            for ckey, contour_item in roi_contour_seq.items():
                try:
                    contour_ref_roi_number = contour_item.ReferencedROINumber
                except AttributeError:
                    continue
                if contour_ref_roi_number == ref_roi_number:
                    if hasattr(contour_item, 'ContourSequence'):
                        copied_contour_seq = copy.deepcopy(contour_item.ContourSequence)
                        structures[key].ContourSequence = copied_contour_seq
                    else:
                        print(f"Matching ROIContourSequence for ReferencedROINumber {ref_roi_number} has no ContourSequence.")
                    match_found = True
                    break
        else:
            for contour_item in roi_contour_seq:
                try:
                    contour_ref_roi_number = contour_item.ReferencedROINumber
                except AttributeError:
                    continue
                if contour_ref_roi_number == ref_roi_number:
                    if hasattr(contour_item, 'ContourSequence'):
                        copied_contour_seq = copy.deepcopy(contour_item.ContourSequence)
                        structures[key].ContourSequence = copied_contour_seq
                    else:
                        print(f"Matching ROIContourSequence for ReferencedROINumber {ref_roi_number} has no ContourSequence.")
                    match_found = True
                    break
        if not match_found:
            print(f"No matching ROIContourSequence found for {key} with ReferencedROINumber {ref_roi_number}.")

    # Update the series_data with the new structures field.
    structured_data[patient_id][study_id][modality][series_index]['structures']       = structures
    structured_data[patient_id][study_id][modality][series_index]['structures_names'] = structures_names



def process_rt_plans(plan,ref_str,structured_data):
    # 
    if structured_data[plan['patient_id']][plan['study_id']][plan['modality']][plan['series_index']]['metadata']['BrachyTreatmentType'] != 'N/A':
        read_brachy_plan(plan,ref_str,structured_data)
        

def read_brachy_plan(plan,ref_str,structured_data):
    app_sequence = structured_data[plan['patient_id']][plan['study_id']][plan['modality']][plan['series_index']]['metadata']['ApplicationSetupSequence']
    # Check if the sequence is not empty
    if len(app_sequence) > 0:
        # Access the first item in the sequence using index 0
        first_item = app_sequence[0]
        # Now, you can access 'channels' or other attributes within the first_item
        channels = first_item.get('ChannelSequence', 'N/A')
    else:
        channels = 'N/A'
    #
    # struct set reference to get channels geometry (Varian)
    stru_info       = structured_data[ref_str['patient_id']][ref_str['study_id']][ref_str['modality']][ref_str['series_index']]['metadata']['ROIContourSequence']
    #
    channel_info    = []
    #
    for chan_idx, channel_item in enumerate(channels):        
        # Access the BrachyControlPointSequence within the channel_item
        control_point_sequence = channel_item.get('BrachyControlPointSequence', [])
        #
        if len(control_point_sequence) > 0:
            # Prepare a list to hold control point data
            control_point_data = []
            dw_index           = 1
            #
            for cp_idx, cp_item in enumerate(control_point_sequence):                
                if cp_idx % 2 == 0:
                    time_weight                     = cp_item.get('CumulativeTimeWeight', np.nan)
                else:
                    # Extract the required fields from cp_item
                    control_point_relative_position = cp_item.get('ControlPointRelativePosition', np.nan)
                    control_point_3d_position       = cp_item.get('ControlPoint3DPosition', [np.nan, np.nan, np.nan])
                    cumulative_time_weight          = cp_item.get('CumulativeTimeWeight', np.nan)
                    control_point_orientation       = cp_item.get('ControlPointOrientation', [np.nan, np.nan, np.nan])
                    # Collect the data into a tuple matching the dtype
                    cp_data = (
                        dw_index,
                        control_point_relative_position,
                        cumulative_time_weight-time_weight,
                        control_point_3d_position[0],
                        control_point_3d_position[1],
                        control_point_3d_position[2],
                        control_point_orientation[0],
                        control_point_orientation[1],
                        control_point_orientation[2],
                    )
                    dw_index += 1
                    control_point_data.append(cp_data)
            
            # Convert the list of tuples to a NumPy structured array
            control_point_array = np.array(control_point_data, dtype=np.float32)
        else:
            print("    No BrachyControlPointSequence found in this channel.")
            control_point_array = np.empty((0, 9), dtype=np.float32)
        
        ref_ROI = channel_item.get('ReferencedROINumber', '')
        # search struct file (Varian to find channels)
        for idx, item in enumerate(stru_info):
            ROI_N = item.get('ReferencedROINumber')
            if ref_ROI == ROI_N:
                ContourSequence = item.get('ContourSequence', [])
                CS              = ContourSequence[0]
                Points          = CS.get('ContourData',[])
                if Points:
                    # Convert Points to a NumPy array of type float32
                    points_array = np.array(Points, dtype=np.float32)
                    # Check if the length of Points is a multiple of 3
                    if len(points_array) % 3 == 0:
                        points_matrix = points_array.reshape((-1, 3))    
        
        info = {
            'ChannelNumber':             channel_item.get('ChannelNumber', 'N/A'),
            'ReferencedROINumber':       channel_item.get('ReferencedROINumber', 'N/A'),
            'NumberofControlPoints':     channel_item.get('NumberofControlPoints', 'N/A'),
            'ChannelLength':             channel_item.get('ChannelLength', 'N/A'),
            'ChannelTotalTime':          channel_item.get('ChannelTotalTime', 'N/A'),
            'SourceApplicatorNumber':    channel_item.get('SourceApplicatorNumber', 'N/A'),
            'SourceApplicatorID':        channel_item.get('NumberofControlPoints', 'N/A'),
            'SourceApplicatorType':      channel_item.get('SourceApplicatorType', 'N/A'),
            'SourceApplicatorLength':    channel_item.get('SourceApplicatorLength', 'N/A'),
            'SourceApplicatorStepSize':  channel_item.get('SourceApplicatorStepSize', 'N/A'),
            'FinalCumulativeTimeWeight': channel_item.get('NumberofControlPoints', 'N/A'),
            'DwellInfo':                 control_point_array,
            'ChPos':                     points_matrix
        }
        #
        channel_info.append(info)
        #
        structured_data[plan['patient_id']][plan['study_id']][plan['modality']][plan['series_index']]['metadata']['Plan_Brachy_Channels'] = channel_info



        
