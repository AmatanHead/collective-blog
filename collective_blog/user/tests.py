"""Tests for user profile"""

from django import test

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext as __

from .models import Profile

User = get_user_model()


class TestProfileModel(test.TransactionTestCase):
    def setUp(self):
        User.objects.create(username="test", password="test")

    def test_profile_creation(self):
        """Test that profile is created for each user"""

        user = User.objects.create(username="test2", password="test2")
        self.assertIsInstance(user.profile, Profile)
        user.save()
        self.assertIsInstance(user.profile, Profile)

    def test_profile_assigned(self):
        """Test that profile is assigned for each user"""

        user = User.objects.get(username="test")
        self.assertIsInstance(user.profile, Profile)

    def test_profile_deleted(self):
        """Test that profile is deleted properly"""

        user = User.objects.get(username="test")
        user.delete()
        profile = Profile.objects.all()
        self.assertEqual(profile.count(), 0)

    def test_user_deleted(self):
        """Test that user is deleted properly"""

        user = User.objects.get(username="test")
        user.profile.delete()
        users = User.objects.all()
        self.assertEqual(users.count(), 0)


class TestProfileModelPerms(test.TransactionTestCase):
    def setUp(self):
        User.objects.create(username="test", password="test", email="a.b@example.com")

        can_change_profile = Permission.objects.get(codename="change_profile")
        can_change_user = Permission.objects.get(codename="change_user")

        moderator_with_perms = User.objects.create(username="moderator_with_perms", password="_", is_staff=True, is_active=True)
        moderator_with_perms.user_permissions.add(can_change_profile)
        moderator_with_perms.save()

        moderator_with_perms2 = User.objects.create(username="moderator_with_perms2", password="_", is_staff=True, is_active=True)
        moderator_with_perms2.user_permissions.add(can_change_user)
        moderator_with_perms2.save()

        moderator_without_perms = User.objects.create(username="moderator_without_perms", password="_", is_staff=True, is_active=True)
        moderator_without_perms.save()

        user_with_perms = User.objects.create(username="user_with_perms", password="_", is_active=True)
        user_with_perms.user_permissions.add(can_change_profile)
        user_with_perms.save()

        user_with_perms2 = User.objects.create(username="user_with_perms2", password="_", is_active=True)
        user_with_perms2.user_permissions.add(can_change_user)
        user_with_perms2.save()

        superuser = User.objects.create(username="superuser", password="_", is_active=True, is_staff=True, is_superuser=True)
        superuser.save()

        disabled_superuser = User.objects.create(username="disabled_superuser", password="_", is_staff=True, is_active=False, is_superuser=True)
        disabled_superuser.save()

        disabled_superuser2 = User.objects.create(username="disabled_superuser2", password="_", is_active=True, is_staff=False, is_superuser=True)
        disabled_superuser2.save()

        ordinary_user = User.objects.create(username="ordinary_user", password="_")
        ordinary_user.save()

    def test_can_edit_profile(self):
        """Test that only moderators and the user can edit the user's profile"""

        moderator_with_perms = User.objects.get(username='moderator_with_perms')
        moderator_with_perms2 = User.objects.get(username='moderator_with_perms2')
        moderator_without_perms = User.objects.get(username='moderator_without_perms')
        user_with_perms = User.objects.get(username='user_with_perms')
        user_with_perms2 = User.objects.get(username='user_with_perms2')
        superuser = User.objects.get(username='superuser')
        disabled_superuser = User.objects.get(username='disabled_superuser')
        disabled_superuser2 = User.objects.get(username='disabled_superuser2')
        ordinary_user = User.objects.get(username='ordinary_user')

        user = User.objects.get(username="test")
        profile = user.profile
        user2 = User.objects.get(username="test")

        self.assertTrue(profile.can_be_edited_by(moderator_with_perms))
        self.assertTrue(profile.can_be_edited_by(moderator_with_perms2))
        self.assertFalse(profile.can_be_edited_by(moderator_without_perms))
        self.assertFalse(profile.can_be_edited_by(user_with_perms))
        self.assertFalse(profile.can_be_edited_by(user_with_perms2))
        self.assertTrue(profile.can_be_edited_by(superuser))
        self.assertFalse(profile.can_be_edited_by(disabled_superuser))
        self.assertFalse(profile.can_be_edited_by(disabled_superuser2))
        self.assertFalse(profile.can_be_edited_by(ordinary_user))
        self.assertTrue(profile.can_be_edited_by(user))
        self.assertTrue(profile.can_be_edited_by(user2))

    def test_can_see_the_email(self):
        """Test that only moderators and the user can seethe user's private email"""

        moderator_with_perms = User.objects.get(username='moderator_with_perms')
        moderator_with_perms2 = User.objects.get(username='moderator_with_perms2')
        moderator_without_perms = User.objects.get(username='moderator_without_perms')
        user_with_perms = User.objects.get(username='user_with_perms')
        user_with_perms2 = User.objects.get(username='user_with_perms2')
        superuser = User.objects.get(username='superuser')
        disabled_superuser = User.objects.get(username='disabled_superuser')
        disabled_superuser2 = User.objects.get(username='disabled_superuser2')
        ordinary_user = User.objects.get(username='ordinary_user')

        user = User.objects.get(username="test")
        profile = user.profile
        user2 = User.objects.get(username="test")

        self.assertTrue(profile.email_can_be_seen_by(moderator_with_perms))
        self.assertTrue(profile.email_can_be_seen_by(moderator_with_perms2))
        self.assertFalse(profile.email_can_be_seen_by(moderator_without_perms))
        self.assertFalse(profile.email_can_be_seen_by(user_with_perms))
        self.assertFalse(profile.email_can_be_seen_by(user_with_perms2))
        self.assertTrue(profile.email_can_be_seen_by(superuser))
        self.assertFalse(profile.email_can_be_seen_by(disabled_superuser))
        self.assertFalse(profile.email_can_be_seen_by(disabled_superuser2))
        self.assertFalse(profile.email_can_be_seen_by(ordinary_user))
        self.assertTrue(profile.email_can_be_seen_by(user))
        self.assertTrue(profile.email_can_be_seen_by(user2))

        user.profile.email_is_public = True
        user.profile.save()

        user = User.objects.get(username="test")
        profile = user.profile
        user2 = User.objects.get(username="test")

        self.assertTrue(profile.email_can_be_seen_by(moderator_with_perms))
        self.assertTrue(profile.email_can_be_seen_by(moderator_with_perms2))
        self.assertTrue(profile.email_can_be_seen_by(moderator_without_perms))
        self.assertTrue(profile.email_can_be_seen_by(user_with_perms))
        self.assertTrue(profile.email_can_be_seen_by(user_with_perms2))
        self.assertTrue(profile.email_can_be_seen_by(superuser))
        self.assertTrue(profile.email_can_be_seen_by(disabled_superuser))
        self.assertTrue(profile.email_can_be_seen_by(disabled_superuser2))
        self.assertTrue(profile.email_can_be_seen_by(ordinary_user))
        self.assertTrue(profile.email_can_be_seen_by(user))
        self.assertTrue(profile.email_can_be_seen_by(user2))

    def test_visible_email(self):
        """Test that private emails are displayed correctly"""

        moderator_with_perms = User.objects.get(username='moderator_with_perms')
        moderator_with_perms2 = User.objects.get(username='moderator_with_perms2')
        moderator_without_perms = User.objects.get(username='moderator_without_perms')
        user_with_perms = User.objects.get(username='user_with_perms')
        user_with_perms2 = User.objects.get(username='user_with_perms2')
        superuser = User.objects.get(username='superuser')
        disabled_superuser = User.objects.get(username='disabled_superuser')
        disabled_superuser2 = User.objects.get(username='disabled_superuser2')
        ordinary_user = User.objects.get(username='ordinary_user')

        user = User.objects.get(username="test")
        profile = user.profile
        user2 = User.objects.get(username="test")

        self.assertEqual(profile.email_as_seen_by(moderator_with_perms), "a.b@example.com (%s)" % __('Only you can see the email'))
        self.assertEqual(profile.email_as_seen_by(moderator_with_perms2), "a.b@example.com (%s)" % __('Only you can see the email'))
        self.assertEqual(profile.email_as_seen_by(moderator_without_perms), '')
        self.assertEqual(profile.email_as_seen_by(user_with_perms), '')
        self.assertEqual(profile.email_as_seen_by(user_with_perms2), '')
        self.assertEqual(profile.email_as_seen_by(superuser), "a.b@example.com (%s)" % __('Only you can see the email'))
        self.assertEqual(profile.email_as_seen_by(disabled_superuser), '')
        self.assertEqual(profile.email_as_seen_by(disabled_superuser2), '')
        self.assertEqual(profile.email_as_seen_by(ordinary_user), '')
        self.assertEqual(profile.email_as_seen_by(user), "a.b@example.com (%s)" % __('Only you can see the email'))
        self.assertEqual(profile.email_as_seen_by(user2), "a.b@example.com (%s)" % __('Only you can see the email'))

        user.profile.email_is_public = True
        user.profile.save()

        user = User.objects.get(username="test")
        profile = user.profile
        user2 = User.objects.get(username="test")

        self.assertEqual(profile.email_as_seen_by(moderator_with_perms), "a.b@example.com")
        self.assertEqual(profile.email_as_seen_by(moderator_with_perms2), "a.b@example.com")
        self.assertEqual(profile.email_as_seen_by(moderator_without_perms), "a.b@example.com")
        self.assertEqual(profile.email_as_seen_by(user_with_perms), "a.b@example.com")
        self.assertEqual(profile.email_as_seen_by(user_with_perms2), "a.b@example.com")
        self.assertEqual(profile.email_as_seen_by(superuser), "a.b@example.com")
        self.assertEqual(profile.email_as_seen_by(disabled_superuser), "a.b@example.com")
        self.assertEqual(profile.email_as_seen_by(disabled_superuser2), "a.b@example.com")
        self.assertEqual(profile.email_as_seen_by(ordinary_user), "a.b@example.com")
        self.assertEqual(profile.email_as_seen_by(user), "a.b@example.com")
        self.assertEqual(profile.email_as_seen_by(user2), "a.b@example.com")
