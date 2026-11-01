"""
"Set positions..." of the Edit panel in View > PLAN > Brachy: new dwell positions along
the selected catheter, every IDD (inter-dwell distance) mm from an offset from its tip
(its first point) over a length, all with 0 s dwell time.
"""
import numpy as np
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QLabel, QMessageBox, QVBoxLayout

from fcn_display.brachy_channel_edit import (DWELL_PATH_TOL_MM, _channel_points, _end_drag, _plan_channels,
                                             _plan_selected_channel, arc_lengths, attach_dwells, catheter_name,
                                             commit_channel_edit, locate_arclength, push_undo, valid_dwells)


# IDD offered for a catheter without dwell positions or applicator step size (mm)
DEFAULT_IDD_MM = 5.0
TIMES_NOTE = "All dwell times of this catheter will be set to 0 s."
WARNING_COLOR = "#e6a23c"


def dwell_count(idd, length):
    """Number of dwell positions every idd mm over 'length' mm (from the first to the last one)."""
    if idd <= 0 or length < 0:
        return 0
    return int(np.floor(length / idd + 1e-6)) + 1


def tip_distances(dwell_info, poly, tol=DWELL_PATH_TOL_MM):
    """Distance (mm) along the catheter from its first point (tip) of each dwell; NaN if farther than tol from it."""
    poly = np.asarray(poly, dtype=float).reshape(-1, 3)
    seg, t, attached = attach_dwells(dwell_info, poly, tol)
    seg_len, cum = arc_lengths(poly)
    return np.where(attached, cum[seg] + t * seg_len[seg], np.nan)


def current_layout(dwell_info, poly):
    """
    (offset from the tip, IDD, length) of the dwell positions of a catheter on its path
    'poly' (IDD None for a single dwell), or None without dwells on the path.
    """
    poly = np.asarray(poly, dtype=float).reshape(-1, 3)
    if not valid_dwells(dwell_info) or len(poly) < 2:
        return None
    s = np.sort(tip_distances(dwell_info, poly))
    s = s[np.isfinite(s)]
    if not s.size:
        return None
    steps = np.diff(s)
    steps = steps[steps > 1e-3]
    return float(s[0]), (float(np.median(steps)) if steps.size else None), float(s[-1] - s[0])


def orientation_sign(dwell_info, poly, tol=DWELL_PATH_TOL_MM):
    """
    -1 if most source directions of the dwells (cols 6-8) point towards the tip of the
    catheter path 'poly', else +1 (away from the tip, also without dwells).
    """
    poly = np.asarray(poly, dtype=float).reshape(-1, 3)
    if not valid_dwells(dwell_info) or dwell_info.shape[1] < 9 or len(poly) < 2:
        return 1.0
    seg, _, attached = attach_dwells(dwell_info, poly, tol)
    along = np.einsum('ij,ij->i', np.asarray(dwell_info, dtype=float)[:, 6:9], poly[seg + 1] - poly[seg])
    along = along[attached & np.isfinite(along)]
    return -1.0 if np.sum(np.sign(along)) < 0 else 1.0


def dwells_on_path(poly, offset, idd, length, sign=1.0):
    """
    DwellInfo (M, 9) for dwell positions every idd mm along the catheter path 'poly', from
    'offset' to offset + length mm from its first point (the tip), cut at the path end:
    IDX 1..M, Rel. Pos = distance from the tip, time 0 s, X, Y, Z, and the source
    direction along the path ('sign' +1: away from the tip).
    """
    poly = np.asarray(poly, dtype=float).reshape(-1, 3)
    total = arc_lengths(poly)[1][-1]
    n = dwell_count(idd, min(length, total - offset))
    s = np.minimum(offset + idd * np.arange(n), total)
    k, t = locate_arclength(poly, s)
    seg = poly[k + 1] - poly[k]
    norm = np.linalg.norm(seg, axis=1, keepdims=True)
    out = np.zeros((n, 9), dtype=np.float32)
    out[:, 0] = np.arange(1, n + 1)
    out[:, 1] = s
    out[:, 3:6] = poly[k] + t[:, None] * seg
    out[:, 6:9] = sign * np.divide(seg, norm, out=np.full_like(seg, np.nan), where=norm > 0)
    return out


def _step_size(ch):
    """Nominal step size (mm) of the catheter's applicator, or None."""
    try:
        step = float(ch.get('SourceApplicatorStepSize'))
    except (TypeError, ValueError):
        return None
    return step if np.isfinite(step) and step > 0 else None


