import sys
import os
import pydicom
from pydicom.dataset import Dataset
from pydicom.sequence import Sequence
from pydicom.multival import MultiValue

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTreeWidget,
    QTreeWidgetItem,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox
)
from PyQt5.QtCore import Qt

# ------------------------------------------------------------
# 1) Helper function to convert scalar values into short strings
# ------------------------------------------------------------
def _process_scalar(value):
    """
    Convert a scalar (non-sequence) value to a readable string.
    - For pydicom.multival.MultiValue, lists, tuples, sets:
      show only the first 20 items, then '... (showing X total)' if more than 20.
    - For strings, show up to 100 chars, then summary if longer.
    - For int/float, return the string version.
    - For other types, return 'Type: <typename>'.
    """
    if isinstance(value, MultiValue) or isinstance(value, (list, tuple, set)):
        length = len(value)
        if length == 0:
            return ""
        elif length <= 20:
            return ", ".join(str(v) for v in value)
        else:
            truncated = ", ".join(str(v) for v in value[:20])
            return f"{truncated}, ... (showing {length} total)"
    elif isinstance(value, str):
        if len(value) < 100:
            return value
        else:
            return f"Length: {len(value)}, Type: str"
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        return f"Type: {type(value).__name__}"

# ------------------------------------------------------------
# 2) Search matching check: partial, case-insensitive
# ------------------------------------------------------------
def _matches_search(elem, value_string, search_text):
    """
    Check if 'search_text' is found in either:
      - The element's name (e.g. 'PatientName')
      - The element's tag (e.g. '(0010,0010)')
      - The text of 'value_string'
    Returns True if there's a match, False otherwise.
    """
    if not search_text:
        return True

    lower_search = search_text.lower()
    name_str = elem.name.lower()
    tag_str = str(elem.tag).lower()
    val_str = (value_string or "").lower()

    return (
        lower_search in name_str
        or lower_search in tag_str
        or lower_search in val_str
    )

# ------------------------------------------------------------
# 3) Recursive function that adds DICOM items to a QTreeWidget,
#    but only if they (or their children) match the search text.
# ------------------------------------------------------------
def _add_dataset_items_to_tree_filtered(ds: Dataset, parent_item: QTreeWidgetItem,
                                        tree_widget: QTreeWidget, search_text: str) -> bool:
    """
    Recursively add each DataElement in dataset 'ds' to the QTreeWidget
    if it or its children match the search text.
    Returns True if at least one match in this dataset's subtree, otherwise False.
    """
    any_match_in_ds = False

    for elem in ds:
        # Build a label like: "PatientName  (Tag (0010,0010))"
        label = f"{elem.name}  (Tag {elem.tag})"

        # If this is a Sequence (VR == "SQ"), dive in recursively
        if elem.VR == "SQ":
            sequence = elem.value
            if not isinstance(sequence, Sequence):
                # Unexpected type: treat as scalar
                value_str = f"Unexpected type: {type(sequence).__name__}"
                if _matches_search(elem, value_str, search_text):
                    seq_item = QTreeWidgetItem([label, value_str])
                    if parent_item is None:
                        tree_widget.addTopLevelItem(seq_item)
                    else:
                        parent_item.addChild(seq_item)
                    any_match_in_ds = True
                continue

            # Normal Sequence handling
            seq_item = QTreeWidgetItem([label, "Sequence"])
            any_match_in_seq = False

            if len(sequence) == 0:
                # Empty Sequence
                if _matches_search(elem, "(empty sequence)", search_text):
                    if parent_item is None:
                        tree_widget.addTopLevelItem(seq_item)
                    else:
                        parent_item.addChild(seq_item)
                    empty_child = QTreeWidgetItem(["(empty)", ""])
                    seq_item.addChild(empty_child)
                    any_match_in_seq = True
            else:
                # Iterate over each item in the Sequence
                for i, item_ds in enumerate(sequence):
                    item_label = f"Item [{i}]"
                    item_node = QTreeWidgetItem([item_label, "Dataset"])
                    if isinstance(item_ds, Dataset):
                        sub_matched = _add_dataset_items_to_tree_filtered(
                            item_ds, item_node, tree_widget, search_text
                        )
                        if sub_matched:
                            seq_item.addChild(item_node)
                            any_match_in_seq = True
                    else:
                        # Rare: item isn't a Dataset => treat as scalar
                        val_str = _process_scalar(item_ds)
                        if _matches_search(elem, val_str, search_text):
                            sub_item = QTreeWidgetItem([item_label, val_str])
                            seq_item.addChild(sub_item)
                            any_match_in_seq = True

            if any_match_in_seq:
                if parent_item is None:
                    tree_widget.addTopLevelItem(seq_item)
                else:
                    parent_item.addChild(seq_item)
                any_match_in_ds = True

        else:
            # Non-sequence DataElement
            val_str = _process_scalar(elem.value)
            if _matches_search(elem, val_str, search_text):
                data_item = QTreeWidgetItem([label, val_str])
                if parent_item is None:
                    tree_widget.addTopLevelItem(data_item)
                else:
                    parent_item.addChild(data_item)
                any_match_in_ds = True

    return any_match_in_ds

