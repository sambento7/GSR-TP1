from exceptions import LSNMPvSError, DecodingError, InvalidTagError, UnknownMessageTypeError, InvalidValueTypeError, IIDValueMismatchError
from utils.format_utils import is_valid_int, validate_date_format

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
        if msg_type not in ['G', 'S']:
            raise UnknownMessageTypeError(f"Invalid message type: {msg_type}")
        cursor += 1

        # Timestamp
        # Extracting the timestamp type
        cursor, ts_type_bytes = self._next_str(cursor, raw_message)
        if ts_type_bytes != b'T':
            raise DecodingError("Expected timestamp type 'T'.")
        
        cursor, ts_len_bytes = self._next_str(cursor, raw_message)
        if not is_valid_int(ts_len_bytes.decode("ascii")) or ts_len_bytes.decode("ascii") != '7':
            raise DecodingError("Invalid timestamp length.")
        ts_len = int(ts_len_bytes.decode("ascii"))

        ts_components = []
        for _ in range(ts_len):
            cursor, comp = self._next_str(cursor, raw_message)
            if not is_valid_int(comp.decode("ascii")):
                raise DecodingError("Invalid timestamp component format.")
            ts_components.append(comp.decode("ascii"))
        timestamp = ":".join(ts_components)
        if not validate_date_format(timestamp):
            raise DecodingError("Invalid timestamp format.")

        # Message ID
        cursor, message_id_bytes = self._next_str(cursor, raw_message)
        message_id = message_id_bytes.decode("ascii")
        if len(message_id) != 16:
            raise DecodingError("Invalid message ID length. Expected 16 characters.")
        #TODO ver no agente que o message_id é único

        # IID List:

        #Number of IIDs present on the list
        cursor, num_iids_bytes = self._next_str(cursor, raw_message)
        if not is_valid_int(num_iids_bytes.decode("ascii")):
            raise DecodingError("Invalid IID List length format.")
        num_iids = int(num_iids_bytes.decode("ascii"))

        iid_list = []
        # Each IID is a list of integers, starting with a type 'D' followed by its length and components
        for _ in range(num_iids):
            cursor, iid_type = self._next_str(cursor, raw_message)
            if iid_type != b'D':
                raise DecodingError("Expected IID type 'D'.")
            
            cursor, iid_len_bytes = self._next_str(cursor, raw_message)
            if not is_valid_int(iid_len_bytes.decode("ascii")) or int(iid_len_bytes.decode("ascii")) not in [2,3,4]:
                raise DecodingError("Invalid IID length.")
            iid_len = int(iid_len_bytes.decode("ascii"))
 
            iid = []
            for _ in range(iid_len):
                cursor, iid_comp = self._next_str(cursor, raw_message)
                if not is_valid_int(iid_comp.decode("ascii")):
                    raise DecodingError("Invalid IID component format.")
                iid.append(int(iid_comp.decode("ascii")))
            iid_list.append(iid)

        
        # Value List:
        cursor, num_values_bytes = self._next_str(cursor, raw_message)
        if not is_valid_int(num_values_bytes.decode("ascii")):
            raise DecodingError("Invalid Value List length format.")
        num_values = int(num_values_bytes.decode("ascii"))

        if msg_type == 'S' and num_values != num_iids:
            raise IIDValueMismatchError("Number of values does not match number of IIDs.")
        if msg_type == 'G' and num_values != 0:
            raise DecodingError("Get request should not contain values.")

        value_list = []
        for _ in range(num_values):
            cursor, raw_val_type = self._next_str(cursor, raw_message)
            val_type = raw_val_type.decode("ascii")
            if val_type not in ['I', 'T', 'S']:
                raise InvalidValueTypeError(f"Unsupported value type '{val_type}' in value list for message type {msg_type}.")

            cursor, len_bytes = self._next_str(cursor, raw_message)
            if not is_valid_int(len_bytes):
                raise DecodingError("Invalid value length format.")
            length = int(len_bytes.decode("ascii"))

            if val_type in ['I', 'S'] and length != 1:
                raise DecodingError(f"Type {val_type} must have length 1.")
            if val_type == 'T' and length != 7: 
                raise DecodingError(f"Invalid timestamp length for {msg_type} messages.")

            value_parts = []
            for _ in range(length):
                cursor, val = self._next_str(cursor, raw_message)
                if (val_type == 'I' or val_type == 'T') and not is_valid_int(val.decode("ascii")):
                    raise DecodingError("Invalid value format.")
                value_parts.append(val.decode("ascii"))

            if val_type == 'T':
                joined_ts = ":".join(value_parts)
                if not validate_date_format(joined_ts):
                    raise DecodingError("Invalid date timestamp format.")
            value_list.append((val_type, value_parts))

        # Error List
        cursor, num_errors_bytes = self._next_str(cursor, raw_message)
        if not is_valid_int(num_errors_bytes):
            raise DecodingError("Invalid Error List length format.")
        num_errors = int(num_errors_bytes.decode("ascii"))
        if num_errors != 0:
            raise DecodingError(f"Error List should be empty for {msg_type} requests.")

        if cursor != len(raw_message):
            raise DecodingError("Extra data found after expected end of message.")

        return {
            "type": msg_type,
            "timestamp": timestamp,
            "message_id": message_id,
            "iid_list": iid_list,
            "value_list": value_list,
            "error_list": []
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
