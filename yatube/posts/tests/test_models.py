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

    def test_str_method_for_post_and_group_models(self):
        """Проверка метода __str__ для Post и Group."""
        data = {
            self.group: self.group.title,
            self.post: self.post.text[:POST_LIMIT],
        }
        for value, expected in data.items():
            with self.subTest(value=value):
                self.assertEqual(str(value), expected)

    def test_post_verbose_name(self):
        """Проверка verbose_name в Post."""
        fields_verbose_name = {
            'text': 'текст',
            'created': 'дата создания',
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
            'group': 'Группа, к которой будет относиться пост'
        }
        for value, expected in fields_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text, expected)
