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

* 📷 **Image Types**: Open, display, and manage standard DICOM and IrIS formats, with future support planned for Nifty and tiff files.
* 🕒 **4DCT**: Dynamic navigation through 4D computed tomography datasets, including 4DCT series comparisons, series splitting, and video rendering.
* 🧪 **Dual Energy CT (DECT)**: Calibration, extraction, and generation of Relative Electron Density (RED), Effective Atomic Number (Zeff), Zeff-vs-I-value, I-value, and Stopping Power Ratio (SPR) using multiple methods.
* 🎯 **Treatment Plans Visualization**: Support for importing, mapping, and overlays of RTDose distributions, RTStruct contours, and RTPlan Brachytherapy datasets (including channel overlays, dwell times, and positions).
* 🔄 **Image Registration**: Tools to handle multi-panel comparisons, image alignment, and registration across multiple datasets.
* ✍️ **Contours & Overlays**: Support for layer overlays (up to 4 layers), selecting cylindrical Regions of Interest (ROIs), and contouring tools.

> [!TIP]
> This is only a subset of the capabilities in AMIGOpy. There are many more features available in the software—we highly encourage you to explore the [Documentation](documentation/index.md) section of this site for detailed explanations and step-by-step user guides!