# ------------------------------------------------------------
# 4) Populate the QTreeWidget (self.MetaViewTable) from a Dataset
# ------------------------------------------------------------
def update_meta_view_table_dicom(self, ds: Dataset, search_text: str = ""):
    """
    Build the QTreeWidget (self.MetaViewTable) from 'ds'.
    If 'search_text' is non-empty, filter elements that don't match.
    """
    if ds is None:
        return

    self.MetaViewTable.clear()
    self.MetaViewTable.setColumnCount(2)
    self.MetaViewTable.setHeaderLabels(["Element", "Value / Subitems"])

    # Recursively add matching items
    _add_dataset_items_to_tree_filtered(
        ds,
        parent_item=None,
        tree_widget=self.MetaViewTable,
        search_text=search_text
    )
    self.MetaViewTable.expandAll()

# ------------------------------------------------------------
# 5) Callback for search box text changes
# ------------------------------------------------------------
def on_metadata_search_text_changed(self, text: str):
    if self.dicom_dataset is not None:
        update_meta_view_table_dicom(
            self,
            self.dicom_dataset,
            search_text=text
        )

# ------------------------------------------------------------
# 6) The main Viewer window
# ------------------------------------------------------------
class DicomHeadersViewer(QMainWindow):
    def __init__(self, dicom_path: str = None):
        super().__init__()
        self.setWindowTitle("DICOM Headers Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.dicom_dataset = None  # Will hold the pydicom.Dataset once loaded

        # ─── Search box ─────────────────────────────────────
        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Search tags or values…")
        # Bind to update function whenever the user types
        self.search_box.textChanged.connect(
            lambda txt: on_metadata_search_text_changed(self, txt)
        )

        # ─── Tree widget for DICOM metadata ───────────────
        self.MetaViewTable = QTreeWidget(self)
        self.MetaViewTable.setColumnCount(2)
        self.MetaViewTable.setHeaderLabels(["Element", "Value / Subitems"])
        self.MetaViewTable.header().setStretchLastSection(True)

        # ─── Layout ───────────────────────────────────────
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.search_box)
        main_layout.addWidget(self.MetaViewTable)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # If a valid path was passed, load it; otherwise, show file dialog
        if dicom_path and os.path.isfile(dicom_path):
            self.load_and_display(dicom_path)
        else:
            self.load_dicom_file_dialog()

    def load_dicom_file_dialog(self):
        """
        Opens a QFileDialog so the user can choose a DICOM file manually.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open DICOM File",
            "",
            "DICOM Files (*.dcm *.ima);;All Files (*)",
            options=options
        )
        if file_path:
            self.load_and_display(file_path)
        else:
            # If the user cancels, just close this window
            self.close()

    def load_and_display(self, dicom_file_path: str):
        """
        Attempt to read the DICOM dataset (without pixel data),
        then populate the tree.
        """
        try:
            ds = pydicom.dcmread(dicom_file_path, stop_before_pixels=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read DICOM:\n{e}")
            self.close()
            return

        self.dicom_dataset = ds
        # Clear any old search text
        self.search_box.clear()
        # Populate tree with all tags
        update_meta_view_table_dicom(self, ds, search_text="")

# ───────────────────────────────────────────────────────────────────────
# 7) Module-level viewer instance & open function
# ───────────────────────────────────────────────────────────────────────
_viewer_instance: DicomHeadersViewer = None

def open_dicom_tag_viewer(dicom_path: str = None):
    """
    Opens (or reuses) a DicomHeadersViewer window.
    - If already open, it is raised/focused. If 'dicom_path' is provided
      and refers to an existing file, it will reload that file in the same window.
    - If not already open, creates a new window. If dicom_path is None,
      user is prompted with a QFileDialog.
    """
    global _viewer_instance

    # If already exists and visible, just raise & reload if needed
    if _viewer_instance is not None and _viewer_instance.isVisible():
        _viewer_instance.activateWindow()
        _viewer_instance.raise_()
        if dicom_path and os.path.isfile(dicom_path):
            _viewer_instance.load_and_display(dicom_path)
        return

    # Otherwise, create a new one
    _viewer_instance = DicomHeadersViewer(dicom_path)
    _viewer_instance.show()

# ───────────────────────────────────────────────────────────────────────
# 8) If run standalone (purely for testing)
# ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # If a file path is passed on the command line, use it
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        open_dicom_tag_viewer(sys.argv[1])
    else:
        open_dicom_tag_viewer()
    # Note: If this module is imported into a larger PyQt app, 
    #       the above block won't run. Instead, call open_dicom_viewer(...) 
    #       from your code.
