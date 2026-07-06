import numpy as np
import SimpleITK as sitk
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox, QCheckBox, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QThread, Signal

class RegistrationWorker(QThread):
    progress_signal = Signal(str)
    finished_signal = Signal(bool, str, object) # success, message, result_dict

    def __init__(self, parent_app, ref_idx, mov_idx, transform_type, metric_type, use_multi_res, max_iter, resample_to_ref):
        super().__init__()
        self.parent_app = parent_app
        self.ref_idx = ref_idx
        self.mov_idx = mov_idx
        self.transform_type = transform_type
        self.metric_type = metric_type
        self.use_multi_res = use_multi_res
        self.max_iter = max_iter
        self.resample_to_ref = resample_to_ref

    def run(self):
        try:
            self.progress_signal.emit("Preparing images...")
            
            # Get reference data
            ref_matrix = self.parent_app.display_data[self.ref_idx]
            ref_thick = float(self.parent_app.slice_thick[self.ref_idx])
            ref_spacing = self.parent_app.pixel_spac[self.ref_idx]
            ref_origin = self.parent_app.Im_PatPosition[self.ref_idx]
            
            # Get moving data
            mov_matrix = self.parent_app.display_data[self.mov_idx]
            mov_thick = float(self.parent_app.slice_thick[self.mov_idx])
            mov_spacing = self.parent_app.pixel_spac[self.mov_idx]
            mov_origin = self.parent_app.Im_PatPosition[self.mov_idx]

            # Convert to SimpleITK Images (Z,Y,X) -> sitk expects (X,Y,Z)
            ref_image = sitk.GetImageFromArray(np.ascontiguousarray(ref_matrix.astype(np.float32)))
            ref_image.SetSpacing((float(ref_spacing[1]), float(ref_spacing[0]), float(ref_thick)))
            ref_image.SetOrigin((float(ref_origin[0]), float(ref_origin[1]), float(ref_origin[2])))
            
            mov_image = sitk.GetImageFromArray(np.ascontiguousarray(mov_matrix.astype(np.float32)))
            mov_image.SetSpacing((float(mov_spacing[1]), float(mov_spacing[0]), float(mov_thick)))
            mov_image.SetOrigin((float(mov_origin[0]), float(mov_origin[1]), float(mov_origin[2])))

            self.progress_signal.emit("Setting up registration framework...")
            
            # Setup registration method
            R = sitk.ImageRegistrationMethod()
            
            # Set metric
            if self.metric_type == "Mutual Information":
                R.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
            elif self.metric_type == "Mean Squares":
                R.SetMetricAsMeanSquares()
            else:
                R.SetMetricAsCorrelation()
                
            # Set interpolator
            R.SetInterpolator(sitk.sitkLinear)
            
            # Setup random metric sampling to drastically speed up optimization
            R.SetMetricSamplingPercentage(0.02, seed=123)
            R.SetMetricSamplingStrategy(R.RANDOM)
            
            # Set optimizer
            R.SetOptimizerAsGradientDescent(
                learningRate=1.0, 
                numberOfIterations=self.max_iter, 
                convergenceMinimumValue=1e-6, 
                convergenceWindowSize=10
            )
            R.SetOptimizerScalesFromPhysicalShift()
            
            # Set initial transform
            if self.transform_type == "Translation Only (3 DoF)":
                initial_transform = sitk.TranslationTransform(3)
            elif self.transform_type == "Affine (12 DoF)":
                initial_transform = sitk.AffineTransform(3)
            else: # Rigid 6 DoF
                initial_transform = sitk.Euler3DTransform()
                
            # Initialize transform centered on geometry
            initial_transform = sitk.CenteredTransformInitializer(
                ref_image, 
                mov_image, 
                initial_transform, 
                sitk.CenteredTransformInitializerFilter.GEOMETRY
            )
            R.SetInitialTransform(initial_transform, inPlace=False)
            
            # Setup multi-resolution if selected
            if self.use_multi_res:
                R.SetShrinkFactorsPerLevel(shrinkFactors = [4, 2, 1])
                R.SetSmoothingSigmasPerLevel(smoothingSigmas = [2, 1, 0])
                R.SetSmoothingSigmasAreSpecifiedInPhysicalUnits(True)

            # Iteration observer to update progress
            def command_iteration():
                self.progress_signal.emit(f"Optimizing... Iteration {R.GetOptimizerIteration()}: Metric={R.GetMetricValue():.4f}")
            
            R.AddCommand(sitk.sitkIterationEvent, command_iteration)

            self.progress_signal.emit("Running optimizer...")
            final_transform = R.Execute(ref_image, mov_image)
            self.progress_signal.emit("Registration completed! Resampling image...")

            result_dict = {}

            if self.resample_to_ref:
                # Resample moving image directly onto fixed grid
                resampler = sitk.ResampleImageFilter()
                resampler.SetReferenceImage(ref_image)
                resampler.SetInterpolator(sitk.sitkLinear)
                resampler.SetTransform(final_transform)
                resampler.SetDefaultPixelValue(float(self.parent_app.reg_fill_value.value()))
                
                resampled_img = resampler.Execute(mov_image)
                resampled_matrix = sitk.GetArrayFromImage(resampled_img)
                
                result_dict['matrix'] = resampled_matrix
                result_dict['spacing'] = ref_spacing
                result_dict['thick'] = ref_thick
                result_dict['origin'] = ref_origin
            else:
                # Just update coordinates / transform
                if self.transform_type == "Translation Only (3 DoF)":
                    # Translation only does not require resampling the voxel grid
                    translation = final_transform.GetParameters()
                    new_origin = np.array(mov_origin) - np.array(translation)
                    result_dict['matrix'] = mov_matrix
                    result_dict['spacing'] = mov_spacing
                    result_dict['thick'] = mov_thick
                    result_dict['origin'] = new_origin
                else:
                    # Rigid / Affine with rotation/shearing MUST resample, but we can do it on its own grid bounding box
                    resampler = sitk.ResampleImageFilter()
                    resampler.SetReferenceImage(ref_image)
                    resampler.SetInterpolator(sitk.sitkLinear)
                    resampler.SetTransform(final_transform)
                    resampler.SetDefaultPixelValue(float(self.parent_app.reg_fill_value.value()))
                    
                    resampled_img = resampler.Execute(mov_image)
                    resampled_matrix = sitk.GetArrayFromImage(resampled_img)
                    
                    # Store as reference-matched spacing & grid
                    result_dict['matrix'] = resampled_matrix
                    result_dict['spacing'] = ref_spacing
                    result_dict['thick'] = ref_thick
                    result_dict['origin'] = ref_origin
            
            result_dict['transform'] = final_transform
            self.finished_signal.emit(True, "Registration succeeded!", result_dict)
            
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self.finished_signal.emit(False, f"Error: {str(e)}\n{tb}", None)


