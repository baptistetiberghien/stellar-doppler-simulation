"""
Top-level simulation: assembles grid, physics, and integration.

This is the only module the API layer calls directly.
All heavy lifting is numpy-vectorised (no Python pixel loops).
"""

import numpy as np

from ..models.params import SimulationParams, SimulationResult
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


def run_simulation(params: SimulationParams) -> SimulationResult:
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
    weight[spot_mask] *= 0.0

    half_range = max(0.12, params.veq * params.lambda0 / 299792.458 * 1.5 + 4 * params.line_sigma)
    wavelength = np.linspace(
        params.lambda0 - half_range,
        params.lambda0 + half_range,
        800,
    )

    w_vis = weight[grid.visible]                       # (N,)
    v_vis = vmap[grid.visible]                         # (N,)

    flux_cont = float(np.sum(w_vis))
    if flux_cont == 0:
        flux_cont = 1.0

    # Fully vectorised: profiles shape (N, M), weighted sum in one go
    profiles = gaussian_line_batch(wavelength, params.lambda0, v_vis, params.line_depth, params.line_sigma)
    profile = np.dot(w_vis, profiles) / flux_cont      # (M,)

    return SimulationResult(
        wavelength=wavelength.tolist(),
        flux=profile.tolist(),
        spot_x=sx if spot_vis else None,
        spot_y=sy if spot_vis else None,
        spot_visible=spot_vis,
    )
