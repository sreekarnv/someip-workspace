import asyncio

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from routes.http_errors import project_error
from routes.v1.common import ERROR_RESPONSES
from schemas.workflow import (
    Job,
    PipelineOverview,
    ProjectBuildRequest,
    TaskResponse,
    TaskStatus,
)
from services import job_service, project_service, workflow_service
from services.build_service import build_project
from services.generator_service import generate_project

router = APIRouter(tags=["pipeline"])


@router.get(
    "/projects/{project_id}/pipeline",
    response_model=PipelineOverview,
    operation_id="getProjectPipeline",
    responses=ERROR_RESPONSES,
)
async def project_pipeline(project_id: str):
    try:
        return workflow_service.pipeline_overview(project_id)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)


@router.post(
    "/projects/{project_id}/pipeline/generate",
    response_model=TaskResponse,
    operation_id="generateProjectArtifacts",
    responses=ERROR_RESPONSES,
)
async def generate_artifacts(project_id: str):
    try:
        project_service.load_manifest(project_id)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)
    job = job_service.create_job("project_generate", project_id)
    await job_service.set_status(job["id"], "running")
    asyncio.create_task(_generate(job["id"], project_id))
    return TaskResponse(
        task_id=job["id"],
        status=TaskStatus.RUNNING,
        message="Project generation started",
    )


async def _generate(job_id: str, project_id: str):
    try:
        success = await generate_project(
            project_id, lambda text: job_service.append_log(job_id, text)
        )
        await job_service.set_status(job_id, "completed" if success else "failed")
    except Exception as exc:
        await job_service.set_status(job_id, "failed", error=str(exc))


@router.post(
    "/projects/{project_id}/pipeline/build",
    response_model=TaskResponse,
    operation_id="buildProjectNodes",
    responses=ERROR_RESPONSES,
)
async def build_nodes(project_id: str, request: ProjectBuildRequest):
    try:
        project_service.load_manifest(project_id)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)
    job = job_service.create_job("project_build", project_id)
    await job_service.set_status(job["id"], "running")
    asyncio.create_task(_build(job["id"], project_id, request.clean, request.generate))
    return TaskResponse(
        task_id=job["id"], status=TaskStatus.RUNNING, message="Project build started"
    )


async def _build(job_id: str, project_id: str, clean: bool, generate: bool):
    try:
        success = await build_project(
            project_id,
            clean,
            generate,
            lambda text: job_service.append_log(job_id, text),
        )
        await job_service.set_status(job_id, "completed" if success else "failed")
    except Exception as exc:
        await job_service.set_status(job_id, "failed", error=str(exc))


@router.get(
    "/jobs/{job_id}",
    response_model=Job,
    operation_id="getJob",
    responses=ERROR_RESPONSES,
)
async def job(job_id: str):
    try:
        value = job_service.get_job(job_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"task_id": value.pop("id"), **value}


@router.websocket("/jobs/{job_id}/events")
async def job_events(websocket: WebSocket, job_id: str):
    try:
        job_service.get_job(job_id)
    except FileNotFoundError:
        await websocket.close(code=4404)
        return
    await websocket.accept()
    queue = job_service.subscribe(job_id)
    try:
        while True:
            await websocket.send_json(await queue.get())
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        job_service.unsubscribe(job_id, queue)
