# fcn_export/export_structures_dialog.py
# -*- coding: utf-8 -*-
"""
Export Structures Dialog for AMIGOpy.
Allows users to export contour masks to NIfTI (.nii.gz) or DICOM RTSTRUCT,
with Select All / Clear All controls, naming customization, and JSON sidecar
metadata manifests to maintain image-mask association.
Also provides 'import_structures_from_nifti' to reload exported masks back into a series.
"""

import os
import json
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple

import numpy as np
import SimpleITK as sitk

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPixmap, QPainter, QCursor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget,
    QListWidgetItem, QRadioButton, QButtonGroup, QLineEdit, QPushButton,
    QGroupBox, QMessageBox, QFrame, QCheckBox, QWidget, QSizePolicy,
    QFileDialog, QProgressBar
)

from fcn_operations.boolean_operations_dialog import (
    DEFAULT_NEW_COLORS, create_color_icon, calculate_mask_volume, refresh_amigo_views
)


def export_single_mask_nifti(mask_3d: np.ndarray, series_dict: dict, out_file_path: str):
    """
    Save a single 3D binary mask array to a compressed NIfTI (.nii.gz) file.
    Reverses AMIGOpy's internal Y-axis flip and replicates the geometry
    (origin, spacing, direction/affine) of the parent series.
    """
    # 1. Undo the Y-axis flip done when importing image/masks into AMIGOpy
    unflipped = np.flip(mask_3d.astype(np.uint8), axis=1)

    # 2. Convert numpy array (z, y, x) to SimpleITK image
    img = sitk.GetImageFromArray(unflipped)
    img = sitk.Cast(img, sitk.sitkUInt8)

    # 3. Restore geometry: prioritize copying directly from the original NIfTI file if available
    copied_from_ref = False
    orig_path = series_dict.get('metadata', {}).get('OriginalFilePath')
    if orig_path and os.path.isfile(orig_path):
        try:
            ref_img = sitk.ReadImage(orig_path)
            img.CopyInformation(ref_img)
            copied_from_ref = True
        except Exception:
            copied_from_ref = False

    if not copied_from_ref:
        md = series_dict.get('metadata', {})
        sp = md.get('PixelSpacing', [1.0, 1.0])
        st = md.get('SliceThickness', 1.0)
        origin = md.get('ImagePositionPatient', [0.0, 0.0, 0.0])
        direction = md.get('Direction', [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0])

        try:
            sx = float(sp[0]) if len(sp) > 0 else 1.0
            sy = float(sp[1]) if len(sp) > 1 else 1.0
            sz = float(st) if st is not None else 1.0
            img.SetSpacing((sx, sy, sz))
        except Exception:
            img.SetSpacing((1.0, 1.0, 1.0))

        if origin and len(origin) == 3:
            try:
                img.SetOrigin(tuple(float(v) for v in origin))
            except Exception:
                pass

        if direction and len(direction) == 9:
            try:
                img.SetDirection(tuple(float(v) for v in direction))
            except Exception:
                pass

    # 4. Write image
    os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
    sitk.WriteImage(img, str(out_file_path))


