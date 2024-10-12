from PyQt5.QtWidgets import QFileDialog, QApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import numpy as np
from skimage.measure import block_reduce
from fcn_display.Data_tree_general import _get_or_create_parent_item
import pandas as pd


# Slot for the 'Open' action
def populate_IrIS_tree(self):
    # Create the data model for the tree view if it doesn't exist
    if not hasattr(self, 'model') or self.model is None:
        self.model = QStandardItemModel()
        self.DataTreeView.setModel(self.model)
        self.model.setHorizontalHeaderLabels(['Data'])

    # Check for existing 'IrIS_Cor' parent item
    IrIS_parent_item = _get_or_create_parent_item(self,'IrIS_Cor')
    #
    # Clear all children of the 'IrIS' parent item
    IrIS_parent_item.removeRows(0, IrIS_parent_item.rowCount())
    # Setup headers for the tree view columns
    # Populate tree view with data
    for key in self.IrIS_corr.keys():
        patient_item = QStandardItem(f"{key}")
        IrIS_parent_item.appendRow(patient_item)


def load_offset_IrIS(self):
   self.IrIS_corr['Offset'] = {}
   Im                                    = load_and_process_cor_files(self)
   Im                                    = np.transpose(Im, (1, 0))
   self.IrIS_corr['Offset']['3DMatrix']  = Im.copy().astype(np.uint16)
   populate_IrIS_tree(self)

def load_CorrectionFrame_IrIS(self):
   Im                                       = load_and_process_cor_files(self)
   Im                                       = np.transpose(Im, (1, 0))
   self.IrIS_corr['Corr_frame']             = {}
   self.IrIS_corr['Corr_frame']['3DMatrix'] = Im.copy().astype(np.uint16)
   populate_IrIS_tree(self)
   
def load_and_process_cor_files(self):
    # Open file dialog to select multiple files
    options  = QFileDialog.Options()
    files, _ = QFileDialog.getOpenFileNames(self, "Open IrIS Files", "", "IrIS Files (*.IrIS);;All Files (*)", options=options)
    if files:
        Image = read_IrIS_correc_files(self,files)
        print_type_and_shape(self,Image)
        return Image
        # Here you can handle the processed image, for example, display it or save it.
   

def print_type_and_shape(self, data):
    # Print the type of the data
    print("Type:", type(data))
    
    # Print the shape of the data if it's a numpy array or pandas DataFrame
    if isinstance(data, np.ndarray):
        print("Shape:", data.shape)
    elif isinstance(data, pd.DataFrame):
        print("Shape:", data.shape)
    elif isinstance(data, list):
        if data and isinstance(data[0], list):
            print("Shape: ({}, {})".format(len(data), len(data[0])))
        else:
            print("Shape: ({},)".format(len(data)))
    else:
        print("Shape: Unknown")

def read_IrIS_correc_files(self, files):
    # Get file info from the first file
    with open(files[0], 'rb') as fid:
        Info = np.fromfile(fid, dtype=np.uint16, count=1000)
        Info = np.concatenate((Info, np.fromfile(fid, dtype=np.float32, count=2)))
        Info = np.concatenate((Info, np.fromfile(fid, dtype=np.uint64, count=5)))
        Buf = int(Info[0])

    IrIS_results = {
        'mode': Info[1],
        'VxVy': Info[4:8],
        'binning': Info[8],
    }

    N_div = self.IrIS_DownSample.value()

    Im_shape = (
        np.uint(IrIS_results['VxVy'][3] - IrIS_results['VxVy'][2] + 1),
        np.uint(IrIS_results['VxVy'][1] - IrIS_results['VxVy'][0] + 1),
        np.uint(len(files))
    )

    Time = np.zeros(len(files))
    Total_f = len(files)
    self.progressBar.setValue(0)
    QApplication.processEvents()

    for i, file in enumerate(files):
        with open(file, 'rb') as fid:
            fid.seek(Buf)
            frame = np.fromfile(fid, dtype=np.uint16, count=Im_shape[0]*Im_shape[1]).reshape(Im_shape[0:2])
            fid.seek(2008)
            Time[i] = np.fromfile(fid, dtype=np.uint64, count=1)[0] * 1e-9

            if N_div > 1:
                frame_downsampled = block_reduce(frame, block_size=(N_div, N_div), func=np.mean)
            else:
                frame_downsampled = frame

            if i == 0:
                downsampled_shape = (frame_downsampled.shape[0], frame_downsampled.shape[1], len(files))
                Im = np.zeros(downsampled_shape, dtype=np.float32)  # Change dtype to float32 for averaging

            Im[:, :, i] = frame_downsampled

        if i % 20 == 0 or i == Total_f - 1:
            progress_percentage = int((i + 1) / Total_f * 100)
            self.progressBar.setValue(progress_percentage)
            QApplication.processEvents()

    # Average the images if more than one file
    if len(files) > 1:
        averaged_image = np.mean(Im, axis=2)
    else:
        averaged_image = Im[:, :, 0]
        

    return averaged_image
