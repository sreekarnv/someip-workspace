from fastapi import APIRouter

from routes.http_errors import project_error
from routes.v1.common import ERROR_RESPONSES
from schemas.workflow import (
    AuthoringWorkspace,
    DocumentFile,
    DocumentUpdate,
    DocumentWriteResult,
    ValidationResult,
)
from services import franca_service, project_service, workflow_service

router = APIRouter(prefix="/projects", tags=["authoring"])


@router.get(
    "/{project_id}/authoring",
    response_model=AuthoringWorkspace,
    operation_id="getProjectAuthoring",
    responses=ERROR_RESPONSES,
)
async def project_authoring(project_id: str):
    try:
        return workflow_service.authoring_workspace(project_id)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)


@router.get(
    "/{project_id}/documents/{document_id:path}",
    response_model=DocumentFile,
    operation_id="getProjectDocument",
    responses=ERROR_RESPONSES,
)
async def get_document(project_id: str, document_id: str):
    try:
        return project_service.read_document(project_id, document_id)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)


@router.put(
    "/{project_id}/documents/{document_id:path}",
    response_model=DocumentWriteResult,
    operation_id="saveProjectDocument",
    responses=ERROR_RESPONSES,
)
async def save_document(project_id: str, document_id: str, request: DocumentUpdate):
    try:
        return project_service.write_document(project_id, document_id, request.content)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)


@router.post(
    "/{project_id}/authoring/validate",
    response_model=ValidationResult,
    operation_id="validateProjectAuthoring",
    responses=ERROR_RESPONSES,
)
async def validate_authoring(project_id: str):
    try:
        return await franca_service.validate_project(project_id)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)
