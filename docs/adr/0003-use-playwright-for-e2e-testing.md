# ADR-0003: Use Playwright for E2E testing

## Status

Accepted

## Date

2026-07-29

## Context

The project requires automated end-to-end tests to validate user workflows across the frontend and backend. The chosen framework should be reliable, easy to maintain, and support modern browsers.

## Decision

Use Playwright as the end-to-end testing framework.

Playwright provides reliable browser automation, automatic waiting mechanisms, parallel execution, and support for Chromium, Firefox, and WebKit. It integrates well with modern web applications and CI environments.

## Alternatives Considered

### Selenium

#### Positives

Well stablished tool, open source and actively maintained

#### Negatives

Handling timeouts and waiting for javascript events to occur has to be handled by the developer.
Parallel test execution is hard

