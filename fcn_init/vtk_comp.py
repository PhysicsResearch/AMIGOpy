import vtk
import numpy as np
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.all import  vtkAxesActor, vtkOrientationMarkerWidget, vtkTransform
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5 import QtWidgets
from fcn_display.mouse_move_slicechanges import onMouseMoveCoronal, onMouseMoveSagittal, onMouseMoveAxial, left_button_pressaxial_event, left_button_releaseaxial_event


def populate_layer_list(self):
    # List of operations
    layer = ["0","1","2"]
    self.active_layer = self.findChild(QtWidgets.QComboBox, 'Layer_selection')
    # Populate the QComboBox
    self.active_layer.addItems(layer)
    # You can also connect the selection change event to a function
    #self.active_layer.currentIndexChanged.connect(lambda index: on_operation_selected(self, index))

def    init_axial_image_Actor(self):
    #
    self.dataImporterAxial = {}
    self.windowLevelAxial  = {}
    self.imageActorAxial   = {}
    #
    for i in range(4):  # Assuming 4 layers, adjust the range as needed
        self.dataImporterAxial[i] = vtk.vtkImageImport()
        self.windowLevelAxial[i]  = vtk.vtkImageMapToWindowLevelColors()
        self.windowLevelAxial[i].SetInputConnection(self.dataImporterAxial[i].GetOutputPort())
        self.imageActorAxial[i] = vtk.vtkImageActor()
        self.imageActorAxial[i].GetMapper().SetInputConnection(self.windowLevelAxial[i].GetOutputPort())
    
    
def    init_sagittal_image_Actor(self):
    #
    self.dataImporterSagittal = {}
    self.windowLevelSagittal  = {}
    self.imageActorSagittal   = {}
    #
    for i in range(4):  # Assuming 4 layers, adjust the range as needed
        self.dataImporterSagittal[i] = vtk.vtkImageImport()
        self.windowLevelSagittal[i]  = vtk.vtkImageMapToWindowLevelColors()
        self.windowLevelSagittal[i].SetInputConnection(self.dataImporterSagittal[i].GetOutputPort())
        self.imageActorSagittal[i] = vtk.vtkImageActor()
        self.imageActorSagittal[i].GetMapper().SetInputConnection(self.windowLevelSagittal[i].GetOutputPort())

def    init_coronal_image_Actor(self):
    #
    self.dataImporterCoronal = {}
    self.windowLevelCoronal  = {}
    self.imageActorCoronal   = {}
    #
    for i in range(4):  # Assuming 4 layers, adjust the range as needed
        self.dataImporterCoronal[i] = vtk.vtkImageImport()
        self.windowLevelCoronal[i]  = vtk.vtkImageMapToWindowLevelColors()
        self.windowLevelCoronal[i].SetInputConnection(self.dataImporterCoronal[i].GetOutputPort())
        self.imageActorCoronal[i] = vtk.vtkImageActor()
        self.imageActorCoronal[i].GetMapper().SetInputConnection(self.windowLevelCoronal[i].GetOutputPort())
  

