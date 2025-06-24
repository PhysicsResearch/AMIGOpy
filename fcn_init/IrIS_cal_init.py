from fcn_IrIS.CalibrationMk_IrIS  import  plot_mk_cal_data, set_ref_shift, update_table, export_mk_pos2csv
from fcn_IrIS.CalibrationTable_IrIS  import load_csv_into_table, load_csv_ref_pro, load_referencecsv_into_table
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView


def init_cal_markers_IrIS(self):
    self.IrIS_cal_load_ref.clicked.connect(lambda: load_csv_into_table(self))
    self.IrIS_cal_load_meas.clicked.connect(lambda: load_csv_ref_pro(self))
    self.IrIS_cal_plot.clicked.connect(lambda: plot_mk_cal_data(self))
    self.IrIS_cal_save.clicked.connect(lambda: update_table(self))
    self.IrIS_cal_export.clicked.connect(lambda: export_mk_pos2csv(self))
    #
    self.IrIS_cal_Ref_MK_ID.valueChanged.connect(lambda: set_ref_shift(self))
    
    
    #
    # update plot when changing value
    self.IrIS_cal_MK_01.valueChanged.connect(lambda: plot_mk_cal_data(self))
    self.IrIS_cal_MK_02.valueChanged.connect(lambda: plot_mk_cal_data(self))
    self.IrIS_cal_MK_03.valueChanged.connect(lambda: plot_mk_cal_data(self))
    self.IrIS_cal_MK_04.valueChanged.connect(lambda: plot_mk_cal_data(self))
    self.IrIS_cal_MK_05.valueChanged.connect(lambda: plot_mk_cal_data(self))
    self.IrIS_cal_MK_06.valueChanged.connect(lambda: plot_mk_cal_data(self))
    #
    self.IrIS_cal_Sour_01.valueChanged.connect(lambda: plot_mk_cal_data(self))
    self.IrIS_cal_Sour_02.valueChanged.connect(lambda: plot_mk_cal_data(self))
    self.IrIS_cal_Sour_03.valueChanged.connect(lambda: plot_mk_cal_data(self))
    column_titles = ["X (mm)", "Y (mm)", "Z (mm)", "MK X (mm)", "MK Y (mm)", "Proj. X (mm)","Proj. Y (mm)"]
    #
    # Set the number of columns
    self.IrIS_cal_ref_table.setColumnCount(len(column_titles))
    #
    # Set the column titles
    self.IrIS_cal_ref_table.setHorizontalHeaderLabels(column_titles)
    #
    # Set the number of rows
    self.IrIS_cal_ref_table.setRowCount(108)
    #
    # Initialize all cells with zeros
    for row in range(108):
        for column in range(len(column_titles)):
            self.IrIS_cal_ref_table.setItem(row, column, QTableWidgetItem("0"))
            #
    # load reference values
    load_referencecsv_into_table(self)
    
    #
    
    
