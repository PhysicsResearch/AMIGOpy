import vtk
from PySide6.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout
from PySide6.QtGui import QAction, QShortcut
from PySide6 import QtWidgets  # Import the correct module for QMessageBox
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Qt
from fcn_init.vtk_comparison_axes     import create_vtk_elements_comp
from fcn_IrIS.FindDwell_IrIS import add_row_dw_table, remove_row_dw_table
from fcn_processing.Im_process_list import image_processing_undo, run_image_processing
from fcn_processing.split_dcm_series import shift_and_split_3D_matrix
from fcn_processing.roi_circle import (toggle_rois, roi_c_add_row, roi_c_remove_row, export_roi_circ_table_to_csv, import_roi_circ_table, 
                                       c_roi_getdata, export_roi_circ_values_to_csv, export_all_roi_voxel_values_to_csv, on_all_series_checkbox_toggled, roi_c_clear_all_rois, roi_c_clear_all_data)
from fcn_IrIS.Load_CorrectionFrames import load_offset_IrIS, load_CorrectionFrame_IrIS
from fcn_DECT.DECT_table_disp        import remove_coll2table, add_row2table, remove_row2table, reset_matTable, add_coll2table, calc_material_parameters, load_csv_mat_info
from fcn_4DCT.disp_4D import play_4D_sequence
from fcn_DECT.export_data import export_matinfotable_to_csv
from fcn_DECT.RED_calc_plot import RED_copy_ref_columns, RED_fit_plot_fcn
from fcn_DECT.zeff_calc_plot import Zeff_copy_ref_columns, Zeff_fit_plot_fcn
from fcn_DECT.ivalue_calc_plot import Iv_copy_ref_columns, Iv_fit_plot_fcn
from fcn_DECT.spr_calc_plot import SPR_copy_ref_columns, SPR_fit_plot_fcn
from fcn_DECT.DECT_table_disp import c_roi_getdata_HU_high_low
from fcn_DECT.Ivalue_Zeff_fit import plot_I_value_points, plot_I_value_precalc, cal_plot_I_value_points
from fcn_DECT.create_process_dect import creat_DECT_derived_maps, c_roi_scatter_plot, export_all_DECT_tables, save_parameters_to_csv, load_parameters_from_csv
from fcn_display.disp_plan_data import update_disp_brachy_plan,  plot_brachy_dwell_channels, export_all_brachy_channels_to_csv
from fcn_brachy_sources.process_brachy_database import (on_brachy_load_sources, on_brachy_source_selection, select_Radial_file2load, plot_brachy_radial_fit, plot_brachy_ani,
                                                        select_Anisotropy_file2load)
from fcn_brachy_sources.process_brachy_database import dose_along_away_Disp_eval
from fcn_display.display_images  import displayaxial, displaycoronal, displaysagittal
from fcn_display.meta_viewer import on_metadata_search_text_changed
from fcn_RTFiles.process_contours import create_contour_masks
from fcn_breathing_curves.functions_import import openCSVFile_BrCv, setParams, createCurve
from fcn_breathing_curves.functions_plot import calcStats, plotViewData_BrCv_plot, exportPlot
from fcn_breathing_curves.functions_edit import applyOperations, undoOperations, exportData, plotViewData_BrCv_edit, cropRange_BrCv_edit, exportGCODE#, cropCurve_BrCv_edit
from fcn_breathing_curves.functions_phantom_operation import setDuetIP, defineInputFolder, setAcqStart, exportMoVeData
from fcn_dosecalculations.eqd2_conversion import add_ab, delete_ab, generate_eqd2_dose, create_ab_matrix, eqd2_calc
from fcn_segmentation.functions_segmentation import (threshSeg, on_brush_click, on_erase_click, InitSeg, calcStrucStats, exportStrucStats, exportSegStruc, 
                                                     DeleteSeg, undo_brush_seg, apply_morph_oper, undo_morph_oper)
from fcn_ctcal.ct_cal import load_ct_cal_curve,save_changes,add_row_to_ct_table, export_ct_cal_to_csv
from fcn_densitymap.density_map import create_density_map,del_density_map
from fcn_brachy.cal_TG43_dose import calculate_TG43_plan_dose
from fcn_3Dview.volume_3d_viewer import play_4D_sequence_3D
from fcn_materialassignment.material_assignment_properties import add_mat_row,del_mat_row,add_element,del_element,save_mat_db,undo_changes
from fcn_brachy.cal_TG43_dose import calculate_TG43_plan_dose
from fcn_materialassignment.material_map import mat2HU,del_mat2HU,generate_mat_map,delete_mat_map,struct2mat,del_stuct2mat,update_mat_struct_list
from fcn_3DPrinting.material_selection import calculate_red_settings
from fcn_3DPrinting import handlers as hdl
from fcn_reg.rigid_reg_manual import update_translation_x, update_translation_y, update_translation_z, update_rotation_x, update_rotation_y, update_rotation_z, set_transformation_step, apply_trasnformation, flip_volume_x, flip_volume_y, flip_volume_z
from fcn_reg.auto_reg_dialog import open_auto_reg_dialog, apply_last_transform_to_layer





