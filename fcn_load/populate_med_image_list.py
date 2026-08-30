from PySide6.QtGui import QStandardItemModel, QStandardItem

def populate_image(self):
    """
    Populate a top level 'Image' branch using self.image.

    self.image is expected to be a list of series dictionaries:
        {
            'SeriesNumber': ...,
            'metadata': {
                'SeriesDescription': <file name>,
                'DataType': 'TIFF' or 'PNG' or ...
                ...
            },
            '3DMatrix': numpy array
        }
    Tree structure:

        Data
            Medical Image
                ...
            Image
                <file name 1>
                <file name 2>
                ...
    """

    # If there is no image data, nothing to do
    if not hasattr(self, 'image') or not isinstance(self.image, list) or not self.image:
        return

    # Ensure model exists
    if not hasattr(self, 'model') or self.model is None:
        self.model = QStandardItemModel()
        self.DataTreeView.setModel(self.model)
        self.model.setHorizontalHeaderLabels(['Data'])

    # Get or create top level "Image" item
    image_root = _get_or_create_parent_item(self, 'Image')
    if image_root is None:
        return

    # Clear previous children
    image_root.removeRows(0, image_root.rowCount())

    # Fill with one row per image
    for series in self.image:
        meta = series.get('metadata', {})
        filename = meta.get('SeriesDescription') or series.get('SeriesNumber') or "Image"
        data_type = meta.get('DataType', '')

        # Label: "filename" (optionally with type)
        label = filename

        item = QStandardItem(label)
        image_root.appendRow(item)

        # Tooltip with type, size and path
        size = meta.get('Size')
        path = meta.get('OriginalFilePath', '')
        tooltip_bits = []
        if data_type:
            tooltip_bits.append(f"type={data_type}")
        if size is not None:
            tooltip_bits.append(f"size={size}")
        if path:
            tooltip_bits.append(path)
        if tooltip_bits:
            item.setToolTip(" | ".join(tooltip_bits))

        # Optionally store the full series for later lookup
        # from PySide6.QtCore import Qt
        # item.setData(series, Qt.UserRole)

    # Expand everything so the us
    # er sees the new branch
    self.DataTreeView.expandAll()


