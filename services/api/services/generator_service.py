import asyncio
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable, Optional

from services import franca_service, project_service

WORKSPACE = Path(__file__).resolve().parent.parent.parent.parent
GENERATOR_DIR = WORKSPACE / "tools" / "generators"


async def generate_project(
    project_id: str, log_callback: Optional[Callable] = None
) -> bool:
    validation = await franca_service.validate_project(project_id)
    if not validation["valid"]:
        if log_callback:
            await log_callback("Validation failed; generation stopped\n")
        return False

    root = project_service._project_dir(project_id)
    manifest = project_service.load_manifest(project_id)
    gen_dir = root / "generated" / "commonapi"
    gen_dir.mkdir(parents=True, exist_ok=True)
    core_gen = GENERATOR_DIR / "commonapi-core-generator-linux-x86_64"
    someip_gen = GENERATOR_DIR / "commonapi-someip-generator-linux-x86_64"

    generator_warnings = []
    franca_dir = root / "franca"
    core_can_run = core_gen.exists() and not _same_file_hash(core_gen, someip_gen)
    if not core_gen.exists():
        generator_warnings.append(f"Core generator missing at {core_gen.name}.")
        if log_callback:
            await log_callback(f"WARNING: {generator_warnings[-1]}\n")
    elif not core_can_run:
        generator_warnings.append(
            "Configured Core generator is identical to the SOME/IP generator; skipping Core .fidl generation. Reinstall or fix the CommonAPI Core toolchain to produce full proxy/stub headers."
        )
        if log_callback:
            await log_callback(f"WARNING: {generator_warnings[-1]}\n")

    if core_can_run:
        for relative in manifest.get("franca", {}).get("fidl", []):
            if not await _run_generator(
                [
                    str(core_gen),
                    "-d",
                    str(gen_dir),
                    "-sp",
                    str(franca_dir),
                    str(root / relative),
                ],
                root,
                log_callback,
            ):
                return False

    for relative in manifest.get("franca", {}).get("deployment", []):
        if not someip_gen.exists():
            if log_callback:
                await log_callback(f"SOME/IP generator missing: {someip_gen}\n")
            return False
        if not await _run_generator(
            [
                str(someip_gen),
                "-d",
                str(gen_dir),
                "-sp",
                str(franca_dir),
                str(root / relative),
            ],
            root,
            log_callback,
        ):
            return False

    _write_node_scaffolds(root, manifest)
    _write_generated_vsomeip_project(root, manifest)
    core_outputs = list(gen_dir.rglob("*Stub.hpp")) + list(
        gen_dir.rglob("*ProxyBase.hpp")
    )
    generated_status = "ready"
    if not core_outputs:
        generated_status = "transport-only"
        generator_warnings.append(
            "Core proxy/stub headers were not emitted; editable node templates, SOME/IP transport artifacts, and a raw-vsomeip runnable node project were produced."
        )
        if log_callback:
            await log_callback(f"WARNING: {generator_warnings[-1]}\n")
    project_service.update_metadata(
        project_id,
        generated={
            "status": generated_status,
            "generated_at": project_service.utc_now(),
            "directory": "generated/commonapi",
            "warnings": generator_warnings,
            "toolchain": {
                "core": core_gen.name,
                "someip": someip_gen.name,
            },
        },
    )
    if log_callback:
        await log_callback("Project generation completed\n")
    return True


def _same_file_hash(left: Path, right: Path) -> bool:
    if not left.exists() or not right.exists():
        return False
    return hashlib.sha256(left.read_bytes()).digest() == hashlib.sha256(right.read_bytes()).digest()


async def _run_generator(cmd, cwd: Path, log_callback) -> bool:
    if log_callback:
        await log_callback(f"Running: {' '.join(cmd)}\n")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(cwd),
    )
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        if log_callback:
            await log_callback(line.decode("utf-8", errors="replace"))
    await proc.wait()
    if proc.returncode and log_callback:
        await log_callback(f"Generator exited with {proc.returncode}\n")
    return proc.returncode == 0


