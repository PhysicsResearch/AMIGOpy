import os
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import Qt,  QSize
from PyQt5.QtGui import   QIcon, QFont
from PyQt5.QtWidgets import QToolButton, QToolTip
from fcn_display.ruller import RulerWidget
from fcn_display.dicom_info import open_dicom_tag_viewer
from fcn_display.circ_ell_roi import CircleRoiWidget, EllipsoidRoiWidget, SquareRoiWidget

def menu_bar_icon_actions(self, base_path):
# ruler       """Add actions to the menu bar with icons."""
# keep adding and remove ruler  (two buttoms)

# 1) Globally increase tooltip font size (optional)
    QToolTip.setFont(QFont("SansSerif", 12))   # adjust point-size as you like

# DICOM inspect ----------------------------------
    # Add a button/action with an icon - Dicom Inspect
    icon_path = os.path.join(base_path, "icons", "dcm_insp.png")  # Adjusted path for icons
    button_action = QAction(QIcon(icon_path),(
        "<div style='font-size:12pt; text-align:left;'>"
        "Select a DICOM file to inspect the <b>Header</b>"
        "</div>"
    ), self)
    button_action.setStatusTip(
        "<div style='font-size:12pt; text-align:left;'>"
        "Select a DICOM file to inspect the <b>Header</b>"
        "</div>"
    )
    button_action.triggered.connect(lambda:open_dicom_tag_viewer())
    self.viewer = None

    # Optional: Set a fixed size for the action to make it more squared
    self.toolbar.setIconSize(QSize(50, 50))  # Adjust size as needed
    self.toolbar.addAction(button_action)
    self.selected_point = None

# Ruler ----------------------------------
    icon = QIcon(os.path.join(base_path, "icons", "ruler.png"))

    tb = QToolButton(self)
    tb.setIcon(icon)
    # 2) Use HTML for a 2-line tooltip and inline font sizing
    tb.setToolTip(
        "<div style='font-size:12pt; text-align:left;'>"
        "Left-click to <b>add</b> ruler<br/>"
        "Right-click to <b>remove</b> all rulers"
        "</div>"
    )
    tb.setIconSize(QSize(50,50))

    # left-click = add another ruler
    tb.clicked.connect(lambda: add_ruler(self))

    # right-click = remove all rulers
    def on_right_click(pos):
        # directly remove, no menu needed
        remove_rulers(self)

    # we only care about the button press, not a menu
    tb.setContextMenuPolicy(Qt.CustomContextMenu)
    tb.customContextMenuRequested.connect(on_right_click)

    # put it in the toolbar
    self.toolbar.addSeparator()
    self.toolbar.addWidget(tb)

# Circle ----------------------------------
    icon = QIcon(os.path.join(base_path, "icons", "roi_circle.png"))

    tb = QToolButton(self)
    tb.setIcon(icon)
    # 2) Use HTML for a 2-line tooltip and inline font sizing
    tb.setToolTip(
        "<div style='font-size:12pt; text-align:left;'>"
        "Left-click to <b>add</b> a circle<br/>"
        "Right-click to <b>remove</b> all circles"
        "</div>"
    )
    tb.setIconSize(QSize(50,50))

    # left-click = add another ruler
    tb.clicked.connect(lambda: add_circle(self))

    # right-click = remove all rulers
    def on_right_click(pos):
        # directly remove, no menu needed
        remove_circles(self)

    # we only care about the button press, not a menu
    tb.setContextMenuPolicy(Qt.CustomContextMenu)
    tb.customContextMenuRequested.connect(on_right_click)

    # put it in the toolbar
    self.toolbar.addWidget(tb)

# Ellipse ----------------------------------
    icon = QIcon(os.path.join(base_path, "icons", "roi_ellipse.png"))

    tb = QToolButton(self)
    tb.setIcon(icon)
    # 2) Use HTML for a 2-line tooltip and inline font sizing
    tb.setToolTip(
        "<div style='font-size:12pt; text-align:left;'>"
        "Left-click to <b>add</b> an ellipse<br/>"
        "Right-click to <b>remove</b> all ellipses"
        "</div>"
    )
    tb.setIconSize(QSize(50,50))

    # left-click = add another ruler
    tb.clicked.connect(lambda: add_ellipse(self))

    # right-click = remove all rulers
    def on_right_click(pos):
        # directly remove, no menu needed
        remove_ellipses(self)

    # we only care about the button press, not a menu
    tb.setContextMenuPolicy(Qt.CustomContextMenu)
    tb.customContextMenuRequested.connect(on_right_click)

    # put it in the toolbar
    self.toolbar.addWidget(tb)

