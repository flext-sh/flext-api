# End-to-End Tests

**Complete workflow testing with full system integration**

## Test Files

### API Workflow Tests

- **test_api_workflow_e2e.py** - Complete API request/response workflows
  - Full API service lifecycle testing
  - HTTP client creation and usage
  - Query building and execution
  - Response processing and validation
  - Error handling across complete workflows

## Test Scope

### Workflow Coverage

- Complete API request/response cycle
- Service startup and health validation
- Client creation with various configurations
- Query building with different parameters
- Error propagation and handling

### Component Integration

- FlextApi service with HTTP client
- Builder integration with API service
- Configuration management across components
- FastAPI application with service layer

## Running Tests

```bash
# All E2E tests
make test-e2e

# With specific markers
pytest tests/e2e/ -m e2e -v

# With extended timeout
pytest tests/e2e/ --timeout=60 -v

# Specific test file
pytest tests/e2e/test_api_workflow_e2e.py -v
```

## Environment Requirements

- Full API service stack availability
- Network connectivity for HTTP operations
- Configuration service access
- Sufficient memory for full service stack

## Test Characteristics

- Execution time: 10-60 seconds per workflow
- System dependencies: Complete service stack
- Test isolation: Limited (shares system resources)
- Reliability: High confidence in system behavior

## Quality Standards

- Complete workflow validation
- Realistic user scenario testing
- Proper resource management
- Clear failure diagnostics

## Development

See parent directory documentation for debugging strategies, workflow design patterns, and best practices for end-to-end testing.
