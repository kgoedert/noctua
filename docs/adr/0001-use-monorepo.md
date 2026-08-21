# ADR-0001: Use a Monorepo

## Status

Accepted

## Date

2026-07-28

## Context

The project contains three main applications:

- Angular frontend
- Spring Boot backend
- Python AI services

A repository strategy is required to organize the source code and support efficient local development, versioning, and collaboration.
The applications are expected to evolve together and are not intended to be released independently.

## Decision

Use a monorepo containing all applications.

```text
project-root/
   |- frontend/
   |- backend/
   |- ai/
   |- infrastructure/
```

Each application keeps its own build system.


## Alternatives Considered

### Multiple repositories

Pros

- Better isolation
- Independent release cycles

Cons

- Harder onboarding
- Harder local development
- Harder to keep versions synchronized

### Git Submodules

Pros

- Independent repositories

Cons

- Difficult workflow
- Steeper learning curve
- Extra Git complexity

## Consequences

Positive

- Easier cloning
- Easier CI
- Easier Docker Compose
- Easier debugging

Negative

- Larger repository
- Slightly longer clone time