from datetime import time

from src.domain.charging import is_in_scheduled_window
from src.domain.models import ChargeSchedule


def test_is_in_scheduled_window_normal_schedule():
    """Test the scheduled window checker with a normal schedule."""
    schedule = ChargeSchedule(
        start_time=time(2, 0), end_time=time(5, 0), is_enabled=True
    )

    # Times outside the window
    assert not is_in_scheduled_window(time(1, 59), schedule)
    assert not is_in_scheduled_window(time(5, 1), schedule)
    assert not is_in_scheduled_window(time(12, 0), schedule)

    # Times inside the window
    assert is_in_scheduled_window(time(2, 0), schedule)
    assert is_in_scheduled_window(time(3, 30), schedule)
    assert is_in_scheduled_window(time(5, 0), schedule)


def test_is_in_scheduled_window_overnight_schedule():
    """Test the scheduled window checker with an overnight schedule."""
    schedule = ChargeSchedule(
        start_time=time(22, 0),  # 10 PM
        end_time=time(5, 0),  # 5 AM
        is_enabled=True,
    )

    # Times outside the window
    assert not is_in_scheduled_window(time(5, 1), schedule)
    assert not is_in_scheduled_window(time(12, 0), schedule)
    assert not is_in_scheduled_window(time(21, 59), schedule)

    # Times inside the window
    assert is_in_scheduled_window(time(22, 0), schedule)
    assert is_in_scheduled_window(time(23, 30), schedule)
    assert is_in_scheduled_window(time(0, 1), schedule)
    assert is_in_scheduled_window(time(4, 59), schedule)
    assert is_in_scheduled_window(time(5, 0), schedule)


def test_is_in_scheduled_window_disabled_schedule():
    """Test that disabled schedules always return False."""
    schedule = ChargeSchedule(
        start_time=time(2, 0),
        end_time=time(5, 0),
        is_enabled=False,  # Disabled
    )

    # Even times inside what would be the window return False
    assert not is_in_scheduled_window(time(2, 0), schedule)
    assert not is_in_scheduled_window(time(3, 30), schedule)
    assert not is_in_scheduled_window(time(5, 0), schedule)
