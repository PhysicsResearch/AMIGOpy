# Docstring Guidelines

This document defines how to write **docstrings** for this project.  
We follow **NumPy-style docstrings** combined with **Python type hints** for clarity and consistency.

---

## 1. General Rules

- Use **Python type hints** → types go in the **function signature**, not duplicated in the docstring.
- Use **NumPy-style** docstrings:
  - Clear structure.
  - Easy to read.
  - Compatible with automated documentation tools.
- A docstring should explain:
  - **What** the function/class/module does.
  - **Meaning and units** of parameters.
  - **What is returned**.
  - **Modifications** to attributes or global state.
  - **Functions called** (if relevant).
  - **Exceptions raised**.
- Keep **trivial functions** one-liners; describe **complex functions** thoroughly.

---

## 2. Docstring Structure

Recommended sections (in order):

| **Section**   | **Purpose**                            | **Required** |
|--------------|---------------------------------------|--------------|
| **Summary**  | Short, imperative description         | ✅ Yes |
| **Parameters** | Describe purpose, meaning, and units | ✅ Yes |
| **Returns**  | Describe returned values              | ✅ Yes |
| **Modifies** | List attributes or globals changed    | ⚠️ If applicable |
| **Calls**    | List important functions invoked      | ✅ Yes|
| **Raises**   | List exceptions                       | ⚠️ If applicable |
| **Notes**    | Assumptions, limitations, etc.        | Optional |
| **Examples** | Demonstrate usage                     | Optional |

---

## 3. Canonical Example

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

    Notes
    -----
    Persist changes with `pydicom.dcmwrite` after this call.
    """
```