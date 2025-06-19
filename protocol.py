import sys
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

        # Message Type: agora aceitamos G, S, R, N
        msg_type = raw_message[cursor:cursor + 1].decode("ascii")
        if msg_type not in ['G', 'S', 'R', 'N']:
            raise UnknownMessageTypeError(f"Invalid message type: {msg_type}")
        cursor += 1

        # Timestamp
        cursor, ts_type = self._next_str(cursor, raw_message)
        if ts_type != b'T':
            raise DecodingError("Expected timestamp type 'T'.")
        cursor, ts_len_b = self._next_str(cursor, raw_message)
        if not is_valid_int(ts_len_b.decode("ascii")):
            raise DecodingError("Invalid timestamp length.")
        ts_len = int(ts_len_b.decode("ascii"))

        # definir comprimento esperado: 7 para G/S, 5 para R/N
        expected = 7 if msg_type in ['G','S'] else 5
        if ts_len != expected:
            raise DecodingError(f"Invalid timestamp length for message type {msg_type}.")

        ts_components = []
        for _ in range(ts_len):
            cursor, comp = self._next_str(cursor, raw_message)
            if not is_valid_int(comp.decode("ascii")):
                raise DecodingError("Invalid timestamp component format.")
            ts_components.append(comp.decode("ascii"))
        timestamp = ":".join(ts_components)

        # para GET/SET validamos formato date completo, para R/N podemos pular ou validar intervalo
        if msg_type in ['G','S'] and not validate_date_format(timestamp):
            raise DecodingError("Invalid timestamp format.")
        # (opcional) poderias validar intervalo R/N também

        # Message ID
        cursor, mid_b = self._next_str(cursor, raw_message)
        message_id = mid_b.decode("ascii")
        if len(message_id) != 16:
            raise DecodingError("Invalid message ID length. Expected 16 characters.")

        # IID List
        cursor, n_iids_b = self._next_str(cursor, raw_message)
        if not is_valid_int(n_iids_b.decode("ascii")):
            raise DecodingError("Invalid IID List length format.")
        num_iids = int(n_iids_b.decode("ascii"))

        iid_list = []
        for _ in range(num_iids):
            cursor, iid_t = self._next_str(cursor, raw_message)
            if iid_t != b'D':
                raise DecodingError("Expected IID type 'D'.")
            cursor, iid_len_b = self._next_str(cursor, raw_message)
            if not is_valid_int(iid_len_b.decode("ascii")) or int(iid_len_b.decode("ascii")) not in [2,3,4]:
                raise DecodingError("Invalid IID length.")
            iid_len = int(iid_len_b.decode("ascii"))

            iid = []
            for _ in range(iid_len):
                cursor, comp = self._next_str(cursor, raw_message)
                if not is_valid_int(comp.decode("ascii")):
                    raise DecodingError("Invalid IID component format.")
                iid.append(int(comp.decode("ascii")))
            iid_list.append(iid)

        # Value List
        cursor, n_values_b = self._next_str(cursor, raw_message)
        if not is_valid_int(n_values_b.decode("ascii")):
            raise DecodingError("Invalid Value List length format.")
        num_values = int(n_values_b.decode("ascii"))

        # regras diferentes para cada tipo
        if msg_type == 'G' and num_values != 0:
            raise DecodingError("Get request should not contain values.")
        if msg_type == 'S' and num_values != num_iids:
            raise IIDValueMismatchError("Number of values does not match number of IIDs.")
        # em R/N não requeremos correspondência, pode haver <>, mas tipicamente equals

        value_list = []
        for _ in range(num_values):
            cursor, vt_b = self._next_str(cursor, raw_message)
            val_type = vt_b.decode("ascii")
            if val_type not in ['I','T','S']:
                raise InvalidValueTypeError(f"Unsupported value type '{val_type}' for {msg_type} message.")
            cursor, len_b = self._next_str(cursor, raw_message)
            if not is_valid_int(len_b):
                raise DecodingError("Invalid value length format.")
            length = int(len_b.decode("ascii"))

            # validações de comprimento por tipo
            if val_type in ['I','S'] and length != 1:
                raise DecodingError(f"Type {val_type} must have length 1.")
            if val_type == 'T' and length not in (5,7):
                raise DecodingError(f"Invalid timestamp length for value in {msg_type} message.")

            parts = []
            for _ in range(length):
                cursor, v = self._next_str(cursor, raw_message)
                txt = v.decode("ascii")
                if val_type in ['I','T'] and not is_valid_int(txt):
                    raise DecodingError("Invalid value format.")
                parts.append(txt)
            if val_type == 'T':
                ts_joined = ":".join(parts)
                # validamos date-format só se for '7'; se for '5' opcional
                if length == 7 and not validate_date_format(ts_joined):
                    raise DecodingError("Invalid date timestamp format.")
            value_list.append((val_type, parts))

        # Error List
        cursor, n_err_b = self._next_str(cursor, raw_message)
        if not is_valid_int(n_err_b):
            raise DecodingError("Invalid Error List length format.")
        num_err = int(n_err_b.decode("ascii"))

        # G/S devem ter zero erros; R/N podem ter >=1
        if msg_type in ['G','S'] and num_err != 0:
            raise DecodingError(f"Error List should be empty for {msg_type} requests.")

        error_list = []
        for _ in range(num_err):
            cursor, eb = self._next_str(cursor, raw_message)
            if not is_valid_int(eb.decode("ascii")):
                raise DecodingError("Invalid error code format.")
            error_list.append(int(eb.decode("ascii")))

        if cursor != len(raw_message):
            raise DecodingError("Extra data found after expected end of message.")

        return {
            "type":       msg_type,
            "timestamp":  timestamp,
            "message_id": message_id,
            "iid_list":   iid_list,
            "value_list": value_list,
            "error_list": error_list
        }

    def encode_message(self, msg_type: str, timestamp: str, message_id: str,
                   iid_list: list[list[int]], value_list: list = None, error_list: list[int] = None) -> bytes:
        """
        Codifica uma mensagem L-SNMPvS completa com o formato especificado no enunciado.
        """
        # Validação do tipo de mensagem
        if msg_type not in ['G', 'S', 'R', 'N']:
            raise UnknownMessageTypeError(f"Invalid message type: {msg_type}")

        # Validação do message_id
        if not isinstance(message_id, str) or len(message_id) != 16:
            raise DecodingError("Invalid message ID length. Expected 16 characters.")

        # Validação do IID
        if not isinstance(iid_list, list) or not all(isinstance(iid, list) and all(isinstance(x, int) for x in iid) for iid in iid_list):
            raise DecodingError("Invalid IID format.")
        for iid in iid_list:
            if len(iid) not in [2, 3, 4]:
                raise DecodingError("Invalid IID length.")

        # Timestamp
        ts_parts = timestamp.split(":")
        if msg_type in ['G', 'S'] and len(ts_parts) != 7:
            raise DecodingError("Invalid timestamp length.")
        if msg_type in ['R', 'N'] and len(ts_parts) != 5:
            raise DecodingError("Invalid timestamp length.")
        ts_bytes = b"T\0" + str(len(ts_parts)).encode("ascii") + b"\0"
        for part in ts_parts:
            if not part.isdigit():
                raise DecodingError("Invalid timestamp component format.")
            ts_bytes += part.encode("ascii") + b"\0"

        # IID List
        iid_bytes = str(len(iid_list)).encode("ascii") + b"\0"
        for iid in iid_list:
            iid_bytes += b"D\0" + str(len(iid)).encode("ascii") + b"\0"
            for val in iid:
                iid_bytes += str(val).encode("ascii") + b"\0"

        # Value List
        value_bytes = b""
        if msg_type == 'G':
            if value_list not in (None, []) or error_list not in (None, []):
                raise DecodingError("Get request should not contain values.")
            value_bytes = b"0\0"
            error_bytes = b"0\0"

        elif msg_type == 'S':
            if not isinstance(value_list, list) or len(value_list) != len(iid_list):
                raise IIDValueMismatchError("Number of values does not match number of IIDs.")
            value_bytes = str(len(value_list)).encode("ascii") + b"\0"
            for (val_type, val_parts) in value_list:
                if val_type not in ['I', 'T', 'S']:
                    raise InvalidValueTypeError(f"Unsupported value type '{val_type}' in value list for message type {msg_type}.")
                value_bytes += val_type.encode("ascii") + b"\0"
                value_bytes += str(len(val_parts)).encode("ascii") + b"\0"
                for part in val_parts:
                    if val_type in ['I', 'T'] and not is_valid_int(part):
                        raise DecodingError("Invalid value format.")
                    value_bytes += str(part).encode("ascii") + b"\0"
            error_bytes = b"0\0"

        elif msg_type == 'R':
            print("value_list", value_list)
            if not isinstance(value_list, list) or not isinstance(error_list, list):
                raise DecodingError("Invalid value or error list for response.")
            value_bytes = str(len(value_list)).encode("ascii") + b"\0"
            for (val_type, val_parts) in value_list:
                if val_type not in ['I', 'T', 'S']:
                    raise InvalidValueTypeError(f"Unsupported value type '{val_type}' in value list for message type {msg_type}.")
                value_bytes += val_type.encode("ascii") + b"\0"
                value_bytes += str(len(val_parts)).encode("ascii") + b"\0"
                for part in val_parts:
                    print(f"Part: {part}, Type: {val_type}")
                    print(f"Is valid int: {is_valid_int(part)}")
                    if val_type in ['I', 'T'] and not is_valid_int(part):
                        raise DecodingError("Invalid value format.")
                    value_bytes += str(part).encode("ascii") + b"\0"
            error_bytes = str(len(error_list)).encode("ascii") + b"\0"
            for err in error_list:
                error_bytes += str(err).encode("ascii") + b"\0"

        elif msg_type == 'N':
            value_bytes = str(len(value_list or [])).encode("ascii") + b"\0"
            if value_list:
                for (val_type, val_parts) in value_list:
                    if val_type not in ['I', 'T', 'S']:
                        raise InvalidValueTypeError(f"Unsupported value type '{val_type}' in value list for message type {msg_type}.")
                    value_bytes += val_type.encode("ascii") + b"\0"
                    value_bytes += str(len(val_parts)).encode("ascii") + b"\0"
                    for part in val_parts:
                        if val_type in ['I', 'T'] and not str(part).isdigit():
                            raise DecodingError("Invalid value format.")
                        value_bytes += str(part).encode("ascii") + b"\0"
            error_bytes = b"0\0"

        # Montagem final da mensagem
        full_message = (
            self.TAG +
            msg_type.encode("ascii") +
            ts_bytes +
            message_id.encode("ascii") + b"\0" +
            iid_bytes +
            value_bytes +
            error_bytes
        )
        return full_message
    
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
