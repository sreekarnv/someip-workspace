# Agent Instructions

## Workspace Shape

```text
libs/                         Trimmed COVESA vsomeip and CommonAPI runtime sources
build/                        Runtime, example, and generated build output
tools/generators/             Downloaded CommonAPI generator executables
projects/                     Editable manifest-backed workbench projects
runs/                         Per-simulation Docker configs, logs, and captures
services/api/                 FastAPI workflow API
services/web/                 React/Vite workbench UI
scripts/                      Setup, runtime build, generator download, and OpenAPI scripts
docker/                       Runtime image and Wireshark container definitions
docs/                         User workflow documentation and troubleshooting guides
start-workbench.sh            Single API and web startup entry point
README.md                     Repository overview with links into docs/
LICENSE and NOTICE            Top-level Apache-2.0 license and license boundary notes
```

Do not reintroduce the removed example/process/docker product workflow. The product flow is project first and runs through the web UI and typed `/api/v1` endpoints.

Keep `docs/` as the detailed user/developer guide set. README should stay a concise repository overview that links into docs. When behavior changes project creation, source-vs-generated files, build blockers, generator limitations, or run inspection, update the matching docs file in the same change.

The top-level Apache-2.0 license applies to original workbench code unless a file or directory says otherwise. Preserve upstream COVESA and generated CommonAPI license notices.

## Setup And Startup

```bash
./scripts/01-setup.sh
./scripts/02-build-libs.sh
./scripts/03-download-generators.sh

cd services/web
pnpm install
cd ../..

./start-workbench.sh dev
```

Use `./start-workbench.sh prod` for a built web preview. The launcher starts both FastAPI and Vite/preview. Keep it as the single startup script. It must check for `pnpm` before starting either service and fail clearly when `pnpm` is unavailable.

`scripts/01-setup.sh` creates the API virtual environment at `services/api/.venv`. `start-workbench.sh` accepts `PYTHON_BIN` when a specific Python interpreter is required. The web service uses the committed pnpm lockfile and keeps required dependency build approvals, such as `esbuild`, in `services/web/pnpm-workspace.yaml`.

## Project Workflow

Editable simulation source belongs under `projects/<project-id>/`.

```text
projects/<project-id>/
  project.yaml
  franca/
    <interface>.fidl
    <interface>.fdepl
  scenarios/
    <scenario>.yaml
  nodes/
  generated/
```

- `project.yaml` owns nodes, topology, scenarios, and project intent.
- Franca `.fidl` files and deployment `.fdepl` files are authored or preset-seeded source. They are not created by validation.
- Validation reads manifest-listed Franca/deployment files and writes derived metadata such as `generated/interface-index.json`.
- `build/` and `runs/` are derived output.
- Create or import projects from the UI unless the task explicitly requires a file-level fixture.
- Project validation, generation, build, simulation, stop, capture download, and inspection belong to the project workflow, not standalone example scripts.

Project presets such as Starter, DoorControl, and Climate Control create FIDL/FDEPL, manifest nodes, and scenarios. Generation emits raw-vsomeip service/client node sources so projects can build/run SOME/IP traffic without handwritten fallback code. Do not describe generated raw-vsomeip nodes as complete CommonAPI proxy/stub implementations.

## API Contract

FastAPI is an API service only:

- `/api/v1`
- `/health`
- `/openapi.json`
- `/docs`

Public JSON routes should use Pydantic request and response models, stable `operation_id` values, and grouped routers under `services/api/routes/v1/`.

OpenAPI is the HTTP contract source of truth:

```bash
./scripts/export-openapi.sh
./scripts/generate-web-api.sh
./scripts/check-web-api.sh
```

- `services/api/openapi/v1.json` is exported from `app.openapi()`.
- `services/web/src/generated/openapi.ts` and `services/web/src/generated/workflowApi.ts` are generated from that schema.
- Do not hand-write duplicate HTTP DTOs in the web service when generated types already cover them.
- WebSocket transport remains handwritten, but event payloads should stay aligned with API event schemas.

## Web Service

The web service lives in `services/web` and consumes the generated RTK Query layer.

Canonical user routes are:

- `/dashboard`
- `/projects`
- `/projects/:projectId`
- `/projects/:projectId/author`
- `/projects/:projectId/build`
- `/projects/:projectId/simulate`
- `/projects/:projectId/runs/:runId`

Keep build and run controls scoped to project routes. The run inspection route should prioritize debugging meaning: run state, node state, scenario evidence, packet capture evidence, Wireshark action, then artifacts and logs.

## Verification

Backend checks:

```bash
python3 -m compileall services/api/main.py services/api/routes/v1 services/api/schemas services/api/services
PYTHONPATH=services/api python3 -m unittest services/api/tests/test_workbench_services.py -v
```

Web checks:

```bash
cd services/web
pnpm run build
pnpm test
```

Run `./scripts/check-web-api.sh` when API schemas or web generated endpoints change.

## Runtime Notes

- Runtime libraries come from COVESA vsomeip and CommonAPI sources under `libs/`.
- `scripts/02-build-libs.sh` builds the runtime artifacts into the `build/` layout used by project builds and Docker. The source trees are trimmed, so the script tolerates missing optional non-runtime vsomeip/CommonAPI build inputs.
- Docker project runs render per-run Compose and vsomeip configs under `runs/`.
- Wireshark is started through `docker/wireshark-compose.yml` and capture snapshots are saved with run artifacts.
- A SOME/IP service node is normally the routing manager for its run topology.

## Documentation Notes

- `docs/index.md` is the documentation entry point.
- `docs/project-creation.md` owns preset and generated-runtime explanation.
- `docs/project-model.md` owns manifest and directory semantics.
- `docs/generated-vs-authored.md` owns authored/generated/runtime artifact boundaries.
- `docs/troubleshooting.md` owns common user-facing failure messages and fixes.
- Keep docs beginner-friendly for developers with basic SOME/IP knowledge.

## Toolchain Limits

- The bundled generator toolchain can report `transport-only` because complete Core proxy/stub headers are not emitted for fully generated node implementations.
- If the Core and SOME/IP generator binaries are identical, the backend skips invalid Core `.fidl` generation and logs a toolchain warning instead of surfacing the `.fdepl` extension error to users.
- SOME/IP transport artifacts, editable node templates, generated raw-vsomeip nodes, Docker runs, and packet capture collection can still exist in that state.
- Projects build/run through generated raw-vsomeip nodes until complete CommonAPI Core proxy/stub output is available.
- Franca scenario calls, subscriptions, event waits, and response assertions remain limited until generated scenario-driver sources implement them.

## Franca And SOME/IP Facts

- Use `Boolean`, not `Bool`, in Franca source.
- `state` is a Franca reserved word.
- `fireAndForget` methods need a body block.
- Custom SOME/IP service IDs should stay in the project deployment files and be validated against the project topology.
- Keep application names unique in project manifests because they become vsomeip runtime identities.
