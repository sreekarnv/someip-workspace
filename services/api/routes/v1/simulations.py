from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from routes.http_errors import project_error
from routes.v1.common import ERROR_RESPONSES
from schemas.workflow import (
    RunDetail,
    RunInspection,
    RunSummary,
    SimulationStartRequest,
    SimulationWorkspace,
)
from services import simulation_service, workflow_service

router = APIRouter(tags=["simulations"])


@router.get(
    "/projects/{project_id}/simulations",
    response_model=SimulationWorkspace,
    operation_id="getProjectSimulations",
    responses=ERROR_RESPONSES,
)
async def project_simulations(project_id: str):
    try:
        return workflow_service.simulation_workspace(project_id)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)


@router.post(
    "/projects/{project_id}/simulations",
    response_model=RunDetail,
    operation_id="startProjectSimulation",
    responses=ERROR_RESPONSES,
)
async def start_simulation(project_id: str, request: SimulationStartRequest):
    try:
        return await simulation_service.create_run(project_id, request.scenario_id)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)


@router.get(
    "/projects/{project_id}/runs",
    response_model=list[RunSummary],
    operation_id="getProjectRuns",
    responses=ERROR_RESPONSES,
)
async def project_runs(project_id: str):
    try:
        return simulation_service.list_project_runs(project_id)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)


@router.get(
    "/runs/{run_id}",
    response_model=RunDetail,
    operation_id="getRun",
    responses=ERROR_RESPONSES,
)
async def run(run_id: str):
    try:
        return simulation_service.get_run(run_id)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)


@router.post(
    "/runs/{run_id}/stop",
    response_model=RunDetail,
    operation_id="stopRun",
    responses=ERROR_RESPONSES,
)
async def stop_run(run_id: str):
    try:
        return await simulation_service.stop_run(run_id)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)


@router.get(
    "/runs/{run_id}/inspection",
    response_model=RunInspection,
    operation_id="getRunInspection",
    responses=ERROR_RESPONSES,
)
async def inspection(run_id: str):
    try:
        return workflow_service.run_inspection(run_id)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)


@router.get(
    "/runs/{run_id}/captures/{capture_name}",
    operation_id="downloadRunCapture",
    responses=ERROR_RESPONSES,
)
async def download_capture(run_id: str, capture_name: str):
    try:
        path = simulation_service.capture_path(run_id, capture_name)
    except (ValueError, FileNotFoundError) as exc:
        raise project_error(exc)
    return FileResponse(
        path, filename=path.name, media_type="application/vnd.tcpdump.pcap"
    )


@router.websocket("/runs/{run_id}/events")
async def run_events(websocket: WebSocket, run_id: str):
    try:
        queue = simulation_service.subscribe(run_id)
    except FileNotFoundError:
        await websocket.close(code=4404)
        return
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(await queue.get())
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        simulation_service.unsubscribe(run_id, queue)
