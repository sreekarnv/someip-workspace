import shutil
import subprocess
from typing import Any, Dict

from services import franca_service, project_service, simulation_service
from services.docker_manager import get_wireshark_status


def _docker_ready() -> Dict[str, Any]:
    if not shutil.which("docker"):
        return {"ready": False, "detail": "docker command not found"}
    try:
        result = subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            capture_output=True,
            text=True,
            timeout=4,
        )
    except Exception as exc:
        return {"ready": False, "detail": str(exc)}
    return {
        "ready": result.returncode == 0,
        "detail": (
            result.stdout.strip()
            if result.returncode == 0
            else (result.stderr.strip() or "docker daemon unavailable")
        ),
    }


def overview() -> Dict[str, Any]:
    runs = simulation_service.list_runs(limit=24)
    return {
        "projects": project_service.list_projects(),
        "active_runs": [
            run for run in runs if run["status"] in {"rendered", "starting", "running"}
        ],
        "recent_runs": runs,
        "runtime": {
            "api": {"ready": True, "detail": "FastAPI responding"},
            "docker": _docker_ready(),
            "wireshark": get_wireshark_status(),
            "generators": {
                "core": {
                    "ready": franca_service.CORE_GEN.exists(),
                    "path": franca_service.CORE_GEN.name,
                },
                "someip": {
                    "ready": franca_service.SOMEIP_GEN.exists(),
                    "path": franca_service.SOMEIP_GEN.name,
                },
            },
        },
    }
