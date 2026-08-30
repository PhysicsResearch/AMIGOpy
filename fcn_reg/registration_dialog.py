"""
Unified Registration Dialog — top-level pop-up for manual + automatic image registration.

Provides:
  - Manual translation (ΔTx, ΔTy, ΔTz in mm, 0-based offsets)
  - Manual rotation (Rx, Ry, Rz in degrees)
  - Automatic registration (Translation / Rigid / Affine) via SimpleITK
  - Live interactive preview across Axial, Coronal, and Sagittal viewports
  - Button to Apply & Save registration: creates a duplicated registered series
    AND stores a DICOM Spatial Registration (REG) matrix in medical_image.
"""

import numpy as np
import copy
from math import radians, cos, sin
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QComboBox, QDoubleSpinBox, QSpinBox, QCheckBox, QPushButton,
    QGroupBox, QMessageBox, QApplication, QFrame
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal

from fcn_reg.apply_dicom_reg import (
    decompose_transform_matrix,
    apply_and_duplicate_registered_series
)
from fcn_reg.rigid_reg_manual import (
    rotate_volume_center_aniso_fast,
    rotate_volume_center_aniso
)
from fcn_display.display_images import (
    displayaxial, displaycoronal, displaysagittal, update_layer_view
)
from fcn_display.disp_data_type import adjust_data_type_input


# ─────────────────────────────────────────────────────────────────────
# Auto-Registration Worker Thread
# ─────────────────────────────────────────────────────────────────────

