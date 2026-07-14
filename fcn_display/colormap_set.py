import vtk


def set_color_map_gray(self):
    idx = self.layer_selected.currentIndex()
    self.CmapIDX[idx] = 0
    set_color_map(self)

def set_color_map_bone(self):
    idx = self.layer_selected.currentIndex()
    self.CmapIDX[idx] = 1
    set_color_map(self)
     
def set_color_map_hot(self):
    idx = self.layer_selected.currentIndex()
    self.CmapIDX[idx] = 2
    set_color_map(self)
     
def set_color_map_cold(self):
    idx = self.layer_selected.currentIndex()
    self.CmapIDX[idx] = 3
    set_color_map(self)
     
def set_color_map_jet(self):
    idx = self.layer_selected.currentIndex()
    self.CmapIDX[idx] = 4
    set_color_map(self)
     
def set_color_map_viridis(self):
    idx = self.layer_selected.currentIndex()
    self.CmapIDX[idx] = 5
    set_color_map(self)
    
def set_color_map_coolwarm(self):
    idx = self.layer_selected.currentIndex()
    self.CmapIDX[idx] = 6
    set_color_map(self)
     
def set_color_map_rainbow(self):
    idx = self.layer_selected.currentIndex()
    self.CmapIDX[idx] = 7
    set_color_map(self)

def set_color_map_magma(self):
    idx = self.layer_selected.currentIndex()
    self.CmapIDX[idx] = 8
    set_color_map(self)

def set_color_map_cividis(self):
    idx = self.layer_selected.currentIndex()
    self.CmapIDX[idx] = 9
    set_color_map(self)

def set_color_map_red(self):
    idx = self.layer_selected.currentIndex()
    self.CmapIDX[idx] = 10
    set_color_map(self)

def set_color_map_green(self):
    idx = self.layer_selected.currentIndex()
    self.CmapIDX[idx] = 11
    set_color_map(self)

def set_color_map_blue(self):
    idx = self.layer_selected.currentIndex()
    self.CmapIDX[idx] = 12
    set_color_map(self)


def create_lookup_table_with_transparency(self, windowLevel, windowWidth,CmapIDX):
    idx = self.layer_selected.currentIndex()
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

def apply_custom_colormap_comp(self):
    if not hasattr(self, 'Comp_im_idx') or not hasattr(self, 'display_comp_data'):
        return
    layer = self.layer_selected.currentIndex()
    
    if not hasattr(self, 'CompCmapIDX'):
        self.CompCmapIDX = {}
        
    for Ax_idx in range(0, self.Comp_im_idx.maximum() + 1):
        if (Ax_idx, layer) not in self.display_comp_data:
            continue
            
        cmap_idx = self.CompCmapIDX.get((Ax_idx, layer), self.CmapIDX[layer])
        self.CompCmapIDX[Ax_idx, layer] = cmap_idx
        
        wl = self.windowLevelAxComp[Ax_idx, layer]
        window = wl.GetWindow()
        level = wl.GetLevel()
        
        if cmap_idx == 0:
            self.windowLevelAxComp[Ax_idx, layer].SetInputConnection(self.dataImporterAxComp[Ax_idx, layer].GetOutputPort())
            self.imageActorAxComp[Ax_idx, layer].GetMapper().SetInputConnection(self.windowLevelAxComp[Ax_idx, layer].GetOutputPort())
        else:
            lut = vtk.vtkLookupTable()
            windowStart = level - (window / 2.0)
            windowEnd = level + (window / 2.0)
            lut.SetRange(windowStart, windowEnd)
            lut.SetRampToLinear()
            lut.SetNumberOfTableValues(256)
            for i in range(256):
                scalar_value = (i / 255.0) * (window) + windowStart
                color = create_colormap(cmap_idx, [windowStart, windowEnd]).GetColor(scalar_value)
                lut.SetTableValue(i, color[0], color[1], color[2], 1)
            lut.Build()
            
            colorMapper = vtk.vtkImageMapToColors()
            colorMapper.SetLookupTable(lut)
            colorMapper.SetInputConnection(self.dataImporterAxComp[Ax_idx, layer].GetOutputPort())
            self.imageActorAxComp[Ax_idx, layer].GetMapper().SetInputConnection(colorMapper.GetOutputPort())