def safe_btn(parent, attr_name, signal_name, callback, style=None):
    btn = getattr(parent, attr_name, None)
    if btn is not None and hasattr(btn, signal_name):
        try:
            signal = getattr(btn, signal_name)
            signal.connect(callback)
            if style and hasattr(btn, 'setStyleSheet'):
                btn.setStyleSheet(style)
        except (TypeError, RuntimeError):
            pass
    elif btn is not None and style and hasattr(btn, 'setStyleSheet'):
        try:
            btn.setStyleSheet(style)
        except (TypeError, RuntimeError):
            pass
    return btn

def safe_style(parent, attr_name, style):
    btn = getattr(parent, attr_name, None)
    if btn is not None and hasattr(btn, 'setStyleSheet'):
        try:
            btn.setStyleSheet(style)
        except (TypeError, RuntimeError):
            pass
    return btn

def initialize_software_buttons(self):


    # IrIS add row dw table
    safe_btn(self, 'add_dw_table', 'clicked', lambda: add_row_dw_table(self))
    safe_btn(self, 'remove_dw_table', 'clicked', lambda: remove_row_dw_table(self))
    
    #Metadata
    safe_btn(self, 'metadata_search', 'textChanged', lambda text: on_metadata_search_text_changed(self,text))

    # Image processing
    safe_btn(self, 'ImageUndo_operation', 'clicked', lambda: image_processing_undo(self), "background-color: green; color: white;")
    #

    # Breathing curves explore
    safe_btn(self, 'loadCSVView_BrCv', 'clicked', lambda: openCSVFile_BrCv(self), "background-color: green; color: white;")
    safe_btn(self, 'setParamsCreateCv', 'clicked', lambda: setParams(self))
    safe_btn(self, 'createCv', 'clicked', lambda: createCurve(self), "background-color: green; color: white;")
    safe_btn(self, 'calcStats_BrCv', 'clicked', lambda: calcStats(self), "background-color: green; color: white;")
    safe_btn(self, 'plotView_BrCv', 'clicked', lambda: plotViewData_BrCv_plot(self), "background-color: green; color: white;")
    # self.plotExport_BrCv.clicked.connect(lambda: exportPlot(self))
    # self.plotExport_BrCv.setStyleSheet("background-color: blue; color: white")
    safe_btn(self, 'applyOper_BrCv', 'clicked', lambda: applyOperations(self), "background-color: green; color: white")
    safe_btn(self, 'undoOperations_BrCv', 'clicked', lambda: undoOperations(self), "background-color: green; color: white")
    safe_btn(self, 'exportData_BrCv', 'clicked', lambda: exportData(self), "background-color: blue; color: white")
    safe_btn(self, 'exportGCODE_BrCv', 'clicked', lambda: exportGCODE(self), "background-color: blue; color: white")
    safe_btn(self, 'cropRangeEdit_BrCv', 'clicked', lambda: cropRange_BrCv_edit(self), "background-color: blue; color:white")
    safe_btn(self, 'loadDuetPage', 'clicked', lambda: setDuetIP(self), "background-color: blue; color:white")
    safe_btn(self, 'definePhOperFolder', 'clicked', lambda: defineInputFolder(self), "background-color: blue; color:white")
    safe_btn(self, 'MoVeAcqStart', 'clicked', lambda: setAcqStart(self), "background-color: green; color:white")
    safe_btn(self, 'exportDataMoVe', 'clicked', lambda: exportMoVeData(self), "background-color: green; color:white")

    # Segmentation
    from fcn_display.display_images_seg import update_seg_slider, disp_seg_image_slice
    from fcn_segmentation.functions_segmentation import plot_hist
    from PySide6.QtGui import QIcon

    safe_btn(self, 'segViewSlider', 'valueChanged', lambda val: disp_seg_image_slice(self))
    safe_btn(self, 'segSelectView', 'currentTextChanged', lambda text: update_seg_slider(self))
    safe_btn(self, 'threshMinHU', 'textChanged', lambda text: plot_hist(self))
    safe_btn(self, 'threshMaxHU', 'textChanged', lambda text: plot_hist(self))

    if hasattr(self, 'segViewSlider') and self.segViewSlider is not None and hasattr(self.segViewSlider, 'setSingleStep'):
        self.segViewSlider.setSingleStep(1)
        self.segViewSlider.setPageStep(1)

    t_min = getattr(self, 'threshMinHU', None)
    t_max = getattr(self, 'threshMaxHU', None)
    if t_min is not None and hasattr(t_min, 'setText') and not t_min.text():
        t_min.setText("-200")
    if t_max is not None and hasattr(t_max, 'setText') and not t_max.text():
        t_max.setText("200")

    b_brush = getattr(self, 'segBrushButton', None)
    b_erase = getattr(self, 'segEraseButton', None)
    b_undo = getattr(self, 'undoSeg', None)
    if b_brush is not None and hasattr(b_brush, 'setIcon'):
        b_brush.setIcon(QIcon("./icons/brush.png"))
    if b_erase is not None and hasattr(b_erase, 'setIcon'):
        b_erase.setIcon(QIcon("./icons/eraser.png"))
    if b_undo is not None and hasattr(b_undo, 'setIcon'):
        b_undo.setIcon(QIcon("./icons/undo.png"))

    safe_btn(self, 'applyThreshSeg', 'clicked', lambda: threshSeg(self), "background-color: blue; color:white")
    safe_btn(self, 'segBrushButton', 'clicked', lambda: on_brush_click(self))
    safe_btn(self, 'segEraseButton', 'clicked', lambda: on_erase_click(self))
    safe_btn(self, 'undoSeg', 'clicked', lambda: undo_brush_seg(self))
    safe_btn(self, 'createSegStruct', 'clicked', lambda: InitSeg(self), "background-color: green; color:white")
    safe_btn(self, 'calcSegStatsButton', 'clicked', lambda: calcStrucStats(self), "background-color: green; color:white")
    safe_btn(self, 'deleteSegStruct', 'clicked', lambda: DeleteSeg(self), "background-color: red; color:white")
    safe_btn(self, 'exportSegStatsButton', 'clicked', lambda: exportStrucStats(self), "background-color: blue; color:white")
    safe_btn(self, 'exportSegStrucButton', 'clicked', lambda: exportSegStruc(self), "background-color: blue; color:white")
    safe_btn(self, 'ApplyMorphOper', 'clicked', lambda: apply_morph_oper(self), "background-color: blue; color:white")
    safe_btn(self, 'UndoMorphOper', 'clicked', lambda: undo_morph_oper(self), "background-color: blue; color:white")
    
    # Connect the button's clicked signal to the slot function - run im processing operations
    safe_btn(self, 'run_im_process', 'clicked', lambda: run_image_processing(self), "background-color: blue; color: white;")
    
    # IrIS correction
    safe_btn(self, 'IrIS_Load_Offset', 'clicked', lambda: load_offset_IrIS(self), "background-color: red; color: white;")
    safe_btn(self, 'IrIS_Load_CorrectionFrame', 'clicked', lambda: load_CorrectionFrame_IrIS(self), "background-color: red; color: white;")
    
    # create vtk comp axes -button (only if im_compare_tab has been created)
    if hasattr(self, 'gridLayout_16') and self.gridLayout_16 is not None:
        from fcn_init.vtk_comparison_axes import on_grid_preset_changed
        self.combo_grid_presets = QtWidgets.QComboBox(self.im_compare_tab)
        self.combo_grid_presets.setObjectName("combo_grid_presets")
        self.combo_grid_presets.addItems([
            "Select Grid Preset",
            "1 Row x 1 Col",
            "1 Row x 2 Col",
            "1 Row x 3 Col",
            "1 Row x 4 Col",
            "2 Rows x 1 Col",
            "2 Rows x 2 Col",
            "2 Rows x 3 Col",
            "2 Rows x 4 Col",
            "3 Rows x 1 Col",
            "3 Rows x 2 Col",
            "3 Rows x 3 Col",
            "3 Rows x 4 Col"
        ])
        # Place it to the left of create button (replacing spacer in column 7)
        self.gridLayout_16.addWidget(self.combo_grid_presets, 3, 7, 1, 1)
        safe_btn(self, 'combo_grid_presets', 'currentIndexChanged', lambda idx: on_grid_preset_changed(self, idx))

        # Sync Checkboxes (Colormaps and Contours) in Column 2
        from fcn_display.colormap_set import on_link_colormap_changed
        from fcn_display.display_images_comp import on_link_contours_changed
        
        self.comp_sync_layout = QtWidgets.QHBoxLayout()
        self.comp_sync_layout.setContentsMargins(0, 0, 0, 0)
        
        self.Comp_linkColormaps = QtWidgets.QCheckBox(self.im_compare_tab)
        self.Comp_linkColormaps.setObjectName("Comp_linkColormaps")
        self.Comp_linkColormaps.setText("Link colormap")
        self.Comp_linkColormaps.setChecked(True)
        self.comp_sync_layout.addWidget(self.Comp_linkColormaps)
        safe_btn(self, 'Comp_linkColormaps', 'stateChanged', lambda: on_link_colormap_changed(self))
        
        self.Comp_linkContours = QtWidgets.QCheckBox(self.im_compare_tab)
        self.Comp_linkContours.setObjectName("Comp_linkContours")
        self.Comp_linkContours.setText("Link contours")
        self.Comp_linkContours.setChecked(True)
        self.comp_sync_layout.addWidget(self.Comp_linkContours)
        safe_btn(self, 'Comp_linkContours', 'stateChanged', lambda: on_link_contours_changed(self))

        self.Comp_linkTools = QtWidgets.QCheckBox(self.im_compare_tab)
        self.Comp_linkTools.setObjectName("Comp_linkTools")
        self.Comp_linkTools.setText("Link tools")
        self.Comp_linkTools.setChecked(True)
        self.comp_sync_layout.addWidget(self.Comp_linkTools)
        
        self.gridLayout_16.addLayout(self.comp_sync_layout, 3, 2, 1, 1)

        from fcn_display.display_images_comp import change_comp_view_orientation, sync_comp_dropdown_to_viewport
        safe_btn(self, 'Comp_view_sel_box', 'currentIndexChanged', lambda idx: change_comp_view_orientation(self, idx))
        safe_btn(self, 'Comp_im_idx', 'valueChanged', lambda idx: sync_comp_dropdown_to_viewport(self, idx))

        safe_btn(self, 'but_create_comp_axes', 'clicked', lambda: create_vtk_elements_comp(self), "background-color: blue; color: white;")

        # Modeless comparison window level popup button
        from fcn_init.view_hist import open_compare_histogram
        self.but_hist_comp = QtWidgets.QPushButton(self.im_compare_tab)
        self.but_hist_comp.setObjectName("but_hist_comp")
        self.but_hist_comp.setText("Window")
        self.but_hist_comp.setStyleSheet("background-color: blue; color: white;")
        # Place it to the right of Create button (column 9)
        self.gridLayout_16.addWidget(self.but_hist_comp, 3, 9, 1, 1)
        safe_btn(self, 'but_hist_comp', 'clicked', lambda: open_compare_histogram(self))

        # Add Ctrl+W shortcut on Compare tab to open Window dialog
        self.shortcut_comp_window = QShortcut(QKeySequence("Ctrl+W"), self.im_compare_tab)
        self.shortcut_comp_window.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.shortcut_comp_window.activated.connect(lambda: open_compare_histogram(self))

    # 4D Display
    safe_btn(self, 'Play4D_Buttom', 'toggled', lambda: play_4D_sequence(self), "background-color: blue; color: white;")

    # 3D viewer
    # 4D video
    if hasattr(self, 'View3D_play4D') and self.View3D_play4D is not None:
        self.View3D_play4D.setCheckable(True)
    safe_btn(self, 'View3D_play4D', 'toggled', lambda: play_4D_sequence_3D(self,1), "background-color: blue; color: white;")
    safe_btn(self, 'View3D_clear_all', 'clicked', getattr(self, 'clear_3d_axes', None), "background-color: blue; color: white;")
    safe_btn(self, 'View3D_reset_camera', 'clicked', getattr(self, 'reset_3d_camera', None), "background-color: blue; color: white;")
    

    # DECT
    safe_btn(self, 'add_coll_table_mat', 'clicked', lambda: add_coll2table(self), "background-color: blue; color: white;")
    safe_btn(self, 'remove_coll_table_mat', 'clicked', lambda: remove_coll2table(self), "background-color: blue; color: white;")
    safe_btn(self, 'add_row_table_mat', 'clicked', lambda: add_row2table(self), "background-color: blue; color: white;")
    safe_btn(self, 'remove_row_table_mat', 'clicked', lambda: remove_row2table(self), "background-color: blue; color: white;")
    safe_btn(self, 'reset_table_mat', 'clicked', lambda: reset_matTable(self), "background-color: blue; color: white;")
    
    # Load material composition and additional info
    safe_btn(self, 'Load_csv_mat', 'clicked', lambda: load_csv_mat_info(self), "background-color: blue; color: white;")
    safe_btn(self, 'cal_mat_ref_info', 'clicked', lambda: calc_material_parameters(self), "background-color: blue; color: white;")
    # I-value plot
    safe_btn(self, 'Ivalue_plot', 'clicked', lambda: plot_I_value_points(self), "background-color: blue; color: white;")
    # Instead of plotting from data use the providded coefficients
    safe_btn(self, 'Ivalue_pre_calc_fit', 'clicked', lambda: plot_I_value_precalc(self), "background-color: blue; color: white;")
    safe_btn(self, 'Ivalue_calc_fit', 'clicked', lambda: cal_plot_I_value_points(self), "background-color: blue; color: white;")
    # export mat table
    safe_btn(self, 'export_table_mat', 'clicked', lambda: export_matinfotable_to_csv(self), "background-color: blue; color: white;")
    safe_btn(self, 'get_HU_high', 'clicked', lambda: c_roi_getdata_HU_high_low(self), "background-color: green; color: white;")
    # RED
    safe_btn(self, 'RED_get_ref', 'clicked', lambda: RED_copy_ref_columns(self), "background-color: green; color: white;")
    safe_btn(self, 'RED_calc_cal', 'clicked', lambda: RED_fit_plot_fcn(self), "background-color: blue; color: white;")
    
    # Zeff
    safe_btn(self, 'Zeff_get_ref', 'clicked', lambda: Zeff_copy_ref_columns(self), "background-color: green; color: white;")
    safe_btn(self, 'Zeff_calc_cal', 'clicked', lambda: Zeff_fit_plot_fcn(self), "background-color: blue; color: white;")
    
    # I-value
    safe_btn(self, 'Iv_get_ref', 'clicked', lambda: Iv_copy_ref_columns(self), "background-color: green; color: white;")
    safe_btn(self, 'Iv_calc_cal', 'clicked', lambda: Iv_fit_plot_fcn(self), "background-color: blue; color: white;")
    
    # SPR
    safe_btn(self, 'SPR_get_ref', 'clicked', lambda: SPR_copy_ref_columns(self), "background-color: green; color: white;")
    safe_btn(self, 'SPR_calc_cal', 'clicked', lambda: SPR_fit_plot_fcn(self), "background-color: blue; color: white;")
    
    # Process Eval - DECT
    safe_btn(self, 'Create_DECT_Images', 'clicked', lambda: creat_DECT_derived_maps(self), "background-color: green; color: white;")
    #
    safe_btn(self, 'plot_roi_scatter', 'clicked', lambda: c_roi_scatter_plot(self), "background-color: green; color: white;")
    
    #
    safe_btn(self, 'export_all_DECT_tables', 'clicked', lambda: export_all_DECT_tables(self), "background-color: blue; color: white;")
    #
    safe_btn(self, 'DECT_exp_fit_par', 'clicked', lambda: save_parameters_to_csv(self), "background-color: blue; color: white;")
    #
    safe_btn(self, 'DECT_load_fit_par', 'clicked', lambda: load_parameters_from_csv(self), "background-color: green; color: white;")
    
    # Struct
    safe_btn(self, 'CreateMask_Structures', 'clicked', lambda: create_contour_masks(self), "background-color: blue; color: white;")

    # Image registrations
    safe_btn(self, 'Reg_manual_Tx', 'valueChanged', lambda: update_translation_x(self))
    safe_btn(self, 'Reg_manual_Ty', 'valueChanged', lambda: update_translation_y(self))
    safe_btn(self, 'Reg_manual_Tz', 'valueChanged', lambda: update_translation_z(self))
    safe_btn(self, 'Reg_manual_Rot_X', 'valueChanged', lambda: update_rotation_x(self))
    safe_btn(self, 'Reg_manual_Rot_Y', 'valueChanged', lambda: update_rotation_y(self))
    safe_btn(self, 'Reg_manual_Rot_Z', 'valueChanged', lambda: update_rotation_z(self))
    safe_btn(self, 'Manual_reg_step', 'valueChanged', lambda: set_transformation_step(self))
    # Flip buttons
    safe_btn(self, 'pushButton_4', 'clicked', lambda: flip_volume_x(self))
    safe_btn(self, 'pushButton_5', 'clicked', lambda: flip_volume_y(self))
    safe_btn(self, 'pushButton_6', 'clicked', lambda: flip_volume_z(self))
    safe_style(self, 'pushButton_4', "background-color: blue; color: white;")
    safe_style(self, 'pushButton_5', "background-color: blue; color: white;")
    safe_style(self, 'pushButton_6', "background-color: blue; color: white;")
    # Dynamic Auto Registration buttons
    from PySide6.QtWidgets import QPushButton
    self.btn_auto_registration = QPushButton("Auto Registration...", self.groupBox_12)
    self.btn_auto_registration.setObjectName("btn_auto_registration")
    safe_style(self, 'btn_auto_registration', "background-color: darkgreen; color: white; font-weight: bold;")
    self.gridLayout_82.addWidget(self.btn_auto_registration, 3, 1, 1, 2)
    safe_btn(self, 'btn_auto_registration', 'clicked', lambda: open_auto_reg_dialog(self))

    self.btn_apply_last_transform = QPushButton("Apply Last Transform", self.groupBox_12)
    self.btn_apply_last_transform.setObjectName("btn_apply_last_transform")
    safe_style(self, 'btn_apply_last_transform', "background-color: darkgreen; color: white; font-weight: bold;")
    self.gridLayout_82.addWidget(self.btn_apply_last_transform, 3, 3, 1, 2)
    safe_btn(self, 'btn_apply_last_transform', 'clicked', lambda: apply_last_transform_to_layer(self))

    # Apply button
    safe_btn(self, 'apply_Im_transformation', 'clicked', lambda: apply_trasnformation(self), "background-color: blue; color: white;")
    
    # Layer selection shortcuts (Ctrl+1 to Ctrl+4)
    def _switch_layer(parent, target_idx):
        if hasattr(parent, 'set_active_layer'):
            parent.set_active_layer(target_idx)
        elif hasattr(parent, 'layer_selected') and parent.layer_selected is not None:
            if 0 <= target_idx < parent.layer_selected.count():
                parent.layer_selected.setCurrentIndex(target_idx)
                from fcn_display.display_images import update_layer_view
                update_layer_view(parent)

    for l_idx, key_seq in enumerate(["Ctrl+1", "Ctrl+2", "Ctrl+3", "Ctrl+4"]):
        sc = QShortcut(QKeySequence(key_seq), self)
        sc.setContext(Qt.ApplicationShortcut)
        sc.activated.connect(lambda idx=l_idx: _switch_layer(self, idx))
        setattr(self, f"shortcut_layer_{l_idx}", sc)

    # -----------------------------------------
    # Plan
    # ------------------------------------------
    # Brachy 
    #
    # spin
    safe_btn(self, 'brachy_spinBox_01', 'valueChanged', lambda: update_disp_brachy_plan(self))
    safe_btn(self, 'brachy_spinBox_02', 'valueChanged', lambda: sync_spinBox_01(self))
    def sync_spinBox_01(self):
        # Update brachy_spinBox_01's value to match brachy_spinBox_02
        self.brachy_spinBox_01.setValue(self.brachy_spinBox_02.value())
    #
    safe_btn(self, 'display_dw_overlay', 'stateChanged', lambda: on_display_dw_overlay_clicked(self))
    safe_btn(self, 'display_brachy_channel_overlay', 'stateChanged', lambda: on_display_dw_overlay_clicked(self))
    # buttom    
    safe_btn(self, 'brachy_ch_plot', 'clicked', lambda:  plot_brachy_dwell_channels(self), "background-color: blue; color: white;")
    #
    safe_style(self, 'brachy_export_dw_channels_csv', "background-color: blue; color: white;")
    safe_btn(self, 'brachy_export_dw_channels_csv', 'clicked', lambda: export_all_brachy_channels_to_csv(self))
    #
    safe_btn(self, 'Brachy_load_sources', 'clicked', lambda: on_brachy_load_sources(self), "background-color: blue; color: white;")
    safe_btn(self, 'Brachy_load_sources', 'clicked', lambda: plot_brachy_ani(self))
    safe_btn(self, 'brachy_source_list', 'currentIndexChanged', lambda: on_brachy_source_selection(self))
    safe_btn(self, 'comboBox_tg43_along_away', 'currentIndexChanged', lambda: dose_along_away_Disp_eval(self))
    #
    # TG43 
    safe_style(self, 'Brachy_Radial_load', "background-color: blue; color: white;")
    safe_btn(self, 'Brachy_Radial_load', 'clicked', lambda: select_Radial_file2load(self))
    safe_btn(self, 'Brachy_Radial_table', 'itemChanged', lambda: plot_brachy_radial_fit(self))
    safe_style(self, 'Brach_plot_ani', "background-color: blue; color: white;")
    safe_btn(self, 'Brach_plot_ani', 'clicked', lambda: plot_brachy_ani(self))
    safe_style(self, 'Brachy_load_ani', "background-color: blue; color: white;")
    safe_btn(self, 'Brachy_load_ani', 'clicked', lambda: select_Anisotropy_file2load(self))

    # using a place holder button for testing
    safe_btn(self, 'Brachy_Calcualte_TG43', 'clicked', lambda: calculate_TG43_plan_dose(self), "background-color: blue; color: white;")
    #EQD2
    safe_btn(self, 'calc_eqd2', 'clicked', lambda: generate_eqd2_dose(self))
    safe_btn(self, 'add_to_ab_list', 'clicked', lambda: add_ab(self))
    safe_btn(self, 'delete_from_ab_list', 'clicked', lambda: delete_ab(self))
    
    safe_btn(self, 'calc_eqd2_2', 'clicked', lambda: eqd2_calc(self))
    safe_btn(self, 'ab_matrix', 'clicked', lambda: create_ab_matrix(self))

    #CT CALIBRATION--------------------------------------------------------------------------
    safe_btn(self, 'load_ct_cal', 'clicked', lambda: load_ct_cal_curve(self))
    safe_btn(self, 'save_changes_ct_cal', 'clicked', lambda: save_changes(self))
    safe_btn(self, 'ct_cal_add_row', 'clicked', lambda: add_row_to_ct_table(self))
    safe_btn(self, 'Export_ct_cal', 'clicked', lambda: export_ct_cal_to_csv(self))
    safe_btn(self, 'ct_cal_save_copy', 'clicked', lambda:export_ct_cal_to_csv(self,export=False))
    safe_btn(self, 'create_density_map', 'clicked', lambda:create_density_map(self), "background-color: green; color: white;")
    safe_btn(self, 'create_density_map__from_mat_map', 'clicked', lambda:create_density_map(self,use_mat_map=True), "background-color: green; color: white;")
    safe_btn(self, 'delete_density_map', 'clicked', lambda:del_density_map(self), "background-color: red; color: white;")
    
    #Material assignment
    safe_btn(self, 'Add_mat', 'clicked', lambda: add_mat_row(self))
    safe_btn(self, 'add_element', 'clicked', lambda:add_element(self))
    safe_btn(self, 'del_element', 'clicked', lambda:del_element(self))
    safe_btn(self, 'del_mat', 'clicked', lambda:del_mat_row(self))
    safe_btn(self, 'save_mat_table', 'clicked', lambda:save_mat_db(self))
    safe_btn(self, 'mat_to_hu', 'clicked', lambda:mat2HU(self))
    safe_btn(self, 'remove_mat_fromhu', 'clicked', lambda:del_mat2HU(self))
    safe_btn(self, 'create_mat_map', 'clicked', lambda:generate_mat_map(self), "background-color: green; color: white;")
    safe_btn(self, 'undo_mat_tab', 'clicked', lambda:undo_changes(self))
    safe_btn(self, 'del_mat_map', 'clicked', lambda:delete_mat_map(self), "background-color: red; color: white;")
    safe_btn(self, 'mat_to_struct', 'clicked', lambda:struct2mat(self))
    safe_btn(self, 'remove_mat_from_struct', 'clicked', lambda: del_stuct2mat(self))
    safe_btn(self, 'update_mat_struct_list', 'clicked', lambda: update_mat_struct_list(self))
    
    # 3D Printing buttons connect
    # setStyleSheet("background-color: green; color: white;")
    safe_btn(self, 'import_reference_btn', 'clicked', lambda: hdl.import_reference_file(self))
    safe_btn(self, 'import_tested_filaments_btn', 'clicked', lambda: hdl.load_gammex_file(self))
    safe_btn(self, 'load_cal_btn', 'clicked', lambda: hdl.load_cal_file(self))
    safe_btn(self, 'show_filaments_button', 'clicked', lambda: hdl.show_best_matching_filaments(self))
    safe_btn(self, 'RED_calc_button', 'clicked', lambda: hdl.calculate_red(self))


 
    # Circle ROI -----------------------------------------------------------------------------------
    # display (or not) ROI
    safe_btn(self, 'checkBox_circ_roi_data_2', 'clicked', lambda: toggle_rois(self))
    self.roi_circle_add_row.setText("Add")
    safe_style(self, 'roi_circle_add_row', "background-color: blue; color: white;")
    safe_btn(self, 'roi_circle_add_row', 'clicked', lambda: roi_c_add_row(self))
    self.roi_circle_remove_row.setText("Remove")
    safe_style(self, 'roi_circle_remove_row', "background-color: blue; color: white;")
    safe_btn(self, 'roi_circle_remove_row', 'clicked', lambda: roi_c_remove_row(self))
    safe_btn(self, 'circ_roi_exp_csv', 'clicked', lambda: export_roi_circ_table_to_csv(self), "background-color: blue; color: white;")
    safe_btn(self, 'circ_roi_load_csv', 'clicked', lambda: import_roi_circ_table(self), "background-color: green; color: white;")
    safe_btn(self, 'get_circ_roi_data', 'clicked', lambda: c_roi_getdata(self, ask_user=True), "background-color: blue; color: white;")
    safe_btn(self, 'get_circ_roi_data2', 'clicked', lambda: c_roi_getdata(self, ask_user=True), "background-color: blue; color: white;")
    safe_btn(self, 'checkBox_circ_roi_data_01', 'clicked', lambda: on_all_series_checkbox_toggled(self))
    if hasattr(self, 'holdOnROI'):
        self.holdOnROI.setVisible(False)
        
    self.btn_clear_all_rois = QPushButton("Clear All ROIs", self.tab_34)
    safe_style(self, 'btn_clear_all_rois', "background-color: #ef4444; color: white; font-weight: bold;")
    safe_btn(self, 'btn_clear_all_rois', 'clicked', lambda: roi_c_clear_all_rois(self))

    # Create Export Voxel Values button and place it where GET DATA was (2, 1)
    self.btn_export_voxel_values = QPushButton("Export Voxel Values", self.tab_34)
    safe_style(self, 'btn_export_voxel_values', "background-color: blue; color: white;")
    safe_btn(self, 'btn_export_voxel_values', 'clicked', lambda: export_all_roi_voxel_values_to_csv(self))

    # Shift GET DATA, Clear All ROIs, and All image series one column to the right
    if hasattr(self, 'get_circ_roi_data'):
        self.gridLayout_45.removeWidget(self.get_circ_roi_data)
    if hasattr(self, 'checkBox_circ_roi_data_01'):
        self.gridLayout_45.removeWidget(self.checkBox_circ_roi_data_01)

    self.gridLayout_45.addWidget(self.btn_export_voxel_values, 2, 1, 1, 1)
    if hasattr(self, 'get_circ_roi_data'):
        self.gridLayout_45.addWidget(self.get_circ_roi_data, 2, 2, 1, 1)
    self.gridLayout_45.addWidget(self.btn_clear_all_rois, 2, 3, 1, 1)
    if hasattr(self, 'checkBox_circ_roi_data_01'):
        self.gridLayout_45.addWidget(self.checkBox_circ_roi_data_01, 2, 4, 1, 1)

    self.btn_clear_all_roi_data = QPushButton("Clear All Data", self.tab_35)
    safe_style(self, 'btn_clear_all_roi_data', "background-color: #ef4444; color: white; font-weight: bold;")
    safe_btn(self, 'btn_clear_all_roi_data', 'clicked', lambda: roi_c_clear_all_data(self))
    self.gridLayout_34.addWidget(self.btn_clear_all_roi_data, 1, 2, 1, 1)
    
    # Span data table across all 3 columns to use full width to the right
    if hasattr(self, 'table_roi_c_values'):
        self.gridLayout_34.removeWidget(self.table_roi_c_values)
        self.gridLayout_34.addWidget(self.table_roi_c_values, 0, 0, 1, 3)
    
    # Create programmatically the ROI configuration inputs (pixel size, slices)
    from PySide6.QtWidgets import QHBoxLayout, QLabel, QSpinBox
    self.roi_config_widget = QtWidgets.QWidget(self.tab_34)
    roi_config_layout = QHBoxLayout(self.roi_config_widget)
    roi_config_layout.setContentsMargins(0, 0, 0, 0)
    roi_config_layout.setSpacing(5)
    
    lbl_pixel_size = QLabel("Default Pixel Size (Px):", self.tab_34)
    self.roi_default_pixel_size = QSpinBox(self.tab_34)
    self.roi_default_pixel_size.setRange(1, 1000)
    self.roi_default_pixel_size.setValue(10)
    
    lbl_slices = QLabel("Slices:", self.tab_34)
    self.roi_slices = QSpinBox(self.tab_34)
    self.roi_slices.setRange(1, 1000)
    self.roi_slices.setValue(1)
    
    roi_config_layout.addWidget(lbl_pixel_size)
    roi_config_layout.addWidget(self.roi_default_pixel_size)
    roi_config_layout.addWidget(lbl_slices)
    roi_config_layout.addWidget(self.roi_slices)
    
    self.gridLayout_45.addWidget(self.roi_config_widget, 1, 3, 1, 1)

    # Populate Direction dropdown inside groupBox_8
    from PySide6.QtWidgets import QVBoxLayout, QComboBox, QPushButton
    if hasattr(self, 'groupBox_8') and self.groupBox_8 is not None:
        if not self.groupBox_8.layout():
            grp_layout = QVBoxLayout(self.groupBox_8)
            grp_layout.setContentsMargins(4, 4, 4, 4)
        else:
            grp_layout = self.groupBox_8.layout()

        self.roi_direction_combo = QComboBox(self.groupBox_8)
        self.roi_direction_combo.addItems(["Axial", "Sagittal", "Coronal"])
        self.roi_direction_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e24;
                color: #ffffff;
                border: 1px solid #3c4450;
                border-radius: 3px;
                padding: 2px;
                font-weight: bold;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e24;
                color: #ffffff;
                selection-background-color: #3b82f6;
            }
        """)
        grp_layout.addWidget(self.roi_direction_combo)

    safe_btn(self, 'exp_csv_roi_c_values', 'clicked', lambda: export_roi_circ_values_to_csv(self), "background-color: blue; color: white;")
    self.checkBox_circ_roi_data_2.setChecked(True)
    
    



def on_display_dw_overlay_clicked(self):
    """
    Slot called when the display_dw_overlay checkbox is clicked.
    Checks if the plan exists and shows an error if not. Otherwise, displays dwell overlay.
    """
    renderer_ax = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()
    renderer_co = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()
    renderer_sa = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()
    # Remove any previous dwell actors
    for actor in self.dwell_actors_ax:
        renderer_ax.RemoveActor(actor)
    self.dwell_actors_ax.clear()
    #
    for actor in self.dwell_actors_co:
        renderer_co.RemoveActor(actor)
    self.dwell_actors_co.clear()
    #
    for actor in self.dwell_actors_sa:
        renderer_sa.RemoveActor(actor)
    self.dwell_actors_sa.clear()
    #
    # Remove any previous channelactors
    for actor in self.channel_actors_ax:
        renderer_ax.RemoveActor(actor)
    self.channel_actors_ax.clear()
    #
    for actor in self.channel_actors_co:
        renderer_co.RemoveActor(actor)
    self.channel_actors_co.clear()
    #
    for actor in self.channel_actors_sa:
        renderer_sa.RemoveActor(actor)
    self.channel_actors_sa.clear()
    

    displayaxial(self)
    displaysagittal(self)
    displaycoronal(self)
    #
    # Check if the required fields exist in medical_image
    try:
        medical_image = self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']
    except KeyError:
        # Show an error message if plan metadata is missing
        QtWidgets.QMessageBox.critical(self, "Plan Missing", "Please select a plan first.")
        self.display_dw_overlay.setChecked(False)  # Uncheck the checkbox if plan is missing
        return

    # Check if 'Plan_Brachy_Channels' exists in 'metadata'
    if 'Plan_Brachy_Channels' not in medical_image:
        # Show an error message if Plan_Brachy_Channels is missing
        QtWidgets.QMessageBox.critical(self, "Plan Missing", "Please select a plan first.")
        self.display_dw_overlay.setChecked(False)  # Uncheck the checkbox if plan is missing
        return

    channels = medical_image['Plan_Brachy_Channels']

    # Check if 'Plan_Brachy_Channels' contains valid data (e.g., non-empty list or array)
    if not channels or not isinstance(channels, list):
        # Show an error message if the plan exists but is invalid or empty
        QtWidgets.QMessageBox.critical(self, "Invalid Plan", "The selected plan is invalid or empty.")
        self.display_dw_overlay.setChecked(False)  # Uncheck the checkbox if plan is invalid
        return


    
    