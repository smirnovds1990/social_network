import math
import random
import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.models import Group, Post, User, Follow
from posts.forms import PostForm
from posts import constants


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class URLTests(TestCase):
    """Тестирование view-функций."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            description='Описание тестовой группы для проверки view-функций.',
            slug='test_slug',
            title='Тестовая группа для проверки view-функций'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Текст для тестового поста при проверке.',
        )

        cls.REVERSES = (
            {
                'template': 'posts/index.html',
                'reverse': reverse('posts:index')
            },
            {
                'template': 'posts/group_list.html',
                'reverse': reverse(
                    'posts:group_posts', kwargs={'slug': (cls.group.slug)}
                )
            },
            {
                'template': 'posts/profile.html',
                'reverse': reverse(
                    'posts:profile', kwargs={'username': (cls.author.username)}
                )
            },
            {
                'template': 'posts/post_detail.html',
                'reverse': reverse(
                    'posts:post_detail', kwargs={'post_id': (cls.post.id)}
                )
            },
            {
                'template': 'posts/create_post.html',
                'reverse': reverse(
                    'posts:post_edit', kwargs={'post_id': (cls.post.id)}
                )
            },
            {
                'template': 'posts/create_post.html',
                'reverse': reverse('posts:post_create')
            },

        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        cache.clear()

    def test_reverses(self):
        """Тестирование реверсов."""
        for reverse_name in self.REVERSES:
            with self.subTest(reverse_name=reverse_name['reverse']):
                response = self.authorized_client.get(reverse_name['reverse'])
                self.assertTemplateUsed(response, reverse_name['template'])

    def test_index_context(self):
        """Тестирование содержимого словаря context в index."""
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.context['page_obj']
        self.assertIsInstance(posts, Page)
        for post in posts:
            self.assertEqual(post.author, self.author)
            self.assertEqual(post.group, self.group)
            self.assertEqual(post.id, self.post.id)
            self.assertEqual(post.text, self.post.text)

    def test_group_posts_context(self):
        """Тестирование содержимого словаря context в group_posts."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts', kwargs={'slug': (self.group.slug)}
            )
        )
        posts = response.context['page_obj']
        group = response.context['group']
        for post in posts:
            self.assertEqual(post.author, self.author)
            self.assertEqual(post.group, self.group)
            self.assertEqual(post.id, self.post.id)
            self.assertEqual(post.text, self.post.text)
        self.assertEqual(group, self.group)

    def test_profile_context(self):
        """Тестирование содержимого словаря context в profile."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': (self.author.username)}
            )
        )
        posts = response.context['page_obj']
        author = response.context['author']
        for post in posts:
            self.assertEqual(post.author, self.author)
            self.assertEqual(post.group, self.group)
            self.assertEqual(post.id, self.post.id)
            self.assertEqual(post.text, self.post.text)
        self.assertEqual(author, self.author)

    def test_post_detail_context(self):
        """Тестирование содержимого словаря context в post_detail."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': (self.post.id)}
            )
        )
        post = response.context['post']
        self.assertEqual(post, self.post)
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.text, self.post.text)

    def test_post_edit_context(self):
        """Тестирование содержимого словаря context в post_edit."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit', kwargs={'post_id': (self.post.id)}
            )
        )
        edited_post = response.context['post']
        edited_post_form = response.context['form']
        edited_post_is_edit = response.context['is_edit']
        self.assertEqual(edited_post, self.post)
        self.assertEqual(edited_post.author, self.author)
        self.assertEqual(edited_post.group, self.group)
        self.assertEqual(edited_post.id, self.post.id)
        self.assertEqual(edited_post.text, self.post.text)
        self.assertIsInstance(edited_post_form, PostForm)
        self.assertTrue(edited_post_is_edit)

    def test_post_create_context(self):
        """Тестирование содержимого словаря context в post_create."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        new_post_from = response.context['form']
        self.assertIsInstance(new_post_from, PostForm)

    def test_post_correct_saving_on_pages(self):
        """
        Проверка появления поста при создании на: главной странице,
        на странице выбранной группы, в профайле пользователя.
        """
        new_post = Post.objects.create(
            author=self.author,
            group=self.group,
            text='Текст для проверки корректности отражения поста.',
        )
        reverses = {
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': (self.group.slug)}),
            reverse(
                'posts:profile', kwargs={'username': (self.author.username)}
            ),
        }
        for url in reverses:
            with self.subTest(reverse=url):
                response = self.client.get(url)
                posts = response.context['page_obj']
                self.assertEqual(new_post, posts[0])

    def test_post_in_the_right_group(self):
        """Проверка попадания нового поста в контекст своей группы."""
        new_post = Post.objects.create(
            author=self.author,
            group=self.group,
            text='Текст для проверки поста в контексте своей группы.',
        )
        other_group = Group.objects.create(
            description='Описание группы для проверки поста в контексте.',
            slug='test_group_slug',
            title='Тестовая группа для проверки поста в контексте'
        )
        response = self.client.get(
            reverse(
                'posts:group_posts', kwargs={'slug': (other_group.slug)}
            )
        )
        other_group_posts = response.context['page_obj'][:]
        self.assertNotIn(new_post, other_group_posts)

    def test_cache(self):
        """Проверка работы кэша."""
        post = Post.objects.create(
            author=self.author,
            group=self.group,
            text='Текст для тестового поста при проверке кэша.',
        )
        url = reverse('posts:index')
        response_1 = self.authorized_client.get(url)
        post.delete()
        response_2 = self.authorized_client.get(url)
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(url)
        self.assertNotEqual(response_3.content, response_1.content)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            description='Описание тестовой группы для проверки картинок.',
            slug='test_slug',
            title='Тестовая группа для проверки картинок'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Текст тестового поста с картинкой.',
            image=uploaded,
        )
        cls.ULRS = {
            reverse('posts:index'),
            reverse(
                'posts:group_posts', kwargs={'slug': (cls.group.slug)}
            ),
            reverse(
                'posts:profile', kwargs={'username': (cls.author.username)}
            ),
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_image_in_context(self):
        """Проверка наличия картинки в словаре context"""
        for url in self.ULRS:
            with self.subTest(reverse=url):
                response = self.client.get(url)
                posts = response.context['page_obj']
                self.assertIsInstance(posts, Page)

    def test_image_on_post_details_page(self):
        """Проверка наличия картинки в словаре context на странице поста"""
        url = reverse('posts:post_detail', kwargs={'post_id': (self.post.id)})
        response = self.client.get(url)
        post = response.context['post']
        self.assertEqual(post, self.post)


class PaginatorViewsTest(URLTests):
    """Тестирование пагинатора."""
    def test_paginator(self):
        posts_num = (constants.PAGINATOR_LIMIT
                     + random.randrange(1, constants.PAGINATOR_LIMIT + 1))
        posts = [
            Post(
                author=self.author,
                group=self.group,
                text=f'Пост №{i+1}'
            ) for i in range(posts_num)
        ]
        Post.objects.bulk_create(posts)
        posts_num = Post.objects.count()
        pages_num = math.ceil(posts_num / constants.PAGINATOR_LIMIT)
        posts_num_on_last_page = (
            posts_num - (constants.PAGINATOR_LIMIT * (pages_num - 1))
        )
        urls = [
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.author}/'
        ]
        for url in urls:
            for page_num in range(1, pages_num + 1):
                with self.subTest(url=url, page_num=page_num):
                    page_obj = self.client.get(
                        f'{url}?page={page_num}'
                    ).context.get('page_obj', False)
                    if page_num == pages_num:
                        self.assertEqual(
                            len(page_obj.object_list),
                            posts_num_on_last_page
                        )
                    else:
                        self.assertEqual(
                            len(page_obj.object_list),
                            constants.PAGINATOR_LIMIT
                        )


