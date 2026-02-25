#!/usr/bin/env python3
"""
Structural Parity Audit
=======================
Scans all domain Python files and cross-compares them to identify:
  1. Methods duplicated across 3+ domains → consolidation candidates
  2. Files with identical names across domains → naming parity candidates
  3. Import statements diverging for the same logical concern
  4. Module-level function patterns appearing in multiple domains

Writes a ranked report to tasks/parity_report.md.

Usage:
  python3 scripts/audit/structural_parity.py
  python3 scripts/audit/structural_parity.py --verbose
"""

from __future__ import annotations

import ast
import sys
import textwrap
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent
DOMAINS_DIR = PROJECT_ROOT / "domains"
SHARED_DIR = PROJECT_ROOT / "shared"
REPORT_PATH = PROJECT_ROOT / "tasks" / "parity_report.md"

KNOWN_DOMAINS = ["materials", "contaminants", "compounds", "settings", "applications"]

VERBOSE = "--verbose" in sys.argv


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MethodSig:
    name: str
    args: List[str]
    returns: Optional[str]
    lineno: int
    docstring: Optional[str] = None
    body_lines: int = 0


@dataclass
class DomainFile:
    domain: str
    rel_path: str                        # relative to project root
    abs_path: Path
    classes: Dict[str, List[MethodSig]] = field(default_factory=dict)
    module_functions: List[MethodSig] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    line_count: int = 0


@dataclass
class PairityFinding:
    category: str           # 'method_overlap', 'file_name', 'import_drift', 'module_func'
    title: str
    priority: str           # 'HIGH', 'MEDIUM', 'LOW'
    domains_affected: List[str]
    details: List[str]
    estimated_lines_saved: int = 0


# ---------------------------------------------------------------------------
# AST parsing helpers
# ---------------------------------------------------------------------------

def _arg_name(arg: ast.arg) -> str:
    return arg.arg


def _parse_returns(node: ast.FunctionDef) -> Optional[str]:
    if node.returns is None:
        return None
    try:
        return ast.unparse(node.returns)
    except Exception:
        return None


def parse_file(path: Path, domain: str) -> Optional[DomainFile]:
    """Parse a .py file and extract structural information."""
    try:
        source = path.read_text(encoding="utf-8")
    except Exception:
        return None

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return None

    lines = source.splitlines()
    df = DomainFile(
        domain=domain,
        rel_path=str(path.relative_to(PROJECT_ROOT)),
        abs_path=path,
        line_count=len(lines),
    )

    # Collect imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                df.imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                df.imports.append(f"{module}.{alias.name}")

    # Collect top-level classes and their methods
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods: List[MethodSig] = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    args = [_arg_name(a) for a in item.args.args]
                    # measure body lines (excluding def line and docstring)
                    body_start = item.lineno
                    body_end = item.end_lineno or item.lineno
                    docstring = ast.get_docstring(item)
                    methods.append(MethodSig(
                        name=item.name,
                        args=args,
                        returns=_parse_returns(item),
                        lineno=item.lineno,
                        docstring=docstring,
                        body_lines=body_end - body_start,
                    ))
            df.classes[node.name] = methods

        elif isinstance(node, ast.FunctionDef):
            args = [_arg_name(a) for a in node.args.args]
            df.module_functions.append(MethodSig(
                name=node.name,
                args=args,
                returns=_parse_returns(node),
                lineno=node.lineno,
                body_lines=(node.end_lineno or node.lineno) - node.lineno,
            ))

    return df


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def collect_domain_files() -> Dict[str, List[DomainFile]]:
    """Walk domains/ and parse every Python file."""
    domain_files: Dict[str, List[DomainFile]] = defaultdict(list)

    for domain in KNOWN_DOMAINS:
        domain_dir = DOMAINS_DIR / domain
        if not domain_dir.exists():
            continue
        for py_file in sorted(domain_dir.rglob("*.py")):
            if "__pycache__" in py_file.parts:
                continue
            df = parse_file(py_file, domain)
            if df:
                domain_files[domain].append(df)

    return domain_files


