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
    IIDValueMismatchError,
    UnsupportedValueError,
    NoDevicesRegisteredError
)
from devices.sensor import Sensor
from devices.actuator import Actuator
from utils.timestamp_utils import generate_date_timestamp

# Constantes
TAG             = Protocol.TAG
MESSAGE_ID_STR  = "abcdefgh12345678"   # sem o '\0'
IID_SENSOR_VAL  = [2, 3, 1]            # Grupo=2 (Sensors), Obj=3 (status), Índice=1
IID_ACT_STATUS  = [3, 3, 1]            # Grupo=3 (Actuators), Obj=3 (status), Índice=1
IID_DEV_BEACON  = [1, 3]               # Grupo=1 (Device), Obj=3 (beaconRate)

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

def test_handle_request_get_with_real_sensor():
    sensor = Sensor(id="T", type="temp", min_value=0, max_value=100)
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

    # executa o GET
    resp = agent.handle_request(raw)

    # decodifica com o protocolo para inspecionar campos estruturados
    decoded = proto.decode_message(resp)

    # Verificações estáveis:
    assert decoded['type'] == 'R'
    assert decoded['iid_list'] == [IID_SENSOR_VAL]

    # deve haver EXACTLY 1 valor e 1 código de erro (0 = sem erro)
    assert len(decoded['value_list']) == 1
    assert decoded['error_list'] == [0]

    # verifica que veio um inteiro e está no intervalo [0,100]
    val_type, parts = decoded['value_list'][0]
    assert val_type == 'I'
    value = int(parts[0])
    assert 0 <= value <= 100

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

# —————————————————————————————————————————————————————
#     NOVOS TESTES DE SET + GET (sem monkeypatch / valores fixos)
# —————————————————————————————————————————————————————

def test_set_and_get_actuator_status_end_to_end():
    """
    Faz um SET real num actuator e, em seguida, um GET para verificar
    que o status mudou para o valor desejado.
    """
    a = Actuator(id="A1", type="motor", min_value=0, max_value=5)
    agent = Agent(host='localhost', port=0, sensors=None, actuators=[a])

    proto = Protocol()
    ts = generate_date_timestamp()

    # SET para 3
    raw_set = proto.encode_message(
        msg_type='S',
        timestamp=ts,
        message_id=MESSAGE_ID_STR,
        iid_list=[IID_ACT_STATUS],
        value_list=[('I',['3'])],
        error_list=[]
    )
    resp_set = agent.handle_request(raw_set)
    dec_set = proto.decode_message(resp_set)
    # SET sem erros
    assert dec_set['error_list'] == [0]
    # e internamente
    assert a.status == 3

    # GET logo a seguir
    raw_get = proto.encode_message(
        msg_type='G',
        timestamp=ts,
        message_id=MESSAGE_ID_STR,
        iid_list=[IID_ACT_STATUS],
        value_list=None,
        error_list=None
    )
    resp_get = agent.handle_request(raw_get)
    dec_get = proto.decode_message(resp_get)
    # devolve exatamente '3'
    val_type, parts = dec_get['value_list'][0]
    assert val_type == 'I'
    assert parts == ['3']


def test_set_and_get_device_beaconRate_end_to_end():
    """
    Faz um SET real ao campo beaconRate (Device) e,
    em seguida, um GET para verificar a alteração.
    """
    agent = Agent(host='localhost', port=0)
    proto = Protocol()
    ts = generate_date_timestamp()

    # SET beaconRate para 45
    raw_set = proto.encode_message(
        msg_type='S',
        timestamp=ts,
        message_id=MESSAGE_ID_STR,
        iid_list=[IID_DEV_BEACON],
        value_list=[('I',['45'])],
        error_list=[]
    )
    resp_set = agent.handle_request(raw_set)
    dec_set = proto.decode_message(resp_set)
    assert dec_set['error_list'] == [0]
    assert agent.mib.device_info["beaconRate"] == 45

    # GET logo a seguir
    raw_get = proto.encode_message(
        msg_type='G',
        timestamp=ts,
        message_id=MESSAGE_ID_STR,
        iid_list=[IID_DEV_BEACON],
        value_list=None,
        error_list=None
    )
    resp_get = agent.handle_request(raw_get)
    dec_get = proto.decode_message(resp_get)
    val_type, parts = dec_get['value_list'][0]
    assert val_type == 'I'
    assert parts == ['45']


def test_set_actuator_out_of_range_produces_error():
    """
    Tentativa de SET fora do intervalo do actuator → UnsupportedValueError.code
    """
    a = Actuator(id="A1", type="motor", min_value=0, max_value=2)
    agent = Agent(host='localhost', port=0, sensors=None, actuators=[a])

    proto = Protocol()
    ts = generate_date_timestamp()

    # SET inválido = 5
    raw = proto.encode_message(
        msg_type='S',
        timestamp=ts,
        message_id=MESSAGE_ID_STR,
        iid_list=[IID_ACT_STATUS],
        value_list=[('I',['5'])],
        error_list=[]
    )
    resp = agent.handle_request(raw)
    dec = proto.decode_message(resp)
    assert dec['error_list'] == [UnsupportedValueError.code]


def test_set_sensor_readonly_produces_error():
    """
    Sensors são read-only → SET em IID_SENSOR_VAL deve dar UnsupportedValueError.code
    """
    sensor = Sensor(id="S1", type="temp", min_value=0, max_value=10)
    agent = Agent(host='localhost', port=0, sensors=[sensor], actuators=[])

    proto = Protocol()
    ts = generate_date_timestamp()

    raw = proto.encode_message(
        msg_type='S',
        timestamp=ts,
        message_id=MESSAGE_ID_STR,
        iid_list=[IID_SENSOR_VAL],
        value_list=[('I',['5'])],
        error_list=[]
    )
    resp = agent.handle_request(raw)
    dec = proto.decode_message(resp)
    assert dec['error_list'] == [UnsupportedValueError.code]
