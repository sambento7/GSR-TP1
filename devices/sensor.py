import random
import time
from utils.timestamp_utils import gerar_timestamp_uptime

class Sensor:
    """
    Classe que simula um sensor domótico virtual.
    Pode gerar valores aleatórios dentro de um intervalo definido.
    """

    def __init__(self, id: str, tipo: str, min_valor: int, max_valor: int):
        self.id = id
        self.tipo = tipo
        self.min_valor = min_valor
        self.max_valor = max_valor
        self.valor_atual = None
        self.last_sampling_time = None
        self.start_time = time.time()

    def ler_valor(self) -> int:
        """
        Gera um valor aleatório dentro do intervalo do sensor.
        Atualiza o valor atual e o timestamp da leitura.
        """
        self.valor_atual = random.randint(self.min_valor, self.max_valor)
        self.last_sampling_time = gerar_timestamp_uptime(self.start_time)
        return self.valor_atual

    def obter_estado(self) -> dict:
        """
        Devolve o estado atual do sensor como dicionário.
        Inclui id, tipo, intervalo, valor lido e tempo da última amostragem.
        """
        return {
            "id": self.id,
            "tipo": self.tipo,
            "intervalo": (self.min_valor, self.max_valor),
            "valor": self.valor_atual,
            "last_sampling_time": self.last_sampling_time
        }
