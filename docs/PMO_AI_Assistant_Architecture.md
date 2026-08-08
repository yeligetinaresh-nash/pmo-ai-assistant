# PMO AI Assistant – Architecture Document

## 1. Purpose

This document describes the technical architecture of the PMO AI Assistant.

The PMO AI Assistant is a full-stack application that accepts Business Requirement Documents (BRDs) and project documents, analyzes their contents using AI, and generates structured PMO artifacts for project managers, PMO teams, business analysts, and delivery teams.

The system is designed around five key principles:

- Simple project and document management
- Reusable AI analysis
- Structured PMO artifact generation
- Cost-aware cache-first processing
- Exportable project-management outputs

---

## 2. Business Problem

Project managers and PMO teams frequently receive requirement documents containing large amounts of business and technical information.

These documents must then be converted manually into project-management artifacts such as:

- Project Charter
- Work Breakdown Structure
- Requirements Register
- RAID Log
- Risk Register
- Stakeholder Register
- RACI Matrix
- Project Timeline

This manual process can be repetitive, time-consuming, and inconsistent.

PMO AI Assistant provides an AI-assisted workflow that converts project requirement information into structured first drafts of these PMO artifacts.

---

## 3. High-Level Architecture

```text
+-----------------------+
|        USER           |
| Project Manager / PMO |
+-----------+-----------+
            |
            v
+-----------------------+
|   React Frontend      |
|   Vite Application    |
+-----------+-----------+
            |
            | HTTP / REST
            |
            v
+-----------------------+
|    FastAPI Backend    |
|                       |
| Project APIs          |
| Document APIs         |
| Analysis APIs         |
| Artifact APIs         |
| Export APIs           |
+-----------+-----------+
            |
     +------+------+
     |             |
     v             v
+----------+   +----------------+
|PostgreSQL|   |   OpenAI API   |
| Database |   |                |
+----------+   +----------------+
     |             |
     |             |
     +------+------+
            |
            v
+-----------------------+
| PMO Artifact Engine   |
|                       |
| Charter               |
| WBS                   |
| Requirements          |
| RAID / Risk           |
| Stakeholder           |
| RACI                  |
| Timeline              |
+-----------+-----------+
            |
            v
+-----------------------+
| Export Generation     |
|                       |
| DOCX                  |
| XLSX                  |
+-----------------------+
```

---

## 4. Architecture Layers

The application is separated into the following logical layers:

1. Presentation Layer
2. API Layer
3. Business Logic Layer
4. AI Processing Layer
5. Persistence Layer
6. Export Layer
7. Infrastructure Layer

---

## 5. Presentation Layer

### Technology

- React
- Vite
- JavaScript
- CSS
- Fetch API

The frontend provides the user interface used to interact with the PMO AI Assistant.

Primary frontend responsibilities include:

- Display projects
- Create projects
- Edit projects
- Delete projects
- Upload documents
- Open project documents
- Delete documents
- Display BRD analysis status
- Display artifact generation status
- Trigger AI analysis
- Trigger artifact generation
- Download documents
- Download generated artifacts

---

## 6. Frontend Application Flow

```text
Dashboard
   |
   +---- Create Project
   |
   +---- Edit Project
   |
   +---- Delete Project
   |
   +---- Open Project
            |
            v
      Project Workspace
            |
            +---- Upload Document
            |
            +---- Download Document
            |
            +---- Delete Document
            |
            +---- Open Document
                     |
                     v
              BRD Analysis Status
                     |
          +----------+----------+
          |                     |
          v                     v
       Cached              Not Analyzed
          |                     |
          v                     v
     Load Analysis        User Confirmation
                                |
                                v
                           OpenAI Request
                                |
                                v
                           Save Analysis
                                |
                                v
                       PMO Artifact Generation
```

---

## 7. Backend Architecture

### Technology

- Python 3.12
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

The backend exposes REST APIs used by the frontend.

Main backend responsibilities include:

- Project CRUD
- Document management
- File validation
- Text extraction
- BRD analysis
- Artifact generation
- Artifact persistence
- Cache lookup
- Export generation
- Error handling
- Database access

---

## 8. Backend Module Structure

A simplified backend structure is:

```text
backend/
│
├── app/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── routers/
│   └── main.py
│
├── tests/
├── alembic/
├── requirements.txt
└── .env
```

---

## 9. API Layer

The API layer is responsible for communication between the frontend and backend.

Typical endpoint categories include:

```text
/projects
/documents
/documents/{document_id}/analysis
/documents/{document_id}/artifacts
```

---

## 10. Project API Flow

