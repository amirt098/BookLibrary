import logging
import uuid
from datetime import timedelta
from typing import Optional
from math import ceil

from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.db import transaction
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, Updater, CallbackQueryHandler, CommandHandler, MessageHandler

from apps.account import interfaces as account_interfaces
from apps.borrowing_book import interfaces as borrowing_book_interfaces
from apps.offer_book import interfaces as offer_book_interfaces

from apps.telegram_bot.models import Contact, Process, Field
from externals.telegram_bot import interfaces as telegram_bot_interfaces
from utils.date_time import interfaces as date_time_interfaces

logger = logging.getLogger(__name__)

OFFER_BOOK = "offer_book"
OFFER_BOOK_TITLE = "offer_book_title"
TOPIC = 'topic'
WRITER = 'writer'
PUBLISHER = 'publisher'
PURCHASE_LINK = 'purchase_link'

REGISTRATION = "registration"
USERNAME = 'username'


class TelegramBotService:

    def __init__(
            self,
            telegram_application_factory: telegram_bot_interfaces.AbstractTelegramApplicationFactory,
            telegram_api_address: str,
            telegram_proxy: Optional[str],
            account_service: account_interfaces.AbstractAccountService,
            borrowing_book: borrowing_book_interfaces.AbstractLibraryFacade,
            offer_book: offer_book_interfaces.AbstractOfferBookService,
            date_time_utils: date_time_interfaces.AbstractDateTimeUtils,
            token: str
    ):
        self.telegram_application_factory = telegram_application_factory
        self.telegram_api_address = telegram_api_address
        self.telegram_proxy = telegram_proxy
        self.account_service = account_service
        self.borrowing_book_service = borrowing_book
        self.offer_book_service = offer_book
        self.date_time_utils = date_time_utils
        self.cache_timeout = timedelta(days=1)
        self.token = token

        self._command_text = (" Here are some commands you can use:\n"
                              "/books - View List of all books\n"
                              "/borrowed_books - View List of borrowed books\n"
                              "/offered_books - View List of offered books\n"
                              "/offer_book - Start the process of offering a book\n"
                              "/dismiss - Dismiss of any process \n"
                              "/start - show this command again")

        self.process_instruction = {
            OFFER_BOOK: [
                Process.STATUS_INITIATE,
                OFFER_BOOK_TITLE, WRITER, TOPIC, PUBLISHER, PURCHASE_LINK,
                Process.STATUS_FINISHED
            ],

        }
        self.process_final_step_mapper = {
            OFFER_BOOK: self.offer_book_final_step,

        }
        self.process_message_handler = {
            OFFER_BOOK: {
                OFFER_BOOK_TITLE: "Please Enter your offer book title.",
                WRITER: "Please Enter the author of book.",
                TOPIC: "Please Enter the topic of the book.",
                PUBLISHER: "Please Enter the publisher of the book.",
                PURCHASE_LINK: "Please Enter link for purchasing the book."
            },

        }

    def start_polling(self):
        bot = self.telegram_application_factory.get_telegram_application(
            token=self.token,
            base_api_address=self.telegram_api_address
        )

        bot.add_handler(CallbackQueryHandler(self.handler))
        bot.add_handler(MessageHandler(None, self.handler))
        bot.add_handler(CommandHandler(["start", "books", "borrowed_books"], self.handler))

        bot.run_polling()
        logger.info("Bot started polling.")

    async def process_engine(
            self,
            update: Update,
            context: CallbackContext,
            user_claim: account_interfaces.UserClaim,
            process_uid: str
    ):
        process = await Process.objects.aget(uid=process_uid)
        logger.info(f'user_claim: {user_claim}, process: {process}')
        if process.status != Process.STATUS_INITIATE:
            field = await Field.objects.acreate(
                process=process,
                name=process.status,
                value=update.message.text
            )
            logger.info(f'field: {field}')

        process.step_counter += 1
        process.status = self.process_instruction[process.type][process.step_counter]
        if process.status == Process.STATUS_FINISHED:
            # final step of process
            await self.process_final_step_mapper.get(process.type)(update, context, user_claim, process.uid)
            return
        message = self.process_message_handler[process.type][process.status]
        logger.info(f'status: {process.status}, message: {message}')
        await process.asave()
        await context.bot.send_message(chat_id=user_claim.telegram_id, text=message)

    @staticmethod
    def _get_cached_user_claim(telegram_id: int) -> Optional[account_interfaces.UserClaim]:
        return cache.get(f"user_claim_{telegram_id}")

    async def _cache_user_claim(self, telegram_id: int, user_claim: account_interfaces.UserClaim):
        logger.info(f'cache: {telegram_id}: {user_claim}')
        cache.set(f"user_claim_{telegram_id}", user_claim, 24 * 60 * 60)

    async def handler(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
        text = update.message.text if update.message else update.callback_query.data

        logger.info(f" \n\n\n >>>>>>>> Received input from chat_id: {chat_id}, text/data: {text} <<<<<<<<< \n\n\n")

        user_claim = self._get_cached_user_claim(chat_id)

        if not user_claim:
            logger.debug('not cached user_claim')
            try:
                user_claim = await self.account_service.telegram_authentication(telegram_id=chat_id)
                await self._cache_user_claim(chat_id, user_claim)
            except account_interfaces.UserNotFound:
                logger.info(f'user not found with chat id {chat_id}')
                if await Contact.objects.filter(chat_id=chat_id, status=Contact.STATUS_WAITING_FOR_USERNAME).aexists():
                    logger.debug('contact exists and status waiting for username')
                    await self.registration_username(update, context)
                    return
                await self.show_registration_prompt(update, context)
                return
            except Exception as e:
                logger.error(f"Error during authentication: {str(e)}")
                await context.bot.send_message(chat_id=chat_id, text="An error occurred. Please try again.")
                return
        contact = await Contact.objects.aget(chat_id=user_claim.telegram_id)
        if text.startswith("/dismiss"):
            await self.handle_dismiss(update, context, user_claim, contact)
        elif contact.process_uid:
            logger.info(f'process: {contact.process_uid}')
            await self.process_engine(update, context, user_claim, contact.process_uid)

        elif text.startswith("/start"):
            await self.show_welcome_message(update, context, user_claim)
        elif text.startswith("/books") or text.startswith("page_"):
            page = int(text.split("_")[1]) if "page_" in text else 1
            await self.show_book_list(update, context, user_claim, page)
        elif text.startswith("/borrowed_books") or text.startswith("bb-page_"):
            page = int(text.split("_")[1]) if "bb-page_" in text else 1
            await self.show_borrowed_book_list(update, context, user_claim, page)
        elif text.startswith("/offered_books") or text.startswith("ofb-page_"):
            page = int(text.split("_")[1]) if "ofb-page_" in text else 1
            await self.show_offered_books_list(update, context, user_claim, page)
        elif text.startswith("/offer_book"):
            await self.offer_book_process(update, context, user_claim)
        elif text.startswith("show-bb_"):
            borrowed_book_id = text.split("_")[1]
            await self.show_borrowed_book_details(update, context, user_claim, borrowed_book_id)
        elif text.startswith("show-ofb_"):
            offered_book_uid = text.split("_")[1]
            await self.show_offered_book_details(update, context, user_claim, offered_book_uid)
        elif text.startswith("show_"):
            book_title = text.split("_")[1]
            await self.show_book_details(update, context, user_claim, book_title)
        elif text.startswith("borrow_"):
            book_title = text.split("_")[1]
            await self.borrow_book(update, context, user_claim, book_title)
        elif text.startswith("return_"):
            book_title = text.split("_")[1]
            await self.return_book(update, context, user_claim, book_title)
        else:
            await self.handle_unknown(update, context)

        if update.callback_query:
            # Deleting the message associated with the callback query
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=update.callback_query.message.message_id)
                await context.bot.answer_callback_query(update.callback_query.id)
            except Exception as e:
                logger.warning(f"Failed to delete callback query message: {e}")

    async def show_registration_prompt(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        logger.info(f'registration: {chat_id}')
        message = "Welcome for registration, please enter your username."
        await Contact.objects.acreate(chat_id=chat_id)
        await context.bot.send_message(chat_id=chat_id, text=message)

    async def registration_username(self, update: Update, context: CallbackContext):
        try:
            username = update.message.text
            logger.info(f'registration_username: {username}')

            await sync_to_async(self.account_service.register_new_user)(
                account_interfaces.UserInfo(
                    username=username,
                    first_name=update.message.chat.first_name,
                    last_name=update.message.chat.last_name,
                    telegram_id=update.message.chat.id
                )
            )

            contact = await Contact.objects.aget(chat_id=update.message.chat.id)
            contact.username = username
            contact.status = Contact.STATUS_REGISTERED
            await contact.asave()
            message = f'Registration complete welcome {update.message.chat.first_name}'
            await context.bot.send_message(chat_id=update.message.chat_id, text=message)

        except account_interfaces.DuplicatedUserName as e:
            logger.info('duplicated username')
            await context.bot.send_message(chat_id=update.message.chat_id, text=str(e))
        except Exception as e:
            logger.debug(f'exception in get username: {e}')
            await context.bot.send_message(chat_id=update.message.chat_id, text=str(e))
            raise e

    async def show_welcome_message(self, update: Update, context: CallbackContext,
                                   user_claim: account_interfaces.UserClaim,
                                   *args):
        chat_id = update.message.chat_id
        message = f"Welcome back, {user_claim.username}! You can now browse and borrow books.\n {self._command_text}"
        await context.bot.send_message(chat_id=chat_id, text=message)
        await self.show_book_list(update, context, user_claim)

    async def show_book_list(self, update: Update, context: CallbackContext, user_claim: account_interfaces.UserClaim,
                             page: int = 1):
        chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
        logger.info(f"Fetching and showing paginated book list to chat_id: {chat_id}, page: {page}")

        try:
            books_per_page = 7
            all_books = await sync_to_async(
                self.borrowing_book_service.get_books
            )(filters=borrowing_book_interfaces.BookFilter())

            total_pages = ceil(len(all_books) / books_per_page)

            start_index = (page - 1) * books_per_page
            end_index = start_index + books_per_page
            books = all_books[start_index:end_index]

            buttons = [
                [InlineKeyboardButton(book.title, callback_data=f"show_{book.title}")]
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
            await context.bot.send_message(chat_id=chat_id, text="Here are the available books:",
                                           reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error fetching book list: {str(e)}")
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"An error occurred while fetching the book list.: {str(e)}")

    async def show_borrowed_book_list(self, update: Update, context: CallbackContext,
                                      user_claim: account_interfaces.UserClaim,
                                      page: int = 1):
        chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
        logger.info(f"Fetching and showing paginated borrowed book list to chat_id: {chat_id}, page: {page}")

        try:
            books_per_page = 7
            all_bb = await sync_to_async(
                self.borrowing_book_service.get_borrowed_books
            )(filters=borrowing_book_interfaces.BorrowedBookFilter())

            total_pages = ceil(len(all_bb) / books_per_page)

            start_index = (page - 1) * books_per_page
            end_index = start_index + books_per_page
            books = all_bb[start_index:end_index]

            buttons = [
                [InlineKeyboardButton(f"{b_book.book_title} by {b_book.username}",
                                      callback_data=f"show-bb_{b_book.id}")]
                for b_book in books
            ]

            navigation_buttons = []
            if page > 1:
                navigation_buttons.append(InlineKeyboardButton("Previous", callback_data=f"bb-page_{page - 1}"))
            if page < total_pages:
                navigation_buttons.append(InlineKeyboardButton("Next", callback_data=f"bb-page_{page + 1}"))

            if navigation_buttons:
                buttons.append(navigation_buttons)

            reply_markup = InlineKeyboardMarkup(buttons)
            await context.bot.send_message(chat_id=chat_id, text="Here are the borrowed books:",
                                           reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error fetching book list: {str(e)}")
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"An error occurred while fetching the borrowed books list.: {str(e)}")

    async def show_book_details(self, update: Update, context: CallbackContext,
                                user_claim: account_interfaces.UserClaim,
                                book_title: str):
        chat_id = update.callback_query.message.chat.id
        logger.info(f"User {user_claim.username} is viewing details for book {book_title}")

        try:
            book = await sync_to_async(self.borrowing_book_service.get_book_by_title)(book_title)
            message = (f"Title: {book.title}\nWriter: {book.writer}\n"
                       f"Available Quantity: {book.quantity}\nTopic: {book.topic}\npublisher: {book.publisher}"
                       f"\nPublished: {book.date_published}")

            if await sync_to_async(self.borrowing_book_service.has_user_borrowed_book)(user_claim, book_title):
                buttons = [[InlineKeyboardButton("Return", callback_data=f"return_{book.title}")]]
            else:
                buttons = [[InlineKeyboardButton("Borrow", callback_data=f"borrow_{book.title}")]]

            reply_markup = InlineKeyboardMarkup(buttons)
            await context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
        except borrowing_book_interfaces.BookNotFound:
            await context.bot.send_message(chat_id=chat_id, text=f"The selected book: {book_title} was not found.")
        except Exception as e:
            logger.error(f"Error fetching book details: {str(e)}")
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"An error occurred while fetching the book details. : {str(e)}")

    async def show_borrowed_book_details(self, update: Update, context: CallbackContext,
                                         user_claim: account_interfaces.UserClaim,
                                         borrowed_book_id: int):
        chat_id = update.callback_query.message.chat.id
        logger.info(f"User {user_claim.username} is viewing details for borrowed book id {borrowed_book_id}")

        try:
            b_book = await sync_to_async(self.borrowing_book_service.get_borrowed_book_by_id)(borrowed_book_id)
            if b_book.return_at:
                return_at = self.date_time_utils.convert_timestamp_to_date_time(b_book.return_at).get_str_ymd()
            else:
                return_at = "Not Returned Yet!"
            message = (f"Book Title: {b_book.book_title}\nBorrowed By: {b_book.username}\n"
                       f"Borrowed at: {self.date_time_utils.convert_timestamp_to_date_time(b_book.borrowed_at).get_str_ymd()}\n"
                       f"Return at :{return_at}")
            await context.bot.send_message(chat_id=chat_id, text=message)

        except borrowing_book_interfaces.BookNotFound:
            await context.bot.send_message(chat_id=chat_id, text=f"The selected borrowed book id: {id} was not found.")
        except Exception as e:
            logger.error(f"Error fetching book details: {str(e)}")
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"An error occurred while fetching the book details. : {str(e)}")
    
    async def show_offered_book_details(self, update: Update, context: CallbackContext,
                                        user_claim: account_interfaces.UserClaim,
                                        offered_book_uid: str):
        chat_id = update.callback_query.message.chat.id
        logger.info(f"User {user_claim.username} is viewing details for offered book uid {offered_book_uid}")

        try:
            offered_book = await sync_to_async(
                self.offer_book_service.get_offered_book)(caller=user_claim, uid=offered_book_uid)


            message = (
                f'offered book title: {offered_book.offered_book_title}\n'
                f'topic: {offered_book.topic}\n'
                f'author: {offered_book.author}\n'
                f'publisher: {offered_book.publisher}\n'
                f'purchase link: {offered_book.purchase_link}\n'
                f'is purchased: {offered_book.is_purchased}\n'
                f'offered_at: {self.date_time_utils.convert_timestamp_to_date_time(offered_book.offered_at).get_str_ymd()}'
            )
            await context.bot.send_message(chat_id=chat_id, text=message)

        except offer_book_interfaces.OfferedBookNotFound:
            await context.bot.send_message(chat_id=chat_id, text=f"The selected offered book uid: {offered_book_uid} was not found.")
        except Exception as e:
            logger.error(f"Error fetching offered book details: {str(e)}")
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"An error occurred while fetching the offered book details. : {str(e)}")

    async def borrow_book(self, update: Update, context: CallbackContext, user_claim: account_interfaces.UserClaim,
                          book_title: str):
        chat_id = update.callback_query.message.chat_id
        logger.info(f"User {user_claim.username} attempting to borrow book ID: {book_title}")

        try:
            await sync_to_async(self.borrowing_book_service.borrow_book)(
                input_data=borrowing_book_interfaces.BorrowBookInput(
                    username=user_claim.username, book_title=book_title)
            )
            await context.bot.send_message(chat_id=chat_id, text="You have successfully borrowed the book!")
        except borrowing_book_interfaces.BookNotFound:
            await context.bot.send_message(chat_id=chat_id, text="The book was not found.")
        except borrowing_book_interfaces.BookNotAvailableException:
            await context.bot.send_message(chat_id=chat_id, text='The book is not available now.')
        except Exception as e:
            logger.error(f"Error borrowing book: {str(e)}")
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"An error occurred while borrowing the book. : {str(e)}")

    async def return_book(self, update: Update, context: CallbackContext, user_claim: account_interfaces.UserClaim,
                          book_title: str):
        chat_id = update.callback_query.message.chat_id
        logger.info(f"User {user_claim.username} attempting to return book ID: {book_title}")

        try:
            await sync_to_async(self.borrowing_book_service.return_book)(
                input_data=borrowing_book_interfaces.ReturnBookInput(
                    username=user_claim.username, borrowed_book_title=book_title)
            )
            await context.bot.send_message(chat_id=chat_id, text="You have successfully returned the book!")
        except borrowing_book_interfaces.BookNotFound:
            await context.bot.send_message(chat_id=chat_id, text="The book was not found.")
        except Exception as e:
            logger.error(f"Error returning book: {str(e)}")
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"An error occurred while returning the book. {str(e)}")

    async def handle_unknown(self, update: Update, context: CallbackContext, *args):
        chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
        logger.debug(f"Received unknown command from chat_id: {chat_id}")
        commands = (
            "Sorry, I didn't understand that command.\n\n"
            f"{self._command_text}"
        )
        await context.bot.send_message(chat_id=chat_id, text=commands)

    async def handle_dismiss(
            self,
            update: Update,
            context: CallbackContext,
            user_claim: account_interfaces.UserClaim,
            contact: Contact,
            *args
    ):
        contact.process_uid = None
        await contact.asave()
        chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
        logger.debug(f"dismiss the process: {chat_id}")
        commands = (
            "Your process have been dismissed.\n\n"
            f"{self._command_text}"
        )
        await context.bot.send_message(chat_id=chat_id, text=commands)

    async def offer_book_final_step(
            self,
            update: Update,
            context: CallbackContext,
            user_claim: account_interfaces.UserClaim,
            process_uid: str
    ):
        logger.info(f' offer book final step: {process_uid}')
        process = await Process.objects.aget(uid=process_uid)
        fields = Field.objects.filter(process=process)
        offer_book_request = offer_book_interfaces.OfferBookRequest(
            offered_book_title=[field.value async for field in fields if field.name == OFFER_BOOK_TITLE][0],
            topic=[field.value async for field in fields if field.name == TOPIC][0],
            author=[field.value async for field in fields if field.name == WRITER][0],
            publisher=[field.value async for field in fields if field.name == PUBLISHER][0],
            proposer=user_claim.username,
            purchase_link=[field.value async for field in fields if field.name == PURCHASE_LINK][0],
        )
        result = await self.offer_book_service.async_add_offer_book(caller=user_claim, request=offer_book_request)
        message = (
            f'offered book title: {result.offered_book_title}\n'
            f'topic: {result.topic}\n'
            f'author: {result.author}\n'
            f'publisher: {result.publisher}\n'
            f'purchase link: {result.purchase_link}\n'
            f'is purchased: {result.is_purchased}\n'
            f'offered_at: {self.date_time_utils.convert_timestamp_to_date_time(result.offered_at).get_str_ymd()}'
        )
        await context.bot.send_message(chat_id=update.message.chat_id, text=message)
        contact = await Contact.objects.aget(chat_id=user_claim.telegram_id)
        contact.process_uid = None
        await contact.asave()

    async def offer_book_process(self, update, context, user_claim):
        contact = await Contact.objects.aget(chat_id=user_claim.telegram_id)
        process_uid = str(uuid.uuid4())
        contact.process_uid = process_uid
        await contact.asave()
        process = await Process.objects.acreate(
            uid=process_uid,
            type=OFFER_BOOK,
            status=Process.STATUS_INITIATE,
        )
        logger.info(f'process: {process}')
        await self.process_engine(update=update, context=context, user_claim=user_claim, process_uid=process.uid)

    async def show_offered_books_list(
            self,
            update: Update,
            context: CallbackContext,
            user_claim: account_interfaces.UserClaim,
            page: int = 1
    ):
        chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
        logger.info(f"Fetching and showing paginated borrowed book list to chat_id: {chat_id}, page: {page}")

        try:
            objects_per_page = 10
            offer_books = await self.offer_book_service.async_get_offer_books(
                caller=user_claim,
                filters=offer_book_interfaces.OfferBookFilters(
                    limit=objects_per_page,
                    offset=(page - 1) * objects_per_page
                )
            )
            total_pages = ceil(offer_books.count / objects_per_page)
            buttons = [
                [
                    InlineKeyboardButton(
                        f"{offer_book.offered_book_title}-{offer_book.author} by {offer_book.proposer}",
                        callback_data=f"show-ofb_{offer_book.uid}"
                    )
                ]
                for offer_book in offer_books.results
            ]
            navigation_buttons = []
            if page > 1:
                navigation_buttons.append(InlineKeyboardButton("Previous", callback_data=f"ofb-page_{page - 1}"))
            if page < total_pages:
                navigation_buttons.append(InlineKeyboardButton("Next", callback_data=f"ofb-page_{page + 1}"))

            if navigation_buttons:
                buttons.append(navigation_buttons)

            reply_markup = InlineKeyboardMarkup(buttons)
            await context.bot.send_message(
                chat_id=chat_id,
                text="Here are the Offered books:",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error fetching book list: {str(e)}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"An error occurred while fetching the offered books list.: {str(e)}"
            )
            raise e

