from PySide6 import QtCore, QtWidgets, QtGui
import vtk
import math
import numpy as np
from fcn_display.roi_additional_plots import show_roi_plots


# ──────────────────────────────────────────────────────────────────────────────
# Small helper for consistent context menu
# ──────────────────────────────────────────────────────────────────────────────
def _context_menu(widget: QtWidgets.QWidget, enable_profile: bool = True):
    menu = QtWidgets.QMenu(widget)
    act_profile = menu.addAction("Profile…")
    act_profile.setEnabled(enable_profile)
    act_delete = menu.addAction("Delete ROI")
    chosen = menu.exec(QtGui.QCursor.pos())
    return chosen, act_profile, act_delete


# ──────────────────────────────────────────────────────────────────────────────
# Point ROI
# ──────────────────────────────────────────────────────────────────────────────
class PointRoiWidget(QtCore.QObject):
    def __init__(self, vtk_widget, renderer, parent, image_actor, orientation):
        super().__init__(parent)
        self.vtkWidget   = vtk_widget
        self.renderer    = renderer
        self.renWin      = vtk_widget.GetRenderWindow()
        self.interactor  = self.renWin.GetInteractor()
        self.parent      = parent
        self.imageActor  = image_actor
        self.orientation = orientation

        # stats-dragging picker and flags
        self._stats_picker   = vtk.vtkPropPicker()
        self._dragging_stats = False
        self._stats_start    = (0, 0)
        self._stats_orig_pix = (0.0, 0.0)

        # geometry and state
        self.crossSources = []    # two vtkLineSource
        self.crossActors  = []    # two vtkActor
        self.handleWidget = None
        self.is_visible   = False
        self._last_point  = (0.0, 0.0, 0.0)
        self._cross_half_length = 0.0

        # stats text
        self.statsActor = None

        # update on slice changed
        self.parent.sliceChanged.connect(self._update_stats)

        # let parent handle dbl-click (maximize)
        self.vtkWidget.installEventFilter(self)

        # stats text actor
        self.statsActor = vtk.vtkTextActor()
        tp = self.statsActor.GetTextProperty()
        tp.SetFontSize(self.parent.selected_font_size)
        tp.SetColor(1, 1, 0)
        tp.SetBackgroundColor(0, 0, 0)
        tp.SetBackgroundOpacity(0.5)
        self.statsActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.statsActor.SetPosition(0.70, 0.10)
        self.renderer.AddActor(self.statsActor)

        # stats drag observers
        self.interactor.AddObserver("LeftButtonPressEvent",   self._on_stats_press,   1)
        self.interactor.AddObserver("MouseMoveEvent",         self._on_stats_drag,    1)
        self.interactor.AddObserver("LeftButtonReleaseEvent", self._on_stats_release, 1)

        # right-click menu
        self._picker_right = vtk.vtkPropPicker()
        self.interactor.AddObserver("RightButtonPressEvent", self._on_right_click, 1)

        # initial render
        self._update_stats()
        self.renWin.Render()

    # Do not intercept double-clicks (so parent can maximize view)
    def eventFilter(self, obj, event):
        if obj is self.vtkWidget and event.type() == QtCore.QEvent.MouseButtonDblClick:
            return False
        return super().eventFilter(obj, event)

    # helper to “release” the VTK right-button state so dolly/zoom is not stuck
    def _cancel_vtk_right_button(self):
        style = self.interactor.GetInteractorStyle()
        try:
            if hasattr(style, "OnRightButtonUp"):
                style.OnRightButtonUp()
        except Exception:
            pass
        try:
            self.interactor.InvokeEvent("RightButtonReleaseEvent")
        except Exception:
            pass

    def _on_right_click(self, caller, event):
        # stop the interactor style from entering dolly mode
        self._cancel_vtk_right_button()

        x, y = self.interactor.GetEventPosition()
        # hit test 3D cross actors
        self._picker_right.Pick(x, y, 0, self.renderer)
        hit_actor = self._picker_right.GetActor()
        # hit test 2D stats
        self._stats_picker.Pick(x, y, 0, self.renderer)
        hit_text = (self._stats_picker.GetActor2D() is self.statsActor)

        if (hit_actor in self.crossActors) or hit_text:
            # make extra sure VTK thinks the right button is up
            self._cancel_vtk_right_button()
            chosen, act_profile, act_delete = _context_menu(self.vtkWidget, enable_profile=False)
            if chosen == act_delete:
                self.delete()
        else:
            return

    def delete(self):
        # reset any internal flags that could affect interaction
        self._dragging_stats = False
        if hasattr(self.parent, "_text_dragging"):
            self.parent._text_dragging = False

        if self.is_visible:
            self.toggle()
        for actor in self.crossActors:
            self.renderer.RemoveActor(actor)
        self.crossActors.clear()
        self.crossSources.clear()
        if self.statsActor:
            self.renderer.RemoveActor(self.statsActor)
            self.statsActor = None
        if self.handleWidget:
            self.handleWidget.Off()
            self.handleWidget = None
        self.renWin.Render()
        if hasattr(self.parent, 'points') and self in getattr(self.parent, 'points', []):
            self.parent.points.remove(self)

    # stats-drag handlers
    def _on_stats_press(self, caller, event):
        if self.statsActor is None:
            self._dragging_stats = False
            return
        x, y = self.interactor.GetEventPosition()
        self._stats_picker.Pick(x, y, 0, self.renderer)
        if self._stats_picker.GetActor2D() is self.statsActor:
            self._dragging_stats = True
            self.parent._text_dragging = True
            self._stats_start = (x, y)
            disp = self.statsActor.GetPositionCoordinate().GetComputedDisplayValue(self.renderer)
            self._stats_orig_pix = (disp[0], disp[1])

    def _on_stats_drag(self, caller, event):
        if not self._dragging_stats or self.statsActor is None:
            return
        x, y = self.interactor.GetEventPosition()
        dx, dy = x - self._stats_start[0], y - self._stats_start[1]
        w, h = self.renWin.GetSize()
        new_x = (self._stats_orig_pix[0] + dx) / w
        new_y = (self._stats_orig_pix[1] + dy) / h
        self.statsActor.GetPositionCoordinate().SetValue(new_x, new_y)
        self.renWin.Render()

    def _on_stats_release(self, caller, event):
        self._dragging_stats = False
        if hasattr(self.parent, "_text_dragging"):
            self.parent._text_dragging = False

    def _get_view_center_world(self):
        w, h = self.renWin.GetSize()
        cx, cy = w / 2, h / 2
        self.renderer.SetDisplayPoint(cx, cy, 0)
        self.renderer.DisplayToWorld()
        x, y, z, w4 = self.renderer.GetWorldPoint()
        if w4:
            x, y = x / w4, y / w4
        z = self.imageActor.GetCenter()[2] + 1.0
        return x, y, z

    def _setup_point(self):
        if self.crossActors:
            return
        cx, cy, cz = self._get_view_center_world()
        self._last_point = (cx, cy, cz)
        xmin, xmax, ymin, ymax, _, _ = self.imageActor.GetBounds()
        base = min(xmax - xmin, ymax - ymin)
        half = base * 0.02
        self._cross_half_length = half

        # two lines
        for dx, dy in [(half, 0), (0, half)]:
            src = vtk.vtkLineSource()
            src.SetPoint1(cx - dx, cy - dy, cz)
            src.SetPoint2(cx + dx, cy + dy, cz)
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(src.GetOutputPort())
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(1, 0, 0)
            actor.GetProperty().SetLineWidth(2)
            self.renderer.AddActor(actor)
            self.crossSources.append(src)
            self.crossActors.append(actor)

        # draggable handle
        rep = vtk.vtkPointHandleRepresentation3D()
        rep.SetHandleSize(10)
        rep.GetProperty().SetColor(1, 1, 0)
        rep.SetWorldPosition(self._last_point)
        hw = vtk.vtkHandleWidget()
        hw.SetInteractor(self.interactor)
        hw.SetRepresentation(rep)
        hw.AddObserver('InteractionEvent', self._on_handle_move)
        hw.On()
        self.handleWidget = hw

        # stats
        if not self.statsActor:
            self.statsActor = vtk.vtkTextActor()
            tp = self.statsActor.GetTextProperty()
            tp.SetFontSize(self.parent.selected_font_size)
            tp.SetColor(1, 1, 0)
            tp.SetBackgroundColor(0, 0, 0)
            tp.SetBackgroundOpacity(0.5)
            self.statsActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
            self.statsActor.SetPosition(0.70, 0.10)
            self.renderer.AddActor(self.statsActor)

        self._update_stats()
        self.renWin.Render()

    def _on_handle_move(self, caller, event):
        if self.handleWidget is None:
            return
        new_pt = self.handleWidget.GetRepresentation().GetWorldPosition()
        self._last_point = new_pt
        self._update_cross()
        self._update_stats()
        self.renWin.Render()

    def _update_cross(self):
        if len(self.crossSources) < 2:
            return
        cx, cy, cz = self._last_point
        half = self._cross_half_length
        self.crossSources[0].SetPoint1(cx - half, cy, cz)
        self.crossSources[0].SetPoint2(cx + half, cy, cz)
        self.crossSources[1].SetPoint1(cx, cy - half, cz)
        self.crossSources[1].SetPoint2(cx, cy + half, cz)
        for src in self.crossSources:
            src.Modified()

    def _update_stats(self):
        cx, cy, cz = self._last_point
        lines = [f"X={cx:.1f}  Y={cy:.1f}"]
        for idx, data in self.parent.display_data.items():
            if data is None or not hasattr(data, 'ndim'):
                lines.append(f"Layer {idx}: ∅")
                continue
            if data.ndim == 2:
                slc = data
            else:
                if self.orientation == 'axial':
                    si = self.parent.current_axial_slice_index[idx]; slc = data[si, :, :]
                elif self.orientation == 'coronal':
                    si = self.parent.current_coronal_slice_index[idx]; slc = data[:, si, :]
                else:
                    si = self.parent.current_sagittal_slice_index[idx]; slc = data[:, :, si]
            h, w = slc.shape
            if self.orientation == 'axial':
                px = (cx - self.parent.Im_Offset[idx, 0]) / self.parent.pixel_spac[idx, 0]
                py = (cy - self.parent.Im_Offset[idx, 1]) / self.parent.pixel_spac[idx, 1]
            elif self.orientation == 'coronal':
                px = (cx - self.parent.Im_Offset[idx, 0]) / self.parent.pixel_spac[idx, 0]
                py = (cy - self.parent.Im_Offset[idx, 2]) / self.parent.slice_thick[idx]
            else:
                px = (cx - self.parent.Im_Offset[idx, 1]) / self.parent.pixel_spac[idx, 1]
                py = (cy - self.parent.Im_Offset[idx, 2]) / self.parent.slice_thick[idx]
            px = int(np.clip(round(px), 0, w - 1)); py = int(np.clip(round(py), 0, h - 1))
            val = slc[py, px]
            lines.append(f"Layer {idx}: {val:.1f}")
        if self.statsActor:
            self.statsActor.SetInput("\n".join(lines))
            self.statsActor.Modified()
            self.statsActor.SetVisibility(self.is_visible)
        self.renWin.Render()

    def toggle(self):
        if not self.crossActors:
            self._setup_point()
            if not self.crossActors:
                return
        self.is_visible = not self.is_visible
        for a in self.crossActors:
            a.SetVisibility(self.is_visible)
        if self.handleWidget:
            self.handleWidget.On() if self.is_visible else self.handleWidget.Off()
        if self.statsActor:
            self.statsActor.SetVisibility(self.is_visible)
            self.statsActor.Modified()
        self.renWin.Render()


