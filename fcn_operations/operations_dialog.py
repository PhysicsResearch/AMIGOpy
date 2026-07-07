import numpy as np
import SimpleITK as sitk
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QListWidget, QTextEdit, QDoubleSpinBox, 
                               QLineEdit, QPushButton, QMessageBox, QFrame, QSplitter)
from PySide6.QtCore import Qt
from fcn_load.populate_med_image_list import populate_medical_image_tree

class OperationsDialog(QDialog):
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.setWindowTitle("Dose & Matrix Operations")
        self.resize(1100, 700)
        
        # Style sheet for premium appearance
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e24;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QLabel {
                color: #e0e0e0;
                font-weight: bold;
            }
            QComboBox, QLineEdit, QDoubleSpinBox {
                background-color: #2b2b36;
                color: #ffffff;
                border: 1px solid #444454;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QListWidget {
                background-color: #18181f;
                color: #ffffff;
                border: 1px solid #3a3a4a;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: #0d6efd;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #15151a;
                color: #00ff66;
                font-family: 'Consolas', monospace;
                border: 1px solid #333340;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #3b3b4a;
                color: #ffffff;
                border: 1px solid #55556a;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4c4c60;
            }
            QPushButton#btn_calc {
                background-color: #198754;
                border: 1px solid #146c43;
            }
            QPushButton#btn_calc:hover {
                background-color: #157347;
            }
        """)

        self.all_items = []
        self.setup_ui()
        self.load_data_tree_items()
        self.on_filter_changed()
        self.on_op_changed()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Header Title
        title_label = QLabel("Dose & Matrix Operations Tool")
        title_label.setStyleSheet("font-size: 18px; color: #0d6efd; padding-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Splitter to balance the layout
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # ----------------- Left Panel: Data Source Selection -----------------
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 5, 0)
        
        # Filter dropdown
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter Type:"))
        self.combo_filter = QComboBox()
        self.combo_filter.addItems(["All Types", "CT", "RTDOSE", "MR", "Operation", "Mask"])
        self.combo_filter.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.combo_filter)
        left_layout.addLayout(filter_layout)

        # Matrix A List Box
        left_layout.addWidget(QLabel("Select Matrix A (Operand 1):"))
        self.list_a = QListWidget()
        self.list_a.itemSelectionChanged.connect(self.on_selection_a_changed)
        left_layout.addWidget(self.list_a)

        # Matrix B List Box
        self.lbl_matrix_b = QLabel("Select Matrix B (Operand 2):")
        left_layout.addWidget(self.lbl_matrix_b)
        self.list_b = QListWidget()
        self.list_b.itemSelectionChanged.connect(self.on_selection_b_changed)
        left_layout.addWidget(self.list_b)
        
        splitter.addWidget(left_frame)

        # ----------------- Middle Panel: Matrix Details -----------------
        middle_frame = QFrame()
        middle_layout = QVBoxLayout(middle_frame)
        middle_layout.setContentsMargins(5, 0, 5, 0)

        middle_layout.addWidget(QLabel("Matrix A Description Details:"))
        self.txt_details_a = QTextEdit()
        self.txt_details_a.setReadOnly(True)
        middle_layout.addWidget(self.txt_details_a)

        self.lbl_details_b = QLabel("Matrix B Description Details:")
        middle_layout.addWidget(self.lbl_details_b)
        self.txt_details_b = QTextEdit()
        self.txt_details_b.setReadOnly(True)
        middle_layout.addWidget(self.txt_details_b)

        splitter.addWidget(middle_frame)

        # ----------------- Right Panel: Operations & Action -----------------
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(5, 0, 0, 0)
        right_layout.setSpacing(12)

        # Operation Selector
        op_layout = QHBoxLayout()
        op_layout.addWidget(QLabel("Operation:"))
        self.combo_op = QComboBox()
        self.combo_op.addItems([
            "+ Constant",
            "- Constant",
            "* Constant",
            "/ Constant",
            "^ Constant (Power)",
            "+ Matrix B",
            "- Matrix B",
            "* Matrix B",
            "/ Matrix B"
        ])
        self.combo_op.currentTextChanged.connect(self.on_op_changed)
        op_layout.addWidget(self.combo_op)
        right_layout.addLayout(op_layout)

        # Constant value spin box
        self.lbl_const = QLabel("Constant Value:")
        right_layout.addWidget(self.lbl_const)
        self.spin_const = QDoubleSpinBox()
        self.spin_const.setRange(-1000000.0, 1000000.0)
        self.spin_const.setValue(1.0)
        self.spin_const.setDecimals(4)
        right_layout.addWidget(self.spin_const)

        # Reference grid select
        self.lbl_ref_grid = QLabel("Interpolate/Resample Reference:")
        right_layout.addWidget(self.lbl_ref_grid)
        self.combo_ref_grid = QComboBox()
        self.combo_ref_grid.addItems(["Use Matrix A coordinates", "Use Matrix B coordinates"])
        right_layout.addWidget(self.combo_ref_grid)

        # Output Name
        right_layout.addWidget(QLabel("Output Series Name:"))
        self.line_name = QLineEdit()
        self.line_name.setText("Operations_Result")
        right_layout.addWidget(self.line_name)

        right_layout.addStretch()

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_calculate = QPushButton("Calculate")
        self.btn_calculate.setObjectName("btn_calc")
        self.btn_calculate.clicked.connect(self.calculate_operation)
        btn_layout.addWidget(self.btn_calculate)

        self.btn_cancel = QPushButton("Close")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        right_layout.addLayout(btn_layout)

        splitter.addWidget(right_frame)

        # Set default proportions
        splitter.setSizes([350, 400, 350])

    def load_data_tree_items(self):
        self.all_items.clear()
        medical_image = self.parent_app.medical_image
        if not medical_image:
            return

        for patient_id, patient_data in medical_image.items():
            for study_id, study_data in patient_data.items():
                for modality, modality_data in study_data.items():
                    for idx, series in enumerate(modality_data):
                        # Try to read the main matrix
                        if '3DMatrix' in series and series['3DMatrix'] is not None:
                            meta = series.get('metadata', {})
                            desc = meta.get('SeriesDescription') or f"Series {series.get('SeriesNumber')}"
                            label = f"[{modality}] {patient_id} - {study_id} - {desc}"
                            
                            self.all_items.append({
                                'label': label,
                                'type': modality,
                                'matrix': series['3DMatrix'],
                                'patient_id': patient_id,
                                'study_id': study_id,
                                'spacing': meta.get('PixelSpacing', [1.0, 1.0]),
                                'thick': float(meta.get('SliceThickness', 1.0)),
                                'origin': meta.get('ImagePositionPatient', [0.0, 0.0, 0.0]),
                                'dims': series['3DMatrix'].shape,
                                'desc': desc
                            })

                        # Try to read segmentations / structures
                        structures = series.get('structures', {})
                        for s_key, s_data in structures.items():
                            if 'Mask3D' in s_data and s_data['Mask3D'] is not None:
                                name = s_data.get('Name', s_key)
                                label = f"[Mask] {patient_id} - {study_id} - {name}"
                                meta = series.get('metadata', {})
                                
                                self.all_items.append({
                                    'label': label,
                                    'type': 'Mask',
                                    'matrix': s_data['Mask3D'],
                                    'patient_id': patient_id,
                                    'study_id': study_id,
                                    'spacing': meta.get('PixelSpacing', [1.0, 1.0]),
                                    'thick': float(meta.get('SliceThickness', 1.0)),
                                    'origin': meta.get('ImagePositionPatient', [0.0, 0.0, 0.0]),
                                    'dims': s_data['Mask3D'].shape,
                                    'desc': name
                                })

    def on_filter_changed(self):
        filter_text = self.combo_filter.currentText()
        
        # Save selection states
        sel_a = self.list_a.currentItem().text() if self.list_a.currentItem() else None
        sel_b = self.list_b.currentItem().text() if self.list_b.currentItem() else None
        
        self.list_a.clear()
        self.list_b.clear()
        
        for item in self.all_items:
            if filter_text == "All Types" or item['type'] == filter_text:
                self.list_a.addItem(item['label'])
                self.list_b.addItem(item['label'])

        # Restore selection if possible
        if sel_a:
            matching_items = self.list_a.findItems(sel_a, Qt.MatchExactly)
            if matching_items:
                self.list_a.setCurrentItem(matching_items[0])
        if sel_b:
            matching_items = self.list_b.findItems(sel_b, Qt.MatchExactly)
            if matching_items:
                self.list_b.setCurrentItem(matching_items[0])

    def on_selection_a_changed(self):
        item = self.get_selected_item(self.list_a)
        if item:
            details = (
                f"Patient ID: {item['patient_id']}\n"
                f"Study ID:   {item['study_id']}\n"
                f"Type:       {item['type']}\n"
                f"Name:       {item['desc']}\n"
                f"---------------------------------\n"
                f"Matrix Size (Z, Y, X): {item['dims']}\n"
                f"Spacing (Y, X):       {item['spacing']}\n"
                f"Thickness (Z):        {item['thick']} mm\n"
                f"Origin (X, Y, Z):     {item['origin']}\n"
            )
            self.txt_details_a.setPlainText(details)
        else:
            self.txt_details_a.clear()

    def on_selection_b_changed(self):
        item = self.get_selected_item(self.list_b)
        if item:
            details = (
                f"Patient ID: {item['patient_id']}\n"
                f"Study ID:   {item['study_id']}\n"
                f"Type:       {item['type']}\n"
                f"Name:       {item['desc']}\n"
                f"---------------------------------\n"
                f"Matrix Size (Z, Y, X): {item['dims']}\n"
                f"Spacing (Y, X):       {item['spacing']}\n"
                f"Thickness (Z):        {item['thick']} mm\n"
                f"Origin (X, Y, Z):     {item['origin']}\n"
            )
            self.txt_details_b.setPlainText(details)
        else:
            self.txt_details_b.clear()

    def on_op_changed(self):
        op = self.combo_op.currentText()
        is_binary = "Matrix B" in op
        
        # Toggle elements visibility/usability based on operation type
        self.list_b.setEnabled(is_binary)
        self.lbl_matrix_b.setEnabled(is_binary)
        self.txt_details_b.setEnabled(is_binary)
        self.lbl_details_b.setEnabled(is_binary)
        self.lbl_ref_grid.setEnabled(is_binary)
        self.combo_ref_grid.setEnabled(is_binary)
        
        self.lbl_const.setEnabled(not is_binary)
        self.spin_const.setEnabled(not is_binary)

    def get_selected_item(self, list_widget):
        sel = list_widget.currentItem()
        if not sel:
            return None
        label = sel.text()
        for item in self.all_items:
            if item['label'] == label:
                return item
        return None

    def calculate_operation(self):
        item_a = self.get_selected_item(self.list_a)
        if not item_a:
            QMessageBox.warning(self, "Selection Error", "Please select Matrix A first.")
            return

        op = self.combo_op.currentText()
        name = self.line_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a valid name for the output series.")
            return

        # Prepare matrix A
        matrix_a = item_a['matrix']
        result_matrix = None
        target_meta = {
            'patient_id': item_a['patient_id'],
            'study_id': item_a['study_id'],
            'spacing': item_a['spacing'],
            'thick': item_a['thick'],
            'origin': item_a['origin']
        }

        # ---------------- Unary Operations ----------------
        if "Constant" in op:
            constant = self.spin_const.value()
            try:
                if op == "+ Constant":
                    result_matrix = matrix_a + constant
                elif op == "- Constant":
                    result_matrix = matrix_a - constant
                elif op == "* Constant":
                    result_matrix = matrix_a * constant
                elif op == "/ Constant":
                    if constant == 0:
                        raise ZeroDivisionError("Cannot divide by a constant of zero.")
                    result_matrix = matrix_a / constant
                elif op == "^ Constant (Power)":
                    result_matrix = np.power(matrix_a, constant)
            except Exception as e:
                QMessageBox.critical(self, "Math Error", f"Operation failed:\n{str(e)}")
                return

        # ---------------- Binary Operations ----------------
        else:
            item_b = self.get_selected_item(self.list_b)
            if not item_b:
                QMessageBox.warning(self, "Selection Error", "Please select Matrix B first.")
                return

            matrix_b = item_b['matrix']
            
            # Determine reference grid
            use_a_ref = self.combo_ref_grid.currentIndex() == 0
            
            ref_item = item_a if use_a_ref else item_b
            mov_item = item_b if use_a_ref else item_a
            
            # Extract spacing/thickness/origin
            ref_spacing = ref_item['spacing']
            ref_thick = ref_item['thick']
            ref_origin = ref_item['origin']
            ref_matrix = ref_item['matrix']
            
            mov_spacing = mov_item['spacing']
            mov_thick = mov_item['thick']
            mov_origin = mov_item['origin']
            mov_matrix = mov_item['matrix']

            # Target metadata is defined by the reference grid
            target_meta = {
                'patient_id': ref_item['patient_id'],
                'study_id': ref_item['study_id'],
                'spacing': ref_spacing,
                'thick': ref_thick,
                'origin': ref_origin
            }

            try:
                # Interpolate moving matrix onto reference matrix size
                ref_img = sitk.GetImageFromArray(np.ascontiguousarray(ref_matrix.astype(np.float32)))
                ref_img.SetSpacing((float(ref_spacing[1]), float(ref_spacing[0]), float(ref_thick)))
                ref_img.SetOrigin((float(ref_origin[0]), float(ref_origin[1]), float(ref_origin[2])))
                
                mov_img = sitk.GetImageFromArray(np.ascontiguousarray(mov_matrix.astype(np.float32)))
                mov_img.SetSpacing((float(mov_spacing[1]), float(mov_spacing[0]), float(mov_thick)))
                mov_img.SetOrigin((float(mov_origin[0]), float(mov_origin[1]), float(mov_origin[2])))
                
                resampler = sitk.ResampleImageFilter()
                resampler.SetReferenceImage(ref_img)
                resampler.SetInterpolator(sitk.sitkLinear)
                resampler.SetTransform(sitk.Transform())
                resampler.SetDefaultPixelValue(0.0)
                
                resampled_img = resampler.Execute(mov_img)
                mov_resampled = sitk.GetArrayFromImage(resampled_img)

                # Define aligned operands
                operand_a = ref_matrix if use_a_ref else mov_resampled
                operand_b = mov_resampled if use_a_ref else ref_matrix

                if op == "+ Matrix B":
                    result_matrix = operand_a + operand_b
                elif op == "- Matrix B":
                    result_matrix = operand_a - operand_b
                elif op == "* Matrix B":
                    result_matrix = operand_a * operand_b
                elif op == "/ Matrix B":
                    result_matrix = np.divide(operand_a, operand_b, out=np.zeros_like(operand_a), where=operand_b!=0)
            except Exception as e:
                QMessageBox.critical(self, "Calculation Error", f"Failed during resampling or matrix computation:\n{str(e)}")
                return

        # ---------------- Save back to Medical Image Database ----------------
        if result_matrix is not None:
            try:
                self.store_operation_result(result_matrix, name, target_meta)
                populate_medical_image_tree(self.parent_app)
                QMessageBox.information(self, "Success", f"Operation completed! Output added to data tree as '{name}'.")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save the result matrix:\n{str(e)}")

    def store_operation_result(self, result_matrix, name, meta):
        patient_id = meta['patient_id']
        study_id = meta['study_id']
        
        # Ensure levels exist
        p_dict = self.parent_app.medical_image.setdefault(patient_id, {})
        s_dict = p_dict.setdefault(study_id, {})
        op_list = s_dict.setdefault('Operation', [])
        
        new_series = {
            'SeriesNumber': len(op_list) + 1,
            '3DMatrix': result_matrix.astype(np.float32),
            'metadata': {
                'Modality': 'Operation',
                'SeriesDescription': name,
                'WindowWidth': float(np.max(result_matrix) - np.min(result_matrix)) or 10.0,
                'WindowCenter': float(np.mean(result_matrix)) or 5.0,
                'SliceThickness': meta['thick'],
                'PixelSpacing': [float(meta['spacing'][0]), float(meta['spacing'][1])],
                'ImagePositionPatient': [float(meta['origin'][0]), float(meta['origin'][1]), float(meta['origin'][2])],
                'SeriesNumber': len(op_list) + 1,
                'LUTLabel': 'N/A',
                'LUTExplanation': 'N/A',
                'AcquisitionNumber': 1,
                'DCM_Info': None
            }
        }
        op_list.append(new_series)

def open_operations_dialog(parent_app):
    dialog = OperationsDialog(parent_app)
    dialog.exec()
