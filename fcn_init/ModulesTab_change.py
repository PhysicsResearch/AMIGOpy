def set_fcn_tabModules_changed(self):
    # Connect the currentChanged signal to the onTabChanged slot
    self.tabModules.currentChanged.connect(lambda: onTabChanged(self))
    
def onTabChanged(self):
    # This function is called whenever the current tab changes.
    # 'index' is the index of the new current tab.
    tabName = self.tabModules.tabText(self.tabModules.currentIndex())
    #
    # 1. Run lazy initialization first so any VTK widgets/actors exist before value changes trigger opacity/rendering updates
    if tabName == "Segmentation":
        if not getattr(self, '_vtk_seg_initialized', False):
            from fcn_init.vtk_comp_seg import setup_vtk_seg
            setup_vtk_seg(self)
            self._vtk_seg_initialized = True
    elif tabName == "IrIS":
        if not getattr(self, '_vtk_iris_initialized', False):
            from fcn_init.vtk_IrIS_eval_axes import setup_vtk_IrISEval
            setup_vtk_IrISEval(self)
            from fcn_init.IrIS_cal_init import init_cal_markers_IrIS
            init_cal_markers_IrIS(self)
            self._vtk_iris_initialized = True
    elif tabName == "_3Dview":
        if not getattr(self, '_3d_view_initialized', False):
            from fcn_init.init_vtk_3D_display import init_vtk3d_widget
            from fcn_3Dview.structures_3D_table import init_3D_Struct_table 
            from fcn_3Dview.surfaces_3D_table import init_STL_Surface_table
            from fcn_3Dview.protons_3D_plan import init_3D_proton_table
            from fcn_3Dview.brachy_3D_table import init_3D_brachy_table
            from fcn_3Dview.render_controls import init_3D_render_controls
            
            init_3D_Struct_table(self)
            init_STL_Surface_table(self)
            init_3D_proton_table(self)
            
            self.VTK3D_widget, self.VTK3D_renderer, self.VTK3D_interactor = \
                init_vtk3d_widget(self, self.VTK_view_3D)
            if hasattr(self, 'vtk3dWidget'):
                self.vtk3dWidget.installEventFilter(self)
            self.init_3d_viewer()
            
            init_3D_brachy_table(self)
            init_3D_render_controls(self)
            
            self._3d_view_initialized = True
    elif tabName == "Breathing curves":
        if not getattr(self, '_breathing_curves_initialized', False):
            from fcn_breathing_curves.functions_phantom_operation import set_fcn_MoVeTab_changed
            set_fcn_MoVeTab_changed(self)
            
            from fcn_breathing_curves.functions_plot import init_BrCv_plot, plotViewData_BrCv_plot
            from fcn_breathing_curves.functions_edit import initXRange, init_BrCv_edit, plotViewData_BrCv_edit
            
            self.tabWidget_BrCv.currentChanged.connect(lambda: init_BrCv_plot(self))
            self.plotXAxis_BrCv.currentTextChanged.connect(lambda: plotViewData_BrCv_plot(self))

            self.tabWidget_BrCv.currentChanged.connect(lambda: init_BrCv_edit(self))
            self.editXMinSlider_BrCv.valueChanged.connect(lambda: plotViewData_BrCv_edit(self))
            self.editXMaxSlider_BrCv.valueChanged.connect(lambda: plotViewData_BrCv_edit(self))
            self.editXAxis_BrCv.currentTextChanged.connect(lambda: initXRange(self))
            
            init_BrCv_plot(self)
            init_BrCv_edit(self)
            self._breathing_curves_initialized = True

    # 2. Update opacity/transparency controls (this might trigger valueChanged and run updates)
    self.layer_selected.setEnabled(True)
    if tabName in self.layerTab:
        self.layer_selected.setCurrentIndex(self.layerTab[tabName])
    self.Layer_0_alpha_spin.setValue(self.transTab[tabName][0])
    self.Layer_1_alpha_spin.setValue(self.transTab[tabName][1])
    self.Layer_2_alpha_spin.setValue(self.transTab[tabName][2])
    self.Layer_3_alpha_spin.setValue(self.transTab[tabName][3])

    # 3. Perform other post-initialization tab operations
    if tabName == "Segmentation":
        from fcn_segmentation.functions_segmentation import update_seg_struct_list, disp_seg_image_slice
        update_seg_struct_list(self)
        disp_seg_image_slice(self)
