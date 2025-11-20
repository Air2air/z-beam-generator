"""
Batch Component Generator - Meet Winston Minimums Efficiently

Generates multiple materials' components in batches to meet Winston's 300-character
minimum requirement while reducing API costs and maintaining quality.

ARCHITECTURE:
- Batch generation for short components (subtitles)
- Single API call generates multiple materials
- Concatenated validation meets Winston 300-char minimum
- Individual extraction with structured format
- Shared Winston feedback across batch

WORKFLOW:
1. Calculate optimal batch size (target 300+ chars)
2. Generate all components in single API call
3. Validate concatenated result with Winston
4. Extract individual components using markers
5. Apply Winston feedback to all materials in batch
6. Save individual components to Materials.yaml

COST SAVINGS:
- Individual: $0.10 Winston × 132 materials = $13.20
- Batch (4 per): $0.10 Winston × 33 batches = $3.30
- Savings: $9.90 (75% reduction)
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

from generation.validation.constants import ValidationConstants

logger = logging.getLogger(__name__)


class BatchGenerator:
    """
    Generate multiple materials' components in batches to meet Winston minimums.
    
    Optimized for short components like subtitles that don't individually
    meet Winston's 300-character requirement.
    """
    
    # Component batch configuration
    BATCH_CONFIG = {
        'subtitle': {
            'eligible': False,           # Disabled - generates one at a time for length variation
            'chars_per_component': 150,
            'min_batch_size': 1,
            'max_batch_size': 1,
            'winston_min_chars': 300,
        },
        'caption': {
            'eligible': False,           # Already meets minimum individually
            'chars_per_component': 400,
            'min_batch_size': 1,
            'max_batch_size': 1,
            'winston_min_chars': 300,
        },
        'faq': {
            'eligible': False,           # Already meets minimum individually
            'chars_per_component': 800,
            'min_batch_size': 1,
            'max_batch_size': 1,
            'winston_min_chars': 300,
        },
        'description': {
            'eligible': False,           # Already meets minimum individually
            'chars_per_component': 1000,
            'min_batch_size': 1,
            'max_batch_size': 1,
            'winston_min_chars': 300,
        }
    }
    
    def __init__(self, generator):
        """
        Initialize batch generator.
        
        Args:
            generator: Generator instance for individual generation calls
                       (SimpleGenerator or legacy DynamicGenerator)
        """
        self.generator = generator
        self.logger = logging.getLogger(__name__)
        
    def is_batch_eligible(self, component_type: str) -> bool:
        """
        Check if component type is eligible for batch generation.
        
        Args:
            component_type: Type of component (caption, subtitle, etc.)
            
        Returns:
            True if component should use batch generation
        """
        config = self.BATCH_CONFIG.get(component_type, {})
        return config.get('eligible', False)
    
    def calculate_batch_size(self, component_type: str, total_materials: int) -> int:
        """
        Calculate optimal batch size to meet Winston minimum.
        
        Args:
            component_type: Type of component
            total_materials: Total number of materials to generate
            
        Returns:
            Optimal batch size (number of materials per batch)
        """
        config = self.BATCH_CONFIG.get(component_type, {})
        chars_per = config.get('chars_per_component', 200)
        winston_min = config.get('winston_min_chars', 300)
        min_size = config.get('min_batch_size', 2)
        max_size = config.get('max_batch_size', 5)
        
        # Calculate minimum batch size to meet Winston requirement
        required_size = max(min_size, int(winston_min / chars_per) + 1)
        
        # Cap at maximum batch size for quality control
        optimal_size = min(required_size, max_size)
        
        self.logger.info(f"📊 Batch configuration for {component_type}:")
        self.logger.info(f"   • Est. chars per component: {chars_per}")
        self.logger.info(f"   • Winston minimum: {winston_min} chars")
        self.logger.info(f"   • Optimal batch size: {optimal_size} materials")
        
        return optimal_size
    
    def batch_generate_subtitles(
        self,
        materials: List[str],
        skip_integrity_check: bool = False
    ) -> Dict[str, Any]:
        """
        Generate subtitles for multiple materials in one batch.
        
        Strategy:
        1. Calculate batch size to exceed 300 chars
        2. Build batch prompt with material markers
        3. Generate all subtitles in single API call
        4. Validate concatenated result with Winston (meets 300-char minimum)
        5. Extract individual subtitles using markers
        6. Apply same Winston feedback to all materials in batch
        7. Save to Materials.yaml individually
        
        Args:
            materials: List of material names (e.g., ["Aluminum", "Steel", "Copper"])
            skip_integrity_check: Skip integrity validation
            
        Returns:
            {
                'success': bool,
                'batch_size': int,
                'results': {
                    'Aluminum': {'content': '...', 'winston_score': 0.12, 'success': True},
                    'Steel': {'content': '...', 'winston_score': 0.12, 'success': True},
                    'Copper': {'content': '...', 'winston_score': 0.12, 'success': True}
                },
                'winston_score': float,  # Shared across batch
                'concatenated_length': int,
                'cost_savings': float
            }
        """
        component_type = 'subtitle'
        batch_size = len(materials)
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"🔄 BATCH GENERATION: {component_type.upper()}")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Materials: {', '.join(materials)}")
        self.logger.info(f"Batch size: {batch_size}")
        
        # Validate batch size
        config = self.BATCH_CONFIG.get(component_type, {})
        min_size = config.get('min_batch_size', 2)
        max_size = config.get('max_batch_size', 5)
        
        if batch_size < min_size:
            self.logger.warning(f"⚠️  Batch size {batch_size} below minimum {min_size}")
            return {
                'success': False,
                'error': f'Batch size {batch_size} below minimum {min_size}',
                'batch_size': batch_size,
                'results': {}
            }
        
        if batch_size > max_size:
            self.logger.warning(f"⚠️  Batch size {batch_size} exceeds maximum {max_size}")
            self.logger.info(f"Splitting into smaller batches...")
            
            # Split into smaller batches
            all_results = {}
            for i in range(0, len(materials), max_size):
                batch = materials[i:i+max_size]
                batch_result = self.batch_generate_subtitles(batch, skip_integrity_check)
                if batch_result['success']:
                    all_results.update(batch_result['results'])
                else:
                    self.logger.error(f"Batch {i//max_size + 1} failed: {batch_result.get('error')}")
            
            return {
                'success': len(all_results) == len(materials),
                'batch_size': len(materials),
                'results': all_results,
                'split_into_batches': True
            }
        
        # Generate batch prompt
        batch_prompt = self._build_batch_prompt(materials, component_type)
        
        # Generate all subtitles in single API call
        try:
            # Use first material's settings as baseline
            material_data = self._load_material_data(materials[0])
            author_id = material_data.get('author', {}).get('id', 2)
            
            # Get parameters for first material (shared across batch)
            params = self.generator._get_adaptive_parameters(
                materials[0],
                component_type,
                attempt=1,
                last_winston_result=None
            )
            
            self.logger.info(f"\n📝 Generating batch with shared parameters:")
            self.logger.info(f"   • Temperature: {params.get('temperature', 0.9):.3f}")
            self.logger.info(f"   • Author ID: {author_id}")
            
            # Generate content
            response = self._generate_batch_content(
                batch_prompt,
                params,
                materials,
                component_type
            )
            
            # Extract individual components
            individual_results = self._extract_batch_components(
                response,
                materials,
                component_type
            )
            
            # Concatenate for potential Winston validation
            concatenated_text = '\n\n'.join([
                result['content'] for result in individual_results.values()
            ])
            
            # Conditionally validate with Winston based on skip_integrity_check flag
            if skip_integrity_check:
                # Skip Winston validation - mark all as passing
                self.logger.info(f"\n⏭️  Skipping Winston validation (--skip-integrity-check)")
                winston_result = {
                    'ai_score': ValidationConstants.DEFAULT_AI_SCORE,
                    'human_score': ValidationConstants.DEFAULT_HUMAN_SCORE,
                    'skipped': True
                }
                passes_threshold = True  # Auto-pass when skipping
            else:
                # Validate concatenated text with Winston
                winston_result = self._validate_batch_with_winston(
                    concatenated_text,
                    component_type,
                    materials
                )
                
                # Determine if batch passes Winston threshold using centralized constant
                ai_score = winston_result.get('ai_score', ValidationConstants.DEFAULT_FALLBACK_AI_SCORE)
                passes_threshold = ValidationConstants.passes_winston(ai_score)
            
            # Apply Winston result to all materials in batch
            final_ai_score = winston_result.get('ai_score', ValidationConstants.DEFAULT_FALLBACK_AI_SCORE)
            for material in materials:
                individual_results[material].update({
                    'winston_score': final_ai_score,
                    'human_score': ValidationConstants.ai_to_human_score(final_ai_score),
                    'passes_winston': passes_threshold,
                    'batch_validated': True,
                    'validation_skipped': skip_integrity_check
                })
            
            # Save successful components to Materials.yaml and display individual reports
            saved_count = 0
            for material, result in individual_results.items():
                # ALWAYS display generation report (required by Generation Report Policy)
                self._display_generation_report(material, component_type, result)
                
                if result.get('passes_winston', False):
                    self._save_component_to_yaml(
                        material,
                        component_type,
                        result['content']
                    )
                    saved_count += 1
            
            # Calculate cost savings
            individual_cost = batch_size * 0.10  # $0.10 per Winston call
            batch_cost = 0.10  # Single Winston call
            cost_savings = individual_cost - batch_cost
            
            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"✅ BATCH COMPLETE")
            self.logger.info(f"{'='*80}")
            self.logger.info(f"Success rate: {saved_count}/{batch_size} materials")
            self.logger.info(f"Winston AI Score: {winston_result.get('ai_score', ValidationConstants.DEFAULT_FALLBACK_AI_SCORE):.3f} (threshold: {ValidationConstants.WINSTON_AI_THRESHOLD})")
            self.logger.info(f"Human Score: {ValidationConstants.ai_to_human_score(winston_result.get('ai_score', ValidationConstants.DEFAULT_FALLBACK_AI_SCORE)):.1f}%")
            self.logger.info(f"Concatenated length: {len(concatenated_text)} chars")
            self.logger.info(f"Cost savings: ${cost_savings:.2f}")
            
            # Save batch report to markdown file
            from postprocessing.reports.generation_report_writer import GenerationReportWriter
            writer = GenerationReportWriter()
            
            # Prepare results list for report
            results_list = []
            for material, result in individual_results.items():
                results_list.append({
                    'material': material,
                    'success': result.get('passes_winston', False),
                    'content': result.get('content', ''),
                    'winston_score': result.get('winston_score'),
                    'error': result.get('error')
                })
            
            # Prepare summary for report
            summary = {
                'success_count': saved_count,
                'winston_score': winston_result.get('ai_score', ValidationConstants.DEFAULT_FALLBACK_AI_SCORE),
                'concatenated_length': len(concatenated_text),
                'cost_savings': cost_savings
            }
            
            report_path = writer.save_batch_report(
                component_type=component_type,
                materials=materials,
                results=results_list,
                summary=summary
            )
            self.logger.info(f"📄 Batch report saved: {report_path}")
            
            return {
                'success': saved_count == batch_size,
                'batch_size': batch_size,
                'results': individual_results,
                'winston_score': winston_result.get('ai_score', ValidationConstants.DEFAULT_FALLBACK_AI_SCORE),
                'concatenated_length': len(concatenated_text),
                'cost_savings': cost_savings,
                'saved_count': saved_count
            }
            
        except Exception as e:
            self.logger.error(f"❌ Batch generation failed: {e}")
            return {
                'success': False,
                'batch_size': batch_size,
                'error': str(e),
                'results': {}
            }
    
    def _build_batch_prompt(self, materials: List[str], component_type: str) -> str:
        """
        Build prompt for batch generation with material markers.
        
        Args:
            materials: List of material names
            component_type: Type of component
            
        Returns:
            Batch prompt with structured format for extraction
        """
        # Load base prompt template - try multiple locations
        prompt_locations = [
            Path(f"prompts/{component_type}.txt"),
            Path(f"domains/materials/prompts/{component_type}.txt"),
            Path(f"prompts/components/{component_type}.txt")
        ]
        
        prompt_file = None
        for location in prompt_locations:
            if location.exists():
                prompt_file = location
                break
        
        if not prompt_file:
            raise FileNotFoundError(
                f"Prompt template not found for {component_type}. Tried: {', '.join(str(p) for p in prompt_locations)}"
            )
        
        with open(prompt_file, 'r') as f:
            base_prompt = f.read()
        
        # Substitute placeholders in base prompt
        base_prompt = base_prompt.replace('{material}', '[MATERIAL_NAME]')
        base_prompt = base_prompt.replace('{author}', 'a professional technical writer')
        
        # Build batch instructions
        batch_instructions = f"""
