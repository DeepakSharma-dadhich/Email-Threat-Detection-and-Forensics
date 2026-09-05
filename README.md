Email Threat Detection and Forensics Platform

An end-to-end Email Security and Forensic Intelligence Platform built to ingest, analyze, investigate, classify, and manage suspicious emails.

The system combines email header forensics, phishing/social-engineering analysis, IOC extraction, static URL/domain intelligence, external threat-intelligence enrichment, risk scoring, lifecycle management, Gmail integration, investigation APIs, and authentication in one modular backend.

The project is being developed as a production-style MCA/SIH-level security system rather than a simple phishing classifier.

Table of Contents

Project Goal

Why This Project

Current Architecture

How the Complete Flow Works

Main Security Modules

Risk and Decision Engine

Email Lifecycle

Gmail Integration

Authentication

Browser Isolation Integration

Technology Stack

Repository Structure

Getting Started

Environment Configuration

Database Setup

Running the Backend

API Overview

Testing

Team Development Workflow

Security Rules for Contributors

Current Development Status

Roadmap

Troubleshooting

Project Design Principles

Disclaimer

Project Goal

The goal of this project is to build a complete platform that can answer questions such as:

Is this email legitimate or suspicious?

Has the sender identity been spoofed?

Are SPF, DKIM, or DMARC signals suspicious?

Does the message contain phishing or social-engineering language?

What URLs, domains, IPs, emails, attachments, and hashes are present?

Are any indicators suspicious according to static or external intelligence?

What is the final risk score?

Should the message be allowed, reviewed, quarantined, or blocked?

What evidence supports the final verdict?

Can an analyst investigate the email later?

Should a suspicious URL be sent to a separate Browser Isolation service?

The platform is designed to provide both a security decision and the forensic evidence behind that decision.

Why This Project

Modern email attacks are not limited to obvious phishing links.

Attackers may use:

Sender spoofing

Domain impersonation

Business Email Compromise (BEC)

Credential theft

Financial fraud

Malicious links

Malicious attachments

Redirect chains

Social engineering

Urgency and pressure

Reply-To manipulation

Return-Path mismatch

Suspicious sender infrastructure

Newly registered or unusual domains

A single detection technique is not sufficient.

For this reason, the project uses multiple independent analysis modules and combines their results using a central decision engine.

Current Architecture

Email Source
     ↓
Source Adapter
     ↓
Email Ingestion Service
     ↓
Email Parser
     ↓
Common Email Object
     ↓
Analysis Orchestrator
     │
     ├── Header Forensics
     │
     ├── NLP / Social Engineering Analysis
     │
     └── IOC Extraction
     │          ↓
     │     Static IOC Intelligence
     │          ↓
     │     External Threat Intelligence
     │
     ↓
Final Risk / Decision Engine
     ↓
Email Lifecycle / Policy Engine
     ↓
PostgreSQL
     ↓
Mailbox / Investigation / Reports / Dashboard APIs

A separate Browser Isolation project will later be connected through an API for dynamic URL analysis.

How the Complete Flow Works

1. Email Source

An email can currently enter the platform from:

.eml test files

Gmail

Future sources may include:

Outlook

Microsoft 365

IMAP sources

Security gateways

All sources should eventually produce the same internal email structure.

2. Source Adapter

Each email source is handled by an adapter.

EML File
   ↓
EML Adapter

Gmail
   ↓
Gmail Adapter

The adapter converts source-specific data into a format that the rest of the system can process. This prevents the security modules from depending directly on Gmail or .eml.

3. Email Ingestion

The ingestion layer is responsible for:

Accepting raw email data

Preserving the original email

Creating a unique email ID

Passing raw data to the parser

Saving parsed email data into PostgreSQL

Saving extracted attachments

The original raw email is preserved for forensic purposes.

4. Email Parser

The parser converts an email into a normalized internal representation.

Important data includes:

Message-ID

Subject

From

Reply-To

Return-Path

To

CC

BCC

Date

Raw headers

Plain-text body

HTML body

Attachments

