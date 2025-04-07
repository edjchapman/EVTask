import pytest
from datetime import datetime, timedelta

import streamlit as st

from src.services.state_manager import init_session_state, get_current_states
from src.services.scheduler import (
    get_future_states,
    start_charge as handle_start_charge,
    stop_charge as handle_stop_charge,
)
from src.domain.models import DemoAdminState


@pytest.fixture
def setup_session_state():
    """Set up the test environment."""
    # Clear session state between tests
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Initialize session state
    init_session_state()

    # Basic demo state with current time and plugged in
    demo_state = DemoAdminState(
        car_is_plugged_in=True,
        current_time=datetime(2025, 1, 1, 12, 0),  # Noon
    )

    # Store demo state in session state
    st.session_state.demo_state = demo_state

    return demo_state


def test_override_then_revert_flow(setup_session_state):
    """Test the full flow of overriding then stopping and reverting to schedule."""
    demo_state = setup_session_state

    # Get initial state
    charger_state, battery_state = get_current_states()

    # Initially not charging
    assert not charger_state.car_is_charging
    assert not charger_state.charge_is_override

    # Start override charge
    handle_start_charge()

    # Check that override charge is active
    charger_state, battery_state = get_current_states()
    assert charger_state.car_is_charging
    assert charger_state.charge_is_override
    assert charger_state.override_end_time is not None

    # Get future states and check charging is active
    future_states = get_future_states(demo_state, num_periods=4)
    assert future_states[0].charger_state.car_is_charging
    assert future_states[0].charger_state.charge_is_override

    # Stop override
    handle_stop_charge()

    # Check that override is cleared but schedule is still enabled
    charger_state, battery_state = get_current_states()
    assert not charger_state.charge_is_override
    assert not charger_state.car_is_charging  # Not in schedule window
    assert st.session_state.charge_schedule.is_enabled  # Schedule still active


def test_schedule_disable_flow(setup_session_state):
    """Test disabling a scheduled charge."""
    # Set the current time to be within the scheduled window
    schedule_demo_state = DemoAdminState(
        car_is_plugged_in=True,
        current_time=datetime(2025, 1, 1, 3, 0),  # 3 AM (within schedule)
    )
    st.session_state.demo_state = schedule_demo_state

    # Get state during scheduled time
    charger_state, battery_state = get_current_states()

    # Should be charging due to schedule
    assert charger_state.car_is_charging
    assert not charger_state.charge_is_override

    # Stop scheduled charging
    handle_stop_charge()

    # Check schedule is disabled
    charger_state, battery_state = get_current_states()
    assert not charger_state.car_is_charging
    assert not st.session_state.charge_schedule.is_enabled

    # Try to start charging again
    handle_start_charge()

    # Should be override charging now
    charger_state, battery_state = get_current_states()
    assert charger_state.car_is_charging
    assert charger_state.charge_is_override


def test_unplugged_car_flow(setup_session_state):
    """Test interactions with an unplugged car."""
    # Set car to unplugged
    unplugged_demo_state = DemoAdminState(
        car_is_plugged_in=False,
        current_time=datetime(2025, 1, 1, 3, 0),  # 3 AM (within schedule)
    )
    st.session_state.demo_state = unplugged_demo_state

    # Get initial state
    charger_state, battery_state = get_current_states()

    # Should not be charging even within schedule window
    assert not charger_state.car_is_charging

    # Try to start charging
    handle_start_charge()

    # Should still not be charging
    charger_state, battery_state = get_current_states()
    assert not charger_state.car_is_charging
    assert not charger_state.charge_is_override

    # Plug in car
    plugged_demo_state = DemoAdminState(
        car_is_plugged_in=True, current_time=datetime(2025, 1, 1, 3, 0)
    )
    st.session_state.demo_state = plugged_demo_state

    # Get the charge schedule and manually set it to be in a charging window
    st.session_state.charge_schedule.is_enabled = True

    # Force init the charge state based on time and schedule
    charger_state, battery_state = get_current_states()

    # Since we're testing at 3 AM (within the schedule window 2-5 AM)
    # and the car is plugged in, it should be charging
    assert charger_state.car_is_charging
    assert not charger_state.charge_is_override


def test_override_expiration_flow(setup_session_state):
    """Test that override charging expires correctly."""
    # We don't need the demo_state variable in this test

    # Start override charge
    handle_start_charge()

    # Verify override is active
    charger_state, battery_state = get_current_states()
    assert charger_state.car_is_charging
    assert charger_state.charge_is_override

    # Store the override end time
    override_end = charger_state.override_end_time

    # Move time forward past override end
    future_demo_state = DemoAdminState(
        car_is_plugged_in=True, current_time=override_end + timedelta(minutes=1)
    )
    st.session_state.demo_state = future_demo_state

    # Get state after override should have expired
    charger_state, battery_state = get_current_states()

    # Override should be cleared
    assert not charger_state.charge_is_override
    assert not charger_state.car_is_charging  # Not in schedule window
    assert charger_state.override_end_time is None
