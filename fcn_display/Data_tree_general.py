import numpy as np
from PyQt5.QtGui import  QStandardItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QCheckBox
from fcn_display.display_images  import displayaxial, displaycoronal, displaysagittal
from pydicom.multival import MultiValue
from fcn_display.meta_viewer import update_meta_view_table_dicom
from fcn_display.disp_data_type import adjust_data_type_input, adjust_data_type_comp_input, adjust_data_type_input_IrIS_eval, adjust_data_type_seg_input
from fcn_display.display_images_comp import disp_comp_image_slice
from fcn_display.display_images_seg import disp_seg_image_slice
from fcn_init.vtk_hist import set_vtk_histogran_fig
from fcn_display.colormap_set import set_color_map
from fcn_display.win_level import set_window
from fcn_display.disp_plan_data import update_plan_tables
from fcn_RTFiles.process_rt_files import update_structure_list_widget
from fcn_RTFiles.process_contours import find_matching_series
from fcn_segmentation.functions_segmentation import plot_hist
from fcn_3Dview.volume_3d_viewer import VTK3DViewerMixin,initialize_3Dsliders, initialize_crop_widgets
from fcn_materialassignment.material_map import update_mat_struct_list



def on_DataTreeView_clicked(self,index):
    model = self.DataTreeView.model()
    #
    # check file type
    # Extract hierarchy information based on the clicked index
    current_index = index
    hierarchy = []
    hierarchy_indices = []
    while current_index.isValid():
        hierarchy.append(model.itemFromIndex(current_index).text())
        hierarchy_indices.append(current_index)
        current_index = current_index.parent()
    # Reverse the hierarchy data so it starts from the topmost level
    hierarchy.reverse()
    hierarchy_indices.reverse()
    idx = self.layer_selection_box.currentIndex()
    currentTabText = self.tabModules.tabText(self.tabModules.currentIndex())
    #
    if hierarchy[0] == "DICOM":
        self.DataType = "DICOM"  
        # clear metadata search field
        # Temporarily block signals so this won't fire textChanged again
        self.metadata_search.blockSignals(True)
        self.metadata_search.setText("")
        # Unblock signals
        self.metadata_search.blockSignals(False)
        if len(hierarchy) >= 5:
            self.series_index = hierarchy_indices[4].row()
            # need to remove part of the tag otherwise it does not match with the key:
            self.patientID = hierarchy[1].replace("PatientID: ", "")
            self.studyID   = hierarchy[2].replace("StudyID: ", "")
            self.modality  = hierarchy[3].replace("Modality: ", "")
            #
            if self.modality == 'RTPLAN':
                # keep track of the last selected plan ... if user chose and image or dose this will not change
                self.patientID_plan    = hierarchy[1].replace("PatientID: ", "")
                self.studyID_plan      = hierarchy[2].replace("StudyID: ", "")
                self.modality_plan     = hierarchy[3].replace("Modality: ", "")
                self.series_index_plan = self.series_index
                self.modality_metadata = self.modality_plan
                update_meta_view_table_dicom(self,self.dicom_data[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']['DCM_Info'])
                update_plan_tables(self)
                
                return
            if self.modality == 'RTSTRUCT':
                # keep track of the last selected struct file ... if user chose and image or dose this will not change
                self.patientID_struct     = hierarchy[1].replace("PatientID: ", "")
                self.studyID_struct       = hierarchy[2].replace("StudyID: ", "")
                self.modality_struct      = hierarchy[3].replace("Modality: ", "")
                self.series_index_struct  = self.series_index
                # 
                self.modality_metadata = self.modality_struct
                update_meta_view_table_dicom(self,self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['metadata']['DCM_Info'])
                update_structure_list_widget(self,
                                             self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['structures_names'],
                                             self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['structures_keys'],
                                            )
                # find reference series
                Ref = None
                if 'ReferencedFrameOfReferenceSequence' in self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['metadata']['DCM_Info']:
                    if 'RTReferencedStudySequence' in self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['metadata']['DCM_Info']['ReferencedFrameOfReferenceSequence'][0]:
                        if 'RTReferencedSeriesSequence' in self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['metadata']['DCM_Info']['ReferencedFrameOfReferenceSequence'][0]['RTReferencedStudySequence'][0]:
                            Ref = self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]['metadata']['DCM_Info']['ReferencedFrameOfReferenceSequence'][0]['RTReferencedStudySequence'][0]['RTReferencedSeriesSequence'][0].get('SeriesInstanceUID')
                
                if Ref is not None:
                    ref_series = find_matching_series(self, Ref)

                # Select the struct tab
                self.tabView01.setCurrentIndex(3)
                return
            #print(self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['AcquisitionNumber'])
            # Assign data and display init image
            #
            Window = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['WindowWidth']
            Level  = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['WindowCenter']
            # For Window
            if Window in ('N/A', None) or Level in ('N/A', None):
                Window = 100
                Level = 0
            else:
                if isinstance(Window, MultiValue):
                    Window = float(Window[0])
                else:
                    Window = float(Window)
                if isinstance(Level, MultiValue):
                    Level = float(Level[0])
                else:
                    Level = float(Level) 
            #
            if idx == 0:
                self.LayerAlpha[0] = 1.0
                self.Layer_0_alpha_sli.setValue(int(self.LayerAlpha[0]*100))
            elif idx==1:
                self.LayerAlpha[1] = 0.6
                self.Layer_1_alpha_sli.setValue(int(self.LayerAlpha[1]*100))
            elif idx==2:
                self.LayerAlpha[2] = 0.6
                self.Layer_2_alpha_sli.setValue(int(self.LayerAlpha[2]*100))
            #
            # check the current module
            if currentTabText == "View":
                
                if len(hierarchy) >= 6 and hierarchy[5] == "Structures": 
                    # structures withing a SERIES
                    update_structure_list_widget(self,
                                self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures_names'],
                                self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures_keys']
                            )


                # list series from the same acquisition and populate a table so the user can pick what to display
                populate_CT4D_table(self)
                #
                if len(hierarchy) == 5: # Series
                    self.display_data[idx] = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix']
                if len(hierarchy) == 7: # binary mask contour or density map
                    
                    if hierarchy[5]=='Structures':
                        s_key = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures_keys'][hierarchy_indices[6].row()]
                        self.display_data[idx] = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures'][s_key]['Mask3D']
                    elif hierarchy[5]=='Density maps':
                       self.display_data[idx] = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['density_maps'][hierarchy[6]]['3DMatrix']
                    elif hierarchy[5]=='Material maps':
                       self.display_data[idx] = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['mat_maps'][hierarchy[6]]['3DMatrix']
                        
                    
                adjust_data_type_input(self,idx)
                #
                self.current_axial_slice_index[idx]    = round(self.display_data[idx].shape[0]/2)
                self.current_sagittal_slice_index[idx] = round(self.display_data[idx].shape[1]/2)
                self.current_coronal_slice_index[idx]  = round(self.display_data[idx].shape[2]/2)
                #
    
                # update_metadata_table
                meta_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']
                if 'DCM_Info' in meta_dict:
                    update_meta_view_table_dicom(self, meta_dict['DCM_Info'])
                self.modality_metadata = self.modality
                # display info
                display_dicom_info(self)
                # Accessing the values
                self.slice_thick[idx]         = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['SliceThickness']
                self.pixel_spac[idx, :2]      = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['PixelSpacing']
                self.Im_PatPosition[idx, :3]  = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['ImagePositionPatient']
                #
                if idx>0:
                    self.Im_Offset[idx,0]   = (self.Im_PatPosition[idx,0]-self.Im_PatPosition[0,0])
                    self.Im_Offset[idx,1]   = (self.display_data[0].shape[1]*self.pixel_spac[0,0]-self.display_data[idx].shape[1]*self.pixel_spac[idx,0])-(self.Im_PatPosition[idx,1]-self.Im_PatPosition[0,1])
                    self.Im_Offset[idx,2]   = (self.Im_PatPosition[idx,2]-self.Im_PatPosition[0,2])
                #
                # Update the slider's value to match the current slice index
                # Setting the maximum will call slider change function chaging the current slice...
                # workaround is to keep the value and update laeter
                Ax_s = self.current_axial_slice_index[idx]
                Sa_s = self.current_sagittal_slice_index[idx]
                Co_s = self.current_coronal_slice_index[idx]
                #
                # This is a workaround to avoid issues when changing the data type ... It basically plots the image on the 3 axis to ensure that when the display function
                # is called all axes have the same type of data (e.g. float) ... Using display without update the images cause issues. E.g. display axial will update some 
                # elements on the cornoal axis and the software will crash if axial and coronal images have different types (because one axes update the data type before the other)
                update_axial_image(self)
                self.vtkWidgetAxial.GetRenderWindow().Render()
                update_coronal_image(self)
                self.vtkWidgetCoronal.GetRenderWindow().Render()
                update_sagittal_image(self)
                self.vtkWidgetSagittal.GetRenderWindow().Render()
                #
                #
                displayaxial(self)
                displaysagittal(self)
                displaycoronal(self)
                #
                self.AxialSlider.setMaximum(self.display_data[idx].shape[0] - 1)
                self.SagittalSlider.setMaximum(self.display_data[idx].shape[2] - 1)
                self.CoronalSlider.setMaximum(self.display_data[idx].shape[1] - 1)
                #
                self.AxialSlider.setValue(Ax_s)
                self.SagittalSlider.setValue(Sa_s)
                self.CoronalSlider.setValue(Co_s)
                #
                self.windowLevelAxial[idx].SetWindow(Window)
                self.windowLevelAxial[idx].SetLevel(Level)
                self.windowLevelSagittal[idx].SetWindow(Window)
                self.windowLevelSagittal[idx].SetLevel(Level)
                self.windowLevelCoronal[idx].SetWindow(Window)
                self.windowLevelCoronal[idx].SetLevel(Level)
                #   
                #
                self.textActorAxialWL.SetInput(f"L: {round(Level,2)}  W: {round(Window,2)}")
                self.textActorSagittalWL.SetInput(f"L: {round(Level,2)}  W: {round(Window,2)}")
                self.textActorCoronalWL.SetInput(f"L: {round(Level,2)}  W: {round(Window,2)}")
                #
                self.renAxial.ResetCamera()
                self.renSagittal.ResetCamera()
                self.renCoronal.ResetCamera() 
                #
                #
                displayaxial(self)
                displaysagittal(self)
                displaycoronal(self)
                #    
                set_vtk_histogran_fig(self)
                #
            elif currentTabText == "_3Dview":
                # Matrix to display + spacing
                idx                                 = self.layer_selection_box.currentIndex()
                self.display_3D_data[idx]           = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix']
                self.pixel_spacing3Dview[idx]       = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['PixelSpacing']
                self.slice_thickness3Dview[idx]     = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['SliceThickness']
                #
                self.Im_PatPosition3Dview[idx, :3]  = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['ImagePositionPatient']
                #
                if idx == 0:
                    offset = (0.0, 0.0, 0.0)
                else:
                    base_pos = self.Im_PatPosition3Dview[0]
                    curr_pos = self.Im_PatPosition3Dview[idx]
                    offset   = tuple(np.array(curr_pos) - np.array(base_pos))
                    self.Im_Offset3Dview[idx] = offset

                # load into VTK and display
                self.display_numpy_volume(
                    self.display_3D_data[idx],
                    voxel_spacing=(
                        self.pixel_spacing3Dview[idx,0],
                        self.pixel_spacing3Dview[idx,1],
                        self.slice_thickness3Dview[idx]
                    ),
                    layer_idx=idx,
                    offset=offset
                )

                # ── reset thresholds (and full‐range) for this layer so the sliders jump to the new data
                # clear any old state
                self._thresholds.pop(idx, None)
                self._full_ranges.pop(idx, None)
                # compute new data range
                vol = self.display_3D_data[idx]
                vmin, vmax = float(vol.min()), float(vol.max())
                # re-initialize the two 3D sliders for this layer
                initialize_3Dsliders(self, vmin, vmax)
                # ── now reset the crop‐region sliders for just this layer
                # clear any old crop state
                self._crops.pop(idx, None)
                self._dims .pop(idx, None)
                # volume_np.shape is (Z, Y, X), but initialize_crop_widgets wants (X, Y, Z)
                dz, dy, dx = vol.shape
                initialize_crop_widgets(self, (dx, dy, dz), idx)

                # stop exectution here
                return
            elif currentTabText == "Compare":
                #
                # Current view
                Ax_idx = self.Comp_im_idx.value()
                if Ax_idx ==-1:
                    QMessageBox.warning(None, "Warning", "Create the comparison axes first (bottom-right button)")
                    return
                # layer
                #
                self.display_comp_data[Ax_idx, idx] = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix']
                adjust_data_type_comp_input(self,Ax_idx,idx)

                self.current_AxComp_slice_index[Ax_idx,idx]   = int(self.display_comp_data[Ax_idx, idx].shape[0]/2)
                
                # check the selected view

                if self.Comp_view_sel_box.currentText() == "Axial":
                    self.im_ori_comp[Ax_idx] = 0
                    self.current_AxComp_slice_index[Ax_idx,idx]   = int(self.display_comp_data[Ax_idx, idx].shape[0]/2)
                    Ax_s = self.current_AxComp_slice_index[Ax_idx,idx]
                    self.SliderCompareView.setMaximum(self.display_comp_data[Ax_idx, idx].shape[0] - 1)
                    self.SliderCompareView.setValue(int(Ax_s))        
                elif self.Comp_view_sel_box.currentText() == "Sagittal":
                    self.current_AxComp_slice_index[Ax_idx,idx]   = int(self.display_comp_data[Ax_idx, idx].shape[2]/2)
                    self.im_ori_comp[Ax_idx] = 1
                    Ax_s = self.current_AxComp_slice_index[Ax_idx,idx]
                    self.SliderCompareView.setMaximum(self.display_comp_data[Ax_idx, idx].shape[2] - 1)
                    self.SliderCompareView.setValue(int(Ax_s))     
                elif self.Comp_view_sel_box.currentText() == "Coronal":
                    self.current_AxComp_slice_index[Ax_idx,idx]   = int(self.display_comp_data[Ax_idx, idx].shape[1]/2)
                    self.im_ori_comp[Ax_idx] = 2
                    Ax_s = self.current_AxComp_slice_index[Ax_idx,idx]
                    self.SliderCompareView.setMaximum(self.display_comp_data[Ax_idx, idx].shape[1] - 1)
                    self.SliderCompareView.setValue(int(Ax_s))        
                #
                #
                # Accessing the values
                self.slice_thick_comp[Ax_idx,idx]         = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['SliceThickness']
                self.pixel_spac_comp[Ax_idx,idx, :2]      = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['PixelSpacing']
                self.Im_PatPosition_comp[Ax_idx,idx, :3]  = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['ImagePositionPatient']
                #
                if idx>0:
                    self.Im_Offset_comp[Ax_idx,idx,0]    = (self.Im_PatPosition_comp[Ax_idx, idx,0]-self.Im_PatPosition_comp[Ax_idx,0,0])
                    self.Im_Offset_comp[Ax_idx,idx,1]    = (self.display_comp_data[Ax_idx, 0].shape[1]*self.pixel_spac_comp[Ax_idx,0,0]-self.display_comp_data[Ax_idx, idx].shape[1]*self.pixel_spac_comp[Ax_idx,idx,0])-(self.Im_PatPosition_comp[Ax_idx,idx,1]-self.Im_PatPosition[Ax_idx,0,1])
                    self.Im_Offset_comp[Ax_idx,idx,2]    = (self.Im_PatPosition_comp[Ax_idx,idx,2]-self.Im_PatPosition_comp[Ax_idx,0,2])
                #
                # Add ID 
                self.textActorAxCom[self.Comp_im_idx.value(),0].SetInput(f"{self.modality} / {hierarchy[4]}")
                disp_comp_image_slice(self) 
                #
                Window = self.windowLevelSagittal[idx].GetWindow()
                Level  = self.windowLevelSagittal[idx].GetLevel()
                self.textActorAxCom[Ax_idx,1].SetInput(f"L: {round(Level,2)}  W: {round(Window,2)}")
                layer = self.layer_selection_box.currentIndex()
                for i in range (0,13):
                    if not ((i, layer) in self.display_comp_data and int(self.current_AxComp_slice_index[i, layer]) in self.display_comp_data[i, layer]):
                        continue
                    self.renAxComp[i].ResetCamera()
                    self.renAxComp[i].GetRenderWindow().Render() 
                #
            if currentTabText == "Segmentation":

                if len(hierarchy) >= 6 and hierarchy[5] == "Structures": 
                    # structures withing a SERIES
                    update_structure_list_widget(self,
                                self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures_names'],
                                self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures_keys']
                            )
                    
                if self.seg_win_lev[0] is not None and self.seg_win_lev[1] is not None:
                    Window = self.seg_win_lev[0]
                    Level = self.seg_win_lev[1]
                    
                self.windowLevelSeg[0].SetWindow(Window)
                self.windowLevelSeg[0].SetLevel(Level)
                
                # Accessing the values
                for i in range(3):
                    self.slice_thick_seg[i]         = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['SliceThickness']
                    self.pixel_spac_seg[i, :2]      = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['PixelSpacing']
                    self.Im_PatPosition_seg[i, :3]  = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['ImagePositionPatient']
                #
                if len(hierarchy) == 5: # Series
                    self.display_seg_data = {}
                    self.curr_struc_key = None
                    self.curr_struc_name = None

                    # Get and store the selected series volume
                    self.display_seg_data[0] = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix']
                    adjust_data_type_seg_input(self,0)
                    plot_hist(self)

                    self.display_seg_data[1] = np.zeros(self.display_seg_data[0].shape, dtype=np.uint8)
                    adjust_data_type_seg_input(self,1)
                    
                if len(hierarchy) == 7: # binary mask contour
                    self.display_seg_data = {}

                    # Get and store the corresponding series volume
                    self.display_seg_data[0] = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix']
                    adjust_data_type_seg_input(self,0)
                    plot_hist(self)

                    # Get and store the selected structure 
                    s_key  = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures_keys'][hierarchy_indices[6].row()]
                    s_name = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures_names'][hierarchy_indices[6].row()]
                    self.curr_struc_key = s_key
                    self.curr_struc_name = s_name

                    self.display_seg_data[1] = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures'][s_key]['Mask3D']
                    adjust_data_type_seg_input(self,1)

                    self.Im_Offset_seg[1,0]    = (self.Im_PatPosition_seg[1,0]-self.Im_PatPosition_seg[0,0])
                    self.Im_Offset_seg[1,1]    = (self.display_seg_data[0].shape[1]*self.pixel_spac_seg[0,0]-self.display_seg_data[1].shape[1]*self.pixel_spac_seg[1,0])-(self.Im_PatPosition_seg[1,1]-self.Im_PatPosition[0,1])
                    self.Im_Offset_seg[1,2]    = (self.Im_PatPosition_seg[1,2]-self.Im_PatPosition_seg[0,2])
                        
                    # check the current module                
                    self.slice_thick_seg[1]         = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['SliceThickness']
                    self.pixel_spac_seg[1, :2]      = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['PixelSpacing']
                    self.Im_PatPosition_seg[1, :3]  = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['ImagePositionPatient']

                self.curr_series_no = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['SeriesNumber']

                # Check if view needs to be initialized
                self.seg_curr_data = {"Orientation": self.segSelectView.currentText(), 
                                      "Dimensions": self.display_seg_data[0].shape,
                                      "SliceThickness": self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['SliceThickness'],
                                      "PixelSpacing": self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['PixelSpacing']}

                if self.seg_prev_data["Orientation"] is None:
                    self.seg_init_view = True
                else:
                    if self.seg_curr_data != self.seg_prev_data:
                        self.seg_init_view = True
                    else:
                        self.seg_init_view = False
                self.seg_prev_data = self.seg_curr_data

                # check the selected view
                if self.segSelectView.currentText() == "Axial":
                    self.im_ori_seg = 0
                    if self.seg_init_view == True:
                        self.current_seg_slice_index   = int(self.display_seg_data[0].shape[0]/2)
                        Ax_s = self.current_seg_slice_index
                        self.segViewSlider.setMaximum(self.display_seg_data[0].shape[0] - 1)
                        self.segViewSlider.setValue(int(Ax_s))   
                elif self.segSelectView.currentText() == "Sagittal":
                    self.im_ori_seg = 1
                    if self.seg_init_view == True:
                        self.current_seg_slice_index   = int(self.display_seg_data[0].shape[2]/2)
                        Ax_s = self.current_seg_slice_index
                        self.segViewSlider.setMaximum(self.display_seg_data[0].shape[2] - 1)  
                        self.segViewSlider.setValue(int(Ax_s))   
                elif self.segSelectView.currentText() == "Coronal":
                    self.im_ori_seg = 2
                    if self.seg_init_view == True:
                        self.current_seg_slice_index   = int(self.display_seg_data[0].shape[1]/2)
                        Ax_s = self.current_seg_slice_index
                        self.segViewSlider.setMaximum(self.display_seg_data[0].shape[1] - 1)  
                        self.segViewSlider.setValue(int(Ax_s))      
                #
                # Add ID 
                self.textActorSeg[0].SetInput(f"{self.modality} / {hierarchy[4]}")
                disp_seg_image_slice(self) 
                
                self.textActorSeg[1].SetInput(f"L: {round(Level,2)}  W: {round(Window,2)}")
                layer = self.layer_selection_box.currentIndex()

                if self.seg_init_view == True:
                    self.renSeg.ResetCamera()
                    self.renSeg.GetRenderWindow().Render() 
                    self.seg_init_view = False
                    self.zoom_scale = None
                    self.zoom_center = (None, None, None)
                    self.camera_pos = (None, None, None)

                if self.zoom_scale is not None:
                    renderer = self.renSeg.GetRenderWindow().GetRenderers().GetFirstRenderer()
                    camera = renderer.GetActiveCamera()
                    camera.SetParallelScale(self.zoom_scale)  # Smaller = more zoomed in
                    camera.SetFocalPoint(self.zoom_center)  # World-space center of zoom
                    camera.SetPosition(self.camera_pos)  # Also useful
                    renderer.ResetCameraClippingRange()
                    self.renSeg.GetRenderWindow().Render()
                #
            if currentTabText=='Plan':
                currentSubTabText = self.Plan_tabs.tabText(self.Plan_tabs.currentIndex())
                if currentSubTabText=='Material Assignment':
                    if len(hierarchy) == 5:
                        update_mat_struct_list(self)
                    
                
                
    elif hierarchy[0] == "IrIS_Cor":    
        # Extract hierarchy information based on the clicked index
        self.DataType = "IrIS_Cor"  
        # check the current module
        if currentTabText == "View":
            # need to remove part of the tag otherwise it does not match with the key:
            self.display_data[idx] = self.IrIS_corr[hierarchy[1]]['3DMatrix']
            adjust_data_type_input(self,idx)
            self.current_axial_slice_index[idx]    = 0
            self.current_sagittal_slice_index[idx] = 0
            self.current_coronal_slice_index[idx]  = 0
            # Accessing the values
            self.slice_thick[idx]         = 1
            self.pixel_spac[idx, :2]      = [1,1]
            self.Im_PatPosition[idx, :3]  = [0,0,0]
            #
            # # # Update the slider's value to match the current slice index
            self.AxialSlider.setValue(0)
            self.SagittalSlider.setValue(0)
            self.CoronalSlider.setValue(0)
            self.AxialSlider.setMaximum(0)
            self.SagittalSlider.setMaximum(0)
            self.CoronalSlider.setMaximum(0)   
            displayaxial(self)
            displaysagittal(self)
            displaycoronal(self)
            # You can now display this 3D matrix using VTK or any other method you prefer.
            self.renAxial.ResetCamera()
            self.renSagittal.ResetCamera()
            self.renCoronal.ResetCamera()
            #
            #update_metadata_table(self,self.IrIS_data[self.patientID])
            set_vtk_histogran_fig(self)   
            #
            self.vtkWidgetAxial.GetRenderWindow().Render()
            self.vtkWidgetSagittal.GetRenderWindow().Render()
            self.vtkWidgetCoronal.GetRenderWindow().Render()
            #
            #
    elif hierarchy[0] == "IrIS":    
        # Extract hierarchy information based on the clicked index
        self.DataType = "IrIS"  
        # check the current module
        self.patientID = hierarchy[1].replace("PatientID: ", "")
        if currentTabText == "View":
            # need to remove part of the tag otherwise it does not match with the key:
            self.display_data[idx] = self.IrIS_data[self.patientID]['3DMatrix']
            adjust_data_type_input(self,idx)
    
            self.current_axial_slice_index[idx]    = round(self.display_data[idx].shape[0]/2)
            self.current_sagittal_slice_index[idx] = round(self.display_data[idx].shape[1]/2)
            self.current_coronal_slice_index[idx]  = round(self.display_data[idx].shape[2]/2)
            # Accessing the values
            self.slice_thick[idx]         = 1
            self.pixel_spac[idx, :2]      = [1,1]
            self.Im_PatPosition[idx, :3]  = [0,0,0]
            #
            # # # Update the slider's value to match the current slice index
            self.AxialSlider.setValue(self.current_axial_slice_index[idx])
            self.SagittalSlider.setValue(self.current_sagittal_slice_index[idx])
            self.CoronalSlider.setValue(self.current_coronal_slice_index[idx])
            self.AxialSlider.setMaximum(self.display_data[idx].shape[0] - 1)
            self.SagittalSlider.setMaximum(self.display_data[idx].shape[2] - 1)
            self.CoronalSlider.setMaximum(self.display_data[idx].shape[1] - 1)
            #
            # 
            displayaxial(self)
            displaysagittal(self)
            displaycoronal(self)
            # You can now display this 3D matrix using VTK or any other method you prefer.
            self.renAxial.ResetCamera()
            self.renSagittal.ResetCamera()
            self.renCoronal.ResetCamera()
            #
            #update_metadata_table(self,self.IrIS_data[self.patientID])
            set_vtk_histogran_fig(self)   
            #
            self.vtkWidgetAxial.GetRenderWindow().Render()
            self.vtkWidgetSagittal.GetRenderWindow().Render()
            self.vtkWidgetCoronal.GetRenderWindow().Render()
            #
        elif currentTabText == "IrIS":
            self.Pk_find_channel.setValue(hierarchy_indices[1].row()+1)    
            self.display_data_IrIS_eval[idx] = self.IrIS_data[self.patientID]['3DMatrix']
            self.display_time_IrIS_eval[idx] = self.IrIS_data[self.patientID]['AcquisitionTime']
            adjust_data_type_input_IrIS_eval(self,idx)
            # Accessing the values
            self.slice_thick[idx]         = 1
            self.pixel_spac[idx, :2]      = [1,1]
            self.Im_PatPosition[idx, :3]  = [0,0,0]
            #
            # # # Update the slider's value to match the current slice index
            if self.List_Eval_Direction.currentText() == "XY":
                self.current_IrIS_eval_slice_index[idx]    = int(self.display_data_IrIS_eval[idx].shape[0]/2)
                self.Slider_Eval_IrIS.setMaximum(self.display_data_IrIS_eval[idx].shape[0] - 1)
                self.Slider_Eval_IrIS.setValue(int(self.current_IrIS_eval_slice_index[idx]))
                data = self.display_data_IrIS_eval[idx][int(self.current_IrIS_eval_slice_index[idx]), :, :].flatten()
            elif self.List_Eval_Direction.currentText() == "X-Time":
                self.current_IrIS_eval_slice_index[idx]    = int(self.display_data_IrIS_eval[idx].shape[2]/2)
                self.Slider_Eval_IrIS.setMaximum(self.display_data_IrIS_eval[idx].shape[2] - 1)
                self.Slider_Eval_IrIS.setValue(int(self.current_IrIS_eval_slice_index[idx]))
                data = self.display_data_IrIS_eval[idx][:,:,int(self.current_IrIS_eval_slice_index[idx])]
            elif self.List_Eval_Direction.currentText() == "Y-Time":
                self.current_IrIS_eval_slice_index[idx]    = int(self.display_data_IrIS_eval[idx].shape[1]/2) 
                self.Slider_Eval_IrIS.setMaximum(self.display_data_IrIS_eval[idx].shape[1] - 1)
                self.Slider_Eval_IrIS.setValue(int(self.current_IrIS_eval_slice_index[idx]))
                data = self.display_data_IrIS_eval[idx][:,int(self.current_IrIS_eval_slice_index[idx]),:]
            #
            Window = np.std(data)*3
            Level  = np.mean(data)
            set_window(self,Window,Level)  
            # You can now display this 3D matrix using VTK or any other method you prefer.
            self.renIrEval.ResetCamera()    
            self.vtkWidgetsIrEval.GetRenderWindow().Render()
        #     
        elif currentTabText == "Compare":
            # Current view
            Ax_idx = self.Comp_im_idx.value()
            if Ax_idx ==-1:
                QMessageBox.warning(None, "Warning", "Create the comparison axes first (bottom-right button)")
                return
            # layer
            #
            self.display_comp_data[Ax_idx, idx] = self.IrIS_data[self.patientID]['3DMatrix']
            adjust_data_type_comp_input(self,Ax_idx,idx)
            self.current_AxComp_slice_index[Ax_idx,idx]   = int(self.display_comp_data[Ax_idx, idx].shape[0]/2)
            
            # check the selected view

            if self.Comp_view_sel_box.currentText() == "Axial":
                self.im_ori_comp[Ax_idx] = 0
                self.current_AxComp_slice_index[Ax_idx,idx]   = int(self.display_comp_data[Ax_idx, idx].shape[0]/2)
                Ax_s = self.current_AxComp_slice_index[Ax_idx,idx]
                self.SliderCompareView.setMaximum(self.display_comp_data[Ax_idx, idx].shape[0] - 1)
                self.SliderCompareView.setValue(int(Ax_s))     
                # use data to set window level if IrIS
                data = self.display_comp_data[Ax_idx, idx][int(self.current_AxComp_slice_index[Ax_idx,idx]), :, :]
            elif self.Comp_view_sel_box.currentText() == "Sagittal":
                self.current_AxComp_slice_index[Ax_idx,idx]   = int(self.display_comp_data[Ax_idx, idx].shape[2]/2)
                self.im_ori_comp[Ax_idx] = 1
                Ax_s = self.current_AxComp_slice_index[Ax_idx,idx]
                self.SliderCompareView.setMaximum(self.display_comp_data[Ax_idx, idx].shape[2] - 1)
                self.SliderCompareView.setValue(int(Ax_s)) 
                data = self.display_comp_data[Ax_idx, idx][:,:,int(self.current_AxComp_slice_index[Ax_idx,idx])]
            elif self.Comp_view_sel_box.currentText() == "Coronal":
                self.current_AxComp_slice_index[Ax_idx,idx]   = int(self.display_comp_data[Ax_idx, idx].shape[1]/2)
                self.im_ori_comp[Ax_idx] = 2
                Ax_s = self.current_AxComp_slice_index[Ax_idx,idx]
                self.SliderCompareView.setMaximum(self.display_comp_data[Ax_idx, idx].shape[1] - 1)
                self.SliderCompareView.setValue(int(Ax_s))        
                data = self.display_comp_data[Ax_idx, idx][:,int(self.current_AxComp_slice_index[Ax_idx,idx]), :]
            #
            #
            # # Accessing the values
            self.slice_thick_comp[Ax_idx,idx]         = 1
            self.pixel_spac_comp[Ax_idx,idx, :2]      = 1
            self.Im_PatPosition_comp[Ax_idx,idx, :3]  = [1,1,1]
            #
            if idx>0:
                self.Im_Offset_comp[Ax_idx,idx,0]    = 0
                self.Im_Offset_comp[Ax_idx,idx,1]    = 0
                self.Im_Offset_comp[Ax_idx,idx,2]    = 0
            #
            # Add ID 
#            self.textActorAxCom[self.Comp_im_idx.value(),0].SetInput(f" IrIS / {hierarchy[4]}")
            disp_comp_image_slice(self) 
            #
            # use the slice data defined above to set the window level
            Window = np.std(data)*3
            Level  = np.mean(data)
            set_window(self,Window,Level)  
            self.textActorAxCom[Ax_idx,1].SetInput(f"L: {round(Level,2)}  W: {round(Window,2)}")
            for i in range (0,13):
                if not ((i, idx) in self.display_comp_data and int(self.current_AxComp_slice_index[i, idx]) in self.display_comp_data[i, idx]):
                    continue
                self.renAxComp[i].ResetCamera()
                self.renAxComp[i].GetRenderWindow().Render() 
            #
    #


      
    

def display_dicom_info(self):
    PatientName = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['DCM_Info'].get('PatientName','')
    PatientID   = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['DCM_Info'].get('PatientID','')
    Date        = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['DCM_Info'].get('AcquisitionDate','')
    KVP         = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['DCM_Info'].get('KVP','')
    
    self.textActorAxialInfo.SetInput(f"{PatientName} \n" 
                                     f"{PatientID}  \n"
                                     f"KVP {KVP}  {Date} ")
    
    
    self.textActorSagittalInfo.SetInput(f"{self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['StudyDescription']} \n"
                                        f"{self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['SeriesDescription']} \n"
                                        f"{self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['ImageComments']}")
    
    DoseType          = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['DCM_Info'].get('DoseType','')
    SumType           = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['DCM_Info'].get('SummationType','')
    DoseUnit          = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['DCM_Info'].get('DoseUnits','')
    TissueHetCorrect  = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['DCM_Info'].get('TissueHeterogeneityCorrection','')
    
    if DoseType != '':
     	self.textActorCoronalInfo.SetInput(f"DoseType {DoseType} \n" 
                                           f"SumType {SumType}  DoseUnit {DoseUnit} \n"
                                           f"TissueHetCorrect {TissueHetCorrect}")

def populate_CT4D_table(self):
    # Clear the table and set headers
    self.CT4D_table_display.clear()
    self.CT4D_table_display.setRowCount(0)
    self.CT4D_table_display.setColumnCount(4)
    self.CT4D_table_display.setHorizontalHeaderLabels(["View","Sequence", "Description","Index" ])
    
    # Initialize sequence ID
    sequence_id = 1

    # Reference acquisition number
    Ref_acq = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['AcquisitionNumber']
    
    # Loop through the data and populate the table
    for j in range(len(self.dicom_data[self.patientID][self.studyID][self.modality])):
        if Ref_acq == self.dicom_data[self.patientID][self.studyID][self.modality][j]['metadata']['AcquisitionNumber']:
            # Insert a new row
            row_position = self.CT4D_table_display.rowCount()
            self.CT4D_table_display.insertRow(row_position)
            
            # Create a checkbox widget for the first column
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.CT4D_table_display.setCellWidget(row_position, 0, checkbox_widget)
            
            # Set the sequence ID in the fourth column
            sequence_item = QTableWidgetItem(str(sequence_id))
            sequence_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)  # Make it editable
            self.CT4D_table_display.setItem(row_position, 1, sequence_item)
            
          
            # Set the series description in the third column
            series_description = self.dicom_data[self.patientID][self.studyID][self.modality][j]['metadata']['SeriesDescription']
            self.CT4D_table_display.setItem(row_position, 2, QTableWidgetItem(series_description))
            
            # Set the index in the second column
            self.CT4D_table_display.setItem(row_position, 3, QTableWidgetItem(str(j)))          

            # Increment the sequence ID for the next row
            sequence_id += 1

def update_axial_image(self,  Im = None):
    idx = self.layer_selection_box.currentIndex()
    #
    for i in range(len(self.dataImporterAxial)):
        # Add or update circular ROIs in the 4th layer
        if i == 3 and self.checkBox_circ_roi_data_2.isChecked():
            renderer = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()
            for actor in self.circle_actors_ax:
                renderer.RemoveActor(actor)
            self.circle_actors_ax.clear()
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
            #  Render to update
        #     

def update_coronal_image(self,  Im = None):
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

def update_sagittal_image(self,  Im = None):
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
            self.dataImporterSagittal[i].Modified() 
        #    
