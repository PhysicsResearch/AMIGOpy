from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QCheckBox, QSpinBox, QColorDialog, QDoubleSpinBox
from PyQt5.QtGui import QColor
import numpy as np
from math import floor, ceil
import functools
import random

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

    # Retrieve the lines for each spot in the beam (L(t) = P + t * v)
    v_vector = points - source_point
    lines = [(source_point, direction) for direction in v_vector]
    random_points = np.random.choice(len(lines), size=50, replace=False)
    lines_visual = []
    data_spots = []
    distances = np.arange(-200, 200.05, .05)

    #for idx in range(len(lines)):
    for idx in random_points:
        spots = []
        P,v = lines[idx]
        loc = P + 1.1 * v
        if idx == random_points[1]:
            lines_visual.append([P,loc])
        spot = P + 1 * v
        for dist in distances:
            weight = (dist + 1850)/1850
            spots.append((dist, P + weight * v))
        data_spots.append((idx,spots))
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

    if point_size == 5:
        import matplotlib.pyplot as plt
        # Normalized dose tuples
        dose_characteristics_per_spot = {}
        for individual_spot in data_spots:
            spot_idx, spot_information = individual_spot
            # Retrieve the dose matrix and the dose voxel spacing
            dose_img = self.display_3D_data[1]
            dose_voxel_spacing=(
                self.pixel_spacing3Dview[1,0],
                self.pixel_spacing3Dview[1,1],
                self.slice_thickness3Dview[1]
            )
            # Dose offset is needed for correct location of the sampled points
            dose_offset = self.Im_Offset3Dview[1]
            # Generate an empty image that can be used as validation
            val_img = np.zeros((dose_img.shape))
            # Retrieve the dose
            dose_distance = []

            # Retrieve each sampled point per proton spot
            for spot in spot_information:
                # Distance from the proton spot
                distance = spot[0]
                # Translate the spot coordinates with the PatientPosition coordinates
                spot = spot[1] - self.Im_PatPosition3Dview[0]
                # Translate the coordinates to image space by using the voxel spacing of the dose matrix, but also the offset of the dose matrix
                voxel_spot = [(spot[i] - dose_offset[i]) / dose_voxel_spacing[i] for i in range(3)]
                # Round the voxel_spot for the 3x3x3 block
                x_c, y_c, z_c = [int(round(v)) for v in voxel_spot]
                if z_c < 0 or z_c > val_img.shape[0]-1 or y_c < 0 or y_c > val_img.shape[1]-1 or x_c < 0 or x_c > val_img.shape[2]-1:
                    dose_distance.append((distance, 0))
                else:
                    z_min = max(z_c - 1, 0)
                    z_max = min(z_c + 2, val_img.shape[0])
                    y_min = max(y_c - 1, 0)
                    y_max = min(y_c + 2, val_img.shape[1])
                    x_min = max(x_c - 1, 0)
                    x_max = min(x_c + 2, val_img.shape[2])

                    # Weight the dose based on inverse distance
                    weights = []
                    doses = []

                    dose_weights = np.flip(dose_img,axis=1)
                    for zz in range(z_min, z_max):
                        for yy in range(y_min, y_max):
                            for xx in range(x_min, x_max):
                                dist_voxels = np.sqrt(
                                    (voxel_spot[0] - xx)**2 +
                                    (voxel_spot[1] - yy)**2 +
                                    (voxel_spot[2] - zz)**2
                                )
                                sigma = 0.5  # in voxels or mm
                                weight = np.exp(-(dist_voxels**2) / (2*sigma**2))
                                weights.append(weight)
                                #weights.append(1 / (dist_voxels + 1e-6))  # avoid division by zero
                                doses.append(dose_weights[zz, yy, xx])
                    
                    weights = np.array(weights)
                    doses = np.array(doses)
                    mean_dose = np.sum(doses * weights) / np.sum(weights)
                    dose_distance.append((distance, mean_dose))
                    val_img[z_c, y_c, x_c] = 1

            validate = False
            if validate:
                # To get correct, the y-axis has to be flipped
                val_img=np.flip(val_img, axis=1)
                # Plot the voxel spot as binary image on axis two
                self.display_numpy_volume(
                    val_img,
                    voxel_spacing= dose_voxel_spacing,
                    layer_idx=2,
                    offset=dose_offset
                )

            dose_distance = np.array(dose_distance)  # shape (N, 2)
            # Sort by distance for clean plotting
            dose_distance = dose_distance[dose_distance[:, 0].argsort()]
            # Extract distance and dose
            distances = (dose_distance[:, 0] + 200)/10
            doses = dose_distance[:, 1]

            # Normalize doses
            max_dose = np.max(doses)
            doses_normalized = doses / max_dose

            # Find the last dose at 0.8
            # Reverse the dataset
            rev_doses = doses_normalized[::-1]
            # look first for the index closest to 0.79 and 0.81
            indexes = np.where((rev_doses >= 0.79) & (rev_doses <= 0.81))[0]
            # take the first index and look 2% of the total dataset further for the closest 0.8
            start_idx = indexes[0]
            window_size = int(0.02 * len(rev_doses))
            end_idx = min(start_idx + window_size, len(rev_doses))
            window_values = rev_doses[start_idx:end_idx]
            local_idx = np.argmin(np.abs(window_values - 0.8))
            # Refer it back to the original index
            idx_rev = start_idx + local_idx
            idx_original = len(doses_normalized) - 1 - idx_rev

            dose_characteristics_per_spot[str(spot_idx)] = {
                "dose_distance": distances,
                "dose_per_distance": doses_normalized,
                "R80_index": idx_original,
                "R80_distance": distances[idx_original],
                "R80_dose": doses_normalized[idx_original]
            }
        
        del distances
        del doses_normalized
        del idx_original

        spots_indexes = list(dose_characteristics_per_spot)
        random_indexes = random.sample(spots_indexes, 6)
        # Create figure with a name
        fig_protons, ax_proton = plt.subplots(figsize=(6, 4), num="Proton Dose vs Distance")
        cmap = plt.cm.viridis
        info_to_display = []
        # Loop over the different spots
        for i, spot_idx in enumerate(random_indexes):
            distances_of_dose = dose_characteristics_per_spot[spot_idx]['dose_distance']
            doses_per_distance = dose_characteristics_per_spot[spot_idx]['dose_per_distance']
            R80_distance = dose_characteristics_per_spot[spot_idx]['R80_distance']
            R80_dose = dose_characteristics_per_spot[spot_idx]['R80_dose']

            # Plot
            color = cmap(i/len(random_indexes))
            ax_proton.plot(distances_of_dose, doses_per_distance,
                    marker=None,
                    linestyle='-', color=color, linewidth=2, alpha = 0.5)

            # Plot the marker
            ax_proton.plot(R80_distance, R80_dose, marker = 'o', color = 'black')

            info_to_display.append((spot_idx, R80_distance, color))
        
        # After the loop, plot the collected labels in the top right corner
        x_pos = 0.98  # Relative position near top right (axes coords)
        y_start = 0.95
        y_step = 0.05

        for i, (spot_idx, dose_val, color) in enumerate(info_to_display):
            y_pos = y_start - i * y_step
            ax_proton.text(x_pos, y_pos,
                        f"{spot_idx}, {dose_val:.4f}",
                        color=color,
                        fontsize=9,
                        ha='right',
                        va='center',
                        transform=ax_proton.transAxes)  # Use axes coordinates

        # Labels and formatting
        ax_proton.set_xlabel("Distance (cm)")
        ax_proton.set_ylabel("Normalized Dose")
        ax_proton.grid(True)
        ax_proton.set_ylim(0, 1.05)

        plt.show(block=True)

        fig_boxplot, ax_boxplot = plt.subplots(figsize=(6, 4), num="R80 boxplot")        
        # Loop over the different spots
        R80_distances = {}
        for ix in range(3):
            R80_info = []
            for i, spot_idx in enumerate(spots_indexes):
                R80_distance = dose_characteristics_per_spot[spot_idx]['R80_distance']
                R80_dose = dose_characteristics_per_spot[spot_idx]['R80_dose']
                R80_info.append(R80_distance)
            R80_distances[str(ix)] = {"data": R80_info}
        
        # Prepare the data and labels
        boxplot_data = [R80_distances[key]["data"] for key in R80_distances]
        labels = list(R80_distances.keys())

        # Define the colors for each box
        colors = ['lightgreen', 'plum', 'lightsalmon']  # matches light green, light purple, light orange

        # Create the boxplot
        bp = ax_boxplot.boxplot(
            boxplot_data,
            labels=labels,
            patch_artist=True,  # allows color fill
            medianprops=dict(color="black", linewidth=2)  # median line
        )

        # Apply custom colors
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)

        # Labels and title
        ax_boxplot.set_ylabel("Distance (mm)")
        ax_boxplot.set_title("R80 Distance Distribution")
        ax_boxplot.set_ylim(0, 40)
        ax_boxplot.grid(True, linestyle="--", alpha=0.6)
        plt.show(block=True)


    # -- Only display if visible! --
    beam_trajectory_name = beam_name + '_trajectory'
    chk = self._3D_proton_table.cellWidget(row, 1)
    is_visible = chk.isChecked()
    self.remove_3d_proton_spots(beam_name)
    self.remove_3d_proton_beam(beam_trajectory_name)
    if is_visible and points.shape[0] > 0:
        self.add_3d_proton_spots(points, iso_shift, color=rgb, size=point_size, name=beam_name)
        self.add_3d_proton_beam_trajectory(source_point, corners, lines_visual, color=rgb, size=1, name=beam_trajectory_name)
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
