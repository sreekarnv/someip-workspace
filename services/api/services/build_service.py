import asyncio
import os
import shutil
from pathlib import Path
from typing import Callable, Optional

from services import project_service

WORKSPACE = Path(__file__).resolve().parent.parent.parent.parent
BUILD_DIR = WORKSPACE / "build"


def runtime_readiness() -> dict:
    checks = {
        "vsomeip_headers": WORKSPACE / "libs" / "vsomeip" / "interface" / "vsomeip" / "vsomeip.hpp",
        "vsomeip_library": BUILD_DIR / "vsomeip" / "libvsomeip3.so",
    }
    missing = [name for name, path in checks.items() if not path.exists()]
    return {
        "ready": not missing,
        "detail": "ready" if not missing else f"missing {', '.join(missing)}; run ./scripts/02-build-libs.sh",
    }


async def build_project(
    project_id: str,
    clean: bool = False,
    generate: bool = True,
    log_callback: Optional[Callable] = None,
) -> bool:
    from services.generator_service import generate_project

    project_service.load_manifest(project_id)
    if generate:
        generated = await generate_project(project_id, log_callback)
        if not generated:
            project_service.update_metadata(
                project_id, build={"status": "blocked", "reason": "generation failed"}
            )
            return False

    success = await _compile_generated_project(
        project_id, clean=clean, log_callback=log_callback
    )
    metadata = project_service.load_metadata(project_id).get("generated_nodes", {})
    project_service.update_metadata(
        project_id,
        build={
            "status": "ready" if success else "failed",
            "built_at": project_service.utc_now(),
            "artifact_type": "generated-vsomeip",
            "runtime_kind": "generated-vsomeip",
            "service_binary": metadata.get("service_binary"),
            "client_binary": metadata.get("client_binary"),
        },
    )
    return success


async def _compile_generated_project(
    project_id: str, clean: bool = False, log_callback: Optional[Callable] = None
) -> bool:
    readiness = runtime_readiness()
    if not readiness["ready"]:
        if log_callback:
            await log_callback(f"Runtime libraries are not ready: {readiness['detail']}\n")
        return False

    project_root = project_service._project_dir(project_id)
    source_dir = project_root / "generated" / "nodes" / "vsomeip"
    if not (source_dir / "CMakeLists.txt").exists():
        if log_callback:
            await log_callback(
                "Generated raw-vsomeip node project was not found. Run generation before build.\n"
            )
        return False

    build_dir = BUILD_DIR / "projects" / project_id
    if clean and build_dir.exists():
        if log_callback:
            await log_callback(f"Cleaning build directory: {build_dir}\n")
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    cmake_cmd = [
        "cmake",
        "-DCMAKE_CXX_STANDARD=20",
        f"-DCMAKE_PREFIX_PATH={BUILD_DIR}/vsomeip",
        str(source_dir),
    ]
    if log_callback:
        await log_callback(f"Building generated raw-vsomeip nodes for {project_id}\n")
        await log_callback(f"Running: {' '.join(cmake_cmd)}\n")

    cmake_proc = await asyncio.create_subprocess_exec(
        *cmake_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(build_dir),
    )
    while True:
        line = await cmake_proc.stdout.readline()
        if not line:
            break
        if log_callback:
            await log_callback(line.decode("utf-8", errors="replace"))
    await cmake_proc.wait()
    if cmake_proc.returncode != 0:
        if log_callback:
            await log_callback(f"CMake failed with return code {cmake_proc.returncode}\n")
        return False

    make_cmd = ["make", f"-j{os.cpu_count() or 4}"]
    if log_callback:
        await log_callback(f"Running: {' '.join(make_cmd)}\n")
    make_proc = await asyncio.create_subprocess_exec(
        *make_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(build_dir),
    )
    while True:
        line = await make_proc.stdout.readline()
        if not line:
            break
        if log_callback:
            await log_callback(line.decode("utf-8", errors="replace"))
    await make_proc.wait()
    success = make_proc.returncode == 0
    if log_callback:
        await log_callback(f"Generated node build {'succeeded' if success else 'failed'}\n")
    return success