BATCH GENERATION TASK:
Generate {component_type}s for {len(materials)} materials in a single response.

MATERIALS:
{chr(10).join([f"{i+1}. {mat}" for i, mat in enumerate(materials)])}

FORMAT (CRITICAL):
Use this exact format with clear material markers:

[MATERIAL: {materials[0]}]
[Your {component_type} content here]
[/MATERIAL: {materials[0]}]

[MATERIAL: {materials[1] if len(materials) > 1 else 'Material2'}]
[Your {component_type} content here]
[/MATERIAL: {materials[1] if len(materials) > 1 else 'Material2'}]

... (continue for all materials)

REQUIREMENTS:
- Follow all style and quality guidelines from base prompt
- Maintain consistency across all {component_type}s in batch
- Use material-specific details (properties, applications, benefits)
- Each {component_type} should stand alone (no cross-references)
- Preserve exact marker format for extraction

BASE PROMPT:
{base_prompt}
"""
        
        return batch_instructions
    
    def _generate_batch_content(
        self,
        prompt: str,
        params: Dict[str, Any],
        materials: List[str],
        component_type: str
    ) -> str:
        """
        Generate batch content using API.
        
        Args:
            prompt: Batch generation prompt
            params: Generation parameters
            materials: List of material names
            component_type: Type of component
            
        Returns:
            Raw API response with all components
        """
        # Use generator's API client with GenerationRequest
        from shared.api.client import GenerationRequest
        
        request = GenerationRequest(
            prompt=prompt,
            max_tokens=500 * len(materials),  # Scale with batch size
            temperature=params.get('temperature', 0.9),
            frequency_penalty=params.get('api_penalties', {}).get('frequency_penalty', 0.0),
            presence_penalty=params.get('api_penalties', {}).get('presence_penalty', 0.0)
        )
        
        api_response = self.generator.api_client.generate(request)
        
        if not api_response.success:
            raise RuntimeError(f"API generation failed: {api_response.error}")
        
        return api_response.content
    
    def _extract_batch_components(
        self,
        response: str,
        materials: List[str],
        component_type: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract individual components from batch response.
        
        Args:
            response: Raw API response
            materials: List of material names
            component_type: Type of component
            
        Returns:
            {
                'Aluminum': {'content': '...', 'success': True},
                'Steel': {'content': '...', 'success': True}
            }
        """
        results = {}
        
        for material in materials:
            # Extract content between markers
            pattern = rf'\[MATERIAL:\s*{re.escape(material)}\s*\](.*?)\[/MATERIAL:\s*{re.escape(material)}\s*\]'
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            
            if match:
                content = match.group(1).strip()
                results[material] = {
                    'content': content,
                    'success': True,
                    'extraction_method': 'marker'
                }
                self.logger.info(f"✅ Extracted {component_type} for {material}: {len(content)} chars")
            else:
                self.logger.warning(f"⚠️  Failed to extract {component_type} for {material}")
                results[material] = {
                    'content': '',
                    'success': False,
                    'error': 'Extraction failed - marker not found'
                }
        
        return results
    
    def _validate_batch_with_winston(
        self,
        concatenated_text: str,
        component_type: str,
        materials: List[str]
    ) -> Dict[str, Any]:
        """
        Validate concatenated batch text with Winston API.
        
        Args:
            concatenated_text: All components concatenated
            component_type: Type of component
            materials: List of material names
            
        Returns:
            Winston validation result
        """
        self.logger.info(f"\n🔍 Winston validation:")
        self.logger.info(f"   • Concatenated length: {len(concatenated_text)} chars")
        self.logger.info(f"   • Materials in batch: {len(materials)}")
        
        if len(concatenated_text) < 300:
            self.logger.warning(f"⚠️  Text below Winston minimum: {len(concatenated_text)}/300 chars")
            return {
                'success': False,
                'error': 'Text too short for Winston validation',
                'ai_score': ValidationConstants.DEFAULT_FALLBACK_AI_SCORE,
                'skip_reason': 'text_too_short'
            }
        
        # Call Winston API through generator's detector ensemble
        winston_result = self.generator.detector.detect(
            text=concatenated_text
        )
        
        return winston_result
    
    def _save_component_to_yaml(
        self,
        material_name: str,
        component_type: str,
        content: str
    ) -> None:
        """
        Save individual component to Materials.yaml.
        
        Args:
            material_name: Name of material
            component_type: Type of component
            content: Generated content
        """
        materials_path = Path("data/materials/Materials.yaml")
        
        with open(materials_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Update material's component
        if material_name in data['materials']:
            data['materials'][material_name][component_type] = content
            
            with open(materials_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            self.logger.info(f"💾 Saved {component_type} for {material_name}")
        else:
            self.logger.error(f"❌ Material not found: {material_name}")
    
    def _display_generation_report(
        self,
        material_name: str,
        component_type: str,
        result: Dict[str, Any]
    ) -> None:
        """
        Display comprehensive generation report for a single material.
        
        Args:
            material_name: Name of material
            component_type: Type of component
            result: Generation result with content and metrics
        """
        content = result.get('content', '')
        winston_score = result.get('winston_score', ValidationConstants.DEFAULT_FALLBACK_AI_SCORE)
        human_score = result.get('human_score', ValidationConstants.ai_to_human_score(ValidationConstants.DEFAULT_FALLBACK_AI_SCORE))
        passes = result.get('passes_winston', False)
        
        print("\n" + "="*80)
        print(f"📊 GENERATION COMPLETE REPORT: {material_name}")
        print("="*80)
        print()
        print("📝 GENERATED CONTENT:")
        print("─"*80)
        print(content)
        print("─"*80)
        print()
        print("📈 QUALITY METRICS:")
        print(f"   • AI Detection Score: {winston_score:.3f} (threshold: {ValidationConstants.WINSTON_AI_THRESHOLD})")
        print(f"   • Human Score: {human_score:.1f}%")
        print(f"   • Status: {ValidationConstants.get_status_label(passes)}")
        print(f"   • Validation: Batch Winston validation")
        print()
        print("📏 STATISTICS:")
        print(f"   • Length: {len(content)} characters")
        print(f"   • Word count: {len(content.split())} words")
        print()
        print("💾 STORAGE:")
        print(f"   • Location: data/materials/Materials.yaml")
        print(f"   • Component: {component_type}")
        print(f"   • Material: {material_name}")
        print()
        print("="*80)
    
    def _load_material_data(self, material_name: str) -> Dict[str, Any]:
        """
        Load material data from Materials.yaml.
        
        Args:
            material_name: Name of material
            
        Returns:
            Material data dict
        """
        materials_path = Path("data/materials/Materials.yaml")
        
        with open(materials_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return data['materials'].get(material_name, {})
