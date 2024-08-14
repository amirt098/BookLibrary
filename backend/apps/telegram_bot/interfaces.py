import abc
from enum import Enum

from apps.account import interfaces as accounts_interfaces
from lib import data_classes as lib_dataclasses


class PlatformSku(str, Enum):
    TELEGRAM: str = 'telegram'
    BALE: str = 'bale'


class BotIdentifier(lib_dataclasses.BaseModel):
    platform_sku: PlatformSku
    token: str


class SendMessageRequest(lib_dataclasses.BaseModel):
    contact_uid: str
    message: str



class AbstractBotPlatform(abc.ABC):
    @abc.abstractmethod
    def run(self, bot_identifier: BotIdentifier):
        """
            this method set listening and will get application and run polling on it.
            ARGS:
                bot_identifier (BotIdentifier): the bot identifier info ( info we need to identify the bots)

        """

        raise NotImplemented

    @abc.abstractmethod
    def send_message(self, caller: accounts_interfaces.UserClaim, message_request: SendMessageRequest):
        """
            admin call this method to send message via bot obj send message method
            ARGS:
                caller (UserClaim): the admin user claim
                message_request (SendMessageRequest): request containing contact uid and message
        """
        raise NotImplemented
