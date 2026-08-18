from django.conf import settings
from django.db import models

from documents.fields import EmbeddingField


class Document(models.Model):
    class FileType(models.TextChoices):
        PDF = 'pdf', 'PDF'
        TXT = 'txt', 'Text'
        DOCX = 'docx', 'Word'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        READY = 'ready', 'Ready'
        FAILED = 'failed', 'Failed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/%Y/%m/')
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FileType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True)
    chunk_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.PositiveIntegerField()
    content = models.TextField()
    token_count = models.PositiveIntegerField(default=0)
    embedding = EmbeddingField(dimensions=settings.EMBEDDING_DIMENSIONS, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['chunk_index']
        unique_together = [('document', 'chunk_index')]

    def __str__(self):
        return f'{self.document_id} #{self.chunk_index}'


class Conversation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations',
    )
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'Conversation {self.pk} · {self.document.title}'


class Message(models.Model):
    class Role(models.TextChoices):
        USER = 'user', 'User'
        ASSISTANT = 'assistant', 'Assistant'

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:40]}'