class ExportStructuresDialog(QDialog):
    """
    Dialog for exporting selected contour structures to NIfTI (.nii.gz) or DICOM RTSTRUCT.
    """

    def __init__(
        self,
        parent_app,
        patient_id: Optional[str] = None,
        study_id: Optional[str] = None,
        modality: Optional[str] = None,
        series_index: Optional[int] = None,
        preselected_name: Optional[str] = None,
        parent=None,
    ):
        super().__init__(parent or (parent_app if isinstance(parent_app, QWidget) else None))
        self.parent_app = parent_app
        self.patient_id = patient_id if patient_id is not None else getattr(parent_app, 'patientID', None)
        self.study_id = study_id if study_id is not None else getattr(parent_app, 'studyID', None)
        self.modality = modality if modality is not None else getattr(parent_app, 'modality', None)
        self.series_index = series_index if series_index is not None else getattr(parent_app, 'series_index', None)
        self.preselected_name = preselected_name

        self.setWindowTitle("Export Structures")
        self.resize(650, 600)
        self.setMinimumSize(560, 500)

        self._setup_style()
        self._init_ui()
        self._load_series_structures()

    def _setup_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1E242B;
                color: #ECEFF1;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QLabel {
                color: #ECEFF1;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #37474F;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                color: #90CAF9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
            }
            QListWidget {
                background-color: #263238;
                border: 1px solid #37474F;
                border-radius: 4px;
                color: #ECEFF1;
                padding: 4px;
            }
            QListWidget::item {
                padding: 4px;
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background-color: #37474F;
            }
            QListWidget::item:selected {
                background-color: #0284C7;
                color: #FFFFFF;
            }
            QComboBox, QLineEdit {
                background-color: #263238;
                border: 1px solid #37474F;
                border-radius: 4px;
                color: #FFFFFF;
                padding: 4px 8px;
            }
            QComboBox:focus, QLineEdit:focus {
                border: 1px solid #0284C7;
            }
            QPushButton {
                background-color: #37474F;
                color: #ECEFF1;
                border: 1px solid #455A64;
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
            QPushButton:pressed {
                background-color: #263238;
            }
            QPushButton#btnExport {
                background-color: #0284C7;
                color: #FFFFFF;
                font-weight: bold;
                border: none;
                padding: 8px 20px;
            }
            QPushButton#btnExport:hover {
                background-color: #0369A1;
            }
            QPushButton#btnExport:pressed {
                background-color: #075985;
            }
            QPushButton#btnExport:disabled {
                background-color: #37474F;
                color: #78909C;
            }
            QCheckBox, QRadioButton {
                color: #ECEFF1;
                spacing: 6px;
            }
            QProgressBar {
                border: 1px solid #37474F;
                border-radius: 4px;
                text-align: center;
                background-color: #263238;
                color: #FFFFFF;
            }
            QProgressBar::chunk {
                background-color: #0284C7;
                border-radius: 3px;
            }
        """)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(10)

        # ── 1. Header Information ──────────────────────────────────────────
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #263238; border-radius: 6px; padding: 6px;")
        h_layout = QVBoxLayout(header_frame)
        h_layout.setContentsMargins(8, 6, 8, 6)
        h_layout.setSpacing(3)

        self.title_lbl = QLabel("<b style='font-size:14px; color:#38BDF8;'>Export Structure Contours</b>")
        h_layout.addWidget(self.title_lbl)

        info_text = f"Series: <b>{self._get_series_name()}</b> | Modality: <b>{self.modality or 'N/A'}</b> | Patient: <b>{self.patient_id or 'N/A'}</b>"
        self.series_info_lbl = QLabel(info_text)
        self.series_info_lbl.setStyleSheet("color: #B0BEC5; font-size: 11px;")
        h_layout.addWidget(self.series_info_lbl)

        main_layout.addWidget(header_frame)

        # ── 2. Format Selection ────────────────────────────────────────────
        fmt_group = QGroupBox("Export Format")
        fmt_layout = QHBoxLayout(fmt_group)
        fmt_layout.setContentsMargins(10, 8, 10, 8)
        fmt_layout.setSpacing(12)

        fmt_layout.addWidget(QLabel("Format:"))
        self.combo_format = QComboBox()
        self.combo_format.addItem("NIfTI (*.nii.gz) — Binary Mask per Structure", "nifti")
        self.combo_format.addItem("DICOM RTSTRUCT (*.dcm) — [Planned]", "dicom")
        self.combo_format.currentIndexChanged.connect(self._on_format_changed)
        fmt_layout.addWidget(self.combo_format, 1)

        main_layout.addWidget(fmt_group)

        # ── 3. Structures Selection List ───────────────────────────────────
        struct_group = QGroupBox("Select Structures to Export")
        sg_layout = QVBoxLayout(struct_group)
        sg_layout.setContentsMargins(10, 8, 10, 8)
        sg_layout.setSpacing(6)

        # Quick action buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.btn_select_all = QPushButton("Select All")
        self.btn_select_all.clicked.connect(self._select_all_structures)
        self.btn_clear_all = QPushButton("Clear All")
        self.btn_clear_all.clicked.connect(self._clear_all_structures)
        self.btn_invert = QPushButton("Invert")
        self.btn_invert.clicked.connect(self._invert_selection)

        self.lbl_selected_count = QLabel("0 selected")
        self.lbl_selected_count.setStyleSheet("color: #38BDF8; font-weight: bold;")
        self.lbl_selected_count.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        btn_row.addWidget(self.btn_select_all)
        btn_row.addWidget(self.btn_clear_all)
        btn_row.addWidget(self.btn_invert)
        btn_row.addStretch(1)
        btn_row.addWidget(self.lbl_selected_count)
        sg_layout.addLayout(btn_row)

        # Filter / Search bar
        self.edit_filter = QLineEdit()
        self.edit_filter.setPlaceholderText("Filter structures by name...")
        self.edit_filter.textChanged.connect(self._filter_structures)
        sg_layout.addWidget(self.edit_filter)

        # Structures ListWidget
        self.list_structures = QListWidget()
        self.list_structures.itemChanged.connect(self._update_selected_count)
        sg_layout.addWidget(self.list_structures, 1)

        main_layout.addWidget(struct_group, 1)

        # ── 4. Destination & Naming Options ────────────────────────────────
        dest_group = QGroupBox("Export Destination & Options")
        dg_layout = QVBoxLayout(dest_group)
        dg_layout.setContentsMargins(10, 8, 10, 8)
        dg_layout.setSpacing(8)

        # Folder picker
        dest_row = QHBoxLayout()
        dest_row.addWidget(QLabel("Output Folder:"))
        self.edit_dest = QLineEdit()
        default_dir = self._get_default_output_dir()
        self.edit_dest.setText(default_dir)
        self.btn_browse = QPushButton("Browse…")
        self.btn_browse.clicked.connect(self._browse_destination)
        dest_row.addWidget(self.edit_dest, 1)
        dest_row.addWidget(self.btn_browse)
        dg_layout.addLayout(dest_row)

        # Checkbox options
        opts_row = QHBoxLayout()
        self.chk_subfolder = QCheckBox("Save in 'structures' subfolder")
        self.chk_subfolder.setChecked(True)
        self.chk_subfolder.setToolTip(
            "Creates a 'structures' subdirectory so mask files are neatly grouped separate from the main image."
        )

        self.chk_manifest = QCheckBox("Create metadata manifest (structures.json)")
        self.chk_manifest.setChecked(True)
        self.chk_manifest.setToolTip(
            "Saves a JSON sidecar file recording structure names, colors, and parent series association.\n"
            "This allows AMIGOpy to automatically reload and reconnect the masks to the original image later."
        )

        opts_row.addWidget(self.chk_subfolder)
        opts_row.addWidget(self.chk_manifest)
        opts_row.addStretch(1)
        dg_layout.addLayout(opts_row)

        # Filename naming convention
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("File Naming:"))
        orig_base = self._get_original_file_base()
        self.rad_name_st = QRadioButton(f"<OriginalFile>_ST_<Name>.nii.gz")
        self.rad_name_st.setChecked(True)
        self.rad_name_st.setToolTip(f"Example: {orig_base}_ST_heart.nii.gz (Enables auto-recognition when reopened)")

        self.rad_name_only = QRadioButton("<Name>.nii.gz")
        self.rad_name_only.setToolTip("Example: heart.nii.gz")

        self.rad_name_series = QRadioButton("<Series>_<Name>.nii.gz")
        self.rad_name_series.setToolTip(f"Example: {orig_base}_heart.nii.gz")

        self.bg_naming = QButtonGroup(self)
        self.bg_naming.addButton(self.rad_name_st)
        self.bg_naming.addButton(self.rad_name_only)
        self.bg_naming.addButton(self.rad_name_series)

        name_row.addWidget(self.rad_name_st)
        name_row.addWidget(self.rad_name_only)
        name_row.addWidget(self.rad_name_series)
        name_row.addStretch(1)
        dg_layout.addLayout(name_row)

        main_layout.addWidget(dest_group)

        # ── 5. Progress Bar & Action Buttons ──────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_export = QPushButton("Export Structures")
        self.btn_export.setObjectName("btnExport")
        self.btn_export.clicked.connect(self._do_export)

        btn_box.addStretch(1)
        btn_box.addWidget(self.btn_cancel)
        btn_box.addWidget(self.btn_export)
        main_layout.addLayout(btn_box)

    def _get_series_name(self) -> str:
        s_series = self._get_series_dict()
        if not s_series:
            return "Current Series"
        sn = s_series.get('SeriesNumber')
        sd = s_series.get('metadata', {}).get('SeriesDescription')
        return str(sd or sn or "Series")

    def _get_original_file_base(self) -> str:
        s_series = self._get_series_dict()
        if not s_series:
            return "image"
        orig_path = s_series.get('metadata', {}).get('OriginalFilePath')
        if orig_path:
            base = os.path.basename(orig_path)
            for ext in ('.nii.gz', '.nii', '.dcm', '.gz'):
                if base.lower().endswith(ext):
                    base = base[:-len(ext)]
                    break
            if base:
                return base
        sd = s_series.get('metadata', {}).get('SeriesDescription')
        sn = s_series.get('SeriesNumber')
        fallback = str(sd or sn or "image")
        for ext in ('.nii.gz', '.nii', '.dcm', '.gz'):
            if fallback.lower().endswith(ext):
                fallback = fallback[:-len(ext)]
                break
        return fallback

    def _get_series_dict(self) -> Optional[dict]:
        try:
            return self.parent_app.medical_image[self.patient_id][self.study_id][self.modality][self.series_index]
        except (KeyError, IndexError, TypeError):
            return None

    def _get_default_output_dir(self) -> str:
        s_series = self._get_series_dict()
        if s_series:
            orig = s_series.get('metadata', {}).get('OriginalFilePath')
            if orig and os.path.exists(os.path.dirname(orig)):
                return os.path.dirname(orig)

        last_dir = getattr(self.parent_app, 'last_export_dir', None)
        if last_dir and os.path.isdir(last_dir):
            return last_dir

        doc_dir = os.path.join(os.path.expanduser("~"), "AMIGO_Exports")
        return doc_dir

    def _load_series_structures(self):
        self.list_structures.clear()
        s_series = self._get_series_dict()
        if not s_series:
            return

        structures = s_series.get('structures', {})
        names = s_series.get('structures_names', [])
        keys = s_series.get('structures_keys', [])
        colors = s_series.get('structures_color', [])
        metadata = s_series.get('metadata', {})

        for idx, name in enumerate(names):
            key = keys[idx] if idx < len(keys) else None
            if not key or key not in structures:
                continue

            s_item = structures[key]
            mask = s_item.get('Mask3D')
            if mask is None:
                continue

            color_hex = colors[idx] if idx < len(colors) else "#00E5FF"
            voxels, vol_cc = calculate_mask_volume(mask, metadata)

            item = QListWidgetItem()
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            
            # If preselected_name was specified, check only that, else check all
            if self.preselected_name:
                item.setCheckState(Qt.Checked if name == self.preselected_name else Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)

            item.setIcon(create_color_icon(color_hex, size=14))
            item.setText(f"{name}  ({vol_cc:.1f} cc, {voxels:,} voxels)")
            item.setData(Qt.UserRole, {
                'name': name,
                'key': key,
                'color': color_hex,
                'voxels': voxels,
                'volume_cc': vol_cc,
                'idx': idx
            })

            self.list_structures.addItem(item)

        self._update_selected_count()

    def _select_all_structures(self):
        for i in range(self.list_structures.count()):
            self.list_structures.item(i).setCheckState(Qt.Checked)
        self._update_selected_count()

    def _clear_all_structures(self):
        for i in range(self.list_structures.count()):
            self.list_structures.item(i).setCheckState(Qt.Unchecked)
        self._update_selected_count()

    def _invert_selection(self):
        for i in range(self.list_structures.count()):
            it = self.list_structures.item(i)
            new_state = Qt.Unchecked if it.checkState() == Qt.Checked else Qt.Checked
            it.setCheckState(new_state)
        self._update_selected_count()

    def _filter_structures(self, text: str):
        query = text.strip().lower()
        for i in range(self.list_structures.count()):
            it = self.list_structures.item(i)
            data = it.data(Qt.UserRole) or {}
            s_name = data.get('name', '').lower()
            it.setHidden(query not in s_name if query else False)

    def _update_selected_count(self):
        checked = 0
        total = self.list_structures.count()
        for i in range(total):
            if self.list_structures.item(i).checkState() == Qt.Checked:
                checked += 1
        self.lbl_selected_count.setText(f"{checked} of {total} selected")
        self.btn_export.setEnabled(checked > 0)

    def _on_format_changed(self, idx: int):
        fmt = self.combo_format.currentData()
        if fmt == "dicom":
            QMessageBox.information(
                self, "DICOM RTSTRUCT Export",
                "DICOM RTSTRUCT export is currently under development.\n"
                "NIfTI export is fully functional and recommended for 3D binary masks."
            )
            self.combo_format.setCurrentIndex(0)

    def _browse_destination(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Export Directory", self.edit_dest.text() or str(Path.home())
        )
        if folder:
            self.edit_dest.setText(folder)
            self.parent_app.last_export_dir = folder

    def _do_export(self):
        s_series = self._get_series_dict()
        if not s_series:
            QMessageBox.critical(self, "Export Failed", "Could not locate series data.")
            return

        base_dir = self.edit_dest.text().strip()
        if not base_dir:
            QMessageBox.warning(self, "Missing Directory", "Please choose an output directory.")
            return

        target_dir = os.path.join(base_dir, "structures") if self.chk_subfolder.isChecked() else base_dir
        os.makedirs(target_dir, exist_ok=True)
        self.parent_app.last_export_dir = base_dir

        # Collect checked items
        selected_items = []
        for i in range(self.list_structures.count()):
            it = self.list_structures.item(i)
            if it.checkState() == Qt.Checked:
                selected_items.append(it.data(Qt.UserRole))

        if not selected_items:
            QMessageBox.warning(self, "No Structures", "No structures selected for export.")
            return

        series_name = self._get_series_name()
        orig_base = self._get_original_file_base()
        safe_orig_base = "".join(c for c in orig_base if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')

        structures = s_series.get('structures', {})
        line_widths = s_series.get('structures_line_width', [])
        transpars = s_series.get('structures_transparency', [])
        mask_trs = s_series.get('structures_mask_transparency', [])

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(selected_items))
        self.progress_bar.setValue(0)
        self.btn_export.setEnabled(False)

        manifest_entries = []
        exported_files = []

        try:
            for idx, data in enumerate(selected_items):
                s_name = data['name']
                s_key = data['key']
                s_idx = data['idx']
                color_hex = data['color']

                mask = structures.get(s_key, {}).get('Mask3D')
                if mask is None:
                    continue

                # Filename
                safe_name = "".join(c for c in s_name if c.isalnum() or c in (' ', '_', '-')).strip()
                safe_name = safe_name.replace(' ', '_')
                if self.rad_name_st.isChecked():
                    file_name = f"{safe_orig_base}_ST_{safe_name}.nii.gz"
                elif self.rad_name_series.isChecked():
                    safe_series = "".join(c for c in series_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
                    file_name = f"{safe_series}_{safe_name}.nii.gz"
                else:
                    file_name = f"{safe_name}.nii.gz"

                file_path = os.path.join(target_dir, file_name)

                # Export single NIfTI mask
                export_single_mask_nifti(mask, s_series, file_path)
                exported_files.append(file_path)

                # Record metadata for manifest
                manifest_entries.append({
                    "name": s_name,
                    "filename": file_name,
                    "relative_path": os.path.relpath(file_path, base_dir).replace("\\", "/"),
                    "color": color_hex,
                    "line_width": line_widths[s_idx] if s_idx < len(line_widths) else 3.0,
                    "transparency": transpars[s_idx] if s_idx < len(transpars) else 0.1,
                    "mask_transparency": mask_trs[s_idx] if s_idx < len(mask_trs) else 0.5,
                    "voxel_count": data['voxels'],
                    "volume_cc": data['volume_cc']
                })

                self.progress_bar.setValue(idx + 1)

            # Write structures.json manifest
            if self.chk_manifest.isChecked():
                manifest_data = {
                    "amigo_version": "1.0",
                    "exported_at": datetime.datetime.now().isoformat(),
                    "parent_series": {
                        "patient_id": self.patient_id,
                        "study_id": self.study_id,
                        "modality": self.modality,
                        "series_number": s_series.get('SeriesNumber'),
                        "series_description": series_name,
                        "original_file": os.path.basename(s_series.get('metadata', {}).get('OriginalFilePath', ''))
                    },
                    "structures": manifest_entries
                }

                manifest_path = os.path.join(target_dir, "structures.json")
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(manifest_data, f, indent=2)

                # Also write a manifest at the base dir if exporting into a subfolder
                if self.chk_subfolder.isChecked():
                    root_manifest = os.path.join(base_dir, f"{safe_orig_base}_structures.json")
                    with open(root_manifest, 'w', encoding='utf-8') as f:
                        json.dump(manifest_data, f, indent=2)

            # Success confirmation
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Export Complete")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText(
                f"<b>Successfully exported {len(exported_files)} structure(s)!</b><br><br>"
                f"Destination folder:<br><code>{target_dir}</code>"
            )
            btn_open = msg_box.addButton("Open Folder", QMessageBox.ActionRole)
            msg_box.addButton(QMessageBox.Ok)
            msg_box.exec_()

            if msg_box.clickedButton() == btn_open:
                try:
                    os.startfile(target_dir)
                except Exception:
                    pass

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred during export:\n{e}")
        finally:
            self.progress_bar.setVisible(False)
            self.btn_export.setEnabled(True)


def open_export_structures_dialog(
    parent_app,
    patient_id: Optional[str] = None,
    study_id: Optional[str] = None,
    modality: Optional[str] = None,
    series_index: Optional[int] = None,
    preselected_name: Optional[str] = None
):
    """
    Launch the Export Structures dialog for the target series.
    """
    if patient_id is None:
        patient_id = getattr(parent_app, 'patientID', None)
    if study_id is None:
        study_id = getattr(parent_app, 'studyID', None)
    if modality is None:
        modality = getattr(parent_app, 'modality', None)
    if series_index is None:
        series_index = getattr(parent_app, 'series_index', None)

    try:
        s_series = parent_app.medical_image[patient_id][study_id][modality][series_index]
        names = s_series.get('structures_names', [])
        if not names:
            QMessageBox.information(
                parent_app, "No Structures",
                "This series has no structures to export."
            )
            return
    except (KeyError, IndexError, TypeError):
        QMessageBox.warning(parent_app, "Error", "Could not locate series data.")
        return

    dlg = ExportStructuresDialog(
        parent_app,
        patient_id=patient_id,
        study_id=study_id,
        modality=modality,
        series_index=series_index,
        preselected_name=preselected_name
    )
    dlg.exec_()


TOTALSEGMENTATOR_LABELS = {
    1: "spleen", 2: "kidney_right", 3: "kidney_left", 4: "gallbladder", 5: "liver",
    6: "stomach", 7: "aorta", 8: "inferior_vena_cava", 9: "portal_vein_and_splenic_vein",
    10: "pancreas", 11: "adrenal_gland_right", 12: "adrenal_gland_left",
    13: "lung_upper_lobe_left", 14: "lung_lower_lobe_left", 15: "lung_upper_lobe_right",
    16: "lung_middle_lobe_right", 17: "lung_lower_lobe_right", 18: "vertebrae_L5",
    19: "vertebrae_L4", 20: "vertebrae_L3", 21: "vertebrae_L2", 22: "vertebrae_L1",
    23: "vertebrae_T12", 24: "vertebrae_T11", 25: "vertebrae_T10", 26: "vertebrae_T9",
    27: "vertebrae_T8", 28: "vertebrae_T7", 29: "vertebrae_T6", 30: "vertebrae_T5",
    31: "vertebrae_T4", 32: "vertebrae_T3", 33: "vertebrae_T2", 34: "vertebrae_T1",
    35: "vertebrae_C7", 36: "vertebrae_C6", 37: "vertebrae_C5", 38: "vertebrae_C4",
    39: "vertebrae_C3", 40: "vertebrae_C2", 41: "vertebrae_C1",
    42: "esophagus", 43: "trachea", 44: "heart_myocardium", 45: "heart_atrium_left",
    46: "heart_ventricle_left", 47: "heart_atrium_right", 48: "heart_ventricle_right",
    49: "pulmonary_artery", 50: "brain", 51: "iliac_artery_left", 52: "iliac_artery_right",
    53: "iliac_vena_left", 54: "iliac_vena_right", 55: "small_bowel", 56: "duodenum",
    57: "colon", 58: "rib_left_1", 59: "rib_left_2", 60: "rib_left_3", 61: "rib_left_4",
    62: "rib_left_5", 63: "rib_left_6", 64: "rib_left_7", 65: "rib_left_8", 66: "rib_left_9",
    67: "rib_left_10", 68: "rib_left_11", 69: "rib_left_12", 70: "rib_right_1",
    71: "rib_right_2", 72: "rib_right_3", 73: "rib_right_4", 74: "rib_right_5",
    75: "rib_right_6", 76: "rib_right_7", 77: "rib_right_8", 78: "rib_right_9",
    79: "rib_right_10", 80: "rib_right_11", 81: "rib_right_12", 82: "humerus_left",
    83: "humerus_right", 84: "scapula_left", 85: "scapula_right", 86: "clavicula_left",
    87: "clavicula_right", 88: "femur_left", 89: "femur_right", 90: "hip_left",
    91: "hip_right", 92: "sacrum", 93: "face", 94: "gluteus_maximus_left",
    95: "gluteus_maximus_right", 96: "gluteus_medius_left", 97: "gluteus_medius_right",
    98: "gluteus_minimus_left", 99: "gluteus_minimus_right", 100: "autochthon_left",
    101: "autochthon_right", 102: "iliopsoas_left", 103: "iliopsoas_right", 104: "urinary_bladder"
}


def clean_structure_name(filename_or_path: str) -> str:
    """
    Derive a clean, human-readable structure name from a filename or path from any software.
    """
    base = os.path.basename(str(filename_or_path))
    for ext in ('.nii.gz', '.nii', '.gz'):
        if base.lower().endswith(ext):
            base = base[:-len(ext)]
            break

    if "_ST_" in base:
        base = base.split("_ST_")[-1].strip()

    bl = base.lower()
    for prefix in (
        "segmentation_", "segmentation-", "mask_", "mask-",
        "seg_", "seg-", "labels_", "labels-", "label_", "label-"
    ):
        if bl.startswith(prefix):
            base = base[len(prefix):]
            bl = base.lower()
            break

    for suffix in (
        "_segmentation", "-segmentation", "_mask", "-mask",
        "_seg", "-seg", "_label", "-label", "_labelmap", "-labelmap",
        "_roi", "-roi"
    ):
        if bl.endswith(suffix):
            base = base[:-len(suffix)]
            bl = base.lower()
            break

    clean = base.strip()
    return clean or "Structure"


def resample_mask_to_series(mask_sitk_img: sitk.Image, series_dict: dict) -> Optional[np.ndarray]:
    """
    Resample a SimpleITK mask image onto the grid/geometry of the target series.
    Returns (z, y, x) binary numpy array flipped along axis=1 (matching AMIGOpy internal format),
    or None if geometry cannot be determined.
    """
    orig_path = series_dict.get('metadata', {}).get('OriginalFilePath')
    ref_img = None
    if orig_path and os.path.isfile(orig_path):
        try:
            ref_img = sitk.ReadImage(orig_path)
        except Exception:
            ref_img = None

    ref_mat = series_dict.get('3DMatrix')
    if ref_mat is None or not isinstance(ref_mat, np.ndarray):
        return None

    if ref_img is None:
        md = series_dict.get('metadata', {})
        sp = md.get('PixelSpacing', [1.0, 1.0])
        st = md.get('SliceThickness', 1.0)
        origin = md.get('ImagePositionPatient', [0.0, 0.0, 0.0])
        direction = md.get('Direction', [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0])

        sx = float(sp[0]) if len(sp) > 0 else 1.0
        sy = float(sp[1]) if len(sp) > 1 else 1.0
        sz = float(st) if st is not None else 1.0

        shape_z, shape_y, shape_x = ref_mat.shape
        ref_img = sitk.Image(shape_x, shape_y, shape_z, sitk.sitkUInt8)
        ref_img.SetSpacing((sx, sy, sz))
        if origin and len(origin) == 3:
            try:
                ref_img.SetOrigin(tuple(float(v) for v in origin))
            except Exception:
                pass
        if direction and len(direction) == 9:
            try:
                ref_img.SetDirection(tuple(float(v) for v in direction))
            except Exception:
                pass

    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(ref_img)
    resampler.SetInterpolator(sitk.sitkNearestNeighbor)
    resampler.SetDefaultPixelValue(0)
    resampled_sitk = resampler.Execute(mask_sitk_img)

    arr = sitk.GetArrayFromImage(resampled_sitk)
    arr = np.flip(arr, axis=1)
    return arr


def import_structures_from_nifti(
    parent_app,
    patient_id: Optional[str] = None,
    study_id: Optional[str] = None,
    modality: Optional[str] = None,
    series_index: Optional[int] = None,
    paths: Optional[List[str]] = None,
    show_message: bool = True
) -> int:
    """
    Import one or more NIfTI mask files (.nii, .nii.gz) or a structures.json manifest
    directly as structures of the specified series.
    Compatible with output from ANY software (TotalSegmentator, 3D Slicer, nnUNet, ITK-SNAP, etc.).
    Supports both binary masks and multi-label segmentation files.
    Automatically resamples masks if spatial dimensions or grids differ.
    """
    if patient_id is None:
        patient_id = getattr(parent_app, 'patientID', None)
    if study_id is None:
        study_id = getattr(parent_app, 'studyID', None)
    if modality is None:
        modality = getattr(parent_app, 'modality', None)
    if series_index is None:
        series_index = getattr(parent_app, 'series_index', None)

    try:
        s_series = parent_app.medical_image[patient_id][study_id][modality][series_index]
    except (KeyError, IndexError, TypeError):
        if show_message:
            QMessageBox.warning(parent_app, "Error", "Could not locate target series to import structures into.")
        return 0

    ref_mat = s_series.get('3DMatrix')
    if ref_mat is None or not isinstance(ref_mat, np.ndarray):
        if show_message:
            QMessageBox.warning(parent_app, "Error", "Target series has no 3D image matrix.")
        return 0

    start_dir = getattr(parent_app, 'last_nifti_dir', str(Path.home()))

    if not paths:
        selected_files, _ = QFileDialog.getOpenFileNames(
            parent_app,
            "Import Structures from NIfTI",
            start_dir,
            "Structure Files (*.nii.gz *.nii *.json);;Compressed NIfTI (*.nii.gz);;NIfTI (*.nii);;Manifest (*.json);;All files (*)"
        )
        if not selected_files:
            return 0
        paths = selected_files

    structures = s_series.setdefault('structures', {})
    existing_names = s_series.setdefault('structures_names', [])
    existing_keys = s_series.setdefault('structures_keys', [])
    existing_colors = s_series.setdefault('structures_color', [])

    imported_count = 0

    # Expand any manifest JSON files
    files_to_process = []
    manifest_meta = {}
    for p in paths:
        if p.lower().endswith('.json'):
            try:
                with open(p, 'r', encoding='utf-8') as jf:
                    data = json.load(jf)
                p_dir = os.path.dirname(p)
                for item in data.get('structures', []):
                    fn = item.get('filename')
                    rel = item.get('relative_path')
                    candidates = []
                    if fn:
                        candidates.append(os.path.normpath(os.path.join(p_dir, fn)))
                    if rel:
                        candidates.append(os.path.normpath(os.path.join(p_dir, rel)))
                        candidates.append(os.path.normpath(os.path.join(os.path.dirname(p_dir), rel)))

                    found_p = None
                    for cand in candidates:
                        if os.path.isfile(cand):
                            found_p = cand
                            break

                    if found_p and found_p not in files_to_process:
                        files_to_process.append(found_p)
                        manifest_meta[found_p] = item
            except Exception as e:
                print(f"[Import] Error reading manifest {p}: {e}")
        else:
            files_to_process.append(p)

    for fpath in files_to_process:
        try:
            reader = sitk.ImageFileReader()
            reader.SetFileName(fpath)
            sitk_img = reader.Execute()

            # Cast to numpy array (z, y, x)
            arr = sitk.GetArrayFromImage(sitk_img)
            # Re-apply internal AMIGOpy Y flip
            arr = np.flip(arr, axis=1)

            # Check dimensions match series image; if not, resample onto series geometry
            if arr.shape != ref_mat.shape:
                try:
                    resampled = resample_mask_to_series(sitk_img, s_series)
                    if resampled is not None and resampled.shape == ref_mat.shape:
                        arr = resampled
                    else:
                        print(f"[Import] Shape mismatch for {fpath}: mask shape {arr.shape} != image shape {ref_mat.shape}. Skipping.")
                        continue
                except Exception as ex_resample:
                    print(f"[Import] Resampling failed for {fpath}: {ex_resample}")
                    continue

            # Identify non-zero labels
            unique_vals = np.unique(arr)
            pos_vals = [int(v) for v in unique_vals if v > 0]
            if not pos_vals:
                print(f"[Import] {fpath} contains only background zeros. Skipping.")
                continue

            # Multi-label check (e.g. TotalSegmentator, nnUNet, 3D Slicer labelmap)
            is_multilabel = (len(pos_vals) > 1 and len(pos_vals) <= 150 and np.all(np.equal(np.mod(unique_vals, 1), 0)))

            if is_multilabel:
                items_to_add = []
                for val in pos_vals:
                    sub_mask = (arr == val).astype(np.uint8)
                    val_name = TOTALSEGMENTATOR_LABELS.get(val) or f"{clean_structure_name(fpath)}_label_{val}"
                    items_to_add.append((val_name, sub_mask, None))
            else:
                meta = manifest_meta.get(fpath, {})
                name = meta.get('name') or clean_structure_name(fpath)
                mask_3d = (arr > 0).astype(np.uint8)
                color = meta.get('color')
                items_to_add = [(name, mask_3d, color)]

            for s_name_cand, mask_3d, pref_color in items_to_add:
                # Ensure unique name
                unique_name = s_name_cand
                c = 1
                while unique_name in existing_names:
                    unique_name = f"{s_name_cand}_{c}"
                    c += 1

                # Allocate unique key Structure_xxx
                all_keys = set(structures.keys())
                existing_nums = [
                    int(k.split("_")[-1]) for k in all_keys
                    if k.startswith("Structure_") and k.split("_")[-1].isdigit()
                ]
                next_num = (max(existing_nums) if existing_nums else len(all_keys)) + 1
                while f"Structure_{next_num:03d}" in all_keys:
                    next_num += 1
                new_key = f"Structure_{next_num:03d}"

                color = pref_color or DEFAULT_NEW_COLORS[len(existing_names) % len(DEFAULT_NEW_COLORS)]

                structures[new_key] = {
                    'Mask3D': mask_3d,
                    'mask': mask_3d,
                    'Name': unique_name,
                    'Modified': 1,
                    'Contours2D': {'axial': {}, 'sagittal': {}, 'coronal': {}},
                    'VTKActors2D': {}
                }

                s_series.setdefault('structures_keys', []).append(new_key)
                s_series.setdefault('structures_names', []).append(unique_name)
                s_series.setdefault('structures_view', []).append(1)
                s_series.setdefault('structures_color', []).append(color)
                s_series.setdefault('structures_line_width', []).append(3.0)
                s_series.setdefault('structures_transparency', []).append(0.1)
                s_series.setdefault('structures_mask_transparency', []).append(0.5)

                imported_count += 1

        except Exception as e:
            print(f"[Import] Failed to import {fpath}: {e}")

    if imported_count > 0:
        refresh_amigo_views(parent_app, s_series, patient_id, study_id, modality, series_index)
        if show_message:
            QMessageBox.information(
                parent_app, "Import Succeeded",
                f"Successfully imported {imported_count} structure(s) into:\n"
                f"{s_series.get('metadata', {}).get('SeriesDescription', 'Series')}"
            )
    else:
        if show_message:
            QMessageBox.warning(
                parent_app, "Import Failed",
                "No compatible structure masks could be imported."
            )

    return imported_count


def is_structure_nifti(path_or_filename: str | Path) -> Tuple[bool, str, str]:
    """
    Check if a NIfTI filename follows the structure contour mask convention:
    <OriginalFile>_ST_<StructureName>.nii.gz (or .nii)

    Returns:
        (is_struct: bool, image_base: str, struct_name: str)
    """
    fn = os.path.basename(str(path_or_filename))
    fl = fn.lower()
    if not (fl.endswith('.nii') or fl.endswith('.nii.gz') or fl.endswith('.gz')):
        return False, "", ""

    stem = fn
    for ext in ('.nii.gz', '.nii', '.gz'):
        if fl.endswith(ext):
            stem = fn[:-len(ext)]
            break

    if "_ST_" in stem:
        parts = stem.split("_ST_")
        img_base = "_ST_".join(parts[:-1]).strip()
        st_name = parts[-1].strip()
        if img_base and st_name:
            return True, img_base, st_name

    return False, "", ""
