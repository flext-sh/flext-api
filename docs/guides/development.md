<!-- Generated from docs/guides/development.md for flext-api. -->

<!-- Source of truth: workspace docs/guides/. -->

# flext-api - FLEXT Development Guide

> Project profile: `flext-api`

This guide covers setting up a development environment for FLEXT contributions and understanding the development workflow.

## Prerequisites

- **Python 3.13+** (required for all FLEXT projects)
- **Poetry** (for dependency management)
- **Git** (for version control)
- **Docker** (optional, for containerized development)

## Development Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/flext-sh/flext.git
cd flext
```

### 2. Install Dependencies

```bash
# Install all dependencies and pre-commit hooks
make setup

# Or install manually
poetry install
pre-commit install
```

### 3. Verify Installation

```bash
# Run quality gates to verify setup
make val

# Check individual components
make lint-all
make type-check-all
make test-all
```

## Project Structure

FLEXT is organized as a monorepo with the following structure:

```
flext/
├── flext-core/           # Foundation library
├── flext-api/            # HTTP client and FastAPI
├── flext-auth/           # Authentication services
├── flext-ldap/           # LDAP operations
├── flext-ldif/           # LDIF processing
├── flext-grpc/           # gRPC services
├── flext-cli/            # Command-line interface
├── flext-meltano/        # Meltano integration
├── flext-observability/  # Monitoring and metrics
├── flext-quality/        # Quality assurance tools
├── docs/                 # Documentation
├── scripts/              # Development scripts
└── examples/             # Usage examples
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/amazing-feature
```

### 2. Make Changes

Follow FLEXT development standards:

- **Use r[T]** for all operations
- **Follow Clean Architecture** principles
- **Maintain type safety** with MyPy strict mode
- **Write comprehensive tests**

### 3. Run Quality Gates

```bash
# Quick validation (before commit)
make check

# Full validation (before push)
make val
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat(component): add amazing feature"
git push origin feature/amazing-feature
```

## Code Standards

### Type Safety (ZERO TOLERANCE)

```python
```

## Adding New Projects

### 1. Create Project Structure

```bash
# Copy from existing project
cp -r flext-api flext-newlib
cd flext-newlib

# Update project metadata
# Edit pyproject.toml, README.md, etc.
```

### 2. Implement Core Patterns

```python
```

### Test Failures

```bash
# Run with verbose output
pytest tests/unit/test_module.py -vv --tb=long

# Debug mode
pytest tests/unit/test_module.py --pdb
```

### Import Issues

```bash
# Verify PYTHONPATH
export PYTHONPATH=src
python -c "import flext_core; u.Cli.print(flext_core.__file__)"

# Check poetry environment
poetry env info
```

## Documentation

### Code Documentation

```python
def process_data(data: t.JsonMapping) -> p.Result[ProcessedData]:
    """Process data using the FLEXT pipeline.

    Args:
        data: Input data dictionary

    Returns:
        r containing processed data or error

    Raises:
        ValidationError: If data validation fails

    Example:
        >>> result = process_data({"key": "value"})
        >>> if result.success:
        ...     processed = result.unwrap()

    """
    # Implementation here```
### README Updates

Update project README.md files when adding new features:

- Add a "New Feature" section with usage and configuration examples.

```python
from flext_newlib import FlextNewlib, FlextNewlibSettings

lib = FlextNewlib()
result = lib.new_feature()

settings = FlextNewlibSettings(new_setting="value")```
## Contributing

### Pull Request Process

1. **Fork the repository**
1. **Create a feature branch**
1. **Make your changes**
1. **Run quality gates**
1. **Write tests**
1. **Update documentation**
1. **Submit pull request**

### Code Review Guidelines

- **Follow FLEXT patterns** and architecture
- **Maintain test coverage** above 85%
- **Update documentation** for new features
- **Ensure type safety** with MyPy strict mode
- **Use descriptive commit messages**

## Troubleshooting

### Common Issues

1. **Import Errors**

   ```bash
   # Check PYTHONPATH
   export PYTHONPATH=src

   # Reinstall dependencies
   make clean && make setup
   ```

````

2. **Test Failures**

   ```bash
   # Run with debug output
   pytest -vv --tb=long

   # Check specific test
   pytest tests/unit/test_specific.py::test_function -v
````

1. **Build Issues**

   ```bash
   # Clean and rebuild
   make clean-all
   make setup
   make build-all
   ```

## Resources

- FLEXT Core Patterns
- Quality Standards
- Testing Guide
- API Reference
- Examples

## Support

- **Issues**: [GitHub Issues](https://github.com/flext-sh/flext/issues)
- **Discussions**: [GitHub Discussions](https://github.com/flext-sh/flext/discussions)
- **Email**: <dev@flext.com>
