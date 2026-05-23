import asyncio
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List

import yaml

from services import docker_manager, franca_service, project_service

RUNS_DIR = project_service.RUNS_DIR
_event_subscribers: Dict[str, list[asyncio.Queue]] = {}


def _run_dir(run_id: str) -> Path:
    path = (RUNS_DIR / run_id).resolve()
    if RUNS_DIR.resolve() not in path.parents:
        raise ValueError("Run path escapes run directory")
    return path


def _metadata_path(run_id: str) -> Path:
    return _run_dir(run_id) / "metadata.json"


def _read_metadata(run_id: str) -> Dict[str, Any]:
    path = _metadata_path(run_id)
    if not path.exists():
        raise FileNotFoundError(run_id)
    return json.loads(path.read_text())


def _write_metadata(run_id: str, data: Dict[str, Any]) -> None:
    path = _metadata_path(run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


async def emit(run_id: str, event: Dict[str, Any]) -> None:
    event.setdefault("run_id", run_id)
    event.setdefault("timestamp", project_service.utc_now())
    metadata = _read_metadata(run_id)
    metadata.setdefault("events", []).append(event)
    metadata["events"] = metadata["events"][-400:]
    _write_metadata(run_id, metadata)
    for queue in _event_subscribers.get(run_id, []):
        await queue.put(event)


def subscribe(run_id: str) -> asyncio.Queue:
    _read_metadata(run_id)
    queue: asyncio.Queue = asyncio.Queue()
    _event_subscribers.setdefault(run_id, []).append(queue)
    return queue


def unsubscribe(run_id: str, queue: asyncio.Queue) -> None:
    subscribers = _event_subscribers.get(run_id, [])
    if queue in subscribers:
        subscribers.remove(queue)


def _scenario(project_id: str, scenario_id: str) -> Dict[str, Any]:
    root = project_service._project_dir(project_id)
    manifest = project_service.load_manifest(project_id)
    for item in manifest.get("scenarios", []):
        if item.get("id") == scenario_id:
            with (root / item["file"]).open() as handle:
                data = yaml.safe_load(handle) or {}
            data.setdefault("id", scenario_id)
            return data
    raise FileNotFoundError(f"Scenario not found: {scenario_id}")


def _node_role(node: Dict[str, Any]) -> str:
    role = node.get("type", "client")
    return "service" if role == "service" else "client"


def render_vsomeip_configs(project_id: str, run_id: str) -> Dict[str, Path]:
    manifest = project_service.load_manifest(project_id)
    network = manifest.get("network", {})
    service_id, instance_id, reliable, unreliable = franca_service.deployment_values(
        project_id
    )
    services = [
        node for node in manifest.get("nodes", []) if _node_role(node) == "service"
    ]
    service_node = services[0] if services else None
    configs = {}
    for offset, node in enumerate(manifest.get("nodes", []), start=1):
        role = _node_role(node)
        config = {
            "unicast": node["id"],
            "logging": {
                "level": "info",
                "console": "true",
                "file": {"enable": "false"},
                "dlt": "false",
            },
            "applications": [
                {
                    "name": node.get("app_name", node["id"]),
                    "id": f"0x{0x1100 + offset:04x}",
                }
            ],
            "services": [
                {
                    "service": service_id,
                    "instance": instance_id,
                    "reliable": {
                        "port": str(reliable),
                        **(
                            {"enable-magic-cookies": False} if role == "service" else {}
                        ),
                    },
                    "unreliable": str(unreliable),
                }
            ],
            "routing": node.get("app_name", node["id"]),
            "service-discovery": {
                "enable": "true" if network.get("service_discovery", True) else "false",
                "multicast": network.get("multicast", "224.224.224.245"),
                "port": str(network.get("sd_port", 30490)),
                "protocol": "udp",
                "wait_route_netlink_notification": "false",
            },
        }
        if role != "service" and service_node:
            config["services"][0]["unicast"] = service_node["id"]
        path = _run_dir(run_id) / "configs" / f"{node['id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config, indent=2) + "\n")
        configs[node["id"]] = path
    return configs


def _compose(project_id: str, run_id: str) -> Dict[str, Any]:
    manifest = project_service.load_manifest(project_id)
    metadata = project_service.load_metadata(project_id)
    source_example = manifest.get("source_example")
    generated_nodes = metadata.get("generated_nodes", {})
    network_name = f"someip-run-{run_id[:8]}"
    services = {}
    service_ids = [
        node["id"]
        for node in manifest.get("nodes", [])
        if _node_role(node) == "service"
    ]
    for node in manifest.get("nodes", []):
        role = _node_role(node)
        if source_example:
            build = {
                "context": "../..",
                "dockerfile": "docker/Dockerfile.example",
                "args": {"EXAMPLE_NAME": source_example},
            }
            environment = {
                "EXAMPLE_NAME": source_example,
            }
        else:
            build = {
                "context": "../..",
                "dockerfile": "docker/Dockerfile.project",
                "args": {"PROJECT_ID": project_id},
            }
            environment = {
                "EXAMPLE_NAME": project_id,
                "SERVICE_BINARY": generated_nodes.get("service_binary", f"{project_id.replace('-', '_')}_service"),
                "CLIENT_BINARY": generated_nodes.get("client_binary", f"{project_id.replace('-', '_')}_client"),
            }
        service = {
            "build": build,
            "container_name": f"{run_id[:8]}-{node['id']}",
            "cap_add": ["NET_ADMIN"],
            "networks": [network_name],
            "volumes": [f"./configs/{node['id']}.json:/app/vsomeip.json:ro"],
            "environment": {
                "VSOMEIP_CONFIGURATION": "/app/vsomeip.json",
                "VSOMEIP_APPLICATION_NAME": node.get("app_name", node["id"]),
                "PROCESS_TYPE": role,
                **environment,
                **({"PROCESS_START_DELAY": "4"} if role == "client" else {}),
            },
        }
        if role == "client" and service_ids:
            service["depends_on"] = service_ids
        services[node["id"]] = service
    return {
        "name": f"someip-{run_id[:8]}",
        "services": services,
        "networks": {network_name: {"driver": "bridge"}},
    }


def _compose_path(run_id: str) -> Path:
    return _run_dir(run_id) / "compose.yaml"


def _scenario_capabilities(scenario: Dict[str, Any]) -> List[str]:
    capabilities = []
    for step in scenario.get("steps", []):
        if "call" in step or "subscribe" in step or "wait_for_event" in step:
            capabilities.append("franca_driver_required")
    return sorted(set(capabilities))


async def create_run(project_id: str, scenario_id: str) -> Dict[str, Any]:
    manifest = project_service.load_manifest(project_id)
    validation = project_service.load_metadata(project_id).get("validation", {})
    if validation.get("status") != "valid":
        raise ValueError("Validate the project before starting a run")
    if (
        not project_service.load_metadata(project_id).get("build", {}).get("status")
        == "ready"
    ):
        raise ValueError("Build the project before starting a run")
    if not manifest.get("nodes"):
        raise ValueError("Project has no runnable nodes")
    scenario = _scenario(project_id, scenario_id)
    run_id = str(uuid.uuid4())
    run_dir = _run_dir(run_id)
    for name in ("configs", "logs", "captures"):
        (run_dir / name).mkdir(parents=True, exist_ok=True)
    metadata = {
        "id": run_id,
        "project_id": project_id,
        "scenario_id": scenario_id,
        "scenario_name": scenario.get("name", scenario_id),
        "status": "rendered",
        "created_at": project_service.utc_now(),
        "events": [],
        "scenario_capabilities": _scenario_capabilities(scenario),
        "capture": {
            "wireshark_url": "https://localhost:3001/",
            "wireshark_root": "/captures",
            "display_filter": "someip || someipsd",
            "files": [],
        },
    }
    _write_metadata(run_id, metadata)
    render_vsomeip_configs(project_id, run_id)
    _compose_path(run_id).write_text(
        yaml.safe_dump(_compose(project_id, run_id), sort_keys=False)
    )
    await emit(
        run_id,
        {
            "type": "scenario.step",
            "status": "rendered",
            "detail": "Run configs rendered",
        },
    )
    asyncio.create_task(start_run(run_id))
    return _read_metadata(run_id)


async def start_run(run_id: str) -> None:
    metadata = _read_metadata(run_id)
    await _status(run_id, "starting")
    await docker_manager.start_wireshark()
    ok, output = await docker_manager.run_cmd(
        ["docker", "compose", "-f", str(_compose_path(run_id)), "up", "-d", "--build"]
    )
    (_run_dir(run_id) / "logs" / "compose.log").write_text(output)
    if not ok:
        await emit(
            run_id,
            {
                "type": "scenario.assertion",
                "status": "failed",
                "detail": "Docker compose failed",
            },
        )
        await _status(run_id, "failed")
        return
    await _status(run_id, "running")
    for node in project_service.load_manifest(metadata["project_id"]).get("nodes", []):
        await emit(
            run_id, {"type": "node.status", "node_id": node["id"], "status": "running"}
        )
    if "franca_driver_required" in metadata.get("scenario_capabilities", []):
        await emit(
            run_id,
            {
                "type": "scenario.step",
                "status": "waiting_for_driver",
                "detail": "Call/event steps need a generated Franca scenario driver; node orchestration and capture are active.",
            },
        )
    else:
        await emit(
            run_id,
            {
                "type": "scenario.step",
                "status": "active",
                "detail": "Scenario nodes started",
            },
        )
    asyncio.create_task(capture_snapshot(run_id))
    project_service.update_metadata(
        metadata["project_id"],
        last_run={
            "id": run_id,
            "status": "running",
            "started_at": project_service.utc_now(),
        },
    )


async def _status(run_id: str, status: str) -> None:
    metadata = _read_metadata(run_id)
    metadata["status"] = status
    metadata["updated_at"] = project_service.utc_now()
    _write_metadata(run_id, metadata)
    await emit(run_id, {"type": "run.status", "status": status})


def get_run(run_id: str) -> Dict[str, Any]:
    run = _read_metadata(run_id)
    run["containers"] = get_containers(run_id)
    run["captures"] = list_captures(run_id)
    return run


def _run_summary(metadata: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": metadata["id"],
        "project_id": metadata.get("project_id", "unknown"),
        "scenario_id": metadata.get("scenario_id", "unknown"),
        "scenario_name": metadata.get(
            "scenario_name", metadata.get("scenario_id", "unknown")
        ),
        "status": metadata.get("status", "unknown"),
        "created_at": metadata.get("created_at"),
        "updated_at": metadata.get("updated_at"),
        "capture": metadata.get("capture", {}),
        "captures": list_captures(metadata["id"]),
        "containers": (
            get_containers(metadata["id"])
            if metadata.get("status") in {"starting", "running"}
            else {}
        ),
    }


def list_runs(
    project_id: str | None = None, status: str | None = None, limit: int = 40
) -> List[Dict[str, Any]]:
    runs = []
    if not RUNS_DIR.exists():
        return runs
    for metadata_path in RUNS_DIR.glob("*/metadata.json"):
        try:
            metadata = json.loads(metadata_path.read_text())
        except (OSError, json.JSONDecodeError, KeyError):
            continue
        if project_id and metadata.get("project_id") != project_id:
            continue
        if status and metadata.get("status") != status:
            continue
        runs.append(_run_summary(metadata))
    runs.sort(
        key=lambda item: item.get("updated_at") or item.get("created_at") or "",
        reverse=True,
    )
    return runs[:limit]


def list_project_runs(project_id: str) -> List[Dict[str, Any]]:
    project_service.load_manifest(project_id)
    return list_runs(project_id=project_id)


async def stop_run(run_id: str) -> Dict[str, Any]:
    await docker_manager.run_cmd(
        ["docker", "compose", "-f", str(_compose_path(run_id)), "down"]
    )
    await _status(run_id, "stopped")
    metadata = _read_metadata(run_id)
    project_service.update_metadata(
        metadata["project_id"],
        last_run={
            "id": run_id,
            "status": "stopped",
            "stopped_at": project_service.utc_now(),
        },
    )
    return get_run(run_id)


async def capture_snapshot(run_id: str) -> None:
    await emit(
        run_id,
        {
            "type": "capture.status",
            "status": "capturing",
            "detail": "Collecting a run packet snapshot",
        },
    )
    target = _run_dir(run_id) / "captures" / f"{run_id[:8]}.pcapng"
    remote = f"/tmp/{run_id[:8]}.pcapng"
    ok, output = await docker_manager.run_cmd(
        [
            "docker",
            "exec",
            "dc-wireshark",
            "dumpcap",
            "-i",
            "any",
            "-a",
            "duration:8",
            "-f",
            "udp port 30490 or tcp port 30500 or udp port 30501",
            "-w",
            remote,
        ]
    )
    if ok:
        copied, copy_output = await docker_manager.run_cmd(
            ["docker", "cp", f"dc-wireshark:{remote}", str(target)]
        )
        ok = copied
        output += copy_output
    if ok and target.exists():
        await emit(
            run_id, {"type": "capture.status", "status": "ready", "detail": target.name}
        )
        await emit(
            run_id,
            {
                "type": "packet.summary",
                "status": "saved",
                "detail": f"{target.stat().st_size} byte pcapng snapshot",
            },
        )
        metadata = _read_metadata(run_id)
        metadata["capture"]["files"] = list_captures(run_id)
        _write_metadata(run_id, metadata)
    else:
        (_run_dir(run_id) / "logs" / "capture.log").write_text(output)
        await emit(
            run_id,
            {
                "type": "capture.status",
                "status": "unavailable",
                "detail": "Wireshark dumpcap snapshot failed",
            },
        )


def get_containers(run_id: str) -> Dict[str, Dict[str, str]]:
    import subprocess

    result = subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            str(_compose_path(run_id)),
            "ps",
            "--all",
            "--format",
            "json",
        ],
        cwd=str(project_service.WORKSPACE),
        text=True,
        capture_output=True,
        timeout=10,
    )
    containers = {}
    for line in result.stdout.splitlines():
        try:
            info = json.loads(line)
        except json.JSONDecodeError:
            continue
        containers[info.get("Service", info.get("Name", "unknown"))] = {
            "name": info.get("Name", "unknown"),
            "status": info.get("State", "unknown"),
        }
    return containers


