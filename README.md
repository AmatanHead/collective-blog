# collective-blog [![Build Status](https://travis-ci.org/AmatanHead/collective-blog.svg?branch=master)](https://travis-ci.org/AmatanHead/collective-blog) [![Coverage](https://api.codacy.com/project/badge/coverage/c434a6e4818c4b83a5aeb55f393056cd)](https://www.codacy.com/app/dev-zelta/collective-blog)

A project for HSE programming technologies course. See [wiki.cs.hse.ru](http://wiki.cs.hse.ru/Проектная_работа_2_курс_(2016)#.D0.9F.D1.80.D0.BE.D0.B5.D0.BA.D1.82:_.D0.9A.D0.BE.D0.BB.D0.BB.D0.B5.D0.BA.D1.82.D0.B8.D0.B2.D0.BD.D1.8B.D0.B9_.D0.B1.D0.BB.D0.BE.D0.B3_.28.D0.94..D0.91.D1.83.D1.80.D0.BC.D0.B8.D1.81.D1.82.D1.80.D0.BE.D0.B2.29) for more information.

## Dev installation

Clone the repo and create a virtualenv, if you need one.

Install the requirements:

```
$ pip install -r requirements.txt
```

Setup dev mode. You can run in either the `DEV=1` mode, `TRAVIS=1` mode, or `HEROKU=1` mode.
The first one is for development, the second one is fot ci tests, and the third one is for running in production.

```
$ export DEV=1
```

Setup other environment variables:

| Variable | Description
| -----|-------------
| SECRET_KEY | Used to encrypt session coockies.
| RECAPTCHA_PUBLIC_KEY | Public key for ReCaptcha.
| RECAPTCHA_PPRIVATE_KEY | Private key for ReCaptcha.
| DEFAULT_FROM_EMAIL | Email settings. See the Django documentation.
| EMAIL_HOST | -//-
| EMAIL_HOST_PASSWORD | -//-
| EMAIL_HOST_USER | -//-
| SERVER_EMAIL | -//-

Migrate your database:

```
$ cd collective-blog/
$ python manage.py makemigrations
$ python manage.py migrate
```

By default, SQLite is used. Be aware that SQLite can't perform case insensitive queries so urls and usernames will be case sensitive.

Launch the dev server:

```
$ python manage.py runserver 0.0.0.0:8000
```

Or tests (well, they are not ready yed; only markdown rendering is covered properly as it is the only thing that denormalizes the database):

```
$ python manage.py test
```

## Functionality

Each user can create a new blog. Once a new blog is created, it can be filled with content.

All blogs can be configured by creator:
* Type of the blog: *open* (anyone can see everything, news are shown on the main page), or *private* (only users who joined the blog can see its contents).
* Who can join the blog: anyone, user with karma above a decided value, or only approved users.
* Who can write to the blog: anyone or users with karma above a decided value or members of the blog.
* Who can write comments: anyone or users with karma above a decided value or members of the blog.

A blog's creator can assign administrators of the blog.
Permissions are configurable:
* Change another user's permissions.
* Change posts.
* Change comments.
* Ban a member.
* Change blog's settings.

Each user has its rating (karma). Users can vote up and down for any other user raising and dropping his karma respectively. Also, each member has individual blog's rating, one value per each blog. This value only matters inside that particular blog and changes while blog members are voting for comments and posts.


## Tools

* Python 2.7 || >= 3.4
* [Django](https://www.djangoproject.com) along with plugins for registration, captcha, markdown, and voting.
* [Markdown](github.com/waylan/Python-Markdown).
* [Codemirror](https://eloquentjavascript.net) for editing markdown.

And **no** WYSIWYG! ('cause it's evil!)


## Development status

* <s>User auth</s> — done
* <s>Markdown system</s> — done
* <s>Votes system</s> — done
* <s>User profiles</s> — done
* <s>Blogs</s> — done
* <s>Posts</s> — done
* <s>Comments</s> — done


## Criteria

**>= 4**

* <s>Can register, post, comment</s> — done
* <s>Comments are displayed flat</s> — done
* <s>SQL injection protected</s> — done by django

**>= 6**

* <s>A rating system which allows to vote without refreshing the page</s> — done (ajax voting)
* <s>WYSIWYG | Markdown</s> — done (markdown)
* <s>XSS proof</s> — done by django
* <s>Registration page protecred with CAPTCHA</s> — done (ReCapthca)
* <s>Comments are displayed with tree</s>  — done (django mptt)

**>= 8**

* <s>Manageable user permissions.</s>  — done
* <s>Service is ready to launch.</s>  — done


## Project structure

* `collective_blog` — django project
  * `collective_blog` — root app; Holds config, root url dispatcher, common css, scripts, and templates.
  Contains main app logic.
  * `user` — auth and user profile stuff, everything behind `/u/`; Holds auth logic and user profiles.
  * `s_appearance` — styles and form renderer.
  * `s_markdown` — standalone reusable app for markdown support.
  * `s_voting` — models for voting support.
