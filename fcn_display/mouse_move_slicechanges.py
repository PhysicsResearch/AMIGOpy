import numpy as np
import vtk
import math
from fcn_display.display_images  import displayaxial, displaycoronal, displaysagittal
from fcn_display.colormap_set import set_color_map
from fcn_display.win_level import set_window


def onMouseMoveAxial(self, caller, event):
    idx = self.layer_selection_box.currentIndex()
    
    if self.current_axial_slice_index[idx]==-1:
        return
    if self.display_data[idx].ndim==2:
        slice_data = self.display_data[idx]
    else:
        slice_data = self.display_data[idx][self.current_axial_slice_index[idx], :, :]
    # Get the position of the mouse
    x, y = caller.GetEventPosition()
    # Get previous event position
    x0, y0 = caller.GetLastEventPosition()
    # # # Initialize a point picker
    picker = vtk.vtkPointPicker()
    # Use the picker to get world coordinates
    picker.Pick(x, y, 1, self.renAxial)   
    world_coordinates = picker.GetPickPosition()
    #
    # Adjust the picked world coordinates by the offset
    offset = self.imageActorAxial[idx].GetPosition()
    adjusted_world_coordinates = (world_coordinates[0] - offset[0], 
                                  world_coordinates[1] - offset[1], 
                                  world_coordinates[2] - offset[2])
    # Get the image data from the image actor
    image_data = self.imageActorAxial[idx].GetInput()
    # Convert world coordinates to image coordinates
    image_id = image_data.FindPoint(adjusted_world_coordinates)
    image_coords = image_data.GetPoint(image_id)
    # adjust coordinates to account for pixel size and offset
    image_coord_vox    = list(image_coords)
    image_coord_vox[0] = int(image_coord_vox[0]/self.pixel_spac[idx,1])
    image_coord_vox[1] = int(image_coord_vox[1]/self.pixel_spac[idx,0])
    # image_coords will be a tuple (x, y, z)
    #    slice_data = self.display_data[idx][self.current_axial_slice_index[idx], :, :]
    # Make sure the image coordinates are within the image bounds
    if (0 <= image_coord_vox[0] < slice_data.shape[1] and
            0 <= image_coord_vox[1] < slice_data.shape[0]) or self.selected_point is not None:
        pixel_value = slice_data[image_coord_vox[1], image_coord_vox[0]]    
        if self.DataType == "IrIS":
            self.textActorAxialMetaTime.SetInput(f"Time {self.IrIS_data[self.patientID]['AcquisitionTime'][int(self.current_axial_slice_index[idx])]:.2f} s")
            self.textActorAxial.SetInput(f"Slice: {self.current_axial_slice_index[idx]} ({int(image_coords[0])}, {int(image_coords[1])}) px  "
                                         f"({(image_coords[0]*self.IrIS_data[self.patientID]['Resolution']*10):.2f}, {(image_coords[1]*self.IrIS_data[self.patientID]['Resolution']*10):.2f}) mm  "
                                         f"Value: {round(pixel_value,3)} ")
        elif self.DataType == "DICOM":
            # convert values to mm
            P_mm = self.current_axial_slice_index[idx] * self.slice_thick[idx] + self.Im_Offset[idx,2]
            self.textActorAxial.SetInput(f"Slice: {P_mm:.2f} mm ({image_coord_vox[0]}, {self.current_axial_slice_index[idx]}, {image_coord_vox[1]}) {round(pixel_value,4):.4f}")
    else:
        P_mm = self.current_axial_slice_index[idx] * self.slice_thick[idx] + self.Im_Offset[idx,2]
        self.textActorAxial.SetInput(f"Slice: {self.current_axial_slice_index[idx]} - {P_mm:.2f} mm")


    if self.selected_point == 0: 
        self.endpoints_Ruller_axial01.SetCenter([image_coords[0],image_coords[1],0.01])
        self.endpoints_Ruller_axial01.Modified() 
        self.axialRullerSource.SetPoint1(image_coords[0],image_coords[1], 0)
        self.axialRullerSource.Modified() 
    elif self.selected_point == 1: 
        self.endpoints_Ruller_axial02.SetCenter([image_coords[0],image_coords[1],0])
        self.endpoints_Ruller_axial02.Modified() 
        self.axialRullerSource.SetPoint2(image_coords[0],image_coords[1], 0.01)
        self.axialRullerSource.Modified() 
        
    if self.selected_point is not None:
        p1 = self.endpoints_Ruller_axial01.GetCenter();    
        p2 = self.endpoints_Ruller_axial02.GetCenter();
        
        # Calculate the distance
        distance = math.sqrt((p2[0] - p1[0]) ** 2 +
                             (p2[1] - p1[1]) ** 2 +
                             (p2[2] - p1[2]) ** 2)
        if self.DataType == "IrIS":
            d_mm = self.IrIS_data[self.patientID]['Resolution'] * distance * 10
                                                 
