# DICOM


A function is called Data_tree_general.py is called every time the user click on a item in the data tree. This functions can be useful to underdant where the data is stored.

### Data Organization and Storage Structure

The software organizes and stores data following a hierarchical structure modeled after the DICOM standard, facilitating structured management of medical imaging data. The hierarchy is as follows:

Patient ID → Study → Modality and Series

- Patient Level: Data begins with a unique Patient ID, serving as the top-level key to segregate data belonging to individual patients.

- Study Level: Each patient contains one or multiple Studies identified by study keys. Each study represents a distinct imaging session or clinical evaluation event.

- Modality and Series Level: Under each study, data is organized by Modality (e.g., CT, MR, RTSTRUCT, RTPLAN, etc.). Each modality further contains one or multiple Series, uniquely identified either by dictionary keys or numerical indices within a list, depending on whether multiple identical series keys may exist.

- Dictionary keys are used for straightforward, unique access.

- List indices facilitate handling scenarios with repeated or duplicated series identifiers, enabling explicit access.

Within each Series, the following data elements are stored:

- Full DICOM Header: The original DICOM metadata is preserved intact, ensuring complete data provenance.

- Extracted Essential Fields: Frequently used fields such as Pixel Spacing, Image Position, and Image Date are extracted and duplicated into dedicated fields for efficient, simplified access throughout the software.

- Contour Data: If applicable contours delineating regions of interest or anatomical structures (binary masks and polygons) are stored at the series level alongside their associated image data. Contour data can be created withing AMIGOpy or importated (RTStructures are stored own its own, but masks created using RTSTRUCTS are stored with the corresponding images)

Example data structure for each series

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d2t9wHZO2wvkiserojdMfH9z1BMu7XtMJ-p0hrBbweh3hJIV8uAKiUCfWiICfJ-zXaIk2xe1NyFlA0v1RzC11B25_NX5BISRV4xSDcvuTV7vCXoVSxkTR8kQc2qgMavChpS47_RVykxlCe8tjhC1JeoB_PdlwX-K2nLNWL4tGtxKzmviNnNorVZx5ANU9TSZNLHcpHmobJw89ZrHPDIrHosMpODs-vWwxeAQR_TEHM=w1280)

Example on how acess the data

the keys: self.patientID - self.studyID - self.modality and self.series_index are defined whe the user click on the data tree.

self.series_index is an index (number) while the others are data keys.

![Image](https://sites.google.com/sitesv-images-rt/ACHe0d0qNAppQeFFZcGEgyAEmwCPtfUiyijjmaLZCV6samlVb7_4yXuDn5_OxTBchtH6_6DnH9hMrgQH41JEZ3Wws7iDX-r5eocSgKxPZBVdVJXPzDMmTj6lLQsE3mNsGkhhcn0dxIxHADBU3ZNdG0_HxNq58awjjrB7F-7aRUtebppi5eUakX-a5w2MJqbVkHWRaFxGdR28mlE1QrLs_5Q-OoDLKyXU8eBQmdw2YglhjVE=w1280)