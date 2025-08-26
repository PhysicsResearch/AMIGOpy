# init_reg_elements.py

from PyQt5.QtCore import Qt

def init_reg_elements(self):
    """
    Initialize registration UI elements:
      - Fill method/optimizer/metric/interpolator combo boxes
      - Set ranges for sliders/spinboxes (-1000..+1000; start at 0)
      - Link sliders <-> spinboxes
      - Wire all controls to self.display_update()
    """

    # ------------------------------------------------------------
    # Ensure display_update exists
    # ------------------------------------------------------------
    if not hasattr(self, "display_update") or not callable(getattr(self, "display_update")):
        def _stub():  # temporary no-op
            pass
        self.display_update = _stub

    # ------------------------------------------------------------
    # Helper: fill combo box with (text, key) pairs
    # ------------------------------------------------------------
    def _fill_combo(combo, items, default_index=0):
        combo.clear()
        for text, key in items:
            combo.addItem(text, key)
        combo.setCurrentIndex(default_index)
        # Any change triggers a display refresh
        combo.currentIndexChanged.connect(lambda _=None: self.display_update())

    # ------------------------------------------------------------
    # Helper: link a slider and a (double)spinbox
    # ------------------------------------------------------------
    def _link_slider_spin(slider, spin, vmin=-1000, vmax=1000, v0=0):
        # Slider setup
        slider.setMinimum(vmin)
        slider.setMaximum(vmax)
        slider.setSingleStep(1)
        slider.setPageStep(10)
        slider.setValue(v0)
        slider.setTracking(True)  # update while dragging

        # SpinBox setup (works for QSpinBox or QDoubleSpinBox)
        if hasattr(spin, "setDecimals"):
            spin.setDecimals(3)  # harmless if it's a QSpinBox (no-op)
        if hasattr(spin, "setSingleStep"):
            spin.setSingleStep(1)
        if hasattr(spin, "setRange"):
            spin.setRange(float(vmin), float(vmax))
        if hasattr(spin, "setValue"):
            spin.setValue(float(v0))

        # Two-way binding (avoid recursion via integer cast)
        slider.valueChanged.connect(spin.setValue)
        try:
            # QDoubleSpinBox: valueChanged(float); QSpinBox: valueChanged(int)
            spin.valueChanged.connect(lambda v: slider.setValue(int(v)))
        except TypeError:
            # In case of overloaded-signal ambiguity in some PyQt versions
            if hasattr(spin, "valueChanged[float]"):
                spin.valueChanged[float].connect(lambda v: slider.setValue(int(v)))
            else:
                spin.valueChanged[int].connect(lambda v: slider.setValue(v))

        # Also notify the viewer
        slider.valueChanged.connect(lambda _=None: self.display_update())
        spin.valueChanged.connect(lambda _=None: self.display_update())

    # ------------------------------------------------------------
    # Combo box options (rigid-only methods as requested)
    # ------------------------------------------------------------
    RIGID_METHODS = [
        ("Euler 3D (Rigid)", "euler3d"),
        ("Versor Rigid 3D",  "versor3d"),
    ]
    OPTIMIZERS = [
        ("Gradient Descent",           "gd"),
        ("Regular Step GradientDesc",  "rsgd"),
        ("LBFGSB",                     "lbfgsb"),
        ("Powell",                     "powell"),
        ("Amoeba (Nelder–Mead)",       "amoeba"),
        ("Exhaustive (grid search)",   "exhaustive"),
    ]
    METRICS = [
        ("Mattes Mutual Information", "mi"),
        ("Mean Squares",              "meansq"),
        ("Correlation",               "corr"),
    ]
    INTERPOLATORS = [
        ("Linear",            "linear"),
        ("Nearest Neighbor",  "nearest"),
        ("BSpline",           "bspline"),
    ]

    # ------------------------------------------------------------
    # Fill the specified combo boxes (skip target/moving as asked)
    # ------------------------------------------------------------
    # Some users spell 'optmizer' differently—support both just in case
    method_cb        = getattr(self, "Reg_method_box")
    optimizer_cb     = getattr(self, "Reg_optimizer_box", None) or getattr(self, "Reg_optimizer_box")
    metric_cb        = getattr(self, "Reg_Metric_box")
    interpolator_cb  = getattr(self, "Reg_interpolator_box")

    _fill_combo(method_cb,       RIGID_METHODS,  default_index=0)
    _fill_combo(optimizer_cb,    OPTIMIZERS,     default_index=0)
    _fill_combo(metric_cb,       METRICS,        default_index=0)
    _fill_combo(interpolator_cb, INTERPOLATORS,  default_index=0)

    # ------------------------------------------------------------
    # Link sliders & spinboxes (Translation / Rotation / Scale)
    # ------------------------------------------------------------
    # Translation
    _link_slider_spin(self.Reg_Trans01_Slider, self.Reg_Trans01_SpinBox)
    _link_slider_spin(self.Reg_Trans02_Slider, self.Reg_Trans02_SpinBox)
    _link_slider_spin(self.Reg_Trans03_Slider, self.Reg_Trans03_SpinBox)

    # Rotation
    _link_slider_spin(self.Reg_Rot01_Slider, self.Reg_Rot01_SpinBox)
    _link_slider_spin(self.Reg_Rot02_Slider, self.Reg_Rot02_SpinBox)
    _link_slider_spin(self.Reg_Rot03_Slider, self.Reg_Rot03_SpinBox)

    # Scale (you asked same range; you can tighten later if desired)
    _link_slider_spin(self.Reg_Scale01_Slider, self.Reg_Scale01_SpinBox)
    _link_slider_spin(self.Reg_Scale02_Slider, self.Reg_Scale02_SpinBox)
    _link_slider_spin(self.Reg_Scale03_Slider, self.Reg_Scale03_SpinBox)

    # Done — everything now calls display_update() on change.
