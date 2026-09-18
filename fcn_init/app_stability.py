"""
Application-wide logging and crash handling.

Replaces the old launcher code that truncated the log on every start and called
sys.exit(1) from sys.excepthook: an unhandled exception inside a Qt slot used to
take the whole application down. Now it is logged, reported once (with a
throttle against dialog storms) and the event loop keeps running; only failures
before the main window is shown remain fatal.
"""

import faulthandler
import io
import logging
import os
import sys
import threading
import time
import traceback
from logging.handlers import RotatingFileHandler

LOGGER_NAME = "amigopy"
_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


def setup_logging(log_dir):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "amigopy.log")

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    for handler in list(root.handlers):
        root.removeHandler(handler)

    file_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
        try:
            file_handler.doRollover()
        except OSError:
            pass
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_FORMAT))
    root.addHandler(file_handler)

    if sys.__stderr__ is not None:
        console = logging.StreamHandler(sys.__stderr__)
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        root.addHandler(console)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)

    try:
        native_log = open(os.path.join(log_dir, "amigopy_native.log"), "a", encoding="utf-8")
        faulthandler.enable(file=native_log, all_threads=True)
    except OSError:
        faulthandler.enable()

    logger.info("=== AMIGOpy started (pid %s) ===", os.getpid())
    return logger, log_path


class StreamToLogger(io.TextIOBase):
    """Redirects print()/stderr text into the logger, one log record per line."""

    def __init__(self, logger, level, fallback_stream=None):
        super().__init__()
        self._logger = logger
        self._level = level
        self._fallback = fallback_stream
        self._buffer = ""

    def writable(self):
        return True

    def isatty(self):
        return False

    def write(self, message):
        if not isinstance(message, str):
            message = str(message)
        if not logging.getLogger().handlers and self._fallback is not None:
            try:
                self._fallback.write(message)
            except Exception:
                pass
            return len(message)
        self._buffer += message
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line.strip():
                self._logger.log(self._level, line.rstrip())
        return len(message)

    def flush(self):
        if self._buffer.strip():
            self._logger.log(self._level, self._buffer.rstrip())
        self._buffer = ""
        if self._fallback is not None:
            try:
                self._fallback.flush()
            except Exception:
                pass


def install_qt_message_handler(logger):
    try:
        from PySide6.QtCore import QtMsgType, qInstallMessageHandler
    except ImportError:
        return
    levels = {
        QtMsgType.QtDebugMsg: logging.DEBUG,
        QtMsgType.QtInfoMsg: logging.INFO,
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg: logging.CRITICAL,
    }

    def handler(mode, context, message):
        logger.log(levels.get(mode, logging.WARNING), "Qt: %s", message)

    qInstallMessageHandler(handler)


class DialogThrottle:
    """Decides whether an error deserves a dialog or only a log line."""

    def __init__(self, dedupe_window=30.0, max_dialogs=3, burst_window=10.0, cooldown=60.0):
        self.dedupe_window = dedupe_window
        self.max_dialogs = max_dialogs
        self.burst_window = burst_window
        self.cooldown = cooldown
        self._last_seen = {}
        self._recent = []
        self._cooldown_until = 0.0
        self.suppressed = 0

    def allow(self, key, now=None):
        now = time.monotonic() if now is None else now
        if now < self._cooldown_until:
            self.suppressed += 1
            return False
        last = self._last_seen.get(key)
        self._last_seen[key] = now
        if last is not None and now - last < self.dedupe_window:
            self.suppressed += 1
            return False
        self._recent = [t for t in self._recent if now - t < self.burst_window]
        if len(self._recent) >= self.max_dialogs:
            self._cooldown_until = now + self.cooldown
            self.suppressed += 1
            return False
        self._recent.append(now)
        return True

    def take_suppressed(self):
        count = self.suppressed
        self.suppressed = 0
        return count


def _last_frame(tb):
    last = None
    while tb is not None:
        last = tb
        tb = tb.tb_next
    if last is None:
        return "?"
    frame = last.tb_frame
    return f"{os.path.basename(frame.f_code.co_filename)}:{last.tb_lineno}"


def install_exception_hooks(logger, log_path, is_ui_ready, get_parent):
    throttle = DialogThrottle()
    state = {"dialog_open": False}

    def show_dialog(exctype, value, tb_str):
        if state["dialog_open"]:
            return
        state["dialog_open"] = True
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox

            parent = None
            try:
                parent = get_parent()
            except Exception:
                pass
            box = QMessageBox(parent)
            box.setIcon(QMessageBox.Warning)
            box.setWindowTitle("AMIGOpy - unexpected error")
            box.setText("AMIGOpy hit an unexpected error and will try to continue.")
            box.setInformativeText(
                f"{exctype.__name__}: {value}\n\nThe full traceback was written to:\n{log_path}"
            )
            box.setDetailedText(tb_str)
            btn_continue = box.addButton("Continue", QMessageBox.AcceptRole)
            btn_copy = box.addButton("Copy details", QMessageBox.ActionRole)
            btn_quit = box.addButton("Quit AMIGOpy", QMessageBox.DestructiveRole)
            box.setDefaultButton(btn_continue)
            while True:
                box.exec()
                if box.clickedButton() is btn_copy:
                    QApplication.clipboard().setText(tb_str)
                    continue
                break
            if box.clickedButton() is btn_quit:
                app = QApplication.instance()
                if app is not None:
                    app.quit()
        except Exception:
            logger.exception("Could not display the error dialog")
        finally:
            state["dialog_open"] = False

    def excepthook(exctype, value, tb):
        try:
            if issubclass(exctype, (KeyboardInterrupt, SystemExit)):
                sys.__excepthook__(exctype, value, tb)
                return
            tb_str = "".join(traceback.format_exception(exctype, value, tb))
            logger.error("Unhandled exception:\n%s", tb_str)
            if threading.current_thread() is not threading.main_thread():
                return
            if not is_ui_ready():
                try:
                    from PySide6.QtWidgets import QApplication, QMessageBox
                    if QApplication.instance() is not None:
                        QMessageBox.critical(
                            None, "AMIGOpy failed to start",
                            f"AMIGOpy could not finish starting up.\n\n{exctype.__name__}: {value}\n\n"
                            f"Details were written to:\n{log_path}",
                        )
                except Exception:
                    pass
                sys.exit(1)
            key = (exctype.__name__, str(value)[:200], _last_frame(tb))
            if throttle.allow(key):
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, lambda: show_dialog(exctype, value, tb_str))
            else:
                logger.warning("Error dialog suppressed (%d suppressed so far); see log for details",
                               throttle.suppressed)
                try:
                    parent = get_parent()
                    if parent is not None and hasattr(parent, "statusBar"):
                        parent.statusBar().showMessage("An error was logged (see amigopy.log)", 5000)
                except Exception:
                    pass
        except SystemExit:
            raise
        except Exception:
            sys.__excepthook__(exctype, value, tb)

    def thread_hook(args):
        name = args.thread.name if args.thread is not None else "?"
        tb_str = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
        logger.error("Unhandled exception in thread %s:\n%s", name, tb_str)

    sys.excepthook = excepthook
    threading.excepthook = thread_hook
    return throttle