def setup_vtk_comp(self):
    populate_layer_list(self)
    # Initialize VTK components - View section - Axial - Sagittal and Coronal
    vtk_layoutAxial = QVBoxLayout()
    self.vtkWidgetAxial = QVTKRenderWindowInteractor()
    vtk_layoutAxial.addWidget(self.vtkWidgetAxial)
    self.VTK_view_01.setLayout(vtk_layoutAxial)
    # Create the renderer here
    self.renAxial = vtk.vtkRenderer()
    self.vtkWidgetAxial.GetRenderWindow().AddRenderer(self.renAxial)
    #
    init_text_actor_axial(self)
    init_axial_lines(self) 
    # Start the VTK widget
    self.vtkWidgetAxial.Initialize()  
    self.vtkWidgetAxial.Start() 
    #
    imageStyle = vtk.vtkInteractorStyleImage()
    self.vtkWidgetAxial.SetInteractorStyle(imageStyle)
    # 
    init_axial_image_Actor(self)

    vtk_layoutSagittal = QVBoxLayout()
    self.vtkWidgetSagittal = QVTKRenderWindowInteractor()
    vtk_layoutSagittal.addWidget(self.vtkWidgetSagittal)
    self.VTK_view_02.setLayout(vtk_layoutSagittal)
    # Create the renderer here
    self.renSagittal = vtk.vtkRenderer()
    self.vtkWidgetSagittal.GetRenderWindow().AddRenderer(self.renSagittal)
    
    init_text_actor_sagittal(self)
    init_sagittal_lines(self)
    # Set the interactor style to vtkInteractorStyleImage
    # Start the VTK widget
    self.vtkWidgetSagittal.Initialize()  
    self.vtkWidgetSagittal.Start()  
    #
    imageStyleSagittal = vtk.vtkInteractorStyleImage()
    self.vtkWidgetSagittal.SetInteractorStyle(imageStyleSagittal)
    # #
    init_sagittal_image_Actor(self)

    vtk_layoutCoronal = QVBoxLayout()
    self.vtkWidgetCoronal = QVTKRenderWindowInteractor()
    vtk_layoutCoronal.addWidget(self.vtkWidgetCoronal)
    self.VTK_view_03.setLayout(vtk_layoutCoronal)
    # Create the renderer here
    self.renCoronal = vtk.vtkRenderer()
    self.vtkWidgetCoronal.GetRenderWindow().AddRenderer(self.renCoronal)
    #
    init_text_actor_coronal(self)
    init_coronal_lines(self)
    init_coord_ref_ax(self)
    # Start the VTK widget
    self.vtkWidgetCoronal.Initialize()  
    self.vtkWidgetCoronal.Start()  
    #
    imageStyleCoronal = vtk.vtkInteractorStyleImage()
    self.vtkWidgetCoronal.SetInteractorStyle(imageStyleCoronal)
    # #
    #
    init_coronal_image_Actor(self)
   
    #
    self.renAxial.GetActiveCamera().SetParallelProjection(1)
    self.renSagittal.GetActiveCamera().SetParallelProjection(1)
    self.renCoronal.GetActiveCamera().SetParallelProjection(1)
    #
    #
    set_mouse_button_custom_fcn(self)
    #
    init_display_empty_image(self)  
    #
    init_add_image_actor(self)
    
    
def init_add_image_actor(self):
    for i in range(len(self.dataImporterAxial)):
        self.renAxial.AddActor(self.imageActorAxial[i])
        self.renSagittal.AddActor(self.imageActorSagittal[i])
        self.renCoronal.AddActor(self.imageActorCoronal[i])
    self.renAxial.ResetCamera()
    self.renSagittal.ResetCamera()
    self.renCoronal.ResetCamera()

