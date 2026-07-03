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
        # Sync dropdown
        ori = int(self.im_ori_comp[Caller_id])
        self.Comp_view_sel_box.blockSignals(True)
        self.Comp_view_sel_box.setCurrentIndex(ori)
        self.Comp_view_sel_box.blockSignals(False)
    
def left_button_releasecomp_event(self, caller, event):
    self.left_but_pressed[0] = 0

        
def on_scroll_backwardcomp(self, caller, event):
    Caller_id = self.interactor_to_index.get(caller)
    if Caller_id is not None:
        self.Comp_im_idx.setValue(Caller_id)
        # Sync dropdown
        ori = int(self.im_ori_comp[Caller_id])
        self.Comp_view_sel_box.blockSignals(True)
        self.Comp_view_sel_box.setCurrentIndex(ori)
        self.Comp_view_sel_box.blockSignals(False)
        self.SliderCompareView.setValue(self.SliderCompareView.value() -1) 

def on_scroll_forwardcomp(self, caller, event):
    Caller_id = self.interactor_to_index.get(caller)
    if Caller_id is not None:
        self.Comp_im_idx.setValue(Caller_id)
        # Sync dropdown
        ori = int(self.im_ori_comp[Caller_id])
        self.Comp_view_sel_box.blockSignals(True)
        self.Comp_view_sel_box.setCurrentIndex(ori)
        self.Comp_view_sel_box.blockSignals(False)
        self.SliderCompareView.setValue(self.SliderCompareView.value() +1) 


def onMouseMovecomp(self, caller, event):
    import numpy as np

    # Guard: force-reset any stuck interactor style state (e.g. dolly/zoom
    # left over from right-click context menus stealing Qt focus).
    # The Compare tab handles all interactions via custom handlers, so the
    # style should never be in any active state.
    style = caller.GetInteractorStyle()
    if style and style.GetState() != 0:
        try:
            style.StopState()
        except Exception:
            pass

    active_layer = self.layer_selected.currentIndex()
    x, y = caller.GetEventPosition()
    
    for Ax_idx in range(0, self.Comp_im_idx.maximum() + 1):
        if (Ax_idx, active_layer) not in self.display_comp_data:
            continue
            
        picker = vtk.vtkPointPicker()
        picker.Pick(x, y, 1, self.renAxComp[Ax_idx])
        world_coordinates = picker.GetPickPosition()
        
        active_coords_str = ""
        layer_values = []
        
        for l_idx in range(4):
            if (Ax_idx, l_idx) not in self.display_comp_data:
                continue
            
            ori = int(self.im_ori_comp[Ax_idx])
            axis = 2 if ori == 1 else (1 if ori == 2 else 0)
            layer_slice_idx = int(self.current_AxComp_slice_index[Ax_idx, l_idx])
            
            if not (0 <= layer_slice_idx < self.display_comp_data[Ax_idx, l_idx].shape[axis]):
                continue
                
            if ori == 0: # Axial
                slice_data = self.display_comp_data[Ax_idx, l_idx][layer_slice_idx, :, :]
            elif ori == 1: # Sagittal
                slice_data = self.display_comp_data[Ax_idx, l_idx][:, :, layer_slice_idx]
            else: # Coronal
                slice_data = self.display_comp_data[Ax_idx, l_idx][:, layer_slice_idx, :]
                
            offset = self.imageActorAxComp[Ax_idx, l_idx].GetPosition()
            adjusted_world = (
                world_coordinates[0] - offset[0],
                world_coordinates[1] - offset[1],
                world_coordinates[2] - offset[2]
            )
            image_data = self.imageActorAxComp[Ax_idx, l_idx].GetInput()
            image_id = image_data.FindPoint(adjusted_world)
            if image_id < 0:
                continue
            image_coords = image_data.GetPoint(image_id)
            spacing = self.dataImporterAxComp[Ax_idx, l_idx].GetDataSpacing()
            if spacing[0] == 0 or spacing[1] == 0:
                continue
                
            px = int(round(image_coords[0] / spacing[0]))
            py = int(round(image_coords[1] / spacing[1]))
            
            if 0 <= px < slice_data.shape[1] and 0 <= py < slice_data.shape[0]:
                val = slice_data[py, px]
                # Format: if int, no decimal. If float, 3 decimals.
                if isinstance(val, (int, np.integer)) or float(val).is_integer():
                    val_str = f"{int(val)}"
                else:
                    val_str = f"{val:.3f}"
                
                layer_values.append(f"Layer{l_idx}: {val_str}")
                
                if l_idx == active_layer:
                    active_coords_str = f"Slice:{layer_slice_idx}  ({px},{py})"
        
        if not active_coords_str:
            active_coords_str = f"Slice:{int(self.current_AxComp_slice_index[Ax_idx, active_layer])}"
            
        if layer_values:
            final_text = f"{active_coords_str}  {' '.join(layer_values)}"
        else:
            final_text = active_coords_str
            
        self.textActorAxCom[Ax_idx, 2].SetInput(final_text)
        
        # Adjust Window/Level
        if self.left_but_pressed[0] == 1 and getattr(self, '_text_dragging', False) == False:
            x0, y0 = caller.GetLastEventPosition()
            current_window = self.windowLevelAxComp[self.left_but_pressed[1], active_layer].GetWindow()
            current_level  = self.windowLevelAxComp[self.left_but_pressed[1], active_layer].GetLevel()
            if current_level == 0:
                current_level = 1
            if current_window == 0:
                current_window = 1
            DeltaW = (x - x0) * 0.01 * current_window
            DeltaL = (y - y0) * 0.01 * current_level
            Window = current_window + DeltaW
            Level  = current_level + DeltaL
               
            set_window(self, Window, Level)
            set_color_map(self)
            
        self.renAxComp[Ax_idx].GetRenderWindow().Render()