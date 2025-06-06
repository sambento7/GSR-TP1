import time

class Actuator:
    '''
    Class that simulates a virtual home automation actuator.
    Can be used to control devices with a defined range of values.
    Attributes:
        id (str): Unique identifier for the actuator.
        type (str): Type of the actuator (e.g., light, thermostat).
        lower_value (int): Minimum value the actuator can set.
        max_value (int): Maximum value the actuator can set.
        state (bool): Current state of the actuator (on/off).
        start_time (float): Time when the actuator was initialized.
    '''
    def __init__(self, id:str, type: str, lower_value: int, max_value: int, state: bool = False):
        self.id = id
        self.type = type
        self.lower_value = lower_value
        self.max_value = max_value
        self.state = state
        self.start_time = time.time()

    def configure_value(self, value: int) -> bool:
        '''
        Sets the actuator to a specific value within its range.
        Updates the state based on the value.
        :param value: The value to set the actuator to.
        :return: True if the value is within range, False otherwise.
        '''
        if self.lower_value <= value <= self.max_value:
            self.state = True if value > 0 else False
            return True
        return False
    
    def get_state(self) -> dict:
        '''
        Returns the current state of the actuator as a dictionary.
        Includes id, type, range, current state, and start time.
        '''
        return {
            "id": self.id,
            "type": self.type,
            "allowed value range": (self.lower_value, self.max_value),
            "state": self.state,
            "start_time": self.start_time
        }