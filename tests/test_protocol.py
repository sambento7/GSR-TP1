import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from protocol import Protocol
from exceptions import (
    DecodingError, InvalidTagError, UnknownMessageTypeError,
    InvalidValueTypeError, IIDValueMismatchError
)

TAG = b'kdk847ufh84jg87g\0'

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
        pass  # Expected behavior

TAG = b'kdk847ufh84jg87g\0'

# Componentes base
msg_type_get = b"G"
msg_type_set = b"S"

timestamp = (
    b"T\0" + b"7\0" +
    b"01\0" + b"01\0" + b"2024\0" + b"12\0" +
    b"00\0" + b"00\0" + b"000\0"
)

message_id = b"abcdefgh12345678\0"
iid_section = b"1\0" + b"D\0" + b"2\0" + b"1\0" + b"1\0"
value_empty = b"0\0"
value_valid_i = b"1\0" + b"I\0" + b"1\0" + b"42\0"
value_valid_s = b"1\0" + b"S\0" + b"1\0" + b"ON\0"
value_valid_t = b"1\0" + b"T\0" + b"7\0" + b"01\0" + b"01\0" + b"2024\0" + b"12\0" + b"00\0" + b"00\0" + b"000\0"
error_list_empty = b"0\0"

def make_message(msg_type, values):
    return TAG + msg_type + timestamp + message_id + iid_section + values + error_list_empty

######################
# TESTES PARA GET
######################

def test_valid_get():
    p = Protocol()
    msg = make_message(msg_type_get, value_empty)
    result = p.decode_message(msg)
    assert result['type'] == 'G'

def test_get_with_value_should_fail():
    p = Protocol()
    msg = make_message(msg_type_get, value_valid_i)
    try:
        p.decode_message(msg)
        assert False
    except DecodingError as e:
        assert "should not contain values" in str(e)

def test_get_with_error_list_not_empty():
    p = Protocol()
    bad_error_list = b"1\0" + b"3\0"
    msg = (
        TAG +
        msg_type_get +
        timestamp +
        message_id +
        iid_section +
        value_empty +
        bad_error_list  # substitui diretamente só esta parte
    )
    try:
        p.decode_message(msg)
        assert False
    except DecodingError as e:
        assert "Error List should be empty" in str(e)


######################
# TESTES PARA SET
######################

def test_valid_set_with_int():
    p = Protocol()
    msg = make_message(msg_type_set, value_valid_i)
    result = p.decode_message(msg)
    assert result['type'] == 'S'
    assert result['value_list'][0][0] == 'I'

def test_valid_set_with_string():
    p = Protocol()
    msg = make_message(msg_type_set, value_valid_s)
    result = p.decode_message(msg)
    assert result['value_list'][0][0] == 'S'

def test_valid_set_with_timestamp():
    p = Protocol()
    msg = make_message(msg_type_set, value_valid_t)
    result = p.decode_message(msg)
    assert result['value_list'][0][0] == 'T'

def test_set_mismatched_values():
    p = Protocol()
    bad_value = b"2\0" + b"I\0" + b"1\0" + b"5\0" + b"I\0" + b"1\0" + b"6\0"
    msg = make_message(msg_type_set, bad_value)
    try:
        p.decode_message(msg)
        assert False
    except IIDValueMismatchError:
        pass

def test_set_invalid_value_type():
    p = Protocol()
    bad_value = b"1\0" + b"X\0" + b"1\0" + b"9\0"
    msg = make_message(msg_type_set, bad_value)
    try:
        p.decode_message(msg)
        assert False
    except InvalidValueTypeError:
        pass

def test_set_invalid_iid_component():
    p = Protocol()
    bad_iid = b"1\0" + b"D\0" + b"2\0" + b"x\0" + b"1\0"
    msg = TAG + msg_type_set + timestamp + message_id + bad_iid + value_valid_i + error_list_empty
    try:
        p.decode_message(msg)
        assert False
    except DecodingError as e:
        assert "Invalid IID component format" in str(e)
