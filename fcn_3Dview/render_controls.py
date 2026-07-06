import vtk
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QDoubleSpinBox, QPushButton, QComboBox, QSlider, QWidget, QHBoxLayout

def init_3D_render_controls(self):
    # Enable all controls in the Render panel
    self.View3D_quality_slider.setEnabled(True)
    self.View3D_quality_spin_01.setEnabled(True)
    self.View3D_brightness_slider.setEnabled(True)
    self.View3D_brightness_spin_01.setEnabled(True)
    self.View3D_specular_slider.setEnabled(True)
    self.View3D_specular_spin_01.setEnabled(True)
    self.View3D_render_options.setEnabled(True)
    self.iew3D_lighting_options.setEnabled(True)
    self.View3D_shading_checkBox.setEnabled(True)
    self.View3D_shoiw_axes_checkBox.setEnabled(True)
    self.View3D_annotation_checkBox.setEnabled(True)

    # Set initial ranges and defaults
    self.View3D_quality_slider.setRange(0, 100)
    self.View3D_quality_slider.setValue(50)
    self.View3D_quality_spin_01.setRange(0.0, 1.0)
    self.View3D_quality_spin_01.setSingleStep(0.05)
    self.View3D_quality_spin_01.setValue(0.50)
    
    self.View3D_brightness_slider.setRange(-100, 100)
    self.View3D_brightness_slider.setValue(0)
    self.View3D_brightness_spin_01.setRange(-1.0, 1.0)
    self.View3D_brightness_spin_01.setSingleStep(0.05)
    self.View3D_brightness_spin_01.setValue(0.00)
    
    self.View3D_specular_slider.setRange(0, 100)
    self.View3D_specular_slider.setValue(0)
    self.View3D_specular_spin_01.setRange(0.0, 100.0)
    self.View3D_specular_spin_01.setSingleStep(1.0)
    self.View3D_specular_spin_01.setValue(0.00)
    
    self.View3D_render_options.clear()
    self.View3D_render_options.addItems(["Composite", "MIP", "MinIP"])
    
    self.iew3D_lighting_options.clear()
    self.iew3D_lighting_options.addItems(["Headlight", "Camera Light", "Scene Light"])
    
    # Internal flag to prevent infinite loops during synchronization
    self._updating_render_controls = False
    
    def on_quality_slider(val):
        if getattr(self, '_updating_render_controls', False):
            return
        self._updating_render_controls = True
        self.View3D_quality_spin_01.setValue(val / 100.0)
        self._updating_render_controls = False
        apply_3d_quality(self)

    def on_quality_spin(val):
        if getattr(self, '_updating_render_controls', False):
            return
        self._updating_render_controls = True
        self.View3D_quality_slider.setValue(int(val * 100))
        self._updating_render_controls = False
        apply_3d_quality(self)

    def on_brightness_slider(val):
        if getattr(self, '_updating_render_controls', False):
            return
        self._updating_render_controls = True
        self.View3D_brightness_spin_01.setValue(val / 100.0)
        self._updating_render_controls = False
        apply_3d_brightness(self)

    def on_brightness_spin(val):
        if getattr(self, '_updating_render_controls', False):
            return
        self._updating_render_controls = True
        self.View3D_brightness_slider.setValue(int(val * 100))
        self._updating_render_controls = False
        apply_3d_brightness(self)

    def on_specular_slider(val):
        if getattr(self, '_updating_render_controls', False):
            return
        self._updating_render_controls = True
        self.View3D_specular_spin_01.setValue(val)
        self._updating_render_controls = False
        apply_3d_specular(self)

    def on_specular_spin(val):
        if getattr(self, '_updating_render_controls', False):
            return
        self._updating_render_controls = True
        self.View3D_specular_slider.setValue(int(val))
        self._updating_render_controls = False
        apply_3d_specular(self)
        
    self.View3D_quality_slider.valueChanged.connect(on_quality_slider)
    self.View3D_quality_spin_01.valueChanged.connect(on_quality_spin)
    
    self.View3D_brightness_slider.valueChanged.connect(on_brightness_slider)
    self.View3D_brightness_spin_01.valueChanged.connect(on_brightness_spin)
    
    self.View3D_specular_slider.valueChanged.connect(on_specular_slider)
    self.View3D_specular_spin_01.valueChanged.connect(on_specular_spin)
    
    # Connect Comboboxes
    self.View3D_render_options.currentTextChanged.connect(lambda _: apply_3d_render_mode(self))
    self.iew3D_lighting_options.currentTextChanged.connect(lambda _: apply_3d_lighting(self))
    
    # Connect CheckBoxes
    self.View3D_shading_checkBox.stateChanged.connect(lambda _: apply_3d_shading(self))
    self.View3D_shoiw_axes_checkBox.stateChanged.connect(lambda _: apply_3d_axes_visibility(self))
    self.View3D_annotation_checkBox.stateChanged.connect(lambda _: apply_3d_annotation_visibility(self))
    
    # Connect Reset Camera and Clear All Buttons
    self.View3D_reset_camera.clicked.connect(self.reset_3d_camera)
    self.View3D_clear_all.clicked.connect(self.clear_3d_axes)
    
    self._render_controls_initialized = True


def apply_3d_quality(self):
    if not hasattr(self, '_volumes'):
        return
    quality_val = self.View3D_quality_spin_01.value()
    # quality_val range: 0.0 (low quality, spacing = 3.0mm) to 1.0 (high quality, spacing = 0.1mm)
    sample_distance = 3.0 - 2.9 * quality_val
    for vol in self._volumes.values():
        mapper = vol.GetMapper()
        mapper.SetAutoAdjustSampleDistances(0)
        mapper.SetSampleDistance(sample_distance)
    if hasattr(self, 'VTK3D_interactor') and self.VTK3D_interactor:
        self.VTK3D_interactor.GetRenderWindow().Render()


