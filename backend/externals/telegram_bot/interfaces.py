import abc
from datetime import datetime
from typing import Union, Any

from lib import data_classes as lib_dataclasses
from telegram._utils.types import JSONDict
from typing_extensions import Optional
from telegram.ext import MessageHandler, filters as telegram_filters


Telegram_Text_Filter = telegram_filters.TEXT

class CallbackQuery(lib_dataclasses.BaseModel):
    chat_instance: int | None = None
    data: str

    class Config:
        arbitrary_types_allowed = True


class User(lib_dataclasses.BaseModel):
    id: int
    first_name: str
    is_bot: bool = False
    last_name: Optional[str] = None,
    username: Optional[str] = None,


class Contact(lib_dataclasses.BaseModel):
    user_id: int
    phone_number: str


class Chat(lib_dataclasses.BaseModel):
    id: int
    type: str = 'Normal'
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    api_kwargs: Optional[JSONDict] = None


class Message(lib_dataclasses.BaseModel):
    message_id: int
    chat: Chat
    from_user: User
    date: datetime | None = None
    contact: Contact | None = None
    edit_date: datetime | None = None
    text: str | None = None
    photo: Any | None = None


class Update(lib_dataclasses.BaseModel):
    update_id: int
    callback_query: CallbackQuery | None = None
    message: Optional[Message] = None
    edited_message: Optional[Message] = None
    channel_post: Optional[Message] = None
    edited_channel_post: Optional[Message] = None


class AbstractTelegramBot(abc.ABC):
    async def send_message(
            self,
            chat_id,
            text,
            parse_mode=None,
            entities=None,
            disable_web_page_preview=None,
            disable_notification=None,
            protect_content=None,
            reply_to_message_id=None,
            allow_sending_without_reply=None,
            reply_markup=None,
            message_thread_id=None,
            *,
            read_timeout=None,
            write_timeout=None,
            connect_timeout=None,
            pool_timeout=None,
            api_kwargs=None,
    ):
        raise NotImplementedError

    async def send_photo(
            self,
            chat_id,
            photo,
            caption=None,
            disable_notification=None,
            reply_markup=None,
            parse_mode=None,
            caption_entities=None,
            protect_content=None,
            message_thread_id=None,
            has_spoiler=None,
            reply_parameters=None,
            business_connection_id=None,
            message_effect_id=None,
            show_caption_above_media=None,
            *,
            allow_sending_without_reply=None,
            reply_to_message_id=None,
            filename=None,
            read_timeout=None,
            write_timeout=None,
            connect_timeout=None,
            pool_timeout=None,
            api_kwargs=None,
    ):
        raise NotImplementedError


class AbstractTelegramApplication(abc.ABC):

    @property
    @abc.abstractmethod
    def bot(self) -> AbstractTelegramBot:
        raise NotImplementedError

    @abc.abstractmethod
    def run_polling(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def add_handler(self, handler: "AbstractBaseHandler") -> None:
        raise NotImplementedError


class AbstractTelegramApplicationFactory(abc.ABC):
    def get_telegram_application(
            self,
            token: str,
            proxy: str = None,
            base_api_address: str = None,
            base_file_address: str = None,
    ) -> AbstractTelegramApplication:
        raise NotImplementedError


class AbstractBaseHandler(abc.ABC):
    """The base class for all update handlers. Create custom handlers by inheriting from it."""

    @abc.abstractmethod
    def check_update(self, update: object) -> Optional[Union[bool, object]]:
        """
        This method is called to determine if an update should be handled by
        this handler instance. It should always be overridden.
        """
        raise NotImplementedError

    async def handle_update(
            self,
            update: Update,
            application: "Any[Any, Any, Any, Any, Any, Any]",
            check_result: object,
            context: Any,
    ) -> Any:
        """
        This method is called if it was determined that an update should indeed
        be handled by this instance.
        """
        raise NotImplementedError

    def collect_additional_context(
            self,
            context: Any,
            update: Update,
            application: Any,
            check_result: Any,
    ) -> None:
        """Prepares additional arguments for the context. Override if needed.
        """
        raise NotImplementedError
