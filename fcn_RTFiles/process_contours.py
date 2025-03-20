import numpy as np
import vtk
from skimage.draw import polygon
from skimage.measure import find_contours
from fcn_load.populate_dcm_list import populate_DICOM_tree


def create_contour_masks(self):
    data_dict = self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]
    target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]

    volume_3d = target_series_dict.get('3DMatrix', None)
    if volume_3d is None:
        print("No 3DMatrix found for this series.")
        return

    if 'structures' not in target_series_dict:
        target_series_dict['structures'] = {}

    mask_shape = volume_3d.shape
    z_spacing = self.slice_thick[0]
    y_spacing, x_spacing = self.pixel_spac[0, :2]
    origin_x, origin_y, origin_z = self.Im_PatPosition[0, :3]

    spacing = (z_spacing, y_spacing, x_spacing)
    origin  = (origin_x, origin_y, origin_z)

    structures_keys  = data_dict.get('structures_keys', [])
    structures_dict  = data_dict.get('structures', {})
    structures_names = data_dict.get('structures_names', [])

    struc_names, struc_keys = [], []

    for idx, s_key in enumerate(structures_keys):
        structure = structures_dict.get(s_key)
        if not structure:
            continue

        mask_3d = create_3d_mask_for_structure_simple(self, structure, mask_shape, spacing, origin)
        name = structures_names[idx] if idx < len(structures_names) else s_key

        struc_names.append(name)
        struc_keys.append(s_key)

        target_series_dict['structures'].setdefault(s_key, {})
        target_series_dict['structures'][s_key]['Mask3D'] = mask_3d
        target_series_dict['structures'][s_key]['Name']   = name

        vtk_actors_2d = {'axial': {}, 'sagittal': {}, 'coronal': {}}

        # Axial
        for z_idx in range(mask_shape[0]):
            slice_2d = mask_3d[z_idx, :, :]

            contours = extract_contours_from_binary_slice(slice_2d)

            print(f"Slice {z_idx}: {len(contours)} contours found")  # Clearly print the count

            if contours:
                vtk_poly = contours_to_vtk_polydata(contours)
                actor = create_actor_2d(vtk_poly)

                # Retrieve the renderer clearly:
                renderer = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()
                renderer.AddActor(actor)

                # Optional: store actor to manage it later:
                self.structure_actors_ax.append(actor)
            else:
                print(f"No contours on slice {z_idx}")  # Clearly print the absence of contours
        # for z_idx in range(mask_shape[0]):
        #     slice_2d = mask_3d[z_idx, :, :]
        #     vtk_poly = vtk_contour_from_slice(slice_2d, (x_spacing, y_spacing), (origin_x, origin_y, origin_z + z_idx*z_spacing))
        #     if vtk_poly:
        #         vtk_actors_2d['axial'][z_idx] = create_actor_2d(vtk_poly)

        # # Sagittal
        # for x_idx in range(mask_shape[2]):
        #     slice_2d = mask_3d[:, :, x_idx]
        #     vtk_poly = vtk_contour_from_slice(slice_2d, (y_spacing, z_spacing), (origin_y, origin_z, origin_x + x_idx*x_spacing))
        #     if vtk_poly:
        #         vtk_actors_2d['sagittal'][x_idx] = create_actor_2d(vtk_poly)

        # # Coronal
        # for y_idx in range(mask_shape[1]):
        #     slice_2d = mask_3d[:, y_idx, :]
        #     vtk_poly = vtk_contour_from_slice(slice_2d, (x_spacing, z_spacing), (origin_x, origin_z, origin_y + y_idx*y_spacing))
        #     if vtk_poly:
        #         vtk_actors_2d['coronal'][y_idx] = create_actor_2d(vtk_poly)

        target_series_dict['structures'][s_key]['VTKActors2D'] = vtk_actors_2d

    target_series_dict['structures_keys'] = struc_keys
    target_series_dict['structures_names'] = struc_names
    populate_DICOM_tree(self)



def create_3d_mask_for_structure_simple(self, structure, mask_shape, spacing, origin):
    mask_3d     = np.zeros(mask_shape, dtype=np.uint8)
    contour_seq = getattr(structure, 'ContourSequence', [])

    if not contour_seq:
        print("No contour sequence found in structure.")
        return mask_3d

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

        # Need to flip y to match
        points[:, 1] = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - points[:, 1]  # Y coordinate

        indices_float = (points - np.array([origin_x, origin_y, origin_z])) / [x_spacing, y_spacing, z_spacing]
        indices = indices_float.round().astype(int)

        slice_idx = indices[0, 2]
        if slice_idx < 0 or slice_idx >= mask_shape[0]:
            continue

        x_coords = indices[:, 0]
        y_coords = indices[:, 1]

        rr, cc = polygon(y_coords, x_coords, shape=mask_shape[1:])
        mask_3d[slice_idx, rr, cc] += 1

    mask_3d = np.mod(mask_3d, 2).astype(np.uint8)
    return mask_3d




def extract_contours_from_binary_slice(slice_2d, level=0.5):
    contours = find_contours(slice_2d, level=level)
    return contours

def contours_to_vtk_polydata(contours):
    """
    Convert list of numpy contours to vtkPolyData for VTK visualization.
    """
    points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()

    point_id = 0

    for contour in contours:
        line = vtk.vtkPolyLine()
        num_points = len(contour)
        line.GetPointIds().SetNumberOfIds(num_points)

        for idx, (row, col) in enumerate(contour):
            # Insert points (note: x corresponds to column, y corresponds to row)
            points.InsertNextPoint(col, row, 0)
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
