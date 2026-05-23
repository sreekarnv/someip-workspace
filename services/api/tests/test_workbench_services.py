import json
import tempfile
import unittest
from pathlib import Path

from main import app
from services import (
    franca_service,
    project_service,
    simulation_service,
    workflow_service,
)


class WorkbenchServiceTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.original_projects = project_service.PROJECTS_DIR
        self.original_runs = project_service.RUNS_DIR
        self.original_sim_runs = simulation_service.RUNS_DIR
        project_service.PROJECTS_DIR = root / "projects"
        project_service.RUNS_DIR = root / "runs"
        simulation_service.RUNS_DIR = root / "runs"

    def tearDown(self):
        project_service.PROJECTS_DIR = self.original_projects
        project_service.RUNS_DIR = self.original_runs
        simulation_service.RUNS_DIR = self.original_sim_runs
        self.tempdir.cleanup()

    def test_new_project_has_editable_source_and_scenario(self):
        detail = project_service.create_project("sample-lab", "Sample Lab")

        self.assertEqual(detail["manifest"]["id"], "sample-lab")
        self.assertEqual(len(detail["manifest"]["nodes"]), 2)
        self.assertEqual(
            [document["id"] for document in detail["documents"]],
            ["franca/Sample.fidl", "franca/Sample.fdepl", "scenarios/smoke.yaml"],
        )


    def test_project_collection_lists_source_only_climate_preset(self):
        collection = workflow_service.project_collection()
        presets = {preset["id"]: preset for preset in collection["presets"]}

        self.assertEqual(
            sorted(presets), ["climate-control", "door-control", "starter"]
        )
        self.assertFalse(presets["climate-control"]["runnable"])
        self.assertIsNone(presets["climate-control"]["source_example"])

    def test_climate_control_preset_seeds_manifest_documents_and_scenario(self):
        detail = project_service.create_project(
            "climate-lab", "Climate Lab", preset_id="climate-control"
        )
        manifest = detail["manifest"]

        self.assertIsNone(manifest["source_example"])
        self.assertEqual(
            manifest["franca"],
            {
                "fidl": ["franca/ClimateControl.fidl"],
                "deployment": ["franca/ClimateControl.fdepl"],
            },
        )
        self.assertEqual(
            [node["id"] for node in manifest["nodes"]],
            ["climate-service", "climate-client"],
        )
        self.assertEqual(
            [node["app_name"] for node in manifest["nodes"]],
            ["climate-control-service", "climate-control-client"],
        )
        self.assertEqual(
            manifest["nodes"][0]["interface"],
            "v1.vehicle.climate.ClimateControl",
        )
        self.assertEqual(
            manifest["scenarios"],
            [{"id": "comfort-flow", "file": "scenarios/comfort-flow.yaml"}],
        )
        scenario = project_service.read_document(
            "climate-lab", "scenarios/comfort-flow.yaml"
        )
        self.assertIn("setTargetTemperature", scenario["content"])

    def test_interface_index_reports_franca_and_deployment(self):
        project_service.create_project("sample-lab", "Sample Lab")

        index = franca_service.interface_index("sample-lab")

        self.assertEqual(index["interfaces"][0]["name"], "Sample")
        self.assertEqual(index["interfaces"][0]["methods"], ["ping"])
        self.assertEqual(index["deployments"][0]["ids"]["serviceId"], ["0x1201"])

    def test_workspace_lists_document_refs_and_reads_one_document(self):
        project_service.create_project("sample-lab", "Sample Lab")

        workspace = project_service.project_workspace("sample-lab")
        document = project_service.read_document("sample-lab", "franca/Sample.fidl")

        self.assertNotIn("content", workspace["documents"][0])
        self.assertIn("interface Sample", document["content"])

    def test_run_renderer_writes_node_vsomeip_configs(self):
        project_service.create_project("sample-lab", "Sample Lab")
        run_id = "run-render-1234"
        run_dir = simulation_service._run_dir(run_id)
        run_dir.mkdir(parents=True)
        simulation_service._write_metadata(run_id, {"id": run_id, "events": []})

        paths = simulation_service.render_vsomeip_configs("sample-lab", run_id)
        service_config = json.loads(paths["sample-lab-service"].read_text())
        client_config = json.loads(paths["sample-lab-client"].read_text())

        self.assertEqual(service_config["service-discovery"]["enable"], "true")
        self.assertEqual(service_config["services"][0]["service"], "0x1201")
        self.assertEqual(client_config["services"][0]["unicast"], "sample-lab-service")

    def test_run_history_artifacts_and_capture_paths_are_project_scoped(self):
        project_service.create_project("sample-lab", "Sample Lab")
        run_id = "run-artifact-1234"
        run_dir = simulation_service._run_dir(run_id)
        (run_dir / "logs").mkdir(parents=True)
        (run_dir / "captures").mkdir()
        (run_dir / "configs").mkdir()
        simulation_service._write_metadata(
            run_id,
            {
                "id": run_id,
                "project_id": "sample-lab",
                "scenario_id": "smoke",
                "scenario_name": "Smoke Start",
                "status": "stopped",
                "created_at": "2026-05-22T00:00:00+00:00",
                "events": [],
                "capture": {},
            },
        )
        (run_dir / "compose.yaml").write_text("services: {}\n")
        (run_dir / "logs" / "compose.log").write_text("compose output")
        (run_dir / "captures" / "smoke.pcapng").write_bytes(b"pcap")

        history = simulation_service.list_project_runs("sample-lab")
        artifacts = simulation_service.run_artifacts(run_id)

        self.assertEqual(history[0]["id"], run_id)
        self.assertEqual(artifacts["compose_log"], "compose output")
        self.assertEqual(
            simulation_service.capture_path(run_id, "smoke.pcapng").name, "smoke.pcapng"
        )
        self.assertEqual(
            artifacts["captures"][0]["wireshark_path"],
            f"/captures/{run_id}/captures/smoke.pcapng",
        )
        with self.assertRaises(FileNotFoundError):
            simulation_service.capture_path(run_id, "../metadata.json")

    def test_overview_recommends_authoring_before_validation(self):
        project_service.create_project("sample-lab", "Sample Lab")

        overview = workflow_service.project_overview("sample-lab")

        self.assertEqual(overview["recommended_action"]["kind"], "author")
        self.assertEqual(overview["readiness_gates"][0]["id"], "validation")

    def test_v1_api_routes_replace_studio_routes(self):
        paths = {getattr(route, "path", "") for route in app.routes}

        self.assertIn("/api/v1/workbench/overview", paths)
        self.assertIn("/api/v1/projects/{project_id}/overview", paths)
        self.assertIn("/api/v1/runs/{run_id}/inspection", paths)
        self.assertNotIn("/api/studio/home", paths)
        self.assertNotIn("/api/projects", paths)
        self.assertNotIn("/api/runs/{run_id}", paths)
        self.assertNotIn("/api/build", paths)
        self.assertNotIn("/api/process/start", paths)
        self.assertNotIn("/api/docker/start", paths)

    def test_v1_openapi_routes_have_stable_operations_and_response_schemas(self):
        paths = app.openapi()["paths"]

        for path, operations in paths.items():
            if not path.startswith("/api/v1") and path != "/health":
                continue
            for method, operation in operations.items():
                if method not in {"get", "post", "put", "delete", "patch"}:
                    continue
                self.assertIn(
                    "operationId", operation, f"{method} {path} has no operation id"
                )
                if "/captures/" not in path:
                    self.assertIn(
                        "schema",
                        operation["responses"]["200"]["content"]["application/json"],
                        f"{method} {path} has no JSON schema",
                    )


if __name__ == "__main__":
    unittest.main()
