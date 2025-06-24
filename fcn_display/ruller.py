# Ruller

import vtk

def create_ruler(self):
    if not hasattr(self, 'axialRullerActor'):
        # create a ruler
        self.axialRullerSource = vtk.vtkLineSource()
        self.axialRullerMapper = vtk.vtkPolyDataMapper()
        self.axialRullerMapper.SetInputConnection(self.axialRullerSource.GetOutputPort())
        self.axialRullerActor = vtk.vtkActor()
        self.axialRullerActor.SetMapper(self.axialRullerMapper)
        self.axialRullerActor.GetProperty().SetColor(1, 0, 0)   # RED
        self.axialRullerActor.GetProperty().SetLineStipplePattern(0xF0F0)  # Dashed
        self.axialRullerActor.GetProperty().SetLineWidth(1)
        self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.axialRullerActor)
        
        self.endpoints_Ruller_axial01 = vtk.vtkRegularPolygonSource()
        self.endpoint_Ruler_axial_actors01 = []
        self.endpoints_Ruller_axial01.SetRadius(3)  # Adjust the radius as needed
        self.endpoints_Ruller_axial01.SetNumberOfSides(4)  # Use a high number for a smooth circle
        self.endpoints_Ruller_axialmapper01 = vtk.vtkPolyDataMapper()
        self.endpoints_Ruller_axialmapper01.SetInputConnection(self.endpoints_Ruller_axial01.GetOutputPort())
        self.endpoints_Ruller_axialactor01 = vtk.vtkActor()
        self.endpoints_Ruller_axialactor01.SetMapper(self.endpoints_Ruller_axialmapper01)
        
        self.axialRullerSource.SetPoint1(0, 0, 0.1)
        self.axialRullerSource.SetPoint2(0, 20, 0.1)
           
        self.endpoints_Ruller_axial01.SetCenter([0,0,0])
        self.endpoints_Ruller_axialactor01.SetPosition([0,0,0])
        self.endpoints_Ruller_axialactor01.GetProperty().SetColor(1, 0, 0)  # RGB for red
        self.endpoints_Ruller_axialactor01.GetProperty().SetOpacity(0.5)  # Adjust opacity for semi-transparency
        
        self.endpoints_Ruller_axial02 = vtk.vtkRegularPolygonSource()
        self.endpoint_Ruler_axial_actors02 = []
        self.endpoints_Ruller_axial02.SetRadius(3)  # Adjust the radius as needed
        self.endpoints_Ruller_axial02.SetNumberOfSides(4)  # Use a high number for a smooth circle
        self.endpoints_Ruller_axialmapper02 = vtk.vtkPolyDataMapper()
        self.endpoints_Ruller_axialmapper02.SetInputConnection(self.endpoints_Ruller_axial02.GetOutputPort())
        self.endpoints_Ruller_axialactor02 = vtk.vtkActor()
        self.endpoints_Ruller_axialactor02.SetMapper(self.endpoints_Ruller_axialmapper02)
        
        self.endpoints_Ruller_axial02.SetCenter([0,20,0])
        #self.endpoints_Ruller_axialactor02.SetPosition([0,20,0])
        self.endpoints_Ruller_axialactor02.GetProperty().SetColor(1, 0, 0)  # RGB for red
        self.endpoints_Ruller_axialactor02.GetProperty().SetOpacity(0.5)  # Adjust opacity for semi-transparency
        
        self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.endpoints_Ruller_axialactor01)
        self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.endpoints_Ruller_axialactor02)
       
        # used for ruler
        self.textActorAxialRuller = vtk.vtkTextActor()
        self.textActorAxialRuller.GetTextProperty().SetFontFamilyToArial()
        self.textActorAxialRuller.GetTextProperty().SetFontSize(12)
        self.textActorAxialRuller.GetTextProperty().SetColor(1, 0, 0)  
        self.textActorAxialRuller.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.textActorAxialRuller.SetPosition(0.01, 0.60)  # Near top-left corner
        self.renAxial.AddActor(self.textActorAxialRuller)
        
        
        
    else:
        # Toggle visibility of the ruler elements
        toggle_visibility(self,self.axialRullerActor)
        toggle_visibility(self,self.endpoints_Ruller_axialactor01)
        toggle_visibility(self,self.endpoints_Ruller_axialactor02)
        toggle_visibility(self,self.textActorAxialRuller)
        
    # Update the render window
    self.vtkWidgetAxial.GetRenderWindow().Render()
    
    # Function to toggle visibility
def toggle_visibility(self, actor):
    actor.SetVisibility(not actor.GetVisibility())