from fcn_3Dview.volume_3d_viewer import VTK3DViewerMixin,initialize_3Dsliders, initialize_crop_widgets
import numpy as np
import vtkmodules.all as vtk
from vtkmodules.util.numpy_support import numpy_to_vtk, get_vtk_array_type

def set_3DViewer_data(self, hierarchy,hierarchy_indices):
    modality  = hierarchy[3].replace("Modality: ", "")     
    idx       = self.layer_selection_box.currentIndex()
    #
    if modality == 'RTSTRUCT':
        # keep track of the last selected struct file ... if user chose and image or dose this will not change
                        # keep track of the last selected struct file ... if user chose and image or dose this will not change
        self.patientID_struct     = hierarchy[1].replace("PatientID: ", "")
        self.studyID_struct       = hierarchy[2].replace("StudyID: ", "")
        self.modality_struct      = hierarchy[3].replace("Modality: ", "")
        self.series_index_struct  = self.series_index
        # 
        index = hierarchy_indices[6].row()
        # print(index)
        name = self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['structures_names'][index]
        # print(self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['structures_keys'][index])
        key  = self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['structures_keys'][index]
        Points3D = create_3d_points(self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['structures'][key])
        if Points3D is not None and Points3D.size > 0:
            Points3D = Points3D.reshape(-1, 3)
            VTK3DViewerMixin.add_3d_point_cloud(self,points=Points3D, name=name)



    if len(hierarchy) == 7: # binary mask contour or density map
        if hierarchy[5]=='Structures' and modality != 'RTSTRUCT':
            index = hierarchy_indices[6].row()
            name = self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['structures_names'][index]
            s_key = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures_keys'][hierarchy_indices[6].row()]
            mask3d = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures'][s_key]['Mask3D']
            surface_polydata = mask3d_to_surface(mask3d, spacing=(1,1,1))
            if surface_polydata.GetNumberOfPoints() > 0:
                print(f"Adding surface for structure: {name} with {surface_polydata.GetNumberOfPoints()} points")
                self.add_surface_actor(surface_polydata, color=(0,1,0), opacity=0.4, name=name)
            return
            # self.display_3D_data[idx] = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures'][s_key]['Mask3D']
            
    else:
        self.display_3D_data[idx]           = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix']

    self.pixel_spacing3Dview[idx]       = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['PixelSpacing']
    self.slice_thickness3Dview[idx]     = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['SliceThickness']
    #
    self.Im_PatPosition3Dview[idx, :3]  = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['ImagePositionPatient']
    #
    if idx == 0:
        offset = (0.0, 0.0, 0.0)
    else:
        base_pos = self.Im_PatPosition3Dview[0]
        curr_pos = self.Im_PatPosition3Dview[idx]
        offset   = tuple(np.array(curr_pos) - np.array(base_pos))
        self.Im_Offset3Dview[idx] = offset

    # load into VTK and display
    self.display_numpy_volume(
        self.display_3D_data[idx],
        voxel_spacing=(
            self.pixel_spacing3Dview[idx,0],
            self.pixel_spacing3Dview[idx,1],
            self.slice_thickness3Dview[idx]
        ),
        layer_idx=idx,
        offset=offset
    )

    # ── reset thresholds (and full‐range) for this layer so the sliders jump to the new data
    # clear any old state
    self._thresholds.pop(idx, None)
    self._full_ranges.pop(idx, None)
    # compute new data range
    vol = self.display_3D_data[idx]
    vmin, vmax = float(vol.min()), float(vol.max())
    # re-initialize the two 3D sliders for this layer
    initialize_3Dsliders(self, vmin, vmax)
    # ── now reset the crop‐region sliders for just this layer
    # clear any old crop state
    self._crops.pop(idx, None)
    self._dims .pop(idx, None)
    # volume_np.shape is (Z, Y, X), but initialize_crop_widgets wants (X, Y, Z)
    dz, dy, dx = vol.shape
    initialize_crop_widgets(self, (dx, dy, dz), idx)
    # stop exectution here
    return



def create_3d_points(structure):
    contour_seq = getattr(structure, 'ContourSequence', [])
    points = []
    if not contour_seq:
        print("No contour sequence found in structure.")
        return np.empty((0, 3))  # Always return a (0,3) array if empty

    for contour in contour_seq:
        geom_type = getattr(contour, 'ContourGeometricType', '').upper()
        if geom_type != 'CLOSED_PLANAR':
            continue

        contour_data = getattr(contour, 'ContourData', [])
        if len(contour_data) % 3 != 0:
            continue

        arr = np.array(contour_data, dtype=float).reshape(-1, 3)
        points.append(arr)

    if points:
        all_points = np.vstack(points)
    else:
        all_points = np.empty((0, 3))  # No points found

    return all_points



def mask3d_to_surface(mask3d, spacing=(1,1,1)):
    arr = numpy_to_vtk(mask3d.astype(np.uint8).ravel(), deep=True)
    img = vtk.vtkImageData()
    img.SetDimensions(mask3d.shape[::-1])  # (X, Y, Z)
    img.SetSpacing(*spacing)
    img.GetPointData().SetScalars(arr)
    mc = vtk.vtkMarchingCubes()
    mc.SetInputData(img)
    mc.SetValue(0, 0.5)
    mc.Update()
    return mc.GetOutput()
