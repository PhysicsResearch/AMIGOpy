"""
Table and overlay settings of View > PLAN > Brachy: the button switching the table
between dwell positions and catheter points, the title above the table and its
"Go to" buttons, the colors / sizes of the overlays (Style) and which overlays are
drawn (Display).
"""
import numpy as np
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton, QTableWidgetItem

from fcn_create_gui.brachy_widgets import color_swatch_icon
from fcn_display.brachy_channel_edit import (TOOL_BUTTONS, _checked, _plan_channels, _selected_channel, catheter_being_drawn,
                                             catheter_name, go_to_point, refresh_brachy_overlays, update_brachy_edit_buttons)


# Overlay style: colors (RGB 0-1) are changed with the color buttons, sizes come from the spin boxes
BRACHY_STYLE_DEFAULTS = {
    'ch_point': (0.0, 0.0, 1.0),        # catheter points
    'ch_line': (0.0, 0.0, 1.0),         # catheter path
    'ch_selected': (0.0, 0.85, 0.0),    # catheter selected in the list (points and path)
    'edit': (1.0, 1.0, 0.0),            # catheter being edited
    'edit_point': (1.0, 0.5, 0.0),      # selected / dragged point
    'dw_slice': (0.6, 1.0, 0.6),        # dwell in the current slice
    'dw_other': (0.0, 0.5, 0.0),        # dwell in another slice
    'dw_zero': (1.0, 0.0, 0.0),         # dwell with 0 s
    'ref_slice': (1.0, 0.6, 0.6),       # reference point in the current slice
    'ref_other': (1.0, 0.0, 0.0),       # reference point in another slice
    'ch_point_size': 3,                 # catheter point diameter (mm)
    'ch_line_width': 2,                 # catheter path width (px)
    'dw_size': 3.0,                     # dwell size (mm)
    'dw_edge_width': 2,                 # dwell outline width (px)
    'dw_fill': 15,                      # dwell fill opacity (%)
    'ref_size': 6.0,                    # reference point cross width (mm)
    'ref_width': 2,                     # reference point cross line width (px)
    'label_size': 12,                   # font size of the catheter numbers / point names (px)
}
COLOR_BUTTONS = (('ch_point', 'brachy_col_ch_point'), ('ch_line', 'brachy_col_ch_line'),
                 ('ch_selected', 'brachy_col_ch_selected'),
                 ('edit', 'brachy_col_edit'), ('edit_point', 'brachy_col_edit_point'),
                 ('dw_slice', 'brachy_col_dw_slice'), ('dw_other', 'brachy_col_dw_other'),
                 ('dw_zero', 'brachy_col_dw_zero'), ('ref_slice', 'brachy_col_ref_slice'),
                 ('ref_other', 'brachy_col_ref_other'))
SIZE_WIDGETS = (('ch_point_size', 'dw_ch_point_size'), ('ch_line_width', 'brachy_ov_line_width'),
                ('dw_size', 'brachy_ov_dw_size'), ('dw_edge_width', 'brachy_ov_dw_edge'),
                ('dw_fill', 'brachy_ov_dw_fill'), ('ref_size', 'brachy_ov_ref_size'),
                ('ref_width', 'brachy_ov_ref_width'), ('label_size', 'brachy_ov_label_size'))

# Display panel: (option, check box, the box of its group). The groups themselves are
# display_brachy_channel_overlay, display_dw_overlay and brachy_show_ref_points.
DISPLAY_OPTIONS = (('ch_points', 'brachy_show_ch_points', 'display_brachy_channel_overlay'),
                   ('ch_path', 'brachy_show_ch_path', 'display_brachy_channel_overlay'),
                   ('ch_labels', 'brachy_show_ch_labels', 'display_brachy_channel_overlay'),
                   ('dw_zero', 'brachy_show_dw_zero', 'display_dw_overlay'),
                   ('ref_labels', 'brachy_show_ref_labels', 'brachy_show_ref_points'))
DISPLAY_DEFAULTS = {'ch_points': True, 'ch_path': True, 'ch_labels': False, 'dw_zero': True, 'ref_labels': False}
# Display panel: (check box, part of the splitter) for the parts that can be hidden (the list always shows)
PANEL_BOXES = (('brachy_show_table_panel', 'brachy_table_panel'), ('brachy_show_edit_panel', 'brachy_edit_scroll'),
               ('brachy_show_dose_panel', 'brachy_dose_scroll'), ('brachy_show_style_panel', 'brachy_style_scroll'))
