import vtk 

def sliderSegView_change(self):
    disp_seg_image_slice(self)
    
    
def update_seg_slider(self):
    layer  = int(self.layer_selection_box.currentIndex())
    ori = self.segSelectView.currentText()

    if ori=="Axial":
        self.segViewSlider.setMaximum(self.display_seg_data[layer].shape[0] - 1)
        self.segViewSlider.setValue(int(self.display_seg_data[layer].shape[0]/2))  
    elif ori=="Sagittal":
        self.display_seg_data[layer].shape[2] - 1
        self.segViewSlider.setMaximum(self.display_seg_data[layer].shape[2] - 1)
        self.segViewSlider.setValue(int(self.display_seg_data[layer].shape[2]/2))  
    elif ori=="Coronal":
        self.segViewSlider.setMaximum(self.display_seg_data[layer].shape[1] - 1)
        self.segViewSlider.setValue(int(self.display_seg_data[layer].shape[1]/2))  

    disp_seg_image_slice(self)
    
    
def undo_brush_seg(self):
    try:
        self.display_seg_data[1] = self.slice_data_copy  
        disp_seg_image_slice(self)
    except:
        return


import numpy as np
def disp_seg_image_slice(self):
    layer  = int(self.layer_selection_box.currentIndex())
    ori = self.segSelectView.currentText()

    self.current_seg_slice_index = self.segViewSlider.value()
    
    for i in range(len(self.dataImporterSeg)):
        layer = i
        if i == 0: # if series
            if ori=="Axial": #Axial
                slice_data = self.display_seg_data[layer][int(self.current_seg_slice_index), :, :]
                self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,0], self.Im_Offset_seg[layer,1], 0)
                self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,1],self.pixel_spac_seg[layer,0],1)
            elif ori=="Sagittal": #Sagittal 
                slice_data = self.display_seg_data[layer][:,:,int(self.current_seg_slice_index)]
                self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,1], self.Im_Offset_seg[layer,2], 0)
                self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,0],self.slice_thick_seg[0],1)
            elif ori=="Coronal": #Coronal
                slice_data = self.display_seg_data[layer][:,int(self.current_seg_slice_index), :]
                self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,0], self.Im_Offset_seg[layer,2], 0)
                self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,1],self.slice_thick_seg[0],1)
            #
        
            data_string = slice_data.tobytes()
            extent = slice_data.shape
            self.dataImporterSeg[layer].CopyImportVoidPointer(data_string, len(data_string))
            self.dataImporterSeg[layer].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            self.dataImporterSeg[layer].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            #
            #
            self.textActorSeg[2].SetInput(f"Slice:{self.current_seg_slice_index}")
            #
            imageProperty = self.imageActorSeg[layer].GetProperty()
            imageProperty.SetOpacity(self.LayerAlpha[layer])  
            self.dataImporterSeg[layer].Modified()     
            self.renSeg.GetRenderWindow().Render()  
        elif i == 1:
            if len(self.display_seg_data) <= i:
                continue

            if ori=="Axial": #Axial
                slice_data = self.display_seg_data[i][int(self.current_seg_slice_index), :, :]
                slice_data_im = self.display_seg_data[0][int(self.current_seg_slice_index), :, :]
                # self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,0], self.Im_Offset_seg[layer,1], 0)
                self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,1],self.pixel_spac_seg[layer,0],1)
            elif ori=="Sagittal": #Sagittal 
                slice_data = self.display_seg_data[i][:,:,int(self.current_seg_slice_index)]
                slice_data_im = self.display_seg_data[0][:,:,int(self.current_seg_slice_index)]
                # self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,1], self.Im_Offset_seg[layer,2], 0)
                self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,0],self.slice_thick_seg[layer],1)
            elif ori=="Coronal": #Coronal
                slice_data = self.display_seg_data[i][:,int(self.current_seg_slice_index), :]
                slice_data_im = self.display_seg_data[0][:,int(self.current_seg_slice_index), :]
                # self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,0], self.Im_Offset_seg[layer,2], 0)
                self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,1],self.slice_thick_seg[layer],1)
            #
            if self.seg_brush_coords is not None:
                self.brush_size = self.BrushSizeSlider.value()
                
                if ori=="Axial": 
                    Y, X = np.ogrid[:slice_data.shape[0], :slice_data.shape[1]]
                    dist_from_center = np.sqrt((X - self.seg_brush_coords[0])**2 + (Y-self.seg_brush_coords[1])**2)
                else:
                    Y, X = np.ogrid[:slice_data.shape[0], :slice_data.shape[1]]
                    dist_from_center = np.sqrt((X - self.seg_brush_coords[0])**2 + (Y-self.seg_brush_coords[1])**2 * 
                                               (self.slice_thick_seg[layer] / self.pixel_spac_seg[layer,1]))
                
                mask = dist_from_center <= self.brush_size 
                if self.seg_erase == 1:
                    slice_data[mask] = 0
                if self.seg_brush == 1:
                    mask_hu = (slice_data_im >= self.threshMinSlider.value()) * (slice_data_im <= self.threshMaxSlider.value())
                    slice_data[mask * mask_hu] = 1

            data_string = slice_data.tobytes()
            extent = slice_data.shape
            self.dataImporterSeg[layer].CopyImportVoidPointer(data_string, len(data_string))
            self.dataImporterSeg[layer].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            self.dataImporterSeg[layer].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            #
            #
            self.textActorSeg[2].SetInput(f"Slice:{self.current_seg_slice_index}")
            #
            # imageProperty = self.imageActorSeg[layer].GetProperty()
            lut         = vtk.vtkLookupTable()
            lut.SetTableValue(0, 0, 0, 0, 0)  # Transparent
            lut.SetTableValue(1, 1, 0, 0, 0.5)
            lut.Build()

            self.imageActorSeg[layer].GetProperty().SetLookupTable(lut)
            # self.imageActorSeg[layer].GetProperty().SetOpacity(0.5)#.imageProperty.SetOpacity(0.5)#self.LayerAlpha[layer])  
            self.dataImporterSeg[layer].Modified()     
            self.renSeg.GetRenderWindow().Render()  


def update_layer_view_seg(self):
    idx = self.layer_selection_box.currentIndex()
    tabName = self.tabModules.tabText(self.tabModules.currentIndex())
    self.layerTab[tabName] = idx
