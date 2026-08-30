import os
import csv
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QTableWidgetItem, QCheckBox, QPushButton, QColorDialog,
    QFileDialog, QMessageBox, QHeaderView, QWidget, QHBoxLayout
)

DEFAULT_BEAM_COLORS = [
    '#e53935', '#1e88e5', '#43a047', '#fb8c00', '#8e24aa',
    '#00acc1', '#fdd835', '#d81b60', '#3949ab', '#00897b'
]


def extract_ebrt_beams_data(dicom_ds):
    """
    Extracts structured beam/field information from an RTPlan DICOM dataset.
    """
    plan_info = {
        'PlanName': getattr(dicom_ds, 'RTPlanName', '') or getattr(dicom_ds, 'RTPlanLabel', 'Plan'),
        'PlanLabel': getattr(dicom_ds, 'RTPlanLabel', '') or getattr(dicom_ds, 'RTPlanName', 'Plan'),
        'PlanDate': getattr(dicom_ds, 'RTPlanDate', 'N/A'),
        'Beams': []
    }

    beam_doses = {}
    beam_metersets = {}
    if hasattr(dicom_ds, 'FractionGroupSequence'):
        for fg in dicom_ds.FractionGroupSequence:
            if hasattr(fg, 'ReferencedBeamSequence'):
                for rb in fg.ReferencedBeamSequence:
                    bn = getattr(rb, 'ReferencedBeamNumber', None)
                    if bn is not None:
                        beam_doses[bn] = getattr(rb, 'BeamDose', 'N/A')
                        beam_metersets[bn] = getattr(rb, 'BeamMeterset', 'N/A')

    if hasattr(dicom_ds, 'BeamSequence'):
        for idx, beam in enumerate(dicom_ds.BeamSequence):
            b_num = getattr(beam, 'BeamNumber', idx + 1)
            b_name = getattr(beam, 'BeamName', f"Field {b_num}")
            b_type = getattr(beam, 'BeamType', 'STATIC')
            rad_type = getattr(beam, 'RadiationType', 'PHOTON')
            sad = float(getattr(beam, 'SourceAxisDistance', 1000.0) or 1000.0)

            # Control points
            cp_seq = getattr(beam, 'ControlPointSequence', [])
            n_cps = len(cp_seq)

            gantry_start = 0.0
            gantry_end = 0.0
            gantry_dir = 'NONE'
            gantry_str = "0.0°"
            coll_angle = 0.0
            couch_angle = 0.0
            iso_pos = [0.0, 0.0, 0.0]
            energy_str = "N/A"
            jaw_x = [-50.0, 50.0]
            jaw_y = [-50.0, 50.0]

            if n_cps > 0:
                cp0 = cp_seq[0]
                gantry_start = float(getattr(cp0, 'GantryAngle', 0.0) or 0.0)
                gantry_dir = getattr(cp0, 'GantryRotationDirection', 'NONE')
                coll_angle = float(getattr(cp0, 'BeamLimitingDeviceAngle', 0.0) or 0.0)
                couch_angle = float(getattr(cp0, 'PatientSupportAngle', 0.0) or 0.0)
                iso_raw = getattr(cp0, 'IsocenterPosition', [0.0, 0.0, 0.0])
                if iso_raw and len(iso_raw) == 3:
                    iso_pos = [float(iso_raw[0]), float(iso_raw[1]), float(iso_raw[2])]

                energy = getattr(cp0, 'NominalBeamEnergy', None)
                if energy is not None:
                    energy_str = f"{energy} MV" if rad_type == 'PHOTON' else f"{energy} MeV"

                # Check if arc / dynamic with gantry movement
                if n_cps > 1:
                    cp_last = cp_seq[-1]
                    gantry_end = float(getattr(cp_last, 'GantryAngle', gantry_start) or gantry_start)
                    if abs(gantry_end - gantry_start) > 0.1:
                        gantry_str = f"{gantry_start:.1f}° -> {gantry_end:.1f}° ({gantry_dir})"
                    else:
                        gantry_str = f"{gantry_start:.1f}°"
                else:
                    gantry_str = f"{gantry_start:.1f}°"

                # Jaws / Field size
                bld_seq = getattr(cp0, 'BeamLimitingDevicePositionSequence', [])
                for bld in bld_seq:
                    dev_type = getattr(bld, 'RTBeamLimitingDeviceType', '')
                    pos = getattr(bld, 'LeafJawPositions', [])
                    if 'X' in dev_type and len(pos) >= 2 and 'MLC' not in dev_type:
                        jaw_x = [float(pos[0]), float(pos[1])]
                    elif 'Y' in dev_type and len(pos) >= 2 and 'MLC' not in dev_type:
                        jaw_y = [float(pos[0]), float(pos[1])]

            field_w = abs(jaw_x[1] - jaw_x[0]) / 10.0
            field_h = abs(jaw_y[1] - jaw_y[0]) / 10.0
            field_size_str = f"{field_w:.1f} x {field_h:.1f} cm"

            mu = getattr(beam, 'FinalCumulativeMetersetWeight', beam_metersets.get(b_num, 'N/A'))
            if mu != 'N/A' and mu is not None:
                try:
                    mu_str = f"{float(mu):.1f} MU"
                except Exception:
                    mu_str = str(mu)
            else:
                mu_str = "N/A"

            color = DEFAULT_BEAM_COLORS[idx % len(DEFAULT_BEAM_COLORS)]

            beam_dict = {
                'BeamNumber': b_num,
                'BeamName': b_name,
                'BeamType': b_type,
                'RadiationType': rad_type,
                'NominalEnergy': energy_str,
                'GantryAngleStart': gantry_start,
                'GantryAngleEnd': gantry_end,
                'GantryDirection': gantry_dir,
                'GantryAngleStr': gantry_str,
                'CollimatorAngle': coll_angle,
                'CouchAngle': couch_angle,
                'Isocenter': iso_pos,
                'JawX': jaw_x,
                'JawY': jaw_y,
                'FieldSizeStr': field_size_str,
                'MU': mu_str,
                'BeamDose': beam_doses.get(b_num, 'N/A'),
                'SAD': sad,
                'Visible': True,
                'Color': color,
                'ControlPoints': cp_seq
            }
            plan_info['Beams'].append(beam_dict)

    return plan_info


