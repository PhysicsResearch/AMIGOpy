# segmentator_ui.py — TotalSegmentator UI with canonical TS labels, grouping, search,
# quick-subgroup checkboxes, and select/unselect all series controls.

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QCheckBox, QHeaderView, QGroupBox,
    QScrollArea, QGridLayout, QDoubleSpinBox, QComboBox, QMessageBox,
    QSplitter, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
import os

# =============== Canonical TS label list (from your ZIP contents) ===============
# NOTE: These are used as the authoritative set for your UI.
TS_ALL_TARGETS = [
    "adrenal_gland_left","adrenal_gland_right","aorta","atrial_appendage_left",
    "autochthon_left","autochthon_right","brachiocephalic_trunk",
    "brachiocephalic_vein_left","brachiocephalic_vein_right","brain",
    "clavicula_left","clavicula_right","colon","common_carotid_artery_left",
    "common_carotid_artery_right","costal_cartilages","duodenum","esophagus",
    "femur_left","femur_right","gallbladder","gluteus_maximus_left",
    "gluteus_maximus_right","gluteus_medius_left","gluteus_medius_right",
    "gluteus_minimus_left","gluteus_minimus_right","heart","hip_left","hip_right",
    "humerus_left","humerus_right","iliac_artery_left","iliac_artery_right",
    "iliac_vena_left","iliac_vena_right","iliopsoas_left","iliopsoas_right",
    "inferior_vena_cava","kidney_cyst_left","kidney_cyst_right","kidney_left",
    "kidney_right","liver","lung_lower_lobe_left","lung_lower_lobe_right",
    "lung_middle_lobe_right","lung_upper_lobe_left","lung_upper_lobe_right",
    "pancreas","portal_vein_and_splenic_vein","prostate","pulmonary_vein",
    "rib_left_1","rib_left_2","rib_left_3","rib_left_4","rib_left_5","rib_left_6",
    "rib_left_7","rib_left_8","rib_left_9","rib_left_10","rib_left_11","rib_left_12",
    "rib_right_1","rib_right_2","rib_right_3","rib_right_4","rib_right_5",
    "rib_right_6","rib_right_7","rib_right_8","rib_right_9","rib_right_10",
    "rib_right_11","rib_right_12","sacrum","scapula_left","scapula_right","skull",
    "small_bowel","spinal_cord","spleen","sternum","stomach",
    "subclavian_artery_left","subclavian_artery_right","superior_vena_cava",
    "thyroid_gland","trachea","urinary_bladder",
    "vertebrae_C1","vertebrae_C2","vertebrae_C3","vertebrae_C4","vertebrae_C5",
    "vertebrae_C6","vertebrae_C7","vertebrae_T1","vertebrae_T2","vertebrae_T3",
    "vertebrae_T4","vertebrae_T5","vertebrae_T6","vertebrae_T7","vertebrae_T8",
    "vertebrae_T9","vertebrae_T10","vertebrae_T11","vertebrae_T12",
    "vertebrae_L1","vertebrae_L2","vertebrae_L3","vertebrae_L4","vertebrae_L5",
    "vertebrae_S1",
]
TS_ALL_SET = set(TS_ALL_TARGETS)

