from django.test import TestCase

from comments.models import User


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        User.objects.create(nickname="bob", firstname="Bob")

    def test_nickname(self):
        user = User.objects.get(nickname="bob")
        self.assertEquals(str(user), user.nickname)
