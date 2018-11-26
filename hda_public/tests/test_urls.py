from io import StringIO

from django.test import TestCase
from django.core.management import call_command


class HappyUrlsTestCase(TestCase):

    # setUpTestData runs once for the class, not once per test,
    # so we can load a data set one time to speed things up IF
    # we have multiple test methods and we don't need to reset
    @classmethod
    def setUpTestData(cls):
        out = StringIO()
        call_command('load_random_data_set', stdout=out)

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
