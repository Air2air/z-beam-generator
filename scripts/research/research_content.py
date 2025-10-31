#!/usr/bin/env python3
"""
Content Type Research CLI

Command-line tool to research and populate content type data.

Usage:
    python research_content.py application "Battery Manufacturing" --industry "Energy Storage" --category "manufacturing"
    python research_content.py contaminant "Welding Spatter" --category "industrial"
    python research_content.py thesaurus "Ablation Threshold" --category "measurement"

Author: AI Assistant
Date: October 30, 2025
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import argparse
import json
import yaml
from shared.research.content_researcher import ContentResearcher


def research_application(args):
    """Research an application."""
    print(f"\n🔬 Researching Application: {args.name}")
    print(f"   Industry: {args.industry}")
    print(f"   Category: {args.category}")
    
    researcher = ContentResearcher.create()
    data = researcher.research_application(
        name=args.name,
        industry=args.industry,
        category=args.category
    )
    
    print(f"\n✅ Research Complete!")
    print(f"   Description: {data['description']}")
    print(f"   Use Cases: {len(data['use_cases'])}")
    print(f"   Materials: {len(data['common_materials'])}")
    print(f"   Contaminants: {len(data['common_contaminants'])}")
    
    if args.output:
        save_data(data, args.output)
    
    if args.json:
        print("\n" + json.dumps(data, indent=2))
    
    return data


def research_contaminant(args):
    """Research a contaminant."""
    print(f"\n🔬 Researching Contaminant: {args.name}")
    print(f"   Category: {args.category}")
    
    researcher = ContentResearcher.create()
    data = researcher.research_contaminant(
        name=args.name,
        category=args.category
    )
    
    print(f"\n✅ Research Complete!")
    print(f"   Description: {data['description']}")
    print(f"   Substrates: {len(data['common_substrates'])}")
    print(f"   Health Hazards: {len(data['health_hazards'])}")
    
    if args.output:
        save_data(data, args.output)
    
    if args.json:
        print("\n" + json.dumps(data, indent=2))
    
    return data


def research_thesaurus(args):
    """Research a thesaurus term."""
    print(f"\n🔬 Researching Term: {args.name}")
    print(f"   Category: {args.category}")
    
    researcher = ContentResearcher.create()
    data = researcher.research_thesaurus_term(
        term=args.name,
        category=args.category
    )
    
    print(f"\n✅ Research Complete!")
    print(f"   Definition: {data['definition'][:100]}...")
    print(f"   Related Terms: {len(data['related_terms'])}")
    print(f"   Synonyms: {len(data['synonyms'])}")
    
    if args.output:
        save_data(data, args.output)
    
    if args.json:
        print("\n" + json.dumps(data, indent=2))
    
    return data


def save_data(data, output_path):
    """Save researched data to file."""
    path = Path(output_path)
    
    if path.suffix == '.json':
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    elif path.suffix in ['.yaml', '.yml']:
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    else:
        raise ValueError(f"Unsupported output format: {path.suffix}")
    
    print(f"   💾 Saved to: {output_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Research content types using AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Research an application
  python research_content.py application "Battery Manufacturing" \\
    --industry "Energy Storage" --category "manufacturing"
  
  # Research a contaminant
  python research_content.py contaminant "Welding Spatter" \\
    --category "industrial"
  
  # Research a thesaurus term
  python research_content.py thesaurus "Ablation Threshold" \\
    --category "measurement"
  
  # Save output
  python research_content.py application "Solar Panel Cleaning" \\
    --industry "Renewable Energy" --category "maintenance" \\
    --output battery_mfg.yaml
        """
    )
    
    subparsers = parser.add_subparsers(dest='content_type', help='Content type to research')
    
    # Application parser
    app_parser = subparsers.add_parser('application', help='Research an application')
    app_parser.add_argument('name', help='Application name')
    app_parser.add_argument('--industry', required=True, help='Industry sector')
    app_parser.add_argument('--category', required=True, 
                           choices=['manufacturing', 'maintenance', 'restoration', 'industrial', 'specialized'],
                           help='Application category')
    app_parser.add_argument('--output', help='Output file path (.yaml or .json)')
    app_parser.add_argument('--json', action='store_true', help='Print JSON to stdout')
    
    # Contaminant parser
    cont_parser = subparsers.add_parser('contaminant', help='Research a contaminant')
    cont_parser.add_argument('name', help='Contaminant name')
    cont_parser.add_argument('--category', required=True,
                            choices=['corrosion', 'coatings', 'biological', 'industrial', 'environmental'],
                            help='Contaminant category')
    cont_parser.add_argument('--output', help='Output file path (.yaml or .json)')
    cont_parser.add_argument('--json', action='store_true', help='Print JSON to stdout')
    
    # Thesaurus parser
    thes_parser = subparsers.add_parser('thesaurus', help='Research a thesaurus term')
    thes_parser.add_argument('name', help='Technical term')
    thes_parser.add_argument('--category', required=True,
                            choices=['process', 'physics', 'equipment', 'measurement', 'safety'],
                            help='Term category')
    thes_parser.add_argument('--output', help='Output file path (.yaml or .json)')
    thes_parser.add_argument('--json', action='store_true', help='Print JSON to stdout')
    
    args = parser.parse_args()
    
    if not args.content_type:
        parser.print_help()
        return
    
    # Route to appropriate handler
    if args.content_type == 'application':
        research_application(args)
    elif args.content_type == 'contaminant':
        research_contaminant(args)
    elif args.content_type == 'thesaurus':
        research_thesaurus(args)


if __name__ == '__main__':
    main()
