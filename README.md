# PMO AI Assistant

AI-powered Project Management Office (PMO) assistant that analyzes Business Requirement Documents (BRDs) and automatically generates structured project-management artifacts.

## Overview

PMO AI Assistant is a full-stack AI application designed to help Project Managers, PMO teams, Business Analysts, and delivery teams convert project requirement documents into structured and reusable PMO outputs.

The application allows users to:

- Create and manage projects
- Upload BRD/project documents
- Analyze documents using AI
- Generate standard PMO artifacts
- Reuse cached AI outputs
- Download artifacts in Word and Excel formats
- Manage project and document records from a React dashboard

The system is designed with a cost-safety approach so that existing AI outputs are reused wherever possible before making a new OpenAI API request.

---

## Key Features

### Project Management

- Create projects
- Edit project name and description
- Update project status
- Delete projects
- Open project-specific workspaces
- Maintain project records in PostgreSQL

Supported project statuses include:

- Draft
- In Progress
- On Hold
- Completed
- Cancelled

---

## Document Management

The application supports project document management from the frontend.

Features include:

- Upload PDF files
- Upload DOCX files
- Maximum upload size of 10 MB
- View uploaded documents
- Download original documents
- Delete documents
- Extract document content for AI processing
- Associate documents with individual projects

---

## AI BRD Analysis

Once a BRD or project document is uploaded, the system can analyze the document using the OpenAI API.

The analysis process includes:

1. User opens a project document.
2. Frontend checks whether an analysis already exists.
3. If analysis exists, it is loaded from cache.
4. If analysis does not exist, the user receives a cost warning.
5. After confirmation, the backend calls the OpenAI API.
6. Analysis output is stored in PostgreSQL.
7. Future requests reuse the stored analysis.

This avoids unnecessary AI calls and reduces API cost.

---

## PMO Artifact Generation

PMO AI Assistant currently supports seven project-management artifacts.

### 1. Project Charter

Generates structured project information such as:

- Project objectives
- Business context
- Scope
- Governance
- Stakeholders
- Assumptions
- Constraints

Export format:

- DOCX

### 2. Work Breakdown Structure (WBS)

Generates a structured project breakdown containing:

- Project phases
- Activities
- Work packages
- Effort estimates
- Delivery structure

Export format:

- DOCX

### 3. Requirements Register

Generates a structured requirements register containing:

- Requirement ID
- Requirement description
- Requirement type
- Priority
- Status
- Ownership information

Export format:

- XLSX

### 4. RAID & Risk Register

Generates structured project governance information including:

- Risks
- Assumptions
- Issues
- Dependencies
- Risk severity
- Mitigation details
- Ownership

Export format:

- XLSX

### 5. Stakeholder Register

Generates stakeholder information including:

- Stakeholder
- Role
- Influence
- Interest
- Engagement approach
- Communication requirements

Export format:

- XLSX

### 6. RACI Matrix

Generates activity responsibility mapping using:

- Responsible
- Accountable
- Consulted
- Informed

Export format:

- XLSX

### 7. Project Timeline

Generates project schedule information including:

- Project phases
- Activities
- Milestones
- Dependencies
- Duration
- Planned sequence

Export format:

- XLSX

---

## Artifact Status Management

The frontend checks the backend before generating an artifact.

Artifact statuses include:

- Checking
- Cached
- Not Generated
- Status Error
- Unknown

If an artifact already exists:

```text
Cached
```

The user can load or download the existing artifact without calling OpenAI again.

If the artifact does not exist:

```text
Not Generated
```

The user is shown a confirmation before a new AI request is made.

---

## BRD Analysis Status

Possible BRD analysis states include:

```text
Checking Analysis
BRD Analysis: Cached
BRD Analysis: Not Analyzed
BRD Analysis: Status Error
BRD Analysis: Unknown
```

Artifacts cannot be generated until the BRD analysis is successfully available.

---

## Cost-Safety Controls

One of the core design principles of this project is to prevent accidental or unnecessary OpenAI API usage.

The application follows a cache-first workflow.

Before making a generation request, it first checks whether the analysis or artifact already exists.

If it exists:

```text
Load existing cached result
```

If it does not exist:

```text
Display cost warning
        |
        v
User confirmation
        |
        v
OpenAI API call
```

This provides better API-cost control during development and production use.

---

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS
- Fetch API

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy
- Uvicorn
- Pydantic

### Database

- PostgreSQL 16
- Docker
- Docker Compose

### AI

- OpenAI API
- Structured prompt processing
- AI-generated PMO artifacts
- Cached AI output reuse

### Document Processing

- PDF text extraction
- DOCX text extraction
- DOCX table extraction

