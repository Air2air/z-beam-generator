"""
Laser Parameter Researcher - Phase 2A Data Population

Researches and populates the 8 missing laser parameters in Settings.yaml:
- power (W)
- scan_speed (mm/s)
- pulse_width (ns)
- repetition_rate (kHz)
- energy_density (J/cm²)
- spot_size (μm)
- pass_count (passes)
- overlap_ratio (%)

Uses Gemini to research academic literature, manufacturer specs, and industry standards.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from shared.api.client_factory import APIClientFactory

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class LaserParameterResearcher:
    """Research laser cleaning parameters for materials."""
    
    def __init__(self):
        """Initialize researcher with Grok API client."""
        # Create Grok client via factory
        self.client = APIClientFactory.create_client(provider="grok")
        
        self.settings_path = project_root / 'data' / 'settings' / 'Settings.yaml'
        
        # Load existing settings
        with open(self.settings_path) as f:
            self.settings_data = yaml.safe_load(f)
    
    def research_material_parameters(self, material_name: str) -> Optional[Dict[str, Any]]:
        """
        Research laser cleaning parameters for a specific material.
        
        Args:
            material_name: Material name (e.g., "Aluminum", "Steel")
        
        Returns:
            Dict with researched parameters or None if research fails
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🔬 RESEARCHING: {material_name}")
        logger.info(f"{'='*70}")
        
        # Build comprehensive research prompt
        prompt = self._build_research_prompt(material_name)
        
        try:
            # Call API for research
            logger.info("📡 Querying API for laser cleaning parameters...")
            
            from shared.api.client import GenerationRequest
            
            request = GenerationRequest(
                prompt=prompt,
                temperature=0.3,  # Low temp for factual research
                max_tokens=4000,
                system_prompt=(
                    "You are a laser cleaning research expert. Provide accurate, "
                    "research-backed laser parameters from academic literature, "
                    "manufacturer specifications, and industry standards. "
                    "Include ranges and recommended values. Cite sources when possible."
                )
            )
            
            response = self.client.generate(request)
            
            if not response.success:
                logger.error(f"API error: {response.error}")
                return None
            
            # Parse response into structured parameters
            parameters = self._parse_research_response(response.content, material_name)
            
            if parameters:
                logger.info(f"✅ Research complete for {material_name}")
                self._display_results(parameters)
                return parameters
            else:
                logger.warning(f"⚠️  Could not extract parameters for {material_name}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Research failed for {material_name}: {e}")
            return None
    
    def _build_research_prompt(self, material_name: str) -> str:
        """Build comprehensive research prompt."""
        
        # Get existing wavelength for context
        existing = self.settings_data['settings'].get(material_name, {})
        wavelength = existing.get('machine_settings', {}).get('wavelength', {})
        wavelength_value = wavelength.get('value', 1064)
        
        return f"""Research laser cleaning parameters for {material_name}.

CONTEXT:
- Material: {material_name}
- Wavelength: {wavelength_value} nm (already researched)
- Application: Industrial laser cleaning (contamination removal, surface preparation)

REQUIRED PARAMETERS TO RESEARCH (8 total):

1. **Power Range (W)**
   - Typical power range for cleaning {material_name}
   - Recommended starting power
   - Maximum safe power before substrate damage
   - Source: Manufacturer specs, academic papers

2. **Scan Speed (mm/s)**
   - Typical scan speeds for effective cleaning
   - Recommended speed for optimal results
   - Range based on contamination type (light vs heavy)
   - Source: Industry standards, equipment manuals

3. **Pulse Width (ns or ps)**
   - Nanosecond vs picosecond vs femtosecond regimes
   - Typical pulse width for {material_name}
   - Recommended for minimal heat-affected zone
   - Source: Laser physics research

4. **Repetition Rate (kHz)**
   - Typical frequency for cleaning applications
   - Recommended rate for {material_name}
   - Trade-offs (high freq = faster, more heat accumulation)
   - Source: Academic literature

5. **Energy Density / Fluence (J/cm²)**
   - Typical fluence range for cleaning
   - Damage threshold for {material_name}
   - Recommended fluence for safe cleaning
   - Source: Ablation threshold studies

6. **Spot Size (μm or mm)**
   - Typical beam diameter for cleaning
   - Range based on application (fine detail vs large area)
   - Recommended for {material_name}
   - Source: Equipment specifications

7. **Pass Count (passes)**
   - Typical number of passes for complete removal
   - Single pass vs multi-pass approaches
   - Recommended for {material_name}
   - Source: Industry practice, case studies

8. **Overlap Ratio (%)**
   - Typical overlap between adjacent scan lines
   - Recommended for uniform coverage
   - Range: 30-80% typical
   - Source: Process optimization studies

FORMAT YOUR RESPONSE AS YAML (machine-readable):

```yaml
power:
  min: [number]
  max: [number]
  value: [recommended]
  unit: W
  description: "[brief rationale with source if available]"

scan_speed:
  min: [number]
  max: [number]
  value: [recommended]
  unit: mm/s
  description: "[brief rationale]"

pulse_width:
  min: [number]
  max: [number]
  value: [recommended]
  unit: ns
  description: "[brief rationale]"

repetition_rate:
  min: [number]
  max: [number]
  value: [recommended]
  unit: kHz
  description: "[brief rationale]"

energy_density:
  min: [number]
  max: [number]
  value: [recommended]
  unit: J/cm²
  description: "[brief rationale]"

spot_size:
  min: [number]
  max: [number]
  value: [recommended]
  unit: μm
  description: "[brief rationale]"

pass_count:
  min: [number]
  max: [number]
  value: [recommended]
  unit: passes
  description: "[brief rationale]"

overlap_ratio:
  min: [number]
  max: [number]
  value: [recommended]
  unit: '%'
  description: "[brief rationale]"
```

IMPORTANT:
- Provide REALISTIC ranges based on actual laser cleaning equipment
- Include brief descriptions with sources when available
- If uncertain, provide conservative estimates and note uncertainty
- Consider {material_name}'s properties (thermal conductivity, reflectivity, melting point)
"""
    
    def _parse_research_response(self, response: str, material_name: str) -> Optional[Dict[str, Any]]:
        """Parse Gemini response into structured parameters."""
        
        # Try to extract YAML from response
        try:
            # Look for yaml code block
            if '```yaml' in response:
                yaml_start = response.find('```yaml') + 7
                yaml_end = response.find('```', yaml_start)
                yaml_text = response[yaml_start:yaml_end].strip()
            elif '```' in response:
                yaml_start = response.find('```') + 3
                yaml_end = response.find('```', yaml_start)
                yaml_text = response[yaml_start:yaml_end].strip()
            else:
                yaml_text = response
            
            # Parse YAML
            parameters = yaml.safe_load(yaml_text)
            
            # Validate we got all 8 parameters
            required = ['power', 'scan_speed', 'pulse_width', 'repetition_rate', 
                       'energy_density', 'spot_size', 'pass_count', 'overlap_ratio']
            
            if all(param in parameters for param in required):
                return parameters
            else:
                missing = [p for p in required if p not in parameters]
                logger.warning(f"Missing parameters: {missing}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            logger.debug(f"Response was: {response[:500]}...")
            return None
    
    def _display_results(self, parameters: Dict[str, Any]) -> None:
        """Display researched parameters in readable format."""
        
        logger.info("\n📊 RESEARCHED PARAMETERS:\n")
        
        for param_name, param_data in parameters.items():
            if isinstance(param_data, dict):
                value = param_data.get('value', 'N/A')
                unit = param_data.get('unit', '')
                min_val = param_data.get('min', '')
                max_val = param_data.get('max', '')
                desc = param_data.get('description', '')
                
                logger.info(f"  {param_name}:")
                logger.info(f"    Recommended: {value} {unit}")
                if min_val and max_val:
                    logger.info(f"    Range: {min_val}-{max_val} {unit}")
                if desc:
                    logger.info(f"    Notes: {desc[:100]}...")
                logger.info("")
    
    def update_settings_file(self, material_name: str, parameters: Dict[str, Any]) -> bool:
        """
        Update Settings.yaml with researched parameters.
        
        Args:
            material_name: Material name
            parameters: Researched parameter dict
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing material data
            if material_name not in self.settings_data['settings']:
                logger.error(f"Material {material_name} not found in Settings.yaml")
                return False
            
            material_data = self.settings_data['settings'][material_name]
            
            # Ensure machine_settings exists
            if 'machine_settings' not in material_data:
                material_data['machine_settings'] = {}
            
            # Update each parameter
            for param_name, param_data in parameters.items():
                material_data['machine_settings'][param_name] = param_data
            
            # Write back to file
            with open(self.settings_path, 'w') as f:
                yaml.dump(self.settings_data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"✅ Updated Settings.yaml for {material_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Settings.yaml: {e}")
            return False


def main():
    """Research parameters for specific materials or all materials."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Research laser parameters for materials')
    parser.add_argument('--all', action='store_true', help='Research all materials in Settings.yaml')
    parser.add_argument('--materials', nargs='+', help='Specific materials to research')
    parser.add_argument('--skip-existing', action='store_true', help='Skip materials that already have all 8 parameters')
    args = parser.parse_args()
    
    researcher = LaserParameterResearcher()
    
    # Determine which materials to research
    if args.all:
        # Get all materials from Settings.yaml
        materials_to_research = list(researcher.settings_data['settings'].keys())
        print(f"\n🔬 Researching ALL {len(materials_to_research)} materials")
    elif args.materials:
        materials_to_research = args.materials
        print(f"\n🔬 Researching {len(materials_to_research)} specified materials")
    else:
        # Demo mode - just a few materials
        materials_to_research = ['Aluminum', 'Steel', 'Copper']
        print("\n🔬 DEMO MODE - Researching 3 materials")
        print("   Use --all to research all 153 materials")
        print("   Use --materials Material1 Material2 to research specific materials")
    
    print("\n" + "="*70)
    print("🔬 LASER PARAMETER RESEARCH - Phase 2A")
    print("="*70)
    print(f"Materials: {len(materials_to_research)}")
    print(f"Parameters per material: 8")
    print(f"Estimated time: {len(materials_to_research) * 8} seconds (~{len(materials_to_research) * 8 / 60:.1f} minutes)\n")
    
    results = {}
    skipped = 0
    
    for i, material in enumerate(materials_to_research, 1):
        print(f"\n[{i}/{len(materials_to_research)}] Processing {material}...")
        
        # Skip if already has all parameters
        if args.skip_existing:
            existing = researcher.settings_data['settings'].get(material, {}).get('machine_settings', {})
            required_params = ['power', 'scan_speed', 'pulse_width', 'repetition_rate', 
                             'energy_density', 'spot_size', 'pass_count', 'overlap_ratio']
            
            if all(param in existing for param in required_params):
                print(f"   ⏭️  Skipping (already complete)")
                results[material] = 'SKIPPED'
                skipped += 1
                continue
        
        parameters = researcher.research_material_parameters(material)
        
        if parameters:
            # Update Settings.yaml
            success = researcher.update_settings_file(material, parameters)
            results[material] = 'SUCCESS' if success else 'FAILED'
        else:
            results[material] = 'NO DATA'
        
        print("\n" + "-"*70)
    
    # Summary
    print("\n" + "="*70)
    print("📊 RESEARCH SUMMARY")
    print("="*70)
    
    success_count = sum(1 for status in results.values() if status == 'SUCCESS')
    failed_count = sum(1 for status in results.values() if status in ['FAILED', 'NO DATA'])
    
    print(f"✅ Success: {success_count}/{len(materials_to_research)}")
    print(f"❌ Failed: {failed_count}/{len(materials_to_research)}")
    if skipped > 0:
        print(f"⏭️  Skipped: {skipped}/{len(materials_to_research)}")
    
    if failed_count > 0:
        print("\n❌ Failed materials:")
        for material, status in results.items():
            if status in ['FAILED', 'NO DATA']:
                print(f"   - {material}: {status}")
    
    print("\n" + "="*70)
    print(f"✅ Research complete: {success_count} materials updated")
    print("="*70)


if __name__ == '__main__':
    main()
