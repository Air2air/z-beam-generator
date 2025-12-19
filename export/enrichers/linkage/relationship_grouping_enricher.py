"""
Relationship Grouping Enricher - Organize flat relationship lists into semantic groups

Enricher that transforms flat relationship lists into grouped structures with:
- Semantic keys (e.g., organic_residues, metals, plastics_polymers)
- Human-readable titles
- Descriptive text explaining each group

This runs AFTER DomainLinkagesEnricher populates relationships.

Created: December 18, 2025
Part of: Relationship Grouping Enhancement
"""

import logging
from typing import Dict, Any, List

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class RelationshipGroupingEnricher(BaseEnricher):
    """
    Organize flat relationship lists into semantic groups.
    
    Transforms:
        relationships:
          related_contaminants: [48 flat items]
    
    Into:
        relationships:
          contaminants:
            title: "Common Contaminants"
            description: "..."
            groups:
              organic_residues:
                title: "Organic Residues"
                description: "..."
                items: [10 items]
              oxidation_corrosion:
                title: "Oxidation & Corrosion"
                description: "..."
                items: [8 items]
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize relationship grouping enricher.
        
        Args:
            config: Configuration dict with 'domain' key (required)
        """
        super().__init__(config)
        
        # Domain is required
        if 'domain' not in config:
            raise ValueError("RelationshipGroupingEnricher requires 'domain' in config")
        
        self.domain = config['domain']
        logger.info(f"Initialized RelationshipGroupingEnricher for domain: {self.domain}")
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform flat relationships into grouped structure.
        
        Args:
            frontmatter: Input frontmatter dict with relationships
        
        Returns:
            Frontmatter with grouped relationships
        """
        print(f"🎯 RelationshipGroupingEnricher.enrich() for {frontmatter.get('id', 'unknown')}")
        
        relationships = frontmatter.get('relationships', {})
        if not relationships:
            logger.debug("No relationships to group")
            return frontmatter
        
        # Group by domain
        if self.domain == 'materials':
            grouped = self._group_materials_relationships(relationships)
        elif self.domain == 'contaminants':
            grouped = self._group_contaminants_relationships(relationships)
        elif self.domain == 'compounds':
            grouped = self._group_compounds_relationships(relationships)
        elif self.domain == 'settings':
            grouped = self._group_settings_relationships(relationships)
        else:
            logger.warning(f"Unknown domain: {self.domain}, skipping grouping")
            return frontmatter
        
        # Update frontmatter
        frontmatter['relationships'] = grouped
        
        # Count groups
        total_groups = sum(
            len(section.get('groups', {})) 
            for section in grouped.values() 
            if isinstance(section, dict) and 'groups' in section
        )
        print(f"   ✅ Created {len(grouped)} sections with {total_groups} total groups")
        
        return frontmatter
    
    def _group_materials_relationships(self, relationships: Dict[str, Any]) -> Dict[str, Any]:
        """
        Group materials domain relationships.
        
        Input:
          related_contaminants: [48 items]
          regulatory_standards: [N items]
        
        Output:
          contaminants:
            title: "Common Contaminants"
            description: "..."
            groups:
              organic_residues: {...}
              oxidation_corrosion: {...}
              coatings_treatments: {...}
              industrial_deposits: {...}
              biological_growth: {...}
              thermal_damage: {...}
          regulatory:
            title: "Regulatory Standards"
            description: "..."
            groups:
              occupational_safety: {...}
              environmental_compliance: {...}
              industry_standards: {...}
        """
        grouped = {}
        
        # Group contaminants by category
        contaminants = relationships.get('related_contaminants', [])
        if contaminants:
            grouped['contaminants'] = {
                'title': 'Common Contaminants',
                'description': 'Contaminants that frequently occur on this material during industrial use and require laser cleaning removal',
                'groups': self._group_by_category(contaminants, {
                    'organic_residues': {
                        'title': 'Organic Residues',
                        'description': 'Adhesives, lubricants, oils, and other carbon-based deposits',
                        'categories': ['organic-residue']
                    },
                    'oxidation_corrosion': {
                        'title': 'Oxidation & Corrosion',
                        'description': 'Surface oxidation, rust, and corrosion products specific to this material',
                        'categories': ['oxidation', 'corrosion']
                    },
                    'coatings_treatments': {
                        'title': 'Coatings & Surface Treatments',
                        'description': 'Applied coatings, anodizing, plating, and surface treatment layers',
                        'categories': ['metallic-coating', 'inorganic-coating', 'coating']
                    },
                    'industrial_deposits': {
                        'title': 'Industrial Deposits',
                        'description': 'Manufacturing residues, machining compounds, and industrial process byproducts',
                        'categories': ['deposit', 'mineral', 'industrial']
                    },
                    'biological_growth': {
                        'title': 'Biological Growth',
                        'description': 'Algae, lichen, biofilms, and other organic growth',
                        'categories': ['biological']
                    },
                    'thermal_damage': {
                        'title': 'Thermal Damage',
                        'description': 'Heat-induced scale, oxidation, and thermal degradation products',
                        'categories': ['thermal-damage', 'scale']
                    },
                    'chemical_residue': {
                        'title': 'Chemical Residues',
                        'description': 'Chemical stains, etching, and industrial chemical deposits',
                        'categories': ['chemical-residue']
                    }
                })
            }
        
        # Group regulatory standards
        regulatory = relationships.get('regulatory_standards', [])
        if regulatory:
            grouped['regulatory'] = {
                'title': 'Regulatory Standards',
                'description': 'Safety, environmental, and industry standards applicable to laser cleaning this material',
                'groups': {
                    'all_standards': {
                        'title': 'Applicable Standards',
                        'description': 'All regulatory standards and guidelines',
                        'items': regulatory
                    }
                }
            }
        
        return grouped
    
    def _group_contaminants_relationships(self, relationships: Dict[str, Any]) -> Dict[str, Any]:
        """
        Group contaminants domain relationships.
        
        Input:
          related_materials: [32-45 items]
        
        Output:
          materials:
            title: "Affected Materials"
            description: "..."
            groups:
              metals: {...}
              plastics_polymers: {...}
              wood_natural: {...}
              stone_masonry: {...}
              composites_advanced: {...}
        """
        grouped = {}
        
        # Group materials by category
        materials = relationships.get('related_materials', [])
        if materials:
            grouped['materials'] = {
                'title': 'Affected Materials',
                'description': 'Materials where this contaminant commonly occurs and can be removed via laser cleaning',
                'groups': self._group_by_category(materials, {
                    'metals': {
                        'title': 'Metals',
                        'description': 'Ferrous and non-ferrous metals including steel, aluminum, copper, and alloys',
                        'categories': ['metal']
                    },
                    'plastics_polymers': {
                        'title': 'Plastics & Polymers',
                        'description': 'Thermoplastics, thermosets, elastomers, and composite materials',
                        'categories': ['plastic', 'polymer']
                    },
                    'wood_natural': {
                        'title': 'Wood & Natural Materials',
                        'description': 'Hardwoods, softwoods, bamboo, and other natural organic materials',
                        'categories': ['wood']
                    },
                    'stone_masonry': {
                        'title': 'Stone & Masonry',
                        'description': 'Natural stone, concrete, brick, and masonry materials',
                        'categories': ['stone', 'masonry', 'concrete']
                    },
                    'composites_advanced': {
                        'title': 'Composites & Advanced Materials',
                        'description': 'Carbon fiber, fiberglass, laminates, and engineered composite materials',
                        'categories': ['composite']
                    },
                    'ceramics_glass': {
                        'title': 'Ceramics & Glass',
                        'description': 'Ceramic materials, glass, and vitreous surfaces',
                        'categories': ['ceramic', 'glass']
                    }
                })
            }
        
        return grouped
    
    def _group_compounds_relationships(self, relationships: Dict[str, Any]) -> Dict[str, Any]:
        """
        Group compounds domain relationships.
        
        Input:
          produced_by_contaminants: [items]
          chemical_properties: [items]
          health_effects: [items]
          environmental_impact: [items]
          detection_monitoring: [items]
          ppe_requirements: [items]
          emergency_response: [items]
        
        Output:
          sources: {...}
          chemical_data: {...}
          health_safety: {...}
          environmental: {...}
          detection: {...}
          protection: {...}
          emergency: {...}
        """
        grouped = {}
        
        # Map flat keys to grouped structure
        mapping = {
            'produced_by_contaminants': {
                'key': 'sources',
                'title': 'Contamination Sources',
                'description': 'Contaminants that produce this compound when ablated by laser cleaning'
            },
            'chemical_properties': {
                'key': 'chemical_data',
                'title': 'Chemical Properties',
                'description': 'Physical and chemical characteristics including molecular structure, reactivity, and behavior'
            },
            'health_effects': {
                'key': 'health_safety',
                'title': 'Health Effects',
                'description': 'Toxicological data, exposure limits, symptoms, and health impacts'
            },
            'environmental_impact': {
                'key': 'environmental',
                'title': 'Environmental Impact',
                'description': 'Atmospheric behavior, persistence, ecological effects, and environmental fate'
            },
            'detection_monitoring': {
                'key': 'detection',
                'title': 'Detection & Monitoring',
                'description': 'Sensors, monitoring methods, detection limits, and measurement techniques'
            },
            'ppe_requirements': {
                'key': 'protection',
                'title': 'PPE Requirements',
                'description': 'Personal protective equipment specifications for handling exposure scenarios'
            },
            'emergency_response': {
                'key': 'emergency',
                'title': 'Emergency Response',
                'description': 'First aid procedures, emergency protocols, and incident response guidance'
            }
        }
        
        for old_key, config in mapping.items():
            items = relationships.get(old_key, [])
            if items:
                grouped[config['key']] = {
                    'title': config['title'],
                    'description': config['description'],
                    'items': items
                }
        
        return grouped
    
    def _group_settings_relationships(self, relationships: Dict[str, Any]) -> Dict[str, Any]:
        """
        Group settings domain relationships.
        
        Input:
          related_materials: [items]
          related_contaminants: [items]
          regulatory_standards: [items]
        
        Output:
          materials:
            title: "Applicable Materials"
            groups:
              all_materials: {...}
          contaminants:
            title: "Target Contaminants"
            groups:
              organic_residues: {...}
              oxidation_products: {...}
          regulatory:
            title: "Regulatory Standards"
            groups:
              all_standards: {...}
        """
        grouped = {}
        
        # Materials (simple group - all in one)
        materials = relationships.get('related_materials', [])
        if materials:
            grouped['materials'] = {
                'title': 'Applicable Materials',
                'description': 'Materials that use these laser parameter settings for optimal cleaning results',
                'groups': {
                    'all_materials': {
                        'title': 'Compatible Materials',
                        'description': 'All materials suitable for these laser parameters',
                        'items': materials
                    }
                }
            }
        
        # Contaminants (group by category)
        contaminants = relationships.get('related_contaminants', [])
        if contaminants:
            grouped['contaminants'] = {
                'title': 'Target Contaminants',
                'description': 'Contaminants effectively removed using these laser parameter settings',
                'groups': self._group_by_category(contaminants, {
                    'organic_residues': {
                        'title': 'Organic Residues',
                        'description': 'Carbon-based deposits and organic contamination',
                        'categories': ['organic-residue']
                    },
                    'oxidation_products': {
                        'title': 'Oxidation Products',
                        'description': 'Surface oxidation and corrosion layers',
                        'categories': ['oxidation', 'corrosion']
                    },
                    'coatings': {
                        'title': 'Coatings & Treatments',
                        'description': 'Surface coatings and treatment layers',
                        'categories': ['coating', 'metallic-coating', 'inorganic-coating']
                    }
                })
            }
        
        # Regulatory (simple group - all in one)
        regulatory = relationships.get('regulatory_standards', [])
        if regulatory:
            grouped['regulatory'] = {
                'title': 'Regulatory Standards',
                'description': 'Safety and operational standards governing use of these laser parameters',
                'groups': {
                    'all_standards': {
                        'title': 'Applicable Standards',
                        'description': 'All regulatory standards and guidelines',
                        'items': regulatory
                    }
                }
            }
        
        return grouped
    
    def _group_by_category(
        self, 
        items: List[Dict[str, Any]], 
        group_definitions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Group items by their category field.
        
        Args:
            items: List of relationship items with 'category' field
            group_definitions: Dict mapping group_key to {title, description, categories}
        
        Returns:
            Dict of groups with items
        """
        groups = {}
        ungrouped = []
        
        # Initialize all groups
        for group_key, group_def in group_definitions.items():
            groups[group_key] = {
                'title': group_def['title'],
                'description': group_def['description'],
                'items': []
            }
        
        # Assign items to groups
        for item in items:
            category = item.get('category', '').lower()
            assigned = False
            
            for group_key, group_def in group_definitions.items():
                if category in group_def['categories']:
                    groups[group_key]['items'].append(item)
                    assigned = True
                    break
            
            if not assigned:
                ungrouped.append(item)
        
        # Add "Other" group if there are ungrouped items
        if ungrouped:
            groups['other'] = {
                'title': 'Other',
                'description': 'Additional items not categorized above',
                'items': ungrouped
            }
        
        # Remove empty groups
        groups = {k: v for k, v in groups.items() if v['items']}
        
        return groups