# Part that takes the spare width: the first one shown
SPARE_WIDTH_PARTS = ('brachy_style_scroll', 'brachy_dose_scroll', 'brachy_table_panel', 'brachy_edit_scroll', 'brachy_tree')

# Table modes (brachy_combobox_01 items) as shown on the mode button
MODE_BUTTON_TEXT = {"Dwells": "Dwells", "Channels": "Catheters", "Ref. Points": "Ref. points"}
# "Go" buttons of the table rows (as in the reference point table)
GO_BUTTON_STYLE = ("QPushButton { background-color: #1c5fa8; color: white; border: 1px solid #104277; margin: 1px;"
                   " padding: 2px 6px; border-radius: 3px; font-weight: bold; }"
                   " QPushButton:hover { background-color: #2475cf; }")


def brachy_style(self):
    """Current overlay colors and sizes (defaults where the style panel is missing)."""
    style = dict(BRACHY_STYLE_DEFAULTS)
    style.update(getattr(self, '_brachy_colors', None) or {})
    for key, attr in SIZE_WIDGETS:
        widget = getattr(self, attr, None)
        if widget is not None:
            style[key] = widget.value()
    return style


def catheter_colors(style, editing, selected):
    """(point color, path color) of a catheter being edited, selected in the list, or neither."""
    if editing:
        return style['edit'], style['edit']
    if selected:
        return style['ch_selected'], style['ch_selected']
    return style['ch_point'], style['ch_line']


def update_brachy_panels(self):
    """Show / hide the table, Edit, Dose and Style parts (Display check boxes); a shown part takes the spare width."""
    splitter = getattr(self, 'brachy_splitter', None)
    if splitter is None:
        return
    for box, part in PANEL_BOXES:
        getattr(self, part).setVisible(_checked(self, box))
    if not _checked(self, 'brachy_show_edit_panel'):
        # no edit tool or new catheter while their buttons are hidden
        if catheter_being_drawn(self) is not None:
            self.brachy_new_catheter_btn.setChecked(False)
        for _name, attr in TOOL_BUTTONS:
            getattr(self, attr).setChecked(False)
    spare = next(getattr(self, name) for name in SPARE_WIDTH_PARTS if not getattr(self, name).isHidden())
    for k in range(splitter.count()):
        splitter.setStretchFactor(k, 1 if splitter.widget(k) is spare else 0)


def brachy_display(self):
    """Which parts of the overlays are drawn: the Display options (defaults where they are missing)."""
    shown = dict(DISPLAY_DEFAULTS)
    for key, attr, _group in DISPLAY_OPTIONS:
        box = getattr(self, attr, None)
        if box is not None:
            shown[key] = box.isChecked()
    return shown


def update_brachy_display_options(self):
    """The options of a Display group (e.g. catheter points / path / numbers) need the group's box."""
    for _key, attr, group in DISPLAY_OPTIONS:
        box, group_box = getattr(self, attr, None), getattr(self, group, None)
        if box is not None and group_box is not None:
            box.setEnabled(group_box.isChecked())


def on_brachy_display_changed(self):
    """A Display check box (other than Catheters / Dwells, which redraw everything) was clicked."""
    update_brachy_display_options(self)
    refresh_brachy_overlays(self)


def update_brachy_color_buttons(self):
    style = brachy_style(self)
    for key, attr in COLOR_BUTTONS:
        btn = getattr(self, attr, None)
        if btn is not None:
            btn.setIcon(color_swatch_icon(style[key]))


def pick_brachy_color(self, key):
    """Color button: choose the color of one overlay element."""
    color = QColorDialog.getColor(QColor.fromRgbF(*brachy_style(self)[key]), self, "Select color")
    if not color.isValid():
        return
    colors = getattr(self, '_brachy_colors', None) or {}
    colors[key] = (color.redF(), color.greenF(), color.blueF())
    self._brachy_colors = colors
    update_brachy_color_buttons(self)
    refresh_brachy_overlays(self)


def toggle_brachy_table_mode(self):
    """Mode button: switch the table between dwell positions and catheter points."""
    combo = self.brachy_combobox_01
    combo.setCurrentText("Channels" if combo.currentText() == "Dwells" else "Dwells")


def set_brachy_table_mode(self, mode):
    """Mode button menu: "Dwells", "Channels" or "Ref. Points"."""
    self.brachy_combobox_01.setCurrentText(mode)


def catheter_table_mode(self):
    """Table mode for a catheter: the last one used of "Dwells" / "Channels"."""
    return getattr(self, '_brachy_catheter_mode', "Dwells")


