from django.test import TestCase
from ..models import User
from .. import interfaces
from ..services import AccountService
from unittest.mock import patch


class TestAccountService(TestCase):
    def setUp(self):
        self.service = AccountService()

    def test_register_new_user_success(self):
        user_info = interfaces.UserInfo(
            username="newuser",
            email="newuser@example.com",
            telegram_id="123456789",
            first_name="New",
            last_name="User",
            mobile="555-5555"
        )

        self.service.register_new_user(user_info)

        user = User.objects.get(username="newuser")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "newuser@example.com")
        self.assertEqual(user.telegram_id, "123456789")

    def test_register_new_user_duplicate_telegram_id(self):
        User.objects.create(
            username="existinguser",
            email="existinguser@example.com",
            telegram_id="123456789"
        )

        user_info = interfaces.UserInfo(
            username="newuser",
            email="newuser@example.com",
            telegram_id="123456789",  # duplicate telegram_id
            first_name="New",
            last_name="User",
            mobile="555-5555"
        )

        with self.assertRaises(interfaces.DuplicatedTelegramId):
            self.service.register_new_user(user_info)

    def test_register_new_user_duplicate_username(self):
        # Create an existing user with a specific username
        User.objects.create(
            username="existinguser",
            email="existinguser@example.com",
            telegram_id="987654321"
        )

        user_info = interfaces.UserInfo(
            username="existinguser",  # duplicate username
            email="newuser@example.com",
            telegram_id="123456789",
            first_name="New",
            last_name="User",
            mobile="555-5555"
        )

        with self.assertRaises(interfaces.DuplicatedUserName):
            self.service.register_new_user(user_info)

    def test_telegram_authentication_success(self):
        # Create a user to authenticate
        User.objects.create(
            username="authuser",
            email="authuser@example.com",
            telegram_id="auth123"
        )

        result = self.service.telegram_authentication("auth123")

        self.assertIsNotNone(result)
        self.assertEqual(result.username, "authuser")
        self.assertEqual(result.telegram_id, "auth123")

    def test_telegram_authentication_failure(self):
        with self.assertRaises(interfaces.UserNotFound):
            self.service.telegram_authentication("nonexistent")

    def test_register_new_user_with_no_telegram_id(self):
        user_info = interfaces.UserInfo(
            username="newuser",
            email="newuser@example.com",
            first_name="New",
            last_name="User",
            mobile="555-5555"
        )

        self.service.register_new_user(user_info)

        user = User.objects.get(username="newuser")
        self.assertIsNotNone(user)
        self.assertIsNone(user.telegram_id)

    def test_telegram_authentication_with_none_telegram_id(self):
        with self.assertRaises(interfaces.UserNotFound):
            self.service.telegram_authentication(None)

    @patch('interfaces.AbstractAccountService._convert_user_to_user_info')
    def test_register_new_user_calls_conversion_method(self, mock_convert_user_to_user_info):
        user_info = interfaces.UserInfo(
            username="newuser",
            email="newuser@example.com",
            telegram_id="123456789",
            first_name="New",
            last_name="User",
            mobile="555-5555"
        )

        self.service.register_new_user(user_info)

        # Ensure the conversion method was called
        mock_convert_user_to_user_info.assert_called_once()
