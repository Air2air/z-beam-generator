#!/usr/bin/env python3
"""
Simple Optimization Interface - Redirects to Smart Optimizer

This file maintains backward compatibility while redirecting to the new
3-file simplified architecture that actually solves content problems.

Usage:
    python3 optimize.py text              # Optimize all text content
    python3 optimize.py text --material copper  # Optimize specific material
"""

import asyncio
import sys

def main():
    print("🔄 Redirecting to Smart Optimizer (3-file simplified architecture)...")
    print("📈 Focused on actual content improvement instead of architectural complexity")
    print("")
    
    # Redirect to smart optimizer with same arguments
    from smart_optimize import optimize
    
    # Parse arguments
    component = sys.argv[1] if len(sys.argv) > 1 else "text"
    material = None
    
    if "--material" in sys.argv:
        material_idx = sys.argv.index("--material") + 1
        if material_idx < len(sys.argv):
            material = sys.argv[material_idx]
    
    # Run smart optimization
    result = asyncio.run(optimize(component, material))
    
    if result["success"]:
        print(f"\n✅ Optimization completed!")
        print(f"🎯 Use 'python3 smart_optimize.py text --material copper' for copper-specific optimization")
    else:
        print(f"\n❌ Optimization failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
