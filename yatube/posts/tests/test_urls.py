from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User


class URLTests(TestCase):
    """Тестирование URLs и шаблонов."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            description='Описание тестовой группы для проверки urls.',
            slug='test_slug',
            title='Тестовая группа для проверки urls'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Текст для тестового поста при проверке.',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_urls_for_any_user(self):
        """Тестирование страниц доступных всем пользователям."""
        general_urls = {
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.author}/',
            f'/posts/{self.post.id}/',
        }
        for url in general_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                auth_response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertEqual(auth_response.status_code, HTTPStatus.OK)

    def test_unexisting_url(self):
        """Тестирование ошибки 404."""
        unexisting_url = '/unexisting_page/'
        response = self.client.get(unexisting_url)
        auth_response = self.authorized_client.get(unexisting_url)
        self.assertEqual(auth_response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_404_page(self):
        """Тестирование шаблона страницы ошибки 404."""
        unexisting_url = '/unexisting_page/'
        template = 'core/404.html'
        response = self.client.get(unexisting_url)
        auth_response = self.authorized_client.get(unexisting_url)
        self.assertTemplateUsed(auth_response, template)
        self.assertTemplateUsed(response, template)

    def test_post_create_url(self):
        """Тестирование страницы создания поста."""
        post_create_url = '/create/'
        response = self.authorized_client.get(post_create_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url(self):
        """Тестирование страницы редактирования поста."""
        post_edit_url = f'/posts/{self.post.id}/edit/'
        response = self.authorized_client.get(post_edit_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_templates_for_any_user(self):
        """Тестирование шаблонов страниц."""
        routes = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        for url, template in routes.items():
            with self.subTest(url=url, template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_guest_redirect_from_post_create(self):
        """Тестирование редиректа гостя со страницы создания поста."""
        path = reverse('posts:post_create')
        response = self.client.get(path)
        self.assertRedirects(
            response, reverse('users:login')
            + '?next='
            + reverse('posts:post_create')
        )

    def test_guest_redirect_from_post_edit(self):
        """Тестирование редиректа гостя со страницы редактирования поста."""
        path = reverse(
            'posts:post_edit', kwargs={'post_id': (self.post.id)}
        )
        response = self.client.get(path)
        self.assertRedirects(
            response, reverse('users:login')
            + '?next='
            + reverse('posts:post_edit', kwargs={'post_id': (self.post.id)})
        )

    def test_changing_post_by_not_author(self):
        """Тестирование редиректа неавтора со страницы редактирования поста."""
        path = reverse(
            'posts:post_edit', kwargs={'post_id': (self.post.id)}
        )
        not_author = User.objects.create_user(username='not_author')
        self.authorized_client.force_login(not_author)
        response = self.authorized_client.get(path)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': (self.post.id)})
        )
