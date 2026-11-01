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


def rtdose_tree_label(study_data, series_data):
    """Label of a dose in the data tree, with the name of its plan if it references a plan of the study."""
    meta = series_data['metadata']
    dose_label = meta.get('SeriesDescription') or meta.get('DoseSummationType') or 'Dose'
    ref_plan_uid = meta.get('ReferencedRTPlanSOPInstanceUID')
    plan_name = None
    if ref_plan_uid and 'RTPLAN' in study_data:
        for p in study_data['RTPLAN']:
            if p['metadata'].get('SOPInstanceUID') == ref_plan_uid:
                from fcn_RTFiles.amigo_rtplan import plan_display_name
                plan_name = plan_display_name(p['metadata'])  # (made in AMIGOpy: its full name)
                break
    if plan_name:
        return f"{dose_label} ({plan_name})_Series: {series_data['SeriesNumber']}"
    return f"{dose_label}_Series: {series_data['SeriesNumber']}"


def populate_medical_image_tree(self):
    # Remember currently active tabs so refreshing the tree never yanks the user away from their current workspace
    saved_tab_module = self.tabModules.currentIndex() if hasattr(self, 'tabModules') and self.tabModules is not None else None
    saved_tab_view = self.tabView01.currentIndex() if hasattr(self, 'tabView01') and self.tabView01 is not None else None
    saved_mc_tab = self.mc_tabs.currentIndex() if hasattr(self, 'mc_tabs') and self.mc_tabs is not None else None
    saved_plan_tab = self.Plan_tabs.currentIndex() if hasattr(self, 'Plan_tabs') and self.Plan_tabs is not None else None
    saved_view_plan_subtab = self.tabWidget_3.currentIndex() if hasattr(self, 'tabWidget_3') and self.tabWidget_3 is not None else None

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
                        if is_brachy:
                            # marked if made in AMIGOpy, not saved yet or changed since saved
                            from fcn_RTFiles.amigo_rtplan import plan_tree_label
                            series_label = plan_tree_label(series_data, type_tag)
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
                        series_label = rtdose_tree_label(study_data, series_data)
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
                        acq_plane = series_data['metadata'].get('AcquisitionPlane', 'AXIAL')
                        plane_tag = f" [{acq_plane.capitalize()}]" if acq_plane in ('CORONAL', 'SAGITTAL') and acq_plane.lower() not in series_desc.lower() else ""
                        if series_desc:
                            series_label = f"{series_desc}{plane_tag}_Series: {series_data['SeriesNumber']}"
                        else:
                            series_label = f"Acq_{Acq_number}{plane_tag}_Series: {series_data['SeriesNumber']}"
                        if LUT.get('LUTLabel', 'N/A') != 'N/A':
                            series_label += f" {LUT['LUTLabel']} {LUT['LUTExplanation']}"

                        series_item = QStandardItem(series_label)
                        modality_item.appendRow(series_item)

                        # If structures exist, add them as a sublevel
                        structures = series_data.get('structures')
                        if structures:
                            structures_names = series_data.get('structures_names')
                            if not structures_names:
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

                        #If MCNP lattice (universe) maps exist, add them as sublevels
                        lat_maps = series_data.get('mcnp_lattice_maps')
                        if lat_maps:
                            lat_parent_item = QStandardItem("MCNP lattice maps")
                            series_item.appendRow(lat_parent_item)
                            for name in lat_maps.keys():
                                lat_parent_item.appendRow(QStandardItem(name))
                                
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
    # Auto-click the current series if still present, else first series
    select_current_or_first_image_series(self)

    # Restore user's active tabs so tree refreshes never pull the user away to another tab
    if saved_tab_module is not None and hasattr(self, 'tabModules') and self.tabModules is not None:
        if self.tabModules.currentIndex() != saved_tab_module:
            self.tabModules.setCurrentIndex(saved_tab_module)
    if saved_tab_view is not None and hasattr(self, 'tabView01') and self.tabView01 is not None:
        if self.tabView01.currentIndex() != saved_tab_view:
            self.tabView01.setCurrentIndex(saved_tab_view)
    if saved_mc_tab is not None and hasattr(self, 'mc_tabs') and self.mc_tabs is not None:
        if self.mc_tabs.currentIndex() != saved_mc_tab:
            self.mc_tabs.setCurrentIndex(saved_mc_tab)
    if saved_plan_tab is not None and hasattr(self, 'Plan_tabs') and self.Plan_tabs is not None:
        if self.Plan_tabs.currentIndex() != saved_plan_tab:
            self.Plan_tabs.setCurrentIndex(saved_plan_tab)
    if saved_view_plan_subtab is not None and hasattr(self, 'tabWidget_3') and self.tabWidget_3 is not None:
        if self.tabWidget_3.currentIndex() != saved_view_plan_subtab:
            self.tabWidget_3.setCurrentIndex(saved_view_plan_subtab)

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

