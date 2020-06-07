from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list') # /api/recipe/recipes


def detail_url(recipe_id): # /api/recipe/recipes/ID
    """Return recipe detail url"""
    return reverse('recipe:recipe-detail', args = [recipe_id])


def sample_tag(user, name = 'Main Course'): # no need to use **params here since we have only 2 arguments
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name = 'Cinnamon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)

def sample_recipe(user, **params): # the ** means that any extra arguments passed in other than user will be passed into a dict called params
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00,
    }
    defaults.update(params) # update here accepts a dictionary object. any parameter passed in will override the defaults if it exists, or will be added if it does not exist

    return Recipe.objects.create(user=user, **defaults) # this will do the opposite and unwind the dictionary into the arguments


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe Api access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email = 'test@gmail.com',
            password = '123456',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        sample_recipe(user = self.user)
        sample_recipe(user = self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for authenticated user"""
        user2 = get_user_model().objects.create_user(
            email = 'test2@gmail.com',
            password = '123465',
        )
        sample_recipe(user = user2)
        sample_recipe(user = self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True) # although we only have one recipe for this user, we still pass many=true since even if there is one object returned, the list api should always return a data type of list

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test Viewing a recipe detail"""
        recipe = sample_recipe(user = self.user)
        recipe.tags.add(sample_tag(user=self.user)) # This is how u add an item on a ManytoMany field
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe) # since this is not a list function, we dont need many=true
        self.assertEqual(res.data, serializer.data) # test that the response is serialized
