# PaperQ — Document Q&A RAG

Upload a PDF, Word, or text file. Ask questions. Answers come **only from that file**, not from the open internet.

PaperQ is a Retrieval-Augmented Generation (RAG) web app: extract text → chunk → embed → search similar chunks → generate a grounded answer.

---

## Problem it solves

People often have notes, reports, contracts, or study material and still have to search the file by hand. Generic chatbots also invent answers from outside knowledge.

PaperQ keeps Q&A on **your uploaded document**:

- Upload `.pdf`, `.txt`, or `.docx`
- Search by meaning (embeddings + pgvector), not just keywords
- Answer only from retrieved chunks
- If the answer is not in the file, the assistant says it does not know

---

## Who can use it / target users

| User | How they use it |
| --- | --- |
| Students | Ask questions on lecture notes or textbooks |
| Researchers | Query papers and reports without rereading everything |
| Developers / learners | Study a Django + RAG + pgvector example |
| Knowledge workers | Query PDFs, Word docs, and notes they already have |
| Small teams | Local or self-hosted document Q&A without a paid LLM (free OpenRouter models) |

This is a **single-user / small-team demo**, not a multi-tenant SaaS. Each account sees only their own files.

---

## Tech stack

| Layer | Choice |
| --- | --- |
| Language | Python 3.14+ |
| Web framework | Django 6 (async views, session auth) |
| Validation | Pydantic v2 (forms / RAG schemas — **no DRF, no serializers**) |
| UI | Django templates + Tailwind CSS (CDN) + HTMX |
| Themes | light, dark, ocean, forest, sunset |
| Database | Neon Postgres (pooled) + **pgvector** |
| Fallback DB | SQLite if `DATABASE_URL` is empty (dev UI only; vectors stored as JSON) |
| Embeddings | OpenRouter `nvidia/nemotron-3-embed-1b:free` (2048 dimensions) |
| Chat | OpenRouter `openrouter/free` (routes to a $0 model) |
| File loaders | `pypdf` (PDF), `python-docx` (Word), UTF-8 read (TXT) |
| HTTP / LLM client | `openai` SDK pointed at `https://openrouter.ai/api/v1` + `httpx` |
| Static files | WhiteNoise |
| ASGI server | Uvicorn (optional; `runserver` works for local use) |

**Not used:** Django REST Framework, token APIs, React.

---

## How it works (RAG pipeline)

```
Upload file
    → Extract text (PDF / TXT / DOCX loaders)
    → Clean + chunk (~700 words, 15% overlap)
    → Embed chunks via OpenRouter (2048-d vectors)
    → Store vectors in Neon pgvector
Ask a question
    → Embed the question
    → Cosine similarity search (top-k chunks, min similarity)
    → Chat model answers only from those chunks
    → Save conversation history
```

Document statuses: `pending` → `processing` → `ready` or `failed`.

You can ask questions only when status is **Ready**.

---

## Requirements

### Software

- Python **3.14+** (3.12+ should work)
- `pip` / a virtualenv
- Git (optional)
- A browser

### External accounts / APIs

