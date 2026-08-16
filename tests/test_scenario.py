import pytest

from event_traffic.scenario import shuttle_capacity


def test_capacity_matches_portfolio_scenario():
    result = shuttle_capacity(
        seats_per_bus=45,
        buses=100,
        rotations=3,
        demand=13_000,
        cost_per_bus=500_000,
    )
    assert result["passenger_movements"] == 13_500
    assert result["capacity_minus_demand"] == 500
    assert result["fleet_cost"] == 50_000_000


def test_invalid_load_factor_is_rejected():
    with pytest.raises(ValueError):
        shuttle_capacity(seats_per_bus=45, buses=100, rotations=3, load_factor=1.2)
