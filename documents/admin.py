from django.contrib import admin

from documents.models import Conversation, Document, DocumentChunk, Message


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'file_type', 'status', 'chunk_count', 'created_at')
    list_filter = ('status', 'file_type')
    search_fields = ('title', 'original_name', 'user__username')


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document', 'chunk_index', 'token_count', 'created_at')
    list_filter = ('document',)


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'document', 'updated_at')
    inlines = [MessageInline]
