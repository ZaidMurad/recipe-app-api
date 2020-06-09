import uuid # used to create the name to uniquely identify the image that we assign to the image field
import os # used to create a valid path for our file destination
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings


def recipe_image_file_path(instance, file_name): # A function to create the path to the image on our system, and generate the name for the image on the system after its uploaded
    """generate file path for new recipe image""" # instance is the instance that is creating the path, file_name is the name of the original file uploaded
    ext = file_name.split('.')[-1] # [-1] means return the last item of the list. here we want to extract the file extension (jpg)
    filename = f'{uuid.uuid4()}.{ext}' # you can call functions in f strings

    return os.path.join('uploads/recipe/', filename) # this allows you to join to strings to make a valid path, if the path is invalid it will return an error


class UserManager(BaseUserManager):

    def create_user(self, email, password = None, **extra_fields): # password is set to none in case you want to create a user with no pass(not active), the last argument allows to take any extra fields passed in and put them in extra_fields
        """Create and save a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields) # self.model is to access the model that this manager is designed for
        user.set_password(password)
        user.save() # the text inside parenthesis (using=._db) is required for supporting multiple databases (not required here)

        return user

    def create_superuser(self, email, password): # used when creating users from the command line
        """Create and save a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save() # (using=._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique = True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default = True)
    is_staff = models.BooleanField(default = False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Tag to be used for recipes"""
    name = models.CharField(max_length = 255) # 255 is the maximum possible
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )

    def __str__(self):
        """returns the string representation"""
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used in a recipe"""
    name = models.CharField(max_length = 255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)# the recommended strategy to make it optional is blank=True (if no link is provided set it to blank string). the user can add a link to the recipe optionally
    ingredients = models.ManyToManyField('Ingredient') # A type of foreign keys
    tags = models.ManyToManyField('Tag') # without the quotes around model name(tag), the models should be defined in correct order. So we put them to ignore this issue
    image = models.ImageField(null=True, upload_to = recipe_image_file_path) # null=true to make this field optional. in the 2nd arg, we dont wanna call the function but to pass a reference to it to be called everytime we upload
    # ImageField validates by default that the uploaded object is a valid image
    def __str__(self):
        return self.title
