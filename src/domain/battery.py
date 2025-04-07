"""
Battery domain logic for the EV Charge Control Panel.
Handles battery state calculations and charge estimation.
"""

from src.config import BATTERY_CAPACITY_KWH, DEFAULT_SOC
from src.domain.models import BatteryState, ChargerState


def initialize_battery_state() -> BatteryState:
    """
    Initialize a new battery state with default values.

    Returns:
        BatteryState: New battery state object
    """
    return BatteryState(
        current_soc=DEFAULT_SOC,
    )


def calculate_charge_added(charge_rate_kw: float, duration_hours: float) -> float:
    """
    Calculate how much charge is added based on charging rate and duration.

    Args:
        charge_rate_kw: Charging rate in kilowatts
        duration_hours: Duration of charging in hours

    Returns:
        float: Charge added as a fraction of total capacity (0.0 to 1.0)
    """
    energy_added = charge_rate_kw * duration_hours  # kWh
    soc_added = energy_added / BATTERY_CAPACITY_KWH
    return soc_added


def project_battery_state(
    battery_state: BatteryState, charger_state: ChargerState, duration_hours: float
) -> BatteryState:
    """
    Project the battery state after a period of charging or not charging.

    Args:
        battery_state: Current battery state
        charger_state: Current charger state (determines if charging)
        duration_hours: Duration to project forward in hours

    Returns:
        BatteryState: Projected battery state
    """
    if not charger_state.car_is_charging:
        # If not charging, battery state doesn't change
        return BatteryState(
            current_soc=battery_state.current_soc, target_soc=battery_state.target_soc
        )

    # Calculate charge added
    charge_added = calculate_charge_added(charger_state.charge_rate_kw, duration_hours)

    # Add charge, but don't exceed target
    new_soc = min(battery_state.current_soc + charge_added, battery_state.target_soc)

    return BatteryState(current_soc=new_soc, target_soc=battery_state.target_soc)