Attachment hashes

Parse warnings

Source information

This normalized object is called the Common Email Object.

Main Security Modules

1. Header Forensics

The Header Forensics module analyzes email identity and delivery information.

It checks:

SPF

DKIM

DMARC

Authentication-Results

Received-SPF

From domain

Reply-To domain

Return-Path domain

Message-ID domain

Sender alignment

Missing headers

Received chain

Relay hops

IP addresses in routing headers

Example suspicious case:

From: security@company.com
Reply-To: attacker@example.net

or:

DMARC = fail
SPF = fail
DKIM = fail

The module produces a module score, confidence, findings, evidence, and metadata.

2. NLP / Social Engineering Analysis

The current NLP module is a deterministic phishing and social-engineering analysis engine.

It detects categories such as:

Urgency

Credential requests

Financial requests

Threat or pressure

Secrecy

Impersonation / BEC

Link-action requests

Example suspicious message:

Your account will be suspended immediately.
Verify your password using the link below.

Possible categories:

urgency
credential_request
link_action
threat_pressure

The current engine is rule-based and explainable. Future versions may add trained ML/NLP models without replacing the existing deterministic analysis.

3. IOC Extraction

IOC means Indicator of Compromise.

The IOC Extractor collects security-relevant indicators from an email:

URLs

Domains

IP addresses

Email addresses

Attachments

SHA-256 hashes

Important design rule:

The IOC Extractor only extracts indicators. It does not decide whether they are malicious.

Risk analysis is performed by other modules.

4. Static IOC Intelligence

After IOC extraction, static intelligence analyzes indicators without requiring an external service.

URL checks include:

HTTP instead of HTTPS

IP-literal URLs

URL shorteners

Punycode

Suspicious keywords

Too many subdomains

@ user-info tricks

Executable extensions

Long URLs

Encoded characters

Suspicious URL structure

This allows the core platform to function even if external APIs are unavailable.

5. External Threat Intelligence

The project includes a provider-based threat-intelligence architecture.

Implemented providers include:

DNS Intelligence

RDAP Intelligence

VirusTotal

Google Safe Browsing

DNS Intelligence

Provides infrastructure information such as A, AAAA, and MX records.

RDAP Intelligence

Provides domain-registration context. Subdomains are normalized to their registrable/root domain before RDAP lookup where appropriate.

VirusTotal

Can provide external reputation information for domains and URLs.

Google Safe Browsing

Can detect URLs matching known threat lists.

External services are optional. If API keys are unavailable, the core email analysis pipeline still works.

Risk and Decision Engine

The final risk engine combines security scores from the main decision-producing modules.

Current weights:

Header Forensics            30%
NLP Analysis                30%
IOC Static Intelligence     40%

IOC Extraction is not included in weighted scoring because it is an extraction module.

The engine can also apply cross-module amplification when multiple independent modules detect suspicious behavior.

Verdict Levels

Score 0-19
Safe
Action: Allow

Score 20-39
Low Risk
Action: Allow With Monitoring

Score 40-59
Suspicious
Action: Review

Score 60-79
High Risk
Action: Quarantine

Score 80-100
Malicious
Action: Block

The engine also determines whether Browser Isolation should be recommended for suspicious URLs.

Email Lifecycle

A verdict is different from an operational mailbox state.

The lifecycle engine manages actual application states:

Inbox
Review
Quarantine
Blocked

Examples:

allow → inbox
review → review
quarantine → quarantine
block → blocked

Manual analyst actions are also supported:

Manual allow

Manual quarantine

Manual block

Manual review

Release

Restore

Every lifecycle change is recorded in an action-history table, creating an audit trail.

Gmail Integration

The platform supports live Gmail integration using Google OAuth 2.0.

Current Gmail access is:

gmail.readonly

This allows the system to:

Authenticate a Gmail account

Fetch message metadata

Fetch raw Gmail messages

Import Gmail messages

Process Gmail messages through the same security pipeline used for .eml

Current Gmail processing flow:

Gmail Message
     ↓
