from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt
import vtk
import numpy as np
import math
from fcn_RTFiles.process_contours import build_contours_for_structure, actors_from_contours


def displayaxial(self, Im = None):
    # ------------------------------------------------------------------
    if (not hasattr(self, "display_data") or
        self.display_data is None or
        len(self.display_data) == 0):
        return   
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
        if i == 3 and  self.display_dw_overlay.isChecked():
            # Check if the required fields exist in dicom_data
                display_dwell_positions_ax(self)
        if i == 3 and  self.display_brachy_channel_overlay.isChecked():
            # Check if the required fields exist in dicom_data
                display_brachy_channel_overlay_ax(self)
        if i == 3:
            # Check if the required fields exist in dicom_data
                # First, clear previous overlays explicitly
                disp_structure_overlay_axial(self)

  
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
        self.sliceChanged.emit("axial", self.current_axial_slice_index)

def disp_structure_overlay_axial(self):
    """
    Show checked structures on the axial renderer.

    • If VTK actors are already cached under
      structure_data['VTKActors2D']['axial'], reuse them.

    • If *only* Contours2D are present (freshly loaded bundle),
      lazily convert those contours → vtkActors and cache them,
      so next call is instant.

    The bundle itself stays pickle-safe because actors are never stored
    back to disk.
    """
    renderer = (
        self.vtkWidgetAxial.GetRenderWindow()
        .GetRenderers()
        .GetFirstRenderer()
    )

    # ─── clear any actors from the previous draw ──────────────────────
    for actor in getattr(self, "structure_actors_ax", []):
        renderer.RemoveActor(actor)
    self.structure_actors_ax = []

    # ─── grab data for the currently displayed image series ───────────
    series_dict = (
        self.dicom_data[self.patientID][self.studyID]
                       [self.modality][self.series_index]
    )
    if not series_dict.get("structures"):
        return                              # nothing to draw yet

    slice_idx = self.current_axial_slice_index[0]     # current Z

    # pixel spacing (row, col)  →  (y, x) in mm
    px_spacing = (self.pixel_spac[0, 1], self.pixel_spac[0, 0])

    # ─── WARNDLG SETUP ──────────────────────────────────────────────
    warn_dlg = None
    for i in range(self.STRUCTlist.count()):
        item_widget = self.STRUCTlist.itemWidget(self.STRUCTlist.item(i))
        if not item_widget.checkbox.isChecked():
            continue                      # structure not selected

        s_key = getattr(item_widget, "structure_key", None)
        if s_key is None:
            continue

        s_data = series_dict["structures"].get(s_key, {})
        if not s_data:
            return
        # ── 1) make sure axial actors exist  if not create all ──────────────────────────
        if 'Contours2D' not in s_data:
            s_data['Contours2D'] = {'axial':{}, 'sagittal':{}, 'coronal':{}},
        if not s_data['Contours2D']:
            return
        
        if "VTKActors2D" not in s_data:
            # show the warn dialog once
            if warn_dlg is None:
                warn_dlg = QProgressDialog(
                    "Pre-loading contours… it may take a few seconds",
                    None, 0, 0, self
                )
                warn_dlg.setWindowTitle("Please wait")
                warn_dlg.setWindowModality(Qt.WindowModal)
                warn_dlg.setAutoClose(False)
                warn_dlg.setMinimumDuration(0)
                warn_dlg.show()
            s_data["VTKActors2D"] = {}

        if not s_data['Contours2D']['axial'] or s_data['Modified'] == 1:          # still empty?
            s_data['Contours2D'] = build_contours_for_structure(s_data['Mask3D'])

        if "axial" not in s_data["VTKActors2D"] or s_data['Modified'] == 1:
            # build once, cache forever (in RAM only)
            contours_axial = s_data.get("Contours2D", {}).get("axial", {})
            s_data["VTKActors2D"]["axial"] = actors_from_contours(
                contours_axial, px_spacing,
                line_width=item_widget.line_width_spinbox.value(),
                color=item_widget.selectedColor.getRgbF()[:3]
                      if item_widget.selectedColor else (1, 0, 0),
            )

        actors_dict = s_data["VTKActors2D"]["axial"]

        if s_data['Modified'] == 1:
            s_data['Modified'] = 0          # reset modified flag

        if slice_idx not in actors_dict:
            continue                          # no contour on this slice

        src_actor = actors_dict[slice_idx]

        # ── 2) customise appearance per-widget (colour, opacity …) ───
        actor = vtk.vtkActor()
        actor.ShallowCopy(src_actor)
        actor.GetProperty().SetColor(
            item_widget.selectedColor.getRgbF()[:3]
            if item_widget.selectedColor else (1, 1, 1)
        )
        actor.GetProperty().SetOpacity(1 - item_widget.transparency_spinbox.value())
        actor.GetProperty().SetLineWidth(item_widget.line_width_spinbox.value())
        actor.GetProperty().SetRepresentationToWireframe()

        # move a little above the image plane so contours are visible
        actor.SetPosition(self.Im_Offset[0, 0],
                          self.Im_Offset[0, 1],
                          2000)

        renderer.AddActor(actor)
        self.structure_actors_ax.append(actor)
    # ─── CLOSE THE WARNDLG ──────────────────────────────────────────
    if warn_dlg is not None and warn_dlg.isVisible():
        warn_dlg.close()
    self.vtkWidgetAxial.GetRenderWindow().Render()


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

