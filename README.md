# Stellar Doppler Simulation

Interactive web application for visualising a simplified model of a rotating star with surface activity and its effect on an integrated spectral line profile. Inspired by Doppler imaging techniques used in stellar astrophysics.

## Architecture

```
stellar-doppler-simulation/
├── backend/                  # Python / FastAPI
│   ├── main.py               # FastAPI app, CORS, /simulate endpoint
│   ├── models/
│   │   └── params.py         # Pydantic request/response schemas
│   └── physics/
│       ├── grid.py           # Stellar disk grid (x² + y² ≤ 1)
│       ├── geometry.py       # Limb-darkening law
│       ├── rotation.py       # Projected rotation velocity field
│       ├── line_profile.py   # Local Gaussian absorption line + Doppler shift
│       ├── activity.py       # Active region (spot) projection & masking
│       └── simulation.py     # Integration: assembles everything, returns spectrum
├── frontend/                 # Vue 3 / TypeScript / Vite
│   └── src/
│       ├── App.vue           # Root layout (star | spectrum)
│       ├── components/
│       │   ├── StarView.vue      # SVG stellar disk visualisation
│       │   ├── SpectrumPlot.vue  # Canvas spectral line plot
│       │   └── ControlsPanel.vue # Sliders + Play/Pause animation
│       ├── composables/
│       │   └── useSimulation.ts  # Reactive fetch to backend API
│       └── types/
│           └── simulation.ts     # TypeScript interfaces
```

## Physics model (V1 — simplified)

| Concept | Formula |
|---|---|
| Stellar disk | Projected unit disk: x² + y² ≤ 1 |
| μ angle | μ = √(1 − x² − y²) |
| Limb darkening | I(μ) = 1 − u·(1 − μ) |
| Projected velocity | v(x) = −v\_eq · sin(i) · x |
| Local line profile | Gaussian: 1 − A·exp(−(λ − λ₀ − Δλ)² / 2σ²) |
| Doppler shift | Δλ = λ₀ · v / c |
| Spot effect | Zero flux inside the spot (dark mask) |
| Integrated spectrum | Σ weight(pixel) × local\_profile(pixel), normalised by Σ weight |

## Running

### Backend

```bash
cd backend
pip install -r requirements.txt
cd ..
python -m uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend proxies `/simulate` to `http://localhost:8000` via Vite's dev server.

Open http://localhost:5173 in your browser.

## Controls

- **Inclination** — rotation axis tilt (0° = pole-on, 90° = equator-on)
- **v\_eq** — equatorial rotation velocity (km/s)
- **Spot latitude / longitude** — position of the active region
- **Spot radius** — angular size of the spot
- **Line width σ** — intrinsic Gaussian width of the spectral line
- **Line depth** — depth of the absorption line
- **Play / Pause** — animates the spot longitude to simulate stellar rotation

## Extension points

The backend is designed for future additions:

- Multiple active regions (loop over a list in `simulation.py`)
- Convective blueshift (per-pixel velocity offset)
- Facular brightening (flux contrast > 1 around spots)
- Differential rotation (latitude-dependent v\_eq in `rotation.py`)
- Quadratic / power-2 limb darkening (add to `geometry.py`)
