import time

def sliderCompareView_change(self):
    disp_comp_image_slice(self)


def map_comp_slice(self, from_idx, to_idx, layer_from, layer_to, s_from):
    """
    Map slice index `s_from` of comparison axis `from_idx` at `layer_from` 
    to comparison axis `to_idx` at `layer_to` based on physical coordinates.
    """
    if (from_idx, layer_from) not in self.display_comp_data or (to_idx, layer_to) not in self.display_comp_data:
        return s_from # fallback
        
    ori_from = int(self.im_ori_comp[from_idx])
    ori_to = int(self.im_ori_comp[to_idx])
    
    if ori_from != ori_to:
        return s_from # fallback
        
    pos_from = self.Im_PatPosition_comp[from_idx, layer_from]
    pos_to = self.Im_PatPosition_comp[to_idx, layer_to]
    
    shape_from = self.display_comp_data[from_idx, layer_from].shape
    shape_to = self.display_comp_data[to_idx, layer_to].shape
    
    if ori_from == 0: # Axial (Z coordinate)
        thick_from = self.slice_thick_comp[from_idx, layer_from]
        thick_to = self.slice_thick_comp[to_idx, layer_to]
        if thick_to == 0:
            return s_from
        z_mm = pos_from[2] + s_from * thick_from
        s_to = int(round((z_mm - pos_to[2]) / thick_to))
        return max(0, min(s_to, shape_to[0] - 1))
        
    elif ori_from == 1: # Sagittal (X coordinate)
        spac_from = self.pixel_spac_comp[from_idx, layer_from, 1]
        spac_to = self.pixel_spac_comp[to_idx, layer_to, 1]
        if spac_to == 0:
            return s_from
        x_mm = pos_from[0] + s_from * spac_from
        s_to = int(round((x_mm - pos_to[0]) / spac_to))
        return max(0, min(s_to, shape_to[2] - 1))
        
    else: # Coronal (Y coordinate)
        spac_from = self.pixel_spac_comp[from_idx, layer_from, 0]
        spac_to = self.pixel_spac_comp[to_idx, layer_to, 0]
        if spac_to == 0:
            return s_from
        y_mm = pos_from[1] + (shape_from[1] - s_from) * spac_from
        s_to = int(round(shape_to[1] - (y_mm - pos_to[1]) / spac_to))
        return max(0, min(s_to, shape_to[1] - 1))


def change_comp_view_orientation(self, new_ori):
    if new_ori < 0:
        return
    layer = self.layer_selected.currentIndex()
    ref_idx = self.Comp_im_idx.value()
    
    if self.Comp_linkSlices.isChecked():
        viewports = list(range(0, self.Comp_im_idx.maximum() + 1))
    else:
        viewports = [ref_idx]
        
    for Ax_idx in viewports:
        self.im_ori_comp[Ax_idx] = new_ori
        
        # Reset slice index for all active layers in this viewport
        for l_idx in range(4):
            if (Ax_idx, l_idx) in self.display_comp_data:
                shape = self.display_comp_data[Ax_idx, l_idx].shape
                if new_ori == 0:
                    self.current_AxComp_slice_index[Ax_idx, l_idx] = shape[0] // 2
                elif new_ori == 1:
                    self.current_AxComp_slice_index[Ax_idx, l_idx] = shape[2] // 2
                else:
                    self.current_AxComp_slice_index[Ax_idx, l_idx] = shape[1] // 2
                    
    # Update slider limits based on active viewport
    if (ref_idx, layer) in self.display_comp_data:
        shape = self.display_comp_data[ref_idx, layer].shape
        limit = shape[0] if new_ori == 0 else (shape[2] if new_ori == 1 else shape[1])
        self.SliderCompareView.blockSignals(True)
        self.SliderCompareView.setMaximum(limit - 1)
        self.SliderCompareView.setValue(int(self.current_AxComp_slice_index[ref_idx, layer]))
        self.SliderCompareView.blockSignals(False)
        
    disp_comp_image_slice(self)


