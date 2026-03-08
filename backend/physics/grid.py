"""
Stellar disk grid construction.

Builds a uniform Cartesian grid over the projected stellar disk (x² + y² ≤ 1)
and precomputes the μ = cos(θ) map needed by limb darkening and integration.
"""

import numpy as np
from numpy.typing import NDArray


class StellarGrid:
    """Immutable grid that can be reused across parameter changes."""

    def __init__(self, n: int = 101) -> None:
        coords = np.linspace(-1.0, 1.0, n)
        self.xx, self.yy = np.meshgrid(coords, coords)
        rr2 = self.xx**2 + self.yy**2
        self.visible: NDArray[np.bool_] = rr2 <= 1.0
        self.mu = np.zeros_like(self.xx)
        self.mu[self.visible] = np.sqrt(1.0 - rr2[self.visible])
        self.n = n
