import streamlit as st

from src.ui.pages import main_panel
from src.services.state_manager import init_session_state


def test_init_session_state_in_pages():
    """Test that session state initialization works correctly for pages."""
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Call initialize
    init_session_state()

    # Check core states were initialized for use in pages
    assert "battery_state" in st.session_state
    assert "charger_state" in st.session_state
    assert "charge_schedule" in st.session_state


def test_main_panel_existence():
    """Test that main_panel function exists."""
    # This is a basic existence test, since properly testing the UI output
    # would require more complex Streamlit mocking
    assert callable(main_panel)
