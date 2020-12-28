import datetime
import unittest

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase


class TestProfileModels(TestCase):
    def setUp(self):
        self.user = User(username='test', first_name='testik', last_name='testoveek', email='test@testik.com')
        self.user.save()
        super().setUp()

    @unittest.expectedFailure
    def test_birth_date_with_past_date(self):
        with self.assertRaises(ValidationError):
            self.user.user_profile.birth_date = datetime.datetime.now() - datetime.timedelta(weeks=1900)
            self.user.user_profile.save()