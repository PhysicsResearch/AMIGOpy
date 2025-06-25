import os
from PyQt5.QtCore import Qt
from fcn_load.drop_folder_files_options import FolderDropArea, FolderDropTreeView

def initialize_drop_fcn(self):
    # Replace VTK container
    old_vtk = self.VTK_view_01
    layout = old_vtk.parent().layout()
    for row in range(layout.rowCount()):
        for col in range(layout.columnCount()):
            if layout.itemAtPosition(row, col) and layout.itemAtPosition(row, col).widget() is old_vtk:
                layout.removeWidget(old_vtk)
                old_vtk.deleteLater()
                self.VTK_view_01 = FolderDropArea(self)  
                layout.addWidget(self.VTK_view_01, row, col)
                break

    old_vtk = self.VTK_view_02
    layout = old_vtk.parent().layout()
    for row in range(layout.rowCount()):
        for col in range(layout.columnCount()):
            if layout.itemAtPosition(row, col) and layout.itemAtPosition(row, col).widget() is old_vtk:
                layout.removeWidget(old_vtk)
                old_vtk.deleteLater()
                self.VTK_view_02 = FolderDropArea(self)  
                layout.addWidget(self.VTK_view_02, row, col)
                break

    old_vtk = self.VTK_view_03
    layout = old_vtk.parent().layout()
    for row in range(layout.rowCount()):
        for col in range(layout.columnCount()):
            if layout.itemAtPosition(row, col) and layout.itemAtPosition(row, col).widget() is old_vtk:
                layout.removeWidget(old_vtk)
                old_vtk.deleteLater()
                self.VTK_view_03 = FolderDropArea(self)  
                layout.addWidget(self.VTK_view_03, row, col)
                break

    # Replace DataTreeView
    old_tree = self.DataTreeView
    layout = old_tree.parent().layout()
    for row in range(layout.rowCount()):
        for col in range(layout.columnCount()):
            if layout.itemAtPosition(row, col) and layout.itemAtPosition(row, col).widget() is old_tree:
                layout.removeWidget(old_tree)
                old_tree.deleteLater()
                self.DataTreeView = FolderDropTreeView(self)  
                layout.addWidget(self.DataTreeView, row, col)
                break
