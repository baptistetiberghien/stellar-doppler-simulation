export interface SimulationParams {
  inclination_deg: number;
  veq: number;
  spot_lat_deg: number;
  spot_lon_deg: number;
  spot_radius: number;
  line_depth: number;
  line_sigma: number;
  limb_darkening: number;
  lambda0: number;
  n_grid: number;
}

export interface SimulationResult {
  wavelength: number[];
  flux: number[];
  spot_x: number | null;
  spot_y: number | null;
  spot_visible: boolean;
}

export interface AdvancedSimulationParams extends SimulationParams {
  spot_line_depth: number;
  spot_contrast: number;
}

export const DEFAULT_PARAMS: SimulationParams = {
  inclination_deg: 60,
  veq: 10,
  spot_lat_deg: 25,
  spot_lon_deg: 0,
  spot_radius: 0.15,
  line_depth: 0.55,
  line_sigma: 0.005,
  limb_darkening: 0.6,
  lambda0: 550,
  n_grid: 101,
};

export const DEFAULT_ADVANCED_PARAMS: AdvancedSimulationParams = {
  ...DEFAULT_PARAMS,
  spot_line_depth: 0.55,
  spot_contrast: 0.65,
};

// ── Multi-spot stochastic model ──

export interface MultiSpotParams {
  inclination_deg: number;
  veq: number;
  line_depth: number;
  line_sigma: number;
  limb_darkening: number;
  lambda0: number;
  n_grid: number;
  rotation_phase: number;
  n_spots: number;
  seed: number;
  min_spot_radius: number;
  max_spot_radius: number;
}

export interface SpotInfo {
  lat_deg: number;
  lon_deg: number;
  radius: number;
  x_proj: number;
  y_proj: number;
  visible: boolean;
}

export interface MultiSpotResult {
  wavelength: number[];
  flux: number[];
  spots: SpotInfo[];
}

export const DEFAULT_MULTISPOT_PARAMS: MultiSpotParams = {
  inclination_deg: 60,
  veq: 10,
  line_depth: 0.55,
  line_sigma: 0.005,
  limb_darkening: 0.6,
  lambda0: 550,
  n_grid: 101,
  rotation_phase: 0,
  n_spots: 5,
  seed: 42,
  min_spot_radius: 0.05,
  max_spot_radius: 0.18,
};