def sync_comp_dropdown_to_viewport(self, idx):
    if idx < 0:
        return
    if hasattr(self, 'im_ori_comp') and idx < len(self.im_ori_comp):
        ori = int(self.im_ori_comp[idx])
        self.Comp_view_sel_box.blockSignals(True)
        self.Comp_view_sel_box.setCurrentIndex(ori)
        self.Comp_view_sel_box.blockSignals(False)
        
    # Refresh open Compare Histogram popup
    if hasattr(self, '_comp_hist_dialog') and self._comp_hist_dialog is not None and self._comp_hist_dialog.isVisible():
        self._comp_hist_dialog.update_histogram()

    # Sync transparency sliders to the selected viewport's recorded opacities
    if not hasattr(self, 'CompLayerAlpha'):
        self.CompLayerAlpha = {}
    for l_idx in range(4):
        opacity = self.CompLayerAlpha.get((idx, l_idx), 1.0 if l_idx == 0 else 0.5)
        self.CompLayerAlpha[idx, l_idx] = opacity
        self.LayerAlpha[l_idx] = opacity
        
        slider = getattr(self, f"Layer_{l_idx}_alpha_sli")
        spin = getattr(self, f"Layer_{l_idx}_alpha_spin")
        
        slider.blockSignals(True)
        slider.setValue(int(opacity * 100))
        slider.blockSignals(False)
        
        spin.blockSignals(True)
        spin.setValue(opacity)
        spin.blockSignals(False)


def disp_comp_image_slice(self):
    active_layer = int(self.layer_selected.currentIndex())
    ref_idx = self.Comp_im_idx.value()
    
    if self.Comp_linkSlices.isChecked():
        r_1 = 0
        r_2 = self.Comp_im_idx.maximum() + 1
    else:
        r_1 = ref_idx
        r_2 = r_1 + 1
        
    if not hasattr(self, 'CompLayerAlpha'):
        self.CompLayerAlpha = {}
        
    for Ax_idx in range(r_1, r_2):
        # Update and blend all 4 layers for this viewport
        for l_idx in range(4):
            if (Ax_idx, l_idx) not in self.display_comp_data:
                if hasattr(self, 'imageActorAxComp') and (Ax_idx, l_idx) in self.imageActorAxComp:
                    self.imageActorAxComp[Ax_idx, l_idx].GetProperty().SetOpacity(0)
                continue
                
            # Align layer slice index physically
            if self.Comp_linkSlices.isChecked() and Ax_idx != ref_idx:
                self.current_AxComp_slice_index[Ax_idx, l_idx] = map_comp_slice(self, ref_idx, Ax_idx, active_layer, l_idx, self.SliderCompareView.value())
            else:
                if Ax_idx == ref_idx:
                    if l_idx == active_layer:
                        self.current_AxComp_slice_index[Ax_idx, l_idx] = self.SliderCompareView.value()
                    else:
                        self.current_AxComp_slice_index[Ax_idx, l_idx] = map_comp_slice(self, ref_idx, ref_idx, active_layer, l_idx, self.SliderCompareView.value())
                else:
                    self.current_AxComp_slice_index[Ax_idx, l_idx] = self.SliderCompareView.value()
                    
            ori = int(self.im_ori_comp[Ax_idx])
            axis = 2 if ori == 1 else (1 if ori == 2 else 0)
            
            if not (0 <= int(self.current_AxComp_slice_index[Ax_idx, l_idx]) < self.display_comp_data[Ax_idx, l_idx].shape[axis]):
                self.imageActorAxComp[Ax_idx, l_idx].GetProperty().SetOpacity(0)
                continue
                
            if ori == 0: # Axial
                slice_data = self.display_comp_data[Ax_idx, l_idx][int(self.current_AxComp_slice_index[Ax_idx, l_idx]), :, :]
                self.imageActorAxComp[Ax_idx, l_idx].SetPosition(self.Im_Offset_comp[Ax_idx, l_idx, 0], self.Im_Offset_comp[Ax_idx, l_idx, 1], 0)
                self.dataImporterAxComp[Ax_idx, l_idx].SetDataSpacing(self.pixel_spac_comp[Ax_idx, l_idx, 1], self.pixel_spac_comp[Ax_idx, l_idx, 0], 1)
            elif ori == 1: # Sagittal
                slice_data = self.display_comp_data[Ax_idx, l_idx][:, :, int(self.current_AxComp_slice_index[Ax_idx, l_idx])]
                self.imageActorAxComp[Ax_idx, l_idx].SetPosition(self.Im_Offset_comp[Ax_idx, l_idx, 1], self.Im_Offset_comp[Ax_idx, l_idx, 2], 0)
                self.dataImporterAxComp[Ax_idx, l_idx].SetDataSpacing(self.pixel_spac_comp[Ax_idx, l_idx, 0], self.slice_thick_comp[Ax_idx, l_idx], 1)
            else: # Coronal
                slice_data = self.display_comp_data[Ax_idx, l_idx][:, int(self.current_AxComp_slice_index[Ax_idx, l_idx]), :]
                self.imageActorAxComp[Ax_idx, l_idx].SetPosition(self.Im_Offset_comp[Ax_idx, l_idx, 0], self.Im_Offset_comp[Ax_idx, l_idx, 2], 0)
                self.dataImporterAxComp[Ax_idx, l_idx].SetDataSpacing(self.pixel_spac_comp[Ax_idx, l_idx, 1], self.slice_thick_comp[Ax_idx, l_idx], 1)
                
            data_string = slice_data.tobytes()
            extent = slice_data.shape
            self.dataImporterAxComp[Ax_idx, l_idx].CopyImportVoidPointer(data_string, len(data_string))
            self.dataImporterAxComp[Ax_idx, l_idx].SetWholeExtent(0, extent[1] - 1, 0, extent[0] - 1, 0, 0)
            self.dataImporterAxComp[Ax_idx, l_idx].SetDataExtent(0, extent[1] - 1, 0, extent[0] - 1, 0, 0)
            
            if l_idx == active_layer:
                self.textActorAxCom[Ax_idx, 2].SetInput(f"Slice:{self.current_AxComp_slice_index[Ax_idx, l_idx]}")
                
            opacity = self.CompLayerAlpha.get((Ax_idx, l_idx), 1.0 if l_idx == 0 else 0.5)
            self.CompLayerAlpha[Ax_idx, l_idx] = opacity
            
            imageProperty = self.imageActorAxComp[Ax_idx, l_idx].GetProperty()
            imageProperty.SetOpacity(opacity)
            self.dataImporterAxComp[Ax_idx, l_idx].Modified()
            
        disp_structure_overlay_comp(self, Ax_idx)
        self.renAxComp[Ax_idx].GetRenderWindow().Render()


