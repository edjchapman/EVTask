import pytest

from src.config import BATTERY_CAPACITY_KWH
from src.domain.battery import (
    calculate_charge_added,
    initialize_battery_state,
    project_battery_state,
)
from src.domain.models import BatteryState, ChargerState


def test_initialize_battery_state():
    """Test initialization of battery state with default values."""
    battery_state = initialize_battery_state()

    assert isinstance(battery_state, BatteryState)
    assert 0.0 <= battery_state.current_soc <= 1.0
    assert battery_state.target_soc == 0.8  # Default target


def test_calculate_charge_added():
    """Test calculation of charge added based on rate and duration."""
    # Test with 7kW for 1 hour
    charge_rate = 7.0  # kW
    duration = 1.0  # hour

    added = calculate_charge_added(charge_rate, duration)

    # Expected: (7kW * 1h) / BATTERY_CAPACITY_KWH
    expected = (charge_rate * duration) / BATTERY_CAPACITY_KWH
    assert added == pytest.approx(expected)

    # Test with different values
    assert calculate_charge_added(3.5, 0.5) == pytest.approx(
        (3.5 * 0.5) / BATTERY_CAPACITY_KWH
    )


def test_project_battery_state_no_charging():
    """Test battery state projection when not charging."""
    initial_state = BatteryState(current_soc=0.6, target_soc=0.8)
    charger_state = ChargerState(car_is_charging=False, charge_is_override=False)

    projected = project_battery_state(initial_state, charger_state, 1.0)

    # When not charging, SOC should remain the same
    assert projected.current_soc == initial_state.current_soc
    assert projected.target_soc == initial_state.target_soc


def test_project_battery_state_with_charging():
    """Test battery state projection when charging."""
    initial_state = BatteryState(current_soc=0.6, target_soc=0.8)
    charger_state = ChargerState(
        car_is_charging=True, charge_is_override=True, charge_rate_kw=7.0
    )

    projected = project_battery_state(initial_state, charger_state, 1.0)

    # Should increase by (7kW * 1h) / BATTERY_CAPACITY_KWH
    expected_increase = (7.0 * 1.0) / BATTERY_CAPACITY_KWH
    assert projected.current_soc == pytest.approx(
        initial_state.current_soc + expected_increase
    )
    assert projected.target_soc == initial_state.target_soc


def test_project_battery_state_reach_target():
    """Test that battery state projection respects the target SOC."""
    # Start at 0.79, very close to target of 0.8
    initial_state = BatteryState(current_soc=0.79, target_soc=0.8)
    charger_state = ChargerState(
        car_is_charging=True, charge_is_override=True, charge_rate_kw=7.0
    )

    projected = project_battery_state(initial_state, charger_state, 1.0)

    # Even with a full hour of charging, we should cap at the target
    assert projected.current_soc == pytest.approx(0.8)
    assert projected.current_soc <= initial_state.target_soc
