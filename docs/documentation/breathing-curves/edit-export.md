# Edit & export


One the user has either imported a CSV/VXP file or created their own analytical breathing curve, it will be displayed on the Edit & export tab. This tab contains a multitude of operations to apply to crop and edit fragments from a breathing curve. The main functionalities are cropping, editing the time-domain (e.g. speeding up/slowing down the curve), editing the amplitude (scaling, shifting and thresholding), as well as inserting breath holds. Once the user is satisfied with the editing process, the fragment can be exported either as a CSV (raw table data) or GCODE file (e.g. as input to drive motion in phantoms).

The following image shows an initial overview of the Edit & export tab. On the left are the panels to apply the editing operations, and export the curve. On the right the amplitude of the curve is displayed as a function of time, together with sliders to select a specific range.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d1wS5L9JyddNlOOtKQP32gn2yuCSeytc6RJm6vjsB8kJFDVYV8rFHLYzQfgkKjcZO14ElNWd7LxSvdeDdFXieaGr5mymCh5s5DHWK1FZLZAvl1YVHJiXE5niE631WjWFVZQeIFCclD3XbgUX9MvhfowaClGlPBhPmXkG94JlOla6Erpx2dgW2WIv9OI4ivrplLNdm1vqybjhxBGZLQ3PH0hko7DsOsRQXw8UpIL=w1280)

## Cropping

In order to select a specific fragment from the curve:

- Change the slider position to select the desired range

- If information about the individual breathing cycles (e.g. phase, instance) is available, the user can check the the Clip to whole cycles option. This option will trim the the "loose" ends of the curve and return only the full cycles.

- Press Crop, after which the curve will be cropped to the selected range (Note: the time information will be reset, starting from zero)

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2U4HUU4zK2XaJ87ES3k0OeOOxwtBMtM4n0UGjL16S2_a5U1lOgHjZekYttLko0GcROM5YqClss5IxgPFuZarN9Hc2dNLQ64_UdK_rV_vVYvz1Q0ggaxNais5qb6cvDDmRB0omQ10cf2f-bR6so2R_XoU3cQBfDODNWhBMCIwNAGg40ipyCeZ334bRwGabwfsiCYJz57upUobxBGURVqeCrjYud27yZAH3KeDK3DBE=w1280)

## Operations

Multiple operations are included to change the overall morphology of the breathing curve:

- The Scale frequency operation can be used to speed up or slow down the breathing curve, either by decreasing or increasing the interpolation value relative to one.

- The Scale amplitude operation is used to scale the amplitude of the curve by multiplication with the set value.

- The Shift amplitude operation is used to shift the amplitude up or down (only if Set min value to zero is unchecked)

- The Max. amplitude threshold will clip the amplitude values that are higher than the set threshold (e.g. to avoid amplitude values that cannot be executed by motors).

- The Set min value to zero option will shift the curve so that the minimum value is set to zero (only relative amplitude changes)

The following image shows the resulting curve after applying a scale frequency factor of 0.5, scale amplitude factor of 2.0, shift value of -10.0 and a max. amplitude threshold of 43.0. Note that the total time is reduced from 100 s (100,000 ms) to 50 s (50,000 ms), and the values are clipped to a maximum amplitude of 43.0 mm (compared to the initial curve displayed at the top of this page).

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2vBKtitQMiFBUHwC-w7adHGt8WLq-52Wsx_pOfwo8StLn0xKOEGHbekG1TKneGbyPspCV1MBdKHZ2RKf02PKnZhFsMTvJsiSPtX-6c3ya0Tg_RwenvKXXkIj2NtCsMi0K2SB_iwCZeWKRZ36cVmpdNodZqto8QZuTNm2Zvv57K3fKO_qBpSuvO6Pi7iDJCsUmRKE6pBh44X6n3pbkaoFvaXG3tHpcph_RIdcNe8pc=w1280)

## Breath hold

The current implementation of AMIGOpy enables the user to insert a breath hold in the breathing curve. This requires information regarding the individual breathing cycles to be present (e.g. phase or instance). In a future edition, this requirement might not be needed anymore.

- Check the Apply breath hold option to enable the breath hold functionality

- Put in the start timestamp to insert the breath hold. This should be in the unit of the X-axis that is selected (either time in ms or s).

- Select the duration of the breath hold in seconds

After pressing Apply operations the breath holds will be inserted at the maximum breathing cycle amplitude, closest to the provided start timestamp input.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2SZmzv6JQpqsVElY7gID2WPSLuuG_NRHwglu1q2ZWqii4jSmKPoPuG2AphvzEtl5Ena7IqXCPP5v5xtNpkM0dS1Php2tM02pnvODINXhcx0MgVLPSBlioDJsGI7RVhfL6NPrKQ8OvmRk45Ltvp07mgLu79ZCSBmHZJ6BXhatoD8NBgtY3zOccB5Hg_uZgXgqlXjnaMv4bloYZEJWvyxPjPPDHKFPPbPMZLJyPhktI=w1280)

## Undo

If at any point the user is not satisfied with the applied changes, the Undo button enables the user to revert the latest operation applied to the curve.

## Export

The edited fragment (as displayed in the right panel) can be exported either as a CSV or GCODE file.

- Select the number of times the fragment is to be copied (e.g. multiple consecutive fragments might be required when using the curve as input during measurements)

To ensure the curve is smooth, the last breathing cycle in the fragment is scaled to the amplitude of the first cycle. This is required to avoid discontinuities that could results in problems when using the breathing curve as input to drive motion.

- Put in the filename of the output file

- By pressing the Export CSV button, the raw data (as displayed on the Import & create tab) with the applied edits is exported to a CSV file.

- By pressing the Export GCODE button, the data is processed to calculate the velocity (derivative of the amplitude), and acceleration (derivative of the velocity) of the breathing signal. Additionally, the speed (absolute value of the velocity in [mm/min] is calculated, as this is required to be used as input to drive motion. The amplitude, velocity, acceleration and speed are then exported to a CSV and GCODE file.