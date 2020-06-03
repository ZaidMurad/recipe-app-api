from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse # allows us to to generate urls for django admin page
from django.test import Client # allows us to make tests requests to our application in our unit tests


class AdminSiteTests(TestCase):

    def setUp(self): # a setup function runs before every test to do some setup tasks that need to be done
        self.client = Client() # creating our test client. a python class that acts as a dummy web browser
        self.admin_user = get_user_model().objects.create_superuser(
            email = 'admin@gmail.com',
            password = '123456',
        )
        self.client.force_login(self.admin_user) # To log the user into our client
        self.user = get_user_model().objects.create_user(
            email = 'test@gmail.com',
            password = '123456',
            name = 'Test Name',
        ) # create a user that is not authenticated to list in the admin page

    def test_users_listed(self):
        """Test that users are listed on user page"""
        url = reverse('admin:core_user_changelist') # ('app you are going for: the url you want') This will generate the url for our list user page. The reason we use this instead of writing the url manually is to account for any change of urls in the future
        res = self.client.get(url) # this will use our test client to to perform HTTP GET on the url above

        self.assertContains(res, self.user.name) # asserts that the response(res) contains a specific item
        self.assertContains(res, self.user.email) # it also checks that the HTTP response is 200

    def test_user_change_page(self):
        """Test that the user edit page works"""
        url = reverse('admin:core_user_change', args = [self.user.id]) # it will generate a url like: /admin/core/user/userID
        res = self.client.get(url) # res = response

        self.assertEqual(res.status_code, 200) # test that the page renders OK (HTTP 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