# ──────────────────────────────────────────────────────────────────────────────
# Circle ROI
# ──────────────────────────────────────────────────────────────────────────────
class CircleRoiWidget(QtCore.QObject):
    def __init__(self, vtk_widget, renderer, parent, image_actor, orientation):
        super().__init__(parent)
        self.vtkWidget   = vtk_widget
        self.renderer    = renderer
        self.renWin      = vtk_widget.GetRenderWindow()
        self.interactor  = self.renWin.GetInteractor()
        self.parent      = parent
        self.imageActor  = image_actor
        self.orientation = orientation

        self.circleSrc   = None
        self.circleActor = None
        self.handles     = {}
        self.is_visible  = False

        self._dragging       = False
        self._drag_offset    = (0.0, 0.0)
        self._last_center    = (0.0, 0.0, 0.0)
        self._last_radius    = 0.0
        self._dragging_stats = False
        self._stats_start    = (0, 0)
        self._stats_orig_pix = (0.0, 0.0)

        self.parent._text_dragging = False
        self.parent.sliceChanged.connect(self._onSliceChanged)
        self.vtkWidget.installEventFilter(self)

        # right-click menu
        self._picker_right = vtk.vtkPropPicker()
        self.interactor.AddObserver("RightButtonPressEvent", self._on_right_click, 1)

    # Let parent handle double-clicks
    def eventFilter(self, obj, event):
        if obj is self.vtkWidget and event.type() == QtCore.QEvent.MouseButtonDblClick:
            return False
        return super().eventFilter(obj, event)

    # same helper as in Point
    def _cancel_vtk_right_button(self):
        style = self.interactor.GetInteractorStyle()
        try:
            if hasattr(style, "OnRightButtonUp"):
                style.OnRightButtonUp()
        except Exception:
            pass
        try:
            self.interactor.InvokeEvent("RightButtonReleaseEvent")
        except Exception:
            pass

    def _onSliceChanged(self, orientation, indices):
        self._update_stats()

    def _on_right_click(self, caller, event):
        # release any VTK dolly/zoom state
        self._cancel_vtk_right_button()

        x, y = self.interactor.GetEventPosition()
        if not self.circleSrc:
            return
        # pick circle actor
        picker = vtk.vtkPropPicker()
        picker.Pick(x, y, 0, self.renderer)
        hit_actor = (picker.GetActor() is self.circleActor)

        # pick stats text
        stats_picker = vtk.vtkPropPicker()
        stats_picker.Pick(x, y, 0, self.renderer)
        hit_text = (hasattr(self, 'statsActor') and stats_picker.GetActor2D() is self.statsActor)

        if hit_actor or hit_text:
            self._cancel_vtk_right_button()
            chosen, act_profile, act_delete = _context_menu(self.vtkWidget, enable_profile=True)
            if chosen == act_delete:
                self.delete()
            elif chosen == act_profile:
                show_roi_plots(
                    parent=self.parent,
                    display_data=self.parent.display_data,
                    Im_Offset=self.parent.Im_Offset,
                    pixel_spac=self.parent.pixel_spac,
                    slice_thick=self.parent.slice_thick,
                    orientation=self.orientation,
                    center=self._last_center,
                    radii=(self._last_radius, self._last_radius),
                    roi_type='circle',
                    window_title="Circle ROI Histogram"
                )
        else:
            return

    def _get_view_center_world(self):
        w, h = self.renWin.GetSize()
        cx, cy = w / 2, h / 2
        self.renderer.SetDisplayPoint(cx, cy, 0)
        self.renderer.DisplayToWorld()
        x, y, z, w4 = self.renderer.GetWorldPoint()
        if w4:
            x, y = x / w4, y / w4
        z = self.imageActor.GetCenter()[2] + 1.0
        return x, y, z

    def _setup_circle(self):
        if self.circleSrc or not getattr(self.parent, 'display_data', None):
            return
        center = self._get_view_center_world()
        self._last_center = center
        xmin, xmax, ymin, ymax, _, _ = self.imageActor.GetBounds()
        base = min(xmax - xmin, ymax - ymin)
        self._last_radius = base * 0.1

        self.circleSrc = vtk.vtkRegularPolygonSource()
        self.circleSrc.SetNumberOfSides(60)
        self.circleSrc.SetCenter(*center)
        self.circleSrc.SetRadius(self._last_radius)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.circleSrc.GetOutputPort())
        self.circleActor = vtk.vtkActor()
        self.circleActor.SetMapper(mapper)
        self.circleActor.GetProperty().SetColor(0, 1, 0)
        self.circleActor.GetProperty().SetOpacity(0.3)
        self.renderer.AddActor(self.circleActor)

        for name in ('north', 'south', 'east', 'west'):
            rep = vtk.vtkPointHandleRepresentation3D()
            rep.SetHandleSize(10)
            rep.GetProperty().SetColor(1, 0, 0)
            handle = vtk.vtkHandleWidget()
            handle.SetRepresentation(rep)
            handle.SetInteractor(self.interactor)
            handle.AddObserver('InteractionEvent', lambda w, e, n=name: self._on_handle_move(n))
            handle.On()
            self.handles[name] = handle

        self.statsActor = vtk.vtkTextActor()
        tp = self.statsActor.GetTextProperty()
        tp.SetFontSize(self.parent.selected_font_size)
        tp.SetColor(1, 1, 0)
        tp.SetBackgroundColor(0, 0, 0)
        tp.SetBackgroundOpacity(0.5)
        self.statsActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.statsActor.SetPosition(0.70, 0.10)
        self.renderer.AddActor(self.statsActor)

        self._stats_picker = vtk.vtkPropPicker()
        self.interactor.AddObserver("LeftButtonPressEvent",   self._on_stats_press,   1)
        self.interactor.AddObserver("MouseMoveEvent",         self._on_stats_drag,    1)
        self.interactor.AddObserver("LeftButtonReleaseEvent", self._on_stats_release, 1)

        self._picker = vtk.vtkPropPicker()
        self.interactor.AddObserver("LeftButtonPressEvent",   self._on_press)
        self.interactor.AddObserver("MouseMoveEvent",         self._on_drag)
        self.interactor.AddObserver("LeftButtonReleaseEvent", self._on_release)

        self._update_handles()
        self._update_stats()
        self.renWin.Render()

    # stats drag
    def _on_stats_press(self, caller, event):
        if self.statsActor is None:
            self._dragging_stats = False
            return
        x, y = self.interactor.GetEventPosition()
        self._stats_picker.Pick(x, y, 0, self.renderer)
        if self._stats_picker.GetActor2D() is self.statsActor:
            self._dragging_stats = True
            self.parent._text_dragging = True
            self._stats_start = (x, y)
            disp = self.statsActor.GetPositionCoordinate().GetComputedDisplayValue(self.renderer)
            self._stats_orig_pix = (disp[0], disp[1])

    def _on_stats_drag(self, caller, event):
        if not self._dragging_stats or self.statsActor is None:
            return
        x, y = self.interactor.GetEventPosition()
        dx = x - self._stats_start[0]
        dy = y - self._stats_start[1]
        w, h = self.renWin.GetSize()
        new_x = (self._stats_orig_pix[0] + dx) / w
        new_y = (self._stats_orig_pix[1] + dy) / h
        self.statsActor.GetPositionCoordinate().SetValue(new_x, new_y)
        self.renWin.Render()

    def _on_stats_release(self, caller, event):
        self._dragging_stats = False
        if hasattr(self.parent, "_text_dragging"):
            self.parent._text_dragging = False

    # circle drag and handle
    def _on_press(self, caller, event):
        if self._dragging_stats:
            return
        if self.circleActor is None:
            return
        x, y = self.interactor.GetEventPosition()
        self._picker.Pick(x, y, 0, self.renderer)
        if self._picker.GetActor() is self.circleActor:
            self._dragging = True
            self.parent._text_dragging = True
            wx, wy, _ = self._get_world_point(x, y)
            cx, cy, cz = self._last_center
            self._drag_offset = (cx - wx, cy - wy)

    def _on_drag(self, caller, event):
        if self._dragging_stats:
            return
        if not self._dragging or self.circleSrc is None or self.circleActor is None:
            return
        x, y = self.interactor.GetEventPosition()
        wx, wy, _ = self._get_world_point(x, y)
        dx, dy = self._drag_offset
        new_ctr = (wx + dx, wy + dy, self._last_center[2])
        self._last_center = new_ctr
        self.circleSrc.SetCenter(*new_ctr)
        self._update_handles()
        self._update_stats()
        self.renWin.Render()

    def _on_release(self, caller, event):
        self._dragging = False
        if hasattr(self.parent, "_text_dragging"):
            self.parent._text_dragging = False

    def _on_handle_move(self, name):
        if self.circleSrc is None or not self.handles:
            return
        if name not in self.handles:
            return
        cx, cy, cz = self._last_center
        ex, ey, _ = self.handles[name].GetRepresentation().GetWorldPosition()
        new_r = math.dist((cx, cy), (ex, ey))
        self._last_radius = new_r
        self.circleSrc.SetCenter(cx, cy, cz)
        self.circleSrc.SetRadius(new_r)
        self._update_handles()
        self._update_stats()
        self.renWin.Render()

    def _update_handles(self):
        if not self.handles:
            return
        cx, cy, cz = self._last_center
        r = self._last_radius
        positions = {
            'north': (cx, cy + r, cz),
            'south': (cx, cy - r, cz),
            'east':  (cx + r, cy, cz),
            'west':  (cx - r, cy, cz)
        }
        for n, p in positions.items():
            h = self.handles.get(n)
            if h is None:
                continue
            h.GetRepresentation().SetWorldPosition(p)

    def _get_world_point(self, x, y):
        self.renderer.SetDisplayPoint(x, y, 0)
        self.renderer.DisplayToWorld()
        wp = self.renderer.GetWorldPoint()
        if wp[3] != 0.0:
            return wp[0] / wp[3], wp[1] / wp[3], wp[2] / wp[3]
        return wp[0], wp[1], wp[2]

    def _update_stats(self):
        r_mm     = self._last_radius
        area_mm2 = math.pi * r_mm**2
        lines = [f"R={r_mm:.1f} mm   A={area_mm2:.1f} mm²"]
        for idx, data in self.parent.display_data.items():
            if data is None or not hasattr(data, 'ndim'):
                lines.append(f"Layer {idx}: ∅")
                continue
            if data.ndim == 2:
                slc = data
            elif data.ndim == 3:
                if self.orientation == 'axial':
                    si = self.parent.current_axial_slice_index[idx]; slc = data[si, :, :]
                elif self.orientation == 'coronal':
                    si = self.parent.current_coronal_slice_index[idx]; slc = data[:, si, :]
                else:
                    si = self.parent.current_sagittal_slice_index[idx]; slc = data[:, :, si]
            else:
                lines.append(f"Layer {idx}: ∅")
                continue

            h, w = slc.shape
            ox, oy, _ = self._last_center
            if self.orientation == 'axial':
                px = (ox - self.parent.Im_Offset[idx, 0]) / self.parent.pixel_spac[idx, 0]
                py = (oy - self.parent.Im_Offset[idx, 1]) / self.parent.pixel_spac[idx, 1]
            elif self.orientation == 'coronal':
                px = (ox - self.parent.Im_Offset[idx, 0]) / self.parent.pixel_spac[idx, 0]
                py = (oy - self.parent.Im_Offset[idx, 2]) / self.parent.slice_thick[idx]
            else:
                px = (ox - self.parent.Im_Offset[idx, 1]) / self.parent.pixel_spac[idx, 1]
                py = (oy - self.parent.Im_Offset[idx, 2]) / self.parent.slice_thick[idx]
            px = int(np.clip(round(px), 0, w - 1)); py = int(np.clip(round(py), 0, h - 1))

            rr = int(round(r_mm / self.parent.pixel_spac[idx, 0]))
            yy, xx = np.ogrid[:h, :w]
            mask   = (xx - px)**2 + (yy - py)**2 <= rr**2
            vals = slc[mask]
            if vals.size:
                μ, σ = vals.mean(), vals.std()
                lines.append(f"Layer {idx}: Mean {μ:.1f} STD {σ:.1f}")
            else:
                lines.append(f"Layer {idx}: ∅")
        if self.statsActor:
            self.statsActor.SetInput("\n".join(lines))
            self.statsActor.Modified()
            self.statsActor.SetVisibility(True)

    def toggle(self):
        if self.circleSrc is None:
            self._setup_circle()
            if self.circleActor is None:
                return
        self.is_visible = not self.is_visible
        self.circleActor.SetVisibility(self.is_visible)
        for h in self.handles.values():
            h.On() if self.is_visible else h.Off()
        if self.statsActor:
            self.statsActor.SetVisibility(self.is_visible)
        self.renWin.Render()

    def set_fill_color(self, r, g, b, a=0.3):
        p = self.circleActor.GetProperty()
        p.SetColor(r, g, b)
        p.SetOpacity(a)
        self.renWin.Render()

    def set_edge_color(self, r, g, b):
        p = self.circleActor.GetProperty()
        p.SetEdgeColor(r, g, b)
        p.EdgeVisibilityOn()
        self.renWin.Render()

    def delete(self):
        # reset flags
        self._dragging = False
        self._dragging_stats = False
        if hasattr(self.parent, "_text_dragging"):
            self.parent._text_dragging = False

        if self.is_visible:
            self.toggle()
        if self.circleActor:
            self.renderer.RemoveActor(self.circleActor)
            self.circleActor = None
        if hasattr(self, 'statsActor') and self.statsActor:
            self.renderer.RemoveActor(self.statsActor)
            self.statsActor = None
        for hw in self.handles.values():
            hw.Off()
        self.handles.clear()
        self.circleSrc = None
        self.renWin.Render()
        if hasattr(self.parent, 'circle') and self in getattr(self.parent, 'circle', []):
            self.parent.circle.remove(self)


