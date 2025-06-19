# utils/value_type_utils.py

from typing import Type, Union, Literal
from devices.sensor import Sensor
from devices.actuator import Actuator
from dataclasses import fields

def get_value_type_from_iid(iid: list[int]) -> Union[Type[int], Type[str], Literal["timestamp"], Literal["list"]]:
    """
    Determina o tipo de valor esperado para um dado IID, usando a L-MIBvS:
      - int
      - str         (IDs, tipos, ON/OFF…)
      - "timestamp" (campos de data/hora ou uptime)
      - "list"      (quando a MIB devolve várias instâncias, ex.: range em tabelas)
    """
    structure, object_id, *indexes = iid

    # DEVICE (1.x)
    if structure == 1:
        device_map = {
            0: int, 1: str, 2: str, 3: int, 4: int,
            5: int, 6: "timestamp", 7: "timestamp",
            8: "timestamp", 9: int, 10: int
        }
        return device_map.get(object_id)

    # SENSORS (2.x)
    if structure == 2:
        if object_id == 0:
            return int
        sensor_fields = fields(Sensor)
        # tabelas / ranges devolvem listas
        if len(indexes) == 2:
            return "list"
        field = sensor_fields[object_id - 1]
        if field.name == "last_sampling_time":
            return "timestamp"
        return field.type

    # ACTUATORS (3.x)
    if structure == 3:
        if object_id == 0:
            return int
        actuator_fields = fields(Actuator)
        if len(indexes) == 2:
            return "list"
        field = actuator_fields[object_id - 1]
        if field.name == "last_control_time":
            return "timestamp"
        return field.type

    return None
