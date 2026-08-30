# -*- coding: utf-8 -*-
"""
retranslate.py - AMIGOpy GUI Text Translations
================================================

Sets all widget text labels, tab titles, button text, group box titles,
and other translatable strings via QCoreApplication.translate().

Called after all widgets are created. Safe to call multiple times
(e.g., after lazy tab creation) — it only sets text on widgets that exist.

This file is part of the fcn_create_gui package.
"""

from PySide6.QtCore import QCoreApplication


def retranslate_ui(w):
    """
    Set all translatable text on widgets.

    Uses hasattr() checks so this can be called before all tabs are created
    (lazy loading). Only widgets that exist will have their text set.

    Args:
        w: The main application window (QMainWindow instance).
    """
    if hasattr(w, 'setWindowTitle'):
        w.setWindowTitle(QCoreApplication.translate("w", u"MainWindow", None))
    if hasattr(w, 'label'):
        w.label.setText("")
    if hasattr(w, 'groupBox'):
        w.groupBox.setTitle("")
    if hasattr(w, 'lineEdit_18'):
        w.lineEdit_18.setText(QCoreApplication.translate("w", u"Layer 0", None))
    if hasattr(w, 'lineEdit_21'):
        w.lineEdit_21.setText(QCoreApplication.translate("w", u"Layer 3", None))
    if hasattr(w, 'lineEdit_20'):
        w.lineEdit_20.setText(QCoreApplication.translate("w", u"Layer 2", None))
    if hasattr(w, 'lineEdit_22'):
        w.lineEdit_22.setText(QCoreApplication.translate("w", u"PMI", None))
    if hasattr(w, 'lineEdit_23'):
        w.lineEdit_23.setText(QCoreApplication.translate("w", u"Transparency", None))
    if hasattr(w, 'lineEdit_24'):
        w.lineEdit_24.setText(QCoreApplication.translate("w", u"Active layer", None))
    if hasattr(w, 'lineEdit_19'):
        w.lineEdit_19.setText(QCoreApplication.translate("w", u"Layer 1", None))
    if hasattr(w, 'label_2'):
        w.label_2.setText(QCoreApplication.translate("w", u"--------------", None))
    if hasattr(w, 'groupBox_17'):
        w.groupBox_17.setTitle("")
    if hasattr(w, 'tabModules'):
        w.tabModules.setProperty(u"Layout", "")
    if hasattr(w, 'groupBox_13'):
        w.groupBox_13.setTitle(QCoreApplication.translate("w", u"Rotation", None))
    if hasattr(w, 'lineEdit_85'):
        w.lineEdit_85.setText(QCoreApplication.translate("w", u"Moving", None))
    if hasattr(w, 'groupBox_15'):
        w.groupBox_15.setTitle(QCoreApplication.translate("w", u"Flip", None))
    if hasattr(w, 'pushButton_5'):
        w.pushButton_5.setText(QCoreApplication.translate("w", u"Y", None))
    if hasattr(w, 'pushButton_6'):
        w.pushButton_6.setText(QCoreApplication.translate("w", u"Z", None))
    if hasattr(w, 'pushButton_4'):
        w.pushButton_4.setText(QCoreApplication.translate("w", u"X", None))
    if hasattr(w, 'groupBox_12'):
        w.groupBox_12.setTitle(QCoreApplication.translate("w", u"Translation", None))
    if hasattr(w, 'lineEdit_71'):
        w.lineEdit_71.setText(QCoreApplication.translate("w", u"Lay. 0", None))
    if hasattr(w, 'lineEdit_72'):
        w.lineEdit_72.setText(QCoreApplication.translate("w", u"Layer", None))
    if hasattr(w, 'lineEdit_73'):
        w.lineEdit_73.setText(QCoreApplication.translate("w", u"STEP", None))
    if hasattr(w, 'apply_Im_transformation'):
        w.apply_Im_transformation.setText(QCoreApplication.translate("w", u"Apply", None))
    if hasattr(w, 'lineEdit_89'):
        w.lineEdit_89.setText(QCoreApplication.translate("w", u"Fill val.", None))
    if hasattr(w, 'tabWidget_10'):
        w.tabWidget_10.setTabText(w.tabWidget_10.indexOf(w.tab_44), QCoreApplication.translate("w", u"Transform_01", None))
    if hasattr(w, 'groupBox_14'):
        w.groupBox_14.setTitle(QCoreApplication.translate("w", u"Resolution", None))
    if hasattr(w, 'pushButton_2'):
        w.pushButton_2.setText(QCoreApplication.translate("w", u"Apply", None))
    if hasattr(w, 'groupBox_16'):
        w.groupBox_16.setTitle(QCoreApplication.translate("w", u"Crop", None))
    if hasattr(w, 'tabWidget_10'):
        w.tabWidget_10.setTabText(w.tabWidget_10.indexOf(w.tab_17), QCoreApplication.translate("w", u"Transform_02", None))
    if hasattr(w, 'run_im_process'):
        w.run_im_process.setText(QCoreApplication.translate("w", u"Run", None))
    if hasattr(w, 'ImageUndo_operation'):
        w.ImageUndo_operation.setText(QCoreApplication.translate("w", u"UNDO", None))
    if hasattr(w, 'ProcessSetBox'):
        w.ProcessSetBox.setTitle(QCoreApplication.translate("w", u"Settings", None))
    if hasattr(w, 'tabWidget_10'):
        w.tabWidget_10.setTabText(w.tabWidget_10.indexOf(w.tab_45), QCoreApplication.translate("w", u"Process", None))
    if hasattr(w, 'tabView01'):
        w.tabView01.setTabText(w.tabView01.indexOf(w.tab_5), QCoreApplication.translate("w", u"View", None))
    if hasattr(w, 'tabView01'):
        w.tabView01.setTabText(w.tabView01.indexOf(w.tab_6), QCoreApplication.translate("w", u"DOSE", None))
    if hasattr(w, 'display_brachy_channel_overlay'):
        w.display_brachy_channel_overlay.setText(QCoreApplication.translate("w", u"Show channel", None))
    if hasattr(w, 'brachy_export_dw_channels_csv'):
        w.brachy_export_dw_channels_csv.setText(QCoreApplication.translate("w", u"Export", None))
    if hasattr(w, 'display_dw_overlay'):
        w.display_dw_overlay.setText(QCoreApplication.translate("w", u"Show dwell", None))
    if hasattr(w, 'lineEdit_63'):
        w.lineEdit_63.setText(QCoreApplication.translate("w", u"Point size", None))
    if hasattr(w, 'overlay_all_channels'):
        w.overlay_all_channels.setText(QCoreApplication.translate("w", u"All channels", None))
    if hasattr(w, 'tabWidget_3'):
        w.tabWidget_3.setTabText(w.tabWidget_3.indexOf(w.tab_37), QCoreApplication.translate("w", u"Brachy", None))
    if hasattr(w, 'tabWidget_3'):
        w.tabWidget_3.setTabText(w.tabWidget_3.indexOf(w.tab_38), QCoreApplication.translate("w", u"EBRT-Plan", None))
    if hasattr(w, 'display_ebrt_fields_overlay'):
        w.display_ebrt_fields_overlay.setText(QCoreApplication.translate("w", u"Show fields", None))
    if hasattr(w, 'display_ebrt_isocenter'):
        w.display_ebrt_isocenter.setText(QCoreApplication.translate("w", u"Isocenter", None))
    if hasattr(w, 'display_ebrt_cax'):
        w.display_ebrt_cax.setText(QCoreApplication.translate("w", u"Central axis", None))
    if hasattr(w, 'display_ebrt_beam_fan'):
        w.display_ebrt_beam_fan.setText(QCoreApplication.translate("w", u"Field outline", None))
    if hasattr(w, 'ebrt_overlay_all_fields'):
        w.ebrt_overlay_all_fields.setText(QCoreApplication.translate("w", u"All fields", None))
    if hasattr(w, 'ebrt_export_csv'):
        w.ebrt_export_csv.setText(QCoreApplication.translate("w", u"Export CSV", None))
    if hasattr(w, 'tabView01'):
        w.tabView01.setTabText(w.tabView01.indexOf(w.tab_14), QCoreApplication.translate("w", u"PLAN", None))
    if hasattr(w, 'lineEdit_66'):
        w.lineEdit_66.setText(QCoreApplication.translate("w", u"Ref. Series", None))
    if hasattr(w, 'CreateMask_Structures'):
        w.CreateMask_Structures.setText(QCoreApplication.translate("w", u"Create Mask", None))
    if hasattr(w, 'tabView01'):
        w.tabView01.setTabText(w.tabView01.indexOf(w.tab_39), QCoreApplication.translate("w", u"STRUCT", None))
    if hasattr(w, 'IrIS_CorFrame_checkbox'):
        w.IrIS_CorFrame_checkbox.setText(QCoreApplication.translate("w", u"Correction Frame", None))
    if hasattr(w, 'lineEdit_39'):
        w.lineEdit_39.setText(QCoreApplication.translate("w", u"Dowmsample while laoding Size  / (N)", None))
    if hasattr(w, 'IrIS_Offset_checkbox'):
        w.IrIS_Offset_checkbox.setText(QCoreApplication.translate("w", u"Offset", None))
    if hasattr(w, 'IrIS_parallel_proc_box'):
        w.IrIS_parallel_proc_box.setText(QCoreApplication.translate("w", u"Parallel processing", None))
    if hasattr(w, 'lineEdit_6'):
        w.lineEdit_6.setText(QCoreApplication.translate("w", u"Skip (N) frames before loading ", None))
    if hasattr(w, 'IrIS_Sens_checkbox'):
        w.IrIS_Sens_checkbox.setText(QCoreApplication.translate("w", u"Sensitivity map", None))
    if hasattr(w, 'lineEdit_7'):
        w.lineEdit_7.setText(QCoreApplication.translate("w", u"Load (N) frames per folder", None))
    if hasattr(w, 'checkBox_4'):
        w.checkBox_4.setText(QCoreApplication.translate("w", u"Histogram - Central slice only", None))
    if hasattr(w, 'IrIS_Load_CorrectionFrame'):
        w.IrIS_Load_CorrectionFrame.setText(QCoreApplication.translate("w", u"Load", None))
    if hasattr(w, 'IrIS_Load_SensMap'):
        w.IrIS_Load_SensMap.setText(QCoreApplication.translate("w", u"Load", None))
    if hasattr(w, 'IrIS_Load_Offset'):
        w.IrIS_Load_Offset.setText(QCoreApplication.translate("w", u"Load", None))
    if hasattr(w, 'tabWidget_4'):
        w.tabWidget_4.setTabText(w.tabWidget_4.indexOf(w.tab_10), QCoreApplication.translate("w", u"Load", None))
    if hasattr(w, 'tabWidget_4'):
        w.tabWidget_4.setTabText(w.tabWidget_4.indexOf(w.tab_11), QCoreApplication.translate("w", u"Operations", None))
    if hasattr(w, 'tabWidget_4'):
        w.tabWidget_4.setTabText(w.tabWidget_4.indexOf(w.tab_12), QCoreApplication.translate("w", u"Calibration", None))
    if hasattr(w, 'tabView01'):
        w.tabView01.setTabText(w.tabView01.indexOf(w.tab_9), QCoreApplication.translate("w", u"IrIS", None))
    if hasattr(w, 'lineEdit_64'):
        w.lineEdit_64.setText(QCoreApplication.translate("w", u"Search", None))
    if hasattr(w, 'tabView01'):
        w.tabView01.setTabText(w.tabView01.indexOf(w.tab_13), QCoreApplication.translate("w", u"MetaData", None))
    if hasattr(w, 'Play4D_Buttom'):
        w.Play4D_Buttom.setText(QCoreApplication.translate("w", u"Play 4DCT", None))
    if hasattr(w, 'lineEdit_5'):
        w.lineEdit_5.setText(QCoreApplication.translate("w", u"Speed", None))
    if hasattr(w, 'tabWidget_8'):
        w.tabWidget_8.setTabText(w.tabWidget_8.indexOf(w.tab_32), QCoreApplication.translate("w", u"Display", None))
    if hasattr(w, 'calcAvg4DCT'):
        w.calcAvg4DCT.setText(QCoreApplication.translate("w", u"Calculate average", None))
    if hasattr(w, 'tabWidget_8'):
        w.tabWidget_8.setTabText(w.tabWidget_8.indexOf(w.tab_33), QCoreApplication.translate("w", u"Tab 2", None))
    if hasattr(w, 'tabView01'):
        w.tabView01.setTabText(w.tabView01.indexOf(w.tab_31), QCoreApplication.translate("w", u"4DCT", None))
    if hasattr(w, 'circ_roi_load_csv'):
        w.circ_roi_load_csv.setText(QCoreApplication.translate("w", u"Load CSV", None))
    if hasattr(w, 'roi_circle_add_row'):
        w.roi_circle_add_row.setText(QCoreApplication.translate("w", u"+", None))
    if hasattr(w, 'roi_circle_remove_row'):
        w.roi_circle_remove_row.setText(QCoreApplication.translate("w", u"-", None))
    if hasattr(w, 'circ_roi_exp_csv'):
        w.circ_roi_exp_csv.setText(QCoreApplication.translate("w", u"Export CSV", None))
    if hasattr(w, 'get_circ_roi_data'):
        w.get_circ_roi_data.setText(QCoreApplication.translate("w", u"GET DATA", None))
    if hasattr(w, 'checkBox_circ_roi_data_01'):
        w.checkBox_circ_roi_data_01.setText(QCoreApplication.translate("w", u"All image series", None))
    if hasattr(w, 'holdOnROI'):
        w.holdOnROI.setText(QCoreApplication.translate("w", u"Hold on", None))
    if hasattr(w, 'checkBox_circ_roi_data_2'):
        w.checkBox_circ_roi_data_2.setText(QCoreApplication.translate("w", u"Display", None))
    if hasattr(w, 'groupBox_8'):
        w.groupBox_8.setTitle(QCoreApplication.translate("w", u"Direction", None))
    if hasattr(w, 'tabWidget_9'):
        w.tabWidget_9.setTabText(w.tabWidget_9.indexOf(w.tab_34), QCoreApplication.translate("w", u"Circles", None))
    if hasattr(w, 'get_circ_roi_data2'):
        w.get_circ_roi_data2.setText(QCoreApplication.translate("w", u"GET", None))
    if hasattr(w, 'exp_csv_roi_c_values'):
        w.exp_csv_roi_c_values.setText(QCoreApplication.translate("w", u"ExportCSV", None))
    if hasattr(w, 'tabWidget_9'):
        w.tabWidget_9.setTabText(w.tabWidget_9.indexOf(w.tab_35), QCoreApplication.translate("w", u"Data", None))
    if hasattr(w, 'tabView01'):
        w.tabView01.setTabText(w.tabView01.indexOf(w.tab_30), QCoreApplication.translate("w", u"ROI", None))
    if hasattr(w, 'tabModules'):
        w.tabModules.setTabText(w.tabModules.indexOf(w.im_display_tab), QCoreApplication.translate("w", u"View", None))
    if hasattr(w, 'View3DgroupBox_12'):
        w.View3DgroupBox_12.setTitle(QCoreApplication.translate("w", u"Render", None))
    if hasattr(w, 'View3D_name_02'):
        w.View3D_name_02.setText(QCoreApplication.translate("w", u"Brightness", None))
    if hasattr(w, 'View3D_name_04'):
        w.View3D_name_04.setText(QCoreApplication.translate("w", u"Render mode", None))
    if hasattr(w, 'View3D_clear_all'):
        w.View3D_clear_all.setText(QCoreApplication.translate("w", u"Clear all", None))
    if hasattr(w, 'View3D_reset_camera'):
        w.View3D_reset_camera.setText(QCoreApplication.translate("w", u"Reset Camera", None))
    if hasattr(w, 'View3D_name_05'):
        w.View3D_name_05.setText(QCoreApplication.translate("w", u"Lighting", None))
    if hasattr(w, 'View3D_name_01'):
        w.View3D_name_01.setText(QCoreApplication.translate("w", u"Quality (vs speed) ", None))
    if hasattr(w, 'View3D_name_03'):
        w.View3D_name_03.setText(QCoreApplication.translate("w", u"Specular power", None))
    if hasattr(w, 'View3D_shading_checkBox'):
        w.View3D_shading_checkBox.setText(QCoreApplication.translate("w", u"Shading", None))
    if hasattr(w, 'View3D_shoiw_axes_checkBox'):
        w.View3D_shoiw_axes_checkBox.setText(QCoreApplication.translate("w", u"Show axes", None))
    if hasattr(w, 'View3D_annotation_checkBox'):
        w.View3D_annotation_checkBox.setText(QCoreApplication.translate("w", u"Annotation", None))
    if hasattr(w, 'tabWidget_3Dview'):
        w.tabWidget_3Dview.setTabText(w.tabWidget_3Dview.indexOf(w.tab_40), QCoreApplication.translate("w", u"Structures", None))
    if hasattr(w, 'tabWidget_3Dview'):
        w.tabWidget_3Dview.setTabText(w.tabWidget_3Dview.indexOf(w.tab_42), QCoreApplication.translate("w", u"Surfaces", None))
    if hasattr(w, 'tabWidget_3Dview'):
        w.tabWidget_3Dview.setTabText(w.tabWidget_3Dview.indexOf(w.tab_41), QCoreApplication.translate("w", u"Plan_Brachy", None))
    if hasattr(w, 'tabWidget_3Dview'):
        w.tabWidget_3Dview.setTabText(w.tabWidget_3Dview.indexOf(w.tab_43), QCoreApplication.translate("w", u"Plan_Proton", None))
    if hasattr(w, 'View3DgroupBox_13'):
        w.View3DgroupBox_13.setTitle(QCoreApplication.translate("w", u"3D view", None))
    if hasattr(w, 'View3D_Apply'):
        w.View3D_Apply.setText(QCoreApplication.translate("w", u"Apply", None))
    if hasattr(w, 'View3D_name_06'):
        w.View3D_name_06.setText(QCoreApplication.translate("w", u"Isovalue ", None))
    if hasattr(w, 'View3D_name_08'):
        w.View3D_name_08.setText(QCoreApplication.translate("w", u"Axial Limit", None))
    if hasattr(w, 'View3D_name_09'):
        w.View3D_name_09.setText(QCoreApplication.translate("w", u"Cor. Limit", None))
    if hasattr(w, 'View3D_name_10'):
        w.View3D_name_10.setText(QCoreApplication.translate("w", u"Sag. Limit", None))
    if hasattr(w, 'View3D_name_07'):
        w.View3D_name_07.setText(QCoreApplication.translate("w", u"Threshold", None))
    if hasattr(w, 'View3DgroupBox_14'):
        w.View3DgroupBox_14.setTitle(QCoreApplication.translate("w", u"4D-CT", None))
    if hasattr(w, 'View3D_play4D'):
        w.View3D_play4D.setText(QCoreApplication.translate("w", u"Play", None))
    if hasattr(w, 'View3D_name_12'):
        w.View3D_name_12.setText(QCoreApplication.translate("w", u"Speed", None))
    if hasattr(w, 'View3D_name_11'):
        w.View3D_name_11.setText(QCoreApplication.translate("w", u"Colormap", None))
    if hasattr(w, 'View3D_real_time_checkBox'):
        w.View3D_real_time_checkBox.setText(QCoreApplication.translate("w", u"Real-time", None))
    if hasattr(w, 'View3D_update_all_3D'):
        w.View3D_update_all_3D.setText(QCoreApplication.translate("w", u"Sync all", None))
    if hasattr(w, 'tabModules'):
        w.tabModules.setTabText(w.tabModules.indexOf(w._3Dview), QCoreApplication.translate("w", u"_3Dview", None))
    if hasattr(w, 'groupBox_2'):
        w.groupBox_2.setTitle("")
    if hasattr(w, 'but_create_comp_axes'):
        w.but_create_comp_axes.setText(QCoreApplication.translate("w", u"Create", None))
    if hasattr(w, 'Comp_linkSlices'):
        w.Comp_linkSlices.setText(QCoreApplication.translate("w", u"Link slices", None))
    if hasattr(w, 'link_win_lev'):
        w.link_win_lev.setText(QCoreApplication.translate("w", u"Link Window/Level", None))
    if hasattr(w, 'comp_link_zoom'):
        w.comp_link_zoom.setText(QCoreApplication.translate("w", u"Link zoom", None))
    if hasattr(w, 'tabModules'):
        w.tabModules.setTabText(w.tabModules.indexOf(w.im_compare_tab), QCoreApplication.translate("w", u"Compare", None))
    if hasattr(w, 'export_table_mat'):
        w.export_table_mat.setText(QCoreApplication.translate("w", u"EXPORT", None))
    if hasattr(w, 'Load_csv_mat'):
        w.Load_csv_mat.setText(QCoreApplication.translate("w", u"LOAD", None))
    if hasattr(w, 'Zeff_m'):
        w.Zeff_m.setText(QCoreApplication.translate("w", u"3.1", None))
    if hasattr(w, 'checkBox_calSPR'):
        w.checkBox_calSPR.setText(QCoreApplication.translate("w", u"SPR", None))
    if hasattr(w, 'remove_row_table_mat'):
        w.remove_row_table_mat.setText(QCoreApplication.translate("w", u"-", None))
    if hasattr(w, 'lineEdit'):
        w.lineEdit.setText(QCoreApplication.translate("w", u"Column Name", None))
    if hasattr(w, 'lineEdit_41'):
        w.lineEdit_41.setText(QCoreApplication.translate("w", u"HU High", None))
    if hasattr(w, 'checkBox_cal_I'):
        w.checkBox_cal_I.setText(QCoreApplication.translate("w", u"I-value", None))
    if hasattr(w, 'label_3'):
        w.label_3.setText(QCoreApplication.translate("w", u"Zeff m", None))
    if hasattr(w, 'reset_table_mat'):
        w.reset_table_mat.setText(QCoreApplication.translate("w", u"Reset", None))
    if hasattr(w, 'add_row_table_mat'):
        w.add_row_table_mat.setText(QCoreApplication.translate("w", u"+", None))
    if hasattr(w, 'lineEdit_8'):
        w.lineEdit_8.setText(QCoreApplication.translate("w", u"HU Low", None))
    if hasattr(w, 'get_HU_high'):
        w.get_HU_high.setText(QCoreApplication.translate("w", u"GET HU HIGH & LOW", None))
    if hasattr(w, 'checkBox_calRED'):
        w.checkBox_calRED.setText(QCoreApplication.translate("w", u"RED", None))
    if hasattr(w, 'cal_mat_ref_info'):
        w.cal_mat_ref_info.setText(QCoreApplication.translate("w", u"CALCULATE ALL", None))
    if hasattr(w, 'add_coll_table_mat'):
        w.add_coll_table_mat.setText(QCoreApplication.translate("w", u"...Add...", None))
    if hasattr(w, 'remove_coll_table_mat'):
        w.remove_coll_table_mat.setText(QCoreApplication.translate("w", u"Remove", None))
    if hasattr(w, 'checkBox_calZeff'):
        w.checkBox_calZeff.setText(QCoreApplication.translate("w", u"Zeff", None))
    if hasattr(w, 'lineEdit_47'):
        w.lineEdit_47.setText(QCoreApplication.translate("w", u"I-value water (eV) - Ref.", None))
    if hasattr(w, 'DECTmenu'):
        w.DECTmenu.setTabText(w.DECTmenu.indexOf(w.tab), QCoreApplication.translate("w", u"Mat_Info", None))
    if hasattr(w, 'Ivalue_pre_calc_fit'):
        w.Ivalue_pre_calc_fit.setText(QCoreApplication.translate("w", u"Pre-Calculated Fit", None))
    if hasattr(w, 'Ivalue_calc_fit'):
        w.Ivalue_calc_fit.setText(QCoreApplication.translate("w", u"Calculate Fit", None))
    if hasattr(w, 'lineEdit_3'):
        w.lineEdit_3.setText(QCoreApplication.translate("w", u"Z - limit for each line (separated with an space)", None))
    if hasattr(w, 'I_value_z_up_lim'):
        w.I_value_z_up_lim.setText(QCoreApplication.translate("w", u"Z upper limits", None))
    if hasattr(w, 'Ivalue_plot'):
        w.Ivalue_plot.setText(QCoreApplication.translate("w", u"Plot", None))
    if hasattr(w, 'lineEdit_2'):
        w.lineEdit_2.setText(QCoreApplication.translate("w", u"Number of Line fits", None))
    if hasattr(w, 'I_value_b_coeff'):
        w.I_value_b_coeff.setText(QCoreApplication.translate("w", u"Coefficients (b)", None))
    if hasattr(w, 'I_value_z_lw_lim'):
        w.I_value_z_lw_lim.setText(QCoreApplication.translate("w", u"Z lower limits", None))
    if hasattr(w, 'I_value_a_coeff'):
        w.I_value_a_coeff.setText(QCoreApplication.translate("w", u"Coefficients (a)", None))
    if hasattr(w, 'I_Fit_limits'):
        w.I_Fit_limits.setText(QCoreApplication.translate("w", u"8.5", None))
    if hasattr(w, 'DECTmenu'):
        w.DECTmenu.setTabText(w.DECTmenu.indexOf(w.IValue), QCoreApplication.translate("w", u"Zeff vs I Value", None))
    if hasattr(w, 'RED_fit_01'):
        w.RED_fit_01.setText(QCoreApplication.translate("w", u"a", None))
    if hasattr(w, 'RED_RMSE'):
        w.RED_RMSE.setText(QCoreApplication.translate("w", u"RMSE", None))
    if hasattr(w, 'RED_calc_cal'):
        w.RED_calc_cal.setText(QCoreApplication.translate("w", u"Fit - Calculate", None))
    if hasattr(w, 'RED_get_ref'):
        w.RED_get_ref.setText(QCoreApplication.translate("w", u"Get Ref", None))
    if hasattr(w, 'RED_r_square'):
        w.RED_r_square.setText(QCoreApplication.translate("w", u"R-square", None))
    if hasattr(w, 'RED_fit_03'):
        w.RED_fit_03.setText(QCoreApplication.translate("w", u"b", None))
    if hasattr(w, 'RED_fit_02'):
        w.RED_fit_02.setText(QCoreApplication.translate("w", u"alpha", None))
    if hasattr(w, 'DECTmenu'):
        w.DECTmenu.setTabText(w.DECTmenu.indexOf(w.tab_2), QCoreApplication.translate("w", u"RED", None))
    if hasattr(w, 'Zeff_r_square'):
        w.Zeff_r_square.setText(QCoreApplication.translate("w", u"R-square", None))
    if hasattr(w, 'Zeff_RMSE'):
        w.Zeff_RMSE.setText(QCoreApplication.translate("w", u"RMSE", None))
    if hasattr(w, 'Zeff_fit_1'):
        w.Zeff_fit_1.setText(QCoreApplication.translate("w", u"gamma", None))
    if hasattr(w, 'Zeff_get_ref'):
        w.Zeff_get_ref.setText(QCoreApplication.translate("w", u"Get Ref", None))
    if hasattr(w, 'Zeff_fit_2'):
        w.Zeff_fit_2.setText(QCoreApplication.translate("w", u"gamma_o", None))
    if hasattr(w, 'Zeff_calc_cal'):
        w.Zeff_calc_cal.setText(QCoreApplication.translate("w", u"Fit - Calculate", None))
    if hasattr(w, 'DECTmenu'):
        w.DECTmenu.setTabText(w.DECTmenu.indexOf(w.tab_3), QCoreApplication.translate("w", u"Zeff", None))
    if hasattr(w, 'Iv_calc_cal'):
        w.Iv_calc_cal.setText(QCoreApplication.translate("w", u"Calculate", None))
    if hasattr(w, 'Ivalue_RMSE'):
        w.Ivalue_RMSE.setText(QCoreApplication.translate("w", u"RMSE", None))
    if hasattr(w, 'Iv_get_ref'):
        w.Iv_get_ref.setText(QCoreApplication.translate("w", u"Get Ref", None))
    if hasattr(w, 'DECTmenu'):
        w.DECTmenu.setTabText(w.DECTmenu.indexOf(w.tab_4), QCoreApplication.translate("w", u"I Value", None))
    if hasattr(w, 'lineEdit_46'):
        w.lineEdit_46.setText(QCoreApplication.translate("w", u"RMSE", None))
    if hasattr(w, 'SPR_get_ref'):
        w.SPR_get_ref.setText(QCoreApplication.translate("w", u"Get Ref", None))
    if hasattr(w, 'SPR_calc_cal'):
        w.SPR_calc_cal.setText(QCoreApplication.translate("w", u"Calculate", None))
    if hasattr(w, 'lineEdit_42'):
        w.lineEdit_42.setText(QCoreApplication.translate("w", u"Reference energy (MeV)", None))
    if hasattr(w, 'DECTmenu'):
        w.DECTmenu.setTabText(w.DECTmenu.indexOf(w.tab_7), QCoreApplication.translate("w", u"SPR", None))
    if hasattr(w, 'groupBox_10'):
        w.groupBox_10.setTitle(QCoreApplication.translate("w", u"Process", None))
    if hasattr(w, 'Create_DECT_Images'):
        w.Create_DECT_Images.setText(QCoreApplication.translate("w", u"Create IMAGES", None))
    if hasattr(w, 'checkBox_Im_RED'):
        w.checkBox_Im_RED.setText(QCoreApplication.translate("w", u"RED", None))
    if hasattr(w, 'checkBox_Im_Zeff'):
        w.checkBox_Im_Zeff.setText(QCoreApplication.translate("w", u"Zeff", None))
    if hasattr(w, 'checkBox_Im_SPR'):
        w.checkBox_Im_SPR.setText(QCoreApplication.translate("w", u"SPR", None))
    if hasattr(w, 'checkBox_Im_I'):
        w.checkBox_Im_I.setText(QCoreApplication.translate("w", u"I-value", None))
    if hasattr(w, 'groupBox_9'):
        w.groupBox_9.setTitle(QCoreApplication.translate("w", u"Plot", None))
    if hasattr(w, 'checkBox_newScplot'):
        w.checkBox_newScplot.setText(QCoreApplication.translate("w", u"Hold plot", None))
    if hasattr(w, 'DECT_exp_scatt_data'):
        w.DECT_exp_scatt_data.setText(QCoreApplication.translate("w", u"Export", None))
    if hasattr(w, 'lineEdit_50'):
        w.lineEdit_50.setText(QCoreApplication.translate("w", u"Point size", None))
    if hasattr(w, 'plot_roi_scatter'):
        w.plot_roi_scatter.setText(QCoreApplication.translate("w", u"Plot", None))
    if hasattr(w, 'lineEdit_49'):
        w.lineEdit_49.setText(QCoreApplication.translate("w", u"High keV or kV", None))
    if hasattr(w, 'lineEdit_48'):
        w.lineEdit_48.setText(QCoreApplication.translate("w", u"Low keV or kV", None))
    if hasattr(w, 'export_all_DECT_tables'):
        w.export_all_DECT_tables.setText(QCoreApplication.translate("w", u"Export all tables", None))
    if hasattr(w, 'DECT_exp_fit_par'):
        w.DECT_exp_fit_par.setText(QCoreApplication.translate("w", u"Export fit parameters", None))
    if hasattr(w, 'DECT_load_fit_par'):
        w.DECT_load_fit_par.setText(QCoreApplication.translate("w", u"Load fit parameters", None))
    if hasattr(w, 'DECTmenu'):
        w.DECTmenu.setTabText(w.DECTmenu.indexOf(w.tab_8), QCoreApplication.translate("w", u"Eval / Process", None))
    if hasattr(w, 'tabModules'):
        w.tabModules.setTabText(w.tabModules.indexOf(w.DECT_tab), QCoreApplication.translate("w", u"DECT", None))
    if hasattr(w, 'lineEdit_51'):
        w.lineEdit_51.setText(QCoreApplication.translate("w", u"Total channel time", None))
    if hasattr(w, 'lineEdit_52'):
        w.lineEdit_52.setText(QCoreApplication.translate("w", u"Total time", None))
    if hasattr(w, 'lineEdit_54'):
        w.lineEdit_54.setText(QCoreApplication.translate("w", u"Plan Acitvity/kerma", None))
    if hasattr(w, 'lineEdit_53'):
        w.lineEdit_53.setText(QCoreApplication.translate("w", u"Number of Channels", None))
    if hasattr(w, 'pushButton'):
        w.pushButton.setText(QCoreApplication.translate("w", u"Export", None))
    if hasattr(w, 'lineEdit_55'):
        w.lineEdit_55.setText(QCoreApplication.translate("w", u"Current channel", None))
    if hasattr(w, 'checkBox_show_dw_plot'):
        w.checkBox_show_dw_plot.setText(QCoreApplication.translate("w", u"Show Active Dwells", None))
    if hasattr(w, 'checkBox_show_ch_plot'):
        w.checkBox_show_ch_plot.setText(QCoreApplication.translate("w", u"Show channels", None))
    if hasattr(w, 'checkBox_dw_ch_plot'):
        w.checkBox_dw_ch_plot.setText(QCoreApplication.translate("w", u"Plot all channels", None))
    if hasattr(w, 'brachy_ch_plot'):
        w.brachy_ch_plot.setText(QCoreApplication.translate("w", u"Plot", None))
    if hasattr(w, 'groupBox_11'):
        w.groupBox_11.setTitle(QCoreApplication.translate("w", u"PlotSettings", None))
    if hasattr(w, 'lineEdit_60'):
        w.lineEdit_60.setText(QCoreApplication.translate("w", u"Line color", None))
    if hasattr(w, 'lineEdit_57'):
        w.lineEdit_57.setText(QCoreApplication.translate("w", u"Ch. line width", None))
    if hasattr(w, 'lineEdit_56'):
        w.lineEdit_56.setText(QCoreApplication.translate("w", u"Dw. point size", None))
    if hasattr(w, 'lineEdit_58'):
        w.lineEdit_58.setText(QCoreApplication.translate("w", u"First ch. point size", None))
    if hasattr(w, 'lineEdit_59'):
        w.lineEdit_59.setText(QCoreApplication.translate("w", u"Dw. color", None))
    if hasattr(w, 'lineEdit_61'):
        w.lineEdit_61.setText(QCoreApplication.translate("w", u"1st point color", None))
    if hasattr(w, 'lineEdit_62'):
        w.lineEdit_62.setText(QCoreApplication.translate("w", u"Structure", None))
    if hasattr(w, 'Brachy_groupBox_12'):
        w.Brachy_groupBox_12.setTitle(QCoreApplication.translate("w", u"Channel settings", None))
    if hasattr(w, 'Brachy_setalldwtimes'):
        w.Brachy_setalldwtimes.setText(QCoreApplication.translate("w", u"Set all Dwell Times", None))
    if hasattr(w, 'Brachy_create_new_channel'):
        w.Brachy_create_new_channel.setText(QCoreApplication.translate("w", u"Create New Channel", None))
    if hasattr(w, 'Brachy_DuplicateChannel'):
        w.Brachy_DuplicateChannel.setText(QCoreApplication.translate("w", u"Duplicate Channel", None))
    if hasattr(w, 'Brachy_setIDD_distance'):
        w.Brachy_setIDD_distance.setText(QCoreApplication.translate("w", u"Change Inter dwell Distance", None))
    if hasattr(w, 'Brachy_DeadSpace_Offset'):
        w.Brachy_DeadSpace_Offset.setText(QCoreApplication.translate("w", u"Dead space - Offset", None))
    if hasattr(w, 'Brachy_DeleteChannel'):
        w.Brachy_DeleteChannel.setText(QCoreApplication.translate("w", u"Delete Channel", None))
    if hasattr(w, 'Brachy_Calcualte_TG43'):
        w.Brachy_Calcualte_TG43.setText(QCoreApplication.translate("w", u"Calculate TG43 Dose", None))
    if hasattr(w, 'BrachytabWidget_2'):
        w.BrachytabWidget_2.setTabText(w.BrachytabWidget_2.indexOf(w.Br_tab_42), QCoreApplication.translate("w", u"Plan", None))
    if hasattr(w, 'brachy_save_tg43_source'):
        w.brachy_save_tg43_source.setText(QCoreApplication.translate("w", u"Save", None))
    if hasattr(w, 'Brachy_load_sources'):
        w.Brachy_load_sources.setText(QCoreApplication.translate("w", u"Load Sources", None))
    if hasattr(w, 'brachy_delete_source'):
        w.brachy_delete_source.setText(QCoreApplication.translate("w", u"Delete Source", None))
    if hasattr(w, 'Brachy_Radial_load'):
        w.Brachy_Radial_load.setText(QCoreApplication.translate("w", u"Load", None))
    if hasattr(w, 'Brachy_rad_eq'):
        w.Brachy_rad_eq.setText(QCoreApplication.translate("w", u"gL = A0 + A1*r + A2*r^2 + A3*r^3 + A4*r^4 + A5*r^5 (only withing the fit range)   ", None))
    if hasattr(w, 'Brachy_rad_A0L'):
        w.Brachy_rad_A0L.setText(QCoreApplication.translate("w", u"A0", None))
    if hasattr(w, 'Brachy_rad_A1L'):
        w.Brachy_rad_A1L.setText(QCoreApplication.translate("w", u"A1", None))
    if hasattr(w, 'Brachy_rad_A2L'):
        w.Brachy_rad_A2L.setText(QCoreApplication.translate("w", u"A2", None))
    if hasattr(w, 'Brachy_rad_A3L'):
        w.Brachy_rad_A3L.setText(QCoreApplication.translate("w", u"A3", None))
    if hasattr(w, 'Brachy_rad_A4L'):
        w.Brachy_rad_A4L.setText(QCoreApplication.translate("w", u"A4", None))
    if hasattr(w, 'Brachy_rad_A5L'):
        w.Brachy_rad_A5L.setText(QCoreApplication.translate("w", u"A5", None))
    if hasattr(w, 'tabWidget_2'):
        w.tabWidget_2.setTabText(w.tabWidget_2.indexOf(w.Brachy_tab_45), QCoreApplication.translate("w", u"Radial Dose", None))
    if hasattr(w, 'Brachy_ani_dist_label'):
        w.Brachy_ani_dist_label.setText(QCoreApplication.translate("w", u"Distance (cm)", None))
    if hasattr(w, 'Brachy_load_ani'):
        w.Brachy_load_ani.setText(QCoreApplication.translate("w", u"Load", None))
    if hasattr(w, 'Brach_plot_ani'):
        w.Brach_plot_ani.setText(QCoreApplication.translate("w", u"Plot", None))
    if hasattr(w, 'Brachy_ani_plot_hold'):
        w.Brachy_ani_plot_hold.setText(QCoreApplication.translate("w", u"Hold", None))
    if hasattr(w, 'tabWidget_2'):
        w.tabWidget_2.setTabText(w.tabWidget_2.indexOf(w.Brachy_tab_46), QCoreApplication.translate("w", u"Anisotropy", None))
    if hasattr(w, 'tabWidget_2'):
        w.tabWidget_2.setTabText(w.tabWidget_2.indexOf(w.tab_36), QCoreApplication.translate("w", u"AlongAway", None))
    if hasattr(w, 'Brachy_cal_add_line'):
        w.Brachy_cal_add_line.setText(QCoreApplication.translate("w", u"Add", None))
    if hasattr(w, 'Brachy_cal_Delete_line'):
        w.Brachy_cal_Delete_line.setText(QCoreApplication.translate("w", u"Delete", None))
    if hasattr(w, 'tabWidget_2'):
        w.tabWidget_2.setTabText(w.tabWidget_2.indexOf(w.DECT_tab_47), QCoreApplication.translate("w", u"Calibration", None))
    if hasattr(w, 'Brachy_doseRate_label'):
        w.Brachy_doseRate_label.setText(QCoreApplication.translate("w", u"Dose Rate Constant ", None))
    if hasattr(w, 'Brachy_rad_leng_label'):
        w.Brachy_rad_leng_label.setText(QCoreApplication.translate("w", u"Source Length", None))
    if hasattr(w, 'Tg43_matrix_size'):
        w.Tg43_matrix_size.setTitle(QCoreApplication.translate("w", u"Dose Matrix", None))
    if hasattr(w, 'lineEdit_tg43_01'):
        w.lineEdit_tg43_01.setText(QCoreApplication.translate("w", u"Dose grid (mm)", None))
    if hasattr(w, 'lineEdit_tg43_02'):
        w.lineEdit_tg43_02.setText(QCoreApplication.translate("w", u"Matriz size (mm)", None))
    if hasattr(w, 'BrachytabWidget_2'):
        w.BrachytabWidget_2.setTabText(w.BrachytabWidget_2.indexOf(w.Br_tab_43), QCoreApplication.translate("w", u"TG43", None))
    if hasattr(w, 'Plan_tabs'):
        if hasattr(w, 'Brachy_plan_tab'):
            w.Plan_tabs.setTabText(w.Plan_tabs.indexOf(w.Brachy_plan_tab), QCoreApplication.translate("w", u"Brachy", None))
        if hasattr(w, 'ebrt_ph_tab'):
            w.Plan_tabs.setTabText(w.Plan_tabs.indexOf(w.ebrt_ph_tab), QCoreApplication.translate("w", u"EBRT-Ph", None))
    if hasattr(w, 'dose_matri_to_eqd2'):
        w.dose_matri_to_eqd2.setTitle(QCoreApplication.translate("w", u"Convert dose matrix to EQD2", None))
    if hasattr(w, 'eqd2_lab1'):
        w.eqd2_lab1.setText(QCoreApplication.translate("w", u"Select dose", None))
    if hasattr(w, 'eqd2_lab1_2'):
        w.eqd2_lab1_2.setText(QCoreApplication.translate("w", u"Select Structure", None))
    if hasattr(w, 'eqd2_lab1_3'):
        w.eqd2_lab1_3.setText(QCoreApplication.translate("w", u"\u03b1/\u03b2", None))
    if hasattr(w, 'add_to_ab_list'):
        w.add_to_ab_list.setText(QCoreApplication.translate("w", u"Add", None))
    if hasattr(w, 'delete_from_ab_list'):
        w.delete_from_ab_list.setText(QCoreApplication.translate("w", u"Delete", None))
    if hasattr(w, 'n_fractions_label'):
        w.n_fractions_label.setText(QCoreApplication.translate("w", u"Number of fractions", None))
    if hasattr(w, 'calc_eqd2'):
        w.calc_eqd2.setText(QCoreApplication.translate("w", u"Convert to EQD2", None))
    if hasattr(w, 'ab_matrix'):
        w.ab_matrix.setText(QCoreApplication.translate("w", u"Save \u03b1/\u03b2 values", None))
    if hasattr(w, 'eqd2_calc'):
        w.eqd2_calc.setTitle(QCoreApplication.translate("w", u"EQD2 Calculator", None))
    if hasattr(w, 'label_1_eqd2_calc_5'):
        w.label_1_eqd2_calc_5.setText(QCoreApplication.translate("w", u"Gy", None))
    if hasattr(w, 'label_1_eqd2_calc_2'):
        w.label_1_eqd2_calc_2.setText(QCoreApplication.translate("w", u"Total dose (Gy)", None))
    if hasattr(w, 'label_1_eqd2_calc_3'):
        w.label_1_eqd2_calc_3.setText(QCoreApplication.translate("w", u"\u03b1/\u03b2", None))
    if hasattr(w, 'label_1_eqd2_calc_4'):
        w.label_1_eqd2_calc_4.setText(QCoreApplication.translate("w", u"Number of fractions", None))
    if hasattr(w, 'calc_eqd2_2'):
        w.calc_eqd2_2.setText(QCoreApplication.translate("w", u"Calculate EQD2", None))
    if hasattr(w, 'Plan_tabs'):
        w.Plan_tabs.setTabText(w.Plan_tabs.indexOf(w.eqd2), QCoreApplication.translate("w", u"EQD2", None))
    if hasattr(w, 'dose_unit_Gy'):
        w.dose_unit_Gy.setText(QCoreApplication.translate("w", u"Gy", None))
    if hasattr(w, 'DoseUnit'):
        w.DoseUnit.setText(QCoreApplication.translate("w", u"Dose Unit", None))
    if hasattr(w, 'VolumeUnit'):
        w.VolumeUnit.setText(QCoreApplication.translate("w", u"Volume Unit", None))
    if hasattr(w, 'button_calculate_dvhs'):
        w.button_calculate_dvhs.setText(QCoreApplication.translate("w", u"Calculate DVHs", None))
    if hasattr(w, 'select_dose'):
        w.select_dose.setText(QCoreApplication.translate("w", u"Select Dose", None))
    if hasattr(w, 'volume_unit_percentage'):
        w.volume_unit_percentage.setText(QCoreApplication.translate("w", u"%", None))
    if hasattr(w, 'volume_unit_cm3'):
        w.volume_unit_cm3.setText(QCoreApplication.translate("w", u"cm\u00b3", None))
    if hasattr(w, 'Structures'):
        w.Structures.setText(QCoreApplication.translate("w", u"Structures", None))
    if hasattr(w, 'dose_unit_percentage'):
        w.dose_unit_percentage.setText(QCoreApplication.translate("w", u"%", None))
    if hasattr(w, 'reference_dose'):
        w.reference_dose.setText(QCoreApplication.translate("w", u"Reference Dose", None))
    if hasattr(w, 'button_update_select_dose'):
        w.button_update_select_dose.setText(QCoreApplication.translate("w", u"Update", None))
    if hasattr(w, 'DoseStatistics'):
        w.DoseStatistics.setText(QCoreApplication.translate("w", u"Dose Statistics ", None))
    if hasattr(w, 'button_select_all_rows_DST'):
        w.button_select_all_rows_DST.setText(QCoreApplication.translate("w", u"Select all", None))
    if hasattr(w, 'DVHs'):
        w.DVHs.setText(QCoreApplication.translate("w", u"Dose Volume Histogram", None))
    if hasattr(w, 'button_update_plot'):
        w.button_update_plot.setText(QCoreApplication.translate("w", u"Plot", None))
    if hasattr(w, 'button_delete_column'):
        w.button_delete_column.setText(QCoreApplication.translate("w", u"Delete column", None))
    if hasattr(w, 'button_export_dose_stats_to_excel'):
        w.button_export_dose_stats_to_excel.setText(QCoreApplication.translate("w", u"Export to CSV", None))
    if hasattr(w, 'Dxx'):
        w.Dxx.setText(QCoreApplication.translate("w", u"Dx", None))
    if hasattr(w, 'vxx_t_label'):
        w.vxx_t_label.setText(QCoreApplication.translate("w", u"to", None))
    if hasattr(w, 'button_calculate_vxx_dxx'):
        w.button_calculate_vxx_dxx.setText(QCoreApplication.translate("w", u"Calculate / Add to table", None))
    if hasattr(w, 'Vxx'):
        w.Vxx.setText(QCoreApplication.translate("w", u"Vx", None))
    if hasattr(w, 'dxx_to_label'):
        w.dxx_to_label.setText(QCoreApplication.translate("w", u"to", None))
    if hasattr(w, 'Mean'):
        w.Mean.setText(QCoreApplication.translate("w", u"Mean", None))
    if hasattr(w, 'NumberOfInteractions'):
        w.NumberOfInteractions.setText(QCoreApplication.translate("w", u"Number of Interactions", None))
    if hasattr(w, 'Y'):
        w.Y.setText(QCoreApplication.translate("w", u"Y", None))
    if hasattr(w, 'StandardDeviation'):
        w.StandardDeviation.setText(QCoreApplication.translate("w", u"St. Dev.", None))
    if hasattr(w, 'X'):
        w.X.setText(QCoreApplication.translate("w", u"X", None))
    if hasattr(w, 'T'):
        w.T.setText(QCoreApplication.translate("w", u"T", None))
    if hasattr(w, 'button_apply_uncertainty'):
        w.button_apply_uncertainty.setText(QCoreApplication.translate("w", u"Apply", None))
    if hasattr(w, 'Z'):
        w.Z.setText(QCoreApplication.translate("w", u"Z", None))
    if hasattr(w, 'button_show_uncertainty_bands'):
        w.button_show_uncertainty_bands.setText(QCoreApplication.translate("w", u"Show Bands", None))
    if hasattr(w, 'tab_errors'):
        w.tab_errors.setTabText(w.tab_errors.indexOf(w.uncertainty), QCoreApplication.translate("w", u"Uncertainty", None))
    if hasattr(w, 'tab_errors'):
        w.tab_errors.setTabText(w.tab_errors.indexOf(w.error_simulation), QCoreApplication.translate("w", u"Error Simulation", None))
    if hasattr(w, 'Deviation_Metrics'):
        w.Deviation_Metrics.setText(QCoreApplication.translate("w", u"Deviation Metrics", None))
    if hasattr(w, 'Plan_tabs'):
        w.Plan_tabs.setTabText(w.Plan_tabs.indexOf(w.Plan_Evaluation), QCoreApplication.translate("w", u"Plan Evaluation ", None))
    if hasattr(w, 'groupBox_mat_to_struct'):
        w.groupBox_mat_to_struct.setTitle(QCoreApplication.translate("w", u"Materials to structures", None))
    if hasattr(w, 'remove_mat_from_struct'):
        w.remove_mat_from_struct.setText(QCoreApplication.translate("w", u"Remove material", None))
    if hasattr(w, 'assign_mat'):
        w.assign_mat.setTitle(QCoreApplication.translate("w", u"Assign", None))
    if hasattr(w, 'mat_to_hu'):
        w.mat_to_hu.setText(QCoreApplication.translate("w", u"Assign to HU range", None))
    if hasattr(w, 'label_mat_2'):
        w.label_mat_2.setText(QCoreApplication.translate("w", u"To", None))
    if hasattr(w, 'label_mat'):
        w.label_mat.setText(QCoreApplication.translate("w", u"From", None))
    if hasattr(w, 'mat_to_struct'):
        w.mat_to_struct.setText(QCoreApplication.translate("w", u"Assign to structure", None))
    if hasattr(w, 'update_mat_struct_list'):
        w.update_mat_struct_list.setText(QCoreApplication.translate("w", u"Update list", None))
    if hasattr(w, 'groupBox_mat_properties'):
        w.groupBox_mat_properties.setTitle(QCoreApplication.translate("w", u"Properties", None))
    if hasattr(w, 'element'):
        w.element.setText(QCoreApplication.translate("w", u"Column Name", None))
    if hasattr(w, 'Add_mat'):
        w.Add_mat.setText(QCoreApplication.translate("w", u"Add Material", None))
    if hasattr(w, 'add_element'):
        w.add_element.setText(QCoreApplication.translate("w", u"Add Element", None))
    if hasattr(w, 'del_element'):
        w.del_element.setText(QCoreApplication.translate("w", u"Delete Element", None))
    if hasattr(w, 'del_mat'):
        w.del_mat.setText(QCoreApplication.translate("w", u"Delete Material", None))
    if hasattr(w, 'save_mat_table'):
        w.save_mat_table.setText(QCoreApplication.translate("w", u"Save", None))
    if hasattr(w, 'undo_mat_tab'):
        w.undo_mat_tab.setText(QCoreApplication.translate("w", u"Reset", None))
    if hasattr(w, 'mat_to_HU_box'):
        w.mat_to_HU_box.setTitle(QCoreApplication.translate("w", u"Materials to HU ranges", None))
    if hasattr(w, 'remove_mat_fromhu'):
        w.remove_mat_fromhu.setText(QCoreApplication.translate("w", u"Remove material", None))
    if hasattr(w, 'del_mat_map'):
        w.del_mat_map.setText(QCoreApplication.translate("w", u"Delete Material Map", None))
    if hasattr(w, 'create_mat_map'):
        w.create_mat_map.setText(QCoreApplication.translate("w", u"Create Material Map", None))
    if hasattr(w, 'Plan_tabs'):
        w.Plan_tabs.setTabText(w.Plan_tabs.indexOf(w.tab_mat_assignment), QCoreApplication.translate("w", u"Material Assignment", None))
    if hasattr(w, 'save_changes_ct_cal'):
        w.save_changes_ct_cal.setText(QCoreApplication.translate("w", u"Update", None))
    if hasattr(w, 'Export_ct_cal'):
        w.Export_ct_cal.setText(QCoreApplication.translate("w", u"Export", None))
    if hasattr(w, 'load_ct_cal'):
        w.load_ct_cal.setText(QCoreApplication.translate("w", u"Load", None))
    if hasattr(w, 'ct_cal_save_copy'):
        w.ct_cal_save_copy.setText(QCoreApplication.translate("w", u"Save", None))
    if hasattr(w, 'ct_cal_add_row'):
        w.ct_cal_add_row.setText(QCoreApplication.translate("w", u"Add row", None))
    if hasattr(w, 'create_density_map'):
        w.create_density_map.setText(QCoreApplication.translate("w", u"Create density map", None))
    if hasattr(w, 'create_density_map__from_mat_map'):
        w.create_density_map__from_mat_map.setText(QCoreApplication.translate("w", u"Create density map from material map", None))
    if hasattr(w, 'delete_density_map'):
        w.delete_density_map.setText(QCoreApplication.translate("w", u"Delete density map", None))
    if hasattr(w, 'override_no_tissue'):
        w.override_no_tissue.setText(QCoreApplication.translate("w", u"Override non tissue materials densities", None))
    if hasattr(w, 'Plan_tabs'):
        w.Plan_tabs.setTabText(w.Plan_tabs.indexOf(w.density_map_tab), QCoreApplication.translate("w", u"Density Map", None))
    if hasattr(w, 'tabModules'):
        w.tabModules.setTabText(w.tabModules.indexOf(w.Plan_tab), QCoreApplication.translate("w", u"Plan", None))
    if hasattr(w, 'tabWidget_5'):
        w.tabWidget_5.setTabText(w.tabWidget_5.indexOf(w.tab_23), QCoreApplication.translate("w", u"PlanCheck", None))
    if hasattr(w, 'tabWidget_5'):
        w.tabWidget_5.setTabText(w.tabWidget_5.indexOf(w.tab_24), QCoreApplication.translate("w", u"DoseMetrics", None))
    if hasattr(w, 'IrIS_cal_load_meas'):
        w.IrIS_cal_load_meas.setText(QCoreApplication.translate("w", u"Load Measurement", None))
    if hasattr(w, 'lineEdit_44'):
        w.lineEdit_44.setText(QCoreApplication.translate("w", u"Markers initial shift (mm)   X  Y  Z", None))
    if hasattr(w, 'IrIS_cal_load_ref'):
        w.IrIS_cal_load_ref.setText(QCoreApplication.translate("w", u"Load Ref Markers", None))
    if hasattr(w, 'lineEdit_45'):
        w.lineEdit_45.setText(QCoreApplication.translate("w", u"Markers initial rotation (deg)", None))
    if hasattr(w, 'lineEdit_43'):
        w.lineEdit_43.setText(QCoreApplication.translate("w", u"Source initial position (mm)  X  Y  Z", None))
    if hasattr(w, 'lineEdit_40'):
        w.lineEdit_40.setText(QCoreApplication.translate("w", u"Reference Marker ID", None))
    if hasattr(w, 'IrIS_Cal_plot_deg'):
        w.IrIS_Cal_plot_deg.setText(QCoreApplication.translate("w", u"XYZ (deg)", None))
    if hasattr(w, 'IrIS_Cal_plot_mm'):
        w.IrIS_Cal_plot_mm.setText(QCoreApplication.translate("w", u" XYZ (mm)", None))
    if hasattr(w, 'IrIS_cal_plot'):
        w.IrIS_cal_plot.setText(QCoreApplication.translate("w", u"PLOT", None))
    if hasattr(w, 'IrIS_cal_save'):
        w.IrIS_cal_save.setText(QCoreApplication.translate("w", u"Save", None))
    if hasattr(w, 'IrIS_cal_export'):
        w.IrIS_cal_export.setText(QCoreApplication.translate("w", u"Export CSV", None))
    if hasattr(w, 'IrIS_cal_findMK'):
        w.IrIS_cal_findMK.setText(QCoreApplication.translate("w", u"Find Markers", None))
    if hasattr(w, 'lineEdit_11'):
        w.lineEdit_11.setText(QCoreApplication.translate("w", u"Ref. Frame", None))
    if hasattr(w, 'tabWidget_7'):
        w.tabWidget_7.setTabText(w.tabWidget_7.indexOf(w.tab_28), QCoreApplication.translate("w", u"Tab 1", None))
    if hasattr(w, 'tabWidget_7'):
        w.tabWidget_7.setTabText(w.tabWidget_7.indexOf(w.tab_29), QCoreApplication.translate("w", u"Tab 2", None))
    if hasattr(w, 'tabWidget_5'):
        w.tabWidget_5.setTabText(w.tabWidget_5.indexOf(w.tab_15), QCoreApplication.translate("w", u"Calibration", None))
    if hasattr(w, 'groupBox_4'):
        w.groupBox_4.setTitle("")
    if hasattr(w, 'pushButton_13'):
        w.pushButton_13.setText(QCoreApplication.translate("w", u"LoadCSV", None))
    if hasattr(w, 'groupBox_7'):
        w.groupBox_7.setTitle(QCoreApplication.translate("w", u"Plot Type", None))
    if hasattr(w, 'lineEdit_38'):
        w.lineEdit_38.setText(QCoreApplication.translate("w", u"Grad. between (N) frames", None))
    if hasattr(w, 'IrIS_ProcessPlot'):
        w.IrIS_ProcessPlot.setText(QCoreApplication.translate("w", u"Process", None))
    if hasattr(w, 'lineEdit_25'):
        w.lineEdit_25.setText(QCoreApplication.translate("w", u"Downsize (N x N)", None))
    if hasattr(w, 'IrIS_Plot'):
        w.IrIS_Plot.setText(QCoreApplication.translate("w", u"Plot", None))
    if hasattr(w, 'IrIS_findPK'):
        w.IrIS_findPK.setText(QCoreApplication.translate("w", u"Find Dwells", None))
    if hasattr(w, 'Average'):
        w.Average.setTitle(QCoreApplication.translate("w", u"Average dwells (Single frame per dwell)", None))
    if hasattr(w, 'IrIsAVg_dw'):
        w.IrIsAVg_dw.setText(QCoreApplication.translate("w", u"Avg Dwells", None))
    if hasattr(w, 'lineEdit_10'):
        w.lineEdit_10.setText(QCoreApplication.translate("w", u"Marging to avoid motion (Frames)", None))
    if hasattr(w, 'checkBox_IrIS_time_rel'):
        w.checkBox_IrIS_time_rel.setText(QCoreApplication.translate("w", u"Time relative to the first channel", None))
    if hasattr(w, 'groupBox_6'):
        w.groupBox_6.setTitle(QCoreApplication.translate("w", u"Average frames (within dwell)", None))
    if hasattr(w, 'IrIsAVg_Framesdw'):
        w.IrIsAVg_Framesdw.setText(QCoreApplication.translate("w", u"Avg Frames", None))
    if hasattr(w, 'lineEdit_12'):
        w.lineEdit_12.setText(QCoreApplication.translate("w", u"Number of frames to average", None))
    if hasattr(w, 'IrIS_ExportCSV'):
        w.IrIS_ExportCSV.setText(QCoreApplication.translate("w", u"ExportCSV", None))
    if hasattr(w, 'tabWidget'):
        w.tabWidget.setTabText(w.tabWidget.indexOf(w.tab_20), QCoreApplication.translate("w", u"Dwell_Find", None))
    if hasattr(w, 'remove_dw_table'):
        w.remove_dw_table.setText(QCoreApplication.translate("w", u"Delete", None))
    if hasattr(w, 'add_dw_table'):
        w.add_dw_table.setText(QCoreApplication.translate("w", u"Add", None))
    if hasattr(w, 'tabWidget'):
        w.tabWidget.setTabText(w.tabWidget.indexOf(w.tab_21), QCoreApplication.translate("w", u"Dwell_List", None))
    if hasattr(w, 'lineEdit_34'):
        w.lineEdit_34.setText(QCoreApplication.translate("w", u"Skip first ", None))
    if hasattr(w, 'lineEdit_27'):
        w.lineEdit_27.setText(QCoreApplication.translate("w", u"Threshold", None))
    if hasattr(w, 'lineEdit_33'):
        w.lineEdit_33.setText(QCoreApplication.translate("w", u"Plateau size", None))
    if hasattr(w, 'lineEdit_30'):
        w.lineEdit_30.setText(QCoreApplication.translate("w", u"Relative height", None))
    if hasattr(w, 'lineEdit_29'):
        w.lineEdit_29.setText(QCoreApplication.translate("w", u"Prominence", None))
    if hasattr(w, 'lineEdit_26'):
        w.lineEdit_26.setText(QCoreApplication.translate("w", u"Height", None))
    if hasattr(w, 'lineEdit_35'):
        w.lineEdit_35.setText(QCoreApplication.translate("w", u"Skip last", None))
    if hasattr(w, 'checkBox_Pk_find_range'):
        w.checkBox_Pk_find_range.setText(QCoreApplication.translate("w", u"Define range using intensity", None))
    if hasattr(w, 'lineEdit_36'):
        w.lineEdit_36.setText(QCoreApplication.translate("w", u"Scipy signal find peaks", None))
    if hasattr(w, 'lineEdit_32'):
        w.lineEdit_32.setText(QCoreApplication.translate("w", u"Window length", None))
    if hasattr(w, 'lineEdit_31'):
        w.lineEdit_31.setText(QCoreApplication.translate("w", u"Width", None))
    if hasattr(w, 'lineEdit_28'):
        w.lineEdit_28.setText(QCoreApplication.translate("w", u"Distance", None))
    if hasattr(w, 'lineEdit_37'):
        w.lineEdit_37.setText(QCoreApplication.translate("w", u"Additional w settings", None))
    if hasattr(w, 'Pk_Plot'):
        w.Pk_Plot.setText(QCoreApplication.translate("w", u"FindPk", None))
    if hasattr(w, 'checkBox_Pk_find_adj_1st_last'):
        w.checkBox_Pk_find_adj_1st_last.setText(QCoreApplication.translate("w", u"Adjust first/last", None))
    if hasattr(w, 'tabWidget'):
        w.tabWidget.setTabText(w.tabWidget.indexOf(w.tab_22), QCoreApplication.translate("w", u"Pk Settings", None))
    if hasattr(w, 'Source_save_cal'):
        w.Source_save_cal.setText(QCoreApplication.translate("w", u"Save", None))
    if hasattr(w, 'tabWidget'):
        w.tabWidget.setTabText(w.tabWidget.indexOf(w.tab_26), QCoreApplication.translate("w", u"Source calibration", None))
    if hasattr(w, 'IrIsAVg_loadSSD_check'):
        w.IrIsAVg_loadSSD_check.setText(QCoreApplication.translate("w", u"Load from SSD", None))
    if hasattr(w, 'lineEdit_9'):
        w.lineEdit_9.setText(QCoreApplication.translate("w", u"Channel", None))
    if hasattr(w, 'Pk_find_processl_all_check'):
        w.Pk_find_processl_all_check.setText(QCoreApplication.translate("w", u"Process all", None))
    if hasattr(w, 'groupBox_3'):
        w.groupBox_3.setTitle("")
    if hasattr(w, 'groupBox_5'):
        w.groupBox_5.setTitle("")
    if hasattr(w, 'tabWidget_5'):
        w.tabWidget_5.setTabText(w.tabWidget_5.indexOf(w.tab_16), QCoreApplication.translate("w", u"Evaluation", None))
    if hasattr(w, 'tabWidget_5'):
        w.tabWidget_5.setTabText(w.tabWidget_5.indexOf(w.tab_25), QCoreApplication.translate("w", u"Advanced", None))
    if hasattr(w, 'tabModules'):
        w.tabModules.setTabText(w.tabModules.indexOf(w.IrIS_tab), QCoreApplication.translate("w", u"IrIS", None))
    if hasattr(w, 'groupBox_BrCv_importCSV'):
        w.groupBox_BrCv_importCSV.setTitle(QCoreApplication.translate("w", u"Import CSV/VXP", None))
    if hasattr(w, 'lineEdit_BrCv_5'):
        w.lineEdit_BrCv_5.setText(QCoreApplication.translate("w", u"Delimiter", None))
    if hasattr(w, 'lineEdit_BrCv_6'):
        w.lineEdit_BrCv_6.setText(QCoreApplication.translate("w", u"Lines to skip", None))
    if hasattr(w, 'lineEdit_BrCv_7'):
        w.lineEdit_BrCv_7.setText(QCoreApplication.translate("w", u"Header line", None))
    if hasattr(w, 'flipCSV_BrCv'):
        w.flipCSV_BrCv.setText(QCoreApplication.translate("w", u"Flip", None))
    if hasattr(w, 'loadCSVView_BrCv'):
        w.loadCSVView_BrCv.setText(QCoreApplication.translate("w", u"Import", None))
    if hasattr(w, 'lineEdit_BrCv_8'):
        w.lineEdit_BrCv_8.setText(QCoreApplication.translate("w", u"Time unit", None))
    if hasattr(w, 'groupBox_BrCv_createCurve'):
        w.groupBox_BrCv_createCurve.setTitle(QCoreApplication.translate("w", u"Create analytical curve", None))
    if hasattr(w, 'lineEdit_BrCv_1'):
        w.lineEdit_BrCv_1.setText(QCoreApplication.translate("w", u"No. of cycles", None))
    if hasattr(w, 'lineEdit_BrCv'):
        w.lineEdit_BrCv.setText(QCoreApplication.translate("w", u"Cycle time (s)", None))
    if hasattr(w, 'lineEdit_BrCv_3'):
        w.lineEdit_BrCv_3.setText(QCoreApplication.translate("w", u"Amplitude (mm)", None))
    if hasattr(w, 'setParamsCreateCv'):
        w.setParamsCreateCv.setText(QCoreApplication.translate("w", u"Set parameters", None))
    if hasattr(w, 'createCv'):
        w.createCv.setText(QCoreApplication.translate("w", u"Create", None))
    if hasattr(w, 'lineEdit_BrCv_4'):
        w.lineEdit_BrCv_4.setText(QCoreApplication.translate("w", u"Curve type", None))
    if hasattr(w, 'lineEdit_BrCv_2'):
        w.lineEdit_BrCv_2.setText(QCoreApplication.translate("w", u"Sampling frequency (Hz)", None))
    if hasattr(w, 'tabWidget_BrCv'):
        w.tabWidget_BrCv.setTabText(w.tabWidget_BrCv.indexOf(w.tab_import), QCoreApplication.translate("w", u"Import && create", None))
    if hasattr(w, 'breathhold_BrCv'):
        w.breathhold_BrCv.setTitle(QCoreApplication.translate("w", u"Breath hold", None))
    if hasattr(w, 'lineEdit_BrCv_30'):
        w.lineEdit_BrCv_30.setText(QCoreApplication.translate("w", u"Duration (s)", None))
    if hasattr(w, 'lineEdit_BrCv_29'):
        w.lineEdit_BrCv_29.setText(QCoreApplication.translate("w", u"Start timestamp (s)", None))
    if hasattr(w, 'applyBreathhold'):
        w.applyBreathhold.setText(QCoreApplication.translate("w", u"Apply breath hold", None))
    if hasattr(w, 'operations_BrCv'):
        w.operations_BrCv.setTitle(QCoreApplication.translate("w", u"Operations", None))
    if hasattr(w, 'lineEdit_BrCv_22'):
        w.lineEdit_BrCv_22.setText(QCoreApplication.translate("w", u"Shift amplitude (mm)", None))
    if hasattr(w, 'lineEdit_BrCv_23'):
        w.lineEdit_BrCv_23.setText(QCoreApplication.translate("w", u"Max. amplitude threshold (mm)", None))
    if hasattr(w, 'lineEdit_BrCv_20'):
        w.lineEdit_BrCv_20.setText(QCoreApplication.translate("w", u"Scale frequency", None))
    if hasattr(w, 'lineEdit_BrCv_21'):
        w.lineEdit_BrCv_21.setText(QCoreApplication.translate("w", u"Scale amplitude", None))
    if hasattr(w, 'setMinZero_BrCv'):
        w.setMinZero_BrCv.setText(QCoreApplication.translate("w", u"Set min value to zero", None))
    if hasattr(w, 'applyOper_BrCv'):
        w.applyOper_BrCv.setText(QCoreApplication.translate("w", u"Apply operations", None))
    if hasattr(w, 'export_BrCv'):
        w.export_BrCv.setTitle(QCoreApplication.translate("w", u"Export", None))
    if hasattr(w, 'exportData_BrCv'):
        w.exportData_BrCv.setText(QCoreApplication.translate("w", u"Export CSV", None))
    if hasattr(w, 'lineEdit_BrCv_28'):
        w.lineEdit_BrCv_28.setText(QCoreApplication.translate("w", u"Filename", None))
    if hasattr(w, 'interp_BrCv'):
        w.interp_BrCv.setText(QCoreApplication.translate("w", u"Interpolate", None))
    if hasattr(w, 'exportGCODE_BrCv'):
        w.exportGCODE_BrCv.setText(QCoreApplication.translate("w", u"Export GCODE", None))
    if hasattr(w, 'lineEdit_77'):
        w.lineEdit_77.setText(QCoreApplication.translate("w", u"ms", None))
    if hasattr(w, 'lineEdit_BrCv_24'):
        w.lineEdit_BrCv_24.setText(QCoreApplication.translate("w", u"Copy fragment", None))
    if hasattr(w, 'lineEdit_83'):
        w.lineEdit_83.setText(QCoreApplication.translate("w", u"Compress below speed", None))
    if hasattr(w, 'undoOperations_BrCv'):
        w.undoOperations_BrCv.setText(QCoreApplication.translate("w", u"Undo", None))
    if hasattr(w, 'smoothing_BrCv'):
        w.smoothing_BrCv.setTitle(QCoreApplication.translate("w", u"Smoothing", None))
    if hasattr(w, 'smooth_BrCv'):
        w.smooth_BrCv.setText(QCoreApplication.translate("w", u"Smoothing", None))
    if hasattr(w, 'lineEdit_79'):
        w.lineEdit_79.setText(QCoreApplication.translate("w", u"kernel size", None))
    if hasattr(w, 'lineEdit_78'):
        w.lineEdit_78.setText(QCoreApplication.translate("w", u"method", None))
    if hasattr(w, 'lineEdit_81'):
        w.lineEdit_81.setText(QCoreApplication.translate("w", u"cut-off frequency", None))
    if hasattr(w, 'detrend_BrCv'):
        w.detrend_BrCv.setText(QCoreApplication.translate("w", u"Detrend", None))
    if hasattr(w, 'lineEdit_BrCv_26'):
        w.lineEdit_BrCv_26.setText(QCoreApplication.translate("w", u"X max", None))
    if hasattr(w, 'clipCycles_BrCv'):
        w.clipCycles_BrCv.setText(QCoreApplication.translate("w", u"Clip to whole cycles", None))
    if hasattr(w, 'lineEdit_BrCv_25'):
        w.lineEdit_BrCv_25.setText(QCoreApplication.translate("w", u"X min", None))
    if hasattr(w, 'cropRangeEdit_BrCv'):
        w.cropRangeEdit_BrCv.setText(QCoreApplication.translate("w", u"Crop", None))
    if hasattr(w, 'lineEdit_BrCv_27'):
        w.lineEdit_BrCv_27.setText(QCoreApplication.translate("w", u"X-axis", None))
    if hasattr(w, 'tabWidget_BrCv'):
        w.tabWidget_BrCv.setTabText(w.tabWidget_BrCv.indexOf(w.tab_BrCv_edit), QCoreApplication.translate("w", u"Edit && export", None))
    if hasattr(w, 'calcStats_BrCv'):
        w.calcStats_BrCv.setText(QCoreApplication.translate("w", u"Calculate statistics", None))
    if hasattr(w, 'lineEdit_BrCv_9'):
        w.lineEdit_BrCv_9.setText(QCoreApplication.translate("w", u"Amplitude", None))
    if hasattr(w, 'lineEdit_BrCv_10'):
        w.lineEdit_BrCv_10.setText(QCoreApplication.translate("w", u"Cycle time ", None))
    if hasattr(w, 'lineEdit_BrCv_11'):
        w.lineEdit_BrCv_11.setText(QCoreApplication.translate("w", u"Speed", None))
    if hasattr(w, 'lineEdit_BrCv_15'):
        w.lineEdit_BrCv_15.setText(QCoreApplication.translate("w", u"Y - Axis", None))
    if hasattr(w, 'plotView_BrCv'):
        w.plotView_BrCv.setText(QCoreApplication.translate("w", u"Plot", None))
    if hasattr(w, 'lineEdit_BrCv_14'):
        w.lineEdit_BrCv_14.setText(QCoreApplication.translate("w", u"X - Axis", None))
    if hasattr(w, 'lineEdit_82'):
        w.lineEdit_82.setText(QCoreApplication.translate("w", u"Title", None))
    if hasattr(w, 'plotPeaks_BrCv'):
        w.plotPeaks_BrCv.setText(QCoreApplication.translate("w", u"Plot peaks", None))
    if hasattr(w, 'tabWidget_BrCv'):
        w.tabWidget_BrCv.setTabText(w.tabWidget_BrCv.indexOf(w.tab_BrCv_plot), QCoreApplication.translate("w", u"Analyze && visualize", None))
    if hasattr(w, 'loadDuetPage'):
        w.loadDuetPage.setText(QCoreApplication.translate("w", u"Load Duet Web Control", None))
    if hasattr(w, 'lineEdit_65'):
        w.lineEdit_65.setText(QCoreApplication.translate("w", u"IP address", None))
    if hasattr(w, 'definePhOperFolder'):
        w.definePhOperFolder.setText(QCoreApplication.translate("w", u"Define Input Folder", None))
    if hasattr(w, 'BrCv_PhOperWidget'):
        w.BrCv_PhOperWidget.setTabText(w.BrCv_PhOperWidget.indexOf(w.tab_DuetControl), QCoreApplication.translate("w", u"Duet Web Control", None))
    if hasattr(w, 'lineEdit_MoVeOffset'):
        w.lineEdit_MoVeOffset.setText(QCoreApplication.translate("w", u"Offset", None))
    if hasattr(w, 'lineEdit_MoVeSF'):
        w.lineEdit_MoVeSF.setText(QCoreApplication.translate("w", u"Speed factor", None))
    if hasattr(w, 'MoVeAutoControl'):
        w.MoVeAutoControl.setText(QCoreApplication.translate("w", u"Auto-control", None))
    if hasattr(w, 'lineEdit_80'):
        w.lineEdit_80.setText(QCoreApplication.translate("w", u"System latency (s)", None))
    if hasattr(w, 'stop_until_radiation'):
        w.stop_until_radiation.setText(QCoreApplication.translate("w", u"Stop until radiation", None))
    if hasattr(w, 'exportDataMoVe'):
        w.exportDataMoVe.setText(QCoreApplication.translate("w", u"Export motion verification data", None))
    if hasattr(w, 'MoVeAcqStart'):
        w.MoVeAcqStart.setText(QCoreApplication.translate("w", u"Acquisition Start", None))
    if hasattr(w, 'BrCv_PhOperWidget'):
        w.BrCv_PhOperWidget.setTabText(w.BrCv_PhOperWidget.indexOf(w.tab_MoVe), QCoreApplication.translate("w", u"Motion Verification", None))
    if hasattr(w, 'tabWidget_BrCv'):
        w.tabWidget_BrCv.setTabText(w.tabWidget_BrCv.indexOf(w.tab_PhOper), QCoreApplication.translate("w", u"Phantom operation", None))
    if hasattr(w, 'tabModules'):
        w.tabModules.setTabText(w.tabModules.indexOf(w.tab_BrCv), QCoreApplication.translate("w", u"Breathing curves", None))
    if hasattr(w, 'groupBox_segStruct'):
        w.groupBox_segStruct.setTitle(QCoreApplication.translate("w", u"Structures overview", None))
    if hasattr(w, 'createSegStruct'):
        w.createSegStruct.setText(QCoreApplication.translate("w", u"Create structure", None))
    if hasattr(w, 'lineEdit_createStructSeg'):
        w.lineEdit_createStructSeg.setText(QCoreApplication.translate("w", u"Structure name", None))
    if hasattr(w, 'initStructCheck'):
        w.initStructCheck.setText(QCoreApplication.translate("w", u"All series", None))
    if hasattr(w, 'deleteSegStruct'):
        w.deleteSegStruct.setText(QCoreApplication.translate("w", u"Delete structure", None))
    if hasattr(w, 'threshMinBox'):
        w.threshMinBox.setText(QCoreApplication.translate("w", u"Min. HU threshold", None))
    if hasattr(w, 'threshMaxBox'):
        w.threshMaxBox.setText(QCoreApplication.translate("w", u"Max. HU threshold", None))
    if hasattr(w, 'undoSegText'):
        w.undoSegText.setText(QCoreApplication.translate("w", u"Undo", None))
    if hasattr(w, 'undoSeg'):
        w.undoSeg.setText(QCoreApplication.translate("w", u"undo", None))
    if hasattr(w, 'segBrushButton'):
        w.segBrushButton.setText(QCoreApplication.translate("w", u"Brush", None))
    if hasattr(w, 'segEraseButton'):
        w.segEraseButton.setText(QCoreApplication.translate("w", u"Eraser", None))
    if hasattr(w, 'BrushSizeText'):
        w.BrushSizeText.setText(QCoreApplication.translate("w", u"Brush size", None))
    if hasattr(w, 'brushClipHU'):
        w.brushClipHU.setText(QCoreApplication.translate("w", u"Use HU thresholds", None))
    if hasattr(w, 'segBrushBox'):
        w.segBrushBox.setText(QCoreApplication.translate("w", u"Brush", None))
    if hasattr(w, 'segEraseBox'):
        w.segEraseBox.setText(QCoreApplication.translate("w", u"Eraser", None))
    if hasattr(w, 'toolBox_seg'):
        w.toolBox_seg.setItemText(w.toolBox_seg.indexOf(w.seg_manual_contour), QCoreApplication.translate("w", u"Manual contouring && edits", None))
    if hasattr(w, 'lineEdit_75'):
        w.lineEdit_75.setText(QCoreApplication.translate("w", u"Min slice index", None))
    if hasattr(w, 'applyThreshSeg'):
        w.applyThreshSeg.setText(QCoreApplication.translate("w", u"Apply threshold", None))
    if hasattr(w, 'lineEdit_76'):
        w.lineEdit_76.setText(QCoreApplication.translate("w", u"Max slice index", None))
    if hasattr(w, 'toolBox_seg'):
        w.toolBox_seg.setItemText(w.toolBox_seg.indexOf(w.page_thresholding), QCoreApplication.translate("w", u"Thresholding", None))
    if hasattr(w, 'lineEdit_70'):
        w.lineEdit_70.setText(QCoreApplication.translate("w", u"Connectivity", None))
    if hasattr(w, 'lineEdit_67'):
        w.lineEdit_67.setText(QCoreApplication.translate("w", u"Operation", None))
    if hasattr(w, 'lineEdit_69'):
        w.lineEdit_69.setText(QCoreApplication.translate("w", u"Rank (dimension)", None))
    if hasattr(w, 'lineEdit_68'):
        w.lineEdit_68.setText(QCoreApplication.translate("w", u"Iterations", None))
    if hasattr(w, 'UndoMorphOper'):
        w.UndoMorphOper.setText(QCoreApplication.translate("w", u"Undo", None))
    if hasattr(w, 'ApplyMorphOper'):
        w.ApplyMorphOper.setText(QCoreApplication.translate("w", u"Apply", None))
    if hasattr(w, 'toolBox_seg'):
        w.toolBox_seg.setItemText(w.toolBox_seg.indexOf(w.morph_oper), QCoreApplication.translate("w", u"Morphological operations", None))
    if hasattr(w, 'calcSegStatsButton'):
        w.calcSegStatsButton.setText(QCoreApplication.translate("w", u"Calculate statistics", None))
    if hasattr(w, 'exportSegStatsButton'):
        w.exportSegStatsButton.setText(QCoreApplication.translate("w", u"Export statistics", None))
    if hasattr(w, 'exportSegStrucButton'):
        w.exportSegStrucButton.setText(QCoreApplication.translate("w", u"Export structures", None))
    if hasattr(w, 'toolBox_seg'):
        w.toolBox_seg.setItemText(w.toolBox_seg.indexOf(w.page), QCoreApplication.translate("w", u"Export && analyze", None))
    if hasattr(w, 'tabModules'):
        w.tabModules.setTabText(w.tabModules.indexOf(w.tab_seg), QCoreApplication.translate("w", u"Segmentation", None))
    if hasattr(w, 'D3'):
        w.D3.setTabText(w.D3.indexOf(w.tab_18), QCoreApplication.translate("w", u"Database", None))
    if hasattr(w, 'D3'):
        w.D3.setTabText(w.D3.indexOf(w.tab_27), QCoreApplication.translate("w", u"MatMix", None))
    if hasattr(w, 'import_reference_btn'):
        w.import_reference_btn.setText(QCoreApplication.translate("w", u"Load Reference Tissue File", None))
    if hasattr(w, 'import_tested_filaments_btn'):
        w.import_tested_filaments_btn.setText(QCoreApplication.translate("w", u"Load Filament Property File", None))
    if hasattr(w, 'label_human_tissue'):
        w.label_human_tissue.setText(QCoreApplication.translate("w", u"Human Tissue:", None))
    if hasattr(w, 'show_filaments_button'):
        w.show_filaments_button.setText(QCoreApplication.translate("w", u"Match Filaments", None))
    if hasattr(w, 'load_cal_btn'):
        w.load_cal_btn.setText(QCoreApplication.translate("w", u"Load Calibration Matrix File", None))
    if hasattr(w, 'label_filament'):
        w.label_filament.setText(QCoreApplication.translate("w", u"Select Filament", None))
    if hasattr(w, 'groupBox_optim_method'):
        w.groupBox_optim_method.setTitle(QCoreApplication.translate("w", u"Optimization Method", None))
    if hasattr(w, 'radio_flow'):
        w.radio_flow.setText(QCoreApplication.translate("w", u"Flow", None))
    if hasattr(w, 'radio_flow_infill'):
        w.radio_flow_infill.setText(QCoreApplication.translate("w", u"Flow + Infill", None))
    if hasattr(w, 'groupBox_Extrap'):
        w.groupBox_Extrap.setTitle(QCoreApplication.translate("w", u"Extrapolation", None))
    if hasattr(w, 'radio_extrap'):
        w.radio_extrap.setText(QCoreApplication.translate("w", u"Extrapolate", None))
    if hasattr(w, 'radio_no_extrap'):
        w.radio_no_extrap.setText(QCoreApplication.translate("w", u"No Extrapolation", None))
    if hasattr(w, 'RED_calc_button'):
        w.RED_calc_button.setText(QCoreApplication.translate("w", u"Calculate Optimal Settings", None))
    if hasattr(w, 'D3'):
        w.D3.setTabText(w.D3.indexOf(w.tab_19), QCoreApplication.translate("w", u"Flow_Infill", None))
    if hasattr(w, 'tabModules'):
        w.tabModules.setTabText(w.tabModules.indexOf(w.tab_3DP), QCoreApplication.translate("w", u"3D Printing", None))
    # retranslateUi


