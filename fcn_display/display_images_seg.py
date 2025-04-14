
def sliderSegView_change(self):
    disp_seg_image_slice(self)


def disp_seg_image_slice(self):
    layer  = int(self.layer_selection_box.currentIndex())
    ori = self.segSelectView.currentText()

    self.current_seg_slice_index[layer] = self.SliderSegView.value()

    if ori=="Axial": #Axial
        slice_data = self.display_seg_data[layer][int(self.current_seg_slice_index[layer]), :, :]
        self.imageActorAxSeg[layer].SetPosition(self.Im_Offset_seg[layer,0], self.Im_Offset_seg[layer,1], 0)
        self.dataImporterAxSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,1],self.pixel_spac_seg[layer,0],1)
    elif ori=="Sagittal": #Sagittal 
        slice_data = self.display_seg_data[layer][:,:,int(self.current_seg_slice_index[layer])]
        self.imageActorAxSeg[layer].SetPosition(self.Im_Offset_seg[layer,1], self.Im_Offset_seg[layer,2], 0)
        self.dataImporterAxSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,0],self.slice_thick_seg[layer],1)
    elif ori=="Coronal": #Coronal
        slice_data = self.display_seg_data[layer][:,int(self.current_seg_slice_index[layer]), :]
        self.imageActorAxSeg[layer].SetPosition(self.Im_Offset_seg[layer,0], self.Im_Offset_seg[layer,2], 0)
        self.dataImporterAxSeg[layer].SetDataSpacing(self.pixel_spac_seg[layer,1],self.slice_thick_seg[layer],1)
    #

    data_string = slice_data.tobytes()
    extent = slice_data.shape
    self.dataImporterAxSeg[layer].CopyImportVoidPointer(data_string, len(data_string))
    self.dataImporterAxSeg[layer].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
    self.dataImporterAxSeg[layer].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
    #
    #
    self.textActorAxSeg[2].SetInput(f"Slice:{self.current_seg_slice_index[layer]}")
    #
    imageProperty = self.imageActorAxSeg[layer].GetProperty()
    imageProperty.SetOpacity(self.LayerAlpha[layer])  
    self.dataImporterAxSeg[layer].Modified()     
    self.renAxSeg.GetRenderWindow().Render()  