# =============== Quick subgroup (subtask) presets ===============
TS_SUBTASKS = {
    # Thorax / lungs
    "Lung lobes": [
        "lung_upper_lobe_left","lung_upper_lobe_right",
        "lung_middle_lobe_right",
        "lung_lower_lobe_left","lung_lower_lobe_right",
    ],
    "Airways": ["trachea"],
    "Heart + veins (basic)": ["heart","atrial_appendage_left","pulmonary_vein"],

    # Great vessels
    "Great vessels": [
        "aorta","inferior_vena_cava","superior_vena_cava",
        "brachiocephalic_trunk","brachiocephalic_vein_left","brachiocephalic_vein_right",
        "common_carotid_artery_left","common_carotid_artery_right",
        "subclavian_artery_left","subclavian_artery_right",
        "portal_vein_and_splenic_vein",
    ],

    # Abdomen solid organs
    "Liver/Pancreas/Spleen/GB": ["liver","pancreas","spleen","gallbladder"],

    # Kidneys + adrenals
    "Kidneys/Adrenals": [
        "kidney_left","kidney_right","kidney_cyst_left","kidney_cyst_right",
        "adrenal_gland_left","adrenal_gland_right",
    ],

    # GI
    "GI (tube)": ["esophagus","stomach","duodenum","small_bowel","colon"],

    # Pelvis
    "Pelvis (urology)": ["urinary_bladder","prostate"],

    # Muscles (pelvis/hips/back)
    "Pelvis/Back muscles": [
        "iliopsoas_left","iliopsoas_right",
        "gluteus_maximus_left","gluteus_maximus_right",
        "gluteus_medius_left","gluteus_medius_right",
        "gluteus_minimus_left","gluteus_minimus_right",
        "autochthon_left","autochthon_right",
    ],

    # Bones
    "Shoulder girdle": ["clavicula_left","clavicula_right","scapula_left","scapula_right"],
    "Arms": ["humerus_left","humerus_right"],
    "Legs + hips + sacrum": ["femur_left","femur_right","hip_left","hip_right","sacrum"],
    "Skull/Sternum/Cartilage": ["skull","sternum","costal_cartilages"],

    # Vertebrae & ribs
    "Vertebrae (all)": [
        "vertebrae_C1","vertebrae_C2","vertebrae_C3","vertebrae_C4","vertebrae_C5","vertebrae_C6","vertebrae_C7",
        "vertebrae_T1","vertebrae_T2","vertebrae_T3","vertebrae_T4","vertebrae_T5","vertebrae_T6","vertebrae_T7","vertebrae_T8","vertebrae_T9","vertebrae_T10","vertebrae_T11","vertebrae_T12",
        "vertebrae_L1","vertebrae_L2","vertebrae_L3","vertebrae_L4","vertebrae_L5","vertebrae_S1",
    ],
    "Ribs (left all)": [
        "rib_left_1","rib_left_2","rib_left_3","rib_left_4","rib_left_5","rib_left_6",
        "rib_left_7","rib_left_8","rib_left_9","rib_left_10","rib_left_11","rib_left_12",
    ],
    "Ribs (right all)": [
        "rib_right_1","rib_right_2","rib_right_3","rib_right_4","rib_right_5","rib_right_6",
        "rib_right_7","rib_right_8","rib_right_9","rib_right_10","rib_right_11","rib_right_12",
    ],

    # Misc / Endocrine / Neuro
    "Thyroid/Spinal cord/Brain": ["thyroid_gland","spinal_cord","brain"],
}

# =============== Grouping for the right-hand list (visual organization) ===============
_GROUPS = [
    ("Head / Neck", [
        "brain","thyroid_gland","skull","spinal_cord"
    ]),
    ("Thorax", [
        "heart","atrial_appendage_left","trachea","esophagus",
        "aorta","inferior_vena_cava","superior_vena_cava",
        "brachiocephalic_trunk","brachiocephalic_vein_left","brachiocephalic_vein_right",
        "common_carotid_artery_left","common_carotid_artery_right",
        "subclavian_artery_left","subclavian_artery_right",
        "pulmonary_vein",
        "lung_upper_lobe_left","lung_upper_lobe_right","lung_middle_lobe_right",
        "lung_lower_lobe_left","lung_lower_lobe_right",
        "clavicula_left","clavicula_right","scapula_left","scapula_right",
        "sternum","costal_cartilages",
        # ribs are many; handled in separate "Ribs" groups for readability
    ]),
    ("Abdomen", [
        "liver","pancreas","spleen","gallbladder",
        "kidney_left","kidney_right","kidney_cyst_left","kidney_cyst_right",
        "adrenal_gland_left","adrenal_gland_right",
        "stomach","duodenum","small_bowel","colon",
        "portal_vein_and_splenic_vein",
        "iliac_artery_left","iliac_artery_right","iliac_vena_left","iliac_vena_right",
    ]),
    ("Pelvis", [
        "urinary_bladder","prostate",
        "hip_left","hip_right","sacrum",
        "iliopsoas_left","iliopsoas_right",
        "gluteus_maximus_left","gluteus_maximus_right",
        "gluteus_medius_left","gluteus_medius_right",
        "gluteus_minimus_left","gluteus_minimus_right",
        "autochthon_left","autochthon_right",
    ]),
    ("Vertebrae", [
        "vertebrae_C1","vertebrae_C2","vertebrae_C3","vertebrae_C4","vertebrae_C5","vertebrae_C6","vertebrae_C7",
        "vertebrae_T1","vertebrae_T2","vertebrae_T3","vertebrae_T4","vertebrae_T5","vertebrae_T6","vertebrae_T7","vertebrae_T8","vertebrae_T9","vertebrae_T10","vertebrae_T11","vertebrae_T12",
        "vertebrae_L1","vertebrae_L2","vertebrae_L3","vertebrae_L4","vertebrae_L5",
        "vertebrae_S1",
    ]),
    ("Ribs (Left)", [
        "rib_left_1","rib_left_2","rib_left_3","rib_left_4","rib_left_5","rib_left_6",
        "rib_left_7","rib_left_8","rib_left_9","rib_left_10","rib_left_11","rib_left_12",
    ]),
    ("Ribs (Right)", [
        "rib_right_1","rib_right_2","rib_right_3","rib_right_4","rib_right_5","rib_right_6",
        "rib_right_7","rib_right_8","rib_right_9","rib_right_10","rib_right_11","rib_right_12",
    ]),
]

