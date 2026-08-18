from django.conf import settings
from django.db import models


def _is_postgres() -> bool:
    engine = settings.DATABASES['default']['ENGINE']
    return 'postgresql' in engine or 'postgres' in engine


if _is_postgres():
    from pgvector.django import VectorField as PgVectorField

    class EmbeddingField(PgVectorField):
        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            return name, 'documents.fields.EmbeddingField', args, kwargs
else:
    class EmbeddingField(models.JSONField):
        """SQLite-safe stand-in until Neon/pgvector is connected."""

        def __init__(self, dimensions=None, **kwargs):
            kwargs.setdefault('null', True)
            kwargs.setdefault('blank', True)
            super().__init__(**kwargs)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            kwargs.pop('dimensions', None)
            return name, 'documents.fields.EmbeddingField', args, kwargs
