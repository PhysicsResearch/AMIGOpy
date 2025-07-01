def set_tooltip(self):
    self.DataTreeView.setToolTip(
        "<div style='font-size:12pt; text-align:left;'>"
        "Drop a <b>folder</b> to open all the content<br/>"
        "Drop a <b>single DICOM file</b> to explore the metadata"
        "</div>"
    )