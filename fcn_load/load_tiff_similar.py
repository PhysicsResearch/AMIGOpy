import os
from pathlib import Path

import numpy as np
import SimpleITK as sitk
from PySide6.QtWidgets import QFileDialog


TIFF_EXTS = ('.tif', '.tiff')
PNG_EXTS  = ('.png',)
JPEG_EXTS = ('.jpg', '.jpeg')
BMP_EXTS  = ('.bmp',)


def _series_number_from_name(filename: str) -> str:
    """
    Strip extensions from a filename for a human friendly SeriesNumber.
    """
    stem, _ = os.path.splitext(filename)
    return stem


def _read_raster_series(path: str, data_type_label: str):
    """
    Internal helper to read TIFF, PNG, JPEG, BMP with SimpleITK and return
    a dict that can be stored in self.image.

    Notes:
      - Uses SimpleITK auto ImageIO detection.
      - Color images are kept as RGB(A) in RGBMatrix (z, y, x, c).
      - 3DMatrix is always single-channel grayscale (z, y, x) for your pipeline.
      - 2D images are returned with z = 1.
    """
    filename = os.path.basename(path)
    series_number = _series_number_from_name(filename)

    reader = sitk.ImageFileReader()
    reader.SetFileName(path)
    image = reader.Execute()

    num_comp = image.GetNumberOfComponentsPerPixel()

    # ---- Get raw array from SimpleITK ----
    arr = sitk.GetArrayFromImage(image)  # shapes:
                                         # scalar: (z, y, x) or (y, x)
                                         # color:  (z, y, x, c) or (y, x, c)

    # Ensure we always have a leading z dimension
    if arr.ndim == 2:
        arr = arr[np.newaxis, ...]           # (1, y, x)
    elif arr.ndim == 3 and num_comp > 1:
        # (y, x, c) -> (1, y, x, c)
        arr = arr[np.newaxis, ...]           # (1, y, x, c)

    # Cast to int16 for consistency
    arr = arr.astype(np.int16)

    if num_comp > 1:
        # Color image: keep full RGB(A) in RGBMatrix
        vol_rgb = arr                         # (z, y, x, c)
        # Make a grayscale volume for 3DMatrix using luminance
        # use only first 3 channels if there is alpha
        rgb_for_gray = vol_rgb[..., :3].astype(np.float32)
        gray = (
            0.2989 * rgb_for_gray[..., 0] +
            0.5870 * rgb_for_gray[..., 1] +
            0.1140 * rgb_for_gray[..., 2]
        )
        gray = gray.astype(np.int16)
        if gray.ndim == 2:
            gray = gray[np.newaxis, ...]     # (1, y, x)
        vol = gray                            # (z, y, x)
    else:
        # Scalar image: no RGB channels
        vol_rgb = None
        if arr.ndim == 3:
            vol = arr                         # (z, y, x)
        else:
            # should not happen with the handling above, but just in case
            vol = arr[np.newaxis, ...]

    # ---- Geometry ----
    spacing   = image.GetSpacing()       # (x, y, [z])
    size      = image.GetSize()          # (x, y, [z])
    origin    = image.GetOrigin()        # image origin
    direction = image.GetDirection()     # flattened 2x2 or 3x3, depending on dim

    # Raw metadata from image header (EXIF, TIFF tags etc when present)
    try:
        raw_meta = {k: image.GetMetaData(k) for k in image.GetMetaDataKeys()}
    except Exception:
        raw_meta = {}

    # TIFF style metadata fields (fill with "N/A" if missing)
    tiff_like_fields = {}
    for key in (
        "ImageWidth",
        "ImageLength",
        "BitsPerSample",
        "SamplesPerPixel",
        "PhotometricInterpretation",
        "Compression",
        "PlanarConfiguration",
        "Orientation",
        "ResolutionUnit",
        "XResolution",
        "YResolution",
        "Software",
        "DateTime",
        "Make",
        "Model",
    ):
        tiff_like_fields[key] = raw_meta.get(key, "N/A")

    # Pixel spacing and slice thickness
    if len(spacing) >= 2:
        pixel_spacing = spacing[0:2]
    else:
        pixel_spacing = (1.0, 1.0)

    slice_thickness = spacing[2] if len(spacing) >= 3 else 1.0

    metadata = {
        # Basic geometry
        'ImageWidth': size[0] if len(size) > 0 else None,
        'ImageLength': size[1] if len(size) > 1 else None,
        'PixelSpacing': pixel_spacing,
        'SliceThickness': slice_thickness,
        'Origin': origin,
        'Direction': direction,

        # TIFF style fields
        **tiff_like_fields,

        # Generic info
        'SeriesDescription': filename,      # file name with extension
        'DataType': data_type_label,
        'Size': size,
        'OriginalFilePath': path,
        'RawMeta': raw_meta,

        # Component info
        'NumComponents': num_comp,
    }

    series = {
        'SeriesNumber': series_number,
        'metadata': metadata,
        # main scalar volume used by current pipeline
        '3DMatrix': vol,        # (z, y, x)
        # full color data when available
        'RGBMatrix': vol_rgb,   # (z, y, x, c) or None
        # kept for compatibility
        'images': {},
        'ImagePositionPatients': [],
        'SliceImageComments': {},
        'AM_name': None,
        'US_name': None,
    }

    return series


