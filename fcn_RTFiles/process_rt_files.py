import numpy as np
import copy
from skimage.draw import polygon
from skimage.measure import find_contours
from fcn_load.populate_dcm_list import populate_DICOM_tree


from PyQt5.QtWidgets import (
    QWidget, QCheckBox, QLabel, QPushButton, QHBoxLayout,
    QVBoxLayout, QColorDialog, QDoubleSpinBox, QListWidgetItem,
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt



class ColorCheckItem(QWidget):
    """
    A custom widget that displays:
      - A checkbox (to toggle the structure on/off),
      - A label (for the structure name),
      - A color-selection button,
      - A 'Line Width' spinbox,
      - A 'Transparency' spinbox,
      - A 'Fill' checkbox (to indicate whether to display a filled polygon).
    """

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.selectedColor = None

        # 1) Master checkbox to enable/disable the structure
        self.checkbox = QCheckBox()
        # 2) Label for the structure name
        self.label = QLabel(text)

        # 3) Button to pick color
        self.color_button = QPushButton("Select Color")
        self.color_button.setMaximumWidth(100)
        self.color_button.clicked.connect(self.openColorDialog)

        # 4) Spinbox for line width
        self.line_width_spinbox = QDoubleSpinBox()
        self.line_width_spinbox.setRange(0.1, 50.0)
        self.line_width_spinbox.setValue(2.0)
        self.line_width_spinbox.setSingleStep(0.5)
        self.line_width_spinbox.setDecimals(1)

        # 5) Spinbox for transparency (0=opaque, 1=fully transparent)
        self.transparency_spinbox = QDoubleSpinBox()
        self.transparency_spinbox.setRange(0.0, 1.0)
        self.transparency_spinbox.setValue(0.5)
        self.transparency_spinbox.setSingleStep(0.1)
        self.transparency_spinbox.setDecimals(2)

        # 6) Checkbox to indicate whether to fill the contour
        # self.fill_checkbox = QCheckBox("Fill")
        # self.fill_checkbox.setChecked(False)  # default: wireframe

        # Lay out horizontally
        layout = QHBoxLayout()
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)
        layout.addWidget(self.color_button)
        layout.addWidget(QLabel("LineW:"))
        layout.addWidget(self.line_width_spinbox)
        layout.addWidget(QLabel("Transp:"))
        layout.addWidget(self.transparency_spinbox)
        # layout.addWidget(self.fill_checkbox)

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def openColorDialog(self):
        color = QColorDialog.getColor(
            initial=self.selectedColor or QColor(Qt.white),
            parent=self
        )
        if color.isValid():
            self.selectedColor = color
            self.color_button.setStyleSheet(f"background-color: {color.name()};")


def update_structure_list_widget(self, structure_names, structure_keys):
    """
    Update self.STRUCTlist (a QListWidget) with custom items that display the structure name,
    a checkbox, and a color-selection button. The corresponding structure key is stored in the custom widget.
    """
    self.STRUCTlist.clear()
    for name, key in zip(structure_names, structure_keys):
        list_item = QListWidgetItem(self.STRUCTlist)
        custom_item = ColorCheckItem(name)
        custom_item.structure_key = key  # Save the key for later lookup
        list_item.setSizeHint(custom_item.sizeHint())
        self.STRUCTlist.addItem(list_item)
        self.STRUCTlist.setItemWidget(list_item, custom_item)

