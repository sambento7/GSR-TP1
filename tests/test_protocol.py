import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from protocol import Protocol

def test_encode_iid_basic():
    p = Protocol()
    result = p.encode_iid([1, 2, 3])
    assert result == ("1\0" + "2\0" + "3\0").encode("ascii")

def test_decode_iid_basic():
    p = Protocol()
    raw = ("4\0" + "5\0" + "6\0").encode("ascii")
    result = p.decode_iid(raw)
    assert result == [4, 5, 6]

def test_encode_decode_cycle():
    p = Protocol()
    original = [10, 0, 99]
    encoded = p.encode_iid(original)
    decoded = p.decode_iid(encoded)
    assert decoded == original

def test_encode_empty_list():
    p = Protocol()
    result = p.encode_iid([])
    assert result == "".encode("ascii")

def test_decode_empty_bytes():
    p = Protocol()
    result = p.decode_iid("".encode("ascii"))
    assert result == []

def test_decode_invalid_format():
    p = Protocol()
    try:
        p.decode_iid(('abc\0').encode("ascii"))
        assert False, "Should raise ValueError"
    except ValueError:
        pass  # Expected behavior

def test_decode_non_terminated_iid():
    p = Protocol()
    try:
        p.decode_iid(('1\02\03').encode("ascii"))  # Missing termination character
        assert False, "Should raise ValueError"
    except ValueError:
        pass  # Expected behaviorsim
    

def test_decode_iid_with_spaces():
    p = Protocol()
    try:
        p.decode_iid("1 \0 2\0".encode("ascii"))
        assert False, "Should raise ValueError"
    except ValueError:
        pass


