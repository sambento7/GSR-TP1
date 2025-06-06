import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from devices.actuator import Actuator

def test_configure_value_within_range():
    actuator = Actuator(id="act1", type="light", lower_value=0, max_value=100)
    assert actuator.configure_value(50) == True
    assert actuator.state == True

def test_conigure_value_below_range():
    actuator = Actuator(id="act2", type="thermostat", lower_value=10, max_value=30)
    assert actuator.configure_value(5) == False
    assert actuator.state == False

def test_get_state():
    actuator = Actuator(id="act3", type="fan", lower_value=0, max_value=5)
    actuator.configure_value(3)
    state = actuator.get_state()
    assert state["id"] == "act3"
    assert state["type"] == "fan"
    assert state["allowed value range"] == (0, 5)
    assert state["state"] == True
    assert "start_time" is not None

