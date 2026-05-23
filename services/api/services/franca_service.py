import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from services import project_service

WORKSPACE = Path(__file__).resolve().parent.parent.parent.parent
GENERATOR_DIR = WORKSPACE / "tools" / "generators"
CORE_GEN = GENERATOR_DIR / "commonapi-core-generator-linux-x86_64"
SOMEIP_GEN = GENERATOR_DIR / "commonapi-someip-generator-linux-x86_64"

PACKAGE_RE = re.compile(r"^\s*package\s+([\w.]+)", re.MULTILINE)
INTERFACE_RE = re.compile(r"^\s*interface\s+(\w+)", re.MULTILINE)
BLOCK_RE = re.compile(
    r"^\s*(method|event|broadcast|struct|enumeration)\s+(\w+)", re.MULTILINE
)
ID_RE = re.compile(
    r"^\s*(serviceId|instanceId|methodId|eventId|eventGroupId|unreliable)\s+([^\s]+)",
    re.MULTILINE,
)
PORT_RE = re.compile(r"^\s*port\s+([^\s]+)", re.MULTILINE)
SOMEIP_ID_RE = re.compile(
    r"^\s*(SomeIpServiceID|SomeIpInstanceID|SomeIpMethodID|SomeIpEventID)\s*=\s*([^\s}]+)",
    re.MULTILINE,
)
SOMEIP_GROUP_RE = re.compile(
    r"^\s*SomeIpEventGroups\s*=\s*\{\s*([^\s},]+)", re.MULTILINE
)


def _diag(severity: str, file: str, message: str) -> Dict[str, str]:
    return {"severity": severity, "file": file, "message": message}


def _index_document(document: Dict[str, str]) -> Dict[str, Any]:
    text = document["content"]
    blocks: Dict[str, List[str]] = {
        "methods": [],
        "events": [],
        "structs": [],
        "enums": [],
    }
    names = {
        "method": "methods",
        "event": "events",
        "broadcast": "events",
        "struct": "structs",
        "enumeration": "enums",
    }
    for kind, name in BLOCK_RE.findall(text):
        blocks[names[kind]].append(name)
    package = PACKAGE_RE.search(text)
    interface = INTERFACE_RE.search(text)
    return {
        "document": document["id"],
        "package": package.group(1) if package else None,
        "name": interface.group(1) if interface else None,
        **blocks,
    }


def _deployment(document: Dict[str, str]) -> Dict[str, Any]:
    ids: Dict[str, List[str]] = {}
    for key, value in ID_RE.findall(document["content"]):
        ids.setdefault(key, []).append(value)
    someip_names = {
        "SomeIpServiceID": "serviceId",
        "SomeIpInstanceID": "instanceId",
        "SomeIpMethodID": "methodId",
        "SomeIpEventID": "eventId",
    }
    for key, value in SOMEIP_ID_RE.findall(document["content"]):
        ids.setdefault(someip_names[key], []).append(_id_literal(value))
    for value in SOMEIP_GROUP_RE.findall(document["content"]):
        ids.setdefault("eventGroupId", []).append(_id_literal(value))
    ports = PORT_RE.findall(document["content"])
    return {"document": document["id"], "ids": ids, "reliable_ports": ports}


def _id_literal(value: str) -> str:
    if value.lower().startswith("0x"):
        return value
    try:
        return f"0x{int(value, 10):04x}"
    except ValueError:
        return value


def interface_index(project_id: str) -> Dict[str, Any]:
    documents = project_service.list_documents(project_id)
    interfaces = [_index_document(doc) for doc in documents if doc["kind"] == "fidl"]
    deployments = [_deployment(doc) for doc in documents if doc["kind"] == "fdepl"]
    return {"interfaces": interfaces, "deployments": deployments}


def _basic_diagnostics(project_id: str, index: Dict[str, Any]) -> List[Dict[str, str]]:
    diagnostics = []
    for interface in index["interfaces"]:
        if not interface["package"]:
            diagnostics.append(
                _diag(
                    "error", interface["document"], "Missing Franca package declaration"
                )
            )
        if not interface["name"]:
            diagnostics.append(
                _diag("error", interface["document"], "Missing interface declaration")
            )
    if not index["interfaces"]:
        diagnostics.append(
            _diag("error", "project.yaml", "Project has no .fidl document")
        )
    if not index["deployments"]:
        diagnostics.append(
            _diag("error", "project.yaml", "Project has no .fdepl document")
        )
    manifest = project_service.load_manifest(project_id)
    app_names = [
        node.get("app_name")
        for node in manifest.get("nodes", [])
        if node.get("app_name")
    ]
    if len(app_names) != len(set(app_names)):
        diagnostics.append(
            _diag("error", "project.yaml", "Node app_name values must be unique")
        )
    seen_ids: Dict[Tuple[str, str], str] = {}
    for deployment in index["deployments"]:
        ids = deployment["ids"]
        for kind in ("serviceId", "instanceId", "methodId", "eventId"):
            for value in ids.get(kind, []):
                key = (kind, value.lower())
                if key in seen_ids:
                    diagnostics.append(
                        _diag(
                            "error",
                            deployment["document"],
                            f"Duplicate {kind} {value} also appears in {seen_ids[key]}",
                        )
                    )
                seen_ids[key] = deployment["document"]
        ports = deployment.get("reliable_ports", []) + ids.get("unreliable", [])
        if len([port for port in ports if ports.count(port) > 1]) > 1:
            diagnostics.append(
                _diag(
                    "error",
                    deployment["document"],
                    "Reliable and unreliable ports must not collide",
                )
            )
    return diagnostics


def _generator_health() -> List[Dict[str, str]]:
    diagnostics = []
    if not CORE_GEN.exists():
        diagnostics.append(
            _diag("warning", "toolchain", f"Core generator missing at {CORE_GEN.name}")
        )
    if not SOMEIP_GEN.exists():
        diagnostics.append(
            _diag(
                "error", "toolchain", f"SOME/IP generator missing at {SOMEIP_GEN.name}"
            )
        )
    return diagnostics


async def validate_project(project_id: str) -> Dict[str, Any]:
    index = interface_index(project_id)
    diagnostics = _basic_diagnostics(project_id, index) + _generator_health()
    valid = not any(item["severity"] == "error" for item in diagnostics)
    generated = project_service._project_dir(project_id) / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    (generated / "interface-index.json").write_text(json.dumps(index, indent=2) + "\n")
    project_service.update_metadata(
        project_id,
        validation={
            "status": "valid" if valid else "failed",
            "diagnostics": diagnostics,
            "validated_at": project_service.utc_now(),
        },
        interface_index="generated/interface-index.json",
    )
    return {"valid": valid, "diagnostics": diagnostics, "interface_index": index}


def deployment_values(project_id: str) -> Tuple[str, str, str, str]:
    deployment = interface_index(project_id)["deployments"]
    ids = deployment[0]["ids"] if deployment else {}
    service = ids.get("serviceId", ["0x1001"])[0]
    instance = ids.get("instanceId", ["0x0001"])[0]
    unreliable = ids.get("unreliable", ["30501"])[0]
    reliable_ports = deployment[0].get("reliable_ports", []) if deployment else []
    reliable = reliable_ports[0] if reliable_ports else "30500"
    return service, instance, reliable, unreliable
