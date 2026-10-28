# -*- coding: utf-8 -*-
"""
range_slider.py - Lightweight two-handle (range) slider for PySide6
===================================================================

A dependency-free horizontal slider with two handles (low / high).

Signals
-------
valuesChanged(int, int)   emitted whenever low or high changes
                          (by dragging, clicking, wheel or setValues).

API
---
setRange(minimum, maximum)
setValues(low, high)
values() -> (low, high)
low(), high(), minimum(), maximum()
setAccentColor(QColor | str)
"""

from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QWidget, QSizePolicy


class RangeSlider(QWidget):
    valuesChanged = Signal(int, int)

    _HANDLE_R = 7      # handle radius (px)
    _GROOVE_H = 4      # groove height (px)

    def __init__(self, parent=None, accent="#3b82f6"):
        super().__init__(parent)
        self._min, self._max = 0, 100
        self._low, self._high = 0, 100
        self._active = None          # 'low' | 'high' | None (dragging)
        self._hover = None
        self._accent = QColor(accent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(120)

    # ------------------------------------------------------------------ API
    def sizeHint(self):
        return QSize(200, 2 * self._HANDLE_R + 8)

    def minimumSizeHint(self):
        return QSize(80, 2 * self._HANDLE_R + 8)

    def setAccentColor(self, color):
        self._accent = QColor(color)
        self.update()

    def minimum(self):
        return self._min

    def maximum(self):
        return self._max

    def low(self):
        return self._low

    def high(self):
        return self._high

    def values(self):
        return self._low, self._high

    def setRange(self, minimum, maximum):
        minimum, maximum = int(minimum), int(maximum)
        if maximum < minimum:
            maximum = minimum
        self._min, self._max = minimum, maximum
        self.setValues(self._low, self._high)
        self.update()

    def setValues(self, low, high):
        low = max(self._min, min(int(low), self._max))
        high = max(self._min, min(int(high), self._max))
        if low > high:
            low, high = high, low
        changed = (low, high) != (self._low, self._high)
        self._low, self._high = low, high
        self.update()
        if changed:
            self.valuesChanged.emit(self._low, self._high)

    # ------------------------------------------------------------ geometry
    def _span(self):
        r = self._HANDLE_R
        return r + 1, max(r + 2, self.width() - r - 1)

    def _val_to_x(self, v):
        x0, x1 = self._span()
        if self._max == self._min:
            return x0
        return x0 + (v - self._min) * (x1 - x0) / (self._max - self._min)

    def _x_to_val(self, x):
        x0, x1 = self._span()
        if x1 == x0:
            return self._min
        frac = (x - x0) / (x1 - x0)
        frac = max(0.0, min(1.0, frac))
        return int(round(self._min + frac * (self._max - self._min)))

    def _nearest_handle(self, x):
        xl, xh = self._val_to_x(self._low), self._val_to_x(self._high)
        if abs(x - xl) == abs(x - xh):
            # handles overlap: choose by direction relative to them
            return "low" if x < xl else "high"
        return "low" if abs(x - xl) < abs(x - xh) else "high"

    # -------------------------------------------------------------- paint
    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cy = self.height() / 2.0
        x0, x1 = self._span()
        enabled = self.isEnabled()

        # groove
        gh = self._GROOVE_H
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#3c4450"))
        p.drawRoundedRect(QRectF(x0, cy - gh / 2, x1 - x0, gh), gh / 2, gh / 2)

        # selected span
        xl, xh = self._val_to_x(self._low), self._val_to_x(self._high)
        accent = QColor(self._accent) if enabled else QColor("#6b7280")
        p.setBrush(accent)
        p.drawRoundedRect(QRectF(xl, cy - gh / 2, max(1.0, xh - xl), gh), gh / 2, gh / 2)

        # handles
        for name, x in (("low", xl), ("high", xh)):
            r = self._HANDLE_R + (1 if name in (self._active, self._hover) else 0)
            p.setPen(QPen(accent, 2))
            p.setBrush(QBrush(QColor("#e5e7eb") if enabled else QColor("#9ca3af")))
            p.drawEllipse(QPointF(x, cy), r, r)
        p.end()

    # -------------------------------------------------------------- mouse
    def mousePressEvent(self, e):
        if e.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(e)
        x = e.position().x()
        self._active = self._nearest_handle(x)
        self._move_active(x)
        e.accept()

    def mouseMoveEvent(self, e):
        x = e.position().x()
        if self._active is not None:
            self._move_active(x)
        else:
            h = self._nearest_handle(x)
            if h != self._hover:
                self._hover = h
                self.update()
        e.accept()

    def mouseReleaseEvent(self, e):
        self._active = None
        self.update()
        e.accept()

    def leaveEvent(self, e):
        self._hover = None
        self.update()
        super().leaveEvent(e)

    def wheelEvent(self, e):
        step = 1 if e.angleDelta().y() > 0 else -1
        h = self._hover or "high"
        if h == "low":
            self.setValues(min(self._low + step, self._high), self._high)
        else:
            self.setValues(self._low, max(self._high + step, self._low))
        e.accept()

    def _move_active(self, x):
        v = self._x_to_val(x)
        if self._active == "low":
            self.setValues(min(v, self._high), self._high)
        elif self._active == "high":
            self.setValues(self._low, max(v, self._low))