from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import vtk
import numpy as np

class CompareStructuresDialog(QtWidgets.QDialog):
    def __init__(self, parent_app, series_dict, series_keys, parent=None):
        super().__init__(parent or parent_app)
        self.parent_app = parent_app
        self.series_dict = series_dict
        self.series_keys = series_keys # (patientID, studyID, modality, series_index)
        
        self.setWindowTitle(f"Compare Tab Structures - {series_dict['metadata']['DCM_Info'].get('SeriesDescription', 'Series')}")
        self.resize(750, 450)
        
        # Layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # QListWidget
        self.list_widget = QtWidgets.QListWidget(self)
        self.layout.addWidget(self.list_widget)
        
        self.populate_list()

    def _ensure_array(self, key, n, default_value):
        app = self.parent_app
        Ax_idx = app.Comp_im_idx.value()
        
        if not hasattr(app, 'Comp_linkContours') or app.Comp_linkContours.isChecked():
            # Synced / Global Mode
            arr = self.series_dict.get(key)
            if not isinstance(arr, list):
                arr = []
            if len(arr) < n:
                arr = arr + [default_value] * (n - len(arr))
            elif len(arr) > n:
                arr = arr[:n]
            self.series_dict[key] = arr
            
            # Keep active viewport's override dictionary in sync
            if not hasattr(app, 'comp_viewport_structures'):
                app.comp_viewport_structures = {}
            if Ax_idx not in app.comp_viewport_structures:
                app.comp_viewport_structures[Ax_idx] = {}
            app.comp_viewport_structures[Ax_idx][key] = arr
            
            return arr
        else:
            # Viewport-Specific Mode
            if not hasattr(app, 'comp_viewport_structures'):
                app.comp_viewport_structures = {}
            if Ax_idx not in app.comp_viewport_structures:
                app.comp_viewport_structures[Ax_idx] = {}
                
            viewport_dict = app.comp_viewport_structures[Ax_idx]
            arr = viewport_dict.get(key)
            if not isinstance(arr, list):
                global_arr = self.series_dict.get(key)
                if isinstance(global_arr, list):
                    arr = list(global_arr)
                else:
                    arr = []
            if len(arr) < n:
                arr = arr + [default_value] * (n - len(arr))
            elif len(arr) > n:
                arr = arr[:n]
            viewport_dict[key] = arr
            return arr

    def populate_list(self):
        from fcn_RTFiles.process_rt_files import set_struct_table
        
        names = self.series_dict.get('structures_names', [])
        keys = self.series_dict.get('structures_keys', [])
        n = len(names)
        
        view_flags = self._ensure_array('structures_view', n, 0)
        colors = self._ensure_array('structures_color', n, "#1b87ae")
        line_widths = self._ensure_array('structures_line_width', n, 3.0)
        transpars = self._ensure_array('structures_transparency', n, 0.1)
        mask_trs = self._ensure_array('structures_mask_transparency', n, 0.5)
        
        def on_toggle(i, checked):
            view_flags[i] = 1 if checked else 0
            
        def on_color(i, hexstr):
            colors[i] = hexstr
            
        def on_line_width(i, v):
            line_widths[i] = float(v)
            
        def on_transparency(i, v):
            transpars[i] = float(v)
            
        def on_mask_tr(i, v):
            mask_trs[i] = float(v)
            
        def on_refresh():
            from fcn_display.display_images_comp import disp_comp_image_slice
            disp_comp_image_slice(self.parent_app)
            
        for idx, (name, key) in enumerate(zip(names, keys)):
            list_item = QtWidgets.QListWidgetItem(self.list_widget)
            custom_item = set_struct_table(
                name, idx=idx, mode=1,
                on_toggle=on_toggle,
                on_color=on_color,
                on_line_width=on_line_width,
                on_transparency=on_transparency,
                on_mask_transparency=on_mask_tr,
                on_refresh=on_refresh,
                init_color=colors[idx],
                init_line_width=line_widths[idx],
                init_transparency=transpars[idx],
                init_mask_transparency=mask_trs[idx]
            )
            custom_item.set_checked(bool(view_flags[idx]))
            list_item.setSizeHint(custom_item.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, custom_item)


