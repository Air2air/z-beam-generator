#!/usr/bin/env python3
"""
Quick Fix for Hardcoded Values

This script automatically fixes the most common hardcoding violations.
Run after Claude makes changes to automatically fix hardcoded values.
"""

import os
import re
import sys
from typing import Dict, List


class HardcodingFixer:
    """Automatically fixes common hardcoded configuration values."""
    
    def __init__(self, generator_dir: str):
        self.generator_dir = generator_dir
        self.fixes_applied = 0
        
        # Common hardcoded patterns and their fixes
        self.fix_patterns = [
            # Temperature fixes
            (r'temperature\s*=\s*0\.3(?![0-9])', 'temperature=get_config().get_detection_temperature()'),
            (r'temperature\s*=\s*0\.6(?![0-9])', 'temperature=get_config().get_content_temperature()'),
            (r'temperature\s*=\s*0\.7(?![0-9])', 'temperature=get_config().get_improvement_temperature()'),
            (r'temperature\s*=\s*0\.4(?![0-9])', 'temperature=get_config().get_summary_temperature()'),
            (r'temperature\s*=\s*0\.2(?![0-9])', 'temperature=get_config().get_metadata_temperature()'),
            
            # Threshold fixes
            (r'ai_threshold\s*=\s*25(?![0-9])', 'ai_threshold=get_config().get_ai_detection_threshold()'),
            (r'human_threshold\s*=\s*25(?![0-9])', 'human_threshold=get_config().get_natural_voice_threshold()'),
            (r'natural_voice_threshold\s*=\s*25(?![0-9])', 'natural_voice_threshold=get_config().get_natural_voice_threshold()'),
            
            # Iteration fixes
            (r'iterations_per_section\s*=\s*[0-9]+(?![0-9])', 'iterations_per_section=get_config().get_iterations_per_section()'),
            (r'max_iterations\s*=\s*[0-9]+(?![0-9])', 'max_iterations=get_config().get_iterations_per_section()'),
            
            # Word limit fixes
            (r'max_article_words\s*=\s*[0-9]+(?![0-9])', 'max_article_words=get_config().get_max_article_words()'),
            
            # Timeout fixes
            (r'timeout\s*=\s*60(?![0-9])', 'timeout=get_config().get_api_timeout()'),
            (r'api_timeout\s*=\s*60(?![0-9])', 'api_timeout=get_config().get_api_timeout()'),
            
            # Provider fixes
            (r'provider\s*=\s*["\']anthropic["\']', 'provider=get_config().get_provider()'),
            (r'provider\s*=\s*["\']openai["\']', 'provider=get_config().get_provider()'),
            (r'provider\s*=\s*["\']google["\']', 'provider=get_config().get_provider()'),
            (r'provider\s*=\s*["\']groq["\']', 'provider=get_config().get_provider()'),
            
            # Model fixes
            (r'model\s*=\s*["\']claude-3-5-sonnet[^"\']*["\']', 'model=get_config().get_model()'),
            (r'model\s*=\s*["\']gpt-4[^"\']*["\']', 'model=get_config().get_model()'),
            (r'model\s*=\s*["\']gemini[^"\']*["\']', 'model=get_config().get_model()'),
            (r'model\s*=\s*["\']llama[^"\']*["\']', 'model=get_config().get_model()'),
            
            # API URL fixes  
            (r'base_url\s*=\s*["\']https://api\.anthropic\.com[^"\']*["\']', 'base_url=get_config().get_api_url()'),
            (r'base_url\s*=\s*["\']https://api\.openai\.com[^"\']*["\']', 'base_url=get_config().get_api_url()'),
            (r'base_url\s*=\s*["\']https://api\.groq\.com[^"\']*["\']', 'base_url=get_config().get_api_url()'),
            (r'api_url\s*=\s*["\']https://[^"\']*["\']', 'api_url=get_config().get_api_url()'),
        ]
        
        # Files to exclude from auto-fixing
        self.excluded_files = {
            'config/global_config.py',  # This file defines the defaults
            'config/settings.py',       # Legacy settings file
            'scripts/detect_hardcoding.py',  # Detection script itself
            'scripts/fix_hardcoding.py',     # This script
            'tests/',                   # Test files
        }
    
    def should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded from auto-fixing."""
        rel_path = os.path.relpath(file_path, self.generator_dir)
        
        for excluded in self.excluded_files:
            if rel_path.startswith(excluded) or excluded in rel_path:
                return True
        
        return False
    
    def fix_file(self, file_path: str) -> int:
        """Fix hardcoded values in a single file."""
        if self.should_exclude_file(file_path):
            return 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return 0
        
        original_content = content
        fixes_in_file = 0
        
        # Apply each fix pattern
        for pattern, replacement in self.fix_patterns:
            if re.search(pattern, content):
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    fixes_in_file += 1
        
        # Add import if we made fixes and it's not already there
        if fixes_in_file > 0 and 'from config.global_config import get_config' not in content:
            # Find the best place to add the import
            lines = content.split('\n')
            import_added = False
            
            for i, line in enumerate(lines):
                # Add after existing imports but before other code
                if (line.strip() and 
                    not line.startswith('"""') and 
                    not line.startswith('#') and
                    not line.startswith('from ') and
                    not line.startswith('import ') and
                    not import_added):
                    
                    lines.insert(i, 'from config.global_config import get_config')
                    import_added = True
                    break
            
            if not import_added and lines:
                # Add at the beginning if no good spot found
                lines.insert(1, 'from config.global_config import get_config')
            
            content = '\n'.join(lines)
        
        # Write back if changed
        if content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed {fixes_in_file} issues in {os.path.relpath(file_path, self.generator_dir)}")
            except Exception as e:
                print(f"❌ Could not write {file_path}: {e}")
                return 0
        
        return fixes_in_file
    
    def fix_all_files(self) -> None:
        """Fix hardcoded values in all Python files."""
        print("🔧 Auto-fixing hardcoded configuration values...")
        print("=" * 60)
        
        python_files = []
        for root, dirs, files in os.walk(self.generator_dir):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        for file_path in python_files:
            fixes = self.fix_file(file_path)
            self.fixes_applied += fixes
        
        print(f"\n🎉 Applied {self.fixes_applied} automatic fixes!")
        
        if self.fixes_applied > 0:
            print("\n⚠️  IMPORTANT: Review the changes before committing!")
            print("1. Check that imports were added correctly")
            print("2. Test that the application still works")
            print("3. Run detect_hardcoding.py again to check for remaining issues")


def main():
    """Main entry point for the hardcoding fixer."""
    # Setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    generator_dir = os.path.dirname(script_dir)  # Parent of scripts directory
    
    if not os.path.exists(generator_dir):
        print(f"❌ Generator directory not found: {generator_dir}")
        sys.exit(1)
    
    print("🚨 AUTO-FIXING HARDCODED VALUES")
    print("This will modify your Python files automatically!")
    
    response = input("Continue? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Cancelled by user")
        return
    
    fixer = HardcodingFixer(generator_dir)
    fixer.fix_all_files()
    
    if fixer.fixes_applied > 0:
        print("\n🔍 Run detection again to see remaining issues:")
        print("python3 scripts/detect_hardcoding.py")


if __name__ == "__main__":
    main()