Fetch Raw Message
     ↓
Gmail Adapter
     ↓
Existing Email Ingestion
     ↓
Parser
     ↓
Security Analysis
     ↓
Risk Engine
     ↓
Lifecycle

Gmail passwords are never collected or stored.

OAuth credentials and tokens must never be committed to GitHub.

Authentication

The application has its own user authentication. Application authentication and Gmail OAuth are separate systems.

Application Login

Signup
Name + Email + Password
        ↓
bcrypt Password Hash
        ↓
User Stored in PostgreSQL
        ↓
Login
        ↓
JWT Access Token
        ↓
Protected Application APIs

Currently implemented:

User signup

Email/password login

bcrypt password hashing

JWT access token

Current-user endpoint

Duplicate account handling

Invalid credential handling

Main endpoints:

POST /api/v1/auth/signup
POST /api/v1/auth/login
GET  /api/v1/auth/me

Multi-user ownership integration is the next backend step.

Browser Isolation Integration

Browser Isolation is intentionally being developed as a separate project/service. It is not embedded directly inside this repository.

Planned flow:

Email Security Platform
        ↓
Suspicious URL Detected
        ↓
Risk Engine Determines
Dynamic Analysis Needed
        ↓
Browser Isolation API
        ↓
Isolated Browser / Sandbox
        ↓
Dynamic Evidence
        ↓
Email Security Platform
        ↓
Final Investigation Result

The Browser Isolation service can later collect redirects, network activity, DOM/HTML, JavaScript behavior, cookies, console logs, downloads, screenshots, and metadata.

Keeping it separate makes both projects easier to scale and maintain.

Technology Stack

Backend

Python

FastAPI

Uvicorn

SQLAlchemy

PostgreSQL

Alembic

Pydantic

Pydantic Settings

Authentication

bcrypt

PyJWT

Email Validator

Email Integration

Gmail API

Google OAuth 2.0

Python email parsing

Threat Intelligence

HTTPX

DNSPython

tldextract

RDAP

VirusTotal API

Google Safe Browsing API

Testing

Pytest

Frontend

Planned/current frontend stack:

React

Modern SaaS/security dashboard design

Repository Structure

email-security/
│
├── README.md
├── .gitignore
│
└── backend/
    │
    ├── app/
    │   ├── main.py
    │   ├── adapters/
    │   ├── analysis/
    │   │   ├── header_forensics/
    │   │   ├── nlp/
    │   │   ├── ioc/
    │   │   ├── risk/
    │   │   └── threat_intelligence/
    │   ├── api/
    │   │   ├── router.py
    │   │   ├── dependencies.py
    │   │   └── routes/
    │   ├── core/
    │   ├── db/
    │   ├── domain/
    │   ├── integrations/
    │   ├── models/
    │   ├── parser/
    │   ├── repositories/
    │   ├── schemas/
    │   └── services/
    │
    ├── alembic/
    │   └── versions/
    ├── tests/
    ├── data/           # ignored from Git
    ├── secrets/        # ignored from Git
    ├── requirements.txt
    ├── alembic.ini
    ├── pyproject.toml
    ├── .env            # ignored from Git
    └── .env.example

Getting Started

These steps are intended for team members cloning the repository for the first time.

1. Clone the Repository

git clone <YOUR-REPOSITORY-URL>

Then:

cd Email-Threat-Detection-and-Forensics
cd backend

2. Create a Python Virtual Environment

python -m venv .venv

Activate it:

.venv\Scripts\Activate.ps1

If PowerShell blocks activation:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Then activate again.

3. Install Dependencies

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Environment Configuration

The real .env file is intentionally not stored in GitHub.

Create:

backend/.env

Use backend/.env.example as the reference.

Example structure:

APP_NAME=Email Threat Detection Platform
APP_ENV=development
API_V1_PREFIX=/api/v1

DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/email_security

STORAGE_ROOT=./data
MAX_EMAIL_SIZE_MB=25
CORS_ORIGINS=["http://localhost:5173"]

