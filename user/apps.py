from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


class UserConfig(AppConfig):
    name = 'user'
    label = 'user'
    verbose_name = _('Profiles and users')

    def ready(self):
        """Callback on models loaded"""

        from django.dispatch import receiver
        from django.db.models.signals import post_save

        @receiver(post_save, sender=get_user_model(), dispatch_uid='create_profile_for_new_user', weak=False)
        def create_profile_for_new_user(sender, created, instance, **kwargs):
            """For each new user we want to create its profile automatically

            :param sender: Default Django parameters
            :param created: Default Django parameters
            :param instance: Default Django parameters
            :param kwargs: Default Django parameters

            """
            if created:
                profile = self.get_model('profile')(user=instance)
                profile.save()
