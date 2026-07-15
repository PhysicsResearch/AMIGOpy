# Physical quantities


## Material Info Subtab

The `Material Info` subtab within the `DECT` tab is devoted to managing and entering material compositions. This tool allows users to specify materials by their atomic numbers, mass fractions, and other relevant parameters for a precise and detailed quantitative information extraction process.

### Creating and Managing Material Table

Resetting the Table

1. Navigate to the `Material Info` subtab under the `DECT` tab.

2. Click the `Reset` button to clear any existing data, presenting a blank table for material input.

### Adding Material Composition

1. Locate the input fields at the bottom right of the table.

2. Enter the material name, the atomic number or symbol of the element, and the mass fraction in the respective fields.

3. Press `Enter` or click the `Add` button to insert the material into the table.

### Calculating RED, Z_eff, I, and SPR

Upon entering the elemental composition:

1. Click the `Calculate` button.

2. The `RED`, `Z_eff`, `I`, and `SPR` values will be computed based on the entered elemental composition and displayed in the corresponding columns of the table.

Note: If the checkbox below the table (selected by default) is not selected, the code will not calculate the specified parameter, allowing for manual entries. For example, if the user defines the I value manually and unchecks the I value box, this value will be used to calculate SPR. On the other hand, if the box is selected, the user's I value will be overwritten and not used in the SPR calculation.

Note: `HU` and `Den` values should be manually added by the user as they are specific to the acquisition and material physical properties, and are not calculated by the tool.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d1Xz0siENeQ4NqCLnHYvFU8UA-H8nTLE7m9EOE9YLsEEuJMhw1GAklKcmoRGa89YF_yIVZBqr2xQJEegmJ0OLnVN45iznZZB5gZP6zo5UVeumM48zK3p9rfOfynePHKfW-wDDVanTX7M4pM1OoobpV6s0KOwkHRueHeVMk5PNuce7azqfOXqyAH1s7g_I0CRguiA8ZMHXxFrN0Wo1cSwNcYY48PBPMPs-n2o2C2gNE=w1280)

## Getting HU values from images

To extract HU (Hounsfield Unit) values from images, the user needs to define Regions of Interest (ROIs). If your table contains 10 materials, then you should create 10 corresponding ROIs. Note that the values will be assigned in the same sequence, meaning the value of the 1st ROI will be assigned to the first material (1st row), the second ROI to the second material (2nd row), and so on.

Important: Regardless of the image displayed in the View module, the values will be extracted from the image series listed in the dropdown menu next to HU_low and HU_high. Ensure you select the correct images. Once the correct image sequences are selected, press "Get HU Low and High" to populate the table. These values will be used in the next steps of the DECT calibration. Note that values can also be filled in manually if needed.