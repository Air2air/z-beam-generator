#!/usr/bin/env python3
"""Compatibility wrapper for the legacy CLI entrypoint."""

from shared.config.settings import API_PROVIDERS, COMPONENT_CONFIG
from legacy.run import main


if __name__ == '__main__':
    main()
