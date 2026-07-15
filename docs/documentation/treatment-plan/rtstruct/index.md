# RTSTRUCT


![Image](https://sites.google.com/sitesv-images-rt/ACHe0d154DJ9AhFzzqaZVk4SBxkbpC7xeY7ug_Wy4y6ZS8lalmoQWIxBic1s_Qb2e1eCq6NYS0ltnh6heCXKkejZys8iS8PMAzof_JW2KEc3yl6ERY0DtOBgcx-zXecyl89EqPOco9XTl46pi_YnuIMU14dnkgIHK_fhjeU9gH701upmAoUXjkhrCMvn0ZtrW1-ND7WDFLK8iQm9wHmYU7HINY96oCmylMNeKkR1oIy9=w1280)

# Loading RTSTRUCT files

When opening a folder, AMIGOpy will automatically load all available RTSTRUCT, RTPLAN, RTDOSE, and image files, organizing them by patient, study, and modality.

In the example below, two structure files were detected. Users can click on a file and navigate to the STRUCT tab (see image below) to view a list of available contours.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2VazkonGPf6Qrq9c_WP91ZP-1DIe0Knat5Ij2VMV1vSsGlN1AAeLR1JD_c-6cno2hk8Xes0fiyEAq3iAmlANhGUKAb28oJtdrWFvvRkV-IkYD4X9welUH-gYNUZ7603Olf5gIXfjvLbRAnf1XYd1offVCZEzOUoGlQMplHm12Q5pN1qdTrU-y2oDDaaP7ezgTIVVzuxE6xazEEeT5AXjBn2coO5359CjRs6nqZg9Y=w1280)

The RTSTRUCT file in Series 8 contains three contours (BODY, Bones, and NS_Control), which were created in a phantom for illustrative purposes.

⚠ IMPORTANT: Although some options (e.g., Select Color) are available, the contours are not yet ready for display.

### Reference Image Series

Pay close attention to the Ref. Series field. This indicates the image series in which the RTSTRUCT was created or linked in the TPS. The dimensions, coordinates, and other attributes should align with this reference image. However, users can apply the contours to any image series—though this may not always work correctly.

### Importing Contours

- Select the contours to import – Since computing the mask and contours takes time, users may choose to load specific contours first and add more later.

- Select the corresponding image series – Click on the image series you want to match with the contours. Ensure that the image series (not the RTSTRUCT) is selected in the data tree.

- Press "Create Mask" (blue button) – The process may take a few minutes (usually seconds), depending on resolution and the number of contours. The progress bar may take a few seconds to update.

Note: If no image series is selected, nothing will happen.

Note: Shift and calling are currently not implemented

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d3YjH9N9cvk2xLj0s3UZ28VWwBawDCan2oPee4XYlx3aPfUh3AB3ZgUi7BMblaRydl4KrKXXJEEfGwhYSLA5V6yrtKGV5PRTXT5wulUm39hfjy_iSymiHLQWJmXRGtQ0rfCQb9BxO0nMSYl5gw3UUaJ4GcLZcCfg93Xj2tt77h5KRgZdrJKAnQ9rcOjwTUh7gfQKbCvOoVrGQCr5YR3qR8ylJ5SflOgKsKxl_8xtnw=w1280)

# Structure list

Once the contours are loaded, expand the tree to confirm that a new Structure item has been created.

There are different ways to visualize the contours—simply clicking on them may not work as expected. For detailed instructions on visualization options, refer to the videos below.

![YouTube Video](https://img.youtube.com/vi/iq3nYSIwCkw/0.jpg)
[Watch Video](https://www.youtube.com/watch?v=iq3nYSIwCkw)

## Link structures with an image series

This video explains how to open RSTRUCTs an link with an image series. It is essential to undestand how AMIGOpy works!

![YouTube Video](https://img.youtube.com/vi/xjQnBeRXTgg/0.jpg)
[Watch Video](https://www.youtube.com/watch?v=xjQnBeRXTgg)

## Display contours

This video explains visualize contours overlaid on a CT. It is essential to undestand how AMIGOpy works! It is simple but some steps are very important.

![YouTube Video](https://img.youtube.com/vi/aPVUMCSpMio/0.jpg)
[Watch Video](https://www.youtube.com/watch?v=aPVUMCSpMio)

## Show masks

This video explains visualize voxlized masks overlaid on a CT.

![YouTube Video](https://img.youtube.com/vi/3Qfh8nbpdNQ/0.jpg)
[Watch Video](https://www.youtube.com/watch?v=3Qfh8nbpdNQ)

## Replace or Append

This video shows how to combine contours from different RTSTRUCT files with the same CT series