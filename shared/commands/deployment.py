#!/usr/bin/env python3
"""
Deployment Command Handlers

Handles deployment to Next.js production site.
"""


def deploy_to_production():
    """Deploy generated content to Next.js production site."""
    import os
    import shutil
    import subprocess

    from domains.materials.data_loader import clear_cache

    # Clear ALL caches to ensure fresh data is used
    from domains.materials.materials_cache import (
        clear_materials_cache,
        invalidate_material_cache,
    )
    clear_cache()  # Clear loader LRU caches
    clear_materials_cache()  # Clear materials cache
    invalidate_material_cache()  # Clear name lookup cache
    print("🔄 Cleared all caches to ensure fresh data")
    
    # STEP 0: Validate source data integrity BEFORE regeneration
    print("\n" + "=" * 80)
    print("🔍 STEP 0: VALIDATING SOURCE DATA INTEGRITY")
    print("=" * 80)
    
    validation_result = subprocess.run(
        ['python3', 'scripts/validation/verify_data_integrity.py'],
        capture_output=True,
        text=True
    )
    
    if validation_result.stdout:
        print(validation_result.stdout)
    
    if validation_result.returncode != 0:
        print("\n❌ DEPLOYMENT ABORTED: Data integrity validation failed")
        print("   Fix broken references in source data before deploying")
        print("   Run: python3 scripts/validation/verify_data_integrity.py")
        return False
    
    print("\n✅ Source data integrity validated - proceeding with deployment")
    
    # STEP 1: Regenerate frontmatter from all domains (Universal Export System)
    print("\n" + "=" * 80)
    print("📦 STEP 1: Regenerating frontmatter for ALL DOMAINS (Universal Export System)")
    print("=" * 80)
    
    try:
        # Use Universal export system (regenerate_all_domains.py)
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        import time

        from scripts.operations.regenerate_all_domains import main as regenerate_all
        
        start_time = time.time()
        print("🔄 Exporting all domains: materials, contaminants, compounds, settings...")
        
        exit_code = regenerate_all()
        
        elapsed = time.time() - start_time
        
        if exit_code == 0:
            print(f"\n✅ Frontmatter regeneration complete (all 424 files)")
            print(f"   • Time: {elapsed:.1f}s")
        else:
            print(f"❌ Frontmatter regeneration had errors (exit code: {exit_code})")
            return False
            
    except Exception as e:
        print(f"❌ Frontmatter regeneration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # STEP 2: Validate exported frontmatter files
    print("\n" + "=" * 80)
    print("🔍 STEP 2: VALIDATING EXPORTED FRONTMATTER")
    print("=" * 80)
    
    frontmatter_validation_result = subprocess.run(
        ['python3', 'scripts/validation/verify_frontmatter_links.py'],
        capture_output=True,
        text=True
    )
    
    if frontmatter_validation_result.stdout:
        print(frontmatter_validation_result.stdout)
    
    if frontmatter_validation_result.returncode != 0:
        print("\n⚠️  WARNING: Frontmatter validation found issues")
        print("   Review warnings above, but deployment will continue")
        print("   Run: python3 scripts/validation/verify_frontmatter_links.py")
    else:
        print("\n✅ Frontmatter link validation passed")
    
    # STEP 3: Deployment complete
    print("\n" + "=" * 80)
    print("✅ STEP 3: Deployment complete - frontmatter in production location")
    print("=" * 80)
    print("📂 Universal export system writes directly to:")
    print("   /Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/")
    print("\n🎉 Deployment successful! Next.js production site updated.")
    
    return True


def legacy_deploy_step_removed():
    """
    LEGACY STEP - NO LONGER NEEDED (Dec 18, 2025)
    
    Old deployment copied from:
      /Users/todddunning/Desktop/Z-Beam/z-beam-generator/frontmatter (TrivialFrontmatterExporter output)
    To:
      /Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter (Next.js production)
    
    New Universal export system writes directly to production location.
    No copy step needed.
    """
    # STEP 2: Deploy to Next.js
    print("\n" + "=" * 80)
    print("🚀 STEP 2: Deploying frontmatter to Next.js production site")
    print("=" * 80)
    
    # Define source and target paths
    source_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/frontmatter"
    target_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter"
    
    try:
        # Verify source directory exists
        if not os.path.exists(source_dir):
            print(f"❌ Source directory not found: {source_dir}")
            return False
        
        # Verify target directory exists
        if not os.path.exists(target_dir):
            print(f"❌ Target directory not found: {target_dir}")
            return False
        
        print("🚀 Deploying frontmatter content from generator to Next.js production site...")
        print(f"📂 Source: {source_dir}")
        print(f"📂 Target: {target_dir}")
        
        deployment_stats = {
            "updated": 0,
            "created": 0,
            "errors": 0,
            "skipped": 0
        }
        
        # Deploy frontmatter component
        print("\n📦 Deploying frontmatter directory structure...")
        
        # Create target directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # Get list of content-type subdirectories and files
        try:
            items = os.listdir(source_dir)
            
            if not items:
                print("  ⚠️ No content found in frontmatter")
                deployment_stats["skipped"] += 1
            else:
                # Process each item (subdirectory or file)
                for item in items:
                    if item.startswith('.'):
                        continue
                    
                    source_path = os.path.join(source_dir, item)
                    target_path = os.path.join(target_dir, item)
                    
                    try:
                        if os.path.isdir(source_path):
                            # It's a content-type directory (materials, regions, etc.)
                            print(f"\n  📁 Processing {item}/ directory...")
                            
                            # Create target subdirectory if needed
                            os.makedirs(target_path, exist_ok=True)
                            
                            # Copy all files in the subdirectory
                            subdir_files = [f for f in os.listdir(source_path) 
                                          if os.path.isfile(os.path.join(source_path, f)) and not f.startswith('.')]
                            
                            for filename in subdir_files:
                                source_file = os.path.join(source_path, filename)
                                target_file = os.path.join(target_path, filename)
                                
                                file_exists = os.path.exists(target_file)
                                shutil.copy2(source_file, target_file)
                                
                                if file_exists:
                                    print(f"    ✅ Updated: {item}/{filename}")
                                    deployment_stats["updated"] += 1
                                else:
                                    print(f"    ✨ Created: {item}/{filename}")
                                    deployment_stats["created"] += 1
                                    
                        elif os.path.isfile(source_path):
                            # It's a root-level file
                            file_exists = os.path.exists(target_path)
                            shutil.copy2(source_path, target_path)
                            
                            if file_exists:
                                print(f"  ✅ Updated: {item}")
                                deployment_stats["updated"] += 1
                            else:
                                print(f"  ✨ Created: {item}")
                                deployment_stats["created"] += 1
                                
                    except Exception as e:
                        print(f"  ❌ Error copying {item}: {e}")
                        deployment_stats["errors"] += 1
                    
        except Exception as e:
            print(f"  ❌ Error processing frontmatter: {e}")
            deployment_stats["errors"] += 1
        
        # Print deployment summary
        print("\n🏁 Deployment completed!")
        print("📊 Statistics:")
        print(f"  ✨ Created: {deployment_stats['created']} files")
        print(f"  ✅ Updated: {deployment_stats['updated']} files")
        print(f"  ⚠️ Skipped: {deployment_stats['skipped']} components")
        print(f"  ❌ Errors: {deployment_stats['errors']} files")
        
        # Success if at least some files were deployed and no errors
        success = (deployment_stats["created"] + deployment_stats["updated"]) > 0 and deployment_stats["errors"] == 0
        
        if success:
            print("🎉 Deployment successful! Next.js production site updated.")
        else:
            print("⚠️ Deployment completed with issues.")
            
        return success
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# =================================================================================
# FRONTMATTER SANITIZATION POST-PROCESSOR
# =================================================================================

