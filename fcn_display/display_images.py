from PySide6.QtWidgets import QProgressDialog, QMessageBox
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
import vtk
import numpy as np
import math
from fcn_RTFiles.process_contours import build_contours_for_structure, actors_from_contours
from fcn_processing.mc_grid import update_mc_grid_axial, update_mc_grid_coronal, update_mc_grid_sagittal
from fcn_materialassignment.mat_overlay import update_mat_overlay_axial, update_mat_overlay_coronal, update_mat_overlay_sagittal
from vtkmodules.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
from fcn_display.brachy_channel_edit import (brachy_highlight, dwell_directions, view_dir, dwell_glyph_size, dwell_outline,
                                             channel_visible, ref_point_visible, ref_point_xyz, ref_point_name, view_xy,
                                             selected_catheter, catheter_label, NORMAL_AXIS, VIEW_SUFFIX, VIEW_WIDGETS,
                                             _slice_point)
from fcn_display.brachy_panel import brachy_style, brachy_display, catheter_colors

# Catheter numbers / reference point names: offset (px) from their point
LABEL_OFFSET_PX = 6


def displayaxial(self, Im = None):
    # ------------------------------------------------------------------
    if (not hasattr(self, "display_data") or
        self.display_data is None or
        len(self.display_data) == 0):
        return   
    idx = self.layer_selected.currentIndex()

    if idx not in self.display_data:
        QMessageBox.warning(None, "Warning", "No image data was found.")
        return
    #
    for i in range(len(self.dataImporterAxial)):

        # Add or update circular ROIs in the 4th layer
        if i == 3:
            renderer = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()
            if self.checkBox_circ_roi_data_2.isChecked():
                for actor in self.circle_actors_ax:
                    renderer.RemoveActor(actor)
                self.circle_actors_ax.clear()
                # self.vtkWidgetAxial.GetRenderWindow().Render() 
                disp_roi_axial(self)

            update_mc_grid_axial(self)
            update_mat_overlay_axial(self)

            # Dose reference points and dwells, as set under View > PLAN > Brachy > Display
            show_ref_points = getattr(self, 'brachy_show_ref_points', None)
            if show_ref_points is not None and show_ref_points.isChecked():
                display_ref_points_ax(self)
            else:
                if hasattr(self, 'ref_point_actors_ax'):
                    for actor in self.ref_point_actors_ax:
                        renderer.RemoveActor(actor)
                    self.ref_point_actors_ax.clear()
            
            if self.display_dw_overlay.isChecked():
                display_dwell_positions_ax(self)
            else:
                for actor in self.dwell_actors_ax:
                    renderer.RemoveActor(actor)
                self.dwell_actors_ax.clear()

            # EBRT Fields overlay
            if hasattr(self, 'display_ebrt_fields_overlay') and self.display_ebrt_fields_overlay.isChecked():
                display_ebrt_fields_ax(self)
            else:
                if hasattr(self, 'ebrt_actors_ax'):
                    for actor in self.ebrt_actors_ax:
                        renderer.RemoveActor(actor)
                    self.ebrt_actors_ax.clear()
        if i == 3 and  self.display_brachy_channel_overlay.isChecked():
            # Check if the required fields exist in medical_image
                display_brachy_channel_overlay_ax(self)
        if i == 3 and self.DataType in ("DICOM", "Nifti"):
            # Check if the required fields exist in medical_image
                # First, clear previous overlays explicitly
                _update_axial_mask_overlay(self)
                disp_structure_overlay_axial(self)
                

  
        if self.slice_thick[i] == 0:
            self.imageActorAxial[i].SetVisibility(0)
            continue
        
        
        Offset_vox = (self.Im_PatPosition[idx,2]-self.Im_PatPosition[i,2])/self.slice_thick[i]
        self.current_axial_slice_index[i] = int(np.round((self.current_axial_slice_index[idx]*(self.slice_thick[idx]/self.slice_thick[i]))+Offset_vox))
        #
        if 0 <=self.current_axial_slice_index[i] <self.display_data[i].shape[0]:
            if self.display_data[i].ndim==2:
                slice_data = self.display_data[i]
            elif Im is not None:
                slice_data = Im
            else:       
                slice_data = self.display_data[i][self.current_axial_slice_index[i], :, :]
            data_string = slice_data.tobytes()
            #
            self.dataImporterAxial[i].SetDataSpacing(self.pixel_spac[i,1],self.pixel_spac[i,0],1)
            #
            extent = slice_data.shape
            self.dataImporterAxial[i].CopyImportVoidPointer(data_string, len(data_string))
            self.dataImporterAxial[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            self.dataImporterAxial[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            #
            self.imageActorAxial[i].SetPosition(self.Im_Offset[i,0], self.Im_Offset[i,1] , 0)
            #
            #
            imageProperty = self.imageActorAxial[i].GetProperty()
            imageProperty.SetOpacity(self.LayerAlpha[i])  
            self.imageActorAxial[i].SetVisibility(1)
            self.dataImporterAxial[i].Modified()  
            if i == idx:
                # Update the position and lateral extension of the axial line to cross the entire image
                self.sagittalLine2Source.SetPoint1(self.Im_Offset[i,1],self.Im_Offset[i,2]+self.current_axial_slice_index[i]*self.slice_thick[i], 0.05)
                self.sagittalLine2Source.SetPoint2(self.Im_Offset[i,1]+extent[0]*self.pixel_spac[i,0]-self.pixel_spac[i,0],self.Im_Offset[i,2]+self.current_axial_slice_index[i]*self.slice_thick[i], 0.05)
                self.sagittalLine2Source.Modified()  # Notify VTK of the changes
                #
                # Update the position and lateral extension of the axial line to cross the entire image
                self.coronalLine2Source.SetPoint1(self.Im_Offset[i,0],self.Im_Offset[i,2]+self.current_axial_slice_index[i]*self.slice_thick[i], 0.05)
                self.coronalLine2Source.SetPoint2(self.Im_Offset[i,0]+extent[1]*self.pixel_spac[i,1]-self.pixel_spac[i,1],self.Im_Offset[i,2]+self.current_axial_slice_index[i]*self.slice_thick[i], 0.05)
                self.coronalLine2Source.Modified()  # Notify VTK of the changes
                self.current_axial_slice_index[i]  
                      
        else:             
            imageProperty = self.imageActorAxial[i].GetProperty()
            imageProperty.SetOpacity(0)
            self.imageActorAxial[i].SetVisibility(0)
            self.dataImporterAxial[i].Modified()
        #     
        #  Render to update
        self.vtkWidgetAxial.GetRenderWindow().Render()
        self.vtkWidgetSagittal.GetRenderWindow().Render()
        self.vtkWidgetCoronal.GetRenderWindow().Render()
        self.sliceChanged.emit("axial", self.current_axial_slice_index)


def disp_structure_overlay_axial(self):
    """
    Show selected structures (structures_view==1) on the axial renderer.
    Uses saved per-structure appearance:
      - structures_color        -> hex "#rrggbb"
      - structures_line_width   -> float
      - structures_transparency -> float in [0,1]
    """
    renderer = (
        self.vtkWidgetAxial.GetRenderWindow()
        .GetRenderers()
        .GetFirstRenderer()
    )

    # ─── clear any actors from the previous draw ──────────────────────
    for actor in getattr(self, "structure_actors_ax", []):
        renderer.RemoveActor(actor)
    self.structure_actors_ax = []

    # ─── grab data for the currently displayed image series ───────────
    series_dict = (
        self.medical_image[self.patientID][self.studyID]
                       [self.modality][self.series_index]
    )
    if not series_dict.get("structures"):
        return  # nothing to draw yet

    slice_idx = self.current_axial_slice_index[0]  # current Z

    # pixel spacing (row, col) → (y, x) in mm
    px_spacing = (self.pixel_spac[0, 1], self.pixel_spac[0, 0])

    names = series_dict.get('structures_names', [])
    keys  = series_dict.get('structures_keys', [])
    view  = series_dict.get('structures_view', [0]*len(names))

    # keep arrays aligned; avoid IndexError
    n = min(len(view), len(keys), len(names))

    # Saved appearance with safe defaults
    def _align(arr, default):
        arr = arr if isinstance(arr, list) else []
        if len(arr) < n:
            arr = arr + [default] * (n - len(arr))
        else:
            arr = arr[:n]
        return arr

    colors_hex   = _align(series_dict.get('structures_color'),        "#ffffff")
    line_widths  = _align(series_dict.get('structures_line_width'),   2.0)
    transpars    = _align(series_dict.get('structures_transparency'), 0.1)

    def _hex_to_rgbf(h):
        try:
            s = (h or "").strip()
            if s.startswith("#"):
                s = s[1:]
            if len(s) == 3:  # e.g. "abc" → "aabbcc"
                s = "".join(c*2 for c in s)
            r = int(s[0:2], 16) / 255.0
            g = int(s[2:4], 16) / 255.0
            b = int(s[4:6], 16) / 255.0
            return (r, g, b)
        except Exception:
            return (1.0, 1.0, 1.0)



    # ─── main loop over selected structures ───────────────────────────
    for i in range(n):
        if view[i] != 1:
            continue

        s_key = keys[i]
        if not s_key:
            continue

        s_data = series_dict.get("structures", {}).get(s_key, {})
        if not s_data:
            continue


        # Ensure contour containers exist
        if 'Contours2D' not in s_data or not isinstance(s_data['Contours2D'], dict):
            s_data['Contours2D'] = {'axial': {}, 'sagittal': {}, 'coronal': {}}

        # First-time creation of actors dict
        if "VTKActors2D" not in s_data:
            s_data["VTKActors2D"] = {}

        # Build contours if missing or marked modified
        if not s_data['Contours2D'].get('axial') or s_data.get('Modified', 0) == 1:
            s_data['Contours2D'] = build_contours_for_structure(s_data['Mask3D'])

        # Rebuild actors (axial) if missing or modified
        if "axial" not in s_data["VTKActors2D"] or s_data.get('Modified', 0) == 1:
            contours_axial = s_data.get("Contours2D", {}).get("axial", {})
            s_data["VTKActors2D"]["axial"] = actors_from_contours(
                contours_axial,
                px_spacing,
                line_width=float(line_widths[i]),
                color=_hex_to_rgbf(colors_hex[i]),
            )

        if s_data.get('Modified', 0) == 1:
            s_data['Modified'] = 0  # reset modified flag

        actors_dict = s_data["VTKActors2D"]["axial"]
        if slice_idx not in actors_dict:
            continue  # no contour on this slice

        src_actor = actors_dict[slice_idx]

        # ── customise appearance from saved arrays ────────────────────
        actor = vtk.vtkActor()
        actor.ShallowCopy(src_actor)
        actor.GetProperty().SetColor(_hex_to_rgbf(colors_hex[i]))
        actor.GetProperty().SetOpacity(1.0 - float(transpars[i]))       # 0→opaque,1→transparent in UI
        actor.GetProperty().SetLineWidth(float(line_widths[i]))
        actor.GetProperty().SetRepresentationToWireframe()

        # Lift above the image plane so contours are visible
        actor.SetPosition(self.Im_Offset[0, 0],
                          self.Im_Offset[0, 1],
                          _overlay_epsilon(self))

        renderer.AddActor(actor)
        self.structure_actors_ax.append(actor)



    renderer.ResetCameraClippingRange()
    self.vtkWidgetAxial.GetRenderWindow().Render()

def _overlay_epsilon(self):
    # small positive offset (mm) so wireframe floats above the slice
    try:
        st = float(self.slice_thick[0]) if self.slice_thick is not None else 1.0
    except Exception:
        st = 1.0
    return max(0.1, 0.05 * (st if st > 0 else 1.0))


def _ensure_axial_mask_overlay(self):
    if hasattr(self, "maskOverlayImporterAxial"):
        return

    self.maskOverlayImporterAxial = vtk.vtkImageImport()
    self.maskOverlayImporterAxial.SetDataScalarTypeToUnsignedChar()
    self.maskOverlayImporterAxial.SetNumberOfScalarComponents(4)  # RGBA

    # 🔧 CRITICAL: match base axial spacing (x = col, y = row)
    self.maskOverlayImporterAxial.SetDataSpacing(self.pixel_spac[0,1], self.pixel_spac[0,0], 1.0)
    self.maskOverlayImporterAxial.SetDataOrigin(0.0, 0.0, 0.0)

    self.maskOverlayActorAxial = vtk.vtkImageActor()
    self.maskOverlayActorAxial.GetMapper().SetInputConnection(
        self.maskOverlayImporterAxial.GetOutputPort()
    )
    self.maskOverlayActorAxial.InterpolateOff()
    self.maskOverlayActorAxial.SetPickable(False)

    # Position is handled in _update_axial_mask_overlay each frame
    renderer = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()
    renderer.AddActor(self.maskOverlayActorAxial)

def _to_rgbf(color):
    """(r,g,b) in [0,1] from '#hex', '#rgb', QColor, or tuple/list."""
    if isinstance(color, QColor):
        r, g, b, _ = color.getRgbF()
        return r, g, b
    if isinstance(color, (tuple, list)) and len(color) >= 3:
        r, g, b = color[:3]
        if max(r, g, b) > 1.0:  # 0-255 input
            return float(r)/255.0, float(g)/255.0, float(b)/255.0
        return float(r), float(g), float(b)
    if isinstance(color, str):
        s = color.strip()
        if s.startswith("#"):
            s = s[1:]
        if len(s) == 3:
            s = "".join(c*2 for c in s)
        try:
            return int(s[0:2],16)/255.0, int(s[2:4],16)/255.0, int(s[4:6],16)/255.0
        except Exception:
            pass
    return 1.0, 0.0, 0.0

def _build_axial_mask_rgba(self):
    # base geometry from layer 0 axial slice
    z = int(self.current_axial_slice_index[0])
    if (not hasattr(self, "display_data") or
        self.display_data is None or
        len(self.display_data) == 0 or
        self.display_data[0].ndim < 2):
        return None

    if self.display_data[0].ndim == 2:
        h, w = self.display_data[0].shape
    else:
        h, w = self.display_data[0].shape[1], self.display_data[0].shape[2]

    rgba = np.zeros((h, w, 4), dtype=np.uint8)

    series = self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]
    if not series.get("structures"):
        return rgba

    names  = series.get('structures_names', [])
    keys   = series.get('structures_keys', [])
    view   = series.get('structures_view', [0]*len(names))
    colors = series.get('structures_color', ["#ff0000"]*len(names))
    widths = series.get('structures_line_width', [2.0]*len(names))      # not used here
    trans  = series.get('structures_transparency', [0.1]*len(names))    # 0→opaque, 1→transparent
    mtr    = series.get('structures_mask_transparency', [1.0]*len(names))  # NEW

    n = min(len(names), len(keys), len(view), len(colors), len(mtr))
    if n == 0:
        return rgba

    layer_opacity = 1.0  # keep as your global multiplier if needed

    for i in range(n):
        if view[i] != 1:      # ← gate by checkbox
            continue
        s_key = keys[i]
        sdat = series["structures"].get(s_key, {})
        mask3d = sdat.get("Mask3D")
        if mask3d is None or z < 0 or z >= mask3d.shape[0]:
            continue

        # skip if mask transparency is 1.0 (fully hidden)
        mt = float(mtr[i])
        if mt >= 0.999:     # small epsilon to avoid flicker
            continue

        mask2d = mask3d[z, :, :] > 0
        if not np.any(mask2d):
            continue

        # color from the contour color
        r, g, b = _to_rgbf(colors[i])
        a = np.clip(layer_opacity * (1.0 - mt), 0.0, 0.99)

        R = int(r * 255); G = int(g * 255); B = int(b * 255); A = int(a * 255)
        m = mask2d
        rgba[m, 0] = np.maximum(rgba[m, 0], R)
        rgba[m, 1] = np.maximum(rgba[m, 1], G)
        rgba[m, 2] = np.maximum(rgba[m, 2], B)
        rgba[m, 3] = np.maximum(rgba[m, 3], A)

    return rgba

def _update_axial_mask_overlay(self):
    _ensure_axial_mask_overlay(self)
    rgba = _build_axial_mask_rgba(self)
    if rgba is None:
        self.maskOverlayActorAxial.GetProperty().SetOpacity(0.0)
        return

    h, w, _ = rgba.shape
    data = rgba.tobytes()

    imp = self.maskOverlayImporterAxial
    # 🔧 Keep spacing synced in case series/layer changed
    imp.SetDataSpacing(self.pixel_spac[0,1], self.pixel_spac[0,0], 1.0)
    imp.SetDataOrigin(0.0, 0.0, 0.0)

    imp.CopyImportVoidPointer(data, len(data))
    imp.SetWholeExtent(0, w-1, 0, h-1, 0, 0)
    imp.SetDataExtent (0, w-1, 0, h-1, 0, 0)
    imp.SetNumberOfScalarComponents(4)
    imp.SetDataScalarTypeToUnsignedChar()
    imp.Modified()

    # 🔧 EXACTLY match layer-0 image position
    self.maskOverlayActorAxial.SetPosition(
        self.Im_Offset[0, 0],
        self.Im_Offset[0, 1],
        _overlay_epsilon(self) * 0.5
    )
    self.maskOverlayActorAxial.SetOpacity(1.0)

def disp_roi_axial(self):
    for row in range(self.table_circ_roi.rowCount()):
        try:
            item_x       = self.table_circ_roi.item(row, 0)
            item_y       = self.table_circ_roi.item(row, 1)
            item_radius  = self.table_circ_roi.item(row, 2)
            sli_ini      = self.table_circ_roi.item(row, 3)
            sli_fin      = self.table_circ_roi.item(row, 4)
            transparency = self.table_circ_roi.item(row, 5)
            R_item = self.table_circ_roi.item(row, 8) or self.table_circ_roi.item(row, 7) or self.table_circ_roi.item(row, 6)
            G_item = self.table_circ_roi.item(row, 9) or self.table_circ_roi.item(row, 8) or self.table_circ_roi.item(row, 7)
            B_item = self.table_circ_roi.item(row, 10) or self.table_circ_roi.item(row, 9) or self.table_circ_roi.item(row, 8)
            
            if (item_x is None or item_y is None or item_radius is None or sli_ini is None or sli_fin is None or transparency is None):
                continue

            sli_ini_val = float(sli_ini.text())
            sli_fin_val = float(sli_fin.text())
            center_x_pixel = float(item_x.text())
            center_y_pixel = float(item_y.text())
            radius = float(item_radius.text())
            transparency_val = float(transparency.text())
            R = float(R_item.text()) if R_item is not None else 1.0
            G = float(G_item.text()) if G_item is not None else 0.0
            B = float(B_item.text()) if B_item is not None else 0.0

            dir_widget = self.table_circ_roi.cellWidget(row, 7)
            if dir_widget is not None and hasattr(dir_widget, 'currentText'):
                row_dir = dir_widget.currentText()
            else:
                row_dir = item_x.data(Qt.UserRole + 1) if item_x is not None else "Axial"
            if not row_dir:
                row_dir = "Axial"

            curr_ax = self.current_axial_slice_index[0]

            if row_dir == "Axial":
                if curr_ax < sli_ini_val or curr_ax > sli_fin_val:
                    if row < len(self.circle_actors_ax):
                        renderer = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()
                        actor_to_remove = self.circle_actors_ax.pop(row)
                        renderer.RemoveActor(actor_to_remove)
                        self.vtkWidgetAxial.GetRenderWindow().Render()
                    continue

                center_x = center_x_pixel * self.pixel_spac[0, 0]
                center_y = center_y_pixel * self.pixel_spac[0, 1]
                radius_phys = radius * self.pixel_spac[0, 0]

                circle_source = vtk.vtkRegularPolygonSource()
                circle_source.SetNumberOfSides(50)
                circle_source.SetRadius(radius_phys)
                circle_source.SetCenter(center_x, center_y, 0)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(circle_source.GetOutputPort())

                if row < len(self.circle_actors_ax):
                    circle_actor = self.circle_actors_ax[row]
                    circle_actor.SetMapper(mapper)
                    circle_actor.GetProperty().SetColor(R, G, B)
                    circle_actor.GetProperty().SetOpacity(1 - transparency_val)
                else:
                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(R, G, B)
                    actor.GetProperty().SetLineWidth(2)
                    actor.GetProperty().SetOpacity(1 - transparency_val)
                    actor.SetPosition(0, 0, 1)
                    self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(actor)
                    self.circle_actors_ax.append(actor)
            else:
                if curr_ax < (center_y_pixel - radius) or curr_ax > (center_y_pixel + radius):
                    if row < len(self.circle_actors_ax):
                        renderer = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()
                        actor_to_remove = self.circle_actors_ax.pop(row)
                        renderer.RemoveActor(actor_to_remove)
                        self.vtkWidgetAxial.GetRenderWindow().Render()
                    continue

                dist = abs(curr_ax - center_y_pixel)
                width = 2 * math.sqrt(max(0, radius**2 - dist**2)) * self.pixel_spac[0, 0]
                height = (sli_fin_val - sli_ini_val + 1) * self.pixel_spac[0, 1]

                cube_source = vtk.vtkCubeSource()
                if row_dir == "Coronal":
                    cube_source.SetXLength(width)
                    cube_source.SetYLength(height)
                    cx_phys = center_x_pixel * self.pixel_spac[0, 0]
                    cy_phys = (sli_ini_val + sli_fin_val) / 2 * self.pixel_spac[0, 1]
                else:
                    cube_source.SetXLength(height)
                    cube_source.SetYLength(width)
                    cx_phys = (sli_ini_val + sli_fin_val) / 2 * self.pixel_spac[0, 0]
                    cy_phys = center_x_pixel * self.pixel_spac[0, 1]
                cube_source.SetZLength(1)
                cube_source.SetCenter(cx_phys, cy_phys, 0)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(cube_source.GetOutputPort())

                if row < len(self.circle_actors_ax):
                    rect_actor = self.circle_actors_ax[row]
                    rect_actor.SetMapper(mapper)
                    rect_actor.GetProperty().SetColor(R, G, B)
                    rect_actor.GetProperty().SetOpacity(1 - transparency_val)
                else:
                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(R, G, B)
                    actor.GetProperty().SetOpacity(1 - transparency_val)
                    actor.SetPosition(0, 0, 1)
                    self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(actor)
                    self.circle_actors_ax.append(actor)
        except Exception as e:
            print(f"Skipping row {row} in disp_roi_axial due to error: {e}")
            continue
            print(f'Skipping row {row} due to invalid data')
            continue  

def _dwell_glyph_actors(xy, dirs, sizes, colors, z_floor, style):
    """
    Actors for the dwell positions of one view. Each dwell is the outline of a cylinder
    along its source direction as seen in the image plane, with an almost transparent
    fill and a solid edge in the dwell color, just above z_floor.

    :param xy: (M, 2) dwell positions in the view
    :param dirs: (M, 3) source directions in view coordinates (z out of the plane)
    :param sizes: (M, 2) cylinder length and radius (mm)
    :param colors: (M, 3) RGB colors in 0-1
    """
    outline = dwell_outline(xy, dirs, sizes[:, 0], sizes[:, 1])
    m, k = outline.shape[:2]
    ids = np.arange(m * k, dtype=np.int64).reshape(m, k)
    rgb = numpy_to_vtk(np.round(np.clip(colors, 0.0, 1.0) * 255).astype(np.uint8), deep=True)

    def flat_actor(z, cells, lines, opacity):
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(np.column_stack((outline.reshape(-1, 2), np.full(m * k, z))), deep=True))
        cell_array = vtk.vtkCellArray()
        cell_array.SetData(numpy_to_vtkIdTypeArray(np.arange(0, cells.size + 1, cells.shape[1], dtype=np.int64), deep=True),
                           numpy_to_vtkIdTypeArray(cells.ravel(), deep=True))
        poly = vtk.vtkPolyData()
        poly.SetPoints(points)
        if lines:
            poly.SetLines(cell_array)
        else:
            poly.SetPolys(cell_array)
        poly.GetCellData().SetScalars(rgb)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly)
        mapper.SetScalarModeToUseCellData()
        mapper.SetColorModeToDirectScalars()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(opacity)
        actor.GetProperty().SetLineWidth(style['dw_edge_width'])
        actor.GetProperty().SetAmbient(1.0)  # flat colors, no shading
        actor.GetProperty().SetDiffuse(0.0)
        return actor

    actors = []
    if style['dw_fill'] > 0:
        actors.append(flat_actor(z_floor + 0.05, ids, False, style['dw_fill'] / 100.0))
    # Closed outline, opaque: depth-tested against the translucent catheter points
    # (drawn lower) instead of being blended under them
    actors.append(flat_actor(z_floor + 0.1, np.column_stack((ids, ids[:, 0])), True, 1.0))
    return actors


