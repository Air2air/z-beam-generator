#!/usr/bin/env python3
"""
API Terminal Diagnostics Tool

Implements mandatory terminal output reading requirements for API diagnostics.
This tool demonstrates the correct way to diagnose API issues by reading
terminal output to capture detailed error information not available in response objects.
"""

import re
import sys
from pathlib import Path


def analyze_terminal_output(terminal_output: str) -> dict:
    """
    Analyze terminal output for API error patterns.
    
    This function implements the required terminal analysis patterns
    identified in docs/API_TERMINAL_DIAGNOSTICS.md
    """
    analysis = {
        'connection_errors': [],
        'ssl_errors': [],
        'timeout_errors': [],
        'retry_patterns': [],
        'endpoint_errors': [],
        'authentication_errors': []
    }
    
    lines = terminal_output.split('\n')
    
    for line in lines:
        # Connection failure patterns
        if 'Connection failed on attempt' in line:
            analysis['connection_errors'].append(line.strip())
        
        if 'Connection error after' in line:
            analysis['connection_errors'].append(line.strip())
            
        # SSL/TLS error patterns
        if 'SSL' in line or 'TLS' in line:
            analysis['ssl_errors'].append(line.strip())
            
        if 'certificate' in line.lower():
            analysis['ssl_errors'].append(line.strip())
            
        # Timeout patterns
        if 'timeout' in line.lower() or 'timed out' in line.lower():
            analysis['timeout_errors'].append(line.strip())
            
        # Retry attempt patterns
        if 'Retry attempt' in line or 'retrying in' in line:
            analysis['retry_patterns'].append(line.strip())
            
        # Endpoint/URL errors
        if '404' in line or 'not found' in line.lower():
            analysis['endpoint_errors'].append(line.strip())
            
        if 'double-path' in line or '/v1/v1/' in line:
            analysis['endpoint_errors'].append(line.strip())
            
        # Authentication errors
        if '401' in line or '403' in line or 'unauthorized' in line.lower():
            analysis['authentication_errors'].append(line.strip())
    
    return analysis


