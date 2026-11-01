"""
Widgets for View > PLAN > Brachy: a table whose preferred width fits its columns,
a tree with check boxes (catheter / reference point list), a number box without
trailing zeros, the style of the colored buttons, and the icons of the catheter
edit tools and color buttons (drawn, no image files).
"""
from PySide6.QtCore import QLocale, QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap, QPolygonF
from PySide6.QtWidgets import QDoubleSpinBox, QScrollArea, QStyle, QStyleOptionViewItem, QTableWidget, QTreeWidget


INK = QColor("#263238")
PATH = QColor("#78909c")
ACCENT = QColor("#ff8f00")
# Colored buttons when disabled (their color would make them look enabled)
DISABLED_BUTTON_STYLE = "background-color: #37414f; color: #788d9c; border: 1px solid #455364;"


def colored_button_style(style):
    """Style sheet of a colored button: 'style', and greyed when disabled."""
    return f"QPushButton {{ {style} }} QPushButton:disabled {{ {DISABLED_BUTTON_STYLE} }}"


class TrimmedDoubleSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox showing its value without trailing zeros (40700 U, 40832.7 U)."""

    def textFromValue(self, value):
        locale = QLocale(self.locale())
        locale.setNumberOptions(locale.numberOptions() | QLocale.NumberOption.OmitGroupSeparator)
        text = locale.toString(float(value), 'f', self.decimals())
        point = locale.decimalPoint()
        return text.rstrip('0').rstrip(point) if point in text else text


class ContentWidthTable(QTableWidget):
    """QTableWidget that asks for the width of its columns; it still shrinks when space is short."""

    def sizeHint(self):
        header = self.verticalHeader()
        width = (self.horizontalHeader().length() + (0 if header.isHidden() else header.sizeHint().width())
                 + self.verticalScrollBar().sizeHint().width() + 2 * self.frameWidth() + 2)
        return QSize(max(width, 160), super().sizeHint().height())


class FitScrollArea(QScrollArea):
    """
    QScrollArea that asks for the current size of its content (QScrollArea caches the first one).
    keep_width: it is not made narrower than its content (it only scrolls vertically).
    """

    def __init__(self, parent=None, keep_width=False):
        super().__init__(parent)
        self._keep_width = keep_width

    def sizeHint(self):
        content = self.widget()
        if content is None:
            return super().sizeHint()
        frame = 2 * self.frameWidth()
        return content.sizeHint() + QSize(frame, frame)

    def minimumSizeHint(self):
        hint = super().minimumSizeHint()
        content = self.widget()
        if self._keep_width and content is not None:
            hint.setWidth(content.minimumSizeHint().width() + 2 * self.frameWidth())
        return hint


class CheckTree(QTreeWidget):
    """
    QTreeWidget for a list with check boxes: clicking a check box toggles it without
    making its item current (clicking the text selects the item). Its preferred width
    fits the first column.
    """

    def on_check_box(self, pos):
        """True if the viewport position pos is on the check box of an item."""
        item = self.itemAt(pos)
        if item is None or not item.flags() & Qt.ItemIsUserCheckable:
            return False
        opt = QStyleOptionViewItem()
        opt.initFrom(self)
        opt.rect = self.visualItemRect(item)
        opt.features = QStyleOptionViewItem.ViewItemFeature.HasCheckIndicator | QStyleOptionViewItem.ViewItemFeature.HasDisplay
        box = self.style().subElementRect(QStyle.SubElement.SE_ItemViewItemCheckIndicator, opt, self)
        return box.adjusted(-2, -2, 2, 2).contains(pos)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton or not self.on_check_box(event.position().toPoint()):
            super().mousePressEvent(event)
            return
        current = self.currentItem()
        self.blockSignals(True)
        try:
            super().mousePressEvent(event)  # the release toggles the check box
            if current is not None:
                self.setCurrentItem(current)
            else:
                self.selectionModel().clear()
        finally:
            self.blockSignals(False)

    def sizeHint(self):
        width = self.sizeHintForColumn(0) + self.verticalScrollBar().sizeHint().width() + 2 * self.frameWidth() + 4
        return QSize(max(width, 150), super().sizeHint().height())


def _arrow_head(painter, tip, direction, size):
    """Filled arrow head with its tip at 'tip', pointing along 'direction'."""
    norm = (direction.x() ** 2 + direction.y() ** 2) ** 0.5 or 1.0
    ux, uy = direction.x() / norm, direction.y() / norm
    bx, by, half = tip.x() - size * ux, tip.y() - size * uy, 0.55 * size
    painter.save()
    painter.setPen(Qt.NoPen)
    painter.setBrush(INK)
    painter.drawPolygon(QPolygonF([tip, QPointF(bx - half * uy, by + half * ux), QPointF(bx + half * uy, by - half * ux)]))
    painter.restore()


def _arc_arrow(painter, rect, start, sweep, pen):
    """Arc (angles in degrees, counter-clockwise) ending in an arrow head."""
    path = QPainterPath()
    path.arcMoveTo(rect, start)
    path.arcTo(rect, start, sweep)
    painter.strokePath(path, pen)
    end = path.pointAtPercent(1.0)
    _arrow_head(painter, end, end - path.pointAtPercent(0.95), 7.0)


def tool_icon(kind):
    """Icon of a catheter edit tool: 'move', 'translate', 'rotate' or 'undo' (drawn on a 32 x 32 grid)."""
    pix = QPixmap(64, 64)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.scale(2.0, 2.0)
    pen = QPen(INK, 2.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    if kind == 'move':
        # catheter path with one point dragged up and to the right
        painter.setPen(QPen(PATH, 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPolyline(QPolygonF([QPointF(4, 28), QPointF(12, 19), QPointF(28, 25)]))
        painter.setPen(Qt.NoPen)
        painter.setBrush(PATH)
        painter.drawEllipse(QPointF(4, 28), 2.5, 2.5)
        painter.drawEllipse(QPointF(28, 25), 2.5, 2.5)
        painter.setBrush(ACCENT)
        painter.drawEllipse(QPointF(12, 19), 4.5, 4.5)
        painter.setPen(pen)
        painter.drawLine(QPointF(15.5, 15.5), QPointF(21.5, 9.5))
        _arrow_head(painter, QPointF(27, 4), QPointF(1, -1), 7.5)
    elif kind == 'translate':
        # four-way arrow
        painter.setPen(pen)
        painter.drawLine(QPointF(16, 9), QPointF(16, 23))
        painter.drawLine(QPointF(9, 16), QPointF(23, 16))
        for tip, d in (((16, 2), (0, -1)), ((16, 30), (0, 1)), ((2, 16), (-1, 0)), ((30, 16), (1, 0))):
            _arrow_head(painter, QPointF(*tip), QPointF(*d), 7.5)
    elif kind == 'rotate':
        # clockwise circular arrow
        _arc_arrow(painter, QRectF(5, 5, 22, 22), 110, -290, pen)
    elif kind == 'undo':
        # arrow curving back to the left
        _arc_arrow(painter, QRectF(6, 9, 20, 20), 0, 180, pen)
    painter.end()
    return QIcon(pix)


def color_swatch_icon(rgb, size=16):
    """Square color swatch (rgb in 0-1) for the overlay color buttons."""
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor.fromRgbF(*rgb))
    painter.setPen(QColor("#455A64"))
    painter.drawRoundedRect(QRectF(1, 1, size - 2, size - 2), 3, 3)
    painter.end()
    return QIcon(pix)