def _load_raster_files(self,
                       path,
                       exts,
                       data_type_label: str,
                       title: str,
                       last_attr_name: str):
    """
    Internal helper to load one format into self.image as a flat list.

    self.image will be a list of series dictionaries.
    """
    start_dir = getattr(self, last_attr_name, str(Path.home()))

    # File selection
    if path is None:
        pattern = " ".join(f"*{e}" for e in exts)
        filter_str = f"{data_type_label} files ({pattern});;All files (*)"
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            title,
            start_dir,
            filter_str
        )
    else:
        if os.path.isdir(path):
            paths = [
                os.path.join(path, f)
                for f in os.listdir(path)
                if Path(f).suffix.lower() in exts
            ]
        elif os.path.isfile(path):
            if Path(path).suffix.lower() in exts:
                paths = [path]
            else:
                paths = []
        else:
            paths = []

    if not paths:
        return

    # Ensure container list
    if not hasattr(self, 'image') or not isinstance(self.image, list):
        self.image = []

    for fpath in paths:
        ext = Path(fpath).suffix.lower()
        if ext not in exts:
            continue

        series = _read_raster_series(fpath, data_type_label=data_type_label)
        self.image.append(series)

    # Remember last directory for this format
    setattr(self, last_attr_name, str(Path(paths[0]).parent))

    # Update the "Image" branch in the tree
    from fcn_load.populate_med_image_list import populate_image
    populate_image(self)


# Public API functions for this module

def load_tiff_files(self, path=None):
    """Load TIFF files into self.image."""
    _load_raster_files(
        self,
        path=path,
        exts=TIFF_EXTS,
        data_type_label="TIFF",
        title="Open TIFF files",
        last_attr_name='last_tiff_dir'
    )


def load_png_files(self, path=None):
    """Load PNG files into self.image."""
    _load_raster_files(
        self,
        path=path,
        exts=PNG_EXTS,
        data_type_label="PNG",
        title="Open PNG files",
        last_attr_name='last_png_dir'
    )


def load_jpeg_files(self, path=None):
    """Load JPEG files into self.image."""
    _load_raster_files(
        self,
        path=path,
        exts=JPEG_EXTS,
        data_type_label="JPEG",
        title="Open JPEG files",
        last_attr_name='last_jpeg_dir'
    )


def load_bmp_files(self, path=None):
    """Load BMP files into self.image."""
    _load_raster_files(
        self,
        path=path,
        exts=BMP_EXTS,
        data_type_label="BMP",
        title="Open BMP files",
        last_attr_name='last_bmp_dir'
    )
