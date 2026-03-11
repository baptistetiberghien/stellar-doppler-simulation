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


def _grid_to_sphere(
    xx: NDArray[np.floating],
    yy: NDArray[np.floating],
    visible: NDArray[np.bool_],
    inc_deg: float,
) -> tuple[NDArray[np.floating], NDArray[np.floating], NDArray[np.floating]]:
    """Convert projected-disk pixels back to 3D Cartesian on the unit sphere.

    The observer frame has:
      x_obs = xx  (sky-plane horizontal)
      y_obs = yy  (sky-plane vertical)
      z_obs = +sqrt(1 - xx² - yy²)  (toward observer)

    We then undo the inclination rotation to get stellar-frame (xs, ys, zs).
    """
    z_obs = np.zeros_like(xx)
    rr2 = xx[visible] ** 2 + yy[visible] ** 2
    z_obs[visible] = np.sqrt(np.clip(1.0 - rr2, 0.0, None))

    inc = np.deg2rad(inc_deg)
    # Inverse of the forward rotation applied in spot_projection
    xs = xx
    ys = yy * np.sin(inc) + z_obs * np.cos(inc)
    zs = -yy * np.cos(inc) + z_obs * np.sin(inc)
    return xs, ys, zs


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

    The spot is a spherical cap of angular radius `radius` (in radians)
    centered at (lon_deg, lat_deg). For each visible pixel we recover
    its 3D position on the sphere and compute the angular separation
    to the spot center — this gives correct foreshortening at the limb.

    Also returns the projected (x, y) center and a visibility flag.
    """
    x_proj, y_proj, z_proj = spot_projection(lon_deg, lat_deg, inc_deg)

    if z_proj <= 0:
        return np.zeros_like(xx, dtype=bool), x_proj, y_proj, False

    # Spot center in stellar-frame Cartesian
    lon = np.deg2rad(lon_deg)
    lat = np.deg2rad(lat_deg)
    cx = np.cos(lat) * np.sin(lon)
    cy = np.sin(lat)
    cz = np.cos(lat) * np.cos(lon)

    # Recover 3D positions for every visible pixel
    xs, ys, zs = _grid_to_sphere(xx, yy, visible, inc_deg)

    # Angular separation via dot product: cos(θ) = xs·cx + ys·cy + zs·cz
    dot = xs * cx + ys * cy + zs * cz
    # radius is given in stellar radii on the projected disk;
    # convert to an angular threshold: cos(angular_radius)
    ang_radius = np.arcsin(np.clip(radius, 0.0, 1.0))
    cos_threshold = np.cos(ang_radius)

    mask = (dot >= cos_threshold) & visible
    return mask, x_proj, y_proj, True