class AutoRegDialog(QDialog):
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Automatic Image Registration")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 1. Reference & Moving Layer Selection
        layout.addWidget(QLabel("<b>Layer Selection:</b>"))
        
        lay_select_layout = QHBoxLayout()
        lay_select_layout.addWidget(QLabel("Reference (Fixed) Layer:"))
        self.combo_ref = QComboBox()
        lay_select_layout.addWidget(self.combo_ref)
        
        lay_select_layout.addWidget(QLabel("Moving Layer:"))
        self.combo_mov = QComboBox()
        lay_select_layout.addWidget(self.combo_mov)
        layout.addLayout(lay_select_layout)
        
        # Populate combos
        for i in range(4):
            if i in self.parent_app.display_data and self.parent_app.display_data[i] is not None:
                modality_str = getattr(self.parent_app, 'modality', 'DICOM') if i == 0 else ""
                label = f"Layer {i} ({modality_str})" if modality_str else f"Layer {i}"
                self.combo_ref.addItem(label, i)
                self.combo_mov.addItem(label, i)
                
        # Set defaults
        if self.combo_ref.count() > 0:
            self.combo_ref.setCurrentIndex(0) # Layer 0 is default reference
        if self.combo_mov.count() > 1:
            self.combo_mov.setCurrentIndex(1) # Layer 1 is default moving
            
        layout.addWidget(QLabel("<hr>"))
        
        # 2. Options Settings
        layout.addWidget(QLabel("<b>Registration Parameters:</b>"))
        
        # Transform type
        t_layout = QHBoxLayout()
        t_layout.addWidget(QLabel("Transform Model:"))
        self.combo_transform = QComboBox()
        self.combo_transform.addItems(["Rigid (6 DoF)", "Translation Only (3 DoF)", "Affine (12 DoF)"])
        t_layout.addWidget(self.combo_transform)
        layout.addLayout(t_layout)
        
        # Metric
        m_layout = QHBoxLayout()
        m_layout.addWidget(QLabel("Similarity Metric:"))
        self.combo_metric = QComboBox()
        self.combo_metric.addItems(["Mutual Information", "Mean Squares", "Normalized Correlation"])
        m_layout.addWidget(self.combo_metric)
        layout.addLayout(m_layout)
        
        # Resolution scale
        r_layout = QHBoxLayout()
        r_layout.addWidget(QLabel("Resolution Scale:"))
        self.combo_res = QComboBox()
        self.combo_res.addItems(["Multi-Resolution (3 Levels)", "Single-Resolution (1 Level)"])
        r_layout.addWidget(self.combo_res)
        layout.addLayout(r_layout)
        
        # Max Iterations
        it_layout = QHBoxLayout()
        it_layout.addWidget(QLabel("Max Iterations:"))
        self.spin_iter = QSpinBox()
        self.spin_iter.setRange(10, 1000)
        self.spin_iter.setValue(100)
        it_layout.addWidget(self.spin_iter)
        layout.addLayout(it_layout)
        
        # Resample checkbox
        self.chk_resample = QCheckBox("Resample moving image to reference grid")
        self.chk_resample.setChecked(True)
        layout.addWidget(self.chk_resample)
        
        layout.addWidget(QLabel("<hr>"))
        
        # 3. Status label
        self.lbl_status = QLabel("Ready to start registration.")
        self.lbl_status.setWordWrap(True)
        layout.addWidget(self.lbl_status)
        
        # 4. Run / Cancel actions
        act_layout = QHBoxLayout()
        self.btn_run = QPushButton("Start Registration")
        self.btn_run.setStyleSheet("background-color: darkgreen; color: white; font-weight: bold;")
        self.btn_run.clicked.connect(self.run_registration)
        act_layout.addWidget(self.btn_run)
        
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        act_layout.addWidget(self.btn_close)
        
        layout.addLayout(act_layout)

    def run_registration(self):
        ref_idx = self.combo_ref.currentData()
        mov_idx = self.combo_mov.currentData()
        
        if ref_idx == mov_idx:
            QMessageBox.warning(self, "Invalid Selection", "Reference Layer and Moving Layer must be different.")
            return
            
        self.btn_run.setEnabled(False)
        self.combo_ref.setEnabled(False)
        self.combo_mov.setEnabled(False)
        self.combo_transform.setEnabled(False)
        self.combo_metric.setEnabled(False)
        self.combo_res.setEnabled(False)
        self.spin_iter.setEnabled(False)
        self.chk_resample.setEnabled(False)
        
        transform_type = self.combo_transform.currentText()
        metric_type = self.combo_metric.currentText()
        use_multi_res = "Multi-Resolution" in self.combo_res.currentText()
        max_iter = self.spin_iter.value()
        resample_to_ref = self.chk_resample.isChecked()
        
        self.lbl_status.setText("Initializing registration thread...")
        
        self.worker = RegistrationWorker(
            self.parent_app, ref_idx, mov_idx, transform_type, metric_type, use_multi_res, max_iter, resample_to_ref
        )
        self.worker.progress_signal.connect(self.lbl_status.setText)
        self.worker.finished_signal.connect(self.registration_finished)
        self.worker.start()

    def registration_finished(self, success, message, result_dict):
        self.btn_run.setEnabled(True)
        self.combo_ref.setEnabled(True)
        self.combo_mov.setEnabled(True)
        self.combo_transform.setEnabled(True)
        self.combo_metric.setEnabled(True)
        self.combo_res.setEnabled(True)
        self.spin_iter.setEnabled(True)
        self.chk_resample.setEnabled(True)
        
        if success:
            self.lbl_status.setText("Success: Registration completed!")
            
            mov_idx = self.combo_mov.currentData()
            original_dtype = self.parent_app.display_data[mov_idx].dtype
            
            # Apply results to parent app, casting back to original dtype
            self.parent_app.display_data[mov_idx] = result_dict['matrix'].astype(original_dtype)
            self.parent_app.pixel_spac[mov_idx] = result_dict['spacing']
            self.parent_app.slice_thick[mov_idx] = result_dict['thick']
            self.parent_app.Im_PatPosition[mov_idx] = result_dict['origin']
            
            # Recalculate physical workspace offsets
            from fcn_reg.rigid_reg_manual import update_view
            self.parent_app.Im_Offset[mov_idx, 0] = (self.parent_app.Im_PatPosition[mov_idx, 0] - self.parent_app.Im_PatPosition[0, 0])
            self.parent_app.Im_Offset[mov_idx, 1] = (self.parent_app.display_data[0].shape[1] * self.parent_app.pixel_spac[0, 0] - self.parent_app.display_data[mov_idx].shape[1] * self.parent_app.pixel_spac[mov_idx, 0]) - (self.parent_app.Im_PatPosition[mov_idx, 1] - self.parent_app.Im_PatPosition[0, 1])
            self.parent_app.Im_Offset[mov_idx, 2] = (self.parent_app.Im_PatPosition[mov_idx, 2] - self.parent_app.Im_PatPosition[0, 2])
            
            # Sync sliders/spinboxes if current layer is the moving layer
            if self.parent_app.layer_selected.currentIndex() == mov_idx:
                was_x = self.parent_app.Reg_manual_Tx.blockSignals(True)
                self.parent_app.Reg_manual_Tx.setValue(float(result_dict['origin'][0]))
                self.parent_app.Reg_manual_Tx.blockSignals(was_x)
                
                was_y = self.parent_app.Reg_manual_Ty.blockSignals(True)
                self.parent_app.Reg_manual_Ty.setValue(float(result_dict['origin'][2]))  # Swap Y to Z
                self.parent_app.Reg_manual_Ty.blockSignals(was_y)
                
                was_z = self.parent_app.Reg_manual_Tz.blockSignals(True)
                self.parent_app.Reg_manual_Tz.setValue(-float(result_dict['origin'][1])) # Swap Z to Y, and flip Y
                self.parent_app.Reg_manual_Tz.blockSignals(was_z)
            
            # Save the last registration parameters on parent_app
            self.parent_app.last_reg_transform = {
                'transform': result_dict.get('transform'),
                'resample_to_ref': self.chk_resample.isChecked(),
                'transform_type': self.combo_transform.currentText(),
                'ref_idx': self.combo_ref.currentData()
            }
            update_view(self.parent_app)
            QMessageBox.information(self, "Registration Completed", "Automatic image registration completed successfully!")
        else:
            self.lbl_status.setText(f"Registration failed.")
            QMessageBox.critical(self, "Registration Error", f"Registration failed:\n{message}")