def _write_node_scaffolds(root: Path, manifest: dict) -> None:
    index_path = root / "generated" / "interface-index.json"
    index = (
        json.loads(index_path.read_text())
        if index_path.exists()
        else {"interfaces": []}
    )
    first_interface = index.get("interfaces", [{}])[0]
    interface_name = ".".join(
        part
        for part in (first_interface.get("package"), first_interface.get("name"))
        if part
    )
    for node in manifest.get("nodes", []):
        src = root / "nodes" / node["id"] / "templates"
        src.mkdir(parents=True, exist_ok=True)
        node_kind = node.get("type", "client")
        readme = src / "README.md"
        if not readme.exists():
            readme.write_text(
                f"# {node['id']} {node_kind} template\n\n"
                f"Generated for `{interface_name or node.get('interface', 'unknown interface')}`.\n"
                "Place editable CommonAPI handler or client driver sources in `../src/`.\n"
                "Runnable sample-backed projects may build from `source_example`; source-only projects need generated node sources before build/run can succeed.\n"
            )



def _snake(value: str) -> str:
    value = re.sub(r"(?<!^)(?=[A-Z])", "_", value).replace("-", "_")
    value = re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_")
    return value.lower() or "project"


def _first_id(index: dict, key: str, default: str) -> str:
    deployments = index.get("deployments") or []
    ids = deployments[0].get("ids", {}) if deployments else {}
    values = ids.get(key) or []
    return values[0] if values else default


def _id_values(index: dict, key: str) -> list[str]:
    deployments = index.get("deployments") or []
    ids = deployments[0].get("ids", {}) if deployments else {}
    return list(ids.get(key) or [])


def _cpp_id(value: str) -> str:
    value = str(value).strip().rstrip(",")
    if value.lower().startswith("0x"):
        return value.lower()
    try:
        return f"0x{int(value, 10):04x}"
    except ValueError:
        return "0x0001"


def _cpp_array(values: list[str], default: str) -> str:
    values = values or [default]
    return ", ".join(_cpp_id(value) for value in values)


def _interface_version(root: Path, manifest: dict) -> tuple[int, int]:
    fidl_paths = manifest.get("franca", {}).get("fidl", [])
    if not fidl_paths:
        return 1, 0
    text = (root / fidl_paths[0]).read_text(errors="replace")
    match = re.search(r"version\s*\{\s*major\s+(\d+)\s+minor\s+(\d+)\s*\}", text, re.MULTILINE)
    if not match:
        return 1, 0
    return int(match.group(1)), int(match.group(2))


def _write_generated_vsomeip_project(root: Path, manifest: dict) -> None:
    index_path = root / "generated" / "interface-index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else {}
    interface = (index.get("interfaces") or [{}])[0]
    project_id = manifest["id"]
    prefix = _snake(project_id)
    service_binary = f"{prefix}_service"
    client_binary = f"{prefix}_client"
    service_id = _cpp_id(_first_id(index, "serviceId", "0x1001"))
    instance_id = _cpp_id(_first_id(index, "instanceId", "0x0001"))
    method_ids = _id_values(index, "methodId")
    event_ids = _id_values(index, "eventId")
    event_group_ids = _id_values(index, "eventGroupId")
    major, minor = _interface_version(root, manifest)
    method_names = interface.get("methods") or ["method"]
    event_names = interface.get("events") or []

    out = root / "generated" / "nodes" / "vsomeip"
    src = out / "src"
    src.mkdir(parents=True, exist_ok=True)
    (out / "CMakeLists.txt").write_text(_generated_cmake(project_id, service_binary, client_binary))
    (src / "service.cpp").write_text(
        _generated_service_cpp(
            project_id=project_id,
            service_id=service_id,
            instance_id=instance_id,
            method_ids=_cpp_array(method_ids, "0x0100"),
            method_count=max(len(method_ids), 1),
            event_ids=_cpp_array(event_ids, "0x8001"),
            event_count=len(event_ids),
            event_group_ids=_cpp_array(event_group_ids, "0x0001"),
            event_group_count=len(event_group_ids),
            major=major,
            minor=minor,
            method_names=method_names,
            event_names=event_names,
        )
    )
    (src / "client.cpp").write_text(
        _generated_client_cpp(
            project_id=project_id,
            service_id=service_id,
            instance_id=instance_id,
            method_ids=_cpp_array(method_ids, "0x0100"),
            method_count=max(len(method_ids), 1),
            event_ids=_cpp_array(event_ids, "0x8001"),
            event_count=len(event_ids),
            event_group_ids=_cpp_array(event_group_ids, "0x0001"),
            event_group_count=len(event_group_ids),
            major=major,
            minor=minor,
            method_names=method_names,
            event_names=event_names,
        )
    )
    (out / "README.md").write_text(
        f"# Generated raw-vsomeip nodes for {project_id}\n\n"
        "These files are derived from Franca/deployment source because the bundled CommonAPI Core generator does not currently emit complete proxy/stub headers.\n"
        "They provide runnable SOME/IP and SOME/IP-SD service/client binaries for Docker simulation and packet capture.\n"
    )
    project_service.update_metadata(
        project_id,
        generated_nodes={
            "status": "ready",
            "kind": "raw-vsomeip",
            "directory": "generated/nodes/vsomeip",
            "service_binary": service_binary,
            "client_binary": client_binary,
        },
    )


