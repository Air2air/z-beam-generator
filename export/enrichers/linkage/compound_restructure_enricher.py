"""
Compound Frontmatter Restructure Enricher

Transforms compound frontmatter from flat structure to grouped relationships structure.
Implements the specification in docs/COMPOUND_FRONTMATTER_RESTRUCTURE_SPEC.md.

MIGRATION:
- Moves 15 top-level sections into relationships.*
- Removes reference arrays from relationships
- Adds cross-references (produced_by_contaminants, found_on_materials)
- Keeps only metadata and identifiers at top-level

Created: December 18, 2025
Part of: Compound Frontmatter Restructure (Phase 1)
"""

from typing import Dict, Any, List
import logging

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class CompoundRestructureEnricher(BaseEnricher):
    """
    Enricher that restructures compound frontmatter to match materials/contaminants pattern.
    
    Moves technical data from top-level into relationships.* structure.
    """
    
    # Fields that STAY at top-level (page metadata + identifiers)
    TOP_LEVEL_FIELDS = {
        'id', 'name', 'display_name', 'category', 'subcategory', 
        'hazard_class', 'datePublished', 'dateModified', 'content_type',
        'schema_version', 'full_path', 'breadcrumb',
        'chemical_formula', 'cas_number', 'molecular_weight',
        'description', 'health_effects', 'exposure_guidelines',
        'detection_methods', 'first_aid', 'author'
    }
    
    # Fields to move from top-level → relationships
    RELATIONSHIP_MAPPINGS = {
        # Simple moves (field name stays same)
        'ppe_requirements': 'ppe_requirements',
        'emergency_response': 'emergency_response',
        'storage_requirements': 'storage_requirements',
        'regulatory_classification': 'regulatory_classification',
        'workplace_exposure': 'workplace_exposure',
        'synonyms_identifiers': 'synonyms_identifiers',
        'reactivity': 'reactivity',
        'environmental_impact': 'environmental_impact',
        'detection_monitoring': 'detection_monitoring',
        
        # Renamed moves
        'physical_properties': 'chemical_properties',
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enricher.
        
        Args:
            config: Enricher config (unused, but required by interface)
        """
        super().__init__(config)
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restructure compound frontmatter from flat to grouped.
        
        Args:
            frontmatter: Input frontmatter dict
            
        Returns:
            Restructured frontmatter with relationships grouping
        """
        # Get or create relationships dict
        if 'relationships' not in frontmatter:
            frontmatter['relationships'] = {}
        
        relationships = frontmatter['relationships']
        
        # 1. Move simple top-level fields to relationships
        self._move_simple_fields(frontmatter, relationships)
        
        # 2. Create exposure_limits group (combines multiple fields)
        self._create_exposure_limits_group(frontmatter, relationships)
        
        # 3. Create health_hazards group (restructures health_effects_keywords)
        self._create_health_hazards_group(frontmatter, relationships)
        
        # 4. Create production_sources group (restructures sources_in_laser_cleaning)
        self._create_production_sources_group(frontmatter, relationships)
        
        # 5. Clear old reference arrays from relationships (if they exist)
        self._clear_reference_arrays(relationships)
        
        # 6. Add cross-references (placeholder structure - will be populated by linkage enrichers)
        self._add_cross_reference_placeholders(relationships)
        
        # 7. Rename relationships (Change 3 - standardize naming - Dec 19, 2025)
        self._rename_relationships(relationships)
        
        logger.debug(f"Restructured compound frontmatter: {frontmatter.get('id', 'unknown')}")
        
        return frontmatter
    
    def _move_simple_fields(
        self, 
        frontmatter: Dict[str, Any], 
        relationships: Dict[str, Any]
    ) -> None:
        """Move simple top-level fields to relationships."""
        for source_field, target_field in self.RELATIONSHIP_MAPPINGS.items():
            if source_field in frontmatter and source_field not in self.TOP_LEVEL_FIELDS:
                # Move to relationships
                relationships[target_field] = frontmatter.pop(source_field)
                logger.debug(f"Moved {source_field} → relationships.{target_field}")
    
    def _create_exposure_limits_group(
        self,
        frontmatter: Dict[str, Any],
        relationships: Dict[str, Any]
    ) -> None:
        """
        Create relationships.exposure_limits group.
        
        Combines:
        - exposure_limits (existing dict)
        - monitoring_required (bool)
        - typical_concentration_range (string)
        """
        exposure_limits = {}
        
        # Move base exposure_limits dict
        if 'exposure_limits' in frontmatter:
            exposure_limits.update(frontmatter.pop('exposure_limits'))
        
        # Add monitoring_required
        if 'monitoring_required' in frontmatter:
            exposure_limits['monitoring_required'] = frontmatter.pop('monitoring_required')
        
        # Add typical_concentration_range
        if 'typical_concentration_range' in frontmatter:
            exposure_limits['typical_concentration_range'] = frontmatter.pop('typical_concentration_range')
        
        if exposure_limits:
            relationships['exposure_limits'] = exposure_limits
            logger.debug("Created relationships.exposure_limits group")
    
    def _create_health_hazards_group(
        self,
        frontmatter: Dict[str, Any],
        relationships: Dict[str, Any]
    ) -> None:
        """
        Create relationships.health_hazards group.
        
        Transforms health_effects_keywords array into structured group:
        - keywords: [array of keywords]
        - severity: (extracted from hazard_class if available)
        - target_organs: (could be enriched later)
        - carcinogenicity: (could be extracted from keywords)
        """
        if 'health_effects_keywords' in frontmatter:
            keywords = frontmatter.pop('health_effects_keywords')
            
            health_hazards = {
                'keywords': keywords
            }
            
            # Extract carcinogenicity if present in keywords
            if any('carcinogen' in kw.lower() for kw in keywords):
                health_hazards['carcinogenicity'] = 'Suspected or confirmed carcinogen'
            
            # Extract severity from hazard_class
            if frontmatter.get('hazard_class'):
                hazard_class = frontmatter['hazard_class']
                if hazard_class in ['toxic', 'corrosive']:
                    health_hazards['severity'] = 'high'
                elif hazard_class in ['irritant', 'oxidizer']:
                    health_hazards['severity'] = 'moderate'
                else:
                    health_hazards['severity'] = 'low'
            
            relationships['health_hazards'] = health_hazards
            logger.debug("Created relationships.health_hazards group")
    
    def _create_production_sources_group(
        self,
        frontmatter: Dict[str, Any],
        relationships: Dict[str, Any]
    ) -> None:
        """
        Create relationships.production_sources group.
        
        Transforms sources_in_laser_cleaning array from simple strings
        to structured objects with process + description.
        """
        if 'sources_in_laser_cleaning' in frontmatter:
            sources = frontmatter.pop('sources_in_laser_cleaning')
            
            # Convert simple array to structured objects
            laser_cleaning_processes = []
            for source in sources:
                # Generate description from process name
                description = self._generate_process_description(source)
                
                laser_cleaning_processes.append({
                    'process': source,
                    'description': description
                })
            
            relationships['production_sources'] = {
                'laser_cleaning_processes': laser_cleaning_processes
            }
            logger.debug("Created relationships.production_sources group")
    
    def _generate_process_description(self, process_name: str) -> str:
        """
        Generate human-readable description from process name.
        
        Args:
            process_name: Process identifier (e.g., 'alcohol_oxidation')
            
        Returns:
            Human-readable description
        """
        # Convert underscores to spaces and capitalize
        words = process_name.replace('_', ' ').split()
        words = [w.capitalize() for w in words]
        base_text = ' '.join(words)
        
        # Add context
        return f"{base_text} during laser ablation process"
    
    def _clear_reference_arrays(self, relationships: Dict[str, Any]) -> None:
        """
        Remove old reference array structure from relationships.
        
        Deletes entries like:
        - chemical_properties: [{type: ..., id: ..., notes: ...}]
        - health_effects: [{type: ..., id: ...}]
        
        These will be replaced by actual data objects.
        """
        # List of fields that should be objects, not arrays
        reference_fields = [
            'chemical_properties',
            'health_effects',
            'environmental_impact',
            'detection_monitoring',
            'ppe_requirements',
            'emergency_response'
        ]
        
        for field in reference_fields:
            if field in relationships and isinstance(relationships[field], list):
                # It's a reference array - delete it
                del relationships[field]
                logger.debug(f"Cleared reference array: relationships.{field}")
    
    def _add_cross_reference_placeholders(self, relationships: Dict[str, Any]) -> None:
        """
        Add placeholder structure for cross-references.
        
        These will be populated by dedicated linkage enrichers:
        - produced_by_contaminants (enriched by contaminant_linkage)
        - found_on_materials (enriched by material_linkage)
        """
        # Only add if not already present
        if 'produced_by_contaminants' not in relationships:
            relationships['produced_by_contaminants'] = {
                'title': 'Contaminant Sources',
                'description': 'Contaminants that produce this compound during laser cleaning',
                'items': []  # Will be populated by enricher
            }
        
        if 'found_on_materials' not in relationships:
            relationships['found_on_materials'] = {
                'title': 'Material Associations',
                'description': 'Materials where this compound is commonly detected during laser cleaning',
                'items': []  # Will be populated by enricher
            }
    
    def _rename_relationships(self, relationships: Dict[str, Any]) -> None:
        """
        Rename relationships to standardized names (Change 3 - Dec 19, 2025).
        
        Renames:
        - produced_by_contaminants → source_contaminants
        - found_on_materials → affected_materials
        """
        if 'produced_by_contaminants' in relationships:
            relationships['source_contaminants'] = relationships.pop('produced_by_contaminants')
            logger.debug("Renamed produced_by_contaminants → source_contaminants")
        
        if 'found_on_materials' in relationships:
            relationships['affected_materials'] = relationships.pop('found_on_materials')
            logger.debug("Renamed found_on_materials → affected_materials")
        
        logger.debug("Added cross-reference placeholder structures")
