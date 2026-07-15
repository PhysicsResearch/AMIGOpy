# Image processing


AMIGOpy offers a comprehensive suite of tools for data processing, including filters for denoising, normalization functions, format conversion, cropping, resizing, and more. Most of these filters leverage established packages like SciPy, scikit-image, and PyWavelets. As a result, our documentation is concise and refers to the original sources for detailed information.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0k-X69AoruVlgdx0zZMpR7_Bmqu-73aoUBZnW_NvLXzjPmGh7t5qV3GDD8QEKIgctfkVgf86neoeu9dLkQf0ign_ARXnEqTU9_W3j3MTSBIFn6obYBkKVC0IqhLaowSAPtX49v3aLazCKyMSSqEcB80YaL3LNmfUdNWCF_Lc-wzBTBJM48Bg7ppvgo9AJblFrCB9x9Y1ST6AOYNlHEekvGgUoByGg-kms-XNmm=w1280)


In the View module, select the "Processing" tab. You'll find the available filters in the dropdown menu. When you select a filter, the input parameters will appear. For detailed explanations of the parameters, refer to the sub-page for each function.

To apply a filter, press "Run." Use "Undo" to revert to the original image. Note that once a filter is applied, the original image is modified, and only the most recent operation can be undone.

The operation is applied to the image currently selected in the datatree. Switching image set before pressing "Undo" may cause unexpected behavior.