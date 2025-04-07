import pytest
from datetime import datetime
from unittest.mock import patch

import streamlit as st

from src.services.scheduler import (
    get_future_states,
    start_charge as handle_start_charge,
    stop_charge as handle_stop_charge,
)
from src.domain.models import DemoAdminState


def test_get_future_states_no_charging(setup_session_state):
    """Test getting future states when no charging is active."""
    # Set up a state where no charging is happening
    st.session_state.charger_state.car_is_charging = False
    st.session_state.charger_state.charge_is_override = False

    # Test during non-charging hours
    demo_state = DemoAdminState(
        car_is_plugged_in=True,
        current_time=datetime(2025, 1, 1, 12, 0),  # Noon
    )

    # Get future states
    states = get_future_states(demo_state, num_periods=3)

    # Check results
    assert len(states) == 3

    # SoC should remain constant
    assert states[0].battery_state.current_soc == pytest.approx(0.6)
    assert states[1].battery_state.current_soc == pytest.approx(0.6)
    assert states[2].battery_state.current_soc == pytest.approx(0.6)

    # No charging should be active
    assert not states[0].charger_state.car_is_charging
    assert not states[1].charger_state.car_is_charging
    assert not states[2].charger_state.car_is_charging


def test_get_future_states_scheduled_charging(setup_session_state):
    """Test getting future states during scheduled charging hours."""
    # Set up a state where scheduled charging is active
    st.session_state.charger_state.car_is_charging = True
    st.session_state.charger_state.charge_is_override = False

    # Test during scheduled charging hours
    demo_state = DemoAdminState(
        car_is_plugged_in=True,
        current_time=datetime(2025, 1, 1, 2, 30),  # 2:30 AM (in scheduled window)
    )

    # Get future states
    states = get_future_states(demo_state, num_periods=3)

    # Check results
    assert len(states) == 3

    # SoC should increase during charging
    initial_soc = states[0].battery_state.current_soc
    assert states[1].battery_state.current_soc > initial_soc
    assert states[2].battery_state.current_soc > states[1].battery_state.current_soc

    # Charging should be active
    assert states[0].charger_state.car_is_charging
    assert states[1].charger_state.car_is_charging
    assert states[2].charger_state.car_is_charging

    # Should be schedule charging, not override
    assert not states[0].charger_state.charge_is_override
    assert not states[1].charger_state.charge_is_override
    assert not states[2].charger_state.charge_is_override


def test_get_future_states_override_charging(setup_session_state):
    """Test getting future states during override charging."""
    # Set up a state where override charging is active
    st.session_state.charger_state.car_is_charging = True
    st.session_state.charger_state.charge_is_override = True
    st.session_state.charger_state.override_end_time = datetime(
        2025, 1, 1, 13, 0
    )  # 1 PM

    # Test during override charging
    demo_state = DemoAdminState(
        car_is_plugged_in=True,
        current_time=datetime(2025, 1, 1, 12, 0),  # Noon
    )

    # Get future states
    states = get_future_states(demo_state, num_periods=3)

    # Check results
    assert len(states) == 3

    # SoC should increase then stop at override end
    initial_soc = states[0].battery_state.current_soc
    assert states[1].battery_state.current_soc > initial_soc
    assert states[2].battery_state.current_soc >= states[1].battery_state.current_soc

    # First two periods should be charging due to override
    assert states[0].charger_state.car_is_charging
    assert states[1].charger_state.car_is_charging
    assert states[0].charger_state.charge_is_override
    assert states[1].charger_state.charge_is_override


def test_get_future_states_unplugged(setup_session_state):
    """Test that unplugged cars don't charge regardless of schedule or override."""
    # Set up a state with active schedule and override
    st.session_state.charger_state.car_is_charging = True
    st.session_state.charger_state.charge_is_override = True
    st.session_state.charger_state.override_end_time = datetime(2025, 1, 1, 13, 0)

    # Test with car unplugged
    demo_state = DemoAdminState(
        car_is_plugged_in=False,
        current_time=datetime(2025, 1, 1, 2, 30),  # 2:30 AM (in scheduled window)
    )

    # Get future states
    states = get_future_states(demo_state, num_periods=3)

    # Check that no charging happens
    for state in states:
        assert not state.charger_state.car_is_charging


@patch("streamlit.toast")
def test_handle_start_charge_unplugged(mock_toast, setup_session_state):
    """Test starting a charge when unplugged."""
    # Set up unplugged state
    st.session_state.demo_state.car_is_plugged_in = False

    # Try to start charge while unplugged
    handle_start_charge()

    # Should show error and not start charging
    mock_toast.assert_called_once()
    assert not st.session_state.charger_state.charge_is_override


@patch("streamlit.toast")
def test_handle_start_charge_plugged_in(mock_toast, setup_session_state):
    """Test starting a charge when plugged in."""
    # Set plugged in
    st.session_state.demo_state.car_is_plugged_in = True

    # Try to start charge while plugged in
    handle_start_charge()

    # Should start override charging
    mock_toast.assert_called_once()
    assert st.session_state.charger_state.car_is_charging
    assert st.session_state.charger_state.charge_is_override
    assert st.session_state.charger_state.override_end_time is not None


@patch("streamlit.toast")
def test_handle_stop_charge_with_override(mock_toast, setup_session_state):
    """Test stopping a charge that was started with override."""
    # Set up override charging state
    st.session_state.charger_state.car_is_charging = True
    st.session_state.charger_state.charge_is_override = True
    st.session_state.charger_state.override_end_time = datetime(2025, 1, 1, 13, 0)

    # Stop charge
    handle_stop_charge()

    # Should disable override but not disable schedule
    mock_toast.assert_called_once()
    assert not st.session_state.charger_state.charge_is_override
    assert st.session_state.charger_state.override_end_time is None
    assert st.session_state.charge_schedule.is_enabled


@patch("streamlit.toast")
def test_handle_stop_charge_with_schedule(mock_toast, setup_session_state):
    """Test stopping a charge that was started by schedule."""
    # Set up scheduled charging state
    st.session_state.charger_state.car_is_charging = True
    st.session_state.charger_state.charge_is_override = False

    # Stop charge
    handle_stop_charge()

    # Should disable schedule
    mock_toast.assert_called_once()
    assert not st.session_state.charge_schedule.is_enabled
    assert not st.session_state.charger_state.car_is_charging


@patch("streamlit.toast")
def test_handle_stop_charge_not_charging(mock_toast, setup_session_state):
    """Test stopping a charge when not charging."""
    # Set up not charging state
    st.session_state.charger_state.car_is_charging = False

    # Try to stop charge
    handle_stop_charge()

    # Should show info message
    mock_toast.assert_called_once()
    mock_toast.assert_called_with("Car is not currently charging", icon="ℹ️")
