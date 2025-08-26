# Installation

This page explains how to install **AMIGO** using two different methods:

* **Option 1:** Download the compiled version (**Windows only**) *(recommended for most users)*
* **Option 2:** Install from source using Anaconda *(recommended for developers)*

Target Python version: **≥ 3.11**

---

## Option 1 — Download Compiled Version (Windows Only)

This is the easiest way to install and run **AMIGO** without setting up Python or dependencies manually.

1. Go to the [AMIGO Releases](https://github.com/PhysicsResearch/AMIGOpy/releases).
2. Download the latest `.exe` installer.
3. Run the installer and follow the on-screen instructions.
4. Launch **AMIGO** from the Start Menu or Desktop shortcut.

> **Note:** The compiled version may not always include the very latest changes. For development, use **Option 2**.

---

## Option 2 — Install from Source (Recommended for Developers)

This option is ideal if you plan to contribute, debug, or modify AMIGO. We recommend using **Anaconda** to create a dedicated virtual environment, ensuring all dependencies are correctly managed and isolated.

### 2.1 — Install Anaconda

Download and install **Anaconda** from the official website:

[https://www.anaconda.com/download](https://www.anaconda.com/download)

> **Tip:** Anaconda simplifies package management and ensures a reproducible setup.

### 2.2 — Install Git (Optional)

We recommend installing **Git** so you can clone the repository instead of downloading it manually.

> **Important:** Run the following commands **in an Anaconda Prompt** (Windows) or terminal (macOS/Linux):

```bash
conda install git
```

* If you don’t want to use Git, you can [download the source code manually](https://github.com/PhysicsResearch/AMIGOpy) as a `.zip` file.
* You **don’t need to create a specific folder manually**. Git will automatically create a folder called `AMIGOpy` when cloning.

### 2.3 — Clone the Repository (Recommended)

```bash
git clone https://github.com/PhysicsResearch/AMIGOpy.git
cd AMIGOpy
```

### 2.4 — Or Download the Source Manually

1. Go to the [AMIGO GitHub repository](https://github.com/PhysicsResearch/AMIGOpy).
2. Click **Code → Download ZIP**.
3. Extract the archive to a desired folder.

### 2.5 — Create and Activate a Conda Environment

Use the provided **`amigo.yml`** file to ensure correct dependencies:

```bash
conda env create -f amigo.yml
conda activate amigo
```

### 2.6 — Run AMIGO

```bash
python Launch_ImGUI.py
```

---

## Troubleshooting


* **Dependency conflicts** → Remove your environment and recreate it using:

  ```bash
  conda env remove -n amigo
  conda env create -f amigo.yml
  ```
* **Issues running compiled version** → Check the [GitHub Issues](https://github.com/PhysicsResearch/AMIGOpy/issues).

---

For advanced usage and development setup, see the [Developer Guide](Developer_Guide.md).
