from django.test import TestCase
from unittest.mock import patch, MagicMock
from Room.models import Room
from Exceptions.customException import customException, exception

class TestRoom(TestCase):
    def setUp(self):
        self.room = Room(
            id="R001",
            location="Edificio A",
            capacity=10,
            state="Disponible",
            description="Sala de reuniones"
        )
        self.room.availability = [[[0 for _ in range(2)] for _ in range(5)] for _ in range(8)]

    @patch.object(Room, "save", MagicMock())  # mockea el método save
    def test_reserve_room_success(self):
        self.room.reserveRoom("Lunes", "7:00-8:30")
        self.assertEqual(self.room.availability[0][0], 1)

    @patch.object(Room, "save", MagicMock())
    def test_reserve_room_already_reserved(self):
        self.room.reserveRoom("Lunes", "7:00-8:30")
        with self.assertRaises(customException) as context:
            self.room.reserveRoom("Lunes", "7:00-8:30")
        self.assertEqual(str(context.exception), exception.ROOMALREADY_RESERVED)

    def test_invalid_availability_format(self):
        self.room.availability = [[0] * 5 for _ in range(8)]
        with self.assertRaises(customException) as context:
            self.room.clean()
        self.assertEqual(str(context.exception), exception.INVALID_ROOMAVAILABILITY)
