from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
import numpy as np

# Angular Y-axis modes that need phase-unwrapping
_ANGULAR_MODES = {"Gantry Angle", "Collimator Angle", "Couch Angle"}

# Map menu strings to matplotlib equivalents
_LINE_STYLE_MAP = {
    "solid": "-",
    "dashed": "--",
    "dotted": ":",
    "dash-dot": "-.",
    "none": "None",
}
_MARKER_MAP = {
    "circle": "o",
    "square": "s",
    "triangle": "^",
    "star": "*",
    "none": "None",
}

def init_ebrt_canvas(w):
    """
    Initialize the matplotlib canvas for the EBRT tab.
    """
    if hasattr(w, 'ebrt_canvas'):
        return

    bg = "#19232D" if getattr(w, 'current_theme', 'dark') == 'dark' else "white"
    
    w.ebrt_figure = Figure(facecolor=bg)
    w.ebrt_ax = w.ebrt_figure.add_subplot(111)
    w.ebrt_ax.set_facecolor(bg)
    
    w.ebrt_canvas = FigureCanvas(w.ebrt_figure)
    w.ebrt_toolbar = NavigationToolbar(w.ebrt_canvas, w)
    
    w.ebrt_plot_layout.addWidget(w.ebrt_toolbar)
    w.ebrt_plot_layout.addWidget(w.ebrt_canvas)
    
    # Hook into the menu's trigger_mix_graph_update so figure settings refresh this plot
    _prev = getattr(w, 'update_mix_graph_func', None)
    def _chained_update():
        if _prev:
            try:
                _prev()
            except Exception:
                pass
        update_ebrt_plot(w)
    w.update_mix_graph_func = _chained_update


