"""
Bilinear/polynomial (ratio, infill) -> RED surface fitting for the
"3D printing -> View and Fit" tab's 3D Plotly view.

Pure-logic helpers only (no Qt) so they can be unit tested / reused
independently of the GUI. Table/cache access needed to look up reference
Zeff values still takes the main window `self` as a parameter, mirroring
the convention used throughout fcn_init/create_3D_database_tab.py.
"""

import numpy as np
import plotly.graph_objects as go


class InsufficientDataError(Exception):
    """Raised when there isn't enough data to fit the requested surface/curve."""
    pass


def safe_float(s, default=0.0):
    try:
        cleaned = "".join(ch for ch in str(s) if ch.isdigit() or ch in ['.', ',', '-', '+']).replace(',', '.')
        return float(cleaned) if cleaned else default
    except (ValueError, TypeError):
        return default


def extract_ratio_infill_red_dataset(self, mix_id):
    """
    Pulls every mix_red combo for `mix_id` and returns a flat dataset of
    (ratio, infill, red, zeff, tower_label) points, using the same row-index
    mapping already used for "mix_red" rows in update_fit_graph_and_calculators
    (Infill % = row[0], RED = row[6], Zeff = row[9]).

    Ratio is defined as the percentage of the last material listed in the mix
    (combo["percentage"][-1]), so this supports mixes with any number of
    components, not just binary ones.
    """
    from fcn_init.create_3D_database_tab import find_mix_group_row_and_size, get_materials_in_mix, format_ratio_string

    start_row, group_size = find_mix_group_row_and_size(self, mix_id)
    mat_names = get_materials_in_mix(self, start_row, group_size) if start_row != -1 else []
    ratio_label = mat_names[-1] if mat_names else "Ratio"

    combos = self.mix_red_cache.get(mix_id, [])
    points = []
    for combo in combos:
        percentages = combo.get("percentage", [])
        if not percentages:
            continue
        ratio = safe_float(percentages[-1])
        tower_label = format_ratio_string(mat_names, percentages) if mat_names else f"Ratio {ratio:g}%"

        for row_vals in combo.get("rows", []):
            if len(row_vals) < 14:
                continue
            infill = safe_float(row_vals[0])
            red = safe_float(row_vals[6])
            zeff = safe_float(row_vals[9])
            if infill <= 0.0 or red <= 0.0:
                continue
            points.append({
                "ratio": ratio,
                "infill": infill,
                "red": red,
                "zeff": zeff if zeff > 0.0 else None,
                "tower": tower_label,
                "percentages": percentages,
            })

    return {
        "points": points,
        "mat_names": mat_names,
        "ratio_label": ratio_label,
    }


def _tensor_design_matrix(ratio, infill, degree):
    ratio = np.asarray(ratio, dtype=float)
    infill = np.asarray(infill, dtype=float)
    terms = []
    powers = []
    for i in range(degree + 1):
        for j in range(degree + 1):
            terms.append((ratio ** i) * (infill ** j))
            powers.append((i, j))
    return np.column_stack(terms), powers


