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
INVALID_TAG = b'badtag\0'

# Componentes base
msg_type_get = b"G"
msg_type_set = b"S"
invalid_msg_type = b"X"

timestamp = (
    b"T\0" + b"7\0" +
    b"01\0" + b"01\0" + b"2024\0" + 
    b"12\0" + b"00\0" + b"00\0" + b"000\0"
)

invalid_timestamp_type = (
    b"I\0" + b"7\0" +
    b"01\0" + b"01\0" + b"2024\0" +
    b"12\0" + b"00\0" + b"00\0" + b"00\0"
)
invalid_timestamp_size = (
    b"T\0" + b"5\0" +
    b"01\0" + b"01\0" + b"2024\0" +
    b"12\0" + b"00\0" + b"00\0" + b"00\0"
)
invalid_timestamp_component = (
    b"T\0" + b"7\0" +
    b"aa\0" + b"01\0" + b"2024\0" +
    b"12\0" + b"00\0" + b"00\0" + b"00\0"
)
invalid_timestamp_date_format = (
    b"T\0" + b"7\0" +
    b"01\0" + b"01\0" + b"2024\0" +
    b"12\0" + b"00\0" + b"00\0" + b"00\0"
)

message_id = b"abcdefgh12345678\0"
invalid_msg_id = b"shortid\0"

iid_section = b"1\0" + b"D\0" + b"2\0" + b"1\0" + b"1\0"
invalid_iid_section_size = b"a\0" + b"D\0" + b"2\0" + b"1\0"
invalid_iid_section_component_type = b"1\0" + b"I\0" + b"2\0" + b"1\0" + b"1\0"
invalid_iid_section_component_size = b"1\0" + b"D\0" + b"1\0" + b"1\0" + b"1\0"
invalid_iid_section_component_value = b"1\0" + b"D\0" + b"2\0" + b"a\0" + b"1\0"

value_empty = b"0\0"
value_valid_i = b"1\0" + b"I\0" + b"1\0" + b"42\0"
value_valid_s = b"1\0" + b"S\0" + b"1\0" + b"ON\0"
value_valid_t = b"1\0" + b"T\0" + b"7\0" + b"01\0" + b"01\0" + b"2024\0" + b"12\0" + b"00\0" + b"00\0" + b"000\0"
invalid_value_more_than_one = b"2\0" + b"I\0" + b"1\0" + b"42\0" + b"I\0" + b"1\0" + b"43\0"
invalid_value_size = b"a\0" + b"I\0" + b"1\0" + b"42\0"
invalid_value_component_type = b"1\0" + b"D\0" + b"1\0" + b"42\0"
invalid_value_component_size = b"1\0" + b"I\0" + b"a\0" + b"42\0"
invalid_value_i_componente_size = b"1\0" + b"I\0" + b"2\0" + b"42\0"
invalid_value_s_componente_size = b"1\0" + b"S\0" + b"2\0" + b"42\0"
invalid_value_t_componente_size =  b"1\0" + b"T\0" + b"5\0" + b"2024\0" + b"12\0" + b"00\0" + b"00\0" + b"000\0"
invalid_value_component_value = b"1\0" + b"I\0" + b"1\0" + b"a\0"
invalid_value_component_t_value = (
    b"1\0" + b"T\0" + b"7\0" +
    b"01\0" + b"01\0" + b"2024\0" +
    b"12\0" + b"00\0" + b"00\0" + b"00\0"
)

error_list_empty = b"0\0"
invalid_error_list_size = b"a\0"
unsupported_error_list_size = b"2\0"

######################
# TESTES GERAIS
######################

def test_valid_get():
    p = Protocol()
    msg = TAG + msg_type_get + timestamp + message_id + iid_section + value_empty + error_list_empty
    result = p.decode_message(msg)
    assert result['type'] == 'G'
    assert result['timestamp'] == "01:01:2024:12:00:00:000"
    assert result['message_id'] == "abcdefgh12345678"
    assert result['iid_list'] == [[1, 1]]
    assert result['value_list'] == []
    assert result['error_list'] == []

def test_valid_set_with_int():
    p = Protocol()
    msg = TAG + msg_type_set + timestamp + message_id + iid_section + value_valid_i + error_list_empty
    result = p.decode_message(msg)
    assert result['type'] == 'S'
    assert result['value_list'][0][0] == 'I'

def test_valid_set_with_string():
    p = Protocol()
    msg = TAG + msg_type_set + timestamp + message_id + iid_section + value_valid_s + error_list_empty
    result = p.decode_message(msg)
    assert result['value_list'][0][0] == 'S'

def test_valid_set_with_timestamp():
    p = Protocol()
    msg = TAG + msg_type_set + timestamp + message_id + iid_section + value_valid_t + error_list_empty
    result = p.decode_message(msg)
    assert result['value_list'][0][0] == 'T'

