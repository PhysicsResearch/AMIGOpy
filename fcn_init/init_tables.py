from PyQt5.QtWidgets import QHeaderView
from fcn_processing.roi_circle import on_roitable_item_changed
from PyQt5.QtWidgets import QHeaderView, QAbstractItemView
from fcn_ctcal.ct_cal import init_ct_cal_table
from fcn_materialassignment.material_assignment_properties import create_dataframe_materials,update_mat_properties_table,update_mat_table_style


def initialize_software_tables(self):
    # Adjust dwell time& position table ----------------------
    self.Dwells_table.setColumnCount(14)
    # Define the column names
    column_names = ["Channel", "Time-1 (s)", "Time-2 (s)", "Transit time(s)", "Dwell time (s)","Dwell time w/ Trans (s)","Dw time 10ci (s)","Pos X", "Pos Y", "Pos Z","Activity (Ci)"]
    # Set the column headers
    self.Dwells_table.setHorizontalHeaderLabels(column_names)
    # Adjust the column width to fit the content or header
    self.Dwells_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    # the last column to stretch and fill the available space
    # self.Dwells_table.horizontalHeader().setStretchLastSection(True)
    
    # Adjust source calibration table ----------------------
    column_names = ["Date", "Activity (Ci)", "Sk (U)", "Ref. time (min)"]
    self.Source_Cal_table.setColumnCount(4)
    #
    self.Source_Cal_table.setHorizontalHeaderLabels(column_names)
    # Adjust the column width to fit the content or header
    self.Source_Cal_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    # the last column to stretch and fill the available space
    
    
    # Adjust source calibration table ----------------------
    column_names = ["X Cent. (Px)", "Y Cent. (Px)", "Rad. (Px)", "Init. Slice", "Last. Slice", "Trasnp.","R","G","B"]
    self.table_circ_roi.setColumnCount(9)
    self.table_circ_roi.setRowCount(0)
    #
    self.table_circ_roi.setHorizontalHeaderLabels(column_names)
    # Adjust the column width to fit the content or header
    self.table_circ_roi.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    #
    self.table_circ_roi.itemChanged.connect(lambda item: on_roitable_item_changed(self,item))
    
    # Adjust DECT RED table ----------------------
    column_names = ["Material","RED Ref.", "RED fit", "Diff.", "Diff. (%)"]
    self.tableRED.setColumnCount(5)
    self.tableRED.setRowCount(0)
    #
    self.tableRED.setHorizontalHeaderLabels(column_names)
    
    # Adjust DECT Zeff table ----------------------
    column_names = ["Material","Zeff Ref.", "Zeff fit", "Diff.", "Diff. (%)"]
    self.tableZeff.setColumnCount(5)
    self.tableZeff.setRowCount(0)
    #
    self.tableZeff.setHorizontalHeaderLabels(column_names)

    # Adjust DECT I-value table ----------------------
    column_names = ["Material","I Ref.", "I fit", "Diff.", "Diff. (%)"]
    self.tableIv.setColumnCount(5)
    self.tableIv.setRowCount(0)
    #
    self.tableIv.setHorizontalHeaderLabels(column_names)
    
    # Adjust DECT SPR table ----------------------
    column_names = ["Material","SPR Ref.", "SPR fit", "Diff.", "Diff. (%)"]
    self.tableSPR.setColumnCount(5)
    self.tableSPR.setRowCount(0)
    #
    self.tableSPR.setHorizontalHeaderLabels(column_names)


   # Adjust alphabeta table
    self.ab_table.setColumnCount(2)
    self.ab_table.setHorizontalHeaderLabels(["Structure Name", "α/β"])
    self.ab_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make it read-only
    self.ab_table.resizeColumnsToContents() 
    self.ab_table.resizeColumnsToContents() 
    
    #Material assignment table
    df=create_dataframe_materials(self)
    update_mat_properties_table(self,df)
    update_mat_table_style(self)
    self.tableMatToHU.setColumnCount(4)
    self.tableMatToHU.setHorizontalHeaderLabels(['Material', 'ID', 'From ', 'To'])
    self.mat_to_struct_tab.setColumnCount(3)
    self.mat_to_struct_tab.setHorizontalHeaderLabels(['Structure', 'Material', 'ID '])


