#!/usr/bin/env python3
"""
Stage 3: Research & Enrichment
Leverages AI research agents and authoritative sources to validate and enrich property data.
"""

import os
import yaml
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib

# Import API clients
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.client_factory import ClientFactory
from api.config import APIConfig

class PropertyResearcher:
    """
    Uses AI research agents and authoritative databases to validate
    and enrich material property data with high-quality sources.
    """
    
    def __init__(self):
        self.frontmatter_dir = Path("content/components/frontmatter")
        self.config_file = Path("config/pipeline_config.yaml")
        
        # Load research configuration
        self.research_config = self._load_research_config()
        
        # Initialize API clients
        self.api_clients = {}
        self._initialize_api_clients()
        
        # Research cache
        self.research_cache = {}
        self.cache_file = Path("pipeline_results/research_cache.json")
        self._load_research_cache()
        
        # Statistics tracking
        self.research_stats = {
            'properties_researched': 0,
            'sources_consulted': 0,
            'enrichments_made': 0,
            'cache_hits': 0,
            'errors': []
        }
    
    def _load_research_config(self) -> Dict[str, Any]:
        """Load research configuration from pipeline config"""
        
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            return config.get('research', {
                'providers': ['deepseek', 'claude'],
                'authoritative_sources': {
                    'nist': 'https://webbook.nist.gov/chemistry/',
                    'matweb': 'http://www.matweb.com/',
                    'asm': 'https://www.asminternational.org/'
                },
                'quality_thresholds': {
                    'min_sources': 2,
                    'min_confidence': 0.8,
                    'max_variance': 0.15
                },
                'research_prompts': {
                    'property_validation': "Validate this material property value and provide authoritative sources",
                    'range_research': "Research typical ranges for this property in similar materials",
                    'source_verification': "Verify these property values with authoritative engineering sources"
                }
            })
            
        except Exception as e:
            print(f"⚠️  Could not load research config: {e}")
            return self._get_default_research_config()
    
    def _get_default_research_config(self) -> Dict[str, Any]:
        """Default research configuration"""
        
        return {
            'providers': ['deepseek'],
            'authoritative_sources': {
                'nist': 'NIST Chemistry WebBook',
                'matweb': 'MatWeb Material Database',
                'asm': 'ASM International Handbooks'
            },
            'quality_thresholds': {
                'min_sources': 2,
                'min_confidence': 0.8,
                'max_variance': 0.15
            },
            'research_timeout': 30,
            'cache_duration': 86400  # 24 hours
        }
    
    def _initialize_api_clients(self):
        """Initialize AI research API clients"""
        
        try:
            config = APIConfig()
            factory = ClientFactory(config)
            
            for provider in self.research_config.get('providers', ['deepseek']):
                try:
                    client = factory.create_client(provider)
                    self.api_clients[provider] = client
                    print(f"✅ Initialized {provider} research client")
                except Exception as e:
                    print(f"⚠️  Could not initialize {provider} client: {e}")
            
            if not self.api_clients:
                print("❌ No AI research clients available - research will be limited")
                
        except Exception as e:
            print(f"❌ Error initializing API clients: {e}")
    
    def _load_research_cache(self):
        """Load research cache from disk"""
        
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    self.research_cache = json.load(f)
                print(f"📚 Loaded research cache with {len(self.research_cache)} entries")
        except Exception as e:
            print(f"⚠️  Could not load research cache: {e}")
            self.research_cache = {}
    
    def _save_research_cache(self):
        """Save research cache to disk"""
        
        try:
            self.cache_file.parent.mkdir(exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.research_cache, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️  Could not save research cache: {e}")
    
    async def research_properties(self, materials_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Research and validate material properties using AI and authoritative sources.
        
        Args:
            materials_filter: Optional list of specific materials to process
            
        Returns:
            Research results with enrichments and validations
        """
        
        print("🔬 Starting property research and enrichment process...")
        
        research_results = []
        enrichments_made = []
        
        for yaml_file in self.frontmatter_dir.glob("*.yaml"):
            material_name = yaml_file.stem.replace("-laser-cleaning", "")
            
            # Apply materials filter if provided
            if materials_filter and material_name not in materials_filter:
                continue
            
            try:
                # Load material data
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Research material properties
                if 'materialProperties' in data:
                    material_enrichments = await self._research_material_properties(
                        material_name,
                        data.get('category', 'unknown'),
                        data['materialProperties']
                    )
                    
                    # Apply enrichments
                    if material_enrichments:
                        data = self._apply_enrichments(data, material_enrichments)
                        enrichments_made.extend(material_enrichments)
                        
                        # Save enriched data
                        self._save_enriched_material(yaml_file, data)
                
                # Create result record
                result = {
                    'material': material_name,
                    'category': data.get('category', 'unknown'),
                    'properties_researched': len(data.get('materialProperties', {})),
                    'enrichments_applied': len([e for e in material_enrichments if e['material'] == material_name]),
                    'research_confidence': self._calculate_research_confidence(material_enrichments),
                    'status': 'success'
                }
                
                research_results.append(result)
                
            except Exception as e:
                error_msg = f"Error researching {material_name}: {e}"
                self.research_stats['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                
                research_results.append({
                    'material': material_name,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Save research cache
        self._save_research_cache()
        
        print(f"✅ Research complete: {len(research_results)} materials researched")
        print(f"🔬 {len(enrichments_made)} enrichments made")
        
        return {
            'results': research_results,
            'enrichments': enrichments_made,
            'statistics': self.research_stats,
            'summary': self._generate_research_summary(research_results, enrichments_made)
        }
    
    async def _research_material_properties(self, material_name: str, category: str, properties: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Research all properties for a single material"""
        
        enrichments = []
        
        # Research high-priority properties first
        priority_properties = ['density', 'meltingPoint', 'thermalConductivity', 'hardness']
        all_properties = list(properties.keys())
        
        # Sort properties by priority
        sorted_properties = []
        for prop in priority_properties:
            if prop in all_properties:
                sorted_properties.append(prop)
        for prop in all_properties:
            if prop not in sorted_properties:
                sorted_properties.append(prop)
        
        # Research each property
        for prop_name in sorted_properties:
            try:
                prop_data = properties[prop_name]
                
                # Research property
                research_result = await self._research_single_property(
                    material_name, category, prop_name, prop_data
                )
                
                if research_result:
                    enrichments.append(research_result)
                    self.research_stats['properties_researched'] += 1
                
            except Exception as e:
                error_msg = f"Error researching {prop_name} for {material_name}: {e}"
                self.research_stats['errors'].append(error_msg)
                print(f"⚠️  {error_msg}")
        
        return enrichments
    
    async def _research_single_property(self, material_name: str, category: str, prop_name: str, prop_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Research a single property using AI and authoritative sources"""
        
        # Create cache key
        cache_key = self._create_cache_key(material_name, prop_name, prop_data)
        
        # Check cache first
        if cache_key in self.research_cache:
            cached_result = self.research_cache[cache_key]
            if self._is_cache_valid(cached_result):
                self.research_stats['cache_hits'] += 1
                return cached_result.get('enrichment')
        
        # Conduct research
        research_data = await self._conduct_property_research(material_name, category, prop_name, prop_data)
        
        if not research_data:
            return None
        
        # Create enrichment record
        enrichment = {
            'material': material_name,
            'property': prop_name,
            'research_timestamp': datetime.now().isoformat(),
            'original_data': prop_data,
            'research_findings': research_data,
            'enrichment_type': self._determine_enrichment_type(prop_data, research_data),
            'confidence_improvement': research_data.get('confidence', 0) - prop_data.get('confidence', 0),
            'sources_consulted': research_data.get('sources', []),
            'validation_status': research_data.get('validation_status', 'unknown')
        }
        
        # Cache the result
        self.research_cache[cache_key] = {
            'timestamp': datetime.now().isoformat(),
            'enrichment': enrichment
        }
        
        return enrichment
    
    async def _conduct_property_research(self, material_name: str, category: str, prop_name: str, prop_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Conduct actual research using AI clients and sources"""
        
        research_findings = {
            'sources': [],
            'validations': [],
            'suggested_ranges': [],
            'confidence': prop_data.get('confidence', 0.5)
        }
        
        # Research with AI clients
        for provider_name, client in self.api_clients.items():
            try:
                ai_research = await self._research_with_ai_client(
                    client, provider_name, material_name, category, prop_name, prop_data
                )
                
                if ai_research:
                    research_findings['sources'].append({
                        'type': 'ai_research',
                        'provider': provider_name,
                        'findings': ai_research
                    })
                    self.research_stats['sources_consulted'] += 1
                
            except Exception as e:
                print(f"⚠️  Error researching with {provider_name}: {e}")
        
        # Validate findings
        validation_result = self._validate_research_findings(prop_data, research_findings)
        research_findings.update(validation_result)
        
        return research_findings if research_findings['sources'] else None
    
    async def _research_with_ai_client(self, client, provider_name: str, material_name: str, category: str, prop_name: str, prop_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Research property using specific AI client"""
        
        # Construct research prompt
        research_prompt = f"""
        Material: {material_name} ({category})
        Property: {prop_name}
        Current Value: {prop_data.get('value')} {prop_data.get('unit', '')}
        Current Range: {prop_data.get('min', 'unknown')} - {prop_data.get('max', 'unknown')}
        
        Please research and validate this material property value. Provide:
        1. Verification of the current value against authoritative engineering sources
        2. Typical ranges for this property in {category} materials
        3. Confidence assessment of the current data
        4. Any recommended corrections or improvements
        5. Specific sources or references consulted
        
        Focus on engineering handbooks, NIST data, and peer-reviewed sources.
        """
        
        try:
            # Make API call
            response = await client.generate_async(research_prompt, max_tokens=1000)
            
            if not response or not response.get('content'):
                return None
            
            # Parse AI response
            ai_findings = self._parse_ai_research_response(response['content'])
            
            return {
                'response': response['content'],
                'parsed_findings': ai_findings,
                'provider': provider_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️  AI research error with {provider_name}: {e}")
            return None
    
    def _parse_ai_research_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI research response for actionable data"""
        
        findings = {
            'validation_status': 'unknown',
            'suggested_value': None,
            'suggested_range': {},
            'confidence_score': None,
            'sources_mentioned': [],
            'recommendations': []
        }
        
        # Look for validation indicators
        if any(phrase in response_text.lower() for phrase in ['correct', 'accurate', 'valid', 'confirmed']):
            findings['validation_status'] = 'validated'
        elif any(phrase in response_text.lower() for phrase in ['incorrect', 'inaccurate', 'wrong', 'error']):
            findings['validation_status'] = 'disputed'
        
        # Extract numeric values
        import re
        numbers = re.findall(r'[-+]?(?:\d*\.\d+|\d+)', response_text)
        if numbers:
            try:
                # Try to identify suggested values (this is a simple heuristic)
                findings['suggested_value'] = float(numbers[0])
                if len(numbers) >= 2:
                    findings['suggested_range'] = {
                        'min': float(numbers[0]),
                        'max': float(numbers[1])
                    }
            except ValueError:
                pass
        
        # Look for confidence indicators
        confidence_patterns = [
            r'confidence[:\s]+(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*%?\s*confidence',
            r'certainty[:\s]+(\d+(?:\.\d+)?)'
        ]
        
        for pattern in confidence_patterns:
            match = re.search(pattern, response_text.lower())
            if match:
                try:
                    confidence = float(match.group(1))
                    if confidence > 1:  # Assume percentage
                        confidence /= 100
                    findings['confidence_score'] = min(confidence, 1.0)
                    break
                except ValueError:
                    continue
        
        # Extract source mentions
        source_keywords = ['nist', 'asm', 'matweb', 'handbook', 'astm', 'iso', 'reference']
        for keyword in source_keywords:
            if keyword.lower() in response_text.lower():
                findings['sources_mentioned'].append(keyword)
        
        return findings
    
    def _validate_research_findings(self, original_data: Dict[str, Any], research_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate research findings and determine confidence"""
        
        validation = {
            'validation_status': 'unknown',
            'consensus_confidence': 0.5,
            'recommended_action': 'no_change'
        }
        
        # Check for consensus among sources
        validations = []
        for source in research_findings.get('sources', []):
            if 'findings' in source and 'parsed_findings' in source['findings']:
                parsed = source['findings']['parsed_findings']
                if parsed.get('validation_status') == 'validated':
                    validations.append(True)
                elif parsed.get('validation_status') == 'disputed':
                    validations.append(False)
        
        if validations:
            validation_rate = sum(validations) / len(validations)
            if validation_rate >= 0.8:
                validation['validation_status'] = 'validated'
                validation['consensus_confidence'] = 0.9
            elif validation_rate <= 0.2:
                validation['validation_status'] = 'disputed'
                validation['consensus_confidence'] = 0.3
                validation['recommended_action'] = 'needs_review'
            else:
                validation['validation_status'] = 'mixed'
                validation['consensus_confidence'] = 0.6
        
        # Check if multiple sources suggest similar values
        suggested_values = []
        for source in research_findings.get('sources', []):
            if 'findings' in source and 'parsed_findings' in source['findings']:
                suggested_val = source['findings']['parsed_findings'].get('suggested_value')
                if suggested_val is not None:
                    suggested_values.append(suggested_val)
        
        if len(suggested_values) >= 2:
            # Calculate variance
            mean_val = sum(suggested_values) / len(suggested_values)
            variance = sum((x - mean_val) ** 2 for x in suggested_values) / len(suggested_values)
            cv = (variance ** 0.5) / mean_val if mean_val != 0 else float('inf')
            
            if cv < 0.1:  # Low variance suggests good consensus
                validation['consensus_confidence'] += 0.2
                if abs(mean_val - original_data.get('value', 0)) / max(mean_val, original_data.get('value', 1)) > 0.2:
                    validation['recommended_action'] = 'update_value'
        
        return validation
    
    def _determine_enrichment_type(self, original_data: Dict[str, Any], research_data: Dict[str, Any]) -> str:
        """Determine what type of enrichment was made"""
        
        if research_data.get('validation_status') == 'validated':
            return 'validation_confirmed'
        elif research_data.get('validation_status') == 'disputed':
            return 'value_disputed'
        elif research_data.get('sources'):
            return 'source_enrichment'
        else:
            return 'research_attempted'
    
    def _apply_enrichments(self, material_data: Dict[str, Any], enrichments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply research enrichments to material data"""
        
        for enrichment in enrichments:
            prop_name = enrichment['property']
            research_findings = enrichment['research_findings']
            
            if prop_name not in material_data.get('materialProperties', {}):
                continue
            
            prop_data = material_data['materialProperties'][prop_name]
            
            # Apply confidence improvements
            if research_findings.get('consensus_confidence', 0) > prop_data.get('confidence', 0):
                prop_data['confidence'] = research_findings['consensus_confidence']
                self.research_stats['enrichments_made'] += 1
            
            # Add source information
            if research_findings.get('sources'):
                prop_data['research_sources'] = len(research_findings['sources'])
                prop_data['last_researched'] = enrichment['research_timestamp']
            
            # Mark validation status
            if research_findings.get('validation_status'):
                prop_data['validation_status'] = research_findings['validation_status']
        
        return material_data
    
    def _calculate_research_confidence(self, enrichments: List[Dict[str, Any]]) -> float:
        """Calculate overall research confidence for a material"""
        
        if not enrichments:
            return 0.0
        
        confidence_scores = []
        for enrichment in enrichments:
            research_findings = enrichment.get('research_findings', {})
            confidence = research_findings.get('consensus_confidence', 0.5)
            confidence_scores.append(confidence)
        
        return sum(confidence_scores) / len(confidence_scores)
    
    def _create_cache_key(self, material_name: str, prop_name: str, prop_data: Dict[str, Any]) -> str:
        """Create cache key for research results"""
        
        # Create hash of relevant data
        key_data = {
            'material': material_name,
            'property': prop_name,
            'value': prop_data.get('value'),
            'unit': prop_data.get('unit')
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_cache_valid(self, cached_result: Dict[str, Any]) -> bool:
        """Check if cached research result is still valid"""
        
        try:
            timestamp = datetime.fromisoformat(cached_result['timestamp'])
            age = (datetime.now() - timestamp).total_seconds()
            max_age = self.research_config.get('cache_duration', 86400)
            
            return age < max_age
        except:
            return False
    
    def _save_enriched_material(self, yaml_file: Path, data: Dict[str, Any]):
        """Save enriched material data back to file"""
        
        try:
            # Create backup
            backup_dir = Path("backups/research")
            backup_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"{yaml_file.stem}_backup_{timestamp}.yaml"
            
            # Copy original to backup
            with open(yaml_file, 'r') as f:
                original_content = f.read()
            with open(backup_file, 'w') as f:
                f.write(original_content)
            
            # Save enriched version
            with open(yaml_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
        except Exception as e:
            print(f"⚠️  Could not save enriched data for {yaml_file}: {e}")
    
    def _generate_research_summary(self, results: List[Dict[str, Any]], enrichments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive summary of research results"""
        
        successful_materials = [r for r in results if r.get('status') == 'success']
        failed_materials = [r for r in results if r.get('status') == 'error']
        
        # Analyze enrichment types
        enrichment_types = {}
        for enrichment in enrichments:
            enrichment_type = enrichment.get('enrichment_type', 'unknown')
            enrichment_types[enrichment_type] = enrichment_types.get(enrichment_type, 0) + 1
        
        # Calculate average confidence improvement
        confidence_improvements = [e.get('confidence_improvement', 0) for e in enrichments]
        avg_confidence_improvement = sum(confidence_improvements) / len(confidence_improvements) if confidence_improvements else 0
        
        # Validation statistics
        validated_properties = len([e for e in enrichments if e.get('research_findings', {}).get('validation_status') == 'validated'])
        disputed_properties = len([e for e in enrichments if e.get('research_findings', {}).get('validation_status') == 'disputed'])
        
        return {
            'materials_researched': len(results),
            'successful_research': len(successful_materials),
            'failed_research': len(failed_materials),
            'total_enrichments': len(enrichments),
            'enrichment_types': enrichment_types,
            'validated_properties': validated_properties,
            'disputed_properties': disputed_properties,
            'avg_confidence_improvement': round(avg_confidence_improvement, 3),
            'research_efficiency': len(enrichments) / max(1, self.research_stats['sources_consulted']),
            'cache_hit_rate': self.research_stats['cache_hits'] / max(1, self.research_stats['properties_researched'])
        }

async def main():
    """Test the research functionality"""
    
    researcher = PropertyResearcher()
    
    # Run research on a subset of materials for testing
    test_materials = ['aluminum', 'steel', 'copper']  # Limit for testing
    results = await researcher.research_properties(materials_filter=test_materials)
    
    # Save results
    results_dir = Path("pipeline_results")
    results_dir.mkdir(exist_ok=True)
    
    with open(results_dir / "stage3_research_results.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "="*60)
    print("🔬 RESEARCH STAGE COMPLETE")
    print("="*60)
    print(f"Materials researched: {results['summary']['materials_researched']}")
    print(f"Total enrichments: {results['summary']['total_enrichments']}")
    print(f"Validated properties: {results['summary']['validated_properties']}")
    print(f"Disputed properties: {results['summary']['disputed_properties']}")
    print(f"Avg confidence improvement: {results['summary']['avg_confidence_improvement']:.3f}")
    
    print("\nEnrichment types:")
    for enrichment_type, count in results['summary']['enrichment_types'].items():
        print(f"  🔬 {enrichment_type}: {count}")

if __name__ == "__main__":
    asyncio.run(main())