def populate_medical_image_tree(self):
    #self.medical_image=load_all_dcm(folder_path=None, progress_callback=self.update_progress,update_label=self.label);
    # Create the data model for the tree view
    # Create the data model for the tree view if it doesn't exist
    if not hasattr(self, 'model') or self.model is None:
        self.model = QStandardItemModel()
        self.DataTreeView.setModel(self.model)
        self.model.setHorizontalHeaderLabels(['Data'])

    # Check for existing 'DICOM' parent item
    dicom_parent_item = _get_or_create_parent_item(self,'Medical Image')
    #
    # Clear the list of series menus for DECT (if DECT tab is created)
    for attr in ('DECT_list_01', 'DECT_list_02', 'scatter_plot_im_01', 'scatter_plot_im_02'):
        w = getattr(self, attr, None)
        if w is not None and hasattr(w, 'clear'):
            w.clear()
    # self.Reg_target_box.clear()
    # self.Reg_moving_box.clear()
    # Dictionary to store series_label and related information
    self.series_info_dict = {}
    
    # Index for comboBox items
    combo_index = 0
    # Clear all children of the 'DICOM' parent item
    dicom_parent_item.removeRows(0, dicom_parent_item.rowCount())
    #
    # Populate tree view with DICOM data
    for patient_id, patient_data in self.medical_image.items():
        patient_item = QStandardItem(f"PatientID: {patient_id}")
        dicom_parent_item.appendRow(patient_item)
        for study_id, study_data in patient_data.items():
            study_item = QStandardItem(f"StudyID: {study_id}")
            patient_item.appendRow(study_item)
            for modality, modality_data in study_data.items():
                modality_item = QStandardItem(f"Modality: {modality}")
                study_item.appendRow(modality_item)
                for item_index, series_data in enumerate(modality_data):  # Iterating over the list
                    if modality == 'RTPLAN':
                        Plan_label = series_data['metadata'].get('RTPlanLabel') or series_data['metadata'].get('RTPlanName') or 'Plan'
                        meta = series_data.get('metadata', {})
                        dcm_info = meta.get('DCM_Info', None)
                        is_brachy = (
                            'Plan_Brachy_Channels' in meta or
                            meta.get('BrachyTreatmentType', 'N/A') not in ['N/A', '', None] or
                            meta.get('BrachyPlan') is True or
                            (dcm_info is not None and hasattr(dcm_info, 'ApplicationSetupSequence') and len(getattr(dcm_info, 'ApplicationSetupSequence', [])) > 0)
                        )
                        has_beams = (
                            (dcm_info is not None and (
                                (hasattr(dcm_info, 'BeamSequence') and len(getattr(dcm_info, 'BeamSequence', [])) > 0) or
                                (hasattr(dcm_info, 'IonBeamSequence') and len(getattr(dcm_info, 'IonBeamSequence', [])) > 0)
                            )) or
                            meta.get('TreatmentProtocols', 'N/A') not in ['N/A', '', None]
                        )
                        if is_brachy:
                            type_tag = "[Brachy]"
                        elif has_beams:
                            type_tag = "[EBRT]"
                        else:
                            type_tag = "[Plan]"

                        series_label = f"{type_tag} {Plan_label}_Series: {series_data['SeriesNumber']}"
                        series_item = QStandardItem(series_label)
                        modality_item.appendRow(series_item)
                    elif modality == 'RTSTRUCT':
                        Struct_label = series_data['metadata'].get('StructureSetLabel') or series_data['metadata'].get('StructureSetName') or 'Struct'
                        struct_date = series_data['metadata'].get('StructureSetDate')
                        if struct_date and struct_date != 'N/A':
                            series_label = f"{Struct_label} ({struct_date})_Series: {series_data['SeriesNumber']}"
                        else:
                            series_label = f"{Struct_label}_Series: {series_data['SeriesNumber']}"
                        series_item = QStandardItem(series_label)
                        modality_item.appendRow(series_item)
                        # If structures exist, add them as a sublevel
                        structures_names = series_data.get('structures_names')
                        if structures_names:
                            structures_parent_item = QStandardItem("Structures")
                            series_item.appendRow(structures_parent_item)
                            for name in structures_names:
                                structure_item = QStandardItem(name)
                                structures_parent_item.appendRow(structure_item)

                    elif modality == 'RTDOSE':
                        Dose_label = series_data['metadata'].get('SeriesDescription') or series_data['metadata'].get('DoseSummationType') or 'Dose'
                        ref_plan_uid = series_data['metadata'].get('ReferencedRTPlanSOPInstanceUID')
                        plan_name = None
                        if ref_plan_uid and 'RTPLAN' in study_data:
                            for p in study_data['RTPLAN']:
                                if p['metadata'].get('SOPInstanceUID') == ref_plan_uid:
                                    plan_name = p['metadata'].get('RTPlanLabel') or p['metadata'].get('RTPlanName')
                                    break
                        if plan_name:
                            series_label = f"{Dose_label} ({plan_name})_Series: {series_data['SeriesNumber']}"
                        else:
                            series_label = f"{Dose_label}_Series: {series_data['SeriesNumber']}"
                        series_item = QStandardItem(series_label)
                        modality_item.appendRow(series_item)
                    elif modality == 'REG':
                        reg_label = series_data['metadata'].get('ContentLabel') or series_data['metadata'].get('SeriesDescription') or 'Registration'
                        series_label = f"{reg_label}_Series: {series_data['SeriesNumber']}"
                        series_item = QStandardItem(series_label)
                        mat_list = series_data['metadata'].get('RegistrationMatrixList', [])
                        if mat_list:
                            tt = f"Registration ({len(mat_list)} matrices)\n"
                            for m_idx, m_info in enumerate(mat_list):
                                tt += f"Matrix {m_idx+1}: Type={m_info.get('MatrixType')} -> TargetFoR={m_info.get('TargetFrameOfReferenceUID')[:20]}...\n"
                            series_item.setToolTip(tt.strip())
                        modality_item.appendRow(series_item)
                    elif modality == 'Operation':
                        Op_label = series_data['metadata'].get('SeriesDescription', 'Operation')
                        series_label = f"{Op_label}_Series: {series_data['SeriesNumber']}"
                        series_item = QStandardItem(series_label)
                        modality_item.appendRow(series_item)
                    else:
                        LUT = series_data['metadata']
                        Acq_number = series_data['metadata'].get('AcquisitionNumber', 'N/A')
                        series_desc = series_data['metadata'].get('SeriesDescription', '')
                        if series_desc:
                            series_label = f"{series_desc}_Series: {series_data['SeriesNumber']}"
                        else:
                            series_label = f"Acq_{Acq_number}_Series: {series_data['SeriesNumber']}"
                        if LUT.get('LUTLabel', 'N/A') != 'N/A':
                            series_label += f" {LUT['LUTLabel']} {LUT['LUTExplanation']}"

                        series_item = QStandardItem(series_label)
                        modality_item.appendRow(series_item)

                        # If structures exist, add them as a sublevel
                        structures = series_data.get('structures')
                        if structures:
                            structures_names = [
                                structures[s_key].get('Name', s_key)
                                for s_key in structures.keys()
                            ]
                            if structures_names:
                                structures_parent_item = QStandardItem("Structures")
                                series_item.appendRow(structures_parent_item)
                                for name in structures_names:
                                    structure_item = QStandardItem(name)
                                    structures_parent_item.appendRow(structure_item)
                    
                        #If density maps exists, add them as sublevels
                        density_maps = series_data.get('density_maps')
                        if density_maps:
                            density_maps_names=density_maps.keys()
                            if density_maps_names:
                                density_parent_item = QStandardItem("Density maps")
                                series_item.appendRow(density_parent_item)
                                for name in density_maps_names:
                                    density_item = QStandardItem(name)
                                    density_parent_item.appendRow(density_item)
                                    
                         #If material maps exists, add them as sublevels
                        mat_maps = series_data.get('mat_maps')
                        if mat_maps:
                            mat_maps_names=mat_maps.keys()
                            if mat_maps_names:
                                mat_parent_item = QStandardItem("Material maps")
                                series_item.appendRow(mat_parent_item)
                                for name in mat_maps_names:
                                    mat_item = QStandardItem(name)
                                    mat_parent_item.appendRow(mat_item)
                                
                        #If ab map exists, add it as sublevel
                        ab_matrix = series_data.get('ab_matrix',[])
                        if len(ab_matrix):
                            ab_parent_item = QStandardItem("α/β")
                            series_item.appendRow(ab_parent_item)
                            
                            

                    # Add to comboBox (if DECT tab is created)
                    for attr in ('DECT_list_01', 'DECT_list_02', 'scatter_plot_im_01', 'scatter_plot_im_02'):
                        w = getattr(self, attr, None)
                        if w is not None and hasattr(w, 'addItem'):
                            w.addItem(series_label)
                    # self.Reg_target_box.addItem(series_label)
                    # self.Reg_moving_box.addItem(series_label)

                    # Store information in the dictionary
                    self.series_info_dict[combo_index] = (series_label, patient_id, study_id, modality, item_index)
                    combo_index += 1
    # Expand all items in the tree view
    self.DataTreeView.expandAll()
    # Auto-click the first image series
    select_first_image_series(self)