# ──────────────────────────────────────────────────────────────────────────────
# Ellipsoid ROI
# ──────────────────────────────────────────────────────────────────────────────
class EllipsoidRoiWidget(QtCore.QObject):
    def __init__(self, vtk_widget, renderer, parent, image_actor, orientation):
        super().__init__(parent)
        self.vtkWidget   = vtk_widget
        self.renderer    = renderer
        self.renWin      = vtk_widget.GetRenderWindow()
        self.interactor  = self.renWin.GetInteractor()
        self.parent      = parent
        self.imageActor  = image_actor
        self.orientation = orientation

        # geometry and state
        self.polySrc      = None
        self.actor        = None
        self.handles      = {}
        self.is_visible   = False
        self._last_center = (0.0, 0.0, 0.0)
        self._last_rx     = 0.0
        self._last_ry     = 0.0

        # dragging flags
        self._dragging_center = False
        self._dragging_stats  = False
        self._drag_offset     = (0.0, 0.0)
        self._stats_start     = (0, 0)
        self._stats_orig_pix  = (0, 0)
        self.parent._text_dragging = False

        # context menu on right-click
        self._picker_right = vtk.vtkPropPicker()
        self.interactor.AddObserver("RightButtonPressEvent", self._on_right_click, 1)

        # let parent handle dbl-clicks
        self.vtkWidget.installEventFilter(self)

        self.parent.sliceChanged.connect(self._onSliceChanged)

    # let parent use double-clicks (maximize)
    def eventFilter(self, obj, event):
        if obj is self.vtkWidget and event.type() == QtCore.QEvent.MouseButtonDblClick:
            return False
        return super().eventFilter(obj, event)

    # same helper
    def _cancel_vtk_right_button(self):
        style = self.interactor.GetInteractorStyle()
        try:
            if hasattr(style, "OnRightButtonUp"):
                style.OnRightButtonUp()
        except Exception:
            pass
        try:
            self.interactor.InvokeEvent("RightButtonReleaseEvent")
        except Exception:
            pass

    def _onSliceChanged(self, orientation, indices):
        self._update_stats()

    def _on_right_click(self, caller, event):
        self._cancel_vtk_right_button()

        x, y = self.interactor.GetEventPosition()
        if not self.actor:
            return
        picker = vtk.vtkPropPicker()
        picker.Pick(x, y, 0, self.renderer)
        stats_picker = vtk.vtkPropPicker()
        stats_picker.Pick(x, y, 0, self.renderer)
        hit = (picker.GetActor() is self.actor)
        hit_text = (hasattr(self, 'statsActor') and stats_picker.GetActor2D() is self.statsActor)

        if hit or hit_text:
            self._cancel_vtk_right_button()
            chosen, act_profile, act_delete = _context_menu(self.vtkWidget, enable_profile=True)
            if chosen == act_delete:
                self.delete()
            elif chosen == act_profile:
                show_roi_plots(
                    parent=self.parent,
                    display_data=self.parent.display_data,
                    Im_Offset=self.parent.Im_Offset,
                    pixel_spac=self.parent.pixel_spac,
                    slice_thick=self.parent.slice_thick,
                    orientation=self.orientation,
                    center=self._last_center,
                    radii=(self._last_rx, self._last_ry),
                    roi_type='ellipse',
                    window_title="Ellipsoid ROI Histogram",
                    return_dialog=False
                )
        else:
            return

    # setup, drag and stats logic
    def _get_view_center_world(self):
        w, h = self.renWin.GetSize()
        cx, cy = w / 2, h / 2
        self.renderer.SetDisplayPoint(cx, cy, 0)
        self.renderer.DisplayToWorld()
        x, y, z, w4 = self.renderer.GetWorldPoint()
        if w4:
            x, y = x / w4, y / w4
        z = self.imageActor.GetCenter()[2] + 1.0
        return x, y, z

    def _setup_ellipse(self):
        if self.polySrc or not getattr(self.parent, 'display_data', None):
            return
        center = self._get_view_center_world()
        self._last_center = center
        bounds = self.imageActor.GetBounds()
        width  = bounds[1] - bounds[0]
        height = bounds[3] - bounds[2]
        self._last_rx = width * 0.1
        self._last_ry = height * 0.1

        self.polySrc = vtk.vtkRegularPolygonSource()
        self.polySrc.SetNumberOfSides(60)
        self.polySrc.SetCenter(0, 0, 0)
        self.polySrc.SetRadius(1.0)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.polySrc.GetOutputPort())
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.SetScale(self._last_rx, self._last_ry, 1)
        self.actor.SetPosition(*center)
        self.actor.GetProperty().SetColor(0, 1, 0)
        self.actor.GetProperty().SetOpacity(0.3)
        self.renderer.AddActor(self.actor)

        for name, offs in [('center', (0, 0)), ('east', (1, 0)), ('north', (0, 1))]:
            rep = vtk.vtkPointHandleRepresentation3D()
            rep.SetHandleSize(12)
            rep.GetProperty().SetColor(1, 0, 0)
            if name == 'center':
                rep.GetProperty().SetOpacity(0.0)  # invisible but pickable
                rep.SetPickable(True)
            widget = vtk.vtkHandleWidget()
            widget.SetRepresentation(rep)
            widget.SetInteractor(self.interactor)
            widget.AddObserver('InteractionEvent', lambda w, e, n=name: self._on_handle_move(n))
            widget.On()
            self.handles[name] = widget

        self.statsActor = vtk.vtkTextActor()
        tp = self.statsActor.GetTextProperty()
        tp.SetFontSize(self.parent.selected_font_size)
        tp.SetColor(1, 1, 0)
        tp.SetBackgroundColor(0, 0, 0)
        tp.SetBackgroundOpacity(0.5)
        self.statsActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.statsActor.SetPosition(0.70, 0.10)
        self.renderer.AddActor(self.statsActor)

        self._stats_picker = vtk.vtkPropPicker()
        self.interactor.AddObserver("LeftButtonPressEvent",   self._on_stats_press,   1)
        self.interactor.AddObserver("MouseMoveEvent",         self._on_stats_drag,    1)
        self.interactor.AddObserver("LeftButtonReleaseEvent", self._on_stats_release, 1)

        self._picker = vtk.vtkPropPicker()
        self.interactor.AddObserver("LeftButtonPressEvent",   self._on_press)
        self.interactor.AddObserver("MouseMoveEvent",         self._on_drag)
        self.interactor.AddObserver("LeftButtonReleaseEvent", self._on_release)

        self._update_handles()
        self._update_stats()
        self.renWin.Render()

    # stats dragging
    def _on_stats_press(self, caller, event):
        if not hasattr(self, 'statsActor') or self.statsActor is None:
            self._dragging_stats = False
            return
        x, y = self.interactor.GetEventPosition()
        self._stats_picker.Pick(x, y, 0, self.renderer)
        if self._stats_picker.GetActor2D() is self.statsActor:
            self._dragging_stats = True
            self.parent._text_dragging = True
            self._stats_start = (x, y)
            disp = self.statsActor.GetPositionCoordinate().GetComputedDisplayValue(self.renderer)
            self._stats_orig_pix = (disp[0], disp[1])

    def _on_stats_drag(self, caller, event):
        if not self._dragging_stats or self.statsActor is None:
            return
        x, y = self.interactor.GetEventPosition()
        dx, dy = x - self._stats_start[0], y - self._stats_start[1]
        w, h = self.renWin.GetSize()
        new_x = (self._stats_orig_pix[0] + dx) / w
        new_y = (self._stats_orig_pix[1] + dy) / h
        self.statsActor.GetPositionCoordinate().SetValue(new_x, new_y)
        self.renWin.Render()

    def _on_stats_release(self, caller, event):
        self._dragging_stats = False
        if hasattr(self.parent, "_text_dragging"):
            self.parent._text_dragging = False

    # ellipse dragging and handles
    def _on_press(self, caller, event):
        if self._dragging_stats:
            return
        if self.actor is None:
            return
        x, y = self.interactor.GetEventPosition()
        self._picker.Pick(x, y, 0, self.renderer)
        if self._picker.GetActor() is self.actor:
            self._dragging_center = True
            self.parent._text_dragging = True
            wx, wy, _ = self._get_world_point(x, y)
            cx, cy, _ = self._last_center
            self._drag_offset = (cx - wx, cy - wy)

    def _on_drag(self, caller, event):
        if self._dragging_stats:
            return
        if not self._dragging_center or self.actor is None:
            return
        x, y = self.interactor.GetEventPosition()
        wx, wy, _ = self._get_world_point(x, y)
        dx, dy = self._drag_offset
        newc = (wx + dx, wy + dy, self._last_center[2])
        self._last_center = newc
        self.actor.SetPosition(*newc)
        self._update_handles()
        self._update_stats()
        self.renWin.Render()

    def _on_release(self, caller, event):
        self._dragging_center = False
        if hasattr(self.parent, "_text_dragging"):
            self.parent._text_dragging = False

    def _on_handle_move(self, name):
        if self.actor is None or not self.handles:
            return
        if name not in self.handles:
            return
        cx, cy, cz = self._last_center
        ex, ey, _ = self.handles[name].GetRepresentation().GetWorldPosition()
        if name == 'east':
            self._last_rx = abs(ex - cx)
        elif name == 'north':
            self._last_ry = abs(ey - cy)
        self.actor.SetScale(self._last_rx, self._last_ry, 1)
        self.actor.SetPosition(cx, cy, cz)
        self._update_handles()
        self._update_stats()
        self.renWin.Render()

    def _update_handles(self):
        if not self.handles:
            return
        cx, cy, cz = self._last_center
        if 'center' in self.handles:
            self.handles['center'].GetRepresentation().SetWorldPosition((cx, cy, cz))
        if 'east' in self.handles:
            self.handles['east'].GetRepresentation().SetWorldPosition((cx + self._last_rx, cy, cz))
        if 'north' in self.handles:
            self.handles['north'].GetRepresentation().SetWorldPosition((cx, cy + self._last_ry, cz))

    def _get_world_point(self, x, y):
        self.renderer.SetDisplayPoint(x, y, 0)
        self.renderer.DisplayToWorld()
        wp = self.renderer.GetWorldPoint()
        if wp[3] != 0.0:
            return wp[0] / wp[3], wp[1] / wp[3], wp[2] / wp[3]
        return wp[0], wp[1], wp[2]

    def _update_stats(self):
        rx, ry = self._last_rx, self._last_ry
        area = math.pi * rx * ry
        lines = [f"Rx={rx:.1f} mm   Ry={ry:.1f} mm   A={area:.1f} mm²"]
        for idx, data in self.parent.display_data.items():
            if data is None or not hasattr(data, 'ndim'):
                lines.append(f"Layer {idx}: ∅")
                continue
            if data.ndim == 2:
                slc = data
            else:
                if self.orientation == 'axial':
                    si = self.parent.current_axial_slice_index[idx]; slc = data[si, :, :]
                elif self.orientation == 'coronal':
                    si = self.parent.current_coronal_slice_index[idx]; slc = data[:, si, :]
                else:
                    si = self.parent.current_sagittal_slice_index[idx]; slc = data[:, :, si]
            h, w = slc.shape
            ox, oy, _ = self._last_center
            if self.orientation == 'axial':
                px = (ox - self.parent.Im_Offset[idx, 0]) / self.parent.pixel_spac[idx, 0]
                py = (oy - self.parent.Im_Offset[idx, 1]) / self.parent.pixel_spac[idx, 1]
            elif self.orientation == 'coronal':
                px = (ox - self.parent.Im_Offset[idx, 0]) / self.parent.pixel_spac[idx, 0]
                py = (oy - self.parent.Im_Offset[idx, 2]) / self.parent.slice_thick[idx]
            else:
                px = (ox - self.parent.Im_Offset[idx, 1]) / self.parent.pixel_spac[idx, 1]
                py = (oy - self.parent.Im_Offset[idx, 2]) / self.parent.slice_thick[idx]
            px = int(np.clip(round(px), 0, w - 1)); py = int(np.clip(round(py), 0, h - 1))
            rpx = int(round(rx / self.parent.pixel_spac[idx, 0]))
            rpy = int(round(ry / self.parent.pixel_spac[idx, 1]))
            yy, xx = np.ogrid[:h, :w]
            mask = ((xx - px) / max(rpx, 1))**2 + ((yy - py) / max(rpy, 1))**2 <= 1.0
            vals = slc[mask]
            if vals.size:
                μ, σ = vals.mean(), vals.std()
                lines.append(f"Layer {idx}: Mean {μ:.1f} STD {σ:.1f}")
            else:
                lines.append(f"Layer {idx}: ∅")
        if hasattr(self, 'statsActor') and self.statsActor:
            self.statsActor.SetInput("\n".join(lines))
            self.statsActor.Modified()
            self.statsActor.SetVisibility(True)

    def toggle(self):
        if self.actor is None:
            self._setup_ellipse()
            if self.actor is None:
                return
        self.is_visible = not self.is_visible
        self.actor.SetVisibility(self.is_visible)
        for h in self.handles.values():
            h.On() if self.is_visible else h.Off()
        if self.statsActor:
            self.statsActor.SetVisibility(self.is_visible)
        self.renWin.Render()

    def delete(self):
        # reset flags
        self._dragging_center = False
        self._dragging_stats  = False
        if hasattr(self.parent, "_text_dragging"):
            self.parent._text_dragging = False

        if self.is_visible:
            self.toggle()
        if self.actor:
            self.renderer.RemoveActor(self.actor)
            self.actor = None
        if hasattr(self, 'statsActor') and self.statsActor:
            self.renderer.RemoveActor(self.statsActor)
            self.statsActor = None
        for hw in self.handles.values():
            hw.Off()
        self.handles.clear()
        self.polySrc = None
        self.renWin.Render()
        if hasattr(self.parent, 'ellipses') and self in getattr(self.parent, 'ellipses', []):
            self.parent.ellipses.remove(self)


