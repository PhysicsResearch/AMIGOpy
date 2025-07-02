import vtk
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout, QAction, QShortcut
from PyQt5 import QtWidgets  # Import the correct module for QMessageBox
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from fcn_init.vtk_comparison_axes     import create_vtk_elements_comp
from fcn_IrIS.FindDwell_IrIS import add_row_dw_table, remove_row_dw_table
from fcn_processing.Im_process_list import image_processing_undo, run_image_processing
from fcn_processing.split_dcm_series import shift_and_split_3D_matrix
from fcn_csv_explorer.general_functions_csv_exp import openCSVFile_exp,plotCSV_ViewData, CSV_apply_oper,exp_csv2_gcode
from fcn_processing.roi_circle import (toggle_rois, roi_c_add_row, roi_c_remove_row, export_roi_circ_table_to_csv, import_roi_circ_table, 
                                       c_roi_getdata, export_roi_circ_values_to_csv)
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
from fcn_dosecalculations.eqd2_conversion import add_ab, delete_ab, generate_eqd2_dose, update_doses_list, update_structure_list, eqd2_calc
from fcn_segmentation.functions_segmentation import threshSeg, on_brush_click, on_erase_click, InitSeg, calcStrucStats, exportStrucStats, exportSegStruc, DeleteSeg
from fcn_display.display_images_seg import undo_brush_seg
from fcn_ctcal.ct_cal import load_ct_cal_curve,save_changes,add_row_to_ct_table, export_ct_cal_to_csv
from fcn_densitymap.density_map import create_density_map
from fcn_brachy.cal_TG43_dose import calculate_TG43_plan_dose
from fcn_3Dview.Prepare_data_3D_vtk import play_4D_sequence_3D
from fcn_materialassignment.material_assignment_properties import add_mat_row,del_mat_row,add_element,del_element,save_mat_db,undo_changes
from fcn_brachy.cal_TG43_dose import calculate_TG43_plan_dose
from fcn_3Dview.Prepare_data_3D_vtk import play_4D_sequence_3D
from fcn_materialassignment.material_map import mat2HU,del_mat2HU,generate_mat_map,delete_mat_map