# Square ----------------------------------
    icon = QIcon(os.path.join(base_path, "icons", "roi_square.png"))

    tb = QToolButton(self)
    tb.setIcon(icon)
    # 2) Use HTML for a 2-line tooltip and inline font sizing
    tb.setToolTip(
        "<div style='font-size:12pt; text-align:left;'>"
        "Left-click to <b>add</b> a square<br/>"
        "Right-click to <b>remove</b> all squares"
        "</div>"
    )
    tb.setIconSize(QSize(50,50))

    # left-click = add another ruler
    tb.clicked.connect(lambda: add_square(self))

    # right-click = remove all rulers
    def on_right_click(pos):
        # directly remove, no menu needed
        remove_squares(self)

    # we only care about the button press, not a menu
    tb.setContextMenuPolicy(Qt.CustomContextMenu)
    tb.customContextMenuRequested.connect(on_right_click)

    # put it in the toolbar
    self.toolbar.addWidget(tb)
    self.toolbar.addSeparator()

# Add interacgtive ROI widgets to the menu bar
# (e.g. CircleRoiWidget, EllipseRoiWidget, etc.)


def add_ruler(self):
    """Create & show a new ruler in the current view."""
    ruler = RulerWidget(self.vtkWidgetAxial, self.renAxial, self, self.imageActorAxial[0])
    ruler.toggle()            # show it immediately
    self.rulers.append(ruler)

    ruler = RulerWidget(self.vtkWidgetCoronal, self.renCoronal, self, self.imageActorCoronal[0])
    ruler.toggle()            # show it immediately
    self.rulers.append(ruler)

    ruler = RulerWidget(self.vtkWidgetSagittal, self.renSagittal, self, self.imageActorSagittal[0])
    ruler.toggle()            # show it immediately
    self.rulers.append(ruler)




def remove_rulers(self):
    """Hide, fully remove and delete *all* existing rulers."""
    for ruler in getattr(self, 'rulers', []):
        # hide the widget
        if ruler.is_visible:
            ruler.toggle()
        # remove all actors
        for actor_name in ('lineActor', 'actor1', 'actor2', 'textActor'):
            act = getattr(ruler, actor_name, None)
            if act:
                ruler.renderer.RemoveActor(act)
        # make sure the handle widgets are off
        for handle_name in ('handle1','handle2'):
            h = getattr(ruler, handle_name, None)
            if h:
                h.Off()
    # clear the list so we don't keep stale references
    self.rulers.clear()
    # trigger a re-render on each view
    for w in (self.vtkWidgetAxial, self.vtkWidgetSagittal, self.vtkWidgetCoronal):
        w.GetRenderWindow().Render()

def add_circle(self):
    """Create & show a new ruler in the current view."""
    circle = CircleRoiWidget(self.vtkWidgetAxial, self.renAxial, self, self.imageActorAxial[0],'axial')
    circle.toggle()            # show it immediately
    self.circle.append(circle)

    circle = CircleRoiWidget(self.vtkWidgetCoronal, self.renCoronal, self, self.imageActorCoronal[0], 'coronal')
    circle.toggle()            # show it immediately
    self.circle.append(circle)

    circle = CircleRoiWidget(self.vtkWidgetSagittal, self.renSagittal, self, self.imageActorSagittal[0], 'sagittal')
    circle.toggle()            # show it immediately
    self.circle.append(circle)