def display_dwell_positions_ax(self):
    """
    Display the dwell positions on top of the DICOM images using VTK.
    - Each dwell is the outline of a cylinder along the source direction (plan orientation,
      else the channel path), with an almost transparent fill.
    - Dwell positions of the catheters ticked in the catheter list (brachy_tree); those
      with 0 s only when "0 s" is checked under Display.
    - Colors and sizes come from the Style panel (brachy_style); by default:
    - Dwell positions with dwell_time == 0 are shown in red.
    - Dwell positions with dwell_time > 0 are shown in dark green.
    - Dwell positions within Ref_Z ± slice_thickness/2 are shown in light green.
    """

    renderer = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()

    # Remove any previous dwell actors
    for actor in self.dwell_actors_ax:
        renderer.RemoveActor(actor)
    self.dwell_actors_ax.clear()

    try:
        meta = (self.medical_image[self.patientID][self.studyID]          # may raise KeyError
                                [self.modality][self.series_index]
                                ['metadata'])
        channels = meta.get('Plan_Brachy_Channels')
    except KeyError:
        # Data tree incomplete (no metadata at all) ─ silently abort
        return
    
    if not channels:                     # None or empty list
        return                           # nothing to draw
    
    # Catheters ticked in the catheter list; dwells with 0 s only if shown (Display)
    channels_to_display = [ch for ch in channels if channel_visible(ch)]
    show_zero = brachy_display(self)['dw_zero']

    # Dwells are drawn above the catheter points (spheres of diameter = catheter point size)
    style = brachy_style(self)
    z_floor = 0.5 + style['ch_point_size'] / 2

    # Get the current slice reference Z position and tolerance
    Ref_z = self.current_axial_slice_index[0] * self.slice_thick[0] + self.Im_Offset[0, 2]
    z_tolerance = self.slice_thick[0] /2

    # Position, source direction (view coordinates), size and color of every dwell shown
    xy, dirs, sizes, colors = [], [], [], []
    for current_ch in channels_to_display:
        dwell_info = current_ch.get('DwellInfo')

        if dwell_info is None or not isinstance(dwell_info, np.ndarray) or dwell_info.shape[1] < 7:
            continue  # Skip invalid channels

        # Extract dwell positions (X, Y, Z coordinates) and convert them to image space
        dwell_times = dwell_info[:, 2]  # Assuming dwell time is in column 2
        x = dwell_info[:, 3] - self.Im_PatPosition[0, 0]  # X coordinate in mm
        y = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - (dwell_info[:, 4] - self.Im_PatPosition[0, 1])  # Y coordinate
        z = dwell_info[:, 5] - self.Im_PatPosition[0, 2]  # Z coordinate in mm
        keep = show_zero | (dwell_times != 0)
        xy.append(np.column_stack((x, y))[keep])
        dirs.append(view_dir('axial', dwell_directions(dwell_info, current_ch.get('ChPos')))[keep])
        sizes.append(np.tile(dwell_glyph_size(dwell_info[:, 3:6], style['dw_size']), (len(x), 1))[keep])
        # Dwell time 0, Z position within Ref_Z ± slice_thickness/2, or elsewhere
        in_slice = (Ref_z - z_tolerance <= z) & (z <= Ref_z + z_tolerance)
        colors.append(np.where((dwell_times == 0)[:, None], style['dw_zero'],
                               np.where(in_slice[:, None], style['dw_slice'], style['dw_other']))[keep])

    xy = np.vstack(xy) if xy else np.zeros((0, 2))
    if len(xy):
        for dwell_actor in _dwell_glyph_actors(xy, np.vstack(dirs), np.vstack(sizes), np.vstack(colors), z_floor, style):
            renderer.AddActor(dwell_actor)
            self.dwell_actors_ax.append(dwell_actor)

    # Re-render to show the updated scene with dwell positions
    self.vtkWidgetAxial.GetRenderWindow().Render()


