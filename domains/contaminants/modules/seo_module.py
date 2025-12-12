"""
SEO Module - Generate SEO optimization fields for contamination frontmatter

Per CONTAMINATION_FRONTMATTER_SPEC.md Enhancement #1

Handles: seo.title, meta_description, keywords, canonical_url

Template for meta_description:
"Professional laser cleaning removes {contamination} {X}x faster than {alternative} 
with zero chemicals. Complete guide to safe {contamination} removal on 100+ materials."
"""

import logging
from typing import Dict, List


class SEOModule:
    """Generate SEO fields for contamination frontmatter"""
    
    # Speed comparisons for common contaminants (vs traditional methods)
    SPEED_MULTIPLIERS = {
        'adhesive': 3,
        'rust': 5,
        'paint': 4,
        'oil': 6,
        'oxidation': 4,
        'default': 3
    }
    
    # Alternative methods per contamination type
    ALTERNATIVE_METHODS = {
        'adhesive': 'solvents',
        'rust': 'chemical treatments',
        'paint': 'sandblasting',
        'oil': 'degreasers',
        'oxidation': 'acid pickling',
        'default': 'chemical methods'
    }
    
    def __init__(self):
        """Initialize SEO module"""
        self.logger = logging.getLogger(__name__)
    
    def generate(self, contaminant_id: str, contaminant_data: Dict) -> Dict:
        """
        Generate SEO fields for contamination frontmatter
        
        Args:
            contaminant_id: ID of contaminant
            contaminant_data: Contaminant data from Contaminants.yaml
            
        Returns:
            Dictionary with SEO fields
        """
        self.logger.info(f"Generating SEO fields for {contaminant_id}")
        
        # Get name
        name = contaminant_data.get('id', contaminant_id).replace('_', ' ').replace('-', ' ').title()
        slug = contaminant_id.lower().replace('_', '-')
        category = contaminant_data.get('category', 'contamination')
        
        # Detect contamination type for speed multiplier
        contam_type = self._detect_contaminant_type(contaminant_id)
        speed_multiplier = self.SPEED_MULTIPLIERS.get(contam_type, 3)
        alternative = self.ALTERNATIVE_METHODS.get(contam_type, 'chemical methods')
        
        # Generate meta description (150-160 chars)
        meta_description = (
            f"Professional laser cleaning removes {name.lower()} {speed_multiplier}x faster than "
            f"{alternative} with zero chemicals. Complete guide to safe {name.lower()} removal on 100+ materials."
        )
        
        # Ensure within character limit
        if len(meta_description) > 160:
            meta_description = meta_description[:157] + "..."
        
        # Generate SEO title
        seo_title = f"{name} Laser Cleaning | Complete Removal Guide"
        
        # Generate keywords
        keywords = self._generate_keywords(name, contaminant_id)
        
        # Canonical URL
        canonical_url = f"/contamination/{category}/{slug}"
        
        seo = {
            'title': seo_title,
            'meta_description': meta_description,
            'keywords': keywords,
            'canonical_url': canonical_url
        }
        
        self.logger.info(f"✅ Generated SEO fields for {name}")
        return seo
    
    def _detect_contaminant_type(self, contaminant_id: str) -> str:
        """Detect contamination type from ID"""
        id_lower = contaminant_id.lower()
        
        if 'adhesive' in id_lower or 'tape' in id_lower or 'label' in id_lower:
            return 'adhesive'
        elif 'rust' in id_lower or 'corrosion' in id_lower:
            return 'rust'
        elif 'paint' in id_lower or 'coating' in id_lower:
            return 'paint'
        elif 'oil' in id_lower or 'grease' in id_lower:
            return 'oil'
        elif 'oxidation' in id_lower or 'oxide' in id_lower:
            return 'oxidation'
        else:
            return 'default'
    
    def _generate_keywords(self, name: str, contaminant_id: str) -> List[str]:
        """Generate SEO keywords"""
        name_lower = name.lower()
        
        keywords = [
            f"{name_lower} removal",
            f"laser cleaning {name_lower}",
            f"{name_lower} laser removal",
            f"industrial {name_lower} removal",
            f"professional {name_lower} cleaning",
        ]
        
        return keywords
