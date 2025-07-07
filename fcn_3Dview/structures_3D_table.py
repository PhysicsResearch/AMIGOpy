from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QCheckBox, QSpinBox, QColorDialog, QDoubleSpinBox

def init_3D_Struct_table(self):
    self._3D_Struct_table.setColumnCount(7)  #
    self._3D_Struct_table.setHorizontalHeaderLabels([
        "Name", "Color", "Size", "Visible", "Surface", "Transparency", "Delete"
    ])
    self._3D_Struct_table.setEditTriggers(self._3D_Struct_table.NoEditTriggers)  # Optional: make non-editable
    self._3D_Struct_table.setSelectionBehavior(self._3D_Struct_table.SelectRows)


def add_cloud_to_table(self, name, color=(1,0,0), size=3, visible=True, surface=False, transparency=1):
    row = self._3D_Struct_table.rowCount()
    self._3D_Struct_table.insertRow(row)
    
    # Name (store the cloud name as an identifier)
    item = QTableWidgetItem(name)
    item.setData(Qt.UserRole, name)  # Store unique cloud name
    self._3D_Struct_table.setItem(row, 0, item)
    
    # Color button
    btn_color = QPushButton()
    btn_color.setStyleSheet(f"background-color: rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)});")
    btn_color.clicked.connect(lambda _, n=name: pick_cloud_color(self, n))
    self._3D_Struct_table.setCellWidget(row, 1, btn_color)
    
    # Size spinbox
    spin_size = QSpinBox()
    spin_size.setRange(1, 20)
    spin_size.setValue(size)
    spin_size.valueChanged.connect(lambda val, n=name: update_cloud_size(self, n, val))
    self._3D_Struct_table.setCellWidget(row, 2, spin_size)
    
    # Visible checkbox
    box_vis = QCheckBox()
    box_vis.setChecked(visible)
    box_vis.stateChanged.connect(lambda state, n=name: update_cloud_visibility(self, n, state))
    self._3D_Struct_table.setCellWidget(row, 3, box_vis)
    
    # Surface checkbox
    box_surf = QCheckBox()
    box_surf.setChecked(surface)
    box_surf.stateChanged.connect(lambda state, n=name: update_cloud_surface(self, n, state))
    self._3D_Struct_table.setCellWidget(row, 4, box_surf)
    

    # Transparency column (column 5)
    spin_trans = QDoubleSpinBox()
    spin_trans.setRange(0.0, 1.0)
    spin_trans.setSingleStep(0.05)
    spin_trans.setDecimals(2)
    spin_trans.setValue(transparency)
    spin_trans.valueChanged.connect(lambda val, n=name: update_cloud_transparency(self, n, val))
    self._3D_Struct_table.setCellWidget(row, 5, spin_trans)


    # Delete button
    btn_del = QPushButton("Delete")
    btn_del.clicked.connect(lambda _, n=name: delete_cloud(self, n))
    self._3D_Struct_table.setCellWidget(row, 6, btn_del)


def update_cloud_transparency(self, cloud_name, value):
    # Update the cloud's transparency property and actor
    if cloud_name in self._clouds:
        self._clouds[cloud_name]['transparency'] = value
        self._clouds[cloud_name]['actor'].GetProperty().SetOpacity(value)
        self.VTK3D_interactor.GetRenderWindow().Render()


def pick_cloud_color(self, cloud_name):
    color = QColorDialog.getColor()
    if color.isValid():
        rgb = (color.red()/255, color.green()/255, color.blue()/255)
        # Update table button (find row by name)
        row = find_row_by_name(self,cloud_name)
        if row is not None:
            self._3D_Struct_table.cellWidget(row, 1).setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});")
        # Update cloud visual property
        self._clouds[cloud_name]['color'] = rgb
        self._clouds[cloud_name]['actor'].GetProperty().SetColor(rgb)
        self.VTK3D_interactor.GetRenderWindow().Render()

def update_cloud_size(self, cloud_name, value):
    self._clouds[cloud_name]['size'] = value
    self._clouds[cloud_name]['actor'].GetProperty().SetPointSize(value)
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_cloud_visibility(self, cloud_name, state):
    actor = self._clouds[cloud_name]['actor']
    actor.SetVisibility(state == 2)
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_cloud_surface(self, cloud_name, state):
    pass  # No change needed unless you need to refer to a row

def delete_cloud(self, cloud_name):
    # Remove the actor
    actor = self._clouds[cloud_name]['actor']
    self.VTK3D_renderer.RemoveActor(actor)
    del self._clouds[cloud_name]
    # Remove the row in the table by name
    row = find_row_by_name(self,cloud_name)
    if row is not None:
        self._3D_Struct_table.removeRow(row)
    self.VTK3D_interactor.GetRenderWindow().Render()

def find_row_by_name(self, cloud_name):
    # Looks for the row containing cloud_name as its Qt.UserRole data in column 0
    for row in range(self._3D_Struct_table.rowCount()):
        item = self._3D_Struct_table.item(row, 0)
        if item and item.data(Qt.UserRole) == cloud_name:
            return row
    return None