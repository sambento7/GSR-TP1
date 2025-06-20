# agent.py

import socket
import uuid
from protocol import Protocol
from l_mibvs import MIB
from utils.timestamp_utils import generate_uptime_timestamp
from exceptions import LSNMPvSError
from utils.value_type_utils import get_value_type_from_iid

class Agent:
    """
    L-SNMPvS Agent that listens for GET and SET requests over UDP,
    interfaces with a local L-MIBvS, and replies with Response PDUs.
    Optionally can send Notification PDUs (traps) to a manager.
    """

    INVALID_MESSAGE_ID = 'invalid\0'

    def __init__(self, host='localhost', port=16100,
                 sensors=None, actuators=None,
                 manager_address=None):
        """
        :param host: UDP address to bind to
        :param port: UDP port to listen on
        :param sensors: list of Sensor instances to register
        :param actuators: list of Actuator instances to register
        :param manager_address: tuple (host, port) for sending notifications
        """
        self.host = host
        self.port = port
        self.mib = MIB()
        self.protocol = Protocol()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))

        # Address of the manager for notifications (optional)
        self.manager_address = manager_address

        # Register provided sensors and actuators in the MIB
        if sensors:
            for s in sensors:
                self.mib.register_sensor(s)
        if actuators:
            for a in actuators:
                self.mib.register_actuator(a)

    def _map_exception_to_code(self, exc: LSNMPvSError) -> int:
        """
        Maps an LSNMPvSError to its numeric code. Falls back to 1 (DecodingError).
        """
        return getattr(exc, 'code', 1)

    def listen(self):
        """
        Main loop: receive requests and send back responses.
        """
        while True:
            data, addr = self.sock.recvfrom(4096)
            reply = self.handle_request(data)
            if reply:
                self.sock.sendto(reply, addr)

    def handle_request(self, data: bytes) -> bytes:
        """
        Decode incoming PDU, perform GET or SET on the MIB, and return a Response PDU.
        """
        try:
            decoded = self.protocol.decode_message(data)
        except LSNMPvSError as e:
            # Malformed PDU: return a generic error response
            code = self._map_exception_to_code(e)
            return self.protocol.encode_message(
                msg_type='R',
                timestamp=generate_uptime_timestamp(self.mib.start_time),
                message_id=self.INVALID_MESSAGE_ID,
                iid_list=[],
                value_list=[],
                error_list=[code]
            )

        msg_type = decoded['type']
        message_id = decoded['message_id']
        iid_list   = decoded['iid_list']
        values     = []
        errors     = []

        # Handle GET requests
        if msg_type == 'G':
            print(f"Received GET request with message_id: {message_id}, iid_list: {iid_list}")
            for iid in iid_list:
                try:
                    print("MIB STATUS: ", self.mib.get_mib_state())
                    raw = self.mib.get_value_by_iid(iid)
                    print(f"RAW value for IID {iid}: {raw}")
                    expected = get_value_type_from_iid(iid)

                    # Empacota raw → (val_type, val_parts)
                    if expected is int:
                        val_type, val_parts = 'I', [str(raw)]
                    elif expected is str:
                        val_type, val_parts = 'S', [raw]
                    elif expected == "timestamp":
                        val_type, val_parts = 'T', raw.split(':')
                    elif expected == "list":
                        # intervalo/tabela → lista de escalares
                        first = raw[0]
                        val_type = 'I' if isinstance(first, int) else 'S'
                        val_parts = [str(x) for x in raw]
                    else:
                        raise LSNMPvSError(f"Tipo não suportado: {expected}")

                    values.append((val_type, val_parts))
                    errors.append(0)

                except LSNMPvSError as e:
                    # fallback: codifica um zero
                    values.append(('I', ['0']))
                    errors.append(self._map_exception_to_code(e))

            return self.protocol.encode_message(
                msg_type='R',
                timestamp=generate_uptime_timestamp(self.mib.start_time),
                message_id=message_id,
                iid_list=iid_list,
                value_list=values,
                error_list=errors
            )

        # Handle SET requests
        elif msg_type == 'S':
            new_values = decoded.get('value_list', [])
            for iid, (val_type, val_parts) in zip(iid_list, new_values):
                raw_value = val_parts[0] if val_parts else None
                print(f"raw_value for IID {iid}: {raw_value}")
                try:
                    self.mib.set_value_by_iid(iid, raw_value)
                    values.append((val_type, val_parts))
                    errors.append(0)
                except LSNMPvSError as e:
                    values.append((val_type, val_parts))
                    errors.append(self._map_exception_to_code(e))
            print(f"Received SET request with message_id: {message_id}, iid_list: {iid_list}, values: {values}")
            return self.protocol.encode_message(
                msg_type='R',
                timestamp=generate_uptime_timestamp(self.mib.start_time),
                message_id=message_id,
                iid_list=iid_list,
                value_list=values,
                error_list=errors
            )

        # Other message types are currently ignored
        return b''

    def send_notification(self, iid_list, value_list, error_list):
        """
        Optionally send a Notification (trap) PDU to the manager via broadcast/unicast.
        """
        if not self.manager_address:
            return
        # Generate a unique Message-Identifier for the notification
        notif_id = uuid.uuid4().hex[:15] + '\0'
        pdu = self.protocol.encode_message(
            msg_type='N',
            timestamp=generate_uptime_timestamp(self.mib.start_time),
            message_id=notif_id,
            iid_list=iid_list,
            value_list=value_list,
            error_list=error_list
        )
        self.sock.sendto(pdu, self.manager_address)