def _get_comp_struct_array(self, Ax_idx, key, n, default_value, series_dict):
    """
    Get a structure array property either globally from series_dict (if Link contours is checked)
    or from viewport-specific overrides.
    """
    if not hasattr(self, 'comp_viewport_structures'):
        self.comp_viewport_structures = {}
        
    if not hasattr(self, 'Comp_linkContours') or self.Comp_linkContours.isChecked():
        arr = series_dict.get(key)
        if not isinstance(arr, list):
            arr = []
        if len(arr) < n:
            arr = arr + [default_value] * (n - len(arr))
        elif len(arr) > n:
            arr = arr[:n]
        series_dict[key] = arr
        return arr
    else:
        if Ax_idx not in self.comp_viewport_structures:
            self.comp_viewport_structures[Ax_idx] = {}
        viewport_dict = self.comp_viewport_structures[Ax_idx]
        arr = viewport_dict.get(key)
        if not isinstance(arr, list):
            global_arr = series_dict.get(key)
            if isinstance(global_arr, list):
                arr = list(global_arr)
            else:
                arr = []
        if len(arr) < n:
            arr = arr + [default_value] * (n - len(arr))
        elif len(arr) > n:
            arr = arr[:n]
        viewport_dict[key] = arr
        return arr


def on_link_contours_changed(self):
    """
    Called when 'Link contours' checkbox state changes.
    """
    if not hasattr(self, 'Comp_linkContours') or not self.Comp_linkContours.isChecked():
        return
        
    # Clear viewport-specific overrides so all axes revert to the global series values
    if hasattr(self, 'comp_viewport_structures'):
        self.comp_viewport_structures.clear()
        
    # Re-render all viewports
    from fcn_display.display_images_comp import disp_comp_image_slice
    for Ax_idx in range(12):
        if (Ax_idx, 0) in self.display_comp_data:
            disp_comp_image_slice(self)