def fit_poly_surface(ratio, infill, red, degree):
    """
    Tensor-product polynomial fit RED ~ sum_ij c_ij * ratio^i * infill^j,
    i,j in 0..degree (degree=1 reproduces the reference HTML's 4-term
    bilinear form, including the cross term).

    Returns a dict with coeffs/powers, a predict(ratio, infill) callable,
    r2, rmse, loocv_mean, loocv_max (leave-one-out % error).
    Raises InsufficientDataError if there aren't enough points to fit.
    """
    ratio_arr = np.asarray(ratio, dtype=float)
    infill_arr = np.asarray(infill, dtype=float)
    red_arr = np.asarray(red, dtype=float)

    valid = np.isfinite(ratio_arr) & np.isfinite(infill_arr) & np.isfinite(red_arr)
    ratio_arr, infill_arr, red_arr = ratio_arr[valid], infill_arr[valid], red_arr[valid]

    A, powers = _tensor_design_matrix(ratio_arr, infill_arr, degree)
    n_features = A.shape[1]
    n_points = A.shape[0]
    if n_points <= n_features:
        raise InsufficientDataError(
            f"Not enough data points for a degree-{degree} surface fit: "
            f"need more than {n_features} points (have {n_points})."
        )

    coeffs, *_ = np.linalg.lstsq(A, red_arr, rcond=None)

    def predict(r, i):
        A_pred, _ = _tensor_design_matrix(np.atleast_1d(r), np.atleast_1d(i), degree)
        return A_pred @ coeffs

    y_pred = A @ coeffs
    y_mean = np.mean(red_arr)
    ss_res = np.sum((red_arr - y_pred) ** 2)
    ss_tot = np.sum((red_arr - y_mean) ** 2)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 1.0
    rmse = float(np.sqrt(np.mean((red_arr - y_pred) ** 2)))

    loocv_errs = []
    for idx in range(n_points):
        mask = np.ones(n_points, dtype=bool)
        mask[idx] = False
        try:
            coeffs_loo, *_ = np.linalg.lstsq(A[mask], red_arr[mask], rcond=None)
        except np.linalg.LinAlgError:
            continue
        y_loo = A[idx] @ coeffs_loo
        actual = red_arr[idx]
        if actual != 0:
            loocv_errs.append(abs(y_loo - actual) / abs(actual) * 100.0)

    loocv_mean = float(np.mean(loocv_errs)) if loocv_errs else float("nan")
    loocv_max = float(np.max(loocv_errs)) if loocv_errs else float("nan")

    return {
        "degree": degree,
        "coeffs": coeffs,
        "powers": powers,
        "predict": predict,
        "r2": r2,
        "rmse": rmse,
        "loocv_mean": loocv_mean,
        "loocv_max": loocv_max,
        "n_points": n_points,
    }


def format_surface_equation(fit):
    terms = []
    for (i, j), coef in zip(fit["powers"], fit["coeffs"]):
        if abs(coef) < 1e-6:
            continue
        label = "1" if i == 0 and j == 0 else ""
        if i == 1:
            label += "ratio"
        elif i > 1:
            label += f"ratio^{i}"
        if j == 1:
            label += "infill" if not label else "·infill"
        elif j > 1:
            label += f"infill^{j}" if not label else f"·infill^{j}"
        terms.append(f"{coef:+.6g}·{label}" if label else f"{coef:+.6g}")
    return "RED = " + " ".join(terms) if terms else "RED = 0"


def estimate_zeff_vs_ratio(ratio, zeff):
    """
    Fits measured Zeff vs. ratio (pooled across infill), trying degree 1 and
    degree 2 polyfits and picking whichever has the lower LOOCV mean error
    (ties favor the simpler, degree-1 fit). Returns None if there aren't at
    least 2 distinct ratios with usable Zeff data.
    """
    ratio_arr = np.asarray(ratio, dtype=float)
    zeff_arr = np.asarray(zeff, dtype=float)
    valid = np.isfinite(ratio_arr) & np.isfinite(zeff_arr) & (zeff_arr > 0)
    ratio_arr, zeff_arr = ratio_arr[valid], zeff_arr[valid]

    distinct_ratios = np.unique(ratio_arr)
    if len(distinct_ratios) < 2:
        return None

    candidate_degrees = [1]
    if len(distinct_ratios) >= 3:
        candidate_degrees.append(2)

    best = None
    for degree in candidate_degrees:
        n_points = len(ratio_arr)
        if n_points <= degree:
            continue
        coefs = np.polyfit(ratio_arr, zeff_arr, degree)

        loocv_errs = []
        for idx in range(n_points):
            mask = np.ones(n_points, dtype=bool)
            mask[idx] = False
            if np.sum(mask) <= degree:
                continue
            coefs_loo = np.polyfit(ratio_arr[mask], zeff_arr[mask], degree)
            y_loo = np.poly1d(coefs_loo)(ratio_arr[idx])
            actual = zeff_arr[idx]
            if actual != 0:
                loocv_errs.append(abs(y_loo - actual) / abs(actual) * 100.0)
        loocv_mean = float(np.mean(loocv_errs)) if loocv_errs else float("inf")

        p = np.poly1d(coefs)
        y_pred = p(ratio_arr)
        y_mean = np.mean(zeff_arr)
        ss_res = np.sum((zeff_arr - y_pred) ** 2)
        ss_tot = np.sum((zeff_arr - y_mean) ** 2)
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 1.0

        candidate = {
            "degree": degree,
            "coefs": coefs,
            "predict": p,
            "r2": r2,
            "loocv_mean": loocv_mean,
        }
        if best is None or loocv_mean < best["loocv_mean"] - 1e-9:
            best = candidate

    return best