def update_ebrt_plot(w):
    """
    Update the plot based on user selections and Figures menu settings.
    
    Polar mode:  theta = Gantry Angle (always), radius = Y-axis selection.
    Cartesian:   X = X-axis dropdown, Y = Y-axis dropdown.
    """
    if not hasattr(w, 'current_ebrt_plan_data'):
        return
        
    init_ebrt_canvas(w)
    
    # ---- Read Figures menu settings ----
    font_size       = getattr(w, 'selected_font_size', 14)
    legend_font     = getattr(w, 'selected_legend_font_size', 14)
    legend_on       = getattr(w, 'selected_legend_on_off', 'On') == 'On'
    line_width      = getattr(w, 'selected_line_width', 2.0)
    line_color      = getattr(w, 'selected_line_color', 'Red').lower()
    line_style_key  = getattr(w, 'selected_line_style', 'Solid').lower()
    marker_key      = getattr(w, 'selected_marker_type', 'Circle').lower()
    point_size      = getattr(w, 'selected_point_size', 8)
    point_color     = getattr(w, 'selected_point_color', 'Blue').lower()
    bg_setting      = getattr(w, 'selected_background', 'Transparent').lower()
    
    ls  = _LINE_STYLE_MAP.get(line_style_key, '-')
    mkr = _MARKER_MAP.get(marker_key, 'o')
    
    # Theme colors
    is_dark = getattr(w, 'current_theme', 'dark') == 'dark'
    if bg_setting == 'transparent':
        bg    = (0, 0, 0, 0)
        ax_bg = (0, 0, 0, 0)
    elif bg_setting == 'white':
        bg    = 'white'
        ax_bg = 'white'
    else:
        bg    = "#19232D" if is_dark else "white"
        ax_bg = "#1e2936" if is_dark else "white"
    text_color  = "white" if is_dark else "black"
    spine_color = "white" if is_dark else "black"
    
    # Combo / polar state
    x_axis_mode = w.ebrt_x_combo.currentText()
    y_axis_mode = w.ebrt_y_combo.currentText()
    is_polar = hasattr(w, 'ebrt_polar_check') and w.ebrt_polar_check.isChecked()
    
    # Recreate axes if projection type changed
    current_is_polar = getattr(w, '_current_plot_is_polar', None)
    if is_polar != current_is_polar:
        w.ebrt_figure.clf()
        if is_polar:
            w.ebrt_ax = w.ebrt_figure.add_subplot(111, projection='polar')
        else:
            w.ebrt_ax = w.ebrt_figure.add_subplot(111)
        w._current_plot_is_polar = is_polar
        if hasattr(w, 'ebrt_toolbar'):
            w.ebrt_toolbar.update()
            
    # Apply theme
    w.ebrt_figure.patch.set_facecolor(bg)
    w.ebrt_ax.set_facecolor(ax_bg)
    w.ebrt_ax.clear()
    
    if is_polar:
        w.ebrt_ax.set_theta_zero_location("N")
        w.ebrt_ax.set_theta_direction(-1)
    
    # Selected beams and their colors
    selected_beams = []
    beam_colors = {}
    
    if hasattr(w, 'ebrt_tree'):
        root = w.ebrt_tree.topLevelItem(0)
        if root:
            for i in range(root.childCount()):
                child = root.child(i)
                if "Beam " in child.text(0) and child.checkState(2) == Qt.Checked:
                    try:
                        # Extract beam number from "Beam X: Name"
                        b_num_str = child.text(0).split(':')[0].replace("Beam ", "").strip()
                        b_num = int(b_num_str)
                        selected_beams.append(b_num)
                        
                        btn = w.ebrt_tree.itemWidget(child, 3)
                        if btn:
                            beam_colors[b_num] = btn.property("beam_color")
                    except Exception:
                        pass
        
    if not selected_beams:
        w.ebrt_ax.text(0.5, 0.5, "Please select a beam", color=text_color,
                       fontsize=font_size, ha='center', va='center',
                       transform=w.ebrt_ax.transAxes)
        w.ebrt_canvas.draw()
        return

    plan_data = w.current_ebrt_plan_data
    has_data = False
    
    for beam in plan_data['Beams']:
        b_num = beam['BeamNumber']
        if b_num not in selected_beams:
            continue
        
        # Use the specific color assigned to this beam in the tree widget
        c = beam_colors.get(b_num, line_color)
        this_line_color  = c
        this_point_color = c
        
        beam_label = f"Beam {b_num}: {beam['BeamName']}"
        
        cumulative_time = 0.0
        cumulative_mu = 0.0
        
        if is_polar:
            theta_data = []
            r_data = []
            for i, cp in enumerate(beam['ControlPoints']):
                if i > 0 and cp['Time_per_CP'] != 'N/A':
                    cumulative_time += float(cp['Time_per_CP'])
                if i > 0 and cp['MU_per_CP'] != 'N/A':
                    cumulative_mu += float(cp['MU_per_CP'])
                if cp['GantryAngle'] == 'N/A':
                    continue
                r_val = _get_y_value(cp, y_axis_mode, cumulative_time, cumulative_mu)
                if r_val is None:
                    continue
                theta_data.append(np.radians(float(cp['GantryAngle'])))
                r_data.append(r_val)
                
            if theta_data and r_data:
                has_data = True
                w.ebrt_ax.plot(theta_data, r_data,
                               color=this_line_color, linewidth=line_width,
                               linestyle=ls,
                               marker=mkr, markersize=point_size,
                               markerfacecolor=this_point_color,
                               markeredgecolor=this_point_color,
                               label=beam_label)
        elif x_axis_mode == "Beam":
            y_val = None
            if y_axis_mode == "Beam Dose":
                y_val = float(beam.get('BeamDose', 0)) if beam.get('BeamDose', 'N/A') != 'N/A' else None
            elif y_axis_mode == "Beam Meterset":
                y_val = float(beam.get('BeamMeterset', 0)) if beam.get('BeamMeterset', 'N/A') != 'N/A' else None
            elif y_axis_mode == "Number of Control Points":
                y_val = int(beam.get('NumberofControlPoints', 0))
            elif y_axis_mode == "Total Time":
                y_val = 0.0
                for cp in beam['ControlPoints']:
                    if cp.get('Time_per_CP', 'N/A') != 'N/A':
                        y_val += float(cp['Time_per_CP'])
                        
            if y_val is not None:
                has_data = True
                w.ebrt_ax.bar(beam_label, y_val, color=this_line_color, label=beam_label)
        else:
            x_data = []
            y_data = []
            for i, cp in enumerate(beam['ControlPoints']):
                if i > 0 and cp['Time_per_CP'] != 'N/A':
                    cumulative_time += float(cp['Time_per_CP'])
                if i > 0 and cp['MU_per_CP'] != 'N/A':
                    cumulative_mu += float(cp['MU_per_CP'])
                x_val = _get_x_value(cp, x_axis_mode, i, cumulative_time, cumulative_mu)
                y_val = _get_y_value(cp, y_axis_mode, cumulative_time, cumulative_mu)
                if x_val is not None and y_val is not None:
                    x_data.append(x_val)
                    y_data.append(y_val)
                    
            if x_data and y_data:
                has_data = True
                if x_axis_mode in _ANGULAR_MODES:
                    x_data = list(np.degrees(np.unwrap(np.radians(x_data))))
                if y_axis_mode in _ANGULAR_MODES:
                    y_data = list(np.degrees(np.unwrap(np.radians(y_data))))
                w.ebrt_ax.plot(x_data, y_data,
                               color=this_line_color, linewidth=line_width,
                               linestyle=ls,
                               marker=mkr, markersize=point_size,
                               markerfacecolor=this_point_color,
                               markeredgecolor=this_point_color,
                               label=beam_label)
            
    # ---- Axis styling ----
    if has_data:
        if is_polar:
            w.ebrt_ax.set_thetagrids(range(0, 360, 15))
            w.ebrt_ax.tick_params(axis='both', colors=text_color, labelsize=font_size)
            w.ebrt_ax.set_rlabel_position(45)
        else:
            w.ebrt_ax.set_xlabel(x_axis_mode, color=text_color, fontsize=font_size)
            w.ebrt_ax.set_ylabel(y_axis_mode, color=text_color, fontsize=font_size)
            w.ebrt_ax.tick_params(axis='x', colors=text_color, labelsize=font_size)
            w.ebrt_ax.tick_params(axis='y', colors=text_color, labelsize=font_size)
            for sp in w.ebrt_ax.spines.values():
                sp.set_color(spine_color)
            
        if legend_on:
            legend = w.ebrt_ax.legend(loc='upper right', fontsize=legend_font)
            if legend:
                legend.get_frame().set_facecolor(
                    "#19232D" if is_dark else "white")
                legend.get_frame().set_edgecolor(spine_color)
                for txt in legend.get_texts():
                    txt.set_color(text_color)
    else:
        w.ebrt_ax.text(0.5, 0.5, "No valid data for selected axes", color=text_color,
                       fontsize=font_size, ha='center', va='center',
                       transform=w.ebrt_ax.transAxes)

    w.ebrt_figure.tight_layout()
    w.ebrt_canvas.draw()


