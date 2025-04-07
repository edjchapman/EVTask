"""
Configuration for the EV Charge Control Panel application.
"""

from datetime import time

# Battery Settings
DEFAULT_SOC = 0.6  # Default State of Charge (60%)
DEFAULT_TARGET_SOC = 0.8  # Default target charge level (80%)

# Charging Settings
DEFAULT_CHARGE_RATE_KW = 7.0  # Default charging rate in kW
DEFAULT_OVERRIDE_MINUTES = 60  # Default duration for override charging
BATTERY_CAPACITY_KWH = 75.0  # Battery capacity in kWh

# Scheduling Settings
DEFAULT_SCHEDULE_START = time(2, 0)  # Default schedule start (2:00 AM)
DEFAULT_SCHEDULE_END = time(5, 0)  # Default schedule end (5:00 AM)
DEFAULT_SCHEDULE_ENABLED = True  # Whether schedule is enabled by default

# Chart Settings
PERIOD_MINUTES = 30  # Time period for charge forecasting
FORECAST_PERIODS = 9  # Number of periods to forecast
