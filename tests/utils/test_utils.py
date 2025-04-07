from datetime import datetime
from unittest.mock import MagicMock

from src.utils import get_current_time_to_nearest_30_minutes


def test_get_current_time_to_nearest_30_minutes_exact(monkeypatch):
    """Test time rounding when current time is exactly on a 30-minute mark."""
    # Set up mock to return a specific time
    fixed_time = datetime(2025, 1, 1, 12, 0, 15)  # 12:00:15

    mock_datetime = MagicMock()
    mock_datetime.now.return_value = fixed_time
    monkeypatch.setattr("src.utils.datetime", mock_datetime)

    # The result should be rounded to 12:00
    result = get_current_time_to_nearest_30_minutes()
    expected = datetime(2025, 1, 1, 12, 0, 0)

    assert result.hour == expected.hour
    assert result.minute == expected.minute
    assert result.second == expected.second


def test_get_current_time_to_nearest_30_minutes_round_up(monkeypatch):
    """Test time rounding when current time should round up to next 30-minute mark."""
    # Set up mock to return a time that should round up
    fixed_time = datetime(2025, 1, 1, 12, 20, 0)  # 12:20:00

    mock_datetime = MagicMock()
    mock_datetime.now.return_value = fixed_time
    monkeypatch.setattr("src.utils.datetime", mock_datetime)

    # The result should round up to 12:30
    result = get_current_time_to_nearest_30_minutes()
    expected = datetime(2025, 1, 1, 12, 30, 0)

    assert result.hour == expected.hour
    assert result.minute == expected.minute
    assert result.second == expected.second


def test_get_current_time_to_nearest_30_minutes_round_down(monkeypatch):
    """Test time rounding when current time should round down to previous 30-minute mark."""
    # Set up mock to return a time that should round down
    fixed_time = datetime(2025, 1, 1, 12, 10, 0)  # 12:10:00

    mock_datetime = MagicMock()
    mock_datetime.now.return_value = fixed_time
    monkeypatch.setattr("src.utils.datetime", mock_datetime)

    # The result should round down to 12:00
    result = get_current_time_to_nearest_30_minutes()
    expected = datetime(2025, 1, 1, 12, 0, 0)

    assert result.hour == expected.hour
    assert result.minute == expected.minute
    assert result.second == expected.second


def test_get_current_time_to_nearest_30_minutes_exact_half_hour(monkeypatch):
    """Test time rounding when current time is exactly on a half-hour mark."""
    # Set up mock to return a specific time
    fixed_time = datetime(2025, 1, 1, 12, 30, 45)  # 12:30:45

    mock_datetime = MagicMock()
    mock_datetime.now.return_value = fixed_time
    monkeypatch.setattr("src.utils.datetime", mock_datetime)

    # The result should be rounded to 12:30
    result = get_current_time_to_nearest_30_minutes()
    expected = datetime(2025, 1, 1, 12, 30, 0)

    assert result.hour == expected.hour
    assert result.minute == expected.minute
    assert result.second == expected.second
