# Typing Guidelines

This document is the **authoritative reference** for using **Python type hints** in this project.
We target **Python ≥ 3.11**. Follow these guidelines to keep code consistent, analyzable, and well-documented.

---

## What is "typing"?

Typing means annotating **function signatures** and **variables** with explicit types so both humans and tools understand your code better.

**Example:**

```python
from pathlib import Path

def load_bytes(path: str | Path) -> bytes:
    """Read a file and return its raw bytes."""
    p = Path(path)
    return p.read_bytes()

# Editors + checkers will now warn:
load_bytes(123)        # ❌ int is not str|Path
load_bytes("data.bin") # ✅ ok
```

Benefits:

* **Developers** see contracts at a glance.
* **Editors** provide better completions.
* **Checkers** (mypy, pyright, ruff) catch mistakes early.

---

## 1) Principles & Scope

* **Annotate everything public**: functions, class attributes, constants.
* **Prefer precise types** over `Any` — use `Any` only when unavoidable.
* Use **PEP 604 unions** (`A | B`) and **PEP 585 built-in generics** (`list[int]`, `dict[str, str]`).
* Prefer `collections.abc` interfaces (`Iterable`, `Mapping`, `Callable`) when exact containers aren’t required.
* Docstrings describe **meaning, units, and behavior** — **not** types.
* Enable **strict mode** in `mypy` and `ruff`.

---

## 2) Relevant Standards (PEPs)

* **PEP 484** — typing basics
* **PEP 585** — built-in generics (`list[int]`)
* **PEP 604** — unions with `|` (`int | float`)
* **PEP 612** — `ParamSpec`, `Concatenate`
* **PEP 646** — variadic generics (`TypeVarTuple`, `Unpack`)
* **PEP 647** — `TypeGuard`
* **PEP 655** — `Required` / `NotRequired` for `TypedDict`
* **PEP 673** — `Self` type
* **PEP 675** — `LiteralString`
* **PEP 593** — `Annotated[T, ...]` for metadata like units

> **Python ≥3.11**: No need for `from __future__ import annotations`.

---

## 3) Core Syntax Examples

```python
# Unions / Optional
def load(path: str | None) -> bytes | None: ...
```

```python
# Collections
from collections.abc import Iterable, Mapping

def uniq(xs: Iterable[int]) -> list[int]: ...
def normalize_map(m: Mapping[str, float]) -> dict[str, float]: ...
```

```python
# Callables
from collections.abc import Callable

def retry(fn: Callable[[], int], attempts: int = 3) -> int: ...
```

```python
# TypedDict
from typing import TypedDict, Required, NotRequired

class SeriesMeta(TypedDict):
    modality: Required[str]
    description: NotRequired[str]
```

```python
# Methods returning the same type
from typing import Self

class Volume:
    def copy(self) -> Self: ...
```

---

## 4) NumPy Typing (Project Standard)

Use `numpy.typing.NDArray`:

```python
import numpy as np
import numpy.typing as npt

def normalize(vol: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]:
    """Scale to [0, 1]. Shape: (z, y, x)."""
    ...

def mask_volume(vol: npt.NDArray[np.float32],
                mask: npt.NDArray[np.bool_]) -> npt.NDArray[np.float32]:
    """Apply binary mask."""
    ...

def transform_points(pts: npt.NDArray[np.float64],
                     T: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """pts: (N,3), T: (4,4)."""
    ...
```

For variable shapes, use:

```python
from collections.abc import Sequence

def bbox_from_points(points: Sequence[Sequence[float]]) -> tuple[float, float, float, float, float, float]:
    """Compute bounding box from list of 3D points."""
    ...
```

---

## 5) pandas Typing

```python
import pandas as pd

def clean_table(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned and standardized DataFrame."""
    ...
```

**Example: Split by modality**

```python
def split_by_modality(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (CT_df, MR_df) filtered by df["Modality"]."""
    df_ct = df[df["Modality"] == "CT"]
    df_mr = df[df["Modality"] == "MR"]
    return df_ct, df_mr
```

---

## 6) SimpleITK & pydicom

Prefer concrete library types:

```python
import SimpleITK as sitk
from pydicom.dataset import FileDataset

def resample(im: sitk.Image, to_like: sitk.Image) -> sitk.Image: ...
def read_rt_dose(path: str | Path) -> FileDataset: ...
```

---

