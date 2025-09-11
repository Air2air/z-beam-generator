#!/usr/bin/env python3
"""
Z-Beam CLI Configuration Display

This module contains configuration display functionality for the Z-Beam CLI.
Extracted from the main run.py file for better organization.
"""


def show_configuration():
    """Show current configuration."""
    print("⚙️  Z-Beam Configuration:")
    from cli.component_config import show_component_configuration

    show_component_configuration()
