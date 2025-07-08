#!/usr/bin/env python3
"""
Display current configuration via GlobalConfigManager
"""

import sys
import os
import re
from pathlib import Path

def check_global_config_exists():
    """Check if GlobalConfigManager exists"""
    config_path = Path("config/global_config.py")
    if not config_path.exists():
        print("❌ ERROR: GlobalConfigManager not found")
        print("   Expected: config/global_config.py")
        print("   Run: python compliance/audit_violations.py")
        return False
    return True

def check_hardcoded_values():
    """Check for hardcoded configuration values outside of config"""
    violations = []
    
    # USER SETTINGS (should use GlobalConfigManager)
    user_setting_patterns = [
        r'temperature\s*=\s*[0-9.]+',
        r'max_tokens\s*=\s*[0-9]+',
        r'timeout\s*=\s*[0-9]+',
        r'max_retries\s*=\s*[0-9]+',
        r'backoff_factor\s*=\s*[0-9.]+'
    ]
    
    # PROVIDER CONFIGURATIONS (should use GlobalConfigManager)
    provider_patterns = [
        r'["\']?(DEEPSEEK|XAI|GEMINI)["\']?\s*[=:]',
        r'["\']?(deepseek-chat|grok-beta|gemini-pro)["\']?',
        r'https://api\.(deepseek|x\.ai|googleapis)\.com'
    ]
    
    # DIRECTORY PATHS (should use GlobalConfigManager)
    path_patterns = [
        r'["\']output["\']?\s*[=:]',
        r'["\']prompts["\']?\s*[=:]',
        r'["\']logs["\']?\s*[=:]'
    ]
    
    # ALLOWED CONSTANTS (should NOT be flagged)
    allowed_constants = [
        r'FILE_EXTENSION\s*=\s*["\']\.mdx["\']',
        r'DEFAULT_ENCODING\s*=\s*["\']utf-8["\']',
        r'HTTP_SUCCESS\s*=\s*200',
        r'CHUNK_SIZE\s*=\s*1024'
    ]
    
    all_patterns = user_setting_patterns + provider_patterns + path_patterns
    
    # Files to check (exclude config files themselves)
    files_to_check = []
    for py_file in Path(".").rglob("*.py"):
        # Skip config files and compliance files
        if any(skip in str(py_file) for skip in ["config/", "compliance/", "tests/"]):
            continue
        files_to_check.append(py_file)
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    # Skip comments and docstrings
                    if line.strip().startswith('#') or '"""' in line or "'''" in line:
                        continue
                    
                    # Check if line contains allowed constants
                    is_allowed = False
                    for allowed_pattern in allowed_constants:
                        if re.search(allowed_pattern, line, re.IGNORECASE):
                            is_allowed = True
                            break
                    
                    if is_allowed:
                        continue
                    
                    # Check for violations
                    for pattern in all_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            violations.append({
                                'file': str(file_path),
                                'line': line_num,
                                'content': line.strip(),
                                'pattern': pattern,
                                'type': 'HARDCODED_SETTING'
                            })
                            
        except Exception:
            continue
    
    return violations

def check_config_usage():
    """Check if files are using GlobalConfigManager properly"""
    violations = []
    
    # Check for direct config dictionaries
    config_dict_patterns = [
        r'config\s*=\s*{',
        r'settings\s*=\s*{',
        r'configuration\s*=\s*{'
    ]
    
    # Check for environment variable usage outside of config
    env_patterns = [
        r'os\.getenv\(',
        r'os\.environ\[',
        r'getenv\('
    ]
    
    files_to_check = []
    for py_file in Path(".").rglob("*.py"):
        # Skip config files and compliance files
        if any(skip in str(py_file) for skip in ["config/", "compliance/", "tests/"]):
            continue
        files_to_check.append(py_file)
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    # Skip comments
                    if line.strip().startswith('#'):
                        continue
                    
                    # Check for direct config dictionaries
                    for pattern in config_dict_patterns:
                        if re.search(pattern, line):
                            violations.append({
                                'file': str(file_path),
                                'line': line_num,
                                'content': line.strip(),
                                'type': 'DIRECT_CONFIG_DICT',
                                'message': 'Use GlobalConfigManager instead of direct config dict'
                            })
                    
                    # Check for environment variable usage
                    for pattern in env_patterns:
                        if re.search(pattern, line):
                            violations.append({
                                'file': str(file_path),
                                'line': line_num,
                                'content': line.strip(),
                                'type': 'DIRECT_ENV_ACCESS',
                                'message': 'Use GlobalConfigManager instead of direct env access'
                            })
                            
        except Exception:
            continue
    
    return violations

