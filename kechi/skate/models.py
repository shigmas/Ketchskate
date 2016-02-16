from django.db import models

from django.contrib.auth.models import User

# Create your models here.

class Store(models.Model):
    name = models.CharField(max_length=512)
    host = models.CharField(max_length=256)
    parserClass = models.CharField(max_length=256)

class Item(models.Model):
    identifier = models.CharField(max_length=512)
    urlPath = models.CharField(max_length=1024)
    createTime = models.DateTimeField()
    creator = models.ForeignKey(User)
    store = models.ForeignKey(Store)
    sku = models.CharField(max_length=256)

class CommPreferences(models.Model):
    user = models.OneToOneField(User)
    # If this goes over the max... well, there's a bug somewhere
    badgeCount = models.IntegerField(default=0)
    # technically, this doesn't work in sqlite... But it seems like it does.
    # or at least, compiles.
    flags = models.BigIntegerField(default=0)
