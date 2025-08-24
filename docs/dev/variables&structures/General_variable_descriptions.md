# AMIGOpy Variables and File Categories

AMIGOpy supports multiple file extensions and automatically groups them into **categories**.  
This approach ensures that the particularities of each supported format are **abstracted** into unified categories, allowing the software to behave more consistently and predictably.

The two main categories currently supported are:

- [Medical Images](#medical-images)
- [3D Objects](#3d-objects)

Each category is briefly described below with more details about python structure in category-specific pages.

---

## **Medical Images**

Medical imaging data is a central part of AMIGOpy's workflow.  
This category includes both **DICOM** and **NIfTI** formats, automatically normalized to a **category-based structure** for consistent behavior across the software.

### Supported Extensions

| Format     | Extensions         | Description                                                                |
|-----------|--------------------|----------------------------------------------------------------------------|
| DICOM     | `.dcm`             | Medical images and metadata in DICOM standard format.                      |
| RT Plan   | `.dcm`             | DICOM radiotherapy plans, stored under the medical image category.         |
| RT Struct | `.dcm`             | DICOM structure sets, containing contour and region information.           |
| RT Dose   | `.dcm`             | DICOM radiotherapy dose distributions.                                     |
| NIfTI     | `.nii`, `.nii.gz`  | Neuroimaging format widely used for research; fully integrated in AMIGOpy. |

### Internal Representation

Internally, AMIGOpy converts all formats into a **common structure** stored within:

```python
self.medical_images
```


## **3D Objects**

AMIGOpy also supports loading **3D object files** used in **simulations**, **phantom design**, and **visualizations**.  
These files are grouped under the **`3d_objects`** category, ensuring consistent handling of geometry and surface data.

---

## **Supported Extensions**

| Format | Extensions | Description                                                      |
|--------|-----------|------------------------------------------------------------------|
| STL    | `.stl`    | Widely used for 3D printing and phantom design.                  |
| OBJ    | `.obj`    | Standard geometry and surface definition files for visualization. |
| 3MF    | `.3mf`    | Modern 3D format supporting colors, textures, and metadata.      |

---

## **Internal Representation**

All loaded 3D object data is stored within the variable:

```python
self.objects_3d
```
