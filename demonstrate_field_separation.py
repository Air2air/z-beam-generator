#!/usr/bin/env python3
"""
Field Separation Demonstration

Shows how the text vs non-text field separation system works
with real frontmatter data from the Z-Beam Generator.
"""

import sys
from pathlib import Path
import yaml
from typing import Dict, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from components.frontmatter.core.text_field_classifier import TextFieldClassifier, FieldType


def load_sample_frontmatter() -> Dict[str, Any]:
    """Load a real frontmatter file for demonstration"""
    frontmatter_path = Path(__file__).parent.parent / "content" / "components" / "frontmatter"
    
    # Try to load aluminum frontmatter
    aluminum_file = frontmatter_path / "aluminum-laser-cleaning.yaml"
    if aluminum_file.exists():
        with open(aluminum_file, 'r') as f:
            return yaml.safe_load(f)
    
    # Fallback to synthetic data
    return {
        'name': 'Aluminum',
        'category': 'Metal',
        'title': 'Aluminum Laser Cleaning',
        'subtitle': 'Advanced laser cleaning parameters for aluminum surfaces',
        'description': 'Comprehensive guide for aluminum laser cleaning operations',
        
        'materialProperties': {
            'laser_material_interaction': {
                'properties': {
                    'thermalConductivity': {
                        'value': 237.0,
                        'unit': 'W/(m·K)',
                        'confidence': 95,
                        'description': 'Excellent thermal conductor enabling efficient heat dissipation',
                        'validation_method': 'Measured using ASTM E1461 standard methodology'
                    },
                    'laserReflectivity': {
                        'value': 0.92,
                        'unit': '',
                        'confidence': 88,
                        'description': 'High reflectivity requires careful power management',
                        'min': 0.85,
                        'max': 0.95
                    }
                }
            }
        },
        
        'machineSettings': {
            'powerRange': {
                'value': 100,
                'unit': 'W',
                'min': 50,
                'max': 200,
                'confidence': 92,
                'description': 'Optimal power range for aluminum cleaning',
                'notes': 'Adjust based on oxide layer thickness and surface condition'
            },
            'frequency': {
                'value': 20000,
                'unit': 'Hz',
                'min': 15000,
                'max': 25000,
                'description': 'Standard frequency for aluminum processing'
            }
        },
        
        'applications': ['Automotive', 'Aerospace', 'Electronics Manufacturing'],
        'safety_notes': 'Mandatory eye protection required due to high reflectivity',
        'technical_notes': 'Optimize settings based on oxide layer thickness',
        
        'author': {
            'id': 4,
            'name': 'Todd Dunning',
            'country': 'United States (California)'
        },
        
        'created_at': '2025-10-22T14:30:00Z',
        'version': '2.1.0'
    }


def demonstrate_field_classification():
    """Demonstrate the field classification system"""
    print("🔍 Field Classification System Demonstration")
    print("=" * 60)
    
    # Load sample data
    frontmatter = load_sample_frontmatter()
    classifier = TextFieldClassifier()
    
    print(f"📄 Sample Material: {frontmatter.get('name', 'Unknown')}")
    print(f"📊 Total Fields: {len(frontmatter)}")
    print()
    
    # Get classification summary
    summary = classifier.get_generation_summary(frontmatter)
    
    print("📈 Field Distribution:")
    print(f"  📝 Text Fields (AI Generation):     {summary['text_fields']:3d} ({summary['text_fields']/summary['total_fields']*100:5.1f}%)")
    print(f"  🔢 Data Fields (Materials.yaml):    {summary['data_fields']:3d} ({summary['data_fields']/summary['total_fields']*100:5.1f}%)")
    print(f"  🔗 Hybrid Fields (Mixed):           {summary['hybrid_fields']:3d} ({summary['hybrid_fields']/summary['total_fields']*100:5.1f}%)")
    print(f"  🏷️  Metadata Fields (System):        {summary['metadata_fields']:3d} ({summary['metadata_fields']/summary['total_fields']*100:5.1f}%)")
    print(f"  📋 Total:                           {summary['total_fields']:3d}")
    print()
    
    # Show field separation
    text_fields, data_fields, hybrid_fields, metadata_fields = \
        classifier.separate_fields_by_type(frontmatter)
    
    print("📝 TEXT FIELDS (Require AI Generation):")
    print("   These fields need author voice and creative content generation")
    for field_path, value in text_fields.items():
        value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
        print(f"   • {field_path}: {value_preview}")
    print()
    
    print("🔢 DATA FIELDS (From Materials.yaml):")
    print("   These fields are populated directly from structured data")
    for field_path, value in data_fields.items():
        print(f"   • {field_path}: {value}")
    print()
    
    print("🔗 HYBRID FIELDS (Structured + Text):")
    print("   These fields contain both data and text descriptions")
    for field_path, value in hybrid_fields.items():
        if isinstance(value, dict):
            print(f"   • {field_path}: [dict with {len(value)} keys]")
        else:
            print(f"   • {field_path}: {value}")
    print()
    
    print("🏷️ METADATA FIELDS (System Generated):")
    print("   These fields are managed by the system")
    for field_path, value in metadata_fields.items():
        print(f"   • {field_path}: {value}")
    print()


