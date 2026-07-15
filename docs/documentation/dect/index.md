# DECT


## DECT Tab

The `DECT` (Dual-Energy Computed Tomography) tab in the GUI is tailored to handle and process DECT data. By using two energy spectra DECT effectively distinguishes materials of similar atomic numbers, offering enhanced contrast and superior material identification. This separation and precise material identification is especially crucial in medical imaging, where subtle differences can hold significant diagnostic information.

### P

seudo-monoenergetic images (PMI - Not implemented yet)

....

### Quantitative Information Extraction

- Relative Electron Density (RED) Offers insight into the electron density of materials in the imaged object.

- Effective Atomic Number (Z_eff): Specifies the effective proton count in the atomic nuclei within the imaged object.

- Mean Excitation Energy (I): Denotes the average energy necessary for exciting atoms in the image.

- Stopping Power Ratio (SPR): Indicates the material's capacity to halt or decelerate incoming particles.

AMIGOpy implemented methods available in the literature:

Nora Hünemohr et al 2014 Phys. Med. Biol. 59 83

DOI 10.1088/0031-9155/59/1/83

Masatoshi Saito, Shota Sagara 2017 Med. Phys 44 8

DOI https://doi.org/10.1002/mp.12386

The methods won't be described here as this page focuses on the steps to perform the calibration using AMIGOpy.  Note that the process involves several steps depending directly on user input. Therefore, understanding the method is essential (Read the papers !)

## DECT 

Calibration

Follow the steps in the correct order:

- - Load Low and High kV (or keV in the case of PMIs) into AMIGOpy. Note that if HU values are known by the user or saved as CSV files they can be loaded into AMIGOpy without requiring CT images (see step 4).

- Create regions of interest ROIs so AMIGOpy can extract average HU values.

- Load or insert the material compositions so theoretical values (reference) based on the elemental composition can be calculated. Note that elemental composition, as well as calculated properties, can beexported as CSV and loaded in the future.

- Fill in the HU values into the material table (item 3) or extract them from images using ROIs (described here)

If the steps above were performed properly the material info table will show RED, Zeff, I-value, SPR, and HU (low and High) for all the materials. These values are mandatory to perform the next steps as they are used as a reference for the calibration.

- - Perform the RED fit

- Perform the Zeff fit

- Perform Zeff vs I-value fit

- Calculate I-values

- Calculate SPR

- Create RED, Zeff, I-value, and SPR iamges