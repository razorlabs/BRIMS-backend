from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
        Custom user stub in case of future user customization need
        Special thanks to WSVincent (and associated tutorial)
        https://wsvincent.com/django-custom-user-model-tutorial/
    """
    pass
