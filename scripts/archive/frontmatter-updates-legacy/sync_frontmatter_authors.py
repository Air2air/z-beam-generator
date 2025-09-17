#!/usr/bin/env python3
"""
Frontmatter Author Synchronization Script

This script updates frontmatter files to use the correct author assignments
from materials.yaml, ensuring consistency across all components.
"""

import json
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple

def load_materials_data() -> Dict:
    """Load materials data from YAML file."""
    materials_file = Path("data/materials.yaml")
    
    if not materials_file.exists():
        print(f"❌ Materials file not found: {materials_file}")
        return {}
    
    try:
        with open(materials_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        print(f"✅ Loaded materials data from {materials_file}")
        return data
    except Exception as e:
        print(f"❌ Error loading materials data: {e}")
        return {}

def load_authors_data() -> List[Dict]:
    """Load authors data from JSON file."""
    authors_file = Path("components/author/authors.json")
    
    if not authors_file.exists():
        print(f"❌ Authors file not found: {authors_file}")
        return []
    
    try:
        with open(authors_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        authors = data.get("authors", [])
        print(f"✅ Loaded {len(authors)} authors from {authors_file}")
        return authors
    except Exception as e:
        print(f"❌ Error loading authors data: {e}")
        return []

def get_author_by_id(authors: List[Dict], author_id: int) -> Optional[Dict]:
    """Get author data by ID."""
    for author in authors:
        if author.get("id") == author_id:
            return author
    return None

def find_material_in_data(materials_data: Dict, material_name: str) -> Optional[Tuple[str, Dict]]:
    """Find material data in the nested materials structure."""
    if "materials" not in materials_data:
        return None
    
    # Check the materials section which contains categories directly
    materials_section = materials_data["materials"]
    for category_name, category_data in materials_section.items():
        if isinstance(category_data, dict) and "items" in category_data:
            for item in category_data["items"]:
                if item.get("name") == material_name:
                    return category_name, item
    
    return None

def get_frontmatter_files() -> List[Path]:
    """Get all frontmatter files."""
    frontmatter_dir = Path("content/components/frontmatter")
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        return []
    
    files = list(frontmatter_dir.glob("*.md"))
    print(f"📁 Found {len(files)} frontmatter files")
    return files

def extract_material_name_from_filename(filename: str) -> str:
    """Extract material name from frontmatter filename."""
    # Remove .md extension and -laser-cleaning suffix
    name = filename.replace(".md", "").replace("-laser-cleaning", "")
    # Convert from kebab-case to Title Case
    return name.replace("-", " ").title()

def parse_frontmatter_file(file_path: Path) -> Tuple[Dict, str]:
    """Parse frontmatter file and extract YAML content and remaining content."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Look for YAML frontmatter between --- markers
        if content.startswith("---\n"):
            # Find the end of the frontmatter
            end_marker = content.find("\n---\n", 4)
            if end_marker != -1:
                yaml_content = content[4:end_marker]
                remaining_content = content[end_marker + 5:]
                
                try:
                    frontmatter_data = yaml.safe_load(yaml_content)
                    return frontmatter_data or {}, remaining_content
                except yaml.YAMLError as e:
                    print(f"⚠️ YAML parsing error in {file_path}: {e}")
                    return {}, content
        
        # No valid frontmatter found
        return {}, content
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return {}, ""

def update_frontmatter_author(frontmatter_data: Dict, author_data: Dict) -> Dict:
    """Update frontmatter data with correct author information."""
    updated_data = frontmatter_data.copy()
    
    # Update author name
    updated_data["author"] = author_data["name"]
    
    # Update author_object if it exists
    if "author_object" in updated_data:
        updated_data["author_object"].update({
            "id": author_data["id"],
            "name": author_data["name"],
            "sex": "male" if author_data["sex"] == "m" else "female",
            "title": author_data["title"],
            "country": author_data["country"],
            "expertise": author_data["expertise"],
            "image": author_data.get("image")
        })
    
    return updated_data

def write_frontmatter_file(file_path: Path, frontmatter_data: Dict, remaining_content: str):
    """Write updated frontmatter file."""
    try:
        # Create YAML content
        yaml_content = yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True)
        
        # Construct the full file content
        full_content = f"---\n{yaml_content}---\n{remaining_content}"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_content)
        
        print(f"✅ Updated {file_path}")
    except Exception as e:
        print(f"❌ Error writing {file_path}: {e}")

def main():
    """Main synchronization function."""
    print("🔄 Starting frontmatter author synchronization...")
    
    # Load data
    materials_data = load_materials_data()
    authors_data = load_authors_data()
    
    if not materials_data or not authors_data:
        print("❌ Failed to load required data files")
        return 1
    
    # Get frontmatter files
    frontmatter_files = get_frontmatter_files()
    if not frontmatter_files:
        print("❌ No frontmatter files found")
        return 1
    
    updates_made = 0
    errors = 0
    
    for file_path in frontmatter_files:
        print(f"\n🔍 Checking {file_path.name}...")
        
        # Extract material name from filename
        material_name = extract_material_name_from_filename(file_path.name)
        print(f"   Material: {material_name}")
        
        # Find material in materials.yaml
        material_result = find_material_in_data(materials_data, material_name)
        if not material_result:
            print(f"   ⚠️ Material '{material_name}' not found in materials.yaml")
            continue
        
        category, material_data = material_result
        author_id = material_data.get("author_id")
        
        if not author_id:
            print(f"   ⚠️ No author_id found for {material_name}")
            continue
        
        print(f"   Expected author_id: {author_id}")
        
        # Get author data
        author_data = get_author_by_id(authors_data, author_id)
        if not author_data:
            print(f"   ❌ Author with ID {author_id} not found")
            errors += 1
            continue
        
        expected_author = author_data["name"]
        print(f"   Expected author: {expected_author}")
        
        # Parse frontmatter file
        frontmatter_data, remaining_content = parse_frontmatter_file(file_path)
        if not frontmatter_data:
            print(f"   ❌ Failed to parse frontmatter")
            errors += 1
            continue
        
        current_author = frontmatter_data.get("author", "Unknown")
        print(f"   Current author: {current_author}")
        
        # Check if update is needed
        if current_author == expected_author:
            print(f"   ✅ Author already correct")
            continue
        
        print(f"   🔄 Updating author: {current_author} → {expected_author}")
        
        # Update frontmatter
        updated_frontmatter = update_frontmatter_author(frontmatter_data, author_data)
        
        # Write updated file
        write_frontmatter_file(file_path, updated_frontmatter, remaining_content)
        updates_made += 1
    
    print(f"\n📊 Synchronization Summary:")
    print(f"   ✅ Files updated: {updates_made}")
    print(f"   ❌ Errors: {errors}")
    print(f"   📁 Total files checked: {len(frontmatter_files)}")
    
    if updates_made > 0:
        print(f"\n🎉 Successfully synchronized {updates_made} frontmatter files with materials.yaml authors!")
    else:
        print(f"\n✨ All frontmatter files are already synchronized!")
    
    return 0 if errors == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
