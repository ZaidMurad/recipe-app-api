from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list') # -list is included here since we are using a viewset (not APIView) which uses a router that automatically appends the action name to the url


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized tags api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'Test@gmail.com',
            '123456'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user = self.user, name = 'Vegan') # sample tag 1
        Tag.objects.create(user = self.user, name = 'Dessert') # sample tag 2

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name') # This makes a query to return all the tags. - means in reverse alphabitical order based on name
        serializer = TagSerializer(tags, many=True) # Here we serialize our tag objects. Since there is more than one item in our serializer, we have to put many=True

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            email = 'Test2@gmail.com',
            password = '123456',
        )
        Tag.objects.create(user = user2, name = 'Fruity')
        tag = Tag.objects.create(user = self.user, name = 'Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Test Tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user = self.user, # only the authenticated user
            name = payload['name'] # # only the tag created above
        ).exists() # returns true or false

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='lunch')
        recipe = Recipe.objects.create(
            user=self.user,
            title='eggs on toast',
            time_minutes=20,
            price=20.00,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1}) # assigned only is the name of our filter, if you assign it to 1, it will evaluate to True, and it will filter by tags/ingredients assigned to recipes only

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self): # if we have two recipes with same tag assigned to both of them, test that the tag is returned once only
        """Test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(user=self.user, name = 'ba7')
        Tag.objects.create(user=self.user, name = 'lunch') # we add this so that we have more than one tag for our test to make sense
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='whatever',
            time_minutes = 50,
            price = 10.00,
        )
        recipe2 = Recipe.objects.create(
            user=self.user,
            title='another recipe',
            time_minutes = 40,
            price = 5.00,
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1}) # assigned only is the name of our filter, if you assign it to 1, it will evaluate to True, and it will filter by tags/ingredients assigned only

        self.assertEqual(len(res.data), 1)
