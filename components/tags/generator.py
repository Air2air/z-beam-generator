#!/usr/bin/env python3
"""
Tags Generator - Generate application-focused tags for laser cleaning materials.
"""

import yaml
import os
from pathlib import Path
from typing import List, Dict, Any

# Import slug utilities for consistent naming
try:
    from utils.slug_utils import create_material_slug, create_filename_slug
except ImportError:
    # Fallback to basic slug generation if utils not available
    def create_material_slug(name: str) -> str:
        return name.lower().replace(' ', '-').replace('_', '-').replace('(', '').replace(')', '')
    def create_filename_slug(name: str, suffix: str = "laser-cleaning") -> str:
        slug = create_material_slug(name)
        return f"{slug}-{suffix}" if suffix else slug

class TagsGenerator:
    """Enhanced tags generator using material-specific tag categories"""
    
    def __init__(self):
        self.material_tags = self._load_material_specific_tags()
        self.application_tags = self._load_application_tags()
        self.process_tags = self._load_process_tags()
        self.author_context = self._load_author_context()
        
    def _load_material_specific_tags(self) -> Dict[str, Dict[str, List[str]]]:
        """Load material category specific tag mappings"""
        return {
            'metal': {
                'contaminants': ['corrosion', 'oxidation', 'rust', 'coating', 'welding-residue', 'scale'],
                'applications': ['aerospace', 'automotive', 'manufacturing', 'marine', 'construction'],
                'benefits': ['precision', 'selective', 'material-preservation', 'weld-prep', 'surface-prep']
            },
            'ceramic': {
                'contaminants': ['firing-residue', 'contamination', 'glaze-defects', 'surface-deposits'],
                'applications': ['electronics', 'aerospace', 'medical', 'industrial', 'research'],
                'benefits': ['precision', 'micro-scale', 'controlled-removal', 'surface-integrity']
            },
            'glass': {
                'contaminants': ['etching-marks', 'residue', 'films', 'deposits', 'contamination'],
                'applications': ['optical', 'electronics', 'automotive', 'architectural', 'solar'],
                'benefits': ['clarity-restoration', 'optical-quality', 'precision', 'transparency']
            },
            'composite': {
                'contaminants': ['matrix-degradation', 'surface-contamination', 'bond-inhibitors', 'residue'],
                'applications': ['aerospace', 'automotive', 'marine', 'wind-energy', 'sports'],
                'benefits': ['fiber-preservation', 'bond-preparation', 'selective', 'damage-free']
            },
            'stone': {
                'contaminants': ['organics', 'soot', 'weathering', 'graffiti', 'biological-growth', 'pollution'],
                'applications': ['restoration', 'heritage', 'conservation', 'archaeology', 'construction'],
                'benefits': ['preservation', 'non-invasive', 'reversible', 'material-conservation']
            },
            'masonry': {
                'contaminants': ['efflorescence', 'biological-growth', 'pollution', 'coatings', 'weathering'],
                'applications': ['restoration', 'construction', 'heritage', 'maintenance', 'conservation'],
                'benefits': ['preservation', 'structural-integrity', 'aesthetic-restoration', 'gentle']
            },
            'wood': {
                'contaminants': ['paint', 'char', 'stains', 'coatings', 'surface-damage'],
                'applications': ['restoration', 'furniture', 'construction', 'heritage', 'refinishing'],
                'benefits': ['grain-preservation', 'controlled-depth', 'gentle', 'eco-friendly']
            },
            'semiconductor': {
                'contaminants': ['particles', 'films', 'oxides', 'contamination', 'residue'],
                'applications': ['electronics', 'fabrication', 'research', 'micro-manufacturing', 'precision'],
                'benefits': ['precision', 'particle-free', 'micro-scale', 'controlled', 'chemical-free']
            },
            'plastic': {
                'contaminants': ['flash', 'contamination', 'surface-defects', 'coatings', 'adhesive-residue'],
                'applications': ['automotive', 'electronics', 'medical', 'manufacturing', 'packaging'],
                'benefits': ['selective', 'gentle', 'precise', 'surface-prep', 'damage-free']
            }
        }
    
    def _load_application_tags(self) -> Dict[str, List[str]]:
        """Load application-specific tag categories"""
        return {
            'heritage': ['restoration', 'conservation', 'archaeology', 'cultural', 'historic'],
            'industrial': ['manufacturing', 'quality-control', 'maintenance', 'surface-prep', 'production'],
            'precision': ['micro-fabrication', 'electronics', 'optical', 'research', 'controlled'],
            'environmental': ['chemical-free', 'eco-friendly', 'sustainable', 'waste-reduction', 'green']
        }
    
    def _load_process_tags(self) -> List[str]:
        """Load process benefit tags"""
        return [
            'non-contact', 'precision', 'selective', 'controlled', 'gentle',
            'chemical-free', 'eco-friendly', 'reversible', 'automated',
            'fast-processing', 'minimal-waste', 'surface-integrity'
        ]
    
    def _load_author_context(self) -> Dict[str, Dict[str, Any]]:
        """Load author-specific context for tag selection"""
        return {
            'yi-chun-lin': {
                'expertise': ['electronics', 'precision', 'semiconductor', 'fabrication'],
                'regional_focus': ['micro-scale', 'high-tech', 'manufacturing'],
                'preferred_applications': ['electronics', 'fabrication', 'precision', 'research']
            },
            'alessandro-moretti': {
                'expertise': ['heritage', 'restoration', 'industrial', 'manufacturing'],
                'regional_focus': ['cultural', 'conservation', 'traditional'],
                'preferred_applications': ['restoration', 'heritage', 'manufacturing', 'construction']
            }
        }
    
    def extract_frontmatter_data(self, material_slug):
        """Extract material name, category, and author from frontmatter file."""
        # Build the correct path to the frontmatter file using clean slug
        frontmatter_file = f"content/components/frontmatter/{material_slug}-laser-cleaning.md"
        
        try:
            with open(frontmatter_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    yaml_content = parts[1]
                    data = yaml.safe_load(yaml_content)
                    
                    material_name = data.get('name', '')
                    category = data.get('category', '')
                    author_name = data.get('author', '')
                    
                    return material_name, category, author_name
            
            return None, None, None
        except Exception as e:
            print(f"Error reading frontmatter file {frontmatter_file}: {e}")
            return None, None, None
    
    def _extract_author_slug(self, author_field: str) -> str:
        """Extract author slug from author field"""
        if not author_field:
            return 'unknown-author'
            
        # Extract name before " from " if present
        if ' from ' in author_field:
            name = author_field.split(' from ')[0].strip()
        else:
            name = author_field.strip()
            
        # Convert to slug format
        return name.lower().replace(' ', '-').replace('.', '').strip('-')
    
    def generate_tags(self, material_slug: str) -> List[str]:
        """Generate 8 tags for a material based on frontmatter data"""
        
        # Extract frontmatter data
        result = self.extract_frontmatter_data(material_slug)
        if not result or len(result) != 3:
            print(f"Could not extract frontmatter data for {material_slug}")
            return self._generate_fallback_tags(material_slug)
        
        material_name, category, author_name = result
        author_slug = author_name.lower().replace(' ', '-') if author_name else 'unknown'
        
        tags = []
        used_tags = set()  # Track used tags to avoid duplicates
        
        # 1. Material identifier (material name or category)
        material_tag = self._get_material_tag(material_name, material_slug)
        tags.append(material_tag)
        used_tags.add(material_tag)
        
        # 2-3. Applications (2 tags)
        application_tags = self._select_applications(category, author_slug)
        for tag in application_tags[:2]:
            if tag not in used_tags:
                tags.append(tag)
                used_tags.add(tag)
        
        # 4-5. Contaminants/Problems (2 tags)
        contaminant_tags = self._select_contaminants(category, author_slug)
        for tag in contaminant_tags[:2]:
            if tag not in used_tags:
                tags.append(tag)
                used_tags.add(tag)
        
        # 6. Process benefit
        benefit_tag = self._select_benefit(category, author_slug)
        if benefit_tag not in used_tags:
            tags.append(benefit_tag)
            used_tags.add(benefit_tag)
        
        # 7. Method characteristic
        method_tag = self._select_method(category, author_slug)
        if method_tag not in used_tags:
            tags.append(method_tag)
            used_tags.add(method_tag)
        
        # Fill remaining slots if needed
        while len(tags) < 7:
            backup_tags = ['controlled', 'surface-prep', 'quality', 'efficient', 'reliable']
            for backup_tag in backup_tags:
                if backup_tag not in used_tags:
                    tags.append(backup_tag)
                    used_tags.add(backup_tag)
                    break
            else:
                break  # No more backup tags available
        
        # 8. Author (always last)
        tags.append(author_slug)
        
        return tags[:8]  # Ensure exactly 8 tags
    
    def _get_material_tag(self, material_name: str, material_slug: str) -> str:
        """Get the primary material identifier tag"""
        # Use the slug as the primary identifier
        return material_slug.split('-')[0] if '-' in material_slug else material_slug
    
    def _select_applications(self, category: str, author_slug: str) -> List[str]:
        """Select 2 application tags based on category and author"""
        category_apps = self.material_tags.get(category, {}).get('applications', [])
        author_context = self.author_context.get(author_slug, {})
        author_apps = author_context.get('preferred_applications', [])
        
        # Combine and prioritize author preferences
        all_apps = author_apps + category_apps
        
        # Remove duplicates while preserving order
        seen = set()
        unique_apps = []
        for app in all_apps:
            if app not in seen:
                unique_apps.append(app)
                seen.add(app)
        
        return unique_apps[:2] if unique_apps else ['manufacturing', 'industrial']
    
    def _select_contaminants(self, category: str, author_slug: str) -> List[str]:
        """Select 2 contaminant/problem tags"""
        contaminants = self.material_tags.get(category, {}).get('contaminants', [])
        
        # Select most common contaminants for the material category
        if not contaminants:
            contaminants = ['contamination', 'surface-deposits']
            
        return contaminants[:2]
    
    def _select_benefit(self, category: str, author_slug: str) -> str:
        """Select primary process benefit"""
        benefits = self.material_tags.get(category, {}).get('benefits', [])
        author_context = self.author_context.get(author_slug, {})
        
        # Prioritize based on author expertise
        if 'precision' in author_context.get('expertise', []) and 'precision' in benefits:
            return 'precision'
        elif 'heritage' in author_context.get('expertise', []) and 'preservation' in benefits:
            return 'preservation'
        elif benefits:
            return benefits[0]
        else:
            return 'controlled'
    
    def _select_method(self, category: str, author_slug: str) -> str:
        """Select method characteristic"""
        # Standard method characteristics by category
        method_map = {
            'stone': 'non-invasive',
            'masonry': 'gentle',
            'metal': 'selective',
            'ceramic': 'precision',
            'glass': 'optical-quality',
            'semiconductor': 'chemical-free',
            'composite': 'damage-free',
            'wood': 'eco-friendly',
            'plastic': 'surface-prep'
        }
        
        return method_map.get(category, 'non-contact')
    
    def _generate_fallback_tags(self, material_slug: str) -> List[str]:
        """Generate fallback tags when frontmatter is unavailable"""
        return [
            material_slug.split('-')[0],
            'manufacturing',
            'industrial', 
            'contamination',
            'surface-cleaning',
            'precision',
            'non-contact',
            'technical-expert'
        ]
    
    def generate_tags_content(self, material_slug: str) -> str:
        """Generate the complete tags file content"""
        tags = self.generate_tags(material_slug)
        return ', '.join(tags)


def main():
    """Command line interface for tags generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate enhanced tags for laser cleaning materials")
    parser.add_argument("material_slug", nargs='?', help="Material slug (e.g., 'alumina')")
    parser.add_argument("--regenerate-all", action="store_true", help="Regenerate all existing tags")
    
    args = parser.parse_args()
    
    generator = TagsGenerator()
    
    if args.regenerate_all:
        # Find all existing frontmatter files and regenerate their tags
        frontmatter_dir = Path("content/components/frontmatter")
        tags_dir = Path("content/components/tags")
        tags_dir.mkdir(exist_ok=True)
        
        regenerated = 0
        for frontmatter_file in frontmatter_dir.glob("*-laser-cleaning.md"):
            material_slug = frontmatter_file.stem.replace("-laser-cleaning", "")
            
            try:
                tags_content = generator.generate_tags_content(material_slug)
                tags_file = tags_dir / f"{material_slug}-laser-cleaning.md"
                
                with open(tags_file, 'w', encoding='utf-8') as f:
                    f.write(tags_content)
                
                print(f"✅ {material_slug}: {tags_content}")
                regenerated += 1
                
            except Exception as e:
                print(f"❌ {material_slug}: Error - {e}")
        
        print(f"\n🎯 Regenerated {regenerated} tag files")
    
    elif args.material_slug:
        # Generate tags for single material
        tags_content = generator.generate_tags_content(args.material_slug)
        print(tags_content)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
