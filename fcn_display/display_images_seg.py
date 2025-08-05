import vtk 
import numpy as np
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt


def update_seg_slider(self):

    self.im_ori_seg = self.segSelectView.currentText().lower()
    if 0 not in self.display_seg_data:
        return

    if self.im_ori_seg=="axial":
        self.segViewSlider.setMaximum(self.display_seg_data[0].shape[0] - 1)
        self.segViewSlider.setValue(int(self.display_seg_data[0].shape[0]/2))  
    elif self.im_ori_seg=="sagittal":
        self.segViewSlider.setMaximum(self.display_seg_data[0].shape[2] - 1)
        self.segViewSlider.setValue(int(self.display_seg_data[0].shape[2]/2))  
    elif self.im_ori_seg=="coronal":
        self.segViewSlider.setMaximum(self.display_seg_data[0].shape[1] - 1)
        self.segViewSlider.setValue(int(self.display_seg_data[0].shape[1]/2))  

    self.indexMinThreshSeg.setMinimum(0)
    self.indexMinThreshSeg.setValue(0)
    self.indexMinThreshSeg.setMaximum(self.segViewSlider.maximum() - 1)
    self.indexMaxThreshSeg.setMinimum(1)
    self.indexMaxThreshSeg.setMaximum(self.segViewSlider.maximum())
    self.indexMaxThreshSeg.setValue(self.segViewSlider.maximum())

    disp_seg_image_slice(self)


