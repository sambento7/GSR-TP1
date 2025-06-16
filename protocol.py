class Protocol:
    TAG = "kdk847ufh84jg87g\0"

    def encode_message(self, msg_type: str, timestamp: str, message_id: str,
                       iid_list: list[list[int]], value_list: list = None, error_list: list[int] = None) -> bytes:
        """
        Codifica uma mensagem L-SNMPvS completa com o formato especificado no enunciado.
        """
        ...

    def decode_message(self, raw_message: bytes) -> dict:
        """
        Descodifica uma mensagem L-SNMPvS recebida, validando cada parte da estrutura.
        """
        ... 

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