def init_display_empty_image(self):   
    slice_data = np.zeros((100, 100), dtype=np.uint16)
    data_string = slice_data.tobytes()
    extent = slice_data.shape
    # initialize display image
    for i in range(len(self.dataImporterAxial)):
        self.dataImporterAxial[i].SetDataScalarTypeToUnsignedShort()
        #
        self.dataImporterAxial[i].CopyImportVoidPointer(data_string, len(data_string))
        self.dataImporterAxial[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        self.dataImporterAxial[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        imageProperty = self.imageActorAxial[i].GetProperty()
        imageProperty.SetOpacity(0)  
        # Inform the pipeline that data has changed.
        self.dataImporterAxial[i].Modified()  
        #
        self.dataImporterSagittal[i].SetDataScalarTypeToUnsignedShort()
        self.dataImporterSagittal[i].CopyImportVoidPointer(data_string, len(data_string))
        self.dataImporterSagittal[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        self.dataImporterSagittal[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        imageProperty = self.imageActorSagittal[i].GetProperty()
        imageProperty.SetOpacity(0)  
        # Inform the pipeline that data has changed.
        self.dataImporterSagittal[i].Modified()
        #
        self.dataImporterCoronal[i].SetDataScalarTypeToUnsignedShort()
        self.dataImporterCoronal[i].CopyImportVoidPointer(data_string, len(data_string))
        self.dataImporterCoronal[i].SetWholeExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        self.dataImporterCoronal[i].SetDataExtent(0, extent[1]-1, 0, extent[0]-1, 0, 0)
        imageProperty = self.imageActorCoronal[i].GetProperty()
        imageProperty.SetOpacity(0)  
        # Inform the pipeline that data has changed.
        self.dataImporterCoronal[i].Modified() 
    

def init_text_actor_axial(self):
    # Initialize the text actor and set its properties - Axial
    # used for pixel info near the bootom 
    self.textActorAxial = vtk.vtkTextActor()
    self.textActorAxial.GetTextProperty().SetFontFamilyToArial()
    self.textActorAxial.GetTextProperty().SetFontSize(12)
    self.textActorAxial.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorAxial.SetPosition(10, 10)  # position at the bottom left
    # used for windowlevel and widht at top-left
    self.textActorAxialWL = vtk.vtkTextActor()
    self.textActorAxialWL.GetTextProperty().SetFontFamilyToArial()
    self.textActorAxialWL.GetTextProperty().SetFontSize(12)
    self.textActorAxialWL.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorAxialWL.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorAxialWL.SetPosition(0.01, 0.95)  # Near top-left corner
    #
    # used for windowlevel and widht at top-left
    self.textActorAxialInfo = vtk.vtkTextActor()
    self.textActorAxialInfo.GetTextProperty().SetFontFamilyToArial()
    self.textActorAxialInfo.GetTextProperty().SetFontSize(12)
    self.textActorAxialInfo.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorAxialInfo.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorAxialInfo.SetPosition(0.70, 0.88)  # Near top-right corner
    #
    # used for windowlevel and widht at top-left
    self.textActorAxialMetaTime = vtk.vtkTextActor()
    self.textActorAxialMetaTime.GetTextProperty().SetFontFamilyToArial()
    self.textActorAxialMetaTime.GetTextProperty().SetFontSize(12)
    self.textActorAxialMetaTime.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorAxialMetaTime.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorAxialMetaTime.SetPosition(0.01, 0.90)  # Near top-left corner
    #
    # add text actors
    self.renAxial.AddActor(self.textActorAxial)
    self.renAxial.AddActor(self.textActorAxialWL)
    self.renAxial.AddActor(self.textActorAxialMetaTime)
    self.renAxial.AddActor(self.textActorAxialInfo)

def init_text_actor_sagittal(self):
    # Initialize the text actor and set its properties - Sagittal
    self.textActorSagittal = vtk.vtkTextActor()
    self.textActorSagittal.GetTextProperty().SetFontFamilyToArial()
    self.textActorSagittal.GetTextProperty().SetFontSize(12)
    self.textActorSagittal.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  # white color
    self.textActorSagittal.SetPosition(10, 10)  # position at the bottom left
    #
    # used for windowlevel and widht at top-left
    self.textActorSagittalWL = vtk.vtkTextActor()
    self.textActorSagittalWL.GetTextProperty().SetFontFamilyToArial()
    self.textActorSagittalWL.GetTextProperty().SetFontSize(12)
    self.textActorSagittalWL.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorSagittalWL.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorSagittalWL.SetPosition(0.01, 0.95)  # Near top-left corner
    
    # used 
    self.textActorSagittalInfo = vtk.vtkTextActor()
    self.textActorSagittalInfo.GetTextProperty().SetFontFamilyToArial()
    self.textActorSagittalInfo.GetTextProperty().SetFontSize(12)
    self.textActorSagittalInfo.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorSagittalInfo.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorSagittalInfo.SetPosition(0.70, 0.88)  # Near top-right corner
    
    
    # used for time of IrIS
    self.textActorSagittalMetaTime = vtk.vtkTextActor()
    self.textActorSagittalMetaTime.GetTextProperty().SetFontFamilyToArial()
    self.textActorSagittalMetaTime.GetTextProperty().SetFontSize(12)
    self.textActorSagittalMetaTime.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorSagittalMetaTime.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorSagittalMetaTime.SetPosition(0.01, 0.90)  # Near top-left corner
    
    self.renSagittal.AddActor(self.textActorSagittal)
    self.renSagittal.AddActor(self.textActorSagittalWL)
    self.renSagittal.AddActor(self.textActorSagittalMetaTime)
    self.renSagittal.AddActor(self.textActorSagittalInfo)


def init_text_actor_coronal(self):
    # Initialize the text actor and set its properties - Coronal
    self.textActorCoronal = vtk.vtkTextActor()
    self.textActorCoronal.GetTextProperty().SetFontFamilyToArial()
    self.textActorCoronal.GetTextProperty().SetFontSize(12)
    self.textActorCoronal.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  # white color
    self.textActorCoronal.SetPosition(10, 10)  # position at the bottom left
    # used for windowlevel and widht at top-left
    self.textActorCoronalWL = vtk.vtkTextActor()
    self.textActorCoronalWL.GetTextProperty().SetFontFamilyToArial()
    self.textActorCoronalWL.GetTextProperty().SetFontSize(12)
    self.textActorCoronalWL.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorCoronalWL.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorCoronalWL.SetPosition(0.01, 0.95)  # Near top-left corner
    # used for
    self.textActorCoronalInfo = vtk.vtkTextActor()
    self.textActorCoronalInfo.GetTextProperty().SetFontFamilyToArial()
    self.textActorCoronalInfo.GetTextProperty().SetFontSize(12)
    self.textActorCoronalInfo.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorCoronalInfo.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorCoronalInfo.SetPosition(0.70, 0.88)  # Near top-right corner
    # used for IrIS time
    self.textActorCoronalMetaTime = vtk.vtkTextActor()
    self.textActorCoronalMetaTime.GetTextProperty().SetFontFamilyToArial()
    self.textActorCoronalMetaTime.GetTextProperty().SetFontSize(12)
    self.textActorCoronalMetaTime.GetTextProperty().SetColor(0.2549, 0.7765, 0.9490)  
    self.textActorCoronalMetaTime.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
    self.textActorCoronalMetaTime.SetPosition(0.01, 0.90)  # Near top-left corner
    #
    self.renCoronal.AddActor(self.textActorCoronal)
    self.renCoronal.AddActor(self.textActorCoronalWL)
    self.renCoronal.AddActor(self.textActorCoronalMetaTime)
    self.renCoronal.AddActor(self.textActorCoronalInfo)

def init_coord_ref_ax(self):
    # For Axial view
    self.axesActorAxial = vtkAxesActor()
    # Hide the Z label
    self.axesActorAxial.GetYAxisCaptionActor2D().GetTextActor().GetTextProperty().SetOpacity(0)
    self.axesActorAxial.GetXAxisShaftProperty().SetLineWidth(2)
    self.axesActorAxial.GetYAxisShaftProperty().SetLineWidth(2)
    self.axesActorAxial.GetZAxisShaftProperty().SetLineWidth(2)
    self.axesActorAxial.SetScale(10)  
    self.axesActorAxial.SetConeRadius(0.2)
    # 
    transform = vtkTransform()
    transform.RotateX(-90)
    # Set the transform to the actor
    self.axesActorAxial.SetUserTransform(transform)
    #
    self.orientationWidgetAxial = vtkOrientationMarkerWidget()
    self.orientationWidgetAxial.SetOrientationMarker(self.axesActorAxial)
    self.orientationWidgetAxial.SetInteractor(self.vtkWidgetAxial.GetRenderWindow().GetInteractor())
    self.orientationWidgetAxial.SetEnabled(1)
    self.orientationWidgetAxial.InteractiveOff()
    self.orientationWidgetAxial.SetViewport(0.85, 0., 1.05, 0.25)  # adjust this for position and size
    #
    # For Sagittal view
    self.axesActorSagittal = vtkAxesActor()
    # Hide the Z label
    self.axesActorSagittal.GetXAxisCaptionActor2D().GetTextActor().GetTextProperty().SetOpacity(0)
    self.axesActorSagittal.GetXAxisShaftProperty().SetLineWidth(2)
    self.axesActorSagittal.GetYAxisShaftProperty().SetLineWidth(2)
    self.axesActorSagittal.GetZAxisShaftProperty().SetLineWidth(2)
    self.axesActorSagittal.SetScale(10)  
    self.axesActorSagittal.SetConeRadius(0.2)
    # Create a transform and apply a 180-degree rotation about the X-axis
    transform = vtkTransform()
    transform.RotateZ(90)
    transform.RotateY(90)
    transform.RotateX(90)
    # Set the transform to the actor
    self.axesActorSagittal.SetUserTransform(transform)
    self.orientationWidgetSagittal = vtkOrientationMarkerWidget()
    self.orientationWidgetSagittal.SetOrientationMarker(self.axesActorSagittal)
    self.orientationWidgetSagittal.SetInteractor(self.vtkWidgetSagittal.GetRenderWindow().GetInteractor())
    self.orientationWidgetSagittal.SetEnabled(1)
    self.orientationWidgetSagittal.InteractiveOff()
    self.orientationWidgetSagittal.SetViewport(0.85, 0., 1.05, 0.25)  # adjust this for position and size
    #
    # For Coronal view
    self.axesActorCoronal = vtkAxesActor()   
    # Hide the Z label
    self.axesActorCoronal.GetZAxisCaptionActor2D().GetTextActor().GetTextProperty().SetOpacity(0)
    self.axesActorCoronal.GetXAxisShaftProperty().SetLineWidth(2)
    self.axesActorCoronal.GetYAxisShaftProperty().SetLineWidth(2)
    self.axesActorCoronal.GetZAxisShaftProperty().SetLineWidth(2)
    self.axesActorCoronal.SetScale(10)  
    self.axesActorCoronal.SetConeRadius(0.2)
    # # Create a transform and apply a 180-degree rotation about the X-axis
    # transform = vtkTransform()
    self.orientationWidgetCoronal = vtkOrientationMarkerWidget()
    self.orientationWidgetCoronal.SetOrientationMarker(self.axesActorCoronal)
    self.orientationWidgetCoronal.SetInteractor(self.vtkWidgetCoronal.GetRenderWindow().GetInteractor())
    self.orientationWidgetCoronal.SetEnabled(1)
    self.orientationWidgetCoronal.InteractiveOff()
    self.orientationWidgetCoronal.SetViewport(0.85, 0., 1.05, 0.25)  # adjust this for position and size

def init_axial_lines(self):
    # Set the interactor style to vtkInteractorStyleImage'
    # Initialize line source, mapper, and actor for the axial line
    # Line that shows coronal position in the axial view
    self.axialLineSource = vtk.vtkLineSource()
    self.axialLineMapper = vtk.vtkPolyDataMapper()
    self.axialLineMapper.SetInputConnection(self.axialLineSource.GetOutputPort())
    self.axialLineActor = vtk.vtkActor()
    self.axialLineActor.SetMapper(self.axialLineMapper)
    self.axialLineActor.GetProperty().SetColor(0.2549, 0.7765, 0.9490)   # Blue
    self.axialLineActor.GetProperty().SetLineStipplePattern(0xF0F0)  # Dashed
    self.axialLineActor.GetProperty().SetLineWidth(1)
    self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.axialLineActor)

    # Initialize line source, mapper, and actor for the axial line
    # Line to display sagittal position in the axial view
    self.axialLine2Source = vtk.vtkLineSource()
    self.axialLine2Mapper = vtk.vtkPolyDataMapper()
    self.axialLine2Mapper.SetInputConnection(self.axialLine2Source.GetOutputPort())
    self.axialLine2Actor = vtk.vtkActor()
    self.axialLine2Actor.SetMapper(self.axialLine2Mapper)
    self.axialLine2Actor.GetProperty().SetColor(0.2549, 0.7765, 0.9490)   # Blue
    self.axialLine2Actor.GetProperty().SetLineStipplePattern(0xF0F0)  # Dashed
    self.axialLine2Actor.GetProperty().SetLineWidth(1)
    self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.axialLine2Actor)
    
    
def init_sagittal_lines(self):
    # Initialize line source, mapper, and actor for the axial line
    self.sagittalLineSource = vtk.vtkLineSource()
    self.sagittalLineMapper = vtk.vtkPolyDataMapper()
    self.sagittalLineMapper.SetInputConnection(self.sagittalLineSource.GetOutputPort())
    self.sagittalLineActor = vtk.vtkActor()
    self.sagittalLineActor.SetMapper(self.sagittalLineMapper)
    self.sagittalLineActor.GetProperty().SetColor(0.2549, 0.7765, 0.9490)   # Blue
    self.sagittalLineActor.GetProperty().SetLineStipplePattern(0xF0F0)  # Dashed
    self.sagittalLineActor.GetProperty().SetLineWidth(1)
    self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.sagittalLineActor)
    
    
    self.sagittalLine2Source = vtk.vtkLineSource()
    self.sagittalLine2Mapper = vtk.vtkPolyDataMapper()
    self.sagittalLine2Mapper.SetInputConnection(self.sagittalLine2Source.GetOutputPort())
    self.sagittalLine2Actor = vtk.vtkActor()
    self.sagittalLine2Actor.SetMapper(self.sagittalLine2Mapper)
    self.sagittalLine2Actor.GetProperty().SetColor(0.2549, 0.7765, 0.9490)   # Blue
    self.sagittalLine2Actor.GetProperty().SetLineStipplePattern(0xF0F0)  # Dashed
    self.sagittalLine2Actor.GetProperty().SetLineWidth(1)
    self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.sagittalLine2Actor)
    
    
