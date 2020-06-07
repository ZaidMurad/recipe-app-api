from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient
from .serializers import TagSerializer, IngredientSerializer


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
    serializer_class = TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
