#!/usr/bin/env python3

"""
Script to manually generate missing components for Alumina.

This script will directly create the JSON-LD and metatags components
for Alumina based on the existing frontmatter data, without using an API.
"""

import sys
import os
import json
import yaml
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

try:
    # Load frontmatter
    frontmatter_path = 'content/components/frontmatter/alumina-laser-cleaning.md'
    with open(frontmatter_path, 'r') as f:
        frontmatter_content = f.read()
    
    # Extract YAML content between --- delimiters
    parts = frontmatter_content.split('---', 2)
    yaml_content = parts[1].strip()
    frontmatter_data = yaml.safe_load(yaml_content)
    
    # Generate JSON-LD directly
    print("Generating JSON-LD content...")
    
    # Create JSON-LD content
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": frontmatter_data.get('name', 'Alumina'),
        "description": frontmatter_data.get('description', 'Technical guide to Alumina for laser cleaning applications'),
        "manufacturer": {
            "@type": "Organization",
            "name": "Z-Beam"
        },
        "category": frontmatter_data.get('category', 'ceramic'),
        "additionalProperty": [],
        "author": {
            "@type": "Person",
            "name": frontmatter_data.get('author', {}).get('author_name', 'Evelyn Wu'),
            "nationality": frontmatter_data.get('author', {}).get('author_country', 'Taiwan')
        }
    }
    
    # Add technical specifications
    if 'technicalSpecifications' in frontmatter_data:
        for name, value in frontmatter_data['technicalSpecifications'].items():
            jsonld['additionalProperty'].append({
                "@type": "PropertyValue",
                "name": name,
                "value": value
            })
    
    # Add properties
    if 'properties' in frontmatter_data:
        for name, value in frontmatter_data['properties'].items():
            jsonld['additionalProperty'].append({
                "@type": "PropertyValue",
                "name": name,
                "value": value
            })
    
    # Add chemical properties
    if 'chemicalProperties' in frontmatter_data:
        for name, value in frontmatter_data['chemicalProperties'].items():
            jsonld['additionalProperty'].append({
                "@type": "PropertyValue",
                "name": f"chemical_{name}",
                "value": value
            })
    
    # Add applications
    if 'applications' in frontmatter_data and isinstance(frontmatter_data['applications'], list):
        app_categories = []
        for app in frontmatter_data['applications']:
            if isinstance(app, dict) and 'name' in app:
                app_categories.append(app['name'])
            elif isinstance(app, str):
                app_categories.append(app)
        if app_categories:
            jsonld['applicationCategory'] = ', '.join(app_categories)
    
    # Format as script tag
    json_str = json.dumps(jsonld, indent=2)
    jsonld_script = f'<script type="application/ld+json">\n{json_str}\n</script>'
    
    # Save to file
    jsonld_output_path = 'content/components/jsonld/alumina-laser-cleaning.md'
    metadata_comment = '<!-- Category: ceramic, Article Type: material, Subject: Alumina -->'
    content = f'{metadata_comment}\n{jsonld_script}'
    
    with open(jsonld_output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Successfully generated JSON-LD content and saved to {jsonld_output_path}')
    
    # Generate metatags directly
    print("\nGenerating metatags content...")
    
    # Create metatags content
    metatags = {
        'title': 'Alumina Laser Cleaning | Technical Guide',
        'description': frontmatter_data.get('description', 'Technical guide to Alumina for laser cleaning, covering optimal parameters, applications, and environmental benefits of using laser technology on this ceramic material.'),
        'keywords': 'Alumina, laser cleaning, ceramic laser cleaning, Al₂O₃ removal, non-contact cleaning',
        'author': frontmatter_data.get('author', {}).get('author_name', 'Z-Beam'),
        'application': {
            'name': 'Alumina Laser Cleaning',
            'description': 'Removal of contaminants, oxides, and coatings from Alumina surfaces using high-precision laser technology.'
        },
        'openGraph': {
            'title': 'Alumina Laser Cleaning: Technical Guide',
            'description': 'Comprehensive technical resource on Alumina laser cleaning applications, specifications, and best practices.',
            'url': 'https://www.z-beam.com/alumina-laser-cleaning',
            'siteName': 'Z-Beam',
            'images': [
                {
                    'url': 'https://www.z-beam.com/images/material/alumina.jpg',
                    'width': 1200,
                    'height': 630,
                    'alt': 'Alumina Laser Cleaning'
                }
            ],
            'locale': 'en_US',
            'type': 'article'
        },
        'twitter': {
            'card': 'summary_large_image',
            'title': 'Alumina Laser Cleaning: Technical Guide',
            'description': 'Comprehensive technical resource on Alumina laser cleaning applications, specifications, and best practices.',
            'images': ['https://www.z-beam.com/images/material/alumina.jpg']
        }
    }
    
    # Format as YAML
    yaml_str = yaml.dump(metatags, sort_keys=False, default_flow_style=False)
    metatags_content = f'---\n{yaml_str}---'
    
    # Save to file
    metatags_output_path = 'components/metatags/alumina-laser-cleaning.md'
    metadata_comment = '<!-- Category: ceramic, Article Type: material, Subject: Alumina -->'
    content = f'{metadata_comment}\n{metatags_content}'
    
    with open(metatags_output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Successfully generated metatags content and saved to {metatags_output_path}')
    
    print("\nAll missing components have been successfully generated!")

except Exception as e:
    print(f'Error: {str(e)}')
    traceback.print_exc()
    sys.exit(1)
