import abc
from typing import List
from enum import Enum
from lib import data_classes as lib_dataclasses


class UserClaim(lib_dataclasses.BaseModel):
    username: str
    telegram_id: int | None = None


class UserInfo(lib_dataclasses.BaseModel):
    username: str
    email: str | None = None
    password: str | None = None
    telegram_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    mobile: str | None = None


# class TelegramAuthInfo(lib_dataclasses.BaseModel):
#     telegram_id


class AbstractAccountService(abc.ABC):

    def register_new_user(self, user: UserInfo):
        """
        Raise:
            DuplicatedTelegramId
            DuplicatedUserName
        """
        raise NotImplementedError

    async def telegram_authentication(self, telegram_id) -> UserClaim:
        """
        Raise:
            UserNotFound
        """
        raise NotImplementedError


class DuplicatedTelegramId(Exception):
    pass


class DuplicatedUserName(Exception):
    pass


class UserNotFound(Exception):
    pass