def display_dwell_positions_ax(self):
    """
    Display the dwell positions on top of the DICOM images using VTK.
    - If self.overlay_all_channels is selected, show all dwell positions from all channels.
    - Otherwise, show dwell positions for the channel selected by self.brachy_spinBox_01.
    - Uses the same point size as defined by self.dw_ch_point_size.
    - Dwell positions with dwell_time == 0 are shown in red.
    - Dwell positions with dwell_time > 0 are shown in dark green.
    - Dwell positions within Ref_Z ± slice_thickness/2 are shown in light green.
    """

    renderer = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()

    # Remove any previous dwell actors
    for actor in self.dwell_actors_ax:
        renderer.RemoveActor(actor)
    self.dwell_actors_ax.clear()

    try:
        meta = (self.dicom_data[self.patientID][self.studyID]          # may raise KeyError
                                [self.modality][self.series_index]
                                ['metadata'])
        channels = meta.get('Plan_Brachy_Channels')
    except KeyError:
        # Data tree incomplete (no metadata at all) ─ silently abort
        return
    
    if not channels:                     # None or empty list
        return                           # nothing to draw
    
    # Determine whether to show all channels or only the one selected by the spinbox
    if self.overlay_all_channels.isChecked():
        channels_to_display = channels  # Show all channels
    else:
        selected_channel_idx = self.brachy_spinBox_01.value() - 1  # Get the index from the spinbox
        channels_to_display = [channels[selected_channel_idx]]  # Show only the selected channel

    # Get the point size from the spinbox
    point_size = self.dw_ch_point_size.value() /1.5

    # Get the current slice reference Z position and tolerance
    Ref_z = self.current_axial_slice_index[0] * self.slice_thick[0] + self.Im_Offset[0, 2]
    z_tolerance = self.slice_thick[0] /2

    # Iterate through the channels to display dwell positions
    for current_ch in channels_to_display:
        dwell_info = current_ch.get('DwellInfo')

        if dwell_info is None or not isinstance(dwell_info, np.ndarray) or dwell_info.shape[1] < 7:
            continue  # Skip invalid channels

        # Extract dwell positions (X, Y, Z coordinates) and convert them to image space
        dwell_times = dwell_info[:, 2]  # Assuming dwell time is in column 2
        x = dwell_info[:, 3] - self.Im_PatPosition[0, 0]  # X coordinate in mm
        y = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - (dwell_info[:, 4] - self.Im_PatPosition[0, 1])  # Y coordinate
        z = dwell_info[:, 5] - self.Im_PatPosition[0, 2]  # Z coordinate in mm

        for i in range(len(x)):
            # Convert physical coordinates (mm) to pixel coordinates
            x_pixel = x[i]
            y_pixel = y[i]
            z_position = 0.5  # Set Z position slightly above the DICOM slice

            # Determine the color based on dwell time and Z position
            if dwell_times[i] == 0:
                # Dwell time is 0, show in red
                color = (1.0, 0.0, 0.0)  # Red
            elif Ref_z - z_tolerance <= z[i] <= Ref_z + z_tolerance:
                # Z position is within Ref_Z ± slice_thickness/2, show in light green
                color = (0.6, 1.0, 0.8)  # Light green
            else:
                # Dwell time > 0 and Z position is outside the tolerance, show in dark green
                color = (0.0, 0.5, 0.0)  # Dark green

            # Create a sphere to represent the dwell position
            sphere_source = vtk.vtkSphereSource()
            sphere_source.SetCenter(x_pixel, y_pixel, z_position)
            sphere_source.SetRadius(point_size)  # Use point size from the spinbox
            sphere_source.SetPhiResolution(20)
            sphere_source.SetThetaResolution(20)

            # Map the sphere to an actor
            sphere_mapper = vtk.vtkPolyDataMapper()
            sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())

            sphere_actor = vtk.vtkActor()
            sphere_actor.SetMapper(sphere_mapper)

            # Set the color based on the logic above
            sphere_actor.GetProperty().SetColor(*color)
            sphere_actor.GetProperty().SetOpacity(0.8)  # Full opacity

            # Add the actor for the sphere to the renderer
            renderer.AddActor(sphere_actor)
            self.dwell_actors_ax.append(sphere_actor)

    # Re-render to show the updated scene with dwell positions
    self.vtkWidgetAxial.GetRenderWindow().Render()


