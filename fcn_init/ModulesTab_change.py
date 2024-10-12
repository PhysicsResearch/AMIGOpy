def set_fcn_tabModules_changed(self):
    # Connect the currentChanged signal to the onTabChanged slot
    self.tabModules.currentChanged.connect(lambda: onTabChanged(self))
    
def onTabChanged(self):
    # This function is called whenever the current tab changes.
    # 'index' is the index of the new current tab.
    tabName = self.tabModules.tabText(self.tabModules.currentIndex())
    #
    self.layer_selection_box.setCurrentIndex(self.layerTab[tabName])
    self.Layer_0_alpha_spinbox.setValue(self.transTab[tabName][0])
    self.Layer_1_alpha_spinbox.setValue(self.transTab[tabName][1])
    self.Layer_2_alpha_spinbox.setValue(self.transTab[tabName][2])
    self.Layer_3_alpha_spinbox.setValue(self.transTab[tabName][3])
#    if tabName == "View":