GMAIL_CREDENTIALS_PATH=./secrets/gmail_credentials.json
GMAIL_TOKEN_PATH=./data/oauth/gmail_token.json

JWT_SECRET_KEY=GENERATE_YOUR_OWN_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

VIRUSTOTAL_API_KEY=
GOOGLE_SAFE_BROWSING_API_KEY=

Never copy another team member's JWT secret or database password into GitHub. Each developer can use local development credentials.

Generate a JWT Secret

python -c "import secrets; print(secrets.token_urlsafe(64))"

Copy the generated value into JWT_SECRET_KEY in your local .env. Do not commit it.

Database Setup

The project currently uses PostgreSQL.

1. Install PostgreSQL

Install PostgreSQL locally if it is not already available. Default development port is usually 5432.

2. Create Database

Create a database named:

email_security

Example:

CREATE DATABASE email_security;

3. Configure DATABASE_URL

Inside .env:

DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/email_security

Verify the backend is using the expected database:

python -c "from app.db.session import engine; print(engine.url.render_as_string(hide_password=True))"

Expected database name: email_security.

4. Apply Alembic Migrations

python -m alembic upgrade head

Check current migration:

python -m alembic current

Do not manually create project tables unless there is a specific reason. Alembic is responsible for schema migrations.

Running the Backend

From email-security/backend run:

python -m uvicorn app.main:app --reload

Expected server:

http://127.0.0.1:8000

Swagger API documentation:

http://127.0.0.1:8000/docs

OpenAPI JSON:

http://127.0.0.1:8000/openapi.json

API Overview

The exact Swagger page is the best source for current request/response schemas.

Health

GET /api/v1/health

Authentication

POST /api/v1/auth/signup
POST /api/v1/auth/login
GET  /api/v1/auth/me

Protected requests use:

Authorization: Bearer <JWT>

Test Lab / EML Upload

POST /api/v1/test-lab/emails

Emails

GET /api/v1/emails
GET /api/v1/emails/{email_id}

Analysis

POST /api/v1/analysis/emails/{email_id}
GET  /api/v1/analysis/emails/{email_id}/history

Dashboard

GET /api/v1/dashboard/summary
GET /api/v1/dashboard/recent

Reports

GET /api/v1/reports/analyses/{analysis_id}

Lifecycle

GET  /api/v1/lifecycle/summary
GET  /api/v1/lifecycle/emails/{email_id}
GET  /api/v1/lifecycle/emails/{email_id}/history

POST /api/v1/lifecycle/emails/{email_id}/quarantine
POST /api/v1/lifecycle/emails/{email_id}/block
POST /api/v1/lifecycle/emails/{email_id}/review
POST /api/v1/lifecycle/emails/{email_id}/allow
POST /api/v1/lifecycle/emails/{email_id}/release
POST /api/v1/lifecycle/emails/{email_id}/restore

Gmail

GET  /api/v1/gmail/status
GET  /api/v1/gmail/messages
POST /api/v1/gmail/messages/{gmail_message_id}/import
POST /api/v1/gmail/messages/{gmail_message_id}/process

Mailbox

GET /api/v1/mailbox/inbox
GET /api/v1/mailbox/review
GET /api/v1/mailbox/quarantine
GET /api/v1/mailbox/blocked
GET /api/v1/mailbox/emails/{email_id}

Supported filters may include:

limit
offset
search
source

Threat Intelligence

Threat-intelligence endpoints are available under the threat-intelligence API group. Use Swagger for the latest exact routes and schemas.

Testing

Run all automated tests:

pytest -q

Before pushing changes, contributors should verify:

1. Application imports successfully
2. Alembic migrations are valid
3. Existing tests still pass
4. New module tests pass
5. Swagger starts without errors
6. No secrets are staged in Git

Team Development Workflow

Team members should not develop everything directly on the main branch.

Recommended workflow:

main
 │
 ├── feature/header-research
 ├── feature/nlp
 ├── feature/ui
 ├── feature/testing
 └── feature/<member-task>

Step 1: Clone

