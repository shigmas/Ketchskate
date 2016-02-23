from django.db import models

from django.contrib.auth.models import User

# Create your models here.

class Store(models.Model):
    name = models.CharField(max_length=512)
    host = models.CharField(max_length=256)
    scheme = models.CharField(max_length=64)
    parserClass = models.CharField(max_length=256)

    def __str__(self):
        # This is the only one where we go through the admin interface, so
        # we need to implement this
        return '%s: (%s://%s)' % (self.name, self.scheme, self.host)

class Item(models.Model):
    identifier = models.CharField(max_length=512)
    urlPath = models.CharField(max_length=1024)
    createTime = models.DateTimeField()
    creator = models.ForeignKey(User)
    store = models.ForeignKey(Store)
    sku = models.CharField(max_length=256)
    # On creation, we need a main URL, but for legacy, it's null right now.
    # alt may be null
    mainImageUrl = models.CharField(max_length=512, null=True)
    altImageUrl = models.CharField(max_length=512, null=True)
    # This will be set when we alert the user. (If the user has continuous
    # notifications turned on, we will continue to send the notifications, even
    # if this is set
    notificationDate = models.DateTimeField(null=True)

    def __str__(self):
        return '%s (%s)' % (self.identifier, self.store.name)


class CommPreferences(models.Model):
    user = models.OneToOneField(User)
    # If this goes over the max... well, there's a bug somewhere
    badgeCount = models.IntegerField(default=0)
    # technically, this doesn't work in sqlite... But it seems like it does.
    # or at least, compiles.
    flags = models.BigIntegerField(default=0)
