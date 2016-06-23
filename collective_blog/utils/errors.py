from django.core.exceptions import PermissionDenied


class PermissionCheckFailed(PermissionDenied):
    def __init__(self, note, *args, **kwargs):
        """Models will raise this if trying to perform illegal action

        It's guaranteed that `note` field contains a proper error description.

        """
        self.note = note
        super(PermissionCheckFailed, self).__init__(*args, **kwargs)
