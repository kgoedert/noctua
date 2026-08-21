# ADR-0002: Use of Docker only for infrastructure services

## Status

Accepted

## Date

2026-07-29

## Context

The project requires several runtime components during development, including a relational database and application runtimes for Java, Node.js, and Python.

Database installation, configuration, and extension management are more difficult to keep consistent across developers' machines.

A development strategy is needed that minimizes onboarding effort while providing a fast edit-build-debug cycle.


## Decision

Run infrastructure services with Docker Compose.
Run the Spring Boot application directly from the IDE or command line.
Run the Angular application locally using Node.js managed with nvm.
Run the Python services in a virtual environment using venv.

## Alternatives Considered

### Run everything on docker.

Pros

Simple setup for a developer

Cons

Longer edit-build-debug cycle.
Additional filesystem synchronization overhead.
More difficult IDE debugging.
Needs more memory

### Using Dev Containers

Pros

Simple setup for a developer

Cons

Development is slower
Higher CPU and memory consumption during development.

### Install everything locally outside any docker infrastructure.

Pros

Better integration with IDEs
Easier debugging

Cons

The setup specially of plugins in a database is not so simple.


## Consequences

### Positive

Consistent database configuration across all developers.
Fast application startup and debugging.
Native IDE integration.
Infrastructure can be recreated with a single Docker Compose command.

### Negative

Developers must install Java, Node.js, and Python locally.
Local development environments may differ slightly between operating systems.
The project depends on both Docker and native tooling.

