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
            
        self.renAxComp[Ax_idx].GetRenderWindow().Render()
    #end_time = time.time()
    #print(f": {end_time - start_time} seconds")