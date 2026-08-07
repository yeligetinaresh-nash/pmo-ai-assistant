from sqlalchemy.orm import Session

from app.models.document import UploadedDocument


def create_document(
    db: Session,
    project_id: int,
    file_name: str,
    original_name: str,
    file_type: str,
    file_size: int,
    storage_path: str,
):
    document = UploadedDocument(
        project_id=project_id,
        file_name=file_name,
        original_name=original_name,
        file_type=file_type,
        file_size=file_size,
        storage_path=storage_path,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document

def get_documents_by_project(
    db: Session,
    project_id: int,
):
    return (
        db.query(UploadedDocument)
        .filter(UploadedDocument.project_id == project_id)
        .order_by(UploadedDocument.uploaded_at.desc())
        .all()
    )

def get_document(
    db: Session,
    document_id: int,
):
    return (
        db.query(UploadedDocument)
        .filter(UploadedDocument.id == document_id)
        .first()
    )


def delete_document(
    db: Session,
    document_id: int,
):
    document = (
        db.query(UploadedDocument)
        .filter(UploadedDocument.id == document_id)
        .first()
    )

    if document is None:
        return None

    db.delete(document)
    db.commit()

    return document