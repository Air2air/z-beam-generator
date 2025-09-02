#!/usr/bin/env python3
"""
Component Architecture Test Suite

Evaluates each component's test architecture end-to-end for:
- Coverage completeness
- Result accuracy  
- Dynamic schema matching
- Example validation
- Component validation workflows

This systematically tests each of the 11 components individually.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

@dataclass
class ComponentTestResult:
    """Result of testing a single component"""
    component_name: str
    schema_coverage: float  # 0.0 - 1.0
    example_validation: float  # 0.0 - 1.0  
    dynamic_matching: float  # 0.0 - 1.0
    generation_accuracy: float  # 0.0 - 1.0
    validation_workflow: float  # 0.0 - 1.0
    overall_score: float  # 0.0 - 1.0
    issues: List[str]
    recommendations: List[str]

class ComponentArchitectureEvaluator:
    """Evaluates component test architecture systematically"""
    
    def __init__(self):
        self.components_dir = Path("components")
        self.test_materials = ["Copper", "Steel", "Aluminum"]  # Representative test materials
        self.component_list = [
            "frontmatter", "content", "author", "bullets", "caption", "table",
            "tags", "metatags", "jsonld", "propertiestable", "badgesymbol"
        ]
        
    def evaluate_all_components(self) -> Dict[str, ComponentTestResult]:
        """Evaluate all components and return comprehensive results"""
        print("🔍 COMPONENT ARCHITECTURE EVALUATION")
        print("=" * 60)
        print("Testing each component for coverage, accuracy, and validation...")
        print()
        
        results = {}
        for component in self.component_list:
            print(f"📦 Evaluating {component}...")
            result = self.evaluate_component(component)
            results[component] = result
            self._print_component_summary(result)
            print()
            
        return results
    
    def evaluate_component(self, component_name: str) -> ComponentTestResult:
        """Evaluate a single component's test architecture"""
        issues = []
        recommendations = []
        
        # 1. Schema Coverage Analysis
        schema_coverage = self._test_schema_coverage(component_name, issues, recommendations)
        
        # 2. Example Validation Testing
        example_validation = self._test_example_validation(component_name, issues, recommendations)
        
        # 3. Dynamic Schema Matching
        dynamic_matching = self._test_dynamic_matching(component_name, issues, recommendations)
        
        # 4. Generation Accuracy Testing
        generation_accuracy = self._test_generation_accuracy(component_name, issues, recommendations)
        
        # 5. Validation Workflow Integration
        validation_workflow = self._test_validation_workflow(component_name, issues, recommendations)
        
        # Calculate overall score
        scores = [schema_coverage, example_validation, dynamic_matching, generation_accuracy, validation_workflow]
        overall_score = sum(scores) / len(scores)
        
        return ComponentTestResult(
            component_name=component_name,
            schema_coverage=schema_coverage,
            example_validation=example_validation, 
            dynamic_matching=dynamic_matching,
            generation_accuracy=generation_accuracy,
            validation_workflow=validation_workflow,
            overall_score=overall_score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _test_schema_coverage(self, component: str, issues: List[str], recommendations: List[str]) -> float:
        """Test how well component integrates with dynamic schema system"""
        score = 0.0
        
        try:
            # Check if component directory exists
            component_dir = self.components_dir / component
            if not component_dir.exists():
                issues.append(f"Component directory missing: {component_dir}")
                return 0.0
            
            # Check for generator.py
            generator_file = component_dir / "generator.py"
            if generator_file.exists():
                score += 0.3
                
                # Check if generator imports schema system
                with open(generator_file, 'r') as f:
                    content = f.read()
                    if 'schema' in content.lower():
                        score += 0.2
                    if 'dynamic' in content.lower():
                        score += 0.2
                        
            else:
                issues.append(f"Generator file missing: {generator_file}")
                recommendations.append(f"Create {component}/generator.py with schema integration")
            
            # Check for prompt.yaml with schema field references
            prompt_file = component_dir / "prompt.yaml"
            if prompt_file.exists():
                score += 0.2
                
                with open(prompt_file, 'r') as f:
                    content = f.read()
                    if '{schema_' in content:
                        score += 0.1
                        
            else:
                issues.append(f"Prompt template missing: {prompt_file}")
                recommendations.append(f"Create {component}/prompt.yaml with schema field placeholders")
                
        except Exception as e:
            issues.append(f"Schema coverage test failed: {e}")
            
        return min(score, 1.0)
    
    def _test_example_validation(self, component: str, issues: List[str], recommendations: List[str]) -> float:
        """Test component example files for correctness and validation"""
        score = 0.0
        
        try:
            component_dir = self.components_dir / component
            example_files = list(component_dir.glob("example_*.md"))
            
            if not example_files:
                issues.append(f"No example files found in {component}/")
                recommendations.append(f"Create example files: {component}/example_copper.md, etc.")
                return 0.0
                
            score += 0.4  # Points for having examples
            
            valid_examples = 0
            total_examples = len(example_files)
            
            for example_file in example_files:
                try:
                    with open(example_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Basic validation checks
                    if content.strip():
                        valid_examples += 1
                        
                    # Component-specific validation
                    if component == "frontmatter":
                        if content.startswith("---") and "---" in content[4:]:
                            score += 0.1
                        else:
                            issues.append(f"Invalid YAML frontmatter in {example_file.name}")
                            
                except Exception as e:
                    issues.append(f"Failed to validate {example_file.name}: {e}")
            
            # Score based on valid examples ratio
            if total_examples > 0:
                score += 0.6 * (valid_examples / total_examples)
                
        except Exception as e:
            issues.append(f"Example validation test failed: {e}")
            
        return min(score, 1.0)
    
    def _test_dynamic_matching(self, component: str, issues: List[str], recommendations: List[str]) -> float:
        """Test dynamic schema field matching and integration"""
        score = 0.0
        
        try:
            # Test if component can be created by factory
            from generators.component_generators import ComponentGeneratorFactory
            generator = ComponentGeneratorFactory.create_generator(component)
            
            if generator:
                score += 0.5
                
                # Test schema fields integration
                try:
                    from generators.dynamic_generator import DynamicGenerator
                    
                    # Fail fast - no mock clients allowed
                    raise RuntimeError("Test requires real API client - no mock fallbacks")
                    dyn_gen = DynamicGenerator(api_client=mock_client)
                    
                    # Get schema fields for material type
                    schema_fields = dyn_gen.schema_manager.get_dynamic_fields('material')
                    
                    if schema_fields:
                        score += 0.3
                        
                        # Test if component generator can handle schema fields
                        if hasattr(generator, 'generate'):
                            material_data = {'name': 'TestMaterial', 'category': 'metal', 'article_type': 'material'}
                            try:
                                result = generator.generate(
                                    material_name='TestMaterial',
                                    material_data=material_data,
                                    api_client=mock_client,
                                    schema_fields=schema_fields
                                )
                                if result.success:
                                    score += 0.2
                                else:
                                    issues.append(f"Generator failed with schema fields: {result.error_message}")
                            except Exception as e:
                                issues.append(f"Schema field integration failed: {e}")
                        
                except Exception as e:
                    issues.append(f"Dynamic schema integration test failed: {e}")
                    
            else:
                issues.append(f"Component generator not found in factory: {component}")
                recommendations.append(f"Add {component} generator to ComponentGeneratorFactory")
                
        except Exception as e:
            issues.append(f"Dynamic matching test failed: {e}")
            
        return min(score, 1.0)
    
    def _test_generation_accuracy(self, component: str, issues: List[str], recommendations: List[str]) -> float:
        """Test actual content generation accuracy and quality"""
        score = 0.0
        
        try:
            from generators.dynamic_generator import DynamicGenerator
            
            # Fail fast - no mock clients for real integration testing
            raise RuntimeError("Integration test requires real API client - no mocks allowed")
            
            successful_generations = 0
            total_tests = len(self.test_materials)
            
            for material in self.test_materials:
                try:
                    result = generator.generate_component(material, component)
                    
                    if result.success and result.content:
                        successful_generations += 1
                        
                        # Quality checks
                        content_length = len(result.content)
                        if content_length > 50:  # Minimum reasonable content length
                            score += 0.1
                            
                        # Component-specific quality checks
                        if component == "frontmatter":
                            if "---" in result.content and "title:" in result.content:
                                score += 0.1
                        elif component == "content":
                            if len(result.content) > 500:  # Substantial content
                                score += 0.1
                                
                    else:
                        issues.append(f"Generation failed for {material}: {result.error_message}")
                        
                except Exception as e:
                    issues.append(f"Generation test failed for {material}: {e}")
            
            # Base score from success rate
            if total_tests > 0:
                success_rate = successful_generations / total_tests
                score += 0.6 * success_rate
                
        except Exception as e:
            issues.append(f"Generation accuracy test failed: {e}")
            
        return min(score, 1.0)
    
    def _test_validation_workflow(self, component: str, issues: List[str], recommendations: List[str]) -> float:
        """Test component validation and post-processing workflows"""
        score = 0.0
        
        try:
            component_dir = self.components_dir / component
            
            # Check for validator.py
            validator_file = component_dir / "validator.py"
            if validator_file.exists():
                score += 0.3
                
                # Check if validator has required methods
                try:
                    with open(validator_file, 'r') as f:
                        content = f.read()
                        if 'validate' in content:
                            score += 0.2
                        if 'post_process' in content:
                            score += 0.2
                except Exception as e:
                    issues.append(f"Failed to analyze validator: {e}")
                    
            else:
                issues.append(f"Validator missing: {validator_file}")
                recommendations.append(f"Create {component}/validator.py with validation methods")
            
            # Check for post_processor.py
            processor_file = component_dir / "post_processor.py"
            if processor_file.exists():
                score += 0.2
                
            # Test validator integration with centralized system
            try:
                from validators.centralized_validator import CentralizedValidator
                validator = CentralizedValidator()
                
                # Test if component is registered
                if hasattr(validator, f'validate_{component}'):
                    score += 0.1
                    
            except Exception as e:
                issues.append(f"Centralized validator integration failed: {e}")
                
        except Exception as e:
            issues.append(f"Validation workflow test failed: {e}")
            
        return min(score, 1.0)
    
    def _print_component_summary(self, result: ComponentTestResult):
        """Print a summary of component test results"""
        status = "✅" if result.overall_score >= 0.8 else "⚠️" if result.overall_score >= 0.6 else "❌"
        
        print(f"   {status} {result.component_name}: {result.overall_score:.2f}")
        print(f"      Schema Coverage: {result.schema_coverage:.2f}")
        print(f"      Example Validation: {result.example_validation:.2f}")
        print(f"      Dynamic Matching: {result.dynamic_matching:.2f}")
        print(f"      Generation Accuracy: {result.generation_accuracy:.2f}")
        print(f"      Validation Workflow: {result.validation_workflow:.2f}")
        
        if result.issues:
            print(f"      Issues: {len(result.issues)}")
            for issue in result.issues[:2]:  # Show first 2 issues
                print(f"        • {issue}")
            if len(result.issues) > 2:
                print(f"        • ... and {len(result.issues) - 2} more")

def main():
    """Run comprehensive component architecture evaluation"""
    evaluator = ComponentArchitectureEvaluator()
    results = evaluator.evaluate_all_components()
    
    # Summary report
    print("\n📊 COMPONENT ARCHITECTURE SUMMARY")
    print("=" * 60)
    
    total_score = sum(r.overall_score for r in results.values()) / len(results)
    passing_components = sum(1 for r in results.values() if r.overall_score >= 0.8)
    warning_components = sum(1 for r in results.values() if 0.6 <= r.overall_score < 0.8)
    failing_components = sum(1 for r in results.values() if r.overall_score < 0.6)
    
    print(f"Overall Architecture Score: {total_score:.2f}")
    print(f"✅ Passing Components: {passing_components}/{len(results)}")
    print(f"⚠️  Warning Components: {warning_components}/{len(results)}")
    print(f"❌ Failing Components: {failing_components}/{len(results)}")
    
    # Detailed recommendations
    print("\n🔧 PRIORITY RECOMMENDATIONS:")
    for component, result in results.items():
        if result.overall_score < 0.8 and result.recommendations:
            print(f"\n{component}:")
            for rec in result.recommendations[:3]:
                print(f"  • {rec}")
    
    # Save detailed results
    results_file = Path("component_architecture_results.json")
    with open(results_file, 'w') as results_f:
        json.dump({
            name: {
                'component_name': r.component_name,
                'schema_coverage': r.schema_coverage,
                'example_validation': r.example_validation,
                'dynamic_matching': r.dynamic_matching,
                'generation_accuracy': r.generation_accuracy,
                'validation_workflow': r.validation_workflow,
                'overall_score': r.overall_score,
                'issues': r.issues,
                'recommendations': r.recommendations
            }
            for name, r in results.items()
        }, results_f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    return total_score >= 0.8

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