def display_brachy_channel_overlay_ax(self):
    """
    Display brachytherapy channels as connected lines with spheres at each channel point
    (colors and sizes from the Style panel: blue by default, the catheter selected in the
    catheter list green, the one being edited yellow).
    - Only the catheters ticked in the catheter list (brachy_tree); their points, path
      and numbers (next to the first point) as set under Display.
    """
    renderer = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()

    # Remove any previous channel actors
    for actor in self.channel_actors_ax:
        renderer.RemoveActor(actor)
    self.channel_actors_ax.clear()

    # Retrieve channels from medical_image
    try:
        meta = (self.medical_image[self.patientID][self.studyID]          # may raise KeyError
                                [self.modality][self.series_index]
                                ['metadata'])
        channels = meta.get('Plan_Brachy_Channels')
    except KeyError:
        # Data tree incomplete (no metadata at all) ─ silently abort
        return

    if not channels:                     # None or empty list
        return                           # nothing to draw

    # Points, path and numbers of the catheters as set under Display
    show = brachy_display(self)

    # Colors and sizes from the Style panel; spheres of diameter = catheter point size
    style = brachy_style(self)
    point_size = style['ch_point_size'] / 2
    # Catheter / point being edited (edit tools) and catheter selected in the list
    edit_ch, edit_pt = brachy_highlight(self, channels)
    sel_ch = selected_catheter(self, channels)

    # Iterate through the catheters ticked in the catheter list, the selected / edited one last (on top)
    for k in sorted(range(len(channels)), key=lambda j: channels[j] is edit_ch or channels[j] is sel_ch):
        current_ch = channels[k]
        if not channel_visible(current_ch):
            continue
        point_color, line_color = catheter_colors(style, current_ch is edit_ch, current_ch is sel_ch)
        ch_points = current_ch.get('ChPos')

        # Check if 'ChPos' exists and contains valid data
        if ch_points is None or not isinstance(ch_points, np.ndarray) or ch_points.shape[1] < 3:
            continue  # Skip invalid channels

        # Extract channel points (X, Y, Z coordinates)
        x = ch_points[:, 0] - self.Im_PatPosition[0, 0]  # X coordinate in mm
        y = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - (ch_points[:, 1] - self.Im_PatPosition[0, 1])  # Y coordinate
        z = ch_points[:, 2] - self.Im_PatPosition[0, 2]  # Z coordinate in mm

        # Create a polyline to represent the connected channel points
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        # Add points and create lines between consecutive points
        for i in range(len(x)):
            points.InsertNextPoint(x[i], y[i], 0.5)  # Insert each point into vtkPoints
            if i > 0:
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0, i - 1)  # Line from previous point to current point
                line.GetPointIds().SetId(1, i)
                lines.InsertNextCell(line)

            if not show['ch_points']:
                continue
            # Create solid blue spheres for each point
            sphere_source = vtk.vtkSphereSource()
            sphere_source.SetCenter(x[i], y[i], 0.5)
            sphere_source.SetRadius(point_size)  # Sphere size is half of the value from the spinbox
            sphere_source.SetPhiResolution(20)
            sphere_source.SetThetaResolution(20)

            # Map the sphere to an actor
            sphere_mapper = vtk.vtkPolyDataMapper()
            sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())

            sphere_actor = vtk.vtkActor()
            sphere_actor.SetMapper(sphere_mapper)

            # Catheter point color (the point being edited in the edit point color)
            if current_ch is edit_ch and i == edit_pt:
                sphere_actor.GetProperty().SetColor(*style['edit_point'])
            else:
                sphere_actor.GetProperty().SetColor(*point_color)
            sphere_actor.GetProperty().SetOpacity(0.7)  # Full opacity

            # Add the actor for the sphere to the renderer
            renderer.AddActor(sphere_actor)
            self.channel_actors_ax.append(sphere_actor)

        # Create the polyline
        polyline = vtk.vtkPolyData()
        polyline.SetPoints(points)
        polyline.SetLines(lines)

        # Map the polyline to an actor
        polyline_mapper = vtk.vtkPolyDataMapper()
        polyline_mapper.SetInputData(polyline)

        polyline_actor = vtk.vtkActor()
        polyline_actor.SetMapper(polyline_mapper)
        polyline_actor.GetProperty().SetColor(*line_color)
        polyline_actor.GetProperty().SetLineWidth(style['ch_line_width'])

        # Add the polyline actor to the renderer (the path, if shown)
        if show['ch_path']:
            renderer.AddActor(polyline_actor)
            self.channel_actors_ax.append(polyline_actor)

        # Catheter name (its number unless renamed) next to its first point (tip)
        if show['ch_labels'] and len(x):
            label = brachy_label_actor(x[0], y[0], 0.5, catheter_label(current_ch, k), line_color, style['label_size'])
            renderer.AddActor(label)
            self.channel_actors_ax.append(label)

    # Render the updated display with the channels
    self.vtkWidgetAxial.GetRenderWindow().Render()


