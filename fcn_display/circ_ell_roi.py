from PyQt5 import QtCore, QtWidgets
import vtk
import math
from fcn_display.roi_additional_plots import show_roi_plots
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)


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

        # stats-dragging picker & flags
        self._stats_picker   = vtk.vtkPropPicker()
        self._dragging_stats = False
        self._stats_start    = (0, 0)
        self._stats_orig_pix = (0.0, 0.0)

        # geometry + state
        self.crossSources = []    # two vtkLineSource
        self.crossActors  = []    # two vtkActor
        self.handleWidget = None
        self.is_visible   = False
        self._last_point  = (0.0,0.0,0.0)
        self._cross_half_length = 0.0

        # stats text
        self.statsActor = None

        # connect slice changes and mouse events
        self.parent.sliceChanged.connect(self._update_stats)
        self.vtkWidget.installEventFilter(self)
                # --- stats text (after self.renderer.AddActor) ---
        self.statsActor = vtk.vtkTextActor()
        tp = self.statsActor.GetTextProperty()
        tp.SetFontSize(self.parent.selected_font_size)
        tp.SetColor(1,1,0)
        tp.SetBackgroundColor(0,0,0)
        tp.SetBackgroundOpacity(0.5)
        self.statsActor.GetPositionCoordinate()\
             .SetCoordinateSystemToNormalizedDisplay()
        self.statsActor.SetPosition(0.70,0.10)
        self.renderer.AddActor(self.statsActor)

        # now hook the stats‐drag observers (priority=1 so before others)
        self.interactor.AddObserver("LeftButtonPressEvent",   self._on_stats_press,   1)
        self.interactor.AddObserver("MouseMoveEvent",         self._on_stats_drag,    1)
        self.interactor.AddObserver("LeftButtonReleaseEvent", self._on_stats_release, 1)

        self._picker_right = vtk.vtkPropPicker()
        self.interactor.AddObserver(
            "RightButtonPressEvent",
            self._on_right_click,
            1
        )

        # initial render
        self._update_stats()
        self.renWin.Render()

    def _on_right_click(self, caller, event):
        x, y = self.interactor.GetEventPosition()
        # pick 3D actors
        self._picker_right.Pick(x, y, 0, self.renderer)
        picked_actor = self._picker_right.GetActor()
        # pick 2D text
        self._stats_picker.Pick(x, y, 0, self.renderer)
        picked_text = (self._stats_picker.GetActor2D() is self.statsActor)

        # if they clicked the crosshair lines or the stats box, delete
        if (picked_actor in self.crossActors) or picked_text:
            self.delete()

    def delete(self):
        # hide if visible
        if self.is_visible:
            self.toggle()
        # remove crosshair actors
        for actor in self.crossActors:
            self.renderer.RemoveActor(actor)
        # remove stats text
        if self.statsActor:
            self.renderer.RemoveActor(self.statsActor)
        # turn off the handle widget
        if self.handleWidget:
            self.handleWidget.Off()
        # re-render
        self.renWin.Render()
        # unregister from parent list
        if hasattr(self.parent, 'points') and self in self.parent.points:
            self.parent.points.remove(self)

    # — stats‐drag handlers —    
    def _on_stats_press(self, caller, event):
        x, y = self.interactor.GetEventPosition()
        self._stats_picker.Pick(x, y, 0, self.renderer)
        if self._stats_picker.GetActor2D() is self.statsActor:
            self._dragging_stats = True
            self.parent._text_dragging = True
            self._stats_start     = (x, y)
            disp = self.statsActor.GetPositionCoordinate()\
                         .GetComputedDisplayValue(self.renderer)
            self._stats_orig_pix = (disp[0], disp[1])

    def _on_stats_drag(self, caller, event):
        if not self._dragging_stats:
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
        self.parent._text_dragging = False

    def _get_view_center_world(self):
        w,h = self.renWin.GetSize()
        cx, cy = w/2, h/2
        self.renderer.SetDisplayPoint(cx, cy, 0)
        self.renderer.DisplayToWorld()
        x,y,z,w4 = self.renderer.GetWorldPoint()
        if w4:
            x,y = x/w4, y/w4
        z = self.imageActor.GetCenter()[2] + 1.0
        return x,y,z

    def _setup_point(self):
        if self.crossActors:
            return

        # initial center & cross size (10% of smaller image-dimension)
        cx, cy, cz = self._get_view_center_world()
        self._last_point = (cx,cy,cz)
        xmin,xmax,ymin,ymax,_,_ = self.imageActor.GetBounds()
        base = min(xmax-xmin, ymax-ymin)
        half = base * 0.02
        self._cross_half_length = half

        # --- build two perpendicular lines ---
        for dx,dy in [(half,0),(0,half)]:
            src = vtk.vtkLineSource()
            src.SetPoint1(cx-dx, cy-dy, cz)
            src.SetPoint2(cx+dx, cy+dy, cz)
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(src.GetOutputPort())
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(1,0,0)
            actor.GetProperty().SetLineWidth(2)
            self.renderer.AddActor(actor)
            self.crossSources.append(src)
            self.crossActors .append(actor)

        # --- handle widget for dragging the point ---
        rep = vtk.vtkPointHandleRepresentation3D()
        rep.SetHandleSize(10)
        rep.GetProperty().SetColor(1,1,0)
        rep.SetWorldPosition(self._last_point)
        hw = vtk.vtkHandleWidget()
        hw.SetInteractor(self.interactor)
        hw.SetRepresentation(rep)
        hw.AddObserver('InteractionEvent', self._on_handle_move)
        hw.On()
        self.handleWidget = hw

        # --- stats text ---
        self.statsActor = vtk.vtkTextActor()
        tp = self.statsActor.GetTextProperty()
        tp.SetFontSize(self.parent.selected_font_size)
        tp.SetColor(1,1,0)
        tp.SetBackgroundColor(0,0,0)
        tp.SetBackgroundOpacity(0.5)
        self.statsActor.GetPositionCoordinate()\
             .SetCoordinateSystemToNormalizedDisplay()
        self.statsActor.SetPosition(0.70,0.10)
        self.renderer.AddActor(self.statsActor)

        # initial render
        self._update_stats()
        self.renWin.Render()

    def _on_handle_move(self, caller, event):
        # get new point, update cross + stats
        new_pt = self.handleWidget.GetRepresentation().GetWorldPosition()
        self._last_point = new_pt
        self._update_cross()
        self._update_stats()
        self.renWin.Render()

    def _update_cross(self):
        cx,cy,cz = self._last_point
        half = self._cross_half_length
        # horizontal line
        self.crossSources[0].SetPoint1(cx-half, cy, cz)
        self.crossSources[0].SetPoint2(cx+half, cy, cz)
        # vertical line
        self.crossSources[1].SetPoint1(cx, cy-half, cz)
        self.crossSources[1].SetPoint2(cx, cy+half, cz)
        for src in self.crossSources:
            src.Modified()

    def _update_stats(self):
        # very similar to circle widget, but just sample the single pixel
        cx, cy, cz = self._last_point
        lines = [f"X={cx:.1f}  Y={cy:.1f}"]
        for idx, data in self.parent.display_data.items():
            if data is None or not hasattr(data, 'ndim'):
                lines.append(f"Layer {idx}: ∅")
                continue

            # select correct slice
            if data.ndim == 2:
                slc = data
            else:
                if self.orientation == 'axial':
                    si = self.parent.current_axial_slice_index[idx]
                    slc = data[si,:,:]
                elif self.orientation == 'coronal':
                    si = self.parent.current_coronal_slice_index[idx]
                    slc = data[:,si,:]
                else:
                    si = self.parent.current_sagittal_slice_index[idx]
                    slc = data[:,:,si]

            h,w = slc.shape

            # map world→pixel
            if self.orientation == 'axial':
                px = (cx - self.parent.Im_Offset[idx,0]) / self.parent.pixel_spac[idx,0]
                py = (cy - self.parent.Im_Offset[idx,1]) / self.parent.pixel_spac[idx,1]
            elif self.orientation == 'coronal':
                px = (cx - self.parent.Im_Offset[idx,0]) / self.parent.pixel_spac[idx,0]
                py = (cy - self.parent.Im_Offset[idx,2]) / self.parent.slice_thick[idx]
            else:
                px = (cx - self.parent.Im_Offset[idx,1]) / self.parent.pixel_spac[idx,1]
                py = (cy - self.parent.Im_Offset[idx,2]) / self.parent.slice_thick[idx]

            px = int(round(np.clip(px,0,w-1)))
            py = int(round(np.clip(py,0,h-1)))
            val = slc[py,px]
            lines.append(f"Layer {idx}: {val:.1f}")

        txt = "\n".join(lines)
        self.statsActor.SetInput(txt)
        self.statsActor.Modified()
        self.statsActor.SetVisibility(self.is_visible)
        self.renWin.Render()

    def toggle(self):
        # build on first show
        if not self.crossActors:
            self._setup_point()
            if not self.crossActors:
                return

        # flip visibility
        self.is_visible = not self.is_visible
        for actor in self.crossActors:
            actor.SetVisibility(self.is_visible)
        if self.handleWidget:
            if self.is_visible:
                self.handleWidget.On()
            else:
                self.handleWidget.Off()
        if self.statsActor:
            self.statsActor.SetVisibility(self.is_visible)
            self.statsActor.Modified()
        self.renWin.Render()

