from fcn_segmentation.functions_segmentation import update_seg_struct_list, disp_seg_image_slice
def set_fcn_tabModules_changed(self):
    # Connect the currentChanged signal to the onTabChanged slot
    self.tabModules.currentChanged.connect(lambda: onTabChanged(self))
    
def onTabChanged(self):
    # This function is called whenever the current tab changes.
    # 'index' is the index of the new current tab.
    tabName = self.tabModules.tabText(self.tabModules.currentIndex())
    #
    self.layer_selection_box.setCurrentIndex(self.layerTab[tabName])
    self.Layer_0_alpha_spin.setValue(self.transTab[tabName][0])
    self.Layer_1_alpha_spin.setValue(self.transTab[tabName][1])
    self.Layer_2_alpha_spin.setValue(self.transTab[tabName][2])
    self.Layer_3_alpha_spin.setValue(self.transTab[tabName][3])
#    if tabName == "View":
    if tabName == "Segmentation":
        update_seg_struct_list(self)
        disp_seg_image_slice(self)
