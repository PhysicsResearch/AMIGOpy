# fcn_autocont/segmentator_ui.py
# -*- coding: utf-8 -*-
"""
Auto-Contouring (TotalSegmentator) UI (embedded/no-server)
- Right pane is a single scrollable column: Sub-routines, CT section, MR section (no visual overlap)
- Each section has its own tall scroll area for labels with larger checkboxes
- Series table (left) with per-row progress
- Run / Stop buttons
Signals:
    runSegRequested(list series, dict params)
    stopRequested()
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QScrollArea, QGridLayout,
    QDoubleSpinBox, QComboBox, QMessageBox, QSplitter, QSizePolicy, QProgressBar
)

# ---------------------------------------------------------------------------
# TUNABLE HEIGHTS
MINH_QUICK       = 160   # Quick-groups scroll height
MINH_CT_GROUPS   = 520   # CT structures groups scroll height
MINH_MR_GROUPS   = 520   # MR structures groups scroll height
COLS_PER_GROUP   = 3     # columns for each label grid
# ---------------------------------------------------------------------------

# ------------------------------- Sub-routines -------------------------------

SUBROUTINE_KEYS = [
    "lung_vessels",
    "body", "body_mr",
    "cerebral_bleed",
    "hip_implant",
    "head_glands_cavities",
    "head_muscles",
    "headneck_bones_vessels",
    "oculomotor_muscles",
    "breasts",
    "liver_segments", "liver_segments_mr",
    "abdominal_muscles",
]

# ------------------------------- CT structures ------------------------------

CT_ALL_TARGETS = [
    "spleen","kidney_right","kidney_left","gallbladder","liver","stomach","pancreas",
    "adrenal_gland_right","adrenal_gland_left",
    "lung_upper_lobe_left","lung_lower_lobe_left","lung_upper_lobe_right",
    "lung_middle_lobe_right","lung_lower_lobe_right",
    "esophagus","trachea","thyroid_gland","small_bowel","duodenum","colon",
    "urinary_bladder","prostate",
    "kidney_cyst_left","kidney_cyst_right",
    "sacrum","vertebrae_S1","vertebrae_L5","vertebrae_L4","vertebrae_L3","vertebrae_L2",
    "vertebrae_L1","vertebrae_T12","vertebrae_T11","vertebrae_T10","vertebrae_T9",
    "vertebrae_T8","vertebrae_T7","vertebrae_T6","vertebrae_T5","vertebrae_T4",
    "vertebrae_T3","vertebrae_T2","vertebrae_T1","vertebrae_C7","vertebrae_C6",
    "vertebrae_C5","vertebrae_C4","vertebrae_C3","vertebrae_C2","vertebrae_C1",
    "heart","aorta","pulmonary_vein","brachiocephalic_trunk",
    "subclavian_artery_right","subclavian_artery_left",
    "common_carotid_artery_right","common_carotid_artery_left",
    "brachiocephalic_vein_left","brachiocephalic_vein_right",
    "atrial_appendage_left","superior_vena_cava","inferior_vena_cava",
    "portal_vein_and_splenic_vein",
    "iliac_artery_left","iliac_artery_right","iliac_vena_left","iliac_vena_right",
    "humerus_left","humerus_right","scapula_left","scapula_right",
    "clavicula_left","clavicula_right","femur_left","femur_right",
    "hip_left","hip_right","spinal_cord",
    "gluteus_maximus_left","gluteus_maximus_right",
    "gluteus_medius_left","gluteus_medius_right",
    "gluteus_minimus_left","gluteus_minimus_right",
    "autochthon_left","autochthon_right","iliopsoas_left","iliopsoas_right",
    "brain","skull",
    "rib_left_1","rib_left_2","rib_left_3","rib_left_4","rib_left_5","rib_left_6",
    "rib_left_7","rib_left_8","rib_left_9","rib_left_10","rib_left_11","rib_left_12",
    "rib_right_1","rib_right_2","rib_right_3","rib_right_4","rib_right_5","rib_right_6",
    "rib_right_7","rib_right_8","rib_right_9","rib_right_10","rib_right_11","rib_right_12",
    "sternum","costal_cartilages",
]
CT_SET = set(CT_ALL_TARGETS)

CT_GROUPS: List[Tuple[str, List[str]]] = [
    ("Head / Neck", ["brain","thyroid_gland","skull","spinal_cord"]),
    ("Thorax", [
        "heart","atrial_appendage_left","trachea","esophagus",
        "aorta","inferior_vena_cava","superior_vena_cava",
        "brachiocephalic_trunk","brachiocephalic_vein_left","brachiocephalic_vein_right",
        "common_carotid_artery_left","common_carotid_artery_right",
        "subclavian_artery_left","subclavian_artery_right","pulmonary_vein",
        "lung_upper_lobe_left","lung_upper_lobe_right","lung_middle_lobe_right",
        "lung_lower_lobe_left","lung_lower_lobe_right",
        "clavicula_left","clavicula_right","scapula_left","scapula_right",
        "sternum","costal_cartilages",
    ]),
    ("Abdomen", [
        "liver","pancreas","spleen","gallbladder",
        "kidney_left","kidney_right","kidney_cyst_left","kidney_cyst_right",
        "adrenal_gland_left","adrenal_gland_right",
        "stomach","duodenum","small_bowel","colon",
        "portal_vein_and_splenic_vein",
        "iliac_artery_left","iliac_artery_right","iliac_vena_left","iliac_vena_right",
    ]),
    ("Pelvis & Muscles", [
        "urinary_bladder","prostate","hip_left","hip_right","sacrum",
        "iliopsoas_left","iliopsoas_right",
        "gluteus_maximus_left","gluteus_maximus_right",
        "gluteus_medius_left","gluteus_medius_right",
        "gluteus_minimus_left","gluteus_minimus_right",
        "autochthon_left","autochthon_right",
    ]),
    ("Vertebrae", [
        "vertebrae_C1","vertebrae_C2","vertebrae_C3","vertebrae_C4","vertebrae_C5","vertebrae_C6","vertebrae_C7",
        "vertebrae_T1","vertebrae_T2","vertebrae_T3","vertebrae_T4","vertebrae_T5","vertebrae_T6","vertebrae_T7","vertebrae_T8","vertebrae_T9","vertebrae_T10","vertebrae_T11","vertebrae_T12",
        "vertebrae_L1","vertebrae_L2","vertebrae_L3","vertebrae_L4","vertebrae_L5","vertebrae_S1",
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

CT_QUICK = {
    "Lungs + Heart": [
        "lung_upper_lobe_left","lung_upper_lobe_right","lung_middle_lobe_right",
        "lung_lower_lobe_left","lung_lower_lobe_right","heart","pulmonary_vein",
    ],
    "Great vessels": [
        "aorta","inferior_vena_cava","superior_vena_cava",
        "brachiocephalic_trunk","brachiocephalic_vein_left","brachiocephalic_vein_right",
        "common_carotid_artery_left","common_carotid_artery_right",
        "subclavian_artery_left","subclavian_artery_right",
        "portal_vein_and_splenic_vein",
    ],
    "Abd solid organs": ["liver","pancreas","spleen","gallbladder"],
    "Pelvis muscles": [
        "iliopsoas_left","iliopsoas_right","gluteus_maximus_left","gluteus_maximus_right",
        "gluteus_medius_left","gluteus_medius_right",
        "gluteus_minimus_left","gluteus_minimus_right","autochthon_left","autochthon_right",
    ],
}

# ------------------------------- MR structures ------------------------------

MR_ALL_TARGETS = [
    "spleen","kidney_right","kidney_left","gallbladder","liver","stomach","pancreas",
    "adrenal_gland_right","adrenal_gland_left","lung_left","lung_right","esophagus",
    "small_bowel","duodenum","colon","urinary_bladder","prostate","sacrum","vertebrae",
    "intervertebral_discs","spinal_cord","heart","aorta","inferior_vena_cava",
    "portal_vein_and_splenic_vein","iliac_artery_left","iliac_artery_right",
    "iliac_vena_left","iliac_vena_right","humerus_left","humerus_right","scapula_left",
    "scapula_right","clavicula_left","clavicula_right","femur_left","femur_right",
    "hip_left","hip_right","gluteus_maximus_left","gluteus_maximus_right",
    "gluteus_medius_left","gluteus_medius_right","gluteus_minimus_left",
    "gluteus_minimus_right","autochthon_left","autochthon_right","iliopsoas_left",
    "iliopsoas_right","brain",
]
MR_SET = set(MR_ALL_TARGETS)

MR_GROUPS: List[Tuple[str, List[str]]] = [
    ("Head / Neck", ["brain"]),
    ("Thorax", ["heart","aorta","inferior_vena_cava","esophagus","lung_left","lung_right"]),
    ("Abdomen", [
        "liver","pancreas","spleen","gallbladder",
        "kidney_left","kidney_right",
        "adrenal_gland_left","adrenal_gland_right",
        "stomach","duodenum","small_bowel","colon",
        "portal_vein_and_splenic_vein",
    ]),
    ("Spine", ["spinal_cord","vertebrae","intervertebral_discs"]),
    ("Pelvis & Muscles", [
        "urinary_bladder","prostate","hip_left","hip_right","sacrum",
        "iliopsoas_left","iliopsoas_right",
        "gluteus_maximus_left","gluteus_maximus_right",
        "gluteus_medius_left","gluteus_medius_right",
        "gluteus_minimus_left","gluteus_minimus_right",
        "autochthon_left","autochthon_right",
    ]),
    ("Shoulder girdle / limbs", [
        "clavicula_left","clavicula_right","scapula_left","scapula_right",
        "humerus_left","humerus_right","femur_left","femur_right",
    ]),
]

MR_QUICK = {
    "Lungs + Heart": ["lung_left","lung_right","heart"],
    "Abd solid organs": ["liver","pancreas","spleen","gallbladder","kidney_left","kidney_right"],
    "Pelvis muscles": [
        "iliopsoas_left","iliopsoas_right",
        "gluteus_maximus_left","gluteus_maximus_right",
        "gluteus_medius_left","gluteus_medius_right",
        "gluteus_minimus_left","gluteus_minimus_right","autochthon_left","autochthon_right"
    ],
    "Spine core": ["spinal_cord","vertebrae","intervertebral_discs"],
}

# ---------------------------------------------------------------------------

class SegmentatorWindow(QWidget):
    runSegRequested = pyqtSignal(list, dict)
    stopRequested   = pyqtSignal()

    def __init__(self, parent=None, dicom_data=None, excluded_modalities=None, data_provider=None):
        super().__init__(None)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle("Auto-Contouring (TotalSegmentator)")
        self.setMinimumSize(1320, 820)

        self.setStyleSheet("""
            QPushButton {
                background-color: #1976D2; color: white; padding: 6px 12px;
                border-radius: 6px; font-weight: 600;
            }
            QPushButton:hover { background-color: #1565C0; }
            QPushButton:disabled { background-color: #90A4AE; color: #ECEFF1; }
            QCheckBox { font-size: 12px; }
        """)

        self.dicom_data = dicom_data or {}
        self.excluded_modalities = excluded_modalities or set()
        self.data_provider = data_provider

        self.series_rows: List[Dict] = []
        self.ct_label_to_cb: Dict[str, QCheckBox] = {}
        self.mr_label_to_cb: Dict[str, QCheckBox] = {}
        self.subr_cb: Dict[str, QCheckBox] = {}

        main = QVBoxLayout(self); main.setContentsMargins(10,10,10,10); main.setSpacing(8)

        # ---- options row (embedded: no host/port)
        opt = QHBoxLayout(); opt.setSpacing(12)
        self.chk_fast  = QCheckBox("Fast (--fast)")
        self.chk_merge = QCheckBox("Merge labels (--ml)")
        opt.addWidget(self.chk_fast); opt.addWidget(self.chk_merge)

        opt.addSpacing(12); opt.addWidget(QLabel("Resample (mm):"))
        self.resample_spin = QDoubleSpinBox()
        self.resample_spin.setDecimals(1); self.resample_spin.setRange(0.0, 10.0)
        self.resample_spin.setSingleStep(0.5); self.resample_spin.setValue(0.0)
        opt.addWidget(self.resample_spin)

        self.chk_no_crop = QCheckBox("Avoid crop (--nr_crop)")
        opt.addWidget(self.chk_no_crop)

        opt.addSpacing(20); opt.addWidget(QLabel("Output type:"))
        self.output_type = QComboBox(); self.output_type.addItems(["nifti","dicom"])
        opt.addWidget(self.output_type)
        opt.addStretch()
        main.addLayout(opt)

        # ---- splitter: left (series) / right (scrollable column)
        splitter = QSplitter(Qt.Horizontal); splitter.setHandleWidth(8)
        splitter.setChildrenCollapsible(False)
        main.addWidget(splitter, 1)

        # LEFT: series table
        left = QWidget(); lv = QVBoxLayout(left); lv.setContentsMargins(0,0,0,0); lv.setSpacing(6)
        hdr = QHBoxLayout(); hdr.addWidget(QLabel("Series:")); hdr.addStretch()
        for txt, slot in [
            ("Select All", lambda: self._select_all_series(True)),
            ("Clear All",  lambda: self._select_all_series(False)),
            ("Refresh",    self._reload_series),
        ]:
            b = QPushButton(txt); b.clicked.connect(slot); hdr.addWidget(b)
        lv.addLayout(hdr)

        self.tbl = QTableWidget(0, 6)
        self.tbl.setHorizontalHeaderLabels(["Select","Patient","Study","Modality","Series [index]","Status"])
        self.tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tbl.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.tbl.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        lv.addWidget(self.tbl, 1)
        self._populate_series_table()
        splitter.addWidget(left)

        # RIGHT: a SINGLE scroll area with a vertical column (prevents overlap)
        right_container = QWidget()
        right_v = QVBoxLayout(right_container); right_v.setContentsMargins(0,0,0,0); right_v.setSpacing(6)

        # Sub-routines
        right_v.addWidget(self._build_subroutine_box())

        # CT section
        ct_box, self.ct_search, _ = self._build_structures_section(
            title="CT Total — pick structures (auto-enables CT task if any selected)",
            all_targets=CT_ALL_TARGETS, groups=CT_GROUPS, quick=CT_QUICK,
            search_ph="Filter CT labels...", min_groups_height=MINH_CT_GROUPS, target_map="ct"
        )
        right_v.addWidget(ct_box)

        # MR section
        mr_box, self.mr_search, _ = self._build_structures_section(
            title="MR Total — pick structures (auto-enables MR task if any selected)",
            all_targets=MR_ALL_TARGETS, groups=MR_GROUPS, quick=MR_QUICK,
            search_ph="Filter MR labels...", min_groups_height=MINH_MR_GROUPS, target_map="mr"
        )
        right_v.addWidget(mr_box)

        right_v.addStretch(1)  # spacer at end so content stacks nicely

        # Scroll wrapper for the whole right column
        right_scroll = QScrollArea(); right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(right_container)

        # Right side composite (scroll + buttons row)
        right_side = QWidget(); rsv = QVBoxLayout(right_side)
        rsv.setContentsMargins(0,0,0,0); rsv.setSpacing(8)
        rsv.addWidget(right_scroll, 1)

        # Run / Stop buttons
        bottom = QHBoxLayout(); bottom.addStretch()
        self.btn_stop = QPushButton("Stop"); self.btn_stop.setEnabled(False)
        self.btn_run  = QPushButton("Run Segmentation")
        self.btn_stop.clicked.connect(lambda: self.stopRequested.emit())
        self.btn_run.clicked.connect(self._on_run_clicked)
        bottom.addWidget(self.btn_stop); bottom.addWidget(self.btn_run)
        rsv.addLayout(bottom)

        splitter.addWidget(right_side)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([700, 900])

    # --------------------------- Subroutine block ---------------------------

    def _build_subroutine_box(self) -> QGroupBox:
        box = QGroupBox("Sub-routines")
        v = QVBoxLayout(box); v.setContentsMargins(10,8,10,8); v.setSpacing(6)

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(140)
        holder = QWidget(); grid = QGridLayout(holder)
        grid.setHorizontalSpacing(18); grid.setVerticalSpacing(6)
        scroll.setWidget(holder)

        col = row = 0
        for key in SUBROUTINE_KEYS:
            cb = QCheckBox(key.replace("_"," "))
            self.subr_cb[key] = cb
            grid.addWidget(cb, row, col)
            col += 1
            if col >= 4:
                col = 0; row += 1

        v.addWidget(scroll)
        return box

    # --------------------------- Structures sections ------------------------

    def _build_structures_section(
        self, title: str, all_targets: List[str],
        groups: List[Tuple[str, List[str]]],
        quick: Dict[str, List[str]],
        search_ph: str, min_groups_height: int, target_map: str
    ):
        box = QGroupBox(title)
        v = QVBoxLayout(box); v.setContentsMargins(10,8,10,8); v.setSpacing(6)

        # Search + select all/clear all
        r = QHBoxLayout()
        search = QLineEdit(); search.setPlaceholderText(search_ph); r.addWidget(search, 1)
        btn_all  = QPushButton("Select All"); btn_none = QPushButton("Clear All")
        r.addWidget(btn_all); r.addWidget(btn_none)
        v.addLayout(r)

        # Quick groups
        quick_box = QGroupBox("Quick Groups")
        quick_scroll = QScrollArea(); quick_scroll.setWidgetResizable(True)
        quick_scroll.setMinimumHeight(MINH_QUICK)
        q_holder = QWidget(); q_grid = QGridLayout(q_holder)
        q_grid.setHorizontalSpacing(18); q_grid.setVerticalSpacing(6)
        quick_scroll.setWidget(q_holder)

        quick_map: Dict[str, QCheckBox] = {}
        col = row = 0
        for name in quick.keys():
            cb = QCheckBox(name); quick_map[name] = cb
            q_grid.addWidget(cb, row, col)
            col += 1
            if col >= 3:
                col = 0; row += 1

        q_wrap = QVBoxLayout(quick_box); q_wrap.addWidget(quick_scroll)
        v.addWidget(quick_box)

        # MAIN structures groups
        groups_scroll = QScrollArea(); groups_scroll.setWidgetResizable(True)
        groups_scroll.setMinimumHeight(min_groups_height)
        groups_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        holder = QWidget(); holder_layout = QVBoxLayout(holder)
        holder_layout.setContentsMargins(6,6,6,6); holder_layout.setSpacing(8)
        groups_scroll.setWidget(holder)
        v.addWidget(groups_scroll)

        label_to_cb: Dict[str,QCheckBox] = {}
        for gtitle, labels in groups:
            labs = [x for x in labels if x in set(all_targets)]
            if not labs:
                continue
            grp = QGroupBox(gtitle)
            glay = QVBoxLayout(grp); glay.setSpacing(6)
            header = QHBoxLayout(); header.addWidget(QLabel(f"<b>{gtitle}</b>")); header.addStretch()
            toggle = QPushButton("Check All"); toggle.setFixedWidth(110); header.addWidget(toggle)
            glay.addLayout(header)

            grid = QGridLayout(); grid.setHorizontalSpacing(18); grid.setVerticalSpacing(6)
            for i, lab in enumerate(labs):
                cb = QCheckBox(lab)
                label_to_cb[lab] = cb
                grid.addWidget(cb, i // COLS_PER_GROUP, i % COLS_PER_GROUP)
            glay.addLayout(grid)

            def make_toggle(cbs: List[QCheckBox], btn: QPushButton):
                def _t():
                    all_on = all(c.isChecked() for c in cbs)
                    for c in cbs:
                        c.setChecked(not all_on)
                    btn.setText("Uncheck All" if not all_on else "Check All")
                return _t
            toggle.clicked.connect(make_toggle([label_to_cb[x] for x in labs], toggle))

            holder_layout.addWidget(grp)

        # search filter
        def _apply_filter(text: str):
            pat = (text or "").strip().lower()
            for lab, cb in label_to_cb.items():
                cb.setVisible(pat in lab.lower() if pat else True)
        search.textChanged.connect(_apply_filter)

        # select all/none (respect filter)
        def _set_all(state: bool):
            pat = (search.text() or "").strip().lower()
            for lab, cb in label_to_cb.items():
                if (not pat) or (pat in lab.lower()):
                    cb.setChecked(state)
        btn_all.clicked.connect(lambda: _set_all(True))
        btn_none.clicked.connect(lambda: _set_all(False))

        # Quick toggles
        def _quick_changed():
            for name, cb in quick_map.items():
                for lab in quick.get(name, []):
                    w = label_to_cb.get(lab)
                    if w:
                        w.setChecked(cb.isChecked())
        for cb in quick_map.values():
            cb.stateChanged.connect(_quick_changed)

        if target_map == "ct":
            self.ct_label_to_cb = label_to_cb
        else:
            self.mr_label_to_cb = label_to_cb

        return box, search, groups_scroll

    # --------------------------- Series table ops ---------------------------

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
        self.tbl.setRowCount(0); self.series_rows.clear()
        rows = []
        for pid, studies in sorted(self.dicom_data.items()):
            for study_id, by_mod in studies.items():
                for modality, series_list in by_mod.items():
                    if modality in (self.excluded_modalities or set()):
                        continue
                    for idx, s in enumerate(series_list):
                        label = self._series_label(modality, s)
                        rows.append((pid, study_id, modality, idx, f"{label} [{idx}]"))

        self.tbl.setRowCount(len(rows))
        for r, (pid, study, mod, idx, label) in enumerate(rows):
            cb = QCheckBox(); self.tbl.setCellWidget(r, 0, cb)
            for col, val in enumerate([pid, study, mod, label], start=1):
                it = QTableWidgetItem(val); it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.tbl.setItem(r, col, it)
            pgb = QProgressBar(); pgb.setRange(0, 100); pgb.setValue(0); pgb.setTextVisible(False)
            self.tbl.setCellWidget(r, 5, pgb)

            self.series_rows.append({
                "row": r, "patient": pid, "study": study, "modality": mod, "index": idx,
                "label": label, "pgb": pgb, "chk": cb
            })

    def _series_label(self, modality, series_data) -> str:
        md = series_data.get('metadata', {})
        if modality not in {'RTPLAN','RTSTRUCT','RTDOSE'}:
            acq = md.get('AcquisitionNumber', 'NA')
            base = f"Acq_{acq}_Series: {series_data.get('SeriesNumber','?')}"
            ll, le = md.get('LUTLabel',''), md.get('LUTExplanation','')
            if ll or le: base += f" {ll} {le}"
            return base.strip()
        return f"{modality}_Series: {series_data.get('SeriesNumber','?')}"

    def _select_all_series(self, state: bool):
        for meta in self.series_rows:
            cb = meta.get("chk")
            if cb:
                cb.setChecked(state)

    def get_selected_series(self) -> List[Dict]:
        selected = []
        for meta in self.series_rows:
            cb = meta.get("chk")
            if cb and cb.isChecked():
                selected.append({k: meta[k] for k in ("patient","study","modality","index","label")})
        return selected

    # --------------------------- Params + actions ---------------------------

    def _selected_labels(self, mapping: Dict[str,QCheckBox]) -> List[str]:
        return [lab for lab, cb in mapping.items() if cb.isChecked() and cb.isVisible()]

    def build_params(self) -> Dict:
        params: Dict = {}
        if self.chk_fast.isChecked():        params["fast"] = True
        if self.chk_merge.isChecked():       params["merge_labels"] = True
        rs = float(self.resample_spin.value())
        if rs > 0:                           params["resample"] = rs
        if self.chk_no_crop.isChecked():     params["no_crop"] = True
        params["output_type"] = self.output_type.currentText().strip().lower()

        params["subroutines"] = [k for k, cb in self.subr_cb.items() if cb.isChecked()]

        ct_targets = self._selected_labels(self.ct_label_to_cb)
        mr_targets = self._selected_labels(self.mr_label_to_cb)
        params["ct_targets"] = ct_targets
        params["mr_targets"] = mr_targets

        tasks = []
        if ct_targets: tasks.append("total")
        if mr_targets: tasks.append("total_mr")
        params["tasks"] = tasks

        # Back-compat (single task/targets)
        if ct_targets and not mr_targets:
            params["task"] = "total";    params["targets"] = ct_targets
        elif mr_targets and not ct_targets:
            params["task"] = "total_mr"; params["targets"] = mr_targets

        return params

    def set_running(self, running: bool):
        # Disable Run while a job is active; enable Stop
        self.btn_run.setEnabled(not running)
        self.btn_stop.setEnabled(running)

    def set_series_progress(self, table_row: int, value: int):
        try:
            w = self.tbl.cellWidget(table_row, 5)
            if isinstance(w, QProgressBar):
                w.setValue(max(0, min(100, int(value))))
        except Exception:
            pass

    def _on_run_clicked(self):
        series = self.get_selected_series()
        if not series:
            QMessageBox.information(self, "Nothing selected", "Please select at least one series.")
            return

        params = self.build_params()
        if not params["ct_targets"] and not params["mr_targets"] and not params["subroutines"]:
            reply = QMessageBox.question(
                self, "No selections",
                "No CT/MR structures or sub-routines were selected.\n"
                "Run CT Total with ALL CT labels?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                for cb in self.ct_label_to_cb.values():
                    cb.setChecked(True)
                params = self.build_params()
            else:
                return

        self.runSegRequested.emit(series, params)