class CircleRoiWidget(QtCore.QObject):

    def __init__(self, vtk_widget, renderer, parent, image_actor, orientation):
        super().__init__(parent)
        """
        vtk_widget:  QVTKRenderWindowInteractor for this view
        renderer:    corresponding vtkRenderer
        parent:      main window with display_data etc.
        image_actor: vtkImageActor showing the DICOM image in this view
        orientation: 'axial', 'coronal' or 'sagittal'
        """
        self.vtkWidget   = vtk_widget
        self.renderer    = renderer
        self.renWin      = vtk_widget.GetRenderWindow()
        self.interactor  = self.renWin.GetInteractor()
        self.parent      = parent
        self.imageActor  = image_actor
        self.orientation = orientation

        # geometry and state
        self.circleSrc   = None
        self.circleActor = None
        self.handles     = {}
        self.is_visible  = False

        # internal flags
        self._dragging       = False
        self._resizing       = False
        self._drag_offset    = (0.0, 0.0)
        self._last_center    = (0.0, 0.0, 0.0)
        self._last_radius    = 0.0
        self._dragging_stats = False
        self._stats_start    = (0, 0)
        self._stats_orig_pix = (0.0, 0.0)
        self.parent._text_dragging = False
        self.parent.sliceChanged.connect(self._onSliceChanged)
        self.vtkWidget.installEventFilter(self)

        self._picker_right = vtk.vtkPropPicker()
        self.interactor.AddObserver(
            "RightButtonPressEvent",
            self._on_right_click,
            1
        )
    
    def _onSliceChanged(self, orientation, indices):
        # indices is [idx0, idx1, idx2, idx3]
        # just recompute your stats/plots against the new slice positions:
        self._update_stats()

    def eventFilter(self, obj, event):
        if obj is self.vtkWidget and event.type() == QtCore.QEvent.MouseButtonDblClick:
            # only proceed if ROI exists and is visible
            if self.circleSrc is None:
                return False
            print("test")
            # compute display-space center and radius of ROI
            cx, cy, cz = self._last_center
            r_world = self._last_radius
            coord = vtk.vtkCoordinate()
            coord.SetCoordinateSystemToWorld()
            coord.SetValue(cx, cy, cz)
            disp_center = coord.GetComputedDisplayValue(self.renderer)
            coord.SetValue(cx + r_world, cy, cz)
            disp_edge = coord.GetComputedDisplayValue(self.renderer)
            r_disp = abs(disp_edge[0] - disp_center[0])

            # get mouse click in display coords
            click_x = event.pos().x()
            click_y = event.pos().y()
            w, h = self.renWin.GetSize()
            click_y_inv = h - click_y

            dx = click_x - disp_center[0]
            dy = click_y_inv - disp_center[1]
            if dx*dx + dy*dy <= r_disp*r_disp:
                # inside ROI: show histogram
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
                return True
            # outside ROI: do not intercept—allow VTK to handle (maximize axes, etc.)
            return False
        return super().eventFilter(obj, event)

    def _get_view_center_world(self):
        """Return (x,y,z) of viewport center in world coords."""
        w, h = self.renWin.GetSize()
        cx, cy = w/2, h/2
        self.renderer.SetDisplayPoint(cx, cy, 0)
        self.renderer.DisplayToWorld()
        x, y, z, w4 = self.renderer.GetWorldPoint()
        if w4:
            x, y = x/w4, y/w4
        # lift above image plane
        z = self.imageActor.GetCenter()[2] + 1.0
        return x, y, z

    def _setup_circle(self):
        if self.circleSrc or not getattr(self.parent, 'display_data', None):
            return

        # --- circle geometry ---
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

        # --- cardinal handles for resizing ---
        for name, (dx, dy) in {
            'north': (0, +1),
            'south': (0, -1),
            'east':  (+1, 0),
            'west':  (-1, 0),
        }.items():
            rep = vtk.vtkPointHandleRepresentation3D()
            rep.SetHandleSize(10)
            rep.GetProperty().SetColor(1, 0, 0)
            handle = vtk.vtkHandleWidget()
            handle.SetRepresentation(rep)
            handle.SetInteractor(self.interactor)
            handle.AddObserver('InteractionEvent',
                               lambda w, e, n=name: self._on_handle_move(n))
            handle.On()
            self.handles[name] = handle

        # --- stats text actor ---
        self.statsActor = vtk.vtkTextActor()
        tp = self.statsActor.GetTextProperty()
        tp.SetFontSize(self.parent.selected_font_size)
        tp.SetColor(1, 1, 0)
        # give it a semi-transparent black background
        tp.SetBackgroundColor(0, 0, 0)
        tp.SetBackgroundOpacity(0.5)
        self.statsActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.statsActor.SetPosition(0.70, 0.10)
        self.renderer.AddActor(self.statsActor)

        # stats dragging picker
        self._stats_picker = vtk.vtkPropPicker()

        # hook stats region first
        self.interactor.AddObserver("LeftButtonPressEvent",   self._on_stats_press,   1)
        self.interactor.AddObserver("MouseMoveEvent",         self._on_stats_drag,    1)
        self.interactor.AddObserver("LeftButtonReleaseEvent", self._on_stats_release, 1)

        # circle pick & drag observers
        self._picker = vtk.vtkPropPicker()
        self.interactor.AddObserver("LeftButtonPressEvent",   self._on_press)
        self.interactor.AddObserver("MouseMoveEvent",         self._on_drag)
        self.interactor.AddObserver("LeftButtonReleaseEvent", self._on_release)

        # initial placement and stats
        self._update_handles()
        self._update_stats()
        self.renWin.Render()

    # — stats‐drag handlers —
    def _on_stats_press(self, caller, event):
        x, y = self.interactor.GetEventPosition()
        self._stats_picker.Pick(x, y, 0, self.renderer)
        if self._stats_picker.GetActor2D() is self.statsActor:
            self._dragging_stats = True
            self.parent._text_dragging = True
            self._stats_start    = (x, y)
            disp = self.statsActor.GetPositionCoordinate()\
                         .GetComputedDisplayValue(self.renderer)
            self._stats_orig_pix = (disp[0], disp[1])

    def _on_stats_drag(self, caller, event):
        if not self._dragging_stats:
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

    # — circle‐drag & handle‐move —
    def _on_press(self, caller, event):
        if self._dragging_stats:
            return
        x, y = self.interactor.GetEventPosition()
        self._picker.Pick(x, y, 0, self.renderer)
        if self._picker.GetActor() is self.circleActor:
            self._dragging = True
            self.parent._text_dragging = True
            wx, wy, _ = self._get_world_point(x, y)
            cx, cy, cz = self._last_center
            self._drag_offset = (cx - wx, cy - wy)
        # otherwise let handle-widgets manage resizing

    def _on_drag(self, caller, event):
        if self._dragging_stats:
            return
        x, y = self.interactor.GetEventPosition()
        if self._dragging:
            wx, wy, _ = self._get_world_point(x, y)
            dx, dy = self._drag_offset
            new_ctr = (wx + dx, wy + dy, self._last_center[2])
            self._last_center = new_ctr
            self.circleSrc.SetCenter(*new_ctr)
            self._update_handles()
            self._update_stats()
            self.renWin.Render()
        # resizing occurs via vtkHandleWidget -> _on_handle_move

    def _on_release(self, caller, event):
        self._dragging = False
        self.parent._text_dragging = False

    def _on_handle_move(self, name):
        """Called when one of the N/S/E/W handles moves."""
        # get current center & the moved handle’s world pos
        cx, cy, cz = self._last_center
        ex, ey, _  = self.handles[name].GetRepresentation().GetWorldPosition()

        # compute new radius and update
        new_r = math.dist((cx, cy), (ex, ey))
        self._last_radius = new_r
        self.circleSrc.SetCenter(cx, cy, cz)
        self.circleSrc.SetRadius(new_r)

        # reposition all handles around this new circle
        self._update_handles()
        # recompute stats display
        self._update_stats()
        self.renWin.Render()

    def _update_handles(self):
        cx, cy, cz = self._last_center
        r = self._last_radius
        for name, pos in {
            'north': (cx, cy + r, cz),
            'south': (cx, cy - r, cz),
            'east':  (cx + r, cy, cz),
            'west':  (cx - r, cy, cz)
        }.items():
            self.handles[name].GetRepresentation().SetWorldPosition(pos)

    def _get_world_point(self, x, y):
        self.renderer.SetDisplayPoint(x, y, 0)
        self.renderer.DisplayToWorld()
        wp = self.renderer.GetWorldPoint()
        if wp[3] != 0.0:
            return wp[0]/wp[3], wp[1]/wp[3], wp[2]/wp[3]
        return wp[0], wp[1], wp[2]

    def _update_stats(self):
        r_mm     = self._last_radius
        area_mm2 = math.pi * r_mm**2
        lines = [f"R={r_mm:.1f} mm   A={area_mm2:.1f} mm²"]

        for idx, data in self.parent.display_data.items():
            if data is None or not hasattr(data, 'ndim'):
                lines.append(f"Layer {idx}: ∅")
                continue

            # pick correct slice per orientation
            if data.ndim == 2:
                slc = data
            elif data.ndim == 3:
                if self.orientation == 'axial':
                    si  = self.parent.current_axial_slice_index[idx]
                    slc = data[si, :, :]
                elif self.orientation == 'coronal':
                    si  = self.parent.current_coronal_slice_index[idx]
                    slc = data[:, si, :]
                else:  # sagittal
                    si  = self.parent.current_sagittal_slice_index[idx]
                    slc = data[:, :, si]
            else:
                lines.append(f"Layer {idx}: ∅")
                continue

            h, w = slc.shape

            # map world-center → pixel coords depending on orientation
            ox, oy, _ = self._last_center
            if self.orientation == 'axial':
                px = (ox - self.parent.Im_Offset[idx,0]) / self.parent.pixel_spac[idx,0]
                py = (oy - self.parent.Im_Offset[idx,1]) / self.parent.pixel_spac[idx,1]
            elif self.orientation == 'coronal':
                # world x→column, world z→row for coronal
                px = (ox - self.parent.Im_Offset[idx,0]) / self.parent.pixel_spac[idx,0]
                py = (oy - self.parent.Im_Offset[idx,2]) / self.parent.slice_thick[idx]
            else:  # sagittal
                # world y→column, world z→row
                px = (ox - self.parent.Im_Offset[idx,1]) / self.parent.pixel_spac[idx,1
                                                                                  ]
                py = (oy - self.parent.Im_Offset[idx,2]) / self.parent.slice_thick[idx]

            px = int(round(np.clip(px, 0, w-1)))
            py = int(round(np.clip(py, 0, h-1)))

            rr = int(round(r_mm / self.parent.pixel_spac[idx,0]))

            yy, xx = np.ogrid[:h, :w]
            mask   = (xx-px)**2 + (yy-py)**2 <= rr**2

            vals = slc[mask]
            if vals.size:
                μ, σ = vals.mean(), vals.std()
                lines.append(f"Layer {idx}: Mean {μ:.1f} STD {σ:.1f}")
            else:
                lines.append(f"Layer {idx}: ∅")

        txt = "\n".join(lines)
        self.statsActor.SetInput(txt)
        self.statsActor.Modified()
        self.statsActor.SetVisibility(True)
        self.renWin.Render()


    def toggle(self):
        # If we haven’t built the circle yet, try now
        if self.circleSrc is None:
            self._setup_circle()
            # If setup failed (no image loaded), bail out
            if self.circleActor is None:
                return

        # Flip visibility
        self.is_visible = not self.is_visible

        # Show/hide circle
        self.circleActor.SetVisibility(self.is_visible)

        # Enable or disable the handle widgets
        for h in self.handles.values():
            if self.is_visible:
                h.On()
            else:
                h.Off()

        # Show/hide stats text
        if self.statsActor:
            self.statsActor.SetVisibility(self.is_visible)
            self.statsActor.Modified()

        # Re-render
        self.renWin.Render()

    # —————————————————————————————————
    # Appearance customization:
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
        
    def _on_right_click(self, caller, event):
        x, y = self.interactor.GetEventPosition()
        # test circle actor
        self._picker_right.Pick(x, y, 0, self.renderer)
        picked = self._picker_right.GetActor()
        # test stats text
        self._stats_picker.Pick(x, y, 0, self.renderer)
        picked_text = (self._stats_picker.GetActor2D() is self.statsActor)

        if picked is self.circleActor or picked_text:
            self.delete()

    def delete(self):
        # hide
        if self.is_visible:
            self.toggle()
        # remove the circle actor
        if self.circleActor:
            self.renderer.RemoveActor(self.circleActor)
        # remove the text actor
        if self.statsActor:
            self.renderer.RemoveActor(self.statsActor)
        # disable all resize handles
        for hw in self.handles.values():
            hw.Off()
        # re-render
        self.renWin.Render()
        # unregister from parent list
        if hasattr(self.parent, 'circle') and self in self.parent.circle:
            self.parent.circle.remove(self)

