import numpy as np
from skimage.draw import polygon
from skimage.measure import find_contours
from fcn_load.populate_dcm_list import populate_DICOM_tree
from PyQt5.QtWidgets import QMessageBox, QDialog
from scipy.ndimage import gaussian_filter1d
from scipy.signal import savgol_filter
import vtk


from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QProgressDialog, QMessageBox
from fcn_materialassignment.material_map import update_mat_struct_list
from fcn_init.datatree_selection_box import SeriesPickerDialog


def find_matching_series(self, Ref):
    """Search through all studies, modalities, and series for the given SeriesInstanceUID (Ref). 
       Returns a list of all matches found.
    """
    matches = []

    # Make sure this patientID is in dicom_data
    if self.patientID not in self.dicom_data:
        print(f"No data found for patientID={self.patientID}")
        return matches

    # Loop over all studies for this patient
    for studyID, study_data in self.dicom_data[self.patientID].items():
        # Loop over all modalities in each study
        for modality, modality_data in study_data.items():
            # If the next level is a list, iterate accordingly
            if isinstance(modality_data, list):
                for series_index, series_data in enumerate(modality_data):
                    # Extract the UID, compare to Ref
                    metadata = series_data.get('metadata', {})
                    dcm_info = metadata.get('DCM_Info', {})
                    series_uid = dcm_info.get('SeriesInstanceUID')

                    if series_uid == Ref:
                        Acq_number   = metadata.get('AcquisitionNumber')
                        matches={
                            'studyID'      : studyID,
                            'modality'     : modality,
                            'series_index' : series_index,
                            'series_label' : f"Acq_{Acq_number}_Series: {series_data.get('SeriesNumber')}"
                        }
                        self.StructRefSeries.setText(f"Acq_{Acq_number}_Series: {series_data.get('SeriesNumber')}")
                        break
            else:
                # Unexpected structure; handle or ignore
                print(f"Unexpected structure at modality '{modality}' in study '{studyID}'. "
                      f"Expected dict or list, got {type(modality_data)}.")
                continue

    return matches

class ContourWorker(QObject):
    progress = pyqtSignal(int)
    message  = pyqtSignal(str)
    finished = pyqtSignal()
    canceled = pyqtSignal()

    def __init__(self, parent, data_dict, target_series_dict,
                 structures_keys, structures_names,
                 mask_shape, spacing, origin, start_index, pixel_spac):
        super().__init__()
        self.parent = parent
        self.data_dict = data_dict
        self.target = target_series_dict
        self.keys = structures_keys
        self.names = structures_names
        self.mask_shape = mask_shape
        self.spacing = spacing
        self.origin = origin
        self.current_index = start_index
        self.px_space = pixel_spac
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        total = len(self.keys)
        for idx, key in enumerate(self.keys):
            if self._is_cancelled:
                self.canceled.emit()
                return

            name = self.names[idx]
            self.message.emit(f"Loading “{name}”…")
            self.progress.emit(int((idx / total) * 100))

            structure = self.data_dict['structures'][key]
            contour_seq = getattr(structure, 'ContourSequence', None)

            if not contour_seq:
                mask = np.zeros(self.mask_shape, dtype=np.uint8)
            else:
                mask, all_points = create_3d_mask_for_structure_simple(
                    self.parent, structure,
                    self.mask_shape, self.spacing, self.origin, self.px_space
                )
                if not mask.any():
                    mask = np.zeros(self.mask_shape, dtype=np.uint8)
                    all_points = np.empty((0, 3), dtype=float)

            new_key = f"Structure_{self.current_index:03d}"
            entry = {
                'Mask3D':    mask,
                'Name':      name,
                'Modified':  0,
                'Contours2D': {'axial':{}, 'sagittal':{}, 'coronal':{}},
                'Contours3D': all_points
            }
            self.target['structures'][new_key] = entry
            self.target['structures_names'].append(name)
            self.target['structures_keys'].append(new_key)
            self.current_index += 1

        self.progress.emit(100)
        self.finished.emit()


