import asyncio
import os
import shutil
from pathlib import Path
from typing import Callable, Optional
from services import project_service

WORKSPACE = Path(__file__).resolve().parent.parent.parent.parent
BUILD_DIR = WORKSPACE / "build"
EXAMPLES_DIR = WORKSPACE / "examples"


async def build_example(
    example_name: str, clean: bool = False, log_callback: Optional[Callable] = None
) -> bool:
    example_dir = EXAMPLES_DIR / example_name

    if not example_dir.exists():
        if log_callback:
            await log_callback(f"Example directory not found: {example_dir}")
        return False

    return await _compile_example(example_name, clean, log_callback)


async def build_project(
    project_id: str,
    clean: bool = False,
    generate: bool = True,
    log_callback: Optional[Callable] = None,
) -> bool:
    from services.generator_service import generate_project

    manifest = project_service.load_manifest(project_id)
    if generate:
        generated = await generate_project(project_id, log_callback)
        if not generated:
            project_service.update_metadata(
                project_id, build={"status": "blocked", "reason": "generation failed"}
            )
            return False

    manifest = project_service.load_manifest(project_id)
    source_example = manifest.get("source_example")
    if not source_example:
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
                "source_example": None,
                "service_binary": metadata.get("service_binary"),
                "client_binary": metadata.get("client_binary"),
            },
        )
        return success

    if log_callback:
        await log_callback(
            f"Building sample-backed node artifacts from examples/{source_example}\n"
        )
    success = await build_example(
        source_example, clean=clean, log_callback=log_callback
    )
    project_service.update_metadata(
        project_id,
        build={
            "status": "ready" if success else "failed",
            "built_at": project_service.utc_now(),
            "artifact_type": "source-example",
            "source_example": source_example,
        },
    )
    return success


async def _compile_generated_project(
    project_id: str, clean: bool = False, log_callback: Optional[Callable] = None
) -> bool:
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


async def _compile_example(
    example_name: str, clean: bool = False, log_callback: Optional[Callable] = None
) -> bool:
    build_dir = BUILD_DIR / "examples" / example_name
    alt_name = example_name.lower()
    alt_build_dir = BUILD_DIR / "examples" / alt_name
    example_dir = EXAMPLES_DIR / example_name

    if not build_dir.exists() and alt_build_dir.exists():
        build_dir = alt_build_dir

    if clean and build_dir.exists():
        if log_callback:
            await log_callback(f"Cleaning build directory: {build_dir}")
        import shutil

        shutil.rmtree(build_dir)

    build_dir.mkdir(parents=True, exist_ok=True)

    cmake_cmd = [
        "cmake",
        "-DCMAKE_CXX_STANDARD=20",
        f"-DCMAKE_INSTALL_PREFIX={BUILD_DIR}/install",
        f"-DCMAKE_PREFIX_PATH={BUILD_DIR}/install;{BUILD_DIR}/vsomeip",
        str(example_dir),
    ]

    if log_callback:
        await log_callback(f"Running: {' '.join(cmake_cmd)}")

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
        text = line.decode("utf-8", errors="replace")
        if log_callback:
            await log_callback(text)

    await cmake_proc.wait()
    if cmake_proc.returncode != 0:
        if log_callback:
            await log_callback(f"CMake failed with return code {cmake_proc.returncode}")
        return False

    make_cmd = ["make", f"-j{os.cpu_count() or 4}"]
    if log_callback:
        await log_callback(f"Running: {' '.join(make_cmd)}")

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
        text = line.decode("utf-8", errors="replace")
        if log_callback:
            await log_callback(text)

    await make_proc.wait()
    success = make_proc.returncode == 0

    if log_callback:
        await log_callback(f"Build {'succeeded' if success else 'failed'}")

    return success
