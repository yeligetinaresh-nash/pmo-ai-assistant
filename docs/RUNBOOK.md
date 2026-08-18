PMO AI Assistant - Runbook

1. Purpose

This runbook explains how to start, stop, validate, and troubleshoot the PMO AI Assistant in a local development or demo environment.

The solution includes:

React/Vite frontend

FastAPI backend

PostgreSQL database

OpenAI API integration

JWT authentication

PMO artifact generation

Artifact export

Automated backend testing

Request logging and observability

2. Prerequisites

Install:

Python 3.12+

Node.js

npm

Docker Desktop

Docker Compose

Git

VS Code

Optional:

Postman

DBeaver

3. Project Structure

pmo-ai-assistant/
├── backend/
├── frontend/
├── docs/
├── docker/
├── generated/
├── scripts/
├── templates/
├── docker-compose.yml
├── README.md
└── LICENSE

4. Environment Configuration

The backend uses:

backend/.env - real local configuration and secrets

backend/.env.example - safe sample values

Example:

DATABASE_URL=postgresql://pmo_user:pmo_password@localhost:5432/pmo_db
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5-mini
JWT_SECRET_KEY=replace_with_a_long_random_secret
ACCESS_TOKEN_EXPIRE_MINUTES=60

Do not commit or share the real backend/.env file.

5. Start PostgreSQL

Make sure Docker Desktop is running.

cd pmo-ai-assistant
docker compose up -d
docker ps

Expected container:

pmo-postgres

PostgreSQL runs in the background.

6. Start Backend

Use Terminal 1.

cd pmo-ai-assistant\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001

Backend:

http://127.0.0.1:8001

Swagger:

http://127.0.0.1:8001/docs

Expected startup:

Connected to PostgreSQL
Application startup complete
Uvicorn running on http://127.0.0.1:8001

Keep this terminal running.

7. Start Frontend

Use Terminal 2.

cd pmo-ai-assistant\frontend
npm run dev

Frontend:

http://localhost:5173

Keep this terminal running.

Normal setup:

Terminal 1 = Backend
Terminal 2 = Frontend
Docker = Running in background

8. Run Automated Tests

Open a temporary terminal when needed.

cd pmo-ai-assistant\backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests -v

Current validated result:

46 passed

The tests cover:

authentication

JWT protection

project CRUD

project validation

artifact routes

cached artifacts

artifact downloads

document errors

Excel exporters

normalization

request IDs

observability

Known non-blocking warning:

datetime.utcnow() deprecation warning

9. Authentication

Authentication flow:

User Login
    ↓
POST /auth/login
    ↓
Credential Validation
    ↓
JWT Access Token
    ↓
Authorization Header
    ↓
Protected APIs

Protected requests use:

Authorization: Bearer <token>

JWT expiry:

ACCESS_TOKEN_EXPIRE_MINUTES=60

10. Core Application Flow

Login
  ↓
Create Project
  ↓
Upload BRD
  ↓
Extract Document Content
  ↓
Clean Text
  ↓
AI BRD Analysis
  ↓
Store Structured Analysis
  ↓
Generate PMO Artifacts
  ↓
Retrieve Cached Results
  ↓
Download Artifacts

11. Supported PMO Artifacts

The system supports:

Project Charter

Work Breakdown Structure

Requirements Register

RAID & Risk Register

Stakeholder Register

RACI Matrix

Project Timeline

12. AI Cost Control

The application stores completed analysis and generated artifacts.

Cached results are reused where available.

This helps avoid unnecessary repeated OpenAI API calls.

Fresh AI generation should only be triggered when required.

13. Observability

The backend includes request logging.

Each request receives a unique request ID.

Each response includes:

X-Request-ID

Logs include:

request ID

HTTP method

API path

response status

execution duration

Example:

request_started | request_id=<id> | method=GET | path=/projects

request_completed | request_id=<id> | method=GET | path=/projects | status_code=200 | duration_ms=<time>

Unexpected server errors are handled through centralized exception handling.

14. Security

Current MVP security includes:

JWT authentication

password hashing

protected project APIs

protected document APIs

protected artifact APIs

authenticated downloads

environment-based secrets

request IDs

centralized error handling

Future production improvements may include:

HTTPS

RBAC

rate limiting

secret manager

secure cookie authentication

centralized monitoring

cloud IAM

15. Troubleshooting

Backend does not start

cd pmo-ai-assistant\backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

Database connection fails

docker ps

If PostgreSQL is not running:

cd pmo-ai-assistant
docker compose up -d

Check:

backend/.env

and verify:

DATABASE_URL

Frontend shows Failed to Fetch

Confirm backend is running on:

http://127.0.0.1:8001

Confirm frontend API configuration also uses port:

8001

API returns 401 Unauthorized

Login again and use a valid JWT.

Authorization: Bearer <token>

Frontend starts on port 5174

Another Vite process may already be using port 5173.

Standard frontend URL:

http://localhost:5173

Close duplicate Vite processes and restart the frontend.

OpenAI generation fails

Check:

OPENAI_API_KEY
OPENAI_MODEL

inside:

backend/.env

Avoid repeatedly forcing regeneration because it may create additional API cost.

16. Stop Application

Stop frontend:

Ctrl + C

Stop backend:

Ctrl + C

Stop PostgreSQL:

cd pmo-ai-assistant
docker compose down

Do not remove the PostgreSQL volume unless you intentionally want to reset the database.

17. Demo Readiness Checklist

Before a demo, confirm:

Docker Desktop is running

PostgreSQL is running

Backend is running on port 8001

Frontend is running on port 5173

Login works

Project dashboard loads

Sample BRD is available

BRD analysis loads

Cached artifacts load

Artifact download works

Automated tests pass

.env is not displayed

API key is not displayed

JWT token is not displayed

No confidential client documents are used

18. Current Validation Baseline

Current backend test result:

46 passed

This should remain green before future releases.

19. Production Readiness Notes

The current solution is a local portfolio MVP.

Before production deployment, additional work should include:

cloud deployment

production database setup

HTTPS

RBAC

CI/CD

secret management

rate limiting

centralized monitoring

backup and recovery

performance testing

production security review