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
        """
        Test that profile is created for each user.

        """

        user = User.objects.create(username="test2", password="test2")
        self.assertIsInstance(user.profile, Profile)
        user.save()
        self.assertIsInstance(user.profile, Profile)

    def test_profile_assigned(self):
        """
        Test that profile is assigned for each user.

        """

        user = User.objects.get(username="test")
        self.assertIsInstance(user.profile, Profile)

    def test_profile_deleted(self):
        """
        Test that profile is deleted properly.

        """

        user = User.objects.get(username="test")
        user.delete()
        profile = Profile.objects.all()
        self.assertEqual(profile.count(), 0)

    def test_user_deleted(self):
        """
        Test that user is deleted properly.

        """
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
        """
        Test that only moderators and the user can edit the user's profile.

        """

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

        self.assertTrue(Profile.can_edit_profile(moderator_with_perms, profile))
        self.assertTrue(Profile.can_edit_profile(moderator_with_perms2, profile))
        self.assertFalse(Profile.can_edit_profile(moderator_without_perms, profile))
        self.assertFalse(Profile.can_edit_profile(user_with_perms, profile))
        self.assertFalse(Profile.can_edit_profile(user_with_perms2, profile))
        self.assertTrue(Profile.can_edit_profile(superuser, profile))
        self.assertFalse(Profile.can_edit_profile(disabled_superuser, profile))
        self.assertFalse(Profile.can_edit_profile(disabled_superuser2, profile))
        self.assertFalse(Profile.can_edit_profile(ordinary_user, profile))
        self.assertTrue(Profile.can_edit_profile(user, profile))
        self.assertTrue(Profile.can_edit_profile(user2, profile))

    def test_can_see_the_email(self):
        """
        Test that only moderators and the user can see
        the user's private email.

        """
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

        self.assertTrue(Profile.can_see_email(moderator_with_perms, profile))
        self.assertTrue(Profile.can_see_email(moderator_with_perms2, profile))
        self.assertFalse(Profile.can_see_email(moderator_without_perms, profile))
        self.assertFalse(Profile.can_see_email(user_with_perms, profile))
        self.assertFalse(Profile.can_see_email(user_with_perms2, profile))
        self.assertTrue(Profile.can_see_email(superuser, profile))
        self.assertFalse(Profile.can_see_email(disabled_superuser, profile))
        self.assertFalse(Profile.can_see_email(disabled_superuser2, profile))
        self.assertFalse(Profile.can_see_email(ordinary_user, profile))
        self.assertTrue(Profile.can_see_email(user, profile))
        self.assertTrue(Profile.can_see_email(user2, profile))

        user.profile.email_is_public = True
        user.profile.save()

        user = User.objects.get(username="test")
        profile = user.profile
        user2 = User.objects.get(username="test")

        self.assertTrue(Profile.can_see_email(moderator_with_perms, profile))
        self.assertTrue(Profile.can_see_email(moderator_with_perms2, profile))
        self.assertTrue(Profile.can_see_email(moderator_without_perms, profile))
        self.assertTrue(Profile.can_see_email(user_with_perms, profile))
        self.assertTrue(Profile.can_see_email(user_with_perms2, profile))
        self.assertTrue(Profile.can_see_email(superuser, profile))
        self.assertTrue(Profile.can_see_email(disabled_superuser, profile))
        self.assertTrue(Profile.can_see_email(disabled_superuser2, profile))
        self.assertTrue(Profile.can_see_email(ordinary_user, profile))
        self.assertTrue(Profile.can_see_email(user, profile))
        self.assertTrue(Profile.can_see_email(user2, profile))

    def test_visible_email(self):
        """
        Test that private emails are displayed correctly.

        """
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

        self.assertEqual(Profile.visible_email(moderator_with_perms, profile), "a.b@example.com (%s)" % __('Only you can see the email'))
        self.assertEqual(Profile.visible_email(moderator_with_perms2, profile), "a.b@example.com (%s)" % __('Only you can see the email'))
        self.assertEqual(Profile.visible_email(moderator_without_perms, profile), '')
        self.assertEqual(Profile.visible_email(user_with_perms, profile), '')
        self.assertEqual(Profile.visible_email(user_with_perms2, profile), '')
        self.assertEqual(Profile.visible_email(superuser, profile), "a.b@example.com (%s)" % __('Only you can see the email'))
        self.assertEqual(Profile.visible_email(disabled_superuser, profile), '')
        self.assertEqual(Profile.visible_email(disabled_superuser2, profile), '')
        self.assertEqual(Profile.visible_email(ordinary_user, profile), '')
        self.assertEqual(Profile.visible_email(user, profile), "a.b@example.com (%s)" % __('Only you can see the email'))
        self.assertEqual(Profile.visible_email(user2, profile), "a.b@example.com (%s)" % __('Only you can see the email'))

        user.profile.email_is_public = True
        user.profile.save()

        user = User.objects.get(username="test")
        profile = user.profile
        user2 = User.objects.get(username="test")

        self.assertEqual(Profile.visible_email(moderator_with_perms, profile), "a.b@example.com")
        self.assertEqual(Profile.visible_email(moderator_with_perms2, profile), "a.b@example.com")
        self.assertEqual(Profile.visible_email(moderator_without_perms, profile), "a.b@example.com")
        self.assertEqual(Profile.visible_email(user_with_perms, profile), "a.b@example.com")
        self.assertEqual(Profile.visible_email(user_with_perms2, profile), "a.b@example.com")
        self.assertEqual(Profile.visible_email(superuser, profile), "a.b@example.com")
        self.assertEqual(Profile.visible_email(disabled_superuser, profile), "a.b@example.com")
        self.assertEqual(Profile.visible_email(disabled_superuser2, profile), "a.b@example.com")
        self.assertEqual(Profile.visible_email(ordinary_user, profile), "a.b@example.com")
        self.assertEqual(Profile.visible_email(user, profile), "a.b@example.com")
        self.assertEqual(Profile.visible_email(user2, profile), "a.b@example.com")
