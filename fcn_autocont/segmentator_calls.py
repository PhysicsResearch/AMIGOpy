# fcn_autocont/segmentator_calls.py
# -*- coding: utf-8 -*-
"""
Segmentator UI launcher with background worker, per-series progress,
and a Stop button that is enabled for ANY non-empty selection.
"""

from __future__ import annotations

from typing import List, Dict, Any

import sip
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QTableWidgetItem, QProgressBar

from fcn_autocont.segmentator_ui import SegmentatorWindow
from .segmentator_vendored import run_totalseg_for_series


# -------------------------- table helpers --------------------------

_STATUS_COL_TITLE = "Status"


def _ensure_status_column(win: SegmentatorWindow) -> int:
    """Ensure the 'Status' column exists and attach a QProgressBar to each row."""
    tbl = win.tbl
    headers = [tbl.horizontalHeaderItem(c).text() for c in range(tbl.columnCount())]
    if _STATUS_COL_TITLE not in headers:
        col = tbl.columnCount()
        tbl.insertColumn(col)
        tbl.setHorizontalHeaderItem(col, QTableWidgetItem(_STATUS_COL_TITLE))
        tbl.horizontalHeader().setSectionResizeMode(col, tbl.horizontalHeader().ResizeToContents)
    else:
        col = headers.index(_STATUS_COL_TITLE)

    if not hasattr(win, "_row_progress"):
        win._row_progress = {}  # row -> QProgressBar

    for r in range(tbl.rowCount()):
        if r not in win._row_progress:
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(True)
            bar.setFormat("")  # empty until we set a state
            tbl.setCellWidget(r, col, bar)
            win._row_progress[r] = bar
    return col


def _match_row_for_meta(win: SegmentatorWindow, meta: dict) -> int:
    """Find table row matching the series meta; returns -1 if not found."""
    patient = meta.get("patient")
    study   = meta.get("study")
    mod     = meta.get("modality")
    idx     = int(meta.get("index", -1))
    for row_meta in getattr(win, "series_rows", []):
        if (
            row_meta.get("patient") == patient and
            row_meta.get("study")   == study   and
            row_meta.get("modality")== mod     and
            int(row_meta.get("index", -99)) == idx
        ):
            return int(row_meta.get("row"))
    return -1


def _set_row_state(win: SegmentatorWindow, row: int, state: str, msg: str = ""):
    """
    Set a standard state on a row's QProgressBar.

    States:
      'queued'   -> indeterminate, text 'Queued…'
      'running'  -> indeterminate, text 'Running…'
      'stopping' -> indeterminate, text 'Stopping…'
      'done'     -> 100%,          text 'Done'
      'failed'   ->   0%,          text 'Failed' (or msg)
      'stopped'  ->   0%,          text 'Stopped'
      'idle'     ->   0%,          text ''
    """
    bar = getattr(win, "_row_progress", {}).get(row)
    if not bar:
        return
    if state in ("queued", "running", "stopping"):
        bar.setRange(0, 0)  # indeterminate marquee
        bar.setFormat({"queued":"Queued…", "running":"Running…", "stopping":"Stopping…"}.get(state, msg or ""))
    elif state == "done":
        bar.setRange(0, 100); bar.setValue(100); bar.setFormat("Done")
    elif state == "failed":
        bar.setRange(0, 100); bar.setValue(0);   bar.setFormat(msg or "Failed")
    elif state == "stopped":
        bar.setRange(0, 100); bar.setValue(0);   bar.setFormat("Stopped")
    else:
        bar.setRange(0, 100); bar.setValue(0);   bar.setFormat("")


# ----------------------- batch worker thread ----------------------

class _SegBatchWorker(QObject):
    series_started   = pyqtSignal(int)                 # row
    series_finished  = pyqtSignal(int, bool, str)      # row, ok, message
    cancelled_rows   = pyqtSignal(list)                # rows list to mark 'Stopped'
    all_done         = pyqtSignal()

    def __init__(self, owner, series_list: List[Dict[str, Any]], params: Dict[str, Any], parent=None):
        super().__init__(parent)
        self._owner = owner
        self._series: List[Dict[str, Any]] = list(series_list)
        self._params = dict(params or {})

    def _cancel_flag(self) -> bool:
        segwin = getattr(self._owner, "segwin", None) or self._owner
        return bool(getattr(segwin, "_seg_cancel", False))

    def run(self):
        # Build ordered list of rows matching the selected series
        ordered_rows: List[int] = []
        for meta in self._series:
            r = _match_row_for_meta(self._owner.segwin, meta)
            if r >= 0:
                ordered_rows.append(r)

        for i, meta in enumerate(self._series):
            row = ordered_rows[i] if i < len(ordered_rows) else -1

            if self._cancel_flag():
                # mark current (if any) and all remaining as 'Stopped'
                if row >= 0:
                    self.series_finished.emit(row, False, "Stopped")
                remain = ordered_rows[i:] if i < len(ordered_rows) else []
                if remain:
                    self.cancelled_rows.emit(remain)
                break

            if row >= 0:
                self.series_started.emit(row)

            ok, msg = True, ""
            try:
                # Run just this single series; vendored code respects cancel mid-run
                run_totalseg_for_series(self._owner, [meta], self._params)
            except Exception as ex:
                ok, msg = False, str(ex)

            if self._cancel_flag():
                ok, msg = False, "Stopped"

            if row >= 0:
                self.series_finished.emit(row, ok, msg)

            if self._cancel_flag():
                remain = ordered_rows[i+1:] if (i + 1) < len(ordered_rows) else []
                if remain:
                    self.cancelled_rows.emit(remain)
                break

        self.all_done.emit()


# ---------------------- controller / wiring -----------------------

