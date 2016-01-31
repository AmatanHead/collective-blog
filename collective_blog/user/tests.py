from django.test import TestCase

from django.contrib.auth import get_user_model
from . import models


class TestProfileModel(TestCase):

    def test_profile_creation(self):
        """Test that profile is created for each user"""

        User = get_user_model()

        user = User.objects.create(username="test", password="test")
        self.assertIsInstance(user.profile, models.Profile)
        user.save()
        self.assertIsInstance(user.profile, models.Profile)