def test_invalid_tag():
    p = Protocol()
    msg = INVALID_TAG + msg_type_get + timestamp + message_id + iid_section + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise InvalidTagError"
    except InvalidTagError as e:
        assert "Invalid message tag." == str(e)
        pass  # Expected behavior

def test_invalid_message_type():
    p = Protocol()
    msg = TAG + invalid_msg_type + timestamp + message_id + iid_section + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise UnknownMessageTypeError"
    except UnknownMessageTypeError as e:
        assert "Invalid message type" in str(e)
        pass  # Expected behavior

def test_invalid_timestamp_type():
    p = Protocol()
    msg = TAG + msg_type_get + invalid_timestamp_type + message_id + iid_section + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Expected timestamp type 'T'" in str(e)
        pass  # Expected behavior

def test_invalid_timestamp_size():
    p = Protocol()
    msg = TAG + msg_type_get + invalid_timestamp_size + message_id + iid_section + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Invalid timestamp length" in str(e)
        pass  # Expected behavior

def test_invalid_timestamp_component():
    p = Protocol()
    msg = TAG + msg_type_get + invalid_timestamp_component + message_id + iid_section + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Invalid timestamp component format" in str(e)
        pass  # Expected behavior

def test_invalid_timestamp_date_format():
    p = Protocol()
    msg = TAG + msg_type_get + invalid_timestamp_date_format + message_id + iid_section + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Invalid timestamp format." == str(e)
        pass  # Expected behavior

def test_invalid_message_id():
    p = Protocol()
    msg = TAG + msg_type_get + timestamp + invalid_msg_id + iid_section + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Invalid message ID length. Expected 16 characters." == str(e)
        pass  # Expected behavior

def test_invalid_iid_section_size():
    p = Protocol()
    msg = TAG + msg_type_get + timestamp + message_id + invalid_iid_section_size + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Invalid IID List length format." == str(e)
        pass  # Expected behavior

def test_invalid_iid_section_type():
    p = Protocol()
    msg = TAG + msg_type_get + timestamp + message_id + invalid_iid_section_component_type + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Expected IID type 'D'" in str(e)
        pass  # Expected behavior

def test_invalid_iid_section_size():
    p = Protocol()
    msg = TAG + msg_type_get + timestamp + message_id + invalid_iid_section_component_size + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Invalid IID length." in str(e)
        pass  # Expected behavior

def test_invalid_iid_section_value():
    p = Protocol()
    msg = TAG + msg_type_get + timestamp + message_id + invalid_iid_section_component_value + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Invalid IID component format." in str(e)
        pass  # Expected behavior

def test_invalid_value_size():
    p = Protocol()
    msg = TAG + msg_type_get + timestamp + message_id + iid_section + invalid_value_size + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Invalid Value List length format." == str(e)
        pass  # Expected behavior

def test_invalid_error_list_size():
    p = Protocol()
    msg = TAG + msg_type_get + timestamp + message_id + iid_section + value_empty + invalid_error_list_size
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"

    except DecodingError as e:
        assert "Invalid Error List length format." == str(e)
        pass  # Expected behavior

def test_unsupported_error_list_size():
    p = Protocol()
    msg = TAG + msg_type_get + timestamp + message_id + iid_section + value_empty + unsupported_error_list_size
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Error List should be empty" in str(e)
        pass  # Expected behavior

def test_missing_message_id():
    p = Protocol()
    msg = TAG + msg_type_get + timestamp + iid_section + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False
    except DecodingError as e:
        assert "Invalid message ID length" in str(e)

def test_repeated_terminators():
    p = Protocol()
    bad_ts = b"T\0\0" + b"7\0" + b"01\0" * 7
    msg = TAG + msg_type_get + bad_ts + message_id + iid_section + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False
    except DecodingError:
        pass

######################
# TESTES PARA GET
######################

def test_get_with_value_should_fail():
    p = Protocol()
    msg = TAG + msg_type_get + timestamp + message_id + iid_section + value_valid_i + error_list_empty
    try:
        p.decode_message(msg)
        assert False
    except DecodingError as e:
        assert "Get request should not contain values." == str(e)


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

def test_get_iid_with_zero_components():
    p = Protocol()
    bad_iid = b"1\0" + b"D\0" + b"0\0"
    msg = TAG + msg_type_get + timestamp + message_id + bad_iid + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False
    except DecodingError as e:
        assert "Invalid IID length." in str(e)

def test_get_iid_with_too_many_components():
    p = Protocol()
    bad_iid = b"1\0" + b"D\0" + b"5\0" + b"1\0" * 5
    msg = TAG + msg_type_get + timestamp + message_id + bad_iid + value_empty + error_list_empty
    try:
        p.decode_message(msg)
        assert False
    except DecodingError as e:
        assert "Invalid IID length." in str(e)

