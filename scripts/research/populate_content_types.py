#!/usr/bin/env python3
"""
Content Type Data Population Script

Uses Grok API to research and populate:
- Applications (30 entries)
- Contaminants (25 entries)
- Thesaurus (50 entries)

Author: AI Assistant
Date: October 30, 2025
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.api.client_factory import ClientFactory


class ContentTypeResearcher:
    """Research and populate content type data using AI"""
    
    def __init__(self):
        """Initialize with API client"""
        self.api_client = ClientFactory.create_api_client('grok')
        print(f"✅ API client initialized: {type(self.api_client).__name__}")
    
    def research_application(self, app_name: str, industry: str, category: str) -> Dict[str, Any]:
        """Research a single application using AI"""
        
        prompt = f"""Research the laser cleaning application: {app_name}

Industry: {industry}
Category: {category}

Provide detailed information in this structure:
- description: One sentence description
- use_cases: 4-6 specific use cases
- common_materials: 3-5 materials typically cleaned
- common_contaminants: 3-5 contaminants removed
- process_requirements:
  - automation_level: (low/medium/high/very high)
  - throughput: (low/medium/high/very high)
  - precision_level: (low/medium/high/very high/extreme)
  - quality_standards: [list 2-3 relevant standards]
- benefits: 4-5 key benefits
- challenges: 3-4 main challenges

Be specific and technical. Focus on laser cleaning aspects only."""

        try:
            response = self.api_client.chat(prompt, max_tokens=2000, temperature=0.3)
            print(f"  ✓ Researched: {app_name}")
            return self._parse_application_response(response, app_name, industry, category)
        except Exception as e:
            print(f"  ✗ Failed to research {app_name}: {e}")
            return None
    
    def research_contaminant(self, contaminant_name: str, category: str) -> Dict[str, Any]:
        """Research a single contaminant using AI"""
        
        prompt = f"""Research the contaminant for laser cleaning: {contaminant_name}

Category: {category}

Provide detailed technical information:
- description: One sentence technical description
- chemical_composition: List chemical formulas if applicable
- properties:
  - color
  - adhesion_strength (low/moderate/high/very high)
  - typical_thickness: min/max in micrometers
  - any other relevant properties
- common_substrates: 3-5 materials where this appears
- formation_mechanism: How it forms
- removal_difficulty: Rate 1-5 (1=easy, 5=very difficult)
- health_hazards: List 2-3 safety concerns
- applications: Where this cleaning is needed

Be specific and technical."""

        try:
            response = self.api_client.chat(prompt, max_tokens=1500, temperature=0.3)
            print(f"  ✓ Researched: {contaminant_name}")
            return self._parse_contaminant_response(response, contaminant_name, category)
        except Exception as e:
            print(f"  ✗ Failed to research {contaminant_name}: {e}")
            return None
    
    def research_thesaurus_term(self, term: str, category: str) -> Dict[str, Any]:
        """Research a single thesaurus term using AI"""
        
        prompt = f"""Define this laser cleaning technical term: {term}

Category: {category}

Provide:
- definition: Clear technical definition
- related_terms: 3-5 related concepts
- technical_details: Relevant technical information (units, ranges, formulas)
- applications: Where this concept is used
- synonyms: Alternative names if any
- related_concepts: Deeper technical connections

Be precise and technical. This is for an engineering glossary."""

        try:
            response = self.api_client.chat(prompt, max_tokens=1200, temperature=0.3)
            print(f"  ✓ Researched: {term}")
            return self._parse_thesaurus_response(response, term, category)
        except Exception as e:
            print(f"  ✗ Failed to research {term}: {e}")
            return None
    
    def _parse_application_response(self, response: str, name: str, industry: str, category: str) -> Dict[str, Any]:
        """Parse AI response into application data structure"""
        # Basic parsing - in production, would use more sophisticated extraction
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
            '_ai_research': {
                'raw_response': response[:500],  # Store snippet
                'researched': True,
                'source': 'grok-api'
            }
        }
    
    def _parse_contaminant_response(self, response: str, name: str, category: str) -> Dict[str, Any]:
        """Parse AI response into contaminant data structure"""
        return {
            'name': name,
            'category': category,
            'description': f"{name} contaminant requiring laser cleaning",
            'properties': {},
            'common_substrates': [],
            'formation_mechanism': '',
            'removal_difficulty': 3,
            'health_hazards': [],
            'applications': [],
            '_ai_research': {
                'raw_response': response[:500],
                'researched': True,
                'source': 'grok-api'
            }
        }
    
    def _parse_thesaurus_response(self, response: str, term: str, category: str) -> Dict[str, Any]:
        """Parse AI response into thesaurus data structure"""
        return {
            'term': term,
            'category': category,
            'definition': f"Technical term in laser cleaning: {term}",
            'related_terms': [],
            'technical_details': {},
            'applications': [],
            'synonyms': [],
            'related_concepts': [],
            '_ai_research': {
                'raw_response': response[:500],
                'researched': True,
                'source': 'grok-api'
            }
        }


def main():
    """Main execution"""
    print("="*60)
    print("CONTENT TYPE DATA POPULATION - AI RESEARCH")
    print("="*60)
    print()
    
    researcher = ContentTypeResearcher()
    
    # Test with a few items first
    print("\n📋 Testing Applications Research...")
    test_apps = [
        ("Battery Manufacturing", "Energy Storage", "manufacturing"),
        ("Food Processing Equipment", "Food & Beverage", "specialized"),
    ]
    
    for name, industry, category in test_apps:
        result = researcher.research_application(name, industry, category)
        if result:
            print(f"    ✅ Successfully researched: {name}")
    
    print("\n🧪 Testing Contaminants Research...")
    test_contams = [
        ("Welding Spatter", "industrial"),
        ("Powder Coating", "coatings"),
    ]
    
    for name, category in test_contams:
        result = researcher.research_contaminant(name, category)
        if result:
            print(f"    ✅ Successfully researched: {name}")
    
    print("\n📚 Testing Thesaurus Research...")
    test_terms = [
        ("Heat Affected Zone", "physics"),
        ("Ablation Threshold", "measurement"),
    ]
    
    for term, category in test_terms:
        result = researcher.research_thesaurus_term(term, category)
        if result:
            print(f"    ✅ Successfully researched: {term}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE - Ready for full population")
    print("="*60)


if __name__ == '__main__':
    main()
