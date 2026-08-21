# ADR-0008: Python for the AI related services

## Status

Approved

## Date

2026-07-30

## Context

The primary goal of the project is to learn how AI capabilities can be integrated into a real application. The project therefore requires access to the libraries, frameworks, models, and tooling commonly used for AI development.

## Decision

Use Python for the AI-related services. Python provides access to a broad ecosystem of AI and machine-learning libraries and is widely adopted for AI development. Using Python also provides an opportunity to gain practical experience with the ecosystem that is the primary focus of this project.

## Alternatives Considered

### Use java

#### Positives

Significant existing experience with the Java ecosystem would allow faster initial development.
Using Java would reduce the opportunity to gain practical experience with the Python-based AI ecosystem, which is one of the project's learning objectives.

#### Negatives

The ecosystem of AI/ML libraries and frameworks available in Java is smaller than Python's.

## Consequences

### Positive

Access to a broad ecosystem of AI/ML libraries and frameworks.
Gain practical experience with Python-based AI tooling.
Allows the AI services to use libraries that may not have equivalent Java implementations.

### Negative

Introduces a second programming language into the project.
Requires Python-specific dependency and environment management.
Requires communication between the Java backend and Python services.