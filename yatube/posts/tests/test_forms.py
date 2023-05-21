import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            description='Описание тестовой группы для проверки форм.',
            slug='test_slug',
            title='Тестовая группа для проверки форм'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Текст для тестового поста при проверке формы.',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_post_create_function(self):
        """Проверка работы функции при создании поста"""
        all_posts = set(Post.objects.all())
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
        form_data = {
            'group': self.group.id,
            'text': 'Отредактированный текст поста.',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        all_posts_with_new_one = set(Post.objects.all())
        difference_between_posts = (
            len(all_posts_with_new_one)
            - len(all_posts)
        )
        self.assertEqual(difference_between_posts, 1)
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'author'})
        )
        self.assertTrue(
            Post.objects.filter(
                author=self.author,
                group=self.group.id,
                text=form_data['text'],
                image='posts/small.gif',
            ).exists()
        )

    def test_post_edit_form(self):
        """Проверка работы функции при редактировании поста"""
        all_posts = Post.objects.count()
        edited_group = Group.objects.create(
            description='Описание тестовой группы для редактирования поста.',
            slug='test_edit_slug',
            title='Тестовая группа для редактирования поста'
        )
        form_data = {
            'group': edited_group.id,
            'text': 'Отредактированный текст поста.'
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': (self.post.id)}),
            data=form_data,
            follow=True
        )
        all_posts_after_editing = Post.objects.count()
        self.assertTrue(
            Post.objects.filter(
                author=self.author,
                group=form_data['group'],
                text=form_data['text'],
                id=self.post.id,
            ).exists()
        )
        self.assertEqual(all_posts, all_posts_after_editing)

    def test_comments_display_on_page(self):
        """Проверка появления комментария на странице поста"""
        all_comments = set(Comment.objects.all())
        form_data = {
            'text': 'Текст тестового комментария.',
        }
        comment_creation = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': (self.post.id)}),
            data=form_data,
            follow=True
        )
        comments_with_new_one = set(Comment.objects.all())
        difference_between_comments = comments_with_new_one - all_comments
        self.assertEqual(len(difference_between_comments), 1)
        self.assertRedirects(
            comment_creation,
            reverse('posts:post_detail', kwargs={'post_id': (self.post.id)})
        )
        for new_comment in difference_between_comments:
            self.assertEqual(new_comment.author, self.author)
            self.assertEqual(new_comment.post, self.post)
            self.assertEqual(new_comment.text, form_data['text'])
        
    def test_comments_allowed_only_authorized_clients(self):
        """
        Проверка возможности комментирования только авторизированным
        пользователям
        """
        comments_quantity = Comment.objects.count()
        form_data = {
            'text': 'Текст тестового комментария.',
        }
        self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': (self.post.id)}),
            data=form_data,
            follow=True
        )
        added_comments = Comment.objects.count()
        self.assertEqual(added_comments, comments_quantity)
