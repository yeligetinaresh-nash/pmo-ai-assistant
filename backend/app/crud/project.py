from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def create_project(db: Session, project: ProjectCreate):
    db_project = Project(
        name=project.name,
        description=project.description,
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


def get_projects(db: Session):
    return db.query(Project).all()


def get_project(db: Session, project_id: int):
    return (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )


def delete_project(db: Session, project_id: int):
    project = get_project(db, project_id)

    if project:
        db.delete(project)
        db.commit()

    return project

def update_project(
    db: Session,
    project_id: int,
    project_data: ProjectUpdate
):
    project = get_project(db, project_id)

    if project is None:
        return None

    project.name = project_data.name
    project.description = project_data.description
    project.status = project_data.status

    db.commit()
    db.refresh(project)

    return project