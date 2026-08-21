# ADR-0004: Use Flyway for database migrations

## Status

Approved

## Date

2026-07-29

## Context

The database schema needs to evolve alongside the application code. Managing SQL scripts manually can make it difficult to determine which migrations have already been applied and which need to be executed to keep development environments consistent with the application version.

## Decision

Use Flyway to manage database schema migrations. Flyway will manage the ordering and execution of versioned SQL migration scripts and integrate with the Spring Boot application lifecycle.

## Alternatives Considered

#### Liquibase

Pros

Mature migration framework
Supports SQL, XML, YAML and JSON
Supports rollback definitions

Cons

More features and configuration than required for this project
The project prefers SQL-based migrations

#### Manual SQL in several files

### Positives

- Less setup needed.
- Easier, simpler copy paste
- Easy to maintain when the database is very small and there are not many developers

### Negatives

- When the database starts to grow becomes hard to maintain.
- When the project grows it becomes hard for developers to know what they need to execute to keep their development environments up to date.

## Consequences

Positive

Database changes are versioned alongside application code.
Developers can bring their database up to date automatically.
Migration order is managed by Flyway.
Migration history is recorded.
Schema changes can be reviewed through normal code review.

Negative

Previously applied migrations should not be modified.
Fixing an incorrect migration generally requires creating a new migration.
Developers need to understand Flyway's migration conventions.