def displaycoronal(self, Im = None):
    # ------------------------------------------------------------------
    if (not hasattr(self, "display_data") or
        self.display_data is None or
        len(self.display_data) == 0):
        return   
    idx = self.layer_selected.currentIndex()

    if idx not in self.display_data:
        QMessageBox.warning(None, "Warning", "No image data was found.")
        return
    if not isinstance(self.display_data[idx], np.ndarray) or self.display_data[idx].ndim==2:
        return
    for i in range(len(self.dataImporterCoronal)):
        # Add or update circular ROIs in the 4th layer
        if i == 3:
            renderer = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()
            if self.checkBox_circ_roi_data_2.isChecked():
                for actor in self.circle_actors_co:
                    renderer.RemoveActor(actor)
                self.circle_actors_co.clear()
                # self.vtkWidgetAxial.GetRenderWindow().Render() 
                disp_roi_coronal(self)

            update_mc_grid_coronal(self)
            update_mat_overlay_coronal(self)

            # Dose reference points and dwells, as set under View > PLAN > Brachy > Display
            show_ref_points = getattr(self, 'brachy_show_ref_points', None)
            if show_ref_points is not None and show_ref_points.isChecked():
                display_ref_points_co(self)
            else:
                if hasattr(self, 'ref_point_actors_co'):
                    for actor in self.ref_point_actors_co:
                        renderer.RemoveActor(actor)
                    self.ref_point_actors_co.clear()
            
            if self.display_dw_overlay.isChecked():
                display_dwell_positions_co(self)
            else:
                for actor in self.dwell_actors_co:
                    renderer.RemoveActor(actor)
                self.dwell_actors_co.clear()

            # EBRT Fields overlay
            if hasattr(self, 'display_ebrt_fields_overlay') and self.display_ebrt_fields_overlay.isChecked():
                display_ebrt_fields_co(self)
            else:
                if hasattr(self, 'ebrt_actors_co'):
                    for actor in self.ebrt_actors_co:
                        renderer.RemoveActor(actor)
                    self.ebrt_actors_co.clear()
        if i == 3 and  self.display_brachy_channel_overlay.isChecked():
            # Check if the required fields exist in medical_image
                display_brachy_channel_overlay_co(self)
        if i == 3 and self.DataType in ("DICOM", "Nifti"):
                _update_coronal_mask_overlay(self)
                disp_structure_overlay_coronal(self)

        if self.slice_thick[i] == 0:
            self.imageActorCoronal[i].SetVisibility(0)
            continue   
        
        
        
        Offset = (self.display_data[idx].shape[1]*self.pixel_spac[idx,0]-self.display_data[i].shape[1]*self.pixel_spac[i,0]-(self.Im_PatPosition[i,1]-self.Im_PatPosition[idx,1]))/self.pixel_spac[i,0]
        self.current_coronal_slice_index[i] = int(np.round((self.current_coronal_slice_index[idx]*(self.pixel_spac[idx,0]/self.pixel_spac[i,0]))-Offset))
        #
        if 0<= self.current_coronal_slice_index[i] <self.display_data[i].shape[1]:
            # Just update the slice data for the existing pipeline
            if Im is not None:
                slice_data = Im
            else:
                slice_data = self.display_data[i][:, self.current_coronal_slice_index[i], :]
            data_string = slice_data.tobytes()
            extent = slice_data.shape
            self.dataImporterCoronal[i].CopyImportVoidPointer(data_string, len(data_string))
            self.dataImporterCoronal[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            self.dataImporterCoronal[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            #
            # 
            self.dataImporterCoronal[i].SetDataSpacing(self.pixel_spac[i,1],self.slice_thick[i],1)     
            # Inform the pipeline that data has changed.
            imageProperty = self.imageActorCoronal[i].GetProperty()
            imageProperty.SetOpacity(self.LayerAlpha[i])  
            self.imageActorCoronal[i].SetVisibility(1)
            self.dataImporterCoronal[i].Modified()  
            if i == idx:
                # Update the position and lateral extension of the axial line to cross the entire image
                self.axialLineSource.SetPoint1(self.Im_Offset[i,0],self.Im_Offset[i,1]+ self.current_coronal_slice_index[i]*self.pixel_spac[i,0], 0.05)
                self.axialLineSource.SetPoint2(self.Im_Offset[i,0]+extent[1]*self.pixel_spac[i,1]-self.pixel_spac[i,1],self.Im_Offset[i,1]+ self.current_coronal_slice_index[i]*self.pixel_spac[i,0], 0.05)
                self.axialLineSource.Modified()  # Notify VTK of the changes
                
                # Update the position and lateral extension of the axial line to cross the entire image
                self.sagittalLineSource.SetPoint1(self.Im_Offset[i,1]+self.current_coronal_slice_index[i]*self.pixel_spac[i,0],self.Im_Offset[i,2], 0.05)
                self.sagittalLineSource.SetPoint2(self.Im_Offset[i,1]+self.current_coronal_slice_index[i]*self.pixel_spac[i,0],self.Im_Offset[i,2]+extent[0]*self.slice_thick[i]-self.slice_thick[i], 0.05)
                self.sagittalLineSource.Modified()  # Notify VTK of the changes
            #
            self.imageActorCoronal[i].SetPosition(self.Im_Offset[i,0], self.Im_Offset[i,2] , 0)
            # if self.modality == 'RTDOSE':   
            #     # Just update the slice data for the existing pipeline
            #     slice_dose = self.current_slice_index[1]-int(self.Dose_Im_offset[1])
        else:
            imageProperty = self.imageActorCoronal[i].GetProperty()
            imageProperty.SetOpacity(0) 
            self.imageActorCoronal[i].SetVisibility(0)
            self.dataImporterCoronal[i].Modified()  
    #

    # Render the updated data
    self.vtkWidgetCoronal.GetRenderWindow().Render()
    self.vtkWidgetAxial.GetRenderWindow().Render()
    self.vtkWidgetSagittal.GetRenderWindow().Render()
    self.sliceChanged.emit("coronal", self.current_coronal_slice_index)



def _ensure_coronal_mask_overlay(self):
    if hasattr(self, "maskOverlayImporterCoronal"):
        return
    self.maskOverlayImporterCoronal = vtk.vtkImageImport()
    self.maskOverlayImporterCoronal.SetDataScalarTypeToUnsignedChar()
    self.maskOverlayImporterCoronal.SetNumberOfScalarComponents(4)  # RGBA
    # (col=x, row=z)
    self.maskOverlayImporterCoronal.SetDataSpacing(self.pixel_spac[0,1], self.slice_thick[0], 1.0)
    self.maskOverlayImporterCoronal.SetDataOrigin(0.0, 0.0, 0.0)

    self.maskOverlayActorCoronal = vtk.vtkImageActor()
    self.maskOverlayActorCoronal.GetMapper().SetInputConnection(
        self.maskOverlayImporterCoronal.GetOutputPort()
    )
    self.maskOverlayActorCoronal.InterpolateOff()
    self.maskOverlayActorCoronal.SetPickable(False)

    renderer = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()
    renderer.AddActor(self.maskOverlayActorCoronal)


def _build_coronal_mask_rgba(self):
    # Y slice index (coronal)
    y = int(self.current_coronal_slice_index[0])

    # geometry: display_data[0][:, y, :] is (z, x)
    if (not hasattr(self, "display_data") or
        self.display_data is None or
        len(self.display_data) == 0 or
        self.display_data[0].ndim < 3):
        return None

    h, w = self.display_data[0].shape[0], self.display_data[0].shape[2]  # (z, x)
    rgba = np.zeros((h, w, 4), dtype=np.uint8)

    series = self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]
    if not series.get("structures"):
        return rgba

    names  = series.get('structures_names', [])
    keys   = series.get('structures_keys',  [])
    view   = series.get('structures_view',  [0]*len(names))
    colors = series.get('structures_color', ["#ff0000"]*len(names))
    mtr    = series.get('structures_mask_transparency', [1.0]*len(names))

    n = min(len(names), len(keys), len(colors), len(mtr))
    if n == 0:
        return rgba

    for i in range(n):
        if view[i] != 1:      # ← gate by checkbox
            continue
        s_key = keys[i]
        sdat  = series["structures"].get(s_key, {})
        mask3d = sdat.get("Mask3D")
        if mask3d is None or y < 0 or y >= mask3d.shape[1]:
            continue

        mt = float(mtr[i])
        if mt >= 0.999:       # 1.0 → hidden
            continue

        mask2d = mask3d[:, y, :] > 0   # (z, x)
        if not np.any(mask2d):
            continue

        r, g, b = _to_rgbf(colors[i])
        a = np.clip(1.0 - mt, 0.0, 0.99)

        R = int(r*255); G = int(g*255); B = int(b*255); A = int(a*255)
        m = mask2d
        rgba[m, 0] = np.maximum(rgba[m, 0], R)
        rgba[m, 1] = np.maximum(rgba[m, 1], G)
        rgba[m, 2] = np.maximum(rgba[m, 2], B)
        rgba[m, 3] = np.maximum(rgba[m, 3], A)

    return rgba


def _update_coronal_mask_overlay(self):
    _ensure_coronal_mask_overlay(self)
    rgba = _build_coronal_mask_rgba(self)
    if rgba is None:
        self.maskOverlayActorCoronal.GetProperty().SetOpacity(0.0)
        return

    h, w, _ = rgba.shape
    data = rgba.tobytes()

    imp = self.maskOverlayImporterCoronal
    imp.SetDataSpacing(self.pixel_spac[0,1], self.slice_thick[0], 1.0)  # (x, z)
    imp.SetDataOrigin(0.0, 0.0, 0.0)
    imp.CopyImportVoidPointer(data, len(data))
    imp.SetWholeExtent(0, w-1, 0, h-1, 0, 0)
    imp.SetDataExtent (0, w-1, 0, h-1, 0, 0)
    imp.SetNumberOfScalarComponents(4)
    imp.SetDataScalarTypeToUnsignedChar()
    imp.Modified()

    # Match coronal image actor position (x,z)
    self.maskOverlayActorCoronal.SetPosition(
        self.Im_Offset[0, 0],
        self.Im_Offset[0, 2],
        _overlay_epsilon(self) * 0.5
    )
    self.maskOverlayActorCoronal.SetOpacity(1.0)






























def disp_structure_overlay_coronal(self):
    """
    Show selected structures (structures_view==1) on the coronal renderer.
    Uses saved per-structure appearance:
      - structures_color        -> hex "#rrggbb"
      - structures_line_width   -> float
      - structures_transparency -> float in [0,1]
    """
    renderer = (
        self.vtkWidgetCoronal.GetRenderWindow()
        .GetRenderers()
        .GetFirstRenderer()
    )

    # ─── clear previous overlay ───────────────────────────────────────
    for actor in getattr(self, "structure_actors_co", []):
        renderer.RemoveActor(actor)
    self.structure_actors_co = []

    # ─── fetch current series ────────────────────────────────────────
    series_dict = (
        self.medical_image[self.patientID][self.studyID]
                       [self.modality][self.series_index]
    )
    if not series_dict.get("structures"):
        return  # nothing to draw

    slice_idx = self.current_coronal_slice_index[0]   # Y index

    # pixel spacing for coronal slices: (row = z, col = x)
    px_spacing = (self.slice_thick[0], self.pixel_spac[0, 0])

    names = series_dict.get('structures_names', [])
    keys  = series_dict.get('structures_keys', [])
    view  = series_dict.get('structures_view', [0]*len(names))

    # keep arrays aligned; avoid IndexError
    n = min(len(view), len(keys), len(names))

    # Saved appearance with safe defaults
    def _align(arr, default):
        arr = arr if isinstance(arr, list) else []
        if len(arr) < n:
            arr = arr + [default] * (n - len(arr))
        else:
            arr = arr[:n]
        return arr

    colors_hex   = _align(series_dict.get('structures_color'),        "#ffffff")
    line_widths  = _align(series_dict.get('structures_line_width'),   2.0)
    transpars    = _align(series_dict.get('structures_transparency'), 0.5)

    def _hex_to_rgbf(h):
        try:
            s = (h or "").strip()
            if s.startswith("#"):
                s = s[1:]
            if len(s) == 3:  # "abc" → "aabbcc"
                s = "".join(c*2 for c in s)
            r = int(s[0:2], 16) / 255.0
            g = int(s[2:4], 16) / 255.0
            b = int(s[4:6], 16) / 255.0
            return (r, g, b)
        except Exception:
            return (1.0, 1.0, 1.0)



    # ─── loop over selected structures ───────────────────────────────
    for i in range(n):
        if view[i] != 1:
            continue

        s_key = keys[i]
        if not s_key:
            continue

        s_data = series_dict.get("structures", {}).get(s_key, {})
        if not s_data:
            continue

        # Ensure contour containers exist
        if 'Contours2D' not in s_data or not isinstance(s_data['Contours2D'], dict):
            s_data['Contours2D'] = {'axial': {}, 'sagittal': {}, 'coronal': {}}

        # First-time actors dict
        if "VTKActors2D" not in s_data:
            s_data["VTKActors2D"] = {}

        # Build contours if missing or modified
        if not s_data['Contours2D'].get('coronal') or s_data.get('Modified', 0) == 1:
            s_data['Contours2D'] = build_contours_for_structure(s_data['Mask3D'])

        # Rebuild actors (coronal) if missing or modified
        if "coronal" not in s_data["VTKActors2D"] or s_data.get('Modified', 0) == 1:
            contours_cor = s_data.get("Contours2D", {}).get("coronal", {})
            s_data["VTKActors2D"]["coronal"] = actors_from_contours(
                contours_cor,
                px_spacing,
                line_width=float(line_widths[i]),
                color=_hex_to_rgbf(colors_hex[i]),
            )

        if s_data.get('Modified', 0) == 1:
            s_data['Modified'] = 0  # reset modified flag

        actors_dict = s_data["VTKActors2D"]["coronal"]
        if slice_idx not in actors_dict:
            continue  # no contour on this Y slice

        src_actor = actors_dict[slice_idx]

        # ── style from saved arrays ───────────────────────────────────
        actor = vtk.vtkActor()
        actor.ShallowCopy(src_actor)
        actor.GetProperty().SetColor(_hex_to_rgbf(colors_hex[i]))
        actor.GetProperty().SetOpacity(1.0 - float(transpars[i]))   # 0→opaque,1→transparent in UI
        actor.GetProperty().SetLineWidth(float(line_widths[i]))
        actor.GetProperty().SetRepresentationToWireframe()

        # place slightly above image plane for visibility
        actor.SetPosition(self.Im_Offset[0, 0],    # X shift
                          self.Im_Offset[0, 2],    # Z shift
                          _overlay_epsilon(self))

        renderer.AddActor(actor)
        self.structure_actors_co.append(actor)



    renderer.ResetCameraClippingRange()
    self.vtkWidgetCoronal.GetRenderWindow().Render()


def disp_roi_coronal(self):
    for row in range(self.table_circ_roi.rowCount()):
        try:
            item_x = self.table_circ_roi.item(row, 0)
            item_y = self.table_circ_roi.item(row, 1)
            item_radius = self.table_circ_roi.item(row, 2)
            sli_ini = self.table_circ_roi.item(row, 3)
            sli_fin = self.table_circ_roi.item(row, 4)
            transparency = self.table_circ_roi.item(row, 5)
            R_item = self.table_circ_roi.item(row, 8) or self.table_circ_roi.item(row, 7) or self.table_circ_roi.item(row, 6)
            G_item = self.table_circ_roi.item(row, 9) or self.table_circ_roi.item(row, 8) or self.table_circ_roi.item(row, 7)
            B_item = self.table_circ_roi.item(row, 10) or self.table_circ_roi.item(row, 9) or self.table_circ_roi.item(row, 8)

            if (item_x is None or item_y is None or item_radius is None or sli_ini is None or sli_fin is None or transparency is None):
                continue

            sli_ini_val = float(sli_ini.text())
            sli_fin_val = float(sli_fin.text())
            center_x_pixel = float(item_x.text())
            center_y_pixel = float(item_y.text())
            radius = float(item_radius.text())
            transparency_val = float(transparency.text())
            R = float(R_item.text()) if R_item is not None else 1.0
            G = float(G_item.text()) if G_item is not None else 0.0
            B = float(B_item.text()) if B_item is not None else 0.0

            dir_widget = self.table_circ_roi.cellWidget(row, 7)
            if dir_widget is not None and hasattr(dir_widget, 'currentText'):
                row_dir = dir_widget.currentText()
            else:
                row_dir = item_x.data(Qt.UserRole + 1) if item_x is not None else "Axial"
            if not row_dir:
                row_dir = "Axial"

            curr_co = self.current_coronal_slice_index[0]

            if row_dir == "Coronal":
                if curr_co < sli_ini_val or curr_co > sli_fin_val:
                    if row < len(self.circle_actors_co):
                        renderer = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()
                        actor_to_remove = self.circle_actors_co.pop(row)
                        renderer.RemoveActor(actor_to_remove)
                        self.vtkWidgetCoronal.GetRenderWindow().Render()
                    continue

                center_x_phys = center_x_pixel * self.pixel_spac[0, 0]
                center_y_phys = center_y_pixel * self.slice_thick[0]
                radius_phys = radius * self.pixel_spac[0, 0]

                circle_source = vtk.vtkRegularPolygonSource()
                circle_source.SetNumberOfSides(50)
                circle_source.SetRadius(radius_phys)
                circle_source.SetCenter(center_x_phys, center_y_phys, 1)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(circle_source.GetOutputPort())

                if row < len(self.circle_actors_co):
                    circle_actor = self.circle_actors_co[row]
                    circle_actor.SetMapper(mapper)
                    circle_actor.GetProperty().SetColor(R, G, B)
                    circle_actor.GetProperty().SetOpacity(1 - transparency_val)
                else:
                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(R, G, B)
                    actor.GetProperty().SetLineWidth(2)
                    actor.GetProperty().SetOpacity(1 - transparency_val)
                    self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(actor)
                    self.circle_actors_co.append(actor)

            else:
                if row_dir == "Axial":
                    if curr_co < (center_y_pixel - radius) or curr_co > (center_y_pixel + radius):
                        if row < len(self.circle_actors_co):
                            renderer = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()
                            actor_to_remove = self.circle_actors_co.pop(row)
                            renderer.RemoveActor(actor_to_remove)
                            self.vtkWidgetCoronal.GetRenderWindow().Render()
                        continue

                    dist = abs(curr_co - center_y_pixel)
                    width = 2 * math.sqrt(max(0, radius**2 - dist**2)) * self.pixel_spac[0, 0]
                    height = (sli_fin_val - sli_ini_val + 1) * self.slice_thick[0]
                    cx_phys = center_x_pixel * self.pixel_spac[0, 0]
                    cy_phys = (sli_ini_val + sli_fin_val) / 2 * self.slice_thick[0]
                else: # Sagittal
                    if curr_co < (center_x_pixel - radius) or curr_co > (center_x_pixel + radius):
                        if row < len(self.circle_actors_co):
                            renderer = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()
                            actor_to_remove = self.circle_actors_co.pop(row)
                            renderer.RemoveActor(actor_to_remove)
                            self.vtkWidgetCoronal.GetRenderWindow().Render()
                        continue

                    dist = abs(curr_co - center_x_pixel)
                    width = (sli_fin_val - sli_ini_val + 1) * self.pixel_spac[0, 0]
                    height = 2 * math.sqrt(max(0, radius**2 - dist**2)) * self.slice_thick[0]
                    cx_phys = (sli_ini_val + sli_fin_val) / 2 * self.pixel_spac[0, 0]
                    cy_phys = center_y_pixel * self.slice_thick[0]

                cube_source = vtk.vtkCubeSource()
                cube_source.SetXLength(width)
                cube_source.SetYLength(height)
                cube_source.SetZLength(1)
                cube_source.SetCenter(cx_phys, cy_phys, 1)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(cube_source.GetOutputPort())

                if row < len(self.circle_actors_co):
                    rect_actor = self.circle_actors_co[row]
                    rect_actor.SetMapper(mapper)
                    rect_actor.GetProperty().SetColor(R, G, B)
                    rect_actor.GetProperty().SetOpacity(1 - transparency_val)
                else:
                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(R, G, B)
                    actor.GetProperty().SetOpacity(1 - transparency_val)
                    self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(actor)
                    self.circle_actors_co.append(actor)

        except Exception as e:
            print(f"Skipping row {row} in disp_roi_coronal due to error: {e}")
            continue  
    

def display_dwell_positions_co(self):
    """
    Display the dwell positions on top of the DICOM images using VTK.
    - Each dwell is the outline of a cylinder along the source direction (plan orientation,
      else the channel path), with an almost transparent fill.
    - Dwell positions of the catheters ticked in the catheter list (brachy_tree); those
      with 0 s only when "0 s" is checked under Display.
    - Colors and sizes come from the Style panel (brachy_style); by default:
    - Dwell positions with dwell_time == 0 are shown in red.
    - Dwell positions with dwell_time > 0 are shown in dark green.
    - Dwell positions within Ref_Z ± slice_thickness/2 are shown in light green.
    """
    renderer = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()

    # Remove any previous dwell actors
    for actor in self.dwell_actors_co:
        renderer.RemoveActor(actor)
    self.dwell_actors_co.clear()

    # Retrieve channels from medical_image
    try:
        meta = (self.medical_image[self.patientID][self.studyID]          # may raise KeyError
                                [self.modality][self.series_index]
                                ['metadata'])
        channels = meta.get('Plan_Brachy_Channels')
    except KeyError:
        # Data tree incomplete (no metadata at all) ─ silently abort
        return

    if not channels:                     # None or empty list
        return                           # nothing to draw

    # Catheters ticked in the catheter list; dwells with 0 s only if shown (Display)
    channels_to_display = [ch for ch in channels if channel_visible(ch)]
    show_zero = brachy_display(self)['dw_zero']

    # Dwells are drawn above the catheter points (spheres of diameter = catheter point size)
    style = brachy_style(self)
    z_floor = 0.5 + style['ch_point_size'] / 2

    # Get the current slice reference Z position and tolerance
    Ref_z = self.current_coronal_slice_index[0] * self.pixel_spac[0, 0] #+ self.Im_Offset[1, 2]
    z_tolerance = self.pixel_spac[0, 0] /2

    # Position, source direction (view coordinates), size and color of every dwell shown
    xy, dirs, sizes, colors = [], [], [], []
    for current_ch in channels_to_display:
        dwell_info = current_ch.get('DwellInfo')

        if dwell_info is None or not isinstance(dwell_info, np.ndarray) or dwell_info.shape[1] < 7:
            continue  # Skip invalid channels

        # Extract dwell positions (X, Y, Z coordinates) and convert them to image space
        dwell_times = dwell_info[:, 2]  # Assuming dwell time is in column 2
        x = dwell_info[:, 3] - self.Im_PatPosition[0, 0]  # X coordinate in mm
        z = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - (dwell_info[:, 4] - self.Im_PatPosition[0, 1])  # Y coordinate
        y = dwell_info[:, 5] - self.Im_PatPosition[0, 2]  # Z coordinate in mm
        keep = show_zero | (dwell_times != 0)
        xy.append(np.column_stack((x, y))[keep])
        dirs.append(view_dir('coronal', dwell_directions(dwell_info, current_ch.get('ChPos')))[keep])
        sizes.append(np.tile(dwell_glyph_size(dwell_info[:, 3:6], style['dw_size']), (len(x), 1))[keep])
        # Dwell time 0, position within Ref_Z ± slice_thickness/2, or elsewhere
        in_slice = (Ref_z - z_tolerance <= z) & (z <= Ref_z + z_tolerance)
        colors.append(np.where((dwell_times == 0)[:, None], style['dw_zero'],
                               np.where(in_slice[:, None], style['dw_slice'], style['dw_other']))[keep])

    xy = np.vstack(xy) if xy else np.zeros((0, 2))
    if len(xy):
        for dwell_actor in _dwell_glyph_actors(xy, np.vstack(dirs), np.vstack(sizes), np.vstack(colors), z_floor, style):
            renderer.AddActor(dwell_actor)
            self.dwell_actors_co.append(dwell_actor)

    # Re-render to show the updated scene with dwell positions
    self.vtkWidgetCoronal.GetRenderWindow().Render()


def display_brachy_channel_overlay_co(self):
    """
    Display brachytherapy channels as connected lines with spheres at each channel point
    (colors and sizes from the Style panel: blue by default, the catheter selected in the
    catheter list green, the one being edited yellow).
    - Only the catheters ticked in the catheter list (brachy_tree); their points, path
      and numbers (next to the first point) as set under Display.
    """
    renderer = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()

    # Remove any previous channel actors
    for actor in self.channel_actors_co:
        renderer.RemoveActor(actor)
    self.channel_actors_co.clear()

    # Retrieve channels from medical_image
    try:
        meta = (self.medical_image[self.patientID][self.studyID]          # may raise KeyError
                                [self.modality][self.series_index]
                                ['metadata'])
        channels = meta.get('Plan_Brachy_Channels')
    except KeyError:
        # Data tree incomplete (no metadata at all) ─ silently abort
        return

    if not channels:                     # None or empty list
        return                           # nothing to draw

    # Points, path and numbers of the catheters as set under Display
    show = brachy_display(self)

    # Colors and sizes from the Style panel; spheres of diameter = catheter point size
    style = brachy_style(self)
    point_size = style['ch_point_size'] / 2
    # Catheter / point being edited (edit tools) and catheter selected in the list
    edit_ch, edit_pt = brachy_highlight(self, channels)
    sel_ch = selected_catheter(self, channels)

    # Iterate through the catheters ticked in the catheter list, the selected / edited one last (on top)
    for k in sorted(range(len(channels)), key=lambda j: channels[j] is edit_ch or channels[j] is sel_ch):
        current_ch = channels[k]
        if not channel_visible(current_ch):
            continue
        point_color, line_color = catheter_colors(style, current_ch is edit_ch, current_ch is sel_ch)
        ch_points = current_ch.get('ChPos')

        # Check if 'ChPos' exists and contains valid data
        if ch_points is None or not isinstance(ch_points, np.ndarray) or ch_points.shape[1] < 3:
            continue  # Skip invalid channels

        # Extract channel points (X, Y, Z coordinates)
        x = ch_points[:, 0] - self.Im_PatPosition[0, 0]  # X coordinate in mm
        z = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - (ch_points[:, 1] - self.Im_PatPosition[0, 1])  # Y coordinate
        y = ch_points[:, 2] - self.Im_PatPosition[0, 2]  # Z coordinate in mm

        # Create a polyline to represent the connected channel points
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        # Add points and create lines between consecutive points
        for i in range(len(x)):
            points.InsertNextPoint(x[i], y[i], 0.5)  # Insert each point into vtkPoints
            if i > 0:
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0, i - 1)  # Line from previous point to current point
                line.GetPointIds().SetId(1, i)
                lines.InsertNextCell(line)

            if not show['ch_points']:
                continue
            # Create solid blue spheres for each point
            sphere_source = vtk.vtkSphereSource()
            sphere_source.SetCenter(x[i], y[i], 0.5)
            sphere_source.SetRadius(point_size)  # Sphere size is half of the value from the spinbox
            sphere_source.SetPhiResolution(20)
            sphere_source.SetThetaResolution(20)

            # Map the sphere to an actor
            sphere_mapper = vtk.vtkPolyDataMapper()
            sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())

            sphere_actor = vtk.vtkActor()
            sphere_actor.SetMapper(sphere_mapper)

            # Catheter point color (the point being edited in the edit point color)
            if current_ch is edit_ch and i == edit_pt:
                sphere_actor.GetProperty().SetColor(*style['edit_point'])
            else:
                sphere_actor.GetProperty().SetColor(*point_color)
            sphere_actor.GetProperty().SetOpacity(0.7)  # Full opacity

            # Add the actor for the sphere to the renderer
            renderer.AddActor(sphere_actor)
            self.channel_actors_co.append(sphere_actor)

        # Create the polyline
        polyline = vtk.vtkPolyData()
        polyline.SetPoints(points)
        polyline.SetLines(lines)

        # Map the polyline to an actor
        polyline_mapper = vtk.vtkPolyDataMapper()
        polyline_mapper.SetInputData(polyline)

        polyline_actor = vtk.vtkActor()
        polyline_actor.SetMapper(polyline_mapper)
        polyline_actor.GetProperty().SetColor(*line_color)
        polyline_actor.GetProperty().SetLineWidth(style['ch_line_width'])

        # Add the polyline actor to the renderer (the path, if shown)
        if show['ch_path']:
            renderer.AddActor(polyline_actor)
            self.channel_actors_co.append(polyline_actor)

        # Catheter name (its number unless renamed) next to its first point (tip)
        if show['ch_labels'] and len(x):
            label = brachy_label_actor(x[0], y[0], 0.5, catheter_label(current_ch, k), line_color, style['label_size'])
            renderer.AddActor(label)
            self.channel_actors_co.append(label)

    # Render the updated display with the channels
    self.vtkWidgetCoronal.GetRenderWindow().Render()



