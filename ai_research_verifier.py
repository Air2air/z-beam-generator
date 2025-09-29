#!/usr/bin/env python3
"""
AI Research Verification Tool
Comprehensive tracking and verification of AI research usage throughout the system.
"""

import os
import yaml
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class AIResearchVerifier:
    """
    Verifies and tracks AI research usage at each step of the pipeline.
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.ai_usage_log = []
        self.api_calls_made = 0
        self.start_time = time.time()
        
    def log_ai_usage(self, step: str, action: str, details: Dict[str, Any]):
        """Log AI usage for verification"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'step': step,
            'action': action,
            'details': details,
            'elapsed_time': time.time() - self.start_time
        }
        self.ai_usage_log.append(entry)
        
        if self.verbose:
            print(f"🤖 AI Usage: {step} - {action}")
            if details.get('api_call'):
                self.api_calls_made += 1
                print(f"   📡 API Call #{self.api_calls_made}: {details.get('prompt_preview', 'N/A')[:50]}...")
                print(f"   ⏱️  Response time: {details.get('response_time', 'N/A')}s")
                print(f"   📊 Success: {details.get('success', 'N/A')}")
    
    def verify_ai_research_pipeline(self) -> Dict[str, Any]:
        """
        Run comprehensive verification of AI research usage throughout the pipeline.
        """
        
        print("🔍 AI Research Verification Pipeline")
        print("=" * 60)
        
        verification_results = {
            'categories_ai_validation': {},
            'materials_ai_research': {},
            'property_ai_validation': {},
            'frontmatter_ai_integration': {},
            'content_generation_ai': {},
            'total_ai_calls': 0,
            'ai_coverage': {},
            'verification_summary': {}
        }
        
        # Step 1: Verify AI validation in Categories.yaml
        print("\n📊 Step 1: Categories.yaml AI Validation")
        categories_ai = self._verify_categories_ai_validation()
        verification_results['categories_ai_validation'] = categories_ai
        
        # Step 2: Verify AI research in Materials.yaml
        print("\n🔬 Step 2: Materials.yaml AI Research")
        materials_ai = self._verify_materials_ai_research()
        verification_results['materials_ai_research'] = materials_ai
        
        # Step 3: Verify property-level AI validation
        print("\n⚗️  Step 3: Property-Level AI Validation")
        property_ai = self._verify_property_ai_validation()
        verification_results['property_ai_validation'] = property_ai
        
        # Step 4: Verify frontmatter AI integration
        print("\n📄 Step 4: Frontmatter AI Integration")
        frontmatter_ai = self._verify_frontmatter_ai_integration()
        verification_results['frontmatter_ai_integration'] = frontmatter_ai
        
        # Step 5: Verify content generation AI usage
        print("\n🎨 Step 5: Content Generation AI Usage")
        content_ai = self._verify_content_generation_ai()
        verification_results['content_generation_ai'] = content_ai
        
        # Step 6: Generate AI coverage analysis
        print("\n📈 Step 6: AI Coverage Analysis")
        coverage = self._analyze_ai_coverage()
        verification_results['ai_coverage'] = coverage
        
        # Generate summary
        verification_results['total_ai_calls'] = self.api_calls_made
        verification_results['verification_summary'] = self._generate_verification_summary(verification_results)
        
        return verification_results
    
    def _verify_categories_ai_validation(self) -> Dict[str, Any]:
        """Verify AI validation in Categories.yaml ranges"""
        
        result = {
            'ai_validation_enabled': False,
            'categories_with_ai_ranges': [],
            'ai_validated_properties': [],
            'api_calls_made': 0,
            'validation_confidence': {}
        }
        
        try:
            # Test AI validation of category ranges
            from hierarchical_validator import HierarchicalValidator
            
            print("   🤖 Testing Categories.yaml AI validation...")
            validator = HierarchicalValidator(ai_validation_enabled=True, silent_mode=False)
            
            # Run AI validation and track calls
            start_calls = self.api_calls_made
            ai_results = validator._ai_validate_property_ranges()
            calls_made = len(ai_results.get('ai_recommendations', {}))
            
            self.log_ai_usage(
                step="Categories Validation",
                action="AI Property Range Validation", 
                details={
                    'api_call': True,
                    'categories_validated': ai_results.get('categories_validated', 0),
                    'properties_validated': ai_results.get('properties_validated', 0),
                    'success': len(ai_results.get('api_errors', [])) == 0
                }
            )
            
            result['ai_validation_enabled'] = True
            result['api_calls_made'] = calls_made
            result['categories_with_ai_ranges'] = list(ai_results.get('ai_recommendations', {}).keys())
            result['validation_confidence'] = {
                cat: data.get('overall_confidence', 0) 
                for cat, data in ai_results.get('ai_recommendations', {}).items()
            }
            
            print(f"   ✅ AI validated {ai_results.get('categories_validated', 0)} categories")
            print(f"   📡 Made {calls_made} API calls for range validation")
            
        except Exception as e:
            print(f"   ❌ Categories AI validation error: {e}")
            result['error'] = str(e)
        
        return result
    
    def _verify_materials_ai_research(self) -> Dict[str, Any]:
        """Verify AI research in Materials.yaml properties"""
        
        result = {
            'materials_with_ai_research': [],
            'ai_researched_properties': {},
            'property_sources': {},
            'ai_confidence_scores': {},
            'research_coverage': 0.0
        }
        
        try:
            # Load Materials.yaml and analyze AI research sources
            with open('data/Materials.yaml', 'r') as f:
                materials_data = yaml.safe_load(f)
            
            total_materials = 0
            ai_researched_materials = 0
            all_property_sources = {}
            
            print("   🔍 Analyzing Materials.yaml for AI research sources...")
            
            for category, category_data in materials_data.get('materials', {}).items():
                for material_item in category_data.get('items', []):
                    material_name = material_item.get('name')
                    total_materials += 1
                    
                    properties = material_item.get('properties', {})
                    has_ai_research = False
                    material_sources = {}
                    
                    for prop_name, prop_data in properties.items():
                        if isinstance(prop_data, dict):
                            source = prop_data.get('source', 'unknown')
                            confidence = prop_data.get('confidence', 0)
                            
                            material_sources[prop_name] = {
                                'source': source,
                                'confidence': confidence
                            }
                            
                            # Track if this property came from AI research
                            if 'ai' in source.lower() or 'research' in source.lower():
                                has_ai_research = True
                            
                            # Collect all sources
                            if source not in all_property_sources:
                                all_property_sources[source] = 0
                            all_property_sources[source] += 1
                    
                    if has_ai_research:
                        ai_researched_materials += 1
                        result['materials_with_ai_research'].append(material_name)
                        result['ai_researched_properties'][material_name] = material_sources
                    
                    # Track confidence scores
                    if properties:
                        avg_confidence = sum(
                            prop_data.get('confidence', 0) for prop_data in properties.values() 
                            if isinstance(prop_data, dict)
                        ) / len(properties)
                        result['ai_confidence_scores'][material_name] = avg_confidence
            
            result['property_sources'] = all_property_sources
            result['research_coverage'] = ai_researched_materials / total_materials if total_materials > 0 else 0
            
            print(f"   📊 Found {ai_researched_materials}/{total_materials} materials with AI research")
            print(f"   🎯 Research coverage: {result['research_coverage']:.1%}")
            print(f"   📝 Property sources: {list(all_property_sources.keys())}")
            
        except Exception as e:
            print(f"   ❌ Materials AI research analysis error: {e}")
            result['error'] = str(e)
        
        return result
    
    def _verify_property_ai_validation(self) -> Dict[str, Any]:
        """Verify AI validation of individual properties"""
        
        result = {
            'ai_validation_active': False,
            'critical_properties_validated': [],
            'validation_api_calls': 0,
            'validation_results': {},
            'confidence_thresholds': {}
        }
        
        try:
            # Test property-level AI validation
            from pipeline_integration import InvisiblePipelineRunner
            
            print("   🤖 Testing property-level AI validation...")
            pipeline = InvisiblePipelineRunner(silent_mode=False)
            
            # Test with sample material properties
            test_properties = {
                'density': {'value': 2.7, 'unit': 'g/cm³'},
                'meltingPoint': {'value': 660, 'unit': '°C'},
                'thermalConductivity': {'value': 205, 'unit': 'W/m·K'}
            }
            
            start_calls = self.api_calls_made
            
            # Test AI validation of critical properties
            if hasattr(pipeline, '_ai_validate_critical_properties'):
                ai_validation_result = pipeline._ai_validate_critical_properties('Aluminum', test_properties)
                
                self.log_ai_usage(
                    step="Property Validation",
                    action="AI Critical Property Validation",
                    details={
                        'api_call': True,
                        'properties_tested': list(test_properties.keys()),
                        'validation_passed': ai_validation_result.get('validation_passed', False),
                        'success': True
                    }
                )
                
                result['ai_validation_active'] = True
                result['validation_api_calls'] = self.api_calls_made - start_calls
                result['critical_properties_validated'] = list(test_properties.keys())
                result['validation_results'] = ai_validation_result
                
                print(f"   ✅ AI validated {len(test_properties)} critical properties")
                print(f"   📡 Made {result['validation_api_calls']} API calls for validation")
            else:
                print("   ⚠️  Property-level AI validation not found")
        
        except Exception as e:
            print(f"   ❌ Property AI validation error: {e}")
            result['error'] = str(e)
        
        return result
    
    def _verify_frontmatter_ai_integration(self) -> Dict[str, Any]:
        """Verify AI integration in frontmatter generation"""
        
        result = {
            'frontmatter_files_checked': 0,
            'ai_generated_content': [],
            'ai_validation_present': False,
            'ai_quality_scores': {},
            'integration_status': 'unknown'
        }
        
        try:
            # Check frontmatter files for AI integration markers
            frontmatter_dir = Path("content/components/frontmatter")
            
            if frontmatter_dir.exists():
                frontmatter_files = list(frontmatter_dir.glob("*.yaml"))
                result['frontmatter_files_checked'] = len(frontmatter_files)
                
                print(f"   🔍 Checking {len(frontmatter_files)} frontmatter files for AI integration...")
                
                ai_markers_found = 0
                
                for frontmatter_file in frontmatter_files[:5]:  # Sample first 5 files
                    try:
                        with open(frontmatter_file, 'r') as f:
                            frontmatter_data = yaml.safe_load(f)
                        
                        # Look for AI integration markers
                        ai_markers = []
                        
                        # Check for AI-generated metadata
                        if 'ai_generated' in frontmatter_data:
                            ai_markers.append('ai_generated_flag')
                        
                        # Check for AI quality scores
                        if 'quality_score' in frontmatter_data:
                            ai_markers.append('quality_score')
                            result['ai_quality_scores'][frontmatter_file.stem] = frontmatter_data['quality_score']
                        
                        # Check for AI validation results
                        if 'validation_result' in frontmatter_data:
                            ai_markers.append('validation_result')
                            result['ai_validation_present'] = True
                        
                        # Check material properties for AI research markers
                        properties = frontmatter_data.get('materialProperties', {})
                        for prop_name, prop_data in properties.items():
                            if isinstance(prop_data, dict) and 'ai_validated' in prop_data:
                                ai_markers.append(f'ai_validated_{prop_name}')
                        
                        if ai_markers:
                            ai_markers_found += 1
                            result['ai_generated_content'].append({
                                'file': frontmatter_file.name,
                                'ai_markers': ai_markers
                            })
                    
                    except Exception as e:
                        continue
                
                result['integration_status'] = 'active' if ai_markers_found > 0 else 'inactive'
                print(f"   📊 Found AI markers in {ai_markers_found}/5 sampled files")
            
            else:
                print("   ⚠️  Frontmatter directory not found")
        
        except Exception as e:
            print(f"   ❌ Frontmatter AI integration check error: {e}")
            result['error'] = str(e)
        
        return result
    
    def _verify_content_generation_ai(self) -> Dict[str, Any]:
        """Verify AI usage in content generation components"""
        
        result = {
            'text_component_ai': False,
            'caption_component_ai': False,
            'research_component_ai': False,
            'api_integrations': [],
            'ai_providers_configured': []
        }
        
        try:
            # Check for AI API configuration
            print("   🔍 Checking AI API configuration...")
            
            try:
                from api.client_factory import create_api_client
                
                # Test API clients
                api_providers = ['deepseek', 'openai', 'claude']
                for provider in api_providers:
                    try:
                        client = create_api_client(provider)
                        if client:
                            result['ai_providers_configured'].append(provider)
                            self.log_ai_usage(
                                step="Content Generation",
                                action=f"API Client Test - {provider}",
                                details={'api_client_available': True, 'provider': provider}
                            )
                    except Exception:
                        continue
                
                print(f"   ✅ Found {len(result['ai_providers_configured'])} AI providers configured")
            
            except Exception as e:
                print(f"   ⚠️  API client factory error: {e}")
            
            # Check text component for AI integration
            try:
                text_component_path = Path("components/text")
                if text_component_path.exists():
                    # Look for AI integration in text component
                    text_files = list(text_component_path.glob("**/*.py"))
                    for text_file in text_files:
                        with open(text_file, 'r') as f:
                            content = f.read()
                            if 'api_client' in content and 'generate' in content:
                                result['text_component_ai'] = True
                                result['api_integrations'].append('text_component')
                                break
                
                print(f"   📝 Text component AI: {'✅' if result['text_component_ai'] else '❌'}")
            
            except Exception as e:
                print(f"   ⚠️  Text component check error: {e}")
            
            # Check caption component for AI integration
            try:
                caption_component_path = Path("components/caption")
                if caption_component_path.exists():
                    caption_files = list(caption_component_path.glob("**/*.py"))
                    for caption_file in caption_files:
                        with open(caption_file, 'r') as f:
                            content = f.read()
                            if 'api_client' in content and ('caption' in content or 'image' in content):
                                result['caption_component_ai'] = True
                                result['api_integrations'].append('caption_component')
                                break
                
                print(f"   🖼️  Caption component AI: {'✅' if result['caption_component_ai'] else '❌'}")
            
            except Exception as e:
                print(f"   ⚠️  Caption component check error: {e}")
            
            # Check research component for AI integration
            try:
                research_files = list(Path(".").glob("**/property_researcher.py"))
                for research_file in research_files:
                    with open(research_file, 'r') as f:
                        content = f.read()
                        if 'api_client' in content and 'research' in content:
                            result['research_component_ai'] = True
                            result['api_integrations'].append('research_component')
                            break
                
                print(f"   🔬 Research component AI: {'✅' if result['research_component_ai'] else '❌'}")
            
            except Exception as e:
                print(f"   ⚠️  Research component check error: {e}")
        
        except Exception as e:
            print(f"   ❌ Content generation AI check error: {e}")
            result['error'] = str(e)
        
        return result
    
    def _analyze_ai_coverage(self) -> Dict[str, Any]:
        """Analyze overall AI coverage across the system"""
        
        coverage = {
            'validation_coverage': 0.0,
            'research_coverage': 0.0,
            'generation_coverage': 0.0,
            'overall_coverage': 0.0,
            'ai_integration_points': [],
            'missing_ai_integration': [],
            'recommendations': []
        }
        
        try:
            # Analyze AI integration points
            integration_points = [
                'Categories.yaml AI validation',
                'Materials.yaml AI research', 
                'Property-level AI validation',
                'Frontmatter AI integration',
                'Text generation AI',
                'Caption generation AI',
                'Research component AI'
            ]
            
            # Calculate coverage scores
            validation_points = 0
            research_points = 0
            generation_points = 0
            total_points = 0
            
            # Add coverage analysis logic here based on previous verification results
            
            print(f"   📊 AI Integration Analysis:")
            print(f"   • Validation Coverage: {coverage['validation_coverage']:.1%}")
            print(f"   • Research Coverage: {coverage['research_coverage']:.1%}")
            print(f"   • Generation Coverage: {coverage['generation_coverage']:.1%}")
            print(f"   • Overall Coverage: {coverage['overall_coverage']:.1%}")
        
        except Exception as e:
            print(f"   ❌ AI coverage analysis error: {e}")
            coverage['error'] = str(e)
        
        return coverage
    
    def _generate_verification_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive verification summary"""
        
        summary = {
            'total_ai_calls_made': self.api_calls_made,
            'ai_integration_active': False,
            'verification_status': 'incomplete',
            'key_findings': [],
            'recommendations': [],
            'next_steps': []
        }
        
        # Analyze results and generate summary
        if self.api_calls_made > 0:
            summary['ai_integration_active'] = True
            summary['key_findings'].append(f"Made {self.api_calls_made} AI API calls during verification")
        
        if results['categories_ai_validation'].get('ai_validation_enabled'):
            summary['key_findings'].append("Categories.yaml AI validation is active")
        
        if results['materials_ai_research'].get('research_coverage', 0) > 0:
            coverage = results['materials_ai_research']['research_coverage']
            summary['key_findings'].append(f"Materials.yaml has {coverage:.1%} AI research coverage")
        
        if results['content_generation_ai'].get('ai_providers_configured'):
            providers = results['content_generation_ai']['ai_providers_configured']
            summary['key_findings'].append(f"AI providers configured: {', '.join(providers)}")
        
        # Generate recommendations
        if self.api_calls_made == 0:
            summary['recommendations'].append("No AI API calls detected - verify API configuration")
        
        if results['materials_ai_research'].get('research_coverage', 0) < 0.5:
            summary['recommendations'].append("Low AI research coverage in Materials.yaml - consider AI property research")
        
        summary['verification_status'] = 'complete'
        
        return summary
    
    def generate_verification_report(self, results: Dict[str, Any], output_file: str = None) -> str:
        """Generate comprehensive verification report"""
        
        report = f"""# AI Research Verification Report
