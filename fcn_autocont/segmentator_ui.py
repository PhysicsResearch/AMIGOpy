# segmentator_ui.py — TotalSegmentator UI with canonical TS labels, grouping, search, and refresh

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QCheckBox, QHeaderView, QGroupBox,
    QScrollArea, QGridLayout, QDoubleSpinBox, QComboBox, QMessageBox,
    QSplitter, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
import os, json, pathlib, re

# ------------------------------------------------------------
# Label discovery (canonical TS names) and grouping heuristics
# ------------------------------------------------------------

def _discover_ts_labels():
    """
    Discover canonical label names from the installed TotalSegmentator package.
    Returns a sorted list of label strings as they appear in TS (lowercase, underscores).
    Fallback: a conservative built-in set if package resources are not found.
    """
    labels = set()
    # Fallback minimal set (safe; TS v1/v2 use these names consistently)
    fallback = {
        # Thorax/heart/lungs
        "left_lung","right_lung","heart","trachea","esophagus","aorta","aortic_arch","pulmonary_artery",
        # Abdomen
        "liver","spleen","pancreas","stomach","gallbladder",
        "left_kidney","right_kidney","left_adrenal_gland","right_adrenal_gland",
        "inferior_vena_cava","portal_vein","small_bowel","large_bowel","duodenum",
        # Pelvis
        "bladder","prostate","rectum","uterus","left_ovary","right_ovary","sacrum","pelvis",
        "left_femur","right_femur","left_hip","right_hip",
        # Head/Neck
        "brain","brainstem","pituitary","left_eye","right_eye","left_lens","right_lens",
        "left_optic_nerve","right_optic_nerve","left_parotid_gland","right_parotid_gland",
        "left_submandibular_gland","right_submandibular_gland","mandible","nasal_cavity","larynx","thyroid","skull",
        # Spine
        "spinal_cord","spine_c","spine_t","spine_l","spine_s",
    }
    labels.update(fallback)

    try:
        import totalsegmentator as ts  # noqa: F401
        pkg_dir = pathlib.Path(ts.__file__).parent

        candidates = [
            pkg_dir / "resources" / "labels_total.json",     # TS >= v2 (typical)
            pkg_dir / "resources" / "labels.json",
            pkg_dir / "map_to_binary" / "labels_total.json",
            pkg_dir / "map_to_binary" / "labels.json",
        ]
        for c in candidates:
            if c.exists():
                with open(c, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # common shapes: dict[label]->id ; or {"labels":[...]} ; or plain list
                if isinstance(data, dict):
                    if "labels" in data and isinstance(data["labels"], list):
                        labels.update(map(str, data["labels"]))
                    else:
                        labels.update(map(str, data.keys()))
                elif isinstance(data, list):
                    labels.update(map(str, data))
                break
    except Exception:
        # TS not installed or resource not found: fallback set is already populated
        pass

    # Normalize: TS canonical names are lowercase underscore — keep as-is if they already are,
    # otherwise lower+underscore (if older file variants had spaces).
    norm = set()
    for s in labels:
        s = s.strip()
        s = re.sub(r"\s+", "_", s)
        norm.add(s.lower())
    return sorted(norm)


# Regex-based grouping (robust across TS versions)
_PATTERNS = [
    ("Head / Neck", [
        r"^brain$", r"^brainstem$", r"^pituitary$",
        r"^(left|right)_eye$", r"^(left|right)_lens$", r"^(left|right)_optic_nerve$",
        r"^(left|right)_parotid_gland$", r"^(left|right)_submandibular_gland$",
        r"^mandible$", r"^maxillary_sinus(_(left|right))?$", r"^nasal_cavity$",
        r"^larynx$", r"^thyroid$", r"^skull$",
        r"^spinal_cord_cervical$",  # sometimes present
    ]),
    ("Thorax", [
        r"^(left|right)_lung$", r"^heart$", r"^trachea$", r"^esophagus$",
        r"^aorta$", r"^aortic_arch$", r"^pulmonary_artery$",
        r"^(left|right)_subclavian_artery$", r"^(left|right)_subclavian_vein$",
        r"^(left|right)_brachiocephalic_vein$", r"^sternum$",
        r"^clavicle_(left|right)$|^(left|right)_clavicle$",
        r"^rib_(left|right)_[0-9]+$",
    ]),
    ("Abdomen", [
        r"^liver$", r"^gallbladder$", r"^pancreas$", r"^spleen$",
        r"^(left|right)_kidney$", r"^(left|right)_adrenal_gland$",
        r"^large_bowel$", r"^small_bowel$", r"^duodenum$", r"^stomach$",
        r"^inferior_vena_cava$", r"^portal_vein$",
    ]),
    ("Pelvis", [
        r"^bladder$", r"^prostate$", r"^rectum$", r"^uterus$",
        r"^(left|right)_ovary$", r"^(left|right)_hip$", r"^(left|right)_femur$",
        r"^sacrum$", r"^pelvis$",
    ]),
    ("Spine & Vertebrae", [
        r"^vertebra_[ctl][0-9]+$",        # vertebra_c1..c7 / t1..t12 / l1..l5
        r"^spine_[ctls]$", r"^spinal_cord$",
    ]),
]

def _group_for_label(lbl: str) -> str:
    for group_name, pats in _PATTERNS:
        for p in pats:
            if re.match(p, lbl):
                return group_name
    return "Other / Ungrouped"


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
        self.setMinimumSize(1280, 780)

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

        # Left pane: series table + refresh
        left = QWidget(); left_v = QVBoxLayout(left)
        left_v.setContentsMargins(0, 0, 0, 0); left_v.setSpacing(6)
        row_hdr = QHBoxLayout()
        row_hdr.addWidget(QLabel("Select series to send:")); row_hdr.addStretch()
        self.btn_refresh_series = QPushButton("Refresh Series")
        self.btn_refresh_series.setToolTip("Reload series list from the app")
        self.btn_refresh_series.clicked.connect(self._reload_series)
        row_hdr.addWidget(self.btn_refresh_series)
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

        # Right pane: structures with search + global controls + grouped checkboxes
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
        self.btn_expand_all = QPushButton("Expand All")
        self.btn_collapse_all = QPushButton("Collapse All")
        self.btn_select_all.clicked.connect(lambda: self._select_all(True))
        self.btn_clear_all.clicked.connect(lambda: self._select_all(False))
        self.btn_expand_all.clicked.connect(lambda: self._expand_collapse_all(True))
        self.btn_collapse_all.clicked.connect(lambda: self._expand_collapse_all(False))
        for b in (self.btn_select_all, self.btn_clear_all, self.btn_expand_all, self.btn_collapse_all):
            controls.addWidget(b)
        right_v.addLayout(controls)

        # scrollable groups
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        holder = QWidget(); self.scroll.setWidget(holder)
        self.groups_layout = QVBoxLayout(holder)
        self.groups_layout.setContentsMargins(6, 6, 6, 6); self.groups_layout.setSpacing(8)

        self._build_groups_with_ts_labels()

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

    def get_selected_series(self):
        selected = []
        for meta in self.series_rows:
            cb = self.tbl.cellWidget(meta["row"], 0)
            if cb and cb.isChecked():
                selected.append({k: meta[k] for k in ("patient","study","modality","index","label")})
        return selected

    # -------------------- structures UI --------------------
    def _build_groups_with_ts_labels(self):
        # 1) discover label universe
        labels = _discover_ts_labels()

        # 2) group them
        grouped = {}
        for lbl in labels:
            g = _group_for_label(lbl)
            grouped.setdefault(g, []).append(lbl)

        # 3) build groups in fixed order + Other
        order = ["Head / Neck", "Thorax", "Abdomen", "Pelvis", "Spine & Vertebrae", "Other / Ungrouped"]
        for group in order:
            labs = sorted(grouped.get(group, []), key=str.lower)
            if not labs:
                continue
            self._add_contour_group(group, labs)

    def _add_contour_group(self, title, labels):
        group = QGroupBox(title)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        outer = QVBoxLayout(); outer.setSpacing(6)
        header = QHBoxLayout()
        header.addWidget(QLabel(f"<b>{title}</b>"))
        header.addStretch()
        btn_toggle = QPushButton("Check All"); btn_toggle.setFixedWidth(100)
        header.addWidget(btn_toggle)
        outer.addLayout(header)

        grid = QGridLayout(); grid.setHorizontalSpacing(18); grid.setVerticalSpacing(4)
        cbs = []
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
        btn_toggle.clicked.connect(toggle)

    def _apply_filter(self, text: str):
        """Hide labels (checkboxes) that don't match the filter string."""
        pat = text.strip().lower()
        for lab, cb in self.label_to_checkbox.items():
            if not pat:
                cb.parentWidget().setVisible(True)
                cb.setVisible(True)
                continue
            show = pat in lab.lower()
            cb.setVisible(show)

    def _select_all(self, state: bool):
        for cb in self.label_to_checkbox.values():
            if cb.isVisible():  # respect current filter
                cb.setChecked(state)

    def _expand_collapse_all(self, expand: bool):
        # QGroupBox doesn't have collapse; emulate by showing/hiding the content layout
        for i in range(self.groups_layout.count()):
            w = self.groups_layout.itemAt(i).widget()
            if isinstance(w, QGroupBox):
                w.setVisible(True)  # keep group headers visible
                # If you prefer true collapse, you can setFlat(True/False) or reparent inner layout.
                # Here, we do nothing (Qt widgets inside remain), but could be extended if needed.

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
                self._select_all(True)
                params = self.build_params()
            else:
                return

        self.runSegRequested.emit(series, params)
