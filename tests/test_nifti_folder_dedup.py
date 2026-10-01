import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import sys
import shutil
import tempfile
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import nibabel as nib
from PySide6.QtWidgets import QApplication

from fcn_load.load_nifti import load_nifti_files


def create_dummy_nifti(path: Path, shape=(32, 32, 16), is_ct=False):
    data = np.zeros(shape, dtype=np.int16)
    if is_ct:
        data[:] = -1000  # CT air
        data[8:24, 8:24, 4:12] = 50   # tissue
    else:
        # Binary mask
        data[8:24, 8:24, 4:12] = 1
    affine = np.eye(4)
    img = nib.Nifti1Image(data, affine)
    nib.save(img, str(path))


class MockApp:
    def __init__(self):
        self.medical_image = {}
        self.last_nifti_dir = ""


def test_select_all_nifti_in_folder_no_duplicates():
    # Ensure QApplication exists for any internal Qt calls
    app = QApplication.instance() or QApplication(sys.argv)

    tmp_dir = Path(tempfile.mkdtemp(prefix="amigo_test_dedup_"))
    try:
        # Create primary scan
        scan = tmp_dir / "phase30_cropped.nii.gz"
        create_dummy_nifti(scan, shape=(20, 20, 10), is_ct=True)

        # Create structure contours
        st_bone = tmp_dir / "phase30_cropped_ST_cortical_bone.nii.gz"
        st_left = tmp_dir / "phase30_cropped_ST_lung_left.nii.gz"
        st_right = tmp_dir / "phase30_cropped_ST_lung_right.nii.gz"
        create_dummy_nifti(st_bone, shape=(20, 20, 10), is_ct=False)
        create_dummy_nifti(st_left, shape=(20, 20, 10), is_ct=False)
        create_dummy_nifti(st_right, shape=(20, 20, 10), is_ct=False)

        # Create structures.json manifest
        manifest_data = {
            "amigo_version": "1.0",
            "parent_series": {
                "original_file": "phase30_cropped.nii.gz"
            },
            "structures": [
                {"name": "cortical_bone", "filename": "phase30_cropped_ST_cortical_bone.nii.gz", "color": "#E6194B"},
                {"name": "lung_left", "filename": "phase30_cropped_ST_lung_left.nii.gz", "color": "#3CBA54"},
                {"name": "lung_right", "filename": "phase30_cropped_ST_lung_right.nii.gz", "color": "#4885ED"},
            ]
        }
        with open(tmp_dir / "structures.json", "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

        # User selects ALL NIfTI files inside the folder:
        # Note: mixing forward and backslashes as can happen between Qt dialog and os.path
        selected_paths = [
            str(scan).replace("\\", "/"),
            str(st_bone),
            str(st_left).replace("\\", "/"),
            str(st_right),
        ]

        mock_app = MockApp()
        load_nifti_files(mock_app, path=selected_paths)

        # Verify only ONE series is created (not double loading!)
        assert len(mock_app.medical_image) == 1, f"Expected 1 patient, got {len(mock_app.medical_image)}"
        pat_id = list(mock_app.medical_image.keys())[0]
        studies = mock_app.medical_image[pat_id]
        assert len(studies) == 1
        study_id = list(studies.keys())[0]
        mods = studies[study_id]
        assert len(mods) == 1
        modality = list(mods.keys())[0]
        series_list = mods[modality]

        assert len(series_list) == 1, f"Main image double-loaded! Expected 1 series, got {len(series_list)}"

        # Verify structures
        series = series_list[0]
        struct_names = series.get("structures_names", [])
        print("Loaded structure names:", struct_names)

        assert len(struct_names) == 3, f"Expected 3 structures, got {len(struct_names)}: {struct_names}"
        assert set(struct_names) == {"cortical_bone", "lung_left", "lung_right"}
        assert "cortical_bone_1" not in struct_names, "Duplicate structure cortical_bone_1 detected!"
        assert "lung_left_1" not in struct_names, "Duplicate structure lung_left_1 detected!"
        assert "lung_right_1" not in struct_names, "Duplicate structure lung_right_1 detected!"

        print("[OK] Deduplication test passed successfully!")

    finally:
        shutil.rmtree(str(tmp_dir), ignore_errors=True)


if __name__ == "__main__":
    test_select_all_nifti_in_folder_no_duplicates()
