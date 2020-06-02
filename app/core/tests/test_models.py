from django.test import TestCase
from django.contrib.auth import get_user_model # u can import the user model directly from the models but thats not recommended because that might change, so its better to get it from the settings file directly


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@gmail.com'
        password = '123456'
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password)) # it has to be done this way because passwords are encrypted. check_password is a helper function that comes with django user model

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@GMAIL.com'
        user = get_user_model().objects.create_user(email, '123456')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError): # anything that we run under this should raise a value error since we did not provide an email, if it does not, the test fails
            get_user_model().objects.create_user(None, '123456')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@gmail.com',
            '123456'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
