import logging
from .models import User
from . import interfaces
logger = logging.getLogger(__name__)


class AccountService(interfaces.AbstractAccountService):
    def register_new_user(self, user: interfaces.UserInfo):
        logger.info(f'user: {user}')
        if user.telegram_id:
            if User.objects.filter(telegram_id=user.telegram_id).exists():
                logger.info(f"Telegram ID {user.telegram_id} is already in use.")
                raise interfaces.DuplicatedTelegramId(f"Telegram ID {user.telegram_id} is already in use.")

        if User.objects.filter(username=user.username).exists():
            logger.info(f"Username {user.username} is already taken.")
            raise interfaces.DuplicatedUserName(f"Username {user.username} is already taken.")

        new_user = User(
            username=user.username,
            email=user.email,
            telegram_id=user.telegram_id,
            first_name=user.first_name,
            last_name=user.last_name,
            mobile=user.mobile,
            is_active=True,
            is_staff=False
        )
        new_user.save()
        result = self._convert_user_to_user_info(new_user)
        logger.info(f'result: {result}')

    async def telegram_authentication(self, telegram_id) -> interfaces.UserClaim:
        logger.info(f"telegram_id: {telegram_id}")
        try:
            account = await User.objects.aget(telegram_id=telegram_id)
            result = interfaces.UserClaim(username= account.username, telegram_id=account.telegram_id)
            logger.info(f'result: {result}')
            return result
        except User.DoesNotExist:
            logger.info(f"No user found with Telegram ID {telegram_id}")
            raise interfaces.UserNotFound(f"No user found with Telegram ID {telegram_id}")


    # def get_user_by_username(self, username) -> interfaces.UserClaim:
    #     try:
    #         account = User.objects.get(username=username)
    #         return interfaces.UserClaim(username=account.username, telegram_id=account.telegram_id)
    #     except ObjectDoesNotExist:
    #         raise interfaces.UserNotFound(f"No user found with username {username}")

    @staticmethod
    def _convert_user_to_user_info(user: User) -> interfaces.UserInfo:
        return interfaces.UserInfo(
            username=user.username,
            email=user.email,
            password=user.password,
            telegram_id=user.telegram_id,
            first_name=user.first_name,
            last_name=user.last_name,
            mobile=user.mobile,
        )
