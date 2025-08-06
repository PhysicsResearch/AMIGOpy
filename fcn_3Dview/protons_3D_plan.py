from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QCheckBox, QSpinBox, QColorDialog, QDoubleSpinBox
from PyQt5.QtGui import QColor
import numpy as np
from math import floor, ceil
import functools

def init_3D_proton_table(self):
    self._proton_spot_data = {}
    self._3D_proton_table.setColumnCount(12)
    self._3D_proton_table.setHorizontalHeaderLabels([
        "Beam Name", "Visible", "Point Size",
        "E Min (MeV)", "E Max (MeV)",
        "Gantry (°)", "Couch (°)",
        "Iso X", "Iso Y", "Iso Z",
        "Reset", "Point Color"
    ])
    self._3D_proton_table.setEditTriggers(self._3D_proton_table.NoEditTriggers)
    self._3D_proton_table.setSelectionBehavior(self._3D_proton_table.SelectRows)

def add_beam_to_proton_table(self, beam_name, info_df, isocenter_off, visible=False, point_size=3, point_color=(1,0,0)):
    row = self._3D_proton_table.rowCount()
    self._3D_proton_table.insertRow(row)

    # Store original data for later reset and transforms
    orig_points = np.vstack([
        info_df['x_spot'].values,
        info_df['y_spot'].values,
        np.zeros_like(info_df['x_spot'].values)
    ]).T

    # -- translate and rotate the beam orientation to patient space --  
    ref_point = np.array([0, 0, 0])
    source_location = np.array([0,0,-1850])

    # Find corners of the spots
    orig_points_corners = orig_points[:,0:2]
    min_x, min_y = orig_points_corners.min(axis=0)
    max_x, max_y = orig_points_corners.max(axis=0)
    ip_corners = np.array([[min_x, min_y, 0], [min_x, max_y, 0], [max_x, min_y, 0], [max_x, max_y, 0]])

    # rotate 90 degress in x-axis
    theta = np.deg2rad(90)
    c, s = np.cos(theta), np.sin(theta)
    rot_x = np.array([[1, 0, 0],
            [0, c, -s],
            [0, s, c]])
    source_location = (source_location - ref_point) @ rot_x.T + ref_point
    ip_points = (orig_points - ref_point) @ rot_x.T + ref_point
    ip_corners = (ip_corners - ref_point) @ rot_x.T + ref_point
    
    # Rotate 270 degrees in y-axis
    theta = np.deg2rad(270)
    c, s = np.cos(theta), np.sin(theta)
    rot_y = np.array([[c, 0, s],
            [0, 1, 0],
            [-s, 0, c]])
    source_location = (source_location - ref_point) @ rot_y.T + ref_point
    ip_points = (ip_points - ref_point) @ rot_y.T + ref_point
    ip_corners = (ip_corners - ref_point) @ rot_y.T + ref_point

    # rotate 180 degrees in z-axis
    theta = np.deg2rad(180)
    c, s = np.cos(theta), np.sin(theta)
    rot_z = np.array([[c, -s, 0],
            [s,  c, 0],
            [0,  0, 1]])
    source_location = (source_location - ref_point) @ rot_z.T + ref_point
    ip_points = (ip_points - ref_point) @ rot_z.T + ref_point
    ip_corners = (ip_corners - ref_point) @ rot_z.T + ref_point

    self._proton_spot_data[beam_name] = {
        "original_points": orig_points,
        "info_df": info_df,
        "isocenter": isocenter_off,
        "inplane_points" : ip_points,
        "source_location": source_location,
        "inplane_corners": ip_corners
    }

    item = QTableWidgetItem(beam_name)
    item.setData(Qt.UserRole, beam_name)
    self._3D_proton_table.setItem(row, 0, item)

    chk = QCheckBox()
    chk.setChecked(visible)
    chk.stateChanged.connect(functools.partial(update_beam_transform_and_display, self, beam_name))
    self._3D_proton_table.setCellWidget(row, 1, chk)

    spin = QSpinBox()
    spin.setRange(1, 20)
    spin.setValue(point_size)
    spin.valueChanged.connect(functools.partial(update_beam_transform_and_display, self, beam_name))
    self._3D_proton_table.setCellWidget(row, 2, spin)

    min_energy = floor(info_df['Energy'].min())
    max_energy = ceil(info_df['Energy'].max())
    spin_min = QSpinBox()
    spin_min.setRange(min_energy, max_energy)
    spin_min.setValue(min_energy)
    spin_min.valueChanged.connect(functools.partial(update_beam_transform_and_display, self, beam_name))
    self._3D_proton_table.setCellWidget(row, 3, spin_min)

    spin_max = QSpinBox()
    spin_max.setRange(min_energy, max_energy)
    spin_max.setValue(max_energy)
    spin_max.valueChanged.connect(functools.partial(update_beam_transform_and_display, self, beam_name))
    self._3D_proton_table.setCellWidget(row, 4, spin_max)

    gantry_default = float(info_df['gantry_ang'].iloc[0])
    gantry_spin = QDoubleSpinBox()
    gantry_spin.setRange(0, 360)
    gantry_spin.setDecimals(1)
    gantry_spin.setValue(gantry_default)
    gantry_spin.valueChanged.connect(functools.partial(update_beam_transform_and_display, self, beam_name))
    self._3D_proton_table.setCellWidget(row, 5, gantry_spin)

    couch_default = float(info_df['couch_ang'].iloc[0])
    couch_spin = QDoubleSpinBox()
    couch_spin.setRange(0, 360)
    couch_spin.setDecimals(1)
    couch_spin.setValue(couch_default)
    couch_spin.valueChanged.connect(functools.partial(update_beam_transform_and_display, self, beam_name))
    self._3D_proton_table.setCellWidget(row, 6, couch_spin)

    # Isocenter X, Y, Z
    iso_x = float(isocenter_off[0])
    iso_y = float(isocenter_off[1])
    iso_z = float(isocenter_off[2])
    for i, val in enumerate([iso_x, iso_y, iso_z]):
        iso_spin = QDoubleSpinBox()
        iso_spin.setDecimals(2)
        iso_spin.setRange(-1000, 1000)
        iso_spin.setValue(val)
        iso_spin.valueChanged.connect(functools.partial(update_beam_transform_and_display, self, beam_name))
        self._3D_proton_table.setCellWidget(row, 7+i, iso_spin)

    btn_reset = QPushButton("Reset")
    btn_reset.clicked.connect(functools.partial(reset_beam_transforms, self, beam_name))
    self._3D_proton_table.setCellWidget(row, 10, btn_reset)

    btn = QPushButton()
    btn.setStyleSheet(f"background-color: rgb({int(point_color[0]*255)}, {int(point_color[1]*255)}, {int(point_color[2]*255)});")
    btn.clicked.connect(functools.partial(pick_beam_color, self, beam_name))
    self._3D_proton_table.setCellWidget(row, 11, btn)

