# collective-blog [![Build Status](https://travis-ci.org/AmatanHead/collective-blog.svg?branch=master)](https://travis-ci.org/AmatanHead/collective-blog) [![Coverage](https://api.codacy.com/project/badge/coverage/c434a6e4818c4b83a5aeb55f393056cd)](https://www.codacy.com/app/dev-zelta/collective-blog)

A project for HSE programming technologies course. See [wiki.cs.hse.ru](http://wiki.cs.hse.ru/Проектная_работа_2_курс_(2016)#.D0.9F.D1.80.D0.BE.D0.B5.D0.BA.D1.82:_.D0.9A.D0.BE.D0.BB.D0.BB.D0.B5.D0.BA.D1.82.D0.B8.D0.B2.D0.BD.D1.8B.D0.B9_.D0.B1.D0.BB.D0.BE.D0.B3_.28.D0.94..D0.91.D1.83.D1.80.D0.BC.D0.B8.D1.81.D1.82.D1.80.D0.BE.D0.B2.29) for more information.

## Dev installation

Clone the repo and create a virtualenv, if you need one.

Install the requirements:

```
$ pip install -r requirements.txt
```

Migrate your database:

```
$ cd collective-blog/
$ python manage.py makemigrations
$ python manage.py migrate
```

By default, SQLite is used. Be aware that SQLite can't perform iexact queries.

Launch the dev server:

```
$ python manage.py runserver 0.0.0.0:8000
```

Or tests (well, they are not ready yed; only markdown rendering is covered properly as it is the only thing that denormalizes the database):

```
$ python manage.py test
```

## Functionality planned

Each user can create a new blog. No limit for blogs per user. Once a new blog is created, it can be filled with content.

A blog's creator can decide how to configure it:
* Type of the blog: *open* (anyone can see everything, news are shown on the main page), or *private* (only users who joined the blog can see its content).
* Who can join the blog: anyone, user with rating above a decided value, only approved users.
* Who can write to the blog: anyone with rating above a decided value, only members of this blog.
* Who can write comments: anyone with rating above a decided value, only members of this blog.

A blog's author can assign blog administrators and moderators and (in any time) resign them.
Permissions are configurable:
* Change another user's permissions.
* Change posts.
* Change comments.
* Ban a member.
* Change blog's settings.

Each user has its rating (karma). Users can vote up and down for any other users raising and dropping his karma respectively. Also, each member has individual blog's rating, one value per each blog. This value only matters inside that particular blog and changes while blog members are voting for comments and posts.


## Tools

* Python 2.7 || >= 3.4
* [Django](https://www.djangoproject.com) along with plugins for registration, captcha, markdown, and voting.
* [Markdown](github.com/waylan/Python-Markdown).
* [Codemirror](https://eloquentjavascript.net) for editing markdown.
* [Light](https://github.com/AmatanHead/light) css framework.

And **no** WYSIWYG! ('cause it's evil!)


## Development status

* <s>User auth</s> — done
* <s>Markdown system</s> — done
* <s>Votes system</s> — done
* <s>User profiles</s> — done
* <s>Blogs</s> — done
* <s>Posts</s> — done
* Comments


## Project structure

* `collective_blog` — django project
  * `collective_blog` — root app; Holds config, root url dispatcher, common css, scripts, and templates.
  * `blog` — blogs and posts and main feed; core functionality.
  * `user` — auth and user profile stuff, everything behind `/u/`; Holds auth logic and user profiles.
  * `s_appearance` — styles and form renderer.
  * `s_markdown` — standalone reusable app for markdown support.
  * `s_voting` — models for voting support.
