import threading
from pathlib import Path

from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib import messages
from django.db import connections
from django.http import HttpResponse
from django.shortcuts import aget_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from core.auth import async_login_required
from core.pydantic import FormError, parse_form
from documents.models import Conversation, Document, Message
from documents.schemas import AskSchema
from rag.pipeline import answer_question, ingest_document


def _file_type_for(name: str) -> str | None:
    suffix = Path(name).suffix.lower()
    return {'.pdf': 'pdf', '.txt': 'txt', '.docx': 'docx'}.get(suffix)


def _start_ingest(document_id: int) -> None:
    try:
        async_to_sync(ingest_document)(document_id)
    finally:
        connections.close_all()


@async_login_required
async def library(request):
    user = await request.auser()
    docs = [doc async for doc in Document.objects.filter(user=user)]
    return render(request, 'documents/library.html', {'documents': docs})


@async_login_required
@require_http_methods(['POST'])
async def upload(request):
    user = await request.auser()
    uploaded = request.FILES.get('file')
    if not uploaded:
        messages.error(request, 'Choose a PDF, Word, or text file to upload.')
        return redirect('documents:library')

    file_type = _file_type_for(uploaded.name)
    if file_type is None:
        messages.error(request, 'Only .pdf, .txt, and .docx files are supported.')
        return redirect('documents:library')

    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if uploaded.size > max_bytes:
        messages.error(request, f'File is too large. Maximum size is {settings.MAX_UPLOAD_MB} MB.')
        return redirect('documents:library')

    title = Path(uploaded.name).stem
    document = await Document.objects.acreate(
        user=user,
        title=title,
        file=uploaded,
        original_name=uploaded.name,
        file_type=file_type,
        status=Document.Status.PENDING,
    )
    threading.Thread(target=_start_ingest, args=(document.pk,), daemon=True).start()
    messages.success(request, f'“{title}” is being processed. You can ask questions once it is ready.')
    return redirect('documents:chat', pk=document.pk)


@async_login_required
async def chat(request, pk: int):
    user = await request.auser()
    document = await aget_object_or_404(Document.objects.filter(user=user), pk=pk)
    conversation, _created = await Conversation.objects.aget_or_create(user=user, document=document)
    history = [message async for message in conversation.messages.all()]
    docs = [doc async for doc in Document.objects.filter(user=user)]
    return render(request, 'documents/chat.html', {
        'document': document,
        'documents': docs,
        'conversation': conversation,
        'chat_messages': history,
    })


@async_login_required
async def document_status(request, pk: int):
    user = await request.auser()
    document = await aget_object_or_404(Document.objects.filter(user=user), pk=pk)
    html = render_to_string('documents/partials/status_badge.html', {'document': document}, request=request)
    response = HttpResponse(html)
    if document.status in {Document.Status.READY, Document.Status.FAILED}:
        response['HX-Refresh'] = 'true'
    return response


@async_login_required
@require_http_methods(['POST'])
async def ask(request, pk: int):
    user = await request.auser()
    document = await aget_object_or_404(Document.objects.filter(user=user), pk=pk)
    conversation, _created = await Conversation.objects.aget_or_create(user=user, document=document)
    sources = []
    answer_text = ''

    try:
        payload = parse_form(AskSchema, request.POST)
    except FormError as exc:
        return render(request, 'documents/partials/ask_error.html', {
            'error': next(iter(exc.errors.values()), 'Please enter a question.'),
        }, status=400)

    if document.status != Document.Status.READY:
        return render(request, 'documents/partials/ask_error.html', {
            'error': 'This document is not ready yet. Wait until processing finishes.',
        }, status=409)

    question = payload.cleaned_question
    await Message.objects.acreate(
        conversation=conversation,
        role=Message.Role.USER,
        content=question,
    )

    try:
        result = await answer_question(document, question)
        answer_text = result.answer
        sources = result.sources
    except Exception as exc:
        answer_text = f'Could not generate an answer yet: {exc}'

    await Message.objects.acreate(
        conversation=conversation,
        role=Message.Role.ASSISTANT,
        content=answer_text,
    )
    await conversation.asave(update_fields=['updated_at'])

    return render(request, 'documents/partials/message_pair.html', {
        'question': question,
        'answer': answer_text,
        'sources': sources,
    })


@async_login_required
@require_http_methods(['POST'])
async def delete_document(request, pk: int):
    user = await request.auser()
    document = await aget_object_or_404(Document.objects.filter(user=user), pk=pk)
    title = document.title
    await document.adelete()
    messages.success(request, f'“{title}” was deleted.')
    return redirect('documents:library')
