#!/usr/bin/env python3
"""
Lightweight validation CLI for Z-Beam components.
Usage: python validate.py <component> [content_file] [--errors error_file]
"""

import sys
import argparse
from validation.validator import validate_component, parse_terminal_errors, format_validation_summary

def main():
    parser = argparse.ArgumentParser(description="Validate Z-Beam component content")
    parser.add_argument('component', help='Component name (frontmatter, content, etc.)')
    parser.add_argument('content_file', nargs='?', help='File with content to validate (or stdin)')
    parser.add_argument('--errors', help='File with terminal errors to parse')
    
    args = parser.parse_args()
    
    # Read content
    if args.content_file:
        try:
            with open(args.content_file, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {args.content_file}", file=sys.stderr)
            return 1
    else:
        content = sys.stdin.read()
    
    # Validate content
    success, score, errors = validate_component(args.component, content)
    print(format_validation_summary(args.component, success, score, errors))
    
    # Show detailed analysis for failed validations
    if not success or errors:
        print("\n🔍 DETAILED ANALYSIS for Claude:")
        print(f"   Component: {args.component}")
        print(f"   Content length: {len(content)} chars")
        print(f"   Quality score: {score:.1f}/10")
        if errors:
            print("   Issues detected:")
            for i, error in enumerate(errors, 1):
                print(f"     {i}. {error}")
        
        # Show content preview for debugging
        if content:
            lines = content.split('\n')
            print(f"   Content structure: {len(lines)} lines")
            print(f"   First line: {lines[0][:80]}..." if lines[0] else "   First line: [empty]")
            if len(lines) > 1:
                print(f"   Last line: {lines[-1][:80]}..." if lines[-1] else "   Last line: [empty]")
    
    # Parse terminal errors if provided
    if args.errors:
        try:
            with open(args.errors, 'r') as f:
                terminal_output = f.read()
            
            terminal_errors = parse_terminal_errors(terminal_output)
            if terminal_errors:
                print(f"\n🚨 TERMINAL ERROR ANALYSIS ({len(terminal_errors)} issues):")
                print("   Claude should focus on these system-level issues:")
                for i, error in enumerate(terminal_errors, 1):
                    print(f"     {i}. {error}")
                    
                # Provide summary guidance for Claude
                error_types = set()
                for error in terminal_errors:
                    if "yaml" in error.lower():
                        error_types.add("YAML parsing")
                    elif "json" in error.lower():
                        error_types.add("JSON formatting")
                    elif "api" in error.lower():
                        error_types.add("API connectivity")
                    elif "timeout" in error.lower():
                        error_types.add("Performance/timeout")
                    elif "auth" in error.lower():
                        error_types.add("Authentication")
                
                if error_types:
                    print(f"\n   🎯 CLAUDE PRIORITY AREAS: {', '.join(error_types)}")
            else:
                print("\n✅ No terminal errors detected")
        except FileNotFoundError:
            print(f"Warning: Error file not found: {args.errors}", file=sys.stderr)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
