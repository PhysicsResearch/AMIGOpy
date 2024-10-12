from PyQt5 import QtWidgets
from fcn_processing.Im_process_list   import on_operation_selected
from fcn_DECT.DECT_table_disp import on_DECT_list_selection_changed

def populate_operation_list(self):
    # List of operations
    operations = ["none","Invert Image", "Average", "Sum","Crop","Normalize", "Threshold", "Denoise Gaussian","Denoise Median","Denoise Percentile",
                  "Denoise Min.","Denoise Max.", "Wiener", "FFT Gaussian","Gaussian Grad.","Gaussian Laplace","Sobel","Prewitt","TV Chambolle","Rolling ball","Wavelet",
                  "Bilateral","NL means","BM3D"]
    # Get the QComboBox by its name
    self.process_list = self.findChild(QtWidgets.QComboBox, 'Process_list')
    # Populate the QComboBox
    self.process_list.addItems(operations)
    # You can also connect the selection change event to a function
    self.process_list.currentIndexChanged.connect(lambda index: on_operation_selected(self, index))
    
    # CSV explore
    Separators = [",", ";", "\\t", " ", "|"]
    # Get the QComboBox by its name
    self.csv_sep_list = self.findChild(QtWidgets.QComboBox, 'CSVDeli_Sel')
    # Populate the QComboBox
    self.csv_sep_list.addItems(Separators)
    # List of operations
    operations_csv = ["Swap","Copy","Add Column","Add/Subtract", "Multiply", "Divide","Log","Exp.","Up.Thresh","Lw.Thresh"]
    # Get the QComboBox by its name
    self.operation_list_csv = self.findChild(QtWidgets.QComboBox, 'CSV_Oper_Box')
    # Populate the QComboBox
    self.operation_list_csv .addItems(operations_csv)
    
    # DECT MatInfo
    self.DECT_list_01.currentIndexChanged.connect(lambda index: on_DECT_list_selection_changed(self, index))
    #self.DECT_list_02.currentIndexChanged.connect(on_comboBox_selection_changed)
    
    # DECT - RED
    methods = ["Saito", "Hunemohr"]
    # Get the QComboBox by its name
    self.RED_method_list = self.findChild(QtWidgets.QComboBox, 'RED_method')
    # Populate the QComboBox
    self.RED_method_list.addItems(methods)

    # DECT - Zeff
    methods = ["Saito", "Hunemohr"]
    # Get the QComboBox by its name
    self.Zeff_method_list = self.findChild(QtWidgets.QComboBox, 'Zeff_method')
    # Populate the QComboBox
    self.Zeff_method_list.addItems(methods)
    
    # DECT - Ivalue
    methods = ["Saito", "Hunemohr"]
    # Get the QComboBox by its name
    self.Ivalue_method_list = self.findChild(QtWidgets.QComboBox, 'Ivaluefit_method')
    # Populate the QComboBox
    self.Ivalue_method_list.addItems(methods)
    
    # Iris correction
    methods = ["Add", "Sub."]
    # Get the QComboBox by its name
    self.IrIS_CorrFrame_operation = self.findChild(QtWidgets.QComboBox, 'IrIS_CorrFrame_oper')
    # Populate the QComboBox
    self.IrIS_CorrFrame_operation.addItems(methods)
    
    # Brachy channel or dwell view
    # 
    methods = ["Dwells", "Channels"]
    # Get the QComboBox by its name
    self.brachy_dw_ch_box_01 = self.findChild(QtWidgets.QComboBox, 'brachy_combobox_01')
    self.brachy_dw_ch_box_02 = self.findChild(QtWidgets.QComboBox, 'brachy_combobox_02')
    # Populate the QComboBox
    self.brachy_dw_ch_box_01.addItems(methods)
    self.brachy_dw_ch_box_02.addItems(methods)
    # Color
    methods = ["Black", "Blue", "Green", "Red", "White"]
    # Get the QComboBox by its name
    self.brachy_dw_sel_col   = self.findChild(QtWidgets.QComboBox, 'brachy_dw_color')
    self.brachy_lin_sel_col  = self.findChild(QtWidgets.QComboBox, 'brachy_line_color')
    self.brachy_p1_sel_col  = self.findChild(QtWidgets.QComboBox, 'brachy_ch_p1_color')
    # Populate the QComboBox
    self.brachy_dw_sel_col.addItems(methods)
    self.brachy_lin_sel_col.addItems(methods)
    self.brachy_p1_sel_col.addItems(methods)
    # Set default selections
    self.brachy_dw_sel_col.setCurrentText("Red")  # First combo box starts with "Green"
    self.brachy_lin_sel_col.setCurrentText("White")   # Second combo box starts with "Blue"
    self.brachy_p1_sel_col.setCurrentText("Blue")    # Third combo box starts with "Red"
    
    
    
    
    
    