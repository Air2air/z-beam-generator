#!/usr/bin/env python3
"""
Terminal Error Capture and Processing Script

This script captures terminal errors and processes them through the
TerminalErrorHandler to ensure systematic error handling, fixing,
documentation, and testing.
"""

import argparse
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.terminal_error_handler import get_error_handler, handle_terminal_error


def capture_from_stdin():
    """Capture error from stdin (useful for piping)"""
    error_text = sys.stdin.read().strip()
    if error_text:
        print("🔍 Processing terminal error from stdin...")
        analysis = handle_terminal_error(error_text)
        print_analysis_summary(analysis)
    else:
        print("❌ No error text provided via stdin")


def capture_from_file(file_path: str):
    """Capture error from a file"""
    try:
        with open(file_path, "r") as f:
            error_text = f.read().strip()

        if error_text:
            print(f"🔍 Processing terminal error from file: {file_path}")
            analysis = handle_terminal_error(error_text)
            print_analysis_summary(analysis)
        else:
            print(f"❌ No error text found in file: {file_path}")

    except FileNotFoundError:
        print(f"❌ Error file not found: {file_path}")
    except Exception as e:
        print(f"❌ Failed to read error file: {e}")


def capture_from_command(command: str):
    """Capture error from running a command"""
    import subprocess

    try:
        print(f"🔍 Running command and capturing errors: {command}")
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )

        error_text = result.stderr.strip()
        if error_text:
            print("❌ Command produced error output:")
            print(error_text)
            print("\n🔧 Processing error...")
            analysis = handle_terminal_error(error_text)
            print_analysis_summary(analysis)
        else:
            print("✅ Command completed without errors")

    except subprocess.TimeoutExpired:
        print("⏰ Command timed out")
    except Exception as e:
        print(f"❌ Failed to run command: {e}")


def print_analysis_summary(analysis):
    """Print a summary of the error analysis"""
    print("\n" + "=" * 60)
    print("📊 ERROR ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Timestamp: {analysis.timestamp}")
    print(f"Error Type: {analysis.error_type}")
    print(f"Severity: {analysis.severity.upper()}")

    if analysis.matched_pattern:
        print(f"Pattern: {analysis.matched_pattern.description}")

    print(f"Fixed: {'✅ Yes' if analysis.fixed else '❌ No'}")
    print(f"Documented: {'✅ Yes' if analysis.documented else '❌ No'}")
    print(f"Tested: {'✅ Yes' if analysis.tested else '❌ No'}")

    if analysis.suggested_fix:
        print(f"Suggested Fix: {analysis.suggested_fix}")

    if analysis.prevention_measures:
        print("Prevention Measures:")
        for measure in analysis.prevention_measures:
            print(f"  • {measure}")

    print("=" * 60)


def show_statistics():
    """Show error handling statistics"""
    handler = get_error_handler()
    stats = handler.get_error_statistics()

    print("\n" + "=" * 60)
    print("📈 ERROR HANDLING STATISTICS")
    print("=" * 60)
    print(f"Total Errors Processed: {stats['total_errors']}")
    print(".1f")
    print(".1f")
    print(".1f")

    if stats["error_types"]:
        print("\nError Types:")
        for error_type, count in stats["error_types"].items():
            print(f"  {error_type}: {count}")

    if stats["severities"]:
        print("\nSeverity Distribution:")
        for severity, count in stats["severities"].items():
            print(f"  {severity}: {count}")

    print("=" * 60)


def generate_report():
    """Generate a comprehensive error report"""
    handler = get_error_handler()
    report = handler.generate_error_report()

    # Save report to file
    report_file = Path("docs/TERMINAL_ERROR_REPORT.md")
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, "w") as f:
        f.write(report)

    print(f"📄 Error report generated: {report_file}")
    print("\n" + report)


def main():
    parser = argparse.ArgumentParser(
        description="Terminal Error Capture and Processing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Capture error from stdin (useful for piping)
  echo "ImportError: No module named 'requests'" | python capture_terminal_errors.py

  # Capture error from file
  python capture_terminal_errors.py --file error.log

  # Capture error from command
  python capture_terminal_errors.py --command "python -c 'import nonexistent'"

  # Show statistics
  python capture_terminal_errors.py --stats

  # Generate report
  python capture_terminal_errors.py --report
        """,
    )

    parser.add_argument("--file", "-f", help="Read error from file")

    parser.add_argument(
        "--command", "-c", help="Run command and capture its error output"
    )

    parser.add_argument(
        "--stats", "-s", action="store_true", help="Show error handling statistics"
    )

    parser.add_argument(
        "--report",
        "-r",
        action="store_true",
        help="Generate comprehensive error report",
    )

    args = parser.parse_args()

    # Handle different modes
    if args.stats:
        show_statistics()
    elif args.report:
        generate_report()
    elif args.file:
        capture_from_file(args.file)
    elif args.command:
        capture_from_command(args.command)
    else:
        # Default: capture from stdin
        if not sys.stdin.isatty():
            capture_from_stdin()
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
