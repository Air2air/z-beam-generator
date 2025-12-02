"""
Content Researcher

Reusable AI research functionality for all content types.
Supports materials, contaminants, and settings.

Author: AI Assistant
Date: October 30, 2025
"""

from typing import Dict, Any, Optional
from shared.api.client_factory import APIClientFactory


class ContentResearcher:
    """
    AI-powered content researcher for all content types.
    
    Usage:
        researcher = ContentResearcher.create()
        data = researcher.research_application("Battery Manufacturing", {...})
        data = researcher.research_contaminant("Welding Spatter", {...})
        data = researcher.research_thesaurus_term("Ablation Threshold", {...})
    """
    
    def __init__(self, api_client=None):
        """
        Initialize researcher with API client.
        
        Args:
            api_client: Optional API client. If None, creates Grok client.
        """
        self.api_client = api_client or APIClientFactory.create_client('grok')
    
    @classmethod
    def create(cls, provider: str = 'grok'):
        """
        Factory method to create researcher.
        
        Args:
            provider: API provider (default: grok)
        
        Returns:
            ContentResearcher instance
        """
        client = APIClientFactory.create_client(provider)
        return cls(client)
    
    def research_application(
        self,
        name: str,
        industry: str,
        category: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Research laser cleaning application using AI.
        
        Args:
            name: Application name (e.g., "Battery Manufacturing")
            industry: Industry sector (e.g., "Energy Storage")
            category: Category (manufacturing, maintenance, etc.)
            context: Additional context for research
        
        Returns:
            Dictionary with researched application data
        """
        context = context or {}
        
        prompt = f"""Research the laser cleaning application: {name}

Industry: {industry}
Category: {category}

Provide detailed, technical information for a laser cleaning database:

DESCRIPTION:
- One concise sentence describing this application

USE CASES:
- List 5-6 specific, practical use cases
- Be concrete (e.g., "Weld seam cleaning before painting")

COMMON MATERIALS:
- List 4-6 materials typically cleaned in this application
- Use proper material names (e.g., "Stainless Steel 316L", "Aluminum 6061")

COMMON CONTAMINANTS:
- List 4-6 contaminants removed in this application
- Be specific (e.g., "oxide layers", "flux residue", "rust")

PROCESS REQUIREMENTS:
automation_level: Choose one: low, medium, high, very high, extreme
throughput: Choose one: low, medium, high, very high
precision_level: Choose one: low, medium, high, very high, extreme
quality_standards: List 2-4 relevant industry standards (ISO, FDA, ASME, etc.)

BENEFITS:
- List 5-6 key advantages of laser cleaning for this application
- Be specific and measurable when possible

CHALLENGES:
- List 3-5 main technical or operational challenges
- Be honest about limitations

Format as clear sections. Be technical and specific."""

        try:
            api_response = self.api_client.generate_simple(prompt, max_tokens=2500, temperature=0.3)
            response_text = api_response.content if hasattr(api_response, 'content') else str(api_response)
            return self._parse_application_response(response_text, name, industry, category)
        except Exception as e:
            print(f"❌ Research failed for {name}: {e}")
            return self._create_placeholder_application(name, industry, category)
    
    def research_contaminant(
        self,
        name: str,
        category: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Research contaminant type using AI.
        
        Args:
            name: Contaminant name (e.g., "Welding Spatter")
            category: Category (corrosion, coatings, biological, etc.)
            context: Additional context
        
        Returns:
            Dictionary with researched contaminant data
        """
        context = context or {}
        
        prompt = f"""Research this contaminant for laser cleaning: {name}

Category: {category}

Provide detailed technical information:

DESCRIPTION:
- One sentence technical description

CHEMICAL COMPOSITION:
- List chemical formulas if applicable (e.g., Fe2O3, CuO)
- If organic/mixed, describe composition

PROPERTIES:
color: Typical visual appearance
adhesion_strength: Choose: low, moderate, high, very high
typical_thickness: Provide min and max in micrometers
other_properties: Any other relevant physical properties

COMMON SUBSTRATES:
- List 4-6 materials where this contaminant typically appears
- Use proper material names

FORMATION MECHANISM:
- Brief explanation of how this forms

REMOVAL DIFFICULTY:
- Rate 1-5 (1=very easy, 5=extremely difficult)
- Justify the rating

HEALTH HAZARDS:
- List 2-4 safety concerns during removal
- Be specific about exposure risks

APPLICATIONS:
- List 3-5 industries/applications where this cleaning is needed

Be technical and specific. This is for laser cleaning professionals."""

        try:
            api_response = self.api_client.generate_simple(prompt, max_tokens=2000, temperature=0.3)
            response_text = api_response.content if hasattr(api_response, 'content') else str(api_response)
            return self._parse_contaminant_response(response_text, name, category)
        except Exception as e:
            print(f"❌ Research failed for {name}: {e}")
            return self._create_placeholder_contaminant(name, category)
    
    def research_thesaurus_term(
        self,
        term: str,
        category: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Research technical term for glossary.
        
        Args:
            term: Technical term (e.g., "Ablation Threshold")
            category: Category (process, physics, equipment, etc.)
            context: Additional context
        
        Returns:
            Dictionary with researched term data
        """
        context = context or {}
        
        prompt = f"""Define this laser cleaning technical term: {term}

Category: {category}

Provide comprehensive technical information for an engineering glossary:

DEFINITION:
- Clear, precise technical definition (2-3 sentences)
- Include key concepts and context

RELATED TERMS:
- List 4-6 directly related technical terms
- Terms that users should also understand

TECHNICAL DETAILS:
- Units of measurement if applicable
- Typical value ranges
- Formulas or equations if relevant
- Physical principles involved

APPLICATIONS:
- Where this concept/parameter is used in practice
- Why it matters for laser cleaning

SYNONYMS:
- Alternative names or terminology
- Industry-specific variations

RELATED CONCEPTS:
- Deeper technical connections
- Broader or narrower concepts

Be precise, technical, and comprehensive. This is for engineers and technicians."""

        try:
            api_response = self.api_client.generate_simple(prompt, max_tokens=1500, temperature=0.3)
            response_text = api_response.content if hasattr(api_response, 'content') else str(api_response)
            return self._parse_thesaurus_response(response_text, term, category)
        except Exception as e:
            print(f"❌ Research failed for {term}: {e}")
            return self._create_placeholder_thesaurus(term, category)
    
    def _parse_application_response(
        self,
        response: str,
        name: str,
        industry: str,
        category: str
    ) -> Dict[str, Any]:
        """Parse AI response into application data structure."""
        # Extract structured data from response
        lines = response.strip().split('\n')
        
        data = {
            'name': name,
            'category': category,
            'description': '',
            'industry': industry,
            'use_cases': [],
            'common_materials': [],
            'common_contaminants': [],
            'process_requirements': {
                'automation_level': 'medium',
                'throughput': 'medium',
                'precision_level': 'medium',
                'quality_standards': []
            },
            'benefits': [],
            'challenges': [],
            '_metadata': {
                'ai_researched': True,
                'research_source': 'grok-api',
                'response_length': len(response)
            }
        }
        
        # Simple extraction - will be enhanced with better parsing
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections (handle both "SECTION:" and "### SECTION" formats)
            upper_line = line.upper().replace('#', '').strip()
            
            # Check if this is a section header
            is_section_header = False
            if 'DESCRIPTION' in upper_line and len(upper_line.split()) <= 2:
                current_section = 'description'
                is_section_header = True
            elif ('USE CASES' in upper_line or 'USE_CASES' in upper_line) and len(upper_line.split()) <= 3:
                current_section = 'use_cases'
                is_section_header = True
            elif ('COMMON MATERIALS' in upper_line or (('MATERIALS' in upper_line) and len(upper_line.split()) <= 2)) and len(upper_line.split()) <= 3:
                current_section = 'materials'
                is_section_header = True
            elif ('COMMON CONTAMINANTS' in upper_line or (('CONTAMINANTS' in upper_line) and len(upper_line.split()) <= 2)) and len(upper_line.split()) <= 3:
                current_section = 'contaminants'
                is_section_header = True
            elif ('BENEFITS' in upper_line or 'ADVANTAGES' in upper_line) and len(upper_line.split()) <= 2:
                current_section = 'benefits'
                is_section_header = True
            elif ('CHALLENGES' in upper_line or 'LIMITATIONS' in upper_line) and len(upper_line.split()) <= 2:
                current_section = 'challenges'
                is_section_header = True
            
            # Skip section headers, extract content from subsequent lines
            if is_section_header:
                continue
            
            # Extract content
            if current_section == 'description' and not data['description']:
                desc_text = line.lstrip('- ').strip()
                if desc_text:  # Only set non-empty descriptions
                    data['description'] = desc_text
            elif current_section == 'use_cases' and line.startswith('-'):
                data['use_cases'].append(line.lstrip('- ').strip())
            elif current_section == 'materials' and line.startswith('-'):
                data['common_materials'].append(line.lstrip('- ').strip())
            elif current_section == 'contaminants' and line.startswith('-'):
                data['common_contaminants'].append(line.lstrip('- ').strip())
            elif current_section == 'benefits' and line.startswith('-'):
                data['benefits'].append(line.lstrip('- ').strip())
            elif current_section == 'challenges' and line.startswith('-'):
                data['challenges'].append(line.lstrip('- ').strip())
        
        return data
    
    def _parse_contaminant_response(
        self,
        response: str,
        name: str,
        category: str
    ) -> Dict[str, Any]:
        """Parse AI response into contaminant data structure."""
        lines = response.strip().split('\n')
        
        data = {
            'name': name,
            'category': category,
            'description': '',
            'chemical_composition': [],
            'properties': {},
            'common_substrates': [],
            'formation_mechanism': '',
            'removal_difficulty': 3,
            'health_hazards': [],
            'applications': [],
            '_metadata': {
                'ai_researched': True,
                'research_source': 'grok-api',
                'response_length': len(response)
            }
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            upper_line = line.upper()
            if 'DESCRIPTION:' in upper_line:
                current_section = 'description'
            elif 'CHEMICAL COMPOSITION:' in upper_line:
                current_section = 'chemical'
            elif 'COMMON SUBSTRATES:' in upper_line or 'SUBSTRATES:' in upper_line:
                current_section = 'substrates'
            elif 'HEALTH HAZARDS:' in upper_line or 'HAZARDS:' in upper_line:
                current_section = 'hazards'
            elif 'APPLICATIONS:' in upper_line:
                current_section = 'applications'
            elif current_section == 'description' and not data['description']:
                data['description'] = line.lstrip('- ').strip()
            elif current_section == 'chemical' and line.startswith('-'):
                data['chemical_composition'].append(line.lstrip('- ').strip())
            elif current_section == 'substrates' and line.startswith('-'):
                data['common_substrates'].append(line.lstrip('- ').strip())
            elif current_section == 'hazards' and line.startswith('-'):
                data['health_hazards'].append(line.lstrip('- ').strip())
            elif current_section == 'applications' and line.startswith('-'):
                data['applications'].append(line.lstrip('- ').strip())
        
        return data
    
    def _parse_thesaurus_response(
        self,
        response: str,
        term: str,
        category: str
    ) -> Dict[str, Any]:
        """Parse AI response into thesaurus data structure."""
        lines = response.strip().split('\n')
        
        data = {
            'term': term,
            'category': category,
            'definition': '',
            'related_terms': [],
            'technical_details': {},
            'applications': [],
            'synonyms': [],
            'related_concepts': [],
            '_metadata': {
                'ai_researched': True,
                'research_source': 'grok-api',
                'response_length': len(response)
            }
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            upper_line = line.upper()
            if 'DEFINITION:' in upper_line:
                current_section = 'definition'
            elif 'RELATED TERMS:' in upper_line:
                current_section = 'related_terms'
            elif 'APPLICATIONS:' in upper_line:
                current_section = 'applications'
            elif 'SYNONYMS:' in upper_line:
                current_section = 'synonyms'
            elif 'RELATED CONCEPTS:' in upper_line:
                current_section = 'related_concepts'
            elif current_section == 'definition' and not data['definition']:
                data['definition'] = line.lstrip('- ').strip()
            elif current_section == 'related_terms' and line.startswith('-'):
                data['related_terms'].append(line.lstrip('- ').strip())
            elif current_section == 'applications' and line.startswith('-'):
                data['applications'].append(line.lstrip('- ').strip())
            elif current_section == 'synonyms' and line.startswith('-'):
                data['synonyms'].append(line.lstrip('- ').strip())
            elif current_section == 'related_concepts' and line.startswith('-'):
                data['related_concepts'].append(line.lstrip('- ').strip())
        
        return data
    
    def _create_placeholder_application(
        self,
        name: str,
        industry: str,
        category: str
    ) -> Dict[str, Any]:
        """Create placeholder when research fails."""
        return {
            'name': name,
            'category': category,
            'description': f"Laser cleaning application in {industry}",
            'industry': industry,
            'use_cases': [],
            'common_materials': [],
            'common_contaminants': [],
            'process_requirements': {
                'automation_level': 'medium',
                'throughput': 'medium',
                'precision_level': 'medium',
                'quality_standards': []
            },
            'benefits': [],
            'challenges': [],
            '_metadata': {
                'ai_researched': False,
                'placeholder': True
            }
        }
    
    def _create_placeholder_contaminant(
        self,
        name: str,
        category: str
    ) -> Dict[str, Any]:
        """Create placeholder when research fails."""
        return {
            'name': name,
            'category': category,
            'description': f"{name} contaminant for laser cleaning",
            'chemical_composition': [],
            'properties': {},
            'common_substrates': [],
            'formation_mechanism': '',
            'removal_difficulty': 3,
            'health_hazards': [],
            'applications': [],
            '_metadata': {
                'ai_researched': False,
                'placeholder': True
            }
        }
    
    def _create_placeholder_thesaurus(
        self,
        term: str,
        category: str
    ) -> Dict[str, Any]:
        """Create placeholder when research fails."""
        return {
            'term': term,
            'category': category,
            'definition': f"Technical term in laser cleaning: {term}",
            'related_terms': [],
            'technical_details': {},
            'applications': [],
            'synonyms': [],
            'related_concepts': [],
            '_metadata': {
                'ai_researched': False,
                'placeholder': True
            }
        }
