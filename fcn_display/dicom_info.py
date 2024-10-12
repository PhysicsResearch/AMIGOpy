import sys
import pydicom
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QFileDialog

def extract_dicom_hierarchy(dicom_file_path):
    ds = pydicom.dcmread(dicom_file_path, stop_before_pixels=True)
    headers_table = []
    grouped_headers = {}
    for data_element in ds:
        group_number = data_element.tag.group
        if group_number not in grouped_headers:
            grouped_headers[group_number] = []
        grouped_headers[group_number].append(data_element)

    for group, elements in grouped_headers.items():
        for element in elements:
            headers_table.append([
                f"{group:X}",
                f"{element.tag.element:X}",
                element.name,
                str(element.value)[:50]  # Truncate long values
            ])
    return headers_table

class DicomHeadersViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DICOM Headers Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Setup the table
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['Group', 'Element', 'Name', 'Value'])

        # Set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Load DICOM file
        self.load_dicom_file()

    def load_dicom_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open DICOM File", "",
                                                  "DICOM Files (*.dcm);;All Files (*)", options=options)
        if fileName:
            self.display_dicom_headers(fileName)

    def display_dicom_headers(self, dicom_file_path):
        headers_table = extract_dicom_hierarchy(dicom_file_path)
        self.tableWidget.setRowCount(len(headers_table))
        
        for i, row in enumerate(headers_table):
            for j, cell in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(cell))

        self.tableWidget.resizeColumnsToContents()

def disp_dicom_info():
    app = QApplication.instance()  # Check if an instance of QApplication already exists
    if not app:  # If it does not exist, create a new instance
        app = QApplication([])
        
    viewer = DicomHeadersViewer()
    viewer.show()
    app.exec_()  # 
    
def disp_dicom_info_from_amigo(self):
    if not self.viewer or not self.viewer.isVisible():
        self.viewer = DicomHeadersViewer()
        self.viewer.show()
    
        
    

if __name__ == "__main__":
    disp_dicom_info()