class _AutoRegWorker(QThread):
    progress = Signal(str)
    finished = Signal(bool, str, object)   # success, message, result_dict

    def __init__(self, ref_data, mov_data, transform_type, metric_type,
                 use_multi_res, max_iter, fill_value=-1024.0,
                 init_user_trans=(0.0, 0.0, 0.0), init_user_rot=(0.0, 0.0, 0.0)):
        super().__init__()
        self.ref_data = ref_data
        self.mov_data = mov_data
        self.transform_type = transform_type
        self.metric_type = metric_type
        self.use_multi_res = use_multi_res
        self.max_iter = max_iter
        self.fill_value = fill_value
        self.init_user_trans = init_user_trans
        self.init_user_rot = init_user_rot

    def run(self):
        try:
            import SimpleITK as sitk
            self.progress.emit("Preparing images…")

            ref = self.ref_data
            mov = self.mov_data

            # Use data AS-IS — both come from AMIGOpy's internal coordinate system,
            # so they share the same axis conventions. No flipping needed.
            ref_img = sitk.GetImageFromArray(np.ascontiguousarray(ref['matrix'].astype(np.float32)))
            ref_img.SetSpacing((float(ref['spacing'][1]), float(ref['spacing'][0]), float(ref['thick'])))
            ref_img.SetOrigin((float(ref['origin'][0]), float(ref['origin'][1]), float(ref['origin'][2])))

            mov_img = sitk.GetImageFromArray(np.ascontiguousarray(mov['matrix'].astype(np.float32)))
            mov_img.SetSpacing((float(mov['spacing'][1]), float(mov['spacing'][0]), float(mov['thick'])))
            mov_img.SetOrigin((float(mov['origin'][0]), float(mov['origin'][1]), float(mov['origin'][2])))

            self.progress.emit("Setting up registration…")

            R = sitk.ImageRegistrationMethod()

            # 1. Similarity Metric
            if self.metric_type == "Mutual Information":
                R.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
            elif self.metric_type == "Mean Squares":
                R.SetMetricAsMeanSquares()
            else:
                R.SetMetricAsCorrelation()

            R.SetInterpolator(sitk.sitkLinear)

            # 2. Metric Sampling — 5% random for speed + quality balance
            R.SetMetricSamplingPercentage(0.05, seed=42)
            R.SetMetricSamplingStrategy(R.RANDOM)

            # 3. Optimizer — Regular Step GD is more robust than plain GD
            R.SetOptimizerAsRegularStepGradientDescent(
                learningRate=1.0,
                minStep=0.001,
                numberOfIterations=self.max_iter,
                gradientMagnitudeTolerance=1e-8,
            )
            R.SetOptimizerScalesFromPhysicalShift()

            # 4. Transform initialization
            if self.transform_type == "Translation Only (3 DoF)":
                init_tx = sitk.TranslationTransform(3)
            elif self.transform_type == "Affine (12 DoF)":
                init_tx = sitk.AffineTransform(3)
            else:   # Rigid 6 DoF
                init_tx = sitk.Euler3DTransform()

            # Initialize centered on anatomical center-of-mass (using body tissue thresholding > -500 HU)
            # This captures large lateral/vertical anatomical couch shifts accurately
            try:
                ref_body = sitk.Cast(sitk.BinaryThreshold(ref_img, lowerThreshold=-500.0, upperThreshold=3000.0, insideValue=1, outsideValue=0), sitk.sitkFloat32)
                mov_body = sitk.Cast(sitk.BinaryThreshold(mov_img, lowerThreshold=-500.0, upperThreshold=3000.0, insideValue=1, outsideValue=0), sitk.sitkFloat32)
                init_tx = sitk.CenteredTransformInitializer(
                    ref_body, mov_body, init_tx,
                    sitk.CenteredTransformInitializerFilter.MOMENTS
                )
            except Exception:
                init_tx = sitk.CenteredTransformInitializer(
                    ref_img, mov_img, init_tx,
                    sitk.CenteredTransformInitializerFilter.GEOMETRY
                )

            # Incorporate user pre-alignment values (from manual spinboxes or previous run)
            dtx, dty, dtz = self.init_user_trans
            rx_deg, ry_deg, rz_deg = self.init_user_rot

            if hasattr(init_tx, 'SetRotation') and (abs(rx_deg) > 0.001 or abs(ry_deg) > 0.001 or abs(rz_deg) > 0.001):
                init_tx.SetRotation(radians(-rx_deg), radians(-ry_deg), radians(-rz_deg))

            if abs(dtx) > 0.001 or abs(dty) > 0.001 or abs(dtz) > 0.001:
                v_init = np.array(init_tx.GetTranslation())
                init_tx.SetTranslation(tuple(v_init - np.array([dtx, dty, dtz])))

            R.SetInitialTransform(init_tx, inPlace=True)

            # 5. Multi-resolution pyramid: coarse-to-fine
            if self.use_multi_res:
                R.SetShrinkFactorsPerLevel(shrinkFactors=[4, 2, 1])
                R.SetSmoothingSigmasPerLevel(smoothingSigmas=[2, 1, 0])
                R.SetSmoothingSigmasAreSpecifiedInPhysicalUnits(True)

            def _iter_cb():
                self.progress.emit(
                    f"Iteration {R.GetOptimizerIteration()}: "
                    f"Metric = {R.GetMetricValue():.6f}"
                )
            R.AddCommand(sitk.sitkIterationEvent, _iter_cb)

            self.progress.emit("Running optimizer…")
            final_tx = R.Execute(ref_img, mov_img)

            metric = R.GetMetricValue()
            stop_cond = R.GetOptimizerStopConditionDescription()
            self.progress.emit(f"Done! Metric={metric:.6f} — Resampling…")

            # Extract 4x4 matrix M mapping physical moving coords to reference coords
            C = np.array(final_tx.GetFixedParameters()[:3], dtype=float)
            R_sitk = np.array(final_tx.GetMatrix(), dtype=float).reshape((3, 3))
            if self.transform_type == "Rigid (6 DoF)":
                V_sitk = np.array(final_tx.GetParameters()[3:6], dtype=float)
            else:
                V_sitk = np.array(final_tx.GetParameters()[:3], dtype=float)

            R_fwd = R_sitk.T
            T_fwd = C - R_fwd @ (C + V_sitk)

            M = np.eye(4, dtype=float)
            M[:3, :3] = R_fwd
            M[:3, 3] = T_fwd

            # Resample moving image directly onto reference image grid
            resampler = sitk.ResampleImageFilter()
            resampler.SetReferenceImage(ref_img)
            resampler.SetInterpolator(sitk.sitkLinear)
            resampler.SetTransform(final_tx)
            resampler.SetDefaultPixelValue(self.fill_value)
            resampled_img = resampler.Execute(mov_img)
            resampled_matrix = sitk.GetArrayFromImage(resampled_img)

            orig_ref_origin = np.array(ref['origin'], dtype=float)
            orig_mov_origin = np.array(mov['origin'], dtype=float)

            decomp = decompose_transform_matrix(M)
            net_T_mm = decomp["Translation"] - (orig_ref_origin - orig_mov_origin)
            angles_deg = decomp["EulerAnglesDeg"]

            result = {
                'matrix4x4': M,
                'resampled_matrix': resampled_matrix,
                'translation_mm': net_T_mm,
                'raw_translation_mm': decomp["Translation"],
                'rotation_deg': angles_deg,
                'metric_value': metric,
                'stop_condition': stop_cond,
                'ref_spacing': ref['spacing'],
                'ref_thick': ref['thick'],
                'ref_origin': ref['origin'],
            }

            self.finished.emit(True, "Registration completed successfully!", result)

        except Exception as e:
            import traceback
            self.finished.emit(False, f"{e}\n{traceback.format_exc()}", None)



# ─────────────────────────────────────────────────────────────────────
# Unified Registration Dialog
# ─────────────────────────────────────────────────────────────────────

