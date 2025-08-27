# Typing Guidelines

This document is the **authoritative reference** for using **Python type hints** in this project.  
We target **Python ≥ 3.12**. Adhere to these rules to keep code readable, analyzable, and well-documented.

---

## 1) Principles & Scope

- **Annotate everything public**: function parameters, return types, class attributes, module-level constants.
- **Prefer precise types** over `Any`. Use `Any` only as an escape hatch.
- **Use PEP 604 unions** (`A | B`) and **PEP 585 built-in generics** (`list[int]`, `dict[str, str]`).
- **Design to interfaces**: prefer `collections.abc` protocols (`Iterable`, `Mapping`, `Callable`) when exact containers aren’t required.
- **Keep docstrings about meaning/units/behavior**; keep *types* in signatures.
- **Fail fast**: enable strict checks in `mypy`/`ruff` (see §14).

---

## 2) PEP Basics

- **PEP 484** — typing semantics (annotations, `typing` module).
- **PEP 585** — built-in generics (`list[int]`, `dict[str, int]`).
- **PEP 604** — unions with `|` (`int | float`, `str | None`).
- **PEP 563/649** — (deferred annotations history; not needed to configure on 3.12).
- **PEP 612** — `ParamSpec`, `Concatenate` (callable parameters).
- **PEP 646** — `TypeVarTuple`, `Unpack` (variadic generics).
- **PEP 647** — `TypeGuard` (user-defined type narrowing).
- **PEP 655** — `Required` / `NotRequired` in `TypedDict`.
- **PEP 673** — `Self` type.
- **PEP 675** — `LiteralString` (security-sensitive APIs).
- **PEP 681** — `@dataclass_transform` (ORM/DTO frameworks).
- **PEP 593** — `Annotated[T, ...]` metadata (units, constraints).

---

## 3) Core Syntax (Use These Forms)

- **Unions / Optional**  
  ```python
  def load(path: str | None) -> bytes | None: ...

  # Typing Examples for Scientific Python Code

This page provides **ready-to-use typing examples** for common libraries in this project:  
**NumPy**, **pandas**, **SimpleITK**, and **pydicom**, plus common path and file handling.  
We target **Python ≥ 3.11  ** and always use:

- **PEP 604 unions** → `A | B` instead of `Union[A, B]`
- **PEP 585 built-in generics** → `list[int]` instead of `List[int]`
- **NumPy typing (`numpy.typing`)** for arrays
- Official classes from libraries (`sitk.Image`, `pydicom.dataset.FileDataset`)

---


# NumPy Typing Guidelines (Python 3.11)

This page defines **how we type NumPy arrays** in this project.  
Target runtime: **Python 3.11**.

> ✅ We use `numpy.typing.NDArray` for array annotations.  
> ✅ Import `numpy` as `np` and `numpy.typing` as `npt`.  
> ⚠️ Don’t alias both modules to the same name — keep `np` for NumPy *and* `npt` for typing.

```python
import numpy as np
import numpy.typing as npt



## 1. NumPy Typing

NumPy typing uses `numpy.typing.NDArray` to describe array contents and dtypes.

```python
import numpy as np
import numpy.typing as npt

# Single dtype (float32)
def normalize(vol: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]:
    """
    Normalize the volume to range [0, 1].
    Shape: (z, y, x)
    """
    ...

# Any floating dtype
def clip_unit(a: npt.NDArray[np.floating]) -> npt.NDArray[np.floating]:
    """Clamp values to [0, 1]."""
    ...

# Boolean mask
def mask_volume(vol: npt.NDArray[np.float32],
                mask: npt.NDArray[np.bool_]) -> npt.NDArray[np.float32]:
    """Applies binary mask to volume."""
    ...

# Vector / matrix transformations
def transform_points(pts: npt.NDArray[np.float64],
                     T: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """
    Apply transformation matrix T to point cloud.
    pts: shape (N, 3)
    T: shape (4, 4)
    """
    ...

# When shape varies → use Sequence
from collections.abc import Sequence

def bbox_from_points(points: Sequence[Sequence[float]]) -> tuple[float, float, float, float, float, float]:
    """Compute bounding box from list of 3D points."""
    ...


## 2. Basic DataFrame Typing

```python
import pandas as pd

def clean_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize the dataset.

    Parameters
    ----------
    df
        Input table containing patient data.

    Returns
    -------
    pd.DataFrame
        Cleaned and standardized DataFrame.
    """
    ...

# 3. Example: Splitting a pandas DataFrame by Modality

This example shows how to **split a pandas DataFrame** into two separate DataFrames based on the **"Modality"** column.

```python
import pandas as pd
from typing import Tuple

def split_by_modality(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split the dataset into CT and MR subsets.

    Parameters
    ----------
    df
        Input dataset containing a "Modality" column.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        First DataFrame: CT studies.
        Second DataFrame: MR studies.
    """
    df_ct = df[df["Modality"] == "CT"]
    df_mr = df[df["Modality"] == "MR"]
    return df_ct, df_mr