# ---------------------------------------------------------------------------
# Analysis passes
# ---------------------------------------------------------------------------

def find_method_overlaps(domain_files: Dict[str, List[DomainFile]]) -> List[PairityFinding]:
    """Find methods with the same name (or same pattern) across 3+ domains."""
    # method_name → {domain → [(class_name, MethodSig)]}
    method_index: Dict[str, Dict[str, List[Tuple[str, MethodSig]]]] = defaultdict(lambda: defaultdict(list))

    for domain, files in domain_files.items():
        for df in files:
            for class_name, methods in df.classes.items():
                for method in methods:
                    method_index[method.name][domain].append((class_name, method))

    findings: List[PairityFinding] = []

    for method_name, domain_map in method_index.items():
        if len(domain_map) < 2:
            continue
        if method_name.startswith("_") and method_name in ("__init__", "__repr__", "__str__"):
            continue

        domains_with = sorted(domain_map.keys())
        total_lines = sum(
            m.body_lines
            for entries in domain_map.values()
            for (_, m) in entries
        )
        # Only count savings if shared impl would eliminate N-1 copies
        n = len(domains_with)
        estimated_saved = int(total_lines * (n - 1) / n) if n > 1 else 0

        # Assess priority
        if n >= 4:
            priority = "HIGH"
        elif n == 3:
            priority = "MEDIUM"
        else:
            # 2 domains — only flag if body is substantial
            priority = "LOW" if total_lines < 30 else "MEDIUM"

        details = []
        for dom, entries in sorted(domain_map.items()):
            for class_name, m in entries:
                arg_str = ", ".join(m.args)
                ret_str = f" → {m.returns}" if m.returns else ""
                details.append(f"  {dom}: `{class_name}.{method_name}({arg_str}){ret_str}` (L{m.lineno}, ~{m.body_lines} lines)")

        findings.append(PairityFinding(
            category="method_overlap",
            title=f"`{method_name}()` — appears in {n} domains",
            priority=priority,
            domains_affected=domains_with,
            details=details,
            estimated_lines_saved=estimated_saved,
        ))

    findings.sort(key=lambda f: (-len(f.domains_affected), -f.estimated_lines_saved))
    return findings


def find_file_name_parity(domain_files: Dict[str, List[DomainFile]]) -> List[PairityFinding]:
    """Find files with identical names/paths (relative to domain root) across domains."""
    # filename (relative to domain dir) → {domain → abs_path}
    filename_index: Dict[str, Dict[str, Path]] = defaultdict(dict)

    for domain, files in domain_files.items():
        domain_dir = DOMAINS_DIR / domain
        for df in files:
            try:
                rel = df.abs_path.relative_to(domain_dir)
                filename_index[str(rel)][domain] = df.abs_path
            except ValueError:
                pass

    findings: List[PairityFinding] = []

    for rel_path, domain_map in filename_index.items():
        if len(domain_map) < 2:
            continue
        domains_with = sorted(domain_map.keys())
        n = len(domains_with)
        details = [f"  {d}: {domain_map[d].relative_to(PROJECT_ROOT)}" for d in domains_with]
        priority = "HIGH" if n >= 4 else ("MEDIUM" if n == 3 else "LOW")

        findings.append(PairityFinding(
            category="file_name",
            title=f"`{rel_path}` — identical path in {n} domains",
            priority=priority,
            domains_affected=domains_with,
            details=details,
        ))

    findings.sort(key=lambda f: -len(f.domains_affected))
    return findings


