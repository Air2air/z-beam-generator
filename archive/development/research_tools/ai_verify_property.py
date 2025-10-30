#!/usr/bin/env python3
"""
AI Property Verification Tool
==============================
Uses AI to verify property values extracted from Materials.yaml.

This tool:
- Reads an extracted property research file
- Uses DeepSeek API to verify each value against scientific databases
- Calculates variance and flags discrepancies
- Creates full audit trail with AI prompts, responses, references
- Updates the research file with verification results

Usage:
    python3 scripts/research_tools/ai_verify_property.py --file data/research/material_properties/density_research.yaml
    python3 scripts/research_tools/ai_verify_property.py --file density_research.yaml --batch-size 10
    python3 scripts/research_tools/ai_verify_property.py --file density_research.yaml --material Aluminum
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime
import argparse
from typing import Dict, Any, Optional
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class PropertyVerifier:
    """AI-powered property verification with full audit trail"""
    
    def __init__(self, api_client):
        self.client = api_client
        self.verification_count = 0
        self.total_cost = 0.0
        
    def create_verification_prompt(self, material_name: str, property_name: str, 
                                   current_value: Any, unit: str) -> str:
        """Create AI prompt for property verification"""
        
        prompt = f"""You are a materials science expert. Verify the following property value:

Material: {material_name}
Property: {property_name}
Current Value: {current_value} {unit}

Task:
1. Research the scientifically accurate value for this property
2. Cite at least 2 authoritative references (NIST, ASM Handbook, CRC Handbook, etc.)
3. Compare with the current value
4. Provide your verified value with confidence level

