# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) that document important architectural decisions made for the FLEXT-API project.

## What are ADRs

Architecture Decision Records (ADRs) are documents that capture important architectural decisions along with their context and consequences.

## ADR Template

```markdown
# [Number]. [Title]

Date: [YYYY-MM-DD]

## Status

[Proposed | Accepted | Rejected | Deprecated | Superseded by [ADR-XXXX]]

## Context

[Describe the context and forces at play. What problem are we trying to solve? What constraints are we under?]

## Decision

[What decision was made? What option was chosen?]

## Consequences

[What are the positive and negative consequences of this decision?]

### Positive

### Negative

### Risks

## Alternatives Considered

[What other options were considered? Why were they not chosen?]

## References

[object references to external documents, issues, or discussions]
```

## Current ADRs

| ADR                                     | Title                             | Status   | Date       |
| --------------------------------------- | --------------------------------- | -------- | ---------- | --------------------------- |
| [ADR-001](001-flext-core-dependency.md) | Mandatory FLEXT-Core Dependency   | Accepted | 2025-01-01 |
| [ADR-002](002-railway-pattern.md)       | Railway-Oriented Error Handling   | Accepted | 2025-01-01 |
| [ADR-003](003-protocol-abstraction.md)  | Protocol Plugin Architecture      | Accepted | 2025-01-01 |
| ADR-004                                 | Pydantic v2 Adoption              | Accepted | 2025-01-15 | _Documentation coming soon_ |
| ADR-005                                 | HTTPX as HTTP Client              | Accepted | 2025-01-15 | _Documentation coming soon_ |
| ADR-006                                 | Clean Architecture Implementation | Accepted | 2025-01-20 | _Documentation coming soon_ |

## ADR Workflow

### Creating a New ADR

1. **Identify Decision**: Recognize when an architectural decision needs to be made
2. **Draft ADR**: Create a new ADR document following the template
3. **Review**: Have the ADR reviewed by team members
4. **Accept/Reject**: Update status based on consensus
5. **Implement**: Implement the accepted decision

### ADR Status Definitions

- **Proposed**: Initial draft, under discussion
- **Accepted**: Decision made and accepted by team
- **Rejected**: Decision considered but not accepted
- **Deprecated**: Decision no longer relevant or has been changed
- **Superseded**: Replaced by a newer decision (reference new ADR)

## Tools and Automation

### ADR Generation Script

```bash
# Generate new ADR
python docs-maintenance/scripts/create_adr.py "New Feature Decision"

# List all ADRs
python docs-maintenance/scripts/list_adrs.py

# Search ADRs
python docs-maintenance/scripts/search_adrs.py "keyword"
```

### Integration with Development

- ADRs are stored in version control alongside code
- CI/CD pipeline validates ADR format and completeness
- ADR references included in commit messages and PRs
- ADR status tracked in project management tools

## Best Practices

### Writing Effective ADRs

1. **Be Specific**: Clearly state what decision was made and why
2. **Include Context**: Explain the problem being solved
3. **Document Alternatives**: Show what other options were considered
4. **List Consequences**: Be honest about trade-offs and risks
5. **Keep Current**: Update status as decisions evolve

### When to Write an ADR

- Choosing between two or more architectural approaches
- Making significant changes to existing architecture
- Adopting new technologies or frameworks
- Changing fundamental design patterns
- Resolving technical debt or architectural issues

### ADR Maintenance

- Review ADRs periodically (quarterly)
- Update status when decisions are superseded
- Archive deprecated ADRs to separate directory
- Cross-reference related ADRs
- Update ADRs when implementation reveals new information

## Examples from Other Projects

### Successful ADR Implementations

- **Spotify**: Uses ADRs for microservices architecture decisions
- **GOV.UK**: Documents all major technical decisions
- **ThoughtWorks**: Open source ADR template and tooling
- **Microsoft**: ADRs for cloud architecture decisions

### Lessons Learned

- Start with lightweight process for initial ADRs
- Involve whole team in decision-making process
- Keep ADRs concise but comprehensive
- Make ADRs easily discoverable and searchable
- Regularly review and update ADR status
