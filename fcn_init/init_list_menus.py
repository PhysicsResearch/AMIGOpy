from PySide6 import QtWidgets
from fcn_processing.Im_process_list   import on_operation_selected
from fcn_DECT.DECT_table_disp import on_DECT_list_selection_changed
from fcn_display.disp_plan_data import update_disp_brachy_plan
from fcn_display.display_images import update_layer_view
from fcn_ctcal.ct_cal import update_ct_cal_view,load_ct_cal_curve,update_ct_cal_table
from fcn_materialassignment.material_map import on_material_change
from fcn_dosecalculations.eqd2_conversion import on_struct_list_change
import os
import sys

# from fcn_3Dview.Prepare_data_3D_vtk import _on_colormap_changed

def safe_combo_items(parent, attr_or_name, items, default_index=None, default_text=None, callback=None):
    combo = getattr(parent, attr_or_name, None)
    if combo is None and hasattr(parent, 'findChild'):
        combo = parent.findChild(QtWidgets.QComboBox, attr_or_name)
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

    # Brachy channel or dwell view
    brachy_methods = ["Dwells", "Channels", "Ref. Points"]
    self.brachy_dw_ch_box_01 = safe_combo_items(self, 'brachy_combobox_01', brachy_methods)
    self.brachy_dw_ch_box_02 = safe_combo_items(self, 'brachy_combobox_02', brachy_methods)

    if self.brachy_dw_ch_box_01 is not None and self.brachy_dw_ch_box_02 is not None:
        def sync_box_1_to_2(index):
            if self.brachy_dw_ch_box_02 is not None:
                self.brachy_dw_ch_box_02.blockSignals(True)
                self.brachy_dw_ch_box_02.setCurrentIndex(index)
                self.brachy_dw_ch_box_02.blockSignals(False)
                update_disp_brachy_plan(self)

        def sync_box_2_to_1(index):
            if self.brachy_dw_ch_box_01 is not None:
                self.brachy_dw_ch_box_01.blockSignals(True)
                self.brachy_dw_ch_box_01.setCurrentIndex(index)
                self.brachy_dw_ch_box_01.blockSignals(False)
                update_disp_brachy_plan(self)

        try:
            self.brachy_dw_ch_box_01.currentIndexChanged.connect(sync_box_1_to_2)
            self.brachy_dw_ch_box_02.currentIndexChanged.connect(sync_box_2_to_1)
        except (TypeError, RuntimeError):
            pass

    # Color
    color_methods = ["Black", "Blue", "Green", "Red", "White"]
    self.brachy_dw_sel_col   = safe_combo_items(self, 'brachy_dw_color', color_methods, default_text="Red")
    self.brachy_lin_sel_col  = safe_combo_items(self, 'brachy_line_color', color_methods, default_text="White")
    self.brachy_p1_sel_col   = safe_combo_items(self, 'brachy_ch_p1_color', color_methods, default_text="Blue")

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

    # Ct calibration
    ct_cal_list = getattr(self, 'ct_cal_list', None)
    if ct_cal_list is not None and hasattr(ct_cal_list, 'currentTextChanged'):
        try:
            ct_cal_list.currentTextChanged.connect(lambda: update_ct_cal_view(self))
        except (TypeError, RuntimeError):
            pass

    self.ct_cal_curves = {}
    ct_cal_dir = get_appdata_ct_cal_dir()
    if os.path.exists(ct_cal_dir):
        ct_cal_files = os.listdir(ct_cal_dir)
        for file in ct_cal_files:
            file_path = os.path.join(ct_cal_dir, file)
            ct_cal_data = load_ct_cal_curve(self, fileName=file_path)
            update_ct_cal_table(self, ct_cal_data)
            update_ct_cal_view(self)

    # Material assignment
    select_mat = getattr(self, 'Select_mat', None)
    if select_mat is not None and hasattr(select_mat, 'currentTextChanged'):
        try:
            select_mat.currentTextChanged.connect(lambda: on_material_change(self))
        except (TypeError, RuntimeError):
            pass

    struct_list_mat = getattr(self, 'Struct_list_mat', None)
    if struct_list_mat is not None and hasattr(struct_list_mat, 'addItem'):
        if struct_list_mat.count() == 0:
            struct_list_mat.addItem('...Select Structure...')
    
    

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller stores data files in _MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_appdata_ct_cal_dir():
    """Returns the user-writable path to the ct_cal_curves folder under AppData/Local/AMIGOpy."""
    from pathlib import Path
    appdata_base = os.path.join(Path.home(), 'AppData', 'Local', 'AMIGOpy')
    ct_cal_dir = os.path.join(appdata_base, 'ct_cal_curves')
    os.makedirs(ct_cal_dir, exist_ok=True)

    # Copy default files from the bundled directory only if empty
    if not os.listdir(ct_cal_dir):
        default_dir = resource_path('fcn_ctcal/ct_cal_curves')
        if os.path.exists(default_dir):
            for fname in os.listdir(default_dir):
                src = os.path.join(default_dir, fname)
                dst = os.path.join(ct_cal_dir, fname)
                try:
                    with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
                        fdst.write(fsrc.read())
                except Exception as e:
                    print(f"Error copying {fname} to AppData: {e}")
    return ct_cal_dir