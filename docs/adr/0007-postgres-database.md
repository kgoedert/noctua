# ADR-0007: PostgreSQL as the only database

## Status

Approved

## Date

2026-07-30

## Context

The project needs persistent storage for regular relational application data as well as vector embeddings used by its AI features. A database strategy is therefore required that can support both use cases.

At the current scale of the project, introducing and operating multiple database technologies would add complexity that is not required by the application's functional requirements.

## Decision

Use PostgreSQL as the project's only database, with the pgvector extension for vector storage and similarity search.

## Alternatives Considered

### Separate relational and vector databases

#### Positives

Each database can be optimized for its specific workload.
Provides experience with dedicated vector database technology.
Allows independent scaling.

#### Negatives

Additional infrastructure.
More operational complexity.
More complicated local development.
Additional backup and monitoring requirements.
Data and application workflows may need to coordinate across two systems.
Not currently required by the project's scale.

## Consequences

#### Positive

One database to deploy, monitor and back up.
Simplified local development.
Relational and vector data can participate in the same application ecosystem.
Avoids introducing additional infrastructure before it is necessary.


#### Negative

Vector workloads share resources with relational workloads.
A dedicated vector database may provide better performance or scalability for larger workloads.
The architecture becomes dependent on PostgreSQL and pgvector for both use cases.