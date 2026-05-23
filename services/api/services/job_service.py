import asyncio
import json
import uuid
from pathlib import Path
from typing import Any, Dict

from services import project_service

JOBS_DIR = project_service.WORKSPACE / "runs" / "jobs"
_queues: Dict[str, list[asyncio.Queue]] = {}


def _path(job_id: str) -> Path:
    return JOBS_DIR / f"{job_id}.json"


def _write(job: Dict[str, Any]) -> None:
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    _path(job["id"]).write_text(json.dumps(job, indent=2) + "\n")


def get_job(job_id: str) -> Dict[str, Any]:
    path = _path(job_id)
    if not path.exists():
        raise FileNotFoundError(job_id)
    return json.loads(path.read_text())


def create_job(kind: str, project_id: str | None = None) -> Dict[str, Any]:
    job = {
        "id": str(uuid.uuid4()),
        "type": kind,
        "project_id": project_id,
        "status": "pending",
        "log": "",
        "created_at": project_service.utc_now(),
    }
    _write(job)
    return job


async def emit(job_id: str, event: Dict[str, Any]) -> None:
    for queue in _queues.get(job_id, []):
        await queue.put(event)


async def append_log(job_id: str, text: str) -> None:
    job = get_job(job_id)
    job["log"] += text
    _write(job)
    await emit(job_id, {"type": "job.log", "job_id": job_id, "text": text})


async def set_status(job_id: str, status: str, **extra: Any) -> None:
    job = get_job(job_id)
    job.update(extra)
    job["status"] = status
    job["updated_at"] = project_service.utc_now()
    _write(job)
    await emit(
        job_id, {"type": "job.status", "job_id": job_id, "status": status, **extra}
    )


def subscribe(job_id: str) -> asyncio.Queue:
    queue: asyncio.Queue = asyncio.Queue()
    _queues.setdefault(job_id, []).append(queue)
    return queue


def unsubscribe(job_id: str, queue: asyncio.Queue) -> None:
    subscribers = _queues.get(job_id, [])
    if queue in subscribers:
        subscribers.remove(queue)