Project management follows the normal CRUD model.

```text
Frontend
   |
   +---- POST /projects
   |         |
   |         v
   |     Create Project
   |
   +---- GET /projects
   |         |
   |         v
   |     Load Projects
   |
   +---- PUT /projects/{id}
   |         |
   |         v
   |     Update Project
   |
   +---- DELETE /projects/{id}
             |
             v
        Delete Project
```

Project information is persisted in PostgreSQL.

---

## 11. Document Management Flow

```text
User
 |
 v
Select PDF / DOCX
 |
 v
Frontend Validation
 |
 +---- Extension validation
 |
 +---- Maximum size validation
 |
 v
POST Document
 |
 v
FastAPI Backend
 |
 v
Store Document Metadata
 |
 v
Store File
 |
 v
Return Document Information
```

Supported file types:

- PDF
- DOCX

Maximum upload size:

```text
10 MB
```

---

## 12. Document Processing

Once a document is uploaded, its content can be extracted for AI processing.

Supported extraction capabilities include:

- PDF text extraction
- DOCX paragraph extraction
- DOCX table extraction

OCR is currently not part of the main MVP document-processing workflow.

---

## 13. BRD Analysis Architecture

The BRD analysis workflow follows a cache-first design.

```text
User Opens Document
        |
        v
GET Existing Analysis
        |
   +----+----+
   |         |
   v         v
Exists     Missing
   |         |
   v         v
Cached     Cost Warning
Result        |
              v
       User Confirmation
              |
              v
         OpenAI API
              |
              v
        Structured Analysis
              |
              v
        PostgreSQL Storage
```

---

## 14. Why Cache-First Processing Is Used

AI API calls have cost and latency.

The application therefore checks whether an analysis already exists before creating another one.

Benefits include:

- Reduced OpenAI API usage
- Reduced cost
- Faster user experience
- Consistent artifact generation
- Reusable outputs
- Better development safety

---

## 15. BRD Analysis Status Model

The frontend can display the following BRD analysis states:

```text
Checking Analysis
BRD Analysis: Cached
BRD Analysis: Not Analyzed
BRD Analysis: Status Error
BRD Analysis: Unknown
```

Artifacts cannot be generated until a valid BRD analysis is available.

---

## 16. PMO Artifact Architecture

After the BRD analysis is available, the system can generate seven PMO artifacts.

```text
BRD Analysis
      |
      v
Artifact Generation Layer
      |
      +---- Project Charter
      |
      +---- WBS
      |
      +---- Requirements Register
      |
      +---- RAID & Risk Register
      |
      +---- Stakeholder Register
      |
      +---- RACI Matrix
      |
      +---- Project Timeline
```

---

## 17. Artifact Cache Logic

Each artifact follows the same basic cache-first pattern.

```text
Generate Artifact Requested
          |
          v
Check Artifact Database
          |
     +----+----+
     |         |
     v         v
  Exists     Missing
     |         |
     v         v
Load Cached  Cost Warning
Artifact        |
                v
          User Confirmation
                |
                v
            OpenAI API
                |
                v
         Generate Artifact
                |
                v
          Save to Database
```

---

## 18. Artifact Status Model

The frontend displays artifact generation states such as:

```text
Checking
Cached
Not Generated
Status Error
Unknown
```

When an artifact is cached:

```text
Load Cached
Download Artifact
```

When it is not generated:

```text
Generate
```

The download button remains disabled until the artifact exists.

---

## 19. Artifact Persistence

Generated artifacts are persisted so they can be reused.

This provides:

- Faster subsequent access
- Reduced AI calls
- Better traceability
- Consistent exports
- Reusable project knowledge

The application uses a shared artifact persistence model for generated PMO outputs.

---

## 20. Export Architecture

Generated outputs are converted into downloadable office documents.

```text
Generated Artifact
       |
       v
Artifact Export Service
       |
   +---+---+
   |       |
   v       v
 DOCX     XLSX
```

Current formats include:

| Artifact | Export |
|---|---|
| Project Charter | DOCX |
| WBS | DOCX |
| Requirements Register | XLSX |
| RAID & Risk Register | XLSX |
| Stakeholder Register | XLSX |
| RACI Matrix | XLSX |
| Project Timeline | XLSX |

---

## 21. Database Architecture

### Technology

PostgreSQL 16

PostgreSQL runs inside Docker during local development.

Typical information stored in the database includes:

- Projects
- Project status
- Documents
- Document metadata
- BRD analyses
- Generated artifacts
- Artifact content
- Creation/update metadata

---

## 22. Database Connection

