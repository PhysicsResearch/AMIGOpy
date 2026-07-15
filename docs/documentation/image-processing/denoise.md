# Denoise


Table of contents

Gaussian Denoise Function

Median Filter Function

Percentile Filter

Minimum Filter

Maximum Filter

Wiener Filter

Fourier Gaussian Filter

Sobel Filter

Gaussian Gradient Magnitude

Gaussian Laplace Filter

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d12qd9b25hvIzIcNIZfTdTQcjW5lFgYguf0h4RU40KepMY_wQ3-odROsfTSmMMXZM0lfFxZ1WiFbFIQWXp945BAi33xKzIS9EUFWDrJKw7y4MRxBXzRD0KFeq0AIj5sgOqJ5keWO0-QD1aCZzDc4eVKJ0bySV_qDKCPziCL2P0d3cvOzEXkpdOVpvzb22JmbqnDt__LCLyq4obVwc7ChjtL7ZKX060RnGmKOeIwVLU=w1280)

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d3i-4QF1OHy2aJ3K6ehXxpNMwy6FVPoQ9rssyi66jCiQpyniom8rUI-q7MiEe6qBt9IB6oIpcwodl3r_e1ICe4takCpBJOPy4A8UX8vM2EtLRnmB1QVyfezZ4q13XDYk8lTvuyJ7rmNtRWXWXBNSCk3clY7byvONYt2yW2yJ3xRhCH8ajFkoqEvQpaEDPAfZbnGDIDHRMfA_76Crm5ssnjySKp0oi9tHs9zWd6tyts=w1280)

### Gaussian Denoise Function

The Gaussian denoise function from SciPy is used to reduce noise in an image by applying a Gaussian filter. This filter works by convolving the image with a Gaussian kernel, which smooths the image and reduces high-frequency noise.

Parameters (SciPy):

- image (ndarray): The input image to be denoised. 2D or 3D. Current image sequence being visualized

- sigma (float or sequence of floats): Standard deviation for Gaussian kernel. The standard deviations of the Gaussian filter are given for each axis as a sequence, or as a single number, in which case it is equal for all axes.

- output (ndarray or None, optional): The array in which to place the output, or None to return a new array.

- mode (str, optional): The mode parameter determines how the array borders are handled. Default is 'reflect', but other options include 'constant', 'nearest', 'mirror', and 'wrap'.

- cval (scalar, optional):  Value to fill past edges of input if mode is 'constant'. Default is 0.0.

- truncate (float, optional): Truncate the filter at this many standard deviations. Default is 4.0.

Kernel Size Definition:

The size of the Gaussian kernel is determined by the sigma parameter and the truncate parameter.

For a detailed description of the Gaussian denoise function, please refer to the SciPy documentation.

Parameters (AMIGOPy):

Axial, Sagittal or Coronal: Images are processed according to this direction (2D mode)

2D or 3D: Process individual slices or the complete sequence at once

### Median Filter Function

The median filter function from SciPy is used to reduce noise in an image by replacing each pixel's value with the median value of the pixels in its neighborhood. This type of filter is effective at preserving edges while removing noise.

Parameters (SciPy):

- image (ndarray): The input image to be denoised. 2D or 3D. The input image to be denoised. 2D or 3D. Current image sequence being visualized.

- size (int or sequence of ints, optional): The size of the filter. If size is a sequence, it represents the size of the filter along each axis. If size is a single integer, the same size is used for all axes.

- footprint (array, optional): A boolean array that specifies which elements within the size block should be considered in the calculation of the median value. size and footprint cannot both be given.  Not used in this implementation !

- output (ndarray or None, optional): The array in which to place the output, or None to return a new array.

- mode (str, optional):The mode parameter determines how the array borders are handled. Default is 'reflect', but other options include 'constant', 'nearest', 'mirror', and 'wrap'.

- cval (scalar, optional): Value to fill past edges of input if mode is 'constant'. Default is 0.0.

- origin (int or sequence of ints, optional): Controls the placement of the filter. Default is 0.

Kernel Size Definition:

The size of the median filter's kernel is defined by the size parameter. If a single integer is provided, the filter size will be the same along all axes. If a sequence of integers is provided, each integer represents the size of the filter along the corresponding axis.

For a detailed description of the median filter function, please refer to the SciPy documentation.

### Percentile Filter

The percentile filter in SciPy replaces each pixel's value with the specified percentile value from the pixel's neighbourhood. This method is useful for highlighting specific intensity ranges within the image.

Parameters (SciPy):

- input (array_like): The input image to be denoised. 2D or 3D. The input image to be denoised. 2D or 3D. Current image sequence being visualized.

- percentile (float): The percentile to compute (range 0-100).

