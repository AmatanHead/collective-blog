# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-04-24 13:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collective_blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='created',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
    ]