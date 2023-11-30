from django.contrib.auth.mixins import UserPassesTestMixin


class UserIsAdmin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff


class CanViewThisSolution(UserPassesTestMixin):
    pass
