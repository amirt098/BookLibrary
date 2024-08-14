import abc


class AbstractRandomGenerator(abc.ABC):

    def get_random_integer(self, min_possible_value=0, max_possible_value=1) -> int:
        raise NotImplementedError

    def get_uuid(self) -> str:
        raise NotImplementedError

    def get_random_string(self, length: int) -> str:
        raise NotImplementedError