def update_disp_ebrt_plan(self):
    """
    Parses the currently selected RTPLAN and populates w.ebrt_table_01.
    """
    if not hasattr(self, 'patientID_plan') or not hasattr(self, 'ebrt_table_01'):
        return

    try:
        series_data = self.medical_image[self.patientID_plan][self.studyID_plan]['RTPLAN'][self.series_index_plan]
        dicom_ds = series_data['metadata'].get('DCM_Info')
    except Exception:
        return

    if dicom_ds is None:
        return

    plan_info = extract_ebrt_beams_data(dicom_ds)
    self.ebrt_beams_data = plan_info['Beams']

    if hasattr(self, 'ebrt_plan_info_label'):
        p_name = plan_info['PlanLabel'] or plan_info['PlanName']
        p_date = plan_info['PlanDate']
        n_b = len(self.ebrt_beams_data)
        self.ebrt_plan_info_label.setText(f"<b>Plan:</b> {p_name} &nbsp;|&nbsp; <b>Date:</b> {p_date} &nbsp;|&nbsp; <b>Fields:</b> {n_b}")

    table = self.ebrt_table_01
    table.blockSignals(True)
    table.clear()

    headers = [
        "Show", "Color", "Beam #", "Name", "Type", "Energy",
        "Gantry", "Coll.", "Couch", "Field Size", "Isocenter (X, Y, Z)", "MU"
    ]
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setRowCount(len(self.ebrt_beams_data))

    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Interactive)
    table.resizeColumnsToContents()
    for c in range(table.columnCount()):
        table.setColumnWidth(c, max(table.columnWidth(c), 65))
    table.setColumnWidth(3, max(table.columnWidth(3), 140))  # Name column
    table.setColumnWidth(10, max(table.columnWidth(10), 160)) # Isocenter column

    for row, beam in enumerate(self.ebrt_beams_data):
        # 0: Show Checkbox
        chk_widget = QWidget()
        chk_layout = QHBoxLayout(chk_widget)
        chk_layout.setContentsMargins(0, 0, 0, 0)
        chk_layout.setAlignment(Qt.AlignCenter)
        chk = QCheckBox()
        chk.setChecked(beam.get('Visible', True))
        
        def _make_toggle(b_idx, checkbox):
            def _toggle(state):
                self.ebrt_beams_data[b_idx]['Visible'] = (state == Qt.Checked or state == 2 or checkbox.isChecked())
                on_ebrt_overlay_toggled(self)
            return _toggle

        chk.stateChanged.connect(_make_toggle(row, chk))
        chk_layout.addWidget(chk)
        table.setCellWidget(row, 0, chk_widget)

        # 1: Color Picker Button
        btn_color = QPushButton("")
        btn_color.setFixedSize(26, 20)
        c_hex = beam.get('Color', DEFAULT_BEAM_COLORS[row % len(DEFAULT_BEAM_COLORS)])
        btn_color.setStyleSheet(f"background-color: {c_hex}; border: 1px solid #757575; border-radius: 3px;")

        def _make_color_picker(b_idx, btn):
            def _pick():
                cur_color = QColor(self.ebrt_beams_data[b_idx]['Color'])
                new_c = QColorDialog.getColor(cur_color, self, "Select Beam Color")
                if new_c.isValid():
                    hex_str = new_c.name()
                    self.ebrt_beams_data[b_idx]['Color'] = hex_str
                    btn.setStyleSheet(f"background-color: {hex_str}; border: 1px solid #757575; border-radius: 3px;")
                    on_ebrt_overlay_toggled(self)
            return _pick

        btn_color.clicked.connect(_make_color_picker(row, btn_color))
        
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(btn_color)
        table.setCellWidget(row, 1, btn_widget)

        # 2: Beam #
        it_num = QTableWidgetItem(str(beam['BeamNumber']))
        it_num.setTextAlignment(Qt.AlignCenter)
        it_num.setFlags(it_num.flags() & ~Qt.ItemIsEditable)
        table.setItem(row, 2, it_num)

        # 3: Name
        it_name = QTableWidgetItem(str(beam['BeamName']))
        it_name.setFlags(it_name.flags() & ~Qt.ItemIsEditable)
        table.setItem(row, 3, it_name)

        # 4: Type
        it_type = QTableWidgetItem(str(beam['BeamType']))
        it_type.setTextAlignment(Qt.AlignCenter)
        it_type.setFlags(it_type.flags() & ~Qt.ItemIsEditable)
        table.setItem(row, 4, it_type)

        # 5: Energy
        it_energy = QTableWidgetItem(str(beam['NominalEnergy']))
        it_energy.setTextAlignment(Qt.AlignCenter)
        it_energy.setFlags(it_energy.flags() & ~Qt.ItemIsEditable)
        table.setItem(row, 5, it_energy)

        # 6: Gantry
        it_gantry = QTableWidgetItem(str(beam['GantryAngleStr']))
        it_gantry.setTextAlignment(Qt.AlignCenter)
        it_gantry.setFlags(it_gantry.flags() & ~Qt.ItemIsEditable)
        table.setItem(row, 6, it_gantry)

        # 7: Collimator
        it_coll = QTableWidgetItem(f"{beam['CollimatorAngle']:.1f}°")
        it_coll.setTextAlignment(Qt.AlignCenter)
        it_coll.setFlags(it_coll.flags() & ~Qt.ItemIsEditable)
        table.setItem(row, 7, it_coll)

        # 8: Couch
        it_couch = QTableWidgetItem(f"{beam['CouchAngle']:.1f}°")
        it_couch.setTextAlignment(Qt.AlignCenter)
        it_couch.setFlags(it_couch.flags() & ~Qt.ItemIsEditable)
        table.setItem(row, 8, it_couch)

        # 9: Field Size
        it_fs = QTableWidgetItem(str(beam['FieldSizeStr']))
        it_fs.setTextAlignment(Qt.AlignCenter)
        it_fs.setFlags(it_fs.flags() & ~Qt.ItemIsEditable)
        table.setItem(row, 9, it_fs)

        # 10: Isocenter
        iso = beam['Isocenter']
        it_iso = QTableWidgetItem(f"[{iso[0]:.1f}, {iso[1]:.1f}, {iso[2]:.1f}]")
        it_iso.setTextAlignment(Qt.AlignCenter)
        it_iso.setFlags(it_iso.flags() & ~Qt.ItemIsEditable)
        table.setItem(row, 10, it_iso)

        # 11: MU
        it_mu = QTableWidgetItem(str(beam['MU']))
        it_mu.setTextAlignment(Qt.AlignCenter)
        it_mu.setFlags(it_mu.flags() & ~Qt.ItemIsEditable)
        table.setItem(row, 11, it_mu)

    table.blockSignals(False)
    on_ebrt_overlay_toggled(self)


