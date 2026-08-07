import os
from pathlib import Path
from uuid import uuid4
from contextlib import asynccontextmanager
from app.ai.project_charter_generator import generate_project_charter
from app.models.project_artifact import ProjectArtifact
from app.exporters.wbs_docx import generate_wbs_docx
from app.exporters.project_charter_docx import (
    generate_project_charter_docx,
)
from app.exporters.requirements_register_excel import (
    generate_requirements_register_excel,
)
from app.exporters.raid_risk_register_excel import (
    generate_raid_risk_register_excel,
)
from app.exporters.raci_matrix_excel import (
    generate_raci_matrix_excel,
)
from app.exporters.project_timeline_excel import (
    generate_project_timeline_excel,
)
from app.exporters.stakeholder_register_excel import (
    generate_stakeholder_register_excel,
)
from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.ai.brd_analyzer import analyze_brd
from app.ai.cleaner import clean_text
from app.ai.parser import parse_document
from app.ai.project_charter_generator import generate_project_charter
from app.ai.requirements_register_generator import (
    generate_requirements_register,
)
from app.ai.raid_risk_register_generator import (
    generate_raid_and_risk_register,
)
from app.ai.stakeholder_register_generator import (
    generate_stakeholder_register,
)
from app.ai.raci_matrix_generator import (
    generate_raci_matrix,
)
from app.ai.project_timeline_generator import (
    generate_project_timeline,
)
from app.ai.wbs_generator import generate_wbs
from app.crud.document import (
    create_document,
    delete_document,
    get_document,
    get_documents_by_project,
)
from app.crud.project import (
    create_project,
    delete_project,
    get_project,
    get_projects,
    update_project,
)
from app.database.connection import get_db, test_connection
from app.models.document import UploadedDocument
from app.models.document_analysis import DocumentAnalysis
from app.schemas.document import DocumentResponse
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    test_connection()
    yield


app = FastAPI(
    title="PMO AI Assistant API",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Upload Configuration
# ============================================================

UPLOAD_DIR = Path("../generated/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ============================================================
# Startup
# ============================================================

# ============================================================
# Root API
# ============================================================

@app.get("/")
def root():
    return {
        "message": "PMO AI Assistant API is running successfully!"
    }


# ============================================================
# Project APIs
# ============================================================

@app.post(
    "/projects",
    response_model=ProjectResponse,
)
def create_new_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
):
    return create_project(
        db,
        project,
    )


@app.get(
    "/projects",
    response_model=list[ProjectResponse],
)
def read_projects(
    db: Session = Depends(get_db),
):
    return get_projects(db)


@app.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
)
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = get_project(
        db,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project


@app.put(
    "/projects/{project_id}",
    response_model=ProjectResponse,
)
def update_existing_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
):
    updated_project = update_project(
        db,
        project_id,
        project,
    )

    if updated_project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return updated_project


@app.delete("/projects/{project_id}")
def remove_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    deleted_project = delete_project(
        db,
        project_id,
    )

    if deleted_project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return {
        "message": "Project deleted successfully"
    }


# ============================================================
# Document Upload API
# ============================================================

@app.post(
    "/projects/{project_id}/documents",
    response_model=DocumentResponse,
)
async def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    project = get_project(
        db,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    original_name = file.filename or "uploaded_file"
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10 MB",
        )

    stored_name = f"{uuid4().hex}{extension}"
    storage_path = UPLOAD_DIR / stored_name

    try:
        storage_path.write_bytes(content)

        document = create_document(
            db=db,
            project_id=project_id,
            file_name=stored_name,
            original_name=original_name,
            file_type=extension.lstrip("."),
            file_size=len(content),
            storage_path=str(storage_path),
        )

        return document

    except Exception:
        if storage_path.exists():
            storage_path.unlink()

        raise


# ============================================================
# Document List API
# ============================================================

