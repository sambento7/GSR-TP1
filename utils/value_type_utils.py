from typing import Union
from devices.sensor import Sensor
from devices.actuator import Actuator
from dataclasses import fields

def get_value_type_from_iid(iid: list[int]) -> type:
    """
    Determina o tipo de valor esperado para um dado IID com base na estrutura L-SNMPvS.

    :param iid: Lista com o IID (ex: [1, 3] ou [2, 3, 1])
    :return: Tipo Python esperado (int, str, list, etc.)
    """
    structure = iid[0]
    object_id = iid[1]
    indexes = iid[2:]

    if structure == 1:  # Device Info
        device_field_map = {
            0: int,  # número de campos
            1: str,   # id
            2: str,   # type
            3: int,   # beaconRate
            4: int,   # nSensors
            5: int,   # nActuators
            6: "timestamp",   # dateAndTime
            7: "timestamp",   # upTime
            8: "timestamp",   # lastTimeUpdated
            9: int,   # operationalStatus
            10: int   # reset
        }
        return device_field_map.get(object_id, None)

    elif structure == 2:  # Sensor
        if object_id == 0:
            return int
        sensor_fields = fields(Sensor)
        try:
            field = sensor_fields[object_id - 1]
            if field.name == "last_sampling_time":
                return "timestamp"
            return field.type
        except IndexError:
            return None

    elif structure == 3:  # Actuator
        if object_id == 0:
            return int
        actuator_fields = fields(Actuator)
        try:
            field = actuator_fields[object_id - 1]
            if field.name == "last_control_time":
                return "timestamp"
            return field.type
        except IndexError:
            return None


    return None