### Export

- DOCX generation
- XLSX generation

### Testing

- Pytest
- FastAPI TestClient

### Development Tools

- Visual Studio Code
- Git
- GitHub
- PowerShell
- DBeaver
- Docker Desktop

---

## High-Level Architecture

```text
                        +----------------------+
                        |        User          |
                        +----------+-----------+
                                   |
                                   v
                        +----------------------+
                        |   React Frontend     |
                        |      Vite UI         |
                        +----------+-----------+
                                   |
                              REST API
                                   |
                                   v
                        +----------------------+
                        |   FastAPI Backend    |
                        +----------+-----------+
                                   |
               +-------------------+-------------------+
               |                                       |
               v                                       v
     +----------------------+                +----------------------+
     |    PostgreSQL DB     |                |      OpenAI API      |
     |                      |                |                      |
     | Projects             |                | BRD Analysis         |
     | Documents            |                | Artifact Generation  |
     | Analysis             |                +----------+-----------+
     | Artifacts            |                           |
     +----------+-----------+                           |
                |                                       |
                +-------------------+-------------------+
                                    |
                                    v
                         +----------------------+
                         | PMO Artifact Engine  |
                         +----------+-----------+
                                    |
                     +--------------+--------------+
                     |                             |
                     v                             v
              +-------------+              +-------------+
              |    DOCX     |              |    XLSX     |
              |   Export    |              |   Export    |
              +-------------+              +-------------+
```

---

## End-to-End Application Workflow

```text
Create Project
      |
      v
Upload BRD / Project Document
      |
      v
Extract Document Content
      |
      v
Check Existing BRD Analysis
      |
      +-----------------------------+
      |                             |
      v                             v
Analysis Exists               Analysis Missing
      |                             |
      v                             v
Load Cached Result            Show Cost Warning
                                    |
                                    v
                              User Confirmation
                                    |
                                    v
                               OpenAI API
                                    |
                                    v
                              Save Analysis
                                    |
                                    v
                         Generate PMO Artifacts
                                    |
                                    v
                         Check Artifact Cache
                                    |
                  +-----------------+----------------+
                  |                                  |
                  v                                  v
          Artifact Exists                     Artifact Missing
                  |                                  |
                  v                                  v
           Load Cached Result                 User Confirmation
                                                     |
                                                     v
                                                 OpenAI API
                                                     |
                                                     v
                                              Save Artifact
                                                     |
                                                     v
                                          Download DOCX / XLSX
```

---

## Project Structure

```text
pmo-ai-assistant/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── routers/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── docs/
├── templates/
├── scripts/
├── generated/
├── docker-compose.yml
└── README.md
```

---

## Prerequisites

Install the following:

- Git
- Python 3.12+
- Node.js
- npm
- Docker Desktop
- Visual Studio Code
- OpenAI API key

Optional:

- DBeaver
- Postman

---

## PostgreSQL Setup

From the project root:

```powershell
cd C:\Users\DELL\Desktop\pmo-ai-assistant
docker compose up -d
```

Check that PostgreSQL is running:

```powershell
docker ps
```

Expected PostgreSQL container:

```text
pmo-postgres
```

---

## Backend Setup

Move to the backend folder:

```powershell
cd C:\Users\DELL\Desktop\pmo-ai-assistant\backend
```

Create a Python virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## Environment Variables

Create:

```text
backend/.env
```

Example:

```env
DATABASE_URL=postgresql://pmo_user:pmo_password@localhost:5432/pmo_db
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5-mini
```

Do not commit the real `.env` file or API key to GitHub.

---

## Database Migrations

Apply the latest database migrations:

```powershell
cd C:\Users\DELL\Desktop\pmo-ai-assistant\backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

---

## Start Backend

```powershell
cd C:\Users\DELL\Desktop\pmo-ai-assistant\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

Open another PowerShell terminal:

```powershell
cd C:\Users\DELL\Desktop\pmo-ai-assistant\frontend
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:5173/
```

---

## Normal Startup Sequence

### 1. Start PostgreSQL

```powershell
cd C:\Users\DELL\Desktop\pmo-ai-assistant
docker compose up -d
```

### 2. Start Backend