def set_color_map(self):
    # if self.DataType == "IrIS":
    #     return
    idx = self.layer_selected.currentIndex()
    # Get window level and width from axial view
    windowLevel = self.windowLevelAxial[idx].GetLevel()
    windowWidth = self.windowLevelAxial[idx].GetWindow()
    # For other indices, create and apply a custom LUT
    lut = create_lookup_table_with_transparency(self, windowLevel, windowWidth, self.CmapIDX)
    apply_custom_colormap(self,lut)

    # Update color intensity scale (colorbar) actors across all views
    actors = ['scalarBarActorAxial', 'scalarBarActorSagittal', 'scalarBarActorCoronal']
    show_scale = getattr(self, 'show_intensity_scale', False)
    has_data = hasattr(self, 'display_data') and self.display_data.get(idx) is not None
    
    for act_name in actors:
        if hasattr(self, act_name):
            actor = getattr(self, act_name)
            if show_scale and has_data:
                actor.SetLookupTable(lut)
                
                # Apply custom legend font size from figures menu settings
                f_size = getattr(self, 'selected_legend_font_size', 14)
                actor.GetLabelTextProperty().SetFontSize(f_size)
                actor.GetTitleTextProperty().SetFontSize(f_size + 2)
                
                # Apply custom position and dimensions
                px = getattr(self, 'scale_pos_x', 0.91)
                py = getattr(self, 'scale_pos_y', 0.15)
                pw = getattr(self, 'scale_width', 0.06)
                ph = getattr(self, 'scale_height', 0.7)
                actor.GetPositionCoordinate().SetValue(px, py)
                actor.SetWidth(pw)
                actor.SetHeight(ph)
                
                # Apply orientation automatically based on width vs height aspect ratio
                if pw > ph:
                    actor.SetOrientationToHorizontal()
                else:
                    actor.SetOrientationToVertical()
                
                # Set title to empty string to prevent numbers/layer text labels on top of the scale
                actor.SetTitle("")
                
                actor.SetVisibility(True)
            else:
                actor.SetVisibility(False)
    
    # Update Compare colormap dictionary based on linkage checkbox
    currentTabText = self.tabModules.tabText(self.tabModules.currentIndex())
    if currentTabText == "Compare" and hasattr(self, 'Comp_linkColormaps'):
        ref_idx = self.Comp_im_idx.value()
        new_cmap = self.CmapIDX[idx]
        if not hasattr(self, 'CompCmapIDX'):
            self.CompCmapIDX = {}
        if self.Comp_linkColormaps.isChecked():
            for Ax_idx in range(0, self.Comp_im_idx.maximum() + 1):
                self.CompCmapIDX[Ax_idx, idx] = new_cmap
        else:
            self.CompCmapIDX[ref_idx, idx] = new_cmap
            
    # Apply custom colormap to comparison views
    apply_custom_colormap_comp(self)
    # Render the views to reflect the updated colormap
    render_views(self)
    # Render comparison views too
    if hasattr(self, 'renAxComp'):
        for ren in self.renAxComp:
            ren.GetRenderWindow().Render()


def on_link_colormap_changed(self):
    if not hasattr(self, 'Comp_linkColormaps'):
        return
    if self.Comp_linkColormaps.isChecked():
        layer = self.layer_selected.currentIndex()
        new_cmap = self.CmapIDX[layer]
        if not hasattr(self, 'CompCmapIDX'):
            self.CompCmapIDX = {}
        for Ax_idx in range(0, self.Comp_im_idx.maximum() + 1):
            self.CompCmapIDX[Ax_idx, layer] = new_cmap
        apply_custom_colormap_comp(self)
        if hasattr(self, 'renAxComp'):
            for ren in self.renAxComp:
                ren.GetRenderWindow().Render()

def apply_custom_colormap(self, lut):
    idx = self.layer_selected.currentIndex()
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

    elif index == 8:  # Magma
        ctf.AddRGBPoint(scalar_range[0], 0.0, 0.0, 0.04)
        ctf.AddRGBPoint(scalar_range[0] + (scalar_range[1]-scalar_range[0])*0.25, 0.32, 0.08, 0.44)
        ctf.AddRGBPoint(scalar_range[0] + (scalar_range[1]-scalar_range[0])*0.50, 0.71, 0.17, 0.45)
        ctf.AddRGBPoint(scalar_range[0] + (scalar_range[1]-scalar_range[0])*0.75, 0.98, 0.50, 0.33)
        ctf.AddRGBPoint(scalar_range[1], 0.99, 0.91, 0.77)

    elif index == 9:  # Cividis
        ctf.AddRGBPoint(scalar_range[0], 0.0, 0.17, 0.43)
        ctf.AddRGBPoint(scalar_range[0] + (scalar_range[1]-scalar_range[0])*0.33, 0.22, 0.34, 0.54)
        ctf.AddRGBPoint(scalar_range[0] + (scalar_range[1]-scalar_range[0])*0.66, 0.51, 0.52, 0.52)
        ctf.AddRGBPoint(scalar_range[1], 0.99, 0.90, 0.14)

    elif index == 10:  # Red
        ctf.AddRGBPoint(scalar_range[0], 0, 0, 0)
        ctf.AddRGBPoint(scalar_range[1], 1, 0, 0)

    elif index == 11:  # Green
        ctf.AddRGBPoint(scalar_range[0], 0, 0, 0)
        ctf.AddRGBPoint(scalar_range[1], 0, 1, 0)

    elif index == 12:  # Blue
        ctf.AddRGBPoint(scalar_range[0], 0, 0, 0)
        ctf.AddRGBPoint(scalar_range[1], 0, 0, 1)

    return ctf