from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from . import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin): # allows list & create actions (functions)
    """Base Viewset for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,) # this requires that token authentication is used

    def get_queryset(self): # to filter objects by user currently authenticated. it overrides the default method. when the list function is called from a url, it will call this method to retrieve the objects in the queryset variable (all objects), so we need to filter that to limit it to the authenticated user only (without this our test that makes sure that the tags returned are for the authenticated user only fails)
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user = self.request.user).order_by('-name')

    def perform_create(self, serializer): # to assign the tag to the authorized user. when we create an object, this function is called and the serializer is passed in
        """Create a new object for the authenticated user"""
        serializer.save(user = self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet): # we used modelviewset because we want to use all functionality (not just list and create)
    """Manage recipes in the database"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the recipe for the authenticated user only"""
        return self.queryset.filter(user = self.request.user)

    def get_serializer_class(self): # This is the function thats called to retrieve the serializer class for a request. we override it to change the serializer class for the different actions available in the viewset
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class
