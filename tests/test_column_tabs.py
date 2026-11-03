"""
Titles of a QTabWidget in columns (fcn_create_gui/column_tabs.py, the View module's sub-tabs): the
tab widget stays the source of the current tab, the titles follow its texts and current tab, and a
short panel makes them smaller, then adds columns, instead of cutting them.
"""
import pytest

from fcn_create_gui.column_tabs import (COLUMNS, MIN_POINT_SIZE, POINT_SIZE, column_height, column_split,
                                        column_tab_box)

TITLES = ["View", "PLAN", "STRUCT", "IrIS", "4DCT", "ROI", "Evaluation", "MonteCarlo"]


def test_split_keeps_the_order_and_balances_the_columns():
    assert column_split([10] * 8, 2) == [[0, 1, 2, 3], [4, 5, 6, 7]]
    assert column_split([10] * 3, 2) == [[0, 1], [2]]                  # a tie: the first column gets more
    assert column_split([100, 10, 10, 10, 10, 10], 2) == [[0], [1, 2, 3, 4, 5]]
    assert column_split([10, 20], 5) == [[0], [1]]
    assert column_split([], 2) == []
    lengths = [48, 52, 69, 35, 50, 37, 92, 100]
    runs = column_split(lengths, 2, spacing=2)
    assert sum(runs, []) == list(range(8))
    tallest = max(column_height(lengths, run, 2) for run in runs)
    assert all(tallest <= max(column_height(lengths, range(0, k), 2), column_height(lengths, range(k, 8), 2))
               for k in range(1, 8))


@pytest.fixture
def tabs(qapp):
    """A west tab widget like tabView01 (10 pt), its titles in columns, shown in a tall panel."""
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QTabWidget, QWidget
    tab_widget = QTabWidget()
    tab_widget.setObjectName("tabView01")
    font = QFont()
    font.setPointSize(10)
    tab_widget.setFont(font)
    tab_widget.setTabPosition(QTabWidget.TabPosition.West)
    for title in TITLES:
        tab_widget.addTab(QWidget(), "")             # texts come later (retranslate_ui), then sync()
    box, bar = column_tab_box(tab_widget)
    for k, title in enumerate(TITLES):
        tab_widget.setTabText(k, title)
    bar.sync()
    box.resize(900, 500)
    box.show()
    qapp.processEvents()
    yield tab_widget, box, bar
    box.close()


def _texts(bar):
    return [[btn.text() for btn in column] for column in bar.columns()]


def test_titles_in_two_columns_larger_than_the_tabs(tabs):
    tab_widget, box, bar = tabs
    assert box.objectName() == "tabView01_box" and bar.objectName() == "tabView01_bar"
    assert tab_widget.tabBar().isHidden()
    assert len(bar.columns()) == COLUMNS and sum(_texts(bar), []) == TITLES
    for btn in bar.buttons():
        assert btn.font().pointSizeF() == POINT_SIZE > tab_widget.font().pointSizeF()
        assert btn.height() == btn.sizeHint().height()                  # whole titles
    first, second = bar.columns()
    assert first[0].x() == 0 and second[0].x() > first[0].x() + first[0].width() - 1
    assert bar.width() <= 2 * first[0].width() + 4


