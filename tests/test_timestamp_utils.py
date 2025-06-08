import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.timestamp_utils import generate_date_timestamp, generate_uptime_timestamp
import time

def test_generate_date_timestamp():
    timestamp = generate_date_timestamp()
    parts = timestamp.split(":")
    
    # Verify number of fields
    assert len(parts) == 7, "Timestamp should have 7 digits seperated for ':'"
    
    # Verify each part is numeric
    for part in parts:
        assert part.isdigit(), f"The field '{part}' must be numeric"
    
    # Verify ranges of each part
    day, month, year, hour, minute, second, ms = map(int, parts)
    assert 1 <= day <= 31
    assert 1 <= month <= 12
    assert 0 <= hour <= 23
    assert 0 <= minute <= 59
    assert 0 <= second <= 59
    assert 0 <= ms <= 999

def test_generate_date_timestamp_with_explicit_time():
    fixed_time = 1717795200.0  # This corresponds to 2024-06-07 00:00:00 UTC
    timestamp1 = generate_date_timestamp(fixed_time)
    timestamp2 = generate_date_timestamp(fixed_time)

    
    assert timestamp1 == timestamp2, "Timestamps generated with the same input time should match"

    
    parts = timestamp1.split(":")
    assert len(parts) == 7
    for part in parts:
        assert part.isdigit()


def test_generate_uptime_timestamp_format():
    start_time = time.time() - 93784.456  # simulates ~1 dia, 2h, 2min, 64s of uptime

    timestamp = generate_uptime_timestamp(start_time)
    parts = timestamp.split(":")

    # Verify number of fields
    assert len(parts) == 5, "Timestamp should have 5 digits seperated for':'"

    # Verify each part is numeric
    for part in parts:
        assert part.isdigit(), f"The fiield '{part}' must be numeric"

    # Verify ranges of each part
    days, hours, minutes, seconds, ms = map(int, parts)
    assert days >= 0
    assert 0 <= hours <= 23
    assert 0 <= minutes <= 59
    assert 0 <= seconds <= 59
    assert 0 <= ms <= 999