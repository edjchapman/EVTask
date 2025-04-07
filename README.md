# EV Charge Control Panel

It implements a Charge Control Panel for a whitelabel EV charging application where users can monitor 
their vehicle's charge state and manage scheduled and immediate charging behavior.

For detailed technical architecture and implementation details, see the [DESIGN.md](DESIGN.md) document.

## 🚗 Features

- Display current battery State of Charge (SoC)
- Show scheduled charging window (default: 2-5am)
- Project future battery charge based on schedule
- Override scheduled charging with immediate 60-minute charging
- Detect when the car is plugged in or unplugged
- Track charging source (schedule vs. override)
- Visualize charging forecast with interactive chart

## 🏗️ Architecture

This application uses a domain-driven design approach with clean separation of concerns:

```
src/
  ├── app.py                 # Application entry point
  ├── config.py              # Configuration settings
  ├── domain/                # Domain models and business logic
  │   ├── battery.py         # Battery state and charging logic
  │   ├── charging.py        # Charging windows and state management
  │   └── models.py          # Core domain data models
  ├── services/              # Application services
  │   ├── scheduler.py       # Charge scheduling service
  │   └── state_manager.py   # Session state management
  └── ui/                    # User interface components
      ├── components.py      # Reusable UI components
      ├── pages.py           # Page layout definitions
      └── visualization.py   # Chart and forecast visualization
```

## ⚙️ Setup & Installation

### Option 1: Using Docker

1. Build and run the Docker container:
   ```bash
   docker compose up
   ```
2. Open the application at http://localhost:8501

### Option 2: Using Python Virtual Environment

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run src/app.py
   ```
4. Open the application at http://localhost:8501

## 🧪 Testing

This project includes comprehensive unit and functional tests. 

The test structure mirrors the application architecture for better maintainability.

### Running Tests

#### Option 1: Using Docker

Run all tests:
```bash
docker compose run --rm streamlit_app pytest
```

Run specific test categories:
```bash
# Domain layer tests
docker compose run --rm streamlit_app pytest tests/domain/

# Services layer tests
docker compose run --rm streamlit_app pytest tests/services/

# UI layer tests
docker compose run --rm streamlit_app pytest tests/ui/

# Functional tests
docker compose run --rm streamlit_app pytest tests/functional/
```

Check test coverage:
```bash
docker compose run --rm streamlit_app pytest --cov=src tests/
```

#### Option 2: Using Python Virtual Environment

Run all tests:
```bash
pytest
```

Run specific test categories:
```bash
# Domain layer tests
pytest tests/domain/

# Services layer tests
pytest tests/services/

# UI layer tests
pytest tests/ui/

# Functional tests
pytest tests/functional/
```

Check test coverage:
```bash
pytest --cov=src tests/
```

## 🤔 Design Decisions

### Technical Approach

1. **Domain-Driven Design**: Applied DDD principles to separate core domain logic from application services and presentation logic.

2. **State Management**: Used Streamlit's session state for persistent user session data, with a centralized state manager to ensure consistent state access patterns.

3. **Forecasting**: Implemented a time-based charging forecast that predicts future battery state based on current settings and charging parameters.

4. **UI Reactivity**: Made UI components that reactively respond to changes in the car's plug state and charging status.

5. **Testing Strategy**: Built a comprehensive test suite covering all layers of the application:
   - Domain tests: Verify core business logic
   - Service tests: Ensure application services function correctly
   - UI tests: Confirm user interface components render appropriately
   - Functional tests: Validate key user flows work end-to-end

### Design Considerations

#### Prioritized Features

- **Essential Charging Management**: Focused on implementing the core charging control functionality first - scheduled charging, overrides, and state tracking.
- **Data Visualization**: Added a forecast chart to help users visualize how their battery will charge over time.
- **User Experience**: Prioritized clear status indicators and intuitive controls based on the car's current state.

#### Simplifications

- **Mocked Data**: Used static data for charging schedule and rates instead of connecting to a real pricing API.
- **No Authentication**: Simplified by not implementing user authentication or multi-user management.
- **Limited Settings**: Focused on core functionality rather than extensive configuration options.

#### Support for End-User Experience

- **Mobile-Friendly UI**: Used Streamlit's responsive layout to ensure the application works on both desktop and mobile devices.
- **Clear Status Indicators**: Made the charging status and plug state immediately visible.
- **Intuitive Controls**: Disabled buttons when actions aren't applicable to prevent user confusion.
- **Visual Feedback**: Added toast notifications to confirm user actions and explain state changes.

## 📝 Future Enhancements

Given more time, these features would enhance the application:

1. User authentication and multi-vehicle support
2. Dynamic electricity pricing integration
3. Historical charging data and analytics
4. Customizable charging preferences
5. More sophisticated battery degradation modeling
6. Push notifications for charging events

## 📚 Tech Stack

- **Frontend**: Streamlit
- **Data Visualization**: Plotly
- **Testing**: Pytest
- **Containerization**: Docker