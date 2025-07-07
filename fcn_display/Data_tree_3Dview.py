from fcn_3Dview.volume_3d_viewer import VTK3DViewerMixin,initialize_3Dsliders, initialize_crop_widgets
import numpy as np
import vtkmodules.all as vtk
from vtkmodules.util.numpy_support import numpy_to_vtk, get_vtk_array_type
from fcn_3Dview.structures_3D_table import add_cloud_to_table
from skimage.measure import find_contours
import math

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
        name = self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['structures_names'][index]
        key  = self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['structures_keys'][index]
        Points3D = create_3d_points(self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['structures'][key])
        if Points3D is not None and Points3D.size > 0:
            Points3D = Points3D.reshape(-1, 3)
            if Points3D.shape[1] == 3:
                # Subtract position from all rows
                Points3D = Points3D - self.Im_PatPosition3Dview[0, :3]
                cloud_name = self.add_3d_point_cloud(points=Points3D, name=name)
                add_cloud_to_table(self, name=cloud_name, color=(1,0,0), size=4,transparency=1.0)
        return


    if len(hierarchy) == 7: # binary mask contour linked to an image
        if hierarchy[5]=='Structures' and modality != 'RTSTRUCT':
            index = hierarchy_indices[6].row()
            name = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures_names'][index]
            s_key = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures_keys'][index]

            struct_entry = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures'][s_key]

            # Check if Contours3D already exists           
            if 'Contours3D' in struct_entry:
                Points3D = struct_entry['Contours3D']
            else:
                # Need to generate Contours3D from Mask3D
                mask = struct_entry['Mask3D']

                # DICOM spatial information
                spacing = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['PixelSpacing']  # [row, col] (y, x)
                slice_thickness = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['SliceThickness']
                origin = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['ImagePositionPatient']  # [x, y, z] or [z, y, x] (should be DICOM order, check yours!)

                # Convert to full spacing (z, y, x)
                spacing_full = (slice_thickness, spacing[0], spacing[1])
                origin = np.array(origin)

                # Prepare to collect all 3D contour points
                all_pts = []
                n_slices = mask.shape[0]
                last_progress = -1  # To ensure first update is called
                for z in range(mask.shape[0]):
                    # Flip the mask in Y before extracting contours
                    flipped_slice = np.flipud(mask[z, :, :])
                    contours2d = find_contours(flipped_slice, level=0.5)
                    for contour in contours2d:
                        rows, cols = contour[:, 0], contour[:, 1]
                        xs = origin[0] + cols * spacing_full[2]
                        ys = origin[1] + rows * spacing_full[1]
                        zs = np.full_like(cols, origin[2] + z * spacing_full[0], dtype=float)
                        pts = np.stack([xs, ys, zs], axis=1)  # N x 3
                        all_pts.append(pts)     
                    # --- Progress update every 5% ---
                    progress = int(((z + 1) / n_slices) * 100)
                    if progress % 5 == 0 and progress != last_progress:
                        self.progressBar.setValue(progress)
                        last_progress = progress

                if all_pts:
                    Points3D = np.vstack(all_pts)  # [N,3]
                else:
                    Points3D = np.zeros((0,3), dtype=float)
                # Save to the structure
                struct_entry['Contours3D'] = Points3D

            if Points3D is not None and Points3D.size > 0:
                Points3D = Points3D.reshape(-1, 3)
                if Points3D.shape[1] == 3:
                    # Subtract position from all rows
                    Points3D = Points3D - self.Im_PatPosition3Dview[0, :3]
                    cloud_name = self.add_3d_point_cloud(points=Points3D, name=name)
                    add_cloud_to_table(self, name=cloud_name, color=(1,0,0), size=4,transparency=1.0)
            return            
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

