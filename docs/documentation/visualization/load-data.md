# Load Data


Current supported formats: DICOM and IrIS

Near future: Nifty, tiff and other forms related to MC (e.g. EGSphantfile)

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2tPPNo1Kwk8bgoTAVmy_-Pfjob5G54DYX3-n8qPxtSFuujuiRqXgV5AvdEbgTbQRmTjGXTH078D-gYFM5qb4zGP9imWKBptsefXTlk0tNVqsgfVKmvq3EK5UaasOo09R9bRRk-zAUgtEGPY40lEEONJrL5Z6yJVOtJ3OqY_hcOlSmuGlXcu_wZ1gWIFsz2KXpdCGYZ2uP3ZFKUIBqZNRidqvM8QtE5uhYnvGsS8ik=w1280)

File >> OPEN >> Image type

or use the shortcut:

e.g. Ctrl + D for DICOM images

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d3nR2cjVv2G8B_xI_T40nKm4UNuKZQJd2TcTyveMFUTUSqQvqorUC8AnXvz1pkQ5h8Iksr9ty1cToPM78oEYa3IqtQY2fcRuLKZBrNNJKa9dicEV4DO-kPScAyVxuR2OFD-kSbXb8mbE0CbUNn8U5EV8AfY3mmXpr0xfN50MTfs6pVDuNn7jOQfp_8Z8tMlSI9rPGXLUrYqgQ0Oycfzgn-EwDAokRIz7Wp5zDyS=w1280)

Select a FOLDER  .... Note that AMIGOpy will scan all subfolders and try to load all the files. In the example above it would open CT images, RTPlans, RTStructs and RTDoses.

! With can easily fill in the memory and crashes depending on your hardware and the number of files in the folder!  Check the content of the folder before loading.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0EZYP9fUFXnWaHg2ZwKZ1n2Oj-BnF_sPFUdHNGuXYjw8D620-fuNTjjykJZmxjpFCWlNsEWlyV7EVJ0JWH8HmQJ8V2fDBHnnqYdpeg02dEl7frvvF9SfsegDBB3ChILWDlRy7bcyEhFk0jgmuv_sQ0Ec-5uLdjZWhd3f3kvohM4pQ3JbVZiP9EjqMMqBAEiBRgpLObK3OmW63rNZP5KkPO9SCCsmA-9clYeKLyizI=w1280)

# Data tree

Loaded data will appear in the lateral menu grouped according to their type (e.g. DICOM) and then subdivided into categories:

For DICOM

- PatientID

- Study

- Modality

- Series

The data should be organized before loading. For example, if you would like to load multiple patients, first place them into the same folder (where each patient can be placed in its own subfolder) and select the main folder when loading the data with AMIGOpy.

Remarks

- Each folder should contain one file type and only one data type will be loaded.