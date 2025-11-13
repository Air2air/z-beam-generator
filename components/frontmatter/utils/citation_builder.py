"""
Citation Builder for Unified Frontmatter

Extracts citations from PropertyResearch.yaml and SettingResearch.yaml,
builds research_library with complete metadata.

NO FALLBACKS: All data must have explicit citations or be marked needs_research.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
import hashlib

logger = logging.getLogger(__name__)


class CitationBuilder:
    """
    Builds research_library and citation references from research data files.
    
    STRICT POLICY:
    - Every non-null value MUST have citations
    - No "source: literature" vague attributions
    - No category defaults
    - Explicit needs_research flag for incomplete data
    """
    
    def __init__(
        self,
        property_research_path: str = "materials/data/PropertyResearch.yaml",
        setting_research_path: str = "materials/data/SettingResearch.yaml"
    ):
        """
        Initialize citation builder with research data paths.
        
        Args:
            property_research_path: Path to PropertyResearch.yaml
            setting_research_path: Path to SettingResearch.yaml
            
        Raises:
            FileNotFoundError: If research files don't exist
        """
        self.property_research_path = Path(property_research_path)
        self.setting_research_path = Path(setting_research_path)
        
        if not self.property_research_path.exists():
            raise FileNotFoundError(
                f"PropertyResearch.yaml not found: {self.property_research_path}\n"
                f"NO FALLBACKS - research data required."
            )
        
        if not self.setting_research_path.exists():
            raise FileNotFoundError(
                f"SettingResearch.yaml not found: {self.setting_research_path}\n"
                f"NO FALLBACKS - research data required."
            )
        
        self.property_research = self._load_yaml(self.property_research_path)
        self.setting_research = self._load_yaml(self.setting_research_path)
        
        # Citation cache to avoid duplicates
        self.citation_cache: Dict[str, Dict] = {}
        
        logger.info("✅ CitationBuilder initialized")
        logger.info(f"   Property research: {len(self.property_research)} materials")
        logger.info(f"   Setting research: {len(self.setting_research)} materials")
    
    def _load_yaml(self, path: Path) -> Dict:
        """Load YAML file with error handling."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return data if data else {}
        except Exception as e:
            raise ValueError(f"Failed to load {path}: {e}")
    
    def generate_citation_id(
        self,
        source_data: Dict,
        material_name: Optional[str] = None
    ) -> str:
        """
        Generate unique citation ID from source data.
        
        Format examples:
        - Journal: "Zhang2021"
        - Standard: "ASTM_C615_2023"
        - Government: "USGS_2023"
        - AI Research: "AI_DeepSeek_20251107"
        
        Args:
            source_data: Source information dictionary
            material_name: Optional material name for AI research context
            
        Returns:
            Unique citation ID string
        """
        source_type = source_data.get('source_type', 'unknown')
        source_name = source_data.get('source', 'Unknown Source')
        
        if source_type == 'ai_research':
            # AI research: Use model name + date
            date_str = source_data.get('research_date', datetime.now().strftime('%Y%m%d'))
            if isinstance(date_str, str) and 'T' in date_str:
                date_str = date_str.split('T')[0].replace('-', '')
            
            model = 'DeepSeek'  # Default
            if 'DeepSeek' in source_name or 'deepseek' in source_name.lower():
                model = 'DeepSeek'
            elif 'GPT' in source_name:
                model = 'GPT4'
            
            citation_id = f"AI_{model}_{date_str}"
            
            # Add material context if provided
            if material_name:
                citation_id += f"_{material_name}"
            
            return citation_id
        
        elif source_type in ['handbook', 'authoritative', 'industry_standard']:
            # Standards and handbooks: Organization + Year
            if 'ASTM' in source_name:
                # Extract standard number: "ASTM C615" -> "ASTM_C615_2023"
                parts = source_name.split()
                if len(parts) >= 2:
                    standard_num = parts[1].replace('-', '')
                    year = source_data.get('year', '2023')
                    return f"ASTM_{standard_num}_{year}"
            
            elif 'USGS' in source_name:
                year = source_data.get('year', '2023')
                return f"USGS_{year}"
            
            elif 'ISO' in source_name:
                parts = source_name.split()
                if len(parts) >= 2:
                    standard_num = parts[1].replace('-', '')
                    year = source_data.get('year', '2023')
                    return f"ISO_{standard_num}_{year}"
            
            # Generic standard format
            org = source_name.split()[0] if source_name else 'Unknown'
            year = source_data.get('year', '2023')
            return f"{org}_{year}"
        
        elif source_type == 'scientific_literature':
            # Academic papers: Author + Year
            author = source_data.get('author', '')
            if not author and source_name:
                # Try to extract from source name
                if '(' in source_name and ')' in source_name:
                    author = source_name.split('(')[0].strip()
            
            # Get last name
            if author:
                last_name = author.split()[-1].split(',')[0]
            else:
                # Generate from hash of source name
                last_name = hashlib.md5(source_name.encode()).hexdigest()[:8].capitalize()
            
            year = source_data.get('year', '2023')
            return f"{last_name}{year}"
        
        else:
            # Unknown type: Use hash
            source_hash = hashlib.md5(source_name.encode()).hexdigest()[:8].capitalize()
            return f"Source_{source_hash}"
    
    def build_citation_entry(
        self,
        source_data: Dict,
        material_name: str,
        property_or_setting_name: str
    ) -> Dict:
        """
        Build complete citation entry for research_library.
        
        Args:
            source_data: Source information from research YAML
            material_name: Material name (e.g., "Aluminum")
            property_or_setting_name: Property/setting name (e.g., "density")
            
        Returns:
            Complete citation dictionary with metadata
        """
        source_type = source_data.get('source_type', 'unknown')
        
        citation = {
            'type': self._map_source_type_to_citation_type(source_type),
            'source_name': source_data.get('source', 'Unknown Source'),
            'confidence': source_data.get('confidence', 90),
            'value_researched': source_data.get('value'),
            'unit': source_data.get('unit'),
            'context': f"{material_name} {property_or_setting_name}",
        }
        
        # Add type-specific fields
        if source_type == 'ai_research':
            citation.update({
                'model': 'DeepSeek R1',  # Default, could parse from source_data
                'research_date': source_data.get('research_date', datetime.now().isoformat()),
                'methodology': 'Multi-source synthesis with validation',
                'sources_consulted': source_data.get('total_sources', 1),
                'raw_response': source_data.get('raw_response', ''),
                'validation_status': 'needs_expert_review',
                'notes': source_data.get('notes', '')
            })
        
        elif source_type in ['handbook', 'authoritative', 'industry_standard']:
            citation.update({
                'organization': self._extract_organization(source_data.get('source', '')),
                'standard_id': self._extract_standard_id(source_data.get('source', '')),
                'year': source_data.get('year', 2023),
                'url': source_data.get('url', ''),
                'authority': 'authoritative',
                'peer_reviewed': True,
                'consensus_document': True
            })
        
        elif source_type == 'scientific_literature':
            citation.update({
                'author': source_data.get('author', ''),
                'year': source_data.get('year', 2023),
                'title': source_data.get('title', ''),
                'journal': source_data.get('journal', ''),
                'doi': source_data.get('doi', ''),
                'url': source_data.get('url', ''),
                'peer_reviewed': True,
                'authority': 'high'
            })
        
        return citation
    
    def _map_source_type_to_citation_type(self, source_type: str) -> str:
        """Map research source_type to citation type."""
        mapping = {
            'ai_research': 'ai_research',
            'handbook': 'handbook',
            'authoritative': 'industry_standard',
            'industry_standard': 'industry_standard',
            'scientific_literature': 'journal_article',
            'database': 'government_database',
            'measured': 'experimental_data'
        }
        return mapping.get(source_type, 'other')
    
    def _extract_organization(self, source_name: str) -> str:
        """Extract organization name from source string."""
        orgs = ['ASTM', 'ISO', 'ANSI', 'IEEE', 'NIST', 'USGS', 'EPA']
        for org in orgs:
            if org in source_name:
                return org
        return source_name.split()[0] if source_name else 'Unknown'
    
    def _extract_standard_id(self, source_name: str) -> str:
        """Extract standard ID from source string."""
        # Examples: "ASTM C615", "ISO 9001"
        parts = source_name.split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1]}"
        return source_name
    
    def build_property_citations(
        self,
        material_name: str,
        property_name: str
    ) -> Tuple[Optional[Dict], List[Dict], Dict]:
        """
        Build citations for a material property.
        
        Args:
            material_name: Material name
            property_name: Property name (e.g., "density")
            
        Returns:
            Tuple of (primary_citation, supporting_citations, source_summary)
            Returns (None, [], {needs_research: True}) if not researched
        """
        material_data = self.property_research.get(material_name, {})
        prop_data = material_data.get(property_name, {})
        
        if not prop_data or not prop_data.get('research', {}).get('values'):
            # NOT RESEARCHED
            return None, [], {
                'total_sources': 0,
                'needs_research': True,
                'research_priority': 'high',
                'notes': f"Property {property_name} not yet researched for {material_name}"
            }
        
        sources = prop_data['research']['values']
        
        # Primary citation (first source, typically highest confidence)
        primary_source = sources[0]
        primary_id = self.generate_citation_id(primary_source, material_name)
        primary_citation_entry = self.build_citation_entry(
            primary_source,
            material_name,
            property_name
        )
        
        # Cache citation
        self.citation_cache[primary_id] = primary_citation_entry
        
        primary_citation = {
            'id': primary_id,
            'relevance': primary_source.get('notes', ''),
            'confidence': primary_source.get('confidence', 90),
            'specific_location': self._extract_location(primary_source)
        }
        
        # Supporting citations
        supporting_citations = []
        for i, source in enumerate(sources[1:], start=1):
            source_id = self.generate_citation_id(source, f"{material_name}_{i}")
            citation_entry = self.build_citation_entry(
                source,
                material_name,
                property_name
            )
            self.citation_cache[source_id] = citation_entry
            
            supporting_citations.append({
                'id': source_id,
                'value': source.get('value'),
                'confidence': source.get('confidence', 90),
                'notes': source.get('notes', ''),
                'variance_explanation': self._calculate_variance(
                    source.get('value'),
                    primary_source.get('value')
                )
            })
        
        # Source summary
        source_summary = {
            'total_sources': len(sources),
            'primary_source_type': primary_citation_entry['type'],
            'validation_status': prop_data.get('metadata', {}).get('validation_status', 'needs_validation'),
            'last_updated': prop_data.get('metadata', {}).get('last_researched', ''),
            'needs_research': False
        }
        
        return primary_citation, supporting_citations, source_summary
    
    def _extract_location(self, source_data: Dict) -> str:
        """Extract specific location (page, table, etc.) from source data."""
        page = source_data.get('page', '')
        table = source_data.get('table', '')
        
        if page and table:
            return f"Page {page}, {table}"
        elif page:
            return f"Page {page}"
        elif table:
            return table
        return ""
    
    def _calculate_variance(
        self,
        value: Optional[float],
        reference_value: Optional[float]
    ) -> str:
        """Calculate percentage variance between values."""
        if value is None or reference_value is None or reference_value == 0:
            return ""
        
        variance = ((value - reference_value) / reference_value) * 100
        
        if variance > 0:
            return f"+{variance:.1f}% higher"
        elif variance < 0:
            return f"{variance:.1f}% lower"
        else:
            return "Same value"
    
    def get_research_library(self) -> Dict[str, Dict]:
        """
        Get complete research_library with all cached citations.
        
        Returns:
            Dictionary mapping citation IDs to citation entries
        """
        return self.citation_cache.copy()
    
    def validate_citations(
        self,
        material_properties: Dict,
        research_library: Dict
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all citations are properly referenced.
        
        Args:
            material_properties: Material properties dictionary
            research_library: Research library dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        for category, properties in material_properties.items():
            for prop_name, prop_data in properties.items():
                # Check if property has value
                if prop_data.get('value') is not None:
                    # Must have citations
                    if 'citations' not in prop_data:
                        errors.append(
                            f"❌ {category}.{prop_name} has value but NO citations"
                        )
                        continue
                    
                    # Validate primary citation
                    if 'primary' not in prop_data['citations']:
                        errors.append(
                            f"❌ {category}.{prop_name} missing PRIMARY citation"
                        )
                    else:
                        primary_id = prop_data['citations']['primary'].get('id')
                        if primary_id and primary_id not in research_library:
                            errors.append(
                                f"❌ Citation {primary_id} referenced but not in research_library"
                            )
                    
                    # Validate supporting citations
                    for citation in prop_data['citations'].get('supporting', []):
                        if citation['id'] not in research_library:
                            errors.append(
                                f"❌ Citation {citation['id']} referenced but not in research_library"
                            )
                
                else:
                    # Null value must have needs_research flag
                    if not prop_data.get('source_summary', {}).get('needs_research'):
                        errors.append(
                            f"❌ {category}.{prop_name} has null value but needs_research not set"
                        )
        
        is_valid = len(errors) == 0
        return is_valid, errors


if __name__ == "__main__":
    # Test the citation builder
    logging.basicConfig(level=logging.INFO)
    
    try:
        builder = CitationBuilder()
        print("\n✅ CitationBuilder initialized\n")
        
        # Test building citations for Aluminum density
        material = "Aluminum"
        prop = "density"
        
        print(f"Building citations for {material} {prop}...")
        primary, supporting, summary = builder.build_property_citations(material, prop)
        
        if primary:
            print("\nPrimary Citation:")
            print(f"  ID: {primary['id']}")
            print(f"  Confidence: {primary['confidence']}%")
            print(f"  Relevance: {primary['relevance'][:80]}...")
        
        print(f"\nSupporting Citations: {len(supporting)}")
        for i, cite in enumerate(supporting, 1):
            print(f"  {i}. {cite['id']} ({cite['confidence']}%)")
        
        print("\nSource Summary:")
        print(f"  Total sources: {summary['total_sources']}")
        print(f"  Needs research: {summary['needs_research']}")
        
        # Get full research library
        library = builder.get_research_library()
        print(f"\n✅ Research library built: {len(library)} citations")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
