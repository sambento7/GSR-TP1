import time
from devices.sensor import Sensor
from devices.actuator import Actuator
from utils.timestamp_utils import generate_date_timestamp, generate_uptime_timestamp
from utils.enums import OperationalResult
from utils.format_utils import validate_date_format, is_valid_int
from utils.iid_utils import parse_iid

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

        match field_id:
            case 1:  return self.device_info["id"]
            case 2:  return self.device_info["type"]
            case 3:  return self.device_info["beaconRate"]
            case 4:  return len(self.sensors)
            case 5:  return len(self.actuators)
            case 6:  return self.device_info["dateAndTime"]
            case 7:  return generate_uptime_timestamp(self.start_time)
            case 8:  return self.last_update_time
            case 9:  return self.operational_status
            case 10: return self.device_info["reset"]
            case _:  return None

    def set_device_value(self, field_id: int, value) -> OperationalResult:
        match field_id:
            case 3:  # beaconRate
                if not is_valid_int(value):
                    return OperationalResult.INVALID

                value_int = int(value)
                if value_int < 0:
                    return OperationalResult.INVALID
                elif value_int == self.device_info["beaconRate"]:
                    return OperationalResult.NO_CHANGE
                else:
                    self.device_info["beaconRate"] = value_int
                    self.last_update_time = generate_date_timestamp()
                    return OperationalResult.UPDATED

            case 6:  # dateAndTime
                if not validate_date_format(value):
                    return OperationalResult.INVALID
                elif value == self.device_info["dateAndTime"]:
                    return OperationalResult.NO_CHANGE
                else:
                    self.device_info["dateAndTime"] = value
                    self.last_update_time = generate_date_timestamp()
                    return OperationalResult.UPDATED  

            case 10:  # reset
                if not is_valid_int(value):
                    return OperationalResult.INVALID

                value_int = int(value)
                if value_int == 1:
                    current_timestamp = time.time()
                    current_date = generate_date_timestamp(current_timestamp)

                    self.device_info["reset"] = 1
                    self.start_time = current_timestamp
                    self.device_info["dateAndTime"] = current_date
                    self.last_update_time = current_date
                    self.device_info["reset"] = 0
                    return OperationalResult.UPDATED

                elif value_int == 0:
                    if self.device_info["reset"] != 0:
                        self.device_info["reset"] = 0
                        self.last_update_time = generate_date_timestamp()
                        return OperationalResult.UPDATED
                    else:
                        return OperationalResult.NO_CHANGE

                else:
                    return OperationalResult.INVALID

            case _:
                return OperationalResult.INVALID
            
    def get_value_by_iid(self, iid: str):

        try:
            parsed_iid = parse_iid(iid)
        except ValueError as e:
            raise ValueError(f"Invalid IID format: {e}")
        structure = parsed_iid["structure"]
        object_id = parsed_iid["object"]
        indexes = parsed_iid["indexes"]
        #Device group
        if structure == 1:
            if len(indexes) > 0:
                raise ValueError("Indexes are not allowed for Device group.")
            elif object_id < 1 or object_id > 10:
                raise ValueError(f"Invalid object ID {object_id} for Device group. Expected 1–10.")
            else:
                return self.get_device_value(object_id)
        # Sensors group
        elif structure == 2:
            if not(0 <= object_id <= 6):
                raise ValueError(f"Invalid object ID {object_id} for Sensors group. Expected 1–6.")
            # If object_id is 0, return the count of all sensors
            elif object_id == 0:
                return len(self.get_all_sensors())
            else:
                
            


            


            

