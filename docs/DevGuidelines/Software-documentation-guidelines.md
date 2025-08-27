# Docstring & Type Hint Guidelines

This page defines the conventions for writing **docstrings** see the [Docstring Guidelines](Docstring.md) and using **type hints** [Typing Guidelines](Typing.md) in this project.  
We follow **NumPy-style docstrings** and use **Python type hints** as the single source of truth for parameter and return types.

---

## 1. General Principles

- **Always use Python type hints** → types go in the **function signature**, not duplicated in the docstring.
- Docstrings should focus on:
  - What the function **does**.
  - Meaning and units of parameters.
  - Return value meaning.
  - State or variables updated (**Modifies**).
  - Functions called (**Calls**).
- Use **NumPy-style** sections for better readability and compatibility with documentation tools.

---

## 2. Example Function with Full Docstring

Below is an example function that demonstrates the **recommended style** for docstrings and type hints in this project.  
It shows how to document **parameters**, **returns**, **modifications**, **calls**, and **exceptions**.

```python
def update_dose_matrix(
    rt_dose: pydicom.dataset.FileDataset,
    new_matrix: np.ndarray,
    normalize: bool = True,
) -> None:
    """
    Update the dose matrix inside an RTDOSE DICOM object.

    Parameters
    ----------
    rt_dose
        DICOM RTDOSE dataset to update.
    new_matrix
        New 3D dose grid (z, y, x), in Gy.
    normalize
        Whether to rescale values to match `DoseGridScaling`.

    Returns
    -------
    None

    Modifies
    --------
    rt_dose.pixel_array
        Replaces the internal dose grid with `new_matrix`.
    rt_dose.DoseGridScaling
        Updated if `normalize=True`.

    Calls
    -----
    - `validate_dose_matrix`
    - `rescale_dose`

    Raises
    ------
    ValueError
        If `new_matrix` has incompatible shape or NaNs.
    """


## 3. PEP 484 vs PEP 604 hints — What We Use and Why

We use **type hints everywhere**. The rules were introduced by **PEP 484** and later improved with **PEP 604**.  
Since this project targets Python ≥ 3.12, we **prefer the modern PEP 604 syntax**.

### PEP 484 (original typing rules, verbose syntax)
- Introduced the `typing` module (e.g., `Optional`, `Union`, `List`, `Dict`).
- Still valid, but often more verbose.

```python
from typing import Optional, Union, List, Dict, Tuple

def load_rtplan(path: Optional[str] = None) -> Optional[pydicom.dataset.FileDataset]:
    ...

def parse_value(x: Union[int, float]) -> float:
    ...

def resample_ct(img: sitk.Image, spacing: Tuple[float, float, float]) -> sitk.Image:
    ...

def summarize(ds_list: List[pydicom.dataset.FileDataset]) -> Dict[str, str]: