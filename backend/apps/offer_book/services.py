import uuid
from logging import Logger

from utils.date_time import interfaces as date_time_utils_interfaces
from apps.account import interfaces as account_interfaces
from . import interfaces
from .models import OfferBook

logger = Logger(__name__)


class OfferBookService(interfaces.AbstractOfferBookService):

    def __init__(
            self,
            date_time_service: date_time_utils_interfaces.AbstractDateTimeUtils
    ):
        self.date_time_service = date_time_service

    def get_offer_books(
            self,
            caller: account_interfaces.UserClaim,
            filters: interfaces.OfferBookFilters
    ) -> interfaces.OfferBookList:
        logger.info(f'caller: {caller}, filters: {filters}')
        queryset = OfferBook.objects.filter(**filters.as_dict()).order_by(filters.order_by)
        count = queryset.count()
        queryset = queryset[filters.offset:filters.offset + filters.limit]
        deposit_results = interfaces.OfferBookList(
            count=count,
            results=[self._convert_offer_book_to_dataclass(offer_book=offer_book) for offer_book in queryset]
        )
        logger.info(f'deposit_results: {deposit_results}')
        return deposit_results

    def add_offer_book(
            self,
            caller: account_interfaces.UserClaim,
            request: interfaces.OfferBookRequest
    ) -> interfaces.OfferBookInfo:
        logger.info(f'caller: {caller}, request: {request}')
        offer_book = OfferBook.objects.create(
            uid=str(uuid.uuid4()),
            offered_book_title=request.offered_book_title,
            topic=request.topic,
            author=request.author,
            publisher=request.publisher,
            proposer=request.proposer,
            purchase_link=request.purchase_link,
            offered_at=self.date_time_service.get_current_timestamp()
        )
        offer_book_dc = self._convert_offer_book_to_dataclass(offer_book)
        logger.info(f'offered book: {offer_book_dc}')
        return offer_book_dc

    def declare_purchase_book(self, caller: account_interfaces.UserClaim, offered_book_title, quantity):
        logger.info(f'caller: {caller}, offer_book_title: {offered_book_title}, quantity: {quantity}')
        raise NotImplementedError  # TODO: compelete this function and add it to bot

    @staticmethod
    def _convert_offer_book_to_dataclass(offer_book: OfferBook) -> interfaces.OfferBookInfo:
        return interfaces.OfferBookInfo(
            uid = offer_book.uid,
            offered_book_title=offer_book.offered_book_title,
            topic=offer_book.topic,
            author=offer_book.author,
            publisher=offer_book.publisher,
            proposer=offer_book.proposer,
            purchase_link=offer_book.purchase_link,
            is_purchased=offer_book.is_purchased,
            offered_at=offer_book.offered_at,
        )