The backend communicates with PostgreSQL using SQLAlchemy.

```text
FastAPI
   |
   v
SQLAlchemy
   |
   v
PostgreSQL
```

Database schema changes are controlled using Alembic migrations.

---

## 23. Database Migration Strategy

Alembic manages schema evolution.

```text
Model Change
     |
     v
Alembic Revision
     |
     v
Migration Review
     |
     v
alembic upgrade head
     |
     v
PostgreSQL Updated
```

This allows database schema changes to be version controlled.

---

## 24. AI Integration Layer

The backend communicates with the OpenAI API when new AI processing is required.

Typical AI tasks include:

- BRD analysis
- Project Charter generation
- WBS generation
- Requirements extraction
- RAID/Risk generation
- Stakeholder analysis
- RACI generation
- Timeline generation

The frontend never directly calls OpenAI.

All AI requests pass through the backend.

---

## 25. AI Security Boundary

```text
Browser
   |
   v
Frontend
   |
   v
FastAPI Backend
   |
   | Reads OPENAI_API_KEY
   |
   v
OpenAI API
```

The API key remains on the backend.

It is not exposed to the browser.

---

## 26. Environment Configuration

Sensitive settings are stored in:

```text
backend/.env
```

Example:

```env
DATABASE_URL=postgresql://pmo_user:pmo_password@localhost:5432/pmo_db
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5-mini
```

The real `.env` file is excluded from Git.

---

## 27. Security Controls

Current security controls include:

- Secrets stored outside source code
- `.env` excluded from Git
- `.venv` excluded from Git
- `node_modules` excluded from Git
- generated files excluded from Git
- frontend production builds excluded from Git
- OpenAI key stored only on backend
- explicit confirmation before new paid AI generation

---

## 28. CORS Architecture

During local development, FastAPI permits the local frontend origins used by Vite.

```text
http://localhost:5173
http://127.0.0.1:5173
```

This allows the React frontend to communicate with the backend while keeping the API separated from the browser application.

---

## 29. Infrastructure Architecture

Current local development infrastructure:

```text
Windows Development Machine
        |
        +---- VS Code
        |
        +---- React / Vite
        |
        +---- Python / FastAPI
        |
        +---- Docker Desktop
                 |
                 v
             PostgreSQL
```

---

## 30. Docker Architecture

PostgreSQL is containerized.

```text
Docker Desktop
      |
      v
Docker Compose
      |
      v
pmo-postgres
      |
      v
PostgreSQL 16
```

Benefits include:

- Reproducible local database
- Simple startup
- Easy environment cleanup
- Consistent development setup

---

## 31. Local Runtime Architecture

The application currently uses three main runtime processes.

```text
Terminal 1
Docker / PostgreSQL

Terminal 2
FastAPI / Uvicorn
Port 8000

Terminal 3
React / Vite
Port 5173
```

Browser:

```text
http://localhost:5173/
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## 32. End-to-End Sequence

```text
User
 |
 | Create Project
 v
React Frontend
 |
 | POST /projects
 v
FastAPI
 |
 v
PostgreSQL

User
 |
 | Upload BRD
 v
React
 |
 v
FastAPI
 |
 | Store metadata/file
 v
Database / Storage

User
 |
 | Open Document
 v
React
 |
 | Check analysis
 v
FastAPI
 |
 +------ Cached ------> Return Existing Analysis
 |
 +------ Missing
             |
             v
       Confirmation
             |
             v
         OpenAI API
             |
             v
       Save Analysis

User
 |
 | Generate Artifact
 v
React
 |
 | Check artifact
 v
FastAPI
 |
 +------ Cached ------> Return Existing Artifact
 |
 +------ Missing
             |
             v
       Confirmation
             |
             v
         OpenAI API
             |
             v
      Save Artifact
             |
             v
        Export File
```

---

## 33. Testing Architecture

The backend uses Pytest and FastAPI TestClient.

Tests cover areas such as:

- Health endpoints
- API metadata
- Project CRUD
- Document error handling
- Artifact routes
- Cached artifact retrieval
- Artifact downloads

Current verified test result:

```text
31 passed
```

---

## 34. Frontend Build Validation

The frontend uses Vite's production build process.

Command:

```powershell
npm run build
```

Successful production builds generate:

```text
frontend/dist/
```

The current frontend production build has been successfully validated.

---

## 35. Error Handling Strategy

Errors can occur at several layers:

```text
Frontend Validation
       |
       v
HTTP/API Validation
       |
       v
Business Logic
       |
       v
Database Operations
       |
       v
AI Provider
       |
       v
