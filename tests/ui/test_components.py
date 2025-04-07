import pytest
from datetime import datetime, time
from unittest.mock import patch, MagicMock

import streamlit as st

from src.ui.components import status_panel, control_buttons
from src.domain.models import BatteryState, ChargeSchedule, ChargerState, DemoAdminState


@pytest.fixture
def setup_test_state():
    """Set up test state for app functions."""
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Create mock states
    st.session_state.battery_state = BatteryState(current_soc=0.65)
    st.session_state.charger_state = ChargerState(
        car_is_charging=True,
        charge_is_override=True,
        override_end_time=datetime(2025, 1, 1, 13, 0),
    )
    st.session_state.charge_schedule = ChargeSchedule(
        start_time=time(2, 0), end_time=time(5, 0), is_enabled=True
    )
    st.session_state.demo_state = DemoAdminState(
        car_is_plugged_in=True, current_time=datetime(2025, 1, 1, 12, 0)
    )


@patch("streamlit.columns")
@patch("streamlit.button")
def test_control_buttons_plugged_in_not_charging(
    mock_button, mock_columns, setup_test_state
):
    """Test controls when car is plugged in but not charging."""
    # Mock columns
    col1, col2 = MagicMock(), MagicMock()
    mock_columns.return_value = [col1, col2]

    # Call controls
    control_buttons(True, False, False)

    # Check start button is enabled, stop button is disabled
    col1.button.assert_called_once()
    col2.button.assert_called_once()

    # Extract the kwargs for the buttons
    start_kwargs = col1.button.call_args[1]
    stop_kwargs = col2.button.call_args[1]

    assert not start_kwargs.get("disabled", False)
    assert stop_kwargs.get("disabled", False)


@patch("streamlit.columns")
@patch("streamlit.button")
def test_control_buttons_override_charging(mock_button, mock_columns, setup_test_state):
    """Test controls when car is override charging."""
    # Mock columns
    col1, col2 = MagicMock(), MagicMock()
    mock_columns.return_value = [col1, col2]

    # Call controls
    control_buttons(True, True, True)

    # Check start button is disabled, stop button is enabled
    col1.button.assert_called_once()
    col2.button.assert_called_once()

    # Extract the kwargs for the buttons
    start_kwargs = col1.button.call_args[1]
    stop_kwargs = col2.button.call_args[1]

    assert start_kwargs.get("disabled", False)
    assert not stop_kwargs.get("disabled", False)


def test_status_panel(setup_test_state):
    """Test that status_panel function exists and takes expected parameters."""
    # This is a basic existence test, since properly testing the UI output
    # would require more complex Streamlit mocking

    # Check that the function exists and has the right signature
    assert callable(status_panel)

    # We can't easily test the actual UI display in a unit test without
    # extensive mocking, but we can verify the function doesn't crash
    try:
        status_panel(
            st.session_state.battery_state,
            st.session_state.charger_state,
            st.session_state.demo_state,
        )
        assert True  # If we got here without an exception, that's a pass
    except Exception as e:
        pytest.fail(f"status_panel raised an exception: {e}")
