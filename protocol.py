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
        converted_iid_list = []
        for n in iid:
            converted_iid_list.append((str(n) + "\0").encode("ascii"))
        converted_iid = b''.join(converted_iid_list)
        return converted_iid

    def decode_iid(self, raw: bytes) -> list[int]:
        """
        Descodifica uma sequência em bytes com inteiros terminados por '\0' para uma lista de ints.
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
