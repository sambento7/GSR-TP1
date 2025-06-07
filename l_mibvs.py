import time
from devices.sensor import Sensor
from devices.actuator import Actuator
from utils.timestamp_utils import generate_date_timestamp, generate_uptime_timestamp

class MIB:
    """
    MIB (Management Information Base) class for L-SNMPvS.

    This class represents the local management database of the agent.
    It stores and manages virtual sensor and actuator devices.
    Devices can be registered, retrieved, and manipulated via this structure.

    Attributes:
        sensors (dict): Dictionary of registered sensors, keyed by their IDs.
        actuators (dict): Dictionary of registered actuators, keyed by their IDs.
        start_time (float): Time when the MIB was initialized.
        device_info (dict): Information about the device, including ID, type, beacon rate, date and time, and reset status.
        last_update_time (str): Last update timestamp of the device information.
        operational_status (int): Operational status of the MIB (0 = standby, 1 = normal, 2+ = error).
    """

    def __init__(self):
        self.start_time = time.time()
        self.device_info = {
            "id": "agent1",  #Tag identifying the device (the MacAddress, for example) -> 1.1
            "type": "Lights & A/C Conditioning", #"Text description for the type of device -> 1.2
            "beaconRate": 60,  # "Frequency rate in seconds for issuing a notification message with information from this group that acts as a beacon broadcasting message to all the managers in the LAN. 
                               # If value is set to zero the notifications for this group are halted. -> 1.3
            "dateAndTime": generate_date_timestamp(), #System date and time setup in the device. -> 1.6
            "reset": 0 #Value 0 means no reset and value 1 means a reset procedure must be done. -> 1.10
        }
        self.sensors = {} # Dictionary to hold registered sensors, keyed by their IDs -> 1.4
        self.actuators = {} # Dictionary to hold registered actuators, keyed by their IDs -> 1.5
        self.last_update_time = generate_date_timestamp() #"Date and time of the last update of any object in the device L-MIBvS. -> 1.8
        self.operational_status = 1  # 0 = standby, 1 = normal, 2+ = erro -> 1.9

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

    #ver se n é melhor retornar valores dos sensores e não os objetos
    def get_all_sensors(self) -> dict:
        """
        Returns all registered sensors.
        :return: Dictionary of all sensors with their IDs as keys.
        """
        return {
            sensor_id: sensor.get_state() for sensor_id, sensor in self.sensors.items()
        }
    
    def get_all_actuators(self) -> dict:    
        """
        Returns all registered actuators.
        :return: Dictionary of all actuators with their IDs as keys.
        """
        return {
            actuator_id: actuator.get_state() for actuator_id, actuator in self.actuators.items()
        }
    
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
    
    def get_device_value(self, field_id: int):
        """        
            Retrieves a specific value from the device information based on the field ID.
            :param field_id: ID of the field to retrieve.
            :return: Value corresponding to the field ID, or None if the field ID is invalid.
        """

        if field_id == 1:
            return self.device_info["id"]
        elif field_id == 2:
            return self.device_info["type"]
        elif field_id == 3:
            return self.device_info["beaconRate"]
        elif field_id == 4:
            return len(self.sensors)
        elif field_id == 5:
            return len(self.actuators)
        elif field_id == 6:
            return self.device_info["dateAndTime"]
        elif field_id == 7:
            return generate_uptime_timestamp(self.start_time)
        elif field_id == 8:
            return self.last_update_time
        elif field_id == 9:
            return self.operational_status
        elif field_id == 10:
            return self.device_info["reset"]
        else:
            return None

    def set_device_value(self, field_id: int, value) -> bool:

        updated = False

        if field_id == 3:  # beaconRate
            try:
                self.device_info["beaconRate"] = int(value)
                updated = True
            except ValueError:
                return False

        #fazer verificação do tipo (se é data válida)
        #TODO
        elif field_id == 6:  # dateAndTime
            self.device_info["dateAndTime"] = value
            updated = True

        elif field_id == 10:  # reset
            if int(value) == 1:
                self.device_info["reset"] = 1
                self.start_time = time.time()
                self.device_info["dateAndTime"] = generate_date_timestamp()
                self.last_update_time = generate_date_timestamp()
                
                # Após executar reset, limpar sinalizador
                self.device_info["reset"] = 0
                return True
            elif int(value) == 0:
                # Só altera se o valor anterior era 1
                if self.device_info["reset"] != 0:
                    self.device_info["reset"] = 0
                    self.last_update_time = generate_date_timestamp()
                    return True
                else:
                    return False  

        if updated:
            self.last_update_time = generate_date_timestamp()

        return updated

