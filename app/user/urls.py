from django.urls import path
from . import views

app_name = 'user' # set to identify which app we are creating the url from when we use the reverse function in the tests

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name = 'create'), # the name is used to identify for the reverse function in tests
    path('token/', views.CreateTokenView.as_view(), name = 'token'),
]
