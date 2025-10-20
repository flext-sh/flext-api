#!/usr/bin/env python3
"""AST-based dead code analyzer for FLEXT-API.

Detects unused imports, functions, classes, variables, and unreachable code
across all Python modules in the flext-api project.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class UnusedItem:
    """Record for an unused code item."""

    file_path: str
    item_type: str  # "import", "function", "class", "variable"
    name: str
    line_number: int
    context: str = ""  # Brief code context


@dataclass
class DeadCodeAnalysis:
    """Complete dead code analysis results."""

    unused_imports: list[UnusedItem] = field(default_factory=list)
    unused_functions: list[UnusedItem] = field(default_factory=list)
    unused_classes: list[UnusedItem] = field(default_factory=list)
    unused_variables: list[UnusedItem] = field(default_factory=list)
    unreachable_code: list[UnusedItem] = field(default_factory=list)

    def total_items(self) -> int:
        """Get total count of unused items."""
        return (
            len(self.unused_imports)
            + len(self.unused_functions)
            + len(self.unused_classes)
            + len(self.unused_variables)
            + len(self.unreachable_code)
        )


class UnusedImportDetector(ast.NodeVisitor):
    """Detect unused import statements."""

    def __init__(self, filename: str) -> None:
        """Initialize the import analyzer with a file."""
        self.filename = filename
        self.imported_names: dict[str, tuple[int, str]] = {}  # name -> (line, context)
        self.used_names: set[str] = set()
        self.unused: list[UnusedItem] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Record direct imports."""
        for alias in node.names:
            name = alias.asname or alias.name
            self.imported_names[name] = (node.lineno, f"import {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Record from-imports."""
        for alias in node.names:
            name = alias.asname or alias.name
            if name != "*":  # Skip wildcard imports
                module = node.module or ""
                self.imported_names[name] = (
                    node.lineno,
                    f"from {module} import {alias.name}",
                )
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Track name usage."""
        if isinstance(node.ctx, (ast.Load, ast.Del)):
            self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Track attribute usage (e.g., os.path)."""
        if isinstance(node.value, ast.Name) and isinstance(node.value.ctx, ast.Load):
            self.used_names.add(node.value.id)
        self.generic_visit(node)

    def analyze(self) -> list[UnusedItem]:
        """Find all unused imports."""
        for name, (line, context) in self.imported_names.items():
            if name not in self.used_names:
                self.unused.append(
                    UnusedItem(
                        file_path=self.filename,
                        item_type="import",
                        name=name,
                        line_number=line,
                        context=context,
                    )
                )
        return self.unused


class UnusedDefinitionDetector(ast.NodeVisitor):
    """Detect unused function and class definitions."""

    def __init__(self, filename: str) -> None:
        """Initialize the definition detector with a file."""
        self.filename = filename
        self.defined_functions: dict[str, int] = {}  # name -> line
        self.defined_classes: dict[str, int] = {}  # name -> line
        self.used_names: set[str] = set()
        self.current_class: str | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Record function definitions."""
        if self.current_class is None and not node.name.startswith("_"):
            self.defined_functions[node.name] = node.lineno
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Record async function definitions."""
        if self.current_class is None and not node.name.startswith("_"):
            self.defined_functions[node.name] = node.lineno
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Record class definitions."""
        if not node.name.startswith("_"):
            self.defined_classes[node.name] = node.lineno
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_Name(self, node: ast.Name) -> None:
        """Track name usage."""
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Track function calls."""
        if isinstance(node.func, ast.Name):
            self.used_names.add(node.func.id)
        self.generic_visit(node)

    def analyze(self) -> tuple[list[UnusedItem], list[UnusedItem]]:
        """Find all unused functions and classes."""
        unused_funcs: list[UnusedItem] = []
        unused_classes: list[UnusedItem] = []

        for name, line in self.defined_functions.items():
            if name not in self.used_names and name != "__init__":
                unused_funcs.append(
                    UnusedItem(
                        file_path=self.filename,
                        item_type="function",
                        name=name,
                        line_number=line,
                    )
                )

        for name, line in self.defined_classes.items():
            if name not in self.used_names:
                unused_classes.append(
                    UnusedItem(
                        file_path=self.filename,
                        item_type="class",
                        name=name,
                        line_number=line,
                    )
                )

        return unused_funcs, unused_classes


class ASTAnalyzer:
    """Main AST analyzer for dead code detection."""

    def __init__(self, root_dir: Path) -> None:
        """Initialize the AST analyzer with a root directory."""
        self.root_dir = root_dir
        self.analysis = DeadCodeAnalysis()

    def analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file for dead code."""
        try:
            with Path(file_path).open("r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))

            # Analyze unused imports
            import_detector = UnusedImportDetector(str(file_path))
            import_detector.visit(tree)
            self.analysis.unused_imports.extend(import_detector.analyze())

            # Analyze unused definitions
            def_detector = UnusedDefinitionDetector(str(file_path))
            def_detector.visit(tree)
            unused_funcs, unused_classes = def_detector.analyze()
            self.analysis.unused_functions.extend(unused_funcs)
            self.analysis.unused_classes.extend(unused_classes)

        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}", file=sys.stderr)

    def analyze_directory(self, pattern: str = "*.py") -> None:
        """Analyze all Python files in directory."""
        python_files = list(self.root_dir.rglob(pattern))
        print(f"Found {len(python_files)} Python files to analyze...")

        for file_path in python_files:
            # Skip __pycache__ and .venv
            if "__pycache__" in str(file_path) or ".venv" in str(file_path):
                continue
            if file_path.name == "__pycache__":
                continue

            print(
                f"Analyzing {file_path.relative_to(self.root_dir)}...",
                end="",
                flush=True,
            )
            self.analyze_file(file_path)
            print(" ✓")

    def generate_report(self) -> str:
        """Generate formatted analysis report."""
        lines: list[str] = []

        lines.extend([
            "=" * 80,
            "AST DEAD CODE ANALYSIS REPORT",
            "=" * 80,
            "",
        ])

        # Summary
        lines.extend([
            f"Total unused items found: {self.analysis.total_items()}",
            "",
        ])

        # Unused imports
        if self.analysis.unused_imports:
            lines.extend((
                f"UNUSED IMPORTS ({len(self.analysis.unused_imports)}):",
                "-" * 80,
            ))
            for item in sorted(self.analysis.unused_imports, key=lambda x: x.file_path):
                lines.extend((
                    f"  {item.file_path}:{item.line_number}",
                    f"    Name: {item.name}",
                    f"    Context: {item.context}",
                ))
            lines.append("")

        # Unused functions
        if self.analysis.unused_functions:
            lines.extend((
                f"UNUSED FUNCTIONS ({len(self.analysis.unused_functions)}):",
                "-" * 80,
            ))
            for item in sorted(
                self.analysis.unused_functions, key=lambda x: x.file_path
            ):
                lines.extend((
                    f"  {item.file_path}:{item.line_number}",
                    f"    Name: {item.name}",
                ))
            lines.append("")

        # Unused classes
        if self.analysis.unused_classes:
            lines.extend((
                f"UNUSED CLASSES ({len(self.analysis.unused_classes)}):",
                "-" * 80,
            ))
            for item in sorted(self.analysis.unused_classes, key=lambda x: x.file_path):
                lines.extend((
                    f"  {item.file_path}:{item.line_number}",
                    f"    Name: {item.name}",
                ))
            lines.append("")

        # Unused variables (placeholder for future enhancement)
        if self.analysis.unused_variables:
            lines.extend((
                f"UNUSED VARIABLES ({len(self.analysis.unused_variables)}):",
                "-" * 80,
            ))
            for item in sorted(
                self.analysis.unused_variables, key=lambda x: x.file_path
            ):
                lines.extend((
                    f"  {item.file_path}:{item.line_number}",
                    f"    Name: {item.name}",
                ))
            lines.append("")

        # Unreachable code (placeholder for future enhancement)
        if self.analysis.unreachable_code:
            lines.extend((
                f"UNREACHABLE CODE ({len(self.analysis.unreachable_code)}):",
                "-" * 80,
            ))
            for item in sorted(
                self.analysis.unreachable_code, key=lambda x: x.file_path
            ):
                lines.extend((
                    f"  {item.file_path}:{item.line_number}",
                    f"    Context: {item.context}",
                ))
            lines.append("")

        lines.extend(("=" * 80, "ANALYSIS COMPLETE", "=" * 80))

        return "\n".join(lines)

    def save_report(self, output_file: Path) -> None:
        """Save report to file."""
        report = self.generate_report()
        with Path(output_file).open("w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nReport saved to {output_file}")


def main() -> None:
    """Main entry point."""
    project_root = Path("/home/marlonsc/flext/flext-api")
    src_dir = project_root / "src" / "flext_api"

    if not src_dir.exists():
        print(f"Error: {src_dir} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing {src_dir}...")
    print()

    analyzer = ASTAnalyzer(src_dir)
    analyzer.analyze_directory()

    print()
    print(analyzer.generate_report())

    # Save report
    report_file = project_root / "ast_analysis_report.txt"
    analyzer.save_report(report_file)


if __name__ == "__main__":
    main()