def test_get_with_extra_trailing_data():
    p = Protocol()
    msg = TAG + msg_type_get + timestamp + message_id + iid_section + value_empty + error_list_empty + b"EXTRA\0"
    try:
        p.decode_message(msg)
        assert False
    except DecodingError as e:
        assert "Extra data found after expected end of message." in str(e)

######################
# TESTES PARA SET
######################


def test_set_invalid_value_size():
    p = Protocol()
    msg = TAG + msg_type_set + timestamp + message_id + iid_section + invalid_value_more_than_one + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise IIDValueMismatchError"
    except IIDValueMismatchError as e:
        assert "Number of values does not match number of IIDs." == str(e)
        pass  # Expected behavior

def test_invalid_value_type():
    p = Protocol()
    msg = TAG + msg_type_set + timestamp + message_id + iid_section + invalid_value_component_type + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise InvalidValueTypeError"
    except InvalidValueTypeError as e:
        assert "Unsupported value type 'D' in value list for message type S." == str(e)
        pass  # Expected behavior

def test_invalid_value_component_size():
    p = Protocol()
    msg = TAG + msg_type_set + timestamp + message_id + iid_section + invalid_value_component_size + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Invalid value length format." in str(e)
        pass  # Expected behavior

def test_invalid_value_i_component_size():
    p = Protocol()
    msg = TAG + msg_type_set + timestamp + message_id + iid_section + invalid_value_i_componente_size + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Type I must have length 1." in str(e)
        pass  # Expected behavior

def test_invalid_value_s_component_size():
    p = Protocol()
    msg = TAG + msg_type_set + timestamp + message_id + iid_section + invalid_value_s_componente_size + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Type S must have length 1." in str(e)
        pass  # Expected behavior

def test_invalid_value_t_component_size():
    p = Protocol()
    msg = TAG + msg_type_set + timestamp + message_id + iid_section + invalid_value_t_componente_size + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Invalid timestamp length for S messages." in str(e)
        pass  # Expected behavior

def test_invalid_value_i_component_value():
    p = Protocol()
    msg = TAG + msg_type_set + timestamp + message_id + iid_section + invalid_value_component_value + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Invalid value format." in str(e)
        pass  # Expected behavior

def test_invalid_value_t_component_value():
    p = Protocol()
    msg = TAG + msg_type_set + timestamp + message_id + iid_section + invalid_value_component_t_value + error_list_empty
    try:
        p.decode_message(msg)
        assert False, "Should raise DecodingError"
    except DecodingError as e:
        assert "Invalid date timestamp format." in str(e)
        pass  # Expected behavior

def test_set_more_values_than_iids():
    p = Protocol()
    bad_values = b"2\0" + b"I\0" + b"1\0" + b"42\0" + b"I\0" + b"1\0" + b"43\0"
    msg = TAG + msg_type_set + timestamp + message_id + iid_section + bad_values + error_list_empty
    try:
        p.decode_message(msg)
        assert False
    except IIDValueMismatchError as e:
        assert "Number of values does not match number of IIDs." in str(e)

def test_set_invalid_date_value():
    p = Protocol()
    bad_ts = (
        b"1\0" + b"T\0" + b"7\0" +
        b"01\0" + b"13\0" + b"2024\0" +
        b"99\0" + b"00\0" + b"00\0" + b"000\0"
    )
    msg = TAG + msg_type_set + timestamp + message_id + iid_section + bad_ts + error_list_empty
    try:
        p.decode_message(msg)
        assert False
    except DecodingError as e:
        assert "Invalid date timestamp format." in str(e)

def test_set_string_with_non_ascii():
    p = Protocol()
    bad_str = b"1\0" + b"S\0" + b"1\0" + "Olá\0".encode("utf-8")
    msg = TAG + msg_type_set + timestamp + message_id + iid_section + bad_str + error_list_empty
    try:
        p.decode_message(msg)
        assert False
    except UnicodeDecodeError:
        pass  # Expected, string not ASCII




def test_encode_response_message():
    p = Protocol()
    timestamp = "01:12:00:00:000"
    message_id = "abcdefgh12345678"
    iid_list = [[1, 2]]
    value_list = [('I', ['99'])]
    error_list = []

    encoded = p.encode_message('R', timestamp, message_id, iid_list, value_list, error_list)

    assert isinstance(encoded, bytes)
    assert encoded.startswith(TAG)
    assert b'R' in encoded
    assert b'99\0' in encoded
    assert b'I\0' in encoded


def test_encode_notification_message():
    p = Protocol()
    timestamp = "15:08:30:00:500"
    message_id = "notifmsg00000001"
    iid_list = [[3, 4]]
    value_list = [('S', ['OFF'])]
    error_list = []

    encoded = p.encode_message('N', timestamp, message_id, iid_list, value_list, error_list)

    assert isinstance(encoded, bytes)
    assert encoded.startswith(TAG)
    assert b'N' in encoded
    assert b'OFF\0' in encoded
    assert b'S\0' in encoded

