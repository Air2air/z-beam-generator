"""
Test Domain Linkages URL Format Compliance

Ensures all domain_linkages URLs have the correct suffixes to prevent 404 errors.

Requirements:
- Contaminant URLs MUST end with -contamination
- Material URLs MUST end with -laser-cleaning  
- Compound URLs MUST end with -compound

Created: Dec 16, 2025
Issue: 2,887+ incorrect URLs found in initial deployment
Fix: Corrected shared/validation/domain_associations.py URL generation
"""

import pytest
import yaml
from pathlib import Path


def get_all_frontmatter_files():
    """Get all frontmatter YAML files across all domains"""
    frontmatter_dir = Path('frontmatter')
    domains = ['materials', 'contaminants', 'settings', 'compounds']
    
    files = []
    for domain in domains:
        domain_dir = frontmatter_dir / domain
        if domain_dir.exists():
            files.extend(domain_dir.glob('*.yaml'))
    
    return files


def extract_urls_from_file(file_path: Path):
    """Extract all URLs from domain_linkages section"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    urls = []
    domain_linkages = data.get('domain_linkages', {})
    
    # Check all possible linkage types
    for key, value in domain_linkages.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and 'url' in item:
                    urls.append(item['url'])
    
    return urls


def test_contaminant_urls_have_suffix():
    """All contaminant URLs MUST end with -contamination"""
    files = get_all_frontmatter_files()
    violations = []
    
    for file_path in files:
        urls = extract_urls_from_file(file_path)
        
        for url in urls:
            if '/contaminants/' in url:
                # Extract slug from URL (last segment)
                slug = url.rstrip('/').split('/')[-1]
                
                if not slug.endswith('-contamination'):
                    violations.append({
                        'file': file_path.name,
                        'url': url,
                        'slug': slug,
                        'issue': 'Missing -contamination suffix'
                    })
    
    if violations:
        error_msg = f"\n\n❌ Found {len(violations)} contaminant URLs without -contamination suffix:\n"
        for v in violations[:10]:  # Show first 10
            error_msg += f"  File: {v['file']}\n"
            error_msg += f"  URL: {v['url']}\n"
            error_msg += f"  Should be: {v['slug']}-contamination\n\n"
        
        pytest.fail(error_msg)


def test_material_urls_have_suffix():
    """All material URLs MUST end with -laser-cleaning"""
    files = get_all_frontmatter_files()
    violations = []
    
    for file_path in files:
        urls = extract_urls_from_file(file_path)
        
        for url in urls:
            if '/materials/' in url:
                slug = url.rstrip('/').split('/')[-1]
                
                if not slug.endswith('-laser-cleaning'):
                    violations.append({
                        'file': file_path.name,
                        'url': url,
                        'slug': slug,
                        'issue': 'Missing -laser-cleaning suffix'
                    })
    
    if violations:
        error_msg = f"\n\n❌ Found {len(violations)} material URLs without -laser-cleaning suffix:\n"
        for v in violations[:10]:
            error_msg += f"  File: {v['file']}\n"
            error_msg += f"  URL: {v['url']}\n"
            error_msg += f"  Should be: {v['slug']}-laser-cleaning\n\n"
        
        pytest.fail(error_msg)


def test_compound_urls_have_suffix():
    """All compound URLs MUST end with -compound"""
    files = get_all_frontmatter_files()
    violations = []
    
    for file_path in files:
        urls = extract_urls_from_file(file_path)
        
        for url in urls:
            if '/compounds/' in url:
                slug = url.rstrip('/').split('/')[-1]
                
                if not slug.endswith('-compound'):
                    violations.append({
                        'file': file_path.name,
                        'url': url,
                        'slug': slug,
                        'issue': 'Missing -compound suffix'
                    })
    
    if violations:
        error_msg = f"\n\n❌ Found {len(violations)} compound URLs without -compound suffix:\n"
        for v in violations[:10]:
            error_msg += f"  File: {v['file']}\n"
            error_msg += f"  URL: {v['url']}\n"
            error_msg += f"  Should be: {v['slug']}-compound\n\n"
        
        pytest.fail(error_msg)


def test_no_urls_with_incorrect_case():
    """Material slugs should be lowercase in URLs"""
    files = get_all_frontmatter_files()
    violations = []
    
    for file_path in files:
        urls = extract_urls_from_file(file_path)
        
        for url in urls:
            if '/materials/' in url:
                slug = url.rstrip('/').split('/')[-1]
                
                # Check if slug has uppercase letters
                if slug != slug.lower():
                    violations.append({
                        'file': file_path.name,
                        'url': url,
                        'slug': slug,
                        'issue': 'Contains uppercase letters'
                    })
    
    if violations:
        error_msg = f"\n\n❌ Found {len(violations)} URLs with incorrect case:\n"
        for v in violations[:10]:
            error_msg += f"  File: {v['file']}\n"
            error_msg += f"  URL: {v['url']}\n"
            error_msg += f"  Should be: {v['slug'].lower()}\n\n"
        
        pytest.fail(error_msg)


def test_url_format_statistics():
    """Report statistics on URL formats across all domains"""
    files = get_all_frontmatter_files()
    
    stats = {
        'total_files': len(files),
        'files_with_linkages': 0,
        'total_urls': 0,
        'contaminant_urls': 0,
        'material_urls': 0,
        'compound_urls': 0,
        'correct_format': 0,
        'incorrect_format': 0
    }
    
    for file_path in files:
        urls = extract_urls_from_file(file_path)
        
        if urls:
            stats['files_with_linkages'] += 1
            stats['total_urls'] += len(urls)
        
        for url in urls:
            if '/contaminants/' in url:
                stats['contaminant_urls'] += 1
                if url.rstrip('/').split('/')[-1].endswith('-contamination'):
                    stats['correct_format'] += 1
                else:
                    stats['incorrect_format'] += 1
            
            elif '/materials/' in url:
                stats['material_urls'] += 1
                if url.rstrip('/').split('/')[-1].endswith('-laser-cleaning'):
                    stats['correct_format'] += 1
                else:
                    stats['incorrect_format'] += 1
            
            elif '/compounds/' in url:
                stats['compound_urls'] += 1
                if url.rstrip('/').split('/')[-1].endswith('-compound'):
                    stats['correct_format'] += 1
                else:
                    stats['incorrect_format'] += 1
    
    # Print statistics (always passes, just for reporting)
    print("\n\n" + "="*80)
    print("📊 DOMAIN LINKAGES URL FORMAT STATISTICS")
    print("="*80)
    print(f"Total frontmatter files: {stats['total_files']}")
    print(f"Files with domain_linkages: {stats['files_with_linkages']}")
    print(f"Total URLs found: {stats['total_urls']}")
    print(f"\nBy domain:")
    print(f"  Contaminant URLs: {stats['contaminant_urls']}")
    print(f"  Material URLs: {stats['material_urls']}")
    print(f"  Compound URLs: {stats['compound_urls']}")
    print(f"\nFormat compliance:")
    print(f"  ✅ Correct format: {stats['correct_format']}")
    print(f"  ❌ Incorrect format: {stats['incorrect_format']}")
    
    if stats['incorrect_format'] == 0:
        print(f"\n🎉 100% URL format compliance!")
    else:
        print(f"\n⚠️  {stats['incorrect_format']} URLs need fixing")
    
    print("="*80 + "\n")
    
    # Always passes (reporting only)
    assert True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
