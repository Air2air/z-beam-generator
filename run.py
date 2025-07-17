#!/usr/bin/env python3
"""Minimal entry point with hardcoded article context."""

import os
import sys

# Define absolute path to output directory
OUTPUT_DIR = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/output"

# Define your article context here - edit this for each generation
ARTICLE_CONTEXT = {
    "subject": "Fairfield",
    "author_id": 3,
    "article_type": "region", # Options: application, material, region, thesaurus
    "output_dir": OUTPUT_DIR,
    "ai_provider": "deepseek"  # Options: openai, deepseek, xai, gemini
}

# Create output directory if it doesn't exist
try:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"✅ Output directory created/verified: {OUTPUT_DIR}")
    
    # Test write permissions with a small file
    test_file = os.path.join(OUTPUT_DIR, ".test_write")
    with open(test_file, "w") as f:
        f.write("Test write access")
    print("✅ Write permissions confirmed")
    os.remove(test_file)  # Clean up test file
except Exception as e:
    print(f"❌ ERROR: Could not create/write to output directory: {e}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    # Determine expected filename based on article type and subject
    subject = ARTICLE_CONTEXT["subject"].lower().replace(" ", "-")
    
    if ARTICLE_CONTEXT["article_type"] == "region":
        expected_file = f"{subject}-laser-cleaning.md"
        ARTICLE_CONTEXT["slug"] = f"{subject}-laser-cleaning"  # Add this line
    else:
        expected_file = f"{subject}.md"
        ARTICLE_CONTEXT["slug"] = subject  # Add this line
    
    print(f"Expected output filename: {expected_file}")
    
    # Print existing files in output directory
    files = os.listdir(OUTPUT_DIR)
    print(f"\n📂 Current files in output directory ({len(files)} found):")
    for file in files:
        print(f"  - {file}")
    
    # Import here to avoid polluting the global namespace
    from generator import generate_article
    
    # Generate the article
    success = generate_article(ARTICLE_CONTEXT)
    
    # Verify file was created after generation
    if success:
        new_files = os.listdir(OUTPUT_DIR)
        print(f"\n📂 Files in output directory after generation ({len(new_files)} found):")
        for file in files:
            print(f"  - {file}")
            
        # Check specifically for our expected file
        if expected_file in new_files:
            full_path = os.path.join(OUTPUT_DIR, expected_file)
            print(f"\n✅ SUCCESS: File created at {full_path}")
            print(f"File size: {os.path.getsize(full_path)} bytes")
        else:
            print(f"\n❓ WARNING: Expected file '{expected_file}' not found, but generation reported success.", file=sys.stderr)
            print("  This could mean the file was saved with a different name.")
            print("  Files found:", ", ".join(new_files))
    else:
        print("\n❌ Generation reported failure")