# Any labels not covered above will appear here:
OTHER_GROUP_TITLE = "Other / Ungrouped"


class SegmentatorWindow(QWidget):
    """
    Standalone window for configuring and launching TotalSegmentator workflows.

    Signals:
      - startApiRequested(str host, int port)
      - stopApiRequested()
      - runSegRequested(list series_list, dict params)
    """
    startApiRequested = pyqtSignal(str, int)   # host, port
    stopApiRequested  = pyqtSignal()
    runSegRequested   = pyqtSignal(list, dict)

    def __init__(self, parent=None, dicom_data=None, excluded_modalities=None, data_provider=None):
        super().__init__(None)  # force top-level window
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle("Auto-Contouring (TotalSegmentator)")
        self.setMinimumSize(1320, 820)

        # Global button style: white text on blue background
        self.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #90A4AE;
                color: #ECEFF1;
            }
        """)

        self.dicom_data = dicom_data or {}
        self.excluded_modalities = excluded_modalities or set()
        self.data_provider = data_provider

        self.group_checkboxes = {}   # group -> [QCheckBox...]
        self.label_to_checkbox = {}  # exact TS name -> QCheckBox
        self.series_rows = []        # table bookkeeping

        # ---------- MAIN ----------
        main = QVBoxLayout(self)
        main.setContentsMargins(10, 10, 10, 10)
        main.setSpacing(8)

        # ---- server controls
        server_row = QHBoxLayout(); server_row.setSpacing(8)
        server_row.addWidget(QLabel("Address:"))
        self.addr_edit = QLineEdit("127.0.0.1"); server_row.addWidget(self.addr_edit)
        server_row.addWidget(QLabel("Port:"))
        self.port_edit = QLineEdit("5000"); self.port_edit.setMaximumWidth(90); server_row.addWidget(self.port_edit)

        self.btn_start_api = QPushButton("Start API"); self.btn_start_api.clicked.connect(self._on_start_api)
        self.btn_stop_api  = QPushButton("Stop API");  self.btn_stop_api.setEnabled(False)
        self.btn_stop_api.clicked.connect(lambda: self.stopApiRequested.emit())
        server_row.addWidget(self.btn_start_api); server_row.addWidget(self.btn_stop_api)

        self.api_status = QLabel("Status: Stopped"); server_row.addWidget(self.api_status)
        server_row.addStretch()
        main.addLayout(server_row)

        # ---- options row
        opt_row = QHBoxLayout(); opt_row.setSpacing(12)
        self.chk_fast  = QCheckBox("Fast (--fast)")
        self.chk_merge = QCheckBox("Merge labels (--ml)"); self.chk_merge.setChecked(False)
        opt_row.addWidget(self.chk_fast); opt_row.addWidget(self.chk_merge); opt_row.addSpacing(12)

        opt_row.addWidget(QLabel("Resample (mm):"))
        self.resample_spin = QDoubleSpinBox()
        self.resample_spin.setDecimals(1); self.resample_spin.setMinimum(0.0)
        self.resample_spin.setMaximum(10.0); self.resample_spin.setSingleStep(0.5)
        self.resample_spin.setValue(0.0)
        self.resample_spin.setToolTip("0 = no resampling (fastest). Example: 3.0 speeds up but reduces detail.")
        opt_row.addWidget(self.resample_spin)

        self.chk_no_crop = QCheckBox("Avoid crop (--nr_crop)")
        self.chk_no_crop.setToolTip("Shown for completeness. The server may ignore this if unsupported.")
        opt_row.addWidget(self.chk_no_crop)

        opt_row.addSpacing(20)
        opt_row.addWidget(QLabel("Output type:"))
        self.output_type = QComboBox(); self.output_type.addItems(["nifti", "dicom"])
        opt_row.addWidget(self.output_type)

        opt_row.addStretch()
        main.addLayout(opt_row)

        # ---- splitter area (series left, structures right)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Left pane: series table + refresh + select/unselect all
        left = QWidget(); left_v = QVBoxLayout(left)
        left_v.setContentsMargins(0, 0, 0, 0); left_v.setSpacing(6)
        row_hdr = QHBoxLayout()
        row_hdr.addWidget(QLabel("Select series to send:")); row_hdr.addStretch()
        self.btn_select_all_series = QPushButton("Select All Series")
        self.btn_clear_all_series  = QPushButton("Clear All Series")
        self.btn_refresh_series = QPushButton("Refresh Series")
        self.btn_select_all_series.clicked.connect(lambda: self._select_all_series(True))
        self.btn_clear_all_series.clicked.connect(lambda: self._select_all_series(False))
        self.btn_refresh_series.setToolTip("Reload series list from the app")
        self.btn_refresh_series.clicked.connect(self._reload_series)
        for b in (self.btn_select_all_series, self.btn_clear_all_series, self.btn_refresh_series):
            row_hdr.addWidget(b)
        left_v.addLayout(row_hdr)

        self.tbl = QTableWidget(0, 5)
        self.tbl.setHorizontalHeaderLabels(["Select", "Patient", "Study", "Modality", "Series [index]"])
        self.tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tbl.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.tbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_v.addWidget(self.tbl)

        self._populate_series_table()

        # Right pane: structures with search + quick groups + grouped checkboxes
        right = QWidget(); right_v = QVBoxLayout(right)
        right_v.setContentsMargins(0, 0, 0, 0); right_v.setSpacing(6)

        right_v.addWidget(QLabel("Select structures (TotalSegmentator canonical names):"))

        # search + global controls
        controls = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter labels (e.g., 'lung', 'vertebra')")
        self.search_edit.textChanged.connect(self._apply_filter)
        controls.addWidget(self.search_edit)

        self.btn_select_all = QPushButton("Select All")
        self.btn_clear_all  = QPushButton("Clear All")
        self.btn_select_all.clicked.connect(lambda: self._select_all_labels(True))
        self.btn_clear_all.clicked.connect(lambda: self._select_all_labels(False))
        controls.addWidget(self.btn_select_all)
        controls.addWidget(self.btn_clear_all)
        right_v.addLayout(controls)

        # Quick subgroup presets
        quick = QGroupBox("Quick Groups")
        quick_l = QGridLayout(); quick_l.setHorizontalSpacing(12); quick_l.setVerticalSpacing(6)
        self.quick_checks = {}  # name -> QCheckBox
        col = 0; row = 0
        for name in TS_SUBTASKS.keys():
            cb = QCheckBox(name)
            cb.stateChanged.connect(self._on_quick_group_changed)
            self.quick_checks[name] = cb
            quick_l.addWidget(cb, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1
        quick.setLayout(quick_l)
        right_v.addWidget(quick)

        # scrollable groups
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        holder = QWidget(); self.scroll.setWidget(holder)
        self.groups_layout = QVBoxLayout(holder)
        self.groups_layout.setContentsMargins(6, 6, 6, 6); self.groups_layout.setSpacing(8)

        self._build_groups_with_labels()

        right_v.addWidget(self.scroll)

        splitter.addWidget(left); splitter.addWidget(right)
        splitter.setStretchFactor(0, 1); splitter.setStretchFactor(1, 1)
        splitter.setSizes([720, 720])
        main.addWidget(splitter)

        # ---- actions row
        bottom = QHBoxLayout()
        self.btn_run = QPushButton("Run Segmentation")
        self.btn_run.clicked.connect(self._on_run_clicked)
        bottom.addStretch(); bottom.addWidget(self.btn_run)
        main.addLayout(bottom)

        # Stretch behavior
        main.setStretch(0, 0)  # server
        main.setStretch(1, 0)  # options
        main.setStretch(2, 1)  # splitter
        main.setStretch(3, 0)  # bottom

    # -------------------- series table --------------------
    def _reload_series(self):
        try:
            if callable(self.data_provider):
                new_data = self.data_provider()
                if new_data is not None:
                    self.dicom_data = new_data
        except Exception as e:
            QMessageBox.warning(self, "Refresh failed", f"Could not refresh series:\n{e}")
            return
        self._populate_series_table()

    def _populate_series_table(self):
        self.tbl.setRowCount(0)
        self.series_rows.clear()
        rows = []
        for pid in sorted(self.dicom_data.keys()):
            for study_id, study_data in self.dicom_data[pid].items():
                for modality, series_list in study_data.items():
                    if modality in self.excluded_modalities:
                        continue
                    for item_index, series_data in enumerate(series_list):
                        series_label = self._build_series_label(modality, series_data)
                        label_with_idx = f"{series_label} [{item_index}]"
                        rows.append((pid, study_id, modality, item_index, label_with_idx))

        self.tbl.setRowCount(len(rows))
        for r, (pid, study, mod, idx, label) in enumerate(rows):
            cb = QCheckBox(); self.tbl.setCellWidget(r, 0, cb)
            it_p = QTableWidgetItem(pid);   it_p.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            it_s = QTableWidgetItem(study); it_s.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            it_m = QTableWidgetItem(mod);   it_m.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            it_l = QTableWidgetItem(label); it_l.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.tbl.setItem(r, 1, it_p); self.tbl.setItem(r, 2, it_s)
            self.tbl.setItem(r, 3, it_m); self.tbl.setItem(r, 4, it_l)
            self.series_rows.append({
                "row": r, "patient": pid, "study": study, "modality": mod, "index": idx, "label": label
            })

    def _build_series_label(self, modality, series_data):
        md = series_data.get('metadata', {})
        if modality not in {'RTPLAN','RTSTRUCT','RTDOSE'}:
            acq = md.get('AcquisitionNumber', 'NA')
            base = f"Acq_{acq}_Series: {series_data.get('SeriesNumber','?')}"
            if md.get('LUTLabel', 'N/A') != 'N/A':
                base += f" {md.get('LUTLabel','')} {md.get('LUTExplanation','')}"
            return base.strip()
        return f"{modality}_Series: {series_data.get('SeriesNumber','?')}"

    def _select_all_series(self, state: bool):
        for meta in self.series_rows:
            cb = self.tbl.cellWidget(meta["row"], 0)
            if cb:
                cb.setChecked(state)

    def get_selected_series(self):
        selected = []
        for meta in self.series_rows:
            cb = self.tbl.cellWidget(meta["row"], 0)
            if cb and cb.isChecked():
                selected.append({k: meta[k] for k in ("patient","study","modality","index","label")})
        return selected

    # -------------------- structures UI --------------------
    def _build_groups_with_labels(self):
        covered = set()
        for group_title, labels in _GROUPS:
            labs = [lab for lab in labels if lab in TS_ALL_SET]
            if labs:
                self._add_contour_group(group_title, sorted(labs))
                covered.update(labs)

        # Ribs & Vertebrae already handled. Add any remaining labels to "Other"
        remaining = sorted([lab for lab in TS_ALL_TARGETS if lab not in covered])
        if remaining:
            self._add_contour_group(OTHER_GROUP_TITLE, remaining)

    def _add_contour_group(self, title, labels):
        group = QGroupBox(title)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        outer = QVBoxLayout(); outer.setSpacing(6)
        header = QHBoxLayout()
        header.addWidget(QLabel(f"<b>{title}</b>"))
        header.addStretch()
        btn_toggle = QPushButton("Check All"); btn_toggle.setFixedWidth(110)
        header.addWidget(btn_toggle)
        outer.addLayout(header)

        grid = QGridLayout(); grid.setHorizontalSpacing(18); grid.setVerticalSpacing(4)
        cbs = []
        # 2 columns for readability
        for i, lab in enumerate(labels):
            cb = QCheckBox(lab)  # lab is the EXACT TS name
            cbs.append(cb)
            self.label_to_checkbox[lab] = cb
            grid.addWidget(cb, i // 2, i % 2)
        outer.addLayout(grid)

        group.setLayout(outer)
        self.groups_layout.addWidget(group)
        self.group_checkboxes[title] = cbs

        # toggle all for this group
        def toggle():
            all_on = all(cb.isChecked() for cb in cbs)
            for cb in cbs:
                cb.setChecked(not all_on)
            btn_toggle.setText("Uncheck All" if not all_on else "Check All")
        # Simpler, robust version:
        def toggle_simple():
            all_on = all(cb.isChecked() for cb in cbs)
            for cb in cbs:
                cb.setChecked(not all_on)
            btn_toggle.setText("Uncheck All" if not all_on else "Check All")
        btn_toggle.clicked.connect(toggle_simple)

    def _apply_filter(self, text: str):
        pat = text.strip().lower()
        for lab, cb in self.label_to_checkbox.items():
            show = (pat in lab.lower()) if pat else True
            cb.setVisible(show)

    def _select_all_labels(self, state: bool):
        for cb in self.label_to_checkbox.values():
            if cb.isVisible():  # respect current filter
                cb.setChecked(state)

    # Quick groups behavior
    def _on_quick_group_changed(self, *_):
        # Clear all visible first? No—act as additive toggles:
        # if a quick group is checked, ensure its labels are checked;
        # if unchecked, uncheck its labels.
        for name, cb in self.quick_checks.items():
            labs = TS_SUBTASKS.get(name, [])
            for lab in labs:
                w = self.label_to_checkbox.get(lab)
                if w and w.isVisible():
                    w.setChecked(cb.isChecked())

    def get_selected_labels(self):
        return [lab for lab, cb in self.label_to_checkbox.items() if cb.isChecked() and cb.isVisible()]

    # -------------------- params + actions --------------------
    def build_params(self):
        """
        Build a dict for the caller:
          fast -> --fast
          merge_labels -> --ml
          resample -> --resample <mm>
          no_crop -> --nr_crop (may be ignored by server)
          output_type -> 'nifti' or 'dicom'
          targets -> exact TS names (list)
        """
        params = {}
        if self.chk_fast.isChecked():        params["fast"] = True
        if self.chk_merge.isChecked():       params["merge_labels"] = True
        rs = float(self.resample_spin.value())
        if rs > 0:                           params["resample"] = rs
        if self.chk_no_crop.isChecked():     params["no_crop"] = True
        out_t = self.output_type.currentText().strip().lower()
        if out_t:                            params["output_type"] = out_t

        targets = self.get_selected_labels()
        if targets:                          params["targets"] = targets
        return params

    def set_api_running(self, running: bool):
        self.btn_start_api.setEnabled(not running)
        self.btn_stop_api.setEnabled(running)
        self.addr_edit.setEnabled(not running)
        self.port_edit.setEnabled(not running)
        self.api_status.setText("Status: Running" if running else "Status: Stopped")

    def _on_start_api(self):
        host = self.addr_edit.text().strip() or "127.0.0.1"
        try:
            port = int(self.port_edit.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Invalid port", "Port must be an integer.")
            return
        self.startApiRequested.emit(host, port)

    def _on_run_clicked(self):
        series = self.get_selected_series()
        if not series:
            QMessageBox.information(self, "Nothing selected", "Please select at least one series.")
            return

        params = self.build_params()
        if "targets" not in params or not params["targets"]:
            reply = QMessageBox.question(
                self, "No structures selected",
                "No structures were selected. Run with ALL available structures?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # select all visible boxes (respecting filter)
                self._select_all_labels(True)
                params = self.build_params()
            else:
                return

        self.runSegRequested.emit(series, params)
