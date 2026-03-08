"""
Local spectral line profile.

Each surface element emits a Gaussian absorption line centered at
λ₀ + Δλ where Δλ = λ₀·(v/c) is the Doppler shift.
"""

import numpy as np
from numpy.typing import NDArray

C_KMS = 299792.458  # speed of light in km/s


def gaussian_line(
    wavelength: NDArray[np.floating],
    lambda0: float,
    v_los: float,
    depth: float,
    sigma: float,
) -> NDArray[np.floating]:
    """Return the local line profile (normalised to continuum = 1)."""
    shift = lambda0 * (v_los / C_KMS)
    center = lambda0 + shift
    return 1.0 - depth * np.exp(-0.5 * ((wavelength - center) / sigma) ** 2)


def gaussian_line_batch(
    wavelength: NDArray[np.floating],
    lambda0: float,
    v_los_array: NDArray[np.floating],
    depth: float,
    sigma: float,
) -> NDArray[np.floating]:
    """Vectorised: compute profiles for many pixels at once.

    wavelength : shape (M,)
    v_los_array: shape (N,)  — one velocity per visible pixel
    Returns     : shape (N, M)
    """
    shifts = lambda0 * (v_los_array / C_KMS)          # (N,)
    centers = lambda0 + shifts                          # (N,)
    diff = wavelength[np.newaxis, :] - centers[:, np.newaxis]  # (N, M)
    return 1.0 - depth * np.exp(-0.5 * (diff / sigma) ** 2)
