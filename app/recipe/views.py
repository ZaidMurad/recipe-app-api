from rest_framework.decorators import action # used to add custom actions to viewsets
from rest_framework.response import Response

from rest_framework import viewsets, mixins, status
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
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0)) # if assigned_only does not return a value, it will be None, which cannot be converted to int, so we need to set a default value for it
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull = False) # this will add a filter to eliminate tag/ingredients not assigned to recipes. but if there is duplicates (same tag assigned to two recipes) it will return it twice, so we used distinct() function at the end
        return queryset.filter(
            user = self.request.user
        ).order_by('-name').distinct() # make sure that the queryset returned is unique

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

    def _params_to_ints(self, qs): # _ before the name of the function is a common convention for functions intended to be private (we can but wont use it outside this class)
        """Convert a string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')] # '1,2,3' to ['1','2','3'] to [1,2,3]

    def get_queryset(self):
        """Retrieve the recipe for the authenticated user only"""
        tags = self.request.query_params.get('tags') # if we have provided tags as a query string it will be assigned to tags variable, if not this will return None. query_params is a method for request object, which is a dictionary containing all of the query params provided in the request(check tests requests for ref)
        ingredients = self.request.query_params.get('ingredients') # request.query_params is similar to request.GET but is better to be used
        queryset = self.queryset #we create this variable to apply the filters to it and return it
        if tags:
            tag_ids = self._params_to_ints(tags) # convert to list of ids
            queryset = queryset.filter(tags__id__in=tag_ids) # django syntax for filtering on foreign key objects. so we have tags field in our recipe queryset, which has a foreinkey to the tags table which has an id, so if u wanna filter by the id in the remote table(Tag) u use '__id'. then 2 more underscores to apply the function 'in'
        if ingredients:
            ing_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ing_ids)

        return queryset.filter(user = self.request.user)

    def get_serializer_class(self): # This is the function thats called to retrieve the serializer class for a request. we override it to change the serializer class for the different actions available in the viewset
        """Return appropriate serializer class"""
        if self.action == 'retrieve': # retrieve represents detailed view
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer): # assigns the user for the recipe to the current authenticated user
        """Create a new recipe for the authenticated user"""
        serializer.save(user = self.request.user)

    # the above methods are all default methods that we are overriding, unlike the custom action we define below
    @action(methods = ['POST'], detail = True, url_path = 'upload-image') # detail=true is used to make the action intended for a single object(true) or a collection(false). so here we need to use the pk in url for detailed view
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object() # retrieve the recipe object being accessed based on the id(pk)
        serializer = self.get_serializer( # this is a helper function that calls get_serializer_class function within its code and return a serializer instance. we can put the serializer directly here but this is not the recommended way
            recipe, # object we are updating to upload the image to it
            data = request.data, # data posted to the endpoint
        )

        if serializer.is_valid(): # validates the data to make sure the image field is correct and no other fields to be provided
            serializer.save() # allowed by ModelSerializers
            return Response(
                serializer.data, # return our image
                status = status.HTTP_200_OK,
            )

        return Response( # if serializer is invalid
            serializer.errors, # return the occured errors
            status = status.HTTP_400_BAD_REQUEST,
        )