- size (int or sequence of ints): The shape that defines the neighborhood.

- footprint (array, optional): A boolean array specifying the shape of the neighborhood. Not used in this implementation !

- output (ndarray or None, optional): The array to store the output, or None to return a new array.

- mode (str, optional): How to handle array borders. Options include 'reflect', 'constant', 'nearest', 'mirror', and 'wrap'.

- cval (scalar, optional): Value for borders if mode is 'constant'.

- origin (int or sequence of ints, optional): Controls the placement of the filter.

Kernel Size Definition:

The size of the median filter's kernel is defined by the size parameter. If a single integer is provided, the filter size will be the same along all axes. If a sequence of integers is provided, each integer represents the size of the filter along the corresponding axis.

For a detailed description of the median filter function, please refer to the SciPy documentation.

Parameters (AMIGOPy):

Axial, Sagittal or Coronal: Images are processed according to this direction (2D mode)

2D or 3D: Process individual slices or the complete sequence at once

### Minimum Filter

The minimum filter in SciPy replaces each pixel's value with the minimum value within the pixel's neighbourhood. This method is useful for removing small bright artefacts and for creating a smoothing effect.

Parameters(SciPy):

- input (array_like): The input image to be denoised. 2D or 3D. The input image to be denoised. 2D or 3D. Current image sequence being visualized.

- size (int or sequence of ints): The shape that defines the neighbourhood.

- footprint (array, optional): A boolean array specifying the shape of the neighbourhood. Not used in this implementation!

- output (ndarray or None, optional): The array to store the output, or None to return a new array.

- mode (str, optional): How to handle array borders. Options include 'reflect', 'constant', 'nearest', 'mirror', and 'wrap'.

- cval (scalar, optional): Value for borders if mode is 'constant'.

- origin (int or sequence of ints, optional): Controls the placement of the filter.

Kernel Size Definition:

The size of the median filter's kernel is defined by the size parameter. If a single integer is provided, the filter size will be the same along all axes. If a sequence of integers is provided, each integer represents the size of the filter along the corresponding axis.

For a detailed description of the median filter function, please refer to the SciPy documentation.

Parameters (AMIGOPy):

Axial, Sagittal or Coronal: Images are processed according to this direction (2D mode)

2D or 3D: Process individual slices or the complete sequence at once

### Maximum Filter

The maximum filter in SciPy replaces each pixel's value with the maximum value within the pixel's neighbourhood. This method is useful for enhancing bright features and suppressing small dark artefacts.

Parameters(SciPy):

- input (array_like): The input image to be denoised. 2D or 3D. The input image to be denoised. 2D or 3D. Current image sequence being visualized.

- size (int or sequence of ints): The shape that defines the neighborhood.

- footprint (array, optional): A boolean array specifying the shape of the neighborhood. Not used in this implementation !

- output (ndarray or None, optional): The array to store the output, or None to return a new array.

- mode (str, optional): How to handle array borders. Options include 'reflect', 'constant', 'nearest', 'mirror', and 'wrap'.

- cval (scalar, optional): Value for borders if mode is 'constant'.

- origin (int or sequence of ints, optional): Controls the placement of the filter.

Kernel Size Definition:

The size of the median filter's kernel is defined by the size parameter. If a single integer is provided, the filter size will be the same along all axes. If a sequence of integers is provided, each integer represents the size of the filter along the corresponding axis.

For a detailed description of the median filter function, please refer to the SciPy documentation.

Parameters (AMIGOPy):

Axial, Sagittal or Coronal: Images are processed according to this direction (2D mode)

2D or 3D: Process individual slices or the complete sequence at once

### Wiener Filter

The Wiener filter in SciPy is used for signal and image denoising based on statistical estimation techniques. It aims to minimize the mean square error between the filtered image and the original image. This filter is particularly effective for images corrupted by Gaussian noise.

Parameters (SciPy):

- image (array_like): The input image to be denoised. 2D or 3D. The input image to be denoised. 2D or 3D. Current image sequence being visualized.

- mysize (int or tuple of ints, optional): The size of the Wiener filter window. It can be a single integer or a tuple representing the window size along each axis. If not specified, the filter size is automatically determined.

- noise (float, optional): The noise power to use for the Wiener filter. If not specified, the noise power is estimated from the input image.

For a detailed description of the median filter function, please refer to the SciPy documentation.

Parameters (AMIGOPy):

Axial, Sagittal or Coronal: Images are processed according to this direction (2D mode)

2D or 3D: Process individual slices or the complete sequence at once

### Fourier Gaussian Filter

The scipy.ndimage.fourier_gaussian function applies a Gaussian filter in the frequency domain. This method is useful for smoothing images or signals by reducing high-frequency noise, which is particularly effective for data that benefits from frequency domain processing.

