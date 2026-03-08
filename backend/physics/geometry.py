"""
Limb-darkening law.

Linear limb darkening: I(μ) = 1 − u·(1 − μ).
Additional laws (quadratic, power-2) can be added here later.
"""

import numpy as np
from numpy.typing import NDArray


def limb_darkening_linear(mu: NDArray[np.floating], u: float) -> NDArray[np.floating]:
    """Return intensity weight for each pixel given its μ value."""
    return 1.0 - u * (1.0 - mu)
