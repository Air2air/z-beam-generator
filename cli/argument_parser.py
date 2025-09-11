#!/usr/bin/env python3
"""
Z-Beam CLI Argument Parser

This module contains the argument parsing logic for the Z-Beam CLI.
Extracted from the main run.py file for better organization.
"""

import argparse


def create_argument_parser():
    """Create and configure the argument parser for Z-Beam CLI."""
    parser = argparse.ArgumentParser(description="Z-Beam Content Generator")

    # Core generation commands
    parser.add_argument(
        "--material", "-m", help="Generate content for specific material"
    )
    parser.add_argument(
        "--components", "-c", help="Comma-separated list of components to generate (e.g., 'frontmatter,text,metatags')"
    )
    parser.add_argument(
        "--all", action="store_true", help="Generate content for all materials"
    )
    parser.add_argument(
        "--content-batch",
        action="store_true",
        help="Clear and regenerate content for first 8 categories",
    )

    # Testing and validation
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run comprehensive test suite (all unit, integration, and e2e tests)",
    )
    parser.add_argument(
        "--test-api",
        action="store_true",
        help="Test API connectivity and configuration",
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate generated content structure"
    )
    parser.add_argument(
        "--list-materials", action="store_true", help="List all available materials"
    )

    # Optimization commands
    parser.add_argument(
        "--optimize", help="Optimize content for a component (e.g., 'text', 'bullets')"
    )

    # Cleanup commands
    parser.add_argument(
        "--clean", action="store_true", help="Clean all generated content files"
    )
    parser.add_argument(
        "--cleanup-scan",
        action="store_true",
        help="Scan for cleanup opportunities (dry-run)",
    )
    parser.add_argument(
        "--cleanup-report",
        action="store_true",
        help="Generate comprehensive cleanup report",
    )
    parser.add_argument(
        "--root-cleanup",
        action="store_true",
        help="Clean up and organize root directory",
    )

    # Configuration and info
    parser.add_argument(
        "--config", action="store_true", help="Show current configuration"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status and component availability",
    )
    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Show API client cache performance statistics",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear API client cache to force fresh connections",
    )
    parser.add_argument(
        "--preload-cache",
        action="store_true",
        help="Preload API clients into cache for better performance",
    )
    parser.add_argument(
        "--no-persistent-cache",
        action="store_true",
        help="Disable persistent caching (not recommended, reduces performance)",
    )
    parser.add_argument(
        "--cache-info",
        action="store_true",
        help="Show detailed information about cached API clients",
    )
    parser.add_argument(
        "--version-history",
        help="Show version history for a material-component pair (format: material:component)",
    )

    # Options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    return parser


def show_help():
    """Show help/usage information."""
    print("🎯 Z-Beam Generator - AI-Powered Content Generation")
    print("=" * 55)
    print()
    print("EXAMPLES:")
    print("  python3 run.py --material \"Copper\"     # Generate specific material")
    print("  python3 run.py --all                   # Generate all materials")
    print()
    print("QUICK START:")
    print("  python3 run.py --material \"Aluminum\"   # Specific material")
    print("  python3 run.py --all                   # All materials")
    print()
    print("🧪 TESTING & VALIDATION:")
    print("  python3 run.py --test                  # Run comprehensive test suite")
    print("  python3 run.py --test-api              # Test API")
    print("  python3 run.py --validate              # Validate content")
    print("  python3 run.py --list-materials        # List materials")
    print()
    print("⚙️  CONFIGURATION:")
    print("  python3 run.py --config                # Show config")
    print("  python3 run.py --status                # System status")
    print("  python3 run.py --cache-stats           # Cache performance")
    print("  python3 run.py --clear-cache           # Clear API cache")
    print("  python3 run.py --preload-cache         # Preload cache")
    print()
    print("📋 VERSION TRACKING:")
    print(
        "  python3 run.py --version-history 'Alumina:text'  # Show version history"
    )
    print()
    print("🧹 CLEANUP:")
    print("  python3 run.py --clean                 # Clean content")
    print("  python3 run.py --cleanup-scan          # Scan cleanup")
    print("  python3 run.py --cleanup-report        # Cleanup report")
    print()
    print("🚀 OPTIMIZATION:")
    print("  python3 run.py --optimize text         # Optimize text")
    print()
    print("💡 TIP: Use --help for complete command reference")