def _generated_cmake(project_id: str, service_binary: str, client_binary: str) -> str:
    return f"""cmake_minimum_required(VERSION 3.16)
project({project_id}_generated_vsomeip CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(WORKSPACE_ROOT "${{CMAKE_CURRENT_SOURCE_DIR}}")
get_filename_component(WORKSPACE_ROOT "${{WORKSPACE_ROOT}}" DIRECTORY)
get_filename_component(WORKSPACE_ROOT "${{WORKSPACE_ROOT}}" DIRECTORY)
get_filename_component(WORKSPACE_ROOT "${{WORKSPACE_ROOT}}" DIRECTORY)
get_filename_component(WORKSPACE_ROOT "${{WORKSPACE_ROOT}}" DIRECTORY)
get_filename_component(WORKSPACE_ROOT "${{WORKSPACE_ROOT}}" DIRECTORY)

set(VSOMEIP_INCLUDE "${{WORKSPACE_ROOT}}/libs/vsomeip/interface")
set(VSOMEIP_LIB "${{WORKSPACE_ROOT}}/build/vsomeip")

include_directories(${{VSOMEIP_INCLUDE}})
link_directories(${{VSOMEIP_LIB}})

add_executable({service_binary} src/service.cpp)
target_link_libraries({service_binary} vsomeip3 pthread)

add_executable({client_binary} src/client.cpp)
target_link_libraries({client_binary} vsomeip3 pthread)
"""


def _name_table(names: list[str], count: int) -> str:
    values = names[:count] or ["method"]
    if len(values) < count:
        values.extend(f"item_{index}" for index in range(len(values), count))
    return ", ".join(f'"{name}"' for name in values)


