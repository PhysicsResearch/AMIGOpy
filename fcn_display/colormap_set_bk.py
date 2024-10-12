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


# Adjusted function to apply colormaps directly using vtkColorTransferFunction
def apply_colormap_to_actor(imageActor, colorTransferFunction=None):
    """
    Apply a colormap to an image actor. If a color transfer function is provided,
    it uses that; otherwise, it defaults to grayscale if None is provided.
    """
    if colorTransferFunction:
        # Create a vtkImageMapToColors and set the color transfer function
        mapToColors = vtk.vtkImageMapToColors()
        mapToColors.SetLookupTable(colorTransferFunction)
        mapToColors.SetInputConnection(imageActor.GetMapper().GetInputConnection(0, 0))
        
        # Update the actor's mapper to use the color-mapped output
        imageActor.GetMapper().SetInputConnection(mapToColors.GetOutputPort())
    else:
        # If no colorTransferFunction is provided, default to grayscale,
        # which is achieved by simply not altering the actor's existing pipeline.
        pass

def set_color_map(self):
    if self.DataType == "IrIS":
        return
    idx = self.layer_selection_box.currentIndex()
    windowLevel = self.windowLevelAxial[idx].GetLevel()
    windowWidth = self.windowLevelAxial[idx].GetWindow()
    scalar_range = [windowLevel - windowWidth/2, windowLevel + windowWidth/2]

    colorTransferFunction = None
    if self.CmapIDX[idx] != 1:  # Only create a custom colormap if the index is not 1
        colorTransferFunction = create_colormap(self.CmapIDX[idx], scalar_range)

    views = {'Axial': self.imageActorAxial[idx], 'Sagittal': self.imageActorSagittal[idx], 'Coronal': self.imageActorCoronal[idx]}
    for viewName, imageActor in views.items():
        apply_colormap_to_actor(imageActor, colorTransferFunction)

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
    
    # Small value to ensure sharp transition to colormap
    epsilon = (scalar_range[1] - scalar_range[0]) * 1e-5
    lower_limit_black = scalar_range[0] - epsilon

    # Always start with black for values below the lower limit
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