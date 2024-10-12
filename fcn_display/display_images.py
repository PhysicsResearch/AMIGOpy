import vtk
import math

def displayaxial(self, Im = None):
    idx = self.layer_selection_box.currentIndex()
    #
    for i in range(len(self.dataImporterAxial)):
        # Add or update circular ROIs in the 4th layer
        if i == 3 and self.checkBox_circ_roi_data_2.isChecked():
            renderer = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()
            for actor in self.circle_actors_ax:
                renderer.RemoveActor(actor)
            self.circle_actors_ax.clear()
            # self.vtkWidgetAxial.GetRenderWindow().Render() 
            disp_roi_axial(self)

  
        if self.slice_thick[i] ==0:
            continue
        
        
        Offset_vox = (self.Im_PatPosition[idx,2]-self.Im_PatPosition[i,2])/self.slice_thick[i]
        self.current_axial_slice_index[i] = int((self.current_axial_slice_index[idx]*(self.slice_thick[idx]/self.slice_thick[i]))+Offset_vox)
        #
        if 0 <=self.current_axial_slice_index[i] <self.display_data[i].shape[0]:
            if self.display_data[i].ndim==2:
                slice_data = self.display_data[i]
            elif Im is not None:
                slice_data = Im
            else:       
                slice_data = self.display_data[i][self.current_axial_slice_index[i], :, :]
            data_string = slice_data.tobytes()
            #
            self.dataImporterAxial[i].SetDataSpacing(self.pixel_spac[i,1],self.pixel_spac[i,0],1)
            #
            extent = slice_data.shape
            self.dataImporterAxial[i].CopyImportVoidPointer(data_string, len(data_string))
            self.dataImporterAxial[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            self.dataImporterAxial[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            #
            self.imageActorAxial[i].SetPosition(self.Im_Offset[i,0], self.Im_Offset[i,1] , 0)
            #
            #
            imageProperty = self.imageActorAxial[i].GetProperty()
            imageProperty.SetOpacity(self.LayerAlpha[i])  
            self.dataImporterAxial[i].Modified()  
            if i == idx:
                # Update the position and lateral extension of the axial line to cross the entire image
                self.sagittalLine2Source.SetPoint1(self.Im_Offset[i,1],self.Im_Offset[i,2]+self.current_axial_slice_index[i]*self.slice_thick[i], 0.1)
                self.sagittalLine2Source.SetPoint2(self.Im_Offset[i,1]+extent[0]*self.pixel_spac[i,0]-self.pixel_spac[i,0],self.Im_Offset[i,2]+self.current_axial_slice_index[i]*self.slice_thick[i], 0.1)
                self.sagittalLine2Source.Modified()  # Notify VTK of the changes
                #
                # Update the position and lateral extension of the axial line to cross the entire image
                self.coronalLine2Source.SetPoint1(self.Im_Offset[i,0],self.Im_Offset[i,2]+self.current_axial_slice_index[i]*self.slice_thick[i], 1)
                self.coronalLine2Source.SetPoint2(self.Im_Offset[i,0]+extent[1]*self.pixel_spac[i,1]-self.pixel_spac[i,1],self.Im_Offset[i,2]+self.current_axial_slice_index[i]*self.slice_thick[i], 0.11)
                self.coronalLine2Source.Modified()  # Notify VTK of the changes
                self.current_axial_slice_index[i]  
                      
        else:             
            imageProperty = self.imageActorAxial[i].GetProperty()
            imageProperty.SetOpacity(0)
            self.dataImporterAxial[i].Modified()
        #     
        #  Render to update
        self.vtkWidgetAxial.GetRenderWindow().Render()
        self.vtkWidgetSagittal.GetRenderWindow().Render()
        self.vtkWidgetCoronal.GetRenderWindow().Render()

def disp_roi_axial(self):
    for row in range(self.table_circ_roi.rowCount()):
        try:
            item_x       = self.table_circ_roi.item(row, 0)
            item_y       = self.table_circ_roi.item(row, 1)
            item_radius  = self.table_circ_roi.item(row, 2)
            sli_ini      = self.table_circ_roi.item(row, 3)
            sli_fin      = self.table_circ_roi.item(row, 4)
            transparency = self.table_circ_roi.item(row, 5)
            R            = self.table_circ_roi.item(row, 6)
            G            = self.table_circ_roi.item(row, 7)
            B            = self.table_circ_roi.item(row, 8)
            
            if (item_x is None or item_y is None or item_radius is None or sli_ini is None or sli_fin is None
                or transparency is None or R is None or G is None or B is None):
                print(f'Skipping row {row} due to missing data')
                continue

            sli_ini        = float(sli_ini.text())
            sli_fin        = float(sli_fin.text())
            
          
            if self.current_axial_slice_index[0] < sli_ini or self.current_axial_slice_index[0] > sli_fin:
                continue

            center_x_pixel = float(item_x.text())
            center_y_pixel = float(item_y.text())
            radius         = float(item_radius.text())
            transparency   = float(transparency.text())
            R              = float(R.text())
            G              = float(G.text())
            B              = float(B.text())
            # Convert pixel coordinates to physical coordinates
            center_x = center_x_pixel * self.pixel_spac[0, 0]  #+ self.Im_Offset[i, 0]
            center_y = center_y_pixel * self.pixel_spac[0, 1]  #+ self.Im_Offset[i, 1]
            radius   = radius * self.pixel_spac[0, 0]
         
            if row < len(self.circle_actors_ax):
                # Update existing circle actor
                circle_actor = self.circle_actors_ax[row]
                circle_source = vtk.vtkRegularPolygonSource()
                circle_source.SetNumberOfSides(50)
                circle_source.SetRadius(radius)
                circle_source.SetCenter(center_x, center_y, 0)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(circle_source.GetOutputPort())
                circle_actor.SetMapper(mapper)
                circle_actor.GetProperty().SetOpacity(1 - transparency)
            else:
                # Create new circle actor
                circle_source = vtk.vtkRegularPolygonSource()
                circle_source.SetNumberOfSides(50)  # More sides for a smoother circle
                circle_source.SetRadius(radius)
                circle_source.SetCenter(center_x, center_y, 0)  # Assuming 2D, set z to 0

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(circle_source.GetOutputPort())

                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(R, G, B)  # Set color to red
                actor.GetProperty().SetLineWidth(2)  # Set line width
                actor.GetProperty().SetOpacity(transparency)  # Set transparency
                # Set Z position slightly above the image layer
                actor.SetPosition(0, 0, 1)
                self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(actor)
                self.circle_actors_ax.append(actor)
        except ValueError:
            print(f'Skipping row {row} due to invalid data')
            continue  


def displaycoronal(self, Im = None):
    idx = self.layer_selection_box.currentIndex()
    if self.display_data[idx].ndim==2:
        return
    for i in range(len(self.dataImporterCoronal)):
        # Add or update circular ROIs in the 4th layer
        if i == 3 and self.checkBox_circ_roi_data_2.isChecked():
            renderer = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()
            for actor in self.circle_actors_co:
                renderer.RemoveActor(actor)
            self.circle_actors_co.clear()
            # self.vtkWidgetAxial.GetRenderWindow().Render() 
            disp_roi_coronal(self)


        if self.slice_thick[i] ==0:
            continue   
        
        
        
        Offset = (self.display_data[idx].shape[1]*self.pixel_spac[idx,0]-self.display_data[i].shape[1]*self.pixel_spac[i,0]-(self.Im_PatPosition[i,1]-self.Im_PatPosition[idx,1]))/self.pixel_spac[i,0]
        self.current_coronal_slice_index[i] = int((self.current_coronal_slice_index[idx]*(self.pixel_spac[idx,0]/self.pixel_spac[i,0]))-Offset)
        #
        if 0<= self.current_coronal_slice_index[i] <self.display_data[i].shape[1]:
            # Just update the slice data for the existing pipeline
            if Im is not None:
                slice_data = Im
            else:
                slice_data = self.display_data[i][:, self.current_coronal_slice_index[i], :]
            data_string = slice_data.tobytes()
            extent = slice_data.shape
            self.dataImporterCoronal[i].CopyImportVoidPointer(data_string, len(data_string))
            self.dataImporterCoronal[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            self.dataImporterCoronal[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            #
            # 
            self.dataImporterCoronal[i].SetDataSpacing(self.pixel_spac[i,1],self.slice_thick[i],1)     
            # Inform the pipeline that data has changed.
            imageProperty = self.imageActorCoronal[i].GetProperty()
            imageProperty.SetOpacity(self.LayerAlpha[i])  
            self.dataImporterCoronal[i].Modified()  
            if i == idx:
                # Update the position and lateral extension of the axial line to cross the entire image
                self.axialLineSource.SetPoint1(self.Im_Offset[i,0],self.Im_Offset[i,1]+ self.current_coronal_slice_index[i]*self.pixel_spac[i,0], 1)
                self.axialLineSource.SetPoint2(self.Im_Offset[i,0]+extent[1]*self.pixel_spac[i,1]-self.pixel_spac[i,1],self.Im_Offset[i,1]+ self.current_coronal_slice_index[i]*self.pixel_spac[i,0], 0.1)
                self.axialLineSource.Modified()  # Notify VTK of the changes
                
                # Update the position and lateral extension of the axial line to cross the entire image
                self.sagittalLineSource.SetPoint1(self.Im_Offset[i,1]+self.current_coronal_slice_index[i]*self.pixel_spac[i,0],self.Im_Offset[i,2], 1)
                self.sagittalLineSource.SetPoint2(self.Im_Offset[i,1]+self.current_coronal_slice_index[i]*self.pixel_spac[i,0],self.Im_Offset[i,2]+extent[0]*self.slice_thick[i]-self.slice_thick[i], 0.1)
                self.sagittalLineSource.Modified()  # Notify VTK of the changes
            #
            self.imageActorCoronal[i].SetPosition(self.Im_Offset[i,0], self.Im_Offset[i,2] , 0)
            # if self.modality == 'RTDOSE':   
            #     # Just update the slice data for the existing pipeline
            #     slice_dose = self.current_slice_index[1]-int(self.Dose_Im_offset[1])
        else:
            imageProperty = self.imageActorCoronal[i].GetProperty()
            imageProperty.SetOpacity(0) 
            self.dataImporterCoronal[i].Modified()  
    #

    # Render the updated data
    self.vtkWidgetCoronal.GetRenderWindow().Render()
    self.vtkWidgetAxial.GetRenderWindow().Render()
    self.vtkWidgetSagittal.GetRenderWindow().Render()
        
def disp_roi_coronal(self):
    for row in range(self.table_circ_roi.rowCount()):
        try:
            item_x = self.table_circ_roi.item(row, 0)
            item_y = self.table_circ_roi.item(row, 1)
            item_radius = self.table_circ_roi.item(row, 2)
            sli_ini = self.table_circ_roi.item(row, 3)
            sli_fin = self.table_circ_roi.item(row, 4)
            transparency = self.table_circ_roi.item(row, 5)
            R = self.table_circ_roi.item(row, 6)
            G = self.table_circ_roi.item(row, 7)
            B = self.table_circ_roi.item(row, 8)

            if (item_x is None or item_y is None or item_radius is None or sli_ini is None or sli_fin is None
                    or transparency is None or R is None or G is None or B is None):
                print(f'Skipping row {row} due to missing data')
                continue

            sli_ini = float(sli_ini.text())
            sli_fin = float(sli_fin.text())
            center_x_pixel = float(item_x.text())
            center_y_pixel = float(item_y.text())
            radius = float(item_radius.text())
            transparency = float(transparency.text())
            R = float(R.text())
            G = float(G.text())
            B = float(B.text())
            
            
            if self.current_coronal_slice_index[0] < (center_y_pixel-radius) or self.current_coronal_slice_index[0] > (center_y_pixel+radius):
                # Remove the specific actor corresponding to this row
                if row < len(self.circle_actors_co):
                    renderer = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()
                    actor_to_remove = self.circle_actors_co.pop(row)
                    renderer.RemoveActor(actor_to_remove)
                    self.vtkWidgetCoronal.GetRenderWindow().Render()
                continue
           


            # Convert pixel coordinates to physical coordinates
            center_z = center_x_pixel    * self.pixel_spac[0, 0]
            height = (sli_fin - sli_ini) * self.slice_thick[0]
            
            # Calculate the distance from the center of the cylinder to the current slice
            current_slice_position = self.current_coronal_slice_index[0]
            center_slice_position  = (sli_ini + sli_fin) / 2 

            distance_from_center   = abs(self.current_coronal_slice_index[0] - center_y_pixel)
            # Calculate the width of the rectangle based on the distance from the center of the cylinder
            if distance_from_center > radius+1:
                width = 0
                
            else:
                width = 2 * math.sqrt(radius**2 - distance_from_center**2) * self.pixel_spac[0, 0]  

            if row < len(self.circle_actors_co):
                # Update existing rectangle actor
                rect_actor = self.circle_actors_co[row]
                cube_source = vtk.vtkCubeSource()
                cube_source.SetXLength(width)
                cube_source.SetYLength(height)
                cube_source.SetZLength(1)  # Assuming the thickness of 1 voxel

                center_y = (sli_ini + sli_fin) / 2 * self.slice_thick[0]

                cube_source.SetCenter(center_z, center_y, 0)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(cube_source.GetOutputPort())
                rect_actor.SetMapper(mapper)
                rect_actor.GetProperty().SetOpacity(transparency)
            else:
                # Create new rectangle actor
                cube_source = vtk.vtkCubeSource()
                cube_source.SetXLength(width)
                cube_source.SetYLength(height)
                cube_source.SetZLength(1)  # Assuming the thickness of 1 voxel

                center_y = (sli_ini + sli_fin) / 2 * self.slice_thick[0]

                cube_source.SetCenter(center_z, center_y, 0)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(cube_source.GetOutputPort())

                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(R, G, B)
                actor.GetProperty().SetOpacity(transparency)

                self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(actor)
                self.circle_actors_co.append(actor)

        except ValueError:
            print(f'Skipping row {row} due to invalid data')
            continue  
    
def displaysagittal(self,Im = None):
    idx = self.layer_selection_box.currentIndex()
    if self.display_data[idx].ndim==2:
        return
    for i in range(len(self.dataImporterSagittal)):
        
        # Add or update circular ROIs in the 4th layer
        if i == 3 and self.checkBox_circ_roi_data_2.isChecked():
            renderer = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()
            for actor in self.circle_actors_sa:
                renderer.RemoveActor(actor)
            self.circle_actors_sa.clear()
            # self.vtkWidgetAxial.GetRenderWindow().Render() 
            disp_roi_sagittal(self)
            
        
        if self.slice_thick[i] ==0:
            continue
        
        
        
        Offset_vox = (self.Im_PatPosition[idx,0]-self.Im_PatPosition[i,0])/self.pixel_spac[i,1]
        self.current_sagittal_slice_index[i] = int(self.current_sagittal_slice_index[idx]*(self.pixel_spac[idx,1]/self.pixel_spac[i,1]) + Offset_vox)
        #
        if 0 <= self.current_sagittal_slice_index[i] < self.display_data[i].shape[2]:
            # Just update the slice data for the existing pipeline
            if Im is not None:
                slice_data = Im
            else:
                slice_data = self.display_data[i][:, :, self.current_sagittal_slice_index[i]]
            data_string = slice_data.tobytes()
          
            extent = slice_data.shape
            self.dataImporterSagittal[i].CopyImportVoidPointer(data_string, len(data_string))
            self.dataImporterSagittal[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            self.dataImporterSagittal[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
            
            self.dataImporterSagittal[i].SetDataSpacing(self.pixel_spac[i,0],self.slice_thick[i],1) 
            self.imageActorSagittal[i].SetPosition(self.Im_Offset[i,1], self.Im_Offset[i,2] , 0)
            imageProperty = self.imageActorSagittal[i].GetProperty()
            imageProperty.SetOpacity(self.LayerAlpha[i])  
            # Inform the pipeline that data has changed.
            self.dataImporterSagittal[i].Modified()  
            if i==idx:
                # Update the position and lateral extension of the axial line to cross the entire image
                self.axialLine2Source.SetPoint1(self.Im_Offset[i,0]+self.current_sagittal_slice_index[i]*self.pixel_spac[i,1],self.Im_Offset[i,1], 1)
                self.axialLine2Source.SetPoint2(self.Im_Offset[i,0]+self.current_sagittal_slice_index[i]*self.pixel_spac[i,1],self.Im_Offset[i,1]+extent[1]*self.pixel_spac[i,0]-self.pixel_spac[i,0],  1)
                self.axialLine2Source.Modified()  # Notify VTK of the changes
            
                # # Update the position and lateral extension of the coronal line to cross the entire image
                self.coronalLineSource.SetPoint1(self.Im_Offset[i,0]+self.current_sagittal_slice_index[i]*self.pixel_spac[i,1], self.Im_Offset[i,2], 1)
                self.coronalLineSource.SetPoint2(self.Im_Offset[i,0]+self.current_sagittal_slice_index[i]*self.pixel_spac[i,1],self.Im_Offset[i,2]+extent[0]*self.slice_thick[i]-self.slice_thick[i],  1)
                self.coronalLineSource.Modified()  # Notify VTK of the changes     
        else: 
            imageProperty = self.imageActorSagittal[i].GetProperty()
            imageProperty.SetOpacity(0)  
        #
    # Render the updated data
    self.vtkWidgetAxial.GetRenderWindow().Render()
    self.vtkWidgetSagittal.GetRenderWindow().Render()
    self.vtkWidgetCoronal.GetRenderWindow().Render()
    

def disp_roi_sagittal(self):
    for row in range(self.table_circ_roi.rowCount()):
        try:
            item_x = self.table_circ_roi.item(row, 0)
            item_y = self.table_circ_roi.item(row, 1)
            item_radius = self.table_circ_roi.item(row, 2)
            sli_ini = self.table_circ_roi.item(row, 3)
            sli_fin = self.table_circ_roi.item(row, 4)
            transparency = self.table_circ_roi.item(row, 5)
            R = self.table_circ_roi.item(row, 6)
            G = self.table_circ_roi.item(row, 7)
            B = self.table_circ_roi.item(row, 8)

            if (item_x is None or item_y is None or item_radius is None or sli_ini is None or sli_fin is None
                    or transparency is None or R is None or G is None or B is None):
                print(f'Skipping row {row} due to missing data')
                continue

            sli_ini = float(sli_ini.text())
            sli_fin = float(sli_fin.text())
            center_x_pixel = float(item_x.text())
            center_y_pixel = float(item_y.text())
            radius = float(item_radius.text())
            transparency = float(transparency.text())
            R = float(R.text())
            G = float(G.text())
            B = float(B.text())
            
            
            if self.current_sagittal_slice_index[0] < (center_x_pixel-radius) or self.current_sagittal_slice_index[0] > (center_x_pixel+radius):
                # Remove the specific actor corresponding to this row
                if row < len(self.circle_actors_sa):
                    renderer = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()
                    actor_to_remove = self.circle_actors_sa.pop(row)
                    renderer.RemoveActor(actor_to_remove)
                    self.vtkWidgetSagittal.GetRenderWindow().Render()
                continue
           


            # Convert pixel coordinates to physical coordinates
            center_z = center_y_pixel    * self.pixel_spac[0, 0]
            height = (sli_fin - sli_ini) * self.slice_thick[0]
            
            # Calculate the distance from the center of the cylinder to the current slice
            current_slice_position = self.current_sagittal_slice_index[0]
            center_slice_position  = (sli_ini + sli_fin) / 2 

            distance_from_center   = abs(self.current_sagittal_slice_index[0] - center_x_pixel)
            # Calculate the width of the rectangle based on the distance from the center of the cylinder
            if distance_from_center > radius+1:
                width = 0
                
            else:
                width = 2 * math.sqrt(radius**2 - distance_from_center**2) * self.pixel_spac[0, 0]  

            if row < len(self.circle_actors_sa):
                # Update existing rectangle actor
                rect_actor = self.circle_actors_sa[row]
                cube_source = vtk.vtkCubeSource()
                cube_source.SetXLength(width)
                cube_source.SetYLength(height)
                cube_source.SetZLength(1)  # Assuming the thickness of 1 voxel

                center_y = (sli_ini + sli_fin) / 2 * self.slice_thick[0]

                cube_source.SetCenter(center_z, center_y, 0)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(cube_source.GetOutputPort())
                rect_actor.SetMapper(mapper)
                rect_actor.GetProperty().SetOpacity(transparency)
            else:
                # Create new rectangle actor
                cube_source = vtk.vtkCubeSource()
                cube_source.SetXLength(width)
                cube_source.SetYLength(height)
                cube_source.SetZLength(1)  # Assuming the thickness of 1 voxel

                center_y = (sli_ini + sli_fin) / 2 * self.slice_thick[0]

                cube_source.SetCenter(center_z, center_y, 0)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(cube_source.GetOutputPort())

                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(R, G, B)
                actor.GetProperty().SetOpacity(transparency)

                self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(actor)
                self.circle_actors_sa.append(actor)

        except ValueError:
            print(f'Skipping row {row} due to invalid data')
            continue





def update_layer_view(self):
    idx = self.layer_selection_box.currentIndex()
    tabName = self.tabModules.tabText(self.tabModules.currentIndex())
    self.layerTab[tabName] = idx
    if self.slice_thick[idx] !=0:
        # Update the slider's value to match the current slice index
        #
        Ax_s = self.current_axial_slice_index[idx]
        Sa_s = self.current_sagittal_slice_index[idx]
        Co_s = self.current_coronal_slice_index[idx]
        # check if the current slice is in the range of the layer
        if Ax_s<0:
            Ax_s = 0
        elif Ax_s > self.display_data[idx].shape[0]-1:
            Ax_s = self.display_data[idx].shape[0] - 1
        #
        if    Sa_s < 0:
            Sa_s = 0
        elif Sa_s > self.display_data[idx].shape[2]-1:
            Sa_s = self.display_data[idx].shape[2]-1
        #
        if Co_s<0:
            Co_s =0
        elif Co_s > self.display_data[idx].shape[1] - 1:
            Co_s = self.display_data[idx].shape[1] - 1
        #
        # Update the slider that will update the view    
        #
        self.AxialSlider.setMaximum(self.display_data[idx].shape[0] - 1)
        self.SagittalSlider.setMaximum(self.display_data[idx].shape[2] - 1)
        self.CoronalSlider.setMaximum(self.display_data[idx].shape[1] - 1)
        #
        self.AxialSlider.setValue(Ax_s)
        self.SagittalSlider.setValue(Sa_s)
        self.CoronalSlider.setValue(Co_s)
        #