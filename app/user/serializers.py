from django.contrib.auth import get_user_model, authenticate # a django helper command to work with django authentication system to authenticate a request
from django.utils.translation import ugettext_lazy as _ # we explained something like this before, used for apis that support multiple languages
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer): # since we are basing our serializer on an existing model, ModelSerializer is much better
    """Serializers for the users object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name') # the fields we want to be accessable in the api
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data): # from DRF docs to override the create fn. we do this to ensure the password stored is encrypted
        """create a new user with encrypted password and return it"""

        return get_user_model().objects.create_user(**validated_data) # validated data is a dict so here we unwind it

    def update(self, instance, validated_data): # instance is the model(user model) instance.
        """Update a user setting the password correctly and return it"""
        password = validated_data.pop('password', None) # None is a default value.
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
        

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style = {'input_type': 'password'},
        trim_whitespace = False # since by default the DRF serializer trims off whitespace
    )

    def validate(self, attrs): # this function is called when we validate our serializer's inputs and authentication credentials, we have to override it to accept email instead of username.
        """Validate and authenticate the user""" #  attrs is just every field that makes up our serializer, and gets passed into the validate function as a dict
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request = self.context.get('request'), # to access the context of the request you have made
            username = email,  # since username is the name of the parameter required for authentication
            password = password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code = 'authentication')

        attrs['user'] = user
        return attrs
