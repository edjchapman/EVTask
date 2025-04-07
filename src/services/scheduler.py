"""
Scheduling service for the EV Charge Control Panel.
Handles charge scheduling and future state projection.
"""

from datetime import timedelta
from typing import List, Tuple

import streamlit as st

from src.config import FORECAST_PERIODS, PERIOD_MINUTES
from src.domain.battery import project_battery_state
from src.domain.charging import update_charger_state
from src.domain.models import (
    BatteryState,
    ChargerState,
    CombinedState,
    DemoAdminState,
)
from src.services import state_manager


def get_current_states() -> Tuple[ChargerState, BatteryState]:
    """
    Get the current charging and battery states, updated based on
    current time and schedule.

    Returns:
        Tuple[ChargerState, BatteryState]: Current charger and battery states
    """
    charger_state = state_manager.get_charger_state()
    battery_state = state_manager.get_battery_state()
    demo_state = state_manager.get_demo_state()
    charge_schedule = state_manager.get_charge_schedule()

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
        state_manager.update_charger_state(updated_charger_state)

    return updated_charger_state, battery_state


def get_future_states(
    demo_state: DemoAdminState, num_periods: int = FORECAST_PERIODS
) -> List[CombinedState]:
    """
    Project future states based on current settings and state.

    Args:
        demo_state: Current demo state
        num_periods: Number of future periods to project

    Returns:
        List[CombinedState]: Projected future states
    """
    # Get current state
    charger_state = state_manager.get_charger_state()
    battery_state = state_manager.get_battery_state()
    charge_schedule = state_manager.get_charge_schedule()

    # Period is in minutes
    period = timedelta(minutes=PERIOD_MINUTES)
    period_hours = PERIOD_MINUTES / 60
    current_time = demo_state.current_time

    # Create list to store future states
    future_states = []

    # Track the current soc as we project forward
    projected_soc = battery_state.current_soc

    for i in range(num_periods):
        # Calculate the time for this period
        future_time = current_time + i * period

        # Create a temporary demo state for this future time
        future_demo_state = DemoAdminState(
            car_is_plugged_in=demo_state.car_is_plugged_in, current_time=future_time
        )

        # Create a temporary battery state with the projected SoC
        future_battery_state = BatteryState(
            current_soc=projected_soc, target_soc=battery_state.target_soc
        )

        # Update charger state for this future time
        future_charger_state = update_charger_state(
            charger_state, future_demo_state, charge_schedule
        )

        # Project battery state for this period
        future_battery_state = project_battery_state(
            future_battery_state, future_charger_state, period_hours
        )

        # Update projected SoC for next period
        projected_soc = future_battery_state.current_soc

        # Add to future states
        future_states.append(
            CombinedState(
                time=future_time,
                battery_state=future_battery_state,
                charger_state=future_charger_state,
            )
        )

    return future_states


def start_charge() -> None:
    """
    Start an override charging session.
    """

    charger_state = state_manager.get_charger_state()
    demo_state = state_manager.get_demo_state()

    # Only start if plugged in
    if not demo_state.car_is_plugged_in:
        st.toast("Car is not plugged in!", icon="⚠️")
        return

    # Set override charging
    charger_state.car_is_charging = True
    charger_state.charge_is_override = True

    # Set override end time
    override_minutes = charger_state.override_minutes
    charger_state.override_end_time = demo_state.current_time + timedelta(
        minutes=override_minutes
    )

    # Update state
    state_manager.update_charger_state(charger_state)

    st.toast(f"Starting charge for {override_minutes} minutes!", icon="🚀")


def stop_charge() -> None:
    """
    Stop the current charging session based on type.
    """

    charger_state = state_manager.get_charger_state()
    charge_schedule = state_manager.get_charge_schedule()

    if not charger_state.car_is_charging:
        st.toast("Car is not currently charging", icon="ℹ️")
        return

    if charger_state.charge_is_override:
        # If charging from override, revert to schedule
        charger_state.charge_is_override = False
        charger_state.override_end_time = None
        state_manager.update_charger_state(charger_state)
        st.toast("Stopped override charging, reverting to schedule", icon="🔄")
    else:
        # If charging from schedule, disable schedule until next morning
        charge_schedule.is_enabled = False
        charger_state.car_is_charging = False
        state_manager.update_charge_schedule(charge_schedule)
        state_manager.update_charger_state(charger_state)
        st.toast("Disabled scheduled charging until tomorrow", icon="⏰")
