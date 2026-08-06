from PySide6 import QtWidgets
from PySide6.QtWidgets import QHeaderView, QAbstractItemView, QTableWidget
from fcn_processing.roi_circle import on_roitable_item_changed
from fcn_ctcal.ct_cal import init_ct_cal_table
from fcn_materialassignment.material_assignment_properties import create_dataframe_materials,update_mat_properties_table,update_mat_table_style


def safe_table(parent, attr_name):
    t = getattr(parent, attr_name, None)
    if t is not None and hasattr(t, 'setColumnCount'):
        return t
    return None

def initialize_software_tables(self):
    # Adjust dwell time& position table ----------------------
    t_dwells = safe_table(self, 'Dwells_table')
    if t_dwells is not None:
        t_dwells.setColumnCount(14)
        column_names = ["Channel", "Time-1 (s)", "Time-2 (s)", "Transit time(s)", "Dwell time (s)","Dwell time w/ Trans (s)","Dw time 10ci (s)","Pos X", "Pos Y", "Pos Z","Activity (Ci)"]
        t_dwells.setHorizontalHeaderLabels(column_names)
        t_dwells.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    
    # Adjust source calibration table ----------------------
    t_source_cal = safe_table(self, 'Source_Cal_table')
    if t_source_cal is not None:
        column_names = ["Date", "Activity (Ci)", "Sk (U)", "Ref. time (min)"]
        t_source_cal.setColumnCount(4)
        t_source_cal.setHorizontalHeaderLabels(column_names)
        t_source_cal.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    
    # Adjust circular ROI table ----------------------
    t_circ_roi = safe_table(self, 'table_circ_roi')
    if t_circ_roi is not None:
        column_names = ["X Cent. (Px)", "Y Cent. (Px)", "Rad. (Px)", "Init. Slice", "Last. Slice", "Trasnp.", "Color", "Dir.", "R", "G", "B", "Actions"]
        t_circ_roi.setColumnCount(12)
        t_circ_roi.setRowCount(0)
        t_circ_roi.setSelectionBehavior(QAbstractItemView.SelectRows)
        t_circ_roi.setSelectionMode(QAbstractItemView.SingleSelection)
        t_circ_roi.setHorizontalHeaderLabels(column_names)
        t_circ_roi.setColumnHidden(8, True)
        t_circ_roi.setColumnHidden(9, True)
        t_circ_roi.setColumnHidden(10, True)
        t_circ_roi.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        t_circ_roi.horizontalHeader().setStretchLastSection(True)
        if hasattr(self, 'table_roi_c_values') and self.table_roi_c_values is not None:
            self.table_roi_c_values.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
            self.table_roi_c_values.horizontalHeader().setStretchLastSection(True)
        from fcn_processing.roi_circle import on_roitable_item_changed, on_roi_table_selection_changed
        try:
            t_circ_roi.itemChanged.connect(lambda item: on_roitable_item_changed(self, item))
            t_circ_roi.itemSelectionChanged.connect(lambda: on_roi_table_selection_changed(self))
        except (TypeError, RuntimeError):
            pass
        t_circ_roi.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #3b82f6;
                color: #ffffff;
                font-weight: bold;
            }
        """)
    
    # Adjust DECT RED table ----------------------
    t_red = safe_table(self, 'tableRED')
    if t_red is not None:
        t_red.setColumnCount(5)
        t_red.setRowCount(0)
        t_red.setHorizontalHeaderLabels(["Material","RED Ref.", "RED fit", "Diff.", "Diff. (%)"])
    
    # Adjust DECT Zeff table ----------------------
    t_zeff = safe_table(self, 'tableZeff')
    if t_zeff is not None:
        t_zeff.setColumnCount(5)
        t_zeff.setRowCount(0)
        t_zeff.setHorizontalHeaderLabels(["Material","Zeff Ref.", "Zeff fit", "Diff.", "Diff. (%)"])

    # Adjust DECT I-value table ----------------------
    t_iv = safe_table(self, 'tableIv')
    if t_iv is not None:
        t_iv.setColumnCount(5)
        t_iv.setRowCount(0)
        t_iv.setHorizontalHeaderLabels(["Material","I Ref.", "I fit", "Diff.", "Diff. (%)"])
    
    # Adjust DECT SPR table ----------------------
    t_spr = safe_table(self, 'tableSPR')
    if t_spr is not None:
        t_spr.setColumnCount(5)
        t_spr.setRowCount(0)
        t_spr.setHorizontalHeaderLabels(["Material","SPR Ref.", "SPR fit", "Diff.", "Diff. (%)"])

   # Adjust alphabeta table
    t_ab = safe_table(self, 'ab_table')
    if t_ab is not None:
        t_ab.setColumnCount(2)
        t_ab.setHorizontalHeaderLabels(["Structure Name", "α/β"])
        t_ab.setEditTriggers(QAbstractItemView.NoEditTriggers)
        t_ab.resizeColumnsToContents()
    
    # Material assignment table
    if hasattr(self, 'table_mat_properties') and self.table_mat_properties is not None:
        df = create_dataframe_materials(self)
        update_mat_properties_table(self, df)
        update_mat_table_style(self)

    t_mat_to_hu = safe_table(self, 'tableMatToHU')
    if t_mat_to_hu is not None:
        t_mat_to_hu.setColumnCount(4)
        t_mat_to_hu.setHorizontalHeaderLabels(['Material', 'ID', 'From ', 'To'])

    t_mat_to_struct = safe_table(self, 'mat_to_struct_tab')
    if t_mat_to_struct is not None:
        t_mat_to_struct.setColumnCount(3)
        t_mat_to_struct.setHorizontalHeaderLabels(['Structure', 'Material', 'ID '])

    b1 = safe_table(self, 'brachy_table_01')
    b2 = safe_table(self, 'brachy_table_02')
    from fcn_display.disp_plan_data import on_brachy_table_item_changed
    if b1 is not None and hasattr(b1, 'itemChanged'):
        try:
            b1.itemChanged.connect(lambda item: on_brachy_table_item_changed(self, b1, item))
        except (TypeError, RuntimeError):
            pass
    if b2 is not None and hasattr(b2, 'itemChanged'):
        try:
            b2.itemChanged.connect(lambda item: on_brachy_table_item_changed(self, b2, item))
        except (TypeError, RuntimeError):
            pass


