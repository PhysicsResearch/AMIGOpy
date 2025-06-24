import vtk
from fcn_display.display_images_comp import disp_comp_image_slice

def toggle_camera_linking(self):
    if self.comp_link_zoom.isChecked():
        link_cameras(self)
    else:
        unlink_cameras(self)
    disp_comp_image_slice(self)
        
def link_cameras(self):
    master_camera = self.renAxComp[0].GetActiveCamera()
    for renderer in self.renAxComp:
        renderer.SetActiveCamera(master_camera)
    # You might need to re-render the first VTK widget or all, depending on your setup
    self.vtkWidgetsComp[0].GetRenderWindow().Render()
    

def unlink_cameras(self):
    # Assume the first renderer's camera is the one currently being shared
    shared_camera = self.renAxComp[0].GetActiveCamera()
     
    for renderer in self.renAxComp:
        # Create a new camera for each renderer
        new_camera = vtk.vtkCamera()
        # Copy settings from the shared camera to the new camera
        copy_camera_settings(shared_camera, new_camera)
        # Set the new camera as the active camera for the renderer
        renderer.SetActiveCamera(new_camera)
        # Re-render the scene for this renderer to update the view
        renderer.GetRenderWindow().Render()
    

def copy_camera_settings(source_camera, target_camera):
    target_camera.SetPosition(source_camera.GetPosition())
    target_camera.SetFocalPoint(source_camera.GetFocalPoint())
    target_camera.SetViewUp(source_camera.GetViewUp())
    target_camera.SetClippingRange(source_camera.GetClippingRange())
    target_camera.SetViewAngle(source_camera.GetViewAngle())
    target_camera.SetParallelScale(source_camera.GetParallelScale())