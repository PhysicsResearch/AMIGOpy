"""
Titles of a QTabWidget in columns on its left (the View module's sub-tabs, tabView01): larger than in
the widget's own west tab bar (hidden), where they ran out of height in one column.
Titles read bottom up like west tabs; the columns are read top to bottom, then the next column, cut
where the tallest column is the shortest. When the panel is too short for them, all titles get
smaller together (down to MIN_POINT_SIZE), then more columns are used. The QTabWidget stays the one
source of the current tab (other modules use its currentIndex, currentWidget and currentChanged): a
click on a title only calls its setCurrentIndex, and the titles follow its currentChanged.
"""
import math
from itertools import combinations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QFontMetricsF, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QAbstractButton, QButtonGroup, QHBoxLayout, QSizePolicy, QWidget

COLUMNS = 2
POINT_SIZE = 12         # the tab widget's own font: 10
MIN_POINT_SIZE = 8      # a short panel makes all titles smaller, down to this, then adds columns
SPACING = 2             # px between the titles, the columns and the tab widget
PAD_ALONG = 5           # px before and after the text
PAD_ACROSS = 4          # px beside the text
EDGE = 3                # px, the current tab's coloured edge (right)
RADIUS = 4
# qdarkstyle's colours of tabs on the left (QTabBar::tab:left)
COLORS = {"tab": "#455364", "current": "#54687A", "edge": "#259AE9", "hover": "#1A72BB",
          "edge_disabled": "#26486B", "text": "#DFE1E2", "text_current": "#FFFFFF", "text_disabled": "#788D9C"}


def title_length(font, text):
    """
    Length of a title (px): its text rounded up, and the padding. On a scaled screen (125 %) text widths
    are fractional: QFontMetrics.horizontalAdvance rounds them, down for some titles, which then did not
    fit when drawn (elided to 'PL…').
    """
    return math.ceil(QFontMetricsF(font).horizontalAdvance(text)) + 2 * PAD_ALONG


def column_height(lengths, run, spacing=SPACING):
    """Height of a column holding the titles 'run' (indices into lengths)."""
    return sum(lengths[i] for i in run) + spacing * (len(run) - 1)


def column_split(lengths, columns=COLUMNS, spacing=SPACING):
    """
    Titles (their lengths, in order) cut into up to 'columns' runs, one per column, whose tallest column
    is the shortest: [[title indices of column 1], [column 2], ...]. On a tie the first column gets more.
    """
    n = len(lengths)
    if n == 0:
        return []
    best = None
    for cuts in combinations(range(1, n), min(columns, n) - 1):
        bounds = (0, *cuts, n)
        runs = [range(a, b) for a, b in zip(bounds, bounds[1:])]
        tallest = max(column_height(lengths, run, spacing) for run in runs)
        if best is None or tallest <= best[0]:
            best = (tallest, runs)
    return [list(run) for run in best[1]]


def _tab_shape(rect):
    """Rounded on the left only, like a west tab."""
    shape = QPainterPath()
    shape.addRoundedRect(rect, RADIUS, RADIUS)
    right = QPainterPath()
    right.addRect(rect.adjusted(rect.width() / 2, 0, 0, 0))
    return shape.united(right)


class ColumnTab(QAbstractButton):
    """A tab title turned to read bottom up (like a west tab); elided when it gets less than its length."""

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self._tip = ""
        self.setText(text)
        self.setCheckable(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)

    def _font(self, current):
        font = QFont(self.font())
        font.setBold(current)
        return font

    def sizeHint(self):
        # the bold title of the current tab: no size change when it becomes current
        bold = self._font(True)
        return QSize(QFontMetrics(bold).height() + 2 * PAD_ACROSS + EDGE, title_length(bold, self.text()))

    def shown_text(self):
        """The title as drawn: whole when the tab has its length, elided only when it gets less."""
        if self.height() >= self.sizeHint().height():
            return self.text()
        return QFontMetricsF(self._font(self.isChecked())).elidedText(
            self.text(), Qt.TextElideMode.ElideRight, max(0, self.height() - 2 * PAD_ALONG))

    def set_tip(self, tip):
        """The tab's tooltip; without one, the whole title when it is elided."""
        self._tip = tip
        self._update_tip()

    def _update_tip(self):
        self.setToolTip(self._tip or (self.text() if self.height() < self.sizeHint().height() else ""))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_tip()

    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        current, enabled = self.isChecked(), self.isEnabled()
        hovered = enabled and not current and self.underMouse()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        p.fillPath(_tab_shape(rect), QColor(COLORS["current" if current else "tab"]))
        if current or hovered:
            edge = QColor(COLORS["hover" if hovered else "edge" if enabled else "edge_disabled"])
            p.fillRect(rect.adjusted(rect.width() - EDGE, 0, 0, 0), edge)
            if hovered:
                p.strokePath(_tab_shape(rect.adjusted(0.5, 0.5, -0.5, -0.5)), QPen(edge, 1))
        p.setFont(self._font(current))
        p.setPen(QColor(COLORS["text_current" if current else "text" if enabled else "text_disabled"]))
        p.translate(0, self.height())
        p.rotate(-90)                       # x up the tab, y to the right: reads bottom up
        p.drawText(QRectF(0, 0, self.height(), self.width() - EDGE), Qt.AlignmentFlag.AlignCenter,
                   self.shown_text())


