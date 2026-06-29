<!-- Generated from docs/guides/testing.md for flext-api. -->

<!-- Source of truth: workspace docs/guides/. -->

# flext-api - FLEXT Testing Guide

> Project profile: `flext-api`

This guide covers testing strategies, best practices, and procedures for FLEXT applications and libraries.

## Overview

FLEXT maintains comprehensive test coverage across all **33 projects** with the following standards:

- **85%+ coverage** for foundation libraries (flext-core)
- **75%+ coverage** for applications and domain libraries
- **100% test pass rate** across all projects
- **Zero Pyrefly errors** in strict mode (successor to MyPy)
- **Zero Ruff violations** in production code

## Test Structure

FLEXT uses a hierarchical test structure:

```
tests/
├── unit/           # Unit tests (fast, isolated)
├── integration/    # Integration tests (component interaction)
├── e2e/           # End-to-end tests (full workflow)
├── fixtures/      # Test data and fixtures
└── conftest.py    # Pytest configuration
```

## Test Categories

### Unit Tests

Test individual functions and classes in isolation:

```python
```

### Parallel Test Execution

```bash
# Run tests in parallel
pytest -n auto

# Specific number of workers
pytest -n 4
```

## Test Fixtures

### Pytest Fixtures

```python
```

### Loading Test Data

```python
import json
from pathlib import Path

def load_test_fixture(fixture_name: str) -> str:
    """Load test fixture from fixtures directory."""
    fixture_path = Path(__file__).parent / "fixtures" / fixture_name
    return fixture_path.read_text()

def load_json_fixture(fixture_name: str) -> t.JsonMapping:
    """Load JSON test fixture."""
    fixture_path = Path(__file__).parent / "fixtures" / fixture_name
    return json.loads(fixture_path.read_text())

# Usage
def test_with_fixture():
    """Test using loaded fixture data."""
    ldif_content = load_test_fixture("ldif/valid.ldif")
    config_data = load_json_fixture("settings/dev.yaml")

    # Use fixture data in test
    result = process_ldif(ldif_content, config_data)
    assert result.success```
## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.13]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Run tests
        run: |
          poetry run pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml```
## Best Practices

### 1. Test Naming

```python
# ✅ GOOD - Descriptive test names
def test_parse_valid_ldif_returns_success():
    """Test that parsing valid LDIF returns success result."""
    pass

def test_parse_invalid_ldif_returns_failure():
    """Test that parsing invalid LDIF returns failure result."""
    pass

# ❌ BAD - Vague test names
def test_parse():
    pass

def test_ldif():
    pass```
### 2. Test Organization

```python
class TestLdifParsing:
    """Test LDIF parsing functionality."""

    def test_parse_valid_single_entry(self):
        """Test parsing single valid LDIF entry."""
        pass

    def test_parse_valid_multiple_entries(self):
        """Test parsing multiple valid LDIF entries."""
        pass

    def test_parse_invalid_format(self):
        """Test parsing invalid LDIF format."""
        pass

class TestLdifMigration:
    """Test LDIF migration functionality."""

    def test_migrate_oid_to_oud(self):
        """Test OID to OUD migration."""
        pass```
### 3. Assertion Quality

```python
# ✅ GOOD - Specific assertions
def test_parse_result():
    result = ldif.parse(content)

    assert result.success
    entries = result.unwrap()
    assert len(entries) == 1
    assert entries[0].dn == "cn=test,dc=example,dc=com"
    assert "cn" in entries[0].attributes

# ❌ BAD - Vague assertions
def test_parse_result():
    result = ldif.parse(content)
    assert result  # Too vague```

### 4. Test Independence
```python
# ✅ GOOD - Independent tests
def test_parse_valid_ldif():
    ldif = ldif()  # Fresh instance
    result = ldif.parse("dn: test")
    assert result.success

def test_parse_invalid_ldif():
    ldif = ldif()  # Fresh instance
    result = ldif.parse("invalid")
    assert result.failure

# ❌ BAD - Dependent tests
ldif = ldif()  # Shared instance

def test_parse_valid_ldif():
    result = ldif.parse("dn: test")
    assert result.success

def test_parse_invalid_ldif():
    result = ldif.parse("invalid")
    assert result.failure```
## Troubleshooting

### Common Test Issues

1. **Import Errors**

   ```bash
   # Set PYTHONPATH
   export PYTHONPATH=src
   pytest
   ```

1. **Fixture Not Found**

   ```python notest
   # Check fixture scope and dependencies
   @pytest.fixture(scope="function")
   def my_fixture():
       return "value"
   ```

1. **Test Timeout**

   ```bash
   # Increase timeout
   pytest --timeout=300
   ```

1. **Coverage Issues**

   ```bash
   # Check coverage configuration
   pytest --cov=src --cov-report=term-missing
   ```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- FLEXT Quality Standards
- Test Examples
- CI/CD Configuration