#        self.textActorAxialRuller.SetInput(f"({p1[0]:.0f}, {p1[1]:.0f})\n\n({p2[0]:.0f}, {p2[1]:.0f})\n\n{distance:.2f} px\n\n{d_mm:.2f} mm")
        
    if self.LeftButtonAxialDown == True and self.LeftButtonRuler == False:
        idx = self.layer_selection_box.currentIndex()
        current_window = self.windowLevelAxial[idx].GetWindow()
        current_level  = self.windowLevelAxial[idx].GetLevel()
        if -0.001<current_level<0.001:
            DeltaL = (y-y0)*0.01
        else:
            DeltaL = (y-y0)*0.01*abs(current_level)
        if current_window==0:
            DeltaW = (x-x0)*0.01
        else:
            DeltaW = (x-x0)*0.01*abs(current_window)
        Window = self.windowLevelAxial[idx].GetWindow() + DeltaW
        Level  = self.windowLevelAxial[idx].GetLevel()  + DeltaL
        #    
        set_window(self,Window,Level)
            
    # Render the updated data (to refresh the displayed text)
    self.vtkWidgetAxial.GetRenderWindow().Render()
    
    
    
def left_button_pressaxial_event(self, caller, event):
    self.LeftButtonAxialDown = True
    #print("obj methods and attributes:", dir(caller))
    #print("event methods and attributes:", dir(event))
    # interactor = caller.GetInteractor()
    # mouse_pos = interactor.GetEventPosition()
    mouse_pos = self.vtkWidgetAxial.GetEventPosition()
    picker = vtk.vtkPropPicker()
    picker.Pick(mouse_pos[0], mouse_pos[1], 0, self.renAxial)
    picked_actor = picker.GetActor()
    if hasattr(self, 'endpoints_Ruller_axialactor01') and picked_actor == self.endpoints_Ruller_axialactor01:
        self.selected_point  = 0
        self.LeftButtonRuler = True  
    elif hasattr(self, 'endpoints_Ruller_axialactor01') and picked_actor == self.endpoints_Ruller_axialactor02:
        self.selected_point  = 1   
        self.LeftButtonRuler = True  
    else:
        self.selected_point = None

def left_button_releaseaxial_event(self, obj, event):
        self.LeftButtonAxialDown = False
        self.selected_point      = None  
        self.LeftButtonRuler     = False         
        
