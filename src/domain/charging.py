"""
Charging domain logic for the EV Charge Control Panel.
Handles charge state management, scheduling, and overrides.
"""

from datetime import datetime, time, timedelta

from src.config import DEFAULT_OVERRIDE_MINUTES, DEFAULT_CHARGE_RATE_KW
from src.domain.models import ChargeSchedule, ChargerState, DemoAdminState


def initialize_charger_state() -> ChargerState:
    """
    Initialize a new charger state with default values.

    Returns:
        ChargerState: New charger state object
    """
    return ChargerState(
        car_is_charging=False,
        charge_is_override=False,
        charge_rate_kw=DEFAULT_CHARGE_RATE_KW,
        override_minutes=DEFAULT_OVERRIDE_MINUTES,
        override_end_time=None,
    )


def is_in_scheduled_window(current_time: time, schedule: ChargeSchedule) -> bool:
    """
    Check if the current time is within the scheduled charging window.

    Args:
        current_time: Current time to check
        schedule: Charge schedule to check against

    Returns:
        bool: True if in the scheduled window, False otherwise
    """
    if not schedule.is_enabled:
        return False

    if schedule.start_time <= schedule.end_time:
        # Normal window (e.g., 2am-5am)
        return schedule.start_time <= current_time <= schedule.end_time
    else:
        # Overnight window (e.g., 10pm-6am)
        return current_time >= schedule.start_time or current_time <= schedule.end_time


def update_charger_state(
    charger_state: ChargerState, demo_state: DemoAdminState, schedule: ChargeSchedule
) -> ChargerState:
    """
    Update the charger state based on current conditions.

    Args:
        charger_state: Current charger state
        demo_state: Current demo/admin state
        schedule: Current charge schedule

    Returns:
        ChargerState: Updated charger state
    """
    # Make a copy of the current state
    new_state = ChargerState(
        car_is_charging=charger_state.car_is_charging,
        charge_is_override=charger_state.charge_is_override,
        charge_rate_kw=charger_state.charge_rate_kw,
        override_minutes=charger_state.override_minutes,
        override_end_time=charger_state.override_end_time,
    )

    # Check if override has expired
    if (
        new_state.charge_is_override
        and new_state.override_end_time
        and demo_state.current_time >= new_state.override_end_time
    ):
        # Reset override status
        new_state.charge_is_override = False
        new_state.override_end_time = None

    # Determine charging state
    if demo_state.car_is_plugged_in:
        if new_state.charge_is_override:
            new_state.car_is_charging = True
        else:
            # Check if current time is in scheduled window
            in_schedule = is_in_scheduled_window(
                demo_state.current_time.time(), schedule
            )
            new_state.car_is_charging = in_schedule and schedule.is_enabled
    else:
        # Can't charge if not plugged in
        new_state.car_is_charging = False

    return new_state


def start_override_charge(
    charger_state: ChargerState, current_time: datetime
) -> ChargerState:
    """
    Start an override charging session.

    Args:
        charger_state: Current charger state
        current_time: Current time for calculating end time

    Returns:
        ChargerState: Updated charger state with override active
    """
    # Calculate override end time
    override_end_time = current_time + timedelta(minutes=charger_state.override_minutes)

    # Create new state with override active
    return ChargerState(
        car_is_charging=True,
        charge_is_override=True,
        charge_rate_kw=charger_state.charge_rate_kw,
        override_minutes=charger_state.override_minutes,
        override_end_time=override_end_time,
    )


def stop_override_charge(charger_state: ChargerState) -> ChargerState:
    """
    Stop an override charging session.

    Args:
        charger_state: Current charger state

    Returns:
        ChargerState: Updated charger state with override stopped
    """
    return ChargerState(
        car_is_charging=False,
        charge_is_override=False,
        charge_rate_kw=charger_state.charge_rate_kw,
        override_minutes=charger_state.override_minutes,
        override_end_time=None,
    )


def disable_scheduled_charge(charger_state: ChargerState) -> ChargerState:
    """
    Disable the current scheduled charging.
    Schedule will be re-enabled later via the schedule service.

    Args:
        charger_state: Current charger state

    Returns:
        ChargerState: Updated charger state with charging disabled
    """
    return ChargerState(
        car_is_charging=False,
        charge_is_override=charger_state.charge_is_override,
        charge_rate_kw=charger_state.charge_rate_kw,
        override_minutes=charger_state.override_minutes,
        override_end_time=charger_state.override_end_time,
    )
