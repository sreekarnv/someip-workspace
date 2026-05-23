---
name: someip-runtime
description: Use when working on Franca FIDL, deployment FDEPL, CommonAPI generation, raw-vsomeip nodes, Docker simulations, SOME/IP-SD, Wireshark captures, or runtime debugging in this workbench.
license: Complete terms in LICENSE.txt
---

This skill keeps SOME/IP work grounded in the actual Franca, CommonAPI, and vsomeip boundaries used by this repository.

## Source Boundaries

- Franca `.fidl` files are authored interface source. They define packages, interfaces, methods, broadcasts, attributes, structs, enums, arrays, maps, and constants.
- Franca deployment `.fdepl` files are authored deployment source. For SOME/IP they own service, instance, method, event, eventgroup, reliability, and port mapping values.
- CommonAPI Core generation is the `.fidl` to proxy/stub-facing C++ path.
- CommonAPI SOME/IP generation is the `.fdepl` to SOME/IP binding/deployment path. The SOME/IP generator validates and consumes deployment files, not plain `.fidl` files.
- vsomeip owns SOME/IP transport, routing, Service Discovery, service offers, service requests, event offers, event requests, subscriptions, notifications, message handlers, and JSON runtime configuration.
- In this workbench, generated raw-vsomeip nodes are the runnable v1 simulation path. Do not describe them as complete CommonAPI proxy/stub implementations.

## Workbench Model

- Editable source lives under `projects/<project-id>/`: `project.yaml`, `franca/*.fidl`, `franca/*.fdepl`, and `scenarios/*.yaml`.
- Validation reads manifest-listed FIDL/FDEPL files and writes derived metadata such as `generated/interface-index.json`; validation does not create missing source files.
- Generation may produce CommonAPI/SOME-IP artifacts and a generated raw-vsomeip node project under `projects/<project-id>/generated/nodes/vsomeip/`.
- Build compiles generated raw-vsomeip nodes into project artifacts used by Docker.
- Run rendering writes Docker Compose, per-node `vsomeip.json`, logs, and captures under `runs/<run-id>/`.

## Franca And Deployment Facts

- Use `Boolean`, not `Bool`.
- `state` is a Franca grammar keyword; avoid it as a field or argument name.
- `fireAndForget` methods still use a method body block.
- `.fdepl` commonly owns `SomeIpServiceID`, `SomeIpMethodID`, `SomeIpEventID`, `SomeIpEventGroups`, `InstanceId`, `SomeIpInstanceID`, `SomeIpReliableUnicastPort`, and `SomeIpUnreliableUnicastPort`.
- Keep SOME/IP service, instance, method, event, eventgroup, and port values unique within a project topology.
- Keep application names unique in `project.yaml`; they become vsomeip runtime identities through `VSOMEIP_APPLICATION_NAME`.

## Runtime Debugging Order

When diagnosing validation, build, run, or capture problems, check in this order:

1. `project.yaml` Franca paths and node application names.
2. Existence and syntax of manifest-listed `.fidl` and `.fdepl` files.
3. Validation diagnostics and `generated/interface-index.json`.
4. Generator job logs and whether output is marked `transport-only`.
5. Generated raw-vsomeip node project and `CMakeLists.txt`.
6. Built service/client binaries.
7. Rendered `runs/<run-id>/configs/*.json` vsomeip configuration.
8. Container environment variables: `VSOMEIP_CONFIGURATION` and `VSOMEIP_APPLICATION_NAME`.
9. Run logs, node lifecycle events, and run metadata.
10. Capture artifacts and Wireshark evidence for SOME/IP and SOME/IP-SD packets.

## Implementation Guidance

- Prefer fixing source files and manifest metadata over patching derived generated output.
- If a complete CommonAPI Core proxy/stub path is unavailable, keep the limitation visible and use generated raw-vsomeip nodes for runnable transport simulation.
- For service behavior, remember the vsomeip lifecycle: create application, initialize, register handlers, offer service/events, start processing.
- For client behavior, request service, observe availability, create/send request messages, request events, subscribe to eventgroups, and handle responses or notifications.
- Treat Wireshark as the deep packet inspection tool; the workbench should surface capture availability, packet summaries, and useful filters.
