from django.test import TestCase
from unittest.mock import patch, MagicMock
from Room.models import Room, RoomXElements
from RecreativeElement.models import RecreativeElement
from Exceptions.customException import customException, exception

class TestRoom(TestCase):
    def setUp(self):
        self.element1 = RecreativeElement.objects.create(name="Mesa de Ping Pong", quantity=2)
        self.element2 = RecreativeElement.objects.create(name="Futbolín", quantity=1)

        self.room = Room.objects.create(
            location="Edificio A",
            capacity=10,
            state="Disponible",
            description="Sala de reuniones"
        )

        RoomXElements.objects.create(room=self.room, element=self.element1, amount=2)
        RoomXElements.objects.create(room=self.room, element=self.element2, amount=1)

    def tearDown(self):
        RoomXElements.objects.all().delete()
        RecreativeElement.objects.all().delete()
        Room.objects.all().delete()

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

    def test_get_room_availability_success(self):
        availability = self.room.getRoomAvailability(self.room.id)
        self.assertEqual(availability, [[0] * 6 for _ in range(8)])

    def test_get_room_availability_room_not_found(self):
        with self.assertRaises(customException) as context:
            Room().getRoomAvailability(999)
        self.assertEqual(str(context.exception), exception.ROOM_NOT_FOUND)

    def test_get_recrereative_elements_success(self):
        self.assertEqual(RecreativeElement.objects.count(), 2)
        self.assertEqual(RoomXElements.objects.count(), 2)

        result = self.room.getRecrereativeElements(self.room.id)
        expected = [
            {"name": "Mesa de Ping Pong", "quantity": 2},
            {"name": "Futbolín", "quantity": 1}
        ]

        self.assertEqual(sorted(result, key=lambda x: x['name']),
                         sorted(expected, key=lambda x: x['name']))