def disp_seg_image_slice(self):
    self.current_seg_slice_index = self.segViewSlider.value()
    
    #########################
    ### DISPLAY CT VOLUME ###
    #########################
    
    # Nothing to display if image volume not available
    if 0 not in self.display_seg_data: 
        return 

    # Display CT volume in layer 0
    layer = 0 
    if self.im_ori_seg=="axial": #Axial
        slice_data = self.display_seg_data[layer][int(self.current_seg_slice_index), :, :]
        self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,0], self.Im_Offset_seg[layer,1], 0)
        self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,1],self.pixel_spac_seg[layer,0],1)
    elif self.im_ori_seg=="sagittal": #Sagittal 
        slice_data = self.display_seg_data[layer][:,:,int(self.current_seg_slice_index)]
        self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,1], self.Im_Offset_seg[layer,2], 0)
        self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,0],self.slice_thick_seg[0],1)
    elif self.im_ori_seg=="coronal": #Coronal
        slice_data = self.display_seg_data[layer][:,int(self.current_seg_slice_index), :]
        self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,0], self.Im_Offset_seg[layer,2], 0)
        self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,1],self.slice_thick_seg[0],1)
    
    # Set data to importer
    data_string = slice_data.tobytes()
    extent = slice_data.shape
    self.dataImporterSeg[layer].CopyImportVoidPointer(data_string, len(data_string))
    self.dataImporterSeg[layer].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
    self.dataImporterSeg[layer].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
    self.dataImporterSeg[layer].Modified() 
    # Set text and opacity
    self.textActorSeg[2].SetInput(f"Slice:{self.current_seg_slice_index}")
    imageProperty = self.imageActorSeg[layer].GetProperty()
    imageProperty.SetOpacity(self.LayerAlpha[layer])   
    # Render window
    self.renSeg.GetRenderWindow().Render()  

    #####################################
    ### DISPLAY SELECTED SEGMENTATION ###
    #####################################
    layer = 1
    if self.im_ori_seg=="axial": #Axial
        self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,1],self.pixel_spac_seg[layer,0],1)
    elif self.im_ori_seg=="sagittal": #Sagittal 
        self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,0],self.slice_thick_seg[layer],1)
    elif self.im_ori_seg=="coronal": #Coronal
        self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,1],self.slice_thick_seg[layer],1)

    # If any structure is selected, display selected segmentation in layer 1
    slice_data_im = slice_data.copy()
    if self.curr_struc_key is not None and 1 in self.display_seg_data:
        if self.file_format == "DICOM":
            target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
        elif self.file_format == "nifti":
            target_series_dict = self.nifti_data[self.series_index]
        else:
            return

        if self.curr_struc_key in target_series_dict['structures']:
            target_series_dict['structures'][self.curr_struc_key]['Modified'] = 1
            patientID = target_series_dict.get('PatientID', '')
            seriesID = target_series_dict.get('SeriesNumber', '')
            target_key = f"{patientID}_{seriesID}_{self.curr_struc_name}"

        if self.display_seg_data[0].shape != self.display_seg_data[1].shape:
            QMessageBox.warning(None, "Warning", "Selected segmentation does not match the image volume shape.")
            return
        
        if self.im_ori_seg=="axial": #Axial
            slice_data = self.display_seg_data[layer][int(self.current_seg_slice_index), :, :]
        elif self.im_ori_seg=="sagittal": #Sagittal 
            slice_data = self.display_seg_data[layer][:,:,int(self.current_seg_slice_index)]
        elif self.im_ori_seg=="coronal": #Coronal
            slice_data = self.display_seg_data[layer][:,int(self.current_seg_slice_index), :]
        
        if self.seg_brush_coords is not None: # If brush enabled
            self.brush_size = self.BrushSizeSlider.value()
            
            if self.im_ori_seg=="axial": 
                Y, X = np.ogrid[:slice_data.shape[0], :slice_data.shape[1]]
                dist_from_center = np.sqrt((X - self.seg_brush_coords[0])**2 + (Y-self.seg_brush_coords[1])**2)
            else: # Account for slice thickness if not axial
                Y, X = np.ogrid[:slice_data.shape[0], :slice_data.shape[1]]
                dist_from_center = np.sqrt((X - self.seg_brush_coords[0])**2 + (Y-self.seg_brush_coords[1])**2 * 
                                            (self.slice_thick_seg[layer] / self.pixel_spac_seg[layer,1]))
            
            mask = dist_from_center <= self.brush_size 
            if self.seg_erase == 1: # Eraser 
                if self.brushClipHU.isChecked():
                    try:
                        min_hu = int(self.threshMinHU.text())
                    except:
                        QMessageBox.warning(None, "Warning", "No valid value (int) was provided for min HU")
                        return
                    try:
                        max_hu = int(self.threshMaxHU.text())
                    except:
                        QMessageBox.warning(None, "Warning", "No valid value (int) was provided for max HU")
                        return
                    if min_hu >= max_hu:
                        QMessageBox.warning(None, "Warning", "No valid HU range was provided (ensure min HU < max HU)")
                        return  
                    mask_hu = (slice_data_im >= min_hu) * (slice_data_im <= max_hu)
                    slice_data[mask * mask_hu] = 0
                else:
                    slice_data[mask] = 0
            
            if self.seg_brush == 1: # Brush
                if self.brushClipHU.isChecked():
                    try:
                        min_hu = int(self.threshMinHU.text())
                    except:
                        QMessageBox.warning(None, "Warning", "No valid value (int) was provided for min HU")
                        return
                    try:
                        max_hu = int(self.threshMaxHU.text())
                    except:
                        QMessageBox.warning(None, "Warning", "No valid value (int) was provided for max HU")
                        return
                    if min_hu >= max_hu:
                        QMessageBox.warning(None, "Warning", "No valid HU range was provided (ensure min HU < max HU)")
                        return  
                    mask_hu = (slice_data_im >= min_hu) * (slice_data_im <= max_hu)
                    slice_data[mask * mask_hu] = 1
                else:
                    slice_data[mask] = 1

        # Get layer color and opacity
        layer_opacity = self.LayerAlpha[1]
        opacity = 0
        color = (1, 0, 0)
        for i in range(self.segStructList.count()):
            item = self.segStructList.item(i)
            widget = self.segStructList.itemWidget(item)
            if not widget:
                continue
            if getattr(widget, "structure_key", None) == target_key:
                self.struct_colors[self.curr_struc_name] = widget.selectedColor if widget.selectedColor else QColor(Qt.red)
                color = widget.selectedColor.getRgbF()[:3] if widget.selectedColor else (1, 0, 0)
                opacity = widget.transparency_spinbox.value()

        # Set data
        data_string = slice_data.tobytes()
        self.dataImporterSeg[layer].CopyImportVoidPointer(data_string, len(data_string))
        self.dataImporterSeg[layer].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        self.dataImporterSeg[layer].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)

        # Set segmentation color and transparency
        lut = vtk.vtkLookupTable()
        lut.SetTableValue(0, 0, 0, 0, 0)  # Set zero to transparent
        lut.SetTableValue(1, *color, np.clip(layer_opacity * opacity, 0, 0.99))
        lut.Build()
        self.imageActorSeg[layer].GetProperty().SetLookupTable(lut)
        imageProperty = self.imageActorSeg[layer].GetProperty()
        imageProperty.SetOpacity(self.LayerAlpha[layer])  

        self.dataImporterSeg[layer].Modified()   
        self.renSeg.GetRenderWindow().Render() 

    # If no selected segmentation, render empty layer
    else:
        slice_data = np.zeros_like(slice_data_im, dtype=np.uint8)
        # Set data
        data_string = slice_data.tobytes()
        self.dataImporterSeg[layer].CopyImportVoidPointer(data_string, len(data_string))
        self.dataImporterSeg[layer].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        self.dataImporterSeg[layer].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)

        # Skip window-level mapping; connect importer directly
        imageProperty = self.imageActorSeg[layer].GetProperty()
        imageProperty.SetOpacity(0)  

        self.dataImporterSeg[layer].SetDataScalarTypeToUnsignedChar()
        self.dataImporterSeg[layer].Modified()   
        self.renSeg.GetRenderWindow().Render() 

    #####################################
    ### DISPLAY CHECKED SEGMENTATIONS ###
    #####################################

    # Display checked segmentations in layer 2
    layer = 2 
    if self.im_ori_seg=="axial": #Axial
        self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[0,1],self.pixel_spac_seg[0,0],1)
    elif self.im_ori_seg=="sagittal": #Sagittal 
        self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[0,0],self.slice_thick_seg[0],1)
    elif self.im_ori_seg=="coronal": #Coronal
        self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[0,1],self.slice_thick_seg[0],1)

    # If any structure in structure list
    plot_structures = False
    if self.segStructList.count() > 0:
        # Create composite of all available and checked structures
        slice_data = render_all_seg_layers(self) 
        if slice_data is not None:
            plot_structures = True

    # If no selected segmentation, render empty layer
    if not plot_structures:
        slice_data = np.zeros((*slice_data_im.shape, 4), dtype=np.uint8)    

    # Set data to importer
    data_string = slice_data.tobytes()
    self.dataImporterSeg[layer].SetNumberOfScalarComponents(4)
    self.dataImporterSeg[layer].CopyImportVoidPointer(data_string, len(data_string))
    self.dataImporterSeg[layer].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
    self.dataImporterSeg[layer].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)

    # Skip window-level mapping; connect importer directly
    self.imageActorSeg[layer].GetMapper().SetInputConnection(self.dataImporterSeg[layer].GetOutputPort())

    if plot_structures:
        self.imageActorSeg[layer].GetProperty().SetOpacity(1.0)  
    else:
        self.imageActorSeg[layer].GetProperty().SetOpacity(0.0)  

    self.dataImporterSeg[layer].SetDataScalarTypeToUnsignedChar()
    self.dataImporterSeg[layer].Modified()   
    self.renSeg.GetRenderWindow().Render()


