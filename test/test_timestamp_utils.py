import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.timestamp_utils import gerar_timestamp_data
import time


def test_gerar_timestamp_data():
    data = gerar_timestamp_data()
    assert isinstance(data, str)
    assert len(data.split(":")) == 7  # Deve ter 7 campos