from exceptions import LSNMPvSError, DecodingError, InvalidTagError, UnknownMessageTypeError
from utils.format_utils import is_valid_int

class Protocol:
    TAG = b'kdk847ufh84jg87g\0'

    def _next_str(self, cursor: int, raw_message: bytes) -> tuple[int, bytes]:
        """
        Helper function to find the next null-terminated string in the raw message.
        :param cursor: Current position in the raw message.
        :param raw_message: The complete raw message bytes.
        :return: A tuple containing the new cursor position and the extracted string.
        """
        end = raw_message.find(b'\0', cursor)
        if end == -1:
            raise DecodingError("Missing '\\0' terminator.")
        return end + 1, raw_message[cursor:end]

    def decode_message(self, raw_message: bytes) -> dict:
        cursor = 0

        # TAG
        if not raw_message.startswith(self.TAG):
            raise InvalidTagError("Invalid message tag.")
        cursor += len(self.TAG)

        # Message Type
        msg_type = raw_message[cursor:cursor + 1].decode("ascii")
        if msg_type not in ['G', 'S', 'R', 'N']:
            raise UnknownMessageTypeError(f"Invalid message type: {msg_type}")
        cursor += 1

        # Timestamp
        cursor, ts_type = self._next_str(cursor, raw_message)
        if ts_type != b'T':
            raise DecodingError("Expected timestamp type 'T'.")
        cursor, ts_len_bytes = self._next_str(cursor, raw_message)
        if not is_valid_iid(ts_len_bytes):
            raise DecodingError("Invalid timestamp length format.")
        ts_len = int(ts_len_bytes.decode("ascii"))

        ts_components = []
        for _ in range(ts_len):
            cursor, comp = self._next_str(cursor, raw_message)
            ts_components.append(comp.decode("ascii"))
        timestamp = ":".join(ts_components)

        #verificar se o timestamp é válido ?
        

        # Message ID
        cursor, message_id = self._next_str(cursor, raw_message)
        message_id = message_id.decode("ascii")

        # verificar se o message_id é válido ?

        # IID List
        cursor, num_iids_bytes = self._next_str(cursor, raw_message)
        if not is_valid_int(num_iids_bytes):
            raise DecodingError("Invalid IID List length format.")
        num_iids = int(num_iids_bytes.decode("ascii"))

        iid_list = []
        for _ in range(num_iids):
            cursor, iid_type = self._next_str(cursor, raw_message)
            if iid_type != b'D':
                raise DecodingError("Expected IID type 'D'.")
            
            cursor, iid_len_bytes = self._next_str(cursor, raw_message)
            if not is_valid_int(iid_len_bytes):
                raise DecodingError("Invalid IID length format.")
            iid_len = int(iid_len_bytes.decode("ascii"))

            iid = []
            for _ in range(iid_len):
                cursor, iid_comp = self._next_str(cursor, raw_message)
                if not is_valid_int(iid_comp):
                    raise DecodingError("Invalid IID component format.")
                iid.append(int(iid_comp.decode("ascii")))
            iid_list.append(iid)

        # Value List
        cursor, num_values_bytes = self._next_str(cursor, raw_message)
        num_values = int(num_values_bytes.decode("ascii"))
        value_list = []
        for _ in range(num_values):
            cursor, raw_val_type = self._next_str(cursor, raw_message)
            val_type = raw_val_type.decode("ascii")
            cursor, len_bytes = self._next_str(cursor, raw_message)
            length = int(len_bytes.decode("ascii"))
            value_parts = []
            for _ in range(length):
                cursor, val = self._next_str(cursor, raw_message)
                value_parts.append(val.decode("ascii"))
            value_list.append((val_type, value_parts))

        # Error List
        cursor, num_errors_bytes = self._next_str(cursor, raw_message)
        num_errors = int(num_errors_bytes.decode("ascii"))
        error_list = []
        for _ in range(num_errors):
            cursor, err = self._next_str(cursor, raw_message)
            error_list.append(int(err.decode("ascii")))

        return {
            "type": msg_type,
            "timestamp": timestamp,
            "message_id": message_id,
            "iid_list": iid_list,
            "value_list": value_list,
            "error_list": error_list
        }
    
    def encode_message(self, msg_type: str, timestamp: str, message_id: str,
                       iid_list: list[list[int]], value_list: list = None, error_list: list[int] = None) -> bytes:
            """
            Codifica uma mensagem L-SNMPvS completa com o formato especificado no enunciado.
            """

    
    def encode_iid(self, iid: list[int]) -> bytes:
            """
            Function to encode a list of integers into a byte sequence,
            where each integer is followed by a null terminator ('\0').
            Atributes:
            - iid: List of integers to be encoded.
            Returns:
            - A byte sequence where each integer is represented as a string followed by a null terminator.
            """
            converted_iid_list = []
            for n in iid:
                converted_iid_list.append((str(n) + "\0").encode("ascii"))
            converted_iid = b''.join(converted_iid_list)
            return converted_iid

    def decode_iid(self, raw: bytes) -> list[int]:
        """
        Function to decode a byte sequence into a list of integers.
        The byte sequence is expected to be in the format where each integer is represented as a string followed by a null terminator.
        Atributes:
        - raw: Byte sequence to be decoded.
        Returns:
        - A list of integers decoded from the byte sequence.
        """
        decoded = raw.decode("ascii")
        return [int(x) for x in decoded.split('\0') if x]

    def encode_value(self, value) -> bytes:
        """
        Codifica um valor no formato: DataType + Length + Value.
        """
        ...

    def decode_value(self, raw: bytes):
        """
        Descodifica um valor do formato TLV-like para valor nativo Python.
        """
        ...
