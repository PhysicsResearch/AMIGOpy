from PySide6.QtWidgets import QTreeWidgetItem, QPushButton, QColorDialog
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from fcn_RTFiles.plot_ebrt_photons import update_ebrt_plot

def extract_ebrt_plan_data(dicom_ds):
    """
    Extract relevant parameters from an RTPlan DICOM dataset.
    Returns a dictionary of plan data, beams, and control points.
    """
    plan_data = {
        'PlanName': getattr(dicom_ds, 'RTPlanName', 'Unknown Plan'),
        'PlanLabel': getattr(dicom_ds, 'RTPlanLabel', 'Unknown Label'),
        'PlanDate': getattr(dicom_ds, 'RTPlanDate', 'Unknown Date'),
        'PlanTime': getattr(dicom_ds, 'RTPlanTime', 'Unknown Time'),
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
        for beam in dicom_ds.BeamSequence:
            b_num = getattr(beam, 'BeamNumber', None)
            final_mu = getattr(beam, 'FinalCumulativeMetersetWeight', None)
            
            beam_data = {
                'BeamNumber': b_num if b_num is not None else 'N/A',
                'BeamName': getattr(beam, 'BeamName', 'N/A'),
                'BeamType': getattr(beam, 'BeamType', 'N/A'),
                'RadiationType': getattr(beam, 'RadiationType', 'N/A'),
                'TreatmentMachineName': getattr(beam, 'TreatmentMachineName', 'N/A'),
                'PrimaryDosimeterUnit': getattr(beam, 'PrimaryDosimeterUnit', 'N/A'),
                'NumberofControlPoints': getattr(beam, 'NumberOfControlPoints', 'N/A'),
                'BeamDose': beam_doses.get(b_num, 'N/A'),
                'BeamMeterset': beam_metersets.get(b_num, 'N/A'),
                'FinalCumulativeMetersetWeight': final_mu,
                'ControlPoints': []
            }
            
            if hasattr(beam, 'ControlPointSequence'):
                prev_weight = 0.0
                current_dose_rate = None
                for cp in beam.ControlPointSequence:
                    current_weight = getattr(cp, 'CumulativeMetersetWeight', None)
                    if hasattr(cp, 'DoseRateSet'):
                        current_dose_rate = getattr(cp, 'DoseRateSet', current_dose_rate)
                        
                    mu_per_cp = 'N/A'
                    time_per_cp = 'N/A'
                    if current_weight is not None and final_mu and float(final_mu) > 0 and beam_data['BeamMeterset'] != 'N/A':
                        delta_weight = float(current_weight) - prev_weight
                        delta_mu = (delta_weight / float(final_mu)) * float(beam_data['BeamMeterset'])
                        mu_per_cp = f"{delta_mu:.4f}"
                        
                        if current_dose_rate and float(current_dose_rate) > 0:
                            delta_time = (delta_mu / float(current_dose_rate)) * 60.0
                            time_per_cp = f"{delta_time:.2f}"
                            
                        prev_weight = float(current_weight)
                    
                    cp_data = {
                        'ControlPointIndex': getattr(cp, 'ControlPointIndex', 'N/A'),
                        'GantryAngle': getattr(cp, 'GantryAngle', 'N/A'),
                        'GantryRotationDirection': getattr(cp, 'GantryRotationDirection', 'N/A'),
                        'BeamLimitingDeviceAngle': getattr(cp, 'BeamLimitingDeviceAngle', 'N/A'),
                        'BeamLimitingDeviceRotationDirection': getattr(cp, 'BeamLimitingDeviceRotationDirection', 'N/A'),
                        'PatientSupportAngle': getattr(cp, 'PatientSupportAngle', 'N/A'),
                        'PatientSupportRotationDirection': getattr(cp, 'PatientSupportRotationDirection', 'N/A'),
                        'CumulativeMetersetWeight': current_weight if current_weight is not None else 'N/A',
                        'DoseRateSet': current_dose_rate if current_dose_rate is not None else 'N/A',
                        'MU_per_CP': mu_per_cp,
                        'Time_per_CP': time_per_cp,
                        'BeamLimitingDevicePositions': {}
                    }
                    
                    if hasattr(cp, 'BeamLimitingDevicePositionSequence'):
                        for bldp in cp.BeamLimitingDevicePositionSequence:
                            device_type = getattr(bldp, 'RTBeamLimitingDeviceType', 'Unknown')
                            positions = getattr(bldp, 'LeafJawPositions', [])
                            cp_data['BeamLimitingDevicePositions'][device_type] = positions
                            
                    beam_data['ControlPoints'].append(cp_data)
            
            plan_data['Beams'].append(beam_data)
            
    return plan_data

def populate_ebrt_tab(w, dicom_ds):
    """
    Parse the RTPlan dataset and populate the EBRT-Ph tree widget.
    """
    if not hasattr(w, 'ebrt_tree'):
        return
        
    w.ebrt_tree.clear()
    
    w.ebrt_tree.blockSignals(True)
    
    plan_data = extract_ebrt_plan_data(dicom_ds)
    w.current_ebrt_plan_data = plan_data
    
    # Root Item for Plan
    plan_item = QTreeWidgetItem(w.ebrt_tree)
    plan_item.setText(0, "Plan")
    plan_item.setText(1, f"{plan_data['PlanLabel']} ({plan_data['PlanName']})")
    
    QTreeWidgetItem(plan_item, ["Date", str(plan_data['PlanDate'])])
    QTreeWidgetItem(plan_item, ["Time", str(plan_data['PlanTime'])])
    
    default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                      '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
                      
    for beam_idx, beam in enumerate(plan_data['Beams']):
        beam_item = QTreeWidgetItem(plan_item)
        beam_item.setText(0, f"Beam {beam['BeamNumber']}: {beam['BeamName']}")
        beam_item.setText(1, str(beam['RadiationType']))
        beam_item.setCheckState(2, Qt.Checked)
        
        # Color picker button
        color = default_colors[beam_idx % len(default_colors)]
        color_btn = QPushButton("")
        color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid gray;")
        color_btn.setProperty("beam_color", color)
        
        # We need a closure to capture the specific button
        def make_color_chooser(btn):
            def chooser():
                current_hex = btn.property("beam_color")
                dialog = QColorDialog(QColor(current_hex), w)
                if dialog.exec():
                    new_color = dialog.selectedColor().name()
                    btn.setStyleSheet(f"background-color: {new_color}; border: 1px solid gray;")
                    btn.setProperty("beam_color", new_color)
                    update_ebrt_plot(w)
            return chooser
            
        color_btn.clicked.connect(make_color_chooser(color_btn))
        w.ebrt_tree.setItemWidget(beam_item, 3, color_btn)
        
        QTreeWidgetItem(beam_item, ["Machine", str(beam['TreatmentMachineName'])])
        QTreeWidgetItem(beam_item, ["Type", str(beam['BeamType'])])
        QTreeWidgetItem(beam_item, ["Unit", str(beam['PrimaryDosimeterUnit'])])
        QTreeWidgetItem(beam_item, ["Beam Dose", str(beam.get('BeamDose', 'N/A'))])
        QTreeWidgetItem(beam_item, ["Beam Meterset", str(beam.get('BeamMeterset', 'N/A'))])
        QTreeWidgetItem(beam_item, ["Final Cumul. Meterset Weight", str(beam.get('FinalCumulativeMetersetWeight', 'N/A'))])
        
        cp_seq_item = QTreeWidgetItem(beam_item)
        cp_seq_item.setText(0, "Control Points")
        cp_seq_item.setText(1, str(beam['NumberofControlPoints']))
        
        for cp in beam['ControlPoints']:
            cp_item = QTreeWidgetItem(cp_seq_item)
            cp_item.setText(0, f"CP {cp['ControlPointIndex']}")
            cp_item.setText(1, f"Weight: {cp['CumulativeMetersetWeight']}")
            
            if cp.get('MU_per_CP') != 'N/A':
                QTreeWidgetItem(cp_item, ["MU", str(cp.get('MU_per_CP'))])
            if cp.get('Time_per_CP') != 'N/A':
                QTreeWidgetItem(cp_item, ["Time", str(cp.get('Time_per_CP'))])
                
            if cp['GantryAngle'] != 'N/A':
                QTreeWidgetItem(cp_item, ["Gantry Angle", f"{cp['GantryAngle']} ({cp['GantryRotationDirection']})"])
            if cp['BeamLimitingDeviceAngle'] != 'N/A':
                QTreeWidgetItem(cp_item, ["Collimator Angle", f"{cp['BeamLimitingDeviceAngle']} ({cp['BeamLimitingDeviceRotationDirection']})"])
            if cp['PatientSupportAngle'] != 'N/A':
                QTreeWidgetItem(cp_item, ["Couch Angle", f"{cp['PatientSupportAngle']} ({cp['PatientSupportRotationDirection']})"])
            if cp['DoseRateSet'] != 'N/A':
                QTreeWidgetItem(cp_item, ["Dose Rate", str(cp['DoseRateSet'])])
            
            if cp['BeamLimitingDevicePositions']:
                bldp_item = QTreeWidgetItem(cp_item)
                bldp_item.setText(0, "Beam Limiting Devices")
                for device_type, positions in cp['BeamLimitingDevicePositions'].items():
                    pos_str = ", ".join(map(str, positions))
                    QTreeWidgetItem(bldp_item, [device_type, pos_str])
                    
    # Expand top levels
    plan_item.setExpanded(True)
    for i in range(plan_item.childCount()):
        child = plan_item.child(i)
        if "Beam" in child.text(0):
            child.setExpanded(True)
            
    # Always reconnect signals to support hot-reloading during development
    if hasattr(w, 'ebrt_x_combo'):
        try: w.ebrt_x_combo.currentIndexChanged.disconnect()
        except Exception: pass
        w.ebrt_x_combo.currentIndexChanged.connect(lambda: update_axis_options_ui(w))
        
        try: w.ebrt_y_combo.currentIndexChanged.disconnect()
        except Exception: pass
        w.ebrt_y_combo.currentIndexChanged.connect(lambda: update_ebrt_plot(w))
        
        if hasattr(w, 'ebrt_polar_check'):
            try: w.ebrt_polar_check.stateChanged.disconnect()
            except Exception: pass
            w.ebrt_polar_check.stateChanged.connect(lambda: update_axis_options_ui(w))
            
    try: w.ebrt_tree.itemChanged.disconnect()
    except Exception: pass
    w.ebrt_tree.itemChanged.connect(lambda item, col: update_ebrt_plot(w))
    
    w.ebrt_tree.blockSignals(False)
    update_axis_options_ui(w)

def update_axis_options_ui(w):
    if not hasattr(w, 'ebrt_polar_check'):
        return
        
    is_polar = w.ebrt_polar_check.isChecked()
    x_mode = w.ebrt_x_combo.currentText()
    
    w.ebrt_x_combo.setVisible(not is_polar)
    w.ebrt_x_label.setVisible(not is_polar)
    w.ebrt_y_label.setVisible(not is_polar)
    
    # Update Y axis options based on polar mode and X mode
    current_y = w.ebrt_y_combo.currentText()
    w.ebrt_y_combo.blockSignals(True)
    w.ebrt_y_combo.clear()
    
    if is_polar:
        # In polar mode, Gantry Angle is already theta, so remove it from Y
        w.ebrt_y_combo.addItems(["Collimator Angle", "Couch Angle", "MU per CP", "Cumulative MU", "Time per CP", "Time Cumulative", "Dose Rate"])
    elif x_mode == "Beam":
        # Specific beam properties when X is categorical beams
        w.ebrt_y_combo.addItems(["Beam Dose", "Beam Meterset", "Number of Control Points", "Total Time"])
    else:
        # Standard continuous parameters
        w.ebrt_y_combo.addItems(["Gantry Angle", "Collimator Angle", "Couch Angle", "MU per CP", "Cumulative MU", "Time per CP", "Time Cumulative", "Dose Rate"])
        
    idx = w.ebrt_y_combo.findText(current_y)
    if idx >= 0:
        w.ebrt_y_combo.setCurrentIndex(idx)
    else:
        w.ebrt_y_combo.setCurrentIndex(0)
        
    w.ebrt_y_combo.blockSignals(False)
    
    # Finally, update the plot
    from fcn_RTFiles.plot_ebrt_photons import update_ebrt_plot
    update_ebrt_plot(w)