def display_brachy_channel_overlay_ax(self):
    """
    Display brachytherapy channels as connected blue lines with solid blue spheres at each channel point.
    - If the checkbox self.overlay_all_channels is selected, display all channels.
    - Otherwise, display only the channel indicated by self.brachy_spinBox_01.
    """
    renderer = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()

    # Remove any previous channel actors
    for actor in self.channel_actors_ax:
        renderer.RemoveActor(actor)
    self.channel_actors_ax.clear()

    # Retrieve channels from dicom_data
    try:
        meta = (self.dicom_data[self.patientID][self.studyID]          # may raise KeyError
                                [self.modality][self.series_index]
                                ['metadata'])
        channels = meta.get('Plan_Brachy_Channels')
    except KeyError:
        # Data tree incomplete (no metadata at all) ─ silently abort
        return

    if not channels:                     # None or empty list
        return                           # nothing to draw

    # Determine whether to show all channels or only the one selected by the spinbox
    if self.overlay_all_channels.isChecked():
        channels_to_display = channels  # Show all channels
    else:
        selected_channel_idx = self.brachy_spinBox_01.value() - 1  # Get the index from the spinbox
        channels_to_display = [channels[selected_channel_idx]]  # Show only the selected channel

    # Get the point size from the spinbox and halve it
    point_size = self.dw_ch_point_size.value() / 2

    # Iterate through the channels to display
    for current_ch in channels_to_display:
        ch_points = current_ch.get('ChPos')

        # Check if 'ChPos' exists and contains valid data
        if ch_points is None or not isinstance(ch_points, np.ndarray) or ch_points.shape[1] < 3:
            continue  # Skip invalid channels

        # Extract channel points (X, Y, Z coordinates)
        x = ch_points[:, 0] - self.Im_PatPosition[0, 0]  # X coordinate in mm
        y = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - (ch_points[:, 1] - self.Im_PatPosition[0, 1])  # Y coordinate
        z = ch_points[:, 2] - self.Im_PatPosition[0, 2]  # Z coordinate in mm

        # Create a polyline to represent the connected channel points
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        # Add points and create lines between consecutive points
        for i in range(len(x)):
            points.InsertNextPoint(x[i], y[i], 0.5)  # Insert each point into vtkPoints
            if i > 0:
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0, i - 1)  # Line from previous point to current point
                line.GetPointIds().SetId(1, i)
                lines.InsertNextCell(line)

            # Create solid blue spheres for each point
            sphere_source = vtk.vtkSphereSource()
            sphere_source.SetCenter(x[i], y[i], 0.5)
            sphere_source.SetRadius(point_size)  # Sphere size is half of the value from the spinbox
            sphere_source.SetPhiResolution(20)
            sphere_source.SetThetaResolution(20)

            # Map the sphere to an actor
            sphere_mapper = vtk.vtkPolyDataMapper()
            sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())

            sphere_actor = vtk.vtkActor()
            sphere_actor.SetMapper(sphere_mapper)

            # Set the color to solid blue for the spheres
            sphere_actor.GetProperty().SetColor(0.0, 0.0, 1.0)  # Solid blue spheres
            sphere_actor.GetProperty().SetOpacity(0.7)  # Full opacity

            # Add the actor for the sphere to the renderer
            renderer.AddActor(sphere_actor)
            self.channel_actors_ax.append(sphere_actor)

        # Create the polyline
        polyline = vtk.vtkPolyData()
        polyline.SetPoints(points)
        polyline.SetLines(lines)

        # Map the polyline to an actor
        polyline_mapper = vtk.vtkPolyDataMapper()
        polyline_mapper.SetInputData(polyline)

        polyline_actor = vtk.vtkActor()
        polyline_actor.SetMapper(polyline_mapper)
        polyline_actor.GetProperty().SetColor(0.0, 0.0, 1.0)  # Blue for the line
        polyline_actor.GetProperty().SetLineWidth(2)  # Line width

        # Add the polyline actor to the renderer
        renderer.AddActor(polyline_actor)
        self.channel_actors_ax.append(polyline_actor)

    # Render the updated display with the channels
    self.vtkWidgetAxial.GetRenderWindow().Render()


def displaycoronal(self, Im = None):
    # ------------------------------------------------------------------
    if (not hasattr(self, "display_data") or
        self.display_data is None or
        len(self.display_data) == 0):
        return   
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
        if i == 3 and  self.display_dw_overlay.isChecked():
            # Check if the required fields exist in dicom_data
                display_dwell_positions_co(self)
        if i == 3 and  self.display_brachy_channel_overlay.isChecked():
            # Check if the required fields exist in dicom_data
                display_brachy_channel_overlay_co(self)
        if i == 3:
                disp_structure_overlay_coronal(self)

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
    self.sliceChanged.emit("coronal", self.current_coronal_slice_index)

