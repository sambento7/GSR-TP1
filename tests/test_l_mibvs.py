import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from devices.actuator import Actuator
from devices.sensor import Sensor
from l_mibvs import MIB

def test_register_sensor():
    mib = MIB()
    sensor = Sensor(id="sensor1", type="temperature", min_value=0, max_value=50)
    mib.register_sensor(sensor)
    assert mib.get_sensor("sensor1") == sensor
    try:
        mib.register_sensor(sensor)
    except ValueError as e:
        assert str(e) == "Sensor with ID sensor1 already exists."

def test_register_actuator():
    mib = MIB()
    actuator = Actuator(id="act1", type="fan", min_value=0, max_value=100)
    mib.register_actuator(actuator)
    assert mib.get_actuator("act1") == actuator
    try:
        mib.register_actuator(actuator)
    except ValueError as e:
        assert str(e) == "Actuator with ID act1 already exists."

def test_get_sensor():
    mib = MIB()
    sensor = Sensor(id="sensor1", type="temperature", min_value=0, max_value=50)
    mib.register_sensor(sensor)
    assert mib.get_sensor("sensor1") == sensor
    assert mib.get_sensor("nonexistent") is None

def test_get_actuator():
    mib = MIB()
    actuator = Actuator(id="act1", type="fan", min_value=0, max_value=100)
    mib.register_actuator(actuator)
    assert mib.get_actuator("act1") == actuator
    assert mib.get_actuator("nonexistent") is None

def test_get_all_sensors():
    mib = MIB()
    sensor1 = Sensor(id="sensor1", type="temperature", min_value=0, max_value=50)
    sensor2 = Sensor(id="sensor2", type="humidity", min_value=0, max_value=100)
    mib.register_sensor(sensor1)
    mib.register_sensor(sensor2)
    all_sensors = mib.get_all_sensors()
    assert len(all_sensors) == 2
    assert all_sensors["sensor1"] == sensor1.get_state()
    assert all_sensors["sensor2"] == sensor2.get_state()

def test_get_all_actuators():
    mib = MIB()
    actuator1 = Actuator(id="act1", type="fan", min_value=0, max_value=100)
    actuator2 = Actuator(id="act2", type="light", min_value=0, max_value=200)
    mib.register_actuator(actuator1)
    mib.register_actuator(actuator2)
    all_actuators = mib.get_all_actuators()
    assert len(all_actuators) == 2
    assert all_actuators["act1"] == actuator1.get_state()
    assert all_actuators["act2"] == actuator2.get_state()

def test_get_mib_state():
    mib = MIB()
    sensor = Sensor(id="sensor1", type="temperature", min_value=0, max_value=50)
    actuator = Actuator(id="act1", type="fan", min_value=0, max_value=100)
    mib.register_sensor(sensor)
    mib.register_actuator(actuator)

    expected_state = {
        "sensors": {"sensor1": sensor.get_state()},
        "actuators": {"act1": actuator.get_state()},
        "start_time": mib.start_time
    }

    assert mib.get_mib_state() == expected_state

def test_get_sensor_state():
    mib = MIB()
    sensor = Sensor(id="sensor1", type="temperature", min_value=0, max_value=50)
    mib.register_sensor(sensor)
    sensor.read_value()
    assert mib.get_sensor_state("sensor1") == sensor.get_state()
    assert mib.get_sensor_state("nonexistent") is None

def test_get_actuator_state():
    mib = MIB()
    actuator = Actuator(id="act1", type="fan", min_value=0, max_value=100)
    mib.register_actuator(actuator)
    actuator.configure_value(50)
    assert mib.get_actuator_state("act1") == actuator.get_state()
    assert mib.get_actuator_state("nonexistent") is None

def test_start_time_is_float():
    mib = MIB()
    assert isinstance(mib.start_time, float)
    assert mib.start_time > 0

def test_sensors_and_actuators_are_separate():
    mib = MIB()
    sensor = Sensor("sensor1", "temperature", 0, 50)
    actuator = Actuator("sensor1", "fan", 0, 1)
    mib.register_sensor(sensor)
    mib.register_actuator(actuator)
    assert mib.get_sensor("sensor1") == sensor
    assert mib.get_actuator("sensor1") == actuator

def test_actuator_state_change_reflected_in_mib():
    mib = MIB()
    a = Actuator("a1", "fan", 0, 1)
    mib.register_actuator(a)

    assert mib.get_actuator_state("a1")["status"] == 0  # estado inicial

    a.configure_value(1)

    assert mib.get_actuator_state("a1")["status"] == 1  # valor alterado
