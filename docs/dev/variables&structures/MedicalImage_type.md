# Medical Image Structure in AMIGOpy

AMIGOpy supports multiple medical image formats and stores both **images** and **metadata** in a unified format.  
Regardless of the original file type (**DICOM**, **NIfTI**, **MHA**, **NRRD**, etc.), **all formats are automatically converted** into this structure to ensure **consistency** across the software to ensure consistent behavior across modules (loading, visualization, segmentation, Monte Carlo simulation, and export).


---

## ✅ Supported & Planned Formats

**Core (supported / priority):**
- 📄 **DICOM** (`.dcm`) — clinical standard, includes RTDose/RTStruct/RTPlan
- 🧩 **NIfTI** (`.nii`, `.nii.gz`) — compact, common in AI and research


**Planned:**
- 🧪 **MHA / MHD** (`.mha`, `.mhd` + raw) — native to ITK/ANTs pipelines
- 🧱 **NRRD / NRD** (`.nrrd`, `.nrd`) — efficient for volumetric data and masks
- 🗂 **HDF5** (`.h5`) — bundles volumes + masks + metadata for AI workflows
- ⚡ **NPZ / NPY** (`.npz`, `.npy`) — fast NumPy storage for preprocessed data


> 🔁 **All input formats are normalized** into the same internal representation described below.

---

## 📌 Data Hierarchy

```python title="Accessing a Series in AMIGOpy"
self.medical_image[patientID][studyID][modality][series_index]
```

| **Level**         | **Type** | **Description** |
|--------------------|---------|------------------|
| **`patientID`**    | `dict`  | Dictionary containing all studies for a given patient |
| **`studyID`**      | `dict`  | Dictionary containing modalities available within the study |
| **`modality`**     | `dict`  | Dictionary containing imaging modalities *(e.g. CT, MR, RTDOSE)* |
| **`series_index`** | `int`   | Index into a **list of series dictionaries** under this modality |

---

## 📦 Series Index vs Series Dict

- **`series_index`** → integer index into the **list of series dictionaries**  
- Each **series_dict** represents one imaging series and contains:

### **1. Metadata**
   - Voxel spacing (`PixelSpacing`)
   - Slice thickness
   - Image orientation
   - Modality type
   - Study and series descriptions
   - Original file path and format-specific tags
   - ...

### **2. Voxel Data**
   - **`3DMatrix`** → a NumPy 3D array storing the full volumetric dataset

### **3. Series Add-ons**
   - **`structures`** → ROI masks and contours - [Structures within image series](Structures.md) 
   - **`density_maps`** → HU → density conversions for dose calculation
   - **`material_maps`** → tissue/material assignments for Monte Carlo simulation

> 💡 For implementation details, see the dedicated sections:  
> **[Structures](Structures.md)** · **[Density & Material Maps](DensityMaterialMaps.md)** · **[Export](Export.md)**

---

## 🧭 Coordinate System & Orientation

To guarantee **compatibility** across modules:

### **1. Normalize orientation at load time**  
Reorient volume data into a **single, agreed coordinate convention**  
(e.g. patient-based **LPS/RAS** or a fixed axis order).

### **2. Standardize voxel axis order**  
Choose a canonical **NumPy layout**, for example:



## 🗂️ Series Metadata Overview

The internal structure is a nested mapping down to a list of series:

```python title="Build_series_dict example"
    """
    Build the internal AMIGOpy series dictionary.

    Parameters
    ----------
    series_number : str | int
    spacing : tuple[float, float, float]   # (dx, dy, dz)
    origin  : tuple[float, float, float]   # DICOM-style origin
    size    : tuple[int, int, int]         # (nx, ny, nz)
    vol     : np.ndarray                   # 3D numpy array (standardized orientation)
    path    : str
    nifti_meta : dict | None
    """
    return {
        'SeriesNumber': series_number,
        'metadata': {
            'PixelSpacing': spacing[0:2],
            'SliceThickness': spacing[2] if len(spacing) >= 3 else 1.0,
            'ImagePositionPatient': origin,
            'ImageOrientationPatient': "N/A",
            'RescaleSlope': "N/A",
            'RescaleIntercept': "N/A",
            'WindowWidth': "N/A",
            'WindowCenter': "N/A",
            'SeriesDescription': series_number,
            'StudyDescription': '',
            'ImageComments': '',
            'DoseGridScaling': "N/A",
            'AcquisitionNumber': "N/A",
            'Modality': "Medical",
            'LUTLabel': "N/A",
            'LUTExplanation': "N/A",
            'size': size,
            'DataType': 'Nifti',
            'DCM_Info': None,
            'Nifti_info': nifti_meta,
            'OriginalFilePath': path,
        },
        'images': {},
        'ImagePositionPatients': [],
        'SliceImageComments': {},
        '3DMatrix': vol,
        'AM_name': None,
        'US_name': None,
    }
```