from fastapi import APIRouter

from routes.http_errors import project_error
from routes.v1.common import ERROR_RESPONSES
from schemas.workflow import (
    ProjectCollection,
    ProjectCreateRequest,
    ProjectImportRequest,
    ProjectOverview,
)
from services import project_service, workflow_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get(
    "",
    response_model=ProjectCollection,
    operation_id="getProjects",
)
async def projects():
    return workflow_service.project_collection()


@router.post(
    "",
    response_model=ProjectOverview,
    operation_id="createProject",
    responses=ERROR_RESPONSES,
)
async def create_project(request: ProjectCreateRequest):
    try:
        project_service.create_project(
            request.project_id,
            request.name,
            source_example=request.source_example,
            preset_id=request.preset_id,
        )
        return workflow_service.project_overview(request.project_id)
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        raise project_error(exc)


@router.post(
    "/import",
    response_model=ProjectOverview,
    operation_id="importProject",
    responses=ERROR_RESPONSES,
)
async def import_project(request: ProjectImportRequest):
    try:
        detail = project_service.import_project(request.source_path)
        return workflow_service.project_overview(detail["manifest"]["id"])
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        raise project_error(exc)


@router.get(
    "/{project_id}/overview",
    response_model=ProjectOverview,
    operation_id="getProjectOverview",
    responses=ERROR_RESPONSES,
)
async def project_overview(project_id: str):
    try:
        return workflow_service.project_overview(project_id)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)