class EllipsoidRoiWidget(QtCore.QObject):
    def __init__(self, vtk_widget, renderer, parent, image_actor, orientation):
        super().__init__(parent)
        """
        vtk_widget:  QVTKRenderWindowInteractor for this view
        renderer:    corresponding vtkRenderer
        parent:      main window with display_data etc.
        image_actor: vtkImageActor showing the DICOM image in this view
        orientation: 'axial', 'coronal' or 'sagittal'
        """
        self.vtkWidget   = vtk_widget
        self.renderer    = renderer
        self.renWin      = vtk_widget.GetRenderWindow()
        self.interactor  = self.renWin.GetInteractor()
        self.parent      = parent
        self.imageActor  = image_actor
        self.orientation = orientation

        # geometry & state
        self.polySrc     = None
        self.actor       = None
        self.handles     = {}
        self.is_visible  = False
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

        # picker for right-click deletion
        self._picker_right = vtk.vtkPropPicker()
        self.interactor.AddObserver(
            "RightButtonPressEvent",
            self._on_right_click,
            1
        )
        # install event filter for double-clicks
        self.vtkWidget.installEventFilter(self)
        self.parent.sliceChanged.connect(self._onSliceChanged)
    
    def _onSliceChanged(self, orientation, indices):
        # indices is [idx0, idx1, idx2, idx3]
        # just recompute your stats/plots against the new slice positions:
        self._update_stats()
    
    def eventFilter(self, obj, event):
        if obj is self.vtkWidget and event.type() == QtCore.QEvent.MouseButtonDblClick:
            # only if ROI exists and is visible
            if not (self.polySrc and self.is_visible):
                return False

            # compute display center
            cx, cy, cz = self._last_center
            coord = vtk.vtkCoordinate()
            coord.SetCoordinateSystemToWorld()
            coord.SetValue(cx, cy, cz)
            disp_center = coord.GetComputedDisplayValue(self.renderer)

            # compute display radii
            coord.SetValue(cx + self._last_rx, cy, cz)
            disp_rx = abs(coord.GetComputedDisplayValue(self.renderer)[0] - disp_center[0])
            coord.SetValue(cx, cy + self._last_ry, cz)
            disp_ry = abs(coord.GetComputedDisplayValue(self.renderer)[1] - disp_center[1])

            # get click position in VTK coords
            click_x = event.pos().x()
            click_y = event.pos().y()
            w, h = self.renWin.GetSize()
            # VTK's y-origin is bottom
            click_y_inv = h - click_y

            dx = click_x - disp_center[0]
            dy = click_y_inv - disp_center[1]
            # ellipse equation test (normalized)
            if (dx/disp_rx)**2 + (dy/disp_ry)**2 <= 1.0:
                show_roi_plots(
                    parent=self.parent,
                    display_data=self.parent.display_data,
                    Im_Offset=self.parent.Im_Offset,
                    pixel_spac=self.parent.pixel_spac,
                    slice_thick=self.parent.slice_thick,
                    orientation=self.orientation,
                    center=self._last_center,
                    radii=(self._last_rx, self._last_ry),  # approximate
                    roi_type='ellipse',
                    window_title="Ellipsoid ROI Histogram",
                    return_dialog = False  
                )
                return True
            return False
        return super().eventFilter(obj, event)

    def _get_view_center_world(self):
        w,h = self.renWin.GetSize()
        cx,cy = w/2,h/2
        self.renderer.SetDisplayPoint(cx,cy,0)
        self.renderer.DisplayToWorld()
        x,y,z,w4 = self.renderer.GetWorldPoint()
        if w4: x,y = x/w4,y/w4
        # lift above slice
        z = self.imageActor.GetCenter()[2] + 1.0
        return x,y,z

    def _setup_ellipse(self):
        if self.polySrc or not getattr(self.parent,'display_data',None):
            return

        # base circle: radius=1, we'll scale it
        center = self._get_view_center_world()
        self._last_center = center
        bounds = self.imageActor.GetBounds()
        width  = bounds[1]-bounds[0]
        height = bounds[3]-bounds[2]
        # 10% of smaller dim
        self._last_rx = width*0.1
        self._last_ry = height*0.1

        # polygon source of unit radius
        self.polySrc = vtk.vtkRegularPolygonSource()
        self.polySrc.SetNumberOfSides(60)
        self.polySrc.SetCenter(0,0,0)
        self.polySrc.SetRadius(1.0)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.polySrc.GetOutputPort())
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.SetScale(self._last_rx, self._last_ry, 1)
        self.actor.SetPosition(*center)
        self.actor.GetProperty().SetColor(0,1,0)
        self.actor.GetProperty().SetOpacity(0.3)
        self.renderer.AddActor(self.actor)

        # handles: center, east, north
        for name,offs in [('center',(0,0)),('east',(1,0)),('north',(0,1))]:
            rep = vtk.vtkPointHandleRepresentation3D()
            rep.SetHandleSize(12)
            rep.GetProperty().SetColor(1,0,0)
                # if this is the center handle, hide it:
            if name == 'center':
                rep.GetProperty().SetOpacity(0.0)     # invisible
                rep.SetPickable(True)     # still respond to clicks
            else:
                rep.GetProperty().SetOpacity(1.0)     # visible
            widget = vtk.vtkHandleWidget()
            widget.SetRepresentation(rep)
            widget.SetInteractor(self.interactor)
            widget.AddObserver('InteractionEvent',
                               lambda w,e,n=name: self._on_handle_move(n))
            widget.On()
            self.handles[name] = widget

        # stats text
        self.statsActor = vtk.vtkTextActor()
        tp = self.statsActor.GetTextProperty()
        tp.SetFontSize(self.parent.selected_font_size)
        tp.SetColor(1,1,0)
        tp.SetBackgroundColor(0, 0, 0)
        tp.SetBackgroundOpacity(0.5)
        self.statsActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.statsActor.SetPosition(0.70,0.10)
        self.renderer.AddActor(self.statsActor)

        # stats picking
        self._stats_picker = vtk.vtkPropPicker()
        self.interactor.AddObserver("LeftButtonPressEvent",   self._on_stats_press,   1)
        self.interactor.AddObserver("MouseMoveEvent",         self._on_stats_drag,    1)
        self.interactor.AddObserver("LeftButtonReleaseEvent", self._on_stats_release,1)

        # circle dragging
        self._picker = vtk.vtkPropPicker()
        self.interactor.AddObserver("LeftButtonPressEvent",   self._on_press)
        self.interactor.AddObserver("MouseMoveEvent",         self._on_drag)
        self.interactor.AddObserver("LeftButtonReleaseEvent", self._on_release)

        # position handles & stats
        self._update_handles()
        self._update_stats()
        self.renWin.Render()

    # — stats dragging —
    def _on_stats_press(self, caller, event):
        x,y = self.interactor.GetEventPosition()
        self._stats_picker.Pick(x,y,0,self.renderer)
        if self._stats_picker.GetActor2D() is self.statsActor:
            self._dragging_stats = True
            self.parent._text_dragging = True
            self._stats_start = (x,y)
            disp = self.statsActor.GetPositionCoordinate().GetComputedDisplayValue(self.renderer)
            self._stats_orig_pix = (disp[0],disp[1])

    def _on_stats_drag(self, caller, event):
        if not self._dragging_stats: return
        x,y = self.interactor.GetEventPosition()
        dx,dy = x-self._stats_start[0], y-self._stats_start[1]
        w,h = self.renWin.GetSize()
        nx = (self._stats_orig_pix[0]+dx)/w
        ny = (self._stats_orig_pix[1]+dy)/h
        self.statsActor.GetPositionCoordinate().SetValue(nx,ny)
        self.renWin.Render()

    def _on_stats_release(self, caller, event):
        self._dragging_stats = False

    # — ellipse dragging & handle moves —
    def _on_press(self, caller, event):
        if self._dragging_stats: return
        x,y = self.interactor.GetEventPosition()
        self._picker.Pick(x,y,0,self.renderer)
        if self._picker.GetActor() is self.actor:
            self._dragging_center = True
            self.parent._text_dragging = True
            wx,wy,_ = self._get_world_point(x,y)
            cx,cy,_ = self._last_center
            self._drag_offset = (cx-wx, cy-wy)

    def _on_drag(self, caller, event):
        if self._dragging_stats: return
        x,y = self.interactor.GetEventPosition()
        if self._dragging_center:
            wx,wy,_ = self._get_world_point(x,y)
            dx,dy = self._drag_offset
            newc = (wx+dx, wy+dy, self._last_center[2])
            self._last_center = newc
            self.actor.SetPosition(*newc)
            self._update_handles()
            self._update_stats()
            self.renWin.Render()

    def _on_release(self, caller, event):
        self._dragging_center = False
        self.parent._text_dragging = False

    def _on_handle_move(self, name):
        cx,cy,cz = self._last_center
        ex,ey,_ = self.handles[name].GetRepresentation().GetWorldPosition()

        if name=='east':
            self._last_rx = abs(ex-cx)
        elif name=='north':
            self._last_ry = abs(ey-cy)
        # center handle move is same as dragging_center
        # update actor scale & position
        self.actor.SetScale(self._last_rx, self._last_ry, 1)
        self.actor.SetPosition(cx,cy,cz)
        self._update_handles()
        self._update_stats()
        self.renWin.Render()

    def _update_handles(self):
        cx,cy,cz = self._last_center
        self.handles['center'].GetRepresentation().SetWorldPosition((cx,cy,cz))
        self.handles['east'  ].GetRepresentation().SetWorldPosition((cx+self._last_rx,cy,cz))
        self.handles['north' ].GetRepresentation().SetWorldPosition((cx,cy+self._last_ry,cz))

    def _get_world_point(self,x,y):
        self.renderer.SetDisplayPoint(x,y,0)
        self.renderer.DisplayToWorld()
        wp = self.renderer.GetWorldPoint()
        if wp[3]!=0.0:
            return wp[0]/wp[3], wp[1]/wp[3], wp[2]/wp[3]
        return wp[0],wp[1],wp[2]

    def _update_stats(self):
        rx, ry = self._last_rx, self._last_ry
        area = math.pi*rx*ry
        lines = [f"Rx={rx:.1f} mm   Ry={ry:.1f} mm   A={area:.1f} mm²"]

        for idx,data in self.parent.display_data.items():
            if data is None or not hasattr(data,'ndim'):
                lines.append(f"Layer {idx}: ∅")
                continue

            # select slice by orientation
            if data.ndim==2:
                slc = data
            else:
                if   self.orientation=='axial':
                    si = self.parent.current_axial_slice_index[idx]; slc = data[si,:,:]
                elif self.orientation=='coronal':
                    si = self.parent.current_coronal_slice_index[idx]; slc = data[:,si,:]
                else:
                    si = self.parent.current_sagittal_slice_index[idx]; slc = data[:,:,si]

            h,w = slc.shape
            ox,oy,_ = self._last_center

            # map to pixel depending on orientation
            if self.orientation=='axial':
                px = (ox - self.parent.Im_Offset[idx,0]) / self.parent.pixel_spac[idx,0]
                py = (oy - self.parent.Im_Offset[idx,1]) / self.parent.pixel_spac[idx,1]
            elif self.orientation=='coronal':
                px = (ox - self.parent.Im_Offset[idx,0]) / self.parent.pixel_spac[idx,0]
                py = (oy - self.parent.Im_Offset[idx,2]) / self.parent.slice_thick[idx]
            else:
                px = (ox - self.parent.Im_Offset[idx,1]) / self.parent.pixel_spac[idx,1]
                py = (oy - self.parent.Im_Offset[idx,2]) / self.parent.slice_thick[idx]

            px = int(round(np.clip(px,0,w-1)))
            py = int(round(np.clip(py,0,h-1)))

            rpx = int(round(rx / self.parent.pixel_spac[idx,0]))
            rpy = int(round(ry / self.parent.pixel_spac[idx,1]))

            yy,xx = np.ogrid[:h,:w]
            mask = ((xx-px)/rpx)**2 + ((yy-py)/rpy)**2 <= 1.0
            vals = slc[mask]

            if vals.size:
                μ,σ = vals.mean(), vals.std()
                lines.append(f"Layer {idx}: Mean {μ:.1f} STD {σ:.1f}")
            else:
                lines.append(f"Layer {idx}: ∅")

        txt = "\n".join(lines)
        self.statsActor.SetInput(txt)
        self.statsActor.Modified()
        self.statsActor.SetVisibility(True)

    def toggle(self):
        # if we haven’t yet created the ellipse (or there’s no image loaded), try to set it up
        if self.actor is None:
            self._setup_ellipse()
            # if setup still didn’t yield an actor, bail out silently
            if self.actor is None:
                return

        # now flip visibility
        self.is_visible = not self.is_visible
        self.actor.SetVisibility(self.is_visible)
        for h in self.handles.values():
            if self.is_visible:
                h.On()
            else:
                h.Off()
        self.statsActor.SetVisibility(self.is_visible)
        self.renWin.Render()


    # optional appearance
    def set_fill_color(self, r,g,b,a=0.3):
        p = self.actor.GetProperty(); p.SetColor(r,g,b); p.SetOpacity(a); self.renWin.Render()
    def set_edge_color(self, r,g,b):
        p = self.actor.GetProperty(); p.SetEdgeColor(r,g,b); p.EdgeVisibilityOn(); self.renWin.Render()

    def _on_right_click(self, caller, event):
        x, y = self.interactor.GetEventPosition()
        # pick the 3D ROI actor
        self._picker_right.Pick(x, y, 0, self.renderer)
        picked_3d = self._picker_right.GetActor()
        # pick the 2D stats box
        self._stats_picker.Pick(x, y, 0, self.renderer)
        picked_text = (self._stats_picker.GetActor2D() is self.statsActor)

        # if they hit either, delete this ROI
        if picked_3d is self.actor or picked_3d is self.polySrc_actor or picked_text:
            self.delete()

    def delete(self):
        # 1) hide if visible
        if self.is_visible:
            self.toggle()
        # 2) remove the main actor
        if hasattr(self, 'actor') and self.actor:
            self.renderer.RemoveActor(self.actor)
        if hasattr(self, 'squareActor') and self.squareActor:
            self.renderer.RemoveActor(self.squareActor)
        # 3) remove stats text
        if self.statsActor:
            self.renderer.RemoveActor(self.statsActor)
        # 4) disable all handle-widgets
        for hw in self.handles.values():
            hw.Off()
        # 5) re-render
        self.renWin.Render()
        # 6) unregister from parent list
        if hasattr(self.parent, 'ellipses') and self in self.parent.ellipses:
            self.parent.ellipses.remove(self)
        if hasattr(self.parent, 'squares')  and self in self.parent.squares:
            self.parent.squares.remove(self)



