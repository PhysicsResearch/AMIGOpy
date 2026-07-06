import functools
import numpy as np
import vtk
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QTableWidgetItem, QCheckBox, QDoubleSpinBox, QPushButton, QColorDialog,
    QAbstractItemView, QHeaderView, QWidget, QGridLayout, QTableWidget, QHBoxLayout, QComboBox
)
from PySide6.QtGui import QColor

def init_3D_brachy_table(self):
    # Ensure self.tab_41 (Plan_Brachy) has a grid layout
    if not self.tab_41.layout():
        layout = QGridLayout(self.tab_41)
        self.tab_41.setLayout(layout)
    else:
        layout = self.tab_41.layout()
        
    # Create the table if not exists
    if not hasattr(self, '_3D_brachy_table'):
        self._3D_brachy_table = QTableWidget(self.tab_41)
        self._3D_brachy_table.setObjectName("_3D_brachy_table")
        layout.addWidget(self._3D_brachy_table, 0, 0, 1, 1)

    self._3D_brachy_table.setColumnCount(6)
    self._3D_brachy_table.setHorizontalHeaderLabels([
        "Element", "Representation", "Size / Thickness", "Opacity", "Color", "Visible"
    ])
    
    self._3D_brachy_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    self._3D_brachy_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    self._3D_brachy_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    
    hh = self._3D_brachy_table.horizontalHeader()
    vh = self._3D_brachy_table.verticalHeader()
    hh.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    hh.setStretchLastSection(True)
    vh.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    
    repopulate_3D_brachy_table(self)


