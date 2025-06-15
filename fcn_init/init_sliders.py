from fcn_3Dview.Prepare_data_3D_vtk import _apply_threshold


def initialize_3Dsliders(self, low: float, high: float, n_steps: int = 100):
    """
    Prepare the two sliders + two spin-boxes for a new dataset.

    Args:
        low  : real minimum scalar in the volume
        high : real maximum scalar in the volume
        n_steps: slider tick count (granularity). 100 → ≈1 % steps
    """
    # -----------------------------------------------------------------------
    # dataset-dependent constants
    # -----------------------------------------------------------------------
    self.slider3D_LOW        = float(low)
    self.slider3D_HIGH       = float(high)
    self.slider3D_SPAN       = self.slider3D_HIGH - self.slider3D_LOW
    self.slider3D_RESOLUTION = int(n_steps)       # 100 keeps your old feel
    if self.slider3D_SPAN == 0:                   # flat image, avoid /0
        self.slider3D_SPAN = 1e-6

    # helpers – slider<->value conversions
    self._s_to_v = lambda s: self.slider3D_LOW +               \
                             (s / self.slider3D_RESOLUTION) *  \
                             self.slider3D_SPAN
    self._v_to_s = lambda v: int(round((v - self.slider3D_LOW) /
                                       self.slider3D_SPAN *
                                       self.slider3D_RESOLUTION))

    # -----------------------------------------------------------------------
    # configure widgets
    # -----------------------------------------------------------------------
    for slider in (self.View3D_Threshold_slider_01,
                   self.View3D_Threshold_slider_02):
        slider.setRange(0, self.slider3D_RESOLUTION)

    for spin in (self.View3D_Threshold_spin_01,
                 self.View3D_Threshold_spin_02):
        spin.setRange(self.slider3D_LOW, self.slider3D_HIGH)
        spin.setDecimals(3)                          # or 0 if HU integers
        spin.setSingleStep(self.slider3D_SPAN /
                           self.slider3D_RESOLUTION)

    # -----------------------------------------------------------------------
    # initial values (full window)
    # -----------------------------------------------------------------------
    self.View3D_Threshold_slider_01.setValue(0)
    self.View3D_Threshold_slider_02.setValue(self.slider3D_RESOLUTION)
    self.View3D_Threshold_spin_01.setValue(self.slider3D_LOW)
    self.View3D_Threshold_spin_02.setValue(self.slider3D_HIGH)

    # -----------------------------------------------------------------------
    # signal / slot wiring –- unchanged names
    # -----------------------------------------------------------------------
    self.View3D_Threshold_slider_01.valueChanged.connect(
        lambda s: _from_slider(self, 1, s))
    self.View3D_Threshold_slider_02.valueChanged.connect(
        lambda s: _from_slider(self, 2, s))
    self.View3D_Threshold_spin_01.valueChanged.connect(
        lambda v: _from_spin(self, 1, v))
    self.View3D_Threshold_spin_02.valueChanged.connect(
        lambda v: _from_spin(self, 2, v))
    
def _from_slider(self, idx: int, sval: int) -> None:
    """Slider → spin-box, enforcing min ≤ max."""
    v = self._s_to_v(sval)
    if idx == 1:
        if v > self.View3D_Threshold_spin_02.value():
            v = self.View3D_Threshold_spin_02.value()
            sval = self._v_to_s(v)
            self.View3D_Threshold_slider_01.blockSignals(True)
            self.View3D_Threshold_slider_01.setValue(sval)
            self.View3D_Threshold_slider_01.blockSignals(False)
        self.View3D_Threshold_spin_01.setValue(v)
    else:
        if v < self.View3D_Threshold_spin_01.value():
            v = self.View3D_Threshold_spin_01.value()
            sval = self._v_to_s(v)
            self.View3D_Threshold_slider_02.blockSignals(True)
            self.View3D_Threshold_slider_02.setValue(sval)
            self.View3D_Threshold_slider_02.blockSignals(False)
        self.View3D_Threshold_spin_02.setValue(v)

    # refresh the transfer functions
    self._apply_threshold(self.View3D_Threshold_spin_01.value(),
                          self.View3D_Threshold_spin_02.value())


def _from_spin(self, idx: int, v: float) -> None:
    """Spin-box → slider, enforcing min ≤ max."""
    sval = self._v_to_s(v)
    if idx == 1:
        if v > self.View3D_Threshold_spin_02.value():
            v = self.View3D_Threshold_spin_02.value()
            sval = self._v_to_s(v)
            self.View3D_Threshold_spin_01.blockSignals(True)
            self.View3D_Threshold_spin_01.setValue(v)
            self.View3D_Threshold_spin_01.blockSignals(False)
        self.View3D_Threshold_slider_01.setValue(sval)
    else:
        if v < self.View3D_Threshold_spin_01.value():
            v = self.View3D_Threshold_spin_01.value()
            sval = self._v_to_s(v)
            self.View3D_Threshold_spin_02.blockSignals(True)
            self.View3D_Threshold_spin_02.setValue(v)
            self.View3D_Threshold_spin_02.blockSignals(False)
        self.View3D_Threshold_slider_02.setValue(sval)

    # refresh the transfer functions
    _apply_threshold(self,self.View3D_Threshold_spin_01.value(),
                          self.View3D_Threshold_spin_02.value())