def create_contour_masks(self):
    if getattr(self, 'DataType', None) != "DICOM":
        QMessageBox.warning(None, "Warning", "No DICOM data was found")
        return
    # ─── 1) gather data ●────────────────────────────────────────────
    data_dict = self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]

    # ── 2) Ask user to pick the destination/target series ───────────
    dlg = SeriesPickerDialog(
        self.dicom_data,
        excluded_modalities={'RTPLAN', 'RTSTRUCT', 'RTDOSE'},
        source_tuple=(self.patientID_struct, self.StructRefSeries.text()),
        parent=self
    )

    if dlg.exec_() != QDialog.Accepted or dlg.selected_series_tuple is None:
        QMessageBox.information(self, "Canceled", "No destination series selected.")
        return

    dest_patient = dlg.selected_patient
    _, dest_study, dest_modality, dest_index = dlg.selected_series_tuple

    # Validate and fetch the selected target
    try:
        target = self.dicom_data[dest_patient][dest_study][dest_modality][dest_index]
    except Exception:
        QMessageBox.warning(self, "Error", "Selected destination series could not be loaded.")
        return

    pixel_spac     = np.array(self.dicom_data[dest_patient][dest_study][dest_modality][dest_index]['metadata']['PixelSpacing'])[None, :]
    slice_thick    = np.array(self.dicom_data[dest_patient][dest_study][dest_modality][dest_index]['metadata']['SliceThickness'])
    Im_PatPosition = np.array(self.dicom_data[dest_patient][dest_study][dest_modality][dest_index]['metadata']['ImagePositionPatient'])

    # ─── 2) Replace vs. Append ●────────────────────────────────────
    existing = target.get('structures', {})
    count_existing = len(existing)
    if existing:
        dlg = QMessageBox(self)
        dlg.setIcon(QMessageBox.Question)
        dlg.setWindowTitle("Structures Exist")
        dlg.setText("Structures already exist. What would you like to do?")
        btn_replace = dlg.addButton("Replace", QMessageBox.AcceptRole)
        btn_append  = dlg.addButton("Append",  QMessageBox.RejectRole)
        dlg.exec_()

        if dlg.clickedButton() == btn_replace:
            target['structures']        = {}
            target['structures_keys']   = []
            target['structures_names']  = []
            start_index = 1
        else:
            start_index = count_existing + 1
    else:
        target['structures']        = {}
        target['structures_keys']   = []
        target['structures_names']  = []
        start_index = 1

    # ─── 3) geometry ●───────────────────────────────────────────────
    volume_3d = target.get('3DMatrix', None)
    mask_shape = volume_3d.shape
    z_sp, yx_sp = slice_thick, pixel_spac[0, :2]
    spacing = (z_sp, *yx_sp)
    origin  = tuple(Im_PatPosition)

    # ─── 4) filter by checkbox ●────────────────────────────────────
    all_keys  = data_dict.get('structures_keys', [])
    all_names = data_dict.get('structures_names', [])
    sel_keys, sel_names = [], []
    for idx, key in enumerate(all_keys):
        item   = self.STRUCTlist.item(idx)
        widget = self.STRUCTlist.itemWidget(item)
        if widget.checkbox.isChecked():
            sel_keys.append(key)
            sel_names.append(all_names[idx])

    if not sel_keys:
        QMessageBox.information(self, "No Structures Selected",
                                "Please check at least one structure to import.")
        return

    # ─── 5) progress dialog ●────────────────────────────────────────
    prog_dlg = QProgressDialog("Starting…", "Cancel", 0, 100, self)
    prog_dlg.setWindowModality(Qt.WindowModal)
    prog_dlg.setAutoClose(False)
    prog_dlg.setAutoReset(False)
    prog_dlg.setMinimumDuration(0)
    prog_dlg.setValue(0)

    # ─── 6) worker + thread ●────────────────────────────────────────
    worker = ContourWorker(self, data_dict, target,
                           sel_keys, sel_names,
                           mask_shape, spacing, origin,
                           start_index,pixel_spac)
    thread = QThread(self)
    worker.moveToThread(thread)

    # ─── 7) wire signals ●───────────────────────────────────────────
    worker.progress.connect(self.progressBar.setValue)
    worker.progress.connect(prog_dlg.setValue)
    worker.message.connect(prog_dlg.setLabelText)
    prog_dlg.canceled.connect(worker.cancel)

    worker.finished.connect(thread.quit)
    worker.finished.connect(prog_dlg.close)
    worker.finished.connect(lambda: populate_DICOM_tree(self))

    worker.canceled.connect(thread.quit)
    worker.canceled.connect(prog_dlg.close)
    worker.canceled.connect(lambda:
        QMessageBox.information(self, "Cancelled", "Contour generation cancelled.")
    )

    thread.started.connect(worker.run)
    thread.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    # ─── 8) start! ●──────────────────────────────────────────────────
    thread.start()
    prog_dlg.exec_()
    # """Uncheck every checkbox in the STRUCTlist."""
    for i in range(self.STRUCTlist.count()):
        item = self.STRUCTlist.item(i)
        widget = self.STRUCTlist.itemWidget(item)
        # assume widget.checkbox is your QCheckBox
        if hasattr(widget, 'checkbox'):
            widget.checkbox.setChecked(False)
    populate_DICOM_tree(self)
    #update_mat_struct_list(self)


