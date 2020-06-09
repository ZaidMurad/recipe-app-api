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
    # define them as special fields
    ingredients = serializers.PrimaryKeyRelatedField(
        many = True, # allow many ingredients
        queryset = Ingredient.objects.all(),
    ) # this lists the ingredients with their IDs(pk) (without names) only since we used (PrimaryKeyRelatedField)
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


class RecipeDetailSerializer(RecipeSerializer): # re-use the RecipeSerializer overriding tags and ingredients
    """Serialize a recipe detail"""
    ingredients = IngredientSerializer(many=True, read_only=True) # many=True means that we can have more than 1 ingredient for a recipe
    tags = TagSerializer(many=True, read_only=True)
    # here we are using serializers as fields (nested relationships) which will
    # allow us to access all the fields of that serializer for detailed view


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes"""

    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)
