# Structures Data Model

This document defines the **structure-related keys** stored under a **series entry** in `self.medical_image`.

## Location in the Hierarchy

```python
self.medical_image[patientID][studyID][modality][series_index]
```

Each `series_index` maps to a **series dictionary** that may contain the keys below.

---

## Key Reference (per series)

| Key                            | Type                                    | Description                                                                                                                                                                                                               |
| ------------------------------ | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `structures`                   | `dict[str, StructureItem]`              | Mapping from **structure key** (e.g., `Item_1`) to a structure payload (see **StructureItem** below). Each item primarily represents a **binary mask** aligned to the series volume, plus cached visualization artifacts. |
| `structures_names`             | `list[str]`                             | Display names for structures (can repeat). Index positions correspond one‑to‑one with `structures_keys`.                                                                                                                  |
| `structures_keys`              | `list[str]`                             | Internal unique keys (`Item_1`, `Item_2`, …). Used to index `structures`. Length equals `len(structures_names)`.                                                                                                          |
| `structures_view`              | `list[int]` (0 or 1)                    | Per‑structure visibility flag used **only by the View tab**. `1` = show, `0` = hide. Same length/order as `structures_keys`.                                                                                              |
| `structures_color`             | `list[tuple[int, int, int]]` or hex str | Per‑structure display color (e.g., `(r,g,b)` in 0–255 or `"#RRGGBB"`). Same length/order as `structures_keys`.                                                                                                            |
| `structures_line_width`        | `list[float]`                           | Per‑structure contour line width (in pixels). Same length/order as `structures_keys`.                                                                                                                                     |
| `structures_transparency`      | `list[float]` (0.0–1.0)                 | Per‑structure **contour line** transparency. `0` = opaque, `1` = fully transparent. Same length/order as `structures_keys`.                                                                                               |
| `structures_mask_transparency` | `list[float]` (0.0–1.0)                 | Per‑structure **mask overlay** transparency. `0` = opaque, `1` = fully transparent. Same length/order as `structures_keys`. *(Note: key name contains a typo: `transparency`)*                                            |

> **Indexing:** The **selected structure** in the UI is determined by the user’s click in the **tree/list widget**. That selection resolves to an **index** `i`, which is used to read the `i`‑th entry across `structures_*` lists and the corresponding `structures_keys[i]` to access the payload in `structures`.

---

## `StructureItem` payload

Each entry in `structures` (e.g., `structures["Item_3"]`) is a dictionary with (at least) the following fields:

| Field         | Type                           | Description                                                                                                                                                    |
| ------------- | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mask`        | `numpy.ndarray` (dtype `bool`) | Binary mask **aligned to the image data** for the series. Same shape as the volume (e.g., `(Z, Y, X)`). Often labelled in code as `Mask3D` (or similar).       |
| `VTKActors2D` | implementation-defined         | Cached **VTK actors** built on first display for fast redraws. Created lazily in the View tab.                                                                 |
| `Contours2D`  | implementation-defined         | Cached **2D contours** corresponding to the mask, created together with VTK actors.                                                                            |
| `modified`    | `int` (0 or 1)                 | Marks whether the mask was **edited** via the segmentation module. When `1`, cached contours/actors must be **regenerated** on next selection in the View tab. |

> Actual field names may include additional items depending on the importer/processing pipeline. The three shown above are the core visualization/logic hooks.

---

## Lifecycle & Performance Notes

* **First display is lazy:** When a user **first toggles** a structure for viewing, AMIGO creates `VTKActors2D` and `Contours2D` **once** (in the View tab) so subsequent redraws are fast.
* **Editing vs. contours:** The **Segmentation** module edits only the **mask** for speed. It does **not** directly edit contours/actors. After an edit, the structure’s `modified` flag is set to `1`.
* **Regeneration trigger:** If `modified == 1`, AMIGO will **recreate** `Contours2D` and `VTKActors2D` the next time the structure is selected for viewing, ensuring the overlays match the updated mask.
* **Transparency semantics:**

  * `structures_transparency` controls **contour line** alpha.
  * `structures_mask_transparency` controls **overlay fill** alpha. *(Key name includes a typo; maintain as-is for compatibility.)*
* **View tab overlays:** The View tab lets users choose between **mask overlays** and **line contours**. Using contours helps when visual inspection of underlying HU/intensity details is important (semi‑transparent fills might obscure features).

---

## Creation & Source

The `Contours2D` and `VTKActors2D` objects are produced in:

```
fcn_RTFiles/process_contours.py
```

(Functions responsible for building contours and VTK actors are defined there.)

---

## Minimal Example

```python
series = self.medical_image[pid][sid][mod][series_index]

# Lists indexed by UI selection index i
series["structures_names"]          # ["PTV", "Lung_L", ...]
series["structures_keys"]           # ["Item_1", "Item_2", ...]
series["structures_view"]           # [1, 0, ...]
series["structures_color"]          # [(255,0,0), (0,255,0), ...]
series["structures_line_width"]     # [1.5, 1.5, ...]
series["structures_transparency"]   # [0.0, 0.3, ...]
series["structures_mask_transparency"] # [0.6, 0.8, ...]

# Structure payload accessed via key
key = series["structures_keys"][i]   # e.g., "Item_2"
item = series["structures"][key]
mask3d = item["mask"]                 # bool array (Z,Y,X)
if item["modified"]:
    # trigger rebuild of contours/actors on next view
    pass
```

---

## Invariants & Validation

* All `structures_*` lists share the **same length** and **order**.
* Every entry in `structures_keys` must exist as a key in `structures`.
* Each `StructureItem.mask` must match the **series volume shape**.
* `structures_view[i]` ∈ `{0,1}`; `modified` ∈ `{0,1}`.
* Colors and widths are optional but, when present, must match list lengths.

---
