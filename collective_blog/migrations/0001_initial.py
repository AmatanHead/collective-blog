# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-23 16:36
from __future__ import unicode_literals

import collective_blog.models.blog
import collective_blog.models.comment
import collective_blog.models.post
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mptt.fields
import s_markdown.datatype
import s_markdown.extensions.autolink
import s_markdown.extensions.automail
import s_markdown.extensions.comment
import s_markdown.extensions.cut
import s_markdown.extensions.escape
import s_markdown.extensions.fenced_code
import s_markdown.extensions.semi_sane_lists
import s_markdown.extensions.strikethrough
import s_markdown.models
import s_markdown.renderer
import s_voting.models
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('slug', models.SlugField(blank=True, editable=False, max_length=100, unique=True)),
                ('about', s_markdown.models.MarkdownField(blank=True, cls_name='about_cls', default=s_markdown.datatype.Markdown(html='', renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.comment.CommentExtension()]), source=''), markdown=s_markdown.datatype.Markdown, renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.comment.CommentExtension()]), renderer_name='about_renderer', state_name='_about_state', verbose_name='About this blog')),
                ('_about_html', s_markdown.models.HtmlCacheField(blank=True, editable=False, markdown_field=s_markdown.models.MarkdownField(blank=True, cls_name='about_cls', default=s_markdown.datatype.Markdown(html='', renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.comment.CommentExtension()]), source=''), markdown=s_markdown.datatype.Markdown, renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.comment.CommentExtension()]), renderer_name='about_renderer', state_name='_about_state', verbose_name='About this blog'), null=True)),
                ('icon', models.CharField(blank=True, choices=[('aircraft', 'aircraft'), ('aircraft-take-off', 'aircraft take off'), ('aircraft-landing', 'aircraft landing'), ('area-graph', 'area graph'), ('archive', 'archive'), ('attachment', 'attachment'), ('awareness-ribbon', 'awareness ribbon'), ('back-in-time', 'back in time'), ('bar-graph', 'bar graph'), ('beamed-note', 'beamed note'), ('bell', 'bell'), ('blackboard', 'blackboard'), ('book', 'book'), ('bowl', 'bowl'), ('bookmarks', 'bookmarks'), ('box', 'box'), ('briefcase', 'briefcase'), ('brush', 'brush'), ('bucket', 'bucket'), ('bug', 'bug'), ('cake', 'cake'), ('camera', 'camera'), ('chat', 'chat'), ('clapperboard', 'clapperboard'), ('classic-computer', 'classic computer'), ('clipboard', 'clipboard'), ('cloud', 'cloud'), ('code', 'code'), ('cog', 'cog'), ('colours', 'colours'), ('compass', 'compass'), ('database', 'database'), ('dial-pad', 'dial pad'), ('documents', 'documents'), ('feather', 'feather'), ('flag', 'flag'), ('flash', 'flash'), ('flashlight', 'flashlight'), ('flat-brush', 'flat brush'), ('flow-branch', 'flow branch'), ('flower', 'flower'), ('folder', 'folder'), ('info-with-circle', 'info with circle'), ('infinity', 'infinity'), ('image', 'image'), ('hand', 'hand'), ('hair-cross', 'hair cross'), ('grid', 'grid'), ('graduation-cap', 'graduation cap'), ('globe', 'globe'), ('lab-flask', 'lab flask'), ('landline', 'landline'), ('keyboard', 'keyboard'), ('key', 'key'), ('layers', 'layers'), ('laptop', 'laptop'), ('leaf', 'leaf'), ('lifebuoy', 'lifebuoy'), ('light-bulb', 'light bulb'), ('light-up', 'light up'), ('line-graph', 'line graph'), ('location-pin', 'location pin'), ('modern-mic', 'modern mic'), ('moon', 'moon'), ('mic', 'mic'), ('medal', 'medal'), ('mail', 'mail'), ('magnet', 'magnet'), ('mouse-pointer', 'mouse pointer'), ('mouse', 'mouse'), ('network', 'network'), ('palette', 'palette'), ('new-message', 'new message'), ('new', 'new'), ('newsletter', 'newsletter'), ('note', 'note'), ('paper-plane', 'paper plane'), ('phone', 'phone'), ('rocket', 'rocket'), ('radio', 'radio'), ('print', 'print'), ('price-tag', 'price tag'), ('shop', 'shop'), ('suitcase', 'suitcase'), ('tablet-mobile-combo', 'tablet mobile combo'), ('thunder-cloud', 'thunder cloud'), ('ticket', 'ticket'), ('time-slot', 'time slot'), ('tools', 'tools'), ('traffic-cone', 'traffic cone'), ('tree', 'tree'), ('tv', 'tv'), ('video-camera', 'video camera'), ('video', 'video'), ('vinyl', 'vinyl'), ('voicemail', 'voicemail'), ('wallet', 'wallet'), ('warning', 'warning'), ('water', 'water')], max_length=100)),
                ('type', models.CharField(choices=[('O', 'Open'), ('P', 'Private')], default='0', max_length=2, verbose_name='Type of the blog')),
                ('join_condition', models.CharField(choices=[('A', 'Anyone can join'), ('K', 'Only users with high karma can join'), ('I', 'Manual approval required')], default='A', max_length=2, verbose_name='Who can join the blog')),
                ('join_karma_threshold', models.SmallIntegerField(default=0, verbose_name='Join karma threshold')),
                ('post_condition', models.CharField(choices=[('A', 'Anyone can add posts'), ('K', 'Only users with high karma can add posts')], default='K', max_length=2, verbose_name='Who can add posts')),
                ('post_membership_required', models.BooleanField(default=True, verbose_name='Require membership to write posts')),
                ('post_admin_required', models.BooleanField(default=False, verbose_name='Only admins can write posts')),
                ('post_karma_threshold', models.SmallIntegerField(default=0, verbose_name='Post karma threshold')),
                ('comment_condition', models.CharField(choices=[('A', 'Anyone can comment'), ('K', 'Only users with high karma can comment')], default='A', max_length=2, verbose_name='Who can comment in the blog')),
                ('comment_membership_required', models.BooleanField(default=False, verbose_name='Require membership to write comments')),
                ('comment_karma_threshold', models.SmallIntegerField(default=0, verbose_name='Comment karma threshold')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'Blogs',
                'verbose_name': 'Blog',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', s_markdown.models.MarkdownField(cls_name='content_cls', default=s_markdown.datatype.Markdown(html='', renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.comment.CommentExtension()]), source=''), markdown=s_markdown.datatype.Markdown, renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.comment.CommentExtension()]), renderer_name='content_renderer', state_name='_content_state', verbose_name='Comment')),
                ('_content_html', s_markdown.models.HtmlCacheField(blank=True, editable=False, markdown_field=s_markdown.models.MarkdownField(cls_name='content_cls', default=s_markdown.datatype.Markdown(html='', renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.comment.CommentExtension()]), source=''), markdown=s_markdown.datatype.Markdown, renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.comment.CommentExtension()]), renderer_name='content_renderer', state_name='_content_state', verbose_name='Comment'), null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('rating', s_voting.models.VoteCacheField(default=0, query=s_voting.models._default_cache_query, vote_model=collective_blog.models.comment.CommentVote)),
                ('is_hidden', models.BooleanField(default=False, verbose_name='Is hidden')),
                ('is_hidden_by_moderator', models.BooleanField(default=False, verbose_name='Is hidden by moderator')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='collective_blog.Comment')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CommentVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.SmallIntegerField(choices=[(1, '+1'), (-1, '-1')])),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='collective_blog.Comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes_for_collective_blog_commentvote', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(choices=[('gray', 'Gray'), ('black', 'Black'), ('blue', 'Blue'), ('orange', 'Orange'), ('purple', 'Purple'), ('marshy', 'Marshy'), ('turquoise', 'Turquoise'), ('red', 'Red'), ('yellow', 'Yellow'), ('green', 'Green')], default='gray', max_length=10)),
                ('role', models.CharField(choices=[('O', 'Owner'), ('M', 'Member'), ('B', 'Banned'), ('A', 'Administrator'), ('W', 'Waiting for approval'), ('L', 'Left the blog'), ('LB', 'Left the blog (banned)')], default='L', max_length=2)),
                ('ban_expiration', models.DateTimeField(default=django.utils.timezone.now)),
                ('can_change_settings_flag', models.BooleanField(default=False, verbose_name="Can change blog's settings")),
                ('can_delete_posts_flag', models.BooleanField(default=False, verbose_name='Can delete posts')),
                ('can_delete_comments_flag', models.BooleanField(default=False, verbose_name='Can delete comments')),
                ('can_ban_flag', models.BooleanField(default=False, verbose_name='Can ban a member')),
                ('can_accept_new_users_flag', models.BooleanField(default=False, verbose_name='Can accept new users')),
                ('can_manage_permissions_flag', models.BooleanField(default=False, verbose_name='Can manage permissions')),
                ('overall_posts_rating', s_voting.models.VoteCacheField(default=0, query=collective_blog.models.blog._overall_posts_rating_cache_query, vote_model=collective_blog.models.post.PostVote)),
                ('overall_comments_rating', s_voting.models.VoteCacheField(default=0, query=collective_blog.models.blog._overall_comments_rating_cache_query, vote_model=collective_blog.models.comment.CommentVote)),
                ('blog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collective_blog.Blog')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(max_length=100, verbose_name='Title')),
                ('slug', models.SlugField(blank=True, editable=False, max_length=100, unique=True)),
                ('is_draft', models.BooleanField(default=True, verbose_name='Is draft')),
                ('content', s_markdown.models.MarkdownField(cls_name='content_cls', default=s_markdown.datatype.Markdown(html='', renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.cut.CutExtension(anchor='cut')]), source=''), markdown=s_markdown.datatype.Markdown, renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.cut.CutExtension(anchor='cut')]), renderer_name='content_renderer', state_name='_content_state', verbose_name='Content')),
                ('_content_html', s_markdown.models.HtmlCacheField(blank=True, editable=False, markdown_field=s_markdown.models.MarkdownField(cls_name='content_cls', default=s_markdown.datatype.Markdown(html='', renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.cut.CutExtension(anchor='cut')]), source=''), markdown=s_markdown.datatype.Markdown, renderer=s_markdown.renderer.BaseRenderer(extensions=['markdown.extensions.smarty', 'markdown.extensions.abbr', 'markdown.extensions.def_list', 'markdown.extensions.tables', 'markdown.extensions.smart_strong', s_markdown.extensions.fenced_code.FencedCodeExtension(), s_markdown.extensions.escape.EscapeHtmlExtension(), s_markdown.extensions.semi_sane_lists.SemiSaneListExtension(), s_markdown.extensions.strikethrough.StrikethroughExtension(), s_markdown.extensions.autolink.AutolinkExtension(), s_markdown.extensions.automail.AutomailExtension(), s_markdown.extensions.cut.CutExtension(anchor='cut')]), renderer_name='content_renderer', state_name='_content_state', verbose_name='Content'), null=True)),
                ('created', models.DateTimeField(blank=True, editable=False, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('rating', s_voting.models.VoteCacheField(default=0, query=s_voting.models._default_cache_query, vote_model=collective_blog.models.post.PostVote)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('blog', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='collective_blog.Blog', verbose_name='Blog')),
            ],
            options={
                'ordering': ('-created',),
                'verbose_name_plural': 'Posts',
                'verbose_name': 'Post',
            },
        ),
        migrations.CreateModel(
            name='PostVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.SmallIntegerField(choices=[(1, '+1'), (-1, '-1')])),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='collective_blog.Post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes_for_collective_blog_postvote', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='Slug')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'Tags',
                'verbose_name': 'Tag',
            },
        ),
        migrations.CreateModel(
            name='TaggedItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.IntegerField(db_index=True, verbose_name='Object id')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collective_blog_taggeditem_tagged_items', to='contenttypes.ContentType', verbose_name='Content type')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collective_blog_taggeditem_items', to='collective_blog.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags', through='collective_blog.TaggedItem', to='collective_blog.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collective_blog.Post', verbose_name='Post'),
        ),
        migrations.AddField(
            model_name='blog',
            name='members',
            field=models.ManyToManyField(editable=False, through='collective_blog.Membership', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='postvote',
            unique_together=set([('user', 'object')]),
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('user', 'blog')]),
        ),
        migrations.AlterUniqueTogether(
            name='commentvote',
            unique_together=set([('user', 'object')]),
        ),
    ]