def disp_structure_overlay_comp(self, Ax_idx):
    """
    Overlay structures on comparison viewport Ax_idx.
    """
    renderer = self.renAxComp[Ax_idx]
    
    # Clear previous contour actors for this viewport
    if not hasattr(self, 'structure_actors_comp'):
        self.structure_actors_comp = {}
    if Ax_idx not in self.structure_actors_comp:
        self.structure_actors_comp[Ax_idx] = []
        
    for actor in self.structure_actors_comp[Ax_idx]:
        renderer.RemoveActor(actor)
    self.structure_actors_comp[Ax_idx] = []
    
    # Check all loaded layers
    for l_idx in range(4):
        if (Ax_idx, l_idx) not in self.display_comp_data:
            continue
            
        if not hasattr(self, 'comp_series_keys') or (Ax_idx, l_idx) not in self.comp_series_keys:
            continue
            
        pID, sID, mod, sIdx = self.comp_series_keys[Ax_idx, l_idx]
        try:
            series_dict = self.medical_image[pID][sID][mod][sIdx]
        except KeyError:
            continue
            
        if not series_dict.get("structures"):
            continue
            
        slice_idx = int(self.current_AxComp_slice_index[Ax_idx, l_idx])
        px_spacing = (self.pixel_spac_comp[Ax_idx, l_idx, 1], self.pixel_spac_comp[Ax_idx, l_idx, 0])
        
        names = series_dict.get('structures_names', [])
        keys = series_dict.get('structures_keys', [])
        n = min(len(names), len(keys))
        
        colors_hex   = _get_comp_struct_array(self, Ax_idx, 'structures_color',        n, "#ffffff", series_dict)
        line_widths  = _get_comp_struct_array(self, Ax_idx, 'structures_line_width',   n, 2.0,       series_dict)
        transpars    = _get_comp_struct_array(self, Ax_idx, 'structures_transparency', n, 0.1,       series_dict)
        view         = _get_comp_struct_array(self, Ax_idx, 'structures_view',         n, 0,         series_dict)
        
        def _hex_to_rgbf(h):
            try:
                s = (h or "").strip()
                if s.startswith("#"):
                    s = s[1:]
                if len(s) == 3:
                    s = "".join(c*2 for c in s)
                r = int(s[0:2], 16) / 255.0
                g = int(s[2:4], 16) / 255.0
                b = int(s[4:6], 16) / 255.0
                return (r, g, b)
            except Exception:
                return (1.0, 1.0, 1.0)
                
        for i in range(n):
            if view[i] != 1:
                continue
                
            s_key = keys[i]
            if not s_key:
                continue
                
            s_data = series_dict.get("structures", {}).get(s_key, {})
            if not s_data:
                continue
                
            if 'Contours2D' not in s_data or not isinstance(s_data['Contours2D'], dict):
                s_data['Contours2D'] = {'axial': {}, 'sagittal': {}, 'coronal': {}}
                
            from fcn_RTFiles.process_contours import build_contours_for_structure
            if not s_data['Contours2D'].get('axial') or s_data.get('Modified', 0) == 1:
                s_data['Contours2D'] = build_contours_for_structure(s_data['Mask3D'])
                
            ori = int(self.im_ori_comp[Ax_idx])
            orientation_name = "axial" if ori == 0 else ("sagittal" if ori == 1 else "coronal")
            
            if "VTKActors2D" not in s_data:
                s_data["VTKActors2D"] = {}
                
            if orientation_name not in s_data["VTKActors2D"] or s_data.get('Modified', 0) == 1:
                contours_list = s_data.get("Contours2D", {}).get(orientation_name, {})
                from fcn_RTFiles.process_contours import actors_from_contours
                s_data["VTKActors2D"][orientation_name] = actors_from_contours(
                    contours_list,
                    px_spacing,
                    line_width=float(line_widths[i]),
                    color=_hex_to_rgbf(colors_hex[i])
                )
                
            if s_data.get('Modified', 0) == 1:
                s_data['Modified'] = 0
                
            actors_dict = s_data["VTKActors2D"][orientation_name]
            if slice_idx not in actors_dict:
                continue
                
            src_actor = actors_dict[slice_idx]
            
            actor = vtk.vtkActor()
            actor.ShCopy = actor.ShallowCopy(src_actor)
            actor.GetProperty().SetColor(_hex_to_rgbf(colors_hex[i]))
            actor.GetProperty().SetOpacity(1.0 - float(transpars[i]))
            actor.GetProperty().SetLineWidth(float(line_widths[i]))
            actor.GetProperty().SetRepresentationToWireframe()
            
            st = float(self.slice_thick_comp[Ax_idx, l_idx]) if self.slice_thick_comp is not None else 1.0
            epsilon = max(0.1, 0.05 * (st if st > 0 else 1.0))
            
            if ori == 0:
                actor.SetPosition(self.Im_Offset_comp[Ax_idx, l_idx, 0],
                                  self.Im_Offset_comp[Ax_idx, l_idx, 1],
                                  epsilon)
            elif ori == 1:
                actor.SetPosition(self.Im_Offset_comp[Ax_idx, l_idx, 1],
                                  self.Im_Offset_comp[Ax_idx, l_idx, 2],
                                  epsilon)
            else:
                actor.SetPosition(self.Im_Offset_comp[Ax_idx, l_idx, 0],
                                  self.Im_Offset_comp[Ax_idx, l_idx, 2],
                                  epsilon)
                                  
            renderer.AddActor(actor)
            self.structure_actors_comp[Ax_idx].append(actor)
            
    _update_comp_mask_overlay(self, Ax_idx)
    renderer.ResetCameraClippingRange()