def displaysagittal(self,Im = None):

    # ------------------------------------------------------------------
    if (not hasattr(self, "display_data") or
        self.display_data is None or
        len(self.display_data) == 0):
        return                    # nothing loaded → ignore the call

    idx = self.layer_selected.currentIndex()
    if idx not in self.display_data:
        QMessageBox.warning(None, "Warning", "No image data was found.")
        return

    if not isinstance(self.display_data[idx], np.ndarray) or self.display_data[idx].ndim==2:
        return
    for i in range(len(self.dataImporterSagittal)):
        
        if i == 3:
            renderer = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()
            if self.checkBox_circ_roi_data_2.isChecked():
                for actor in self.circle_actors_sa:
                    renderer.RemoveActor(actor)
                self.circle_actors_sa.clear()
                # self.vtkWidgetAxial.GetRenderWindow().Render() 
                disp_roi_sagittal(self)

            update_mc_grid_sagittal(self)
            update_mat_overlay_sagittal(self)

            # Dose reference points and dwells, as set under View > PLAN > Brachy > Display
            show_ref_points = getattr(self, 'brachy_show_ref_points', None)
            if show_ref_points is not None and show_ref_points.isChecked():
                display_ref_points_sa(self)
            else:
                if hasattr(self, 'ref_point_actors_sa'):
                    for actor in self.ref_point_actors_sa:
                        renderer.RemoveActor(actor)
                    self.ref_point_actors_sa.clear()
            
            if self.display_dw_overlay.isChecked():
                display_dwell_positions_sa(self)
            else:
                for actor in self.dwell_actors_sa:
                    renderer.RemoveActor(actor)
                self.dwell_actors_sa.clear()

            # EBRT Fields overlay
            if hasattr(self, 'display_ebrt_fields_overlay') and self.display_ebrt_fields_overlay.isChecked():
                display_ebrt_fields_sa(self)
            else:
                if hasattr(self, 'ebrt_actors_sa'):
                    for actor in self.ebrt_actors_sa:
                        renderer.RemoveActor(actor)
                    self.ebrt_actors_sa.clear()
        if i == 3 and  self.display_brachy_channel_overlay.isChecked():
            # Check if the required fields exist in medical_image
                display_brachy_channel_overlay_sa(self)    
        if i == 3 and self.DataType in ("DICOM", "Nifti"):
            _update_sagittal_mask_overlay(self)
            disp_structure_overlay_sagittal(self)

        if self.slice_thick[i] == 0:
            self.imageActorSagittal[i].SetVisibility(0)
            continue
        
        
        
        Offset_vox = (self.Im_PatPosition[idx,0]-self.Im_PatPosition[i,0])/self.pixel_spac[i,1]
        self.current_sagittal_slice_index[i] = int(np.round(self.current_sagittal_slice_index[idx]*(self.pixel_spac[idx,1]/self.pixel_spac[i,1]) + Offset_vox))
        #
        if 0 <= self.current_sagittal_slice_index[i] < self.display_data[i].shape[2]:
            # Just update the slice data for the existing pipeline
            if Im is not None:
                slice_data = Im
            else:
                slice_data = self.display_data[i][:, :, self.current_sagittal_slice_index[i]]
            data_string = slice_data.tobytes()
          
            extent = slice_data.shape
            self.dataImporterSagittal[i].CopyImportVoidPointer(data_string, len(data_string))
            self.dataImporterSagittal[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            self.dataImporterSagittal[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            
            self.dataImporterSagittal[i].SetDataSpacing(self.pixel_spac[i,0],self.slice_thick[i],1) 
            self.imageActorSagittal[i].SetPosition(self.Im_Offset[i,1], self.Im_Offset[i,2] , 0)
            imageProperty = self.imageActorSagittal[i].GetProperty()
            imageProperty.SetOpacity(self.LayerAlpha[i])  
            self.imageActorSagittal[i].SetVisibility(1)
            # Inform the pipeline that data has changed.
            self.dataImporterSagittal[i].Modified()  
            if i==idx:
                # Update the position and lateral extension of the axial line to cross the entire image
                self.axialLine2Source.SetPoint1(self.Im_Offset[i,0]+self.current_sagittal_slice_index[i]*self.pixel_spac[i,1],self.Im_Offset[i,1], 0.05)
                self.axialLine2Source.SetPoint2(self.Im_Offset[i,0]+self.current_sagittal_slice_index[i]*self.pixel_spac[i,1],self.Im_Offset[i,1]+extent[1]*self.pixel_spac[i,0]-self.pixel_spac[i,0],  0.05)
                self.axialLine2Source.Modified()  # Notify VTK of the changes
            
                # # Update the position and lateral extension of the coronal line to cross the entire image
                self.coronalLineSource.SetPoint1(self.Im_Offset[i,0]+self.current_sagittal_slice_index[i]*self.pixel_spac[i,1], self.Im_Offset[i,2], 0.05)
                self.coronalLineSource.SetPoint2(self.Im_Offset[i,0]+self.current_sagittal_slice_index[i]*self.pixel_spac[i,1],self.Im_Offset[i,2]+extent[0]*self.slice_thick[i]-self.slice_thick[i],  0.05)
                self.coronalLineSource.Modified()  # Notify VTK of the changes     
        else: 
            imageProperty = self.imageActorSagittal[i].GetProperty()
            imageProperty.SetOpacity(0)  
            self.imageActorSagittal[i].SetVisibility(0)  
        #
    # Render the updated data
    self.vtkWidgetSagittal.GetRenderWindow().Render()
    self.vtkWidgetCoronal.GetRenderWindow().Render()
    self.vtkWidgetAxial.GetRenderWindow().Render()
    self.sliceChanged.emit("coronal", self.current_sagittal_slice_index)
    


def _ensure_sagittal_mask_overlay(self):
    if hasattr(self, "maskOverlayImporterSagittal"):
        return
    self.maskOverlayImporterSagittal = vtk.vtkImageImport()
    self.maskOverlayImporterSagittal.SetDataScalarTypeToUnsignedChar()
    self.maskOverlayImporterSagittal.SetNumberOfScalarComponents(4)  # RGBA
    # (col=y, row=z)
    self.maskOverlayImporterSagittal.SetDataSpacing(self.pixel_spac[0,0], self.slice_thick[0], 1.0)
    self.maskOverlayImporterSagittal.SetDataOrigin(0.0, 0.0, 0.0)

    self.maskOverlayActorSagittal = vtk.vtkImageActor()
    self.maskOverlayActorSagittal.GetMapper().SetInputConnection(
        self.maskOverlayImporterSagittal.GetOutputPort()
    )
    self.maskOverlayActorSagittal.InterpolateOff()
    self.maskOverlayActorSagittal.SetPickable(False)

    renderer = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()
    renderer.AddActor(self.maskOverlayActorSagittal)


def _build_sagittal_mask_rgba(self):
    # X slice index (sagittal)
    x = int(self.current_sagittal_slice_index[0])

    # geometry: display_data[0][:, :, x] is (z, y)
    if (not hasattr(self, "display_data") or
        self.display_data is None or
        len(self.display_data) == 0 or
        self.display_data[0].ndim < 3):
        return None

    h, w = self.display_data[0].shape[0], self.display_data[0].shape[1]  # (z, y)
    rgba = np.zeros((h, w, 4), dtype=np.uint8)

    series = self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]
    if not series.get("structures"):
        return rgba

    names  = series.get('structures_names', [])
    keys   = series.get('structures_keys',  [])
    view   = series.get('structures_view',  [0]*len(names))
    colors = series.get('structures_color', ["#ff0000"]*len(names))
    mtr    = series.get('structures_mask_transparency', [1.0]*len(names))

    n = min(len(names), len(keys), len(colors), len(mtr))
    if n == 0:
        return rgba

    for i in range(n):
        if view[i] != 1:      # ← gate by checkbox
            continue
        s_key = keys[i]
        sdat  = series["structures"].get(s_key, {})
        mask3d = sdat.get("Mask3D")
        if mask3d is None or x < 0 or x >= mask3d.shape[2]:
            continue

        mt = float(mtr[i])
        if mt >= 0.999:
            continue

        mask2d = mask3d[:, :, x] > 0   # (z, y)
        if not np.any(mask2d):
            continue

        r, g, b = _to_rgbf(colors[i])
        a = np.clip(1.0 - mt, 0.0, 0.99)

        R = int(r*255); G = int(g*255); B = int(b*255); A = int(a*255)
        m = mask2d
        rgba[m, 0] = np.maximum(rgba[m, 0], R)
        rgba[m, 1] = np.maximum(rgba[m, 1], G)
        rgba[m, 2] = np.maximum(rgba[m, 2], B)
        rgba[m, 3] = np.maximum(rgba[m, 3], A)

    return rgba


def _update_sagittal_mask_overlay(self):
    _ensure_sagittal_mask_overlay(self)
    rgba = _build_sagittal_mask_rgba(self)
    if rgba is None:
        self.maskOverlayActorSagittal.GetProperty().SetOpacity(0.0)
        return

    h, w, _ = rgba.shape
    data = rgba.tobytes()

    imp = self.maskOverlayImporterSagittal
    imp.SetDataSpacing(self.pixel_spac[0,0], self.slice_thick[0], 1.0)  # (y, z)
    imp.SetDataOrigin(0.0, 0.0, 0.0)
    imp.CopyImportVoidPointer(data, len(data))
    imp.SetWholeExtent(0, w-1, 0, h-1, 0, 0)
    imp.SetDataExtent (0, w-1, 0, h-1, 0, 0)
    imp.SetNumberOfScalarComponents(4)
    imp.SetDataScalarTypeToUnsignedChar()
    imp.Modified()

    # Match sagittal image actor position (y,z)
    self.maskOverlayActorSagittal.SetPosition(
        self.Im_Offset[0, 1],
        self.Im_Offset[0, 2],
        _overlay_epsilon(self) * 0.5
    )
    self.maskOverlayActorSagittal.SetOpacity(1.0)














def disp_structure_overlay_sagittal(self):
    """
    Show selected structures (structures_view==1) on the sagittal renderer.
    Uses saved per-structure appearance:
      - structures_color        -> hex "#rrggbb"
      - structures_line_width   -> float
      - structures_transparency -> float in [0,1]
    """
    renderer = (
        self.vtkWidgetSagittal.GetRenderWindow()
        .GetRenderers()
        .GetFirstRenderer()
    )

    # ─── clear any actors from the previous draw ──────────────────────
    for actor in getattr(self, "structure_actors_sa", []):
        renderer.RemoveActor(actor)
    self.structure_actors_sa = []

    # ─── grab data for the currently displayed image series ───────────
    series_dict = (
        self.medical_image[self.patientID][self.studyID]
                       [self.modality][self.series_index]
    )
    if not series_dict.get("structures"):
        return  # nothing to draw yet

    slice_idx = self.current_sagittal_slice_index[0]  # X index

    # pixel spacing for sagittal slices: (row = z, col = y) in mm
    px_spacing = (self.slice_thick[0], self.pixel_spac[0, 1])

    names = series_dict.get('structures_names', [])
    keys  = series_dict.get('structures_keys', [])
    view  = series_dict.get('structures_view', [0]*len(names))

    # keep arrays aligned; avoid IndexError
    n = min(len(view), len(keys), len(names))

    # Saved appearance with safe defaults
    def _align(arr, default):
        arr = arr if isinstance(arr, list) else []
        if len(arr) < n:
            arr = arr + [default] * (n - len(arr))
        else:
            arr = arr[:n]
        return arr

    colors_hex   = _align(series_dict.get('structures_color'),        "#ffffff")
    line_widths  = _align(series_dict.get('structures_line_width'),   2.0)
    transpars    = _align(series_dict.get('structures_transparency'), 0.5)

    def _hex_to_rgbf(h):
        try:
            s = (h or "").strip()
            if s.startswith("#"):
                s = s[1:]
            if len(s) == 3:  # "abc" → "aabbcc"
                s = "".join(c*2 for c in s)
            r = int(s[0:2], 16) / 255.0
            g = int(s[2:4], 16) / 255.0
            b = int(s[4:6], 16) / 255.0
            return (r, g, b)
        except Exception:
            return (1.0, 1.0, 1.0)



    # ─── main loop over selected structures ───────────────────────────
    for i in range(n):
        if view[i] != 1:
            continue

        s_key = keys[i]
        if not s_key:
            continue

        s_data = series_dict.get("structures", {}).get(s_key, {})
        if not s_data:
            continue

        # Ensure contour containers exist
        if 'Contours2D' not in s_data or not isinstance(s_data['Contours2D'], dict):
            s_data['Contours2D'] = {'axial': {}, 'sagittal': {}, 'coronal': {}}

        # First-time creation of actors dict
        if "VTKActors2D" not in s_data:
            s_data["VTKActors2D"] = {}

        # Build contours if missing or marked modified
        if not s_data['Contours2D'].get('sagittal') or s_data.get('Modified', 0) == 1:
            s_data['Contours2D'] = build_contours_for_structure(s_data['Mask3D'])

        # Rebuild actors (sagittal) if missing or modified
        if "sagittal" not in s_data["VTKActors2D"] or s_data.get('Modified', 0) == 1:
            contours_sag = s_data.get("Contours2D", {}).get("sagittal", {})
            s_data["VTKActors2D"]["sagittal"] = actors_from_contours(
                contours_sag,
                px_spacing,
                line_width=float(line_widths[i]),
                color=_hex_to_rgbf(colors_hex[i]),
            )

        if s_data.get('Modified', 0) == 1:
            s_data['Modified'] = 0  # reset modified flag

        actors_dict = s_data["VTKActors2D"]["sagittal"]
        if slice_idx not in actors_dict:
            continue  # no contour on this X slice

        src_actor = actors_dict[slice_idx]

        # ── customise appearance from saved arrays ────────────────────
        actor = vtk.vtkActor()
        actor.ShallowCopy(src_actor)
        actor.GetProperty().SetColor(_hex_to_rgbf(colors_hex[i]))
        actor.GetProperty().SetOpacity(1.0 - float(transpars[i]))       # 0→opaque,1→transparent in UI
        actor.GetProperty().SetLineWidth(float(line_widths[i]))
        actor.GetProperty().SetRepresentationToWireframe()

        # place slightly above image plane for visibility
        actor.SetPosition(self.Im_Offset[0, 1],    # Y shift
                          self.Im_Offset[0, 2],    # Z shift
                          _overlay_epsilon(self))

        renderer.AddActor(actor)
        self.structure_actors_sa.append(actor)



        
    renderer.ResetCameraClippingRange()
    self.vtkWidgetSagittal.GetRenderWindow().Render()


def disp_roi_sagittal(self):
    for row in range(self.table_circ_roi.rowCount()):
        try:
            item_x = self.table_circ_roi.item(row, 0)
            item_y = self.table_circ_roi.item(row, 1)
            item_radius = self.table_circ_roi.item(row, 2)
            sli_ini = self.table_circ_roi.item(row, 3)
            sli_fin = self.table_circ_roi.item(row, 4)
            transparency = self.table_circ_roi.item(row, 5)
            R_item = self.table_circ_roi.item(row, 8) or self.table_circ_roi.item(row, 7) or self.table_circ_roi.item(row, 6)
            G_item = self.table_circ_roi.item(row, 9) or self.table_circ_roi.item(row, 8) or self.table_circ_roi.item(row, 7)
            B_item = self.table_circ_roi.item(row, 10) or self.table_circ_roi.item(row, 9) or self.table_circ_roi.item(row, 8)

            if (item_x is None or item_y is None or item_radius is None or sli_ini is None or sli_fin is None or transparency is None):
                continue

            sli_ini_val = float(sli_ini.text())
            sli_fin_val = float(sli_fin.text())
            center_x_pixel = float(item_x.text())
            center_y_pixel = float(item_y.text())
            radius = float(item_radius.text())
            transparency_val = float(transparency.text())
            R = float(R_item.text()) if R_item is not None else 1.0
            G = float(G_item.text()) if G_item is not None else 0.0
            B = float(B_item.text()) if B_item is not None else 0.0

            dir_widget = self.table_circ_roi.cellWidget(row, 7)
            if dir_widget is not None and hasattr(dir_widget, 'currentText'):
                row_dir = dir_widget.currentText()
            else:
                row_dir = item_x.data(Qt.UserRole + 1) if item_x is not None else "Axial"
            if not row_dir:
                row_dir = "Axial"

            curr_sa = self.current_sagittal_slice_index[0]

            if row_dir == "Sagittal":
                if curr_sa < sli_ini_val or curr_sa > sli_fin_val:
                    if row < len(self.circle_actors_sa):
                        renderer = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()
                        actor_to_remove = self.circle_actors_sa.pop(row)
                        renderer.RemoveActor(actor_to_remove)
                        self.vtkWidgetSagittal.GetRenderWindow().Render()
                    continue

                center_x_phys = center_x_pixel * self.pixel_spac[0, 1]
                center_y_phys = center_y_pixel * self.slice_thick[0]
                radius_phys = radius * self.pixel_spac[0, 1]

                circle_source = vtk.vtkRegularPolygonSource()
                circle_source.SetNumberOfSides(50)
                circle_source.SetRadius(radius_phys)
                circle_source.SetCenter(center_x_phys, center_y_phys, 1)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(circle_source.GetOutputPort())

                if row < len(self.circle_actors_sa):
                    circle_actor = self.circle_actors_sa[row]
                    circle_actor.SetMapper(mapper)
                    circle_actor.GetProperty().SetColor(R, G, B)
                    circle_actor.GetProperty().SetOpacity(1 - transparency_val)
                else:
                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(R, G, B)
                    actor.GetProperty().SetLineWidth(2)
                    actor.GetProperty().SetOpacity(1 - transparency_val)
                    self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(actor)
                    self.circle_actors_sa.append(actor)

            else:
                if row_dir == "Axial":
                    if curr_sa < (center_x_pixel - radius) or curr_sa > (center_x_pixel + radius):
                        if row < len(self.circle_actors_sa):
                            renderer = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()
                            actor_to_remove = self.circle_actors_sa.pop(row)
                            renderer.RemoveActor(actor_to_remove)
                            self.vtkWidgetSagittal.GetRenderWindow().Render()
                        continue

                    dist = abs(curr_sa - center_x_pixel)
                    width = 2 * math.sqrt(max(0, radius**2 - dist**2)) * self.pixel_spac[0, 1]
                    height = (sli_fin_val - sli_ini_val + 1) * self.slice_thick[0]
                    cx_phys = center_y_pixel * self.pixel_spac[0, 1]
                    cy_phys = (sli_ini_val + sli_fin_val) / 2 * self.slice_thick[0]
                else: # Coronal
                    if curr_sa < (center_x_pixel - radius) or curr_sa > (center_x_pixel + radius):
                        if row < len(self.circle_actors_sa):
                            renderer = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()
                            actor_to_remove = self.circle_actors_sa.pop(row)
                            renderer.RemoveActor(actor_to_remove)
                            self.vtkWidgetSagittal.GetRenderWindow().Render()
                        continue

                    dist = abs(curr_sa - center_x_pixel)
                    width = (sli_fin_val - sli_ini_val + 1) * self.pixel_spac[0, 1]
                    height = 2 * math.sqrt(max(0, radius**2 - dist**2)) * self.slice_thick[0]
                    cx_phys = (sli_ini_val + sli_fin_val) / 2 * self.pixel_spac[0, 1]
                    cy_phys = center_y_pixel * self.slice_thick[0]

                cube_source = vtk.vtkCubeSource()
                cube_source.SetXLength(width)
                cube_source.SetYLength(height)
                cube_source.SetZLength(1)
                cube_source.SetCenter(cx_phys, cy_phys, 1)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(cube_source.GetOutputPort())

                if row < len(self.circle_actors_sa):
                    rect_actor = self.circle_actors_sa[row]
                    rect_actor.SetMapper(mapper)
                    rect_actor.GetProperty().SetColor(R, G, B)
                    rect_actor.GetProperty().SetOpacity(1 - transparency_val)
                else:
                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(R, G, B)
                    actor.GetProperty().SetOpacity(1 - transparency_val)
                    self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(actor)
                    self.circle_actors_sa.append(actor)

        except Exception as e:
            print(f"Skipping row {row} in disp_roi_sagittal due to error: {e}")
            continue


def display_dwell_positions_sa(self):
    """
    Display the dwell positions on top of the DICOM images using VTK.
    - Each dwell is the outline of a cylinder along the source direction (plan orientation,
      else the channel path), with an almost transparent fill.
    - Dwell positions of the catheters ticked in the catheter list (brachy_tree); those
      with 0 s only when "0 s" is checked under Display.
    - Colors and sizes come from the Style panel (brachy_style); by default:
    - Dwell positions with dwell_time == 0 are shown in red.
    - Dwell positions with dwell_time > 0 are shown in dark green.
    - Dwell positions within Ref_Z ± slice_thickness/2 are shown in light green.
    """
    renderer = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()

    # Remove any previous dwell actors
    for actor in self.dwell_actors_sa:
        renderer.RemoveActor(actor)
    self.dwell_actors_sa.clear()

    # Retrieve channels from medical_image
    try:
        meta = (self.medical_image[self.patientID][self.studyID]          # may raise KeyError
                                [self.modality][self.series_index]
                                ['metadata'])
        channels = meta.get('Plan_Brachy_Channels')
    except KeyError:
        # Data tree incomplete (no metadata at all) ─ silently abort
        return

    if not channels:                     # None or empty list
        return                           # nothing to draw

    # Catheters ticked in the catheter list; dwells with 0 s only if shown (Display)
    channels_to_display = [ch for ch in channels if channel_visible(ch)]
    show_zero = brachy_display(self)['dw_zero']

    # Dwells are drawn above the catheter points (spheres of diameter = catheter point size)
    style = brachy_style(self)
    z_floor = 0.5 + style['ch_point_size'] / 2

    # Get the current slice reference Z position and tolerance
    Ref_z = self.current_sagittal_slice_index[0] * self.pixel_spac[0, 1] #- self.Im_Offset[1, 2]
    z_tolerance = self.pixel_spac[0, 1] /2
    # Position, source direction (view coordinates), size and color of every dwell shown
    xy, dirs, sizes, colors = [], [], [], []
    for current_ch in channels_to_display:
        dwell_info = current_ch.get('DwellInfo')

        if dwell_info is None or not isinstance(dwell_info, np.ndarray) or dwell_info.shape[1] < 7:
            continue  # Skip invalid channels

        # Extract dwell positions (X, Y, Z coordinates) and convert them to image space
        dwell_times = dwell_info[:, 2]  # dwell time is in column 2
        z = dwell_info[:, 3] - self.Im_PatPosition[0, 0]                                                              # X coordinate in mm
        x = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - (dwell_info[:, 4] - self.Im_PatPosition[0, 1])  # Y coordinate
        y = dwell_info[:, 5] - self.Im_PatPosition[0, 2]                                                              # Z coordinate in mm
        keep = show_zero | (dwell_times != 0)
        xy.append(np.column_stack((x, y))[keep])
        dirs.append(view_dir('sagittal', dwell_directions(dwell_info, current_ch.get('ChPos')))[keep])
        sizes.append(np.tile(dwell_glyph_size(dwell_info[:, 3:6], style['dw_size']), (len(x), 1))[keep])
        # Dwell time 0, position within Ref_Z ± slice_thickness/2, or elsewhere
        in_slice = (Ref_z - z_tolerance <= z) & (z <= Ref_z + z_tolerance)
        colors.append(np.where((dwell_times == 0)[:, None], style['dw_zero'],
                               np.where(in_slice[:, None], style['dw_slice'], style['dw_other']))[keep])

    xy = np.vstack(xy) if xy else np.zeros((0, 2))
    if len(xy):
        for dwell_actor in _dwell_glyph_actors(xy, np.vstack(dirs), np.vstack(sizes), np.vstack(colors), z_floor, style):
            renderer.AddActor(dwell_actor)
            self.dwell_actors_sa.append(dwell_actor)

    # Re-render to show the updated scene with dwell positions
    self.vtkWidgetSagittal.GetRenderWindow().Render()


def display_brachy_channel_overlay_sa(self):
    """
    Display brachytherapy channels as connected lines with spheres at each channel point
    (colors and sizes from the Style panel: blue by default, the catheter selected in the
    catheter list green, the one being edited yellow).
    - Only the catheters ticked in the catheter list (brachy_tree); their points, path
      and numbers (next to the first point) as set under Display.
    """
    renderer = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()

    # Remove any previous channel actors
    for actor in self.channel_actors_sa:
        renderer.RemoveActor(actor)
    self.channel_actors_sa.clear()

    # Retrieve channels from medical_image
    try:
        meta = (self.medical_image[self.patientID][self.studyID]          # may raise KeyError
                                [self.modality][self.series_index]
                                ['metadata'])
        channels = meta.get('Plan_Brachy_Channels')
    except KeyError:
        # Data tree incomplete (no metadata at all) ─ silently abort
        return

    if not channels:                     # None or empty list
        return                           # nothing to draw

    # Points, path and numbers of the catheters as set under Display
    show = brachy_display(self)

    # Colors and sizes from the Style panel; spheres of diameter = catheter point size
    style = brachy_style(self)
    point_size = style['ch_point_size'] / 2
    # Catheter / point being edited (edit tools) and catheter selected in the list
    edit_ch, edit_pt = brachy_highlight(self, channels)
    sel_ch = selected_catheter(self, channels)

    # Iterate through the catheters ticked in the catheter list, the selected / edited one last (on top)
    for k in sorted(range(len(channels)), key=lambda j: channels[j] is edit_ch or channels[j] is sel_ch):
        current_ch = channels[k]
        if not channel_visible(current_ch):
            continue
        point_color, line_color = catheter_colors(style, current_ch is edit_ch, current_ch is sel_ch)
        ch_points = current_ch.get('ChPos')

        # Check if 'ChPos' exists and contains valid data
        if ch_points is None or not isinstance(ch_points, np.ndarray) or ch_points.shape[1] < 3:
            continue  # Skip invalid channels

        # Extract channel points (X, Y, Z coordinates)
        z = ch_points[:, 0] - self.Im_PatPosition[0, 0]  # X coordinate in mm
        x = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - (ch_points[:, 1] - self.Im_PatPosition[0, 1])  # Y coordinate
        y = ch_points[:, 2] - self.Im_PatPosition[0, 2]  # Z coordinate in mm

        # Create a polyline to represent the connected channel points
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        # Add points and create lines between consecutive points
        for i in range(len(x)):
            points.InsertNextPoint(x[i], y[i], 0.5)  # Insert each point into vtkPoints
            if i > 0:
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0, i - 1)  # Line from previous point to current point
                line.GetPointIds().SetId(1, i)
                lines.InsertNextCell(line)

            if not show['ch_points']:
                continue
            # Create solid blue spheres for each point
            sphere_source = vtk.vtkSphereSource()
            sphere_source.SetCenter(x[i], y[i], 0.5)
            sphere_source.SetRadius(point_size)  # Sphere size is half of the value from the spinbox
            sphere_source.SetPhiResolution(20)
            sphere_source.SetThetaResolution(20)

            # Map the sphere to an actor
            sphere_mapper = vtk.vtkPolyDataMapper()
            sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())

            sphere_actor = vtk.vtkActor()
            sphere_actor.SetMapper(sphere_mapper)

            # Catheter point color (the point being edited in the edit point color)
            if current_ch is edit_ch and i == edit_pt:
                sphere_actor.GetProperty().SetColor(*style['edit_point'])
            else:
                sphere_actor.GetProperty().SetColor(*point_color)
            sphere_actor.GetProperty().SetOpacity(0.7)  # Full opacity

            # Add the actor for the sphere to the renderer
            renderer.AddActor(sphere_actor)
            self.channel_actors_sa.append(sphere_actor)

        # Create the polyline
        polyline = vtk.vtkPolyData()
        polyline.SetPoints(points)
        polyline.SetLines(lines)

        # Map the polyline to an actor
        polyline_mapper = vtk.vtkPolyDataMapper()
        polyline_mapper.SetInputData(polyline)

        polyline_actor = vtk.vtkActor()
        polyline_actor.SetMapper(polyline_mapper)
        polyline_actor.GetProperty().SetColor(*line_color)
        polyline_actor.GetProperty().SetLineWidth(style['ch_line_width'])

        # Add the polyline actor to the renderer (the path, if shown)
        if show['ch_path']:
            renderer.AddActor(polyline_actor)
            self.channel_actors_sa.append(polyline_actor)

        # Catheter name (its number unless renamed) next to its first point (tip)
        if show['ch_labels'] and len(x):
            label = brachy_label_actor(x[0], y[0], 0.5, catheter_label(current_ch, k), line_color, style['label_size'])
            renderer.AddActor(label)
            self.channel_actors_sa.append(label)

    # Render the updated display with the channels
    self.vtkWidgetSagittal.GetRenderWindow().Render()


