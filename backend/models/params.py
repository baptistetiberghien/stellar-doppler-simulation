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
