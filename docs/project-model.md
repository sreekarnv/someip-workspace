# Project Model

A workbench project is an editable directory under `projects/`. It is the source of truth for authoring and simulation intent.

## Directory Layout

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

Derived build and run output lives outside or below the editable project source:

```text
build/projects/<project-id>/
runs/<run-id>/
  compose.yaml
  configs/
  logs/
  captures/
  metadata.json
```

## `project.yaml`

`project.yaml` owns topology and workbench intent:

- Project id and display name.
- Franca and deployment document paths.
- Node ids, node roles, interfaces, and vsomeip application names.
- Network settings such as service discovery multicast and SD port.
- Scenario ids and scenario file paths.
- Optional `source_example` fallback metadata.

The manifest does not own the interface shape. The `.fidl` file owns that.

## Franca Source

`franca/*.fidl` owns the service contract:

- Package name.
- Interface name.
- Version.
- Methods.
- Broadcasts/events.
- Structs and enumerations.

Use Franca types such as `Boolean`, `String`, `UInt8`, `Int16`, and so on. Avoid using `state` as an identifier because it is reserved in Franca.

## Deployment Source

`franca/*.fdepl` owns SOME/IP deployment values:

- Service ID.
- Instance ID.
- Method IDs.
- Event IDs.
- Event groups.
- Transport ports when configured.

The UI inspector reads these values through the backend indexer. Docker and UI code should not parse Franca text independently.

## Scenarios

`scenarios/*.yaml` owns saved run steps. A scenario can describe node start order, waits, calls, assertions, and capture marks.

Some scenario actions, such as Franca method calls and event assertions, are limited until generated scenario-driver code exists. The run inspection UI reports this limitation.

## `source_example`

`source_example` controls whether the project has a checked-in C++ fallback implementation.

| Value | Meaning |
|-------|---------|
| `null` | No fallback C++ implementation. Build/run use generated project nodes after Generate and Build. |
| `DoorControl` | Build and Docker run use `examples/DoorControl`. |

Do not set `source_example` just because a project has Franca files. It should only point at a real directory under `examples/` that contains buildable service/client code. Source-only projects should leave it `null`.

## Generated Project Metadata

`projects/<project-id>/generated/` is derived output. Important files include:

- `interface-index.json`: created by validation from `.fidl` and `.fdepl` files.
- Generator metadata and output status.

You can delete and recreate generated output. Do not treat it as the source of truth.
