import numpy as np

def set_transp_slider_fcn(self):
    self.Layer_0_alpha_sli.valueChanged.connect(lambda: Layer_alpha_slider_set(self,0))
    self.Layer_0_alpha_spin.valueChanged.connect(lambda: Layer_0_alpha_spinbox_set(self))
    self.Layer_1_alpha_sli.valueChanged.connect(lambda: Layer_alpha_slider_set(self,1))
    self.Layer_1_alpha_spin.valueChanged.connect(lambda: Layer_1_alpha_spinbox_set(self))
    self.Layer_2_alpha_sli.valueChanged.connect(lambda: Layer_alpha_slider_set(self,2))
    self.Layer_2_alpha_spin.valueChanged.connect(lambda: Layer_2_alpha_spinbox_set(self))
    self.Layer_3_alpha_sli.valueChanged.connect(lambda: Layer_alpha_slider_set(self,3))
    self.Layer_3_alpha_spin.valueChanged.connect(lambda: Layer_3_alpha_spinbox_set(self))
    
def Layer_alpha_slider_set(self,layer):
    currentTabText = self.tabModules.tabText(self.tabModules.currentIndex())
    if layer==0:
        self.LayerAlpha[layer] = self.Layer_0_alpha_sli.value()/100
        self.Layer_0_alpha_spin.setValue(self.LayerAlpha[layer])
        self.transTab[currentTabText][0] = np.copy(self.LayerAlpha[0])
    elif layer==1:
        self.LayerAlpha[layer] = self.Layer_1_alpha_sli.value()/100
        self.Layer_1_alpha_spin.setValue(self.LayerAlpha[layer])
        self.transTab[currentTabText][1] = np.copy(self.LayerAlpha[1])
    elif layer==2:
        self.LayerAlpha[layer] = self.Layer_2_alpha_sli.value()/100
        self.Layer_2_alpha_spin.setValue(self.LayerAlpha[layer])
        self.transTab[currentTabText][2] = np.copy(self.LayerAlpha[2])
    elif layer==3:
        self.LayerAlpha[layer] = self.Layer_3_alpha_sli.value()/100
        self.Layer_3_alpha_spin.setValue(self.LayerAlpha[layer])
        self.transTab[currentTabText][3] = np.copy(self.LayerAlpha[3])
    #
    #
    if currentTabText == "View":
        imageProperty = self.imageActorAxial[layer].GetProperty()
        imageProperty.SetOpacity(self.LayerAlpha[layer])
        imageProperty = self.imageActorSagittal[layer].GetProperty()
        imageProperty.SetOpacity(self.LayerAlpha[layer])
        imageProperty = self.imageActorCoronal[layer].GetProperty()
        imageProperty.SetOpacity(self.LayerAlpha[layer])
        self.vtkWidgetAxial.GetRenderWindow().Render()
        self.vtkWidgetSagittal.GetRenderWindow().Render()
        self.vtkWidgetCoronal.GetRenderWindow().Render()
        #
    elif currentTabText == "_3Dview":
        #
        if hasattr(self, '_on_opacity_changed'):
            self._on_opacity_changed(self.LayerAlpha[layer], layer)
        #
    elif currentTabText == "Compare":
        ref_idx = self.Comp_im_idx.value()
        if not hasattr(self, 'CompLayerAlpha'):
            self.CompLayerAlpha = {}
        self.CompLayerAlpha[ref_idx, layer] = self.LayerAlpha[layer]
        
        if hasattr(self, 'imageActorAxComp') and (ref_idx, layer) in self.imageActorAxComp:
            imageProperty = self.imageActorAxComp[ref_idx, layer].GetProperty()
            imageProperty.SetOpacity(self.LayerAlpha[layer])
            if hasattr(self, 'renAxComp') and len(self.renAxComp) > ref_idx and self.renAxComp[ref_idx]:
                self.renAxComp[ref_idx].GetRenderWindow().Render()  
    elif currentTabText == "Segmentation":
        self.LayerAlpha[layer] = np.clip(self.LayerAlpha[layer], 0, 0.99)
        if hasattr(self, 'imageActorSeg') and layer in self.imageActorSeg:
            imageProperty = self.imageActorSeg[layer].GetProperty()
            imageProperty.SetOpacity(self.LayerAlpha[layer])
            if hasattr(self, 'renSeg') and self.renSeg:
                self.renSeg.GetRenderWindow().Render()

    
def Layer_0_alpha_spinbox_set(self):
    self.LayerAlpha[0] = self.Layer_0_alpha_spin.value()
    self.Layer_0_alpha_sli.setValue(int(self.LayerAlpha[0]*100))
    
def Layer_1_alpha_spinbox_set(self):
    self.LayerAlpha[1] = self.Layer_1_alpha_spin.value()
    self.Layer_1_alpha_sli.setValue(int(self.LayerAlpha[1]*100))

def Layer_2_alpha_spinbox_set(self):
    self.LayerAlpha[2] = self.Layer_2_alpha_spin.value()
    self.Layer_2_alpha_sli.setValue(int(self.LayerAlpha[2]*100))
    
def Layer_3_alpha_spinbox_set(self):
    self.LayerAlpha[3] = self.Layer_3_alpha_spin.value()
    self.Layer_3_alpha_sli.setValue(int(self.LayerAlpha[3]*100))