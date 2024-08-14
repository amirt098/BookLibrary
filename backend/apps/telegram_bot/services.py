import logging
from datetime import timedelta
from typing import Optional

from django.core.cache import cache
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, MessageHandler
from telegram.ext import Updater, CallbackQueryHandler

from apps.account import interfaces as account_interfaces
from apps.book import interfaces as book_interfaces

from externals.telegram_bot import interfaces as telegram_bot_interfaces
from utils.date_time import interfaces as data_time_interfaces

logger = logging.getLogger(__name__)


class TelegramBotService:
    def __init__(
            self,
            telegram_application_factory: telegram_bot_interfaces.AbstractTelegramApplicationFactory,
            bale_api_address: str,
            telegram_api_address: str,
            telegram_proxy: str | None,
            account_service: account_interfaces.AbstractAccountService,
            book_service: book_interfaces.AbstractBookService,
            date_time_utils: data_time_interfaces.AbstractDateTimeUtils,
    ):
        self.telegram_application_factory = telegram_application_factory
        self.bale_api_address = bale_api_address
        self.telegram_api_address = telegram_api_address
        self.telegram_proxy = telegram_proxy
        self.account_service = account_service
        self.book_service = book_service
        self.date_time_utils = date_time_utils
        self.cache_timeout = timedelta(days=1)

    @staticmethod
    def _get_cached_user_claim(telegram_id: int) -> Optional[account_interfaces.UserClaim]:
        return cache.get(f"user_claim_{telegram_id}")

    def _cache_user_claim(self, telegram_id: int, user_claim: account_interfaces.UserClaim):
        cache.set(f"user_claim_{telegram_id}", user_claim, self.cache_timeout)

    def handle_start(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        logger.info(f"/start command received from chat_id: {chat_id}")
        user_claim = self._get_cached_user_claim(chat_id)

        if not user_claim:
            try:
                user_claim = self.account_service.telegram_authentication(telegram_id=chat_id)
                self._cache_user_claim(chat_id, user_claim)
                self.show_welcome_message(update, context, user_claim)
            except account_interfaces.UserNotFound:
                self.show_registration_prompt(update, context)
        else:
            self.show_welcome_message(update, context, user_claim)

    def show_welcome_message(self, update: Update, context: CallbackContext, user_claim: account_interfaces.UserClaim):
        chat_id = update.message.chat_id
        message = f"Welcome back, {user_claim.username}! You can now browse and borrow books."
        context.bot.send_message(chat_id=chat_id, text=message)
        self.show_book_list(update, context, user_claim)

    def show_registration_prompt(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        message = "Welcome to the library bot! Please register to continue."
        buttons = [[InlineKeyboardButton("Register", callback_data="register")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

    def handle_books(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        logger.info(f"/books command received from chat_id: {chat_id}")

        user_claim = self._get_cached_user_claim(chat_id)
        if not user_claim:
            self.show_registration_prompt(update, context)
        else:
            self.show_book_list(update, context, user_claim)

    def show_book_list(self, update: Update, context: CallbackContext, user_claim: account_interfaces.UserClaim):
        chat_id = update.message.chat_id
        logger.info(f"Fetching and showing book list to chat_id: {chat_id}")

        books = self.book_service.get_books(user_claim, filters={})
        buttons = [
            [InlineKeyboardButton(book.title, callback_data=f"borrow_{book.title}")]
            for book in books.result
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=chat_id, text="Here are the available books:", reply_markup=reply_markup)

    def handle_button_click(self, update: Update, context: CallbackContext):
        query = update.callback_query
        chat_id = query.message.chat_id
        query_data = query.data

        logger.info(f"Button clicked by chat_id: {chat_id}, data: {query_data}")
        user_claim = self._get_cached_user_claim(chat_id)

        if not user_claim:
            self.show_registration_prompt(update, context)
        elif query_data == "register":
            self.register_user(update, context)
        elif query_data.startswith("borrow_"):
            book_title = query_data.split("_", 1)[1]
            self.borrow_book(update, context, user_claim, book_title)

    def register_user(self, update: Update, context: CallbackContext):
        chat_id = update.callback_query.message.chat_id
        logger.info(f"Registering new user for chat_id: {chat_id}")

        # Registration process here...
        # This could be sending a registration form or handling inline input.

        context.bot.send_message(chat_id=chat_id, text="You have been registered successfully!")

    def borrow_book(self, update: Update, context: CallbackContext, user_claim: account_interfaces.UserClaim, book_title: str):
        chat_id = update.callback_query.message.chat_id
        logger.info(f"User {user_claim.username} attempting to borrow {book_title}")
        try:
            self.book_service.borrow_book(user_claim, book_title)
            context.bot.send_message(chat_id=chat_id, text=f"You have successfully borrowed '{book_title}'!")
        except book_interfaces.BookNotFound:
            context.bot.send_message(chat_id=chat_id, text=f"Book '{book_title}' not found.")

    def handle_unknown(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        logger.info(f"Received unknown command from chat_id: {chat_id}")
        context.bot.send_message(chat_id=chat_id, text="Sorry, I didn't understand that command.")

    def start_polling(self):
        self.updater.start_polling()
        logger.info("Bot started polling.")
