"""
Entry point for the EV Charge Control Panel application.
"""

import streamlit as st

from src.config import UI_PAGE_TITLE, UI_PAGE_ICON, UI_LAYOUT
from src.services import state_manager
from src.ui.pages import main_panel


def main():
    """Run the EV Charge Control Panel application."""
    # Configure page settings
    st.set_page_config(
        page_title=UI_PAGE_TITLE,
        page_icon=UI_PAGE_ICON,
        layout=UI_LAYOUT,
    )

    # Initialize session state
    state_manager.init_session_state()

    # Display the main panel
    main_panel()


if __name__ == "__main__":
    main()