def onMouseMoveSagittal(self, caller, event):
    idx = self.layer_selection_box.currentIndex()
    if self.current_axial_slice_index[idx]==-1:
        return
    if self.display_data[idx].ndim==2:
        return
    # Get the position of the mouse
    x, y = caller.GetEventPosition()
    
    # Get previous event position
    x0, y0 = caller.GetLastEventPosition()
    idx = self.layer_selection_box.currentIndex()
    if self.LeftButtonSagittalDown:
        current_window = self.windowLevelSagittal[idx].GetWindow()
        current_level  = self.windowLevelSagittal[idx].GetLevel()
        # Data can be in the range of 1 (RED and SPR) or 10 (Zeff)
        # so the adjustment needs to be done in smaller increments in this region
        if -0.001<current_level<0.001:
            DeltaL = (y-y0)*0.01
        else:
            DeltaL = (y-y0)*0.01*current_level   
        if current_window==0:
            DeltaW = (x-x0)*0.01
        else:
            DeltaW = (x-x0)*0.01*current_window
        Window = self.windowLevelSagittal[idx].GetWindow() + DeltaW
        Level  = self.windowLevelSagittal[idx].GetLevel()  + DeltaL
        if Window < 0:
            Window = self.windowLevelSagittal[idx].GetWindow()
        #    
        set_window(self,Window,Level)
    
    # Initialize a point picker
    picker = vtk.vtkPointPicker()
    # Use the picker to get world coordinates
    picker.Pick(x, y, 0, self.renSagittal)  # Assuming self.ren is your vtkRenderer
    world_coordinates = picker.GetPickPosition()
    # Adjust the picked world coordinates by the offset
    offset = self.imageActorSagittal[idx].GetPosition()
    adjusted_world_coordinates = (world_coordinates[0] - offset[0], 
                                  world_coordinates[1] - offset[1], 
                                  world_coordinates[2] - offset[2])
    # Get the image data from the image actor
    image_data = self.imageActorSagittal[idx].GetInput()

    # Convert world coordinates to image coordinates
    image_id     = image_data.FindPoint(adjusted_world_coordinates)
    image_coords = image_data.GetPoint(image_id)
    image_coord_vox    = list(image_coords)
    image_coord_vox[0] = int(image_coord_vox[0]/self.pixel_spac[idx,0])
    image_coord_vox[1] = int(image_coord_vox[1]/self.slice_thick[idx])
    # image_coords will be a tuple (x, y, z)
    if self.display_data[idx].ndim==2:
        slice_data = self.display_data[idx]
    else:
        slice_data = self.display_data[idx][:, :, self.current_sagittal_slice_index[idx]]
    # slice_data = np.flipud(slice_data);
    # Make sure the image coordinates are within the image bounds
    P_mm = self.current_sagittal_slice_index[idx] * self.pixel_spac[idx,1] + self.Im_Offset[idx,0]
    if (0 <= image_coord_vox[0] < slice_data.shape[1]
        and 0 <= image_coord_vox[1] < slice_data.shape[0]):
        pixel_value = slice_data[image_coord_vox[1],image_coord_vox[0]]
        self.textActorSagittal.SetInput (f"Slice: {P_mm:.1f} mm ({self.current_sagittal_slice_index[idx]}, {image_coord_vox[0]}, {image_coord_vox[1]}) {round(pixel_value,4):.4f}")
    else:
        self.textActorSagittal.SetInput(f"Slice: {self.current_sagittal_slice_index[idx]} - Slice: {P_mm:.2f} mm")
    
    if self.DataType == "IrIS":
        self.textActorSagittalMetaTime.SetInput(f"Time {self.IrIS_data[self.patientID]['AcquisitionTime'][int(image_coords[1])]:.2f} s")


    # Render the updated data (to refresh the displayed text)
    self.vtkWidgetSagittal.GetRenderWindow().Render()

def onMouseMoveCoronal(self, caller, event):
    idx = self.layer_selection_box.currentIndex()
    if self.current_axial_slice_index[idx]==-1:
        return
    if self.display_data[idx].ndim==2:
        return
    # Get the position of the mouse
    x, y = caller.GetEventPosition()
    # Get previous event position
    x0, y0 = caller.GetLastEventPosition()
    #
    idx = self.layer_selection_box.currentIndex()
    #
    if self.LeftButtonCoronalDown:
        current_window = self.windowLevelCoronal[idx].GetWindow()
        current_level  = self.windowLevelCoronal[idx].GetLevel()
        # Data can be in the range of 1 (RED and SPR) or 10 (Zeff)
        # so the adjustment needs to be done in smaller increments in this region
        DeltaW = (x-x0)*0.01*current_window
        DeltaL = (y-y0)*0.01*current_level
        if current_level==0:
            current_level=1
        if current_window==0:
            current_window=1
        #
        Window = self.windowLevelCoronal[idx].GetWindow() + DeltaW
        Level  = self.windowLevelCoronal[idx].GetLevel()   + DeltaL
        set_window(self,Window,Level)

    # Initialize a point picker
    picker = vtk.vtkPointPicker()

    # Use the picker to get world coordinates
    picker.Pick(x, y, 0, self.renCoronal)  # Assuming self.ren is your vtkRenderer
    world_coordinates = picker.GetPickPosition()
    # Adjust the picked world coordinates by the offset
    offset = self.imageActorCoronal[idx].GetPosition()
    adjusted_world_coordinates = (world_coordinates[0] - offset[0], 
                                  world_coordinates[1] - offset[1], 
                                  world_coordinates[2] - offset[2])
    # Get the image data from the image actor
    image_data = self.imageActorCoronal[idx].GetInput()
    
    # Convert world coordinates to image coordinates
    image_id = image_data.FindPoint(adjusted_world_coordinates)
    image_coords = image_data.GetPoint(image_id)
    # Convert world coordinates to image coordinates
    image_id     = image_data.FindPoint(adjusted_world_coordinates)
    image_coords = image_data.GetPoint(image_id)
    image_coord_vox    = list(image_coords)
    image_coord_vox[0] = int(image_coord_vox[0]/self.pixel_spac[idx,1])
    image_coord_vox[1] = int(image_coord_vox[1]/self.slice_thick[idx])
    # image_coords will be a tuple (x, y, z)
    slice_data = self.display_data[idx][:, self.current_coronal_slice_index[idx], :]
    #slice_data = np.flipud(slice_data);
    # Make sure the image coordinates are within the image bounds
    P_mm = self.current_coronal_slice_index[idx] * self.pixel_spac[idx,0] + self.Im_Offset[idx,0]
    if (0 <= image_coord_vox[0] < slice_data.shape[1] and
            0 <= image_coord_vox[1] < slice_data.shape[0]*self.pixel_spac[idx,0]):
        pixel_value = slice_data[image_coord_vox[1], image_coord_vox[0]]
        self.textActorCoronal.SetInput(f"Slice: {P_mm:.1f} mm ({image_coord_vox[0]}, {image_coord_vox[1]}, {self.current_coronal_slice_index[idx]}) {round(pixel_value,4):.4f}")
    else:
        self.textActorCoronal.SetInput(f"Slice: {self.current_coronal_slice_index[idx]}  -  Slice: {P_mm:.2f} mm")
    
         
    if self.DataType == "IrIS":
        self.textActorCoronalMetaTime.SetInput(f"Time {self.IrIS_data[self.patientID]['AcquisitionTime'][int(image_coords[1])]:.2f} s")

    
    # Render the updated data (to refresh the displayed text)
    self.vtkWidgetCoronal.GetRenderWindow().Render()
 
    