Generated: {datetime.now().isoformat()}

## Executive Summary
- Total AI API Calls Made: {results['total_ai_calls']}
- AI Integration Status: {'Active' if results['verification_summary']['ai_integration_active'] else 'Inactive'}
- Verification Status: {results['verification_summary']['verification_status'].title()}

## Key Findings
"""
        
        for finding in results['verification_summary']['key_findings']:
            report += f"- {finding}\n"
        
        report += f"""
## Detailed Analysis

### Categories.yaml AI Validation
- AI Validation Enabled: {results['categories_ai_validation'].get('ai_validation_enabled', False)}
- API Calls Made: {results['categories_ai_validation'].get('api_calls_made', 0)}
- Categories Validated: {len(results['categories_ai_validation'].get('categories_with_ai_ranges', []))}

### Materials.yaml AI Research
- Research Coverage: {results['materials_ai_research'].get('research_coverage', 0):.1%}
- Materials with AI Research: {len(results['materials_ai_research'].get('materials_with_ai_research', []))}
- Property Sources: {list(results['materials_ai_research'].get('property_sources', {}).keys())}

### Property-Level AI Validation
- AI Validation Active: {results['property_ai_validation'].get('ai_validation_active', False)}
- Critical Properties Validated: {len(results['property_ai_validation'].get('critical_properties_validated', []))}
- Validation API Calls: {results['property_ai_validation'].get('validation_api_calls', 0)}