def find_import_drift(domain_files: Dict[str, List[DomainFile]]) -> List[PairityFinding]:
    """Find shared/ imports used inconsistently across domains (some use, some don't)."""
    # shared_symbol → set of domains that import it
    shared_imports: Dict[str, Set[str]] = defaultdict(set)

    for domain, files in domain_files.items():
        seen: Set[str] = set()
        for df in files:
            for imp in df.imports:
                if imp.startswith("shared.") and imp not in seen:
                    seen.add(imp)
                    shared_imports[imp].add(domain)

    all_domains = set(KNOWN_DOMAINS) & set(domain_files.keys())
    findings: List[PairityFinding] = []

    for symbol, domains_using in shared_imports.items():
        missing = sorted(all_domains - domains_using)
        using = sorted(domains_using)
        if not missing or len(using) < 2:
            continue

        priority = "HIGH" if len(using) >= 3 else "MEDIUM"
        details = [
            f"  Uses: {', '.join(using)}",
            f"  Missing: {', '.join(missing)}",
        ]
        findings.append(PairityFinding(
            category="import_drift",
            title=f"`{symbol}` — used by {len(using)} domains, absent in {len(missing)}",
            priority=priority,
            domains_affected=using,
            details=details,
        ))

    findings.sort(key=lambda f: (-len(f.domains_affected), f.title))
    return findings


def find_module_function_patterns(domain_files: Dict[str, List[DomainFile]]) -> List[PairityFinding]:
    """Find module-level functions with the same name across multiple domains."""
    func_index: Dict[str, Dict[str, MethodSig]] = defaultdict(dict)

    for domain, files in domain_files.items():
        for df in files:
            for func in df.module_functions:
                func_index[func.name][domain] = func

    findings: List[PairityFinding] = []

    for func_name, domain_map in func_index.items():
        if len(domain_map) < 2:
            continue
        domains_with = sorted(domain_map.keys())
        n = len(domains_with)
        total_lines = sum(m.body_lines for m in domain_map.values())
        estimated_saved = int(total_lines * (n - 1) / n)

        priority = "HIGH" if n >= 4 else ("MEDIUM" if n == 3 else "LOW")

        details = []
        for dom in domains_with:
            m = domain_map[dom]
            arg_str = ", ".join(m.args)
            ret_str = f" → {m.returns}" if m.returns else ""
            details.append(f"  {dom}: `{func_name}({arg_str}){ret_str}` (L{m.lineno}, ~{m.body_lines} lines)")

        findings.append(PairityFinding(
            category="module_func",
            title=f"`{func_name}()` module-level — {n} domains",
            priority=priority,
            domains_affected=domains_with,
            details=details,
            estimated_lines_saved=estimated_saved,
        ))

    findings.sort(key=lambda f: (-len(f.domains_affected), -f.estimated_lines_saved))
    return findings


# ---------------------------------------------------------------------------
# Base class coverage check
# ---------------------------------------------------------------------------

def find_base_class_gaps(domain_files: Dict[str, List[DomainFile]]) -> List[PairityFinding]:
    """Find methods in domain coordinators that could move to the base class."""
    # Load base coordinator signatures
    base_file = SHARED_DIR / "domain" / "base_coordinator.py"
    if not base_file.exists():
        return []

    base_df = parse_file(base_file, "_base")
    base_methods: Set[str] = set()
    for class_name, methods in (base_df.classes if base_df else {}).items():
        for m in methods:
            base_methods.add(m.name)

    # Coordinator class pattern: *Coordinator in coordinators
    coordinator_methods: Dict[str, Dict[str, MethodSig]] = defaultdict(dict)
    for domain, files in domain_files.items():
        for df in files:
            if "coordinator" in df.rel_path:
                for class_name, methods in df.classes.items():
                    for m in methods:
                        if m.name not in base_methods:
                            coordinator_methods[m.name][domain] = m

    findings: List[PairityFinding] = []
    for method_name, domain_map in coordinator_methods.items():
        if len(domain_map) < 3:
            continue
        domains_with = sorted(domain_map.keys())
        total_lines = sum(m.body_lines for m in domain_map.values())
        estimated_saved = int(total_lines * (len(domains_with) - 1) / len(domains_with))
        details = []
        for dom in domains_with:
            m = domain_map[dom]
            arg_str = ", ".join(m.args)
            details.append(f"  {dom}: `{m.name}({arg_str})` (~{m.body_lines} lines)")

        findings.append(PairityFinding(
            category="base_class_gap",
            title=f"`{method_name}()` in {len(domains_with)} coordinators but not in base class",
            priority="HIGH" if len(domains_with) >= 4 else "MEDIUM",
            domains_affected=domains_with,
            details=details,
            estimated_lines_saved=estimated_saved,
        ))

    findings.sort(key=lambda f: (-len(f.domains_affected), -f.estimated_lines_saved))
    return findings


