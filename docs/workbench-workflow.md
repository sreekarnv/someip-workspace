# Workbench Workflow

The workbench is organized around project routes. Build and run operations are scoped to a project, not global examples or fallback samples.

## Routes

| Route | Purpose |
|-------|---------|
| `/dashboard` | Global readiness, project health, active runs, recent captures |
| `/projects` | Create, import, and browse projects |
| `/projects/:projectId` | Project overview, readiness, topology, latest evidence, next action |
| `/projects/:projectId/author` | Edit `.fidl` and `.fdepl`, validate, inspect diagnostics and IDs |
| `/projects/:projectId/build` | Generate artifacts, build runnable nodes, view job logs and generator warnings |
| `/projects/:projectId/simulate` | Choose a scenario, inspect blockers, start a run, edit scenario YAML |
| `/projects/:projectId/runs/:runId` | Inspect node state, events, packet capture evidence, Wireshark action, logs, and artifacts |

## Overview

Start at the project overview. It summarizes:

- Validation state.
- Generation state.
- Build state.
- Latest run state.
- Recommended next action.
- Topology and recent runs.

If you are unsure what to do next, follow the recommended action.

## Author

Use Author to edit the source contract:

- `.fidl` files define the Franca interface.
- `.fdepl` files define SOME/IP deployment values.
- Validation reads the manifest-listed documents and produces diagnostics.
- Validation writes `generated/interface-index.json` for UI summaries.

If Author shows no files, check `project.yaml` and the `franca/` directory.

## Build

Use Build after validation.

The build page separates three gates:

1. Validate Franca.
2. Generate CommonAPI/SOME-IP artifacts.
3. Build runnable nodes.

Generation creates a raw-vsomeip node project when full CommonAPI Core proxy/stub output is unavailable. Build compiles that generated project for every preset, including DoorControl and ClimateControl.

## Simulate

Use Simulate after build is ready.

This page shows:

- Available scenarios.
- Run blockers.
- Participating nodes.
- Scenario YAML.
- Recent project runs.

If a project has no runnable node artifacts, start will be blocked. Run Generate and Build so the raw-vsomeip nodes are compiled first.

## Run Inspection

Run inspection is the debug surface. Read it in this order:

1. Run status and scenario result.
2. Node lifecycle.
3. Packet/capture evidence.
4. Timeline events.
5. Logs and rendered artifacts.

Wireshark remains the deep packet inspection tool. The workbench provides capture files, links, filters, and evidence summaries around it.

## Expected Blockers

| Blocker | Meaning | What to do |
|---------|---------|------------|
| Validation failed | Franca or deployment source is missing or invalid | Fix source in Author and validate again |
| Generation is `transport-only` | The current generator path lacks complete Core proxy/stub output | Continue only if the workflow allows it; read the warning |
| No generated node artifacts | Generation/build has not produced project binaries | Run Generate and Build, then retry simulation |
| Run blocked before simulation | Validation/build/run prerequisites are not met | Open Simulate and read blockers |
