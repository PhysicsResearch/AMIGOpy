# General info


![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2F0nUxLHsfPliNRlskEFa1cPMGXrKx8_LQR6FGEYecHJCdkjjPYPCvUDy9WXncKij4WVHLnT1S24UUk7nsFc0rI2c2Kpv7njZYlFWBH2XYvbRghnQ5zh0Us1of0gikk4MHvbFvHLaqcuNt0vW0Lpk5pVmrtFm3Ym6Y37bHntnj0-ezVpFr3gSwgH_0i8w81dMdUYUlcq6eOi9mBNGvSCUAr5mQGxDBqdsfEpoIuxU=w1280)

# General information

AMIGOpy imports contours from the TPS as a cloud of points and converts them into a mask that matches the resolution and size of the reference image. Due to the discrete nature of voxels, this voxelization process may introduce some differences depending on factors such as modeling and approximation. Small structures might appear differently across different systems.

When displaying contours in AMIGOpy, the mask is reconverted into contours and smoothed, which may introduce additional variations. While users should inspect the contours, these differences are generally minimal.

Additionally, AMIGOpy can display the voxelized mask without smoothing, providing an alternative visualization of the data.

Images on the left are from BrachyVision whilst the images on the right are from AMIGOpy.