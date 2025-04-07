from datetime import time
import streamlit as st

from src.services.state_manager import init_session_state
from src.domain.models import BatteryState, ChargeSchedule, ChargerState


def test_init_session_state():
    """Test that session state is properly initialized."""
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Initialize session state
    init_session_state()

    # Check that all required keys exist
    assert "battery_state" in st.session_state
    assert "charger_state" in st.session_state
    assert "charge_schedule" in st.session_state

    # Check battery state values
    assert isinstance(st.session_state.battery_state, BatteryState)
    assert 0 <= st.session_state.battery_state.current_soc <= 1.0

    # Check charger state values
    assert isinstance(st.session_state.charger_state, ChargerState)
    assert isinstance(st.session_state.charger_state.car_is_charging, bool)
    assert isinstance(st.session_state.charger_state.charge_is_override, bool)

    # Check schedule values
    assert isinstance(st.session_state.charge_schedule, ChargeSchedule)
    assert isinstance(st.session_state.charge_schedule.start_time, time)
    assert isinstance(st.session_state.charge_schedule.end_time, time)
    assert isinstance(st.session_state.charge_schedule.is_enabled, bool)