def repopulate_3D_brachy_table(self):
    # Clear any old actors
    if not hasattr(self, '_3D_brachy_actors'):
        self._3D_brachy_actors = {}
    for name, actors in list(self._3D_brachy_actors.items()):
        for actor in actors:
            self.VTK3D_renderer.RemoveActor(actor)
    self._3D_brachy_actors.clear()

    self._3D_brachy_table.setRowCount(0)
    
    if not hasattr(self, 'patientID_plan') or not self.patientID_plan:
        return
        
    metadata = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']
    channels = metadata.get('Plan_Brachy_Channels', [])
    ref_pts = metadata.get('Plan_Dose_References', [])
    
    items_to_add = []
    
    # 1. Dwells - one row per channel
    for idx in range(len(channels)):
        name = f"Dwells - Ch {idx + 1}"
        items_to_add.append({
            "name": name,
            "type": "Dwells",
            "index": idx,
            "visible": True,
            "rep": "Sphere",
            "size": 1.5,
            "opacity": 1.0,
            "color": (1.0, 1.0, 0.0) # Yellow
        })
        
    # 2. Catheters - one row per channel
    for idx in range(len(channels)):
        name = f"Catheter - Ch {idx + 1}"
        items_to_add.append({
            "name": name,
            "type": "Catheters",
            "index": idx,
            "visible": True,
            "rep": "Tube",
            "size": 1.0,
            "opacity": 0.8,
            "color": (0.0, 1.0, 0.0) # Green
        })
        
    # 3. Reference Points - one row per point
    for idx, rp in enumerate(ref_pts):
        desc = rp.get('DoseReferenceDescription', f"Point {idx + 1}")
        name = f"Ref Point - {desc}"
        items_to_add.append({
            "name": name,
            "type": "Reference Points",
            "index": idx,
            "visible": True,
            "rep": "Sphere",
            "size": 2.0,
            "opacity": 1.0,
            "color": (1.0, 0.0, 0.0) # Red
        })

    for row, elem in enumerate(items_to_add):
        self._3D_brachy_table.insertRow(row)
        
        # 0. Element Name
        item = QTableWidgetItem(elem["name"])
        item.setData(Qt.UserRole, elem)
        self._3D_brachy_table.setItem(row, 0, item)
        
        # 1. Representation Combobox (Sphere/Cross/Contour or Tube/Line or Sphere/Cube/Cone/Cylinder)
        combo = QComboBox()
        if elem["type"] == "Dwells":
            combo.addItems(["Sphere", "Cross", "Contour"])
        elif elem["type"] == "Catheters":
            combo.addItems(["Tube", "Line"])
        elif elem["type"] == "Reference Points":
            combo.addItems(["Sphere", "Cube", "Contour"])
        
        combo.setCurrentText(elem["rep"])
        combo.currentTextChanged.connect(functools.partial(update_3D_brachy_element, self, elem["name"]))
        self._3D_brachy_table.setCellWidget(row, 1, combo)
        
        # 2. Size / Thickness
        spin_size = QDoubleSpinBox()
        spin_size.setRange(0.1, 20.0)
        spin_size.setSingleStep(0.1)
        spin_size.setValue(elem["size"])
        spin_size.valueChanged.connect(functools.partial(update_3D_brachy_element, self, elem["name"]))
        self._3D_brachy_table.setCellWidget(row, 2, spin_size)
        
        # 3. Opacity
        spin_opac = QDoubleSpinBox()
        spin_opac.setRange(0.0, 1.0)
        spin_opac.setSingleStep(0.05)
        spin_opac.setValue(elem["opacity"])
        spin_opac.valueChanged.connect(functools.partial(update_3D_brachy_element, self, elem["name"]))
        self._3D_brachy_table.setCellWidget(row, 3, spin_opac)
        
        # 4. Color (small, centered button)
        btn = QPushButton()
        btn.setFixedSize(30, 20)
        c = elem["color"]
        btn.setStyleSheet(f"background-color: rgb({int(c[0]*255)}, {int(c[1]*255)}, {int(c[2]*255)});")
        btn.clicked.connect(functools.partial(pick_3D_brachy_color, self, elem["name"]))
        
        lay_btn = QHBoxLayout()
        lay_btn.addWidget(btn)
        lay_btn.setAlignment(Qt.AlignCenter)
        lay_btn.setContentsMargins(0, 0, 0, 0)
        c_btn = QWidget()
        c_btn.setLayout(lay_btn)
        self._3D_brachy_table.setCellWidget(row, 4, c_btn)
        
        # 5. Visible (centered checkbox at the very right)
        chk = QCheckBox()
        chk.setChecked(elem["visible"])
        chk.stateChanged.connect(functools.partial(update_3D_brachy_element, self, elem["name"]))
        
        lay_chk = QHBoxLayout()
        lay_chk.addWidget(chk)
        lay_chk.setAlignment(Qt.AlignCenter)
        lay_chk.setContentsMargins(0, 0, 0, 0)
        c_chk = QWidget()
        c_chk.setLayout(lay_chk)
        self._3D_brachy_table.setCellWidget(row, 5, c_chk)

    # Trigger initial update of the renderer for all elements
    for elem in items_to_add:
        update_3D_brachy_element(self, elem["name"])


