# Performance Benchmarks

**Performance testing and benchmarking for FLEXT API components**

## Test Files

### Performance Benchmarks

- **test_performance_benchmarks.py** - Core component performance testing
  - API service creation and initialization benchmarks
  - HTTP client creation and configuration benchmarks
  - Query builder performance testing
  - Response builder performance validation
  - Memory usage and allocation profiling

## Benchmark Categories

### Service Performance

- API service instantiation time
- Service startup and shutdown performance
- Health check response time
- Resource cleanup efficiency

### Client Performance

- HTTP client creation time
- Request processing throughput
- Connection pooling efficiency
- Plugin processing overhead

### Builder Performance

- Query construction time
- Response building efficiency
- Memory allocation patterns
- Object creation overhead

## Running Benchmarks

```bash
# All performance benchmarks
make test-benchmark

# With specific markers
pytest tests/benchmarks/ -m benchmark -v

# With profiling
pytest tests/benchmarks/ --profile -v

# Generate benchmark report
pytest tests/benchmarks/ --benchmark-json=results.json
```

## Benchmark Configuration

```bash
# Custom iterations
pytest tests/benchmarks/ --benchmark-iterations=1000

# Memory profiling
pytest tests/benchmarks/ --benchmark-memory

# Specific benchmark file
pytest tests/benchmarks/test_performance_benchmarks.py -v
```

## Performance Metrics

### Time Measurements

- Minimum/maximum/mean execution time
- Standard deviation
- 95th percentile response time

### Memory Measurements

- Peak memory usage
- Memory allocation patterns
- Memory leak detection

### Throughput Measurements

- Operations per second
- Concurrent operation handling
- Resource utilization efficiency

## Development

See parent directory documentation for benchmark development patterns, performance debugging, and optimization guidelines.
