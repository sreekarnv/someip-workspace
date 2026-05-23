# Authored, Generated, And Derived Files

The workbench uses several kinds of files. Keeping them separate prevents most confusion.

## Authored Or Seeded Source

These files are the source of truth. They are created by a preset, imported with a project, or edited by you.

| Path | Meaning |
|------|---------|
| `projects/<project-id>/project.yaml` | Project manifest, topology, and scenario list |
| `projects/<project-id>/franca/*.fidl` | Franca interface source |
| `projects/<project-id>/franca/*.fdepl` | SOME/IP deployment source |
| `projects/<project-id>/scenarios/*.yaml` | Saved scenario source |
| `projects/<project-id>/nodes/` | Editable node implementation area for future CommonAPI-backed logic |

If these files are missing, validation cannot fix that by itself.

## Generated Files

Generated files are produced from authored source.

| Path | Meaning |
|------|---------|
| `projects/<project-id>/generated/interface-index.json` | Interface and deployment summary created by validation |
| `projects/<project-id>/generated/commonapi/` | CommonAPI/SOME-IP generator output where available |
| `projects/<project-id>/generated/nodes/vsomeip/` | Generated raw-vsomeip service/client node source |
| `build/projects/<project-id>/` | Compiled generated project node binaries |

Generated files can be recreated. Do not edit them as the main source of truth.

## Runtime-Derived Files

Runtime files are created for a specific simulation run.

| Path | Meaning |
|------|---------|
| `runs/<run-id>/compose.yaml` | Rendered Docker Compose file for that run |
| `runs/<run-id>/configs/*.json` | Rendered per-node `vsomeip.json` files |
| `runs/<run-id>/logs/` | Compose and runtime logs |
| `runs/<run-id>/captures/*.pcapng` | Packet capture artifacts |
| `runs/<run-id>/metadata.json` | Run status and structured event history |

Runtime files are evidence. They are useful for debugging but should not be edited to change the project design.

## What Validation Does

Validation reads `project.yaml` and the manifest-listed `.fidl` and `.fdepl` files. It writes diagnostics in metadata and `generated/interface-index.json`.

Validation does not create missing `.fidl` or `.fdepl` files.

## What Generation Does

Generation runs the CommonAPI generator path from the Franca and deployment source. It also writes a generated raw-vsomeip node project so the workbench can build runnable protocol simulation nodes even when full CommonAPI Core output is unavailable.

Current limitation: the bundled Core generator path can report `transport-only`. That means SOME/IP transport artifacts, raw-vsomeip node sources, and metadata may exist, but complete Core proxy/stub headers for full CommonAPI node projects are not available yet.

## What Build Does

Build compiles generated raw-vsomeip node sources under:

```text
projects/<project-id>/generated/nodes/vsomeip
```

The resulting binaries are written under:

```text
build/projects/<project-id>/
```

Docker simulation uses those binaries through `docker/Dockerfile.project`.
