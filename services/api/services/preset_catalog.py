from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


PRESET_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "starter",
        "name": "Starter",
        "description": "Generic project for a minimal Franca ping service and generated SOME/IP transport nodes.",
        "category": "authoring",
        "runnable": True,
        "runtime_kind": "generated-vsomeip",
        "default_project_id": "sample-lab",
        "default_name": "Sample Lab",
    },
    {
        "id": "door-control",
        "name": "Door Control",
        "description": "Door lock and status SOME/IP project generated from canonical project source.",
        "category": "vehicle-body",
        "runnable": True,
        "runtime_kind": "generated-vsomeip",
        "default_project_id": "door-control",
        "default_name": "Door Control",
        "source_project": "door-control",
        "interface": "v1.vehicle.doors.DoorControl",
        "nodes": [
            {"id": "door-service", "type": "service", "app_name": "door-control-service"},
            {"id": "door-client", "type": "client", "app_name": "door-control-client"},
        ],
        "scenario": {
            "id": "basic-lock-flow",
            "name": "Basic Lock Flow",
            "file": "scenarios/basic-lock-flow.yaml",
            "source_file": "scenarios/basic-lock-flow.yaml",
        },
    },
    {
        "id": "climate-control",
        "name": "Climate Control",
        "description": "HVAC temperature, fan level, status, and SOME/IP event ID project generated from Franca source.",
        "category": "vehicle-body",
        "runnable": True,
        "runtime_kind": "generated-vsomeip",
        "default_project_id": "climate-control",
        "default_name": "Climate Control",
        "franca": {
            "fidl": {
                "name": "ClimateControl.fidl",
                "content": 'package v1.vehicle.climate\n\ninterface ClimateControl {\n\n    version { major 1 minor 0 }\n\n    struct ClimateStatus {\n        Int16 targetTemperatureC\n        UInt8 fanLevel\n        Boolean airConditioning\n    }\n\n    method setTargetTemperature {\n        in { Int16 targetTemperatureC }\n        out { Boolean accepted }\n    }\n\n    method setFanLevel {\n        in { UInt8 level }\n        out { Boolean accepted }\n    }\n\n    method getClimateStatus {\n        out { ClimateStatus status }\n    }\n\n    broadcast onClimateStatusChanged {\n        out { ClimateStatus status }\n    }\n}\n',
            },
            "deployment": {
                "name": "ClimateControl.fdepl",
                "content": 'import "platform:/plugin/org.genivi.commonapi.someip/deployment/CommonAPI-SOMEIP_deployment_spec.fdepl"\nimport "ClimateControl.fidl"\n\ndefine org.genivi.commonapi.someip.deployment for interface v1.vehicle.climate.ClimateControl {\n    SomeIpServiceID = 4353\n\n    method setTargetTemperature {\n        SomeIpMethodID = 256\n    }\n\n    method setFanLevel {\n        SomeIpMethodID = 257\n    }\n\n    method getClimateStatus {\n        SomeIpMethodID = 258\n    }\n\n    broadcast onClimateStatusChanged {\n        SomeIpEventID = 32769\n        SomeIpEventGroups = { 1 }\n    }\n}\n\ndefine org.genivi.commonapi.someip.deployment for provider as ClimateControlService {\n    instance v1.vehicle.climate.ClimateControl {\n        InstanceId = "vehicle.climate.ClimateControl"\n        SomeIpInstanceID = 1\n    }\n}\n',
            },
        },
        "interface": "v1.vehicle.climate.ClimateControl",
        "nodes": [
            {"id": "climate-service", "type": "service", "app_name": "climate-control-service"},
            {"id": "climate-client", "type": "client", "app_name": "climate-control-client"},
        ],
        "scenario": {
            "id": "comfort-flow",
            "name": "Comfort Flow",
            "file": "scenarios/comfort-flow.yaml",
            "content": """id: comfort-flow
name: Comfort Flow
steps:
  - start: climate-service
  - wait_for:
      service: v1.vehicle.climate.ClimateControl
      timeout_ms: 5000
  - start: climate-client
  - call:
      node: climate-client
      method: setTargetTemperature
      args:
        targetTemperatureC: 21
  - call:
      node: climate-client
      method: setFanLevel
      args:
        level: 3
  - capture_mark:
      label: climate-comfort-ready
""",
        },
    },
]


def all_presets() -> List[Dict[str, Any]]:
    return [dict(item) for item in PRESET_CATALOG]


def public_presets() -> List[Dict[str, Any]]:
    return [
        {
            "id": item["id"],
            "name": item["name"],
            "description": item.get("description"),
            "category": item.get("category", "sample"),
            "runnable": bool(item.get("runnable")),
            "runtime_kind": item.get("runtime_kind", "generated-vsomeip"),
            "default_project_id": item.get("default_project_id"),
            "default_name": item.get("default_name"),
        }
        for item in PRESET_CATALOG
    ]


def by_id(preset_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if preset_id is None:
        return next(item for item in PRESET_CATALOG if item["id"] == "starter")
    for item in PRESET_CATALOG:
        if item["id"] == preset_id:
            return item
    return None


def common_project_id(name: str) -> str:
    value = re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()
    value = re.sub(r"[^a-z0-9-]+", "-", value).strip("-")
    return value
