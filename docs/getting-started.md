# Getting Started

This guide gets the local workbench running and walks through the first successful DoorControl flow.

## Requirements

Install these before starting:

- Linux with Docker and Docker Compose
- CMake 3.16 or newer
- GCC with C++20 support
- Boost development packages required by vsomeip
- Python 3.8 or newer
- Node.js 20 or newer
- pnpm on `PATH`
- Java and Maven only if you plan to build CommonAPI generators from source

## One-Time Setup

From the repository root:

```bash
./scripts/01-setup.sh
./scripts/02-build-libs.sh
./scripts/03-download-generators.sh

cd services/web
pnpm install
cd ../..
```

What these commands do:

- `01-setup.sh` creates the API virtual environment at `services/api/.venv`.
- `02-build-libs.sh` builds the runtime libraries into `build/`.
- `03-download-generators.sh` downloads the CommonAPI generator executables into `tools/generators/`.
- `pnpm install` installs the web UI dependencies.

## Start The Workbench

For development:

```bash
./start-workbench.sh dev
```

Open:

- Web UI: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`
- API health: `http://localhost:8000/health`

For a built web preview:

```bash
./start-workbench.sh prod
```

Open:

- Web preview: `http://localhost:4173`
- API docs: `http://localhost:8000/docs`

## First Successful Flow: DoorControl

Use DoorControl first because it is the current runnable sample-backed project.

1. Open `http://localhost:5173/projects`.
2. If `door-control` already exists, open it. If not, click **New project** and choose **Door Control**.
3. Open the project overview at `/projects/door-control`.
4. Follow the recommended next action. Usually this starts with validation.
5. Open **Author** and confirm `DoorControl.fidl` and `DoorControl.fdepl` are listed.
6. Click **Validate**.
7. Open **Build** and run generation/build.
8. Open **Simulate**, choose **Basic Lock Flow**, and start the scenario.
9. Open the run inspection page when the run starts.
10. Check node lifecycle, scenario events, capture state, Wireshark action, and artifacts.

## What Success Looks Like

A good DoorControl run should show:

- Franca validation is valid.
- Generation is ready or `transport-only` with an explicit warning.
- Build is ready.
- Simulation starts Docker containers.
- Run inspection shows node lifecycle events.
- A capture is available or capture state explains why it is not.

If packets are not visible, go to [Troubleshooting](troubleshooting.md#no-packets-visible-in-wireshark).
