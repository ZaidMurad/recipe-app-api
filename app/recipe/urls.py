from django.urls import path, include
from rest_framework.routers import DefaultRouter # a feature from DRF that automatically generates urls for viewsets (for all actions in the viewset)

from . import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)

app_name = 'recipe' # for the reverse function in tests

urlpatterns = [
    path('', include(router.urls)), # pass all the requests to the router
]