def change_sliceAxial(self, delta):
    idx = self.layer_selection_box.currentIndex()
    # Modify the current slice index
    self.current_axial_slice_index[idx] += delta
    # Ensure slice index is within bounds
    if self.current_axial_slice_index[idx] < 0:
        self.current_axial_slice_index[idx] = 0
    elif self.current_axial_slice_index[idx] >= self.display_data[idx].shape[0]:
        self.current_axial_slice_index[idx] = self.display_data[idx].shape[0] - 1
    # Update the display
    displayaxial(self)
    self.textActorAxial.SetInput(f"Slice: {self.current_axial_slice_index[idx]}")
    # Update the slider's value to match the current slice index
    self.AxialSlider.setValue(self.current_axial_slice_index[idx])
    
    if self.DataType == "IrIS":
        self.textActorAxialMetaTime.SetInput(f"Time {self.IrIS_data[self.patientID]['AcquisitionTime'][int(self.current_axial_slice_index[idx])]:.2f} s")
        
        
        
def change_sliceSagittal(self, delta):
    idx = self.layer_selection_box.currentIndex()
    # Modify the current slice index
    self.current_sagittal_slice_index[idx] += delta
    # Ensure slice index is within bounds
    if self.current_sagittal_slice_index[idx] < 0:
        self.current_sagittal_slice_index[idx] = 0
    elif self.current_sagittal_slice_index[idx] >= self.display_data[idx].shape[2]:
        self.current_sagittal_slice_index[idx] = self.display_data[idx].shape[2] - 1
    # Update the display
    displaysagittal(self)
    self.textActorSagittal.SetInput(f"Slice: {self.current_sagittal_slice_index[idx]}")
    # Update the slider's value to match the current slice index
    self.SagittalSlider.setValue(self.current_sagittal_slice_index[idx])        
    
    
def change_sliceCoronal(self, delta):
    idx = self.layer_selection_box.currentIndex()
    # Modify the current slice index
    self.current_coronal_slice_index[idx] += delta
    # Ensure slice index is within bounds
    if self.current_coronal_slice_index[idx] < 0:
        self.current_coronal_slice_index[idx] = 0
    elif self.current_coronal_slice_index[idx] >= self.display_data[idx].shape[1]:
        self.current_coronal_slice_index[idx] = self.display_data[idx].shape[1] - 1
    # Update the display
    displaycoronal(self)
    self.textActorCoronal.SetInput(f"Slice: {self.current_coronal_slice_index[idx]}")
    # Update the slider's value to match the current slice index
    self.CoronalSlider.setValue(self.current_coronal_slice_index[idx])   