"""
FastAPI application — Stellar Doppler Simulation backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models.params import (
    AdvancedSimulationParams,
    MultiSpotParams,
    MultiSpotResult,
    SimulationParams,
    SimulationResult,
)
from .physics.simulation import run_simulation
from .physics.simulation_advanced import run_advanced_simulation
from .physics.simulation_multispot import run_multispot_simulation

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


@app.post("/simulate-multispot", response_model=MultiSpotResult)
async def simulate_multispot(params: MultiSpotParams) -> MultiSpotResult:
    return run_multispot_simulation(params)