def find_loader_base_gaps(domain_files: Dict[str, List[DomainFile]]) -> List[PairityFinding]:
    """Find methods in domain data_loader_v2 files that are identical in 3+ domains."""
    # Gather methods specifically from loader files
    loader_methods: Dict[str, Dict[str, MethodSig]] = defaultdict(dict)

    for domain, files in domain_files.items():
        for df in files:
            if "data_loader_v2" in df.rel_path:
                for class_name, methods in df.classes.items():
                    for m in methods:
                        loader_methods[m.name][domain] = m

    # Check what BaseDataLoader already provides
    base_loader = SHARED_DIR / "data" / "base_loader.py"
    base_methods: Set[str] = set()
    if base_loader.exists():
        base_df = parse_file(base_loader, "_base")
        if base_df:
            for _, methods in base_df.classes.items():
                for m in methods:
                    base_methods.add(m.name)

    findings: List[PairityFinding] = []
    for method_name, domain_map in loader_methods.items():
        if len(domain_map) < 3:
            continue
        if method_name in base_methods:
            continue
        domains_with = sorted(domain_map.keys())
        total_lines = sum(m.body_lines for m in domain_map.values())
        n = len(domains_with)
        estimated_saved = int(total_lines * (n - 1) / n)

        priority = "HIGH" if n >= 4 else "MEDIUM"
        details = []
        for dom in domains_with:
            m = domain_map[dom]
            arg_str = ", ".join(m.args)
            ret = f" → {m.returns}" if m.returns else ""
            details.append(f"  {dom}/loaders/data_loader_v2: `{m.name}({arg_str}){ret}` (~{m.body_lines} lines)")

        findings.append(PairityFinding(
            category="loader_gap",
            title=f"`{method_name}()` in {n} loaders but not in BaseDataLoader",
            priority=priority,
            domains_affected=domains_with,
            details=details,
            estimated_lines_saved=estimated_saved,
        ))

    findings.sort(key=lambda f: (-len(f.domains_affected), -f.estimated_lines_saved))
    return findings


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

PRIORITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
PRIORITY_EMOJI = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}


def _section(title: str, findings: List[PairityFinding], verbose: bool) -> List[str]:
    lines: List[str] = []
    if not findings:
        lines.append(f"### {title}\n\n_None found._\n")
        return lines

    lines.append(f"### {title}\n")
    sorted_findings = sorted(findings, key=lambda f: (PRIORITY_ORDER[f.priority], -f.estimated_lines_saved))

    for finding in sorted_findings:
        emoji = PRIORITY_EMOJI[finding.priority]
        saved = f" (~{finding.estimated_lines_saved} lines saved)" if finding.estimated_lines_saved else ""
        lines.append(f"**{emoji} {finding.priority}** — {finding.title}{saved}")
        lines.append(f"  - Domains: `{'`, `'.join(finding.domains_affected)}`")
        if verbose or finding.priority == "HIGH":
            for d in finding.details:
                lines.append(d)
        lines.append("")

    return lines


