from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# NOTE: Model to create a user with no special permissions
class AccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError("Accounts must contain an email associated")
        
        if not email or not username:
            raise ValueError("Accounts must contain an username associated")

        # NOTE: 'normalize_email'is a lowercase method
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self.db)
        return user

    # NOTE: Model to create a user with special site access
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
        superuser.save(using=self.db)
        return superuser

class Account(AbstractBaseUser):
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    username        = models.CharField(max_length=50, unique=True)
    email           = models.CharField(max_length=100, unique=True)
    phone_number    = models.CharField(max_length=30, unique=True, null=True)

    # required
    date_joined     = models.DateTimeField(auto_now_add=True)
    last_logged_in  = models.DateTimeField(auto_now_add=True)
    is_admin        = models.BooleanField(default=False)
    is_staff        = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=False)
    is_superadmin   = models.BooleanField(default=False)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    # NOTE: This lets the account model know that they will be using/inheriting the Account Models to instantiate user and superuser accounts
    objects = AccountManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'


    # NOTE: This causes the top field on the django login page to prompt for email instead of username
    def __str__(self):
        return self.email

    # django required methods
    def has_perm(self, permission, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True


class UserProfile(models.Model):
    user                = models.OneToOneField(Account, on_delete=models.CASCADE)
    addr_1              = models.CharField(max_length=100, blank=True)
    addr_2              = models.CharField(max_length=100, blank=True)
    city                = models.CharField(max_length=20, blank=True)
    state               = models.CharField(max_length=20, blank=True)
    zip_code            = models.CharField(max_length=6, blank=True)
    country             = models.CharField(max_length=50, blank=True)
    profile_picture     = models.ImageField(upload_to='userprofile', blank=True)

    def __str__(self):
        return self.user.first_name

    def full_address(self):
        return f'{self.addr_1}, {self.city}, {self.state}, {self.country}'