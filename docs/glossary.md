# Glossary

Short definitions for terms used by the workbench.

## Franca

The interface definition language used by the CommonAPI toolchain. Franca describes service contracts independently from a transport binding.

## FIDL

A Franca interface file, usually ending in `.fidl`. It defines packages, interfaces, versions, methods, broadcasts/events, structs, arrays, and enumerations.

## FDEPL

A Franca deployment file, usually ending in `.fdepl`. In this workbench it assigns SOME/IP deployment details such as service IDs, instance IDs, method IDs, event IDs, and event groups.

## CommonAPI

A COVESA middleware abstraction and code generation stack. The workbench uses CommonAPI generators where available, but currently uses generated raw-vsomeip nodes for runnable transport simulation when complete Core proxy/stub output is unavailable.

## vsomeip

The COVESA SOME/IP runtime used by generated service/client nodes. It handles SOME/IP messaging, routing, and SOME/IP-SD participation.

## SOME/IP

Scalable service-Oriented MiddlewarE over IP. It is the automotive service communication protocol simulated by this workbench.

## SOME/IP-SD

SOME/IP Service Discovery. It advertises and discovers service instances, events, and subscriptions over the run network.

## Service ID

A SOME/IP identifier for an interface/service. It is configured in `.fdepl` as `SomeIpServiceID`.

## Instance ID

A SOME/IP identifier for a concrete instance of a service. It is configured in `.fdepl` as `SomeIpInstanceID`.

## Method ID

A SOME/IP identifier for a method on a service. It is configured in `.fdepl` as `SomeIpMethodID`.

## Event ID

A SOME/IP identifier for an event or broadcast. It is configured in `.fdepl` as `SomeIpEventID`.

## Event Group

A SOME/IP-SD subscription grouping for events. It is configured in `.fdepl` as `SomeIpEventGroups`.

## Project

A manifest-backed workbench directory under `projects/<project-id>/`. It owns editable source, topology, nodes, and scenarios.

## Scenario

A saved YAML file that describes a simulation flow, such as node start order, waits, calls, assertions, and capture marks.

## Run

One execution of a scenario. A run has its own rendered Docker Compose file, per-node config, logs, metadata, and captures under `runs/<run-id>/`.

## Capture

A saved packet capture, usually `.pcapng`, produced during a run for Wireshark inspection.

## Runtime Kind

The strategy used to run a project. The current v1 runtime kind is `generated-vsomeip`, which builds generated transport-level service/client nodes from project Franca and deployment source.

## `transport-only`

A generator status meaning the current output is not a complete generated CommonAPI proxy/stub node project. It can still provide useful transport artifacts, generated raw-vsomeip nodes, interface metadata, and packet-capture-capable runs.
