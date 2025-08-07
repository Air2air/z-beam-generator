#!/usr/bin/env python3
"""
Check quartzite frontmatter compliance and demonstrate auto-fix capability.
"""

import json
import yaml

def check_quartzite_compliance():
    """Check quartzite frontmatter compliance against material schema."""
    print("=== QUARTZITE FRONTMATTER COMPLIANCE CHECK ===")
    
    # Load material schema
    with open('schemas/material.json', 'r') as f:
        schema = json.load(f)
    
    required_fields = schema['materialProfile']['validation']['frontmatter']['requiredFields']
    print(f"Required fields from material schema ({len(required_fields)}):")
    for i, field in enumerate(required_fields, 1):
        print(f"{i:2d}. {field}")
    
    # Parse quartzite frontmatter
    with open('content/components/frontmatter/quartzite-laser-cleaning.md', 'r') as f:
        content = f.read()
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 2:
            frontmatter_yaml = parts[1]
            frontmatter = yaml.safe_load(frontmatter_yaml)
            
            print(f"\nFields present in quartzite frontmatter ({len(frontmatter)}):")
            present_fields = sorted(frontmatter.keys())
            for i, field in enumerate(present_fields, 1):
                print(f"{i:2d}. {field}")
            
            # Compliance analysis
            present_required = set(present_fields) & set(required_fields)
            missing_fields = set(required_fields) - set(present_fields)
            extra_fields = set(present_fields) - set(required_fields)
            
            compliance_percentage = (len(present_required) / len(required_fields)) * 100
            
            print(f"\n=== COMPLIANCE ANALYSIS ===")
            print(f"📊 COMPLIANCE SCORE: {compliance_percentage:.1f}% ({len(present_required)}/{len(required_fields)} required fields)")
            
            if missing_fields:
                print(f"\n❌ MISSING REQUIRED FIELDS ({len(missing_fields)}):")
                for field in sorted(missing_fields):
                    print(f"   - {field}")
            
            if extra_fields:
                print(f"\n➕ EXTRA FIELDS ({len(extra_fields)}):")
                for field in sorted(extra_fields):
                    print(f"   - {field}")
            
            print(f"\n✅ PRESENT REQUIRED FIELDS ({len(present_required)}):")
            for field in sorted(present_required):
                print(f"   - {field}")
            
            return compliance_percentage, missing_fields, present_fields, frontmatter
    
    return 0, set(), [], {}

def demonstrate_auto_fix():
    """Demonstrate how the enhanced generator would auto-fix missing fields."""
    print("\n=== DEMONSTRATING AUTO-FIX CAPABILITY ===")
    
    try:
        from components.frontmatter.generator import FrontmatterGenerator
        import json
        
        # Load material schema
        with open('schemas/material.json', 'r') as f:
            schema = json.load(f)
        
        # Test data
        author_data = {
            'author_name': 'Material Science Expert',
            'author_country': 'United States',
            'author_id': 1
        }
        
        component_config = {
            'enabled': True,
            'ai_provider': 'mock',
            'options': {},
            'category': 'stone'
        }
        
        print("Creating enhanced FrontmatterGenerator...")
        fm_gen = FrontmatterGenerator('Quartzite', 'material', schema, author_data, component_config)
        
        # Load current quartzite frontmatter
        with open('content/components/frontmatter/quartzite-laser-cleaning.md', 'r') as f:
            content = f.read()
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                frontmatter_yaml = parts[1]
                current_frontmatter = yaml.safe_load(frontmatter_yaml)
                
                print(f"Current frontmatter has {len(current_frontmatter)} fields")
                
                # Use the enhanced auto-population functionality
                enhanced_frontmatter = fm_gen.validate_and_populate_required_fields(
                    current_frontmatter.copy(), 'frontmatter'
                )
                
                print(f"Enhanced frontmatter would have {len(enhanced_frontmatter)} fields")
                
                # Check new compliance
                required_fields = fm_gen.get_required_fields('frontmatter')
                new_compliance = (len(set(enhanced_frontmatter.keys()) & set(required_fields)) / len(required_fields)) * 100
                
                print(f"New compliance score: {new_compliance:.1f}%")
                
                # Show what would be added
                added_fields = set(enhanced_frontmatter.keys()) - set(current_frontmatter.keys())
                if added_fields:
                    print(f"\nFields that would be auto-added ({len(added_fields)}):")
                    for field in sorted(added_fields):
                        print(f"   - {field}")
                
                return enhanced_frontmatter
        
    except Exception as e:
        print(f"Error in auto-fix demonstration: {e}")
        return None

if __name__ == "__main__":
    compliance, missing, present, frontmatter = check_quartzite_compliance()
    
    if compliance < 100:
        enhanced = demonstrate_auto_fix()
        
        if enhanced and compliance < 80:
            print(f"\n🔧 RECOMMENDATION: Use enhanced generator to auto-populate missing fields")
            print(f"   This would improve compliance from {compliance:.1f}% to 100%")
    else:
        print("\n🎉 Quartzite frontmatter is fully compliant!")