def find_tree_item(self, path):
    """Item of the data tree at a path of item texts from the top ("Medical Image", "PatientID: p", ...), or None."""
    model = getattr(self, 'model', None)
    if model is None:
        return None
    item = None
    for text in path:
        children = ([model.item(r) for r in range(model.rowCount())] if item is None
                    else [item.child(r) for r in range(item.rowCount())])
        item = next((child for child in children if child is not None and child.text() == text), None)
        if item is None:
            return None
    return item

def add_series_tree_item(self, patient_id, study_id, modality, index, label):
    """
    Item of a new series (series 'index', the last of its modality in the study) in the data
    tree, added to the tree as it is: rebuilding it would click the current series again (it is
    reloaded, the slices go back to the middle). If the tree does not match the data, it is
    rebuilt instead (None).
    """
    study_path = ("Medical Image", f"PatientID: {patient_id}", f"StudyID: {study_id}")
    study_item = find_tree_item(self, study_path)
    modality_item = find_tree_item(self, study_path + (f"Modality: {modality}",))
    if study_item is not None and modality_item is None:
        modality_item = QStandardItem(f"Modality: {modality}")
        study_item.appendRow(modality_item)
    if modality_item is None or modality_item.rowCount() != index:
        populate_medical_image_tree(self)
        return None
    item = QStandardItem(label)
    modality_item.appendRow(item)
    self.DataTreeView.expand(modality_item.index())
    return item

def select_current_or_first_image_series(self):
    model = self.DataTreeView.model()
    if not model:
        return

    cur_p = getattr(self, 'patientID', None)
    cur_s = getattr(self, 'studyID', None)
    cur_m = getattr(self, 'modality', None)
    cur_idx = getattr(self, 'series_index', None)

    # If cur_m is a non-image modality like RTPLAN, RTSTRUCT, or REG,
    # do NOT auto-trigger a click on it (which would switch tabs and views).
    # Instead, resolve the underlying image series in this study (preferring CT).
    if (
        cur_m in ("RTPLAN", "RTSTRUCT", "REG")
        and hasattr(self, 'medical_image')
        and cur_p in self.medical_image
    ):
        study_dict = self.medical_image.get(cur_p, {}).get(cur_s, {})
        if "CT" in study_dict and len(study_dict["CT"]) > 0:
            cur_m = "CT"
            cur_idx = 0
        else:
            for mod in study_dict.keys():
                if mod not in ("RTPLAN", "RTSTRUCT", "REG", "Operation") and len(study_dict[mod]) > 0:
                    cur_m = mod
                    cur_idx = 0
                    break

    if (
        cur_p is not None and cur_s is not None and cur_m is not None and cur_idx is not None
        and hasattr(self, 'medical_image') and cur_p in self.medical_image
    ):
        medical_image_item = None
        for i in range(model.rowCount()):
            item = model.item(i)
            if item and item.text() == "Medical Image":
                medical_image_item = item
                break
        if medical_image_item:
            for p_idx in range(medical_image_item.rowCount()):
                p_item = medical_image_item.child(p_idx)
                if not p_item or p_item.text().replace("PatientID: ", "") != str(cur_p):
                    continue
                for s_idx in range(p_item.rowCount()):
                    s_item = p_item.child(s_idx)
                    if not s_item or s_item.text().replace("StudyID: ", "") != str(cur_s):
                        continue
                    for m_idx in range(s_item.rowCount()):
                        m_item = s_item.child(m_idx)
                        if not m_item or m_item.text().replace("Modality: ", "") != str(cur_m):
                            continue
                        if cur_idx < m_item.rowCount():
                            ser_item = m_item.child(cur_idx)
                            if ser_item:
                                trigger_tree_click(self, ser_item.index())
                                return

    select_first_image_series(self)

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