def get_mix_component_reference_zeffs(self, mix_id, mat_names):
    """
    Reference Zeff per mix component, read from the MatMix top table first
    (column 4), falling back to the main material database (column 8) - same
    lookup precedence used by calculate_predicted_values() in
    fcn_init/create_3D_database_tab.py, but decoupled from
    self.current_viewed_mix_id so it can be used for any mix by id.
    """
    from fcn_3DPrinting.material_props import get_mix_components

    components = get_mix_components(self, mix_id)
    if not components:
        return [0.0] * len(mat_names)
    return [c["zeff"].value for c in components]


def estimate_zeff_powerlaw(self, mix_id, mat_names):
    """
    Mayneord power-law mixing rule: Zeff = (sum_i Zeff_i^m * frac_i)^(1/m),
    using each component's reference Zeff and the mix's configured m-value
    (default 3.4), matching the formula already used elsewhere in the app
    for MatMix Zeff predictions.
    """
    m = self.mix_m_value_cache.get(mix_id, 3.4) if hasattr(self, "mix_m_value_cache") else 3.4
    ref_zeffs = get_mix_component_reference_zeffs(self, mix_id, mat_names)

    def predict(pct_list):
        term_sum = 0.0
        for zeff_i, pct_i in zip(ref_zeffs, pct_list):
            term_sum += (zeff_i ** m) * (pct_i / 100.0)
        return term_sum ** (1.0 / m) if m != 0 else 0.0

    return {"predict": predict, "m_value": m, "ref_zeffs": ref_zeffs}


def interpolate_percentages(points, ratio_query):
    """
    Interpolates each material's mixing percentage at an arbitrary ratio
    value from the discrete combos actually present in `points` (linear
    interpolation vs. ratio, per material index). Used to reconstruct a full
    percentage vector for the Mayneord power-law Zeff estimate at grid
    points that fall between measured ratio combos.
    """
    combos = {}
    for p in points:
        combos.setdefault(p["ratio"], p["percentages"])
    ratios_sorted = sorted(combos.keys())
    if not ratios_sorted:
        return []
    n_mats = len(combos[ratios_sorted[0]])
    result = []
    for i in range(n_mats):
        vals = [combos[r][i] if i < len(combos[r]) else 0.0 for r in ratios_sorted]
        result.append(float(np.interp(ratio_query, ratios_sorted, vals)))
    return result


FIGURES_COLOR_MAP = {
    "blue": "#3b82f6", "red": "#ef4444", "green": "#10b981", "orange": "#f59e0b",
    "purple": "#8b5cf6", "cyan": "#06b6d4", "yellow": "#eab308", "magenta": "#ec4899",
    "white": "#ffffff", "black": "#000000",
}

# Plotly's Scatter3d marker.symbol only supports this fixed set - no triangle/star in 3D,
# unlike the 2D matplotlib marker set the Figures menu was designed around, so those map
# to the closest available 3D symbol.
MARKER_SYMBOL_MAP = {
    "circle": "circle", "square": "square", "triangle": "diamond",
    "star": "cross", "none": "circle",
}