def remove_circles(self):
    """Hide, fully remove and delete *all* existing circular ROIs."""
    # if you stored them as self.circle = [CircleRoiWidget…]
    for roi in getattr(self, 'circle', []):
        # 1) hide it if it’s currently on-screen
        if roi.is_visible:
            roi.toggle()

        # 2) remove its actors from the renderer
        for actor_name in ('circleActor', 'actor1', 'actor2'):
            actor = getattr(roi, actor_name, None)
            if actor:
                roi.renderer.RemoveActor(actor)

        # 3) disable its handle‐widgets
        for hw in roi.handles.values():
            hw.Off()

    # 4) forget all the ROIs
    self.circle.clear()

    # 5) redraw each view
    for w in (self.vtkWidgetAxial,
              self.vtkWidgetSagittal,
              self.vtkWidgetCoronal):
        w.GetRenderWindow().Render()

# Ellipse ----------------------------------
def add_ellipse(self):
    """Create & show a new ellipse ROI in each view."""
    # Ensure the storage list exists
    if not hasattr(self, 'ellipses'):
        self.ellipses = []

    # Axial
    e = EllipsoidRoiWidget(
        self.vtkWidgetAxial, self.renAxial, self,
        self.imageActorAxial[0], 'axial'
    )
    e.toggle()
    self.ellipses.append(e)

    # Coronal
    e = EllipsoidRoiWidget(
        self.vtkWidgetCoronal, self.renCoronal, self,
        self.imageActorCoronal[0], 'coronal'
    )
    e.toggle()
    self.ellipses.append(e)

    # Sagittal
    e = EllipsoidRoiWidget(
        self.vtkWidgetSagittal, self.renSagittal, self,
        self.imageActorSagittal[0], 'sagittal'
    )
    e.toggle()
    self.ellipses.append(e)


def remove_ellipses(self):
    """Hide, fully remove, and delete *all* existing ellipse ROIs."""
    for roi in getattr(self, 'ellipses', []):
        # 1) hide it if visible
        if getattr(roi, 'is_visible', False):
            roi.toggle()

        # 2) remove its main actor
        if hasattr(roi, 'actor') and roi.actor:
            roi.renderer.RemoveActor(roi.actor)

        # 3) remove its stats text
        if hasattr(roi, 'statsActor') and roi.statsActor:
            roi.renderer.RemoveActor(roi.statsActor)

        # 4) disable all handle-widgets
        for handle in roi.handles.values():
            handle.Off()

    # 5) forget all the ROIs
    self.ellipses.clear()

    # 6) re-render each view
    for w in (self.vtkWidgetAxial,
              self.vtkWidgetCoronal,
              self.vtkWidgetSagittal):
        w.GetRenderWindow().Render()

# ─── Square ROI ────────────────────────────────────────────────────────────

def add_square(self):
    """Create & show a new square ROI in each of the three views."""
    # make sure we have a list to hold them
    if not hasattr(self, 'squares'):
        self.squares = []

    # axial
    sq = SquareRoiWidget(
        self.vtkWidgetAxial, self.renAxial, self,
        self.imageActorAxial[0], 'axial'
    )
    sq.toggle()
    self.squares.append(sq)

    # coronal
    sq = SquareRoiWidget(
        self.vtkWidgetCoronal, self.renCoronal, self,
        self.imageActorCoronal[0], 'coronal'
    )
    sq.toggle()
    self.squares.append(sq)

    # sagittal
    sq = SquareRoiWidget(
        self.vtkWidgetSagittal, self.renSagittal, self,
        self.imageActorSagittal[0], 'sagittal'
    )
    sq.toggle()
    self.squares.append(sq)


def remove_squares(self):
    """Hide, remove and delete *all* existing square ROIs."""
    for roi in getattr(self, 'squares', []):
        # 1) hide it if it’s visible
        if getattr(roi, 'is_visible', False):
            roi.toggle()

        # 2) remove the square actor itself
        if hasattr(roi, 'squareActor') and roi.squareActor:
            roi.renderer.RemoveActor(roi.squareActor)

        # 3) remove its stats‐text actor
        if hasattr(roi, 'statsActor') and roi.statsActor:
            roi.renderer.RemoveActor(roi.statsActor)

        # 4) turn off all the handle‐widgets
        for handle in roi.handles.values():
            handle.Off()

    # 5) clear the list
    self.squares.clear()

    # 6) re‐render each view
    for w in (self.vtkWidgetAxial,
              self.vtkWidgetCoronal,
              self.vtkWidgetSagittal):
        w.GetRenderWindow().Render()