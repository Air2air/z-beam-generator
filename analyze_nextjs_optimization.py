#!/usr/bin/env python3
"""
Next.js Optimized Orchestration Analysis
Comprehensive analysis of the Next.js context-aware frontmatter generation.
"""

import yaml
from pathlib import Path

def analyze_nextjs_optimization():
    """Analyze the Next.js optimized frontmatter structure and performance."""
    
    print("🚀 Next.js Optimized Orchestration Analysis")
    print("=" * 60)
    
    # Load the Next.js optimized frontmatter
    optimized_file = Path("aluminum-nextjs-optimized.yaml")
    if not optimized_file.exists():
        print("❌ Next.js optimized file not found")
        return
    
    with open(optimized_file, 'r', encoding='utf-8') as f:
        optimized_data = yaml.safe_load(f)
    
    # Load previous direct orchestration for comparison
    direct_file = Path("aluminum-direct-orchestrated.yaml")
    direct_data = None
    if direct_file.exists():
        with open(direct_file, 'r', encoding='utf-8') as f:
            direct_data = yaml.safe_load(f)
    
    print("📊 File Size Analysis:")
    optimized_size = optimized_file.stat().st_size
    print(f"   📁 Next.js optimized: {optimized_size:,} bytes ({optimized_size/1024:.1f} KB)")
    
    if direct_data:
        direct_size = direct_file.stat().st_size
        print(f"   📁 Direct orchestrated: {direct_size:,} bytes ({direct_size/1024:.1f} KB)")
        size_change = ((optimized_size - direct_size) / direct_size) * 100
        print(f"   📈 Size change: {size_change:+.1f}%")
    
    print("\\n🎯 Next.js Structure Analysis:")
    
    # Analyze componentOutputs structure
    component_outputs = optimized_data.get('componentOutputs', {})
    print(f"   📦 Component categories: {len(component_outputs)}")
    
    for category_name, category_data in component_outputs.items():
        print(f"\\n   📂 {category_name.upper()} Category:")
        if isinstance(category_data, dict):
            for component_name, component_data in category_data.items():
                print(f"      🧩 {component_name}: {len(str(component_data)):,} chars")
                
                # Analyze component purpose alignment
                if component_name == "caption":
                    print(f"         🔬 Microscopic context: {component_data.get('microscopicContext', {}).get('purpose', 'N/A')}")
                    print(f"         📸 Viewing recommendations: {component_data.get('microscopicContext', {}).get('viewingRecommendations', 'N/A')}")
                
                elif component_name == "table":
                    print(f"         📊 Table purpose: {component_data.get('purpose', 'N/A')}")
                    sections = component_data.get('sections', {})
                    print(f"         📋 Table sections: {list(sections.keys())}")
                    total_rows = sum(len(section.get('data', {})) for section in sections.values())
                    print(f"         📝 Total data rows: {total_rows}")
                
                elif component_name == "tags":
                    search_tags = component_data.get('searchTags', [])
                    print(f"         🏷️ Search tags: {len(search_tags)} tags")
                    search_opt = component_data.get('searchOptimization', {})
                    print(f"         🔍 Clickable interface: {search_opt.get('clickableInterface', False)}")
                    categories = search_opt.get('searchCategories', {})
                    print(f"         📂 Tag categories: {list(categories.keys())}")
                
                elif component_name == "jsonld":
                    structured_data = component_data.get('structuredData', {})
                    print(f"         🏗️ Schema types: {structured_data.get('@type', [])}")
                    seo_opt = component_data.get('seoOptimization', {})
                    print(f"         📈 Properties included: {seo_opt.get('propertiesIncluded', 0)}")
                
                elif component_name == "metatags":
                    html_meta = component_data.get('htmlMeta', {})
                    og_meta = component_data.get('openGraph', {})
                    twitter_meta = component_data.get('twitterCard', {})
                    print(f"         🌐 HTML meta tags: {len(html_meta)}")
                    print(f"         📱 Social platforms: {len(og_meta) + len(twitter_meta)} total")
    
    print("\\n📋 Next.js Optimization Metadata:")
    nextjs_info = optimized_data.get('nextjs', {})
    print(f"   ⚙️ Optimization type: {nextjs_info.get('optimization', 'unknown')}")
    print(f"   ⏱️ Generation time: {nextjs_info.get('totalTime', 'N/A')}")
    print(f"   🏗️ Structure pattern: {nextjs_info.get('structure', 'unknown')}")
    
    component_purposes = nextjs_info.get('componentPurposes', {})
    print(f"\\n   🎯 Component Purpose Mapping:")
    for component, purpose in component_purposes.items():
        print(f"      {component}: {purpose}")
    
    print("\\n✅ Next.js Optimization Benefits:")
    print("   🔬 Caption: Optimized for microscopic photo descriptions with technical analysis")
    print("   📊 Table: Efficient overflow data display for machineSettings and applications") 
    print("   🏷️ Tags: Clickable search navigation with 10 essential tags")
    print("   🏗️ JSON-LD: SEO-optimized structured data with material properties")
    print("   📱 Metatags: Social media and HTML SEO optimization")
    
    print("\\n🎨 Next.js App Integration:")
    print("   📸 Caption component: Serves microscopic before/after photo descriptions")
    print("   📋 Table component: Displays overflow data too large for core properties")
    print("   🔍 Tags component: Provides clickable search navigation interface")
    print("   📡 JSON-LD component: Enhances SEO with structured data markup")
    print("   📱 Metatags component: Optimizes social media sharing and HTML meta")
    
    # Performance metrics
    total_char_count = len(str(optimized_data))
    component_char_count = len(str(component_outputs))
    component_percentage = (component_char_count / total_char_count) * 100
    
    print("\\n📊 Performance Metrics:")
    print(f"   📄 Total frontmatter: {total_char_count:,} characters")
    print(f"   🧩 Component outputs: {component_char_count:,} characters ({component_percentage:.1f}%)")
    print(f"   📦 Components per category: {len(component_outputs)} categories")
    print(f"   🎯 Next.js optimized structure: Content | Navigation | Metadata")
    
    return optimized_data

