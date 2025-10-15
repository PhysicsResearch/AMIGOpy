from fcn_display.display_images  import displayaxial, displaycoronal, displaysagittal  

def update_translation_x(self):
    self.Im_PatPosition[1,0]   =  float(self.Reg_manual_Tx.value())
    self.Im_Offset[1,0]   = (self.Im_PatPosition[1,0]-self.Im_PatPosition[0,0])
    displaycoronal(self)
    displaysagittal(self)
    displayaxial(self)

def update_translation_y(self):     
    self.Im_PatPosition[1,1]   =  float(self.Reg_manual_Ty.value())
    self.Im_Offset[1,1]        = (self.display_data[0].shape[1]*self.pixel_spac[0,0]-self.display_data[1].shape[1]*self.pixel_spac[1,0])-(self.Im_PatPosition[1,1]-self.Im_PatPosition[0,1])
    displaycoronal(self)
    displaysagittal(self)
    displayaxial(self)

def update_translation_z(self):
    self.Im_PatPosition[1,2]   =  float(self.Reg_manual_Tz.value())
    self.Im_Offset[1,2]        = (self.Im_PatPosition[1,2]-self.Im_PatPosition[0,2])
    displaysagittal(self)
    displaycoronal(self)
    displayaxial(self)

                 
def update_rotation_x(self):
    self.Im_PatPosition[1,0]   =  float(self.Reg_manual_Tx.value())
    self.Im_Offset[1,0]   = (self.Im_PatPosition[1,0]-self.Im_PatPosition[0,0])
    displaycoronal(self)
    displaysagittal(self)
    displayaxial(self)

def update_rotation_y(self):     
    self.Im_PatPosition[1,1]   =  float(self.Reg_manual_Ty.value())
    self.Im_Offset[1,1]        = (self.display_data[0].shape[1]*self.pixel_spac[0,0]-self.display_data[1].shape[1]*self.pixel_spac[1,0])-(self.Im_PatPosition[1,1]-self.Im_PatPosition[0,1])
    displaycoronal(self)
    displaysagittal(self)
    displayaxial(self)

def update_rotation_z(self):
    self.Im_PatPosition[1,2]   =  float(self.Reg_manual_Tz.value())
    self.Im_Offset[1,2]        = (self.Im_PatPosition[1,2]-self.Im_PatPosition[0,2])
    displaysagittal(self)
    displaycoronal(self)
    displayaxial(self)

def set_transformation_step(self):
    for w in (
    self.Reg_manual_Tx, self.Reg_manual_Ty, self.Reg_manual_Tz,
    self.Reg_manual_Refx, self.Reg_manual_Refy, self.Reg_manual_Refz,
    self.Reg_manual_Rot_X, self.Reg_manual_Rot_Y, self.Reg_manual_Rot_Z
    ):
        w.blockSignals(False)

    # set step size for all spinboxes
    step = self.Manual_reg_step.value()  # QDoubleSpinBox current step size
    for w in (
        self.Reg_manual_Tx, self.Reg_manual_Ty, self.Reg_manual_Tz,
        self.Reg_manual_Refx, self.Reg_manual_Refy, self.Reg_manual_Refz,
        self.Reg_manual_Rot_X, self.Reg_manual_Rot_Y, self.Reg_manual_Rot_Z
    ):
        w.setSingleStep(step)
        w.setDecimals(3)              # optional
        w.setRange(-1e6, 1e6)         # optional: sensible range