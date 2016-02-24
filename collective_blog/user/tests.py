from django.test import TestCase

from django.contrib.auth import get_user_model
from . import models

User = get_user_model()


class TestProfileModel(TestCase):

    def test_profile_creation(self):
        """Test that profile is created for each user"""

        user = User.objects.create(username="test", password="test")
        self.assertIsInstance(user.profile, models.Profile)
        user.save()
        self.assertIsInstance(user.profile, models.Profile)