def update_beam_transform_and_display(self, beam_name, *args):
    """
    Applies energy filter, gantry/couch rotations, and isocenter translation in sequence,
    then replots the proton spots. Call this after ANY parameter change.
    """
    row = find_row_by_beam_name(self,beam_name)
    data = self._proton_spot_data[beam_name]
    info_df = data['info_df']
    orig_points = data['inplane_points']
    corners = data['inplane_corners']
    source_point = data['source_location']

    # -- Energy filter --
    spin_min = self._3D_proton_table.cellWidget(row, 3)
    spin_max = self._3D_proton_table.cellWidget(row, 4)
    min_energy = spin_min.value()
    max_energy = spin_max.value()
    energy = info_df['Energy'].values
    mask = (energy >= min_energy) & (energy <= max_energy)
    points = orig_points[mask, :]

    # -- Isocenter translation --
    iso_x = self._3D_proton_table.cellWidget(row, 7).value()
    iso_y = self._3D_proton_table.cellWidget(row, 8).value()
    iso_z = self._3D_proton_table.cellWidget(row, 9).value()
    iso_shift = np.array([iso_x, iso_y, iso_z])
    points = points + iso_shift
    source_point = source_point + iso_shift
    corners = corners + iso_shift

    # Gantry (around y axis):
    gantry_angle = self._3D_proton_table.cellWidget(row, 5).value()
    if gantry_angle != 0:
        theta = np.deg2rad(gantry_angle)
        c, s = np.cos(theta), np.sin(theta)
        rot_z = np.array([
            [c, -s, 0],
            [s,  c, 0],
            [0,  0, 1]
        ])
        points = (points - iso_shift) @ rot_z.T + iso_shift
        source_point = (source_point - iso_shift) @ rot_z.T + iso_shift
        corners = (corners - iso_shift) @ rot_z.T + iso_shift

    # Couch (around x axis):
    couch_angle = self._3D_proton_table.cellWidget(row, 6).value()
    if couch_angle != 0:
        theta = np.deg2rad(couch_angle)
        c, s = np.cos(theta), np.sin(theta)
        rot_y = np.array([
            [c, 0, s],
            [0, 1, 0],
            [-s, 0, c]
        ])
        points = (points - iso_shift) @ rot_y.T + iso_shift
        source_point = (source_point - iso_shift) @ rot_y.T + iso_shift
        corners = (corners - iso_shift) @ rot_y.T + iso_shift

    # -- Color & Size --
    spin_size = self._3D_proton_table.cellWidget(row, 2)
    point_size = spin_size.value()
    btn_color = self._3D_proton_table.cellWidget(row, 11)
    import re
    style = btn_color.styleSheet()
    m = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', style)
    if m:
        rgb = tuple(int(x)/255. for x in m.groups())
    else:
        rgb = (1, 0, 0)

    # -- Only display if visible! --
    beam_trajectory_name = beam_name + '_trajectory'
    chk = self._3D_proton_table.cellWidget(row, 1)
    is_visible = chk.isChecked()
    self.remove_3d_proton_spots(beam_name)
    self.remove_3d_proton_beam(beam_trajectory_name)
    if is_visible and points.shape[0] > 0:
        self.add_3d_proton_spots(points, iso_shift, color=rgb, size=point_size, name=beam_name)
        self.add_3d_proton_beam_trajectory(source_point, corners, color=rgb, size=1, name=beam_trajectory_name)
    self.VTK3D_interactor.GetRenderWindow().Render()