def init_coronal_lines(self): 
    # Line that shows coronal position in the axial view
    # shows axial position in the coronal view.
    self.coronalLineSource = vtk.vtkLineSource()
    self.coronalLineMapper = vtk.vtkPolyDataMapper()
    self.coronalLineMapper.SetInputConnection(self.coronalLineSource.GetOutputPort())
    self.coronalLineActor = vtk.vtkActor()
    self.coronalLineActor.SetMapper(self.coronalLineMapper)
    self.coronalLineActor.GetProperty().SetColor(0.2549, 0.7765, 0.9490)   # Blue
    self.coronalLineActor.GetProperty().SetLineStipplePattern(0xF0F0)  # Dashed
    self.coronalLineActor.GetProperty().SetLineWidth(1)
    self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.coronalLineActor)
    
    self.coronalLine2Source = vtk.vtkLineSource()
    self.coronalLine2Mapper = vtk.vtkPolyDataMapper()
    self.coronalLine2Mapper.SetInputConnection(self.coronalLine2Source.GetOutputPort())
    self.coronalLine2Actor = vtk.vtkActor()
    self.coronalLine2Actor.SetMapper(self.coronalLine2Mapper)
    self.coronalLine2Actor.GetProperty().SetColor(0.2549, 0.7765, 0.9490)   # Blue
    self.coronalLine2Actor.GetProperty().SetLineStipplePattern(0xF0F0)  # Dashed
    self.coronalLine2Actor.GetProperty().SetLineWidth(1)
    self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.coronalLine2Actor)
    # Set the interactor style to vtkInteractorStyleImage
 
    