class DwellPositionsDialog(QDialog):
    """Offset from the tip, IDD and length of new dwell positions, and the positions they give."""

    def __init__(self, parent, name, catheter_length, offset, idd, length):
        super().__init__(parent)
        self.setWindowTitle(f"Set dwell positions - {name}")
        self.setMinimumWidth(380)
        self.catheter_length = catheter_length
        self.offset = self._spin(offset, 0.0, catheter_length, 0.5,
                                 "Distance of the first dwell position from the tip (the first catheter point), along the catheter")
        self.idd = self._spin(idd, 0.1, 100.0, 0.5, "Inter-dwell distance: distance between neighbouring dwell positions, along the catheter")
        self.length = self._spin(length, 0.0, 10000.0, 1.0, "Distance from the first to the last dwell position, along the catheter")
        form = QFormLayout()
        form.addRow("Offset from the tip", self.offset)
        form.addRow("IDD", self.idd)
        form.addRow("Length", self.length)
        self.summary = QLabel(self)
        self.summary.setWordWrap(True)
        note = QLabel(TIMES_NOTE, self)
        note.setStyleSheet(f"color: {WARNING_COLOR}; font-weight: bold;")
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Set")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.summary)
        layout.addWidget(note)
        layout.addWidget(buttons)
        for spin in (self.offset, self.idd, self.length):
            spin.valueChanged.connect(self._update_summary)
        self._update_summary()

    def _spin(self, value, low, high, step, tip):
        spin = QDoubleSpinBox(self)
        spin.setDecimals(1)
        spin.setRange(low, max(high, low))
        spin.setSingleStep(step)
        spin.setSuffix(" mm")
        spin.setValue(value)
        spin.setToolTip(tip)
        return spin

    def values(self):
        """(offset, IDD, length) in mm, as entered."""
        return self.offset.value(), self.idd.value(), self.length.value()

    def _update_summary(self):
        offset, idd, length = self.values()
        room = self.catheter_length - offset
        lines = [f"Catheter length: {self.catheter_length:.1f} mm."]
        if length > room + 1e-6:
            lines.append(f"<span style='color:{WARNING_COLOR}'>The length goes past the end of the catheter: "
                         f"it will be reduced to {room:.1f} mm.</span>")
            length = room
        n = dwell_count(idd, length)
        lines.append(f"{n} dwell position{'s' if n != 1 else ''}, from {offset:.1f} to {offset + (n - 1) * idd:.1f} mm from the tip.")
        self.summary.setText("<br>".join(lines))


def brachy_set_dwell_positions(self):
    """Edit panel "Set positions...": new dwell positions along the selected catheter (0 s dwell times)."""
    _end_drag(self)
    ch = _plan_selected_channel(self)
    if ch is None:
        return
    pts = _channel_points(ch)
    poly = pts[:, :3].astype(float) if pts is not None else np.zeros((0, 3))
    total = float(arc_lengths(poly)[1][-1]) if len(poly) >= 2 else 0.0
    if total <= 0:
        QMessageBox.warning(self, "Set dwell positions", "The catheter needs at least two points to place dwell positions.")
        return
    channels = _plan_channels(self)
    k = next(i for i, c in enumerate(channels) if c is ch)
    offset, idd, length = current_layout(ch.get('DwellInfo'), poly) or (0.0, None, total)
    dialog = DwellPositionsDialog(self, catheter_name(ch, k), total, min(offset, total),
                                  idd or _step_size(ch) or DEFAULT_IDD_MM, length)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return
    offset, idd, length = dialog.values()
    if offset + length > total + 1e-6:
        reduced = total - offset
        QMessageBox.warning(self, "Set dwell positions",
                            f"The length ({length:.1f} mm) from the offset ({offset:.1f} mm) exceeds the catheter length "
                            f"({total:.1f} mm).\nThe length is reduced to {reduced:.1f} mm.")
        length = reduced
    sign = orientation_sign(ch.get('DwellInfo'), poly)
    push_undo(self, channels)
    ch['DwellInfo'] = dwells_on_path(poly, offset, idd, length, sign)
    ch['NumberofControlPoints'] = 2 * len(ch['DwellInfo'])  # a start and an end control point per dwell
    if self.brachy_combobox_01.currentText() != "Dwells":
        self.brachy_combobox_01.setCurrentText("Dwells")  # lists the new dwells; refreshes the table and views
    else:
        commit_channel_edit(self)
