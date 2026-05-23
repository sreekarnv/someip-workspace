# SOME/IP Workbench Documentation

These docs are for developers who already know the basics of SOME/IP and SOME/IP-SD and want to use this workspace without guessing how the UI, project files, generators, Docker, and Wireshark fit together.

The workbench is project first. Create or import a project, edit its Franca and deployment source, validate it, generate artifacts, build runnable nodes when available, run a saved scenario, and inspect the evidence.

## Start Here

| Guide | Use it for |
|-------|------------|
| [Getting started](getting-started.md) | Install prerequisites, start the API and web UI, and run the DoorControl happy path |
| [Project creation](project-creation.md) | Understand Starter, Climate Control, and Door Control presets before creating a project |
| [Project model](project-model.md) | Understand `project.yaml`, `franca/`, `scenarios/`, `generated/`, and `runs/` |
| [Workbench workflow](workbench-workflow.md) | Learn what each project page does and when to use it |
| [Authored vs generated](generated-vs-authored.md) | Understand which files you write, which files are generated, and which files are runtime artifacts |
| [Troubleshooting](troubleshooting.md) | Fix common validation, build, run, and capture problems |
| [Glossary](glossary.md) | Quick definitions for terms used in the workbench |

## Mental Model

A project has two important layers:

1. Editable source under `projects/<project-id>/`.
2. Derived output under `build/`, `projects/<project-id>/generated/`, and `runs/`.

Do not treat generated output as the source of truth. If the UI says a project has no `.fidl` or `.fdepl` document, fix the project source or manifest first. Validation does not invent missing Franca source files.

## Project Creation Paths

There are two project creation paths:

| Path | What you get | Can build and run now? |
|------|--------------|------------------------|
| Source-only project | `.fidl`, `.fdepl`, `project.yaml`, nodes, scenario YAML, and generated raw-vsomeip nodes | Yes, after Generate and Build, with limited Franca semantics |
| Runnable sample-backed project | Project files plus `source_example` pointing at checked-in C++ sample code | Yes, for supported samples |

Currently DoorControl is the runnable sample-backed path. Starter and Climate Control are source-only paths that run through generated raw-vsomeip nodes after generation/build.
