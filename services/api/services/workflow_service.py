from typing import Any, Dict, List

from services import dashboard_service, example_catalog, project_service, simulation_service


def _readiness(status: Dict[str, str]) -> int:
    ready = [
        status.get("validation") == "valid",
        status.get("generation") in {"ready", "transport-only"},
        status.get("build") == "ready",
        status.get("last_run") not in {None, "none", "unknown"},
    ]
    return len([item for item in ready if item]) * 25


def _document_refs(project_id: str) -> List[Dict[str, Any]]:
    return project_service.project_workspace(project_id)["documents"]


def _nodes(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "id": node["id"],
            "type": node.get("type", "client"),
            "interface": node.get("interface", "unknown"),
            "app_name": node.get("app_name", node["id"]),
        }
        for node in manifest.get("nodes", [])
    ]


def _interface_index(metadata: Dict[str, Any]) -> Dict[str, Any] | None:
    return metadata.get("interface_index_data")


def workbench_overview() -> Dict[str, Any]:
    overview = dashboard_service.overview()
    return {
        "projects": overview["projects"],
        "active_runs": overview["active_runs"],
        "recent_runs": overview["recent_runs"],
        "runtime": overview["runtime"],
    }


def project_collection() -> Dict[str, Any]:
    return {
        "projects": project_service.list_projects(),
        "presets": example_catalog.public_presets(),
    }


def _readiness_gates(status: Dict[str, str]) -> List[Dict[str, Any]]:
    return [
        {
            "id": "validation",
            "label": "Franca contract",
            "status": status["validation"],
            "ready": status["validation"] == "valid",
            "detail": "Validate source and deployment IDs before generating.",
        },
        {
            "id": "generation",
            "label": "Generated artifacts",
            "status": status["generation"],
            "ready": status["generation"] in {"ready", "transport-only"},
            "detail": "CommonAPI output and node templates must be current.",
        },
        {
            "id": "build",
            "label": "Runnable nodes",
            "status": status["build"],
            "ready": status["build"] == "ready",
            "detail": "Build runnable binaries/images before simulation.",
        },
        {
            "id": "evidence",
            "label": "Run evidence",
            "status": status["last_run"],
            "ready": status["last_run"] not in {"none", "unknown"},
            "detail": "A run produces logs, events, and packet captures.",
        },
    ]


def _recommended_action(
    status: Dict[str, str], runs: List[Dict[str, Any]]
) -> Dict[str, str]:
    if status["validation"] != "valid":
        return {
            "kind": "author",
            "title": "Validate the interface",
            "detail": "Review Franca and deployment diagnostics before code generation.",
        }
    if status["generation"] not in {"ready", "transport-only"}:
        return {
            "kind": "build",
            "title": "Generate project artifacts",
            "detail": "Create CommonAPI artifacts and editable node templates from validated source.",
        }
    if status["build"] != "ready":
        return {
            "kind": "build",
            "title": "Build runnable nodes",
            "detail": "Compile the project before starting Docker simulations.",
        }
    if not runs:
        return {
            "kind": "simulate",
            "title": "Run the first scenario",
            "detail": "Start Docker nodes and packet capture for a saved project scenario.",
        }
    return {
        "kind": "inspect",
        "title": "Inspect the latest run",
        "detail": "Review node lifecycle, capture evidence, and saved run artifacts.",
    }


def project_overview(project_id: str) -> Dict[str, Any]:
    workspace = project_service.project_workspace(project_id)
    manifest = workspace["manifest"]
    status = workspace["status"]
    runs = simulation_service.list_project_runs(project_id)
    return {
        "id": manifest["id"],
        "name": manifest.get("name", manifest["id"]),
        "source_example": manifest.get("source_example"),
        "status": status,
        "readiness": _readiness(status),
        "readiness_gates": _readiness_gates(status),
        "recommended_action": _recommended_action(status, runs),
        "network": manifest.get("network", {}),
        "nodes": _nodes(manifest),
        "interface_index": _interface_index(workspace["metadata"]),
        "documents": workspace["documents"],
        "scenario_count": len(manifest.get("scenarios", [])),
        "recent_runs": runs[:8],
    }


def authoring_workspace(project_id: str) -> Dict[str, Any]:
    workspace = project_service.project_workspace(project_id)
    validation = workspace["metadata"].get("validation", {})
    return {
        "project_id": project_id,
        "documents": workspace["documents"],
        "validation_status": validation.get(
            "status", workspace["status"]["validation"]
        ),
        "diagnostics": validation.get("diagnostics", []),
        "interface_index": _interface_index(workspace["metadata"]),
    }