def update_layer_view(self):
    if not hasattr(self, 'layer_selected') or self.layer_selected is None:
        return
    idx = self.layer_selected.currentIndex()
    tabName = self.tabModules.tabText(self.tabModules.currentIndex())
    if hasattr(self, 'layerTab'):
        self.layerTab[tabName] = idx
    if tabName == "Compare":
        if hasattr(self, '_comp_hist_dialog') and self._comp_hist_dialog is not None and self._comp_hist_dialog.isVisible():
            self._comp_hist_dialog.update_histogram()
        return
        
    if tabName != "segmentation":
        if idx in self.display_data and self.display_data[idx] is not None and self.slice_thick[idx] != 0:
            # Update the slider's value to match the current slice index
            Ax_s = self.current_axial_slice_index[idx]
            Sa_s = self.current_sagittal_slice_index[idx]
            Co_s = self.current_coronal_slice_index[idx]
            # check if the current slice is in the range of the layer
            Ax_s = max(0, min(Ax_s, self.display_data[idx].shape[0] - 1))
            Sa_s = max(0, min(Sa_s, self.display_data[idx].shape[2] - 1))
            Co_s = max(0, min(Co_s, self.display_data[idx].shape[1] - 1))
            
            # Update the sliders
            self.AxialSlider.setMaximum(self.display_data[idx].shape[0] - 1)
            self.SagittalSlider.setMaximum(self.display_data[idx].shape[2] - 1)
            self.CoronalSlider.setMaximum(self.display_data[idx].shape[1] - 1)
            
            self.AxialSlider.setValue(Ax_s)
            self.SagittalSlider.setValue(Sa_s)
            self.CoronalSlider.setValue(Co_s)

            # Explicitly refresh all 3 orthogonal views
            displayaxial(self)
            displaysagittal(self)
            displaycoronal(self)
            
            from fcn_init.view_hist import set_vtk_histogran_fig
            try:
                set_vtk_histogran_fig(self)
            except Exception as e:
                print(f"Error updating histogram: {e}")

        if hasattr(self, 'combo_colormap') and self.combo_colormap is not None and hasattr(self, 'CmapIDX'):
            if len(self.CmapIDX) > idx:
                self.combo_colormap.blockSignals(True)
                self.combo_colormap.setCurrentIndex(int(self.CmapIDX[idx]))
                self.combo_colormap.blockSignals(False)


