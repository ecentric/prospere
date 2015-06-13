#coding: utf-8 
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Notifications(models.Model):
    user = models.ForeignKey(User)

    username = models.CharField(max_length = 30)
    choices = (
        ('AD', 'новый файл'),
        ('AC', 'сообщение'),
    )
    action = models.CharField(max_length = 2, choices = choices)
    creation_date = models.DateTimeField(auto_now_add = True)

    content_type =  models.ForeignKey(ContentType)
    object_pk      = models.BigIntegerField()
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")