def _get_x_value(cp, mode, index, cumulative_time, cumulative_mu):
    """Return the X value for a control point based on the selected mode."""
    if mode == "CP Index":
        return index
    elif mode == "Time Cumulative":
        return cumulative_time
    elif mode == "Cumulative MU":
        return cumulative_mu
    elif mode == "Gantry Angle" and cp['GantryAngle'] != 'N/A':
        return float(cp['GantryAngle'])
    elif mode == "Collimator Angle" and cp['BeamLimitingDeviceAngle'] != 'N/A':
        return float(cp['BeamLimitingDeviceAngle'])
    elif mode == "Couch Angle" and cp['PatientSupportAngle'] != 'N/A':
        return float(cp['PatientSupportAngle'])
    return None


def _get_y_value(cp, mode, cumulative_time, cumulative_mu):
    """Return the Y (or radial) value for a control point based on the selected mode."""
    if mode == "Gantry Angle" and cp['GantryAngle'] != 'N/A':
        return float(cp['GantryAngle'])
    elif mode == "Collimator Angle" and cp['BeamLimitingDeviceAngle'] != 'N/A':
        return float(cp['BeamLimitingDeviceAngle'])
    elif mode == "Couch Angle" and cp['PatientSupportAngle'] != 'N/A':
        return float(cp['PatientSupportAngle'])
    elif mode == "MU per CP" and cp['MU_per_CP'] != 'N/A':
        return float(cp['MU_per_CP'])
    elif mode == "Cumulative MU":
        return cumulative_mu
    elif mode == "Time per CP" and cp['Time_per_CP'] != 'N/A':
        return float(cp['Time_per_CP'])
    elif mode == "Time Cumulative":
        return cumulative_time
    elif mode == "Dose Rate" and cp['DoseRateSet'] != 'N/A':
        return float(cp['DoseRateSet'])
    return None
