"""
Script to check component conformance with standards and suggest improvements.
"""

import os
import re
import ast
import argparse
from typing import List, Dict, Any

def scan_component_file(file_path: str) -> Dict[str, Any]:
    """Scan a component file for conformance metrics."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    metrics = {
        'file': file_path,
        'has_generate': bool(re.search(r'def\s+generate\s*\(', content)),
        'has_prepare_data': bool(re.search(r'def\s+_prepare_data\s*\(', content)),
        'has_format_prompt': bool(re.search(r'def\s+_format_prompt\s*\(', content)),
        'has_call_api': bool(re.search(r'def\s+_call_api\s*\(', content)),
        'has_post_process': bool(re.search(r'def\s+_post_process\s*\(', content)),
        'uses_frontmatter': 'get_frontmatter_data' in content,
        'has_error_handling': 'try' in content and 'except' in content,
        'return_error_markdown': '_create_error_markdown' in content
    }
    
    # Calculate conformance percentage
    conformance_checks = [v for k, v in metrics.items() if k not in ['file']]
    metrics['conformance'] = sum(conformance_checks) / len(conformance_checks) * 100
    
    return metrics

def find_component_files() -> List[str]:
    """Find all component files in the components directory."""
    component_files = []
    for root, _, files in os.walk('./components'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                if 'class' in content and ('Component' in content or 'Generator' in content):
                    component_files.append(file_path)
    return component_files

def generate_report(metrics_list: List[Dict[str, Any]]) -> str:
    """Generate a report of component conformance."""
    report = ["# Component Standardization Report", ""]
    
    # Sort by conformance
    metrics_list.sort(key=lambda x: x['conformance'])
    
    for metrics in metrics_list:
        conformance = metrics['conformance']
        file = metrics['file']
        report.append(f"## {os.path.basename(file)} - {conformance:.1f}% conformant")
        report.append("")
        
        # Add details
        report.append("| Method | Present |")
        report.append("|--------|---------|")
        report.append(f"| generate | {'✅' if metrics['has_generate'] else '❌'} |")
        report.append(f"| _prepare_data | {'✅' if metrics['has_prepare_data'] else '❌'} |")
        report.append(f"| _format_prompt | {'✅' if metrics['has_format_prompt'] else '❌'} |")
        report.append(f"| _call_api | {'✅' if metrics['has_call_api'] else '❌'} |")
        report.append(f"| _post_process | {'✅' if metrics['has_post_process'] else '❌'} |")
        report.append("")
        
        report.append("| Feature | Present |")
        report.append("|--------|---------|")
        report.append(f"| Uses frontmatter | {'✅' if metrics['uses_frontmatter'] else '❌'} |")
        report.append(f"| Error handling | {'✅' if metrics['has_error_handling'] else '❌'} |")
        report.append(f"| Error markdown | {'✅' if metrics['return_error_markdown'] else '❌'} |")
        report.append("")
    
    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description='Check component standards conformance')
    parser.add_argument('--report', action='store_true', help='Generate a report file')
    args = parser.parse_args()
    
    component_files = find_component_files()
    metrics_list = [scan_component_file(file) for file in component_files]
    
    report = generate_report(metrics_list)
    
    if args.report:
        with open('component_standards_report.md', 'w') as f:
            f.write(report)
        print(f"Report saved to component_standards_report.md")
    else:
        print(report)

if __name__ == "__main__":
    main()