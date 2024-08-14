import random
import string
import uuid
from . import interfaces


class RandomGenerator(interfaces.AbstractRandomGenerator):

    def get_random_integer(self, min_possible_value=10000, max_possible_value=99999) -> int:
        return random.randint(min_possible_value, max_possible_value)

    def get_uuid(self) -> str:
        return str(uuid.uuid4())

    def get_random_string(self, length=4) -> str:
        return ''.join(random.choices(
            string.ascii_uppercase,
            k=length)
        )
