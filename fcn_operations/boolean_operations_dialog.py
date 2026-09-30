# fcn_operations/boolean_operations_dialog.py
# -*- coding: utf-8 -*-
"""
Boolean Contour Operations Tool for AMIGOpy.
Allows users to perform 3D Boolean operations (Union, Subtract, Intersect, XOR)
between a Main contour and one or more Tool contours, with the option to
create a new contour or overwrite the main contour.
"""

from typing import Optional, List, Dict, Tuple
import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPixmap, QPainter, QCursor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget,
    QListWidgetItem, QRadioButton, QButtonGroup, QLineEdit, QPushButton,
    QGroupBox, QColorDialog, QMessageBox, QFrame, QSplitter, QCheckBox,
    QWidget, QSizePolicy, QTextEdit, QInputDialog
)


DEFAULT_NEW_COLORS = [
    "#00E5FF",  # Bright Cyan
    "#FF4081",  # Pink
    "#76FF03",  # Lime
    "#FFD600",  # Yellow
    "#FF6D00",  # Deep Orange
    "#E040FB",  # Purple
    "#1DE9B6",  # Teal
    "#FF5252",  # Coral Red
    "#69F0AE",  # Mint
    "#448AFF",  # Blue
]


def create_color_icon(color_hex: str, size: int = 14) -> QIcon:
    """Create a small rounded color swatch icon for dropdowns and list items."""
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(color_hex))
    painter.setPen(QColor("#455A64"))
    painter.drawRoundedRect(1, 1, size - 2, size - 2, 3, 3)
    painter.end()
    return QIcon(pix)


def calculate_mask_volume(mask: np.ndarray, metadata: dict) -> Tuple[int, float]:
    """Calculate voxel count and volume in cc (cm^3)."""
    voxels = int(np.sum(mask > 0)) if mask is not None else 0
    sx, sy, sz = 1.0, 1.0, 1.0
    if isinstance(metadata, dict):
        sp = metadata.get('PixelSpacing')
        if sp and len(sp) >= 2:
            try:
                sx = float(sp[0])
                sy = float(sp[1])
            except (ValueError, TypeError):
                pass
        st = metadata.get('SliceThickness')
        if st is not None:
            try:
                sz = float(st)
            except (ValueError, TypeError):
                pass
    vol_cc = (voxels * sx * sy * sz) / 1000.0
    return voxels, vol_cc


def refresh_amigo_views(parent_app, series_dict, patient_id=None, study_id=None, modality=None, series_index=None):
    """
    Refresh all AMIGOpy UI lists, trees, and VTK views to reflect structure changes.
    """
    # 1. Update left Data Tree if available
    if hasattr(parent_app, 'DataTreeView') and getattr(parent_app, 'model', None) is not None:
        try:
            from fcn_load.populate_med_image_list import populate_medical_image_tree
            populate_medical_image_tree(parent_app)
        except Exception as e:
            print(f"[Boolean] Error populating medical image tree: {e}")

    # Check if this series is currently active in the viewer
    is_active = True
    if patient_id is not None and getattr(parent_app, 'patientID', None) != patient_id:
        is_active = False
    if study_id is not None and getattr(parent_app, 'studyID', None) != study_id:
        is_active = False
    if modality is not None and getattr(parent_app, 'modality', None) != modality:
        is_active = False
    if series_index is not None and getattr(parent_app, 'series_index', None) != series_index:
        is_active = False

    if is_active:
        # 2. Update View tab STRUCTlist
        names = series_dict.get('structures_names', [])
        keys = series_dict.get('structures_keys', [])
        if hasattr(parent_app, 'STRUCTlist') and parent_app.STRUCTlist is not None:
            try:
                from fcn_RTFiles.process_rt_files import update_structure_list_widget
                update_structure_list_widget(parent_app, names, keys, mode=1)
            except Exception as e:
                print(f"[Boolean] Error updating STRUCTlist: {e}")

        # 3. Update Segmentation tab segStructList
        if hasattr(parent_app, 'segStructList') and parent_app.segStructList is not None:
            try:
                from fcn_segmentation.functions_segmentation import update_seg_struct_list
                update_seg_struct_list(parent_app)
            except Exception as e:
                pass

        # 4. Trigger contour pre-computation and redraw in View tab
        if isinstance(parent_app, QWidget) and hasattr(parent_app, 'vtkWidgetAxial'):
            try:
                from fcn_RTFiles.process_rt_files import _refresh_all_views
                _refresh_all_views(parent_app)
            except Exception as e:
                print(f"[Boolean] Error refreshing views: {e}")

        # 5. Render VTK widgets
        for widget_name in ("vtkWidgetAxial", "vtkWidgetSagittal", "vtkWidgetCoronal"):
            w = getattr(parent_app, widget_name, None)
            if w is not None and hasattr(w, "GetRenderWindow"):
                try:
                    w.GetRenderWindow().Render()
                except Exception:
                    pass


