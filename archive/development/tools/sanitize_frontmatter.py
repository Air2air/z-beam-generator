#!/usr/bin/env python3
"""
Frontmatter YAML Sanitization Post-Processor
Applies comprehensive YAML syntax fixes to existing frontmatter files without regenerating them.
"""

import re
import yaml
from pathlib import Path

class FrontmatterSanitizer:
    """Comprehensive YAML sanitization for frontmatter files"""
    
    def __init__(self):
        self.processed_count = 0
        self.fixed_count = 0
        self.error_count = 0
        self.errors = []
    
    def sanitize_all_frontmatter(self, frontmatter_dir: str = "content/components/frontmatter") -> dict:
        """Sanitize all frontmatter files in the specified directory"""
        print("🧹 Starting comprehensive frontmatter YAML sanitization...")
        
        frontmatter_path = Path(frontmatter_dir)
        if not frontmatter_path.exists():
            print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
            return {"success": False, "error": "Directory not found"}
        
        # Find all frontmatter files
        frontmatter_files = list(frontmatter_path.glob("*-laser-cleaning.md"))
        total_files = len(frontmatter_files)
        
        print(f"📋 Found {total_files} frontmatter files to process")
        
        # Process each file
        for i, file_path in enumerate(frontmatter_files, 1):
            material_name = file_path.stem.replace("-laser-cleaning", "")
            print(f"🔧 [{i:3d}/{total_files}] Processing {material_name}...", end="")
            
            try:
                result = self.sanitize_file(file_path)
                if result["fixed"]:
                    self.fixed_count += 1
                    print(" ✅ Fixed")
                else:
                    print(" ✓ Already valid")
                self.processed_count += 1
                
            except Exception as e:
                self.error_count += 1
                error_msg = f"{material_name}: {str(e)}"
                self.errors.append(error_msg)
                print(f" ❌ Error: {e}")
        
        # Print summary
        self.print_summary()
        
        return {
            "success": True,
            "total": total_files,
            "processed": self.processed_count,
            "fixed": self.fixed_count,
            "errors": self.error_count,
            "error_details": self.errors
        }
    
    def sanitize_file(self, file_path: Path) -> dict:
        """Sanitize a single frontmatter file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Extract YAML content
        yaml_content = self.extract_yaml_content(original_content)
        if not yaml_content:
            return {"fixed": False, "reason": "No YAML content found"}
        
        # Test if original YAML is valid
        original_valid = self.test_yaml_validity(yaml_content)
        
        # Apply sanitization
        sanitized_yaml = self.apply_comprehensive_sanitization(yaml_content)
        
        # Test if sanitized YAML is valid
        sanitized_valid = self.test_yaml_validity(sanitized_yaml)
        
        # Only write if we made improvements
        if not original_valid and sanitized_valid:
            # Reconstruct the full file content
            new_content = f"---\n{sanitized_yaml}---"
            
            # Add version log if it exists in original
            if "Version Log" in original_content:
                version_log_start = original_content.find("---\nVersion Log")
                if version_log_start > 0:
                    version_log = original_content[version_log_start:]
                    new_content += f"\n\n{version_log}"
            
            # Write the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return {"fixed": True, "reason": "YAML syntax fixed"}
        
        elif not original_valid and not sanitized_valid:
            return {"fixed": False, "reason": "Unable to fix YAML syntax"}
        
        else:
            return {"fixed": False, "reason": "Already valid"}
    
    def extract_yaml_content(self, content: str) -> str:
        """Extract YAML content from frontmatter file"""
        if not content.startswith("---"):
            return ""
        
        # Find the closing ---
        yaml_start = 3  # Skip first ---
        yaml_end = content.find("---", yaml_start)
        
        if yaml_end == -1:
            # No closing ---, assume rest of content until next --- is YAML
            next_section = content.find("---", yaml_start)
            if next_section == -1:
                yaml_content = content[yaml_start:].strip()
            else:
                yaml_content = content[yaml_start:next_section].strip()
        else:
            yaml_content = content[yaml_start:yaml_end].strip()
        
        return yaml_content
    
    def test_yaml_validity(self, yaml_content: str) -> bool:
        """Test if YAML content is valid"""
        try:
            yaml.safe_load(yaml_content)
            return True
        except yaml.YAMLError:
            return False
    
    def apply_comprehensive_sanitization(self, yaml_content: str) -> str:
        """Apply all discovered YAML sanitization patterns"""
        
        # Pattern 1: Fix specific problematic quoting like "'"value"'
        yaml_content = re.sub(r':\s*"\'([^"\']*(?:\n[^"\']*)*)\'"', r': "\1"', yaml_content, flags=re.MULTILINE | re.DOTALL)
        
        # Pattern 2: Fix patterns like "'value'" (including multi-line)
        yaml_content = re.sub(r':\s*\'([^\']*(?:\n[^\']*)*?)\'', r': "\1"', yaml_content, flags=re.MULTILINE | re.DOTALL)
        
        # Pattern 3: Fix double-quoted patterns like ""value"" (including multi-line)
        yaml_content = re.sub(r':\s*""([^"]*(?:\n[^"]*)*?)""', r': "\1"', yaml_content, flags=re.MULTILINE | re.DOTALL)
        
        # Pattern 4: Fix triple-quoted patterns like """value"""
        yaml_content = re.sub(r':\s*"""([^"]*(?:\n[^"]*)*?)"""', r': "\1"', yaml_content, flags=re.MULTILINE | re.DOTALL)
        
        # Pattern 5: Fix over-escaped quotes
        yaml_content = re.sub(r'\\"([^"]+)\\"', r'"\1"', yaml_content)
        
        # Pattern 6: Fix patterns like ""\"text\""
        yaml_content = re.sub(r'""\\"([^"]+)\\""', r'"\1"', yaml_content)
        
        # Pattern 7: Fix broken multi-line strings in descriptions
        yaml_content = re.sub(r'description:\s*"\'([^"\']*?)"\s*\n\s*([^"\']*?)\'"', r'description: "\1 \2"', yaml_content, flags=re.MULTILINE)
        
        # Pattern 8: Fix keywords with similar issues  
        yaml_content = re.sub(r'keywords:\s*"\'([^"\']*?)\'"', r'keywords: "\1"', yaml_content)
        
        # Pattern 9: Fix symbol patterns
        yaml_content = re.sub(r'symbol:\s*"\'([^"\']*?)\'"', r'symbol: "\1"', yaml_content)
        
        # Pattern 10: Fix unicode escape sequences
        unicode_fixes = {
            '\\xB0': '°',   # degree symbol
            '\\xB3': '³',   # superscript 3
            '\\xB7': '·',   # middle dot
            '\\u2082': '₂', # subscript 2
            '\\u2083': '₃', # subscript 3
            '\\u03BC': 'μ', # mu
            '\\u2013': '–', # en dash
            '\\u00B1': '±', # plus-minus
            '\\u03A9': 'Ω', # omega
            '\\u03B1': 'α', # alpha
            '\\u03B2': 'β', # beta
            '\\u03B3': 'γ', # gamma
            '\\u03B4': 'δ', # delta
            '\\u03BB': 'λ', # lambda
        }
        
        for escape_seq, char in unicode_fixes.items():
            yaml_content = yaml_content.replace(escape_seq, char)
        
        # Pattern 11: Fix broken multi-line strings that span multiple lines
        yaml_content = re.sub(r':\s*"([^"]*)\n\s*([^"]*)"', r': "\1 \2"', yaml_content, flags=re.MULTILINE)
        
        # Pattern 12: Fix broken array values that got split
        yaml_content = re.sub(r'- "\'([^"\']*?)\'"', r'- "\1"', yaml_content)
        
        # Pattern 13: Fix formula lines that got broken across multiple lines
        yaml_content = re.sub(r'formula: "([^"]*)\n\s*([^"]*)"', r'formula: "\1\2"', yaml_content, flags=re.MULTILINE)
        
        # Pattern 14: Fix chemical symbols that got broken
        yaml_content = re.sub(r'symbol: ([^\n]*)\n\s*([A-Z][a-z]*)', r'symbol: "\1\2"', yaml_content, flags=re.MULTILINE)
        
        # Pattern 15: Clean up any remaining whitespace and line breaks in quoted strings
        yaml_content = re.sub(r':\s*"([^"]*)\s*\n\s*([^"]*)"', r': "\1 \2"', yaml_content, flags=re.MULTILINE)
        
        # Pattern 16: Fix any remaining line continuations in quoted values
        yaml_content = re.sub(r'"([^"]*?)\n\s+([^"]*?)"', r'"\1 \2"', yaml_content, flags=re.MULTILINE)
        
        # Pattern 17: Fix YAML structure issues
        yaml_content = self.fix_yaml_structure(yaml_content)
        
        # Pattern 18: Final cleanup
        yaml_content = self.final_cleanup(yaml_content)
        
        return yaml_content
    
    def fix_yaml_structure(self, yaml_content: str) -> str:
        """Fix structural YAML issues"""
        lines = yaml_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if ':' in line and not line.strip().startswith('-'):
                # Ensure there's a space after the colon
                line = re.sub(r':([^\s])', r': \1', line)
                
                # Fix values that lost their quotes but need them
                if re.match(r'^\s*\w+:\s*[^"\'\s].*[^"\s]$', line):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0]
                        value = parts[1].strip()
                        # Only quote if it's not a number and doesn't already have quotes
                        if value and not value.startswith('"') and not value.startswith("'") and not value.replace('.', '').replace('-', '').isdigit():
                            # Check if value contains special characters that need quoting
                            if any(char in value for char in [',', ':', '(', ')', '%', '°', '³', '₂', '₃']):
                                line = f'{key}: "{value}"'
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def final_cleanup(self, yaml_content: str) -> str:
        """Apply final cleanup patterns"""
        # Remove excessive double quotes
        yaml_content = yaml_content.replace('""""', '"')
        yaml_content = yaml_content.replace('"""', '"')
        yaml_content = yaml_content.replace('""', '"')
        
        # Fix spacing issues
        yaml_content = re.sub(r'\n\s*\n\s*\n', '\n\n', yaml_content)  # Max 2 consecutive newlines
        
        return yaml_content.strip()
    
    def print_summary(self):
        """Print processing summary"""
        print("\n" + "="*60)
        print("📊 FRONTMATTER SANITIZATION SUMMARY")
        print("="*60)
        print(f"📋 Total processed: {self.processed_count}")
        print(f"🔧 Files fixed: {self.fixed_count}")
        print(f"❌ Errors: {self.error_count}")
        
        if self.fixed_count > 0:
            success_rate = (self.fixed_count / self.processed_count) * 100
            print(f"✅ Fix success rate: {success_rate:.1f}%")
        
        if self.errors:
            print("\n❌ Error details:")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"   • {error}")
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more errors")
        
        print("="*60)

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sanitize frontmatter YAML files")
    parser.add_argument("--dir", default="content/components/frontmatter", 
                      help="Directory containing frontmatter files")
    parser.add_argument("--file", help="Sanitize a specific file instead of all files")
    
    args = parser.parse_args()
    
    sanitizer = FrontmatterSanitizer()
    
    if args.file:
        # Sanitize single file
        file_path = Path(args.file)
        if file_path.exists():
            result = sanitizer.sanitize_file(file_path)
            print(f"✅ {file_path.name}: {result}")
        else:
            print(f"❌ File not found: {args.file}")
    else:
        # Sanitize all files
        result = sanitizer.sanitize_all_frontmatter(args.dir)
        if result["success"]:
            print(f"\n🎉 Sanitization complete! Fixed {result['fixed']} out of {result['total']} files")
        else:
            print(f"❌ Sanitization failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
