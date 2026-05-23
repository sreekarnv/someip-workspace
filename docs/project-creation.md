# Project Creation

Project creation is where most confusion happens. The key rule is simple: creating a project should write the editable source files. Validation and generation happen later.

## UI Steps

1. Open `/projects`.
2. Click **New project**.
3. Choose starter content.
4. Confirm the `Project ID`.
5. Confirm the display name.
6. Click **Create project**.
7. Open the project overview and follow the recommended next action.

The project is created under `projects/<project-id>/`.

## Preset Types

| Preset | Type | What it creates | Runtime fallback |
|--------|------|-----------------|------------------|
| Starter | Source-only generic project | Minimal `.fidl`, `.fdepl`, `project.yaml`, nodes, scenario YAML, and generated raw-vsomeip nodes after generation | None |
| Climate Control | Source-only vehicle body contract | Climate `.fidl`, `.fdepl`, manifest nodes, `comfort-flow` scenario YAML, and generated raw-vsomeip nodes after generation | None |
| Door Control | Runnable sample-backed project | Door `.fidl`, `.fdepl`, manifest nodes, scenario YAML, and `source_example: DoorControl` | `examples/DoorControl` |

## Source-Only Projects

Source-only projects start from valid project source and do not include checked-in C++ service/client fallback binaries. During generation, the workbench creates derived raw-vsomeip service/client sources so Docker can still produce SOME/IP and SOME/IP-SD traffic while full CommonAPI Core output is unavailable.

A source-only project can usually:

- Show documents in Author.
- Validate Franca and deployment source.
- Produce `generated/interface-index.json`.
- Run the generator path as far as the current toolchain supports.
- Build generated raw-vsomeip service/client binaries.
- Run Docker simulations that produce SOME/IP and SOME/IP-SD traffic.

Generated raw-vsomeip nodes are protocol simulation nodes. They do not provide complete CommonAPI proxy/stub behavior or full Franca scenario-driver semantics yet.

## Runnable Sample-Backed Projects

Runnable sample-backed projects use checked-in C++ code while the fully generated node path is incomplete.

DoorControl is currently the supported runnable sample. Its manifest has:

```yaml
source_example: DoorControl
```

That tells the build and Docker path to use `examples/DoorControl` for service/client binaries.

## Important: FIDL And FDEPL Are Seeded, Not Validation-Generated

When you create a project from a preset, the `.fidl` and `.fdepl` documents should be written immediately under `projects/<project-id>/franca/` and referenced by `project.yaml`.

Validation does not create missing `.fidl` or `.fdepl` files. Validation reads the manifest, opens the listed documents, checks them, and writes derived metadata such as:

```text
projects/<project-id>/generated/interface-index.json
```

If the inspector says `Project has no .fidl document` or `Project has no .fdepl document`, inspect `project.yaml` first. The `franca.fidl` and `franca.deployment` lists must point at real files.

## Expected Source-Only ClimateControl Shape

A source-only Climate Control project should look like this:

```text
projects/climate-control/
  project.yaml
  franca/
    ClimateControl.fidl
    ClimateControl.fdepl
  scenarios/
    comfort-flow.yaml
  nodes/
  generated/
```

Its manifest should have `source_example: null` and should reference the Franca files:

```yaml
source_example: null
franca:
  fidl:
    - franca/ClimateControl.fidl
  deployment:
    - franca/ClimateControl.fdepl
```
