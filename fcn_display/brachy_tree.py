"""
Catheter and dose reference point list of View > PLAN > Brachy (left of the table).

- Check boxes: show / hide a catheter or reference point on the images ('Visible' in
  its dict); the check box of "Catheters" / "Reference points" shows / hides all.
- Click: the table lists that catheter (its dwell positions or points) or the
  reference points.
- Double-click or right-click menu: go to it (the slices through it). The menu also
  shows only it, renames, duplicates or deletes it, and moves a reference point to the
  current position (where the slices shown intersect); these edits can be undone.
- Rename: click the name of the selected item again, F2 or the right-click menu. A
  catheter name is kept in 'CatheterName', a reference point name is its description.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QCheckBox, QMenu, QMessageBox, QTreeWidgetItem

from fcn_display.brachy_channel_edit import (_plan_channels, brachy_delete_catheter, brachy_duplicate_catheter,
                                             catheter_being_drawn, catheter_name, channel_visible, current_slice_position,
                                             go_to_point, plan_ref_points, push_undo, ref_point_name, ref_point_visible,
                                             ref_point_xyz, refresh_brachy_overlays)
from fcn_display.brachy_panel import catheter_table_mode, update_brachy_table_header


# Item data: kind ('catheters' / 'refs' for the two top items, 'catheter' / 'ref') and list index
KIND, INDEX = Qt.UserRole, Qt.UserRole + 1
GROUPS = ('catheters', 'refs')
NO_POSITION_COLOR = QColor("#9e9e9e")


def _check_state(checked):
    return Qt.Checked if checked else Qt.Unchecked


def _group_state(item):
    """Check state of a top item from its children: all, none or some of them shown."""
    states = [item.child(k).checkState(0) == Qt.Checked for k in range(item.childCount())]
    if states and all(states):
        return Qt.Checked
    return Qt.PartiallyChecked if any(states) else Qt.Unchecked


def _group_item(tree, kind):
    """Top item "Catheters" or "Reference points" (made on first use)."""
    for k in range(tree.topLevelItemCount()):
        if tree.topLevelItem(k).data(0, KIND) == kind:
            return tree.topLevelItem(k)
    item = QTreeWidgetItem()
    item.setData(0, KIND, kind)
    item.setData(0, INDEX, -1)
    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
    font = item.font(0)
    font.setBold(True)
    item.setFont(0, font)
    tree.insertTopLevelItem(GROUPS.index(kind) if kind == 'catheters' else tree.topLevelItemCount(), item)
    item.setExpanded(True)
    return item


def _fill_group(group, kind, rows):
    """Children of a top item from rows of (text, shown, tooltip, has a position)."""
    while group.childCount() > len(rows):
        group.removeChild(group.child(group.childCount() - 1))
    while group.childCount() < len(rows):
        child = QTreeWidgetItem(group)
        child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
    for k, (text, shown, tip, positioned) in enumerate(rows):
        child = group.child(k)
        child.setData(0, KIND, kind)
        child.setData(0, INDEX, k)
        child.setText(0, text)
        child.setToolTip(0, tip)
        child.setCheckState(0, _check_state(shown))
        child.setForeground(0, QBrush() if positioned else QBrush(NO_POSITION_COLOR))
    group.setCheckState(0, _group_state(group))


def _catheter_rows(channels):
    rows = []
    for k, ch in enumerate(channels):
        pts, dwells = ch.get('ChPos'), ch.get('DwellInfo')
        n_pts = len(pts) if hasattr(pts, '__len__') else 0
        n_dw = len(dwells) if hasattr(dwells, '__len__') else 0
        name = catheter_name(ch, k)
        number = "" if name == f"Catheter {k + 1}" else f" (catheter {k + 1})"
        rows.append((name, channel_visible(ch), f"{name}{number}: {n_pts} points, {n_dw} dwell positions", n_pts + n_dw > 0))
    return rows


def _ref_rows(refs):
    rows = []
    for k, pt in enumerate(refs):
        xyz, name = ref_point_xyz(pt), ref_point_name(pt, k)
        where = (f"({xyz[0]:.1f}, {xyz[1]:.1f}, {xyz[2]:.1f}) mm" if xyz is not None
                 else "no position (set it in the reference point table)")
        rows.append((name, ref_point_visible(pt), f"{name}: {where}", xyz is not None))
    return rows


def refresh_brachy_tree(self):
    """List the catheters and reference points of the loaded plan; mark what the table lists."""
    tree = getattr(self, 'brachy_tree', None)
    if tree is None:
        return
    plan_channels = _plan_channels(self)  # None without a brachy plan; empty for a new plan
    channels = plan_channels or []
    refs = plan_ref_points(self)
    tree.blockSignals(True)
    try:
        catheters = _group_item(tree, 'catheters')
        _fill_group(catheters, 'catheter', _catheter_rows(channels))
        catheters.setText(0, f"Catheters ({len(channels)})")
        catheters.setHidden(plan_channels is None)
        ref_group = _group_item(tree, 'refs')
        _fill_group(ref_group, 'ref', _ref_rows(refs))
        ref_group.setText(0, f"Reference points ({len(refs)})")
        ref_group.setHidden(not refs)
        # what the table lists: the selected catheter, or the reference points (and the selected one)
        if self.brachy_combobox_01.currentText() == "Ref. Points":
            row = self.brachy_table_01.currentRow()
            current = ref_group.child(row) if 0 <= row < ref_group.childCount() else ref_group
        else:
            k = self.brachy_spinBox_01.value() - 1
            current = catheters.child(k) if 0 <= k < catheters.childCount() else None
        if current is not None and not current.isHidden() and not (current.parent() or current).isHidden():
            tree.setCurrentItem(current)
        else:
            tree.selectionModel().clear()
    finally:
        tree.blockSignals(False)
    tree.updateGeometry()
    # the plan's name and whether it is saved (Plan box, data tree) and its Sk (Dose calculation
    # panel) follow the edits and their undo
    from fcn_display.brachy_plan_actions import update_brachy_plan_box
    from fcn_display.brachy_dose_calc import update_brachy_dose_panel
    update_brachy_plan_box(self)
    update_brachy_dose_panel(self)


def select_catheter(self, k):
    """List catheter k (0-based) in the table: its dwell positions or points."""
    channels = _plan_channels(self)
    if channels is None or not 0 <= k < len(channels):
        return
    drawn = catheter_being_drawn(self)
    if drawn is not None and channels[k] is not drawn:
        self.brachy_new_catheter_btn.setChecked(False)  # Stop adding points to the new catheter
    spin, combo = self.brachy_spinBox_01, self.brachy_combobox_01
    if combo.currentText() == "Ref. Points":
        spin.blockSignals(True)
        spin.setValue(k + 1)
        spin.blockSignals(False)
        combo.setCurrentText(catheter_table_mode(self))  # refreshes the table
    elif spin.value() != k + 1:
        spin.setValue(k + 1)  # refreshes the table


def select_ref_point(self, k):
    """List the reference points in the table and select point k (all of them if k < 0)."""
    combo = self.brachy_combobox_01
    if combo.currentText() != "Ref. Points":
        combo.setCurrentText("Ref. Points")  # refreshes the table
    if 0 <= k < len(plan_ref_points(self)):
        self.brachy_table_01.selectRow(k)
    refresh_brachy_tree(self)


def on_brachy_tree_current_changed(self, item):
    """Click (or arrow keys) in the list: the table lists the catheter / the reference points."""
    if item is None:
        return
    kind, k = item.data(0, KIND), item.data(0, INDEX)
    if kind == 'catheter':
        select_catheter(self, k)
    elif kind == 'catheters':
        if self.brachy_combobox_01.currentText() == "Ref. Points":
            self.brachy_combobox_01.setCurrentText(catheter_table_mode(self))
        else:
            refresh_brachy_tree(self)  # keep the selected catheter marked
    elif kind in ('ref', 'refs'):
        select_ref_point(self, k)


def _sync_ref_table_check_boxes(self):
    """The "Visible" check boxes of the reference point tables follow the list."""
    if self.brachy_combobox_01.currentText() != "Ref. Points":
        return
    refs = plan_ref_points(self)
    for name in ('brachy_table_01', 'brachy_table_02'):
        table = getattr(self, name, None)
        if table is None:
            continue
        for k, pt in enumerate(refs):
            cell = table.cellWidget(k, 9)
            box = cell.findChild(QCheckBox) if cell is not None else None
            if box is not None:
                box.blockSignals(True)
                box.setChecked(ref_point_visible(pt))
                box.blockSignals(False)


def _elements(self, kind):
    """The catheter or reference point dicts of a list item kind."""
    return (_plan_channels(self) or []) if kind in ('catheter', 'catheters') else plan_ref_points(self)


def rename_catheter(self, k, text):
    """New name of catheter k; empty (or its default "Catheter <k + 1>") goes back to the default name."""
    channels = _plan_channels(self) or []
    if not 0 <= k < len(channels):
        return
    name = text.strip()
    if name and name != f"Catheter {k + 1}":
        channels[k]['CatheterName'] = name
    else:
        channels[k].pop('CatheterName', None)
    update_brachy_table_header(self)  # title and list
    refresh_brachy_overlays(self)     # names on the images


def rename_ref_point(self, k, text):
    """New name (description) of reference point k, from the list or the table; empty keeps the old name."""
    refs = plan_ref_points(self)
    if not 0 <= k < len(refs):
        return
    name = text.strip()
    if name:
        refs[k]['DoseReferenceDescription'] = name
        for key in ('DoseReference Description', 'DoseReferenceDescription '):  # copies kept by the loaders
            if key in refs[k]:
                refs[k][key] = name
    if self.brachy_combobox_01.currentText() == "Ref. Points":
        for table_name in ('brachy_table_01', 'brachy_table_02'):  # Description column
            table = getattr(self, table_name, None)
            cell = table.item(k, 2) if table is not None else None
            if cell is not None:
                table.blockSignals(True)
                cell.setText(ref_point_name(refs[k], k))
                table.blockSignals(False)
    refresh_brachy_tree(self)
    refresh_brachy_overlays(self)


def on_brachy_tree_item_changed(self, item, column):
    """
    A check box was clicked: show / hide the catheter or reference point (on a top item:
    all of them); or an item was renamed.
    """
    if column != 0:
        return
    kind, k = item.data(0, KIND), item.data(0, INDEX)
    shown = item.checkState(0) == Qt.Checked
    elements = _elements(self, kind)
    if kind not in GROUPS:
        if not 0 <= k < len(elements):
            return
        if item.text(0) != (catheter_name if kind == 'catheter' else ref_point_name)(elements[k], k):
            (rename_catheter if kind == 'catheter' else rename_ref_point)(self, k, item.text(0))
            return
        if shown == (channel_visible if kind == 'catheter' else ref_point_visible)(elements[k]):
            return
    tree = self.brachy_tree
    tree.blockSignals(True)
    try:
        if kind in GROUPS:
            for child in range(item.childCount()):
                item.child(child).setCheckState(0, _check_state(shown))
            for element in elements:
                element['Visible'] = shown
        else:
            elements[k]['Visible'] = shown
            item.parent().setCheckState(0, _group_state(item.parent()))
    finally:
        tree.blockSignals(False)
    _sync_ref_table_check_boxes(self)
    refresh_brachy_overlays(self)


def show_only(self, kind, k):
    """Show only catheter / reference point k of its list (and switch its overlay on)."""
    for j, element in enumerate(_elements(self, kind)):
        element['Visible'] = j == k
    refresh_brachy_tree(self)
    _sync_ref_table_check_boxes(self)
    box = getattr(self, 'display_brachy_channel_overlay' if kind == 'catheter' else 'brachy_show_ref_points', None)
    if box is not None and not box.isChecked():
        box.setChecked(True)  # redraws
    else:
        refresh_brachy_overlays(self)


def go_to_item(self, kind, k):
    """Show the slices through a reference point or the first point (tip) of a catheter."""
    elements = _elements(self, kind)
    if not 0 <= k < len(elements):
        return False
    if kind == 'ref':
        return go_to_point(self, ref_point_xyz(elements[k]))
    pts, dwells = elements[k].get('ChPos'), elements[k].get('DwellInfo')
    if hasattr(pts, 'shape') and pts.ndim == 2 and len(pts):
        return go_to_point(self, pts[0, :3])
    if hasattr(dwells, 'shape') and dwells.ndim == 2 and len(dwells) and dwells.shape[1] >= 6:
        return go_to_point(self, dwells[0, 3:6])
    return False


def on_brachy_tree_double_clicked(self, item):
    """Double-click on a catheter / reference point: go to it."""
    kind = item.data(0, KIND)
    if kind in ('catheter', 'ref'):
        go_to_item(self, kind, item.data(0, INDEX))


def refresh_ref_points(self, select=None):
    """
    Reference point table (with its doses), list and overlays after the points changed,
    without asking for the RTDOSE again; 'select' is a row to select in the table.
    """
    from fcn_display.disp_plan_data import apply_alternating_row_colors, calculate_ref_points_dose, populate_brachy_table
    refs = plan_ref_points(self)
    if self.brachy_combobox_01.currentText() == "Ref. Points":
        populate_brachy_table(self, refs)
        if getattr(self, 'selected_rtdose_ref', None) is not None:
            calculate_ref_points_dose(self, self.selected_rtdose_ref)
        apply_alternating_row_colors(self)
        if select is not None and 0 <= select < len(refs):
            self.brachy_table_01.selectRow(select)
    update_brachy_table_header(self)  # title and list
    refresh_brachy_overlays(self)


def _push_ref_undo(self, refs):
    """Remember the reference points (before an edit) for undo."""
    channels = _plan_channels(self)
    if channels is not None:
        push_undo(self, channels, refs=refs)


def duplicate_ref_point(self, k):
    """Copy reference point k as a new point (next number, "<name> copy"), selected."""
    refs = plan_ref_points(self)
    if not 0 <= k < len(refs):
        return
    _push_ref_undo(self, refs)
    copy = {key: (list(val) if isinstance(val, list) else val) for key, val in refs[k].items()}
    numbers = []
    for pt in refs:
        try:
            numbers.append(int(pt.get('DoseReferenceNumber')))
        except (TypeError, ValueError):
            pass
    copy['DoseReferenceNumber'] = max(numbers, default=len(refs)) + 1
    name = f"{ref_point_name(refs[k], k)} copy"
    copy['DoseReferenceDescription'] = name
    for key in ('DoseReference Description', 'DoseReferenceDescription '):  # copies kept by the loaders
        if key in copy:
            copy[key] = name
    copy['Visible'] = True
    refs.append(copy)
    refresh_ref_points(self, select=len(refs) - 1)


def delete_ref_point(self, k):
    """Delete reference point k (undo brings it back)."""
    refs = plan_ref_points(self)
    if not 0 <= k < len(refs):
        return
    _push_ref_undo(self, refs)
    refs.pop(k)
    refresh_ref_points(self, select=min(k, len(refs) - 1))


def move_ref_point_to_slices(self, k):
    """Move reference point k to the current position: where the slices shown intersect (as "Get Plane")."""
    refs = plan_ref_points(self)
    if not 0 <= k < len(refs):
        return
    xyz = current_slice_position(self)
    if xyz is None:
        QMessageBox.warning(self, "Reference point", "No image loaded.")
        return
    _push_ref_undo(self, refs)
    refs[k]['DoseReferencePointCoordinates'] = [float(f"{v:.2f}") for v in xyz]
    refresh_ref_points(self, select=k)


def brachy_tree_context_menu(self, pos):
    """
    Right-click on a catheter / reference point: go to it, show only it, rename,
    duplicate or delete it; move a reference point to the current position.
    """
    tree = self.brachy_tree
    item = tree.itemAt(pos)
    if item is None or item.data(0, KIND) not in ('catheter', 'ref'):
        return
    kind, k = item.data(0, KIND), item.data(0, INDEX)
    catheter = kind == 'catheter'
    menu = QMenu(tree)
    menu.setToolTipsVisible(True)
    go = menu.addAction("Go to the tip" if catheter else "Go to the point")
    go.setEnabled(item.foreground(0).color() != NO_POSITION_COLOR)
    actions = {go: lambda: go_to_item(self, kind, k)}
    if not catheter:
        move = menu.addAction("Move to current position")
        move.setToolTip("Move the point to where the axial, coronal and sagittal slices shown intersect")
        actions[move] = lambda: move_ref_point_to_slices(self, k)
    actions[menu.addAction("Show only this catheter" if catheter else "Show only this point")] = lambda: show_only(self, kind, k)
    actions[menu.addAction("Rename")] = lambda: tree.editItem(item, 0)
    menu.addSeparator()
    duplicate = menu.addAction("Duplicate")
    delete = menu.addAction("Delete")
    if catheter:
        actions[duplicate] = lambda: (select_catheter(self, k), brachy_duplicate_catheter(self))
        actions[delete] = lambda: (select_catheter(self, k), brachy_delete_catheter(self))
    else:
        actions[duplicate] = lambda: duplicate_ref_point(self, k)
        actions[delete] = lambda: delete_ref_point(self, k)
    chosen = menu.exec(tree.viewport().mapToGlobal(pos))
    if chosen in actions:
        actions[chosen]()
