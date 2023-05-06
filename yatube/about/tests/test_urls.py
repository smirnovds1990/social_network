from http import HTTPStatus

from django.test import TestCase


class URLTests(TestCase):
    """Тестирование статичных страниц."""
    def test_static_pages(self):
        self.static_urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for route, template in self.static_urls.items():
            with self.subTest(url=route, template=template):
                response = self.client.get(route)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
