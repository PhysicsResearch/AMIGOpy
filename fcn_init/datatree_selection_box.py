from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt

class SeriesPickerDialog(QDialog):
    def __init__(self, dicom_data, excluded_modalities=None, source_tuple=None, parent=None):
        """
        dicom_data: your nested dict
        excluded_modalities: set like {'RTPLAN','RTSTRUCT','RTDOSE'}
        source_tuple: optional (src_patient, src_study, src_modality, src_series_index)
                      only for display purposes
        """
        super().__init__(parent)
        self.setWindowTitle("Select destination series")
        self.setModal(True)

        self.dicom_data = dicom_data
        self.excluded_modalities = excluded_modalities or set()
        self.patientCombo = QComboBox()
        self.seriesCombo  = QComboBox()

        layout = QVBoxLayout(self)

        if source_tuple is not None:
            if len(source_tuple) == 4:
                sp, ss, sm, si = source_tuple
                text = f"Reference: {sp} / {ss} / {sm} / {si}"
            elif len(source_tuple) == 2:
                sp, ss = source_tuple
                text = f"Reference: {sp} / {ss}"
            else:
                # optional fallback
                text = "Select"
            layout.addWidget(QLabel(text))

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Patient:"))
        r1.addWidget(self.patientCombo)
        layout.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Series:"))
        r2.addWidget(self.seriesCombo)
        layout.addLayout(r2)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        layout.addWidget(btns)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        # patients
        self._patient_ids = sorted(self.dicom_data.keys())
        self.patientCombo.addItems(self._patient_ids)

        # map series_label -> (series_label, study_id, modality, item_index)
        self._series_map = {}

        self.patientCombo.currentIndexChanged.connect(self._refresh_series_for_patient)

        # initial fill; ensure we land on first patient with at least one valid series
        self._select_first_patient_with_valid_series()

        self.selected_patient = None
        self.selected_series_tuple = None

    def _select_first_patient_with_valid_series(self):
        for i, pid in enumerate(self._patient_ids):
            if self._has_valid_series(pid):
                self.patientCombo.setCurrentIndex(i)
                self._refresh_series_for_patient(i)
                return
        # fallback (no valid series anywhere)
        if self._patient_ids:
            self.patientCombo.setCurrentIndex(0)
            self._refresh_series_for_patient(0)

    def _has_valid_series(self, pid):
        for study_id, study_data in self.dicom_data[pid].items():
            for modality, modality_data in study_data.items():
                if modality in self.excluded_modalities:
                    continue
                if any(True for _ in modality_data):
                    return True
        return False

    def _refresh_series_for_patient(self, _idx):
        pid = self.patientCombo.currentText()
        self.seriesCombo.blockSignals(True)
        self.seriesCombo.clear()
        self._series_map.clear()

        for study_id, study_data in self.dicom_data[pid].items():
            for modality, modality_data in study_data.items():
                if modality in self.excluded_modalities:
                    continue
                for item_index, series_data in enumerate(modality_data):
                    series_label = self._build_series_label(modality, series_data)
                    self._series_map[series_label] = (series_label, study_id, modality, item_index)
                    self.seriesCombo.addItem(series_label)

        self.seriesCombo.blockSignals(False)

    def _build_series_label(self, modality, series_data):
        md = series_data.get('metadata', {})
        if modality not in {'RTPLAN','RTSTRUCT','RTDOSE'}:
            acq = md.get('AcquisitionNumber', 'NA')
            base = f"Acq_{acq}_Series: {series_data.get('SeriesNumber','?')}"
            if md.get('LUTLabel', 'N/A') != 'N/A':
                base += f" {md.get('LUTLabel','')} {md.get('LUTExplanation','')}"
            return base.strip()
        # (won't be used because we exclude them)
        return f"{modality}_Series: {series_data.get('SeriesNumber','?')}"

    def accept(self):
        self.selected_patient = self.patientCombo.currentText()
        lbl = self.seriesCombo.currentText()
        self.selected_series_tuple = self._series_map.get(lbl, None)
        super().accept()