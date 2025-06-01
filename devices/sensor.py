import random
import time
from utils.timestamp_utils import generate_date_timestamp

class Sensor:
    '''
    Class that simulates a virtual home automation sensor.
    Can generate random values within a defined range.
    Attributes:
        id (str): Unique identifier for the sensor.
        type (str): Type of the sensor (e.g., temperature, humidity).
        lower_value (int): Minimum value the sensor can read.
        max_value (int): Maximum value the sensor can read.
        current_value (int): The last value read by the sensor.
        last_sampling_time (str): Timestamp of the last reading.
        start_time (float): Time when the sensor was initialized.
    '''
    def __init__(self, id: str, type: str, lower_value: int, max_value: int):
        self.id = id
        self.type = type
        self.lower_value = lower_value
        self.max_value = max_value
        self.current_value = None
        self.last_sampling_time = None
        self.start_time = time.time()

    def read_value(self) -> int:
        ''' 
        Generates a random value within the sensor's range.
        Updates the current value and the timestamp of the reading.
        :return: The generated random value.
        '''
        self.current_value = random.randint(self.lower_value, self.max_value)
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
            "allowed value range": (self.lower_value, self.max_value),
            "value": self.current_value,
            "last_sampling_time": self.last_sampling_time
        }
