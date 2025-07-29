#!/usr/bin/env python3
"""
Demonstration script showing optimized pytest usage with all installed plugins.

This script shows various ways to run tests efficiently using the configured plugins.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> None:
    """Run a command and show the description."""
    print(f"\n🎯 {description}")
    print(f"💻 Command: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout:
                print(result.stdout[-500:])  # Show last 500 chars
        else:
            print(f"❌ Failed (exit code: {result.returncode})")
            if result.stderr:
                print(result.stderr[-500:])
    except Exception as e:
        print(f"💥 Error: {e}")


def main() -> None:
    """Demonstrate optimized pytest usage."""
    
    print("🚀 FLEXT-API Pytest Optimization Demo")
    print("=" * 60)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    print(f"📁 Working directory: {project_dir}")
    
    demos = [
        # 1. Fast unit tests only
        (
            ["pytest", "-m", "unit", "-v", "--tb=short"],
            "Fast unit tests with verbose output"
        ),
        
        # 2. Parallel execution
        (
            ["pytest", "-n", "auto", "--dist=loadfile", "-q"],
            "Parallel test execution with auto-scaling"
        ),
        
        # 3. Coverage with smart reporting
        (
            ["pytest", "--cov=src/flext_api", "--cov-report=term-missing:skip-covered", "--cov-fail-under=90"],
            "Coverage analysis with optimized reporting"
        ),
        
        # 4. Integration tests with timeout
        (
            ["pytest", "-m", "integration", "--timeout=300", "-v"],
            "Integration tests with timeout protection"
        ),
        
        # 5. Random test order for independence verification
        (
            ["pytest", "--randomly-seed=12345", "--randomly-dont-reorganize", "-q"],
            "Tests with deterministic random order"
        ),
        
        # 6. Benchmark tests (if enabled)
        (
            ["pytest", "-m", "benchmark", "--benchmark-only", "--benchmark-sort=mean"],
            "Performance benchmarks with optimized reporting"
        ),
        
        # 7. Dead fixtures detection
        (
            ["pytest", "--dead-fixtures"],
            "Dead fixtures detection for cleanup"
        ),
        
        # 8. Test discovery without execution
        (
            ["pytest", "--collect-only", "-q"],
            "Test discovery and collection analysis"
        ),
        
        # 9. Failed tests from last run
        (
            ["pytest", "--lf", "-v"],
            "Re-run only failed tests from last execution"
        ),
        
        # 10. Comprehensive test suite with all optimizations
        (
            ["pytest", 
             "-n", "auto",
             "--dist=loadfile", 
             "--cov=src/flext_api",
             "--cov-report=html:htmlcov",
             "--cov-report=xml:reports/coverage.xml",
             "--randomly-seed=auto",
             "--timeout=300",
             "-ra",
             "--tb=short"
            ],
            "Full optimized test suite execution"
        )
    ]
    
    for cmd, description in demos:
        run_command(cmd, description)
        print("\n" + "⏸️ " * 30)
        
        # Ask user if they want to continue
        if "--collect-only" not in cmd:  # Skip prompt for non-destructive commands
            response = input("\nContinue to next demo? (y/n/q): ").lower()
            if response == 'q':
                break
            elif response == 'n':
                continue
    
    print("\n🎉 Pytest optimization demo completed!")
    print("\n📚 Key optimizations implemented:")
    print("   ✅ Parallel execution with pytest-xdist")
    print("   ✅ Smart coverage reporting with pytest-cov")
    print("   ✅ Random test ordering with pytest-randomly") 
    print("   ✅ Timeout protection with pytest-timeout")
    print("   ✅ Enhanced mocking with pytest-mock")
    print("   ✅ HTTP testing with pytest-httpx")
    print("   ✅ Factory-based data generation with factory-boy")
    print("   ✅ Performance benchmarking with pytest-benchmark")
    print("   ✅ Dead fixture detection with pytest-deadfixtures")
    print("   ✅ Environment variable management with pytest-env")
    print("   ✅ Better test output with pytest-sugar and pytest-clarity")
    
    print("\n🔧 Usage examples:")
    print("   # Fast feedback loop:")
    print("   pytest -m unit -n auto --tb=short")
    print()
    print("   # Complete validation:")
    print("   pytest --cov=src/flext_api --cov-fail-under=90 -n auto")
    print()
    print("   # Integration tests only:")
    print("   pytest -m integration --timeout=600")
    print()
    print("   # Benchmarks:")
    print("   pytest -m benchmark --benchmark-only")


if __name__ == "__main__":
    main()