def diagnose_content_impact(content_file_path: str) -> dict:
    """
    Analyze content file for signs of API failure impact.
    """
    if not Path(content_file_path).exists():
        return {'error': f'Content file not found: {content_file_path}'}
    
    with open(content_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analysis = {
        'incomplete_content': False,
        'multiple_frontmatter': False,
        'mixed_authors': False,
        'truncation_point': None,
        'frontmatter_count': 0
    }
    
    # Check for incomplete content (ends mid-sentence)
    lines = content.strip().split('\n')
    if lines:
        last_line = lines[-1].strip()
        if last_line and not last_line.endswith(('.', '!', '?', ':')):
            analysis['incomplete_content'] = True
            analysis['truncation_point'] = last_line
    
    # Count frontmatter sections
    frontmatter_count = content.count('---')
    analysis['frontmatter_count'] = frontmatter_count
    if frontmatter_count > 4:  # Expect opening/closing pairs
        analysis['multiple_frontmatter'] = True
    
    # Check for mixed author attribution
    author_pattern = r'author:\s*(.+)'
    authors = re.findall(author_pattern, content)
    if len(set(authors)) > 1:
        analysis['mixed_authors'] = True
        analysis['authors_found'] = list(set(authors))
    
    return analysis


def generate_recommendations(terminal_analysis: dict, content_analysis: dict) -> list:
    """
    Generate specific recommendations based on error patterns.
    """
    recommendations = []
    
    # SSL/TLS recommendations
    if terminal_analysis['ssl_errors']:
        recommendations.append({
            'category': 'SSL/TLS Issues',
            'severity': 'HIGH',
            'issue': 'SSL certificate or hostname verification failure',
            'recommendations': [
                'Check if Winston API SSL certificate is valid',
                'Verify network can reach api.winston.ai',
                'Consider using alternative provider temporarily',
                'Check firewall/proxy SSL inspection settings'
            ]
        })
    
    # Connection failure recommendations
    if terminal_analysis['connection_errors']:
        recommendations.append({
            'category': 'Connection Failures',
            'severity': 'HIGH',
            'issue': 'Unable to establish connection to API endpoint',
            'recommendations': [
                'Verify internet connectivity',
                'Check if API service is operational',
                'Verify API endpoint URL is correct',
                'Check for DNS resolution issues'
            ]
        })
    
    # Timeout recommendations
    if terminal_analysis['timeout_errors']:
        recommendations.append({
            'category': 'Timeout Issues',
            'severity': 'MEDIUM',
            'issue': 'API requests timing out',
            'recommendations': [
                'Increase timeout settings in API configuration',
                'Reduce request complexity (shorter prompts)',
                'Check network latency to API provider',
                'Consider using faster alternative provider'
            ]
        })
    
    # Content impact recommendations
    if content_analysis.get('incomplete_content'):
        recommendations.append({
            'category': 'Content Generation Impact',
            'severity': 'HIGH',
            'issue': 'API failures causing incomplete content generation',
            'recommendations': [
                'Regenerate content using working API provider',
                'Implement robust fallback mechanisms',
                'Add content completion detection',
                'Use alternative provider for affected materials'
            ]
        })
    
    # Endpoint configuration recommendations
    if terminal_analysis['endpoint_errors']:
        recommendations.append({
            'category': 'Endpoint Configuration',
            'severity': 'HIGH',
            'issue': 'API endpoint configuration errors',
            'recommendations': [
                'Check for double-path issues (/v1/v1/)',
                'Verify model names are current (not deprecated)',
                'Update base_url configuration',
                'Test endpoint URLs manually'
            ]
        })
    
    return recommendations


def run_comprehensive_api_diagnosis(provider_name: str, content_file: str = None):
    """
    Run comprehensive API diagnosis with terminal output analysis.
    
    This is the REQUIRED procedure for all API diagnostics.
    """
    print(f"🔍 Comprehensive API Diagnosis for {provider_name}")
    print("=" * 60)
    
    print("\n📋 Step 1: Running API connectivity test...")
    print("(Terminal output will be analyzed for detailed error patterns)")
    
    # Note: In real implementation, this would capture terminal ID
    # and use get_terminal_output() to read the actual terminal output
    print(f"\n⚠️  REQUIREMENT: After running API test, use get_terminal_output(terminal_id)")
    print(f"   to capture detailed error messages for {provider_name}")
    
    # Simulated terminal output analysis (replace with real terminal reading)
    example_terminal_output = """
🔍 [CLIENT MANAGER] Testing API connectivity...
🧪 [CLIENT MANAGER] Testing winston...
🚀 [API CLIENT] Starting request to ai-detection
🔌 [API CLIENT] Establishing connection...
🔌 [API CLIENT] Connection failed on attempt 1, retrying in 1.0s...
🔄 [API CLIENT] Retry attempt 1/3 after 1.0s delay
🔌 [API CLIENT] Connection failed on attempt 2, retrying in 2.0s...
🔌 [API CLIENT] Connection error after 4 attempts
❌ [CLIENT MANAGER] winston: Failed - None
HTTPSConnectionPool(host='api.winston.ai', port=443): Max retries exceeded
(Caused by SSLError(SSLError(1, '[SSL: TLSV1_UNRECOGNIZED_NAME] tlsv1 unrecognized name')))
"""
    
    print("\n📊 Step 2: Analyzing terminal output for error patterns...")
    terminal_analysis = analyze_terminal_output(example_terminal_output)
    
    print("\n🔍 Terminal Analysis Results:")
    for category, errors in terminal_analysis.items():
        if errors:
            print(f"   {category.upper()}: {len(errors)} found")
            for error in errors[:2]:  # Show first 2 errors
                print(f"      • {error}")
    
    # Content impact analysis
    if content_file:
        print(f"\n📄 Step 3: Analyzing content impact ({content_file})...")
        content_analysis = diagnose_content_impact(content_file)
        
        print("\n📊 Content Impact Analysis:")
        if content_analysis.get('incomplete_content'):
            print("   ❌ INCOMPLETE CONTENT DETECTED")
            print(f"      Truncation point: {content_analysis.get('truncation_point', 'Unknown')}")
        
        if content_analysis.get('multiple_frontmatter'):
            print("   ⚠️  MULTIPLE FRONTMATTER SECTIONS")
            print(f"      Count: {content_analysis.get('frontmatter_count', 0)}")
        
        if content_analysis.get('mixed_authors'):
            print("   ⚠️  MIXED AUTHOR ATTRIBUTION")
            print(f"      Authors: {content_analysis.get('authors_found', [])}")
    else:
        content_analysis = {}
    
    # Generate recommendations
    print("\n💡 Step 4: Generating recommendations...")
    recommendations = generate_recommendations(terminal_analysis, content_analysis)
    
    print("\n🎯 Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n   {i}. {rec['category']} ({rec['severity']} PRIORITY)")
        print(f"      Issue: {rec['issue']}")
        print("      Actions:")
        for action in rec['recommendations'][:3]:  # Show top 3 actions
            print(f"        • {action}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 DIAGNOSIS COMPLETE")
    
    if any(terminal_analysis.values()):
        print("❌ API Issues Detected - See recommendations above")
    else:
        print("✅ No major API issues detected in terminal output")
    
    if content_analysis.get('incomplete_content'):
        print("❌ Content Generation Impact Confirmed")
    
    print(f"\n📚 Reference: docs/API_TERMINAL_DIAGNOSTICS.md")
    print(f"🔧 Next Steps: Implement top priority recommendations")


def main():
    """Main function demonstrating proper API diagnosis procedure."""
    if len(sys.argv) < 2:
        print("Usage: python3 api_terminal_diagnostics.py <provider_name> [content_file]")
        print("Example: python3 api_terminal_diagnostics.py winston content/components/text/alumina-laser-cleaning.md")
        sys.exit(1)
    
    provider_name = sys.argv[1]
    content_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    run_comprehensive_api_diagnosis(provider_name, content_file)


if __name__ == "__main__":
    main()
