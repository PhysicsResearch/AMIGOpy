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
    QPushButton,
    QLabel
)

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
    # Handle multi-value or common Python collections
    if isinstance(value, MultiValue) or isinstance(value, (list, tuple, set)):
        length = len(value)
        if length == 0:
            return ""
        elif length <= 20:
            return ', '.join(str(v) for v in value)
        else:
            truncated_values = ', '.join(str(v) for v in value[:20])
            return f"{truncated_values}, ... (showing {length} total)"
    
    # Handle strings
    elif isinstance(value, str):
        if len(value) < 100:
            return value
        else:
            return f"Length: {len(value)}, Type: str"
    
    # Handle simple numeric types
    elif isinstance(value, (int, float)):
        return str(value)
    
    # Handle all other types
    else:
        return f"Type: {type(value).__name__}"

# ------------------------------------------------------------
# 2) Search matching check: partial, case-insensitive
# ------------------------------------------------------------
def _matches_search(elem, value_string, search_text):
    """
    Check if 'search_text' is found in either:
      - The element's name (e.g. 'ROIContourSequence')
      - The element's tag (e.g. '(3006, 0020)')
      - The text of 'value_string'
    Returns True if there's a match, False otherwise.
    """
    if not search_text:
        return True  # Empty search => everything matches

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
#    but only if they match (or their children match).
# ------------------------------------------------------------
def _add_dataset_items_to_tree_filtered(ds, parent_item, tree_widget, search_text):
    """
    Recursively add each DataElement in dataset 'ds' to the QTreeWidget
    if it or its children match the search text.
    
    Returns True if at least one match in this dataset's subtree,
    otherwise False.
    """
    any_match_in_ds = False

    for elem in ds:
        label = f"{elem.name} (Tag {elem.tag})"

        if elem.VR == "SQ":
            # It's a Sequence
            sequence = elem.value
            if not isinstance(sequence, Sequence):
                # Unexpected type, handle gracefully
                value_str = f"Unexpected type: {type(sequence).__name__}"
                if _matches_search(elem, value_str, search_text):
                    seq_item = QTreeWidgetItem([label, value_str])
                    if parent_item is None:
                        tree_widget.addTopLevelItem(seq_item)
                    else:
                        parent_item.addChild(seq_item)
                    any_match_in_ds = True
                continue

            # Normal Sequence
            seq_item = QTreeWidgetItem([label, "Sequence"])
            any_match_in_seq = False

            if len(sequence) == 0:
                # empty sequence
                if _matches_search(elem, "(empty sequence)", search_text):
                    if parent_item is None:
                        tree_widget.addTopLevelItem(seq_item)
                    else:
                        parent_item.addChild(seq_item)
                    QTreeWidgetItem(seq_item, ["(empty)"])
                    any_match_in_seq = True
            else:
                for i, item_ds in enumerate(sequence):
                    item_label = f"Item[{i}]"
                    item_node = QTreeWidgetItem([item_label, "Dataset"])

                    if isinstance(item_ds, Dataset):
                        sub_matched = _add_dataset_items_to_tree_filtered(
                            item_ds, item_node, tree_widget, search_text
                        )
                        if sub_matched:
                            # Only add item_node if there's a match below
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
                # If anything matched inside the sequence => add seq_item
                if parent_item is None:
                    tree_widget.addTopLevelItem(seq_item)
                else:
                    parent_item.addChild(seq_item)
                any_match_in_ds = True

        else:
            # Normal (non-sequence) DataElement
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
# 4) The main function to update your QTreeWidget 
#    (called 'MetaViewTable') with the DICOM structure,
#    filtering by search text if provided.
# ------------------------------------------------------------
def update_meta_view_table_dicom(self,ds, search_text=""):
    """
    Build the QTreeWidget (self.MetaViewTable) from ds.
    If 'search_text' is non-empty, filter elements that don't match.
    """
    if not ds:
        return  # No DICOM loaded

    self.MetaViewTable.clear()
    self.MetaViewTable.setColumnCount(2)
    self.MetaViewTable.setHeaderLabels(["Element", "Value / Subitems"])

    # Recursively add the matching items
    _add_dataset_items_to_tree_filtered(
        ds, parent_item=None,
        tree_widget=self.MetaViewTable,
        search_text=search_text
    )


def on_metadata_search_text_changed(self, text):
    if self.patientID is None:
        return

    try:
        md = self.dicom_data[self.patientID][self.studyID][self.modality_metadata][self.series_index]['metadata']
    except Exception:
        # If the path is invalid, just clear table and return
        self.MetaViewTable.clear()
        self.MetaViewTable.setColumnCount(2)
        self.MetaViewTable.setHeaderLabels(["Element", "Value / Subitems"])
        return

    dcm_info = md.get('DCM_Info', None)

    # 1) Prefer DICOM header if available
    if isinstance(dcm_info, Dataset):
        update_meta_view_table_dicom(self, dcm_info, text)
        return

    # 2) Otherwise try NIfTI header
    nifti_meta = md.get('Nifiti_info', None)
    if isinstance(nifti_meta, dict) and len(nifti_meta) > 0:
        update_meta_view_table_nifti(self, nifti_meta, text)
        return

    # 3) Neither available -> clear and return
    self.MetaViewTable.clear()
    self.MetaViewTable.setColumnCount(2)
    self.MetaViewTable.setHeaderLabels(["Element", "Value / Subitems"])
    return


# ------------------------------------------------------------
# Render NIfTI (SimpleITK) key/value metadata dict
# ------------------------------------------------------------
def update_meta_view_table_nifti(self, meta_dict: dict, search_text: str = ""):
    """
    Build the QTreeWidget (self.MetaViewTable) from a NIfTI meta dict (key->str).
    Supports case-insensitive filtering on key or value.
    """
    self.MetaViewTable.clear()
    self.MetaViewTable.setColumnCount(2)
    self.MetaViewTable.setHeaderLabels(["Key", "Value"])

    if not meta_dict:
        return

    s = (search_text or "").lower().strip()

    # Sort keys for stable view
    for k in sorted(meta_dict.keys()):
        v = meta_dict.get(k, "")
        k_str = str(k)
        v_str = _process_scalar(v)  # reuses your scalar shortener (ok for strings)

        if s:
            if s not in k_str.lower() and s not in str(v).lower():
                continue

        self.MetaViewTable.addTopLevelItem(QTreeWidgetItem([k_str, v_str]))


