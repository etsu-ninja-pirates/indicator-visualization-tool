from io import StringIO

from django.test import TestCase, Client
from django.core.management import call_command
from django.contrib.auth import get_user_model


class HappyUrlsTestCase(TestCase):
    def setUp(self):
        out = StringIO()
        call_command('load_random_data_set', stdout=out)

        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='12345')

        self.client = Client()
        self.client.login(username='testuser', password='12345')

    def testPrivUrlsLoad(self):
        paths_to_test = [
            ('home', '/priv/home'),
            ('home filtered', '/priv/home/1'),
            ('upload', '/priv/upload'),
            ('metric', '/priv/metric'),
            ('create metric', '/priv/metric/create'),
            ('login', '/priv/login'),
        ]
        for (name, path) in paths_to_test:
            with self.subTest(label=name):
                response = self.client.get(path, follow=True)
                self.assertEqual(response.status_code, 200, response.content)

    # ToDO: test logout
    # ToDO: test that URLs are not publicly accessible!