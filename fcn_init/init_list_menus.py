from PySide6 import QtWidgets
from fcn_processing.Im_process_list   import on_operation_selected
from fcn_DECT.DECT_table_disp import on_DECT_list_selection_changed
from fcn_display.disp_plan_data import update_disp_brachy_plan
from fcn_display.display_images import update_layer_view
from fcn_display.layer_panel import init_layer_panel
# (material assignment is now edited directly in its tables - see material_map.py)
from fcn_dosecalculations.eqd2_conversion import on_struct_list_change
import os
import sys

# from fcn_3Dview.Prepare_data_3D_vtk import _on_colormap_changed

def safe_combo_items(parent, attr_or_name, items, default_index=None, default_text=None, callback=None):
    combo = getattr(parent, attr_or_name, None)
    if combo is not None and isinstance(combo, QtWidgets.QComboBox):
        if combo.count() == 0:
            combo.addItems(items)
            if default_index is not None:
                combo.setCurrentIndex(default_index)
            if default_text is not None:
                combo.setCurrentText(default_text)
            if callback is not None:
                combo.currentIndexChanged.connect(callback)
    return combo

def populate_list_menus(self):
    # Populate selection box
    Layers = ["1", "2", "3", "4"]
    self.layer_selected = safe_combo_items(self, 'layer_selected', Layers, callback=lambda: update_layer_view(self))
    if self.layer_selected is None:
        self.layer_selected = safe_combo_items(self, 'Layer_sel', Layers, callback=lambda: update_layer_view(self))
    init_layer_panel(self)      # layer names and colour map buttons of the side bar (once)

    # List of operations
    operations = ["none","Invert Image", "Average", "Sum","Crop","Normalize", "Threshold", "Denoise Gaussian","Denoise Median","Denoise Percentile",
                  "Denoise Min.","Denoise Max.", "Wiener", "FFT Gaussian","Gaussian Grad.","Gaussian Laplace","Sobel","Prewitt","TV Chambolle","Rolling ball","Wavelet",
                  "Bilateral","NL means","BM3D"]
    self.process_list = safe_combo_items(self, 'process_list', operations, callback=lambda idx: on_operation_selected(self, idx))
    if self.process_list is None:
        self.process_list = safe_combo_items(self, 'Process_list', operations, callback=lambda idx: on_operation_selected(self, idx))

    # Breathing curves
    Separators = [",", ";", "\\t", " ", "|"]
    self.csv_sep_list_BrCv = safe_combo_items(self, 'selDelimCSV_BrCv', Separators)
    self.time_units_list_BrCv = safe_combo_items(self, 'timeUnitCSV_BrCv', ["ms", "s"])
    self.cv_type_list_BrCv = safe_combo_items(self, 'cvType', ["Cosine^2", "Cosine^4", "Cosine^6"])
    self.editXAxis_list_BrCv = safe_combo_items(self, 'editXAxis_BrCv', ["timestamp", "time"])
    self.smooth_method_BrCv = safe_combo_items(self, 'smooth_method_BrCv', ["Fourier", "Uniform", "Median"])

    thresh_slider = getattr(self, 'threshFourierSlider', None)
    if thresh_slider is not None:
        self.fourier_cutoffs = [(x*y) for y in [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1] for x in list(range(1, 10))]
        thresh_slider.setMinimum(0)
        thresh_slider.setMaximum(len(self.fourier_cutoffs) - 1)
        thresh_slider.setValue(26)

    # Segmentation
    self.views_list = safe_combo_items(self, 'segSelectView', ["Axial", "Coronal", "Sagittal"])
    self.morph_oper_list = safe_combo_items(self, 'morph_oper_method', ['erosion', 'dilation', 'opening', 'closing'])

    # DECT MatInfo
    dect_list_01 = getattr(self, 'DECT_list_01', None)
    if dect_list_01 is not None and hasattr(dect_list_01, 'currentIndexChanged'):
        try:
            dect_list_01.currentIndexChanged.connect(lambda index: on_DECT_list_selection_changed(self, index))
        except (TypeError, RuntimeError):
            pass

    # DECT - RED, Zeff, Ivalue
    methods = ["Saito", "Hunemohr"]
    self.RED_method_list = safe_combo_items(self, 'RED_method', methods)
    self.Zeff_method_list = safe_combo_items(self, 'Zeff_method', methods)
    self.Ivalue_method_list = safe_combo_items(self, 'Ivaluefit_method', methods)

    # Iris correction
    self.IrIS_CorrFrame_operation = safe_combo_items(self, 'IrIS_CorrFrame_oper', ["Add", "Sub."])

    # Brachy
    self.brachy_along_away_type = safe_combo_items(self, 'comboBox_tg43_along_away', ["Reference", "Calculated", "Comparison"])
    self.brachy_tg43_dose_grid = safe_combo_items(self, 'Tg43_dose_grid', ["0.5","1","2","3","4","5"], default_index=1)
    self.brachy_tg43_matrix_size = safe_combo_items(self, 'Tg43_matrix_size_2', ["50x50","100x100","150x150","200x200"], default_index=3)

    # Brachy channel or dwell view (View > PLAN > Brachy table): a new mode lists it for the plan shown
    brachy_methods = ["Dwells", "Channels", "Ref. Points"]
    self.brachy_dw_ch_box_01 = safe_combo_items(self, 'brachy_combobox_01', brachy_methods,
                                                callback=lambda: update_disp_brachy_plan(self) if hasattr(self, 'patientID_plan') else None)

    # Eqd2
    dose_list = getattr(self, 'dose_list', None)
    if dose_list is not None and hasattr(dose_list, 'addItems'):
        if dose_list.count() == 0:
            dose_list.addItems(['None'])

    eqd2_struct_list = getattr(self, 'eqd2_struct_list', None)
    if eqd2_struct_list is not None and hasattr(eqd2_struct_list, 'addItems'):
        if eqd2_struct_list.count() == 0:
            eqd2_struct_list.addItems(['None'])
            try:
                eqd2_struct_list.currentTextChanged.connect(lambda: on_struct_list_change(self))
            except (TypeError, RuntimeError):
                pass

    # (HU tables of the Density Map tab: fcn_ctcal/ct_cal.py, init_ct_cal_selector in init_buttons)

    # Material assignment: the former Select_mat / Struct_list_mat combo boxes
    # were replaced by dropdowns inside the assignment tables.
    
    
