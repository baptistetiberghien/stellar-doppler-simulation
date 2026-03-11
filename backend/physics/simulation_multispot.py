"""
Stochastic multi-spot simulation.

Generates N spots randomly on the stellar surface using a reproducible seed,
then computes the integrated spectrum with all spots acting as dark masks.
The spot positions rotate rigidly with the star via rotation_phase.
"""

import numpy as np

from ..models.params import MultiSpotParams, MultiSpotResult, SpotInfo
from .activity import active_region_mask, spot_projection
from .geometry import limb_darkening_linear
from .grid import StellarGrid
from .line_profile import gaussian_line_batch
from .rotation import solid_body_velocity

_grid_cache: dict[int, StellarGrid] = {}


def _get_grid(n: int) -> StellarGrid:
    if n not in _grid_cache:
        _grid_cache[n] = StellarGrid(n)
    return _grid_cache[n]


def _generate_spots(
    n_spots: int,
    seed: int,
    min_r: float,
    max_r: float,
) -> list[dict]:
    """Generate a random spot population on the unit sphere.

    Longitude: uniform in [0, 360).
    Latitude:  from uniform cos(theta) to avoid polar bias.
               theta = arccos(u) with u uniform in [-1, 1],
               then latitude = 90 - theta (degrees).
    Radius:    uniform in [min_r, max_r].
    """
    rng = np.random.default_rng(seed)

    lons = rng.uniform(0, 360, n_spots)

    # Uniform distribution on the sphere: sample cos(colatitude) uniformly
    cos_colat = rng.uniform(-1, 1, n_spots)
    lats = np.rad2deg(np.arcsin(cos_colat))  # arcsin(cos_colat) = latitude

    radii = rng.uniform(min_r, max_r, n_spots)

    return [
        {"lat_deg": float(lats[i]), "lon_deg": float(lons[i]), "radius": float(radii[i])}
        for i in range(n_spots)
    ]


def run_multispot_simulation(params: MultiSpotParams) -> MultiSpotResult:
    grid = _get_grid(params.n_grid)

    intensity = np.zeros_like(grid.xx)
    intensity[grid.visible] = limb_darkening_linear(grid.mu[grid.visible], params.limb_darkening)

    vmap = solid_body_velocity(grid.xx, params.inclination_deg, params.veq)
    weight = intensity.copy()

    # Generate the spot population (deterministic for a given seed)
    spot_configs = _generate_spots(
        params.n_spots, params.seed,
        params.min_spot_radius, params.max_spot_radius,
    )

    # Apply rotation phase: shift all longitudes by phase * 360°
    phase_offset = params.rotation_phase * 360.0

    spot_infos: list[SpotInfo] = []
    combined_mask = np.zeros_like(grid.xx, dtype=bool)

    for cfg in spot_configs:
        lon = cfg["lon_deg"] + phase_offset
        # Normalise to [0, 360)
        lon = lon % 360.0

        mask, sx, sy, vis = active_region_mask(
            grid.xx, grid.yy, grid.visible,
            lon_deg=lon,
            lat_deg=cfg["lat_deg"],
            radius=cfg["radius"],
            inc_deg=params.inclination_deg,
        )
        combined_mask |= mask

        spot_infos.append(SpotInfo(
            lat_deg=cfg["lat_deg"],
            lon_deg=lon,
            radius=cfg["radius"],
            x_proj=sx,
            y_proj=sy,
            visible=vis,
        ))

    # All spotted pixels become dark
    weight[combined_mask] *= 0.0

    half_range = max(0.12, params.veq * params.lambda0 / 299792.458 * 1.5 + 4 * params.line_sigma)
    wavelength = np.linspace(
        params.lambda0 - half_range,
        params.lambda0 + half_range,
        800,
    )

    w_vis = weight[grid.visible]
    v_vis = vmap[grid.visible]

    flux_cont = float(np.sum(w_vis))
    if flux_cont == 0:
        flux_cont = 1.0

    profiles = gaussian_line_batch(wavelength, params.lambda0, v_vis, params.line_depth, params.line_sigma)
    profile = np.dot(w_vis, profiles) / flux_cont

    return MultiSpotResult(
        wavelength=wavelength.tolist(),
        flux=profile.tolist(),
        spots=spot_infos,
    )
