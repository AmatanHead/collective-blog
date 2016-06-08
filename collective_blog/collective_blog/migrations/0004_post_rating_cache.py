# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-06-08 16:14
from __future__ import unicode_literals

import collective_blog.models.post
from django.db import migrations
import s_voting.models


class Migration(migrations.Migration):

    dependencies = [
        ('collective_blog', '0003_auto_20160606_1932'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='rating_cache',
            field=s_voting.models.VoteCacheField(default=0, query=s_voting.models._default_cache_query, vote_model=collective_blog.models.post.PostVote),
        ),
    ]
