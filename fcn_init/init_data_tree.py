from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QAction
from fcn_display.Data_tree_general import on_DataTreeView_clicked
from fcn_export.export_dcm import export_dicom_series
from fcn_load.populate_dcm_list import populate_DICOM_tree

def set_context_menu(self):
    """
    Set the context menu for the DataTreeView.
    This method connects the custom context menu request signal to the handler.
    """
    # Ensure the DataTreeView has a context menu policy set 
    self.DataTreeView.setContextMenuPolicy(Qt.CustomContextMenu)
    self.DataTreeView.customContextMenuRequested.connect(lambda pos: on_tree_context_menu(self,pos))



def on_tree_context_menu(self, pos):
    # Map the click into an index in the model
    idx = self.DataTreeView.indexAt(pos)
    if not idx.isValid():
        return

    # Get the corresponding QStandardItem, if you need it
    item = self.model.itemFromIndex(idx)
    print(item)

    model = self.DataTreeView.model()
    #
    # check file type
    # Extract hierarchy information based on the clicked index
    current_index = idx
    hierarchy = []
    hierarchy_indices = []
    while current_index.isValid():
        hierarchy.append(model.itemFromIndex(current_index).text())
        hierarchy_indices.append(current_index)
        current_index = current_index.parent()
    # Reverse the hierarchy data so it starts from the topmost level
    hierarchy.reverse()
    hierarchy_indices.reverse()

    # Print the hierarchy for debugging
    print("Hierarchy:", hierarchy)

    if len(hierarchy) >= 1:
        Type = "DICOM"
    if len(hierarchy) >= 2:
        Patient = hierarchy[1].replace("PatientID: ", "")
    if len(hierarchy) >= 3:
        Study = hierarchy[2].replace("StudyID: ", "")
    if len(hierarchy) >= 4:     
        Modality = hierarchy[3].replace("Modality: ", "")
    if len(hierarchy) >= 5:
        Series = hierarchy_indices[4].row()

    if Type == "DICOM" and len(hierarchy) == 5:
        # Build your menu
        menu = QMenu()
        open_action        = menu.addAction("Open…")
        exp_action_dcm     = menu.addAction("Export DCM")
        exp_action_np      = menu.addAction("Export NumPy")
        delete_action      = menu.addAction("Delete")
        
        # Pop up the menu at the global screen position
        action = menu.exec_(self.DataTreeView.viewport().mapToGlobal(pos))
        if action == open_action:
            print("Open action triggered")
            on_DataTreeView_clicked(self,idx)
   
        elif action == delete_action:
            print("Delete action triggered")
            delete_series(self, Patient, Study, Modality, Series)
            populate_DICOM_tree(self)
        elif action == exp_action_dcm:
            print("Export action triggered")
            meta_data   = self.dicom_data[Patient][Study][Modality][Series]['metadata']['DCM_Info']
            data        = self.dicom_data[Patient][Study][Modality][Series]['3DMatrix']
            slice_thick = self.dicom_data[Patient][Study][Modality][Series]['metadata']['SliceThickness']
            export_dicom_series(meta_data, data, slice_thick, output_folder=None)



def delete_series(self, Patient, Study, Modality, Series):
    """
    Deletes the series at index 'Series' (int) from self.dicom_data[Patient][Study][Modality] (a list).
    After deletion, recursively removes empty parent containers: Modality, Study, Patient.
    """
    # Step 1: Try to delete the series
    try:
        series_list = self.dicom_data[Patient][Study][Modality]
        del series_list[Series]
        print(f"Series at index {Series} deleted.")
    except (KeyError, IndexError):
        print(f"Series index {Series} not found for {Patient}, {Study}, {Modality}.")
        return

    # Step 2: If the list is empty, delete the Modality key from the dict
    if not series_list:
        del self.dicom_data[Patient][Study][Modality]
        print(f"Modality '{Modality}' deleted (was empty).")

        # Step 3: If Study dict is now empty, delete Study key
        if not self.dicom_data[Patient][Study]:
            del self.dicom_data[Patient][Study]
            print(f"Study '{Study}' deleted (was empty).")

            # Step 4: If Patient dict is now empty, delete Patient key
            if not self.dicom_data[Patient]:
                del self.dicom_data[Patient]
                print(f"Patient '{Patient}' deleted (was empty).")