def disp_structure_overlay_coronal(self):
    """
    Show checked structures in the *coronal* renderer.

    * Actors are created on-demand from stored Contours2D and cached
      in RAM (structure_data['VTKActors2D']['coronal']).

    * No VTK objects are ever written back to disk, so the bundle
      remains pickle-safe.
    """
    renderer = (
        self.vtkWidgetCoronal.GetRenderWindow()
        .GetRenderers()
        .GetFirstRenderer()
    )


    # ─── clear previous overlay ───────────────────────────────────────
    for actor in getattr(self, "structure_actors_co", []):
        renderer.RemoveActor(actor)
    self.structure_actors_co = []

    # ─── fetch data for current series ────────────────────────────────
    series_dict = (
        self.dicom_data[self.patientID][self.studyID]
                       [self.modality][self.series_index]
    )
    if not series_dict.get("structures"):
        return                         # nothing to draw

    slice_idx = self.current_coronal_slice_index[0]   # Y index

    # pixel spacing for coronal slices: (row = z, col = x)
    px_spacing = (self.slice_thick[0], self.pixel_spac[0, 0])

    for i in range(self.STRUCTlist.count()):
        widget = self.STRUCTlist.itemWidget(self.STRUCTlist.item(i))
        if not widget.checkbox.isChecked():
            continue

        s_key = getattr(widget, "structure_key", None)
        if s_key is None:
            continue

        s_data = series_dict["structures"].get(s_key, {})

        # ── 1) make sure axial actors exist  if not create all ──────────────────────────
        if 'Contours2D' not in s_data:
            return
        if not s_data['Contours2D']:
            return

        # ── 1) make sure coronal actors exist ─────────────────────────
        if "VTKActors2D" not in s_data:
            s_data["VTKActors2D"] = {}

        if "coronal" not in s_data["VTKActors2D"]:
            contours_cor = s_data.get("Contours2D", {}).get("coronal", {})
            s_data["VTKActors2D"]["coronal"] = actors_from_contours(
                contours_cor, px_spacing,
                line_width=widget.line_width_spinbox.value(),
                color=widget.selectedColor.getRgbF()[:3]
                      if widget.selectedColor else (1, 0, 0),
            )

        actors_dict = s_data["VTKActors2D"]["coronal"]
        if slice_idx not in actors_dict:
            continue                    # no contour on this Y slice

        src_actor = actors_dict[slice_idx]

        # ── 2) customise per-UI-settings ─────────────────────────────
        actor = vtk.vtkActor()
        actor.ShallowCopy(src_actor)
        actor.GetProperty().SetColor(
            widget.selectedColor.getRgbF()[:3]
            if widget.selectedColor else (1, 1, 1)
        )
        actor.GetProperty().SetOpacity(1 - widget.transparency_spinbox.value())
        actor.GetProperty().SetLineWidth(widget.line_width_spinbox.value())
        actor.GetProperty().SetRepresentationToWireframe()

        # place slightly above image plane so wireframe is visible
        actor.SetPosition(self.Im_Offset[0, 0],    # X shift
                          self.Im_Offset[0, 2],    # Z shift (coronal view)
                          2000)

        renderer.AddActor(actor)
        self.structure_actors_co.append(actor)

    self.vtkWidgetCoronal.GetRenderWindow().Render()

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
    

