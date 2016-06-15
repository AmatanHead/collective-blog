# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-06-15 16:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import s_markdown.datatype
import s_markdown.extensions.autolink
import s_markdown.extensions.automail
import s_markdown.extensions.comment
import s_markdown.extensions.escape
import s_markdown.extensions.fenced_code
import s_markdown.extensions.semi_sane_lists
import s_markdown.extensions.strikethrough
import s_markdown.models
import s_markdown.renderer
import s_voting.models
import user.models.karma


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Karma',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.SmallIntegerField(choices=[(1, '+1'), (-1, '-1')])),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='karma', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes_for_user_karma', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(blank=True, max_length=100, verbose_name='Location')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='Birthday')),
                ('about', s_markdown.models.MarkdownField(blank=True, cls_name='about_cls', default=s_markdown.datatype.Markdown(html='', renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.comment.CommentExtension()]), source=''), help_text='Tell us about yourself (use the markdown, Luke!)', markdown=s_markdown.datatype.Markdown, renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.comment.CommentExtension()]), renderer_name='about_renderer', state_name='_about_state', verbose_name='About')),
                ('_about_html', s_markdown.models.HtmlCacheField(blank=True, editable=False, markdown_field=s_markdown.models.MarkdownField(blank=True, cls_name='about_cls', default=s_markdown.datatype.Markdown(html='', renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.comment.CommentExtension()]), source=''), help_text='Tell us about yourself (use the markdown, Luke!)', markdown=s_markdown.datatype.Markdown, renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.comment.CommentExtension()]), renderer_name='about_renderer', state_name='_about_state', verbose_name='About'), null=True)),
                ('email_is_public', models.BooleanField(default=False, verbose_name='Show email')),
                ('karma', s_voting.models.VoteCacheField(default=0, query=s_voting.models._default_cache_query, vote_model=user.models.karma.Karma)),
                ('user', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
                'ordering': ('user',),
            },
        ),
        migrations.AlterUniqueTogether(
            name='karma',
            unique_together=set([('user', 'object')]),
        ),
    ]
