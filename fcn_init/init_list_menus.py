from PyQt5 import QtWidgets
from fcn_processing.Im_process_list   import on_operation_selected
from fcn_DECT.DECT_table_disp import on_DECT_list_selection_changed
from fcn_display.disp_plan_data import update_disp_brachy_plan
from fcn_display.display_images import update_layer_view
from fcn_ctcal.ct_cal import update_ct_cal_view,load_ct_cal_curve,update_ct_cal_table
from fcn_materialassignment.material_map import on_material_change
import os
import sys

# from fcn_3Dview.Prepare_data_3D_vtk import _on_colormap_changed

def populate_list_menus(self):
    # self._imgs = {}        # layer_idx -> vtkImageData
    # self._ctfs = {}        # layer_idx -> vtkColorTransferFunction
    # self._otfs = {}        # layer_idx -> vtkPiecewiseFunction
    # self._vol_props = {}   # layer_idx -> vtkVolumeProperty
    # self._volumes = {}     # layer_idx -> vtkVolume
    # self._play3D_index = 0
    # cmap_list = ['Gray', 'Bone', 'Hot', 'Cool', 'Viridis',
    #              'Plasma', 'Jet', 'Rainbow', 'Spectral', 'BlueWhiteRed']
    # self.View3D_CMap = self.findChild(QtWidgets.QComboBox, 'View3D_colormap')
    # self.View3D_CMap.addItems(cmap_list)
    # self.View3D_CMap.currentIndexChanged.connect(
    #     lambda idx: _on_colormap_changed(self)
    # )

    # Populate selection box
    Layers = ["0", "1", "2", "3"]
    self.layer_selection_box = self.findChild(QtWidgets.QComboBox, 'Layer_selection')
    self.layer_selection_box.addItems(Layers)   
    self.layer_selection_box.currentIndexChanged.connect(lambda: update_layer_view(self))

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
    

    # Breathing curves
    Separators = [",", ";", "\\t", " ", "|"]
    self.csv_sep_list_BrCv = self.findChild(QtWidgets.QComboBox, 'selDelimCSV_BrCv')
    self.csv_sep_list_BrCv.addItems(Separators)
    
    time_units = ["ms", "s"]
    self.time_units_list_BrCv = self.findChild(QtWidgets.QComboBox, 'timeUnitCSV_BrCv')
    self.time_units_list_BrCv.addItems(time_units)
    
    cv_types = ["Cosine^2", "Cosine^4", "Cosine^6"]
    self.cv_type_list_BrCv = self.findChild(QtWidgets.QComboBox, 'cvType')
    self.cv_type_list_BrCv.addItems(cv_types)
    
    self.editXAxis_list_BrCv = self.findChild(QtWidgets.QComboBox, 'editXAxis_BrCv')
    self.editXAxis_list_BrCv.addItems(["timestamp", "time"])

    self.smooth_method_BrCv = self.findChild(QtWidgets.QComboBox, 'smooth_method_BrCv')
    self.smooth_method_BrCv.addItems(["Uniform", "Median", "Fourier"])
    
    self.fourier_cutoffs = [(x*y) for y in [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1] for x in list(range(1, 10))] 
    self.threshFourierSlider.setMinimum(0)
    self.threshFourierSlider.setMaximum(len(self.fourier_cutoffs) - 1)
    self.threshFourierSlider.setValue(19)
    
    # Segmentation
    views = ["Axial", "Coronal", "Sagittal"]
    self.views_list = self.findChild(QtWidgets.QComboBox, 'segSelectView')
    self.views_list.addItems(views)


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
    
    # Brachy -----------------------------------------------------------
    #
    along_away = ["Reference", "Calculated", "Comparison"]
    self.brachy_along_away_type = self.findChild(QtWidgets.QComboBox, 'comboBox_tg43_along_away')
    self.brachy_along_away_type.addItems(along_away)
    #
    DoseGrid = ["0.5","1","2","3","4","5"]
    self.brachy_tg43_dose_grid = self.findChild(QtWidgets.QComboBox, 'Tg43_dose_grid')
    self.brachy_tg43_dose_grid.addItems(DoseGrid)
    self.brachy_tg43_dose_grid.setCurrentIndex(1)
    #
    MatrixSize = ["50x50","100x100","150x150","200x200"]
    self.brachy_tg43_matrix_size = self.findChild(QtWidgets.QComboBox, 'Tg43_matrix_size_2')
    self.brachy_tg43_matrix_size.addItems(MatrixSize)
    self.brachy_tg43_matrix_size.setCurrentIndex(3)
    #
    # Brachy channel or dwell view
    # 
    methods = ["Dwells", "Channels"]
    # Get the QComboBox by its name
    self.brachy_dw_ch_box_01 = self.findChild(QtWidgets.QComboBox, 'brachy_combobox_01')
    self.brachy_dw_ch_box_02 = self.findChild(QtWidgets.QComboBox, 'brachy_combobox_02')
    # Populate the QComboBox
    self.brachy_dw_ch_box_01.addItems(methods)
    self.brachy_dw_ch_box_02.addItems(methods)
    # call back
    def sync_box_1_to_2(index):
        self.brachy_dw_ch_box_02.blockSignals(True)
        self.brachy_dw_ch_box_02.setCurrentIndex(index)
        self.brachy_dw_ch_box_02.blockSignals(False)
        update_disp_brachy_plan(self)

    def sync_box_2_to_1(index):
        self.brachy_dw_ch_box_01.blockSignals(True)
        self.brachy_dw_ch_box_01.setCurrentIndex(index)
        self.brachy_dw_ch_box_01.blockSignals(False)
        update_disp_brachy_plan(self)

    self.brachy_dw_ch_box_01.currentIndexChanged.connect(sync_box_1_to_2)
    self.brachy_dw_ch_box_02.currentIndexChanged.connect(sync_box_2_to_1)


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
    self.brachy_dw_sel_col.setCurrentText("Red")      # First combo box starts with "Green"
    self.brachy_lin_sel_col.setCurrentText("White")   # Second combo box starts with "Blue"
    self.brachy_p1_sel_col.setCurrentText("Blue")     # Third combo box starts with "Red"
     
    
    #Eqd2
    self.dose_list.addItems(['None'])
    self.eqd2_struct_list.addItems(['None'])
    

    #Ct calibration
    self.ct_cal_list.currentTextChanged.connect(lambda: update_ct_cal_view(self))
    #Initialize a list to store the CT calibration curves
    self.ct_cal_curves={}
    ct_cal_dir = resource_path('fcn_ctcal/ct_cal_curves')
    ct_cal_files = os.listdir(ct_cal_dir)
    for file in ct_cal_files:
        file_path = os.path.join(ct_cal_dir, file)
        ct_cal_data = load_ct_cal_curve(self, fileName=file_path)
        update_ct_cal_table(self,ct_cal_data)
        update_ct_cal_view(self)
    
    
    #Material assignment
    self.Select_mat.currentTextChanged.connect(lambda: on_material_change(self))
    self.Struct_list_mat.clear()
    self.Struct_list_mat.addItem('...Select Structure...')
    
    

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller stores data files in _MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)