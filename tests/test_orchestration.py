#!/usr/bin/env python3
"""
Test Component Orchestration Order

Verify that components are generated in the correct order, specifically ensuring
that propertiestable comes after frontmatter so it can access frontmatter data.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from run import COMPONENT_CONFIG


def test_orchestration_order():
    """Test that the orchestration order is properly defined and logical"""
    print("🎯 TESTING COMPONENT ORCHESTRATION ORDER")
    print("=" * 60)
    
    orchestration_order = COMPONENT_CONFIG.get("orchestration_order", [])
    components_config = COMPONENT_CONFIG.get("components", {})
    
    print("📋 Defined orchestration order:")
    for i, component in enumerate(orchestration_order, 1):
        print(f"   {i:2d}. {component}")
    
    # Test key dependencies
    print("\n🔍 DEPENDENCY ANALYSIS:")
    
    # Test 1: frontmatter should come before propertiestable
    frontmatter_pos = orchestration_order.index('frontmatter') if 'frontmatter' in orchestration_order else -1
    propertiestable_pos = orchestration_order.index('propertiestable') if 'propertiestable' in orchestration_order else -1
    
    if frontmatter_pos != -1 and propertiestable_pos != -1:
        if frontmatter_pos < propertiestable_pos:
            print("   ✅ frontmatter → propertiestable: CORRECT ORDER")
        else:
            print("   ❌ frontmatter → propertiestable: WRONG ORDER")
    else:
        print("   ⚠️ frontmatter or propertiestable not found in orchestration order")
    
    # Test 2: frontmatter should come before badgesymbol
    badgesymbol_pos = orchestration_order.index('badgesymbol') if 'badgesymbol' in orchestration_order else -1
    
    if frontmatter_pos != -1 and badgesymbol_pos != -1:
        if frontmatter_pos < badgesymbol_pos:
            print("   ✅ frontmatter → badgesymbol: CORRECT ORDER")
        else:
            print("   ❌ frontmatter → badgesymbol: WRONG ORDER")
    else:
        print("   ⚠️ frontmatter or badgesymbol not found in orchestration order")
    
    # Test 3: static components should come early
    static_components = [comp for comp, config in components_config.items() 
                        if config.get("api_provider") == "none"]
    
    print(f"\n📊 Static components (api_provider='none'): {static_components}")
    
    for component in static_components:
        if component in orchestration_order:
            pos = orchestration_order.index(component)
            print(f"   {component}: position {pos + 1}")
    
    # Test 4: All configured components should be in orchestration order
    missing_components = set(components_config.keys()) - set(orchestration_order)
    if missing_components:
        print(f"\n⚠️ Components missing from orchestration order: {missing_components}")
    else:
        print("\n✅ All configured components are in orchestration order")
    
    return frontmatter_pos < propertiestable_pos if frontmatter_pos != -1 and propertiestable_pos != -1 else False


def test_component_order_simulation():
    """Simulate component generation order"""
    print("\n🎭 COMPONENT ORDER SIMULATION")
    print("=" * 60)
    
    # Simulate the ordering logic from run.py
    components = ["propertiestable", "content", "frontmatter", "badgesymbol", "author", "bullets"]
    
    print(f"Input components (random order): {components}")
    
    # Apply the same ordering logic as in run.py
    components_config = COMPONENT_CONFIG.get("components", {})
    orchestration_order = COMPONENT_CONFIG.get("orchestration_order", [])

    # Filter enabled components
    enabled_components = []
    for component in components:
        if component in components_config and components_config[component]["enabled"]:
            enabled_components.append(component)

    # Order according to orchestration_order
    ordered_components = []
    
    # First, add components in the defined orchestration order
    for component in orchestration_order:
        if component in enabled_components:
            ordered_components.append(component)
    
    # Then add any remaining enabled components
    for component in enabled_components:
        if component not in ordered_components:
            ordered_components.append(component)
    
    print(f"Ordered components: {ordered_components}")
    
    # Verify frontmatter comes before propertiestable
    if 'frontmatter' in ordered_components and 'propertiestable' in ordered_components:
        frontmatter_idx = ordered_components.index('frontmatter')
        propertiestable_idx = ordered_components.index('propertiestable')
        
        if frontmatter_idx < propertiestable_idx:
            print("✅ SUCCESS: frontmatter will be generated before propertiestable")
        else:
            print("❌ FAILURE: propertiestable would be generated before frontmatter")
        
        print(f"   frontmatter position: {frontmatter_idx + 1}")
        print(f"   propertiestable position: {propertiestable_idx + 1}")
    
    return ordered_components


def test_real_world_scenario():
    """Test with a realistic generation scenario"""
    print("\n🌍 REAL-WORLD SCENARIO TEST")
    print("=" * 60)
    
    # Typical material generation request - all components
    all_components = list(COMPONENT_CONFIG.get("components", {}).keys())
    
    print(f"Generating all components for a material: {all_components}")
    
    # Apply ordering
    components_config = COMPONENT_CONFIG.get("components", {})
    orchestration_order = COMPONENT_CONFIG.get("orchestration_order", [])

    enabled_components = [comp for comp in all_components 
                         if components_config.get(comp, {}).get("enabled", True)]
    
    ordered_components = []
    for component in orchestration_order:
        if component in enabled_components:
            ordered_components.append(component)
    
    for component in enabled_components:
        if component not in ordered_components:
            ordered_components.append(component)
    
    print("\n📋 Generation order:")
    for i, component in enumerate(ordered_components, 1):
        api_provider = components_config.get(component, {}).get("api_provider", "unknown")
        component_type = "Static" if api_provider == "none" else f"API ({api_provider})"
        print(f"   {i:2d}. {component:<15} [{component_type}]")
    
    # Verify that static components that depend on frontmatter come after frontmatter
    frontmatter_idx = ordered_components.index('frontmatter') if 'frontmatter' in ordered_components else -1
    
    dependent_components = ['propertiestable', 'badgesymbol']
    for dep_component in dependent_components:
        if dep_component in ordered_components:
            dep_idx = ordered_components.index(dep_component)
            if frontmatter_idx != -1 and dep_idx > frontmatter_idx:
                print(f"   ✅ {dep_component} correctly positioned after frontmatter")
            else:
                print(f"   ❌ {dep_component} incorrectly positioned before frontmatter")
    
    return ordered_components


def main():
    """Run orchestration order tests"""
    print("🧪 COMPONENT ORCHESTRATION ORDER TESTS")
    print("=" * 60)
    
    # Test 1: Basic orchestration order
    order_correct = test_orchestration_order()
    
    # Test 2: Simulate component ordering
    simulated_order = test_component_order_simulation()
    
    # Test 3: Real-world scenario
    real_world_order = test_real_world_scenario()
    
    print("\n" + "=" * 60)
    print("🎯 ORCHESTRATION TEST RESULTS")
    print("=" * 60)
    
    if order_correct:
        print("✅ Orchestration order is correctly configured")
        print("✅ frontmatter will be generated before propertiestable")
        print("✅ Static components can access frontmatter data")
    else:
        print("❌ Orchestration order needs adjustment")
        print("❌ propertiestable may not have access to frontmatter data")
    
    print("\n💡 KEY BENEFITS:")
    print("   • frontmatter generates data first")
    print("   • propertiestable extracts from frontmatter data")
    print("   • badgesymbol extracts from frontmatter data")
    print("   • No API calls needed for static components")
    print("   • Consistent data flow and dependencies")
    
    return order_correct


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