def add_brachy_goto_column(self):
    """Last column of the dwell / catheter point table: a "Go" button per row (slices through the point)."""
    table = getattr(self, 'brachy_table_01', None)
    mode = self.brachy_combobox_01.currentText()
    if table is None or mode not in ("Dwells", "Channels"):
        return
    col = table.columnCount()
    table.setColumnCount(col + 1)
    table.setHorizontalHeaderItem(col, QTableWidgetItem("Go to"))
    tip = "Show the slices through this " + ("dwell position" if mode == "Dwells" else "catheter point")
    for row in range(table.rowCount()):
        btn = QPushButton("Go")
        btn.setStyleSheet(GO_BUTTON_STYLE)
        btn.setToolTip(tip)
        btn.clicked.connect(lambda _checked=False, r=row: go_to_table_row(self, r))
        table.setCellWidget(row, col, btn)


def go_to_table_row(self, row):
    """"Go" button of a dwell / catheter point row: select the row and show the slices through the point."""
    mode = self.brachy_combobox_01.currentText()
    ch = _selected_channel(self, _plan_channels(self))
    data = ch.get('DwellInfo' if mode == "Dwells" else 'ChPos') if ch is not None else None
    if not isinstance(data, np.ndarray) or data.ndim != 2 or not 0 <= row < len(data):
        return
    self.brachy_table_01.selectRow(row)
    go_to_point(self, data[row, 3:6] if mode == "Dwells" else data[row, :3])


def fit_brachy_table_part(self):
    """Give the table part of the splitter the width of the table columns, from / to the part with the spare width."""
    splitter = getattr(self, 'brachy_splitter', None)
    panel = getattr(self, 'brachy_table_panel', None)
    if splitter is None or panel is None or panel.isHidden():
        return
    sizes = splitter.sizes()
    if sum(sizes) <= 0:
        return  # not laid out yet: the splitter starts from the preferred widths
    spare = next(getattr(self, name) for name in SPARE_WIDTH_PARTS if not getattr(self, name).isHidden())
    if spare is panel:
        return  # the table part takes the spare width itself
    i, j = splitter.indexOf(panel), splitter.indexOf(spare)
    room = sizes[j] - spare.minimumSizeHint().width()
    delta = min(panel.sizeHint().width() - sizes[i], max(room, 0))
    if delta:
        sizes[i] += delta
        sizes[j] -= delta
        splitter.setSizes(sizes)


def _table_title(self, mode):
    rows = self.brachy_table_01.rowCount()
    if mode == "Ref. Points":
        return f"Dose reference points ({max(rows - 1, 0)})"  # the last row holds the ADD button
    try:
        channels = (self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan]
                    [self.series_index_plan]['metadata']['Plan_Brachy_Channels'])
    except (AttributeError, KeyError, IndexError, TypeError):
        return ""
    if not channels:
        return "No catheters yet: Edit > Catheter > New, then click on the images"
    idx = self.brachy_spinBox_01.value()
    what = "dwell positions" if mode == "Dwells" else "points"
    name = catheter_name(channels[idx - 1], idx - 1) if 0 < idx <= len(channels) else f"Catheter {idx}"
    if name == f"Catheter {idx}":
        title = f"Catheter {idx} of {len(channels)}: {rows} {what}"
    else:
        title = f"{name} ({idx} of {len(channels)}): {rows} {what}"
    drawn = catheter_being_drawn(self)
    if drawn is not None and 0 < idx <= len(channels) and channels[idx - 1] is drawn:
        title += " - click on the images to add points, Stop when done"
    return title


def update_brachy_table_header(self):
    """
    Mode button text and title for what the table lists, the catheter list, the width
    of the table part (when the columns changed) and the edit buttons.
    """
    combo = getattr(self, 'brachy_combobox_01', None)
    table = getattr(self, 'brachy_table_01', None)
    if combo is None or table is None:
        return
    mode = combo.currentText()
    if mode in ("Dwells", "Channels"):
        self._brachy_catheter_mode = mode
    btn = getattr(self, 'brachy_mode_btn', None)
    if btn is not None:
        btn.setText(MODE_BUTTON_TEXT.get(mode, mode))
    title = getattr(self, 'brachy_table_title', None)
    if title is not None:
        title.setText(_table_title(self, mode))
    table.updateGeometry()  # its preferred width follows the columns
    columns = (mode, table.columnCount())
    if getattr(self, '_brachy_fitted_columns', None) != columns:
        self._brachy_fitted_columns = columns
        fit_brachy_table_part(self)
    from fcn_display.brachy_tree import refresh_brachy_tree
    refresh_brachy_tree(self)
    update_brachy_edit_buttons(self)
