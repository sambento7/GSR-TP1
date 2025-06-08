import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.iid_utils import parse_iid
import pytest

def test_valid_iid_no_indexes():
    assert parse_iid("2.1") == {"structure": 2, "object": 1, "indexes": []}

def test_valid_iid_one_index():
    assert parse_iid("2.1.3") == {"structure": 2, "object": 1, "indexes": [3]}

def test_valid_iid_two_indexes():
    assert parse_iid("2.1.1.3") == {"structure": 2, "object": 1, "indexes": [1, 3]}

def test_iid_too_short():
    with pytest.raises(ValueError, match="IID must contain between 2 and 4 integers."):
        parse_iid("2")

def test_iid_too_long():
    with pytest.raises(ValueError, match="IID must contain between 2 and 4 integers."):
        parse_iid("1.2.3.4.5")

def test_iid_non_integer_part():
    with pytest.raises(ValueError, match="All IID parts must be integers."):
        parse_iid("2.a.3")

def test_iid_structure_zero():
    with pytest.raises(ValueError, match="Structure ID must be a positive integer."):
        parse_iid("0.1")

def test_iid_structure_negative():
    with pytest.raises(ValueError, match="Structure ID must be a positive integer."):
        parse_iid("-1.1")

def test_iid_object_negative():
    with pytest.raises(ValueError, match="Object ID must be 0 or positive."):
        parse_iid("1.-2")
