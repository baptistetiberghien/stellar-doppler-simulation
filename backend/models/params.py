from pydantic import BaseModel, Field


class SimulationParams(BaseModel):
    """Parameters for a single simulation snapshot."""

    inclination_deg: float = Field(60.0, ge=0.0, le=90.0, description="Stellar rotation axis inclination (degrees)")
    veq: float = Field(10.0, ge=0.1, le=100.0, description="Equatorial rotation velocity (km/s)")
    spot_lat_deg: float = Field(25.0, ge=-90.0, le=90.0, description="Active region latitude (degrees)")
    spot_lon_deg: float = Field(0.0, ge=-180.0, le=360.0, description="Active region longitude (degrees)")
    spot_radius: float = Field(0.15, ge=0.01, le=0.5, description="Active region angular radius (stellar radii)")
    line_depth: float = Field(0.55, ge=0.01, le=1.0, description="Local spectral line depth")
    line_sigma: float = Field(0.005, ge=0.001, le=0.05, description="Local spectral line width (nm)")
    limb_darkening: float = Field(0.6, ge=0.0, le=1.0, description="Linear limb-darkening coefficient")
    lambda0: float = Field(550.0, ge=300.0, le=900.0, description="Rest wavelength (nm)")
    n_grid: int = Field(101, ge=31, le=301, description="Grid resolution (pixels per axis)")


class SimulationResult(BaseModel):
    """Result returned by a simulation call."""

    wavelength: list[float]
    flux: list[float]
    spot_x: float | None = None
    spot_y: float | None = None
    spot_visible: bool = False


class AdvancedSimulationParams(SimulationParams):
    """Extended parameters for the advanced model with per-spot line depth."""

    spot_line_depth: float = Field(0.55, ge=0.0, le=1.0, description="Spectral line depth inside the spot")
    spot_contrast: float = Field(0.65, ge=0.0, le=1.5, description="Photometric brightness of spot relative to photosphere")


class MultiSpotParams(BaseModel):
    """Parameters for the stochastic multi-spot model."""

    inclination_deg: float = Field(60.0, ge=0.0, le=90.0)
    veq: float = Field(10.0, ge=0.1, le=100.0)
    line_depth: float = Field(0.55, ge=0.01, le=1.0)
    line_sigma: float = Field(0.005, ge=0.001, le=0.05)
    limb_darkening: float = Field(0.6, ge=0.0, le=1.0)
    lambda0: float = Field(550.0, ge=300.0, le=900.0)
    n_grid: int = Field(101, ge=31, le=301)
    rotation_phase: float = Field(0.0, ge=0.0, le=1.0, description="Current rotation phase 0..1")

    n_spots: int = Field(5, ge=1, le=30)
    seed: int = Field(42, ge=0, le=999999)
    min_spot_radius: float = Field(0.05, ge=0.02, le=0.3)
    max_spot_radius: float = Field(0.18, ge=0.03, le=0.5)


class SpotInfo(BaseModel):
    """Projected position of a single spot (returned to frontend for display)."""
    lat_deg: float
    lon_deg: float
    radius: float
    x_proj: float
    y_proj: float
    visible: bool


class MultiSpotResult(BaseModel):
    """Result returned by the multi-spot simulation."""

    wavelength: list[float]
    flux: list[float]
    spots: list[SpotInfo]
