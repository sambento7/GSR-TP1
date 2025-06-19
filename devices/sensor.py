from dataclasses import dataclass, field
import random
import time
from utils.timestamp_utils import generate_date_timestamp

@dataclass
class Sensor:
    '''
    Class that simulates a virtual home automation sensor.
    Can generate random values within a defined range.
    Attributes:
        id (str): Unique identifier for the sensor.
        type (str): Type of the sensor (e.g., temperature, humidity).
        min_value (int): Minimum value the sensor can read.
        max_value (int): Maximum value the sensor can read.
        current_value (int): The last value read by the sensor.
        last_sampling_time (str): Timestamp of the last reading.
        start_time (float): Time when the sensor was initialized.
    '''

    id: str
    type: str
    min_value: int
    max_value: int
    current_value: int = field(default=None, init=False)
    status: float = field(default=None, init=False)
    last_sampling_time: str = field(default=None, init=False)
    start_time: float = field(default_factory=time.time, init=False)

    def read_value(self) -> int:
        ''' 
        Simulates reading a value from the sensor.
        Generates a random value within the defined range and updates the last sampling time.
        :return: The current value read by the sensor.
        '''
        self.current_value = random.randint(self.min_value, self.max_value)
        intervalo = self.max_value - self.min_value
        self.status = int(((self.current_value - self.min_value) / intervalo) * 100) if intervalo > 0 else 0
        self.last_sampling_time = generate_date_timestamp()
        return self.current_value

    def get_state(self) -> dict:
        '''
        Returns the current state of the sensor as a dictionary.
        Includes id, type, range, read value, and last sampling time.
        '''
        return {
            "id": self.id,
            "type": self.type,
            "allowed value range": (self.min_value, self.max_value),
            "value": self.current_value,
            "status (%)": self.status,
            "last_sampling_time": self.last_sampling_time
        }