def display_dwell_positions_co(self):
    """
    Display the dwell positions on top of the DICOM images using VTK.
    - If self.overlay_all_channels is selected, show all dwell positions from all channels.
    - Otherwise, show dwell positions for the channel selected by self.brachy_spinBox_01.
    - Uses the same point size as defined by self.dw_ch_point_size.
    - Dwell positions with dwell_time == 0 are shown in red.
    - Dwell positions with dwell_time > 0 are shown in dark green.
    - Dwell positions within Ref_Z ± slice_thickness/2 are shown in light green.
    """
    renderer = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()

    # Remove any previous dwell actors
    for actor in self.dwell_actors_co:
        renderer.RemoveActor(actor)
    self.dwell_actors_co.clear()

    # Retrieve channels from dicom_data
    try:
        meta = (self.dicom_data[self.patientID][self.studyID]          # may raise KeyError
                                [self.modality][self.series_index]
                                ['metadata'])
        channels = meta.get('Plan_Brachy_Channels')
    except KeyError:
        # Data tree incomplete (no metadata at all) ─ silently abort
        return

    if not channels:                     # None or empty list
        return                           # nothing to draw

    # Determine whether to show all channels or only the one selected by the spinbox
    if self.overlay_all_channels.isChecked():
        channels_to_display = channels  # Show all channels
    else:
        selected_channel_idx = self.brachy_spinBox_01.value() - 1  # Get the index from the spinbox
        channels_to_display = [channels[selected_channel_idx]]  # Show only the selected channel

    # Get the point size from the spinbox
    point_size = self.dw_ch_point_size.value() /1.5

    # Get the current slice reference Z position and tolerance
    Ref_z = self.current_coronal_slice_index[0] * self.pixel_spac[0, 1] #+ self.Im_Offset[1, 2]
    z_tolerance = self.pixel_spac[0, 1] /2

    # Iterate through the channels to display dwell positions
    for current_ch in channels_to_display:
        dwell_info = current_ch.get('DwellInfo')

        if dwell_info is None or not isinstance(dwell_info, np.ndarray) or dwell_info.shape[1] < 7:
            continue  # Skip invalid channels

        # Extract dwell positions (X, Y, Z coordinates) and convert them to image space
        dwell_times = dwell_info[:, 2]  # Assuming dwell time is in column 2
        x = dwell_info[:, 3] - self.Im_PatPosition[0, 0]  # X coordinate in mm
        z = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - (dwell_info[:, 4] - self.Im_PatPosition[0, 1])  # Y coordinate
        y = dwell_info[:, 5] - self.Im_PatPosition[0, 2]  # Z coordinate in mm

        for i in range(len(x)):
            # Convert physical coordinates (mm) to pixel coordinates
            x_pixel = x[i]
            y_pixel = y[i]
            z_position = 0.5  # Set Z position slightly above the DICOM slice

            # Determine the color based on dwell time and Z position
            if dwell_times[i] == 0:
                # Dwell time is 0, show in red
                color = (1.0, 0.0, 0.0)  # Red
            elif Ref_z - z_tolerance <= z[i] <= Ref_z + z_tolerance:
                # Z position is within Ref_Z ± slice_thickness/2, show in light green
                color = (0.6, 1.0, 0.6)  # Light green
            else:
                # Dwell time > 0 and Z position is outside the tolerance, show in dark green
                color = (0.0, 0.5, 0.0)  # Dark green

            # Create a sphere to represent the dwell position
            sphere_source = vtk.vtkSphereSource()
            sphere_source.SetCenter(x_pixel, y_pixel, z_position)
            sphere_source.SetRadius(point_size)  # Use point size from the spinbox
            sphere_source.SetPhiResolution(20)
            sphere_source.SetThetaResolution(20)

            # Map the sphere to an actor
            sphere_mapper = vtk.vtkPolyDataMapper()
            sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())

            sphere_actor = vtk.vtkActor()
            sphere_actor.SetMapper(sphere_mapper)

            # Set the color based on the logic above
            sphere_actor.GetProperty().SetColor(*color)
            sphere_actor.GetProperty().SetOpacity(0.8)  # Full opacity

            # Add the actor for the sphere to the renderer
            renderer.AddActor(sphere_actor)
            self.dwell_actors_co.append(sphere_actor)

    # Re-render to show the updated scene with dwell positions
    self.vtkWidgetCoronal.GetRenderWindow().Render()


def display_brachy_channel_overlay_co(self):
    """
    Display brachytherapy channels as connected blue lines with solid blue spheres at each channel point.
    - If the checkbox self.overlay_all_channels is selected, display all channels.
    - Otherwise, display only the channel indicated by self.brachy_spinBox_01.
    """
    renderer = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()

    # Remove any previous channel actors
    for actor in self.channel_actors_co:
        renderer.RemoveActor(actor)
    self.channel_actors_co.clear()

    # Retrieve channels from dicom_data
    try:
        meta = (self.dicom_data[self.patientID][self.studyID]          # may raise KeyError
                                [self.modality][self.series_index]
                                ['metadata'])
        channels = meta.get('Plan_Brachy_Channels')
    except KeyError:
        # Data tree incomplete (no metadata at all) ─ silently abort
        return

    if not channels:                     # None or empty list
        return                           # nothing to draw

    # Determine whether to show all channels or only the one selected by the spinbox
    if self.overlay_all_channels.isChecked():
        channels_to_display = channels  # Show all channels
    else:
        selected_channel_idx = self.brachy_spinBox_01.value() - 1  # Get the index from the spinbox
        channels_to_display = [channels[selected_channel_idx]]  # Show only the selected channel

    # Get the point size from the spinbox and halve it
    point_size = self.dw_ch_point_size.value() / 2

    # Iterate through the channels to display
    for current_ch in channels_to_display:
        ch_points = current_ch.get('ChPos')

        # Check if 'ChPos' exists and contains valid data
        if ch_points is None or not isinstance(ch_points, np.ndarray) or ch_points.shape[1] < 3:
            continue  # Skip invalid channels

        # Extract channel points (X, Y, Z coordinates)
        x = ch_points[:, 0] - self.Im_PatPosition[0, 0]  # X coordinate in mm
        z = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - (ch_points[:, 1] - self.Im_PatPosition[0, 1])  # Y coordinate
        y = ch_points[:, 2] - self.Im_PatPosition[0, 2]  # Z coordinate in mm

        # Create a polyline to represent the connected channel points
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        # Add points and create lines between consecutive points
        for i in range(len(x)):
            points.InsertNextPoint(x[i], y[i], 0.5)  # Insert each point into vtkPoints
            if i > 0:
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0, i - 1)  # Line from previous point to current point
                line.GetPointIds().SetId(1, i)
                lines.InsertNextCell(line)

            # Create solid blue spheres for each point
            sphere_source = vtk.vtkSphereSource()
            sphere_source.SetCenter(x[i], y[i], 0.5)
            sphere_source.SetRadius(point_size)  # Sphere size is half of the value from the spinbox
            sphere_source.SetPhiResolution(20)
            sphere_source.SetThetaResolution(20)

            # Map the sphere to an actor
            sphere_mapper = vtk.vtkPolyDataMapper()
            sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())

            sphere_actor = vtk.vtkActor()
            sphere_actor.SetMapper(sphere_mapper)

            # Set the color to solid blue for the spheres
            sphere_actor.GetProperty().SetColor(0.0, 0.0, 1.0)  # Solid blue spheres
            sphere_actor.GetProperty().SetOpacity(0.7)  # Full opacity

            # Add the actor for the sphere to the renderer
            renderer.AddActor(sphere_actor)
            self.channel_actors_co.append(sphere_actor)

        # Create the polyline
        polyline = vtk.vtkPolyData()
        polyline.SetPoints(points)
        polyline.SetLines(lines)

        # Map the polyline to an actor
        polyline_mapper = vtk.vtkPolyDataMapper()
        polyline_mapper.SetInputData(polyline)

        polyline_actor = vtk.vtkActor()
        polyline_actor.SetMapper(polyline_mapper)
        polyline_actor.GetProperty().SetColor(0.0, 0.0, 1.0)  # Blue for the line
        polyline_actor.GetProperty().SetLineWidth(2)  # Line width

        # Add the polyline actor to the renderer
        renderer.AddActor(polyline_actor)
        self.channel_actors_co.append(polyline_actor)

    # Render the updated display with the channels
    self.vtkWidgetCoronal.GetRenderWindow().Render()






