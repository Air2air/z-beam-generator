"""
Batch Component Generator - Meet Winston Minimums Efficiently

Generates multiple materials' components in batches to meet Winston's 300-character
minimum requirement while reducing API costs and maintaining quality.

ARCHITECTURE:
- Batch generation for short components (material descriptions)
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
from typing import Any, Dict, List, Optional

from generation.config.config_loader import ProcessingConfig
from shared.utils.yaml_utils import load_yaml, save_yaml
from shared.text.validation.constants import ValidationConstants

logger = logging.getLogger(__name__)


class BatchGenerator:
    """
    Generate multiple materials' components in batches to meet Winston minimums.
    
    Optimized for short components like material descriptions that don't individually
    meet Winston's 300-character requirement.
    """
    
    # Component batch configuration
    BATCH_CONFIG = {
        'description': {
            'eligible': True,            # ✅ ENABLED - batches 3 materials to meet Winston 300-char min
            'chars_per_component': 140,  # Actual average (was 175 estimate)
            'min_batch_size': 3,         # Minimum 3 material descriptions = 420+ chars (was 2)
            'max_batch_size': 4,         # Maximum 4 material descriptions = 560+ chars (was 3)
            'winston_min_chars': 300,
            'separator': '\n\n',         # Clear separation for Winston sentence analysis
        },
        'micro': {
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
        self.config = ProcessingConfig()
        self.batch_tokens_per_material = int(
            self.config.get_required_config('constants.batch_generator.tokens_per_material')
        )

    def _get_batch_config(self, component_type: str) -> Dict[str, Any]:
        if component_type not in self.BATCH_CONFIG:
            raise KeyError(f"No batch config defined for component_type='{component_type}'")

        config = self.BATCH_CONFIG[component_type]
        required_keys = [
            'eligible',
            'chars_per_component',
            'min_batch_size',
            'max_batch_size',
            'winston_min_chars',
        ]
        missing = [key for key in required_keys if key not in config]
        if missing:
            raise KeyError(
                f"Batch config for '{component_type}' missing required keys: {', '.join(missing)}"
            )
        return config
        
    def is_batch_eligible(self, component_type: str) -> bool:
        """
        Check if component type is eligible for batch generation.
        
        Args:
            component_type: Type of component (micro, description, etc.)
            
        Returns:
            True if component should use batch generation
        """
        config = self._get_batch_config(component_type)
        return config['eligible']
    
    def calculate_batch_size(self, component_type: str, total_materials: int) -> int:
        """
        Calculate optimal batch size to meet Winston minimum.
        
        Args:
            component_type: Type of component
            total_materials: Total number of materials to generate
            
        Returns:
            Optimal batch size (number of materials per batch)
        """
        config = self._get_batch_config(component_type)
        chars_per = config['chars_per_component']
        winston_min = config['winston_min_chars']
        min_size = config['min_batch_size']
        max_size = config['max_batch_size']
        
        # Calculate minimum batch size to meet Winston requirement
        required_size = max(min_size, int(winston_min / chars_per) + 1)
        
        # Cap at maximum batch size for quality control
        optimal_size = min(required_size, max_size)
        
        self.logger.info(f"📊 Batch configuration for {component_type}:")
        self.logger.info(f"   • Est. chars per component: {chars_per}")
        self.logger.info(f"   • Winston minimum: {winston_min} chars")
        self.logger.info(f"   • Optimal batch size: {optimal_size} materials")
        
        return optimal_size
    
    def batch_generate_descriptions(
        self,
        materials: List[str],
        skip_integrity_check: bool = False
    ) -> Dict[str, Any]:
        """
        Generate material descriptions for multiple materials in one batch.
        
        Strategy:
        1. Calculate batch size to exceed 300 chars
        2. Build batch prompt with material markers
        3. Generate all material descriptions in single API call
        4. Validate concatenated result with Winston (meets 300-char minimum)
        5. Extract individual material descriptions using markers
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
        component_type = 'pageDescription'
        batch_size = len(materials)
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"🔄 BATCH GENERATION: {component_type.upper()}")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Materials: {', '.join(materials)}")
        self.logger.info(f"Batch size: {batch_size}")
        
        # Validate batch size
        config = self._get_batch_config(component_type)
        min_size = config['min_batch_size']
        max_size = config['max_batch_size']
        
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
                batch_result = self.batch_generate_descriptions(batch, skip_integrity_check)
                if batch_result['success']:
                    all_results.update(batch_result['results'])
                else:
                    if 'error' not in batch_result:
                        raise KeyError("Batch result missing required key: 'error'")
                    self.logger.error(f"Batch {i//max_size + 1} failed: {batch_result['error']}")
            
            return {
                'success': len(all_results) == len(materials),
                'batch_size': len(materials),
                'results': all_results,
                'split_into_batches': True
            }
        
        # Generate each material description individually (existing generator pattern)
        # Then concatenate for batch Winston validation
        try:
            individual_results = {}
            
            self.logger.info(f"\n📝 Generating {len(materials)} material descriptions individually...")
            
            for material in materials:
                self.logger.info(f"   Generating: {material}")
                
                # Generate using existing generator (quality-gated with auto-retry)
                # Note: Generator may return string (description) or object (micro/faq)
                try:
                    result = self.generator.generate(material, component_type)
                    
                    # Handle string return (description case)
                    if isinstance(result, str):
                        individual_results[material] = {
                            'content': result,
                            'success': True
                        }
                        self.logger.info(f"   ✅ Generated {len(result)} chars")
                    # Handle GenerationResult object (micro/faq case)
                    elif hasattr(result, 'success') and result.success and result.content:
                        individual_results[material] = {
                            'content': result.content,
                            'success': True
                        }
                        self.logger.info(f"   ✅ Generated {len(result.content)} chars")
                    else:
                        raise ValueError("Generation returned invalid result")
                        
                except Exception as e:
                    individual_results[material] = {
                        'content': '',
                        'success': False,
                        'error': str(e)
                    }
                    self.logger.error(f"   ❌ Generation failed: {e}")
            
            # Concatenate all generated content for Winston validation
            if 'separator' not in config:
                raise KeyError("Batch config missing required key: 'separator'")
            separator = config['separator']

            concatenated_text = separator.join([
                result['content'] for result in individual_results.values() 
                if 'content' in result and result['content']
            ])
            
            self.logger.info(f"\n📏 Batch statistics:")
            self.logger.info(f"   • Generated: {len(individual_results)}/{len(materials)} materials")
            self.logger.info(f"   • Concatenated length: {len(concatenated_text)} chars")
            self.logger.info(f"   • Winston minimum: {config['winston_min_chars']} chars")
            
            # Conditionally validate with Winston based on skip_integrity_check flag
            if not skip_integrity_check:
                # Validate concatenated text with Winston
                winston_result = self._validate_batch_with_winston(
                    concatenated_text,
                    component_type,
                    materials
                )
                
                # Determine if batch passes Winston threshold
                if 'ai_score' not in winston_result:
                    raise KeyError("Winston validation result missing required key: 'ai_score'")
                ai_score = winston_result['ai_score']
                if ai_score is None:
                    raise RuntimeError("Winston validation returned no AI score - cannot proceed")
                passes_threshold = ValidationConstants.passes_winston(ai_score)
                
                # Apply Winston result to all materials in batch
                for material in materials:
                    if material in individual_results:
                        individual_results[material].update({
                            'winston_score': ai_score,
                            'human_score': ValidationConstants.ai_to_human_score(ai_score),
                            'passes_winston': passes_threshold,
                            'batch_validated': True
                        })
            else:
                # Skip Winston but mark as validated
                self.logger.warning("⚠️  Winston validation skipped (--skip-integrity-check)")
                for material in materials:
                    if material in individual_results:
                        individual_results[material].update({
                            'winston_score': None,
                            'human_score': None,
                            'passes_winston': True,  # Allow save without Winston
                            'batch_validated': False
                        })
            
            # Save successful components to Materials.yaml
            saved_count = 0
            for material, result in individual_results.items():
                if 'passes_winston' not in result:
                    raise KeyError(f"Result for '{material}' missing required key: 'passes_winston'")
                if 'content' not in result:
                    raise KeyError(f"Result for '{material}' missing required key: 'content'")

                if result['passes_winston'] and result['content']:
                    self._save_component_to_yaml(
                        material,
                        component_type,
                        result['content']
                    )
                    saved_count += 1
                    
                    # Display individual generation report
                    self._display_generation_report(material, component_type, result)
            
            # Calculate cost savings
            individual_cost = batch_size * 0.10  # $0.10 per Winston call
            batch_cost = 0.10 if not skip_integrity_check else 0  # Single Winston call
            cost_savings = individual_cost - batch_cost
            
            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"✅ BATCH COMPLETE")
            self.logger.info(f"{'='*80}")
            self.logger.info(f"Success rate: {saved_count}/{batch_size} materials")
            
            if not skip_integrity_check and 'winston_result' in locals():
                if 'ai_score' not in winston_result:
                    raise KeyError("Winston validation result missing required key: 'ai_score'")
                ai_score = winston_result['ai_score']
                if ai_score is not None:
                    self.logger.info(f"Winston AI Score: {ai_score:.3f} (threshold: {ValidationConstants.WINSTON_AI_THRESHOLD})")
                    self.logger.info(f"Human Score: {ValidationConstants.ai_to_human_score(ai_score):.1f}%")
            
            self.logger.info(f"Concatenated length: {len(concatenated_text)} chars")
            self.logger.info(f"Cost savings: ${cost_savings:.2f}")
            
            # Save batch report to markdown file
            from postprocessing.reports.generation_report_writer import (
                GenerationReportWriter,
            )
            writer = GenerationReportWriter()
            
            # Prepare results list for report
            results_list = []
            for material, result in individual_results.items():
                if 'passes_winston' not in result:
                    raise KeyError(f"Result for '{material}' missing required key: 'passes_winston'")
                if 'content' not in result:
                    raise KeyError(f"Result for '{material}' missing required key: 'content'")
                results_list.append({
                    'material': material,
                    'success': result['passes_winston'],
                    'content': result['content'],
                    'winston_score': result['winston_score'] if 'winston_score' in result else None,
                    'error': result['error'] if 'error' in result else None
                })
            
            # Determine winston_score for summary
            winston_score_value = None
            if not skip_integrity_check:
                if 'winston_result' in locals() and winston_result:
                    if 'ai_score' not in winston_result:
                        raise KeyError("Winston validation result missing required key: 'ai_score'")
                    winston_score_value = winston_result['ai_score']
            
            # Prepare summary for report
            summary = {
                'success_count': saved_count,
                'winston_score': winston_score_value,
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
                'winston_score': winston_score_value,
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
        # Load base prompt template from materials config.yaml
        import yaml
        config_file = Path("domains/materials/config.yaml")
        
        if not config_file.exists():
            raise FileNotFoundError(
                f"Materials config not found: {config_file}"
            )
        
        config_data = load_yaml(config_file)
        
        if not isinstance(config_data, dict):
            raise TypeError("domains/materials/config.yaml must parse to a dictionary")
        if 'prompts' not in config_data:
            raise KeyError("domains/materials/config.yaml missing required key: 'prompts'")
        prompts = config_data['prompts']
        if not isinstance(prompts, dict):
            raise TypeError("domains/materials/config.yaml key 'prompts' must be a dictionary")
        if component_type not in prompts:
            raise KeyError(f"Prompt 'prompts.{component_type}' not found in materials/config.yaml")
        base_prompt = prompts[component_type]
        
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

        # Fail-fast: Require proper configuration (GROK_INSTRUCTIONS.md Core Principle #3)
        if 'temperature' not in params:
            raise RuntimeError(
                "Missing temperature in batch generation params. "
                "Required: params['temperature']"
            )
        
        if 'api_penalties' not in params:
            raise RuntimeError(
                "Missing API penalties in batch generation config. "
                "Required: params['api_penalties']"
            )
        api_penalties = params['api_penalties']
        if not api_penalties or 'frequency_penalty' not in api_penalties or 'presence_penalty' not in api_penalties:
            raise RuntimeError(
                "Missing API penalties in batch generation config. "
                "Required: frequency_penalty, presence_penalty in params['api_penalties']"
            )
        
        request = GenerationRequest(
            prompt=prompt,
            max_tokens=self.batch_tokens_per_material * len(materials),
            temperature=params['temperature'],
            frequency_penalty=api_penalties['frequency_penalty'],
            presence_penalty=api_penalties['presence_penalty']
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
        self.logger.info("\n🔍 Winston validation:")
        self.logger.info(f"   • Concatenated length: {len(concatenated_text)} chars")
        self.logger.info(f"   • Materials in batch: {len(materials)}")
        
        if len(concatenated_text) < 300:
            self.logger.error(f"❌ Text below Winston minimum: {len(concatenated_text)}/300 chars")
            raise RuntimeError(f"Text too short for Winston validation: {len(concatenated_text)}/300 chars required")
        
        # Create Winston detector for validation
        from postprocessing.detection.ensemble import AIDetectorEnsemble
        from shared.api.client_factory import create_api_client
        
        winston_client = create_api_client('winston')
        detector = AIDetectorEnsemble(winston_client=winston_client)
        
        winston_result = detector.detect(text=concatenated_text)
        
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
        
        data = load_yaml(materials_path)
        
        # Update material's component
        if material_name in data['materials']:
            data['materials'][material_name][component_type] = content
            save_yaml(data, materials_path)
            
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
        if 'content' not in result:
            raise KeyError("Generation report result missing required key: 'content'")
        content = result['content']
        winston_score = result['winston_score'] if 'winston_score' in result else None
        human_score = result['human_score'] if 'human_score' in result else None
        if 'passes_winston' not in result:
            raise KeyError("Generation report result missing required key: 'passes_winston'")
        if 'batch_validated' not in result:
            raise KeyError("Generation report result missing required key: 'batch_validated'")
        passes = result['passes_winston']
        batch_validated = result['batch_validated']
        
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
        
        if winston_score is not None and human_score is not None:
            print(f"   • AI Detection Score: {winston_score:.3f} (threshold: {ValidationConstants.WINSTON_AI_THRESHOLD})")
            print(f"   • Human Score: {human_score:.1f}%")
            print(f"   • Status: {ValidationConstants.get_status_label(passes)}")
            if batch_validated:
                print("   • Validation: Batch Winston validation")
        else:
            print("   • Validation: SKIPPED (--skip-integrity-check)")
            print(f"   • Status: ⚠️  UNVALIDATED")
        print()
        print("📏 STATISTICS:")
        print(f"   • Length: {len(content)} characters")
        print(f"   • Word count: {len(content.split())} words")
        print()
        print("💾 STORAGE:")
        print("   • Location: data/materials/Materials.yaml")
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
        
        data = load_yaml(materials_path)
        
        if not isinstance(data, dict):
            raise TypeError("Materials.yaml must parse to a dictionary")
        if 'materials' not in data:
            raise KeyError("Materials.yaml missing required top-level key: 'materials'")
        materials = data['materials']
        if not isinstance(materials, dict):
            raise TypeError("Materials.yaml key 'materials' must be a dictionary")
        if material_name not in materials:
            raise KeyError(f"Material not found in Materials.yaml: {material_name}")

        return materials[material_name]
