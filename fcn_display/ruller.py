# fcn_display/ruller.py

import vtk
import math
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleUser

class RulerWidget:
    def __init__(self, vtk_widget, renderer, parent, image_actor):
        """
        vtk_widget:       QVTKRenderWindowInteractor for this view
        renderer:         corresponding vtkRenderer
        parent:           main window with display_data etc.
        image_actor:      vtkImageActor showing the DICOM image in this view
        """
        self.vtkWidget   = vtk_widget
        self.renderer    = renderer
        self.renWin      = vtk_widget.GetRenderWindow()
        self.parent      = parent
        self.imageActor  = image_actor
        self.interactor  = self.renWin.GetInteractor()
        self.lineSource  = None       # created on first toggle
        self.halfLength  = 10.0       # mm on each side (total 20 mm)
        self.z_offset    = 1.0        # mm above image plane
        self.is_visible  = False
        self._text_dragging = False         # local to be used within the class one per object
        self.parent._text_dragging = False  # to avoid conflicts with text dragging and window level - global
        

    def _get_view_center_world(self):
        """Return (x,y) in world coordinates of the viewport center."""
        width, height = self.renWin.GetSize()
        cx = width  / 2
        cy = height / 2
        self.halfLength  = cx/5
        self.renderer.SetDisplayPoint(cx, cy, 0)
        self.renderer.DisplayToWorld()
        wp = self.renderer.GetWorldPoint()
        if wp[3] != 0.0:
            return (wp[0]/wp[3], wp[1]/wp[3])
        return (wp[0], wp[1])

    def _setup_ruler(self):
        # only once, and only after images are loaded
        if self.lineSource or not getattr(self.parent, 'display_data', None):
            return

        # create line source & actor
        self.lineSource = vtk.vtkLineSource()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.lineSource.GetOutputPort())
        self.lineActor = vtk.vtkActor()
        self.lineActor.SetMapper(mapper)
        prop = self.lineActor.GetProperty()
        prop.SetColor(1, 0, 0)              # red
        prop.SetLineStipplePattern(0xF0F0)  # dashed
        prop.SetLineWidth(2)
        prop.SetRenderLinesAsTubes(True)    # optional, to draw on top
        self.renderer.AddActor(self.lineActor)

        # endpoint circles
        for idx in (1, 2):
            poly = vtk.vtkRegularPolygonSource()
            poly.SetNumberOfSides(20)
            poly.SetRadius(3)
            setattr(self, f'poly{idx}', poly)
            pm = vtk.vtkPolyDataMapper()
            pm.SetInputConnection(poly.GetOutputPort())
            actor = vtk.vtkActor()
            actor.SetMapper(pm)
            actor.GetProperty().SetColor(1, 0, 0)
            actor.GetProperty().SetOpacity(0.5)
            setattr(self, f'actor{idx}', actor)
            self.renderer.AddActor(actor)

        # handles
        for idx in (1, 2):
            rep = vtk.vtkPointHandleRepresentation3D()
            rep.SetHandleSize(10)
            rep.SetWorldPosition((0,0,0))  # will recenter
            handle = vtk.vtkHandleWidget()
            handle.SetInteractor(self.interactor)
            handle.SetRepresentation(rep)
            handle.AddObserver('InteractionEvent', lambda w,e,i=idx: self._on_handle_move(i))
            handle.On()
            setattr(self, f'handle{idx}', handle)

        # measurement text
        self.textActor = vtk.vtkTextActor()
        tp = self.textActor.GetTextProperty()
        tp.SetFontSize(self.parent.selected_font_size)
        tp.SetColor(1, 1, 0)
        tp.SetBackgroundColor(0, 0, 0)
        tp.SetBackgroundOpacity(0.5)
        self.textActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.textActor.SetPosition(0.05, 0.90)
        self.textActor.SetInput("0.00 mm")
        self.renderer.AddActor(self.textActor)
        self.picker        = vtk.vtkPropPicker()
        self._text_dragging = False
        self._drag_start   = (0, 0)
        coord = self.textActor.GetPositionCoordinate()
        self._text_orig    = (coord.GetValue()[0], coord.GetValue()[1])

        self.interactor.AddObserver("LeftButtonPressEvent",   self._on_text_press)
        self.interactor.AddObserver("MouseMoveEvent",         self._on_text_move)
        self.interactor.AddObserver("LeftButtonReleaseEvent", self._on_text_release)

        # initial center
        self._recenter_line()

    def _on_text_press(self, caller, event):
        x, y = self.interactor.GetEventPosition()
        self.picker.Pick(x, y, 0, self.renderer)
        if self.picker.GetActor2D() is self.textActor:
            self.parent._text_dragging = True
            self._text_dragging = True
            self._drag_start    = (x, y)
            coord = self.textActor.GetPositionCoordinate()
            self._text_orig     = (coord.GetValue()[0], coord.GetValue()[1])

    def _on_text_move(self, caller, event):
        if not self._text_dragging:
            return
        x, y = self.interactor.GetEventPosition()
        dx = (x - self._drag_start[0]) / self.renWin.GetSize()[0]
        dy = (y - self._drag_start[1]) / self.renWin.GetSize()[1]
        new_x = self._text_orig[0] + dx
        new_y = self._text_orig[1] + dy
        self.textActor.GetPositionCoordinate().SetValue(new_x, new_y)
        self.renWin.Render()

    def _on_text_release(self, caller, event):
        self.parent._text_dragging = False
        self._text_dragging = False


    def _on_handle_move(self, idx):
        rep = getattr(self, f'handle{idx}').GetRepresentation()
        pos = [0.0, 0.0, 0.0]
        rep.GetWorldPosition(pos)
        if idx == 1:
            self.lineSource.SetPoint1(pos)
        else:
            self.lineSource.SetPoint2(pos)
        self.lineSource.Modified()
        getattr(self, f'poly{idx}').SetCenter(pos)
        getattr(self, f'actor{idx}').SetPosition(0, 0, 0)
        self._update_measure()

    def _update_measure(self):
        p1 = self.lineSource.GetPoint1()
        p2 = self.lineSource.GetPoint2()
        dist = math.dist(p1, p2)
        self.textActor.SetInput(f"{dist:.2f} mm")
        self.vtkWidget.GetRenderWindow().Render()

    def _recenter_line(self):
        # center the ruler on the *visible* viewport
        x, y = self._get_view_center_world()
        z = self.imageActor.GetCenter()[2] + self.z_offset
        p1 = (x - self.halfLength, y, z)
        p2 = (x + self.halfLength, y, z)
        self.lineSource.SetPoint1(p1)
        self.lineSource.SetPoint2(p2)
        self.lineSource.Modified()
        # reposition circles
        self.poly1.SetCenter(p1)
        self.actor1.SetPosition(0, 0, 0)
        self.poly2.SetCenter(p2)
        self.actor2.SetPosition(0, 0, 0)
        # reposition handles
        self.handle1.GetRepresentation().SetWorldPosition(p1)
        self.handle2.GetRepresentation().SetWorldPosition(p2)
        self._update_measure()

    def toggle(self):
        # first click: set up
        if self.lineSource is None:
            self._setup_ruler()
            self.is_visible = True
            return
        # toggle on/off
        newVis = not self.is_visible
        if newVis:
            self._recenter_line()
        for name in ('lineActor', 'actor1', 'actor2', 'textActor'):
            getattr(self, name).SetVisibility(newVis)
        if newVis:
            self.handle1.On()
            self.handle2.On()
        else:
            self.handle1.Off()
            self.handle2.Off()
        self.is_visible = newVis
        self.vtkWidget.GetRenderWindow().Render()