```powershell
cd C:\Users\DELL\Desktop\pmo-ai-assistant\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### 3. Start Frontend

Open another terminal:

```powershell
cd C:\Users\DELL\Desktop\pmo-ai-assistant\frontend
npm run dev
```

### 4. Open the Application

```text
http://localhost:5173/
```

---

## Using PMO AI Assistant

### Create a Project

From the dashboard, click:

```text
+ New Project
```

Enter a project name and description.

### Edit a Project

Each project includes:

```text
Open Project | Edit | Delete
```

Edit allows updating:

- Project name
- Description
- Project status

### Upload a BRD

Open a project and upload a PDF or DOCX document.

Supported formats:

```text
PDF
DOCX
```

Maximum size:

```text
10 MB
```

### Analyze a BRD

Open an uploaded document.

If the analysis exists:

```text
BRD Analysis: Cached
```

If the analysis does not exist:

```text
BRD Analysis: Not Analyzed
```

A confirmation is displayed before a new OpenAI API call.

### Generate PMO Artifacts

After BRD analysis is available, the system can generate:

```text
Project Charter
WBS
Requirements Register
RAID & Risk Register
Stakeholder Register
RACI Matrix
Project Timeline
```

Previously generated artifacts are reused from cache.

### Download Artifacts

Cached artifacts can be downloaded from the frontend using:

```text
Load Cached
Download Artifact
```

### Delete Documents

Document actions include:

```text
Open Document | Download | Delete
```

A confirmation is required before deletion.

---

## Automated Testing

The backend includes automated tests covering:

- API metadata
- Health endpoints
- Project CRUD
- Document error handling
- Artifact endpoints
- Cached artifact retrieval
- Artifact downloads

Run tests:

```powershell
cd C:\Users\DELL\Desktop\pmo-ai-assistant\backend
.\.venv\Scripts\Activate.ps1
pytest -q
```

Latest verified result:

```text
31 passed
```

---

## Frontend Production Build

Run:

```powershell
cd C:\Users\DELL\Desktop\pmo-ai-assistant\frontend
npm run build
```

The build creates:

```text
frontend/dist/
```

The `dist` folder is ignored by Git.

---

## Git Security Controls

Check for accidentally committed API keys:

```powershell
git grep -n -E "sk-[A-Za-z0-9_-]{20,}|OPENAI_API_KEY=.*sk-"
```

Check ignored development files:

```powershell
git status --short --ignored | Select-String "\.env|generated|\.venv|node_modules|dist"
```

Expected ignored items include:

```text
backend/.env
backend/.venv/
frontend/node_modules/
frontend/dist/
generated/
```

---

## Current MVP Capabilities

The current MVP includes:

- Project CRUD
- Project status management
- PostgreSQL persistence
- PDF/DOCX document upload
- Document download
- Document deletion
- BRD text extraction
- AI BRD analysis
- Cached analysis
- Seven AI-generated PMO artifacts
- Artifact persistence
- Artifact caching
- DOCX exports
- XLSX exports
- Cost-safety confirmation
- Artifact status tracking
- BRD analysis status tracking
- React frontend dashboard
- FastAPI REST APIs
- Automated backend testing
- Frontend production build
- Dockerized PostgreSQL
- Git/GitHub version control

---

## Future Enhancements

Potential future enhancements include:

- User authentication
- JWT security
- Role-based access control
- Multi-user support
- Cloud deployment
- Audit logging
- Artifact version history
- Approval workflows
- Executive portfolio dashboard
- PMO KPI dashboard
- AI project health scoring
- Schedule variance tracking
- Cost variance tracking
- Resource planning
- Project dependency visualization
- Risk heat maps
- Automated notifications
- Jira integration
- Azure DevOps integration
- Microsoft Teams integration
- Email notifications
- Retrieval-Augmented Generation (RAG)
- Project knowledge assistant
- Agentic AI workflows

---

## Business Value

Traditional PMO teams spend significant time manually preparing project-management documentation after receiving business requirements.

PMO AI Assistant demonstrates how AI can help reduce repetitive documentation work by producing structured first drafts of core PMO artifacts.

Potential benefits include:

- Faster project initiation
- Improved documentation consistency
- Reduced manual effort
- Better governance standardization
- Faster conversion of requirements into delivery plans
- Reusable project knowledge
- Improved PMO productivity
- Better project traceability

---

## Portfolio Use Case

This project demonstrates practical experience across:

- Project Management
- PMO Governance
- Business Analysis
- Generative AI
- Prompt Engineering
- REST API Development
- Python
- FastAPI
- React
- PostgreSQL
- Docker
- Document Processing
- Data Persistence
- Automated Testing
- Git/GitHub
- Full-stack application development

---

## Project Status

```text
Status: Active Development
Stage: Portfolio MVP
```

Current development focus:

```text
Documentation
Architecture
Portfolio polish
Deployment readiness
```

---

## Disclaimer

AI-generated PMO artifacts should be reviewed and validated by qualified project stakeholders before being used for production project decisions.

The application is currently intended as a portfolio and learning project demonstrating AI-assisted PMO automation.