def write_report(
    method_overlaps: List[PairityFinding],
    file_names: List[PairityFinding],
    import_drifts: List[PairityFinding],
    module_funcs: List[PairityFinding],
    base_gaps: List[PairityFinding],
    loader_gaps: List[PairityFinding],
    domain_files: Dict[str, List[DomainFile]],
) -> None:
    all_findings = method_overlaps + file_names + import_drifts + module_funcs + base_gaps + loader_gaps
    high = sum(1 for f in all_findings if f.priority == "HIGH")
    medium = sum(1 for f in all_findings if f.priority == "MEDIUM")
    low_count = sum(1 for f in all_findings if f.priority == "LOW")
    total_saved = sum(f.estimated_lines_saved for f in all_findings)

    domain_stats = {
        d: sum(df.line_count for df in files)
        for d, files in domain_files.items()
    }
    total_lines = sum(domain_stats.values())

    lines: List[str] = [
        "# Structural Parity Report",
        "",
        "> Auto-generated by `scripts/audit/structural_parity.py`  ",
        "> Re-run after each consolidation session to track progress.",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total domain Python files | {sum(len(f) for f in domain_files.values())} |",
        f"| Total domain lines | {total_lines:,} |",
        f"| HIGH priority findings | {high} |",
        f"| MEDIUM priority findings | {medium} |",
        f"| LOW priority findings | {low_count} |",
        f"| Estimated lines removable | ~{total_saved:,} |",
        "",
        "## Per-domain file counts",
        "",
    ]
    for dom, lcount in sorted(domain_stats.items()):
        file_count = len(domain_files[dom])
        lines.append(f"- **{dom}**: {file_count} files, {lcount:,} lines")
    lines.append("")

    # --- Ranked consolidation targets ----------------------------------------
    lines.append("---")
    lines.append("")
    lines.append("## Consolidation Targets")
    lines.append("")
    lines.append("> Ordered by: priority → estimated lines saved")
    lines.append("")

    HIGH_label = "🔴 HIGH PRIORITY"
    lines.append(f"### {HIGH_label}")
    lines.append("")
    high_findings = sorted(
        [f for f in all_findings if f.priority == "HIGH"],
        key=lambda f: -f.estimated_lines_saved,
    )
    if not high_findings:
        lines.append("_None found._")
        lines.append("")
    for finding in high_findings:
        saved = f" (~{finding.estimated_lines_saved} lines saved)" if finding.estimated_lines_saved else ""
        lines.append(f"#### `[{finding.category}]` {finding.title}{saved}")
        lines.append(f"- Domains: `{'`, `'.join(finding.domains_affected)}`")
        for d in finding.details:
            lines.append(d)
        lines.append("")

    lines += _section("🟡 MEDIUM PRIORITY", [f for f in all_findings if f.priority == "MEDIUM"], VERBOSE)
    lines += _section("🟢 LOW PRIORITY", [f for f in all_findings if f.priority == "LOW"], VERBOSE)

    lines += [
        "---",
        "",
        "## Suggested Next Sessions",
        "",
        "Work through HIGH items in order. Contract per session:",
        "",
        "1. Read all N domain copies side-by-side",
        "2. Identify canonical (most callers, most complete)",
        "3. Identify divergences (meaningful vs drift?)",
        "4. Write to `shared/` with proper namespace",
        "5. Shim each domain's old path (one-liner re-export)",
        "6. Run full test suite — must be green",
        "7. Delete originals, commit as atomic unit",
        "8. Re-run `python3 scripts/audit/structural_parity.py`",
        "",
    ]

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {REPORT_PATH.relative_to(PROJECT_ROOT)}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print("Collecting domain files...")
    domain_files = collect_domain_files()

    total_files = sum(len(f) for f in domain_files.values())
    print(f"  {total_files} Python files across {len(domain_files)} domains")

    print("Analysing method overlaps...")
    method_overlaps = find_method_overlaps(domain_files)

    print("Analysing file name parity...")
    file_names = find_file_name_parity(domain_files)

    print("Analysing import drift...")
    import_drifts = find_import_drift(domain_files)

    print("Analysing module-level function patterns...")
    module_funcs = find_module_function_patterns(domain_files)

    print("Checking base coordinator coverage gaps...")
    base_gaps = find_base_class_gaps(domain_files)

    print("Checking BaseDataLoader coverage gaps...")
    loader_gaps = find_loader_base_gaps(domain_files)

    all_findings = method_overlaps + file_names + import_drifts + module_funcs + base_gaps + loader_gaps
    high = sum(1 for f in all_findings if f.priority == "HIGH")
    medium = sum(1 for f in all_findings if f.priority == "MEDIUM")

    print(f"\nFindings: {high} HIGH, {medium} MEDIUM, "
          f"{len(all_findings) - high - medium} LOW")

    write_report(
        method_overlaps, file_names, import_drifts,
        module_funcs, base_gaps, loader_gaps, domain_files,
    )


if __name__ == "__main__":
    main()
