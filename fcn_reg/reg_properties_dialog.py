import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QGroupBox, QComboBox, QPushButton, QMessageBox, QHeaderView,
    QWidget, QApplication
)
from fcn_reg.apply_dicom_reg import (
    decompose_transform_matrix,
    find_all_image_series_in_patient,
    apply_and_duplicate_registered_series
)


class RegPropertiesDialog(QDialog):
    def __init__(self, parent, patientID, studyID, series_idx):
        super().__init__(parent)
        self.parent_app = parent
        self.patientID = patientID
        self.studyID = studyID
        self.series_idx = series_idx
        
        self.reg_series = parent.medical_image[patientID][studyID]['REG'][series_idx]
        self.metadata = self.reg_series.get('metadata', {})
        self.root_for = self.metadata.get('FrameOfReferenceUID', '')
        self.matrix_list = self.metadata.get('RegistrationMatrixList', [])
        
        # Build map of FoR -> Matrix (transforms from FoR to root_for)
        self.for_to_matrix = {self.root_for: np.eye(4)}
        for m in self.matrix_list:
            t_for = m.get('TargetFrameOfReferenceUID')
            raw = m.get('Matrix')
            if t_for and raw is not None:
                self.for_to_matrix[t_for] = np.array(raw, dtype=float).reshape((4,4))
                
        self.setWindowTitle("DICOM Spatial Registration Properties")
        self.resize(760, 720)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e24; color: #ffffff; font-size: 12px; }
            QGroupBox { font-weight: bold; border: 1px solid #3d3d4a; border-radius: 6px; margin-top: 12px; padding-top: 10px; color: #90caf9; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }
            QLabel { color: #e0e0e0; }
            QTableWidget { background-color: #252530; color: #ffffff; gridline-color: #3d3d4a; border: 1px solid #3d3d4a; border-radius: 4px; }
            QHeaderView::section { background-color: #2e2e3e; color: #90caf9; font-weight: bold; border: 1px solid #3d3d4a; padding: 4px; }
            QComboBox { background-color: #2b2b3b; color: #ffffff; border: 1px solid #4a4a5e; border-radius: 4px; padding: 5px 8px; }
            QComboBox QAbstractItemView { background-color: #252530; color: #ffffff; selection-background-color: #1976d2; }
            QPushButton { background-color: #1976d2; color: #ffffff; font-weight: bold; border-radius: 5px; padding: 8px 16px; border: none; }
            QPushButton:hover { background-color: #1565c0; }
            QPushButton#btn_close { background-color: #424242; }
            QPushButton#btn_close:hover { background-color: #616161; }
        """)
        
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(14, 14, 14, 14)

        # ─── Top Info Group ───────────────────────────────────────────
        info_group = QGroupBox("Registration Overview", self)
        info_layout = QVBoxLayout(info_group)
        
        desc = self.metadata.get('SeriesDescription', 'Image Registration')
        label = self.metadata.get('ContentLabel', '')
        date = self.metadata.get('SeriesDate', self.metadata.get('StudyDate', 'N/A'))
        
        lbl_text = (
            f"<b>Patient:</b> {self.patientID} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Registration Study:</b> Study {self.studyID} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Date:</b> {date}<br>"
            f"<b>Label:</b> {label} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Description:</b> {desc}<br>"
            f"<b>Registration Target Frame of Reference:</b> <font color='#80cbc4'>...{self.root_for[-16:]}</font>"
        )
        lbl_info = QLabel(lbl_text, info_group)
        lbl_info.setTextFormat(Qt.RichText)
        info_layout.addWidget(lbl_info)
        main_layout.addWidget(info_group)

        # ─── Series Selection for Registration ────────────────────────
        reg_action_group = QGroupBox("Apply Registration & Create Transformed Copy", self)
        reg_layout = QVBoxLayout(reg_action_group)
        reg_layout.setSpacing(10)

        all_series = find_all_image_series_in_patient(self.parent_app.medical_image, self.patientID)

        # Moving Series Combo (pre-select current study)
        h_mov = QHBoxLayout()
        lbl_m = QLabel("<b>Moving Series (to be transformed):</b>")
        lbl_m.setFixedWidth(230)
        self.combo_mov = QComboBox(reg_action_group)
        mov_default_idx = 0
        for i, s in enumerate(all_series):
            is_registered_tag = " [Registered]" if s['series_data'].get('metadata', {}).get('IsRegistered') else ""
            self.combo_mov.addItem(
                f"Study {s['studyID']} - {s['modality']} [{s['description']}]{is_registered_tag} (Shape: {s['shape']})",
                s
            )
            if str(s['studyID']) == str(self.studyID) and not s['series_data'].get('metadata', {}).get('IsRegistered'):
                mov_default_idx = i

        self.combo_mov.setCurrentIndex(mov_default_idx)
        h_mov.addWidget(lbl_m)
        h_mov.addWidget(self.combo_mov, 1)
        reg_layout.addLayout(h_mov)

        # Reference Series Combo (pre-select target study referenced in REG)
        h_ref = QHBoxLayout()
        lbl_r = QLabel("<b>Reference Series (Target Frame):</b>")
        lbl_r.setFixedWidth(230)
        self.combo_ref = QComboBox(reg_action_group)
        for s in all_series:
            is_registered_tag = " [Registered]" if s['series_data'].get('metadata', {}).get('IsRegistered') else ""
            self.combo_ref.addItem(
                f"Study {s['studyID']} - {s['modality']} [{s['description']}]{is_registered_tag} (Shape: {s['shape']})",
                s
            )

        # Find target candidate FoRs from non-identity matrix items
        target_candidate_fors = []
        for m in self.matrix_list:
            t_for = m.get('TargetFrameOfReferenceUID')
            mat = m.get('Matrix')
            if t_for:
                if mat is not None and not np.allclose(np.array(mat).reshape((4,4)), np.eye(4), atol=1e-4):
                    target_candidate_fors.insert(0, t_for)
                elif t_for != self.root_for:
                    target_candidate_fors.append(t_for)

        ref_default_idx = 0
        found_ref = False
        for cand_for in target_candidate_fors:
            for i, s in enumerate(all_series):
                if s['for_uid'] == cand_for and str(s['studyID']) != str(self.studyID) and not s['series_data'].get('metadata', {}).get('IsRegistered'):
                    ref_default_idx = i
                    found_ref = True
                    break
            if found_ref:
                break

        if not found_ref:
            for i, s in enumerate(all_series):
                if str(s['studyID']) != str(self.studyID) and not s['series_data'].get('metadata', {}).get('IsRegistered'):
                    ref_default_idx = i
                    break

        self.combo_ref.setCurrentIndex(ref_default_idx)
        h_ref.addWidget(lbl_r)
        h_ref.addWidget(self.combo_ref, 1)
        reg_layout.addLayout(h_ref)

        # ─── Matrix & Parameter Display ───────────────────────────────
        self.table_mat = QTableWidget(4, 4, reg_action_group)
        self.table_mat.setHorizontalHeaderLabels(["X'", "Y'", "Z'", "T (mm)"])
        self.table_mat.setVerticalHeaderLabels(["X", "Y", "Z", "W"])
        self.table_mat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_mat.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_mat.setFixedHeight(135)
        reg_layout.addWidget(self.table_mat)

        # Metrics Label
        self.lbl_metrics = QLabel(reg_action_group)
        self.lbl_metrics.setTextFormat(Qt.RichText)
        reg_layout.addWidget(self.lbl_metrics)

        # Live Status Label
        self.lbl_status = QLabel("", reg_action_group)
        self.lbl_status.setTextFormat(Qt.RichText)
        self.lbl_status.setAlignment(Qt.AlignCenter)
        reg_layout.addWidget(self.lbl_status)

        # Apply Button
        self.btn_apply = QPushButton("Apply Registration & Create Registered Copy", reg_action_group)
        self.btn_apply.setStyleSheet("background-color: #2e7d32; color: #ffffff; font-weight: bold; padding: 9px; font-size: 13px;")
        self.btn_apply.clicked.connect(self.on_apply_registration)
        reg_layout.addWidget(self.btn_apply)

        main_layout.addWidget(reg_action_group)

        # ─── Bottom Actions ───────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)

        btn_close = QPushButton("Close", self)
        btn_close.setObjectName("btn_close")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        main_layout.addLayout(btn_layout)

        # Connect signals
        self.combo_mov.currentIndexChanged.connect(self.update_computed_matrix)
        self.combo_ref.currentIndexChanged.connect(self.update_computed_matrix)

        # Initial calculation
        self.update_computed_matrix()

    def get_matrix_for_pair(self, mov_for, ref_for):
        """
        Computes the 4x4 matrix that transforms coordinates from mov_for to ref_for:
        P_ref = M * P_mov
        """
        M_mov_to_root = self.for_to_matrix.get(mov_for)
        M_ref_to_root = self.for_to_matrix.get(ref_for)

        if M_mov_to_root is None or M_ref_to_root is None:
            # Check if one is identity
            if mov_for == self.root_for and M_ref_to_root is not None:
                return np.linalg.inv(M_ref_to_root), True
            elif ref_for == self.root_for and M_mov_to_root is not None:
                return M_mov_to_root, True
            return np.eye(4), False

        # P_root = M_mov_to_root @ P_mov
        # P_root = M_ref_to_root @ P_ref  => P_ref = inv(M_ref_to_root) @ P_root
        # Therefore: P_ref = inv(M_ref_to_root) @ M_mov_to_root @ P_mov
        M_mov_to_ref = np.linalg.inv(M_ref_to_root) @ M_mov_to_root
        return M_mov_to_ref, True

    def update_computed_matrix(self):
        mov_data = self.combo_mov.currentData()
        ref_data = self.combo_ref.currentData()

        if not mov_data or not ref_data:
            return

        mov_for = mov_data.get('for_uid', '')
        ref_for = ref_data.get('for_uid', '')

        M, is_valid = self.get_matrix_for_pair(mov_for, ref_for)
        self.current_matrix = M

        decomp = decompose_transform_matrix(M)
        T = decomp["Translation"]
        angles = decomp["EulerAnglesDeg"]
        det = decomp["Determinant"]

        is_identity = np.allclose(M, np.eye(4), atol=1e-4)

        for r in range(4):
            for c in range(4):
                val = M[r, c]
                item = QTableWidgetItem(f"{val:10.5f}")
                item.setTextAlignment(Qt.AlignCenter)
                if r == c:
                    item.setForeground(Qt.yellow if not is_identity else Qt.white)
                elif c == 3:
                    item.setForeground(Qt.cyan)
                self.table_mat.setItem(r, c, item)

        status_txt = "<font color='#81c784'><b>Identity (Same Frame)</b></font>" if is_identity else "<font color='#ffb74d'><b>Rigid Transform Matrix</b></font>"
        if not is_valid and not is_identity:
            status_txt = "<font color='#e57373'><b>Notice: Direct transform not in this REG file (using relative transform)</b></font>"

        self.lbl_metrics.setText(
            f"<b>Status:</b> {status_txt} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Translation:</b> T<sub>x</sub> = <font color='#4fc3f7'>{T[0]:+.2f} mm</font>, "
            f"T<sub>y</sub> = <font color='#4fc3f7'>{T[1]:+.2f} mm</font>, "
            f"T<sub>z</sub> = <font color='#4fc3f7'>{T[2]:+.2f} mm</font> (Norm: <b>{np.linalg.norm(T):.2f} mm</b>)<br>"
            f"<b>Rotation:</b> Roll = <font color='#aed581'>{angles[0]:+.2f}&deg;</font>, "
            f"Pitch = <font color='#aed581'>{angles[1]:+.2f}&deg;</font>, "
            f"Yaw = <font color='#aed581'>{angles[2]:+.2f}&deg;</font> &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Det:</b> {det:.4f}"
        )

    def on_apply_registration(self):
        mov_data = self.combo_mov.currentData()
        ref_data = self.combo_ref.currentData()

        if not mov_data or not ref_data:
            return

        self.btn_apply.setEnabled(False)
        self.btn_apply.setText("Applying Registration... Please wait...")
        self.lbl_status.setText("<font color='#ffd54f'><b>Applying 3D affine registration and resampling volume... Please wait...</b></font>")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()

        try:
            new_desc = apply_and_duplicate_registered_series(
                self.parent_app,
                self.patientID,
                source_studyID=mov_data['studyID'],
                source_modality=mov_data['modality'],
                source_series_idx=mov_data['series_index'],
                target_for_uid=ref_data['for_uid'],
                matrix4x4=self.current_matrix,
                target_studyID=ref_data['studyID'],
                target_modality=ref_data['modality'],
                target_series_idx=ref_data['series_index']
            )

            self.lbl_status.setText(f"<font color='#81c784'><b>Registration completed: {new_desc}</b></font>")
            QMessageBox.information(
                self,
                "Registration Complete",
                f"Successfully transformed moving volume '{mov_data['description']}' into reference grid '{ref_data['description']}'.\n\n"
                f"Created registered dataset:\n'{new_desc}'\n\n"
                f"The new series is now in the Data Tree under Study {mov_data['studyID']}.\n"
                f"Its coordinates and Frame of Reference match Study {ref_data['studyID']}."
            )
        except Exception as e:
            self.lbl_status.setText(f"<font color='#ef5350'><b>Registration failed: {str(e)}</b></font>")
            QMessageBox.critical(self, "Error", f"Failed to apply registration:\n{str(e)}")
        finally:
            QApplication.restoreOverrideCursor()
            self.btn_apply.setEnabled(True)
            self.btn_apply.setText("Apply Registration & Create Registered Copy")
