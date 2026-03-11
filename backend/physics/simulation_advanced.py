"""
Advanced simulation: spot modifies both photometric weight AND local line depth.

Simple model (simulation.py):
    - spot pixels have weight = 0 (dark mask)
    - all pixels use the same line_depth

Advanced model (this file):
    - spot pixels have weight = base_weight * spot_contrast
    - photosphere pixels use line_depth
    - spot pixels use spot_line_depth
    → the two effects (photometric contrast vs spectral signature) are separated.
"""

import numpy as np

from ..models.params import AdvancedSimulationParams, SimulationResult
from .activity import active_region_mask
from .geometry import limb_darkening_linear
from .grid import StellarGrid
from .line_profile import gaussian_line_batch
from .rotation import solid_body_velocity

_grid_cache: dict[int, StellarGrid] = {}


def _get_grid(n: int) -> StellarGrid:
    if n not in _grid_cache:
        _grid_cache[n] = StellarGrid(n)
    return _grid_cache[n]


def run_advanced_simulation(params: AdvancedSimulationParams) -> SimulationResult:
    grid = _get_grid(params.n_grid)

    intensity = np.zeros_like(grid.xx)
    intensity[grid.visible] = limb_darkening_linear(grid.mu[grid.visible], params.limb_darkening)

    vmap = solid_body_velocity(grid.xx, params.inclination_deg, params.veq)
    weight = intensity.copy()

    spot_mask, sx, sy, spot_vis = active_region_mask(
        grid.xx, grid.yy, grid.visible,
        lon_deg=params.spot_lon_deg,
        lat_deg=params.spot_lat_deg,
        radius=params.spot_radius,
        inc_deg=params.inclination_deg,
    )

    # Photometric contrast: spot pixels are dimmed (or brightened) by spot_contrast
    weight[spot_mask] *= params.spot_contrast

    half_range = max(0.12, params.veq * params.lambda0 / 299792.458 * 1.5 + 4 * params.line_sigma)
    wavelength = np.linspace(
        params.lambda0 - half_range,
        params.lambda0 + half_range,
        800,
    )

    # Build per-pixel line depth array: photosphere vs spot
    vis_mask = grid.visible
    depth_map = np.full_like(grid.xx, params.line_depth)
    depth_map[spot_mask] = params.spot_line_depth

    w_vis = weight[vis_mask]
    v_vis = vmap[vis_mask]
    d_vis = depth_map[vis_mask]

    # Normalise by the total continuum (weighted by photometric contribution)
    flux_cont = float(np.sum(w_vis))
    if flux_cont == 0:
        flux_cont = 1.0

    # Vectorised integration with per-pixel depth
    # For each pixel i: profile_i(λ) = 1 - d_i * exp(-0.5 * ((λ - λ_i)/σ)²)
    # Weighted sum: F(λ) = Σ w_i * profile_i(λ) / Σ w_i
    from .line_profile import C_KMS

    shifts = params.lambda0 * (v_vis / C_KMS)
    centers = params.lambda0 + shifts
    diff = wavelength[np.newaxis, :] - centers[:, np.newaxis]   # (N, M)
    gauss = np.exp(-0.5 * (diff / params.line_sigma) ** 2)     # (N, M)

    # Per-pixel profiles: 1 - depth_i * gauss_i
    profiles = 1.0 - d_vis[:, np.newaxis] * gauss               # (N, M)
    profile = np.dot(w_vis, profiles) / flux_cont                # (M,)

    return SimulationResult(
        wavelength=wavelength.tolist(),
        flux=profile.tolist(),
        spot_x=sx if spot_vis else None,
        spot_y=sy if spot_vis else None,
        spot_visible=spot_vis,
    )