def demonstrate_nested_classification():
    """Show detailed nested field classification"""
    print("🔍 Detailed Nested Field Classification")
    print("=" * 60)
    
    frontmatter = load_sample_frontmatter()
    classifier = TextFieldClassifier()
    
    # Get all field classifications including nested
    classifications = classifier.classify_frontmatter_structure(frontmatter)
    
    # Group by type
    by_type = {
        FieldType.TEXT: [],
        FieldType.DATA: [],
        FieldType.HYBRID: [],
        FieldType.METADATA: []
    }
    
    for field_path, field_type in classifications.items():
        by_type[field_type].append(field_path)
    
    # Show each type with details
    type_names = {
        FieldType.TEXT: "📝 TEXT FIELDS",
        FieldType.DATA: "🔢 DATA FIELDS", 
        FieldType.HYBRID: "🔗 HYBRID FIELDS",
        FieldType.METADATA: "🏷️ METADATA FIELDS"
    }
    
    for field_type, field_paths in by_type.items():
        if field_paths:
            print(f"{type_names[field_type]} ({len(field_paths)} total):")
            for path in sorted(field_paths):
                print(f"   • {path}")
            print()


def demonstrate_processing_simulation():
    """Simulate processing pipeline performance"""
    print("⚡ Processing Pipeline Performance Simulation")
    print("=" * 60)
    
    frontmatter = load_sample_frontmatter()
    classifier = TextFieldClassifier()
    
    # Get field counts
    text_fields = classifier.get_text_fields(frontmatter)
    data_fields = classifier.get_data_fields(frontmatter)
    
    print("🎯 Processing Efficiency Analysis:")
    print()
    
    # Simulate TEXT field processing (AI generation)
    text_count = len(text_fields)
    estimated_ai_time = text_count * 8.0  # 8 seconds per field average
    estimated_ai_cost = text_count * 0.025  # $0.025 per field average
    
    print("📝 TEXT FIELD PROCESSING:")
    print(f"   Fields to process: {text_count}")
    print(f"   Estimated time:    {estimated_ai_time:.1f} seconds")
    print(f"   Estimated cost:    ${estimated_ai_cost:.3f}")
    print("   Method:            AI generation with author voice")
    print()
    
    # Simulate DATA field processing (direct copy)
    data_count = len(data_fields)
    estimated_data_time = data_count * 0.001  # 1ms per field
    estimated_data_cost = 0.0  # No cost for direct copy
    
    print("🔢 DATA FIELD PROCESSING:")
    print(f"   Fields to process: {data_count}")
    print(f"   Estimated time:    {estimated_data_time:.3f} seconds")
    print(f"   Estimated cost:    ${estimated_data_cost:.3f}")
    print("   Method:            Direct copy from Materials.yaml")
    print()
    
    # Show optimization benefits
    total_fields = text_count + data_count
    if total_fields > 0:
        optimization_ratio = data_count / total_fields * 100
        print("🚀 OPTIMIZATION BENEFITS:")
        print(f"   {optimization_ratio:.1f}% of fields bypass AI generation")
        print(f"   Time saved: ~{data_count * 8:.1f} seconds")
        print(f"   Cost saved: ~${data_count * 0.025:.3f}")
        print()


def main():
    """Run complete field separation demonstration"""
    try:
        demonstrate_field_classification()
        demonstrate_nested_classification()
        demonstrate_processing_simulation()
        
        print("✅ Field Separation Demonstration Complete")
        print()
        print("💡 Key Benefits:")
        print("   • Faster generation for data-only updates")
        print("   • Lower costs by avoiding unnecessary AI calls")
        print("   • Better quality through specialized processing")
        print("   • Clear separation of concerns")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())