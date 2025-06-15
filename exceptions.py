class LSNMPvSError(Exception):
    """Classe base para exceções do protocolo L-SNMPvS."""
    pass

class DecodingError(LSNMPvSError):
    """Erro na descodificação da mensagem (código 1)."""
    pass

class InvalidTagError(LSNMPvSError):
    """Erro na Tag da mensagem (código 2)."""
    pass

class UnknownMessageTypeError(LSNMPvSError):
    """Tipo de mensagem desconhecido (código 3)."""
    pass

class DuplicateMessageError(LSNMPvSError):
    """Mensagem duplicada (código 4)."""
    pass

class InvalidIIDError(LSNMPvSError):
    """IID inválido ou desconhecido (código 5)."""
    pass

class InvalidValueTypeError(LSNMPvSError):
    """Tipo de valor desconhecido (código 6)."""
    pass

class UnsupportedValueError(LSNMPvSError):
    """Valor fora dos limites ou não suportado (código 7)."""
    pass

class IIDValueMismatchError(LSNMPvSError):
    """Número de valores não corresponde ao número de IIDs (código 8)."""
    pass

class NoDevicesRegisteredError(LSNMPvSError):
    """Nenhum sensor ou atuador registado (código 9)."""
    pass
