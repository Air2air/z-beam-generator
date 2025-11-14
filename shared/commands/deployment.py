#!/usr/bin/env python3
"""
Deployment Command Handlers

Handles deployment to Next.js production site.
"""


def deploy_to_production():
    """Deploy generated content to Next.js production site."""
    import shutil
    import os
    
    # Clear materials cache to ensure fresh data is used
    from data.materials.materials import clear_materials_cache
    clear_materials_cache()
    print("🔄 Cleared materials cache to ensure fresh data")
    
    # Define source and target paths - ONLY FRONTMATTER
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
        print("📋 Deploying frontmatter component only")
        
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

