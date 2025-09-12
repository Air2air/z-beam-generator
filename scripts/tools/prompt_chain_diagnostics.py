#!/usr/bin/env python3
"""
Prompt Chain Architecture Diagnostics Tool
Validates the complete text optimization system and modular component architecture.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import json

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from optimizer.text_optimization.utils.modular_loader import ModularConfigLoader


class PromptChainDiagnostics:
    """Comprehensive diagnostics for the prompt chain architecture."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.issues = []
        self.successes = []
        
    def run_full_diagnostics(self) -> Dict[str, Any]:
        """Run complete diagnostic suite."""
        print("🔍 Z-Beam Prompt Chain Architecture Diagnostics")
        print("=" * 60)
        
        results = {
            "timestamp": self._get_timestamp(),
            "architecture_validation": self._validate_architecture(),
            "modular_components": self._validate_modular_components(),
            "persona_system": self._validate_persona_system(),
            "optimization_config": self._validate_optimization_config(),
            "integration_points": self._validate_integration_points(),
            "prompt_chain_flow": self._validate_prompt_chain_flow(),
            "summary": self._generate_summary()
        }
        
        self._print_summary(results)
        return results
    
    def _validate_architecture(self) -> Dict[str, Any]:
        """Validate the overall architecture structure."""
        print("\n📋 Architecture Validation")
        print("-" * 30)
        
        required_paths = [
            "components/text/prompts/core/ai_detection_core.yaml",
            "optimizer/text_optimization/utils/modular_loader.py",
            "optimizer/text_optimization/ai_detection_prompt_optimizer.py",
            "optimizer/text_optimization/dynamic_prompt_generator.py",
            "optimizer/text_optimization/validation/content_scorer.py"
        ]
        
        architecture_results = {
            "core_files_present": True,
            "missing_files": [],
            "file_sizes": {},
            "config_structure": {}
        }
        
        for path in required_paths:
            full_path = self.project_root / path
            if full_path.exists():
                size = full_path.stat().st_size
                architecture_results["file_sizes"][path] = size
                print(f"✅ {path} ({size:,} bytes)")
                self.successes.append(f"Core file present: {path}")
            else:
                architecture_results["core_files_present"] = False
                architecture_results["missing_files"].append(path)
                print(f"❌ MISSING: {path}")
                self.issues.append(f"Missing core file: {path}")
        
        return architecture_results
    
    def _validate_modular_components(self) -> Dict[str, Any]:
        """Validate modular components system."""
        print("\n🧩 Modular Components Validation")
        print("-" * 35)
        
        try:
            loader = ModularConfigLoader()
            
            # Test modular loading
            config = loader.load_config(use_modular=True)
            component_info = loader.get_component_info()
            
            results = {
                "modular_loading_works": config is not None,
                "component_info": component_info,
                "config_sections": list(config.keys()) if config else [],
                "modular_components_found": component_info.get("total_components", 0),
                "all_components_loaded": True
            }
            
            if config:
                print(f"✅ Modular configuration loaded successfully")
                print(f"   - Total sections: {len(config)}")
                self.successes.append("Modular configuration system working")
            else:
                print(f"❌ Failed to load modular configuration")
                self.issues.append("Modular configuration system failed")
                results["modular_loading_works"] = False
            
            # Check individual components
            if component_info.get("modular"):
                print(f"📊 Component Status:")
                for comp in component_info["components"]:
                    status = "✅" if comp["loaded"] else "❌"
                    print(f"   - {comp['name']}: {status} ({comp['size']} chars)")
                    if not comp["loaded"]:
                        results["all_components_loaded"] = False
                        self.issues.append(f"Component failed to load: {comp['name']}")
                    else:
                        self.successes.append(f"Component loaded: {comp['name']}")
            else:
                print("❌ Modular components system not configured")
                self.issues.append("Modular components system not properly configured")
                results["all_components_loaded"] = False
            
            return results
            
        except Exception as e:
            print(f"❌ Error validating modular components: {e}")
            self.issues.append(f"Modular components validation error: {e}")
            return {
                "modular_loading_works": False,
                "error": str(e),
                "component_info": {},
                "config_sections": [],
                "modular_components_found": 0,
                "all_components_loaded": False
            }
    
    def _validate_persona_system(self) -> Dict[str, Any]:
        """Validate the persona system."""
        print("\n🎭 Persona System Validation")
        print("-" * 30)
        
        persona_paths = [
            "optimizer/text_optimization/prompts/personas/taiwan_persona.yaml",
            "optimizer/text_optimization/prompts/personas/italy_persona.yaml", 
            "optimizer/text_optimization/prompts/personas/indonesia_persona.yaml",
            "optimizer/text_optimization/prompts/personas/usa_persona.yaml"
        ]
        
        formatting_paths = [
            "optimizer/text_optimization/prompts/formatting/taiwan_formatting.yaml",
            "optimizer/text_optimization/prompts/formatting/italy_formatting.yaml",
            "optimizer/text_optimization/prompts/formatting/indonesia_formatting.yaml", 
            "optimizer/text_optimization/prompts/formatting/usa_formatting.yaml"
        ]
        
        results = {
            "personas_present": 0,
            "formatting_present": 0,
            "missing_personas": [],
            "missing_formatting": [],
            "persona_content": {}
        }
        
        # Check personas
        for path in persona_paths:
            full_path = self.project_root / path
            country = path.split('/')[-1].replace('_persona.yaml', '')
            if full_path.exists():
                results["personas_present"] += 1
                print(f"✅ Persona: {country}")
                self.successes.append(f"Persona found: {country}")
                
                # Load content for validation
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        persona_data = yaml.safe_load(f)
                        results["persona_content"][country] = {
                            "sections": list(persona_data.keys()) if persona_data else [],
                            "size": len(str(persona_data)) if persona_data else 0
                        }
                except Exception as e:
                    self.issues.append(f"Error loading persona {country}: {e}")
            else:
                results["missing_personas"].append(country)
                print(f"❌ MISSING: Persona {country}")
                self.issues.append(f"Missing persona: {country}")
        
        # Check formatting
        for path in formatting_paths:
            full_path = self.project_root / path
            country = path.split('/')[-1].replace('_formatting.yaml', '')
            if full_path.exists():
                results["formatting_present"] += 1
                print(f"✅ Formatting: {country}")
                self.successes.append(f"Formatting found: {country}")
            else:
                results["missing_formatting"].append(country)
                print(f"❌ MISSING: Formatting {country}")
                self.issues.append(f"Missing formatting: {country}")
        
        return results
    
    def _validate_optimization_config(self) -> Dict[str, Any]:
        """Validate optimization configuration."""
        print("\n⚙️ Optimization Configuration Validation")
        print("-" * 40)
        
        # Check run.py configuration
        run_config_path = self.project_root / "run.py"
        results = {
            "run_config_present": False,
            "api_providers": {},
            "winston_configured": False,
            "deepseek_configured": False,
            "config_errors": []
        }
        
        if run_config_path.exists():
            results["run_config_present"] = True
            print("✅ run.py configuration file present")
            self.successes.append("Main configuration file present")
            
            try:
                # Read and analyze run.py
                with open(run_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for API provider configurations
                if "API_PROVIDERS" in content:
                    print("✅ API_PROVIDERS configuration found")
                    self.successes.append("API providers configuration present")
                    
                    if "winston" in content.lower():
                        results["winston_configured"] = True
                        print("✅ Winston AI configuration found")
                        self.successes.append("Winston AI configured")
                    else:
                        print("❌ Winston AI configuration missing")
                        self.issues.append("Winston AI not configured")
                    
                    if "deepseek" in content.lower():
                        results["deepseek_configured"] = True
                        print("✅ DeepSeek configuration found")
                        self.successes.append("DeepSeek configured")
                    else:
                        print("❌ DeepSeek configuration missing")
                        self.issues.append("DeepSeek not configured")
                else:
                    print("❌ API_PROVIDERS configuration missing")
                    self.issues.append("API providers not configured")
                    
            except Exception as e:
                results["config_errors"].append(str(e))
                print(f"❌ Error reading run.py: {e}")
                self.issues.append(f"Configuration read error: {e}")
        else:
            print("❌ run.py configuration file missing")
            self.issues.append("Main configuration file missing")
        
        return results
    
    def _validate_integration_points(self) -> Dict[str, Any]:
        """Validate integration points between components."""
        print("\n🔗 Integration Points Validation")
        print("-" * 33)
        
        results = {
            "text_component_integration": False,
            "factory_integration": False,
            "optimization_integration": False,
            "import_paths_valid": True,
            "integration_errors": []
        }
        
        # Check if text component can import optimizer
        try:
            sys.path.insert(0, str(self.project_root))
            from optimizer.text_optimization.ai_detection_prompt_optimizer import AIDetectionPromptOptimizer
            results["optimization_integration"] = True
            print("✅ Optimization module importable")
            self.successes.append("Optimization module integration working")
        except ImportError as e:
            results["optimization_integration"] = False
            results["integration_errors"].append(f"Optimizer import error: {e}")
            print(f"❌ Cannot import optimizer: {e}")
            self.issues.append(f"Optimizer import failed: {e}")
        
        # Check ComponentGeneratorFactory integration
        try:
            from generators.component_generator_factory import ComponentGeneratorFactory
            results["factory_integration"] = True
            print("✅ ComponentGeneratorFactory importable")
            self.successes.append("Factory integration working")
        except ImportError as e:
            results["factory_integration"] = False
            results["integration_errors"].append(f"Factory import error: {e}")
            print(f"❌ Cannot import ComponentGeneratorFactory: {e}")
            self.issues.append(f"Factory import failed: {e}")
        
        return results
    
    def _validate_prompt_chain_flow(self) -> Dict[str, Any]:
        """Validate the 12-step prompt chain flow."""
        print("\n🔄 Prompt Chain Flow Validation")
        print("-" * 33)
        
        results = {
            "chain_steps_validated": 0,
            "chain_complete": False,
            "flow_errors": []
        }
        
        # Test the modular loader can build a complete prompt chain
        try:
            loader = ModularConfigLoader()
            config = loader.load_config(use_modular=True)
            
            if config:
                expected_sections = [
                    "ai_detection_avoidance",
                    "human_writing_characteristics", 
                    "natural_imperfections",
                    "human_authenticity_enhancements",
                    "cognitive_variability",
                    "personal_touch",
                    "conversational_flow",
                    "cultural_humanization"
                ]
                
                present_sections = 0
                for section in expected_sections:
                    if section in config:
                        present_sections += 1
                        print(f"✅ Chain step: {section}")
                        self.successes.append(f"Prompt chain section: {section}")
                    else:
                        print(f"❌ MISSING: {section}")
                        self.issues.append(f"Missing prompt chain section: {section}")
                
                results["chain_steps_validated"] = present_sections
                results["chain_complete"] = present_sections == len(expected_sections)
                
                if results["chain_complete"]:
                    print(f"✅ Complete prompt chain validated ({present_sections}/{len(expected_sections)} sections)")
                    self.successes.append("Complete prompt chain validated")
                else:
                    print(f"❌ Incomplete prompt chain ({present_sections}/{len(expected_sections)} sections)")
                    self.issues.append("Prompt chain incomplete")
            else:
                print("❌ Cannot load configuration for chain validation")
                self.issues.append("Configuration loading failed for chain validation")
                
        except Exception as e:
            results["flow_errors"].append(str(e))
            print(f"❌ Error validating prompt chain: {e}")
            self.issues.append(f"Prompt chain validation error: {e}")
        
        return results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate diagnostic summary."""
        total_checks = len(self.successes) + len(self.issues)
        success_rate = (len(self.successes) / total_checks * 100) if total_checks > 0 else 0
        
        return {
            "total_checks": total_checks,
            "successes": len(self.successes),
            "issues": len(self.issues),
            "success_rate": round(success_rate, 1),
            "status": "HEALTHY" if success_rate >= 80 else "NEEDS_ATTENTION" if success_rate >= 60 else "CRITICAL",
            "top_issues": self.issues[:5],
            "top_successes": self.successes[:5]
        }
    
    def _print_summary(self, results: Dict[str, Any]) -> None:
        """Print diagnostic summary."""
        summary = results["summary"]
        
        print("\n" + "=" * 60)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 60)
        
        status_icon = "🟢" if summary["status"] == "HEALTHY" else "🟡" if summary["status"] == "NEEDS_ATTENTION" else "🔴"
        print(f"{status_icon} Overall Status: {summary['status']}")
        print(f"📈 Success Rate: {summary['success_rate']}% ({summary['successes']}/{summary['total_checks']})")
        
        if summary["issues"] > 0:
            print(f"\n❌ Top Issues ({len(self.issues)} total):")
            for i, issue in enumerate(summary["top_issues"], 1):
                print(f"   {i}. {issue}")
        
        if summary["successes"] > 0:
            print(f"\n✅ Key Successes ({len(self.successes)} total):")
            for i, success in enumerate(summary["top_successes"], 1):
                print(f"   {i}. {success}")
        
        print("\n🔧 Next Steps:")
        if summary["status"] == "CRITICAL":
            print("   - Address critical configuration issues immediately")
            print("   - Verify all required files are present")
            print("   - Check API configurations")
        elif summary["status"] == "NEEDS_ATTENTION":
            print("   - Review and fix identified issues")
            print("   - Test optimization functionality")
            print("   - Validate prompt chain completeness")
        else:
            print("   - System appears healthy")
            print("   - Run optimization tests to verify functionality")
            print("   - Monitor performance metrics")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save_results(self, results: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Save diagnostic results to file."""
        if not output_file:
            timestamp = self._get_timestamp().replace(":", "-").replace(" ", "_")
            output_file = f"prompt_chain_diagnostics_{timestamp}.json"
        
        output_path = self.project_root / "logs" / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_path}")
        return str(output_path)


def main():
    """Main diagnostic function."""
    diagnostics = PromptChainDiagnostics()
    results = diagnostics.run_full_diagnostics()
    
    # Save results
    diagnostics.save_results(results)
    
    # Exit with appropriate code
    summary = results["summary"]
    exit_code = 0 if summary["status"] == "HEALTHY" else 1 if summary["status"] == "NEEDS_ATTENTION" else 2
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
