# Troubleshooting

Use this guide by matching the message you see in the UI.

## `Project has no .fidl document`

The backend could not find any manifest-listed Franca IDL file.

Check `projects/<project-id>/project.yaml`:

```yaml
franca:
  fidl:
    - franca/ClimateControl.fidl
```

Then confirm the file exists:

```text
projects/<project-id>/franca/ClimateControl.fidl
```

Validation does not create this file. It must be created by the preset, import, or your editor.

## `Project has no .fdepl document`

The backend could not find any manifest-listed deployment file.

Check `project.yaml`:

```yaml
franca:
  deployment:
    - franca/ClimateControl.fdepl
```

Then confirm the file exists under `projects/<project-id>/franca/`.

## Build Blocked: Generated Nodes Missing

Build needs the generated raw-vsomeip node project created by the Generate step.

Check for:

```text
projects/<project-id>/generated/nodes/vsomeip/CMakeLists.txt
```

If it is missing, run **Generate** from the Build page. If runtime libraries are missing, run:

```bash
./scripts/02-build-libs.sh
```

## Build Artifacts Are Missing

Simulation needs compiled binaries under:

```text
build/projects/<project-id>/
```

Run **Build nodes** again. If the project was cleaned manually, generation metadata may still say ready while binaries are gone.

## Generator Output Is `transport-only`

The current CommonAPI generator path does not provide all Core proxy/stub headers needed for complete generated CommonAPI node builds.

If an old job log says `The file extension should be .fdepl` while running the Core generator, the Core executable was behaving like the SOME/IP deployment generator. Newer generation jobs skip that invalid `.fidl` invocation and report a toolchain warning instead.

What still works:

- Franca/deployment validation.
- Interface index generation.
- SOME/IP transport artifact generation where available.
- Generated raw-vsomeip node builds and Docker runs.
- Packet capture collection.

What may be blocked:

- Full CommonAPI proxy/stub node builds.
- Generated scenario-driver calls and event assertions.

## Run Blocked Before Simulation

Open `/projects/<project-id>/simulate` and read the blockers.

Common causes:

- Validation is not valid.
- Generation has not produced node sources.
- Build is not ready.
- Runtime libraries are missing.
- Docker is unavailable.
- Compiled project binaries are missing.
- The project has no runnable nodes.

Fix the earliest blocker first. Usually the order is Author, Build, Simulate.

## No Packets Visible In Wireshark

Check these in order:

1. Confirm the project build is ready.
2. Confirm the run actually started containers.
3. Open the run inspection page and check node lifecycle events.
4. Check capture state and capture files in Inspect.
5. Confirm Wireshark Compose is running.
6. Use display filter `someip || someipsd`.
7. Check rendered `vsomeip.json` files under `runs/<run-id>/configs/`.
8. Check `runs/<run-id>/logs/compose.log` for Docker failures.

If the run failed before containers started, Wireshark will not show SOME/IP traffic.

## Existing Project Looks Stale After Preset Changes

Projects are editable directories. Updating the preset code does not automatically rewrite an existing project.

If an old project has empty Franca lists, repair or recreate it:

```yaml
franca:
  fidl:
    - franca/<Interface>.fidl
  deployment:
    - franca/<Interface>.fdepl
```

Then make sure the files exist and validate again from Author.
