#!/usr/bin/env python3
"""
Frontmatter Debugging Utility

A utility script to test the frontmatter loader on specific materials.
"""

import sys
import logging
from utils.file_ops.frontmatter_loader import load_frontmatter_data

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(levelname)s:%(name)s:%(message)s')

def main():
    """Main entry point for the frontmatter debug utility."""
    if len(sys.argv) < 2:
        print("Usage: python debug_frontmatter.py <material_name>")
        return

    material_name = sys.argv[1]
    print(f"Testing frontmatter loading for material: {material_name}")
    
    # Try to load frontmatter data
    frontmatter_data = load_frontmatter_data(material_name)
    
    if frontmatter_data:
        print("\n✅ Successfully loaded frontmatter data:")
        # Print the first few keys and values
        print("\nFirst few fields:")
        for i, (key, value) in enumerate(frontmatter_data.items()):
            if i < 5:  # Only show first 5 fields
                print(f"  {key}: {value}")
            else:
                remaining = len(frontmatter_data) - 5
                print(f"  ... and {remaining} more fields")
                break
        
        print(f"\nTotal fields: {len(frontmatter_data)}")
    else:
        print("\n❌ Failed to load frontmatter data.")

if __name__ == "__main__":
    main()
