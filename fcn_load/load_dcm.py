# Importing necessary libraries
import numpy as np
import pydicom
from pydicom.tag import Tag
import math
from fcn_load.populate_med_image_list import populate_medical_image_tree
from fcn_RTFiles.process_rt_files  import process_rt_plans, process_rt_struct

# Import the function that retrieves a detailed description of DICOM data.
from fcn_load.sort_dcm import get_data_description
from collections import Counter


def assemble_and_reorient_volume(series_data):
    """
    Assembles 2D slices into a 3D volume, geometrically sorted along the slice normal,
    and reoriented to standard AMIGOpy (Z, Y, X) LPS space.

    Ensures:
      - Axis 0 is Z (Axial slices, increasing from Inferior to Superior).
      - Axis 1 is Y (Coronal rows, with VTK row flip applied).
      - Axis 2 is X (Sagittal cols, increasing from Right to Left).
      - Coronal and Sagittal reformats are properly converted into (Z, Y, X) volume
        so they display on the correct viewer axes instead of having axes swapped.
      - Feet-First / Prone acquisitions are oriented in standard patient coordinate space
        without erroneous inverted slices or flipped Left/Right.
      - SliceThickness, PixelSpacing, and ImagePositionPatient are accurately recalculated.
    """
    # 1. Retrieve slices
    if 'slice_list' in series_data and len(series_data['slice_list']) > 0:
        slices = series_data['slice_list']
    else:
        slices = [
            {
                'ImageData': item['ImageData'],
                'ImagePositionPatient': item['ImagePositionPatient'],
                'InstanceNumber': k,
                'ImageComments': series_data.get('SliceImageComments', {}).get(k, ''),
                'ImageOrientationPatient': series_data.get('metadata', {}).get('ImageOrientationPatient', None)
            }
            for k, item in series_data.get('images', {}).items()
        ]

    if not slices:
        return

    # Check slice matrix shapes; filter out any slice with mismatched shape
    shapes = [s['ImageData'].shape for s in slices if hasattr(s.get('ImageData'), 'shape')]
    if shapes:
        common_shape = Counter(shapes).most_common(1)[0][0]
        slices = [s for s in slices if getattr(s.get('ImageData'), 'shape', None) == common_shape]

    # Handle single slice (2D)
    if len(slices) == 1:
        raw = slices[0]['ImageData']
        vol = raw[np.newaxis, :, :].astype(np.float32)
        series_data['3DMatrix'] = np.flip(vol, axis=1)
        series_data['SliceImageComments'] = [slices[0].get('ImageComments', '')]
        return

    # Check if localizer / scout with non-parallel views (e.g. AP and Lateral scouts)
    is_localizer = False
    first_dcm = series_data.get('metadata', {}).get('DCM_Info')
    img_type = getattr(first_dcm, 'ImageType', []) if first_dcm else []
    if any('LOCALIZER' in str(t).upper() for t in img_type):
        is_localizer = True
    elif len(slices) <= 4:
        normals = []
        for s in slices:
            s_iop = s.get('ImageOrientationPatient')
            if s_iop is not None and s_iop != 'N/A' and len(s_iop) == 6:
                sn = np.cross(s_iop[:3], s_iop[3:])
                sn_norm = np.linalg.norm(sn)
                if sn_norm > 0:
                    normals.append(sn / sn_norm)
        if len(normals) >= 2 and abs(float(np.dot(normals[0], normals[1]))) < 0.5:
            is_localizer = True

    if is_localizer:
        slices = sorted(slices, key=lambda s: int(s.get('InstanceNumber', 0)))
        series_data['SliceImageComments'] = [s.get('ImageComments', '') for s in slices]
        raw_stack = np.stack([s['ImageData'] for s in slices], axis=0).astype(np.float32)
        series_data['3DMatrix'] = np.flip(raw_stack, axis=1)
        series_data['metadata']['ImagePositionPatient'] = slices[0].get('ImagePositionPatient', [0.0, 0.0, 0.0])
        return

    # 2. Extract IOP
    iop = series_data['metadata'].get('ImageOrientationPatient')
    if iop is None or iop == 'N/A' or len(iop) != 6:
        iop = slices[0].get('ImageOrientationPatient')
    if iop is None or iop == 'N/A' or len(iop) != 6:
        iop = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
    else:
        iop = [float(x) for x in iop]

    r = np.array(iop[:3], dtype=np.float64)
    c = np.array(iop[3:], dtype=np.float64)
    r_norm = np.linalg.norm(r)
    c_norm = np.linalg.norm(c)
    if r_norm > 0: r = r / r_norm
    if c_norm > 0: c = c / c_norm
    n = np.cross(r, c)
    n_norm = np.linalg.norm(n)
    if n_norm > 0: n = n / n_norm

    # 3. Sort slices along slice normal n
    def get_proj(slc):
        ipp = slc.get('ImagePositionPatient', [0.0, 0.0, 0.0])
        return float(np.dot(np.array(ipp, dtype=np.float64), n))

    slices = sorted(slices, key=lambda s: (round(get_proj(s), 4), int(s.get('InstanceNumber', 0))))
    series_data['SliceImageComments'] = [s.get('ImageComments', '') for s in slices]

    # 4. Calculate step along normal n using median of adjacent slice differences
    projs = [get_proj(s) for s in slices]
    if len(projs) >= 2:
        diffs = [abs(b - a) for a, b in zip(projs, projs[1:]) if abs(b - a) > 1e-4]
        if diffs:
            step_s = float(np.median(diffs))
        else:
            step_s = abs(projs[1] - projs[0])
    else:
        step_s = float(series_data['metadata'].get('SliceThickness', 1.0) or 1.0)
    if step_s <= 0:
        step_s = float(series_data['metadata'].get('SliceThickness', 1.0) or 1.0)

    # Trim leading or trailing outlier slices (e.g. overview scouts with large gaps)
    if len(slices) > 3 and step_s > 0:
        while len(slices) > 3 and abs(get_proj(slices[1]) - get_proj(slices[0])) > 4 * step_s:
            slices = slices[1:]
        while len(slices) > 3 and abs(get_proj(slices[-1]) - get_proj(slices[-2])) > 4 * step_s:
            slices = slices[:-1]

    series_data['SliceImageComments'] = [s.get('ImageComments', '') for s in slices]

    # Pixel spacing in original 2D slices: ps[0] is row spacing, ps[1] is col spacing
    ps = series_data['metadata'].get('PixelSpacing', [1.0, 1.0])
    try:
        row_spacing = float(ps[0])
        col_spacing = float(ps[1])
    except (ValueError, TypeError, IndexError):
        row_spacing = 1.0
        col_spacing = 1.0

    # 5. Stack slices along axis 0
    raw_stack = np.stack([s['ImageData'] for s in slices], axis=0).astype(np.float32)

    # 6. Dominant anatomical axes in LPS space (0=X, 1=Y, 2=Z)
    col_axis = int(np.argmax(np.abs(r)))
    row_axis = int(np.argmax(np.abs(c)))
    slc_axis = int(np.argmax(np.abs(n)))

    col_sign = float(np.sign(r[col_axis]))
    row_sign = float(np.sign(c[row_axis]))
    slc_sign = float(np.sign(n[slc_axis]))

    axis_map = {slc_axis: 0, row_axis: 1, col_axis: 2}
    if len(set(axis_map.keys())) < 3:
        axis_map = {2: 0, 1: 1, 0: 2}
        col_sign, row_sign, slc_sign = 1.0, 1.0, 1.0

    # Permute axes so vol is (Z, Y, X)
    perm = (axis_map[2], axis_map[1], axis_map[0])
    vol = np.transpose(raw_stack, perm)

    # Map direction cosines to their respective patient axes (0=X, 1=Y, 2=Z)
    pat_signs = {col_axis: col_sign, row_axis: row_sign, slc_axis: slc_sign}

    # If any axis runs backwards in LPS, flip it
    flip_z = (pat_signs[2] < 0)
    flip_y = (pat_signs[1] < 0)
    flip_x = (pat_signs[0] < 0)

    if flip_z:
        vol = np.flip(vol, axis=0)
    if flip_y:
        vol = np.flip(vol, axis=1)
    if flip_x:
        vol = np.flip(vol, axis=2)

    # Standard VTK row flip (axis 1): VTK places row 0 at bottom and row max at top.
    # In AMIGOpy, flipping axis 1 ensures Anterior (-Y) is at the top of the viewport.
    vol = np.flip(vol, axis=1)

    # Target spacings for (Z, Y, X)
    src_spacings = [step_s, row_spacing, col_spacing]
    target_z_sp = float(src_spacings[axis_map[2]])
    target_y_sp = float(src_spacings[axis_map[1]])
    target_x_sp = float(src_spacings[axis_map[0]])

    # Calculate origin (coordinate of voxel (0, 0, 0))
    t_z = (vol.shape[0] - 1) if flip_z else 0
    t_y = (vol.shape[1] - 1) if flip_y else 0
    t_x = (vol.shape[2] - 1) if flip_x else 0

    target_indices = [t_z, t_y, t_x]
    k_slc = target_indices[perm.index(0)]
    k_row = target_indices[perm.index(1)]
    k_col = target_indices[perm.index(2)]

    ipp_ref = np.array(slices[k_slc].get('ImagePositionPatient', [0.0, 0.0, 0.0]), dtype=np.float64)
    origin_pt = ipp_ref + k_row * row_spacing * c + k_col * col_spacing * r

    series_data['3DMatrix'] = vol
    series_data['metadata']['SliceThickness'] = target_z_sp
    series_data['metadata']['PixelSpacing'] = [target_y_sp, target_x_sp]
    series_data['metadata']['ImagePositionPatient'] = [float(origin_pt[0]), float(origin_pt[1]), float(origin_pt[2])]
    series_data['metadata']['AcquisitionPlane'] = 'AXIAL' if slc_axis == 2 else ('CORONAL' if slc_axis == 1 else 'SAGITTAL')
    series_data['ImagePositionPatients'] = [
        [float(origin_pt[0]), float(origin_pt[1]), float(origin_pt[2] + kz * target_z_sp)]
        for kz in range(vol.shape[0])
    ]


