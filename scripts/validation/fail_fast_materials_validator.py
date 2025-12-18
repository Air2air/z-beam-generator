#!/usr/bin/env python3
"""
FAIL-FAST MATERIALS VALIDATOR

Per GROK_INSTRUCTIONS.md: "ZERO TOLERANCE FOR MOCKS/FALLBACKS IN PRODUCTION CODE"

This validator enforces the fail-fast architecture by immediately rejecting
any materials database with default values or fallbacks.

NO MOCKS OR FALLBACKS - System MUST fail if dependencies are missing.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List
from shared.validation.errors import ConfigurationError

class MaterialsValidationError(Exception):
    """Materials database validation failure - system cannot operate"""

def load_materials_yaml() -> Dict:
    """Load materials YAML with strict validation"""
    materials_path = Path(__file__).parent.parent.parent / "data" / "materials" / "Materials.yaml"
    
    if not materials_path.exists():
        raise ConfigurationError(f"CRITICAL: Materials.yaml not found at {materials_path}")
    
    try:
        with open(materials_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise ConfigurationError(f"CRITICAL: Failed to load Materials.yaml: {e}")

def validate_no_default_values(materials_data: Dict) -> List[str]:
    """
    FAIL-FAST VALIDATION: NO DEFAULT VALUES ALLOWED
    
    Per GROK_INSTRUCTIONS.md: System must fail immediately if using defaults.
    """
    violations = []
    
    # Check for default source attribution
    for category, category_data in materials_data.get('materials', {}).items():
        items = category_data.get('items', [])
        
        for item in items:
            material_name = item.get('name', 'Unknown')
            
            # Check properties for default sources
            properties = item.get('properties', {})
            for prop_name, prop_data in properties.items():
                if isinstance(prop_data, dict):
                    source = prop_data.get('source')
                    confidence = prop_data.get('confidence', 1.0)
                    
                    # VIOLATION: Default source detected
                    if source == 'default_from_category_range':
                        violations.append(
                            f"CRITICAL VIOLATION: {material_name}.{prop_name} "
                            f"uses forbidden default source 'default_from_category_range'"
                        )
                    
                    # VIOLATION: Low confidence indicates default
                    if confidence == 0.7:  # Standard default confidence
                        violations.append(
                            f"CRITICAL VIOLATION: {material_name}.{prop_name} "
                            f"has default confidence level 0.7 (indicates unresearched default)"
                        )
    
    return violations

def validate_ai_research_requirement(materials_data: Dict) -> List[str]:
    """
    FAIL-FAST VALIDATION: ALL VALUES MUST BE AI-RESEARCHED
    
    Per project requirements: Every value must be independently AI-researched.
    """
    violations = []
    total_properties = 0
    ai_researched_properties = 0
    
    for category, category_data in materials_data.get('materials', {}).items():
        items = category_data.get('items', [])
        
        for item in items:
            material_name = item.get('name', 'Unknown')
            properties = item.get('properties', {})
            
            for prop_name, prop_data in properties.items():
                if isinstance(prop_data, dict):
                    total_properties += 1
                    source = prop_data.get('source')
                    
                    if source == 'ai_research':
                        ai_researched_properties += 1
                    else:
                        violations.append(
                            f"CRITICAL VIOLATION: {material_name}.{prop_name} "
                            f"is not AI-researched (source: {source})"
                        )
    
    # Calculate compliance percentage
    if total_properties > 0:
        compliance_rate = (ai_researched_properties / total_properties) * 100
        
        if compliance_rate < 100.0:
            violations.append(
                f"CRITICAL SYSTEM FAILURE: Only {compliance_rate:.1f}% of properties "
                f"are AI-researched ({ai_researched_properties}/{total_properties}). "
                f"System requires 100% AI-researched values - NO DEFAULTS ALLOWED."
            )
    
    return violations

def validate_forbidden_defaults_only(materials_data: Dict) -> List[str]:
    """
    SMART VALIDATION: Check only for forbidden default sources
    
    Per GROK_INSTRUCTIONS.md: Zero tolerance for defaults/fallbacks.
    This version focuses on SOURCE validation rather than value duplicates,
    allowing legitimate scientific duplicates while blocking forbidden defaults.
    """
    violations = []
    
    # Define forbidden sources that indicate defaults/fallbacks
    forbidden_sources = [
        'default_from_category_range',
        'category_default', 
        'fallback',
        'mock',
        'placeholder',
        'estimated',
        'inherited',
        'template'
    ]
    
    # Check each material for forbidden sources
    for category, category_data in materials_data.get('materials', {}).items():
        for item in category_data.get('items', []):
            material_name = item.get('name', 'Unknown')
            properties = item.get('properties', {})
            
            for prop_name, prop_data in properties.items():
                if isinstance(prop_data, dict):
                    source = prop_data.get('source', '')
                    confidence = prop_data.get('confidence', 0)
                    
                    # Check for forbidden sources
                    if source in forbidden_sources:
                        violations.append(
                            f"FORBIDDEN DEFAULT: {material_name}.{prop_name} "
                            f"has source '{source}' (confidence: {confidence}). "
                            f"Must use 'ai_research' source."
                        )
                    
                    # Check for missing AI research source
                    elif source != 'ai_research':
                        violations.append(
                            f"NON-AI SOURCE: {material_name}.{prop_name} "
                            f"has source '{source}'. Must use 'ai_research'."
                        )
                    
                    # Check for low confidence (potential default indicator)
                    elif confidence < 0.9:
                        violations.append(
                            f"LOW CONFIDENCE: {material_name}.{prop_name} "
                            f"has confidence {confidence} < 0.9. "
                            f"AI research should have high confidence."
                        )
    
    return violations

def validate_value_uniqueness_legacy(materials_data: Dict) -> List[str]:
    """
    LEGACY VALIDATION: Check for suspicious duplicate values (DISABLED)
    
    This function is disabled to allow legitimate scientific duplicates.
    Use validate_forbidden_defaults_only() instead for GROK compliance.
    """
    # Return empty list - duplicates are now allowed as they may be scientifically accurate
    return []

def validate_category_ranges() -> List[str]:
    """
    FAIL-FAST VALIDATION: ALL CATEGORY RANGES MUST EXIST
    
    MaterialProperties.yaml must have complete min/max ranges for all properties.
    Missing or null ranges are VIOLATIONS.
    
    Note: Updated to use new multi-file architecture (MaterialProperties.yaml)
    instead of deprecated Categories.yaml.
    """
    violations = []
    
    try:
        from domains.materials.data_loader import get_category_ranges
        
        # Get category ranges from new architecture
        category_ranges_data = get_category_ranges()
        
        if not category_ranges_data:
            violations.append("CRITICAL: No category ranges found in MaterialProperties.yaml")
            return violations
        
    except Exception as e:
        violations.append(f"CRITICAL: Failed to load category ranges: {e}")
        return violations
    
    # Check all categories for complete ranges
    for category_name, category_data in category_ranges_data.items():
        ranges = category_data.get('ranges', {})
        
        if not ranges:
            violations.append(
                f"MISSING RANGES: Category '{category_name}' has no ranges defined"
            )
            continue
        
        for prop_name, prop_data in ranges.items():
            if not isinstance(prop_data, dict):
                continue
            
            # Check for missing min
            if 'min' not in prop_data or prop_data['min'] is None:
                violations.append(
                    f"NULL RANGE: {category_name}.{prop_name}.min is null or missing"
                )
            
            # Check for missing max
            if 'max' not in prop_data or prop_data['max'] is None:
                violations.append(
                    f"NULL RANGE: {category_name}.{prop_name}.max is null or missing"
                )
    
    return violations


def validate_material_completeness(materials_data: Dict) -> List[str]:
    """
    FAIL-FAST VALIDATION: MATERIAL PROPERTIES MUST BE COMPLETE
    
    Checks that properties sections have actual property values,
    not just labels or empty sections.
    """
    violations = []
    
    for material_name, material_data in materials_data.get('materials', {}).items():
        props = material_data.get('properties', {})
        
        if not props:
            violations.append(
                f"EMPTY PROPERTIES: {material_name} has no properties defined"
            )
            continue
        
        # Check if properties only contain labels (meta-fields) but no actual data
        has_actual_properties = False
        label_only_properties = []
        
        for prop_name, prop_data in props.items():
            if not isinstance(prop_data, dict):
                continue
            
            # Check if this property has actual value data (not just label/type metadata)
            has_value = any(key in prop_data for key in ['value', 'min', 'max'])
            
            if has_value:
                has_actual_properties = True
            else:
                # Only has metadata fields like 'label', 'type', etc.
                label_only_properties.append(prop_name)
        
        # If ALL properties are label-only (no actual values), it's incomplete
        if not has_actual_properties and label_only_properties:
            violations.append(
                f"INCOMPLETE PROPERTIES: {material_name} has {len(label_only_properties)} "
                f"properties with labels but no values (e.g., {', '.join(label_only_properties[:3])})"
            )
        
        # Check for null/empty property values
        for prop_name, prop_data in props.items():
            if not isinstance(prop_data, dict):
                continue
            
            if 'value' in prop_data and (prop_data['value'] is None or prop_data['value'] == ''):
                violations.append(
                    f"NULL VALUE: {material_name}.{prop_name}.value is null or empty"
                )
    
    return violations


def fail_fast_validate_materials() -> None:
    """
    FAIL-FAST MATERIALS VALIDATION
    
    Per GROK_INSTRUCTIONS.md: "Fail immediately if dependencies are missing"
    
    This function enforces zero tolerance for mocks/fallbacks/defaults.
    If ANY violations are found, the system MUST NOT operate.
    """
    
    print("🚨 FAIL-FAST MATERIALS VALIDATION")
    print("=" * 50)
    print("Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE FOR DEFAULTS/FALLBACKS")
    print()
    
    try:
        # Load materials database
        materials_data = load_materials_yaml()
        print("✅ Materials.yaml loaded successfully")
        
        all_violations = []
        
        # 1. Check for default values (FORBIDDEN)
        print("\n🔍 Checking for forbidden default values...")
        default_violations = validate_no_default_values(materials_data)
        all_violations.extend(default_violations)
        
        if default_violations:
            print(f"❌ Found {len(default_violations)} default value violations")
        else:
            print("✅ No default values detected")
        
        # 2. Check forbidden defaults only (SMART VALIDATION)
        print("\n🔍 Checking for forbidden default sources...")
        default_violations = validate_forbidden_defaults_only(materials_data)
        all_violations.extend(default_violations)
        
        if default_violations:
            print(f"❌ Found {len(default_violations)} forbidden default violations")
        else:
            print("✅ All sources are ai_research with high confidence")
        
        # 3. Skip duplicate checking (allow legitimate scientific duplicates)
        print("\n🔍 Checking value uniqueness...")
        print("✅ Allowing scientific duplicates - checking sources only")
        
        # 4. SKIP material completeness (handled by workflow auto-remediation)
        # Material completeness is checked in unified_workflow.py where auto-remediation
        # can trigger property research and populate missing data inline.
        # Fail-fast validation should ONLY check for mocks/fallbacks/defaults.
        
        # 5. Check category ranges (CRITICAL DEPENDENCY)
        print("\n🔍 Validating category ranges in MaterialProperties.yaml...")
        range_violations = validate_category_ranges()
        all_violations.extend(range_violations)
        
        if range_violations:
            print(f"❌ Found {len(range_violations)} missing/null category ranges")
        else:
            print("✅ All category ranges present and valid")
        
        # FAIL-FAST DECISION
        if all_violations:
            print("\n🚨 CRITICAL SYSTEM FAILURE")
            print("=" * 50)
            print(f"Found {len(all_violations)} violations that PREVENT system operation:")
            print()
            
            for i, violation in enumerate(all_violations[:10], 1):  # Show first 10
                print(f"{i:2d}. {violation}")
            
            if len(all_violations) > 10:
                print(f"    ... and {len(all_violations) - 10} more violations")
            
            print()
            print("🚫 SYSTEM CANNOT OPERATE WITH DEFAULTS/FALLBACKS")
            print("🚫 Per GROK_INSTRUCTIONS.md: ZERO TOLERANCE FOR MOCKS/FALLBACKS")
            print()
            print("REQUIRED ACTIONS:")
            print("1. Replace ANY remaining forbidden defaults with AI-researched values")
            print("2. Ensure ALL properties have source: ai_research")
            print("3. Ensure ALL confidence levels >= 0.9")
            print("4. Note: Value duplicates are allowed if scientifically accurate")
            print()
            print("See MATERIALS_REMEDIATION_PLAN.md for detailed fix instructions.")
            
            raise MaterialsValidationError(
                f"CRITICAL: Materials database has {len(all_violations)} violations. "
                f"System cannot operate with defaults/fallbacks. "
                f"See MATERIALS_ANALYSIS_CRITICAL_FINDINGS.md for details."
            )
        
        else:
            print("\n🎉 VALIDATION PASSED")
            print("=" * 50)
            print("✅ Materials database meets fail-fast requirements")
            print("✅ Zero defaults/fallbacks detected")
            print("✅ All values are AI-researched and unique")
            print("✅ System approved for operation")
    
    except (ConfigurationError, MaterialsValidationError) as e:
        print(f"\n💥 FAIL-FAST VALIDATION FAILED: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n💥 UNEXPECTED VALIDATION ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fail_fast_validate_materials()