git clone <repository-url>
cd Email-Threat-Detection-and-Forensics

Step 2: Create Your Branch

git checkout -b feature/nlp-improvements

Check branch:

git branch

Step 3: Make Changes

Only modify files related to your assigned task unless an integration change is required. Avoid unnecessary redesign of already completed modules.

Step 4: Check Modified Files

git status

Make sure no secret files are listed.

Step 5: Stage Changes

git add .
git status

Step 6: Commit

git commit -m "Improve NLP phishing detection rules"

Use meaningful commit messages.

Good examples:

Add phishing dataset loader
Improve header alignment detection
Fix IOC URL normalization
Add mailbox UI
Add authentication tests

Avoid vague messages such as update, changes, final, or done.

Step 7: Push Branch

git push -u origin feature/nlp-improvements

Then create a Pull Request on GitHub.

Pull Request Rules

Before opening a Pull Request:

Code should run

Tests should pass

No passwords or tokens

Do not commit .env

Do not commit Gmail credentials

Do not commit OAuth tokens

Explain what you changed

Mention any database migration

Mention any new dependency

Mention any API contract change

Security Rules for Contributors

This repository is public.

Never Commit

.env
backend/.env
gmail_credentials.json
gmail_token.json
OAuth access tokens
OAuth refresh tokens
JWT_SECRET_KEY
database passwords
VirusTotal API keys
Google Safe Browsing API keys
private certificates
personal credentials
production credentials

Protected Locations

The following locations should remain ignored:

backend/secrets/
backend/data/
backend/data/oauth/

Before Every Push

git status

Optionally verify ignored files:

git status --ignored

If a sensitive file appears under staged files, stop and remove it before pushing.

Gmail Setup for Developers

The repository does not include Google OAuth credentials.

A developer who needs Gmail functionality must use their own authorized Google OAuth credentials.

Expected local location:

backend/secrets/gmail_credentials.json

Generated OAuth token:

backend/data/oauth/gmail_token.json

Both must remain outside Git.

Developers who do not need Gmail can still work on most other modules.

External Threat Intelligence API Keys

VirusTotal and Google Safe Browsing are optional.

Without keys, the following still work:

Header Forensics
NLP Analysis
IOC Extraction
Static IOC Analysis
DNS Intelligence
RDAP Intelligence
Risk Engine
Lifecycle
Mailbox APIs

Only the corresponding external reputation provider is unavailable.

Current Development Status

Completed

Project architecture

PostgreSQL database

Alembic migrations

.eml source adapter

Raw email preservation

Email parser

Common Email Object

Attachment extraction

SHA-256 hashing

Email persistence

Header Forensics

SPF/DKIM/DMARC parsing

Sender-domain alignment analysis

Received-chain analysis

NLP/social-engineering rules

IOC extraction

Static IOC intelligence

Analysis Orchestrator

Final Risk Engine

Verdict generation

Recommended actions

Browser Isolation recommendation logic

Analysis history

Dashboard APIs

Report-ready APIs

Email lifecycle system

Inbox/Review/Quarantine/Blocked states

Action-history auditing

Gmail OAuth

Gmail message fetching

Gmail import

Automatic Gmail processing

DNS threat intelligence

RDAP threat intelligence

VirusTotal provider

Google Safe Browsing provider

External threat-intelligence orchestration

Mailbox APIs

Investigation detail API

User signup

User login

bcrypt password hashing

JWT authentication

/auth/me

In Progress / Next

Multi-user ownership

User-specific mailbox isolation

User-specific dashboard data

User-specific Gmail ownership

Protected security APIs

React frontend

Planned

Dashboard frontend

Inbox frontend

Investigation frontend

Quarantine frontend

Threat-intelligence frontend

Connected Accounts frontend

Reports frontend

Browser Isolation API integration

Deployment

Final security hardening

Roadmap

Authentication Core
        ↓
User Ownership Integration
        ↓
React Frontend Foundation
        ↓
Dashboard UI
        ↓
Mailbox UI
        ↓
Investigation UI
        ↓
