import time

def sliderCompareView_change(self):
    disp_comp_image_slice(self)


def disp_comp_image_slice(self):
    layer  = int(self.layer_selection_box.currentIndex())
    #start_time = time.time()
    if self.Comp_linkSlices.isChecked():
        r_1 = 0;
        r_2 = self.Comp_im_idx.maximum()+1;
    else:
        r_1 = self.Comp_im_idx.value();
        r_2 = r_1+ 1
    for Ax_idx in range (r_1,r_2):
        if not ((Ax_idx, layer) in self.display_comp_data and int(self.current_AxComp_slice_index[Ax_idx, layer]) in self.display_comp_data[Ax_idx, layer]):
             continue
        #end_time = time.time()
        #print(f": P1 {end_time - start_time} seconds")
        self.current_AxComp_slice_index[Ax_idx,layer] = self.SliderCompareView.value()
        #
        #end_time = time.time()
        #print(f": P2 {end_time - start_time} seconds {Ax_idx}")
        if self.im_ori_comp[Ax_idx] ==0: #Axial
            slice_data = self.display_comp_data[Ax_idx, layer][int(self.current_AxComp_slice_index[Ax_idx,layer]), :, :]
            self.imageActorAxComp[Ax_idx,layer].SetPosition(self.Im_Offset_comp[Ax_idx,layer,0], self.Im_Offset_comp[Ax_idx,layer,1], 0)
            self.dataImporterAxComp[Ax_idx,layer].SetDataSpacing(self.pixel_spac_comp[Ax_idx,layer,1],self.pixel_spac_comp[Ax_idx,layer,0],1)
        elif self.im_ori_comp[Ax_idx] ==1: #Sagittal 
            slice_data = self.display_comp_data[Ax_idx, layer][:,:,int(self.current_AxComp_slice_index[Ax_idx,layer])]
            self.imageActorAxComp[Ax_idx,layer].SetPosition(self.Im_Offset_comp[Ax_idx,layer,1], self.Im_Offset_comp[Ax_idx,layer,2], 0)
            self.dataImporterAxComp[Ax_idx,layer].SetDataSpacing(self.pixel_spac_comp[Ax_idx,layer,0],self.slice_thick_comp[Ax_idx,layer],1)
        elif self.im_ori_comp[Ax_idx] ==2: #Coronal
            slice_data = self.display_comp_data[Ax_idx, layer][:,int(self.current_AxComp_slice_index[Ax_idx,layer]), :]
            self.imageActorAxComp[Ax_idx,layer].SetPosition(self.Im_Offset_comp[Ax_idx,layer,0], self.Im_Offset_comp[Ax_idx,layer,2], 0)
            self.dataImporterAxComp[Ax_idx,layer].SetDataSpacing(self.pixel_spac_comp[Ax_idx,layer,1],self.slice_thick_comp[Ax_idx,layer],1)
        #

        data_string = slice_data.tobytes()
        extent = slice_data.shape
        self.dataImporterAxComp[Ax_idx,layer].CopyImportVoidPointer(data_string, len(data_string))
        self.dataImporterAxComp[Ax_idx,layer].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        self.dataImporterAxComp[Ax_idx,layer].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        #
        #
        self.textActorAxCom[Ax_idx,2].SetInput(f"Slice:{self.current_AxComp_slice_index[Ax_idx,layer]}")
        #
        imageProperty = self.imageActorAxComp[Ax_idx, layer].GetProperty()
        imageProperty.SetOpacity(self.LayerAlpha[layer])  
        self.dataImporterAxComp[Ax_idx,layer].Modified()     
        self.renAxComp[Ax_idx].GetRenderWindow().Render()  
    #end_time = time.time()
    #print(f": {end_time - start_time} seconds")