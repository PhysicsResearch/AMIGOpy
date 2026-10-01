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

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QScrollArea, QGridLayout,
    QDoubleSpinBox, QComboBox, QMessageBox, QSplitter, QSizePolicy, QProgressBar,
    QRadioButton, QButtonGroup, QFrame, QSpinBox, QTabWidget, QFileDialog
)
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# TUNABLE HEIGHTS
MINH_QUICK       = 110   # Quick-groups scroll height
MINH_CT_GROUPS   = 200   # CT structures groups scroll height
MINH_MR_GROUPS   = 200   # MR structures groups scroll height
COLS_PER_GROUP   = 3     # columns for each label grid
# ---------------------------------------------------------------------------

# ------------------------------- Sub-routines -------------------------------

SUBROUTINE_KEYS = [
    "all_bone",
    "cortical_bone",
    "bone_marrow",
    "lungs_merged",
    "lungs_merged_side",
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

# ------------------------------- Bone Subroutine Targets --------------------

ALL_BONE_TARGETS_CT = [
    "skull",
    "sacrum",
    "vertebrae_C1","vertebrae_C2","vertebrae_C3","vertebrae_C4","vertebrae_C5","vertebrae_C6","vertebrae_C7",
    "vertebrae_T1","vertebrae_T2","vertebrae_T3","vertebrae_T4","vertebrae_T5","vertebrae_T6","vertebrae_T7","vertebrae_T8","vertebrae_T9","vertebrae_T10","vertebrae_T11","vertebrae_T12",
    "vertebrae_L1","vertebrae_L2","vertebrae_L3","vertebrae_L4","vertebrae_L5","vertebrae_S1",
    "rib_left_1","rib_left_2","rib_left_3","rib_left_4","rib_left_5","rib_left_6",
    "rib_left_7","rib_left_8","rib_left_9","rib_left_10","rib_left_11","rib_left_12",
    "rib_right_1","rib_right_2","rib_right_3","rib_right_4","rib_right_5","rib_right_6",
    "rib_right_7","rib_right_8","rib_right_9","rib_right_10","rib_right_11","rib_right_12",
    "sternum",
    "costal_cartilages",
    "clavicula_left","clavicula_right",
    "scapula_left","scapula_right",
    "humerus_left","humerus_right",
    "hip_left","hip_right",
    "femur_left","femur_right",
]

ALL_BONE_TARGETS_MR = [
    "sacrum",
    "vertebrae",
    "intervertebral_discs",
    "clavicula_left","clavicula_right",
    "scapula_left","scapula_right",
    "humerus_left","humerus_right",
    "hip_left","hip_right",
    "femur_left","femur_right",
]

# ------------------------------- Lung Subroutine Targets --------------------

ALL_LUNG_TARGETS_CT_LEFT = [
    "lung_upper_lobe_left",
    "lung_lower_lobe_left",
]

ALL_LUNG_TARGETS_CT_RIGHT = [
    "lung_upper_lobe_right",
    "lung_middle_lobe_right",
    "lung_lower_lobe_right",
]

ALL_LUNG_TARGETS_CT = ALL_LUNG_TARGETS_CT_LEFT + ALL_LUNG_TARGETS_CT_RIGHT

ALL_LUNG_TARGETS_MR_LEFT = ["lung_left"]
ALL_LUNG_TARGETS_MR_RIGHT = ["lung_right"]
ALL_LUNG_TARGETS_MR = ALL_LUNG_TARGETS_MR_LEFT + ALL_LUNG_TARGETS_MR_RIGHT

# ---------------------------------------------------------------------------

class SegmentatorWindow(QWidget):
    runSegRequested = Signal(list, dict)
    runFolderBatchRequested = Signal(str, list, dict)
    stopRequested   = Signal()

    def __init__(self, parent=None, medical_image=None, excluded_modalities=None, data_provider=None):
        super().__init__(None)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle("Auto-Contouring (TotalSegmentator)")
        self.setMinimumSize(950, 600)

        # Determine screen size and set startup size dynamically
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            scr_w = geom.width()
            scr_h = geom.height()
            new_w = min(1360, int(scr_w * 0.95))
            new_h = min(880, int(scr_h * 0.90))
            self.resize(new_w, new_h)
        else:
            self.resize(1360, 880)

        self.setStyleSheet("""
            QWidget {
                color: #ECEFF1;
            }
            QPushButton {
                background-color: #1976D2; color: #FFFFFF; padding: 5px 12px;
                border-radius: 5px; font-weight: 600;
            }
            QPushButton:hover { background-color: #1565C0; }
            QPushButton:disabled { background-color: #90A4AE; color: #ECEFF1; }
            QCheckBox {
                font-size: 12px;
                color: #ECEFF1;
            }
            QCheckBox:hover {
                color: #FFFFFF;
            }
            QRadioButton {
                font-size: 12px;
                color: #ECEFF1;
            }
            QRadioButton:hover {
                color: #FFFFFF;
            }
            QLabel {
                color: #ECEFF1;
            }
            QGroupBox {
                color: #ECEFF1;
            }
            QSpinBox, QDoubleSpinBox {
                color: #ECEFF1;
                background-color: #263238;
                border: 1px solid #455A64;
                border-radius: 3px;
                padding: 2px 4px;
            }
        """)

        self.medical_image = medical_image or {}
        self.excluded_modalities = excluded_modalities or set()
        self.data_provider = data_provider

        self.series_rows: List[Dict] = []
        self.ct_label_to_cb: Dict[str, QCheckBox] = {}
        self.mr_label_to_cb: Dict[str, QCheckBox] = {}
        self.subr_cb: Dict[str, QCheckBox] = {}

        # Category and filter tracking
        self.ct_group_boxes: Dict[str, QGroupBox] = {}
        self.mr_group_boxes: Dict[str, QGroupBox] = {}
        self.ct_group_labels: Dict[str, List[str]] = {}
        self.mr_group_labels: Dict[str, List[str]] = {}
        self.cat_visibility: Dict[str, bool] = {}
        self.cat_checkboxes: Dict[str, QCheckBox] = {}
        self.ct_quick_cbs: Dict[str, QCheckBox] = {}
        self.mr_quick_cbs: Dict[str, QCheckBox] = {}

        # Folder Batch mode tracking
        self.folder_files: List[Path] = []
        self._folder_row_progress: Dict[int, QProgressBar] = {}

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

        opt.addSpacing(12)
        self.chk_separate_cortical = QCheckBox("Split Cortical/Marrow")
        self.chk_separate_cortical.setChecked(True)
        self.chk_separate_cortical.setToolTip("When segmenting bone, separate cortical bone (outer shell) from bone marrow (inner cavity)")
        opt.addWidget(self.chk_separate_cortical)

        lbl_hu = QLabel("Cortical HU:")
        self.cortical_hu_spin = QSpinBox()
        self.cortical_hu_spin.setRange(100, 1500)
        self.cortical_hu_spin.setSingleStep(25)
        self.cortical_hu_spin.setValue(300)
        self.cortical_hu_spin.setSuffix(" HU")
        self.cortical_hu_spin.setToolTip("Threshold in Hounsfield Units to separate cortical bone (>= threshold) from inner bone marrow (< threshold). Default: 300 HU")
        self.cortical_hu_spin.setFixedWidth(85)
        self.chk_separate_cortical.toggled.connect(self.cortical_hu_spin.setEnabled)
        opt.addWidget(lbl_hu)
        opt.addWidget(self.cortical_hu_spin)

        opt.addSpacing(16); opt.addWidget(QLabel("Output type:"))
        self.output_type = QComboBox(); self.output_type.addItems(["nifti","dicom"])
        opt.addWidget(self.output_type)

        opt.addSpacing(20); opt.addWidget(QLabel("Device:"))
        self.device_type = QComboBox(); self.device_type.addItems(["cpu", "gpu"])
        opt.addWidget(self.device_type)

        # GPU Detection
        gpu_detected = False
        gpu_name = ""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_detected = True
                gpu_name = torch.cuda.get_device_name(0)
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                gpu_detected = True
                gpu_name = "Apple Silicon MPS"
        except ImportError:
            pass

        if gpu_detected:
            self.lbl_gpu = QLabel(f"🟢 GPU Detected: {gpu_name}")
            self.lbl_gpu.setStyleSheet("color: green; font-weight: bold;")
            self.device_type.setCurrentText("gpu")
        else:
            self.lbl_gpu = QLabel("🔴 GPU: Not Detected (CPU mode)")
            self.lbl_gpu.setStyleSheet("color: #D32F2F;")
            self.device_type.setCurrentText("cpu")
        opt.addWidget(self.lbl_gpu)

        opt.addStretch()
        main.addLayout(opt)

        # ---- splitter: left (series + visualization panel) / right (structures & subroutines)
        splitter = QSplitter(Qt.Horizontal); splitter.setHandleWidth(8)
        splitter.setChildrenCollapsible(False)
        main.addWidget(splitter, 1)

        # LEFT PANE: series table (top) and visualization / filters (bottom)
        left = QWidget(); lv = QVBoxLayout(left); lv.setContentsMargins(0,0,0,0); lv.setSpacing(6)
        
        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.setHandleWidth(6)
        left_splitter.setChildrenCollapsible(False)

        # 1. Top container: Tabs to switch between Loaded Series and Folder Batch
        self.mode_tabs = QTabWidget()
        self.mode_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #37474F;
                border-radius: 4px;
                background-color: transparent;
            }
            QTabBar::tab {
                background: #1E242B;
                color: #B0BEC5;
                padding: 6px 14px;
                border: 1px solid #37474F;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
                font-size: 11px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #263238;
                color: #38BDF8;
                border-color: #0284C7;
            }
            QTabBar::tab:hover:!selected {
                background: #212B36;
                color: #ECEFF1;
            }
        """)

        # Tab 0: Loaded Series (AMIGO)
        series_container = QWidget()
        sc_layout = QVBoxLayout(series_container); sc_layout.setContentsMargins(4, 4, 4, 4); sc_layout.setSpacing(4)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("<b>Series:</b>"))
        hdr.addStretch()
        for txt, slot in [
            ("Select All", lambda: self._select_all_series(True)),
            ("Clear All",  lambda: self._select_all_series(False)),
            ("Refresh",    self._reload_series),
        ]:
            b = QPushButton(txt); b.setStyleSheet("padding: 3px 8px; font-size: 11px;"); b.clicked.connect(slot); hdr.addWidget(b)
        sc_layout.addLayout(hdr)

        self.tbl = QTableWidget(0, 6)
        self.tbl.setHorizontalHeaderLabels(["Select","Patient","Study","Modality","Series [index]","Status"])
        self.tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tbl.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.tbl.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tbl.setMinimumHeight(110)
        sc_layout.addWidget(self.tbl, 1)

        self.mode_tabs.addTab(series_container, "Loaded Series (AMIGO)")

        # Tab 1: Folder Batch
        folder_container = self._build_folder_container()
        self.mode_tabs.addTab(folder_container, "Folder Batch")
        self.mode_tabs.currentChanged.connect(self._on_mode_tab_changed)

        left_splitter.addWidget(self.mode_tabs)

        # 2. Bottom container: Visualization & Filter Options Panel
        vis_panel = self._build_visualization_panel()
        left_splitter.addWidget(vis_panel)

        left_splitter.setSizes([260, 440])
        left_splitter.setStretchFactor(0, 1)
        left_splitter.setStretchFactor(1, 1)

        lv.addWidget(left_splitter, 1)
        splitter.addWidget(left)

        # RIGHT: single unified scroll area containing subroutines, CT section, MR section
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QScrollArea.NoFrame)

        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(4, 4, 8, 4)
        right_layout.setSpacing(10)

        # 1. Sub-routines
        self.subr_box = self._build_subroutine_box()
        right_layout.addWidget(self.subr_box)

        # 2. CT section
        self.ct_box, self.ct_search, self.ct_quick_box, self.ct_group_boxes, self.ct_quick_cbs = self._build_structures_section(
            title="CT Total — pick structures (auto-enables CT task if any selected)",
            all_targets=CT_ALL_TARGETS, groups=CT_GROUPS, quick=CT_QUICK,
            search_ph="Filter CT labels...", target_map="ct"
        )
        right_layout.addWidget(self.ct_box)

        # 3. MR section
        self.mr_box, self.mr_search, self.mr_quick_box, self.mr_group_boxes, self.mr_quick_cbs = self._build_structures_section(
            title="MR Total — pick structures (auto-enables MR task if any selected)",
            all_targets=MR_ALL_TARGETS, groups=MR_GROUPS, quick=MR_QUICK,
            search_ph="Filter MR labels...", target_map="mr"
        )
        right_layout.addWidget(self.mr_box)

        right_layout.addStretch()
        right_scroll.setWidget(right_content)

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
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([520, 840])

        self._populate_series_table()
        self._on_modality_view_changed()

    # --------------------------- Folder Batch mode --------------------------

    def _build_folder_container(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # 1. Top row: Folder selector
        folder_row = QHBoxLayout()
        folder_row.setSpacing(6)
        folder_row.addWidget(QLabel("<b>Folder:</b>"))

        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setPlaceholderText("Select folder containing NIfTI files (*.nii, *.nii.gz)...")
        self.folder_path_edit.setStyleSheet("""
            QLineEdit {
                background-color: #263238;
                color: #ECEFF1;
                border: 1px solid #455A64;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 1px solid #0284C7;
            }
        """)
        self.folder_path_edit.returnPressed.connect(self._scan_folder)
        folder_row.addWidget(self.folder_path_edit, 1)

        btn_browse = QPushButton("Browse...")
        btn_browse.setStyleSheet("padding: 4px 10px; font-size: 11px; background-color: #0284C7;")
        btn_browse.clicked.connect(self._browse_folder)
        folder_row.addWidget(btn_browse)

        btn_scan = QPushButton("Scan")
        btn_scan.setStyleSheet("padding: 4px 10px; font-size: 11px;")
        btn_scan.clicked.connect(self._scan_folder)
        folder_row.addWidget(btn_scan)

        layout.addLayout(folder_row)

        # 2. Controls row: Select All, Clear All, and count label
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(6)

        self.lbl_folder_count = QLabel("No folder selected")
        self.lbl_folder_count.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: bold;")
        ctrl_row.addWidget(self.lbl_folder_count)
        ctrl_row.addStretch()

        btn_all = QPushButton("Select All")
        btn_all.setStyleSheet("padding: 3px 8px; font-size: 11px;")
        btn_all.clicked.connect(lambda: self._select_all_folder(True))
        ctrl_row.addWidget(btn_all)

        btn_clear = QPushButton("Clear All")
        btn_clear.setStyleSheet("padding: 3px 8px; font-size: 11px;")
        btn_clear.clicked.connect(lambda: self._select_all_folder(False))
        ctrl_row.addWidget(btn_clear)

        layout.addLayout(ctrl_row)

        # 3. NIfTI files table
        self.folder_tbl = QTableWidget(0, 5)
        self.folder_tbl.setHorizontalHeaderLabels(["Select", "File Name", "Size", "Dimensions", "Status"])
        self.folder_tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.folder_tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.folder_tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.folder_tbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.folder_tbl.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.folder_tbl.setMinimumHeight(110)
        self.folder_tbl.setStyleSheet("""
            QTableWidget {
                background-color: #1E242B;
                gridline-color: #37474F;
                color: #ECEFF1;
                border: 1px solid #37474F;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #263238;
                color: #B0BEC5;
                font-weight: bold;
                border: 1px solid #37474F;
                padding: 4px;
                font-size: 11px;
            }
            QTableWidget::item:selected {
                background-color: #0284C7;
                color: #FFFFFF;
            }
        """)
        layout.addWidget(self.folder_tbl, 1)

        # 4. Info banner
        info_lbl = QLabel("ℹ Output will be saved to: <b><Folder>/autocont/<filename>/</b> (original scan + contours)")
        info_lbl.setStyleSheet("color: #90CAF9; font-size: 10px; padding: 2px;")
        layout.addWidget(info_lbl)

        return container

    def _on_mode_tab_changed(self, index: int):
        if hasattr(self, "btn_run"):
            if index == 1:
                self.btn_run.setText("Run Folder Batch")
            else:
                self.btn_run.setText("Run Segmentation")

    def _browse_folder(self):
        cur = self.folder_path_edit.text().strip() or os.getcwd()
        folder = QFileDialog.getExistingDirectory(self, "Select Folder Containing NIfTI Files", cur)
        if folder:
            self.folder_path_edit.setText(folder)
            self._scan_folder()

    def _quick_nifti_dims(self, fpath) -> str:
        try:
            import nibabel as nib
            hdr = nib.load(str(fpath)).header
            shape = hdr.get_data_shape()
            if len(shape) >= 3:
                return f"{shape[0]}×{shape[1]}×{shape[2]}"
            return "×".join(str(s) for s in shape)
        except Exception:
            try:
                import SimpleITK as sitk
                reader = sitk.ImageFileReader()
                reader.SetFileName(str(fpath))
                reader.ReadImageInformation()
                size = reader.GetSize()
                return f"{size[0]}×{size[1]}×{size[2]}"
            except Exception:
                return "-"

    def _scan_folder(self):
        folder_str = self.folder_path_edit.text().strip()
        if not folder_str or not os.path.isdir(folder_str):
            self.lbl_folder_count.setText("Please select a valid folder.")
            self.folder_tbl.setRowCount(0)
            self.folder_files = []
            return

        folder = Path(folder_str)
        nii_files = []
        for f in folder.iterdir():
            if not f.is_file():
                continue
            name_lower = f.name.lower()
            if not (name_lower.endswith(".nii") or name_lower.endswith(".nii.gz")):
                continue
            # Exclude structure mask files (e.g. *_ST_*.nii.gz, or starting with dot)
            if "_st_" in name_lower or name_lower.startswith("."):
                continue
            try:
                from fcn_export.export_structures_dialog import is_structure_nifti
                is_struct, _, _ = is_structure_nifti(f.name)
                if is_struct:
                    continue
            except Exception:
                pass
            nii_files.append(f)

        nii_files.sort(key=lambda p: p.name.lower())
        self.folder_files = nii_files

        self.folder_tbl.setRowCount(len(nii_files))
        self._folder_row_progress = {}

        if not nii_files:
            self.lbl_folder_count.setText("No NIfTI files found in this folder (*.nii, *.nii.gz)")
            return

        for r, fpath in enumerate(nii_files):
            # Col 0: Checkbox
            chk = QCheckBox()
            chk.setChecked(True)
            chk.stateChanged.connect(self._update_folder_count)
            cb_wrap = QWidget()
            cb_l = QHBoxLayout(cb_wrap)
            cb_l.setContentsMargins(8, 0, 0, 0)
            cb_l.setAlignment(Qt.AlignCenter)
            cb_l.addWidget(chk)
            self.folder_tbl.setCellWidget(r, 0, cb_wrap)

            # Col 1: Filename
            it_name = QTableWidgetItem(fpath.name)
            it_name.setToolTip(str(fpath))
            it_name.setFlags(it_name.flags() & ~Qt.ItemIsEditable)
            self.folder_tbl.setItem(r, 1, it_name)

            # Col 2: Size
            try:
                size_bytes = fpath.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                it_size = QTableWidgetItem(f"{size_mb:.1f} MB" if size_mb >= 1.0 else f"{size_bytes/1024:.0f} KB")
            except Exception:
                it_size = QTableWidgetItem("-")
            it_size.setTextAlignment(Qt.AlignCenter)
            it_size.setFlags(it_size.flags() & ~Qt.ItemIsEditable)
            self.folder_tbl.setItem(r, 2, it_size)

            # Col 3: Dimensions
            dims_str = self._quick_nifti_dims(fpath)
            it_dims = QTableWidgetItem(dims_str)
            it_dims.setTextAlignment(Qt.AlignCenter)
            it_dims.setFlags(it_dims.flags() & ~Qt.ItemIsEditable)
            self.folder_tbl.setItem(r, 3, it_dims)

            # Col 4: Status / Progress bar
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(True)
            bar.setFormat("Ready")
            bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #37474F;
                    border-radius: 3px;
                    text-align: center;
                    font-size: 10px;
                    background-color: #1E242B;
                    color: #ECEFF1;
                }
                QProgressBar::chunk {
                    background-color: #0284C7;
                }
            """)
            self.folder_tbl.setCellWidget(r, 4, bar)
            self._folder_row_progress[r] = bar

        self._update_folder_count()

    def _select_all_folder(self, state: bool):
        for r in range(self.folder_tbl.rowCount()):
            cb_wrap = self.folder_tbl.cellWidget(r, 0)
            if cb_wrap:
                cb = cb_wrap.findChild(QCheckBox)
                if cb:
                    cb.setChecked(state)
        self._update_folder_count()

    def _update_folder_count(self):
        total = self.folder_tbl.rowCount()
        selected = len(self.get_selected_folder_files())
        self.lbl_folder_count.setText(f"{selected} of {total} files selected")

    def get_selected_folder_files(self) -> List[Dict[str, Any]]:
        selected = []
        for r in range(self.folder_tbl.rowCount()):
            cb_wrap = self.folder_tbl.cellWidget(r, 0)
            if cb_wrap:
                cb = cb_wrap.findChild(QCheckBox)
                if cb and cb.isChecked() and r < len(getattr(self, "folder_files", [])):
                    fpath = self.folder_files[r]
                    selected.append({
                        "row": r,
                        "path": str(fpath),
                        "name": fpath.name,
                    })
        return selected

    # --------------------------- Visualization panel ------------------------

    def _build_visualization_panel(self) -> QGroupBox:
        box = QGroupBox("Visualization & Filter Options")
        box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #37474F;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ECEFF1;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
                color: #90CAF9;
            }
            QRadioButton {
                color: #ECEFF1;
                font-size: 12px;
                font-weight: 600;
            }
            QRadioButton:hover {
                color: #FFFFFF;
            }
            QCheckBox {
                color: #ECEFF1;
                font-size: 12px;
            }
            QCheckBox:hover {
                color: #FFFFFF;
            }
            QLabel {
                color: #ECEFF1;
            }
        """)
        v = QVBoxLayout(box)
        v.setContentsMargins(8, 10, 8, 8)
        v.setSpacing(8)

        # 1. Modality View Selection
        lbl_mod = QLabel("Modality View:")
        lbl_mod.setStyleSheet("font-weight: bold; color: #ECEFF1; font-size: 12px;")
        v.addWidget(lbl_mod)

        mod_row = QHBoxLayout()
        mod_row.setSpacing(14)
        self.rb_ct = QRadioButton("CT (Total)")
        self.rb_mr = QRadioButton("MRI (Total MR)")
        self.rb_both = QRadioButton("Both")
        self.rb_ct.setStyleSheet("font-size: 12px; font-weight: 600; color: #ECEFF1;")
        self.rb_mr.setStyleSheet("font-size: 12px; font-weight: 600; color: #ECEFF1;")
        self.rb_both.setStyleSheet("font-size: 12px; font-weight: 600; color: #ECEFF1;")

        self.mod_group = QButtonGroup(self)
        self.mod_group.addButton(self.rb_ct, 1)
        self.mod_group.addButton(self.rb_mr, 2)
        self.mod_group.addButton(self.rb_both, 3)
        self.rb_ct.setChecked(True)

        mod_row.addWidget(self.rb_ct)
        mod_row.addWidget(self.rb_mr)
        mod_row.addWidget(self.rb_both)
        mod_row.addStretch()
        v.addLayout(mod_row)

        self.rb_ct.toggled.connect(self._on_modality_view_changed)
        self.rb_mr.toggled.connect(self._on_modality_view_changed)
        self.rb_both.toggled.connect(self._on_modality_view_changed)

        # Divider line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #37474F;")
        v.addWidget(line)

        # 2. Sub-categories header + Show All / Hide All buttons
        cat_hdr = QHBoxLayout()
        lbl_cats = QLabel("Sub-Categories to Display:")
        lbl_cats.setStyleSheet("font-weight: bold; color: #ECEFF1; font-size: 12px;")
        cat_hdr.addWidget(lbl_cats)
        cat_hdr.addStretch()

        btn_show_all = QPushButton("Show All")
        btn_show_all.setStyleSheet("background-color: #1976D2; color: #FFFFFF; padding: 2px 8px; font-size: 11px;")
        btn_show_all.clicked.connect(self._show_all_categories)
        cat_hdr.addWidget(btn_show_all)

        btn_hide_all = QPushButton("Hide All")
        btn_hide_all.setStyleSheet("background-color: #1976D2; color: #FFFFFF; padding: 2px 8px; font-size: 11px;")
        btn_hide_all.clicked.connect(self._hide_all_categories)
        cat_hdr.addWidget(btn_hide_all)
        v.addLayout(cat_hdr)

        # 3. Scroll area containing the category checkboxes
        cat_scroll = QScrollArea()
        cat_scroll.setWidgetResizable(True)
        cat_scroll.setFrameShape(QScrollArea.NoFrame)
        self.cat_container = QWidget()
        self.cat_layout = QVBoxLayout(self.cat_container)
        self.cat_layout.setContentsMargins(2, 2, 2, 2)
        self.cat_layout.setSpacing(6)
        cat_scroll.setWidget(self.cat_container)
        v.addWidget(cat_scroll, 1)

        return box

    def _on_modality_view_changed(self):
        is_ct = self.rb_ct.isChecked()
        is_mr = self.rb_mr.isChecked()
        is_both = self.rb_both.isChecked()

        if hasattr(self, "ct_box"):
            self.ct_box.setVisible(is_ct or is_both)
        if hasattr(self, "mr_box"):
            self.mr_box.setVisible(is_mr or is_both)

        self._update_category_filter_list()
        self._apply_all_category_visibilities()
        self._update_category_counts()

    def _get_active_category_names(self) -> List[str]:
        cats = ["Sub-routines", "Quick Groups"]
        if self.rb_ct.isChecked():
            for gtitle, _ in CT_GROUPS:
                if gtitle not in cats:
                    cats.append(gtitle)
        elif self.rb_mr.isChecked():
            for gtitle, _ in MR_GROUPS:
                if gtitle not in cats:
                    cats.append(gtitle)
        else: # Both
            all_groups = [g[0] for g in CT_GROUPS] + [g[0] for g in MR_GROUPS]
            for gtitle in all_groups:
                if gtitle not in cats:
                    cats.append(gtitle)
        return cats

    def _update_category_filter_list(self):
        while self.cat_layout.count():
            item = self.cat_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self.cat_checkboxes.clear()
        active_cats = self._get_active_category_names()

        for cat_name in active_cats:
            is_vis = self.cat_visibility.get(cat_name, True)
            self.cat_visibility[cat_name] = is_vis

            cb = QCheckBox(cat_name)
            cb.setChecked(is_vis)
            cb.setStyleSheet("color: #ECEFF1; font-size: 12px;")
            cb.setToolTip(f"Show/hide {cat_name} category on the right side")
            cb.toggled.connect(lambda chk, name=cat_name: self._on_cat_toggled(name, chk))
            self.cat_layout.addWidget(cb)
            self.cat_checkboxes[cat_name] = cb

        self.cat_layout.addStretch()

    def _on_cat_toggled(self, name: str, checked: bool):
        self.cat_visibility[name] = checked
        self._apply_category_visibility(name, checked)

    def _apply_category_visibility(self, name: str, visible: bool):
        if name == "Sub-routines":
            if hasattr(self, "subr_box"):
                self.subr_box.setVisible(visible)
        elif name == "Quick Groups":
            if hasattr(self, "ct_quick_box"):
                self.ct_quick_box.setVisible(visible)
            if hasattr(self, "mr_quick_box"):
                self.mr_quick_box.setVisible(visible)
        else:
            if hasattr(self, "ct_group_boxes") and name in self.ct_group_boxes:
                self.ct_group_boxes[name].setVisible(visible)
            if hasattr(self, "mr_group_boxes") and name in self.mr_group_boxes:
                self.mr_group_boxes[name].setVisible(visible)

    def _apply_all_category_visibilities(self):
        for cat_name, visible in self.cat_visibility.items():
            self._apply_category_visibility(cat_name, visible)

    def _show_all_categories(self):
        for name, cb in self.cat_checkboxes.items():
            cb.setChecked(True)

    def _hide_all_categories(self):
        for name, cb in self.cat_checkboxes.items():
            cb.setChecked(False)

    def _update_category_counts(self):
        for cat_name, cb in self.cat_checkboxes.items():
            count = 0
            if cat_name == "Sub-routines":
                count = sum(1 for c in self.subr_cb.values() if c.isChecked())
            elif cat_name == "Quick Groups":
                if self.rb_ct.isChecked():
                    count = sum(1 for c in self.ct_quick_cbs.values() if c.isChecked())
                elif self.rb_mr.isChecked():
                    count = sum(1 for c in self.mr_quick_cbs.values() if c.isChecked())
                else:
                    count = sum(1 for c in self.ct_quick_cbs.values() if c.isChecked()) + sum(1 for c in self.mr_quick_cbs.values() if c.isChecked())
            else:
                if (self.rb_ct.isChecked() or self.rb_both.isChecked()) and hasattr(self, "ct_group_labels"):
                    for lab in self.ct_group_labels.get(cat_name, []):
                        if lab in self.ct_label_to_cb and self.ct_label_to_cb[lab].isChecked():
                            count += 1
                if (self.rb_mr.isChecked() or self.rb_both.isChecked()) and hasattr(self, "mr_group_labels"):
                    for lab in self.mr_group_labels.get(cat_name, []):
                        if lab in self.mr_label_to_cb and self.mr_label_to_cb[lab].isChecked():
                            count += 1

            if count > 0:
                cb.setText(f"{cat_name}  ({count} selected)")
                cb.setStyleSheet("font-weight: 600; color: #42A5F5; font-size: 12px;")
            else:
                cb.setText(cat_name)
                cb.setStyleSheet("font-weight: normal; color: #ECEFF1; font-size: 12px;")

    # --------------------------- Subroutine block ---------------------------

    def _build_subroutine_box(self) -> QGroupBox:
        box = QGroupBox("Sub-routines")
        box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #37474F;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
                color: #81C784;
            }
        """)
        v = QVBoxLayout(box); v.setContentsMargins(10,8,10,8); v.setSpacing(6)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("<b>Sub-routines</b> (independent specialized models)"))
        hdr.addStretch()
        btn_all = QPushButton("Check All"); btn_all.setFixedWidth(80)
        btn_none = QPushButton("Clear All"); btn_none.setFixedWidth(80)
        btn_all.setStyleSheet("padding: 2px 6px; font-size: 11px;")
        btn_none.setStyleSheet("padding: 2px 6px; font-size: 11px;")
        
        def _set_subr(state: bool):
            for c in self.subr_cb.values():
                c.setChecked(state)
            self._update_category_counts()

        btn_all.clicked.connect(lambda: _set_subr(True))
        btn_none.clicked.connect(lambda: _set_subr(False))
        hdr.addWidget(btn_all); hdr.addWidget(btn_none)
        v.addLayout(hdr)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18); grid.setVerticalSpacing(6)

        col = row = 0
        for key in SUBROUTINE_KEYS:
            if key == "all_bone":
                display_name = "All bone"
            elif key == "cortical_bone":
                display_name = "Cortical bone"
            elif key == "bone_marrow":
                display_name = "Bone marrow"
            elif key == "lungs_merged":
                display_name = "Lungs (merged)"
            elif key == "lungs_merged_side":
                display_name = "Lungs (merged/side)"
            else:
                display_name = key.replace("_", " ")
            cb = QCheckBox(display_name)
            if key == "all_bone":
                cb.setToolTip("Segment all bone structures and merge into a single 'bone' structure (or split if Split Cortical/Marrow enabled)")
            elif key == "cortical_bone":
                cb.setToolTip("Segment all bones and extract the dense outer cortical bone shell via HU thresholding")
            elif key == "bone_marrow":
                cb.setToolTip("Segment all bones and extract inner bone marrow / cancellous space via HU thresholding")
            elif key == "lungs_merged":
                cb.setToolTip("Segment all lung structures and merge into a single 'lungs' mask")
            elif key == "lungs_merged_side":
                cb.setToolTip("Segment lung lobes and merge by side into 'lung_left' and 'lung_right' masks")

            def _make_subr_handler(k):
                def _handler(state):
                    if k in ("cortical_bone", "bone_marrow") and state:
                        self.chk_separate_cortical.setChecked(True)
                    self._update_category_counts()
                return _handler

            cb.stateChanged.connect(_make_subr_handler(key))
            self.subr_cb[key] = cb
            grid.addWidget(cb, row, col)
            col += 1
            if col >= 4:
                col = 0; row += 1

        v.addLayout(grid)
        return box

    # --------------------------- Structures sections ------------------------

    def _build_structures_section(
        self, title: str, all_targets: List[str],
        groups: List[Tuple[str, List[str]]],
        quick: Dict[str, List[str]],
        search_ph: str, target_map: str
    ):
        box = QGroupBox(title)
        color = "#64B5F6" if target_map == "ct" else "#BA68C8"
        box.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid #37474F;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
                color: {color};
            }}
        """)
        v = QVBoxLayout(box); v.setContentsMargins(10,8,10,8); v.setSpacing(8)

        # Search + select all/clear all
        r = QHBoxLayout()
        search = QLineEdit(); search.setPlaceholderText(search_ph); r.addWidget(search, 1)
        btn_all  = QPushButton("Select All"); btn_none = QPushButton("Clear All")
        r.addWidget(btn_all); r.addWidget(btn_none)
        v.addLayout(r)

        # Quick groups
        quick_box = QGroupBox("Quick Groups")
        q_vbox = QVBoxLayout(quick_box); q_vbox.setContentsMargins(8, 6, 8, 6); q_vbox.setSpacing(6)
        q_grid = QGridLayout()
        q_grid.setHorizontalSpacing(18); q_grid.setVerticalSpacing(6)

        quick_map: Dict[str, QCheckBox] = {}
        col = row = 0
        for name in quick.keys():
            cb = QCheckBox(name); quick_map[name] = cb
            q_grid.addWidget(cb, row, col)
            col += 1
            if col >= 3:
                col = 0; row += 1

        q_vbox.addLayout(q_grid)
        v.addWidget(quick_box)

        # Main structures groups
        group_boxes: Dict[str, QGroupBox] = {}
        group_labels: Dict[str, List[str]] = {}
        label_to_cb: Dict[str, QCheckBox] = {}

        for gtitle, labels in groups:
            labs = [x for x in labels if x in set(all_targets)]
            if not labs:
                continue
            group_labels[gtitle] = labs
            grp = QGroupBox(gtitle)
            glay = QVBoxLayout(grp); glay.setContentsMargins(8, 6, 8, 6); glay.setSpacing(6)
            
            header = QHBoxLayout()
            header.addWidget(QLabel(f"<b>{gtitle}</b>"))
            header.addStretch()
            
            toggle = QPushButton("Check All"); toggle.setFixedWidth(100)
            btn_collapse = QPushButton("▾")
            btn_collapse.setFixedWidth(28)
            btn_collapse.setStyleSheet("padding: 2px; font-size: 11px;")
            btn_collapse.setToolTip("Collapse / Expand")
            header.addWidget(toggle)
            header.addWidget(btn_collapse)
            glay.addLayout(header)

            grid_holder = QWidget()
            grid = QGridLayout(grid_holder)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(18); grid.setVerticalSpacing(6)
            for i, lab in enumerate(labs):
                cb = QCheckBox(lab)
                cb.stateChanged.connect(lambda _: self._update_category_counts())
                label_to_cb[lab] = cb
                grid.addWidget(cb, i // COLS_PER_GROUP, i % COLS_PER_GROUP)
            glay.addWidget(grid_holder)

            def make_collapse(w: QWidget, b: QPushButton):
                def _c():
                    if w.isVisible():
                        w.setVisible(False)
                        b.setText("▸")
                    else:
                        w.setVisible(True)
                        b.setText("▾")
                return _c
            btn_collapse.clicked.connect(make_collapse(grid_holder, btn_collapse))

            def make_toggle(cbs: List[QCheckBox], btn: QPushButton):
                def _t():
                    all_on = all(c.isChecked() for c in cbs)
                    for c in cbs:
                        c.setChecked(not all_on)
                    btn.setText("Uncheck All" if not all_on else "Check All")
                    self._update_category_counts()
                return _t
            toggle.clicked.connect(make_toggle([label_to_cb[x] for x in labs], toggle))

            group_boxes[gtitle] = grp
            v.addWidget(grp)

        # search filter
        def _apply_filter(text: str):
            pat = (text or "").strip().lower()
            for lab, cb in label_to_cb.items():
                cb.setVisible(pat in lab.lower() if pat else True)
            
            for gtitle, labels in groups:
                grp = group_boxes.get(gtitle)
                if not grp:
                    continue
                if pat:
                    has_match = any(pat in l.lower() for l in labels)
                    grp.setVisible(has_match)
                else:
                    grp.setVisible(self.cat_visibility.get(gtitle, True))
        search.textChanged.connect(_apply_filter)

        # select all/none (respect filter)
        def _set_all(state: bool):
            pat = (search.text() or "").strip().lower()
            for lab, cb in label_to_cb.items():
                if (not pat) or (pat in lab.lower()):
                    cb.setChecked(state)
            self._update_category_counts()
        btn_all.clicked.connect(lambda: _set_all(True))
        btn_none.clicked.connect(lambda: _set_all(False))

        # Quick toggles (each quick-group toggle only affects its own member structures)
        for name, cb in quick_map.items():
            def make_qc(grp_name):
                def _qc(state):
                    is_on = bool(state)
                    for lab in quick.get(grp_name, []):
                        w = label_to_cb.get(lab)
                        if w:
                            w.setChecked(is_on)
                    self._update_category_counts()
                return _qc
            cb.stateChanged.connect(make_qc(name))

        if target_map == "ct":
            self.ct_label_to_cb = label_to_cb
            self.ct_group_boxes = group_boxes
            self.ct_group_labels = group_labels
            self.ct_quick_box = quick_box
            self.ct_quick_cbs = quick_map
        else:
            self.mr_label_to_cb = label_to_cb
            self.mr_group_boxes = group_boxes
            self.mr_group_labels = group_labels
            self.mr_quick_box = quick_box
            self.mr_quick_cbs = quick_map

        return box, search, quick_box, group_boxes, quick_map

    # --------------------------- Series table ops ---------------------------

    def _reload_series(self):
        try:
            if callable(self.data_provider):
                new_data = self.data_provider()
                if new_data is not None:
                    self.medical_image = new_data
        except Exception as e:
            QMessageBox.warning(self, "Refresh failed", f"Could not refresh series:\n{e}")
            return
        self._populate_series_table()

    def _populate_series_table(self):
        self.tbl.setRowCount(0); self.series_rows.clear()
        rows = []
        modalities_found = set()
        for pid, studies in sorted(self.medical_image.items()):
            for study_id, by_mod in studies.items():
                for modality, series_list in by_mod.items():
                    if modality in (self.excluded_modalities or set()):
                        continue
                    modalities_found.add(str(modality).upper())
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

            row_dict = {
                "row": r, "patient": pid, "study": study, "modality": mod, "index": idx,
                "label": label, "pgb": pgb, "chk": cb
            }
            self.series_rows.append(row_dict)

            # Modality auto-detection on checking a series
            def make_chk_handler(mod_val):
                def _h(state):
                    if state:
                        m = str(mod_val).upper()
                        if m in ("MR", "MRI") and not self.rb_mr.isChecked():
                            self.rb_mr.setChecked(True)
                        elif m == "CT" and not self.rb_ct.isChecked():
                            self.rb_ct.setChecked(True)
                return _h
            cb.stateChanged.connect(make_chk_handler(mod))

        # Initial selection based on available data
        if any(m in ("MR", "MRI") for m in modalities_found) and not any(m == "CT" for m in modalities_found):
            if not self.rb_mr.isChecked():
                self.rb_mr.setChecked(True)
        elif any(m == "CT" for m in modalities_found):
            if not self.rb_ct.isChecked():
                self.rb_ct.setChecked(True)

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
        return [lab for lab, cb in mapping.items() if cb.isChecked()]

    def build_params(self) -> Dict:
        params: Dict = {}
        if self.chk_fast.isChecked():        params["fast"] = True
        if self.chk_merge.isChecked():       params["merge_labels"] = True
        rs = float(self.resample_spin.value())
        if rs > 0:                           params["resample"] = rs
        if self.chk_no_crop.isChecked():     params["no_crop"] = True
        params["output_type"] = self.output_type.currentText().strip().lower()
        params["device"] = self.device_type.currentText().strip().lower()

        subroutines = [k for k, cb in self.subr_cb.items() if cb.isChecked()]
        bone_subroutines = {"all_bone", "cortical_bone", "bone_marrow"}
        all_bone_selected = any(k in subroutines for k in bone_subroutines)

        lung_subroutines = {"lungs_merged", "lungs_merged_side"}
        lung_selected = any(k in subroutines for k in lung_subroutines)

        # Filter targets based on active modality view
        if self.rb_mr.isChecked():
            ct_targets = []
            mr_targets = self._selected_labels(self.mr_label_to_cb)
        elif self.rb_ct.isChecked():
            ct_targets = self._selected_labels(self.ct_label_to_cb)
            mr_targets = []
        else: # Both
            ct_targets = self._selected_labels(self.ct_label_to_cb)
            mr_targets = self._selected_labels(self.mr_label_to_cb)

        # Record manual targets explicitly
        params["manual_ct_targets"] = list(ct_targets)
        params["manual_mr_targets"] = list(mr_targets)
        params["all_bone"] = all_bone_selected
        params["lungs_merged"] = ("lungs_merged" in subroutines)
        params["lungs_merged_side"] = ("lungs_merged_side" in subroutines)

        requested_lung_types = []
        if "lungs_merged" in subroutines:
            requested_lung_types.append("lungs_merged")
        if "lungs_merged_side" in subroutines:
            requested_lung_types.append("lungs_merged_side")
        params["requested_lung_types"] = requested_lung_types

        separate_cortical = self.chk_separate_cortical.isChecked() or any(k in subroutines for k in ("cortical_bone", "bone_marrow"))
        params["separate_cortical"] = separate_cortical
        params["cortical_hu"] = int(self.cortical_hu_spin.value())

        # Determine which bone structures are requested to be saved/imported
        requested_bone_types = []
        if "all_bone" in subroutines:
            requested_bone_types.append("all_bone")
            if separate_cortical:
                if "cortical_bone" not in requested_bone_types:
                    requested_bone_types.append("cortical_bone")
                if "bone_marrow" not in requested_bone_types:
                    requested_bone_types.append("bone_marrow")
        if "cortical_bone" in subroutines and "cortical_bone" not in requested_bone_types:
            requested_bone_types.append("cortical_bone")
        if "bone_marrow" in subroutines and "bone_marrow" not in requested_bone_types:
            requested_bone_types.append("bone_marrow")

        params["requested_bone_types"] = requested_bone_types

        # Custom subroutines are handled via targets + merge/split; exclude them from raw TS subroutines
        custom_subroutines = bone_subroutines | lung_subroutines
        ts_subroutines = [s for s in subroutines if s not in custom_subroutines]
        params["subroutines"] = ts_subroutines

        effective_ct_targets = list(ct_targets)
        effective_mr_targets = list(mr_targets)

        if all_bone_selected:
            if not self.rb_mr.isChecked(): # CT or Both
                for b in ALL_BONE_TARGETS_CT:
                    if b not in effective_ct_targets:
                        effective_ct_targets.append(b)
            if not self.rb_ct.isChecked(): # MR or Both
                for b in ALL_BONE_TARGETS_MR:
                    if b not in effective_mr_targets:
                        effective_mr_targets.append(b)

        if lung_selected:
            if not self.rb_mr.isChecked(): # CT or Both
                for lt in ALL_LUNG_TARGETS_CT:
                    if lt not in effective_ct_targets:
                        effective_ct_targets.append(lt)
            if not self.rb_ct.isChecked(): # MR or Both
                for lt in ALL_LUNG_TARGETS_MR:
                    if lt not in effective_mr_targets:
                        effective_mr_targets.append(lt)

        params["ct_targets"] = effective_ct_targets
        params["mr_targets"] = effective_mr_targets

        tasks = []
        if effective_ct_targets: tasks.append("total")
        if effective_mr_targets: tasks.append("total_mr")
        for sub in ts_subroutines:
            if sub not in tasks:
                tasks.append(sub)
        params["tasks"] = tasks

        # Primary / fallback task and targets
        if effective_ct_targets:
            params["task"] = "total"
            params["targets"] = effective_ct_targets
        elif effective_mr_targets:
            params["task"] = "total_mr"
            params["targets"] = effective_mr_targets
        elif ts_subroutines:
            params["task"] = ts_subroutines[0]
            params["targets"] = []
        else:
            params["task"] = "total_mr" if self.rb_mr.isChecked() else "total"
            params["targets"] = []

        return params

    def set_running(self, running: bool):
        # Disable Run while a job is active; enable Stop
        self.btn_run.setEnabled(not running)
        self.btn_stop.setEnabled(running)
        if hasattr(self, "mode_tabs"):
            self.mode_tabs.setEnabled(not running)

    def set_series_progress(self, table_row: int, value: int):
        try:
            w = self.tbl.cellWidget(table_row, 5)
            if isinstance(w, QProgressBar):
                w.setValue(max(0, min(100, int(value))))
        except Exception:
            pass

    def _on_run_clicked(self):
        is_folder_mode = (hasattr(self, "mode_tabs") and self.mode_tabs.currentIndex() == 1)

        if is_folder_mode:
            selected_files = self.get_selected_folder_files()
            if not selected_files:
                QMessageBox.information(self, "Nothing selected", "Please select at least one NIfTI file to process.")
                return

            folder_str = self.folder_path_edit.text().strip()
            if not folder_str or not os.path.isdir(folder_str):
                QMessageBox.warning(self, "Invalid Folder", "Please select a valid folder.")
                return

            params = self.build_params()
            if not params["ct_targets"] and not params["mr_targets"] and not params["subroutines"]:
                if self.rb_mr.isChecked():
                    reply = QMessageBox.question(
                        self, "No selections",
                        "No MR structures or sub-routines were selected.\n"
                        "Run MR Total with ALL MR labels?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        for cb in self.mr_label_to_cb.values():
                            cb.setChecked(True)
                        params = self.build_params()
                    else:
                        return
                else:
                    reply = QMessageBox.question(
                        self, "No selections",
                        "No CT structures or sub-routines were selected.\n"
                        "Run CT Total with ALL CT labels?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        for cb in self.ct_label_to_cb.values():
                            cb.setChecked(True)
                        params = self.build_params()
                    else:
                        return

            self.runFolderBatchRequested.emit(folder_str, selected_files, params)
            return

        # Loaded Series (AMIGO) mode
        series = self.get_selected_series()
        if not series:
            QMessageBox.information(self, "Nothing selected", "Please select at least one series.")
            return

        params = self.build_params()
        if not params["ct_targets"] and not params["mr_targets"] and not params["subroutines"]:
            if self.rb_mr.isChecked():
                reply = QMessageBox.question(
                    self, "No selections",
                    "No MR structures or sub-routines were selected.\n"
                    "Run MR Total with ALL MR labels?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    for cb in self.mr_label_to_cb.values():
                        cb.setChecked(True)
                    params = self.build_params()
                else:
                    return
            else:
                reply = QMessageBox.question(
                    self, "No selections",
                    "No CT structures or sub-routines were selected.\n"
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
