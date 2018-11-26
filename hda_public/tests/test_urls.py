from io import StringIO

from django.test import TestCase, Client
from django.core.management import call_command


class HappyUrlsTestCase(TestCase):
    def setUp(self):
        out = StringIO()
        call_command('load_random_data_set', stdout=out)
        self.client = Client()

    def testPublicUrlsLoad(self):
        paths_to_test = [
            ('home', ''),
            ('state chart', '/chart/al/1'),
            ('county chart', '/chart/al/001/1'),
            ('table', '/table'),
            ('select state', '/state'),
            ('select county', '/state/AL'),
            ('select indicator', '/state/AL/001'),
        ]
        for (name, path) in paths_to_test:
            with self.subTest(label=name):
                response = self.client.get(path, follow=True)
                self.assertEqual(response.status_code, 200, response.content)
