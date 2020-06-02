from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin


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