def list_captures(run_id: str) -> List[Dict[str, Any]]:
    captures = []
    for path in sorted((_run_dir(run_id) / "captures").glob("*.pcap*")):
        captures.append(
            {
                "name": path.name,
                "bytes": path.stat().st_size,
                "wireshark_path": f"/captures/{run_id}/captures/{path.name}",
            }
        )
    return captures


def capture_path(run_id: str, capture_name: str) -> Path:
    capture_dir = (_run_dir(run_id) / "captures").resolve()
    path = (capture_dir / capture_name).resolve()
    if (
        capture_dir not in path.parents
        or not path.exists()
        or not path.is_file()
        or not path.name.endswith((".pcap", ".pcapng"))
    ):
        raise FileNotFoundError(capture_name)
    return path


def _artifact_entry(run_dir: Path, path: Path) -> Dict[str, Any]:
    return {"name": path.relative_to(run_dir).as_posix(), "bytes": path.stat().st_size}


def run_artifacts(run_id: str) -> Dict[str, Any]:
    run_dir = _run_dir(run_id)
    metadata = _read_metadata(run_id)
    files = []
    for pattern in ("compose.yaml", "configs/*.json", "logs/*.log"):
        for path in sorted(run_dir.glob(pattern)):
            if path.is_file():
                files.append(_artifact_entry(run_dir, path))

    def read_log(name: str) -> str:
        path = run_dir / "logs" / name
        return path.read_text(errors="replace") if path.exists() else ""

    return {
        "run_id": run_id,
        "files": files,
        "capture": metadata.get("capture", {}),
        "compose_log": read_log("compose.log"),
        "capture_log": read_log("capture.log"),
        "captures": list_captures(run_id),
    }
