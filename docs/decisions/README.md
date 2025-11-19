# Architecture Decision Records (ADRs)

This directory contains records of architectural decisions made in the Z-Beam Generator system.

## Purpose

ADRs document **WHY** architectural choices were made, helping AI assistants understand:
- The problem context that led to the decision
- What alternatives were considered
- The consequences and trade-offs
- How to work within the chosen architecture

## Format

Each ADR follows this structure:
- **Status**: Accepted | Superseded | Deprecated
- **Context**: What problem are we solving?
- **Decision**: What did we choose?
- **Consequences**: What does this mean for developers?
- **Alternatives Considered**: What did we reject and why?

## Index

- [ADR-001: Dual Voice Enforcement Architecture](./ADR-001-dual-voice-enforcement.md)
- [ADR-002: Fail-Fast vs Runtime Recovery](./ADR-002-fail-fast-vs-runtime-recovery.md)
- [ADR-003: Exploration Rate and Reproducibility](./ADR-003-exploration-rate-reproducibility.md)
- [ADR-004: Content Instructions Location](./ADR-004-content-instructions-location.md)

## When to Create an ADR

Create an ADR when:
1. Making a significant architectural choice
2. Resolving a conflict between two approaches
3. Learning from a failure that required major changes
4. Establishing a pattern that others must follow

## When to Update an ADR

Update when:
- The decision is superseded by a new approach
- Consequences become clearer through experience
- New alternatives are discovered
- The context changes significantly
