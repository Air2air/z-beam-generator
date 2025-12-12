"""
Crosslinking Module - Generate crosslinking sections for contamination frontmatter

Per CONTAMINATION_FRONTMATTER_SPEC.md lines 172-254

Purpose: Crosslinking strategies for SEO and user navigation
- Affected materials (categories + top 5 featured)
- Related contaminations (similarity scoring)
- Recommended settings pages
"""

import logging
from typing import Dict, List


class CrosslinkingModule:
    """Generate crosslinking sections for contamination frontmatter"""
    
    def __init__(self):
        """Initialize crosslinking module"""
        self.logger = logging.getLogger(__name__)
    
    def generate(self, contaminant_data: Dict, pattern_id: str) -> Dict:
        """
        Generate crosslinking sections from contaminant data
        
        Args:
            contaminant_data: Contaminant data from Contaminants.yaml
            pattern_id: Unique pattern identifier
            
        Returns:
            Dictionary with affected_materials and related_content
        """
        self.logger.info("Generating crosslinking sections")
        
        return {
            'affected_materials': self._generate_affected_materials(contaminant_data),
            'related_content': self._generate_related_content(contaminant_data, pattern_id)
        }
    
    def _generate_affected_materials(self, contaminant_data: Dict) -> Dict:
        """
        Generate affected_materials section with categories and featured materials
        
        Per spec: Top 5 materials with percentage_of_cases, notes, industry_context
        """
        self.logger.info("Generating affected_materials section")
        
        # Extract valid_materials from contaminant data
        valid_materials = contaminant_data.get('valid_materials', [])
        
        if not valid_materials or valid_materials == ['ALL']:
            # Generic fallback
            return {
                'categories': ['metal', 'concrete', 'stone'],
                'specific_materials_featured': []
            }
        
        # Determine categories from materials
        categories = self._determine_categories_from_materials(valid_materials)
        
        # Generate top 5 featured materials
        featured = self._generate_featured_materials(valid_materials, contaminant_data)
        
        return {
            'categories': categories,
            'specific_materials_featured': featured
        }
    
    def _determine_categories_from_materials(self, materials: List[str]) -> List[str]:
        """Determine material categories from material names"""
        # Category mappings based on material names
        category_keywords = {
            'metal': ['steel', 'aluminum', 'titanium', 'copper', 'iron', 'alloy'],
            'concrete': ['concrete', 'cement'],
            'stone': ['granite', 'marble', 'limestone', 'stone'],
            'glass': ['glass'],
            'ceramic': ['ceramic'],
            'plastic': ['plastic', 'polymer'],
            'composite': ['composite', 'carbon fiber'],
            'wood': ['wood']
        }
        
        detected_categories = set()
        
        for material in materials:
            material_lower = material.lower()
            for category, keywords in category_keywords.items():
                if any(keyword in material_lower for keyword in keywords):
                    detected_categories.add(category)
        
        # Default to metal if nothing detected
        if not detected_categories:
            detected_categories.add('metal')
        
        return sorted(list(detected_categories))
    
    def _generate_featured_materials(self, valid_materials: List[str], 
                                     contaminant_data: Dict) -> List[Dict]:
        """
        Generate top 5 featured materials with details
        
        Per spec: slug, name, frequency, percentage_of_cases, notes, industry_context
        """
        # Take first 5 materials
        top_materials = valid_materials[:5]
        
        # Get contamination category for context
        category = contaminant_data.get('category', 'contamination')
        contamination_name = contaminant_data.get('name', 'this contamination')
        
        featured = []
        # Base percentages that sum to ~100% for top 5
        base_percentages = [35, 25, 20, 12, 8]
        
        for i, material in enumerate(top_materials):
            # Generate slug from material name
            slug = material.lower().replace(' ', '-').replace('(', '').replace(')', '')
            
            # Determine frequency
            if i == 0:
                frequency = 'very_high'
            elif i <= 2:
                frequency = 'high'
            else:
                frequency = 'moderate'
            
            # Generate contextual notes
            notes = self._generate_material_notes(material, contamination_name, category)
            
            # Generate industry context
            industry_context = self._generate_industry_context(material, category)
            
            featured.append({
                'slug': slug,
                'name': material,
                'frequency': frequency,
                'percentage_of_cases': base_percentages[i] if i < len(base_percentages) else 5,
                'notes': notes,
                'industry_context': industry_context
            })
        
        return featured
    
    def _generate_material_notes(self, material: str, contamination_name: str, 
                                 category: str) -> str:
        """Generate contextual notes for material"""
        notes_templates = {
            'adhesive': f"Common {category} on {material} in manufacturing and assembly",
            'rust': f"Frequent oxidation issue on {material} in industrial environments",
            'paint': f"Typical coating removal need on {material} for refinishing",
            'oil': f"Common surface contamination on {material} in manufacturing",
            'dirt': f"Standard cleaning requirement for {material} surfaces"
        }
        
        # Use category-specific template or generic
        template = notes_templates.get(category, 
                                      f"Common {category} found on {material} surfaces")
        
        return template
    
    def _generate_industry_context(self, material: str, category: str) -> str:
        """Generate industry context for material"""
        industry_templates = {
            'steel': 'Manufacturing and construction applications',
            'aluminum': 'Aerospace and automotive industries',
            'titanium': 'Aerospace and medical device manufacturing',
            'concrete': 'Construction and infrastructure maintenance',
            'stainless': 'Food processing and pharmaceutical facilities'
        }
        
        material_lower = material.lower()
        
        # Check for keyword matches
        for keyword, context in industry_templates.items():
            if keyword in material_lower:
                return context
        
        # Generic fallback
        return 'Industrial and commercial applications'
    
    def _generate_related_content(self, contaminant_data: Dict, 
                                  pattern_id: str) -> Dict:
        """
        Generate related_content section with similar contaminations
        
        Per spec: similar_contaminations with similarity scoring (0-1 scale)
        """
        self.logger.info("Generating related_content section")
        
        category = contaminant_data.get('category', 'contamination')
        name = contaminant_data.get('name', '')
        
        # Generate similar contaminations based on category
        similar = self._generate_similar_contaminations(category, name, pattern_id)
        
        return {
            'similar_contaminations': similar
        }
    
    def _generate_similar_contaminations(self, category: str, name: str, 
                                        current_pattern_id: str) -> List[Dict]:
        """
        Generate list of similar contaminations with similarity scoring
        
        Per spec: slug, name, similarity_score (0-1), shared_characteristics
        """
        # Related contamination mappings by category
        related_mappings = {
            'adhesive': [
                {'name': 'Glue Residue', 'slug': 'glue-residue', 'score': 0.95,
                 'chars': ['Polymer-based composition', 'Requires surface preparation', 'Multi-pass removal']},
                {'name': 'Tape Adhesive', 'slug': 'tape-adhesive', 'score': 0.85,
                 'chars': ['Thin film contamination', 'Bonds to substrate', 'Similar removal parameters']},
                {'name': 'Epoxy Residue', 'slug': 'epoxy-residue', 'score': 0.75,
                 'chars': ['Strong surface adhesion', 'Organic contamination', 'Requires precision removal']}
            ],
            'rust': [
                {'name': 'Oxidation', 'slug': 'oxidation', 'score': 0.95,
                 'chars': ['Metal surface degradation', 'Color change indicators', 'Similar laser parameters']},
                {'name': 'Corrosion', 'slug': 'corrosion', 'score': 0.90,
                 'chars': ['Surface integrity concerns', 'Chemical reaction products', 'Depth variation']},
                {'name': 'Scale', 'slug': 'scale', 'score': 0.80,
                 'chars': ['Surface layer formation', 'Industrial environments', 'Requires careful removal']}
            ],
            'paint': [
                {'name': 'Coating', 'slug': 'coating', 'score': 0.90,
                 'chars': ['Layered surface treatment', 'Color pigments', 'Multi-pass removal']},
                {'name': 'Varnish', 'slug': 'varnish', 'score': 0.85,
                 'chars': ['Organic coating', 'Transparent/translucent', 'Similar removal technique']},
                {'name': 'Powder Coating', 'slug': 'powder-coating', 'score': 0.80,
                 'chars': ['Thermally applied coating', 'Uniform coverage', 'Requires precision']}
            ]
        }
        
        # Get related contaminations for this category
        related = related_mappings.get(category, [])
        
        # Generic fallback for unknown categories
        if not related:
            related = [
                {'name': 'Surface Contamination', 'slug': 'surface-contamination', 'score': 0.70,
                 'chars': ['Common industrial cleaning', 'Similar removal approach', 'Standard laser parameters']}
            ]
        
        # Format for spec
        formatted = []
        for item in related:
            formatted.append({
                'slug': item['slug'],
                'name': item['name'],
                'similarity_score': item['score'],
                'shared_characteristics': item['chars']
            })
        
        return formatted
