from fastapi import APIRouter

from schemas.workflow import WorkbenchOverview
from services import workflow_service

router = APIRouter(prefix="/workbench", tags=["workbench"])


@router.get(
    "/overview",
    response_model=WorkbenchOverview,
    operation_id="getWorkbenchOverview",
)
async def workbench_overview():
    return workflow_service.workbench_overview()
