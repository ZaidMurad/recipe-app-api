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


def sample_recipe(user, **params): # the ** means that any extra key-word arguments passed in other than user will be passed into a dict called params
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00,
    }
    defaults.update(params) # update here is a method for dicts that accepts a dictionary object. any parameter passed in will override the defaults if it exists, or will be added if it does not exist

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
        serializer = RecipeSerializer(recipes, many=True) # many=true returns the data as a list

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
        recipe.tags.add(sample_tag(user=self.user)) # This is how u add an item on a ManytoManyField
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe) # since this is not a list function, we dont need many=true
        self.assertEqual(res.data, serializer.data) # test that the response is serialized

    def test_create_basic_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'Chocolate Cheesecake',
            'time_minutes': 30,
            'price': 5.00
        } # minimum fields requried
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id']) # retrive the recipe created in the API from our db(models) by specifying its own id

        for key in payload.keys(): # loop through each key in the dict
            self.assertEqual(payload[key], getattr(recipe, key)) # getattr allows you to retrieve an attribute from an object by passing in a variable. you cannot just use recipe.key wince that will search for a key called 'key' in recipe

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name = 'Vegan')
        tag2 = sample_tag(user=self.user, name = 'Dessert')
        payload = {
            'title': 'Avocado lime Cheesecake',
            'tags': [tag1.id, tag2.id], # this is how tags are assigned
            'time_minutes': 20,
            'price': 20.00,
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name = 'bla')
        ingredient2 = sample_ingredient(user=self.user, name = 'blaa')
        payload = {
            'title': 'red curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 30,
            'price': 30.00
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name = 'Curry')

        payload = {'title': 'Chicken tikka', 'tags': [new_tag.id]}
        url = detail_url(recipe.id) # to update an object you have to use the detail endpoint(with the pk of the specific recipe)
        self.client.patch(url, payload)

        recipe.refresh_from_db() # we always need this when we update an object
        self.assertEqual(recipe.title, payload['title'])

        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Spaghetti',
            'time_minutes': 25,
            'price': 5.00,
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
