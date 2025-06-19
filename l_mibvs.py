import time
from devices.sensor import Sensor
from devices.actuator import Actuator
from utils.timestamp_utils import generate_date_timestamp, generate_uptime_timestamp
from utils.format_utils import validate_date_format, is_valid_int
from utils.iid_utils import parse_iid
from dataclasses import fields
from exceptions import DecodingError, InvalidTagError, UnknownMessageTypeError, DuplicateMessageError, InvalidIIDError, InvalidValueTypeError, UnsupportedValueError, IIDValueMismatchError, NoDevicesRegisteredError

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
        self.start_time = time.time()  # usado internamente para uptime

        self.device_info = {
            "id": "agent1",  # 1.1
            "type": "Lights & A/C Conditioning",  # 1.2
            "beaconRate": 60,  # 1.3
            "nSensors": 0,  # 1.4 (será atualizado com len(self.sensors))
            "nActuators": 0,  # 1.5 (idem)
            "dateAndTime": generate_date_timestamp(),  # 1.6
            "upTime": generate_uptime_timestamp(self.start_time),  # 1.7 (atualizado dinamicamente)
            "lastTimeUpdated": generate_date_timestamp(),  # 1.8
            "operationalStatus": 1,  # 1.9 (0 = standby, 1 = normal, 2+ = erro)
            "reset": 0  # 1.10
        }

        # tabelas de sensores e atuadores (estruturas 2 e 3)
        self.sensors = {}    # sensor_id: Sensor
        self.actuators = {}  # actuator_id: Actuator

    def register_sensor(self, sensor: Sensor):
        """
        Registers a new sensor in the MIB.

        :param sensor: Sensor object to be registered.
        """
        if sensor.id not in self.sensors:
            self.sensors[sensor.id] = sensor
            self.device_info["nSensors"] = len(self.sensors)
        else:
            raise ValueError(f"Sensor with ID {sensor.id} already exists.")
        
    def register_actuator(self, actuator: Actuator):
        """
        Registers a new actuator in the MIB.
        :param actuator: Actuator object to be registered.
        """
        if actuator.id not in self.actuators:
            self.actuators[actuator.id] = actuator
            self.device_info["nActuators"] = len(self.actuators)
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
            case 0:  return len(self.device_info)
            case 1:  return self.device_info["id"]
            case 2:  return self.device_info["type"]
            case 3:  return self.device_info["beaconRate"]
            case 4:  return self.device_info["nSensors"]
            case 5:  return self.device_info["nActuators"]
            case 6:  return self.device_info["dateAndTime"]
            case 7:
                up_time = generate_uptime_timestamp(self.start_time)
                self.device_info["upTime"] = up_time  
                return up_time
            case 8:  return self.device_info["lastTimeUpdated"]
            case 9:  return self.device_info["operationalStatus"]
            case 10: return self.device_info["reset"]
            case _:  raise InvalidIIDError(f"Unknown Device field ID: {field_id}.")

    def set_device_value(self, field_id: int, value):
        match field_id:
            case 3:  # beaconRate
                if not is_valid_int(value):
                    raise InvalidValueTypeError("Invalid type for beaconRate.")
                value_int = int(value)

                if value_int < 0:
                    raise UnsupportedValueError("Invalid value for beaconRate.")

                if value_int == self.device_info["beaconRate"]:
                    return None # Sem alteração o que fazer aqui??? #TODO: pensar em algo melhor
                else:
                    self.device_info["beaconRate"] = value_int
                    self.device_info["lastTimeUpdated"] = generate_date_timestamp()
                    return None

            case 6:  # dateAndTime
                if not validate_date_format(value):
                    raise InvalidValueTypeError("Invalid date format.")

                if value == self.device_info["dateAndTime"]:
                    return None # Sem alteração
                else:
                    self.device_info["dateAndTime"] = value
                    self.device_info["lastTimeUpdated"] = generate_date_timestamp()
                    return None

            case 10:  # reset
                if not is_valid_int(value):
                    raise InvalidValueTypeError("Invalid type for reset.")

                value_int = int(value)

                if value_int == 1:
                    current_timestamp = time.time()
                    current_date = generate_date_timestamp(current_timestamp)

                    self.device_info["reset"] = 1
                    # Resetting the MIB
                    self.start_time = current_timestamp
                    self.device_info["dateAndTime"] = current_date
                    self.device_info["lastTimeUpdated"] = current_date
                    # after reset is done we put the reset value back to 0
                    self.device_info["reset"] = 0
                    return None

                elif value_int == 0:
                    if self.device_info["reset"] != 0:
                        self.device_info["reset"] = 0
                        self.device_info["lastTimeUpdated"] = generate_date_timestamp()
                        return None
                    else:
                        return None # Sem alteração
                else:
                    raise UnsupportedValueError("Invalid value for reset.")

            case _:
                raise InvalidIIDError(f"Field ID {field_id} is not writable or does not exist in the device information.")

    def get_sensor_field(self, object_id: int, index: int):
        sensors_list = list(self.sensors.values())
        print(f"get_sensor_field: object_id={object_id}, index={index}, sensors_list={sensors_list}")
        if len(sensors_list) == 0:
            raise NoDevicesRegisteredError("No sensors registered in the MIB.")
        match object_id:
            case 1: return sensors_list[index].id
            case 2: return sensors_list[index].type
            case 3:
                sensors_list[index].read_value() 
                return sensors_list[index].status
            case 4: return sensors_list[index].min_value
            case 5: return sensors_list[index].max_value
            case 6: return sensors_list[index].last_sampling_time
            case _: raise InvalidIIDError(f"Unknown sensor object ID: {object_id}.")

    def get_actuator_field(self, object_id: int, index: int):
        actuators_list = list(self.actuators.values())
        if len(actuators_list) == 0:
            raise NoDevicesRegisteredError("No actuators registered in the MIB.")
        match object_id:
            case 1: return actuators_list[index].id
            case 2: return actuators_list[index].type
            case 3: return actuators_list[index].status
            case 4: return actuators_list[index].min_value
            case 5: return actuators_list[index].max_value
            case 6: return actuators_list[index].last_control_time
            case _: raise InvalidIIDError(f"Unknown actuator object ID: {object_id}.")

    def get_value_by_iid(self, iid: list[int]):

        parsed_iid = parse_iid(iid)

        structure = parsed_iid["structure"]
        object_id = parsed_iid["object"]
        indexes = parsed_iid["indexes"]
        #Device group
        if structure == 1:
            if len(indexes) > 0:
                raise InvalidIIDError("Indexes are not allowed for Device group.")
            elif object_id < 0 or object_id > len(self.device_info):
                raise InvalidIIDError(f"Invalid object ID {object_id} for Device group. Expected 1–{len(self.device_info)}.")
            else:
                return self.get_device_value(object_id)
        # Sensors group
        elif structure == 2:
            if not(0 <= object_id <= len(fields(Sensor))):
                raise InvalidIIDError(f"Invalid object ID {object_id} for Sensors group. Expected 1–{len(fields(Sensor))}.")
            elif object_id == 0:
                return len(fields(Sensor))  # Number of fields in Sensor class
            else:
                if len(indexes) == 0:
                    return self.get_sensor_field(object_id, 0)
                elif len(indexes) == 1:
                    index = indexes[0]
                    if index == 0:
                        return len(self.sensors)
                    elif 1 <= index <= len(self.sensors):
                        return self.get_sensor_field(object_id, index - 1)
                    else:
                        raise InvalidIIDError(f"Invalid sensor index {index}. Expected 1–{len(self.sensors)}.")
                elif len(indexes) == 2:
                    i1, i2 = indexes
                    if i1 == 0 and i2 == 0:
                        # return all sensors values for the given object_id
                        return [self.get_sensor_field(object_id, i) for i in range(len(self.sensors))]
                    elif i1 > 0 and i2 >= i1 and i2 <= len(self.sensors):
                        return [self.get_sensor_field(object_id, i) for i in range(i1 - 1, i2)]
                    else:
                        raise InvalidIIDError(f"Invalid range for sensor indexes.")
                else:
                    raise InvalidIIDError("Invalid number of indexes for Sensors group. Expected 0, 1, or 2 indexes.")
        elif structure == 3:
            if not(0 <= object_id <= len(fields(Actuator))):
                raise InvalidIIDError(f"Invalid object ID {object_id} for Actuators group. Expected 1–{len(fields(Actuator))}.")
            elif object_id == 0:
                return len(fields(Actuator))
            else:
                if len(indexes) == 0:
                    return self.get_actuator_field(object_id, 0)
                elif len(indexes) == 1:
                    index = indexes[0]
                    if index == 0:
                        return len(self.actuators)
                    elif 1 <= index <= len(self.actuators):
                        return self.get_actuator_field(object_id, index - 1)
                    else:
                        raise InvalidIIDError(f"Invalid actuator index {index}. Expected 1–{len(self.actuators)}.")
                elif len(indexes) == 2:
                    i1, i2 = indexes
                    if i1 == 0 and i2 == 0:
                        # return all actuators values for the given object_id
                        return [self.get_actuator_field(object_id, i) for i in range(len(self.actuators))]
                    elif i1 > 0 and i2 >= i1 and i2 <= len(self.actuators):
                        return [self.get_actuator_field(object_id, i) for i in range(i1 - 1, i2)]
                    else:
                        raise InvalidIIDError(f"Invalid range for actuator indexes.")
                else:
                    raise InvalidIIDError("Invalid number of indexes for Actuators group. Expected 0, 1, or 2 indexes.")

    def set_value_by_iid(self, iid: list[int], value):
        
        parsed_iid = parse_iid(iid)
 
        structure = parsed_iid["structure"]
        object_id = parsed_iid["object"]
        indexes = parsed_iid["indexes"]

        # Device group
        if structure == 1:
            if len(indexes) > 0:
                raise InvalidIIDError("Indexes are not allowed for Device group.")
            elif object_id < 0 or object_id > len(self.device_info):
                raise InvalidIIDError(f"Invalid object ID {object_id} for Device group. Expected 1–{len(self.device_info)}.")
            else:
                self.set_device_value(object_id, value)
                return None

        # Sensors group
        elif structure == 2:
            raise UnsupportedValueError("Sensors group is read-only. Cannot set values directly.")

        # Actuators group
        elif structure == 3:
            if not(0 <= object_id <= len(fields(Actuator))):
                raise InvalidIIDError(f"Invalid object ID {object_id} for Actuators group. Expected 1–{len(fields(Actuator))}.")
            
            if object_id != 3:  # only object_id 3 (status) is writable
                raise UnsupportedValueError(f"Object ID {object_id} in Actuators group is not writable.")
            
            if len(indexes) != 1:
                raise InvalidIIDError("Invalid number of indexes for Actuators group. Expected 1 index for setting status.")
            
            index = indexes[0]
            index_int = int(index)

            if not is_valid_int(value):
                raise InvalidValueTypeError("Invalid type for actuator status value.")
            value_int = int(value)

            if 1 <= index_int <= len(self.actuators):
                print(f"Setting actuator status for index {index_int} with value {value_int}.")
                actuator = self.get_actuator(list(self.actuators.keys())[index_int - 1])
                updated = actuator.configure_value(value_int)
                print(f"Updated actuator status: {updated}")
                if not updated:
                    raise UnsupportedValueError("Invalid value for actuator status.")
                self.device_info["lastTimeUpdated"] = generate_date_timestamp()
                return None
            else:
                raise InvalidIIDError(f"Invalid actuator index {index_int}. Expected 1–{len(self.actuators)}.")
                
