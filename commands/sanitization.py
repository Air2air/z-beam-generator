#!/usr/bin/env python3
"""
Deployment Command Handlers

Handles deployment to Next.js production site.
"""



def run_frontmatter_sanitization(specific_file=None):
    """Run frontmatter YAML sanitization as a post-processor"""
    try:
        # Import the sanitizer
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts', 'tools'))
        from scripts.tools.sanitize_frontmatter import FrontmatterSanitizer
        
        sanitizer = FrontmatterSanitizer()
        
        if specific_file:
            # Sanitize specific file
            from pathlib import Path
            file_path = Path(specific_file)
            if not file_path.exists():
                print(f"❌ File not found: {specific_file}")
                return False
            
            print(f"🧹 Sanitizing specific file: {file_path.name}")
            result = sanitizer.sanitize_file(file_path)
            
            if result["fixed"]:
                print(f"✅ File fixed: {result['reason']}")
            else:
                print(f"ℹ️  No changes needed: {result['reason']}")
            
            return True
        else:
            # Sanitize all frontmatter files
            print("🧹 Running comprehensive frontmatter YAML sanitization...")
            result = sanitizer.sanitize_all_frontmatter()
            
            if result["success"]:
                if result["fixed"] > 0:
                    print(f"🎉 Sanitization complete! Fixed {result['fixed']} out of {result['total']} files")
                else:
                    print(f"✅ All {result['total']} frontmatter files are already valid!")
                return True
            else:
                print(f"❌ Sanitization failed: {result.get('error', 'Unknown error')}")
                return False
    
    except Exception as e:
        print(f"❌ Sanitization error: {e}")
        import traceback
        traceback.print_exc()
        return False


# =================================================================================
# CAPTION GENERATION
# =================================================================================

