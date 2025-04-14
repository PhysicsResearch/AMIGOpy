from fcn_display.mouse_move_slicechanges import onMouseMoveSeg, left_button_pressseg_event, left_button_releaseseg_event



def init_seg_image_Actor(self):
    self.dataImporterSeg = {}
    self.windowLevelSeg = {}
    self.imageActorSeg = {}
    for i in range(4):  # Assuming 4 layers, adjust the range as needed
        self.dataImporterSeg[i] = vtk.vtkImageImport()
        self.windowLevelSeg[i]  = vtk.vtkImageMapToWindowLevelColors()
        self.windowLevelSeg[i].SetInputConnection(self.dataImporterSeg[i].GetOutputPort())
        self.imageActorSeg[i] = vtk.vtkImageActor()
        self.imageActorSeg[i].GetMapper().SetInputConnection(self.windowLevelSeg[i].GetOutputPort())


def setup_vtk_seg(self):
    populate_layer_list(self)
    # Initialize VTK components - View section - Axial - Sagittal and Coronal
    vtk_layoutSeg = QVBoxLayout()
    self.vtkWidgetSeg = QVTKRenderWindowInteractor()
    vtk_layoutSeg.addWidget(self.vtkWidgetSeg)
    self.VTK_SegView.setLayout(vtk_layoutSeg)
    # Create the renderer here
    self.renSeg = vtk.vtkRenderer()
    self.vtkWidgetSeg.GetRenderWindow().AddRenderer(self.renSeg)
    #
    init_text_actor_seg(self)
    # Start the VTK widget
    self.vtkWidgetSeg.Initialize()  
    self.vtkWidgetSeg.Start() 
    #
    imageStyle = vtk.vtkInteractorStyleImage()
    self.vtkWidgetSeg.SetInteractorStyle(imageStyle)
    # 
    init_seg_image_Actor(self)
    #
    self.renSeg.GetActiveCamera().SetParallelProjection(1)
    #
    set_mouse_button_custom_fcn_seg(self)
    #
    init_display_empty_image_seg(self)  
    #
    init_add_image_actor_seg(self)
    
    
            
def init_add_image_actor_seg(self):
    for i in range(len(self.dataImporterSeg)):
        self.renSeg.AddActor(self.imageActorSeg[i])
    self.renSeg.ResetCamera()


