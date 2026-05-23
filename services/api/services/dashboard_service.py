from typing import Any, Dict

from services import build_service, franca_service, project_service, simulation_service
from services.docker_manager import docker_ready, get_wireshark_status


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
            "docker": docker_ready(),
            "vsomeip": build_service.runtime_readiness(),
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
