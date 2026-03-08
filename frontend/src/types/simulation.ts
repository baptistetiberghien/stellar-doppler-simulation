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
