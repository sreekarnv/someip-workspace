import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml

from services import example_catalog

WORKSPACE = Path(__file__).resolve().parent.parent.parent.parent
PROJECTS_DIR = WORKSPACE / "projects"
RUNS_DIR = WORKSPACE / "runs"
BUILD_PROJECTS_DIR = WORKSPACE / "build" / "projects"
ALLOWED_DOC_SUFFIXES = {".fidl", ".fdepl", ".yaml", ".yml", ".cpp", ".hpp", ".h"}
PROJECT_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,62}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _project_dir(project_id: str) -> Path:
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError("Project IDs must be lowercase letters, digits, and hyphens")
    path = (PROJECTS_DIR / project_id).resolve()
    if PROJECTS_DIR.resolve() not in path.parents:
        raise ValueError("Project path escapes projects directory")
    return path


def _manifest_path(project_id: str) -> Path:
    return _project_dir(project_id) / "project.yaml"


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open() as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a YAML mapping")
    return data


def load_manifest(project_id: str) -> Dict[str, Any]:
    path = _manifest_path(project_id)
    if not path.exists():
        raise FileNotFoundError(f"Project not found: {project_id}")
    manifest = _load_yaml(path)
    if manifest.get("id") != project_id:
        raise ValueError("Manifest id does not match its directory")
    return manifest


