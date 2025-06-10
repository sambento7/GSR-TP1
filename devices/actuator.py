from dataclasses import dataclass, field
import time
from utils.timestamp_utils import generate_date_timestamp

@dataclass
class Actuator:
    '''
    Class that simulates a virtual home automation actuator.
    Can be used to control devices with a defined range of values.
    '''
    id: str
    type: str
    min_value: int
    max_value: int
    status: int = field(default=0, init=False)
    last_control_time: str = field(default=None, init=False)
    start_time: float = field(default_factory=time.time, init=False)

    def configure_value(self, value: int) -> bool:
        '''
        Sets the actuator to a specific value within its range.
        Updates the state based on the value.
        '''
        if self.min_value <= value <= self.max_value:
            self.status = value
            self.last_control_time = generate_date_timestamp()
            return True
        return False

    def get_state(self) -> dict:
        '''
        Returns the current state of the actuator as a dictionary.
        '''
        return {
            "id": self.id,
            "type": self.type,
            "allowed value range": (self.min_value, self.max_value),
            "status": self.status,
            "last_control_time": self.last_control_time,
            "start_time": self.start_time
        }

