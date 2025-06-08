import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.format_utils import validate_date_format, is_valid_int

def test_valid_date_with_valid_milliseconds():
    """Test a valid date and time with correct 3-digit milliseconds"""
    assert validate_date_format("07:06:2025:14:30:15:123") == True

def test_invalid_date_day_out_of_range():
    """Test invalid date (e.g., February 31st)"""
    assert validate_date_format("31:02:2025:14:30:15:123") == False

def test_invalid_milliseconds_too_short():
    """Test when milliseconds are less than 3 digits"""
    assert validate_date_format("07:06:2025:14:30:15:12") == False

def test_invalid_milliseconds_too_long():
    """Test when milliseconds are more than 3 digits"""
    assert validate_date_format("07:06:2025:14:30:15:1234") == False

def test_invalid_missing_parts():
    """Test missing the milliseconds component"""
    assert validate_date_format("07:06:2025:14:30:15") == False

def test_non_numeric_milliseconds():
    """Test milliseconds with non-numeric characters"""
    assert validate_date_format("07:06:2025:14:30:15:abc") == False

def test_valid_edge_milliseconds_000():
    """Test valid date with 000 milliseconds (edge case)"""
    assert validate_date_format("07:06:2025:14:30:15:000") == True

def test_valid_edge_milliseconds_999():
    """Test valid date with 999 milliseconds (edge case)"""
    assert validate_date_format("07:06:2025:14:30:15:999") == True

def test_valid_int():
    """Test a valid integer string"""
    assert is_valid_int("123") == True

def test_invalid_int_non_numeric():
    """Test a non-numeric string"""
    assert is_valid_int("abc") == False
