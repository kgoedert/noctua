# ADR-0006: Use Angular as the frontend framework

## Status

Approved 

## Date

2026-07-29

## Context

The project requires a web frontend through which users can interact with the application's AI capabilities.

The primary goal of the project is to learn and experiment with AI rather than to learn a new frontend framework. The frontend should therefore allow the project to move quickly without introducing unnecessary learning overhead.


## Decision

Use Angular as the frontend framework.

Angular was selected because the project prioritizes AI experimentation, and the existing experience with Angular allows frontend development to proceed without significant framework-learning overhead.

## Alternatives Considered

### Use React

#### Postives

Large ecosystem
Widely adopted
Opportunity to develop React expertise

#### Negatives

Requires additional learning effort
Would shift some project focus away from AI experimentation

### Vue

#### Postives

Relatively low learning curve
Mature ecosystem

#### Negatives

Would still introduce another framework to learn
Doesn't provide a significant benefit for the current project goals

## Consequences

#### Postives


Faster frontend development due to existing Angular experience.
Allows the project to focus on AI-related functionality.
Avoids introducing another major learning objective.

#### Negatives

Does not provide an opportunity to develop React expertise.
The project remains dependent on Angular's ecosystem and conventions.