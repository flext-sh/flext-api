# FLEXT API Examples

Examples in this folder show the public `flext_api` surface through the local `examples` aliases and the typed `s` service base. The goal is to demonstrate request normalization, model validation, and response or storage ergonomics without depending on an external HTTP service.

## Example Files

- `01_basic_usage.py` — guided tour of `FlextApi`, `m.Api.*`, `u.Api.RequestUtils`, and the railway result contract

## Running Examples

```bash
PYTHONPATH=src python -m examples.01_basic_usage
```

Run commands from the `flext-api` project root.

## Core Pattern

```python
from __future__ import annotations

from typing import override

from flext_api import FlextApi, c, m, p, r, s, t, u


class FlextApiExamplesDemo(s[t.JsonMapping]):
    @override
    def execute(self) -> p.Result[t.JsonMapping]:
        api = FlextApi(settings=settings)
        return api.execute().map(
            lambda ready: {
                "ready": ready,
                "base_url": settings.Api.base_url,
            }
        )
```

## Public Surfaces To Prefer

- `s` for example setup through `base.py` and typed `settings`
- `FlextApi` for facade ergonomics
- `m.Api.*` for request, response, and storage models
- `u.Api.RequestUtils` for normalized request payload construction
- `r` and `p.Result` for explicit success and failure flow

## What The Basic Example Demonstrates

- runtime settings through the local `examples` package
- request normalization before model parsing
- Pydantic 2 validation through `m.Api`
- storage and stats models without ad-hoc helper layers
- result handling with `success` and `failure`

## Best Practices

- import aliases from `examples`, not private modules
- keep examples executable from the project root
- prefer public facades and typed models over ad-hoc dict plumbing
- update this README whenever example filenames or flows change
