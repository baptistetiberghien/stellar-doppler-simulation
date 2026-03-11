"""
FastAPI application — Stellar Doppler Simulation backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models.params import AdvancedSimulationParams, SimulationParams, SimulationResult
from .physics.simulation import run_simulation
from .physics.simulation_advanced import run_advanced_simulation

app = FastAPI(
    title="Stellar Doppler Simulation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/simulate", response_model=SimulationResult)
async def simulate(params: SimulationParams) -> SimulationResult:
    return run_simulation(params)


@app.post("/simulate-advanced", response_model=SimulationResult)
async def simulate_advanced(params: AdvancedSimulationParams) -> SimulationResult:
    return run_advanced_simulation(params)
