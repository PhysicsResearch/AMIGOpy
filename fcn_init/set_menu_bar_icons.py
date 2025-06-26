import os
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import  QSize
from PyQt5.QtGui import  QIcon
from fcn_display.ruller import RulerWidget
from fcn_display.dicom_info import open_dicom_tag_viewer

def menu_bar_icon_actions(self, base_path):
# ruler       """Add actions to the menu bar with icons."""
# keep adding and remove ruler  (two buttoms)

    # Add a button/action with an icon - Dicom Inspect
    icon_path = os.path.join(base_path, "icons", "dcm_insp.png")  # Adjusted path for icons
    button_action = QAction(QIcon(icon_path), "DICOM Inspect", self)
    button_action.setStatusTip("Inspect DICOM file")
    button_action.triggered.connect(lambda:open_dicom_tag_viewer())
    self.viewer = None

    # Optional: Set a fixed size for the action to make it more squared
    self.toolbar.setIconSize(QSize(40, 40))  # Adjust size as needed
    self.toolbar.addAction(button_action)
    self.selected_point = None
        
    # insert a visual separator
    self.toolbar.addSeparator()

    icon_path = os.path.join(base_path, "icons", "ruler.png")
    add_action = QAction(QIcon(icon_path), "Add Ruler", self)
    add_action.triggered.connect(lambda: add_ruler(self))
    icon_path = os.path.join(base_path, "icons", "ruler_remove.png")
    remove_action = QAction(QIcon(icon_path), "Remove Ruler", self)
    remove_action.triggered.connect(lambda: remove_rulers(self))
    self.toolbar.addAction(add_action)
    self.toolbar.addAction(remove_action)
    self.toolbar.setIconSize(QSize(32,32))

     # insert a visual separator
    self.toolbar.addSeparator()
        



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