"""
Projected rotation velocity field.

Solid-body rotation: v_proj(x) = −v_eq · sin(i) · x.
Differential rotation can be added as an alternative function later.
"""

import numpy as np
from numpy.typing import NDArray


def solid_body_velocity(
    xx: NDArray[np.floating],
    inc_deg: float,
    veq: float,
) -> NDArray[np.floating]:
    """Compute projected LOS velocity for each pixel (km/s)."""
    inc = np.deg2rad(inc_deg)
    return -veq * np.sin(inc) * xx