def render_all_seg_layers(self):

    if self.im_ori_seg=="axial": #Axial
        slice_data = self.display_seg_data[0][int(self.current_seg_slice_index), :, :]
    elif self.im_ori_seg=="sagittal": #Sagittal 
        slice_data = self.display_seg_data[0][:,:,int(self.current_seg_slice_index)]
    elif self.im_ori_seg=="coronal": #Coronal
        slice_data = self.display_seg_data[0][:,int(self.current_seg_slice_index), :]
    
    height, width = slice_data.shape

    if self.file_format == "DICOM":
        target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    elif self.file_format == "nifti":
        target_series_dict = self.nifti_data[self.series_index]
    else:
        return None
    
    if 'structures_keys' in target_series_dict and 'structures_names' in target_series_dict:
        structures_keys = target_series_dict['structures_keys']
        structures_names = target_series_dict['structures_names']
    else:
        return

    layer_opacity = self.LayerAlpha[2]

    colors = []
    masks = []

    for i in range(self.segStructList.count()):
        item = self.segStructList.item(i)
        widget = self.segStructList.itemWidget(item)
        if not widget:
            continue
        if getattr(widget, "checkbox", None) is None: 
            continue
        if not widget.checkbox.isChecked():
            continue

        patient_id, series_id, name = widget.patient_id.text(), widget.series_id.text(), widget.struct_name.text()
        s_key = structures_keys[structures_names.index(name)]

        if self.file_format == "DICOM":
            if not ((patient_id == self.patientID) and (int(series_id) == self.curr_series_no) and (name != self.curr_struc_name)):
                return
            else:
                mask = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures'][s_key]['Mask3D']
        elif self.file_format == "nifti":
            if series_id != self.nifti_data[self.series_index]["SeriesNumber"]:
                return
            else:
                mask = self.nifti_data[self.series_index]['structures'][s_key]['Mask3D']
            
        if self.im_ori_seg=="axial": #Axial
            slice_data = mask[int(self.current_seg_slice_index), :, :]
        elif self.im_ori_seg=="sagittal": #Sagittal 
            slice_data = mask[:,:,int(self.current_seg_slice_index)]
        elif self.im_ori_seg=="coronal": #Coronal
            slice_data = mask[:,int(self.current_seg_slice_index), :]

        self.struct_colors[name] = widget.selectedColor if widget.selectedColor else QColor(Qt.red)
        color = widget.selectedColor.getRgbF()[:3] if widget.selectedColor else (1, 0, 0)
        opacity = widget.transparency_spinbox.value()

        masks.append(slice_data)
        colors.append((*color, np.clip(layer_opacity * opacity, 0, 0.99)))

    rgba_image = np.zeros((height, width, 4), dtype=np.uint8)

    for mask, color in zip(masks, colors):
        r, g, b, a = [int(c * 255) for c in color]
        mask_indices = mask > 0
        rgba_image[mask_indices, 0] = np.maximum(rgba_image[mask_indices, 0], r)
        rgba_image[mask_indices, 1] = np.maximum(rgba_image[mask_indices, 1], g)
        rgba_image[mask_indices, 2] = np.maximum(rgba_image[mask_indices, 2], b)
        rgba_image[mask_indices, 3] = np.maximum(rgba_image[mask_indices, 3], a)

    return rgba_image


def update_layer_view_seg(self):
    idx = self.layer_selection_box.currentIndex()
    tabName = self.tabModules.tabText(self.tabModules.currentIndex())
    self.layerTab[tabName] = idx
