"""
Histograms of the image layers (View > View, fcn_init/view_hist.py), with exact voxel counts:
- integer images (CT, masks, maps): a voxel count per value (bincount in chunks), from which any bins
  follow at once and exactly;
- other images (dose, density): numpy's uniform histogram of all finite voxels.
The bins are uniform and the same for all the layers shown, so the CSV export is one table.
"""
import math

import numpy as np

CHUNK = 8_000_000           # voxels per bincount call (an int64 index array of 64 MB)
MAX_TABLE = 5_000_000       # values of a per-value count table (a wider integer range: numpy's histogram)
MAX_BINS = 20_000
SMOOTH_SIGMA = 2.0          # bins: the smoothing the View histogram always had


def finite_range(arr):
    """(min, max, number of finite voxels) of an image, None when it has no finite value."""
    a = np.asarray(arr)
    if a.size == 0:
        return None
    if a.dtype.kind in "iub":
        return float(a.min()), float(a.max()), int(a.size)
    finite = np.isfinite(a)
    n = int(np.count_nonzero(finite))
    if n == 0:
        return None
    if n == a.size:
        return float(a.min()), float(a.max()), n
    return float(np.min(a, where=finite, initial=np.inf)), float(np.max(a, where=finite, initial=-np.inf)), n


def value_table(arr, lo, hi):
    """(lo, voxel count of each value lo..hi) of an integer image; None for other images or a too wide range."""
    a = np.asarray(arr)
    lo, hi = int(lo), int(hi)
    if a.dtype.kind not in "iub" or hi - lo + 1 > MAX_TABLE:
        return None
    counts = np.zeros(hi - lo + 1, dtype=np.int64)
    flat = a.reshape(-1)
    for start in range(0, flat.size, CHUNK):
        part = flat[start:start + CHUNK].astype(np.int64)
        part -= lo
        counts += np.bincount(part, minlength=counts.size)
    return lo, counts


def bin_edges(lo, hi, n_bins=512, width=None, integer=False):
    """
    Uniform bin edges over [lo, hi]: bins 'width' wide (centred on its multiples), else n_bins of them.
    Integer images get whole-number widths with bins centred on whole values, so that no bin holds
    one value more than its neighbours (a comb in the histogram).
    """
    lo, hi = float(lo), float(hi)
    if not (math.isfinite(lo) and math.isfinite(hi)):
        lo, hi = 0.0, 1.0
    if hi < lo:
        lo, hi = hi, lo
    if width is not None and width > 0:
        width = max(float(width), (hi - lo) / (MAX_BINS - 2))      # centring can add a bin at each end
        first = (math.floor(lo / width + 0.5) - 0.5) * width
        n = max(1, math.ceil((hi - first) / width - 1e-9))
        if first + n * width < hi:
            n += 1
        return first + width * np.arange(n + 1)
    n_bins = int(min(max(1, n_bins), MAX_BINS))
    if integer:
        width = float(max(1, math.ceil((hi - lo + 1) / n_bins - 1e-9)))
        n = max(1, math.ceil((hi - lo + 1) / width - 1e-9))
        return (lo - 0.5) + width * np.arange(n + 1)
    if hi == lo:
        lo, hi = lo - 0.5, hi + 0.5
    return np.linspace(lo, hi, n_bins + 1)


def table_histogram(table, edges):
    """Exact voxel counts per bin from a value table (numpy's bins: [start, end), the last one closed)."""
    lo, counts = table
    n = counts.size
    cum = np.concatenate(([0], np.cumsum(counts)))      # cum[j]: voxels with a value below lo + j
    edges = np.asarray(edges, dtype=float)
    below = cum[np.clip(np.ceil(edges).astype(np.int64) - lo, 0, n)]
    out = np.diff(below)
    out[-1] = cum[np.clip(int(math.floor(edges[-1])) - lo + 1, 0, n)] - below[-2]
    return out


def array_histogram(arr, edges):
    """Exact counts of an image's finite voxels in uniform bins (numpy's histogram)."""
    counts, _ = np.histogram(arr, bins=len(edges) - 1, range=(float(edges[0]), float(edges[-1])))
    return counts


def quantile_range(arr, rng, table, q_low, q_high):
    """
    Values at two quantiles of an image's finite voxels (0 and 1: its min and max), e.g. a window over
    1-99 % of the voxels: exact from a value table, else from up to 2 million voxels.
    """
    lo, hi, _ = rng
    if table is not None:
        first, counts = table
        cum = np.cumsum(counts)

        def at(q):
            return lo if q <= 0 else hi if q >= 1 else float(first + np.searchsorted(cum, q * cum[-1]))

        return at(q_low), at(q_high)
    flat = np.asarray(arr).reshape(-1)
    sample = flat[::max(1, flat.size // 2_000_000)]
    sample = sample[np.isfinite(sample)]
    if sample.size == 0:
        return lo, hi
    q = np.quantile(sample, [min(max(q_low, 0.0), 1.0), min(max(q_high, 0.0), 1.0)])
    return (lo if q_low <= 0 else float(q[0])), (hi if q_high >= 1 else float(q[1]))


def smooth(values, sigma=SMOOTH_SIGMA):
    """Gaussian smoothing over the bins (sigma in bins)."""
    values = np.asarray(values, dtype=float)
    k = 6 * int(math.ceil(sigma)) + 1
    if values.size < k:
        return values.copy()
    x = np.arange(k) - (k - 1) / 2.0
    kernel = np.exp(-0.5 * (x / sigma) ** 2)
    return np.convolve(values, kernel / kernel.sum(), mode="same")


def csv_table(edges, curves):
    """
    Header and rows of the histograms shown: bin start, end and centre, then per layer its voxel counts
    and, when the plot shows other values (percent, smoothed), those. curves: [(label, counts, plotted
    or None, name of the plotted values)].
    """
    header, columns = ["bin_start", "bin_end", "bin_center"], []
    for label, counts, plotted, what in curves:
        header.append(f"{label} voxels")
        columns.append(np.asarray(counts))
        if plotted is not None:
            header.append(f"{label} {what}")
            columns.append(np.asarray(plotted))
    edges = np.asarray(edges, dtype=float)
    centers = 0.5 * (edges[:-1] + edges[1:])
    rows = [[edges[i], edges[i + 1], centers[i], *(col[i] for col in columns)] for i in range(len(centers))]
    return header, rows
