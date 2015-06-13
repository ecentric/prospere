from django.db import models
from django.contrib.auth.models import User

class SessionBonds(models.Model):

    user = models.ForeignKey(User, unique=True)
    session_key = models.CharField(max_length=40)

