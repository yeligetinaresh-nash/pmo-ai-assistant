PMO AI Assistant - Demo Guide

1. Demo Objective

Demonstrate how the PMO AI Assistant converts a Business Requirements Document (BRD) into structured PMO artifacts using AI, while maintaining authentication, caching, persistence, and downloadable outputs.

Recommended demo duration:

8-12 minutes

2. Demo Setup

Before starting the demo, confirm:

Docker Desktop is running

PostgreSQL is running

Backend is running on port 8001

Frontend is running on port 5173

Login credentials are available

A sample non-confidential BRD is available

At least one cached analysis/artifact is available

Backend automated tests are passing

3. Start Database

cd pmo-ai-assistant
docker compose up -d
docker ps

Expected container:

pmo-postgres

4. Start Backend

Use Terminal 1:

cd pmo-ai-assistant\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001

Backend:

http://127.0.0.1:8001

Swagger:

http://127.0.0.1:8001/docs

5. Start Frontend

Use Terminal 2:

cd pmo-ai-assistant\frontend
npm run dev

Frontend:

http://localhost:5173

6. Demo Flow

Follow this sequence during the demo:

Login
  ↓
Dashboard
  ↓
Create/Open Project
  ↓
Upload/Open BRD
  ↓
View BRD Analysis
  ↓
Show Cached Result
  ↓
Open PMO Artifacts
  ↓
Download Artifact
  ↓
Show Logs / Request ID
  ↓
Show Test Result

7. Step 1 - Login

Open the frontend:

http://localhost:5173

Login using a demo account.

Explain:

The application uses JWT-based authentication. Protected PMO APIs, documents, and artifact downloads require a valid authenticated session.

8. Step 2 - Dashboard

Show the main project dashboard.

Explain:

The dashboard provides a central workspace for project records, uploaded BRDs, AI analysis, and generated PMO artifacts.

9. Step 3 - Create or Open a Project

Create a new project or open an existing demo project.

Explain:

Each BRD and generated artifact is linked to a project so the application can maintain structured project-level governance and traceability.

10. Step 4 - BRD Document

Open or upload a sample BRD.

Supported formats:

PDF

DOCX

Explain:

The backend extracts document content, cleans the text, and prepares it for structured AI analysis.

Do not use confidential employer or client documents in the demo.

11. Step 5 - BRD Analysis

Open the BRD analysis.

If the UI shows:

BRD Analysis: Cached

highlight it.

Explain:

The analysis has already been generated and stored in PostgreSQL. The application returns the cached result instead of making another paid AI request.

This demonstrates AI cost control.

12. Step 6 - Project Charter

Open the Project Charter.

Explain:

The Project Charter converts structured BRD information into a governance-oriented project artifact that can support project initiation and stakeholder alignment.

Show the download option if available.

13. Step 7 - Work Breakdown Structure

Open the WBS.

Explain:

The Work Breakdown Structure decomposes the project scope into structured delivery components that support planning, ownership, and execution tracking.

14. Step 8 - Requirements Register

Open the Requirements Register.

Explain:

The Requirements Register converts business requirements into a structured view that improves traceability and governance.

15. Step 9 - RAID & Risk Register

Open the RAID & Risk Register.

Explain:

Risks, assumptions, issues, and dependencies are structured into a governance-ready RAID view to support project control and decision-making.

16. Step 10 - Stakeholder Register

Open the Stakeholder Register.

Explain:

Identified stakeholders are transformed into a structured stakeholder-management artifact that can support engagement planning.

17. Step 11 - RACI Matrix

Open the RACI Matrix.

Explain:

The RACI Matrix clarifies Responsible, Accountable, Consulted, and Informed roles across project activities.

18. Step 12 - Project Timeline

Open the Project Timeline.

Explain:

The timeline provides an initial structured delivery schedule based on the analyzed BRD scope and dependencies.

19. Step 13 - Artifact Download

Download one artifact.

Explain:

Artifact downloads are also protected by authentication. The frontend retrieves the file using the authenticated API flow.

Supported export formats include:

DOCX

XLSX

20. Step 14 - Authentication and Security

Explain the security model:

User
  ↓
Login
  ↓
JWT
  ↓
Protected FastAPI Endpoint
  ↓
Authorized Response

Current MVP security includes:

JWT authentication

password hashing

protected project APIs

protected document APIs

protected artifact APIs

authenticated downloads

environment-based secrets

centralized error handling

21. Step 15 - Observability

Show the backend terminal logs.

Explain that each request includes:

request ID

HTTP method

API path

response status

execution duration

Each response contains:

X-Request-ID

Explain:

The request ID allows an API request to be correlated with backend logs during troubleshooting.

22. Step 16 - Automated Tests

If required, open a temporary terminal and run:

cd pmo-ai-assistant\backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests -v

Current validated baseline:

46 passed

Explain:

Automated tests cover authentication, JWT protection, project APIs, cached artifacts, downloads, exporters, normalization, document errors, and observability.

23. Technical Architecture

Use this simple explanation:

React / Vite Frontend
        ↓
JWT Authentication
        ↓
FastAPI REST API
        ↓
Business + AI Services
        ↓
OpenAI API
        ↓
PostgreSQL
        ↓
DOCX / XLSX Artifact Export

Docker is used to run PostgreSQL locally.

24. AI Cost-Control Explanation

Explain:

AI calls are not made every time an artifact is viewed. Completed analysis and artifacts are persisted and cached. Existing results are reused by default, while explicit regeneration is used only when a fresh AI result is required.

This demonstrates practical AI cost control.

25. Suggested Interview Explanation

I designed the PMO AI Assistant as a full-stack AI-enabled PMO solution. A user logs in through JWT authentication, creates a project, uploads a BRD, and the FastAPI backend extracts and analyzes the content using an LLM. Structured analysis is persisted in PostgreSQL and reused through caching to control AI cost. From that analysis, the system generates project-management artifacts such as the Project Charter, WBS, Requirements Register, RAID Register, Stakeholder Register, RACI Matrix, and Project Timeline. The React/Vite frontend provides the workspace, while FastAPI provides secured REST APIs, authenticated downloads, centralized error handling, request tracing, and automated testing.

26. Demo Best Practices

Before presenting:

use a sample non-confidential BRD

pre-generate expensive AI artifacts where possible

verify login

verify database

verify backend

verify frontend

verify at least one artifact download

run tests before the meeting

avoid exposing .env

avoid exposing API keys

avoid exposing JWT tokens

keep one cached demo project available in case the AI API is unavailable

27. Common Demo Problems

Login fails

Check backend availability:

http://127.0.0.1:8001

Confirm valid demo credentials.

Frontend shows Failed to Fetch

Confirm backend is running on port 8001.

Frontend starts on 5174

Close duplicate Vite processes and restart on:

http://localhost:5173

Artifact generation fails

Check:

OPENAI_API_KEY
OPENAI_MODEL

Avoid repeated forced generation during a live demo.

API returns 401

Login again to obtain a valid JWT.

28. Recommended Demo Ending

Conclude with:

The current MVP demonstrates the full journey from BRD ingestion to secure, AI-assisted PMO artifact generation. It combines project governance, AI integration, persistence, caching, authentication, downloadable outputs, automated testing, and observability in one end-to-end solution.

Then mention future production enhancements such as:

cloud deployment

RBAC

CI/CD

centralized monitoring

secret management

rate limiting

stronger production authentication

portfolio-level analytics

29. Demo Validation Baseline

Current backend automated-test baseline:

46 passed

This baseline should remain green before any project demonstration.