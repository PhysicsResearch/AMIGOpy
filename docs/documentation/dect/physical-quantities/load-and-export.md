# Load and export


### Loading and Exporting Material Composition

Loading from CSV File

1. Click the `Load` button in the `Material Info` subtab.

2. Browse and select the desired CSV file.

3. Confirm the upload. The table will populate with material data from the CSV.

Exporting to CSV File

1. After all the materials and corresponding data are entered or calculated, click on the `Export` button.

2. The data from the table will be saved in a CSV file for future use, ensuring a smooth and efficient workflow for subsequent analyses.

CSV File Structure

- Lines starting with `#` are comments.

-The first non-comment line is used as the title of the table.

- Each subsequent line defines a material, following the sequence: `"Material Name", "Atomic Number", "Mass Fraction"`, with optional elements: `'Den', 'RED', 'Zeff', 'I', 'SPR','HUlow','HUhigh'`.

Optional Terms Explanation:

- **Den**: Mass density (g/cm³)

- **RED**: Relative Electron Density

- **Zeff**: Effective Atomic Number

- **I**: Mean Excitation Energy

- **SPR**: Stopping Power Ratio

- **HUlow**: HU value for the acquisition performed with the lowest kV.

- **HUhigh**: HU value from the acquisition performed with the highest kV.