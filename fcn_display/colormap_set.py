import vtk


def set_color_map_gray(self):
    idx = self.layer_selection_box.currentIndex()
    self.CmapIDX[idx] = 0
    set_color_map(self)

def set_color_map_bone(self):
    idx = self.layer_selection_box.currentIndex()
    self.CmapIDX[idx] = 1
    set_color_map(self)
     
def set_color_map_hot(self):
    idx = self.layer_selection_box.currentIndex()
    self.CmapIDX[idx] = 2
    set_color_map(self)
     
def set_color_map_cold(self):
    idx = self.layer_selection_box.currentIndex()
    self.CmapIDX[idx] = 3
    set_color_map(self)
     
def set_color_map_jet(self):
    idx = self.layer_selection_box.currentIndex()
    self.CmapIDX[idx] = 4
    set_color_map(self)
     
def set_color_map_viridis(self):
    idx = self.layer_selection_box.currentIndex()
    self.CmapIDX[idx] = 5
    set_color_map(self)
    
def set_color_map_coolwarm(self):
    idx = self.layer_selection_box.currentIndex()
    self.CmapIDX[idx] = 6
    set_color_map(self)
     
def set_color_map_rainbow(self):
    idx = self.layer_selection_box.currentIndex()
    self.CmapIDX[idx] = 7
    set_color_map(self)


def create_lookup_table_with_transparency(self, windowLevel, windowWidth,CmapIDX):
    idx = self.layer_selection_box.currentIndex()
    #
    lut         = vtk.vtkLookupTable()
    windowWidth = windowWidth
    windowStart = windowLevel - (windowWidth/2)
    windowEnd   = windowLevel + (windowWidth/2)
    lut.SetRange(windowStart, windowEnd)
    lut.SetRampToLinear()
    lut.SetNumberOfTableValues(256)
    #
    for i in range(256):
        # # Map i to the scalar range
        scalar_value = (i / 255.0) * (windowWidth) + windowStart
        # normalized_value = (scalar_value - windowStart) / windowWidth
        color = create_colormap(CmapIDX[idx], [windowStart, windowEnd]).GetColor(scalar_value)
        lut.SetTableValue(i, color[0], color[1], color[2], 1)  # Opaque
    lut.Build()
    return lut

def set_color_map(self):
    # if self.DataType == "IrIS":
    #     return
    idx = self.layer_selection_box.currentIndex()
    # Get window level and width from axial view
    windowLevel = self.windowLevelAxial[idx].GetLevel()
    windowWidth = self.windowLevelAxial[idx].GetWindow()
    # For other indices, create and apply a custom LUT
    lut = create_lookup_table_with_transparency(self, windowLevel, windowWidth, self.CmapIDX)
    apply_custom_colormap(self,lut)
    # Render the views to reflect the updated colormap
    render_views(self)

def apply_custom_colormap(self, lut):
    idx = self.layer_selection_box.currentIndex()
    views = {'Axial': self.imageActorAxial[idx], 'Sagittal': self.imageActorSagittal[idx], 'Coronal': self.imageActorCoronal[idx]}
    windowLevels = {'Axial': self.dataImporterAxial[idx], 'Sagittal': self.dataImporterSagittal[idx], 'Coronal': self.dataImporterCoronal[idx]}
    # Apply the provided custom LUT to all image actors
    for viewName, imageActor in views.items():
        colorMapper = vtk.vtkImageMapToColors()
        colorMapper.SetLookupTable(lut)
        colorMapper.SetInputConnection(windowLevels[viewName].GetOutputPort())
        imageActor.GetMapper().SetInputConnection(colorMapper.GetOutputPort())

def render_views(self):
    self.vtkWidgetAxial.GetRenderWindow().Render()
    self.vtkWidgetSagittal.GetRenderWindow().Render()
    self.vtkWidgetCoronal.GetRenderWindow().Render()

def create_colormap(index, scalar_range):
    """
    Creates a vtkColorTransferFunction based on the given index.
    Index corresponds to a specific colormap.
    
    Args:
    - index: An integer [0-7] indicating the colormap choice.
    - scalar_range: A tuple (min, max) defining the scalar range for the colormap.
    
    Returns:
    - vtkColorTransferFunction object with the specified colormap.
    """
    ctf = vtk.vtkColorTransferFunction()
    ctf.SetRange(scalar_range)
    
    # # Small value to ensure sharp transition to colormap
    epsilon = (scalar_range[1] - scalar_range[0]) * 1e-5
    lower_limit_black = scalar_range[0] - epsilon

    # # Always start with black for values below the lower limit
    ctf.AddRGBPoint(lower_limit_black, 0, 0, 0)

    if index == 0:  # Grayscale
        ctf.AddRGBPoint(scalar_range[0], 0, 0, 0)
        ctf.AddRGBPoint(scalar_range[1], 1, 1, 1)

    elif index == 1:  # Bone (MATLAB mimic)
        ctf.AddRGBPoint(scalar_range[0], 0, 0, 0)
        ctf.AddRGBPoint(scalar_range[1] * 0.376, 0.34, 0.34, 0.38)
        ctf.AddRGBPoint(scalar_range[1] * 0.753, 0.65, 0.63, 0.67)
        ctf.AddRGBPoint(scalar_range[1], 1, 1, 1)

    elif index == 2:  # Hot (MATLAB mimic)
        ctf.AddRGBPoint(scalar_range[0], 0.1, 0, 0)
        ctf.AddRGBPoint(scalar_range[1] * 0.3, 0.9, 0, 0)
        ctf.AddRGBPoint(scalar_range[1] * 0.6, 0.9, 0.9, 0)
        ctf.AddRGBPoint(scalar_range[1], 0.9, 0.9, 0.9)

    elif index == 3:  # Cold
        ctf.AddRGBPoint(scalar_range[0], 0, 0, 0.55)
        ctf.AddRGBPoint(scalar_range[1], 0.55, 0.55, 1)

    elif index == 4:  # Jet (MATLAB mimic)
        ctf.AddRGBPoint(scalar_range[0], 0, 0, 0.5)
        ctf.AddRGBPoint(scalar_range[1] * 0.35, 0, 1, 1)
        ctf.AddRGBPoint(scalar_range[1] * 0.66, 1, 1, 0)
        ctf.AddRGBPoint(scalar_range[1], 0.5, 0, 0)

    elif index == 5:  # Viridis (Perceptually uniform)
        ctf.AddRGBPoint(scalar_range[0], 0.267, 0.005, 0.329)
        ctf.AddRGBPoint(scalar_range[1], 0.229, 0.322, 0.545)

    elif index == 6:  # CoolWarm (Diverging)
        ctf.AddRGBPoint(scalar_range[0], 0.230, 0.299, 0.754)
        ctf.AddRGBPoint(scalar_range[1], 0.706, 0.016, 0.150)

    elif index == 7:  # Rainbow
        ctf.AddRGBPoint(scalar_range[0], 0, 0, 1)
        ctf.AddRGBPoint(scalar_range[1] / 4, 0, 1, 1)
        ctf.AddRGBPoint(scalar_range[1] / 2, 0, 1, 0)
        ctf.AddRGBPoint(scalar_range[1] * 3 / 4, 1, 1, 0)
        ctf.AddRGBPoint(scalar_range[1], 1, 0, 0)

    return ctf