def process_rt_struct(self, rtstruct, structured_data):
    """
    Corrected function to process RTSTRUCT data ensuring
    structures_names and structures_keys always match explicitly.
    """

    patient_id   = rtstruct['patient_id']
    study_id     = rtstruct['study_id']
    modality     = rtstruct['modality']
    series_index = rtstruct['series_index']

    try:
        series_data = structured_data[patient_id][study_id][modality][series_index]
    except KeyError:
        print("Error: Series not found, check identifiers.")
        return

    metadata = series_data.get('metadata')
    if metadata is None:
        print("Error: No metadata found.")
        return

    rt_roi_obs_seq  = metadata.get('RTROIObservationsSequence')
    roi_contour_seq = metadata.get('ROIContourSequence')
    structure_set_roi_seq = metadata.get('StructureSetROISequence')

    if rt_roi_obs_seq is None or roi_contour_seq is None:
        print("Error: Required sequences missing in metadata.")
        return

    structures = series_data.setdefault('structures', {})
    structures_names = []
    structures_keys  = []

    for idx, obs_item in enumerate(rt_roi_obs_seq):
        key = f"Item_{idx+1}"

        if getattr(obs_item, 'RTROIInterpretedType', '') == 'BRACHY_CHANNEL':
            continue

        ref_roi_number = getattr(obs_item, 'ReferencedROINumber', None)
        if ref_roi_number is None:
            print(f"{key}: ReferencedROINumber missing; skipping.")
            continue

        roi_name = getattr(obs_item, 'ROIObservationLabel', None)
        if roi_name is None and structure_set_roi_seq:
            roi_name = next(
                (roi_item.ROIName for roi_item in structure_set_roi_seq
                 if getattr(roi_item, 'ROINumber', None) == ref_roi_number), None)

        if roi_name is None:
            roi_name = key

        # Match ROIContour explicitly by ReferencedROINumber
        matched_contour = next(
            (contour_item for contour_item in roi_contour_seq
             if getattr(contour_item, 'ReferencedROINumber', None) == ref_roi_number), None)

        if matched_contour and hasattr(matched_contour, 'ContourSequence'):
            copied_obs = copy.deepcopy(obs_item)
            copied_obs.ContourSequence = copy.deepcopy(matched_contour.ContourSequence)

            structures[key] = copied_obs
            structures_names.append(roi_name)
            structures_keys.append(key)
        else:
            print(f"No valid contours for '{roi_name}' (ROI {ref_roi_number}); skipping.")

    # Explicitly update structured_data
    series_data['structures'] = structures
    series_data['structures_names'] = structures_names
    series_data['structures_keys'] = structures_keys



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
    print(ref_str)
    if ref_str != 'NUCLETRON' and ref_str != None:
        # struct set reference to get channels geometry (Varian)
        stru_info       = structured_data[ref_str['patient_id']][ref_str['study_id']][ref_str['modality']][ref_str['series_index']]['metadata']['ROIContourSequence']
    else:
        # Get the reference contours (Nucletron) for each channel
        brachy_channel_points = []
        if ref_str == 'NUCLETRON':
            cat_onc_element = structured_data[plan['patient_id']][plan['study_id']][plan['modality']][plan['series_index']]['metadata']['CatOnc']
            first_item = cat_onc_element.value[0]

            roi_contour_sequence = getattr(first_item, 'ROIContourSequence', [])
            rt_roi_obs_sequence = getattr(first_item, 'RTROIObservationsSequence', [])

            if roi_contour_sequence and rt_roi_obs_sequence:
                for roi_contour, rt_roi_obs in zip(roi_contour_sequence, rt_roi_obs_sequence):
                    interpreted_type = getattr(rt_roi_obs, 'RTROIInterpretedType', '')
                    if interpreted_type == 'BRACHY_CHANNEL':
                        contour_sequence = getattr(roi_contour, 'ContourSequence', [])
                        if contour_sequence:
                            contour_data = contour_sequence[0].ContourData
                            points_array = np.array(contour_data, dtype=np.float32)
                            if len(points_array) % 3 == 0:
                                points_matrix = points_array.reshape((-1, 3))
                                brachy_channel_points.append(points_matrix)
                            else:
                                brachy_channel_points.append(np.empty((0, 3), dtype=np.float32))
            else:
                print("ROIContourSequence or RTROIObservationsSequence missing or empty.")
    #
    #
    # Initialize a list to hold channel information - Dwell and Catheter
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
        points_matrix = np.empty((0, 3), dtype=np.float32)
        # Varian
        if ref_str != 'NUCLETRON' and ref_str != None:
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
        #Nucletron
        elif ref_str == 'NUCLETRON':
            if chan_idx < len(brachy_channel_points):
                points_matrix = brachy_channel_points[chan_idx]
            else:
                print(f"Warning: No BRACHY_CHANNEL match for chan_idx {chan_idx}")
                points_matrix = np.empty((0, 3), dtype=np.float32)

                if not found_channel:
                    print(f"No BRACHY_CHANNEL found matching chan_idx={chan_idx}. Using empty points_matrix.")

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
        structured_data[plan['patient_id']][plan['study_id']][plan['modality']][plan['series_index']]['metadata']['ReferenceAirKermaRate']= structured_data[plan['patient_id']][plan['study_id']][plan['modality']][plan['series_index']]['metadata']['SourceSequence'][0]['ReferenceAirKermaRate']



        
