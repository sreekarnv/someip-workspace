# Project Creation

Project creation writes editable source files. Validation and generation happen later.

## UI Steps

1. Open `/projects`.
2. Click **New project**.
3. Choose starter content.
4. Confirm the `Project ID`.
5. Confirm the display name.
6. Click **Create project**.
7. Open the project overview and follow the recommended next action.

The project is created under `projects/<project-id>/`.

## Presets

| Preset | What it creates | Runtime kind |
|--------|-----------------|--------------|
| Starter | Minimal `.fidl`, `.fdepl`, `project.yaml`, nodes, and smoke scenario YAML | Generated raw-vsomeip |
| Door Control | Door `.fidl`, `.fdepl`, manifest nodes, and `basic-lock-flow` scenario YAML | Generated raw-vsomeip |
| Climate Control | Climate `.fidl`, `.fdepl`, manifest nodes, and `comfort-flow` scenario YAML | Generated raw-vsomeip |

A preset does not provide handwritten service/client fallback code. Build and simulation use generated project nodes for every preset.

## What Gets Written

When you create a project from a preset, these files should exist immediately:

```text
projects/<project-id>/
  project.yaml
  franca/
    <Interface>.fidl
    <Interface>.fdepl
  scenarios/
    <scenario>.yaml
  nodes/
  generated/
```

The `.fidl` and `.fdepl` documents are seeded source. They are not produced by validation.

Validation reads the manifest, opens the listed documents, checks them, and writes derived metadata such as:

```text
projects/<project-id>/generated/interface-index.json
```

If the inspector says `Project has no .fidl document` or `Project has no .fdepl document`, inspect `project.yaml` first. The `franca.fidl` and `franca.deployment` lists must point at real files.

## Generated Runtime

After validation, generation creates transport artifacts and a generated raw-vsomeip node project under:

```text
projects/<project-id>/generated/nodes/vsomeip/
```

Build compiles those nodes into:

```text
build/projects/<project-id>/
```

Simulation then runs those binaries through `docker/Dockerfile.project`.

Generated raw-vsomeip nodes are protocol simulation nodes. They do not provide complete CommonAPI proxy/stub behavior or full Franca scenario-driver semantics yet.
