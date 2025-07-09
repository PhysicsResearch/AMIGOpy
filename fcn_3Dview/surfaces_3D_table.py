from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QCheckBox, QSpinBox, QColorDialog, QDoubleSpinBox
from PyQt5.QtGui import QColor

def init_STL_Surface_table(self):
    self._STL_Surface_table.setColumnCount(16)
    self._STL_Surface_table.setHorizontalHeaderLabels([
        "Name",         # 0
        "Face Color",   # 1
        "Line Color",   # 2
        "Show Faces",   # 3
        "Show Lines",   # 4
        "Face Alpha",   # 5
        "Line Width",   # 6
        "Tx", "Ty", "Tz",    # 7-9 translation
        "Sx", "Sy", "Sz",    # 10-12 scaling
        "Reset T",           # 13
        "Reset S",           # 14
        "Delete"             # 15 ← LAST COLUMN
    ])
    self._STL_Surface_table.setEditTriggers(self._STL_Surface_table.NoEditTriggers)
    self._STL_Surface_table.setSelectionBehavior(self._STL_Surface_table.SelectRows)


def add_stl_to_table(self, name,
                     face_color=(0.8,0.8,0.3), line_color=(0,0,0),
                     show_faces=True, show_lines=True,
                     face_alpha=1.0,
                     line_width=1.0,
                     tx=0, ty=0, tz=0,
                     sx=1.0, sy=1.0, sz=1.0):
    row = self._STL_Surface_table.rowCount()
    self._STL_Surface_table.insertRow(row)

    # Name
    item = QTableWidgetItem(name)
    item.setData(Qt.UserRole, name)
    self._STL_Surface_table.setItem(row, 0, item)

    # Face color
    btn_face_color = QPushButton()
    btn_face_color.setStyleSheet(f"background-color: rgb({int(face_color[0]*255)}, {int(face_color[1]*255)}, {int(face_color[2]*255)});")
    btn_face_color.clicked.connect(lambda _, n=name: pick_stl_face_color(self, n))
    self._STL_Surface_table.setCellWidget(row, 1, btn_face_color)

    # Line color
    btn_line_color = QPushButton()
    btn_line_color.setStyleSheet(f"background-color: rgb({int(line_color[0]*255)}, {int(line_color[1]*255)}, {int(line_color[2]*255)});")
    btn_line_color.clicked.connect(lambda _, n=name: pick_stl_line_color(self, n))
    self._STL_Surface_table.setCellWidget(row, 2, btn_line_color)

    # Show Faces
    box_faces = QCheckBox()
    box_faces.setChecked(show_faces)
    box_faces.stateChanged.connect(lambda state, n=name: update_stl_show_faces(self, n, state))
    self._STL_Surface_table.setCellWidget(row, 3, box_faces)

    # Show Lines
    box_lines = QCheckBox()
    box_lines.setChecked(show_lines)
    box_lines.stateChanged.connect(lambda state, n=name: update_stl_show_lines(self, n, state))
    self._STL_Surface_table.setCellWidget(row, 4, box_lines)

    # Face Alpha
    spin_face_alpha = QDoubleSpinBox()
    spin_face_alpha.setRange(0.0, 1.0)
    spin_face_alpha.setSingleStep(0.05)
    spin_face_alpha.setValue(face_alpha)
    spin_face_alpha.valueChanged.connect(lambda val, n=name: update_stl_face_alpha(self, n, val))
    self._STL_Surface_table.setCellWidget(row, 5, spin_face_alpha)

    # Line Width
    spin_line_width = QDoubleSpinBox()
    spin_line_width.setRange(0.1, 10.0)
    spin_line_width.setSingleStep(0.1)
    spin_line_width.setValue(line_width)
    spin_line_width.valueChanged.connect(lambda val, n=name: update_stl_line_width(self, n, val))
    self._STL_Surface_table.setCellWidget(row, 6, spin_line_width)

    # Translation X, Y, Z (columns 7-9)
    for col, val, update_func in zip([7, 8, 9], [tx, ty, tz], [update_stl_tx, update_stl_ty, update_stl_tz]):
        spin = QDoubleSpinBox()
        spin.setRange(-1000, 1000)
        spin.setSingleStep(0.1)
        spin.setValue(val)
        spin.valueChanged.connect(lambda v, n=name, f=update_func: f(self, n, v))
        self._STL_Surface_table.setCellWidget(row, col, spin)

    # Scaling Sx, Sy, Sz (columns 10-12)
    for col, val, update_func in zip([10, 11, 12], [sx, sy, sz], [update_stl_sx, update_stl_sy, update_stl_sz]):
        spin = QDoubleSpinBox()
        spin.setRange(0.01, 100.0)
        spin.setSingleStep(0.01)
        spin.setValue(val)
        spin.valueChanged.connect(lambda v, n=name, f=update_func: f(self, n, v))
        self._STL_Surface_table.setCellWidget(row, col, spin)

    # Reset translation button (col 13)
    btn_reset_t = QPushButton("Reset T")
    btn_reset_t.setStyleSheet(
        "background-color: #2574A9; color: white; margin-right: 4px; margin-left: 2px; border-radius: 4px;")
    btn_reset_t.clicked.connect(lambda _, n=name: reset_stl_translation(self, n))
    self._STL_Surface_table.setCellWidget(row, 13, btn_reset_t)

    # Reset scaling button (col 14)
    btn_reset_s = QPushButton("Reset S")
    btn_reset_s.setStyleSheet(
        "background-color: #2574A9; color: white; margin-left: 4px; margin-right: 4px; border-radius: 4px;")
    btn_reset_s.clicked.connect(lambda _, n=name: reset_stl_scale(self, n))
    self._STL_Surface_table.setCellWidget(row, 14, btn_reset_s)

    # Delete button (col 15)
    btn_del = QPushButton("Delete")
    btn_del.setStyleSheet(
        "background-color: #D64541; color: white; margin-left: 8px; border-radius: 4px;")
    btn_del.clicked.connect(lambda _, n=name: delete_stl_surface(self, n))
    self._STL_Surface_table.setCellWidget(row, 15, btn_del)

    # Sync initial colors for table and actor
    pick_stl_face_color(self, name, initial=True, rgb=face_color)
    pick_stl_line_color(self, name, initial=True, rgb=line_color)


