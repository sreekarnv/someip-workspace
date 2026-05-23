---
name: repo-hygiene
description: Use when cleaning unused code, updating repository layout, managing generated artifacts, adjusting .gitignore, checking license boundaries, keeping docs aligned, or preparing a commit.
license: Complete terms in LICENSE.txt
---

This skill keeps the workbench repository clean, explainable, and commit-ready without reintroducing removed legacy paths.

## Repository Boundaries

- Do not reintroduce the old example/process/docker product workflow.
- The product workflow is project first: create or import a project, validate, generate, build, simulate, and inspect through the web UI and typed `/api/v1` API.
- `projects/` contains editable project source.
- `build/` and `runs/` are derived output.
- `services/api/` is FastAPI only.
- `services/web/` is the React/Vite web service.
- `docs/` contains detailed user and developer guidance; README stays concise and links into docs.

## Cleanup Rules

- Remove unused code only after searching for references with `rg`.
- Do not delete user-authored project source or checked-in docs without confirming the replacement behavior.
- Keep generated OpenAPI and web API files in sync when API schemas change.
- Keep `.gitignore` focused on derived output, local virtualenvs, package installs, logs, captures, and build products.
- Avoid adding new scripts when the same operation is available through the UI or the existing `start-workbench.sh` and setup scripts.

## Documentation Rules

- Update docs in the same change when behavior changes project creation, source-vs-generated files, generation output, build blockers, simulation startup, run inspection, or troubleshooting messages.
- Use `docs/index.md` as the documentation entry point.
- Keep README as a repository overview, not a full user manual.
- Keep wording beginner-friendly for developers with basic SOME/IP knowledge.

## License And Attribution

- The top-level Apache-2.0 license applies to original workbench code unless a file or directory says otherwise.
- Preserve COVESA, BMW, MPL-2.0, Eclipse, Franca, and generated CommonAPI notices where they already exist.
- Do not strip license headers from vendored runtime sources or generated files.
- Keep `NOTICE` accurate when repository ownership or third-party boundary text changes.

## Verification

Use checks that match the scope of the change:

- Backend: `python3 -m compileall services/api/main.py services/api/routes/v1 services/api/schemas services/api/services`
- Backend services: `PYTHONPATH=services/api python3 -m unittest services/api/tests/test_workbench_services.py -v`
- Web: from `services/web`, run `pnpm run build` and `pnpm test`
- API contract: run `./scripts/check-web-api.sh` when Pydantic schemas, routes, OpenAPI, or generated web endpoints change
- Repo cleanup: use `git status --short` and `rg` to confirm stale references are gone
