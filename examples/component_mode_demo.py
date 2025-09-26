#!/usr/bin/env python3
"""
Component Mode Demo

Example showing how to use the new component mode selection system.
"""

import argparse
import sys
import os
from typing import Dict, List, Optional

# Add the parent directory to the Python path to import run
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import COMPONENT_CONFIG
from utils.component_mode import get_component_mode, should_use_api
from generators.component_helpers import (
    get_required_api_components,
    preload_required_apis,
    optimize_component_ordering
)


def demo_component_modes(material_name: str, component_types: Optional[List[str]] = None):
    """
    Demonstrate the component mode selection system.
    
    Args:
        material_name: Name of the material to generate content for
        component_types: List of component types to generate, or None for all
    """
    print("\n🔍 Component Mode Selection Demo")
    print("=" * 60)
    
    # Use all components if none specified
    if not component_types:
        component_types = list(COMPONENT_CONFIG.keys())
    
    print(f"📋 Components to generate: {', '.join(component_types)}")
    
    # Determine required APIs
    required_apis = preload_required_apis(component_types)
    print(f"\n🔌 Required API providers:")
    if required_apis:
        for component, provider in required_apis.items():
            print(f"   • {component}: {provider}")
    else:
        print("   • None required (all static components)")
    
    # Optimize component ordering
    optimized_order = optimize_component_ordering(component_types)
    print(f"\n📊 Optimized generation order:")
    for i, component in enumerate(optimized_order, 1):
        config = COMPONENT_CONFIG.get(component, {})
        mode = config.get("data_provider", "static")
        api = config.get("api_provider", "none")
        print(f"   {i}. {component} - Mode: {mode}, API: {api}")
    
    print("\n🔄 Production Mode: Component Analysis")
    print("=" * 60)
    
    # Production note: Real API clients would be created here based on configuration
    # No mock clients allowed in production or demo code
    
    for component in optimized_order:
        config = COMPONENT_CONFIG.get(component, {})
        api_provider = config.get("api_provider", "none")
        
        # In production, real API clients would be instantiated here
        has_real_api = api_provider != "none"
        
        # Get component mode
        mode = get_component_mode(component, has_real_api)  # Modified to use boolean
        should_use_api_result = should_use_api(component, has_real_api)  # Modified to use boolean
        
        print(f"\n🔧 Processing: {component}")
        print(f"   📋 Configuration:")
        print(f"      • data_provider: {config.get('data_provider', 'static')}")
        print(f"      • api_provider: {api_provider}")
        print(f"   🔍 Decision:")
        print(f"      • Mode: {mode}")
        print(f"      • Use API: {'Yes' if should_use_api_result else 'No'}")
        print(f"      • API Available: {'Yes' if has_real_api else 'No'}")
        
        # Show what would happen in the real generation process
        if should_use_api_result:
            print(f"   ✅ Would use hybrid generation with API enhancement")
        elif mode == "static":
            print(f"   ✅ Would use static generation without API")
        elif mode == "frontmatter":
            print(f"   ✅ Would extract data from frontmatter without API")
        else:
            print(f"   ⚠️  Would fall back to static generation (API not available)")


def main():
    """Command line interface for the demo."""
    parser = argparse.ArgumentParser(description="Component Mode Demo")
    parser.add_argument("--material", "-m", default="Titanium", help="Material name")
    parser.add_argument("--components", "-c", help="Comma-separated list of components")
    
    args = parser.parse_args()
    
    component_list = None
    if args.components:
        component_list = [c.strip() for c in args.components.split(",")]
    
    demo_component_modes(args.material, component_list)


if __name__ == "__main__":
    main()