def set_mouse_button_custom_fcn(self):
     # After setting up your vtkWidget and renderer:
     interactor_styleAxial = self.vtkWidgetAxial.GetInteractorStyle()
     interactor_styleAxial.AddObserver("MouseWheelForwardEvent", self.on_scroll_forwardAxial)
     interactor_styleAxial.AddObserver("MouseWheelBackwardEvent", self.on_scroll_backwardAxial)
     interactor_styleAxial.AddObserver("LeftButtonReleaseEvent", lambda caller, event: left_button_releaseaxial_event(self, caller, event))
     interactor_styleAxial.AddObserver("LeftButtonPressEvent", lambda caller, event: left_button_pressaxial_event(self, caller, event))
     interactor_styleAxial.OnMouseWheelForward = lambda: None
     interactor_styleAxial.OnMouseWheelBackward = lambda: None
     interactor_styleAxial.OnLeftButtonDown = lambda: None
     interactor_styleAxial.OnLeftButtonUp = lambda: None
     
     #
     self.vtkWidgetAxial.AddObserver("LeftButtonPressEvent", lambda caller, event: left_button_pressaxial_event(self, caller, event),0)
     self.vtkWidgetAxial.AddObserver("LeftButtonReleaseEvent",lambda caller, event:left_button_releaseaxial_event(self, caller, event),0)
     # mouse
     self.vtkWidgetAxial.AddObserver("MouseWheelForwardEvent", self.on_scroll_forwardAxial)
     self.vtkWidgetAxial.AddObserver("MouseWheelBackwardEvent", self.on_scroll_backwardAxial)
     #
     # After setting up your vtkWidget and renderer:
     interactor_styleSagittal = self.vtkWidgetSagittal.GetInteractorStyle()
     interactor_styleSagittal.AddObserver("LeftButtonReleaseEvent", self.left_button_releasesagittal_event)
     interactor_styleSagittal.AddObserver("LeftButtonPressEvent", self.left_button_presssagittal_event)
     interactor_styleSagittal.AddObserver("MouseWheelForwardEvent", self.on_scroll_forwardSagittal)
     interactor_styleSagittal.AddObserver("MouseWheelBackwardEvent", self.on_scroll_backwardSagittal)
     interactor_styleSagittal.OnMouseWheelForward  = lambda: None
     interactor_styleSagittal.OnMouseWheelBackward = lambda: None
     interactor_styleSagittal.OnLeftButtonDown     = lambda: None
     interactor_styleSagittal.OnLeftButtonUp       = lambda: None
     # mouse
     self.vtkWidgetSagittal.AddObserver("MouseWheelForwardEvent", self.on_scroll_forwardSagittal)
     self.vtkWidgetSagittal.AddObserver("MouseWheelBackwardEvent", self.on_scroll_backwardSagittal)
     #
     self.vtkWidgetSagittal.AddObserver("LeftButtonPressEvent", self.left_button_presssagittal_event,0)
     self.vtkWidgetSagittal.AddObserver("LeftButtonReleaseEvent", self.left_button_releasesagittal_event,0)
     #
     #
     # After setting up your vtkWidget and renderer:
     interactor_styleCoronal = self.vtkWidgetCoronal.GetInteractorStyle()
     interactor_styleCoronal.AddObserver("LeftButtonReleaseEvent", self.left_button_releasecoronal_event)
     interactor_styleCoronal.AddObserver("LeftButtonPressEvent", self.left_button_presscoronal_event)
     interactor_styleCoronal.AddObserver("MouseWheelForwardEvent", self.on_scroll_forwardCoronal)
     interactor_styleCoronal.AddObserver("MouseWheelBackwardEvent", self.on_scroll_backwardCoronal)
     interactor_styleCoronal.OnMouseWheelForward   = lambda: None
     interactor_styleCoronal.OnMouseWheelBackward  = lambda: None
     interactor_styleCoronal.OnLeftButtonDown      = lambda: None
     interactor_styleCoronal.OnLeftButtonUp        = lambda: None
     
     # Window level
     self.vtkWidgetCoronal.AddObserver("LeftButtonPressEvent", self.left_button_presscoronal_event,0)
     self.vtkWidgetCoronal.AddObserver("LeftButtonReleaseEvent", self.left_button_releasecoronal_event,0)
                     
     # mouse to chenge slice
     self.vtkWidgetCoronal.AddObserver("MouseWheelForwardEvent", self.on_scroll_forwardCoronal)
     self.vtkWidgetCoronal.AddObserver("MouseWheelBackwardEvent", self.on_scroll_backwardCoronal)
     
     self.vtkWidgetSagittal.GetRenderWindow().GetInteractor().AddObserver("MouseMoveEvent",lambda caller, event: onMouseMoveSagittal(self, caller, event))
     self.vtkWidgetCoronal.GetRenderWindow().GetInteractor().AddObserver("MouseMoveEvent",lambda caller, event: onMouseMoveCoronal(self, caller, event))
     self.vtkWidgetAxial.GetRenderWindow().GetInteractor().AddObserver("MouseMoveEvent",lambda caller, event:onMouseMoveAxial(self, caller, event))