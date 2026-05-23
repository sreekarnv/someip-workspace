# Glossary

## Franca

The interface definition language used by the CommonAPI toolchain.

## FIDL

A Franca IDL file. It defines packages, interfaces, methods, broadcasts/events, structs, and enumerations. In this workspace these files live under `projects/<project-id>/franca/`.

## FDEPL

A Franca deployment file. It maps the Franca interface to SOME/IP deployment values such as service ID, instance ID, method IDs, event IDs, event groups, and ports.

## CommonAPI

A COVESA middleware abstraction and generator stack. It generates proxy/stub style application glue from Franca source and can bind that interface to SOME/IP.

## vsomeip

The COVESA SOME/IP runtime used for transport, routing, and SOME/IP Service Discovery behavior.

## SOME/IP

Scalable service-Oriented MiddlewarE over IP. It is used for service method calls, events, and field-like communication over IP networks.

## SOME/IP-SD

SOME/IP Service Discovery. It lets clients find offered services, subscribe to event groups, and observe service availability.

## Service ID

A SOME/IP identifier for a service. In this workspace it should be declared in the `.fdepl` file.

## Instance ID

A SOME/IP identifier for a specific service instance. It is also declared in deployment source.

## Method ID

A SOME/IP identifier for an interface method.

## Event ID

A SOME/IP identifier for a broadcast or event.

## Event Group

A SOME/IP-SD subscription group that contains one or more events.

## Node

A simulated participant in a project topology. Nodes are listed in `project.yaml` and usually act as service or client applications.

## Scenario

A saved YAML file that describes a simulation flow, such as node start order, waits, calls, assertions, and capture marks.

## Run

One execution of a scenario. A run has its own rendered Docker Compose file, per-node config, logs, metadata, and captures under `runs/<run-id>/`.

## Capture

A saved packet capture, usually `.pcapng`, produced during a run for Wireshark inspection.

## `source_example`

A manifest field that points at a checked-in C++ sample implementation under `examples/`. `null` means the project uses generated project nodes instead of fallback implementation code.

## `transport-only`

A generator status meaning the current output is not a complete generated CommonAPI proxy/stub node project. It can still provide useful transport artifacts, generated raw-vsomeip nodes, interface metadata, and packet-capture-capable runs.
