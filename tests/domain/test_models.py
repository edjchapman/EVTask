from datetime import datetime, time

from src.domain.models import (
    BatteryState,
    ChargeSchedule,
    ChargerState,
    CombinedState,
    DemoAdminState,
)


def test_battery_state_defaults():
    """Test BatteryState default values."""
    battery = BatteryState(current_soc=0.5)

    assert battery.current_soc == 0.5
    assert battery.target_soc == 0.8  # Default value


def test_charge_schedule_defaults():
    """Test ChargeSchedule default values."""
    start = time(2, 0)
    end = time(5, 0)
    schedule = ChargeSchedule(start_time=start, end_time=end)

    assert schedule.start_time == start
    assert schedule.end_time == end
    assert schedule.is_enabled is True  # Default value


def test_charger_state_defaults():
    """Test ChargerState default values."""
    charger = ChargerState(car_is_charging=True, charge_is_override=False)

    assert charger.car_is_charging is True
    assert charger.charge_is_override is False
    assert charger.charge_rate_kw == 7.0  # Default value
    assert charger.override_minutes == 60  # Default value
    assert charger.override_end_time is None  # Default value


def test_combined_state_composition():
    """Test CombinedState composition."""
    current_time = datetime(2025, 1, 1, 12, 0)
    battery = BatteryState(current_soc=0.6)
    charger = ChargerState(car_is_charging=True, charge_is_override=False)

    combined = CombinedState(
        time=current_time, battery_state=battery, charger_state=charger
    )

    assert combined.time == current_time
    assert combined.battery_state is battery
    assert combined.charger_state is charger
    assert combined.battery_state.current_soc == 0.6
    assert combined.charger_state.car_is_charging is True


def test_demo_admin_state():
    """Test DemoAdminState initialization."""
    current_time = datetime(2025, 1, 1, 12, 0)
    demo = DemoAdminState(car_is_plugged_in=True, current_time=current_time)

    assert demo.car_is_plugged_in is True
    assert demo.current_time == current_time