def delete_single_structure(parent_app, patient_id, study_id, modality, series_index, struct_name):
    """
    Delete a single structure by name from the given series and refresh all views.
    """
    reply = QMessageBox.question(
        parent_app, "Confirm Deletion",
        f"Are you sure you want to delete structure '{struct_name}'?",
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    if reply != QMessageBox.Yes:
        return

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
        return

    structures = s_series.get('structures', {})
    names = s_series.get('structures_names', [])
    keys = s_series.get('structures_keys', [])

    if struct_name not in names:
        return

    idx = names.index(struct_name)
    s_key = keys[idx] if idx < len(keys) else None

    # Remove from structures dict
    if s_key and s_key in structures:
        structures.pop(s_key, None)

    # Remove from parallel lists
    for list_name in ('structures_names', 'structures_keys', 'structures_view',
                      'structures_color', 'structures_line_width',
                      'structures_transparency', 'structures_mask_transparency'):
        arr = s_series.get(list_name)
        if isinstance(arr, list) and idx < len(arr):
            arr.pop(idx)

    refresh_amigo_views(parent_app, s_series, patient_id, study_id, modality, series_index)


def duplicate_structure(parent_app, patient_id, study_id, modality, series_index, struct_name):
    """
    Duplicate a structure in the given series and refresh all views.
    Prompts the user for a new contour name with a sensible default like '<name>_copy'.
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
        QMessageBox.warning(parent_app, "Error", "Could not locate series data.")
        return

    structures = s_series.get('structures', {})
    names = s_series.get('structures_names', [])
    keys = s_series.get('structures_keys', [])

    if struct_name not in names:
        QMessageBox.warning(parent_app, "Error", f"Structure '{struct_name}' not found.")
        return

    src_idx = names.index(struct_name)
    src_key = keys[src_idx] if src_idx < len(keys) else None
    if not src_key or src_key not in structures:
        QMessageBox.warning(parent_app, "Error", f"Structure data for '{struct_name}' is missing.")
        return

    src_item = structures[src_key]
    src_mask = src_item.get('Mask3D')
    if src_mask is None:
        QMessageBox.warning(parent_app, "Error", f"Structure '{struct_name}' has no 3D mask.")
        return

    # Suggest unique default name
    base_name = f"{struct_name}_copy"
    candidate_name = base_name
    counter = 1
    while candidate_name in names:
        candidate_name = f"{base_name}_{counter}"
        counter += 1

    # Prompt user for new structure name
    new_name, ok = QInputDialog.getText(
        parent_app, "Duplicate Structure",
        f"Enter name for duplicated structure of '{struct_name}':",
        text=candidate_name
    )
    if not ok or not new_name.strip():
        return

    new_name = new_name.strip()
    if new_name in names:
        QMessageBox.warning(parent_app, "Duplicate Name", f"A structure named '{new_name}' already exists.")
        return

    # Generate unique key Structure_xxx
    existing_keys = set(structures.keys())
    existing_nums = []
    for k in existing_keys:
        if k.startswith("Structure_"):
            suffix = k.split("_")[-1]
            if suffix.isdigit():
                existing_nums.append(int(suffix))
    next_num = (max(existing_nums) if existing_nums else len(existing_keys)) + 1
    while f"Structure_{next_num:03d}" in existing_keys:
        next_num += 1
    new_key = f"Structure_{next_num:03d}"

    # Copy 3D mask
    new_mask = np.copy(src_mask)

    # Determine a distinct color from DEFAULT_NEW_COLORS
    src_colors = s_series.get('structures_color', [])
    src_color = src_colors[src_idx] if src_idx < len(src_colors) else "#00E5FF"
    new_color = DEFAULT_NEW_COLORS[0]
    for c in DEFAULT_NEW_COLORS:
        if c.lower() != str(src_color).lower():
            new_color = c
            break

    # Insert into structures dictionary
    structures[new_key] = {
        'Mask3D': new_mask,
        'mask': new_mask,
        'Name': new_name,
        'Modified': 1,
        'Contours2D': {'axial': {}, 'sagittal': {}, 'coronal': {}},
        'VTKActors2D': {}
    }

    s_series.setdefault('structures_keys', []).append(new_key)
    s_series.setdefault('structures_names', []).append(new_name)
    s_series.setdefault('structures_view', []).append(1)
    s_series.setdefault('structures_color', []).append(new_color)
    s_series.setdefault('structures_line_width', []).append(3.0)
    s_series.setdefault('structures_transparency', []).append(0.1)
    s_series.setdefault('structures_mask_transparency', []).append(0.5)

    # Refresh AMIGOpy views
    refresh_amigo_views(parent_app, s_series, patient_id, study_id, modality, series_index)


class BooleanOperationsDialog(QDialog):
    """
    Dialog for performing Boolean operations on 3D contour masks.
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
        self.patient_id = patient_id
        self.study_id = study_id
        self.modality = modality
        self.series_index = series_index
        self.preselected_name = preselected_name

        self.setWindowTitle("Boolean Contour Operations")
        self.resize(760, 680)
        self.setMinimumSize(680, 580)

        # Selected color for new contour
        self._new_color_hex = DEFAULT_NEW_COLORS[0]
        self._user_edited_name = False

        self._setup_style()
        self._init_ui()
        self._populate_series_selector()
        self._load_structures_for_active_series()

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
                color: #90CAF9;
            }
            QComboBox, QLineEdit {
                background-color: #263238;
                color: #FFFFFF;
                border: 1px solid #455A64;
                border-radius: 4px;
                padding: 5px 8px;
                font-size: 12px;
            }
            QComboBox:focus, QLineEdit:focus {
                border: 1px solid #42A5F5;
            }
            QListWidget {
                background-color: #263238;
                color: #ECEFF1;
                border: 1px solid #455A64;
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 4px 6px;
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background-color: #37474F;
            }
            QListWidget::item:selected {
                background-color: #1565C0;
                color: #FFFFFF;
            }
            QRadioButton, QCheckBox {
                color: #ECEFF1;
                font-size: 12px;
                spacing: 6px;
            }
            QPushButton {
                background-color: #37474F;
                color: #ECEFF1;
                border: 1px solid #546E7A;
                border-radius: 4px;
                padding: 5px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #455A64;
                color: #FFFFFF;
            }
            QPushButton#btn_apply {
                background-color: #2E7D32;
                border: 1px solid #388E3C;
                color: #FFFFFF;
                font-size: 13px;
                padding: 8px 24px;
            }
            QPushButton#btn_apply:hover {
                background-color: #388E3C;
            }
            QTextEdit {
                background-color: #12161A;
                color: #81C784;
                border: 1px solid #263238;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(12)

        # ── Header ──
        header_layout = QHBoxLayout()
        icon_lbl = QLabel("📐")
        icon_lbl.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_lbl)

        title_v = QVBoxLayout()
        title_lbl = QLabel("Boolean Contour Operations")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #42A5F5;")
        desc_lbl = QLabel("Combine, subtract, intersect, or isolate 3D contour structures.")
        desc_lbl.setStyleSheet("font-size: 11px; color: #B0BEC5;")
        title_v.addWidget(title_lbl)
        title_v.addWidget(desc_lbl)
        header_layout.addLayout(title_v)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # ── Series Selector ──
        series_box = QHBoxLayout()
        series_box.addWidget(QLabel("<b>Target Series:</b>"))
        self.combo_series = QComboBox()
        self.combo_series.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_series.currentIndexChanged.connect(self._on_series_changed)
        series_box.addWidget(self.combo_series)
        main_layout.addLayout(series_box)

        # ── Middle Pane: Main (left) & Tools (right) via Splitter ──
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(8)

        # Left Column: Main Contour & Operation
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 4, 0)
        left_layout.setSpacing(10)

        # 1. Main Contour Box
        main_group = QGroupBox("1. Main Contour (Base A)")
        mg_layout = QVBoxLayout(main_group)
        mg_layout.setSpacing(6)

        self.combo_main = QComboBox()
        self.combo_main.currentIndexChanged.connect(self._on_main_contour_changed)
        mg_layout.addWidget(self.combo_main)

        self.lbl_main_stats = QLabel("Volume: —")
        self.lbl_main_stats.setStyleSheet("font-size: 11px; color: #90CAF9;")
        mg_layout.addWidget(self.lbl_main_stats)
        left_layout.addWidget(main_group)

        # 2. Boolean Operation Box
        op_group = QGroupBox("2. Operation")
        og_layout = QVBoxLayout(op_group)
        og_layout.setSpacing(8)

        self.op_btn_group = QButtonGroup(self)
        self.rb_union = QRadioButton("➕  Union  (A ∪ B)")
        self.rb_sub = QRadioButton("➖  Subtract  (A - B)")
        self.rb_intersect = QRadioButton("✖️  Intersection  (A ∩ B)")
        self.rb_xor = QRadioButton("🔀  Symmetric Difference  (A ⊕ B)")

        self.op_btn_group.addButton(self.rb_union, 1)
        self.op_btn_group.addButton(self.rb_sub, 2)
        self.op_btn_group.addButton(self.rb_intersect, 3)
        self.op_btn_group.addButton(self.rb_xor, 4)

        # Default to Subtract (most common clinical use case: target minus avoidance / envelope minus inner)
        self.rb_sub.setChecked(True)

        og_layout.addWidget(self.rb_union)
        og_layout.addWidget(self.rb_sub)
        og_layout.addWidget(self.rb_intersect)
        og_layout.addWidget(self.rb_xor)

        self.lbl_op_desc = QLabel()
        self.lbl_op_desc.setWordWrap(True)
        self.lbl_op_desc.setStyleSheet("""
            background-color: #263238;
            border: 1px solid #37474F;
            border-radius: 4px;
            padding: 6px;
            font-size: 11px;
            color: #CFD8DC;
        """)
        og_layout.addWidget(self.lbl_op_desc)
        self.op_btn_group.idToggled.connect(self._on_operation_changed)
        left_layout.addWidget(op_group)
        left_layout.addStretch()

        splitter.addWidget(left_widget)

        # Right Column: Tool Contours
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(4, 0, 0, 0)
        right_layout.setSpacing(6)

        tool_group = QGroupBox("3. Tool Contour(s) (Tools B)")
        tg_layout = QVBoxLayout(tool_group)
        tg_layout.setSpacing(6)

        # Tool Filter & Action row
        tool_top = QHBoxLayout()
        self.tool_filter = QLineEdit()
        self.tool_filter.setPlaceholderText("Filter tool contours…")
        self.tool_filter.textChanged.connect(self._filter_tool_list)
        tool_top.addWidget(self.tool_filter)

        btn_sel_all = QPushButton("All")
        btn_sel_all.setFixedWidth(45)
        btn_sel_all.clicked.connect(lambda: self._set_all_tools(True))
        btn_clear_all = QPushButton("None")
        btn_clear_all.setFixedWidth(45)
        btn_clear_all.clicked.connect(lambda: self._set_all_tools(False))
        tool_top.addWidget(btn_sel_all)
        tool_top.addWidget(btn_clear_all)
        tg_layout.addLayout(tool_top)

        # Tool List Widget
        self.list_tools = QListWidget()
        self.list_tools.itemChanged.connect(self._on_tool_selection_changed)
        tg_layout.addWidget(self.list_tools, 1)

        self.lbl_tool_stats = QLabel("Selected: 0 contours")
        self.lbl_tool_stats.setStyleSheet("font-size: 11px; color: #90CAF9;")
        tg_layout.addWidget(self.lbl_tool_stats)

        right_layout.addWidget(tool_group)
        splitter.addWidget(right_widget)

        splitter.setSizes([340, 380])
        main_layout.addWidget(splitter, 1)

        # ── Output Destination Box ──
        out_group = QGroupBox("4. Output Destination")
        out_layout = QVBoxLayout(out_group)
        out_layout.setSpacing(8)

        # Radio 1: Create New Contour
        r1_layout = QHBoxLayout()
        self.rb_create_new = QRadioButton("Create New Contour:")
        self.rb_create_new.setChecked(True)
        r1_layout.addWidget(self.rb_create_new)

        self.edit_new_name = QLineEdit()
        self.edit_new_name.setPlaceholderText("New contour name…")
        self.edit_new_name.textEdited.connect(self._on_name_manually_edited)
        r1_layout.addWidget(self.edit_new_name, 1)

        self.btn_color = QPushButton("Color")
        self.btn_color.setFixedWidth(75)
        self.btn_color.clicked.connect(self._pick_new_color)
        r1_layout.addWidget(self.btn_color)
        self._update_color_button_swatch()
        out_layout.addLayout(r1_layout)

        # Radio 2: Overwrite Main Contour
        self.rb_overwrite = QRadioButton("Overwrite Main Contour (in-place)")
        out_layout.addWidget(self.rb_overwrite)

        self.out_btn_group = QButtonGroup(self)
        self.out_btn_group.addButton(self.rb_create_new, 1)
        self.out_btn_group.addButton(self.rb_overwrite, 2)
        self.out_btn_group.idToggled.connect(self._on_out_mode_changed)

        main_layout.addWidget(out_group)

        # ── Status / Log Label ──
        self.txt_status = QLabel("Ready. Select main and tool contours then click Calculate.")
        self.txt_status.setStyleSheet("font-size: 11px; color: #81C784; padding: 2px 4px;")
        main_layout.addWidget(self.txt_status)

        # ── Bottom Button Bar ──
        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()

        self.btn_cancel = QPushButton("Close")
        self.btn_cancel.clicked.connect(self.accept)
        bottom_bar.addWidget(self.btn_cancel)

        self.btn_apply = QPushButton("Apply / Calculate")
        self.btn_apply.setObjectName("btn_apply")
        self.btn_apply.clicked.connect(self._execute_boolean)
        bottom_bar.addWidget(self.btn_apply)

        main_layout.addLayout(bottom_bar)

        self._update_operation_description()

    # ── Series & Structure Population ─────────────────────────────────────────

    def _get_active_series_dict(self) -> Optional[Dict]:
        """Fetch the active series dict from parent_app's medical_image."""
        if not self.patient_id or not self.study_id or not self.modality or self.series_index is None:
            return None
        try:
            return self.parent_app.medical_image[self.patient_id][self.study_id][self.modality][self.series_index]
        except (KeyError, IndexError, TypeError):
            return None

    def _populate_series_selector(self):
        """Populate series dropdown with all series containing structures."""
        self.combo_series.blockSignals(True)
        self.combo_series.clear()

        med_img = getattr(self.parent_app, 'medical_image', {}) or {}
        series_found = []

        active_key = (self.patient_id, self.study_id, self.modality, self.series_index)
        match_idx = 0

        for pid, pdata in med_img.items():
            if not isinstance(pdata, dict): continue
            for sid, sdata in pdata.items():
                if not isinstance(sdata, dict): continue
                for mod, mlist in sdata.items():
                    if not isinstance(mlist, list): continue
                    for s_idx, s_entry in enumerate(mlist):
                        if not isinstance(s_entry, dict): continue
                        structs = s_entry.get('structures', {})
                        if structs:
                            desc = s_entry.get('metadata', {}).get('SeriesDescription', '')
                            s_no = s_entry.get('metadata', {}).get('SeriesNumber', s_idx)
                            label = f"[{pid}] {mod} (Series {s_no}) - {desc} ({len(structs)} structures)"
                            data = (pid, sid, mod, s_idx)
                            if data == active_key:
                                match_idx = len(series_found)
                            series_found.append((label, data))

        for label, data in series_found:
            self.combo_series.addItem(label, data)

        if series_found:
            self.combo_series.setCurrentIndex(match_idx)
            cur_data = self.combo_series.currentData()
            if cur_data:
                self.patient_id, self.study_id, self.modality, self.series_index = cur_data

        self.combo_series.blockSignals(False)

    def _on_series_changed(self, idx: int):
        cur_data = self.combo_series.currentData()
        if cur_data:
            self.patient_id, self.study_id, self.modality, self.series_index = cur_data
            self._load_structures_for_active_series()

    def _load_structures_for_active_series(self):
        """Populate Main and Tool contour lists from the current series."""
        s_series = self._get_active_series_dict()
        if not s_series:
            self.combo_main.clear()
            self.list_tools.clear()
            self.txt_status.setText("No structures found for selected series.")
            return

        structures = s_series.get('structures', {})
        names = s_series.get('structures_names', [])
        keys = s_series.get('structures_keys', [])
        colors = s_series.get('structures_color', [])
        md = s_series.get('metadata', {})

        self.combo_main.blockSignals(True)
        self.combo_main.clear()

        preselect_idx = 0
        for i, (name, key) in enumerate(zip(names, keys)):
            color_hex = colors[i] if i < len(colors) else "#FFFFFF"
            icon = create_color_icon(color_hex)
            mask = structures.get(key, {}).get('Mask3D')
            voxels, vol_cc = calculate_mask_volume(mask, md)
            label = f"{name}  ({vol_cc:.2f} cc)"
            self.combo_main.addItem(icon, label, key)
            if self.preselected_name and name.lower() == self.preselected_name.lower():
                preselect_idx = i

        if self.combo_main.count() > 0:
            self.combo_main.setCurrentIndex(preselect_idx)
        self.combo_main.blockSignals(False)

        self._update_main_contour_stats()
        self._rebuild_tool_list()
        self._update_suggested_output_name()

    def _on_main_contour_changed(self, idx: int):
        self._update_main_contour_stats()
        self._rebuild_tool_list()
        self._update_suggested_output_name()

    def _update_main_contour_stats(self):
        s_series = self._get_active_series_dict()
        if not s_series:
            self.lbl_main_stats.setText("Volume: —")
            return
        main_key = self.combo_main.currentData()
        if not main_key:
            self.lbl_main_stats.setText("Volume: —")
            return
        struct_data = s_series.get('structures', {}).get(main_key, {})
        mask = struct_data.get('Mask3D')
        voxels, vol_cc = calculate_mask_volume(mask, s_series.get('metadata', {}))
        self.lbl_main_stats.setText(f"Volume: <b>{vol_cc:.2f} cc</b> ({voxels:,} voxels)")

    def _rebuild_tool_list(self):
        """Rebuild the Tool Contours list widget, excluding the current Main contour."""
        s_series = self._get_active_series_dict()
        if not s_series:
            self.list_tools.clear()
            return

        structures = s_series.get('structures', {})
        names = s_series.get('structures_names', [])
        keys = s_series.get('structures_keys', [])
        colors = s_series.get('structures_color', [])
        md = s_series.get('metadata', {})
        main_key = self.combo_main.currentData()

        # Remember currently checked tool keys
        previously_checked = set()
        for i in range(self.list_tools.count()):
            item = self.list_tools.item(i)
            if item.checkState() == Qt.Checked:
                previously_checked.add(item.data(Qt.UserRole))

        self.list_tools.blockSignals(True)
        self.list_tools.clear()

        for i, (name, key) in enumerate(zip(names, keys)):
            if key == main_key:
                continue  # cannot use main contour as its own tool
            color_hex = colors[i] if i < len(colors) else "#FFFFFF"
            icon = create_color_icon(color_hex)
            mask = structures.get(key, {}).get('Mask3D')
            voxels, vol_cc = calculate_mask_volume(mask, md)

            item = QListWidgetItem(icon, f"{name}  ({vol_cc:.2f} cc)")
            item.setData(Qt.UserRole, key)
            item.setData(Qt.UserRole + 1, name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if key in previously_checked else Qt.Unchecked)
            self.list_tools.addItem(item)

        self.list_tools.blockSignals(False)
        self._filter_tool_list(self.tool_filter.text())
        self._update_tool_stats()

    def _filter_tool_list(self, query: str):
        query = (query or "").strip().lower()
        for i in range(self.list_tools.count()):
            item = self.list_tools.item(i)
            visible = (not query) or (query in item.text().lower())
            item.setHidden(not visible)

    def _set_all_tools(self, state: bool):
        self.list_tools.blockSignals(True)
        for i in range(self.list_tools.count()):
            item = self.list_tools.item(i)
            if not item.isHidden():
                item.setCheckState(Qt.Checked if state else Qt.Unchecked)
        self.list_tools.blockSignals(False)
        self._on_tool_selection_changed(None)

    def _on_tool_selection_changed(self, _):
        self._update_tool_stats()
        self._update_suggested_output_name()

    def _get_selected_tool_keys(self) -> List[str]:
        keys = []
        for i in range(self.list_tools.count()):
            item = self.list_tools.item(i)
            if item.checkState() == Qt.Checked:
                keys.append(item.data(Qt.UserRole))
        return keys

    def _get_selected_tool_names(self) -> List[str]:
        names = []
        for i in range(self.list_tools.count()):
            item = self.list_tools.item(i)
            if item.checkState() == Qt.Checked:
                names.append(item.data(Qt.UserRole + 1))
        return names

    def _update_tool_stats(self):
        s_series = self._get_active_series_dict()
        md = s_series.get('metadata', {}) if s_series else {}
        structs = s_series.get('structures', {}) if s_series else {}

        selected_keys = self._get_selected_tool_keys()
        n = len(selected_keys)

        total_cc = 0.0
        for k in selected_keys:
            mask = structs.get(k, {}).get('Mask3D')
            _, cc = calculate_mask_volume(mask, md)
            total_cc += cc

        if n == 0:
            self.lbl_tool_stats.setText("Selected: 0 tools")
        else:
            self.lbl_tool_stats.setText(f"Selected: <b>{n} tool{'s' if n>1 else ''}</b> (Combined: ~{total_cc:.2f} cc)")

    # ── Operation Handling & Suggested Names ──────────────────────────────────

    def _on_operation_changed(self, *args):
        self._update_operation_description()
        self._update_suggested_output_name()

    def _update_operation_description(self):
        op_id = self.op_btn_group.checkedId()
        if op_id == 1:
            self.lbl_op_desc.setText(
                "<b>Union (A ∪ B)</b>: Combines Main contour with Tool contour(s). "
                "Any voxel inside Main OR Tools will be included."
            )
        elif op_id == 2:
            self.lbl_op_desc.setText(
                "<b>Subtract (A - B)</b>: Carves Tool contour(s) out of the Main contour. "
                "Any overlapping voxels are removed from Main."
            )
        elif op_id == 3:
            self.lbl_op_desc.setText(
                "<b>Intersection (A ∩ B)</b>: Keeps only the overlapping volume between "
                "Main contour and Tool contour(s)."
            )
        elif op_id == 4:
            self.lbl_op_desc.setText(
                "<b>Symmetric Difference (A ⊕ B)</b>: Retains voxels belonging to either "
                "Main or Tools, but excludes their overlap."
            )

    def _on_name_manually_edited(self, text: str):
        self._user_edited_name = bool(text.strip())

    def _update_suggested_output_name(self):
        if self._user_edited_name:
            return  # preserve user custom input

        main_text = self.combo_main.currentText()
        main_name = main_text.split("  (")[0] if main_text else "Contour"

        tool_names = self._get_selected_tool_names()
        if not tool_names:
            tool_suffix = "tool"
        elif len(tool_names) == 1:
            tool_suffix = tool_names[0]
        else:
            tool_suffix = f"{len(tool_names)}tools"

        op_id = self.op_btn_group.checkedId()
        tag = "UNION" if op_id == 1 else "SUB" if op_id == 2 else "INT" if op_id == 3 else "XOR"
        suggested = f"{main_name}_{tag}_{tool_suffix}"
        self.edit_new_name.setText(suggested)

    def _on_out_mode_changed(self, btn_id: int):
        is_new = (btn_id == 1)
        self.edit_new_name.setEnabled(is_new)
        self.btn_color.setEnabled(is_new)
        if not is_new:
            main_name = self.combo_main.currentText().split("  (")[0]
            self.txt_status.setText(f"Warning: Applying will overwrite '{main_name}' directly.")
        else:
            self.txt_status.setText("Ready.")

    def _pick_new_color(self):
        dlg = QColorDialog(QColor(self._new_color_hex), self)
        dlg.setWindowTitle("Select Color for New Contour")
        if dlg.exec():
            c = dlg.selectedColor()
            if c.isValid():
                self._new_color_hex = c.name().upper()
                self._update_color_button_swatch()

    def _update_color_button_swatch(self):
        self.btn_color.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._new_color_hex};
                color: #000000;
                font-weight: bold;
                border: 2px solid #FFFFFF;
                border-radius: 4px;
            }}
        """)

    # ── Execution ─────────────────────────────────────────────────────────────

    def _execute_boolean(self):
        s_series = self._get_active_series_dict()
        if not s_series:
            QMessageBox.warning(self, "Invalid Series", "No active series data found.")
            return

        structures = s_series.get('structures', {})
        main_key = self.combo_main.currentData()
        if not main_key or main_key not in structures:
            QMessageBox.warning(self, "Missing Main Contour", "Please select a valid Main contour.")
            return

        tool_keys = self._get_selected_tool_keys()
        if not tool_keys:
            QMessageBox.warning(self, "Missing Tool Contours", "Please select at least one Tool contour from the list.")
            return

        is_create_new = self.rb_create_new.isChecked()
        new_name = self.edit_new_name.text().strip()
        if is_create_new and not new_name:
            QMessageBox.warning(self, "Missing Name", "Please specify a name for the new contour.")
            return

        # 1. Fetch Main Mask
        mask_main = structures[main_key].get('Mask3D')
        if mask_main is None:
            QMessageBox.warning(self, "Error", f"Could not load 3D mask for main contour '{main_key}'.")
            return

        mask_main_bool = (mask_main > 0)

        # 2. Combine all tool masks
        tools_combined = np.zeros_like(mask_main_bool, dtype=bool)
        for tk in tool_keys:
            t_mask = structures.get(tk, {}).get('Mask3D')
            if t_mask is not None:
                if t_mask.shape != mask_main_bool.shape:
                    QMessageBox.warning(
                        self, "Shape Mismatch",
                        f"Tool mask '{tk}' shape {t_mask.shape} does not match main mask {mask_main_bool.shape}."
                    )
                    return
                tools_combined |= (t_mask > 0)

        # 3. Perform boolean logic
        op_id = self.op_btn_group.checkedId()
        if op_id == 1:    # Union
            res_bool = mask_main_bool | tools_combined
            op_label = "Union"
        elif op_id == 2:  # Subtract
            res_bool = mask_main_bool & (~tools_combined)
            op_label = "Subtraction"
        elif op_id == 3:  # Intersect
            res_bool = mask_main_bool & tools_combined
            op_label = "Intersection"
        elif op_id == 4:  # XOR
            res_bool = mask_main_bool ^ tools_combined
            op_label = "Symmetric Difference"
        else:
            return

        res_uint8 = res_bool.astype(np.uint8)
        voxels, vol_cc = calculate_mask_volume(res_uint8, s_series.get('metadata', {}))

        # 4. Save result
        if is_create_new:
            # Generate unique Structure_xxx key
            existing_keys = set(structures.keys())
            existing_nums = []
            for k in existing_keys:
                if k.startswith("Structure_"):
                    suffix = k.split("_")[-1]
                    if suffix.isdigit():
                        existing_nums.append(int(suffix))
            next_num = (max(existing_nums) if existing_nums else len(existing_keys)) + 1
            while f"Structure_{next_num:03d}" in existing_keys:
                next_num += 1
            new_key = f"Structure_{next_num:03d}"

            # Append to series dictionary structures
            structures[new_key] = {
                'Mask3D': res_uint8,
                'mask': res_uint8,
                'Name': new_name,
                'Modified': 1,
                'Contours2D': {'axial': {}, 'sagittal': {}, 'coronal': {}},
                'VTKActors2D': {}
            }

            s_series.setdefault('structures_keys', []).append(new_key)
            s_series.setdefault('structures_names', []).append(new_name)
            s_series.setdefault('structures_view', []).append(1)  # make visible
            s_series.setdefault('structures_color', []).append(self._new_color_hex)
            s_series.setdefault('structures_line_width', []).append(3.0)
            s_series.setdefault('structures_transparency', []).append(0.1)
            s_series.setdefault('structures_mask_transparency', []).append(0.5)

            msg = f"✓ Created new contour '{new_name}' via {op_label}: {vol_cc:.2f} cc ({voxels:,} voxels)"
            # Cycle to next color for convenience in future operations
            cur_color_idx = DEFAULT_NEW_COLORS.index(self._new_color_hex) if self._new_color_hex in DEFAULT_NEW_COLORS else 0
            self._new_color_hex = DEFAULT_NEW_COLORS[(cur_color_idx + 1) % len(DEFAULT_NEW_COLORS)]
            self._update_color_button_swatch()
            self._user_edited_name = False
        else:
            # Overwrite in-place
            structures[main_key]['Mask3D'] = res_uint8
            structures[main_key]['mask'] = res_uint8
            structures[main_key]['Modified'] = 1
            structures[main_key]['Contours2D'] = {'axial': {}, 'sagittal': {}, 'coronal': {}}
            structures[main_key]['VTKActors2D'] = {}
            main_name = structures[main_key].get('Name', main_key)
            msg = f"✓ Overwrote '{main_name}' via {op_label}: {vol_cc:.2f} cc ({voxels:,} voxels)"

        self.txt_status.setText(msg)

        # 5. Refresh AMIGOpy views & UI components
        refresh_amigo_views(
            self.parent_app, s_series,
            self.patient_id, self.study_id, self.modality, self.series_index
        )

        # 6. Re-populate dialog lists so the user can immediately continue working
        self._load_structures_for_active_series()


def open_boolean_dialog(
    parent_app,
    patient_id: Optional[str] = None,
    study_id: Optional[str] = None,
    modality: Optional[str] = None,
    series_index: Optional[int] = None,
    preselected_name: Optional[str] = None,
):
    """
    Open the Boolean Contour Operations dialog.
    If series params are omitted, defaults to the active series in parent_app.
    """
    # Fallback to parent_app active attributes if not supplied
    if patient_id is None:
        patient_id = getattr(parent_app, 'patientID', None)
    if study_id is None:
        study_id = getattr(parent_app, 'studyID', None)
    if modality is None:
        modality = getattr(parent_app, 'modality', None)
    if series_index is None:
        series_index = getattr(parent_app, 'series_index', None)

    # Check if any structures exist across the entire project
    med_img = getattr(parent_app, 'medical_image', {}) or {}
    has_any_structures = False
    for p in med_img.values():
        if isinstance(p, dict):
            for s in p.values():
                if isinstance(s, dict):
                    for m in s.values():
                        if isinstance(m, list):
                            for ser in m:
                                if isinstance(ser, dict) and ser.get('structures'):
                                    has_any_structures = True
                                    break

    if not has_any_structures:
        QMessageBox.information(
            parent_app, "No Structures Found",
            "No series with contour structures were found in the current project.\n"
            "Please import, segment, or create contour structures first."
        )
        return

    dlg = BooleanOperationsDialog(
        parent_app=parent_app,
        patient_id=patient_id,
        study_id=study_id,
        modality=modality,
        series_index=series_index,
        preselected_name=preselected_name,
    )
    dlg.exec()
