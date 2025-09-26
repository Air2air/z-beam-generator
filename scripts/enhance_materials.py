#!/usr/bin/env python3
"""
Materials Enhancement CLI

Command-line interface for the Materials.yaml enhancement pipeline.
Provides easy access to gap analysis and automated research enhancement.

Usage:
    python enhance_materials.py analyze                    # Run gap analysis
    python enhance_materials.py enhance 10                 # Enhance up to 10 materials  
    python enhance_materials.py enhance 5 density hardness # Enhance specific properties
    python enhance_materials.py report                     # Generate detailed report
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from ai_research.enhancement.materials_yaml_enhancer import MaterialsYamlEnhancer
from datetime import datetime


def run_gap_analysis(args):
    """Run comprehensive gap analysis"""
    print("🔍 Starting Materials Gap Analysis...")
    
    enhancer = MaterialsYamlEnhancer()
    gap_analysis = enhancer.analyze_material_gaps()
    
    print(f"\n📊 Gap Analysis Results:")
    print(f"   Total Materials: {gap_analysis['total_materials']}")
    print(f"   Materials Needing Research: {gap_analysis['gap_summary']['materials_needing_research']}")
    print(f"   Current Completion: {gap_analysis['gap_summary']['completion_percentage']:.1f}%")
    print(f"   Total Gap Instances: {gap_analysis['gap_summary']['total_gap_instances']}")
    
    print(f"\n🔥 Most Common Missing Properties:")
    for prop, count in gap_analysis['gap_summary']['most_common_gaps'][:5]:
        print(f"   • {prop}: {count} materials")
    
    print(f"\n⚡ Top Priority Research Items:")
    for i, item in enumerate(gap_analysis['priority_research'][:5], 1):
        print(f"   {i}. {item['material']} - {item['property']}")
    
    # Save detailed report
    if args.save_report:
        report_path = f"materials_gap_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        enhancer.generate_enhancement_report(report_path)
        print(f"\n💾 Detailed report saved to: {report_path}")


def run_enhancement(args):
    """Run materials enhancement with AI research"""
    max_materials = args.max_materials
    target_properties = args.properties if hasattr(args, 'properties') and args.properties else None
    
    print(f"🚀 Starting Materials Enhancement...")
    print(f"   Max Materials: {max_materials}")
    if target_properties:
        print(f"   Target Properties: {', '.join(target_properties)}")
    
    enhancer = MaterialsYamlEnhancer()
    
    try:
        results = enhancer.enhance_materials_with_research(
            max_materials=max_materials,
            target_properties=target_properties
        )
        
        print(f"\n✅ Enhancement Complete!")
        print(f"   Enhanced Materials: {len(results['enhanced_materials'])}")
        print(f"   Properties Researched: {results['properties_researched']}")
        print(f"   Failed Materials: {len(results['failed_materials'])}")
        print(f"   Backup Created: {results['backup_path']}")
        
        if results['enhanced_materials']:
            print(f"\n📈 Successfully Enhanced:")
            for material in results['enhanced_materials'][:5]:
                props = ', '.join(material['properties_added'])
                print(f"   • {material['name']}: {props}")
        
        if results['failed_materials']:
            print(f"\n❌ Enhancement Failures:")
            for material in results['failed_materials'][:3]:
                error = material.get('error', 'Unknown error')
                print(f"   • {material['name']}: {error}")
    
    except Exception as e:
        print(f"\n💥 Enhancement Failed: {e}")
        sys.exit(1)


def generate_report(args):
    """Generate detailed enhancement report"""
    print("📋 Generating Detailed Enhancement Report...")
    
    enhancer = MaterialsYamlEnhancer()
    
    report_path = f"materials_enhancement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    enhancer.generate_enhancement_report(report_path)
    
    print(f"✅ Report generated: {report_path}")
    
    # Display preview
    with open(report_path, 'r') as f:
        lines = f.readlines()
        print("\n📖 Report Preview (first 20 lines):")
        for line in lines[:20]:
            print(f"   {line.rstrip()}")


def main():
    parser = argparse.ArgumentParser(
        description="Materials.yaml Enhancement Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Gap analysis command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze gaps in Materials.yaml')
    analyze_parser.add_argument('--save-report', action='store_true', 
                               help='Save detailed gap analysis report')
    
    # Enhancement command
    enhance_parser = subparsers.add_parser('enhance', help='Enhance materials with AI research')
    enhance_parser.add_argument('max_materials', type=int, default=5, nargs='?',
                               help='Maximum number of materials to enhance (default: 5)')
    enhance_parser.add_argument('properties', nargs='*',
                               help='Specific properties to research (e.g., density hardness)')
    
    # Report generation command
    report_parser = subparsers.add_parser('report', help='Generate detailed enhancement report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == 'analyze':
        run_gap_analysis(args)
    elif args.command == 'enhance':
        run_enhancement(args)
    elif args.command == 'report':
        generate_report(args)


if __name__ == "__main__":
    main()