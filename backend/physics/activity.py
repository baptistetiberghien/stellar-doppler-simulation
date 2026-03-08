"""
Active region (spot) modelling.

A circular spot is placed at given (longitude, latitude) on the stellar sphere,
then projected onto the visible disk. Only the flux-masking effect is applied
in V1 (no convective shift, no facular brightening).

Extension points:
  - multiple regions: iterate over a list of SpotConfig
  - faculae: add a brightening ring around the spot
  - convective_shift: per-region velocity offset
  - flux_contrast modulation with μ
"""

import numpy as np
from numpy.typing import NDArray


def spot_projection(
    lon_deg: float,
    lat_deg: float,
    inc_deg: float,
) -> tuple[float, float, float]:
    """Project a point (lon, lat) on the sphere onto the observer plane.

    Convention: inc_deg is the standard astronomical inclination —
      i = 0°  → pole-on  (observer looks along the rotation axis)
      i = 90° → equator-on (observer looks perpendicular to the axis)

    Returns (x_proj, y_proj, z_proj) where z_proj > 0 means visible.
    """
    lon = np.deg2rad(lon_deg)
    lat = np.deg2rad(lat_deg)
    inc = np.deg2rad(inc_deg)

    # Cartesian in the stellar frame (ys = rotation axis = North Pole)
    xs = np.cos(lat) * np.sin(lon)
    ys = np.sin(lat)
    zs = np.cos(lat) * np.cos(lon)

    # Rotate so that the observer's LOS (z_proj) aligns with the
    # direction at angle i from the pole:
    #   i=0°  → LOS along pole  → z_proj = ys
    #   i=90° → LOS along equator → z_proj = zs
    x_proj = xs
    y_proj = ys * np.sin(inc) - zs * np.cos(inc)
    z_proj = ys * np.cos(inc) + zs * np.sin(inc)
    return float(x_proj), float(y_proj), float(z_proj)


def active_region_mask(
    xx: NDArray[np.floating],
    yy: NDArray[np.floating],
    visible: NDArray[np.bool_],
    lon_deg: float,
    lat_deg: float,
    radius: float,
    inc_deg: float,
) -> tuple[NDArray[np.bool_], float, float, bool]:
    """Return a boolean mask of pixels covered by the spot.

    Also returns the projected (x, y) center and a visibility flag.
    """
    x_proj, y_proj, z_proj = spot_projection(lon_deg, lat_deg, inc_deg)

    if z_proj <= 0:
        return np.zeros_like(xx, dtype=bool), x_proj, y_proj, False

    dist2 = (xx - x_proj) ** 2 + (yy - y_proj) ** 2
    mask = (dist2 <= radius**2) & visible
    return mask, x_proj, y_proj, True
