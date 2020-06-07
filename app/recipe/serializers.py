from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient objects"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects"""
    # since ingredients and tags are references to other models, we have to
    # define them as special keys
    ingredients = serializers.PrimaryKeyRelatedField(
        many = True, # allow many ingredient
        queryset = Ingredient.objects.all(),
    ) # this lists the ingredients with their IDs
    tags = serializers.PrimaryKeyRelatedField(
        many = True,
        queryset = Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'title', 'ingredients', 'tags', 'time_minutes',
            'price', 'link',
        )
        read_only_fields = ('id',)
