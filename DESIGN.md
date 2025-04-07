# Design Document - EV Charge Control Panel

## Overview

This document outlines the design decisions and architecture for the Axle Energy EV Charge Control Panel, 
which enables users to monitor and control EV charging, including scheduled and immediate charging options.

## Architecture

The application follows a clean architecture pattern with:

1. **Data Models**: Core dataclasses representing state
2. **Backend Logic**: Business rules for charging behavior
3. **UI Layer**: Streamlit interface for user interaction
4. **Visualization**: Charge forecasting and status display

## Components

### Data Models

- **BatteryState**: Represents the current and target state of charge
- **ChargerState**: Tracks charging status, rate, and override details
- **ChargeSchedule**: Defines scheduled charging windows
- **DemoAdminState**: Test controls for simulating car and time state
- **CombinedState**: Aggregates state for forecasting and visualization

### State Management

The application uses Streamlit's session state for persistence across interactions:

```python
import streamlit as st

battery_state = st.session_state.battery_state    # Battery charge status
charger_state = st.session_state.charger_state    # Charging status and configuration
charge_schedule = st.session_state.charge_schedule  # Scheduled charging windows
demo_state = st.session_state.demo_state       # Demo/simulation controls
```

### Charging Logic

The charging decisions follow this priority:

1. Unplugged cars never charge
2. Override charging takes precedence when active (time-limited)
3. Scheduled charging applies within configured windows
4. Battery charges until target SoC is reached

### Key Flows

#### Charge Override Flow
1. User presses "Start Charging"
2. System sets `charge_is_override = True`
3. System calculates override end time (current time + override duration)
4. When override expires, system reverts to schedule

#### Schedule Disabling Flow
1. User stops a scheduled charge
2. System sets `schedule.is_enabled = False`
3. Schedule remains disabled until next morning

## Design Decisions

### 1. Time-Based Simulation
The application treats time as a simulation parameter rather than using real-time to enable testing different scenarios.

### 2. State of Charge Model
We model the SoC as a simple linear function based on charging rate and time, which is sufficient for demonstrating the interface.

### 3. Data Visualization
The charge forecast visualization shows:
- Current SoC
- Projected SoC
- Charging windows (distinguishing override vs. scheduled charging)

### 4. Incremental Charging
The system calculates charge state in 30-minute increments to balance forecast accuracy against complexity.

## Future Improvements

1. **Variable Rate Charging**: Implement time-of-use electricity pricing
2. **Smart Scheduling**: Algorithm to optimize charging times based on electricity cost
3. **Charge History**: Track historical charging data and display statistics
4. **Multiple Vehicle Support**: Extend to manage multiple EVs with shared charging infrastructure