def update_3D_brachy_element(self, element_name, *args):
    if not hasattr(self, '_3D_brachy_table'):
        return
        
    # Find row index of the element
    row = None
    elem_info = None
    for r in range(self._3D_brachy_table.rowCount()):
        item = self._3D_brachy_table.item(r, 0)
        if item and item.data(Qt.UserRole) and item.data(Qt.UserRole).get("name") == element_name:
            row = r
            elem_info = item.data(Qt.UserRole)
            break
    if row is None or elem_info is None:
        return
        
    # Retrieve Centered Widgets
    container_chk = self._3D_brachy_table.cellWidget(row, 5)
    chk = container_chk.findChild(QCheckBox) if container_chk else None
    is_visible = chk.isChecked() if chk else False
    
    combo_rep = self._3D_brachy_table.cellWidget(row, 1)
    rep_val = combo_rep.currentText() if combo_rep else ""
    
    spin_size = self._3D_brachy_table.cellWidget(row, 2)
    size_val = spin_size.value() if spin_size else 1.0
    
    spin_opac = self._3D_brachy_table.cellWidget(row, 3)
    opac_val = spin_opac.value() if spin_opac else 1.0
    
    container_btn = self._3D_brachy_table.cellWidget(row, 4)
    btn_color = container_btn.findChild(QPushButton) if container_btn else None
    if btn_color:
        import re
        style = btn_color.styleSheet()
        m = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', style)
        if m:
            rgb = tuple(int(x)/255. for x in m.groups())
        else:
            rgb = (1.0, 1.0, 0.0)
    else:
        rgb = (1.0, 1.0, 0.0)

    # Ensure actors dict is initialized
    if not hasattr(self, '_3D_brachy_actors'):
        self._3D_brachy_actors = {}
        
    # Remove old actors for this element name
    if element_name in self._3D_brachy_actors:
        for actor in self._3D_brachy_actors[element_name]:
            self.VTK3D_renderer.RemoveActor(actor)
        del self._3D_brachy_actors[element_name]
        
    self._3D_brachy_actors[element_name] = []
    
    if not is_visible:
        if hasattr(self, 'VTK3D_interactor') and self.VTK3D_interactor:
            self.VTK3D_interactor.GetRenderWindow().Render()
        return

    # Check that we have a loaded plan
    if not hasattr(self, 'patientID_plan') or not self.patientID_plan:
        return
        
    metadata = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']
    channels = metadata.get('Plan_Brachy_Channels', [])
    ref_pts = metadata.get('Plan_Dose_References', [])
    
    # Shift reference to match the 3D volume
    ref = self.Im_PatPosition3Dview[0, :3] if hasattr(self, "Im_PatPosition3Dview") else np.zeros(3)

    idx = elem_info["index"]
    elem_type = elem_info["type"]
    
    if elem_type == "Dwells":
        if idx < len(channels):
            dw_info = channels[idx].get('DwellInfo')
            if dw_info is not None and isinstance(dw_info, np.ndarray) and dw_info.size > 0:
                pts = dw_info[:, 3:6]
                shifted = pts - ref
                # Swap Y and Z, then flip Z
                transformed = np.zeros_like(shifted)
                transformed[:, 0] = shifted[:, 0]
                transformed[:, 1] = shifted[:, 2]
                transformed[:, 2] = -shifted[:, 1]
                shifted = transformed
                
                actor = vtk.vtkActor()
                
                if rep_val == "Cross":
                    # Build 3D crosshairs
                    append = vtk.vtkAppendPolyData()
                    for pt in shifted:
                        for axis in range(3):
                            line = vtk.vtkLineSource()
                            start = list(pt)
                            end   = list(pt)
                            start[axis] -= size_val / 2
                            end[axis]   += size_val / 2
                            line.SetPoint1(*start)
                            line.SetPoint2(*end)
                            line.Update()
                            append.AddInputData(line.GetOutput())
                    append.Update()
                    mapper = vtk.vtkPolyDataMapper()
                    mapper.SetInputConnection(append.GetOutputPort())
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetLineWidth(2.0)
                else:  # Sphere or Contour (Wireframe)
                    append = vtk.vtkAppendPolyData()
                    for pt in shifted:
                        sphere = vtk.vtkSphereSource()
                        sphere.SetCenter(pt[0], pt[1], pt[2])
                        sphere.SetRadius(size_val)
                        sphere.SetThetaResolution(12)
                        sphere.SetPhiResolution(12)
                        sphere.Update()
                        append.AddInputData(sphere.GetOutput())
                    append.Update()
                    mapper = vtk.vtkPolyDataMapper()
                    mapper.SetInputConnection(append.GetOutputPort())
                    actor.SetMapper(mapper)
                    
                    if rep_val == "Contour":
                        actor.GetProperty().SetRepresentationToWireframe()
                    
                actor.GetProperty().SetColor(rgb)
                actor.GetProperty().SetOpacity(opac_val)
                
                self.VTK3D_renderer.AddActor(actor)
                self._3D_brachy_actors[element_name].append(actor)
                
    elif elem_type == "Catheters":
        if idx < len(channels):
            ch_pos = channels[idx].get('ChPos')
            if ch_pos is not None and isinstance(ch_pos, np.ndarray) and ch_pos.size > 0:
                shifted = ch_pos - ref
                # Swap Y and Z, then flip Z
                transformed = np.zeros_like(shifted)
                transformed[:, 0] = shifted[:, 0]
                transformed[:, 1] = shifted[:, 2]
                transformed[:, 2] = -shifted[:, 1]
                shifted = transformed
                
                points_vtk = vtk.vtkPoints()
                lines = vtk.vtkCellArray()
                lines.InsertNextCell(len(shifted))
                for pt_idx, pt in enumerate(shifted):
                    points_vtk.InsertNextPoint(pt[0], pt[1], pt[2])
                    lines.InsertCellPoint(pt_idx)
                    
                polydata = vtk.vtkPolyData()
                polydata.SetPoints(points_vtk)
                polydata.SetLines(lines)
                
                actor = vtk.vtkActor()
                
                if rep_val == "Tube":
                    tube = vtk.vtkTubeFilter()
                    tube.SetInputData(polydata)
                    tube.SetRadius(size_val)
                    tube.SetNumberOfSides(12)
                    tube.Update()
                    
                    mapper = vtk.vtkPolyDataMapper()
                    mapper.SetInputConnection(tube.GetOutputPort())
                    actor.SetMapper(mapper)
                else:  # Line
                    mapper = vtk.vtkPolyDataMapper()
                    mapper.SetInputData(polydata)
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetLineWidth(size_val)
                    
                actor.GetProperty().SetColor(rgb)
                actor.GetProperty().SetOpacity(opac_val)
                
                self.VTK3D_renderer.AddActor(actor)
                self._3D_brachy_actors[element_name].append(actor)
                
    elif elem_type == "Reference Points":
        if idx < len(ref_pts):
            rp = ref_pts[idx]
            coords = rp.get('DoseReferencePointCoordinates')
            if isinstance(coords, list) and len(coords) >= 3:
                if coords[0] != 'N/A' and coords[1] != 'N/A' and coords[2] != 'N/A':
                    pt = np.array([coords[0], coords[1], coords[2]])
                    shifted = pt - ref
                    # Swap Y and Z, then flip Z
                    shifted = np.array([shifted[0], shifted[2], -shifted[1]])
                    
                    mapper = vtk.vtkPolyDataMapper()
                    actor = vtk.vtkActor()
                    
                    if rep_val == "Cube":
                        cube = vtk.vtkCubeSource()
                        cube.SetCenter(shifted[0], shifted[1], shifted[2])
                        cube.SetXLength(size_val * 2)
                        cube.SetYLength(size_val * 2)
                        cube.SetZLength(size_val * 2)
                        cube.Update()
                        mapper.SetInputConnection(cube.GetOutputPort())
                    else:  # Sphere or Contour
                        sphere = vtk.vtkSphereSource()
                        sphere.SetCenter(shifted[0], shifted[1], shifted[2])
                        sphere.SetRadius(size_val)
                        sphere.SetThetaResolution(12)
                        sphere.SetPhiResolution(12)
                        sphere.Update()
                        mapper.SetInputConnection(sphere.GetOutputPort())
                        
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(rgb)
                    actor.GetProperty().SetOpacity(opac_val)
                    
                    if rep_val == "Contour":
                        actor.GetProperty().SetRepresentationToWireframe()
                        
                    self.VTK3D_renderer.AddActor(actor)
                    self._3D_brachy_actors[element_name].append(actor)
                    
    if hasattr(self, 'VTK3D_interactor') and self.VTK3D_interactor:
        self.VTK3D_interactor.GetRenderWindow().Render()


def pick_3D_brachy_color(self, element_name):
    color = QColorDialog.getColor()
    if color.isValid():
        # Find row
        row = None
        for r in range(self._3D_brachy_table.rowCount()):
            item = self._3D_brachy_table.item(r, 0)
            if item and item.data(Qt.UserRole) and item.data(Qt.UserRole).get("name") == element_name:
                row = r
                break
        if row is not None:
            container_btn = self._3D_brachy_table.cellWidget(row, 4)
            btn = container_btn.findChild(QPushButton) if container_btn else None
            if btn:
                btn.setStyleSheet(
                    f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});"
                )
            update_3D_brachy_element(self, element_name)