def test_current_title_is_whole(tabs):
    """
    The current title is bold: each title is as long as its bold text, rounded up (on a 125 % screen the
    widths are fractional; rounded down, 'PLAN' was drawn 'PL…'), and is not elided at that length.
    """
    from PySide6.QtGui import QFontMetricsF
    _tab_widget, _box, bar = tabs
    for btn in bar.buttons():
        btn.setChecked(True)
        bold = QFontMetricsF(btn._font(True)).horizontalAdvance(btn.text())
        assert btn.height() >= bold and btn.shown_text() == btn.text()
    short = bar.buttons()[7]
    short.resize(short.width(), short.sizeHint().height() // 2)          # only when it gets less
    assert short.shown_text() != short.text() and short.toolTip() == short.text()


def test_a_click_makes_its_tab_current_and_titles_follow_the_widget(tabs, qapp):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    tab_widget, _box, bar = tabs
    btns = bar.buttons()
    assert tab_widget.currentIndex() == 0 and btns[0].isChecked()
    for i in (6, 1, 7):
        QTest.mouseClick(btns[i], Qt.MouseButton.LeftButton)
        assert tab_widget.currentIndex() == i and [b.isChecked() for b in btns] == [k == i for k in range(8)]
    QTest.mouseClick(btns[7], Qt.MouseButton.LeftButton)                # the current one stays current
    assert tab_widget.currentIndex() == 7 and btns[7].isChecked()
    tab_widget.setCurrentIndex(2)                                       # from code (data tree, ...)
    assert btns[2].isChecked() and not btns[7].isChecked()


def test_sync_follows_texts_hidden_and_disabled_tabs(tabs, qapp):
    tab_widget, _box, bar = tabs
    before = bar.buttons()
    bar.sync()                                                          # nothing changed: same titles
    assert bar.buttons() == before
    tab_widget.setTabText(4, "4D CT")
    tab_widget.setTabVisible(5, False)
    tab_widget.setTabEnabled(3, False)
    tab_widget.setTabToolTip(0, "Histogram and DICOM header")
    bar.sync()
    qapp.processEvents()
    btns = bar.buttons()
    assert btns[4].text() == "4D CT" and btns[5] is None and not btns[3].isEnabled()
    assert btns[0].toolTip() == "Histogram and DICOM header"
    assert sum(_texts(bar), []) == ["View", "PLAN", "STRUCT", "IrIS", "4D CT", "Evaluation", "MonteCarlo"]
    assert btns[0].isChecked()


def test_short_panel_makes_titles_smaller_then_adds_columns(tabs, qapp):
    tab_widget, box, bar = tabs
    # the two columns' height with the largest titles (8 pt titles need about 3/4 of it)
    natural = max(column[-1].y() + column[-1].height() for column in bar.columns())
    plans = []
    for height in (500, int(0.85 * natural), int(0.45 * natural), 500):
        box.resize(900, height)
        for _ in range(3):
            qapp.processEvents()
        size = bar.buttons()[0].font().pointSizeF()
        plans.append((size, len(bar.columns())))
        assert MIN_POINT_SIZE <= size <= POINT_SIZE
        for column in bar.columns():                                    # whole titles, inside the panel
            assert all(btn.height() == btn.sizeHint().height() for btn in column)
            assert column[-1].y() + column[-1].height() <= bar.height()
    tall, short, tiny, tall_again = plans
    assert tall == tall_again == (POINT_SIZE, COLUMNS)
    assert MIN_POINT_SIZE < short[0] < POINT_SIZE and short[1] == COLUMNS
    assert tiny[0] == MIN_POINT_SIZE and tiny[1] > COLUMNS


def test_titles_keep_their_size_under_an_application_style_sheet(qapp):
    """
    A widget made under a parent already styled by a style sheet does not get the parent's font (the
    real app: qdarkstyle, then retranslate_ui sets the texts and the titles are made again).
    """
    from PySide6.QtWidgets import QTabWidget, QWidget
    qapp.setStyleSheet("QWidget { color: #DFE1E2; }")
    try:
        tab_widget = QTabWidget()
        tab_widget.addTab(QWidget(), "")
        tab_widget.addTab(QWidget(), "")
        holder = QWidget()
        box, bar = column_tab_box(tab_widget, holder)
        holder.resize(600, 400)
        box.resize(600, 400)
        holder.show()
        qapp.processEvents()
        tab_widget.setTabText(0, "View")
        tab_widget.setTabText(1, "MonteCarlo")
        bar.sync()
        qapp.processEvents()
        assert [btn.text() for btn in bar.buttons()] == ["View", "MonteCarlo"]
        assert [btn.font().pointSizeF() for btn in bar.buttons()] == [POINT_SIZE, POINT_SIZE]
        holder.close()
    finally:
        qapp.setStyleSheet("")
