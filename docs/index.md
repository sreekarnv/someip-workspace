# SOME/IP Workbench Documentation

These docs are for developers who know basic SOME/IP and SOME/IP-SD and want to use the workbench without guessing how the UI, project files, generators, Docker, and Wireshark fit together.

The workbench is project first. Create or import a project, edit its Franca and deployment source, validate it, generate artifacts, build generated transport nodes, run a saved scenario, and inspect the evidence.

## Start Here

| Guide | Use it for |
|-------|------------|
| [Getting started](getting-started.md) | Install prerequisites, start the API and web UI, and run the DoorControl happy path |
| [Project creation](project-creation.md) | Understand Starter, Door Control, and Climate Control presets before creating a project |
| [Project model](project-model.md) | Understand `project.yaml`, `franca/`, `scenarios/`, `generated/`, and `runs/` |
| [Workbench workflow](workbench-workflow.md) | Learn what each project page does and when to use it |
| [Authored vs generated](generated-vs-authored.md) | Understand which files you write, which files are generated, and which files are runtime artifacts |
| [Troubleshooting](troubleshooting.md) | Fix common validation, build, run, and capture problems |
| [Glossary](glossary.md) | Quick definitions for terms used in the workbench |

## Mental Model

A project has two important layers:

1. Editable source under `projects/<project-id>/`.
2. Derived output under `projects/<project-id>/generated/`, `build/`, and `runs/`.

Do not treat generated output as the source of truth. If the UI says a project has no `.fidl` or `.fdepl` document, fix the project source or manifest first. Validation does not invent missing Franca source files.

## Project Presets

All presets now use the same runtime model: project source is seeded under `projects/`, generation creates raw-vsomeip transport nodes, build compiles those nodes, and simulation runs them in Docker.

| Preset | What you get | Runtime |
|--------|--------------|---------|
| Starter | Minimal `.fidl`, `.fdepl`, manifest nodes, and smoke scenario | Generated raw-vsomeip nodes |
| Door Control | Door contract, deployment IDs, topology, and basic lock scenario | Generated raw-vsomeip nodes |
| Climate Control | HVAC contract, deployment IDs, topology, and comfort scenario | Generated raw-vsomeip nodes |

Raw-vsomeip nodes are protocol simulation nodes. They are useful for SOME/IP-SD traffic and packet capture while complete CommonAPI proxy/stub generation remains a toolchain limitation.
