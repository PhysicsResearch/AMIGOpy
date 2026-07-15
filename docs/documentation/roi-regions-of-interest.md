# ROI - Regions of interest


Regions of Interest (ROIs) can be useful for quantitative analysis. In the future, more options and shapes will be added, but for now, only cylinders are available. The user can export the values as CSV files and perform analysis elsewhere, or within AMIGOpy, for example, for DECT. The figure below shows a Gammex phantom with multiple ROIs.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0wn90TluAX98OZ9ueJB37SlzMezEn-8eTjFc14mo9s6LTGZz1K2TeSUBOfac078k4glC9gGes0J49YO2ZvFpMA-r5DuOwjFn0IaG_QXmiGiEoDsdHeBIlwJinIIKLW9k7z7p5hiYwpjoAp5gx2f4_xH7vhrWiq7TMPYA4vxy0pwgXbcWXjXMwe3iFTFNA6bV0xLYF2L_fqqksb3JZnUjr7MlnMXhB-gVnHZAuAVwY=w1280)

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0d53lZuFc5gnme1g9gLUWE-4ghaq1FWEG01MIznoxEltgKevoErzotxxDeqBvPdJOuZGLxWsdImjJLjouo9tHDJbPN51X_756Uug0MWO1KJRDKerRLfEky4JP1QIsEN71s70PB4veyL0hw-5phuXOh9r9uX0foPPdVH0eUq3DNEKcmAQl9Bra9f1X97dRu40jCJJyPcN8aIl4diZXsjcei0nBUwj82hoveFzq3-cc=w1280)

The user can define X, Y, initial and final slice, as well as the radius. Note that AMIGO uses values in pixels/voxels, not mm. Transparency and color (RGB) can be adjusted to improve visualization. The color of the line on the table should match the color of the ROI on the image. There is a checkbox labeled "display" at the bottom right, just below the table, that must be checked to enable display. Make sure to select the "ROI" tab within the view module. The data can be exported as a CSV file and also loaded in the case of multiple acquisitions with the same geometry.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2cr6rEWWTsET8zyBURUx6DeQouu3RGmZb3JNoDk9qJSfpXl9eG14bzxXuYJuTEN1ECNCbWuhcnTltIEBOoq21s0oEX7KXedh1PZf11iS3dqZBT6Kda3GEemU1RAypxorcis4w8EH7ipPWJygKnd3RtcnRpmCuCXFxdGGCdnjMno8G0XO_kWi3C8V6LWcNq0lL1egjVNa6CE7QlVvfrLvfzRNiLjdjtu6zD3kWZTf0=w1280)

Use the function "Get Data" or "Get" (select the Data tab) to calculate the mean and standard deviation for values for each ROI. The table also includes the series number (in case of multiple series) and the number of voxels.