| Service | Why | Cost |
| --- | --- | --- |
| [Neon](https://neon.tech) | Postgres + pgvector | Free tier is enough |
| [OpenRouter](https://openrouter.ai) | Embeddings + chat | Free models (`:free` / `openrouter/free`) |

OpenRouter free models are **rate-limited** (often ~20 requests/minute). Large files take longer because embeddings are sent in batches of 16 chunks.

### Hardware

A normal laptop is enough. Embeddings run on OpenRouter, not on your GPU.

---

## Project layout

```
RAG System/
├── accounts/          # Register, login, logout (session auth)
├── core/              # Themes, Pydantic form helper, async HTTP helpers
├── documents/         # Library, upload, chat, models, management commands
├── rag/               # Loaders, chunking, embeddings, retrieve, generate
│   └── loaders/       # pdf.py, txt.py, docx.py
├── scripts/           # Standalone OpenRouter embedding smoke test
├── templates/         # Tailwind layouts + reusable components
├── static/            # themes.css, app.js
├── config/            # Django settings, env (Pydantic), URLs
├── manage.py
├── requirements.txt
└── .env.example
```

---

## Setup

### 1. Clone and enter the project

```powershell
cd "C:\Users\Dell\Desktop\RAG System"
```

### 2. Create and activate a virtualenv

PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks scripts:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\venv\Scripts\Activate.ps1
```

Command Prompt:

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create `.env`

```powershell
copy .env.example .env
```

Fill in at least:

```env
SECRET_KEY=replace-with-a-long-random-string
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgresql://USER:PASSWORD@HOST/neondb?sslmode=require

OPEN_ROUTER_API_KEY=sk-or-v1-your-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_CHAT_MODEL=openrouter/free
OPENROUTER_EMBEDDING_MODEL=nvidia/nemotron-3-embed-1b:free
EMBEDDING_DIMENSIONS=2048
```

**Never commit `.env`.** It is gitignored.

### 5. Neon Postgres + pgvector

1. Create a project at [neon.tech](https://neon.tech)
2. Copy the **pooled** connection string into `DATABASE_URL`
3. In Neon’s SQL Editor run once:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

If `DATABASE_URL` is empty, Django uses local SQLite so you can still open the UI. Embeddings need Postgres + pgvector for production-quality retrieval.

### 6. OpenRouter

1. Create an account at [openrouter.ai](https://openrouter.ai)
2. Create an API key
3. Put it in `OPEN_ROUTER_API_KEY` (or `OPENROUTER_API_KEY`)

Chat and embedding slugs **must** be free:

- chat: `openrouter/free` or any model ending in `:free`
- embeddings: `nvidia/nemotron-3-embed-1b:free` (2048 dimensions)

Paid models are rejected at startup.

### 7. Migrate and run

```powershell
python manage.py migrate
python manage.py check
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

Register an account, then go to **Library**.

Optional ASGI:

```powershell
python -m uvicorn config.asgi:application --reload
```

---

## How to use the app

1. **Register / sign in** at `/` or `/register/`
2. Open **Library** (`/library/`)
3. Drop or select a `.pdf`, `.txt`, or `.docx` (default max **10 MB**)
4. Wait until the badge is **Ready** (status polls every 2 seconds)
5. Open the file and ask a question that is **in the document**
6. Read the answer and optional source chunk scores
7. Delete a file from the library when you no longer need it
8. Switch theme (light / dark / ocean / forest / sunset) from the sidebar

If processing **Failed**, the error message is shown on the chat header (for example missing API key, empty text, or vector dimension mismatch).

---

## Environment variables

| Variable | Required | Default | Meaning |
| --- | --- | --- | --- |
| `SECRET_KEY` | Yes (prod) | insecure dev default | Django secret |
| `DEBUG` | No | `True` | Debug mode |
| `ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Comma-separated hosts |
| `DATABASE_URL` | Yes (RAG) | empty → SQLite | Neon pooled Postgres URL |
| `OPEN_ROUTER_API_KEY` | Yes (RAG) | empty | OpenRouter key |
| `OPENROUTER_BASE_URL` | No | `https://openrouter.ai/api/v1` | API base |
| `OPENROUTER_CHAT_MODEL` | No | `openrouter/free` | Must be free |
| `OPENROUTER_EMBEDDING_MODEL` | No | `nvidia/nemotron-3-embed-1b:free` | Must be free |
| `EMBEDDING_DIMENSIONS` | No | `2048` | Must match the embedding model |
| `RAG_CHUNK_TOKENS` | No | `700` | Chunk size (word estimate) |
| `RAG_CHUNK_OVERLAP` | No | `0.15` | Overlap ratio |
| `RAG_TOP_K` | No | `5` | Chunks retrieved per question |
| `RAG_MIN_SIMILARITY` | No | `0.25` | Drop weak matches |
| `MAX_UPLOAD_MB` | No | `10` | Upload size limit |
| `DEFAULT_THEME` | No | `light` | UI theme |

---

## Python dependencies

From `requirements.txt`:

| Package | Role |
| --- | --- |
| `Django` | Web app |
| `pydantic` / `pydantic-settings` | Env + form/RAG schemas |
| `email-validator` | Register email validation |
| `dj-database-url` | Parse `DATABASE_URL` |
| `psycopg[binary]` | Postgres driver |
| `pgvector` | Vector column + cosine distance |
| `openai` | OpenAI-compatible OpenRouter client |
| `pypdf` | PDF text extraction |
| `python-docx` | Word `.docx` extraction |
| `httpx` | HTTP (smoke tests / client) |
| `uvicorn[standard]` | ASGI server |
| `whitenoise` | Serve static files |

---

## External APIs

### OpenRouter

Base URL: `https://openrouter.ai/api/v1`

The app uses the OpenAI-compatible SDK (`AsyncOpenAI`) with that base URL.

| Call | Endpoint | Model |
| --- | --- | --- |
| Key check (scripts) | `GET /key` | — |
| Embeddings | `POST /embeddings` | `nvidia/nemotron-3-embed-1b:free` |
| Chat | `POST /chat/completions` | `openrouter/free` |

Embeddings **must** use `encoding_format=float` (NVIDIA rejects `base64`).

Headers sent:

- `Authorization: Bearer <key>`
- `HTTP-Referer: http://localhost:8000`
- `X-Title: RAG Document Q&A`

### Neon / Postgres

No HTTP API from the app. Django talks to Postgres over `DATABASE_URL`.

Required extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Chunk embeddings are stored as `vector(2048)` on `documents_documentchunk.embedding`.

If you change embedding models, the vector size must match. A 1536-d column cannot store 2048-d vectors.

---

## App routes (pages, not a public JSON API)

There is **no REST API**. Everything is HTML + HTMX + sessions.

| Method | Path | What it does |
| --- | --- | --- |
| GET/POST | `/` | Sign in |
| GET/POST | `/register/` | Create account |
| POST | `/logout/` | Sign out |
| GET | `/library/` | Document library |
| POST | `/library/upload/` | Upload file and start ingest |
| GET | `/library/<id>/` | Chat with a document |
| GET | `/library/<id>/status/` | HTMX status badge poll |
| POST | `/library/<id>/ask/` | Ask a question |
| POST | `/library/<id>/delete/` | Delete document + chunks |
| POST | `/theme/` | Save theme cookie |
| GET | `/admin/` | Django admin |

---

## Useful commands

```powershell
# Install
pip install -r requirements.txt

# Database
python manage.py migrate
python manage.py check

# Run
python manage.py runserver

# Tests (chunking; live OpenRouter skipped unless env is set)
python manage.py test documents

# Prove OpenRouter embeddings work (no Django)
python scripts/test_openrouter_embeddings.py
python scripts/test_openrouter_embeddings.py --text "hello from PaperQ"

# Same embedding path the app uses
python manage.py test_embeddings
python manage.py test_embeddings --text "test paragraph"

# Re-run ingest for a stuck/failed document (id from /library/2/)
python manage.py ingest_document 2

# Admin user
python manage.py createsuperuser
```

Live embedding test:

```powershell
$env:RUN_LIVE_EMBEDDING_TEST="1"
python manage.py test documents.tests.EmbeddingIntegrationTests
```

---

## Limits and defaults

- File types: `.pdf`, `.txt`, `.docx`
- Max size: `MAX_UPLOAD_MB` (default 10)
- Question length: 3–2000 characters (Pydantic)
- Chunk size: ~700 words, 15% overlap
- Embed batch size: 16
- Retrieval: top 5 chunks, min cosine similarity 0.25
- Embedding vector size: **2048**
- Free OpenRouter rate limits apply

A short `.txt` often becomes Ready in seconds. A large text file can take 1–3 minutes because of many chunks and free-tier limits.

---

## Troubleshooting

**Processing never becomes Ready**  
Restart `runserver`, watch the terminal for `Ingest started` / `Extracted N chunks` / `Embedding batch`. Then re-upload, or run `python manage.py ingest_document <id>`.

**`expected 1536 dimensions, not 2048`**  
The table was created for an older embedding size. Run migrations (includes `0002_resize_embedding_to_2048`) and re-ingest the file.

**`Nvidia embeddings do not support base64`**  
The app already sends `encoding_format=float`.

**OpenRouter 429**  
You hit the free rate limit. Wait and retry; ingest retries 429s a few times.

**Empty / failed extract**  
Scanned PDFs with no selectable text cannot be chunked. Use a text PDF, `.txt`, or `.docx`.

**SQLite instead of Neon**  
`DATABASE_URL` is missing or empty. Set the Neon pooled URL and migrate again.

**Broken pipe on `/library/<id>/status/`**  
Harmless: HTMX polls status every 2 seconds while processing.

---

## License

Use this project for learning and internal document Q&A. You are responsible for your Neon data, OpenRouter usage, and any files you upload.

Do not upload confidential data to free OpenRouter endpoints if the provider’s terms disallow it.
