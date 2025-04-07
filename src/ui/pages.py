"""
Page layouts for the EV Charge Control Panel.
"""

import streamlit as st

from src.domain.models import DemoAdminState
from src.services import state_manager
from src.ui.components import status_panel, charging_info, control_buttons
from src.ui.visualization import plot_charge_forecast
from src.utils import get_current_time_to_nearest_30_minutes


def admin_panel() -> DemoAdminState:
    """
    Display the admin panel for controlling the demo state.

    Returns:
        DemoAdminState: Updated demo state
    """
    # Start with current values from session state
    current_demo_state = state_manager.get_demo_state()
    current_battery_state = state_manager.get_battery_state()
    current_charge_schedule = state_manager.get_charge_schedule()

    rounded_time = (
        current_demo_state.current_time
        if current_demo_state
        else get_current_time_to_nearest_30_minutes()
    )

    with st.sidebar:
        st.subheader("Demo Admin Controls")
        st.write("Use these controls to simulate the car and charger state.")

        current_time = st.time_input("Current Time", rounded_time.time())
        # Add back in the date to the time
        current_time = rounded_time.replace(
            hour=current_time.hour, minute=current_time.minute
        )

        car_is_plugged_in = st.toggle("Plugged in", value=True)

        # Allow adjusting the battery state
        st.subheader("Battery State")
        current_soc = st.slider(
            "Current State of Charge (%)",
            min_value=0,
            max_value=100,
            value=int(current_battery_state.current_soc * 100),
            step=5,
        )
        current_battery_state.current_soc = current_soc / 100
        state_manager.update_battery_state(current_battery_state)

        # Allow adjusting charge schedule
        st.subheader("Charge Schedule")
        schedule_start = st.time_input(
            "Schedule Start Time", current_charge_schedule.start_time
        )
        schedule_end = st.time_input(
            "Schedule End Time", current_charge_schedule.end_time
        )

        # Update the schedule
        current_charge_schedule.start_time = schedule_start
        current_charge_schedule.end_time = schedule_end
        state_manager.update_charge_schedule(current_charge_schedule)

    # Update the demo state
    demo_state = DemoAdminState(
        car_is_plugged_in=car_is_plugged_in, current_time=current_time
    )
    state_manager.update_demo_state(demo_state)

    return demo_state


def main_panel():
    """Display the main control panel for the EV charger."""
    st.title("EV Charge Control Panel")

    # Get current states
    demo_state = admin_panel()
    charger_state, battery_state = state_manager.get_current_states()
    charge_schedule = state_manager.get_charge_schedule()

    # Display status panels
    status, info = st.columns([1, 1])

    with status:
        status_panel(battery_state, charger_state, demo_state)

    with info:
        charging_info(charger_state, charge_schedule)

    # Display charging schedule chart
    st.subheader("Charging Schedule")
    from src.services.scheduler import get_future_states

    future_states = get_future_states(demo_state)
    st.plotly_chart(
        plot_charge_forecast(
            future_states,
            current_time=demo_state.current_time,
        ),
        use_container_width=True,
    )

    # Display controls
    start_charging, stop_charging = control_buttons(
        demo_state.car_is_plugged_in,
        charger_state.car_is_charging,
        charger_state.charge_is_override,
    )
