import pytest
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objs as go

from src.domain.models import BatteryState, ChargerState, CombinedState
from src.ui.visualization import (
    _convert_states_to_dataframe,
    plot_charge_forecast,
)

# Define PERIOD constant (from visualization.py)
PERIOD = timedelta(minutes=30)


@pytest.fixture
def sample_states():
    """Create sample states for testing plotting functions."""
    base_time = datetime(2025, 1, 1, 12, 0)  # Noon
    states = []

    # Create 5 states with 30 minute intervals
    for i in range(5):
        time = base_time + i * PERIOD
        battery_state = BatteryState(
            current_soc=0.6 + i * 0.05,  # Increasing SoC
            target_soc=0.8,
        )
        charger_state = ChargerState(
            car_is_charging=i < 3,  # Charging for first 3 periods
            charge_is_override=i < 2,  # Override for first 2 periods
            override_end_time=base_time + 2 * PERIOD if i < 2 else None,
        )
        states.append(
            CombinedState(
                time=time, battery_state=battery_state, charger_state=charger_state
            )
        )

    return states


def test_convert_states_to_dataframe_empty():
    """Test dataframe conversion with empty states list."""
    df = _convert_states_to_dataframe([])

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert "Time" in df.columns
    assert "State of Charge" in df.columns
    assert "Car is Charging" in df.columns
    assert "Charge is Override" in df.columns


def test_convert_states_to_dataframe(sample_states):
    """Test dataframe conversion with sample states."""
    df = _convert_states_to_dataframe(sample_states)

    # Check dataframe structure
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    assert "Time" in df.columns
    assert "State of Charge" in df.columns
    assert "Car is Charging" in df.columns
    assert "Charge is Override" in df.columns

    # Check values
    assert df["State of Charge"].tolist() == [0.6, 0.65, 0.7, 0.75, 0.8]
    assert df["Car is Charging"].tolist() == [True, True, True, False, False]
    assert df["Charge is Override"].tolist() == [True, True, False, False, False]


def test_plot_charge_forecast(sample_states):
    """Test the plot generation with sample states."""
    current_time = datetime(2025, 1, 1, 12, 0)

    fig = plot_charge_forecast(sample_states, current_time)

    # Check that we got a valid figure
    assert isinstance(fig, go.Figure)

    # Check that data is present
    assert len(fig.data) > 0

    # Check that we have some shapes (lines, rectangles)
    assert len(fig.layout.shapes) > 0

    # Check that we have some annotations
    assert len(fig.layout.annotations) > 0

    # Check Y-axis range is set to percentage scale
    assert list(fig.layout.yaxis.range) == [0, 100]
