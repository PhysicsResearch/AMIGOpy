import numpy as np
import time
from fcn_display.display_images  import displayaxial, displaycoronal, displaysagittal
from PyQt5.QtCore import QTimer

def play_4D_sequence(self):
    # Initialize an empty list to hold (index, sequence_id) tuples
    checked_items = []
    if self.Play4D_Buttom.isChecked():
        self.Play4D_Buttom.setStyleSheet("background-color: red; color: white;")
    else:
        self.Play4D_Buttom.setStyleSheet("background-color: blue; color: white;")
        return
    # Iterate over the table rows
    for row in range(self.CT4D_table_display.rowCount()):
        # Get the checkbox widget from the first column
        checkbox_widget = self.CT4D_table_display.cellWidget(row, 0)
        checkbox = checkbox_widget.layout().itemAt(0).widget()
    
        # Check if the checkbox is checked
        if checkbox.isChecked():
            # Get the index from the second column
            index_item = self.CT4D_table_display.item(row, 3)
            index = int(index_item.text())
    
            # Get the sequence ID from the fourth column
            sequence_item = self.CT4D_table_display.item(row, 1)
            sequence_id = int(sequence_item.text())
    
            # Add the (index, sequence_id) tuple to the list
            checked_items.append((index, sequence_id))
    
    # Sort the list based on the sequence_id
    idx = self.layer_selection_box.currentIndex()
    checked_items.sort(key=lambda x: x[1])

    # Initialize a counter for iterations and checked items
    self.checked_items_index = 0

    def update_display():
        if not self.Play4D_Buttom.isChecked():
            return
        if self.checked_items_index < len(checked_items):
                slice_data_ax = self.dicom_data[self.patientID][self.studyID][self.modality][checked_items[self.checked_items_index][0]]['3DMatrix'][self.current_axial_slice_index[idx], :, :]
                displayaxial(self, slice_data_ax)
                slice_data_co = self.dicom_data[self.patientID][self.studyID][self.modality][checked_items[self.checked_items_index][0]]['3DMatrix'][:,self.current_coronal_slice_index[idx], :]
                displaycoronal(self, slice_data_co)
                slice_data_sa = self.dicom_data[self.patientID][self.studyID][self.modality][checked_items[self.checked_items_index][0]]['3DMatrix'][:,:,self.current_sagittal_slice_index[idx]]
                displaysagittal(self, slice_data_sa)
                
                self.checked_items_index += 1
                
                if self.checked_items_index >= len(checked_items):
                    self.checked_items_index = 0
                speed = int(1000/self.Play_DCT_speed.value())   
                QTimer.singleShot(speed, update_display)  # 400 ms pause
        else:
            # Reset the counters when done
            self.checked_items_index = 0

    # Start the display update loop
    if self.Play4D_Buttom.isChecked():
        update_display()
    else:
        return