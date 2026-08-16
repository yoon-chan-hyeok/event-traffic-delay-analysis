"""Simple capacity arithmetic for a shuttle operating scenario."""

from __future__ import annotations

from typing import Any


def shuttle_capacity(
    *,
    seats_per_bus: int,
    buses: int,
    rotations: int,
    load_factor: float = 1.0,
    demand: int | None = None,
    cost_per_bus: float | None = None,
) -> dict[str, Any]:
    """Return passenger-movement capacity and optional demand/cost comparisons."""
    if seats_per_bus <= 0 or buses <= 0 or rotations <= 0:
        raise ValueError("seats_per_bus, buses and rotations must be positive")
    if not 0 < load_factor <= 1:
        raise ValueError("load_factor must be greater than 0 and at most 1")
    if demand is not None and demand < 0:
        raise ValueError("demand must be non-negative")
    if cost_per_bus is not None and cost_per_bus < 0:
        raise ValueError("cost_per_bus must be non-negative")

    capacity = int(seats_per_bus * buses * rotations * load_factor)
    result: dict[str, Any] = {
        "seats_per_bus": seats_per_bus,
        "buses": buses,
        "rotations": rotations,
        "load_factor": load_factor,
        "passenger_movements": capacity,
    }
    if demand is not None:
        result["demand"] = demand
        result["capacity_minus_demand"] = capacity - demand
        result["coverage_ratio"] = capacity / demand if demand else None
    if cost_per_bus is not None:
        result["fleet_cost"] = buses * cost_per_bus
    return result
