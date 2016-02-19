# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommPreferences',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('badgeCount', models.IntegerField(default=0)),
                ('flags', models.BigIntegerField(default=0)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('identifier', models.CharField(max_length=512)),
                ('urlPath', models.CharField(max_length=1024)),
                ('createTime', models.DateTimeField()),
                ('sku', models.CharField(max_length=256)),
                ('mainImageUrl', models.CharField(null=True, max_length=512)),
                ('altImageUrl', models.CharField(null=True, max_length=512)),
                ('notificationDate', models.DateTimeField(null=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=512)),
                ('host', models.CharField(max_length=256)),
                ('scheme', models.CharField(max_length=64)),
                ('parserClass', models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='store',
            field=models.ForeignKey(to='skate.Store'),
        ),
    ]