def on_ebrt_overlay_toggled(self):
    """
    Refreshes all 2D viewports to update the EBRT beam overlays.
    """
    from fcn_display.display_images import displayaxial, displaycoronal, displaysagittal
    displayaxial(self)
    displaycoronal(self)
    displaysagittal(self)


def on_ebrt_all_fields_toggled(self):
    """
    Selects or deselects all fields in the EBRT table.
    """
    if not hasattr(self, 'ebrt_table_01') or not hasattr(self, 'ebrt_overlay_all_fields'):
        return

    is_checked = self.ebrt_overlay_all_fields.isChecked()
    table = self.ebrt_table_01

    for row in range(table.rowCount()):
        cell_widget = table.cellWidget(row, 0)
        if cell_widget is not None:
            chk = cell_widget.findChild(QCheckBox)
            if chk is not None:
                chk.blockSignals(True)
                chk.setChecked(is_checked)
                chk.blockSignals(False)

        if hasattr(self, 'ebrt_beams_data') and row < len(self.ebrt_beams_data):
            self.ebrt_beams_data[row]['Visible'] = is_checked

    on_ebrt_overlay_toggled(self)


def export_ebrt_beams_to_csv(self):
    """
    Exports the current EBRT plan beams table to a CSV file.
    """
    if not hasattr(self, 'ebrt_beams_data') or not self.ebrt_beams_data:
        QMessageBox.warning(self, "Export Beams", "No EBRT plan beams loaded to export.")
        return

    file_path, _ = QFileDialog.getSaveFileName(
        self, "Export EBRT Beams to CSV", "", "CSV Files (*.csv);;All Files (*)"
    )
    if not file_path:
        return

    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "BeamNumber", "BeamName", "BeamType", "RadiationType",
                "NominalEnergy", "GantryAngleStart", "GantryAngleEnd",
                "GantryDirection", "CollimatorAngle", "CouchAngle",
                "Isocenter_X_mm", "Isocenter_Y_mm", "Isocenter_Z_mm",
                "Jaw_X1_mm", "Jaw_X2_mm", "Jaw_Y1_mm", "Jaw_Y2_mm",
                "FieldSize", "MU", "BeamDose"
            ])
            for b in self.ebrt_beams_data:
                iso = b.get('Isocenter', [0, 0, 0])
                jx = b.get('JawX', [-50, 50])
                jy = b.get('JawY', [-50, 50])
                writer.writerow([
                    b.get('BeamNumber', ''),
                    b.get('BeamName', ''),
                    b.get('BeamType', ''),
                    b.get('RadiationType', ''),
                    b.get('NominalEnergy', ''),
                    b.get('GantryAngleStart', ''),
                    b.get('GantryAngleEnd', ''),
                    b.get('GantryDirection', ''),
                    b.get('CollimatorAngle', ''),
                    b.get('CouchAngle', ''),
                    iso[0], iso[1], iso[2],
                    jx[0], jx[1], jy[0], jy[1],
                    b.get('FieldSizeStr', ''),
                    b.get('MU', ''),
                    b.get('BeamDose', '')
                ])
        QMessageBox.information(self, "Export Complete", f"Successfully exported {len(self.ebrt_beams_data)} beams to:\n{file_path}")
    except Exception as e:
        QMessageBox.critical(self, "Export Error", f"Failed to export CSV:\n{str(e)}")
