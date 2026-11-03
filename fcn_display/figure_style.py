"""
The Figures menu settings (fcn_init/create_menu.py) as matplotlib values, with their defaults, and the
figures redrawn when they change (create_menu.trigger_mix_graph_update calls the listeners).
"""

LINE_STYLES = {"solid": "-", "dashed": "--", "dotted": ":", "dash-dot": "-.", "none": "None"}
MARKERS = {"circle": "o", "square": "s", "triangle": "^", "star": "*", "none": "None"}


def figure_style(self):
    """The Figures menu settings with their defaults (line style "None": no line)."""
    return {"font": getattr(self, "selected_font_size", 14),
            "legend_font": getattr(self, "selected_legend_font_size", 14),
            "legend": getattr(self, "selected_legend_on_off", "On") == "On",
            "background": str(getattr(self, "selected_background", "Transparent")).lower(),
            "line_width": float(getattr(self, "selected_line_width", 2.0)),
            "line_color": str(getattr(self, "selected_line_color", "Red")).lower(),
            "line_style": LINE_STYLES.get(str(getattr(self, "selected_line_style", "Solid")).lower(), "-"),
            "marker": MARKERS.get(str(getattr(self, "selected_marker_type", "Circle")).lower(), "o"),
            "point_size": float(getattr(self, "selected_point_size", 8)),
            "point_color": str(getattr(self, "selected_point_color", "Blue")).lower()}


def add_figure_style_listener(self, key, func):
    """func() redraws a figure after any change in the Figures menu; one per key (set again: replaced)."""
    listeners = getattr(self, "_figure_style_listeners", None)
    if listeners is None:
        listeners = self._figure_style_listeners = {}
    listeners[key] = func