def initialize_software_buttons(self):





    # IrIS add row dw table
    self.add_dw_table.clicked.connect(lambda: add_row_dw_table(self))
    self.remove_dw_table.clicked.connect(lambda: remove_row_dw_table(self))
    
    #Metadata
    self.metadata_search.textChanged.connect(lambda text: on_metadata_search_text_changed(self,text))

    # Image processing
    self.ImageUndo_operation.clicked.connect(lambda: image_processing_undo(self))
    self.ImageUndo_operation.setStyleSheet("background-color: green; color: white;")
    #

    # Breathing curves explore
    self.loadCSVView_BrCv.clicked.connect(lambda: openCSVFile_BrCv(self))
    self.loadCSVView_BrCv.setStyleSheet("background-color: green; color: white;")
    self.setParamsCreateCv.clicked.connect(lambda: setParams(self))
    self.createCv.clicked.connect(lambda: createCurve(self))
    self.createCv.setStyleSheet("background-color: green; color: white;")
    self.calcStats_BrCv.clicked.connect(lambda: calcStats(self))
    self.calcStats_BrCv.setStyleSheet("background-color: green; color: white;")
    self.plotView_BrCv.clicked.connect(lambda: plotViewData_BrCv_plot(self))
    self.plotView_BrCv.setStyleSheet("background-color: green; color: white;")
    # self.plotExport_BrCv.clicked.connect(lambda: exportPlot(self))
    # self.plotExport_BrCv.setStyleSheet("background-color: blue; color: white")
    self.applyOper_BrCv.clicked.connect(lambda: applyOperations(self))
    self.applyOper_BrCv.setStyleSheet("background-color: green; color: white")
    self.undoOperations_BrCv.clicked.connect(lambda: undoOperations(self))
    self.undoOperations_BrCv.setStyleSheet("background-color: green; color: white")
    self.exportData_BrCv.clicked.connect(lambda: exportData(self))
    self.exportData_BrCv.setStyleSheet("background-color: blue; color: white")
    self.exportGCODE_BrCv.clicked.connect(lambda: exportGCODE(self))
    self.exportGCODE_BrCv.setStyleSheet("background-color: blue; color: white")
    self.cropRangeEdit_BrCv.clicked.connect(lambda: cropRange_BrCv_edit(self))
    self.cropRangeEdit_BrCv.setStyleSheet("background-color: blue; color:white")

    # Segmentation
    self.applyThreshSeg.clicked.connect(lambda: threshSeg(self))
    self.applyThreshSeg.setStyleSheet("background-color: blue; color:white")
    self.segBrushButton.clicked.connect(lambda: on_brush_click(self))
    self.segEraseButton.clicked.connect(lambda: on_erase_click(self))
    self.undoSeg.clicked.connect(lambda: undo_brush_seg(self))
    self.createSegStruct.clicked.connect(lambda: InitSeg(self))
    self.createSegStruct.setStyleSheet("background-color: green; color:white")
    self.calcSegStatsButton.clicked.connect(lambda: calcStrucStats(self))
    self.calcSegStatsButton.setStyleSheet("background-color: green; color:white")
    self.deleteSegStruct.clicked.connect(lambda: DeleteSeg(self))
    self.deleteSegStruct.setStyleSheet("background-color: red; color:white")
    self.exportSegStatsButton.clicked.connect(lambda: exportStrucStats(self))
    self.exportSegStatsButton.setStyleSheet("background-color: blue; color:white")
    self.exportSegStrucButton.clicked.connect(lambda: exportSegStruc(self))
    self.exportSegStrucButton.setStyleSheet("background-color: blue; color:white")
    
    # Connect the button's clicked signal to the slot function - run im processing operations
    self.run_im_process.clicked.connect(lambda: run_image_processing(self))
    self.run_im_process.setStyleSheet("background-color: blue; color: white;")
    
    # IrIS correction
    self.IrIS_Load_Offset.clicked.connect(lambda: load_offset_IrIS(self))
    self.IrIS_Load_Offset.setStyleSheet("background-color: red; color: white;")
    self.IrIS_Load_CorrectionFrame.clicked.connect(lambda: load_CorrectionFrame_IrIS(self))
    self.IrIS_Load_CorrectionFrame.setStyleSheet("background-color: red; color: white;")
    
    # CSV explore
    self.LoadCSVView.clicked.connect(lambda: openCSVFile_exp(self))
    self.LoadCSVView.setStyleSheet("background-color: green; color: white;")
    self.PlotCSVView.clicked.connect(lambda: plotCSV_ViewData(self))
    self.PlotCSVView.setStyleSheet("background-color: blue; color: white;")
    self.CSV_Oper_Apply.clicked.connect(lambda: CSV_apply_oper(self))
    self.CSV_Oper_Apply.setStyleSheet("background-color: blue; color: white;")
    self.exp_csv_2_gcode.clicked.connect(lambda: exp_csv2_gcode(self))
    self.exp_csv_2_gcode.setStyleSheet("background-color: blue; color: white;")
    
    #  create vtk comp axes -buttom
    self.but_create_comp_axes.clicked.connect(lambda: create_vtk_elements_comp(self))
    self.but_create_comp_axes.setStyleSheet("background-color: blue; color: white;")

    # 4D Display
    self.Play4D_Buttom.toggled.connect(lambda: play_4D_sequence(self))
    self.Play4D_Buttom.setStyleSheet("background-color: blue; color: white;")

    # 3D viewer
    # 4D video
    self.View3D_play4D.setCheckable(True)
    self.View3D_play4D.toggled.connect(lambda: play_4D_sequence_3D(self,1))

    # DECT
    self.add_coll_table_mat.clicked.connect(lambda: add_coll2table(self))
    self.add_coll_table_mat.setStyleSheet("background-color: blue; color: white;")
    self.remove_coll_table_mat.clicked.connect(lambda: remove_coll2table(self))
    self.remove_coll_table_mat.setStyleSheet("background-color: blue; color: white;")
    self.add_row_table_mat.clicked.connect(lambda: add_row2table(self))
    self.add_row_table_mat.setStyleSheet("background-color: blue; color: white;")
    self.remove_row_table_mat.clicked.connect(lambda: remove_row2table(self))
    self.remove_row_table_mat.setStyleSheet("background-color: blue; color: white;")
    self.reset_table_mat.clicked.connect(lambda: reset_matTable(self))
    self.reset_table_mat.setStyleSheet("background-color: blue; color: white;")
    
    # Load material composition and additional info
    self.Load_csv_mat.clicked.connect(lambda: load_csv_mat_info(self))
    self.Load_csv_mat.setStyleSheet("background-color: blue; color: white;")
    self.cal_mat_ref_info.clicked.connect(lambda: calc_material_parameters(self))
    self.cal_mat_ref_info.setStyleSheet("background-color: blue; color: white;")
    # I-value plot
    self.Ivalue_plot.clicked.connect(lambda: plot_I_value_points(self))
    self.Ivalue_plot.setStyleSheet("background-color: blue; color: white;")
    # Instead of plotting from data use the providded coefficients
    self.Ivalue_pre_calc_fit.clicked.connect(lambda: plot_I_value_precalc(self))
    self.Ivalue_pre_calc_fit.setStyleSheet("background-color: blue; color: white;")
    self.Ivalue_calc_fit.clicked.connect(lambda: cal_plot_I_value_points(self))
    self.Ivalue_calc_fit.setStyleSheet("background-color: blue; color: white;")
    # export mat table
    self.export_table_mat.clicked.connect(lambda: export_matinfotable_to_csv(self))
    self.export_table_mat.setStyleSheet("background-color: blue; color: white;")
    self.get_HU_high.clicked.connect(lambda: c_roi_getdata_HU_high_low(self))
    self.get_HU_high.setStyleSheet("background-color: green; color: white;")
    # RED
    self.RED_get_ref.clicked.connect(lambda: RED_copy_ref_columns(self))
    self.RED_get_ref.setStyleSheet("background-color: green; color: white;")
    self.RED_calc_cal.clicked.connect(lambda: RED_fit_plot_fcn(self))
    self.RED_calc_cal.setStyleSheet("background-color: blue; color: white;")
    
    # Zeff
    self.Zeff_get_ref.clicked.connect(lambda: Zeff_copy_ref_columns(self))
    self.Zeff_get_ref.setStyleSheet("background-color: green; color: white;")
    self.Zeff_calc_cal.clicked.connect(lambda: Zeff_fit_plot_fcn(self))
    self.Zeff_calc_cal.setStyleSheet("background-color: blue; color: white;")
    
    # I-value
    self.Iv_get_ref.clicked.connect(lambda: Iv_copy_ref_columns(self))
    self.Iv_get_ref.setStyleSheet("background-color: green; color: white;")
    self.Iv_calc_cal.clicked.connect(lambda: Iv_fit_plot_fcn(self))
    self.Iv_calc_cal.setStyleSheet("background-color: blue; color: white;")
    
    # SPR
    self.SPR_get_ref.clicked.connect(lambda: SPR_copy_ref_columns(self))
    self.SPR_get_ref.setStyleSheet("background-color: green; color: white;")
    self.SPR_calc_cal.clicked.connect(lambda: SPR_fit_plot_fcn(self))
    self.SPR_calc_cal.setStyleSheet("background-color: blue; color: white;")
    
    # Process Eval - DECT
    self.Create_DECT_Images.clicked.connect(lambda: creat_DECT_derived_maps(self))
    self.Create_DECT_Images.setStyleSheet("background-color: green; color: white;")
    #
    self.plot_roi_scatter.clicked.connect(lambda: c_roi_scatter_plot(self))
    self.plot_roi_scatter.setStyleSheet("background-color: green; color: white;")
    
    #
    self.export_all_DECT_tables.clicked.connect(lambda: export_all_DECT_tables(self))
    self.export_all_DECT_tables.setStyleSheet("background-color: blue; color: white;")
    #
    self.DECT_exp_fit_par.clicked.connect(lambda: save_parameters_to_csv(self))
    self.DECT_exp_fit_par.setStyleSheet("background-color: blue; color: white;")
    #
    self.DECT_load_fit_par.clicked.connect(lambda: load_parameters_from_csv(self))
    self.DECT_load_fit_par.setStyleSheet("background-color: green; color: white;")
    
    # Struct
    self.CreateMask_Structures.clicked.connect(lambda: create_contour_masks(self))  # create mask
    self.CreateMask_Structures.setStyleSheet("background-color: blue; color: white;")

    # -----------------------------------------
    # Plan
    # ------------------------------------------
    # Brachy 
    #
    # spin
    self.brachy_spinBox_01.valueChanged.connect(lambda: update_disp_brachy_plan(self))
    self.brachy_spinBox_02.valueChanged.connect(lambda: sync_spinBox_01(self))
    def sync_spinBox_01(self):
        # Update brachy_spinBox_01's value to match brachy_spinBox_02
        self.brachy_spinBox_01.setValue(self.brachy_spinBox_02.value())
    #
    self.display_dw_overlay.stateChanged.connect(lambda: on_display_dw_overlay_clicked(self))
    self.display_brachy_channel_overlay.stateChanged.connect(lambda: on_display_dw_overlay_clicked(self))
    # buttom    
    self.brachy_ch_plot.clicked.connect(lambda:  plot_brachy_dwell_channels(self))
    self.brachy_ch_plot.setStyleSheet("background-color: blue; color: white;")
    #
    self.brachy_export_dw_channels_csv.setStyleSheet("background-color: blue; color: white;")
    self.brachy_export_dw_channels_csv.clicked.connect(lambda: export_all_brachy_channels_to_csv(self))
    #
    self.Brachy_load_sources.clicked.connect(lambda: on_brachy_load_sources(self))
    self.Brachy_load_sources.setStyleSheet("background-color: blue; color: white;")
    self.Brachy_load_sources.clicked.connect(lambda: plot_brachy_ani(self))
    self.brachy_source_list.currentIndexChanged.connect(lambda: on_brachy_source_selection(self))
    self.comboBox_tg43_along_away.currentIndexChanged.connect(lambda: dose_along_away_Disp_eval(self))
    #
    # TG43 
    self.Brachy_Radial_load.setStyleSheet("background-color: blue; color: white;")
    self.Brachy_Radial_load.clicked.connect(lambda: select_Radial_file2load(self))
    self.Brachy_Radial_table.itemChanged.connect(lambda: plot_brachy_radial_fit(self))
    self.Brach_plot_ani.setStyleSheet("background-color: blue; color: white;")
    self.Brach_plot_ani.clicked.connect(lambda: plot_brachy_ani(self))
    self.Brachy_load_ani.setStyleSheet("background-color: blue; color: white;")
    self.Brachy_load_ani.clicked.connect(lambda: select_Anisotropy_file2load(self))

    # using a place holder button for testing
    self.Brachy_Calcualte_TG43.clicked.connect(lambda: calculate_TG43_plan_dose(self))
    self.Brachy_Calcualte_TG43.setStyleSheet("background-color: blue; color: white;")
    #EQD2
    self.calc_eqd2.clicked.connect(lambda: generate_eqd2_dose(self))
    self.add_to_ab_list.clicked.connect(lambda: add_ab(self))
    self.delete_from_ab_list.clicked.connect(lambda: delete_ab(self))
    self.eqd2_update_dose_list.clicked.connect(lambda: update_doses_list(self))
    self.eqd2_update_structure_list.clicked.connect(lambda: update_structure_list(self))
    self.calc_eqd2_2.clicked.connect(lambda: eqd2_calc(self))

    #CT CALIBRATION--------------------------------------------------------------------------
    self.load_ct_cal.clicked.connect(lambda: load_ct_cal_curve(self))
    self.save_changes_ct_cal.clicked.connect(lambda: save_changes(self))
    self.ct_cal_add_row.clicked.connect(lambda: add_row_to_ct_table(self))
    self.Export_ct_cal.clicked.connect(lambda: export_ct_cal_to_csv(self))
    self.ct_cal_save_copy.clicked.connect(lambda:export_ct_cal_to_csv(self,export=False))
    self.create_density_map.clicked.connect(lambda:create_density_map(self))
    
    #Material assignment
    self.Add_mat.clicked.connect(lambda: add_mat_row(self))
    self.add_element.clicked.connect(lambda:add_element(self))
    self.del_element.clicked.connect(lambda:del_element(self))
    self.del_mat.clicked.connect(lambda:del_mat_row(self))
    self.save_mat_table.clicked.connect(lambda:save_mat_db(self))
    self.mat_to_hu.clicked.connect(lambda:mat2HU(self))
    self.remove_mat_fromhu.clicked.connect(lambda:del_mat2HU(self))
    self.create_mat_map.clicked.connect(lambda:generate_mat_map(self))
    self.undo_mat_tab.clicked.connect(lambda:undo_changes(self))
    self.del_mat_map.clicked.connect(lambda:delete_mat_map(self))


 
    # Circle ROI -----------------------------------------------------------------------------------
    # display (or not) ROI
    self.checkBox_circ_roi_data_2.clicked.connect(lambda: toggle_rois(self)) 
    self.roi_circle_add_row.clicked.connect(lambda: roi_c_add_row(self))
    self.roi_circle_remove_row.clicked.connect(lambda: roi_c_remove_row(self))
    self.circ_roi_exp_csv.clicked.connect(lambda: export_roi_circ_table_to_csv(self))
    self.circ_roi_exp_csv.setStyleSheet("background-color: blue; color: white;")
    self.circ_roi_load_csv.clicked.connect(lambda: import_roi_circ_table(self))
    self.circ_roi_load_csv.setStyleSheet("background-color: red; color: white;")
    self.get_circ_roi_data.clicked.connect(lambda: c_roi_getdata(self))
    self.get_circ_roi_data.setStyleSheet("background-color: blue; color: white;")
    self.get_circ_roi_data2.clicked.connect(lambda: c_roi_getdata(self))
    self.get_circ_roi_data2.setStyleSheet("background-color: blue; color: white;")
    #
    self.exp_csv_roi_c_values.clicked.connect(lambda: export_roi_circ_values_to_csv(self))
    self.exp_csv_roi_c_values.setStyleSheet("background-color: blue; color: white;")
    
    
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
    #    #
    displayaxial(self)
    displaysagittal(self)
    displaycoronal(self)
    #
    # Check if the required fields exist in dicom_data
    try:
        dicom_data = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']
    except KeyError:
        # Show an error message if plan metadata is missing
        QtWidgets.QMessageBox.critical(self, "Plan Missing", "Please select a plan first.")
        self.display_dw_overlay.setChecked(False)  # Uncheck the checkbox if plan is missing
        return

    # Check if 'Plan_Brachy_Channels' exists in 'metadata'
    if 'Plan_Brachy_Channels' not in dicom_data:
        # Show an error message if Plan_Brachy_Channels is missing
        QtWidgets.QMessageBox.critical(self, "Plan Missing", "Please select a plan first.")
        self.display_dw_overlay.setChecked(False)  # Uncheck the checkbox if plan is missing
        return

    channels = dicom_data['Plan_Brachy_Channels']

    # Check if 'Plan_Brachy_Channels' contains valid data (e.g., non-empty list or array)
    if not channels or not isinstance(channels, list):
        # Show an error message if the plan exists but is invalid or empty
        QtWidgets.QMessageBox.critical(self, "Invalid Plan", "The selected plan is invalid or empty.")
        self.display_dw_overlay.setChecked(False)  # Uncheck the checkbox if plan is invalid
        return


    
    