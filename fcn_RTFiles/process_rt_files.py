import numpy as np
import copy
from skimage.draw import polygon
from skimage.measure import find_contours
from fcn_load.populate_dcm_list import populate_DICOM_tree
from fcn_RTFiles.process_mevion import read_proton_plan


from PyQt5.QtWidgets import (
    QWidget, QCheckBox, QLabel, QPushButton, QHBoxLayout,
    QVBoxLayout, QColorDialog, QDoubleSpinBox, QListWidgetItem,
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt



from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QCheckBox, QLabel, QPushButton, QDoubleSpinBox, QColorDialog
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class set_struct_table(QWidget):
    """
    mode=0 → checkbox + name only
    mode=1 → + color button, line width, transparency
    """
    def __init__(
        self, text, idx, mode=1, parent=None,
        on_toggle=None, on_color=None, on_line_width=None, on_transparency=None,
        on_refresh=None,
        init_color=None, init_line_width=None, init_transparency=None
    ):
        super().__init__(parent)
        self._on_refresh = on_refresh
        self._on_color = on_color
        self.selectedColor = None
        self.idx = idx
        self._mode = 1 if mode else 0

        # Always-visible
        self.checkbox = QCheckBox()
        self.label = QLabel(text)

        # Optional controls
        self.controls_container = QWidget(self)
        cc = QHBoxLayout(self.controls_container)
        cc.setContentsMargins(0, 0, 0, 0)

        self.color_button = QPushButton("Select Color")
        self.color_button.setMaximumWidth(100)
        self.color_button.clicked.connect(self.openColorDialog)

        self.line_width_spinbox = QDoubleSpinBox()
        self.line_width_spinbox.setRange(0.1, 50.0)
        self.line_width_spinbox.setDecimals(1)
        self.line_width_spinbox.setSingleStep(0.5)

        self.transparency_spinbox = QDoubleSpinBox()
        self.transparency_spinbox.setRange(0.0, 1.0)
        self.transparency_spinbox.setDecimals(2)
        self.transparency_spinbox.setSingleStep(0.1)

        cc.addWidget(self.color_button)
        cc.addWidget(QLabel("LineW:"))
        cc.addWidget(self.line_width_spinbox)
        cc.addWidget(QLabel("Transp:"))
        cc.addWidget(self.transparency_spinbox)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)
        layout.addWidget(self.controls_container)
        layout.addStretch(1)
        self.controls_container.setVisible(bool(self._mode))

        # Callbacks
        self._on_color = on_color

        if self._mode == 1:
            # one handler to do both: save flag + refresh views
            if on_toggle is not None or on_refresh is not None:
                def _on_toggled(checked, i=self.idx):
                    if on_toggle is not None:
                        on_toggle(i, checked)
                    if on_refresh is not None:
                        on_refresh()
                self.checkbox.toggled.connect(_on_toggled)

            if on_line_width is not None:
                def _lw(v, i=self.idx):
                    on_line_width(i, float(v))
                    if self._on_refresh: self._on_refresh()
                self.line_width_spinbox.valueChanged.connect(_lw)
            if on_transparency is not None:
                def _tr(v, i=self.idx):
                    on_transparency(i, float(v))
                    if self._on_refresh: self._on_refresh()
                self.transparency_spinbox.valueChanged.connect(_tr)

        # Initialize controls in mode=1
        if self._mode == 1:
            self.set_color(QColor(init_color) if init_color else QColor(Qt.white))
            self.line_width_spinbox.setValue(3.0 if init_line_width is None else float(init_line_width))
            self.transparency_spinbox.setValue(0.1 if init_transparency is None else float(init_transparency))

    def set_checked(self, checked: bool):
        # programmatic set without emitting signals (no redraw during init)
        old = self.checkbox.blockSignals(True)
        self.checkbox.setChecked(bool(checked))
        self.checkbox.blockSignals(old)

    def set_color(self, color: QColor):
        self.selectedColor = color
        self.color_button.setStyleSheet(f"background-color: {color.name()};")

    def openColorDialog(self):
        color = QColorDialog.getColor(
            initial=self.selectedColor or QColor(Qt.white),
            parent=self
        )
        if color.isValid():
            self.set_color(color)
            if self._on_color is not None:
                self._on_color(self.idx, color.name())
            if self._on_refresh is not None:
                self._on_refresh()


def _refresh_all_views(self):
    from fcn_display.display_images  import disp_structure_overlay_axial, disp_structure_overlay_coronal, disp_structure_overlay_sagittal
    disp_structure_overlay_sagittal(self)
    disp_structure_overlay_coronal(self)
    disp_structure_overlay_axial(self)



