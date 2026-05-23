# Authored, Generated, And Derived Files

The workbench uses several kinds of files. Keeping them separate prevents most confusion.

## Authored Or Seeded Source

These files are the source of truth. They are created by a preset, imported with a project, or edited by you.

| Path | Meaning |
|------|---------|
| `projects/<project-id>/project.yaml` | Project manifest, topology, scenario list, optional fallback metadata |
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
| `projects/<project-id>/generated/` | Generator metadata and generated artifacts |
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

Validation reads:

- `project.yaml`
- Manifest-listed `.fidl` files
- Manifest-listed `.fdepl` files

Validation writes:

- Diagnostics in project metadata
- `generated/interface-index.json`

Validation does not create missing `.fidl` or `.fdepl` files.

## What Generation Does

Generation runs the CommonAPI generator path from the Franca and deployment source.

Current limitation: the bundled Core generator path can report `transport-only`. That means SOME/IP transport artifacts, raw-vsomeip node sources, and metadata may exist, but complete Core proxy/stub headers for full CommonAPI node projects are not available yet.

In `transport-only` state:

- Interface/deployment summaries can still be useful.
- Docker runs can still work for runnable sample-backed projects such as DoorControl.
- Source-only projects can build and run generated raw-vsomeip nodes for protocol traffic.

## What Build Does

Build attempts to create runnable node artifacts.

For `source_example: DoorControl`, build uses `examples/DoorControl`.

For `source_example: null`, build uses generated raw-vsomeip node sources under `projects/<project-id>/generated/nodes/vsomeip`.
