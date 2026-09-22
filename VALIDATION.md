# flext-api Projection Validation

## Summary
All projections conform to flext-infra templates. Full gate sequence executed on `8d0659cc`.

## Gate Results

| Gate | Result |
|---|---|
| `make gen` x2 | 0 effects (idempotent) |
| `make fix` | 1 check stage, 0 failures |
| `make fmt` | 83 files left unchanged |
| `make check` | 19/20 rules pass; 1 layout failure (lock file below) |
| `make test` | 0 tests (thin driver over flext-meltano; no test surface) |

## Layout Failure
`flext-infra-codegen-transaction-journal.json.lock` at repo root flagged as non-canonical root entry. This 0-byte lock file is not produced by any template and does not exist in flext-infra repo. It is a runtime codegen artifact that was accidentally committed. Fix: remove from tracking and add to `.gitignore`.

## Projection Comparison
All projected files conform to flext-infra templates (0 effects from conform check):
- `.envrc` → `.envrc.j2`
- `.mise.toml` → `.mise.toml.j2`
- `Makefile` → `Makefile.j2`
- `.gitignore` → `.gitignore.j2`
- `.github/workflows/ci.yml` → `ci.yml.j2`
- `.github/workflows/ci-matrix.yml` → `ci-matrix.yml.j2`
- `.github/workflows/docs.yml` → `docs.yml.j2`
- `.github/workflows/release.yml` → `release.yml.j2`
- `.github/workflows/_fragments/*` → fragment templates

## Product Finding
`.github/workflows/release.yml` is tracked and unignored in `.gitignore` but `make gen` does not produce it. The template `release.yml.j2` exists in flext-infra but is not rendered for this projection. The file at HEAD was committed manually and is not generated output.

## SHA
Worktree HEAD: `8d0659cc2f061b2f875eb19971928235a132b42b`
