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
    ROOM_NOT_FOUND = "Room not found."
    INVALID_ARGS = "Invalid arguments provided."

    @staticmethod
    def raise_invalid_room_availability():
        raise customException(exception.INVALID_ROOMAVAILABILITY)

    @staticmethod
    def raise_room_already_reserved():
        raise customException(exception.ROOMALREADY_RESERVED)

    @staticmethod
    def raise_room_not_found():
        raise customException(exception.ROOM_NOT_FOUND)

    @staticmethod
    def raise_invalid_args():
        raise customException(exception.INVALID_ARGS)