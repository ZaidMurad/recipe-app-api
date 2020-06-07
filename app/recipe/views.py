from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag
from .serializers import TagSerializer


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin, # allows list action
                 mixins.CreateModelMixin): # allows create action (function)
    """Manage tags in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,) # this requires that token authentication is used
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self): # overrides the default method. when the list function is called from a url, it will call this method to retrieve the objects in the queryset variable (all objects), so we need to filter that to limit it to the authenticated user only (without this our test that makes sure that the tags returned are for the authenticated user fails)
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user = self.request.user).order_by('-name')

    def perform_create(self, serializer): # to assign the tag to the authorized user. when we create an object, this function is called and the serializer is passed in
        """Create a new tag"""
        serializer.save(user = self.request.user)
