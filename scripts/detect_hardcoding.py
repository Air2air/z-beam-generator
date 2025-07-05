#!/usr/bin/env python3
"""
Anti-Hardcoding Linter

Scans the codebase for hardcoded configuration values and suggests fixes.
Run this regularly to prevent Claude from hardcoding values!
"""

import os
import re
import sys
from typing import List, Tuple, Dict


class HardcodingDetector:
    """Detects hardcoded configuration values and architectural violations in Python files."""
    
    def __init__(self, generator_dir: str):
        self.generator_dir = generator_dir
        self.root_dir = os.path.dirname(generator_dir)  # Parent directory (project root)
        self.violations: List[Tuple[str, int, str, str]] = []
        
        # Directories to exclude from scanning (Next.js website files)
        self.excluded_website_dirs = {
            'app',           # Next.js app directory
            'public',        # Next.js public directory  
            'pages',         # Next.js pages directory (if using pages router)
            'components',    # Next.js components (already in app/components)
            'styles',        # CSS/styling directories
            'node_modules',  # Dependencies
            '.next',         # Next.js build directory
            '.git',          # Git directory
            '__pycache__',   # Python cache
            'docs',          # Documentation
        }
        
        # Generator-related files allowed in root
        self.allowed_root_generator_files = {
            'run.py',           # Main user config file
            'train.py',         # Training entry point  
            'workflow.py',      # Workflow commands
            'show_config.py',   # Config display utility
        }
        
        # Patterns that indicate hardcoded values
        self.hardcoded_patterns = [
            # Temperature values
            (r'temperature.*=.*[0-9]\.[0-9]', 'hardcoded_temperature', 
             'Use get_config().get_*_temperature() instead'),
            
            # Threshold values
            (r'threshold.*=.*[0-9]+', 'hardcoded_threshold',
             'Use get_config().get_ai_detection_threshold() or get_natural_voice_threshold()'),
            
            # Iteration values
            (r'iterations.*=.*[0-9]+', 'hardcoded_iterations',
             'Use get_config().get_iterations_per_section()'),
            
            # Word limits
            (r'max.*words.*=.*[0-9]+', 'hardcoded_word_limit',
             'Use get_config().get_max_article_words()'),
             
            # API timeouts
            (r'timeout.*=.*[0-9]+', 'hardcoded_timeout',
             'Use get_config().get_api_timeout()'),
            
            # Common hardcoded values in function calls
            (r'temperature\s*=\s*0\.[0-9]+', 'hardcoded_temp_param',
             'Use temperature from get_config().get_temperature_config()'),
             
            (r'ai_threshold\s*=\s*[0-9]+', 'hardcoded_ai_threshold',
             'Use get_config().get_ai_detection_threshold()'),
             
            (r'human_threshold\s*=\s*[0-9]+', 'hardcoded_human_threshold', 
             'Use get_config().get_natural_voice_threshold()'),
             
            # API Providers (hardcoded strings)
            (r'["\']anthropic["\']', 'hardcoded_provider',
             'Use get_config().get_provider() instead'),
             
            (r'["\']openai["\']', 'hardcoded_provider',
             'Use get_config().get_provider() instead'),
             
            (r'["\']google["\']', 'hardcoded_provider',
             'Use get_config().get_provider() instead'),
             
            (r'["\']groq["\']', 'hardcoded_provider',
             'Use get_config().get_provider() instead'),
             
            # Model names (hardcoded strings)
            (r'["\']claude-3-5-sonnet["\']', 'hardcoded_model',
             'Use get_config().get_model() instead'),
             
            (r'["\']gpt-4["\']', 'hardcoded_model',
             'Use get_config().get_model() instead'),
             
            (r'["\']gemini["\']', 'hardcoded_model',
             'Use get_config().get_model() instead'),
             
            (r'["\']llama["\']', 'hardcoded_model',
             'Use get_config().get_model() instead'),
             
            # API URLs (hardcoded strings)
            (r'["\']https://api\.anthropic\.com["\']', 'hardcoded_api_url',
             'Use get_config().get_api_url() instead'),
             
            (r'["\']https://api\.openai\.com["\']', 'hardcoded_api_url',
             'Use get_config().get_api_url() instead'),
             
            (r'["\']https://api\.groq\.com["\']', 'hardcoded_api_url',
             'Use get_config().get_api_url() instead'),
             
            # Provider assignments
            (r'provider\s*=\s*["\'][^"\']+["\']', 'hardcoded_provider_assignment',
             'Use provider=get_config().get_provider() instead'),
             
            # Model assignments
            (r'model\s*=\s*["\'][^"\']+["\']', 'hardcoded_model_assignment',
             'Use model=get_config().get_model() instead'),
             
            # API key patterns (security risk)
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'hardcoded_api_key',
             'SECURITY RISK: Use environment variables or get_config()'),
             
            # Base URL assignments
            (r'base_url\s*=\s*["\']https://[^"\']+["\']', 'hardcoded_base_url',
             'Use base_url=get_config().get_api_url() instead'),
        ]
        
        # Files to exclude from checking
        self.excluded_files = {
            'config/global_config.py',  # This file is allowed to have defaults
            'config/settings.py',       # Legacy settings file
            'tests/',                   # Test files can have hardcoded values
            'scripts/',                 # Utility scripts
        }
    
    def should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded from hardcoding detection."""
        rel_path = os.path.relpath(file_path, self.generator_dir)
        
        for excluded in self.excluded_files:
            if rel_path.startswith(excluded) or excluded in rel_path:
                return True
        
        return False
    
    def scan_file(self, file_path: str) -> List[Tuple[int, str, str]]:
        """Scan a single file for hardcoded values."""
        violations = []
        
        if self.should_exclude_file(file_path):
            return violations
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return violations
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and docstrings
            if line.startswith('#') or '"""' in line or "'''" in line:
                continue
            
            # Check each hardcoding pattern
            for pattern, violation_type, suggestion in self.hardcoded_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append((line_num, line, suggestion))
        
        return violations
    
    def scan_directory(self) -> None:
        """Scan the generator directory and relevant root files for hardcoded values."""
        print("🔍 Scanning generator project files for hardcoded configuration values...")
        print("=" * 60)
        
        python_files = []
        
        # 1. Scan all files in the /generator directory
        for root, dirs, files in os.walk(self.generator_dir):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        # 2. Scan specific generator-related files in the root directory
        #    (but exclude Next.js website files entirely)
        for item in os.listdir(self.root_dir):
            item_path = os.path.join(self.root_dir, item)
            
            if os.path.isfile(item_path) and item.endswith('.py'):
                # Only include if it's a known generator file or has generator imports
                if (item in self.allowed_root_generator_files or 
                    self._is_generator_file(item_path)):
                    python_files.append(item_path)
        
        total_violations = 0
        
        for file_path in python_files:
            violations = self.scan_file(file_path)
            
            if violations:
                # Show path relative to project root for clarity
                rel_path = os.path.relpath(file_path, self.root_dir)
                print(f"\n❌ {rel_path}")
                print("-" * 40)
                
                for line_num, line, suggestion in violations:
                    print(f"  Line {line_num}: {line}")
                    print(f"    💡 {suggestion}")
                    print()
                    total_violations += 1
        
        if total_violations == 0:
            print("✅ No hardcoded configuration values found in generator project files!")
        else:
            print(f"\n💥 Found {total_violations} hardcoded configuration values!")
            print("\n🔧 How to fix:")
            print("1. Import: from config.global_config import get_config")
            print("2. Replace hardcoded values with get_config().get_*() calls")
            print("3. Run this tool again to verify fixes")
        
        # Check architectural violations
        print(f"\n{'='*60}")
        print("🏗️  Checking Architecture Rules...")
        architectural_violations = self.check_architectural_violations()
        
        if architectural_violations:
            print(f"\n❌ Found {len(architectural_violations)} architectural violations!")
            print("-" * 40)
            for file_path, message in architectural_violations:
                rel_path = os.path.relpath(file_path, self.root_dir)
                print(f"  {rel_path}")
                print(f"    💡 {message}")
                print()
        else:
            print("✅ No architectural violations found!")
        
        # Update total violation count
        total_violations += len(architectural_violations)
    
    def generate_fix_suggestions(self) -> Dict[str, str]:
        """Generate specific fix suggestions for common patterns."""
        return {
            # Temperature fixes
            "temperature=0.3": "temperature=get_config().get_detection_temperature()",
            "temperature=0.6": "temperature=get_config().get_content_temperature()",
            "temperature=0.7": "temperature=get_config().get_improvement_temperature()",
            
            # Threshold fixes
            "ai_threshold=25": "ai_threshold=get_config().get_ai_detection_threshold()",
            "human_threshold=25": "human_threshold=get_config().get_natural_voice_threshold()",
            
            # Configuration fixes
            "iterations_per_section=3": "iterations_per_section=get_config().get_iterations_per_section()",
            "max_article_words=1200": "max_article_words=get_config().get_max_article_words()",
            "timeout=60": "timeout=get_config().get_api_timeout()",
            
            # Provider fixes
            'provider="anthropic"': "provider=get_config().get_provider()",
            'provider="openai"': "provider=get_config().get_provider()",
            'provider="google"': "provider=get_config().get_provider()",
            'provider="groq"': "provider=get_config().get_provider()",
            
            # Model fixes
            'model="claude-3-5-sonnet"': "model=get_config().get_model()",
            'model="gpt-4"': "model=get_config().get_model()",
            'model="gemini"': "model=get_config().get_model()",
            
            # API URL fixes
            'base_url="https://api.anthropic.com"': "base_url=get_config().get_api_url()",
            'base_url="https://api.openai.com"': "base_url=get_config().get_api_url()",
            'base_url="https://api.groq.com"': "base_url=get_config().get_api_url()",
        }
    
    def check_architectural_violations(self) -> List[Tuple[str, str]]:
        """Check for generator project files that violate the architectural rule: all generator files except allowed ones should be in /generator."""
        violations = []
        
        # Generator-related directories that should NOT be in root
        # (excluding Next.js website directories like app/, public/, etc.)
        generator_related_dirs = {
            'detection',        # Should be in /generator
            'sections',         # Should be in /generator  
            'prompt_archive',   # Should be in /generator
            'logs',            # Should be in /generator
            'cache',           # Should be in /generator
            'config',          # Should be in /generator (if standalone)
            'core',            # Should be in /generator
            'infrastructure',  # Should be in /generator
            'modules',         # Should be in /generator
            'prompts',         # Should be in /generator
            'scripts',         # Should be in /generator
            'tests',           # Should be in /generator (generator tests)
        }
        
        # Scan root directory for generator violations
        try:
            for item in os.listdir(self.root_dir):
                # Skip Next.js website directories entirely
                if item in self.excluded_website_dirs:
                    continue
                    
                item_path = os.path.join(self.root_dir, item)
                
                if os.path.isfile(item_path):
                    if item.endswith('.py'):
                        # Check if it's a generator file that should be moved
                        if item not in self.allowed_root_generator_files:
                            # Check if it's a generator file
                            if self._is_generator_file(item_path):
                                violations.append((
                                    item_path,
                                    f"Generator file '{item}' should be moved to /generator directory"
                                ))
                                
                elif os.path.isdir(item_path):
                    # Check if it's a generator-related directory
                    if item in generator_related_dirs:
                        violations.append((
                            item_path,
                            f"Generator directory '{item}' should be moved to /generator"
                        ))
                            
        except Exception as e:
            print(f"Warning: Could not scan root directory: {e}")
            
        return violations
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a pattern (simple wildcard support)."""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def _imports_generator_modules(self, file_path: str) -> bool:
        """Check if a Python file imports generator-specific modules."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for imports that suggest this is a generator file
            generator_imports = [
                'from modules.',
                'from core.',
                'from infrastructure.',
                'from config.global_config',
                'from detection.',
                'import ApplicationRunner',
                'import GenerationContext',
                'import TemperatureConfig',
                'get_logger("',
            ]
            
            return any(imp in content for imp in generator_imports)
            
        except Exception:
            return False
    
    def _is_generator_file(self, file_path: str) -> bool:
        """Check if a file is a generator-related file based on patterns and imports."""
        filename = os.path.basename(file_path)
        
        # Generator-related file patterns
        generator_file_patterns = [
            'interactive_training.py',
            'test_runner.py', 
            'section_json_util.py',
            '*_service.py',
            '*_detector.py',
            '*_generator.py',
            '*_optimizer.py',
            '*_repository.py',
        ]
        
        # Check if it matches generator patterns
        is_generator_pattern = any(
            self._matches_pattern(filename, pattern) 
            for pattern in generator_file_patterns
        )
        
        # Also check if it imports from generator modules
        return is_generator_pattern or self._imports_generator_modules(file_path)
    
def main():
    """Main entry point for the hardcoding detector."""
    # Setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    generator_dir = os.path.dirname(script_dir)  # Parent of scripts directory
    
    if not os.path.exists(generator_dir):
        print(f"❌ Generator directory not found: {generator_dir}")
        sys.exit(1)
    
    detector = HardcodingDetector(generator_dir)
    detector.scan_directory()
    
    print("\n" + "=" * 60)
    print("🎯 PREVENTION TIPS:")
    print("• Always use get_config() for configuration values")
    print("• Never hardcode thresholds, temperatures, or limits")
    print("• Add @requires_config decorator to functions needing config")
    print("• Run this tool before committing code changes")
    
    fix_suggestions = detector.generate_fix_suggestions()
    if fix_suggestions:
        print("\n🔧 COMMON FIXES:")
        for wrong, right in fix_suggestions.items():
            print(f"  ❌ {wrong}")
            print(f"  ✅ {right}")
            print()


if __name__ == "__main__":
    main()