def _generated_service_cpp(**data: Any) -> str:
    return f"""// Generated by SOME/IP Workbench. Edit Franca/deployment source, not this file.
#include <vsomeip/vsomeip.hpp>

#include <atomic>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <memory>
#include <set>
#include <thread>
#include <vector>

namespace {{
constexpr vsomeip::service_t SERVICE_ID = {data['service_id']};
constexpr vsomeip::instance_t INSTANCE_ID = {data['instance_id']};
constexpr vsomeip::major_version_t MAJOR_VERSION = {data['major']};
constexpr vsomeip::minor_version_t MINOR_VERSION = {data['minor']};
constexpr vsomeip::method_t METHOD_IDS[] = {{{data['method_ids']}}};
constexpr const char *METHOD_NAMES[] = {{{_name_table(data['method_names'], data['method_count'])}}};
constexpr std::size_t METHOD_COUNT = {data['method_count']};
constexpr vsomeip::event_t EVENT_IDS[] = {{{data['event_ids']}}};
constexpr std::size_t EVENT_COUNT = {data['event_count']};
constexpr vsomeip::eventgroup_t EVENTGROUP_IDS[] = {{{data['event_group_ids']}}};
constexpr std::size_t EVENTGROUP_COUNT = {data['event_group_count']};

std::shared_ptr<vsomeip::application> app;
std::atomic_bool running{{true}};

std::shared_ptr<vsomeip::payload> payload(std::initializer_list<vsomeip::byte_t> bytes) {{
    return vsomeip::runtime::get()->create_payload(std::vector<vsomeip::byte_t>(bytes));
}}

void on_message(const std::shared_ptr<vsomeip::message> &request) {{
    auto response = vsomeip::runtime::get()->create_response(request);
    response->set_payload(payload({{0x01}}));
    app->send(response);
    std::cout << "{data['project_id']} service handled method 0x"
              << std::hex << std::setw(4) << std::setfill('0') << request->get_method()
              << std::dec << std::endl;
}}

void on_state(vsomeip::state_type_e state) {{
    if (state != vsomeip::state_type_e::ST_REGISTERED) {{
        return;
    }}
    std::set<vsomeip::eventgroup_t> groups;
    for (std::size_t index = 0; index < EVENTGROUP_COUNT; ++index) {{
        groups.insert(EVENTGROUP_IDS[index]);
    }}
    for (std::size_t index = 0; index < EVENT_COUNT; ++index) {{
        app->offer_event(SERVICE_ID, INSTANCE_ID, EVENT_IDS[index], groups, vsomeip::event_type_e::ET_EVENT, std::chrono::milliseconds::zero(), false, true, nullptr, vsomeip::reliability_type_e::RT_UNRELIABLE);
    }}
    app->offer_service(SERVICE_ID, INSTANCE_ID, MAJOR_VERSION, MINOR_VERSION);
    std::cout << "{data['project_id']} service offered SOME/IP service" << std::endl;
}}

void event_loop() {{
    while (running.load()) {{
        std::this_thread::sleep_for(std::chrono::seconds(2));
        for (std::size_t index = 0; index < EVENT_COUNT; ++index) {{
            app->notify(SERVICE_ID, INSTANCE_ID, EVENT_IDS[index], payload({{0x00, 0x15, 0x03, 0x01}}), true);
            std::cout << "{data['project_id']} service notified event 0x"
                      << std::hex << std::setw(4) << std::setfill('0') << EVENT_IDS[index]
                      << std::dec << std::endl;
        }}
    }}
}}

void stop(int) {{
    running.store(false);
    if (app) {{
        app->stop();
    }}
}}
}} // namespace

int main() {{
    std::signal(SIGINT, stop);
    std::signal(SIGTERM, stop);
    app = vsomeip::runtime::get()->create_application();
    app->init();
    app->register_state_handler(on_state);
    for (std::size_t index = 0; index < METHOD_COUNT; ++index) {{
        app->register_message_handler(SERVICE_ID, INSTANCE_ID, METHOD_IDS[index], on_message);
        std::cout << "{data['project_id']} service registered " << METHOD_NAMES[index]
                  << " as method 0x" << std::hex << METHOD_IDS[index] << std::dec << std::endl;
    }}
    std::thread notifier(event_loop);
    app->start();
    running.store(false);
    if (notifier.joinable()) {{
        notifier.join();
    }}
    return 0;
}}
"""


