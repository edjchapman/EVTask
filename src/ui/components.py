"""
UI components for the EV Charge Control Panel.
"""

import streamlit as st

from src.domain.models import BatteryState, ChargeSchedule, ChargerState, DemoAdminState
from src.services import scheduler


def status_panel(
    battery_state: BatteryState, charger_state: ChargerState, demo_state: DemoAdminState
) -> None:
    """
    Display current vehicle and charging status.

    Args:
        battery_state: Current battery state
        charger_state: Current charger state
        demo_state: Current demo state
    """
    st.subheader("Current Status")

    # Plug icon
    plug_icon = "🔌" if demo_state.car_is_plugged_in else "❌"
    st.write(
        f"{plug_icon} {'Connected' if demo_state.car_is_plugged_in else 'Disconnected'}"
    )

    # Battery icon and percentage
    soc_percent = int(battery_state.current_soc * 100)
    if soc_percent >= 80:
        battery_icon = "🔋"  # Full battery
    elif soc_percent >= 50:
        battery_icon = "🔋"  # Medium battery
    elif soc_percent >= 20:
        battery_icon = "🪫"  # Low battery
    else:
        battery_icon = "🪫"  # Critical battery

    st.write(f"{battery_icon} Battery: {soc_percent}%")

    # Charging status
    if charger_state.car_is_charging:
        if charger_state.charge_is_override:
            st.write("⚡ Charging: Override active")
        else:
            st.write("⚡ Charging: Schedule active")
    else:
        st.write("💤 Charging: Inactive")


def charging_info(charger_state: ChargerState, charge_schedule: ChargeSchedule) -> None:
    """
    Display charging schedule and rate information.

    Args:
        charger_state: Current charger state
        charge_schedule: Current charge schedule
    """
    st.subheader("Charging Info")

    # Format schedule times
    start_time_str = charge_schedule.start_time.strftime("%-I:%M %p")
    end_time_str = charge_schedule.end_time.strftime("%-I:%M %p")

    schedule_status = "Enabled" if charge_schedule.is_enabled else "Disabled"
    st.write(f"⏰ Schedule: {start_time_str} - {end_time_str} ({schedule_status})")

    # Show override end time if applicable
    if charger_state.charge_is_override and charger_state.override_end_time:
        override_end = charger_state.override_end_time.strftime("%-I:%M %p")
        st.write(f"🕒 Override until: {override_end}")

    # Show target charge
    target_percent = int(charger_state.charge_rate_kw * 100)
    st.write(f"🎯 Target charge: {target_percent}%")

    # Show charge rate
    st.write(f"⚡ Charge rate: {charger_state.charge_rate_kw} kW")


def control_buttons(
    car_is_plugged_in: bool, car_is_charging: bool, charge_is_override: bool
) -> tuple:
    """
    Display charge control buttons with appropriate state.

    Args:
        car_is_plugged_in: Whether the car is plugged in
        car_is_charging: Whether the car is currently charging
        charge_is_override: Whether charging is from an override

    Returns:
        tuple: Start and stop button states
    """
    st.subheader("Controls")
    c1, c2 = st.columns([1, 1])

    # Customize button text and disabled state based on car status
    start_button_text = "Start Charging"
    start_disabled = not car_is_plugged_in or (car_is_charging and charge_is_override)

    stop_button_text = "Stop Charging"
    stop_disabled = not car_is_plugged_in or not car_is_charging

    return (
        c1.button(
            start_button_text,
            disabled=start_disabled,
            on_click=scheduler.start_charge,
            use_container_width=True,
        ),
        c2.button(
            stop_button_text,
            disabled=stop_disabled,
            on_click=scheduler.stop_charge,
            use_container_width=True,
        ),
    )