def displaysagittal(self,Im = None):

    # ------------------------------------------------------------------
    if (not hasattr(self, "display_data") or
        self.display_data is None or
        len(self.display_data) == 0):
        return                    # nothing loaded → ignore the call


    
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
        if i == 3 and  self.display_dw_overlay.isChecked():
            # Check if the required fields exist in dicom_data
                display_dwell_positions_sa(self)
        if i == 3 and  self.display_brachy_channel_overlay.isChecked():
            # Check if the required fields exist in dicom_data
                display_brachy_channel_overlay_sa(self)    
        if i == 3:
            disp_structure_overlay_sagittal(self)

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
    self.vtkWidgetSagittal.GetRenderWindow().Render()
    self.vtkWidgetCoronal.GetRenderWindow().Render()
    self.vtkWidgetAxial.GetRenderWindow().Render()
    self.sliceChanged.emit("coronal", self.current_sagittal_slice_index)
    

def disp_structure_overlay_sagittal(self):
    """
    Show checked structures in the *sagittal* renderer.

    • Creates actors on-demand from Contours2D → vtkActor, caches them.
    • Reuses cached actors on subsequent calls for speed.
    • UI controls (colour, opacity, line-width) still work per structure.
    """
    renderer = (
        self.vtkWidgetSagittal.GetRenderWindow()
        .GetRenderers()
        .GetFirstRenderer()
    )


    # ── clear existing overlay ────────────────────────────────────────
    for actor in getattr(self, "structure_actors_sa", []):
        renderer.RemoveActor(actor)
    self.structure_actors_sa = []

    # ── fetch current series data ─────────────────────────────────────
    series_dict = (
        self.dicom_data[self.patientID][self.studyID]
                       [self.modality][self.series_index]
    )
    if not series_dict.get("structures"):
        return                              # nothing to draw

    slice_idx = self.current_sagittal_slice_index[0]   # X index

    # pixel spacing for sagittal slices: (row = z, col = y)
    px_spacing = (self.slice_thick[0], self.pixel_spac[0, 1])

    for i in range(self.STRUCTlist.count()):
        widget = self.STRUCTlist.itemWidget(self.STRUCTlist.item(i))
        if not widget.checkbox.isChecked():
            continue

        s_key = getattr(widget, "structure_key", None)
        if s_key is None:
            continue

        s_data = series_dict["structures"].get(s_key, {})

        # ── 1) make sure sagittal actors exist ───────────────────────
        if 'Contours2D' not in s_data:
            return
        if not s_data['Contours2D']:
            return
            
        if "VTKActors2D" not in s_data:
            s_data["VTKActors2D"] = {}

        if "sagittal" not in s_data["VTKActors2D"]:
            # build once, cache in RAM
            contours_sag = s_data.get("Contours2D", {}).get("sagittal", {})
            s_data["VTKActors2D"]["sagittal"] = actors_from_contours(
                contours_sag, px_spacing,
                line_width=widget.line_width_spinbox.value(),
                color=widget.selectedColor.getRgbF()[:3]
                      if widget.selectedColor else (1, 0, 0),
            )

        actors_dict = s_data["VTKActors2D"]["sagittal"]
        if slice_idx not in actors_dict:
            continue                          # no contour on this X slice

        src_actor = actors_dict[slice_idx]

        # ── 2) clone & style according to UI ─────────────────────────
        actor = vtk.vtkActor()
        actor.ShallowCopy(src_actor)
        actor.GetProperty().SetColor(
            widget.selectedColor.getRgbF()[:3]
            if widget.selectedColor else (1, 1, 1)
        )
        actor.GetProperty().SetOpacity(1 - widget.transparency_spinbox.value())
        actor.GetProperty().SetLineWidth(widget.line_width_spinbox.value())
        actor.GetProperty().SetRepresentationToWireframe()

        # place slightly above image plane for visibility
        actor.SetPosition(self.Im_Offset[0, 1],    # Y shift
                          self.Im_Offset[0, 2],    # Z shift
                          2000)

        renderer.AddActor(actor)
        self.structure_actors_sa.append(actor)

    self.vtkWidgetSagittal.GetRenderWindow().Render()


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


