# AMIGOpy 

## Welcome to the AMIGOpy Documentation 

This site documents the **AMIGOpy** software, including its main functionalities, coding standards, and development roadmap.

> **Note for developers**   
> This documentation includes **in-depth details** about the source code, architecture, and contribution guidelines.  
> **Regular users** should focus on the pages describing the **main features**, **user guides**, and **roadmap** — no need to dive into implementation details unless you're contributing.

---

##  Overview

**AMIGOpy** is a medical imaging toolkit designed to support **radiotherapy research** and **clinical workflows**.

It provides tools for:

- ⚡ **Radiotherapy workflows** — treatment planning, data handling, and advanced analysis
- 🧩 **Segmentation & Autocontouring** — integrated with AI-based APIs and customizable pipelines
- 🎲 **Monte Carlo simulation** — dose calculation, modeling, and validation for research and clinical applications
- 🌐 **3D / 4D Rendering** — high-quality visualization for volumetric and time-resolved imaging data
- 🧠 **Research & Development** — flexible tools for rapid prototyping, innovation, and integration with external platforms

---

> **AMIGOpy** is designed to bring together **automation**, **research tools**, and **clinical support** into a single, extensible platform.  
> It not only provides built-in functionalities but also **integrates and expands upon community-driven developments**, creating a powerful and collaborative software ecosystem.


---

##  Documentation Structure

### **1. Installation**
See [Installation](installation.md)  
Step-by-step instructions for installing both the **compiled version** and the **developer setup**.

---

### **2. Coding & Documentation Guidelines**
See [Software Documentation Guidelines](DevGuidelines/Software-documentation-guidelines.md)  
Clear standards for writing **docstrings**, using **type hints**, and maintaining **consistent code style**.  
These rules are **mandatory** for all contributors.

- 📝 **Docstring rules:** [Docstring Guidelines](DevGuidelines/Docstring.md)
- 🔠 **Type hints:** [Typing Guidelines](DevGuidelines/Typing.md)

---

### **3. Software Variables & Developer Notes**
See [General Variable Descriptions](dev/variables&structures/General_variable_descriptions.md)  
An overview of **variable naming conventions**, **data structures**, and **core architecture**.

---

## Key Features

AMIGOpy contains a wide array of tools and resources for medical physics and imaging research:

* 📷 **Supported File Formats**:
    * **Medical Images**: Import, display, and manage standard DICOM, NIfTI (`.nii`/`.nii.gz`), MetaImage (`.mha`/`.mhd`), NumPy arrays (`.npy`), TIFF stacks, and IrIS formats.
    * **3D Printing & CAD**: Import and visualize 3D meshes and CAD formats including STL, OBJ, 3MF, and STEP/STP.
* 🕒 **4DCT Analysis**: Dynamic navigation through 4D computed tomography datasets, including 4DCT series comparisons, series splitting, and temporal video loop rendering.
* 🧪 **Dual Energy CT (DECT)**: Comprehensive calibration, extraction, and generation of Relative Electron Density (RED), Effective Atomic Number (Zeff), Zeff-vs-I-value, I-value, and Stopping Power Ratio (SPR) using multiple conversion methods.
* 🎯 **Treatment Plan Visualization**: Full integration with radiotherapy DICOM (RT-DICOM) standards to import and overlay 3D RTDose distributions, RTStruct contours, and RTPlan Brachytherapy sources (including channel overlays, dwell times, and source positions).
* 🔄 **Image Registration**: Support for both automatic image registration (intensity-based mutual registration) and manual rigid/translational registration for precise multi-scan alignment.
* ✍️ **Contours & Overlays**: Advanced multi-layer overlays (up to 4 concurrent layers), interactive cylindrical ROI selection, contour generation, and dose-volume histogram (DVH) statistics.
* 🛠️ **3D Printing & Phantom Design**: Tissue-equivalent phantom design tools, including matching 3D printing filaments with specific tissue RED/Zeff values and G-code file parsing/splitting.

> [!TIP]
> This is only a subset of the capabilities in AMIGOpy. There are many more features available in the software—we highly encourage you to explore the [Documentation](documentation/index.md) section of this site for detailed explanations and step-by-step user guides!