def open_auto_reg_dialog(parent_app):
    dialog = AutoRegDialog(parent_app)
    dialog.exec()

def apply_last_transform_to_layer(self):
    if not hasattr(self, 'last_reg_transform') or self.last_reg_transform is None:
        QMessageBox = None
        try:
            from PySide6.QtWidgets import QMessageBox
        except:
            pass
        if QMessageBox:
            QMessageBox.warning(self, "No Transform Recorded", "No automatic registration transform has been recorded yet in this session.")
        return

    idx = self.layer_selected.currentIndex()
    info = self.last_reg_transform
    ref_idx = info['ref_idx']
    
    QMessageBox = None
    try:
        from PySide6.QtWidgets import QMessageBox
    except:
        pass

    if idx == ref_idx:
        if QMessageBox:
            QMessageBox.warning(self, "Invalid Layer", f"Cannot apply the transform to Layer {idx} because it is the Reference Layer.")
        return
        
    mov_matrix = self.display_data[idx]
    if mov_matrix is None:
        if QMessageBox:
            QMessageBox.warning(self, "No Image", f"No image is loaded in Layer {idx}.")
        return

    resample_to_ref = info['resample_to_ref']
    final_transform = info['transform']
    transform_type = info['transform_type']
    
    # Get reference grid parameters
    ref_matrix = self.display_data[ref_idx]
    ref_thick = float(self.slice_thick[ref_idx])
    ref_spacing = self.pixel_spac[ref_idx]
    ref_origin = self.Im_PatPosition[ref_idx]
    
    # Get moving grid parameters
    mov_thick = float(self.slice_thick[idx])
    mov_spacing = self.pixel_spac[idx]
    mov_origin = self.Im_PatPosition[idx]

    try:
        original_dtype = self.display_data[idx].dtype
        import SimpleITK as sitk
        
        # Convert to sitk Images
        ref_image = sitk.GetImageFromArray(np.ascontiguousarray(ref_matrix.astype(np.float32)))
        ref_image.SetSpacing((float(ref_spacing[1]), float(ref_spacing[0]), float(ref_thick)))
        ref_image.SetOrigin((float(ref_origin[0]), float(ref_origin[1]), float(ref_origin[2])))
        
        mov_image = sitk.GetImageFromArray(np.ascontiguousarray(mov_matrix.astype(np.float32)))
        mov_image.SetSpacing((float(mov_spacing[1]), float(mov_spacing[0]), float(mov_thick)))
        mov_image.SetOrigin((float(mov_origin[0]), float(mov_origin[1]), float(mov_origin[2])))

        if resample_to_ref:
            # Resample moving image directly onto fixed grid
            resampler = sitk.ResampleImageFilter()
            resampler.SetReferenceImage(ref_image)
            resampler.SetInterpolator(sitk.sitkLinear)
            resampler.SetTransform(final_transform)
            resampler.SetDefaultPixelValue(float(self.reg_fill_value.value()))
            
            resampled_img = resampler.Execute(mov_image)
            resampled_matrix = sitk.GetArrayFromImage(resampled_img)
            
            self.display_data[idx] = resampled_matrix.astype(original_dtype)
            self.pixel_spac[idx] = ref_spacing
            self.slice_thick[idx] = ref_thick
            self.Im_PatPosition[idx] = ref_origin
        else:
            if transform_type == "Translation Only (3 DoF)":
                translation = final_transform.GetParameters()
                new_origin = np.array(mov_origin) - np.array(translation)
                self.Im_PatPosition[idx] = new_origin
            else:
                # Resample moving image onto reference grid size
                resampler = sitk.ResampleImageFilter()
                resampler.SetReferenceImage(ref_image)
                resampler.SetInterpolator(sitk.sitkLinear)
                resampler.SetTransform(final_transform)
                resampler.SetDefaultPixelValue(float(self.reg_fill_value.value()))
                
                resampled_img = resampler.Execute(mov_image)
                resampled_matrix = sitk.GetArrayFromImage(resampled_img)
                
                self.display_data[idx] = resampled_matrix.astype(original_dtype)
                self.pixel_spac[idx] = ref_spacing
                self.slice_thick[idx] = ref_thick
                self.Im_PatPosition[idx] = ref_origin
                
        # Recalculate offsets for display
        from fcn_reg.rigid_reg_manual import update_view
        self.Im_Offset[idx, 0] = (self.Im_PatPosition[idx, 0] - self.Im_PatPosition[0, 0])
        self.Im_Offset[idx, 1] = (self.display_data[0].shape[1] * self.pixel_spac[0, 0] - self.display_data[idx].shape[1] * self.pixel_spac[idx, 0]) - (self.Im_PatPosition[idx, 1] - self.Im_PatPosition[0, 1])
        self.Im_Offset[idx, 2] = (self.Im_PatPosition[idx, 2] - self.Im_PatPosition[0, 2])
        
        # Sync spinboxes
        was_x = self.Reg_manual_Tx.blockSignals(True)
        self.Reg_manual_Tx.setValue(float(self.Im_PatPosition[idx, 0]))
        self.Reg_manual_Tx.blockSignals(was_x)
        
        was_y = self.Reg_manual_Ty.blockSignals(True)
        self.Reg_manual_Ty.setValue(float(self.Im_PatPosition[idx, 2]))  # Swap Y to Z
        self.Reg_manual_Ty.blockSignals(was_y)
        
        was_z = self.Reg_manual_Tz.blockSignals(True)
        self.Reg_manual_Tz.setValue(-float(self.Im_PatPosition[idx, 1])) # Swap Z to Y, and flip Y
        self.Reg_manual_Tz.blockSignals(was_z)
        
        update_view(self)
        
        if QMessageBox:
            QMessageBox.information(self, "Transform Applied", f"Successfully applied the last auto-registration transform to Layer {idx}!")
    except Exception as e:
        if QMessageBox:
            QMessageBox.critical(self, "Application Error", f"Failed to apply transform:\n{str(e)}")