class SquareRoiWidget(QtCore.QObject):
    """
    Rectangle ROI widget (named SquareRoiWidget for legacy). Users can adjust width and height independently.
    Supports dragging of the stats text box like Circle/Ellipse.
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

        # geometry & state
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


        # vertical line (world Y extents will be set on update)
        self._vline_src = vtk.vtkLineSource()
        self._vline_mapper = vtk.vtkPolyDataMapper()
        self._vline_mapper.SetInputConnection(self._vline_src.GetOutputPort())
        self._vline_actor = vtk.vtkActor()
        self._vline_actor.SetMapper(self._vline_mapper)
        self._vline_actor.GetProperty().SetColor(1,0,0)
        self._vline_actor.SetVisibility(False)
        self._vline_actor.GetProperty().SetLineWidth(3)
        self.renderer.AddActor(self._vline_actor)

        # horizontal line
        self._hline_src = vtk.vtkLineSource()
        self._hline_mapper = vtk.vtkPolyDataMapper()
        self._hline_mapper.SetInputConnection(self._hline_src.GetOutputPort())
        self._hline_actor = vtk.vtkActor()
        self._hline_actor.SetMapper(self._hline_mapper)
        self._hline_actor.GetProperty().SetColor(1,0,0)
        self._hline_actor.SetVisibility(False)
        self._vline_actor.GetProperty().SetLineWidth(3)
        self.renderer.AddActor(self._hline_actor)

        # install event filter for double-click on ROI
        self.vtkWidget.installEventFilter(self)
        # register stats-drag events at init
        self.interactor.AddObserver("LeftButtonPressEvent",   self._on_stats_press,   1)
        self.interactor.AddObserver("MouseMoveEvent",         self._on_stats_drag,    1)
        self.interactor.AddObserver("LeftButtonReleaseEvent", self._on_stats_release, 1)
        #
        self.parent.sliceChanged.connect(self._onSliceChanged)
    
    def _onSliceChanged(self, orientation, indices):
        # indices is [idx0, idx1, idx2, idx3]
        # just recompute your stats/plots against the new slice positions:
        self._update_stats()

    def _setup_square(self):
        if self.squareSrc:
            return
        #
        # —————— profile‐line actors ——————

        # initialize center & half-sizes to 10% of image bbox
        cx, cy, cz = self._get_view_center_world()
        self._last_center = (cx, cy, cz)
        b = self.imageActor.GetBounds()
        base = min(b[1]-b[0], b[3]-b[2])
        self._last_rx = self._last_ry = base * 0.1

        # create vtkPlaneSource as rectangle
        self.squareSrc = vtk.vtkPlaneSource()
        self._update_plane()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.squareSrc.GetOutputPort())
        self.squareActor = vtk.vtkActor()
        self.squareActor.SetMapper(mapper)
        self.squareActor.GetProperty().SetColor(0,1,0)
        self.squareActor.GetProperty().SetOpacity(0.3)
        self.renderer.AddActor(self.squareActor)

        # add mid-edge handles
        for name in ('north','south','east','west'):
            rep = vtk.vtkPointHandleRepresentation3D()
            rep.SetHandleSize(10)
            rep.GetProperty().SetColor(1,0,0)
            handle = vtk.vtkHandleWidget()
            handle.SetRepresentation(rep)
            handle.SetInteractor(self.interactor)
            handle.AddObserver('InteractionEvent', lambda w,e,n=name: self._on_handle_move(n))
            handle.On()
            self.handles[name] = handle

        # add stats text actor
        self.statsActor = vtk.vtkTextActor()
        tp = self.statsActor.GetTextProperty()
        tp.SetFontSize(self.parent.selected_font_size)
        tp.SetColor(1,1,0)
        tp.SetBackgroundColor(0,0,0)
        tp.SetBackgroundOpacity(0.5)
        self.statsActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.statsActor.SetPosition(0.7,0.1)
        self.renderer.AddActor(self.statsActor)

        # register move & resize events
        self.interactor.AddObserver('LeftButtonPressEvent',   self._on_press)
        self.interactor.AddObserver('MouseMoveEvent',         self._on_drag)
        self.interactor.AddObserver('LeftButtonReleaseEvent', self._on_release)

        # picker for right-click deletion
        self._picker_right = vtk.vtkPropPicker()
        self.interactor.AddObserver(
            "RightButtonPressEvent",
            self._on_right_click,
            1
        )
        # initial draw
        self._update_handles()
        self._update_stats()
        self.renWin.Render()

    def _get_view_center_world(self):
        """Return (x,y,z) of viewport center in world coords."""
        w, h = self.renWin.GetSize()
        cx, cy = w/2, h/2
        self.renderer.SetDisplayPoint(cx, cy, 0)
        self.renderer.DisplayToWorld()
        x, y, z, w4 = self.renderer.GetWorldPoint()
        if w4:
            x, y = x/w4, y/w4
        # lift above image plane
        z = self.imageActor.GetCenter()[2] + 1.0
        return x, y, z
    
    def eventFilter(self, obj, event):
        # detect double-click inside ROI to pop plots
        if obj is self.vtkWidget and event.type() == QtCore.QEvent.MouseButtonDblClick:
            if not (self.squareSrc and self.is_visible):
                return False
            cx, cy, cz = self._last_center
            coord = vtk.vtkCoordinate()
            coord.SetCoordinateSystemToWorld(); coord.SetValue(cx, cy, cz)
            dc = coord.GetComputedDisplayValue(self.renderer)
            # display radii
            coord.SetValue(cx+self._last_rx, cy, cz)
            drx = abs(coord.GetComputedDisplayValue(self.renderer)[0]-dc[0])
            coord.SetValue(cx, cy+self._last_ry, cz)
            dry = abs(coord.GetComputedDisplayValue(self.renderer)[1]-dc[1])
            x, y = event.pos().x(), event.pos().y()
            y = self.renWin.GetSize()[1] - y
            if abs(x-dc[0])<=drx and abs(y-dc[1])<=dry:
                # 1) create & show the ROI‐plots dialog *but do not exec it yet*
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
                    return_dialog = True     # ← new flag
                )

                # 2) turn on our cross‐hair lines
                self._vline_actor.SetVisibility(True)
                self._hline_actor.SetVisibility(True)
                self.renWin.Render()

                # 3) hook the sliders up to our line‐move methods
                dlg.sld_x.valueChanged.connect(self._onProfileXChanged)
                dlg.sld_y.valueChanged.connect(self._onProfileYChanged)

                # 4) when the dialog closes, hide the lines again
                dlg.finished.connect(self._hideProfileLines)

                # 5) now exec
                dlg.exec_()
                return True
            return False
        return super().eventFilter(obj, event)
    

    def _onProfileXChanged(self, x_mm: int):
        """Move vertical line to world-X = x_mm, spanning current ROI Y extents."""
        cx, cy, cz = self._last_center
        ry = self._last_ry
        # line from (x_mm, cy-ry) to (x_mm, cy+ry)
        self._vline_src.SetPoint1(x_mm, cy-ry, cz)
        self._vline_src.SetPoint2(x_mm, cy+ry, cz)
        self._vline_src.Update()
        self.renWin.Render()

    def _onProfileYChanged(self, y_mm: int):
        """Move horizontal line to world-Y = y_mm, spanning current ROI X extents."""
        cx, cy, cz = self._last_center
        rx = self._last_rx
        # line from (cx-rx, y_mm) to (cx+rx, y_mm)
        self._hline_src.SetPoint1(cx-rx, y_mm, cz)
        self._hline_src.SetPoint2(cx+rx, y_mm, cz)
        self._hline_src.Update()
        self.renWin.Render()

    def _hideProfileLines(self):
        """Hide both profile lines."""
        self._vline_actor.SetVisibility(False)
        self._hline_actor.SetVisibility(False)
        self.renWin.Render()


    # stats dragging handlers
    def _on_stats_press(self, caller, event):
        x, y = self.interactor.GetEventPosition()
        self._stats_picker.Pick(x, y, 0, self.renderer)
        if self._stats_picker.GetActor2D() is self.statsActor:
            self._dragging_stats = True
            self.parent._text_dragging = True
            self._stats_start    = (x, y)
            disp = self.statsActor.GetPositionCoordinate().GetComputedDisplayValue(self.renderer)
            self._stats_orig_pix = (disp[0], disp[1])

    def _on_stats_drag(self, caller, event):
        if not self._dragging_stats:
            return
        x, y = self.interactor.GetEventPosition()
        dx = x - self._stats_start[0]; dy = y - self._stats_start[1]
        w, h = self.renWin.GetSize()
        self.statsActor.GetPositionCoordinate().SetValue(
            (self._stats_orig_pix[0]+dx)/w,
            (self._stats_orig_pix[1]+dy)/h
        )
        self.renWin.Render()

    def _on_stats_release(self, caller, event):
        self._dragging_stats = False
        self.parent._text_dragging = False

    # press/drag/release for ROI move
    def _on_press(self, caller, event):
        if self._dragging_stats:
            return
        x,y = self.interactor.GetEventPosition()
        self._picker.Pick(x,y,0,self.renderer)
        if self._picker.GetActor() is self.squareActor:
            self._dragging_center = True
            self.parent._text_dragging = True
            wx,wy,_ = self._get_world_point(x,y)
            cx,cy,_ = self._last_center
            self._drag_offset = (cx-wx, cy-wy)

    def _on_drag(self, caller, event):
        if not self._dragging_center:
            return
        x,y = self.interactor.GetEventPosition()
        wx,wy,_ = self._get_world_point(x,y)
        dx,dy = self._drag_offset
        self._last_center = (wx+dx, wy+dy, self._last_center[2])
        self._update_plane(); self._update_handles(); self._update_stats(); self.renWin.Render()

    def _on_release(self, caller, event):
        self._dragging_center = False
        self.parent._text_dragging = False

    def _update_plane(self):
        cx, cy, cz = self._last_center; rx, ry = self._last_rx, self._last_ry
        self.squareSrc.SetOrigin(cx-rx, cy-ry, cz)
        self.squareSrc.SetPoint1(cx+rx, cy-ry, cz)
        self.squareSrc.SetPoint2(cx-rx, cy+ry, cz)
        self.squareSrc.Update()

    def _on_handle_move(self, name):
        cx, cy, cz = self._last_center
        ex, ey, _ = self.handles[name].GetRepresentation().GetWorldPosition()
        if name in ('north','south'):
            self._last_ry = abs(ey-cy)
        else:
            self._last_rx = abs(ex-cx)
        self._update_plane(); self._update_handles(); self._update_stats(); self.renWin.Render()

    def _update_handles(self):
        cx,cy,cz = self._last_center; rx, ry = self._last_rx, self._last_ry
        positions = {'north':(cx,cy+ry,cz),'south':(cx,cy-ry,cz),'east':(cx+rx,cy,cz),'west':(cx-rx,cy,cz)}
        for n,p in positions.items():
            self.handles[n].GetRepresentation().SetWorldPosition(p)

    def _get_world_point(self, x, y):
        self.renderer.SetDisplayPoint(x, y, 0); self.renderer.DisplayToWorld()
        wp = self.renderer.GetWorldPoint()
        if wp[3]!=0: return (wp[0]/wp[3], wp[1]/wp[3], wp[2])
        return (wp[0], wp[1], wp[2])

    def _update_stats(self):
        rx, ry = self._last_rx, self._last_ry
        area = (2*rx)*(2*ry)
        lines = [f"W={2*rx:.1f} H={2*ry:.1f} A={area:.1f} mm²"]
        for idx, data in self.parent.display_data.items():
            if data is None or not hasattr(data, 'ndim'):
                lines.append(f"Layer {idx}: ∅")
                continue

            # pick correct slice
            if data.ndim == 2:
                slc = data
            else:
                if self.orientation == 'axial':
                    si = self.parent.current_axial_slice_index[idx]
                    slc = data[si, :, :]
                elif self.orientation == 'coronal':
                    si = self.parent.current_coronal_slice_index[idx]
                    slc = data[:, si, :]
                else:  # sagittal
                    si = self.parent.current_sagittal_slice_index[idx]
                    slc = data[:, :, si]

            h, w = slc.shape
            ox, oy, _ = self._last_center

            # world→pixel mapping
            if self.orientation == 'axial':
                px = (ox - self.parent.Im_Offset[idx,0]) / self.parent.pixel_spac[idx,0]
                py = (oy - self.parent.Im_Offset[idx,1]) / self.parent.pixel_spac[idx,1]
            elif self.orientation == 'coronal':
                px = (ox - self.parent.Im_Offset[idx,0]) / self.parent.pixel_spac[idx,0]
                py = (oy - self.parent.Im_Offset[idx,2]) / self.parent.slice_thick[idx]
            else:
                px = (ox - self.parent.Im_Offset[idx,1]) / self.parent.pixel_spac[idx,1]
                py = (oy - self.parent.Im_Offset[idx,2]) / self.parent.slice_thick[idx]

            px = int(round(np.clip(px, 0, w-1)))
            py = int(round(np.clip(py, 0, h-1)))

            # convert radii to pixel
            rpx = int(round(rx / self.parent.pixel_spac[idx,0]))
            rpy = int(round(ry / self.parent.pixel_spac[idx,1]))

            yy, xx = np.ogrid[:h, :w]
            mask = ((xx - px)/rpx)**2 + ((yy - py)/rpy)**2 <= 1.0
            vals = slc[mask]

            if vals.size:
                μ, σ = vals.mean(), vals.std()
                lines.append(f"Layer {idx}: Mean {μ:.1f} STD {σ:.1f}")
            else:
                lines.append(f"Layer {idx}: ∅")

        # finally:
        self.statsActor.SetInput("\n".join(lines))
        self.statsActor.Modified()
        self.statsActor.SetVisibility(True)

    def toggle(self):
        if not self.squareSrc:
            self._setup_square()
        self.is_visible = not self.is_visible
        self.squareActor.SetVisibility(self.is_visible)
        for h in self.handles.values(): h.On() if self.is_visible else h.Off()
        self.statsActor.SetVisibility(self.is_visible); self.statsActor.Modified(); self.renWin.Render()

    def _on_right_click(self, caller, event):
        x, y = self.interactor.GetEventPosition()
        # 3D pick on the rectangle actor
        self._picker_right.Pick(x, y, 0, self.renderer)
        picked = self._picker_right.GetActor()
        # 2D pick on the stats text
        self._stats_picker.Pick(x, y, 0, self.renderer)
        picked_text = (self._stats_picker.GetActor2D() is self.statsActor)

        if picked is self.squareActor or picked_text:
            self.delete()

    def delete(self):
        # hide if visible
        if self.is_visible:
            self.toggle()
        # remove the rectangle actor
        if self.squareActor:
            self.renderer.RemoveActor(self.squareActor)
        # remove the stats text
        if self.statsActor:
            self.renderer.RemoveActor(self.statsActor)
        # turn off all handles
        for hw in self.handles.values():
            hw.Off()
        # re-render
        self.renWin.Render()
        # unregister from parent list
        if hasattr(self.parent, 'squares') and self in self.parent.squares:
            self.parent.squares.remove(self)