def load_images(self,detailed_files_info, progress_callback=None, total_steps=None):
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
        
        if (modality != 'RTIMAGE' and modality != 'CT' and modality != 'MR' and modality != 'RTDOSE' and modality != 'RTPLAN'
            and modality != 'RTSTRUCT' and modality != 'REG'):
            non_im_files.append(file_info)
            continue

        dicom_file    = pydicom.dcmread(file_path, force=True)
        patient_data  = structured_data.setdefault(patient_id, {})
        study_data    = patient_data.setdefault(study_id, {})
        modality_data = study_data.setdefault(modality, [])
        
        if (modality == 'RTIMAGE' or modality == 'CT' or modality == 'MR' or modality == 'RTDOSE'):
            image = dicom_file.pixel_array
            instance_number = getattr(dicom_file, "InstanceNumber", None)
            if instance_number is None:
                instance_number = file_info.get('InstanceNumber', 1)
            try:
                instance_number = int(instance_number)
            except (ValueError, TypeError):
                instance_number = 1
            image_position_patient = getattr(dicom_file, "ImagePositionPatient", [0, 0, 0])
              
            # slice thickness it not always available specially for RTDose so this needs to be considered 
            sli_thick = getattr(dicom_file, "SliceThickness", None)
            if sli_thick is None or sli_thick == 0 or sli_thick == '':
                # calculate the slice thickness using additional info if available
                vect = getattr(dicom_file, "GridFrameOffsetVector", None)
                if vect is None or vect == 0 or vect == '' or len(vect) < 2:
                    sli_thick = np.float32(1)
                else:
                    sli_thick = np.float32(abs(vect[1] - vect[0]))
        
        # Check if the current series already exists in the modality_data list.
        # For CT, MR, and RTIMAGE we group files by SeriesInstanceUID (or SeriesNumber if UID missing).
        # For RTDOSE, RTPLAN, RTSTRUCT, and REG, each file is a self-contained object,
        # so we treat them as separate entries even if they share the same SeriesNumber.
        if modality in ['CT', 'MR', 'RTIMAGE']:
            series_uid = getattr(dicom_file, "SeriesInstanceUID", file_info.get('SeriesInstanceUID', 'N/A'))
            if series_uid and series_uid != 'N/A':
                existing_series_data = next((s for s in modality_data if s.get('metadata', {}).get('SeriesInstanceUID') == series_uid), None)
            else:
                existing_series_data = next((s for s in modality_data if s.get('SeriesNumber') == series_number), None)
        else:
            existing_series_data = None

        if not existing_series_data:
            if (modality == 'CT' or modality == 'MR' or modality == 'RTDOSE'):
                Header = pydicom.dcmread(file_path, stop_before_pixels=True, force=True)
                
                # Check RTDOSE specific references
                ref_plan_uid = "N/A"
                if hasattr(dicom_file, "ReferencedRTPlanSequence") and len(dicom_file.ReferencedRTPlanSequence) > 0:
                    ref_plan_uid = getattr(dicom_file.ReferencedRTPlanSequence[0], "ReferencedSOPInstanceUID", "N/A")
                ref_struct_uid = "N/A"
                if hasattr(dicom_file, "ReferencedStructureSetSequence") and len(dicom_file.ReferencedStructureSetSequence) > 0:
                    ref_struct_uid = getattr(dicom_file.ReferencedStructureSetSequence[0], "ReferencedSOPInstanceUID", "N/A")

                existing_series_data = {
                    'SeriesNumber': series_number,
                    'metadata': {
                        'PixelSpacing': getattr(dicom_file, "PixelSpacing", [1.0, 1.0]),
                        'SliceThickness': sli_thick,
                        'LUTExplanation': LUTExplanation,
                        'LUTLabel': LUTLabel,
                        'ImageOrientationPatient': getattr(dicom_file, "ImageOrientationPatient", "N/A"),
                        'ImagePositionPatient': getattr(dicom_file, "ImagePositionPatient", [0, 0, 0]),
                        'RescaleSlope': getattr(dicom_file, "RescaleSlope", "N/A"),
                        'RescaleIntercept': getattr(dicom_file, "RescaleIntercept", "N/A"),
                        'WindowWidth': getattr(dicom_file, "WindowWidth", "N/A"),
                        'WindowCenter': getattr(dicom_file, "WindowCenter", "N/A"),
                        'SeriesDescription': getattr(dicom_file, "SeriesDescription", ''),
                        'StudyDescription': getattr(dicom_file, "StudyDescription", ''),
                        'ImageComments': getattr(dicom_file, "ImageComments", ''),
                        'DoseGridScaling': getattr(dicom_file, "DoseGridScaling", "N/A"),
                        'DoseSummationType': getattr(dicom_file, "DoseSummationType", "N/A"),
                        'DoseType': getattr(dicom_file, "DoseType", "N/A"),
                        'ReferencedRTPlanSOPInstanceUID': ref_plan_uid,
                        'ReferencedStructureSetSOPInstanceUID': ref_struct_uid,
                        'AcquisitionNumber': getattr(dicom_file, "AcquisitionNumber", "N/A"),
                        'PatientPosition': getattr(dicom_file, "PatientPosition", "N/A"),
                        'SeriesInstanceUID': getattr(dicom_file, "SeriesInstanceUID", file_info.get('SeriesInstanceUID', 'N/A')),
                        'StudyInstanceUID': getattr(dicom_file, "StudyInstanceUID", file_info.get('StudyInstanceUID', 'N/A')),
                        'FrameOfReferenceUID': getattr(dicom_file, "FrameOfReferenceUID", file_info.get('FrameOfReferenceUID', 'N/A')),
                        'SOPInstanceUID': getattr(dicom_file, "SOPInstanceUID", file_info.get('SOPInstanceUID', 'N/A')),
                        'StudyDate': getattr(dicom_file, "StudyDate", file_info.get('AcquisitionDate', '')),
                        'SeriesDate': getattr(dicom_file, "SeriesDate", ''),
                        'DataType': 'DICOM',
                        'Modality': modality,
                        'DCM_Info': Header,

                        # Useful extras
                        'size': None,
                        'Nifiti_info': None,         # original NIfTI fields
                        'OriginalFilePath': file_path,    # for traceability - used with Nifti 
                    },
                    'images': {},
                    'ImagePositionPatients': [],
                    'SliceImageComments': {},
                    'AM_name': None,  # name defined (auto) in populate tree function 
                    'US_name': None,  # name that could be defined by the user in the interface (manual)
                }
            elif (modality == 'RTIMAGE'):
                Header = pydicom.dcmread(file_path, stop_before_pixels=True, force=True)
                existing_series_data = {
                    'SeriesNumber': series_number,
                    'metadata': {
                        'PixelSpacing': getattr(dicom_file, "ImagePlanePixelSpacing", [1.0, 1.0]),
                        'SliceThickness': sli_thick,
                        'LUTExplanation': LUTExplanation,
                        'LUTLabel': LUTLabel,
                        'ImageOrientationPatient': getattr(dicom_file, "ImageOrientationPatient", "N/A"),
                        'ImagePositionPatient': getattr(dicom_file, "ImagePositionPatient", [0, 0, 0]),
                        'RescaleSlope': getattr(dicom_file, "RescaleSlope", "N/A"),
                        'RescaleIntercept': getattr(dicom_file, "RescaleIntercept", "N/A"),
                        'WindowWidth': getattr(dicom_file, "WindowWidth", "N/A"),
                        'WindowCenter': getattr(dicom_file, "WindowCenter", "N/A"),
                        'SeriesDescription': getattr(dicom_file, "SeriesDescription", ''),
                        'StudyDescription': getattr(dicom_file, "StudyDescription", ''),
                        'ImageComments': getattr(dicom_file, "ImageComments", ''),
                        'DoseGridScaling': getattr(dicom_file, "DoseGridScaling", "N/A"),
                        'AcquisitionNumber': getattr(dicom_file, "AcquisitionNumber", "N/A"),
                        'PatientPosition': getattr(dicom_file, "PatientPosition", "N/A"),
                        'SeriesInstanceUID': getattr(dicom_file, "SeriesInstanceUID", file_info.get('SeriesInstanceUID', 'N/A')),
                        'StudyInstanceUID': getattr(dicom_file, "StudyInstanceUID", file_info.get('StudyInstanceUID', 'N/A')),
                        'FrameOfReferenceUID': getattr(dicom_file, "FrameOfReferenceUID", file_info.get('FrameOfReferenceUID', 'N/A')),
                        'SOPInstanceUID': getattr(dicom_file, "SOPInstanceUID", file_info.get('SOPInstanceUID', 'N/A')),
                        'StudyDate': getattr(dicom_file, "StudyDate", file_info.get('AcquisitionDate', '')),
                        'SeriesDate': getattr(dicom_file, "SeriesDate", ''),
                        'DataType': 'DICOM',
                        'Modality': modality,
                        'DCM_Info': Header,

                        # Useful extras
                        'size': None,
                        'Nifiti_info': None,         # original NIfTI fields
                        'OriginalFilePath': file_path,    # for traceability - used with Nifti 
                    },
                    'images': {},
                    'ImagePositionPatients': [],
                    'SliceImageComments': {},
                    'AM_name': None,  # name defined (auto) in populate tree function 
                    'US_name': None,  # name that could be defined by the user in the interface (manual)
                }
            elif modality == 'RTPLAN':
                # Define the private creator tag explicitly - Used in ONCENTRA so it is not always available
                private_creator_tag = Tag(0x300b, 0x0010) # NuCLETRON if created using ONCENTRA/ACE
                creator_value = dicom_file.get(Tag(0x300b, 0x0010), '').value if Tag(0x300b, 0x0010) in dicom_file else ''
                if creator_value == '':
                    creator_value = dicom_file.get(Tag(0x300f, 0x0010), '').value if Tag(0x300f, 0x0010) in dicom_file else ''
                
                private_channels = Tag(0x300f, 0x1000) # Cathether position if created using ONCENTRA/ACE
                existing_series_data = {
                    'SeriesNumber': series_number,
                    'metadata': {
                        'Modality': modality,
                        'Manufacturer': getattr(dicom_file, "Manufacturer", "N/A"),
                        'BrachyTreatmentType': getattr(dicom_file, "BrachyTreatmentType", "N/A"),
                        'LUTLabel': "N/A",
                        'AcquisitionNumber': getattr(dicom_file, "AcquisitionNumber", "N/A"),
                        'RTPlanLabel': getattr(dicom_file, "RTPlanLabel", ''),
                        'RTPlanName': getattr(dicom_file, "RTPlanName", ''),
                        'RTPlanDescription': getattr(dicom_file, "RTPlanDescription", ''),
                        'RTPlanDate': getattr(dicom_file, "RTPlanDate", getattr(dicom_file, "SeriesDate", '')),
                        'StudyDescription': getattr(dicom_file, "StudyDescription", ''),
                        'ReferencedStructureSetSequence': getattr(dicom_file, "ReferencedStructureSetSequence", []),
                        'ApplicationSetupSequence': getattr(dicom_file, "ApplicationSetupSequence", []),
                        'BeamSequence': getattr(dicom_file, "BeamSequence", []),
                        'FractionGroupSequence': getattr(dicom_file, "FractionGroupSequence", []),
                        'SourceSequence': getattr(dicom_file, "SourceSequence", []),
                        'PrivateCreator': creator_value,
                        'CatOnc': getattr(dicom_file, 'get', lambda *args: [])(Tag(0x300f, 0x1000), []),
                        'DoseReferenceSequence': getattr(dicom_file, "DoseReferenceSequence", "N/A"),
                        'TreatmentProtocols': getattr(dicom_file, "TreatmentProtocols", "N/A"),
                        'SeriesInstanceUID': getattr(dicom_file, "SeriesInstanceUID", file_info.get('SeriesInstanceUID', 'N/A')),
                        'StudyInstanceUID': getattr(dicom_file, "StudyInstanceUID", file_info.get('StudyInstanceUID', 'N/A')),
                        'FrameOfReferenceUID': getattr(dicom_file, "FrameOfReferenceUID", file_info.get('FrameOfReferenceUID', 'N/A')),
                        'SOPInstanceUID': getattr(dicom_file, "SOPInstanceUID", file_info.get('SOPInstanceUID', 'N/A')),
                        'StudyDate': getattr(dicom_file, "StudyDate", ''),
                        'SeriesDate': getattr(dicom_file, "SeriesDate", ''),
                        'DCM_Info': dicom_file,
                        'OriginalFilePath': file_path,
                    },
                    'images': {},
                    'ImagePositionPatients': [],
                    'SliceImageComments': {},
                }
            elif modality == 'RTSTRUCT':
                existing_series_data = {
                    'SeriesNumber': series_number,
                    'metadata': {
                        'Modality': modality,
                        'LUTLabel': "N/A",
                        'AcquisitionNumber': getattr(dicom_file, "AcquisitionNumber", "N/A"),
                        'StudyDescription': getattr(dicom_file, "StudyDescription", ''),
                        'StructureSetLabel': getattr(dicom_file, "StructureSetLabel", ''),
                        'StructureSetName': getattr(dicom_file, "StructureSetName", ''),
                        'StructureSetDate': getattr(dicom_file, "StructureSetDate", getattr(dicom_file, "SeriesDate", '')),
                        'SOPInstanceUID': getattr(dicom_file, "SOPInstanceUID", file_info.get('SOPInstanceUID', 'N/A')),
                        'SeriesInstanceUID': getattr(dicom_file, "SeriesInstanceUID", file_info.get('SeriesInstanceUID', 'N/A')),
                        'StudyInstanceUID': getattr(dicom_file, "StudyInstanceUID", file_info.get('StudyInstanceUID', 'N/A')),
                        'FrameOfReferenceUID': getattr(dicom_file, "FrameOfReferenceUID", file_info.get('FrameOfReferenceUID', 'N/A')),
                        'ReferencedFrameOfReferenceSequence': getattr(dicom_file, "ReferencedFrameOfReferenceSequence", []),
                        'ROIContourSequence': getattr(dicom_file, "ROIContourSequence", []),
                        'RTROIObservationsSequence': getattr(dicom_file, "RTROIObservationsSequence", []),
                        'StructureSetROISequence': getattr(dicom_file, "StructureSetROISequence", []),
                        'StudyDate': getattr(dicom_file, "StudyDate", ''),
                        'SeriesDate': getattr(dicom_file, "SeriesDate", ''),
                        'DCM_Info': dicom_file,
                        'OriginalFilePath': file_path,
                    },
                    'images': {},
                    'ImagePositionPatients': [],
                    'SliceImageComments': {},
                }
            elif modality == 'REG':
                # Parse Spatial Registration / Registration Sequence
                matrix_list = []
                reg_seq = getattr(dicom_file, "RegistrationSequence", None)
                if reg_seq is None:
                    reg_seq = getattr(dicom_file, "SpatialRegistrationSequence", [])
                
                for item in reg_seq:
                    item_for = getattr(item, "FrameOfReferenceUID", "N/A")
                    mat_reg_seq = getattr(item, "MatrixRegistrationSequence", [])
                    for mr in mat_reg_seq:
                        m_seq = getattr(mr, "MatrixSequence", [])
                        for ms in m_seq:
                            m_type = getattr(ms, "FrameOfReferenceTransformationMatrixType", "N/A")
                            mat = getattr(ms, "FrameOfReferenceTransformationMatrix", None)
                            if mat is None and (0x3006, 0x00c6) in ms:
                                mat = ms[0x3006, 0x00c6].value
                            if mat is not None:
                                matrix_list.append({
                                    "TargetFrameOfReferenceUID": item_for,
                                    "MatrixType": m_type,
                                    "Matrix": mat
                                })

                existing_series_data = {
                    'SeriesNumber': series_number,
                    'metadata': {
                        'Modality': modality,
                        'SeriesDescription': getattr(dicom_file, "SeriesDescription", 'Image Registration'),
                        'StudyDescription': getattr(dicom_file, "StudyDescription", ''),
                        'ContentLabel': getattr(dicom_file, "ContentLabel", 'REGISTRATION'),
                        'ContentDescription': getattr(dicom_file, "ContentDescription", ''),
                        'SOPInstanceUID': getattr(dicom_file, "SOPInstanceUID", file_info.get('SOPInstanceUID', 'N/A')),
                        'SeriesInstanceUID': getattr(dicom_file, "SeriesInstanceUID", file_info.get('SeriesInstanceUID', 'N/A')),
                        'StudyInstanceUID': getattr(dicom_file, "StudyInstanceUID", file_info.get('StudyInstanceUID', 'N/A')),
                        'FrameOfReferenceUID': getattr(dicom_file, "FrameOfReferenceUID", file_info.get('FrameOfReferenceUID', 'N/A')),
                        'StudyDate': getattr(dicom_file, "StudyDate", ''),
                        'SeriesDate': getattr(dicom_file, "SeriesDate", ''),
                        'RegistrationMatrixList': matrix_list,
                        'RegistrationSequence': reg_seq,
                        'DCM_Info': dicom_file,
                        'DataType': 'DICOM',
                        'OriginalFilePath': file_path,
                    },
                    'images': {},
                    'ImagePositionPatients': [],
                    'SliceImageComments': {},
                }
                
            modality_data.append(existing_series_data)
        
        if modality == 'RTIMAGE' or modality == 'CT' or modality == 'MR':
            existing_series_data['images'][instance_number] = {
                'ImageData': image,
                'ImagePositionPatient': image_position_patient,
            }
            existing_series_data['ImagePositionPatients'].append(image_position_patient)
            existing_series_data['SliceImageComments'][instance_number] = getattr(dicom_file, "ImageComments", '')
            existing_series_data.setdefault('slice_list', []).append({
                'ImageData': image,
                'ImagePositionPatient': image_position_patient,
                'ImageOrientationPatient': getattr(dicom_file, "ImageOrientationPatient", None),
                'InstanceNumber': instance_number,
                'ImageComments': getattr(dicom_file, "ImageComments", ''),
                'SliceThickness': sli_thick,
                'PixelSpacing': getattr(dicom_file, "PixelSpacing", None),
            })
        elif modality == 'RTDOSE':
           # RT dose are loaded using absolut coordinates 
           # Initial position and voxel size are difned when displaying so it alignes with referenced images
           # Get the dimensions
           existing_series_data['3DMatrix'] = image.reshape((dicom_file.NumberOfFrames, dicom_file.Rows, dicom_file.Columns)) 

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
    
    warnings_list = []

    for patient_id, studies in structured_data.items():
        for study_id, modalities in studies.items():
            for modality in list(modalities.keys()):
                series_list = modalities[modality]
                valid_series = []
                for index, series_data in enumerate(series_list):
                    try:
                        if modality in ('CT', 'MR'):
                            assemble_and_reorient_volume(series_data)
                        elif modality == 'RTIMAGE':
                            sorted_comments = sorted(series_data['SliceImageComments'].items(), key=lambda x: x[0])
                            # Extract only the values from the sorted list of tuples
                            series_data['SliceImageComments'] = [comment for _, comment in sorted_comments]
                            sorted_image_data = sorted(series_data['images'].items(), key=lambda x: x[0])
                            series_data['3DMatrix'] = np.stack([item[1]['ImageData'] for item in sorted_image_data], axis=0)
                            series_data['3DMatrix'] = np.flip(series_data['3DMatrix'], axis=1)
                            #
                            series_data['3DMatrix'] = series_data['3DMatrix'].astype(np.float32)
                        elif modality == 'RTDOSE':
                            # series_data['3DMatrix'] was already populated directly in the first loop
                            series_data['3DMatrix'] = np.flip(series_data['3DMatrix'], axis=1)
                            
                            # Check if Z-axis needs to be flipped based on GridFrameOffsetVector
                            dicom_file_ref = series_data['metadata']['DCM_Info']
                            vect = getattr(dicom_file_ref, "GridFrameOffsetVector", None)
                            if vect is not None and len(vect) >= 2:
                                series_data['metadata']['SliceThickness'] = float(abs(vect[1] - vect[0]))
                                if vect[1] - vect[0] < 0:
                                    series_data['3DMatrix'] = np.flip(series_data['3DMatrix'], axis=0)
                                    orig = list(series_data['metadata']['ImagePositionPatient'])
                                    orig[2] = float(dicom_file_ref.ImagePositionPatient[2] + vect[-1])
                                    series_data['metadata']['ImagePositionPatient'] = orig
                                    
                            series_data['3DMatrix'] = series_data['3DMatrix'].astype(np.float32)
                            series_data['3DMatrix'] = series_data['3DMatrix']*series_data['metadata']['DoseGridScaling']
                            active_dose = series_data['3DMatrix'][series_data['3DMatrix'] > 0.0]
                            if active_dose.size > 0:
                                mean_active = float(np.mean(active_dose))
                                series_data['metadata']['WindowWidth'] = mean_active * 2.0
                                series_data['metadata']['WindowCenter']= mean_active
                            else:
                                ref_value = np.max(series_data['3DMatrix'])
                                series_data['metadata']['WindowWidth'] = ref_value if ref_value > 0 else 10.0
                                series_data['metadata']['WindowCenter']= ref_value * 0.5 if ref_value > 0 else 5.0
                        #
                        elif modality == 'RTPLAN':
                            # Store patient_id, study_id, modality, and other relevant data
                            rtplan_info = {
                                'patient_id': patient_id,
                                'study_id': study_id,
                                'modality': modality,
                                'series_data_ref': series_data,
                                'PlanLabel': series_data['metadata']['RTPlanLabel']
                            }
                            rtplan_files.append(rtplan_info)
                        elif modality == 'RTSTRUCT':
                            # Store patient_id, study_id, modality, and other relevant data
                            rtstruct_info = {
                                'patient_id': patient_id,
                                'study_id': study_id,
                                'modality': modality,
                                'series_data_ref': series_data,
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
                        if 'slice_list' in series_data:
                            del series_data['slice_list']
                        #
                        lut_label = series_data['metadata'].get('LUTLabel', 'N/A')
                        if '3DMatrix' in series_data and series_data['3DMatrix'] is not None:
                            if lut_label == "SPR":
                                series_data['3DMatrix'] = (series_data['3DMatrix'] / 1000) + 1
                                series_data['metadata']['WindowWidth'] = 0.5
                                series_data['metadata']['WindowCenter'] = 1.0
                            elif lut_label == "EFF_ATOMIC_NUM":
                                series_data['metadata']['WindowWidth'] = 4
                                series_data['metadata']['WindowCenter'] = 8 
                            elif lut_label == "ELECTRON_DENSITY":
                                series_data['3DMatrix'] = (series_data['3DMatrix'] / 1000) + 1
                                series_data['metadata']['WindowWidth'] = 0.5
                                series_data['metadata']['WindowCenter'] = 1.0  
                            elif modality != 'RTDOSE' and modality != 'RTIMAGE':
                                series_data['3DMatrix'] = series_data['3DMatrix'].astype(np.int16)
                        
                        valid_series.append(series_data)
                    except Exception as e:
                        import os
                        import traceback
                        tb = traceback.format_exc()
                        fpath = series_data.get('metadata', {}).get('OriginalFilePath')
                        fdir = os.path.dirname(fpath) if fpath else "Unknown Folder"
                        warnings_list.append((series_data.get('SeriesNumber', 'Unknown'), modality, fdir, str(e)))
                        print(f"[WARN] Skipped series {series_data.get('SeriesNumber')} ({modality}) due to error: {e}\n{tb}")

                modalities[modality] = valid_series

    # Re-calculate correct series_index after filtering out any bad series
    for plan in rtplan_files:
        try:
            lst = structured_data[plan['patient_id']][plan['study_id']][plan['modality']]
            plan['series_index'] = lst.index(plan['series_data_ref'])
        except (ValueError, KeyError):
            plan['series_index'] = -1

    for rtstruct in rtstruct_files:
        try:
            lst = structured_data[rtstruct['patient_id']][rtstruct['study_id']][rtstruct['modality']]
            rtstruct['series_index'] = lst.index(rtstruct['series_data_ref'])
        except (ValueError, KeyError):
            rtstruct['series_index'] = -1

    # Filter out any plans/structs whose referenced series was removed/skipped
    rtplan_files = [p for p in rtplan_files if p['series_index'] != -1]
    rtstruct_files = [r for r in rtstruct_files if r['series_index'] != -1]

    # Show warning QMessageBox on GUI thread if there were load errors
    if warnings_list:
        try:
            from PySide6.QtWidgets import QMessageBox
            from PySide6.QtCore import QCoreApplication
            
            msg = "Some DICOM series failed to load (e.g. inconsistent image slice sizes). The affected series have been skipped:\n\n"
            for s_num, mod, fdir, err in warnings_list:
                msg += f"• Series {s_num} ({mod}) in folder:\n  {fdir}\n  Error: {err}\n\n"
            
            # Show QMessageBox only if 'self' is a QWidget
            from PySide6.QtWidgets import QWidget
            if isinstance(self, QWidget):
                QMessageBox.warning(self, "DICOM Load Warning", msg)
            else:
                print(f"[DICOM Load Warning]\n{msg}")
        except Exception as q_err:
            print(f"Failed to display QMessageBox warning: {q_err}")

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
        matching_rtstruct = None
        # Now, search in rtstruct_files for a matching SOPInstanceUID
        # this is required to get the correct RTSTRUCT file for the current RTPLAN Varian stores catether delineation in a RTSTRUCT file while
        # dwell positions and times are stored in the RTPLAN file

        # Oncentra sotres the catether delineation in the RTPLAN file
        PrivateCreator = structured_data[plan['patient_id']][plan['study_id']][plan['modality']][plan['series_index']]['metadata']['PrivateCreator']

        if PrivateCreator != 'NUCLETRON':
            for rtstruct in rtstruct_files:
                if rtstruct['SOPInstanceUID'] == ref_struct_UID:
                    matching_rtstruct = rtstruct
                    break  # Stop the search once a match is found
        else:
            # ONCENTRA uses this tag 'Private_300f_1000'
            matching_rtstruct = 'NUCLETRON'
        
        # call a function to process plan data ... which is different depeding on TPS and treatment type.    
        process_rt_plans(plan,matching_rtstruct,structured_data)    
    #
    for rtstruct in rtstruct_files:
        process_rt_struct(self, rtstruct,structured_data)
  
    

    return structured_data, non_im_files 
 

def load_all_dcm(self, folder_path=None, progress_callback=None, update_label=None):
    """
    Load and append DICOM data into self.medical_image without overwriting existing entries.
    """
    detailed_files_info, unique_files_info, folder = get_data_description(
        folder_path, self.progressBar.setValue, update_label
    )
    self.files_info = detailed_files_info
    if detailed_files_info is None:
        return

    total_steps = len(detailed_files_info)

    if update_label:
        update_label.setText(f"Loading {total_steps} files")

    # ✅ Only create if not present
    if not hasattr(self, 'medical_image') or self.medical_image is None or not isinstance(self.medical_image, dict):
        self.medical_image = {}

    # Load into a temporary dict
    new_data, non_im_files = load_images(
        self, detailed_files_info, self.progressBar.setValue, total_steps
    )

    # ✅ Merge new data into existing self.medical_image
    for patient_id, studies in new_data.items():
        patient_data = self.medical_image.setdefault(patient_id, {})
        for study_id, modalities in studies.items():
            study_data = patient_data.setdefault(study_id, {})
            for modality, series_list in modalities.items():
                modality_data = study_data.setdefault(modality, [])
                modality_data.extend(series_list)  # append series

    # Clear the segmentation structure list (if tab_seg has been created)
    if hasattr(self, 'segStructList') and self.segStructList is not None and hasattr(self.segStructList, 'clear'):
        self.segStructList.clear()

    self.DataType = "DICOM"
    populate_medical_image_tree(self)


if __name__ == "__main__":
    medical_image = load_all_dcm()
    # data_plot = medical_image['Siem_K']['4']['CT'][0]['3DMatrix']
    # # Plot an axial slice - for example the fifth slice along the third axis (0-indexed)
    # axial_slice = data_plot[150, :,:]
    # plt.imshow(axial_slice, cmap='gray')
    # plt.colorbar()
    # plt.title('Axial Slice')
    # plt.show()
    for patient_id, patient_data in medical_image.items():
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
                    
                    