def apply_3d_brightness(self):
    if not hasattr(self, '_vol_props'):
        return
    brightness_val = self.View3D_brightness_spin_01.value()
    # Ambient: default 0.1. Range: 0.0 to 0.9.
    ambient_val = 0.1 + 0.8 * brightness_val if brightness_val >= 0 else 0.1 * (1.0 + brightness_val)
    # Diffuse: default 0.7. Range: 0.2 to 1.0.
    diffuse_val = 0.7 - 0.5 * brightness_val if brightness_val >= 0 else 0.7 + 0.3 * brightness_val
    
    for volp in self._vol_props.values():
        volp.SetAmbient(ambient_val)
        volp.SetDiffuse(diffuse_val)
    if hasattr(self, 'VTK3D_interactor') and self.VTK3D_interactor:
        self.VTK3D_interactor.GetRenderWindow().Render()


def apply_3d_specular(self):
    if not hasattr(self, '_vol_props'):
        return
    specular_power_val = self.View3D_specular_spin_01.value()
    for volp in self._vol_props.values():
        if specular_power_val > 0:
            volp.SetSpecular(0.5)
            volp.SetSpecularPower(specular_power_val)
        else:
            volp.SetSpecular(0.0)
    if hasattr(self, 'VTK3D_interactor') and self.VTK3D_interactor:
        self.VTK3D_interactor.GetRenderWindow().Render()


def apply_3d_render_mode(self):
    if not hasattr(self, '_volumes'):
        return
    mode = self.View3D_render_options.currentText()
    for vol in self._volumes.values():
        mapper = vol.GetMapper()
        if mode == "MIP":
            mapper.SetBlendModeToMaximumIntensity()
        elif mode == "MinIP":
            mapper.SetBlendModeToMinimumIntensity()
        else:
            mapper.SetBlendModeToComposite()
    if hasattr(self, 'VTK3D_interactor') and self.VTK3D_interactor:
        self.VTK3D_interactor.GetRenderWindow().Render()


def apply_3d_lighting(self):
    if not hasattr(self, 'VTK3D_renderer'):
        return
    light_mode = self.iew3D_lighting_options.currentText()
    
    if not hasattr(self, '_3d_custom_light'):
        self._3d_custom_light = vtk.vtkLight()
        self.VTK3D_renderer.AddLight(self._3d_custom_light)
        
    light = self._3d_custom_light
    if light_mode == "Headlight":
        light.SetLightTypeToHeadlight()
    elif light_mode == "Camera Light":
        light.SetLightTypeToCameraLight()
    else:  # Scene Light
        light.SetLightTypeToSceneLight()
        light.SetPosition(100.0, 100.0, 150.0)
        
    if hasattr(self, 'VTK3D_interactor') and self.VTK3D_interactor:
        self.VTK3D_interactor.GetRenderWindow().Render()


def apply_3d_shading(self):
    if not hasattr(self, '_vol_props'):
        return
    shading_on = self.View3D_shading_checkBox.isChecked()
    for volp in self._vol_props.values():
        if shading_on:
            volp.ShadeOn()
        else:
            volp.ShadeOff()
    if hasattr(self, 'VTK3D_interactor') and self.VTK3D_interactor:
        self.VTK3D_interactor.GetRenderWindow().Render()


def apply_3d_axes_visibility(self):
    if not hasattr(self, 'VTK3D_interactor'):
        return
    show_axes = self.View3D_shoiw_axes_checkBox.isChecked()
    if show_axes:
        if not hasattr(self, '_3d_axes_widget'):
            axes_actor = vtk.vtkAxesActor()
            axes_widget = vtk.vtkOrientationMarkerWidget()
            axes_widget.SetOrientationMarker(axes_actor)
            axes_widget.SetInteractor(self.VTK3D_interactor)
            axes_widget.InteractiveOff()
            self._3d_axes_widget = axes_widget
        self._3d_axes_widget.SetEnabled(1)
    else:
        if hasattr(self, '_3d_axes_widget'):
            self._3d_axes_widget.SetEnabled(0)
    if hasattr(self, 'VTK3D_interactor') and self.VTK3D_interactor:
        self.VTK3D_interactor.GetRenderWindow().Render()


def apply_3d_annotation_visibility(self):
    if not hasattr(self, 'VTK3D_renderer'):
        return
    show_annot = self.View3D_annotation_checkBox.isChecked()
    if show_annot:
        if not hasattr(self, '_3d_annotation_actor'):
            txt = vtk.vtkTextActor()
            txt.SetInput("AMIGOpy 3D Viewport\nShading: Auto\nBlending: Composite")
            txt.GetTextProperty().SetFontSize(14)
            txt.GetTextProperty().SetFontFamilyToArial()
            txt.GetTextProperty().BoldOn()
            txt.GetTextProperty().SetColor(0.8, 0.8, 1.0)
            txt.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
            txt.GetPositionCoordinate().SetValue(0.02, 0.92)
            self._3d_annotation_actor = txt
        self.VTK3D_renderer.AddActor(self._3d_annotation_actor)
    else:
        if hasattr(self, '_3d_annotation_actor'):
            self.VTK3D_renderer.RemoveActor(self._3d_annotation_actor)
    if hasattr(self, 'VTK3D_interactor') and self.VTK3D_interactor:
        self.VTK3D_interactor.GetRenderWindow().Render()