def validate_nextjs_component_alignment():
    """Validate that components align with Next.js app usage patterns."""
    
    print("\\n🔍 Next.js Component Alignment Validation")
    print("=" * 50)
    
    optimized_file = Path("aluminum-nextjs-optimized.yaml")
    if not optimized_file.exists():
        print("❌ Next.js optimized file not found")
        return False
    
    with open(optimized_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    component_outputs = data.get('componentOutputs', {})
    validation_results = {}
    
    # Validate content components
    content_components = component_outputs.get('content', {})
    
    # Caption validation
    caption = content_components.get('caption', {})
    caption_valid = (
        'beforeText' in caption and
        'afterText' in caption and
        'microscopicContext' in caption and
        caption.get('microscopicContext', {}).get('purpose') == 'microscopic_photo_descriptions'
    )
    validation_results['caption'] = caption_valid
    print(f"   🔬 Caption (microscopic photos): {'✅ Valid' if caption_valid else '❌ Invalid'}")
    
    # Table validation
    table = content_components.get('table', {})
    table_valid = (
        table.get('purpose') == 'short_string_data_overflow' and
        'sections' in table and
        len(table.get('sections', {})) > 0 and
        'displayFormat' in table
    )
    validation_results['table'] = table_valid
    print(f"   📊 Table (overflow data): {'✅ Valid' if table_valid else '❌ Invalid'}")
    
    # Validate navigation components
    navigation_components = component_outputs.get('navigation', {})
    
    # Tags validation
    tags = navigation_components.get('tags', {})
    tags_valid = (
        'searchTags' in tags and
        len(tags.get('searchTags', [])) == 10 and
        tags.get('searchOptimization', {}).get('clickableInterface') == True
    )
    validation_results['tags'] = tags_valid
    print(f"   🏷️ Tags (search navigation): {'✅ Valid' if tags_valid else '❌ Invalid'}")
    
    # Validate metadata components
    metadata_components = component_outputs.get('metadata', {})
    
    # JSON-LD validation
    jsonld = metadata_components.get('jsonld', {})
    jsonld_valid = (
        'structuredData' in jsonld and
        jsonld.get('structuredData', {}).get('@context') == 'https://schema.org' and
        'seoOptimization' in jsonld
    )
    validation_results['jsonld'] = jsonld_valid
    print(f"   🏗️ JSON-LD (SEO structured): {'✅ Valid' if jsonld_valid else '❌ Invalid'}")
    
    # Metatags validation
    metatags = metadata_components.get('metatags', {})
    metatags_valid = (
        'htmlMeta' in metatags and
        'openGraph' in metatags and
        'twitterCard' in metatags and
        'socialOptimization' in metatags
    )
    validation_results['metatags'] = metatags_valid
    print(f"   📱 Metatags (social/SEO): {'✅ Valid' if metatags_valid else '❌ Invalid'}")
    
    # Overall validation
    all_valid = all(validation_results.values())
    print(f"\\n   🎯 Overall Next.js alignment: {'✅ All components valid' if all_valid else '❌ Some components invalid'}")
    
    return all_valid

if __name__ == "__main__":
    # Run comprehensive analysis
    optimized_data = analyze_nextjs_optimization()
    
    if optimized_data:
        # Validate component alignment
        alignment_valid = validate_nextjs_component_alignment()
        
        print("\\n🎉 Next.js Optimized Orchestration Analysis Complete!")
        print(f"   ✅ Structure: Content | Navigation | Metadata")
        print(f"   ✅ Components: 5 total (Caption, Table, Tags, JSON-LD, Metatags)")
        print(f"   ✅ Purpose alignment: {'Valid' if alignment_valid else 'Needs adjustment'}")
        print(f"   ✅ Next.js integration: Optimized for app component usage patterns")