#!/usr/bin/env python3
"""
Copilot Image Generation Command Handler

Handles natural language image generation requests like:
- "Make me a Bismuth Hero image"
- "Generate Aluminum contamination image"
- "Create Steel before/after split"

Automatically:
- Looks up material from Materials.yaml (category, properties)
- Determines contamination patterns from Contaminants.yaml
- Validates prompt against impossible combinations
- Outputs to correct domain path (materials, contaminants, regions)
- Handles before/after splits for contamination images

Author: AI Assistant
Date: November 26, 2025
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass

# Local imports
from domains.materials.image.material_generator import MaterialImageGenerator
from domains.materials.image.material_config import MaterialImageConfig
from shared.image.validation.payload_validator import ImagePromptPayloadValidator
from shared.api.gemini_image_client import GeminiImageClient


@dataclass
class ImageRequest:
    """Parsed image generation request"""
    material_name: str
    image_type: str  # 'hero', 'micro', 'contamination', 'before-after'
    domain: str  # 'materials', 'contaminants', 'regions'
    output_path: Path
    category: str
    contaminant_id: Optional[str] = None
    has_split: bool = False  # Before/after split


class ImageGenerationHandler:
    """
    Handles Copilot image generation requests with natural language parsing.
    
    Usage:
        handler = ImageGenerationHandler()
        
        # Simple request
        handler.generate("Make me a Bismuth Hero image")
        
        # Contamination request
        handler.generate("Generate Aluminum oil contamination image")
        
        # Before/after split
        handler.generate("Create Steel rust before/after split")
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None, use_category_research: bool = True):
        """
        Initialize image generation handler.
        
        Args:
            gemini_api_key: Optional Gemini API key for image generation
            use_category_research: Use category-level contamination research (default: True)
        """
        self.materials_data = self._load_materials_yaml()
        self.contaminants_data = self._load_contaminants_yaml()
        self.validator = ImagePromptPayloadValidator()
        
        # MaterialImageGenerator with category research
        self.generator = MaterialImageGenerator(
            gemini_api_key=gemini_api_key,
            use_category_research=use_category_research
        )
        
        self.image_client = GeminiImageClient(api_key=gemini_api_key) if gemini_api_key else None
        
        # Output paths
        self.base_path = Path("/Users/todddunning/Desktop/Z-Beam/z-beam-generator/public/images")
        self.materials_path = self.base_path / "materials"
        self.contaminants_path = self.base_path / "contaminants"
        self.regions_path = self.base_path / "regions"
    
    def _load_materials_yaml(self) -> Dict:
        """Load Materials.yaml data"""
        materials_path = Path(__file__).parent.parent.parent / "data" / "materials" / "Materials.yaml"
        with open(materials_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_contaminants_yaml(self) -> Dict:
        """Load Contaminants.yaml data"""
        contaminants_path = Path(__file__).parent.parent.parent / "data" / "contaminants" / "Contaminants.yaml"
        with open(contaminants_path, 'r') as f:
            return yaml.safe_load(f)
    
    def parse_request(self, request: str) -> ImageRequest:
        """
        Parse natural language image generation request.
        
        Examples:
            "Make me a Bismuth Hero image" → Bismuth hero image in materials/
            "Generate Aluminum oil contamination" → Aluminum + oil in materials/
            "Create Steel rust before/after split" → Steel + rust split in materials/
            "Show me a Copper oxide micro image" → Copper + oxide micro in materials/
        
        Args:
            request: Natural language request string
            
        Returns:
            ImageRequest with parsed details
            
        Raises:
            ValueError: If material not found or request cannot be parsed
        """
        # Normalize request
        request_lower = request.lower()
        
        # Extract material name (check against material_index)
        material_name = None
        material_index = self.materials_data.get('material_index', {})
        
        for mat_name in material_index.keys():
            # Check for exact match or word boundary match
            if re.search(r'\b' + re.escape(mat_name.lower()) + r'\b', request_lower):
                material_name = mat_name
                break
        
        if not material_name:
            raise ValueError(
                f"Material not found in request: '{request}'\n"
                f"Available materials: {', '.join(list(material_index.keys())[:10])}..."
            )
        
        # Get category from material_index
        category = material_index[material_name]
        
        # Detect image type
        image_type = self._detect_image_type(request_lower)
        
        # Detect contamination pattern
        contaminant_id = self._detect_contaminant(request_lower)
        
        # Detect before/after split
        has_split = any(term in request_lower for term in [
            'before/after', 'before and after', 'split', 'comparison', 'vs'
        ])
        
        # Determine domain (currently only materials supported)
        domain = 'materials'
        
        # Build output path
        output_path = self._build_output_path(
            domain=domain,
            material_name=material_name,
            image_type=image_type,
            contaminant_id=contaminant_id
        )
        
        return ImageRequest(
            material_name=material_name,
            image_type=image_type,
            domain=domain,
            output_path=output_path,
            category=category,
            contaminant_id=contaminant_id,
            has_split=has_split
        )
    
    def _detect_image_type(self, request: str) -> str:
        """
        Detect image type from request.
        
        Priority: hero > micro > contamination > default (hero)
        """
        if 'micro' in request or 'microscop' in request or '500x' in request:
            return 'micro'
        elif 'hero' in request or 'main' in request or 'primary' in request:
            return 'hero'
        elif any(term in request for term in ['contamination', 'contaminant', 'before', 'after', 'split']):
            return 'contamination'
        else:
            # Default to hero for simple requests like "Make me a Bismuth image"
            return 'hero'
    
    def _detect_contaminant(self, request: str) -> Optional[str]:
        """
        Detect contamination pattern from request.
        
        Checks against contamination_patterns in Contaminants.yaml
        """
        patterns = self.contaminants_data.get('contamination_patterns', {})
        
        for pattern_id, pattern_data in patterns.items():
            pattern_name = pattern_data.get('name', '').lower()
            
            # Check for pattern ID (e.g., 'rust', 'oil', 'oxide')
            if pattern_id.replace('-', ' ') in request:
                return pattern_id
            
            # Check for pattern name (e.g., 'iron oxide', 'oil grease')
            if pattern_name in request:
                return pattern_id
            
            # Check for key terms (e.g., 'rust' matches 'rust-oxidation')
            key_terms = pattern_id.split('-')
            if any(term in request for term in key_terms):
                return pattern_id
        
        # If contamination mentioned but no specific pattern, return generic
        if any(term in request for term in ['contamination', 'contaminant', 'dirty', 'fouling']):
            return 'generic-contamination'
        
        return None
    
    def _build_output_path(
        self,
        domain: str,
        material_name: str,
        image_type: str,
        contaminant_id: Optional[str]
    ) -> Path:
        """
        Build output file path based on domain and image type.
        
        Materials domain:
            Hero: /images/materials/bismuth-laser-cleaning.png
            Micro: /images/materials/bismuth-laser-cleaning-micro.png
            Contamination: /images/materials/bismuth-oil-contamination.png
        
        Contaminants domain:
            /images/contaminants/rust-oxidation/steel-rust-before-after.png
        
        Regions domain:
            /images/regions/san-francisco/historical.png
        """
        # Normalize material name for filename
        material_slug = material_name.lower().replace(' ', '-').replace('(', '').replace(')', '')
        
        if domain == 'materials':
            if image_type == 'hero':
                filename = f"{material_slug}-laser-cleaning.png"
            elif image_type == 'micro':
                filename = f"{material_slug}-laser-cleaning-micro.png"
            elif image_type == 'contamination' and contaminant_id:
                contaminant_slug = contaminant_id.replace('_', '-')
                filename = f"{material_slug}-{contaminant_slug}-before-after.png"
            else:
                filename = f"{material_slug}-laser-cleaning.png"
            
            return self.materials_path / filename
        
        elif domain == 'contaminants':
            contaminant_slug = contaminant_id.replace('_', '-') if contaminant_id else 'contamination'
            filename = f"{material_slug}-{contaminant_slug}-before-after.png"
            return self.contaminants_path / contaminant_slug / filename
        
        elif domain == 'regions':
            # Regions use different structure (city/historical.png)
            region_slug = material_name.lower().replace(' ', '-')
            return self.regions_path / region_slug / "historical.png"
        
        else:
            raise ValueError(f"Unknown domain: {domain}")
    
    def get_material_properties(self, material_name: str) -> Optional[Dict]:
        """
        Get material properties from Materials.yaml.
        
        Args:
            material_name: Name of material (e.g., "Bismuth", "Aluminum")
            
        Returns:
            Dictionary with material properties or None if not found
        """
        # Materials are stored under their name as keys
        materials = self.materials_data.get('materials', {})
        return materials.get(material_name)
    
    def validate_material_contaminant(
        self,
        material_name: str,
        contaminant_id: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate material-contaminant combination.
        
        Args:
            material_name: Material name
            contaminant_id: Contamination pattern ID
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        patterns = self.contaminants_data.get('contamination_patterns', {})
        pattern_data = patterns.get(contaminant_id)
        
        if not pattern_data:
            return False, [f"Contamination pattern '{contaminant_id}' not found"]
        
        # Check prohibited materials
        prohibited = pattern_data.get('prohibited_materials', [])
        if material_name in prohibited:
            return False, [
                f"❌ {contaminant_id} cannot occur on {material_name}",
                f"   Prohibited materials: {', '.join(prohibited)}"
            ]
        
        # Check valid materials (if specified)
        valid_materials = pattern_data.get('valid_materials', [])
        if valid_materials and material_name not in valid_materials:
            return False, [
                f"⚠️  {contaminant_id} is uncommon on {material_name}",
                f"   Typically valid for: {', '.join(valid_materials)}"
            ]
        
        return True, []
    
    def generate(
        self,
        request: str,
        dry_run: bool = False,
        validate_only: bool = False
    ) -> Dict:
        """
        Generate image from natural language request.
        
        Args:
            request: Natural language request (e.g., "Make me a Bismuth Hero image")
            dry_run: If True, only show what would be generated (don't call API)
            validate_only: If True, only validate the prompt (don't generate image)
            
        Returns:
            Dictionary with generation results:
            {
                'success': bool,
                'request': ImageRequest,
                'prompt': str,
                'validation': ValidationResult,
                'output_path': Path,
                'image_data': bytes (if generated)
            }
        """
        print(f"\n{'='*80}")
        print(f"📸 IMAGE GENERATION REQUEST")
        print(f"{'='*80}")
        print(f"Request: {request}")
        
        # Parse request
        try:
            parsed = self.parse_request(request)
        except ValueError as e:
            print(f"\n❌ Parsing failed: {e}")
            return {'success': False, 'error': str(e)}
        
        print(f"\n✅ Parsed Request:")
        print(f"   • Material: {parsed.material_name}")
        print(f"   • Category: {parsed.category}")
        print(f"   • Image Type: {parsed.image_type}")
        print(f"   • Domain: {parsed.domain}")
        print(f"   • Output: {parsed.output_path}")
        if parsed.contaminant_id:
            print(f"   • Contaminant: {parsed.contaminant_id}")
        if parsed.has_split:
            print(f"   • Split: Before/After")
        
        # Validate material-contaminant combination
        if parsed.contaminant_id:
            is_valid, errors = self.validate_material_contaminant(
                parsed.material_name, parsed.contaminant_id
            )
            if not is_valid:
                print(f"\n❌ Material-Contaminant Validation Failed:")
                for error in errors:
                    print(f"   {error}")
                return {
                    'success': False,
                    'request': parsed,
                    'error': 'Invalid material-contaminant combination',
                    'validation_errors': errors
                }
        
        # Get material properties
        material_props = self.get_material_properties(parsed.material_name)
        
        # Create configuration
        config = MaterialImageConfig(
            category=parsed.category,
            contamination_uniformity=3,  # Moderate diversity
            view_mode="Contextual",  # 3D perspective
            guidance_scale=15.0
        )
        
        # Generate prompt
        try:
            prompt_package = self.generator.generate_complete(
                material_name=parsed.material_name,
                material_properties=material_props,
                config=config
            )
            prompt = prompt_package['prompt']
            negative_prompt = prompt_package['negative_prompt']
            
            print(f"\n✅ Prompt Generated ({len(prompt)} chars)")
            
        except Exception as e:
            print(f"\n❌ Prompt generation failed: {e}")
            return {
                'success': False,
                'request': parsed,
                'error': str(e)
            }
        
        # Validate prompt with payload validator
        print(f"\n🔍 Validating prompt...")
        validation_result = self.validator.validate(
            prompt=prompt,
            material=parsed.material_name,
            contaminant=parsed.contaminant_id
        )
        
        if validation_result.has_critical_issues:
            print(f"\n❌ Validation FAILED (critical issues):")
            print(validation_result.format_report())
            return {
                'success': False,
                'request': parsed,
                'prompt': prompt,
                'validation': validation_result,
                'error': 'Prompt validation failed critically'
            }
        
        if validation_result.has_errors or validation_result.has_warnings:
            print(f"\n⚠️  Validation warnings:")
            print(validation_result.format_report())
        else:
            print(f"   ✅ Prompt validated successfully")
        
        # Stop here if validate_only
        if validate_only:
            print(f"\n✅ Validation complete (validate_only=True)")
            return {
                'success': True,
                'request': parsed,
                'prompt': prompt,
                'negative_prompt': negative_prompt,
                'validation': validation_result,
                'output_path': parsed.output_path
            }
        
        # Stop here if dry_run
        if dry_run:
            print(f"\n✅ Dry run complete (no image generated)")
            print(f"\n📝 PROMPT PREVIEW:")
            print(f"{'─'*80}")
            print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
            print(f"{'─'*80}")
            return {
                'success': True,
                'request': parsed,
                'prompt': prompt,
                'negative_prompt': negative_prompt,
                'validation': validation_result,
                'output_path': parsed.output_path
            }
        
        # Generate image
        if not self.image_client:
            print(f"\n⚠️  No Gemini API key provided - cannot generate image")
            return {
                'success': False,
                'request': parsed,
                'prompt': prompt,
                'validation': validation_result,
                'error': 'No Gemini API key configured'
            }
        
        print(f"\n🎨 Generating image...")
        try:
            image_data = self.image_client.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                aspect_ratio="16:9",
                output_mime_type="image/png"
            )
            
            # Save image
            parsed.output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(parsed.output_path, 'wb') as f:
                f.write(image_data)
            
            print(f"\n✅ Image generated successfully!")
            print(f"   💾 Saved to: {parsed.output_path}")
            
            return {
                'success': True,
                'request': parsed,
                'prompt': prompt,
                'negative_prompt': negative_prompt,
                'validation': validation_result,
                'output_path': parsed.output_path,
                'image_data': image_data
            }
            
        except Exception as e:
            print(f"\n❌ Image generation failed: {e}")
            return {
                'success': False,
                'request': parsed,
                'prompt': prompt,
                'validation': validation_result,
                'error': str(e)
            }
    
    def show_material_info(self, material_name: str):
        """
        Display information about a material.
        
        Args:
            material_name: Name of material
        """
        material_index = self.materials_data.get('material_index', {})
        
        if material_name not in material_index:
            print(f"❌ Material '{material_name}' not found")
            print(f"\nAvailable materials: {', '.join(list(material_index.keys())[:20])}...")
            return
        
        category = material_index[material_name]
        props = self.get_material_properties(material_name)
        
        print(f"\n{'='*80}")
        print(f"📊 MATERIAL INFO: {material_name}")
        print(f"{'='*80}")
        print(f"Category: {category}")
        
        if props:
            print(f"\n Properties available: {len(props)} entries")
            # Show sample properties
            for key in list(props.keys())[:5]:
                print(f"   • {key}")
        
        # Show compatible contaminants
        print(f"\n🔬 Compatible Contamination Patterns:")
        patterns = self.contaminants_data.get('contamination_patterns', {})
        compatible = []
        
        for pattern_id, pattern_data in patterns.items():
            prohibited = pattern_data.get('prohibited_materials', [])
            if material_name not in prohibited:
                pattern_name = pattern_data.get('name', pattern_id)
                compatible.append(f"{pattern_id} ({pattern_name})")
        
        for pattern in compatible[:10]:
            print(f"   ✅ {pattern}")
        
        if len(compatible) > 10:
            print(f"   ... and {len(compatible) - 10} more")
    
    def list_materials(self, category: Optional[str] = None):
        """
        List all materials, optionally filtered by category.
        
        Args:
            category: Optional category filter (metal, ceramic, wood, etc.)
        """
        material_index = self.materials_data.get('material_index', {})
        
        if category:
            materials = {k: v for k, v in material_index.items() if v == category}
            print(f"\n📊 Materials in category '{category}': {len(materials)}")
        else:
            materials = material_index
            print(f"\n📊 All Materials: {len(materials)}")
        
        # Group by category
        by_category = {}
        for mat, cat in materials.items():
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(mat)
        
        for cat in sorted(by_category.keys()):
            mats = sorted(by_category[cat])
            print(f"\n{cat.upper()} ({len(mats)} materials):")
            for mat in mats[:10]:
                print(f"   • {mat}")
            if len(mats) > 10:
                print(f"   ... and {len(mats) - 10} more")


def main():
    """CLI interface for image generation handler"""
    import sys
    import os
    
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    
    handler = ImageGenerationHandler(gemini_api_key=api_key)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python image_generation_handler.py 'Make me a Bismuth Hero image'")
        print("  python image_generation_handler.py --info Aluminum")
        print("  python image_generation_handler.py --list-materials")
        print("  python image_generation_handler.py --list-materials metal")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == '--info' and len(sys.argv) > 2:
        handler.show_material_info(sys.argv[2])
    elif command == '--list-materials':
        category = sys.argv[2] if len(sys.argv) > 2 else None
        handler.list_materials(category)
    else:
        # Generate image
        result = handler.generate(command, dry_run=not api_key, validate_only=False)
        
        if result['success']:
            print(f"\n✅ SUCCESS")
        else:
            print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")


if __name__ == '__main__':
    main()