def display_dwell_positions_sa(self):
    """
    Display the dwell positions on top of the DICOM images using VTK.
    - If self.overlay_all_channels is selected, show all dwell positions from all channels.
    - Otherwise, show dwell positions for the channel selected by self.brachy_spinBox_01.
    - Uses the same point size as defined by self.dw_ch_point_size.
    - Dwell positions with dwell_time == 0 are shown in red.
    - Dwell positions with dwell_time > 0 are shown in dark green.
    - Dwell positions within Ref_Z ± slice_thickness/2 are shown in light green.
    """
    renderer = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()

    # Remove any previous dwell actors
    for actor in self.dwell_actors_sa:
        renderer.RemoveActor(actor)
    self.dwell_actors_sa.clear()

    # Retrieve channels from dicom_data
    try:
        meta = (self.dicom_data[self.patientID][self.studyID]          # may raise KeyError
                                [self.modality][self.series_index]
                                ['metadata'])
        channels = meta.get('Plan_Brachy_Channels')
    except KeyError:
        # Data tree incomplete (no metadata at all) ─ silently abort
        return

    if not channels:                     # None or empty list
        return                           # nothing to draw

    # Determine whether to show all channels or only the one selected by the spinbox
    if self.overlay_all_channels.isChecked():
        channels_to_display = channels  # Show all channels
    else:
        selected_channel_idx = self.brachy_spinBox_01.value() - 1  # Get the index from the spinbox
        channels_to_display = [channels[selected_channel_idx]]  # Show only the selected channel

    # Get the point size from the spinbox
    point_size = self.dw_ch_point_size.value() /1.5

    # Get the current slice reference Z position and tolerance
    Ref_z = self.current_sagittal_slice_index[0] * self.pixel_spac[0, 0] #- self.Im_Offset[1, 2]
    z_tolerance = self.pixel_spac[0, 0] /2
    # Iterate through the channels to display dwell positions
    for current_ch in channels_to_display:
        dwell_info = current_ch.get('DwellInfo')

        if dwell_info is None or not isinstance(dwell_info, np.ndarray) or dwell_info.shape[1] < 7:
            continue  # Skip invalid channels

        # Extract dwell positions (X, Y, Z coordinates) and convert them to image space
        dwell_times = dwell_info[:, 2]  # dwell time is in column 2
        z = dwell_info[:, 3] - self.Im_PatPosition[0, 0]                                                              # X coordinate in mm
        x = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - (dwell_info[:, 4] - self.Im_PatPosition[0, 1])  # Y coordinate
        y = dwell_info[:, 5] - self.Im_PatPosition[0, 2]                                                              # Z coordinate in mm
        for i in range(len(x)):
            # Convert physical coordinates (mm) to pixel coordinates
            x_pixel = x[i]
            y_pixel = y[i]
            z_position = 0.5  # Set Z position slightly above the DICOM slice

            # Determine the color based on dwell time and Z position
            if dwell_times[i] == 0:
                # Dwell time is 0, show in red
                color = (1.0, 0.0, 0.0)  # Red
            elif Ref_z - z_tolerance <= z[i] <= Ref_z + z_tolerance:
                # Z position is within Ref_Z ± slice_thickness/2, show in light green
                color = (0.6, 1.0, 0.6)  # Light green
            else:
                # Dwell time > 0 and Z position is outside the tolerance, show in dark green
                color = (0.0, 0.5, 0.0)  # Dark green

            # Create a sphere to represent the dwell position
            sphere_source = vtk.vtkSphereSource()
            sphere_source.SetCenter(x_pixel, y_pixel, z_position)
            sphere_source.SetRadius(point_size)  # Use point size from the spinbox
            sphere_source.SetPhiResolution(20)
            sphere_source.SetThetaResolution(20)

            # Map the sphere to an actor
            sphere_mapper = vtk.vtkPolyDataMapper()
            sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())

            sphere_actor = vtk.vtkActor()
            sphere_actor.SetMapper(sphere_mapper)

            # Set the color based on the logic above
            sphere_actor.GetProperty().SetColor(*color)
            sphere_actor.GetProperty().SetOpacity(0.8)  # Full opacity

            # Add the actor for the sphere to the renderer
            renderer.AddActor(sphere_actor)
            self.dwell_actors_sa.append(sphere_actor)

    # Re-render to show the updated scene with dwell positions
    self.vtkWidgetSagittal.GetRenderWindow().Render()


