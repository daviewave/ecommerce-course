from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class AccountManager(BaseUserManager):
    # NOTE: Function to create a user with no special permissions
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email or not username:
            raise ValueError("Accounts must contain an email and a username")

        # NOTE: 'normalize_email' is just making everything lowercase to create consistency in database
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save() # NOTE: this might be deprecated. Course is using django 3.2 -- this is just saving our newly created user into the database
        return user

    # NOTE: Function to create a user with special site access
    def create_superuser(self, first_name, last_name, username, email, password):
        superuser = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name =  last_name,
        )

        # Give the user superuser permissions
        superuser.is_admin = True
        superuser.is_active = True
        superuser.is_staff = True
        superuser.is_superadmin = True
        superuser.save()
        return superuser

class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    username = models.CharField(max_length=50, unique=True, null=True)
    email = models.CharField(max_length=100, unique=True, null=True)
    phone_number = models.CharField(max_length=30, unique=True, null=True)

    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_logged_in = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    # NOTE: This lets the account model know that they will be using/inheriting the Account Models to instantiate user and superuser accounts
    objects = AccountManager()

    # NOTE: This causes the top field on the django login page to prompt for email instead of username
    def __str__(self):
        return self.email

    # django required methods
    def has_perm(self, permission, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True