def pick_stl_face_color(self, stl_name, initial=False, rgb=None):
    if initial and rgb is not None:
        color = rgb
    else:
        c = QColorDialog.getColor()
        if not c.isValid():
            return
        color = (c.red()/255, c.green()/255, c.blue()/255)
    row = find_row_by_name_stl(self, stl_name)
    if row is not None:
        qcolor = QColor(int(color[0]*255), int(color[1]*255), int(color[2]*255))
        self._STL_Surface_table.cellWidget(row, 1).setStyleSheet(f"background-color: rgb({qcolor.red()}, {qcolor.green()}, {qcolor.blue()});")
    self._surfaces[stl_name].GetProperty().SetColor(color)
    self.VTK3D_interactor.GetRenderWindow().Render()

def pick_stl_line_color(self, stl_name, initial=False, rgb=None):
    if initial and rgb is not None:
        color = rgb
    else:
        c = QColorDialog.getColor()
        if not c.isValid():
            return
        color = (c.red()/255, c.green()/255, c.blue()/255)
    row = find_row_by_name_stl(self, stl_name)
    if row is not None:
        qcolor = QColor(int(color[0]*255), int(color[1]*255), int(color[2]*255))
        self._STL_Surface_table.cellWidget(row, 2).setStyleSheet(f"background-color: rgb({qcolor.red()}, {qcolor.green()}, {qcolor.blue()});")
    self._surfaces[stl_name].GetProperty().SetEdgeColor(color)
    self.VTK3D_interactor.GetRenderWindow().Render()


