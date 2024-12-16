import os
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import  QSize
from PyQt5.QtGui import  QIcon
from fcn_display.ruller import create_ruler
from fcn_display.dicom_info import disp_dicom_info_from_amigo

def menu_bar_icon_actions(self, base_path):
        # Add a button/action with an icon - Ruler
        icon_path = os.path.join(base_path, "icons", "ruler.png")  # Adjusted path for icons
        button_action = QAction(QIcon(icon_path), "Ruler", self)
        button_action.setStatusTip("Ruler")
        button_action.triggered.connect(lambda:create_ruler(self))

        # Optional: Set a fixed size for the action to make it more squared
        self.toolbar.setIconSize(QSize(40, 40))  # Adjust size as needed
        self.toolbar.addAction(button_action)
        self.selected_point = None
        
        
        # Add a button/action with an icon - Dicom Inspect
        icon_path = os.path.join(base_path, "icons", "dcm_insp.png")  # Adjusted path for icons
        button_action = QAction(QIcon(icon_path), "DICOM Info", self)
        button_action.setStatusTip("Inspect DICOM file")
        button_action.triggered.connect(lambda:disp_dicom_info_from_amigo(self))
        self.viewer = None

        # Optional: Set a fixed size for the action to make it more squared
        self.toolbar.setIconSize(QSize(40, 40))  # Adjust size as needed
        self.toolbar.addAction(button_action)
        self.selected_point = None
        