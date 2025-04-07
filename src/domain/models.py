"""
Core domain models for the EV Charge Control Panel application.
"""

from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional

from src.config import (
    DEFAULT_CHARGE_RATE_KW,
    DEFAULT_OVERRIDE_MINUTES,
    DEFAULT_TARGET_SOC,
)


@dataclass
class DemoAdminState:
    """State controlled from the admin panel for demo/simulation purposes."""

    car_is_plugged_in: bool
    current_time: datetime


@dataclass
class BatteryState:
    """
    Represents the state of the car's battery.

    Attributes:
        current_soc: Current State of Charge (0.0 to 1.0)
        target_soc: Target state of charge (default from config)
    """

    current_soc: float  # State of Charge (0.0 to 1.0)
    target_soc: float = DEFAULT_TARGET_SOC


@dataclass
class ChargeSchedule:
    """
    Represents a scheduled charging window.

    Attributes:
        start_time: Daily start time (e.g., 2:00 AM)
        end_time: Daily end time (e.g., 5:00 AM)
        is_enabled: Whether the schedule is currently active
    """

    start_time: time
    end_time: time
    is_enabled: bool = True


@dataclass
class ChargerState:
    """
    Represents the state of the car's charger.

    Attributes:
        car_is_charging: Whether the car is currently charging
        charge_is_override: Whether charging is from a user override
        charge_rate_kw: Charging rate in kW
        override_minutes: Duration of override in minutes
        override_end_time: When the override ends (None if not in override)
    """

    car_is_charging: bool
    charge_is_override: bool
    charge_rate_kw: float = DEFAULT_CHARGE_RATE_KW
    override_minutes: int = DEFAULT_OVERRIDE_MINUTES
    override_end_time: Optional[datetime] = None


@dataclass
class CombinedState:
    """
    Helper class for grouping time, battery, and charger states together.
    Used primarily for forecasting and visualization.

    Attributes:
        time: Point in time for this state
        battery_state: Battery state at this time
        charger_state: Charger state at this time
    """

    time: datetime
    battery_state: BatteryState
    charger_state: ChargerState