def pipeline_overview(project_id: str) -> Dict[str, Any]:
    workspace = project_service.project_workspace(project_id)
    status = workspace["status"]
    metadata = workspace["metadata"]
    generated = metadata.get("generated", {})
    return {
        "project_id": project_id,
        "status": status,
        "stages": [
            {
                "id": "validation",
                "label": "Validate Franca",
                "status": status["validation"],
                "ready": status["validation"] == "valid",
                "detail": "Derive diagnostics and deployment index from editable source.",
            },
            {
                "id": "generation",
                "label": "Generate CommonAPI",
                "status": status["generation"],
                "ready": status["generation"] in {"ready", "transport-only"},
                "detail": "Generate transport output and project node templates.",
                "warnings": generated.get("warnings", []),
            },
            {
                "id": "build",
                "label": "Build nodes",
                "status": status["build"],
                "ready": status["build"] == "ready",
                "detail": "Compile or build the runnable project artifacts used by Docker.",
            },
        ],
    }


def _simulation_blockers(
    project_id: str, manifest: Dict[str, Any], status: Dict[str, str]
) -> List[Dict[str, str]]:
    blockers = []
    if status["validation"] != "valid":
        blockers.append(
            {
                "id": "validation",
                "message": "Validate the project before starting a run.",
            }
        )
    if status["build"] != "ready":
        blockers.append(
            {"id": "build", "message": "Build runnable nodes before starting a run."}
        )
    if not manifest.get("nodes"):
        blockers.append(
            {"id": "nodes", "message": "The project manifest has no runnable nodes."}
        )
    return blockers


def simulation_workspace(project_id: str) -> Dict[str, Any]:
    workspace = project_service.project_workspace(project_id)
    manifest = workspace["manifest"]
    return {
        "project_id": project_id,
        "scenarios": project_service.list_scenarios(project_id),
        "blockers": _simulation_blockers(project_id, manifest, workspace["status"]),
        "nodes": _nodes(manifest),
        "recent_runs": simulation_service.list_project_runs(project_id)[:12],
    }


def _scenario_result(run: Dict[str, Any]) -> Dict[str, Any]:
    failed = next(
        (
            event
            for event in reversed(run.get("events", []))
            if event.get("type") == "scenario.assertion"
            and event.get("status") == "failed"
        ),
        None,
    )
    limitations = []
    if "franca_driver_required" in run.get("scenario_capabilities", []):
        limitations.append(
            "Franca call and event assertions need a generated scenario driver."
        )
    if failed:
        return {
            "status": "failed",
            "detail": failed.get("detail", "Scenario assertion failed."),
            "limitations": limitations,
        }
    if limitations:
        return {
            "status": "limited",
            "detail": "Docker nodes and capture ran, but scenario assertion execution is incomplete.",
            "limitations": limitations,
        }
    return {
        "status": run.get("status", "unknown"),
        "detail": "Run events and capture evidence are available.",
        "limitations": [],
    }


def _node_lifecycle(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    latest: Dict[str, Dict[str, Any]] = {}
    for event in events:
        if event.get("type") == "node.status" and event.get("node_id"):
            latest[event["node_id"]] = {
                "node_id": event["node_id"],
                "status": event.get("status", "unknown"),
                "timestamp": event.get("timestamp"),
            }
    return list(latest.values())


def _evidence(run: Dict[str, Any]) -> Dict[str, Any]:
    captures = run.get("captures", [])
    capture_event = next(
        (
            event
            for event in reversed(run.get("events", []))
            if event.get("type") == "capture.status"
        ),
        {},
    )
    saved = bool(captures)
    observation = (
        "captured"
        if saved
        else (
            "unavailable" if capture_event.get("status") == "unavailable" else "unknown"
        )
    )
    return {
        "capture_status": capture_event.get("status", "ready" if saved else "unknown"),
        "capture_count": len(captures),
        "wireshark_url": run.get("capture", {}).get("wireshark_url"),
        "packet_snapshot_saved": saved,
        "someip_observation": observation,
        "service_discovery_observation": observation,
    }


def run_inspection(run_id: str) -> Dict[str, Any]:
    run = simulation_service.get_run(run_id)
    return {
        "run": run,
        "scenario_result": _scenario_result(run),
        "node_lifecycle": _node_lifecycle(run.get("events", [])),
        "evidence": _evidence(run),
        "timeline": run.get("events", []),
        "artifacts": simulation_service.run_artifacts(run_id),
    }