class RegistrationDialog(QDialog):
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.app = parent_app
        self.worker = None
        self._saved_state = {}   # original IPP / data per layer for reset
        self._rotation_timer = QTimer()
        self._rotation_timer.setSingleShot(True)
        self._rotation_timer.timeout.connect(self._deferred_rotation)
        
        self._save_original_state()
        self._init_ui()

    # ─── UI Setup ─────────────────────────────────────────────────

    def _init_ui(self):
        self.setWindowTitle("Image Registration")
        self.setMinimumWidth(580)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e24; color: #e0e0e0; font-size: 12px; }
            QGroupBox { font-weight: bold; border: 1px solid #3d3d4a; border-radius: 6px;
                        margin-top: 12px; padding-top: 14px; color: #90caf9; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }
            QLabel { color: #e0e0e0; }
            QComboBox { background-color: #2b2b3b; color: #ffffff; border: 1px solid #4a4a5e;
                        border-radius: 4px; padding: 5px 8px; }
            QComboBox QAbstractItemView { background: #252530; color: #fff; selection-background-color: #1976d2; }
            QDoubleSpinBox, QSpinBox { background-color: #252530; color: #ffffff;
                        border: 1px solid #4a4a5e; border-radius: 3px; padding: 3px; font-weight: bold; }
            QPushButton { border-radius: 5px; padding: 7px 14px; font-weight: bold; border: none; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 14)

        # ── 1. Layer selection ─────────────────────────────────────
        grp_layers = QGroupBox("Layer Selection")
        g = QGridLayout(grp_layers)

        g.addWidget(QLabel("Reference (Fixed) Layer:"), 0, 0)
        self.combo_ref = QComboBox()
        g.addWidget(self.combo_ref, 0, 1)

        g.addWidget(QLabel("Moving Layer:"), 1, 0)
        self.combo_mov = QComboBox()
        g.addWidget(self.combo_mov, 1, 1)

        self._populate_layer_combos()
        layout.addWidget(grp_layers)

        # ── 2. Manual Translation ──────────────────────────────────
        grp_trans = QGroupBox("Manual Translation (mm)")
        gt = QGridLayout(grp_trans)

        self.spin_tx = self._make_spin(-2000, 2000, 0.0)
        self.spin_ty = self._make_spin(-2000, 2000, 0.0)
        self.spin_tz = self._make_spin(-2000, 2000, 0.0)
        self.spin_t_step = self._make_spin(0.01, 50, 1.0)

        gt.addWidget(QLabel("ΔX (L/R):"), 0, 0); gt.addWidget(self.spin_tx, 0, 1)
        gt.addWidget(QLabel("ΔY (S/I):"), 0, 2); gt.addWidget(self.spin_ty, 0, 3)
        gt.addWidget(QLabel("ΔZ (A/P):"), 0, 4); gt.addWidget(self.spin_tz, 0, 5)
        gt.addWidget(QLabel("Step:"), 1, 0); gt.addWidget(self.spin_t_step, 1, 1)

        btn_reset_t = QPushButton("Reset T")
        btn_reset_t.setStyleSheet("background-color: #555566; color: #fff;")
        btn_reset_t.clicked.connect(self._reset_translation)
        gt.addWidget(btn_reset_t, 1, 4, 1, 2)

        self.spin_tx.valueChanged.connect(self._on_alignment_input_changed)
        self.spin_ty.valueChanged.connect(self._on_alignment_input_changed)
        self.spin_tz.valueChanged.connect(self._on_alignment_input_changed)
        self.spin_t_step.valueChanged.connect(self._update_steps)

        layout.addWidget(grp_trans)

        # ── 3. Manual Rotation ─────────────────────────────────────
        grp_rot = QGroupBox("Manual Rotation (degrees)")
        gr = QGridLayout(grp_rot)

        self.spin_rx = self._make_spin(-180, 180, 0.0)
        self.spin_ry = self._make_spin(-180, 180, 0.0)
        self.spin_rz = self._make_spin(-180, 180, 0.0)
        self.spin_r_step = self._make_spin(0.01, 10, 1.0)

        gr.addWidget(QLabel("Rx (Roll):"), 0, 0); gr.addWidget(self.spin_rx, 0, 1)
        gr.addWidget(QLabel("Ry (Pitch):"), 0, 2); gr.addWidget(self.spin_ry, 0, 3)
        gr.addWidget(QLabel("Rz (Yaw):"), 0, 4); gr.addWidget(self.spin_rz, 0, 5)
        gr.addWidget(QLabel("Step:"), 1, 0); gr.addWidget(self.spin_r_step, 1, 1)

        btn_reset_r = QPushButton("Reset R")
        btn_reset_r.setStyleSheet("background-color: #555566; color: #fff;")
        btn_reset_r.clicked.connect(self._reset_rotation)
        gr.addWidget(btn_reset_r, 1, 4, 1, 2)

        self.spin_rx.valueChanged.connect(self._on_alignment_input_changed)
        self.spin_ry.valueChanged.connect(self._on_alignment_input_changed)
        self.spin_rz.valueChanged.connect(self._on_alignment_input_changed)
        self.spin_r_step.valueChanged.connect(self._update_steps)

        layout.addWidget(grp_rot)

        # ── 4. Auto Registration ───────────────────────────────────
        grp_auto = QGroupBox("Automatic Registration")
        ga = QGridLayout(grp_auto)

        ga.addWidget(QLabel("Transform:"), 0, 0)
        self.combo_transform = QComboBox()
        self.combo_transform.addItems(["Rigid (6 DoF)", "Translation Only (3 DoF)", "Affine (12 DoF)"])
        ga.addWidget(self.combo_transform, 0, 1, 1, 2)

        ga.addWidget(QLabel("Metric:"), 1, 0)
        self.combo_metric = QComboBox()
        self.combo_metric.addItems(["Mutual Information", "Mean Squares", "Correlation"])
        ga.addWidget(self.combo_metric, 1, 1, 1, 2)

        self.chk_multi_res = QCheckBox("Multi-Resolution (3 levels)")
        self.chk_multi_res.setChecked(True)
        ga.addWidget(self.chk_multi_res, 2, 0, 1, 2)

        ga.addWidget(QLabel("Max Iter:"), 2, 2)
        self.spin_max_iter = QSpinBox()
        self.spin_max_iter.setRange(20, 2000)
        self.spin_max_iter.setValue(200)
        ga.addWidget(self.spin_max_iter, 2, 3)

        self.btn_run = QPushButton("▶  Run Auto Registration")
        self.btn_run.setStyleSheet("background-color: #2e7d32; color: #ffffff; font-size: 13px; padding: 9px;")
        self.btn_run.clicked.connect(self._run_auto_reg)
        ga.addWidget(self.btn_run, 3, 0, 1, 4)

        self.lbl_status = QLabel("")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet("color: #b0bec5; font-size: 11px;")
        ga.addWidget(self.lbl_status, 4, 0, 1, 4)

        layout.addWidget(grp_auto)

        # ── 5. Action Buttons ──────────────────────────────────────
        btn_apply_save = QPushButton("💾  Apply && Save as New Registered Series")
        btn_apply_save.setStyleSheet("background-color: #2e7d32; color: #ffffff; font-size: 13px; padding: 10px;")
        btn_apply_save.clicked.connect(self._apply_and_save_new_series)
        layout.addWidget(btn_apply_save)

        hb = QHBoxLayout()

        btn_reset_all = QPushButton("Reset to Initial")
        btn_reset_all.setStyleSheet("background-color: #616161; color: #ffffff; padding: 9px;")
        btn_reset_all.clicked.connect(self._reset_all)
        hb.addWidget(btn_reset_all)

        btn_discard = QPushButton("Discard && Close")
        btn_discard.setStyleSheet("background-color: #424242; color: #ffffff; padding: 9px;")
        btn_discard.clicked.connect(self._discard_and_close)
        hb.addWidget(btn_discard)

        layout.addLayout(hb)

        # Re-sync when changing moving layer combo
        self.combo_mov.currentIndexChanged.connect(self._on_layer_selection_changed)

    # ─── Helpers ──────────────────────────────────────────────────

    def _make_spin(self, vmin, vmax, v0):
        sb = QDoubleSpinBox()
        sb.setRange(vmin, vmax)
        sb.setDecimals(2)
        sb.setSingleStep(1.0)
        sb.setValue(v0)
        sb.setMinimumWidth(80)
        return sb

    def _populate_layer_combos(self):
        self.combo_ref.clear()
        self.combo_mov.clear()
        for i in range(4):
            dd = self.app.display_data.get(i)
            if dd is not None:
                info = self._get_layer_series_info(i)
                mod = info.get('modality', '')
                desc = info.get('description', '')
                study = info.get('studyID', '')
                shape_str = f"{dd.shape[0]}×{dd.shape[1]}×{dd.shape[2]}" if dd.ndim == 3 else str(dd.shape)
                label = f"Layer {i+1}: Study {study} - {mod} [{desc}] ({shape_str})"
                self.combo_ref.addItem(label, i)
                self.combo_mov.addItem(label, i)

        if self.combo_ref.count() > 0:
            self.combo_ref.setCurrentIndex(0)
        if self.combo_mov.count() > 1:
            self.combo_mov.setCurrentIndex(1)

    def _save_original_state(self):
        """Save original IPP, Spacing, Thickness, and Matrix for all layers."""
        self._saved_state = {}
        for i in range(4):
            dd = self.app.display_data.get(i)
            if dd is not None:
                self._saved_state[i] = {
                    'origin': self.app.Im_PatPosition[i].copy(),
                    'offset': self.app.Im_Offset[i].copy(),
                    'spacing': self.app.pixel_spac[i].copy(),
                    'thick': float(self.app.slice_thick[i]),
                    'matrix': dd.copy(),
                }

    def _mov_idx(self):
        return self.combo_mov.currentData()

    def _ref_idx(self):
        return self.combo_ref.currentData()

    def _update_steps(self):
        t_step = self.spin_t_step.value()
        self.spin_tx.setSingleStep(t_step)
        self.spin_ty.setSingleStep(t_step)
        self.spin_tz.setSingleStep(t_step)
        r_step = self.spin_r_step.value()
        self.spin_rx.setSingleStep(r_step)
        self.spin_ry.setSingleStep(r_step)
        self.spin_rz.setSingleStep(r_step)

    def _on_layer_selection_changed(self):
        mov_idx = self._mov_idx()
        if mov_idx is not None and mov_idx in self._saved_state:
            for sb in (self.spin_tx, self.spin_ty, self.spin_tz,
                       self.spin_rx, self.spin_ry, self.spin_rz):
                sb.blockSignals(True)
                sb.setValue(0.0)
                sb.blockSignals(False)

    def _get_layer_series_info(self, layer_idx):
        """Finds patientID, studyID, modality, series_index, and for_uid for the layer."""
        if not hasattr(self.app, 'patientID') or not self.app.patientID:
            return {'patientID': 'Patient_01', 'studyID': '1', 'modality': 'CT', 'series_index': 0, 'for_uid': '', 'description': f"Layer {layer_idx+1}"}
        if not hasattr(self.app, 'medical_image') or self.app.patientID not in self.app.medical_image:
            return {'patientID': self.app.patientID, 'studyID': '1', 'modality': 'CT', 'series_index': 0, 'for_uid': '', 'description': f"Layer {layer_idx+1}"}

        patient_data = self.app.medical_image[self.app.patientID]
        layer_vol = self.app.display_data.get(layer_idx)
        layer_ipp = self.app.Im_PatPosition[layer_idx] if hasattr(self.app, 'Im_PatPosition') else None

        for study_id, study_dict in patient_data.items():
            if not isinstance(study_dict, dict):
                continue
            for mod, series_list in study_dict.items():
                if mod in ('REG', 'RTPLAN', 'RTSTRUCT') or not isinstance(series_list, list):
                    continue
                for s_idx, series in enumerate(series_list):
                    if not isinstance(series, dict):
                        continue
                    meta = series.get('metadata', {})
                    s_vol = series.get('3DMatrix')
                    s_ipp = meta.get('ImagePositionPatient')

                    if (s_vol is layer_vol) or (
                        s_vol is not None and layer_vol is not None and
                        s_vol.shape == layer_vol.shape and
                        s_ipp is not None and layer_ipp is not None and
                        np.allclose(s_ipp, layer_ipp[:3], atol=1.0)
                    ):
                        return {
                            'patientID': self.app.patientID,
                            'studyID': study_id,
                            'modality': mod,
                            'series_index': s_idx,
                            'for_uid': meta.get('FrameOfReferenceUID', ''),
                            'description': meta.get('SeriesDescription', '') or mod,
                            'series_data': series
                        }

        return {
            'patientID': getattr(self.app, 'patientID', 'Patient_01'),
            'studyID': getattr(self.app, 'studyID', '1'),
            'modality': getattr(self.app, 'modality', 'CT'),
            'series_index': getattr(self.app, 'series_index', 0),
            'for_uid': f"for_layer_{layer_idx}",
            'description': f"Layer {layer_idx+1}",
            'series_data': {}
        }

    # ─── Live Viewport Updates ────────────────────────────────────

    def _on_alignment_input_changed(self, _=None):
        mov_idx = self._mov_idx()
        ref_idx = self._ref_idx()
        if mov_idx is None or mov_idx not in self._saved_state:
            return

        orig_origin = self._saved_state[mov_idx]['origin']
        orig_vol = self._saved_state[mov_idx]['matrix']

        dtx = self.spin_tx.value() # ΔX: Left / Right (DICOM X, index 0)
        dty = self.spin_ty.value() # ΔY: Superior / Inferior (DICOM Z, index 2)
        dtz = self.spin_tz.value() # ΔZ: Anterior / Posterior (DICOM Y, index 1)

        rx = self.spin_rx.value()
        ry = self.spin_ry.value()
        rz = self.spin_rz.value()

        # 1. Update physical ImagePositionPatient
        self.app.Im_PatPosition[mov_idx, 0] = orig_origin[0] + dtx
        self.app.Im_PatPosition[mov_idx, 2] = orig_origin[2] + dty
        self.app.Im_PatPosition[mov_idx, 1] = orig_origin[1] - dtz

        # 2. Handle Rotation
        if abs(rx) < 0.01 and abs(ry) < 0.01 and abs(rz) < 0.01:
            # Restore original unrotated volume
            self.app.display_data[mov_idx] = orig_vol
            self.app.pixel_spac[mov_idx] = self._saved_state[mov_idx]['spacing'].copy()
            self.app.slice_thick[mov_idx] = self._saved_state[mov_idx]['thick']
        else:
            self.app._ax = rx
            self.app._ay = ry
            self.app._az = rz
            # Fast low-res preview
            self.app.display_data[mov_idx] = rotate_volume_center_aniso_fast(
                self.app, orig_vol, rx, ry, rz, ds=3
            )
            # Schedule deferred full quality rotation
            self._rotation_timer.start(300)

        adjust_data_type_input(self.app, mov_idx)
        self._recalc_offsets(mov_idx)
        self._refresh_views()

    def _deferred_rotation(self):
        mov_idx = self._mov_idx()
        if mov_idx is None or mov_idx not in self._saved_state:
            return

        rx = self.spin_rx.value()
        ry = self.spin_ry.value()
        rz = self.spin_rz.value()

        if abs(rx) < 0.01 and abs(ry) < 0.01 and abs(rz) < 0.01:
            return

        orig_vol = self._saved_state[mov_idx]['matrix']
        self.app.display_data[mov_idx] = rotate_volume_center_aniso(
            self.app, orig_vol, rx, ry, rz, order=0
        )
        adjust_data_type_input(self.app, mov_idx)
        self._recalc_offsets(mov_idx)
        self._refresh_views()

    def _reset_translation(self):
        for sb in (self.spin_tx, self.spin_ty, self.spin_tz):
            sb.blockSignals(True)
            sb.setValue(0.0)
            sb.blockSignals(False)
        self._on_alignment_input_changed()

    def _reset_rotation(self):
        for sb in (self.spin_rx, self.spin_ry, self.spin_rz):
            sb.blockSignals(True)
            sb.setValue(0.0)
            sb.blockSignals(False)
        self._on_alignment_input_changed()

    def _reset_all(self):
        self._reset_translation()
        self._reset_rotation()
        self.lbl_status.setText("<font color='#b0bec5'>Reset to initial alignment.</font>")

    def _recalc_offsets(self, idx):
        ref_idx = self._ref_idx() or 0
        self.app.Im_Offset[idx, 0] = (self.app.Im_PatPosition[idx, 0] - self.app.Im_PatPosition[ref_idx, 0])
        self.app.Im_Offset[idx, 1] = (
            self.app.display_data[ref_idx].shape[1] * self.app.pixel_spac[ref_idx, 0]
            - self.app.display_data[idx].shape[1] * self.app.pixel_spac[idx, 0]
        ) - (self.app.Im_PatPosition[idx, 1] - self.app.Im_PatPosition[ref_idx, 1])
        self.app.Im_Offset[idx, 2] = (self.app.Im_PatPosition[idx, 2] - self.app.Im_PatPosition[ref_idx, 2])

    def _refresh_views(self):
        displaycoronal(self.app)
        displaysagittal(self.app)
        displayaxial(self.app)
        update_layer_view(self.app)

    # ─── Auto Registration ────────────────────────────────────────

    def _run_auto_reg(self):
        ref_idx = self._ref_idx()
        mov_idx = self._mov_idx()
        if ref_idx is None or mov_idx is None:
            QMessageBox.warning(self, "No Layers", "Both Reference and Moving layers must be selected.")
            return
        if ref_idx == mov_idx:
            QMessageBox.warning(self, "Invalid Selection", "Reference and Moving layers must be different.")
            return

        self.btn_run.setEnabled(False)
        self.btn_run.setText("⏳  Optimizing Registration…")
        self.lbl_status.setText("<font color='#ffd54f'><b>Running multi-resolution automatic registration…</b></font>")
        QApplication.processEvents()

        ref_data = {
            'matrix': self._saved_state[ref_idx]['matrix'],
            'spacing': self._saved_state[ref_idx]['spacing'],
            'thick':   self._saved_state[ref_idx]['thick'],
            'origin':  self._saved_state[ref_idx]['origin'],
        }
        mov_data = {
            'matrix': self._saved_state[mov_idx]['matrix'],
            'spacing': self._saved_state[mov_idx]['spacing'],
            'thick':   self._saved_state[mov_idx]['thick'],
            'origin':  self._saved_state[mov_idx]['origin'],
        }

        fill_val = -1024.0
        if hasattr(self.app, 'reg_fill_value'):
            fill_val = float(self.app.reg_fill_value.value())

        user_trans = (float(self.spin_tx.value()), -float(self.spin_tz.value()), float(self.spin_ty.value()))
        user_rot = (float(self.spin_rx.value()), float(self.spin_ry.value()), float(self.spin_rz.value()))

        self.worker = _AutoRegWorker(
            ref_data, mov_data,
            self.combo_transform.currentText(),
            self.combo_metric.currentText(),
            self.chk_multi_res.isChecked(),
            self.spin_max_iter.value(),
            fill_val,
            init_user_trans=user_trans,
            init_user_rot=user_rot,
        )
        self.worker.progress.connect(self._on_auto_progress)
        self.worker.finished.connect(self._on_auto_finished)
        self.worker.start()

    def _on_auto_progress(self, msg):
        self.lbl_status.setText(f"<font color='#ffd54f'>{msg}</font>")

    def _on_auto_finished(self, success, message, result):
        self.btn_run.setEnabled(True)
        self.btn_run.setText("▶  Run Auto Registration")

        if not success:
            self.lbl_status.setText(f"<font color='#ef5350'><b>Failed: {message}</b></font>")
            QMessageBox.critical(self, "Registration Error", f"Registration failed:\n{message}")
            return

        T_lps = result['translation_mm']
        angles = result['rotation_deg']

        t_lr = float(T_lps[0])
        t_si = float(T_lps[2])
        t_ap = -float(T_lps[1])
        rx = float(angles[0])
        ry = float(angles[1])
        rz = float(angles[2])

        # 1. Update display layer with the resampled volume for perfect alignment
        mov_idx = self._mov_idx()
        ref_idx = self._ref_idx()
        if mov_idx is not None and mov_idx in self._saved_state:
            orig_dtype = self._saved_state[mov_idx]['matrix'].dtype
            resampled_mat = result['resampled_matrix'].astype(orig_dtype)
            self.app.display_data[mov_idx] = resampled_mat
            self.app.pixel_spac[mov_idx] = np.array(result['ref_spacing'], dtype=float)
            self.app.slice_thick[mov_idx] = float(result['ref_thick'])
            self.app.Im_PatPosition[mov_idx] = np.array(result['ref_origin'], dtype=float)

            adjust_data_type_input(self.app, mov_idx)

            # Update spinboxes WITH the computed values so the user can see and adjust them!
            for sb in (self.spin_tx, self.spin_ty, self.spin_tz,
                       self.spin_rx, self.spin_ry, self.spin_rz):
                sb.blockSignals(True)

            self.spin_tx.setValue(t_lr)
            self.spin_ty.setValue(t_si)
            self.spin_tz.setValue(t_ap)
            self.spin_rx.setValue(rx)
            self.spin_ry.setValue(ry)
            self.spin_rz.setValue(rz)

            for sb in (self.spin_tx, self.spin_ty, self.spin_tz,
                       self.spin_rx, self.spin_ry, self.spin_rz):
                sb.blockSignals(False)

            self._recalc_offsets(mov_idx)
            self._refresh_views()

        self.lbl_status.setText(
            f"<font color='#81c784'><b>✓ Auto Registration Applied & Aligned!</b></font><br>"
            f"ΔX (L/R) = {t_lr:+.2f} mm ({t_lr/10.0:+.2f} cm) &nbsp;|&nbsp; "
            f"ΔY (S/I) = {t_si:+.2f} mm ({t_si/10.0:+.2f} cm) &nbsp;|&nbsp; "
            f"ΔZ (A/P) = {t_ap:+.2f} mm ({t_ap/10.0:+.2f} cm)<br>"
            f"Rot = ({rx:+.2f}°, {ry:+.2f}°, {rz:+.2f}°) &nbsp;|&nbsp; "
            f"Metric: {result['metric_value']:.4f}"
        )

    # ─── Compute 4x4 Matrix from Current Spinboxes ─────────────────

    def _compute_current_matrix4x4(self):
        """Constructs the 4x4 matrix mapping physical moving coords to reference coords."""
        mov_idx = self._mov_idx()
        orig_origin = self._saved_state[mov_idx]['origin']
        orig_vol = self._saved_state[mov_idx]['matrix']
        spacing = self._saved_state[mov_idx]['spacing']
        thick = self._saved_state[mov_idx]['thick']

        dtx = self.spin_tx.value() # L/R (DICOM X)
        dty = self.spin_ty.value() # S/I (DICOM Z)
        dtz = self.spin_tz.value() # A/P (DICOM -Y)
        rx_deg = self.spin_rx.value()
        ry_deg = self.spin_ry.value()
        rz_deg = self.spin_rz.value()

        # Rotation matrix around volume center
        ax, ay, az = radians(rx_deg), radians(ry_deg), radians(rz_deg)
        Rx = np.array([[1, 0, 0], [0, cos(ax), -sin(ax)], [0, sin(ax), cos(ax)]], dtype=float)
        Ry = np.array([[cos(ay), 0, sin(ay)], [0, 1, 0], [-sin(ay), 0, cos(ay)]], dtype=float)
        Rz = np.array([[cos(az), -sin(az), 0], [sin(az), cos(az), 0], [0, 0, 1]], dtype=float)
        R = Rz @ (Ry @ Rx)

        # Physical center of moving volume in LPS
        D, H, W = orig_vol.shape # (Nz, Ny, Nx)
        center_lps = orig_origin + np.array([W * spacing[1], H * spacing[0], D * thick]) / 2.0

        T_vec = np.array([dtx, -dtz, dty], dtype=float)
        translation_component = center_lps - R @ center_lps + T_vec

        M = np.eye(4, dtype=float)
        M[:3, :3] = R
        M[:3, 3] = translation_component

        return M

    # ─── Apply & Save as Registered Dataset + REG Matrix ───────────

    def _apply_and_save_new_series(self):
        mov_idx = self._mov_idx()
        ref_idx = self._ref_idx()

        if mov_idx is None or ref_idx is None:
            QMessageBox.warning(self, "Error", "Invalid layer selection.")
            return

        M = self._compute_current_matrix4x4()
        mov_info = self._get_layer_series_info(mov_idx)
        ref_info = self._get_layer_series_info(ref_idx)

        patientID = mov_info['patientID']
        source_studyID = mov_info['studyID']
        source_modality = mov_info['modality']
        source_series_idx = mov_info['series_index']

        target_for_uid = ref_info.get('for_uid') or mov_info.get('for_uid') or "REG_TARGET_FOR"
        target_studyID = ref_info.get('studyID')
        target_modality = ref_info.get('modality')
        target_series_idx = ref_info.get('series_index')

        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()

        try:
            current_vol = self.app.display_data[mov_idx]
            current_origin = self.app.Im_PatPosition[mov_idx]
            current_spacing = self.app.pixel_spac[mov_idx]
            current_thick = self.app.slice_thick[mov_idx]

            new_desc = apply_and_duplicate_registered_series(
                self.app,
                patientID=patientID,
                source_studyID=source_studyID,
                source_modality=source_modality,
                source_series_idx=source_series_idx,
                target_for_uid=target_for_uid,
                matrix4x4=M,
                target_studyID=target_studyID,
                target_modality=target_modality,
                target_series_idx=target_series_idx,
                precomputed_volume=current_vol,
                precomputed_origin=current_origin,
                precomputed_spacing=current_spacing,
                precomputed_thick=current_thick
            )

            # Load the newly created registered series directly into the moving layer
            new_series_list = self.app.medical_image[patientID][source_studyID][source_modality]
            new_series = new_series_list[-1]
            new_vol = new_series['3DMatrix']
            new_meta = new_series['metadata']

            self.app.display_data[mov_idx] = new_vol
            self.app.pixel_spac[mov_idx] = np.array(new_meta['PixelSpacing'], dtype=float)
            self.app.slice_thick[mov_idx] = float(new_meta['SliceThickness'])
            self.app.Im_PatPosition[mov_idx] = np.array(new_meta['ImagePositionPatient'], dtype=float)
            adjust_data_type_input(self.app, mov_idx)

            self._recalc_offsets(mov_idx)
            self._refresh_views()

            QApplication.restoreOverrideCursor()
            QMessageBox.information(
                self,
                "Registration Saved",
                f"Successfully created registered dataset and DICOM Spatial Registration (REG) matrix!\n\n"
                f"• Registered Series: '{new_desc}'\n"
                f"• Target Frame: Study {target_studyID}\n"
                f"• Stored in Study {source_studyID} under '{source_modality}' and 'REG'.\n\n"
                f"Both the transformed dataset and its REG matrix are now available in the Data Tree."
            )
            if hasattr(self.app, '_reg_dialog'):
                self.app._reg_dialog = None
            self.accept()
            self.close()

        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Save Error", f"Failed to save registered series:\n{str(e)}")

    # ─── Apply to View & Close ────────────────────────────────────

    def _apply_and_close(self):
        mov_idx = self._mov_idx()
        if mov_idx is not None and hasattr(self.app, 'Reg_manual_Tx'):
            # Sync sidebar spinboxes if present
            self.app.Reg_manual_Tx.blockSignals(True)
            self.app.Reg_manual_Tx.setValue(float(self.app.Im_PatPosition[mov_idx, 0]))
            self.app.Reg_manual_Tx.blockSignals(False)

            self.app.Reg_manual_Ty.blockSignals(True)
            self.app.Reg_manual_Ty.setValue(float(self.app.Im_PatPosition[mov_idx, 2]))
            self.app.Reg_manual_Ty.blockSignals(False)

    def closeEvent(self, event):
        if hasattr(self.app, '_reg_dialog'):
            self.app._reg_dialog = None
        event.accept()

    # ─── Discard & Close ──────────────────────────────────────────

    def _discard_and_close(self):
        for idx, saved in self._saved_state.items():
            self.app.display_data[idx] = saved['matrix']
            self.app.Im_PatPosition[idx] = saved['origin'].copy()
            self.app.Im_Offset[idx] = saved['offset'].copy()
            self.app.pixel_spac[idx] = saved['spacing'].copy()
            self.app.slice_thick[idx] = saved['thick']
            adjust_data_type_input(self.app, idx)

        self._refresh_views()
        if hasattr(self.app, '_reg_dialog'):
            self.app._reg_dialog = None
        self.reject()
        self.close()


# ─── Public entry-point ──────────────────────────────────────────────

def open_registration_dialog(parent_app):
    if hasattr(parent_app, '_reg_dialog') and parent_app._reg_dialog is not None:
        try:
            parent_app._reg_dialog.show()
            parent_app._reg_dialog.raise_()
            parent_app._reg_dialog.activateWindow()
            return parent_app._reg_dialog
        except RuntimeError:
            parent_app._reg_dialog = None

    dlg = RegistrationDialog(parent_app)
    dlg.setWindowModality(Qt.NonModal)
    parent_app._reg_dialog = dlg
    dlg.show()
    return dlg
