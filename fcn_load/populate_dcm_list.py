from PyQt5.QtGui import QStandardItemModel, QStandardItem


def populate_DICOM_tree(self):
    #self.dicom_data=load_all_dcm(folder_path=None, progress_callback=self.update_progress,update_label=self.label);
    # Create the data model for the tree view
    # Create the data model for the tree view if it doesn't exist
    if not hasattr(self, 'model') or self.model is None:
        self.model = QStandardItemModel()
        self.DataTreeView.setModel(self.model)
        self.model.setHorizontalHeaderLabels(['Data'])

    # Check for existing 'DICOM' parent item
    dicom_parent_item = _get_or_create_parent_item(self,'DICOM')
    #
    # Clear the clist of series menus for DECT
    self.DECT_list_01.clear()
    self.DECT_list_02.clear()
    self.scatter_plot_im_01.clear()
    self.scatter_plot_im_02.clear()
    # Dictionary to store series_label and related information
    self.series_info_dict = {}
    
    # Index for comboBox items
    combo_index = 0
    # Clear all children of the 'DICOM' parent item
    dicom_parent_item.removeRows(0, dicom_parent_item.rowCount())
    #
    # Populate tree view with DICOM data
    for patient_id, patient_data in self.dicom_data.items():
        patient_item = QStandardItem(f"PatientID: {patient_id}")
        dicom_parent_item.appendRow(patient_item)
        for study_id, study_data in patient_data.items():
            study_item = QStandardItem(f"StudyID: {study_id}")
            patient_item.appendRow(study_item)
            for modality, modality_data in study_data.items():
                modality_item = QStandardItem(f"Modality: {modality}")
                study_item.appendRow(modality_item)
                for item_index, series_data in enumerate(modality_data):  # Iterating over the list
                    if   modality == 'RTPLAN':
                        Plan_label = series_data['metadata']['RTPlanLabel']
                        series_label = f"{Plan_label}_Series: {series_data['SeriesNumber']}"
                        #
                        series_item = QStandardItem(series_label)
                        modality_item.appendRow(series_item)
                    elif modality == 'RTSTRUCT':
                        Struct_label = series_data['metadata']['StructureSetLabel']
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
                        Dose_label = series_data['metadata']['SeriesDescription']
                        series_label = f"{Dose_label}_Series: {series_data['SeriesNumber']}"
                        series_item = QStandardItem(series_label)
                        modality_item.appendRow(series_item)
                    else:
                        LUT = series_data['metadata']
                        Acq_number = series_data['metadata']['AcquisitionNumber']
                        series_label = f"Acq_{Acq_number}_Series: {series_data['SeriesNumber']}"
                        if LUT['LUTLabel'] != 'N/A':
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
                            
                            

                    # Add to comboBox
                    self.DECT_list_01.addItem(series_label)
                    self.DECT_list_02.addItem(series_label)
                    self.scatter_plot_im_01.addItem(series_label)
                    self.scatter_plot_im_02.addItem(series_label)

                    # Store information in the dictionary
                    self.series_info_dict[combo_index] = (series_label, patient_id, study_id, modality, item_index)
                    combo_index += 1
    # Expand all items in the tree view
    self.DataTreeView.expandAll()

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