def save_manifest(project_id: str, manifest: Dict[str, Any]) -> None:
    path = _manifest_path(project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        yaml.safe_dump(manifest, handle, sort_keys=False)


def _metadata_path(project_id: str) -> Path:
    return _project_dir(project_id) / "generated" / "metadata.json"


def load_metadata(project_id: str) -> Dict[str, Any]:
    path = _metadata_path(project_id)
    if not path.exists():
        return {}
    with path.open() as handle:
        return json.load(handle)


def update_metadata(project_id: str, **updates: Any) -> Dict[str, Any]:
    metadata = load_metadata(project_id)
    metadata.update(updates)
    metadata["updated_at"] = utc_now()
    path = _metadata_path(project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        json.dump(metadata, handle, indent=2)
        handle.write("\n")
    return metadata


def _document_paths(
    project_id: str, manifest: Dict[str, Any] | None = None
) -> List[Path]:
    root = _project_dir(project_id)
    manifest = manifest or load_manifest(project_id)
    configured = list(manifest.get("franca", {}).get("fidl", []))
    configured += list(manifest.get("franca", {}).get("deployment", []))
    configured += [
        item.get("file") for item in manifest.get("scenarios", []) if item.get("file")
    ]
    paths = []
    for relative in configured:
        path = (root / relative).resolve()
        if root.resolve() in path.parents and path.exists():
            paths.append(path)
    return paths


def _document_id(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def get_document_path(project_id: str, document_id: str) -> Path:
    root = _project_dir(project_id).resolve()
    path = (root / document_id).resolve()
    if root not in path.parents or path.suffix not in ALLOWED_DOC_SUFFIXES:
        raise ValueError("Document must stay in the project and use an editable suffix")
    return path


def list_documents(project_id: str) -> List[Dict[str, Any]]:
    root = _project_dir(project_id)
    return [
        {
            "id": _document_id(root, path),
            "name": path.name,
            "kind": path.suffix.lstrip("."),
            "content": path.read_text(),
        }
        for path in _document_paths(project_id)
    ]


def document_refs(project_id: str) -> List[Dict[str, Any]]:
    root = _project_dir(project_id)
    return [
        {
            "id": _document_id(root, path),
            "name": path.name,
            "kind": path.suffix.lstrip("."),
        }
        for path in _document_paths(project_id)
    ]


def read_document(project_id: str, document_id: str) -> Dict[str, Any]:
    root = _project_dir(project_id)
    path = get_document_path(project_id, document_id)
    if not path.exists() or path not in _document_paths(project_id):
        raise FileNotFoundError(f"Document not found: {document_id}")
    return {
        "id": _document_id(root, path),
        "name": path.name,
        "kind": path.suffix.lstrip("."),
        "content": path.read_text(),
    }


def write_document(project_id: str, document_id: str, content: str) -> Dict[str, Any]:
    path = get_document_path(project_id, document_id)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {document_id}")
    path.write_text(content)
    update_metadata(
        project_id, validation={"status": "stale"}, generated={"status": "stale"}
    )
    return {"id": document_id, "name": path.name, "bytes": len(content.encode())}


def _status(project_id: str) -> Dict[str, Any]:
    metadata = load_metadata(project_id)
    return {
        "validation": metadata.get("validation", {}).get("status", "unknown"),
        "generation": metadata.get("generated", {}).get("status", "unknown"),
        "build": metadata.get("build", {}).get("status", "unknown"),
        "last_run": metadata.get("last_run", {}).get("status", "none"),
    }


def _metadata_with_interface_index(project_id: str) -> Dict[str, Any]:
    metadata = load_metadata(project_id)
    index_path = _project_dir(project_id) / "generated" / "interface-index.json"
    if index_path.exists():
        metadata["interface_index_data"] = json.loads(index_path.read_text())
    return metadata


def project_detail(project_id: str) -> Dict[str, Any]:
    return {
        "manifest": load_manifest(project_id),
        "metadata": _metadata_with_interface_index(project_id),
        "documents": list_documents(project_id),
        "status": _status(project_id),
    }


def project_workspace(project_id: str) -> Dict[str, Any]:
    return {
        "manifest": load_manifest(project_id),
        "metadata": _metadata_with_interface_index(project_id),
        "documents": document_refs(project_id),
        "status": _status(project_id),
    }


def list_projects() -> List[Dict[str, Any]]:
    if not PROJECTS_DIR.exists():
        return []
    projects = []
    for child in sorted(PROJECTS_DIR.iterdir()):
        if not child.is_dir() or not (child / "project.yaml").exists():
            continue
        try:
            manifest = load_manifest(child.name)
        except (ValueError, yaml.YAMLError):
            continue
        projects.append(
            {
                "id": manifest["id"],
                "name": manifest.get("name", manifest["id"]),
                "document_count": len(_document_paths(child.name, manifest)),
                "node_count": len(manifest.get("nodes", [])),
                "scenario_count": len(manifest.get("scenarios", [])),
                "latest_status": _status(child.name),
            }
        )
    return projects


def _franca_files_from_example(
    source_example: str, project_root: Path
) -> Dict[str, List[str]]:
    canonical = WORKSPACE / "projects" / common_project_id(source_example) / "franca"
    source = (
        canonical
        if canonical.exists()
        else WORKSPACE / "examples" / source_example / "fidl"
    )
    if not source.exists():
        raise FileNotFoundError(f"Example Franca directory not found: {source_example}")
    franca = project_root / "franca"
    franca.mkdir(parents=True, exist_ok=True)
    copied = {"fidl": [], "deployment": []}
    for item in sorted(source.iterdir()):
        if item.suffix in {".fidl", ".fdepl"}:
            target = franca / item.name
            shutil.copyfile(item, target)
            copied["fidl" if item.suffix == ".fidl" else "deployment"].append(
                target.relative_to(project_root).as_posix()
            )
    return copied


def _franca_files_from_preset(
    preset: Dict[str, Any], project_root: Path
) -> Dict[str, List[str]]:
    franca_source = preset.get("franca") or {}
    franca = project_root / "franca"
    franca.mkdir(parents=True, exist_ok=True)
    written = {"fidl": [], "deployment": []}
    for key, suffix in (("fidl", ".fidl"), ("deployment", ".fdepl")):
        document = franca_source.get(key)
        if not document:
            continue
        target = franca / document.get("name", f"{preset['id']}{suffix}")
        target.write_text(document.get("content", ""))
        written[key].append(target.relative_to(project_root).as_posix())
    if not written["fidl"] or not written["deployment"]:
        raise ValueError(f"Preset {preset['id']} does not define FIDL and FDEPL source")
    return written


def common_project_id(name: str) -> str:
    return example_catalog.common_project_id(name)


def create_project(
    project_id: str,
    name: str,
    source_example: str | None = None,
    preset_id: str | None = None,
) -> Dict[str, Any]:
    preset = (
        example_catalog.by_id(preset_id)
        if preset_id
        else example_catalog.by_source_example(source_example)
    )
    if preset is None:
        requested = preset_id or source_example
        raise FileNotFoundError(f"Unknown project preset: {requested}")

    resolved_source_example = source_example or preset.get("source_example")
    root = _project_dir(project_id)
    if root.exists():
        raise FileExistsError(f"Project already exists: {project_id}")
    for directory in ("franca", "nodes", "scenarios", "generated"):
        (root / directory).mkdir(parents=True, exist_ok=True)

    if preset.get("franca"):
        franca = _franca_files_from_preset(preset, root)
    elif resolved_source_example:
        franca = _franca_files_from_example(resolved_source_example, root)
    else:
        franca = _starter_franca(root)

    if preset.get("interface") and preset.get("nodes"):
        scenarios = _scenario_from_preset(root, preset)
        nodes = [
            {
                "id": node["id"],
                "type": node.get("type", "client"),
                "interface": preset["interface"],
                "app_name": node.get("app_name", node["id"]),
            }
            for node in preset.get("nodes", [])
        ]
    else:
        scenarios = _starter_scenario(root)
        nodes = [
            {
                "id": f"{project_id}-service",
                "type": "service",
                "interface": "v1.simulation.Sample",
                "app_name": f"{project_id}-service",
            },
            {
                "id": f"{project_id}-client",
                "type": "client",
                "interface": "v1.simulation.Sample",
                "app_name": f"{project_id}-client",
            },
        ]

    manifest = {
        "id": project_id,
        "name": name,
        "source_example": resolved_source_example,
        "franca": franca,
        "nodes": nodes,
        "network": {
            "service_discovery": True,
            "multicast": "224.224.224.245",
            "sd_port": 30490,
        },
        "scenarios": scenarios,
    }
    save_manifest(project_id, manifest)
    update_metadata(project_id, created_at=utc_now(), validation={"status": "unknown"})
    return project_detail(project_id)


def import_project(source_path: str) -> Dict[str, Any]:
    source = Path(source_path).expanduser().resolve()
    if not source.is_dir() or not (source / "project.yaml").exists():
        raise FileNotFoundError(
            "Import source must be a project directory containing project.yaml"
        )
    manifest = _load_yaml(source / "project.yaml")
    project_id = manifest.get("id", "")
    destination = _project_dir(project_id)
    if destination.exists():
        raise FileExistsError(f"Project already exists: {project_id}")
    shutil.copytree(source, destination)
    update_metadata(
        project_id,
        imported_at=utc_now(),
        validation={"status": "stale"},
        generated={"status": "stale"},
    )
    return project_detail(project_id)


def _starter_franca(root: Path) -> Dict[str, List[str]]:
    fidl = root / "franca" / "Sample.fidl"
    fdepl = root / "franca" / "Sample.fdepl"
    fidl.write_text(
        "package v1.simulation\n\n"
        "interface Sample {\n"
        "    version { major 1 minor 0 }\n\n"
        "    method ping {\n"
        "        in { String message }\n"
        "        out { String response }\n"
        "    }\n"
        "}\n"
    )
    fdepl.write_text(
        'import "platform:/plugin/org.genivi.commonapi.someip/deployment/CommonAPI-SOMEIP_deployment_spec.fdepl"\n'
        'import "Sample.fidl"\n\n'
        "define org.genivi.commonapi.someip.deployment for interface v1.simulation.Sample {\n"
        "    SomeIpServiceID = 4609\n"
        "    method ping { SomeIpMethodID = 256 }\n"
        "}\n\n"
        "define org.genivi.commonapi.someip.deployment for provider as SampleService {\n"
        "    instance v1.simulation.Sample {\n"
        '        InstanceId = "v1.simulation.Sample"\n'
        "        SomeIpInstanceID = 1\n"
        "    }\n"
        "}\n"
    )
    return {"fidl": ["franca/Sample.fidl"], "deployment": ["franca/Sample.fdepl"]}


def _starter_scenario(root: Path) -> List[Dict[str, str]]:
    scenario = root / "scenarios" / "smoke.yaml"
    scenario.write_text(
        "id: smoke\n"
        "name: Smoke Start\n"
        "steps:\n"
        "  - start: service\n"
        "  - wait_for:\n"
        "      service: v1.simulation.Sample\n"
        "      timeout_ms: 5000\n"
        "  - start: client\n"
    )
    return [{"id": "smoke", "file": "scenarios/smoke.yaml"}]



def _scenario_from_preset(root: Path, preset: Dict[str, Any]) -> List[Dict[str, str]]:
    scenario = preset.get("scenario") or {}
    scenario_id = scenario.get("id", "smoke")
    relative_file = scenario.get("file", f"scenarios/{scenario_id}.yaml")
    target = root / relative_file
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(scenario.get("content", "id: smoke\nname: Smoke\nsteps: []\n"))
    return [{"id": scenario_id, "file": relative_file}]


def list_scenarios(project_id: str) -> List[Dict[str, Any]]:
    root = _project_dir(project_id)
    scenarios = []
    for item in load_manifest(project_id).get("scenarios", []):
        path = (root / item["file"]).resolve()
        if root.resolve() not in path.parents or not path.exists():
            continue
        scenario = _load_yaml(path)
        scenarios.append(
            {
                "id": item["id"],
                "name": scenario.get("name", item["id"]),
                "file": item["file"],
                "steps": scenario.get("steps", []),
            }
        )
    return scenarios