# ──────────────────────────────────────────────────────────────────────────────
# Square (Rectangle) ROI
# ──────────────────────────────────────────────────────────────────────────────
class SquareRoiWidget(QtCore.QObject):
    """
    Rectangle ROI widget (named SquareRoiWidget for legacy). Users can adjust width and height independently.
    Supports dragging of the stats text box like Circle and Ellipse.
    """
    def __init__(self, vtk_widget, renderer, parent, image_actor, orientation):
        super().__init__(parent)
        self.vtkWidget   = vtk_widget
        self.renderer    = renderer
        self.renWin      = vtk_widget.GetRenderWindow()
        self.interactor  = self.renWin.GetInteractor()
        self.parent      = parent
        self.imageActor  = image_actor
        self.orientation = orientation

        # geometry and state
        self.squareSrc   = None
        self.squareActor = None
        self.handles     = {}
        self.statsActor  = None
        self.is_visible  = False

        # ROI extents in world coords
        self._last_center = (0.0, 0.0, 0.0)
        self._last_rx     = 0.0  # half-width
        self._last_ry     = 0.0  # half-height

        # dragging flags
        self._dragging_center = False
        self._drag_offset     = (0.0, 0.0)
        self._dragging_stats  = False
        self._stats_start     = (0, 0)
        self._stats_orig_pix  = (0.0, 0.0)
        self.parent._text_dragging = False

        # pickers
        self._stats_picker = vtk.vtkPropPicker()
        self._picker       = vtk.vtkPropPicker()

        # optional profile helper lines (hidden by default)
        self._vline_src = vtk.vtkLineSource()
        self._vline_mapper = vtk.vtkPolyDataMapper()
        self._vline_mapper.SetInputConnection(self._vline_src.GetOutputPort())
        self._vline_actor = vtk.vtkActor()
        self._vline_actor.SetMapper(self._vline_mapper)
        self._vline_actor.GetProperty().SetColor(1, 0, 0)
        self._vline_actor.GetProperty().SetLineWidth(3)
        self._vline_actor.SetVisibility(False)
        self.renderer.AddActor(self._vline_actor)

        self._hline_src = vtk.vtkLineSource()
        self._hline_mapper = vtk.vtkPolyDataMapper()
        self._hline_mapper.SetInputConnection(self._hline_src.GetOutputPort())
        self._hline_actor = vtk.vtkActor()
        self._hline_actor.SetMapper(self._hline_mapper)
        self._hline_actor.GetProperty().SetColor(1, 0, 0)
        self._hline_actor.GetProperty().SetLineWidth(3)
        self._hline_actor.SetVisibility(False)
        self.renderer.AddActor(self._hline_actor)

        # let parent handle dbl-clicks
        self.vtkWidget.installEventFilter(self)

        # stats drag events
        self.interactor.AddObserver("LeftButtonPressEvent",   self._on_stats_press,   1)
        self.interactor.AddObserver("MouseMoveEvent",         self._on_stats_drag,    1)
        self.interactor.AddObserver("LeftButtonReleaseEvent", self._on_stats_release, 1)

        # right-click menu
        self._picker_right = vtk.vtkPropPicker()
        self.interactor.AddObserver("RightButtonPressEvent", self._on_right_click, 1)

        self.parent.sliceChanged.connect(self._onSliceChanged)

    # do not intercept double-clicks
    def eventFilter(self, obj, event):
        if obj is self.vtkWidget and event.type() == QtCore.QEvent.MouseButtonDblClick:
            return False
        return super().eventFilter(obj, event)

    # helper
    def _cancel_vtk_right_button(self):
        style = self.interactor.GetInteractorStyle()
        try:
            if hasattr(style, "OnRightButtonUp"):
                style.OnRightButtonUp()
        except Exception:
            pass
        try:
            self.interactor.InvokeEvent("RightButtonReleaseEvent")
        except Exception:
            pass

    def _onSliceChanged(self, orientation, indices):
        self._update_stats()

    def _setup_square(self):
        if self.squareSrc:
            return
        cx, cy, cz = self._get_view_center_world()
        self._last_center = (cx, cy, cz)
        b = self.imageActor.GetBounds()
        base = min(b[1] - b[0], b[3] - b[2])
        self._last_rx = self._last_ry = base * 0.1

        self.squareSrc = vtk.vtkPlaneSource()
        self._update_plane()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.squareSrc.GetOutputPort())
        self.squareActor = vtk.vtkActor()
        self.squareActor.SetMapper(mapper)
        self.squareActor.GetProperty().SetColor(0, 1, 0)
        self.squareActor.GetProperty().SetOpacity(0.3)
        self.renderer.AddActor(self.squareActor)

        for name in ('north', 'south', 'east', 'west'):
            rep = vtk.vtkPointHandleRepresentation3D()
            rep.SetHandleSize(10)
            rep.GetProperty().SetColor(1, 0, 0)
            handle = vtk.vtkHandleWidget()
            handle.SetRepresentation(rep)
            handle.SetInteractor(self.interactor)
            handle.AddObserver('InteractionEvent', lambda w, e, n=name: self._on_handle_move(n))
            handle.On()
            self.handles[name] = handle

        self.statsActor = vtk.vtkTextActor()
        tp = self.statsActor.GetTextProperty()
        tp.SetFontSize(self.parent.selected_font_size)
        tp.SetColor(1, 1, 0)
        tp.SetBackgroundColor(0, 0, 0)
        tp.SetBackgroundOpacity(0.5)
        self.statsActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.statsActor.SetPosition(0.7, 0.1)
        self.renderer.AddActor(self.statsActor)

        # ROI move observers
        self.interactor.AddObserver('LeftButtonPressEvent',   self._on_press)
        self.interactor.AddObserver('MouseMoveEvent',         self._on_drag)
        self.interactor.AddObserver('LeftButtonReleaseEvent', self._on_release)

        self._update_handles()
        self._update_stats()
        self.renWin.Render()

    def _get_view_center_world(self):
        w, h = self.renWin.GetSize()
        cx, cy = w / 2, h / 2
        self.renderer.SetDisplayPoint(cx, cy, 0)
        self.renderer.DisplayToWorld()
        x, y, z, w4 = self.renderer.GetWorldPoint()
        if w4:
            x, y = x / w4, y / w4
        z = self.imageActor.GetCenter()[2] + 1.0
        return x, y, z

    def _on_right_click(self, caller, event):
        # tell VTK "right button is up" before anything
        self._cancel_vtk_right_button()

        x, y = self.interactor.GetEventPosition()
        if not self.squareSrc:
            return
        self._picker_right.Pick(x, y, 0, self.renderer)
        picked = self._picker_right.GetActor()
        self._stats_picker.Pick(x, y, 0, self.renderer)
        picked_text = (self._stats_picker.GetActor2D() is self.statsActor)

        if picked is self.squareActor or picked_text:
            self._cancel_vtk_right_button()
            chosen, act_profile, act_delete = _context_menu(self.vtkWidget, enable_profile=True)
            if chosen == act_delete:
                self.delete()
            elif chosen == act_profile:
                dlg = show_roi_plots(
                    parent=self.parent,
                    display_data=self.parent.display_data,
                    Im_Offset=self.parent.Im_Offset,
                    pixel_spac=self.parent.pixel_spac,
                    slice_thick=self.parent.slice_thick,
                    orientation=self.orientation,
                    center=self._last_center,
                    radii=(self._last_rx, self._last_ry),
                    roi_type='square',
                    window_title='Rectangle ROI Analysis',
                    return_dialog=True
                )
                if dlg is None:
                    return

                # Connect sliders (values are in world mm)
                def on_x(val):
                    self._update_vertical_profile_line(float(val))

                def on_y(val):
                    self._update_horizontal_profile_line(float(val))

                dlg.sld_x.valueChanged.connect(on_x)
                dlg.sld_y.valueChanged.connect(on_y)

                dlg.show()
        else:
            return

    #
    # profile helper lines
    #
    def _update_vertical_profile_line(self, x_mm: float):
        """Draw vertical red line at given X (world mm) through the current ROI."""
        if not self.squareSrc:
            return
        cx, cy, cz = self._last_center
        rx, ry     = self._last_rx, self._last_ry
        y0 = cy - ry
        y1 = cy + ry
        self._vline_src.SetPoint1(x_mm, y0, cz)
        self._vline_src.SetPoint2(x_mm, y1, cz)
        self._vline_src.Modified()
        self._vline_actor.SetVisibility(True)
        self.renWin.Render()

    def _update_horizontal_profile_line(self, y_mm: float):
        """Draw horizontal red line at given Y (world mm) through the current ROI."""
        if not self.squareSrc:
            return
        cx, cy, cz = self._last_center
        rx, ry     = self._last_rx, self._last_ry
        x0 = cx - rx
        x1 = cx + rx
        self._hline_src.SetPoint1(x0, y_mm, cz)
        self._hline_src.SetPoint2(x1, y_mm, cz)
        self._hline_src.Modified()
        self._hline_actor.SetVisibility(True)
        self.renWin.Render()

    # stats dragging handlers
    def _on_stats_press(self, caller, event):
        if self.statsActor is None:
            self._dragging_stats = False
            return
        x, y = self.interactor.GetEventPosition()
        self._stats_picker.Pick(x, y, 0, self.renderer)
        if self._stats_picker.GetActor2D() is self.statsActor:
            self._dragging_stats = True
            self.parent._text_dragging = True
            self._stats_start = (x, y)
            disp = self.statsActor.GetPositionCoordinate().GetComputedDisplayValue(self.renderer)
            self._stats_orig_pix = (disp[0], disp[1])

    def _on_stats_drag(self, caller, event):
        if not self._dragging_stats or self.statsActor is None:
            return
        x, y = self.interactor.GetEventPosition()
        dx = x - self._stats_start[0]
        dy = y - self._stats_start[1]
        w, h = self.renWin.GetSize()
        self.statsActor.GetPositionCoordinate().SetValue(
            (self._stats_orig_pix[0] + dx) / w,
            (self._stats_orig_pix[1] + dy) / h
        )
        self.renWin.Render()

    def _on_stats_release(self, caller, event):
        self._dragging_stats = False
        if hasattr(self.parent, "_text_dragging"):
            self.parent._text_dragging = False

    # ROI move
    def _on_press(self, caller, event):
        if self._dragging_stats:
            return
        if self.squareActor is None:
            return
        x, y = self.interactor.GetEventPosition()
        self._picker.Pick(x, y, 0, self.renderer)
        if self._picker.GetActor() is self.squareActor:
            self._dragging_center = True
            self.parent._text_dragging = True
            wx, wy, _ = self._get_world_point(x, y)
            cx, cy, _ = self._last_center
            self._drag_offset = (cx - wx, cy - wy)

    def _on_drag(self, caller, event):
        # if ROI deleted, stop handling drag
        if self.squareSrc is None or self.squareActor is None or not self.handles:
            self._dragging_center = False
            return
        if not self._dragging_center:
            return
        x, y = self.interactor.GetEventPosition()
        wx, wy, _ = self._get_world_point(x, y)
        dx, dy = self._drag_offset
        self._last_center = (wx + dx, wy + dy, self._last_center[2])
        self._update_plane()
        self._update_handles()
        self._update_stats()
        self.renWin.Render()

    def _on_release(self, caller, event):
        self._dragging_center = False
        if hasattr(self.parent, "_text_dragging"):
            self.parent._text_dragging = False

    def _get_world_point(self, x, y):
        self.renderer.SetDisplayPoint(x, y, 0)
        self.renderer.DisplayToWorld()
        wp = self.renderer.GetWorldPoint()
        if wp[3] != 0:
            return (wp[0] / wp[3], wp[1] / wp[3], wp[2] / wp[3])
        return (wp[0], wp[1], wp[2])

    def _update_plane(self):
        if self.squareSrc is None:
            return
        cx, cy, cz = self._last_center
        rx, ry = self._last_rx, self._last_ry
        self.squareSrc.SetOrigin(cx - rx, cy - ry, cz)
        self.squareSrc.SetPoint1(cx + rx, cy - ry, cz)
        self.squareSrc.SetPoint2(cx - rx, cy + ry, cz)
        self.squareSrc.Update()

    def _on_handle_move(self, name):
        # ignore stray events after delete
        if self.squareSrc is None or not self.handles:
            return
        if name not in self.handles:
            return
        cx, cy, cz = self._last_center
        ex, ey, _ = self.handles[name].GetRepresentation().GetWorldPosition()
        if name in ('north', 'south'):
            self._last_ry = abs(ey - cy)
        else:
            self._last_rx = abs(ex - cx)
        self._update_plane()
        self._update_handles()
        self._update_stats()
        self.renWin.Render()

    def _update_handles(self):
        # if ROI deleted or handles cleared or partial, do nothing
        if not self.handles:
            return
        cx, cy, cz = self._last_center
        rx, ry = self._last_rx, self._last_ry
        positions = {
            'north': (cx, cy + ry, cz),
            'south': (cx, cy - ry, cz),
            'east':  (cx + rx, cy, cz),
            'west':  (cx - rx, cy, cz)
        }
        for n, p in positions.items():
            h = self.handles.get(n)
            if h is None:
                continue
            h.GetRepresentation().SetWorldPosition(p)

    def _update_stats(self):
        rx, ry = self._last_rx, self._last_ry
        area = (2 * rx) * (2 * ry)
        lines = [f"W={2*rx:.1f} H={2*ry:.1f} A={area:.1f} mm²"]
        for idx, data in self.parent.display_data.items():
            if data is None or not hasattr(data, 'ndim'):
                lines.append(f"Layer {idx}: ∅")
                continue

            if data.ndim == 2:
                slc = data
            else:
                if self.orientation == 'axial':
                    si = self.parent.current_axial_slice_index[idx]; slc = data[si, :, :]
                elif self.orientation == 'coronal':
                    si = self.parent.current_coronal_slice_index[idx]; slc = data[:, si, :]
                else:
                    si = self.parent.current_sagittal_slice_index[idx]; slc = data[:, :, si]

            h, w = slc.shape
            ox, oy, _ = self._last_center
            if self.orientation == 'axial':
                px = (ox - self.parent.Im_Offset[idx, 0]) / self.parent.pixel_spac[idx, 0]
                py = (oy - self.parent.Im_Offset[idx, 1]) / self.parent.pixel_spac[idx, 1]
            elif self.orientation == 'coronal':
                px = (ox - self.parent.Im_Offset[idx, 0]) / self.parent.pixel_spac[idx, 0]
                py = (oy - self.parent.Im_Offset[idx, 2]) / self.parent.slice_thick[idx]
            else:
                px = (ox - self.parent.Im_Offset[idx, 1]) / self.parent.pixel_spac[idx, 1]
                py = (oy - self.parent.Im_Offset[idx, 2]) / self.parent.slice_thick[idx]
            px = int(np.clip(round(px), 0, w - 1))
            py = int(np.clip(round(py), 0, h - 1))

            rpx = int(round(rx / self.parent.pixel_spac[idx, 0]))
            rpy = int(round(ry / self.parent.pixel_spac[idx, 1]))
            yy, xx = np.ogrid[:h, :w]
            mask = ((xx - px) / max(rpx, 1))**2 + ((yy - py) / max(rpy, 1))**2 <= 1.0
            vals = slc[mask]
            if vals.size:
                μ, σ = vals.mean(), vals.std()
                lines.append(f"Layer {idx}: Mean {μ:.1f} STD {σ:.1f}")
            else:
                lines.append(f"Layer {idx}: ∅")

        if self.statsActor:
            self.statsActor.SetInput("\n".join(lines))
            self.statsActor.Modified()
            self.statsActor.SetVisibility(True)

    def toggle(self):
        if not self.squareSrc:
            self._setup_square()
        self.is_visible = not self.is_visible
        self.squareActor.SetVisibility(self.is_visible)
        for h in self.handles.values():
            h.On() if self.is_visible else h.Off()
        if self.statsActor:
            self.statsActor.SetVisibility(self.is_visible)
        self.renWin.Render()

    def delete(self):
        # reset flags
        self._dragging_center = False
        self._dragging_stats  = False
        if hasattr(self.parent, "_text_dragging"):
            self.parent._text_dragging = False

        if self.is_visible:
            self.toggle()
        if self.squareActor:
            self.renderer.RemoveActor(self.squareActor)
            self.squareActor = None
        if self.statsActor:
            self.renderer.RemoveActor(self.statsActor)
            self.statsActor = None
        for hw in self.handles.values():
            hw.Off()
        self.handles.clear()
        self.squareSrc = None
        # hide helper lines
        self._vline_actor.SetVisibility(False)
        self._hline_actor.SetVisibility(False)
        self.renWin.Render()
        if hasattr(self.parent, 'squares') and self in getattr(self.parent, 'squares', []):
            self.parent.squares.remove(self)
