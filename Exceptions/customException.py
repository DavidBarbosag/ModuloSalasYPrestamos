class customException(Exception):
    """
    Base class for all exceptions in this module.
    """
    def __init__(self, message):
        super().__init__(message)


class exception:
    # Error messages
    INVALID_ROOMAVAILABILITY = "Invalid room availability format. Must be a list of 8 lists, each containing 6 elements."
    ROOMALREADY_RESERVED = "La sala ya está reservada en este horario."
    @staticmethod
    def argumento_invalido():
        raise customException(customException.INVALID_ROOMAVAILABILITY)
