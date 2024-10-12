import vtk
from fcn_display.display_images_comp import disp_comp_image_slice
from fcn_display.colormap_set import set_color_map
from fcn_display.win_level import set_window
import time

def left_button_presscomp_event(self, caller, event):
    Caller_id = self.interactor_to_index.get(caller)
    if Caller_id is not None:
        self.Comp_im_idx.setValue(Caller_id)
        self.left_but_pressed[0] = 1
        self.left_but_pressed[1] = Caller_id
    
def left_button_releasecomp_event(self, caller, event):
    self.left_but_pressed[0] = 0

        
def on_scroll_backwardcomp(self, caller, event):
    Caller_id = self.interactor_to_index.get(caller)
    if Caller_id is not None:
        self.Comp_im_idx.setValue(Caller_id)
        self.SliderCompareView.setValue(self.SliderCompareView.value() -1) 

def on_scroll_forwardcomp(self, caller, event):
    Caller_id = self.interactor_to_index.get(caller)
    if Caller_id is not None:
        self.Comp_im_idx.setValue(Caller_id)
        self.SliderCompareView.setValue(self.SliderCompareView.value() +1) 


def onMouseMovecomp(self, caller, event):
    layer = self.layer_selection_box.currentIndex()
    for Ax_idx in range (0,self.Comp_im_idx.maximum()+1):
        if not ((Ax_idx, layer) in self.display_comp_data and int(self.current_AxComp_slice_index[Ax_idx, layer]) in self.display_comp_data[Ax_idx, layer]):
            continue
        # if self.current_axial_slice_index[idx]==-1:
        #     return
        if self.im_ori_comp[Ax_idx] ==0: #Axial
            slice_data = self.display_comp_data[Ax_idx, layer][int(self.current_AxComp_slice_index[Ax_idx,layer]), :, :]
        elif self.im_ori_comp[Ax_idx] ==1: #Sagittal 
            slice_data = self.display_comp_data[Ax_idx, layer][:,:,int(self.current_AxComp_slice_index[Ax_idx,layer])]
        elif self.im_ori_comp[Ax_idx] ==2: #Coronal
            slice_data = self.display_comp_data[Ax_idx, layer][:,int(self.current_AxComp_slice_index[Ax_idx,layer]), :]
        #    
        # Get the position of the mouse
        x, y = caller.GetEventPosition()
        # Get previous event position
        x0, y0 = caller.GetLastEventPosition()
        # # # Initialize a point picker
        picker = vtk.vtkPointPicker()
        # Use the picker to get world coordinates
        picker.Pick(x, y, 1, self.renAxComp[Ax_idx])   
        world_coordinates = picker.GetPickPosition()
        #
        # Adjust the picked world coordinates by the offset
        offset = self.imageActorAxComp[Ax_idx,layer].GetPosition()
        adjusted_world_coordinates = (world_coordinates[0] - offset[0], 
                                      world_coordinates[1] - offset[1], 
                                      world_coordinates[2] - offset[2])
        # Get the image data from the image actor
        image_data = self.imageActorAxComp[Ax_idx,layer].GetInput()
        # Convert world coordinates to image coordinates
        image_id = image_data.FindPoint(adjusted_world_coordinates)
        image_coords = image_data.GetPoint(image_id)
        # adjust coordinates to account for pixel size and offset
        spacing = self.dataImporterAxComp[Ax_idx, layer].GetDataSpacing()
        image_coord_vox    = list(image_coords)
        image_coord_vox[0] = int(image_coord_vox[0]/spacing[0])
        image_coord_vox[1] = int(image_coord_vox[1]/spacing[1])
        #
        # Make sure the image coordinates are within the image bounds
        # if (0 <= image_coord_vox[0] < slice_data.shape[1] and
        #         0 <= image_coord_vox[1] < slice_data.shape[0]) or self.selected_point is not None:
        pixel_value = slice_data[image_coord_vox[1], image_coord_vox[0]]    
        # 
        self.textActorAxCom[Ax_idx,2].SetInput(f"Slice:{self.current_AxComp_slice_index[Ax_idx,layer]}  ({image_coord_vox[0]},{image_coord_vox[1]}) {round(pixel_value,4):.4f}")
        #
        if self.left_but_pressed[0] == 1:
            current_window = self.windowLevelAxComp[self.left_but_pressed[1],layer].GetWindow()
            current_level  = self.windowLevelAxComp[self.left_but_pressed[1],layer].GetLevel()
            if current_level==0:
                current_level=1
            if current_window==0:
                current_window=1
            # Data can be in the range of 1 (RED and SPR) or 10 (Zeff)
            # so the adjustment needs to be done in smaller increments in this region
            DeltaW = (x-x0)*0.01*current_window
            DeltaL = (y-y0)*0.01*current_level
            Window = current_window + DeltaW
            Level  = current_level  + DeltaL
            #    
            set_window(self,Window,Level)
            set_color_map(self)
        #
        self.renAxComp[Ax_idx].GetRenderWindow().Render()