def build_contours_for_structure(mask_3d):
    contours = {'axial': {}, 'sagittal': {}, 'coronal': {}}

    # axial slices
    for z, slice_ in enumerate(mask_3d):
        c = extract_contours_from_binary_slice(slice_)
        if c:
            contours['axial'][z] = c

    # sagittal slices
    for x in range(mask_3d.shape[2]):
        c = extract_contours_from_binary_slice(mask_3d[:, :, x])
        if c:
            contours['sagittal'][x] = c

    # coronal slices
    for y in range(mask_3d.shape[1]):
        c = extract_contours_from_binary_slice(mask_3d[:, y, :])
        if c:
            contours['coronal'][y] = c

    return contours

def create_3d_mask_for_structure_simple(self, structure, mask_shape, spacing, origin, pixel_spac):
    mask_3d     = np.zeros(mask_shape, dtype=np.uint8)
    contour_seq = getattr(structure, 'ContourSequence', [])
    # Collect ALL original DICOM points in a list
    all_original_points = []

    if not contour_seq:
        print("No contour sequence found in structure.")
        return mask_3d, np.empty((0, 3), dtype=float)

    z_spacing, y_spacing, x_spacing = spacing
    origin_x, origin_y, origin_z = origin

    # flip coordinate to match Y 
    origin_y = -origin_y



    for contour in contour_seq:
        geom_type = getattr(contour, 'ContourGeometricType', '').upper()
        if geom_type != 'CLOSED_PLANAR':
            continue

        contour_data = getattr(contour, 'ContourData', [])
        if len(contour_data) % 3 != 0:
            continue

        points = np.array(contour_data).reshape(-1, 3)
        # Append all points to the big list
        all_original_points.append(points)
        # Need to flip y to match
        points[:, 1] = (mask_3d.shape[1] * pixel_spac[0, 0]) - points[:, 1]  # Y coordinate

        indices_float = (points - np.array([origin_x, origin_y, origin_z])) / [x_spacing, y_spacing, z_spacing]
        indices = indices_float.round().astype(int)

        slice_idx = indices[0, 2]
        if slice_idx < 0 or slice_idx >= mask_shape[0]:
            continue

        x_coords = indices[:, 0]
        y_coords = indices[:, 1]

        rr, cc = polygon(y_coords, x_coords, shape=mask_shape[1:])
        mask_3d[slice_idx, rr, cc] += 1

    # Combine all to single [N, 3] array (if there were any contours)
    if all_original_points:
        all_original_points_array = np.vstack(all_original_points)
    else:
        all_original_points_array = np.empty((0, 3), dtype=float)


    mask_3d = np.mod(mask_3d, 2).astype(np.uint8)



    return mask_3d, all_original_points_array




