import socket
from protocol import Protocol
from l_mibvs import MIB
from utils.timestamp_utils import generate_uptime_timestamp
from exceptions import LSNMPvSError
class Agent:
    def __init__(self, host='localhost', port=16100):
        self.host = host
        self.port = port
        self.mib = MIB()
        self.protocol = Protocol()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))

    def listen(self):
        """
        Start listening for incoming messages on the specified host and port.
        This method will block and wait for messages, processing them as they arrive.
        Attributes:
        - host: The host address to bind the socket to.
        - port: The port number to bind the socket to.
        """
        print(f"Agent listening at {self.host}:{self.port}")
        while True:
            data, addr = self.sock.recvfrom(4096)
            print(f"Received from {addr}: {data}")
            response = self.handle_request(data)
            self.sock.sendto(response, addr)

    def handle_request(self, raw_message: bytes) -> bytes:
        """
        Processa uma mensagem G (get-request) ou S (set-request) e responde com R (response).
        """
        try:
            decoded = self.protocol.decode_message(raw_message)
        except LSNMPvSError as e:
            return self.protocol.encode_message(
                msg_type='R',
                timestamp=generate_uptime_timestamp(self.mib.start_time),
                message_id='invalid\0',
                iid_list=[],
                value_list=[],
                error_list=[e.code]
            )

        msg_type = decoded["msg_type"]
        message_id = decoded["message_id"]
        iid_list = decoded["iid_list"]

        if msg_type == "G":
            values = []
            errors = []

            for iid in iid_list:
                try:
                    iid_str = ".".join(map(str, iid))
                    value = self.mib.get_value_by_iid(iid_str)
                    values.append(value)
                    errors.append(0)
                except LSNMPvSError as e:
                    values.append(None)
                    errors.append(e.code)
                except Exception:
                    values.append(None)
                    errors.append(1)  # erro genérico

            return self.protocol.encode_message(
                msg_type='R',
                timestamp=generate_uptime_timestamp(self.mib.start_time),
                message_id=message_id,
                iid_list=iid_list,
                value_list=values,
                error_list=errors
            )

        # Futuramente tratar mensagens "S" (set-request)
        return b''  # Por agora ignora outros tipos

