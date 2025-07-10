from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt


def populate_stl_tree(self):
    # --- Ensure model exists ---
    if not hasattr(self, 'model') or self.model is None:
        self.model = QStandardItemModel()
        self.DataTreeView.setModel(self.model)
        self.model.setHorizontalHeaderLabels(['Data'])

    # --- Get/create parent "Surfaces" node ---
    stl_parent_item = _get_or_create_parent_item(self, "Surfaces")
    stl_parent_item.removeRows(0, stl_parent_item.rowCount())  # clear children

    # --- Add STL nodes ---
    if hasattr(self, "STL_data") and self.STL_data:
        for key, stl_info in self.STL_data.items():
            surface_item = QStandardItem(stl_info.get("name", key))
            surface_item.setToolTip(stl_info.get("", ""))
            surface_item.setData(key, Qt.UserRole)  # <-- store key for retrieval!
            stl_parent_item.appendRow(surface_item)

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