from unittest.mock import patch # we used this in test_commands file too

from django.test import TestCase
from django.contrib.auth import get_user_model # u can import the user model directly from the models but thats not recommended because that might change, so its better to get it from the settings file directly

from core import models

def sample_user(email = 'test@gmail.com', password = '123456'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)

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

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user = sample_user(),
            name = 'Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user = sample_user(),
            name = 'Cucumber',
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the recipe creation and string representation"""
        recipe = models.Recipe.objects.create(
            user = sample_user(),
            title = 'Steak and mushroom sauce',
            time_minutes = 5,
            price = 5.00,
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4') # the argument is the function we wanna mock.
    def test_recipe_file_name_uuid(self, mock_uuid): # the second argument is sent by the patch decorator
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid' # set the uuid to a fixed string
        mock_uuid.return_value = uuid # any time we call uuid4 function in our tests, it will override the default behaviour and return our string instead
        file_path = models.recipe_image_file_path(None, 'myimage.jpg') # we dont need to provide the instance(1st arg) here so we just pass None, the second argument is the file name for the original file being added (uploaded by user)

        expected_path = f'uploads/recipe/{uuid}.jpg' # uuid.jpg is the new name assigned to the file after its uploaded
        self.assertEqual(file_path, expected_path)
