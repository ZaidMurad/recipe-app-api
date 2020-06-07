# from django.shortcuts import render
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView): # CreateApiView is used for create-only endpoints (pre-defined view for this particular case)
    """Creates a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken): # used to generate the auth token
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES # this sets the renderer so we can view this endpoint in the browser with the browsable api


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,) # to specify the level of access the user has. here the user must be authenticated to use the API

    def get_object(self): # used to get the model for the authenticated (loggen in) user. we are overriding the default method which return the object that the view is displaying
        """Retrieve and return the authenticated user"""
        return self.request.user # the authentication class (in authentication_classes variable) takes care of assigning the user to the request
