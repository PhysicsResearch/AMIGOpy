
def sliderSegView_change(self):
    disp_seg_image_slice(self)


def disp_seg_image_slice(self):
    layer  = int(self.layer_selection_box.currentIndex())
    ori = self.segSelectView.currentText()

    self.current_seg_slice_index[layer] = self.segViewSlider.value()

    if ori=="Axial": #Axial
        slice_data = self.display_seg_data[layer][int(self.current_seg_slice_index[layer]), :, :]
        self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,0], self.Im_Offset_seg[layer,1], 0)
        self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,1],self.pixel_spac_seg[layer,0],1)
    elif ori=="Sagittal": #Sagittal 
        slice_data = self.display_seg_data[layer][:,:,int(self.current_seg_slice_index[layer])]
        self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,1], self.Im_Offset_seg[layer,2], 0)
        self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,0],self.slice_thick_seg[layer],1)
    elif ori=="Coronal": #Coronal
        slice_data = self.display_seg_data[layer][:,int(self.current_seg_slice_index[layer]), :]
        self.imageActorSeg[layer].SetPosition(self.Im_Offset_seg[layer,0], self.Im_Offset_seg[layer,2], 0)
        self.dataImporterSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,1],self.slice_thick_seg[layer],1)
    #

    data_string = slice_data.tobytes()
    extent = slice_data.shape
    self.dataImporterSeg[layer].CopyImportVoidPointer(data_string, len(data_string))
    self.dataImporterSeg[layer].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
    self.dataImporterSeg[layer].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
    #
    #
    self.textActorSeg[2].SetInput(f"Slice:{self.current_seg_slice_index[layer]}")
    #
    imageProperty = self.imageActorSeg[layer].GetProperty()
    imageProperty.SetOpacity(self.LayerAlpha[layer])  
    self.dataImporterSeg[layer].Modified()     
    self.renSeg.GetRenderWindow().Render()  