def create_cross_actor(x_c, y_c, z_c, size, color, thickness=2.0):
    """
    Creates a VTK actor representing a 2D cross centered at (x_c, y_c, z_c).
    """
    line1 = vtk.vtkLineSource()
    line1.SetPoint1(x_c - size, y_c, z_c)
    line1.SetPoint2(x_c + size, y_c, z_c)
    
    line2 = vtk.vtkLineSource()
    line2.SetPoint1(x_c, y_c - size, z_c)
    line2.SetPoint2(x_c, y_c + size, z_c)
    
    append = vtk.vtkAppendPolyData()
    append.AddInputConnection(line1.GetOutputPort())
    append.AddInputConnection(line2.GetOutputPort())
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(append.GetOutputPort())
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color)
    actor.GetProperty().SetLineWidth(thickness)
    return actor


def brachy_label_actor(x, y, z, text, color, size):
    """Text next to a point (x, y, z) of a 2D view: a few pixels up and right of it, on top of the image."""
    anchor = vtk.vtkCoordinate()
    anchor.SetCoordinateSystemToWorld()
    anchor.SetValue(x, y, z)
    actor = vtk.vtkTextActor()
    actor.SetInput(text)
    position = actor.GetPositionCoordinate()
    position.SetCoordinateSystemToDisplay()
    position.SetReferenceCoordinate(anchor)
    position.SetValue(LABEL_OFFSET_PX, LABEL_OFFSET_PX)
    prop = actor.GetTextProperty()
    prop.SetFontSize(int(size))
    prop.SetColor(*color)
    prop.SetBold(True)
    prop.ShadowOn()
    return actor


def display_ref_points(self, view):
    """
    Crosses at the dose reference points ticked in the catheter list (brachy_tree), with
    their names when "names" is checked under Display. Colors and sizes come from the
    Style panel; the points in the current slice are drawn in the "in slice" color.
    """
    suffix = VIEW_SUFFIX[view]
    widget = getattr(self, dict(VIEW_WIDGETS)[view])
    renderer = widget.GetRenderWindow().GetRenderers().GetFirstRenderer()
    actors = getattr(self, 'ref_point_actors_' + suffix, None)
    if actors is None:
        actors = []
        setattr(self, 'ref_point_actors_' + suffix, actors)
    for actor in actors:
        renderer.RemoveActor(actor)
    actors.clear()

    try:
        meta = self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']
        ref_points = meta.get('Plan_Dose_References') or []
    except (KeyError, IndexError, TypeError):
        ref_points = []
    # (index, point, coordinates) of the points shown that have coordinates
    shown = [(k, pt, ref_point_xyz(pt)) for k, pt in enumerate(ref_points) if ref_point_visible(pt)]
    shown = [item for item in shown if item[2] is not None]
    if shown:
        style, labels = brachy_style(self), brachy_display(self)['ref_labels']
        xyz = np.array([item[2] for item in shown])
        xy = view_xy(view, xyz, self.Im_PatPosition[0], self.display_data[0].shape[1] * self.pixel_spac[0, 0])
        # in the current slice: within half a voxel of it along the view normal
        axis = NORMAL_AXIS[view]
        half = (self.pixel_spac[0, 1], self.pixel_spac[0, 0], self.slice_thick[0])[axis] / 2
        in_slice = np.abs(xyz[:, axis] - _slice_point(self)[axis]) <= half
        z = 0.7 + style['ch_point_size'] / 2  # above the dwells
        for (k, pt, _xyz), (x, y), here in zip(shown, xy, in_slice):
            color = style['ref_slice'] if here else style['ref_other']
            actors.append(create_cross_actor(x, y, z, style['ref_size'] / 2, color, style['ref_width']))
            if labels:
                actors.append(brachy_label_actor(x, y, z, ref_point_name(pt, k), color, style['label_size']))
        for actor in actors:
            renderer.AddActor(actor)

    widget.GetRenderWindow().Render()


def display_ref_points_ax(self):
    display_ref_points(self, 'axial')


def display_ref_points_co(self):
    display_ref_points(self, 'coronal')


def display_ref_points_sa(self):
    display_ref_points(self, 'sagittal')


def _compute_ebrt_beam_3d_geom(beam):
    """
    Computes 3D geometry coordinates (in DICOM patient space) for an EBRT beam:
    - Isocenter position
    - Central Axis (CAX) entry and exit endpoints (Start and End if Arc)
    - Collimator jaw aperture corners at isocenter distance (SAD)
    - 4 Diverging boundary rays from entry to exit
    - Arc circular trajectory around the patient if dynamic / arc
    """
    iso = np.array(beam.get('Isocenter', [0.0, 0.0, 0.0]), dtype=float)
    g_deg = float(beam.get('GantryAngleStart', 0.0))
    g_end_deg = float(beam.get('GantryAngleEnd', g_deg))
    g_dir = str(beam.get('GantryDirection', 'NONE')).upper()
    c_deg = float(beam.get('CouchAngle', 0.0))
    col_deg = float(beam.get('CollimatorAngle', 0.0))
    sad = float(beam.get('SAD', 1000.0) or 1000.0)
    jaw_x = beam.get('JawX', [-50.0, 50.0])
    jaw_y = beam.get('JawY', [-50.0, 50.0])

    g_rad = np.radians(g_deg)
    c_rad = np.radians(c_deg)
    col_rad = np.radians(col_deg)

    # Unit vectors in DICOM IEC space for Start field
    u_beam = np.array([-np.sin(g_rad) * np.cos(c_rad), np.cos(g_rad), -np.sin(g_rad) * np.sin(c_rad)], dtype=float)
    u_cross = np.array([np.cos(g_rad), np.sin(g_rad), 0.0], dtype=float)
    u_long = np.array([0.0, 0.0, 1.0], dtype=float)

    e_x = np.cos(col_rad) * u_cross + np.sin(col_rad) * u_long
    e_y = -np.sin(col_rad) * u_cross + np.cos(col_rad) * u_long

    S = iso - sad * u_beam

    def _corner_pts(d):
        scale = d / sad
        p1 = S + d * u_beam + scale * (jaw_x[0] * e_x + jaw_y[1] * e_y) # Top-Left
        p2 = S + d * u_beam + scale * (jaw_x[1] * e_x + jaw_y[1] * e_y) # Top-Right
        p3 = S + d * u_beam + scale * (jaw_x[1] * e_x + jaw_y[0] * e_y) # Bottom-Right
        p4 = S + d * u_beam + scale * (jaw_x[0] * e_x + jaw_y[0] * e_y) # Bottom-Left
        return [p1, p2, p3, p4]

    d_ent = min(sad, max(sad - 250.0, 400.0))
    d_exit = sad + 200.0

    cax_entry = S + d_ent * u_beam
    cax_exit = S + d_exit * u_beam

    iso_corners = _corner_pts(sad)
    entry_corners = _corner_pts(d_ent)
    exit_corners = _corner_pts(d_exit)

    geom = {
        'Isocenter': iso,
        'CAX': (cax_entry, cax_exit),
        'IsoCorners': iso_corners,
        'EntryCorners': entry_corners,
        'ExitCorners': exit_corners,
        'Rays': [
            (entry_corners[0], exit_corners[0]),
            (entry_corners[1], exit_corners[1]),
            (entry_corners[2], exit_corners[2]),
            (entry_corners[3], exit_corners[3]),
        ],
        'IsArc': False
    }

    # Check if beam is an Arc (VMAT / Dynamic Arc / Conformal Arc)
    is_arc = (beam.get('BeamType') == 'DYNAMIC' or abs(g_end_deg - g_deg) > 0.1 or g_dir in ['CW', 'CCW']) and (g_dir != 'NONE' or abs(g_end_deg - g_deg) > 0.5)

    if is_arc:
        geom['IsArc'] = True
        if g_dir == 'CW':
            span = (g_end_deg - g_deg) if (g_end_deg > g_deg) else ((360.0 - g_deg) + g_end_deg if g_end_deg < g_deg else 360.0)
            n_steps = max(int(span / 2.0), 25)
            arc_angles = (g_deg + np.linspace(0.0, span, n_steps)) % 360.0
        elif g_dir == 'CCW':
            span = (g_deg - g_end_deg) if (g_deg > g_end_deg) else ((360.0 - g_end_deg) + g_deg if g_deg < g_end_deg else 360.0)
            n_steps = max(int(span / 2.0), 25)
            arc_angles = (g_deg - np.linspace(0.0, span, n_steps)) % 360.0
        else:
            diff = g_end_deg - g_deg
            n_steps = max(int(abs(diff) / 2.0), 25)
            arc_angles = np.linspace(g_deg, g_end_deg, n_steps)

        # Generate smooth circular arc trajectory at R = 350 mm around isocenter (around the patient body)
        r_arc = 350.0
        arc_pts = []
        for a in arc_angles:
            a_rad = np.radians(a)
            u_a = np.array([-np.sin(a_rad) * np.cos(c_rad), np.cos(a_rad), -np.sin(a_rad) * np.sin(c_rad)], dtype=float)
            arc_pts.append(iso - r_arc * u_a)
        geom['ArcTrajectory'] = arc_pts

    return geom


def _create_vtk_line_actor(p1, p2, color, line_width=2, opacity=0.9, stipple=False):
    """Helper to create a VTK line actor between two points in display coordinates."""
    pts = vtk.vtkPoints()
    pts.InsertNextPoint(p1[0], p1[1], p1[2] if len(p1) > 2 else 0.6)
    pts.InsertNextPoint(p2[0], p2[1], p2[2] if len(p2) > 2 else 0.6)
    
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(2, [0, 1])
    
    pd = vtk.vtkPolyData()
    pd.SetPoints(pts)
    pd.SetLines(lines)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(pd)
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color[0], color[1], color[2])
    actor.GetProperty().SetLineWidth(line_width)
    actor.GetProperty().SetOpacity(opacity)
    if stipple:
        actor.GetProperty().SetLineStipplePattern(0xF0F0)
    return actor


def _create_vtk_polyline_actor(pts, color, line_width=3, opacity=0.9, stipple=False):
    """Helper to create a VTK open polyline actor connecting a sequence of 2D/3D points."""
    vtk_pts = vtk.vtkPoints()
    n = len(pts)
    if n < 2:
        return None
    for p in pts:
        vtk_pts.InsertNextPoint(p[0], p[1], p[2] if len(p) > 2 else 0.6)
        
    lines = vtk.vtkCellArray()
    for i in range(n - 1):
        lines.InsertNextCell(2, [i, i + 1])
        
    pd = vtk.vtkPolyData()
    pd.SetPoints(vtk_pts)
    pd.SetLines(lines)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(pd)
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color[0], color[1], color[2])
    actor.GetProperty().SetLineWidth(line_width)
    actor.GetProperty().SetOpacity(opacity)
    if stipple:
        actor.GetProperty().SetLineStipplePattern(0xAAAA)
    return actor


def _create_vtk_arrow_actor(p_end, p_prev, color, arrow_len=14.0, line_width=3.0, opacity=1.0):
    """Creates an arrowhead at p_end pointing along (p_end - p_prev)."""
    dx = p_end[0] - p_prev[0]
    dy = p_end[1] - p_prev[1]
    norm = np.hypot(dx, dy)
    if norm < 1e-3:
        return None
    u_t = np.array([dx / norm, dy / norm])
    u_n = np.array([-u_t[1], u_t[0]])
    
    w1 = np.array(p_end[:2]) - arrow_len * u_t + 0.5 * arrow_len * u_n
    w2 = np.array(p_end[:2]) - arrow_len * u_t - 0.5 * arrow_len * u_n
    
    pts = vtk.vtkPoints()
    pts.InsertNextPoint(w1[0], w1[1], 0.7)
    pts.InsertNextPoint(p_end[0], p_end[1], 0.7)
    pts.InsertNextPoint(w2[0], w2[1], 0.7)
    
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(2, [0, 1])
    lines.InsertNextCell(2, [1, 2])
    
    pd = vtk.vtkPolyData()
    pd.SetPoints(pts)
    pd.SetLines(lines)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(pd)
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color[0], color[1], color[2])
    actor.GetProperty().SetLineWidth(line_width)
    actor.GetProperty().SetOpacity(opacity)
    return actor


def _create_vtk_closed_polygon_actor(pts_2d, color, line_width=2, opacity=0.85, stipple=False):
    """Helper to create a closed polygon outline actor connecting a sequence of 2D points."""
    pts = vtk.vtkPoints()
    n = len(pts_2d)
    for p in pts_2d:
        pts.InsertNextPoint(p[0], p[1], 0.6)
        
    lines = vtk.vtkCellArray()
    for i in range(n):
        lines.InsertNextCell(2, [i, (i + 1) % n])
        
    pd = vtk.vtkPolyData()
    pd.SetPoints(pts)
    pd.SetLines(lines)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(pd)
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color[0], color[1], color[2])
    actor.GetProperty().SetLineWidth(line_width)
    actor.GetProperty().SetOpacity(opacity)
    if stipple:
        actor.GetProperty().SetLineStipplePattern(0xF0F0)
    return actor