def pick_beam_color(self, beam_name):
    color = QColorDialog.getColor()
    if color.isValid():
        rgb = (color.red()/255, color.green()/255, color.blue()/255)
        # Update the table color button
        row = find_row_by_beam_name(self,beam_name)
        if row is not None:
            self._3D_proton_table.cellWidget(row, 11).setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});"
            )
        # Re-apply plot with new color
        update_beam_transform_and_display(self, beam_name)

def reset_beam_transforms(self, beam_name):
    """
    Reset all beam parameters (gantry, couch, isocenter) to original values.
    """
    row = find_row_by_beam_name(self, beam_name)
    info_df = self._proton_spot_data[beam_name]['info_df']
    # Reset isocenter
    iso = self._proton_spot_data[beam_name]['isocenter']
    self._3D_proton_table.cellWidget(row, 7).setValue(float(iso[0]))
    self._3D_proton_table.cellWidget(row, 8).setValue(float(iso[1]))
    self._3D_proton_table.cellWidget(row, 9).setValue(float(iso[2]))
    # Reset gantry/couch
    self._3D_proton_table.cellWidget(row, 5).setValue(float(info_df['gantry_ang'].iloc[0]))
    self._3D_proton_table.cellWidget(row, 6).setValue(float(info_df['couch_ang'].iloc[0]))
    # Also reset energy to original min/max
    min_energy = floor(info_df['Energy'].min())
    max_energy = ceil(info_df['Energy'].max())
    self._3D_proton_table.cellWidget(row, 3).setValue(min_energy)
    self._3D_proton_table.cellWidget(row, 4).setValue(max_energy)
    # Reset point size to 3 (optional)
    self._3D_proton_table.cellWidget(row, 2).setValue(3)
    # Replot with all default values
    update_beam_transform_and_display(self, beam_name)

def find_row_by_beam_name(self, beam_name):
    """Return the row index of the given beam_name, or None if not found."""
    for row in range(self._3D_proton_table.rowCount()):
        item = self._3D_proton_table.item(row, 0)
        if item and item.data(Qt.UserRole) == beam_name:
            return row
    return None
