import os
import numpy as np
from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox

# ------- helpers -------------------------------------------------
def get_save_path(parent: QWidget | None = None) -> str | None:
    """Show a Qt folder picker and return the selected directory (or None)."""
    folder = QFileDialog.getExistingDirectory(parent, "Select Folder")
    return folder or None

def warn(parent: QWidget | None, title: str, text: str) -> None:
    QMessageBox.warning(parent, title, text)

def error(parent: QWidget | None, title: str, text: str) -> None:
    QMessageBox.critical(parent, title, text)

# ------- IrIS ----------------------------------------------------
def export_np_array(self):
    """Export current IrIS 3D numpy array to AMBpy_export.npy in a chosen folder."""
    idx = self.layer_selected.currentIndex()
    if idx not in self.display_data_IrIS_eval or self.display_data_IrIS_eval[idx].size == 0:
        error(self, "Error",
              "This function requires an image set loaded in the IrIS module (not View mode).")
        return

    save_folder = get_save_path(self)
    if not save_folder:
        return

    array_to_save = self.display_data_IrIS_eval[idx]
    full_path = os.path.join(save_folder, "AMBpy_export.npy")
    try:
        np.save(full_path, array_to_save)
        QMessageBox.information(self, "Export complete", f"Saved:\n{full_path}")
    except Exception as e:
        error(self, "Save failed", f"Could not save file:\n{e}")

def export_dw_np(self):
    """Export dwell-window frame ranges for each channel to .npy files in a chosen folder."""
    directory = get_save_path(self)
    if not directory:
        return

    keys_list = list(self.IrIS_data.keys())
    margin = self.IrIsAVg_dw_margin.value()

    for i in range(len(self.Dw_pos_info)):
        ch = int(self.Dw_pos_info[i, 15]) - 1
        data = self.IrIS_data[keys_list[ch]]['3DMatrix']
        start_index = int(self.Dw_pos_info[i, 2]) + margin
        end_index   = int(self.Dw_pos_info[i, 3]) - margin

        if start_index < end_index:
            frames_slice = data[start_index:end_index]
            filename = f"chan_{ch+1}_dw_{i+1}.npy"
            filepath = os.path.join(directory, filename)
            try:
                np.save(filepath, frames_slice)
                print(f"Saved {filepath}")
            except Exception as e:
                print(f"Failed to save {filepath}: {e}")
        else:
            print(f"Skipping chan_{ch+1}, dw_{i+1} due to margin or invalid range.")

# ------- DICOM ---------------------------------------------------
def export_dcm_np_array(self):
    """Export current DICOM volume (current layer) as <series_idx>_export.npy."""
    save_folder = get_save_path(self)
    if not save_folder:
        return

    idx = self.layer_selected.currentIndex()
    array_to_save = self.display_data[idx]
    filename = f"{self.series_index + 1}_export.npy"
    full_path = os.path.join(save_folder, filename)

    try:
        np.save(full_path, array_to_save)
        QMessageBox.information(self, "Export complete", f"Saved:\n{full_path}")
    except Exception as e:
        error(self, "Save failed", f"Could not save file:\n{e}")