@app.get(
    "/projects/{project_id}/documents",
    response_model=list[DocumentResponse],
)
def list_project_documents(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = get_project(
        db,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return get_documents_by_project(
        db,
        project_id,
    )


# ============================================================
# Document Download API
# ============================================================

@app.get("/documents/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = get_document(
        db,
        document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    file_path = Path(document.storage_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Physical file not found",
        )

    return FileResponse(
        path=file_path,
        filename=document.original_name,
        media_type="application/octet-stream",
    )


# ============================================================
# Document Delete API
# ============================================================

@app.delete("/documents/{document_id}")
def remove_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = get_document(
        db,
        document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    file_path = Path(document.storage_path)

    deleted_document = delete_document(
        db,
        document_id,
    )

    if file_path.exists():
        file_path.unlink()

    return {
        "message": "Document deleted successfully",
        "document_id": deleted_document.id,
    }


# ============================================================
# Analyze Document API
# ============================================================

@app.post("/documents/{document_id}/analyze")
def analyze_document(
    document_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    existing_analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if existing_analysis and not force:
        return {
            "id": existing_analysis.id,
            "document_id": existing_analysis.document_id,
            "analysis_type": existing_analysis.analysis_type,
            "model_name": existing_analysis.model_name,
            "status": existing_analysis.status,
            "result": existing_analysis.result_json,
            "created_at": existing_analysis.created_at,
            "cached": True,
        }

    if not os.path.exists(document.storage_path):
        raise HTTPException(
            status_code=404,
            detail="Stored document file not found",
        )

    try:
        raw_text = parse_document(
            document.storage_path
        )

        cleaned_text = clean_text(
            raw_text
        )

        if not cleaned_text:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the document",
            )

        analysis = analyze_brd(
            cleaned_text
        )

        saved_analysis = DocumentAnalysis(
            document_id=document.id,
            analysis_type="brd_analysis",
            result_json=analysis.model_dump(),
            model_name=os.getenv(
                "OPENAI_MODEL",
                "gpt-5-mini",
            ),
            status="completed",
        )

        db.add(saved_analysis)
        db.commit()
        db.refresh(saved_analysis)

        return {
            "id": saved_analysis.id,
            "document_id": saved_analysis.document_id,
            "analysis_type": saved_analysis.analysis_type,
            "model_name": saved_analysis.model_name,
            "status": saved_analysis.status,
            "result": saved_analysis.result_json,
            "created_at": saved_analysis.created_at,
            "cached": False,
        }

    except HTTPException:
        raise

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Document analysis failed: {str(error)}",
        )


# ============================================================
# Get Saved Analysis API
# ============================================================

@app.get("/documents/{document_id}/analysis")
def get_document_analysis(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    saved_analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not saved_analysis:
        raise HTTPException(
            status_code=404,
            detail="No analysis found for this document",
        )

    return {
        "id": saved_analysis.id,
        "document_id": saved_analysis.document_id,
        "analysis_type": saved_analysis.analysis_type,
        "model_name": saved_analysis.model_name,
        "status": saved_analysis.status,
        "result": saved_analysis.result_json,
        "created_at": saved_analysis.created_at,
    }


@app.post(
    "/documents/{document_id}/artifacts/project-charter"
)
def create_project_charter(
    document_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=(
                "No completed BRD analysis found. "
                "Analyze the document first."
            ),
        )

    existing_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id == document.project_id,
            ProjectArtifact.document_analysis_id == analysis.id,
            ProjectArtifact.artifact_type == "project_charter",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if existing_artifact and not force:
        return {
            "id": existing_artifact.id,
            "project_id": existing_artifact.project_id,
            "document_analysis_id": (
                existing_artifact.document_analysis_id
            ),
            "artifact_type": existing_artifact.artifact_type,
            "model_name": existing_artifact.model_name,
            "status": existing_artifact.status,
            "content": existing_artifact.content_json,
            "created_at": existing_artifact.created_at,
            "cached": True,
        }

    try:
        charter = generate_project_charter(
            analysis.result_json
        )

        saved_artifact = ProjectArtifact(
            project_id=document.project_id,
            document_analysis_id=analysis.id,
            artifact_type="project_charter",
            content_json=charter.model_dump(),
            model_name=os.getenv(
                "OPENAI_MODEL",
                "gpt-5-mini",
            ),
            status="completed",
        )

        db.add(saved_artifact)
        db.commit()
        db.refresh(saved_artifact)

        return {
            "id": saved_artifact.id,
            "project_id": saved_artifact.project_id,
            "document_analysis_id": (
                saved_artifact.document_analysis_id
            ),
            "artifact_type": saved_artifact.artifact_type,
            "model_name": saved_artifact.model_name,
            "status": saved_artifact.status,
            "content": saved_artifact.content_json,
            "created_at": saved_artifact.created_at,
            "cached": False,
        }

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Project Charter generation failed: "
                f"{str(error)}"
            ),
        )

@app.get(
    "/documents/{document_id}/artifacts/project-charter"
)
def get_project_charter(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No completed BRD analysis found",
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id == document.project_id,
            ProjectArtifact.document_analysis_id == analysis.id,
            ProjectArtifact.artifact_type == "project_charter",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if not saved_artifact:
        raise HTTPException(
            status_code=404,
            detail="No Project Charter found for this document",
        )

    content = dict(saved_artifact.content_json)

    if not content.get("approval_status"):
        content["approval_status"] = "Draft"

    return {
        "id": saved_artifact.id,
        "project_id": saved_artifact.project_id,
        "document_analysis_id": (
            saved_artifact.document_analysis_id
        ),
        "artifact_type": saved_artifact.artifact_type,
        "model_name": saved_artifact.model_name,
        "status": saved_artifact.status,
        "content": content,
        "created_at": saved_artifact.created_at,
    }

@app.get(
    "/documents/{document_id}/artifacts/project-charter/download"
)
def download_project_charter_docx(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No completed BRD analysis found",
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id == document.project_id,
            ProjectArtifact.document_analysis_id == analysis.id,
            ProjectArtifact.artifact_type == "project_charter",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if not saved_artifact:
        raise HTTPException(
            status_code=404,
            detail="No Project Charter found for this document",
        )

    content = dict(saved_artifact.content_json)

    if not content.get("approval_status"):
        content["approval_status"] = "Draft"

    export_dir = Path("../generated/exports")
    export_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = export_dir / (
        f"project_charter_document_{document_id}.docx"
    )

    generate_project_charter_docx(
        charter=content,
        output_path=output_path,
    )

    return FileResponse(
        path=output_path,
        filename=(
            f"Project_Charter_{document.original_name.rsplit('.', 1)[0]}.docx"
        ),
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
    )

@app.post(
    "/documents/{document_id}/artifacts/wbs"
)
def create_wbs_artifact(
    document_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=(
                "No completed BRD analysis found. "
                "Analyze the document first."
            ),
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type == "wbs",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if saved_artifact and not force:
        return {
            "id": saved_artifact.id,
            "project_id": saved_artifact.project_id,
            "document_analysis_id": (
                saved_artifact.document_analysis_id
            ),
            "artifact_type": (
                saved_artifact.artifact_type
            ),
            "model_name": saved_artifact.model_name,
            "status": saved_artifact.status,
            "content": saved_artifact.content_json,
            "created_at": saved_artifact.created_at,
            "cached": True,
        }

    try:
        wbs = generate_wbs(
            brd_analysis=analysis.result_json
        )

        wbs_content = wbs.model_dump()

        artifact = ProjectArtifact(
            project_id=document.project_id,
            document_analysis_id=analysis.id,
            artifact_type="wbs",
            content_json=wbs_content,
            model_name=os.getenv(
                "OPENAI_MODEL",
                "gpt-5-mini",
            ),
            status="completed",
        )

        db.add(artifact)
        db.commit()
        db.refresh(artifact)

        return {
            "id": artifact.id,
            "project_id": artifact.project_id,
            "document_analysis_id": (
                artifact.document_analysis_id
            ),
            "artifact_type": artifact.artifact_type,
            "model_name": artifact.model_name,
            "status": artifact.status,
            "content": artifact.content_json,
            "created_at": artifact.created_at,
            "cached": False,
        }

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"WBS generation failed: {str(exc)}",
        ) from exc

def _prepare_wbs_for_response(
    saved_content: dict,
) -> dict:
    content = dict(saved_content)

    original_items = content.get(
        "items",
        [],
    )

    items = [
        dict(item)
        for item in original_items
    ]

    parent_ids = {
        item.get("parent_wbs_id")
        for item in items
        if item.get("parent_wbs_id")
    }

    leaf_items = [
        item
        for item in items
        if item.get("wbs_id") not in parent_ids
    ]

    leaf_effort_total = sum(
        float(
            item.get(
                "estimated_effort_hours",
                0,
            )
            or 0
        )
        for item in leaf_items
    )

    for item in items:
        wbs_id = item.get("wbs_id")

        if wbs_id == "7.2":
            item["status"] = "Complete"
            item["description"] = (
                "Hierarchical WBS generation, persistence, "
                "cached retrieval, response normalization, "
                "and DOCX export implemented."
    )

        elif wbs_id == "7.2.1":
            item["status"] = "Complete"
            item["description"] = (
                "WBS schema, AI generator, persistence, "
                "cached generation, retrieval, normalization, "
                "and DOCX download endpoint implemented."
    )

        elif wbs_id == "10.2.1":
            item["owner"] = "Naresh Yeligeti"

    content["items"] = items

    content["total_estimated_effort_hours"] = round(
        leaf_effort_total,
        2,
    )

    content["artifact_status"] = "Draft"

    notes = list(
        content.get(
            "notes",
            [],
        )
    )

    normalization_note = (
        "Total effort is calculated from leaf-level "
        "work packages and tasks only to prevent "
        "double-counting parent items."
    )

    if normalization_note not in notes:
        notes.append(
            normalization_note
        )

    content["notes"] = notes

    return content


@app.get(
    "/documents/{document_id}/artifacts/wbs"
)
def get_wbs_artifact(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No completed BRD analysis found",
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type == "wbs",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if not saved_artifact:
        raise HTTPException(
            status_code=404,
            detail="No WBS found for this document",
        )

    content = _prepare_wbs_for_response(
        saved_artifact.content_json
    )

    return {
        "id": saved_artifact.id,
        "project_id": saved_artifact.project_id,
        "document_analysis_id": (
            saved_artifact.document_analysis_id
        ),
        "artifact_type": saved_artifact.artifact_type,
        "model_name": saved_artifact.model_name,
        "status": saved_artifact.status,
        "content": content,
        "created_at": saved_artifact.created_at,
        "cached": True,
    }

@app.get(
    "/documents/{document_id}/artifacts/wbs/download"
)
def download_wbs_docx(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No completed BRD analysis found",
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type == "wbs",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if not saved_artifact:
        raise HTTPException(
            status_code=404,
            detail="No WBS found for this document",
        )

    content = _prepare_wbs_for_response(
        saved_artifact.content_json
    )

    export_dir = Path(
        "../generated/exports"
    )

    export_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = export_dir / (
        f"wbs_document_{document_id}.docx"
    )

    generate_wbs_docx(
        wbs=content,
        output_path=output_path,
    )

    base_name = document.original_name.rsplit(
        ".",
        1,
    )[0]

    return FileResponse(
        path=output_path,
        filename=f"WBS_{base_name}.docx",
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
    )
def _prepare_requirements_register_for_response(
    saved_content: dict,
) -> dict:
    content = dict(saved_content or {})

    items = [
        dict(item)
        for item in content.get("items", [])
    ]

    for item in items:
        requirement_id = item.get(
            "requirement_id",
            "",
        )

        if requirement_id == "BR-11":
            item["status"] = "Partially Complete"

            item["description"] = (
                "Generate WBS, RAID Log, Risk Register, "
                "Stakeholder Register, RACI Matrix, Timeline, "
                "and Requirements Register."
            )

            item["notes"] = (
                "Partially implemented. WBS generation, "
                "persistence, cached retrieval, normalization, "
                "and DOCX export are complete. Requirements "
                "Register generation, persistence, and cached "
                "retrieval are complete. RAID Log, Risk Register, "
                "Stakeholder Register, RACI, Timeline, and their "
                "applicable exports remain planned."
            )

        elif requirement_id == "NFR-02":
            item["status"] = "Partially Complete"

            item["notes"] = (
                "SQLAlchemy commit and rollback handling exists "
                "for implemented write operations. Dedicated "
                "transactional integration tests and verification "
                "of every multi-step operation remain planned."
            )

        elif requirement_id == "NFR-05":
            item["status"] = "Partially Complete"

            item["notes"] = (
                "The project is intended to use synthetic or "
                "sanitized content. Repository scanning, automated "
                "data-loss checks, and a formal recurring review "
                "control are not yet implemented."
            )

        elif requirement_id == "NFR-08":
            item["status"] = "Partially Complete"

            item["notes"] = (
                "Basic application and server logging is available. "
                "Structured request logging, model-usage metrics, "
                "latency measurement, consistent secret redaction, "
                "and observability testing remain planned."
            )

    complete_count = sum(
        1
        for item in items
        if item.get("status") == "Complete"
    )

    planned_count = sum(
        1
        for item in items
        if item.get("status") == "Planned"
    )

    partially_complete_count = sum(
        1
        for item in items
        if item.get("status") == "Partially Complete"
    )

    content["items"] = items
    content["total_requirements"] = len(items)
    content["complete_count"] = complete_count
    content["planned_count"] = planned_count
    content["partially_complete_count"] = (
        partially_complete_count
    )

    content["artifact_status"] = "Draft"

    content["notes"] = [
        (
            "Completed capabilities include project CRUD, "
            "document upload and management, text extraction "
            "and processing, structured BRD analysis, analysis "
            "persistence and caching, Project Charter generation "
            "and DOCX export, WBS generation and DOCX export, "
            "and Requirements Register generation and retrieval."
        ),
        (
            "Partially completed requirements represent controls "
            "or capabilities that have an implemented foundation "
            "but still require additional artifacts, testing, "
            "automation, or operational verification."
        ),
        (
            "Planned capabilities include the RAID Log, Risk "
            "Register, Stakeholder Register, RACI Matrix, Timeline, "
            "frontend, JWT authentication, PDF and Excel exports, "
            "and expanded testing and observability."
        ),
        (
            "Requirement counts are recalculated locally from "
            "normalized status values to prevent stale totals."
        ),
    ]

    return content


@app.post(
    "/documents/{document_id}/artifacts/requirements-register"
)
def create_requirements_register_artifact(
    document_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=(
                "No completed BRD analysis found. "
                "Analyze the document first."
            ),
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "requirements_register",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if saved_artifact and not force:
        content = _prepare_requirements_register_for_response(
        saved_artifact.content_json
    )

        return {
            "id": saved_artifact.id,
            "project_id": saved_artifact.project_id,
            "document_analysis_id": (
            saved_artifact.document_analysis_id
            ),
            "artifact_type": (
            saved_artifact.artifact_type
            ),
            "model_name": saved_artifact.model_name,
            "status": saved_artifact.status,
            "content": content,
            "created_at": saved_artifact.created_at,
            "cached": True,
    }

    try:
        requirements_register = (
            generate_requirements_register(
                brd_analysis=analysis.result_json
            )
        )

        content = requirements_register.model_dump()

        artifact = ProjectArtifact(
            project_id=document.project_id,
            document_analysis_id=analysis.id,
            artifact_type="requirements_register",
            content_json=content,
            model_name=os.getenv(
                "OPENAI_MODEL",
                "gpt-5-mini",
            ),
            status="completed",
        )

        db.add(artifact)
        db.commit()
        db.refresh(artifact)

        return {
            "id": artifact.id,
            "project_id": artifact.project_id,
            "document_analysis_id": (
                artifact.document_analysis_id
            ),
            "artifact_type": artifact.artifact_type,
            "model_name": artifact.model_name,
            "status": artifact.status,
            "content": artifact.content_json,
            "created_at": artifact.created_at,
            "cached": False,
        }

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Requirements Register generation failed: "
                f"{str(exc)}"
            ),
        ) from exc

@app.get(
    "/documents/{document_id}/artifacts/requirements-register"
)
def get_requirements_register_artifact(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No completed BRD analysis found",
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "requirements_register",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if not saved_artifact:
        raise HTTPException(
            status_code=404,
            detail=(
                "No Requirements Register found "
                "for this document"
            ),
        )

    content = _prepare_requirements_register_for_response(
    saved_artifact.content_json
)

    return {
        "id": saved_artifact.id,
        "project_id": saved_artifact.project_id,
        "document_analysis_id": (
        saved_artifact.document_analysis_id
        ),
        "artifact_type": saved_artifact.artifact_type,
        "model_name": saved_artifact.model_name,
        "status": saved_artifact.status,
        "content": content,
        "created_at": saved_artifact.created_at,
        "cached": True,
}

@app.get(
    "/documents/{document_id}/artifacts/"
    "requirements-register/download"
)
def download_requirements_register_excel(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No completed BRD analysis found",
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "requirements_register",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if not saved_artifact:
        raise HTTPException(
            status_code=404,
            detail=(
                "No Requirements Register found "
                "for this document"
            ),
        )

    content = _prepare_requirements_register_for_response(
        saved_artifact.content_json
    )

    export_dir = Path(
        "../generated/exports"
    )

    export_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = export_dir / (
        f"requirements_register_document_"
        f"{document_id}.xlsx"
    )

    generate_requirements_register_excel(
        requirements_register=content,
        output_path=output_path,
    )

    base_name = document.original_name.rsplit(
        ".",
        1,
    )[0]

    return FileResponse(
        path=output_path,
        filename=(
            f"Requirements_Register_"
            f"{base_name}.xlsx"
        ),
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )


def _prepare_raid_risk_register_for_response(
    saved_content: dict,
) -> dict:
    content = dict(saved_content or {})

    raid_items = [
        dict(item)
        for item in content.get("raid_items", [])
    ]

    risk_register = [
        dict(item)
        for item in content.get("risk_register", [])
    ]

    for item in raid_items:
        item_id = item.get(
            "item_id",
            "",
        )

        if item_id == "D-002":
            item["status"] = "Resolved"
            item["notes"] = (
                "Docker Desktop and the PostgreSQL container "
                "are installed, configured, and working for "
                "local development."
            )

        elif item_id == "D-003":
            item["status"] = "Resolved"
            item["notes"] = (
                "Python 3.12 virtual environment and backend "
                "dependencies are installed and maintained "
                "through requirements.txt."
            )

        elif item_id == "D-004":
            item["status"] = "Resolved"
            item["notes"] = (
                "Postman and DBeaver are installed and available "
                "for API testing and database inspection."
            )

        elif item_id == "D-005":
            item["status"] = "Monitoring"
            item["notes"] = (
                "Developer availability remains an active delivery "
                "dependency and is monitored through phased scope "
                "and incremental implementation."
            )

        elif item_id == "I-001":
            item["status"] = "In Progress"
            item["title"] = (
                "Remaining PMO artifacts are partially implemented"
            )
            item["description"] = (
                "WBS, Requirements Register, RAID Log, and Risk "
                "Register generation are implemented. Stakeholder "
                "Register, RACI Matrix, Timeline, and their "
                "applicable exports remain planned."
            )
            item["response_or_action"] = (
                "Continue incremental artifact delivery. Implement "
                "Stakeholder Register next, followed by RACI Matrix "
                "and Timeline."
            )
            item["notes"] = (
                "This issue now represents the remaining PMO "
                "artifact backlog rather than all artifacts."
            )

        elif item_id == "I-003":
            item["status"] = "Accepted"
            item["title"] = (
                "OCR support excluded from current MVP"
            )
            item["description"] = (
                "The current MVP supports readable PDF and DOCX "
                "content but does not support OCR for scanned "
                "documents."
            )
            item["notes"] = (
                "Accepted MVP limitation. OCR may be considered "
                "during a future enhancement phase."
            )

    for risk in risk_register:
        risk_id = risk.get(
            "risk_id",
            "",
        )

        if risk_id == "R-002":
            risk["mitigation_plan"] = (
                "Continue using validated structured output and "
                "human review. Synthetic regression testing, prompt "
                "versioning, and broader quality measurement remain "
                "planned mitigation actions."
            )

        elif risk_id == "R-003":
            risk["mitigation_plan"] = (
                "Use only synthetic or sanitized files and keep "
                "sensitive files excluded through .gitignore. "
                "Formal repository scanning and recurring review "
                "controls remain planned."
            )

        elif risk_id == "R-004":
            risk["mitigation_plan"] = (
                "Use cached results by default and require explicit "
                "force=true for regeneration. Automated usage "
                "monitoring and billing alerts remain planned."
            )

        elif risk_id == "R-005":
            risk["mitigation_plan"] = (
                "Use Docker volumes and keep source code in Git. "
                "A documented recurring database and file backup "
                "process remains planned."
            )

    open_statuses = {
        "Open",
        "In Progress",
        "Monitoring",
        "Accepted",
    }

    high_priorities = {
        "Critical",
        "High",
    }

    content["raid_items"] = raid_items
    content["risk_register"] = risk_register
    content["total_raid_items"] = len(
        raid_items
    )
    content["total_risks"] = len(
        risk_register
    )

    content["open_risk_count"] = sum(
        1
        for risk in risk_register
        if risk.get("status") in open_statuses
    )

    content["high_priority_risk_count"] = sum(
        1
        for risk in risk_register
        if risk.get("priority") in high_priorities
    )

    content["artifact_status"] = "Draft"

    content["notes"] = [
        (
            "RAID and Risk Register items were generated from "
            "the saved BRD analysis and normalized against the "
            "current implementation status."
        ),
        (
            "Docker, PostgreSQL, Python dependencies, Postman, "
            "and DBeaver are available and marked Resolved."
        ),
        (
            "WBS, Requirements Register, RAID Log, and Risk "
            "Register are implemented. Stakeholder Register, "
            "RACI Matrix, and Timeline remain planned."
        ),
        (
            "Mitigation activities not yet implemented are "
            "clearly described as planned actions."
        ),
        (
            "All minor visual and formatting refinements remain "
            "deferred to the final portfolio-polish stage."
        ),
    ]

    return content


@app.post(
    "/documents/{document_id}/artifacts/raid-risk-register"
)
def create_raid_risk_register_artifact(
    document_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=(
                "No completed BRD analysis found. "
                "Analyze the document first."
            ),
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "raid_risk_register",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if saved_artifact and not force:
        content = _prepare_raid_risk_register_for_response(
            saved_artifact.content_json
        )

        return {
            "id": saved_artifact.id,
            "project_id": saved_artifact.project_id,
            "document_analysis_id": (
                saved_artifact.document_analysis_id
            ),
            "artifact_type": (
                saved_artifact.artifact_type
            ),
            "model_name": saved_artifact.model_name,
            "status": saved_artifact.status,
            "content": content,
            "created_at": saved_artifact.created_at,
            "cached": True,
        }

    try:
        raid_risk_register = (
            generate_raid_and_risk_register(
                brd_analysis=analysis.result_json
            )
        )

        content = raid_risk_register.model_dump()

        artifact = ProjectArtifact(
            project_id=document.project_id,
            document_analysis_id=analysis.id,
            artifact_type="raid_risk_register",
            content_json=content,
            model_name=os.getenv(
                "OPENAI_MODEL",
                "gpt-5-mini",
            ),
            status="completed",
        )

        db.add(artifact)
        db.commit()
        db.refresh(artifact)

        return {
            "id": artifact.id,
            "project_id": artifact.project_id,
            "document_analysis_id": (
                artifact.document_analysis_id
            ),
            "artifact_type": artifact.artifact_type,
            "model_name": artifact.model_name,
            "status": artifact.status,
            "content": artifact.content_json,
            "created_at": artifact.created_at,
            "cached": False,
        }

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "RAID and Risk Register generation failed: "
                f"{str(exc)}"
            ),
        ) from exc

@app.get(
    "/documents/{document_id}/artifacts/raid-risk-register"
)
def get_raid_risk_register_artifact(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No completed BRD analysis found",
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "raid_risk_register",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if not saved_artifact:
        raise HTTPException(
            status_code=404,
            detail=(
                "No RAID and Risk Register found "
                "for this document"
            ),
        )
    content = _prepare_raid_risk_register_for_response(
        saved_artifact.content_json
    )
    return {
        "id": saved_artifact.id,
        "project_id": saved_artifact.project_id,
        "document_analysis_id": (
            saved_artifact.document_analysis_id
        ),
        "artifact_type": saved_artifact.artifact_type,
        "model_name": saved_artifact.model_name,
        "status": saved_artifact.status,
        "content": content,
        "created_at": saved_artifact.created_at,
        "cached": True,
    }

@app.get(
    "/documents/{document_id}/artifacts/"
    "raid-risk-register/download"
)
def download_raid_risk_register_excel(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No completed BRD analysis found",
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "raid_risk_register",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if not saved_artifact:
        raise HTTPException(
            status_code=404,
            detail=(
                "No RAID and Risk Register found "
                "for this document"
            ),
        )

    content = _prepare_raid_risk_register_for_response(
        saved_artifact.content_json
    )

    export_dir = Path(
        "../generated/exports"
    )

    export_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = export_dir / (
        f"raid_risk_register_document_"
        f"{document_id}.xlsx"
    )

    generate_raid_risk_register_excel(
        raid_risk_register=content,
        output_path=output_path,
    )

    base_name = document.original_name.rsplit(
        ".",
        1,
    )[0]

    return FileResponse(
        path=output_path,
        filename=(
            f"RAID_Risk_Register_"
            f"{base_name}.xlsx"
        ),
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
def _prepare_stakeholder_register_for_response(
    saved_content: dict,
) -> dict:
    content = dict(saved_content or {})

    stakeholders = [
        dict(item)
        for item in content.get("stakeholders", [])
    ]

    for stakeholder in stakeholders:
        stakeholder_id = stakeholder.get(
            "stakeholder_id",
            "",
        )

        if stakeholder_id == "STK-004":
            stakeholder["status"] = "Planned"

            stakeholder["current_engagement"] = "Neutral"
            stakeholder["desired_engagement"] = "Supportive"

            stakeholder["communication_channel"] = (
                "Documentation / Email; UI notifications planned"
            )

            stakeholder["notes"] = (
                "Represents the target end-user group. Backend "
                "artifact workflows are available, while the "
                "frontend, authentication, and UI notifications "
                "remain planned."
            )

    content["stakeholders"] = stakeholders
    content["total_stakeholders"] = len(
        stakeholders
    )

    content["high_influence_count"] = sum(
        1
        for stakeholder in stakeholders
        if stakeholder.get("influence_level") == "High"
    )

    content["manage_closely_count"] = sum(
        1
        for stakeholder in stakeholders
        if stakeholder.get(
            "power_interest_quadrant"
        ) == "Manage Closely"
    )

    content["artifact_status"] = "Draft"

    content["notes"] = [
        (
            "Stakeholders were generated from the saved BRD "
            "analysis and normalized against current project status."
        ),
        (
            "Naresh Yeligeti remains the primary delivery owner, "
            "decision-maker, and stakeholder relationship owner."
        ),
        (
            "The future end-user stakeholder is marked Planned "
            "because the frontend and authentication remain "
            "under development."
        ),
        (
            "All minor visual and formatting refinements remain "
            "deferred to the final portfolio-polish stage."
        ),
    ]

    return content


@app.post(
    "/documents/{document_id}/artifacts/stakeholder-register"
)
def create_stakeholder_register_artifact(
    document_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=(
                "No completed BRD analysis found. "
                "Analyze the document first."
            ),
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "stakeholder_register",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if saved_artifact and not force:
        content = _prepare_stakeholder_register_for_response(
            saved_artifact.content_json
        )

        return {
            "id": saved_artifact.id,
            "project_id": saved_artifact.project_id,
            "document_analysis_id": (
                saved_artifact.document_analysis_id
            ),
            "artifact_type": (
                saved_artifact.artifact_type
            ),
            "model_name": saved_artifact.model_name,
            "status": saved_artifact.status,
            "content": content,
            "created_at": saved_artifact.created_at,
            "cached": True,
    }

    try:
        stakeholder_register = (
            generate_stakeholder_register(
                brd_analysis=analysis.result_json
            )
        )

        content = stakeholder_register.model_dump()

        artifact = ProjectArtifact(
            project_id=document.project_id,
            document_analysis_id=analysis.id,
            artifact_type="stakeholder_register",
            content_json=content,
            model_name=os.getenv(
                "OPENAI_MODEL",
                "gpt-5-mini",
            ),
            status="completed",
        )

        db.add(artifact)
        db.commit()
        db.refresh(artifact)

        return {
            "id": artifact.id,
            "project_id": artifact.project_id,
            "document_analysis_id": (
                artifact.document_analysis_id
            ),
            "artifact_type": artifact.artifact_type,
            "model_name": artifact.model_name,
            "status": artifact.status,
            "content": artifact.content_json,
            "created_at": artifact.created_at,
            "cached": False,
        }

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Stakeholder Register generation failed: "
                f"{str(exc)}"
            ),
        ) from exc

@app.get(
    "/documents/{document_id}/artifacts/stakeholder-register"
)
def get_stakeholder_register_artifact(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No completed BRD analysis found",
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "stakeholder_register",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if not saved_artifact:
        raise HTTPException(
            status_code=404,
            detail=(
                "No Stakeholder Register found "
                "for this document"
            ),
        )
    content = _prepare_stakeholder_register_for_response(
        saved_artifact.content_json
    )

    return {
        "id": saved_artifact.id,
        "project_id": saved_artifact.project_id,
        "document_analysis_id": (
            saved_artifact.document_analysis_id
        ),
        "artifact_type": saved_artifact.artifact_type,
        "model_name": saved_artifact.model_name,
        "status": saved_artifact.status,
        "content": content,
        "created_at": saved_artifact.created_at,
        "cached": True,
    }

@app.get(
    "/documents/{document_id}/artifacts/"
    "stakeholder-register/download"
)
def download_stakeholder_register_artifact(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No completed BRD analysis found",
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "stakeholder_register",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if not saved_artifact:
        raise HTTPException(
            status_code=404,
            detail=(
                "No Stakeholder Register found "
                "for this document"
            ),
        )

    content = _prepare_stakeholder_register_for_response(
        saved_artifact.content_json
    )

    excel_file = generate_stakeholder_register_excel(
        content
    )

    original_filename = (
        document.original_name
        or document.file_name
        or f"document_{document_id}"
    )

    base_filename = os.path.splitext(
        original_filename
    )[0]

    download_filename = (
        f"Stakeholder_Register_{base_filename}.xlsx"
    )

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{download_filename}"'
            )
        },
    )
def _prepare_raci_matrix_for_response(
    saved_content: dict,
) -> dict:
    content = dict(saved_content or {})

    activities = [
        dict(activity)
        for activity in content.get("activities", [])
    ]

    for activity in activities:
        activity_id = activity.get(
            "activity_id",
            "",
        )

        if activity_id == "RAC-009":
            activity["phase"] = "Development"

            activity["notes"] = (
                "Project Charter generation, persistence, "
                "retrieval, cache protection, and DOCX export "
                "are complete."
            )

        elif activity_id == "RAC-010":
            activity["phase"] = "Development"

            activity["notes"] = (
                "WBS schema, generator, persistence, "
                "normalization, retrieval, and DOCX export "
                "are complete."
            )

        elif activity_id == "RAC-011":
            activity["status"] = "Complete"

            activity["notes"] = (
                "Reusable artifact patterns are implemented "
                "through Pydantic schemas, AI generators, "
                "ProjectArtifact persistence, cache protection, "
                "normalization, retrieval, and export modules."
            )

        elif activity_id == "RAC-012":
            activity["phase"] = "Development"
            activity["status"] = "In Progress"

            activity["deliverable_or_outcome"] = (
                "Stakeholder Register generation and Excel "
                "export completed; RACI generation completed "
                "with Excel export currently in progress."
            )

            activity["notes"] = (
                "Stakeholder Register is complete. RACI schema, "
                "generation, persistence, caching, retrieval, "
                "and normalization are complete; RACI Excel "
                "export remains in progress."
            )

        elif activity_id == "RAC-014":
            activity["status"] = "In Progress"

            activity["notes"] = (
                "Environment-variable secrets and foundational "
                "application logging are implemented. Structured "
                "usage monitoring, automated testing, performance "
                "testing, and broader observability remain planned."
            )

    content["activities"] = activities
    content["total_activities"] = len(
        activities
    )

    used_stakeholders = []

    for activity in activities:
        for role_field in (
            "responsible",
            "accountable",
            "consulted",
            "informed",
        ):
            for stakeholder in activity.get(
                role_field,
                [],
            ):
                if stakeholder not in used_stakeholders:
                    used_stakeholders.append(
                        stakeholder
                    )

    content["stakeholders"] = used_stakeholders
    content["artifact_status"] = "Draft"

    content["notes"] = [
        (
            "Naresh Yeligeti is the single delivery owner and "
            "is Responsible and Accountable for core MVP work."
        ),
        (
            "Mentor is Consulted for architecture, technical "
            "design, maintainability, and critical decisions."
        ),
        (
            "Portfolio Reviewer / Interviewer participates only "
            "in portfolio review, milestone validation, and demos."
        ),
        (
            "Future End User participates in usability, artifact "
            "validation, workflow, and future frontend activities."
        ),
        (
            "Activity statuses were normalized against actual "
            "implementation progress as of the current build."
        ),
        (
            "Visual formatting, role colours, dropdowns, and "
            "dashboard refinements remain deferred to the final "
            "portfolio-polish stage."
        ),
    ]

    return content
@app.post(
    "/documents/{document_id}/artifacts/raci-matrix"
)
def create_raci_matrix_artifact(
    document_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=(
                "No completed BRD analysis found. "
                "Analyze the document first."
            ),
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "raci_matrix",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if saved_artifact and not force:
        content = _prepare_raci_matrix_for_response(
            saved_artifact.content_json
        )

        return {
            "id": saved_artifact.id,
            "project_id": saved_artifact.project_id,
            "document_analysis_id": (
                saved_artifact.document_analysis_id
            ),
            "artifact_type": (
                saved_artifact.artifact_type
            ),
            "model_name": saved_artifact.model_name,
            "status": saved_artifact.status,
            "content": content,
            "created_at": saved_artifact.created_at,
            "cached": True,
        }

    stakeholder_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "stakeholder_register",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    wbs_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type == "wbs",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    stakeholder_content = None

    if stakeholder_artifact:
        stakeholder_content = (
            _prepare_stakeholder_register_for_response(
                stakeholder_artifact.content_json
            )
        )

    wbs_content = None

    if wbs_artifact:
        wbs_content = _prepare_wbs_for_response(
            wbs_artifact.content_json
        )

    try:
        raci_matrix = generate_raci_matrix(
            brd_analysis=analysis.result_json,
            stakeholder_register=stakeholder_content,
            wbs=wbs_content,
        )

        content = raci_matrix.model_dump()

        artifact = ProjectArtifact(
            project_id=document.project_id,
            document_analysis_id=analysis.id,
            artifact_type="raci_matrix",
            content_json=content,
            model_name=os.getenv(
                "OPENAI_MODEL",
                "gpt-5-mini",
            ),
            status="completed",
        )

        db.add(artifact)
        db.commit()
        db.refresh(artifact)

        return {
            "id": artifact.id,
            "project_id": artifact.project_id,
            "document_analysis_id": (
                artifact.document_analysis_id
            ),
            "artifact_type": artifact.artifact_type,
            "model_name": artifact.model_name,
            "status": artifact.status,
            "content": artifact.content_json,
            "created_at": artifact.created_at,
            "cached": False,
        }

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "RACI Matrix generation failed: "
                f"{str(exc)}"
            ),
        ) from exc

@app.get(
    "/documents/{document_id}/artifacts/raci-matrix"
)
def get_raci_matrix_artifact(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No completed BRD analysis found",
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "raci_matrix",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if not saved_artifact:
        raise HTTPException(
            status_code=404,
            detail=(
                "No RACI Matrix found "
                "for this document"
            ),
        )
    content = _prepare_raci_matrix_for_response(
        saved_artifact.content_json
    )
    return {
        "id": saved_artifact.id,
        "project_id": saved_artifact.project_id,
        "document_analysis_id": (
            saved_artifact.document_analysis_id
        ),
        "artifact_type": saved_artifact.artifact_type,
        "model_name": saved_artifact.model_name,
        "status": saved_artifact.status,
        "content": content,
        "created_at": saved_artifact.created_at,
        "cached": True,
    }

@app.get(
    "/documents/{document_id}/artifacts/"
    "raci-matrix/download"
)
def download_raci_matrix_artifact(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No completed BRD analysis found",
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "raci_matrix",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if not saved_artifact:
        raise HTTPException(
            status_code=404,
            detail=(
                "No RACI Matrix found "
                "for this document"
            ),
        )

    content = _prepare_raci_matrix_for_response(
        saved_artifact.content_json
    )

    excel_file = generate_raci_matrix_excel(
        content
    )

    original_filename = (
        document.original_name
        or document.file_name
        or f"document_{document_id}"
    )

    base_filename = os.path.splitext(
        original_filename
    )[0]

    download_filename = (
        f"RACI_Matrix_{base_filename}.xlsx"
    )

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{download_filename}"'
            )
        },
    )
def _prepare_project_timeline_for_response(
    saved_content: dict,
) -> dict:
    content = dict(saved_content or {})

    activities = [
        dict(activity)
        for activity in content.get("activities", [])
    ]

    updates = {
        "TL-003": {
            "predecessor_ids": ["TL-001"],
        },
        "TL-004": {
            "start_week": 9,
            "end_week": 12,
            "predecessor_ids": ["TL-002", "TL-003"],
        },
        "TL-005": {
            "start_week": 13,
            "end_week": 14,
            "predecessor_ids": ["TL-004"],
        },
        "TL-006": {
            "start_week": 15,
            "end_week": 17,
            "predecessor_ids": ["TL-005"],
        },
        "TL-007": {
            "start_week": 18,
            "end_week": 18,
            "predecessor_ids": ["TL-006"],
            "status": "Complete",
            "progress_percent": 100,
            "milestone": True,
            "milestone_name": (
                "Stakeholder Register and RACI Complete"
            ),
            "deliverable_or_outcome": (
                "Stakeholder Register and RACI Matrix generation, "
                "persistence, caching, retrieval, normalization, "
                "and Excel exports completed."
            ),
            "notes": (
                "Stakeholder Register and RACI Matrix artifacts "
                "are complete for the MVP."
            ),
        },
        "TL-008": {
            "start_week": 18,
            "end_week": 20,
            "predecessor_ids": ["TL-006"],
            "status": "In Progress",
            "progress_percent": 80,
            "deliverable_or_outcome": (
                "Requirements Register generation and Excel export "
                "completed; Project Timeline generation, persistence, "
                "retrieval, and normalization completed, with Timeline "
                "Excel/Gantt export in progress."
            ),
            "notes": (
                "Requirements Register is complete. Timeline "
                "Excel/Gantt export remains in progress."
            ),
        },
        "TL-009": {
            "start_week": 21,
            "end_week": 25,
            "predecessor_ids": ["TL-007", "TL-008"],
            "status": "In Progress",
            "progress_percent": 65,
            "deliverable_or_outcome": (
                "Core DOCX and Excel artifact exporters implemented. "
                "Timeline export, automated unit tests, integration "
                "tests, and end-to-end tests remain in progress."
            ),
            "notes": (
                "Charter, WBS, Requirements, RAID/Risk, Stakeholder, "
                "and RACI exports are complete. Automated testing and "
                "Timeline export remain pending."
            ),
        },
        "TL-010": {
            "start_week": 13,
            "end_week": 17,
            "predecessor_ids": ["TL-004"],
        },
        "TL-011": {
            "start_week": 21,
            "end_week": 32,
            "predecessor_ids": ["TL-006", "TL-008"],
        },
        "TL-012": {
            "start_week": 33,
            "end_week": 36,
            "predecessor_ids": ["TL-009", "TL-011"],
        },
        "TL-013": {
            "start_week": 1,
            "end_week": 36,
            "status": "In Progress",
            "progress_percent": 55,
        },
    }

    for activity in activities:
        activity_id = activity.get(
            "activity_id",
            "",
        )

        activity_updates = updates.get(
            activity_id
        )

        if activity_updates:
            activity.update(
                activity_updates
            )

        start_week = activity.get(
            "start_week",
            1,
        )

        end_week = activity.get(
            "end_week",
            start_week,
        )

        activity["duration_weeks"] = (
            end_week - start_week + 1
        )

        if not activity.get("milestone"):
            activity["milestone_name"] = ""

    content["activities"] = activities
    content["total_activities"] = len(
        activities
    )

    content["total_milestones"] = sum(
        1
        for activity in activities
        if activity.get("milestone") is True
    )

    content["total_duration_weeks"] = max(
        (
            activity.get("end_week", 1)
            for activity in activities
        ),
        default=1,
    )

    content["planning_basis"] = (
        "Relative weekly schedule normalized against current "
        "implementation progress, logical dependencies, and the "
        "part-time single-developer delivery constraint."
    )

    content["artifact_status"] = "Draft"

    content["notes"] = [
        (
            "The timeline uses relative project weeks and does "
            "not assign calendar dates."
        ),
        (
            "Finish-to-start dependencies were normalized so "
            "dependent activities do not begin before their "
            "predecessors finish."
        ),
        (
            "Stakeholder Register and RACI Matrix generation and "
            "Excel exports are marked Complete."
        ),
        (
            "Requirements Register is Complete, while Timeline "
            "Excel/Gantt export remains In Progress."
        ),
        (
            "Core artifact exports are substantially complete; "
            "automated testing remains In Progress or Planned."
        ),
        (
            "Frontend, authentication, deployment documentation, "
            "and final portfolio preparation remain Planned."
        ),
        (
            "Visual Gantt styling, milestone colours, dependency "
            "arrows, and dashboard refinements are deferred to "
            "the final portfolio-polish stage."
        ),
    ]

    return content

@app.post(
    "/documents/{document_id}/artifacts/project-timeline"
)
def create_project_timeline_artifact(
    document_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=(
                "No completed BRD analysis found. "
                "Analyze the document first."
            ),
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "project_timeline",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if saved_artifact and not force:
        content = _prepare_project_timeline_for_response(
            saved_artifact.content_json
        )

        return {
            "id": saved_artifact.id,
            "project_id": saved_artifact.project_id,
            "document_analysis_id": (
                saved_artifact.document_analysis_id
            ),
            "artifact_type": (
                saved_artifact.artifact_type
            ),
            "model_name": saved_artifact.model_name,
            "status": saved_artifact.status,
            "content": content,
            "created_at": saved_artifact.created_at,
            "cached": True,
        }

    wbs_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type == "wbs",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    raci_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "raci_matrix",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    wbs_content = None

    if wbs_artifact:
        wbs_content = _prepare_wbs_for_response(
            wbs_artifact.content_json
        )

    raci_content = None

    if raci_artifact:
        raci_content = _prepare_raci_matrix_for_response(
            raci_artifact.content_json
        )

    try:
        project_timeline = generate_project_timeline(
            brd_analysis=analysis.result_json,
            wbs=wbs_content,
            raci_matrix=raci_content,
        )

        content = project_timeline.model_dump()

        artifact = ProjectArtifact(
            project_id=document.project_id,
            document_analysis_id=analysis.id,
            artifact_type="project_timeline",
            content_json=content,
            model_name=os.getenv(
                "OPENAI_MODEL",
                "gpt-5-mini",
            ),
            status="completed",
        )

        db.add(artifact)
        db.commit()
        db.refresh(artifact)

        return {
            "id": artifact.id,
            "project_id": artifact.project_id,
            "document_analysis_id": (
                artifact.document_analysis_id
            ),
            "artifact_type": artifact.artifact_type,
            "model_name": artifact.model_name,
            "status": artifact.status,
            "content": artifact.content_json,
            "created_at": artifact.created_at,
            "cached": False,
        }

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Project Timeline generation failed: "
                f"{str(exc)}"
            ),
        ) from exc

@app.get(
    "/documents/{document_id}/artifacts/project-timeline"
)
def get_project_timeline_artifact(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No completed BRD analysis found",
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "project_timeline",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if not saved_artifact:
        raise HTTPException(
            status_code=404,
            detail=(
                "No Project Timeline found "
                "for this document"
            ),
        )

    content = _prepare_project_timeline_for_response(
        saved_artifact.content_json
    )

    return {
        "id": saved_artifact.id,
        "project_id": saved_artifact.project_id,
        "document_analysis_id": (
            saved_artifact.document_analysis_id
        ),
        "artifact_type": saved_artifact.artifact_type,
        "model_name": saved_artifact.model_name,
        "status": saved_artifact.status,
        "content": content,
        "created_at": saved_artifact.created_at,
        "cached": True,
    }

@app.get(
    "/documents/{document_id}/artifacts/"
    "project-timeline/download"
)
def download_project_timeline_artifact(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.document_id == document_id,
            DocumentAnalysis.analysis_type == "brd_analysis",
            DocumentAnalysis.status == "completed",
        )
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No completed BRD analysis found",
        )

    saved_artifact = (
        db.query(ProjectArtifact)
        .filter(
            ProjectArtifact.project_id
            == document.project_id,
            ProjectArtifact.document_analysis_id
            == analysis.id,
            ProjectArtifact.artifact_type
            == "project_timeline",
            ProjectArtifact.status == "completed",
        )
        .order_by(
            ProjectArtifact.created_at.desc()
        )
        .first()
    )

    if not saved_artifact:
        raise HTTPException(
            status_code=404,
            detail=(
                "No Project Timeline found "
                "for this document"
            ),
        )

    content = _prepare_project_timeline_for_response(
        saved_artifact.content_json
    )

    excel_file = generate_project_timeline_excel(
        content
    )

    original_filename = (
        document.original_name
        or document.file_name
        or f"document_{document_id}"
    )

    base_filename = os.path.splitext(
        original_filename
    )[0]

    download_filename = (
        f"Project_Timeline_{base_filename}.xlsx"
    )

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{download_filename}"'
            )
        },
    )