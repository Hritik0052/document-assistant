from asgiref.sync import sync_to_async
from django.contrib import messages
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

async_render = sync_to_async(render, thread_sensitive=True)
async_redirect = sync_to_async(redirect, thread_sensitive=True)
async_render_to_string = sync_to_async(render_to_string, thread_sensitive=True)
async_add_message = sync_to_async(messages.add_message, thread_sensitive=True)


async def success_message(request, text: str) -> None:
    await async_add_message(request, messages.SUCCESS, text)


async def error_message(request, text: str) -> None:
    await async_add_message(request, messages.ERROR, text)
