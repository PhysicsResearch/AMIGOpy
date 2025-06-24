def sliderIrISeval_change(self):
    disp_eval_iris_slice(self)


def disp_eval_iris_slice(self):
    # layer  = int(self.layer_selection_box.currentIndex())
    for layer in range(len(self.dataImporterIrEval)): 
        if self.slice_thick[layer] ==0:
            continue
        self.current_IrIS_eval_slice_index[layer] = self.Slider_Eval_IrIS.value()
        #
        if self.List_Eval_Direction.currentText() == "XY": 
            slice_data = self.display_data_IrIS_eval[layer][int(self.current_IrIS_eval_slice_index[layer]), :, :]
            self.dataImporterIrEval[layer].SetDataSpacing(self.pixel_spac[layer,1],self.pixel_spac[layer,0],1)
        elif self.List_Eval_Direction.currentText() == "X-Time":
            slice_data = self.display_data_IrIS_eval[layer][:,:,int(self.current_IrIS_eval_slice_index[layer])]
            self.dataImporterIrEval[layer].SetDataSpacing(self.pixel_spac[layer,0],self.slice_thick[layer],1)
        elif self.List_Eval_Direction.currentText() == "Y-Time":
            slice_data = self.display_data_IrIS_eval[layer][:,int(self.current_IrIS_eval_slice_index[layer]), :]
            self.dataImporterIrEval[layer].SetDataSpacing(self.pixel_spac[layer,1],self.slice_thick[layer],1)
        #
    
        data_string = slice_data.tobytes()
        extent = slice_data.shape
        self.dataImporterIrEval[layer].CopyImportVoidPointer(data_string, len(data_string))
        self.dataImporterIrEval[layer].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        self.dataImporterIrEval[layer].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        #         
        imageProperty = self.imageActorIrEval[layer].GetProperty()
        imageProperty.SetOpacity(self.LayerAlpha[layer])  
        self.dataImporterIrEval[layer].Modified() 
        #
        imageProperty = self.imageActorIrEval[layer].GetProperty()
        imageProperty.SetOpacity(self.LayerAlpha[layer])  
        self.dataImporterIrEval[layer].Modified()     
        self.renIrEval.GetRenderWindow().Render()  