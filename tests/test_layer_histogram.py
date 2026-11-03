"""
Exact layer histograms (fcn_display/layer_histogram.py): integer images through a per-value table,
other images through numpy, uniform bins shared by the layers, quantiles and the CSV table.
"""
import numpy as np
import pytest

from fcn_display import layer_histogram as lh


def test_bins_of_integer_images_are_whole_values():
    edges = lh.bin_edges(-1000, 3000, n_bins=512, integer=True)
    widths = np.diff(edges)
    assert np.allclose(widths, 8.0)                           # 4001 values / 512 bins -> 8 per bin
    assert edges[0] == -1000.5 and edges[-1] >= 3000.5        # bins centred on whole values, all covered
    one_per_value = lh.bin_edges(-3, 3, width=1)
    assert np.allclose(one_per_value, np.arange(-3.5, 4.0)) and np.allclose(np.diff(one_per_value), 1)
    tens = lh.bin_edges(-1000, 2000, width=10)
    assert np.isclose(tens[0], -1005) and tens[-1] >= 2000 and np.allclose(np.diff(tens), 10)
    floats = lh.bin_edges(0.0, 70.0, n_bins=7)
    assert np.allclose(floats, np.arange(0, 71, 10))
    assert len(lh.bin_edges(0, 1e6, width=0.001)) - 1 <= lh.MAX_BINS


@pytest.mark.parametrize("edges", [np.arange(-10.5, 11.0, 1.0), np.linspace(-10, 10, 7), np.array([-3.0, 0.0, 2.5, 7.0])])
def test_value_table_counts_equal_numpy(edges, monkeypatch):
    monkeypatch.setattr(lh, "CHUNK", 37)                      # several bincount chunks
    data = np.random.default_rng(1).integers(-10, 11, size=(5, 7, 9)).astype(np.int16)
    rng = lh.finite_range(data)
    table = lh.value_table(data, rng[0], rng[1])
    assert table[1].sum() == data.size
    expected, _ = np.histogram(data, bins=edges)
    assert np.array_equal(lh.table_histogram(table, edges), expected)
    assert np.array_equal(lh.array_histogram(data, edges), expected) or edges.size == 4   # numpy: uniform bins only


def test_value_table_kinds():
    mask = np.zeros((4, 4), bool)
    mask[1:3, 1:3] = True
    lo, counts = lh.value_table(mask, 0, 1)
    assert lo == 0 and counts.tolist() == [12, 4]
    assert lh.value_table(np.array([0, 10 ** 9], np.int64), 0, 10 ** 9) is None     # too wide: numpy instead
    assert lh.value_table(np.array([0.5, 1.5]), 0, 2) is None


def test_float_images_count_finite_voxels_only():
    dose = np.array([0.0, 1.5, np.nan, 2.5, np.inf, 9.9])
    assert lh.finite_range(dose) == (0.0, 9.9, 4)
    assert lh.finite_range(np.full(3, np.nan)) is None
    counts = lh.array_histogram(dose, lh.bin_edges(0.0, 9.9, n_bins=3))
    assert counts.tolist() == [3, 0, 1]


def test_quantiles():
    data = np.repeat(np.arange(100, dtype=np.int16), 10)       # 0..99, ten voxels each
    rng = lh.finite_range(data)
    table = lh.value_table(data, rng[0], rng[1])
    assert lh.quantile_range(data, rng, table, 0.0, 1.0) == (0.0, 99.0)
    assert lh.quantile_range(data, rng, table, 0.05, 0.95) == (4.0, 94.0)
    floats = data.astype(float) + 0.5
    low, high = lh.quantile_range(floats, lh.finite_range(floats), None, 0.05, 0.95)
    assert low == pytest.approx(5.0, abs=0.6) and high == pytest.approx(94.5, abs=0.6)


def test_smoothing_keeps_the_area():
    values = np.zeros(101)
    values[50] = 30.0
    smoothed = lh.smooth(values)
    assert smoothed.sum() == pytest.approx(30.0) and smoothed.argmax() == 50 and smoothed[50] < 30.0


def test_csv_table():
    edges = np.array([0.0, 1.0, 2.0])
    header, rows = lh.csv_table(edges, [("Layer 1: CT", np.array([3, 4]), None, ""),
                                        ("Layer 2: RTDOSE", np.array([1, 0]), np.array([100.0, 0.0]), "(% of voxels)")])
    assert header == ["bin_start", "bin_end", "bin_center", "Layer 1: CT voxels", "Layer 2: RTDOSE voxels",
                      "Layer 2: RTDOSE (% of voxels)"]
    assert rows == [[0.0, 1.0, 0.5, 3, 1, 100.0], [1.0, 2.0, 1.5, 4, 0, 0.0]]