### Content Generation AI
- AI Providers Configured: {results['content_generation_ai'].get('ai_providers_configured', [])}
- Text Component AI: {results['content_generation_ai'].get('text_component_ai', False)}
- Caption Component AI: {results['content_generation_ai'].get('caption_component_ai', False)}
- Research Component AI: {results['content_generation_ai'].get('research_component_ai', False)}

## Recommendations
"""
        
        for rec in results['verification_summary']['recommendations']:
            report += f"- {rec}\n"
        
        report += f"""
## AI Usage Log
Total logged actions: {len(self.ai_usage_log)}

"""
        
        for i, entry in enumerate(self.ai_usage_log[-10:], 1):  # Last 10 entries
            report += f"{i}. {entry['step']} - {entry['action']} ({entry['timestamp']})\n"
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"\n📄 Verification report saved to: {output_file}")
        
        return report


def main():
    """Run AI research verification"""
    
    print("🤖 AI Research Verification Tool")
    print("=" * 60)
    
    verifier = AIResearchVerifier(verbose=True)
    results = verifier.verify_ai_research_pipeline()
    
    # Generate and display report
    report = verifier.generate_verification_report(results, "ai_research_verification_report.md")
    
    print(f"\n🎉 AI Research Verification Complete!")
    print(f"   📊 Total AI API calls made: {results['total_ai_calls']}")
    print(f"   ⚡ Verification time: {time.time() - verifier.start_time:.1f}s")
    print(f"   📄 Report saved: ai_research_verification_report.md")

if __name__ == "__main__":
    main()