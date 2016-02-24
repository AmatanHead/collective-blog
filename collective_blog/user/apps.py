from django.apps import AppConfig
from django.contrib.auth import get_user_model


class UserConfig(AppConfig):
    name = 'user'
    label = 'user'
    verbose_name = 'user'

    def ready(self):
        from django.dispatch import receiver
        from django.db.models.signals import post_save

        @receiver(post_save, sender=get_user_model(), dispatch_uid='create_profile_for_new_user', weak=False)
        def create_profile_for_new_user(sender, created, instance, **kwargs):
            """For each new user we want to create its profile automatically"""
            if created:
                profile = self.get_model('profile')(user=instance)
                profile.save()
