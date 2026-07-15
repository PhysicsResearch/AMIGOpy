# Segmentation


On the Segmentation tab, the user can find multiple tools for delineating structures in CT images. The current delineation tools include Hounsfield Unit-based thresholding, as well as a HU-based brush and eraser tool. The Segmentation module also included functions to export key statistics such as volume, and centre-of-mass, and export the structures as a mask in .nifti format. On this page, the user can find an extensive explanation of the possible functionalities.

## Creating empty structures

In order to use one of the segmentation tools, the user first has to create an empty structure. This can be seen as an empty canvas on which the segmentation will be 'drawn'. The user has the option to create a structure for the select volume only, or for all the loaded image volumes.

### Create single empty structure

To create a empty structure for an image volume:

- Click on the image volume for which to create an empty structure.

- Insert the name of structure to be created (only letters and digits)

- To also create the empty structure for the other series of the selected patient, enable the "All series" option.

- Press "Create structure"

- If a structure with the specified name already exists, the user will be prompted to either overwrite this structure or cancel creating the empty structure.

The structure(s) will now be added to the Data tree view (on the left) & Structures overview (top right).

![YouTube Video](https://img.youtube.com/vi/SEZJr_uCjJc/0.jpg)
[Watch Video](https://www.youtube.com/watch?v=SEZJr_uCjJc)

### Deleting 

structures for multiple volumes

To delete one of the created structures

- Select the structure to be removed & press "Delete structure"

- Enable the "All series" option to delete the structures with the same name from all other image series.

- The user will be prompted with a warning prompt, to verify deleting the structure of interest.

The structure(s) will now be deleted and removed from the Data Tree View and the Structures overview.

![YouTube Video](https://img.youtube.com/vi/Q6_eySWEqpg/0.jpg)
[Watch Video](https://www.youtube.com/watch?v=Q6_eySWEqpg)

## Manual delineation tools

For manual delineation, the user can use the brush, erase and undo functionalities.

- First, select a structure to delineate and select the brush tool under the Manual edits tab.

- To clip the Brush or Eraser to specific Hounsfield-Unit range, specify the HU range to clip the brush and erase tool, using the sliders and the HU distribution graph on the top.

- The undo button can be used to undo the latest brush or erase stroke.

- Additionally, the user can specify brush size, which is useful when delineating small or large structures.

![YouTube Video](https://img.youtube.com/vi/A35K1tHSGlA/0.jpg)
[Watch Video](https://www.youtube.com/watch?v=A35K1tHSGlA)

![YouTube Video](https://img.youtube.com/vi/H-YpGdgQBIk/0.jpg)
[Watch Video](https://www.youtube.com/watch?v=H-YpGdgQBIk)

![YouTube Video](https://img.youtube.com/vi/9JjyaGqJ7Wc/0.jpg)
[Watch Video](https://www.youtube.com/watch?v=9JjyaGqJ7Wc)

![YouTube Video](https://img.youtube.com/vi/GT1lTUXtpuY/0.jpg)
[Watch Video](https://www.youtube.com/watch?v=GT1lTUXtpuY)

![YouTube Video](https://img.youtube.com/vi/Lbo5Qt254LY/0.jpg)
[Watch Video](https://www.youtube.com/watch?v=Lbo5Qt254LY)

## Morphological operations

Currently, four morphological operations are supported, including Erosion, Dilation, Opening & Closing. These are implemented using the binary_erosion, binary_dilation, binary_opening and binary_closing functions of scipy.ndimage (https://docs.scipy.org/doc/scipy/reference/ndimage.html). The user can change the rank, connectivity and number of iterations, depending on the image dimension and application. More information regarding these variables can be found on https://docs.scipy.org/doc/scipy/reference/ndimage.html#morphology.

![YouTube Video](https://img.youtube.com/vi/fz6tukD4InQ/0.jpg)
[Watch Video](https://www.youtube.com/watch?v=fz6tukD4InQ)

## Exporting

Once the user has delineated the structures of interest, they can go to the Analysis tab.

- First, the user can press "Calculate statistics"  to calculate some statistics of the structure such as the volume and the center-of-mass.

- Next, the user can select the structures to export using the checkboxes.

- The user can then export the statistics of the selected structures as a comma-separated values (CSV) file by clicking on the "Export statistics" button and selecting the folder destination.

- Lastly, the user can export the 3D masks corresponding to the structures in nifti format by clicking on "Export structures" and selecting the folder destination.

![YouTube Video](https://img.youtube.com/vi/Fnr3d8epLo4/0.jpg)
[Watch Video](https://www.youtube.com/watch?v=Fnr3d8epLo4)