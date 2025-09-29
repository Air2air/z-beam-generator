#!/usr/bin/env python3
"""
AI Research Logging Demo - Show verbose AI research in action
"""

import time
from hierarchical_validator import HierarchicalValidator
from pipeline_integration import InvisiblePipelineRunner

def demo_verbose_ai_research_logging():
    """Demonstrate verbose AI research logging across the system"""
    
    print("🔬 VERBOSE AI RESEARCH LOGGING DEMONSTRATION")
    print("=" * 60)
    print("This demo shows detailed AI research logging throughout the validation pipeline")
    print()
    
    # Test 1: Hierarchical Validator AI Research Logging
    print("📊 TEST 1: Hierarchical Validator AI Research")
    print("-" * 50)
    
    validator = HierarchicalValidator(ai_validation_enabled=True, silent_mode=False)
    
    print(f"✅ Configuration:")
    print(f"   • AI Verbose Logging: {validator.ai_verbose_logging}")
    print(f"   • AI Log Prompts: {validator.ai_log_prompts}")
    print(f"   • AI Log Timing: {validator.ai_log_timing}")
    print(f"   • AI Research Logger: {validator.ai_research_logger_enabled}")
    print()
    
    # Load actual data and run validation
    try:
        validator_result = validator.run_hierarchical_validation()
        print(f"📊 Hierarchical validation completed")
        print(f"   • AI Validation Status: {validator_result.get('ai_validation_status', 'Unknown')}")
        print()
    except Exception as e:
        print(f"⚠️  Hierarchical validation error: {e}")
        print()
    
    # Test 2: Pipeline Integration AI Research Logging
    print("🔧 TEST 2: Pipeline Integration AI Research")
    print("-" * 50)
    
    pipeline = InvisiblePipelineRunner(silent_mode=False)
    
    print(f"✅ Configuration:")
    print(f"   • AI Verbose Logging: {pipeline.ai_verbose_logging}")
    print(f"   • AI Log Prompts: {pipeline.ai_log_prompts}")
    print(f"   • AI Log Timing: {pipeline.ai_log_timing}")
    print(f"   • AI Research Logger: {pipeline.ai_research_logger_enabled}")
    print()
    
    # Test AI validation of specific material properties
    test_properties = {
        'density': {'value': 2.7, 'unit': 'g/cm³'},
        'thermalConductivity': {'value': 205, 'unit': 'W/m·K'},
        'meltingPoint': {'value': 660, 'unit': '°C'}
    }
    
    try:
        ai_result = pipeline._ai_validate_critical_properties('Aluminum', test_properties)
        print(f"🎯 AI property validation completed")
        print(f"   • Validation Passed: {ai_result.get('validation_passed', False)}")
        print(f"   • Confidence Score: {ai_result.get('confidence_score', 0):.1%}")
        print(f"   • Properties Validated: {len(ai_result.get('ai_responses', {}))}")
        print()
        
        # Show detailed AI responses
        for prop_name, ai_response in ai_result.get('ai_responses', {}).items():
            valid = ai_response.get('valid', True)
            confidence = ai_response.get('confidence', 0)
            reason = ai_response.get('reason', 'No reason provided')
            print(f"   📋 {prop_name}: {'✅ VALID' if valid else '❌ INVALID'} (confidence: {confidence:.1%})")
            print(f"      Reason: {reason}")
        
    except Exception as e:
        print(f"⚠️  Pipeline AI validation error: {e}")
    
    print()
    print("🎉 DEMONSTRATION COMPLETE!")
    print("The verbose AI research logging is now enabled by default and shows:")
    print("   • 🤖 AI research calls and timing")
    print("   • 📝 AI prompts and responses (when enabled)")
    print("   • 🎯 AI confidence scores and validation results")
    print("   • ⚡ Detailed timing information")
    print("   • 📊 Comprehensive validation summaries")

if __name__ == "__main__":
    demo_verbose_ai_research_logging()