Response Format:
VERIFIED_VALUE: [your verified value] {unit}
CONFIDENCE: [0-100]
REFERENCES: [source1], [source2]
REASONING: [brief explanation of why this value is correct]
VARIANCE: [percentage difference from current value, if any]
"""
        return prompt
    
    def parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse structured AI response"""
        
        result = {
            'verified_value': None,
            'confidence': 0,
            'references': [],
            'reasoning': '',
            'variance_pct': 0.0
        }
        
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('VERIFIED_VALUE:'):
                # Extract numeric value
                value_str = line.replace('VERIFIED_VALUE:', '').strip()
                # Remove unit and get just the number
                value_str = value_str.split()[0]
                try:
                    result['verified_value'] = float(value_str)
                except ValueError:
                    pass
            
            elif line.startswith('CONFIDENCE:'):
                conf_str = line.replace('CONFIDENCE:', '').strip()
                try:
                    result['confidence'] = int(conf_str)
                except ValueError:
                    pass
            
            elif line.startswith('REFERENCES:'):
                refs = line.replace('REFERENCES:', '').strip()
                result['references'] = [r.strip() for r in refs.split(',')]
            
            elif line.startswith('REASONING:'):
                result['reasoning'] = line.replace('REASONING:', '').strip()
            
            elif line.startswith('VARIANCE:'):
                var_str = line.replace('VARIANCE:', '').strip()
                var_str = var_str.replace('%', '').strip()
                try:
                    result['variance_pct'] = float(var_str)
                except ValueError:
                    pass
        
        return result
    
    def calculate_variance(self, current: float, verified: float) -> float:
        """Calculate percentage variance between current and verified values"""
        
        if current == 0:
            return 100.0 if verified != 0 else 0.0
        
        variance = abs((verified - current) / current) * 100
        return round(variance, 2)
    
    def determine_status(self, variance_pct: float, confidence: int) -> str:
        """Determine verification status based on variance and confidence"""
        
        if confidence < 80:
            return 'LOW_CONFIDENCE'
        
        if variance_pct < 0.5:
            return 'VERIFIED'
        elif variance_pct < 2.0:
            return 'MINOR_VARIANCE'
        elif variance_pct < 5.0:
            return 'NEEDS_REVIEW'
        else:
            return 'CRITICAL_ERROR'
    
    def verify_material_property(self, material_name: str, material_data: Dict[str, Any],
                                property_name: str) -> Dict[str, Any]:
        """Verify a single material's property value using AI"""
        
        current_value = material_data['current_value']
        unit = material_data.get('unit', '')
        
        print(f"  🔍 Verifying {material_name}... ", end='', flush=True)
        
        # Create verification prompt
        prompt = self.create_verification_prompt(material_name, property_name, 
                                                 current_value, unit)
        
        # Get AI response
        try:
            from api.client import GenerationRequest
            
            request = GenerationRequest(
                prompt=prompt,
                temperature=0.1,  # Low temperature for factual accuracy
                max_tokens=500
            )
            
            api_response = self.client.generate(request)
            
            if not api_response.success:
                print(f"❌ API error: {api_response.error}")
                return self._create_error_result(material_data, api_response.error)
            
            response = api_response.content
            
            # Parse response
            parsed = self.parse_ai_response(response)
            
            if parsed['verified_value'] is None:
                print("❌ Failed to parse")
                return self._create_error_result(material_data, "Failed to parse AI response")
            
            # Calculate variance
            variance = self.calculate_variance(current_value, parsed['verified_value'])
            
            # Determine status
            status = self.determine_status(variance, parsed['confidence'])
            
            # Update material data
            material_data['ai_verified_value'] = parsed['verified_value']
            material_data['variance'] = f"{variance}%"
            material_data['status'] = status
            material_data['ai_confidence'] = parsed['confidence']
            material_data['ai_references'] = parsed['references']
            material_data['ai_reasoning'] = parsed['reasoning']
            material_data['ai_prompt'] = prompt
            material_data['ai_response'] = response
            material_data['verification_date'] = datetime.now().isoformat()
            
            # Status emoji
            status_emoji = {
                'VERIFIED': '✅',
                'MINOR_VARIANCE': '⚠️',
                'NEEDS_REVIEW': '🔶',
                'CRITICAL_ERROR': '🚨',
                'LOW_CONFIDENCE': '❓'
            }
            
            print(f"{status_emoji.get(status, '❓')} {status} ({variance}% variance)")
            
            self.verification_count += 1
            
            return material_data
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return self._create_error_result(material_data, str(e))
    
    def _create_error_result(self, material_data: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        """Create error result for failed verification"""
        
        material_data['status'] = 'ERROR'
        material_data['error'] = error_msg
        material_data['verification_date'] = datetime.now().isoformat()
        
        return material_data
    
    def verify_research_file(self, research_file: Path, batch_size: int = None,
                            specific_material: str = None) -> Dict[str, Any]:
        """Verify all materials in a research file"""
        
        print(f"\n🔬 AI Property Verification")
        print("=" * 70)
        
        # Load research file
        with open(research_file, 'r') as f:
            research_data = yaml.safe_load(f)
        
        property_info = research_data.get('property', {})
        property_name = property_info.get('name', 'unknown')
        materials = research_data.get('materials', {})
        
        print(f"📄 Research File: {research_file.name}")
        print(f"🔬 Property: {property_name}")
        print(f"📊 Total Materials: {len(materials)}")
        
        # Filter materials if specific material requested
        if specific_material:
            if specific_material in materials:
                materials = {specific_material: materials[specific_material]}
                print(f"🎯 Verifying single material: {specific_material}")
            else:
                print(f"❌ Material '{specific_material}' not found in research file")
                return research_data
        
        # Apply batch size limit
        if batch_size:
            material_items = list(materials.items())[:batch_size]
            materials = dict(material_items)
            print(f"📦 Batch Size: {batch_size} materials")
        
        print("=" * 70)
        
        # Verify each material
        start_time = time.time()
        
        for material_name, material_data in materials.items():
            # Skip already verified (unless re-verification requested)
            if material_data.get('status') not in ['PENDING', 'ERROR', None]:
                print(f"  ⏭️  Skipping {material_name} (already verified)")
                continue
            
            # Verify
            updated_data = self.verify_material_property(
                material_name, material_data, property_name
            )
            
            # Update in research data
            research_data['materials'][material_name] = updated_data
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        elapsed = time.time() - start_time
        
        # Update research status
        verification_stats = self._calculate_verification_stats(research_data['materials'])
        research_data['research_status']['ai_verification_complete'] = (
            verification_stats['pending_count'] == 0
        )
        research_data['research_status']['last_verification_date'] = datetime.now().isoformat()
        research_data['research_status']['verification_stats'] = verification_stats
        
        # Save updated research file
        with open(research_file, 'w') as f:
            yaml.dump(research_data, f, default_flow_style=False, sort_keys=False, indent=2)
        
        # Print summary
        print("=" * 70)
        print(f"\n✅ Verification Complete!")
        print(f"⏱️  Time: {elapsed:.1f}s")
        print(f"📊 Verified: {self.verification_count} materials")
        print(f"\n📈 Status Breakdown:")
        for status, count in verification_stats['status_counts'].items():
            print(f"   {status}: {count}")
        
        print(f"\n🔍 Critical Issues: {verification_stats['critical_count']}")
        print(f"⚠️  Needs Review: {verification_stats['review_count']}")
        print(f"✅ Verified: {verification_stats['verified_count']}")
        
        if verification_stats['critical_count'] > 0:
            print(f"\n🚨 CRITICAL: {verification_stats['critical_count']} materials need immediate correction!")
            self._list_critical_issues(research_data['materials'])
        
        print(f"\n💾 Updated: {research_file}")
        print("=" * 70 + "\n")
        
        return research_data
    
    def _calculate_verification_stats(self, materials: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate verification statistics"""
        
        stats = {
            'total_count': len(materials),
            'verified_count': 0,
            'pending_count': 0,
            'review_count': 0,
            'critical_count': 0,
            'error_count': 0,
            'status_counts': {}
        }
        
        for material_data in materials.values():
            status = material_data.get('status', 'PENDING')
            
            stats['status_counts'][status] = stats['status_counts'].get(status, 0) + 1
            
            if status == 'VERIFIED':
                stats['verified_count'] += 1
            elif status == 'PENDING':
                stats['pending_count'] += 1
            elif status in ['NEEDS_REVIEW', 'MINOR_VARIANCE']:
                stats['review_count'] += 1
            elif status == 'CRITICAL_ERROR':
                stats['critical_count'] += 1
            elif status == 'ERROR':
                stats['error_count'] += 1
        
        return stats
    
    def _list_critical_issues(self, materials: Dict[str, Any]):
        """List materials with critical errors"""
        
        print("\n🚨 Critical Issues:")
        for material_name, material_data in materials.items():
            if material_data.get('status') == 'CRITICAL_ERROR':
                current = material_data.get('current_value')
                verified = material_data.get('ai_verified_value')
                variance = material_data.get('variance', 'N/A')
                print(f"   • {material_name}: {current} → {verified} ({variance} variance)")


def main():
    parser = argparse.ArgumentParser(
        description='Verify property values using AI research'
    )
    parser.add_argument('--file', type=str, required=True,
                       help='Research file to verify (e.g., density_research.yaml)')
    parser.add_argument('--batch-size', type=int,
                       help='Limit verification to first N materials (for testing)')
    parser.add_argument('--material', type=str,
                       help='Verify only a specific material')
    
    args = parser.parse_args()
    
    # Resolve file path
    research_file = Path(args.file)
    if not research_file.is_absolute():
        research_file = project_root / args.file
    
    if not research_file.exists():
        print(f"❌ Error: Research file not found: {research_file}")
        sys.exit(1)
    
    # Initialize API client
    print("🔧 Initializing API client...")
    from api.client_manager import setup_api_client
    client = setup_api_client(provider="deepseek")
    
    # Create verifier
    verifier = PropertyVerifier(client)
    
    # Run verification
    verifier.verify_research_file(
        research_file,
        batch_size=args.batch_size,
        specific_material=args.material
    )


if __name__ == '__main__':
    main()
