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
from PySide6.QtCore import Qt

from fcn_autocont.segmentator_ui import SegmentatorWindow
from fcn_autocont.segmentator_vendored import run_totalseg_for_folder_file
import fcn_autocont.segmentator_vendored as seg_vendored


def create_dummy_nifti(path: Path, shape=(32, 32, 16)):
    data = np.zeros(shape, dtype=np.int16)
    data[8:24, 8:24, 4:12] = 100
    affine = np.eye(4)
    img = nib.Nifti1Image(data, affine)
    nib.save(img, str(path))


def test_folder_batch_pipeline():
    app = QApplication.instance() or QApplication(sys.argv)

    # 1. Create a temporary folder with mock NIfTI scans
    tmp_dir = Path(tempfile.mkdtemp(prefix="amigo_test_folder_"))
    try:
        scan1 = tmp_dir / "patient01.nii.gz"
        scan2 = tmp_dir / "patient02.nii.gz"
        mask_file = tmp_dir / "patient01_ST_oldmask.nii.gz" # should be ignored
        text_file = tmp_dir / "notes.txt"                   # should be ignored

        create_dummy_nifti(scan1, shape=(20, 20, 10))
        create_dummy_nifti(scan2, shape=(30, 30, 15))
        create_dummy_nifti(mask_file, shape=(20, 20, 10))
        text_file.write_text("dummy info", encoding="utf-8")

        # 2. Test UI Window and Folder Batch Tab
        win = SegmentatorWindow()
        assert hasattr(win, "mode_tabs"), "SegmentatorWindow must have mode_tabs"
        assert win.mode_tabs.count() == 2, "mode_tabs must have 2 tabs"
        assert win.mode_tabs.tabText(0) == "Loaded Series (AMIGO)"
        assert win.mode_tabs.tabText(1) == "Folder Batch"

        # Switch to Folder Batch tab
        win.mode_tabs.setCurrentIndex(1)
        assert win.btn_run.text() == "Run Folder Batch"

        # Set folder path and scan
        win.folder_path_edit.setText(str(tmp_dir))
        win._scan_folder()

        # Check table contents
        assert win.folder_tbl.rowCount() == 2, f"Expected 2 NIfTI scans in table, found {win.folder_tbl.rowCount()}"
        file_names = [win.folder_tbl.item(r, 1).text() for r in range(win.folder_tbl.rowCount())]
        assert "patient01.nii.gz" in file_names
        assert "patient02.nii.gz" in file_names
        assert "patient01_ST_oldmask.nii.gz" not in file_names
        assert "notes.txt" not in file_names

        # Check dimensions column
        dim_item = win.folder_tbl.item(0, 3)
        assert dim_item is not None and "20×20×10" in dim_item.text()

        # Test selection getters
        selected = win.get_selected_folder_files()
        assert len(selected) == 2, "Both files should be selected by default"

        # Test deselect / select all
        win._select_all_folder(False)
        assert len(win.get_selected_folder_files()) == 0
        win._select_all_folder(True)
        assert len(win.get_selected_folder_files()) == 2

        # 3. Test run_totalseg_for_folder_file execution logic
        # Mock _run_totalseg to create fake masks in ts_out
        def mock_run_totalseg(owner, input_nii, out_dir, job_params):
            # Create a mock liver mask and spleen mask
            create_dummy_nifti(out_dir / "liver.nii.gz", shape=(20, 20, 10))
            create_dummy_nifti(out_dir / "spleen.nii.gz", shape=(20, 20, 10))
            return True, "Mock TS Success"

        orig_run_totalseg = seg_vendored._run_totalseg
        seg_vendored._run_totalseg = mock_run_totalseg

        try:
            params = {
                "task": "total",
                "ct_targets": ["liver", "spleen"],
                "mr_targets": [],
                "subroutines": [],
            }

            ok, msg, count = run_totalseg_for_folder_file(win, scan1, tmp_dir, params)
            assert ok is True, f"run_totalseg_for_folder_file failed: {msg}"
            assert count == 2, f"Expected 2 exported contours, got {count}"

            # Check autocont folder and case subfolder
            autocont_dir = tmp_dir / "autocont"
            assert autocont_dir.is_dir(), "autocont directory was not created"

            case_dir = autocont_dir / "patient01"
            assert case_dir.is_dir(), "Case subfolder 'patient01' was not created"

            # Check original file copied inside
            copied_orig = case_dir / "patient01.nii.gz"
            assert copied_orig.exists(), "Original file was not copied into case directory"

            # Check exported structure contours
            liver_contour = case_dir / "patient01_ST_liver.nii.gz"
            spleen_contour = case_dir / "patient01_ST_spleen.nii.gz"
            assert liver_contour.exists(), "Exported liver contour not found"
            assert spleen_contour.exists(), "Exported spleen contour not found"

            # Check structures.json manifest
            manifest_file = case_dir / "structures.json"
            assert manifest_file.exists(), "structures.json manifest not found"

            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            assert manifest.get("amigo_version") == "1.0"
            assert manifest["parent_series"]["original_file"] == "patient01.nii.gz"
            assert len(manifest["structures"]) == 2
            struc_names = [s["name"] for s in manifest["structures"]]
            assert "liver" in struc_names
            assert "spleen" in struc_names
            assert "color" in manifest["structures"][0]

            print("[OK] Folder batch autosegmentation test passed successfully!")

        finally:
            seg_vendored._run_totalseg = orig_run_totalseg

    finally:
        shutil.rmtree(str(tmp_dir), ignore_errors=True)


if __name__ == "__main__":
    test_folder_batch_pipeline()
