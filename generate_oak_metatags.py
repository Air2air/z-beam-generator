#!/usr/bin/env python3
"""
Metatags Direct Generator

Generates meta tags directly from frontmatter for Oak material.
This is a quick solution to demonstrate the format.
"""

import yaml
from pathlib import Path
from versioning import stamp_component_output

def generate_oak_metatags():
    """Generate metatags for Oak using the example template"""
    
    # Oak metadata
    oak_metadata = {
        "title": "Oak Laser Cleaning - Complete Technical Guide for Precision Wood Restoration Methods",
        "meta_tags": [
            {"name": "description", "content": "Comprehensive oak laser cleaning guide using 1064nm wavelength technology. Professional restoration methods for wood preservation, furniture renovation, and precision surface treatment applications."},
            {"name": "keywords", "content": "oak, oak wood, laser ablation, laser cleaning, non-contact cleaning, precision laser processing, surface contamination removal, industrial laser applications, wood restoration, furniture renovation, heritage preservation, pulsed laser cleaning, wood fabrication, oxide cleaning, restoration applications, conservation applications, 1064nm laser"},
            {"name": "author", "content": "Yi-Chun Lin"},
            {"name": "category", "content": "wood"},
            {"name": "robots", "content": "index, follow, max-snippet:-1, max-image-preview:large"},
            {"name": "googlebot", "content": "index, follow, max-snippet:-1, max-image-preview:large"},
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
            {"name": "format-detection", "content": "telephone=no"},
            {"name": "theme-color", "content": "#2563eb"},
            {"name": "color-scheme", "content": "light dark"},
            {"name": "material:category", "content": "wood"},
            {"name": "laser:wavelength", "content": "1064nm"},
            {"name": "application-name", "content": "Z-Beam Laser Processing Guide"},
            {"name": "msapplication-TileColor", "content": "#2563eb"},
            {"name": "msapplication-config", "content": "/browserconfig.xml"}
        ],
        "opengraph": [
            {"property": "og:title", "content": "Oak Laser Cleaning - Complete Technical Guide"},
            {"property": "og:description", "content": "Comprehensive oak laser cleaning guide using 1064nm wavelength technology. Professional restoration methods for wood preservation and furniture renovation."},
            {"property": "og:type", "content": "article"},
            {"property": "og:image", "content": "/images/oak-laser-cleaning-hero.jpg"},
            {"property": "og:image:alt", "content": "Oak laser cleaning process showing precision wood restoration and surface treatment"},
            {"property": "og:image:width", "content": "1200"},
            {"property": "og:image:height", "content": "630"},
            {"property": "og:url", "content": "https://z-beam.com/oak-laser-cleaning"},
            {"property": "og:site_name", "content": "Z-Beam Laser Processing Guide"},
            {"property": "og:locale", "content": "en_US"},
            {"property": "article:author", "content": "Yi-Chun Lin"},
            {"property": "article:section", "content": "Wood Processing"},
            {"property": "article:tag", "content": "Oak laser cleaning"}
        ],
        "twitter": [
            {"name": "twitter:card", "content": "summary_large_image"},
            {"name": "twitter:title", "content": "Oak Laser Cleaning - Precision Restoration Guide"},
            {"name": "twitter:description", "content": "Professional oak laser cleaning using 1064nm technology. Complete guide for wood restoration, furniture renovation, and precision surface treatment."},
            {"name": "twitter:image", "content": "/images/oak-laser-cleaning-hero.jpg"},
            {"name": "twitter:image:alt", "content": "Oak wood laser cleaning technical guide"},
            {"name": "twitter:site", "content": "@z-beamTech"},
            {"name": "twitter:creator", "content": "@z-beamTech"}
        ],
        "canonical": "https://z-beam.com/oak-laser-cleaning",
        "alternate": [
            {"hreflang": "en", "href": "https://z-beam.com/oak-laser-cleaning"}
        ]
    }
    
    # Convert to YAML string with frontmatter delimiters
    yaml_content = yaml.dump(oak_metadata, default_flow_style=False, sort_keys=False, allow_unicode=True)
    content = f"---\n{yaml_content.strip()}\n---"
    
    # Apply centralized version stamping
    content = stamp_component_output("metatags", content)
    
    # Save the file
    output_dir = Path("content/components/metatags")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "oak-laser-cleaning.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"✅ Generated metatags file: {output_file}")
    
if __name__ == "__main__":
    generate_oak_metatags()