def _build_comp_mask_rgba(self, Ax_idx):
    """
    Build a 2D RGBA mask image representing filled structure contours for Compare viewport Ax_idx.
    """
    ori = int(self.im_ori_comp[Ax_idx])
    
    if (Ax_idx, 0) not in self.display_comp_data:
        return None
        
    base_data = self.display_comp_data[Ax_idx, 0]
    
    # 2D shape of the slice depending on view orientation
    if ori == 0:
        h, w = base_data.shape[1], base_data.shape[2]
    elif ori == 1:
        h, w = base_data.shape[0], base_data.shape[1]
    else:
        h, w = base_data.shape[0], base_data.shape[2]
        
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    
    for l_idx in range(4):
        if (Ax_idx, l_idx) not in self.display_comp_data:
            continue
            
        if not hasattr(self, 'comp_series_keys') or (Ax_idx, l_idx) not in self.comp_series_keys:
            continue
            
        pID, sID, mod, sIdx = self.comp_series_keys[Ax_idx, l_idx]
        try:
            series_dict = self.medical_image[pID][sID][mod][sIdx]
        except KeyError:
            continue
            
        if not series_dict.get("structures"):
            continue
            
        slice_idx = int(self.current_AxComp_slice_index[Ax_idx, l_idx])
        names = series_dict.get('structures_names', [])
        keys = series_dict.get('structures_keys', [])
        n = min(len(names), len(keys))
        
        view   = _get_comp_struct_array(self, Ax_idx, 'structures_view',              n, 0,         series_dict)
        colors = _get_comp_struct_array(self, Ax_idx, 'structures_color',             n, "#ff0000", series_dict)
        mtr    = _get_comp_struct_array(self, Ax_idx, 'structures_mask_transparency', n, 0.5,       series_dict)
        
        for i in range(n):
            if view[i] != 1:
                continue
                
            s_key = keys[i]
            sdat = series_dict["structures"].get(s_key, {})
            mask3d = sdat.get("Mask3D")
            if mask3d is None or slice_idx < 0 or slice_idx >= mask3d.shape[0]:
                continue
                
            mt = float(mtr[i])
            if mt >= 0.999: # fully hidden
                continue
                
            if ori == 0: # Axial: Z slice
                mask2d = mask3d[slice_idx, :, :] > 0
            elif ori == 1: # Sagittal: X slice
                mask2d = mask3d[:, :, slice_idx] > 0
            else: # Coronal: Y slice
                mask2d = mask3d[:, slice_idx, :] > 0
                
            if not np.any(mask2d):
                continue
                
            def _hex_to_rgbf(h):
                try:
                    s = (h or "").strip()
                    if s.startswith("#"):
                        s = s[1:]
                    if len(s) == 3:
                        s = "".join(c*2 for c in s)
                    r = int(s[0:2], 16) / 255.0
                    g = int(s[2:4], 16) / 255.0
                    b = int(s[4:6], 16) / 255.0
                    return (r, g, b)
                except Exception:
                    return (1.0, 0.0, 0.0)
                    
            r, g, b = _hex_to_rgbf(colors[i])
            a = np.clip(1.0 - mt, 0.0, 0.99)
            
            R = int(r * 255); G = int(g * 255); B = int(b * 255); A = int(a * 255)
            rgba[mask2d, 0] = np.maximum(rgba[mask2d, 0], R)
            rgba[mask2d, 1] = np.maximum(rgba[mask2d, 1], G)
            rgba[mask2d, 2] = np.maximum(rgba[mask2d, 2], B)
            rgba[mask2d, 3] = np.maximum(rgba[mask2d, 3], A)
            
    return rgba


