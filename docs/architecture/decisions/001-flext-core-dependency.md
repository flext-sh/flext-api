# 001. Mandatory FLEXT-Core Dependency

<!-- TOC START -->

- [Status](#status)
- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
  - [Positive](#positive)
  - [Negative](#negative)
  - [Risks](#risks)
- [Alternatives Considered](#alternatives-considered)
  - [Option 1: Standalone HTTP Library](#option-1-standalone-http-library)
  - [Option 2: Optional flext-core Integration](#option-2-optional-flext-core-integration)
  - [Option 3: Minimal flext-core Integration](#option-3-minimal-flext-core-integration)
- [Implementation Plan](#implementation-plan)
  - [Phase 1: Core Integration (Week 1-2)](#phase-1-core-integration-week-1-2)
  - [Phase 2: Ecosystem Migration (Week 3-8)](#phase-2-ecosystem-migration-week-3-8)
  - [Phase 3: Enforcement (Week 9-12)](#phase-3-enforcement-week-9-12)
- [References](#references)

<!-- TOC END -->

Date: 2025-01-01

## Status

Accepted

## Context

FLEXT-API is designed as part of the FLEXT enterprise ecosystem, which provides shared patterns and utilities across multiple projects. The decision needed to be made about whether FLEXT-API should depend on flext-core and integrate with the broader ecosystem patterns.

Key considerations:

- FLEXT ecosystem has 30+ projects that need consistent patterns
- HTTP operations are fundamental to enterprise applications
- Error handling, logging, and service patterns need to be standardized
- Dependency management and maintenance overhead
- Backward compatibility and ecosystem evolution

## Decision

FLEXT-API will have a **mandatory dependency on flext-core** and will fully integrate with FLEXT ecosystem patterns. All HTTP operations in the FLEXT ecosystem MUST use FLEXT-API exclusively - NO direct httpx imports allowed in ecosystem projects.

## Consequences

### Positive

- **Consistent Patterns**: All FLEXT projects use the same error handling, logging, and service patterns
- **Shared Infrastructure**: Common HTTP client, configuration, and monitoring across projects
- **Ecosystem Cohesion**: Seamless integration between FLEXT projects using consistent APIs
- **Reduced Duplication**: HTTP client code doesn't need to be rewritten in each project
- **Centralized Maintenance**: HTTP functionality improvements benefit all ecosystem projects
- **Quality Assurance**: Enterprise-grade HTTP operations with comprehensive testing

### Negative

- **Dependency Coupling**: FLEXT-API cannot evolve independently of flext-core
- **Version Coordination**: Ecosystem projects must coordinate flext-core and flext-api versions
- **Migration Complexity**: Existing projects must migrate to use FLEXT-API instead of direct HTTP libraries
- **Learning Curve**: Developers must learn FLEXT patterns in addition to HTTP concepts

### Risks

- **Breaking Changes**: Changes to flext-core could break FLEXT-API and downstream projects
- **Coordination Overhead**: Release coordination across 30+ projects becomes more complex
- **Adoption Resistance**: Teams may resist migrating from familiar HTTP libraries

## Alternatives Considered

### Option 1: Standalone HTTP Library

- **Description**: FLEXT-API as independent library without flext-core dependency
- **Pros**: Independent evolution, simpler dependencies, easier adoption
- **Cons**: Pattern inconsistency across ecosystem, duplication of core functionality
- **Rejected**: Violates ecosystem standardization goals

### Option 2: Optional flext-core Integration

- **Description**: flext-core as optional dependency with fallback implementations
- **Pros**: Gradual adoption, reduced coupling, flexible integration
- **Cons**: Inconsistent behavior, maintenance burden, testing complexity
- **Rejected**: Would lead to ecosystem fragmentation

### Option 3: Minimal flext-core Integration

- **Description**: Only use core utilities, implement custom patterns for HTTP operations
- **Pros**: Some consistency benefits, reduced coupling
- **Cons**: Still requires coordination, partial benefits
- **Rejected**: Doesn't achieve full ecosystem integration

## Implementation Plan

### Phase 1: Core Integration (Week 1-2)

- [x] Add flext-core dependency to pyproject.toml
- [x] Update imports to use FlextResult, FlextService, etc.
- [x] Replace custom error handling with railway pattern
- [x] Integrate FlextLogger for structured logging

### Phase 2: Ecosystem Migration (Week 3-8)

- [x] Update all internal HTTP operations to use FLEXT-API
- [ ] Create migration guide for ecosystem projects
- [ ] Provide migration utilities and examples
- [ ] Update documentation and examples

### Phase 3: Enforcement (Week 9-12)

- [ ] Add linting rules to prevent direct httpx imports
- [ ] Implement CI/CD checks for ecosystem compliance
- [ ] Create monitoring and reporting for adoption status
- [ ] Establish support channels for migration assistance

## References

- [FLEXT-Core Documentation](https://github.com/organization/flext/tree/main/flext-core/)
- [Railway Pattern Implementation](002-railway-pattern.md)
- [Ecosystem Architecture Overview](../../overview.md)
- GitHub Issue: #123 - Ecosystem HTTP Standardization