_STOP_ATTRS = ("btn_stop", "btnStop", "btn_stop_seg", "btn_stop_run", "btn_cancel")


def _find_stop_buttons(win: SegmentatorWindow):
    """Locate Stop-like buttons by common attribute names; cache them on the window."""
    if hasattr(win, "_stop_buttons") and win._stop_buttons:
        return win._stop_buttons
    found = []
    for attr in _STOP_ATTRS:
        btn = getattr(win, attr, None)
        if btn:
            found.append(btn)
    win._stop_buttons = found
    return found


def _bind_stop_handler_once(win: SegmentatorWindow, handler):
    """
    Connect the handler to all Stop buttons once.
    Also record a flag to avoid duplicate connects.
    """
    if getattr(win, "_stop_bound", False):
        return
    for btn in _find_stop_buttons(win):
        btn.clicked.connect(handler)
    win._stop_bound = True


def _set_controls_busy(win: SegmentatorWindow, busy: bool):
    # Enable/disable Run
    if hasattr(win, "btn_run") and win.btn_run:
        win.btn_run.setEnabled(not busy)
    # Enable/disable ALL detected Stop buttons (independent of how many series are selected)
    for btn in _find_stop_buttons(win):
        btn.setEnabled(busy)


def _start_batch_with_progress(win: SegmentatorWindow, owner, series_list, params):
    """Spin a worker thread, animate per-row progress bars, and handle Stop properly."""
    if not series_list:
        return  # nothing to do

    _ensure_status_column(win)

    # Map / order rows for selected series
    ordered_rows: List[int] = []
    for meta in series_list:
        r = _match_row_for_meta(win, meta)
        if r >= 0:
            ordered_rows.append(r)

    # Pre-mark selected as queued
    win._batch_rows = set(ordered_rows)
    win._current_row = None
    win._seg_cancel = False
    for r in ordered_rows:
        _set_row_state(win, r, "queued")

    # Controls: ALWAYS enable Stop for any non-empty selection
    def _on_stop_clicked():
        # Flip cancel flag; immediately reflect in UI
        win._seg_cancel = True
        if getattr(win, "_current_row", None) is not None:
            _set_row_state(win, win._current_row, "stopping")
        # Mark queued-but-not-started rows as 'Stopped'
        for r in list(getattr(win, "_batch_rows", set())):
            if r != getattr(win, "_current_row", None):
                _set_row_state(win, r, "stopped")

    _bind_stop_handler_once(win, _on_stop_clicked)
    _set_controls_busy(win, True)  # <- this enables the Stop button now

    # Create thread + worker
    thread = QThread(win)
    worker = _SegBatchWorker(owner, series_list, params)
    worker.moveToThread(thread)

    # GUI-thread updates
    def _on_series_started(row: int):
        win._current_row = row
        _set_row_state(win, row, "running")

    def _on_series_finished(row: int, ok: bool, msg: str):
        if hasattr(win, "_batch_rows") and row in win._batch_rows:
            win._batch_rows.discard(row)
        if msg == "Stopped":
            _set_row_state(win, row, "stopped")
        else:
            _set_row_state(win, row, "done" if ok else "failed", msg or "")
        win._current_row = None

    def _on_cancelled_rows(rows: List[int]):
        for r in rows:
            if hasattr(win, "_batch_rows") and r in win._batch_rows:
                _set_row_state(win, r, "stopped")
                win._batch_rows.discard(r)

    def _on_all_done():
        # Any leftover queued rows become Stopped/Failed accordingly
        for r in list(getattr(win, "_batch_rows", set())):
            _set_row_state(win, r, "stopped" if getattr(win, "_seg_cancel", False) else "failed")
        win._batch_rows = set()
        win._current_row = None
        win._seg_cancel = False
        _set_controls_busy(win, False)  # disable Stop, re-enable Run

    worker.series_started.connect(_on_series_started)
    worker.series_finished.connect(_on_series_finished)
    worker.cancelled_rows.connect(_on_cancelled_rows)
    worker.all_done.connect(_on_all_done)

    thread.started.connect(worker.run)
    thread.finished.connect(thread.deleteLater)

    # Keep references
    win._seg_worker_thread = thread
    win._seg_worker = worker

    # Go!
    thread.start()


# -------------------------- public entry -------------------------------------

def open_segmentator_tab(self):
    """
    Create (or re-focus) the Segmentator window and wire the Run action
    to a background batch that supports clean cancellation.
    """
    # Reuse existing window if alive
    if getattr(self, "segwin", None) is not None:
        try:
            if not sip.isdeleted(self.segwin) and self.segwin.isVisible():
                self.segwin.raise_()
                self.segwin.activateWindow()
                return
        except RuntimeError:
            self.segwin = None

    excluded = {"RTPLAN", "RTSTRUCT", "RTDOSE"}
    self.segwin = SegmentatorWindow(
        parent=None,
        dicom_data=getattr(self, "dicom_data", {}) or {},
        excluded_modalities=excluded,
        data_provider=lambda: getattr(self, "dicom_data", {}) or {},
    )
    self.segwin.setAttribute(Qt.WA_DeleteOnClose, True)
    self.segwin.destroyed.connect(lambda *_: setattr(self, "segwin", None))

    # Ensure status column now
    _ensure_status_column(self.segwin)

    # Wire Run -> batch with progress + cancellation
    self.segwin.runSegRequested.connect(
        lambda series_list, params, owner=self:
            _start_batch_with_progress(self.segwin, owner, series_list, params)
    )

    # Ensure Stop buttons are discovered and initially disabled
    _find_stop_buttons(self.segwin)
    _set_controls_busy(self.segwin, False)

    # Show
    self.segwin.show()
    self.segwin.raise_()
    self.segwin.activateWindow()
