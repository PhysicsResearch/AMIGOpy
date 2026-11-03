"""
Button colours of the interface (fcn_create_gui/button_style.py): a button with a function is blue,
"Delete" red, "Remove" black, a placeholder (nothing connected) keeps qdarkstyle's grey; icon buttons,
colour swatches and customStyle buttons are left alone.
"""
import collections

import pytest

from fcn_create_gui.button_style import (ACTION, BUTTON_QSS, DELETE, PLACEHOLDER, REMOVE, apply_button_roles,
                                         button_role, colour_by_role, install_button_style)


def _button(text, connect=True):
    from PySide6.QtWidgets import QPushButton
    btn = QPushButton(text)
    if connect:
        btn.clicked.connect(lambda: None)
    return btn


def test_role_from_text_and_connection(qapp):
    from PySide6.QtWidgets import QButtonGroup, QMenu, QPushButton
    assert button_role(_button("Calculate TG43 dose")) == ACTION
    assert button_role(_button("Add level")) == ACTION and button_role(_button("+")) == ACTION
    assert button_role(_button("Delete row")) == DELETE and button_role(_button("&Delete")) == DELETE
    assert button_role(_button("Remove material")) == REMOVE and button_role(_button("-")) == REMOVE
    assert button_role(_button("Clear All")) == ACTION        # clear: uncheck all, clear a plot...
    assert button_role(_button("Deleted items")) == ACTION    # a word, not "Delete"
    assert button_role(_button("Calculate DVHs", connect=False)) == PLACEHOLDER
    assert button_role(_button("Delete column", connect=False)) == PLACEHOLDER
    toggled = QPushButton("Play")
    toggled.setCheckable(True)
    toggled.toggled.connect(lambda on: None)
    assert button_role(toggled) == ACTION
    in_group = QPushButton("Layer")                                # connected through its button group
    group = QButtonGroup()
    group.addButton(in_group, 0)
    assert button_role(in_group) == PLACEHOLDER
    group.idClicked.connect(lambda i: None)
    assert button_role(in_group) == ACTION
    with_menu = QPushButton("Mode")
    with_menu.setMenu(QMenu(with_menu))
    assert button_role(with_menu) == ACTION


def test_icon_buttons_swatches_and_custom_buttons_keep_their_look(qapp):
    from PySide6.QtGui import QIcon, QPixmap
    from PySide6.QtWidgets import QToolButton
    assert colour_by_role(_button("Save"))
    swatch = _button("")
    swatch.setStyleSheet("background-color: #ff8000; border: 1px solid #888;")
    custom = _button("Layer 1")
    custom.setProperty("customStyle", True)
    tool_text, tool_icon = QToolButton(), QToolButton()
    tool_text.setText("Dwells")
    pixmap = QPixmap(8, 8)
    pixmap.fill()
    tool_icon.setIcon(QIcon(pixmap))
    tool_icon.setText("Brush")
    assert not colour_by_role(swatch) and not colour_by_role(custom) and not colour_by_role(tool_icon)
    assert colour_by_role(tool_text)


@pytest.fixture
def styled_app(qapp):
    """The application with ButtonRoleStyle and qdarkstyle + BUTTON_QSS, as Launch_ImGUI sets them; restored after."""
    import qdarkstyle
    from PySide6.QtWidgets import QStyleFactory
    name = qapp.style().name()
    install_button_style(qapp)
    qapp.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6") + BUTTON_QSS)
    yield qapp
    qapp.setStyleSheet("")
    qapp.setStyle(QStyleFactory.create(name))


def _main_colour(btn):
    image = btn.grab().toImage()
    counts = collections.Counter(image.pixelColor(x, y).name()
                                 for x in range(image.width()) for y in range(image.height()))
    return counts.most_common(1)[0][0]


def test_colours_as_drawn(styled_app):
    from PySide6.QtWidgets import QVBoxLayout, QWidget
    holder = QWidget()
    layout = QVBoxLayout(holder)
    buttons = {"Save": _button("Save"), "Delete": _button("Delete"), "Remove": _button("Remove"),
               "placeholder": _button("Not yet", connect=False)}
    disabled = _button("Export")
    disabled.setEnabled(False)
    playing = _button("Play")                  # a toggle on (Play, New catheter while drawing): lighter blue
    playing.setCheckable(True)
    playing.setChecked(True)
    for btn in (*buttons.values(), disabled, playing):
        btn.setMinimumSize(120, 32)
        layout.addWidget(btn)
    holder.show()
    styled_app.processEvents()
    colours = {name: _main_colour(btn) for name, btn in buttons.items()}
    assert colours == {"Save": "#0000ff", "Delete": "#ff0000", "Remove": "#000000", "placeholder": "#455364"}
    assert _main_colour(disabled) not in ("#0000ff", "#455364")          # dimmed, not a placeholder's grey
    assert _main_colour(playing) == "#259ae9"
    # connected after it was polished (module tabs that connect their buttons when first opened)
    late = buttons["placeholder"]
    late.clicked.connect(lambda: None)
    assert _main_colour(late) == "#455364"
    apply_button_roles(holder)
    styled_app.processEvents()
    assert late.property("role") == ACTION and _main_colour(late) == "#0000ff"
    holder.close()
