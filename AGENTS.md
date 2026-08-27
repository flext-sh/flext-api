# AGENTS.md — flext-api

> **Parent workspace law** lives in [`../AGENTS.md`](../AGENTS.md) — read it first.
> Universal engineering core: `~/.agents/UNIVERSAL_CORE.md`. Composition: global skills + parent/root `AGENTS.md` + this scope delta. Do not re-embed universal law.
>
> **Standalone / independent mode:** when `../AGENTS.md` does not resolve, pin the parent raw `AGENTS.md` URL to the same branch/release as this package (never `main`).

<!-- AIHUB-AGENTS-SCOPE-LOCAL-BEGIN -->
**Package:** `flext_api` · deps: `flext-core`, `flext-web`

## Overview

High-performance REST layer (FastAPI-oriented). The HTTP boundary consumed by `flext-auth`, `flext-oracle-oic`, `flext-oracle-wms`, `flext-quality`, and OIC connectors.

## Structure

```text
src/flext_api/
├── api.py            # FlextApi facade: typed HTTP methods over a shared client
├── base.py
├── constants.py typings.py protocols.py models.py utilities.py   # AUTO-GENERATED facets
└── _config.py _constants/ _models/ _protocols/ _typings/ _utilities/
```

## Code Map

| Symbol | Kind | Location | Role |
|--------|------|----------|------|
| `FlextApi` | class | `api.py` | facade: `client`, `settings`, `request`, `get/post/put/patch/delete` |

All method calls funnel through the private `_http_method`; headers/kwargs are assembled per call.

## Conventions (specific to this package)

- Use the **typed HTTP methods / facade** — never bypass the shared client chain.
- Request/response payloads are Pydantic-2 models (`model_dump(mode="json")` only at the wire edge).
- Config/settings canonical pattern: ADR-012.
- Codemod governance (ast-grep + make mod): ADR-014.

## Commands

```bash
make check PROJECT=flext-api
make test  PROJECT=flext-api       # tests/unit
```
<!-- AIHUB-AGENTS-SCOPE-LOCAL-END -->