Threat Intelligence UI
        ↓
Connected Accounts
        ↓
Browser Isolation API Integration
        ↓
Deployment

Troubleshooting

Error: ModuleNotFoundError

Make sure the virtual environment is active:

.venv\Scripts\Activate.ps1

Then:

python -m pip install -r requirements.txt

PostgreSQL Connection Error

Verify .env:

DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/email_security

Check actual backend connection:

python -c "from app.db.session import engine; print(engine.url.render_as_string(hide_password=True))"

Alembic Error

python -m alembic current
python -m alembic history
python -m alembic upgrade head

Do not use alembic stamp or manually delete tables unless the migration problem is understood first.

JWT Secret Error

Check that .env contains:

JWT_SECRET_KEY=<your-secret>

Verify the application config can load it:

python -c "from app.core.config import settings; print(bool(settings.jwt_secret_key))"

Expected:

True

Do not print the actual secret.

Gmail Authentication Error

Confirm local files exist:

backend/secrets/gmail_credentials.json
backend/data/oauth/gmail_token.json

If the OAuth token is invalid, it may need to be regenerated locally. Never upload the token to GitHub.

Swagger Shows 500

Swagger normally only displays Internal Server Error. Check the terminal running Uvicorn for the actual Python traceback.

Project Design Principles

1. Modular Architecture

Each analysis component should have a clear responsibility.

IOC Extractor
→ extracts indicators

IOC Intelligence
→ analyzes indicators

Risk Engine
→ makes aggregate decision

2. Explainable Security Decisions

Security findings should include evidence. The system should be able to explain why an email received a certain risk score.

3. External APIs Are Optional

The core system must continue to function when third-party services are unavailable.

4. Browser Isolation Is Separate

The Browser Isolation engine is intentionally not part of this repository. It will communicate through an API.

5. Preserve Forensic Evidence

Raw messages, hashes, findings, analysis history, and lifecycle actions are preserved so investigations can be reproduced.

6. Avoid Breaking Completed Modules

The project is being built in batches. Once a batch is complete, avoid rewriting it unless required for a bug fix, security fix, required integration, ownership change, or API compatibility.

Suggested Team Responsibilities

Email Research
→ email structure, phishing vectors, headers, spoofing

Dataset / Testing
→ phishing, benign, malware-related sample emails

NLP
→ phishing language, BEC, impersonation, social engineering

Frontend
→ dashboard, inbox, investigation, quarantine

Threat Intelligence
→ domains, URLs, reputation, DNS/RDAP research

Documentation
→ architecture, API flows, diagrams, testing notes

Changes should later be integrated through Git branches and Pull Requests.

Important Note About AI

The platform is designed as an AI-powered/intelligent email-security platform, but the current NLP implementation is primarily an explainable deterministic rule-based engine.

This is intentional for the current development stage.

Future versions can add:

Machine-learning phishing classification

Transformer-based text classification

Embedding-based similarity

BEC anomaly models

Behavioral sender profiling

These can be added as additional analysis modules without replacing the existing pipeline.

Project Purpose

The focus is not only:

Is this phishing?

but also:

Why is it suspicious?
What indicators were found?
What evidence supports the decision?
What action should be taken?
Can an analyst investigate the event later?
Should the URL be dynamically isolated?

Disclaimer

This project is created for education, cybersecurity research, defensive security, authorized testing, and academic demonstration.

It should only be used on emails, accounts, systems, and infrastructure that you own or are authorized to analyze.

Contributors

Deepak Sharma


Final Note for Team Members

If you are new to this repository, follow this order:

1. Read this README
2. Clone the repository
3. Create your own branch
4. Create and activate .venv
5. Install requirements
6. Create your own .env
7. Configure PostgreSQL
8. Run Alembic migrations
9. Start FastAPI
10. Open Swagger
11. Run pytest
12. Work only on your assigned module
13. Check git status
14. Never push secrets
15. Push your branch
16. Create a Pull Request

For the latest API behavior, always check:

http://127.0.0.1:8000/docs

before modifying an existing API contract.