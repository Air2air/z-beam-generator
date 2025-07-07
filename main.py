#!/usr/bin/env python3
"""
Simplified Z-Beam Content Generator

Single-file implementation following anti-bloat and anti-hardcoding rules.
All configuration via GlobalConfigManager, no abstractions, maximum simplicity.
"""

import sys
from typing import Optional
from pathlib import Path

def main():
    """Main entry point for content generation."""
    try:
        # Import configuration from run.py - NO FALLBACKS
        from run import USER_CONFIG, PROVIDER_MODELS
        from config.global_config import GlobalConfigManager
        
        # Initialize GlobalConfigManager - SINGLE SOURCE OF TRUTH
        config = GlobalConfigManager.initialize(USER_CONFIG, PROVIDER_MODELS)
        
        print("🚀 Z-Beam Generator - Simplified Architecture")
        print(f"📋 Material: {config.get_material()}")
        print(f"🔧 Provider: {config.get_generator_provider()}")
        print(f"📝 File: {config.get_file_name()}")
        
        # Check PROJECT_GUIDE.md compliance
        if not check_project_guide_compliance():
            print("❌ Compliance check failed - aborting operation")
            sys.exit(1)
        
        # Generate content using simplified approach
        result = generate_content_simple(config)
        
        if result:
            print(f"✅ Content generated successfully: {result}")
        else:
            print("❌ Content generation failed")
            
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        print("NO FALLBACKS - system must fail fast")
        sys.exit(1)

# === PROJECT_GUIDE.md COMPLIANCE CHECK ===
def check_project_guide_compliance():
    """Validate PROJECT_GUIDE.md compliance before any operations."""
    try:
        from audit_violations import ClaudeComplianceValidator
        validator = ClaudeComplianceValidator(".")
        
        print("🔍 Checking PROJECT_GUIDE.md compliance...")
        
        # Validate project guide exists and is compliant
        if not validator.validate_project_guide():
            print("❌ PROJECT_GUIDE.md compliance issues detected:")
            for violation in validator.violations:
                print(f"  {violation}")
            return False
        
        # Validate documentation file count
        if not validator.validate_documentation_count():
            print("❌ Unauthorized documentation files detected:")
            for violation in validator.violations:
                print(f"  {violation}")
            return False
        
        print("✅ PROJECT_GUIDE.md compliance verified")
        return True
        
    except Exception as e:
        print(f"❌ PROJECT_GUIDE.md compliance check failed: {e}")
        return False

def generate_content_simple(config) -> Optional[str]:
    """
    Simple content generation using direct API calls.
    No abstractions, no service layers, maximum simplicity.
    """
    try:
        from modules.content_generator import generate_content_for_material
        
        # Get configuration values from GlobalConfigManager
        material = config.get_material()
        provider = config.get_generator_provider()
        max_tokens = config.get_max_tokens()
        temperature = config.get_content_temperature()
        
        print(f"🎯 Generating content for {material} using {provider}")
        print(f"⚙️ Settings: {max_tokens} tokens, {temperature} temperature")
        
        # Simple content generation call
        content = generate_content_for_material(
            material=material,
            provider=provider,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if content:
            # Save to output file
            output_path = save_content_simple(config, content)
            return output_path
        else:
            raise RuntimeError("Empty content returned from generator")
            
    except Exception as e:
        print(f"❌ Content generation error: {e}")
        return None

def save_content_simple(config, content: str) -> str:
    """
    Save content to output file using simple direct approach.
    """
    try:
        # Get file name from config
        file_name = config.get_file_name()
        
        # Create output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Write content
        output_path = output_dir / file_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return str(output_path)
        
    except Exception as e:
        raise RuntimeError(f"Failed to save content: {e}")

if __name__ == "__main__":
    main()
