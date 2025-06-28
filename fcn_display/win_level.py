from fcn_display.display_images   import displayaxial, displaycoronal, displaysagittal
from fcn_display.display_images_seg import disp_seg_image_slice
from fcn_display.display_images_IrISeval import disp_eval_iris_slice
from PyQt5.QtWidgets import QInputDialog
import numpy as np
from fcn_display.colormap_set import set_color_map


def window_auto(self):
    idx = self.layer_selection_box.currentIndex()
    data = self.display_data.get(idx)
    if data is None or (hasattr(data, 'size') and data.size == 0):
        return
    currentTabText = self.tabModules.tabText(self.tabModules.currentIndex())
    if currentTabText == "Segmentation":
        slice_data = self.display_seg_data[0][self.current_slice_index[0], :, :]
    else:
        slice_data = self.display_data[idx][self.current_slice_index[0], :, :]
    Window = np.std(slice_data)*2
    Level  = np.mean(slice_data)
    set_window(self,Window,Level)
    
def set_window(self,Window,Level):
    # check which tab is selecgted to apply it to the correct axes
    currentTabText = self.tabModules.tabText(self.tabModules.currentIndex())
    layer = self.layer_selection_box.currentIndex()
    data = self.display_data.get(layer)
    if data is None or (hasattr(data, 'size') and data.size == 0):
        return
    if currentTabText == "View":
        self.windowLevelAxial[layer].SetWindow(Window)
        self.windowLevelAxial[layer].SetLevel(Level)
        self.windowLevelSagittal[layer].SetWindow(Window)
        self.windowLevelSagittal[layer].SetLevel(Level)
        self.windowLevelCoronal[layer].SetWindow(Window)
        self.windowLevelCoronal[layer].SetLevel(Level)
        self.textActorAxialWL.SetInput(f"L: {round(Level,2)}  W: {round(Window,2)}")
        self.textActorSagittalWL.SetInput(f"L: {round(Level,2)}  W: {round(Window,2)}")
        self.textActorCoronalWL.SetInput(f"L: {round(Level,2)}  W: {round(Window,2)}")   
        set_color_map(self)
        displayaxial(self)
        displaysagittal(self)
        displaycoronal(self)
    elif currentTabText == "IrIS":
        self.windowLevelIrEval[layer].SetWindow(Window)
        self.windowLevelIrEval[layer].SetLevel(Level)
        disp_eval_iris_slice(self)
    elif currentTabText == "Compare":
        if Window == -99: # code to syn all windows using the first as reference
            Window = self.windowLevelAxComp[self.Comp_im_idx.value(),layer].GetWindow()
            Level  = self.windowLevelAxComp[self.Comp_im_idx.value(),layer].GetLevel()
        if self.link_win_lev.isChecked():
            r_1 = 0;
            r_2 = self.Comp_im_idx.maximum()+1;
        else:
            if self.left_but_pressed[0]==1:
                r_1 = int(self.left_but_pressed[1])
            else:                  
                r_1 = self.Comp_im_idx.value();
            r_2 = r_1+ 1
        for Ax_idx in range (r_1,r_2):
            if not ((Ax_idx, layer) in self.display_comp_data and int(self.current_AxComp_slice_index[Ax_idx, layer]) in self.display_comp_data[Ax_idx, layer]):
                continue
            self.windowLevelAxComp[Ax_idx,layer].SetWindow(Window)
            self.windowLevelAxComp[Ax_idx,layer].SetLevel(Level)
            self.textActorAxCom[Ax_idx,1].SetInput(f"L: {round(Level,2)}  W: {round(Window,2)}")
            
    elif currentTabText == "Segmentation":
        self.seg_win_lev = [Window, Level]
        self.windowLevelSeg[layer].SetWindow(Window)
        self.windowLevelSeg[layer].SetLevel(Level)
        self.textActorSeg[1].SetInput(f"L: {round(Level,2)}  W: {round(Window,2)}")
        disp_seg_image_slice(self)
            
            

def window_lung(self):
    Window = 1500
    Level  = -600
    set_window(self,Window,Level)
    
def window_stissue(self):
    Window = 200
    Level  =   0
    set_window(self,Window,Level)
    
def window_bone(self):
    Window =  500
    Level  = 1200
    set_window(self,Window,Level)
    
def window_sprred(self):
    Window =  0.4
    Level  =  1
    set_window(self,Window,Level)
    
def window_zeff(self):
    Window =  4
    Level  =  8
    set_window(self,Window,Level)    

def window_IrIS_1(self):
    Window =  2000
    Level  =  2000
    set_window(self,Window,Level)  
       
def window_IrIS_2(self):
    Window =  5000
    Level  =  5000
    set_window(self,Window,Level)  
      
def window_IrIS_3(self):
    Window =  10000
    Level  =  10000
    set_window(self,Window,Level)      
    
def window_IrIS_4(self):
    Window =  20000
    Level  =  20000
    set_window(self,Window,Level)   
    
def window_custom(self):
    # Ask for Window value
    Window, ok1 = QInputDialog.getInt(self, "Input Window", "Enter Window value:", min=0, max=1000000, step=1)
    if not ok1:
        return  # User cancelled or closed the dialog
    # Ask for Level value
    Level, ok2 = QInputDialog.getInt(self, "Input Level", "Enter Level value:", min=-1000000, max=1000000, step=1)
    if not ok2:
        return  # User cancelled or closed the dialog
    set_window(self,Window,Level)
            