def update_stl_show_faces(self, stl_name, state):
    actor = self._surfaces[stl_name]
    # Show/hide faces, but keep lines visible if checked
    if state == 2:  # Checked: show faces (surface)
        actor.GetProperty().SetRepresentationToSurface()
        # Restore face opacity (get from table or actor if needed)
        # (optionally restore face color, etc)
    else:  # Unchecked: show only lines (wireframe)
        actor.GetProperty().SetRepresentationToWireframe()
    self.VTK3D_interactor.GetRenderWindow().Render()


def update_stl_show_lines(self, stl_name, state):
    actor = self._surfaces[stl_name]
    actor.GetProperty().SetEdgeVisibility(state == 2)
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_stl_face_alpha(self, stl_name, val):
    self._surfaces[stl_name].GetProperty().SetOpacity(val)
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_stl_line_alpha(self, stl_name, val):
    actor = self._surfaces[stl_name]
    edge_color = actor.GetProperty().GetEdgeColor()
    # You can store original edge color and multiply by alpha for blending, or just set it here
    new_color = tuple(c * val for c in edge_color)
    actor.GetProperty().SetEdgeColor(*new_color)
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_stl_line_width(self, stl_name, val):
    self._surfaces[stl_name].GetProperty().SetLineWidth(val)
    self.VTK3D_interactor.GetRenderWindow().Render()

def delete_stl_surface(self, stl_name):
    actor = self._surfaces[stl_name]
    self.VTK3D_renderer.RemoveActor(actor)
    del self._surfaces[stl_name]
    row = find_row_by_name_stl(self, stl_name)
    if row is not None:
        self._STL_Surface_table.removeRow(row)
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_stl_tx(self, stl_name, val):
    actor = self._surfaces[stl_name]
    pos = list(actor.GetPosition())
    pos[0] = val
    actor.SetPosition(*pos)
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_stl_ty(self, stl_name, val):
    actor = self._surfaces[stl_name]
    pos = list(actor.GetPosition())
    pos[1] = val
    actor.SetPosition(*pos)
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_stl_tz(self, stl_name, val):
    actor = self._surfaces[stl_name]
    pos = list(actor.GetPosition())
    pos[2] = val
    actor.SetPosition(*pos)
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_stl_sx(self, stl_name, val):
    actor = self._surfaces[stl_name]
    sy, sz = actor.GetScale()[1:]
    actor.SetScale(val, sy, sz)
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_stl_sy(self, stl_name, val):
    actor = self._surfaces[stl_name]
    sx, _, sz = actor.GetScale()
    actor.SetScale(sx, val, sz)
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_stl_sz(self, stl_name, val):
    actor = self._surfaces[stl_name]
    sx, sy, _ = actor.GetScale()
    actor.SetScale(sx, sy, val)
    self.VTK3D_interactor.GetRenderWindow().Render()

def reset_stl_translation(self, stl_name):
    actor = self._surfaces[stl_name]
    actor.SetPosition(0, 0, 0)
    row = find_row_by_name_stl(self, stl_name)
    if row is not None:
        for i in [9, 10, 11]:
            self._STL_Surface_table.cellWidget(row, i).setValue(0)
    self.VTK3D_interactor.GetRenderWindow().Render()

def reset_stl_scale(self, stl_name):
    actor = self._surfaces[stl_name]
    actor.SetScale(1, 1, 1)
    row = find_row_by_name_stl(self, stl_name)
    if row is not None:
        for i in [12, 13, 14]:
            self._STL_Surface_table.cellWidget(row, i).setValue(1)
    self.VTK3D_interactor.GetRenderWindow().Render()

def find_row_by_name_stl(self, stl_name):
    for row in range(self._STL_Surface_table.rowCount()):
        item = self._STL_Surface_table.item(row, 0)
        if item and item.data(Qt.UserRole) == stl_name:
            return row
    return None