def update_structure_list_widget(self, structure_names, structure_keys, mode=1):
    from functools import partial
    self.STRUCTlist.clear()
    n = len(structure_names)

    # ensure arrays exist
    view_flags   = _ensure_structures_view(self, n)
    colors       = _ensure_structures_color(self, n)
    line_widths  = _ensure_structures_line_width(self, n)
    transpars    = _ensure_structures_transparency(self, n)

    for idx, (name, key) in enumerate(zip(structure_names, structure_keys)):
        list_item = QListWidgetItem(self.STRUCTlist)

        on_toggle       = (lambda i, checked: _set_structure_view_flag(self, i, checked)) if mode == 1 else None
        on_color        = (lambda i, hexstr:   _set_structure_color(self, i, hexstr))      if mode == 1 else None
        on_line_width   = (lambda i, v:        _set_structure_line_width(self, i, v))      if mode == 1 else None
        on_transparency = (lambda i, v:        _set_structure_transparency(self, i, v))    if mode == 1 else None
        on_refresh = (partial(_refresh_all_views, self) if mode == 1 else None)

        custom_item = set_struct_table(
            name, idx=idx, mode=mode,
            on_toggle=on_toggle,
            on_color=on_color,
            on_line_width=on_line_width,
            on_transparency=on_transparency,
            on_refresh=on_refresh,
            init_color=colors[idx] if idx < len(colors) else "#ffffff",
            init_line_width=line_widths[idx] if idx < len(line_widths) else 2.0,
            init_transparency=transpars[idx] if idx < len(transpars) else 0.0
        )
        custom_item.structure_key = key

        # programmatic init: won't trigger redraw thanks to blockSignals
        custom_item.set_checked(bool(view_flags[idx]) if idx < len(view_flags) else False)

        list_item.setSizeHint(custom_item.sizeHint())
        self.STRUCTlist.addItem(list_item)
        self.STRUCTlist.setItemWidget(list_item, custom_item)

    # ── Normalize widths across rows ───────────────────────────────────────────
    rows = []
    for i in range(self.STRUCTlist.count()):
        item = self.STRUCTlist.item(i)
        w = self.STRUCTlist.itemWidget(item)
        if w is not None:
            # make sure hints are up-to-date
            if w.layout() is not None:
                w.layout().activate()
            w.adjustSize()
            rows.append((item, w))

    if rows:
        # pick maximums
        max_row_w      = max((w.sizeHint().width() for _, w in rows), default=0)
        max_label_w    = max((w.label.sizeHint().width() for _, w in rows), default=0)
        # controls_container might be hidden in mode=0
        max_controls_w = max((w.controls_container.sizeHint().width()
                              for _, w in rows if w.controls_container.isVisible()), default=0)

        for item, w in rows:
            # align columns
            w.label.setMinimumWidth(max_label_w)
            if w.controls_container.isVisible():
                w.controls_container.setMinimumWidth(max_controls_w)
            # enforce same total row width (prevents narrower rows)
            w.setMinimumWidth(max_row_w)
            # refresh item size hint (height primarily matters in QListWidget)
            item.setSizeHint(w.sizeHint())

    if mode ==1:
        self.CreateMask_Structures.setVisible(False)
    else:   
        self.CreateMask_Structures.setVisible(True)

def _series_dict(self):
    return self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]

def _ensure_array(self, key, n, default_value):
    s = _series_dict(self)
    arr = s.get(key)
    if not isinstance(arr, list):
        arr = []
    # resize while preserving existing values
    if len(arr) < n:
        arr = arr + [default_value] * (n - len(arr))
    elif len(arr) > n:
        arr = arr[:n]
    s[key] = arr
    return arr

# view flags (0/1)
def _ensure_structures_view(self, n):           return _ensure_array(self, 'structures_view',         n, 0)

def _set_structure_view_flag(self, idx, checked):
    v = _ensure_structures_view(self, len(_series_dict(self).get('structures_names', [])))
    if 0 <= idx < len(v):
        v[idx] = 1 if checked else 0

# colors as hex strings "#rrggbb"
def _ensure_structures_color(self, n):          return _ensure_array(self, 'structures_color',        n, "#1b87ae")

def _set_structure_color(self, idx, hexstr):
    v = _ensure_structures_color(self, len(_series_dict(self).get('structures_names', [])))
    if 0 <= idx < len(v):
        v[idx] = hexstr

# line widths as float
def _ensure_structures_line_width(self, n):     return _ensure_array(self, 'structures_line_width',   n, 2.0)

def _set_structure_line_width(self, idx, val):
    v = _ensure_structures_line_width(self, len(_series_dict(self).get('structures_names', [])))
    if 0 <= idx < len(v):
        v[idx] = float(val)

# transparency as float [0,1]
def _ensure_structures_transparency(self, n):   return _ensure_array(self, 'structures_transparency', n, 0.5)

def _set_structure_transparency(self, idx, val):
    v = _ensure_structures_transparency(self, len(_series_dict(self).get('structures_names', [])))
    if 0 <= idx < len(v):
        v[idx] = float(val)

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
    series_data['structures']        = structures
    series_data['structures_names']  = structures_names
    series_data['structures_keys']   = structures_keys



def process_rt_plans(plan,ref_str,structured_data):
    # 
    if structured_data[plan['patient_id']][plan['study_id']][plan['modality']][plan['series_index']]['metadata']['BrachyTreatmentType'] != 'N/A':
        read_brachy_plan(plan,ref_str,structured_data)
    elif structured_data[plan['patient_id']][plan['study_id']][plan['modality']][plan['series_index']]['metadata']['TreatmentProtocols'] != 'N/A':
        read_proton_plan(plan, structured_data)




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



        
