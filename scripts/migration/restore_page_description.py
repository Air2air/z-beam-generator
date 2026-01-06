#!/usr/bin/env python3
"""
Restore pageDescription field from z-beam frontmatter git history

This script:
1. Extracts pageDescription from commit adb841c0a (last known good)
2. Maps frontmatter filenames to source data keys
3. Updates source YAML files with restored pageDescription content

Per docs/FRONTEND_REQUIRED_FIELDS_JAN4_2026.md:
- pageDescription: Used by PageTitle component as subtitle (150-200 chars)
- metaDescription: SEO meta tag (120-155 chars)
Both fields are REQUIRED and DIFFERENT
"""

import subprocess
import yaml
import os
import sys

def get_file_from_git(commit, filepath):
    """Get file content from git commit"""
    result = subprocess.run(
        f"git show {commit}:{filepath}",
        shell=True,
        capture_output=True,
        text=True,
        cwd='../z-beam'
    )
    if result.returncode == 0:
        return yaml.safe_load(result.stdout)
    return None

def extract_page_descriptions(domain):
    """Extract pageDescription from all files in a domain"""
    descriptions = {}
    
    # Get file list
    result = subprocess.run(
        f"git ls-tree -r --name-only adb841c0a frontmatter/{domain}",
        shell=True,
        capture_output=True,
        text=True,
        cwd='../z-beam'
    )
    
    files = [f for f in result.stdout.strip().split('\n') if f.endswith('.yaml')]
    
    for filepath in files:
        data = get_file_from_git('adb841c0a', filepath)
        if data and 'pageDescription' in data:
            filename = os.path.basename(filepath).replace('.yaml', '')
            
            # Map filename to source data key
            if domain == 'settings':
                # alabaster-settings -> alabaster
                key = filename.replace('-settings', '')
            elif domain == 'materials':
                # alabaster-laser-cleaning -> alabaster-laser-cleaning
                key = filename
            elif domain == 'contaminants':
                # rust-oxidation-contamination -> rust-oxidation-contamination
                key = filename
            elif domain == 'compounds':
                # carbon-monoxide-compound -> carbon-monoxide-compound
                key = filename
            
            descriptions[key] = data['pageDescription']
    
    return descriptions

def update_source_file(filepath, domain_key, descriptions):
    """Update source YAML file with pageDescription"""
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    
    count = 0
    for key, item in data[domain_key].items():
        if key in descriptions:
            item['pageDescription'] = descriptions[key]
            count += 1
    
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    
    return count

def main():
    print("="*80)
    print("RESTORING pageDescription FROM GIT BACKUP (adb841c0a)")
    print("="*80)
    
    # Process each domain
    domains = [
        ('materials', 'data/materials/Materials.yaml', 'materials'),
        ('settings', 'data/settings/Settings.yaml', 'settings'),
        ('contaminants', 'data/contaminants/Contaminants.yaml', 'contaminants'),
        ('compounds', 'data/compounds/Compounds.yaml', 'compounds'),
    ]
    
    total_restored = 0
    
    for domain, filepath, domain_key in domains:
        print(f"\n📁 Processing {domain}...")
        
        # Extract descriptions from git
        descriptions = extract_page_descriptions(domain)
        print(f"   Found {len(descriptions)} pageDescription entries in git")
        
        # Update source file
        count = update_source_file(filepath, domain_key, descriptions)
        print(f"   ✅ Updated {count} items in {filepath}")
        
        # Show samples
        if descriptions:
            sample_keys = list(descriptions.keys())[:2]
            for key in sample_keys:
                print(f"      • {key}: {descriptions[key][:60]}...")
        
        total_restored += count
    
    print("\n" + "="*80)
    print(f"✅ RESTORATION COMPLETE: {total_restored} items updated")
    print("="*80)
    print("\nBoth fields now present:")
    print("  • pageDescription: PageTitle component subtitle")
    print("  • metaDescription: SEO meta tag")
    print("\nNext: Regenerate frontmatter with --export")

if __name__ == '__main__':
    main()
