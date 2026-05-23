import asyncio
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List

WORKSPACE = Path(__file__).resolve().parent.parent.parent.parent
WIRESHARK_COMPOSE = WORKSPACE / "docker" / "wireshark-compose.yml"


def docker_ready() -> Dict:
    if not shutil.which("docker"):
        return {"ready": False, "detail": "docker command not found"}
    try:
        result = subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            capture_output=True,
            text=True,
            timeout=4,
        )
    except Exception as exc:
        return {"ready": False, "detail": str(exc)}
    return {
        "ready": result.returncode == 0,
        "detail": result.stdout.strip() if result.returncode == 0 else (result.stderr.strip() or "docker daemon unavailable"),
    }


async def run_cmd(cmd: List[str], log_callback=None) -> tuple[bool, str]:
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(WORKSPACE),
        )
        output = []
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="replace")
            output.append(text)
            if log_callback:
                await log_callback(text)
        await proc.wait()
        return proc.returncode == 0, "".join(output)
    except Exception as e:
        return False, str(e)


async def start_wireshark(log_callback=None):
    if log_callback:
        await log_callback("// starting wireshark container...\n")
    success, output = await run_cmd(
        ["docker", "compose", "-f", str(WIRESHARK_COMPOSE), "up", "-d"], log_callback
    )
    if log_callback:
        await log_callback(f"// wireshark: {'started' if success else 'failed'}\n")
    return success


def get_wireshark_status() -> Dict:
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=dc-wireshark", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.stdout.strip():
            info = json.loads(result.stdout.strip().split("\n")[0])
            return {"status": "running", "url": "https://localhost:3001/"}
        return {"status": "stopped", "url": "https://localhost:3001/"}
    except Exception:
        return {"status": "unknown", "url": "https://localhost:3001/"}
