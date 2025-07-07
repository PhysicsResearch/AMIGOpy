from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QCheckBox, QSpinBox, QColorDialog

def init_3D_Struct_table(self):
    self._3D_Struct_table.setColumnCount(6)
    self._3D_Struct_table.setHorizontalHeaderLabels([
        "Name", "Color", "Size", "Visible", "Surface", "Delete"
    ])
    self._3D_Struct_table.setEditTriggers(self._3D_Struct_table.NoEditTriggers)  # Optional: make non-editable
    self._3D_Struct_table.setSelectionBehavior(self._3D_Struct_table.SelectRows)


def add_cloud_to_table(self, name, color=(1,0,0), size=3, visible=True, surface=False):
    row = self._3D_Struct_table.rowCount()
    self._3D_Struct_table.insertRow(row)
    
    # Name
    item = QTableWidgetItem(name)
    self._3D_Struct_table.setItem(row, 0, item)
    
    # Color button
    btn_color = QPushButton()
    btn_color.setStyleSheet(f"background-color: rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)});")
    btn_color.clicked.connect(lambda _, r=row: pick_cloud_color(self,r))
    self._3D_Struct_table.setCellWidget(row, 1, btn_color)
    
    # Size spinbox
    spin_size = QSpinBox()
    spin_size.setRange(1, 20)
    spin_size.setValue(size)
    spin_size.valueChanged.connect(lambda val, r=row: update_cloud_size(self, r, val))
    self._3D_Struct_table.setCellWidget(row, 2, spin_size)
    
    # Visible checkbox
    box_vis = QCheckBox()
    box_vis.setChecked(visible)
    box_vis.stateChanged.connect(lambda state, r=row: update_cloud_visibility(self, r, state))
    self._3D_Struct_table.setCellWidget(row, 3, box_vis)
    
    # Surface checkbox
    box_surf = QCheckBox()
    box_surf.setChecked(surface)
    box_surf.stateChanged.connect(lambda state, r=row: update_cloud_surface(self, r, state))
    self._3D_Struct_table.setCellWidget(row, 4, box_surf)
    
    # Delete button
    btn_del = QPushButton("Delete")
    btn_del.clicked.connect(lambda _, r=row: delete_cloud(self, r))
    self._3D_Struct_table.setCellWidget(row, 5, btn_del)


def pick_cloud_color(self, row):
    color = QColorDialog.getColor()
    if color.isValid():
        rgb = (color.red()/255, color.green()/255, color.blue()/255)
        # Update table button
        self._3D_Struct_table.cellWidget(row, 1).setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});")
        # Update cloud visual property
        name = self._3D_Struct_table.item(row, 0).text()
        self._clouds[name]['color'] = rgb
        self._clouds[name]['actor'].GetProperty().SetColor(rgb)
        self.VTK3D_interactor.GetRenderWindow().Render()

def update_cloud_size(self, row, value):
    name = self._3D_Struct_table.item(row, 0).text()
    self._clouds[name]['size'] = value
    self._clouds[name]['actor'].GetProperty().SetPointSize(value)
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_cloud_visibility(self, row, state):
    name = self._3D_Struct_table.item(row, 0).text()
    actor = self._clouds[name]['actor']
    actor.SetVisibility(state == 2)
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_cloud_surface(self, row, state):
    # For toggling surface display, up to your design (e.g. add/remove a surface actor)
    pass

def delete_cloud(self, row):
    name = self._3D_Struct_table.item(row, 0).text()
    actor = self._clouds[name]['actor']
    self.VTK3D_renderer.RemoveActor(actor)
    del self._clouds[name]
    self._3D_Struct_table.removeRow(row)
    self.VTK3D_interactor.GetRenderWindow().Render()