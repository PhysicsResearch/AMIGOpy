"""
One colour rule for the buttons of the whole interface (user request, Nov 2026):
- a button with a function: blue, white text ("Add" and "+" too);
- "Delete": red, black text ("Clear" is not: it also means uncheck all, or clear a plot);
- "Remove" (and "-"): black, white text;
- a button without a function yet (a placeholder): grey, qdarkstyle's own button.
A button's role comes from the button itself: its text, and whether something is connected to it
(clicked, toggled, pressed, released, a menu, or its button group). BUTTON_QSS colours the roles, on
top of the application style sheet. ButtonRoleStyle sets the role of every button when Qt polishes it
(also in dialogs and table rows made later); apply_button_roles sets them again where buttons are
connected after they were polished (module tabs that connect their buttons when first opened).
Not changed: icon buttons (tools, colour swatches with an icon), buttons with their own background
(colour swatches) and buttons with the customStyle property (e.g. the layer names).
"""
import re

from PySide6.QtCore import SIGNAL
from PySide6.QtWidgets import QApplication, QProxyStyle, QPushButton, QStyleFactory, QToolButton

ACTION, DELETE, REMOVE, PLACEHOLDER = "action", "delete", "remove", "placeholder"

BUTTON_QSS = """
QPushButton[role="action"], QToolButton[role="action"] { background-color: blue; color: white; }
QPushButton[role="action"]:hover, QToolButton[role="action"]:hover { background-color: #3d3dff; }
QPushButton[role="action"]:pressed, QToolButton[role="action"]:pressed { background-color: #0000b0; }
QPushButton[role="action"]:checked, QToolButton[role="action"]:checked { background-color: #259AE9; }
QPushButton[role="action"]:disabled, QToolButton[role="action"]:disabled { background-color: #26315e; color: #788D9C; }
QPushButton[role="delete"], QToolButton[role="delete"] { background-color: red; color: black; }
QPushButton[role="delete"]:hover, QToolButton[role="delete"]:hover { background-color: #ff5050; }
QPushButton[role="delete"]:pressed, QToolButton[role="delete"]:pressed { background-color: #b00000; }
QPushButton[role="delete"]:disabled, QToolButton[role="delete"]:disabled { background-color: #5e2626; color: #9b8585; }
QPushButton[role="remove"], QToolButton[role="remove"] {
    background-color: black; color: white; border: 1px solid #788D9C; padding: 1px; }
QPushButton[role="remove"]:hover, QToolButton[role="remove"]:hover { border-color: #DFE1E2; }
QPushButton[role="remove"]:pressed, QToolButton[role="remove"]:pressed { background-color: #2b2b2b; }
QPushButton[role="remove"]:disabled, QToolButton[role="remove"]:disabled { color: #788D9C; border-color: #455364; }
"""

_DELETE_TEXT = re.compile(r"(delete|del)\b", re.IGNORECASE)
_REMOVE_TEXT = re.compile(r"remove\b", re.IGNORECASE)
_MINUS = ("-", "−", "–")
_SIGNALS = ("clicked()", "clicked(bool)", "toggled(bool)")
# a QToolButton connects its own pressed / released inside Qt: they say nothing about a function
_PUSH_SIGNALS = _SIGNALS + ("pressed()", "released()")
_TOOL_SIGNALS = _SIGNALS + ("triggered(QAction*)",)
_GROUP_SIGNALS = ("buttonClicked(QAbstractButton*)", "idClicked(int)", "buttonToggled(QAbstractButton*,bool)",
                  "idToggled(int,bool)", "buttonPressed(QAbstractButton*)", "idPressed(int)",
                  "buttonReleased(QAbstractButton*)", "idReleased(int)")


def has_function(button):
    """Something is connected to the button: a slot, its menu or its default action, or its button group's slot."""
    tool = isinstance(button, QToolButton)
    if any(button.receivers(SIGNAL(s)) > 0 for s in (_TOOL_SIGNALS if tool else _PUSH_SIGNALS)):
        return True
    if button.menu() is not None or (tool and button.defaultAction() is not None):
        return True
    group = button.group()
    return group is not None and any(group.receivers(SIGNAL(s)) > 0 for s in _GROUP_SIGNALS)


def colour_by_role(button):
    """Text buttons without their own background or the customStyle property (icons and swatches keep their look)."""
    if isinstance(button, QToolButton):
        if not button.text() or not button.icon().isNull():
            return False
    elif not isinstance(button, QPushButton):
        return False
    return (not button.property("customStyle") and not button.objectName().startswith("qt_")
            and "background" not in button.styleSheet())


def button_role(button):
    """ACTION, DELETE, REMOVE or PLACEHOLDER (no function yet), from its text and connections."""
    if not has_function(button):
        return PLACEHOLDER
    text = button.text().replace("&&", "\0").replace("&", "").replace("\0", "&").strip(" .…:")
    if _DELETE_TEXT.match(text):
        return DELETE
    if _REMOVE_TEXT.match(text) or text in _MINUS:
        return REMOVE
    return ACTION


def set_button_role(button):
    """The button's role property as it is now (None when the colours are not ours); True if it changed."""
    role = button_role(button) if colour_by_role(button) else None
    if button.property("role") == role:
        return False
    button.setProperty("role", role)
    return True


def apply_button_roles(root):
    """Roles of all the buttons under root again (connected after they were polished), re-polished where changed."""
    for button in root.findChildren(QPushButton) + root.findChildren(QToolButton):
        if set_button_role(button):
            style = button.style()
            style.unpolish(button)
            style.polish(button)
            button.update()


class ButtonRoleStyle(QProxyStyle):
    """The application's style, setting the role of each button when it is polished (BUTTON_QSS colours it)."""

    def polish(self, arg):
        result = super().polish(arg)
        if isinstance(arg, (QPushButton, QToolButton)):
            set_button_role(arg)        # before the style sheet matches the rules of this polish
        return result


def install_button_style(app=None):
    """The button roles on every button of the application; call before setting its style sheet (+ BUTTON_QSS)."""
    app = app or QApplication.instance()
    base = QStyleFactory.create(app.style().name())
    app.setStyle(ButtonRoleStyle(base) if base is not None else ButtonRoleStyle())
    return app.style()
