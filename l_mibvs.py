import time
from devices.sensor import Sensor
from devices.actuator import Actuator

class MIB:
    """
    MIB (Management Information Base) class for L-SNMPvS.

    This class represents the local management database of the agent.
    It stores and manages virtual sensor and actuator devices.
    Devices can be registered, retrieved, and manipulated via this structure.

    Attributes:
        sensors (dict): Dictionary to hold sensor objects with their IDs as keys.
        actuators (dict): Dictionary to hold actuator objects with their IDs as keys.
        start_time (float): Timestamp when the MIB was initialized.
    """

    def __init__(self):
        self.sensors = {}
        self.actuators = {}
        self.start_time = time.time()

    def register_sensor(self, sensor: Sensor):
        """
        Registers a new sensor in the MIB.

        :param sensor: Sensor object to be registered.
        """
        if sensor.id not in self.sensors:
            self.sensors[sensor.id] = sensor
        else:
            raise ValueError(f"Sensor with ID {sensor.id} already exists.")
        
    def register_actuator(self, actuator: Actuator):
        """
        Registers a new actuator in the MIB.
        :param actuator: Actuator object to be registered.
        """
        if actuator.id not in self.actuators:
            self.actuators[actuator.id] = actuator
        else:
            raise ValueError(f"Actuator with ID {actuator.id} already exists.")
        
    def get_sensor(self, sensor_id: str) -> Sensor:
        """ 
        Retrieves a sensor by its ID.
        :param sensor_id: ID of the sensor to retrieve.
        :return: Sensor object if found, None otherwise.
        """
        return self.sensors[sensor_id] if sensor_id in self.sensors else None
    
    def get_actuator(self, actuator_id: str) -> Actuator:
        """
        Retrieves an actuator by its ID.
        :param actuator_id: ID of the actuator to retrieve.
        :return: Actuator object if found, None otherwise.
        """
        return self.actuators[actuator_id] if actuator_id in self.actuators else None

    def get_all_sensors(self) -> dict:
        """
        Returns all registered sensors.
        :return: Dictionary of all sensors with their IDs as keys.
        """
        return self.sensors
    
    def get_all_actuators(self) -> dict:    
        """
        Returns all registered actuators.
        :return: Dictionary of all actuators with their IDs as keys.
        """
        return self.actuators
    
    def get_mib_state(self) -> dict:
        """
        Returns the current state of the MIB.
        Includes all registered sensors and actuators, and the start time of the MIB.
        :return: Dictionary containing MIB state.
        """
        return {
            "sensors": {sensor_id: sensor.get_state() for sensor_id, sensor in self.sensors.items()},
            "actuators": {actuator_id: actuator.get_state() for actuator_id, actuator in self.actuators.items()},
            "start_time": self.start_time
        }
    
    def get_sensor_state(self, sensor_id: str) -> dict:
        """
        Returns the state of a specific sensor.
        :param sensor_id: ID of the sensor to retrieve the state for.
        :return: Dictionary containing the sensor's state.
        """
        sensor = self.get_sensor(sensor_id)
        return sensor.get_state() if sensor else None
    
    def get_actuator_state(self, actuator_id: str) -> dict:
        """
        Returns the state of a specific actuator.
        :param actuator_id: ID of the actuator to retrieve the state for.
        :return: Dictionary containing the actuator's state.
        """
        actuator = self.get_actuator(actuator_id)
        return actuator.get_state() if actuator else None
    
    def get_all_devices_states(self) -> dict:
        """
        Returns the states of all registered sensors and actuators.
        :return: Dictionary containing states of all sensors and actuators.
        """

        return {
            "sensors": {sensor_id : sensor_state for sensor_id, sensor_state in self.sensors.items()},
            "actuators": {actuator_id : actuator_state for actuator_id, actuator_state in self.actuators.items()}
        }
