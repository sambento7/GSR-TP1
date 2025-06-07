import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from devices.sensor import Sensor

def test_read_value_within_range():
    sensor = Sensor("S1", "temperature", 10, 50)
    value = sensor.read_value()

    assert sensor.min_value <= value <= sensor.max_value
    assert value == sensor.current_value
    assert sensor.last_sampling_time is not None

    # Verificação do campo status (%)
    assert sensor.status is not None
    assert isinstance(sensor.status, float)
    assert 0.0 <= sensor.status <= 100.0

def test_get_state_format():
    sensor = Sensor("S2", "humidity", 20, 80)
    sensor.read_value()
    state = sensor.get_state()

    assert isinstance(state, dict)
    assert "id" in state
    assert "type" in state
    assert "allowed value range" in state
    assert "value" in state
    assert "status (%)" in state
    assert "last_sampling_time" in state
    assert isinstance(state["value"], int)
    assert isinstance(state["status (%)"], float)
    assert 0.0 <= state["status (%)"] <= 100.0
    assert isinstance(state["last_sampling_time"], str)
