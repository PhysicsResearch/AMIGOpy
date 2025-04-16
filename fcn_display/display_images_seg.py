
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
            vol = self.display_seg_data[i]
            if ori=="Axial": #Axial
                slice_data = vol[int(self.current_seg_slice_index), :, :]
                # self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,0], self.Im_Offset_seg[layer,1], 0)
                self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,1],self.pixel_spac_seg[layer,0],1)
            elif ori=="Sagittal": #Sagittal 
                slice_data = vol[:,:,int(self.current_seg_slice_index)]
                # self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,1], self.Im_Offset_seg[layer,2], 0)
                self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,0],self.slice_thick_seg[layer],1)
            elif ori=="Coronal": #Coronal
                slice_data = vol[:,int(self.current_seg_slice_index), :]
                # self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,0], self.Im_Offset_seg[layer,2], 0)
                self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,1],self.slice_thick_seg[layer],1)
            #
            if self.seg_brush_coords is not None:
                self.brush_size = 5
                
                if ori=="Axial": 
                    Y, X = np.ogrid[:slice_data.shape[0], :slice_data.shape[1]]
                    dist_from_center = np.sqrt((X - self.seg_brush_coords[0])**2 + (Y-self.seg_brush_coords[1])**2)
                else:
                    Y, X = np.ogrid[:slice_data.shape[0], :slice_data.shape[1]]
                    dist_from_center = np.sqrt((X - self.seg_brush_coords[0])**2 + (Y-self.seg_brush_coords[1])**2 * 
                                               (self.slice_thick_seg[layer] / self.pixel_spac_seg[layer,1]))
                
                mask = dist_from_center <= self.brush_size 
                slice_data[mask] = 0
                # slice_data[self.seg_brush_coords[1], self.seg_brush_coords[0]] = -1000

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


def update_layer_view_seg(self):
    idx = self.layer_selection_box.currentIndex()
    tabName = self.tabModules.tabText(self.tabModules.currentIndex())
    self.layerTab[tabName] = idx
