# Docstring & Type Hint Guidelines

This page defines the conventions for writing **docstrings** (see [Docstring Guidelines](Docstring.md)) and using **type hints** (see [Typing Guidelines](Typing.md)) in this project.
We follow **NumPy-style docstrings** and use **Python type hints** as the single source of truth for parameter and return types. Target runtime: **Python ≥ 3.11**.

---

## 1. General Principles

* **Always use Python type hints** → types live in the **function signature**, not duplicated in the docstring.
* Docstrings focus on:

  * What the function **does**.
  * Meaning and units of parameters.
  * Return value meaning.
  * State/variables updated (**Modifies**).
  * Functions called (**Calls**).
  * Expected errors (**Raises**).
* Use **NumPy-style** sections for readability and doc tool compatibility.

---

## 2. Example Function with Full Docstring

Below is an example that demonstrates the **recommended style** for docstrings and type hints in this project. It shows how to document **parameters**, **returns**, **modifications**, **calls**, and **exceptions**.

```python
from pathlib import Path
from typing import Final

import numpy as np
import numpy.typing as npt
import pydicom
from pydicom.dataset import FileDataset

# Example constant with a type hint
EPS: Final[float] = 1e-12


def update_dose_matrix(
    rt_dose: FileDataset,
    new_matrix: npt.NDArray[np.float32],  # shape: (z, y, x), Gy
    normalize: bool = True,
) -> None:
    """
    Update the dose matrix inside an RTDOSE DICOM object.

    Parameters
    ----------
    rt_dose
        DICOM RTDOSE dataset to update.
    new_matrix
        New 3D dose grid ``(z, y, x)`` in **Gy**.
    normalize
        If ``True``, rescale values to match ``DoseGridScaling``.

    Returns
    -------
    None

    Modifies
    --------
    rt_dose.pixel_array
        Replaces the internal dose grid with ``new_matrix``.
    rt_dose.DoseGridScaling
        Updated if ``normalize=True``.

    Calls
    -----
    validate_dose_matrix, rescale_dose

    Raises
    ------
    ValueError
        If ``new_matrix`` has incompatible shape or contains NaNs.
    """
    # (implementation here)
    pass
```

---

## 3. Typing Examples (Python 3.11 syntax)

Use **modern forms** (`|` unions, built‑in generics) and concrete library types.

```python
from pathlib import Path
import SimpleITK as sitk
import pydicom
from pydicom.dataset import FileDataset

# Accept both strings and Paths; may return nothing

def load_rtplan(path: str | Path | None = None) -> FileDataset | None:
    ...

# Simple union narrowing

def parse_value(x: int | float) -> float:
    ...

# Tuples with built-in generics

def resample_ct(img: sitk.Image, spacing: tuple[float, float, float]) -> sitk.Image:
    ...

# Collections with built-in generics

def summarize(ds_list: list[FileDataset]) -> dict[str, str]:
    ...
```

> **Tip:** For arrays, prefer `numpy.typing.NDArray` with explicit dtypes, e.g. `npt.NDArray[np.float32]`.

---

## 4. Docstring Template (NumPy style)

Copy this template when adding new functions.

```python
def function_name(param1: int, param2: str | None = None) -> bool:
    """
    One-sentence summary in the imperative mood.

    Extended description (what, why, and context). Keep types in the signature,
    and focus here on meaning, units, shapes, side effects, and behavior.

    Parameters
    ----------
    param1
        Meaning of param1; units if applicable.
    param2
        Meaning of param2; when ``None`` is allowed and what it means.

    Returns
    -------
    bool
        What ``True``/``False`` indicate.

    Modifies
    --------
    obj.attr
        What object/attribute is modified (if any).

    Calls
    -----
    other_function, helper

    Raises
    ------
    ValueError
        When inputs are invalid (describe conditions).
    RuntimeError
        When an unexpected state is encountered.
    """
    ...
```

---

## 5. Common Pitfalls

* **Don’t duplicate types in the docstring** — keep them in the signature.
* **Document shapes and units** (e.g., `(z, y, x)`, `mm`, `Gy`) in the docstring text.
* **Prefer concrete library types**: `sitk.Image`, `pydicom.dataset.FileDataset`.
* **Be precise with `Path`**: accept `str | Path` in public APIs.
* **Use `Final` for constants** and annotate dataclass/attrs fields.
