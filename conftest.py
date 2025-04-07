"""
Configuration file for pytest.
Provides common test fixtures used across test files.
"""

from datetime import datetime, time
from unittest.mock import MagicMock

import pytest
import streamlit as st

from src.domain.models import BatteryState, ChargeSchedule, ChargerState, DemoAdminState


@pytest.fixture
def setup_session_state():
    """Set up streamlit session state for testing."""
    # Clear session state between tests
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Add mock states to session state
    st.session_state.battery_state = BatteryState(current_soc=0.6, target_soc=0.8)

    st.session_state.charger_state = ChargerState(
        car_is_charging=False,
        charge_is_override=False,
        override_minutes=60,
        override_end_time=None,
    )

    st.session_state.charge_schedule = ChargeSchedule(
        start_time=time(2, 0),  # 2 AM
        end_time=time(5, 0),  # 5 AM
        is_enabled=True,
    )

    current_time = datetime(2025, 1, 1, 12, 0)  # Noon
    demo_state = DemoAdminState(car_is_plugged_in=True, current_time=current_time)
    st.session_state.demo_state = demo_state

    return demo_state


@pytest.fixture
def mock_datetime(monkeypatch):
    """Mock datetime for consistent testing."""
    fixed_time = datetime(2025, 1, 1, 12, 0, 0)  # Noon

    mock_dt = MagicMock()
    mock_dt.now.return_value = fixed_time
    monkeypatch.setattr("src.utils.datetime", mock_dt)

    return mock_dt