class ColumnTabBar(QWidget):
    """The titles of a QTabWidget in columns: a click makes its tab current, the current title follows the widget."""

    def __init__(self, tabs, parent=None, columns=COLUMNS, point_size=POINT_SIZE):
        super().__init__(parent)
        self.tabs = tabs
        self.n_columns = columns
        font = QFont(tabs.font())
        font.setPointSize(point_size)
        self.setFont(font)                  # the titles' largest font
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self._shown = None                  # the tabs' texts, tooltips, visible and enabled shown
        self._size = float(point_size)      # the titles' font size now
        self._runs = []                     # tab indices of each column
        self._laid_out = False              # given its height by the layout (resizeEvent)
        self.group = QButtonGroup(self)     # exclusive: a click on the current title keeps it current
        self.group.idClicked.connect(tabs.setCurrentIndex)
        tabs.tabBar().hide()
        tabs.currentChanged.connect(self.follow)
        self.sync()

    def buttons(self):
        """The title of each tab, by tab index (None for a hidden tab)."""
        return [self.group.button(i) for i in range(self.tabs.count())]

    def columns(self):
        """The titles of each column, top to bottom."""
        return [[self.group.button(i) for i in run] for run in self._runs]

    def _state(self):
        t = self.tabs
        return [(t.tabText(i), t.tabToolTip(i), t.isTabVisible(i), t.isTabEnabled(i)) for i in range(t.count())]

    def sync(self):
        """Titles again from the tab widget: texts (set later by retranslate_ui), tooltips, hidden or disabled tabs."""
        state = self._state()
        if state != self._shown:
            self._shown = state
            self._build(state)
            self._fit()
        self.follow(self.tabs.currentIndex())

    def _build(self, state):
        for btn in self.group.buttons():
            self.group.removeButton(btn)
            btn.hide()
            btn.deleteLater()
        for i, (text, tip, visible, enabled) in enumerate(state):
            if visible:
                btn = ColumnTab(text, self)
                # set on each: made after a style sheet styled the bar, it would not get the bar's font
                btn.setFont(self._title_font(self._size))
                btn.set_tip(tip)
                btn.setEnabled(enabled)
                self.group.addButton(btn, i)
                btn.show()

    def _title_font(self, size, bold=False):
        font = QFont(self.font())
        font.setPointSizeF(size)
        font.setBold(bold)
        return font

    def _column_width(self):
        return QFontMetrics(self._title_font(self._size, bold=True)).height() + 2 * PAD_ACROSS + EDGE

    def _plan(self, ids, height):
        """
        (font size, tab indices of each column) for this height: COLUMNS columns with the largest font
        that fits, down to MIN_POINT_SIZE; if that does not fit either, more columns.
        """
        def lengths_at(size):
            bold = self._title_font(size, bold=True)
            return [title_length(bold, self.group.button(i).text()) for i in ids]

        def tallest(lengths, runs):
            return max((column_height(lengths, run) for run in runs), default=0)

        size = self.font().pointSizeF()
        lengths = lengths_at(size)
        runs = column_split(lengths, self.n_columns)
        while tallest(lengths, runs) > height and size > MIN_POINT_SIZE:
            size = max(size - 0.5, MIN_POINT_SIZE)
            lengths = lengths_at(size)
            runs = column_split(lengths, self.n_columns)
        n_columns = self.n_columns
        while tallest(lengths, runs) > height and n_columns < len(ids):
            n_columns += 1
            runs = column_split(lengths, n_columns)
        return size, [[ids[j] for j in run] for run in runs]

    def _fit(self):
        """Font size and columns for the bar's height (before its first layout: the largest font), titles placed."""
        ids = [i for i in range(self.tabs.count()) if self.group.button(i) is not None]
        size, runs = self._plan(ids, self.height() if self._laid_out else float("inf"))
        resized = size != self._size
        if resized:
            self._size = size
            for btn in self.group.buttons():
                btn.setFont(self._title_font(size))
        if resized or runs != self._runs:
            self._runs = runs
            self.updateGeometry()           # the bar's width
        self._place()

    def _place(self):
        width = self._column_width()
        for k, run in enumerate(self._runs):
            y = 0
            for i in run:
                btn = self.group.button(i)
                length = max(0, min(btn.sizeHint().height(), self.height() - y))
                btn.setGeometry(k * (width + SPACING), y, width, length)
                y += length + SPACING

    def sizeHint(self):
        n = len(self._runs)
        height = max((sum(btn.sizeHint().height() for btn in column) + SPACING * (len(column) - 1)
                      for column in self.columns()), default=0)
        return QSize(n * self._column_width() + SPACING * max(n - 1, 0), height)

    def minimumSizeHint(self):
        return QSize(self.sizeHint().width(), 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._laid_out = True
        self._fit()

    def follow(self, index):
        """The current tab's title checked (none for no tab or a hidden one)."""
        btn = self.group.button(index)
        if btn is not None:
            btn.setChecked(True)
        elif self.group.checkedButton() is not None:
            self.group.setExclusive(False)
            self.group.checkedButton().setChecked(False)
            self.group.setExclusive(True)


def column_tab_box(tabs, parent=None, columns=COLUMNS, point_size=POINT_SIZE):
    """The tab widget with its titles in columns on its left: (box, bar). The box goes where the tab widget was."""
    box = QWidget(parent)
    box.setObjectName(f"{tabs.objectName()}_box")
    box.setSizePolicy(tabs.sizePolicy())
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(SPACING)
    bar = ColumnTabBar(tabs, box, columns, point_size)
    bar.setObjectName(f"{tabs.objectName()}_bar")
    row.addWidget(bar)
    row.addWidget(tabs, 1)
    return box, bar