def resolve_figures_style(self):
    """
    Reads the app-wide "Figures" menu settings (fcn_init/create_menu.py) off the main
    window and resolves them into the concrete values build_plotly_figure() needs, using
    the same background/color conventions as the existing 2D matplotlib plots in this tab
    (see update_fit_graph_and_calculators / update_mix_graph).
    """
    background = getattr(self, "selected_background", "Transparent")
    if background.lower() == "white":
        bg, text_color, grid_color = "#ffffff", "#23201c", "#e5e7eb"
    else:
        bg, text_color, grid_color = "#1e1e24", "#e5e7eb", "#2b2b36"

    accent_color = FIGURES_COLOR_MAP.get(getattr(self, "selected_point_color", "Blue").lower(), "#3b82f6")
    marker_symbol = MARKER_SYMBOL_MAP.get(getattr(self, "selected_marker_type", "Circle").lower(), "circle")

    return {
        "bg": bg,
        "text_color": text_color,
        "grid_color": grid_color,
        "font_size": getattr(self, "selected_font_size", 14),
        "legend_font_size": getattr(self, "selected_legend_font_size", 14),
        "show_legend": getattr(self, "selected_legend_on_off", "On") == "On",
        "point_size": getattr(self, "selected_point_size", 8),
        "marker_symbol": marker_symbol,
        "line_width": getattr(self, "selected_line_width", 2.0),
        "accent_color": accent_color,
    }


DEFAULT_STYLE = {
    "bg": "#1e1e24", "text_color": "#e5e7eb", "grid_color": "#2b2b36",
    "font_size": 14, "legend_font_size": 14, "show_legend": True,
    "point_size": 8, "marker_symbol": "circle", "line_width": 2.0,
    "accent_color": "#3b82f6",
}