Export Generation
```

The frontend displays readable error messages where possible.

Future development can introduce structured logging and centralized error monitoring.

---

## 36. Data Lifecycle

```text
Project
   |
   v
Document
   |
   v
Extracted Content
   |
   v
BRD Analysis
   |
   v
PMO Artifacts
   |
   v
DOCX / XLSX Exports
```

This hierarchy helps maintain traceability between the original requirements and generated project-management outputs.

---

## 37. Current MVP Boundary

The current MVP includes:

- Full project CRUD
- Document upload/download/delete
- PDF/DOCX support
- BRD content extraction
- BRD AI analysis
- Analysis persistence
- Seven PMO artifact generators
- Artifact persistence
- Cache-first processing
- Cost confirmation
- DOCX/XLSX export
- React dashboard
- PostgreSQL database
- Dockerized database
- Automated backend tests
- Production frontend build
- Git/GitHub source control

---

## 38. Current Limitations

The current portfolio MVP does not yet include:

- Authentication
- Authorization
- Multi-user access
- Role-based access control
- Cloud hosting
- Production monitoring
- Centralized audit logs
- Full artifact version history
- Jira integration
- Azure DevOps integration
- Teams integration
- Email notifications
- RAG project knowledge search
- Agentic workflow orchestration

These capabilities can be introduced incrementally.

---

## 39. Future Target Architecture

A future enterprise architecture could evolve toward:

```text
Users
  |
  v
Web Application
  |
  v
API Gateway
  |
  v
Authentication / RBAC
  |
  v
FastAPI Services
  |
  +--------------------+
  |                    |
  v                    v
PostgreSQL          AI Services
  |                    |
  v                    v
Object Storage      RAG Layer
  |                    |
  +---------+----------+
            |
            v
      Agentic Workflows
            |
      +-----+-----+
      |     |     |
      v     v     v
    Jira  Teams  Email
```

---

## 40. Future RAG Architecture

Retrieval-Augmented Generation can later allow the assistant to answer project-specific questions.

```text
Project Documents
       |
       v
Text Extraction
       |
       v
Chunking
       |
       v
Embeddings
       |
       v
Vector Store
       |
       v
User Question
       |
       v
Relevant Context Retrieval
       |
       v
LLM Response
```

Possible questions include:

- What are the top project risks?
- Which requirements are high priority?
- Who is accountable for UAT?
- Which milestones are delayed?
- What dependencies affect go-live?

---

## 41. Future Agentic AI Architecture

A future agentic version could support specialized PMO agents.

```text
PMO Orchestrator Agent
        |
        +---- Risk Agent
        |
        +---- Planning Agent
        |
        +---- Requirements Agent
        |
        +---- Governance Agent
        |
        +---- Reporting Agent
```

The orchestrator could route tasks to specialized agents and combine their outputs.

---

## 42. Deployment Evolution

Current:

```text
Local Development
```

Possible future deployment:

```text
Internet
   |
   v
Cloud Frontend
   |
   v
API Service
   |
   +------ PostgreSQL
   |
   +------ Object Storage
   |
   +------ OpenAI API
   |
   +------ Monitoring
```

Potential cloud platforms may include:

- AWS
- Azure
- Google Cloud

---

## 43. Observability Roadmap

Future production monitoring can include:

- API request logs
- Response times
- AI request latency
- OpenAI token usage
- AI cost tracking
- Failed generations
- Database failures
- User activity
- Artifact generation rates

This would allow administrators to understand system health and AI usage.

---

## 44. Portfolio Architecture Value

This architecture demonstrates practical understanding of:

- Full-stack architecture
- REST APIs
- React frontend development
- FastAPI backend development
- Relational databases
- Docker
- AI API integration
- Cache-first AI workflows
- Document processing
- Structured AI generation
- Office file exports
- Automated testing
- Security-conscious API-key handling
- Git/GitHub workflow

---

## 45. Architecture Summary

The PMO AI Assistant uses a modular full-stack architecture in which:

1. React provides the user interface.
2. FastAPI provides REST APIs and business logic.
3. PostgreSQL stores application and AI-generated data.
4. OpenAI provides BRD analysis and structured artifact generation.
5. Cache-first logic minimizes unnecessary AI calls.
6. Export services generate reusable DOCX and XLSX project artifacts.
7. Docker provides reproducible PostgreSQL infrastructure.
8. Pytest validates backend behavior.
9. Git and GitHub provide source-control and development traceability.

The resulting architecture provides a strong foundation for evolving the portfolio MVP into a more advanced AI-enabled PMO platform.