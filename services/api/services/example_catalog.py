from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


EXAMPLE_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "starter",
        "name": "Starter",
        "description": "Generic authoring project for a minimal Franca ping service.",
        "category": "authoring",
        "runnable": False,
        "source_example": None,
        "default_project_id": "sample-lab",
        "default_name": "Sample Lab",
    },
    {
        "id": "door-control",
        "name": "Door Control",
        "description": "Sample-backed door lock and status SOME/IP service.",
        "category": "vehicle-body",
        "runnable": True,
        "source_example": "DoorControl",
        "default_project_id": "door-control",
        "default_name": "Door Control",
        "interface": "v1.vehicle.doors.DoorControl",
        "nodes": [
            {"id": "door-service", "type": "service", "app_name": "door-control-service"},
            {"id": "door-client", "type": "client", "app_name": "door-control-client"},
        ],
        "scenario": {
            "id": "basic-lock-flow",
            "name": "Basic Lock Flow",
            "file": "scenarios/basic-lock-flow.yaml",
            "content": """id: basic-lock-flow
name: Basic Lock Flow
steps:
  - start: door-service
  - wait_for:
      service: v1.vehicle.doors.DoorControl
      timeout_ms: 5000
  - start: door-client
  - call:
      node: door-client
      method: unlockDoor
      args:
        door: FRONT_LEFT
  - assert:
      response:
        success: true
  - capture_mark:
      label: unlock-complete
""",
        },
    },
    {
        "id": "climate-control",
        "name": "Climate Control",
        "description": "Franca/deployment authoring sample for HVAC temperature, fan level, status, and SOME/IP event IDs.",
        "category": "vehicle-body",
        "runnable": False,
        "source_example": None,
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
    return [dict(item) for item in EXAMPLE_CATALOG]


def public_presets() -> List[Dict[str, Any]]:
    return [
        {
            "id": item["id"],
            "name": item["name"],
            "description": item.get("description"),
            "category": item.get("category", "sample"),
            "runnable": bool(item.get("runnable")),
            "source_example": item.get("source_example"),
            "default_project_id": item.get("default_project_id"),
            "default_name": item.get("default_name"),
        }
        for item in EXAMPLE_CATALOG
    ]


def by_id(preset_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if preset_id is None:
        return next(item for item in EXAMPLE_CATALOG if item["id"] == "starter")
    for item in EXAMPLE_CATALOG:
        if item["id"] == preset_id:
            return item
    return None


def by_source_example(source_example: Optional[str]) -> Optional[Dict[str, Any]]:
    if source_example is None:
        return by_id("starter")
    for item in EXAMPLE_CATALOG:
        if item.get("source_example") == source_example:
            return item
    return None


def common_project_id(name: str) -> str:
    value = re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()
    value = re.sub(r"[^a-z0-9-]+", "-", value).strip("-")
    return value
