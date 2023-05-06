from django.test import TestCase

from posts.models import Group, Post, User
from posts.constants import POST_LIMIT


class TestModels(TestCase):
    """Тестирование моделей"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            description='Описание тестовой группы.',
            slug='test_slug',
            title='Тестовая группа'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Текст для тестового поста.',
        )

    def test_group_model(self):
        """Проверка метода __str__ для Group."""
        self.assertEqual(str(self.group), self.group.title)

    def test_post_str_method(self):
        """Проверка метода __str__ для Post."""
        self.assertEqual(str(self.post), self.post.text[:POST_LIMIT])

    def test_post_verbose_name(self):
        """Проверка verbose_name в Post."""
        fields_verbose_name = {
            'text': 'текст',
            'pub_date': 'дата публикации',
            'author': 'автор',
            'group': 'группа',
        }
        for value, expected in fields_verbose_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name, expected)

    def test_post_help_text(self):
        """Проверка help_text в Post."""
        fields_help_text = {
            'pub_date': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for value, expected in fields_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text, expected)