Parameters (SciPy):

sigma (float or sequence of floats): The standard deviation of the Gaussian filter. If a single float is provided, the same standard deviation is used for all axes. If a sequence is provided, it specifies the standard deviation for each axis.

For a detailed description of the median filter function, please refer to the SciPy documentation.

Parameters (AMIGOPy):

Axial, Sagittal or Coronal: Images are processed according to this direction (2D mode)

2D or 3D: Process individual slices or the complete sequence at once

### Sobel Filter

The Sobel filter is used to detect edges in an image by calculating the gradient magnitude. It highlights regions of high spatial frequency which correspond to edges.

Parameters(SciPy):

- image (array_like): The input image to be denoised. 2D or 3D. The input image to be denoised. 2D or 3D. Current image sequence being visualized.

- axis (int or sequence of ints): The axis along which to compute the Sobel filter. If axis is a sequence, the filter is applied sequentially along each axis.

- mode (str, optional): How to handle borders ('reflect', 'constant', 'nearest', 'mirror', 'wrap').

- cval (scalar, optional): Value for borders if mode is 'constant'.

For a detailed description of the median filter function, please refer to the SciPy documentation.

Parameters (AMIGOPy):

Axial, Sagittal or Coronal: Images are processed according to this direction (2D mode)

2D or 3D: Process individual slices or the complete sequence at once

### Gaussian Gradient Magnitude

The scipy.ndimage.gaussian_gradient_magnitude function computes the gradient magnitude using Gaussian derivatives. It is useful for edge detection with noise reduction.

Parameters(SciPy):

- image (array_like): The input image to be denoised. 2D or 3D. The input image to be denoised. 2D or 3D. Current image sequence being visualized.

- sigma (float or sequence of floats): The standard deviation for Gaussian kernel.

For a detailed description of the median filter function, please refer to the SciPy documentation.

Parameters (AMIGOPy):

Axial, Sagittal or Coronal: Images are processed according to this direction (2D mode)

2D or 3D: Process individual slices or the complete sequence at once

### Gaussian Laplace Filter

The scipy.ndimage.gaussian_laplace function applies a Gaussian filter followed by the Laplacian, which is useful for edge detection and blob detection.

Parameters:

- image (array_like): The input image to be denoised. 2D or 3D. The input image to be denoised. 2D or 3D. Current image sequence being visualized.

- sigma (float or sequence of floats): The standard deviation for Gaussian kernel.

For a detailed description of the median filter function, please refer to the SciPy documentation.

Parameters (AMIGOPy):

Axial, Sagittal or Coronal: Images are processed according to this direction (2D mode)

2D or 3D: Process individual slices or the complete sequence at once

Rolling Ball Filter

The skimage.restoration.rolling_ball function is used to subtract a background from an image using a rolling ball algorithm. This is particularly useful for removing smooth continuous backgrounds.

Parameters:

- image (ndarray): The input image.

- radius (float): The radius of the ball. Larger values will remove larger features.

- kernel (array, optional): A precomputed ball kernel.

4. Prewitt Filter

The skimage.filters.prewitt function detects edges by computing the Prewitt filter, which calculates the gradient of the image intensity.

Parameters:

- image (ndarray): The input image.

- mask (ndarray, optional): An optional mask to apply to the image.

5. Bilateral Filter

The skimage.restoration.denoise_bilateral function reduces noise while preserving edges by applying a bilateral filter.

Parameters:

- image (ndarray): The input image.

- sigma_color (float): Filter sigma in the color space.

- sigma_spatial (float): Filter sigma in the coordinate space.

- bins (int, optional): Number of discrete values for Gaussian weights.

- mode (str, optional): How to handle borders.

Key Features:

- Reduces noise while preserving edges.

- Effective for color images and grayscale images.

6. Non-Local Means Denoising

The skimage.restoration.denoise_nl_means function applies non-local means denoising, which averages pixel values based on similarity, rather than proximity.

Parameters:

- image (ndarray): The input image.

- h (float): The cut-off distance.

- fast_mode (bool, optional): Whether to use a fast approximation.

- patch_size (int, optional): The size of patches used for comparison.

- patch_distance (int, optional): The maximum distance for patch comparison.

- multichannel (bool, optional): Whether the image has multiple channels.

2. Wavelet Denoising

The skimage.restoration.denoise_wavelet function applies denoising using wavelet transforms, which is effective for reducing noise while preserving the structure of the image.

Parameters:

- image (ndarray): The input image.

- sigma (float or list, optional): The standard deviation of the noise.

- wavelet (str, optional): The type of wavelet to use.

- mode (str, optional): The signal extension mode.

- multichannel (bool, optional): Whether the image is a multichannel (color) image.