def display_brachy_channel_overlay_sa(self):
    """
    Display brachytherapy channels as connected blue lines with solid blue spheres at each channel point.
    - If the checkbox self.overlay_all_channels is selected, display all channels.
    - Otherwise, display only the channel indicated by self.brachy_spinBox_01.
    """
    renderer = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()

    # Remove any previous channel actors
    for actor in self.channel_actors_sa:
        renderer.RemoveActor(actor)
    self.channel_actors_sa.clear()

    # Retrieve channels from dicom_data
    try:
        meta = (self.dicom_data[self.patientID][self.studyID]          # may raise KeyError
                                [self.modality][self.series_index]
                                ['metadata'])
        channels = meta.get('Plan_Brachy_Channels')
    except KeyError:
        # Data tree incomplete (no metadata at all) ─ silently abort
        return

    if not channels:                     # None or empty list
        return                           # nothing to draw

    # Determine whether to show all channels or only the one selected by the spinbox
    if self.overlay_all_channels.isChecked():
        channels_to_display = channels  # Show all channels
    else:
        selected_channel_idx = self.brachy_spinBox_01.value() - 1  # Get the index from the spinbox
        channels_to_display = [channels[selected_channel_idx]]  # Show only the selected channel

    # Get the point size from the spinbox and halve it
    point_size = self.dw_ch_point_size.value() / 2

    # Iterate through the channels to display
    for current_ch in channels_to_display:
        ch_points = current_ch.get('ChPos')

        # Check if 'ChPos' exists and contains valid data
        if ch_points is None or not isinstance(ch_points, np.ndarray) or ch_points.shape[1] < 3:
            continue  # Skip invalid channels

        # Extract channel points (X, Y, Z coordinates)
        z = ch_points[:, 0] - self.Im_PatPosition[0, 0]  # X coordinate in mm
        x = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - (ch_points[:, 1] - self.Im_PatPosition[0, 1])  # Y coordinate
        y = ch_points[:, 2] - self.Im_PatPosition[0, 2]  # Z coordinate in mm

        # Create a polyline to represent the connected channel points
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        # Add points and create lines between consecutive points
        for i in range(len(x)):
            points.InsertNextPoint(x[i], y[i], 0.5)  # Insert each point into vtkPoints
            if i > 0:
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0, i - 1)  # Line from previous point to current point
                line.GetPointIds().SetId(1, i)
                lines.InsertNextCell(line)

            # Create solid blue spheres for each point
            sphere_source = vtk.vtkSphereSource()
            sphere_source.SetCenter(x[i], y[i], 0.5)
            sphere_source.SetRadius(point_size)  # Sphere size is half of the value from the spinbox
            sphere_source.SetPhiResolution(20)
            sphere_source.SetThetaResolution(20)

            # Map the sphere to an actor
            sphere_mapper = vtk.vtkPolyDataMapper()
            sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())

            sphere_actor = vtk.vtkActor()
            sphere_actor.SetMapper(sphere_mapper)

            # Set the color to solid blue for the spheres
            sphere_actor.GetProperty().SetColor(0.0, 0.0, 1.0)  # Solid blue spheres
            sphere_actor.GetProperty().SetOpacity(0.7)  # Full opacity

            # Add the actor for the sphere to the renderer
            renderer.AddActor(sphere_actor)
            self.channel_actors_sa.append(sphere_actor)

        # Create the polyline
        polyline = vtk.vtkPolyData()
        polyline.SetPoints(points)
        polyline.SetLines(lines)

        # Map the polyline to an actor
        polyline_mapper = vtk.vtkPolyDataMapper()
        polyline_mapper.SetInputData(polyline)

        polyline_actor = vtk.vtkActor()
        polyline_actor.SetMapper(polyline_mapper)
        polyline_actor.GetProperty().SetColor(0.0, 0.0, 1.0)  # Blue for the line
        polyline_actor.GetProperty().SetLineWidth(2)  # Line width

        # Add the polyline actor to the renderer
        renderer.AddActor(polyline_actor)
        self.channel_actors_sa.append(polyline_actor)

    # Render the updated display with the channels
    self.vtkWidgetSagittal.GetRenderWindow().Render()


def update_layer_view(self):
    idx = self.layer_selection_box.currentIndex()
    tabName = self.tabModules.tabText(self.tabModules.currentIndex())
    self.layerTab[tabName] = idx
    if self.tabModules.tabText(self.tabModules.currentIndex()) != "segmentation":
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


