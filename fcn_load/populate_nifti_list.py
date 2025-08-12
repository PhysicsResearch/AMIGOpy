
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt


def populate_nifti_tree(self):
    # --- Ensure model exists ---
    if not hasattr(self, 'model') or self.model is None:
        self.model = QStandardItemModel()
        self.DataTreeView.setModel(self.model)
        self.model.setHorizontalHeaderLabels(['Data'])

    # --- Get/create parent "Nifti" node ---
    nifti_parent_item = _get_or_create_parent_item(self, "Nifti")
    nifti_parent_item.removeRows(0, nifti_parent_item.rowCount())  # clear children

    # --- Add STL nodes ---
    if hasattr(self, "nifti_data") and self.nifti_data:
        for nifti_info in self.nifti_data:
            key = nifti_info.get("SeriesNumber", "")
            nifti_item = QStandardItem(key)
            nifti_item.setToolTip(nifti_info.get("", ""))
            nifti_item.setData(key, Qt.UserRole)  # <-- store key for retrieval!
            nifti_parent_item.appendRow(nifti_item)

            # If structures exist, add them as a sublevel
            structures = nifti_info.get('structures')
            if structures:
                structures_names = [
                    structures[s_key].get('Name', s_key)
                    for s_key in structures.keys()
                ]
                if structures_names:
                    structures_parent_item = QStandardItem("Structures")
                    nifti_item.appendRow(structures_parent_item)
                    for name in structures_names:
                        structure_item = QStandardItem(name)
                        structures_parent_item.appendRow(structure_item)

    # --- Expand all ---
    self.DataTreeView.expandAll()



def _get_or_create_parent_item(self, label):
    if not hasattr(self, 'model') or self.model is None:
        print("Error: Model is not initialized.")
        return None

    # Search for existing parent
    for i in range(self.model.rowCount()):
        item = self.model.item(i)
        if item and item.text() == label:
            return item

    # Create new parent if not found
    new_item = QStandardItem(label)
    self.model.appendRow(new_item)
    return new_item