from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse # to generate our api urls

from rest_framework.test import APIClient # test client used to make requests to our api and get the response
from rest_framework import status # to generate status codes

CREATE_USER_URL = reverse('user:create') # since we will use it a lot. this will create the user create url
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me') # the account of the user whos authenticated

def create_user(**params): # (**params) is a dynamic list of args, it can take as much args as we want, which are passed directly to create_user model so we have a lot of flexibility
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase): # a public API is one thats unauthenticated (such as an API to create a user)
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload successful"""
        payload = { # the object that you pass to the api when you make the request
            'email': 'test@gmail.com',
            'password': '123456',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload) # HTTP post request to our client

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data) # it will take the dict response and pass it in to see if it gets the user successfully
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data) # we dont want the pass to be returned in the request since it will be a security vunerability

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            'email': 'test@gmail.com',
            'password': '123456',
            'name': 'Test Name'
        }
        create_user(**payload) # unwind the payload argument using ** (similar to passing the email and password and name to the function) then create the user
        res = self.client.post(CREATE_USER_URL, payload) # since the we already created the user this should fail

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'pw',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email = payload['email']
        ).exists() # if the user does not exist this will be false
        self.assertFalse(user_exists)

    ###########################################################################
    # since to generate a token u dont need to be authenticated, we do it here
    ###########################################################################

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email': 'testie@gmail.com',
            'password': 'TestPass',
        }
        create_user(**payload) # we have to create a user before generating a token for it
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data) # test that there is a key called token
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials given"""
        create_user( email = 'test@gmail.com', password = '123456')
        payload = { 'email': 'test@gmail.com', 'password': 'wrongpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user does not exist"""
        payload = { 'email': 'test@gmail.com', 'password': '123456'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    ###########################################################################

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email = 'test@gmail.com',
            password = '123456',
            name = 'Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user) # used to authenticate any request that our client make with our sample user

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        }) # we dont want the pass to be returned even if its hashed

    def test_post_me_not_allowed(self):
        """Test that post is not allowed on the me url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'passywordy'} # anything different from the user created in the setup method
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db() # used to update the user with the latest values from db
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
