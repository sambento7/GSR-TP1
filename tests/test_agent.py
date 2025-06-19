# tests/test_agent.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from agent import Agent
from protocol import Protocol
from exceptions import (
    LSNMPvSError,
    DecodingError,
    InvalidTagError,
    UnknownMessageTypeError,
    IIDValueMismatchError
)
from devices.sensor import Sensor
from devices.actuator import Actuator
from utils.timestamp_utils import generate_date_timestamp

# Constantes
TAG             = Protocol.TAG
MESSAGE_ID_STR  = "abcdefgh12345678"   # sem o '\0'
IID_SENSOR_VAL  = [2, 3, 1]             # Grupo=2 (Sensors), Obj=3 (value), Índice=1

@pytest.mark.parametrize("exc, expected", [
    (DecodingError("e"),           DecodingError.code),
    (InvalidTagError("e"),         InvalidTagError.code),
    (UnknownMessageTypeError("e"), UnknownMessageTypeError.code),
    (IIDValueMismatchError("e"),   IIDValueMismatchError.code),
    (LSNMPvSError("e"),            1),  # fallback
])
def test_map_exception_to_code(exc, expected):
    agent = Agent(host='localhost', port=0)
    assert agent._map_exception_to_code(exc) == expected

def test_register_devices():
    s = Sensor(id="S1", type="temp", min_value=0, max_value=100)
    a = Actuator(id="A1", type="light", min_value=0, max_value=10)
    agent = Agent(host='localhost', port=0, sensors=[s], actuators=[a])

    assert "S1" in agent.mib.sensors
    assert agent.mib.device_info["nSensors"] == 1
    assert "A1" in agent.mib.actuators
    assert agent.mib.device_info["nActuators"] == 1

def test_handle_request_get_with_real_sensor(monkeypatch):
    sensor = Sensor(id="T", type="temp", min_value=0, max_value=100)
    monkeypatch.setattr(sensor, 'read_value', lambda: 42)

    agent = Agent(host='localhost', port=0, sensors=[sensor], actuators=[])

    proto = Protocol()
    ts = generate_date_timestamp()
    raw = proto.encode_message(
        msg_type='G',
        timestamp=ts,
        message_id=MESSAGE_ID_STR,
        iid_list=[IID_SENSOR_VAL],
        value_list=None,
        error_list=None
    )

    resp = agent.handle_request(raw)

    assert resp.startswith(TAG + b'R')
    assert b'I\0' in resp
    assert b'42\0' in resp

def test_handle_request_set_with_dummy_mib():
    class DummyMIB:
        start_time = 0
        def get_value_by_iid(self, iid):    raise RuntimeError()
        def set_value_by_iid(self, iid, v): return ('S',['ON'])
        def register_sensor(self, s): pass
        def register_actuator(self, a): pass

    agent = Agent(host='localhost', port=0)
    agent.mib = DummyMIB()

    proto = Protocol()
    ts = generate_date_timestamp()
    raw = proto.encode_message(
        msg_type='S',
        timestamp=ts,
        message_id=MESSAGE_ID_STR,
        iid_list=[[1,1]],
        value_list=[('S',['ON'])],
        error_list=[]
    )

    resp = agent.handle_request(raw)
    assert resp.startswith(TAG + b'R')
    assert b'S\0' in resp and b'ON\0' in resp

def test_send_notification():
    agent = Agent(host='localhost', port=0, manager_address=('127.0.0.1', 9999))
    class FakeSock:
        def __init__(self): self.sent = []
        def sendto(self, pdu, addr): self.sent.append((pdu, addr))
    agent.sock = FakeSock()

    iid_list   = [[1,1]]
    value_list = [('S',['OFF'])]
    error_list = [0]
    agent.send_notification(iid_list, value_list, error_list)

    assert len(agent.sock.sent) == 1
    pdu, addr = agent.sock.sent[0]
    assert addr == ('127.0.0.1', 9999)
    assert pdu.startswith(TAG + b'N')
    assert b'S\0' in pdu
    assert b'OFF\0' in pdu
