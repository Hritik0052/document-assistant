"""
Quick OpenRouter embedding smoke test (no Django required).

Usage:
  python scripts/test_openrouter_embeddings.py
  python scripts/test_openrouter_embeddings.py --text "hello world"
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key.strip(), value)


def main() -> int:
    parser = argparse.ArgumentParser(description='Test OpenRouter embedding API')
    parser.add_argument(
        '--text',
        nargs='+',
        default=['This is a small test sentence for RAG embeddings.'],
        help='One or more strings to embed',
    )
    parser.add_argument('--model', default=None, help='Override OPENROUTER_EMBEDDING_MODEL')
    args = parser.parse_args()

    load_dotenv(ROOT / '.env')

    api_key = os.environ.get('OPEN_ROUTER_API_KEY') or os.environ.get('OPENROUTER_API_KEY', '')
    base_url = os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1').rstrip('/')
    model = args.model or os.environ.get(
        'OPENROUTER_EMBEDDING_MODEL',
        'nvidia/nemotron-3-embed-1b:free',
    )
    texts = args.text

    print('=== OpenRouter embedding smoke test ===')
    print(f'base_url: {base_url}')
    print(f'model:    {model}')
    print(f'key_set:  {bool(api_key)}')
    print(f'inputs:   {len(texts)} text(s)')
    for i, text in enumerate(texts, start=1):
        preview = text if len(text) <= 80 else text[:77] + '...'
        print(f'  [{i}] {preview!r}')
    print()

    if not api_key:
        print('ERROR: OPEN_ROUTER_API_KEY is missing from .env')
        return 1

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:8000',
        'X-Title': 'RAG Embedding Test',
    }
    payload = {
        'model': model,
        'input': texts if len(texts) > 1 else texts[0],
        'encoding_format': 'float',
    }

    started = time.perf_counter()
    try:
        with httpx.Client(timeout=90.0) as client:
            print('1) Checking API key...')
            key_resp = client.get(f'{base_url}/key', headers=headers)
            print(f'   GET /key -> {key_resp.status_code}')
            if key_resp.status_code != 200:
                print(f'   body: {key_resp.text[:400]}')
                return 1

            print('2) Requesting embeddings (encoding_format=float)...')
            embed_resp = client.post(
                f'{base_url}/embeddings',
                headers=headers,
                json=payload,
            )
            elapsed = time.perf_counter() - started
            print(f'   POST /embeddings -> {embed_resp.status_code} ({elapsed:.2f}s)')

            if embed_resp.status_code != 200:
                print(f'   ERROR body: {embed_resp.text[:600]}')
                return 1

            data = embed_resp.json()
            items = sorted(data.get('data', []), key=lambda item: item.get('index', 0))
            if not items:
                print('   ERROR: response has no embedding data')
                print(json.dumps(data, indent=2)[:800])
                return 1

            print('3) Results')
            for item in items:
                vec = item.get('embedding') or []
                print(f'   index={item.get("index", "?")} dim={len(vec)} '
                      f'sample=[{vec[0]:.6f}, {vec[1]:.6f}, {vec[2]:.6f}, ...]')

            print()
            print('SUCCESS: OpenRouter returned embeddings.')
            return 0
    except httpx.TimeoutException:
        print(f'ERROR: request timed out after {time.perf_counter() - started:.1f}s')
        return 1
    except Exception as exc:
        print(f'ERROR: {type(exc).__name__}: {exc}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