def _create_vtk_crosshair_actor(center_x, center_y, color, size=10.0, line_width=3, opacity=1.0):
    """Helper to create an isocenter crosshair actor."""
    pts = vtk.vtkPoints()
    pts.InsertNextPoint(center_x - size, center_y, 0.7)
    pts.InsertNextPoint(center_x + size, center_y, 0.7)
    pts.InsertNextPoint(center_x, center_y - size, 0.7)
    pts.InsertNextPoint(center_x, center_y + size, 0.7)
    
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(2, [0, 1])
    lines.InsertNextCell(2, [2, 3])
    
    pd = vtk.vtkPolyData()
    pd.SetPoints(pts)
    pd.SetLines(lines)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(pd)
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color[0], color[1], color[2])
    actor.GetProperty().SetLineWidth(line_width)
    actor.GetProperty().SetOpacity(opacity)
    return actor


def display_ebrt_fields_ax(self):
    """
    Renders 2D EBRT beam geometries (isocenter, central axis, field boundaries, and Arc trajectory)
    on the Axial viewport for the current slice.
    """
    if not hasattr(self, 'vtkWidgetAxial') or not hasattr(self, 'ebrt_beams_data'):
        return
    renderer = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()
    if renderer is None:
        return

    # Clear previous axial EBRT actors
    for actor in getattr(self, 'ebrt_actors_ax', []):
        renderer.RemoveActor(actor)
    self.ebrt_actors_ax.clear()

    if not self.ebrt_beams_data or not hasattr(self, 'display_data') or not self.display_data:
        return

    curr_slice_idx = self.current_axial_slice_index[0]
    curr_z = self.Im_PatPosition[0, 2] + curr_slice_idx * self.slice_thick[0]

    show_iso = getattr(self, 'display_ebrt_isocenter', None) is None or self.display_ebrt_isocenter.isChecked()
    show_cax = getattr(self, 'display_ebrt_cax', None) is None or self.display_ebrt_cax.isChecked()
    show_fan = getattr(self, 'display_ebrt_beam_fan', None) is None or self.display_ebrt_beam_fan.isChecked()

    def to_vtk_ax(p):
        vx = p[0] - self.Im_PatPosition[0, 0] + self.Im_Offset[0, 0]
        vy = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - (p[1] - self.Im_PatPosition[0, 1]) + self.Im_Offset[0, 1]
        return vx, vy

    for beam in self.ebrt_beams_data:
        if not beam.get('Visible', True):
            continue

        qcol = QColor(beam.get('Color', '#e53935'))
        color = (qcol.redF(), qcol.greenF(), qcol.blueF())

        geom = _compute_ebrt_beam_3d_geom(beam)
        iso = geom['Isocenter']
        iso_dist_z = abs(curr_z - iso[2])
        is_near_iso = (iso_dist_z <= max(self.slice_thick[0] * 2.0, 4.0))

        # 1. Isocenter Crosshair
        if show_iso:
            ivx, ivy = to_vtk_ax(iso)
            op = 1.0 if is_near_iso else 0.5
            lw = 4 if is_near_iso else 2
            sz = 13.0 if is_near_iso else 8.0
            act_iso = _create_vtk_crosshair_actor(ivx, ivy, color, size=sz, line_width=lw, opacity=op)
            renderer.AddActor(act_iso)
            self.ebrt_actors_ax.append(act_iso)

        # 2. Central Axis (CAX) - Start field
        if show_cax:
            p1_v = to_vtk_ax(geom['CAX'][0])
            p2_v = to_vtk_ax(geom['CAX'][1])
            cax_len = np.hypot(p2_v[0] - p1_v[0], p2_v[1] - p1_v[1])
            if cax_len > 2.0:
                act_cax = _create_vtk_line_actor(p1_v, p2_v, color, line_width=3.0, opacity=0.95, stipple=False)
                renderer.AddActor(act_cax)
                self.ebrt_actors_ax.append(act_cax)

        # 3. Field Outline & Boundary Rays - Start field
        if show_fan:
            for r_entry, r_exit in geom['Rays']:
                p_s = to_vtk_ax(r_entry)
                p_e = to_vtk_ax(r_exit)
                ray_len = np.hypot(p_e[0] - p_s[0], p_e[1] - p_s[1])
                if ray_len > 2.0:
                    act_ray = _create_vtk_line_actor(p_s, p_e, color, line_width=2.0, opacity=0.85, stipple=True)
                    renderer.AddActor(act_ray)
                    self.ebrt_actors_ax.append(act_ray)

            iso_2d_corners = [to_vtk_ax(c) for c in geom['IsoCorners']]
            diag = np.hypot(iso_2d_corners[2][0] - iso_2d_corners[0][0], iso_2d_corners[2][1] - iso_2d_corners[0][1])
            if diag > 2.0:
                act_box = _create_vtk_closed_polygon_actor(iso_2d_corners, color, line_width=2.8, opacity=1.0 if is_near_iso else 0.6)
                renderer.AddActor(act_box)
                self.ebrt_actors_ax.append(act_box)

        # 4. Arc Trajectory around the patient
        if geom.get('IsArc', False):
            arc_3d = geom.get('ArcTrajectory', [])
            if len(arc_3d) >= 2:
                arc_2d = [to_vtk_ax(p) for p in arc_3d]
                act_arc = _create_vtk_polyline_actor(arc_2d, color, line_width=3.2, opacity=0.95)
                if act_arc:
                    renderer.AddActor(act_arc)
                    self.ebrt_actors_ax.append(act_arc)

                # Arrowhead at end of arc indicating rotation direction
                act_arrow = _create_vtk_arrow_actor(arc_2d[-1], arc_2d[-2], color, arrow_len=14.0, line_width=3.0, opacity=1.0)
                if act_arrow:
                    renderer.AddActor(act_arrow)
                    self.ebrt_actors_ax.append(act_arrow)

    self.vtkWidgetAxial.GetRenderWindow().Render()


def display_ebrt_fields_co(self):
    """
    Renders 2D EBRT beam geometries on the Coronal viewport for the current slice.
    """
    if not hasattr(self, 'vtkWidgetCoronal') or not hasattr(self, 'ebrt_beams_data'):
        return
    renderer = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()
    if renderer is None:
        return

    for actor in getattr(self, 'ebrt_actors_co', []):
        renderer.RemoveActor(actor)
    self.ebrt_actors_co.clear()

    if not self.ebrt_beams_data or not hasattr(self, 'display_data') or not self.display_data:
        return

    curr_slice_idx = self.current_coronal_slice_index[0]
    curr_y = self.Im_PatPosition[0, 1] + (self.display_data[0].shape[1] - 1 - curr_slice_idx) * self.pixel_spac[0, 0]

    show_iso = getattr(self, 'display_ebrt_isocenter', None) is None or self.display_ebrt_isocenter.isChecked()
    show_cax = getattr(self, 'display_ebrt_cax', None) is None or self.display_ebrt_cax.isChecked()
    show_fan = getattr(self, 'display_ebrt_beam_fan', None) is None or self.display_ebrt_beam_fan.isChecked()

    def to_vtk_co(p):
        vx = p[0] - self.Im_PatPosition[0, 0] + self.Im_Offset[0, 0]
        vy = p[2] - self.Im_PatPosition[0, 2] + self.Im_Offset[0, 2]
        return vx, vy

    for beam in self.ebrt_beams_data:
        if not beam.get('Visible', True):
            continue

        qcol = QColor(beam.get('Color', '#e53935'))
        color = (qcol.redF(), qcol.greenF(), qcol.blueF())

        geom = _compute_ebrt_beam_3d_geom(beam)
        iso = geom['Isocenter']
        iso_dist_y = abs(curr_y - iso[1])
        is_near_iso = (iso_dist_y <= max(self.pixel_spac[0, 0] * 2.0, 4.0))

        # 1. Isocenter Crosshair
        if show_iso:
            ivx, ivy = to_vtk_co(iso)
            op = 1.0 if is_near_iso else 0.5
            lw = 4 if is_near_iso else 2
            sz = 13.0 if is_near_iso else 8.0
            act_iso = _create_vtk_crosshair_actor(ivx, ivy, color, size=sz, line_width=lw, opacity=op)
            renderer.AddActor(act_iso)
            self.ebrt_actors_co.append(act_iso)

        # 2. Central Axis (CAX)
        if show_cax:
            p1_v = to_vtk_co(geom['CAX'][0])
            p2_v = to_vtk_co(geom['CAX'][1])
            cax_len = np.hypot(p2_v[0] - p1_v[0], p2_v[1] - p1_v[1])
            if cax_len > 2.0:
                act_cax = _create_vtk_line_actor(p1_v, p2_v, color, line_width=3.0, opacity=0.95, stipple=False)
                renderer.AddActor(act_cax)
                self.ebrt_actors_co.append(act_cax)

        # 3. Field Outline & Boundary Rays
        if show_fan:
            for r_entry, r_exit in geom['Rays']:
                p_s = to_vtk_co(r_entry)
                p_e = to_vtk_co(r_exit)
                ray_len = np.hypot(p_e[0] - p_s[0], p_e[1] - p_s[1])
                if ray_len > 2.0:
                    act_ray = _create_vtk_line_actor(p_s, p_e, color, line_width=2.0, opacity=0.85, stipple=True)
                    renderer.AddActor(act_ray)
                    self.ebrt_actors_co.append(act_ray)

            iso_2d_corners = [to_vtk_co(c) for c in geom['IsoCorners']]
            diag = np.hypot(iso_2d_corners[2][0] - iso_2d_corners[0][0], iso_2d_corners[2][1] - iso_2d_corners[0][1])
            if diag > 2.0:
                act_box = _create_vtk_closed_polygon_actor(iso_2d_corners, color, line_width=2.8, opacity=1.0 if is_near_iso else 0.6)
                renderer.AddActor(act_box)
                self.ebrt_actors_co.append(act_box)

        # 4. Arc Trajectory
        if geom.get('IsArc', False):
            arc_3d = geom.get('ArcTrajectory', [])
            if len(arc_3d) >= 2:
                arc_2d = [to_vtk_co(p) for p in arc_3d]
                act_arc = _create_vtk_polyline_actor(arc_2d, color, line_width=3.2, opacity=0.95)
                if act_arc:
                    renderer.AddActor(act_arc)
                    self.ebrt_actors_co.append(act_arc)

    self.vtkWidgetCoronal.GetRenderWindow().Render()


def display_ebrt_fields_sa(self):
    """
    Renders 2D EBRT beam geometries on the Sagittal viewport for the current slice.
    """
    if not hasattr(self, 'vtkWidgetSagittal') or not hasattr(self, 'ebrt_beams_data'):
        return
    renderer = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()
    if renderer is None:
        return

    for actor in getattr(self, 'ebrt_actors_sa', []):
        renderer.RemoveActor(actor)
    self.ebrt_actors_sa.clear()

    if not self.ebrt_beams_data or not hasattr(self, 'display_data') or not self.display_data:
        return

    curr_slice_idx = self.current_sagittal_slice_index[0]
    curr_x = self.Im_PatPosition[0, 0] + curr_slice_idx * self.pixel_spac[0, 1]

    show_iso = getattr(self, 'display_ebrt_isocenter', None) is None or self.display_ebrt_isocenter.isChecked()
    show_cax = getattr(self, 'display_ebrt_cax', None) is None or self.display_ebrt_cax.isChecked()
    show_fan = getattr(self, 'display_ebrt_beam_fan', None) is None or self.display_ebrt_beam_fan.isChecked()

    def to_vtk_sa(p):
        vx = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - (p[1] - self.Im_PatPosition[0, 1]) + self.Im_Offset[0, 1]
        vy = p[2] - self.Im_PatPosition[0, 2] + self.Im_Offset[0, 2]
        return vx, vy

    for beam in self.ebrt_beams_data:
        if not beam.get('Visible', True):
            continue

        qcol = QColor(beam.get('Color', '#e53935'))
        color = (qcol.redF(), qcol.greenF(), qcol.blueF())

        geom = _compute_ebrt_beam_3d_geom(beam)
        iso = geom['Isocenter']
        iso_dist_x = abs(curr_x - iso[0])
        is_near_iso = (iso_dist_x <= max(self.pixel_spac[0, 1] * 2.0, 4.0))

        # 1. Isocenter Crosshair
        if show_iso:
            ivx, ivy = to_vtk_sa(iso)
            op = 1.0 if is_near_iso else 0.5
            lw = 4 if is_near_iso else 2
            sz = 13.0 if is_near_iso else 8.0
            act_iso = _create_vtk_crosshair_actor(ivx, ivy, color, size=sz, line_width=lw, opacity=op)
            renderer.AddActor(act_iso)
            self.ebrt_actors_sa.append(act_iso)

        # 2. Central Axis (CAX)
        if show_cax:
            p1_v = to_vtk_sa(geom['CAX'][0])
            p2_v = to_vtk_sa(geom['CAX'][1])
            cax_len = np.hypot(p2_v[0] - p1_v[0], p2_v[1] - p1_v[1])
            if cax_len > 2.0:
                act_cax = _create_vtk_line_actor(p1_v, p2_v, color, line_width=3.0, opacity=0.95, stipple=False)
                renderer.AddActor(act_cax)
                self.ebrt_actors_sa.append(act_cax)

        # 3. Field Outline & Boundary Rays
        if show_fan:
            for r_entry, r_exit in geom['Rays']:
                p_s = to_vtk_sa(r_entry)
                p_e = to_vtk_sa(r_exit)
                ray_len = np.hypot(p_e[0] - p_s[0], p_e[1] - p_s[1])
                if ray_len > 2.0:
                    act_ray = _create_vtk_line_actor(p_s, p_e, color, line_width=2.0, opacity=0.85, stipple=True)
                    renderer.AddActor(act_ray)
                    self.ebrt_actors_sa.append(act_ray)

            iso_2d_corners = [to_vtk_sa(c) for c in geom['IsoCorners']]
            diag = np.hypot(iso_2d_corners[2][0] - iso_2d_corners[0][0], iso_2d_corners[2][1] - iso_2d_corners[0][1])
            if diag > 2.0:
                act_box = _create_vtk_closed_polygon_actor(iso_2d_corners, color, line_width=2.8, opacity=1.0 if is_near_iso else 0.6)
                renderer.AddActor(act_box)
                self.ebrt_actors_sa.append(act_box)

        # 4. Arc Trajectory
        if geom.get('IsArc', False):
            arc_3d = geom.get('ArcTrajectory', [])
            if len(arc_3d) >= 2:
                arc_2d = [to_vtk_sa(p) for p in arc_3d]
                act_arc = _create_vtk_polyline_actor(arc_2d, color, line_width=3.2, opacity=0.95)
                if act_arc:
                    renderer.AddActor(act_arc)
                    self.ebrt_actors_sa.append(act_arc)

    self.vtkWidgetSagittal.GetRenderWindow().Render()
