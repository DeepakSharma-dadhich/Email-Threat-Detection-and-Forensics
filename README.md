# Email Threat Detection Platform — Batch 1

Batch 1 implements the ingestion foundation:

`.eml upload -> source adapter -> raw preservation -> parser -> normalized Common Email Object -> PostgreSQL -> FastAPI APIs`

## Intentionally not included in Batch 1

- SPF/DKIM/DMARC and header-risk analysis
- AI/NLP phishing analysis
- IOC reputation or risk scoring
- Browser isolation / URL sandbox execution
- Final aggregate risk score / verdict
- Production Gmail ingestion
- React dashboard wiring

Those modules consume the stable Batch 1 contracts instead of rewriting the ingestion/parser files.

## Run

### 1. Start PostgreSQL

```bash
docker compose up -d postgres
```

### 2. Backend

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
python -m uvicorn app.main:app --reload
```

Open:

- Swagger: `http://127.0.0.1:8000/docs`
- Health: `GET /api/v1/health`

## Batch 1 API

### Upload a test `.eml`

`POST /api/v1/test-lab/emails`

Multipart field:

- `file`: `.eml`

### Read normalized email

`GET /api/v1/emails/{email_id}`

### List ingested emails

`GET /api/v1/emails?limit=50&offset=0`

## Storage

Raw and extracted artifacts are stored under:

```text
backend/data/
└── emails/
    └── <email_id>/
        ├── raw.eml
        └── attachments/
            └── <attachment_id>_<safe_filename>
```

The database stores storage keys, hashes, metadata and normalized email content.

## Run tests

```bash
cd backend
pytest -q
```