def _get_or_create_parent_item(self, label):
    # Check if model is None
    if self.model is None:
        print("Error: Model is not initialized.")
        return None

    # Iterate through existing items to find if the parent item already exists
    for i in range(self.model.rowCount()):
        item = self.model.item(i)
        if item and item.text() == label:
            return item

    # Create a new parent item if it doesn't exist
    new_item = QStandardItem(label)
    self.model.appendRow(new_item)
    return new_item    

def select_first_image_series(self):
    model = self.DataTreeView.model()
    if not model:
        return
        
    first_fallback_index = None
    
    # 0. Find "Medical Image" parent
    medical_image_item = None
    for i in range(model.rowCount()):
        item = model.item(i)
        if item and item.text() == "Medical Image":
            medical_image_item = item
            break
            
    if not medical_image_item:
        return
        
    # Let's traverse patient -> study -> modality -> series
    for p_idx in range(medical_image_item.rowCount()):
        patient_item = medical_image_item.child(p_idx)
        if not patient_item: continue
        for s_idx in range(patient_item.rowCount()):
            study_item = patient_item.child(s_idx)
            if not study_item: continue
            for m_idx in range(study_item.rowCount()):
                modality_item = study_item.child(m_idx)
                if not modality_item: continue
                modality = modality_item.text().replace("Modality: ", "")
                
                # Iterate over series items
                for ser_idx in range(modality_item.rowCount()):
                    series_item = modality_item.child(ser_idx)
                    if not series_item: continue
                    
                    index = series_item.index()
                    if modality not in ("RTPLAN", "RTSTRUCT", "REG"):
                        trigger_tree_click(self, index)
                        return
                    elif first_fallback_index is None:
                        first_fallback_index = index

    if first_fallback_index is not None:
        trigger_tree_click(self, first_fallback_index)

def trigger_tree_click(self, index):
    from PySide6.QtCore import QItemSelectionModel
    from fcn_display.Data_tree_general import on_DataTreeView_clicked
    self.DataTreeView.selectionModel().clearSelection()
    self.DataTreeView.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
    self.DataTreeView.scrollTo(index)
    on_DataTreeView_clicked(self, index)