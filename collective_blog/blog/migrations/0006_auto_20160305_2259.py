# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-05 19:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0005_auto_20160305_2238'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.SmallIntegerField(choices=[(1, '+1'), (-1, '-1')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-created',), 'verbose_name': 'Post', 'verbose_name_plural': 'Posts'},
        ),
        migrations.AlterField(
            model_name='post',
            name='created',
            field=models.DateTimeField(blank=True, editable=False),
        ),
        migrations.AddField(
            model_name='postvote',
            name='object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='blog.Post'),
        ),
        migrations.AddField(
            model_name='postvote',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes_for_blog_postvote', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='postvote',
            unique_together=set([('user', 'object')]),
        ),
    ]