def _update_comp_mask_overlay(self, Ax_idx):
    """
    Import and update the vtkImageActor overlay representing filled masks for Compare viewport Ax_idx.
    """
    if not hasattr(self, 'maskOverlayActorComp'):
        self.maskOverlayActorComp = {}
    if not hasattr(self, 'maskOverlayImporterComp'):
        self.maskOverlayImporterComp = {}
        
    renderer = self.renAxComp[Ax_idx]
    
    rgba = _build_comp_mask_rgba(self, Ax_idx)
    if rgba is None:
        if Ax_idx in self.maskOverlayActorComp:
            self.maskOverlayActorComp[Ax_idx].GetProperty().SetOpacity(0.0)
        return
        
    if Ax_idx not in self.maskOverlayImporterComp:
        self.maskOverlayImporterComp[Ax_idx] = vtk.vtkImageImport()
        self.maskOverlayActorComp[Ax_idx] = vtk.vtkImageActor()
        self.maskOverlayActorComp[Ax_idx].GetMapper().SetInputConnection(
            self.maskOverlayImporterComp[Ax_idx].GetOutputPort()
        )
        self.maskOverlayActorComp[Ax_idx].InterpolateOff()
        self.maskOverlayActorComp[Ax_idx].SetPickable(False)
        renderer.AddActor(self.maskOverlayActorComp[Ax_idx])
        
    h, w, _ = rgba.shape
    data = rgba.tobytes()
    
    imp = self.maskOverlayImporterComp[Ax_idx]
    
    ori = int(self.im_ori_comp[Ax_idx])
    if ori == 0:
        spacing = (self.pixel_spac_comp[Ax_idx, 0, 1], self.pixel_spac_comp[Ax_idx, 0, 0], 1.0)
    elif ori == 1:
        spacing = (self.pixel_spac_comp[Ax_idx, 0, 0], self.slice_thick_comp[Ax_idx, 0], 1.0)
    else:
        spacing = (self.pixel_spac_comp[Ax_idx, 0, 1], self.slice_thick_comp[Ax_idx, 0], 1.0)
        
    imp.SetDataSpacing(spacing[0], spacing[1], spacing[2])
    imp.SetDataOrigin(0.0, 0.0, 0.0)
    imp.CopyImportVoidPointer(data, len(data))
    imp.SetWholeExtent(0, w-1, 0, h-1, 0, 0)
    imp.SetDataExtent(0, w-1, 0, h-1, 0, 0)
    imp.SetNumberOfScalarComponents(4)
    imp.SetDataScalarTypeToUnsignedChar()
    imp.Modified()
    
    st = float(self.slice_thick_comp[Ax_idx, 0]) if self.slice_thick_comp is not None else 1.0
    epsilon = max(0.1, 0.05 * (st if st > 0 else 1.0))
    
    if ori == 0:
        self.maskOverlayActorComp[Ax_idx].SetPosition(
            self.Im_Offset_comp[Ax_idx, 0, 0],
            self.Im_Offset_comp[Ax_idx, 0, 1],
            epsilon * 0.5
        )
    elif ori == 1:
        self.maskOverlayActorComp[Ax_idx].SetPosition(
            self.Im_Offset_comp[Ax_idx, 0, 1],
            self.Im_Offset_comp[Ax_idx, 0, 2],
            epsilon * 0.5
        )
    else:
        self.maskOverlayActorComp[Ax_idx].SetPosition(
            self.Im_Offset_comp[Ax_idx, 0, 0],
            self.Im_Offset_comp[Ax_idx, 0, 2],
            epsilon * 0.5
        )
        
    self.maskOverlayActorComp[Ax_idx].GetProperty().SetOpacity(1.0)
    #end_time = time.time()
    #print(f": {end_time - start_time} seconds")