import logging
import sys
import threading

import pytest

from fcn_init import app_stability as st


def test_throttle_dedupes_and_caps_bursts():
    t = st.DialogThrottle(dedupe_window=30, max_dialogs=3, burst_window=10, cooldown=60)
    key = ("ValueError", "boom", "x.py:1")
    assert t.allow(key, now=0)
    assert not t.allow(key, now=5)               # same error within the dedupe window
    assert t.allow(("A", "1", "a:1"), now=6)
    assert t.allow(("B", "2", "b:2"), now=7)
    assert not t.allow(("C", "3", "c:3"), now=8)  # 4th distinct error inside 10 s -> cooldown
    assert not t.allow(("D", "4", "d:4"), now=50)  # still cooling down
    assert t.allow(("D", "4", "d:4"), now=70)
    assert t.take_suppressed() == 3 and t.suppressed == 0


def test_stream_to_logger_emits_one_record_per_line(caplog):
    logger = logging.getLogger("amigopy.test_stream")
    stream = st.StreamToLogger(logger, logging.INFO)
    with caplog.at_level(logging.INFO, logger="amigopy.test_stream"):
        stream.write("first line\nsecond ")
        stream.write("half\n")
        stream.flush()
    assert [r.getMessage() for r in caplog.records] == ["first line", "second half"]


@pytest.fixture
def hooks(qapp):
    old_sys, old_thread = sys.excepthook, threading.excepthook
    logger = logging.getLogger("amigopy.test_hook")
    state = {"ready": True}
    yield logger, state
    sys.excepthook, threading.excepthook = old_sys, old_thread


def _raise_into_hook():
    try:
        raise ValueError("slot failure")
    except ValueError:
        sys.excepthook(*sys.exc_info())


def test_hook_does_not_exit_when_ui_ready(hooks, caplog, monkeypatch):
    logger, state = hooks
    st.install_exception_hooks(logger, "log.txt", is_ui_ready=lambda: state["ready"], get_parent=lambda: None)
    scheduled = []
    from PySide6.QtCore import QTimer
    monkeypatch.setattr(QTimer, "singleShot", lambda ms, fn: scheduled.append(fn))
    with caplog.at_level(logging.ERROR, logger="amigopy.test_hook"):
        _raise_into_hook()          # must not raise SystemExit
        _raise_into_hook()          # duplicate -> suppressed, only logged
    assert len(scheduled) == 1
    assert sum("Unhandled exception" in r.getMessage() for r in caplog.records) == 2


def test_hook_is_fatal_before_ui_ready(hooks, monkeypatch):
    logger, state = hooks
    state["ready"] = False
    shown = []
    from PySide6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, "critical", lambda *a, **k: shown.append(a[1]))  # a modal box would block offscreen
    st.install_exception_hooks(logger, "log.txt", is_ui_ready=lambda: state["ready"], get_parent=lambda: None)
    with pytest.raises(SystemExit):
        _raise_into_hook()
    assert shown == ["AMIGOpy failed to start"]


def test_worker_thread_exceptions_only_log(hooks, caplog):
    logger, _ = hooks
    st.install_exception_hooks(logger, "log.txt", is_ui_ready=lambda: True, get_parent=lambda: None)

    def worker():
        raise RuntimeError("in thread")
    with caplog.at_level(logging.ERROR, logger="amigopy.test_hook"):
        t = threading.Thread(target=worker)
        t.start()
        t.join()
    assert any("in thread" in r.getMessage() for r in caplog.records)
