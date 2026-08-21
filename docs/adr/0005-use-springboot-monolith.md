# ADR-0005: Use a Spring Boot Modular Monolith

## Status

Approved

## Date

2026-07-29

## Context

The application is intended as a portfolio project that may grow over time, but does not initially require independently deployable services.

The primary goal of the project is to learn and experiment with AI by applying AI concepts to a real application, rather than to explore distributed Java application architectures.

Introducing independently deployable services would add operational complexity without providing a significant benefit at the current scale.

## Decision

Modules should communicate through well-defined interfaces and should avoid directly accessing the internal implementation details of other modules.

This decision can be revisited if the system develops requirements for independent deployment, scaling, or team ownership of individual modules.


### Consequences

#### Positive

Simpler development and debugging
Clear module boundaries can reduce the effort required to extract a module into an independent service if that becomes necessary.Simpler deployment

### Negative

Requires discipline to maintain module boundaries
The separation of concerns is not as strong as with microsservices

## Alternatives Considered

### Microservices from day one

#### Positives

Strong separation of concerns.
Independent deployment and scaling can be valuable when different parts of the system have substantially different availability, scaling, or release requirements.

#### Negatives

For the current project, independently deployable services would introduce additional operational complexity in areas such as service communication, deployment, monitoring, testing, and local development.
All modules share the same deployment and runtime resources.
A failure or resource issue in one module can potentially affect the entire application.
