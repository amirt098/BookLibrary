import logging
from datetime import timedelta
from typing import Optional, Dict
from math import ceil

from django.core.cache import cache
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, Updater, CallbackQueryHandler, CommandHandler, MessageHandler

from apps.account import interfaces as account_interfaces
from apps.book import interfaces as book_interfaces
from externals.telegram_bot import interfaces as telegram_bot_interfaces
from utils.date_time import interfaces as date_time_interfaces
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class TelegramBotService:
    def __init__(
            self,
            telegram_application_factory: telegram_bot_interfaces.AbstractTelegramApplicationFactory,
            bale_api_address: str,
            telegram_api_address: str,
            telegram_proxy: Optional[str],
            account_service: account_interfaces.AbstractAccountService,
            borrowing_book: book_interfaces.AbstractBookService,
            date_time_utils: date_time_interfaces.AbstractDateTimeUtils,
    ):
        self.telegram_application_factory = telegram_application_factory
        self.bale_api_address = bale_api_address
        self.telegram_api_address = telegram_api_address
        self.telegram_proxy = telegram_proxy
        self.account_service = account_service
        self.borrowing_book = borrowing_book
        self.date_time_utils = date_time_utils
        self.cache_timeout = timedelta(days=1)

        # State mapping
        self.state_map: Dict[str, callable] = {
            "start": self.show_welcome_message,
            "books": self.show_book_list,
            "register": self.register_user,
            "borrow": self.borrow_book,
            "unknown": self.handle_unknown,
        }

        # Example commands map (this will trigger different states)
        self.command_map = {
            "/start": "start",
            "/books": "books",
        }

    @staticmethod
    def _get_cached_user_claim(telegram_id: int) -> Optional[account_interfaces.UserClaim]:
        return cache.get(f"user_claim_{telegram_id}")

    def _cache_user_claim(self, telegram_id: int, user_claim: account_interfaces.UserClaim):
        cache.set(f"user_claim_{telegram_id}", user_claim, self.cache_timeout)

    def handler(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
        text = update.message.text if update.message else update.callback_query.data

        logger.info(f"Received input from chat_id: {chat_id}, text/data: {text}")

        user_claim = self._get_cached_user_claim(chat_id)

        if not user_claim:
            try:
                user_claim = self.account_service.telegram_authentication(telegram_id=chat_id)
                self._cache_user_claim(chat_id, user_claim)
            except account_interfaces.UserNotFound:
                self.show_registration_prompt(update, context)
                return
            except Exception as e:
                logger.error(f"Error during authentication: {str(e)}")
                context.bot.send_message(chat_id=chat_id, text="An error occurred. Please try again.")
                return

        if text.startswith("/start"):
            self.show_welcome_message(update, context, user_claim)
        elif text.startswith("/books") or text.startswith("page_"):
            page = int(text.split("_")[1]) if "page_" in text else 1
            self.show_book_list(update, context, user_claim, page)
        elif text.startswith("show_"):
            book_id = text.split("_")[1]
            self.show_book_details(update, context, user_claim, book_id)
        elif text.startswith("borrow_"):
            book_id = text.split("_")[1]
            self.borrow_book(update, context, user_claim, book_id)
        elif text.startswith("return_"):
            book_id = text.split("_")[1]
            self.return_book(update, context, user_claim, book_id)
        else:
            self.handle_unknown(update, context)

    def show_welcome_message(self, update: Update, context: CallbackContext, user_claim: account_interfaces.UserClaim,
                             *args):
        chat_id = update.message.chat_id
        message = f"Welcome back, {user_claim.username}! You can now browse and borrow books."
        context.bot.send_message(chat_id=chat_id, text=message)
        self.show_book_list(update, context, user_claim)

    def show_book_list(self, update: Update, context: CallbackContext, user_claim: account_interfaces.UserClaim, page: int = 1):
        chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
        logger.info(f"Fetching and showing paginated book list to chat_id: {chat_id}, page: {page}")

        try:
            books_per_page = 5  # Number of books per page
            all_books = self.book_service.get_books(user_claim=user_claim, filters={})  # Fetch all books
            total_pages = ceil(len(all_books) / books_per_page)

            start_index = (page - 1) * books_per_page
            end_index = start_index + books_per_page
            books = all_books[start_index:end_index]

            buttons = [
                [InlineKeyboardButton(book.title, callback_data=f"show_{book.id}")]
                for book in books
            ]

            navigation_buttons = []
            if page > 1:
                navigation_buttons.append(InlineKeyboardButton("Previous", callback_data=f"page_{page - 1}"))
            if page < total_pages:
                navigation_buttons.append(InlineKeyboardButton("Next", callback_data=f"page_{page + 1}"))

            if navigation_buttons:
                buttons.append(navigation_buttons)

            reply_markup = InlineKeyboardMarkup(buttons)
            context.bot.send_message(chat_id=chat_id, text="Here are the available books:", reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error fetching book list: {str(e)}")
            context.bot.send_message(chat_id=chat_id, text="An error occurred while fetching the book list.")

    def show_book_details(self, update: Update, context: CallbackContext, user_claim: account_interfaces.UserClaim, book_id: str):
        chat_id = update.callback_query.message.chat_id
        logger.info(f"User {user_claim.username} is viewing details for book {book_id}")

        try:
            book = self.book_service.get_book_by_id(book_id)
            message = f"Title: {book.title}\nAuthor: {book.author}\nPublished: {book.published_date}\n\nDescription: {book.description}"

            # Check if the user has already borrowed the book
            if self.book_service.has_user_borrowed_book(user_claim, book_id):
                buttons = [[InlineKeyboardButton("Return", callback_data=f"return_{book.id}")]]
            else:
                buttons = [[InlineKeyboardButton("Borrow", callback_data=f"borrow_{book.id}")]]

            reply_markup = InlineKeyboardMarkup(buttons)
            context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
        except book_interfaces.BookNotFound:
            context.bot.send_message(chat_id=chat_id, text="The selected book was not found.")
        except Exception as e:
            logger.error(f"Error fetching book details: {str(e)}")
            context.bot.send_message(chat_id=chat_id, text="An error occurred while fetching the book details.")



    def register_user(self, update: Update, context: CallbackContext, *args):
        chat_id = update.callback_query.message.chat_id
        logger.info(f"Registering new user for chat_id: {chat_id}")

        # Registration process here...
        context.bot.send_message(chat_id=chat_id, text="You have been registered successfully!")

    def borrow_book(self, update: Update, context: CallbackContext, user_claim: account_interfaces.UserClaim, book_id: str):
        chat_id = update.callback_query.message.chat_id
        logger.info(f"User {user_claim.username} attempting to borrow book ID: {book_id}")

        try:
            self.book_service.borrow_book(user_claim=user_claim, book_id=book_id)
            context.bot.send_message(chat_id=chat_id, text=f"You have successfully borrowed the book!")
        except book_interfaces.BookNotFound:
            context.bot.send_message(chat_id=chat_id, text="The book was not found.")
        except Exception as e:
            logger.error(f"Error borrowing book: {str(e)}")
            context.bot.send_message(chat_id=chat_id, text="An error occurred while borrowing the book.")

    def return_book(self, update: Update, context: CallbackContext, user_claim: account_interfaces.UserClaim, book_id: str):
        chat_id = update.callback_query.message.chat_id
        logger.info(f"User {user_claim.username} attempting to return book ID: {book_id}")

        try:
            self.book_service.return_book(user_claim=user_claim, book_id=book_id)
            context.bot.send_message(chat_id=chat_id, text=f"You have successfully returned the book!")
        except book_interfaces.BookNotFound:
            context.bot.send_message(chat_id=chat_id, text="The book was not found.")
        except Exception as e:
            logger.error(f"Error returning book: {str(e)}")
            context.bot.send_message(chat_id=chat_id, text="An error occurred while returning the book.")



    def handle_unknown(self, update: Update, context: CallbackContext, *args):
        chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
        logger.info(f"Received unknown command from chat_id: {chat_id}")
        context.bot.send_message(chat_id=chat_id, text="Sorry, I didn't understand that command.")

    def start_polling(self):
        updater = self.telegram_application_factory.create_updater(api_address=self.telegram_api_address, proxy=self.telegram_proxy)

        dp = updater.dispatcher

        dp.add_handler(CommandHandler(["start", "books"], self.handler))
        dp.add_handler(CallbackQueryHandler(self.handler))
        dp.add_handler(MessageHandler(None, self.handler))  # Handle all other messages

        updater.start_polling()
        logger.info("Bot started polling.")