import time
from utils.timestamp_utils import generate_date_timestamp

class Actuator:
    '''
    Class that simulates a virtual home automation actuator.
    Can be used to control devices with a defined range of values.
    Attributes:
        id (str): Unique identifier for the actuator.
        type (str): Type of the actuator (e.g., light, thermostat).
        min_value (int): Minimum value the actuator can set.
        max_value (int): Maximum value the actuator can set.
        state (bool): Current state of the actuator (on/off).
        start_time (float): Time when the actuator was initialized.
    '''

    def __init__(self, id: str, type: str, min_value: int, max_value: int):
        self.id = id
        self.type = type
        self.min_value = min_value
        self.max_value = max_value
        self.status = 0  # Valor atual do atuador (padrão: desligado)
        self.last_control_time = None
        self.start_time = time.time()

    def configure_value(self, value: int) -> bool:
        '''
        Sets the actuator to a specific value within its range.
        Updates the state based on the value.
        :param value: The value to set the actuator to.
        :return: True if the value is within range, False otherwise.
        '''
        if self.min_value <= value <= self.max_value:
            self.status = value
            self.last_control_time = generate_date_timestamp()
            return True
        return False

    def get_state(self) -> dict:
        '''
        Returns the current state of the actuator as a dictionary.
        Includes id, type, range, current staus, last control time and start time.
        '''
        return {
            "id": self.id,
            "type": self.type,
            "allowed value range": (self.min_value, self.max_value),
            "status": self.status,
            "last_control_time": self.last_control_time,
            "start_time": self.start_time
        }
