from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QCheckBox, QSpinBox, QColorDialog, QDoubleSpinBox
from PyQt5.QtGui import QColor
import numpy as np
from math import floor, ceil

def init_3D_proton_table(self):
    self._proton_spot_data = {}
    self._3D_proton_table.setColumnCount(6)
    self._3D_proton_table.setHorizontalHeaderLabels([
        "Beam Name", "Visible", "Point Size", "E Min (MeV)", "E Max (MeV)", "Point Color"
    ])
    self._3D_proton_table.setEditTriggers(self._3D_proton_table.NoEditTriggers)
    self._3D_proton_table.setSelectionBehavior(self._3D_proton_table.SelectRows)

def add_beam_to_proton_table(self, beam_name, info_df, visible=False, point_size=3, point_color=(1,0,0)):
    row = self._3D_proton_table.rowCount()
    self._3D_proton_table.insertRow(row)

    # 1. Beam Name (read-only)
    item = QTableWidgetItem(beam_name)
    item.setData(Qt.UserRole, beam_name)
    self._3D_proton_table.setItem(row, 0, item)

    # 2. Visible checkbox (unchecked by default)
    chk = QCheckBox()
    chk.setChecked(visible)
    chk.stateChanged.connect(
        lambda state, n=beam_name, info=info_df, c=point_color, s=point_size:
        toggle_beam_visibility(self, n, info, state, c, s)
    )
    self._3D_proton_table.setCellWidget(row, 1, chk)

    # 3. Point size spinbox
    spin = QSpinBox()
    spin.setRange(1, 20)
    spin.setValue(point_size)
    spin.valueChanged.connect(
        lambda val, n=beam_name: update_beam_point_size(self, n, val)
    )
    self._3D_proton_table.setCellWidget(row, 2, spin)

    # 4. Energy Min spinbox
    min_energy = floor(info_df['Energy'].min())
    max_energy = ceil(info_df['Energy'].max())
    spin_min = QSpinBox()
    spin_min.setRange(min_energy, max_energy)
    spin_min.setValue(min_energy)
    spin_min.valueChanged.connect(
        lambda val, n=beam_name: update_beam_energy_range(self, n)
    )
    self._3D_proton_table.setCellWidget(row, 3, spin_min)

    # 5. Energy Max spinbox
    spin_max = QSpinBox()
    spin_max.setRange(min_energy, max_energy)
    spin_max.setValue(max_energy)
    spin_max.valueChanged.connect(
        lambda val, n=beam_name: update_beam_energy_range(self, n)
    )
    self._3D_proton_table.setCellWidget(row, 4, spin_max)

    # 6. Color button
    btn = QPushButton()
    btn.setStyleSheet(f"background-color: rgb({int(point_color[0]*255)}, {int(point_color[1]*255)}, {int(point_color[2]*255)});")
    btn.clicked.connect(
        lambda _, n=beam_name: pick_beam_color(self, n)
    )
    self._3D_proton_table.setCellWidget(row, 5, btn)

def toggle_beam_visibility(self, beam_name, info_df, state, color, size):
    row = find_row_by_beam_name(self, beam_name)
    if row is None:
        return

    # Get current energy min/max from the spinboxes
    spin_min = self._3D_proton_table.cellWidget(row, 3)
    spin_max = self._3D_proton_table.cellWidget(row, 4)
    min_energy = spin_min.value()
    max_energy = spin_max.value()

    if state == Qt.Checked:
        # Filter by energy
        energy = info_df['Energy'].values
        mask = (energy >= min_energy) & (energy <= max_energy)
        x = info_df['x_spot'].values[mask]
        y = info_df['y_spot'].values[mask]
        z = np.zeros_like(x)
        points = np.vstack([x, y, z]).T
        self._proton_spot_data[beam_name] = points
        self.add_3d_proton_spots(points, color=color, size=size, name=beam_name)
    else:
        self.remove_3d_proton_spots(beam_name)
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_beam_point_size(self, beam_name, value):
    # Update the cross size for the spot actors
    if hasattr(self, '_proton_spots') and beam_name in self._proton_spots:
        # Remove and re-add the actor to update size (cross length)
        actor = self._proton_spots[beam_name]
        self.VTK3D_renderer.RemoveActor(actor)
        # You need the original points/color to redraw with new size
        points = self._proton_spot_data[beam_name]
        color = actor.GetProperty().GetColor()
        self.add_3d_proton_spots(points, color=color, size=value, name=beam_name)
        self.VTK3D_interactor.GetRenderWindow().Render()

def pick_beam_color(self, beam_name):
    color = QColorDialog.getColor()
    if color.isValid():
        rgb = (color.red()/255, color.green()/255, color.blue()/255)
        # Update the table color button
        row = find_row_by_beam_name(self, beam_name)
        if row is not None:
            self._3D_proton_table.cellWidget(row, 5).setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});"
            )
        # Update actor color in 3D view
        if hasattr(self, '_proton_spots') and beam_name in self._proton_spots:
            actor = self._proton_spots[beam_name]
            actor.GetProperty().SetColor(rgb)
            self.VTK3D_interactor.GetRenderWindow().Render()



def update_beam_energy_range(self, beam_name):
    # Find the table row
    row = find_row_by_beam_name(self,beam_name)
    if row is None:
        return

    # Retrieve min/max energy values from spinboxes
    spin_min = self._3D_proton_table.cellWidget(row, 3)
    spin_max = self._3D_proton_table.cellWidget(row, 4)
    min_energy = spin_min.value()
    max_energy = spin_max.value()

    # Retrieve Info DataFrame for this beam
    info_df = self._beam_info_dfs[beam_name] if hasattr(self, "_beam_info_dfs") else None
    if info_df is None:
        return

    # Check visibility
    chk = self._3D_proton_table.cellWidget(row, 1)
    is_visible = chk.isChecked()

    # Remove existing spot actor
    self.remove_3d_proton_spots(beam_name)

    if is_visible:
        # Filter by new energy range
        energy = info_df['Energy'].values
        mask = (energy >= min_energy) & (energy <= max_energy)
        x = info_df['x_spot'].values[mask]
        y = info_df['y_spot'].values[mask]
        z = np.zeros_like(x)
        points = np.vstack([x, y, z]).T
        self._proton_spot_data[beam_name] = points

        # Get latest point size
        spin_size = self._3D_proton_table.cellWidget(row, 2)
        point_size = spin_size.value()

        # Extract RGB color from the button's styleSheet (assumes 'background-color: rgb(R, G, B);')
        btn_color = self._3D_proton_table.cellWidget(row, 5)
        style = btn_color.styleSheet()
        import re
        m = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', style)
        if m:
            rgb = tuple(int(x)/255. for x in m.groups())
        else:
            rgb = (1, 0, 0)  # fallback: red

        self.add_3d_proton_spots(points, color=rgb, size=point_size, name=beam_name)

    self.VTK3D_interactor.GetRenderWindow().Render()

def find_row_by_beam_name(self, beam_name):
    """Return the row index of the given beam_name, or None if not found."""
    for row in range(self._3D_proton_table.rowCount()):
        item = self._3D_proton_table.item(row, 0)  # assuming name is in column 0
        if item and item.data(Qt.UserRole) == beam_name:
            return row
    return None