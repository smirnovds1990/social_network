from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляетс дату создания."""
    created = models.DateTimeField(
        verbose_name='дата создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True
