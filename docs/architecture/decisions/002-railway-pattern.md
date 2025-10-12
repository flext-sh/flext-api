# 002. Railway-Oriented Error Handling

Date: 2025-01-01

## Status

Accepted

## Context

HTTP operations are inherently unreliable - network failures, server errors, timeouts, and malformed responses are common. Traditional exception-based error handling makes code complex and error-prone. The FLEXT ecosystem needed a consistent approach to error handling that:

1. Makes error handling explicit and visible in the type system
2. Enables composable operations that can be chained together
3. Prevents silent failures and unhandled errors
4. Provides clear separation between success and failure paths
5. Integrates well with async/await patterns

Key challenges:

- HTTP errors are expected and frequent (timeouts, 4xx, 5xx responses)
- Error handling code often obscures business logic
- Exception-based code is hard to test and reason about
- Async error handling adds complexity

## Decision

FLEXT-API will use **Railway-Oriented Programming** with `FlextCore.Result[T]` for all HTTP operations. Every public method returns `FlextCore.Result[T]` instead of throwing exceptions. Operations are composed using `flat_map`, `map`, and `map_error` methods.

## Consequences

### Positive

- **Explicit Error Handling**: Errors are visible in type signatures and cannot be ignored
- **Composable Operations**: HTTP operations can be chained without nested try/catch blocks
- **Testable Code**: Railway pattern makes testing success and failure paths straightforward
- **Type Safety**: Compiler catches unhandled error cases
- **Clear Intent**: Code reads like a recipe of operations that can succeed or fail
- **Async Friendly**: Works seamlessly with async/await patterns

### Negative

- **Learning Curve**: Developers must learn railway pattern concepts
- **Verbose Code**: Some operations require more lines than exception-based code
- **Type Complexity**: Generic types can be harder to understand initially
- **Migration Effort**: Converting existing exception-based code requires significant changes

### Risks

- **Adoption Resistance**: Teams accustomed to exceptions may resist the change
- **Type System Complexity**: Advanced generic patterns may confuse some developers
- **Debugging Difficulty**: Stack traces become less useful for railway pattern code

## Alternatives Considered

### Option 1: Traditional Exceptions

```python
def get_user(user_id: int) -> User:
    response = httpx.get(f"/users/{user_id}")
    response.raise_for_status()
    return User(**response.json())
```

- **Pros**: Familiar, concise for success paths
- **Cons**: Silent failures, complex error handling, hard to test
- **Rejected**: Not suitable for enterprise HTTP operations

### Option 2: Result Pattern (Custom Implementation)

```python
class Result:
    def __init__(self, success: bool, value=None, error=None):
        self.success = success
        self.value = value
        self.error = error
```

- **Pros**: Simple implementation, explicit error handling
- **Cons**: No composability, reinventing the wheel, less type-safe
- **Rejected**: FlextCore.Result from flext-core is more robust and feature-complete

### Option 3: Hybrid Approach

- **Description**: Use railway pattern internally but expose traditional APIs
- **Pros**: Gradual adoption, familiar external APIs
- **Cons**: Inconsistent error handling, defeats the purpose
- **Rejected**: Would undermine the architectural benefits

## Implementation Examples

### Basic HTTP Operation

```python
def get_user(user_id: int) -> FlextCore.Result[User]:
    """Get user with railway error handling."""
    return (FlextApiClient()
        .get(f"/users/{user_id}")
        .flat_map(lambda resp: validate_status_code(resp))
        .flat_map(lambda resp: parse_json_response(resp))
        .map(lambda data: User(**data))
        .map_error(lambda err: f"User fetch failed: {err}")
    )
```

### Usage in Application Code

```python
# Success path
result = get_user(123)
if result.is_success:
    user = result.unwrap()
    print(f"Found user: {user.name}")

# Error handling
if result.is_failure:
    logger.error(result.error)
    return None

# Chained operations
user_profile = (get_user(user_id)
    .flat_map(lambda user: get_user_profile(user.id))
    .flat_map(lambda profile: enrich_profile(profile))
    .map_error(lambda err: log_and_notify(err))
)
```

### Testing Railway Code

```python
def test_get_user_success():
    # Given
    mock_response = MockHttpResponse(status_code=200, body='{"name": "John"}')
    client.get.return_value = FlextCore.Result.ok(mock_response)

    # When
    result = get_user(123)

    # Then
    assert result.is_success
    assert result.unwrap().name == "John"

def test_get_user_not_found():
    # Given
    client.get.return_value = FlextCore.Result.fail("HTTP 404")

    # When
    result = get_user(123)

    # Then
    assert result.is_failure
    assert "404" in result.error
```

## Migration Strategy

### Phase 1: Core Implementation

- [x] Implement FlextCore.Result integration in all HTTP operations
- [x] Update FlextApiClient to return FlextCore.Result[T]
- [x] Add railway pattern utilities and helpers

### Phase 2: Ecosystem Migration

- [x] Update all internal usage to railway pattern
- [ ] Create migration examples and documentation
- [ ] Provide utility functions for common transformations
- [ ] Update testing patterns and examples

### Phase 3: Ecosystem Adoption

- [ ] Update all ecosystem projects to use railway pattern
- [ ] Provide training and support for migration
- [ ] Update documentation and code examples
- [ ] Establish coding standards for railway pattern usage

## Best Practices

### Railway Pattern Guidelines

1. **Always Return FlextCore.Result**: Every public method should return FlextCore.Result[T]
2. **Use Descriptive Errors**: Error messages should be user-friendly and actionable
3. **Chain Operations**: Use `flat_map` for sequential operations, `map` for transformations
4. **Handle Errors Early**: Validate inputs and fail fast with clear error messages
5. **Test Both Paths**: Always test both success and failure code paths

### Error Message Standards

```python
# Good error messages
FlextCore.Result.fail("Invalid user ID: must be positive integer")
FlextCore.Result.fail("HTTP request timeout after 30 seconds")
FlextCore.Result.fail("JSON parsing failed: invalid response format")

# Avoid generic messages
FlextCore.Result.fail("Error")  # Too vague
FlextCore.Result.fail("Something went wrong")  # Not helpful
```

### Performance Considerations

- **Short-Circuiting**: Failed operations don't execute subsequent operations
- **Memory Efficiency**: No exception object creation for expected errors
- **Async Compatibility**: Works seamlessly with async/await
- **Composable**: Enables efficient pipelining of operations

## References

- [FLEXT-Core FlextCore.Result Documentation](../../../flext-core/docs/flext_result.md)
- [Railway-Oriented Programming](https://fsharpforfunandprofit.com/rop/)
- [Error Handling in Scala](https://typelevel.org/cats/datatypes/either.html)
- GitHub Issue: #156 - Railway Pattern Implementation
