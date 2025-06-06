import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import l_mibvs as MIB
from devices.actuator import Actuator
from devices.sensor import Sensor

def test():
    mib = MIB.MIB()
    mib.register_sensor(Sensor(id="sensor1", type="temperature", lower_value=0, max_value=50))
    mib.register_actuator(Actuator(id="act1", type="fan", lower_value=0, max_value=100))

    print("mib state" + str(mib.get_mib_state()))