def _generated_client_cpp(**data: Any) -> str:
    return f"""// Generated by SOME/IP Workbench. Edit Franca/deployment source, not this file.
#include <vsomeip/vsomeip.hpp>

#include <atomic>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <memory>
#include <set>
#include <thread>
#include <vector>

namespace {{
constexpr vsomeip::service_t SERVICE_ID = {data['service_id']};
constexpr vsomeip::instance_t INSTANCE_ID = {data['instance_id']};
constexpr vsomeip::major_version_t MAJOR_VERSION = {data['major']};
constexpr vsomeip::minor_version_t MINOR_VERSION = {data['minor']};
constexpr vsomeip::method_t METHOD_IDS[] = {{{data['method_ids']}}};
constexpr const char *METHOD_NAMES[] = {{{_name_table(data['method_names'], data['method_count'])}}};
constexpr std::size_t METHOD_COUNT = {data['method_count']};
constexpr vsomeip::event_t EVENT_IDS[] = {{{data['event_ids']}}};
constexpr std::size_t EVENT_COUNT = {data['event_count']};
constexpr vsomeip::eventgroup_t EVENTGROUP_IDS[] = {{{data['event_group_ids']}}};
constexpr std::size_t EVENTGROUP_COUNT = {data['event_group_count']};

std::shared_ptr<vsomeip::application> app;
std::atomic_bool running{{true}};
std::atomic_bool available{{false}};

std::shared_ptr<vsomeip::payload> payload(std::initializer_list<vsomeip::byte_t> bytes) {{
    return vsomeip::runtime::get()->create_payload(std::vector<vsomeip::byte_t>(bytes));
}}

void send_request(vsomeip::method_t method, const char *name) {{
    auto request = vsomeip::runtime::get()->create_request(false);
    request->set_service(SERVICE_ID);
    request->set_instance(INSTANCE_ID);
    request->set_method(method);
    request->set_interface_version(MAJOR_VERSION);
    request->set_payload(payload({{0x00, 0x15, 0x03, 0x01}}));
    app->send(request);
    std::cout << "{data['project_id']} client sent " << name
              << " method 0x" << std::hex << std::setw(4) << std::setfill('0') << method
              << std::dec << std::endl;
}}

void on_message(const std::shared_ptr<vsomeip::message> &message) {{
    std::cout << "{data['project_id']} client received message method/event 0x"
              << std::hex << std::setw(4) << std::setfill('0') << message->get_method()
              << " type 0x" << std::setw(2) << static_cast<int>(message->get_message_type())
              << std::dec << std::endl;
}}

void on_availability(vsomeip::service_t, vsomeip::instance_t, bool is_available) {{
    available.store(is_available);
    std::cout << "{data['project_id']} client service availability "
              << (is_available ? "available" : "unavailable") << std::endl;
    if (!is_available) {{
        return;
    }}
    std::set<vsomeip::eventgroup_t> groups;
    for (std::size_t index = 0; index < EVENTGROUP_COUNT; ++index) {{
        groups.insert(EVENTGROUP_IDS[index]);
    }}
    for (std::size_t index = 0; index < EVENT_COUNT; ++index) {{
        app->request_event(SERVICE_ID, INSTANCE_ID, EVENT_IDS[index], groups, vsomeip::event_type_e::ET_EVENT, vsomeip::reliability_type_e::RT_UNRELIABLE);
    }}
    for (std::size_t index = 0; index < EVENTGROUP_COUNT; ++index) {{
        app->subscribe(SERVICE_ID, INSTANCE_ID, EVENTGROUP_IDS[index], MAJOR_VERSION);
    }}
}}

void on_state(vsomeip::state_type_e state) {{
    if (state != vsomeip::state_type_e::ST_REGISTERED) {{
        return;
    }}
    app->request_service(SERVICE_ID, INSTANCE_ID, MAJOR_VERSION, MINOR_VERSION);
    std::cout << "{data['project_id']} client requested SOME/IP service" << std::endl;
}}

void request_loop() {{
    while (running.load()) {{
        if (available.load()) {{
            for (std::size_t index = 0; index < METHOD_COUNT; ++index) {{
                send_request(METHOD_IDS[index], METHOD_NAMES[index]);
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
            }}
        }}
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }}
}}

void stop(int) {{
    running.store(false);
    if (app) {{
        app->stop();
    }}
}}
}} // namespace

int main() {{
    std::signal(SIGINT, stop);
    std::signal(SIGTERM, stop);
    app = vsomeip::runtime::get()->create_application();
    app->init();
    app->register_state_handler(on_state);
    app->register_availability_handler(SERVICE_ID, INSTANCE_ID, on_availability, MAJOR_VERSION, MINOR_VERSION);
    for (std::size_t index = 0; index < METHOD_COUNT; ++index) {{
        app->register_message_handler(SERVICE_ID, INSTANCE_ID, METHOD_IDS[index], on_message);
    }}
    for (std::size_t index = 0; index < EVENT_COUNT; ++index) {{
        app->register_message_handler(SERVICE_ID, INSTANCE_ID, EVENT_IDS[index], on_message);
    }}
    std::thread requests(request_loop);
    app->start();
    running.store(false);
    if (requests.joinable()) {{
        requests.join();
    }}
    return 0;
}}
"""
