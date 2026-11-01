"""
Dose calculation panel of View > PLAN > Brachy: the source, the air kerma strength (Sk) of
the plan and the TG43 dose of the plan.

- Source: a source of the TG43 source database (fcn_brachy_sources, a folder per source; its
  data are shown in Plan > Brachy > TG43). It is loaded, with its reference dose matrix, the
  first time a dose is calculated with it.
- Sk: air kerma strength of the plan's source, saved with the plan; changing it asks whether
  to scale the dwell times (same dose). It can be undone.
- Calculate TG43 dose: the dose of the plan shown (Gy, fcn_brachy.cal_TG43_dose) as a new
  RTDOSE of the plan's study in the data tree, labelled with the plan's name. The dose grid
  and the size of the reference dose matrix are set in Plan > Brachy > TG43.
"""
import numpy as np
from PySide6.QtWidgets import QMessageBox

from fcn_brachy.cal_TG43_dose import calculate_TG43_plan_dose, store_dose_to_medical_image
from fcn_brachy_sources.process_brachy_database import brachy_source_names
from fcn_RTFiles.amigo_rtplan import plan_sk
from fcn_display.brachy_channel_edit import push_undo, valid_dwells
from fcn_display.brachy_plan_actions import _current_plan, _next_series_number, _refresh
from fcn_load.populate_med_image_list import add_series_tree_item, rtdose_tree_label


def _timed_channels(channels):
    """The catheters with a dwell time (more than 0 s at one of their dwell positions)."""
    return [ch for ch in channels if valid_dwells(ch.get('DwellInfo')) and np.any(np.nan_to_num(ch['DwellInfo'][:, 2]) > 0)]


# ---------------------------------------------------------------------------
# Source
# ---------------------------------------------------------------------------
def update_brachy_dose_sources(self):
    """Source list: the sources of the database (the selected one stays selected while it is there)."""
    combo = getattr(self, 'brachy_dose_source', None)
    if combo is None:
        return
    try:
        names = brachy_source_names()
    except OSError:
        names = []
    current = combo.currentText()
    combo.blockSignals(True)
    combo.clear()
    combo.addItems(names)
    if current in names:
        combo.setCurrentText(current)
    combo.blockSignals(False)
    update_brachy_dose_panel(self)


# ---------------------------------------------------------------------------
# Air kerma strength
# ---------------------------------------------------------------------------
def on_brachy_sk_edited(self):
    """Sk entered: it goes into the plan; with dwell times set, asks first whether to scale them (same dose)."""
    spin = getattr(self, 'brachy_sk_spin', None)
    plan = _current_plan(self)
    if spin is None or plan is None or getattr(self, '_brachy_sk_busy', False):
        return
    meta = plan[3]['metadata']
    channels = meta['Plan_Brachy_Channels']
    old, new = plan_sk(meta), spin.value()
    if abs(new - round(old, spin.decimals())) < 0.5 * 10 ** -spin.decimals():
        return
    self._brachy_sk_busy = True  # (the question takes the focus from the box: one more editingFinished)
    try:
        timed = _timed_channels(channels)
        scale = False
        if timed:
            answer = QMessageBox.question(
                self, "Air kerma strength",
                f"Sk: {old:.10g} U → {new:.10g} U.\n\nScale the dwell times to keep the same dose?\n\n"
                f"Yes: every dwell time × {old / new:.4f} (same dose).\n"
                f"No: the dwell times are kept (dose × {new / old:.4f}).",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            if answer not in (QMessageBox.Yes, QMessageBox.No):
                spin.blockSignals(True)
                spin.setValue(old)
                spin.blockSignals(False)
                return
            scale = answer == QMessageBox.Yes
        push_undo(self, channels, sk=True)
        if scale:
            for ch in timed:
                ch['DwellInfo'][:, 2] = ch['DwellInfo'][:, 2] * (old / new)
        meta['ReferenceAirKermaRate'] = float(new)
        _refresh(self)
    finally:
        self._brachy_sk_busy = False


# ---------------------------------------------------------------------------
# TG43 dose
# ---------------------------------------------------------------------------
def brachy_calculate_dose(self):
    """
    Calculate TG43 dose: the dose of the plan shown, with the source of the panel and the
    plan's Sk, as a new RTDOSE of the plan's study in the data tree.
    """
    plan = _current_plan(self)
    if plan is None or getattr(self, '_brachy_dose_busy', False):
        return
    pid, sid, _idx, series = plan
    meta = series['metadata']
    source = self.brachy_dose_source.currentText().strip()
    if not source:
        QMessageBox.warning(self, "TG43 dose", "No source: the TG43 source database (fcn_brachy_sources) has none.")
        return
    if not _timed_channels(meta['Plan_Brachy_Channels']):
        QMessageBox.information(self, "TG43 dose", "The plan has no dwell times yet (0 s at every dwell position): "
                                                   "there is no dose to calculate.")
        return
    self._brachy_dose_busy = True  # (the calculation lets the window update: no second one meanwhile)
    update_brachy_dose_panel(self)
    try:
        result = calculate_TG43_plan_dose(self, source)
    finally:
        self._brachy_dose_busy = False
        update_brachy_dose_panel(self)
    if result is None:
        return
    dose, dose_meta = result
    study = self.medical_image[pid][sid]
    plan_uid = meta.get('SOPInstanceUID')
    k = store_dose_to_medical_image(self, dose, dose_meta, pid, sid, _next_series_number(study),
                                    plan_uid if plan_uid not in ('', 'N/A') else None)
    label = rtdose_tree_label(study, study['RTDOSE'][k])
    # (added as it is: rebuilding the tree would click the image series shown again)
    item = add_series_tree_item(self, pid, sid, 'RTDOSE', k, label)
    if item is not None:
        self.DataTreeView.scrollTo(item.index())
    status = getattr(self, 'label_2', None)
    if status is not None:
        status.setText(f"TG43 dose calculated: {label} (data tree, RTDOSE; click it to show it)")
        status.show()


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------
def update_brachy_dose_panel(self):
    """Dose calculation panel: the Sk of the plan shown; Sk and Calculate need a plan (Calculate a source too)."""
    if getattr(self, 'brachy_dose_group', None) is None:
        return
    plan = _current_plan(self)
    for name in ('brachy_sk_label', 'brachy_sk_spin'):
        widget = getattr(self, name, None)
        if widget is not None:
            widget.setEnabled(plan is not None)
    btn = getattr(self, 'brachy_calc_dose_btn', None)
    if btn is not None:
        btn.setEnabled(plan is not None and self.brachy_dose_source.count() > 0
                       and not getattr(self, '_brachy_dose_busy', False))
    if plan is None:
        return
    sk = plan_sk(plan[3]['metadata'])
    spin = getattr(self, 'brachy_sk_spin', None)
    if spin is not None:
        spin.blockSignals(True)
        spin.setValue(sk)
        spin.blockSignals(False)
    ac = getattr(self, 'brachy_plan_Ac', None)
    if ac is not None:
        ac.setText(f"{sk:.10g}")  # (the plan's Sk, in the Plan module)
