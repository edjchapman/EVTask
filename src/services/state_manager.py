"""
State management service for the EV Charge Control Panel.
Centralizes access to Streamlit session state.
"""

import streamlit as st

from src.config import (
    DEFAULT_SCHEDULE_ENABLED,
    DEFAULT_SCHEDULE_END,
    DEFAULT_SCHEDULE_START,
)
from src.domain.battery import initialize_battery_state
from src.domain.charging import initialize_charger_state
from src.domain.models import (
    BatteryState,
    ChargeSchedule,
    ChargerState,
    DemoAdminState,
)
from src.utils import get_current_time_to_nearest_30_minutes


def init_session_state() -> None:
    """Initialize all required session state variables."""
    if "battery_state" not in st.session_state:
        st.session_state.battery_state = initialize_battery_state()

    if "charger_state" not in st.session_state:
        st.session_state.charger_state = initialize_charger_state()

    if "charge_schedule" not in st.session_state:
        st.session_state.charge_schedule = ChargeSchedule(
            start_time=DEFAULT_SCHEDULE_START,
            end_time=DEFAULT_SCHEDULE_END,
            is_enabled=DEFAULT_SCHEDULE_ENABLED,
        )

    if "demo_state" not in st.session_state:
        rounded_time = get_current_time_to_nearest_30_minutes()
        st.session_state.demo_state = DemoAdminState(
            car_is_plugged_in=True,
            current_time=rounded_time,
        )


def get_battery_state() -> BatteryState:
    """
    Get the current battery state from session state.

    Returns:
        BatteryState: Current battery state
    """
    init_session_state()
    return st.session_state.battery_state


def get_charger_state() -> ChargerState:
    """
    Get the current charger state from session state.

    Returns:
        ChargerState: Current charger state
    """
    init_session_state()
    return st.session_state.charger_state


def get_charge_schedule() -> ChargeSchedule:
    """
    Get the current charge schedule from session state.

    Returns:
        ChargeSchedule: Current charge schedule
    """
    init_session_state()
    return st.session_state.charge_schedule


def get_demo_state() -> DemoAdminState:
    """
    Get the current demo state from session state.

    Returns:
        DemoAdminState: Current demo state
    """
    init_session_state()
    return st.session_state.demo_state


def update_battery_state(battery_state: BatteryState) -> None:
    """
    Update the battery state in session state.

    Args:
        battery_state: New battery state
    """
    init_session_state()
    st.session_state.battery_state = battery_state


def update_charger_state(charger_state: ChargerState) -> None:
    """
    Update the charger state in session state.

    Args:
        charger_state: New charger state
    """
    init_session_state()
    st.session_state.charger_state = charger_state


def update_charge_schedule(charge_schedule: ChargeSchedule) -> None:
    """
    Update the charge schedule in session state.

    Args:
        charge_schedule: New charge schedule
    """
    init_session_state()
    st.session_state.charge_schedule = charge_schedule


def update_demo_state(demo_state: DemoAdminState) -> None:
    """
    Update the demo state in session state.

    Args:
        demo_state: New demo state
    """
    init_session_state()
    st.session_state.demo_state = demo_state


def get_current_states() -> tuple[ChargerState, BatteryState]:
    """
    Get the current charger and battery states.
    A convenience function that returns both states together.

    Returns:
        tuple[ChargerState, BatteryState]: Current charger and battery states
    """
    from src.domain.charging import update_charger_state

    charger_state = get_charger_state()
    battery_state = get_battery_state()
    demo_state = get_demo_state()
    charge_schedule = get_charge_schedule()

    # Update charger state based on current time and schedule
    updated_charger_state = update_charger_state(
        charger_state, demo_state, charge_schedule
    )

    # Store the updated state if it changed
    if (
        updated_charger_state.car_is_charging != charger_state.car_is_charging
        or updated_charger_state.charge_is_override != charger_state.charge_is_override
        or updated_charger_state.override_end_time != charger_state.override_end_time
    ):
        # Use our own function to update the state in session_state
        st.session_state.charger_state = updated_charger_state

    return updated_charger_state, battery_state
