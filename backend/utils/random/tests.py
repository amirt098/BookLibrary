import uuid
from django.test import TestCase
from .services import RandomGenerator


class RandomServiceTestCase(TestCase):
    def setUp(self) -> None:
        self.random_service = RandomGenerator()

    def test_get_random_integer(self):
        random_int = self.random_service.get_random_integer(min_possible_value=0, max_possible_value=100)
        self.assertIsInstance(random_int, int)
        self.assertGreaterEqual(random_int, 0)
        self.assertLessEqual(random_int, 100)

        y = [[self.random_service.get_random_integer(min_possible_value=0, max_possible_value=100) for j in range(5)]
             for j in range(10)]
        y_set = set(tuple(x) for x in y)
        self.assertEqual(len(y_set), 10)

    def test_get_uuid(self):
        random_uuid = self.random_service.get_uuid()
        self.assertIsInstance(random_uuid, str)
        self.assertEqual(len(random_uuid), 36)
        self.assertTrue(uuid.UUID(random_uuid), True)
