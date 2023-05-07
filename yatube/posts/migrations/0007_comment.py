# Generated by Django 2.2.16 on 2023-04-29 13:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0006_auto_20230426_1418'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='текст комментария')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Ваш комментарий здесь', verbose_name='дата публикации комментария')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='автор комментария')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Post', verbose_name='комментарии')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'КОмментарии',
                'ordering': ['-created'],
            },
        ),
    ]