def build_plotly_figure(dataset, surface_fit, zeff_lookup, zeff_model_desc,
                         show_surface=True, show_points=True, style=None, grid_n=25):
    """
    Builds the 3D Plotly figure: fitted RED surface plus one scatter3d trace
    per tower (mixing ratio), with hover tooltips showing ratio/infill/
    predicted RED/Zeff. Returns the figure's standalone HTML (plotly.js
    bundled inline, so it renders fully offline in QWebEngineView).

    `zeff_lookup` is a callable ratio -> Zeff, or None if no Zeff estimate is
    available/wanted, in which case the surface is colored by predicted RED
    instead and Zeff is omitted from tooltips.

    `style` is a dict from resolve_figures_style() (or DEFAULT_STYLE) carrying
    the app's "Figures" menu settings (background, font sizes, legend on/off,
    point size/marker/accent color, line width), so this plot reflects the
    same look-and-feel controls as the rest of the app's figures.
    """
    style = {**DEFAULT_STYLE, **(style or {})}
    points = dataset["points"]
    ratio_label = dataset.get("ratio_label", "Ratio")

    ratios = [p["ratio"] for p in points]
    infills = [p["infill"] for p in points]

    ratio_grid = np.linspace(min(ratios), max(ratios), grid_n)
    infill_grid = np.linspace(min(infills), max(infills), grid_n)
    RR, II = np.meshgrid(ratio_grid, infill_grid)
    ZZ = surface_fit["predict"](RR.ravel(), II.ravel()).reshape(RR.shape)

    has_zeff = zeff_lookup is not None
    if has_zeff:
        zeff_by_ratio = {r: float(zeff_lookup(r)) for r in ratio_grid}
        color_grid = np.array([[zeff_by_ratio[r] for r in ratio_grid] for _ in infill_grid])
        colorbar_title = "Zeff"
        surface_hover = (f"{ratio_label} %{{x:.1f}}%<br>infill %{{y:.1f}}%<br>"
                          "predicted RED %{z:.4f}<br>est. Zeff %{customdata:.2f}<extra></extra>")
    else:
        color_grid = ZZ
        colorbar_title = "RED"
        surface_hover = (f"{ratio_label} %{{x:.1f}}%<br>infill %{{y:.1f}}%<br>"
                          "predicted RED %{z:.4f}<extra></extra>")

    traces = []
    if show_surface:
        traces.append(go.Surface(
            x=ratio_grid, y=infill_grid, z=ZZ,
            surfacecolor=color_grid,
            colorscale=[[0, "#3f6fb0"], [0.5, "#d9d3c2"], [1, "#c94f3a"]],
            opacity=0.72,
            showscale=True,
            colorbar=dict(title=colorbar_title, len=0.6, x=1.02, tickfont=dict(size=style["font_size"] - 2)),
            customdata=color_grid,
            hovertemplate=surface_hover,
            name="Fitted surface",
            contours=dict(z=dict(show=True, usecolormap=False, highlightcolor=style["text_color"],
                                  project=dict(z=False), width=max(1.0, style["line_width"]))),
        ))

    if show_points:
        towers = {}
        for p in points:
            towers.setdefault(p["tower"], []).append(p)
        default_colors = ["#ef4444", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#06b6d4", "#ec4899", "#eab308"]
        accent = style["accent_color"]
        color_list = [accent] + [c for c in default_colors if c != accent]
        for idx, (tower, pts) in enumerate(sorted(towers.items())):
            if has_zeff:
                customdata = [float(zeff_lookup(p["ratio"])) for p in pts]
                point_hover = (f"%{{text}}<br>{ratio_label} %{{x:.1f}}%<br>infill %{{y:.1f}}%<br>"
                                "measured RED %{z:.4f}<br>est. Zeff %{customdata:.2f}<extra></extra>")
            else:
                customdata = [0] * len(pts)
                point_hover = (f"%{{text}}<br>{ratio_label} %{{x:.1f}}%<br>infill %{{y:.1f}}%<br>"
                                "measured RED %{z:.4f}<extra></extra>")
            traces.append(go.Scatter3d(
                x=[p["ratio"] for p in pts],
                y=[p["infill"] for p in pts],
                z=[p["red"] for p in pts],
                mode="markers",
                name=tower,
                marker=dict(size=style["point_size"], symbol=style["marker_symbol"],
                            color=color_list[idx % len(color_list)],
                            line=dict(color=style["text_color"], width=min(2.0, style["line_width"] * 0.3))),
                customdata=customdata,
                text=[tower] * len(pts),
                hovertemplate=point_hover,
            ))

    layout = go.Layout(
        autosize=True,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor=style["bg"],
        plot_bgcolor=style["bg"],
        font=dict(color=style["text_color"], size=style["font_size"]),
        scene=dict(
            xaxis=dict(title=f"{ratio_label} (%)", backgroundcolor=style["bg"],
                       color=style["text_color"], gridcolor=style["grid_color"]),
            yaxis=dict(title="Infill (%)", backgroundcolor=style["bg"],
                       color=style["text_color"], gridcolor=style["grid_color"]),
            zaxis=dict(title="RED", backgroundcolor=style["bg"],
                       color=style["text_color"], gridcolor=style["grid_color"]),
            camera=dict(eye=dict(x=1.6, y=-1.6, z=0.9)),
        ),
        showlegend=style["show_legend"],
        legend=dict(orientation="h", y=-0.02, x=0, font=dict(size=style["legend_font_size"])),
        title=dict(text=f"RED vs {ratio_label} & Infill  |  Zeff model: {zeff_model_desc}",
                   font=dict(size=style["font_size"] + 1)),
    )

    fig = go.Figure(data=traces, layout=layout)
    return fig.to_html(full_html=True, include_plotlyjs="inline", config={"displaylogo": False})


def insufficient_data_html(message):
    return f"""
    <html><body style="background:#1e1e24;color:#e5e7eb;font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;
    display:flex;align-items:center;justify-content:center;height:100vh;margin:0;">
    <div style="max-width:480px;text-align:center;padding:20px;border:1px solid #3c4450;border-radius:8px;">
    {message}
    </div></body></html>
    """