class FollowTests(TestCase):
    def setUp(self):
        self.authorized_client_author = Client()
        self.authorized_client_follower = Client()
        self.authorized_client_unfollower = Client()
        self.user_author = (User.objects.create(username='author'))
        self.user_follower = (User.objects.create(username='follower'))
        self.user_unfollower = (User.objects.create(username='unfollower'))
        self.post = Post.objects.create(
            author=self.user_author,
            text='Пост для тестирования подписки'
        )
        self.authorized_client_author.force_login(self.user_author)
        self.authorized_client_follower.force_login(self.user_follower)
        self.authorized_client_unfollower.force_login(self.user_unfollower)

    def test_follow(self):
        """Тестирование подписки"""
        self.authorized_client_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), 1)

    def test_unfollow(self):
        """Тестирование отписки"""
        self.authorized_client_follower.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_new_post_displays_correctly_for_any_user(self):
        """
        Тестирование появления нового поста на странице подписчика и
        отсутствие на странице не подписанного пользователя
        """
        Follow.objects.create(
            author=self.user_author,
            user=self.user_follower
        )
        response_1 = self.authorized_client_follower.get(
            reverse('posts:follow_index')
        )
        response_2 = self.authorized_client_unfollower.get(
            reverse('posts:follow_index')
        )
        self.assertContains(response_1, self.post.text)
        self.assertNotContains(response_2, self.post.text)
