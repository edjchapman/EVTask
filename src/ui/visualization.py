"""
Visualization components for the EV Charge Control Panel.
"""

from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure

from src.config import PERIOD_MINUTES
from src.domain.models import CombinedState

# These set the resampling period for graphing
PERIOD = timedelta(minutes=PERIOD_MINUTES)


def _convert_states_to_dataframe(states: list[CombinedState]) -> pd.DataFrame:
    """
    Convert a list of CombinedState objects to a pandas DataFrame for plotting.

    Args:
        states: List of CombinedState objects

    Returns:
        pd.DataFrame: DataFrame with time, SoC, and charging status
    """
    if not states:
        # Return empty dataframe with expected columns if no states
        return pd.DataFrame(
            columns=["Time", "State of Charge", "Car is Charging", "Charge is Override"]
        )

    # Extract data from CombinedState objects
    times = [state.time for state in states]
    socs = [state.battery_state.current_soc for state in states]
    car_is_charging = [state.charger_state.car_is_charging for state in states]
    charge_is_override = [state.charger_state.charge_is_override for state in states]

    df = pd.DataFrame(
        {
            "Time": times,
            "State of Charge": socs,
            "Car is Charging": car_is_charging,
            "Charge is Override": charge_is_override,
        }
    )

    # Only reset index if one exists, otherwise just return the dataframe
    if df.index.name is not None or not df.index.equals(
        pd.RangeIndex(start=0, stop=len(df))
    ):
        return df.reset_index()
    return df


def plot_charge_forecast(states: list[CombinedState], current_time: datetime) -> Figure:
    """
    Plot a forecast of battery charge and charging periods.

    Args:
        states: List of future combined states
        current_time: Current time for reference line

    Returns:
        Figure: Plotly figure showing charge trajectory
    """
    df = _convert_states_to_dataframe(states)

    # Format SoC as percentage for display
    df["SoC %"] = df["State of Charge"] * 100

    # Create figure
    fig = px.line(
        df,
        x="Time",
        y="SoC %",
        title="Battery Charge Forecast",
        labels={"SoC %": "State of Charge (%)"},
    )

    # Customize layout
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Time",
        yaxis_title="State of Charge (%)",
        yaxis_range=[0, 100],
    )

    # Add a vertical line at the current time
    # Convert datetime to string format for plotly
    fig.add_shape(
        type="line",
        x0=current_time,
        y0=0,
        x1=current_time,
        y1=100,
        line=dict(
            color="white",
            width=2,
            dash="dash",
        ),
    )

    # Add "Now" annotation
    fig.add_annotation(x=current_time, y=100, text="Now", showarrow=False, yshift=10)

    # Add vertical rectangles for charging periods
    last_label_type = None
    for i, row in df.iterrows():
        if not row["Car is Charging"]:
            continue

        # Only add label if this is a different type than the last one
        label_type = "Override" if row["Charge is Override"] else "Scheduled"
        show_label = label_type != last_label_type
        last_label_type = label_type

        # Add rectangle shape for charging period
        rect_color = "red" if row["Charge is Override"] else "green"
        time_start = row["Time"]
        time_end = time_start + PERIOD

        fig.add_shape(
            type="rect",
            x0=time_start,
            y0=0,
            x1=time_end,
            y1=100,
            fillcolor=rect_color,
            opacity=0.2,
            layer="below",
            line_width=0,
        )

        # Add label annotation if needed
        if show_label:
            # Calculate middle point for annotation
            if isinstance(time_start, pd.Timestamp):
                # For pandas Timestamp objects
                time_mid = time_start + pd.Timedelta(PERIOD / 2)
            else:
                # For datetime objects
                time_mid = time_start + (time_end - time_start) / 2

            fig.add_annotation(
                x=time_mid,
                y=100,
                text=label_type,
                showarrow=False,
                font=dict(color=rect_color),
                yshift=10,
            )

    fig.update_traces(mode="markers+lines", line=dict(width=3))
    return fig