def display_config():
    """Display current configuration"""
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from config.global_config import GlobalConfigManager
        
        config = GlobalConfigManager.get_instance()
        
        print("📋 Z-BEAM CONFIGURATION")
        print("=" * 40)
        
        # Core settings
        print("🔧 CORE SETTINGS:")
        print(f"  Generation Provider: {config.get_generation_provider()}")
        print(f"  Content Temperature: {config.get_content_temperature()}")
        print(f"  Optimization Temperature: {config.get_optimization_temperature()}")
        print(f"  Output Directory: {config.get_output_directory()}")
        print(f"  Prompts Directory: {config.get_prompts_directory()}")
        
        # API Keys status
        print("\n🔑 API KEYS STATUS:")
        api_keys = {
            "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
            "XAI_API_KEY": os.getenv("XAI_API_KEY"),
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY")
        }
        
        for key, value in api_keys.items():
            status = "✅ SET" if value else "❌ MISSING"
            print(f"  {key}: {status}")
        
        # File structure status
        print("\n📁 FILE STRUCTURE:")
        expected_files = [
            "run.py",
            "main.py",
            "config/global_config.py",
            "modules/content_generator.py",
            "modules/api_client.py"
        ]
        
        for file_path in expected_files:
            status = "✅ EXISTS" if Path(file_path).exists() else "❌ MISSING"
            print(f"  {file_path}: {status}")
        
        # Configuration methods
        print("\n🛠️ AVAILABLE CONFIG METHODS:")
        config_methods = [
            "get_generation_provider",
            "get_content_temperature", 
            "get_optimization_temperature",
            "get_output_directory",
            "get_prompts_directory"
        ]
        
        for method in config_methods:
            if hasattr(config, method):
                try:
                    value = getattr(config, method)()
                    print(f"  {method}(): {value}")
                except Exception as e:
                    print(f"  {method}(): ERROR - {e}")
            else:
                print(f"  {method}(): ❌ NOT FOUND")
        
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        print("   Check if GlobalConfigManager is properly implemented")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)

def display_hardcoded_violations():
    """Display hardcoded value violations"""
    print("\n🚨 HARDCODED VALUES CHECK")
    print("=" * 40)
    
    # Check for hardcoded values
    hardcoded_violations = check_hardcoded_values()
    if hardcoded_violations:
        print("❌ HARDCODED VALUES FOUND:")
        for violation in hardcoded_violations:
            print(f"  • {violation['file']}:{violation['line']}")
            print(f"    {violation['content']}")
            print(f"    Pattern: {violation['pattern']}")
            print()
    else:
        print("✅ NO HARDCODED VALUES FOUND")
    
    # Check for config usage violations
    config_violations = check_config_usage()
    if config_violations:
        print("\n❌ CONFIG USAGE VIOLATIONS:")
        for violation in config_violations:
            print(f"  • {violation['file']}:{violation['line']}")
            print(f"    {violation['content']}")
            print(f"    Issue: {violation['message']}")
            print()
    else:
        print("\n✅ PROPER CONFIG USAGE")
    
    # Summary
    total_violations = len(hardcoded_violations) + len(config_violations)
    print(f"\n📊 HARDCODED VALUES SUMMARY:")
    print(f"  Hardcoded values: {len(hardcoded_violations)}")
    print(f"  Config violations: {len(config_violations)}")
    print(f"  Total violations: {total_violations}")
    
    if total_violations > 0:
        print(f"  Status: ❌ VIOLATIONS FOUND")
        return False
    else:
        print(f"  Status: ✅ COMPLIANT")
        return True

def main():
    """Main function"""
    if not check_global_config_exists():
        sys.exit(1)
    
    display_config()
    
    # Check for hardcoded values
    is_compliant = display_hardcoded_violations()
    
    print(f"\n🎯 USAGE:")
    print(f"  python compliance/audit_violations.py  # Check compliance")
    print(f"  python compliance/show_config.py       # Show this config")
    print(f"  python main.py                         # Run application")
    
    if not is_compliant:
        print(f"\n⚠️  FIX REQUIRED: Move hardcoded values to GlobalConfigManager")
        sys.exit(1)

if __name__ == "__main__":
    main()