def init_display_empty_image_seg(self):   
    slice_data = np.zeros((100, 100), dtype=np.uint16)
    data_string = slice_data.tobytes()
    extent = slice_data.shape
    # initialize display image
    for i in range(len(self.dataImporterSeg)):
        self.dataImporterSeg[i].SetDataScalarTypeToUnsignedShort()
        #
        self.dataImporterSeg[i].CopyImportVoidPointer(data_string, len(data_string))
        self.dataImporterSeg[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        self.dataImporterSeg[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        imageProperty = self.imageActorSeg[i].GetProperty()
        imageProperty.SetOpacity(0)  
        # Inform the pipeline that data has changed.
        self.dataImporterSeg[i].Modified()  
    
    
    
def init_text_actor_seg(self):
    # Initialize the text actor and set its properties - Coronal
    self.textActorSeg = vtk.vtkTextActor()
    self.textActorSeg.GetTextProperty().SetFontFamilyToArial()
    self.textActorSeg.GetTextProperty().SetFontSize(12)
    self.textActorSeg.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  # white color
    self.textActorSeg.SetPosition(10, 10)  # position at the bottom left
    # used for windowlevel and widht at top-left
    self.textActorSegWL = vtk.vtkTextActor()
    self.textActorSegWL.GetTextProperty().SetFontFamilyToArial()
    self.textActorSegWL.GetTextProperty().SetFontSize(12)
    self.textActorSegWL.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorSegWL.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorSegWL.SetPosition(0.01, 0.95)  # Near top-left corner
    # used for
    self.textActorSegInfo = vtk.vtkTextActor()
    self.textActorSegInfo.GetTextProperty().SetFontFamilyToArial()
    self.textActorSegInfo.GetTextProperty().SetFontSize(12)
    self.textActorSegInfo.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorSegInfo.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorSegInfo.SetPosition(0.70, 0.88)  # Near top-right corner
    # used for IrIS time
    self.textActorSegMetaTime = vtk.vtkTextActor()
    self.textActorSegMetaTime.GetTextProperty().SetFontFamilyToArial()
    self.textActorSegMetaTime.GetTextProperty().SetFontSize(12)
    self.textActorSegMetaTime.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorSegMetaTime.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorSegMetaTime.SetPosition(0.01, 0.90)  # Near top-left corner
    #
    self.renSeg.AddActor(self.textActorSeg)
    self.renSeg.AddActor(self.textActorSegWL)
    self.renSeg.AddActor(self.textActorSegMetaTime)
    self.renSeg.AddActor(self.textActorSegInfo)
    
    
    
    
    
def init_coord_ref_ax_seg(self):
    
    self.axesActorSeg = vtkAxesActor()
    # Hide the Z label
    self.axesActorSeg.GetYAxisCaptionActor2D().GetTextActor().GetTextProperty().SetOpacity(0)
    self.axesActorSeg.GetXAxisShaftProperty().SetLineWidth(2)
    self.axesActorSeg.GetYAxisShaftProperty().SetLineWidth(2)
    self.axesActorSeg.GetZAxisShaftProperty().SetLineWidth(2)
    self.axesActorSeg.SetScale(10)  
    self.axesActorSeg.SetConeRadius(0.2)
    
    transform = vtkTransform()
    if self.segSelectView.currentText() == "Axial":
        transform.RotateX(-90)
    elif self.segSelectView.currentText() == "Sagittal":
        transform.RotateZ(90)
        transform.RotateY(90)
        transform.RotateX(90)
        
    # Set the transform to the actor
    self.axesActorSeg.SetUserTransform(transform)
    
    
    
def set_mouse_button_custom_fcn_seg(self):
     # After setting up your vtkWidget and renderer:
     interactor_styleSeg = self.vtkWidgetSeg.GetInteractorStyle()
     interactor_styleSeg.AddObserver("MouseWheelForwardEvent", self.on_scroll_forwardSeg)
     interactor_styleSeg.AddObserver("MouseWheelBackwardEvent", self.on_scroll_backwardSeg)
     interactor_styleSeg.AddObserver("LeftButtonReleaseEvent", lambda caller, event: left_button_releaseseg_event(self, caller, event))
     interactor_styleSeg.AddObserver("LeftButtonPressEvent", lambda caller, event: left_button_pressseg_event(self, caller, event))
     interactor_styleSeg.OnMouseWheelForward = lambda: None
     interactor_styleSeg.OnMouseWheelBackward = lambda: None
     interactor_styleSeg.OnLeftButtonDown = lambda: None
     interactor_styleSeg.OnLeftButtonUp = lambda: None
     
     #
     self.vtkWidgetSeg.AddObserver("LeftButtonPressEvent", lambda caller, event: left_button_pressseg_event(self, caller, event),0)
     self.vtkWidgetSeg.AddObserver("LeftButtonReleaseEvent",lambda caller, event:left_button_releaseseg_event(self, caller, event),0)
     # mouse
     self.vtkWidgetSeg.AddObserver("MouseWheelForwardEvent", self.on_scroll_forwardSeg)
     self.vtkWidgetSeg.AddObserver("MouseWheelBackwardEvent", self.on_scroll_backwardSeg)
     #
     self.vtkWidgetSeg.GetRenderWindow().GetInteractor().AddObserver("MouseMoveEvent",lambda caller, event:onMouseMoveSeg(self, caller, event))
     
     
def left_button_pressseg_event(self, obj, event):
    self.LeftButtonSegDown = True
    
def left_button_releaseseg_event(self, obj, event):
    self.LeftButtonSegDown = False
    
    
    
def onMouseMoveSeg(self, caller, event):
    idx = self.layer_selection_box.currentIndex()
    if self.current_seg_slice_index[idx]==-1:
        return
    if self.display_data_seg[idx].ndim==2:
        return
    # Get the position of the mouse
    x, y = caller.GetEventPosition()
    # Get previous event position
    x0, y0 = caller.GetLastEventPosition()
    #
    idx = self.layer_selection_box.currentIndex()
    #
    if self.LeftButtonSegDown:
        current_window = self.windowLevelSeg[idx].GetWindow()
        current_level  = self.windowLevelSeg[idx].GetLevel()
        # Data can be in the range of 1 (RED and SPR) or 10 (Zeff)
        # so the adjustment needs to be done in smaller increments in this region
        DeltaW = (x-x0)*0.01*current_window
        DeltaL = (y-y0)*0.01*current_level
        if current_level==0:
            current_level=1
        if current_window==0:
            current_window=1
        #
        Window = self.windowLevelSeg[idx].GetWindow() + DeltaW
        Level  = self.windowLevelSeg[idx].GetLevel()   + DeltaL
        set_window(self,Window,Level)

    # Initialize a point picker
    picker = vtk.vtkPointPicker()

    # Use the picker to get world coordinates
    picker.Pick(x, y, 0, self.renSeg)  # Assuming self.ren is your vtkRenderer
    world_coordinates = picker.GetPickPosition()
    # Adjust the picked world coordinates by the offset
    offset = self.imageActorSeg[idx].GetPosition()
    adjusted_world_coordinates = (world_coordinates[0] - offset[0], 
                                  world_coordinates[1] - offset[1], 
                                  world_coordinates[2] - offset[2])
    # Get the image data from the image actor
    image_data = self.imageActorSeg[idx].GetInput()
    
    # Convert world coordinates to image coordinates
    image_id = image_data.FindPoint(adjusted_world_coordinates)
    image_coords = image_data.GetPoint(image_id)
    # Convert world coordinates to image coordinates
    image_id     = image_data.FindPoint(adjusted_world_coordinates)
    image_coords = image_data.GetPoint(image_id)
    image_coord_vox    = list(image_coords)
    
    if self.segSelectView.currentText() == "Axial":
        image_coord_vox[0] = int(image_coord_vox[0]/self.pixel_spac[idx,1])
        image_coord_vox[1] = int(image_coord_vox[1]/self.pixel_spac[idx,0])
        if self.display_data_seg[idx].ndim==2:
            slice_data = self.display_data_seg[idx]
        else:
            slice_data = self.display_data_seg[idx][self.current_axial_slice_index[idx], :, :]
        P_mm = self.current_axial_slice_index[idx] * self.slice_thick[idx] + self.Im_Offset[idx,2]
        if (0 <= image_coord_vox[0] < slice_data.shape[1] and
                0 <= image_coord_vox[1] < slice_data.shape[0]) or self.selected_point is not None:
            pixel_value = slice_data[image_coord_vox[1], image_coord_vox[0]]    
            self.textActorAxial.SetInput(f"Slice: {P_mm:.2f} mm ({image_coord_vox[0]}, {self.current_axial_slice_index[idx]}, {image_coord_vox[1]}) {round(pixel_value,4):.4f}")
        else:
            self.textActorAxial.SetInput(f"Slice: {self.current_axial_slice_index[idx]} - {P_mm:.2f} mm")
            
    elif self.segSelectView.currentText() == "Coronal":
        image_coord_vox[0] = int(image_coord_vox[0]/self.pixel_spac[idx,1])
        image_coord_vox[1] = int(image_coord_vox[1]/self.slice_thick[idx])
        if self.display_data_seg[idx].ndim==2:
            slice_data = self.display_data_seg[idx]
        else:
            slice_data = self.display_data_seg[idx][:, self.current_coronal_slice_index[idx], :]
        P_mm = self.current_coronal_slice_index[idx] * self.pixel_spac[idx,0] + self.Im_Offset[idx,0]
        if (0 <= image_coord_vox[0] < slice_data.shape[1] and
                0 <= image_coord_vox[1] < slice_data.shape[0]*self.pixel_spac[idx,0]):
            pixel_value = slice_data[image_coord_vox[1], image_coord_vox[0]]
            self.textActorCoronal.SetInput(f"Slice: {P_mm:.1f} mm ({image_coord_vox[0]}, {image_coord_vox[1]}, {self.current_coronal_slice_index[idx]}) {round(pixel_value,4):.4f}")
        else:
            self.textActorCoronal.SetInput(f"Slice: {self.current_coronal_slice_index[idx]}  -  Slice: {P_mm:.2f} mm")
            
    elif self.segSelectView.currentText() == "Sagittal":
        image_coord_vox[0] = int(image_coord_vox[0]/self.pixel_spac[idx,0])
        image_coord_vox[1] = int(image_coord_vox[1]/self.slice_thick[idx])
        if self.display_data_seg[idx].ndim==2:
            slice_data = self.display_data_seg[idx]
        else:
            slice_data = self.display_data_seg[idx][:, :, self.current_sagittal_slice_index[idx]]
        P_mm = self.current_sagittal_slice_index[idx] * self.pixel_spac[idx,1] + self.Im_Offset[idx,0]
        if (0 <= image_coord_vox[0] < slice_data.shape[1]
            and 0 <= image_coord_vox[1] < slice_data.shape[0]):
            pixel_value = slice_data[image_coord_vox[1],image_coord_vox[0]]
            self.textActorSagittal.SetInput (f"Slice: {P_mm:.1f} mm ({self.current_sagittal_slice_index[idx]}, {image_coord_vox[0]}, {image_coord_vox[1]}) {round(pixel_value,4):.4f}")
        else:
            self.textActorSagittal.SetInput(f"Slice: {self.current_sagittal_slice_index[idx]} - Slice: {P_mm:.2f} mm")

    # Render the updated data (to refresh the displayed text)
    self.vtkWidgetSeg.GetRenderWindow().Render()
    

def change_sliceSeg(self, delta):
    idx = self.layer_selection_box.currentIndex()
    # Modify the current slice index
    self.current_seg_slice_index[idx] += delta
    # Ensure slice index is within bounds
    if self.segSelectView.currentText() == "Axial":
        max_idx = self.display_data_seg[idx].shape[0]
    elif self.segSelectView.currentText() == "Coronal":
        max_idx = self.display_data_seg[idx].shape[1]
    elif self.segSelectView.currentText() == "Sagittal":
        max_idx = self.display_data_seg[idx].shape[2]
    if self.current_seg_slice_index[idx] < 0:
        self.current_seg_slice_index[idx] = 0
    elif self.current_seg_slice_index[idx] >= max_idx:
        self.current_seg_slice_index[idx] = max_idx - 1
    # Update the display
    displayseg(self)
    self.textActorSeg.SetInput(f"Slice: {self.current_seg_slice_index[idx]}")
    # Update the slider's value to match the current slice index
    self.segViewSlider.setValue(self.current_seg_slice_index[idx]) 
    
    
    
def displayseg(self, Im = None):
    idx = self.layer_selection_box.currentIndex()

    if self.segSelectView.currentText() == "Axial":
        for i in range(len(self.dataImporterSeg)):
            # if i == 3:
            #     disp_structure_overlay_seg(self)

            if self.slice_thick[i] ==0:
                continue
            
            Offset_vox = (self.Im_PatPosition[idx,2]-self.Im_PatPosition[i,2])/self.slice_thick[i]
            self.current_seg_slice_index[i] = int((self.current_seg_slice_index[idx]*(self.slice_thick[idx]/self.slice_thick[i]))+Offset_vox)
            #
            if 0 <=self.current_seg_slice_index[i] <self.display_data_seg[i].shape[0]:
                if self.display_data_seg[i].ndim==2:
                    slice_data = self.display_data_seg[i]
                elif Im is not None:
                    slice_data = Im
                else:       
                    slice_data = self.display_data_seg[i][self.current_seg_slice_index[i], :, :]
                data_string = slice_data.tobytes()
                extent = slice_data.shape
                self.dataImporterSeg[i].CopyImportVoidPointer(data_string, len(data_string))
                self.dataImporterSeg[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
                self.dataImporterSeg[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
                self.dataImporterSeg[i].SetDataSpacing(self.pixel_spac[i,1],self.pixel_spac[i,0],1)
                self.dataImporterSeg[i].Modified()  
                
                self.imageActorSeg[i].SetPosition(self.Im_Offset[i,0], self.Im_Offset[i,1] , 0)
                imageProperty = self.imageActorSeg[i].GetProperty()
                imageProperty.SetOpacity(self.LayerAlpha[i])  
  
            else:             
                imageProperty = self.imageActorSeg[i].GetProperty()
                imageProperty.SetOpacity(0)
                self.dataImporterSeg[i].Modified()

    elif self.segSelectView.currentText() == "Coronal":
        if self.display_data_seg[idx].ndim==2:
            return
        for i in range(len(self.dataImporterSeg)):
            # if i == 3:
            #     disp_structure_overlay_seg(self)

            if self.slice_thick[i] ==0:
                continue
            
            Offset = (self.display_data_seg[idx].shape[1]*self.pixel_spac[idx,0]-self.display_data_seg[i].shape[1]*self.pixel_spac[i,0]-(self.Im_PatPosition[i,1]-self.Im_PatPosition[idx,1]))/self.pixel_spac[i,0]
            self.current_seg_slice_index[i] = int((self.current_seg_slice_index[idx]*(self.pixel_spac[idx,0]/self.pixel_spac[i,0]))-Offset)
            
            if 0<= self.current_seg_slice_index[i] <self.display_data_seg[i].shape[1]:
                if Im is not None:
                    slice_data = Im
                else:
                    slice_data = self.display_data_seg[i][:, self.current_seg_slice_index[i], :]
                data_string = slice_data.tobytes()
                extent = slice_data.shape
                self.dataImporterSeg[i].CopyImportVoidPointer(data_string, len(data_string))
                self.dataImporterSeg[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
                self.dataImporterSeg[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
                self.dataImporterSeg[i].SetDataSpacing(self.pixel_spac[i,1],self.slice_thick[i],1)     
                self.dataImporterSeg[i].Modified() 
                
                imageProperty = self.imageActorSeg[i].GetProperty()
                imageProperty.SetOpacity(self.LayerAlpha[i])
                self.imageActorSeg[i].SetPosition(self.Im_Offset[i,0], self.Im_Offset[i,2] , 0)
            else:
                imageProperty = self.imageActorSeg[i].GetProperty()
                imageProperty.SetOpacity(0) 
                self.dataImporterSeg[i].Modified()  

    elif self.segSelectView.currentText() == "Sagittal":
        if self.display_data_seg[idx].ndim==2:
            return
        for i in range(len(self.dataImporterSeg)):
            # if i == 3:
            #     disp_structure_overlay_seg(self)

            if self.slice_thick[i] ==0:
                continue
            
            Offset_vox = (self.Im_PatPosition[idx,0]-self.Im_PatPosition[i,0])/self.pixel_spac[i,1]
            self.current_seg_slice_index[i] = int(self.current_seg_slice_index[idx]*(self.pixel_spac[idx,1]/self.pixel_spac[i,1]) + Offset_vox)
            
            if 0 <= self.current_seg_slice_index[i] < self.display_data_seg[i].shape[2]:
                if Im is not None:
                    slice_data = Im
                else:
                    slice_data = self.display_data_seg[i][:, :, self.current_seg_slice_index[i]]
                data_string = slice_data.tobytes()
                extent = slice_data.shape
                self.dataImporterSeg[i].CopyImportVoidPointer(data_string, len(data_string))
                self.dataImporterSeg[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
                self.dataImporterSeg[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
                self.dataImporterSeg[i].SetDataSpacing(self.pixel_spac[i,0],self.slice_thick[i],1) 
                self.dataImporterSeg[i].Modified()  
                
                self.imageActorSeg[i].SetPosition(self.Im_Offset[i,1], self.Im_Offset[i,2] , 0)
                imageProperty = self.imageActorSeg[i].GetProperty()
                imageProperty.SetOpacity(self.LayerAlpha[i])  
            else: 
                imageProperty = self.imageActorSeg[i].GetProperty()
                imageProperty.SetOpacity(0)  
                self.dataImporterSeg[i].Modified()
            #
    # Render the updated data
    self.vtkWidgetSeg.GetRenderWindow().Render()


def disp_structure_overlay_seg(self):
    renderer = self.vtkWidgetSeg.GetRenderWindow().GetRenderers().GetFirstRenderer()

    # Clear previous actors explicitly
    if hasattr(self, "structure_actors_seg"):
        for actor in self.structure_actors_seg:
            renderer.RemoveActor(actor)
    self.structure_actors_seg = []

    target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    if 'structures' not in target_series_dict or not target_series_dict['structures']:
        # print("No structures found.")
        return

    slice_index = self.current_seg_slice_index[0]  # Base reference slice
    # print(f"Displaying actors for axial slice: {slice_index}")

    structures_dict = target_series_dict['structures']

    for i in range(self.STRUCTlist.count()):
        widget = self.STRUCTlist.itemWidget(self.STRUCTlist.item(i))
        if widget.checkbox.isChecked():
            structure_key = getattr(widget, 'structure_key', None)
            if structure_key is None:
                continue

            structure_data = structures_dict.get(structure_key, {})
            actors_dict = structure_data.get('VTKActors2D', {}).get('seg', {})

            if slice_index not in actors_dict:
                # print(f"No actor stored for slice {slice_index} in structure {structure_key}. Available slices: {list(actors_dict.keys())}")
                continue
            
            actor = actors_dict.get(slice_index)

            actor_copy = vtk.vtkActor()
            actor_copy.ShallowCopy(actor)
            actor_copy.GetProperty().SetColor(widget.selectedColor.getRgbF()[:3] if widget.selectedColor else (1, 1, 1))
            actor_copy.GetProperty().SetOpacity(1 - widget.transparency_spinbox.value())
            actor_copy.GetProperty().SetLineWidth(widget.line_width_spinbox.value())

            actor_copy.GetProperty().SetRepresentationToSurface()  # Solid Fill

            actor_copy.SetPosition(self.Im_Offset[0, 0], 
                                   self.Im_Offset[0, 1], 
                                   2000)  # Move contour on top layer

            renderer.AddActor(actor_copy)
            self.structure_actors_ax.append(actor_copy)

    self.vtkWidgetAxial.GetRenderWindow().Render()
    

def update_seg_image(self, Im = None):
    idx = self.layer_selection_box.currentIndex()
    #
    if self.segSelectView.currentText() == "Axial":
        for i in range(len(self.dataImporterSeg)):
            if self.slice_thick[i] ==0:
                continue
    
            Offset_vox = (self.Im_PatPosition[idx,2]-self.Im_PatPosition[i,2])/self.slice_thick[i]
            self.current_seg_slice_index[i] = int((self.current_seg_slice_index[idx]*(self.slice_thick[idx]/self.slice_thick[i]))+Offset_vox)
            #
            if 0 <=self.current_seg_slice_index[i] <self.display_data_seg[i].shape[0]:
                if self.display_data_seg[i].ndim==2:
                    slice_data = self.display_data_seg[i]
                elif Im is not None:
                    slice_data = Im
                else:       
                    slice_data = self.display_data_seg[i][self.current_seg_slice_index[i], :, :]
                data_string = slice_data.tobytes()
                #
                self.dataImporterSeg[i].SetDataSpacing(self.pixel_spac[i,1],self.pixel_spac[i,0],1)
                #
                extent = slice_data.shape
                self.dataImporterSeg[i].CopyImportVoidPointer(data_string, len(data_string))
                self.dataImporterSeg[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
                self.dataImporterSeg[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
                #
                self.imageActorSeg[i].SetPosition(self.Im_Offset[i,0], self.Im_Offset[i,1] , 0)
                #
                #
                imageProperty = self.imageActorSeg[i].GetProperty()
                imageProperty.SetOpacity(self.LayerAlpha[i])  
                self.dataImporterSeg[i].Modified()   
                          
            else:             
                imageProperty = self.imageActorSeg[i].GetProperty()
                imageProperty.SetOpacity(0)
                self.dataImporterSeg[i].Modified()
                
    if self.segSelectView.currentText() == "Coronal":
        if self.display_data_seg[idx].ndim==2:
            return
        for i in range(len(self.dataImporterSeg)):
            if self.slice_thick[i] ==0:
                continue   

            Offset = (self.display_data_seg[idx].shape[1]*self.pixel_spac[idx,0]-self.display_data_seg[i].shape[1]*self.pixel_spac[i,0]-(self.Im_PatPosition[i,1]-self.Im_PatPosition[idx,1]))/self.pixel_spac[i,0]
            self.current_seg_slice_index[i] = int((self.current_seg_slice_index[idx]*(self.pixel_spac[idx,0]/self.pixel_spac[i,0]))-Offset)
            #
            if 0<= self.current_seg_slice_index[i] <self.display_data_seg[i].shape[1]:
                # Just update the slice data for the existing pipeline
                if Im is not None:
                    slice_data = Im
                else:
                    slice_data = self.display_data_seg[i][:, self.current_seg_slice_index[i], :]
                data_string = slice_data.tobytes()
                extent = slice_data.shape
                self.dataImporterSeg[i].CopyImportVoidPointer(data_string, len(data_string))
                self.dataImporterSeg[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
                self.dataImporterSeg[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
                self.dataImporterSeg[i].SetDataSpacing(self.pixel_spac[i,1],self.slice_thick[i],1)    
                self.dataImporterSeg[i].Modified() 

                imageProperty = self.imageActorSeg[i].GetProperty()
                imageProperty.SetOpacity(self.LayerAlpha[i])  
                self.imageActorSeg[i].SetPosition(self.Im_Offset[i,0], self.Im_Offset[i,2] , 0)
                # if self.modality == 'RTDOSE':   
                #     # Just update the slice data for the existing pipeline
                #     slice_dose = self.current_slice_index[1]-int(self.Dose_Im_offset[1])
            else:
                imageProperty = self.imageActorSeg[i].GetProperty()
                imageProperty.SetOpacity(0) 
                self.dataImporterSeg[i].Modified() 
                
    if self.segSelectView.currentText() == "Sagittal":
        if self.display_data_seg[idx].ndim==2:
            return
        for i in range(len(self.dataImporterSeg)):
            if self.slice_thick[i] ==0:
                continue
            
            Offset_vox = (self.Im_PatPosition[idx,0]-self.Im_PatPosition[i,0])/self.pixel_spac[i,1]
            self.current_seg_slice_index[i] = int(self.current_seg_slice_index[idx]*(self.pixel_spac[idx,1]/self.pixel_spac[i,1]) + Offset_vox)
            
            if 0 <= self.current_seg_slice_index[i] < self.display_data_seg[i].shape[2]:
                if Im is not None:
                    slice_data = Im
                else:
                    slice_data = self.display_data_seg[i][:, :, self.current_seg_slice_index[i]]
                data_string = slice_data.tobytes()
              
                extent = slice_data.shape
                self.dataImporterSeg[i].CopyImportVoidPointer(data_string, len(data_string))
                self.dataImporterSeg[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
                self.dataImporterSeg[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
                self.dataImporterSeg[i].SetDataSpacing(self.pixel_spac[i,0],self.slice_thick[i],1) 
                self.dataImporterSeg[i].Modified()  
                
                self.imageActorSeg[i].SetPosition(self.Im_Offset[i,1], self.Im_Offset[i,2] , 0)
                imageProperty = self.imageActorSeg[i].GetProperty()
                imageProperty.SetOpacity(self.LayerAlpha[i])  

            else: 
                imageProperty = self.imageActorSeg[i].GetProperty()
                imageProperty.SetOpacity(0)
                self.dataImporterSeg[i].Modified() 


    
def Data_tree_general(self):
            if currentTabText == "Segmentation":
                if len(hierarchy) >= 6 and hierarchy[5] == "Structures": 
                    # structures withing a SERIES
                    update_structure_list_widget(self,
                                self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures_names'],
                                self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures_keys']
                            )

                # list series from the same acquisition and populate a table so the user can pick what to display
                #
                if len(hierarchy) == 5: # Series
                    self.display_data_seg[idx] = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix']
                if len(hierarchy) == 7: # binary mask contour
                    s_key = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures_keys'][hierarchy_indices[6].row()]
                    self.display_data_seg[idx] = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures'][s_key]['Mask3D']

                adjust_data_type_input(self,idx)
                #
                if self.segSelectView.currentText() == "Axial":
                    self.current_seg_slice_index[idx]    = round(self.display_data_seg[idx].shape[0]/2)
                elif self.segSelectView.currentText() == "Coronal":
                    self.current_seg_slice_index[idx]    = round(self.display_data_seg[idx].shape[1]/2)
                elif self.segSelectView.currentText() == "Sagittal":
                    self.current_seg_slice_index[idx]    = round(self.display_data_seg[idx].shape[2]/2)
                #
                # Update the slider's value to match the current slice index
                # Setting the maximum will call slider change function chaging the current slice...
                # workaround is to keep the value and update laeter
                Ax_s = self.current_seg_slice_index[idx]
                #
                # This is a workaround to avoid issues when changing the data type ... It basically plots the image on the 3 axis to ensure that when the display function
                # is called all axes have the same type of data (e.g. float) ... Using display without update the images cause issues. E.g. display axial will update some 
                # elements on the cornoal axis and the software will crash if axial and coronal images have different types (because one axes update the data type before the other)
                update_seg_image(self)
                self.vtkWidgetSeg.GetRenderWindow().Render()
                #
                #
                displayseg(self)
                #
                if self.segSelectView.currentText() == "Axial":
                    self.segViewSlider.setMaximum(self.display_data_seg[idx].shape[0] - 1)
                elif self.segSelectView.currentText() == "Coronal":
                    self.segViewSlider.setMaximum(self.display_data_seg[idx].shape[1] - 1)
                elif self.segSelectView.currentText() == "Sagittal":
                    self.segViewSlider.setMaximum(self.display_data_seg[idx].shape[2] - 1)
                self.segViewSlider.setValue(Ax_s)
                #
                self.windowLevelSeg[idx].SetWindow(Window)
                self.windowLevelSeg[idx].SetLevel(Level)
                #   
                self.textActorSegWL.SetInput(f"L: {round(Level,2)}  W: {round(Window,2)}")
                #
                self.renSeg.ResetCamera() 
                #
                #
                displayseg(self)