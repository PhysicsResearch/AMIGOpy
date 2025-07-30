import numpy as np
import pydicom
from pydicom.dataset import FileDataset
from pydicom.uid import generate_uid
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QFileDialog, QApplication
import sys
import os

def export_dicom_series(meta_data, data, slice_thick, output_folder=None):
    if output_folder is None:
        app = QApplication.instance() or QApplication(sys.argv)
        output_folder = QFileDialog.getExistingDirectory(None, "Select Output Folder")
        if not output_folder:
            print("No folder selected. Operation cancelled.")
            return

    num_slices = data.shape[0]

    ipp = np.array(meta_data.ImagePositionPatient, dtype=float)
    iop = np.array(meta_data.ImageOrientationPatient, dtype=float)
    slice_dir = np.cross(iop[:3], iop[3:])

    # --- Get original rescale parameters ---
    rescale_slope = float(getattr(meta_data, 'RescaleSlope', 1.0))
    rescale_intercept = float(getattr(meta_data, 'RescaleIntercept', 0.0))

    # Use AcquisitionTime with or without decimals
    try:
        original_time = datetime.strptime(meta_data.AcquisitionTime, "%H%M%S.%f")
    except ValueError:
        original_time = datetime.strptime(meta_data.AcquisitionTime, "%H%M%S")

    for i in range(num_slices):
        output_filename = os.path.join(output_folder, f"slice_{i+1:03d}.dcm")

        # Create a new FileDataset for each slice
        new_ds = FileDataset(
            output_filename,
            {},
            file_meta=meta_data.file_meta,
            preamble=meta_data.preamble,
        )

        # Copy all tags except pixel data (0x7FE0,0x0010)
        for elem in meta_data.iterall():
            if elem.tag != (0x7FE0, 0x0010):
                new_ds.add(elem)

        # Per-slice header changes:
        new_ds.InstanceNumber = i + 1
        new_time = original_time + timedelta(milliseconds=10*i)
        new_ds.AcquisitionTime = new_time.strftime("%H%M%S.%f")[:-3]
        new_ipp = ipp + slice_dir * slice_thick * i
        new_ds.ImagePositionPatient = [f"{x:.6f}" for x in new_ipp]
        new_ds.SOPInstanceUID = generate_uid()

        # --- Apply inverse rescale and flip Y axis ---
        slice_data = data[i, :, :]             # shape: (rows, cols)
        slice_data = np.flipud(slice_data)     # flip Y
        # Inverse: (raw_pixel_value) = (HU_value - intercept) / slope
        slice_data = (slice_data - rescale_intercept) / rescale_slope
        slice_data = np.round(slice_data).astype(np.int16)

        # Set PixelData
        new_ds.PixelData = slice_data.tobytes()

        # Restore original RescaleSlope and RescaleIntercept
        new_ds.RescaleSlope = rescale_slope
        new_ds.RescaleIntercept = rescale_intercept

        new_ds.save_as(output_filename)
   