def extract_contours_from_binary_slice(slice_2d, level=0.4, smooth=True, method="gaussian"):
    """
    Extracts and optionally smooths contours from a binary slice.

    Parameters:
        slice_2d (ndarray): Binary mask slice
        level (float): Contour extraction threshold
        smooth (bool): Whether to apply smoothing
        method (str): Smoothing method ("savgol" or "gaussian")

    Returns:
        list of np.array: Extracted (and optionally smoothed) contours
    """
    contours = find_contours(slice_2d, level=level)
    
    if smooth:
        contours = smooth_contours(contours, method=method)

    return contours

def smooth_contours(contours, method="savgol", window_length=5, polyorder=2, sigma=1.0):
    """
    Smooths extracted contours using either a Savitzky-Golay filter or Gaussian smoothing.

    Parameters:
        contours (list of np.array): List of contours (each contour is Nx2)
        method (str): "savgol" (Savitzky-Golay) or "gaussian" (Gaussian filter)
        window_length (int): Window size for Savitzky-Golay filter
        polyorder (int): Polynomial order for Savitzky-Golay filter
        sigma (float): Standard deviation for Gaussian smoothing

    Returns:
        list of np.array: Smoothed contours
    """
    smoothed_contours = []
    
    for contour in contours:
        x, y = contour[:, 0], contour[:, 1]  # Separate x and y coordinates
        
        if method == "savgol":
            x_smooth = savgol_filter(x, window_length=window_length, polyorder=polyorder, mode='nearest')
            y_smooth = savgol_filter(y, window_length=window_length, polyorder=polyorder, mode='nearest')
        elif method == "gaussian":
            x_smooth = gaussian_filter1d(x, sigma=sigma)
            y_smooth = gaussian_filter1d(y, sigma=sigma)
        else:
            x_smooth, y_smooth = x, y  # No smoothing
        
        smoothed_contours.append(np.column_stack((x_smooth, y_smooth)))
    
    return smoothed_contours



def actors_from_contours(contours_by_slice, pixel_spacing, line_width=2, color=(1,0,0)):
    """
    Convert {sliceIdx: [np.ndarray, …]} → {sliceIdx: vtkActor}
    Returned dict is ready to be cached under entry['VTKActors2D'].
    """
    actors = {}
    for slice_idx, contours in contours_by_slice.items():
        poly = contours_to_vtk_polydata(contours, pixel_spacing)
        actors[slice_idx] = create_actor_2d(poly, color=color, line_width=line_width)
    return actors

def contours_to_vtk_polydata(contours, pixel_spacing):
    """
    Convert list of numpy contours to vtkPolyData for VTK visualization.
    Applies pixel spacing and image origin for correct alignment.
    """
    points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()

    point_id = 0

    for contour in contours:
        line = vtk.vtkPolyLine()
        num_points = len(contour)
        line.GetPointIds().SetNumberOfIds(num_points)

        for idx, (row, col) in enumerate(contour):
            # Apply pixel spacing and origin shift
            x = col * pixel_spacing[1] 
            y = row * pixel_spacing[0] 

            points.InsertNextPoint(x, y, 0)  # Keep z = 0 for 2D display
            line.GetPointIds().SetId(idx, point_id)
            point_id += 1

        lines.InsertNextCell(line)

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetLines(lines)

    return polydata

def create_actor_2d(polydata, color=(1, 0, 0), line_width=2):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetLineWidth(line_width)
    actor.GetProperty().SetRepresentationToWireframe()
    actor.GetProperty().SetOpacity(1.0)
    
    return actor
